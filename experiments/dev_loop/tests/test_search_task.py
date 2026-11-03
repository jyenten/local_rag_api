"""Second fixed task: independent contract, task routing and isolation boundaries."""

import json
import os
import sys
import uuid

import pytest
from fastapi.testclient import TestClient

from experiments.dev_loop import __main__ as cli, api, batch
from experiments.dev_loop.adapters import (
    LAB, DemoWorker, InfrastructureError, ProcessResult, process_environment,
    run_process, validate_test_evidence,
)
from experiments.dev_loop.codex_docker import DockerCodexWorker, parse_response
from experiments.dev_loop.docker_adapters import DockerPytestChecker, DockerRunner
from experiments.dev_loop.tasks import NORMALIZE, SEARCH_REQUEST, get_task
from experiments.dev_loop.workflow import run_job

TASK = SEARCH_REQUEST.task_id
TOKEN = "synthetic-search-token-at-least-24-characters"
# A trusted reference for harness tests only, never supplied as a live model answer.
CORRECT_SOURCE = '''def build_search_request(query: str, top_k: int = 5) -> dict:
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    normalized = " ".join(query.split())
    if not normalized:
        raise ValueError("empty query")
    if type(top_k) is not int:
        raise TypeError("top_k must be an integer")
    if not 1 <= top_k <= 20:
        raise ValueError("top_k out of range")
    return {"query": normalized, "top_k": top_k}
'''


def evidence(phase="acceptance", count=28):
    return "<testsuites><testsuite>" + "".join(
        "<testcase><skipped/></testcase>" if phase == "baseline" and i >= 2 else "<testcase/>"
        for i in range(count)) + "</testsuite></testsuites>"


def trusted_checks(workspace, phase):
    """Host execution here is only of known test fixtures/reference, never model output."""
    env = process_environment()
    env.update(DEV_LOOP_WORKSPACE=str(workspace), DEV_LOOP_PHASE=phase,
               PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1")
    result = run_process([
        sys.executable, "-m", "pytest", "-q", "-c", str(LAB / "checks/pytest.ini"),
        "--confcutdir", str(LAB / "checks"), "-p", "no:cacheprovider",
        "--junitxml", str(workspace.parent / "search-checks.xml"), str(LAB / "checks" / SEARCH_REQUEST.checks),
    ], workspace, timeout=20, env=env)
    return result


def test_independent_contract_counts_baseline_failures_and_complete_acceptance(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "question.py").write_bytes((LAB / "fixture" / SEARCH_REQUEST.fixture).read_bytes())
    baseline = trusted_checks(workspace, "baseline")
    assert baseline.returncode == 0 and "2 passed, 26 skipped" in baseline.stdout
    validate_test_evidence((tmp_path / "search-checks.xml").read_bytes(), "baseline",
                           expected_cases=SEARCH_REQUEST.test_count, baseline_skips=SEARCH_REQUEST.baseline_skips)
    assert trusted_checks(workspace, "acceptance").returncode == 1
    (workspace / "question.py").write_bytes(CORRECT_SOURCE.encode("utf-8"))
    result = trusted_checks(workspace, "acceptance")
    assert result.returncode == 0 and "28 passed" in result.stdout
    validate_test_evidence((tmp_path / "search-checks.xml").read_bytes(), "acceptance", expected_cases=28)


@pytest.mark.parametrize("mutant", [
    CORRECT_SOURCE.replace("type(top_k) is not int", "not isinstance(top_k, int)"),
    CORRECT_SOURCE.replace('normalized = " ".join(query.split())', 'normalized = query.strip()'),
    CORRECT_SOURCE.replace('normalized = " ".join(query.split())', 'normalized = " ".join(query.split()).lower()'),
    CORRECT_SOURCE.replace('    if not 1 <= top_k <= 20:\n        raise ValueError("top_k out of range")',
                           '    top_k = max(1, min(top_k, 20))'),
])
def test_contract_rejects_bool_strip_only_case_changes_and_clamping(tmp_path, mutant):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "question.py").write_text(mutant, encoding="utf-8")
    result = trusted_checks(workspace, "acceptance")
    assert result.returncode == 1 and "failed" in result.stdout


@pytest.mark.parametrize("task_id", ["../../checks.py", "shell-command", "unknown"])
def test_task_registry_is_a_fixed_allowlist(task_id):
    with pytest.raises(ValueError, match="Unknown fixed"):
        get_task(task_id)


def test_wrong_adapters_are_rejected_before_workspace_creation(tmp_path):
    with pytest.raises(ValueError, match="configured"):
        run_job(str(uuid.uuid4()), TASK, tmp_path / "runs", DemoWorker(),
                DockerPytestChecker(DockerRunner(), TASK))
    assert not (tmp_path / "runs").exists()


def test_new_task_source_requires_the_new_function_name():
    from experiments.dev_loop.tests.test_codex_docker import events, jsonl

    output = jsonl(events(CORRECT_SOURCE))
    assert parse_response(output, SEARCH_REQUEST.function_name)[0] == CORRECT_SOURCE
    with pytest.raises(InfrastructureError, match="artifact"):
        parse_response(output)


@pytest.mark.parametrize("reported_task,count", [(None, 28), (NORMALIZE.task_id, 28), (TASK, 6)])
def test_old_or_misidentified_checker_cannot_report_success(monkeypatch, tmp_path, reported_task, count):
    (tmp_path / "question.py").write_text(CORRECT_SOURCE, encoding="utf-8")
    runner = DockerRunner(SEARCH_REQUEST.checker_image)

    def invoke(mode, payload, cwd):
        assert payload["task_id"] == TASK
        return ProcessResult(0, "", ""), {"task_id": reported_task, "returncode": 0,
            "stdout": "claims success", "stderr": "", "junit": evidence(count=count)}

    monkeypatch.setattr(runner, "invoke", invoke)
    with pytest.raises(InfrastructureError):
        DockerPytestChecker(runner, TASK).check(tmp_path, "acceptance")


def test_incomplete_new_task_baseline_stops_before_codex(monkeypatch, tmp_path):
    runner = DockerRunner(SEARCH_REQUEST.checker_image)
    monkeypatch.setattr(runner, "invoke", lambda *a: (ProcessResult(0, "", ""), {
        "task_id": TASK, "returncode": 0, "stdout": "", "stderr": "", "junit": evidence("baseline", 6)}))
    live = DockerCodexWorker(task_id=TASK)
    monkeypatch.setattr(live, "implement", lambda *a: pytest.fail("Model must not run"))
    report = run_job(str(uuid.uuid4()), TASK, tmp_path, live, DockerPytestChecker(runner, TASK))
    assert report["status"] == "infrastructure_error" and report["attempts"] == 0


def test_live_worker_prompt_and_graph_select_second_task_without_host_execution(monkeypatch, tmp_path):
    from experiments.dev_loop.tests.test_codex_docker import transport, events

    calls = transport(monkeypatch, tmp_path, events(CORRECT_SOURCE))
    worker = DockerCodexWorker(task_id=TASK)
    runner = DockerRunner(SEARCH_REQUEST.checker_image)
    phases = []

    def invoke(mode, payload, cwd):
        assert payload["task_id"] == TASK and mode == "check"
        phases.append(payload["phase"])
        if payload["phase"] == "baseline":
            assert payload["source"] == (LAB / "fixture/search_request.py").read_text(encoding="utf-8")
        else:
            assert payload["source"] == CORRECT_SOURCE
        runner.image_id = "sha256:" + "b" * 64
        return ProcessResult(0, "", ""), {"task_id": TASK, "returncode": 0, "stdout": "checks",
                                           "stderr": "", "junit": evidence(payload["phase"])}

    monkeypatch.setattr(runner, "invoke", invoke)
    report = run_job(str(uuid.uuid4()), TASK, tmp_path / "runs", worker, DockerPytestChecker(runner, TASK))
    assert report["status"] == "review_ready" and report["task_id"] == TASK
    assert report["backend"] == "codex-docker" and report["attempts"] == 1
    assert phases == ["baseline", "acceptance"]
    prompt = next(k["input_text"] for c, k in calls if c[1] == "start")
    assert "build_search_request(query: str, top_k: int = 5)" in prompt
    assert "1 <= top_k <= 20" in prompt and "reject bool" in prompt
    assert "normalize_question(value:" not in prompt


@pytest.mark.parametrize("args", [["--backend", "demo", "--isolation", "docker"],
                                 ["--backend", "codex", "--isolation", "host"]])
def test_second_task_rejects_unsupported_demo_or_host_profiles(monkeypatch, args):
    monkeypatch.setattr(sys, "argv", ["dev-loop", "--task", TASK, *args])
    with pytest.raises(SystemExit) as exc:
        cli.main()
    assert exc.value.code == 2


def test_cli_selects_new_checker_image_and_task(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dev-loop", "--task", TASK, "--backend", "codex", "--isolation", "docker"])

    def job(request_id, task_id, runs_dir, worker, checker):
        assert task_id == worker.task_id == checker.task_id == TASK
        assert checker.runner.image == "local-rag-dev-loop:2"
        return {"status": "review_ready"}

    monkeypatch.setattr(cli, "run_job", job)
    assert cli.main() == 0


def test_api_requires_service_task_and_rejects_unknown_inputs(monkeypatch, tmp_path):
    worker = DockerCodexWorker(task_id=TASK)
    checker = DockerPytestChecker(DockerRunner(SEARCH_REQUEST.checker_image), TASK)
    calls = []

    def job(request_id, task_id, runs_dir, selected_worker, selected_checker):
        calls.append(task_id)
        return {"status": "review_ready", "task_id": task_id}

    monkeypatch.setattr(api, "run_job", job)
    client = TestClient(api.create_app(worker, checker, tmp_path, TOKEN))
    assert client.get("/health").json()["task_id"] == TASK
    for task_id in [NORMALIZE.task_id, "../../checks.py"]:
        assert client.post("/runs", headers={"X-Dev-Loop-Token": TOKEN},
                           json={"request_id": str(uuid.uuid4()), "task_id": task_id}).status_code == 422
    assert calls == []
    response = client.post("/runs", headers={"X-Dev-Loop-Token": TOKEN},
                           json={"request_id": str(uuid.uuid4()), "task_id": TASK})
    assert response.status_code == 200 and calls == [TASK]


def test_api_refuses_mixed_task_adapters(tmp_path):
    with pytest.raises(ValueError, match="same fixed task"):
        api.create_app(DockerCodexWorker(), DockerPytestChecker(DockerRunner(), TASK), tmp_path, TOKEN)


def test_batch_records_the_selected_task_and_labels_report(monkeypatch, tmp_path):
    def job(request_id, task_id, runs_dir, worker, checker):
        assert task_id == TASK
        return {"request_id": request_id, "backend": worker.name, "status": "review_ready",
                "attempts": 1, "duration_s": .1, "trace": []}

    monkeypatch.setattr(batch, "run_job", job)
    report = batch.run_batch(1, tmp_path / "batch", DockerCodexWorker(task_id=TASK),
                             DockerPytestChecker(DockerRunner(SEARCH_REQUEST.checker_image), TASK))
    assert report["task_id"] == report["rows"][0]["task_id"] == TASK
    assert TASK in batch.render_report(report, tmp_path / "batch").read_text(encoding="utf-8")


def test_search_workflow_is_manual_fixed_task_and_has_no_credentials():
    workflow = json.loads((LAB / "n8n-search-workflow.json").read_text(encoding="utf-8"))
    assert workflow["active"] is False
    calls = [n for n in workflow["nodes"] if n["type"] == "n8n-nodes-base.httpRequest"]
    assert len(calls) == 1 and calls[0]["retryOnFail"] is False
    assert "credentials" not in calls[0]
    parameters = calls[0]["parameters"]
    assert parameters["method"] == "POST"
    assert parameters["url"] == "http://host.docker.internal:8765/runs"
    assert parameters["genericAuthType"] == "httpHeaderAuth"
    assert "task_id: 'build-search-request'" in parameters["jsonBody"]
    assert "$execution.id" in parameters["jsonBody"]
    assert parameters["options"]["timeout"] == 900000


live_search = pytest.mark.skipif(os.environ.get("DEV_LOOP_SEARCH_DOCKER_TESTS") != "1",
                                reason="Opt in after building local-rag-dev-loop:2")


@live_search
def test_live_new_task_baseline_failure_and_acceptance_in_docker(tmp_path):
    checker = DockerPytestChecker(DockerRunner(SEARCH_REQUEST.checker_image), TASK)
    (tmp_path / "question.py").write_bytes((LAB / "fixture/search_request.py").read_bytes())
    assert checker.check(tmp_path, "baseline").returncode == 0
    assert checker.check(tmp_path, "acceptance").returncode == 1
    (tmp_path / "question.py").write_bytes(CORRECT_SOURCE.encode("utf-8"))
    assert checker.check(tmp_path, "acceptance").returncode == 0


@live_search
def test_live_new_checker_image_preserves_original_task(tmp_path):
    checker = DockerPytestChecker(DockerRunner(SEARCH_REQUEST.checker_image))
    (tmp_path / "question.py").write_bytes((LAB / "fixture/question.py").read_bytes())
    assert checker.check(tmp_path, "baseline").returncode == 0
    DemoWorker().implement(tmp_path, 2, "")  # Known scripted text, no host execution.
    assert checker.check(tmp_path, "acceptance").returncode == 0
