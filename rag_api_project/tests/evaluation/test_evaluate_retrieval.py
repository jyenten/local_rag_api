import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock, call

import pytest

from evaluation.history import load_history
from evaluation.models import EvaluationQuestion, GoldEvidence, LatencyMetrics


@pytest.fixture
def cli(monkeypatch):
    # Stub imports before loading the CLI: no model dependencies or settings access.
    for name, attribute in (
        ("app.config", "get_settings"),
        ("app.retrieval", "Retriever"),
        ("app.retrievers.vector", "VectorRetriever"),
        ("app.retrievers.bm25", "BM25Retriever"),
    ):
        module = ModuleType(name)
        setattr(module, attribute, Mock())
        monkeypatch.setitem(sys.modules, name, module)
    script = Path(__file__).resolve().parents[2] / "scripts" / "evaluate_retrieval.py"
    spec = importlib.util.spec_from_file_location("latency_cli_under_test", script)
    cli = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cli)
    return cli


@pytest.mark.parametrize("strategy", ["legacy", "vector","bm25"])
@pytest.mark.parametrize("dataset", ["dev", "random"])
def test_cli_evaluates_and_persists_latency(tmp_path, monkeypatch, capsys, strategy, dataset, cli):
    script = Path(cli.__file__)
    monkeypatch.setattr(sys, "argv", [str(script), "--retriever", strategy, "--dataset", dataset])
    assert set(cli.DATASET_PATHS) == {"dev", "random"}
    original_history = cli.HISTORY_PATHS[(strategy, dataset)]
    suffixes = {
        "legacy": "",
        "vector": "_vector",
        "bm25": "_bm25",
    }

    expected_name = f"{dataset}{suffixes[strategy]}_runs.jsonl"
    assert original_history == Path("eval/results") / expected_name
    path = tmp_path / expected_name
    monkeypatch.setitem(cli.HISTORY_PATHS, (strategy, dataset), path)
    question = EvaluationQuestion(
        "fake_001", "topic", "question", (GoldEvidence("manual.pdf", (1,), ("evidence",)),)
    )
    loader = Mock(return_value=[question, question])
    monkeypatch.setattr(cli, "load_dataset", loader)
    monkeypatch.setattr(cli, "calculate_dataset_hash", Mock(return_value="fake-hash"))
    settings = SimpleNamespace(collection_name="fake", embedding_model_name="fake", retrieval_results=8)
    monkeypatch.setattr(cli, "get_settings", lambda: settings)
    fake = Mock()
    fake.search.return_value = (["evidence"], [0.1], [{"source": "manual.pdf", "page": 1}])
    constructor_names = {
        "legacy": "LegacyRetriever",
        "vector": "VectorRetriever",
        "bm25": "BM25Retriever",
    }

    constructor = getattr(
        cli,
        constructor_names[strategy]
    )
    constructor.return_value = fake
    probe = Mock(side_effect=["fake-commit\n", ""])
    monkeypatch.setattr(cli.subprocess, "check_output", probe)
    ticks = iter([0, 0.001, 1, 1.003])
    monkeypatch.setattr("evaluation.latency.perf_counter", lambda: next(ticks))

    cli.main()

    constructor.assert_called_once_with(settings)
    loader.assert_called_once_with(cli.DATASET_PATHS[dataset])
    assert fake.search.call_count == 2
    run, = load_history(path)
    assert isinstance(run.latency, LatencyMetrics)
    assert run.latency.mean_ms == pytest.approx(2)
    assert run.latency.p50_ms == pytest.approx(2)
    assert run.latency.p95_ms == pytest.approx(3)
    assert run.metrics.mrr == 1
    assert run.metrics.hit_at_1 == 1
    assert run.question_count == 2
    assert run.dataset == dataset
    assert run.git_commit == "fake-commit"
    assert run.git_dirty is False
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert raw["latency"]["mean_ms"] == pytest.approx(2)
    output = capsys.readouterr().out
    for label, value in [("MEAN", "2.00"), ("P50", "2.00"), ("P95", "3.00")]:
        assert f"LATENCY {label}: {value} ms" in output


@pytest.mark.parametrize("status, dirty", [("", False), (" M scripts/evaluate_retrieval.py\n", True)])
def test_git_probes_use_script_repository_from_other_cwd(cli, tmp_path, monkeypatch, status, dirty):
    monkeypatch.chdir(tmp_path)
    probe = Mock(side_effect=["abc123\n", status])
    monkeypatch.setattr(cli.subprocess, "check_output", probe)
    assert cli.get_git_commit() == "abc123"
    assert cli.get_git_dirty() is dirty
    expected_cwd = Path(cli.__file__).resolve().parent.parent
    assert probe.call_args_list == [
        call(["git", "rev-parse", "HEAD"], text=True, cwd=expected_cwd),
        call(["git", "status", "--porcelain"], text=True, cwd=expected_cwd),
    ]


@pytest.mark.parametrize("helper", ["get_git_commit", "get_git_dirty"])
@pytest.mark.parametrize("error", [
    subprocess.CalledProcessError(128, ["git"]),
    FileNotFoundError("Git executable missing"),
    subprocess.TimeoutExpired(["git"], 1),
])
def test_git_probe_failures_are_explicit(cli, monkeypatch, helper, error):
    monkeypatch.setattr(cli.subprocess, "check_output", Mock(side_effect=error))
    with pytest.raises(RuntimeError, match="Unable to determine Git") as caught:
        getattr(cli, helper)()
    assert caught.value.__cause__ is error


@pytest.mark.parametrize("failure_stage", ["commit", "status"])
@pytest.mark.parametrize("error", [
    subprocess.CalledProcessError(128, ["git"]),
    FileNotFoundError("Git executable missing"),
])
def test_failed_provenance_does_not_append_history(cli, monkeypatch, failure_stage, error):
    monkeypatch.setattr(sys, "argv", [cli.__file__])
    responses = [error] if failure_stage == "commit" else ["abc123\n", error]
    monkeypatch.setattr(cli.subprocess, "check_output", Mock(side_effect=responses))
    append = Mock()
    loader = Mock()
    evaluate = Mock()
    monkeypatch.setattr(cli, "append_run", append)
    monkeypatch.setattr(cli, "load_dataset", loader)
    monkeypatch.setattr(cli, "evaluate_dataset", evaluate)
    with pytest.raises(RuntimeError, match="Unable to determine Git"):
        cli.main()
    append.assert_not_called()
    loader.assert_not_called()
    evaluate.assert_not_called()


def test_empty_commit_does_not_append_history(cli, monkeypatch):
    monkeypatch.setattr(sys, "argv", [cli.__file__])
    monkeypatch.setattr(cli.subprocess, "check_output", Mock(return_value="\n"))
    append = Mock()
    monkeypatch.setattr(cli, "append_run", append)
    with pytest.raises(RuntimeError, match="empty output"):
        cli.main()
    append.assert_not_called()
