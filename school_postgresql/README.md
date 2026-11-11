# Školní PostgreSQL projekt – Evidence a evaluace Local RAG API

**Stav:** samostatný návrh pro Databázové systémy I (VŠB), nikoliv změna běžící aplikace. **8 tabulek**, 8 vazeb; návrh schématu je ve `01_schema.sql`, relační model pro dbdiagram.io v `relational_model.dbml`.

## Co znamená jeden záznam v tabulce
| Tabulka | Význam řádku |
|---|---|
| documents | Identifikátor jednoho PDF zdroje z původních evaluačních dat (samotné PDF se neukládá) |
| eval_datasets | Jedna neměnná Git verze datasetu DEV/RANDOM/TEST |
| eval_questions | Jedna otázka v konkrétní verzi datasetu |
| gold_evidence | Jeden očekávaný textový fragment na jedné fyzické stránce PDF, přiřazený k otázce a zdroji |
| indexing_runs | Jedno skutečné spuštění indexování; bez lokálního indexu se do této tabulky nevymýšlejí data |
| eval_runs | Jeden evaluační běh nebo zdokumentovaný historický souhrn (původ je výslovně označen) |
| eval_results | Výsledek jedné otázky v reálném běhu; z agregovaného MRR jej nelze zpětně zrekonstruovat |
| eval_hit_rates | Jedna metrika Hit@k pro konkrétní evaluační běh; PK je dvojice (evaluation_run_id, k) |

**Původní zjednodušení z 9 na 7:** vypuštěny `document_versions` a `document_chunks`. Část historizace řeší verzované datasety a evidence indexovacích běhů; chunky/embeddingy zůstávají v ChromaDB. Nevýhoda: tento školní model neudržuje verze obsahu jednotlivých PDF ani referenční integritu vůči chunkům. Pro provozní RAG může být později vhodné samostatné rozšíření, nikoli automatická migrace.

**Aktuální normalizace 7 → 8:** čtyři sloupce Hit@1/3/5/8 byly nahrazeny samostatnou tabulkou `eval_hit_rates`. Lze přidat další k bez nové kolony a FK na `eval_runs` brání osiřelým metrikám. Zkrácené názvy tabulek `eval_datasets`, `eval_questions`, `eval_runs` a `eval_results` jsou záměrné; dlouhé identifikátory `evaluation_run_id` a `dataset_id` zůstaly kvůli konzistentním vazbám a migraci.

## Původ skutečných dat
- Otázky DEV (20) a RANDOM (25) jsou beze změny převzaty z `rag_api_project/eval/dev_questions.json` a `rag_api_project/eval/random_questions.json`. Z původních 50 skupin `gold_evidence` vytváříme 62 atomických dvojic (povolená fyzická stránka, alternativní textový fragment). Neznamená to, že každý fragment byl nezávisle potvrzen na každé z uvedených stran: zdrojové PDF chybí ve veřejném repozitáři. Logika `contains_any` (OR) zůstává zachována; žádné SQL pole neobsahuje seznam hodnot. Model je vhodnější pro výuku 1NF.
- Tři názvy PDF jsou **reálně uvedeny v těchto datasetech**, soubory PDF nejsou součástí veřejného repozitáře. `file_sha256=NULL` není vymyšlený hash.
- Čtyři historické souhrny BM25 vs Vector (20. 10. 2026) jsou přepsány z `docs/en/EVALUATION.md`, oddíl 8. MRR je historický záznam, Hit@K pochází ze staršího reportu a není nezávisle reprodukován; původní JSONL, korpus a index nejsou zveřejněny. `record_kind=documented_baseline`, `executed_at=NULL`, `dataset_sha256=NULL`. Původní SHA-256 historických datasetů není dostupné, takže tyto čtyři souhrny mají záměrně `dataset_id=NULL` a pouze `dataset_label`: nevytváříme falešnou vazbu na dnešní verzi. Bez původních dat nejsou vymyšleny individuální výsledky ani latence.
- TEST je úmyslně vynechán. Původní chráněné datové soubory se nemění.

## Převod již existující lokální sedmitabulkové databáze (bez mazání dat)

Pokud již máš databázi `local_rag_school` se 7 tabulkami a 116 záznamy, **nespouštěj znovu `01_schema.sql`** a nesmaž žádnou tabulku. Nejdříve vytvoř zálohu (příklad z PowerShellu pro lokální Docker kontejner `local_rag_test`):

```powershell
docker exec local_rag_test pg_dump -U Admin -d local_rag_school --format=custom --file=/tmp/local_rag_school_before_hitk.dump
docker cp local_rag_test:/tmp/local_rag_school_before_hitk.dump .\local_rag_school_before_hitk.dump
```

Ulož zálohu mimo Git a zkontroluj, že soubor existuje. Ve VS Code ověř `SELECT current_database(), current_user;` = `local_rag_school`, `Admin`. Potom spusť **celý** `07_migrate_from_seven_tables.sql` v jednom SQL editoru, zkontroluj výstup a spusť `08_verify_eight_tables.sql`, `05_checks.sql`, `06_integrity_tests.sql` a `03_queries.sql`. Skript je jednorázový, v transakci, kontroluje každý převáděný Hit@k před odstraněním původních sloupců a zachová existující ID a FK. Pokud nastane chyba, neprováděj ruční mazání; opravíme ji ze zálohy.

Očekávaný stav beze změny ostatních dat: **132 řádků** (původních 116 + 16 Hit@k), z toho čtyři historické běhy. Pokud jsi mezitím vložil další skutečné běhy, migrují se také jejich nenulové metriky; finální počet může být vyšší.

## Postup spuštění v PostgreSQL (nová databáze)
1. V pgAdmin nebo psql vytvoř **novou**, prázdnou databázi `local_rag_school`. Nepoužívej existující provozní databázi.
2. Připoj se k ní a spusť `01_schema.sql`.
3. Spusť `02_seed_real.sql`. Opakovaný běh skriptu nemá přidávat duplicitní zdroje.
4. Spusť `08_verify_eight_tables.sql`, `05_checks.sql`, integritní test `06_integrity_tests.sql` a následně analytické `03_queries.sql`.
5. Soubor `04_dynamic_workflow.sql` demonstruje zápis nové události do databáze a končí `ROLLBACK`; nevytváří falešná měření.
6. Pro školu otevři `relational_model.dbml` v dbdiagram.io a vyexportuj grafický relační model do PDF.

Schéma, DML, analytické dotazy, idempotence a integritní testy jsou ověřovány na skutečném PostgreSQL 16/18 v GitHub Actions (`.github/workflows/school-postgresql.yml`). Lokální školní instalaci je i tak potřeba spustit a zkontrolovat samostatně.

## Netriviální operace pro DS II
1. Porovnat MRR a Hit@K BM25 a Vector **pro tentýž dataset i indexovací snapshot**, nikoli pouze nejvyšší skóre bez kontroly provenance.
2. Přes JOINy propojit témata, otázky a technické dokumenty a určit nejkritičtější stránky.
3. Najít otázky, pro které je první relevantní výsledek mimo top-k nebo úplně chybí.
4. Ověřit úplnost vložených výsledků běhu oproti `question_count`.

## Co je zatím nehotové
Tabulky `indexing_runs` a `eval_results` v prvotním real-data seedu nemají řádky, protože veřejný repo neobsahuje reálný log indexování a jednotlivé JSONL výsledky. Jde o **připravenou strukturu pro dynamická data**, ne o hotovou synchronizaci FastAPI. Nové běhy se musí vložit z reálného měření; žádná změna původního API, ingestu ani evaluace nebyla provedena.

## Proč škola dostane více než katalog
Databáze zaznamenává skutečně proměnlivý proces: příchod nových otázek, záznam nové verze datasetu, spouštění indexování, měření běhů, detailní skóre a porovnávání metod. Splňuje 8 tabulek a více než 5 entitních vazeb. Originální problém je reprodukovatelná evaluace RAG.

**Bezpečnost:** nedávat do GitHubu zdrojová PDF, lokální Chroma data, `.env`, autentizační údaje ani interní dotazy. Změny jsou v odděleném adresáři `school_postgresql/` a v samostatném testovacím workflow `.github/workflows/school-postgresql.yml`; provozní FastAPI ani retrieval se nemění.

## Import nových skutečných dat (dynamická část)
Při lokálně dostupných původních souborech `eval/results/*.jsonl` lze vložit **reálně naměřené** jednotlivé výsledky; bez lokálního corpus/indexu není možné je znovu vytvořit. Skript používá parametrizované SQL, kontroluje původní SHA-256 datasetu, Git blob verzi, kompletnost otázek a přepočítá MRR/Hit@K před zápisem.

Z kořene repozitáře (příklad PowerShell):
```powershell
python -m pip install "psycopg[binary]"
python school_postgresql/import_real_history.py --dataset dev --dataset-file rag_api_project/eval/dev_questions.json --retriever bm25 --history-file rag_api_project/eval/results/dev_bm25_runs.jsonl --check-only
$env:SCHOOL_RAG_DSN = 'postgresql://UZIVATEL:HESLO@localhost:54774/local_rag_school'
python school_postgresql/import_real_history.py --dataset dev --dataset-file rag_api_project/eval/dev_questions.json --retriever bm25 --history-file rag_api_project/eval/results/dev_bm25_runs.jsonl
```
Heslo nikdy neukládej do repozitáře. Import existujících real-data JSONL je volitelný, nevkládá žádná vymyšlená měření. Skutečné běhy bez ověřeného indexovacího manifestu ponechávají `indexing_run_id=NULL` a nelze je tvrdit jako plně srovnatelné napříč korpusy. Validátor má izolované testy:
```powershell
python -m unittest discover -s school_postgresql -p "test_*.py" -v
```

## Ověřená integrace a školní odevzdání
- Dříve PostgreSQL 16 úspěšně spustil sedmitabulkové DDL, DML, integritní testy s ROLLBACK, osm analytických dotazů i opakovaný import bez duplicit: https://github.com/jyenten/local_rag_api/actions/runs/42829827443
- Po normalizaci očekáváme **132 prvotních řádků** (3 dokumenty + 2 datasety + 45 otázek + 62 alternativních důkazů + 4 historické souhrny + 16 Hit@k hodnot).
- Grafický relační model obsahuje všech osm tabulek, osm vztahů a úplný soupis atributů; zdrojem je `relational_model.dbml` pro dbdiagram.io. Export do PDF je nutné přiložit k odevzdání.
- Na počítači studenta doporučujeme samostatnou DB `local_rag_school`, nikdy nepouštět tyto skripty nad ChromaDB nebo hlavním RAG.
- Normální formy: `gold_evidence` nyní ukládá jednu (stránka, fragment) kombinaci na řádek a nevyužívá pole jako vícehodnotové atributy.

## Stav nové verze
Osmítabulková varianta je v samostatné větvi `school/postgresql-rag-eight-tables`; předchozí `school/postgresql-rag-seven-tables` je záloha. Migrační SQL je určeno výhradně pro lokální školní DB, nikoliv pro produkční RAG a nikoliv pro školní server VŠB. Nový CI ověřuje jak čisté založení, tak převod původního seedu.
