"""Citation regressions for the real retrieval module; no databases or ML models."""

import importlib.util
import os
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

import pytest


def load_retrieval(path):
    """Execute the complete module with only optional external constructors stubbed."""
    def forbidden(*args, **kwargs):
        raise AssertionError('This regression must not initialize storage or a model')
    chroma, utils, embeddings = (ModuleType(name) for name in
                               ('chromadb', 'chromadb.utils', 'chromadb.utils.embedding_functions'))
    chroma.PersistentClient = forbidden
    chroma.utils, utils.embedding_functions = utils, embeddings
    embeddings.SentenceTransformerEmbeddingFunction = forbidden
    transformers, config = ModuleType('sentence_transformers'), ModuleType('app.config')
    transformers.CrossEncoder, config.Settings = forbidden, SimpleNamespace
    spec = importlib.util.spec_from_file_location('_citation_regression_subject', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'chromadb': chroma, 'chromadb.utils': utils,
            'chromadb.utils.embedding_functions': embeddings, 'sentence_transformers': transformers,
            'app.config': config, spec.name: module}):
        spec.loader.exec_module(module)
    return module


@pytest.fixture
def subject():
    workspace = os.environ.get('DEV_LOOP_WORKSPACE')
    path = (Path(workspace) / 'question.py' if workspace else
            Path(__file__).resolve().parents[1] / 'app/retrieval.py')
    return load_retrieval(path)


def retriever(module, documents=(), metadata=(), *, scores=None, limit=5, fallback=False):
    instance = module.Retriever.__new__(module.Retriever)
    instance.settings = SimpleNamespace(max_context_lines=limit, reranker_candidate_lines=40)
    instance.reranker = SimpleNamespace(predict=lambda pairs:
        list(scores) if scores is not None else [10.0] * len(pairs))
    instance.search = lambda question: (list(documents), [0.2] * len(documents), list(metadata))
    if fallback:
        instance.rerank_lines = lambda question, lines: []
    return instance


def test_existing_empty_rerank(subject):
    assert retriever(subject).rerank_lines('alpha', []) == []


def test_existing_positive_scores_sorted(subject):
    lines = [subject.RetrievedLine('Alpha first relevant statement.', {'source': 'one.pdf'}),
             subject.RetrievedLine('Alpha second relevant statement.', {'source': 'two.pdf'})]
    selected = retriever(subject, scores=[1, 20]).rerank_lines('alpha', lines)
    assert selected == [lines[1]]


def test_existing_search_payload_preserved(subject):
    text, metadata = ['Alpha is useful evidence for this query.'], [{'source': 'one.pdf', 'page': 7}]
    context, selected, documents, distances, returned = retriever(subject, text, metadata).build_context('alpha')
    assert context == text[0] and selected[0].metadata == metadata[0]
    assert documents == text and returned == metadata and distances == [0.2]


@pytest.mark.parametrize('score', [-2.0, -100.0, -1000.0])
def test_negative_best_kept(subject, score):
    line = subject.RetrievedLine('Alpha is useful evidence for this query.', {'source': 'one.pdf'})
    assert retriever(subject, scores=[score]).rerank_lines('alpha', [line]) == [line]


def test_zero_best_kept(subject):
    line = subject.RetrievedLine('Alpha is useful evidence for this query.', {'source': 'one.pdf'})
    assert retriever(subject, scores=[-1]).rerank_lines('alpha', [line]) == [line]


def test_forced_fallback_retains_second_source(subject):
    texts = ['Unrelated overview in the first document.', 'Alpha belongs to the second document.']
    metadata = [{'source': 'one.pdf', 'page': 1, 'chunk_index': 3},
                {'source': 'two.pdf', 'page': 9, 'chunk_index': 12}]
    expected = dict(metadata[1])
    context, selected, *_ = retriever(subject, texts, metadata, fallback=True).build_context('alpha')
    assert context == texts[1] and len(selected) == 1
    assert selected[0].text == texts[1] and selected[0].metadata == expected


def test_forced_fallback_retains_each_source(subject):
    texts = ['Alpha has evidence in the first document.', 'Alpha has evidence in the second document.']
    metadata = [{'source': 'one.pdf', 'page': 2}, {'source': 'two.pdf', 'page': 8}]
    expected = [dict(item) for item in metadata]
    context, selected, *_ = retriever(subject, texts, metadata, fallback=True).build_context('alpha')
    assert context == '\n'.join(line.text for line in selected) and len(selected) == 2
    assert [(line.text, line.metadata) for line in selected] == list(zip(texts, expected))


def test_forced_fallback_deduplicates_identical_lines(subject):
    text = 'Alpha is the same repeated evidence sentence.'
    metadata = [{'source': 'one.pdf', 'page': 2}, {'source': 'two.pdf', 'page': 8}]
    context, selected, *_ = retriever(subject, [text, text], metadata, fallback=True).build_context('alpha')
    assert context == text and len(selected) == 1 and selected[0].metadata == metadata[0]


def test_reranked_lines_keep_identity(subject):
    texts = ['Alpha first relevant evidence sentence.', 'Alpha second relevant evidence sentence.']
    metadata = [{'source': 'one.pdf', 'page': 2}, {'source': 'two.pdf', 'page': 8}]
    _, selected, *_ = retriever(subject, texts, metadata, scores=[1, 20]).build_context('alpha')
    assert selected[0].text == texts[1] and selected[0].metadata == metadata[1]


def test_no_evidence_no_fabricated_source(subject):
    instance = retriever(subject, ['Unrelated overview without the keyword.'], [{'source': 'one.pdf'}], fallback=True)
    context, selected, *_ = instance.build_context('alpha')
    assert context == '' and selected == []


@pytest.mark.parametrize('limit', [1, 2])
def test_fallback_respects_context_limit(subject, limit):
    texts = [f'Alpha evidence sentence number {i} is relevant.' for i in range(3)]
    metadata = [{'source': f'{i}.pdf', 'page': i + 1} for i in range(3)]
    context, selected, *_ = retriever(subject, texts, metadata, fallback=True, limit=limit).build_context('alpha')
    assert len(selected) == limit and context == '\n'.join(texts[:limit])
    assert [line.metadata for line in selected] == metadata[:limit]


def test_metadata_not_mutated(subject):
    metadata = [{'source': 'one.pdf', 'page': 2, 'chunk_index': 17},
                {'source': 'two.pdf', 'page': 9, 'chunk_index': 27}]
    before = [dict(item) for item in metadata]
    retriever(subject, ['Unrelated text from the first document.', 'Alpha is relevant evidence from the second source.'],
              metadata, fallback=True).build_context('alpha')
    assert metadata == before
