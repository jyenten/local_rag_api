import argparse
import subprocess
from dataclasses import replace
from pathlib import Path

from app.config import get_settings
from app.retrieval import Retriever as LegacyRetriever
from app.retrievers.vector import VectorRetriever
from app.retrievers.bm25 import BM25Retriever
from evaluation.dataset import (
    calculate_dataset_hash,
    load_dataset,
)
from evaluation.history import append_run
from evaluation.latency import TimedRetriever
from evaluation.models import RetrievalConfig
from evaluation.runner import evaluate_dataset


REPOSITORY_DIR = Path(__file__).resolve().parent.parent


DATASET_PATHS = {
    "dev": Path("eval/dev_questions.json"),
    "random": Path("eval/random_questions.json"),
}

HISTORY_PATHS = {
    ("legacy", "dev"): Path(
        "eval/results/dev_runs.jsonl"
    ),
    ("legacy", "random"): Path(
        "eval/results/random_runs.jsonl"
    ),
    ("vector", "dev"): Path(
        "eval/results/dev_vector_runs.jsonl"
    ),
    ("vector", "random"): Path(
        "eval/results/random_vector_runs.jsonl"
    ),
    ("bm25", "dev"): Path(
        "eval/results/dev_bm25_runs.jsonl"
    ),
    ("bm25", "random"): Path(
        "eval/results/random_bm25_runs.jsonl"
    ),
}

RETRIEVERS = {
    "vector": VectorRetriever,
    "bm25": BM25Retriever,
    "legacy": LegacyRetriever,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Evaluate a retrieval strategy "
            "against DEV or RANDOM."
        )
    )

    parser.add_argument(
        "--retriever",
        choices=tuple(RETRIEVERS),
        default="legacy",
        help="Retrieval strategy to evaluate.",
    )

    parser.add_argument(
        "--dataset",
        choices=("dev", "random"),
        default="dev",
        help="Evaluation dataset.",
    )

    return parser.parse_args()


def get_git_commit() -> str:
    try:
        commit = subprocess.check_output(
            [
                "git",
                "rev-parse",
                "HEAD",
            ],
            text=True,
            cwd=REPOSITORY_DIR,
        ).strip()
    except (subprocess.SubprocessError, OSError) as exc:
        raise RuntimeError("Unable to determine Git commit.") from exc
    if not commit:
        raise RuntimeError("Unable to determine Git commit: empty output.")
    return commit


def get_git_dirty() -> bool:
    try:
        status = subprocess.check_output(
            [
                "git",
                "status",
                "--porcelain",
            ],
            text=True,
            cwd=REPOSITORY_DIR,
        ).strip()

        return bool(status)
    except (subprocess.SubprocessError, OSError) as exc:
        raise RuntimeError("Unable to determine Git working-tree status.") from exc


def build_retriever(
    name: str,
    settings,
):
    try:
        retriever_class = RETRIEVERS[name]
    except KeyError as exc:
        raise ValueError(
            f"Unknown retriever: {name}"
        ) from exc

    return retriever_class(settings)



def main() -> None:
    args = parse_args()
    git_commit = get_git_commit()
    git_dirty = get_git_dirty()

    eval_path = DATASET_PATHS[
        args.dataset
    ]
    history_path = HISTORY_PATHS[
        (args.retriever, args.dataset)
    ]

    questions = load_dataset(
        eval_path
    )

    settings = get_settings()

    retriever = TimedRetriever(build_retriever(
        args.retriever,
        settings,
    ))

    retrieval_config = RetrievalConfig(
        collection_name=settings.collection_name,
        embedding_model_name=(
            settings.embedding_model_name
        ),
        retrieval_results=(
            settings.retrieval_results
        ),
    )

    run = evaluate_dataset(
        questions,
        retriever,
        dataset=args.dataset,
        dataset_hash=calculate_dataset_hash(
            eval_path
        ),
        retrieval_config=retrieval_config,
        git_commit=git_commit,
        git_dirty=git_dirty,
    )

    run = replace(run, latency=retriever.metrics())

    append_run(
        history_path,
        run,
        max_runs=10,
    )

    print("=" * 80)
    print(f"RETRIEVER: {args.retriever}")
    print(f"DATASET: {args.dataset}")
    print(f"QUESTIONS: {len(questions)}")
    print(f"LATENCY MEAN: {run.latency.mean_ms:.2f} ms")
    print(f"LATENCY P50: {run.latency.p50_ms:.2f} ms")
    print(f"LATENCY P95: {run.latency.p95_ms:.2f} ms")

    for question, result in zip(
        questions,
        run.questions,
        strict=True,
    ):
        print("=" * 80)
        print(f"ID: {question.id}")
        print(
            f"QUESTION: {question.question}"
        )
        print(
            "FIRST_EVIDENCE_RANK: "
            f"{result.first_evidence_rank}"
        )
        print(
            "RECIPROCAL_RANK: "
            f"{result.reciprocal_rank:.4f}"
        )

    print()
    print("=" * 80)
    print(
        f"MRR: {run.metrics.mrr:.4f}"
    )
    print(
        f"HIT@1: {run.metrics.hit_at_1:.4f}"
    )
    print(
        f"HIT@3: {run.metrics.hit_at_3:.4f}"
    )
    print(
        f"HIT@5: {run.metrics.hit_at_5:.4f}"
    )
    print(
        f"HIT@8: {run.metrics.hit_at_8:.4f}"
    )


if __name__ == "__main__":
    main()
