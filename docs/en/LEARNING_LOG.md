<a id="top"></a>

# AI Engineering — Learning Log

[Česky](../cs/LEARNING_LOG.md#cz) · [English](#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Contents — click to expand</summary>

- [Goal](#en-goal)
- [Skill levels](#en-skill-levels)
- [Current project checkpoint](#en-current-project-checkpoint)
- [Historical project checkpoint — 2026-10-12](#en-historical-project-checkpoint--2026-10-12)
- [Historical learning plan: Phase 3.3 — BM25 (2026-10-12)](#en-historical-learning-plan-phase-33--bm25-2026-10-12)
- [Learning entry template](#en-learning-entry-template)
- [YYYY-MM-DD — Topic](#en-yyyy-mm-dd--topic)
- [Learning rules](#en-learning-rules)
- [Project and learning history](#en-project-and-learning-history)
- [2026-05-12 to 2026-05-22 — Python, data analysis and classical ML](#en-2026-05-12-to-2026-05-22--python-data-analysis-and-classical-ml)
- [2026-05-23 to 2026-06-09 — PyTorch, NLP, initial RAG and containers](#en-2026-05-23-to-2026-06-09--pytorch-nlp-initial-rag-and-containers)
- [2026-07-27 to 2026-08-21 — RAG API foundation, diagnostics and CI](#en-2026-07-27-to-2026-08-21--rag-api-foundation-diagnostics-and-ci)
- [2026-09-01 to 2026-09-16 — Retrieval diagnostics and evaluation foundation](#en-2026-09-01-to-2026-09-16--retrieval-diagnostics-and-evaluation-foundation)
- [2026-09-16 to 2026-09-17 — Independent PDF page explorer](#en-2026-09-16-to-2026-09-17--independent-pdf-page-explorer)
- [2026-09-22 to 2026-10-08 — Evidence matching and governed evaluation](#en-2026-09-22-to-2026-10-08--evidence-matching-and-governed-evaluation)
- [2026-10-11 to 2026-10-12 — Vector baseline, latency and agent rules](#en-2026-10-11-to-2026-10-12--vector-baseline-latency-and-agent-rules)
- [2026-10-13 — Phase 3.3: BM25 Retriever](#en-2026-10-13--phase-33-bm25-retriever)
- [2026-10-14 — Portfolio history, agent provenance and security automation](#en-2026-10-14--portfolio-history-agent-provenance-and-security-automation)
- [2026-10-15 to 2026-10-17 — Linux dependency reproducibility proposal](#en-2026-10-15-to-2026-10-17--linux-dependency-reproducibility-proposal)
- [2026-10-20 — Phase 3.4: Retrieval Evaluation](#en-2026-10-20--phase-34-retrieval-evaluation)
- [2026-10-26 — Document store and verified FAISS bundle experiment](#en-2026-10-26--document-store-and-verified-faiss-bundle-experiment)
- [2026-10-26 — Automated GitHub Actions dependency proposal](#en-2026-10-26--automated-github-actions-dependency-proposal)
- [2026-10-28 — Bilingual runbooks, validator regressions and default main](#en-2026-10-28--bilingual-runbooks-validator-regressions-and-default-main)
- [2026-10-28 — Documentation responsibilities and Czech navigation](#en-2026-10-28--documentation-responsibilities-and-czech-navigation)
- [2026-10-28 — Separate documentation languages](#en-separate-documentation-languages)
- [2026-10-28 — Centralized documentation and simpler navigation](#en-centralized-documentation)
- [Uncommitted work observed on 2026-10-28](#en-uncommitted-work-observed-on-2026-10-28)
- [Branch audit coverage — 2026-10-28](#en-branch-audit-coverage--2026-10-28)

- [2026-10-29 — Portfolio documentation and local operation context](#en-2026-10-29-portfolio-documentation)

</details>

---

<a id="en"></a>

<a id="en-goal"></a>

## Goal

Develop independent proficiency in:

- Python programming
- Software architecture and testing
- Git, CI/CD and Docker
- RAG systems and information retrieval
- AI evaluation and observability
- AI agents and agent-assisted development


<a id="en-skill-levels"></a>

## Skill levels

- NOT ASSESSED — no independent demonstration yet
- GUIDED — completed with explanations or assistance
- INDEPENDENT — implemented and explained without assistance
- PROFICIENT — independently applied in a different problem

A completed project feature does not automatically
mean the corresponding skill is mastered.


<a id="en-current-project-checkpoint"></a>

## Current project checkpoint

Date: 2026-10-29
Default branch: main
Reviewed project commit: 82d5889 (before this log update)

- PRs #6–#8 are merged: portfolio evidence, the Local RAG API name and canonical
  `jyenten/local_rag_api` links are integrated. PR #2's `setup-python` update is
  also merged; it does not integrate the separate dependency-lock proposal.
- Latest verified GitHub CI on `main`: **223 passed in 7.29s**
  ([run 40865587005](https://github.com/jyenten/local_rag_api/actions/runs/40865587005)).
- Gitleaks and CodeQL passed on that revision. Dependency Audit still fails with
  the same known ChromaDB advisory set; it remains enabled without an exception.
- BM25 and Vector DEV/RANDOM baselines are preserved. They were not rerun for
  this log update; held-out TEST remains unchanged.
- Hybrid RRF and retriever-ID interface work remain local and uncommitted.
- The Linux dependency-lock proposal (PR #1) remains open; the local FAISS/storage
  experiment is also separate from the integrated `main` state.

Project completion and human skill assessment remain separate. The existing
GUIDED assessments below are preserved; this history review assigns no new
INDEPENDENT or PROFICIENT rating.


<a id="en-historical-project-checkpoint--2026-10-12"></a>

## Historical project checkpoint — 2026-10-12

Date: 2026-10-12
Branch: document-search-bm25
Commit: 9ed9985

Completed in the project:

- FastAPI RAG foundation
- PDF processing and Chroma vector storage
- Vector retrieval baseline
- Evaluation datasets and retrieval metrics
- DEV / RANDOM / held-out TEST separation
- Retrieval latency measurement
- JSONL evaluation history
- Git provenance checks
- Automated testing and GitHub CI

Last verified full test suite:
142 passed, 1 skipped.

These are project achievements, not independent
skill assessments.


<a id="en-historical-learning-plan-phase-33--bm25-2026-10-12"></a>

## Historical learning plan: Phase 3.3 — BM25 (2026-10-12)

Topic:
Lexical retrieval over existing Chroma chunks.

Learning objectives:

- Explain how BM25 ranks documents.
- Understand tokenization, TF, IDF and document length.
- Implement retrieval ranking in Python.
- Preserve source and page metadata.
- Write meaningful unit and integration tests.
- Compare BM25 with vector retrieval.

Independent exercise:

Implement BM25Retriever.search() and explain the
ranking and tie-breaking behavior.

Current skill assessment:
NOT ASSESSED


<a id="en-learning-entry-template"></a>

## Learning entry template


<a id="en-yyyy-mm-dd--topic"></a>

### YYYY-MM-DD — Topic

What I worked on:

- To be filled in.

Concepts I learned:

- To be filled in.

What I implemented independently:

- To be filled in.

What Codex or ChatGPT implemented:

- To be filled in.

Problems I diagnosed:

- To be filled in.

Tests and evidence:

- To be filled in.

Skill level:
NOT ASSESSED / GUIDED / INDEPENDENT / PROFICIENT

Next exercise:

- To be filled in.


<a id="en-learning-rules"></a>

## Learning rules

Update this log after meaningful milestones,
not after every small code change.

Record difficulties and misunderstandings.
Do not inflate skill assessments.
Revisit weak topics through independent exercises.


<a id="en-project-and-learning-history"></a>

## Project and learning history

The retrospective entries added on 2026-10-28 are reconstructed from commit
history, selected source/test changes, PR state and local worktree status.
Dates describe recorded commits, not verified study time. Concepts listed are
present in the work; Git authorship alone does not prove independent human
implementation, understanding or the extent of AI assistance. Attribution is
stated only where the existing log or observed collaboration establishes it.
Historical scripts and experimental tests were not rerun during this log audit.


<a id="en-2026-05-12-to-2026-05-22--python-data-analysis-and-classical-ml"></a>

### 2026-05-12 to 2026-05-22 — Python, data analysis and classical ML

**Project evidence:** Exercises originally recorded on the history now retained
by `master`, subsequently inherited by `main` and moved under `archive/`.

- Python input, conditions, loops, functions and collections; later Pandas CSV
  analysis, filtering/grouping, missing values and Matplotlib plots.
- Linear regression, classification, cross-validation/overfitting,
  RandomForest, feature engineering and a complete ML exercise.
- Concepts to consolidate: train/test separation, reproducible splits,
  preprocessing and interpreting metrics rather than only fitting a model.
- Evidence: [initial days 1–4, 8daf3fa](https://github.com/jyenten/local_rag_api/commit/8daf3fa),
  [Pandas, 909b475](https://github.com/jyenten/local_rag_api/commit/909b475),
  [complete ML exercise, 1c852a6](https://github.com/jyenten/local_rag_api/commit/1c852a6).


<a id="en-2026-05-23-to-2026-06-09--pytorch-nlp-initial-rag-and-containers"></a>

### 2026-05-23 to 2026-06-09 — PyTorch, NLP, initial RAG and containers

**Project evidence:** Archived learning exercises, already included in `main`.

- PyTorch networks, CNN/image classification, transfer learning and ResNet18.
- NLP sentiment classification, embeddings, BERT/tokenizers, attention and
  Hugging Face pipeline/QA experiments.
- Initial RAG experiments followed by FastAPI and Docker application exercises.
- Concepts to consolidate: tensor/model interfaces, tokenization, retrieval
  versus generation, package compatibility and container runtime boundaries.
- Evidence: [PyTorch, 1c05b12](https://github.com/jyenten/local_rag_api/commit/1c05b12),
  [BERT, 4097483](https://github.com/jyenten/local_rag_api/commit/4097483),
  [Hugging Face QA, 1441c8a](https://github.com/jyenten/local_rag_api/commit/1441c8a),
  [Docker/RAG API, f57517e](https://github.com/jyenten/local_rag_api/commit/f57517e).


<a id="en-2026-07-27-to-2026-08-21--rag-api-foundation-diagnostics-and-ci"></a>

### 2026-07-27 to 2026-08-21 — RAG API foundation, diagnostics and CI

**Project milestone:** Historical `master` foundation; included in `main`.

- Improved PDF cleaning/chunking, retrieved context and alignment of sources
  with selected context; added source metadata to API responses.
- Added health/stats/readiness endpoints, blank-question validation and handling
  for unavailable RAG services; added Docker and Compose setup.
- Added API checks, a test Chroma setup, smoke tests and GitHub Actions CI.
- Concepts covered: service readiness versus liveness, traceable responses,
  typed API boundaries, test isolation and repeatable development checks.
- Evidence: [source metadata, 581d6f6](https://github.com/jyenten/local_rag_api/commit/581d6f6),
  [readiness, 6950495](https://github.com/jyenten/local_rag_api/commit/6950495),
  [CI/smoke tests, 702c0ab](https://github.com/jyenten/local_rag_api/commit/702c0ab),
  [`master` tip, 3c0bfdd](https://github.com/jyenten/local_rag_api/commit/3c0bfdd).


<a id="en-2026-09-01-to-2026-09-16--retrieval-diagnostics-and-evaluation-foundation"></a>

### 2026-09-01 to 2026-09-16 — Retrieval diagnostics and evaluation foundation

**Project milestone:** Included in `main`; `retrieval-eval-refactor` retains an
early checkpoint of this development, not the final evaluation implementation.

- Added retrieval diagnostics, revised preprocessing/chunking with regression
  tests, initial DEV retrieval evaluation and evaluation-history tooling.
- Recorded architecture, roadmap and development rules.
- Concepts covered: diagnosing retrieval separately from generation, chunk
  boundaries/overlap, evidence-based evaluation and bounded development scope.
- Evidence: [chunking regressions, 26b39e6](https://github.com/jyenten/local_rag_api/commit/26b39e6),
  [initial evaluation, 2fafcae](https://github.com/jyenten/local_rag_api/commit/2fafcae),
  [`retrieval-eval-refactor` tip, 010d8d1](https://github.com/jyenten/local_rag_api/commit/010d8d1).


<a id="en-2026-09-16-to-2026-09-17--independent-pdf-page-explorer"></a>

### 2026-09-16 to 2026-09-17 — Independent PDF page explorer

**Project milestone:** Implemented and included in `main`.

- Added page/search data models, normalization/tokenization, PDF loading,
  path/PDF/input validation, BM25 indexing/search and an interactive CLI.
- Added synthetic tests, development checks and automatic test watching.
- Concepts covered: immutable models, source/page identity, resource limits,
  lexical ranking and keeping page-level discovery separate from chunk retrieval.
- Evidence: [safe PDF loading, f05e080](https://github.com/jyenten/local_rag_api/commit/f05e080),
  [BM25 search, 4a0fa06](https://github.com/jyenten/local_rag_api/commit/4a0fa06),
  [page-explorer CLI, 1f3fad5](https://github.com/jyenten/local_rag_api/commit/1f3fad5).


<a id="en-2026-09-22-to-2026-10-08--evidence-matching-and-governed-evaluation"></a>

### 2026-09-22 to 2026-10-08 — Evidence matching and governed evaluation

**Project milestone:** Implemented and included in `main`.

- Split evaluation into models, dataset loading, evidence matching, metrics,
  runner and JSONL history; added reproducible random sampling.
- Added DEV/RANDOM/held-out TEST separation, candidate validation/promotion
  tools, curator rules, CODEOWNERS and evaluation-governance CI.
- Concepts covered: physical PDF page numbers, normalized literal fragments,
  MRR/Hit@K, random seeds, dataset leakage and human approval boundaries.
- Evidence: [dataset models, f0b30b8](https://github.com/jyenten/local_rag_api/commit/f0b30b8),
  [evidence matching, 8e93ce5](https://github.com/jyenten/local_rag_api/commit/8e93ce5),
  [runner/metrics, ed6bf73](https://github.com/jyenten/local_rag_api/commit/ed6bf73),
  [random sampling, 3247ab4](https://github.com/jyenten/local_rag_api/commit/3247ab4),
  [governance, 8aae380](https://github.com/jyenten/local_rag_api/commit/8aae380).
- Later review identified defects in the older `scripts.evaluate_random`;
  historical implementation does not mean every legacy CLI is currently sound.
  The supported comparison procedure is documented in
  [EVALUATION.md](EVALUATION.md).


<a id="en-2026-10-11-to-2026-10-12--vector-baseline-latency-and-agent-rules"></a>

### 2026-10-11 to 2026-10-12 — Vector baseline, latency and agent rules

**Project milestone:** Implemented and included in `main`.

- Added a standalone VectorRetriever baseline, retriever selection in evaluation,
  retrieval-only latency mean/p50/p95 and stricter run/history validation.
- Added tests for CLI selection, latency, models/history and Git provenance.
- Added repository-level LEARN/IMPLEMENT/REVIEW rules and this learning log.
- Concepts covered: stable retriever interfaces, measurement boundaries,
  reproducible run metadata and separating project completion from skill mastery.
- Evidence: [vector/observability, 9ed9985](https://github.com/jyenten/local_rag_api/commit/9ed9985),
  [agent rules/log, 50797d4](https://github.com/jyenten/local_rag_api/commit/50797d4).


<a id="en-2026-10-13--phase-33-bm25-retriever"></a>

### 2026-10-13 — Phase 3.3: BM25 Retriever

**Project milestone:** Completed

- Implemented `BM25Retriever` over existing Chroma chunks with guided learning.
- Implemented corpus loading, validation, tokenization, lexical matching, ranking and top-k selection.
- Codex independently prepared regression tests.
- Tests passed code review and were integrated.
- Full regression: 210 passed, 1 skipped, 2 warnings.
- Commit: `c101680` (pushed to origin/document-search-bm25).

**Learning evidence:**

- Practiced Python collections, list comprehensions, `enumerate()`, `sorted()`, `lambda` and data validation.
- Practiced distinguishing document indices from relevance scores.
- Understood the purpose of deterministic tie-breaking and lexical filtering.
- Required guidance and corrections during implementation.

**Skill assessment:** GUIDED

**Next independent exercise:** Explain and modify retrieval ranking without step-by-step assistance.

**Next project milestone:** BM25 vs. Vector evaluation on DEV, followed by RANDOM.


<a id="en-2026-10-14--portfolio-history-agent-provenance-and-security-automation"></a>

### 2026-10-14 — Portfolio history, agent provenance and security automation

**Project milestone:** Included in `main`.

- Moved earlier exercises under `archive/` without rewriting their contents;
  refreshed portfolio/project READMEs and disclosed AI-assisted development.
- Documented nested agent rules, the local BM25-test worktree and manually
  synchronized private-mirror workflow. The existing BM25 entry attributes
  regression-test preparation to Codex; no broader independent authorship is inferred.
- Added Gitleaks, Dependabot, Dependency Review and scheduled/PR dependency audit.
- Concepts covered: exact staging, preserving learning evidence, isolated agent
  work, secret scanning and distinguishing a passing test suite from dependency safety.
- Evidence: [archive move, d157023](https://github.com/jyenten/local_rag_api/commit/d157023),
  [agent provenance, 646525d](https://github.com/jyenten/local_rag_api/commit/646525d),
  [secret scanning, b032e9a](https://github.com/jyenten/local_rag_api/commit/b032e9a),
  [dependency audit, 6a20b25](https://github.com/jyenten/local_rag_api/commit/6a20b25).


<a id="en-2026-10-15-to-2026-10-17--linux-dependency-reproducibility-proposal"></a>

### 2026-10-15 to 2026-10-17 — Linux dependency reproducibility proposal

**Project milestone:** Implemented on `chore/linux-lock-ci`, **not merged** into
`main`; [PR #1](https://github.com/jyenten/local_rag_api/pull/1) remains open.

- Added a Linux/Python 3.11 dependency snapshot, clean Ubuntu installation
  verification, direct-dependency/lock consistency checks and CI lock installation.
- Added a separate ChromaDB risk-assessment document on that branch.
- Concepts covered: direct versus transitive dependencies, OS-specific locks,
  `pip check`, clean-environment validation and security risk tracking.
- Evidence: [snapshot workflow, 4b26db1](https://github.com/jyenten/local_rag_api/commit/4b26db1),
  [lock checker, 8e2e7ec](https://github.com/jyenten/local_rag_api/commit/8e2e7ec),
  [branch tip, a258e85](https://github.com/jyenten/local_rag_api/commit/a258e85).
- [Historical PR CI](https://github.com/jyenten/local_rag_api/actions/runs/39022965393)
  passed at that tip, while dependency-security checks failed. This is not
  approval of those dependency versions or proof that `main` uses the lock.


<a id="en-2026-10-20--phase-34-retrieval-evaluation"></a>

### 2026-10-20 — Phase 3.4: Retrieval Evaluation

**Project milestone:** Completed

- Integrated BM25 into the evaluation CLI using a retriever registry.
- Extended parametrized CLI tests for legacy, vector and BM25.
- Full regression suite passed.
- Evaluated BM25 and Vector on DEV (20 questions)
  and RANDOM (25 questions).
- Preserved the held-out TEST dataset.

**Baseline MRR:**

- DEV: BM25 0.7171, Vector 0.8321
- RANDOM: BM25 0.8133, Vector 0.6050

**Learning evidence:**

- Practiced dictionary lookup and registry pattern.
- Practiced exception chaining with `raise ... from exc`.
- Practiced `getattr()`, parametrized pytest tests
  and debugging `KeyError` and `ImportError`.
- Required guidance during implementation.

**Skill assessment:** GUIDED

**Next project milestone:** Hybrid retrieval using RRF.


<a id="en-2026-10-26--document-store-and-verified-faiss-bundle-experiment"></a>

### 2026-10-26 — Document store and verified FAISS bundle experiment

**Project milestone:** Committed only on local `experiment/vector-backend` at
`14159ce`; **not present in the public `main` branch**.

- Added `DocumentStore` with JSON loading, ID/text/source/page validation and
  duplicate-ID rejection.
- Added FAISS/index-record count checks and a verified-bundle loader that checks
  SHA-256 values against a manifest before loading the bundle.
- Added committed storage regression tests for valid/invalid records, bundles
  and checksums. Their presence was inspected; this audit did not execute them
  or establish a passing test count.
- Concepts covered: stable document IDs, separating vector index and metadata,
  integrity versus authenticity, validation before loading and regression tests.
- The branch descends from the **unmerged Linux-lock proposal**, so it cannot be
  treated as an isolated, reviewed change already integrated into `main`.
- An additional FAISS-retriever test is untracked in its worktree. A completed
  FAISS retriever or Chroma replacement is not established by this storage commit.
- Human/AI implementation split and independent explanation were not established
  from the available evidence; no new skill rating is assigned.


<a id="en-2026-10-26--automated-github-actions-dependency-proposal"></a>

### 2026-10-26 — Automated GitHub Actions dependency proposal

**Project milestone:** Bot-authored proposal, **not merged**.

- `dependabot/github_actions/actions/setup-python-7.1.0` at `21a5733` proposes
  `actions/setup-python` 7.0.0 → 7.1.0 in three workflows.
- [PR #2](https://github.com/jyenten/local_rag_api/pull/2) is open. Its historical
  [CI run](https://github.com/jyenten/local_rag_api/actions/runs/40291737972) passed;
  not all security/governance checks passed.
- This records automation activity and a review opportunity, not human
  implementation or a demonstrated new skill.


<a id="en-2026-10-28--bilingual-runbooks-validator-regressions-and-default-main"></a>

### 2026-10-28 — Bilingual runbooks, validator regressions and default main

**Project milestone:** Completed and integrated through
[PR #3](https://github.com/jyenten/local_rag_api/pull/3), merge commit `cbb2928`.

- Codex audited/refined Czech and English READMEs, AGENTS rules, operations,
  architecture/development status and golden-evidence procedures under explicit
  IMPLEMENT + REVIEW delegation.
- Fixed validation of every evidence page and duplicate normalized questions;
  expanded synthetic candidate-validator coverage to 10 cases. Against the
  original validator, three cases reproduced the defects.
- Verified destructive ingest ordering with a fake client, source-page discovery
  and validation with synthetic data, relative links and Compose configuration.
  No real corpus benchmark, real-PDF evidence review or Docker runtime test was claimed.
- After the owner's explicit approval, Eval Governance passed including structure
  checks of all seven candidate batches. The owner separately authorized merge;
  dependency-audit findings remained open and the check stayed enabled.
- Preserved the old independent `main` as `archive/main-initial-20261028`, renamed
  the active default branch to `main`, and aligned CI/runbooks in `bfb1d85`.
  Existing open PR targets were updated; history and datasets were preserved.
- Evidence: [validator fix, 5dffd5b](https://github.com/jyenten/local_rag_api/commit/5dffd5b),
  [regressions, aefaa40](https://github.com/jyenten/local_rag_api/commit/aefaa40),
  [default-branch follow-up, bfb1d85](https://github.com/jyenten/local_rag_api/commit/bfb1d85).
- Verification: Windows **222 passed, 1 skipped** (symlink privileges), two
  dependency warnings; GitHub CI on `main` **223 passed**. These results concern
  the integrated project, not the separate FAISS/lock experiments.
- Concepts covered: evidence-based documentation, meaningful regressions,
  governance boundaries, environment-dependent tests and preserving Git history.
- The observed implementation/audit was agent-assisted; it does not establish
  independent human mastery of these topics.


<a id="en-2026-10-28--documentation-responsibilities-and-czech-navigation"></a>

### 2026-10-28 — Documentation responsibilities and Czech navigation

**Project evidence:** `da6b382` separates the development workflow from the approved
phase plan. DEVELOPMENT_GUIDE.md describes implementation/review practice;
ROADMAP.md owns phase goals and status. Original phase specifications were preserved.

- The subsequent documentation review adds complete Czech counterparts, language
  jumps, collapsible contents and section-return links across tracked Markdown files.
- API identifiers, examples, historical measurements, existing skill assessments
  and approval boundaries are preserved. Translation does not establish a new
  implementation milestone or an independent skill rating.
- Evidence: [documentation split, da6b382](https://github.com/jyenten/local_rag_api/commit/da6b382).


<a id="en-separate-documentation-languages"></a>

### 2026-10-28 — Separate documentation languages

**Project maintenance:** The documentation revision in [PR #4](https://github.com/jyenten/local_rag_api/pull/4) separates full project guides into `rag_api_project/docs/en/` and `rag_api_project/docs/cs/`, with a shared [documentation index](../README.md).

- README, AGENTS and this log retain English/Czech file pairs at their repository/project level.
- Original guide paths retain navigation and chapter bookmarks; relative links and language switches are updated.
- CODEOWNERS and Eval Governance retain existing protections and cover the new Czech agent rules and both curator-guide paths.
- This agent-assisted documentation work changes no retrieval code, dependencies, golden evidence, protected datasets or existing skill assessments.

<a id="en-centralized-documentation"></a>

### 2026-10-28 — Centralized documentation and simpler navigation

**Documentation maintenance:** All versioned Markdown files now live under repository-root `docs/`, except the root `README.md`. Czech and English guides, learning records and agent rules use `docs/cs/` and `docs/en/`; [the documentation index](../README.md) lists their locations.

- Removed repeated links back to the contents; chapter contents and the final back-to-top link remain.
- Updated relative links and the protected paths in CODEOWNERS/Eval Governance; repository and project agent rules retain their scope and must be loaded explicitly through the README references.
- Historical skill assessments, approved roadmap goals, retrieval code, dependencies, golden evidence and DEV/RANDOM/TEST are unchanged.

<a id="en-uncommitted-work-observed-on-2026-10-28"></a>

## Uncommitted work observed on 2026-10-28

These are worktree observations, not dated completed milestones. Their creation
dates and correctness are not inferred from file presence.

- Former `document-search-bm25` worktree: local `rrf_contribution`/`fuse_rankings`
  prototype with deterministic ID tie-breaking; BM25/Vector `search_with_ids`
  interface changes; modified requirements and an untracked Windows lockfile.
  There is no committed/released HybridRetriever integration or verified hybrid
  evaluation result from this work. Dependencies/lockfile are not approved by
  their existence. Other untracked agent experiments were not attributed to a
  versioned milestone.
- `agent/phase3-model-hardening`: the branch tip is the older `8aae380`, with
  uncommitted history/model/CLI/latency/retriever/test changes. Several concerns
  overlap the later integrated vector-baseline milestone; the dirty worktree is
  not evidence of another completed or merged feature.
- `experiment/vector-backend`: committed storage work is distinguished above
  from its untracked FAISS-retriever test. No experimental test-pass claim is made.

The original worktrees and their uncommitted changes were read only and preserved.
Next learning focus remains hybrid RRF with DEV/RANDOM measurement and no TEST
tuning; the storage/backend experiment remains a separate review track.


<a id="en-branch-audit-coverage--2026-10-28"></a>

## Branch audit coverage — 2026-10-28

Seven current public GitHub branches were fetched and inspected. Ancestor
branches are counted once in the history above, rather than as separate
achievements. The inventory is a point-in-time snapshot, not a live status page.

| Public branch | Reviewed tip | Status relative to the reviewed `main` |
| --- | --- | --- |
| `main` | `bfb1d85` | Integrated project and current default |
| `master` | `3c0bfdd` | Historical API/CI foundation; ancestor of `main` |
| `retrieval-eval-refactor` | `010d8d1` | Early roadmap/evaluation checkpoint; ancestor of `main` |
| `docs/bilingual-rag-runbooks-20261028` | `9504b1e` | Merged through PR #3 |
| `chore/linux-lock-ci` | `a258e85` | Unmerged PR #1; lock proposal only |
| `dependabot/github_actions/actions/setup-python-7.1.0` | `21a5733` | Unmerged bot proposal, PR #2 |
| `archive/main-initial-20261028` | `0cb285c` | Preserved independent initial README history |

Eight local branches in the original project clone were also inspected, along
with all five registered worktrees. The current documentation checkout's
`main` and documentation branch are already represented in the public table.

| Original local branch | Reviewed tip | Evidence/state |
| --- | --- | --- |
| `agent/bm25-tests` | `646525d` | Clean worktree; tip already included in `main`; BM25 test provenance documented |
| `agent/phase3-model-hardening` | `8aae380` | Tip included in `main`; dirty audit worktree kept separate |
| `chore/linux-lock-ci` | `a258e85` | Clean worktree; same unmerged proposal as the public branch |
| `document-search-bm25` | `f9cc7e2` | Former default name; dirty hybrid/dependency worktree, not synchronized by this audit |
| `experiment/vector-backend` | `14159ce` | Local-only storage/FAISS commit plus an untracked retriever test |
| `master` | `3c0bfdd` | Same historical checkpoint as the public branch |
| `retrieval-eval-refactor` | `010d8d1` | Same historical checkpoint as the public branch |
| `retrieval-eval-refactor¨` | `3c0bfdd` | Local alias of the `master` checkpoint; no unique milestone |

Cached private-mirror refs `codex-private/main` and
`codex-private/agent/bm25-tests` both pointed to `646525d`, already included in
the public history. Only those local refs were inspected; the live private
remote was not fetched. The obsolete cached `origin/document-search-bm25` in
the documentation checkout is a pre-rename ref, not an eighth current public
branch. No branches, source code, datasets or dependency files were changed by
this learning-log audit.

<a id="en-2026-10-29-portfolio-documentation"></a>

### 2026-10-29 — Portfolio documentation and local operation context

**Documentation maintenance:** Prepared under the owner's explicit instruction to implement the portfolio audit, based on public `main` at `28c7450`.

- Shortened the English/Czech portfolio and project introductions, retained substantial AI-assistance disclosure and links to agent rules, and moved workflow detail behind learning/development references.
- Added the dated public CI result for `28c7450`: **223 passed in 7.51s** ([run 40770029069](https://github.com/jyenten/local_rag_api/actions/runs/40770029069)). This result belongs to that base revision, not automatically to the new documentation commit.
- Linked the historical 2026-10-20 BM25/Vector MRR comparison with explicit evidence and reproduction limits; made the English schema example and baseline table self-contained. Historical metrics were not rerun or changed.
- Corrected documentation paths in the target-structure illustration, clarified the implemented `/ready` check and used full milestone names instead of ambiguous journal phase numbers in the portfolio summaries.
- Recorded the owner's local/offline operation context and known dependency-audit state in operations guides. Dependency/security checks remain enabled.
- Verification for this change covers relative paths/anchors, preserved old anchors, CLI choices and unchanged benchmark values. No source-PDF ingest, corpus evaluation or Docker runtime test was performed.
- Retrieval code, architecture decisions, roadmap priorities, dependencies, protected datasets and prior skill assessments are unchanged. This maintenance entry assigns no new skill rating.

[↑ Back to top](#top)
