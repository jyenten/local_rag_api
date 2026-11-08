<a id="top"></a>

# Roadmapa projektu AI RAG

[Česky](#cz) · [English](../en/ROADMAP.md#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Obsah — kliknutím rozbalit</summary>

- [Stavový přehled — 2026-10-28](#cz-stavový-přehled--2026-10-28)
- [Aktuální zaměření vývoje](#cz-aktuální-zaměření-vývoje)
- [Jak číst a aktualizovat schválený plán](#cz-jak-číst-a-aktualizovat-schválený-plán)
- [FÁZE 1 - Funkční kostra RAG](#cz-fáze-1---funkční-kostra-rag)
- [FÁZE 2 - Základ evaluace](#cz-fáze-2---základ-evaluace)
- [FÁZE 2A - Univerzální průzkumník dokumentů](#cz-fáze-2a---univerzální-průzkumník-dokumentů)
- [FÁZE 2A.0 - Zmrazení architektury](#cz-fáze-2a0---zmrazení-architektury)
- [FÁZE 2A.1 - Datové modely](#cz-fáze-2a1---datové-modely)
- [FÁZE 2A.2 - Zpracování textu](#cz-fáze-2a2---zpracování-textu)
- [FÁZE 2A.3 - Základy bezpečnosti](#cz-fáze-2a3---základy-bezpečnosti)
- [FÁZE 2A.4 - Načítání PDF a validace PDF](#cz-fáze-2a4---načítání-pdf-a-validace-pdf)
- [FÁZE 2A.5 - BM25 index](#cz-fáze-2a5---bm25-index)
- [FÁZE 2A.6 - Vyhledávací modul](#cz-fáze-2a6---vyhledávací-modul)
- [FÁZE 2A.7 - CLI](#cz-fáze-2a7---cli)
- [FÁZE 2A.8 - Integrace](#cz-fáze-2a8---integrace)
- [FÁZE 2B - Evaluační datové modely](#cz-fáze-2b---evaluační-datové-modely)
- [FÁZE 2C - Metriky retrievalu](#cz-fáze-2c---metriky-retrievalu)
- [FÁZE 2D - Evaluační runner a historie](#cz-fáze-2d---evaluační-runner-a-historie)
- [FÁZE 2E - Evaluace RANDOM](#cz-fáze-2e---evaluace-random)
- [FÁZE 2F - Kompletní evaluační dataset](#cz-fáze-2f---kompletní-evaluační-dataset)
- [FÁZE 3 - Refaktoring retrievalu](#cz-fáze-3---refaktoring-retrievalu)
- [FÁZE 3.1 - Retrieval modely](#cz-fáze-31---retrieval-modely)
- [FÁZE 3.2 - Embeddingy](#cz-fáze-32---embeddingy)
- [FÁZE 3.3 - Vektorové vyhledávání](#cz-fáze-33---vektorové-vyhledávání)
- [FÁZE 3.4 - Zpracování dotazu](#cz-fáze-34---zpracování-dotazu)
- [FÁZE 3.5 - Reranker](#cz-fáze-35---reranker)
- [FÁZE 3.6 - Skórování](#cz-fáze-36---skórování)
- [FÁZE 3.7 - Retrieval služba](#cz-fáze-37---retrieval-služba)
- [FÁZE 4 - Zodolnění API](#cz-fáze-4---zodolnění-api)
- [FÁZE 4.1 - Životní cyklus aplikace](#cz-fáze-41---životní-cyklus-aplikace)
- [FÁZE 4.2 - Routy](#cz-fáze-42---routy)
- [FÁZE 4.3 - Vkládání závislostí](#cz-fáze-43---vkládání-závislostí)
- [FÁZE 4.4 - Chyby](#cz-fáze-44---chyby)
- [FÁZE 4.5 - Middleware](#cz-fáze-45---middleware)
- [FÁZE 5 - Produkční inženýrství](#cz-fáze-5---produkční-inženýrství)
- [FÁZE 5.1 - Linux / WSL2](#cz-fáze-51---linux--wsl2)
- [FÁZE 5.2 - Strukturované logování](#cz-fáze-52---strukturované-logování)
- [FÁZE 5.3 - Běhové metriky](#cz-fáze-53---běhové-metriky)
- [FÁZE 5.4 - Zodolnění Dockeru](#cz-fáze-54---zodolnění-dockeru)
- [FÁZE 5.5 - CI/CD](#cz-fáze-55---cicd)
- [FÁZE 6 - Bezpečnost](#cz-fáze-6---bezpečnost)
- [FÁZE 6.1 - Modelování hrozeb](#cz-fáze-61---modelování-hrozeb)
- [FÁZE 6.2 - Validace běhových vstupů](#cz-fáze-62---validace-běhových-vstupů)
- [FÁZE 6.3 - Běhové limity](#cz-fáze-63---běhové-limity)
- [FÁZE 6.4 - Tajemství](#cz-fáze-64---tajemství)
- [FÁZE 6.5 - Bezpečnost závislostí](#cz-fáze-65---bezpečnost-závislostí)
- [FÁZE 6.6 - Bezpečnost kontejneru](#cz-fáze-66---bezpečnost-kontejneru)
- [FÁZE 6.7 - Bezpečnost HTTP](#cz-fáze-67---bezpečnost-http)
- [FÁZE 6.8 - Bezpečnost specifická pro RAG](#cz-fáze-68---bezpečnost-specifická-pro-rag)
- [FÁZE 7 - Produkční verze v1](#cz-fáze-7---produkční-verze-v1)
- [FÁZE 7.1 - Health a readiness](#cz-fáze-71---health-a-readiness)
- [FÁZE 7.2 - Produkční smoke test](#cz-fáze-72---produkční-smoke-test)
- [FÁZE 7.3 - Dokumentace](#cz-fáze-73---dokumentace)
- [FÁZE 8 - Rozšíření](#cz-fáze-8---rozšíření)
- [FÁZE 8A - Průzkum agentů](#cz-fáze-8a---průzkum-agentů)
- [FÁZE 8B - SQL a ETL](#cz-fáze-8b---sql-a-etl)
- [FÁZE 8C - MLOps](#cz-fáze-8c---mlops)
- [FÁZE 8D - Pokročilí agenti](#cz-fáze-8d---pokročilí-agenti)
- [Původní plánovací odhady — historické](#cz-původní-plánovací-odhady--historické)
- [Historie plánování](#cz-historie-plánování)

</details>

---

<a id="cz"></a>

Tento dokument určuje **co budovat, pořadí fází, cíle a kritéria přijetí**. Postup implementace a revize patří do [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md#cz), hranice komponent do [ARCHITECTURE.md](ARCHITECTURE.md#cz) a datované výsledky práce a učení do [LEARNING_LOG.md](LEARNING_LOG.md#cz).


<a id="cz-stavový-přehled--2026-10-28"></a>

## Stavový přehled — 2026-10-28

Jde o aktuální plánovací bod, nikoli o přečíslování nebo náhradu schválených specifikací fází níže. Dokončení milníku nepotvrzuje splnění všech kritérií širší fáze ani připravenost do produkce.

| Milník | Zjištěný stav | Důkazy / postup |
| --- | --- | --- |
| RAG API, ingest PDF a úložiště Chroma | Implementovaný prototyp; další zodolnění je plánované | [README projektu](PROJECT.md), [architektura](ARCHITECTURE.md#cz) |
| Samostatný průzkumník PDF stránek | Implementovaný | `document_search/`, [provoz](OPERATIONS.md#cz) |
| Evaluace retrievalu podle důkazů | Implementované metriky, historie, latence a provenance | `evaluation/`, [evaluační metodika](EVALUATION.md#cz) |
| Porovnání chunkového BM25 a Vector | Implementované v offline CLI nad DEV/RANDOM | `app/retrievers/`, [zapsané milníky](LEARNING_LOG.md#cz-historie-projektu-a-učení) |
| Hybridní lexikální/sémantický retrieval s RRF | Lokálně rozpracovaný; nejde o zveřejněný režim CLI/API | [Záznam necommitnuté práce](LEARNING_LOG.md#cz-necommitnutá-práce-pozorovaná-28-10-2026) |
| Evaluace na odděleném TEST | Vyhrazena pro závěrečné posouzení, nikoli průběžné ladění | [Evaluační pravidla](EVALUATION.md#cz) |
| Dvojjazyčné příručky a regrese validátoru | Začleněné přes [PR #3](https://github.com/jyenten/local_rag_api/pull/3) | [Provoz](OPERATIONS.md#cz), [evaluace](EVALUATION.md#cz) |
| Automatizace závislostí a bezpečnosti | Zapnutá; nálezy závislosti ChromaDB zůstávají otevřené | `.github/workflows/`, [aktuální projektový bod](LEARNING_LOG.md#cz-ověřený-stav-projektu) |

Podrobné výsledky a historické MRR/Hit@K patří do evaluační metodiky a deníku učení; roadmapa neudržuje další kopii benchmarkové tabulky.


<a id="cz-aktuální-zaměření-vývoje"></a>

## Aktuální zaměření vývoje

Dalším zaznamenaným milníkem je hybridní BM25 + Vector retrieval s RRF. Nejprve dokonči a zkontroluj implementaci, potom změř DEV/RANDOM proti zachovaným baseline a až pak rozhoduj o zlepšeních. TEST ponech oddělený. Lokální experimenty s backendem a nezačleněné návrhy závislostí podléhají vlastní revizi; jejich existence není začleněním do `main` ani schválením náhrady retrieval architektury.

Deník učení historicky označoval BM25 jako Phase 3.3, evaluaci retrievalu jako Phase 3.4 a hybridní RRF jako Phase 3.5. Tato označení **nejsou identifikátory fází této roadmapy**. Zde nadále platí původní čísla a názvy: 3.3 Vektorové vyhledávání, 3.4 Zpracování dotazu a 3.5 Reranker. Při odkazu na práci v deníku používej celý název milníku.


<a id="cz-jak-číst-a-aktualizovat-schválený-plán"></a>

## Jak číst a aktualizovat schválený plán

Specifikace fází níže zachovávají schválené pořadí, plánované moduly, výukové koncepty a checklisty Definition of Done. Jejich původní **stav**, odhady a nezaškrtnutá políčka jsou výchozím plánem, nikoli dalším živým přehledem postupu. Zjištěný pokrok čti v přehledu výše; nezaškrtnuté historické políčko samo nedokazuje, že modul chybí. Kritéria neoznačuj za splněná bez potřebných důkazů.

Pracovní postup je **Complete → Measure → Improve**. Společná pravidla rozsahu, backlogu, zmrazení, testování a revize patří do [vývojového postupu](DEVELOPMENT_GUIDE.md#cz-vývojový-postup). Změna cílů, priorit nebo kritérií přijetí vyžaduje výslovné plánovací rozhodnutí; redakční úprava ji neschvaluje.

---


<a id="cz-fáze-1---funkční-kostra-rag"></a>

# FÁZE 1 - Funkční kostra RAG

**Stav:** Z větší části dokončeno

**Původní odhad zbývající práce:** 2–4 hodiny

<a id="cz-cíl"></a>

## Cíl

Udržovat funkční RAG aplikaci od vstupu až po odpověď.

Hlavní běhová pipeline:

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

Smyslem FÁZE 1 není architektonická dokonalost.

Smyslem je funkční systém, který lze následně měřit a zlepšovat.

---

<a id="cz-11-appconfigpy"></a>

## 1.1 `app/config.py`

<a id="cz-odpovědnosti"></a>

### Odpovědnosti

- konfigurace aplikace
- názvy modelů
- konfigurace kolekce Chroma
- limity retrievalu
- limity generování
- konfigurace prostředí

<a id="cz-důležité-koncepty"></a>

### Důležité koncepty

- centralizovaná konfigurace
- proměnné prostředí
- validace konfigurace
- Pydantic Settings

<a id="cz-budoucí-směr"></a>

### Budoucí směr

Konfigurace se má načítat přes validovaný objekt nastavení, nikoli přes duplicitní konstanty.

Možný veřejný přístup:

```python
get_settings()
```

---

<a id="cz-12-appschemaspy"></a>

## 1.2 `app/schemas.py`

<a id="cz-současné-modely"></a>

### Současné modely

- `QuestionRequest`
- `SourceChunk`
- `AnswerResponse`

<a id="cz-možné-budoucí-modely"></a>

### Možné budoucí modely

- `ErrorResponse`
- `HealthResponse`

<a id="cz-důležitý-koncept"></a>

### Důležitý koncept

API schémata popisují data přenášená přes hranici HTTP.

Mají zůstat oddělená od interních retrieval modelů.

---

<a id="cz-13-appretrievalpy"></a>

## 1.3 `app/retrieval.py`

<a id="cz-současné-odpovědnosti"></a>

### Současné odpovědnosti

- načítání embedding modelu
- příprava dotazu
- retrieval z Chroma
- výběr kandidátů
- přerovnání pomocí CrossEncoderu
- heuristické skórování
- výběr výsledků

<a id="cz-současný-technický-dluh"></a>

### Současný technický dluh

Tento modul nyní spojuje více odpovědností a logiku specifickou pro doménu.

Ve FÁZI 1 se záměrně nerefactoruje.

Větší refaktoring retrievalu patří do:

```text
PHASE 3
```

---

<a id="cz-14-appgenerationpy"></a>

## 1.4 `app/generation.py`

<a id="cz-hlavní-odpovědnosti"></a>

### Hlavní odpovědnosti

- načítání generativního modelu
- sestavení promptu
- inference modelu
- generování odpovědi

Hlavní tok:

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

Možné budoucí oddělení:

```text
prompt construction
model inference
output processing
```

K tomuto rozdělení přistup pouze tehdy, vyžaduje-li je složitost.

---

<a id="cz-15-appragpy"></a>

## 1.5 `app/rag.py`

<a id="cz-odpovědnost"></a>

### Odpovědnost

Orchestrace RAG.

Cílový konceptuální tok:

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

<a id="cz-současný-technický-dluh-1"></a>

### Současný technický dluh

Současná implementace obsahuje chování specifické pro OSPF.

Jeho odstranění patří do:

```text
PHASE 3
```

---

<a id="cz-16-appmainpy"></a>

## 1.6 `app/main.py`

<a id="cz-odpovědnost-1"></a>

### Odpovědnost

Vstupní bod aplikace FastAPI.

Současné endpointy:

```text
GET /
GET /health
POST /ask
```

Cílová odpovědnost:

```text
HTTP request
    ->
validation
    ->
application service
    ->
HTTP response
```

Aplikační logika se má postupně přesunout mimo vstupní bod API.

---

<a id="cz-17-scriptsingestpy"></a>

## 1.7 `scripts/ingest.py`

<a id="cz-současná-pipeline"></a>

### Současná pipeline

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

<a id="cz-dosavadní-zlepšení"></a>

### Dosavadní zlepšení

- čištění textu PDF
- ochrana a obnova URL
- chunkování podle slov
- překryv chunků
- validace překryvu

<a id="cz-důležité-pravidlo"></a>

### Důležité pravidlo

Ingest nerefactoruj pouze kvůli architektonické symetrii.

Refactoruj ho pouze tehdy, když:

- je obtížné testování
- je nutné opětovné použití
- výrazně roste složitost
- evaluace odhalí problém ingestu

---

<a id="cz-fáze-1--podmínky-dokončení"></a>

## FÁZE 1 — Podmínky dokončení

- [x] PDF dokumenty lze ingestovat
- [x] extrakce textu funguje
- [x] chunkování funguje
- [x] lze generovat embeddingy
- [x] ChromaDB ukládá prohledávatelné chunky
- [x] retrieval funguje
- [x] přerovnání funguje
- [x] generování funguje
- [x] `POST /ask` funguje
- [x] odpovědi obsahují informace o zdrojích
- [x] smoke testy procházejí
- [ ] zbývající technický dluh je zdokumentovaný

Po splnění těchto podmínek je FÁZE 1 zmrazená.

---


<a id="cz-fáze-2---základ-evaluace"></a>

# FÁZE 2 - Základ evaluace

**Stav:** Rozpracováno

**Původní odhad zbývající práce:** 8–12 hodin

<a id="cz-cíl-1"></a>

## Cíl

Vytvořit spolehlivý evaluační rámec před většími změnami retrievalu.

Retrieval se už nemá zlepšovat pouze podle několika ručně vybraných otázek.

Cílový vývojový tok:

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

<a id="cz-úlohy-evaluačních-datasetů"></a>

## Úlohy evaluačních datasetů

Tři kategorie datasetů mají záměrně odlišné účely.

<a id="cz-dev"></a>

### DEV

Používá se při vývoji a ladění.

Výsledky DEV mohou ovlivnit implementační rozhodnutí.

Cílová velikost:

```text
approximately 20 manually validated questions
```

---

<a id="cz-random"></a>

### RANDOM

Používá se pro:

- průzkum robustnosti
- hledání neočekávaných selhání
- průzkum pokrytí korpusu

Náhodné vzorkování musí být reprodukovatelné pomocí uloženého seedu.

RANDOM nenahrazuje TEST.

---

<a id="cz-test"></a>

### TEST

Oddělená závěrečná evaluace.

TEST se nesmí opakovaně procházet a používat k ladění.

Jeho účelem je odhad generalizace po dokončení ladění.

---


<a id="cz-fáze-2a---univerzální-průzkumník-dokumentů"></a>

# FÁZE 2A - Univerzální průzkumník dokumentů

**Historický stav plánu:** Aktuální aktivní podfáze

**Odhad práce:** 3–4 hodiny

<a id="cz-cíl-2"></a>

## Cíl

Vytvořit opakovaně použitelný lexikální průzkumník korpusu nezávislý na doméně pro:

- hledání kandidátních důkazů
- prohlížení obsahu PDF
- ruční validaci referenčních důkazů
- pomoc při sestavování datasetů DEV / RANDOM / TEST

Průzkumník musí fungovat i po nahrazení celého PDF korpusu.

Příklady budoucích domén:

```text
Kubernetes
cybersecurity
Linux
law
manufacturing
accounting
networking
```

Průzkumník nesmí obsahovat pravidla řazení specifická pro OSPF.

---

<a id="cz-cílová-struktura"></a>

## Cílová struktura

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

Testy:

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


<a id="cz-fáze-2a0---zmrazení-architektury"></a>

# FÁZE 2A.0 - Zmrazení architektury

<a id="cz-cíl-3"></a>

## Cíl

Před implementací definovat:

- odpovědnosti modulů
- datové modely
- veřejná rozhraní
- směr závislostí
- bezpečnostní hranice
- podmínky dokončení

Dokumentace:

```text
docs/ROADMAP.md
docs/ARCHITECTURE.md
docs/DEVELOPMENT_GUIDE.md
```

Produkční kód nepřepracovávej opakovaně, když už vznikají závislé moduly, pokud to nevyžaduje konkrétní technický problém.

---


<a id="cz-fáze-2a1---datové-modely"></a>

# FÁZE 2A.1 - Datové modely

<a id="cz-soubor"></a>

## Soubor

```text
document_search/models.py
```

<a id="cz-plánované-modely"></a>

## Plánované modely

```python
PageDocument
SearchResult
BM25SearchIndex
```

<a id="cz-pagedocument"></a>

### `PageDocument`

Konceptuálně:

```python
PageDocument(
    source="manual.pdf",
    page=26,
    text="...",
)
```

Představuje jednu prohledávatelnou zdrojovou stránku.

---

<a id="cz-searchresult"></a>

### `SearchResult`

Konceptuálně:

```python
SearchResult(
    document=document,
    score=12.5,
)
```

Představuje jeden seřazený výsledek BM25.

---

<a id="cz-bm25searchindex"></a>

### `BM25SearchIndex`

Vlastní:

```text
page corpus
+
BM25 model
```

Volající tak nemusí tyto objekty ručně udržovat v souladu.

---

<a id="cz-nový-koncept---neměnné-datové-třídy"></a>

## Nový koncept - Neměnné datové třídy

Preferovaný vzor:

```python
@dataclass(frozen=True)
```

Přínosy:

- brání nechtěným změnám
- usnadňuje uvažování o stavu
- činí testy předvídatelnějšími
- jasně reprezentuje faktická data

Příklady neměnných faktů:

```text
source filename
page number
document text
completed search score
```

---


<a id="cz-fáze-2a2---zpracování-textu"></a>

# FÁZE 2A.2 - Zpracování textu

**Odhad práce:** Méně než 1 hodina

Tyto moduly jsou malé a úzce souvisejí, proto je lze implementovat společně.

---

<a id="cz-soubor-1"></a>

## Soubor

```text
document_search/normalize.py
```

Hlavní funkce:

```python
normalize_text(
    text: str,
) -> str
```

Odpovědnosti:

- převod na malá písmena
- sjednocení whitespace
- obecné čištění textu

Nesmí obsahovat:

```text
OSPF terminology
Cisco rules
manual ranking boosts
domain-specific vocabulary
```

---

<a id="cz-soubor-2"></a>

## Soubor

```text
document_search/tokenize.py
```

Hlavní funkce:

```python
tokenize(
    text: str,
) -> list[str]
```

Příklad:

```text
"OSPF calculates interface cost."
```

se přibližně změní na:

```python
[
    "ospf",
    "calculates",
    "interface",
    "cost",
]
```

---

<a id="cz-důležité-koncepty-1"></a>

## Důležité koncepty

- čisté funkce
- deterministické předzpracování
- opakovaně použitelné zpracování textu
- oddělení normalizace a retrievalu

---


<a id="cz-fáze-2a3---základy-bezpečnosti"></a>

# FÁZE 2A.3 - Základy bezpečnosti

**Odhad práce:** Přibližně 1 hodina

<a id="cz-cíl-4"></a>

## Cíl

Chránit souborový systém a uživatelské vstupy vyhledávání ještě před parsováním PDF a řazením.

---

<a id="cz-soubor-3"></a>

## Soubor

```text
document_search/security/paths.py
```

Plánované funkce:

```python
resolve_safe_path(...)
validate_data_directory(...)
```

Odpovědnosti:

- hranice povolených adresářů
- zabránění path traversal
- validace vyhodnocených cest
- kontroly zohledňující symbolické odkazy

---

<a id="cz-nový-koncept---path-traversal"></a>

## Nový koncept - Path traversal

Příklad nebezpečného vstupu:

```text
../../private_file
```

Cesta, která zdánlivě vede dovnitř adresáře, může přes symbolický odkaz ve skutečnosti směřovat mimo něj.

Bezpečnost proto musí ověřovat vyhodnocené souborové cesty, nikoli pouze původní vstupní řetězec.

---

<a id="cz-soubor-4"></a>

## Soubor

```text
document_search/security/input_validation.py
```

Plánované funkce:

```python
validate_query(...)
validate_top_k(...)
```

Odpovědnosti:

- odmítat prázdné dotazy
- odmítat příliš dlouhé dotazy
- odmítat neplatné `top_k`
- bránit nepřiměřeným požadavkům na prostředky

---

<a id="cz-nový-koncept---validační-hranice"></a>

## Nový koncept - Validační hranice

Externí vstup se má validovat poblíž hranice systému.

Interní funkce pak mohou pracovat s hodnotami, které už splňují očekávaný kontrakt.

---


<a id="cz-fáze-2a4---načítání-pdf-a-validace-pdf"></a>

# FÁZE 2A.4 - Načítání PDF a validace PDF

**Odhad práce:** 1–2 hodiny

<a id="cz-soubor-5"></a>

## Soubor

```text
document_search/security/pdf_validation.py
```

Plánované funkce:

```python
validate_pdf_extension(...)
validate_pdf_signature(...)
validate_pdf_limits(...)
```

Odpovědnosti:

- ověřit příponu `.pdf`
- ověřit, že soubor skutečně vypadá jako PDF
- vynutit limit velikosti souboru
- vynutit limit počtu stránek

---

<a id="cz-nový-koncept---signatura-souboru"></a>

## Nový koncept - Signatura souboru

Název souboru jako:

```text
document.pdf
```

nedokazuje, že soubor skutečně je PDF.

Validace má vedle přípony kontrolovat i hlavičku nebo signaturu souboru.

---

<a id="cz-nový-koncept---vyčerpání-prostředků"></a>

## Nový koncept - Vyčerpání prostředků

I zdánlivě platný soubor může spotřebovat nepřiměřené prostředky.

Příklady:

```text
multi-gigabyte file
hundreds of thousands of pages
extremely large extracted text
```

Limity prostředků chrání:

- RAM
- CPU
- latenci
- dostupnost služby

---

<a id="cz-soubor-6"></a>

## Soubor

```text
document_search/load_pages.py
```

Hlavní funkce:

```python
load_pdf_pages(
    data_dir: Path,
) -> list[PageDocument]
```

Hlavní tok:

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

Důležité pravidlo:

Loader nesmí dokumenty potichu zkracovat.

Pokud nelze soubor zpracovat bezpečně nebo celý, musí být selhání výslovné.

---


<a id="cz-fáze-2a5---bm25-index"></a>

# FÁZE 2A.5 - BM25 index

**Odhad práce:** Méně než 1 hodina

<a id="cz-soubor-7"></a>

## Soubor

```text
document_search/build_index.py
```

Hlavní funkce:

```python
build_bm25_index(
    pages: list[PageDocument],
) -> BM25SearchIndex
```

Externí závislost:

```text
rank-bm25
```

---

<a id="cz-nový-koncept---bm25"></a>

## Nový koncept - BM25

BM25 je standardní lexikální algoritmus pro vyhledávání informací.

Zohledňuje:

- četnost termínu
- inverzní četnost dokumentů
- normalizaci podle délky dokumentu

Konceptuálně:

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

Je vhodnější než ručně napsané řazení typu:

```text
neighbor = +1
DROTHER = +5
distance below 200 chars = +3
```

protože řazení BM25 vychází ze statistik korpusu, nikoli z ručně zadaných doménových heuristik.

---


<a id="cz-fáze-2a6---vyhledávací-modul"></a>

# FÁZE 2A.6 - Vyhledávací modul

**Odhad práce:** Přibližně 1 hodina

<a id="cz-soubor-8"></a>

## Soubor

```text
document_search/search.py
```

Veřejná funkce:

```python
search_pages(
    index: BM25SearchIndex,
    query: str,
    top_k: int = 10,
) -> list[SearchResult]
```

Hlavní tok:

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

<a id="cz-důležitý-nový-koncept---hranice-veřejného-api"></a>

## Důležitý nový koncept - Hranice veřejného API

Ostatní moduly mají používat:

```python
search_pages(...)
```

aniž by ručně přistupovaly k:

```text
BM25 internals
page arrays
raw score arrays
sorting logic
```

Interní implementaci pak lze změnit bez změny každého volajícího.

---


<a id="cz-fáze-2a7---cli"></a>

# FÁZE 2A.7 - CLI

**Odhad práce:** Méně než 1 hodina

<a id="cz-soubor-9"></a>

## Soubor

```text
scripts/search_pdf.py
```

Plánované funkce:

```python
build_parser()
print_results()
select_result()
print_result_detail()
main()
```

Cílové použití:

```text
python -m scripts.search_pdf "how does OSPF calculate interface cost"
```

Volitelně:

```text
--top-k 5
```

CLI má obsahovat:

- parsování argumentů
- čitelný výstup pro člověka
- interaktivní výběr

Nemá obsahovat:

- implementaci BM25
- vnitřnosti parsování PDF
- heuristiky řazení

---


<a id="cz-fáze-2a8---integrace"></a>

# FÁZE 2A.8 - Integrace

<a id="cz-úkoly"></a>

## Úkoly

- přidat závislost `rank-bm25`
- spustit unit testy dokumentového vyhledávání
- spustit všechny projektové testy
- prohledat skutečný Cisco korpus
- ručně prohlédnout několik pořadí výsledků
- ověřit obecné chování
- potvrdit odstranění heuristik řazení specifických pro OSPF

---

<a id="cz-fáze-2a--podmínky-dokončení"></a>

## FÁZE 2A — Podmínky dokončení

- [ ] lze najít libovolná PDF
- [ ] hranice souborového systému jsou validované
- [ ] přípona PDF je validovaná
- [ ] signatura PDF je validovaná
- [ ] existují limity prostředků PDF
- [ ] stránky reprezentují typované datové modely
- [ ] normalizace je nezávislá na doméně
- [ ] tokenizace funguje
- [ ] lze vytvořit BM25 index
- [ ] lze řadit libovolné textové dotazy
- [ ] výsledky zpřístupňují zdroj, stránku, skóre a text
- [ ] CLI funguje
- [ ] příslušné unit testy procházejí
- [ ] všechny projektové testy procházejí
- [ ] neexistují heuristiky řazení specifické pro OSPF

Po splnění těchto podmínek je FÁZE 2A zmrazená.

Mimo rozsah:

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


<a id="cz-fáze-2b---evaluační-datové-modely"></a>

# FÁZE 2B - Evaluační datové modely

**Odhad práce:** 1–2 hodiny

<a id="cz-cíl-5"></a>

## Cíl

Přesunout opakovaně použitelnou evaluační logiku z volných skriptů a slovníků do typovaných projektových modulů.

Cílová struktura:

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

<a id="cz-soubor-10"></a>

## Soubor

```text
evaluation/models.py
```

Plánované modely:

```python
GoldEvidence
EvaluationQuestion
QuestionResult
EvaluationMetrics
EvaluationRun
```

---

<a id="cz-nový-koncept---typované-evaluační-modely"></a>

## Nový koncept - Typované evaluační modely

Namísto:

```python
question["gold_evidence"][0]["source"]
```

preferuj:

```python
question.gold_evidence
```

Přínosy:

- čitelnější kód
- lepší podporu IDE
- méně chyb v názvech klíčů
- jednodušší validaci
- bezpečnější refaktoring

---

<a id="cz-soubor-11"></a>

## Soubor

```text
evaluation/dataset.py
```

Plánované funkce:

```python
load_dataset(...)
validate_dataset(...)
calculate_dataset_hash(...)
```

Odpovědnosti:

- načítání datasetů DEV / TEST
- validace schématu
- identita datasetu
- reprodukovatelnost

---

<a id="cz-nový-koncept---hashování-datasetu"></a>

## Nový koncept - Hashování datasetu

SHA256 hash identifikuje přesnou verzi datasetu použitou v evaluačním běhu.

Odstraňuje nejednoznačnost tvrzení typu:

```text
"MRR was 0.82 on the DEV dataset"
```

pokud se DEV dataset od tohoto běhu změnil.

Namísto toho:

```text
dataset_hash = abc123...
MRR = 0.82
```

---

<a id="cz-soubor-12"></a>

## Soubor

```text
evaluation/evidence.py
```

Plánované funkce:

```python
normalize_evidence_text(...)
matches_gold_evidence(...)
find_gold_rank(...)
```

Platná shoda důkazu má vyžadovat:

```text
source
AND
page
AND
expected text fragment
```

v rámci jedné přijatelné varianty důkazu.

---


<a id="cz-fáze-2c---metriky-retrievalu"></a>

# FÁZE 2C - Metriky retrievalu

**Odhad práce:** Přibližně 1 hodina

<a id="cz-soubor-13"></a>

## Soubor

```text
evaluation/metrics.py
```

Plánované funkce:

```python
reciprocal_rank(...)
mean_reciprocal_rank(...)
hit_at_k(...)
aggregate_metrics(...)
```

---

<a id="cz-metrika---hitk"></a>

## Metrika - Hit@K

Otázka:

```text
Did the correct evidence appear in the first K results?
```

Příklady:

```text
Hit@1
Hit@3
Hit@5
Hit@8
```

---

<a id="cz-metrika---reciproční-pořadí"></a>

## Metrika - Reciproční pořadí

Pokud se správný důkaz objeví na:

```text
rank 1 -> 1.0
rank 2 -> 0.5
rank 4 -> 0.25
```

Konceptuální vzorec:

```text
1 / rank
```

---

<a id="cz-metrika---mrr"></a>

## Metrika - MRR

Průměrné reciproční pořadí:

```text
average reciprocal rank
across all evaluation questions
```

MRR odměňuje systémy, které umisťují relevantní důkazy poblíž začátku pořadí.

---


<a id="cz-fáze-2d---evaluační-runner-a-historie"></a>

# FÁZE 2D - Evaluační runner a historie

**Odhad práce:** Přibližně 1 hodina

<a id="cz-soubor-14"></a>

## Soubor

```text
evaluation/runner.py
```

Plánované funkce:

```python
evaluate_question(...)
evaluate_dataset(...)
build_run_metadata(...)
```

Konceptuální tok:

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

<a id="cz-soubor-15"></a>

## Soubor

```text
evaluation/history.py
```

Plánované funkce:

```python
load_history(...)
append_run(...)
save_history(...)
```

Ukládaná metadata mají zahrnovat:

- SHA Git commitu
- příznak necommitnutých změn
- SHA256 datasetu
- časové razítko
- konfiguraci
- evaluační metriky

Příklad:

```text
commit A
MRR = 0.71

commit B
MRR = 0.82
```

Změny retrievalu tak lze porovnávat podle důkazů.

---


<a id="cz-fáze-2e---evaluace-random"></a>

# FÁZE 2E - Evaluace RANDOM

**Odhad práce:** 2–3 hodiny

<a id="cz-soubor-16"></a>

## Soubor

```text
evaluation/random_eval.py
```

Možné funkce:

```python
sample_pages(...)
build_random_sample(...)
save_seed(...)
```

---

<a id="cz-nový-koncept---reprodukovatelná-náhodnost"></a>

## Nový koncept - Reprodukovatelná náhodnost

Použij samostatný generátor náhodných čísel se seedem.

Příklad:

```python
random.Random(seed)
```

Stejný seed má vytvořit stejný vzorek.

Neočekávané selhání RANDOM pak lze později zopakovat.

---

<a id="cz-účel-random"></a>

## Účel RANDOM

RANDOM je určen pro:

```text
robustness
coverage
failure discovery
```

Není určen pro:

```text
final generalization claims
```

To zůstává úlohou TEST.

---


<a id="cz-fáze-2f---kompletní-evaluační-dataset"></a>

# FÁZE 2F - Kompletní evaluační dataset

**Odhad práce:** Zahrnut v odhadu FÁZE 2

<a id="cz-úkoly-1"></a>

## Úkoly

- rozšířit DEV přibližně na 20 otázek
- ručně ověřit referenční důkazy
- rozšířit témata otázek
- implementovat workflow RANDOM
- vytvořit TEST dataset
- zmrazit TEST dataset
- zdokumentovat role datasetů

---

<a id="cz-fáze-2--podmínky-dokončení"></a>

## FÁZE 2 — Podmínky dokončení

- [ ] univerzální BM25 průzkumník dokumentů je dokončený
- [ ] DEV dataset je dostatečně široký
- [ ] referenční důkazy DEV jsou ručně ověřené
- [ ] workflow RANDOM je implementované
- [ ] běhy RANDOM jsou reprodukovatelné
- [ ] TEST dataset je vytvořený
- [ ] TEST dataset je zmrazený
- [ ] MRR je implementované
- [ ] Hit@1 je implementované
- [ ] Hit@3 je implementované
- [ ] Hit@5 je implementované
- [ ] Hit@8 je implementované
- [ ] hashování datasetu je implementované
- [ ] Git metadata se zaznamenávají
- [ ] historie evaluace je dostupná
- [ ] evaluační testy procházejí

Po FÁZI 2 se evaluační infrastruktura zmrazí, pokud se neobjeví konkrétní problém měření.

---


<a id="cz-fáze-3---refaktoring-retrievalu"></a>

# FÁZE 3 - Refaktoring retrievalu

**Stav:** Plánováno

**Odhad práce:** 8–14 hodin

<a id="cz-cíl-6"></a>

## Cíl

Hlavní RAG retrieval refactorovat až po vytvoření spolehlivé evaluace.

Současný velký modul:

```text
app/retrieval.py
```

Cílová struktura:

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


<a id="cz-fáze-31---retrieval-modely"></a>

# FÁZE 3.1 - Retrieval modely

<a id="cz-soubor-17"></a>

## Soubor

```text
app/retrieval/models.py
```

Plánované modely:

```python
RetrievedChunk
ScoredChunk
RetrievalResult
```

Účel:

nahradit volně strukturované slovníky a n-tice explicitními interními typy pro retrieval.

---


<a id="cz-fáze-32---embeddingy"></a>

# FÁZE 3.2 - Embeddingy

<a id="cz-soubor-18"></a>

## Soubor

```text
app/retrieval/embeddings.py
```

Plánované funkce:

```python
load_embedding_model(...)
embed_query(...)
embed_documents(...)
```

Odpovědnost:

pouze operace s embeddingy.

Nesmí:

- komunikovat s FastAPI
- rozhodovat o pořadí
- formátovat API odpovědi

---


<a id="cz-fáze-33---vektorové-vyhledávání"></a>

# FÁZE 3.3 - Vektorové vyhledávání

<a id="cz-soubor-19"></a>

## Soubor

```text
app/retrieval/vector_search.py
```

Plánované funkce:

```python
search_vector_store(...)
convert_chroma_results(...)
```

Odpovědnost:

komunikace s ChromaDB.

Důležité architektonické pravidlo:

Vyšší vrstvy nemají přímo záviset na struktuře odpovědí Chroma.

---


<a id="cz-fáze-34---zpracování-dotazu"></a>

# FÁZE 3.4 - Zpracování dotazu

<a id="cz-soubor-20"></a>

## Soubor

```text
app/retrieval/query.py
```

Možná funkce:

```python
normalize_query(...)
```

Budoucí rozšiřování dotazů je přípustné pouze při měřitelném přínosu prokázaném evaluací DEV.

Doménové podmínky pevně zakódované v retrievalu mají být odstraněny.

---


<a id="cz-fáze-35---reranker"></a>

# FÁZE 3.5 - Reranker

<a id="cz-soubor-21"></a>

## Soubor

```text
app/retrieval/reranker.py
```

Plánované funkce:

```python
load_reranker(...)
rerank(...)
```

Hlavní tok:

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


<a id="cz-fáze-36---skórování"></a>

# FÁZE 3.6 - Skórování

<a id="cz-soubor-22"></a>

## Soubor

```text
app/retrieval/scoring.py
```

Cíl:

odstranit nevhodné kombinace skóre.

Současný známý problém:

```text
raw CrossEncoder score
+
large heuristic bonus
```

může způsobit, že heuristická škála převáží relevanci modelu.

Možné přístupy k vyhodnocení:

- řazení pouze podle CrossEncoderu
- normalizovaná kombinace skóre
- slučování pořadí

Volba musí vycházet z metrik DEV.

---

<a id="cz-nový-koncept---slučování-pořadí"></a>

## Nový koncept - Slučování pořadí

Místo přímého sčítání neslučitelných hrubých skóre mohou systémy kombinovat relativní pozice v pořadí.

Tím se omezují některé problémy rozdílných škál skóre.

Zavést je lze pouze při odůvodnění evaluací.

---


<a id="cz-fáze-37---retrieval-služba"></a>

# FÁZE 3.7 - Retrieval služba

<a id="cz-soubor-23"></a>

## Soubor

```text
app/retrieval/service.py
```

Cílové veřejné API:

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

Vyšší vrstvy mají primárně volat toto veřejné rozhraní.

---

<a id="cz-fáze-3--podmínky-dokončení"></a>

## FÁZE 3 — Podmínky dokončení

- [ ] retrieval neobsahuje pevně zakódované OSPF podmínky
- [ ] existují retrieval datové modely
- [ ] práce s embeddingy je oddělená
- [ ] komunikace s Chroma je oddělená
- [ ] reranking je oddělený
- [ ] skórování je izolované
- [ ] existuje stabilní veřejné retrieval API
- [ ] baseline metriky jsou zaznamenané
- [ ] refactorovaný retrieval je vyhodnocený na DEV
- [ ] retrieval regresní testy procházejí
- [ ] TEST se nepoužívá při ladění
- [ ] po ladění proběhl závěrečný TEST běh

---


<a id="cz-fáze-4---zodolnění-api"></a>

# FÁZE 4 - Zodolnění API

**Stav:** Plánováno

**Odhad práce:** 5–8 hodin

<a id="cz-cíl-7"></a>

## Cíl

Přeměnit stávající FastAPI obálku na aplikační hranici bližší produkčnímu provozu.

Cílová struktura:

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


<a id="cz-fáze-41---životní-cyklus-aplikace"></a>

# FÁZE 4.1 - Životní cyklus aplikace

<a id="cz-soubor-24"></a>

## Soubor

```text
app/lifecycle.py
```

Hlavní funkce:

```python
lifespan(...)
```

Odpovědnosti:

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

<a id="cz-nový-koncept---fastapi-lifespan"></a>

## Nový koncept - FastAPI lifespan

Náročné modely se obvykle inicializují jednou při startu aplikace, ne zvlášť pro každý požadavek.

Přínosy:

- nižší latence
- menší paměťová režie
- jasnější životní cyklus prostředků
- jednodušší zjištění chyby při startu

---


<a id="cz-fáze-42---routy"></a>

# FÁZE 4.2 - Routy

<a id="cz-soubor-25"></a>

## Soubor

```text
app/api/routes.py
```

Odpovědnosti:

```text
GET /health
POST /ask
```

Routy převádějí:

```text
HTTP
<->
application services
```

Nemají obsahovat implementaci retrievalu.

---


<a id="cz-fáze-43---vkládání-závislostí"></a>

# FÁZE 4.3 - Vkládání závislostí

<a id="cz-soubor-26"></a>

## Soubor

```text
app/api/dependencies.py
```

Možné funkce:

```python
get_settings(...)
get_rag_service(...)
```

---

<a id="cz-nový-koncept---dependency-injection"></a>

## Nový koncept - Dependency injection

Místo vytváření závislostí v každém endpointu je může poskytnout FastAPI.

Přínosy:

- jednodušší testování
- méně globálního stavu
- zaměnitelné služby
- jasnější vlastnictví

---


<a id="cz-fáze-44---chyby"></a>

# FÁZE 4.4 - Chyby

<a id="cz-soubor-27"></a>

## Soubor

```text
app/api/errors.py
```

Možné výjimky:

```python
InvalidQueryError
RetrievalError
GenerationError
```

Dále:

```text
FastAPI exception handlers
```

Cíl:

převádět interní selhání na řízené strukturované HTTP odpovědi.

---


<a id="cz-fáze-45---middleware"></a>

# FÁZE 4.5 - Middleware

<a id="cz-soubor-28"></a>

## Soubor

```text
app/api/middleware.py
```

Možné odpovědnosti:

- ID požadavku
- měření času požadavku
- základní HTTP logování

---

<a id="cz-fáze-4--podmínky-dokončení"></a>

## FÁZE 4 — Podmínky dokončení

- [ ] modely se inicializují jednou
- [ ] životní cyklus aplikace je definovaný
- [ ] routy jsou oddělené od aplikační logiky
- [ ] dependency injection se používá tam, kde je vhodná
- [ ] existují strukturované aplikační chyby
- [ ] existují ID požadavků
- [ ] měření času API je dostupné
- [ ] health endpoint je definovaný
- [ ] význam readiness je definovaný
- [ ] integrační testy API procházejí

---


<a id="cz-fáze-5---produkční-inženýrství"></a>

# FÁZE 5 - Produkční inženýrství

**Stav:** Plánováno

**Odhad práce:** 10–16 hodin

<a id="cz-cíl-8"></a>

## Cíl

Zajistit reprodukovatelnost, pozorovatelnost, kontejnerizaci a nasaditelnost systému.

Fáze zahrnuje Python i infrastrukturu.

---


<a id="cz-fáze-51---linux--wsl2"></a>

# FÁZE 5.1 - Linux / WSL2

<a id="cz-cíl-9"></a>

## Cíl

Ověřit funkčnost aplikace mimo vývojové prostředí Windows.

Úkoly:

- vytvořit prostředí Linux/WSL2
- nainstalovat závislosti
- spustit unit testy
- spustit ingest
- spustit API
- ověřit předpoklady o souborovém systému
- ověřit načítání modelů

---

<a id="cz-nový-koncept---přenositelnost-prostředí"></a>

## Nový koncept - Přenositelnost prostředí

Systém funkční pouze v jediném lokálním prostředí ještě není reprodukovatelný.

Kompatibilita s Linuxem připravuje projekt také pro Docker a cloudové nasazení.

---


<a id="cz-fáze-52---strukturované-logování"></a>

# FÁZE 5.2 - Strukturované logování

Cílová struktura:

```text
app/
+-- observability/
    +-- __init__.py
    +-- logging.py
    +-- metrics.py
    +-- middleware.py
```

---

<a id="cz-soubor-29"></a>

## Soubor

```text
app/observability/logging.py
```

Plánované funkce:

```python
configure_logging(...)
get_logger(...)
```

---

<a id="cz-nový-koncept---strukturované-logování"></a>

## Nový koncept - Strukturované logování

Namísto pouhého:

```text
"Retrieval finished"
```

může strukturovaná událost obsahovat:

```text
event = retrieval_complete
request_id = ...
latency_ms = 143
candidate_count = 30
```

Strukturované logy se snáze:

- prohledávají
- agregují
- monitorují
- automaticky analyzují

---


<a id="cz-fáze-53---běhové-metriky"></a>

# FÁZE 5.3 - Běhové metriky

<a id="cz-soubor-30"></a>

## Soubor

```text
app/observability/metrics.py
```

Možné funkce:

```python
record_request(...)
record_latency(...)
record_retrieval_latency(...)
record_generation_latency(...)
record_error(...)
```

Provozní metriky mají zahrnovat:

- počet požadavků
- počet chyb
- latenci odpovědi
- latenci retrievalu
- latenci rerankingu
- latenci generování

Později tam, kde je to relevantní:

- spotřebu tokenů
- využití modelu
- cenu API

---

<a id="cz-nový-koncept---kvalitativní-a-provozní-metriky"></a>

## Nový koncept - Kvalitativní a provozní metriky

Metriky kvality:

```text
MRR
Hit@K
answer groundedness
```

Provozní metriky:

```text
latency
request count
error rate
resource usage
cost
```

Systém může dosahovat vysoké kvality retrievalu, ale nevyhovující produkční latence.

Důležité jsou oba rozměry.

---


<a id="cz-fáze-54---zodolnění-dockeru"></a>

# FÁZE 5.4 - Zodolnění Dockeru

Soubory:

```text
Dockerfile
compose.yaml
.dockerignore
```

Úkoly:

- reprodukovatelný build
- správná instalace závislostí
- explicitní konfigurace
- healthcheck
- uživatel bez oprávnění root
- omezení zbytečného obsahu obrazu

---

<a id="cz-nový-koncept---vícestupňový-docker-build"></a>

## Nový koncept - Vícestupňový Docker build

Build fáze může obsahovat nástroje potřebné jen pro sestavení závislostí.

Výsledný běhový obraz může obsahovat pouze to, co je nutné pro spuštění aplikace.

Možné přínosy:

- menší obraz
- menší útočná plocha
- čistší běhové prostředí

Použij pouze tehdy, přinese-li to projektu praktickou hodnotu.

---


<a id="cz-fáze-55---cicd"></a>

# FÁZE 5.5 - CI/CD

Současné CI už spouští projektové testy.

Budoucí tok může být:

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

Možná zlepšení:

- kontrola formátování
- Ruff
- typová kontrola
- coverage
- audit závislostí

---

<a id="cz-fáze-5--podmínky-dokončení"></a>

## FÁZE 5 — Podmínky dokončení

- [ ] aplikace funguje pod Linuxem / WSL2
- [ ] Docker build je reprodukovatelný
- [ ] kontejner úspěšně startuje
- [ ] healthcheck kontejneru funguje
- [ ] běh bez root oprávnění je nastavený
- [ ] CI spouští projektové testy
- [ ] existuje strukturované logování
- [ ] lze měřit latenci požadavku
- [ ] lze měřit latenci retrievalu
- [ ] lze měřit latenci generování
- [ ] postup nasazení je definovaný

---


<a id="cz-fáze-6---bezpečnost"></a>

# FÁZE 6 - Bezpečnost

**Stav:** Plánováno

**Odhad práce:** 6–10 hodin

<a id="cz-cíl-10"></a>

## Cíl

Provést samostatnou důkladnou bezpečnostní revizi po vytvoření produkční architektury.

Bezpečnost se řeší i v předchozích fázích; FÁZE 6 provádí hlubší kontrolu.

Cílová struktura může obsahovat:

```text
app/
+-- security/
    +-- __init__.py
    +-- validation.py
    +-- limits.py
    +-- headers.py
```

---


<a id="cz-fáze-61---modelování-hrozeb"></a>

# FÁZE 6.1 - Modelování hrozeb

<a id="cz-nový-koncept---model-hrozeb"></a>

## Nový koncept - Model hrozeb

Výslovně určit:

```text
assets
trust boundaries
attack surfaces
possible attackers
failure modes
impact
mitigations
```

Příklady systémových hranic:

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


<a id="cz-fáze-62---validace-běhových-vstupů"></a>

# FÁZE 6.2 - Validace běhových vstupů

<a id="cz-soubor-31"></a>

## Soubor

```text
app/security/validation.py
```

Možné funkce:

```python
validate_query(...)
validate_input_size(...)
```

---


<a id="cz-fáze-63---běhové-limity"></a>

# FÁZE 6.3 - Běhové limity

<a id="cz-soubor-32"></a>

## Soubor

```text
app/security/limits.py
```

Možné limity:

```text
maximum query length
maximum context size
maximum top_k
maximum request size
```

Zde lze posoudit případné budoucí omezení frekvence požadavků.

---


<a id="cz-fáze-64---tajemství"></a>

# FÁZE 6.4 - Tajemství

Úkoly:

- ověřit, že Git neobsahuje tajemství
- používat proměnné prostředí
- definovat produkční strategii pro tajemství
- zkontrolovat `.env.example`
- nelogovat tajemství

---


<a id="cz-fáze-65---bezpečnost-závislostí"></a>

# FÁZE 6.5 - Bezpečnost závislostí

Možné úkoly:

- skenování zranitelností
- revize závislostí
- strategie pinování verzí
- proces bezpečnostních aktualizací

---


<a id="cz-fáze-66---bezpečnost-kontejneru"></a>

# FÁZE 6.6 - Bezpečnost kontejneru

Zkontrolovat:

- běh bez root oprávnění
- souborová oprávnění
- zveřejněné porty
- zbytečné balíčky
- zapisovatelné adresáře
- předávání tajemství
- útočnou plochu

---


<a id="cz-fáze-67---bezpečnost-http"></a>

# FÁZE 6.7 - Bezpečnost HTTP

Zkontrolovat:

- CORS
- bezpečnostní hlavičky
- limity požadavků
- únik informací v chybách
- požadavky na autentizaci, bude-li zavedena

---


<a id="cz-fáze-68---bezpečnost-specifická-pro-rag"></a>

# FÁZE 6.8 - Bezpečnost specifická pro RAG

<a id="cz-nový-koncept---nepřímá-prompt-injection"></a>

## Nový koncept - Nepřímá prompt injection

Vyhledaný dokument může obsahovat text jako:

```text
Ignore previous instructions...
```

Samotný dokument se stává nedůvěryhodným vstupem modelu.

Bezpečnostní revize má zvážit:

- oddělení instrukcí a vyhledaných dat
- sestavování promptu
- důvěryhodnost zdrojů
- chování modelu
- přístup k nástrojům v budoucích agentních systémech

---

<a id="cz-fáze-6--podmínky-dokončení"></a>

## FÁZE 6 — Podmínky dokončení

- [ ] model hrozeb je zdokumentovaný
- [ ] vstupní limity jsou zkontrolované
- [ ] hranice souborového systému jsou zkontrolované
- [ ] zpracování PDF je zkontrolované
- [ ] bezpečnost závislostí je zkontrolovaná
- [ ] správa tajemství je zkontrolovaná
- [ ] oprávnění kontejneru jsou zkontrolovaná
- [ ] běh bez root oprávnění je ověřený
- [ ] HTTP kontroly jsou zkontrolované
- [ ] nepřímá prompt injection je zkontrolovaná
- [ ] hlavní opatření jsou zdokumentovaná

---


<a id="cz-fáze-7---produkční-verze-v1"></a>

# FÁZE 7 - Produkční verze v1

**Stav:** Plánováno

**Odhad práce:** 4–6 hodin

<a id="cz-cíl-11"></a>

## Cíl

Propojit dokončené vrstvy do první verze připomínající produkční vydání.

Produkční v1 neznamená úplnost podnikového řešení.

Znamená, že projekt je:

```text
reproducible
tested
deployable
observable
documented
reasonably hardened
```

---


<a id="cz-fáze-71---health-a-readiness"></a>

# FÁZE 7.1 - Health a readiness

Možný soubor:

```text
app/health.py
```

Možné funkce:

```python
check_vector_store(...)
check_models(...)
build_readiness_status(...)
```

---

<a id="cz-nový-koncept---liveness-a-readiness"></a>

## Nový koncept - Liveness a readiness

<a id="cz-liveness--běh-procesu"></a>

### Liveness — běh procesu

Otázka:

```text
Is the process alive?
```

<a id="cz-readiness--připravenost-služby"></a>

### Readiness — připravenost služby

Otázka:

```text
Can the application actually serve a valid RAG request?
```

Aplikace může běžet, ale její model nebo vektorové úložiště nemusí být připravené.

---


<a id="cz-fáze-72---produkční-smoke-test"></a>

# FÁZE 7.2 - Produkční smoke test

<a id="cz-soubor-33"></a>

## Soubor

```text
scripts/production_smoke.py
```

Možný tok:

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


<a id="cz-fáze-73---dokumentace"></a>

# FÁZE 7.3 - Dokumentace

README má vysvětlovat:

- účel projektu
- shrnutí architektury
- instalaci
- přípravu prostředí
- ingest
- spuštění API
- spuštění testů
- použití Dockeru
- použití evaluace
- bezpečnostní hlediska

Odkazy:

```text
docs/ROADMAP.md
docs/ARCHITECTURE.md
docs/DEVELOPMENT_GUIDE.md
```

---

<a id="cz-fáze-7--podmínky-dokončení"></a>

## FÁZE 7 — Podmínky dokončení

V čistém prostředí lze:

- [ ] naklonovat repozitář
- [ ] nakonfigurovat proměnné prostředí
- [ ] nainstalovat nebo sestavit závislosti
- [ ] spustit aplikaci
- [ ] ingestovat korpus
- [ ] poslat dotaz do API
- [ ] získat podloženou odpověď se zdroji
- [ ] spustit testy
- [ ] spustit evaluaci
- [ ] vytvořit strukturované logy
- [ ] zpřístupnit běhové metriky
- [ ] postupovat podle zdokumentované instalace

V tomto bodě projekt dosahuje:

```text
Production v1
```

---


<a id="cz-fáze-8---rozšíření"></a>

# FÁZE 8 - Rozšíření

FÁZE 8 začíná až po produkční v1.

Účelem je rozšířit dovednosti a schopnosti systému bez destabilizace hlavního RAG projektu.

---


<a id="cz-fáze-8a---průzkum-agentů"></a>

# FÁZE 8A - Průzkum agentů

**Odhad práce:** 4–6 hodin

<a id="cz-cíl-12"></a>

## Cíl

Ukázat přechod z běžné RAG aplikace na agentní workflow.

První agent má používat existující RAG systém jako nástroj.

Cílová struktura:

```text
agent/
|
+-- __init__.py
+-- models.py
+-- tools.py
+-- agent.py
```

---

<a id="cz-soubor-34"></a>

## Soubor

```text
agent/tools.py
```

Příklad funkce:

```python
search_knowledge_base(
    question: str,
)
```

Možná implementace:

```text
agent
    ->
FastAPI /ask
```

nebo:

```text
agent
    ->
RAG service
```

---

<a id="cz-nový-koncept---volání-nástrojů"></a>

## Nový koncept - Volání nástrojů

Jazykový model už pouze negeneruje text.

Může rozhodnout:

```text
which tool to use
which arguments to provide
how to use the tool result
```

Příklad toku:

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

<a id="cz-fáze-8a--podmínky-dokončení"></a>

## FÁZE 8A — Podmínky dokončení

- [ ] existuje jeden agent
- [ ] agent umí zavolat existující RAG systém
- [ ] argumenty nástroje jsou strukturované
- [ ] výsledek nástroje se vrací modelu
- [ ] chování agenta je testovatelné
- [ ] rozsah zůstává záměrně malý

---


<a id="cz-fáze-8b---sql-a-etl"></a>

# FÁZE 8B - SQL a ETL

**Odhad práce:** 6–10 hodin

<a id="cz-cíl-13"></a>

## Cíl

Po dokončení produkčního RAG systému doplnit praktické základy datového inženýrství.

Cílová struktura:

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

<a id="cz-soubor-35"></a>

## Soubor

```text
data_pipeline/database.py
```

Koncepty:

```text
database connections
SELECT
JOIN
GROUP BY
indexes
transactions
```

---

<a id="cz-soubor-36"></a>

## Soubor

```text
data_pipeline/extract.py
```

Možná funkce:

```python
extract_from_source(...)
```

---

<a id="cz-soubor-37"></a>

## Soubor

```text
data_pipeline/transform.py
```

Možné funkce:

```python
clean_records(...)
transform_records(...)
validate_records(...)
```

---

<a id="cz-soubor-38"></a>

## Soubor

```text
data_pipeline/load.py
```

Možná funkce:

```python
load_to_database(...)
```

---

<a id="cz-nový-koncept---etl"></a>

## Nový koncept - ETL

ETL znamená:

```text
Extract
    ->
Transform
    ->
Load
```

Jde o běžný vzor pipeline v datovém inženýrství.

---

<a id="cz-fáze-8b--podmínky-dokončení"></a>

## FÁZE 8B — Podmínky dokončení

- [ ] základní SQL workflow je implementované
- [ ] data lze extrahovat
- [ ] data lze transformovat
- [ ] existuje validace
- [ ] transformovaná data lze načíst do cíle
- [ ] jednoduchá ETL pipeline funguje od začátku do konce

---


<a id="cz-fáze-8c---mlops"></a>

# FÁZE 8C - MLOps

**Odhad práce:** 8–12 hodin

<a id="cz-cíl-14"></a>

## Cíl

Zavést systematické sledování experimentů a modelů.

Možná struktura:

```text
mlops/
|
+-- __init__.py
+-- experiment.py
+-- artifacts.py
+-- model_metadata.py
```

---

<a id="cz-soubor-39"></a>

## Soubor

```text
mlops/experiment.py
```

Záznamy experimentů mají obsahovat:

- model
- parametry modelu
- konfiguraci retrievalu
- hash datasetu
- Git commit
- časové razítko
- metriky kvality
- provozní metriky
- metriky nákladů tam, kde jsou relevantní

---

<a id="cz-nový-koncept---sledování-experimentů"></a>

## Nový koncept - Sledování experimentů

Namísto:

```text
"This version seemed better."
```

ukládat:

```text
commit = abc123
dataset_hash = xyz456
embedding_model = ...
reranker = ...
MRR = 0.84
Hit@3 = 0.93
latency = 190 ms
```

Možná budoucí technologie:

```text
MLflow
```

Nejprve lze implementovat jednodušší lokální sledování experimentů.

---

<a id="cz-soubor-40"></a>

## Soubor

```text
mlops/artifacts.py
```

Možné odpovědnosti:

- evaluační artefakty
- metadata modelů
- snímky konfigurace
- výstupy běhů

---

<a id="cz-fáze-8c--podmínky-dokončení"></a>

## FÁZE 8C — Podmínky dokončení

- [ ] experimenty mají jedinečnou identitu
- [ ] verze datasetu se zaznamenává
- [ ] Git commit se zaznamenává
- [ ] konfigurace modelu se zaznamenává
- [ ] metriky kvality se zaznamenávají
- [ ] provozní metriky se zaznamenávají
- [ ] běhy lze porovnávat

---


<a id="cz-fáze-8d---pokročilí-agenti"></a>

# FÁZE 8D - Pokročilí agenti

**Stav:** Budoucí

Podrobná architektura je záměrně odložena.

Možná témata:

- více nástrojů
- trvalý stav
- plánování
- grafy workflow
- lidské schvalování
- evaluace agentů
- koordinace více agentů

Technologie vybírej až po pochopení jednoduššího agentního workflow.

Tuto fázi nenavrhuj předčasně.

---


<a id="cz-původní-plánovací-odhady--historické"></a>

# Původní plánovací odhady — historické

Hodnoty jsou zachované z původního plánu. Nejde o aktuální předpověď zbývající práce ani termínový závazek; nové posouzení vyžaduje samostatné plánovací rozhodnutí.

Původní odhady aktivního vývoje (nepřepočítané):

| Fáze | Odhad času |
|---|---:|
| Dokončení FÁZE 1 | 2-4 h |
| FÁZE 2 — základ evaluace | 8-12 h |
| FÁZE 3 — refaktoring retrievalu | 8-14 h |
| FÁZE 4 — zodolnění API | 5-8 h |
| FÁZE 5 — produkční inženýrství | 10-16 h |
| FÁZE 6 — bezpečnost | 6-10 h |
| FÁZE 7 — produkční v1 | 4-6 h |
| FÁZE 8A — průzkum agentů | 4-6 h |
| FÁZE 8B — SQL / ETL | 6-10 h |
| FÁZE 8C — MLOps | 8-12 h |

Původní odhad zbývající práce do produkční v1:

```text
43-70 hours
```

Tyto odhady zahrnují:

- implementaci
- vysvětlení
- ruční zápis kódu
- testování
- ladění
- integraci

Nejde o odhady samotného psaní kódu.

---


<a id="cz-historie-plánování"></a>

## Historie plánování

Předchozí stav FÁZE 2A a podrobný seznam nejbližších úkolů zůstávají v [roadmapě před zkrácením](https://github.com/jyenten/local_rag_api/blob/d7c3b4f71711c798646bd0a878b96b9c46c92d93/rag_api_project/docs/ROADMAP.md#historical-project-status-original-phase-2a-plan). Popisují starší bod, nikoli dnešní další kroky. Dokončená práce je v [LEARNING_LOG.md](LEARNING_LOG.md#cz); aktuální zaměření patří pouze do [aktuálního zaměření vývoje](#cz-aktuální-zaměření-vývoje) této roadmapy.

[↑ Nahoru](#top)
