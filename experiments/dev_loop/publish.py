"""Publish the fixed real-BM25 result to a branch and draft PR, using host gh auth."""

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
    def branch(self):
        return 'agent/bm25-tokenize-once-' + self.request_id

    def plan(self):
        return {'repository': REPOSITORY, 'base': BASE, 'branch': self.branch,
                'task_id': 'bm25-tokenize-once', 'request_id': self.request_id,
                'allowed_files': [TARGET], 'candidate_sha256': digest(self.candidate),
                'draft': True, 'publish_requested': False, 'merge_allowed': False,
                'docker_recheck_required': True}


def load_bundle(directory):
    directory = Path(directory).absolute()
    try:
        report = json.loads(read_file(directory, 'result.json', 1024 * 1024))
        if not isinstance(report, dict):
            raise ValueError('Expected a result object')
        request_id = str(uuid.UUID(report['request_id']))
        expected = {'status': 'review_ready', 'task_id': 'bm25-tokenize-once',
                    'backend': 'codex-real-bm25-docker', 'measurement': 'live-codex-real-repository',
                    'source_repository': REPOSITORY, 'reviewed_source_commit': MANIFEST['source_commit'],
                    'target': TARGET, 'checker_isolation': 'docker',
                    'source_sha256': MANIFEST['source_sha256'], 'regression_test_count': 68}
        if directory.name != request_id or any(report.get(k) != v for k, v in expected.items()):
            raise ValueError('Wrong run identity or status')
        commit_sha(report['source_commit'])
        if not IMAGE.fullmatch(report['runner_image']):
            raise ValueError('Missing immutable checker image')
        original = read_file(directory, 'before.py')
        candidate = read_file(directory, 'workspace/question.py')
        if digest(original) != MANIFEST['source_sha256'] or digest(candidate) != report['candidate_sha256']:
            raise ValueError('Artifact hash mismatch')
        if candidate == original or validate_candidate(candidate, original) != candidate:
            raise ValueError('Invalid or unchanged candidate')
        validate_comparison(report['comparison'])
        if not (report['comparison']['single_pass_observed'] and report['comparison']['search_results_equal']):
            raise ValueError('Acceptance comparison did not pass')
        last = report['verification'][-1]
        if (last['phase'] != 'acceptance' or type(last['regression_returncode']) is not int
                or last['regression_returncode'] != 0):
            raise ValueError('No successful final verification')
        return Bundle(directory, request_id, original, candidate, report)
    except (KeyError, ValueError, TypeError, IndexError, UnicodeError) as exc:
        raise PublicationError('Not a complete, unchanged, successful real-BM25 run') from exc


class GitHub:
    """Fixed github.com repository. No update-ref, merge, workflow or shell operation."""

    def __init__(self, cwd):
        self.cwd = cwd
        self.executable = shutil.which('gh')
        if not self.executable:
            raise PublicationError('Install GitHub CLI (gh) and run gh auth login --hostname github.com')

    def api(self, method, path='', data=None):
        source_paths = (TARGET, *MANIFEST['files'])
        source_endpoint = any(re.fullmatch(re.escape('contents/' + name) + r'\?ref=[0-9a-f]{40}', path)
                              for name in source_paths)
        allowed_get = (path == '' or path == 'git/ref/heads/main'
                       or re.fullmatch(r'git/commits/[0-9a-f]{40}', path)
                       or source_endpoint
                       or re.fullmatch(r'compare/[0-9a-f]{40}\.\.\.[0-9a-f]{40}', path)
                       or re.fullmatch(r'git/matching-refs/heads/agent/bm25-tokenize-once-[0-9a-f-]{36}', path)
                       or path == 'pulls?state=open&base=main&per_page=100'
                       or re.fullmatch(r'pulls\?state=all&head=jyenten:agent/bm25-tokenize-once-[0-9a-f-]{36}&per_page=100', path)
                       or re.fullmatch(r'pulls/[0-9]+(?:/files\?per_page=2)?', path))
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
                                     and len(data['tree']) == 1
                                     and data['tree'][0].get('path') == TARGET
                                     and data['tree'][0].get('mode') == '100644'
                                     and data['tree'][0].get('type') == 'blob'
                                     and set(data['tree'][0]) == {'path', 'mode', 'type', 'content'}
                                     and isinstance(data['tree'][0]['content'], str)),
                'git/commits': lambda: (set(data) == {'message', 'tree', 'parents'}
                                       and len(data['parents']) == 1
                                       and SHA.fullmatch(data['parents'][0])
                                       and SHA.fullmatch(data['tree'])),
                'git/refs': lambda: (set(data) == {'ref', 'sha'}
                                    and re.fullmatch(r'refs/heads/agent/bm25-tokenize-once-[0-9a-f-]{36}', data['ref'])
                                    and SHA.fullmatch(data['sha'])),
                'pulls': lambda: (set(data) == {'base', 'head', 'title', 'body', 'draft'}
                                 and data['base'] == BASE and data['draft'] is True
                                 and re.fullmatch(r'agent/bm25-tokenize-once-[0-9a-f-]{36}', data['head'])),
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
    expected = {TARGET: MANIFEST['source_sha256'],
                **{p: f['sha256'] for p, f in MANIFEST['files'].items()}}
    for path, expected_hash in expected.items():
        source = remote_source(github, path, revision)
        if digest(source) != expected_hash or (path == TARGET and source != original):
            raise PublicationError('Remote source or original tests changed; review the task baseline again')


def recheck(bundle):
    """Re-execute candidate only in the original immutable offline checker image."""
    checker = BM25Checker(bundle.original)
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


def one_file_diff(github, base, head, candidate):
    comparison = github.api('GET', 'compare/' + commit_sha(base) + '...' + commit_sha(head))
    files = comparison.get('files', [])
    return (comparison.get('status') == 'ahead' and comparison.get('total_commits') == 1
            and len(files) == 1 and files[0].get('filename') == TARGET
            and files[0].get('status') == 'modified'
            and remote_source(github, TARGET, head) == candidate)


def existing_pr(github, bundle, base):
    pulls = github.api('GET', 'pulls?state=open&base=main&per_page=100')
    if not isinstance(pulls, list) or len(pulls) >= 100:
        raise PublicationError('Cannot establish a complete bounded list of open PRs')
    for pr in pulls:
        if pr.get('head', {}).get('repo', {}).get('id') != REPOSITORY_ID:
            continue
        files = github.api('GET', 'pulls/' + str(int(pr['number'])) + '/files?per_page=2')
        if len(files) == 1 and files[0].get('filename') == TARGET:
            head = commit_sha(pr['head']['sha'])
            if one_file_diff(github, base, head, bundle.candidate):
                return pr
            raise PublicationError('Another open PR changes BM25; review it before publishing a competing result')
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


def publish(directory, *, github=None, checker=None):
    bundle = load_bundle(directory)
    lock = bundle.directory / 'publication.lock'
    try:
        handle = lock.open('x', encoding='utf-8')
    except FileExistsError as exc:
        raise PublicationError('Publication already active; inspect publication.lock before retrying') from exc
    try:
        with handle:
            handle.write(bundle.request_id)
        github = github or GitHub(bundle.directory)
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
            if not one_file_diff(github, base, head, bundle.candidate):
                raise PublicationError('Existing publication branch differs; it will not be overwritten')
        else:
            base_tree = commit_sha(github.api('GET', 'git/commits/' + base)['tree']['sha'])
            tree = github.api('POST', 'git/trees', {
                'base_tree': base_tree,
                'tree': [{'path': TARGET, 'mode': '100644', 'type': 'blob', 'content': bundle.candidate}],
            })
            commit = github.api('POST', 'git/commits', {
                'message': 'perf(bm25): tokenize each document once during initialization',
                'tree': commit_sha(tree['sha']), 'parents': [base],
            })
            head = commit_sha(commit['sha'])
            if not one_file_diff(github, base, head, bundle.candidate):
                raise PublicationError('Created commit exceeds the allowed diff; no branch published')
            if github.api('GET', 'git/ref/heads/main')['object']['sha'] != base:
                raise PublicationError('main moved during publication; retry against its current baseline')
            # Create-only: collisions fail. No update-ref, force push, or local Git hooks.
            github.api('POST', 'git/refs', {'ref': 'refs/heads/' + bundle.branch, 'sha': head})
        # A lost POST response can be recovered by rerunning the same UUID; refs are never reset.
        body = ('BM25 currently tokenizes each document twice during construction. Reuse the validated '
                'tokens in the same sorted record. Only the constructor body changes.\n\n'
                'Publication reran the same 68 regressions before and after in the pinned offline Docker '
                'checker and required identical results for six synthetic-corpus queries and tokenizer '
                'calls 2000 → 1000. This does not establish real-corpus or end-to-end latency improvement.\n\n'
                f'Run: `{bundle.request_id}`; candidate SHA-256: `{digest(bundle.candidate)}`; '
                f'checker: `{bundle.report["runner_image"]}`.\n\n'
                'Review the diff, CI and security findings before merging. Dependency findings are not '
                'waived by this result. No automatic merge is enabled.')
        created = github.api('POST', 'pulls', {'base': BASE, 'head': bundle.branch,
                                             'title': 'perf(bm25): reuse validated document tokens',
                                             'body': body, 'draft': True})
        pr = github.api('GET', 'pulls/' + str(int(created['number'])))
        if (pr.get('draft') is not True or pr.get('head', {}).get('sha') != head
                or pr.get('head', {}).get('ref') != bundle.branch
                or not one_file_diff(github, base, head, bundle.candidate)):
            raise PublicationError('Unexpected published PR; inspect it before retrying')
        return receipt(bundle, pr, base, verification, False)
    finally:
        lock.unlink()


def main(argv=None):
    parser = argparse.ArgumentParser(description='Preview or publish one verified real-BM25 run as a draft PR')
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
