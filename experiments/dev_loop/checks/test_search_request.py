"""Independent fixed contract for the build-search-request task."""

import os
import runpy
from pathlib import Path

import pytest

if "DEV_LOOP_WORKSPACE" not in os.environ:
    pytest.skip("Only collected by the isolated dev-loop runner", allow_module_level=True)

new_requirement = pytest.mark.skipif(os.environ.get("DEV_LOOP_PHASE") == "baseline",
                                    reason="New requirement")


@pytest.fixture
def build():
    module = runpy.run_path(str(Path(os.environ["DEV_LOOP_WORKSPACE"]) / "question.py"))
    return module["build_search_request"]


def test_existing_valid_request(build):
    assert build("What is OSPF?", 5) == {"query": "What is OSPF?", "top_k": 5}


def test_existing_empty_query(build):
    with pytest.raises(ValueError):
        build("")


@new_requirement
def test_default_top_k(build):
    assert build("OSPF") == {"query": "OSPF", "top_k": 5}


@new_requirement
def test_keyword_arguments(build):
    assert build(query="  OSPF  ", top_k=2) == {"query": "OSPF", "top_k": 2}


@new_requirement
@pytest.mark.parametrize("value", ["  OSPF   routes  ", "\tOSPF\n\t routes\r\n", "\u00a0OSPF\u2003routes\u00a0"])
def test_collapse_whitespace(build, value):
    assert build(value, 7) == {"query": "OSPF routes", "top_k": 7}


@new_requirement
def test_preserve_case_and_punctuation(build):
    assert build("  OSPF: Area 0?  ")["query"] == "OSPF: Area 0?"


@new_requirement
@pytest.mark.parametrize("value", ["   ", "\t\n", "\u00a0\u2003"])
def test_reject_whitespace_query(build, value):
    with pytest.raises(ValueError):
        build(value)


@new_requirement
@pytest.mark.parametrize("value", [None, 123, False, ["OSPF"]])
def test_reject_non_string_query(build, value):
    with pytest.raises(TypeError):
        build(value)


@new_requirement
@pytest.mark.parametrize("top_k", [1, 20])
def test_accept_top_k_boundaries(build, top_k):
    result = build("OSPF", top_k)
    assert result == {"query": "OSPF", "top_k": top_k}
    assert type(result["top_k"]) is int


@new_requirement
@pytest.mark.parametrize("top_k", [True, False, 1.5, 5.0, "5", None])
def test_reject_non_integer_top_k(build, top_k):
    with pytest.raises(TypeError):
        build("OSPF", top_k)


@new_requirement
@pytest.mark.parametrize("top_k", [0, -1, 21, 1000])
def test_reject_out_of_range_top_k(build, top_k):
    with pytest.raises(ValueError):
        build("OSPF", top_k)


@new_requirement
def test_fresh_mapping(build):
    first = build("OSPF")
    second = build("OSPF")
    assert type(first) is type(second) is dict and first is not second
    first["top_k"] = 19
    assert second == {"query": "OSPF", "top_k": 5}
