"""n8n publication boundary: fixed run selection, credential separation and serialization."""

from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import threading
from types import SimpleNamespace
import uuid

from fastapi.testclient import TestClient
import pytest

from experiments.dev_loop import publication_api as api
from experiments.dev_loop.adapters import InfrastructureError
from experiments.dev_loop.publish import PublicationError

TOKEN = 'test-token-with-at-least-24-characters'
RUN_ID = 'a5739357-6da4-4118-be18-5c038306e0e9'
HEAD = 'a' * 40
ROOT = Path(__file__).resolve().parents[1]


def result():
    return {'request_id': RUN_ID, 'task_id': api.TASK_ID, 'repository': api.REPOSITORY,
            'base': 'main', 'base_sha': HEAD, 'head_sha': HEAD, 'branch': 'perf/bm25-tokenize-once',
            'allowed_files': [api.TARGET], 'candidate_sha256': 'b' * 64,
            'pull_request': 'https://github.com/jyenten/local_rag_api/pull/10',
            'draft': True, 'reused_existing_pr': True, 'published_to_github': True,
            'local_source_changed': False, 'merged': False, 'merge_allowed': False,
            'ci_status': 'not_checked', 'checker_image': 'sha256:' + 'c' * 64,
            'workspace': '/private/host/path', 'raw_logs': 'not-for-n8n',
            'verification': [{'host_detail': 'not-for-n8n'}]}


def client(tmp_path, publisher=None, registered=(RUN_ID,)):
    app = api.create_app(tmp_path, TOKEN, registered, publisher=publisher)
    return TestClient(app, base_url='http://127.0.0.1')


def post(c, path='/publications', body=None, headers=None):
    return c.post(path, json=body if body is not None else {'task_id': api.TASK_ID, 'run_id': RUN_ID},
                  headers={'X-Dev-Loop-Token': TOKEN, **(headers or {})})


def test_health_is_liveness_only_and_task_listing_requires_auth(tmp_path):
    c = client(tmp_path)
    assert c.get('/health').json() == {'status': 'ok', 'service': 'verified-publication', 'task_id': api.TASK_ID}
    assert c.get('/tasks').status_code == 401
    response = c.get('/tasks', headers={'X-Dev-Loop-Token': TOKEN})
    assert response.json()['tasks'] == [{'task_id': api.TASK_ID, 'allowed_run_ids': [RUN_ID],
                                       'operations': ['preview', 'publish'], 'merge_allowed': False}]
    assert c.get('/docs', headers={'X-Dev-Loop-Token': TOKEN}).status_code == 404


@pytest.mark.parametrize('token', ['', 'wrong-token', None])
def test_auth_is_checked_before_request_parsing_or_publisher(tmp_path, token):
    calls = []
    c = client(tmp_path, lambda path: calls.append(path) or result())
    response = c.post('/publications', content='not-json',
                      headers={'X-Dev-Loop-Token': token} if token is not None else {})
    assert response.status_code == 401 and calls == []
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('extra', [
    {'repo': 'some/other'}, {'command': 'execute something'}, {'run_dir': '../.env'},
    {'prompt': 'arbitrary task'}, {'token': 'not-an-api-field'}, {'publish': False},
])
def test_http_cannot_select_repo_path_command_prompt_or_credentials(tmp_path, extra):
    c = client(tmp_path, lambda path: pytest.fail('Invalid request must not reach publisher'))
    response = post(c, body={'task_id': api.TASK_ID, 'run_id': RUN_ID, **extra})
    assert response.status_code == 422 and list(tmp_path.iterdir()) == []


@pytest.mark.parametrize('body', [
    {'task_id': 'build-search-package', 'run_id': RUN_ID},
    {'task_id': api.TASK_ID, 'run_id': '../something'},
    {'task_id': api.TASK_ID}, {'run_id': RUN_ID},
])
def test_wrong_task_and_invalid_uuid_fail_validation(tmp_path, body):
    c = client(tmp_path, lambda path: pytest.fail('Invalid body'))
    assert post(c, body=body).status_code == 422


def test_only_host_registered_uuid_is_resolved_and_private_details_are_removed(tmp_path):
    calls = []
    c = client(tmp_path, lambda path: calls.append(path) or result())
    denied = post(c, body={'task_id': api.TASK_ID, 'run_id': str(uuid.uuid4())})
    assert denied.status_code == 404 and calls == []
    response = post(c)
    assert response.status_code == 200
    assert calls == [tmp_path / RUN_ID]
    receipt = response.json()
    assert receipt['pull_request'].endswith('/10') and receipt['ci_status'] == 'not_checked'
    assert receipt['merged'] is False and receipt['merge_allowed'] is False
    assert all(key not in receipt for key in ('workspace', 'raw_logs', 'verification'))
    assert 'not-for-n8n' not in response.text


def test_preview_uses_validated_plan_without_github_or_docker(tmp_path, monkeypatch):
    calls = []
    def load(path):
        calls.append(path)
        return SimpleNamespace(task=SimpleNamespace(task_id=api.TASK_ID),
                               plan=lambda: {'publish_requested': False, 'merge_allowed': False})
    monkeypatch.setattr(api, 'load_bundle', load)
    c = client(tmp_path, lambda path: pytest.fail('Preview must not publish'))
    response = post(c, path='/publications/preview')
    assert response.json() == {'publish_requested': False, 'merge_allowed': False}
    assert calls == [tmp_path / RUN_ID]


@pytest.mark.parametrize('error,status', [
    (FileNotFoundError('/private/location'), 404),
    (PublicationError('raw detail with host path or token'), 422),
    (InfrastructureError('raw infrastructure detail'), 503),
    (OSError('raw filesystem detail'), 500),
])
def test_errors_are_safe_for_n8n_and_failed_job_releases_lock(tmp_path, error, status):
    attempts = []
    def publisher(path):
        attempts.append(path)
        if len(attempts) == 1: raise error
        return result()
    c = client(tmp_path, publisher)
    first = post(c)
    assert first.status_code == status and 'raw' not in first.text and '/private' not in first.text
    assert post(c).status_code == 200


def test_concurrent_http_publication_is_rejected_without_duplicate_call(tmp_path):
    entered, release = threading.Event(), threading.Event()
    calls = []
    def publisher(path):
        calls.append(path)
        entered.set()
        assert release.wait(5)
        return result()
    c = client(tmp_path, publisher)
    with ThreadPoolExecutor(max_workers=1) as executor:
        first = executor.submit(post, c)
        try:
            assert entered.wait(5)
            assert post(c).status_code == 409
            assert len(calls) == 1
        finally:
            release.set()
        assert first.result().status_code == 200


@pytest.mark.parametrize('change', [
    {'merged': True}, {'merge_allowed': True}, {'repository': 'someone/else'},
    {'allowed_files': ['.env']}, {'local_source_changed': True},
    {'pull_request': 'https://untrusted.invalid/10'}, {'request_id': str(uuid.uuid4())},
])
def test_unexpected_publisher_receipt_is_not_reported_as_success(tmp_path, change):
    c = client(tmp_path, lambda path: {**result(), **change})
    assert post(c).status_code == 422


def test_origin_host_media_and_size_boundaries(tmp_path):
    c = client(tmp_path, lambda path: pytest.fail('Request must be rejected first'))
    assert post(c, headers={'Origin': 'https://untrusted.invalid'}).status_code == 403
    assert post(c, headers={'Host': 'untrusted.invalid'}).status_code == 400
    assert post(c, headers={'Content-Type': 'text/plain'}).status_code == 415
    assert post(c, body={'data': 'x' * 1024}).status_code == 413
    assert post(c, headers={'Transfer-Encoding': 'chunked'}).status_code == 411
    assert post(c, headers={'Content-Length': 'invalid'}).status_code == 411
    assert post(c, headers={'Content-Length': '9' * 6000}).status_code == 413
    assert post(c, body={'data': 'x' * 1024}, headers={'Content-Length': '1'}).status_code == 413


@pytest.mark.parametrize('runs', [[], [str(uuid.uuid4()) for _ in range(21)], ['../not-a-uuid']])
def test_server_requires_a_bounded_exact_uuid_registration(tmp_path, runs):
    with pytest.raises(ValueError): api.create_app(tmp_path, TOKEN, runs)


def test_cli_binds_only_loopback_and_does_not_enable_proxy_headers(tmp_path, monkeypatch):
    import uvicorn
    calls, checked = [], []
    monkeypatch.setenv('DEV_LOOP_TOKEN', TOKEN)
    monkeypatch.setattr(api, 'load_bundle', lambda path: checked.append(path))
    monkeypatch.setattr(uvicorn, 'run', lambda app, **kw: calls.append(kw))
    assert api.main(['--runs-root', str(tmp_path), '--allow-run', RUN_ID]) == 0
    assert checked == [tmp_path / RUN_ID]
    assert calls == [{'host': '127.0.0.1', 'port': 8766, 'proxy_headers': False, 'workers': 1,
                      'limit_concurrency': 8, 'timeout_keep_alive': 5}]
    with pytest.raises(SystemExit):
        api.main(['--runs-root', str(tmp_path), '--allow-run', RUN_ID, '--host', '0.0.0.0'])
    assert len(calls) == 1


def test_cli_refuses_missing_token_or_bad_saved_run_before_listening(tmp_path, monkeypatch):
    import uvicorn
    monkeypatch.setattr(uvicorn, 'run', lambda *a, **k: pytest.fail('Must not listen'))
    monkeypatch.delenv('DEV_LOOP_TOKEN', raising=False)
    with pytest.raises(SystemExit): api.main(['--runs-root', str(tmp_path), '--allow-run', RUN_ID])
    monkeypatch.setenv('DEV_LOOP_TOKEN', TOKEN)
    with pytest.raises(SystemExit): api.main(['--runs-root', str(tmp_path), '--allow-run', RUN_ID])


def test_n8n_workflow_is_manual_registered_run_selection_and_one_authenticated_request():
    flow = json.loads((ROOT / 'n8n-publication-workflow.json').read_text())
    assert flow['active'] is False
    assert flow['nodes'][0]['type'] == 'n8n-nodes-base.manualTrigger'
    select = next(node for node in flow['nodes'] if node['type'] == 'n8n-nodes-base.set')
    fields = {item['name']: item['value'] for item in select['parameters']['assignments']['assignments']}
    assert fields == {'task_id': api.TASK_ID, 'run_id': RUN_ID}
    nodes = [node for node in flow['nodes'] if node['type'] == 'n8n-nodes-base.httpRequest']
    assert len(nodes) == 1
    node = nodes[0]
    assert node['parameters']['url'] == 'http://host.docker.internal:8766/publications'
    assert node['retryOnFail'] is False and node['parameters']['options']['timeout'] == 900000
    assert node['parameters']['genericAuthType'] == 'httpHeaderAuth'
    assert '$execution.id' not in node['parameters']['jsonBody']
    assert 'credentials' not in node and flow['pinData'] == {}
    assert not any(n['type'] in ('n8n-nodes-base.executeCommand', 'n8n-nodes-base.code') for n in flow['nodes'])
