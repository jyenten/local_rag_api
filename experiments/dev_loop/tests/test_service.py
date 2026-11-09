"""Stable profile lifecycle and launcher behavior, without model/Docker/GitHub calls."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from types import SimpleNamespace

import pytest

from experiments.dev_loop import service
from experiments.dev_loop.adapters import InfrastructureError
from experiments.dev_loop.tests.test_publish import run_dir


@pytest.fixture
def configured(tmp_path, run_dir):
    config = tmp_path / 'profile with spaces' / 'service.json'
    assert service.main(['init', '--config', str(config), '--runs-root', str(run_dir.parent),
                         '--allow-run', run_dir.name]) == 0
    return SimpleNamespace(config=config, run_dir=run_dir)


def test_profile_preserves_non_secret_paths_and_check_never_claims_runtime_readiness(configured, monkeypatch, capsys):
    monkeypatch.setenv('DEV_LOOP_TOKEN', 'host-secret-must-not-be-saved')
    profile = service.read_profile(configured.config)
    assert profile['python_executable'] == service.absolute(sys.executable)
    assert profile['runs_root'] == str(configured.run_dir.parent)
    assert profile['allowed_run_ids'] == [configured.run_dir.name]
    assert set(profile) == service.FIELDS
    assert 'host-secret' not in configured.config.read_text()
    assert service.main(['check', '--config', str(configured.config)]) == 0
    output = capsys.readouterr().out
    assert '"configuration_valid": true' in output and '"runtime_readiness": "not_checked"' in output
    assert 'host-secret' not in output


def test_start_reuses_profile_and_existing_token_without_install_update_or_model_calls(configured, monkeypatch):
    from experiments.dev_loop import publication_api
    calls = []
    monkeypatch.setenv('DEV_LOOP_TOKEN', 'test-existing-token-at-least-24-characters')
    monkeypatch.setattr(service.getpass, 'getpass', lambda *a: pytest.fail('Existing token must not prompt'))
    monkeypatch.setattr(publication_api, 'main', lambda args: calls.append((args, os.environ['DEV_LOOP_TOKEN'])) or 0)
    original = configured.config.read_bytes()
    assert service.main(['start', '--config', str(configured.config)]) == 0
    args, token = calls[0]
    assert token == 'test-existing-token-at-least-24-characters'
    assert args == ['--runs-root', str(configured.run_dir.parent), '--port', '8766',
                    '--allow-run', configured.run_dir.name]
    assert configured.config.read_bytes() == original


def test_interactive_start_prompts_once_and_does_not_leave_token_in_profile_or_environment(configured, monkeypatch):
    from experiments.dev_loop import publication_api
    monkeypatch.delenv('DEV_LOOP_TOKEN', raising=False)
    monkeypatch.setattr(service.sys, 'stdin', SimpleNamespace(isatty=lambda: True))
    entered, observed = [], []
    def prompt(message):
        entered.append(message)
        return 'test-interactive-token-at-least-24-characters'
    monkeypatch.setattr(service.getpass, 'getpass', prompt)
    monkeypatch.setattr(publication_api, 'main', lambda args: observed.append(os.environ['DEV_LOOP_TOKEN']) or 0)
    assert service.main(['start', '--config', str(configured.config)]) == 0
    assert len(entered) == 1 and observed == ['test-interactive-token-at-least-24-characters']
    assert 'DEV_LOOP_TOKEN' not in os.environ
    assert 'test-interactive' not in configured.config.read_text()


def test_noninteractive_missing_token_and_short_token_stop_before_service(configured, monkeypatch):
    from experiments.dev_loop import publication_api
    monkeypatch.setattr(publication_api, 'main', lambda args: pytest.fail('Must not start'))
    monkeypatch.delenv('DEV_LOOP_TOKEN', raising=False)
    monkeypatch.setattr(service.sys, 'stdin', SimpleNamespace(isatty=lambda: False))
    with pytest.raises(SystemExit): service.main(['start', '--config', str(configured.config)])
    monkeypatch.setenv('DEV_LOOP_TOKEN', 'short')
    with pytest.raises(SystemExit): service.main(['start', '--config', str(configured.config)])


def test_explicit_replacement_keeps_unrelated_files_safe(configured):
    before = configured.config.read_bytes()
    args = ['init', '--config', str(configured.config), '--runs-root', str(configured.run_dir.parent),
            '--allow-run', configured.run_dir.name, '--port', '8767']
    with pytest.raises(SystemExit): service.main(args)
    assert configured.config.read_bytes() == before
    assert service.main(args + ['--replace']) == 0
    assert service.read_profile(configured.config)['port'] == 8767
    configured.config.write_text('not a service profile')
    with pytest.raises(SystemExit): service.main(args + ['--replace'])
    assert configured.config.read_text() == 'not a service profile'


@pytest.mark.parametrize('change', [
    {'DEV_LOOP_TOKEN': 'not-allowed'}, {'host': '0.0.0.0'}, {'command': 'arbitrary'},
    {'max_new_jobs': True}, {'max_new_jobs': 21}, {'max_new_jobs': 2},
    {'runs_root': '../relative'}, {'port': 80}, {'schema_version': True},
    {'allowed_run_ids': ['../path']}, {'python_executable': 'relative-python'},
])
def test_invalid_or_secret_config_fields_are_rejected_before_start(configured, change):
    data = json.loads(configured.config.read_text())
    data.update(change)
    configured.config.write_text(json.dumps(data))
    with pytest.raises((ValueError, TypeError)): service.read_profile(configured.config)


def test_real_job_source_is_explicit_checked_and_limits_are_preserved(configured, tmp_path, monkeypatch):
    from experiments.dev_loop.real_bm25 import __main__ as real
    source, jobs = tmp_path / 'reviewed source', tmp_path / 'jobs'
    calls = []
    monkeypatch.setattr(real, 'read_source', lambda path: calls.append(path) or ('trusted test source', 'a' * 40))
    args = ['init', '--config', str(configured.config), '--replace',
            '--runs-root', str(configured.run_dir.parent), '--allow-run', configured.run_dir.name,
            '--source-repo', str(source), '--jobs-root', str(jobs)]
    assert service.main(args) == 0
    profile = service.read_profile(configured.config)
    assert calls == [source]
    assert profile['max_new_jobs'] == 1
    assert service.service_arguments(profile)[-6:] == ['--source-repo', str(source), '--jobs-root', str(jobs),
                                                     '--max-new-jobs', '1']


def test_missing_saved_run_or_source_never_writes_a_new_profile(tmp_path):
    config = tmp_path / 'not-created.json'
    with pytest.raises(SystemExit):
        service.main(['init', '--config', str(config), '--runs-root', str(tmp_path),
                      '--allow-run', '00000000-0000-4000-8000-000000000001'])
    assert not config.exists()


def test_symlink_profile_is_not_replaced(configured, tmp_path):
    link = tmp_path / 'linked.json'
    try: link.symlink_to(configured.config)
    except OSError: pytest.skip('Symlinks unavailable')
    with pytest.raises(InfrastructureError): service.read_profile(link)


def test_powershell_launcher_handles_profile_path_spaces_without_printing_secrets(configured):
    executable = shutil.which('pwsh') or shutil.which('powershell')
    if not executable:
        pytest.skip('PowerShell launcher is exercised by Windows CI')
    script = Path(service.__file__).with_name('Start-DevLoop.ps1')
    result = subprocess.run([executable, '-NoProfile', '-NonInteractive', '-File', str(script),
                             '-Action', 'check', '-ConfigPath', str(configured.config)],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    assert '"configuration_valid": true' in result.stdout
    assert '"runtime_readiness": "not_checked"' in result.stdout


def test_select_reviewed_task_preserves_paths_limits_and_rejects_unavailable_source(configured, tmp_path, monkeypatch):
    from experiments.dev_loop.citations import task
    from experiments.dev_loop.real_bm25 import __main__ as bm25
    from experiments.dev_loop.registered_tasks import CITATIONS
    monkeypatch.setattr(bm25, 'read_source', lambda path: ('public original', 'a' * 40))
    monkeypatch.setattr(task, 'read_source', lambda path: ('public retrieval', 'a' * 40))
    assert service.main(['init', '--config', str(configured.config), '--replace',
        '--runs-root', str(configured.run_dir.parent), '--allow-run', configured.run_dir.name,
        '--source-repo', str(tmp_path / 'source'), '--jobs-root', str(tmp_path / 'jobs')]) == 0
    before = service.read_profile(configured.config)
    assert service.main(['select-task', CITATIONS, '--config', str(configured.config)]) == 0
    after = service.read_profile(configured.config)
    assert after == {**before, 'schema_version': 2, 'task_id': CITATIONS}
    assert service.service_arguments(after)[-2:] == ['--task', CITATIONS]
    snapshot = configured.config.read_bytes()
    def fail(path): raise InfrastructureError('Source changed')
    monkeypatch.setattr(task, 'read_source', fail)
    with pytest.raises(SystemExit): service.main(['select-task', CITATIONS, '--config', str(configured.config)])
    assert configured.config.read_bytes() == snapshot


def test_powershell_launcher_accepts_v2_profile_without_running_a_model(configured, tmp_path):
    executable = shutil.which('pwsh') or shutil.which('powershell')
    if not executable:
        pytest.skip('PowerShell v2 launcher is exercised by Windows CI')
    profile = service.read_profile(configured.config)
    profile.update(schema_version=2, task_id='bm25-tokenize-once')
    configured.config.write_text(json.dumps(profile), encoding='utf-8')
    script = Path(service.__file__).with_name('Start-DevLoop.ps1')
    result = subprocess.run([executable, '-NoProfile', '-NonInteractive', '-File', str(script),
        '-Action', 'check', '-ConfigPath', str(configured.config)], capture_output=True, text=True, timeout=30)
    assert result.returncode == 0 and '"configuration_valid": true' in result.stdout, result.stderr
