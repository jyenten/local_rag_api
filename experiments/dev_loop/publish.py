"""Publish a host-registered verified result through create-only scoped Git operations."""

from __future__ import annotations

import argparse
import base64
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import uuid

from .adapters import InfrastructureError, process_environment, run_process
from .docker_adapters import DockerRunner
from .real_bm25.__main__ import (
    BM25Checker, MANIFEST, TARGET, digest, validate_candidate, validate_comparison,
)
from .registered_tasks import BM25, get_registered_task

REPOSITORY = 'jyenten/local_rag_api'
REPOSITORY_ID = 1236923375
BASE = 'main'
SHA = re.compile(r'[0-9a-f]{40}')
IMAGE = re.compile(r'sha256:[0-9a-f]{64}')
MAX_FILE = 65536


class PublicationError(InfrastructureError):
    """Stop publication without changing local source or updating existing refs."""


def commit_sha(value):
    if not isinstance(value, str) or not SHA.fullmatch(value):
        raise PublicationError('Invalid Git commit SHA')
    return value


def read_file(root, relative, limit=MAX_FILE):
    path = root / relative
    if (root.is_symlink() or any(p.is_symlink() for p in (path, *path.parents) if p != root.parent)
            or not path.is_file() or not path.resolve().is_relative_to(root.resolve())):
        raise PublicationError('Run artifacts must be regular files without symlinks')
    if path.stat().st_size > limit:
        raise PublicationError('Run artifact exceeds the size limit')
    return path.read_text(encoding='utf-8')


@dataclass(frozen=True)
class Bundle:
    directory: Path
    request_id: str
    original: str
    candidate: str
    report: dict

    @property
    def task(self):
        return get_registered_task(self.report.get('task_id', BM25))

    @property
    def candidate_files(self):
        return {self.task.target: self.candidate, **self.task.fixed_files}

    @property
    def branch(self):
        return 'agent/' + self.task.task_id + '-' + self.request_id

    def plan(self):
        return {'repository': REPOSITORY, 'base': BASE, 'branch': self.branch,
                'task_id': self.task.task_id, 'request_id': self.request_id,
                'allowed_files': self.task.allowed_files, 'candidate_sha256': digest(self.candidate),
                'draft': True, 'publish_requested': False, 'merge_allowed': False,
                'docker_recheck_required': True,
                **({'fixed_files_sha256': {name: digest(source) for name, source in self.task.fixed_files.items()}}
                   if self.task.fixed_files else {})}


def load_bundle(directory):
    directory = Path(directory).absolute()
    try:
        report = json.loads(read_file(directory, 'result.json', 1024 * 1024))
        if not isinstance(report, dict):
            raise ValueError('Expected a result object')
        task = get_registered_task(report.get('task_id'))
        manifest = task.manifest
        request_id = str(uuid.UUID(report['request_id']))
        expected = {'status': 'review_ready', 'task_id': task.task_id,
                    'backend': task.backend, 'measurement': 'live-codex-real-repository',
                    'source_repository': REPOSITORY, 'reviewed_source_commit': manifest['source_commit'],
                    'target': task.target, 'checker_isolation': 'docker',
                    'source_sha256': manifest['source_sha256'], 'regression_test_count': manifest['regression_test_count']}
        if directory.name != request_id or any(report.get(k) != v for k, v in expected.items()):
            raise ValueError('Wrong run identity or status')
        commit_sha(report['source_commit'])
        if not IMAGE.fullmatch(report['runner_image']):
            raise ValueError('Missing immutable checker image')
        original = read_file(directory, 'before.py')
        candidate = read_file(directory, 'workspace/question.py')
        if digest(original) != manifest['source_sha256'] or digest(candidate) != report['candidate_sha256']:
            raise ValueError('Artifact hash mismatch')
        validator = validate_candidate if task.task_id == BM25 else task.module.validate_candidate
        if candidate == original or validator(candidate, original) != candidate:
            raise ValueError('Invalid or unchanged candidate')
        comparison_validator = validate_comparison if task.task_id == BM25 else task.module.validate_comparison
        comparison_validator(report['comparison'])
        if task.task_id == BM25 and not (report['comparison']['single_pass_observed'] and report['comparison']['search_results_equal']):
            raise ValueError('Acceptance comparison did not pass')
        if task.fixed_files and report.get('fixed_files_sha256') != {
                name: digest(source) for name, source in task.fixed_files.items()}:
            raise ValueError('Fixed regressions differ from the reviewed task')
        last = report['verification'][-1]
        if (last['phase'] != 'acceptance' or type(last['regression_returncode']) is not int
                or last['regression_returncode'] != 0):
            raise ValueError('No successful final verification')
        return Bundle(directory, request_id, original, candidate, report)
    except (KeyError, ValueError, TypeError, IndexError, UnicodeError) as exc:
        raise PublicationError('Not a complete, unchanged, successful registered run') from exc


class GitHub:
    """Fixed github.com repository. No update-ref, merge, workflow or shell operation."""

    def __init__(self, cwd, *, task_id=BM25):
        self.cwd = cwd
        self.task = get_registered_task(task_id)
        self.task_id = task_id
        self.executable = shutil.which('gh')
        if not self.executable:
            raise PublicationError('Install GitHub CLI (gh) and run gh auth login --hostname github.com')

    def api(self, method, path='', data=None):
        task = self.task
        source_paths = (task.target, *task.manifest['files'], *task.fixed_files)
        branch_pattern = re.escape('agent/' + task.task_id + '-') + r'[0-9a-f-]{36}'
        source_endpoint = any(re.fullmatch(re.escape('contents/' + name) + r'\?ref=[0-9a-f]{40}', path)
                              for name in source_paths)
        allowed_get = (path == '' or path == 'git/ref/heads/main'
                       or re.fullmatch(r'git/commits/[0-9a-f]{40}', path)
                       or source_endpoint
                       or re.fullmatch(r'compare/[0-9a-f]{40}\.\.\.[0-9a-f]{40}', path)
                       or re.fullmatch('git/matching-refs/heads/' + branch_pattern, path)
                       or (bool(task.fixed_files) and re.fullmatch(r'git/trees/[0-9a-f]{40}\?recursive=1', path))
                       or path == 'pulls?state=open&base=main&per_page=100'
                       or re.fullmatch(r'pulls\?state=all&head=jyenten:' + branch_pattern + '&per_page=100', path)
                       or re.fullmatch(r'pulls/[0-9]+(?:/files\?per_page=' + str(len(task.allowed_files) + 1) + ')?', path))
        if not ((method == 'GET' and allowed_get) or
                (method == 'POST' and path in {'git/trees', 'git/commits', 'git/refs', 'pulls'})):
            raise PublicationError('GitHub operation is outside publication scope')
        endpoint = 'repos/' + REPOSITORY + ('/' + path if path else '')
        command = [self.executable, 'api', '--hostname', 'github.com', '--method', method,
                   '-H', 'Accept: application/vnd.github+json', endpoint]
        payload = None
        if method == 'POST':
            if not isinstance(data, dict):
                raise PublicationError('Publication writes require a structured payload')
            # Constrain even the transport to create-only scoped operations.
            valid = {
                'git/trees': lambda: (set(data) == {'base_tree', 'tree'}
                                     and SHA.fullmatch(data['base_tree'])
                                     and len(data['tree']) == len(task.allowed_files)
                                     and {entry.get('path') for entry in data['tree']} == set(task.allowed_files)
                                     and all(entry.get('mode') == '100644' and entry.get('type') == 'blob'
                                             and set(entry) == {'path', 'mode', 'type', 'content'}
                                             and isinstance(entry['content'], str)
                                             and (entry['path'] == task.target or
                                                  entry['content'] == task.fixed_files[entry['path']])
                                             for entry in data['tree'])),
                'git/commits': lambda: (set(data) == {'message', 'tree', 'parents'}
                                       and len(data['parents']) == 1
                                       and SHA.fullmatch(data['parents'][0])
                                       and SHA.fullmatch(data['tree'])),
                'git/refs': lambda: (set(data) == {'ref', 'sha'}
                                    and re.fullmatch('refs/heads/' + branch_pattern, data['ref'])
                                    and SHA.fullmatch(data['sha'])),
                'pulls': lambda: (set(data) == {'base', 'head', 'title', 'body', 'draft'}
                                 and data['base'] == BASE and data['draft'] is True
                                 and re.fullmatch(branch_pattern, data['head'])),
            }
            try:
                if not valid[path]():
                    raise ValueError()
            except (KeyError, TypeError, ValueError, IndexError) as exc:
                raise PublicationError('Publication write exceeds the allowed scope') from exc
            command += ['--input', '-']
            payload = json.dumps(data, ensure_ascii=False)
        # Only this host-side process gets GitHub auth, never the worker or checker.
        env = process_environment()
        for key in ('GH_CONFIG_DIR', 'GH_TOKEN', 'GITHUB_TOKEN'):
            if key in os.environ:
                env[key] = os.environ[key]
        env['GH_PROMPT_DISABLED'] = '1'
        result = run_process(command, self.cwd, timeout=45, input_text=payload, env=env)
        if result.returncode:
            # Do not copy gh stderr, HTTP bodies or credentials into reports.
            raise PublicationError('GitHub request failed; check gh auth status and retry the same run')
        try:
            return json.loads(result.stdout)
        except ValueError as exc:
            raise PublicationError('GitHub returned invalid JSON') from exc


def remote_source(github, path, revision):
    data = github.api('GET', 'contents/' + path + '?ref=' + commit_sha(revision))
    try:
        if data['type'] != 'file' or data['encoding'] != 'base64' or data['size'] > MAX_FILE:
            raise ValueError()
        raw = base64.b64decode(data['content'].replace('\n', ''), validate=True)
        if len(raw) > MAX_FILE:
            raise ValueError()
        return raw.decode('utf-8').replace('\r\n', '\n')
    except (KeyError, TypeError, ValueError, UnicodeError) as exc:
        raise PublicationError('Invalid repository source response') from exc


def check_revision(github, revision, original):
    task = get_registered_task(getattr(github, 'task_id', BM25))
    expected = {task.target: task.manifest['source_sha256'],
                **{p: f['sha256'] for p, f in task.manifest['files'].items()}}
    for path, expected_hash in expected.items():
        source = remote_source(github, path, revision)
        if digest(source) != expected_hash or (path == task.target and source != original):
            raise PublicationError('Remote source or original tests changed; review the task baseline again')
    if task.fixed_files:
        tree_sha = commit_sha(github.api('GET', 'git/commits/' + commit_sha(revision))['tree']['sha'])
        tree = github.api('GET', 'git/trees/' + tree_sha + '?recursive=1')
        if (tree.get('truncated') is not False or not isinstance(tree.get('tree'), list)
                or any(entry.get('path') in task.fixed_files for entry in tree['tree'])):
            raise PublicationError('Cannot establish the reviewed fixed-regression destination is absent')


def recheck(bundle):
    """Re-execute candidate only in the original immutable offline checker image."""
    checker = (BM25Checker(bundle.original) if bundle.task.task_id == BM25 else
               bundle.task.module.CitationChecker(bundle.original))
    checker.runner = DockerRunner(bundle.report['runner_image'], timeout=45)
    with tempfile.TemporaryDirectory(prefix='publish-check-') as temporary:
        workspace = Path(temporary)
        artifact = workspace / 'question.py'
        for phase, code in [('baseline', bundle.original), ('acceptance', bundle.candidate)]:
            artifact.write_bytes(code.encode('utf-8'))
            result = checker.check(workspace, phase)
            if result.returncode or artifact.read_bytes() != code.encode('utf-8'):
                raise PublicationError('Independent Docker recheck failed; nothing published')
    if checker.runner.image_id != bundle.report['runner_image']:
        raise PublicationError('Checker image changed')
    return checker.records


def scoped_diff(github, base, head, candidate):
    task = get_registered_task(getattr(github, 'task_id', BM25))
    comparison = github.api('GET', 'compare/' + commit_sha(base) + '...' + commit_sha(head))
    files = comparison.get('files', [])
    expected = {task.target: ('modified', candidate),
                **{name: ('added', source) for name, source in task.fixed_files.items()}}
    return (comparison.get('status') == 'ahead' and comparison.get('total_commits') == 1
            and len(files) == len(expected) and {f.get('filename') for f in files} == set(expected)
            and all(f.get('status') == expected[f['filename']][0]
                    and remote_source(github, f['filename'], head) == expected[f['filename']][1]
                    for f in files))


def existing_pr(github, bundle, base):
    pulls = github.api('GET', 'pulls?state=open&base=main&per_page=100')
    if not isinstance(pulls, list) or len(pulls) >= 100:
        raise PublicationError('Cannot establish a complete bounded list of open PRs')
    for pr in pulls:
        if pr.get('head', {}).get('repo', {}).get('id') != REPOSITORY_ID:
            continue
        limit = len(bundle.task.allowed_files) + 1
        files = github.api('GET', 'pulls/' + str(int(pr['number'])) + '/files?per_page=' + str(limit))
        if any(f.get('filename') in bundle.task.allowed_files for f in files):
            head = commit_sha(pr['head']['sha'])
            if scoped_diff(github, base, head, bundle.candidate):
                return pr
            raise PublicationError('Another open PR changes the task files; review it before publishing a competing result')
    return None


def receipt(bundle, pr, base, verification, reused):
    number = pr.get('number')
    if (type(number) is not int or number <= 0 or pr.get('state') != 'open'
            or pr.get('base', {}).get('ref') != BASE
            or pr.get('head', {}).get('repo', {}).get('id') != REPOSITORY_ID
            or pr.get('html_url') != f'https://github.com/{REPOSITORY}/pull/{number}'):
        raise PublicationError('Unexpected PR response; inspect remote state before retrying')
    record = {**bundle.plan(), 'publish_requested': True, 'base_sha': base,
              'head_sha': commit_sha(pr['head']['sha']), 'branch': pr['head']['ref'],
              'pull_request': pr['html_url'], 'draft': pr['draft'], 'reused_existing_pr': reused,
              'verification': verification, 'checker_image': bundle.report['runner_image'],
              'published_to_github': True, 'local_source_changed': False, 'merged': False,
              'ci_status': 'not_checked'}
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=bundle.directory,
                                     prefix='publication-', suffix='.tmp', delete=False) as handle:
        temporary = Path(handle.name)
        try:
            handle.write(json.dumps(record, indent=2))
        except BaseException:
            handle.close()
            temporary.unlink()
            raise
    try:
        temporary.replace(bundle.directory / 'publication.json')
    finally:
        temporary.unlink(missing_ok=True)
    return record


def publish(directory, *, github=None, checker=None, expected_task=None):
    bundle = load_bundle(directory)
    if expected_task is not None and bundle.task.task_id != expected_task:
        raise PublicationError('Run belongs to another registered task; nothing published')
    lock = bundle.directory / 'publication.lock'
    try:
        handle = lock.open('x', encoding='utf-8')
    except FileExistsError as exc:
        raise PublicationError('Publication already active; inspect publication.lock before retrying') from exc
    try:
        with handle:
            handle.write(bundle.request_id)
        github = github or (GitHub(bundle.directory) if bundle.task.task_id == BM25 else
                            GitHub(bundle.directory, task_id=bundle.task.task_id))
        if getattr(github, 'task_id', BM25) != bundle.task.task_id:
            raise PublicationError('Publisher task transport does not match the verified run')
        if github.api('GET').get('id') != REPOSITORY_ID:
            raise PublicationError('Repository identity mismatch')
        base = commit_sha(github.api('GET', 'git/ref/heads/main')['object']['sha'])
        check_revision(github, base, bundle.original)
        source_revision = bundle.report['source_commit']
        if source_revision != base:
            check_revision(github, source_revision, bundle.original)
        # Saved JSON is not a trust decision: require fresh independent offline evidence.
        verification = (checker or recheck)(bundle)
        if load_bundle(bundle.directory) != bundle:
            raise PublicationError('Run artifacts changed during publication')
        pr = existing_pr(github, bundle, base)
        if pr:
            return receipt(bundle, pr, base, verification, True)
        history = github.api('GET', 'pulls?state=all&head=jyenten:' + bundle.branch + '&per_page=100')
        if not isinstance(history, list) or history:
            raise PublicationError('This run already has PR history; inspect it before publishing again')
        refs = github.api('GET', 'git/matching-refs/heads/' + bundle.branch)
        exact = [ref for ref in refs if ref.get('ref') == 'refs/heads/' + bundle.branch]
        if exact:
            head = commit_sha(exact[0]['object']['sha'])
            if not scoped_diff(github, base, head, bundle.candidate):
                raise PublicationError('Existing publication branch differs; it will not be overwritten')
        else:
            base_tree = commit_sha(github.api('GET', 'git/commits/' + base)['tree']['sha'])
            tree = github.api('POST', 'git/trees', {
                'base_tree': base_tree,
                'tree': [{'path': name, 'mode': '100644', 'type': 'blob', 'content': source}
                         for name, source in bundle.candidate_files.items()],
            })
            commit = github.api('POST', 'git/commits', {
                'message': bundle.task.commit_message,
                'tree': commit_sha(tree['sha']), 'parents': [base],
            })
            head = commit_sha(commit['sha'])
            if not scoped_diff(github, base, head, bundle.candidate):
                raise PublicationError('Created commit exceeds the allowed diff; no branch published')
            if github.api('GET', 'git/ref/heads/main')['object']['sha'] != base:
                raise PublicationError('main moved during publication; retry against its current baseline')
            # Create-only: collisions fail. No update-ref, force push, or local Git hooks.
            github.api('POST', 'git/refs', {'ref': 'refs/heads/' + bundle.branch, 'sha': head})
        # A lost POST response can be recovered by rerunning the same UUID; refs are never reset.
        body = (bundle.task.pr_body + '\n\n' +
                f'Run: `{bundle.request_id}`; candidate SHA-256: `{digest(bundle.candidate)}`; '
                f'checker: `{bundle.report["runner_image"]}`.\n\n'
                'Review the diff, CI and security findings before merging. Dependency findings are not '
                'waived by this result. No automatic merge is enabled.')
        created = github.api('POST', 'pulls', {'base': BASE, 'head': bundle.branch,
                                             'title': bundle.task.pr_title,
                                             'body': body, 'draft': True})
        pr = github.api('GET', 'pulls/' + str(int(created['number'])))
        if (pr.get('draft') is not True or pr.get('head', {}).get('sha') != head
                or pr.get('head', {}).get('ref') != bundle.branch
                or not scoped_diff(github, base, head, bundle.candidate)):
            raise PublicationError('Unexpected published PR; inspect it before retrying')
        return receipt(bundle, pr, base, verification, False)
    finally:
        lock.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description='Preview or publish one registered verified run as a draft PR')
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--publish', action='store_true', help='Recheck in Docker and publish through host gh login')
    args = parser.parse_args(argv)
    try:
        result = publish(args.run_dir) if args.publish else load_bundle(args.run_dir).plan()
    except (InfrastructureError, OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, str(exc) + '\n')
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
