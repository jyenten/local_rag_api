<a id="top"></a>

# Pokyny pro agenty

[Česky](#cz) · [English](../en/PROJECT_AGENTS.md#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Obsah — kliknutím rozbalit</summary>

- [Kurátorství evaluačních datasetů](#cz-kurátorství-evaluačních-datasetů)
- [Provozní a evaluační postupy](#cz-provozní-a-evaluační-postupy)

</details>

---

<a id="cz"></a>

**Působnost:** Tato pravidla platí pro práci v `rag_api_project/` společně s [globálními pravidly](AGENTS.md). Cesty začínající `docs/` jsou relativní ke kořeni repozitáře; provozní příkazy se spouštějí z `rag_api_project/`.

<a id="cz-kurátorství-evaluačních-datasetů"></a>

## Kurátorství evaluačních datasetů

Při generování nebo správě evaluačních datasetů:

- Řiď se `docs/cs/EVAL_CURATOR_AGENT.md`.
- Generované evaluační kandidáty zapisuj pouze do `eval/candidates/`.
- Nikdy neměň:
  - `eval/dev_questions.json`
  - `eval/random_questions.json`
  - `eval/test_questions.json`
  - implementaci retrievalu
  - evaluační metriky
- Nikdy automaticky nepovyšuj kandidáty.
- Povýšení vyžaduje lidské schválení.
- Každá dávka kandidátů musí úspěšně projít:

```bash
python -m scripts.validate_eval_candidates <candidate-file>
```

- Neoslabuj ani neobcházej validaci kvůli přijetí kandidáta.
- Gold evidence musí pocházet pouze z lokálních PDF v `data/`.
- Používej fyzická čísla stránek PDF.
- Dodržuj postup evidence -> otázka.


<a id="cz-provozní-a-evaluační-postupy"></a>

## Provozní a evaluační postupy

[OPERATIONS.md](OPERATIONS.md#cz) používej pro **anglické/české** příkazy instalace, ingestu, API, Dockeru a testů; [EVALUATION.md](EVALUATION.md#cz) pro golden evidence, metriky, validaci a povýšení schválené člověkem. Tyto dokumenty vysvětlují postupy; tento soubor určuje oprávnění agentů.

- Před navržením nebo spuštěním ingestu zkontroluj `scripts/ingest.py` a vybraný korpus/kolekci. Ingest nyní kolekci **smaže a znovu vytvoří**. Destruktivní ingest nikdy nespouštěj bez výslovného oprávnění a rozhodnutí o záloze.
- Při správě evidence zachovej výše uvedená pravidla: pouze zdrojová PDF, fyzické stránky a nejprve evidence. Validace kandidáta **neopravňuje** k jeho povýšení.
- Oddělený `eval/test_questions.json` nikdy nepoužívej k ladění ani k opakovanému rozboru chyb retrievalu.
- Nikdy nepřepisuj existující DEV/RANDOM/TEST gold evidence, metriky ani historii baseline jako automatický způsob zlepšení výsledků.
- Při změně evaluačního validačního kódu přidej regresní testy (včetně více stránek evidence) a zkontroluj pravidla CI pro chráněné soubory.
- Kvůli aktualizaci dokumentace neměň `requirements.txt`, lock soubory, architekturu ani parametry retrievalu. Udržuj české a anglické návody synchronizované.

[↑ Nahoru](#top)
