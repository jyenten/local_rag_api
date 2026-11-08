<a id="top"></a>

# Golden evidence a evaluace retrievalu

[Česky](#cz) · [English](../en/EVALUATION.md#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Obsah — kliknutím rozbalit</summary>

- [1. Co je golden evidence?](#cz-1-co-je-golden-evidence)
- [2. Rozdělení datasetů](#cz-2-rozdělení-datasetů)
- [3. Jak vytvořit nový důkaz: evidence → question](#cz-3-jak-vytvořit-nový-důkaz-evidence--question)
- [4. Validace kandidátů](#cz-4-validace-kandidátů)
- [5. Povýšení schválených kandidátů](#cz-5-povýšení-schválených-kandidátů)
- [6. Jak se důkaz páruje s chunkem](#cz-6-jak-se-důkaz-páruje-s-chunkem)
- [7. Spuštění offline evaluace](#cz-7-spuštění-offline-evaluace)
- [8. Historický baseline Phase 3.4 (2026-10-20)](#cz-8-historický-baseline-phase-34-2026-10-20)

</details>

---

<a id="cz"></a>

**Pracovní adresář:** Příkazy spouštěj z `rag_api_project/`. Níže uvedené cesty k datasetům a PDF jsou relativní k tomuto projektovému adresáři.

> **Pravidlo:** Skutečné DEV/RANDOM/TEST datasety jsou chráněné. Generování kandidátů je nesmí upravovat. Povýšení kandidátů vyžaduje výslovný souhlas člověka a TEST nesmí sloužit k ladění.

<a id="cz-1-co-je-golden-evidence"></a>

## 1. Co je golden evidence?

Golden evidence (referenční důkaz) není odpověď vytvořená LLM. Je to **ověřitelný textový fragment z konkrétní fyzické PDF stránky**, který prokazatelně podporuje danou otázku. V tomto projektu ho tvoří trojice:

- `source`: přesný název zdrojového PDF;
- `pages`: seznam fyzických stránek PDF číslovaných od 1, nikoli čísla vytištěná uvnitř dokumentu;
- `contains_any`: jeden nebo více doslovných fragmentů podporujícího textu; mezi fragmenty platí logické **OR**.

Evaluační otázka má navíc `id`, `topic` a `question`. Příklad **pouze formátu** (není to ověřená golden evidence a nesmí se přímo přidat do datasetu):

```json
[
  {
    "id": "routing_dev_example",
    "topic": "routing",
    "question": "Example question about a documented routing fact?",
    "gold_evidence": [
      {
        "source": "Example_Manual.pdf",
        "pages": [12],
        "contains_any": ["Exact evidence fragment copied from the source PDF"]
      }
    ]
  }
]
```

Jedna otázka může mít více objektů `gold_evidence`, pokud ji nezávisle podporuje více pasáží. Fragmenty musí skutečně odpovídat textu ze zdrojového PDF; nevymýšlej je, neupravuj je podle retrieval výsledků a nevybírej fragmenty pouze proto, že je vyhledávač vrací.


<a id="cz-2-rozdělení-datasetů"></a>

## 2. Rozdělení datasetů

| Dataset | Soubor | Úloha |
| --- | --- | --- |
| DEV | `eval/dev_questions.json` | Vývoj a měřené změny |
| RANDOM | `eval/random_questions.json` | Robustnost, nové typy selhání |
| TEST | `eval/test_questions.json` | Oddělená závěrečná kontrola; nikoli tuning |

Historický rozsah projektu: DEV 20, RANDOM 25 a TEST 15 otázek. Konkrétní počet ověř při načtení datasetu a u každého měření zaznamenej hash. Přehledové soubory mohou obsahovat starší naměřené hodnoty; samotný nový běh je autoritativní pro daný commit a lokální korpus.


<a id="cz-3-jak-vytvořit-nový-důkaz-evidence--question"></a>

## 3. Jak vytvořit nový důkaz: evidence → question

1. Vezmi **původní lokální PDF** z `data/`. Nepoužívej internet jako zdroj referenčního textu.
2. Objev relevantní fyzickou stránku přes samostatný page explorer:

   ```powershell
   python -m scripts.search_pdf "OSPF router ID" --top-k 10 --interactive
   ```
3. Ručně ověř, zda pasáž opravdu odpovídá na jednu konkrétní otázku, a zapiš přesný název PDF, číslo fyzické stránky a stabilní doslovný fragment.
4. **Teprve podle ověřené pasáže** formuluj otázku (evidence → question). Nekonstruuj nejprve otázku a nehledej dodatečně přibližně odpovídající text.
5. Zkontroluj duplicity vůči DEV/RANDOM, vyváženost témat a jednoznačnost odpovědi. Duplicity vůči TEST nech ověřit skriptem; ručně jeho obsah při ladění neprocházej.
6. Ulož kandidátní JSON pouze do `eval/candidates/`, například `eval/candidates/new_batch.json`. Kurátor má standardně připravit pět kandidátů na dávku, pokud zadání neurčuje jinak.

Page explorer používá BM25 index *stránek*. Vyhodnocované retrievery pracují s chunky z Chroma. Výsledek page exploreru **není automaticky správná golden evidence**.


<a id="cz-4-validace-kandidátů"></a>

## 4. Validace kandidátů

```powershell
# Spusť z rag_api_project/; new_batch.json je zástupný název.
python -m scripts.validate_eval_candidates eval/candidates/new_batch.json
```

Skript načte existující DEV/RANDOM/TEST datasety a porovná ID a normalizované texty otázek. Validátor porovnává doslovné fragmenty s původním lokálním PDF textem po normalizaci velikosti písmen a whitespace. Současná opravená implementace ověřuje každou deklarovanou stránku a odmítá duplicitní normalizované otázky uvnitř jedné dávky.

Strukturální loader vyžaduje neprázdné texty, neprázdné seznamy důkazů/fragmentů a kladná celočíselná čísla stránek (ne `true`/`false`). Na **každé** uvedené stránce musí být alespoň jeden fragment; různé stránky mohou odpovídat různým fragmentům. Validátor však nezaručuje ověření **každého** fragmentu z `contains_any`: všechny alternativy musí ručně ověřit kurátor. Prázdné stránky bez extrahovatelného textu nejsou v lookupu; hláška o chybějícím source/page tak nemusí znamenat neexistující fyzickou stránku. OCR není součástí workflow.

Skripty kontrolují pouze existující chráněné datasety, nikoli ostatní dávky v `eval/candidates/`; chybějící dataset přeskočí. Před validací ověř přítomnost všech tří datasetů. Duplicity faktů/parafrází vyžadují ruční kontrolu DEV/RANDOM. `--data-dir <adresář>` určuje korpus pro validaci i povýšení a nepřebírá `RAG_DATA_DIR`.

Revize 2026-10-28: všech sedm verzovaných dávek má platnou strukturu (5 položek každá), ale všech 35 ID už existuje v chráněných datasetech. Jde o historické dávky, nikoli nové kandidáty k opětovnému povýšení; úplná validace je správně odmítne jako kolize ID. Skutečnou shodu fragmentů s PDF tím tato revize nepotvrzuje.

Úspěch vypíše například `VALID: 5 candidate(s)`. To **neznamená automatické schválení kvality**: člověk musí stále ověřit, zda fragment skutečně dokládá celou odpověď a zda stránka a otázka dávají věcný smysl.

Pokud validace selže, oprav **pouze kandidátní JSON**, ne validátor ani stávající golden evidence. Validátor nemá být oslabován kvůli průchodu chybné dávky.


<a id="cz-5-povýšení-schválených-kandidátů"></a>

## 5. Povýšení schválených kandidátů

Povýšení do skutečného datasetu je **zvláštní, zapisující a chráněná operace**. Kurátorský agent ji nesmí provádět. Následující syntaxe je určena výhradně pro člověkem schválené ID a cílový dataset (příklady jsou zástupné):

```powershell
python -m scripts.promote_eval_candidates eval/candidates/new_batch.json eval/dev_questions.json --ids routing_dev_101
```

Před spuštěním zkontroluj zdroj, cílový soubor a seznam ID; zálohuj schválený dataset a počítej s tím, že příkaz soubor **změní**. U změn chráněných souborů platí GitHub governance v `.github/workflows/eval-governance.yml` včetně lidského schválení. Nikdy automaticky nepovyšuj kandidáty do TEST pro následné ladění.

`--ids` přijímá jedno nebo více ID oddělených mezerami. Skript znovu validuje pouze vybrané kandidáty a přepíše celý cílový JSON bez automatické zálohy a bez kontroly lidského schválení. Schválení je procesní hranice, nikoli CLI přepínač. CI kontroluje u kandidátů pouze **strukturu**, ne shodu se soukromými PDF. Po lidské revizi chráněných změn musí oprávněný člověk přidat label `human-approved-eval-change`. Workflow nereaguje na samotné přidání labelu a opakování starého běhu může používat starý payload; pro ověření zajisti nový PR běh s aktuálními labely.


<a id="cz-6-jak-se-důkaz-páruje-s-chunkem"></a>

## 6. Jak se důkaz páruje s chunkem

`evaluation/evidence.py` normalizuje text pomocí `casefold()` a sjednocení whitespace. Chunk se považuje za shodný, pokud v rámci **jednoho GoldEvidence objektu** sedí název zdroje, jeho fyzická stránka patří do `pages`, a text chunku obsahuje alespoň jeden fragment z `contains_any`.

`first_evidence_rank` je první pozice shodného chunku v seřazených výsledcích, od 1; `None` znamená, že se shodný důkaz v kontrolovaných výsledcích nenašel. **Neznamená to**, že retriever nevrátil žádné dokumenty. Z prvních pozic se počítají MRR a Hit@1/3/5/8.

Pozor: validátor fragmenty ověřuje vůči textu extrahovanému ze *stránky*, zatímco evaluátor požaduje přítomnost fragmentu uvnitř konkrétního *chunku*. Příliš dlouhý fragment přes hranici chunků může dát falešné neúspěchy. Při tvorbě referencí proto používej krátké, ale dostatečně specifické, nezávisle ověřené pasáže.


<a id="cz-7-spuštění-offline-evaluace"></a>

## 7. Spuštění offline evaluace

```powershell
python -m scripts.evaluate_retrieval --retriever legacy --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset dev
python -m scripts.evaluate_retrieval --retriever bm25 --dataset dev
python -m scripts.evaluate_retrieval --retriever vector --dataset random
python -m scripts.evaluate_retrieval --retriever bm25 --dataset random
```

Aktuální zveřejněné CLI podporuje retrievery `legacy`, `vector`, `bm25` a datasety `dev`, `random`. Experimentální hybrid ani `test` nejsou publikovanou volbou.

Každý běh: vypíše individuální `FIRST_EVIDENCE_RANK`, `RECIPROCAL_RANK`, agregované MRR, Hit@K, latency mean/P50/P95 a **zapíše** JSONL historii do `eval/results/`. Historie je rozdělená podle retrieveru a datasetu, uchovává maximálně 10 běhů na soubor a obsahuje timestamp, Git commit/dirty, hash datasetu a retrieval config. Při porovnávání musí souhlasit verze PDF, indexu, dataset hash i konfigurace.

**Výkonnost:** reportovaná latency měří vyhledávací `search()`, nikoli inicializaci indexu, generování LLM nebo celý HTTP request. Pro seriózní porovnání používej warm-up a opakování.

Pro reprodukci ulož mimo automatickou historii také SHA-256 každého PDF, identitu/snapshot indexu a počet chunků, parametry ingestu, verze a revize modelů, Python/balíčky, OS/hardware a postup warm-upu. Tyto údaje se automaticky neukládají a dirty příznak neuchovává samotný diff. Historii exportuj před rotací. CLI neprovádí warm-up ani nemá parametr pro opakování; měří i první `search()`. `--dataset random` zde vyhodnotí **celý** pevný RANDOM dataset, nikoli nový náhodný vzorek. Starší `scripts.evaluate_random` má samostatné neopravené chyby v historii, Git statusu a výpisu metrik; pro tento postup použij `scripts.evaluate_retrieval --dataset random`.


<a id="cz-8-historický-baseline-phase-34-2026-10-20"></a>

## 8. Historický baseline Phase 3.4 (2026-10-20)

| Dataset | Retriever | MRR | Hit@1 | Hit@3 | Hit@5 | Hit@8 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| DEV (20) | BM25 | 0.7171 | 0.60 | 0.80 | 0.85 | 0.90 |
| DEV (20) | Vector | 0.8321 | 0.75 | 0.90 | 0.90 | 0.95 |
| RANDOM (25) | BM25 | 0.8133 | 0.72 | 0.92 | 0.92 | 0.92 |
| RANDOM (25) | Vector | 0.6050 | 0.44 | 0.72 | 0.80 | 0.84 |

MRR jsou doložena v [deníku učení](LEARNING_LOG.md#cz-2026-10-20--fáze-34-evaluace-retrievalu). Hodnoty Hit@K pocházejí z předchozího pracovního reportu a bez původních JSONL běhů je nelze nezávisle potvrdit. Původní běhy, korpus ani index nejsou součástí tohoto veřejného snapshotu; hodnoty nebyly pro tuto úpravu dokumentace znovu reprodukovány. Jde o metriky retrievalu, nikoli o přesnost generovaných odpovědí. Nejsou zárukou stejného výsledku při změně dat nebo prostředí. Latency jednotlivých krátkých běhů nepovažuj za finální benchmark. TEST zůstává nedotčený.

[↑ Nahoru](#top)
