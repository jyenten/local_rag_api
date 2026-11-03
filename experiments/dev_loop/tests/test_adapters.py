import json
import sys

import pytest

from experiments.dev_loop import adapters
from experiments.dev_loop.adapters import CodexWorker, InfrastructureError, ProcessResult, run_process


def test_prompt_uses_stdin_and_sandbox_with_no_shell(monkeypatch, tmp_path):
    seen = {}
    monkeypatch.setattr(adapters.shutil, "which", lambda name: "codex")
    monkeypatch.setenv("DEV_LOOP_TOKEN", "must-not-reach-worker")

    def fake_process(command, cwd, **kwargs):
        seen.update(command=command, cwd=cwd, **kwargs)
        return ProcessResult(0, json.dumps({"type": "turn.completed"}) + "\n", "")

    monkeypatch.setattr(adapters, "run_process", fake_process)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    CodexWorker().implement(workspace, 1, "literal $(do-not-execute)")
    assert seen["command"][-1] == "-"
    assert "workspace-write" in seen["command"]
    assert "--ask-for-approval" in seen["command"]
    assert "literal $(do-not-execute)" in seen["input_text"]
    assert not any("do-not-execute" in arg for arg in seen["command"])
    assert "DEV_LOOP_TOKEN" not in seen["env"]
    assert "sandbox_workspace_write.network_access=false" in seen["command"]


def test_missing_codex_is_infrastructure_error(monkeypatch, tmp_path):
    monkeypatch.setattr(adapters.shutil, "which", lambda name: None)
    with pytest.raises(InfrastructureError, match="not installed"):
        CodexWorker().implement(tmp_path, 1, "")


@pytest.mark.parametrize("code,output", [(1, ""), (0, "not json"),
                                         (0, '{"type":"turn.failed"}'), (0, "")])
def test_unsuccessful_codex_turn_is_not_reported_as_completed(monkeypatch, tmp_path, code, output):
    monkeypatch.setattr(adapters.shutil, "which", lambda name: "codex")
    monkeypatch.setattr(adapters, "run_process", lambda *a, **kw: ProcessResult(code, output, ""))
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    with pytest.raises(InfrastructureError):
        CodexWorker().implement(workspace, 1, "")


def test_real_process_preserves_literal_input(tmp_path):
    result = run_process([sys.executable, "-c", "import sys; print(sys.stdin.read())"],
                         tmp_path, timeout=5, input_text="$(literal); spaces")
    assert result.returncode == 0
    assert result.stdout.strip() == "$(literal); spaces"


def test_real_process_timeout_stops_the_run(tmp_path):
    with pytest.raises(InfrastructureError, match="timed out"):
        run_process([sys.executable, "-c", "import time; time.sleep(10)"], tmp_path, timeout=1)


@pytest.mark.parametrize("exit_code", [2, 3, 4, 5])
def test_pytest_configuration_and_collection_errors_are_infrastructure(monkeypatch, tmp_path, exit_code):
    monkeypatch.setattr(adapters, "run_process",
                        lambda *a, **kw: ProcessResult(exit_code, "broken pytest", ""))
    with pytest.raises(InfrastructureError):
        adapters.PytestChecker().check(tmp_path, "acceptance")


@pytest.mark.parametrize("report", [None, "<not-xml", "<testsuites/>",
                                   '<testsuites><testsuite>' +
                                   '<testcase><skipped/></testcase>' * 6 +
                                   '</testsuite></testsuites>'])
def test_zero_exit_without_complete_test_evidence_is_not_success(monkeypatch, tmp_path, report):
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    def fake_process(*args, **kwargs):
        if report is not None:
            (tmp_path / "checks-acceptance.xml").write_text(report, encoding="utf-8")
        return ProcessResult(0, "claims to pass", "")

    monkeypatch.setattr(adapters, "run_process", fake_process)
    with pytest.raises(InfrastructureError):
        adapters.PytestChecker().check(workspace, "acceptance")


def test_environment_does_not_inherit_unrelated_credentials_or_git_overrides(monkeypatch):
    for name in ("GH_TOKEN", "GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "DATABASE_URL",
                 "GIT_DIR", "GIT_CONFIG_COUNT", "DEV_LOOP_TOKEN"):
        monkeypatch.setenv(name, "must-not-be-inherited")
    monkeypatch.setenv("CODEX_API_KEY", "worker-only-auth")
    monkeypatch.setenv("CODEX_HOME", "/configured/codex")
    worker_env = adapters.process_environment(codex=True)
    test_env = adapters.process_environment()
    for name in ("GH_TOKEN", "GITHUB_TOKEN", "AWS_ACCESS_KEY_ID", "DATABASE_URL",
                 "GIT_DIR", "GIT_CONFIG_COUNT", "DEV_LOOP_TOKEN"):
        assert name not in worker_env and name not in test_env
    assert worker_env["CODEX_API_KEY"] == "worker-only-auth"
    assert "CODEX_API_KEY" not in test_env and "CODEX_HOME" not in test_env
