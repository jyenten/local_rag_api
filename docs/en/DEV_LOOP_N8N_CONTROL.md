# Operating tasks through n8n

[Česky](../cs/DEV_LOOP_N8N_CONTROL.md) · [Policy](DEV_LOOP_POLICY.md) · [Older publication](DEV_LOOP_N8N_PUBLICATION.md)

## Scope

Import `experiments/dev_loop/n8n-control-workflow.json` to put an operator form in
front of the existing controller on port 8766. n8n selects an action, shows its
plan and collects a decision. LangGraph controls implementation and at most two
repairs; independent checks run in offline Docker. Publication is a separately
approved action. The owner continues to approve merges.

This delivery supports the registered `bm25-tokenize-once` task. It is completed
in current `main`: historical reports remain inspectable, but source/remote
preflight rejects new generation against changed baselines without model calls
or allowance consumption. Citation repair needs its own reviewed manifest and
checker in a subsequent PR. No arbitrary prompts, shell or remote registration.

## Update the service once

Reuse the stable worktree and ignored local profile. Do not replace/rebuild n8n.
Stop the old service with Ctrl+C in its PowerShell window first. Example matching
the owner's existing installation:

```powershell
cd D:\AI_roadmap_n8n_publication
git status -sb
git fetch origin
git switch --detach origin/feat/dev-loop-n8n-control
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
