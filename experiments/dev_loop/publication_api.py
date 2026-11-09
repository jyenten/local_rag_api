"""Loopback-only n8n boundary for explicitly registered, verified BM25 runs."""

from __future__ import annotations

import argparse
import logging
import os
from pathlib import Path
import re
import secrets
import threading
from typing import Literal
from uuid import UUID

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .adapters import InfrastructureError
from .publish import BASE, REPOSITORY, TARGET, PublicationError, load_bundle, publish

TASK_ID = 'bm25-tokenize-once'
PORT = 8766
MAX_BODY_BYTES = 1024
LOGGER = logging.getLogger(__name__)


class PublicationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    task_id: Literal['bm25-tokenize-once']
    run_id: UUID


class JobRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    task_id: Literal['bm25-tokenize-once']
    request_id: UUID


def public_receipt(record, run_id):
    """Only review metadata leaves the host: no filesystem paths or raw evidence."""
    if (not isinstance(record, dict) or record.get('request_id') != run_id or record.get('task_id') != TASK_ID
            or record.get('repository') != REPOSITORY or record.get('base') != BASE
            or record.get('allowed_files') != [TARGET]
            or record.get('merged') is not False or record.get('merge_allowed') is not False
            or record.get('local_source_changed') is not False
            or record.get('published_to_github') is not True
            or not isinstance(record.get('pull_request'), str)
            or not re.fullmatch(r'https://github\.com/jyenten/local_rag_api/pull/[1-9][0-9]*', record['pull_request'])):
        raise PublicationError('Unexpected publisher receipt; inspect host publication state')
    keys = ('request_id', 'task_id', 'repository', 'base', 'base_sha', 'head_sha', 'branch',
            'allowed_files', 'candidate_sha256', 'pull_request', 'draft', 'reused_existing_pr',
            'published_to_github', 'local_source_changed', 'merged', 'merge_allowed',
            'ci_status', 'checker_image')
    return {key: record[key] for key in keys}


def create_app(runs_root: Path, token: str, allowed_runs, *, publisher=None, jobs=None) -> FastAPI:
    if not isinstance(token, str) or len(token) < 24:
        raise ValueError('DEV_LOOP_TOKEN must contain at least 24 characters')
    runs_root = Path(runs_root).absolute()
    registered = frozenset(str(UUID(str(value))) for value in allowed_runs)
    if not 1 <= len(registered) <= 20:
        raise ValueError('Register between 1 and 20 exact run UUIDs on the host')
    publisher = publisher or publish
    app = FastAPI(title='Local RAG verified publication', version='0.1.0', docs_url=None, redoc_url=None,
                  openapi_url=None)
    lock = threading.Lock()

    @app.middleware('http')
    async def boundary(request: Request, call_next):
        if request.url.path == '/health' and request.method == 'GET':
            return await call_next(request)
        provided = request.headers.get('X-Dev-Loop-Token', '')
        if not secrets.compare_digest(provided.encode('utf-8'), token.encode('utf-8')):
            return JSONResponse({'detail': 'Invalid development-loop token'}, status_code=401)
        # n8n server requests have no Origin. Browser cross-origin requests are not supported.
        if 'origin' in request.headers:
            return JSONResponse({'detail': 'Browser-origin requests are not supported'}, status_code=403)
        if request.method == 'POST':
            length = request.headers.get('content-length', '')
            if 'transfer-encoding' in request.headers or not re.fullmatch(r'[0-9]+', length):
                return JSONResponse({'detail': 'A fixed Content-Length is required'}, status_code=411)
            digits = length.lstrip('0') or '0'
            if len(digits) > 4 or int(digits) > MAX_BODY_BYTES:
                return JSONResponse({'detail': 'Publication request exceeds 1024 bytes'}, status_code=413)
            if request.headers.get('content-type', '').split(';')[0].strip() != 'application/json':
                return JSONResponse({'detail': 'Use application/json'}, status_code=415)
            if len(await request.body()) > MAX_BODY_BYTES:
                return JSONResponse({'detail': 'Publication request exceeds 1024 bytes'}, status_code=413)
        return await call_next(request)

    app.add_middleware(TrustedHostMiddleware,
                       allowed_hosts=['127.0.0.1', 'localhost', 'host.docker.internal'])

    @app.get('/health')
    def health():
        # Liveness only: no run listing, account identity, credentials or readiness claim.
        return {'status': 'ok', 'service': 'verified-publication', 'task_id': TASK_ID}

    @app.get('/tasks')
    def tasks():
        result = {'tasks': [{'task_id': TASK_ID, 'allowed_run_ids': sorted(registered),
                             'operations': ['preview', 'publish'], 'merge_allowed': False}]}
        if jobs is not None:
            result['real_job'] = jobs.capabilities()
        return result

    if jobs is not None:
        from .real_jobs import NewJobLimit
        from .workflow import JobConflict

        @app.post('/jobs')
        def start_job(body: JobRequest):
            if not lock.acquire(blocking=False):
                raise HTTPException(409, 'A task or publication is active; inspect its status')
            try:
                return jobs.execute(str(body.request_id))
            except NewJobLimit as exc:
                raise HTTPException(429, 'New-job allowance consumed; host action is required') from exc
            except JobConflict as exc:
                raise HTTPException(409, 'Job conflicts with saved or active state; inspect on the host') from exc
            except (InfrastructureError, OSError, ValueError, KeyError, TypeError) as exc:
                LOGGER.warning('Real task stopped (%s)', type(exc).__name__)
                raise HTTPException(503, 'Real task stopped; inspect saved job state on the host') from exc
            finally:
                lock.release()

        @app.get('/jobs/{request_id}')
        def job_status(request_id: UUID):
            try:
                return jobs.status(str(request_id))
            except FileNotFoundError as exc:
                raise HTTPException(404, 'Unknown real-task job') from exc
            except (InfrastructureError, OSError, ValueError, KeyError, TypeError) as exc:
                raise HTTPException(409, 'Job state requires host inspection') from exc

    def run_directory(body):
        run_id = str(body.run_id)
        if run_id not in registered:
            raise HTTPException(404, 'Run is not registered on this service')
        # The HTTP caller supplies neither a root directory nor any artifact path.
        return runs_root / run_id

    @app.post('/publications/preview')
    def preview(body: PublicationRequest):
        directory = run_directory(body)
        try:
            return load_bundle(directory).plan()
        except FileNotFoundError as exc:
            raise HTTPException(404, 'Registered run files are unavailable') from exc
        except (InfrastructureError, OSError, ValueError) as exc:
            LOGGER.warning('Publication preview rejected (%s)', type(exc).__name__)
            raise HTTPException(422, 'Run failed validation; inspect it with the host CLI') from exc

    @app.post('/publications')
    def start_publication(body: PublicationRequest):
        directory = run_directory(body)
        if not lock.acquire(blocking=False):
            raise HTTPException(409, 'A publication is active; do not resubmit')
        try:
            return public_receipt(publisher(directory), str(body.run_id))
        except FileNotFoundError as exc:
            raise HTTPException(404, 'Registered run files are unavailable') from exc
        except PublicationError as exc:
            LOGGER.warning('Publication rejected (%s)', type(exc).__name__)
            raise HTTPException(422, 'Publication stopped; inspect the host CLI and remote PR state') from exc
        except InfrastructureError as exc:
            LOGGER.warning('Publication infrastructure unavailable (%s)', type(exc).__name__)
            raise HTTPException(503, 'Docker or GitHub infrastructure unavailable; inspect the host CLI') from exc
        except (OSError, ValueError, KeyError, TypeError) as exc:
            LOGGER.warning('Publication failed (%s)', type(exc).__name__)
            raise HTTPException(500, 'Publication failed; inspect host and remote state before retrying') from exc
        finally:
            lock.release()

    from .control_api import install_control_routes

    install_control_routes(app, runs_root, registered, publisher, jobs, lock)
    return app


def main(argv=None):
    parser = argparse.ArgumentParser(description='Loopback-only n8n publication of registered verified runs')
    parser.add_argument('--runs-root', type=Path, required=True,
                        help='Host-owned parent of real-BM25 UUID directories')
    parser.add_argument('--allow-run', type=UUID, action='append', required=True,
                        help='Exact verified run UUID; repeat for at most 20 registered runs')
    parser.add_argument('--port', type=int, default=PORT)
    parser.add_argument('--source-repo', type=Path,
                        help='Explicitly enable real BM25 jobs from this reviewed original worktree')
    parser.add_argument('--jobs-root', type=Path, help='Separate host-owned real-job state and artifacts')
    parser.add_argument('--max-new-jobs', type=int, default=1,
                        help='New real jobs allowed per service session (1-20, default 1)')
    args = parser.parse_args(argv)
    if not 1024 <= args.port <= 65535:
        parser.error('--port must be between 1024 and 65535')
    if args.source_repo is None and (args.jobs_root is not None or args.max_new_jobs != 1):
        parser.error('--jobs-root/--max-new-jobs require --source-repo')
    try:
        jobs = None
        if args.source_repo is not None:
            from .real_jobs import RealJobs

            jobs = RealJobs(args.source_repo, args.jobs_root or args.runs_root.parent / 'n8n-real-jobs',
                            args.max_new_jobs)
        app = create_app(args.runs_root, os.environ.get('DEV_LOOP_TOKEN', ''), args.allow_run, jobs=jobs)
        for run_id in args.allow_run:
            load_bundle(args.runs_root / str(run_id))
    except (InfrastructureError, ValueError, OSError) as exc:
        parser.error(str(exc))
    import uvicorn

    # No non-loopback override, proxy-supplied client address or extra worker process.
    uvicorn.run(app, host='127.0.0.1', port=args.port, proxy_headers=False, workers=1,
                limit_concurrency=8, timeout_keep_alive=5)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
