"""Generate a real BM25 patch, compare before/after offline, leave source untouched."""

from __future__ import annotations

import argparse
import ast
import copy
from dataclasses import replace
import difflib
import hashlib
import html
import json
import math
from pathlib import Path
import statistics
import time
import uuid

from ..adapters import InfrastructureError, ProcessResult, process_environment, run_process, validate_test_evidence
from ..codex_docker import DockerCodexWorker, parse_turn
from ..docker_adapters import DockerRunner, MAX_SOURCE_BYTES, candidate_source
from ..workflow import build_graph

HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
TARGET = MANIFEST['target']
CHECKER_IMAGE = 'local-rag-bm25-compare:1'
INSTRUCTIONS = (
    'The source in question.py is the COMPLETE REAL app/retrievers/bm25.py module. '
    'Optimize ONLY the BODY of BM25Retriever.__init__ so each valid corpus document '
    'is tokenized exactly once during construction. Reuse those exact tokens for '
    'both validation and the BM25Okapi corpus and token_sets. Retain sorting by '
    'chunk ID and token alignment after sorting. Preserve all existing error types '
    'and validation, batch loading, metadata copying, attributes and public behavior. '
    'Do not change imports, constants, constructor signature or ANY code outside '
    'the constructor body, including search(). Do not add imports inside the constructor. '
    'Do not implement an alternative tokenizer, global cache, or test detection. '
    'Return the complete module source, not a fragment. '
)


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def read_source(repo):
    """Known public source only; unrelated local work is never copied into Docker."""
    result = {}
    expected = {TARGET: MANIFEST['source_sha256'],
                **{p: info['sha256'] for p, info in MANIFEST['files'].items()}}
    for relative, expected_hash in expected.items():
        path = repo / relative
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(repo.resolve()):
            raise InfrastructureError(f'Expected a regular repository file: {relative}')
        if path.stat().st_size > 65536:
            raise InfrastructureError(f'Repository file too large: {relative}')
        source = path.read_text(encoding='utf-8')  # Canonical LF permits Windows CRLF checkout.
        if digest(source) != expected_hash:
            raise InfrastructureError(f'Source differs from the reviewed baseline: {relative}; no files changed')
        result[relative] = source
    revision = run_process(['git', 'rev-parse', 'HEAD'], repo, timeout=10, env=process_environment())
    if revision.returncode:
        raise InfrastructureError('Could not identify source Git revision')
    return result[TARGET], revision.stdout.strip()


def validate_candidate(code, original):
    if not isinstance(code, str) or not code.strip() or len(code.encode('utf-8')) > MAX_SOURCE_BYTES:
        raise InfrastructureError('Empty or oversized BM25 source')
    try:
        baseline, candidate = ast.parse(original), ast.parse(code)

        def constructor(tree):
            cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'BM25Retriever')
            return next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == '__init__')

        old, new = constructor(baseline), constructor(candidate)
        if any(isinstance(n, (ast.Import, ast.ImportFrom)) for n in ast.walk(new)):
            raise ValueError('Unexpected constructor import')
        # Replace only the body for comparison, so signatures/decorators stay protected too.
        new.body = copy.deepcopy(old.body)
        if ast.dump(candidate, include_attributes=False) != ast.dump(baseline, include_attributes=False):
            raise ValueError('Change outside constructor body')
    except (ValueError, TypeError, SyntaxError, StopIteration, RecursionError) as exc:
        raise InfrastructureError('BM25 artifact changes code outside the allowed constructor body') from exc
    return code.rstrip() + '\n'


class BM25Worker(DockerCodexWorker):
    name = 'codex-real-bm25-docker'

    def __init__(self, original):
        super().__init__()
        self.original = original
        self.task = replace(self.task, instructions=INSTRUCTIONS)
        self.invocation_durations = []

    def implement(self, workspace, attempt, feedback):
        started = time.perf_counter()
        try:
            return super().implement(workspace, attempt, feedback)
        finally:
            self.invocation_durations.append(time.perf_counter() - started)

    def parse_artifact(self, output):
        artifact, usage = parse_turn(output)
        if set(artifact) != {'code'}:
            raise InfrastructureError('Expected one complete BM25 source artifact')
        try:
            code = validate_candidate(artifact['code'], self.original)
        except UnicodeError as exc:
            raise InfrastructureError('BM25 source is not valid UTF-8') from exc
        return {'question.py': code}, usage


def validate_comparison(data):
    """Reject missing/inconsistent measurements; never turn absent values into zero."""
    try:
        if data['document_count'] != 1000 or data['paired_trials'] != 7:
            raise ValueError()
        if data['dataset_sha256'] != MANIFEST['dataset_sha256'] or data['queries'] != MANIFEST['queries']:
            raise ValueError()
        for label in ('before', 'after'):
            values = data['init_ms'][label]
            if (len(values) != 7 or any(type(v) not in (int, float) or not math.isfinite(v) or v <= 0 for v in values)
                    or data['median_init_ms'][label] != statistics.median(values)):
                raise ValueError()
            count = data['init_tokenize_calls'][label]
            if type(count) is not int or count < 0:
                raise ValueError()
        if any(type(data[key]) is not bool for key in
               ('search_results_equal', 'single_pass_observed', 'tokenize_inputs_match_corpus')):
            raise ValueError()
        if data['search_results_equal'] != (data['search_results_sha256']['before'] == data['search_results_sha256']['after']):
            raise ValueError()
        expected_single = (data['init_tokenize_calls'] == {'before': 2000, 'after': 1000}
                           and data['tokenize_inputs_match_corpus'])
        if data['single_pass_observed'] != expected_single:
            raise ValueError()
    except (KeyError, ValueError, TypeError) as exc:
        raise InfrastructureError('Missing or inconsistent paired comparison evidence') from exc


class BM25Checker:
    isolation = 'docker'

    def __init__(self, original):
        self.original = original
        self.runner = DockerRunner(CHECKER_IMAGE, timeout=45)
        self.records = []

    def check(self, workspace, phase):
        process, response = self.runner.invoke('check', {
            'source': candidate_source(workspace), 'before_source': self.original, 'phase': phase}, workspace)
        if response.get('task_id') != 'bm25-tokenize-once':
            raise InfrastructureError('Wrong BM25 checker image')
        code, regression = response.get('returncode'), response.get('regression_returncode')
        if type(code) is not int or code != process.returncode or type(regression) is not int or regression not in (0, 1):
            raise InfrastructureError('Invalid BM25 result')
        if regression == 0:
            validate_test_evidence(response.get('junit', ''), 'acceptance',
                                   expected_cases=MANIFEST['regression_test_count'], baseline_skips=0)
            validate_comparison(response.get('comparison'))
            comparison = response['comparison']
            if phase == 'baseline' and (not comparison['search_results_equal'] or
                    comparison['init_tokenize_calls'] != {'before': 2000, 'after': 2000}):
                raise InfrastructureError('Baseline comparison is not the reviewed original behavior')
            expected_ok = phase == 'baseline' or (comparison['single_pass_observed'] and comparison['search_results_equal'])
            if code != (0 if expected_ok else 1):
                raise InfrastructureError('BM25 result disagrees with independent comparison')
        elif code != 1:
            raise InfrastructureError('Regression failure cannot be accepted')
        self.records.append({'phase': phase, 'regression_returncode': regression,
                             'comparison': response.get('comparison')})
        output = response.get('stdout', '') + response.get('stderr', '')
        if regression == 0:
            output += '\nIndependent initialization comparison: ' + json.dumps({
                key: response['comparison'][key] for key in
                ('init_tokenize_calls', 'single_pass_observed', 'search_results_equal')})
        return ProcessResult(code, output[-8000:], '')


def render(report, directory):
    comparison = report.get('comparison')
    rows = []
    regressions = {}
    for phase, label in [('baseline', 'before'), ('acceptance', 'after')]:
        record = next((r for r in reversed(report['verification']) if r['phase'] == phase), None)
        regressions[label] = ('68 passed' if record and record['regression_returncode'] == 0
                              else 'neověřeno / chyba')
    rows.append('<tr><th>Stejná regresní sada</th><td>' + regressions['before'] + '</td><td>' + regressions['after'] + '</td></tr>')
    if comparison:
        for label, key in [('Tokenizace při sestavení', 'init_tokenize_calls'),
                           ('Medián sestavení (ms)', 'median_init_ms')]:
            values = comparison[key]
            rows.append(f'<tr><th>{label}</th><td>{values["before"]:.3f}</td><td>{values["after"]:.3f}</td></tr>')
        rows.append('<tr><th>Výsledky šesti dotazů shodné</th><td colspan="2">' + str(comparison['search_results_equal']) + '</td></tr>')
    content = ('<!doctype html><meta charset="utf-8"><title>BM25 před a po</title>'
               '<style>body{font:17px system-ui;max-width:1000px;margin:3em auto;padding:1em;background:#111827;color:#eee}'
               'table{border-collapse:collapse;width:100%}td,th{border:1px solid #526071;padding:.7em;text-align:left}'
               'pre{white-space:pre-wrap;background:#1f2937;padding:1em}a{color:#8acbff}</style>'
               '<h1>BM25: před a po</h1><p>Status: ' + html.escape(report['status']) + '</p>'
               '<table><tr><th>Metrika</th><th>Před</th><th>Po</th></tr>' + ''.join(rows) + '</table>'
               '<p>Stejných 68 původních regresních testů. 1000 syntetických dokumentů, 7 párových měření. '
               'Čas je inicializace retrieveru; Chroma storage je nahrazena. Ranking rank_bm25 je skutečný. '
               'Nejde o měření celého RAG, PDF ingestu ani času modelu. Cena modelu není měřena.</p>'
               '<p>Zdroj: ' + html.escape(report['source_commit']) + ', SHA-256: ' + report['source_sha256'] + '</p>'
               '<p>Codex worker celkem: ' + str(report['codex_worker_elapsed_s']) + ' s '
               '(včetně jeho Docker režie). Celý běh: ' + str(report['duration_s']) + ' s.</p>'
               '<h2>Diff návrhu</h2><pre>' + html.escape(report['diff']) + '</pre>')
    (directory / 'report.html').write_text(content, encoding='utf-8')


def run(repo, output_root):
    original, revision = read_source(repo)
    directory = output_root / str(uuid.uuid4())
    directory.mkdir(parents=True, exist_ok=False)
    workspace = directory / 'workspace'
    workspace.mkdir()
    (workspace / 'question.py').write_bytes(original.encode('utf-8'))
    (directory / 'before.py').write_bytes(original.encode('utf-8'))
    worker, checker = BM25Worker(original), BM25Checker(original)
    started = time.perf_counter()
    state = build_graph(workspace, worker, checker).invoke(
        {'attempts': 0, 'status': 'pending', 'feedback': '', 'trace': []}, {'recursion_limit': 12})
    candidate = candidate_source(workspace)
    # Verify the user's actual source is still the reviewed original before exporting a patch.
    try:
        current, _ = read_source(repo)
        if current != original:
            raise InfrastructureError('Source changed during the run; no project patch exported')
    except (InfrastructureError, OSError) as exc:
        state.update(status='infrastructure_error', feedback=str(exc))
    patch = ''.join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
                                        fromfile='a/' + TARGET, tofile='b/' + TARGET))
    comparison = next((r['comparison'] for r in reversed(checker.records) if r['phase'] == 'acceptance'), None)
    report = {**state, 'task_id': 'bm25-tokenize-once', 'request_id': directory.name,
              'backend': worker.name, 'measurement': 'live-codex-real-repository',
              'source_repository': MANIFEST['repository'], 'source_commit': revision,
              'reviewed_source_commit': MANIFEST['source_commit'], 'target': TARGET,
              'source_sha256': digest(original), 'candidate_sha256': digest(candidate),
              'runner_image': checker.runner.image_id, 'worker_image': worker.image_id,
              'checker_isolation': 'docker', 'worker_attempts': worker.attempt_records,
              'duration_s': round(time.perf_counter() - started, 6), 'comparison': comparison,
              'codex_worker_elapsed_s': round(sum(worker.invocation_durations), 6),
              'authentication': 'chatgpt', 'model_usage_measured': bool(worker.attempt_records) and
              all(r.get('usage') is not None for r in worker.attempt_records),
              'regression_test_count': MANIFEST['regression_test_count'],
              'verification': checker.records, 'diff': patch, 'committed': False,
              'applied_to_rag': False, 'model_cost': None, 'model_calls': None}
    if state['status'] == 'review_ready':
        (directory / 'candidate.patch').write_text(patch, encoding='utf-8')
    (directory / 'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    render(report, directory)
    return report, directory


def main(argv=None):
    parser = argparse.ArgumentParser(description='One real BM25 improvement with paired offline before/after comparison')
    parser.add_argument('--repo', type=Path, default=HERE.parents[2])
    parser.add_argument('--output-root', type=Path, default=HERE.parent / '.runs/real-bm25')
    args = parser.parse_args(argv)
    try:
        report, directory = run(args.repo.resolve(), args.output_root.resolve())
    except (InfrastructureError, OSError, ValueError) as exc:
        parser.exit(1, str(exc) + '\n')
    print(json.dumps(report, indent=2))
    print('Report: ' + str(directory / 'report.html'))
    return 0 if report['status'] == 'review_ready' else 1


if __name__ == '__main__':
    raise SystemExit(main())
