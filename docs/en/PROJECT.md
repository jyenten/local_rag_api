<a id="top"></a>

<a id="rag-api--document-search--retrieval-evaluation"></a>

# Local RAG API — Document Search & Retrieval Evaluation

[Česky](../cs/PROJECT.md#cz) · [English](#en) · [Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Obsah / Contents — kliknutím rozbalit / click to expand</summary>

**English**

- [Tech stack](#en-tech-stack)
- [Architecture and modules](#en-architecture-and-modules)
- [Data flow](#en-data-flow)
- [Key engineering decisions](#en-key-engineering-decisions)
- [Local setup](#en-local-setup)
- [Index local PDFs](#en-index-local-pdfs)
- [Running the API](#en-running-the-api)
- [Tests](#en-tests)
- [Offline retrieval evaluation](#en-offline-retrieval-evaluation)
- [Standalone BM25 PDF search](#en-standalone-bm25-pdf-search)
- [Docker and Compose](#en-docker-and-compose)
- [Current limitations and next steps](#en-current-limitations-and-next-steps)
- [AI-assisted development and contributor boundaries](#en-ai-assisted-development-and-contributor-boundaries)

</details>

---

<a id="en"></a>

A local Python/FastAPI chatbot for technical PDF documentation, currently focused on OSPF, with retrieval evaluation, source metadata and regression testing. Inference runs locally; installation and first model use may require downloads.

**Status:** actively developed educational prototype, not a production service. The existing `/ask` pipeline uses Chroma retrieval, context selection, reranking, and rule-based/model-generated responses. Separately, the repository includes a vector retriever, BM25 lexical retriever, and offline retrieval evaluation tools.


<a id="en-tech-stack"></a>

## Tech stack

Python 3.11 · FastAPI · Pydantic · ChromaDB · Sentence Transformers · `rank-bm25` · Transformers/PyTorch · pypdf · pytest · Docker · GitHub Actions.


<a id="en-architecture-and-modules"></a>

## Architecture and modules

| Component | Path | Purpose |
| --- | --- | --- |
| HTTP API | `app/main.py` | `/`, `/health`, `/ready`, `/stats`, `/ask` |
| Configuration | `app/config.py` | Environment-based Pydantic settings |
| RAG orchestration | `app/rag.py` | Answers and supporting context |
| Existing retrieval pipeline | `app/retrieval.py` | Retrieval, context-line selection and reranking |
| Vector retrieval | `app/retrievers/vector.py` | Chroma vector baseline |
| BM25 retrieval | `app/retrievers/bm25.py` | Lexical ranking over Chroma chunks |
| PDF ingestion | `scripts/ingest.py` | Extract and index PDF text |
| PDF search CLI | `scripts/search_pdf.py` | Independent local BM25 page search |
| Retrieval evaluation | `evaluation/`, `scripts/evaluate_retrieval.py` | Rank-based quality, latency and provenance |
| Tests | `tests/` | Unit and regression tests |


<a id="en-data-flow"></a>

### Data flow

| Path | Current flow | Interface / output |
| --- | --- | --- |
| HTTP answers | Chroma retrieval → context selection and reranking → OSPF rules / model fallback | `POST /ask`; answer, context and source metadata |
| Offline evaluation | `legacy` / `vector` / `bm25` → comparison against golden evidence | CLI; MRR, Hit@K, retrieval latency and JSONL history |
| PDF exploration | Local PDF pages → independent BM25 page search | `search_pdf` CLI; input to human evidence verification |

**Integration boundary:** BM25 is implemented and selectable in the **offline evaluation CLI** together with `legacy` and `vector`. The HTTP `/ask` API has not been switched to a BM25 or hybrid retrieval mode. Hybrid RRF is work in progress, not an established released feature.


<a id="en-key-engineering-decisions"></a>

## Key engineering decisions

- Indexed chunks carry source, physical PDF page, and chunk metadata for traceability.
- BM25 loads stored chunks in bounded batches, validates data consistency, filters non-matching documents, and breaks score ties using ascending chunk IDs.
- Vector search returns distance-like scores (lower typically closer); BM25 returns ranking scores (higher ranks first). Raw scores should not be compared directly.
- Evaluation is split into development, random-sample, and held-out test data, with dataset hashes and Git provenance.
- Model-based generation is a fallback to task-specific answer logic; the system is not a general-purpose, production-grade QA engine.


<a id="en-local-setup"></a>

## Local setup

Run from `rag_api_project/` using Python 3.11.

**Windows PowerShell**

~~~powershell
python --version  # Must be 3.11.x.
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
~~~

**macOS/Linux**

~~~bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
~~~

Dependencies are currently unpinned; this is not yet a fully reproducible lockfile-based installation.


<a id="en-index-local-pdfs"></a>

### Index local PDFs

Put technical PDF files in `data/` (ignored by Git), then run:

~~~bash
python -m scripts.ingest
~~~

The local Chroma collection is stored under `chroma_db/`. The example configuration uses the collection named `ospf`. **Warning: `scripts.ingest` deletes and recreates an existing collection with that name**, rather than incrementally updating it. Back up the index if it must be preserved. The API requires suitable indexed data to answer corpus-specific questions. Full procedure: [OPERATIONS.md](OPERATIONS.md).


<a id="en-running-the-api"></a>

## Running the API

~~~bash
python -m uvicorn app.main:app --reload
~~~

Open `http://127.0.0.1:8000/docs` for interactive OpenAPI documentation.

- `GET /` and `GET /health` — liveness and environment information.
- `GET /ready` — initializes the retrieval service and reports the collection chunk count. It does not execute a question or verify generation-model loading, so it is not a full `/ask` smoke test.
- `GET /stats` — reports collection information.
- `POST /ask` — accepts a JSON question and returns an answer with supporting context and source previews.

Example request:

~~~bash
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"question":"How does OSPF select the router ID?"}'
~~~

On Windows PowerShell, use `Invoke-RestMethod` if shell-specific `curl` quoting differs:

~~~powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/ask -Method Post -ContentType 'application/json' -Body '{"question":"How does OSPF select the router ID?"}'
~~~


<a id="en-tests"></a>

## Tests

From `rag_api_project/`:

~~~bash
python -m pytest -q tests
~~~

Verified run for **commit `ce9a088`, 2026-11-08**: **223 passed in 7.62s** on Ubuntu / Python 3.11 ([GitHub Actions run](https://github.com/jyenten/local_rag_api/actions/runs/42511536430)). This dated result covers `main` after the BM25 initialization token-reuse change, the loopback-only Compose port binding and documentation updates; it does not establish improved retrieval quality, end-to-end latency or security and remains separate from real-corpus retrieval evaluation. Historical local runs remain in the [learning log](LEARNING_LOG.md).

BM25 tests use synthetic Chroma fixtures and cover pagination, ranking, deterministic tie-breaking, metadata alignment, invalid queries and records, and malformed batches.


<a id="en-offline-retrieval-evaluation"></a>

## Offline retrieval evaluation

The framework reports MRR, Hit@1/3/5/8 and retrieval latency mean/p50/p95. Run metadata includes the dataset hash, Git commit and dirty-worktree state. Runtime evaluation results under `eval/results/` are excluded from version control. Repeating a historical result requires the same source PDFs, index, retrieval configuration and model/dependency versions. The public snapshot does not bundle the original corpus, index or JSONL run histories.

Supported commands in the published evaluation CLI:

~~~bash
python -m scripts.evaluate_retrieval --retriever legacy --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset dev
python -m scripts.evaluate_retrieval --retriever bm25 --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset random
python -m scripts.evaluate_retrieval --retriever bm25 --dataset random
~~~

The CLI accepts `legacy`, `vector`, `bm25` and `dev`/`random`. It writes JSONL run history, so it is not read-only. The held-out TEST set is reserved for final assessment, not iterative tuning. See [EVALUATION.md](EVALUATION.md) for evidence creation and comparison discipline.


<a id="en-standalone-bm25-pdf-search"></a>

## Standalone BM25 PDF search

A separate discovery CLI indexes local PDF pages:

~~~bash
python -m scripts.search_pdf "router ID" --top-k 5 --interactive
~~~

This tool reads PDF files in `data/` and is distinct from the Chroma-backed `BM25Retriever`.


<a id="en-docker-and-compose"></a>

## Docker and Compose

The repository contains a Dockerfile and `compose.yaml`:

~~~bash
docker compose up --build
docker compose down
~~~

Compose maps host port `8001` to container port `8000` and mounts local Chroma/model-cache directories. This is a local container configuration, not a hosted demo.

**Known limitations:** the image copies `app/` and `scripts/`, but omits `document_search/`, `evaluation/`, `eval/` and source PDFs. Compose does not pass the host `.env` into the container. Run ingestion and evaluation natively; the container API requires a compatible mounted index. See [OPERATIONS.md](OPERATIONS.md) for configuration and packaging boundaries.


<a id="en-current-limitations-and-next-steps"></a>

## Current limitations and next steps

- Preserve the [BM25 vs. Vector DEV/RANDOM baseline recorded on 2026-10-20](EVALUATION.md#en-8-historical-baseline-2026-10-20).
- Experiment with hybrid lexical + semantic retrieval (RRF), based on measured results, without tuning on held-out TEST.
- Improve dependency pinning, Docker packaging coverage, and operational observability.
- Continue improving extraction robustness, error reporting and evaluation on unseen questions.


<a id="en-ai-assisted-development-and-contributor-boundaries"></a>

## AI-assisted development and contributor boundaries

Developed with substantial ChatGPT and Codex assistance, including code and test generation, debugging and review. The [learning log](LEARNING_LOG.md) records collaboration, BM25 test attribution and learning evidence; completed features are separate from independently demonstrated skills. Detailed worktree and private-mirror history remains in that log.

Before changing files, read the [repository rules](AGENTS.md) and [project rules](PROJECT_AGENTS.md). Development and review procedures are in the [development guide](DEVELOPMENT_GUIDE.md).

[↑ Nahoru / Back to top](#top)
