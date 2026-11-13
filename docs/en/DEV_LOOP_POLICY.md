# Development-loop agreements

[Česky](../cs/DEV_LOOP_POLICY.md) · [Repository rules](AGENTS.md) · [Operations](DEV_LOOP.md)

Recorded on 2026-11-08 from the approved agreements in this work. This is a versioned
operating contract for Local RAG API / dev-loop, not complete conversation memory.
Current explicit owner instructions and higher-priority instructions take precedence.
An agent must not rewrite these rules to expand its own authority.

## Authorization scope

Within an owner-delegated bounded implementation task, the owner authorized creating
a branch, commit, push and draft PR without approval for each operation. This covers
`experiments/dev_loop/`, its specifically necessary CI/runbooks, and approved real-task
implementation within its manifest. It does not assign arbitrary new work or approve
architecture, technology, roadmap or budget changes.

- Preserve unrelated WIP, worktrees, indexes, caches and authentication.
- Stage exact paths; no automatic `git add .`, force push or resetting another branch.
- A maintenance feature branch may receive a checked fast-forward. The application
  publisher creates new refs and never overwrites existing ones.
- Deliver through Git branches and PRs. A patch is an optional recovery export, not
  the normal installation/update procedure.
- Lab PRs target the experimental branch or a reviewed preceding feature branch.
  Application changes have separate PRs to `main`; do not merge the entire lab there.
- Every merge requires fresh explicit owner approval for the specific PR after review.
  Commit/push authorization or a generic “continue” does not authorize merge.

## Review and evidence

Before merging, inspect current head/diff, file scope, relevant tests, CI and security
findings. Challenge conclusions unsupported by evidence. Check implementation and
independent results; do not repeat successful runs without a reason.

- Distinguish unit/contract tests, live Docker, actual model use, n8n connectivity
  and live PR creation. Reusing an existing PR does not prove branch/PR creation.
- `review_ready` or a green HTTP node is not approval. `pr_ready` records the handoff
  at that time, not current CI or the state after a later human merge.
- State unperformed checks and remaining risks. A few checked ports are not a
  whole-machine audit or a library CVE fix.
- Preserve dependency auditing without suppression. Report failed checks and inherited
  findings; accepting residual risk requires explicit human approval.
- A human may add approval labels, including `human-approved-eval-change`, after review.
  An agent must not apply them to bypass protection of rule changes.
- Changes to this policy and AGENTS entry points belong in a protected, human-reviewed PR.

## Execution boundaries

- n8n selects a registered task/ID. HTTP must not accept shell commands, arbitrary
  prompts, repository/file paths, source files or GitHub credentials.
- Reviewed host controller code fixes source, allowed files, tests and limits. Another
  task type needs reviewed registration, not a manifest bypass.
- The model returns structured source. Candidate Python is checked in a separate offline
  Docker checker without host mounts, network or credentials. Isolation failure must
  not fall back to executing candidate code on the host.
- LangGraph retains at most three implementation attempts. New jobs require explicit
  host allowance, defaulting to one per service process. This session allowance is not
  a durable/global token or financial cap.
- Same-ID retries/restarts must not silently regenerate code. An interrupted incomplete
  result needs inspection; publication failure can repeat only publication.
- Keep model-call count and cost unknown unless actually measured. Distinguish demo,
  controlled fault injection and real model runs.

## Data, credentials and networking

- GitHub authentication stays on the host. Codex receives only its separate auth volume;
  neither checker nor n8n receives a GitHub token. n8n uses only bridge Header Auth.
- Keep tokens in credentials/protected environment, never Git configuration profiles,
  workflow JSON, reports, commits or public logs.
- Do not modify private PDFs, Chroma indexes, DEV/RANDOM/TEST, gold evidence or metrics
  to improve a score. Destructive ingestion requires separate consent and a backup.
- Bind the service to loopback. Connectivity failure must not automatically enable
  `0.0.0.0`, a public tunnel or a broad firewall exception.
- A stable installation uses one working directory and ignored local settings.
  Routine jobs do not switch worktrees, rebuild n8n or install dependencies. The
  controller creates/removes worker/checker containers automatically.

## What Git rules enforce

Root/module `AGENTS.md` files direct agents to this contract. CODEOWNERS and Eval
Governance protect rule changes from unreviewed merge in the established review
process. A text file itself is not a sandbox or branch protection.

Runtime limits remain enforced by task/file allowlists, source hashes, AST validation,
Docker isolation, authentication, locks and stable IDs in code. The Docker worker does
not receive the entire repository or automatically remember this conversation; it
receives fixed task instructions and schema. When agreements change, review the
corresponding code/tests and both language versions.
