from dataclasses import replace
from pathlib import Path

import pytest

from evaluation import candidates
from document_search.models import PageDocument
from evaluation.models import EvaluationQuestion, GoldEvidence


def make_candidate(
    question_id: str,
    question: str,
    pages: tuple[int, ...] = (1,),
) -> EvaluationQuestion:
    return EvaluationQuestion(
        id=question_id,
        topic="routing",
        question=question,
        gold_evidence=(
            GoldEvidence(
                source="guide.pdf",
                pages=pages,
                contains_any=("supporting evidence",),
            ),
        ),
    )


@pytest.mark.parametrize("missing_page", [1, 2])
def test_every_declared_page_must_exist(
    monkeypatch: pytest.MonkeyPatch,
    missing_page: int,
) -> None:
    monkeypatch.setattr(
        candidates,
        "build_page_lookup",
        lambda _: {("guide.pdf", 3 - missing_page): "supporting evidence"},
    )

    with pytest.raises(
        ValueError,
        match=rf"guide\.pdf page {missing_page}",
    ):
        candidates.validate_candidate_questions(
            candidates=(make_candidate("q1", "Question one?", (1, 2)),),
            existing_datasets=(),
            data_dir=Path("unused"),
        )


@pytest.mark.parametrize("unsupported_page", [1, 2])
def test_every_declared_page_must_contain_evidence(
    monkeypatch: pytest.MonkeyPatch,
    unsupported_page: int,
) -> None:
    monkeypatch.setattr(
        candidates,
        "build_page_lookup",
        lambda _: {
            ("guide.pdf", 3 - unsupported_page): "supporting evidence",
            ("guide.pdf", unsupported_page): "unrelated material",
        },
    )

    with pytest.raises(
        ValueError,
        match=rf"no contains_any fragment matches guide\.pdf page {unsupported_page}",
    ):
        candidates.validate_candidate_questions(
            candidates=(make_candidate("q1", "Question one?", (1, 2)),),
            existing_datasets=(),
            data_dir=Path("unused"),
        )


@pytest.mark.parametrize("collision", ["id", "question"])
def test_collisions_with_existing_datasets_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
    collision: str,
) -> None:
    monkeypatch.setattr(
        candidates,
        "build_page_lookup",
        lambda _: {("guide.pdf", 1): "supporting evidence"},
    )
    existing = make_candidate("existing", "What is routing?")
    candidate = make_candidate(
        "existing" if collision == "id" else "new",
        "A different question?" if collision == "id" else " WHAT\nIS ROUTING? ",
    )
    with pytest.raises(ValueError, match="ID already exists|duplicate candidate question"):
        candidates.validate_candidate_questions(
            candidates=(candidate,),
            existing_datasets=((existing,),),
            data_dir=Path("unused"),
        )


def test_different_fragments_may_support_different_pages(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Exercise the real lookup normalization as well as contains_any OR semantics.
    monkeypatch.setattr(
        candidates,
        "load_pdf_pages",
        lambda _: [
            PageDocument(source="guide.pdf", page=1, text="FIRST\n\tEvidence"),
            PageDocument(source="guide.pdf", page=2, text="Second   evidence"),
        ],
    )
    candidate = replace(
        make_candidate("q1", "Question?"),
        gold_evidence=(GoldEvidence(
            source="guide.pdf",
            pages=(1, 2),
            contains_any=("first evidence", "SECOND EVIDENCE"),
        ),),
    )
    candidates.validate_candidate_questions(
        candidates=(candidate,), existing_datasets=(), data_dir=Path("unused"),
    )


def test_all_evidence_objects_are_validated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        candidates,
        "build_page_lookup",
        lambda _: {("guide.pdf", 1): "supporting evidence"},
    )
    candidate = make_candidate("q1", "Question?")
    candidate = replace(
        candidate,
        gold_evidence=(*candidate.gold_evidence, GoldEvidence(
            source="missing.pdf", pages=(1,), contains_any=("evidence",),
        )),
    )
    with pytest.raises(ValueError, match=r"missing\.pdf page 1"):
        candidates.validate_candidate_questions(
            candidates=(candidate,), existing_datasets=(), data_dir=Path("unused"),
        )


def test_valid_evidence_on_all_pages_passes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        candidates,
        "build_page_lookup",
        lambda _: {
            ("guide.pdf", 1): "supporting evidence for first page",
            ("guide.pdf", 2): "second page includes supporting evidence",
        },
    )

    candidates.validate_candidate_questions(
        candidates=(make_candidate("q1", "Question one?", (1, 2)),),
        existing_datasets=(),
        data_dir=Path("unused"),
    )


def test_duplicate_question_text_within_batch_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        candidates,
        "build_page_lookup",
        lambda _: {("guide.pdf", 1): "supporting evidence"},
    )

    with pytest.raises(ValueError, match="duplicate candidate question"):
        candidates.validate_candidate_questions(
            candidates=(
                make_candidate("q1", "What is routing?"),
                make_candidate("q2", " WHAT  IS  ROUTING? "),
            ),
            existing_datasets=(),
            data_dir=Path("unused"),
        )
