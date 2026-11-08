<a id="top"></a>

# Operations runbook

[Česky](../cs/OPERATIONS.md#cz) · [English](#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Contents — click to expand</summary>

- [1. Setup and configuration](#en-1-setup-and-configuration)
- [1a. Dependency reproducibility (Windows Python 3.11)](#en-1a-dependency-reproducibility-windows-python-311)
- [1b. Dependency audit context](#en-1b-dependency-audit-context)
- [2. Prepare and ingest PDF sources](#en-2-prepare-and-ingest-pdf-sources)
- [3. Run and inspect the application](#en-3-run-and-inspect-the-application)
- [4. PDF evidence discovery and offline evaluation](#en-4-pdf-evidence-discovery-and-offline-evaluation)
- [5. Tests, Git and Docker](#en-5-tests-git-and-docker)
- [6. Troubleshooting and limits](#en-6-troubleshooting-and-limits)

</details>

---

<a id="en"></a>

> **Scope:** Current Chroma-backed RAG project, Python 3.11. Commands below run from `rag_api_project/`. This is a local educational prototype, not a production deployment.
>
> **Safety:** `python -m scripts.ingest` **deletes and recreates** the existing Chroma collection with the configured name. Back up the index and confirm the PDF corpus and configuration before running. It is **not** an incremental ingest.

<a id="en-1-setup-and-configuration"></a>

## 1. Setup and configuration

Use Python 3.11 and run commands from `rag_api_project/`. On Windows PowerShell:

```powershell
# From the cloned repository root (change directory only once):
cd rag_api_project
python --version  # Must be 3.11.x.
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

On Linux/macOS:

```bash
cd rag_api_project
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
```

The configuration lives in `.env` (see `.env.example` and `app/config.py`). Defaults include `data/`, `chroma_db/`, collection `ospf`, embedding model `all-MiniLM-L6-v2` and eight retrieval results. Verify your active Python environment before installing packages. This published branch does not yet provide an approved universal dependency lockfile.

`RAG_GENERATION_MODEL_NAME` defaults to `google/flan-t5-base`; `RAG_RERANKER_MODEL_NAME` to `cross-encoder/ms-marco-MiniLM-L-6-v2`. Optional `RAG_DATA_DIR` / `RAG_CHROMA_DIR` override paths (prefer absolute paths). Environment variables override `.env`; restart the API after changes because settings are cached. Ingest and vector/legacy retrieval must use the index's embedding model. Page discovery and candidate validation default to relative `data/`, independently of `RAG_DATA_DIR`; pass `--data-dir <directory>` for a custom corpus.


<a id="en-1a-dependency-reproducibility-windows-python-311"></a>

## 1a. Dependency reproducibility (Windows Python 3.11)

The published `requirements.txt` does not pin versions. A locally generated `requirements-win-py311.lock.txt` may exist but is **not automatically approved, tracked or portable**. Before adopting such a lockfile, independently verify the generation method, Python/OS support, clean Windows installs, CI compatibility, consistency with the requirements file, and an update policy. Keep dependency changes in a separate reviewed commit.


<a id="en-1b-dependency-audit-context"></a>

## 1b. Dependency audit context

The chatbot currently runs locally/offline. The owner keeps dependency auditing enabled with possible future API integration in mind. The [2026-10-29 audit of `82d5889`](https://github.com/jyenten/local_rag_api/actions/runs/40865587058) failed with the same known ChromaDB advisory set; this is separate from the Python test results.

Applicability depends on the affected functionality and deployment configuration. Local/offline operation alone does not establish whether a finding is exploitable or irrelevant. No check is disabled or waived by this documentation update.

The [ChromaDB security assessment](CHROMA_SECURITY.md), updated on 2026-11-07, records four distinct CVEs, local-profile boundaries, and owner-reported running-container checks. `pip-audit` remains enabled without suppressing known findings.


<a id="en-2-prepare-and-ingest-pdf-sources"></a>

## 2. Prepare and ingest PDF sources

Place PDF files directly in `data/` using the `*.pdf` extension. Review source filenames, configuration and backups **before** ingest:

```bash
python -m scripts.ingest
```

**Destructive operation:** The script drops an existing collection with the configured name and recreates it. It does not append incrementally. It extracts physical PDF pages, cleans text, chunks it (1000 characters / 150 overlap by default), embeds and upserts into Chroma, preserving source/page/chunk metadata.

Deletion happens **before** PDF extraction and upsert. A later failure does not restore the old index; ingestion is not transactional. Back up the Chroma directory while processes using it are stopped.

Verify count and sample metadata **without changing collection records**:

```bash
python -c "import chromadb; from app.config import get_settings; s=get_settings(); c=chromadb.PersistentClient(path=str(s.chroma_dir)).get_collection(name=s.collection_name); print('COLLECTION:', c.name, 'CHUNKS:', c.count()); print(c.get(limit=3, include=['metadatas']))"
```

`PersistentClient` is not read-only: opening it may create a directory/database or run migrations. Check that the intended `RAG_CHROMA_DIR` exists first; use an index copy for strictly immutable inspection.

Keep private PDFs, indices, `.env` secrets and model caches out of Git. Document corpus/configuration changes before comparing evaluation runs.


<a id="en-3-run-and-inspect-the-application"></a>

## 3. Run and inspect the application

```bash
python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs. Supported endpoints include `/`, `/health`, `/ready`, `/stats` and `/ask`. Example PowerShell request:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/ask -Method Post -ContentType 'application/json' -Body '{"question":"How does OSPF select the router ID?"}'
```

BM25 is selectable in the offline evaluation CLI, **not** as an established `/ask` retrieval mode. Hybrid RRF integration is experimental, not a documented deployed endpoint.


<a id="en-4-pdf-evidence-discovery-and-offline-evaluation"></a>

## 4. PDF evidence discovery and offline evaluation

Explore source *pages* independently of Chroma-backed chunk retrieval:

```bash
python -m scripts.search_pdf "OSPF router ID" --top-k 10 --interactive
```

Evaluate existing golden-evidence datasets:

```bash
python -m scripts.evaluate_retrieval --retriever legacy --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset dev
python -m scripts.evaluate_retrieval --retriever bm25 --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset random
python -m scripts.evaluate_retrieval --retriever bm25 --dataset random
```

Evaluation prints MRR, Hit@K and retrieval-only latency. It appends JSONL run history with dataset hash and Git provenance. **TEST is intentionally unavailable for iterative tuning.** Follow [EVALUATION.md](EVALUATION.md) for ground-truth construction, validation, approval and interpretation.


<a id="en-5-tests-git-and-docker"></a>

## 5. Tests, Git and Docker

```bash
python -m pytest -q
python -m pytest -q tests/retrievers/test_bm25.py
git diff --check
git diff --cached --check
python -m scripts.git_check
```

Use explicit `git add <paths>`, review staged changes, and follow project agent/governance rules. Never silently modify gold evidence to improve a score.

Inspect `git status --short` and `git branch --show-current` first. The default integration branch is `main`; prepare changes on a separate working branch and merge through a reviewed PR. Do not switch across unrelated WIP. After staging exact paths, inspect `git diff --cached` and its file list. The helper checks staged whitespace and runs tests; it does not verify secrets, approvals or scope. Commit/push only within authorized scope; never merge automatically.

Docker commands (from the project directory):

```bash
docker compose up --build
docker compose down
```

Compose explicitly binds `127.0.0.1:8001:8000`; the API is at http://127.0.0.1:8001/docs. It mounts Chroma/model-cache directories. Editing YAML does not change an existing container; identify its original Compose project and mount paths before recreating it, as described in the [security assessment](CHROMA_SECURITY.md). The image omits `document_search/`, `evaluation/`, `eval/` and PDFs. Run ingestion, page discovery and evaluation natively; the API container needs a compatible existing index and model access on first use.

Compose does **not** pass the host `.env` to the application: it defines neither `env_file` nor `environment`, and the image contains only `.env.example`. Custom `RAG_*` values require explicit local Compose configuration with container-valid paths. Startup or `/health` alone does not verify `/ask`; also inspect `/ready` and `/stats`.


<a id="en-6-troubleshooting-and-limits"></a>

## 6. Troubleshooting and limits

- Missing PDFs: inspect `data/`, exact filenames and `*.pdf` extension.
- Missing collection: check `RAG_COLLECTION_NAME`, `chroma_db/` and whether ingestion completed.
- Package import errors: check Python interpreter, virtual environment and project working directory.
- `FIRST_EVIDENCE_RANK=None`: no ranked result matched the declared source/page/text evidence; this does not prove the retriever returned no documents.
- Fast latency measurements exclude initialization and full answer generation; compare repeated warmed runs for operational conclusions.

[↑ Back to top](#top)
