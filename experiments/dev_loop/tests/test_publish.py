"""Publication recovery and rejection paths, with no GitHub writes or model calls."""

import base64
import copy
import json
from pathlib import Path
from types import SimpleNamespace
import uuid

import pytest

from experiments.dev_loop import publish as module
from experiments.dev_loop.adapters import InfrastructureError, ProcessResult, process_environment, run_process
from experiments.dev_loop.real_bm25.__main__ import MANIFEST, TARGET, digest

ROOT = Path(__file__).resolve().parents[3]
BASE, TREE, HEAD = 'a' * 40, 'b' * 40, 'c' * 40
IMAGE = 'sha256:' + 'd' * 64


def reviewed_file(path):
    result = run_process(['git', 'show', f'{MANIFEST["source_commit"]}:{path}'], ROOT,
                         timeout=10, env=process_environment())
    assert result.returncode == 0
    return result.stdout


ORIGINAL = reviewed_file(TARGET)
CANDIDATE = ORIGINAL.replace('records: list[tuple[str, str, Metadata]]',
                            'records: list[tuple[str, str, Metadata, list[str]]]')
CANDIDATE = CANDIDATE.replace('if not isinstance(document, str) or not tokenize(document):',
    'if not isinstance(document, str):\n'
    '                    raise ValueError(f"Invalid document for chunk {chunk_id}")\n'
    '                tokens = tokenize(document)\n                if not tokens:')
CANDIDATE = CANDIDATE.replace('(chunk_id, document, dict(metadata))',
                            '(chunk_id, document, dict(metadata), tokens)')
CANDIDATE = CANDIDATE.replace('tokenize(document)\n            for document in self.documents',
                            'record[3]\n            for record in records')


def comparison():
    return {'document_count': 1000, 'paired_trials': 7, 'dataset_sha256': MANIFEST['dataset_sha256'],
            'queries': MANIFEST['queries'], 'init_ms': {'before': [20.] * 7, 'after': [15.] * 7},
            'median_init_ms': {'before': 20., 'after': 15.},
            'init_tokenize_calls': {'before': 2000, 'after': 1000}, 'single_pass_observed': True,
            'search_results_equal': True, 'tokenize_inputs_match_corpus': True,
            'search_results_sha256': {'before': 'e' * 64, 'after': 'e' * 64}}


@pytest.fixture
def run_dir(tmp_path):
    root = tmp_path / str(uuid.uuid4())
    (root / 'workspace').mkdir(parents=True)
    (root / 'before.py').write_bytes(ORIGINAL.encode())
    (root / 'workspace/question.py').write_bytes(CANDIDATE.encode())
    report = {'status': 'review_ready', 'task_id': 'bm25-tokenize-once',
              'request_id': root.name, 'backend': 'codex-real-bm25-docker',
              'measurement': 'live-codex-real-repository', 'source_repository': module.REPOSITORY,
              'reviewed_source_commit': MANIFEST['source_commit'], 'source_commit': BASE,
              'target': TARGET, 'source_sha256': digest(ORIGINAL),
              'candidate_sha256': digest(CANDIDATE), 'checker_isolation': 'docker',
              'runner_image': IMAGE, 'regression_test_count': 68, 'comparison': comparison(),
              'verification': [{'phase': 'acceptance', 'regression_returncode': 0}]}
    (root / 'result.json').write_text(json.dumps(report), encoding='utf-8')
    return root


class FakeGitHub:
    """Small stateful API stand-in to exercise partial writes and resumed runs."""
    def __init__(self):
        self.calls, self.refs, self.pulls = [], [], []
        self.tree_files = []
        self.sources = {p: reviewed_file(p) for p in (TARGET, *MANIFEST['files'])}
        self.base = BASE
        self.fail_pr = False
        self.move_main = False
        self.changed_diff = False
        self.repo_id = module.REPOSITORY_ID

    def api(self, method, path='', data=None):
        self.calls.append((method, path, copy.deepcopy(data)))
        if path == '': return {'id': self.repo_id}
        if path == 'git/ref/heads/main': return {'object': {'sha': self.base}}
        if path.startswith('contents/'):
            file, ref = path[len('contents/'):].split('?ref=')
            content = CANDIDATE if file == TARGET and ref == HEAD else self.sources[file]
            raw = content.encode()
            return {'type': 'file', 'encoding': 'base64', 'size': len(raw),
                    'content': base64.b64encode(raw).decode()}
        if path.startswith('git/matching-refs/'): return self.refs
        if path == 'pulls?state=open&base=main&per_page=100': return self.pulls
        if path.startswith('pulls?state=all&head='): return getattr(self, 'history', [])
        if path.endswith('/files?per_page=2'): return [{'filename': TARGET}]
        if path.startswith('git/commits/') and method == 'GET': return {'tree': {'sha': TREE}}
        if path.startswith('compare/'):
            return {'status': 'ahead', 'total_commits': 1,
                    'files': [{'filename': 'other.py' if self.changed_diff else TARGET, 'status': 'modified'}]}
        if path == 'git/trees':
            self.tree_files = data['tree']
            return {'sha': TREE}
        if path == 'git/commits':
            if self.move_main: self.base = 'f' * 40
            return {'sha': HEAD}
        if path == 'git/refs':
            assert not self.refs
            self.refs.append({'ref': data['ref'], 'object': {'sha': data['sha']}})
            return self.refs[0]
        if path == 'pulls':
            if self.fail_pr: raise module.PublicationError('Simulated lost PR request')
            pr = {'number': 12, 'state': 'open', 'draft': data['draft'],
                  'html_url': 'https://github.com/' + module.REPOSITORY + '/pull/12',
                  'base': {'ref': 'main'},
                  'head': {'sha': HEAD, 'ref': data['head'], 'repo': {'id': module.REPOSITORY_ID}}}
            self.pulls.append(pr)
            return pr
        if path.startswith('pulls/'): return self.pulls[0]
        raise AssertionError((method, path, data))


def checker(bundle):
    return [{'phase': 'baseline', 'regression_returncode': 0},
            {'phase': 'acceptance', 'regression_returncode': 0, 'comparison': comparison()}]


def writes(github):
    return [c for c in github.calls if c[0] != 'GET']


def test_preview_is_offline_and_does_not_publish(run_dir, monkeypatch, capsys):
    monkeypatch.setattr(module, 'GitHub', lambda *a: pytest.fail('Preview must not use GitHub'))
    monkeypatch.setattr(module, 'recheck', lambda *a: pytest.fail('Preview must not run Docker'))
    assert module.main(['--run-dir', str(run_dir)]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result['merge_allowed'] is False and result['publish_requested'] is False
    assert result['allowed_files'] == [TARGET]
    assert not (run_dir / 'publication.json').exists()


@pytest.mark.parametrize('change', [
    lambda d: d.update(status='attempt_limit'),
    lambda d: d.update(task_id='build-search-package'),
    lambda d: d.update(source_repository='someone/else'),
    lambda d: d.update(source_commit='--bad-ref'),
    lambda d: d.update(runner_image='local-rag-bm25-compare:1'),
    lambda d: d.update(candidate_sha256='0' * 64),
    lambda d: d['verification'][-1].update(regression_returncode=1),
    lambda d: d['comparison'].update(search_results_equal=False),
    lambda d: d.update(target='../.env'),
])
def test_bad_saved_evidence_cannot_reach_github(run_dir, change):
    path = run_dir / 'result.json'
    report = json.loads(path.read_text())
    change(report)
    path.write_text(json.dumps(report))
    github = FakeGitHub()
    with pytest.raises(InfrastructureError): module.publish(run_dir, github=github, checker=checker)
    assert github.calls == []


def test_artifact_tampering_scope_escape_and_symlinks_rejected(run_dir, tmp_path):
    file = run_dir / 'workspace/question.py'
    file.write_text(CANDIDATE + '\nprint("changed")\n')
    with pytest.raises(InfrastructureError): module.load_bundle(run_dir)
    report_path = run_dir / 'result.json'
    report = json.loads(report_path.read_text())
    report['candidate_sha256'] = digest(file.read_text())
    report_path.write_text(json.dumps(report))
    with pytest.raises(InfrastructureError, match='constructor'): module.load_bundle(run_dir)
    outside = tmp_path / 'elsewhere.py'
    outside.write_text(CANDIDATE)
    file.unlink()
    try: file.symlink_to(outside)
    except OSError: pytest.skip('Symlinks unavailable on this platform')
    with pytest.raises(InfrastructureError, match='regular'): module.load_bundle(run_dir)


def test_only_allowed_source_goes_to_one_draft_pr_and_local_files_stay_unchanged(run_dir):
    github = FakeGitHub()
    before = {p: p.read_bytes() for p in run_dir.rglob('*') if p.is_file()}
    result = module.publish(run_dir, github=github, checker=checker)
    assert result['draft'] is True and result['merged'] is False
    assert result['ci_status'] == 'not_checked' and result['local_source_changed'] is False
    assert github.tree_files == [{'path': TARGET, 'mode': '100644', 'type': 'blob', 'content': CANDIDATE}]
    assert [path for _, path, _ in writes(github)] == ['git/trees', 'git/commits', 'git/refs', 'pulls']
    assert all(p.read_bytes() == data for p, data in before.items())
    assert (run_dir / 'publication.json').is_file() and not (run_dir / 'publication.lock').exists()
    first_writes = len(writes(github))
    again = module.publish(run_dir, github=github, checker=checker)
    assert again['reused_existing_pr'] and again['pull_request'] == result['pull_request']
    assert len(writes(github)) == first_writes


def test_existing_legacy_bm25_pr_is_reused_without_any_write(run_dir):
    github = FakeGitHub()
    github.pulls.append({'number': 10, 'state': 'open', 'draft': True,
        'html_url': 'https://github.com/' + module.REPOSITORY + '/pull/10',
        'base': {'ref': 'main'}, 'head': {'sha': HEAD, 'ref': 'perf/bm25-tokenize-once',
                                      'repo': {'id': module.REPOSITORY_ID}}})
    result = module.publish(run_dir, github=github, checker=checker)
    assert result['pull_request'].endswith('/10') and result['reused_existing_pr']
    assert not writes(github)


def test_resume_after_branch_created_but_pr_request_failed(run_dir):
    github = FakeGitHub()
    github.fail_pr = True
    with pytest.raises(module.PublicationError, match='Simulated'):
        module.publish(run_dir, github=github, checker=checker)
    assert len(github.refs) == 1 and not (run_dir / 'publication.lock').exists()
    github.fail_pr = False
    result = module.publish(run_dir, github=github, checker=checker)
    assert result['pull_request'].endswith('/12')
    assert len([c for c in writes(github) if c[1] == 'git/refs']) == 1


@pytest.mark.parametrize('failure', ['identity', 'remote_source', 'docker', 'changed_run', 'scope', 'main_moved'])
def test_failed_preconditions_do_not_publish_a_branch(run_dir, failure):
    github = FakeGitHub()
    def check(bundle):
        if failure == 'docker': raise InfrastructureError('Docker unavailable')
        if failure == 'changed_run':
            (run_dir / 'workspace/question.py').write_text(CANDIDATE + '# changed\n')
        return checker(bundle)
    if failure == 'identity': github.repo_id = 9
    if failure == 'remote_source': github.sources[TARGET] += '# new upstream\n'
    if failure == 'scope': github.changed_diff = True
    if failure == 'main_moved': github.move_main = True
    with pytest.raises(InfrastructureError): module.publish(run_dir, github=github, checker=check)
    assert not github.refs and not github.pulls
    assert not (run_dir / 'publication.lock').exists()


def test_conflicting_existing_branch_is_never_overwritten(run_dir):
    github = FakeGitHub()
    branch = module.load_bundle(run_dir).branch
    github.refs = [{'ref': 'refs/heads/' + branch, 'object': {'sha': HEAD}}]
    github.changed_diff = True
    with pytest.raises(module.PublicationError, match='not be overwritten'):
        module.publish(run_dir, github=github, checker=checker)
    assert writes(github) == []


def test_parallel_publication_lock_is_not_removed_by_second_caller(run_dir):
    lock = run_dir / 'publication.lock'
    lock.write_text('another publisher')
    with pytest.raises(module.PublicationError, match='already active'):
        module.publish(run_dir, github=FakeGitHub(), checker=checker)
    assert lock.read_text() == 'another publisher'


def test_recheck_pins_image_and_checks_original_then_exact_candidate(run_dir, monkeypatch):
    observed = []
    class Checker:
        def __init__(self, original):
            assert original == ORIGINAL
            self.records = []
        def check(self, workspace, phase):
            observed.append((phase, (workspace / 'question.py').read_text()))
            self.records.append({'phase': phase, 'regression_returncode': 0})
            return ProcessResult(0, '', '')
    monkeypatch.setattr(module, 'BM25Checker', Checker)
    monkeypatch.setattr(module, 'DockerRunner', lambda image, **k: SimpleNamespace(image_id=image))
    records = module.recheck(module.load_bundle(run_dir))
    assert observed == [('baseline', ORIGINAL), ('acceptance', CANDIDATE)]
    assert len(records) == 2


def test_gh_credentials_only_reach_host_client_and_payload_uses_stdin(tmp_path, monkeypatch):
    monkeypatch.setenv('GH_TOKEN', 'test-host-only')
    monkeypatch.setenv('OPENAI_API_KEY', 'excluded')
    monkeypatch.setenv('DEV_LOOP_TOKEN', 'excluded')
    monkeypatch.setenv('GH_HOST', 'untrusted.invalid')
    monkeypatch.setattr(module.shutil, 'which', lambda name: '/trusted/gh')
    calls = []
    def process(command, cwd, **kwargs):
        calls.append((command, kwargs))
        return ProcessResult(0, '{"sha":"' + HEAD + '"}', '')
    monkeypatch.setattr(module, 'run_process', process)
    client = module.GitHub(tmp_path)
    source = 'literal $(shell) `code`\n'
    client.api('POST', 'git/trees', {'base_tree': TREE, 'tree': [
        {'path': TARGET, 'mode': '100644', 'type': 'blob', 'content': source}]})
    command, kwargs = calls[0]
    assert command[:6] == ['/trusted/gh', 'api', '--hostname', 'github.com', '--method', 'POST']
    assert source not in command and json.loads(kwargs['input_text'])['tree'][0]['content'] == source
    assert kwargs['env']['GH_TOKEN'] == 'test-host-only'
    assert all(k not in kwargs['env'] for k in ('OPENAI_API_KEY', 'DEV_LOOP_TOKEN', 'GH_HOST'))
    for method, path in [('PATCH', 'git/refs/heads/main'), ('PUT', 'pulls/10/merge'),
                         ('POST', 'actions/workflows/x/dispatches'), ('GET', 'https://untrusted.invalid')]:
        with pytest.raises(module.PublicationError): client.api(method, path)
    assert len(calls) == 1


def test_gh_errors_do_not_expose_stderr_or_tokens(tmp_path, monkeypatch):
    monkeypatch.setattr(module.shutil, 'which', lambda name: '/trusted/gh')
    monkeypatch.setattr(module, 'run_process', lambda *a, **k: ProcessResult(1, '', 'secret-token'))
    with pytest.raises(module.PublicationError) as error: module.GitHub(tmp_path).api('GET')
    assert 'secret-token' not in str(error.value)


def test_closed_pr_history_does_not_open_another_pr(run_dir):
    github = FakeGitHub()
    github.history = [{'state': 'closed', 'number': 12}]
    with pytest.raises(module.PublicationError, match='PR history'):
        module.publish(run_dir, github=github, checker=checker)
    assert writes(github) == []


@pytest.mark.parametrize('method,path,payload', [
    ('POST', 'git/refs', {'ref': 'refs/heads/main', 'sha': HEAD}),
    ('POST', 'pulls', {'base': 'main', 'head': 'some-branch', 'title': 'x', 'body': 'x', 'draft': False}),
    ('POST', 'git/trees', {'base_tree': TREE, 'tree': [
        {'path': '.github/workflows/x.yml', 'mode': '100644', 'type': 'blob', 'content': 'x'}]}),
    ('GET', 'contents/.env?ref=' + BASE, None),
])
def test_transport_rejects_scope_escape_even_before_process_start(tmp_path, monkeypatch, method, path, payload):
    monkeypatch.setattr(module.shutil, 'which', lambda name: '/trusted/gh')
    monkeypatch.setattr(module, 'run_process', lambda *a, **k: pytest.fail('Must not launch gh'))
    with pytest.raises(module.PublicationError): module.GitHub(tmp_path).api(method, path, payload)


@pytest.mark.parametrize('success', [True, False])
def test_real_cli_handoff_runs_only_after_success_without_losing_saved_result(tmp_path, monkeypatch, capsys, success):
    from experiments.dev_loop.real_bm25 import __main__ as real
    report = {'status': 'review_ready' if success else 'attempt_limit'}
    monkeypatch.setattr(real, 'run', lambda *a: (report, tmp_path))
    calls = []
    monkeypatch.setattr(module, 'publish', lambda path: calls.append(path) or {'pull_request': 'test-only'})
    assert real.main(['--publish']) == (0 if success else 1)
    assert calls == ([tmp_path] if success else [])
    assert 'Report:' in capsys.readouterr().out


def test_real_cli_publication_failure_keeps_run_and_explains_resume(tmp_path, monkeypatch, capsys):
    from experiments.dev_loop.real_bm25 import __main__ as real
    monkeypatch.setattr(real, 'run', lambda *a: ({'status': 'review_ready'}, tmp_path))
    def fail(path): raise module.PublicationError('GitHub unavailable')
    monkeypatch.setattr(module, 'publish', fail)
    with pytest.raises(SystemExit) as error: real.main(['--publish'])
    assert error.value.code == 1
    captured = capsys.readouterr()
    assert str(tmp_path) in captured.out and 'Run saved' in captured.err


def test_missing_gh_and_bad_json_have_clear_failures(tmp_path, monkeypatch):
    monkeypatch.setattr(module.shutil, 'which', lambda name: None)
    with pytest.raises(module.PublicationError, match='Install GitHub CLI'): module.GitHub(tmp_path)
    monkeypatch.setattr(module.shutil, 'which', lambda name: '/trusted/gh')
    monkeypatch.setattr(module, 'run_process', lambda *a, **k: ProcessResult(0, 'not json', ''))
    with pytest.raises(module.PublicationError, match='invalid JSON'): module.GitHub(tmp_path).api('GET')
