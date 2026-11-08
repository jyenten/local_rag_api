<a id="top"></a>

# AI Roadmap — pravidla spolupráce s agenty

[Česky](#cz) · [English](../en/AGENTS.md#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Obsah — kliknutím rozbalit</summary>

- [Cíle](#cz-cíle)
- [Režimy spolupráce](#cz-režimy-spolupráce)
- [LEARN — výchozí režim](#cz-learn--výchozí-režim)
- [IMPLEMENT — výslovné zadání implementace](#cz-implement--výslovné-zadání-implementace)
- [REVIEW — audit](#cz-review--audit)
- [Inženýrský postup](#cz-inženýrský-postup)
- [Pravidla záznamů o učení](#cz-pravidla-záznamů-o-učení)
- [Závěrečný přehled](#cz-závěrečný-přehled)
- [Provozní dokumentace a bezpečnost](#cz-provozní-dokumentace-a-bezpečnost)

</details>

---

<a id="cz"></a>

**Působnost:** Tato globální pravidla platí pro veškerou práci v repozitáři. Při změnách v `rag_api_project/` načti také [projektová pravidla agentů](PROJECT_AGENTS.md). Uložení pod `docs/` jejich působnost neomezuje.

<a id="cz-cíle"></a>

## Cíle

Tento repozitář má dva cíle:

1. Vytvářet spolehlivé a udržovatelné AI/RAG aplikace.
2. Rozvíjet samostatné dovednosti vlastníka projektu v Pythonu, softwarovém a AI inženýrství.

Kvalita učení se nesmí obětovat rychlosti psaní kódu.


<a id="cz-režimy-spolupráce"></a>

## Režimy spolupráce


<a id="cz-learn--výchozí-režim"></a>

### LEARN — výchozí režim

Používej pro nové pojmy, algoritmy a inženýrské dovednosti.

- Nejprve vysvětli problém a očekávané chování.
- Nech vlastníka navrhnout a implementovat hlavní výukovou logiku.
- Poskytuj cílené vedení místo okamžitých řešení.
- Podpůrný kód nebo testy implementuj po schválení.
- Zkontroluj implementaci vlastníka.
- Zařaď praktické ověření porozumění.


<a id="cz-implement--výslovné-zadání-implementace"></a>

### IMPLEMENT — výslovné zadání implementace

Používej, když vlastník deleguje ohraničený implementační úkol.

- Respektuj schválené soubory a kritéria přijetí.
- Piš idiomatický, udržovatelný Python.
- Přidej smysluplné regresní testy.
- Zachovej existující rozhraní a uživatelské změny.
- Vyhni se nesouvisejícímu refaktoringu a zbytečně složitému návrhu.
- Bez schválení neprováděj commit, push ani merge.


<a id="cz-review--audit"></a>

### REVIEW — audit

- Upřednostni kontrolu bez úprav.
- Urči konkrétní vady a reprodukovatelné scénáře.
- Rozlišuj ověřené chyby od možných rizik.
- Doporuč minimální opravy a regresní testy.
- Soubory neupravuj bez oprávnění.


<a id="cz-inženýrský-postup"></a>

## Inženýrský postup

Dodržuj:

Complete -> Measure -> Improve

- Udržuj soudržné moduly a jasné odpovědnosti.
- Testuj funkčnost, okrajové případy a integritu dat.
- Nikdy neoslabuj testy jen kvůli úspěšnému výsledku.
- Zachovej reprodukovatelnost evaluace.
- Nepřistupuj k tajným ani soukromým datům mimo rozsah úkolu.
- Respektuj vnořené soubory AGENTS.md.
- Nikdy nepoužívej git add . pro automatický staging.


<a id="cz-pravidla-záznamů-o-učení"></a>

## Pravidla záznamů o učení

Udržuj [LEARNING_LOG.md](LEARNING_LOG.md).

- Navrhuj aktualizace po významných milnících.
- Odděluj dokončenou projektovou práci od prokázaných dovedností.
- Bez praktických důkazů nikdy neoznačuj dovednost za zvládnutou.
- Upřednostni samostatná cvičení a diagnostické úkoly.
- Bez lidského schválení neměň hodnocení dovedností.


<a id="cz-závěrečný-přehled"></a>

## Závěrečný přehled

U implementační práce uveď:

1. Změněné soubory.
2. Spuštěné testy a výsledky.
3. Důležitá návrhová rozhodnutí.
4. Zbývající omezení.
5. Pojmy, kterým má vlastník rozumět.

Konečnou integraci a commity schvaluje lidský vlastník.


<a id="cz-provozní-dokumentace-a-bezpečnost"></a>

## Provozní dokumentace a bezpečnost

Při práci v `rag_api_project/` si podle úkolu přečti projektový [přehled](PROJECT.md), [provozní návod](OPERATIONS.md#cz) a [evaluační příručku](EVALUATION.md#cz). Anglické a české pokyny musí popisovat stejné implementované chování.

- Před dokumentováním příkazů zkontroluj skutečné CLI a zdrojový kód; nevymýšlej parametry, cesty ani dokončené funkce.
- Považuj `python -m scripts.ingest` za **destruktivní** operaci: existující pojmenovanou Chroma kolekci smaže a znovu vytvoří. Bez výslovného oprávnění jej nespouštěj ani nenahrazuj uživatelův lokální index.
- Nezveřejňuj ani necommituj zdrojová PDF, `.env`, soukromé korpusy, cache modelů ani lokální Chroma data.
- Neměň golden evidence, benchmarkové metriky ani chráněné evaluační datasety za účelem zvýšení skóre retrievalu.
- Zachovej baseline DEV/RANDOM a nezávislost odděleného TEST; při tvrzení o porovnání uveď hash datasetu, Git původ a konfiguraci.
- Kde je to praktické, odděl úpravy dokumentace od oprav validátoru a změn závislostí či jejich verzí.
- V režimu REVIEW uváděj ověřené vady odděleně od rizik; soubory upravuj jen po schválení vlastníkem.

[↑ Nahoru](#top)
