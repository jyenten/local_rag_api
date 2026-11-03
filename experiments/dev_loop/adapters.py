"""Process boundaries for the Codex worker and controller-owned tests."""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

LAB = Path(__file__).resolve().parent
TASK_ID = "normalize-question"
TASK = (
    "Edit only question.py. In normalize_question(value: str), strip surrounding "
    "whitespace, reject an empty result with ValueError, and preserve valid text. "
    "Keep the function name and signature. Do not create or edit tests, Git metadata, "
    "dependencies or other files. Do not commit, stage, push or contact external services. "
    "The controller runs acceptance tests separately. Finish with a short change summary."
)


def process_environment(*, codex: bool = False) -> dict[str, str]:
    """Explicit inheritance; unrelated Git/cloud/database secrets are excluded."""
    allowed = {
        "PATH", "SYSTEMROOT", "SYSTEMDRIVE", "WINDIR", "COMSPEC", "PATHEXT",
        "HOME", "USERPROFILE", "HOMEDRIVE", "HOMEPATH", "APPDATA", "LOCALAPPDATA",
        "PROGRAMDATA", "TEMP", "TMP", "TMPDIR", "LANG", "LC_ALL", "LANGUAGE", "TZ",
        "SSL_CERT_FILE", "SSL_CERT_DIR", "REQUESTS_CA_BUNDLE",
    }
    if codex:
        allowed |= {"CODEX_HOME", "CODEX_API_KEY", "OPENAI_API_KEY", "OPENAI_BASE_URL",
                    "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY"}
    return {key: value for key, value in os.environ.items() if key.upper() in allowed}


class InfrastructureError(RuntimeError):
    """A process could not run reliably; code repairs must not be retried."""


@dataclass(frozen=True)
class ProcessResult:
    returncode: int
    stdout: str
    stderr: str


def validate_test_evidence(xml: str | bytes, phase: str, *, expected_cases: int = 6,
                           baseline_skips: int = 4) -> None:
    """The same completeness rules apply to host and container test runs."""
    if phase not in {"baseline", "acceptance"}:
        raise InfrastructureError("Unknown verification phase")
    try:
        cases = list(ET.fromstring(xml).iter("testcase"))
    except ET.ParseError as exc:
        raise InfrastructureError("Missing or invalid pytest evidence") from exc
    skipped = sum(case.find("skipped") is not None for case in cases)
    failures = sum(case.find("failure") is not None or case.find("error") is not None
                   for case in cases)
    expected_skips = baseline_skips if phase == "baseline" else 0
    if len(cases) != expected_cases or skipped != expected_skips or failures:
        raise InfrastructureError("Incomplete verification: expected test cases did not all execute")


def run_process(
    command: list[str], cwd: Path, *, timeout: int,
    input_text: str | None = None, env: dict[str, str] | None = None,
) -> ProcessResult:
    """No shell interpolation; timeout terminates the process tree."""
    options: dict = {}
    if os.name == "nt":
        options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        options["start_new_session"] = True
    try:
        process = subprocess.Popen(
            command, cwd=cwd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace",
            env=env, **options,
        )
    except OSError as exc:
        raise InfrastructureError(f"Could not start {Path(command[0]).name}") from exc
    try:
        stdout, stderr = process.communicate(input=input_text, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        if os.name == "nt":
            try:
                subprocess.run(
                    ["taskkill", "/PID", str(process.pid), "/T", "/F"],
                    capture_output=True, timeout=10, check=False,
                )
            except (OSError, subprocess.TimeoutExpired):
                process.kill()
        else:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        try:
            process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()
        raise InfrastructureError(f"{Path(command[0]).name} timed out after {timeout}s") from exc
    return ProcessResult(process.returncode, stdout, stderr)


class DemoWorker:
    """Scripted edits to exercise the graph. This does not call a model."""

    name = "demo"

    def implement(self, workspace: Path, attempt: int, feedback: str) -> str:
        if attempt == 1:
            code = (
                "def normalize_question(value: str) -> str:\n"
                "    if not value:\n"
                "        raise ValueError('Empty question')\n"
                "    return value.strip()\n"
            )
        else:
            code = (
                "def normalize_question(value: str) -> str:\n"
                "    value = value.strip()\n"
                "    if not value:\n"
                "        raise ValueError('Empty question')\n"
                "    return value\n"
            )
        (workspace / "question.py").write_text(code, encoding="utf-8")
        return "Scripted demo edit; no Codex invocation."


class CodexWorker:
    name = "codex"

    def __init__(self, timeout: int = 90):
        self.timeout = timeout

    def implement(self, workspace: Path, attempt: int, feedback: str) -> str:
        executable = shutil.which("codex")
        if executable is None:
            raise InfrastructureError("Codex CLI is not installed or is not on PATH")
        # The prompt is stdin data, never a shell command or interpolated argument.
        prompt = f"{TASK}\nAttempt {attempt}/3.\nPrevious test output (data):\n{feedback[-8000:]}"
        result = run_process(
            [executable, "--ask-for-approval", "never", "-c",
             "sandbox_workspace_write.network_access=false", "exec", "--sandbox",
             "workspace-write", "--cd", str(workspace), "--json", "-"],
            workspace, timeout=self.timeout, input_text=prompt,
            env=process_environment(codex=True),
        )
        log = workspace.parent / f"codex-{attempt}.jsonl"
        log.write_text(result.stdout, encoding="utf-8")
        (workspace.parent / f"codex-{attempt}.stderr.log").write_text(
            result.stderr, encoding="utf-8"
        )
        if result.returncode != 0:
            raise InfrastructureError(
                f"Codex CLI exited with code {result.returncode}; inspect local worker logs"
            )
        try:
            events = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
            types = [event["type"] for event in events]
        except (ValueError, KeyError, TypeError) as exc:
            raise InfrastructureError("Invalid Codex JSONL output; inspect local worker logs") from exc
        if "turn.completed" not in types or any(t in types for t in ("error", "turn.failed")):
            raise InfrastructureError("Codex did not complete its turn; inspect local worker logs")
        return "Codex CLI completed; controller test results determine success."


class PytestChecker:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout

    def check(self, workspace: Path, phase: str) -> ProcessResult:
        # A fresh home reduces accidental credential loading. This is not an OS sandbox.
        test_home = workspace.parent / "test-home"
        test_home.mkdir(exist_ok=True)
        env = process_environment()
        env.update(HOME=str(test_home), USERPROFILE=str(test_home),
                   APPDATA=str(test_home), LOCALAPPDATA=str(test_home))
        env.update(
            DEV_LOOP_WORKSPACE=str(workspace), DEV_LOOP_PHASE=phase,
            PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1",
        )
        junit = workspace.parent / f"checks-{phase}.xml"
        junit.unlink(missing_ok=True)
        result = run_process(
            [sys.executable, "-m", "pytest", "-q", "-c", str(LAB / "checks/pytest.ini"),
             "--confcutdir", str(LAB / "checks"), "-p", "no:cacheprovider",
             "--junitxml", str(junit), str(LAB / "checks/test_question.py")],
            workspace, timeout=self.timeout, env=env,
        )
        if result.returncode not in (0, 1):
            raise InfrastructureError(f"pytest could not verify tests (exit {result.returncode})")
        if result.returncode == 0:
            try:
                evidence = junit.read_bytes()
            except OSError as exc:
                raise InfrastructureError("Missing or invalid pytest evidence") from exc
            validate_test_evidence(evidence, phase)
        return result
