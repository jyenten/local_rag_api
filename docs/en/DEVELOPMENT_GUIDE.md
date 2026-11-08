<a id="top"></a>

# AI RAG Project Development Guide

[Česky](../cs/DEVELOPMENT_GUIDE.md#cz) · [English](#en) · [Dokumentace / Documentation](../README.md)

<a id="obsah"></a>

<details>
<summary>Contents — click to expand</summary>

- [Documentation responsibilities](#en-documentation-responsibilities)
- [Development workflow](#en-development-workflow)
- [Code and module design](#en-code-and-module-design)
- [Errors, side effects and diagnostics](#en-errors-side-effects-and-diagnostics)
- [Verification and regression tests](#en-verification-and-regression-tests)
- [Retrieval and evaluation discipline](#en-retrieval-and-evaluation-discipline)
- [Git, review and integration](#en-git-review-and-integration)
- [Security and dependency management](#en-security-and-dependency-management)
- [Collaboration and learning](#en-collaboration-and-learning)
- [Completion and documentation updates](#en-completion-and-documentation-updates)

</details>

---

<a id="en"></a>

This guide defines **how to develop and review changes**. Phase priorities and
current project status belong to [ROADMAP.md](ROADMAP.md); completed work and
learning evidence belong to [LEARNING_LOG.md](LEARNING_LOG.md).


<a id="en-documentation-responsibilities"></a>

## Documentation responsibilities

| Document | Source of truth for |
| --- | --- |
| [ROADMAP.md](ROADMAP.md) | Approved phases, their goals and acceptance criteria, current development focus |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Implemented components, interfaces and explicitly marked target architecture |
| This guide | Development workflow, code quality, verification and Git practice |
| [OPERATIONS.md](OPERATIONS.md) | Setup, configuration, ingestion, API, Docker and runnable commands (CZ/EN) |
| [EVALUATION.md](EVALUATION.md) | Evidence construction, matching, metrics, evaluation and reproducibility (CZ/EN) |
| [LEARNING_LOG.md](LEARNING_LOG.md) | Dated milestones, branch provenance and demonstrated learning evidence |
| [Repository AGENTS.md](AGENTS.md), [project AGENTS.md](PROJECT_AGENTS.md) | Agent permissions, collaboration modes and approval boundaries |

Do not maintain another milestone table, benchmark table or active-phase list
here. Link to the owning document when a procedure needs that context.


<a id="en-development-workflow"></a>

## Development workflow

Follow **Complete → Measure → Improve**:

1. Inspect the implementation, applicable AGENTS rules, current branch and
   uncommitted changes. Identify the approved roadmap goal and affected files.
2. Define expected behavior, scope and acceptance criteria. Keep useful but
   unrelated ideas in the backlog; do not expand the current phase for them.
3. Complete a working vertical slice before optimizing individual components.
   Prefer one coherent change over a large speculative refactor.
4. Verify behavior with appropriate tests and, for retrieval changes, controlled
   DEV/RANDOM measurements. A manually selected successful query is insufficient.
5. Review the result, record evidence and limitations, then improve the measured
   weakness. Update the document that owns any changed behavior or status.

A new idea belongs in the current change only when it helps satisfy the current
Definition of Done. Do not reopen completed work merely because another design
is imaginable. Reopen it for a concrete evaluation/integration failure, a
security issue or a material requirement change.

The roadmap owns phase-specific goals and Definition of Done checklists. This
guide defines the shared implementation and verification practices below.


<a id="en-code-and-module-design"></a>

## Code and module design

- Keep one cohesive responsibility per module and a small public interface per
  subsystem. Separate document loading, text processing, retrieval, reranking,
  generation, evaluation and HTTP transport.
- Prefer high cohesion and low coupling. Call public functions instead of
  reaching into another subsystem's internal models, caches or ranking arrays.
- Use explicit typed data models where tuple/dictionary positions obscure
  meaning. Prefer immutable records for document identity, source/page data,
  evidence and completed results; allow mutation only when it is intentional.
- Keep generic infrastructure independent of domain-specific routing terms.
  Domain rules belong at an explicit domain boundary, not in generic ranking.
- Centralize model names, paths and limits in configuration. Preserve published
  interfaces and user changes unless an approved task requires changing them.
- Use idiomatic, typed Python: clear names, small purposeful functions and
  comprehensions/generators where they remain readable. Avoid code golf,
  deeply nested expressions and abstractions without a current need.
- A helper does not automatically require its own file. Split it when reuse,
  independent responsibility, size or testing justifies the boundary.
- Use direct attributes for simple records. Add properties/getters/setters only
  when controlled access provides actual behavior; they are not security controls.
- Do not introduce inheritance, async code, design patterns or metaprogramming
  merely for architectural symmetry. For a large refactor, first establish the
  problem, target boundaries and interfaces in ARCHITECTURE.md.


<a id="en-errors-side-effects-and-diagnostics"></a>

## Errors, side effects and diagnostics

Validate external input at the appropriate boundary and fail with a useful
reason. Do not silently swallow exceptions, discard failed inputs or report a
partially processed document as a successful ingestion.

Keep pure transformations separate from filesystem/database access, model
loading and history writes. Make significant side effects explicit in function
names, interfaces and operating instructions. Resource limits should cover the
relevant file, PDF-page, query, result-count and request boundaries; verify the
implemented limits rather than assuming a planned control already exists.

Keep security validation separate from text preprocessing: rejecting an unsafe
file must not silently change valid document semantics. Prefer logging in
reusable modules; CLI scripts may print user-facing output. Diagnostics should
identify failures without exposing secrets or private corpus content.


<a id="en-verification-and-regression-tests"></a>

## Verification and regression tests

Use the verification layer that answers the actual question:

| Layer | Purpose |
| --- | --- |
| Unit tests | Deterministic module behavior, validation and edge cases |
| Integration tests | Behavior across component boundaries |
| Smoke tests | Basic application operation in the intended environment |
| Retrieval evaluation | Evidence-based quality and retrieval latency |

Prefer small synthetic fixtures, fake collections and explicit failure cases
for unit tests. Real PDFs/models belong in suitable integration, manual or
evaluation checks; passing synthetic tests does not prove real-corpus quality.

Add a meaningful regression for a verified defect. Confirm that it exposes the
original failure where practical. Never weaken assertions or validation merely
to obtain a passing result. Test data integrity and interface alignment as well
as the normal success path.

For code changes, run focused tests and the full project suite before commit.
From `rag_api_project/`:

```bash
python -m pytest tests -q
```

For documentation-only changes, verify facts, links, examples and affected
configuration rather than inventing tests that mirror the text. Report exactly
what ran, skips/warnings and material checks that could not be performed. Do not
claim GitHub CI success or real-corpus results from a local report alone.


<a id="en-retrieval-and-evaluation-discipline"></a>

## Retrieval and evaluation discipline

Use [EVALUATION.md](EVALUATION.md) for the schema, matching rules, CLI commands,
approval/promotion procedure and reproducibility requirements. Use
[EVAL_CURATOR_AGENT.md](EVAL_CURATOR_AGENT.md) for candidate-curation constraints.

- Keep DEV development, RANDOM robustness exploration and held-out TEST separate.
  Do not repeatedly inspect TEST errors and then optimize for them.
- Establish a baseline before changing ranking. Compare DEV/RANDOM runs with
  controlled corpus, index, dataset and configuration; preserve provenance.
- Construct evidence from source PDFs before writing questions. Discovery scores
  do not establish factual validity, even when page and chunk retrieval use
  different implementations of BM25.
- Do not change existing golden evidence, metrics or baseline history to raise a
  score. Candidate validation does not authorize promotion.
- Distinguish measured `search()` latency from initialization and full answer/
  HTTP response cost; state which retrieval or reranking work the timed method
  includes. Do not combine incompatible raw relevance scores without a justified
  scoring method and measured evaluation.


<a id="en-git-review-and-integration"></a>

## Git, review and integration

The default integration branch is `main`. Prepare new work on a suitable working
branch; preserve unrelated worktrees and uncommitted changes. Do not reset,
stash, switch across or stage someone else's WIP as an incidental cleanup.

Before staging, inspect `git status --short` and `git diff`. Stage exact intended
paths, then review the staged file list and content:

```bash
git diff --cached --stat
git diff --cached
git diff --cached --check
```

Do not use automatic `git add .`. Keep private PDFs, local indices, model caches,
`.env` and other secrets out of commits. Prefer coherent commits with messages
that describe completed behavior; separate unrelated documentation, dependency
and feature changes when practical.

From `rag_api_project/`, the project helper runs staged whitespace checks and
the project test suite:

```bash
python -m scripts.git_check
```

It does not grant approval or establish that secrets, scope, dependencies and
retrieval quality were reviewed. Before pushing, know the working-tree state,
review the intended changes and satisfy applicable AGENTS and repository rules.
Commit, push and merge only within explicit authorization; do not bypass
required reviews or CI policies.


<a id="en-security-and-dependency-management"></a>

## Security and dependency management

Security applies throughout development, not only during the planned security
phase. Validate external inputs, enforce appropriate filesystem/resource
boundaries, handle secrets deliberately and make failures explicit.

Dependency auditing, Dependency Review, Gitleaks and Dependabot are already
configured. Treat their findings as evidence to investigate; passing Python
tests does not resolve a dependency vulnerability. Do not disable or weaken
checks to make a change appear healthy.

`requirements.txt` pins direct dependencies and four explicit security pins for
transitive/build packages. Linux CI uses `requirements-linux-py311.lock.txt`
(Ubuntu 24.04, Python 3.11) in a fresh virtual environment. The lock is not a
Windows installation file. `python -B scripts/check_dependency_lock.py`, run
from `rag_api_project/`, checks that all direct/security pins match the lock.

When changing versions, update both manifests and verify a clean installation,
`pip check`, the full regression suite and both dependency audits. The audits
run independently: one resolves `requirements.txt`; the other checks the exact
Linux lock, including its transitive packages. Findings still fail CI.

The **Generate Linux Python Lock** workflow can be dispatched on the dependency
branch to regenerate the snapshot in a clean environment. Its verification job
downloads that generated artifact into a second clean environment and runs the
tests there. Review and commit the artifact through Git; the workflow does not
write to branches. Pinning ChromaDB 1.5.9 does not fix its known vulnerabilities
or grant a risk exception; see [CHROMA_SECURITY.md](CHROMA_SECURITY.md).

Before recommending or running `python -m scripts.ingest`, explain that it
**deletes and recreates** the configured Chroma collection. Follow the backup,
configuration and authorization boundaries in [OPERATIONS.md](OPERATIONS.md).


<a id="en-collaboration-and-learning"></a>

## Collaboration and learning

The repository and project AGENTS files govern permissions. Select the mode
appropriate to the owner's request rather than imposing a teaching procedure
on every implementation task:

- **LEARN:** explain the problem and behavior, support the owner's implementation,
  review it and obtain practical understanding evidence.
- **IMPLEMENT:** deliver the delegated bounded change, preserve interfaces/WIP,
  verify it and report the outcome and limitations.
- **REVIEW:** inspect and report reproducible findings; modify files only when
  the owner has authorized fixes.

In LEARN mode, use complete logical units with the goal, rationale, relevant new
concepts, scope and a clear verification step. Give large/risky components their
own focused review; avoid import-by-import conversational steps. Use idiomatic
Python without artificial simplification or unnecessary advanced machinery.

Record meaningful milestones, difficulties, assistance and test evidence in
[LEARNING_LOG.md](LEARNING_LOG.md). Separate a completed feature from an
independently demonstrated skill. Do not assign mastery or change learning
assessments without the required human evidence/approval.


<a id="en-completion-and-documentation-updates"></a>

## Completion and documentation updates

A reusable module is normally complete when its responsibility and interface are
clear, expected behavior works, important inputs are validated, relevant tests
and project regression checks pass, and known intentional limits are documented.
Use the roadmap's specific acceptance criteria for completion of a subphase.
Do not declare it complete while a critical unresolved bug remains.

When behavior or an approved decision changes:

- Update the owning document from the responsibilities table.
- Keep current implementation distinct from target architecture and local WIP.
- Synchronize Czech and English operating/evaluation instructions.
- Put dates, measurements and branch provenance in the learning/evaluation
  records; link to them instead of copying volatile status into every document.
- Report changed files, verification, decisions and remaining limitations.

A phase's goals or priorities change only through an approved roadmap decision.
Do not silently redesign the plan as part of a documentation cleanup.

[↑ Back to top](#top)
