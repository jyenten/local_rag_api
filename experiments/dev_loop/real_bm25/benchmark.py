"""Offline paired measurements. Imported only by the container or trusted tests."""

import hashlib
import importlib.util
import json
import statistics
import sys
from collections import Counter
from pathlib import Path
from time import perf_counter
from types import SimpleNamespace


def corpus():
    return [(f"chunk-{i:04}",
             " ".join([f"term{(i + j) % 173}" for j in range(128)]),
             {"source": "synthetic-bm25.txt", "page": i + 1}) for i in range(1000)]


QUERIES = ["term0", "term30 term31", "TERM90", "term172", "unrelated", "term5 term170"]


class Collection:
    def __init__(self, rows):
        self.rows = rows

    def count(self):
        return len(self.rows)

    def get(self, *, limit, offset, include):
        rows = self.rows[offset:offset + limit]
        return {"ids": [r[0] for r in rows], "documents": [r[1] for r in rows],
                "metadatas": [dict(r[2]) for r in rows]}


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def construct(module, rows):
    collection = Collection(rows)
    module.chromadb.PersistentClient = lambda **kwargs: SimpleNamespace(
        get_collection=lambda **kwargs: collection)
    settings = SimpleNamespace(chroma_dir=Path('/unused'), collection_name='synthetic', retrieval_results=20)
    return module.BM25Retriever(settings)


def counted(module, rows):
    original = module.tokenize
    calls = []

    def tokenize(text):
        calls.append(text)
        return original(text)

    module.tokenize = tokenize
    try:
        retriever = construct(module, rows)
    finally:
        module.tokenize = original
    return retriever, calls


def compare(before_path, after_path):
    before = load(before_path, 'before_bm25')
    after = load(after_path, 'after_bm25')
    rows = corpus()
    data_hash = hashlib.sha256(json.dumps(rows, ensure_ascii=True, separators=(',', ':')).encode()).hexdigest()
    results, counts, call_inputs = {}, {}, {}
    for label, module in [('before', before), ('after', after)]:
        retriever, calls = counted(module, rows)
        counts[label] = len(calls)
        call_inputs[label] = Counter(calls)
        results[label] = [retriever.search(query) for query in QUERIES]
    # Warm both paths once. Count instrumentation is not included in timings.
    for module in (before, after):
        construct(module, rows)
    times = {'before': [], 'after': []}
    for trial in range(7):
        ordering = [('before', before), ('after', after)]
        for label, module in (ordering if trial % 2 == 0 else reversed(ordering)):
            start = perf_counter()
            construct(module, rows)
            times[label].append((perf_counter() - start) * 1000)
    equal = results['before'] == results['after']
    fingerprints = {k: hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest()
                    for k, v in results.items()}
    expected_inputs = Counter(row[1] for row in rows)
    inputs_match = (call_inputs['before'] == expected_inputs + expected_inputs
                    and call_inputs['after'] == expected_inputs)
    return {'dataset': 'deterministic-synthetic-1000x128', 'dataset_sha256': data_hash,
            'document_count': len(rows), 'queries': QUERIES, 'paired_trials': 7,
            'init_tokenize_calls': counts, 'init_ms': times,
            'median_init_ms': {k: statistics.median(v) for k, v in times.items()},
            'search_results_equal': equal, 'search_results_sha256': fingerprints,
            'tokenize_inputs_match_corpus': inputs_match,
            'single_pass_observed': inputs_match and counts['before'] == 2 * len(rows) and counts['after'] == len(rows),
            'storage': 'synthetic Chroma seam; real rank_bm25 ranking',
            'timing_scope': 'BM25Retriever initialization only; model/container startup excluded'}


def main():
    # Only controller-selected paths inside the ephemeral container.
    sys.path.insert(0, '/opt/bm25/vendor')
    print(json.dumps(compare(Path('/work/before.py'), Path('/work/app/retrievers/bm25.py'))))


if __name__ == '__main__':
    main()
