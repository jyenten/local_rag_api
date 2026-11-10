# Školní PostgreSQL projekt – Evidence a evaluace Local RAG API

**Stav:** samostatný návrh pro Databázové systémy I (VŠB), nikoliv změna běžící aplikace. **7 tabulek**, 7 vazeb; návrh schématu je ve `01_schema.sql`, relační model pro dbdiagram.io v `relational_model.dbml`.

## Co znamená jeden záznam v tabulce
| Tabulka | Význam řádku |
|---|---|
| documents | Identifikátor jednoho PDF zdroje z původních evaluačních dat (samotné PDF se neukládá) |
| evaluation_datasets | Jedna neměnná Git verze datasetu DEV/RANDOM/TEST |
| evaluation_questions | Jedna otázka v konkrétní verzi datasetu |
| gold_evidence | Jedna sada alternativních ověřovacích fragmentů a fyzických PDF stran pro otázku a zdroj |
| indexing_runs | Jedno skutečné spuštění indexování; bez lokálního indexu se do této tabulky nevymýšlejí data |
| evaluation_runs | Jeden evaluační běh nebo zdokumentovaný historický souhrn (původ je výslovně označen) |
| evaluation_results | Výsledek jedné otázky v reálném běhu; z agregovaného MRR jej nelze zpětně zrekonstruovat |

**Zjednodušení z 9 na 7:** vypuštěny `document_versions` a `document_chunks`. Část historizace řeší verzované datasety a evidence indexovacích běhů; chunky/embeddingy zůstávají v ChromaDB. Nevýhoda: tento školní model neudržuje verze obsahu jednotlivých PDF ani referenční integritu vůči chunkům. Pro provozní RAG může být později vhodné samostatné rozšíření, nikoli automatická migrace.

## Původ skutečných dat
- Otázky DEV (20) a RANDOM (25) jsou beze změny převzaty z `rag_api_project/eval/dev_questions.json` a `rag_api_project/eval/random_questions.json`. Pole `gold_evidence` zachovávají fyzické stránky (1-based) a logiku `contains_any` (OR).
- Tři názvy PDF jsou **reálně uvedeny v těchto datasetech**, soubory PDF nejsou součástí veřejného repozitáře. `file_sha256=NULL` není vymyšlený hash.
- Čtyři historické souhrny BM25 vs Vector (20. 10. 2026) jsou přepsány z `docs/en/EVALUATION.md`, oddíl 8. MRR je historický záznam, Hit@K pochází ze staršího reportu a není nezávisle reprodukován; původní JSONL, korpus a index nejsou zveřejněny. `record_kind=documented_baseline`, `executed_at=NULL`, `dataset_sha256=NULL`. Původní SHA-256 historických datasetů není dostupné, takže tyto čtyři souhrny mají záměrně `dataset_id=NULL` a pouze `dataset_label`: nevytváříme falešnou vazbu na dnešní verzi. Bez původních dat nejsou vymyšleny individuální výsledky ani latence.
- TEST je úmyslně vynechán. Původní chráněné datové soubory se nemění.

## Postup spuštění v PostgreSQL
1. V pgAdmin nebo psql vytvoř **novou**, prázdnou databázi `local_rag_school`. Nepoužívej existující provozní databázi.
2. Připoj se k ní a spusť `01_schema.sql`.
3. Spusť `02_seed_real.sql`. Opakovaný běh skriptu nemá přidávat duplicitní zdroje.
4. Spusť `05_checks.sql`, následně analytické `03_queries.sql`.
5. Soubor `04_dynamic_workflow.sql` demonstruje zápis nové události do databáze a končí `ROLLBACK`; nevytváří falešná měření.
6. Pro školu otevři `relational_model.dbml` v dbdiagram.io a vyexportuj grafický relační model do PDF.

Bez běžícího PostgreSQL serveru nelze tvrdit, že byly SQL skripty integračně otestovány; kontrola po nasazení je součástí kroku 4.

## Netriviální operace pro DS II
1. Porovnat MRR a Hit@K BM25 a Vector **pro tentýž dataset i indexovací snapshot**, nikoli pouze nejvyšší skóre bez kontroly provenance.
2. Přes JOINy propojit témata, otázky a technické dokumenty a určit nejkritičtější stránky.
3. Najít otázky, pro které je první relevantní výsledek mimo top-k nebo úplně chybí.
4. Ověřit úplnost vložených výsledků běhu oproti `question_count`.

## Co je zatím nehotové
Tabulky `indexing_runs` a `evaluation_results` v prvotním real-data seedu nemají řádky, protože veřejný repo neobsahuje reálný log indexování a jednotlivé JSONL výsledky. Jde o **připravenou strukturu pro dynamická data**, ne o hotovou synchronizaci FastAPI. Nové běhy se musí vložit z reálného měření; žádná změna původního API, ingestu ani evaluace nebyla provedena.

## Proč škola dostane více než katalog
Databáze zaznamenává skutečně proměnlivý proces: příchod nových otázek, záznam nové verze datasetu, spouštění indexování, měření běhů, detailní skóre a porovnávání metod. Splňuje 7 tabulek a více než 5 entitních vazeb. Originální problém je reprodukovatelná evaluace RAG.

**Bezpečnost:** nedávat do GitHubu zdrojová PDF, lokální Chroma data, `.env`, autentizační údaje ani interní dotazy. Změny jsou výhradně v tomto odděleném adresáři a neimplementují PostgreSQL do FastAPI.

## Import nových skutečných dat (dynamická část)
Při lokálně dostupných původních souborech `eval/results/*.jsonl` lze vložit **reálně naměřené** jednotlivé výsledky; bez lokálního corpus/indexu není možné je znovu vytvořit. Skript používá parametrizované SQL, kontroluje původní SHA-256 datasetu, Git blob verzi, kompletnost otázek a přepočítá MRR/Hit@K před zápisem.

Z kořene repozitáře (příklad PowerShell):
```powershell
python -m pip install "psycopg[binary]"
python school_postgresql/import_real_history.py --dataset dev --dataset-file rag_api_project/eval/dev_questions.json --retriever bm25 --history-file rag_api_project/eval/results/dev_bm25_runs.jsonl --check-only
$env:SCHOOL_RAG_DSN = 'postgresql://UZIVATEL:HESLO@localhost:5432/local_rag_school'
python school_postgresql/import_real_history.py --dataset dev --dataset-file rag_api_project/eval/dev_questions.json --retriever bm25 --history-file rag_api_project/eval/results/dev_bm25_runs.jsonl
```
Heslo nikdy neukládej do repozitáře. Import existujících real-data JSONL je volitelný, nevkládá žádná vymyšlená měření. Skutečné běhy bez ověřeného indexovacího manifestu ponechávají `indexing_run_id=NULL` a nelze je tvrdit jako plně srovnatelné napříč korpusy. Validátor má izolované testy:
```powershell
python -m unittest discover -s school_postgresql -p "test_*.py" -v
```
