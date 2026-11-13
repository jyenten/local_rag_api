"""User-visible approval and recovery boundaries; no model or GitHub calls."""

from concurrent.futures import ThreadPoolExecutor
import json
import shutil
import threading
from types import SimpleNamespace
import uuid

from fastapi.testclient import TestClient
import pytest

from experiments.dev_loop import control_api as control
from experiments.dev_loop import publication_api as api
from experiments.dev_loop import real_jobs as jobs
from experiments.dev_loop.adapters import InfrastructureError
from experiments.dev_loop.tests.test_publish import BASE, ORIGINAL, run_dir
from experiments.dev_loop.tests.test_real_jobs import receipt

TOKEN = 'control-test-token-at-least-24-characters'
ID = '00000000-0000-4000-8000-000000000061'
HEADERS = {'X-Dev-Loop-Token': TOKEN}


@pytest.fixture
def panel(tmp_path, run_dir, monkeypatch):
    for module in (jobs, control):
        monkeypatch.setattr(module, 'read_source', lambda repo: (ORIGINAL, BASE))
    generated, published = [], []
    def generator(repo, output_root, *, request_id):
        generated.append(request_id)
        directory = output_root / request_id
        shutil.copytree(run_dir, directory)
        path = directory / 'result.json'
        data = json.loads(path.read_text())
        data.update(request_id=request_id, attempts=1, model_usage_measured=True,
                    committed=False, applied_to_rag=False,
                    worker_attempts=[{'attempt': 1}])
        path.write_text(json.dumps(data), encoding='utf-8')
        return data, directory
    def publisher(directory):
        published.append(directory.name)
        return receipt(directory.name)
    controller = jobs.RealJobs(tmp_path / 'source', tmp_path / 'jobs', generator=generator,
                               publisher=publisher, preflight=lambda: None)
    app = api.create_app(run_dir.parent, TOKEN, [run_dir.name], publisher=publisher, jobs=controller)
    return SimpleNamespace(client=TestClient(app, base_url='http://127.0.0.1'), jobs=controller,
                           old_run=run_dir, generated=generated, published=published)


def preview(panel, action, request_id=ID, **extra):
    return panel.client.post('/control/preview', headers=HEADERS,
                             json={'action': action, 'task_id': control.TASK_ID,
                                   'request_id': request_id, **extra})


def approved(panel, plan, **extra):
    return panel.client.post('/control/execute', headers=HEADERS, json={
        'action': plan['action'], 'task_id': plan['task_id'], 'request_id': plan['request_id'],
        'approved': True, 'plan_sha256': plan['plan_sha256'], **extra})


def test_catalog_and_plan_do_not_invoke_models_publish_or_claim_allowance(panel):
    catalog = preview(panel, 'catalog', None).json()
    assert catalog['tasks'][0]['allowed_run_ids'] == [panel.old_run.name]
    assert 'source' not in catalog['tasks'][0] and TOKEN not in json.dumps(catalog)
    plan = preview(panel, 'generate').json()
    assert plan['requires_approval'] is True
    assert plan['plan']['publication'] == 'separate_approval_required'
    assert panel.generated == [] and panel.published == [] and panel.jobs.used == 0
    assert not panel.jobs.root.exists()


def test_generate_review_report_then_separate_publication_and_no_regeneration(panel):
    plan = preview(panel, 'generate').json()
    result = approved(panel, plan)
    assert result.status_code == 200
    assert result.json()['result']['status'] == 'review_ready'
    assert result.json()['result']['publication_status'] == 'awaiting_approval'
    assert panel.generated == [ID] and panel.published == []
    status = preview(panel, 'status').json()['result']
    assert status['status'] == 'review_ready' and status['worker_invocations'] == 1
    report = preview(panel, 'report').json()['result']
    assert report['comparison']['init_tokenize_calls'] == {'before': 2000, 'after': 1000}
    assert 'records:' in report['diff'] and report['regression_test_count'] == 68
    plan = preview(panel, 'publish').json()
    assert plan['requires_approval'] and plan['plan']['model_invocations'] == 0
    assert panel.published == []
    response = approved(panel, plan).json()['result']
    assert response['status'] == 'pr_ready' and response['publication']['merge_allowed'] is False
    assert preview(panel, 'generate').json()['requires_approval'] is False
    assert preview(panel, 'publish').json()['requires_approval'] is False
    assert panel.generated == [ID] and panel.published == [ID]


def test_cancel_false_approval_and_forged_hash_never_mutate(panel):
    plan = preview(panel, 'generate').json()
    assert approved(panel, plan, approved=False).status_code == 403
    assert approved(panel, plan, approved='true').status_code == 422
    assert approved(panel, plan, plan_sha256='0' * 64).status_code == 409
    assert panel.jobs.used == 0 and panel.generated == [] and panel.published == []


def test_changed_budget_or_remote_preflight_invalidates_approval_before_model(panel):
    plan = preview(panel, 'generate').json()
    panel.jobs.used = 1
    assert approved(panel, plan).status_code == 409
    panel.jobs.used = 0
    def fail(): raise InfrastructureError('private remote baseline details')
    panel.jobs.preflight = fail
    response = preview(panel, 'generate')
    assert response.json()['error_code'] == 'SOURCE_OR_REMOTE_PREFLIGHT_BLOCKED'
    assert 'private' not in response.text and not response.json()['requires_approval']
    assert approved(panel, plan).status_code == 409
    assert panel.generated == [] and panel.jobs.used == 0


def test_local_source_drift_is_a_blocked_plan_without_exposing_host_details(panel, monkeypatch):
    plan = preview(panel, 'generate').json()
    def changed(repo): raise InfrastructureError('private source location')
    monkeypatch.setattr(control, 'read_source', changed)
    response = preview(panel, 'generate')
    assert response.json()['error_code'] == 'SOURCE_CHANGED' and 'private' not in response.text
    assert approved(panel, plan).status_code == 409
    assert panel.generated == [] and panel.jobs.used == 0


def test_changed_candidate_invalidates_publication_approval(panel):
    plan = preview(panel, 'publish', panel.old_run.name).json()
    path = panel.old_run / 'workspace/question.py'
    candidate = path.read_text().replace('tokens = tokenize(document)',
                                          'tokens = tokenize(document)  # reviewed change')
    path.write_text(candidate, encoding='utf-8')
    result_path = panel.old_run / 'result.json'
    data = json.loads(result_path.read_text())
    data['candidate_sha256'] = control.digest(candidate)
    result_path.write_text(json.dumps(data))
    assert preview(panel, 'publish', panel.old_run.name).json()['requires_approval']
    assert approved(panel, plan).status_code == 409 and panel.published == []


def test_registered_report_is_derived_and_does_not_export_raw_logs_html_or_host_paths(panel):
    path = panel.old_run / 'result.json'
    data = json.loads(path.read_text())
    data.update(diff='PRIVATE-TAMPERED-DIFF', raw_logs='HOST-SECRET', workspace='/host/private')
    data['comparison']['median_init_ms']['unexpected'] = '/host/private/nested'
    path.write_text(json.dumps(data))
    response = preview(panel, 'report', panel.old_run.name)
    assert response.status_code == 200 and 'records:' in response.json()['result']['diff']
    assert not any(value in response.text for value in ('PRIVATE-TAMPERED', 'HOST-SECRET', '/host/private'))
    blocked = preview(panel, 'generate', panel.old_run.name).json()
    assert blocked['error_code'] == 'SAVED_RUN_CANNOT_BE_REGENERATED'
    data['comparison']['init_tokenize_calls']['unexpected'] = 'HOST-SECRET'
    path.write_text(json.dumps(data))
    rejected = preview(panel, 'report', panel.old_run.name)
    assert rejected.status_code == 503 and 'HOST-SECRET' not in rejected.text


@pytest.mark.parametrize('extra', [{'command': 'shell'}, {'prompt': 'new task'}, {'run_dir': '/private'},
                                 {'max_attempts': 30}, {'allowed_files': ['.env']}])
def test_control_cannot_expand_host_registration_or_limits(panel, extra):
    assert preview(panel, 'generate', **extra).status_code == 422
    plan = preview(panel, 'generate').json()
    assert approved(panel, plan, **extra).status_code == 422
    assert panel.generated == [] and panel.published == []


def test_auth_wrong_task_uuid_and_missing_id_fail_before_any_action(panel):
    assert panel.client.post('/control/preview', json={'action': 'catalog'}).status_code == 401
    assert panel.client.post('/control/execute', content='not-json').status_code == 401
    assert preview(panel, 'report', None).status_code == 422
    assert preview(panel, 'generate', '../private').status_code == 422
    assert preview(panel, 'catalog', None, task_id='fix-anything').status_code == 422
    assert preview(panel, 'publish', str(uuid.uuid4())).status_code == 404
    assert panel.generated == [] and panel.published == []


def test_job_generation_cannot_be_reached_through_publish_existing(panel):
    with pytest.raises(FileNotFoundError): panel.jobs.publish_existing(ID)
    assert panel.generated == [] and panel.jobs.used == 0


def test_publication_failure_needs_another_approval_and_never_regenerates(panel):
    approved(panel, preview(panel, 'generate').json())
    def fail(directory): raise InfrastructureError('private publication failure')
    real = panel.jobs.publisher
    panel.jobs.publisher = fail
    first = approved(panel, preview(panel, 'publish').json())
    assert first.json()['result']['status'] == 'publication_blocked'
    panel.jobs.publisher = real
    second = approved(panel, preview(panel, 'publish').json())
    assert second.json()['result']['status'] == 'pr_ready'
    assert panel.generated == [ID] and panel.published == [ID]


def test_status_is_readable_during_generation_and_mutations_are_serialized(panel):
    entered, release = threading.Event(), threading.Event()
    original = panel.jobs.generator
    def generate(*args, **kwargs):
        entered.set()
        assert release.wait(5)
        return original(*args, **kwargs)
    panel.jobs.generator = generate
    plan = preview(panel, 'generate').json()
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(approved, panel, plan)
        try:
            assert entered.wait(5)
            assert preview(panel, 'status').json()['result']['status'] == 'generating'
            assert approved(panel, plan).status_code == 409
            # The legacy publication route shares the same mutation lock.
            response = panel.client.post('/publications', headers=HEADERS,
                json={'task_id': control.TASK_ID, 'run_id': panel.old_run.name})
            assert response.status_code == 409 and panel.published == []
        finally:
            release.set()
        assert future.result().status_code == 200
    assert panel.generated == [ID] and panel.published == []


def test_restart_and_interrupted_generation_never_silently_call_model(panel):
    approved(panel, preview(panel, 'generate').json())
    panel.jobs.used = 0  # A new process resets only its session allowance, not the saved identity.
    assert preview(panel, 'generate').json()['result']['status'] == 'review_ready'
    other = str(uuid.uuid4())
    _, directory, _ = panel.jobs.paths(other)
    directory.mkdir()
    jobs.write_json(directory / 'request.json', panel.jobs.identity(other))
    jobs.write_json(directory / 'state.json', {'status': 'generating'})
    assert preview(panel, 'generate', other).json()['error_code'] == 'JOB_ACTIVE_OR_INTERRUPTED'
    assert panel.generated == [ID]


def test_read_only_service_supports_reports_and_explains_disabled_generation(panel):
    app = api.create_app(panel.old_run.parent, TOKEN, [panel.old_run.name])
    panel.client = TestClient(app, base_url='http://127.0.0.1')
    assert preview(panel, 'report', panel.old_run.name).status_code == 200
    assert preview(panel, 'generate').json()['error_code'] == 'NEW_JOBS_NOT_CONFIGURED'
