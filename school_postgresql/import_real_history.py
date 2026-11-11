"""Import ACTUAL Local RAG API evaluation JSONL runs (never synthesize scores).

Usage (from repository root, after SQL schema+seed):
  python -m pip install "psycopg[binary]"
  set SCHOOL_RAG_DSN=postgresql://USER:PASSWORD@localhost:HOST_PORT/local_rag_school
  python school_postgresql/import_real_history.py --dataset dev \
      --dataset-file rag_api_project/eval/dev_questions.json \
      --retriever bm25 \
      --history-file rag_api_project/eval/results/dev_bm25_runs.jsonl

JSONL files under eval/results are local and typically absent from public GitHub.
No change to /ask, ingestion, retrieval metrics or gold datasets.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path


def git_blob_sha(data: bytes) -> str:
    """SHA-1 object identifier, including Git's blob header."""
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def load_questions(dataset_path: Path) -> tuple[set[str], str, str]:
    raw_bytes = dataset_path.read_bytes()
    raw = json.loads(raw_bytes)
    if not isinstance(raw, list) or not raw:
        raise ValueError("Dataset must be a nonempty list")
    ids: list[str] = []
    for q in raw:
        if not isinstance(q, dict) or not isinstance(q.get("id"), str):
            raise ValueError("Malformed evaluation question")
        ids.append(q["id"])
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate dataset question IDs")
    return set(ids), git_blob_sha(raw_bytes), hashlib.sha256(raw_bytes).hexdigest()


def validate_run(raw: dict, dataset_name: str, dataset_hash: str,
                 ids: set[str]) -> tuple[list[tuple[str, int | None]], datetime]:
    if raw.get("dataset") != dataset_name or raw.get("dataset_hash") != dataset_hash:
        raise ValueError("Dataset name or SHA-256 does not match the local JSON source")
    questions = raw.get("questions")
    if not isinstance(questions, list) or len(questions) != len(ids):
        raise ValueError("Run must evaluate the complete fixed dataset")
    if raw.get("question_count") != len(ids):
        raise ValueError("Incorrect question_count")
    found: list[tuple[str, int | None]] = []
    for q in questions:
        if not isinstance(q, dict) or not isinstance(q.get("id"), str):
            raise ValueError("Invalid question-result entry")
        rank = q.get("first_evidence_rank")
        if rank is not None and (type(rank) is not int or rank <= 0):
            raise ValueError("Invalid first_evidence_rank")
        expected_rr = 0 if rank is None else 1 / rank
        rr = q.get("reciprocal_rank")
        if type(rr) not in (int, float) or not math.isfinite(rr) or abs(rr-expected_rr) > 1e-6:
            raise ValueError("Question reciprocal_rank inconsistent with first_evidence_rank")
        found.append((q["id"],rank))
    if {qid for qid, _ in found} != ids or len(set(qid for qid, _ in found)) != len(ids):
        raise ValueError("Run question IDs differ from dataset")
    metrics = raw.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("Missing metrics")
    expected = {"mrr": sum((0 if rank is None else 1/rank) for _,rank in found)/len(found)}
    for k in (1,3,5,8):
        expected[f"hit_at_{k}"] = sum(rank is not None and rank <= k
                                    for _,rank in found)/len(found)
    for name,value in expected.items():
        got = metrics.get(name)
        if type(got) not in (int,float) or not math.isfinite(got) or abs(got-value)>1e-6:
            raise ValueError(f"Aggregate {name} inconsistent with actual question ranks")
    timestamp = datetime.fromisoformat(raw["timestamp"])
    if timestamp.tzinfo is None:
        raise ValueError("Run timestamp must be timezone aware")
    return found,timestamp


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset",choices=("dev","random"),required=True)
    parser.add_argument("--dataset-file",type=Path,required=True)
    parser.add_argument("--retriever",choices=("legacy","bm25","vector"),required=True)
    parser.add_argument("--history-file",type=Path,required=True)
    parser.add_argument("--check-only",action="store_true",
                        help="Validate local JSONL without opening the database")
    args=parser.parse_args()

    ids,blob_sha,dataset_hash=load_questions(args.dataset_file)
    parsed=[]
    for lineno,line in enumerate(args.history_file.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip():
            continue
        raw=json.loads(line)
        try:
            question_results,timestamp=validate_run(raw,args.dataset,dataset_hash,ids)
        except (KeyError,ValueError,TypeError) as exc:
            raise ValueError(f"Invalid JSONL line {lineno}: {exc}") from exc
        provenance="jsonl:sha256:"+hashlib.sha256(
            json.dumps(raw,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")
        ).hexdigest()
        parsed.append((raw,question_results,timestamp,provenance))
    if not parsed:
        raise ValueError("No original evaluation runs in the JSONL file")
    if args.check_only:
        print(f"Validated {len(parsed)} real run(s); dataset={args.dataset}, questions={len(ids)}")
        return

    dsn=os.environ.get("SCHOOL_RAG_DSN")
    if not dsn:
        raise RuntimeError("Set SCHOOL_RAG_DSN (never commit credentials)")
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError('Install PostgreSQL driver: pip install "psycopg[binary]"') from exc

    inserted=0
    with psycopg.connect(dsn) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT dataset_id FROM school_rag.eval_datasets
                   WHERE dataset_name=%s AND source_git_blob_sha=%s""",
                (args.dataset,blob_sha))
            row=cur.fetchone()
            if row is None:
                raise ValueError("Seeded dataset Git blob differs from local dataset: refuse import")
            dataset_id=row[0]
            cur.execute(
                """SELECT external_question_id,question_id
                   FROM school_rag.eval_questions WHERE dataset_id=%s""",
                (dataset_id,))
            question_map=dict(cur.fetchall())
            if set(question_map) != ids:
                raise ValueError("Database question IDs differ from local source file")
            for raw,question_results,timestamp,provenance in parsed:
                cur.execute(
                    """SELECT evaluation_run_id FROM school_rag.eval_runs
                       WHERE record_kind='jsonl_run' AND source_reference=%s""",
                    (provenance,))
                if cur.fetchone():
                    continue
                latency=raw.get("latency") or {}
                if not isinstance(latency,dict):
                    raise ValueError("Malformed latency metadata")
                config=raw.get("retrieval_config")
                if not isinstance(config,dict):
                    raise ValueError("Malformed retrieval config")
                commit=raw.get("git_commit")
                if not isinstance(commit,str) or len(commit)!=40:
                    raise ValueError("Missing full Git commit hash")
                dirty=raw.get("git_dirty")
                if type(dirty) is not bool:
                    raise ValueError("Missing git_dirty bool")
                top_k=config.get("retrieval_results")
                if type(top_k) is not int or top_k<=0:
                    raise ValueError("Missing retrieval top-k")
                cur.execute(
                    """INSERT INTO school_rag.eval_runs
                       (dataset_id,dataset_label,retriever,run_date,executed_at,question_count,
                        retrieval_top_k,git_commit_sha,git_dirty,dataset_sha256,
                        mrr,latency_mean_ms,latency_p50_ms,latency_p95_ms,
                        record_kind,source_reference,provenance_note)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                               %s,%s,%s,%s,'jsonl_run',%s,%s)
                       RETURNING evaluation_run_id""",
                    (dataset_id,args.dataset,args.retriever,timestamp.date(),timestamp,len(ids),
                     top_k,commit,dirty,dataset_hash,
                     raw["metrics"]["mrr"],latency.get("mean_ms"),
                     latency.get("p50_ms"),latency.get("p95_ms"),provenance,
                     "Actual local JSONL; indexing_run_id NULL until corpus provenance verified"))
                run_id=cur.fetchone()[0]
                for k in (1,3,5,8):
                    cur.execute(
                        """INSERT INTO school_rag.eval_hit_rates
                           (evaluation_run_id,k,hit_rate) VALUES (%s,%s,%s)""",
                        (run_id,k,raw["metrics"][f"hit_at_{k}"]))
                for qid,rank in question_results:
                    cur.execute(
                        """INSERT INTO school_rag.eval_results
                           (evaluation_run_id,dataset_id,question_id,first_evidence_rank)
                           VALUES (%s,%s,%s,%s)""",
                        (run_id,dataset_id,question_map[qid],rank))
                inserted+=1
    print(f"Imported {inserted} new real JSONL run(s); skipped {len(parsed)-inserted} duplicates")


if __name__=="__main__":
    main()
