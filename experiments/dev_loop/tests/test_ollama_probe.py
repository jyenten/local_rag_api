import io
import json

import pytest

from experiments.dev_loop import ollama_probe as probe
from experiments.dev_loop.adapters import InfrastructureError, ProcessResult

SOURCE = '''def normalize_question(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Input cannot be empty after stripping whitespace.")
    return stripped
'''


class Checker:
    image_id = "sha256:" + "a" * 64

    def __init__(self, acceptance_code=0):
        self.phases = []
        self.acceptance_code = acceptance_code

    def check(self, workspace, phase):
        self.phases.append(phase)
        if phase == "acceptance":
            assert (workspace / "question.py").read_bytes() == SOURCE.encode("utf-8")
        return ProcessResult(self.acceptance_code if phase == "acceptance" else 0,
                             "6 passed" if phase == "acceptance" else "2 passed, 4 skipped", "")


def transport(monkeypatch, response):
    seen = []

    class Opener:
        def open(self, request, timeout):
            seen.append((request, timeout))
            return io.BytesIO(json.dumps(response).encode("utf-8"))

    monkeypatch.setattr(probe.urllib.request, "build_opener", lambda *args: Opener())
    return seen


def reply(source=SOURCE):
    return {"response": source, "done": True, "done_reason": "stop",
            "total_duration": 3700000000, "prompt_eval_count": 62, "eval_count": 41}


def test_one_request_is_saved_exactly_before_docker_verification(monkeypatch, tmp_path):
    seen = transport(monkeypatch, reply())
    checker = Checker()
    result = probe.run_probe(tmp_path, checker=checker)
    assert result["status"] == "review_ready"
    assert result["model_duration_s"] == 3.7
    assert result["generation_requests"] == 1
    assert result["code_bytes"] == len(SOURCE.encode("utf-8"))
    assert checker.phases == ["baseline", "acceptance"]
    assert len(seen) == 1
    assert seen[0][0].full_url == "http://127.0.0.1:11434/api/generate"
    payload = json.loads(seen[0][0].data)
    assert payload["think"] is False and payload["options"]["num_ctx"] == 4096
    run_dir = tmp_path / next(tmp_path.iterdir()).name
    assert json.loads((run_dir / "response.json").read_text(encoding="utf-8")) == reply()
    assert json.loads((run_dir / "report.json").read_text(encoding="utf-8")) == result
    assert result["runner_image"] == checker.image_id


@pytest.mark.parametrize("source", [None, "", " \n", "# no function\n", "```python\ninvalid\n```", "def broken("])
def test_invalid_or_empty_output_does_not_create_a_candidate(monkeypatch, tmp_path, source):
    transport(monkeypatch, reply(source))
    checker = Checker()
    result = probe.run_probe(tmp_path, checker=checker)
    assert result["status"] == "invalid_model_output"
    assert checker.phases == ["baseline"]
    assert not list(tmp_path.rglob("candidate/question.py"))
    assert len(list(tmp_path.rglob("response.json"))) == 1


def test_missing_docker_stops_before_any_model_request(monkeypatch, tmp_path):
    def forbidden(*args):
        raise AssertionError("Must not call Ollama before Docker baseline")

    class BrokenChecker:
        image_id = None

        def check(self, *args):
            raise InfrastructureError("Docker Engine is offline")

    monkeypatch.setattr(probe, "fetch_response", forbidden)
    result = probe.run_probe(tmp_path, checker=BrokenChecker())
    assert result["status"] == "infrastructure_error"
    assert result["generation_requests"] == 0
    assert not list(tmp_path.rglob("candidate/question.py"))


def test_a_test_failure_is_not_reported_as_success_or_retried(monkeypatch, tmp_path):
    seen = transport(monkeypatch, reply())
    result = probe.run_probe(tmp_path, checker=Checker(acceptance_code=1))
    assert result["status"] == "verification_failed"
    assert len(seen) == 1
    assert result["repair_attempts"] == 0


def test_source_is_parsed_but_never_executed_on_host():
    hostile = "raise RuntimeError('Do not execute on host')\n" + SOURCE
    assert probe.validate_source(reply(hostile)) == hostile


def test_output_token_limit_is_not_accepted_as_completed_code(monkeypatch, tmp_path):
    response = reply()
    response["done_reason"] = "length"
    transport(monkeypatch, response)
    result = probe.run_probe(tmp_path, checker=Checker())
    assert result["status"] == "invalid_model_output"
    assert not list(tmp_path.rglob("candidate/question.py"))
