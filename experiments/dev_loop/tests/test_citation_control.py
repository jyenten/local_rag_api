"""n8n-to-citation-task contract with durable model/publisher stand-ins only."""

import json
import shutil
from types import SimpleNamespace

from fastapi.testclient import TestClient
import pytest

from experiments.dev_loop import publication_api as api
from experiments.dev_loop import real_jobs
from experiments.dev_loop import publish
from experiments.dev_loop.citations import task
from experiments.dev_loop.registered_tasks import BM25, CITATIONS
from experiments.dev_loop.tests.test_citations import citation_run, ORIGINAL, BASE
from experiments.dev_loop.tests.test_publish import run_dir

ID = '00000000-0000-4000-8000-000000000072'
TOKEN = 'citation-control-test-at-least-24-characters'
HEADERS = {'X-Dev-Loop-Token': TOKEN}


@pytest.fixture
def panel(tmp_path, citation_run, run_dir, monkeypatch):
    monkeypatch.setattr(task, 'read_source', lambda repo: (ORIGINAL, BASE))
    generated, published = [], []
    def generator(repo, output_root, *, request_id):
        generated.append(request_id)
        destination = output_root / request_id
        shutil.copytree(citation_run, destination)
        path = destination / 'result.json'
        data = json.loads(path.read_text())
        data['request_id'] = request_id
        path.write_text(json.dumps(data))
        return data, destination
    def publisher(directory):
        published.append(directory.name)
        bundle = publish.load_bundle(directory)
        return {**bundle.plan(), 'publish_requested': True, 'base_sha': BASE, 'head_sha': 'c' * 40,
            'pull_request': 'https://github.com/jyenten/local_rag_api/pull/123', 'reused_existing_pr': False,
            'published_to_github': True, 'local_source_changed': False, 'merged': False,
            'ci_status': 'not_checked', 'checker_image': bundle.report['runner_image']}
    jobs = real_jobs.RealJobs(tmp_path / 'source', tmp_path / 'jobs', generator=generator,
                             publisher=publisher, preflight=lambda: None, task_id=CITATIONS)
    app = api.create_app(run_dir.parent, TOKEN, [run_dir.name], publisher=publisher, jobs=jobs)
    return SimpleNamespace(client=TestClient(app, base_url='http://127.0.0.1'), jobs=jobs,
                           generated=generated, published=published, old_run=run_dir)


def preview(panel, action, request_id=ID, task_id=CITATIONS):
    return panel.client.post('/control/preview', headers=HEADERS,
        json={'action': action, 'task_id': task_id, 'request_id': request_id})


def execute(panel, plan, approved=True):
    return panel.client.post('/control/execute', headers=HEADERS, json={
        'action': plan['action'], 'task_id': plan['task_id'], 'request_id': plan['request_id'],
        'approved': approved, 'plan_sha256': plan['plan_sha256']})


def test_citation_job_runs_only_after_review_and_publishes_only_after_second_approval(panel):
    assert panel.client.get('/health').json()['task_id'] == CITATIONS
    catalog = preview(panel, 'catalog', None).json()
    tasks = {item['task_id']: item for item in catalog['tasks']}
    assert tasks[CITATIONS]['generation_configured'] is True
    assert tasks[BM25]['generation_configured'] is False
    plan = preview(panel, 'generate').json()
    assert plan['requires_approval'] and len(plan['plan']['allowed_files']) == 2
    assert plan['plan']['worker_allowed_files'] == [task.TARGET]
    assert plan['plan']['acceptance_test_count'] == 15
    assert plan['plan']['fixed_files_sha256'] == {task.MANIFEST['fixed_test_target']: task.MANIFEST['fixed_test_sha256']}
    assert execute(panel, plan, approved=False).status_code == 403
    assert panel.generated == [] and panel.jobs.used == 0
    result = execute(panel, plan)
    assert result.status_code == 200 and result.json()['result']['status'] == 'review_ready'
    assert panel.generated == [ID] and panel.published == [] and panel.jobs.used == 1
    report = preview(panel, 'report').json()['result']
    assert report['task_id'] == CITATIONS and report['comparison']['after'] == {key: True for key in task.PROBE_KEYS}
    assert '/dev/null' in report['diff'] and 'test_forced_fallback_retains_second_source' in report['diff']
    plan = preview(panel, 'publish').json()
    assert panel.published == [] and plan['plan']['model_invocations'] == 0
    assert execute(panel, plan).json()['result']['status'] == 'pr_ready'
    assert panel.generated == [ID] and panel.published == [ID]
    assert preview(panel, 'generate').json()['result']['status'] == 'pr_ready'


def test_legacy_combined_execution_and_wrong_task_identity_cannot_reach_citation_worker(panel):
    response = panel.client.post('/jobs', headers=HEADERS,
        json={'task_id': BM25, 'request_id': ID})
    assert response.status_code == 410 and panel.generated == []
    assert preview(panel, 'generate', task_id=BM25).json()['error_code'] == 'NEW_JOBS_NOT_CONFIGURED'
    assert preview(panel, 'report', panel.old_run.name, task_id=CITATIONS).status_code == 404
    assert preview(panel, 'report', panel.old_run.name, task_id=BM25).status_code == 200
    execute(panel, preview(panel, 'generate').json())
    assert preview(panel, 'status', task_id=BM25).status_code == 404
    assert panel.generated == [ID] and panel.published == []


def test_receipt_cannot_substitute_other_tests_or_target(panel):
    execute(panel, preview(panel, 'generate').json())
    record = panel.jobs.publisher(panel.jobs.paths(ID)[2])
    assert api.public_receipt(record, ID, CITATIONS)['fixed_files_sha256'] == record['fixed_files_sha256']
    for key, value in [('fixed_files_sha256', {}), ('allowed_files', [task.TARGET]), ('task_id', BM25)]:
        with pytest.raises(publish.PublicationError): api.public_receipt({**record, key: value}, ID, CITATIONS)
