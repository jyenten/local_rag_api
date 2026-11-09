"""Reviewed n8n actions over the existing fixed task; no remote task registration."""

from __future__ import annotations

import difflib
import hashlib
import json
import logging
import secrets
from typing import Literal
from uuid import UUID

from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictBool

from .adapters import InfrastructureError
from .publish import REPOSITORY, load_bundle
from .real_bm25.__main__ import digest, read_source
from .real_jobs import NewJobLimit
from .workflow import JobConflict
from .registered_tasks import BM25, REAL_TASK_IDS, get_registered_task

TASK_ID = 'bm25-tokenize-once'
LOGGER = logging.getLogger(__name__)


class ControlRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    action: Literal['catalog', 'generate', 'status', 'report', 'publish']
    task_id: Literal['bm25-tokenize-once', 'retrieval-citation-provenance'] = TASK_ID
    request_id: UUID | None = None


class ApprovedRequest(ControlRequest):
    action: Literal['generate', 'publish']
    request_id: UUID
    approved: StrictBool
    plan_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')


def plan_hash(plan):
    return hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


class ControlPanel:
    def __init__(self, runs_root, registered, publisher, jobs):
        self.runs_root, self.registered = runs_root, registered
        self.publisher, self.jobs = publisher, jobs

    def envelope(self, body, status, **values):
        return {'status': status, 'action': body.action, 'task_id': body.task_id,
                'request_id': str(body.request_id) if body.request_id else None,
                'requires_approval': False, 'merge_allowed': False, **values}

    def blocked(self, body, code):
        return self.envelope(body, 'blocked', error_code=code)

    def directory(self, request_id, task_id=TASK_ID):
        if request_id in self.registered:
            directory = self.runs_root / request_id
            if load_bundle(directory).task.task_id != task_id:
                raise FileNotFoundError('Run belongs to another registered task')
            return directory, False
        if self.jobs is None:
            raise FileNotFoundError('Unknown registered run or job')
        state = self.jobs.status(request_id)  # Validate durable identity before reading any artifact.
        if state['task_id'] != task_id:
            raise FileNotFoundError('Job belongs to another registered task')
        return self.jobs.paths(request_id)[2], True

    def report(self, request_id, task_id=TASK_ID):
        directory, _ = self.directory(request_id, task_id)
        bundle = load_bundle(directory)
        task = bundle.task
        data = bundle.report
        comparison = data['comparison']
        # Derive diff from validated public artifacts, never trust raw report HTML/logs.
        patch = ''.join(difflib.unified_diff(
            bundle.original.splitlines(True), bundle.candidate.splitlines(True),
            fromfile='before/' + task.target, tofile='after/' + task.target))
        for name, source in task.fixed_files.items():
            patch += ''.join(difflib.unified_diff([], source.splitlines(True), fromfile='/dev/null', tofile='after/' + name))
        return {'request_id': request_id, 'task_id': task_id, 'repository': REPOSITORY,
                'status': 'review_ready', 'allowed_files': task.allowed_files,
                'source_commit': data['source_commit'], 'source_sha256': digest(bundle.original),
                'candidate_sha256': digest(bundle.candidate), 'checker_isolation': 'docker',
                'checker_image': data['runner_image'], 'regression_test_count': task.manifest['regression_test_count'],
                'comparison': task.public_comparison(comparison),
                **({'fixed_files_sha256': data['fixed_files_sha256']} if task.fixed_files else {}),
                'diff': patch, 'committed': False, 'applied_to_rag': False,
                'ci_status': 'not_checked', 'merge_allowed': False}

    def preview(self, body):
        if body.action == 'catalog':
            registered = {run_id: load_bundle(self.runs_root / run_id).task.task_id for run_id in self.registered}
            tasks = []
            for task_id in REAL_TASK_IDS:
                task = get_registered_task(task_id)
                tasks.append({'task_id': task_id, 'description': task.description,
                    'allowed_files': task.allowed_files,
                    'allowed_run_ids': sorted(key for key, value in registered.items() if value == task_id),
                    'generation_configured': self.jobs is not None and self.jobs.task_id == task_id,
                    'generation_readiness': 'requires_source_and_github_preflight',
                    'max_attempts': 3, 'merge_allowed': False})
            return self.envelope(body, 'catalog', tasks=tasks,
                real_job=self.jobs.capabilities() if self.jobs else None)
        if body.request_id is None:
            raise HTTPException(422, 'Choose an exact run/job UUID')
        request_id = str(body.request_id)
        if body.action == 'status':
            if request_id in self.registered:
                data = self.report(request_id, body.task_id)
                return self.envelope(body, 'view', result={key: data[key] for key in (
                    'request_id', 'task_id', 'status', 'candidate_sha256', 'checker_isolation',
                    'ci_status', 'merge_allowed')})
            if self.jobs is None or self.jobs.task_id != body.task_id:
                raise FileNotFoundError('Unknown job')
            return self.envelope(body, 'view', result=self.jobs.status(request_id))
        if body.action == 'report':
            return self.envelope(body, 'view', result=self.report(request_id, body.task_id))

        task = get_registered_task(body.task_id)
        plan = {'action': body.action, 'task_id': body.task_id, 'request_id': request_id,
                'repository': REPOSITORY, 'allowed_files': task.allowed_files,
                'max_attempts': 3, 'checker_isolation': 'docker', 'merge_allowed': False}
        if task.fixed_files:
            plan.update(worker_allowed_files=[task.target], editable_methods=task.manifest['allowed_methods'],
                        fixed_files_sha256={name: digest(source) for name, source in task.fixed_files.items()},
                        acceptance_test_count=task.manifest['regression_test_count'])
        if body.action == 'generate':
            if request_id in self.registered:
                return self.blocked(body, 'SAVED_RUN_CANNOT_BE_REGENERATED')
            if self.jobs is None or self.jobs.task_id != body.task_id:
                return self.blocked(body, 'NEW_JOBS_NOT_CONFIGURED')
            if self.jobs.lock.locked():
                return self.blocked(body, 'TASK_ACTIVE')
            _, state_dir, run_dir = self.jobs.paths(request_id)
            if state_dir.exists():
                state = self.jobs.status(request_id)
                if state['status'] in {'pr_ready', 'generation_failed', 'generation_error', 'review_ready'}:
                    return self.envelope(body, 'view', result=state)
                if not (run_dir / 'result.json').is_file():
                    return self.blocked(body, 'JOB_ACTIVE_OR_INTERRUPTED')
                self.jobs.cached_report(run_dir / 'result.json', request_id)
            else:
                if self.jobs.used >= self.jobs.max_new_jobs:
                    return self.blocked(body, 'NEW_JOB_ALLOWANCE_CONSUMED')
                try:
                    current, revision = (read_source(self.jobs.source_repo) if body.task_id == BM25 else
                                         self.jobs.read_source())
                except (InfrastructureError, OSError, ValueError) as exc:
                    LOGGER.warning('Control source check stopped: %s', exc)
                    return self.blocked(body, 'SOURCE_CHANGED')
                if current != self.jobs.original or revision != self.jobs.revision:
                    return self.blocked(body, 'SOURCE_CHANGED')
                try:
                    self.jobs.preflight()
                except (InfrastructureError, OSError, ValueError, KeyError, TypeError) as exc:
                    LOGGER.warning('Control preflight stopped: %s', exc)
                    return self.blocked(body, 'SOURCE_OR_REMOTE_PREFLIGHT_BLOCKED')
            plan.update(source_commit=self.jobs.revision, source_sha256=digest(self.jobs.original),
                        new_jobs_remaining=self.jobs.max_new_jobs - self.jobs.used,
                        cached_generation=state_dir.exists(), publication='separate_approval_required')
        else:
            directory, managed = self.directory(request_id, body.task_id)
            bundle = load_bundle(directory)
            if managed:
                state = self.jobs.status(request_id)
                if state['status'] == 'pr_ready':
                    return self.envelope(body, 'view', result=state)
            plan.update(bundle.plan(), action='publish', source_commit=bundle.report['source_commit'],
                        source_sha256=digest(bundle.original), model_invocations=0)
        return self.envelope(body, 'approval_required', requires_approval=True,
                             plan=plan, plan_sha256=plan_hash(plan),
                             result=self.report(request_id, body.task_id) if body.action == 'publish' else None)

    def execute(self, body):
        if body.approved is not True:
            raise HTTPException(403, 'Explicit approval of this plan is required')
        request = ControlRequest(action=body.action, task_id=body.task_id, request_id=body.request_id)
        preview = self.preview(request)  # Revalidate current source, budget and candidate under the API lock.
        if (not preview['requires_approval']
                or not secrets.compare_digest(preview['plan_sha256'], body.plan_sha256)):
            raise HTTPException(409, 'Plan changed or action blocked; preview and review it again')
        request_id = str(body.request_id)
        if body.action == 'generate':
            result = self.jobs.generate(request_id)
        else:
            directory, managed = self.directory(request_id, body.task_id)
            if managed:
                result = self.jobs.publish_existing(request_id)
            else:
                from .publication_api import public_receipt

                result = public_receipt(self.publisher(directory), request_id, body.task_id)
        return self.envelope(body, 'completed', result=result)


def install_control_routes(app, runs_root, registered, publisher, jobs, lock):
    """Reuse the existing token/body/host boundary and single mutation lock."""
    panel = ControlPanel(runs_root, registered, publisher, jobs)

    def call(operation):
        try:
            return operation()
        except FileNotFoundError as exc:
            raise HTTPException(404, 'Unknown run/job or unavailable report') from exc
        except NewJobLimit as exc:
            raise HTTPException(429, 'New-job allowance consumed') from exc
        except JobConflict as exc:
            raise HTTPException(409, 'Job requires inspection; no automatic regeneration') from exc
        except (InfrastructureError, OSError, ValueError, KeyError, TypeError) as exc:
            LOGGER.warning('Control action stopped: %s', exc)
            raise HTTPException(503, 'Action stopped; inspect controller logs on the host') from exc

    @app.post('/control/preview')
    def preview(body: ControlRequest):
        return call(lambda: panel.preview(body))

    @app.post('/control/execute')
    def execute(body: ApprovedRequest):
        if not lock.acquire(blocking=False):
            raise HTTPException(409, 'An action is active; use status instead of resubmitting')
        try:
            return call(lambda: panel.execute(body))
        finally:
            lock.release()
