# Dohody pro vývojovou laboratoř

[English](../en/DEV_LOOP_POLICY.md) · [Globální pravidla](AGENTS.md) · [Provoz](DEV_LOOP.md)

Zapsáno 8. 11. 2026 podle schválených dohod této práce. Jde o verzovaný provozní
kontrakt pro Local RAG API / dev-loop, nikoli úplnou paměť konverzace. Aktuální
výslovné pokyny vlastníka a nadřazené instrukce mají přednost. Tato pravidla nesmí
agent sám přepsat za účelem rozšíření svého oprávnění.

## Rozsah oprávnění

Vlastník povolil v rámci jím delegovaného, ohraničeného implementačního úkolu
samostatné vytvoření větve, commitu, push a draft PR. Platí pro controller v
`experiments/dev_loop/`, jeho konkrétně potřebné CI, návody a schválenou implementaci
skutečného úkolu v rozsahu jeho manifestu. Nejde o trvalé zadání libovolných nových
úkolů ani o změnu architektury, technologií, priorit či nárokování vyššího rozpočtu.

- Zachovej cizí WIP, pracovní větve, indexy, cache a přihlášení.
- Stageuj přesné cesty; nepoužívej automatické `git add .`, force push ani reset cizí větve.
- Údržbová feature větev může přijmout zkontrolovaný fast-forward. Publisher
  aplikačního výsledku vytváří nové reference a existující nepřepisuje.
- Změny předávej přes Git větev a PR. Patch je případný nouzový export, nikoli
  běžný instalační postup.
- Lab PR směřuje do experimentální větve či předchozí větve ve zkontrolovaném
  řetězci. Aplikační změna má samostatný PR do `main`; celá laboratoř se tam neslučuje.
- Žádný merge bez nového výslovného schválení konkrétního PR vlastníkem po kontrole.
  Souhlas s commitem/push ani obecné „pokračuj“ není souhlas s mergem.

## Kontrola a důkazy

Před mergem zkontroluj aktuální head/diff, rozsah souborů, relevantní testy, CI a
bezpečnostní nálezy. Rozporuj závěr, který důkazy nepodporují. Kontroluj kód i
nezávislý výsledek; nezdvojuj bezdůvodně již úspěšné běhy.

- Odděluj unit/contract testy, živý Docker, skutečný model, n8n spojení a živé GitHub
  vytvoření PR. Použití existujícího PR nedokazuje vytvoření nové větve/PR.
- `review_ready` ani zelený HTTP uzel není schválení. `pr_ready` potvrzuje tehdejší
  předání, nikoli aktuální CI nebo stav po pozdějším lidském mergi.
- Přiznej neprovedené ověření a zbývající riziko. Nevydávej kontrolu několika portů
  za audit celého počítače nebo opravu knihovní CVE.
- Zachovej bezpečnostní audit bez potlačování. Červenou kontrolu a známé zděděné
  nálezy popiš; rozhodnutí o případném zbytkovém riziku vyžaduje výslovné lidské schválení.
- Schvalovací štítek, včetně `human-approved-eval-change`, smí po kontrole přidat
  člověk. Agent jej nesmí použít jako obcházení ochrany změn pravidel.
- Změna těchto pravidel a vstupních AGENTS souborů patří do chráněného PR s lidskou kontrolou.

## Hranice provádění

- n8n vybírá registrovaný úkol/ID. HTTP nesmí přijímat shell příkazy, libovolné
  prompty, repository/file cesty, zdrojové soubory nebo GitHub přihlášení.
- Zdroj, povolené soubory, testy a limity určuje zkontrolovaný hostitelský controller.
  Nový typ úkolu potřebuje vlastní zkontrolovanou registraci, nikoli obcházení manifestu.
- Model vrací strukturovaný návrh. Jeho Python se ověřuje v odděleném offline
  Docker checkeru bez hostitelských mountů, sítě a přihlášení; selhání izolace
  nesmí přepnout na hostitelské provádění.
- LangGraph zachová maximum tří implementačních pokusů. Nové joby mají výslovné
  hostitelské povolení; výchozí limit je jeden nový job na proces služby. Jde o
  limit relace, nikoli trvalý/globální tokenový či finanční strop.
- Stejné ID a restart nesmí potichu regenerovat kód. Neúplný přerušený výsledek
  vyžaduje kontrolu; selhání publikování dovoluje zopakovat pouze publikování.
- Model-call count a cenu uváděj jako neznámé, pokud nejsou skutečně měřené. Demo,
  řízená injekce chyby a skutečný model musí zůstat rozlišené.

## Data, přihlášení a síť

- GitHub přihlášení zůstává na hostiteli. Codex dostává jen svůj oddělený auth volume;
  checker ani n8n nepřebírají GitHub token. n8n používá pouze bridge Header Auth.
- Token se ukládá do credential/chráněného prostředí, nikdy do Git config profilu,
  workflow JSON, reportu, commitu nebo veřejného logu.
- Neměň soukromé PDF, Chroma index, DEV/RANDOM/TEST, gold evidence ani metriky jako
  prostředek ke zvýšení skóre. Ingest je destruktivní a vyžaduje samostatný souhlas a zálohu.
- Služba naslouchá na loopbacku. Problém spojení nesmí automaticky vyústit v bind
  `0.0.0.0`, veřejný tunel nebo širokou výjimku firewallu.
- Stabilní instalace používá jeden pracovní adresář a ignorovaný lokální profil.
  Běžný úkol nepřepíná worktree, nepřestavuje n8n a neinstaluje závislosti.
  Worker/checker kontejnery vytváří a odstraňuje controller automaticky.

## Co Git pravidla vynucují

Kořenový a modulový `AGENTS.md` ukazují agentům na tento kontrakt. CODEOWNERS a
Eval Governance chrání změny pravidel před nezkontrolovaným mergem v používaném
review procesu. Textový soubor sám není sandbox ani branch protection.

Runtime omezení dál vynucují task/file allowlisty, hashe zdrojů, AST validace,
Docker hranice, token, zámky a stabilní ID v kódu. Worker v Dockeru nedostává celý
repozitář ani automaticky tuto konverzaci; dostává pevné instrukce úkolu a schema.
Při změně provozních dohod zkontroluj odpovídající kód, testy a oba jazyky návodů.
