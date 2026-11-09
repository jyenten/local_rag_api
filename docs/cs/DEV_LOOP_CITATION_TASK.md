# Registrovaná oprava původu citací

[English](../en/DEV_LOOP_CITATION_TASK.md) · [Ovládání n8n](DEV_LOOP_N8N_CONTROL.md) · [Dohody](DEV_LOOP_POLICY.md)

## Rozsah a důkazy

Úloha `retrieval-citation-provenance` opravuje dvě konkrétní vady: fallback kontext
přiřazuje textům metadata prvního dokumentu a relativní práh může vyřadit všechny
kandidáty se záporným skóre. Neřeší obecnou pravdivost generátoru ani Chroma CVE.

Registraci určuje `experiments/dev_loop/citations/manifest.json`. Výchozí modul
je připnutý na veřejnou revizi `ce9a088373d7dc2ad005af07c4ab09cb2df7b9fd` a jeho
obsahový hash. Lokální i vzdálený zdroj musí přesně odpovídat; stejné bajty mohou
pocházet i ze staršího worktree `f58f6f2`. Žádné PDF, index ani TEST gold evidence.

| Část výsledku | Kdo ji připravuje | Omezení |
|---|---|---|
| `rag_api_project/app/retrieval.py` | Model | Pouze těla `Retriever.rerank_lines` a `Retriever.build_context`; importy, podpisy, konstruktor, search a pomocné funkce chrání AST kontrola |
| `rag_api_project/tests/test_retrieval_citations.py` | Hostitelský controller | Pevný přezkoumaný soubor z checkeru, ověřený SHA-256; model jej nedostává k úpravám |

Baseline spouští 3 existující kontrakty. Acceptance spouští všech 15 případů:
záporná/nulová/kladná skóre, správný druhý dokument i více zdrojů, deduplikaci,
limity, prázdnou evidenci a zachování metadat/návratového tvaru. Samostatný proces
navíc změří dva booleanové probe výsledky před/po. Checker načítá skutečný celý
modul s nahrazenými konstruktory Chroma/modelů; nevytváří index ani nestahuje váhy.
Jde o syntetické regresní důkazy, nikoli o měření přesnosti na soukromém korpusu.

Pevný test se předá do aplikačního PR spolu s návrhem. Publisher dovolí právě dva
soubory a jediný nový commit: změněný modul a nově přidaný přesný test. Opakovaná
publikace nepřepisuje větev; změna zdroje, existující cílový test či konkurenční PR
vede k zastavení. Před publikací se zopakuje baseline i acceptance v původním
neměnném Docker image. Model nesmí získat GitHub přihlášení.

## Jednorázová aktivace

Nejdřív zkontroluj registraci/PR, potom zastav controller Ctrl+C. V čistém stabilním
worktree aktualizuj stejnou feature větev; n8n kontejner zůstává stejný:

```powershell
cd D:\AI_roadmap_n8n_publication
git status -sb
git fetch origin
if ($LASTEXITCODE -ne 0) { throw "Git fetch selhal." }
git switch --detach origin/feat/dev-loop-n8n-control
if ($LASTEXITCODE -ne 0) { throw "Přepnutí větve selhalo." }
```

Při chybě nepokračuj, nepoužívej force/reset. Lokální profil a přihlášení zachovej.
Připrav pouze nový checker image (stávající Codex image/auth volume se používají dál):

```powershell
docker build -t local-rag-citation-check:1 .\experiments\dev_loop\citations
if ($LASTEXITCODE -ne 0) { throw "Build checkeru selhal." }
```

Pokud build selže, generování nespouštěj. Výběr úlohy je jednorázové výslovné
hostitelské nastavení. Tento příkaz zachová cesty, port, povolené historické běhy
i limit jobů; nezapisuje token a původní profil změní až po úspěšné kontrole:

```powershell
$labPython = 'D:\AI_roadmap_autonomous\experiments\dev_loop\.venv\Scripts\python.exe'
& $labPython -m experiments.dev_loop.service select-task retrieval-citation-provenance
if ($LASTEXITCODE -ne 0) { throw "Výběr úlohy selhal." }
& $labPython -m experiments.dev_loop.service check
if ($LASTEXITCODE -ne 0) { throw "Kontrola profilu selhala." }
& $labPython -m experiments.dev_loop.service start
```

Po každé chybě zastav a vyřeš ji před dalším příkazem. Verze profilu 1 zůstává
podporovaná. Výběr přejde na verzi 2; stále je povolen pouze jeden hostem vybraný
typ nových jobů a původní limit (standardně 1 nový job na proces), ne jeden limit
pro každý řádek katalogu. Stávající přerušené identity se nikdy neregenerují.
Výběr se projeví až při příštím spuštění služby, nikoli změnou běžícího procesu.

## Jeden skutečný běh přes n8n

1. Aktualizuj/importuj `n8n-control-workflow.json`, vyber stejné credentials. Přibyla
   pevná volba `retrieval-citation-provenance`; import žádné tajemství neobsahuje.
2. `catalog`: nová úloha musí mít `generation_configured: true`. Historický BM25
   zůstává dostupný pro povolené reporty, nové BM25 joby tímto profilem povolené nejsou.
3. Vyber novou úlohu a `generate`, UUID nech prázdné. Zkontroluj dvě povolené cesty,
   dvě editovatelné metody, hash pevného testu, 15 acceptance případů a max. 3 pokusy.
4. Teprve **Schválit** spustí baseline, případnou generaci a offline ověření.
   Výsledek má být `review_ready` / `awaiting_approval`, žádný PR se ještě nevytváří.
5. Se stejnou úlohou a UUID otevři `report`. Před opravou jsou oba probe výsledky
   false, po ověřené opravě true. To není nové měření BM25 rychlosti.
6. Po prohlédnutí diffu zvol `publish` se stejným UUID a samostatně schval plán.
   Tato akce nevolá model, znovu ověřuje a vytvoří/použije draft PR do `main`.
   Aplikační CI pak ověřuje také nový trvalý regresní soubor. Merge schvaluješ zvlášť.

Při timeoutu nejdřív `status` se stejným UUID; nepoužívej náhradní ID, restart ani
vyšší limit k obcházení stavu. Starý kombinovaný `/jobs` endpoint je při výběru
této úlohy vypnutý (410); používá se pouze oddělený schvalovaný control workflow.
Zrušení plánu nepouští model ani publikaci. Schvalovací formulář čeká nejvýše 10
minut, HTTP akce 900 sekund a workflow má celkový limit 45 minut.

## Ověření registrace

Unit/contract testy používají jasně označenou lokální referenci a fake GitHub/model,
nikoli skutečný Codex. GitHub Actions job `citation-checker` navíc postaví image a
živě ověří: původní baseline projde, původní kód neprojde acceptance, reference
projde acceptance. Příkaz pro stejné dobrovolné Docker ověření:

```powershell
$env:DEV_LOOP_CITATION_DOCKER_TESTS = '1'
& $labPython -m pytest experiments/dev_loop/tests/test_citations.py -k test_docker_citation_checker -q -p no:cacheprovider
Remove-Item Env:DEV_LOOP_CITATION_DOCKER_TESTS
```

Toto ověření nevolá model a nepublikuje PR. Chroma audit zůstává nezávislý a jeho
červený výsledek tímto testem není prominutý. Skutečný modelový běh a uživatelův
Docker/n8n import se vykazují samostatně od ověření registrace.
