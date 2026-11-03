import json
import sys

import pytest

from experiments.dev_loop import batch
from experiments.dev_loop.__main__ import main
from experiments.dev_loop.adapters import DemoWorker, PytestChecker


@pytest.mark.parametrize("count", [0, 21])
def test_batch_limit_prevents_any_execution(tmp_path, count):
    with pytest.raises(ValueError):
        batch.run_batch(count, tmp_path / "report", DemoWorker(), PytestChecker())
    assert list(tmp_path.iterdir()) == []


def test_report_is_based_on_measured_runs_and_excludes_raw_logs(tmp_path):
    output = tmp_path / "report"
    report = batch.run_batch(2, output, DemoWorker(), PytestChecker())
    assert report["completed_cycles"] == 2
    assert report["total_attempts"] == 4
    assert report["total_repairs"] == 2
    assert report["model_calls"] == 0
    assert all(row["duration_s"] > 0 for row in report["rows"])
    assert all(row["verification_returncodes"] == [1, 0] for row in report["rows"])
    public = json.loads((output / "batch.json").read_text(encoding="utf-8"))
    assert "workspace" not in json.dumps(public)
    assert "feedback" not in json.dumps(public)
    destination = batch.render_report(report, output)
    assert destination.is_file() and (output / "cycles.png").is_file()
    assert "data:image/png;base64," in destination.read_text(encoding="utf-8")


def test_critical_failure_stops_batch_instead_of_spending_remaining_budget(monkeypatch, tmp_path):
    calls = []

    def fake_run(request_id, task_id, runs_dir, worker, checker):
        calls.append(request_id)
        return {"request_id": request_id, "backend": "demo", "status": "infrastructure_error",
                "attempts": 1, "duration_s": .5, "trace": []}

    monkeypatch.setattr(batch, "run_job", fake_run)
    report = batch.run_batch(20, tmp_path / "report", DemoWorker(), PytestChecker())
    assert report["completed_cycles"] == 1
    assert report["stopped_early"] is True
    assert len(calls) == 1


def test_non_loopback_binding_is_not_accidentally_enabled(monkeypatch):
    monkeypatch.setenv("DEV_LOOP_TOKEN", "test-token-at-least-24-characters")
    monkeypatch.setattr(sys, "argv", ["dev-loop", "--serve", "--host", "0.0.0.0"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2


def test_cli_rejects_more_than_twenty_cycles(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["dev-loop", "--cycles", "21"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
