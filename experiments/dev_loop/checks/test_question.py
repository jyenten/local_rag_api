"""Controller-owned acceptance criteria, outside the worker's workspace."""

import os
import runpy
from pathlib import Path

import pytest

if "DEV_LOOP_WORKSPACE" not in os.environ:
    pytest.skip("Only collected by the isolated dev-loop runner", allow_module_level=True)


@pytest.fixture
def normalize():
    module = runpy.run_path(str(Path(os.environ["DEV_LOOP_WORKSPACE"]) / "question.py"))
    return module["normalize_question"]


def test_existing_valid_question(normalize):
    assert normalize("What is OSPF?") == "What is OSPF?"


def test_existing_empty_question(normalize):
    with pytest.raises(ValueError):
        normalize("")


@pytest.mark.skipif(os.environ.get("DEV_LOOP_PHASE") == "baseline", reason="New requirement")
@pytest.mark.parametrize("value", ["   ", "\t", "\n \t"])
def test_reject_whitespace(normalize, value):
    with pytest.raises(ValueError):
        normalize(value)


@pytest.mark.skipif(os.environ.get("DEV_LOOP_PHASE") == "baseline", reason="New requirement")
def test_strip_outer_whitespace(normalize):
    assert normalize("  What is OSPF?\n") == "What is OSPF?"
