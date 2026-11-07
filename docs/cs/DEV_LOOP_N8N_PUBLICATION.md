# Publikování ověřených běhů z n8n

[English](../en/DEV_LOOP_N8N_PUBLICATION.md) · [Vývojová smyčka](DEV_LOOP.md)

Tato integrace publikuje **existující úspěšný skutečný BM25 běh**. n8n vybere jeho
registrované UUID, hostitelský publisher zopakuje offline Docker kontroly a HTTP
uzel zobrazí odkaz na draft/existující PR. Nevolá Codex, negeneruje nový návrh,
neaplikuje lokální soubory a neslučuje větve. Generování a opravy řídí LangGraph
v původním CLI běhu.

## Hostitelská služba

Použij čisté worktree s touto integrací. Příklady používají
`D:\AI_roadmap_n8n_publication` a existující experimentální Python prostředí.
GitHub CLI musí být přihlášené na hostiteli, Docker musí běžet a neměnný obraz
checkeru z běhu musí zůstat dostupný. Další přihlášení k modelu není potřeba.

V tomto PowerShell okně obnov **stejný uložený token jako v n8n Header Auth**.
Nový nevytvářej, pokud současně nezměníš tuto credential:

```powershell
$secureToken = Read-Host 'Ulozeny DEV_LOOP_TOKEN' -AsSecureString
$env:DEV_LOOP_TOKEN = [System.Net.NetworkCredential]::new('', $secureToken).Password
Remove-Variable secureToken
```

Spusť službu v okně, které necháš otevřené:

```powershell
cd D:\AI_roadmap_n8n_publication
$labPython = 'D:\AI_roadmap_autonomous\experiments\dev_loop\.venv\Scripts\python.exe'
$runRoot = 'D:\AI_roadmap_autonomous\experiments\dev_loop\.runs\real-bm25'
& $labPython -m experiments.dev_loop.publication_api --runs-root $runRoot --allow-run a5739357-6da4-4118-be18-5c038306e0e9
```

CLI ověří uložené registrované běhy před zahájením naslouchání. Pro nejvýše 20
konkrétních UUID lze opakovat `--allow-run`. Kořenový adresář je nastavení hostitele,
nikoli HTTP položka. Server naslouchá **pouze na `127.0.0.1:8766`**, v jednom workeru,
bez zpracování proxy hlaviček. Nemá přepínač pro ne-loopback adresu. Port 8765 a
původní API výukových úloh zůstávají samostatné; toto workflow je nepotřebuje.
Žádný kontejner, firewall, n8n volume ani RAG index se znovu nevytváří ani nemění.

## Ověření spojení před importem

Ve druhém PowerShell okně:

```powershell
Invoke-RestMethod http://127.0.0.1:8766/health
Get-NetTCPConnection -State Listen -LocalPort 8766 |
    Select-Object LocalAddress,LocalPort,OwningProcess
docker exec rag-lab-n8n node -e "fetch('http://host.docker.internal:8766/health').then(async r=>{console.log(r.status,await r.text());if(!r.ok)process.exitCode=1}).catch(e=>{console.error(e.message);process.exitCode=1})"
```

Očekávej naslouchání na `127.0.0.1` a HTTP 200 **zevnitř existujícího n8n kontejneru**.
`/health` potvrzuje pouze běh služby, nikoli připravenost Dockeru/GitHubu. Nezveřejňuje
registrovaná UUID ani účet. Test spojení neobsahuje token. Docker dokumentuje
[`host.docker.internal`](https://docs.docker.com/desktop/features/networking/networking-how-tos/)
pro komunikaci kontejneru s hostitelem; dosažitelnost tohoto loopback serveru je
přesto nutné ověřit na skutečném Docker Desktop backendu.

Pokud nativní požadavek projde a kontejnerový ne, zastav se u problému spojení.
Nepřepínej na `0.0.0.0`, nepřidávej široké výjimky firewallu a znovu nevytvářej n8n
jako obcházení problému. Zkontroluj Docker Desktop/VPN/proxy směrování; pokud backend
nedosáhne na loopback hostitele, vyber samostatně zkontrolovaný lokální transport.
Vývojové prostředí neověřilo směrování na vlastníkově Docker Desktop.

## Ruční n8n workflow

Přes **Import from File** načti
`experiments/dev_loop/n8n-publication-workflow.json` z tohoto Git worktree.
Workflow není aktivní a obsahuje:

1. **Publish verified run** — ruční trigger, bez plánovače/webhooku.
2. **Choose registered run** — uzel Edit Fields s `task_id: bm25-tokenize-once` a
   přesným úspěšným `run_id`. Měň pouze na jiné UUID povolené hostitelem.
   Nepoužívej `$execution.id`: vybírá se uložený důkaz, nikoli nový generační běh.
3. **Recheck and get draft PR** — jeden HTTP POST na
   `http://host.docker.internal:8766/publications`, bez automatického opakování,
   timeout 900000 ms. Vyber existující Header Auth credential s
   `X-Dev-Loop-Token`. GitHub přihlášení nepatří do n8n ani workflow JSON.

Spusť workflow ručně. U zaznamenaného přijatého výsledku očekávej PR #10 s
`reused_existing_pr: true`, pokud stále odpovídá. Výstup obsahuje `pull_request`,
`draft`, větev/head/base, hash návrhu a výslovné `merge_allowed: false`,
`merged: false`, `local_source_changed: false`, `ci_status: not_checked`.
Surové modelové/testové logy, plné záznamy porovnání, přihlášení a souborové cesty
se v HTTP odpovědi nepřenášejí. Čerstvé důkazy zůstávají v hostitelském
`publication.json` příslušného běhu.

Opakování požadavku zopakuje nezávislý checker a následně použije shodný otevřený
PR; nespotřebuje modelové tokeny. Používají se pouze shodné výsledky. Jiný návrh či
změněný upstream základ publikování zastaví. Pro pouhé ověření n8n spojení není
potřeba živě vytvářet další PR.

## HTTP hranice a chyby

| Metoda/cesta | Účel |
| --- | --- |
| `GET /health` | Minimální stav běhu bez přihlášení |
| `GET /tasks` | Pevný úkol a registrovaná UUID, chráněné tokenem |
| `POST /publications/preview` | Offline náhled s tokenem, bez Dockeru/GitHub zápisů |
| `POST /publications` | Opakované ověření a vytvoření/použití draft PR s tokenem |

POST JSON obsahuje **přesně** `task_id` a `run_id`. Další položky, libovolné příkazy,
prompty, cesty repozitářů/souborů, nepodporované úkoly a neplatná UUID se odmítnou.
Nepovolené UUID vrací 404. Přihlášení se kontroluje před parsováním těla. Požadavky
s browser Origin a neočekávanou Host hlavičkou se odmítají; Content-Type musí být
JSON a vyžaduje se pevná deklarovaná Content-Length nejvýše 1024 bajtů.
Nezpřístupňují se CORS, veřejná dokumentace, webhooky ani libovolné operace.
Loopback nechrání před napadeným lokálním procesem či důvěryhodným kontejnerem;
služba i token mají zůstat součástí lokální laboratoře.

| Stav | Význam / další postup |
| --- | --- |
| 401 | Token chybí nebo se liší od tokenu v okně služby |
| 409 | Jiná HTTP publikace běží; neposílej další |
| 422 | Neplatný vstup, vadný uložený běh či odmítnuté publikování; ověř hostitelské CLI/vzdálený stav |
| 503 | Nedostupná infrastruktura Docker/GitHub; ověř hostitelské CLI |
| 500 | Jiná chyba publikování; před opakováním zkontroluj hostitele i GitHub |

Odpovědi neobsahují surové výjimky, hostitelské cesty ani gh stderr. Po timeoutu či
chybě nejprve zkontroluj existující PR a `publication.json`; vzdálená větev/PR již
mohou existovat. Poté případně opakuj stejné UUID. Automatické opakování není zapnuté.
Před mergem nezávisle zkontroluj diff, CI a bezpečnostní nálezy. Služba nemůže
slučovat, udělovat výjimku z auditu ani schvalovat vlastní výsledek.

## Rozsah ověření

Controller testy pokrývají token, rozsah a registraci běhů, souběh, redakci chyb,
filtrování výsledku, loopback start a strukturu workflow bez volání modelu nebo
GitHub zápisů. Neprokazují živý import n8n ani spojení přes Docker Desktop.
Generování skutečného BM25 je ve výchozím stavu vypnuté. Výslovná registrace na
hostiteli popsaná níže může povolit pevný run-and-publish úkol. Jiné skutečné úkoly
dál vyžadují samostatně zkontrolovaný zdroj, povolené soubory a nezávislý checker.

## Volitelný nový skutečný úkol přes LangGraph a Codex

Jde o **nové generování**, nikoli publikování starého výsledku. Ruční n8n běh může
zavolat Codex přihlášený účtem, spustit dosavadní LangGraph baseline/implement/verify/
repair graf (nejvýše tři pokusy) a následně nezávislý publisher. Spotřebovává limit
účtu ChatGPT/Codex. Přesný počet modelových požadavků a peněžní cena nejsou měřeny;
limit nových úloh není tokenový ani finanční strop. Plánovač a automatické HTTP
opakování nejsou zapnuté.

### Výslovná registrace na hostiteli

Použij worktree s touto funkcí, např. `D:\AI_roadmap_n8n_jobs`. Před restartem zastav
původní službu 8766 přes Ctrl+C v jejím okně. Zachovej uložený `DEV_LOOP_TOKEN`;
pokud v novém okně není nastavený, obnov jej postupem výše.

Vstupní zdroj musí obsahovat zkontrolovaný **původní** BM25 kód. Již vytvořené
`D:\AI_roadmap_chroma_security` je vhodné, dokud jeho zdrojové soubory odpovídají
manifestu. Optimalizované experimentální worktree se záměrně nepřijme.
Ve zdrojovém worktree se nic neupravuje; ingest ani přístup k indexu neprobíhá.
Worker dostává pouze známý veřejný modul, offline checker používá dosavadní
syntetický korpus a 68 regresních testů.

```powershell
cd D:\AI_roadmap_n8n_jobs
$labPython = 'D:\AI_roadmap_autonomous\experiments\dev_loop\.venv\Scripts\python.exe'
$runRoot = 'D:\AI_roadmap_autonomous\experiments\dev_loop\.runs\real-bm25'
$jobRoot = 'D:\AI_roadmap_autonomous\experiments\dev_loop\.runs\n8n-real-jobs'
& $labPython -m experiments.dev_loop.publication_api --runs-root $runRoot --allow-run a5739357-6da4-4118-be18-5c038306e0e9 --source-repo D:\AI_roadmap_chroma_security --jobs-root $jobRoot
```

`--source-repo` výslovně povoluje pevný úkol `bm25-tokenize-once`. Bez něj cesty
`/jobs` neexistují. Zdroj a jeho Git revize se kontrolují při registraci i znovu
před novým během. Hostitelská gh kontrola ověří pevný repozitář a hashe zdroje,
podpůrných modulů a testů jak na aktuálním `main`, tak ve zdrojovém commitu před
voláním modelu. Po mergi PR #10 či změně zkontrolovaného zdroje/testů se úkol zastaví;
neoptimalizuje opakovaně již přijatou změnu. Posun během generování se kontroluje
znovu před publikováním.

Výchozí povolení je **jedna nová úloha na proces služby**. Hostitel může výslovně
nastavit `--max-new-jobs 1..20`. Restart tento limit relace obnoví; nejde o trvalý
ani globální finanční limit. Existující ID zůstávají uložená a restart sám nikdy
nepovoluje jejich nové generování. Používej jeden proces služby; nespouštěj více
instancí nad stejným kořenem jako obcházení zamýšleného limitu.

### Spuštění z n8n

Nejprve ověř `/health` a kontejnerový test spojení výše. Importuj
`experiments/dev_loop/n8n-real-bm25-workflow.json`, vyber dosavadní Header Auth a
spusť celý workflow **jednou**. Obsahuje ruční trigger a jediný HTTP POST na
`http://host.docker.internal:8766/jobs`. Tělo obsahuje přesně `task_id:
bm25-tokenize-once` a UUID odvozené z `$execution.id`. Neobsahuje libovolný prompt,
cestu, plánovač, automatické opakování ani uložené přihlášení.

Nové úplné n8n spuštění vytvoří nové ID a může spotřebovat povolení jedné úlohy.
Opakování stejného ID načte uložené generování; Codex se znovu nevolá. Po timeoutu
nespouštěj druhou novou exekuci jako obnovu. Poznamenej první ID a zkontroluj jeho
stav. Infrastrukturní chyba nevede k neomezeným opravám; původní maximum tří
implementačních pokusů zůstává stejné.

### Výsledky, uložený stav a obnova

Pouze **`status: pr_ready`** potvrzuje dokončení generování i předání do PR. Samotné
HTTP 200 nebo zelený n8n uzel toto nepotvrzuje. Další výsledné stavy:

| Stav | Význam |
| --- | --- |
| `generating` / `publishing` | Uložený průběh dostupný přes dotaz na stav |
| `generation_failed` | Stop kvůli baseline, acceptance, rozsahu nebo limitu pokusů; bez publikování |
| `generation_error` | Neočekávané přerušení generování; model se automaticky neopakuje |
| `publication_blocked` | Návrh uložený; před opakováním stejného ID ověř publisher/PR |
| `pr_ready` | Vybraný PR výsledek je v `publication`; merge se neprovádí |

Odpověď obsahuje `generation_status`, pokusy, počet worker invokací,
`generation_cached` a vybrané údaje publikování. Nepřenáší zdroj, diff, surové logy
ani lokální cesty. `worker_invocations` popisuje původní generování i u odpovědi z
cache; není to počet nových volání vyvolaných daným HTTP požadavkem. Jiný platný
návrh může kolidovat s existujícím PR #10 a publikování zablokovat. Controller tento
PR nepřepíše jen kvůli zelenému výsledku.

Hostitelské soubory jsou v `$jobRoot/requests/<UUID>/request.json` a `state.json`,
vlastní report/návrh a případná účtenka publikování v `$jobRoot/runs/<UUID>/`.
Identita požadavku a adresář vznikají před generováním. Pokud po přerušení chybí
úplný konečný výsledek, vrátí se 409 a je nutná kontrola hostitele; generování se
**nikdy** potichu neopakuje. Uložený dokončený stav `pr_ready` či neúspěšného
generování se vrací bez nového modelu a bez nové GitHub kontroly. Jde o výsledek
tehdejšího běhu, nikoli o aktuální stav PR/CI.

Pokud generování prošlo a selhalo publikování, po kontrole hostitele opakuj **stejné
ID**; znovu může běžet pouze publisher. Příklad v PowerShellu s uloženým tokenem v
daném okně (`<UUID>` nahraď původním ID požadavku):

```powershell
$headers = @{ 'X-Dev-Loop-Token' = $env:DEV_LOOP_TOKEN }
Invoke-RestMethod 'http://127.0.0.1:8766/jobs/<UUID>' -Headers $headers
$body = @{ task_id = 'bm25-tokenize-once'; request_id = '<UUID>' } | ConvertTo-Json
Invoke-RestMethod 'http://127.0.0.1:8766/jobs' -Method Post -Headers $headers -ContentType 'application/json' -Body $body
```

Autentizované `GET /tasks` ukazuje registraci a zbývající povolení v relaci,
`GET /jobs/<UUID>` uložený stav bez generování. Nové ID nad limit dostane 429,
aktivní/přerušený/kolizní běh 409. Neúspěšná kontrola zdroje zastaví postup před
modelem. Diagnostické logy zůstávají na hostiteli. Zablokovaný i úspěšný PR dále
vyžadují nezávislou kontrolu diffu, CI a bezpečnostních nálezů a výslovné schválení
člověkem před mergem.
