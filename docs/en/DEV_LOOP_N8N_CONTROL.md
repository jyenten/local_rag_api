# Operating tasks through n8n

[Česky](../cs/DEV_LOOP_N8N_CONTROL.md) · [Policy](DEV_LOOP_POLICY.md) · [Older publication](DEV_LOOP_N8N_PUBLICATION.md)

## Scope

Import `experiments/dev_loop/n8n-control-workflow.json` to put an operator form in
front of the existing controller on port 8766. n8n selects an action, shows its
plan and collects a decision. LangGraph controls implementation and at most two
repairs; independent checks run in offline Docker. After one plan approval,
`autonomous` continues automatically through the report and draft PR. `generate`
and `publish` still support separate approvals. The owner approves merges.

The catalog contains historical `bm25-tokenize-once` and registered
[`retrieval-citation-provenance`](DEV_LOOP_CITATION_TASK.md). BM25 is completed
in `main`; source/remote preflight blocks generation against changed baselines.
The host profile explicitly selects the enabled new-job type; the n8n dropdown
cannot enable it. No arbitrary prompts, shell or remote registration. Activating
a reviewed task is a one-time setup; routine operations then use the form.

## Update the service once

Reuse the stable worktree and ignored local profile. Do not replace/rebuild n8n.
Stop the old service with Ctrl+C in its PowerShell window first. Example matching
the owner's existing installation:

```powershell
cd D:\AI_roadmap_n8n_publication
git status -sb
git fetch origin
git switch --detach origin/feat/dev-loop-autonomous-prototype
.\experiments\dev_loop\Start-DevLoop.ps1 -Action check
.\experiments\dev_loop\Start-DevLoop.ps1 -Action start
```

Preserve local changes before switching; do not use force/reset. The feature
branch is for pre-merge verification. After approved integration the same clean
worktree can follow `origin/experiment/autonomous-dev`; the entire lab does not
belong in application `main`. Preserve the profile, saved runs, caches and auth.
No patch download is involved.

The launcher uses saved Python/settings. When DEV_LOOP_TOKEN is absent, it
prompts without echoing: enter the same saved token as n8n Header Auth. No token
is saved in the profile/workflow. Restarting does not authorize resetting the
session allowance to force more model calls.

## Import and authentication

1. Import the JSON from the updated worktree into n8n.
2. On **Ovládání úloh**, select an **HTTP Basic Auth** credential for a separate
   local form login, not GitHub/Codex credentials. The export contains no password.
3. On **Zkontrolovat plán** and **Provést schválenou akci**, select existing
   **Header Auth**: `X-Dev-Loop-Token` with the saved service token.
4. First use **Execute Workflow** and the form's **Test URL**. After activation
   the production URL uses `/form/local-rag-control`.
5. Keep n8n on `127.0.0.1:5678` and the controller on `127.0.0.1:8766`. HTTP nodes
   inside Docker connect to `host.docker.internal:8766`.

Form/Form Trigger 2.4, IF 2.2 and HTTP Request 4.2 parameters were checked against
n8n 2.45.7 sources. Actual import/rendering on the owner's installation remains a
separate integration step; unit/contract tests do not establish that result.

## Actions

| Action | UUID | Result |
|---|---|---|
| `catalog` | Empty | Registered tasks/runs and configuration; no model/publication |
| `status` | Existing job or registered run | State without starting/repeating the model |
| `report` | Successful job or registered run | Validated comparison and readable diff; no host paths/raw logs |
| `autonomous` | Empty creates an ID; existing jobs can finish without another model call | One plan approval → baseline → Codex → checks / at most two repairs → report → Docker recheck → draft PR |
| `generate` | Empty creates an ID; explicit ID accepted | Plan and approval, then generation/checks only, no publication |
| `publish` | Successful job or registered run | Plan, candidate hash, diff and separate approval; recheck/draft PR without a model |

Default action: `catalog`. Default decision: **Zrušit** (Cancel). **Schválit**
(Approve) authorizes only the displayed action, UUID and plan hash. Changed
artifacts, source or remaining allowance require a fresh preview. The token
authenticates the caller; the form choice is not separate identity verification
or a human cryptographic signature.

First run `catalog`, then copy an allowed UUID into a new `report` action. The
owner's historical run is `a5739357-6da4-4118-be18-5c038306e0e9`; it works only
when registered by the profile and its files remain available. No generation.

Generation is a synchronous HTTP step with a 900-second timeout. Open the form in
a second tab to select `status` with the same UUID while it runs. `generating` is
aggregate state, not a token stream. The ID/progress are also in n8n Executions.
After timeout inspect the original UUID before doing anything else; do not start
a replacement model run. There are no automatic retries or remote worker kills.

## Autonomous prototype: one complete cycle

Activate the [registered citation repair](DEV_LOOP_CITATION_TASK.md) once: build
its fixed checker and select `retrieval-citation-provenance` in the existing
profile. Reuse the Codex image/auth volume, host GitHub login and n8n container.
Import the updated `n8n-control-workflow.json` and select the same Basic Auth and
Header Auth credentials as before.

1. The catalog must show `generation_configured: true` and one remaining job.
2. Select `autonomous`, `retrieval-citation-provenance`, and leave UUID empty.
3. Review two allowed paths, two editable methods, the fixed regression file,
   15 acceptance cases, at most 3 attempts, and automatic **draft** PR to `main`.
   **Schválit** now authorizes this entire specific cycle.
4. The running cycle needs no further human step. LangGraph repairs according to
   test feedback; the publisher independently rechecks the accepted candidate in
   the original offline Docker image and creates the draft PR. The result contains
   its link, before/after evidence and diff.
5. Success means `result.status: pr_ready` and both `report.comparison.after`
   flags true. `ci_status: not_checked` does not establish passing GitHub CI.

Baseline, infrastructure or three-attempt failure stops without publication.
Publication failure stops as `publication_blocked`; after inspection approve a
fresh plan using the **same UUID**. It binds the saved candidate hash and shows
`generation_required: false`, `max_worker_attempts: 0`: retry publication only.
An existing successful `generate` job can finish the same way. Use `publish` for
historical registered runs, rather than treating them as new autonomous jobs.
Interrupted jobs without `result.json` never regenerate, and completed jobs return
saved state. The new-job allowance remains per process; restarting is neither a
permanent financial cap nor authorization for more jobs.

The prototype controls one registered development task. It does not select new
tasks, merge, ingest or deploy. GitHub CI and security findings still require
review before merge.

## Verification boundaries

Contract tests cover one approval, automatic handoff, failures, retries, stale
hashes and compatibility with separate actions. Node.js evaluates workflow
expressions, including safe diff rendering and the PR link.

CI `citation-checker` additionally exercises HTTP → LangGraph → real offline
Docker → repair → Docker recheck → publisher. Its worker is an explicitly
scripted reference and GitHub is fake: no live model calls or public PR creation.
Live Codex, import/execution in the owner's n8n, and actual PR publication are
separate integration checks requiring evidence from a concrete run.

## Troubleshooting

| State | Meaning |
|---|---|
| `approval_required` | Plan ready, no mutation performed |
| `review_ready` | Proposal verified; separate publication approval required |
| `pr_ready` | Handoff at that time, not current CI or merge approval |
| `publication_blocked` | Generation preserved; after inspection retry publication only |
| `SOURCE_CHANGED` / `SOURCE_OR_REMOTE_PREFLIGHT_BLOCKED` | Source/remote differs; expected for completed BM25 |
| `NEW_JOBS_NOT_CONFIGURED` | Host enabled saved-run operations only |
| `NEW_JOB_ALLOWANCE_CONSUMED` | Session limit exhausted; form cannot increase it |
| `JOB_ACTIVE_OR_INTERRUPTED` | Active/incomplete job; do not evade with another ID |
| HTTP 401 | Check Header Auth credential; never print the token |
| HTTP 409 | Active mutation, stale plan or conflict; inspect status/preview again |
| HTTP 503 | Artifact/infrastructure checks stopped; details stay in host logs |

## Learning the nodes

| Node | Responsibility |
|---|---|
| Ovládání úloh | Form Trigger: fixed actions and UUID input |
| Zkontrolovat plán | HTTP Request: JSON and Header Auth |
| Vyžaduje schválení? | IF: actual boolean rather than a green HTTP node |
| Prohlédnout a schválit | Form: wait for a human decision |
| Schváleno? | IF: only explicit Approve reaches the action |
| Provést schválenou akci | Identity/hash from the reviewed plan, not new form input |
| Výsledek a report / Zrušeno bez provedení | Form Ending: result or cancellation without mutation |

Exercise: run `catalog` and `report`, explain why no worker ran, and identify the
node preventing publication on **Zrušit**. This is not a prior mastery claim.

For compatibility older `/jobs` and `n8n-real-bm25-workflow.json` still combine
generation and publication. Do not use them for the new control flow. The form
calls only `/control/preview` and `/control/execute`; allowlists, Docker isolation,
three attempts, source hashes and the merge ban remain controller-enforced.
