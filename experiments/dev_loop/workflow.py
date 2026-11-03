"""A bounded repair loop. Only LangGraph decides whether to retry."""

from __future__ import annotations

import difflib
import hashlib
import json
import time
import uuid
from pathlib import Path
from typing import Literal, Protocol, TypedDict

from langgraph.graph import END, START, StateGraph

from .adapters import LAB, TASK_ID, InfrastructureError, ProcessResult, run_process
from .tasks import get_task

MAX_ATTEMPTS = 3  # One implementation and at most two repairs.


class Worker(Protocol):
    name: str

    def implement(self, workspace: Path, attempt: int, feedback: str) -> str: ...


class Checker(Protocol):
    def check(self, workspace: Path, phase: str) -> ProcessResult: ...


class State(TypedDict):
    attempts: int
    status: str
    feedback: str
    trace: list[dict]


def protected_snapshot(workspace: Path, allowed_files: tuple[str, ...] = ("question.py",)) -> dict[str, str]:
    """Audit everything except the controller-owned fixed artifact allowlist."""
    result = {}
    for path in workspace.rglob("*"):
        relative = path.relative_to(workspace).as_posix()
        if relative in allowed_files:
            if path.is_symlink() or not path.is_file():
                raise InfrastructureError("Allowed artifacts must remain regular files")
            continue
        if path.is_symlink():
            raise InfrastructureError("Symlinks are outside the allowed change scope")
        if path.is_file():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    if any(not (workspace / name).is_file() for name in allowed_files):
        raise InfrastructureError("An allowed artifact was removed")
    return result


def build_graph(workspace: Path, worker: Worker, checker: Checker, *,
                allowed_files: tuple[str, ...] = ("question.py",)):
    protected = protected_snapshot(workspace, allowed_files)

    def event(state, node, **values):
        return state["trace"] + [{"node": node, **values}]

    def baseline(state):
        try:
            result = checker.check(workspace, "baseline")
        except (InfrastructureError, OSError) as exc:
            return {"status": "infrastructure_error", "feedback": str(exc),
                    "trace": event(state, "baseline", error=str(exc))}
        output = (result.stdout + result.stderr)[-8000:]
        return {"status": "working" if result.returncode == 0 else "baseline_failed",
                "feedback": output,
                "trace": event(state, "baseline", returncode=result.returncode, output=output)}

    def implement(state):
        attempt = state["attempts"] + 1
        try:
            note = worker.implement(workspace, attempt, state["feedback"])
        except (InfrastructureError, OSError) as exc:
            return {"attempts": attempt, "status": "infrastructure_error",
                    "feedback": str(exc), "trace": event(state, "implement", attempt=attempt,
                                                          error=str(exc))}
        return {"attempts": attempt, "trace": event(state, "implement", attempt=attempt, note=note)}

    def verify(state):
        try:
            if protected_snapshot(workspace, allowed_files) != protected:
                raise InfrastructureError("Worker changed files outside the allowed artifacts")
        except (InfrastructureError, OSError) as exc:
            return {"status": "scope_violation", "feedback": str(exc),
                    "trace": event(state, "verify", error=str(exc))}
        try:
            result = checker.check(workspace, "acceptance")
        except (InfrastructureError, OSError) as exc:
            return {"status": "infrastructure_error", "feedback": str(exc),
                    "trace": event(state, "verify", error=str(exc))}
        try:
            if protected_snapshot(workspace, allowed_files) != protected:
                raise InfrastructureError("Files outside the allowed artifacts changed during verification")
        except (InfrastructureError, OSError) as exc:
            return {"status": "scope_violation", "feedback": str(exc),
                    "trace": event(state, "verify", error=str(exc))}
        output = (result.stdout + result.stderr)[-8000:]
        if result.returncode == 0:
            status = "review_ready"
        elif state["attempts"] >= MAX_ATTEMPTS:
            status = "attempt_limit"
        else:
            status = "repair_needed"
        return {"status": status, "feedback": output,
                "trace": event(state, "verify", attempt=state["attempts"],
                               returncode=result.returncode, output=output)}

    def after_baseline(state) -> Literal["implement", "end"]:
        return "implement" if state["status"] == "working" else "end"

    def after_implement(state) -> Literal["verify", "end"]:
        return "end" if state["status"] == "infrastructure_error" else "verify"

    def after_verify(state) -> Literal["implement", "end"]:
        return "implement" if state["status"] == "repair_needed" else "end"

    graph = StateGraph(State)
    graph.add_node("baseline", baseline)
    graph.add_node("implement", implement)
    graph.add_node("verify", verify)
    graph.add_edge(START, "baseline")
    graph.add_conditional_edges("baseline", after_baseline, {"implement": "implement", "end": END})
    graph.add_conditional_edges("implement", after_implement, {"verify": "verify", "end": END})
    graph.add_conditional_edges("verify", after_verify, {"implement": "implement", "end": END})
    return graph.compile()


class JobConflict(ValueError):
    """The same ID already belongs to an incomplete or different run."""


def run_job(request_id: str, task_id: str, runs_dir: Path, worker: Worker, checker: Checker) -> dict:
    started = time.perf_counter()
    record_start = len(getattr(worker, "attempt_records", []))
    request_id = str(uuid.UUID(request_id))
    task = get_task(task_id)
    if any(getattr(adapter, "task_id", TASK_ID) != task_id for adapter in (worker, checker)):
        raise ValueError("Worker and checker must be configured for the requested fixed task")
    run_dir = runs_dir.resolve() / request_id
    identity = {"request_id": request_id, "task_id": task_id, "backend": worker.name}
    try:
        run_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        if (run_dir / "result.json").is_file():
            previous = json.loads((run_dir / "result.json").read_text(encoding="utf-8"))
            if all(previous.get(k) == v for k, v in identity.items()):
                return previous
        raise JobConflict("ID already used; inspect that run before submitting a new ID")
    (run_dir / "request.json").write_text(json.dumps(identity), encoding="utf-8")
    workspace = run_dir / "workspace"
    workspace.mkdir()
    originals = {
        name: ((LAB / "fixture" / task.fixture / name) if len(task.artifacts) > 1
               else (LAB / "fixture" / task.fixture)).read_text(encoding="utf-8")
        for name in task.artifacts
    }
    for name, source in originals.items():
        (workspace / name).write_bytes(source.encode("utf-8"))
    # A separate Git root makes the worker workspace independent of the RAG worktree.
    # No initial commit, staging or remote is needed.
    try:
        from .adapters import process_environment

        init = run_process(["git", "-c", "init.templateDir=", "init", "--quiet", str(workspace)],
                           workspace, timeout=10, env=process_environment())
        if init.returncode:
            raise InfrastructureError("Could not initialize worker Git workspace")
        result = build_graph(workspace, worker, checker, allowed_files=task.artifacts).invoke(
            {"attempts": 0, "status": "pending", "feedback": "", "trace": []},
            {"recursion_limit": 12},
        )
    except (InfrastructureError, OSError) as exc:
        result = {"attempts": 0, "status": "infrastructure_error", "feedback": str(exc), "trace": []}
    diffs = []
    for name, original in originals.items():
        candidate = workspace / name
        final = (candidate.read_text(encoding="utf-8", errors="replace")
                 if candidate.is_file() and not candidate.is_symlink() else "")
        diffs.extend(difflib.unified_diff(original.splitlines(True), final.splitlines(True),
                                         fromfile=f"before/{name}", tofile=f"after/{name}"))
    diff = "".join(diffs)
    report = {**identity, **result, "max_attempts": MAX_ATTEMPTS, "diff": diff,
              "workspace": str(workspace), "committed": False, "applied_to_rag": False,
              "isolation": getattr(worker, "isolation", "host"),
              "checker_isolation": getattr(checker, "isolation", "host"),
              "runner_image": getattr(checker, "image_id", None),
              "duration_s": round(time.perf_counter() - started, 6)}
    if len(task.artifacts) > 1:
        report["allowed_files"] = list(task.artifacts)
    if hasattr(worker, "attempt_records"):
        records = worker.attempt_records[record_start:]
        report.update(worker_image=getattr(worker, "image_id", None), worker_attempts=records,
                      authentication="chatgpt", model_cost=None,
                      model_usage_measured=bool(records) and all(r.get("usage") is not None for r in records))
    temporary = run_dir / "result.tmp"
    temporary.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(run_dir / "result.json")
    return report
