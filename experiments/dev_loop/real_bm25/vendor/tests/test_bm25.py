"""Independent tests of the owner-confirmed BM25 public contract.

BM25Retriever(Settings).search(question) returns document, score and metadata
lists. Settings controls top_k (1--20); scores descend, ties use ascending IDs,
and unrelated chunks are excluded. BATCH_SIZE controls Chroma pagination.
Empty collections, invalid queries and metadata raise ValueError; duplicate IDs
and inconsistent batch lengths raise RuntimeError. Metadata requires a nonblank
source and positive integer page; chunk_index is preserved without validation.
Only Chroma storage is faked: production loading and ranking run unchanged.
The absent production module intentionally blocks collection, without a stub.
"""

from copy import deepcopy
from itertools import permutations
from unittest.mock import Mock

import pytest

from app.config import Settings
from app.retrievers import bm25


class FakeCollection:
    """Synthetic, bounded offset pagination; no embeddings or persistence."""

    def __init__(self, records, *, reported_count=None, corrupt=None):
        self.records = deepcopy(records)
        self.reported_count = reported_count
        self.corrupt = corrupt
        self.calls = []
        self.loaded_ids = []

    def count(self):
        if self.reported_count is not None:
            return self.reported_count
        return len(self.records)

    def get(self, *, limit, offset=0, include=None):
        assert isinstance(limit, int) and limit > 0
        assert isinstance(offset, int) and offset >= 0
        # Turn a repeated-page/infinite-loop bug into a bounded failure.
        assert len(self.calls) < 20, "Pagination did not terminate"
        self.calls.append((offset, limit))
        rows = self.records[offset : offset + limit]
        batch = {
            "ids": [row[0] for row in rows],
            "documents": [row[1] for row in rows],
            "metadatas": deepcopy([row[2] for row in rows]),
        }
        self.loaded_ids.extend(batch["ids"])
        if self.corrupt is not None:
            self.corrupt(batch, offset)
        return batch


def record(identifier, text, page=1):
    return identifier, text, {
        "source": "synthetic.txt",
        "page": page,
        "chunk_index": page - 1,
    }


@pytest.fixture
def run_search(monkeypatch, tmp_path):
    """Construct through the public API with storage replaced, never ranking."""
    def search(collection, query, top_k, *, batch_size=2):
        settings = Settings(
            _env_file=None,
            chroma_dir=tmp_path / "unused-chroma",
            collection_name="synthetic-bm25",
            retrieval_results=top_k,
        )
        client = Mock(spec=["get_collection"])
        client.get_collection.return_value = collection
        persistent_client = Mock(return_value=client)
        monkeypatch.setattr(bm25.chromadb, "PersistentClient", persistent_client)
        monkeypatch.setattr(bm25, "BATCH_SIZE", batch_size)
        retriever = bm25.BM25Retriever(settings)
        persistent_client.assert_called_once_with(path=str(settings.chroma_dir))
        client.get_collection.assert_called_once_with(name=settings.collection_name)
        result = retriever.search(query)
        assert isinstance(result, tuple) and len(result) == 3
        assert all(isinstance(values, list) for values in result)
        assert all(isinstance(text, str) for text in result[0])
        assert all(isinstance(score, float) for score in result[1])
        assert all(isinstance(metadata, dict) for metadata in result[2])
        assert len(result[0]) == len(result[1]) == len(result[2])
        return result

    return search


def test_pagination_loads_every_chunk_once_with_final_partial_batch(run_search):
    rows = [record(f"id-{i}", f"quartz marker{i}", i + 1) for i in range(5)]
    rows += [record(f"noise-{i}", "unrelated granite", i + 6) for i in range(8)]
    collection = FakeCollection(rows)

    documents, scores, metadatas = run_search(collection, "quartz", 20, batch_size=2)

    assert len(documents) == len(scores) == len(metadatas) == 5
    assert set(documents) == {row[1] for row in rows[:5]}
    assert len(collection.loaded_ids) == len(rows)
    assert set(collection.loaded_ids) == {row[0] for row in rows}
    assert collection.calls == [(offset, 2) for offset in range(0, 12, 2)] + [(12, 1)]
    repeated = run_search(FakeCollection(rows), "quartz", 20, batch_size=2)
    assert repeated == (documents, scores, metadatas)


def ranking_rows():
    # Rare query terms and equal document lengths avoid common-term IDF traps.
    return [
        record("strong", "quartz zircon mineral", 1),
        record("weak", "quartz granite mineral", 2),
        *[record(f"noise-{i}", "basalt granite mineral", i + 3) for i in range(8)],
    ]


def test_relevant_lexical_match_ranks_above_weaker_match(run_search):
    documents, scores, metadatas = run_search(
        FakeCollection(ranking_rows()), "quartz zircon", 10
    )
    assert documents == ["quartz zircon mineral", "quartz granite mineral"]
    assert len(scores) == len(metadatas) == 2
    assert scores[0] > scores[1]
    assert scores == sorted(scores, reverse=True)


def test_top_k_limits_results(run_search):
    documents, scores, metadatas = run_search(
        FakeCollection(ranking_rows()), "quartz zircon", 1
    )
    assert documents == ["quartz zircon mineral"]
    assert len(scores) == len(metadatas) == 1


def test_ties_use_document_id_independently_of_collection_order(run_search):
    tied = [record(identifier, "quartz mineral", page)
            for identifier, page in [("z", 1), ("a", 3), ("m", 2)]]
    noise = [record(f"noise-{i}", "granite mineral", i + 4) for i in range(7)]
    observed = []
    for ordering in permutations(tied):
        documents, scores, metadatas = run_search(
            FakeCollection([*ordering, *noise]), "quartz", 2
        )
        assert documents == ["quartz mineral"] * 2
        assert len(scores) == len(metadatas) == 2
        assert scores[0] == scores[1]
        pages = [metadata["page"] for metadata in metadatas]
        assert pages == [3, 2]
        observed.append((documents, scores, metadatas))
    assert all(result == observed[0] for result in observed)


def test_ranking_is_independent_of_chroma_return_order(run_search):
    rows = ranking_rows()
    forward = run_search(FakeCollection(rows), "quartz zircon", 10)
    reverse = run_search(FakeCollection(list(reversed(rows))), "quartz zircon", 10)
    assert forward == reverse


def test_unrelated_chunks_do_not_fill_unused_top_k_slots(run_search):
    documents, scores, metadatas = run_search(
        FakeCollection(ranking_rows()), "zircon", 20
    )
    assert documents == ["quartz zircon mineral"]
    assert len(scores) == len(metadatas) == 1


def test_query_without_lexical_matches_returns_no_chunks(run_search):
    documents, scores, metadatas = run_search(
        FakeCollection(ranking_rows()), "sapphire", 20
    )
    assert list(documents) == list(scores) == list(metadatas) == []


def test_metadata_and_scores_remain_aligned_after_ranking(run_search):
    rows = ranking_rows()
    rows[0][2].update(source="first-synthetic.txt", page=17, chunk_index=4)
    rows[1][2].update(source="second-synthetic.txt", page=29, chunk_index="unvalidated")
    collection = FakeCollection(list(reversed(rows)))
    before = deepcopy(collection.records)
    documents, scores, metadatas = run_search(
        collection, "quartz zircon", 10
    )
    assert len(documents) == len(scores) == len(metadatas) == 2
    assert documents == [rows[0][1], rows[1][1]]
    assert scores[0] > scores[1]
    expected = {text: metadata for _, text, metadata in rows}
    for text, metadata in zip(documents, metadatas):
        assert metadata == expected[text]
    # Changing top_k must preserve the leading document/score association.
    singleton = run_search(FakeCollection(rows), "quartz zircon", 1)
    assert singleton[0] == [documents[0]]
    assert singleton[1] == [scores[0]]
    assert collection.records == before


def test_empty_collection_raises_value_error(run_search):
    with pytest.raises(ValueError):
        run_search(FakeCollection([]), "quartz", 5)


@pytest.mark.parametrize("chunk_fields", [{}, {"chunk_index": None},
                                         {"chunk_index": -7},
                                         {"chunk_index": "unvalidated"}])
def test_chunk_index_is_preserved_without_mandatory_validation(run_search, chunk_fields):
    rows = ranking_rows()
    metadata = {"source": "synthetic.txt", "page": 1, **chunk_fields}
    rows[0] = (rows[0][0], rows[0][1], metadata)
    documents, _, metadatas = run_search(FakeCollection(rows), "zircon", 5)
    assert documents == [rows[0][1]]
    assert metadatas == [metadata]


@pytest.mark.parametrize("duplicate_position", [1, 3])
def test_duplicate_document_ids_raise_runtime_error(run_search, duplicate_position):
    rows = ranking_rows()
    rows[duplicate_position] = record(rows[0][0], "different quartz chunk", 15)
    with pytest.raises(RuntimeError):
        run_search(FakeCollection(rows), "quartz", 5, batch_size=2)


@pytest.mark.parametrize("query", ["", "   ", None, 42, [], "!!!"])
def test_invalid_query_raises_value_error(run_search, query):
    with pytest.raises(ValueError):
        run_search(FakeCollection(ranking_rows()), query, 5)


@pytest.mark.parametrize("identifier", [None, "", "   ", 123])
@pytest.mark.parametrize("invalid_position", [0, 3])
def test_invalid_chunk_id_raises_value_error(run_search, identifier, invalid_position):
    rows = ranking_rows()
    _, text, metadata = rows[invalid_position]
    rows[invalid_position] = (identifier, text, metadata)
    collection = FakeCollection(rows)

    with pytest.raises(ValueError, match="Invalid chunk ID"):
        run_search(collection, "quartz", 5, batch_size=2)

    expected_offset = (invalid_position // 2) * 2
    assert any(offset == expected_offset for offset, _ in collection.calls)


@pytest.mark.parametrize("document", ["", "   ", "!!!", None, 123])
@pytest.mark.parametrize("invalid_position", [0, 3])
def test_invalid_document_raises_value_error(run_search, document, invalid_position):
    rows = ranking_rows()
    identifier, _, metadata = rows[invalid_position]
    rows[invalid_position] = (identifier, document, metadata)
    collection = FakeCollection(rows)

    with pytest.raises(ValueError, match="Invalid document for chunk"):
        run_search(collection, "quartz", 5, batch_size=2)

    expected_offset = (invalid_position // 2) * 2
    assert any(offset == expected_offset for offset, _ in collection.calls)


def test_overreported_collection_count_raises_runtime_error(run_search):
    rows = ranking_rows()
    collection = FakeCollection(rows, reported_count=len(rows) + 1)

    with pytest.raises(RuntimeError):
        run_search(collection, "quartz", 5, batch_size=2)

    assert any(offset >= len(rows) for offset, _ in collection.calls)


@pytest.mark.parametrize("metadata", [
    None, {}, "malformed",
    {"page": 1}, {"source": "synthetic.txt"},
    *[{"source": source, "page": 1} for source in [None, "", "   ", 42]],
    *[{"source": "synthetic.txt", "page": page}
      for page in [None, 0, -1, "1", "not-an-int", 1.5, True]],
])
def test_invalid_metadata_raises_value_error(run_search, metadata):
    rows = ranking_rows()
    rows[3] = (rows[3][0], rows[3][1], metadata)
    with pytest.raises(ValueError):
        run_search(FakeCollection(rows), "quartz", 5, batch_size=2)


@pytest.mark.parametrize("field", ["ids", "documents", "metadatas"])
@pytest.mark.parametrize("change", ["shorter", "longer"])
@pytest.mark.parametrize("corrupt_offset", [0, 2])
def test_inconsistent_batch_lengths_raise_runtime_error(
    run_search, field, change, corrupt_offset
):
    def corrupt(batch, offset):
        if offset == corrupt_offset:
            if change == "shorter":
                batch[field].pop()
            else:
                extra = {
                    "ids": "extra-id",
                    "documents": "extra quartz chunk",
                    "metadatas": {"source": "extra.txt", "page": 1},
                }
                batch[field].append(extra[field])

    collection = FakeCollection(ranking_rows(), corrupt=corrupt)
    with pytest.raises(RuntimeError):
        run_search(collection, "quartz", 5, batch_size=2)
    assert any(offset == corrupt_offset for offset, _ in collection.calls)
