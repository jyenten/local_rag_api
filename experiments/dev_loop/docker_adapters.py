"""Ephemeral offline containers; candidate code is never executed on the host."""

from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
import threading
import time
import uuid
from pathlib import Path

from .adapters import (
    InfrastructureError, ProcessResult, process_environment, run_process,
    validate_test_evidence,
)
from .tasks import NORMALIZE, get_task

DEFAULT_IMAGE = "local-rag-dev-loop:1"
MAX_SOURCE_BYTES = 65536
MAX_OUTPUT_BYTES = 262144


def bounded_process(command: list[str], cwd: Path, *, input_text: str,
                    timeout: int, env: dict[str, str]) -> ProcessResult:
    """Drain both pipes concurrently, retaining at most 256 KiB in total."""
    options = ({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt"
               else {"start_new_session": True})
    try:
        process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   env=env, **options)
    except OSError as exc:
        raise InfrastructureError("Could not start Docker CLI") from exc
    output: list[list[bytes]] = [[], []]
    total = 0
    guard = threading.Lock()
    overflow = threading.Event()
    io_error = threading.Event()

    def read(pipe, index):
        nonlocal total
        try:
            while chunk := pipe.read(4096):
                with guard:
                    total += len(chunk)
                    if total > MAX_OUTPUT_BYTES:
                        overflow.set()
                        return
                    output[index].append(chunk)
        except OSError:
            io_error.set()
        finally:
            pipe.close()

    def write():
        try:
            process.stdin.write(input_text.encode("utf-8"))
            process.stdin.flush()
        except (BrokenPipeError, OSError):
            # The return code/protocol check will reject an interrupted request.
            pass
        finally:
            try:
                process.stdin.close()
            except OSError:
                pass

    threads = [threading.Thread(target=read, args=(process.stdout, 0), daemon=True),
               threading.Thread(target=read, args=(process.stderr, 1), daemon=True),
               threading.Thread(target=write, daemon=True)]
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + timeout
    try:
        while process.poll() is None:
            if overflow.is_set():
                raise InfrastructureError("Container output exceeded 256 KiB")
            if time.monotonic() >= deadline:
                raise InfrastructureError(f"Container timed out after {timeout}s")
            overflow.wait(.02)
        for thread in threads:
            thread.join(timeout=2)
        if overflow.is_set():
            raise InfrastructureError("Container output exceeded 256 KiB")
        if io_error.is_set() or any(thread.is_alive() for thread in threads):
            raise InfrastructureError("Container I/O did not complete")
        return ProcessResult(process.returncode,
                             b"".join(output[0]).decode("utf-8", errors="replace"),
                             b"".join(output[1]).decode("utf-8", errors="replace"))
    finally:
        if process.poll() is None:
            if os.name == "nt":
                try:
                    run_process(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                cwd, timeout=10, env=env)
                except InfrastructureError:
                    pass
                if process.poll() is None:
                    process.kill()
            else:
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            process.wait(timeout=5)
        for thread in threads:
            thread.join(timeout=2)


def candidate_source(workspace: Path) -> str:
    return candidate_files(workspace, ("question.py",))["question.py"]


def candidate_files(workspace: Path, names: tuple[str, ...]) -> dict[str, str]:
    sources = {}
    total = 0
    for name in names:
        if not re.fullmatch(r"[a-z_]+\.py", name):
            raise InfrastructureError("Artifacts must have fixed flat Python filenames")
        path = workspace / name
        if path.is_symlink() or not path.is_file():
            raise InfrastructureError("Candidate must be a regular UTF-8 file of at most 64 KiB")
        total += path.stat().st_size
        if total > MAX_SOURCE_BYTES:
            raise InfrastructureError("Combined candidate source exceeds 64 KiB")
        try:
            sources[name] = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            raise InfrastructureError("Candidate is not UTF-8") from exc
    return sources


class DockerRunner:
    def __init__(self, image: str = DEFAULT_IMAGE, timeout: int = 30):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:/@-]{0,255}", image):
            raise ValueError("Invalid runner image reference")
        self.image = image
        self.image_id: str | None = None
        self.timeout = timeout

    def invoke(self, mode: str, payload: dict, cwd: Path) -> tuple[ProcessResult, dict]:
        if mode not in {"demo-worker", "check", "check-files"}:
            raise InfrastructureError("Unknown container operation")
        executable = shutil.which("docker")
        if executable is None:
            raise InfrastructureError("Docker CLI is not installed or is not on PATH")
        env = process_environment()  # Host CLI only; these values are NOT passed into the container.
        if self.image_id is None:
            inspected = run_process([executable, "image", "inspect", "--format", "{{.Id}}",
                                     self.image], cwd, timeout=10, env=env)
            image_id = inspected.stdout.strip()
            if inspected.returncode or not re.fullmatch(r"sha256:[0-9a-f]{64}", image_id):
                raise InfrastructureError("Runner image unavailable; build the image and check Docker Engine")
            self.image_id = image_id  # Freeze the image for this runner's lifetime.
        name = "dev-loop-" + uuid.uuid4().hex
        command = [
            executable, "create", "--interactive", "--name", name,
            "--network", "none", "--read-only", "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges=true", "--user", "10001:10001",
            "--memory", "256m", "--memory-swap", "256m", "--cpus", "1",
            "--pids-limit", "64", "--log-driver", "none",
            "--tmpfs", "/work:rw,noexec,nosuid,nodev,size=32m,mode=1777",
            "--tmpfs", "/tmp:rw,noexec,nosuid,nodev,size=16m,mode=1777",
            "--workdir", "/work", "--entrypoint", "python", self.image_id,
            "-I", "/opt/dev-loop/container_entry.py", mode,
        ]
        # No mounts, host networking, Docker socket, credentials or environment forwarding.
        # Cleanup is attempted even when `create` times out after the daemon accepted it.
        try:
            created = run_process(command, cwd, timeout=10, env=env)
            if created.returncode:
                raise InfrastructureError("Could not create restricted runner container")
            result = bounded_process([executable, "start", "--attach", "--interactive", name],
                                     cwd, input_text=json.dumps(payload, ensure_ascii=False),
                                     timeout=self.timeout, env=env)
            if result.returncode not in ({0} if mode == "demo-worker" else {0, 1}):
                raise InfrastructureError(f"Runner failed (exit {result.returncode}); no host fallback")
            try:
                response = json.loads(result.stdout)
            except (ValueError, RecursionError) as exc:
                raise InfrastructureError("Invalid runner JSON response") from exc
            expected_protocol = 2 if mode == "check-files" else 1
            if (not isinstance(response, dict) or type(response.get("protocol")) is not int
                    or response["protocol"] != expected_protocol):
                raise InfrastructureError("Unknown runner response protocol")
            return result, response
        finally:
            removed = run_process([executable, "rm", "--force", name], cwd, timeout=10, env=env)
            missing = "no such container" in removed.stderr.lower()
            if removed.returncode and not missing:
                raise InfrastructureError(f"Container cleanup failed; inspect {name} before continuing")


class DockerDemoWorker:
    name = "demo-docker"
    isolation = "docker"

    def __init__(self, runner: DockerRunner):
        self.runner = runner

    def implement(self, workspace: Path, attempt: int, feedback: str) -> str:
        _, response = self.runner.invoke("demo-worker", {
            "source": candidate_source(workspace), "attempt": attempt,
            "feedback": feedback[-8000:],
        }, workspace)
        code, note = response.get("code"), response.get("note")
        try:
            valid_code = isinstance(code, str) and len(code.encode("utf-8")) <= MAX_SOURCE_BYTES
        except UnicodeError:
            valid_code = False
        if not valid_code or not isinstance(note, str) or len(note) > 2000:
            raise InfrastructureError("Invalid worker artifact")
        # Only an explicitly named text artifact crosses the boundary; never extract an archive.
        candidate_source(workspace)  # Recheck before writing.
        (workspace / "question.py").write_text(code, encoding="utf-8")
        return note


class DockerPytestChecker:
    isolation = "docker"

    def __init__(self, runner: DockerRunner, task_id: str = NORMALIZE.task_id):
        self.task = get_task(task_id)
        self.task_id = task_id
        self.runner = runner

    @property
    def image_id(self):
        return self.runner.image_id

    def check(self, workspace: Path, phase: str) -> ProcessResult:
        if phase not in {"baseline", "acceptance"}:
            raise InfrastructureError("Unknown verification phase")
        multiple = len(self.task.artifacts) > 1
        payload = ({"files": candidate_files(workspace, self.task.artifacts), "phase": phase}
                   if multiple else {"source": candidate_source(workspace), "phase": phase})
        if self.task_id != NORMALIZE.task_id:
            payload["task_id"] = self.task_id
        process, response = self.runner.invoke("check-files" if multiple else "check", payload, workspace)
        if self.task_id != NORMALIZE.task_id and response.get("task_id") != self.task_id:
            raise InfrastructureError(f"Checker image does not identify the requested task; build {self.task.checker_image}")
        if multiple and response.get("files") != list(self.task.artifacts):
            raise InfrastructureError("Checker did not identify the complete fixed artifact set")
        code, stdout, stderr = (response.get(key) for key in ("returncode", "stdout", "stderr"))
        if (type(code) is not int or code not in {0, 1} or code != process.returncode
                or not isinstance(stdout, str) or not isinstance(stderr, str)):
            raise InfrastructureError("Invalid test result from container")
        if code == 0:
            evidence = response.get("junit")
            if not isinstance(evidence, str):
                raise InfrastructureError("Missing container pytest evidence")
            validate_test_evidence(evidence, phase, expected_cases=self.task.test_count,
                                   baseline_skips=self.task.baseline_skips)
        return ProcessResult(code, stdout[-8000:], stderr[-8000:])
