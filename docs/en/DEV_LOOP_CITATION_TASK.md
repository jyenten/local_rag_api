# Registered citation-provenance repair

[Česky](../cs/DEV_LOOP_CITATION_TASK.md) · [n8n controls](DEV_LOOP_N8N_CONTROL.md) · [Policy](DEV_LOOP_POLICY.md)

## Scope and evidence

`retrieval-citation-provenance` addresses two concrete defects: fallback context
attaches the first document's metadata to other text, and a relative threshold
can discard every negative-scoring candidate. It does not fix general answer
truthfulness or Chroma CVEs.

`experiments/dev_loop/citations/manifest.json` pins the public source revision
`ce9a088373d7dc2ad005af07c4ab09cb2df7b9fd` and content hash. Local/remote source
must match exactly; identical bytes can also come from older worktree `f58f6f2`.
No PDFs, indexes or TEST gold evidence are needed.

| Result | Producer | Constraint |
|---|---|---|
| `rag_api_project/app/retrieval.py` | Model | Only the bodies of `Retriever.rerank_lines` and `Retriever.build_context`; AST protects imports, signatures, constructor, search and helpers |
| `rag_api_project/tests/test_retrieval_citations.py` | Host controller | Fixed reviewed checker regression file, SHA-256 verified; not editable by the model |

Baseline runs 3 existing contracts. Acceptance runs all 15 cases: negative/zero/
positive scores, second-document and multiple-source attribution, deduplication,
limits, no evidence, metadata and return-shape preservation. A fresh process also
observes two boolean probes before/after. The checker loads the complete actual
module with model/Chroma constructors stubbed; no index or weights are loaded.
These are synthetic regressions, not private-corpus accuracy measurements.

The fixed test accompanies the proposed application patch. Publication permits
exactly two files and one new commit: the modified module and added exact tests.
Retries never overwrite refs. Changed source, an existing test destination or
a competing PR stop publication. Baseline/acceptance rerun in the original pinned
offline Docker image. The model never receives GitHub credentials.

## One-time activation

Review the registration/PR, stop the controller with Ctrl+C, and update the same
feature branch in the clean stable worktree. Keep the n8n container unchanged:

```powershell
cd D:\AI_roadmap_n8n_publication
git status -sb
git fetch origin
if ($LASTEXITCODE -ne 0) { throw "Git fetch failed." }
git switch --detach origin/feat/dev-loop-n8n-control
if ($LASTEXITCODE -ne 0) { throw "Branch switch failed." }
```

Stop on errors; never use force/reset. Preserve the local profile and credentials.
Build only the new checker; reuse the existing Codex image/auth volume:

```powershell
docker build -t local-rag-citation-check:1 .\experiments\dev_loop\citations
if ($LASTEXITCODE -ne 0) { throw "Checker build failed." }
```

Do not start generation after a failed build. Task selection is a one-time explicit
host operation. The command below preserves paths, port, allowed historical runs
and job allowance, stores no token, and only changes a valid profile after checking
the new source:

```powershell
$labPython = 'D:\AI_roadmap_autonomous\experiments\dev_loop\.venv\Scripts\python.exe'
& $labPython -m experiments.dev_loop.service select-task retrieval-citation-provenance
if ($LASTEXITCODE -ne 0) { throw "Task selection failed." }
& $labPython -m experiments.dev_loop.service check
if ($LASTEXITCODE -ne 0) { throw "Profile check failed." }
& $labPython -m experiments.dev_loop.service start
```

Resolve each error before proceeding. Profile v1 remains supported; selection
moves to v2. There is still one host-selected new-job type with the existing
allowance (default one new job per process), not an allowance for each catalog
row. Interrupted identities never silently regenerate. Selection takes effect
at the next service start, not by altering an already running process.

## One live run through n8n

1. Update/import `n8n-control-workflow.json` and select the same credentials. The
   fixed `retrieval-citation-provenance` option is added; no secrets are exported.
2. `catalog`: the new task must show `generation_configured: true`. Allowed historic
   BM25 reports remain available; new BM25 jobs are not enabled by this profile.
3. Select the new task and `generate`; leave UUID empty. Review both allowed paths,
   two editable methods, fixed-test hash, 15 acceptance cases and at most 3 attempts.
4. Only **Schválit** starts baseline, possible generation and offline verification.
   Expected success: `review_ready` / `awaiting_approval`; no PR is created yet.
5. Select `report` with the same task and UUID. Both probes are false before the
   repair and true after acceptance. This is not a new BM25 speed benchmark.
6. After reviewing the diff, select `publish` with the same UUID and separately
   approve its plan. It calls no model, rechecks and creates/reuses a draft PR to
   `main`. Application CI also runs the permanent new regression file. Merge is
   a separate owner decision.

After timeout inspect `status` with the same UUID; do not evade it with another
ID, restart or higher allowance. The old combined `/jobs` endpoint is disabled
for this selected task (410); use the separate reviewed control workflow. Cancel
invokes neither model nor publisher. Approval waits at most 10 minutes, the HTTP
action at most 900 seconds, and the workflow has a 45-minute overall limit.

## Registration validation

Unit/contract tests use an explicitly labeled trusted local reference and fake
GitHub/model, not live Codex. The GitHub Actions `citation-checker` job builds the
image and runs live Docker tests: original baseline passes, original acceptance
fails, reference acceptance passes. Optional equivalent local check:

```powershell
$env:DEV_LOOP_CITATION_DOCKER_TESTS = '1'
& $labPython -m pytest experiments/dev_loop/tests/test_citations.py -k test_docker_citation_checker -q -p no:cacheprovider
Remove-Item Env:DEV_LOOP_CITATION_DOCKER_TESTS
```

This validation invokes no model and publishes no PR. The independent Chroma audit
is not waived. Live model execution and owner-side Docker/n8n import are reported
separately from registration validation.
