<a id="top"></a>

# Provozní příručka

[Česky](#cz) · [English](../en/OPERATIONS.md#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Obsah — kliknutím rozbalit</summary>

- [1. Předpoklady a instalace (Windows PowerShell)](#cz-1-předpoklady-a-instalace-windows-powershell)
- [1a. Reprodukovatelnost závislostí (Windows Python 3.11)](#cz-1a-reprodukovatelnost-závislostí-windows-python-311)
- [1b. Kontext kontroly závislostí](#cz-1b-kontext-kontroly-zavislosti)
- [2. Konfigurace a zdroje](#cz-2-konfigurace-a-zdroje)
- [3. Ingest PDF do ChromaDB](#cz-3-ingest-pdf-do-chromadb)
- [4. Spuštění API](#cz-4-spuštění-api)
- [5. Vyhledání podkladů v původních PDF (page explorer)](#cz-5-vyhledání-podkladů-v-původních-pdf-page-explorer)
- [6. Testy a kontrola commitu](#cz-6-testy-a-kontrola-commitu)
- [7. Offline evaluace](#cz-7-offline-evaluace)
- [8. Docker a provozní omezení](#cz-8-docker-a-provozní-omezení)

</details>

---

<a id="cz"></a>

> **Rozsah:** Současný RAG projekt nad Chroma, Python 3.11. Příkazy spouštěj z `rag_api_project/`. Jde o lokální výukový prototyp.
>
> **Bezpečnost:** `python -m scripts.ingest` existující Chroma kolekci s nakonfigurovaným názvem **smaže a znovu vytvoří**. Před spuštěním ověř zálohu, korpus a konfiguraci; nejde o přírůstkový ingest.

<a id="cz-1-předpoklady-a-instalace-windows-powershell"></a>

## 1. Předpoklady a instalace (Windows PowerShell)

Požadavky: Python 3.11, Git, přístup k potřebným Python balíčkům a modelům při první instalaci. Pracuj v adresáři `rag_api_project/`:

```powershell
# Z kořene klonovaného repozitáře (cd proveď pouze jednou):
cd rag_api_project
python --version  # Musí být 3.11.x.
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
```

V PowerShellu lze příkazy spouštět i bez aktivace pomocí `.\.venv\Scripts\python.exe -m ...`. Instalaci lze ověřit pomocí `python -m pytest -q`.

**Linux / macOS:**

```bash
cd rag_api_project
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
```

Před instalací zkontroluj použitý interpreter a kompatibilitu balíčků. Ve zveřejněné větvi je `requirements.txt` nepinovaný; lokálně vytvořené lockfily nelze automaticky pokládat za schválené ani přenositelné. Neměň verze závislostí jako součást dokumentační úpravy.


<a id="cz-1a-reprodukovatelnost-závislostí-windows-python-311"></a>

## 1a. Reprodukovatelnost závislostí (Windows Python 3.11)

Základní `requirements.txt` ve zveřejněné větvi obsahuje neomezené verze balíčků; lokálně může existovat `requirements-win-py311.lock.txt` s přesnými verzemi. Tento lockfile **není automaticky schválený ani verzovaný**. Nezacházej s ním jako s univerzálním instalačním návodem bez samostatné kontroly kompatibility a CI.

Před případným přijetím lockfilu je nutné ověřit podporovaný Python/OS, metodu vytvoření, čisté instalace na Windows a CI, soulad s `requirements.txt` a proces aktualizace balíčků. Změny balíčků patří do samostatného commitu a nesmí se slučovat s revizí dokumentace.


<a id="cz-1b-kontext-kontroly-zavislosti"></a>

## 1b. Kontext kontroly závislostí

Chatbot nyní běží lokálně/offline. Vlastník kontrolu závislostí ponechává zapnutou i s ohledem na možné budoucí napojení API. [Audit revize `82d5889` z 29. 10. 2026](https://github.com/jyenten/local_rag_api/actions/runs/40865587058) skončil chybou se stejnou známou sadou nálezů u ChromaDB; jde o stav oddělený od výsledků Python testů.

Relevance nálezů závisí na zasažených funkcích a konfiguraci provozu. Samotný lokální/offline provoz neprokazuje zneužitelnost ani nerelevanci nálezu. Tato úprava dokumentace žádnou kontrolu nevypíná ani neuděluje výjimku.

Posouzení aktualizované 7. 11. 2026, čtyři unikátní CVE, hranice lokálního profilu a doložený stav běžících kontejnerů jsou v [bezpečnostním posouzení ChromaDB](CHROMA_SECURITY.md). `pip-audit` zůstává zapnutý a známé nálezy se nepotlačují.


<a id="cz-2-konfigurace-a-zdroje"></a>

## 2. Konfigurace a zdroje

Aplikace čte `.env` z `rag_api_project/` přes `app/config.py`. Důležité proměnné:

| Proměnná | Příklad | Význam |
| --- | --- | --- |
| `RAG_COLLECTION_NAME` | `ospf` | Název Chroma kolekce |
| `RAG_EMBEDDING_MODEL_NAME` | `all-MiniLM-L6-v2` | Embedding model |
| `RAG_RETRIEVAL_RESULTS` | `8` | Počet vyhledaných chunků |
| `RAG_GENERATION_MODEL_NAME` | `google/flan-t5-base` | Generační model |
| `RAG_RERANKER_MODEL_NAME` | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Reranking v RAG odpovědní pipeline |
| `RAG_DATA_DIR` | absolutní cesta k PDF | Volitelné přepsání adresáře pro ingest |
| `RAG_CHROMA_DIR` | absolutní cesta k indexu | Volitelné přepsání umístění Chroma |

Implicitní cesty z `app/config.py`: `data/` pro PDF a `chroma_db/` pro Chroma index. Obsah těchto adresářů může být lokální nebo neveřejný; necommituj soukromé PDF, databázi, `.env` ani modelové cache.

Vlož zdrojová PDF **přímo do** `data/` (nikoli do podadresářů). Současný ingest vyhledává soubory odpovídající vzoru `*.pdf`; před spuštěním ověř přesné názvy a přípony.

Proměnné prostředí mají přednost před `.env`. Po změně konfigurace restartuj API (nastavení se cachuje). Ingest a vector/legacy retrieval musí používat stejný embedding model jako index. Page explorer a validátor čtou standardně relativní `data/`, nikoli `RAG_DATA_DIR`; vlastní cestu jim předej pomocí `--data-dir <adresář>`.


<a id="cz-3-ingest-pdf-do-chromadb"></a>

## 3. Ingest PDF do ChromaDB

```powershell
python -m scripts.ingest
```

**Pozor — destruktivní operace:** `scripts/ingest.py` zavolá `delete_collection()`, pokud kolekce s daným názvem existuje, a následně vytvoří novou. Neprováděj ingest automaticky jako krok testů nebo rutinní evaluace. Pro opakovaný ingest nejdříve ověř zálohu a schválený záměr.

Aktuální pipeline: extrakce fyzických PDF stránek pomocí pypdf → čištění textu → chunkování (výchozí `chunk_size=1000`, `overlap=150`, ve znacích) → SentenceTransformer embeddingy → Chroma. Chunk metadata obsahují `source` (název PDF), `page` (fyzická stránka od 1) a `chunk_index` (pořadí v rámci PDF). Identifikátory chunků jsou v poli Chroma `ids`, nikoliv automaticky v metadatech.

Kolekce se maže **před** extrakcí a upsertem. Chyba čtení PDF nebo zápisu po smazání neobnoví starý index; obnova není transakční. Zálohu adresáře Chroma pořizuj při zastavených procesech, které index používají.

Po ingestu ověř počet záznamů a ukázku metadat **bez změny obsahu kolekce**:

```powershell
python -c "import chromadb; from app.config import get_settings; s=get_settings(); c=chromadb.PersistentClient(path=str(s.chroma_dir)).get_collection(name=s.collection_name); print('COLLECTION:', c.name, 'CHUNKS:', c.count()); print(c.get(limit=3, include=['metadatas']))"
```

`PersistentClient` není připojení v režimu read-only: při otevření může vytvořit adresář/databázi nebo provést migrace. Před kontrolou ověř existenci správného `RAG_CHROMA_DIR`; pro striktně neměnnou kontrolu pracuj s kopií indexu.

Počet chunků závisí na přesné verzi PDF, chunkování a konfiguraci; historické počty nejsou univerzálním očekáváním. U změn korpusu zaznamenej názvy/identitu zdrojových PDF a konfiguraci, aby šlo výsledky evaluace reprodukovat.


<a id="cz-4-spuštění-api"></a>

## 4. Spuštění API

```powershell
python -m uvicorn app.main:app --reload
```

OpenAPI: http://127.0.0.1:8000/docs. Příklady:

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
Invoke-RestMethod -Uri http://127.0.0.1:8000/ask -Method Post -ContentType 'application/json' -Body '{"question":"How does OSPF select the router ID?"}'
```

`/ready` a `/stats` poskytují další diagnostiku prostředí a kolekce. **Důležitá hranice:** BM25 je volitelný v *offline evaluation CLI*, nikoliv automaticky jako možnost pro HTTP `/ask`. Rozpracovaný hybrid nepovažuj za implementovanou funkci API.


<a id="cz-5-vyhledání-podkladů-v-původních-pdf-page-explorer"></a>

## 5. Vyhledání podkladů v původních PDF (page explorer)

```powershell
python -m scripts.search_pdf "OSPF router ID" --top-k 10 --interactive
```

`scripts.search_pdf` používá samostatný BM25 index *PDF stránek* z `data/`. Není to totéž jako `app/retrievers/bm25.py`, který řadí chunky uložené v Chroma. Page explorer slouží k průzkumu a ručnímu ověření důkazů, nikoli k automatickému přepisování golden evidence.


<a id="cz-6-testy-a-kontrola-commitu"></a>

## 6. Testy a kontrola commitu

```powershell
python -m pytest -q
python -m pytest -q tests/retrievers/test_bm25.py
git diff --check
```

Před commitem připrav pouze zamýšlené soubory (nikdy automatické `git add .`), zkontroluj staging a případně spusť projektový pre-commit helper:

```powershell
git diff --cached --check
python -m scripts.git_check
```

`scripts.git_check` kontroluje staged whitespace a spouští pytest. Pro změny v `eval/` nebo pravidlech curatoru platí dodatečná pravidla v `AGENTS.md`, `docs/cs/EVAL_CURATOR_AGENT.md` a CI governance.

Před prací použij `git status --short` a `git branch --show-current`. Výchozí integrační větev je `main`; změny připravuj na samostatné pracovní větvi a slučuj přes zkontrolovaný PR. Nepřepínej větev přes nesouvisející WIP. Po explicitním `git add <cesty>` přečti `git diff --cached` i seznam souborů. Helper nekontroluje tajemství, schválení ani věcný rozsah změn. Commit/push prováděj jen v autorizovaném rozsahu, bez automatického merge.


<a id="cz-7-offline-evaluace"></a>

## 7. Offline evaluace

```powershell
python -m scripts.evaluate_retrieval --retriever legacy --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset dev
python -m scripts.evaluate_retrieval --retriever bm25 --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset random
python -m scripts.evaluate_retrieval --retriever bm25 --dataset random
```

Výstup: MRR, Hit@1/3/5/8, latence mean/P50/P95 a první pozice relevantního důkazu pro jednotlivé otázky. Běhy se zapisují do `eval/results/*_runs.jsonl` podle strategie a datasetu; obsahují hash datasetu, Git commit a příznak dirty worktree. Zápis do historie je vedlejší efekt: příkaz není čistě read-only. **TEST je held-out** a úmyslně není volbou tohoto CLI. Podrobnosti: [EVALUATION.md](EVALUATION.md).


<a id="cz-8-docker-a-provozní-omezení"></a>

## 8. Docker a provozní omezení

```powershell
docker compose up --build
docker compose down
```

Compose váže port výslovně na `127.0.0.1:8001:8000`; API je na http://127.0.0.1:8001/docs. Připojuje `chroma_db/` a modelovou cache. Změna YAML sama neupraví již běžící kontejner; před jeho znovuvytvořením ověř původní Compose projekt a cesty mountů podle [bezpečnostního posouzení](CHROMA_SECURITY.md). Dockerfile kopíruje pouze `app/`, `scripts/` a `.env.example`; nekopíruje `document_search/`, `evaluation/`, `eval/` ani PDF. Ingest, page explorer a evaluaci proto spouštěj nativně. Kontejner potřebuje hotový kompatibilní index a přístup k modelům při prvním použití.

Compose nepředává hostitelský `.env` aplikaci: nemá `env_file` ani `environment` a obraz `.env` neobsahuje. Pro vlastní nastavení je nutné explicitní předání `RAG_*` proměnných v lokální Compose konfiguraci, s cestami platnými uvnitř kontejneru. Samotný start nebo `/health` nepotvrzuje funkčnost `/ask`; zkontroluj také `/ready` a `/stats`.

**Diagnostika:** `No PDF files found` znamená zkontrolovat adresář `data/` a příponu souborů. Chybějící Chroma kolekce může znamenat nesprávnou cestu nebo neprovedený ingest. `ModuleNotFoundError` typicky znamená nesprávné prostředí či pracovní adresář. `FIRST_EVIDENCE_RANK=None` neznamená automaticky prázdný retrieval — pouze že žádný z hodnocených chunků neodpovídal golden evidence.

[↑ Nahoru](#top)
