"""Protocol tests run everywhere; actual isolation tests require an explicit opt-in."""

import json
import os
import sys
import uuid

import pytest

from experiments.dev_loop import docker_adapters as docker
from experiments.dev_loop.__main__ import main
from experiments.dev_loop.adapters import (
    LAB, TASK_ID, DemoWorker, InfrastructureError, ProcessResult, process_environment,
)
from experiments.dev_loop.workflow import JobConflict, run_job

IMAGE_ID = "sha256:" + "a" * 64


def evidence(phase="acceptance"):
    return "<testsuites><testsuite>" + "".join(
        "<testcase><skipped/></testcase>" if phase == "baseline" and i >= 2
        else "<testcase/>" for i in range(6)
    ) + "</testsuite></testsuites>"


def fake_transport(monkeypatch, response, returncode=0):
    calls = []
    monkeypatch.setattr(docker.shutil, "which", lambda name: "docker")

    def control(command, cwd, **kwargs):
        calls.append((command, kwargs))
        if command[1:3] == ["image", "inspect"]:
            return ProcessResult(0, IMAGE_ID, "")
        return ProcessResult(0, "container-id", "")

    def attach(command, cwd, **kwargs):
        calls.append((command, kwargs))
        return ProcessResult(returncode, json.dumps(response), "")

    monkeypatch.setattr(docker, "run_process", control)
    monkeypatch.setattr(docker, "bounded_process", attach)
    return calls


def test_containers_receive_no_mounts_secrets_or_host_namespaces(monkeypatch, tmp_path):
    monkeypatch.setenv("DEV_LOOP_TOKEN", "synthetic-api-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-model-secret")
    calls = fake_transport(monkeypatch, {"protocol": 1})
    runner = docker.DockerRunner()
    runner.invoke("check", {"source": "safe text"}, tmp_path)
    runner.invoke("check", {"source": "safe text"}, tmp_path)
    assert runner.image_id == IMAGE_ID
    assert sum(command[1:3] == ["image", "inspect"] for command, _ in calls) == 1
    creates = [command for command, _ in calls if command[1] == "create"]
    assert len(creates) == 2
    for command in creates:
        for option, value in (("--network", "none"), ("--cap-drop", "ALL"),
                              ("--user", "10001:10001"), ("--memory", "256m"),
                              ("--memory-swap", "256m"), ("--cpus", "1"),
                              ("--pids-limit", "64"),
                              ("--security-opt", "no-new-privileges=true")):
            assert command[command.index(option) + 1] == value
        assert "--read-only" in command
        assert IMAGE_ID in command
        assert all(flag not in command for flag in (
            "--mount", "--volume", "-v", "--env", "-e", "--env-file", "--privileged",
            "--pid", "--ipc", "--publish", "-p",
        ))
        assert "size=32m" in command[command.index("--tmpfs") + 1]
    for _, kwargs in calls:
        assert "DEV_LOOP_TOKEN" not in kwargs["env"]
        assert "OPENAI_API_KEY" not in kwargs["env"]
    assert sum(command[1] == "rm" for command, _ in calls) == 2


def test_timeout_removes_daemon_container_and_never_falls_back(monkeypatch, tmp_path):
    calls = fake_transport(monkeypatch, {"protocol": 1})

    def timeout(*args, **kwargs):
        raise InfrastructureError("Container timed out")

    monkeypatch.setattr(docker, "bounded_process", timeout)
    with pytest.raises(InfrastructureError, match="timed out"):
        docker.DockerRunner().invoke("check", {}, tmp_path)
    created = next(c for c, _ in calls if c[1] == "create")
    removed = next(c for c, _ in calls if c[1] == "rm")
    assert removed[-1] == created[created.index("--name") + 1]
    assert "--force" in removed


def test_create_timeout_also_attempts_cleanup(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(docker.shutil, "which", lambda name: "docker")

    def control(command, cwd, **kwargs):
        calls.append(command)
        if command[1:3] == ["image", "inspect"]:
            return ProcessResult(0, IMAGE_ID, "")
        if command[1] == "create":
            raise InfrastructureError("Create timed out")
        return ProcessResult(0, "", "")

    monkeypatch.setattr(docker, "run_process", control)
    with pytest.raises(InfrastructureError, match="Create timed out"):
        docker.DockerRunner().invoke("check", {}, tmp_path)
    assert calls[-1][1:3] == ["rm", "--force"]


def test_cleanup_failure_prevents_a_successful_result(monkeypatch, tmp_path):
    fake_transport(monkeypatch, {"protocol": 1})
    original = docker.run_process

    def control(command, cwd, **kwargs):
        if command[1] == "rm":
            return ProcessResult(1, "", "daemon disconnected")
        return original(command, cwd, **kwargs)

    monkeypatch.setattr(docker, "run_process", control)
    with pytest.raises(InfrastructureError, match="cleanup failed"):
        docker.DockerRunner().invoke("check", {}, tmp_path)


@pytest.mark.parametrize("response", [[], {"protocol": True}, {"protocol": 2}])
def test_unknown_protocol_is_not_success(monkeypatch, tmp_path, response):
    calls = fake_transport(monkeypatch, response)
    with pytest.raises(InfrastructureError, match="protocol"):
        docker.DockerRunner().invoke("check", {}, tmp_path)
    assert calls[-1][0][1] == "rm"


def test_missing_image_is_infrastructure_error_without_container(monkeypatch, tmp_path):
    monkeypatch.setattr(docker.shutil, "which", lambda name: "docker")
    monkeypatch.setattr(docker, "run_process", lambda *a, **k: ProcessResult(1, "", "missing"))
    with pytest.raises(InfrastructureError, match="image unavailable"):
        docker.DockerRunner().invoke("check", {}, tmp_path)


def test_missing_docker_is_infrastructure_error(monkeypatch, tmp_path):
    monkeypatch.setattr(docker.shutil, "which", lambda name: None)
    with pytest.raises(InfrastructureError, match="not installed"):
        docker.DockerRunner().invoke("check", {}, tmp_path)


@pytest.mark.parametrize("code", [None, "x" * 65537, "\ud800"])
def test_invalid_worker_artifact_is_not_written(monkeypatch, tmp_path, code):
    (tmp_path / "question.py").write_text("original", encoding="utf-8")
    fake_transport(monkeypatch, {"protocol": 1, "code": code, "note": "done"})
    with pytest.raises(InfrastructureError, match="artifact"):
        docker.DockerDemoWorker(docker.DockerRunner()).implement(tmp_path, 1, "")
    assert (tmp_path / "question.py").read_text(encoding="utf-8") == "original"


def test_oversized_candidate_is_not_sent_to_docker(tmp_path):
    (tmp_path / "question.py").write_text("x" * 65537, encoding="utf-8")
    with pytest.raises(InfrastructureError, match="64 KiB"):
        docker.DockerPytestChecker(docker.DockerRunner()).check(tmp_path, "acceptance")


@pytest.mark.parametrize("junit", ["", "<testsuites/>", evidence("baseline")])
def test_container_zero_exit_requires_complete_evidence(monkeypatch, tmp_path, junit):
    (tmp_path / "question.py").write_text("source", encoding="utf-8")
    fake_transport(monkeypatch, {"protocol": 1, "returncode": 0,
                                "stdout": "claims success", "stderr": "", "junit": junit})
    with pytest.raises(InfrastructureError):
        docker.DockerPytestChecker(docker.DockerRunner()).check(tmp_path, "acceptance")


def test_local_fallback_is_not_used_for_docker_graph(monkeypatch, tmp_path):
    from experiments.dev_loop.adapters import PytestChecker

    def forbidden(*args, **kwargs):
        raise AssertionError("Host pytest must not execute")

    monkeypatch.setattr(PytestChecker, "check", forbidden)
    runner = docker.DockerRunner()
    operations = []

    def transport(mode, payload, cwd):
        operations.append((mode, payload))
        runner.image_id = IMAGE_ID
        if mode == "demo-worker":
            code = ("def normalize_question(value: str) -> str:\n"
                    "    return value.strip()\n" if payload["attempt"] == 1 else
                    "def normalize_question(value: str) -> str:\n"
                    "    value = value.strip()\n"
                    "    if not value: raise ValueError('empty')\n"
                    "    return value\n")
            return ProcessResult(0, "", ""), {"code": code, "note": "container edit"}
        phase = payload["phase"]
        code = int(phase == "acceptance" and "raise ValueError('empty')" not in payload["source"])
        return ProcessResult(code, "", ""), {"returncode": code, "stdout": "checks",
                                               "stderr": "", "junit": evidence(phase)}

    monkeypatch.setattr(runner, "invoke", transport)
    request_id = str(uuid.uuid4())
    result = run_job(request_id, TASK_ID, tmp_path, docker.DockerDemoWorker(runner),
                     docker.DockerPytestChecker(runner))
    assert (result["status"], result["attempts"]) == ("review_ready", 2)
    assert result["backend"] == "demo-docker"
    assert result["isolation"] == result["checker_isolation"] == "docker"
    assert result["runner_image"] == IMAGE_ID
    assert [mode for mode, _ in operations] == ["check", "demo-worker", "check", "demo-worker", "check"]
    with pytest.raises(JobConflict):
        run_job(request_id, TASK_ID, tmp_path, DemoWorker(), PytestChecker())


def test_cli_selects_live_worker_and_offline_checker(monkeypatch):
    from experiments.dev_loop import __main__ as cli
    from experiments.dev_loop.codex_docker import DockerCodexWorker

    monkeypatch.setattr(sys, "argv", ["dev-loop", "--backend", "codex", "--isolation", "docker"])
    def fake_run(request_id, task_id, runs_dir, worker, checker):
        assert isinstance(worker, DockerCodexWorker)
        assert isinstance(checker, docker.DockerPytestChecker)
        assert worker.image != checker.runner.image
        return {"status": "review_ready"}

    monkeypatch.setattr(cli, "run_job", fake_run)
    assert main() == 0


def test_docker_health_reports_isolation_without_starting_a_container(tmp_path):
    from fastapi.testclient import TestClient
    from experiments.dev_loop.api import create_app

    runner = docker.DockerRunner()
    client = TestClient(create_app(docker.DockerDemoWorker(runner),
                                  docker.DockerPytestChecker(runner), tmp_path,
                                  "synthetic-token-at-least-24-characters"))
    health = client.get("/health").json()
    assert health == {"status": "ok", "backend": "demo-docker", "isolation": "docker",
                      "checker_isolation": "docker", "task_id": TASK_ID}
    assert runner.image_id is None


def test_batch_does_not_mislabel_docker_demo_as_live_codex(monkeypatch, tmp_path):
    from experiments.dev_loop import batch

    runner = docker.DockerRunner()
    runner.image_id = IMAGE_ID

    def fake_run(request_id, task_id, runs_dir, worker, checker):
        return {"request_id": request_id, "backend": worker.name, "status": "review_ready",
                "attempts": 2, "duration_s": .1, "trace": []}

    monkeypatch.setattr(batch, "run_job", fake_run)
    report = batch.run_batch(1, tmp_path / "batch", docker.DockerDemoWorker(runner),
                             docker.DockerPytestChecker(runner))
    assert report["measurement"] == "scripted-demo"
    assert report["model_calls"] == 0
    assert report["isolation"] == report["checker_isolation"] == "docker"
    assert report["runner_image"] == IMAGE_ID
    document = batch.render_report(report, tmp_path / "batch").read_text(encoding="utf-8")
    assert "DEMO - bez volání modelu | Docker" in document
    assert "CHYBÍ OS izolace" not in document
    assert "Python má oprávnění lokálního uživatele" not in document


def test_bounded_process_preserves_utf8_and_literal_stdin(tmp_path):
    result = docker.bounded_process(
        [sys.executable, "-c", "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"],
        tmp_path, input_text="žluťoučký $(literal)", timeout=5, env=process_environment())
    assert result.returncode == 0
    assert result.stdout == "žluťoučký $(literal)"


def test_bounded_process_stops_output_flood(tmp_path):
    with pytest.raises(InfrastructureError, match="256 KiB"):
        docker.bounded_process([sys.executable, "-c",
                                "import os; os.write(1,b'x'*300000); os.write(2,b'y'*300000)"],
                               tmp_path, input_text="", timeout=5, env=process_environment())


def test_bounded_process_times_out(tmp_path):
    with pytest.raises(InfrastructureError, match="timed out"):
        docker.bounded_process([sys.executable, "-c", "import time; time.sleep(10)"],
                               tmp_path, input_text="", timeout=1, env=process_environment())


live_docker = pytest.mark.skipif(os.environ.get("DEV_LOOP_DOCKER_TESTS") != "1",
                                 reason="Opt in after building the image: DEV_LOOP_DOCKER_TESTS=1")


@live_docker
def test_live_docker_graph_repairs_and_removes_all_five_containers(tmp_path):
    runner = docker.DockerRunner()
    result = run_job(str(uuid.uuid4()), TASK_ID, tmp_path,
                     docker.DockerDemoWorker(runner), docker.DockerPytestChecker(runner))
    assert result["status"] == "review_ready"
    assert result["attempts"] == 2
    assert result["runner_image"].startswith("sha256:")
    assert result["isolation"] == result["checker_isolation"] == "docker"


@live_docker
def test_live_container_cannot_read_host_secret_write_checks_or_use_network(monkeypatch, tmp_path):
    secret = tmp_path / "host-only-secret.txt"
    secret.write_text("synthetic host canary", encoding="utf-8")
    monkeypatch.setenv("DEV_LOOP_TOKEN", "synthetic-secret-must-not-enter-container")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    source = f'''import os, socket
from pathlib import Path
assert os.getuid() == 10001
assert 'DEV_LOOP_TOKEN' not in os.environ
assert not Path({str(secret)!r}).exists()
assert not Path('/var/run/docker.sock').exists()
assert os.statvfs('/').f_flag & os.ST_RDONLY
status = Path('/proc/self/status').read_text(encoding='utf-8')
assert 'NoNewPrivs:\\t1' in status
assert 'CapEff:\\t0000000000000000' in status
def limit_file(*paths):
    return next(Path(p) for p in paths if Path(p).is_file()).read_text(encoding='utf-8').strip()
memory = limit_file('/sys/fs/cgroup/memory.max', '/sys/fs/cgroup/memory/memory.limit_in_bytes')
assert 0 < int(memory) <= 256 * 1024 * 1024
pids = limit_file('/sys/fs/cgroup/pids.max', '/sys/fs/cgroup/pids/pids.max')
assert 0 < int(pids) <= 64
if Path('/sys/fs/cgroup/cpu.max').is_file():
    quota, period = limit_file('/sys/fs/cgroup/cpu.max').split()
else:
    quota = limit_file('/sys/fs/cgroup/cpu/cpu.cfs_quota_us', '/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us')
    period = limit_file('/sys/fs/cgroup/cpu/cpu.cfs_period_us', '/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_period_us')
assert 0 < int(quota) / int(period) <= 1
for directory, maximum in [('/work', 32 * 1024 * 1024), ('/tmp', 16 * 1024 * 1024)]:
    fs = os.statvfs(directory)
    assert fs.f_blocks * fs.f_frsize <= maximum
try:
    Path('/opt/dev-loop/checks/test_question.py').write_text('tamper', encoding='utf-8')
except OSError:
    pass
else:
    raise AssertionError('Checks must remain read-only')
try:
    sock = socket.create_connection(('192.0.2.1', 80), timeout=0.2)
except OSError:
    pass
else:
    sock.close()
    raise AssertionError('Network must be disabled')
def normalize_question(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError('empty')
    return value
'''
    (workspace / "question.py").write_text(source, encoding="utf-8")
    result = docker.DockerPytestChecker(docker.DockerRunner()).check(workspace, "acceptance")
    assert result.returncode == 0, result.stdout + result.stderr
    assert secret.read_text(encoding="utf-8") == "synthetic host canary"


@live_docker
def test_live_infinite_candidate_hits_timeout(tmp_path):
    (tmp_path / "question.py").write_text("while True: pass\n", encoding="utf-8")
    with pytest.raises(InfrastructureError, match="timed out"):
        docker.DockerPytestChecker(docker.DockerRunner(timeout=3)).check(tmp_path, "acceptance")
