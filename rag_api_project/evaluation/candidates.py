from collections.abc import Iterable
from pathlib import Path

from document_search.load_pages import load_pdf_pages
from evaluation.evidence import normalize_evidence_text
from evaluation.models import EvaluationQuestion


def normalize_question(text: str) -> str:
    return " ".join(text.casefold().split())


def build_page_lookup(
    data_dir: Path,
) -> dict[tuple[str, int], str]:
    return {
        (page.source, page.page): normalize_evidence_text(page.text)
        for page in load_pdf_pages(data_dir)
    }


def validate_candidate_questions(
    candidates: tuple[EvaluationQuestion, ...],
    existing_datasets: Iterable[
        tuple[EvaluationQuestion, ...]
    ],
    data_dir: Path,
) -> None:
    existing_questions = [
        question
        for dataset in existing_datasets
        for question in dataset
    ]

    existing_ids = {
        question.id
        for question in existing_questions
    }

    existing_question_texts = {
        normalize_question(question.question)
        for question in existing_questions
    }

    candidate_ids: set[str] = set()
    candidate_question_texts: set[str] = set()

    page_lookup = build_page_lookup(data_dir)

    errors: list[str] = []

    for candidate in candidates:
        if candidate.id in existing_ids:
            errors.append(
                f"{candidate.id}: ID already exists."
            )

        if candidate.id in candidate_ids:
            errors.append(
                f"{candidate.id}: duplicate candidate ID."
            )

        candidate_ids.add(candidate.id)

        normalized_question = normalize_question(
            candidate.question
        )

        if (
            normalized_question in existing_question_texts
            or normalized_question in candidate_question_texts
        ):
            errors.append(
                f"{candidate.id}: duplicate candidate question."
            )

        candidate_question_texts.add(
            normalized_question
        )

        for evidence in candidate.gold_evidence:
            normalized_fragments = tuple(
                normalize_evidence_text(fragment)
                for fragment in evidence.contains_any
            )

            for page_number in evidence.pages:
                page_text = page_lookup.get(
                    (evidence.source, page_number)
                )

                if page_text is None:
                    errors.append(
                        f"{candidate.id}: source/page does not exist: "
                        f"{evidence.source} page {page_number}."
                    )
                    continue

                if not any(
                    fragment in page_text
                    for fragment in normalized_fragments
                ):
                    errors.append(
                        f"{candidate.id}: no contains_any fragment "
                        f"matches {evidence.source} "
                        f"page {page_number}."
                    )

    if errors:
        raise ValueError(
            "Candidate validation invalid:\n- "
            + "\n- ".join(errors)
        )