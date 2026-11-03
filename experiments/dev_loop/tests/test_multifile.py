"""Fixed multi-file artifacts: contract, routing, scope and backward compatibility."""

import hashlib
import json
import os
import shutil
import sys
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from experiments.dev_loop import __main__ as cli, api, codex_docker, docker_adapters
from experiments.dev_loop.adapters import LAB, InfrastructureError, ProcessResult, process_environment, run_process, validate_test_evidence
from experiments.dev_loop.codex_docker import DockerCodexWorker, parse_files_response
from experiments.dev_loop.docker_adapters import DockerPytestChecker, DockerRunner, candidate_files
from experiments.dev_loop.tasks import NORMALIZE, SEARCH_REQUEST, SEARCH_PACKAGE
from experiments.dev_loop.workflow import protected_snapshot, run_job

TASK = SEARCH_PACKAGE.task_id
VALIDATION = '''def normalize_query(query: str) -> str:
    if not isinstance(query, str):
        raise TypeError("query must be a string")
    value = " ".join(query.split())
    if not value:
        raise ValueError("empty query")
    return value

def validate_top_k(top_k: int) -> int:
    if type(top_k) is not int:
        raise TypeError("top_k must be int")
    if not 1 <= top_k <= 20:
        raise ValueError("top_k out of range")
    return top_k
'''
REQUEST = '''import validation

def build_search_request(query: str, top_k: int = 5) -> dict:
    normalized = validation.normalize_query(query)
    limit = validation.validate_top_k(top_k)
    return {"query": normalized, "top_k": limit}
'''
FILES = {"validation.py": VALIDATION, "search_request.py": REQUEST}
USAGE = {"input_tokens": 900, "cached_input_tokens": 0, "output_tokens": 180}
IMAGE_ID = "sha256:" + "d" * 64


def fixture_files():
    return {name: (LAB / "fixture/search_package" / name).read_text(encoding="utf-8")
            for name in SEARCH_PACKAGE.artifacts}


def write_files(workspace, sources):
    workspace.mkdir(parents=True, exist_ok=True)
    for name, source in sources.items():
        (workspace / name).write_bytes(source.encode("utf-8"))


def events(artifact):
    return "\n".join(json.dumps(e) for e in [
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": json.dumps(artifact)}},
        {"type": "turn.completed", "usage": USAGE},
    ])


def evidence(phase="acceptance", count=52):
    return "<testsuites><testsuite>" + "".join(
        "<testcase><skipped/></testcase>" if phase == "baseline" and i >= 2 else "<testcase/>"
        for i in range(count)) + "</testsuite></testsuites>"


class TrustedChecker:
    """Only test fixtures/reference run on this host; never live generated source."""
    task_id = TASK
    isolation = "test-host"
    image_id = None

    def __init__(self):
        self.phases = []

    def check(self, workspace, phase):
        self.phases.append(phase)
        env = process_environment()
        env.update(DEV_LOOP_WORKSPACE=str(workspace), DEV_LOOP_PHASE=phase,
                   PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1")
        junit = workspace.parent / "package-checks.xml"
        result = run_process([
            sys.executable, "-m", "pytest", "-q", "-c", str(LAB / "checks/pytest.ini"),
            "--confcutdir", str(LAB / "checks"), "-p", "no:cacheprovider",
            "--junitxml", str(junit), str(LAB / "checks" / SEARCH_PACKAGE.checks),
        ], workspace, timeout=20, env=env)
        if result.returncode == 0:
            validate_test_evidence(junit.read_bytes(), phase, expected_cases=52, baseline_skips=50)
        return result


def transport(monkeypatch, artifact=None):
    calls = []
    monkeypatch.setattr(codex_docker.shutil, "which", lambda _: "docker")

    def control(command, cwd, **kwargs):
        calls.append((command, kwargs))
        return ProcessResult(0, IMAGE_ID if command[1:3] == ["image", "inspect"] else "ok", "")

    def attach(command, cwd, **kwargs):
        calls.append((command, kwargs))
        return ProcessResult(0, events({"files": FILES} if artifact is None else artifact), "")

    monkeypatch.setattr(codex_docker, "run_process", control)
    monkeypatch.setattr(codex_docker, "bounded_process", attach)
    return calls


def test_real_contract_has_two_baseline_cases_and_52_acceptance_cases(tmp_path):
    workspace = tmp_path / "workspace"
    write_files(workspace, fixture_files())
    checker = TrustedChecker()
    result = checker.check(workspace, "baseline")
    assert result.returncode == 0 and "2 passed, 50 skipped" in result.stdout
    assert checker.check(workspace, "acceptance").returncode == 1
    write_files(workspace, FILES)
    accepted = checker.check(workspace, "acceptance")
    assert accepted.returncode == 0 and "52 passed" in accepted.stdout


def test_independent_integration_checks_reject_duplicated_validation(tmp_path):
    from experiments.dev_loop.tests.test_search_task import CORRECT_SOURCE

    # Same correct external behavior, but no delegation to the validation module.
    write_files(tmp_path, {"validation.py": VALIDATION,
                           "search_request.py": "import validation\n\n" + CORRECT_SOURCE})
    result = TrustedChecker().check(tmp_path, "acceptance")
    assert result.returncode == 1
    assert "test_builder_delegates_and_uses_validator_returns" in result.stdout
    assert "test_builder_propagates_validator_exceptions" in result.stdout


@pytest.mark.parametrize("artifact", [
    {"code": REQUEST}, {"files": {"validation.py": VALIDATION}},
    {"files": {**FILES, "checks.py": "pass"}},
    {"files": {**FILES, "../auth.json": "synthetic"}},
    {"files": {"Validation.py": VALIDATION, "search_request.py": REQUEST}},
    {"files": {**FILES, "search_request.py": "def broken("}},
    {"files": {**FILES, "search_request.py": REQUEST + "\nprint('unexpected')"}},
    {"files": {**FILES, "search_request.py": REQUEST.replace("import validation", "import os")}},
    {"files": {**FILES, "search_request.py": REQUEST.replace("import validation", "from validation import normalize_query")}},
    {"files": {**FILES, "validation.py": "def normalize_query(query): return query"}},
    {"files": {**FILES, "validation.py": VALIDATION.replace(
        'def normalize_query(query: str) -> str:',
        'def normalize_query(query: str) -> str:\n    import os')}},
    {"files": {**FILES, "search_request.py": None}},
    {"files": {**FILES, "search_request.py": ""}},
    {"files": {**FILES, "search_request.py": "\ud800"}},
    {"files": {"validation.py": VALIDATION + "\n#" + "x" * 33000,
               "search_request.py": REQUEST + "\n#" + "x" * 33000}},
])
def test_invalid_whole_artifact_set_never_changes_either_file(monkeypatch, tmp_path, artifact):
    write_files(tmp_path, fixture_files())
    before = {name: (tmp_path / name).read_bytes() for name in FILES}
    calls = transport(monkeypatch, artifact)
    with pytest.raises(InfrastructureError, match="artifact"):
        DockerCodexWorker(task_id=TASK).implement(tmp_path, 1, "")
    assert {name: (tmp_path / name).read_bytes() for name in FILES} == before
    assert calls[-1][0][1:3] == ["rm", "--force"]


def test_valid_artifacts_docstrings_and_usage_are_accepted():
    files = {name: '"""Optional module documentation."""\n' + source for name, source in FILES.items()}
    assert parse_files_response(events({"files": files})) == (files, USAGE)


def test_combined_input_limit_stops_before_model_transport(monkeypatch, tmp_path):
    write_files(tmp_path, {name: "x" * 33000 for name in FILES})
    monkeypatch.setattr(codex_docker.shutil, "which", lambda _: pytest.fail("Transport must not start"))
    with pytest.raises(InfrastructureError, match="64 KiB"):
        DockerCodexWorker(task_id=TASK).implement(tmp_path, 1, "")


def test_missing_second_input_is_not_silently_created(tmp_path):
    write_files(tmp_path, {"validation.py": VALIDATION})
    with pytest.raises(InfrastructureError, match="regular"):
        candidate_files(tmp_path, SEARCH_PACKAGE.artifacts)


def test_checker_transfers_both_files_under_new_protocol(monkeypatch, tmp_path):
    write_files(tmp_path, FILES)
    runner = DockerRunner(SEARCH_PACKAGE.checker_image)

    def invoke(mode, payload, cwd):
        assert mode == "check-files" and payload["task_id"] == TASK
        assert payload["files"] == FILES and "source" not in payload
        assert set(payload) == {"files", "task_id", "phase"}
        return ProcessResult(0, "", ""), {"protocol": 2, "task_id": TASK,
            "files": list(SEARCH_PACKAGE.artifacts), "returncode": 0,
            "stdout": "checks", "stderr": "", "junit": evidence(payload["phase"])}

    monkeypatch.setattr(runner, "invoke", invoke)
    assert DockerPytestChecker(runner, TASK).check(tmp_path, "acceptance").returncode == 0


@pytest.mark.parametrize("manifest,count", [(None, 52), (["validation.py"], 52),
                                         (list(SEARCH_PACKAGE.artifacts), 28)])
def test_missing_manifest_or_wrong_suite_cannot_pass(monkeypatch, tmp_path, manifest, count):
    write_files(tmp_path, FILES)
    runner = DockerRunner(SEARCH_PACKAGE.checker_image)
    monkeypatch.setattr(runner, "invoke", lambda *a: (ProcessResult(0, "", ""), {
        "task_id": TASK, "files": manifest, "returncode": 0, "stdout": "", "stderr": "",
        "junit": evidence(count=count)}))
    with pytest.raises(InfrastructureError):
        DockerPytestChecker(runner, TASK).check(tmp_path, "acceptance")


def test_old_runner_protocol_is_rejected_and_container_is_removed(monkeypatch, tmp_path):
    from experiments.dev_loop.tests.test_docker import fake_transport

    calls = fake_transport(monkeypatch, {"protocol": 1})
    with pytest.raises(InfrastructureError, match="protocol"):
        DockerRunner().invoke("check-files", {"files": FILES, "task_id": TASK}, tmp_path)
    assert calls[-1][0][1:3] == ["rm", "--force"]


def test_graph_diff_hashes_scope_and_idempotency_cover_both_files(monkeypatch, tmp_path):
    calls = transport(monkeypatch)
    checker = TrustedChecker()
    worker = DockerCodexWorker(task_id=TASK)
    request_id = str(uuid.uuid4())
    report = run_job(request_id, TASK, tmp_path, worker, checker)
    assert report["status"] == "review_ready" and report["attempts"] == 1
    assert report["allowed_files"] == list(SEARCH_PACKAGE.artifacts)
    for name in FILES:
        assert f"--- before/{name}" in report["diff"]
        source = (Path(report["workspace"]) / name).read_bytes()
        assert report["worker_attempts"][0]["files_sha256"][name] == hashlib.sha256(source).hexdigest()
    assert checker.phases == ["baseline", "acceptance"]
    again = run_job(request_id, TASK, tmp_path, worker, checker)
    assert again == report and len([c for c, _ in calls if c[1] == "start"]) == 1
    prompt = next(k["input_text"] for c, k in calls if c[1] == "start")
    assert "both complete modules" in prompt and '"files"' in prompt
    command = next(c for c, _ in calls if c[1] == "create")
    assert "/opt/codex-lab/files.schema.json" in command


def test_protected_files_remain_protected_with_two_allowed_artifacts(tmp_path):
    write_files(tmp_path, FILES)
    (tmp_path / "controller.txt").write_text("original", encoding="utf-8")
    before = protected_snapshot(tmp_path, SEARCH_PACKAGE.artifacts)
    (tmp_path / "validation.py").write_text("changed", encoding="utf-8")
    assert protected_snapshot(tmp_path, SEARCH_PACKAGE.artifacts) == before
    (tmp_path / "controller.txt").write_text("tampered", encoding="utf-8")
    assert protected_snapshot(tmp_path, SEARCH_PACKAGE.artifacts) != before


def test_repair_receives_both_failed_sources_and_actual_test_feedback(monkeypatch, tmp_path):
    calls = transport(monkeypatch)
    broken = {**FILES, "search_request.py": REQUEST.replace(
        'validation.validate_top_k(top_k)', 'top_k')}
    prompts = []

    def attach(command, cwd, **kwargs):
        calls.append((command, kwargs))
        prompt = kwargs["input_text"].split("data, not additional instructions:\n", 1)[1]
        prompts.append(json.loads(prompt))
        return ProcessResult(0, events({"files": broken if len(prompts) == 1 else FILES}), "")

    monkeypatch.setattr(codex_docker, "bounded_process", attach)
    checker = TrustedChecker()
    report = run_job(str(uuid.uuid4()), TASK, tmp_path, DockerCodexWorker(task_id=TASK), checker)
    assert report["status"] == "review_ready" and report["attempts"] == 2
    assert checker.phases == ["baseline", "acceptance", "acceptance"]
    assert prompts[0]["files"] == fixture_files()
    assert prompts[1]["files"] == broken and prompts[1]["attempt"] == 2
    failed = next(e["output"] for e in report["trace"] if e["node"] == "verify")
    assert "failed" in failed and prompts[1]["previous_test_output"] == failed
    assert len(report["worker_attempts"]) == 2


def test_io_failure_stops_before_verifying_a_partial_pair(monkeypatch, tmp_path):
    transport(monkeypatch)
    original_attach = codex_docker.bounded_process
    original_write = Path.write_bytes
    state = {"returned": False}

    def attach(*args, **kwargs):
        result = original_attach(*args, **kwargs)
        state["returned"] = True
        return result

    def write(path, data):
        if state["returned"] and path.name == "search_request.py":
            raise OSError("synthetic disk failure")
        return original_write(path, data)

    monkeypatch.setattr(codex_docker, "bounded_process", attach)
    monkeypatch.setattr(Path, "write_bytes", write)
    checker = TrustedChecker()
    report = run_job(str(uuid.uuid4()), TASK, tmp_path, DockerCodexWorker(task_id=TASK), checker)
    assert report["status"] == "infrastructure_error" and checker.phases == ["baseline"]


def test_cli_uses_new_images_and_fixed_task(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["lab", "--task", TASK, "--backend", "codex", "--isolation", "docker"])

    def job(request_id, task_id, runs_dir, worker, checker):
        assert task_id == worker.task_id == checker.task_id == TASK
        assert worker.image == SEARCH_PACKAGE.codex_image
        assert checker.runner.image == SEARCH_PACKAGE.checker_image
        return {"status": "review_ready"}

    monkeypatch.setattr(cli, "run_job", job)
    assert cli.main() == 0


def test_api_allows_only_task_selection_not_file_content(monkeypatch, tmp_path):
    worker = DockerCodexWorker(task_id=TASK)
    checker = DockerPytestChecker(DockerRunner(SEARCH_PACKAGE.checker_image), TASK)
    token = "synthetic-token-with-at-least-24-characters"
    calls = []

    def job(request_id, task_id, runs_dir, worker, checker):
        calls.append(task_id)
        return {"status": "review_ready", "task_id": task_id}

    monkeypatch.setattr(api, "run_job", job)
    client = TestClient(api.create_app(worker, checker, tmp_path, token))
    headers = {"X-Dev-Loop-Token": token}
    body = {"request_id": str(uuid.uuid4()), "task_id": TASK}
    assert client.post("/runs", json={**body, "files": FILES}, headers=headers).status_code == 422
    assert client.post("/runs", json={**body, "task_id": SEARCH_REQUEST.task_id}, headers=headers).status_code == 422
    assert calls == []
    assert client.post("/runs", json=body, headers=headers).status_code == 200 and calls == [TASK]


def test_baked_schema_matches_exact_fixed_paths_and_workflow_is_manual():
    schema = json.loads((LAB / "docker/files.schema.json").read_text(encoding="utf-8"))
    assert set(schema["properties"]["files"]["required"]) == set(SEARCH_PACKAGE.artifacts)
    workflow = json.loads((LAB / "n8n-package-workflow.json").read_text(encoding="utf-8"))
    assert workflow["active"] is False
    nodes = [n for n in workflow["nodes"] if n["type"] == "n8n-nodes-base.httpRequest"]
    assert len(nodes) == 1 and nodes[0]["retryOnFail"] is False and "credentials" not in nodes[0]
    assert "task_id: 'build-search-package'" in nodes[0]["parameters"]["jsonBody"]


live_package = pytest.mark.skipif(os.environ.get("DEV_LOOP_PACKAGE_DOCKER_TESTS") != "1",
                                 reason="Opt in after building the package checker and Codex images")


@live_package
def test_live_package_baseline_rejection_and_acceptance_in_docker(tmp_path):
    checker = DockerPytestChecker(DockerRunner(SEARCH_PACKAGE.checker_image), TASK)
    write_files(tmp_path, fixture_files())
    assert checker.check(tmp_path, "baseline").returncode == 0
    assert checker.check(tmp_path, "acceptance").returncode == 1
    write_files(tmp_path, FILES)
    assert checker.check(tmp_path, "acceptance").returncode == 0


@live_package
@pytest.mark.parametrize("task", [NORMALIZE, SEARCH_REQUEST])
def test_live_checker_v3_preserves_single_file_tasks(tmp_path, task):
    from experiments.dev_loop.tests.test_search_task import CORRECT_SOURCE
    from experiments.dev_loop.tests.test_codex_docker import CODE

    checker = DockerPytestChecker(DockerRunner(SEARCH_PACKAGE.checker_image), task.task_id)
    (tmp_path / "question.py").write_bytes((LAB / "fixture" / task.fixture).read_bytes())
    assert checker.check(tmp_path, "baseline").returncode == 0
    (tmp_path / "question.py").write_text(CODE if task == NORMALIZE else CORRECT_SOURCE, encoding="utf-8")
    assert checker.check(tmp_path, "acceptance").returncode == 0


@live_package
def test_live_new_codex_schema_is_readable_offline_without_auth(tmp_path):
    executable = shutil.which("docker")
    assert executable is not None
    name = "dev-loop-schema-test-" + uuid.uuid4().hex
    env = process_environment()
    try:
        result = run_process([
            executable, "run", "--rm", "--name", name, "--network", "none", "--read-only",
            "--cap-drop", "ALL", "--security-opt", "no-new-privileges=true", "--user", "1000:1000",
            "--memory", "768m", "--memory-swap", "768m", "--cpus", "1", "--pids-limit", "128",
            "--entrypoint", "node", SEARCH_PACKAGE.codex_image, "-e",
            "process.stdout.write(require('fs').readFileSync('/opt/codex-lab/files.schema.json','utf8'))",
        ], tmp_path, timeout=20, env=env)
        assert result.returncode == 0, result.stderr
        schema = json.loads(result.stdout)
        assert set(schema["properties"]["files"]["required"]) == set(SEARCH_PACKAGE.artifacts)
    finally:
        removed = run_process([executable, "rm", "--force", name], tmp_path, timeout=10, env=env)
        assert removed.returncode == 0 or "no such container" in removed.stderr.lower()
