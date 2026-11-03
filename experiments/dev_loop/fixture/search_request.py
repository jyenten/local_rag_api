def build_search_request(query: str, top_k: int = 5) -> dict:
    """Initial behavior; normalization and strict validation are the task."""
    if query == "":
        raise ValueError("Empty query")
    return {"query": query, "top_k": top_k}
