<a id="top"></a>

# AI inženýrství — deník učení

[Česky](#cz) · [English](../en/LEARNING_LOG.md#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Obsah — kliknutím rozbalit</summary>

- [Cíl](#cz-cíl)
- [Úrovně dovedností](#cz-úrovně-dovedností)
- [Ověřený stav projektu](#cz-ověřený-stav-projektu)
- [Historický stav projektu — 2026-10-12](#cz-historický-stav-projektu--2026-10-12)
- [Historický učební plán: fáze 3.3 — BM25 (2026-10-12)](#cz-historický-učební-plán-fáze-33--bm25-2026-10-12)
- [Šablona záznamu učení](#cz-šablona-záznamu-učení)
- [YYYY-MM-DD — téma](#cz-yyyy-mm-dd--téma)
- [Pravidla záznamů učení](#cz-pravidla-záznamů-učení)
- [Historie projektu a učení](#cz-historie-projektu-a-učení)
- [2026-05-12 až 2026-05-22 — Python, analýza dat a klasické ML](#cz-2026-05-12-až-2026-05-22--python-analýza-dat-a-klasické-ml)
- [2026-05-23 až 2026-06-09 — PyTorch, NLP, počáteční RAG a kontejnery](#cz-2026-05-23-až-2026-06-09--pytorch-nlp-počáteční-rag-a-kontejnery)
- [2026-07-27 až 2026-08-21 — Základ RAG API, diagnostika a CI](#cz-2026-07-27-až-2026-08-21--základ-rag-api-diagnostika-a-ci)
- [2026-09-01 až 2026-09-16 — Diagnostika retrievalu a základ evaluace](#cz-2026-09-01-až-2026-09-16--diagnostika-retrievalu-a-základ-evaluace)
- [2026-09-16 až 2026-09-17 — Nezávislý průzkumník PDF stránek](#cz-2026-09-16-až-2026-09-17--nezávislý-průzkumník-pdf-stránek)
- [2026-09-22 až 2026-10-08 — Párování evidence a řízená evaluace](#cz-2026-09-22-až-2026-10-08--párování-evidence-a-řízená-evaluace)
- [2026-10-11 až 2026-10-12 — Vektorový baseline, latence a pravidla agentů](#cz-2026-10-11-až-2026-10-12--vektorový-baseline-latence-a-pravidla-agentů)
- [2026-10-13 — Fáze 3.3: BM25 Retriever](#cz-2026-10-13--fáze-33-bm25-retriever)
- [2026-10-14 — Historie portfolia, původ práce agentů a bezpečnostní automatizace](#cz-2026-10-14--historie-portfolia-původ-práce-agentů-a-bezpečnostní-automatizace)
- [2026-10-15 až 2026-10-17 — Návrh reprodukovatelných Linux závislostí](#cz-2026-10-15-až-2026-10-17--návrh-reprodukovatelných-linux-závislostí)
- [2026-10-20 — Fáze 3.4: Evaluace retrievalu](#cz-2026-10-20--fáze-34-evaluace-retrievalu)
- [2026-10-26 — Experiment úložiště dokumentů a ověřeného FAISS balíčku](#cz-2026-10-26--experiment-úložiště-dokumentů-a-ověřeného-faiss-balíčku)
- [2026-10-26 — Automatizovaný návrh závislosti GitHub Actions](#cz-2026-10-26--automatizovaný-návrh-závislosti-github-actions)
- [2026-10-28 — Dvojjazyčné návody, regrese validátoru a výchozí main](#cz-2026-10-28--dvojjazyčné-návody-regrese-validátoru-a-výchozí-main)
- [2026-10-28 — Odpovědnosti dokumentace a česká navigace](#cz-2026-10-28--odpovědnosti-dokumentace-a-česká-navigace)
- [2026-10-28 — Oddělené jazyky dokumentace](#cz-oddělené-jazyky-dokumentace)
- [2026-10-28 — Centralizovaná dokumentace a jednodušší navigace](#cz-centralizovaná-dokumentace)
- [Necommitnutá práce pozorovaná 28. 10. 2026](#cz-necommitnutá-práce-pozorovaná-28-10-2026)
- [Pokrytí auditu větví — 2026-10-28](#cz-pokrytí-auditu-větví--2026-10-28)

- [2026-10-29 — Dokumentace portfolia a kontext lokálního provozu](#cz-2026-10-29-portfolio-dokumentace)

</details>

---

<a id="cz"></a>

<a id="cz-cíl"></a>

## Cíl

Rozvíjet samostatnou zdatnost v:

- programování v Pythonu
- softwarové architektuře a testování
- Gitu, CI/CD a Dockeru
- RAG systémech a vyhledávání informací
- evaluaci AI a observabilitě
- AI agentech a vývoji s jejich pomocí


<a id="cz-úrovně-dovedností"></a>

## Úrovně dovedností

- NOT ASSESSED — dosud bez samostatného prokázání
- GUIDED — dokončeno s vysvětlováním nebo pomocí
- INDEPENDENT — implementováno a vysvětleno bez pomoci
- PROFICIENT — samostatně použito na jiném problému

Dokončená funkce projektu automaticky neznamená zvládnutí příslušné dovednosti.


<a id="cz-ověřený-stav-projektu"></a>

## Ověřený stav projektu

Datum: 2026-10-29
Výchozí větev: main
Zkontrolovaný commit projektu: 82d5889 (před touto aktualizací deníku)

- PR #6 až #8 jsou sloučené: evidence portfolia, název Local RAG API a kanonické odkazy `jyenten/local_rag_api` jsou začleněné. Aktualizace `setup-python` z PR #2 je také sloučená; oddělený návrh lockfilu tím začleněný není.
- Poslední ověřené GitHub CI na `main`: **223 úspěšných testů za 7,29 s** ([běh 40865587005](https://github.com/jyenten/local_rag_api/actions/runs/40865587005)).
- Gitleaks a CodeQL na této revizi prošly. Dependency Audit nadále selhává se stejnou známou sadou nálezů ChromaDB; zůstává zapnutý bez výjimky.
- Baseline BM25 a Vector na DEV/RANDOM zůstávají zachované. Při aktualizaci tohoto deníku nebyly znovu měřeny; oddělený TEST zůstává beze změny.
- Hybridní RRF a práce na rozhraní ID retrieverů zůstávají lokální a necommitnuté.
- Návrh Linux lock souboru (PR #1) zůstává otevřený; lokální experiment FAISS/úložiště je také oddělený od integrovaného stavu `main`.

Dokončení projektu a hodnocení lidských dovedností zůstávají oddělené. Níže uvedená existující hodnocení GUIDED jsou zachována; tato revize historie nepřiděluje nové INDEPENDENT ani PROFICIENT.


<a id="cz-historický-stav-projektu--2026-10-12"></a>

## Historický stav projektu — 2026-10-12

Datum: 2026-10-12
Větev: document-search-bm25
Commit: 9ed9985

V projektu dokončeno:

- základ FastAPI RAG
- zpracování PDF a vektorové úložiště Chroma
- baseline vektorového retrievalu
- evaluační datasety a metriky retrievalu
- oddělení DEV / RANDOM / závěrečného TEST
- měření latence retrievalu
- JSONL historie evaluace
- kontroly Git původu
- automatizované testování a GitHub CI

Poslední ověřená úplná testovací sada: 142 úspěšných testů, 1 přeskočený.

Jde o dosažené výsledky projektu, nikoli o hodnocení samostatných dovedností.


<a id="cz-historický-učební-plán-fáze-33--bm25-2026-10-12"></a>

## Historický učební plán: fáze 3.3 — BM25 (2026-10-12)

Téma: Lexikální retrieval nad existujícími Chroma chunky.

Cíle učení:

- Vysvětlit řazení dokumentů v BM25.
- Rozumět tokenizaci, TF, IDF a délce dokumentu.
- Implementovat řazení retrievalu v Pythonu.
- Zachovat metadata zdroje a stránky.
- Psát smysluplné jednotkové a integrační testy.
- Porovnat BM25 s vektorovým retrievalem.

Samostatné cvičení:

Implementovat BM25Retriever.search() a vysvětlit řazení i rozhodování při shodě skóre.

Dosavadní hodnocení dovednosti: NOT ASSESSED


<a id="cz-šablona-záznamu-učení"></a>

## Šablona záznamu učení


<a id="cz-yyyy-mm-dd--téma"></a>

### YYYY-MM-DD — téma

Na čem jsem pracoval:

- doplnit

Co jsem se naučil:

- doplnit

Co jsem implementoval samostatně:

- doplnit

Co implementoval Codex nebo ChatGPT:

- doplnit

Jaké problémy jsem diagnostikoval:

- doplnit

Testy a důkazy:

- doplnit

Úroveň dovednosti: NOT ASSESSED / GUIDED / INDEPENDENT / PROFICIENT

Další cvičení:

- doplnit


<a id="cz-pravidla-záznamů-učení"></a>

## Pravidla záznamů učení

Deník aktualizuj po významných milnících, nikoli po každé malé změně kódu.

Zaznamenávej obtíže a neporozumění. Nenadhodnocuj dovednosti. Ke slabým tématům se vracej samostatnými cvičeními.


<a id="cz-historie-projektu-a-učení"></a>

## Historie projektu a učení

Retrospektivní záznamy přidané 28. 10. 2026 jsou rekonstruované z historie commitů, vybraných změn zdrojů/testů, stavu PR a lokálních worktrees. Data označují zaznamenané commity, nikoli ověřenou dobu studia. Uvedené pojmy se v práci vyskytují; samotné Git autorství neprokazuje samostatnou lidskou implementaci, porozumění ani rozsah AI pomoci. Autorství uvádíme pouze tam, kde je dokládá existující deník nebo pozorovaná spolupráce. Historické skripty a experimentální testy při auditu deníku nebyly znovu spouštěny.


<a id="cz-2026-05-12-až-2026-05-22--python-analýza-dat-a-klasické-ml"></a>

### 2026-05-12 až 2026-05-22 — Python, analýza dat a klasické ML

**Doklady projektu:** Cvičení původně zaznamenaná v historii nyní uchované větví `master`, následně převzatá do `main` a přesunutá pod `archive/`.

- Vstup v Pythonu, podmínky, cykly, funkce a kolekce; později analýza CSV v Pandas, filtrování/seskupování, chybějící hodnoty a grafy Matplotlib.
- Lineární regrese, klasifikace, křížová validace/přeučení, RandomForest, tvorba příznaků a úplné ML cvičení.
- Pojmy k upevnění: oddělení train/test, reprodukovatelné rozdělení, předzpracování a interpretace metrik místo pouhého fitování modelu.
- Důkazy: [počáteční dny 1–4, 8daf3fa](https://github.com/jyenten/local_rag_api/commit/8daf3fa), [Pandas, 909b475](https://github.com/jyenten/local_rag_api/commit/909b475), [úplné ML cvičení, 1c852a6](https://github.com/jyenten/local_rag_api/commit/1c852a6).


<a id="cz-2026-05-23-až-2026-06-09--pytorch-nlp-počáteční-rag-a-kontejnery"></a>

### 2026-05-23 až 2026-06-09 — PyTorch, NLP, počáteční RAG a kontejnery

**Doklady projektu:** Archivovaná učební cvičení, již zahrnutá v `main`.

- Sítě PyTorch, CNN/klasifikace obrázků, transfer learning a ResNet18.
- Klasifikace sentimentu v NLP, embeddingy, BERT/tokenizéry, attention a experimenty Hugging Face pipeline/QA.
- Počáteční RAG experimenty následované cvičeními aplikací FastAPI a Docker.
- Pojmy k upevnění: rozhraní tensor/model, tokenizace, retrieval oproti generování, kompatibilita balíčků a hranice běhu kontejnerů.
- Důkazy: [PyTorch, 1c05b12](https://github.com/jyenten/local_rag_api/commit/1c05b12), [BERT, 4097483](https://github.com/jyenten/local_rag_api/commit/4097483), [Hugging Face QA, 1441c8a](https://github.com/jyenten/local_rag_api/commit/1441c8a), [Docker/RAG API, f57517e](https://github.com/jyenten/local_rag_api/commit/f57517e).


<a id="cz-2026-07-27-až-2026-08-21--základ-rag-api-diagnostika-a-ci"></a>

### 2026-07-27 až 2026-08-21 — Základ RAG API, diagnostika a CI

**Milník projektu:** Historický základ `master`; zahrnutý v `main`.

- Lepší čištění/chunkování PDF, získaný kontext a přiřazení zdrojů k vybranému kontextu; metadata zdrojů přidaná do API odpovědí.
- Endpointy health/stats/readiness, validace prázdných otázek a ošetření nedostupnosti RAG služeb; Docker a Compose konfigurace.
- Kontroly API, testovací Chroma, smoke testy a GitHub Actions CI.
- Zahrnuté pojmy: připravenost služby oproti životnosti, dohledatelné odpovědi, typované hranice API, izolace testů a opakovatelné vývojové kontroly.
- Důkazy: [metadata zdrojů, 581d6f6](https://github.com/jyenten/local_rag_api/commit/581d6f6), [readiness, 6950495](https://github.com/jyenten/local_rag_api/commit/6950495), [CI/smoke testy, 702c0ab](https://github.com/jyenten/local_rag_api/commit/702c0ab), [vrchol `master`, 3c0bfdd](https://github.com/jyenten/local_rag_api/commit/3c0bfdd).


<a id="cz-2026-09-01-až-2026-09-16--diagnostika-retrievalu-a-základ-evaluace"></a>

### 2026-09-01 až 2026-09-16 — Diagnostika retrievalu a základ evaluace

**Milník projektu:** Zahrnutý v `main`; `retrieval-eval-refactor` uchovává raný stav tohoto vývoje, nikoli konečnou implementaci evaluace.

- Diagnostika retrievalu, upravené předzpracování/chunkování s regresními testy, počáteční DEV evaluace a nástroje historie evaluace.
- Zaznamenaná architektura, roadmapa a vývojová pravidla.
- Zahrnuté pojmy: diagnostika retrievalu odděleně od generování, hranice/překryv chunků, evaluace podložená evidencí a ohraničený rozsah vývoje.
- Důkazy: [regrese chunkování, 26b39e6](https://github.com/jyenten/local_rag_api/commit/26b39e6), [počáteční evaluace, 2fafcae](https://github.com/jyenten/local_rag_api/commit/2fafcae), [vrchol `retrieval-eval-refactor`, 010d8d1](https://github.com/jyenten/local_rag_api/commit/010d8d1).


<a id="cz-2026-09-16-až-2026-09-17--nezávislý-průzkumník-pdf-stránek"></a>

### 2026-09-16 až 2026-09-17 — Nezávislý průzkumník PDF stránek

**Milník projektu:** Implementovaný a zahrnutý v `main`.

- Modely stránek/vyhledávání, normalizace/tokenizace, načítání PDF, validace cest/PDF/vstupů, BM25 indexování/vyhledávání a interaktivní CLI.
- Syntetické testy, vývojové kontroly a automatické sledování změn pro testy.
- Zahrnuté pojmy: neměnné modely, identita zdroje/stránky, limity prostředků, lexikální řazení a oddělení stránkového průzkumu od chunkového retrievalu.
- Důkazy: [bezpečné načítání PDF, f05e080](https://github.com/jyenten/local_rag_api/commit/f05e080), [BM25 vyhledávání, 4a0fa06](https://github.com/jyenten/local_rag_api/commit/4a0fa06), [CLI průzkumníku stránek, 1f3fad5](https://github.com/jyenten/local_rag_api/commit/1f3fad5).


<a id="cz-2026-09-22-až-2026-10-08--párování-evidence-a-řízená-evaluace"></a>

### 2026-09-22 až 2026-10-08 — Párování evidence a řízená evaluace

**Milník projektu:** Implementovaný a zahrnutý v `main`.

- Evaluace rozdělená na modely, načítání datasetů, párování evidence, metriky, runner a JSONL historii; reprodukovatelný náhodný výběr.
- Oddělení DEV/RANDOM/závěrečného TEST, validace/povýšení kandidátů, kurátorská pravidla, CODEOWNERS a CI Eval Governance.
- Zahrnuté pojmy: fyzická čísla PDF stránek, normalizované doslovné fragmenty, MRR/Hit@K, náhodné seedy, únik dat mezi datasety a hranice lidského schválení.
- Důkazy: [modely datasetů, f0b30b8](https://github.com/jyenten/local_rag_api/commit/f0b30b8), [párování evidence, 8e93ce5](https://github.com/jyenten/local_rag_api/commit/8e93ce5), [runner/metriky, ed6bf73](https://github.com/jyenten/local_rag_api/commit/ed6bf73), [náhodný výběr, 3247ab4](https://github.com/jyenten/local_rag_api/commit/3247ab4), [governance, 8aae380](https://github.com/jyenten/local_rag_api/commit/8aae380).
- Pozdější revize našla vady ve starším `scripts.evaluate_random`; historická implementace neznamená, že je každé starší CLI nyní správné. Podporovaný postup porovnání je v [EVALUATION.md](EVALUATION.md#cz).


<a id="cz-2026-10-11-až-2026-10-12--vektorový-baseline-latence-a-pravidla-agentů"></a>

### 2026-10-11 až 2026-10-12 — Vektorový baseline, latence a pravidla agentů

**Milník projektu:** Implementovaný a zahrnutý v `main`.

- Samostatný baseline VectorRetriever, výběr retrieveru v evaluaci, latence samotného retrievalu mean/p50/p95 a přísnější validace běhů/historie.
- Testy výběru v CLI, latence, modelů/historie a Git původu.
- Globální pravidla LEARN/IMPLEMENT/REVIEW a tento deník učení.
- Zahrnuté pojmy: stabilní rozhraní retrieverů, hranice měření, reprodukovatelná metadata běhu a oddělení dokončení projektu od zvládnutí dovedností.
- Důkazy: [vector/observabilita, 9ed9985](https://github.com/jyenten/local_rag_api/commit/9ed9985), [pravidla agentů/deník, 50797d4](https://github.com/jyenten/local_rag_api/commit/50797d4).


<a id="cz-2026-10-13--fáze-33-bm25-retriever"></a>

### 2026-10-13 — Fáze 3.3: BM25 Retriever

**Milník projektu:** Dokončeno

- Implementován `BM25Retriever` nad existujícími Chroma chunky s výukovým vedením.
- Implementováno načítání korpusu, validace, tokenizace, lexikální párování, řazení a výběr top-k.
- Codex samostatně připravil regresní testy.
- Testy prošly revizí kódu a byly integrovány.
- Úplná regrese: 210 úspěšných testů, 1 přeskočený, 2 varování.
- Commit: `c101680` (push do origin/document-search-bm25).

**Doklady učení:**

- Procvičovány Python kolekce, list comprehensions, `enumerate()`, `sorted()`, `lambda` a validace dat.
- Procvičováno rozlišování indexů dokumentů od skóre relevance.
- Pochopen účel deterministického rozhodování při shodě skóre a lexikálního filtrování.
- Během implementace bylo potřebné vedení a opravy.

**Hodnocení dovednosti:** GUIDED

**Další samostatné cvičení:** Vysvětlit a změnit řazení retrievalu bez vedení krok za krokem.

**Další projektový milník:** Evaluace BM25 oproti Vector na DEV a poté RANDOM.


<a id="cz-2026-10-14--historie-portfolia-původ-práce-agentů-a-bezpečnostní-automatizace"></a>

### 2026-10-14 — Historie portfolia, původ práce agentů a bezpečnostní automatizace

**Milník projektu:** Zahrnutý v `main`.

- Starší cvičení přesunuta pod `archive/` bez přepisování obsahu; aktualizovány README portfolia/projektu a uvedena pomoc AI při vývoji.
- Zdokumentována vnořená pravidla agentů, lokální worktree BM25 testů a ručně synchronizované soukromé zrcadlo. Existující BM25 záznam připisuje přípravu regresních testů Codexu; širší samostatné autorství se nevyvozuje.
- Přidány Gitleaks, Dependabot, Dependency Review a plánovaný/PR audit závislostí.
- Zahrnuté pojmy: přesný staging, zachování dokladů učení, izolovaná práce agentů, kontrola tajných údajů a odlišení úspěšných testů od bezpečnosti závislostí.
- Důkazy: [přesun archivu, d157023](https://github.com/jyenten/local_rag_api/commit/d157023), [původ agentů, 646525d](https://github.com/jyenten/local_rag_api/commit/646525d), [kontrola tajných údajů, b032e9a](https://github.com/jyenten/local_rag_api/commit/b032e9a), [audit závislostí, 6a20b25](https://github.com/jyenten/local_rag_api/commit/6a20b25).


<a id="cz-2026-10-15-až-2026-10-17--návrh-reprodukovatelných-linux-závislostí"></a>

### 2026-10-15 až 2026-10-17 — Návrh reprodukovatelných Linux závislostí

**Milník projektu:** Implementováno na `chore/linux-lock-ci`, **nesloučeno** do `main`; [PR #1](https://github.com/jyenten/local_rag_api/pull/1) zůstává otevřený.

- Snapshot závislostí Linux/Python 3.11, ověření čisté instalace Ubuntu, kontroly souladu přímých závislostí/locku a instalace podle locku v CI.
- Na této větvi přidán samostatný dokument posouzení rizik ChromaDB.
- Zahrnuté pojmy: přímé a tranzitivní závislosti, locky specifické pro OS, `pip check`, validace čistého prostředí a sledování bezpečnostních rizik.
- Důkazy: [snapshot workflow, 4b26db1](https://github.com/jyenten/local_rag_api/commit/4b26db1), [kontrola locku, 8e2e7ec](https://github.com/jyenten/local_rag_api/commit/8e2e7ec), [vrchol větve, a258e85](https://github.com/jyenten/local_rag_api/commit/a258e85).
- [Historické PR CI](https://github.com/jyenten/local_rag_api/actions/runs/39022965393) na tomto vrcholu prošlo, bezpečnostní kontroly závislostí selhaly. Nejde o schválení verzí závislostí ani důkaz, že `main` tento lock používá.


<a id="cz-2026-10-20--fáze-34-evaluace-retrievalu"></a>

### 2026-10-20 — Fáze 3.4: Evaluace retrievalu

**Milník projektu:** Dokončeno

- BM25 integrováno do evaluačního CLI přes registr retrieverů.
- Rozšířeny parametrizované CLI testy pro legacy, vector a BM25.
- Úplná regresní sada prošla.
- BM25 a Vector vyhodnoceny na DEV (20 otázek) a RANDOM (25 otázek).
- Oddělený TEST dataset zachován.

**Baseline MRR:**

- DEV: BM25 0.7171, Vector 0.8321
- RANDOM: BM25 0.8133, Vector 0.6050

**Doklady učení:**

- Procvičováno vyhledávání ve slovníku a vzor registru.
- Procvičováno řetězení výjimek pomocí `raise ... from exc`.
- Procvičovány `getattr()`, parametrizované pytest testy a diagnostika `KeyError` a `ImportError`.
- Během implementace bylo potřebné vedení.

**Hodnocení dovednosti:** GUIDED

**Další projektový milník:** Hybridní retrieval pomocí RRF.


<a id="cz-2026-10-26--experiment-úložiště-dokumentů-a-ověřeného-faiss-balíčku"></a>

### 2026-10-26 — Experiment úložiště dokumentů a ověřeného FAISS balíčku

**Milník projektu:** Commit pouze na lokální `experiment/vector-backend` v `14159ce`; **není ve veřejné větvi `main`**.

- Přidán `DocumentStore` s načítáním JSON, validací ID/textu/zdroje/stránky a odmítáním duplicitních ID.
- Přidány kontroly počtu FAISS/indexových záznamů a loader ověřeného balíčku, který před načtením porovnává SHA-256 hodnoty s manifestem.
- Commitnuty regresní testy úložiště pro platné/neplatné záznamy, balíčky a kontrolní součty. Byla zkontrolována jejich přítomnost; audit je nespouštěl ani neurčil počet úspěšných testů.
- Zahrnuté pojmy: stabilní ID dokumentů, oddělení vektorového indexu a metadat, integrita oproti autenticitě, validace před načtením a regrese.
- Větev navazuje na **nesloučený návrh Linux locku**, a proto ji nelze považovat za izolovanou revidovanou změnu již integrovanou v `main`.
- Dodatečný test FAISS retrieveru není ve worktree sledovaný Gitem. Tento storage commit nedokládá hotový FAISS retriever ani náhradu Chroma.
- Z dostupných důkazů nebylo určeno rozdělení implementace člověk/AI ani samostatné vysvětlení; nové hodnocení dovednosti se nepřiděluje.


<a id="cz-2026-10-26--automatizovaný-návrh-závislosti-github-actions"></a>

### 2026-10-26 — Automatizovaný návrh závislosti GitHub Actions

**Milník projektu:** Návrh vytvořený botem, **nesloučený**.

- `dependabot/github_actions/actions/setup-python-7.1.0` v `21a5733` navrhuje `actions/setup-python` 7.0.0 → 7.1.0 ve třech workflow.
- [PR #2](https://github.com/jyenten/local_rag_api/pull/2) je otevřený. Jeho historický [běh CI](https://github.com/jyenten/local_rag_api/actions/runs/40291737972) prošel; neprošly všechny bezpečnostní/governance kontroly.
- Jde o záznam aktivity automatizace a příležitosti k revizi, nikoli lidské implementace nebo prokázané nové dovednosti.


<a id="cz-2026-10-28--dvojjazyčné-návody-regrese-validátoru-a-výchozí-main"></a>

### 2026-10-28 — Dvojjazyčné návody, regrese validátoru a výchozí main

**Milník projektu:** Dokončeno a integrováno přes [PR #3](https://github.com/jyenten/local_rag_api/pull/3), merge commit `cbb2928`.

- Codex na základě výslovného zadání IMPLEMENT + REVIEW zkontroloval a upravil české/anglické README, pravidla AGENTS, provozní dokumentaci, stav architektury/vývoje a postupy golden evidence.
- Opravena validace každé stránky evidence a duplicitních normalizovaných otázek; syntetické pokrytí validátoru rozšířeno na 10 případů. Proti původnímu validátoru tři případy reprodukovaly vady.
- Ověřeno pořadí destruktivního ingestu s falešným klientem, průzkum zdrojových stránek a validace na syntetických datech, relativní odkazy a konfigurace Compose. Nebyl tvrzen benchmark skutečného korpusu, revize evidence ze skutečných PDF ani běhový test Dockeru.
- Po výslovném schválení vlastníkem prošla Eval Governance včetně strukturálních kontrol všech sedmi kandidátních dávek. Vlastník samostatně schválil merge; nálezy auditu závislostí zůstaly otevřené a kontrola zapnutá.
- Původní nezávislá `main` zachována jako `archive/main-initial-20261028`, aktivní výchozí větev přejmenována na `main` a CI/návody sladěny v `bfb1d85`. Cíle existujících otevřených PR byly aktualizovány; historie a datasety zachovány.
- Důkazy: [oprava validátoru, 5dffd5b](https://github.com/jyenten/local_rag_api/commit/5dffd5b), [regrese, aefaa40](https://github.com/jyenten/local_rag_api/commit/aefaa40), [navazující změna výchozí větve, bfb1d85](https://github.com/jyenten/local_rag_api/commit/bfb1d85).
- Ověření: Windows **222 úspěšných testů, 1 přeskočený** (oprávnění symlinků), dvě varování závislostí; GitHub CI na `main` **223 úspěšných testů**. Tyto výsledky se vztahují k integrovanému projektu, nikoli k odděleným FAISS/lock experimentům.
- Zahrnuté pojmy: dokumentace podložená důkazy, smysluplné regrese, schvalovací hranice, testy závislé na prostředí a zachování Git historie.
- Pozorovaná implementace/audit využívaly agenta; nedokládají samostatné lidské zvládnutí těchto témat.


<a id="cz-2026-10-28--odpovědnosti-dokumentace-a-česká-navigace"></a>

### 2026-10-28 — Odpovědnosti dokumentace a česká navigace

**Doklady projektu:** `da6b382` odděluje vývojový postup od schváleného plánu fází.
DEVELOPMENT_GUIDE.md popisuje implementaci a revizi; ROADMAP.md určuje cíle a stav
fází. Původní specifikace fází zůstaly zachovány.

- Následná revize dokumentace přidává úplné české protějšky, přepínání jazyků,
  sbalitelné obsahy a návraty z kapitol ve všech verzovaných Markdown souborech.
- Identifikátory API, příklady, historická měření, existující hodnocení dovedností
  a schvalovací hranice zůstávají zachované. Překlad nedokládá nový implementační
  milník ani samostatnou úroveň dovednosti.
- Důkaz: [oddělení dokumentace, da6b382](https://github.com/jyenten/local_rag_api/commit/da6b382).


<a id="cz-oddělené-jazyky-dokumentace"></a>

### 2026-10-28 — Oddělené jazyky dokumentace

**Údržba projektu:** Revize dokumentace v [PR #4](https://github.com/jyenten/local_rag_api/pull/4) odděluje úplné projektové příručky do `rag_api_project/docs/en/` a `rag_api_project/docs/cs/` se společným [rozcestníkem dokumentace](../README.md).

- README, AGENTS a tento deník zachovávají anglické/české soubory na své úrovni repozitáře/projektu.
- Původní cesty příruček zachovávají navigaci a záložky kapitol; relativní odkazy a přepínání jazyků jsou aktualizované.
- CODEOWNERS a Eval Governance zachovávají dosavadní ochranu a pokrývají nová česká pravidla agentů a obě jazykové cesty kurátorské příručky.
- Tato dokumentační práce s pomocí agenta nemění retrieval kód, závislosti, golden evidence, chráněné datasety ani existující hodnocení dovedností.

<a id="cz-centralizovaná-dokumentace"></a>

### 2026-10-28 — Centralizovaná dokumentace a jednodušší navigace

**Údržba dokumentace:** Všechny verzované Markdown soubory jsou nyní pod `docs/` v kořeni repozitáře, kromě kořenového `README.md`. České a anglické příručky, deník učení i pravidla agentů používají `docs/cs/` a `docs/en/`; jejich umístění uvádí [rozcestník dokumentace](../README.md).

- Odstraněny opakované návraty na obsah; obsah kapitol a závěrečný odkaz nahoru zůstávají.
- Aktualizovány relativní odkazy a chráněné cesty v CODEOWNERS/Eval Governance; globální a projektová pravidla agentů zachovávají působnost a načítají se výslovně přes odkazy v README.
- Historická hodnocení dovedností, schválené cíle roadmapy, retrieval kód, závislosti, golden evidence a DEV/RANDOM/TEST jsou beze změn.

<a id="cz-necommitnutá-práce-pozorovaná-28-10-2026"></a>

## Necommitnutá práce pozorovaná 28. 10. 2026

Jde o pozorování worktrees, nikoli datované dokončené milníky. Z pouhé přítomnosti souborů se nevyvozuje datum vytvoření ani správnost.

- Bývalý worktree `document-search-bm25`: lokální prototyp `rrf_contribution`/`fuse_rankings` s deterministickým rozhodováním podle ID; změny rozhraní BM25/Vector `search_with_ids`; upravené requirements a nesledovaný Windows lock soubor. Tato práce nedokládá commitnutou/vydanou integraci HybridRetrieveru ani ověřený výsledek hybridní evaluace. Přítomnost závislostí/locku neznamená jejich schválení. Další nesledované experimenty agentů nebyly připsány verzovanému milníku.
- `agent/phase3-model-hardening`: vrchol větve je starší `8aae380` s necommitnutými změnami historie/modelů/CLI/latence/retrieverů/testů. Několik oblastí se překrývá s později integrovaným vektorovým baseline; změněný worktree není důkazem další hotové či sloučené funkce.
- `experiment/vector-backend`: výše je odlišena commitnutá práce na úložišti od nesledovaného testu FAISS retrieveru. Úspěch experimentálních testů se netvrdí.

Původní worktrees a necommitnuté změny byly pouze čteny a zachovány. Dalším učebním zaměřením zůstává hybridní RRF s měřením DEV/RANDOM bez ladění na TEST; experiment úložiště/backendu zůstává samostatným předmětem revize.


<a id="cz-pokrytí-auditu-větví--2026-10-28"></a>

## Pokrytí auditu větví — 2026-10-28

Bylo staženo a zkontrolováno sedm tehdejších veřejných GitHub větví. Předkové se v historii počítají jednou, nikoli jako samostatné úspěchy. Soupis je časový snímek, nikoli živá stavová stránka.

| Veřejná větev | Zkontrolovaný vrchol | Stav vůči zkontrolované `main` |
| --- | --- | --- |
| `main` | `bfb1d85` | Integrovaný projekt a současná výchozí větev |
| `master` | `3c0bfdd` | Historický základ API/CI; předek `main` |
| `retrieval-eval-refactor` | `010d8d1` | Raný stav roadmapy/evaluace; předek `main` |
| `docs/bilingual-rag-runbooks-20261028` | `9504b1e` | Sloučeno přes PR #3 |
| `chore/linux-lock-ci` | `a258e85` | Nesloučený PR #1; pouze návrh locku |
| `dependabot/github_actions/actions/setup-python-7.1.0` | `21a5733` | Nesloučený návrh bota, PR #2 |
| `archive/main-initial-20261028` | `0cb285c` | Zachovaná nezávislá původní historie README |

Zkontrolováno bylo také osm lokálních větví v původním klonu projektu a všech pět registrovaných worktrees. `main` a dokumentační větev nynějšího dokumentačního checkoutu jsou již zastoupené ve veřejné tabulce.

| Původní lokální větev | Zkontrolovaný vrchol | Důkazy/stav |
| --- | --- | --- |
| `agent/bm25-tests` | `646525d` | Čistý worktree; vrchol již v `main`; původ BM25 testů zdokumentován |
| `agent/phase3-model-hardening` | `8aae380` | Vrchol v `main`; změněný auditní worktree ponechán odděleně |
| `chore/linux-lock-ci` | `a258e85` | Čistý worktree; stejný nesloučený návrh jako veřejná větev |
| `document-search-bm25` | `f9cc7e2` | Bývalý výchozí název; změněný hybridní/závislostní worktree, audit jej nesynchronizoval |
| `experiment/vector-backend` | `14159ce` | Pouze lokální storage/FAISS commit a nesledovaný test retrieveru |
| `master` | `3c0bfdd` | Stejný historický stav jako veřejná větev |
| `retrieval-eval-refactor` | `010d8d1` | Stejný historický stav jako veřejná větev |
| `retrieval-eval-refactor¨` | `3c0bfdd` | Lokální alias stavu `master`; bez samostatného milníku |

Uložené reference soukromého zrcadla `codex-private/main` a `codex-private/agent/bm25-tests` obě ukazovaly na `646525d`, již zahrnutý ve veřejné historii. Kontrolovaly se pouze tyto lokální reference; živý soukromý remote nebyl stahován. Zastaralá uložená `origin/document-search-bm25` v dokumentačním checkoutu je reference před přejmenováním, nikoli osmá současná veřejná větev. Audit deníku učení nezměnil větve, zdrojový kód, datasety ani soubory závislostí.

<a id="cz-2026-10-29-portfolio-dokumentace"></a>

### 2026-10-29 — Dokumentace portfolia a kontext lokálního provozu

**Údržba dokumentace:** Připravena na základě výslovného pokynu vlastníka provést úpravy z auditu portfolia; výchozí veřejný `main` je `28c7450`.

- Zkráceny české/anglické úvody portfolia a projektu, zachováno přiznání výrazné AI asistence a odkazy na pravidla agentů; podrobnosti workflow odkazují na deník a vývojovou příručku.
- Doplněn datovaný veřejný výsledek CI pro `28c7450`: **223 testů prošlo za 7,51 s** ([běh 40770029069](https://github.com/jyenten/local_rag_api/actions/runs/40770029069)). Výsledek patří této výchozí revizi, nikoli automaticky novému dokumentačnímu commitu.
- Doplněny odkazy na historické MRR srovnání BM25/Vector z 20. 10. 2026 s výslovným původem a omezeními reprodukce; anglický příklad schématu a tabulka baseline jsou obsahově soběstačné. Historické metriky se neměřily znovu ani neměnily.
- Opraveny dokumentační cesty v ukázce cílové struktury, zpřesněn skutečný rozsah `/ready` a v přehledech použity plné názvy milníků místo nejednoznačných čísel fází z deníku.
- Do provozních příruček doplněn vlastníkem potvrzený lokální/offline kontext a známý stav kontroly závislostí. Závislostní a bezpečnostní kontroly zůstávají zapnuté.
- Ověření změny zahrnuje relativní cesty/kotvy, zachování starých kotev, volby CLI a nezměněné benchmark hodnoty. Neprováděl se ingest zdrojových PDF, evaluace korpusu ani test Docker runtime.
- Retrieval kód, architektonická rozhodnutí, priority roadmapy, závislosti, chráněné datasety a původní hodnocení dovedností zůstávají zachovány. Tento záznam nepřiděluje nové hodnocení dovedností.

[↑ Nahoru](#top)
