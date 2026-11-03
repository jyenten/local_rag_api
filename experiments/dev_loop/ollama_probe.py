"""One local generation, immediate evidence saving, then container-only checks."""

from __future__ import annotations

import ast
import hashlib
import json
import time
import uuid
import urllib.request
from pathlib import Path

from .adapters import LAB, InfrastructureError
from .docker_adapters import DockerPytestChecker, DockerRunner, MAX_SOURCE_BYTES

MODEL = "qwen3.5:4b-q4_K_M"
REQUEST = {
    "model": MODEL,
    "prompt": (
        "Write only Python code defining normalize_question(value: str) -> str.\n"
        "Strip leading and trailing whitespace.\n"
        "Raise ValueError if the stripped result is empty.\n"
        "Otherwise return the stripped text.\n"
        "No markdown, explanation, imports or top-level execution."
    ),
    "stream": False,
    "think": False,
    "options": {"num_ctx": 4096, "num_predict": 256, "temperature": 0},
}


class InvalidModelOutput(ValueError):
    pass


def fetch_response(run_dir: Path) -> dict:
    request = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(REQUEST).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    )
    # The fixed loopback request must not be sent through a host HTTP proxy.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=90) as response:
        raw = response.read(524289)
    (run_dir / "response.json").write_bytes(raw)
    if len(raw) > 524288:
        raise InvalidModelOutput("Ollama response exceeded 512 KiB")
    try:
        data = json.loads(raw)
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise InvalidModelOutput("Ollama did not return valid JSON; inspect response.json") from exc
    if not isinstance(data, dict):
        raise InvalidModelOutput("Expected an Ollama response object")
    return data


def validate_source(response: dict) -> str:
    if response.get("done") is not True or response.get("done_reason") != "stop":
        raise InvalidModelOutput("Generation did not finish normally")
    source = response.get("response")
    if not isinstance(source, str) or not source.strip():
        raise InvalidModelOutput("Ollama returned empty code; candidate was not written")
    try:
        size = len(source.encode("utf-8"))
    except UnicodeError as exc:
        raise InvalidModelOutput("Response is not UTF-8 source") from exc
    if size > MAX_SOURCE_BYTES:
        raise InvalidModelOutput("Candidate exceeded 64 KiB")
    try:
        tree = ast.parse(source)
    except (SyntaxError, UnicodeError, ValueError, RecursionError) as exc:
        raise InvalidModelOutput("Response is not valid Python; inspect response.json") from exc
    if not any(isinstance(node, ast.FunctionDef) and node.name == "normalize_question"
               for node in tree.body):
        raise InvalidModelOutput("Response has no top-level normalize_question function")
    return source  # Preserve exact source; do not strip fences or repair the answer.


def run_probe(output_root: Path | None = None, *, checker=None) -> dict:
    started = time.perf_counter()
    root = output_root if output_root is not None else LAB / ".runs/ollama-probe"
    run_dir = root.resolve() / str(uuid.uuid4())
    run_dir.mkdir(parents=True, exist_ok=False)
    if checker is None:
        checker = DockerPytestChecker(DockerRunner())
    report = {"backend": "ollama-probe", "model": MODEL, "status": "pending",
              "generation_requests": 0, "repair_attempts": 0,
              "checker_isolation": "docker", "run_dir": str(run_dir),
              "committed": False, "applied_to_rag": False}
    (run_dir / "request.json").write_text(json.dumps(REQUEST, indent=2), encoding="utf-8")
    try:
        baseline_dir = run_dir / "baseline"
        baseline_dir.mkdir()
        (baseline_dir / "question.py").write_bytes((LAB / "fixture/question.py").read_bytes())
        baseline = checker.check(baseline_dir, "baseline")
        report["baseline"] = {"returncode": baseline.returncode,
                              "stdout": baseline.stdout, "stderr": baseline.stderr}
        if baseline.returncode != 0:
            report["status"] = "baseline_failed"
        else:
            report["generation_requests"] = 1
            response = fetch_response(run_dir)
            duration = response.get("total_duration")
            report.update(
                done_reason=response.get("done_reason"),
                prompt_eval_count=response.get("prompt_eval_count"),
                eval_count=response.get("eval_count"),
                model_duration_s=(round(duration / 1e9, 6)
                                  if type(duration) is int and duration >= 0 else None),
            )
            source = validate_source(response)
            candidate_dir = run_dir / "candidate"
            candidate_dir.mkdir()
            candidate = candidate_dir / "question.py"
            candidate.write_bytes(source.encode("utf-8"))
            report.update(candidate=str(candidate), code_bytes=candidate.stat().st_size,
                          code_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest())
            verified = checker.check(candidate_dir, "acceptance")
            report["acceptance"] = {"returncode": verified.returncode,
                                    "stdout": verified.stdout, "stderr": verified.stderr}
            report["status"] = "review_ready" if verified.returncode == 0 else "verification_failed"
    except InvalidModelOutput as exc:
        report.update(status="invalid_model_output", error=str(exc))
    except (InfrastructureError, OSError) as exc:
        report.update(status="infrastructure_error", error=str(exc))
    finally:
        report["runner_image"] = getattr(checker, "image_id", None)
        report["total_duration_s"] = round(time.perf_counter() - started, 6)
        temporary = run_dir / "report.tmp"
        temporary.write_text(json.dumps(report, ensure_ascii=True, indent=2), encoding="utf-8")
        temporary.replace(run_dir / "report.json")
    return report


def main() -> int:
    report = run_probe()
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["status"] == "review_ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
