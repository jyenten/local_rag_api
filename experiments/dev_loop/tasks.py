"""Controller-owned allowlist. Requests cannot supply test paths or instructions."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    function_name: str
    instructions: str
    fixture: str
    checks: str
    test_count: int
    baseline_skips: int
    checker_image: str
    artifacts: tuple[str, ...] = ("question.py",)
    codex_image: str = "local-rag-codex:0.162.1"
    response_schema: str = "response.schema.json"


NORMALIZE = TaskSpec(
    "normalize-question", "normalize_question",
    "Define only normalize_question(value: str) -> str. Strip surrounding whitespace, "
    "raise ValueError if the stripped result is empty, otherwise return the stripped text. ",
    "question.py", "test_question.py", 6, 4, "local-rag-dev-loop:1",
)
SEARCH_REQUEST = TaskSpec(
    "build-search-request", "build_search_request",
    "Define only build_search_request(query: str, top_k: int = 5) -> dict. "
    "Require query to be a string (otherwise raise TypeError). Collapse every sequence "
    "of whitespace, including Unicode whitespace, to one ASCII space and remove outer "
    "whitespace. Preserve letter case and punctuation. Reject an empty normalized query "
    "with ValueError. Require top_k to have exactly type int (reject bool, float, str, "
    "None with TypeError), and require 1 <= top_k <= 20 (otherwise raise ValueError). "
    "Return a fresh dict with exactly keys query (normalized text) and top_k (unchanged "
    "integer). Do not coerce or clamp invalid inputs. No imports or top-level execution. ",
    "search_request.py", "test_search_request.py", 28, 26, "local-rag-dev-loop:2",
)
SEARCH_PACKAGE = TaskSpec(
    "build-search-package", "build_search_request",
    "Return both complete modules validation.py and search_request.py. "
    "validation.py must define exactly normalize_query(query: str) -> str and "
    "validate_top_k(top_k: int) -> int, with no imports. normalize_query requires a "
    "string (otherwise TypeError), collapses all whitespace including Unicode to one "
    "ASCII space, removes outer whitespace, preserves case/punctuation and raises "
    "ValueError for an empty result. validate_top_k requires exactly type int "
    "(reject bool, float, str and None with TypeError), requires 1 <= top_k <= 20 "
    "(otherwise ValueError), and returns the unchanged valid integer. "
    "search_request.py must contain exactly import validation (no alias or from-import) "
    "and define build_search_request(query: str, top_k: int = 5) -> dict. "
    "Call validation.normalize_query(query) first, then validation.validate_top_k(top_k); "
    "use their return values in a fresh dict with exactly keys query and top_k. "
    "Delegate validation to that module rather than duplicating it. Propagate its "
    "exceptions unchanged. Do not coerce or clamp inputs. Keyword arguments must work. "
    "Optional docstrings are allowed; no other top-level statements or imports. ",
    "search_package", "test_search_package.py", 52, 50, "local-rag-dev-loop:3",
    artifacts=("validation.py", "search_request.py"),
    codex_image="local-rag-codex:0.162.1-multifile", response_schema="files.schema.json",
)
TASK_IDS = (NORMALIZE.task_id, SEARCH_REQUEST.task_id, SEARCH_PACKAGE.task_id)


def get_task(task_id: str) -> TaskSpec:
    for task in (NORMALIZE, SEARCH_REQUEST, SEARCH_PACKAGE):
        if task.task_id == task_id:
            return task
    raise ValueError("Unknown fixed development-loop task")
