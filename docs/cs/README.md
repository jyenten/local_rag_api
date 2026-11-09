<a id="top"></a>

<a id="ai-engineering-portfolio--python-rag-a-evaluace-retrievalu"></a>

# Local RAG API — vyhledávání v dokumentech a evaluace retrievalu

[Česky](#cz) · [English](../../README.md#en) · [Dokumentace](../README.md)

<a id="cz"></a>

Lokální Python/FastAPI prototyp pro odpovídání nad technickými PDF, aktuálně zaměřený na dokumentaci OSPF. Propojuje metadata zdrojů a stránek v HTTP odpovědích se samostatnými experimenty s vektorovým a BM25 retrievalem. Offline evaluace zaznamenává MRR, Hit@K, latenci retrievalu, hashe datasetů a Git původ.

**Technologie:** Python 3.11 · FastAPI · Pydantic · ChromaDB · Sentence Transformers · BM25 · Pytest · Docker · GitHub Actions

<a id="obsah"></a>

<details>
<summary>Obsah — kliknutím rozbalit</summary>

- [Hlavní projekt](#cz-hlavní-projekt-rag-api-a-vyhledávání-v-dokumentech)
- [Co je implementováno](#cz-co-je-implementováno)
- [Ověření](#cz-ověření)
- [Zaznamenaný retrieval baseline](#cz-zaznamenany-retrieval-baseline)
- [Architektura v přehledu](#cz-architektura-v-přehledu)
- [Jak začít](#cz-jak-začít)
- [Inženýrský přístup](#cz-inženýrský-přístup)
- [Struktura repozitáře](#cz-struktura-repozitáře)
- [Další kroky](#cz-další-kroky)
- [Rychlý start na Windows](#cz-rychlý-start-na-windows)

</details>

<a id="cz-hlavní-projekt-rag-api-a-vyhledávání-v-dokumentech"></a>

<a id="hlavní-projekt-rag-api-a-vyhledávání-v-dokumentech"></a>

## Hlavní projekt: Local RAG API

**[Otevřít Local RAG API](PROJECT.md)**

Ingest PDF extrahuje a chunkuje technickou dokumentaci do ChromaDB. Současná HTTP pipeline používá výběr kontextu, reranking, pravidla odpovědí specifická pro OSPF a generování modelem jako fallback. Samostatné strategie retrievalu se porovnávají v offline evaluačním CLI.

<a id="cz-co-je-implementováno"></a>

### Co je implementováno

- **API:** FastAPI endpointy pro health, readiness, statistiky a otázky; typované modely požadavků/odpovědí.
- **Dokumentová pipeline:** extrakce textu PDF, chunkování, indexování do ChromaDB a metadata zdroje/stránky/chunku.
- **Retrieval:** vektorový retrieval pomocí větných embeddingů, samostatně testovaný lexikální BM25 retriever a existující RAG postup retrievalu/rerankingu.
- **Evaluace:** označené datasety otázek, Hit@1/3/5/8, MRR, latence mean/p50/p95, JSONL historie evaluace, hashe datasetů a Git původ.
- **Testování:** jednotkové a regresní pytest testy se syntetickými fixtures a falešnými Chroma kolekcemi; GitHub Actions CI.
- **Nástroje nasazení:** Dockerfile a Compose konfigurace pro lokální kontejner API.

<a id="cz-ověření"></a>

### Ověření

Ověřený běh pro **commit `ce9a088`, 8. 11. 2026**: **223 testů prošlo za 7,62 s** na Ubuntu / Python 3.11 ([běh GitHub Actions](https://github.com/jyenten/local_rag_api/actions/runs/42511536430)). Tento datovaný výsledek pokrývá `main` po změně znovupoužití tokenů při inicializaci BM25, omezení publikovaného portu Compose na loopback a aktualizacích dokumentace; nedokládá zlepšení kvality retrievalu, end-to-end latence ani bezpečnosti a zůstává oddělený od evaluace retrievalu na skutečném korpusu. Historické lokální běhy zůstávají v [deníku učení](LEARNING_LOG.md).

<a id="cz-zaznamenany-retrieval-baseline"></a>

### Zaznamenaný retrieval baseline — 20. 10. 2026

| Dataset | Otázek | BM25 MRR | Vector MRR |
| --- | ---: | ---: | ---: |
| DEV | 20 | 0.7171 | 0.8321 |
| RANDOM | 25 | 0.8133 | 0.6050 |

Jde o historické výsledky zapsané v [deníku učení](LEARNING_LOG.md#cz-2026-10-20--fáze-34-evaluace-retrievalu). Původní JSONL běhy, korpus ani index nejsou součástí tohoto veřejného snapshotu; hodnoty nebyly pro tuto úpravu dokumentace znovu reprodukovány. MRR hodnotí pořadí nalezené evidence, nikoli přesnost generované odpovědi. Pevný RANDOM dataset slouží k průzkumu robustnosti; TEST je vyhrazen závěrečnému posouzení. Původ a omezení porovnání popisuje [evaluační příručka](EVALUATION.md#cz-8-historický-baseline-phase-34-2026-10-20).

<a id="cz-architektura-v-přehledu"></a>

### Architektura v přehledu

| Cesta | Současný tok | Rozhraní / výstup |
| --- | --- | --- |
| HTTP odpovědi | Chroma retrieval → výběr kontextu a reranking → OSPF pravidla / modelový fallback | `POST /ask`; odpověď, kontext a metadata zdrojů |
| Offline evaluace | `legacy` / `vector` / `bm25` → porovnání s golden evidence | CLI; MRR, Hit@K, latence retrievalu a JSONL historie |
| Průzkum PDF | Lokální PDF stránky → samostatné BM25 vyhledávání stránek | CLI `search_pdf`; podklad pro ruční ověření evidence |

**Stav integrace:** HTTP endpoint `/ask` používá existující RAG pipeline nad ChromaDB. `legacy`, `vector` a `bm25` jsou volitelné v offline evaluačním CLI na DEV/RANDOM. Hybridní RRF zatím není integrované do veřejné větve `main`.

<a id="cz-jak-začít"></a>

## Jak začít

Začni [českým přehledem projektu](PROJECT.md) ([English](../en/PROJECT.md)). Pro instalaci/ingest použij [provozní návod](OPERATIONS.md#cz); pro evidenci, metriky a postup porovnání [evaluační příručku](EVALUATION.md#cz).

**Stav projektu:** výukové inženýrské portfolio / aktivně vyvíjený lokální prototyp. Hostovaná ukázka není k dispozici. Instalace a první použití modelů mohou vyžadovat jejich stažení; inference používá lokální modely.

<a id="cz-inženýrský-přístup"></a>

## Inženýrský přístup

Projekt vzniká s výraznou pomocí ChatGPT a Codexu, včetně generování kódu a testů, diagnostiky a revizí. [Deník učení](LEARNING_LOG.md) zaznamenává spolupráci a doklady učení; dokončené funkce rozlišuje od samostatně prokázaných dovedností. Vývojové postupy popisuje [vývojová příručka](DEVELOPMENT_GUIDE.md).

**Pokyny pro přispěvatele a agenty:** před změnou souborů načti [globální pravidla](AGENTS.md) a pro RAG také [projektová pravidla](PROJECT_AGENTS.md). Jejich umístění pod `docs/` nemění jejich působnost. Původ BM25 testů a historii práce agentů zachovává [deník učení](LEARNING_LOG.md#cz-2026-10-13--fáze-33-bm25-retriever).

<a id="cz-struktura-repozitáře"></a>

## Struktura repozitáře

- [rag_api_project/](../../rag_api_project/) — aktivní vývoj FastAPI, RAG, retrievalu a evaluace.
- [docs/](../README.md) — všechny ostatní verzované Markdown soubory: české/anglické příručky, pravidla agentů a historie učení.
- [.github/](../../.github/) — konfigurace CI workflow.
- [archive/](../../archive/) — 29 dřívějších složek programovacích a ML cvičení zachovaných jako historie učení a reference.

<a id="cz-další-kroky"></a>

## Další kroky

- Zachovat baseline BM25/Vector na DEV a RANDOM ze srovnání retrievalu zaznamenaného 20. 10. 2026.
- Implementovat a vyhodnotit hybridní lexikální + sémantický retrieval (RRF) bez ladění na TEST.
- Zlepšovat reprodukovatelnost, pinování závislostí, provozní metriky a úvodní dokumentaci.

<a id="cz-rychlý-start-na-windows"></a>

## Rychlý start na Windows

```powershell
# Z kořene klonovaného repozitáře:
cd rag_api_project
python --version  # Musí být 3.11.x.
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

Potom vlož vlastní PDF do `data/`. **Před ingestem čti varování v provozním návodu: existující Chroma kolekce je smazána a znovu vytvořena.**

```powershell
python -m scripts.ingest
python -m uvicorn app.main:app --reload
```

Swagger: http://127.0.0.1:8000/docs. Offline evaluaci můžeš spustit samostatně nad již existujícím indexem:

```powershell
python -m scripts.evaluate_retrieval --retriever bm25 --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset dev
```

Tyto evaluace zapisují JSONL historii. TEST dataset je záměrně vyhrazen pro závěrečné ověření.

[↑ Nahoru / Back to top](#top)
