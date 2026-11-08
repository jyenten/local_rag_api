<a id="top"></a>

# Vývojová příručka projektu AI RAG

[Česky](#cz) · [English](../en/DEVELOPMENT_GUIDE.md#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Obsah — kliknutím rozbalit</summary>

- [Odpovědnosti dokumentace](#cz-odpovědnosti-dokumentace)
- [Vývojový postup](#cz-vývojový-postup)
- [Návrh kódu a modulů](#cz-návrh-kódu-a-modulů)
- [Chyby, vedlejší účinky a diagnostika](#cz-chyby-vedlejší-účinky-a-diagnostika)
- [Ověřování a regresní testy](#cz-ověřování-a-regresní-testy)
- [Disciplína retrievalu a evaluace](#cz-disciplína-retrievalu-a-evaluace)
- [Git, revize a integrace](#cz-git-revize-a-integrace)
- [Bezpečnost a správa závislostí](#cz-bezpečnost-a-správa-závislostí)
- [Spolupráce a učení](#cz-spolupráce-a-učení)
- [Dokončení a aktualizace dokumentace](#cz-dokončení-a-aktualizace-dokumentace)

</details>

---

<a id="cz"></a>

Tato příručka určuje, **jak vyvíjet a kontrolovat změny**. Priority fází a současný stav projektu patří do [ROADMAP.md](ROADMAP.md#cz); dokončená práce a doklady o učení do [LEARNING_LOG.md](LEARNING_LOG.md#cz).


<a id="cz-odpovědnosti-dokumentace"></a>

## Odpovědnosti dokumentace

| Dokument | Určuje |
| --- | --- |
| [ROADMAP.md](ROADMAP.md#cz) | Schválené fáze, jejich cíle a kritéria přijetí, současné zaměření vývoje |
| [ARCHITECTURE.md](ARCHITECTURE.md#cz) | Implementované komponenty, rozhraní a výslovně označená cílová architektura |
| Tato příručka | Vývojový postup, kvalita kódu, ověřování a práce s Gitem |
| [OPERATIONS.md](OPERATIONS.md#cz) | Instalace, konfigurace, ingest, API, Docker a spustitelné příkazy (CZ/EN) |
| [EVALUATION.md](EVALUATION.md#cz) | Tvorba evidence, párování, metriky, evaluace a reprodukovatelnost (CZ/EN) |
| [LEARNING_LOG.md](LEARNING_LOG.md#cz) | Datované milníky, původ práce ve větvích a prokázané učební výsledky |
| [Globální AGENTS.md](AGENTS.md#cz), [projektový AGENTS.md](PROJECT_AGENTS.md#cz) | Oprávnění agentů, režimy spolupráce a hranice schvalování |

Neudržuj zde další tabulku milníků, benchmarků ani seznam aktivních fází. Pokud postup potřebuje tento kontext, odkaž na příslušný dokument.


<a id="cz-vývojový-postup"></a>

## Vývojový postup

Dodržuj **Complete → Measure → Improve**:

1. Zkontroluj implementaci, platná pravidla AGENTS, současnou větev a necommitnuté změny. Urči schválený cíl roadmapy a dotčené soubory.
2. Vymez očekávané chování, rozsah a kritéria přijetí. Užitečné nesouvisející nápady nech v backlogu; nerozšiřuj kvůli nim současnou fázi.
3. Před optimalizací jednotlivých komponent dokonči funkční celek napříč vrstvami. Upřednostni jednu soudržnou změnu před velkým spekulativním refaktoringem.
4. Ověř chování vhodnými testy a u změn retrievalu řízeným měřením DEV/RANDOM. Jeden ručně vybraný úspěšný dotaz nestačí.
5. Zkontroluj výsledek, zaznamenej důkazy a omezení a pak zlepšuj naměřenou slabinu. Aktualizuj dokument, který spravuje změněné chování nebo stav.

Nový nápad patří do současné změny pouze tehdy, pomáhá-li splnit nynější Definition of Done. Neotevírej dokončenou práci jen proto, že si lze představit jiný návrh. Znovu ji otevři při konkrétním selhání evaluace/integrace, bezpečnostním problému nebo podstatné změně požadavků.

Cíle a checklisty Definition of Done jednotlivých fází určuje roadmapa. Tato příručka níže stanovuje společné implementační a ověřovací postupy.


<a id="cz-návrh-kódu-a-modulů"></a>

## Návrh kódu a modulů

- Každému modulu ponech jednu soudržnou odpovědnost a každému subsystému malé veřejné rozhraní. Odděluj načítání dokumentů, zpracování textu, retrieval, reranking, generování, evaluaci a HTTP přenos.
- Upřednostni vysokou soudržnost a malou provázanost. Volej veřejné funkce místo přístupu k interním modelům, cache nebo polím pořadí jiného subsystému.
- Používej výslovné typované modely, pokud pozice v n-tici/slovníku zakrývají význam. Pro identitu dokumentu, zdroj/stránku, evidenci a hotové výsledky preferuj neměnné záznamy; mutaci povol pouze záměrně.
- Obecnou infrastrukturu udržuj nezávislou na doménových směrovacích pojmech. Doménová pravidla patří na výslovnou doménovou hranici, nikoli do obecného řazení.
- Názvy modelů, cesty a limity centralizuj v konfiguraci. Zachovej zveřejněná rozhraní a uživatelské změny, pokud schválený úkol nevyžaduje jejich změnu.
- Piš idiomatický typovaný Python: jasné názvy, malé účelné funkce, comprehensions/generátory tam, kde zůstávají čitelné. Vyhni se samoúčelně krátkému kódu, hluboce vnořeným výrazům a abstrakcím bez současné potřeby.
- Pomocná funkce automaticky nepotřebuje vlastní soubor. Odděl ji, pokud hranici odůvodní opakované použití, samostatná odpovědnost, velikost nebo testování.
- Pro jednoduché záznamy používej přímé atributy. Properties/gettery/settery přidávej jen tehdy, přináší-li řízený přístup skutečné chování; nejsou bezpečnostním opatřením.
- Nezaváděj dědičnost, asynchronní kód, návrhové vzory ani metaprogramování pouze kvůli architektonické symetrii. Před velkým refaktoringem nejprve popiš problém, cílové hranice a rozhraní v ARCHITECTURE.md.


<a id="cz-chyby-vedlejší-účinky-a-diagnostika"></a>

## Chyby, vedlejší účinky a diagnostika

Externí vstup validuj na vhodné hranici a při selhání uveď užitečný důvod. Nepotlačuj výjimky potichu, nezahazuj neúspěšné vstupy a neoznačuj částečně zpracovaný dokument za úspěšný ingest.

Odděl čisté transformace od přístupu k souborům/databázi, načítání modelů a zápisu historie. Významné vedlejší účinky vyjádři v názvech funkcí, rozhraních a provozních pokynech. Limity prostředků mají pokrývat relevantní hranice souboru, PDF stránky, dotazu, počtu výsledků a požadavku; ověř implementované limity, nepředpokládej existenci plánovaných kontrol.

Bezpečnostní validaci odděl od předzpracování textu: odmítnutí nebezpečného souboru nesmí potichu měnit význam platného dokumentu. Ve znovupoužitelných modulech preferuj logování; CLI může vypisovat uživatelské výstupy. Diagnostika má určit selhání bez vyzrazení tajných údajů či soukromého obsahu korpusu.


<a id="cz-ověřování-a-regresní-testy"></a>

## Ověřování a regresní testy

Použij vrstvu ověření, která odpovídá skutečné otázce:

| Vrstva | Účel |
| --- | --- |
| Jednotkové testy | Deterministické chování modulů, validace a okrajové případy |
| Integrační testy | Chování přes hranice komponent |
| Smoke testy | Základní fungování aplikace v zamýšleném prostředí |
| Evaluace retrievalu | Kvalita podložená evidencí a latence retrievalu |

Pro jednotkové testy preferuj malé syntetické fixtures, falešné kolekce a výslovné chybové scénáře. Skutečná PDF/modely patří do vhodných integračních, ručních nebo evaluačních kontrol; úspěšné syntetické testy neprokazují kvalitu nad skutečným korpusem.

Pro ověřenou vadu přidej smysluplný regresní test. Kde je to praktické, ověř, že odhaluje původní selhání. Nikdy neoslabuj assertions ani validaci kvůli úspěšnému výsledku. Kromě běžného úspěšného průchodu testuj integritu dat a soulad rozhraní.

Při změně kódu spusť cílené testy a celou projektovou sadu před commitem. Z `rag_api_project/`:

```bash
python -m pytest tests -q
```

U změn pouze v dokumentaci ověř fakta, odkazy, příklady a dotčenou konfiguraci; nevymýšlej testy kopírující text. Přesně uveď spuštěné kontroly, přeskočení/varování a důležité kontroly, které provést nešlo. Z lokálního hlášení samotného nevyvozuj úspěch GitHub CI ani výsledky nad skutečným korpusem.


<a id="cz-disciplína-retrievalu-a-evaluace"></a>

## Disciplína retrievalu a evaluace

[EVALUATION.md](EVALUATION.md#cz) určuje schéma, pravidla párování, CLI příkazy, schvalování/povýšení a požadavky na reprodukovatelnost. [EVAL_CURATOR_AGENT.md](EVAL_CURATOR_AGENT.md#cz) určuje omezení kurátorství kandidátů.

- Odděluj vývoj DEV, průzkum robustnosti RANDOM a závěrečný TEST. Neprohlížej opakovaně chyby TEST a pak pro ně neoptimalizuj.
- Před změnou řazení stanov baseline. Běhy DEV/RANDOM porovnávej při kontrolovaném korpusu, indexu, datasetu a konfiguraci; uchovej původ výsledků.
- Evidenci vytvoř ze zdrojových PDF před psaním otázek. Skóre průzkumu neprokazuje věcnou platnost, ani když stránkové a chunkové vyhledávání používají různé implementace BM25.
- Neměň existující golden evidence, metriky ani historii baseline za účelem zvýšení skóre. Validace kandidátů neopravňuje k povýšení.
- Rozlišuj naměřenou latenci `search()` od inicializace a ceny celé odpovědi/HTTP požadavku; uveď, kterou práci retrievalu či rerankingu měřená metoda zahrnuje. Neslučuj neslučitelná surová skóre relevance bez odůvodněné metody a naměřené evaluace.


<a id="cz-git-revize-a-integrace"></a>

## Git, revize a integrace

Výchozí integrační větev je `main`. Novou práci připravuj na vhodné pracovní větvi; zachovej nesouvisející worktrees a necommitnuté změny. V rámci vedlejšího úklidu neresetuj, nestashuj, nepřepínej ani nestaguj cizí rozpracovanou práci.

Před stagingem zkontroluj `git status --short` a `git diff`. Přidej přesné zamýšlené cesty a pak zkontroluj seznam i obsah připravených souborů:

```bash
git diff --cached --stat
git diff --cached
git diff --cached --check
```

Nepoužívej automatické `git add .`. Soukromá PDF, lokální indexy, cache modelů, `.env` a další tajné údaje nepatří do commitů. Preferuj soudržné commity se zprávou popisující dokončené chování; kde je to praktické, odděl nesouvisející dokumentaci, závislosti a funkce.

Z `rag_api_project/` projektový pomocník spouští kontrolu bílých znaků ve staged změnách a projektovou testovací sadu:

```bash
python -m scripts.git_check
```

Neuděluje oprávnění ani nedokládá kontrolu tajných údajů, rozsahu, závislostí a kvality retrievalu. Před pushem znej stav pracovního stromu, zkontroluj zamýšlené změny a splň platná pravidla AGENTS a repozitáře. Commit, push a merge prováděj pouze v rozsahu výslovného oprávnění; neobcházej povinné revize ani pravidla CI.


<a id="cz-bezpečnost-a-správa-závislostí"></a>

## Bezpečnost a správa závislostí

Bezpečnost platí v celém vývoji, nejen v plánované bezpečnostní fázi. Validuj externí vstupy, vynucuj vhodné hranice souborového systému/prostředků, zacházej uvážlivě s tajnými údaji a selhání uváděj výslovně.

Audit závislostí, Dependency Review, Gitleaks a Dependabot jsou již nakonfigurované. Jejich nálezy považuj za podněty k šetření; úspěšné Python testy neřeší zranitelnost závislosti. Nevypínej ani neoslabuj kontroly, aby změna vypadala zdravě.

`requirements.txt` připíná přímé závislosti a čtyři výslovné bezpečnostní piny nepřímých/build balíčků. Linux CI používá `requirements-linux-py311.lock.txt` (Ubuntu 24.04, Python 3.11) v čistém virtuálním prostředí. Tento lock není instalační soubor pro Windows. Příkaz `python -B scripts/check_dependency_lock.py`, spuštěný z `rag_api_project/`, kontroluje shodu všech přímých a bezpečnostních pinů s lock souborem.

Při změně verzí aktualizuj oba manifesty a ověř čistou instalaci, `pip check`, všechny regresní testy a oba audity závislostí. Audity běží nezávisle: jeden vyřeší závislosti z `requirements.txt`, druhý kontroluje přesný Linux lock včetně nepřímých balíčků. Nálezy nadále způsobí selhání CI.

Workflow **Generate Linux Python Lock** lze ručně spustit na větvi se závislostmi a znovu vytvořit snapshot v čistém prostředí. Ověřovací job stáhne právě vytvořený artefakt do druhého čistého prostředí a spustí v něm testy. Artefakt zkontroluj a commituj přes Git; workflow do větví nezapisuje. Připnutí ChromaDB 1.5.9 neopravuje známé zranitelnosti ani neschvaluje rizikovou výjimku; viz [CHROMA_SECURITY.md](CHROMA_SECURITY.md).

Před doporučením či spuštěním `python -m scripts.ingest` vysvětli, že nakonfigurovanou Chroma kolekci **smaže a znovu vytvoří**. Dodrž zálohovací, konfigurační a schvalovací hranice v [OPERATIONS.md](OPERATIONS.md#cz).


<a id="cz-spolupráce-a-učení"></a>

## Spolupráce a učení

Oprávnění určují globální a projektový AGENTS. Zvol režim odpovídající požadavku vlastníka; nevnucuj výukový postup každému implementačnímu úkolu:

- **LEARN:** vysvětli problém a chování, podpoř implementaci vlastníka, zkontroluj ji a získej praktický doklad porozumění.
- **IMPLEMENT:** dokonči delegovanou ohraničenou změnu, zachovej rozhraní/WIP, ověř ji a popiš výsledek i omezení.
- **REVIEW:** kontroluj a uváděj reprodukovatelné nálezy; soubory měň jen po schválení oprav vlastníkem.

V LEARN používej úplné logické celky s cílem, odůvodněním, novými relevantními pojmy, rozsahem a jasným ověřením. Velkým/rizikovým komponentám věnuj samostatnou cílenou revizi; vyhni se konverzačnímu postupu import po importu. Používej idiomatický Python bez umělého zjednodušování a nepotřebných pokročilých mechanismů.

Zaznamenávej významné milníky, obtíže, pomoc a testovací důkazy do [LEARNING_LOG.md](LEARNING_LOG.md#cz). Odděluj hotovou funkci od samostatně prokázané dovednosti. Bez požadovaných lidských důkazů/schválení neuděluj hodnocení zvládnutí ani neměň hodnocení učení.


<a id="cz-dokončení-a-aktualizace-dokumentace"></a>

## Dokončení a aktualizace dokumentace

Znovupoužitelný modul je obvykle hotový, když má jasnou odpovědnost a rozhraní, funguje očekávané chování, validuje důležité vstupy, procházejí relevantní testy i projektové regrese a známá záměrná omezení jsou zdokumentovaná. Dokončení podfáze posuzuj podle konkrétních kritérií roadmapy. Neoznačuj ji za hotovou při zásadní nevyřešené chybě.

Při změně chování nebo schváleného rozhodnutí:

- Aktualizuj odpovědný dokument z tabulky.
- Odliš současnou implementaci od cílové architektury a lokální rozpracované práce.
- Synchronizuj české a anglické provozní/evaluační pokyny.
- Data, měření a původ práce ve větvích uváděj v učebních/evaluačních záznamech; odkazuj na ně místo kopírování proměnlivého stavu do všech dokumentů.
- Uveď změněné soubory, ověření, rozhodnutí a zbývající omezení.

Cíle nebo priority fáze se mění pouze schváleným rozhodnutím o roadmapě. Při úklidu dokumentace plán potichu nepřepracovávej.

[↑ Nahoru](#top)
