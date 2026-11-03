"""Scope, source provenance and comparison checks; no model calls."""

import hashlib
import json
import os
from pathlib import Path

import pytest

from experiments.dev_loop.adapters import InfrastructureError, ProcessResult, process_environment, run_process
from experiments.dev_loop.real_bm25.__main__ import (
    HERE, MANIFEST, TARGET, BM25Worker, read_source, validate_candidate, validate_comparison,
)


ROOT = HERE.parents[2]


def reviewed_file(relative):
    """The fixture is pinned history, independent of accepted working-tree edits."""
    result = run_process(['git', 'show', f'{MANIFEST["source_commit"]}:{relative}'],
                         ROOT, timeout=10, env=process_environment())
    if result.returncode:
        raise RuntimeError('Reviewed Git source must be available for the BM25 tests')
    return result.stdout


ORIGINAL = reviewed_file(TARGET)


def reference_change(original):
    """Trusted test reference only. The real command always obtains code from Codex."""
    code = original.replace('records: list[tuple[str, str, Metadata]]',
                            'records: list[tuple[str, str, Metadata, list[str]]]')
    code = code.replace('if not isinstance(document, str) or not tokenize(document):',
                        'if not isinstance(document, str):\n'
                        '                    raise ValueError(f"Invalid document for chunk {chunk_id}")\n'
                        '                tokens = tokenize(document)\n'
                        '                if not tokens:')
    code = code.replace('(chunk_id, document, dict(metadata))', '(chunk_id, document, dict(metadata), tokens)')
    code = code.replace('tokenize(document)\n            for document in self.documents',
                        'record[3]\n            for record in records')
    return code


def test_real_source_and_vendored_checks_match_reviewed_git_provenance(monkeypatch, tmp_path):
    from experiments.dev_loop.real_bm25 import __main__ as module

    for relative in (TARGET, *MANIFEST['files']):
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(reviewed_file(relative), encoding='utf-8')
    monkeypatch.setattr(module, 'run_process', lambda *a, **k:
                        ProcessResult(0, MANIFEST['source_commit'] + '\n', ''))
    source, revision = read_source(tmp_path)
    assert source == ORIGINAL and revision == MANIFEST['source_commit']
    for info in MANIFEST['files'].values():
        source = (HERE / 'vendor' / info['vendor']).read_text(encoding='utf-8')
        assert hashlib.sha256(source.encode('utf-8')).hexdigest() == info.get('vendor_sha256', info['sha256'])


@pytest.mark.parametrize('change', [lambda source: source + '\n# unrelated local change\n', reference_change])
def test_real_source_with_local_changes_is_rejected_before_transport(tmp_path, change):
    target = tmp_path / TARGET
    target.parent.mkdir(parents=True)
    target.write_text(change(ORIGINAL), encoding='utf-8')
    with pytest.raises(InfrastructureError, match='differs'):
        read_source(tmp_path)


def test_only_constructor_body_can_change():
    assert validate_candidate(reference_change(ORIGINAL), ORIGINAL).startswith('\nimport chromadb')


@pytest.mark.parametrize('change', [
    lambda code: code.replace('def search(', 'def changed_search('),
    lambda code: code.replace('BATCH_SIZE = 500', 'BATCH_SIZE = 100'),
    lambda code: code.replace('def __init__(self, settings: Settings):', 'def __init__(self, settings):'),
    lambda code: code + '\nprint("unexpected top level")',
    lambda code: code.replace('import chromadb', 'import os'),
    lambda code: code.replace('self.settings = settings', 'import os\n        self.settings = settings'),
])
def test_other_code_and_nested_imports_cannot_be_changed(change):
    with pytest.raises(InfrastructureError, match='constructor'):
        validate_candidate(change(reference_change(ORIGINAL)), ORIGINAL)


def test_invalid_complete_module_is_rejected():
    with pytest.raises(InfrastructureError):
        validate_candidate('def broken(', ORIGINAL)
    with pytest.raises(InfrastructureError):
        BM25Worker(ORIGINAL).parse_artifact('\n'.join(json.dumps(event) for event in [
            {'type': 'item.completed', 'item': {'type': 'agent_message', 'text': '{"files":{}}'}},
            {'type': 'turn.completed'},
        ]))


def measurement():
    return {'document_count': 1000, 'paired_trials': 7,
            'dataset_sha256': MANIFEST['dataset_sha256'], 'queries': MANIFEST['queries'],
            'init_ms': {'before': [20.0] * 7, 'after': [15.0] * 7},
            'median_init_ms': {'before': 20.0, 'after': 15.0},
            'init_tokenize_calls': {'before': 2000, 'after': 1000},
            'single_pass_observed': True, 'search_results_equal': True, 'tokenize_inputs_match_corpus': True,
            'search_results_sha256': {'before': 'same', 'after': 'same'}}


def test_complete_measurements_are_required_and_missing_values_are_not_zero():
    validate_comparison(measurement())
    for data in [None, {}, {**measurement(), 'init_ms': {'before': [], 'after': []}},
                 {**measurement(), 'median_init_ms': {'before': 0, 'after': 0}},
                 {**measurement(), 'init_tokenize_calls': {'before': 2000, 'after': 2000}}]:
        with pytest.raises(InfrastructureError):
            validate_comparison(data)


@pytest.mark.parametrize('source_changed', [False, True])
def test_command_exports_patch_only_after_success_and_rechecks_user_source(monkeypatch, tmp_path, source_changed):
    from experiments.dev_loop.real_bm25 import __main__ as module
    from experiments.dev_loop.adapters import ProcessResult
    from types import SimpleNamespace

    reads = []

    def source(repo):
        reads.append(repo)
        if source_changed and len(reads) > 1:
            raise InfrastructureError('Source changed during the run')
        return ORIGINAL, 'a' * 40

    class Worker:
        name, image_id, isolation = 'trusted-test-reference', 'sha256:' + 'a' * 64, 'test-only'
        attempt_records = [{'attempt': 1, 'completed': True, 'usage': None}]
        invocation_durations = [1.0]

        def __init__(self, original):
            assert original == ORIGINAL

        def implement(self, workspace, attempt, feedback):
            (workspace / 'question.py').write_text(reference_change(ORIGINAL), encoding='utf-8')
            return 'Trusted local test reference; no model call'

    class Checker:
        runner = SimpleNamespace(image_id='sha256:' + 'b' * 64)

        def __init__(self, original):
            self.records = []

        def check(self, workspace, phase):
            data = measurement()
            if phase == 'baseline':
                data['init_tokenize_calls']['after'] = 2000
                data['single_pass_observed'] = False
                data['tokenize_inputs_match_corpus'] = False
            self.records.append({'phase': phase, 'regression_returncode': 0, 'comparison': data})
            return ProcessResult(0, '68 passed', '')

    monkeypatch.setattr(module, 'read_source', source)
    monkeypatch.setattr(module, 'BM25Worker', Worker)
    monkeypatch.setattr(module, 'BM25Checker', Checker)
    working_source = (ROOT / TARGET).read_bytes()
    report, directory = module.run(ROOT, tmp_path)
    assert len(reads) == 2 and (ROOT / TARGET).read_bytes() == working_source
    assert (directory / 'report.html').is_file() and (directory / 'result.json').is_file()
    assert report['comparison']['single_pass_observed'] and report['applied_to_rag'] is False
    assert (directory / 'candidate.patch').is_file() is (not source_changed)
    assert report['status'] == ('infrastructure_error' if source_changed else 'review_ready')
    if not source_changed:
        patch = (directory / 'candidate.patch').read_text(encoding='utf-8')
        assert patch.startswith('--- a/' + TARGET) and 'record[3]' in patch


@pytest.mark.skipif(os.environ.get('DEV_LOOP_REAL_BM25_DOCKER_TESTS') != '1',
                    reason='Optional real Docker comparison, no model call')
def test_live_checker_runs_same_68_regressions_and_detects_real_work_reduction(tmp_path):
    from experiments.dev_loop.real_bm25.__main__ import BM25Checker

    checker = BM25Checker(ORIGINAL)
    (tmp_path / 'question.py').write_text(ORIGINAL, encoding='utf-8')
    assert checker.check(tmp_path, 'baseline').returncode == 0
    assert checker.check(tmp_path, 'acceptance').returncode == 1
    (tmp_path / 'question.py').write_text(reference_change(ORIGINAL), encoding='utf-8')
    assert checker.check(tmp_path, 'acceptance').returncode == 0
