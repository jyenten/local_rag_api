import re

from document_search.normalize import normalize_text


_TOKEN_PATTERN = re.compile(r"\b\w+\b")

def tokenize(text: str) -> list[str]:
    normalized = normalize_text(text)
    return _TOKEN_PATTERN.findall(normalized)