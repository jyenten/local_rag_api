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
TASK_IDS = (NORMALIZE.task_id, SEARCH_REQUEST.task_id)


def get_task(task_id: str) -> TaskSpec:
    for task in (NORMALIZE, SEARCH_REQUEST):
        if task.task_id == task_id:
            return task
    raise ValueError("Unknown fixed development-loop task")
