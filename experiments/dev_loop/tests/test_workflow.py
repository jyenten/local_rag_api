import json
import uuid
from pathlib import Path

import pytest

from experiments.dev_loop.adapters import (
    TASK_ID, DemoWorker, InfrastructureError, ProcessResult, PytestChecker,
)
from experiments.dev_loop.workflow import JobConflict, run_job


class RecordingWorker(DemoWorker):
    def __init__(self):
        self.calls = []

    def implement(self, workspace, attempt, feedback):
        self.calls.append((attempt, feedback))
        return super().implement(workspace, attempt, feedback)


def run(tmp_path, worker=None, checker=None, request_id=None):
    return run_job(request_id or str(uuid.uuid4()), TASK_ID, tmp_path,
                   worker or DemoWorker(), checker or PytestChecker())


def test_real_pytest_failure_is_repaired_by_graph(tmp_path):
    worker = RecordingWorker()
    result = run(tmp_path, worker)
    assert result["status"] == "review_ready"
    assert result["backend"] == "demo"
    assert result["attempts"] == 2
    assert result["committed"] is False
    assert result["applied_to_rag"] is False
    assert [e["node"] for e in result["trace"]] == [
        "baseline", "implement", "verify", "implement", "verify"
    ]
    assert result["trace"][0]["returncode"] == 0
    assert result["trace"][2]["returncode"] == 1
    assert result["trace"][4]["returncode"] == 0
    assert "Failed: DID NOT RAISE" in worker.calls[1][1]
    assert "value = value.strip()" in result["diff"]


class AlwaysWrongWorker(DemoWorker):
    def implement(self, workspace, attempt, feedback):
        return super().implement(workspace, 1, feedback)


def test_at_most_one_implementation_and_two_repairs(tmp_path):
    result = run(tmp_path, AlwaysWrongWorker())
    assert result["status"] == "attempt_limit"
    assert result["attempts"] == 3
    assert len([e for e in result["trace"] if e["node"] == "implement"]) == 3


class FailingBaseline:
    def check(self, workspace, phase):
        assert phase == "baseline"
        return ProcessResult(1, "existing failure", "")


def test_existing_failure_prevents_model_invocation(tmp_path):
    worker = RecordingWorker()
    result = run(tmp_path, worker, FailingBaseline())
    assert result["status"] == "baseline_failed"
    assert result["attempts"] == 0
    assert worker.calls == []


class BrokenWorker(DemoWorker):
    def implement(self, workspace, attempt, feedback):
        raise InfrastructureError("authentication or worker timeout")


def test_worker_infrastructure_error_is_not_retried(tmp_path):
    result = run(tmp_path, BrokenWorker())
    assert result["status"] == "infrastructure_error"
    assert result["attempts"] == 1
    assert [e["node"] for e in result["trace"]] == ["baseline", "implement"]


class BrokenChecker:
    def check(self, workspace, phase):
        raise InfrastructureError("missing interpreter")


def test_test_infrastructure_error_is_not_retried(tmp_path):
    result = run(tmp_path, checker=BrokenChecker())
    assert result["status"] == "infrastructure_error"
    assert result["attempts"] == 0


class FailsOnVerification(PytestChecker):
    def check(self, workspace, phase):
        if phase == "acceptance":
            raise InfrastructureError("verification timed out")
        return super().check(workspace, phase)


def test_verification_timeout_does_not_trigger_another_implementation(tmp_path):
    worker = RecordingWorker()
    result = run(tmp_path, worker, FailsOnVerification())
    assert result["status"] == "infrastructure_error"
    assert result["attempts"] == 1
    assert len(worker.calls) == 1


class ModifiesFilesDuringVerification(PytestChecker):
    def check(self, workspace, phase):
        if phase == "acceptance":
            (workspace / "unexpected.py").write_text("changed during tests", encoding="utf-8")
        return super().check(workspace, phase)


def test_scope_is_checked_after_tests_too(tmp_path):
    result = run(tmp_path, checker=ModifiesFilesDuringVerification())
    assert result["status"] == "scope_violation"
    assert result["attempts"] == 1


class FailsDuringRepair(DemoWorker):
    def implement(self, workspace, attempt, feedback):
        if attempt == 2:
            raise OSError("disk is unavailable")
        return super().implement(workspace, attempt, feedback)


def test_late_os_error_preserves_attempts_and_history(tmp_path):
    result = run(tmp_path, FailsDuringRepair())
    assert result["status"] == "infrastructure_error"
    assert result["attempts"] == 2
    assert [event["node"] for event in result["trace"]] == [
        "baseline", "implement", "verify", "implement"
    ]
    assert result["duration_s"] > 0


class EscapingWorker(DemoWorker):
    def implement(self, workspace, attempt, feedback):
        (workspace / "new_test.py").write_text("assert True", encoding="utf-8")
        return super().implement(workspace, 2, feedback)


def test_out_of_scope_file_blocks_success(tmp_path):
    result = run(tmp_path, EscapingWorker())
    assert result["status"] == "scope_violation"
    assert result["attempts"] == 1


class GitChangingWorker(DemoWorker):
    def implement(self, workspace, attempt, feedback):
        (workspace / ".git/HEAD").write_text("ref: refs/heads/unwanted\n", encoding="utf-8")
        return super().implement(workspace, 2, feedback)


def test_git_metadata_changes_are_blocked(tmp_path):
    assert run(tmp_path, GitChangingWorker())["status"] == "scope_violation"


class RemovingWorker(DemoWorker):
    def implement(self, workspace, attempt, feedback):
        (workspace / "question.py").unlink()
        return "deleted"


def test_removing_the_target_is_blocked(tmp_path):
    assert run(tmp_path, RemovingWorker())["status"] == "scope_violation"


def test_completed_request_is_not_run_again_even_after_restart(tmp_path):
    request_id = str(uuid.uuid4())
    first = run(tmp_path, request_id=request_id)
    worker = RecordingWorker()
    second = run(tmp_path, worker=worker, request_id=request_id)
    assert second == first
    assert worker.calls == []
    assert json.loads((tmp_path / request_id / "result.json").read_text(encoding="utf-8"))["status"] == "review_ready"


def test_interrupted_request_is_not_automatically_repeated(tmp_path):
    request_id = str(uuid.uuid4())
    (tmp_path / request_id).mkdir()
    with pytest.raises(JobConflict, match="ID already used"):
        run(tmp_path, request_id=request_id)


@pytest.mark.parametrize("task_id,request_id", [("shell-command", str(uuid.uuid4())),
                                                (TASK_ID, "../../outside")])
def test_invalid_tasks_and_ids_do_not_create_workspaces(tmp_path, task_id, request_id):
    with pytest.raises(ValueError):
        run_job(request_id, task_id, tmp_path, DemoWorker(), PytestChecker())
    assert list(tmp_path.iterdir()) == []


def test_original_fixture_and_rag_are_not_modified(tmp_path):
    from experiments.dev_loop.adapters import LAB

    source = LAB / "fixture/question.py"
    original = source.read_bytes()
    result = run(tmp_path)
    assert source.read_bytes() == original
    assert Path(result["workspace"]).parent.parent == tmp_path
