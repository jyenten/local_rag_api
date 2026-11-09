"""One reviewed real-repository citation repair; generation never publishes."""

import ast
from dataclasses import replace
import difflib
import html
import json
from pathlib import Path
import time
import uuid

from ..adapters import InfrastructureError, ProcessResult, process_environment, run_process, validate_test_evidence
from ..codex_docker import DockerCodexWorker, parse_turn
from ..docker_adapters import DockerRunner, MAX_SOURCE_BYTES, candidate_source
from ..real_bm25.__main__ import digest
from ..workflow import build_graph

HERE = Path(__file__).resolve().parent
MANIFEST = json.loads((HERE / 'manifest.json').read_text(encoding='utf-8'))
TARGET = MANIFEST['target']
TASK_ID = 'retrieval-citation-provenance'
CHECKER_IMAGE = 'local-rag-citation-check:1'
PROBE_KEYS = {'fallback_source_and_page_correct', 'negative_best_retained'}
INSTRUCTIONS = (
    'question.py contains the COMPLETE REAL app/retrieval.py module. Change ONLY the bodies of '
    'Retriever.rerank_lines and Retriever.build_context. Preserve imports, signatures, all other '
    'code, positive-score ranking, search results and context/source return shape. '
    'Fix fallback selection so every selected line retains its actual source/page/chunk metadata, '
    'deduplicate repeated lines and respect max_context_lines. Never assign the first document '
    'metadata to unrelated text. If all combined reranker/heuristic scores are negative, retain '
    'at least the highest-scoring candidate; keep existing behavior for positive scores. '
    'Do not add imports, reflection, file access, test detection, alternate models or test code. '
    'Return the complete module. The controller supplies independent fixed regression tests.'
)


def fixed_files():
    source = (HERE / 'checks/test_retrieval_citations.py').read_text(encoding='utf-8')
    if digest(source) != MANIFEST['fixed_test_sha256']:
        raise InfrastructureError('Fixed citation regressions differ from the reviewed registration')
    return {MANIFEST['fixed_test_target']: source}


def read_source(repo):
    repo = Path(repo)
    path = repo / TARGET
    if (path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(repo.resolve())
            or path.stat().st_size > MAX_SOURCE_BYTES):
        raise InfrastructureError('Expected the reviewed public retrieval module')
    source = path.read_text(encoding='utf-8')
    if digest(source) != MANIFEST['source_sha256']:
        raise InfrastructureError('Retrieval source changed; review the citation baseline again')
    tests = repo / MANIFEST['fixed_test_target']
    if tests.exists() or tests.is_symlink():
        raise InfrastructureError('Fixed regression destination already exists; review baseline')
    fixed_files()
    result = run_process(['git', 'rev-parse', 'HEAD'], repo, timeout=10, env=process_environment())
    if result.returncode:
        raise InfrastructureError('Could not identify the source Git revision')
    return source, result.stdout.strip()


def validate_candidate(code, original):
    if not isinstance(code, str) or not code.strip() or len(code.encode('utf-8')) > MAX_SOURCE_BYTES:
        raise InfrastructureError('Empty or oversized retrieval candidate')
    try:
        baseline, candidate = ast.parse(original), ast.parse(code)
        before = next(n for n in baseline.body if isinstance(n, ast.ClassDef) and n.name == 'Retriever')
        after = next(n for n in candidate.body if isinstance(n, ast.ClassDef) and n.name == 'Retriever')
        for name in ('rerank_lines', 'build_context'):
            old = next(n for n in before.body if isinstance(n, ast.FunctionDef) and n.name == name)
            new = next(n for n in after.body if isinstance(n, ast.FunctionDef) and n.name == name)
            forbidden = {'open', 'eval', 'exec', 'compile', '__import__', 'globals', 'locals',
                         'getattr', 'setattr', 'vars', 'os', 'sys', 'Path'}
            if any(isinstance(n, (ast.Import, ast.ImportFrom))
                   or isinstance(n, ast.Name) and (n.id in forbidden or n.id.startswith('__'))
                   or isinstance(n, ast.Attribute) and n.attr.startswith('__')
                   for n in ast.walk(new)):
                raise ValueError('Unexpected import/reflection or IO')
            new.body = old.body
        if ast.dump(candidate, include_attributes=False) != ast.dump(baseline, include_attributes=False):
            raise ValueError('Change outside the registered method bodies')
    except (ValueError, SyntaxError, TypeError, StopIteration, RecursionError) as exc:
        raise InfrastructureError('Candidate exceeds the two allowed retrieval method bodies') from exc
    return code.rstrip() + '\n'


def validate_observation(data):
    if not isinstance(data, dict) or set(data) != PROBE_KEYS or any(type(v) is not bool for v in data.values()):
        raise InfrastructureError('Missing independent citation probe evidence')


def validate_comparison(data):
    if not isinstance(data, dict) or set(data) != {'before', 'after'}:
        raise InfrastructureError('Missing before/after citation evidence')
    for phase in ('before', 'after'):
        validate_observation(data[phase])
    if any(data['before'].values()) or not all(data['after'].values()):
        raise InfrastructureError('Citation comparison did not demonstrate the reviewed repair')


class CitationWorker(DockerCodexWorker):
    name = 'codex-real-citations-docker'

    def __init__(self, original):
        super().__init__()
        self.original = original
        self.task = replace(self.task, instructions=INSTRUCTIONS)

    def parse_artifact(self, output):
        artifact, usage = parse_turn(output)
        if set(artifact) != {'code'}:
            raise InfrastructureError('Expected one complete retrieval module')
        return {'question.py': validate_candidate(artifact['code'], self.original)}, usage


class CitationChecker:
    isolation = 'docker'

    def __init__(self, original):
        self.original, self.records = original, []
        self.runner = DockerRunner(CHECKER_IMAGE, timeout=45)

    def check(self, workspace, phase):
        if phase not in {'baseline', 'acceptance'}:
            raise InfrastructureError('Unknown citation check phase')
        process, response = self.runner.invoke('check', {'source': candidate_source(workspace),
            'before_source': self.original, 'phase': phase}, workspace)
        code, regression = response.get('returncode'), response.get('regression_returncode')
        if (response.get('task_id') != TASK_ID or type(code) is not int or code not in (0, 1)
                or code != process.returncode or type(regression) is not int or regression not in (0, 1)):
            raise InfrastructureError('Wrong citation checker identity or invalid result')
        observed = response.get('comparison')
        validate_observation(observed)
        if regression == 0:
            validate_test_evidence(response.get('junit', ''), 'acceptance',
                expected_cases=MANIFEST['baseline_test_count'] if phase == 'baseline' else MANIFEST['regression_test_count'],
                baseline_skips=0)
        expected = regression == 0 and (not any(observed.values()) if phase == 'baseline' else all(observed.values()))
        if code != (0 if expected else 1):
            raise InfrastructureError('Checker outcome disagrees with independent citation evidence')
        self.records.append({'phase': phase, 'regression_returncode': regression, 'comparison': observed})
        output = response.get('stdout', '') + response.get('stderr', '')
        return ProcessResult(code, (output + '\nIndependent citation probes: ' + json.dumps(observed))[-8000:], '')


def run(repo, output_root, *, request_id=None):
    original, revision = read_source(repo)
    directory = Path(output_root) / str(uuid.UUID(str(request_id)) if request_id else uuid.uuid4())
    directory.mkdir(parents=True, exist_ok=False)
    workspace = directory / 'workspace'
    workspace.mkdir()
    (workspace / 'question.py').write_text(original, encoding='utf-8')
    (directory / 'before.py').write_text(original, encoding='utf-8')
    worker, checker = CitationWorker(original), CitationChecker(original)
    started = time.perf_counter()
    state = build_graph(workspace, worker, checker).invoke(
        {'attempts': 0, 'status': 'pending', 'feedback': '', 'trace': []}, {'recursion_limit': 12})
    candidate = candidate_source(workspace)
    current, current_revision = read_source(repo)
    if current != original or current_revision != revision:
        state.update(status='infrastructure_error', feedback='Source changed during generation')
    comparison = {label: next((r['comparison'] for r in reversed(checker.records) if r['phase'] == phase), None)
                  for label, phase in [('before', 'baseline'), ('after', 'acceptance')]}
    fixed = fixed_files()
    patch = ''.join(difflib.unified_diff(original.splitlines(True), candidate.splitlines(True),
                                        fromfile='a/' + TARGET, tofile='b/' + TARGET))
    for name, source in fixed.items():
        patch += ''.join(difflib.unified_diff([], source.splitlines(True), fromfile='/dev/null', tofile='b/' + name))
    report = {**state, 'request_id': directory.name, 'task_id': TASK_ID, 'backend': worker.name,
        'measurement': 'live-codex-real-repository', 'source_repository': MANIFEST['repository'],
        'source_commit': revision, 'reviewed_source_commit': MANIFEST['source_commit'], 'target': TARGET,
        'source_sha256': digest(original), 'candidate_sha256': digest(candidate),
        'fixed_files_sha256': {name: digest(source) for name, source in fixed.items()},
        'runner_image': checker.runner.image_id, 'worker_image': worker.image_id,
        'checker_isolation': 'docker', 'worker_attempts': worker.attempt_records,
        'duration_s': round(time.perf_counter() - started, 6), 'comparison': comparison,
        'authentication': 'chatgpt', 'model_cost': None, 'model_calls': None,
        'model_usage_measured': bool(worker.attempt_records) and all(r.get('usage') is not None for r in worker.attempt_records),
        'regression_test_count': MANIFEST['regression_test_count'], 'verification': checker.records,
        'diff': patch, 'committed': False, 'applied_to_rag': False}
    (directory / 'result.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    if state['status'] == 'review_ready':
        validate_comparison(comparison)
        (directory / 'candidate.patch').write_text(patch, encoding='utf-8')
    (directory / 'report.html').write_text('<!doctype html><meta charset="utf-8"><h1>Citation provenance</h1><pre>'
        + html.escape(json.dumps(report, indent=2)) + '</pre>', encoding='utf-8')
    return report, directory
