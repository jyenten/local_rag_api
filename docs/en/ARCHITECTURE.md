<a id="top"></a>

# AI RAG Project Architecture

[Česky](../cs/ARCHITECTURE.md#cz) · [English](#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Contents — click to expand</summary>

- [Current implementation snapshot (2026-10-28)](#en-current-implementation-snapshot-2026-10-28)
- [Identity and evaluation boundary](#en-identity-and-evaluation-boundary)
- [1. Purpose](#en-1-purpose)
- [2. Architectural Principles](#en-2-architectural-principles)
- [3. High-Level System Architecture](#en-3-high-level-system-architecture)
- [4. Offline Data Pipeline](#en-4-offline-data-pipeline)
- [5. Runtime Application](#en-5-runtime-application)
- [6. Target Retrieval Architecture](#en-6-target-retrieval-architecture)
- [7. Generation Architecture](#en-7-generation-architecture)
- [8. RAG Orchestration](#en-8-rag-orchestration)
- [9. API Architecture](#en-9-api-architecture)
- [10. Evaluation Architecture](#en-10-evaluation-architecture)
- [11. Evaluation Dataset Roles](#en-11-evaluation-dataset-roles)
- [12. Evaluation Flow](#en-12-evaluation-flow)
- [13. Universal Document Explorer](#en-13-universal-document-explorer)
- [14. Document Explorer Data Flow](#en-14-document-explorer-data-flow)
- [15. Document Search Models](#en-15-document-search-models)
- [16. Document Explorer Security Boundary](#en-16-document-explorer-security-boundary)
- [17. Security Architecture](#en-17-security-architecture)
- [18. Observability Architecture](#en-18-observability-architecture)
- [19. Testing Architecture](#en-19-testing-architecture)
- [20. Infrastructure Architecture](#en-20-infrastructure-architecture)
- [21. Dependency Direction](#en-21-dependency-direction)
- [22. Public Interfaces](#en-22-public-interfaces)
- [23. Current Technical Debt](#en-23-current-technical-debt)
- [24. Target Project Structure](#en-24-target-project-structure)
- [25. Architecture Change Rule](#en-25-architecture-change-rule)
- [26. Historical Phase 2A Architectural Focus](#en-26-historical-phase-2a-architectural-focus)

</details>

---

<a id="en"></a>

<a id="en-current-implementation-snapshot-2026-10-28"></a>

## Current implementation snapshot (2026-10-28)

The sections marked **target** below describe planned design, not necessarily shipped code. The default `main` branch currently contains:

- Runtime: `app/main.py`, `app/rag.py`, `app/retrieval.py` for the existing FastAPI RAG path.
- Experiment retrievers: `app/retrievers/vector.py` and `app/retrievers/bm25.py` over the same Chroma collection.
- Offline evaluation: `scripts/evaluate_retrieval.py` selects `legacy`, `vector` or `bm25` on DEV/RANDOM.
- Evidence: `evaluation/evidence.py`, `evaluation/candidates.py`, approved JSON datasets and independent page-based `scripts/search_pdf.py`.
- Hybrid RRF is **in progress** and is not yet an established selectable CLI or `/ask` mode.
- PDF ingestion `scripts/ingest.py` **deletes and recreates** its target Chroma collection.

Architecture boundaries: the standalone page explorer is not the chunk-level BM25 retriever; retrieval evaluation is independent of the HTTP answer pipeline; no raw BM25 relevance score may be added directly to vector distances. The separate bilingual [OPERATIONS.md](OPERATIONS.md) and [EVALUATION.md](EVALUATION.md) contain verified commands and golden-evidence governance.


<a id="en-identity-and-evaluation-boundary"></a>

## Identity and evaluation boundary

A Chroma chunk has an `id` distinct from `chunk_index`. `source`, physical `page` and chunk metadata preserve provenance. Planned hybrid fusion should match the same chunk by stable Chroma ID, not by text equality or page number alone. When changes to retrieval ranking or chunk identity are introduced, compare DEV and RANDOM results under controlled corpus/configuration and keep TEST held out.

---



<a id="en-1-purpose"></a>

## 1. Purpose

This document describes the architecture of the AI RAG project.

It defines:

- major system components
- module responsibilities
- dependency boundaries
- public interfaces between subsystems
- data flow
- evaluation architecture
- security boundaries
- future target structure

The architecture should remain domain-independent wherever possible.

Domain-specific behavior must not be embedded into generic retrieval,
evaluation, document loading, or infrastructure components.

---


<a id="en-2-architectural-principles"></a>

## 2. Architectural Principles

The project follows the architectural principles described below.

### 2.1 Separation of Concerns

Each module should have one primary responsibility.

Examples:

```text
PDF loading
≠
text normalization
≠
retrieval
≠
reranking
≠
generation
≠
API transport
```

A module should not contain unrelated responsibilities simply because
they are currently used together.

---

### 2.2 Explicit Module Boundaries

Higher-level modules should interact with lower-level subsystems through
defined public interfaces.

Preferred:

```text
RAG service
    ↓
retrieval service
    ↓
retrieval internals
```

Not preferred:

```text
RAG service
    ↓
embedding model
    ↓
ChromaDB internals
    ↓
reranker internals
    ↓
scoring helpers
```

The caller should not need to understand implementation details of the
subsystem it uses.

---

### 2.3 Domain Independence

Generic infrastructure must not depend on OSPF-specific terms or rules.

For example, generic components must not contain hardcoded logic for:

```text
OSPF
DROTHER
designated router
virtual links
Cisco-specific terminology
```

Such terms may appear in:

- source documents
- evaluation datasets
- user queries

but not in generic ranking or infrastructure code.

---

### 2.4 Prefer Immutable Data

Data objects that represent facts should be immutable whenever practical.

Examples:

```text
PageDocument
SearchResult
RetrievedChunk
EvaluationQuestion
GoldEvidence
```

Preferred implementation:

```python
@dataclass(frozen=True)
```

This reduces accidental state changes and makes the system easier to
reason about and test.

---

### 2.5 Configuration Outside Business Logic

Configuration should be centralized.

Examples:

```text
model names
retrieval limits
collection names
file limits
API settings
security limits
```

Business logic should not contain duplicated hardcoded configuration.

---

### 2.6 Measure Before Optimizing

Retrieval changes must be evaluated using the evaluation framework.

The project should not introduce ranking heuristics only because they
appear useful for one manually inspected query.

Development flow:

```text
baseline
    ↓
measurement
    ↓
change
    ↓
measurement
    ↓
comparison
```

---


<a id="en-3-high-level-system-architecture"></a>

## 3. High-Level System Architecture

The main runtime architecture is:

```text
                         USER / CLIENT
                              │
                              ▼
                           FastAPI
                              │
                              ▼
                         RAG SERVICE
                              │
                ┌─────────────┴─────────────┐
                │                           │
                ▼                           ▼
         RETRIEVAL SERVICE              GENERATION
                │                           │
                ▼                           │
         VECTOR RETRIEVAL                   │
                │                           │
                ▼                           │
            RERANKING                       │
                │                           │
                ▼                           │
       SELECTED CONTEXT ────────────────────┘
                │
                ▼
          FINAL RESPONSE
                │
                ▼
        ANSWER + SOURCES
```

The runtime application does not directly depend on the evaluation
system or the document explorer.

---


<a id="en-4-offline-data-pipeline"></a>

## 4. Offline Data Pipeline

The ingestion pipeline is separate from online query processing.

```text
PDF DOCUMENTS
      │
      ▼
TEXT EXTRACTION
      │
      ▼
PREPROCESSING
      │
      ▼
CHUNKING
      │
      ▼
EMBEDDING
      │
      ▼
VECTOR STORE
   ChromaDB
```

Current implementation:

```text
scripts/ingest.py
```

Future refactoring may split ingestion into additional modules, but this
is not required until measurements or complexity justify it.

---


<a id="en-5-runtime-application"></a>

## 5. Runtime Application

Current application structure:

```text
app/
├── __init__.py
├── config.py
├── generation.py
├── main.py
├── rag.py
├── retrieval.py
└── schemas.py
```

Current responsibilities are described below.

---

### 5.1 `app/config.py`

Owns application configuration.

Examples:

```text
embedding model
reranker model
generation model
Chroma collection
candidate count
returned result count
context limits
```

Target rule:

Other modules should read configuration rather than duplicate constants.

---

### 5.2 `app/schemas.py`

Owns external API data schemas.

Examples:

```text
QuestionRequest
SourceChunk
AnswerResponse
```

These schemas describe data exchanged across the HTTP boundary.

They are separate from internal retrieval models.

For example:

```text
API SourceChunk
```

does not need to be identical to:

```text
internal RetrievalResult
```

---

### 5.3 `app/retrieval.py`

Current retrieval implementation.

Current responsibilities include several concerns:

```text
query processing
embedding retrieval
candidate selection
reranking
heuristic scoring
result selection
```

This file remains operational alongside the experiment retrievers in `app/retrievers/`.

The approved PHASE 3 target proposes decomposition into:

```text
app/
└── retrieval/
    ├── __init__.py
    ├── models.py
    ├── embeddings.py
    ├── vector_search.py
    ├── query.py
    ├── reranker.py
    ├── scoring.py
    └── service.py
```

The final public entry point should be located in:

```text
app/retrieval/service.py
```

with an interface similar to:

```python
retrieve(
    query: str,
) -> list[RetrievalResult]
```

---


<a id="en-6-target-retrieval-architecture"></a>

## 6. Target Retrieval Architecture

The planned retrieval flow is:

```text
QUERY
  │
  ▼
query.py
normalize / prepare query
  │
  ▼
embeddings.py
query embedding
  │
  ▼
vector_search.py
retrieve candidate chunks
  │
  ▼
reranker.py
CrossEncoder scoring
  │
  ▼
scoring.py
optional score combination
  │
  ▼
service.py
select TOP K results
  │
  ▼
RetrievalResult
```

Each layer has one primary responsibility.

---

### 6.1 `retrieval/models.py`

Internal retrieval data models.

Planned types:

```text
RetrievedChunk
ScoredChunk
RetrievalResult
```

These models represent internal retrieval data and should not depend on
FastAPI.

---

### 6.2 `retrieval/embeddings.py`

Owns embedding-model operations.

Functions may include:

```python
load_embedding_model()
embed_query()
embed_documents()
```

This module must not know how FastAPI works.

It should also not decide final ranking.

---

### 6.3 `retrieval/vector_search.py`

Owns communication with the vector store.

Functions may include:

```python
search_vector_store()
convert_chroma_results()
```

Chroma-specific result formats should be converted into project-owned
data models here.

Higher layers should not depend directly on Chroma response structure.

---

### 6.4 `retrieval/query.py`

Owns generic query preparation.

Possible functions:

```python
normalize_query()
```

Query expansion may only be added if evaluation demonstrates a measurable
benefit.

Domain-specific expansion rules must not be hardcoded into the generic
retrieval layer.

---

### 6.5 `retrieval/reranker.py`

Owns CrossEncoder reranking.

Functions:

```python
load_reranker()
rerank()
```

Input:

```text
query
+
candidate chunks
```

Output:

```text
scored candidates
```

---

### 6.6 `retrieval/scoring.py`

Owns score combination if score fusion is required.

This layer exists specifically to prevent scoring rules from being
distributed throughout the retrieval pipeline.

Any combination of:

```text
vector score
CrossEncoder score
other retrieval score
```

must account for score scale and meaning.

Raw incompatible scores must not simply be added together.

---

### 6.7 `retrieval/service.py`

Public retrieval interface.

It orchestrates retrieval internals:

```text
query
↓
candidate retrieval
↓
reranking
↓
score handling
↓
TOP K
```

Other application layers should primarily depend on this service rather
than individual retrieval internals.

---


<a id="en-7-generation-architecture"></a>

## 7. Generation Architecture

Current file:

```text
app/generation.py
```

Current responsibility:

```text
question
+
retrieved context
↓
prompt
↓
generation model
↓
answer
```

Possible future internal separation:

```text
prompt construction
model inference
output processing
```

This split should only be introduced if complexity justifies it.

---


<a id="en-8-rag-orchestration"></a>

## 8. RAG Orchestration

Current file:

```text
app/rag.py
```

The RAG layer coordinates other services.

Target responsibility:

```text
question
    │
    ▼
retrieval service
    │
    ▼
context construction
    │
    ▼
generation service
    │
    ▼
answer + sources
```

The RAG layer must not implement:

```text
vector search details
embedding internals
CrossEncoder internals
Chroma response parsing
HTTP transport
```

Its role is orchestration.

---


<a id="en-9-api-architecture"></a>

## 9. API Architecture

Current entry point:

```text
app/main.py
```

Target PHASE 4 structure:

```text
app/
├── main.py
├── lifecycle.py
│
└── api/
    ├── __init__.py
    ├── routes.py
    ├── dependencies.py
    ├── errors.py
    └── middleware.py
```

---

### 9.1 `app/main.py`

Should eventually become a small composition root.

Responsibilities:

```text
create FastAPI application
register routes
register middleware
register lifecycle
register exception handlers
```

It should not contain business logic.

---

### 9.2 `app/lifecycle.py`

Owns process lifecycle.

Examples:

```text
startup
↓
load models
load vector store
initialize services

shutdown
↓
release resources
```

Models should normally be initialized once, not once per HTTP request.

---

### 9.3 `app/api/routes.py`

Owns HTTP routes.

Examples:

```text
GET /health
POST /ask
```

Routes should translate:

```text
HTTP
↔
application services
```

but should not implement retrieval logic.

---

### 9.4 `app/api/dependencies.py`

Owns FastAPI dependency injection.

Possible interfaces:

```python
get_settings()
get_rag_service()
```

This allows application components to be replaced during testing without
rewriting endpoints.

---

### 9.5 `app/api/errors.py`

Owns application/API error translation.

Examples:

```text
InvalidQueryError
RetrievalError
GenerationError
```

Internal exceptions can be mapped to controlled HTTP responses.

---

### 9.6 `app/api/middleware.py`

Possible responsibilities:

```text
request ID
request timing
basic HTTP logging
```

Middleware should handle cross-cutting HTTP concerns rather than business
logic.

---


<a id="en-10-evaluation-architecture"></a>

## 10. Evaluation Architecture

Evaluation is independent from the runtime application.

Target structure:

```text
evaluation/
├── __init__.py
├── models.py
├── dataset.py
├── evidence.py
├── metrics.py
├── runner.py
├── history.py
└── random_eval.py
```

Primary rule:

```text
evaluation measures retrieval
```

but:

```text
retrieval must not depend on evaluation
```

Dependency direction:

```text
evaluation
    ↓
retrieval
```

Never:

```text
retrieval
    ↓
evaluation
```

---


<a id="en-11-evaluation-dataset-roles"></a>

## 11. Evaluation Dataset Roles

Three dataset categories are intentionally separated.

### DEV

Used during development.

May influence design and tuning.

The DEV dataset is allowed to influence implementation decisions.

---

### RANDOM

Used for:

```text
robustness exploration
unexpected failure discovery
coverage exploration
```

Random sampling must be reproducible through a stored seed.

---

### TEST

Held-out evaluation.

TEST must not become another tuning dataset.

Repeated manual inspection of TEST results during optimization would
reduce its value as an independent generalization check.

---


<a id="en-12-evaluation-flow"></a>

## 12. Evaluation Flow

```text
EvaluationQuestion
       │
       ▼
retrieval service
       │
       ▼
ranked results
       │
       ▼
gold evidence matching
       │
       ▼
rank of correct evidence
       │
       ▼
metrics
       │
       ├── Hit@K
       └── MRR
```

Evaluation run metadata should also contain:

```text
Git commit
working-tree dirty state
dataset hash
timestamp
configuration
```

This makes results reproducible and comparable.

---


<a id="en-13-universal-document-explorer"></a>

## 13. Universal Document Explorer

The document explorer is not part of the runtime RAG retrieval path.

Its purpose is:

```text
corpus exploration
+
gold evidence discovery
+
manual benchmark construction
```

Target structure:

```text
document_search/
├── __init__.py
├── models.py
├── normalize.py
├── tokenize.py
├── load_pages.py
├── build_index.py
├── search.py
│
└── security/
    ├── __init__.py
    ├── paths.py
    ├── pdf_validation.py
    └── input_validation.py
```

CLI:

```text
scripts/search_pdf.py
```

---


<a id="en-14-document-explorer-data-flow"></a>

## 14. Document Explorer Data Flow

```text
PDF CORPUS
    │
    ▼
security validation
    │
    ▼
load_pdf_pages()
    │
    │ list[PageDocument]
    ▼
normalize_text()
    │
    ▼
tokenize()
    │
    ▼
build_bm25_index()
    │
    │ BM25SearchIndex
    ▼
search_pages()
    │
    │ list[SearchResult]
    ▼
CLI
    │
    ▼
human evidence validation
    │
    ▼
evaluation dataset
```

This architecture intentionally differs from the RAG retrieval stack.

Document exploration:

```text
BM25 lexical retrieval
+
human validation
```

Main RAG:

```text
embedding retrieval
+
CrossEncoder reranking
```

This separation reduces circular benchmark construction.

---


<a id="en-15-document-search-models"></a>

## 15. Document Search Models

### 15.1 `PageDocument`

Represents one source page.

Conceptually:

```python
PageDocument(
    source="manual.pdf",
    page=26,
    text="...",
)
```

The combination:

```text
source
+
page
+
text
```

represents the identity and content of the searchable source unit.

---

### 15.2 `SearchResult`

Represents a ranked search result.

Conceptually:

```text
document
+
score
```

The result should reference the original `PageDocument` rather than
duplicate document metadata across multiple structures.

---

### 15.3 `BM25SearchIndex`

Owns:

```text
page corpus
+
BM25 model
```

The rest of the application should not need to manage these two objects
independently.

---


<a id="en-16-document-explorer-security-boundary"></a>

## 16. Document Explorer Security Boundary

The PDF corpus is treated as external input.

Security flow:

```text
filesystem input
      │
      ▼
path validation
      │
      ▼
file validation
      │
      ▼
resource limits
      │
      ▼
PDF parser
```

Important controls:

```text
allowed directory boundary
path traversal prevention
symlink resolution
PDF extension validation
PDF signature validation
file size limits
page count limits
query limits
top_k limits
```

Security validation must not silently modify document semantics.

If a document cannot be safely or completely loaded, the failure should
be explicit.

---


<a id="en-17-security-architecture"></a>

## 17. Security Architecture

Security is a cross-cutting concern.

Some controls belong close to the data source:

```text
document_search/security/
```

Other controls belong to the runtime application:

```text
app/security/
```

Future target:

```text
app/
└── security/
    ├── __init__.py
    ├── validation.py
    ├── limits.py
    └── headers.py
```

Security is not implemented through getters and setters.

Primary mechanisms include:

```text
input validation
immutability
filesystem boundaries
resource limits
dependency controls
secrets handling
permissions
container isolation
HTTP controls
```

---

### 17.1 Future Threat Modeling

A dedicated security phase should identify:

```text
assets
trust boundaries
attack surfaces
possible attackers
failure modes
impact
mitigations
```

RAG-specific threats may include:

```text
indirect prompt injection
malicious document content
resource exhaustion
unsafe file handling
oversized requests
dependency vulnerabilities
```

---


<a id="en-18-observability-architecture"></a>

## 18. Observability Architecture

Target structure:

```text
app/
└── observability/
    ├── __init__.py
    ├── logging.py
    ├── metrics.py
    └── middleware.py
```

Observability should cover both quality and operation.

Operational metrics include:

```text
request count
error count
response latency
retrieval latency
reranking latency
generation latency
```

Where relevant:

```text
token usage
model usage
cost
```

Observability must not change retrieval results.

---

### 18.1 Structured Logging

Runtime logs should eventually contain structured fields such as:

```text
request_id
event
latency_ms
candidate_count
model
error_type
```

rather than relying only on free-form text.

---

### 18.2 Quality Metrics vs Operational Metrics

Quality metrics:

```text
MRR
Hit@K
groundedness
answer quality
```

Operational metrics:

```text
latency
request count
error rate
resource usage
token usage
cost
```

These measure different aspects of the system and should not be mixed.

---


<a id="en-19-testing-architecture"></a>

## 19. Testing Architecture

Current tests live in:

```text
tests/
```

Future tests should increasingly mirror production modules.

Example:

```text
document_search/normalize.py
        ↕
tests/document_search/test_normalize.py
```

and:

```text
document_search/search.py
        ↕
tests/document_search/test_search.py
```

Testing layers:

```text
UNIT TESTS
    ↓
individual functions/modules

INTEGRATION TESTS
    ↓
multiple modules together

SMOKE TESTS
    ↓
basic end-to-end system operation

EVALUATION
    ↓
retrieval quality
```

These are different responsibilities.

A passing unit test does not prove retrieval quality.

A good MRR score does not prove API correctness.

---

### 19.1 Test Independence

Where practical, unit tests should avoid depending on:

```text
large real PDF corpora
network access
production vector databases
external APIs
```

Small synthetic inputs should be preferred for deterministic unit tests.

Real corpus tests belong in integration or manual validation workflows.

---


<a id="en-20-infrastructure-architecture"></a>

## 20. Infrastructure Architecture

Current infrastructure includes:

```text
Dockerfile
compose.yaml
.github/workflows/ci.yml
```

Target production path:

```text
SOURCE CODE
    │
    ▼
Git
    │
    ▼
CI
    │
    ├── tests
    ├── static checks
    └── later security checks
    │
    ▼
Docker image
    │
    ▼
deployment
    │
    ▼
runtime monitoring
```

---

### 20.1 Container Architecture

Future production containers should aim for:

```text
reproducible builds
minimal runtime dependencies
non-root execution
health checks
explicit configuration
small attack surface
```

Multi-stage Docker builds may be introduced when useful.

---

### 20.2 CI/CD

Current CI primarily validates the project.

Future CI/CD may extend the flow to:

```text
push
↓
tests
↓
static checks
↓
security checks
↓
image build
↓
deployment
```

Deployment automation should be added only after the runtime architecture
is stable enough to deploy reliably.

---


<a id="en-21-dependency-direction"></a>

## 21. Dependency Direction

The intended dependency direction is:

```text
API
 ↓
RAG
 ↓
Retrieval / Generation
 ↓
Models / Infrastructure integrations
```

Evaluation may call retrieval:

```text
Evaluation
    ↓
Retrieval
```

Document explorer is independent:

```text
Document Explorer
    ↓
PDF / BM25 libraries
```

The following dependency directions should be avoided:

```text
retrieval → API
retrieval → evaluation
generation → FastAPI
document_search → RAG
document_search → OSPF logic
```

This reduces coupling.

---


<a id="en-22-public-interfaces"></a>

## 22. Public Interfaces

The architecture should expose a small number of stable entry points.

Planned examples are listed below.

### 22.1 Document Search

```python
load_pdf_pages(...)
build_bm25_index(...)
search_pages(...)
```

---

### 22.2 Retrieval

```python
retrieve(...)
```

---

### 22.3 RAG

Conceptually:

```python
answer_question(...)
```

---

### 22.4 Evaluation

Conceptually:

```python
evaluate_dataset(...)
```

Internal helper functions may change without requiring all callers to
change.

---


<a id="en-23-current-technical-debt"></a>

## 23. Current Technical Debt

Known architectural debt is documented below.

### 23.1 Retrieval

Current:

```text
app/retrieval.py
```

contains multiple responsibilities and domain-specific rules.

Resolution:

```text
PHASE 3
```

---

### 23.2 RAG

Current:

```text
app/rag.py
```

contains OSPF-specific behavior.

Resolution:

```text
PHASE 3
```

---

### 23.3 Evaluation — foundation implemented

Reusable dataset loading, evidence matching, metrics, latency and history already live in `evaluation/`; CLI orchestration remains in `scripts/`. The older `scripts.evaluate_random` still contains history-path, Git-status and metric-output defects. The supported comparison workflow is `scripts.evaluate_retrieval` on DEV/RANDOM; see [EVALUATION.md](EVALUATION.md).

---

### 23.4 Document Search — historical prototype replaced

The previous heuristic search prototype experimented with:

```text
required terms
boost terms
manual proximity scoring
anchor terms
manual exclusions
```

That historical prototype has been replaced by the generic page-based BM25 implementation in `document_search/`.

Current discovery workflow:

```text
generic BM25 search
+
human evidence validation
```

Source-PDF evidence still requires human validation, independently of search ranking.

---

### 23.5 Ingestion

The current ingestion pipeline remains concentrated in:

```text
scripts/ingest.py
```

This is acceptable for the current phase.

It should only be decomposed when:

```text
complexity increases
testing becomes difficult
reuse is required
or measurements expose a concrete problem
```

Avoid refactoring ingestion only for architectural symmetry.

---


<a id="en-24-target-project-structure"></a>

## 24. Target Project Structure

Long-term target structure:

```text
rag_api_project/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── lifecycle.py
│   ├── schemas.py
│   ├── generation.py
│   ├── rag.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   ├── dependencies.py
│   │   ├── errors.py
│   │   └── middleware.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── embeddings.py
│   │   ├── vector_search.py
│   │   ├── query.py
│   │   ├── reranker.py
│   │   ├── scoring.py
│   │   └── service.py
│   │
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── metrics.py
│   │   └── middleware.py
│   │
│   └── security/
│       ├── __init__.py
│       ├── validation.py
│       ├── limits.py
│       └── headers.py
│
├── document_search/
│   ├── __init__.py
│   ├── models.py
│   ├── normalize.py
│   ├── tokenize.py
│   ├── load_pages.py
│   ├── build_index.py
│   ├── search.py
│   │
│   └── security/
│       ├── __init__.py
│       ├── paths.py
│       ├── pdf_validation.py
│       └── input_validation.py
│
├── evaluation/
│   ├── __init__.py
│   ├── models.py
│   ├── dataset.py
│   ├── evidence.py
│   ├── metrics.py
│   ├── runner.py
│   ├── history.py
│   └── random_eval.py
│
├── scripts/
│   ├── __init__.py
│   ├── ingest.py
│   ├── search_pdf.py
│   ├── evaluate_retrieval.py
│   ├── production_smoke.py
│   └── git_check.py
│
├── tests/
│   ├── document_search/
│   ├── evaluation/
│   ├── retrieval/
│   ├── integration/
│   └── test_smoke.py
│
├── eval/
│   ├── dev_questions.json
│   ├── random/
│   └── test_questions.json
│
├── Dockerfile
├── compose.yaml
├── requirements.txt
└── .env.example
```

This is a target application-module structure. Documentation remains centralized at the repository root; this diagram does not plan a move back into `rag_api_project/`.

| Documentation | Repository path |
| --- | --- |
| Portfolio entry | [README.md](../../README.md) |
| Documentation index | [docs/README.md](../README.md) |
| English project overview | [docs/en/PROJECT.md](PROJECT.md) |
| Czech project overview | [docs/cs/PROJECT.md](../cs/PROJECT.md) |
| Language guides and rules | `docs/en/` and `docs/cs/` |

Directories should be created only when their corresponding development
phase begins.

The project should not create empty architecture merely to match the
diagram.

---


<a id="en-25-architecture-change-rule"></a>

## 25. Architecture Change Rule

Architecture may evolve.

However, significant architecture changes should follow this process:

```text
identify concrete problem
        ↓
measure or demonstrate problem
        ↓
propose architectural change
        ↓
update architecture documentation
        ↓
implement change
        ↓
test
```

Architecture should not be changed only because another design appears
more sophisticated.

The simplest architecture that satisfies current requirements is
preferred.

---


<a id="en-26-historical-phase-2a-architectural-focus"></a>

## 26. Historical Phase 2A Architectural Focus

The sequence below preserves the original plan. It is no longer the active step; see the [current implementation snapshot](#en-current-implementation-snapshot-2026-10-28) and [current development focus](ROADMAP.md#en-current-development-focus). The current work is the hybrid RRF experiment described in the development log; this does not renumber the approved roadmap.

Current development phase:

```text
PHASE 2 — Evaluation Foundation
```

Current architectural task:

```text
PHASE 2A — Universal Document Explorer
```

Immediate target:

```text
document_search/
```

with:

```text
immutable data models
domain-independent text processing
safe PDF loading
BM25 retrieval
small public API
unit tests
```

The main RAG retrieval implementation remains unchanged until the
evaluation foundation is sufficiently complete.

The next architectural milestone is:

```text
PHASE 2A.0
architecture freeze

↓

PHASE 2A.1
document_search/models.py
```

[↑ Back to top](#top)
