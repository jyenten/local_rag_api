def normalize_question(value: str) -> str:
    """Initial behavior for the experiment; whitespace support is the task."""
    if value == "":
        raise ValueError("Empty question")
    return value
