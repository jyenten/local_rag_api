<a id="top"></a>

# AI RAG Project Roadmap

[Česky](cs/ROADMAP.md#cz) · [English](en/ROADMAP.md#en) · [Dokumentace / Documentation](README.md)

Tento dokument má samostatnou [českou](cs/ROADMAP.md#cz) a [anglickou](en/ROADMAP.md#en) verzi. Otevři vybraný jazyk pro úplný text, obsah a příklady.

This document has separate [Czech](cs/ROADMAP.md#cz) and [English](en/ROADMAP.md#en) versions. Open a language for the full text, contents and examples.

<a id="obsah"></a>

## Starší odkazy na kapitoly / Legacy chapter links

Starší záložky vedou na příslušný řádek níže. Odkaz v řádku otevře úplnou kapitolu. / Older bookmarks lead to the matching row below; follow its link to the full chapter.

| Jazyk / Language | Kapitola / Chapter |
| --- | --- |
| EN | <a id="en"></a><a id="en--english"></a>[EN — English](en/ROADMAP.md#en) |
| EN | <a id="en-status-snapshot--2026-10-28"></a><a id="status-snapshot--2026-10-28"></a>[Status snapshot — 2026-10-28](en/ROADMAP.md#en-status-snapshot--2026-10-28) |
| EN | <a id="en-current-development-focus"></a><a id="current-development-focus"></a>[Current development focus](en/ROADMAP.md#en-current-development-focus) |
| EN | <a id="en-reading-and-updating-the-approved-plan"></a><a id="reading-and-updating-the-approved-plan"></a>[Reading and updating the approved plan](en/ROADMAP.md#en-reading-and-updating-the-approved-plan) |
| EN | <a id="en-phase-1---functional-rag-skeleton"></a><a id="phase-1---functional-rag-skeleton"></a>[PHASE 1 - Functional RAG Skeleton](en/ROADMAP.md#en-phase-1---functional-rag-skeleton) |
| EN | <a id="goal"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="11-appconfigpy"></a>[1.1 `app/config.py`](en/ROADMAP.md#en) |
| EN | <a id="responsibilities"></a>[Responsibilities](en/ROADMAP.md#en) |
| EN | <a id="important-concepts"></a>[Important concepts](en/ROADMAP.md#en) |
| EN | <a id="future-direction"></a>[Future direction](en/ROADMAP.md#en) |
| EN | <a id="12-appschemaspy"></a>[1.2 `app/schemas.py`](en/ROADMAP.md#en) |
| EN | <a id="current-models"></a>[Current models](en/ROADMAP.md#en) |
| EN | <a id="future-possible-models"></a>[Future possible models](en/ROADMAP.md#en) |
| EN | <a id="important-concept"></a>[Important concept](en/ROADMAP.md#en) |
| EN | <a id="13-appretrievalpy"></a>[1.3 `app/retrieval.py`](en/ROADMAP.md#en) |
| EN | <a id="current-responsibilities"></a>[Current responsibilities](en/ROADMAP.md#en) |
| EN | <a id="current-technical-debt"></a>[Current technical debt](en/ROADMAP.md#en) |
| EN | <a id="14-appgenerationpy"></a>[1.4 `app/generation.py`](en/ROADMAP.md#en) |
| EN | <a id="main-responsibilities"></a>[Main responsibilities](en/ROADMAP.md#en) |
| EN | <a id="15-appragpy"></a>[1.5 `app/rag.py`](en/ROADMAP.md#en) |
| EN | <a id="responsibility"></a>[Responsibility](en/ROADMAP.md#en) |
| EN | <a id="current-technical-debt-1"></a>[Current technical debt](en/ROADMAP.md#en) |
| EN | <a id="16-appmainpy"></a>[1.6 `app/main.py`](en/ROADMAP.md#en) |
| EN | <a id="responsibility-1"></a>[Responsibility](en/ROADMAP.md#en) |
| EN | <a id="17-scriptsingestpy"></a>[1.7 `scripts/ingest.py`](en/ROADMAP.md#en) |
| EN | <a id="current-pipeline"></a>[Current pipeline](en/ROADMAP.md#en) |
| EN | <a id="existing-improvements"></a>[Existing improvements](en/ROADMAP.md#en) |
| EN | <a id="important-rule"></a>[Important rule](en/ROADMAP.md#en) |
| EN | <a id="phase-1-definition-of-done"></a>[PHASE 1 Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2---evaluation-foundation"></a><a id="phase-2---evaluation-foundation"></a>[PHASE 2 - Evaluation Foundation](en/ROADMAP.md#en-phase-2---evaluation-foundation) |
| EN | <a id="goal-1"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="evaluation-dataset-roles"></a>[Evaluation Dataset Roles](en/ROADMAP.md#en) |
| EN | <a id="dev"></a>[DEV](en/ROADMAP.md#en) |
| EN | <a id="random"></a>[RANDOM](en/ROADMAP.md#en) |
| EN | <a id="test"></a>[TEST](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2a---universal-document-explorer"></a><a id="phase-2a---universal-document-explorer"></a>[PHASE 2A - Universal Document Explorer](en/ROADMAP.md#en-phase-2a---universal-document-explorer) |
| EN | <a id="goal-2"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="target-structure"></a>[Target Structure](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2a0---architecture-freeze"></a><a id="phase-2a0---architecture-freeze"></a>[PHASE 2A.0 - Architecture Freeze](en/ROADMAP.md#en-phase-2a0---architecture-freeze) |
| EN | <a id="goal-3"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2a1---data-models"></a><a id="phase-2a1---data-models"></a>[PHASE 2A.1 - Data Models](en/ROADMAP.md#en-phase-2a1---data-models) |
| EN | <a id="file"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="planned-models"></a>[Planned models](en/ROADMAP.md#en) |
| EN | <a id="pagedocument"></a>[`PageDocument`](en/ROADMAP.md#en) |
| EN | <a id="searchresult"></a>[`SearchResult`](en/ROADMAP.md#en) |
| EN | <a id="bm25searchindex"></a>[`BM25SearchIndex`](en/ROADMAP.md#en) |
| EN | <a id="new-concept---immutable-dataclasses"></a>[New Concept - Immutable Dataclasses](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2a2---text-processing"></a><a id="phase-2a2---text-processing"></a>[PHASE 2A.2 - Text Processing](en/ROADMAP.md#en-phase-2a2---text-processing) |
| EN | <a id="file-1"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="file-2"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="important-concepts-1"></a>[Important Concepts](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2a3---security-foundations"></a><a id="phase-2a3---security-foundations"></a>[PHASE 2A.3 - Security Foundations](en/ROADMAP.md#en-phase-2a3---security-foundations) |
| EN | <a id="goal-4"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="file-3"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---path-traversal"></a>[New Concept - Path Traversal](en/ROADMAP.md#en) |
| EN | <a id="file-4"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---validation-boundary"></a>[New Concept - Validation Boundary](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2a4---pdf-loading-and-pdf-validation"></a><a id="phase-2a4---pdf-loading-and-pdf-validation"></a>[PHASE 2A.4 - PDF Loading and PDF Validation](en/ROADMAP.md#en-phase-2a4---pdf-loading-and-pdf-validation) |
| EN | <a id="file-5"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---file-signature"></a>[New Concept - File Signature](en/ROADMAP.md#en) |
| EN | <a id="new-concept---resource-exhaustion"></a>[New Concept - Resource Exhaustion](en/ROADMAP.md#en) |
| EN | <a id="file-6"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2a5---bm25-index"></a><a id="phase-2a5---bm25-index"></a>[PHASE 2A.5 - BM25 Index](en/ROADMAP.md#en-phase-2a5---bm25-index) |
| EN | <a id="file-7"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---bm25"></a>[New Concept - BM25](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2a6---search-engine"></a><a id="phase-2a6---search-engine"></a>[PHASE 2A.6 - Search Engine](en/ROADMAP.md#en-phase-2a6---search-engine) |
| EN | <a id="file-8"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="important-new-concept---public-api-boundary"></a>[Important New Concept - Public API Boundary](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2a7---cli"></a><a id="phase-2a7---cli"></a>[PHASE 2A.7 - CLI](en/ROADMAP.md#en-phase-2a7---cli) |
| EN | <a id="file-9"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2a8---integration"></a><a id="phase-2a8---integration"></a>[PHASE 2A.8 - Integration](en/ROADMAP.md#en-phase-2a8---integration) |
| EN | <a id="tasks"></a>[Tasks](en/ROADMAP.md#en) |
| EN | <a id="phase-2a-definition-of-done"></a>[PHASE 2A Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2b---evaluation-data-models"></a><a id="phase-2b---evaluation-data-models"></a>[PHASE 2B - Evaluation Data Models](en/ROADMAP.md#en-phase-2b---evaluation-data-models) |
| EN | <a id="goal-5"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="file-10"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---typed-evaluation-models"></a>[New Concept - Typed Evaluation Models](en/ROADMAP.md#en) |
| EN | <a id="file-11"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---dataset-hashing"></a>[New Concept - Dataset Hashing](en/ROADMAP.md#en) |
| EN | <a id="file-12"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2c---retrieval-metrics"></a><a id="phase-2c---retrieval-metrics"></a>[PHASE 2C - Retrieval Metrics](en/ROADMAP.md#en-phase-2c---retrieval-metrics) |
| EN | <a id="file-13"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="metric---hitk"></a>[Metric - Hit@K](en/ROADMAP.md#en) |
| EN | <a id="metric---reciprocal-rank"></a>[Metric - Reciprocal Rank](en/ROADMAP.md#en) |
| EN | <a id="metric---mrr"></a>[Metric - MRR](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2d---evaluation-runner-and-history"></a><a id="phase-2d---evaluation-runner-and-history"></a>[PHASE 2D - Evaluation Runner and History](en/ROADMAP.md#en-phase-2d---evaluation-runner-and-history) |
| EN | <a id="file-14"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="file-15"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2e---random-evaluation"></a><a id="phase-2e---random-evaluation"></a>[PHASE 2E - RANDOM Evaluation](en/ROADMAP.md#en-phase-2e---random-evaluation) |
| EN | <a id="file-16"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---reproducible-randomness"></a>[New Concept - Reproducible Randomness](en/ROADMAP.md#en) |
| EN | <a id="random-purpose"></a>[RANDOM Purpose](en/ROADMAP.md#en) |
| EN | <a id="en-phase-2f---complete-evaluation-dataset"></a><a id="phase-2f---complete-evaluation-dataset"></a>[PHASE 2F - Complete Evaluation Dataset](en/ROADMAP.md#en-phase-2f---complete-evaluation-dataset) |
| EN | <a id="tasks-1"></a>[Tasks](en/ROADMAP.md#en) |
| EN | <a id="phase-2-definition-of-done"></a>[PHASE 2 Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-3---retrieval-refactor"></a><a id="phase-3---retrieval-refactor"></a>[PHASE 3 - Retrieval Refactor](en/ROADMAP.md#en-phase-3---retrieval-refactor) |
| EN | <a id="goal-6"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="en-phase-31---retrieval-models"></a><a id="phase-31---retrieval-models"></a>[PHASE 3.1 - Retrieval Models](en/ROADMAP.md#en-phase-31---retrieval-models) |
| EN | <a id="file-17"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-32---embeddings"></a><a id="phase-32---embeddings"></a>[PHASE 3.2 - Embeddings](en/ROADMAP.md#en-phase-32---embeddings) |
| EN | <a id="file-18"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-33---vector-search"></a><a id="phase-33---vector-search"></a>[PHASE 3.3 - Vector Search](en/ROADMAP.md#en-phase-33---vector-search) |
| EN | <a id="file-19"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-34---query-processing"></a><a id="phase-34---query-processing"></a>[PHASE 3.4 - Query Processing](en/ROADMAP.md#en-phase-34---query-processing) |
| EN | <a id="file-20"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-35---reranker"></a><a id="phase-35---reranker"></a>[PHASE 3.5 - Reranker](en/ROADMAP.md#en-phase-35---reranker) |
| EN | <a id="file-21"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-36---scoring"></a><a id="phase-36---scoring"></a>[PHASE 3.6 - Scoring](en/ROADMAP.md#en-phase-36---scoring) |
| EN | <a id="file-22"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---rank-fusion"></a>[New Concept - Rank Fusion](en/ROADMAP.md#en) |
| EN | <a id="en-phase-37---retrieval-service"></a><a id="phase-37---retrieval-service"></a>[PHASE 3.7 - Retrieval Service](en/ROADMAP.md#en-phase-37---retrieval-service) |
| EN | <a id="file-23"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="phase-3-definition-of-done"></a>[PHASE 3 Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-4---api-hardening"></a><a id="phase-4---api-hardening"></a>[PHASE 4 - API Hardening](en/ROADMAP.md#en-phase-4---api-hardening) |
| EN | <a id="goal-7"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="en-phase-41---application-lifecycle"></a><a id="phase-41---application-lifecycle"></a>[PHASE 4.1 - Application Lifecycle](en/ROADMAP.md#en-phase-41---application-lifecycle) |
| EN | <a id="file-24"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---fastapi-lifespan"></a>[New Concept - FastAPI Lifespan](en/ROADMAP.md#en) |
| EN | <a id="en-phase-42---routes"></a><a id="phase-42---routes"></a>[PHASE 4.2 - Routes](en/ROADMAP.md#en-phase-42---routes) |
| EN | <a id="file-25"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-43---dependency-injection"></a><a id="phase-43---dependency-injection"></a>[PHASE 4.3 - Dependency Injection](en/ROADMAP.md#en-phase-43---dependency-injection) |
| EN | <a id="file-26"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---dependency-injection"></a>[New Concept - Dependency Injection](en/ROADMAP.md#en) |
| EN | <a id="en-phase-44---errors"></a><a id="phase-44---errors"></a>[PHASE 4.4 - Errors](en/ROADMAP.md#en-phase-44---errors) |
| EN | <a id="file-27"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-45---middleware"></a><a id="phase-45---middleware"></a>[PHASE 4.5 - Middleware](en/ROADMAP.md#en-phase-45---middleware) |
| EN | <a id="file-28"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="phase-4-definition-of-done"></a>[PHASE 4 Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-5---production-engineering"></a><a id="phase-5---production-engineering"></a>[PHASE 5 - Production Engineering](en/ROADMAP.md#en-phase-5---production-engineering) |
| EN | <a id="goal-8"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="en-phase-51---linux--wsl2"></a><a id="phase-51---linux--wsl2"></a>[PHASE 5.1 - Linux / WSL2](en/ROADMAP.md#en-phase-51---linux--wsl2) |
| EN | <a id="goal-9"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="new-concept---environment-portability"></a>[New Concept - Environment Portability](en/ROADMAP.md#en) |
| EN | <a id="en-phase-52---structured-logging"></a><a id="phase-52---structured-logging"></a>[PHASE 5.2 - Structured Logging](en/ROADMAP.md#en-phase-52---structured-logging) |
| EN | <a id="file-29"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---structured-logging"></a>[New Concept - Structured Logging](en/ROADMAP.md#en) |
| EN | <a id="en-phase-53---runtime-metrics"></a><a id="phase-53---runtime-metrics"></a>[PHASE 5.3 - Runtime Metrics](en/ROADMAP.md#en-phase-53---runtime-metrics) |
| EN | <a id="file-30"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---quality-vs-operational-metrics"></a>[New Concept - Quality vs Operational Metrics](en/ROADMAP.md#en) |
| EN | <a id="en-phase-54---docker-hardening"></a><a id="phase-54---docker-hardening"></a>[PHASE 5.4 - Docker Hardening](en/ROADMAP.md#en-phase-54---docker-hardening) |
| EN | <a id="new-concept---multi-stage-docker-build"></a>[New Concept - Multi-stage Docker Build](en/ROADMAP.md#en) |
| EN | <a id="en-phase-55---cicd"></a><a id="phase-55---cicd"></a>[PHASE 5.5 - CI/CD](en/ROADMAP.md#en-phase-55---cicd) |
| EN | <a id="phase-5-definition-of-done"></a>[PHASE 5 Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-6---security"></a><a id="phase-6---security"></a>[PHASE 6 - Security](en/ROADMAP.md#en-phase-6---security) |
| EN | <a id="goal-10"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="en-phase-61---threat-modeling"></a><a id="phase-61---threat-modeling"></a>[PHASE 6.1 - Threat Modeling](en/ROADMAP.md#en-phase-61---threat-modeling) |
| EN | <a id="new-concept---threat-model"></a>[New Concept - Threat Model](en/ROADMAP.md#en) |
| EN | <a id="en-phase-62---runtime-input-validation"></a><a id="phase-62---runtime-input-validation"></a>[PHASE 6.2 - Runtime Input Validation](en/ROADMAP.md#en-phase-62---runtime-input-validation) |
| EN | <a id="file-31"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-63---runtime-limits"></a><a id="phase-63---runtime-limits"></a>[PHASE 6.3 - Runtime Limits](en/ROADMAP.md#en-phase-63---runtime-limits) |
| EN | <a id="file-32"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-64---secrets"></a><a id="phase-64---secrets"></a>[PHASE 6.4 - Secrets](en/ROADMAP.md#en-phase-64---secrets) |
| EN | <a id="en-phase-65---dependency-security"></a><a id="phase-65---dependency-security"></a>[PHASE 6.5 - Dependency Security](en/ROADMAP.md#en-phase-65---dependency-security) |
| EN | <a id="en-phase-66---container-security"></a><a id="phase-66---container-security"></a>[PHASE 6.6 - Container Security](en/ROADMAP.md#en-phase-66---container-security) |
| EN | <a id="en-phase-67---http-security"></a><a id="phase-67---http-security"></a>[PHASE 6.7 - HTTP Security](en/ROADMAP.md#en-phase-67---http-security) |
| EN | <a id="en-phase-68---rag-specific-security"></a><a id="phase-68---rag-specific-security"></a>[PHASE 6.8 - RAG-Specific Security](en/ROADMAP.md#en-phase-68---rag-specific-security) |
| EN | <a id="new-concept---indirect-prompt-injection"></a>[New Concept - Indirect Prompt Injection](en/ROADMAP.md#en) |
| EN | <a id="phase-6-definition-of-done"></a>[PHASE 6 Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-7---production-v1"></a><a id="phase-7---production-v1"></a>[PHASE 7 - Production v1](en/ROADMAP.md#en-phase-7---production-v1) |
| EN | <a id="goal-11"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="en-phase-71---health-and-readiness"></a><a id="phase-71---health-and-readiness"></a>[PHASE 7.1 - Health and Readiness](en/ROADMAP.md#en-phase-71---health-and-readiness) |
| EN | <a id="new-concept---liveness-vs-readiness"></a>[New Concept - Liveness vs Readiness](en/ROADMAP.md#en) |
| EN | <a id="liveness"></a>[Liveness](en/ROADMAP.md#en) |
| EN | <a id="readiness"></a>[Readiness](en/ROADMAP.md#en) |
| EN | <a id="en-phase-72---production-smoke-test"></a><a id="phase-72---production-smoke-test"></a>[PHASE 7.2 - Production Smoke Test](en/ROADMAP.md#en-phase-72---production-smoke-test) |
| EN | <a id="file-33"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="en-phase-73---documentation"></a><a id="phase-73---documentation"></a>[PHASE 7.3 - Documentation](en/ROADMAP.md#en-phase-73---documentation) |
| EN | <a id="phase-7-definition-of-done"></a>[PHASE 7 Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-8---expansion"></a><a id="phase-8---expansion"></a>[PHASE 8 - Expansion](en/ROADMAP.md#en-phase-8---expansion) |
| EN | <a id="en-phase-8a---agent-exploration"></a><a id="phase-8a---agent-exploration"></a>[PHASE 8A - Agent Exploration](en/ROADMAP.md#en-phase-8a---agent-exploration) |
| EN | <a id="goal-12"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="file-34"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---tool-calling"></a>[New Concept - Tool Calling](en/ROADMAP.md#en) |
| EN | <a id="phase-8a-definition-of-done"></a>[PHASE 8A Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-8b---sql-and-etl"></a><a id="phase-8b---sql-and-etl"></a>[PHASE 8B - SQL and ETL](en/ROADMAP.md#en-phase-8b---sql-and-etl) |
| EN | <a id="goal-13"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="file-35"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="file-36"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="file-37"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="file-38"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---etl"></a>[New Concept - ETL](en/ROADMAP.md#en) |
| EN | <a id="phase-8b-definition-of-done"></a>[PHASE 8B Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-8c---mlops"></a><a id="phase-8c---mlops"></a>[PHASE 8C - MLOps](en/ROADMAP.md#en-phase-8c---mlops) |
| EN | <a id="goal-14"></a>[Goal](en/ROADMAP.md#en) |
| EN | <a id="file-39"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="new-concept---experiment-tracking"></a>[New Concept - Experiment Tracking](en/ROADMAP.md#en) |
| EN | <a id="file-40"></a>[File](en/ROADMAP.md#en) |
| EN | <a id="phase-8c-definition-of-done"></a>[PHASE 8C Definition of Done](en/ROADMAP.md#en) |
| EN | <a id="en-phase-8d---advanced-agents"></a><a id="phase-8d---advanced-agents"></a>[PHASE 8D - Advanced Agents](en/ROADMAP.md#en-phase-8d---advanced-agents) |
| EN | <a id="en-original-planning-estimates--historical"></a><a id="original-planning-estimates--historical"></a>[Original planning estimates — historical](en/ROADMAP.md#en-original-planning-estimates--historical) |
| EN | <a id="en-planning-history"></a><a id="planning-history"></a>[Planning history](en/ROADMAP.md#en-planning-history) |
| CZ | <a id="cz"></a><a id="cz--česká-verze"></a>[CZ — Česká verze](cs/ROADMAP.md#cz) |
| CZ | <a id="cz-stavový-přehled--2026-10-28"></a><a id="stavový-přehled--2026-10-28"></a>[Stavový přehled — 2026-10-28](cs/ROADMAP.md#cz-stavový-přehled--2026-10-28) |
| CZ | <a id="cz-aktuální-zaměření-vývoje"></a><a id="aktuální-zaměření-vývoje"></a>[Aktuální zaměření vývoje](cs/ROADMAP.md#cz-aktuální-zaměření-vývoje) |
| CZ | <a id="cz-jak-číst-a-aktualizovat-schválený-plán"></a><a id="jak-číst-a-aktualizovat-schválený-plán"></a>[Jak číst a aktualizovat schválený plán](cs/ROADMAP.md#cz-jak-číst-a-aktualizovat-schválený-plán) |
| CZ | <a id="cz-fáze-1---funkční-kostra-rag"></a><a id="fáze-1---funkční-kostra-rag"></a>[FÁZE 1 - Funkční kostra RAG](cs/ROADMAP.md#cz-fáze-1---funkční-kostra-rag) |
| CZ | <a id="cz-cíl"></a><a id="cíl"></a>[Cíl](cs/ROADMAP.md#cz-cíl) |
| CZ | <a id="cz-11-appconfigpy"></a><a id="11-appconfigpy-1"></a>[1.1 `app/config.py`](cs/ROADMAP.md#cz-11-appconfigpy) |
| CZ | <a id="cz-odpovědnosti"></a><a id="odpovědnosti"></a>[Odpovědnosti](cs/ROADMAP.md#cz-odpovědnosti) |
| CZ | <a id="cz-důležité-koncepty"></a><a id="důležité-koncepty"></a>[Důležité koncepty](cs/ROADMAP.md#cz-důležité-koncepty) |
| CZ | <a id="cz-budoucí-směr"></a><a id="budoucí-směr"></a>[Budoucí směr](cs/ROADMAP.md#cz-budoucí-směr) |
| CZ | <a id="cz-12-appschemaspy"></a><a id="12-appschemaspy-1"></a>[1.2 `app/schemas.py`](cs/ROADMAP.md#cz-12-appschemaspy) |
| CZ | <a id="cz-současné-modely"></a><a id="současné-modely"></a>[Současné modely](cs/ROADMAP.md#cz-současné-modely) |
| CZ | <a id="cz-možné-budoucí-modely"></a><a id="možné-budoucí-modely"></a>[Možné budoucí modely](cs/ROADMAP.md#cz-možné-budoucí-modely) |
| CZ | <a id="cz-důležitý-koncept"></a><a id="důležitý-koncept"></a>[Důležitý koncept](cs/ROADMAP.md#cz-důležitý-koncept) |
| CZ | <a id="cz-13-appretrievalpy"></a><a id="13-appretrievalpy-1"></a>[1.3 `app/retrieval.py`](cs/ROADMAP.md#cz-13-appretrievalpy) |
| CZ | <a id="cz-současné-odpovědnosti"></a><a id="současné-odpovědnosti"></a>[Současné odpovědnosti](cs/ROADMAP.md#cz-současné-odpovědnosti) |
| CZ | <a id="cz-současný-technický-dluh"></a><a id="současný-technický-dluh"></a>[Současný technický dluh](cs/ROADMAP.md#cz-současný-technický-dluh) |
| CZ | <a id="cz-14-appgenerationpy"></a><a id="14-appgenerationpy-1"></a>[1.4 `app/generation.py`](cs/ROADMAP.md#cz-14-appgenerationpy) |
| CZ | <a id="cz-hlavní-odpovědnosti"></a><a id="hlavní-odpovědnosti"></a>[Hlavní odpovědnosti](cs/ROADMAP.md#cz-hlavní-odpovědnosti) |
| CZ | <a id="cz-15-appragpy"></a><a id="15-appragpy-1"></a>[1.5 `app/rag.py`](cs/ROADMAP.md#cz-15-appragpy) |
| CZ | <a id="cz-odpovědnost"></a><a id="odpovědnost"></a>[Odpovědnost](cs/ROADMAP.md#cz-odpovědnost) |
| CZ | <a id="cz-současný-technický-dluh-1"></a><a id="současný-technický-dluh-1"></a>[Současný technický dluh](cs/ROADMAP.md#cz-současný-technický-dluh-1) |
| CZ | <a id="cz-16-appmainpy"></a><a id="16-appmainpy-1"></a>[1.6 `app/main.py`](cs/ROADMAP.md#cz-16-appmainpy) |
| CZ | <a id="cz-odpovědnost-1"></a><a id="odpovědnost-1"></a>[Odpovědnost](cs/ROADMAP.md#cz-odpovědnost-1) |
| CZ | <a id="cz-17-scriptsingestpy"></a><a id="17-scriptsingestpy-1"></a>[1.7 `scripts/ingest.py`](cs/ROADMAP.md#cz-17-scriptsingestpy) |
| CZ | <a id="cz-současná-pipeline"></a><a id="současná-pipeline"></a>[Současná pipeline](cs/ROADMAP.md#cz-současná-pipeline) |
| CZ | <a id="cz-dosavadní-zlepšení"></a><a id="dosavadní-zlepšení"></a>[Dosavadní zlepšení](cs/ROADMAP.md#cz-dosavadní-zlepšení) |
| CZ | <a id="cz-důležité-pravidlo"></a><a id="důležité-pravidlo"></a>[Důležité pravidlo](cs/ROADMAP.md#cz-důležité-pravidlo) |
| CZ | <a id="cz-fáze-1--podmínky-dokončení"></a><a id="fáze-1--podmínky-dokončení"></a>[FÁZE 1 — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-1--podmínky-dokončení) |
| CZ | <a id="cz-fáze-2---základ-evaluace"></a><a id="fáze-2---základ-evaluace"></a>[FÁZE 2 - Základ evaluace](cs/ROADMAP.md#cz-fáze-2---základ-evaluace) |
| CZ | <a id="cz-cíl-1"></a><a id="cíl-1"></a>[Cíl](cs/ROADMAP.md#cz-cíl-1) |
| CZ | <a id="cz-úlohy-evaluačních-datasetů"></a><a id="úlohy-evaluačních-datasetů"></a>[Úlohy evaluačních datasetů](cs/ROADMAP.md#cz-úlohy-evaluačních-datasetů) |
| CZ | <a id="cz-dev"></a><a id="dev-1"></a>[DEV](cs/ROADMAP.md#cz-dev) |
| CZ | <a id="cz-random"></a><a id="random-1"></a>[RANDOM](cs/ROADMAP.md#cz-random) |
| CZ | <a id="cz-test"></a><a id="test-1"></a>[TEST](cs/ROADMAP.md#cz-test) |
| CZ | <a id="cz-fáze-2a---univerzální-průzkumník-dokumentů"></a><a id="fáze-2a---univerzální-průzkumník-dokumentů"></a>[FÁZE 2A - Univerzální průzkumník dokumentů](cs/ROADMAP.md#cz-fáze-2a---univerzální-průzkumník-dokumentů) |
| CZ | <a id="cz-cíl-2"></a><a id="cíl-2"></a>[Cíl](cs/ROADMAP.md#cz-cíl-2) |
| CZ | <a id="cz-cílová-struktura"></a><a id="cílová-struktura"></a>[Cílová struktura](cs/ROADMAP.md#cz-cílová-struktura) |
| CZ | <a id="cz-fáze-2a0---zmrazení-architektury"></a><a id="fáze-2a0---zmrazení-architektury"></a>[FÁZE 2A.0 - Zmrazení architektury](cs/ROADMAP.md#cz-fáze-2a0---zmrazení-architektury) |
| CZ | <a id="cz-cíl-3"></a><a id="cíl-3"></a>[Cíl](cs/ROADMAP.md#cz-cíl-3) |
| CZ | <a id="cz-fáze-2a1---datové-modely"></a><a id="fáze-2a1---datové-modely"></a>[FÁZE 2A.1 - Datové modely](cs/ROADMAP.md#cz-fáze-2a1---datové-modely) |
| CZ | <a id="cz-soubor"></a><a id="soubor"></a>[Soubor](cs/ROADMAP.md#cz-soubor) |
| CZ | <a id="cz-plánované-modely"></a><a id="plánované-modely"></a>[Plánované modely](cs/ROADMAP.md#cz-plánované-modely) |
| CZ | <a id="cz-pagedocument"></a><a id="pagedocument-1"></a>[`PageDocument`](cs/ROADMAP.md#cz-pagedocument) |
| CZ | <a id="cz-searchresult"></a><a id="searchresult-1"></a>[`SearchResult`](cs/ROADMAP.md#cz-searchresult) |
| CZ | <a id="cz-bm25searchindex"></a><a id="bm25searchindex-1"></a>[`BM25SearchIndex`](cs/ROADMAP.md#cz-bm25searchindex) |
| CZ | <a id="cz-nový-koncept---neměnné-datové-třídy"></a><a id="nový-koncept---neměnné-datové-třídy"></a>[Nový koncept - Neměnné datové třídy](cs/ROADMAP.md#cz-nový-koncept---neměnné-datové-třídy) |
| CZ | <a id="cz-fáze-2a2---zpracování-textu"></a><a id="fáze-2a2---zpracování-textu"></a>[FÁZE 2A.2 - Zpracování textu](cs/ROADMAP.md#cz-fáze-2a2---zpracování-textu) |
| CZ | <a id="cz-soubor-1"></a><a id="soubor-1"></a>[Soubor](cs/ROADMAP.md#cz-soubor-1) |
| CZ | <a id="cz-soubor-2"></a><a id="soubor-2"></a>[Soubor](cs/ROADMAP.md#cz-soubor-2) |
| CZ | <a id="cz-důležité-koncepty-1"></a><a id="důležité-koncepty-1"></a>[Důležité koncepty](cs/ROADMAP.md#cz-důležité-koncepty-1) |
| CZ | <a id="cz-fáze-2a3---základy-bezpečnosti"></a><a id="fáze-2a3---základy-bezpečnosti"></a>[FÁZE 2A.3 - Základy bezpečnosti](cs/ROADMAP.md#cz-fáze-2a3---základy-bezpečnosti) |
| CZ | <a id="cz-cíl-4"></a><a id="cíl-4"></a>[Cíl](cs/ROADMAP.md#cz-cíl-4) |
| CZ | <a id="cz-soubor-3"></a><a id="soubor-3"></a>[Soubor](cs/ROADMAP.md#cz-soubor-3) |
| CZ | <a id="cz-nový-koncept---path-traversal"></a><a id="nový-koncept---path-traversal"></a>[Nový koncept - Path traversal](cs/ROADMAP.md#cz-nový-koncept---path-traversal) |
| CZ | <a id="cz-soubor-4"></a><a id="soubor-4"></a>[Soubor](cs/ROADMAP.md#cz-soubor-4) |
| CZ | <a id="cz-nový-koncept---validační-hranice"></a><a id="nový-koncept---validační-hranice"></a>[Nový koncept - Validační hranice](cs/ROADMAP.md#cz-nový-koncept---validační-hranice) |
| CZ | <a id="cz-fáze-2a4---načítání-pdf-a-validace-pdf"></a><a id="fáze-2a4---načítání-pdf-a-validace-pdf"></a>[FÁZE 2A.4 - Načítání PDF a validace PDF](cs/ROADMAP.md#cz-fáze-2a4---načítání-pdf-a-validace-pdf) |
| CZ | <a id="cz-soubor-5"></a><a id="soubor-5"></a>[Soubor](cs/ROADMAP.md#cz-soubor-5) |
| CZ | <a id="cz-nový-koncept---signatura-souboru"></a><a id="nový-koncept---signatura-souboru"></a>[Nový koncept - Signatura souboru](cs/ROADMAP.md#cz-nový-koncept---signatura-souboru) |
| CZ | <a id="cz-nový-koncept---vyčerpání-prostředků"></a><a id="nový-koncept---vyčerpání-prostředků"></a>[Nový koncept - Vyčerpání prostředků](cs/ROADMAP.md#cz-nový-koncept---vyčerpání-prostředků) |
| CZ | <a id="cz-soubor-6"></a><a id="soubor-6"></a>[Soubor](cs/ROADMAP.md#cz-soubor-6) |
| CZ | <a id="cz-fáze-2a5---bm25-index"></a><a id="fáze-2a5---bm25-index"></a>[FÁZE 2A.5 - BM25 index](cs/ROADMAP.md#cz-fáze-2a5---bm25-index) |
| CZ | <a id="cz-soubor-7"></a><a id="soubor-7"></a>[Soubor](cs/ROADMAP.md#cz-soubor-7) |
| CZ | <a id="cz-nový-koncept---bm25"></a><a id="nový-koncept---bm25"></a>[Nový koncept - BM25](cs/ROADMAP.md#cz-nový-koncept---bm25) |
| CZ | <a id="cz-fáze-2a6---vyhledávací-modul"></a><a id="fáze-2a6---vyhledávací-modul"></a>[FÁZE 2A.6 - Vyhledávací modul](cs/ROADMAP.md#cz-fáze-2a6---vyhledávací-modul) |
| CZ | <a id="cz-soubor-8"></a><a id="soubor-8"></a>[Soubor](cs/ROADMAP.md#cz-soubor-8) |
| CZ | <a id="cz-důležitý-nový-koncept---hranice-veřejného-api"></a><a id="důležitý-nový-koncept---hranice-veřejného-api"></a>[Důležitý nový koncept - Hranice veřejného API](cs/ROADMAP.md#cz-důležitý-nový-koncept---hranice-veřejného-api) |
| CZ | <a id="cz-fáze-2a7---cli"></a><a id="fáze-2a7---cli"></a>[FÁZE 2A.7 - CLI](cs/ROADMAP.md#cz-fáze-2a7---cli) |
| CZ | <a id="cz-soubor-9"></a><a id="soubor-9"></a>[Soubor](cs/ROADMAP.md#cz-soubor-9) |
| CZ | <a id="cz-fáze-2a8---integrace"></a><a id="fáze-2a8---integrace"></a>[FÁZE 2A.8 - Integrace](cs/ROADMAP.md#cz-fáze-2a8---integrace) |
| CZ | <a id="cz-úkoly"></a><a id="úkoly"></a>[Úkoly](cs/ROADMAP.md#cz-úkoly) |
| CZ | <a id="cz-fáze-2a--podmínky-dokončení"></a><a id="fáze-2a--podmínky-dokončení"></a>[FÁZE 2A — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-2a--podmínky-dokončení) |
| CZ | <a id="cz-fáze-2b---evaluační-datové-modely"></a><a id="fáze-2b---evaluační-datové-modely"></a>[FÁZE 2B - Evaluační datové modely](cs/ROADMAP.md#cz-fáze-2b---evaluační-datové-modely) |
| CZ | <a id="cz-cíl-5"></a><a id="cíl-5"></a>[Cíl](cs/ROADMAP.md#cz-cíl-5) |
| CZ | <a id="cz-soubor-10"></a><a id="soubor-10"></a>[Soubor](cs/ROADMAP.md#cz-soubor-10) |
| CZ | <a id="cz-nový-koncept---typované-evaluační-modely"></a><a id="nový-koncept---typované-evaluační-modely"></a>[Nový koncept - Typované evaluační modely](cs/ROADMAP.md#cz-nový-koncept---typované-evaluační-modely) |
| CZ | <a id="cz-soubor-11"></a><a id="soubor-11"></a>[Soubor](cs/ROADMAP.md#cz-soubor-11) |
| CZ | <a id="cz-nový-koncept---hashování-datasetu"></a><a id="nový-koncept---hashování-datasetu"></a>[Nový koncept - Hashování datasetu](cs/ROADMAP.md#cz-nový-koncept---hashování-datasetu) |
| CZ | <a id="cz-soubor-12"></a><a id="soubor-12"></a>[Soubor](cs/ROADMAP.md#cz-soubor-12) |
| CZ | <a id="cz-fáze-2c---metriky-retrievalu"></a><a id="fáze-2c---metriky-retrievalu"></a>[FÁZE 2C - Metriky retrievalu](cs/ROADMAP.md#cz-fáze-2c---metriky-retrievalu) |
| CZ | <a id="cz-soubor-13"></a><a id="soubor-13"></a>[Soubor](cs/ROADMAP.md#cz-soubor-13) |
| CZ | <a id="cz-metrika---hitk"></a><a id="metrika---hitk"></a>[Metrika - Hit@K](cs/ROADMAP.md#cz-metrika---hitk) |
| CZ | <a id="cz-metrika---reciproční-pořadí"></a><a id="metrika---reciproční-pořadí"></a>[Metrika - Reciproční pořadí](cs/ROADMAP.md#cz-metrika---reciproční-pořadí) |
| CZ | <a id="cz-metrika---mrr"></a><a id="metrika---mrr"></a>[Metrika - MRR](cs/ROADMAP.md#cz-metrika---mrr) |
| CZ | <a id="cz-fáze-2d---evaluační-runner-a-historie"></a><a id="fáze-2d---evaluační-runner-a-historie"></a>[FÁZE 2D - Evaluační runner a historie](cs/ROADMAP.md#cz-fáze-2d---evaluační-runner-a-historie) |
| CZ | <a id="cz-soubor-14"></a><a id="soubor-14"></a>[Soubor](cs/ROADMAP.md#cz-soubor-14) |
| CZ | <a id="cz-soubor-15"></a><a id="soubor-15"></a>[Soubor](cs/ROADMAP.md#cz-soubor-15) |
| CZ | <a id="cz-fáze-2e---evaluace-random"></a><a id="fáze-2e---evaluace-random"></a>[FÁZE 2E - Evaluace RANDOM](cs/ROADMAP.md#cz-fáze-2e---evaluace-random) |
| CZ | <a id="cz-soubor-16"></a><a id="soubor-16"></a>[Soubor](cs/ROADMAP.md#cz-soubor-16) |
| CZ | <a id="cz-nový-koncept---reprodukovatelná-náhodnost"></a><a id="nový-koncept---reprodukovatelná-náhodnost"></a>[Nový koncept - Reprodukovatelná náhodnost](cs/ROADMAP.md#cz-nový-koncept---reprodukovatelná-náhodnost) |
| CZ | <a id="cz-účel-random"></a><a id="účel-random"></a>[Účel RANDOM](cs/ROADMAP.md#cz-účel-random) |
| CZ | <a id="cz-fáze-2f---kompletní-evaluační-dataset"></a><a id="fáze-2f---kompletní-evaluační-dataset"></a>[FÁZE 2F - Kompletní evaluační dataset](cs/ROADMAP.md#cz-fáze-2f---kompletní-evaluační-dataset) |
| CZ | <a id="cz-úkoly-1"></a><a id="úkoly-1"></a>[Úkoly](cs/ROADMAP.md#cz-úkoly-1) |
| CZ | <a id="cz-fáze-2--podmínky-dokončení"></a><a id="fáze-2--podmínky-dokončení"></a>[FÁZE 2 — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-2--podmínky-dokončení) |
| CZ | <a id="cz-fáze-3---refaktoring-retrievalu"></a><a id="fáze-3---refaktoring-retrievalu"></a>[FÁZE 3 - Refaktoring retrievalu](cs/ROADMAP.md#cz-fáze-3---refaktoring-retrievalu) |
| CZ | <a id="cz-cíl-6"></a><a id="cíl-6"></a>[Cíl](cs/ROADMAP.md#cz-cíl-6) |
| CZ | <a id="cz-fáze-31---retrieval-modely"></a><a id="fáze-31---retrieval-modely"></a>[FÁZE 3.1 - Retrieval modely](cs/ROADMAP.md#cz-fáze-31---retrieval-modely) |
| CZ | <a id="cz-soubor-17"></a><a id="soubor-17"></a>[Soubor](cs/ROADMAP.md#cz-soubor-17) |
| CZ | <a id="cz-fáze-32---embeddingy"></a><a id="fáze-32---embeddingy"></a>[FÁZE 3.2 - Embeddingy](cs/ROADMAP.md#cz-fáze-32---embeddingy) |
| CZ | <a id="cz-soubor-18"></a><a id="soubor-18"></a>[Soubor](cs/ROADMAP.md#cz-soubor-18) |
| CZ | <a id="cz-fáze-33---vektorové-vyhledávání"></a><a id="fáze-33---vektorové-vyhledávání"></a>[FÁZE 3.3 - Vektorové vyhledávání](cs/ROADMAP.md#cz-fáze-33---vektorové-vyhledávání) |
| CZ | <a id="cz-soubor-19"></a><a id="soubor-19"></a>[Soubor](cs/ROADMAP.md#cz-soubor-19) |
| CZ | <a id="cz-fáze-34---zpracování-dotazu"></a><a id="fáze-34---zpracování-dotazu"></a>[FÁZE 3.4 - Zpracování dotazu](cs/ROADMAP.md#cz-fáze-34---zpracování-dotazu) |
| CZ | <a id="cz-soubor-20"></a><a id="soubor-20"></a>[Soubor](cs/ROADMAP.md#cz-soubor-20) |
| CZ | <a id="cz-fáze-35---reranker"></a><a id="fáze-35---reranker"></a>[FÁZE 3.5 - Reranker](cs/ROADMAP.md#cz-fáze-35---reranker) |
| CZ | <a id="cz-soubor-21"></a><a id="soubor-21"></a>[Soubor](cs/ROADMAP.md#cz-soubor-21) |
| CZ | <a id="cz-fáze-36---skórování"></a><a id="fáze-36---skórování"></a>[FÁZE 3.6 - Skórování](cs/ROADMAP.md#cz-fáze-36---skórování) |
| CZ | <a id="cz-soubor-22"></a><a id="soubor-22"></a>[Soubor](cs/ROADMAP.md#cz-soubor-22) |
| CZ | <a id="cz-nový-koncept---slučování-pořadí"></a><a id="nový-koncept---slučování-pořadí"></a>[Nový koncept - Slučování pořadí](cs/ROADMAP.md#cz-nový-koncept---slučování-pořadí) |
| CZ | <a id="cz-fáze-37---retrieval-služba"></a><a id="fáze-37---retrieval-služba"></a>[FÁZE 3.7 - Retrieval služba](cs/ROADMAP.md#cz-fáze-37---retrieval-služba) |
| CZ | <a id="cz-soubor-23"></a><a id="soubor-23"></a>[Soubor](cs/ROADMAP.md#cz-soubor-23) |
| CZ | <a id="cz-fáze-3--podmínky-dokončení"></a><a id="fáze-3--podmínky-dokončení"></a>[FÁZE 3 — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-3--podmínky-dokončení) |
| CZ | <a id="cz-fáze-4---zodolnění-api"></a><a id="fáze-4---zodolnění-api"></a>[FÁZE 4 - Zodolnění API](cs/ROADMAP.md#cz-fáze-4---zodolnění-api) |
| CZ | <a id="cz-cíl-7"></a><a id="cíl-7"></a>[Cíl](cs/ROADMAP.md#cz-cíl-7) |
| CZ | <a id="cz-fáze-41---životní-cyklus-aplikace"></a><a id="fáze-41---životní-cyklus-aplikace"></a>[FÁZE 4.1 - Životní cyklus aplikace](cs/ROADMAP.md#cz-fáze-41---životní-cyklus-aplikace) |
| CZ | <a id="cz-soubor-24"></a><a id="soubor-24"></a>[Soubor](cs/ROADMAP.md#cz-soubor-24) |
| CZ | <a id="cz-nový-koncept---fastapi-lifespan"></a><a id="nový-koncept---fastapi-lifespan"></a>[Nový koncept - FastAPI lifespan](cs/ROADMAP.md#cz-nový-koncept---fastapi-lifespan) |
| CZ | <a id="cz-fáze-42---routy"></a><a id="fáze-42---routy"></a>[FÁZE 4.2 - Routy](cs/ROADMAP.md#cz-fáze-42---routy) |
| CZ | <a id="cz-soubor-25"></a><a id="soubor-25"></a>[Soubor](cs/ROADMAP.md#cz-soubor-25) |
| CZ | <a id="cz-fáze-43---vkládání-závislostí"></a><a id="fáze-43---vkládání-závislostí"></a>[FÁZE 4.3 - Vkládání závislostí](cs/ROADMAP.md#cz-fáze-43---vkládání-závislostí) |
| CZ | <a id="cz-soubor-26"></a><a id="soubor-26"></a>[Soubor](cs/ROADMAP.md#cz-soubor-26) |
| CZ | <a id="cz-nový-koncept---dependency-injection"></a><a id="nový-koncept---dependency-injection"></a>[Nový koncept - Dependency injection](cs/ROADMAP.md#cz-nový-koncept---dependency-injection) |
| CZ | <a id="cz-fáze-44---chyby"></a><a id="fáze-44---chyby"></a>[FÁZE 4.4 - Chyby](cs/ROADMAP.md#cz-fáze-44---chyby) |
| CZ | <a id="cz-soubor-27"></a><a id="soubor-27"></a>[Soubor](cs/ROADMAP.md#cz-soubor-27) |
| CZ | <a id="cz-fáze-45---middleware"></a><a id="fáze-45---middleware"></a>[FÁZE 4.5 - Middleware](cs/ROADMAP.md#cz-fáze-45---middleware) |
| CZ | <a id="cz-soubor-28"></a><a id="soubor-28"></a>[Soubor](cs/ROADMAP.md#cz-soubor-28) |
| CZ | <a id="cz-fáze-4--podmínky-dokončení"></a><a id="fáze-4--podmínky-dokončení"></a>[FÁZE 4 — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-4--podmínky-dokončení) |
| CZ | <a id="cz-fáze-5---produkční-inženýrství"></a><a id="fáze-5---produkční-inženýrství"></a>[FÁZE 5 - Produkční inženýrství](cs/ROADMAP.md#cz-fáze-5---produkční-inženýrství) |
| CZ | <a id="cz-cíl-8"></a><a id="cíl-8"></a>[Cíl](cs/ROADMAP.md#cz-cíl-8) |
| CZ | <a id="cz-fáze-51---linux--wsl2"></a><a id="fáze-51---linux--wsl2"></a>[FÁZE 5.1 - Linux / WSL2](cs/ROADMAP.md#cz-fáze-51---linux--wsl2) |
| CZ | <a id="cz-cíl-9"></a><a id="cíl-9"></a>[Cíl](cs/ROADMAP.md#cz-cíl-9) |
| CZ | <a id="cz-nový-koncept---přenositelnost-prostředí"></a><a id="nový-koncept---přenositelnost-prostředí"></a>[Nový koncept - Přenositelnost prostředí](cs/ROADMAP.md#cz-nový-koncept---přenositelnost-prostředí) |
| CZ | <a id="cz-fáze-52---strukturované-logování"></a><a id="fáze-52---strukturované-logování"></a>[FÁZE 5.2 - Strukturované logování](cs/ROADMAP.md#cz-fáze-52---strukturované-logování) |
| CZ | <a id="cz-soubor-29"></a><a id="soubor-29"></a>[Soubor](cs/ROADMAP.md#cz-soubor-29) |
| CZ | <a id="cz-nový-koncept---strukturované-logování"></a><a id="nový-koncept---strukturované-logování"></a>[Nový koncept - Strukturované logování](cs/ROADMAP.md#cz-nový-koncept---strukturované-logování) |
| CZ | <a id="cz-fáze-53---běhové-metriky"></a><a id="fáze-53---běhové-metriky"></a>[FÁZE 5.3 - Běhové metriky](cs/ROADMAP.md#cz-fáze-53---běhové-metriky) |
| CZ | <a id="cz-soubor-30"></a><a id="soubor-30"></a>[Soubor](cs/ROADMAP.md#cz-soubor-30) |
| CZ | <a id="cz-nový-koncept---kvalitativní-a-provozní-metriky"></a><a id="nový-koncept---kvalitativní-a-provozní-metriky"></a>[Nový koncept - Kvalitativní a provozní metriky](cs/ROADMAP.md#cz-nový-koncept---kvalitativní-a-provozní-metriky) |
| CZ | <a id="cz-fáze-54---zodolnění-dockeru"></a><a id="fáze-54---zodolnění-dockeru"></a>[FÁZE 5.4 - Zodolnění Dockeru](cs/ROADMAP.md#cz-fáze-54---zodolnění-dockeru) |
| CZ | <a id="cz-nový-koncept---vícestupňový-docker-build"></a><a id="nový-koncept---vícestupňový-docker-build"></a>[Nový koncept - Vícestupňový Docker build](cs/ROADMAP.md#cz-nový-koncept---vícestupňový-docker-build) |
| CZ | <a id="cz-fáze-55---cicd"></a><a id="fáze-55---cicd"></a>[FÁZE 5.5 - CI/CD](cs/ROADMAP.md#cz-fáze-55---cicd) |
| CZ | <a id="cz-fáze-5--podmínky-dokončení"></a><a id="fáze-5--podmínky-dokončení"></a>[FÁZE 5 — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-5--podmínky-dokončení) |
| CZ | <a id="cz-fáze-6---bezpečnost"></a><a id="fáze-6---bezpečnost"></a>[FÁZE 6 - Bezpečnost](cs/ROADMAP.md#cz-fáze-6---bezpečnost) |
| CZ | <a id="cz-cíl-10"></a><a id="cíl-10"></a>[Cíl](cs/ROADMAP.md#cz-cíl-10) |
| CZ | <a id="cz-fáze-61---modelování-hrozeb"></a><a id="fáze-61---modelování-hrozeb"></a>[FÁZE 6.1 - Modelování hrozeb](cs/ROADMAP.md#cz-fáze-61---modelování-hrozeb) |
| CZ | <a id="cz-nový-koncept---model-hrozeb"></a><a id="nový-koncept---model-hrozeb"></a>[Nový koncept - Model hrozeb](cs/ROADMAP.md#cz-nový-koncept---model-hrozeb) |
| CZ | <a id="cz-fáze-62---validace-běhových-vstupů"></a><a id="fáze-62---validace-běhových-vstupů"></a>[FÁZE 6.2 - Validace běhových vstupů](cs/ROADMAP.md#cz-fáze-62---validace-běhových-vstupů) |
| CZ | <a id="cz-soubor-31"></a><a id="soubor-31"></a>[Soubor](cs/ROADMAP.md#cz-soubor-31) |
| CZ | <a id="cz-fáze-63---běhové-limity"></a><a id="fáze-63---běhové-limity"></a>[FÁZE 6.3 - Běhové limity](cs/ROADMAP.md#cz-fáze-63---běhové-limity) |
| CZ | <a id="cz-soubor-32"></a><a id="soubor-32"></a>[Soubor](cs/ROADMAP.md#cz-soubor-32) |
| CZ | <a id="cz-fáze-64---tajemství"></a><a id="fáze-64---tajemství"></a>[FÁZE 6.4 - Tajemství](cs/ROADMAP.md#cz-fáze-64---tajemství) |
| CZ | <a id="cz-fáze-65---bezpečnost-závislostí"></a><a id="fáze-65---bezpečnost-závislostí"></a>[FÁZE 6.5 - Bezpečnost závislostí](cs/ROADMAP.md#cz-fáze-65---bezpečnost-závislostí) |
| CZ | <a id="cz-fáze-66---bezpečnost-kontejneru"></a><a id="fáze-66---bezpečnost-kontejneru"></a>[FÁZE 6.6 - Bezpečnost kontejneru](cs/ROADMAP.md#cz-fáze-66---bezpečnost-kontejneru) |
| CZ | <a id="cz-fáze-67---bezpečnost-http"></a><a id="fáze-67---bezpečnost-http"></a>[FÁZE 6.7 - Bezpečnost HTTP](cs/ROADMAP.md#cz-fáze-67---bezpečnost-http) |
| CZ | <a id="cz-fáze-68---bezpečnost-specifická-pro-rag"></a><a id="fáze-68---bezpečnost-specifická-pro-rag"></a>[FÁZE 6.8 - Bezpečnost specifická pro RAG](cs/ROADMAP.md#cz-fáze-68---bezpečnost-specifická-pro-rag) |
| CZ | <a id="cz-nový-koncept---nepřímá-prompt-injection"></a><a id="nový-koncept---nepřímá-prompt-injection"></a>[Nový koncept - Nepřímá prompt injection](cs/ROADMAP.md#cz-nový-koncept---nepřímá-prompt-injection) |
| CZ | <a id="cz-fáze-6--podmínky-dokončení"></a><a id="fáze-6--podmínky-dokončení"></a>[FÁZE 6 — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-6--podmínky-dokončení) |
| CZ | <a id="cz-fáze-7---produkční-verze-v1"></a><a id="fáze-7---produkční-verze-v1"></a>[FÁZE 7 - Produkční verze v1](cs/ROADMAP.md#cz-fáze-7---produkční-verze-v1) |
| CZ | <a id="cz-cíl-11"></a><a id="cíl-11"></a>[Cíl](cs/ROADMAP.md#cz-cíl-11) |
| CZ | <a id="cz-fáze-71---health-a-readiness"></a><a id="fáze-71---health-a-readiness"></a>[FÁZE 7.1 - Health a readiness](cs/ROADMAP.md#cz-fáze-71---health-a-readiness) |
| CZ | <a id="cz-nový-koncept---liveness-a-readiness"></a><a id="nový-koncept---liveness-a-readiness"></a>[Nový koncept - Liveness a readiness](cs/ROADMAP.md#cz-nový-koncept---liveness-a-readiness) |
| CZ | <a id="cz-liveness--běh-procesu"></a><a id="liveness--běh-procesu"></a>[Liveness — běh procesu](cs/ROADMAP.md#cz-liveness--běh-procesu) |
| CZ | <a id="cz-readiness--připravenost-služby"></a><a id="readiness--připravenost-služby"></a>[Readiness — připravenost služby](cs/ROADMAP.md#cz-readiness--připravenost-služby) |
| CZ | <a id="cz-fáze-72---produkční-smoke-test"></a><a id="fáze-72---produkční-smoke-test"></a>[FÁZE 7.2 - Produkční smoke test](cs/ROADMAP.md#cz-fáze-72---produkční-smoke-test) |
| CZ | <a id="cz-soubor-33"></a><a id="soubor-33"></a>[Soubor](cs/ROADMAP.md#cz-soubor-33) |
| CZ | <a id="cz-fáze-73---dokumentace"></a><a id="fáze-73---dokumentace"></a>[FÁZE 7.3 - Dokumentace](cs/ROADMAP.md#cz-fáze-73---dokumentace) |
| CZ | <a id="cz-fáze-7--podmínky-dokončení"></a><a id="fáze-7--podmínky-dokončení"></a>[FÁZE 7 — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-7--podmínky-dokončení) |
| CZ | <a id="cz-fáze-8---rozšíření"></a><a id="fáze-8---rozšíření"></a>[FÁZE 8 - Rozšíření](cs/ROADMAP.md#cz-fáze-8---rozšíření) |
| CZ | <a id="cz-fáze-8a---průzkum-agentů"></a><a id="fáze-8a---průzkum-agentů"></a>[FÁZE 8A - Průzkum agentů](cs/ROADMAP.md#cz-fáze-8a---průzkum-agentů) |
| CZ | <a id="cz-cíl-12"></a><a id="cíl-12"></a>[Cíl](cs/ROADMAP.md#cz-cíl-12) |
| CZ | <a id="cz-soubor-34"></a><a id="soubor-34"></a>[Soubor](cs/ROADMAP.md#cz-soubor-34) |
| CZ | <a id="cz-nový-koncept---volání-nástrojů"></a><a id="nový-koncept---volání-nástrojů"></a>[Nový koncept - Volání nástrojů](cs/ROADMAP.md#cz-nový-koncept---volání-nástrojů) |
| CZ | <a id="cz-fáze-8a--podmínky-dokončení"></a><a id="fáze-8a--podmínky-dokončení"></a>[FÁZE 8A — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-8a--podmínky-dokončení) |
| CZ | <a id="cz-fáze-8b---sql-a-etl"></a><a id="fáze-8b---sql-a-etl"></a>[FÁZE 8B - SQL a ETL](cs/ROADMAP.md#cz-fáze-8b---sql-a-etl) |
| CZ | <a id="cz-cíl-13"></a><a id="cíl-13"></a>[Cíl](cs/ROADMAP.md#cz-cíl-13) |
| CZ | <a id="cz-soubor-35"></a><a id="soubor-35"></a>[Soubor](cs/ROADMAP.md#cz-soubor-35) |
| CZ | <a id="cz-soubor-36"></a><a id="soubor-36"></a>[Soubor](cs/ROADMAP.md#cz-soubor-36) |
| CZ | <a id="cz-soubor-37"></a><a id="soubor-37"></a>[Soubor](cs/ROADMAP.md#cz-soubor-37) |
| CZ | <a id="cz-soubor-38"></a><a id="soubor-38"></a>[Soubor](cs/ROADMAP.md#cz-soubor-38) |
| CZ | <a id="cz-nový-koncept---etl"></a><a id="nový-koncept---etl"></a>[Nový koncept - ETL](cs/ROADMAP.md#cz-nový-koncept---etl) |
| CZ | <a id="cz-fáze-8b--podmínky-dokončení"></a><a id="fáze-8b--podmínky-dokončení"></a>[FÁZE 8B — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-8b--podmínky-dokončení) |
| CZ | <a id="cz-fáze-8c---mlops"></a><a id="fáze-8c---mlops"></a>[FÁZE 8C - MLOps](cs/ROADMAP.md#cz-fáze-8c---mlops) |
| CZ | <a id="cz-cíl-14"></a><a id="cíl-14"></a>[Cíl](cs/ROADMAP.md#cz-cíl-14) |
| CZ | <a id="cz-soubor-39"></a><a id="soubor-39"></a>[Soubor](cs/ROADMAP.md#cz-soubor-39) |
| CZ | <a id="cz-nový-koncept---sledování-experimentů"></a><a id="nový-koncept---sledování-experimentů"></a>[Nový koncept - Sledování experimentů](cs/ROADMAP.md#cz-nový-koncept---sledování-experimentů) |
| CZ | <a id="cz-soubor-40"></a><a id="soubor-40"></a>[Soubor](cs/ROADMAP.md#cz-soubor-40) |
| CZ | <a id="cz-fáze-8c--podmínky-dokončení"></a><a id="fáze-8c--podmínky-dokončení"></a>[FÁZE 8C — Podmínky dokončení](cs/ROADMAP.md#cz-fáze-8c--podmínky-dokončení) |
| CZ | <a id="cz-fáze-8d---pokročilí-agenti"></a><a id="fáze-8d---pokročilí-agenti"></a>[FÁZE 8D - Pokročilí agenti](cs/ROADMAP.md#cz-fáze-8d---pokročilí-agenti) |
| CZ | <a id="cz-původní-plánovací-odhady--historické"></a><a id="původní-plánovací-odhady--historické"></a>[Původní plánovací odhady — historické](cs/ROADMAP.md#cz-původní-plánovací-odhady--historické) |
| CZ | <a id="cz-historie-plánování"></a><a id="historie-plánování"></a>[Historie plánování](cs/ROADMAP.md#cz-historie-plánování) |

[↑ Nahoru / Back to top](#top)
