<a id="top"></a>

# Golden evidence and retrieval evaluation

[Česky](../cs/EVALUATION.md#cz) · [English](#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Contents — click to expand</summary>

- [1. Definition and source of truth](#en-1-definition-and-source-of-truth)
- [2. Dataset separation](#en-2-dataset-separation)
- [3. Evidence-first curation workflow](#en-3-evidence-first-curation-workflow)
- [4. Validation, approval and promotion](#en-4-validation-approval-and-promotion)
- [5. Matching and metrics](#en-5-matching-and-metrics)
- [6. Repeatable evaluation and historical baseline](#en-6-repeatable-evaluation-and-historical-baseline)
- [7. Governance references](#en-7-governance-references)
- [8. Historical baseline — 2026-10-20](#en-8-historical-baseline-2026-10-20)

</details>

---

<a id="en"></a>

**Working directory:** Run commands from `rag_api_project/`. Dataset and PDF paths below are relative to that project directory.

> **Policy:** The real `eval/dev_questions.json`, `eval/random_questions.json` and `eval/test_questions.json` datasets are protected. Candidate generation never modifies these files. Promotion requires explicit human approval. The TEST set is held out and must not be used to tune retrieval.

<a id="en-1-definition-and-source-of-truth"></a>

## 1. Definition and source of truth

A **gold evidence** record is a source-grounded passage, not an LLM-generated answer. It stores `source` (exact PDF filename), `pages` (physical 1-based PDF page numbers, not printed page labels) and `contains_any` (literal evidence fragments with **OR** semantics). An evaluation question also has `id`, `topic` and `question`. Multiple GoldEvidence records may support independent valid passages.

The following example illustrates the **schema only**. It is not verified gold evidence and must not be promoted into a protected dataset. Evidence text must be copied from the actual local PDF and must genuinely answer the question.

```json
[
  {
    "id": "routing_dev_example",
    "topic": "routing",
    "question": "Example question about a documented routing fact?",
    "gold_evidence": [
      {
        "source": "Example_Manual.pdf",
        "pages": [12],
        "contains_any": ["Exact evidence fragment copied from the source PDF"]
      }
    ]
  }
]
```


<a id="en-2-dataset-separation"></a>

## 2. Dataset separation

- `eval/dev_questions.json` — development and measured tuning.
- `eval/random_questions.json` — reproducible robustness exploration.
- `eval/test_questions.json` — held-out final assessment, never used for iterative tuning.

Historically the project uses 20 DEV, 25 RANDOM and 15 TEST questions. Dataset count and SHA-256 hash belong to the run's provenance.


<a id="en-3-evidence-first-curation-workflow"></a>

## 3. Evidence-first curation workflow

1. Inspect original PDFs in `data/`; use no external source for gold evidence.
2. Discover candidate *pages* with `python -m scripts.search_pdf "routing query" --top-k 10 --interactive`.
3. Manually verify the exact filename, physical page and directly supporting verbatim fragment.
4. Formulate **one question from that evidence** (evidence → question).
5. Check topic diversity and avoid duplicate questions or facts.
6. Write candidates **only** to `eval/candidates/<batch>.json`, normally five per curator batch.

Page-level BM25 discovery is distinct from Chroma-backed chunk-level BM25 evaluation. A high search score never proves gold validity.


<a id="en-4-validation-approval-and-promotion"></a>

## 4. Validation, approval and promotion

```bash
python -m scripts.validate_eval_candidates eval/candidates/new_batch.json
```

Validation checks IDs, duplicate question text, local source/page existence and literal fragments (normalized for case/whitespace). The validator now checks **each** listed page; tests cover missing pages and unsupported fragments. A successful `VALID: 5 candidate(s)` is necessary but not sufficient: human factual review is required.

The structural loader rejects empty text/evidence/fragment lists and non-positive or non-integer pages (including booleans). Each declared page must match **at least one** fragment; different pages may match different alternatives. This does not verify **every** `contains_any` fragment, so manually verify all alternatives. Pages without extractable text are absent from the lookup; a missing source/page error can also mean an image-only or blank page. OCR is not implemented.

Only existing protected datasets are checked for duplicates; missing datasets are skipped and other candidate batches are not scanned. Ensure all three datasets exist. Review DEV/RANDOM for repeated facts and paraphrases; use the automatic duplicate check for TEST without manually inspecting its contents during tuning. Validation/promotion use `--data-dir <directory>` independently of `RAG_DATA_DIR`.

As of the 2026-10-28 review, all seven tracked batches pass structural loading (five items each), but all 35 IDs already exist in protected datasets. Treat these as historical batches, not new candidates for promotion; full validation correctly rejects those ID collisions. This review does not confirm their fragments against source PDFs.

**Do not automatically run promotion.** Only after explicit human approval may the owner use the writing command below with an approved target and IDs:

```bash
python -m scripts.promote_eval_candidates eval/candidates/new_batch.json eval/dev_questions.json --ids routing_dev_101
```

This changes a protected dataset. GitHub evaluation governance requires human review/authorization. Never alter existing gold to make a retriever score higher.

`--ids` accepts space-separated IDs. Promotion revalidates only selected candidates and rewrites the target JSON without an automatic backup or an approval check. Human approval is a procedural boundary, not a CLI flag. CI checks candidate **structure only**, not source-PDF truth. After reviewing protected changes, an authorized human must add `human-approved-eval-change`. The workflow does not trigger on labeling alone; rerunning an old run may retain its old event payload, so ensure a fresh PR run sees the current labels.


<a id="en-5-matching-and-metrics"></a>

## 5. Matching and metrics

`evaluation/evidence.py` matches a retrieved *chunk* only when its source name equals the evidence source, its physical page is allowed, and at least one normalized `contains_any` fragment occurs in the chunk. `FIRST_EVIDENCE_RANK=None` means no evaluated result matched the gold evidence; it does not mean zero results were retrieved.

MRR averages reciprocal rank of the first match (0 for no match); Hit@K counts questions with a match at or before position K. These measure evidence retrieval, not the accuracy of generated answers. Extracted page text and indexed chunk text can differ; avoid fragments crossing chunk boundaries.


<a id="en-6-repeatable-evaluation-and-historical-baseline"></a>

## 6. Repeatable evaluation and historical baseline

```bash
python -m scripts.evaluate_retrieval --retriever legacy --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset dev
python -m scripts.evaluate_retrieval --retriever bm25 --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset random
python -m scripts.evaluate_retrieval --retriever bm25 --dataset random
```

The CLI **writes** strategy-specific JSONL histories under `eval/results/`; each file retains up to 10 runs. Provenance includes timestamp, Git commit and dirty state, dataset hash and retrieval configuration. Keep source corpus, indexing and dataset fixed when comparing retrievers.

Also archive PDF SHA-256 hashes, an index snapshot/identity and chunk count, ingest parameters, model versions/revisions, Python/packages, OS/hardware and warm-up procedure. These are not automatically recorded; a dirty flag does not preserve the diff. Export histories before rotation. There is no built-in warm-up or repetition flag; the first `search()` is included. `--dataset random` evaluates the **entire fixed** RANDOM set. The older `scripts.evaluate_random` has unresolved history-path, Git-status and metric-output defects; use `scripts.evaluate_retrieval --dataset random` for this workflow.

The historical BM25 vs. Vector comparison from 2026-10-20 and its evidence limits are in the [baseline table](#en-8-historical-baseline-2026-10-20). Latency is retrieval-only; do not infer full-pipeline cost or response time from it. No TEST tuning.


<a id="en-7-governance-references"></a>

## 7. Governance references

Read [EVAL_CURATOR_AGENT.md](EVAL_CURATOR_AGENT.md), [project agent rules](PROJECT_AGENTS.md), the [repository-wide AGENTS.md](AGENTS.md), [OPERATIONS.md](OPERATIONS.md) and `.github/workflows/eval-governance.yml` (repository root). Respect human approval boundaries even when a validation script passes.

<a id="en-8-historical-baseline-2026-10-20"></a>

## 8. Historical baseline — 2026-10-20

| Dataset | Retriever | MRR | Hit@1 | Hit@3 | Hit@5 | Hit@8 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DEV (20) | BM25 | 0.7171 | 0.60 | 0.80 | 0.85 | 0.90 |
| DEV (20) | Vector | 0.8321 | 0.75 | 0.90 | 0.90 | 0.95 |
| RANDOM (25) | BM25 | 0.8133 | 0.72 | 0.92 | 0.92 | 0.92 |
| RANDOM (25) | Vector | 0.6050 | 0.44 | 0.72 | 0.80 | 0.84 |

MRR is recorded in the [learning log](LEARNING_LOG.md#en-2026-10-20--phase-34-retrieval-evaluation). Hit@K values come from an earlier working report and cannot be independently confirmed without its original JSONL runs. The original runs, corpus and index are not bundled with this public snapshot; the values were not reproduced for this documentation update. These are retrieval metrics, not generated-answer accuracy. Changes to data or environment may change the results. Short-run retrieval latency is not a final operational benchmark. TEST remains held out.

[↑ Back to top](#top)
