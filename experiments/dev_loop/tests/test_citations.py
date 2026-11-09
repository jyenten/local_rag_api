"""Fixed task scope and real regression semantics; reference fixtures are not model output."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

import pytest

from experiments.dev_loop.adapters import InfrastructureError, ProcessResult, process_environment, run_process
from experiments.dev_loop.citations import task
from experiments.dev_loop.citations import probe
from experiments.dev_loop import publish
from experiments.dev_loop.registered_tasks import BM25, CITATIONS, get_registered_task
from experiments.dev_loop.tests.test_publish import FakeGitHub, BASE, TREE, HEAD, IMAGE

ROOT = Path(__file__).resolve().parents[3]
result = run_process(['git', 'show', task.MANIFEST['source_commit'] + ':' + task.TARGET], ROOT,
                     timeout=15, env=process_environment())
assert result.returncode == 0, 'Reviewed citation source must be available in Git history'
ORIGINAL = result.stdout


def reference_change(original):
    """Trusted test-only reference, never applied to the application or given to the worker."""
    code = original.replace('minimum_score = best_score * 0.5',
        'minimum_score = best_score * 0.5 if best_score >= 0 else best_score')
    start = code.index('        if not context:', code.index('    def build_context('))
    end = code.index('        return context, selected_lines, documents, distances, metadatas', start)
    code = code[:start] + ('        if not context:\n'
        '            selected_lines = candidate_lines[:self.settings.max_context_lines]\n'
        '            context = "\\n".join(line.text for line in selected_lines)\n') + code[end:]
    return code.rstrip() + '\n'


CANDIDATE = reference_change(ORIGINAL)


@pytest.fixture
def citation_run(tmp_path):
    directory = tmp_path / str(uuid.uuid4())
    (directory / 'workspace').mkdir(parents=True)
    (directory / 'before.py').write_text(ORIGINAL, encoding='utf-8')
    (directory / 'workspace/question.py').write_text(CANDIDATE, encoding='utf-8')
    report = {'status': 'review_ready', 'task_id': CITATIONS, 'request_id': directory.name,
        'backend': 'codex-real-citations-docker', 'measurement': 'live-codex-real-repository',
        'source_repository': publish.REPOSITORY, 'source_commit': BASE,
        'reviewed_source_commit': task.MANIFEST['source_commit'], 'target': task.TARGET,
        'source_sha256': task.digest(ORIGINAL), 'candidate_sha256': task.digest(CANDIDATE),
        'fixed_files_sha256': {name: task.digest(source) for name, source in task.fixed_files().items()},
        'checker_isolation': 'docker', 'runner_image': IMAGE, 'regression_test_count': 15,
        'verification': [{'phase': 'acceptance', 'regression_returncode': 0}],
        'comparison': {'before': {key: False for key in task.PROBE_KEYS},
                       'after': {key: True for key in task.PROBE_KEYS}},
        'attempts': 1, 'worker_attempts': [{'attempt': 1}], 'model_usage_measured': True,
        'committed': False, 'applied_to_rag': False}
    (directory / 'result.json').write_text(json.dumps(report), encoding='utf-8')
    return directory


def test_registration_and_baseline_are_immutable_and_test_destination_is_protected(tmp_path, monkeypatch):
    assert task.digest(ORIGINAL) == task.MANIFEST['source_sha256']
    assert task.validate_candidate(CANDIDATE, ORIGINAL) == CANDIDATE
    spec = get_registered_task(CITATIONS)
    assert spec.allowed_files == [task.TARGET, task.MANIFEST['fixed_test_target']]
    assert get_registered_task(BM25).fixed_files == {}
    with pytest.raises(InfrastructureError): get_registered_task('arbitrary-task')
    source = tmp_path / task.TARGET
    source.parent.mkdir(parents=True)
    source.write_text(ORIGINAL, encoding='utf-8')
    monkeypatch.setattr(task, 'run_process', lambda *a, **kw: ProcessResult(0, BASE, ''))
    assert task.read_source(tmp_path) == (ORIGINAL, BASE)
    destination = tmp_path / task.MANIFEST['fixed_test_target']
    destination.parent.mkdir(parents=True)
    destination.write_text('existing local work')
    with pytest.raises(InfrastructureError, match='already exists'): task.read_source(tmp_path)
    assert destination.read_text() == 'existing local work'


@pytest.mark.parametrize('changed', [
    lambda s: s.replace('import re', 'import os\nimport re'),
    lambda s: s.replace('n_results=self.settings.retrieval_results', 'n_results=100'),
    lambda s: s.replace('def build_context(', 'def another_method('),
    lambda s: s.replace('minimum_score =', 'open("/tmp/test")\n        minimum_score =', 1),
    lambda s: s.replace('minimum_score =', '__import__("os")\n        minimum_score =', 1),
    lambda s: s.replace('minimum_score =', '__builtins__["open"]("/tmp/forged")\n        minimum_score =', 1),
])
def test_worker_cannot_change_imports_search_or_escape_two_method_scope(changed):
    with pytest.raises(InfrastructureError): task.validate_candidate(changed(CANDIDATE), ORIGINAL)


def test_complete_module_regressions_fail_before_and_pass_after_without_optional_dependencies(tmp_path):
    workspace = tmp_path / 'trusted reference'
    workspace.mkdir()
    source = workspace / 'question.py'
    env = {**os.environ, 'DEV_LOOP_WORKSPACE': str(workspace), 'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1'}
    command = [sys.executable, '-m', 'pytest', str(task.HERE / 'checks/test_retrieval_citations.py'),
               '-q', '-p', 'no:cacheprovider', '-o', 'addopts=']
    source.write_text(ORIGINAL, encoding='utf-8')
    baseline = subprocess.run(command + ['-k', 'test_existing_'], env=env, capture_output=True, text=True, timeout=15)
    broken = subprocess.run(command, env=env, capture_output=True, text=True, timeout=15)
    before = probe.observe(source)
    source.write_text(CANDIDATE, encoding='utf-8')
    fixed = subprocess.run(command, env=env, capture_output=True, text=True, timeout=15)
    assert baseline.returncode == 0 and '3 passed' in baseline.stdout
    assert broken.returncode == 1 and 'test_forced_fallback_retains_second_source' in broken.stdout
    assert fixed.returncode == 0 and '15 passed' in fixed.stdout, fixed.stdout + fixed.stderr
    assert before == {key: False for key in task.PROBE_KEYS}
    assert probe.observe(source) == {key: True for key in task.PROBE_KEYS}


def test_bundle_rejects_tampered_fixed_tests_or_unproven_comparison(citation_run):
    bundle = publish.load_bundle(citation_run)
    assert set(bundle.candidate_files) == set(get_registered_task(CITATIONS).allowed_files)
    path = citation_run / 'result.json'
    original = path.read_text()
    for field, value in [('fixed_files_sha256', {}), ('comparison', {'before': {}, 'after': {}}),
                         ('task_id', BM25), ('candidate_sha256', 'f' * 64)]:
        report = json.loads(original)
        report[field] = value
        path.write_text(json.dumps(report))
        with pytest.raises(InfrastructureError): publish.load_bundle(citation_run)
    path.write_text(original)


def test_legacy_bm25_publication_cannot_publish_a_citation_run(citation_run):
    with pytest.raises(publish.PublicationError, match='another registered task'):
        publish.publish(citation_run, expected_task=BM25)
    assert not (citation_run / 'publication.lock').exists()


class CitationGitHub(FakeGitHub):
    task_id = CITATIONS

    def __init__(self):
        super().__init__()
        self.sources = {task.TARGET: ORIGINAL, **task.fixed_files()}
        self.extra = False
        self.truncated = False

    def api(self, method, path='', data=None):
        if method == 'GET' and path.startswith('git/trees/'):
            self.calls.append((method, path, data))
            return {'truncated': self.truncated, 'tree': [{'path': task.TARGET, 'type': 'blob'}]}
        if method == 'GET' and path.startswith('contents/'):
            file, ref = path[len('contents/'):].split('?ref=')
            import base64
            source = CANDIDATE if file == task.TARGET and ref == HEAD else self.sources[file]
            return {'type': 'file', 'encoding': 'base64', 'size': len(source.encode()),
                    'content': base64.b64encode(source.encode()).decode()}
        if method == 'GET' and path.startswith('compare/'):
            return {'status': 'ahead', 'total_commits': 1, 'files': [
                {'filename': task.TARGET, 'status': 'modified'},
                {'filename': task.MANIFEST['fixed_test_target'], 'status': 'added'},
                *([{'filename': '.env', 'status': 'added'}] if self.extra else [])]}
        if method == 'GET' and '/files?' in path:
            return [{'filename': name} for name in get_registered_task(CITATIONS).allowed_files]
        return super().api(method, path, data)


def test_publication_includes_exact_fixed_tests_and_never_updates_refs_or_merges(citation_run):
    github = CitationGitHub()
    record = publish.publish(citation_run, github=github, checker=lambda bundle: [{'offline': 'reference'}])
    assert record['task_id'] == CITATIONS and record['draft'] is True and record['merged'] is False
    assert record['fixed_files_sha256'] == publish.load_bundle(citation_run).report['fixed_files_sha256']
    assert {entry['path'] for entry in github.tree_files} == set(get_registered_task(CITATIONS).allowed_files)
    test = next(entry for entry in github.tree_files if entry['path'] != task.TARGET)
    assert test['content'] == next(iter(task.fixed_files().values()))
    assert all(method in ('GET', 'POST') and '/merge' not in path for method, path, _ in github.calls)
    assert (citation_run / 'before.py').read_text() == ORIGINAL


def test_extra_diff_or_incomplete_tree_stops_before_publishing_ref(citation_run):
    for flag in ('extra', 'truncated'):
        github = CitationGitHub()
        setattr(github, flag, True)
        with pytest.raises(publish.PublicationError):
            publish.publish(citation_run, github=github, checker=lambda bundle: [])
        assert github.refs == []


def test_citation_transport_accepts_only_registered_files_and_exact_host_tests(tmp_path, monkeypatch):
    monkeypatch.setattr(publish.shutil, 'which', lambda value: 'gh')
    calls = []
    monkeypatch.setattr(publish, 'run_process', lambda *a, **kw: calls.append((a, kw)) or ProcessResult(0, '{}', ''))
    github = publish.GitHub(tmp_path, task_id=CITATIONS)
    payload = {'base_tree': TREE, 'tree': [{'path': name, 'mode': '100644', 'type': 'blob', 'content': source}
               for name, source in {task.TARGET: CANDIDATE, **task.fixed_files()}.items()]}
    github.api('POST', 'git/trees', payload)
    assert len(calls) == 1
    for name, source in [('.env', 'secret'), (task.MANIFEST['fixed_test_target'], 'weakened tests')]:
        bad = copy.deepcopy(payload)
        bad['tree'][1].update(path=name, content=source)
        with pytest.raises(publish.PublicationError): github.api('POST', 'git/trees', bad)
    with pytest.raises(publish.PublicationError):
        github.api('POST', 'git/refs', {'ref': 'refs/heads/agent/bm25-tokenize-once-' + citation_uuid(), 'sha': HEAD})
    assert len(calls) == 1


def citation_uuid():
    return '00000000-0000-4000-8000-000000000071'


@pytest.mark.skipif(os.environ.get('DEV_LOOP_CITATION_DOCKER_TESTS') != '1', reason='Opt-in live offline Docker checker')
@pytest.mark.parametrize('phase,source,expected', [('baseline', ORIGINAL, 0), ('acceptance', ORIGINAL, 1),
                                                 ('acceptance', CANDIDATE, 0)])
def test_docker_citation_checker_executes_real_module_in_offline_container(tmp_path, phase, source, expected):
    (tmp_path / 'question.py').write_text(source, encoding='utf-8')
    checker = task.CitationChecker(ORIGINAL)
    result = checker.check(tmp_path, phase)
    assert result.returncode == expected and checker.runner.image_id.startswith('sha256:')
