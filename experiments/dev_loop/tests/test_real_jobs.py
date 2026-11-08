"""Generation idempotency and HTTP real-job handoff without model or GitHub calls."""

import json
from pathlib import Path
from types import SimpleNamespace
import uuid

from fastapi.testclient import TestClient
import pytest

from experiments.dev_loop import real_jobs as jobs
from experiments.dev_loop import publication_api as api
from experiments.dev_loop.adapters import InfrastructureError
from experiments.dev_loop.real_bm25.__main__ import MANIFEST, digest
from experiments.dev_loop.workflow import JobConflict

TOKEN = 'test-token-with-at-least-24-characters'
SOURCE_COMMIT = 'a' * 40
REQUEST_ID = '00000000-0000-4000-8000-000000000051'
OLD_ID = 'a5739357-6da4-4118-be18-5c038306e0e9'
SOURCE = 'trusted-test-source'


def receipt(request_id):
    return {'request_id': request_id, 'task_id': jobs.TASK_ID, 'repository': jobs.REPOSITORY,
            'base': 'main', 'base_sha': 'b' * 40, 'head_sha': 'c' * 40, 'branch': 'test-branch',
            'allowed_files': [MANIFEST['target']], 'candidate_sha256': 'd' * 64,
            'pull_request': 'https://github.com/jyenten/local_rag_api/pull/10',
            'draft': True, 'reused_existing_pr': True, 'published_to_github': True,
            'local_source_changed': False, 'merged': False, 'merge_allowed': False,
            'ci_status': 'not_checked', 'checker_image': 'sha256:' + 'e' * 64,
            'workspace': '/not-for-http', 'verification': [{'private': 'not-for-http'}]}


@pytest.fixture
def harness(tmp_path, monkeypatch):
    monkeypatch.setattr(jobs, 'read_source', lambda repo: (SOURCE, SOURCE_COMMIT))
    generated, published = [], []
    state = {'generation_status': 'review_ready', 'publication_error': False}
    def generator(repo, output_root, *, request_id):
        generated.append(request_id)
        directory = output_root / request_id
        directory.mkdir(parents=True)
        report = {'request_id': request_id, 'task_id': jobs.TASK_ID,
                  'source_repository': jobs.REPOSITORY, 'source_commit': SOURCE_COMMIT,
                  'source_sha256': digest(SOURCE), 'backend': 'codex-real-bm25-docker',
                  'measurement': 'live-codex-real-repository', 'reviewed_source_commit': MANIFEST['source_commit'],
                  'target': MANIFEST['target'], 'checker_isolation': 'docker',
                  'committed': False, 'applied_to_rag': False, 'status': state['generation_status'],
                  'attempts': 1, 'model_usage_measured': True, 'worker_attempts': [{'attempt': 1}]}
        (directory / 'result.json').write_text(json.dumps(report))
        return report, directory
    def publisher(directory):
        published.append(directory.name)
        if state['publication_error']: raise InfrastructureError('test host-only failure')
        return receipt(directory.name)
    def create(**options):
        return jobs.RealJobs(tmp_path / 'source', tmp_path / 'jobs', generator=generator,
                             publisher=publisher, preflight=lambda: None, **options)
    return SimpleNamespace(create=create, generated=generated, published=published, state=state,
                           generator=generator, publisher=publisher, root=tmp_path / 'jobs')


def test_new_job_generates_then_publishes_and_same_id_never_regenerates_even_after_restart(harness):
    controller = harness.create()
    first = controller.execute(REQUEST_ID)
    assert first['status'] == 'pr_ready' and first['generation_cached'] is False
    assert first['publication']['pull_request'].endswith('/10')
    assert first['worker_invocations'] == 1 and first['attempts'] == 1
    assert 'not-for-http' not in json.dumps(first)
    assert controller.capabilities()['new_jobs_remaining'] == 0
    assert controller.execute(REQUEST_ID)['generation_cached'] is True
    assert harness.create().execute(REQUEST_ID)['generation_cached'] is True
    assert harness.generated == [REQUEST_ID] and harness.published == [REQUEST_ID]


def test_failed_publication_retries_only_publisher_not_codex(harness):
    harness.state['publication_error'] = True
    first = harness.create().execute(REQUEST_ID)
    assert first['status'] == 'publication_blocked' and first['generation_status'] == 'review_ready'
    assert first['publication_status'] == 'blocked' and first['error_code'] == 'PUBLICATION_STOPPED_INSPECT_HOST'
    harness.state['publication_error'] = False
    second = harness.create().execute(REQUEST_ID)
    assert second['status'] == 'pr_ready' and second['generation_cached'] is True
    assert harness.generated == [REQUEST_ID] and harness.published == [REQUEST_ID, REQUEST_ID]


def test_host_allowance_and_failed_acceptance_do_not_create_unbounded_new_calls(harness):
    harness.state['generation_status'] = 'attempt_limit'
    controller = harness.create()
    first = controller.execute(REQUEST_ID)
    assert first['status'] == 'generation_failed' and harness.published == []
    assert controller.execute(REQUEST_ID)['generation_cached'] is True
    with pytest.raises(jobs.NewJobLimit): controller.execute(str(uuid.uuid4()))
    assert harness.generated == [REQUEST_ID]


def test_interrupted_job_without_result_is_never_automatically_regenerated(harness):
    controller = harness.create()
    _, directory, _ = controller.paths(REQUEST_ID)
    directory.mkdir(parents=True)
    jobs.write_json(directory / 'request.json', controller.identity(REQUEST_ID))
    jobs.write_json(directory / 'state.json', {'status': 'generating'})
    assert controller.status(REQUEST_ID)['status'] == 'generating'
    with pytest.raises(JobConflict, match='interrupted'): controller.execute(REQUEST_ID)
    assert harness.generated == [] and harness.published == []


def test_completed_run_is_recovered_after_crash_before_publication(harness):
    controller = harness.create()
    _, directory, _ = controller.paths(REQUEST_ID)
    directory.mkdir(parents=True)
    jobs.write_json(directory / 'request.json', controller.identity(REQUEST_ID))
    jobs.write_json(directory / 'state.json', {'status': 'generating'})
    harness.generator(controller.source_repo, controller.root / 'runs', request_id=REQUEST_ID)
    assert controller.execute(REQUEST_ID)['status'] == 'pr_ready'
    assert len(harness.generated) == 1


def test_generation_exception_is_terminal_and_does_not_trigger_automatic_retry(harness):
    controller = harness.create()
    calls = []
    def failed(*a, **kw):
        calls.append(kw['request_id'])
        raise InfrastructureError('host-only exception details')
    controller.generator = failed
    state = controller.execute(REQUEST_ID)
    assert state['status'] == 'generation_error' and 'host-only' not in json.dumps(state)
    assert controller.execute(REQUEST_ID)['generation_cached'] is True
    assert harness.create().execute(REQUEST_ID)['generation_cached'] is True
    assert calls == [REQUEST_ID]


def test_source_change_and_mismatched_saved_identity_stop_generation(harness, monkeypatch):
    controller = harness.create()
    monkeypatch.setattr(jobs, 'read_source', lambda repo: ('changed', SOURCE_COMMIT))
    with pytest.raises(JobConflict, match='Source changed'): controller.execute(REQUEST_ID)
    assert harness.generated == []
    monkeypatch.setattr(jobs, 'read_source', lambda repo: (SOURCE, SOURCE_COMMIT))
    controller.execute(REQUEST_ID)
    request = harness.root / 'requests' / REQUEST_ID / 'request.json'
    data = json.loads(request.read_text())
    data['source_commit'] = 'f' * 40
    request.write_text(json.dumps(data))
    with pytest.raises(JobConflict, match='different source'): controller.execute(REQUEST_ID)
    assert len(harness.generated) == 1


def test_tampered_state_symlinks_and_bad_allowance_are_rejected(harness, tmp_path):
    for allowance in (0, 21, True):
        with pytest.raises(ValueError): harness.create(max_new_jobs=allowance)
    controller = harness.create()
    controller.execute(REQUEST_ID)
    state_file = harness.root / 'requests' / REQUEST_ID / 'state.json'
    state = json.loads(state_file.read_text())
    state['publication']['merge_allowed'] = True
    state_file.write_text(json.dumps(state))
    with pytest.raises(InfrastructureError): controller.status(REQUEST_ID)
    other = tmp_path / 'outside'
    other.mkdir()
    next_dir = harness.root / 'requests' / str(uuid.uuid4())
    try: next_dir.symlink_to(other, target_is_directory=True)
    except OSError: pytest.skip('Symlinks unavailable')
    with pytest.raises(InfrastructureError): controller.execute(next_dir.name)


def api_client(tmp_path, controller):
    app = api.create_app(tmp_path / 'old-runs', TOKEN, [OLD_ID], jobs=controller)
    return TestClient(app, base_url='http://127.0.0.1')


def test_http_to_real_controller_generation_and_pr_handoff_is_idempotent(harness, tmp_path):
    c = api_client(tmp_path, harness.create())
    headers = {'X-Dev-Loop-Token': TOKEN}
    body = {'task_id': jobs.TASK_ID, 'request_id': REQUEST_ID}
    assert c.post('/jobs', json=body).status_code == 401
    assert c.get('/jobs/' + REQUEST_ID, headers=headers).status_code == 404
    capabilities = c.get('/tasks', headers=headers).json()['real_job']
    assert capabilities['new_jobs_remaining'] == 1 and capabilities['max_attempts'] == 3
    first = c.post('/jobs', json=body, headers=headers)
    assert first.status_code == 200 and first.json()['status'] == 'pr_ready'
    again = c.post('/jobs', json=body, headers=headers)
    assert again.json()['generation_cached'] is True and harness.generated == [REQUEST_ID]
    saved = c.get('/jobs/' + REQUEST_ID, headers=headers)
    assert saved.status_code == 200 and saved.json()['status'] == 'pr_ready'
    exhausted = c.post('/jobs', json={**body, 'request_id': str(uuid.uuid4())}, headers=headers)
    assert exhausted.status_code == 429
    assert len(harness.generated) == 1


@pytest.mark.parametrize('extra', [{'repo': '../private'}, {'source_repo': '/private'},
                                 {'prompt': 'arbitrary task'}, {'max_attempts': 100}, {'publish': False}])
def test_job_requests_cannot_choose_paths_prompts_attempts_or_actions(harness, tmp_path, extra):
    c = api_client(tmp_path, harness.create())
    body = {'task_id': jobs.TASK_ID, 'request_id': REQUEST_ID, **extra}
    assert c.post('/jobs', json=body, headers={'X-Dev-Loop-Token': TOKEN}).status_code == 422
    assert harness.generated == []


def test_real_jobs_are_disabled_without_explicit_host_registration(tmp_path):
    c = api_client(tmp_path, None)
    headers = {'X-Dev-Loop-Token': TOKEN}
    assert 'real_job' not in c.get('/tasks', headers=headers).json()
    assert c.post('/jobs', json={'task_id': jobs.TASK_ID, 'request_id': REQUEST_ID}, headers=headers).status_code == 404


def test_incomplete_job_conflict_and_active_job_serialize_with_publication(harness, tmp_path):
    controller = harness.create()
    assert controller.lock.acquire(blocking=False)
    try:
        c = api_client(tmp_path, controller)
        response = c.post('/jobs', headers={'X-Dev-Loop-Token': TOKEN},
                          json={'task_id': jobs.TASK_ID, 'request_id': REQUEST_ID})
        assert response.status_code == 409
    finally: controller.lock.release()
    assert harness.generated == []


def test_cli_enables_jobs_only_with_reviewed_source_and_keeps_loopback(tmp_path, monkeypatch):
    import uvicorn
    observed, calls = [], []
    class Controller:
        def __init__(self, *args): observed.append(args)
    monkeypatch.setattr(jobs, 'RealJobs', Controller)
    monkeypatch.setattr(api, 'load_bundle', lambda path: None)
    monkeypatch.setenv('DEV_LOOP_TOKEN', TOKEN)
    monkeypatch.setattr(uvicorn, 'run', lambda app, **kw: calls.append(kw))
    assert api.main(['--runs-root', str(tmp_path / 'runs'), '--allow-run', OLD_ID,
                     '--source-repo', str(tmp_path / 'source'), '--jobs-root', str(tmp_path / 'jobs')]) == 0
    assert observed == [(tmp_path / 'source', tmp_path / 'jobs', 1)]
    assert calls[0]['host'] == '127.0.0.1'
    with pytest.raises(SystemExit):
        api.main(['--runs-root', str(tmp_path / 'runs'), '--allow-run', OLD_ID, '--max-new-jobs', '2'])


def test_new_workflow_generates_a_job_uuid_not_a_saved_run_selection():
    path = Path(__file__).resolve().parents[1] / 'n8n-real-bm25-workflow.json'
    flow = json.loads(path.read_text())
    assert flow['active'] is False and len(flow['nodes']) == 2
    node = next(n for n in flow['nodes'] if n['type'] == 'n8n-nodes-base.httpRequest')
    assert node['parameters']['url'] == 'http://host.docker.internal:8766/jobs'
    assert '$execution.id' in node['parameters']['jsonBody']
    assert 'request_id' in node['parameters']['jsonBody'] and 'run_id' not in node['parameters']['jsonBody']
    assert node['retryOnFail'] is False and 'credentials' not in node


def test_real_graph_writes_requested_uuid_and_refuses_to_rerun_existing_directory(tmp_path, monkeypatch):
    from experiments.dev_loop.real_bm25 import __main__ as real
    from experiments.dev_loop.tests.test_real_bm25 import ORIGINAL, reference_change, measurement
    from experiments.dev_loop.adapters import ProcessResult
    monkeypatch.setattr(real, 'read_source', lambda repo: (ORIGINAL, SOURCE_COMMIT))
    calls = []
    class Worker:
        name = 'codex-real-bm25-docker'
        image_id = 'sha256:' + 'f' * 64
        attempt_records = []
        invocation_durations = []
        def __init__(self, original): assert original == ORIGINAL
        def implement(self, workspace, attempt, feedback):
            calls.append(attempt)
            (workspace / 'question.py').write_text(reference_change(ORIGINAL))
            return 'Trusted local test reference; no model call'
    class Checker:
        runner = SimpleNamespace(image_id='sha256:' + 'e' * 64)
        def __init__(self, original): self.records = []
        def check(self, workspace, phase):
            data = measurement()
            if phase == 'baseline':
                data['init_tokenize_calls']['after'] = 2000
                data['single_pass_observed'] = False
                data['tokenize_inputs_match_corpus'] = False
            self.records.append({'phase': phase, 'regression_returncode': 0, 'comparison': data})
            return ProcessResult(0, 'test-only', '')
    monkeypatch.setattr(real, 'BM25Worker', Worker)
    monkeypatch.setattr(real, 'BM25Checker', Checker)
    report, directory = real.run(tmp_path / 'source', tmp_path / 'runs', request_id=REQUEST_ID)
    assert report['request_id'] == REQUEST_ID and report['status'] == 'review_ready'
    assert directory == tmp_path / 'runs' / REQUEST_ID and calls == [1]
    original_report = (directory / 'result.json').read_bytes()
    with pytest.raises(FileExistsError):
        real.run(tmp_path / 'source', tmp_path / 'runs', request_id=REQUEST_ID)
    assert calls == [1] and (directory / 'result.json').read_bytes() == original_report


def test_github_preflight_failure_stops_before_budget_claim_or_model_call(harness):
    controller = harness.create()
    def fail(): raise InfrastructureError('Remote baseline changed')
    controller.preflight = fail
    with pytest.raises(InfrastructureError, match='baseline'): controller.execute(REQUEST_ID)
    assert harness.generated == [] and harness.published == []
    assert controller.capabilities()['new_jobs_remaining'] == 1
    assert not (harness.root / 'requests' / REQUEST_ID).exists()


def test_real_github_preflight_checks_fixed_repo_and_both_source_revisions(harness, monkeypatch):
    controller = harness.create()
    calls = []
    class Client:
        def __init__(self, cwd): assert cwd == controller.source_repo
        def api(self, method, path=''):
            calls.append(path)
            if not path: return {'id': jobs.REPOSITORY_ID}
            return {'object': {'sha': 'b' * 40}}
    revisions = []
    monkeypatch.setattr(jobs, 'GitHub', Client)
    monkeypatch.setattr(jobs, 'check_revision', lambda client, revision, original:
                        revisions.append((revision, original)))
    controller.github_preflight()
    assert calls == ['', 'git/ref/heads/main']
    assert revisions == [('b' * 40, SOURCE), (SOURCE_COMMIT, SOURCE)]
