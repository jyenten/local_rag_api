"""Controlled Docker fault injection, genuine test feedback, then live Codex repair."""

from __future__ import annotations

import argparse
import hashlib
import json
import uuid
from pathlib import Path

from .adapters import LAB, TASK_ID
from .codex_docker import DockerCodexWorker
from .docker_adapters import DockerDemoWorker, DockerPytestChecker, DockerRunner, candidate_source
from .workflow import run_job


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ControlledRepairWorker:
    """The first candidate is scripted; all subsequent implementations use Codex."""

    name = "codex-controlled-repair-docker"
    isolation = "docker"

    def __init__(self, injected_worker, codex_worker):
        self.injected_worker = injected_worker
        self.codex_worker = codex_worker
        self.injections: list[dict] = []
        self.repair_inputs: list[dict] = []

    @property
    def image_id(self):
        return self.codex_worker.image_id

    @property
    def attempt_records(self):
        return self.codex_worker.attempt_records

    def implement(self, workspace: Path, attempt: int, feedback: str) -> str:
        if attempt == 1:
            self.injected_worker.implement(workspace, attempt, feedback)
            prompt_source = candidate_source(workspace)  # Validate before saving evidence.
            source = (workspace / "question.py").read_bytes()
            artifact = workspace.parent / "injected-question.py"
            with artifact.open("xb") as stream:
                stream.write(source)
            self.injections.append({"attempt": attempt, "origin": "scripted-demo-docker",
                                    "artifact": str(artifact),
                                    "prompt_source_sha256": digest(prompt_source),
                                    "code_sha256": hashlib.sha256(source).hexdigest()})
            return "Controlled fault injection by scripted Docker demo worker; Codex was not invoked."
        self.repair_inputs.append({"attempt": attempt,
                                   "source_sha256": digest(candidate_source(workspace)),
                                   "feedback_sha256": digest(feedback)})
        return self.codex_worker.implement(workspace, attempt, feedback)


def observed_repair(report: dict, worker: ControlledRepairWorker) -> bool:
    """A passing final state alone must not pass the controlled repair experiment."""
    failures = [e for e in report["trace"] if e["node"] == "verify"
                and e.get("attempt") == 1 and e.get("returncode") == 1]
    if len(worker.injections) != 1 or len(failures) != 1:
        return False
    first_repair = next((r for r in worker.repair_inputs if r["attempt"] == 2), None)
    if first_repair is None or first_repair["feedback_sha256"] != digest(failures[0]["output"]):
        return False
    if first_repair["source_sha256"] != worker.injections[0]["prompt_source_sha256"]:
        return False
    completed_attempts = {r["attempt"] for r in worker.attempt_records if r.get("completed") is True}
    return any(e["node"] == "verify" and e.get("attempt", 0) > 1
               and e.get("attempt") in completed_attempts and e.get("returncode") == 0
               for e in report["trace"])


def run_probe(output_root: Path | None = None, *, codex_worker=None,
              injected_worker=None, checker=None) -> dict:
    # No arbitrary task, executable, host directory mount or public API input is added.
    runner = DockerRunner()
    live = codex_worker if codex_worker is not None else DockerCodexWorker()
    injected = injected_worker if injected_worker is not None else DockerDemoWorker(runner)
    checker = checker if checker is not None else DockerPytestChecker(runner)
    worker = ControlledRepairWorker(injected, live)
    root = output_root if output_root is not None else LAB / ".runs/repair-probe"
    # A fresh UUID for every probe; no completed run is overwritten or replayed.
    report = run_job(str(uuid.uuid4()), TASK_ID, root, worker, checker)
    observed = observed_repair(report, worker)
    report.update(
        measurement="controlled-repair", injected_attempts=len(worker.injections),
        fault_injections=worker.injections, repair_inputs=worker.repair_inputs,
        injection_image=getattr(getattr(injected, "runner", None), "image_id", None),
        codex_worker_invocations=len(worker.repair_inputs),
        codex_completed_invocations=sum(r.get("completed") is True for r in worker.attempt_records),
        model_calls=None, repair_path_observed=observed,
        probe_passed=report["status"] == "review_ready" and observed,
    )
    result = Path(report["workspace"]).parent / "result.json"
    temporary = result.with_suffix(".tmp")
    temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(result)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="One controlled Docker fault injection and live Codex repair")
    parser.parse_args(argv)  # Help or unsupported options must not trigger a model invocation.
    report = run_probe()
    print(json.dumps(report, indent=2, ensure_ascii=True))
    return 0 if report["probe_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
