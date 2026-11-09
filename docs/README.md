<a id="dokumentace-ai-rag--ai-rag-documentation"></a>

# Dokumentace Local RAG API / Local RAG API documentation

Veškerá verzovaná Markdown dokumentace je v této složce. Výjimkou jsou [hlavní README](../README.md) a vstupní `AGENTS.md` v kořeni a příslušných modulech; ty odkazují na zde uložená pravidla. / Exceptions are the [root README](../README.md) and root/module `AGENTS.md` entry points, which link to the rules stored here.

Příručky mají samostatný obsah kapitol a závěrečný odkaz nahoru. / Guides have chapter contents and a final back-to-top link.

## První návštěva / First visit

| Co hledáš / What to inspect | Česky | English |
| --- | --- | --- |
| Co projekt řeší a obsahuje / Problem and implemented features | [Přehled projektu](cs/PROJECT.md#cz) | [Project overview](en/PROJECT.md#en) |
| Zaznamenané výsledky a jejich omezení / Recorded results and limits | [Historický baseline](cs/EVALUATION.md#cz-8-historický-baseline-phase-34-2026-10-20) | [Historical baseline](en/EVALUATION.md#en-8-historical-baseline-2026-10-20) |
| Jak jej spustit / Run locally | [Provozní příručka](cs/OPERATIONS.md#cz) | [Operations runbook](en/OPERATIONS.md#en) |

## Všechny příručky / All guides

| Oblast / Topic | Česky | English |
| --- | --- | --- |
| Přehled repozitáře / Repository overview | [Česky](cs/README.md#cz) | [English](../README.md#en) |
| Přehled RAG projektu / RAG project overview | [Česky](cs/PROJECT.md#cz) | [English](en/PROJECT.md#en) |
| Instalace a provoz / Setup and operations | [Česky](cs/OPERATIONS.md#cz) | [English](en/OPERATIONS.md#en) |
| Golden evidence a evaluace / Golden evidence and evaluation | [Česky](cs/EVALUATION.md#cz) | [English](en/EVALUATION.md#en) |
| Pravidla kurátora / Curator rules | [Česky](cs/EVAL_CURATOR_AGENT.md#cz) | [English](en/EVAL_CURATOR_AGENT.md#en) |
| Architektura / Architecture | [Česky](cs/ARCHITECTURE.md#cz) | [English](en/ARCHITECTURE.md#en) |
| Plán fází / Phase plan | [Česky](cs/ROADMAP.md#cz) | [English](en/ROADMAP.md#en) |
| Vývoj a revize / Development and review | [Česky](cs/DEVELOPMENT_GUIDE.md#cz) | [English](en/DEVELOPMENT_GUIDE.md#en) |
| Experiment n8n / LangGraph / Codex | [Česky](cs/DEV_LOOP.md#cz) | [English](en/DEV_LOOP.md#en) |
| Ovládací formulář n8n / n8n operator form | [Česky](cs/DEV_LOOP_N8N_CONTROL.md) | [English](en/DEV_LOOP_N8N_CONTROL.md) |
| Deník učení / Learning log | [Česky](cs/LEARNING_LOG.md#cz) | [English](en/LEARNING_LOG.md#en) |

## Pravidla agentů / Agent rules

Před změnou souborů načti globální pravidla a pro práci na RAG také projektová pravidla. Umístění dokumentů nemění jejich působnost. Vstupem pro agenty je také [kořenový AGENTS.md](../AGENTS.md). / Before changing files, read the repository rules and, for RAG work, the project rules. Their storage location does not narrow their scope. The [root AGENTS.md](../AGENTS.md) is also an agent entry point.

| Pravidla / Rules | Česky | English |
| --- | --- | --- |
| Globální / Repository-wide | [Česky](cs/AGENTS.md#cz) | [English](en/AGENTS.md#en) |
| Dev-loop dohody / Dev-loop agreements | [Česky](cs/DEV_LOOP_POLICY.md) | [English](en/DEV_LOOP_POLICY.md) |
| RAG projekt / RAG project | [Česky](cs/PROJECT_AGENTS.md#cz) | [English](en/PROJECT_AGENTS.md#en) |

## Další dokumenty / Other documents

Soubory `ARCHITECTURE.md`, `ROADMAP.md`, `DEVELOPMENT_GUIDE.md`, `OPERATIONS.md`, `EVALUATION.md` a `EVAL_CURATOR_AGENT.md` přímo v `docs/` jsou rozcestníky na jazykové verze a kapitoly. / These files directly under `docs/` are navigation pages for the language versions and chapters.

## Odkazy a údržba / Links and maintenance

Při změně návodu aktualizuj oba jazyky. Příkazy pro aplikaci, ingest, PDF a evaluaci se spouštějí z `rag_api_project/`; umístění příručky tento pracovní adresář nemění. / Keep both languages synchronized. Application, ingestion, PDF and evaluation commands run from `rag_api_project/`; the guide location does not change that working directory.

Pravidla agentů a kurátora v obou jazycích chrání CODEOWNERS a Eval Governance. Změny chráněných pravidel vyžadují lidské schválení. / CODEOWNERS and Eval Governance protect agent and curator instructions in both languages; protected-rule changes require human approval.
