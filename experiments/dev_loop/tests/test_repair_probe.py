"""Trusted scripted substitutes exercise the graph; no account or model is used here."""

import hashlib
import json
from pathlib import Path

import pytest

from experiments.dev_loop import repair_probe as probe
from experiments.dev_loop.adapters import LAB, DemoWorker, InfrastructureError, ProcessResult, PytestChecker


class RecordingCodex:
    # Test substitute only. Its candidate source is known/trusted, never from a model.
    image_id = "sha256:" + "c" * 64

    def __init__(self, *, wrong=False, failure=False):
        self.calls = []
        self.attempt_records = []
        self.wrong, self.failure = wrong, failure

    def implement(self, workspace, attempt, feedback):
        self.calls.append((attempt, (workspace / "question.py").read_text(encoding="utf-8"), feedback))
        record = {"attempt": attempt, "completed": False, "usage": None}
        self.attempt_records.append(record)
        if self.failure:
            raise InfrastructureError("synthetic authentication failure")
        DemoWorker().implement(workspace, 1 if self.wrong else 2, feedback)
        record.update(completed=True, usage={"input_tokens": 700, "cached_input_tokens": 0,
                                            "output_tokens": 52})
        return "Test-only scripted Codex substitute"


def run(tmp_path, *, codex=None, checker=None, injected=None):
    return probe.run_probe(tmp_path, codex_worker=codex if codex is not None else RecordingCodex(),
                           checker=checker if checker is not None else PytestChecker(),
                           injected_worker=injected if injected is not None else DemoWorker())


def test_genuine_failed_pytest_output_and_broken_source_reach_repair_worker(tmp_path):
    live = RecordingCodex()
    original = (LAB / "fixture/question.py").read_bytes()
    report = run(tmp_path, codex=live)
    assert report["status"] == "review_ready" and report["attempts"] == 2
    assert report["measurement"] == "controlled-repair"
    assert report["injected_attempts"] == report["codex_worker_invocations"] == 1
    assert report["codex_completed_invocations"] == 1
    assert report["probe_passed"] is True and report["repair_path_observed"] is True
    assert report["model_calls"] is None
    assert [e["node"] for e in report["trace"]] == ["baseline", "implement", "verify", "implement", "verify"]
    assert [e["returncode"] for e in report["trace"] if e["node"] in {"baseline", "verify"}] == [0, 1, 0]
    attempt, source, feedback = live.calls[0]
    assert attempt == 2 and "if not value:" in source and "return value.strip()" in source
    assert "Failed: DID NOT RAISE" in feedback and "3 failed, 3 passed" in feedback
    assert feedback == report["trace"][2]["output"]
    assert report["repair_inputs"][0]["feedback_sha256"] == probe.digest(feedback)
    assert report["repair_inputs"][0]["source_sha256"] == probe.digest(source)
    injection = report["fault_injections"][0]
    artifact = Path(injection["artifact"])
    assert artifact.read_text(encoding="utf-8") == source
    assert injection["code_sha256"] == hashlib.sha256(artifact.read_bytes()).hexdigest()
    assert injection["prompt_source_sha256"] == report["repair_inputs"][0]["source_sha256"]
    assert injection["origin"] == "scripted-demo-docker"
    assert report["worker_attempts"][0]["attempt"] == 2
    assert report["model_usage_measured"] is True
    assert "Codex was not invoked" in report["trace"][1]["note"]
    assert (LAB / "fixture/question.py").read_bytes() == original
    assert report["committed"] is report["applied_to_rag"] is False
    result = Path(report["workspace"]).parent / "result.json"
    assert json.loads(result.read_text(encoding="utf-8")) == report


class BrokenBaseline:
    def check(self, workspace, phase):
        assert phase == "baseline"
        return ProcessResult(1, "existing failure", "")


def test_baseline_failure_does_not_inject_or_invoke_codex(tmp_path):
    live = RecordingCodex()
    report = run(tmp_path, codex=live, checker=BrokenBaseline())
    assert report["status"] == "baseline_failed" and report["probe_passed"] is False
    assert report["injected_attempts"] == report["codex_worker_invocations"] == 0
    assert report["fault_injections"] == report["worker_attempts"] == live.calls == []


class CorrectInjection(DemoWorker):
    def implement(self, workspace, attempt, feedback):
        return super().implement(workspace, 2, feedback)


def test_correct_injection_is_not_falsely_claimed_as_repair_success(tmp_path):
    live = RecordingCodex()
    report = run(tmp_path, codex=live, injected=CorrectInjection())
    assert report["status"] == "review_ready" and report["attempts"] == 1
    assert report["probe_passed"] is report["repair_path_observed"] is False
    assert report["codex_worker_invocations"] == 0 and live.calls == []


def test_failed_repairs_respect_existing_three_attempt_limit(tmp_path):
    live = RecordingCodex(wrong=True)
    report = run(tmp_path, codex=live)
    assert report["status"] == "attempt_limit" and report["attempts"] == 3
    assert report["injected_attempts"] == 1 and report["codex_worker_invocations"] == 2
    assert [a for a, _, _ in live.calls] == [2, 3]
    assert report["probe_passed"] is False


def test_infrastructure_failure_is_not_retried(tmp_path):
    live = RecordingCodex(failure=True)
    report = run(tmp_path, codex=live)
    assert report["status"] == "infrastructure_error" and report["attempts"] == 2
    assert report["codex_worker_invocations"] == 1 and report["codex_completed_invocations"] == 0
    assert report["model_usage_measured"] is report["probe_passed"] is False


@pytest.mark.parametrize("tampered", ["feedback_sha256", "source_sha256"])
def test_tampered_input_evidence_cannot_claim_observed_repair(tampered):
    live = RecordingCodex()
    worker = probe.ControlledRepairWorker(DemoWorker(), live)
    worker.injections = [{"attempt": 1, "prompt_source_sha256": probe.digest("actual source")}]
    worker.repair_inputs = [{"attempt": 2, "feedback_sha256": probe.digest("actual output"),
                             "source_sha256": probe.digest("actual source")}]
    worker.repair_inputs[0][tampered] = probe.digest("different input")
    live.attempt_records = [{"attempt": 2, "completed": True}]
    report = {"trace": [{"node": "verify", "attempt": 1, "returncode": 1, "output": "actual output"},
                         {"node": "verify", "attempt": 2, "returncode": 0}]}
    assert probe.observed_repair(report, worker) is False


@pytest.mark.parametrize("passed", [True, False])
def test_cli_exit_code_requires_probe_evidence_not_only_job_status(monkeypatch, passed):
    monkeypatch.setattr(probe, "run_probe", lambda: {"status": "review_ready", "probe_passed": passed})
    assert probe.main([]) == (0 if passed else 1)


@pytest.mark.parametrize("argv,exit_code", [(["--help"], 0), (["--unknown-option"], 2)])
def test_help_or_invalid_options_do_not_run_probe(monkeypatch, argv, exit_code):
    monkeypatch.setattr(probe, "run_probe", lambda: pytest.fail("Must not invoke probe"))
    with pytest.raises(SystemExit) as exc:
        probe.main(argv)
    assert exc.value.code == exit_code


def test_default_probe_stops_without_docker_before_any_host_or_model_execution(monkeypatch, tmp_path):
    from experiments.dev_loop import docker_adapters

    monkeypatch.setattr(docker_adapters.shutil, "which", lambda _: None)
    report = probe.run_probe(tmp_path)
    assert report["status"] == "infrastructure_error"
    assert report["attempts"] == report["injected_attempts"] == report["codex_worker_invocations"] == 0
    assert report["isolation"] == report["checker_isolation"] == "docker"
    assert report["probe_passed"] is False and report["worker_image"] is None
