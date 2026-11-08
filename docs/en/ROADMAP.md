<a id="top"></a>

# AI RAG Project Roadmap

[Česky](../cs/ROADMAP.md#cz) · [English](#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Contents — click to expand</summary>

- [Status snapshot — 2026-10-28](#en-status-snapshot--2026-10-28)
- [Current development focus](#en-current-development-focus)
- [Reading and updating the approved plan](#en-reading-and-updating-the-approved-plan)
- [PHASE 1 - Functional RAG Skeleton](#en-phase-1---functional-rag-skeleton)
- [PHASE 2 - Evaluation Foundation](#en-phase-2---evaluation-foundation)
- [PHASE 2A - Universal Document Explorer](#en-phase-2a---universal-document-explorer)
- [PHASE 2A.0 - Architecture Freeze](#en-phase-2a0---architecture-freeze)
- [PHASE 2A.1 - Data Models](#en-phase-2a1---data-models)
- [PHASE 2A.2 - Text Processing](#en-phase-2a2---text-processing)
- [PHASE 2A.3 - Security Foundations](#en-phase-2a3---security-foundations)
- [PHASE 2A.4 - PDF Loading and PDF Validation](#en-phase-2a4---pdf-loading-and-pdf-validation)
- [PHASE 2A.5 - BM25 Index](#en-phase-2a5---bm25-index)
- [PHASE 2A.6 - Search Engine](#en-phase-2a6---search-engine)
- [PHASE 2A.7 - CLI](#en-phase-2a7---cli)
- [PHASE 2A.8 - Integration](#en-phase-2a8---integration)
- [PHASE 2B - Evaluation Data Models](#en-phase-2b---evaluation-data-models)
- [PHASE 2C - Retrieval Metrics](#en-phase-2c---retrieval-metrics)
- [PHASE 2D - Evaluation Runner and History](#en-phase-2d---evaluation-runner-and-history)
- [PHASE 2E - RANDOM Evaluation](#en-phase-2e---random-evaluation)
- [PHASE 2F - Complete Evaluation Dataset](#en-phase-2f---complete-evaluation-dataset)
- [PHASE 3 - Retrieval Refactor](#en-phase-3---retrieval-refactor)
- [PHASE 3.1 - Retrieval Models](#en-phase-31---retrieval-models)
- [PHASE 3.2 - Embeddings](#en-phase-32---embeddings)
- [PHASE 3.3 - Vector Search](#en-phase-33---vector-search)
- [PHASE 3.4 - Query Processing](#en-phase-34---query-processing)
- [PHASE 3.5 - Reranker](#en-phase-35---reranker)
- [PHASE 3.6 - Scoring](#en-phase-36---scoring)
- [PHASE 3.7 - Retrieval Service](#en-phase-37---retrieval-service)
- [PHASE 4 - API Hardening](#en-phase-4---api-hardening)
- [PHASE 4.1 - Application Lifecycle](#en-phase-41---application-lifecycle)
- [PHASE 4.2 - Routes](#en-phase-42---routes)
- [PHASE 4.3 - Dependency Injection](#en-phase-43---dependency-injection)
- [PHASE 4.4 - Errors](#en-phase-44---errors)
- [PHASE 4.5 - Middleware](#en-phase-45---middleware)
- [PHASE 5 - Production Engineering](#en-phase-5---production-engineering)
- [PHASE 5.1 - Linux / WSL2](#en-phase-51---linux--wsl2)
- [PHASE 5.2 - Structured Logging](#en-phase-52---structured-logging)
- [PHASE 5.3 - Runtime Metrics](#en-phase-53---runtime-metrics)
- [PHASE 5.4 - Docker Hardening](#en-phase-54---docker-hardening)
- [PHASE 5.5 - CI/CD](#en-phase-55---cicd)
- [PHASE 6 - Security](#en-phase-6---security)
- [PHASE 6.1 - Threat Modeling](#en-phase-61---threat-modeling)
- [PHASE 6.2 - Runtime Input Validation](#en-phase-62---runtime-input-validation)
- [PHASE 6.3 - Runtime Limits](#en-phase-63---runtime-limits)
- [PHASE 6.4 - Secrets](#en-phase-64---secrets)
- [PHASE 6.5 - Dependency Security](#en-phase-65---dependency-security)
- [PHASE 6.6 - Container Security](#en-phase-66---container-security)
- [PHASE 6.7 - HTTP Security](#en-phase-67---http-security)
- [PHASE 6.8 - RAG-Specific Security](#en-phase-68---rag-specific-security)
- [PHASE 7 - Production v1](#en-phase-7---production-v1)
- [PHASE 7.1 - Health and Readiness](#en-phase-71---health-and-readiness)
- [PHASE 7.2 - Production Smoke Test](#en-phase-72---production-smoke-test)
- [PHASE 7.3 - Documentation](#en-phase-73---documentation)
- [PHASE 8 - Expansion](#en-phase-8---expansion)
- [PHASE 8A - Agent Exploration](#en-phase-8a---agent-exploration)
- [PHASE 8B - SQL and ETL](#en-phase-8b---sql-and-etl)
- [PHASE 8C - MLOps](#en-phase-8c---mlops)
- [PHASE 8D - Advanced Agents](#en-phase-8d---advanced-agents)
- [Original planning estimates — historical](#en-original-planning-estimates--historical)
- [Planning history](#en-planning-history)

</details>

---

<a id="en"></a>

This document owns **what to build, phase order, goals and acceptance criteria**.
Use [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md) for how to implement/review work,
[ARCHITECTURE.md](ARCHITECTURE.md) for component boundaries and
[LEARNING_LOG.md](LEARNING_LOG.md) for dated work and learning evidence.


<a id="en-status-snapshot--2026-10-28"></a>

## Status snapshot — 2026-10-28

This is the current planning checkpoint, not a renumbering or replacement of the
approved phase specifications below. Completion of a milestone does not certify
all acceptance criteria of its broader phase or production readiness.

| Milestone | Observed status | Evidence / procedure |
| --- | --- | --- |
| RAG API, PDF ingestion and Chroma storage | Implemented prototype; hardening remains planned | [Project README](PROJECT.md), [architecture](ARCHITECTURE.md) |
| Independent PDF page explorer | Implemented | `document_search/`, [operations](OPERATIONS.md) |
| Evidence-based retrieval evaluation | Implemented: metrics, history, latency and provenance | `evaluation/`, [evaluation guide](EVALUATION.md) |
| Chunk-level BM25 and Vector comparison | Implemented in the offline CLI on DEV/RANDOM | `app/retrievers/`, [recorded milestones](LEARNING_LOG.md#en-project-and-learning-history) |
| Hybrid lexical/semantic retrieval with RRF | Local work in progress; not a published CLI/API mode | [Uncommitted-work record](LEARNING_LOG.md#en-uncommitted-work-observed-on-2026-10-28) |
| Held-out TEST evaluation | Reserved for final assessment, not iterative tuning | [Evaluation policy](EVALUATION.md) |
| Bilingual runbooks and validator regressions | Integrated through [PR #3](https://github.com/jyenten/local_rag_api/pull/3) | [Operations](OPERATIONS.md), [evaluation](EVALUATION.md) |
| Dependency/security automation | Enabled; ChromaDB dependency findings remain open | `.github/workflows/`, [current project checkpoint](LEARNING_LOG.md#en-current-project-checkpoint) |

Detailed results and historical MRR/Hit@K belong to the evaluation guide and
learning log; this roadmap does not maintain a second benchmark table.


<a id="en-current-development-focus"></a>

## Current development focus

The next recorded development milestone is hybrid BM25 + Vector retrieval with
RRF. Complete and review the implementation, then measure DEV/RANDOM against the
preserved baselines before deciding on improvements. Keep TEST held out.
Separate local/backend experiments and unmerged dependency proposals remain
subject to their own review; their presence is not integration into `main` or
approval to replace the retrieval architecture.

The learning journal historically used labels such as Phase 3.3 for BM25,
Phase 3.4 for retrieval evaluation and Phase 3.5 for hybrid RRF. Those journal
labels are **not IDs in this roadmap**. Here, the original phase numbers and
names remain authoritative: 3.3 Vector Search, 3.4 Query Processing and
3.5 Reranker. Use the full milestone name when referring to journal work.


<a id="en-reading-and-updating-the-approved-plan"></a>

## Reading and updating the approved plan

The phase specifications below preserve the approved order, planned modules,
learning concepts and Definition of Done checklists. Their original **Status**,
estimates and unchecked boxes are a planning baseline, not a second live status
tracker. Use the snapshot above for observed progress; do not infer that an
existing module is missing just because an original checkbox remains unchecked.
Do not mark acceptance criteria satisfied without the necessary evidence.

The working method is **Complete → Measure → Improve**. Shared scope, backlog,
freeze, testing and review rules live in the
[development workflow](DEVELOPMENT_GUIDE.md#en-development-workflow), not here.
Changes to phase goals, priorities or acceptance criteria require an explicit
planning decision; editorial cleanup does not authorize them.

---


<a id="en-phase-1---functional-rag-skeleton"></a>

# PHASE 1 - Functional RAG Skeleton

**Status:** Mostly complete

**Estimated remaining work:** 2-4 hours

## Goal

Maintain a working end-to-end RAG application.

Core runtime pipeline:

```text
PDF documents
    ->
ingestion
    ->
text preprocessing
    ->
chunking
    ->
embeddings
    ->
ChromaDB
    ->
retrieval
    ->
reranking
    ->
context construction
    ->
generation
    ->
FastAPI response
```

The purpose of PHASE 1 is not architectural perfection.

The purpose is a working system that can later be measured and improved.

---

## 1.1 `app/config.py`

### Responsibilities

- application configuration
- model names
- Chroma collection configuration
- retrieval limits
- generation limits
- environment configuration

### Important concepts

- centralized configuration
- environment variables
- configuration validation
- Pydantic Settings

### Future direction

Configuration should eventually be loaded through a validated settings
object rather than duplicated constants.

Possible public access:

```python
get_settings()
```

---

## 1.2 `app/schemas.py`

### Current models

- `QuestionRequest`
- `SourceChunk`
- `AnswerResponse`

### Future possible models

- `ErrorResponse`
- `HealthResponse`

### Important concept

API schemas describe data crossing the HTTP boundary.

They should remain separate from internal retrieval models.

---

## 1.3 `app/retrieval.py`

### Current responsibilities

- embedding model loading
- query preparation
- Chroma retrieval
- candidate selection
- CrossEncoder reranking
- heuristic scoring
- result selection

### Current technical debt

This module currently contains multiple responsibilities and
domain-specific logic.

That is intentionally not refactored during PHASE 1.

Major retrieval refactoring belongs to:

```text
PHASE 3
```

---

## 1.4 `app/generation.py`

### Main responsibilities

- generator model loading
- prompt construction
- model inference
- answer generation

Core flow:

```text
question
+
retrieved context
    ->
prompt
    ->
generation model
    ->
answer
```

Possible future separation:

```text
prompt construction
model inference
output processing
```

This split should only be introduced if complexity requires it.

---

## 1.5 `app/rag.py`

### Responsibility

RAG orchestration.

Target conceptual flow:

```text
question
    ->
retrieval
    ->
context selection
    ->
generation
    ->
sources
    ->
final response
```

### Current technical debt

The current implementation contains OSPF-specific behavior.

Removal belongs to:

```text
PHASE 3
```

---

## 1.6 `app/main.py`

### Responsibility

FastAPI application entry point.

Current endpoints:

```text
GET /
GET /health
POST /ask
```

Target responsibility:

```text
HTTP request
    ->
validation
    ->
application service
    ->
HTTP response
```

Business logic should eventually move out of the API entry point.

---

## 1.7 `scripts/ingest.py`

### Current pipeline

```text
PDF
    ->
extract text
    ->
clean text
    ->
chunk
    ->
embed
    ->
store in ChromaDB
```

### Existing improvements

- PDF text cleanup
- URL protection/restoration
- word-based chunking
- chunk overlap
- overlap validation

### Important rule

Do not refactor ingestion only for architectural symmetry.

Refactor it only when:

- testing becomes difficult
- reuse is required
- complexity grows significantly
- evaluation exposes an ingestion problem

---

## PHASE 1 Definition of Done

- [x] PDF documents can be ingested
- [x] text extraction works
- [x] chunking works
- [x] embeddings can be generated
- [x] ChromaDB stores searchable chunks
- [x] retrieval works
- [x] reranking works
- [x] generation works
- [x] `POST /ask` works
- [x] responses contain source information
- [x] smoke tests pass
- [ ] remaining technical debt is documented

When these conditions are satisfied, PHASE 1 is frozen.

---


<a id="en-phase-2---evaluation-foundation"></a>

# PHASE 2 - Evaluation Foundation

**Status:** In progress

**Estimated remaining work:** 8-12 hours

## Goal

Create a reliable evaluation framework before major retrieval changes.

Retrieval should no longer be improved only by inspecting a few manually
selected questions.

Target development flow:

```text
baseline
    ->
evaluation
    ->
retrieval change
    ->
evaluation
    ->
comparison
```

---

## Evaluation Dataset Roles

Three dataset categories have intentionally different purposes.

### DEV

Used during development and tuning.

DEV results may influence implementation decisions.

Target size:

```text
approximately 20 manually validated questions
```

---

### RANDOM

Used for:

- robustness exploration
- unexpected failure discovery
- corpus coverage exploration

Random sampling must be reproducible through a stored seed.

RANDOM is not a replacement for TEST.

---

### TEST

Held-out final evaluation.

TEST should not be repeatedly inspected and tuned against.

Its purpose is to estimate generalization after tuning is complete.

---


<a id="en-phase-2a---universal-document-explorer"></a>

# PHASE 2A - Universal Document Explorer

**Status:** Current active subphase

**Estimated work:** 3-4 hours

## Goal

Build a reusable, domain-independent lexical corpus explorer used for:

- finding candidate evidence
- inspecting PDF content
- manually validating gold evidence
- helping construct DEV / RANDOM / TEST datasets

The explorer must continue to work if the entire PDF corpus is replaced.

Example future domains:

```text
Kubernetes
cybersecurity
Linux
law
manufacturing
accounting
networking
```

The explorer must not contain OSPF-specific ranking logic.

---

## Target Structure

```text
document_search/
|
+-- __init__.py
+-- models.py
+-- normalize.py
+-- tokenize.py
+-- load_pages.py
+-- build_index.py
+-- search.py
|
+-- security/
    +-- __init__.py
    +-- paths.py
    +-- pdf_validation.py
    +-- input_validation.py
```

CLI:

```text
scripts/
+-- search_pdf.py
```

Tests:

```text
tests/
+-- document_search/
    +-- test_models.py
    +-- test_normalize.py
    +-- test_tokenize.py
    +-- test_load_pages.py
    +-- test_build_index.py
    +-- test_search.py
```

---


<a id="en-phase-2a0---architecture-freeze"></a>

# PHASE 2A.0 - Architecture Freeze

## Goal

Before implementation, define:

- module responsibilities
- data models
- public interfaces
- dependency direction
- security boundaries
- Definition of Done

Documentation:

```text
docs/ROADMAP.md
docs/ARCHITECTURE.md
docs/DEVELOPMENT_GUIDE.md
```

No production code should be redesigned repeatedly while dependent modules
are already being implemented unless a concrete technical issue requires
it.

---


<a id="en-phase-2a1---data-models"></a>

# PHASE 2A.1 - Data Models

## File

```text
document_search/models.py
```

## Planned models

```python
PageDocument
SearchResult
BM25SearchIndex
```

### `PageDocument`

Conceptually:

```python
PageDocument(
    source="manual.pdf",
    page=26,
    text="...",
)
```

Represents one searchable source page.

---

### `SearchResult`

Conceptually:

```python
SearchResult(
    document=document,
    score=12.5,
)
```

Represents one ranked BM25 result.

---

### `BM25SearchIndex`

Owns:

```text
page corpus
+
BM25 model
```

This prevents callers from manually keeping those objects synchronized.

---

## New Concept - Immutable Dataclasses

Preferred pattern:

```python
@dataclass(frozen=True)
```

Benefits:

- prevents accidental mutation
- improves reasoning about state
- makes tests more predictable
- clearly represents factual data

Examples of immutable facts:

```text
source filename
page number
document text
completed search score
```

---


<a id="en-phase-2a2---text-processing"></a>

# PHASE 2A.2 - Text Processing

**Estimated work:** less than 1 hour

Because these modules are small and closely related, they may be
implemented together.

---

## File

```text
document_search/normalize.py
```

Main function:

```python
normalize_text(
    text: str,
) -> str
```

Responsibilities:

- lowercase normalization
- whitespace normalization
- generic text cleanup

Must not contain:

```text
OSPF terminology
Cisco rules
manual ranking boosts
domain-specific vocabulary
```

---

## File

```text
document_search/tokenize.py
```

Main function:

```python
tokenize(
    text: str,
) -> list[str]
```

Example:

```text
"OSPF calculates interface cost."
```

becomes approximately:

```python
[
    "ospf",
    "calculates",
    "interface",
    "cost",
]
```

---

## Important Concepts

- pure functions
- deterministic preprocessing
- reusable text processing
- separation between normalization and retrieval

---


<a id="en-phase-2a3---security-foundations"></a>

# PHASE 2A.3 - Security Foundations

**Estimated work:** approximately 1 hour

## Goal

Protect filesystem and user-controlled search inputs before PDF parsing
and ranking.

---

## File

```text
document_search/security/paths.py
```

Planned functions:

```python
resolve_safe_path(...)
validate_data_directory(...)
```

Responsibilities:

- allowed directory boundaries
- path traversal prevention
- resolved path validation
- symlink-aware checks

---

## New Concept - Path Traversal

Unsafe input example:

```text
../../private_file
```

A path that appears to be inside a directory may also resolve outside it
through a symbolic link.

Security therefore must validate resolved filesystem paths, not only the
original input string.

---

## File

```text
document_search/security/input_validation.py
```

Planned functions:

```python
validate_query(...)
validate_top_k(...)
```

Responsibilities:

- reject empty queries
- reject oversized queries
- reject invalid `top_k`
- prevent unreasonable resource requests

---

## New Concept - Validation Boundary

External input should be validated near the system boundary.

Internal functions can then operate on values that already satisfy the
expected contract.

---


<a id="en-phase-2a4---pdf-loading-and-pdf-validation"></a>

# PHASE 2A.4 - PDF Loading and PDF Validation

**Estimated work:** 1-2 hours

## File

```text
document_search/security/pdf_validation.py
```

Planned functions:

```python
validate_pdf_extension(...)
validate_pdf_signature(...)
validate_pdf_limits(...)
```

Responsibilities:

- verify `.pdf` extension
- verify that the file actually looks like a PDF
- enforce file size limits
- enforce page count limits

---

## New Concept - File Signature

A filename such as:

```text
document.pdf
```

does not prove that the file is actually a PDF.

Validation should inspect the file header/signature as well as the file
extension.

---

## New Concept - Resource Exhaustion

A valid-looking file may still consume unreasonable resources.

Examples:

```text
multi-gigabyte file
hundreds of thousands of pages
extremely large extracted text
```

Resource limits protect:

- RAM
- CPU
- latency
- service availability

---

## File

```text
document_search/load_pages.py
```

Main function:

```python
load_pdf_pages(
    data_dir: Path,
) -> list[PageDocument]
```

Core flow:

```text
data directory
    ->
discover PDF files
    ->
security validation
    ->
PdfReader
    ->
extract each page
    ->
PageDocument
```

Important rule:

The loader must not silently truncate documents.

If a file cannot be processed safely or completely, failure should be
explicit.

---


<a id="en-phase-2a5---bm25-index"></a>

# PHASE 2A.5 - BM25 Index

**Estimated work:** less than 1 hour

## File

```text
document_search/build_index.py
```

Main function:

```python
build_bm25_index(
    pages: list[PageDocument],
) -> BM25SearchIndex
```

External dependency:

```text
rank-bm25
```

---

## New Concept - BM25

BM25 is a standard lexical information retrieval algorithm.

It considers:

- term frequency
- inverse document frequency
- document length normalization

Conceptually:

```text
query terms
    +
how often they appear in a page
    +
how rare they are across the corpus
    +
page/document length
    ->
relevance score
```

This is preferable to hand-written ranking such as:

```text
neighbor = +1
DROTHER = +5
distance below 200 chars = +3
```

because BM25 ranking is derived from corpus statistics rather than
domain-specific manual heuristics.

---


<a id="en-phase-2a6---search-engine"></a>

# PHASE 2A.6 - Search Engine

**Estimated work:** approximately 1 hour

## File

```text
document_search/search.py
```

Public function:

```python
search_pages(
    index: BM25SearchIndex,
    query: str,
    top_k: int = 10,
) -> list[SearchResult]
```

Core flow:

```text
query
    ->
validation
    ->
tokenization
    ->
BM25 scores
    ->
descending ranking
    ->
TOP K
    ->
SearchResult
```

---

## Important New Concept - Public API Boundary

Other modules should use:

```python
search_pages(...)
```

without manually accessing:

```text
BM25 internals
page arrays
raw score arrays
sorting logic
```

This allows internal implementation to change without changing every
caller.

---


<a id="en-phase-2a7---cli"></a>

# PHASE 2A.7 - CLI

**Estimated work:** less than 1 hour

## File

```text
scripts/search_pdf.py
```

Planned functions:

```python
build_parser()
print_results()
select_result()
print_result_detail()
main()
```

Target usage:

```text
python -m scripts.search_pdf "how does OSPF calculate interface cost"
```

Optional:

```text
--top-k 5
```

The CLI should contain:

- argument parsing
- human-readable output
- interactive selection

It should not contain:

- BM25 implementation
- PDF parsing internals
- ranking heuristics

---


<a id="en-phase-2a8---integration"></a>

# PHASE 2A.8 - Integration

## Tasks

- add `rank-bm25` dependency
- run document-search unit tests
- run full project tests
- search real Cisco corpus
- inspect several result rankings manually
- verify generic behavior
- confirm no OSPF-specific ranking rules remain

---

## PHASE 2A Definition of Done

- [ ] arbitrary PDFs can be discovered
- [ ] filesystem boundaries are validated
- [ ] PDF extension is validated
- [ ] PDF signature is validated
- [ ] PDF resource limits exist
- [ ] pages are represented by typed data models
- [ ] normalization is domain-independent
- [ ] tokenization works
- [ ] BM25 index can be created
- [ ] arbitrary text queries can be ranked
- [ ] results expose source, page, score, and text
- [ ] CLI works
- [ ] relevant unit tests pass
- [ ] complete project tests pass
- [ ] no OSPF-specific ranking heuristics exist

Once these conditions are satisfied, PHASE 2A is frozen.

Out of scope:

```text
fuzzy retrieval
semantic document explorer
LLM reranking
query rewriting
synonym dictionaries
hybrid BM25 + embedding explorer
advanced UI
```

---


<a id="en-phase-2b---evaluation-data-models"></a>

# PHASE 2B - Evaluation Data Models

**Estimated work:** 1-2 hours

## Goal

Move reusable evaluation logic out of loose scripts and dictionaries into
typed project modules.

Target structure:

```text
evaluation/
|
+-- __init__.py
+-- models.py
+-- dataset.py
+-- evidence.py
+-- metrics.py
+-- runner.py
+-- history.py
+-- random_eval.py
```

---

## File

```text
evaluation/models.py
```

Planned models:

```python
GoldEvidence
EvaluationQuestion
QuestionResult
EvaluationMetrics
EvaluationRun
```

---

## New Concept - Typed Evaluation Models

Instead of:

```python
question["gold_evidence"][0]["source"]
```

prefer:

```python
question.gold_evidence
```

Benefits:

- clearer code
- better IDE support
- fewer key-name errors
- easier validation
- safer refactoring

---

## File

```text
evaluation/dataset.py
```

Planned functions:

```python
load_dataset(...)
validate_dataset(...)
calculate_dataset_hash(...)
```

Responsibilities:

- load DEV / TEST datasets
- schema validation
- dataset identity
- reproducibility

---

## New Concept - Dataset Hashing

A SHA256 hash can identify the exact dataset version used for an
evaluation run.

This prevents ambiguity such as:

```text
"MRR was 0.82 on the DEV dataset"
```

when the DEV dataset may have changed since the run.

Instead:

```text
dataset_hash = abc123...
MRR = 0.82
```

---

## File

```text
evaluation/evidence.py
```

Planned functions:

```python
normalize_evidence_text(...)
matches_gold_evidence(...)
find_gold_rank(...)
```

A valid evidence match should require:

```text
source
AND
page
AND
expected text fragment
```

within the same accepted evidence variant.

---


<a id="en-phase-2c---retrieval-metrics"></a>

# PHASE 2C - Retrieval Metrics

**Estimated work:** approximately 1 hour

## File

```text
evaluation/metrics.py
```

Planned functions:

```python
reciprocal_rank(...)
mean_reciprocal_rank(...)
hit_at_k(...)
aggregate_metrics(...)
```

---

## Metric - Hit@K

Question:

```text
Did the correct evidence appear in the first K results?
```

Examples:

```text
Hit@1
Hit@3
Hit@5
Hit@8
```

---

## Metric - Reciprocal Rank

If correct evidence appears at:

```text
rank 1 -> 1.0
rank 2 -> 0.5
rank 4 -> 0.25
```

Formula conceptually:

```text
1 / rank
```

---

## Metric - MRR

Mean Reciprocal Rank:

```text
average reciprocal rank
across all evaluation questions
```

MRR rewards systems that place relevant evidence near the top of the
ranking.

---


<a id="en-phase-2d---evaluation-runner-and-history"></a>

# PHASE 2D - Evaluation Runner and History

**Estimated work:** approximately 1 hour

## File

```text
evaluation/runner.py
```

Planned functions:

```python
evaluate_question(...)
evaluate_dataset(...)
build_run_metadata(...)
```

Conceptual flow:

```text
EvaluationQuestion
    ->
retrieval
    ->
ranked results
    ->
gold evidence matching
    ->
question metrics
```

---

## File

```text
evaluation/history.py
```

Planned functions:

```python
load_history(...)
append_run(...)
save_history(...)
```

Stored metadata should include:

- Git commit SHA
- dirty working-tree state
- dataset SHA256
- timestamp
- configuration
- evaluation metrics

Example:

```text
commit A
MRR = 0.71

commit B
MRR = 0.82
```

This allows retrieval changes to be compared with evidence.

---


<a id="en-phase-2e---random-evaluation"></a>

# PHASE 2E - RANDOM Evaluation

**Estimated work:** 2-3 hours

## File

```text
evaluation/random_eval.py
```

Possible functions:

```python
sample_pages(...)
build_random_sample(...)
save_seed(...)
```

---

## New Concept - Reproducible Randomness

Use a dedicated seeded random generator.

Example:

```python
random.Random(seed)
```

The same seed should produce the same sample.

This allows a surprising RANDOM failure to be reproduced later.

---

## RANDOM Purpose

RANDOM is intended for:

```text
robustness
coverage
failure discovery
```

It is not intended for:

```text
final generalization claims
```

That remains the role of TEST.

---


<a id="en-phase-2f---complete-evaluation-dataset"></a>

# PHASE 2F - Complete Evaluation Dataset

**Estimated work:** included in PHASE 2 estimate

## Tasks

- expand DEV to approximately 20 questions
- manually validate gold evidence
- diversify question topics
- implement RANDOM workflow
- create TEST dataset
- freeze TEST dataset
- document dataset roles

---

## PHASE 2 Definition of Done

- [ ] universal BM25 document explorer complete
- [ ] DEV dataset sufficiently broad
- [ ] DEV gold evidence manually validated
- [ ] RANDOM workflow implemented
- [ ] RANDOM runs reproducible
- [ ] TEST dataset created
- [ ] TEST dataset frozen
- [ ] MRR implemented
- [ ] Hit@1 implemented
- [ ] Hit@3 implemented
- [ ] Hit@5 implemented
- [ ] Hit@8 implemented
- [ ] dataset hashing implemented
- [ ] Git metadata recorded
- [ ] evaluation history available
- [ ] evaluation tests pass

After PHASE 2, evaluation infrastructure is frozen unless a concrete
measurement problem appears.

---


<a id="en-phase-3---retrieval-refactor"></a>

# PHASE 3 - Retrieval Refactor

**Status:** Planned

**Estimated work:** 8-14 hours

## Goal

Refactor the main RAG retrieval system only after reliable evaluation is
available.

Current large module:

```text
app/retrieval.py
```

Target structure:

```text
app/
+-- retrieval/
    +-- __init__.py
    +-- models.py
    +-- embeddings.py
    +-- vector_search.py
    +-- query.py
    +-- reranker.py
    +-- scoring.py
    +-- service.py
```

---


<a id="en-phase-31---retrieval-models"></a>

# PHASE 3.1 - Retrieval Models

## File

```text
app/retrieval/models.py
```

Planned models:

```python
RetrievedChunk
ScoredChunk
RetrievalResult
```

Purpose:

replace loosely structured dictionaries/tuples with explicit internal
retrieval data types.

---


<a id="en-phase-32---embeddings"></a>

# PHASE 3.2 - Embeddings

## File

```text
app/retrieval/embeddings.py
```

Planned functions:

```python
load_embedding_model(...)
embed_query(...)
embed_documents(...)
```

Responsibility:

embedding operations only.

Must not:

- communicate with FastAPI
- decide ranking
- format API responses

---


<a id="en-phase-33---vector-search"></a>

# PHASE 3.3 - Vector Search

## File

```text
app/retrieval/vector_search.py
```

Planned functions:

```python
search_vector_store(...)
convert_chroma_results(...)
```

Responsibility:

communication with ChromaDB.

Important architectural rule:

Higher layers should not depend directly on Chroma's response structure.

---


<a id="en-phase-34---query-processing"></a>

# PHASE 3.4 - Query Processing

## File

```text
app/retrieval/query.py
```

Possible function:

```python
normalize_query(...)
```

Potential future query expansion is allowed only if DEV evaluation shows
a measurable benefit.

Domain-specific hardcoding should be removed.

---


<a id="en-phase-35---reranker"></a>

# PHASE 3.5 - Reranker

## File

```text
app/retrieval/reranker.py
```

Planned functions:

```python
load_reranker(...)
rerank(...)
```

Core flow:

```text
query
+
candidate chunk
    ->
CrossEncoder
    ->
relevance score
```

---


<a id="en-phase-36---scoring"></a>

# PHASE 3.6 - Scoring

## File

```text
app/retrieval/scoring.py
```

Goal:

remove pathological score combinations.

Current known issue:

```text
raw CrossEncoder score
+
large heuristic bonus
```

can cause the heuristic scale to dominate model relevance.

Possible approaches to evaluate:

- pure CrossEncoder ranking
- normalized score combination
- rank fusion

Choice must be driven by DEV metrics.

---

## New Concept - Rank Fusion

Instead of directly adding incompatible raw scores, ranking systems may
combine relative rank positions.

This avoids some score-scale problems.

It should only be introduced if evaluation justifies it.

---


<a id="en-phase-37---retrieval-service"></a>

# PHASE 3.7 - Retrieval Service

## File

```text
app/retrieval/service.py
```

Target public API:

```python
retrieve(
    query: str,
) -> list[RetrievalResult]
```

Pipeline:

```text
query
    ->
vector search
    ->
candidate set
    ->
reranking
    ->
score handling
    ->
TOP K
```

Higher-level code should primarily call this public interface.

---

## PHASE 3 Definition of Done

- [ ] OSPF-specific retrieval hardcoding removed
- [ ] retrieval data models exist
- [ ] embedding responsibility separated
- [ ] Chroma responsibility separated
- [ ] reranking separated
- [ ] scoring isolated
- [ ] stable retrieval public API exists
- [ ] baseline metrics recorded
- [ ] refactored retrieval evaluated on DEV
- [ ] retrieval regression tests pass
- [ ] TEST is not used during tuning
- [ ] final TEST run performed after tuning

---


<a id="en-phase-4---api-hardening"></a>

# PHASE 4 - API Hardening

**Status:** Planned

**Estimated work:** 5-8 hours

## Goal

Turn the existing FastAPI wrapper into a more production-like application
boundary.

Target structure:

```text
app/
|
+-- main.py
+-- lifecycle.py
|
+-- api/
    +-- __init__.py
    +-- routes.py
    +-- dependencies.py
    +-- errors.py
    +-- middleware.py
```

---


<a id="en-phase-41---application-lifecycle"></a>

# PHASE 4.1 - Application Lifecycle

## File

```text
app/lifecycle.py
```

Main function:

```python
lifespan(...)
```

Responsibilities:

```text
startup
->
load models
load vector store
initialize services

shutdown
->
release resources
```

---

## New Concept - FastAPI Lifespan

Expensive models should normally be initialized once during application
startup rather than independently for every request.

Benefits:

- lower latency
- lower memory overhead
- clearer resource lifecycle
- easier startup failure detection

---


<a id="en-phase-42---routes"></a>

# PHASE 4.2 - Routes

## File

```text
app/api/routes.py
```

Responsibilities:

```text
GET /health
POST /ask
```

Routes translate:

```text
HTTP
<->
application services
```

They should not contain retrieval implementation.

---


<a id="en-phase-43---dependency-injection"></a>

# PHASE 4.3 - Dependency Injection

## File

```text
app/api/dependencies.py
```

Possible functions:

```python
get_settings(...)
get_rag_service(...)
```

---

## New Concept - Dependency Injection

Instead of creating dependencies inside every endpoint, FastAPI can
provide them.

Benefits:

- easier testing
- reduced global state
- replaceable services
- clearer ownership

---


<a id="en-phase-44---errors"></a>

# PHASE 4.4 - Errors

## File

```text
app/api/errors.py
```

Possible exceptions:

```python
InvalidQueryError
RetrievalError
GenerationError
```

Also:

```text
FastAPI exception handlers
```

Goal:

convert internal failures into controlled structured HTTP responses.

---


<a id="en-phase-45---middleware"></a>

# PHASE 4.5 - Middleware

## File

```text
app/api/middleware.py
```

Responsibilities may include:

- request ID
- request timing
- basic HTTP logging

---

## PHASE 4 Definition of Done

- [ ] models initialize once
- [ ] application lifecycle defined
- [ ] routes separated from business logic
- [ ] dependency injection used where appropriate
- [ ] structured application errors exist
- [ ] request IDs exist
- [ ] API timing available
- [ ] health endpoint defined
- [ ] readiness semantics defined
- [ ] API integration tests pass

---


<a id="en-phase-5---production-engineering"></a>

# PHASE 5 - Production Engineering

**Status:** Planned

**Estimated work:** 10-16 hours

## Goal

Make the system reproducible, observable, containerized, and deployable.

This phase includes Python code and infrastructure work.

---


<a id="en-phase-51---linux--wsl2"></a>

# PHASE 5.1 - Linux / WSL2

## Goal

Validate that the application works outside the Windows development
environment.

Tasks:

- create Linux/WSL2 environment
- install dependencies
- run unit tests
- run ingestion
- run API
- verify filesystem assumptions
- verify model loading

---

## New Concept - Environment Portability

A system that only runs in one local development environment is not yet
reproducible.

Linux compatibility also prepares the project for Docker and cloud
deployment.

---


<a id="en-phase-52---structured-logging"></a>

# PHASE 5.2 - Structured Logging

Target structure:

```text
app/
+-- observability/
    +-- __init__.py
    +-- logging.py
    +-- metrics.py
    +-- middleware.py
```

---

## File

```text
app/observability/logging.py
```

Planned functions:

```python
configure_logging(...)
get_logger(...)
```

---

## New Concept - Structured Logging

Instead of only:

```text
"Retrieval finished"
```

a structured event may contain:

```text
event = retrieval_complete
request_id = ...
latency_ms = 143
candidate_count = 30
```

Structured logs are easier to:

- search
- aggregate
- monitor
- analyze automatically

---


<a id="en-phase-53---runtime-metrics"></a>

# PHASE 5.3 - Runtime Metrics

## File

```text
app/observability/metrics.py
```

Possible functions:

```python
record_request(...)
record_latency(...)
record_retrieval_latency(...)
record_generation_latency(...)
record_error(...)
```

Operational metrics should include:

- request count
- error count
- response latency
- retrieval latency
- reranking latency
- generation latency

Where applicable later:

- token usage
- model usage
- API cost

---

## New Concept - Quality vs Operational Metrics

Quality metrics:

```text
MRR
Hit@K
answer groundedness
```

Operational metrics:

```text
latency
request count
error rate
resource usage
cost
```

A system can have high retrieval quality but poor production latency.

Both dimensions matter.

---


<a id="en-phase-54---docker-hardening"></a>

# PHASE 5.4 - Docker Hardening

Files:

```text
Dockerfile
compose.yaml
.dockerignore
```

Tasks:

- reproducible build
- correct dependency installation
- explicit configuration
- healthcheck
- non-root user
- reduce unnecessary image contents

---

## New Concept - Multi-stage Docker Build

A build stage can contain tools required only to build dependencies.

The final runtime image can contain only what is needed to run the
application.

Potential benefits:

- smaller image
- smaller attack surface
- cleaner runtime

Use only if it provides practical value for this project.

---


<a id="en-phase-55---cicd"></a>

# PHASE 5.5 - CI/CD

Current CI already runs project tests.

Future flow may become:

```text
push
    ->
tests
    ->
static checks
    ->
security checks
    ->
Docker build
    ->
deployment
```

Possible improvements:

- formatter check
- Ruff
- type checking
- coverage
- dependency scan

---

## PHASE 5 Definition of Done

- [ ] application works under Linux / WSL2
- [ ] Docker build is reproducible
- [ ] container starts successfully
- [ ] container healthcheck works
- [ ] non-root execution configured
- [ ] CI runs project tests
- [ ] structured logging exists
- [ ] request latency can be measured
- [ ] retrieval latency can be measured
- [ ] generation latency can be measured
- [ ] deployment process is defined

---


<a id="en-phase-6---security"></a>

# PHASE 6 - Security

**Status:** Planned

**Estimated work:** 6-10 hours

## Goal

Perform a dedicated security hardening review after the production
architecture exists.

Security is also considered during earlier phases, but PHASE 6 performs
the deeper review.

Target structure may include:

```text
app/
+-- security/
    +-- __init__.py
    +-- validation.py
    +-- limits.py
    +-- headers.py
```

---


<a id="en-phase-61---threat-modeling"></a>

# PHASE 6.1 - Threat Modeling

## New Concept - Threat Model

Explicitly identify:

```text
assets
trust boundaries
attack surfaces
possible attackers
failure modes
impact
mitigations
```

Example system boundaries:

```text
user
->
FastAPI

PDF corpus
->
PDF parser

environment variables
->
application configuration

RAG context
->
generation model
```

---


<a id="en-phase-62---runtime-input-validation"></a>

# PHASE 6.2 - Runtime Input Validation

## File

```text
app/security/validation.py
```

Possible functions:

```python
validate_query(...)
validate_input_size(...)
```

---


<a id="en-phase-63---runtime-limits"></a>

# PHASE 6.3 - Runtime Limits

## File

```text
app/security/limits.py
```

Possible limits:

```text
maximum query length
maximum context size
maximum top_k
maximum request size
```

Future possible rate limiting may be evaluated here.

---


<a id="en-phase-64---secrets"></a>

# PHASE 6.4 - Secrets

Tasks:

- verify no secrets committed to Git
- use environment variables
- define production secret strategy
- review `.env.example`
- avoid logging secrets

---


<a id="en-phase-65---dependency-security"></a>

# PHASE 6.5 - Dependency Security

Tasks may include:

- vulnerability scanning
- dependency review
- version pinning strategy
- security update process

---


<a id="en-phase-66---container-security"></a>

# PHASE 6.6 - Container Security

Review:

- non-root execution
- filesystem permissions
- exposed ports
- unnecessary packages
- writable directories
- secret injection
- attack surface

---


<a id="en-phase-67---http-security"></a>

# PHASE 6.7 - HTTP Security

Review:

- CORS
- security headers
- request limits
- error information leakage
- authentication requirements if introduced

---


<a id="en-phase-68---rag-specific-security"></a>

# PHASE 6.8 - RAG-Specific Security

## New Concept - Indirect Prompt Injection

A retrieved document may contain text such as:

```text
Ignore previous instructions...
```

The document itself becomes an untrusted model input.

Security review should consider:

- separation between instructions and retrieved data
- prompt construction
- source trust
- model behavior
- tool access in future agent systems

---

## PHASE 6 Definition of Done

- [ ] threat model documented
- [ ] input limits reviewed
- [ ] filesystem boundaries reviewed
- [ ] PDF handling reviewed
- [ ] dependency security reviewed
- [ ] secret handling reviewed
- [ ] container permissions reviewed
- [ ] non-root execution verified
- [ ] HTTP controls reviewed
- [ ] indirect prompt injection reviewed
- [ ] major mitigations documented

---


<a id="en-phase-7---production-v1"></a>

# PHASE 7 - Production v1

**Status:** Planned

**Estimated work:** 4-6 hours

## Goal

Integrate all completed layers into the first production-style release.

Production v1 does not mean enterprise completeness.

It means the project is:

```text
reproducible
tested
deployable
observable
documented
reasonably hardened
```

---


<a id="en-phase-71---health-and-readiness"></a>

# PHASE 7.1 - Health and Readiness

Possible file:

```text
app/health.py
```

Possible functions:

```python
check_vector_store(...)
check_models(...)
build_readiness_status(...)
```

---

## New Concept - Liveness vs Readiness

### Liveness

Question:

```text
Is the process alive?
```

### Readiness

Question:

```text
Can the application actually serve a valid RAG request?
```

An application may be alive while its model or vector store is not ready.

---


<a id="en-phase-72---production-smoke-test"></a>

# PHASE 7.2 - Production Smoke Test

## File

```text
scripts/production_smoke.py
```

Possible flow:

```text
health check
    ->
known question
    ->
validate HTTP response
    ->
validate answer structure
    ->
validate sources
    ->
record latency
```

---


<a id="en-phase-73---documentation"></a>

# PHASE 7.3 - Documentation

README should explain:

- project purpose
- architecture summary
- installation
- environment setup
- ingestion
- running API
- running tests
- Docker usage
- evaluation usage
- security considerations

Links:

```text
docs/ROADMAP.md
docs/ARCHITECTURE.md
docs/DEVELOPMENT_GUIDE.md
```

---

## PHASE 7 Definition of Done

A fresh environment can:

- [ ] clone the repository
- [ ] configure environment variables
- [ ] install/build dependencies
- [ ] start the application
- [ ] ingest a corpus
- [ ] query the API
- [ ] receive a grounded answer with sources
- [ ] run tests
- [ ] run evaluation
- [ ] produce structured logs
- [ ] expose runtime metrics
- [ ] follow documented setup instructions

At this point the project reaches:

```text
Production v1
```

---


<a id="en-phase-8---expansion"></a>

# PHASE 8 - Expansion

PHASE 8 begins only after Production v1.

The purpose is to expand skills and system capabilities without
destabilizing the core RAG project.

---


<a id="en-phase-8a---agent-exploration"></a>

# PHASE 8A - Agent Exploration

**Estimated work:** 4-6 hours

## Goal

Demonstrate the transition from a normal RAG application to an agentic
workflow.

The first agent should use the existing RAG system as a tool.

Target structure:

```text
agent/
|
+-- __init__.py
+-- models.py
+-- tools.py
+-- agent.py
```

---

## File

```text
agent/tools.py
```

Example function:

```python
search_knowledge_base(
    question: str,
)
```

Possible implementation:

```text
agent
    ->
FastAPI /ask
```

or:

```text
agent
    ->
RAG service
```

---

## New Concept - Tool Calling

A language model no longer only generates text.

It can decide:

```text
which tool to use
which arguments to provide
how to use the tool result
```

Example flow:

```text
user request
    ->
model decision
    ->
tool call
    ->
RAG system
    ->
tool result
    ->
final response
```

---

## PHASE 8A Definition of Done

- [ ] one agent exists
- [ ] agent can call the existing RAG system
- [ ] tool arguments are structured
- [ ] tool result returns to the model
- [ ] agent behavior is testable
- [ ] scope remains intentionally small

---


<a id="en-phase-8b---sql-and-etl"></a>

# PHASE 8B - SQL and ETL

**Estimated work:** 6-10 hours

## Goal

Add practical data-engineering foundations after the production RAG
system is complete.

Target structure:

```text
data_pipeline/
|
+-- __init__.py
+-- database.py
+-- extract.py
+-- transform.py
+-- load.py
+-- pipeline.py
```

---

## File

```text
data_pipeline/database.py
```

Concepts:

```text
database connections
SELECT
JOIN
GROUP BY
indexes
transactions
```

---

## File

```text
data_pipeline/extract.py
```

Possible function:

```python
extract_from_source(...)
```

---

## File

```text
data_pipeline/transform.py
```

Possible functions:

```python
clean_records(...)
transform_records(...)
validate_records(...)
```

---

## File

```text
data_pipeline/load.py
```

Possible function:

```python
load_to_database(...)
```

---

## New Concept - ETL

ETL means:

```text
Extract
    ->
Transform
    ->
Load
```

It represents a common data-engineering pipeline pattern.

---

## PHASE 8B Definition of Done

- [ ] basic SQL workflow implemented
- [ ] data can be extracted
- [ ] data can be transformed
- [ ] validation exists
- [ ] transformed data can be loaded
- [ ] simple end-to-end ETL pipeline works

---


<a id="en-phase-8c---mlops"></a>

# PHASE 8C - MLOps

**Estimated work:** 8-12 hours

## Goal

Introduce systematic experiment and model tracking.

Possible structure:

```text
mlops/
|
+-- __init__.py
+-- experiment.py
+-- artifacts.py
+-- model_metadata.py
```

---

## File

```text
mlops/experiment.py
```

Experiment records should contain:

- model
- model parameters
- retrieval configuration
- dataset hash
- Git commit
- timestamp
- quality metrics
- operational metrics
- cost metrics where applicable

---

## New Concept - Experiment Tracking

Instead of:

```text
"This version seemed better."
```

store:

```text
commit = abc123
dataset_hash = xyz456
embedding_model = ...
reranker = ...
MRR = 0.84
Hit@3 = 0.93
latency = 190 ms
```

Possible future technology:

```text
MLflow
```

A simpler local experiment tracker may be implemented first.

---

## File

```text
mlops/artifacts.py
```

Possible responsibilities:

- evaluation artifacts
- model metadata
- configuration snapshots
- run outputs

---

## PHASE 8C Definition of Done

- [ ] experiments have unique identity
- [ ] dataset version is recorded
- [ ] Git commit is recorded
- [ ] model configuration is recorded
- [ ] quality metrics are recorded
- [ ] operational metrics are recorded
- [ ] runs can be compared

---


<a id="en-phase-8d---advanced-agents"></a>

# PHASE 8D - Advanced Agents

**Status:** Future

Detailed architecture is intentionally deferred.

Possible topics:

- multiple tools
- persistent state
- planning
- workflow graphs
- human approval
- agent evaluation
- multi-agent coordination

Potential technologies should be selected only after the simpler agent
workflow is understood.

This phase must not be designed prematurely.

---


<a id="en-original-planning-estimates--historical"></a>

# Original planning estimates — historical

These values are preserved from the original plan. They are not a current
remaining-work forecast or a delivery commitment; reassessment requires a
separate planning decision.

Original active-development estimates (not recalculated):

| Phase | Estimated time |
|---|---:|
| PHASE 1 completion | 2-4 h |
| PHASE 2 evaluation foundation | 8-12 h |
| PHASE 3 retrieval refactor | 8-14 h |
| PHASE 4 API hardening | 5-8 h |
| PHASE 5 production engineering | 10-16 h |
| PHASE 6 security | 6-10 h |
| PHASE 7 Production v1 | 4-6 h |
| PHASE 8A agent exploration | 4-6 h |
| PHASE 8B SQL / ETL | 6-10 h |
| PHASE 8C MLOps | 8-12 h |

Original estimate of remaining effort to Production v1:

```text
43-70 hours
```

These estimates include:

- implementation
- explanation
- manual code entry
- testing
- debugging
- integration

They are not pure typing estimates.

---


<a id="en-planning-history"></a>

## Planning history

The previous Phase 2A status and step-by-step immediate-task list are retained in
[the pre-cleanup roadmap revision](https://github.com/jyenten/local_rag_api/blob/d7c3b4f71711c798646bd0a878b96b9c46c92d93/rag_api_project/docs/ROADMAP.md#historical-project-status-original-phase-2a-plan).
They describe an earlier checkpoint, not today's next steps. Completed work is
recorded in [LEARNING_LOG.md](LEARNING_LOG.md); the current focus belongs
only to this roadmap's [current development focus](#en-current-development-focus).

[↑ Back to top](#top)
