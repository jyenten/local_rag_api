<a id="top"></a>

# Agent pro kurátorství evaluace

[Česky](#cz) · [English](../en/EVAL_CURATOR_AGENT.md#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Obsah — kliknutím rozbalit</summary>

- [Cíl](#cz-cíl)
- [Povolený výstup](#cz-povolený-výstup)
- [Existující datasety](#cz-existující-datasety)
- [Zdrojový materiál](#cz-zdrojový-materiál)
- [Postup tvorby kandidátů](#cz-postup-tvorby-kandidátů)
- [Schéma kandidáta](#cz-schéma-kandidáta)
- [Pravidla gold evidence](#cz-pravidla-gold-evidence)
- [Různorodost témat](#cz-různorodost-témat)
- [Zakázané chování](#cz-zakázané-chování)
- [Velikost dávky](#cz-velikost-dávky)
- [Validace](#cz-validace)
- [Hranice lidského schválení](#cz-hranice-lidského-schválení)

</details>

---

<a id="cz"></a>

**Pracovní adresář:** Příkazy spouštěj z `rag_api_project/`. Níže uvedené cesty k datasetům a PDF jsou relativní k tomuto projektovému adresáři.

<a id="cz-cíl"></a>

## Cíl

Připravovat kvalitní kandidátní evaluační otázky pro dataset offline evaluace RAG retrievalu.

Cílová struktura datasetů:

- DEV: 20 otázek
- RANDOM: 25 otázek
- TEST: 15 otázek

Celkový cíl: 60 otázek.

Agent připravuje pouze kandidáty. Nikdy je nesmí sám povýšit do skutečných evaluačních datasetů.

---


<a id="cz-povolený-výstup"></a>

## Povolený výstup

Kandidátní otázky zapisuj pouze do:

eval/candidates/

Příklad:

eval/candidates/random_batch_001.json

Neměň:

- eval/dev_questions.json
- eval/random_questions.json
- eval/test_questions.json
- app/
- document_search/
- evaluation/
- tests/

---


<a id="cz-existující-datasety"></a>

## Existující datasety

Před generováním kandidátů zkontroluj DEV/RANDOM kvůli duplicitním faktům a pokrytí témat:

- eval/dev_questions.json
- eval/random_questions.json

`eval/test_questions.json` ponech stranou. Validační skript automaticky kontroluje jeho ID a normalizované otázky, aniž by bylo nutné při vývoji ručně prohlížet obsah TEST. Zajisti přítomnost všech tří datasetových souborů: skript chybějící soubory přeskakuje.

Vyhni se duplicitním otázkám, duplicitním faktům a zbytečně opakovaným tématům.

---


<a id="cz-zdrojový-materiál"></a>

## Zdrojový materiál

Používej pouze PDF dokumenty v:

data/

Gold evidence musí pocházet ze skutečného textu PDF.

Pro průzkum použij existující průzkumník dokumentů:

```bash
python -m scripts.search_pdf "<query>" --top-k 10 --interactive
```

BM25 vyhledávání je pouze nástroj průzkumu.

Vysoké BM25 skóre neznamená, že je pasáž správnou gold evidence.

---


<a id="cz-postup-tvorby-kandidátů"></a>

## Postup tvorby kandidátů

Vždy postupuj v tomto směru:

evidence -> otázka

Nikdy:

otázka -> hledání, dokud něco přibližně neodpovídá

Pro každého kandidáta:

1. Najdi jasnou faktickou pasáž ve zdrojovém PDF.
2. Zaznamenej fyzické číslo stránky PDF.
3. Vytvoř jednu otázku, na kterou evidence přímo odpovídá.
4. Do contains_any zkopíruj stabilní přesný fragment evidence.
5. Otázku omez tak, aby ji evidence úplně zodpovídala.
6. Vyhni se otázkám vyžadujícím několik nesouvisejících faktů, pokud je všechny nepodporuje jeden fragment evidence.

---


<a id="cz-schéma-kandidáta"></a>

## Schéma kandidáta

Výstup musí být JSON pole.

Každá položka musí mít tuto strukturu:

```json
[
  {
    "id": "topic_random_001",
    "topic": "descriptive-topic",
    "question": "One clear question?",
    "gold_evidence": [
      {
        "source": "Exact_Source_Filename.pdf",
        "pages": [123],
        "contains_any": [
          "Exact supporting fragment from the source page"
        ]
      }
    ]
  }
]
```

---


<a id="cz-pravidla-gold-evidence"></a>

## Pravidla gold evidence

Gold evidence musí:

- používat přesný název PDF souboru
- používat fyzická čísla stránek PDF
- obsahovat text skutečně přítomný na uvedené stránce
- přímo odpovídat na otázku
- používat stabilní fragmenty místo záhlaví nebo navigačního textu

Nepoužívej tištěné číslování uvnitř PDF.

Fragmenty contains_any si nevymýšlej ani je neparafrázuj.

Více objektů GoldEvidence je povoleno, když na stejnou otázku odpovídá několik samostatně platných pasáží.

contains_any má sémantiku OR (stačí jedna alternativa).

Nevkládej do contains_any dva fragmenty, pokud jsou pro odpověď potřebné oba současně.

---


<a id="cz-různorodost-témat"></a>

## Různorodost témat

Preferuj pokrytí mimo již nadměrně zastoupená témata.

Nevytvářej dávku ovládanou jedním protokolem nebo jedním PDF.

Podle obsahu korpusu mohou být užitečné oblasti:

- adresace IPv4 / IPv6
- DHCP / DHCPv6
- NAT
- základy směrování
- BGP
- EIGRP
- RIP
- OSPF
- redistribuce tras
- Neighbor Discovery
- bezpečnost směrování nebo validační mechanismy
- směrovací funkce nezávislé na protokolu

Různorodost témat je podřízena kvalitě evidence.

Nikdy nevytvářej slabou otázku jen kvůli vyvážení témat.

---


<a id="cz-zakázané-chování"></a>

## Zakázané chování

Nesmíš:

- měnit kód retrievalu
- měnit evaluační metriky
- měnit existující gold evidence
- spouštět retrieval a přepisovat gold jen kvůli zlepšení metriky
- přebírat existující otázku DEV nebo RANDOM pouze s jiným zněním
- vymýšlet zdrojový text
- odhadovat čísla stránek
- používat externí internetové zdroje
- používat jako gold evidence znalosti, které nejsou v lokálních PDF
- povyšovat kandidáty do skutečného datasetu

---


<a id="cz-velikost-dávky"></a>

## Velikost dávky

Pokud není zadáno jinak, generuj přesně 5 kandidátů v dávce.

Pro RANDOM používej ID odpovídající existujícímu datasetu, například:

```text
bgp_random_002
ipv6_random_002
routing_random_002
```

ID musí být unikátní napříč všemi evaluačními datasety a současnou kandidátní dávkou.

---


<a id="cz-validace"></a>

## Validace

Po zápisu kandidátního JSON spusť:

```bash
python -m scripts.validate_eval_candidates <candidate-file>
```

Pokud validace selže:

1. diagnostikuj kandidáta
2. oprav pouze kandidátní soubor
3. spusť validaci znovu

Neoslabuj validátor.

Dávka je dokončená pouze tehdy, když validace vypíše:

```text
VALID: 5 candidate(s)
```

---


<a id="cz-hranice-lidského-schválení"></a>

## Hranice lidského schválení

Po validaci skonči.

Uveď:

- cestu ke kandidátnímu souboru
- všech 5 ID kandidátů
- téma každého kandidáta
- zdrojové PDF a stránku každého kandidáta
- výsledek validace

Nespouštěj promote_eval_candidates.

Povýšení vyžaduje výslovné lidské schválení.

[↑ Nahoru](#top)
