"""Builder contract plus direct validator and cross-module integration checks."""

import os
import importlib.util
import sys
from pathlib import Path

import pytest

if "DEV_LOOP_WORKSPACE" not in os.environ:
    pytest.skip("Only collected by the isolated dev-loop runner", allow_module_level=True)

new_requirement = pytest.mark.skipif(os.environ.get("DEV_LOOP_PHASE") == "baseline",
                                    reason="New requirement")


@pytest.fixture
def modules(monkeypatch):
    workspace = Path(os.environ["DEV_LOOP_WORKSPACE"])
    loaded = []
    for name in ("validation", "search_request"):
        spec = importlib.util.spec_from_file_location(name, workspace / f"{name}.py")
        module = importlib.util.module_from_spec(spec)
        monkeypatch.setitem(sys.modules, name, module)
        spec.loader.exec_module(module)
        loaded.append(module)
    return tuple(loaded)


@pytest.fixture
def build(modules):
    return modules[1].build_search_request


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


@new_requirement
@pytest.mark.parametrize("value", ["  A\tB  ", "\u2003A\u00a0B "])
def test_normalize_query_direct(modules, value):
    assert modules[0].normalize_query(value) == "A B"


@new_requirement
@pytest.mark.parametrize("value", [None, 42, False, ["OSPF"]])
def test_normalize_query_type_direct(modules, value):
    with pytest.raises(TypeError):
        modules[0].normalize_query(value)


@new_requirement
@pytest.mark.parametrize("value", ["", " ", "\u00a0\u2003"])
def test_normalize_query_empty_direct(modules, value):
    with pytest.raises(ValueError):
        modules[0].normalize_query(value)


@new_requirement
@pytest.mark.parametrize("value", [1, 20])
def test_validate_top_k_direct(modules, value):
    assert modules[0].validate_top_k(value) == value


@new_requirement
@pytest.mark.parametrize("value", [True, False, 1.5, 5.0, "5", None])
def test_validate_top_k_type_direct(modules, value):
    with pytest.raises(TypeError):
        modules[0].validate_top_k(value)


@new_requirement
@pytest.mark.parametrize("value", [0, -1, 21, 1000])
def test_validate_top_k_range_direct(modules, value):
    with pytest.raises(ValueError):
        modules[0].validate_top_k(value)


@new_requirement
def test_builder_delegates_and_uses_validator_returns(modules, monkeypatch):
    validation, request = modules
    calls = []
    def normalize(query):
        calls.append(("query", query))
        return "NORMALIZED"
    def limit(top_k):
        calls.append(("top_k", top_k))
        return 13
    monkeypatch.setattr(validation, "normalize_query", normalize)
    monkeypatch.setattr(validation, "validate_top_k", limit)
    assert request.build_search_request(" raw ", 7) == {"query": "NORMALIZED", "top_k": 13}
    assert calls == [("query", " raw "), ("top_k", 7)]


@new_requirement
@pytest.mark.parametrize("name,error_type", [("normalize_query", ValueError), ("validate_top_k", TypeError)])
def test_builder_propagates_validator_exceptions(modules, monkeypatch, name, error_type):
    validation, request = modules
    marker = error_type("controller-owned test sentinel")
    def fail(value):
        raise marker
    monkeypatch.setattr(validation, name, fail)
    with pytest.raises(error_type) as caught:
        request.build_search_request("OSPF", 5)
    assert caught.value is marker
