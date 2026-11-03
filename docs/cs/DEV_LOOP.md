<a id="top"></a>

# Experiment: n8n, LangGraph a Codex

[English](../en/DEV_LOOP.md#en) · [Dokumentace](../README.md)

<a id="cz"></a>

## Obsah

- [Rozsah](#rozsah)
- [Spuštění](#spuštění)
- [n8n](#n8n)
- [Skutečný Codex](#skutečný-codex)
- [Report 20 běhů](#report-20-běhů)
- [Veřejná větev a bezpečnost](#veřejná-větev-a-bezpečnost)
- [Docker izolace dema](#docker-izolace-dema)
- [Codex v Dockeru přes ChatGPT](#codex-v-dockeru-přes-chatgpt)
- [Kontrolovaný test opravy](#kontrolovaný-test-opravy)
- [Druhá úloha: build-search-request](#druhá-úloha-build-search-request)
- [Dva soubory: build-search-package](#dva-soubory-build-search-package)
- [Jednorázový test Ollamy](#jednorázový-test-ollamy)
- [Ověření a omezení](#ověření-a-omezení)

## Rozsah

Laboratoř žije v `experiments/dev_loop/` na větvi `experiment/autonomous-dev`.
Příkazy se spouštějí z **kořene repozitáře**, nikoli z `rag_api_project/`.
RAG API, produkční závislosti, korpus, indexy a evaluace se nemění.

První pevně zadaný úkol `normalize-question` řeší odstranění okolních mezer
a odmítnutí prázdného dotazu. Každý běh kopíruje výchozí `question.py` do vlastní
složky `.runs/<request_id>/workspace/`, kde vytvoří samostatný Git kořen bez
commitu a bez remote. Agent upravuje tuto kopii, nikoli RAG aplikaci.

| Nástroj | Odpovědnost |
| --- | --- |
| n8n | Ruční zahájení, jedno HTTP volání, zobrazení výsledku |
| LangGraph | Baseline, implementace, ověření, rozhodnutí o opravě a konci |
| Codex CLI | Úprava povoleného souboru; žádný commit, staging ani push |
| pytest | Pevné kontrolní testy uložené mimo pracovní složku agenta |

Baseline ověřuje dva původní případy; čtyři nové požadavky při něm záměrně přeskakuje.
Po každé úpravě se musí provést všech šest kontrol bez přeskočení. Úspěch vyžaduje
návratový kód 0 **a** úplný JUnit výsledek. LangGraph povolí první implementaci
a nejvýše dvě opravy. Chyba prostředí, timeout nebo nepovolená změna běh ukončí.

Demo používá skutečný LangGraph a skutečný pytest, ale změny souboru provádí
deterministický `DemoWorker`: první pokus selže a druhý projde. Model se nevolá.

## Spuštění

Python 3.11+, Git. V PowerShellu vytvoř oddělené prostředí:

```powershell
python -m venv experiments/dev_loop/.venv
$labPython = (Resolve-Path experiments/dev_loop/.venv/Scripts/python.exe).Path
& $labPython -m pip install -r experiments/dev_loop/requirements.txt
& $labPython -m experiments.dev_loop --backend demo
```

Na Linuxu/WSL použij `experiments/dev_loop/.venv/bin/python`.
Výsledné JSON obsahuje `backend`, `status`, `attempts`, průchod uzly `trace`,
výstupy testů a `diff`. Demo má skončit `review_ready` po dvou pokusech.
Každé nové spuštění CLI má nové UUID. Opakování s `--request-id <UUID>` načte
dokončený výsledek bez další práce. Jiný backend se stejným UUID je konflikt.

`review_ready` znamená pouze splnění kontrol této malé úlohy; stále vyžaduje
lidskou kontrolu diffu a neznamená schválení integrace do RAG.

## n8n

Spusť lokální HTTP službu. Token nedávej do Git souborů ani do exportu workflow:

```powershell
$env:DEV_LOOP_TOKEN = & $labPython -c "import secrets; print(secrets.token_urlsafe(32))"
Set-Clipboard $env:DEV_LOOP_TOKEN
& $labPython -m experiments.dev_loop --backend demo --serve
```

V n8n:

1. Importuj `experiments/dev_loop/n8n-workflow.json`.
2. V uzlu **Run LangGraph loop** vytvoř přihlašovací údaj typu **Header Auth**:
   název hlavičky `X-Dev-Loop-Token`, hodnota z `DEV_LOOP_TOKEN`.
   Předchozí příkaz ji zkopíroval do schránky. Nově otevřené PowerShell okno
   tuto proměnnou nepřebírá.
3. Ověř URL služby. Výchozí `http://127.0.0.1:8765/runs` platí,
   pokud n8n běží přímo na stejném hostiteli.
4. Spusť **Execute workflow** a otevři výstup HTTP uzlu.

Workflow je po importu neaktivní, používá ruční trigger a nemá vlastní retry.
UUID odvozuje od číselného `$execution.id` dané n8n instance (do 12 číslic).
Backend vybírá provozovatel při startu služby, nikoli příchozí požadavek.
API přijímá pouze UUID a známé `task_id`; nepřijímá příkazy ani volné prompty.

Jestli n8n běží v Docker Desktopu, jeho `127.0.0.1` označuje kontejner.
Změň URL na `http://host.docker.internal:8765/runs` a službu spusť s
`--host 0.0.0.0 --allow-non-loopback` v důvěryhodné lokální síti. Na Linuxu může být potřeba vlastní
nastavení host-gateway. n8n Cloud vyžaduje jinak dosažitelnou službu;
veřejné hostování tento experiment nenastavuje.

HTTP požadavek čeká na celý výsledek, timeout workflow je 420 sekund.
Jedna instance služby provádí současně jeden běh; další požadavek dostane 409.
Výsledek je atomicky uložen do `.runs/<UUID>/result.json`. Stejné UUID se znovu
neprovede ani po restartu služby. Nedokončený běh vrátí 409; před případným novým
UUID nejprve zkontroluj jeho pracovní složku. Dvě různá UUID znamenají dvě úlohy.

## Skutečný Codex

Pro nové lokální běhy použij [Codex v Dockeru přes ChatGPT](#codex-v-dockeru-přes-chatgpt).
Následující původní hostitelský adaptér spouští i kandidátní pytest přímo na hostiteli;
není totožný s Docker profilem. Jeho konfigurace používá CLI na tomtéž hostiteli:

```powershell
codex --version
codex login status
& $labPython -m experiments.dev_loop --backend codex
```

Pro n8n ukonči demo službu a spusť ji s `--backend codex --serve`.
S novým backendem použij nové UUID / nové provedení workflow.
Adaptér spouští `codex --ask-for-approval never exec --sandbox workspace-write`
s `--cd <workspace> --json -`. Zadání i relevantní chyby předává přes stdin;
příkazy se neinterpolují do shellu. Použije model a autentizaci nastavené v CLI.
Kontroluje návratový kód a událost `turn.completed`; neúspěch není důkaz opravy.

Každé volání Codexu má limit 90 sekund, pytest 20 sekund. Při timeoutu runner
ukončí procesový strom; na Windows k tomu používá `taskkill`.
JSONL a stderr Codexu zůstávají v lokální složce běhu. Token HTTP služby se
workeru nepředává a z testovacího prostředí se odstraňují běžné názvy tajných hodnot.

## Ověření a omezení

```powershell
& $labPython -m pytest experiments/dev_loop/tests -q -p no:cacheprovider
```

- Ověřeno: skutečný LangGraph/pytest demo běh, oprava po selhání,
  limit pokusů, chyby infrastruktury, nepovolené změny, úplnost testů,
  autentizované API a opakované požadavky po restartu.
  Před doplněním Docker adaptéru měla sada laboratoře včetně reportu 42 passed na Pythonu 3.12.14
  (31. 10. 2026).
- Transport Codex CLI je testovaný s náhradním procesovým výsledkem.
  Živý Codex ani import a provedení v n8n nebyly v tomto prostředí ověřeny:
  samostatný Codex CLI a n8n tu nejsou dostupné.
- Neměnil se RAG kód; jeho původní testovací sada se v tomto kroku nespouštěla.
- Žádné commity, push, PR, automatický merge ani aplikování výsledku do RAG.
- Kontrola rozsahu změn je audit, ne samostatný bezpečnostní sandbox.
  Testovaný Python kód běží jako lokální proces. Pro nedůvěryhodné úlohy je
  potřeba izolovaný runner; tato malá úloha není obecná veřejná vývojová služba.
- Limity pokusů a času neznamenají pevný finanční limit; živý backend může
  spotřebovat placené využití. Detailní události zůstávají v JSONL.
- `.runs/` je ignorované Gitem. Pro pokračování experimentu zachovej jeho
  obsah; smazáním se ztratí historie i ochrana před opakováním daných UUID.

Zdroje: [Codex non-interactive](https://learn.chatgpt.com/docs/non-interactive-mode),
[Codex CLI](https://learn.chatgpt.com/docs/cli/reference),
[LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api),
[n8n HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/).

## Report 20 běhů

Nejde o zvýšení limitu oprav: dávka znamená 20 nezávislých úloh, každou z původní
kopie souboru, nejvýše se třemi pokusy. Instaluj také závislost pro graf:

```powershell
& $labPython -m pip install -r experiments/dev_loop/requirements-report.txt
& $labPython -m experiments.dev_loop --backend demo --cycles 20 --report-dir experiments/dev_loop/.runs/reports/demo-20
```

Cílová složka musí být nová. Vznikne `batch.json`, graf `cycles.png` a samostatný
`report.html` s vloženým grafem, tabulkou běhů a bezpečnostními omezeními.
Při chybě infrastruktury, baseline nebo rozsahu změn se celá dávka zastaví.
Shrnutí neobsahuje surové logy ani pracovní cesty; složku `runs/` nezveřejňuj.

Naměřeno 31. 10. 2026: 20/20 `review_ready`, 40 pokusů, 20 oprav,
celkem 20,819 s, medián 0,976 s, maximum 1,476 s. Každý běh měl návratové kódy
ověření `[1, 0]`. Úspěch na první pokus: 0/20. Model nebyl volán.
Demo první chybu i opravu předepisuje; nejde o měření schopností Codexu,
kvality RAG ani průchodu přes n8n. Doby zahrnují režii testů, nikoli latenci modelu.

Živý backend lze vybrat přes `--backend codex`; 20 úloh znamená až 60 volání workeru.
Tokeny a cenu zatím neměříme a limit pokusů není finanční strop.

## Veřejná větev a bezpečnost

Veřejná větev je čitelná stejně jako repozitář; nedává veřejnosti právo zápisu.
Větev ani worktree neomezují procesy. Nový kód zůstává bez commitu a push.

Implementováno: pevný seznam úloh, token API (nejméně 24 znaků), loopback jako
výchozí adresa, explicitní souhlas parametrem pro jinou adresu, jeden běh v procesu,
opakování dokončeného UUID bez nové práce, limity času/pokusů/dávky a audit souborů.
Procesy se spouštějí bez shellu, přes omezený seznam proměnných prostředí;
testy mají vlastní HOME. Adaptér Codexu požaduje `workspace-write` a vypnutou síť
příkazů; jeho skutečné vynucení zde nebylo živě ověřeno.

**Výchozí režim `--isolation host` nemá izolaci kandidátního Pythonu na úrovni OS.** Testy běží s oprávněními
uživatele a mohou číst hostitele nebo použít síť. Testy mimo pracovní složku,
hash souborů a JUnit nejsou ochrana před úmyslným podvržením.
Sandbox Codexu se nevztahuje na pytest spuštěný naším programem.

Před obecnými nebo nedůvěryhodnými úlohami je třeba jednorázový izolovaný runner
pro worker i testy, oddělená autentizace modelu, testy jen pro čtení, omezená síť
a limity CPU/paměti/disku. Chybí globální finanční strop, rate limiting,
limit HTTP vstupu a omezení zachyceného procesového výstupu v paměti.
Zámek API není distribuovaný a nechrání více serverových procesů.

Lokální kopie obsahuje workflow Gitleaks, pip-audit a dependency review;
CI spouští testy RAG a audit závislostí RAG, ne tuto laboratoř.
Aktuální výsledky CI, rulesets ani vynucení ochrany větví tento krok nepotvrzuje
a nastavení GitHubu nemění. Část workflow používá pohyblivé tagy akcí.
Před další automatizací ověř vyžadované kontroly a lidskou kontrolu změn.

Nezapojovat veřejné issues, komentáře nebo cizí PR do privilegovaného běhu.
GitHub varuje před nedůvěryhodným kódem na self-hosted runnerech veřejných
repozitářů a před spuštěním kódu cizího PR přes `pull_request_target` se secrets.
Lokální tokeny, auth soubory a `.runs/` nepublikovat; `.gitignore` není
bezpečnostní bariéra a nezabrání zveřejnění již sledovaných souborů.

Zdroje: [GitHub Secure use](https://docs.github.com/en/actions/reference/security/secure-use),
[pull_request_target](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target),
[Codex security](https://developers.openai.com/codex/security/).

## Docker izolace dema

Připravený volitelný profil `--isolation docker` používá odlišný backend
`demo-docker` pro pevnou demo úlohu. Živý `--backend codex --isolation docker`
má vlastní síťový worker a auth volume; viz [návod níže](#codex-v-dockeru-přes-chatgpt).
Níže popsaný offline profil workeru platí pro demo, offline profil checkeru pro oba backendy.

Hostitelský LangGraph přijímá z workeru pouze JSON s textem `question.py`.
Zdrojový kód se nikdy neimportuje na hostiteli. Každá implementace i každý
pytest dostanou vlastní nový kontejner, bez sdíleného zapisovatelného disku.
Kontrolní testy jsou zabudované do image v `/opt/dev-loop/checks`, nikoli
kopírované z pracovního prostoru. Do kontejneru se nepřipojuje repozitář,
osobní složky ani Docker socket. Žádné tokeny ani hostitelské proměnné prostředí
se do něj nepředávají. Docker CLI na hostiteli stále vyžaduje důvěryhodného správce.

Profil: síť `none`, read-only root filesystem, UID/GID `10001:10001`,
`cap-drop ALL`, `no-new-privileges`, 1 CPU, 256 MiB RAM bez dalšího swapu,
64 procesů, tmpfs `/work` 32 MiB a `/tmp` 16 MiB s `noexec,nosuid,nodev`.
Stdin a stdout přenášejí pouze data. Kandidát má nejvýše 64 KiB; zachycený
stdout/stderr Docker attach má společný limit 256 KiB. Attach má timeout 30 s;
Docker create, inspect a cleanup mají každý 10 s. Po úspěchu, chybě i timeoutu
se provede `docker rm --force` daného kontejneru. Selhání úklidu zastaví běh.
Není žádný automatický přechod na hostitelský pytest nebo worker.

Build kontext obsahuje pouze laboratoř; `.dockerignore` vybírá nutné soubory.
Base tag `python:3.11-slim-bookworm` ani tranzitivní Python závislosti zatím
nejsou připnuté digestem/lockfilem. Pro jeden běžící runner se image vyhodnotí
jednou na konkrétní `sha256` ID; report ho zaznamená jako `runner_image`.

Z kořene `D:\AI_roadmap_autonomous` nejdřív vytvoř image:

```powershell
docker build -t local-rag-dev-loop:1 -f experiments/dev_loop/docker/Dockerfile experiments/dev_loop
```

Potom proveď skutečné Docker testy. Nastavení proměnné platí pro toto PowerShell okno:

```powershell
$labPython = ".\experiments\dev_loop\.venv\Scripts\python.exe"
$env:DEV_LOOP_DOCKER_TESTS = "1"
& $labPython -m pytest experiments/dev_loop/tests/test_docker.py -q -p no:cacheprovider
Remove-Item Env:DEV_LOOP_DOCKER_TESTS
```

Tři opt-in testy ověřují celou opravnou smyčku, zákaz čtení syntetického
hostitelského souboru/předání tokenu/zápisu do kontrol/sítě, nastavené limity
cgroups a tmpfs a timeout nekonečného
kandidáta. Bez opt-in se skutečný Docker nespouští a tyto tři testy jsou skipped.
Řídicí testy neprokazují vynucení kernelových omezení. V prostředí autora není
Docker CLI, proto zde image ani tyto tři testy nebyly živě spuštěné.

Jeden běh a dávka:

```powershell
& $labPython -m experiments.dev_loop --backend demo --isolation docker
& $labPython -m experiments.dev_loop --backend demo --isolation docker --cycles 20 --report-dir experiments/dev_loop/.runs/reports/docker-demo-20
```

Očekávaný stav je `review_ready`, dva pokusy, `backend: demo-docker`,
`isolation: docker`, `checker_isolation: docker` a vyplněné `runner_image`.
Jeden úspěšný běh vytvoří postupně pět kontejnerů: baseline, worker, testy,
worker, testy. Režie Dockeru se započítává do doby běhu.

Pro n8n zastav starou API službu přes Ctrl+C. V PowerShellu, kde je stále
nastavený **stejný** `DEV_LOOP_TOKEN`, spusť službu s novým přepínačem:

```powershell
& $labPython -m experiments.dev_loop --backend demo --isolation docker --serve --host 0.0.0.0 --allow-non-loopback
```

URL v n8n i Header Auth se nemění. `/health` nyní ukazuje `demo-docker` a obě
izolace `docker`; health sám kontejner nespouští a nepotvrzuje dostupnost image.
Veřejné spouštění nadále nepovolovat. Kontejnery sdílejí kernel Docker hostitele
a nejsou VM. Kandidát může ovlivnit vlastní pytest proces; úplný JUnit není
důkaz odolnosti proti úmyslnému podvržení testů. Profil neřeší globální finanční
limit, distribuovaný zámek API, veřejné vstupy ani vynucení GitHub rulesets.

Zdroje: [Docker run](https://docs.docker.com/engine/containers/run/),
[Resource constraints](https://docs.docker.com/engine/containers/resource_constraints/),
[None network](https://docs.docker.com/engine/network/drivers/none/).

## Jednorázový test Ollamy

Pro malou místní zkoušku `qwen3.5:4b-q4_K_M` použij z kořene worktree:

```powershell
& .\experiments\dev_loop\.venv\Scripts\python.exe -m experiments.dev_loop.ollama_probe
```

Skript nejprve ověří původní fixture Docker baseline kontrolami; při chybě Dockeru
Ollamu nevolá. Potom provede jediný požadavek na `http://127.0.0.1:11434/api/generate`
bez hostitelského HTTP proxy, s `think: false`, kontextem 4096 a limitem 256 tokenů.
Generování má timeout 90 sekund. Není potřeba znovu buildovat Docker image.

Každý pokus má vlastní `.runs/ollama-probe/<UUID>/`: `request.json`, surovou odpověď
`response.json`, případný `candidate/question.py` a atomicky uložený `report.json`.
Odpověď se ukládá hned. Prázdný kód, neukončená odpověď, neplatný Python nebo
chybějící top-level funkce `normalize_question` vedou na `invalid_model_output`;
kandidátní soubor se v takovém případě nevytvoří. Zdroj se na hostiteli pouze parsuje
přes AST, nikdy se nespouští. Validní zdroj se ukládá přesně v UTF-8 bez ručních oprav,
odstraňování Markdownu nebo závislosti na proměnných PowerShellu.

Následně běží stejných šest acceptance kontrol v Dockeru. `review_ready` znamená,
že prošly; `verification_failed` značí selhání kontrol. `generation_requests`
počítá pokusy o HTTP generování, `model_duration_s` dobu vrácenou Ollamou a
`total_duration_s` celý pokus včetně Dockeru. Nejde o backend n8n/LangGraph smyčky:
je to samostatná zkouška bez opravné smyčky. Původní prázdné kandidáty nepřepisuje.
Není zapojený Codex ani přihlášení ChatGPT. Změny se neaplikují do RAG a necommitují.

[↑ Zpět nahoru](#top)


## Codex v Dockeru přes ChatGPT

Tento backend propojuje stávající LangGraph smyčku s opravdovým `codex exec`.
Používá pevný úkol `normalize-question`, nejvýše tři pokusy a backend `codex-docker`.
Codex vrací JSON s jediným polem `code`; hostitel přijímá pouze UTF-8 text do
`question.py` (nejvýše 64 KiB, syntakticky platná definice požadované funkce).
Kandidátní Python se na hostiteli neimportuje ani nespouští. Správnost určuje
stejných šest nezávislých testů v odděleném offline kontejneru. Vadný protokol,
chyba CLI, autentizace nebo úklidu zastaví běh bez fallbacku na hostitele.

Image obsahuje připnutý Codex CLI `0.162.1`. Model volí výchozí konfigurace této
verze; uživatelský config, rules a session historie se nepřenášejí. CLI běží s
`--ignore-user-config --ignore-rules --ephemeral --sandbox read-only`, bez shell
nástrojů, aplikací, pluginů, memories, dalších agentů a webového vyhledávání.
Kontrolér odmítá i zaznamenané volání nástroje. To je úzce vymezený generátor
kódu s opravnou smyčkou, nikoli obecný agent s terminálem.

Nejprve v PowerShellu sestav samostatný image. Stávající checker image
`local-rag-dev-loop:1` musí být také dostupný; jeho rebuild tento doplněk nevyžaduje.
Node/npm na Windows nepotřebuješ, jsou pouze při buildu uvnitř image.

```powershell
cd D:\AI_roadmap_autonomous
$labPython = '.\experiments\dev_loop\.venv\Scripts\python.exe'
& $labPython -m pytest experiments/dev_loop/tests -q -p no:cacheprovider
docker build -t local-rag-codex:0.162.1 -f experiments/dev_loop/docker/Codex.Dockerfile experiments/dev_loop
```

Přihlášení ve Windows se do Linux kontejneru automaticky nepřenáší. Pro tento
profil se jednou přihlas přímo v kontejneru; nekopíruj osobní Windows auth soubory.
V ChatGPT bezpečnostním nastavení nejprve povol device code login, pak spusť:

```powershell
docker volume create local-rag-codex-auth
docker run --rm -it --cap-drop ALL --security-opt no-new-privileges=true --mount type=volume,source=local-rag-codex-auth,target=/home/node/.codex local-rag-codex:0.162.1 -c cli_auth_credentials_store=file -c forced_login_method=chatgpt login --device-auth
```

Otevři vypsaný odkaz v prohlížeči a potvrď jednorázový kód. Kód ani auth soubory
nikam neposílej. Ověř metodu přihlášení, pak spusť jeden skutečný úkol:

```powershell
docker run --rm --cap-drop ALL --security-opt no-new-privileges=true --mount type=volume,source=local-rag-codex-auth,target=/home/node/.codex local-rag-codex:0.162.1 -c cli_auth_credentials_store=file -c forced_login_method=chatgpt login status
& $labPython -m experiments.dev_loop --backend codex --isolation docker
```

Očekávej `backend: codex-docker`, `isolation: docker`, `checker_isolation: docker`,
`authentication: chatgpt`, dva různé hashe `worker_image` a `runner_image` a při
úspěchu `status: review_ready`, šest acceptance testů. Počet pokusů určí model,
není předepsaný jako u dema. `worker_attempts` ukládá pouze dokončení, hash kódu
a počty tokenů hlášené CLI. Chybějící telemetrie je `null`, nikoli nula. Cached
input je podmnožina input tokenů; nesčítá se k němu. `model_cost` zůstává `null`;
metriky neurčují zbývající limit účtu ani cenu. V další dávce lze měřit 1–20 cyklů,
ale nejprve ověř jeden úkol. Jedna invokace CLI nemusí znamenat jedno volání modelu.

Pro n8n ukonči předchozí Uvicorn pomocí Ctrl+C. Ve stejném PowerShell okně musí
být nastaven tvůj uložený `DEV_LOOP_TOKEN`; jeho hodnotu neměň. Spusť jednu instanci:

```powershell
& $labPython -m experiments.dev_loop --backend codex --isolation docker --serve --host 0.0.0.0 --allow-non-loopback
```

URL `http://host.docker.internal:8765/runs` a Header Auth zůstávají stejné. V uzlu
HTTP Request nastav Timeout na `900000` ms (aktualizovaný import má tuto hodnotu);
změna souboru sama neupraví již importovaný workflow. Spusť nové provedení s novým
UUID. `/health` ukáže backend a izolaci, dostupnost image či přihlášení ale netestuje.

Worker má limit 90 s, 768 MiB RAM bez dalšího swapu, 1 CPU, 128 PID, read-only root,
odebrané capabilities, no-new-privileges a tmpfs `/work` 16 MiB, `/tmp` 64 MiB.
Je neprivilegovaný UID 1000. Nemá mount repozitáře, osobních složek ani Docker socketu.
Jediný mount je vlastní zapisovatelný auth volume pro obnovu ChatGPT tokenů; volume
obsahuje tajné hodnoty a patří pouze tomuto lokálnímu workeru. Nemá pevný limit
velikosti; obsah se nesmí publikovat. Checker toto volume ani přihlašovací údaje
nedostane, zachovává `--network none` a UID 10001. Worker používá síť `bridge`:
**odchozí provoz není omezen na domény OpenAI**. Nejde o ochranu pro cizí veřejné
úlohy ani veřejný CI runner. Docker správce a image musí být důvěryhodní.

Image ID se zmrazí po prvním inspect pro životnost workeru. Základní image a npm
tranzitivní závislosti nejsou uzamčené digestem. Docker attach má limit 256 KiB
kombinovaného výstupu, create/inspect/cleanup po 10 s. I po timeoutu se provede
`docker rm --force`; chyba úklidu nedovolí zapsat kandidáta. Surové autentizované
CLI logy se neposílají do n8n ani souhrnného reportu.

Ověření zde pokrývá náhradní transport, validaci protokolu, oddělení přístupů,
limity, úklid, zapojení smyčky a report. Docker Engine a přihlášené skutečné volání
nového image se musí ověřit na tvém počítači; automatické testy je nepředstírají.
Dosavadní úspěšný Windows CLI test potvrzuje přihlášení a odpověď, nikoli tento nový
Docker profil. Změny se neaplikují do RAG; commit, staging ani push se neprovádí.

Zdroje: [Autentizace a device login](https://learn.chatgpt.com/docs/auth),
[Strukturovaný výstup CLI](https://learn.chatgpt.com/docs/non-interactive-mode),
[Konfigurace shell nástrojů](https://learn.chatgpt.com/docs/config-file/config-reference).

### Chyba spojení při device login

`error sending request ... /deviceauth/usercode` samo o sobě neurčuje příčinu.
Image výslovně instaluje `ca-certificates`, nastavuje `SSL_CERT_FILE` a při buildu
ověřuje neprázdný systémový CA bundle. Původní varianta toto nezajišťovala.
Po opravě Dockerfile znovu sestav image stejným build příkazem a opakuj device
login; auth volume se nemaže. Pokud chyba zůstane, ověř HTTPS bez credentials:

```powershell
docker run --rm --entrypoint curl local-rag-codex:0.162.1 --connect-timeout 10 --max-time 20 -sS -o /dev/null -w "HTTP=%{http_code}" https://auth.openai.com/api/accounts/deviceauth/usercode
```

GET může dostat například 400, 403 nebo 405; samotná HTTP odpověď znamená, že se
navázalo HTTPS spojení, nikoli že je device login povolený. `curl` chyba 6 ukazuje
na DNS, 7 na spojení, 28 na timeout a 60 na ověření certifikátu. Přesnou příčinu
urči podle výstupu, ne podle obecné CLI hlášky. Firemní proxy může vyžadovat vlastní
CA bundle (`CODEX_CA_CERTIFICATE` dle OpenAI dokumentace); nevypínej kontrolu TLS.
Docker Engine ani živé připojení nového image zde nejsou dostupné k ověření.


## Kontrolovaný test opravy

Dávka, ve které všech 20 prvních pokusů uspěje, neověří opravnou větev. Samostatný
scénář ji ověří řízeným vložením známé chyby. První implementaci vrátí existující
offline Docker demo worker: prázdnotu kontroluje před `strip()`, takže whitespace
neodmítá. Skutečný checker tuto chybu ověří původními testy. LangGraph pak předá
nezměněný výstup neúspěšných testů a chybný zdroj skutečnému Docker Codex workeru.
Další kontrola běží opět odděleně, bez sítě a přihlašovacích údajů.

Nejde o spontánní chybu modelu ani o úspěšnost oprav v různorodých úlohách.
Výsledek musí označovat `measurement: controlled-repair`; první kandidát má
původ `scripted-demo-docker`. Limit zůstává tři implementační pokusy celkem:
jedna vložená chyba a nejvýše dvě invokace Codex workeru. Počet skutečných
požadavků na model zůstává neměřený. Chyba infrastruktury smyčku zastaví.

Použiješ stávající přihlášení v `local-rag-codex-auth`, worker image
`local-rag-codex:0.162.1` a checker image `local-rag-dev-loop:1`. Není třeba měnit
token n8n, znovu se přihlašovat nebo buildovat image. V PowerShellu spusť:

```powershell
cd D:\AI_roadmap_autonomous
& .\experiments\dev_loop\.venv\Scripts\python.exe -m pytest experiments/dev_loop/tests -q -p no:cacheprovider
& .\experiments\dev_loop\.venv\Scripts\python.exe -m experiments.dev_loop.repair_probe
```

Při úspěšné opravě prvním voláním Codexu očekávej:

- baseline: 2 passed, 4 skipped;
- vložený chybný kandidát: 3 failed, 3 passed;
- oprava Codexem: 6 passed;
- `status: review_ready`, `attempts: 2`, `injected_attempts: 1`;
- `codex_worker_invocations: 1`, `codex_completed_invocations: 1`;
- `repair_path_observed: true`, `probe_passed: true`.

Toto jsou očekávané výsledky, nikoli tvrzení o již provedeném živém běhu. Pokud
první oprava selže, může následovat ještě jedna; úspěch není předepsaný. Samotný
`review_ready` bez zaznamenaného selhání a navazující opravy experiment nesplní:
CLI vrátí úspěšný exit code jen s `probe_passed: true`.

Každý pokus má nové UUID pod `.runs/repair-probe/`. Výsledek `result.json` obsahuje
původ vložené chyby, tokeny pouze skutečného Codex workeru, oba druhy počtů pokusů
a hashe vstupů oprav. Kopie původního chybného kandidáta je `injected-question.py`
vedle výsledku, mimo auditovaný workspace. Její `code_sha256` odpovídá přesným
bajtům souboru; `prompt_source_sha256` odpovídá UTF-8 textu předávanému Codexu
(s normalizací konců řádků). `repair_inputs` musí potvrdit shodu prvního opravovaného
zdroje a přesné testovací zpětné vazby. Žádný kandidát se neimportuje na hostiteli.

Jde o samostatný CLI scénář; běžný backend, předchozí dávka 20 běhů, n8n workflow,
původní fixture a kontrolní testy se nemění. Živé provedení Docker/Codex se ověřuje
na tvém počítači. Automatické testy používají důvěryhodné skriptované náhrady pro
transport/model a skutečný pytest; nejsou důkazem živého volání Codexu ani Docker
izolace. RAG se nemění, neprovádí se staging, commit ani push.


## Druhá úloha: build-search-request

Pevné zadání požaduje funkci `build_search_request(query: str, top_k: int = 5) -> dict`.
Tato laboratorní úloha generuje kód pro sestavení požadavku; neprovádí skutečný
retrieval ani změny v RAG. Akceptační kontrakt:

- `query` musí být řetězec; jinak `TypeError`.
- Každou posloupnost bílých znaků včetně Unicode nahradit jednou ASCII mezerou;
  odstranit krajní bílé znaky, zachovat velikost písmen a interpunkci.
- Prázdný výsledek odmítnout přes `ValueError`.
- `top_k` musí mít přesně typ `int`, včetně odmítnutí `True`, `False` a `5.0` přes
  `TypeError`. Hodnoty mimo uzavřený interval 1–20 odmítnout přes `ValueError`.
- Vrátit nový slovník pouze s klíči `query` a `top_k`. Žádné převádění nebo ořezávání
  neplatných hodnot na povolené meze. Musí fungovat i pojmenované argumenty.

Příklad: `build_search_request("  OSPF\t routes  ", 3)` má vrátit
`{"query": "OSPF routes", "top_k": 3}`. Nejde o tělo HTTP požadavku na bridge:
HTTP stále vybírá pouze úlohu a UUID, model má implementovat celou funkci.

`--task build-search-request` podporuje pouze `--backend codex --isolation docker`.
Výchozí úloha zůstává `normalize-question`; host režim a demo druhý úkol odmítají.
Registry `tasks.py` obsahuje pouze tato dvě pevná zadání, fixture, názvy funkcí a
kontrolní testy. Cesty k testům, prompt ani příkazy se z HTTP vstupu nepřebírají.
Kandidátní modul se pro oba úkoly jmenuje `question.py`, aby zůstala jedna pevná
povolená cesta pro zápis; druhá úloha v něm definuje `build_search_request`.

Nový checker image `local-rag-dev-loop:2` obsahuje obě sady kontrol a v odpovědi
identifikuje úlohu. Druhý úkol vyžaduje správné task ID i úplné JUnit výsledky pro
**28 testů**; šest původních testů se za ně nesmí vydávat. Baseline zachovává dvě
existující vlastnosti a 26 nových případů přeskakuje. Acceptance nepřeskakuje nic.
Původní úloha nadále jako výchozí používá ověřený image `local-rag-dev-loop:1`.
Codex image a uložené přihlášení se nemění; buildovat je třeba pouze nový checker:

```powershell
cd D:\AI_roadmap_autonomous
$labPython = '.\experiments\dev_loop\.venv\Scripts\python.exe'
& $labPython -m pytest experiments/dev_loop/tests -q -p no:cacheprovider
docker build -t local-rag-dev-loop:2 -f experiments/dev_loop/docker/Dockerfile experiments/dev_loop
```

Před živým voláním modelu lze zdarma z hlediska modelové spotřeby ověřit oba
kontrakty přímo v novém Docker image. Tyto testy nepoužívají Codex ani přihlášení:

```powershell
$env:DEV_LOOP_SEARCH_DOCKER_TESTS = '1'
& $labPython -m pytest experiments/dev_loop/tests/test_search_task.py -q -p no:cacheprovider
Remove-Item Env:DEV_LOOP_SEARCH_DOCKER_TESTS
```

Dva opt-in testy prověří nový baseline, odmítnutí vadné fixture, úspěch důvěryhodné
reference a kompatibilitu nového image s původním úkolem. Bez této proměnné jsou
přeskočené. Řídicí testy také ověřují, že neprojdou záměna úlohy nebo neúplné důkazy,
že chyba baseline zabrání volání modelu, a že kontrakt odhalí běžné vadné implementace.
Bez skutečného Dockeru testy nepotvrzují vynucení izolace.

Pak spusť jeden skutečný běh:

```powershell
& $labPython -m experiments.dev_loop --task build-search-request --backend codex --isolation docker
```

Očekávání: `task_id: build-search-request`, `backend: codex-docker`, baseline
`2 passed, 26 skipped` a při úspěchu `28 passed`, `status: review_ready`. Pokusy a
opravy určuje model; žádná chyba se zde záměrně nevkládá. Platí limit tři pokusy.
`runner_image` má identifikovat nový checker, `worker_image` stávající Codex image.
Současné prostředí nemá Docker CLI, takže build a skutečný běh je nutné ověřit u tebe.

Pro n8n nejprve ukonči starý Uvicorn přes Ctrl+C a v jeho PowerShell okně s původním
`DEV_LOOP_TOKEN` spusť službu nakonfigurovanou na druhý úkol:

```powershell
& $labPython -m experiments.dev_loop --task build-search-request --backend codex --isolation docker --serve --host 0.0.0.0 --allow-non-loopback
```

Importuj samostatný `experiments/dev_loop/n8n-search-workflow.json` jako neaktivní
ruční workflow a vyber svůj ověřený Header Auth. Windows/Docker URL už je
`http://host.docker.internal:8765/runs`, timeout 900000 ms. Spusť celé nové provedení,
ať se vytvoří nové UUID. Původní workflow zůstává pro první úlohu. Jeden server
obsluhuje jednu nakonfigurovanou úlohu: nesoulad task ID vrátí 422 před spuštěním
workeru. `/health` nyní pro oba úkoly obsahuje také `task_id`. Dodatečné HTTP klíče
zůstávají zakázané. Zelený HTTP uzel sám není úspěch; ověř `status: review_ready`.

Dávky podporují stejný `--task` a přidávají task ID do JSON i HTML reportu. Nemíchej
výsledky obou zadání do jedné míry úspěšnosti. Tokeny jsou stále telemetrie CLI,
počet požadavků na model a cena zůstávají neměřené. Přihlašovací volume zůstává jen
u síťového Codex workeru; checker nemá síť, hostitelské mounty ani credentials.
Fixtures a kontroly jsou oddělené; hostitel kandidátní Python pouze ukládá jako text.

## Dva soubory: build-search-package

Třetí pevná úloha ověřuje spolupráci dvou modulů. Jedinými povolenými artefakty
jsou `validation.py` a `search_request.py` v samostatném workspace z fixtures.
Nejde o agenta s přístupem k celému repozitáři.

| Modul | Kontrakt |
| --- | --- |
| `validation.py` | `normalize_query(query: str) -> str`: stejné typové kontroly a normalizace jako u druhé úlohy. `validate_top_k(top_k: int) -> int`: přesně `int`, rozsah 1–20, vrátit platnou hodnotu beze změny. Bez importů. |
| `search_request.py` | Pouze `import validation` bez aliasu a `build_search_request(query: str, top_k: int = 5) -> dict`. Zavolat nejprve `validation.normalize_query`, potom `validation.validate_top_k`; oba výsledky použít v novém slovníku `query`/`top_k`. Výjimky předat beze změny. |

Model vrací `{"files":{"validation.py":"…","search_request.py":"…"}}`.
Řadič vyžaduje přesnou úplnou dvojici, neprázdné UTF-8 zdroje, platný AST a souhrnný
limit 64 KiB. Odmítne další cesty, chybějící modul, jiné importy a neočekávané
příkazy na úrovni modulu. AST není bezpečnostní sandbox; kandidátní Python se
spouští pouze v offline checkeru. Celá odpověď se validuje před prvním zápisem
po odstranění workeru. Zápis dvojice není atomický: chyba I/O může zanechat
částečný artefakt, ale graf skončí jako `infrastructure_error` před ověřením.
Takový workspace zkontroluj; nové ID vytvoří nové fixtures.

Checker používá `check-files`, protokol 2, ověřené task ID, úplný manifest a JUnit
důkaz všech **52 testů**. Baseline: `2 passed, 50 skipped`; acceptance bez přeskočení.
Testuje i validátory přímo, delegování, pořadí volání, použití návratových hodnot a
identitu výjimek. Protokol 1 a výchozí image předchozích úloh zůstávají podporované.

V PowerShellu sestav nové tagy, které zachovají dosavadní image:

```powershell
cd D:\AI_roadmap_autonomous
$labPython = '.\experiments\dev_loop\.venv\Scripts\python.exe'
& $labPython -m pytest experiments/dev_loop/tests -q -p no:cacheprovider
docker build -t local-rag-dev-loop:3 -f experiments/dev_loop/docker/Dockerfile experiments/dev_loop
docker build -t local-rag-codex:0.162.1-multifile -f experiments/dev_loop/docker/Codex.Dockerfile experiments/dev_loop
```

Nejprve spusť čtyři skutečné integrační případy bez modelového volání: nová sada,
kompatibilita checkeru se dvěma původními úlohami a čitelnost nového Codex schématu
bez sítě a přihlašovacího volume. Lokální testy bez Dockeru je nenahrazují.

```powershell
$env:DEV_LOOP_PACKAGE_DOCKER_TESTS = '1'
& $labPython -m pytest experiments/dev_loop/tests/test_multifile.py -q -p no:cacheprovider
Remove-Item Env:DEV_LOOP_PACKAGE_DOCKER_TESTS
& $labPython -m experiments.dev_loop --task build-search-package --backend codex --isolation docker
```

Poslední příkaz je skutečné volání Codexu. Použije existující
`local-rag-codex-auth`, nové přihlášení není potřeba. Očekávej task ID
`build-search-package`, `review_ready`, `52 passed`, oba názvy v `allowed_files`,
diff obou modulů a mapu `files_sha256` v `worker_attempts`. Počet pokusů není
zaručen, nejvýše jsou tři. `committed` a `applied_to_rag` zůstávají `false`.
Jeden běh není obecným benchmarkem úprav projektů.

Po úspěchu zastav starý server Ctrl+C. V okně s původním `DEV_LOOP_TOKEN` spusť:

```powershell
& $labPython -m experiments.dev_loop --task build-search-package --backend codex --isolation docker --serve --host 0.0.0.0 --allow-non-loopback
```

Importuj `experiments/dev_loop/n8n-package-workflow.json` a vyber existující Header
Auth. Neaktivní ruční workflow má jediný HTTP uzel bez automatického retry, timeout
900000 ms a URL `http://host.docker.internal:8765/runs`. Spusť celé nové provedení.
Task ID musí odpovídat serveru; HTTP klient nesmí dodávat obsah souborů nebo vlastní
instrukce. Opakování request ID vrací uložený výsledek, není dalším měřením.

Pro samostatnou dávku přidej ke CLI příkazu bez `--serve` například
`--cycles 20 --report-dir experiments/dev_loop/.runs/reports/package-20-local`.
Nemíchej úspěšnost různých zadání. Tokeny jsou telemetrie CLI; přesný počet požadavků
na model a cena zůstávají `null`. Worker má síť bridge a pouze své auth volume,
bez omezení provozu seznamem domén; checker nemá síť, credentials ani hostitelské
mounty. Experiment je pro místní pevné úlohy, ne pro veřejný endpoint nebo
nedůvěryhodné větve.
