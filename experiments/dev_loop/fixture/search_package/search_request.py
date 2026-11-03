import validation


def build_search_request(query: str, top_k: int = 5) -> dict:
    return {"query": validation.normalize_query(query), "top_k": top_k}
