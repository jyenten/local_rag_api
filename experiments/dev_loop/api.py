"""Small local HTTP boundary for n8n. Requests select a fixed task, not commands."""

from __future__ import annotations

import secrets
import threading
from pathlib import Path
from typing import Annotated, Literal
from uuid import UUID

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, ConfigDict

from .adapters import TASK_ID
from .workflow import Checker, JobConflict, Worker, run_job


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: UUID
    task_id: Literal["normalize-question", "build-search-request"] = TASK_ID


def create_app(worker: Worker, checker: Checker, runs_dir: Path, token: str) -> FastAPI:
    if len(token) < 24:
        raise ValueError("DEV_LOOP_TOKEN must contain at least 24 characters")
    app = FastAPI(title="Local RAG development experiment", version="0.1.0")
    lock = threading.Lock()
    configured_task = getattr(worker, "task_id", TASK_ID)
    if getattr(checker, "task_id", TASK_ID) != configured_task:
        raise ValueError("Worker and checker must use the same fixed task")

    def authenticate(provided: str | None):
        if not secrets.compare_digest((provided or "").encode("utf-8"), token.encode("utf-8")):
            raise HTTPException(status_code=401, detail="Invalid development-loop token")

    @app.get("/health")
    def health():
        return {"status": "ok", "backend": worker.name,
                "task_id": configured_task,
                "isolation": getattr(worker, "isolation", "host"),
                "checker_isolation": getattr(checker, "isolation", "host")}

    @app.post("/runs")
    def start_run(
        body: RunRequest,
        x_dev_loop_token: Annotated[str | None, Header()] = None,
    ):
        authenticate(x_dev_loop_token)
        if body.task_id != configured_task:
            raise HTTPException(status_code=422, detail="Request task does not match this service's configured task")
        if not lock.acquire(blocking=False):
            raise HTTPException(status_code=409, detail="A run is already active; do not resubmit")
        try:
            return run_job(str(body.request_id), body.task_id, runs_dir, worker, checker)
        except JobConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        finally:
            lock.release()

    return app
