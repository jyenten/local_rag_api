def normalize_query(query: str) -> str:
    if query == "":
        raise ValueError("Empty query")
    return query


def validate_top_k(top_k: int) -> int:
    return top_k
