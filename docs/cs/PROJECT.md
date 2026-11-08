<a id="top"></a>

<a id="rag-api--vyhledávání-v-dokumentech-a-evaluace-retrievalu"></a>

# Local RAG API — vyhledávání v dokumentech a evaluace retrievalu

[Česky](#cz) · [English](../en/PROJECT.md#en) · [Dokumentace](../README.md)

<a id="obsah"></a>

<details>
<summary>Obsah / Contents — kliknutím rozbalit / click to expand</summary>

**Česky**

- [Technologie](#cz-technologie)
- [Architektura a moduly](#cz-architektura-a-moduly)
- [Tok dat](#cz-tok-dat)
- [Hlavní návrhová rozhodnutí](#cz-hlavní-návrhová-rozhodnutí)
- [Lokální instalace](#cz-lokální-instalace)
- [Indexování lokálních PDF](#cz-indexování-lokálních-pdf)
- [Spuštění API](#cz-spuštění-api)
- [Testy](#cz-testy)
- [Offline evaluace retrievalu](#cz-offline-evaluace-retrievalu)
- [Samostatné BM25 vyhledávání v PDF](#cz-samostatné-bm25-vyhledávání-v-pdf)
- [Docker a Compose](#cz-docker-a-compose)
- [Současná omezení a další kroky](#cz-současná-omezení-a-další-kroky)
- [Vývoj s pomocí AI a hranice spolupráce](#cz-vývoj-s-pomocí-ai-a-hranice-spolupráce)
- [Rozcestník](#cz-rozcestník)

</details>

---

<a id="cz"></a>

Lokální Python/FastAPI chatbot nad technickou PDF dokumentací, aktuálně zaměřený na OSPF, s evaluací retrievalu, metadaty zdrojů a regresním testováním. Inference běží lokálně; instalace a první použití modelů mohou vyžadovat jejich stažení.

**Stav:** aktivně vyvíjený výukový prototyp, nikoli produkční služba. Existující `/ask` pipeline používá Chroma retrieval, výběr kontextu, reranking a odpovědi podle pravidel nebo modelu. Vedle toho repozitář obsahuje vektorový retriever, lexikální BM25 retriever a nástroje offline evaluace retrievalu.


<a id="cz-technologie"></a>

## Technologie

Python 3.11 · FastAPI · Pydantic · ChromaDB · Sentence Transformers · `rank-bm25` · Transformers/PyTorch · pypdf · pytest · Docker · GitHub Actions.


<a id="cz-architektura-a-moduly"></a>

## Architektura a moduly

| Komponenta | Cesta | Účel |
| --- | --- | --- |
| HTTP API | `app/main.py` | `/`, `/health`, `/ready`, `/stats`, `/ask` |
| Konfigurace | `app/config.py` | Nastavení Pydantic podle prostředí |
| Koordinace RAG | `app/rag.py` | Odpovědi a podpůrný kontext |
| Existující retrieval pipeline | `app/retrieval.py` | Retrieval, výběr řádků kontextu a reranking |
| Vektorový retrieval | `app/retrievers/vector.py` | Vektorový baseline Chroma |
| BM25 retrieval | `app/retrievers/bm25.py` | Lexikální řazení nad Chroma chunky |
| Ingest PDF | `scripts/ingest.py` | Extrakce a indexování textu PDF |
| CLI vyhledávání v PDF | `scripts/search_pdf.py` | Nezávislé lokální BM25 vyhledávání stránek |
| Evaluace retrievalu | `evaluation/`, `scripts/evaluate_retrieval.py` | Kvalita pořadí, latence a původ výsledků |
| Testy | `tests/` | Jednotkové a regresní testy |


<a id="cz-tok-dat"></a>

### Tok dat

| Cesta | Současný tok | Rozhraní / výstup |
| --- | --- | --- |
| HTTP odpovědi | Chroma retrieval → výběr kontextu a reranking → OSPF pravidla / modelový fallback | `POST /ask`; odpověď, kontext a metadata zdrojů |
| Offline evaluace | `legacy` / `vector` / `bm25` → porovnání s golden evidence | CLI; MRR, Hit@K, latence retrievalu a JSONL historie |
| Průzkum PDF | Lokální PDF stránky → samostatné BM25 vyhledávání stránek | CLI `search_pdf`; podklad pro ruční ověření evidence |

**Hranice integrace:** BM25 je implementované a volitelné v **offline evaluačním CLI** společně s `legacy` a `vector`. HTTP `/ask` API nebylo přepnuto na BM25 ani hybridní režim. Hybridní RRF je rozpracované, nikoli zavedená vydaná funkce.


<a id="cz-hlavní-návrhová-rozhodnutí"></a>

## Hlavní návrhová rozhodnutí

- Indexované chunky nesou zdroj, fyzickou PDF stránku a metadata chunku pro dohledatelnost.
- BM25 načítá uložené chunky v omezených dávkách, validuje konzistenci dat, filtruje dokumenty bez lexikální shody a při shodě skóre řadí podle vzestupného ID chunku.
- Vektorové vyhledávání vrací skóre typu vzdálenosti (nižší bývá bližší); BM25 vrací skóre relevance (vyšší je první). Surová skóre se nemají přímo porovnávat.
- Evaluace se dělí na vývojová, náhodně vybraná a oddělená testovací data s hashi datasetů a Git původem.
- Modelové generování je záloha k odpovědím podle úlohových pravidel; systém není univerzální produkční QA engine.


<a id="cz-lokální-instalace"></a>

## Lokální instalace

Spouštěj z `rag_api_project/` s Pythonem 3.11.

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

Verze závislostí nyní nejsou pinované; zatím nejde o plně reprodukovatelnou instalaci podle lock souboru.


<a id="cz-indexování-lokálních-pdf"></a>

### Indexování lokálních PDF

Vlož technická PDF do `data/` (ignorováno Gitem), potom spusť:

~~~bash
python -m scripts.ingest
~~~

Lokální Chroma kolekce je uložená v `chroma_db/`. Ukázková konfigurace používá název `ospf`. **Pozor: `scripts.ingest` existující kolekci tohoto jména smaže a znovu vytvoří**, místo průběžného doplňování. Pokud je nutné index zachovat, zálohuj jej. API potřebuje vhodná indexovaná data pro odpovědi nad korpusem. Úplný postup: [OPERATIONS.md](OPERATIONS.md#cz).


<a id="cz-spuštění-api"></a>

## Spuštění API

~~~bash
python -m uvicorn app.main:app --reload
~~~

Interaktivní OpenAPI dokumentaci otevři na `http://127.0.0.1:8000/docs`.

- `GET /` a `GET /health` — životnost služby a informace o prostředí.
- `GET /ready` — inicializuje retrieval službu a vrací počet chunků v kolekci. Neprovádí otázku ani neověřuje načtení generovacího modelu; nejde o úplný smoke test `/ask`.
- `GET /stats` — informace o kolekci.
- `POST /ask` — přijme JSON otázku a vrátí odpověď s podpůrným kontextem a náhledy zdrojů.

Příklad požadavku:

~~~bash
curl -X POST http://127.0.0.1:8000/ask -H "Content-Type: application/json" -d '{"question":"How does OSPF select the router ID?"}'
~~~

Ve Windows PowerShell použij `Invoke-RestMethod`, pokud se liší shellové uvozování `curl`:

~~~powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/ask -Method Post -ContentType 'application/json' -Body '{"question":"How does OSPF select the router ID?"}'
~~~


<a id="cz-testy"></a>

## Testy

Z `rag_api_project/`:

~~~bash
python -m pytest -q tests
~~~

Ověřený běh pro **commit `7081599`, 8. 11. 2026**: **223 testů prošlo za 5,65 s** na Ubuntu / Python 3.11 ([běh GitHub Actions](https://github.com/jyenten/local_rag_api/actions/runs/42482651938)). Tento datovaný výsledek testů následuje po změně znovupoužití tokenů při inicializaci BM25; nedokládá zlepšení kvality retrievalu ani end-to-end latence a zůstává oddělený od evaluace retrievalu na skutečném korpusu. Historické lokální běhy zůstávají v [deníku učení](LEARNING_LOG.md).

BM25 testy používají syntetické Chroma fixtures a pokrývají stránkování, řazení, deterministické rozhodování při shodě skóre, soulad metadat, neplatné dotazy a záznamy i vadné dávky.


<a id="cz-offline-evaluace-retrievalu"></a>

## Offline evaluace retrievalu

Framework hlásí MRR, Hit@1/3/5/8 a latenci retrievalu mean/p50/p95. Metadata běhu obsahují hash datasetu, Git commit a stav necommitnutých změn. Běhové výsledky pod `eval/results/` jsou vyloučené z verzování. Zopakování historického výsledku vyžaduje stejné zdrojové PDF, index, konfiguraci retrievalu a verze modelů a závislostí. Veřejný snapshot neobsahuje původní korpus, index ani JSONL historie běhů.

Podporované příkazy ve zveřejněném evaluačním CLI:

~~~bash
python -m scripts.evaluate_retrieval --retriever legacy --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset dev
python -m scripts.evaluate_retrieval --retriever bm25 --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset random
python -m scripts.evaluate_retrieval --retriever bm25 --dataset random
~~~

CLI přijímá `legacy`, `vector`, `bm25` a `dev`/`random`. Zapisuje JSONL historii běhů, proto nejde o operaci pouze pro čtení. Oddělený TEST je vyhrazen závěrečnému hodnocení, nikoli iterativnímu ladění. Postup tvorby evidence a porovnávání viz [EVALUATION.md](EVALUATION.md#cz).


<a id="cz-samostatné-bm25-vyhledávání-v-pdf"></a>

## Samostatné BM25 vyhledávání v PDF

Samostatné průzkumné CLI indexuje lokální PDF stránky:

~~~bash
python -m scripts.search_pdf "router ID" --top-k 5 --interactive
~~~

Nástroj čte PDF v `data/` a liší se od `BM25Retriever`, který pracuje s Chroma chunky.


<a id="cz-docker-a-compose"></a>

## Docker a Compose

Repozitář obsahuje Dockerfile a `compose.yaml`:

~~~bash
docker compose up --build
docker compose down
~~~

Compose mapuje hostitelský port `8001` na kontejnerový `8000` a připojuje lokální adresáře Chroma/modelové cache. Jde o lokální kontejnerovou konfiguraci, nikoli hostovanou ukázku.

**Známá omezení:** obraz kopíruje `app/` a `scripts/`, ale vynechává `document_search/`, `evaluation/`, `eval/` a zdrojová PDF. Compose nepředává hostitelský `.env` do kontejneru. Ingest a evaluaci spouštěj nativně; kontejnerové API vyžaduje kompatibilní připojený index. Konfigurační a balíčkové hranice viz [OPERATIONS.md](OPERATIONS.md#cz).


<a id="cz-současná-omezení-a-další-kroky"></a>

## Současná omezení a další kroky

- Zachovat [baseline BM25 oproti Vector na DEV/RANDOM zaznamenaný 20. 10. 2026](EVALUATION.md#cz-8-historický-baseline-phase-34-2026-10-20).
- Experimentovat s hybridním lexikálním + sémantickým retrievalem (RRF) podle měření bez ladění na odděleném TEST.
- Zlepšit pinování závislostí, úplnost Docker balíčku a provozní observabilitu.
- Pokračovat ve zlepšování robustnosti extrakce, hlášení chyb a evaluace na dosud neviděných otázkách.


<a id="cz-vývoj-s-pomocí-ai-a-hranice-spolupráce"></a>

## Vývoj s pomocí AI a hranice spolupráce

Projekt vzniká s výraznou pomocí ChatGPT a Codexu, včetně generování kódu a testů, diagnostiky a revizí. [Deník učení](LEARNING_LOG.md) zaznamenává spolupráci, původ BM25 testů a doklady učení; dokončené funkce rozlišuje od samostatně prokázaných dovedností. Podrobnou historii worktrees a soukromého zrcadla zachovává tento deník.

Před změnou souborů načti [globální pravidla](AGENTS.md) a [projektová pravidla](PROJECT_AGENTS.md). Vývojové a revizní postupy popisuje [vývojová příručka](DEVELOPMENT_GUIDE.md).


<a id="cz-rozcestník"></a>

## Rozcestník

| Úkol | Dokument |
| --- | --- |
| Kompletní instalace, `.env`, ingest, kontrola Chroma, API, Docker, testy | [Provozní příručka (CZ/EN)](OPERATIONS.md#cz) |
| Golden evidence, kandidáti, schvalování, validace, metriky | [Evaluace (CZ/EN)](EVALUATION.md#cz) |
| Architektura současná i plánovaná | [ARCHITECTURE.md](ARCHITECTURE.md#cz) |
| Stav a prioritizace vývoje | [ROADMAP.md](ROADMAP.md#cz) |
| Vývoj, testy, Git | [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md#cz) |
| Pravidla Codex/ChatGPT | [AGENTS.md](PROJECT_AGENTS.md#cz), [globální AGENTS.md](AGENTS.md#cz) |

[↑ Nahoru / Back to top](#top)
