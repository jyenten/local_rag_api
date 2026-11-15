"""One approved cycle through the HTTP controller; model/GitHub are explicit stand-ins."""

import json
import os
import uuid

import pytest

from experiments.dev_loop.adapters import InfrastructureError
from experiments.dev_loop import real_jobs
from experiments.dev_loop import publish
from experiments.dev_loop.tests.test_citation_control import panel, preview, execute, ID, HEADERS
from experiments.dev_loop.tests.test_citations import citation_run, task, CitationGitHub, ORIGINAL, CANDIDATE
from experiments.dev_loop.tests.test_publish import run_dir


def test_one_approval_generates_checks_and_publishes_with_report(panel):
    plan = preview(panel, 'autonomous').json()
    assert plan['requires_approval'] is True
    assert plan['plan']['publication'] == 'automatic_draft_after_acceptance'
    assert plan['plan']['draft'] is True and plan['plan']['merge_allowed'] is False
    assert plan['plan']['max_worker_attempts'] == 3 and plan['plan']['generation_required'] is True
    assert plan['plan']['acceptance_test_count'] == 15
    assert plan['plan']['worker_timeout_s'] == task.WORKER_TIMEOUT_S == 180
    assert plan['plan']['worker_allowed_files'] == [task.TARGET]
    assert panel.generated == [] and panel.published == [] and panel.jobs.used == 0
    response = execute(panel, plan)
    assert response.status_code == 200
    result = response.json()
    assert result['result']['status'] == 'pr_ready'
    assert result['result']['publication']['draft'] is True
    assert result['result']['publication']['ci_status'] == 'not_checked'
    assert result['report']['comparison']['after'] == {key: True for key in task.PROBE_KEYS}
    assert 'test_forced_fallback_retains_second_source' in result['report']['diff']
    assert not any(secret in response.text for secret in (str(panel.jobs.root), HEADERS['X-Dev-Loop-Token']))
    assert panel.generated == [ID] and panel.published == [ID] and panel.jobs.used == 1
    # Repeating the same operation, including after a process restart, is read-only.
    panel.jobs.used = 0
    assert preview(panel, 'autonomous').json()['result']['status'] == 'pr_ready'
    assert execute(panel, plan).status_code == 409
    assert panel.generated == [ID] and panel.published == [ID]


def test_generate_approval_cannot_be_reused_to_authorize_automatic_publication(panel):
    plan = preview(panel, 'generate').json()
    response = panel.client.post('/control/execute', headers=HEADERS, json={
        'action': 'autonomous', 'task_id': plan['task_id'], 'request_id': ID,
        'approved': True, 'plan_sha256': plan['plan_sha256']})
    assert response.status_code == 409
    assert execute(panel, preview(panel, 'autonomous').json(), approved=False).status_code == 403
    assert panel.generated == [] and panel.published == [] and panel.jobs.used == 0


@pytest.mark.parametrize('status', ['attempt_limit', 'baseline_failed', 'infrastructure_error'])
def test_failed_generation_stops_cycle_without_publication_or_automatic_new_id(panel, status):
    original = panel.jobs.generator
    def failed(*args, **kwargs):
        report, directory = original(*args, **kwargs)
        report['status'] = status
        (directory / 'result.json').write_text(json.dumps(report), encoding='utf-8')
        return report, directory
    panel.jobs.generator = failed
    result = execute(panel, preview(panel, 'autonomous').json()).json()
    assert result['status'] == 'failed'
    assert result['result']['status'] == 'generation_failed' and 'report' not in result
    assert preview(panel, 'autonomous').json()['result']['status'] == 'generation_failed'
    assert preview(panel, 'autonomous', str(uuid.uuid4())).json()['error_code'] == 'NEW_JOB_ALLOWANCE_CONSUMED'
    assert panel.generated == [ID] and panel.published == []


def test_publication_failure_keeps_candidate_and_retry_never_calls_model(panel):
    calls = []
    original = panel.jobs.publisher
    def failed(directory):
        calls.append(directory.name)
        raise InfrastructureError('private publication diagnostics')
    panel.jobs.publisher = failed
    result = execute(panel, preview(panel, 'autonomous').json())
    assert result.json()['status'] == 'blocked'
    assert result.json()['result']['status'] == 'publication_blocked'
    assert 'private publication' not in result.text
    retry = preview(panel, 'autonomous').json()
    assert retry['plan']['max_worker_attempts'] == 0
    assert retry['plan']['generation_required'] is False
    assert retry['plan']['candidate_sha256'] == retry['result']['candidate_sha256']
    panel.jobs.publisher = original
    assert execute(panel, retry).json()['result']['status'] == 'pr_ready'
    assert panel.generated == [ID] and panel.published == [ID] and calls == [ID]


def test_existing_reviewed_generation_can_finish_without_spending_another_job(panel):
    assert execute(panel, preview(panel, 'generate').json()).json()['result']['status'] == 'review_ready'
    plan = preview(panel, 'autonomous').json()
    assert plan['plan']['cached_generation'] is True and plan['plan']['generation_required'] is False
    assert plan['plan']['new_jobs_remaining'] == 0
    assert execute(panel, plan).json()['result']['status'] == 'pr_ready'
    assert panel.generated == [ID] and panel.published == [ID] and panel.jobs.used == 1


def test_remote_drift_and_interrupted_job_stop_before_automatic_generation(panel):
    plan = preview(panel, 'autonomous').json()
    def changed(): raise InfrastructureError('private remote details')
    panel.jobs.preflight = changed
    assert execute(panel, plan).status_code == 409
    assert preview(panel, 'autonomous').json()['error_code'] == 'SOURCE_OR_REMOTE_PREFLIGHT_BLOCKED'
    _, directory, _ = panel.jobs.paths(ID)
    directory.mkdir(parents=True)
    real_jobs.write_json(directory / 'request.json', panel.jobs.identity(ID))
    real_jobs.write_json(directory / 'state.json', {'status': 'generating'})
    assert preview(panel, 'autonomous').json()['error_code'] == 'JOB_ACTIVE_OR_INTERRUPTED'
    assert panel.generated == [] and panel.published == [] and panel.jobs.used == 0


@pytest.mark.skipif(os.environ.get('DEV_LOOP_CITATION_DOCKER_TESTS') != '1',
                    reason='Opt-in full cycle with real offline Docker; scripted worker and fake GitHub')
def test_docker_autonomous_cycle_repairs_and_rechecks_before_draft_handoff(panel, monkeypatch):
    """No live model/GitHub credentials: exercise real HTTP, graph, Docker and publisher."""
    attempts = []
    class ScriptedWorker:
        name = 'codex-real-citations-docker'
        image_id = 'sha256:' + 'f' * 64
        def __init__(self, original):
            assert original == ORIGINAL
            self.attempt_records = []
        def implement(self, workspace, attempt, feedback):
            attempts.append(attempt)
            if attempt == 2:
                assert 'failed' in feedback
            source = ORIGINAL if attempt == 1 else CANDIDATE
            (workspace / 'question.py').write_text(source, encoding='utf-8')
            self.attempt_records.append({'attempt': attempt, 'usage': None})
            return 'Scripted reference for integration test; no model call.'
    monkeypatch.setattr(task, 'CitationWorker', ScriptedWorker)
    panel.jobs.generator = task.run
    github = CitationGitHub()
    panel.jobs.publisher = lambda directory: publish.publish(directory, github=github)
    response = execute(panel, preview(panel, 'autonomous').json())
    assert response.status_code == 200, response.text
    result = response.json()
    assert result['result']['status'] == 'pr_ready', result
    assert result['result']['attempts'] == 2 and attempts == [1, 2]
    assert result['result']['model_usage_measured'] is False
    assert result['report']['comparison'] == {
        'before': {key: False for key in task.PROBE_KEYS},
        'after': {key: True for key in task.PROBE_KEYS}}
    directory = panel.jobs.paths(ID)[2]
    record = json.loads((directory / 'publication.json').read_text(encoding='utf-8'))
    assert [phase['phase'] for phase in record['verification']] == ['baseline', 'acceptance']
    assert len(github.refs) == 1
    assert {entry['path'] for entry in github.tree_files} == {task.TARGET, *task.fixed_files()}
    assert all(method in {'GET', 'POST'} and '/merge' not in path for method, path, _ in github.calls)
    assert preview(panel, 'autonomous').json()['result']['status'] == 'pr_ready'
    assert attempts == [1, 2] and len(github.refs) == 1
