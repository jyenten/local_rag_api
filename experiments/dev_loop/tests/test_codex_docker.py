"""No account or model calls: protocol, boundaries and graph wiring are verified here."""

import hashlib
import json
import uuid

import pytest

from experiments.dev_loop import codex_docker as codex
from experiments.dev_loop.adapters import InfrastructureError, ProcessResult, TASK_ID
from experiments.dev_loop.docker_adapters import DockerPytestChecker, DockerRunner
from experiments.dev_loop.workflow import run_job

IMAGE_ID = "sha256:" + "c" * 64
CODE = ('def normalize_question(value: str) -> str:\n'
        '    value = value.strip()\n'
        '    if not value:\n'
        '        raise ValueError("empty")\n'
        '    return value\n')
USAGE = {"input_tokens": 500, "cached_input_tokens": 100, "output_tokens": 70}


def events(code=CODE, usage=USAGE):
    return [
        {"type": "thread.started", "thread_id": "synthetic"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"type": "agent_message",
         "text": json.dumps({"code": code})}},
        {"type": "turn.completed", "usage": usage},
    ]


def jsonl(items):
    return "\n".join(json.dumps(item) for item in items)


def transport(monkeypatch, tmp_path, items=None, returncode=0):
    (tmp_path / "question.py").write_text("original", encoding="utf-8")
    calls = []
    monkeypatch.setattr(codex.shutil, "which", lambda _: "docker")

    def control(command, cwd, **kwargs):
        calls.append((command, kwargs))
        if command[1:3] == ["image", "inspect"]:
            return ProcessResult(0, IMAGE_ID, "")
        return ProcessResult(0, "ok", "")

    def attach(command, cwd, **kwargs):
        calls.append((command, kwargs))
        return ProcessResult(returncode, jsonl(events() if items is None else items), "")

    monkeypatch.setattr(codex, "run_process", control)
    monkeypatch.setattr(codex, "bounded_process", attach)
    return calls


def test_only_worker_gets_named_auth_volume_and_network(monkeypatch, tmp_path):
    monkeypatch.setenv("DEV_LOOP_TOKEN", "synthetic-http-token")
    monkeypatch.setenv("OPENAI_API_KEY", "synthetic-api-key")
    monkeypatch.setenv("CODEX_HOME", "synthetic-host-auth-directory")
    calls = transport(monkeypatch, tmp_path)
    worker = codex.DockerCodexWorker()
    worker.implement(tmp_path, 1, "literal $(not-a-command)")
    worker.implement(tmp_path, 2, "repair")
    assert (tmp_path / "question.py").read_text(encoding="utf-8") == CODE
    assert worker.image_id == IMAGE_ID
    assert worker.attempt_records[0]["usage"] == USAGE
    assert worker.attempt_records[0]["code_sha256"] == hashlib.sha256((tmp_path / "question.py").read_bytes()).hexdigest()
    assert sum(c[1:3] == ["image", "inspect"] for c, _ in calls) == 1
    command = next(c for c, _ in calls if c[1] == "create")
    assert command.count("--mount") == 1
    assert command[command.index("--mount") + 1] == (
        "type=volume,source=local-rag-codex-auth,target=/home/node/.codex")
    assert command[command.index("--network") + 1] == "bridge"
    assert command[command.index("--sandbox") + 1] == "read-only"
    assert command[command.index("--user") + 1] == "1000:1000"
    assert "--read-only" in command and "--ignore-user-config" in command
    assert "--ignore-rules" in command and "--ephemeral" in command
    for config in ["forced_login_method=chatgpt", "cli_auth_credentials_store=file",
                   "model_provider=openai", "web_search=disabled", "features.shell_tool=false",
                   "features.apps=false", "features.plugins=false", "features.multi_agent=false"]:
        assert config in command
    assert not any(flag in command for flag in ["-v", "--volume", "--env", "-e", "--publish",
                                                "--privileged", "--dangerously-bypass-approvals-and-sandbox"])
    for _, kwargs in calls:
        assert not {"DEV_LOOP_TOKEN", "OPENAI_API_KEY", "CODEX_HOME"} & kwargs["env"].keys()
    attached = next(kwargs for c, kwargs in calls if c[1] == "start")
    assert "literal $(not-a-command)" in attached["input_text"]
    assert all("literal $(not-a-command)" not in part for part in command)
    assert calls[-1][0][1:3] == ["rm", "--force"]


@pytest.mark.parametrize("items", [
    [], events()[:-1], events() + [{"type": "error", "message": "synthetic"}],
    events()[:-1] + [{"type": "turn.failed"}],
    events() + [events()[-1]],
    events()[:2] + [{"type": "item.started", "item": {"type": "command_execution"}}] + events()[2:],
    events(code=""), events(code="```python\n" + CODE + "```"),
    events(code="def other(): pass"), events(code="x" * 65537),
    events(code=CODE + "\nprint('do not execute')"),
    [{"type": "item.completed", "item": None}, events()[-1]],
])
def test_bad_output_never_overwrites_candidate(monkeypatch, tmp_path, items):
    calls = transport(monkeypatch, tmp_path, items)
    with pytest.raises(InfrastructureError, match="artifact"):
        codex.DockerCodexWorker().implement(tmp_path, 1, "")
    assert (tmp_path / "question.py").read_text(encoding="utf-8") == "original"
    assert calls[-1][0][1:3] == ["rm", "--force"]


@pytest.mark.parametrize("usage", [None, {}, {**USAGE, "output_tokens": True},
                                    {**USAGE, "cached_input_tokens": 501}])
def test_missing_or_invalid_usage_is_unknown_not_zero(usage):
    code, actual = codex.parse_response(jsonl(events(usage=usage)))
    assert code == CODE and actual is None


@pytest.mark.parametrize("value", ["D:\\auth", "/tmp/auth", "name,target=/host", "../auth"])
def test_auth_mount_cannot_be_a_host_path_or_mount_injection(value):
    with pytest.raises(ValueError, match="named Docker volume"):
        codex.DockerCodexWorker(auth_volume=value)


@pytest.mark.parametrize("operation", ["create", "start"])
def test_timeout_cleans_up_and_preserves_candidate(monkeypatch, tmp_path, operation):
    calls = transport(monkeypatch, tmp_path)
    original = codex.run_process

    def fail(command, cwd, **kwargs):
        if command[1] == operation:
            raise InfrastructureError("synthetic timeout")
        return original(command, cwd, **kwargs)

    if operation == "start":
        monkeypatch.setattr(codex, "bounded_process", fail)
    else:
        monkeypatch.setattr(codex, "run_process", fail)
    with pytest.raises(InfrastructureError, match="timeout"):
        codex.DockerCodexWorker().implement(tmp_path, 1, "")
    assert calls[-1][0][1:3] == ["rm", "--force"]
    assert (tmp_path / "question.py").read_text(encoding="utf-8") == "original"


@pytest.mark.parametrize("failure", ["image", "volume"])
def test_missing_prerequisites_stop_before_container_creation(monkeypatch, tmp_path, failure):
    calls = transport(monkeypatch, tmp_path)
    original = codex.run_process

    def control(command, cwd, **kwargs):
        return ProcessResult(1, "", "missing") if command[1] == failure else original(command, cwd, **kwargs)

    monkeypatch.setattr(codex, "run_process", control)
    with pytest.raises(InfrastructureError, match="unavailable"):
        codex.DockerCodexWorker().implement(tmp_path, 1, "")
    assert not any(c[1] in {"create", "start"} for c, _ in calls)


def test_failed_cli_does_not_publish_raw_authenticated_logs(monkeypatch, tmp_path):
    calls = transport(monkeypatch, tmp_path, returncode=1)
    monkeypatch.setattr(codex, "bounded_process", lambda *a, **k:
                        ProcessResult(1, "synthetic-secret", "synthetic-secret"))
    with pytest.raises(InfrastructureError) as exc:
        codex.DockerCodexWorker().implement(tmp_path, 1, "")
    assert "synthetic-secret" not in str(exc.value)
    assert calls[-1][0][1] == "rm"


def test_cleanup_failure_prevents_artifact_write(monkeypatch, tmp_path):
    transport(monkeypatch, tmp_path)
    original = codex.run_process
    monkeypatch.setattr(codex, "run_process", lambda c, cwd, **k:
                        ProcessResult(1, "", "disconnected") if c[1] == "rm" else original(c, cwd, **k))
    with pytest.raises(InfrastructureError, match="cleanup failed"):
        codex.DockerCodexWorker().implement(tmp_path, 1, "")
    assert (tmp_path / "question.py").read_text(encoding="utf-8") == "original"


def test_two_graph_jobs_keep_usage_separate_and_checks_offline(monkeypatch, tmp_path):
    from experiments.dev_loop.adapters import PytestChecker
    from experiments.dev_loop.tests.test_docker import evidence

    transport(monkeypatch, tmp_path)
    monkeypatch.setattr(PytestChecker, "check", lambda *a: pytest.fail("No host checker"))
    runner = DockerRunner()
    worker = codex.DockerCodexWorker()
    phases = []

    def check(mode, payload, cwd):
        phases.append(payload["phase"])
        assert mode == "check"
        assert "auth" not in payload and "token" not in payload
        runner.image_id = "sha256:" + "a" * 64
        return ProcessResult(0, "", ""), {"returncode": 0, "stdout": "six checks",
                                           "stderr": "", "junit": evidence(payload["phase"])}

    monkeypatch.setattr(runner, "invoke", check)
    for _ in range(2):
        report = run_job(str(uuid.uuid4()), TASK_ID, tmp_path / "runs", worker, DockerPytestChecker(runner))
        assert report["status"] == "review_ready" and report["attempts"] == 1
        assert report["authentication"] == "chatgpt"
        assert report["worker_image"] == IMAGE_ID
        assert report["runner_image"] != report["worker_image"]
        assert len(report["worker_attempts"]) == 1
        assert report["worker_attempts"][0]["usage"] == USAGE
        assert report["model_usage_measured"] is True and report["model_cost"] is None
    assert phases == ["baseline", "acceptance"] * 2


def test_baseline_failure_never_calls_model(monkeypatch, tmp_path):
    worker = codex.DockerCodexWorker()
    monkeypatch.setattr(worker, "implement", lambda *a: pytest.fail("Model must not be called"))

    class BrokenChecker:
        def check(self, *args):
            raise InfrastructureError("Docker unavailable")

    report = run_job(str(uuid.uuid4()), TASK_ID, tmp_path, worker, BrokenChecker())
    assert report["status"] == "infrastructure_error" and report["attempts"] == 0
    assert report["worker_attempts"] == []


@pytest.mark.parametrize("complete", [True, False])
def test_batch_sums_only_complete_token_evidence_and_describes_worker_network(monkeypatch, tmp_path, complete):
    from experiments.dev_loop import batch

    calls = 0

    def job(request_id, task_id, runs_dir, worker, checker):
        nonlocal calls
        calls += 1
        measured = complete or calls == 1
        return {"request_id": request_id, "backend": worker.name, "status": "review_ready",
                "attempts": 1, "duration_s": .1, "trace": [],
                "model_usage_measured": measured,
                "worker_attempts": [{"usage": USAGE if measured else None}]}

    monkeypatch.setattr(batch, "run_job", job)
    report = batch.run_batch(2, tmp_path / "batch", codex.DockerCodexWorker(),
                             DockerPytestChecker(DockerRunner()))
    assert report["measurement"] == "live-codex" and report["model_calls"] is None
    assert report["model_cost"] is None
    assert report["model_usage_measured"] is complete
    assert report["cli_reported_tokens"] == ({k: v * 2 for k, v in USAGE.items()} if complete else None)
    document = batch.render_report(report, tmp_path / "batch").read_text(encoding="utf-8")
    assert "se sítí bridge" in document and "vlastním přihlašovacím volume ChatGPT" in document
    assert "Worker a pytest jsou spouštěny v oddělených jednorázových kontejnerech bez sítě" not in document
