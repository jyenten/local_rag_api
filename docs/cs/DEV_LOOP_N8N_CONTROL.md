# Ovládání úloh přes n8n

[English](../en/DEV_LOOP_N8N_CONTROL.md) · [Dohody](DEV_LOOP_POLICY.md) · [Starší publikace](DEV_LOOP_N8N_PUBLICATION.md)

## Co ovládáš

Import `experiments/dev_loop/n8n-control-workflow.json` přidá formulář před
existující controller na portu 8766. n8n vybírá akci, zobrazí plán a přijme
rozhodnutí; LangGraph řídí implementaci a nejvýše dvě opravy. Nezávislé testy běží
v offline Dockeru. Režim `autonomous` po jediném schválení plánu automaticky
pokračuje až k reportu a draft PR. `generate` a `publish` dál dovolují oddělené
schvalování. Merge zůstává na člověku.

Katalog obsahuje historickou `bm25-tokenize-once` a registrovanou
[`retrieval-citation-provenance`](DEV_LOOP_CITATION_TASK.md). BM25 je v `main`
dokončený; další generování proti změněnému zdroji preflight odmítne. Aktivní typ
nových jobů výslovně volí hostitelský profil; nabídka v n8n jej sama nezapne.
Není zde libovolný prompt, shell ani vzdálené přidávání úloh. Registrace nové úlohy
je jednorázové nastavení podle odkazovaného návodu, běžné akce potom běží z formuláře.

## Jednorázové aktualizování služby

Použij stávající stabilní worktree a ignorovaný profil. n8n kontejner neměň ani
nepřestavuj. Starou službu ukonči pomocí Ctrl+C v jejím PowerShell okně.
Příklad pro existující instalaci vlastníka:

```powershell
cd D:\AI_roadmap_n8n_publication
git status -sb
git fetch origin
git switch --detach origin/feat/dev-loop-autonomous-prototype
.\experiments\dev_loop\Start-DevLoop.ps1 -Action check
.\experiments\dev_loop\Start-DevLoop.ps1 -Action start
```

Při lokálních změnách nejprve zajisti jejich zachování; nepoužívej force/reset.
Feature větev slouží k ověření před mergem. Po schválené integraci může stejný
čistý worktree sledovat `origin/experiment/autonomous-dev`; celá laboratoř nepatří
do aplikačního `main`. Zachovej profil, historické běhy, cache a přihlášení.
Nejde o patchový instalační postup.

Launcher použije uložený Python a nastavení. Chybějící DEV_LOOP_TOKEN vyžádá
skrytě: vlož stejný uložený token jako v n8n Header Auth. Token neukládá do
profilu ani workflow. Restart není oprávnění resetovat allowance a vynutit další
modelová volání.

## Import a přihlášení

1. V n8n importuj JSON z aktualizovaného worktree.
2. U **Ovládání úloh** vyber credential **HTTP Basic Auth** se samostatným lokálním
   přihlášením k formuláři. Nepoužívej GitHub/Codex přihlášení. Export neobsahuje heslo.
3. U **Zkontrolovat plán** a **Provést schválenou akci** vyber existující **Header
   Auth**: hlavička `X-Dev-Loop-Token`, hodnota uložený token služby.
4. Pro první kontrolu použij **Execute Workflow** a **Test URL** formuláře.
   Produkční URL má po aktivaci cestu `/form/local-rag-control`.
5. Zachovej n8n na `127.0.0.1:5678` a controller na `127.0.0.1:8766`.
   HTTP uzly uvnitř Dockeru oslovují `host.docker.internal:8766`.

Parametry Form/Form Trigger 2.4, IF 2.2 a HTTP Request 4.2 jsou ověřené proti
zdrojům n8n 2.45.7. Skutečný import/zobrazení na uživatelově instalaci je oddělený
integrační krok; unit/contract testy jej nenahrazují.

## Akce

| Akce | UUID | Výsledek |
|---|---|---|
| `catalog` | Prázdné | Seznam povolených úloh/běhů a konfigurace, bez modelu/publikace |
| `status` | Existující job nebo registrovaný běh | Stav, bez zahájení/opakování modelu |
| `report` | Úspěšný job nebo registrovaný běh | Validované srovnání a čitelný diff, bez hostitelských cest/raw logů |
| `autonomous` | Prázdné vytvoří ID; existující job lze dokončit bez nového modelu | Jediné schválení celého plánu → baseline → Codex → testy / nejvýše dvě opravy → report → Docker recheck → draft PR |
| `generate` | Prázdné vytvoří ID; lze zadat vlastní | Plán a schválení, potom pouze generování/testy, bez publikace |
| `publish` | Úspěšný job nebo registrovaný běh | Plán, hash kandidáta, diff a samostatné schválení, potom nové ověření a draft PR bez modelu |

Výchozí akce je `catalog`, výchozí rozhodnutí **Zrušit**. **Schválit** povoluje
pouze zobrazenou akci, UUID a hash plánu. Změna kandidáta, zdroje nebo zbývajícího
rozpočtu vyžaduje nový preview. Token autentizuje volajícího; volba ve formuláři
není samostatné ověření totožnosti ani kryptografický podpis člověka.

Nejprve spusť `catalog`, potom zkopíruj povolené UUID do nové akce `report`.
Historický běh vlastníka je `a5739357-6da4-4118-be18-5c038306e0e9`; funguje pouze,
pokud jej profil skutečně povoluje a soubory zůstávají dostupné. Nic se negeneruje.

Generování je synchronní HTTP krok s timeoutem 1800 sekund. Během něj lze otevřít
formulář ve druhé kartě a zvolit `status` se stejným UUID. `generating` je souhrnný
stav, ne tokenový stream. ID a průběh jsou také v n8n Executions. Po timeoutu
nejprve ověř původní UUID, nevytvářej náhradní modelový běh. Automatické retry ani
příkaz pro násilné ukončení workeru zde nejsou.

## Autonomní prototyp: jeden celý průchod

Jednorázově aktivuj [registrovanou opravu citací](DEV_LOOP_CITATION_TASK.md):
postav její pevný checker a v existujícím profilu vyber
`retrieval-citation-provenance`. Používá stávající Codex image/auth volume,
GitHub přihlášení hostitele i n8n kontejner. Potom importuj aktualizovaný
`n8n-control-workflow.json` a přiřaď stejný Basic Auth a Header Auth jako dosud.

1. V katalogu musí být u úlohy `generation_configured: true` a zbývat jeden job.
2. Vyber `autonomous`, úlohu `retrieval-citation-provenance`, UUID nech prázdné.
3. Zkontroluj plán: dvě povolené cesty, dvě editovatelné metody, pevný regresní
   soubor, 15 acceptance případů, max. 3 pokusy a automatický **draft** PR do `main`.
   **Schválit** teď povoluje celý tento konkrétní cyklus.
4. Od tohoto okamžiku už běh nečeká na další lidský krok. LangGraph podle testů
   opravuje návrh; publisher úspěšný návrh znovu ověří v původním offline Dockeru
   a vytvoří draft PR. Výsledek obsahuje odkaz, srovnání před/po a diff.
5. Úspěšný konec je `result.status: pr_ready`; oba `report.comparison.after`
   příznaky mají být true. `ci_status: not_checked` neznamená zelené GitHub CI.

Selhání baseline, infrastruktury či všech tří pokusů končí bez publikace. Selhání
publikace končí `publication_blocked`; po kontrole lze schválit nový plán se
**stejným UUID**. Ten váže hash uloženého kandidáta a má `generation_required:
false`, `max_worker_attempts: 0`: pouze opakuje publikaci. Uložený úspěšný `generate`
job lze stejným způsobem dokončit. Historický registrovaný běh používej přes
`publish`, nikoli jako nový autonomní job. Přerušený job bez `result.json` se
neregeneruje, dokončený job se jen zobrazí. Limit nových jobů zůstává na proces;
restart není trvalý finanční limit ani oprávnění k dalším úlohám.

Tento prototyp řídí jeden registrovaný vývojový úkol. Nerozhoduje o dalších úlohách,
neprovádí merge, ingest ani nasazení. GitHub CI a případné bezpečnostní nálezy
zůstávají ke kontrole před mergem.

## Co bylo ověřeno a co ověřit u sebe

Contract testy procházejí jediné schválení, automatické předání, chyby, opakování,
starý hash a zachování oddělených akcí. JavaScript výrazy workflow se vyhodnocují
v Node.js včetně bezpečného zobrazení diffu a odkazu na PR.

CI `citation-checker` navíc spouští celý HTTP → LangGraph → skutečný offline Docker
→ oprava → opakované Docker ověření → publisher průchod. Worker je v tomto testu
výslovně skriptovaná reference a GitHub je fake; test nevolá skutečný model ani
nevytváří veřejný PR. Živý Codex, import/spuštění v uživatelově n8n a skutečné
předání PR jsou samostatná integrační ověření, která musí doložit konkrétní běh.

## Diagnostika

| Stav | Význam |
|---|---|
| `approval_required` | Plán připraven, nic se neprovedlo |
| `review_ready` | Návrh ověřen, publikace čeká na samostatné schválení |
| `pr_ready` | Tehdejší předání PR, ne aktuální CI ani souhlas s mergem |
| `publication_blocked` | Generování zachováno; po kontrole lze zopakovat pouze publikaci |
| `SOURCE_CHANGED` / `SOURCE_OR_REMOTE_PREFLIGHT_BLOCKED` | Zdroj/remote neodpovídá úloze; u dokončeného BM25 očekávané |
| `NEW_JOBS_NOT_CONFIGURED` | Host povolil pouze uložené běhy |
| `NEW_JOB_ALLOWANCE_CONSUMED` | Vyčerpán limit relace; formulář jej nenavyšuje |
| `JOB_ACTIVE_OR_INTERRUPTED` | Aktivní/neúplný job; neobcházej novým ID |
| HTTP 401 | Zkontroluj Header Auth credential; token nevypisuj |
| HTTP 409 | Aktivní změna, starý plán nebo konflikt; nejprve status/nový preview |
| HTTP 503 | Podklady/infrastruktura odmítnuty; podrobnosti zůstávají v hostitelském logu |

## Učení na uzlech

| Uzel | Co ukazuje |
|---|---|
| Ovládání úloh | Form Trigger: pevné akce a vstup UUID |
| Zkontrolovat plán | HTTP Request: JSON a Header Auth |
| Vyžaduje schválení? | IF: skutečný boolean místo zelené barvy HTTP |
| Prohlédnout a schválit | Form: čekání na lidské rozhodnutí |
| Schváleno? | IF: pouze výslovné Schválit vede k akci |
| Provést schválenou akci | Identita/hash z kontrolovaného plánu, ne z nového vstupu |
| Výsledek a report / Zrušeno bez provedení | Form Ending: výsledek nebo konec bez změny |

Cvičení: spusť `catalog` a `report`, vysvětli, proč neběžel worker, a ukaž uzel,
který při volbě **Zrušit** zabrání publikaci. Toto není předem potvrzené zvládnutí.

Starší `/jobs` a `n8n-real-bm25-workflow.json` kvůli kompatibilitě stále spojují
generování a publikaci. Pro nové ovládání je nepoužívej. Nový formulář volá pouze
`/control/preview` a `/control/execute`; allowlisty, Docker izolace, tři pokusy,
zdrojové hashe a zákaz automatického merge nadále vynucuje controller.
