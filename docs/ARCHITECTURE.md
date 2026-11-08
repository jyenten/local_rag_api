<a id="top"></a>

# AI RAG Project Architecture

[Česky](cs/ARCHITECTURE.md#cz) · [English](en/ARCHITECTURE.md#en) · [Dokumentace / Documentation](README.md)

Tento dokument má samostatnou [českou](cs/ARCHITECTURE.md#cz) a [anglickou](en/ARCHITECTURE.md#en) verzi. Otevři vybraný jazyk pro úplný text, obsah a příklady.

This document has separate [Czech](cs/ARCHITECTURE.md#cz) and [English](en/ARCHITECTURE.md#en) versions. Open a language for the full text, contents and examples.

<a id="obsah"></a>

## Starší odkazy na kapitoly / Legacy chapter links

Starší záložky vedou na příslušný řádek níže. Odkaz v řádku otevře úplnou kapitolu. / Older bookmarks lead to the matching row below; follow its link to the full chapter.

| Jazyk / Language | Kapitola / Chapter |
| --- | --- |
| EN | <a id="en"></a><a id="en--english"></a>[EN — English](en/ARCHITECTURE.md#en) |
| EN | <a id="en-current-implementation-snapshot-2026-10-28"></a><a id="current-implementation-snapshot-2026-10-28"></a>[Current implementation snapshot (2026-10-28)](en/ARCHITECTURE.md#en-current-implementation-snapshot-2026-10-28) |
| EN | <a id="en-identity-and-evaluation-boundary"></a><a id="identity-and-evaluation-boundary"></a>[Identity and evaluation boundary](en/ARCHITECTURE.md#en-identity-and-evaluation-boundary) |
| EN | <a id="en-1-purpose"></a><a id="1-purpose"></a>[1. Purpose](en/ARCHITECTURE.md#en-1-purpose) |
| EN | <a id="en-2-architectural-principles"></a><a id="2-architectural-principles"></a>[2. Architectural Principles](en/ARCHITECTURE.md#en-2-architectural-principles) |
| EN | <a id="21-separation-of-concerns"></a>[2.1 Separation of Concerns](en/ARCHITECTURE.md#en) |
| EN | <a id="22-explicit-module-boundaries"></a>[2.2 Explicit Module Boundaries](en/ARCHITECTURE.md#en) |
| EN | <a id="23-domain-independence"></a>[2.3 Domain Independence](en/ARCHITECTURE.md#en) |
| EN | <a id="24-prefer-immutable-data"></a>[2.4 Prefer Immutable Data](en/ARCHITECTURE.md#en) |
| EN | <a id="25-configuration-outside-business-logic"></a>[2.5 Configuration Outside Business Logic](en/ARCHITECTURE.md#en) |
| EN | <a id="26-measure-before-optimizing"></a>[2.6 Measure Before Optimizing](en/ARCHITECTURE.md#en) |
| EN | <a id="en-3-high-level-system-architecture"></a><a id="3-high-level-system-architecture"></a>[3. High-Level System Architecture](en/ARCHITECTURE.md#en-3-high-level-system-architecture) |
| EN | <a id="en-4-offline-data-pipeline"></a><a id="4-offline-data-pipeline"></a>[4. Offline Data Pipeline](en/ARCHITECTURE.md#en-4-offline-data-pipeline) |
| EN | <a id="en-5-runtime-application"></a><a id="5-runtime-application"></a>[5. Runtime Application](en/ARCHITECTURE.md#en-5-runtime-application) |
| EN | <a id="51-appconfigpy"></a>[5.1 `app/config.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="52-appschemaspy"></a>[5.2 `app/schemas.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="53-appretrievalpy"></a>[5.3 `app/retrieval.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="en-6-target-retrieval-architecture"></a><a id="6-target-retrieval-architecture"></a>[6. Target Retrieval Architecture](en/ARCHITECTURE.md#en-6-target-retrieval-architecture) |
| EN | <a id="61-retrievalmodelspy"></a>[6.1 `retrieval/models.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="62-retrievalembeddingspy"></a>[6.2 `retrieval/embeddings.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="63-retrievalvector_searchpy"></a>[6.3 `retrieval/vector_search.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="64-retrievalquerypy"></a>[6.4 `retrieval/query.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="65-retrievalrerankerpy"></a>[6.5 `retrieval/reranker.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="66-retrievalscoringpy"></a>[6.6 `retrieval/scoring.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="67-retrievalservicepy"></a>[6.7 `retrieval/service.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="en-7-generation-architecture"></a><a id="7-generation-architecture"></a>[7. Generation Architecture](en/ARCHITECTURE.md#en-7-generation-architecture) |
| EN | <a id="en-8-rag-orchestration"></a><a id="8-rag-orchestration"></a>[8. RAG Orchestration](en/ARCHITECTURE.md#en-8-rag-orchestration) |
| EN | <a id="en-9-api-architecture"></a><a id="9-api-architecture"></a>[9. API Architecture](en/ARCHITECTURE.md#en-9-api-architecture) |
| EN | <a id="91-appmainpy"></a>[9.1 `app/main.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="92-applifecyclepy"></a>[9.2 `app/lifecycle.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="93-appapiroutespy"></a>[9.3 `app/api/routes.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="94-appapidependenciespy"></a>[9.4 `app/api/dependencies.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="95-appapierrorspy"></a>[9.5 `app/api/errors.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="96-appapimiddlewarepy"></a>[9.6 `app/api/middleware.py`](en/ARCHITECTURE.md#en) |
| EN | <a id="en-10-evaluation-architecture"></a><a id="10-evaluation-architecture"></a>[10. Evaluation Architecture](en/ARCHITECTURE.md#en-10-evaluation-architecture) |
| EN | <a id="en-11-evaluation-dataset-roles"></a><a id="11-evaluation-dataset-roles"></a>[11. Evaluation Dataset Roles](en/ARCHITECTURE.md#en-11-evaluation-dataset-roles) |
| EN | <a id="dev"></a>[DEV](en/ARCHITECTURE.md#en) |
| EN | <a id="random"></a>[RANDOM](en/ARCHITECTURE.md#en) |
| EN | <a id="test"></a>[TEST](en/ARCHITECTURE.md#en) |
| EN | <a id="en-12-evaluation-flow"></a><a id="12-evaluation-flow"></a>[12. Evaluation Flow](en/ARCHITECTURE.md#en-12-evaluation-flow) |
| EN | <a id="en-13-universal-document-explorer"></a><a id="13-universal-document-explorer"></a>[13. Universal Document Explorer](en/ARCHITECTURE.md#en-13-universal-document-explorer) |
| EN | <a id="en-14-document-explorer-data-flow"></a><a id="14-document-explorer-data-flow"></a>[14. Document Explorer Data Flow](en/ARCHITECTURE.md#en-14-document-explorer-data-flow) |
| EN | <a id="en-15-document-search-models"></a><a id="15-document-search-models"></a>[15. Document Search Models](en/ARCHITECTURE.md#en-15-document-search-models) |
| EN | <a id="151-pagedocument"></a>[15.1 `PageDocument`](en/ARCHITECTURE.md#en) |
| EN | <a id="152-searchresult"></a>[15.2 `SearchResult`](en/ARCHITECTURE.md#en) |
| EN | <a id="153-bm25searchindex"></a>[15.3 `BM25SearchIndex`](en/ARCHITECTURE.md#en) |
| EN | <a id="en-16-document-explorer-security-boundary"></a><a id="16-document-explorer-security-boundary"></a>[16. Document Explorer Security Boundary](en/ARCHITECTURE.md#en-16-document-explorer-security-boundary) |
| EN | <a id="en-17-security-architecture"></a><a id="17-security-architecture"></a>[17. Security Architecture](en/ARCHITECTURE.md#en-17-security-architecture) |
| EN | <a id="171-future-threat-modeling"></a>[17.1 Future Threat Modeling](en/ARCHITECTURE.md#en) |
| EN | <a id="en-18-observability-architecture"></a><a id="18-observability-architecture"></a>[18. Observability Architecture](en/ARCHITECTURE.md#en-18-observability-architecture) |
| EN | <a id="181-structured-logging"></a>[18.1 Structured Logging](en/ARCHITECTURE.md#en) |
| EN | <a id="182-quality-metrics-vs-operational-metrics"></a>[18.2 Quality Metrics vs Operational Metrics](en/ARCHITECTURE.md#en) |
| EN | <a id="en-19-testing-architecture"></a><a id="19-testing-architecture"></a>[19. Testing Architecture](en/ARCHITECTURE.md#en-19-testing-architecture) |
| EN | <a id="191-test-independence"></a>[19.1 Test Independence](en/ARCHITECTURE.md#en) |
| EN | <a id="en-20-infrastructure-architecture"></a><a id="20-infrastructure-architecture"></a>[20. Infrastructure Architecture](en/ARCHITECTURE.md#en-20-infrastructure-architecture) |
| EN | <a id="201-container-architecture"></a>[20.1 Container Architecture](en/ARCHITECTURE.md#en) |
| EN | <a id="202-cicd"></a>[20.2 CI/CD](en/ARCHITECTURE.md#en) |
| EN | <a id="en-21-dependency-direction"></a><a id="21-dependency-direction"></a>[21. Dependency Direction](en/ARCHITECTURE.md#en-21-dependency-direction) |
| EN | <a id="en-22-public-interfaces"></a><a id="22-public-interfaces"></a>[22. Public Interfaces](en/ARCHITECTURE.md#en-22-public-interfaces) |
| EN | <a id="221-document-search"></a>[22.1 Document Search](en/ARCHITECTURE.md#en) |
| EN | <a id="222-retrieval"></a>[22.2 Retrieval](en/ARCHITECTURE.md#en) |
| EN | <a id="223-rag"></a>[22.3 RAG](en/ARCHITECTURE.md#en) |
| EN | <a id="224-evaluation"></a>[22.4 Evaluation](en/ARCHITECTURE.md#en) |
| EN | <a id="en-23-current-technical-debt"></a><a id="23-current-technical-debt"></a>[23. Current Technical Debt](en/ARCHITECTURE.md#en-23-current-technical-debt) |
| EN | <a id="231-retrieval"></a>[23.1 Retrieval](en/ARCHITECTURE.md#en) |
| EN | <a id="232-rag"></a>[23.2 RAG](en/ARCHITECTURE.md#en) |
| EN | <a id="233-evaluation--foundation-implemented"></a>[23.3 Evaluation — foundation implemented](en/ARCHITECTURE.md#en) |
| EN | <a id="234-document-search--historical-prototype-replaced"></a>[23.4 Document Search — historical prototype replaced](en/ARCHITECTURE.md#en) |
| EN | <a id="235-ingestion"></a>[23.5 Ingestion](en/ARCHITECTURE.md#en) |
| EN | <a id="en-24-target-project-structure"></a><a id="24-target-project-structure"></a>[24. Target Project Structure](en/ARCHITECTURE.md#en-24-target-project-structure) |
| EN | <a id="en-25-architecture-change-rule"></a><a id="25-architecture-change-rule"></a>[25. Architecture Change Rule](en/ARCHITECTURE.md#en-25-architecture-change-rule) |
| EN | <a id="en-26-historical-phase-2a-architectural-focus"></a><a id="26-historical-phase-2a-architectural-focus"></a>[26. Historical Phase 2A Architectural Focus](en/ARCHITECTURE.md#en-26-historical-phase-2a-architectural-focus) |
| CZ | <a id="cz"></a><a id="cz--česká-verze"></a>[CZ — Česká verze](cs/ARCHITECTURE.md#cz) |
| CZ | <a id="cz-přehled-implementace-k-28-10-2026"></a><a id="přehled-implementace-k-28-10-2026"></a>[Přehled implementace k 28. 10. 2026](cs/ARCHITECTURE.md#cz-přehled-implementace-k-28-10-2026) |
| CZ | <a id="cz-identita-a-hranice-evaluace"></a><a id="identita-a-hranice-evaluace"></a>[Identita a hranice evaluace](cs/ARCHITECTURE.md#cz-identita-a-hranice-evaluace) |
| CZ | <a id="cz-1-účel"></a><a id="1-účel"></a>[1. Účel](cs/ARCHITECTURE.md#cz-1-účel) |
| CZ | <a id="cz-2-architektonické-principy"></a><a id="2-architektonické-principy"></a>[2. Architektonické principy](cs/ARCHITECTURE.md#cz-2-architektonické-principy) |
| CZ | <a id="cz-21-oddělení-odpovědností"></a><a id="21-oddělení-odpovědností"></a>[2.1 Oddělení odpovědností](cs/ARCHITECTURE.md#cz-21-oddělení-odpovědností) |
| CZ | <a id="cz-22-výslovné-hranice-modulů"></a><a id="22-výslovné-hranice-modulů"></a>[2.2 Výslovné hranice modulů](cs/ARCHITECTURE.md#cz-22-výslovné-hranice-modulů) |
| CZ | <a id="cz-23-nezávislost-na-doméně"></a><a id="23-nezávislost-na-doméně"></a>[2.3 Nezávislost na doméně](cs/ARCHITECTURE.md#cz-23-nezávislost-na-doméně) |
| CZ | <a id="cz-24-upřednostnění-neměnných-dat"></a><a id="24-upřednostnění-neměnných-dat"></a>[2.4 Upřednostnění neměnných dat](cs/ARCHITECTURE.md#cz-24-upřednostnění-neměnných-dat) |
| CZ | <a id="cz-25-konfigurace-mimo-aplikační-logiku"></a><a id="25-konfigurace-mimo-aplikační-logiku"></a>[2.5 Konfigurace mimo aplikační logiku](cs/ARCHITECTURE.md#cz-25-konfigurace-mimo-aplikační-logiku) |
| CZ | <a id="cz-26-měření-před-optimalizací"></a><a id="26-měření-před-optimalizací"></a>[2.6 Měření před optimalizací](cs/ARCHITECTURE.md#cz-26-měření-před-optimalizací) |
| CZ | <a id="cz-3-celková-architektura-systému"></a><a id="3-celková-architektura-systému"></a>[3. Celková architektura systému](cs/ARCHITECTURE.md#cz-3-celková-architektura-systému) |
| CZ | <a id="cz-4-offline-datová-pipeline"></a><a id="4-offline-datová-pipeline"></a>[4. Offline datová pipeline](cs/ARCHITECTURE.md#cz-4-offline-datová-pipeline) |
| CZ | <a id="cz-5-běhová-aplikace"></a><a id="5-běhová-aplikace"></a>[5. Běhová aplikace](cs/ARCHITECTURE.md#cz-5-běhová-aplikace) |
| CZ | <a id="cz-51-appconfigpy"></a><a id="51-appconfigpy-1"></a>[5.1 `app/config.py`](cs/ARCHITECTURE.md#cz-51-appconfigpy) |
| CZ | <a id="cz-52-appschemaspy"></a><a id="52-appschemaspy-1"></a>[5.2 `app/schemas.py`](cs/ARCHITECTURE.md#cz-52-appschemaspy) |
| CZ | <a id="cz-53-appretrievalpy"></a><a id="53-appretrievalpy-1"></a>[5.3 `app/retrieval.py`](cs/ARCHITECTURE.md#cz-53-appretrievalpy) |
| CZ | <a id="cz-6-cílová-architektura-retrievalu"></a><a id="6-cílová-architektura-retrievalu"></a>[6. Cílová architektura retrievalu](cs/ARCHITECTURE.md#cz-6-cílová-architektura-retrievalu) |
| CZ | <a id="cz-61-retrievalmodelspy"></a><a id="61-retrievalmodelspy-1"></a>[6.1 `retrieval/models.py`](cs/ARCHITECTURE.md#cz-61-retrievalmodelspy) |
| CZ | <a id="cz-62-retrievalembeddingspy"></a><a id="62-retrievalembeddingspy-1"></a>[6.2 `retrieval/embeddings.py`](cs/ARCHITECTURE.md#cz-62-retrievalembeddingspy) |
| CZ | <a id="cz-63-retrievalvector_searchpy"></a><a id="63-retrievalvector_searchpy-1"></a>[6.3 `retrieval/vector_search.py`](cs/ARCHITECTURE.md#cz-63-retrievalvector_searchpy) |
| CZ | <a id="cz-64-retrievalquerypy"></a><a id="64-retrievalquerypy-1"></a>[6.4 `retrieval/query.py`](cs/ARCHITECTURE.md#cz-64-retrievalquerypy) |
| CZ | <a id="cz-65-retrievalrerankerpy"></a><a id="65-retrievalrerankerpy-1"></a>[6.5 `retrieval/reranker.py`](cs/ARCHITECTURE.md#cz-65-retrievalrerankerpy) |
| CZ | <a id="cz-66-retrievalscoringpy"></a><a id="66-retrievalscoringpy-1"></a>[6.6 `retrieval/scoring.py`](cs/ARCHITECTURE.md#cz-66-retrievalscoringpy) |
| CZ | <a id="cz-67-retrievalservicepy"></a><a id="67-retrievalservicepy-1"></a>[6.7 `retrieval/service.py`](cs/ARCHITECTURE.md#cz-67-retrievalservicepy) |
| CZ | <a id="cz-7-architektura-generování"></a><a id="7-architektura-generování"></a>[7. Architektura generování](cs/ARCHITECTURE.md#cz-7-architektura-generování) |
| CZ | <a id="cz-8-koordinace-rag"></a><a id="8-koordinace-rag"></a>[8. Koordinace RAG](cs/ARCHITECTURE.md#cz-8-koordinace-rag) |
| CZ | <a id="cz-9-architektura-api"></a><a id="9-architektura-api"></a>[9. Architektura API](cs/ARCHITECTURE.md#cz-9-architektura-api) |
| CZ | <a id="cz-91-appmainpy"></a><a id="91-appmainpy-1"></a>[9.1 `app/main.py`](cs/ARCHITECTURE.md#cz-91-appmainpy) |
| CZ | <a id="cz-92-applifecyclepy"></a><a id="92-applifecyclepy-1"></a>[9.2 `app/lifecycle.py`](cs/ARCHITECTURE.md#cz-92-applifecyclepy) |
| CZ | <a id="cz-93-appapiroutespy"></a><a id="93-appapiroutespy-1"></a>[9.3 `app/api/routes.py`](cs/ARCHITECTURE.md#cz-93-appapiroutespy) |
| CZ | <a id="cz-94-appapidependenciespy"></a><a id="94-appapidependenciespy-1"></a>[9.4 `app/api/dependencies.py`](cs/ARCHITECTURE.md#cz-94-appapidependenciespy) |
| CZ | <a id="cz-95-appapierrorspy"></a><a id="95-appapierrorspy-1"></a>[9.5 `app/api/errors.py`](cs/ARCHITECTURE.md#cz-95-appapierrorspy) |
| CZ | <a id="cz-96-appapimiddlewarepy"></a><a id="96-appapimiddlewarepy-1"></a>[9.6 `app/api/middleware.py`](cs/ARCHITECTURE.md#cz-96-appapimiddlewarepy) |
| CZ | <a id="cz-10-architektura-evaluace"></a><a id="10-architektura-evaluace"></a>[10. Architektura evaluace](cs/ARCHITECTURE.md#cz-10-architektura-evaluace) |
| CZ | <a id="cz-11-role-evaluačních-datasetů"></a><a id="11-role-evaluačních-datasetů"></a>[11. Role evaluačních datasetů](cs/ARCHITECTURE.md#cz-11-role-evaluačních-datasetů) |
| CZ | <a id="cz-dev"></a><a id="dev-1"></a>[DEV](cs/ARCHITECTURE.md#cz-dev) |
| CZ | <a id="cz-random"></a><a id="random-1"></a>[RANDOM](cs/ARCHITECTURE.md#cz-random) |
| CZ | <a id="cz-test"></a><a id="test-1"></a>[TEST](cs/ARCHITECTURE.md#cz-test) |
| CZ | <a id="cz-12-průběh-evaluace"></a><a id="12-průběh-evaluace"></a>[12. Průběh evaluace](cs/ARCHITECTURE.md#cz-12-průběh-evaluace) |
| CZ | <a id="cz-13-univerzální-průzkumník-dokumentů"></a><a id="13-univerzální-průzkumník-dokumentů"></a>[13. Univerzální průzkumník dokumentů](cs/ARCHITECTURE.md#cz-13-univerzální-průzkumník-dokumentů) |
| CZ | <a id="cz-14-tok-dat-průzkumníku-dokumentů"></a><a id="14-tok-dat-průzkumníku-dokumentů"></a>[14. Tok dat průzkumníku dokumentů](cs/ARCHITECTURE.md#cz-14-tok-dat-průzkumníku-dokumentů) |
| CZ | <a id="cz-15-modely-vyhledávání-v-dokumentech"></a><a id="15-modely-vyhledávání-v-dokumentech"></a>[15. Modely vyhledávání v dokumentech](cs/ARCHITECTURE.md#cz-15-modely-vyhledávání-v-dokumentech) |
| CZ | <a id="cz-151-pagedocument"></a><a id="151-pagedocument-1"></a>[15.1 `PageDocument`](cs/ARCHITECTURE.md#cz-151-pagedocument) |
| CZ | <a id="cz-152-searchresult"></a><a id="152-searchresult-1"></a>[15.2 `SearchResult`](cs/ARCHITECTURE.md#cz-152-searchresult) |
| CZ | <a id="cz-153-bm25searchindex"></a><a id="153-bm25searchindex-1"></a>[15.3 `BM25SearchIndex`](cs/ARCHITECTURE.md#cz-153-bm25searchindex) |
| CZ | <a id="cz-16-bezpečnostní-hranice-průzkumníku-dokumentů"></a><a id="16-bezpečnostní-hranice-průzkumníku-dokumentů"></a>[16. Bezpečnostní hranice průzkumníku dokumentů](cs/ARCHITECTURE.md#cz-16-bezpečnostní-hranice-průzkumníku-dokumentů) |
| CZ | <a id="cz-17-bezpečnostní-architektura"></a><a id="17-bezpečnostní-architektura"></a>[17. Bezpečnostní architektura](cs/ARCHITECTURE.md#cz-17-bezpečnostní-architektura) |
| CZ | <a id="cz-171-budoucí-modelování-hrozeb"></a><a id="171-budoucí-modelování-hrozeb"></a>[17.1 Budoucí modelování hrozeb](cs/ARCHITECTURE.md#cz-171-budoucí-modelování-hrozeb) |
| CZ | <a id="cz-18-architektura-observability"></a><a id="18-architektura-observability"></a>[18. Architektura observability](cs/ARCHITECTURE.md#cz-18-architektura-observability) |
| CZ | <a id="cz-181-strukturované-logování"></a><a id="181-strukturované-logování"></a>[18.1 Strukturované logování](cs/ARCHITECTURE.md#cz-181-strukturované-logování) |
| CZ | <a id="cz-182-metriky-kvality-a-provozní-metriky"></a><a id="182-metriky-kvality-a-provozní-metriky"></a>[18.2 Metriky kvality a provozní metriky](cs/ARCHITECTURE.md#cz-182-metriky-kvality-a-provozní-metriky) |
| CZ | <a id="cz-19-architektura-testování"></a><a id="19-architektura-testování"></a>[19. Architektura testování](cs/ARCHITECTURE.md#cz-19-architektura-testování) |
| CZ | <a id="cz-191-nezávislost-testů"></a><a id="191-nezávislost-testů"></a>[19.1 Nezávislost testů](cs/ARCHITECTURE.md#cz-191-nezávislost-testů) |
| CZ | <a id="cz-20-architektura-infrastruktury"></a><a id="20-architektura-infrastruktury"></a>[20. Architektura infrastruktury](cs/ARCHITECTURE.md#cz-20-architektura-infrastruktury) |
| CZ | <a id="cz-201-architektura-kontejnerů"></a><a id="201-architektura-kontejnerů"></a>[20.1 Architektura kontejnerů](cs/ARCHITECTURE.md#cz-201-architektura-kontejnerů) |
| CZ | <a id="cz-202-cicd"></a><a id="202-cicd-1"></a>[20.2 CI/CD](cs/ARCHITECTURE.md#cz-202-cicd) |
| CZ | <a id="cz-21-směr-závislostí"></a><a id="21-směr-závislostí"></a>[21. Směr závislostí](cs/ARCHITECTURE.md#cz-21-směr-závislostí) |
| CZ | <a id="cz-22-veřejná-rozhraní"></a><a id="22-veřejná-rozhraní"></a>[22. Veřejná rozhraní](cs/ARCHITECTURE.md#cz-22-veřejná-rozhraní) |
| CZ | <a id="cz-221-vyhledávání-v-dokumentech"></a><a id="221-vyhledávání-v-dokumentech"></a>[22.1 Vyhledávání v dokumentech](cs/ARCHITECTURE.md#cz-221-vyhledávání-v-dokumentech) |
| CZ | <a id="cz-222-retrieval"></a><a id="222-retrieval-1"></a>[22.2 Retrieval](cs/ARCHITECTURE.md#cz-222-retrieval) |
| CZ | <a id="cz-223-rag"></a><a id="223-rag-1"></a>[22.3 RAG](cs/ARCHITECTURE.md#cz-223-rag) |
| CZ | <a id="cz-224-evaluace"></a><a id="224-evaluace"></a>[22.4 Evaluace](cs/ARCHITECTURE.md#cz-224-evaluace) |
| CZ | <a id="cz-23-současný-technický-dluh"></a><a id="23-současný-technický-dluh"></a>[23. Současný technický dluh](cs/ARCHITECTURE.md#cz-23-současný-technický-dluh) |
| CZ | <a id="cz-231-retrieval"></a><a id="231-retrieval-1"></a>[23.1 Retrieval](cs/ARCHITECTURE.md#cz-231-retrieval) |
| CZ | <a id="cz-232-rag"></a><a id="232-rag-1"></a>[23.2 RAG](cs/ARCHITECTURE.md#cz-232-rag) |
| CZ | <a id="cz-233-evaluace--základ-je-implementován"></a><a id="233-evaluace--základ-je-implementován"></a>[23.3 Evaluace — základ je implementován](cs/ARCHITECTURE.md#cz-233-evaluace--základ-je-implementován) |
| CZ | <a id="cz-234-vyhledávání-v-dokumentech--historický-prototyp-nahrazen"></a><a id="234-vyhledávání-v-dokumentech--historický-prototyp-nahrazen"></a>[23.4 Vyhledávání v dokumentech — historický prototyp nahrazen](cs/ARCHITECTURE.md#cz-234-vyhledávání-v-dokumentech--historický-prototyp-nahrazen) |
| CZ | <a id="cz-235-ingest"></a><a id="235-ingest"></a>[23.5 Ingest](cs/ARCHITECTURE.md#cz-235-ingest) |
| CZ | <a id="cz-24-cílová-struktura-projektu"></a><a id="24-cílová-struktura-projektu"></a>[24. Cílová struktura projektu](cs/ARCHITECTURE.md#cz-24-cílová-struktura-projektu) |
| CZ | <a id="cz-25-pravidlo-změn-architektury"></a><a id="25-pravidlo-změn-architektury"></a>[25. Pravidlo změn architektury](cs/ARCHITECTURE.md#cz-25-pravidlo-změn-architektury) |
| CZ | <a id="cz-26-historické-architektonické-zaměření-fáze-2a"></a><a id="26-historické-architektonické-zaměření-fáze-2a"></a>[26. Historické architektonické zaměření fáze 2A](cs/ARCHITECTURE.md#cz-26-historické-architektonické-zaměření-fáze-2a) |

[↑ Nahoru / Back to top](#top)
