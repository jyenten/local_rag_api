"""Durable, bounded real-task execution; retries cannot silently regenerate code."""

from __future__ import annotations

import json
import logging
from pathlib import Path
import tempfile
import threading
from uuid import UUID

from .adapters import InfrastructureError
from .publish import REPOSITORY, REPOSITORY_ID, GitHub, check_revision, commit_sha, publish
from .real_bm25.__main__ import MANIFEST, digest, read_source, run
from .workflow import JobConflict

TASK_ID = 'bm25-tokenize-once'
MAX_STATE_BYTES = 1024 * 1024
LOGGER = logging.getLogger(__name__)


class NewJobLimit(JobConflict):
    """The host's per-service-session allowance has been consumed."""


def read_json(path):
    if (path.is_symlink() or any(p.is_symlink() for p in path.parents)
            or not path.is_file() or path.stat().st_size > MAX_STATE_BYTES):
        raise InfrastructureError('Job state is missing, oversized or not a regular file')
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError()
        return data
    except (ValueError, UnicodeError) as exc:
        raise InfrastructureError('Invalid saved job state; inspect on the host') from exc


def write_json(path, data):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=path.parent,
                                     prefix='job-', suffix='.tmp', delete=False) as handle:
        temporary = Path(handle.name)
        try:
            json.dump(data, handle, indent=2)
        except BaseException:
            handle.close()
            temporary.unlink()
            raise
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


class RealJobs:
    def __init__(self, source_repo, jobs_root, max_new_jobs=1, *, generator=None, publisher=None,
                 preflight=None):
        if type(max_new_jobs) is not int or not 1 <= max_new_jobs <= 20:
            raise ValueError('Allow between 1 and 20 new jobs per service session')
        self.source_repo = Path(source_repo).absolute()
        self.root = Path(jobs_root).absolute()
        if any(p.is_symlink() for p in (self.root, *self.root.parents)):
            raise ValueError('Job root must not use symlinks')
        self.original, self.revision = read_source(self.source_repo)
        self.max_new_jobs, self.used = max_new_jobs, 0
        self.generator, self.publisher = generator or run, publisher or publish
        self.preflight = preflight or self.github_preflight
        self.lock = threading.Lock()

    def github_preflight(self):
        github = GitHub(self.source_repo)
        if github.api('GET').get('id') != REPOSITORY_ID:
            raise InfrastructureError('Unexpected GitHub repository identity')
        base = commit_sha(github.api('GET', 'git/ref/heads/main')['object']['sha'])
        check_revision(github, base, self.original)
        if self.revision != base:
            check_revision(github, self.revision, self.original)

    def capabilities(self):
        return {'task_id': TASK_ID, 'operations': ['run-and-publish'],
                'source_commit': self.revision, 'allowed_files': [MANIFEST['target']],
                'max_attempts': 3, 'max_new_jobs_this_session': self.max_new_jobs,
                'new_jobs_remaining': self.max_new_jobs - self.used, 'merge_allowed': False}

    def paths(self, request_id):
        request_id = str(UUID(str(request_id)))
        directory, run_dir = self.root / 'requests' / request_id, self.root / 'runs' / request_id
        if any(path.is_symlink() for path in
               (self.root, directory.parent, run_dir.parent, directory, run_dir, *self.root.parents)):
            raise InfrastructureError('Job directories must not use symlinks')
        return request_id, directory, run_dir

    def identity(self, request_id):
        return {'request_id': request_id, 'task_id': TASK_ID, 'repository': REPOSITORY,
                'source_commit': self.revision, 'source_sha256': digest(self.original)}

    def status(self, request_id):
        request_id, directory, _ = self.paths(request_id)
        if not directory.exists():
            raise FileNotFoundError('Unknown real-task job')
        if read_json(directory / 'request.json') != self.identity(request_id):
            raise JobConflict('Job ID belongs to a different source revision')
        return self.safe_state(read_json(directory / 'state.json'), request_id)

    @staticmethod
    def safe_state(state, request_id):
        if state.get('publication') is not None:
            from .publication_api import public_receipt

            state = {**state, 'publication': public_receipt(state['publication'], request_id)}
        if state.get('status') == 'pr_ready' and state.get('publication') is None:
            raise JobConflict('Completed job is missing a publication receipt')
        allowed = ('status', 'generation_status', 'attempts', 'generation_cached', 'publication',
                   'publication_status', 'error_code', 'model_usage_measured', 'worker_invocations')
        return {'request_id': request_id, 'task_id': TASK_ID, 'merge_allowed': False,
                'merged': False, 'local_source_changed': False,
                **{key: state[key] for key in allowed if key in state}}

    def cached_report(self, path, request_id):
        report = read_json(path)
        expected = {'request_id': request_id, 'task_id': TASK_ID,
                    'source_repository': REPOSITORY, 'source_commit': self.revision,
                    'source_sha256': digest(self.original), 'backend': 'codex-real-bm25-docker',
                    'measurement': 'live-codex-real-repository',
                    'reviewed_source_commit': MANIFEST['source_commit'], 'target': MANIFEST['target'],
                    'checker_isolation': 'docker', 'committed': False, 'applied_to_rag': False}
        if any(report.get(key) != value for key, value in expected.items()):
            raise JobConflict('Saved generation belongs to a different task or source')
        return report

    def execute(self, request_id):
        if not self.lock.acquire(blocking=False):
            raise JobConflict('A real task is active; inspect its status instead of resubmitting')
        try:
            return self._execute(request_id)
        finally:
            self.lock.release()

    def _execute(self, request_id):
        request_id, directory, run_dir = self.paths(request_id)
        cached = directory.exists()
        if cached:
            # A crash before result.json is not permission to call the model again.
            state = self.status(request_id)
            if state['status'] in {'pr_ready', 'generation_failed', 'generation_error'}:
                return {**state, 'generation_cached': True}
            if not (run_dir / 'result.json').is_file():
                raise JobConflict('Job is active or interrupted without a final result; inspect on the host')
        else:
            if self.used >= self.max_new_jobs:
                raise NewJobLimit('No new jobs remain in this service session')
            current, revision = read_source(self.source_repo)
            if current != self.original or revision != self.revision:
                raise JobConflict('Source changed since registration; restart only after reviewing it')
            # Refuse an already merged/changed baseline before spending a model invocation.
            self.preflight()
            directory.parent.mkdir(parents=True, exist_ok=True)
            try:
                directory.mkdir()
            except FileExistsError as exc:
                raise JobConflict('Another controller claimed this job; inspect its status') from exc
            self.used += 1
            write_json(directory / 'request.json', self.identity(request_id))
            write_json(directory / 'state.json', {'status': 'generating', 'publication_status': 'not_attempted'})
            try:
                report, generated = self.generator(self.source_repo, self.root / 'runs', request_id=request_id)
                if generated.absolute() != run_dir or report.get('request_id') != request_id:
                    raise InfrastructureError('Generator returned an unexpected run directory')
            except (InfrastructureError, OSError, ValueError, KeyError, TypeError) as exc:
                LOGGER.warning('Real generation stopped: %s', exc)
                state = {'status': 'generation_error', 'generation_status': 'unknown',
                         'publication_status': 'not_attempted', 'error_code': 'GENERATION_STOPPED'}
                write_json(directory / 'state.json', state)
                return self.safe_state(state, request_id)
        report = self.cached_report(run_dir / 'result.json', request_id)
        state = {'status': 'publishing', 'generation_status': report['status'],
                 'attempts': report['attempts'], 'generation_cached': cached,
                 'publication_status': 'pending',
                 'model_usage_measured': report.get('model_usage_measured', False),
                 'worker_invocations': len(report.get('worker_attempts', []))}
        if report['status'] != 'review_ready':
            state.update(status='generation_failed', publication_status='not_attempted')
            write_json(directory / 'state.json', state)
            return self.safe_state(state, request_id)
        write_json(directory / 'state.json', state)
        try:
            from .publication_api import public_receipt

            state['publication'] = public_receipt(self.publisher(run_dir), request_id)
            state.update(status='pr_ready', publication_status='published')
        except (InfrastructureError, OSError, ValueError, KeyError, TypeError) as exc:
            LOGGER.warning('Real publication stopped: %s', exc)
            # Generation stays durable: a retry can repeat publication, never the model call.
            state.update(status='publication_blocked', publication_status='blocked',
                         error_code='PUBLICATION_STOPPED_INSPECT_HOST')
        write_json(directory / 'state.json', state)
        return self.safe_state(state, request_id)
