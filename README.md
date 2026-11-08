<a id="top"></a>

<a id="ai-engineering-portfolio--python-rag--retrieval-evaluation"></a>

# Local RAG API — Document Search & Retrieval Evaluation

[Česky](docs/cs/README.md#cz) · [English](#en) · [Documentation](docs/README.md)

<a id="en"></a>

Local Python/FastAPI prototype for question answering over technical PDFs, currently focused on OSPF documentation. It combines source and page metadata in HTTP answers with separate vector and BM25 retrieval experiments. Offline evaluation records MRR, Hit@K, retrieval latency, dataset hashes and Git provenance.

**Tech stack:** Python 3.11 · FastAPI · Pydantic · ChromaDB · Sentence Transformers · BM25 · Pytest · Docker · GitHub Actions

<a id="obsah"></a>

<details>
<summary>Contents — click to expand</summary>

- [Featured project](#en-featured-project-rag-api-and-document-search)
- [What is implemented](#en-what-is-implemented)
- [Verification](#en-verification)
- [Recorded retrieval baseline](#en-recorded-retrieval-baseline)
- [Architecture at a glance](#en-architecture-at-a-glance)
- [Getting started](#en-getting-started)
- [Engineering approach](#en-engineering-approach)
- [Repository layout](#en-repository-layout)
- [Next steps](#en-next-steps)

</details>

<a id="en-featured-project-rag-api-and-document-search"></a>

<a id="featured-project-rag-api-and-document-search"></a>

## Featured project: Local RAG API

**[Explore Local RAG API](docs/en/PROJECT.md)**

PDF ingestion extracts and chunks technical documentation into ChromaDB. The current HTTP answer pipeline uses context selection, reranking, OSPF-specific answer rules and model generation as a fallback. Separate retrieval strategies are compared in the offline evaluation CLI.

<a id="en-what-is-implemented"></a>

### What is implemented

- **API:** FastAPI endpoints for health, readiness, statistics and questions; typed request/response models.
- **Document pipeline:** PDF text extraction, chunking, ChromaDB indexing and source/page/chunk metadata.
- **Retrieval:** vector retrieval with sentence embeddings, a separately tested BM25 lexical retriever, and the existing RAG retrieval/reranking workflow.
- **Evaluation:** labeled question datasets, Hit@1/3/5/8, MRR, latency mean/p50/p95, JSONL evaluation history, dataset hashes and Git provenance.
- **Testing:** pytest unit and regression tests with synthetic fixtures and fake Chroma collections; GitHub Actions CI.
- **Deployment tooling:** Dockerfile and Compose configuration for a local API container.

<a id="en-verification"></a>

### Verification

Verified run for **commit `7081599`, 2026-11-08**: **223 passed in 5.65s** on Ubuntu / Python 3.11 ([GitHub Actions run](https://github.com/jyenten/local_rag_api/actions/runs/42482651938)). This dated test result follows the BM25 initialization token-reuse change; it does not establish improved retrieval quality or end-to-end latency and remains separate from real-corpus retrieval evaluation. Historical local runs remain in the [learning log](docs/en/LEARNING_LOG.md).

<a id="en-recorded-retrieval-baseline"></a>

### Recorded retrieval baseline — 2026-10-20

| Dataset | Questions | BM25 MRR | Vector MRR |
| --- | ---: | ---: | ---: |
| DEV | 20 | 0.7171 | 0.8321 |
| RANDOM | 25 | 0.8133 | 0.6050 |

These are historical results recorded in the [learning log](docs/en/LEARNING_LOG.md#en-2026-10-20--phase-34-retrieval-evaluation). The original JSONL runs, corpus and index are not bundled with this public snapshot; the values were not reproduced for this documentation update. MRR measures the rank of matching evidence, not generated-answer accuracy. The fixed RANDOM dataset is used for robustness exploration; TEST remains reserved for final assessment. See the [evaluation guide](docs/en/EVALUATION.md#en-8-historical-baseline-2026-10-20) for provenance and comparison limits.

<a id="en-architecture-at-a-glance"></a>

### Architecture at a glance

| Path | Current flow | Interface / output |
| --- | --- | --- |
| HTTP answers | Chroma retrieval → context selection and reranking → OSPF rules / model fallback | `POST /ask`; answer, context and source metadata |
| Offline evaluation | `legacy` / `vector` / `bm25` → comparison against golden evidence | CLI; MRR, Hit@K, retrieval latency and JSONL history |
| PDF exploration | Local PDF pages → independent BM25 page search | `search_pdf` CLI; input to human evidence verification |

**Integration status:** the HTTP `/ask` endpoint uses the existing Chroma-backed RAG pipeline. `legacy`, `vector` and `bm25` are selectable in the offline evaluation CLI on DEV/RANDOM. Hybrid RRF has not been integrated into public `main`.

<a id="en-getting-started"></a>

## Getting started

Start with the [project overview](docs/en/PROJECT.md) or [Czech project overview](docs/cs/PROJECT.md). Use the [operations runbook](docs/en/OPERATIONS.md) for setup/ingestion and the [evaluation guide](docs/en/EVALUATION.md) for evidence, metrics and comparison procedures.

**Project status:** educational engineering portfolio / actively developed local prototype. There is no hosted demo. Installation and first model use may require model downloads; inference uses local models.

<a id="en-engineering-approach"></a>

## Engineering approach

Developed with substantial ChatGPT and Codex assistance, including code and test generation, debugging and review. The [learning log](docs/en/LEARNING_LOG.md) records collaboration and learning evidence; completed features are kept separate from independently demonstrated skills. Development procedures are in the [development guide](docs/en/DEVELOPMENT_GUIDE.md).

**Contributor and agent instructions:** before changing files, read the [repository rules](docs/en/AGENTS.md) and, for RAG work, the [project rules](docs/en/PROJECT_AGENTS.md). Their location under `docs/` does not narrow their scope. BM25 test attribution and agent-work history remain in the [learning log](docs/en/LEARNING_LOG.md#en-2026-10-13--phase-33-bm25-retriever).

<a id="en-repository-layout"></a>

## Repository layout

- [rag_api_project/](rag_api_project/) — active FastAPI, RAG, retrieval and evaluation work.
- [docs/](docs/README.md) — all other versioned Markdown: Czech/English guides, agent rules and learning history.
- [.github/](.github/) — CI workflow configuration.
- [archive/](archive/) — 29 earlier programming and machine-learning exercise folders, preserved for learning history and reference.

<a id="en-next-steps"></a>

## Next steps

- Preserve the BM25/Vector DEV and RANDOM baselines from the retrieval comparison recorded on 2026-10-20.
- Implement and evaluate hybrid lexical + semantic retrieval (RRF) without tuning on TEST.
- Improve reproducibility, dependency pinning, operational metrics and onboarding documentation.

[↑ Back to top](#top)
