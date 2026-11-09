"""Fresh-process provenance probes, separate from pytest and model feedback."""

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / 'checks'))
from test_retrieval_citations import load_retrieval, retriever


def observe(path):
    module = load_retrieval(path)
    texts = ['Unrelated first-document overview.', 'Alpha is evidence from the second document.']
    metadata = [{'source': 'one.pdf', 'page': 1}, {'source': 'two.pdf', 'page': 9}]
    context, selected, *_ = retriever(module, texts, metadata, fallback=True).build_context('alpha')
    provenance = (context == texts[1] and len(selected) == 1
                  and selected[0].text == texts[1] and selected[0].metadata == {'source': 'two.pdf', 'page': 9}
                  and metadata == [{'source': 'one.pdf', 'page': 1}, {'source': 'two.pdf', 'page': 9}])
    line = module.RetrievedLine(texts[1], metadata[1])
    negative = retriever(module, scores=[-100]).rerank_lines('alpha', [line]) == [line]
    return {'fallback_source_and_page_correct': provenance, 'negative_best_retained': negative}


if __name__ == '__main__':
    print(json.dumps(observe(Path('/work/question.py'))))
