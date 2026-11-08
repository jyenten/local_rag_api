<a id="top"></a>

# Experiment: n8n, LangGraph and Codex

[Česky](../cs/DEV_LOOP.md#cz) · [Documentation](../README.md)

<a id="en"></a>

## Contents

- [Scope](#scope)
- [Run locally](#run-locally)
- [n8n](#n8n)
- [Live Codex](#live-codex)
- [20-run report](#20-run-report)
- [Public branch and security](#public-branch-and-security)
- [Docker demo isolation](#docker-demo-isolation)
- [Codex in Docker with ChatGPT](#codex-in-docker-with-chatgpt)
- [Controlled repair probe](#controlled-repair-probe)
- [Second task: build-search-request](#second-task-build-search-request)
- [Two files: build-search-package](#two-files-build-search-package)
- [One-shot Ollama probe](#one-shot-ollama-probe)
- [Verification and limitations](#verification-and-limitations)

- [Real BM25: direct before/after comparison](#real-bm25-direct-beforeafter-comparison)

- [Publish a verified real task through Git](#publish-a-verified-real-task-through-git)

## Scope

The lab lives in `experiments/dev_loop/` on `experiment/autonomous-dev`.
Run commands from the **repository root**, not from `rag_api_project/`.
RAG code, application dependencies, corpora, indexes and evaluation remain unchanged.

The fixed `normalize-question` task strips outer whitespace and rejects an empty
question. Each run copies the starting `question.py` into its own
`.runs/<request_id>/workspace/` and initializes a separate Git root without
a commit or remote. The worker edits that copy, not the RAG application.

| Tool | Responsibility |
| --- | --- |
| n8n | Manual intake, one HTTP request, display the result |
| LangGraph | Baseline, implementation, verification, retry/stop decisions |
| Codex CLI | Edit the allowed file; no commit, staging or push |
| pytest | Fixed controller-owned checks outside the worker workspace |

Baseline checks two existing cases and intentionally skips four new requirements.
After each edit all six checks must execute without skips. Success requires both
exit code 0 **and** complete JUnit evidence. LangGraph permits one implementation
and at most two repairs. Infrastructure errors, timeouts and scope violations stop the run.

Demo mode runs real LangGraph and real pytest, but a deterministic `DemoWorker`
edits the file: its first attempt fails and its second succeeds. No model is called.

## Run locally

Requires Python 3.11+ and Git. Create a separate environment in PowerShell:

```powershell
python -m venv experiments/dev_loop/.venv
$labPython = (Resolve-Path experiments/dev_loop/.venv/Scripts/python.exe).Path
& $labPython -m pip install -r experiments/dev_loop/requirements.txt
& $labPython -m experiments.dev_loop --backend demo
```

On Linux/WSL use `experiments/dev_loop/.venv/bin/python`.
The JSON result contains `backend`, `status`, `attempts`, node `trace`, test output
and `diff`. Demo should finish with `review_ready` after two attempts.
Every new CLI invocation generates a fresh UUID. Reusing `--request-id <UUID>`
returns the completed result without executing again. A different backend with
the same UUID conflicts.

`review_ready` only means this small task met its checks. The diff still needs
human review; it does not approve integration into RAG.

## n8n

Start the local HTTP service. Keep its token out of Git and workflow exports:

```powershell
$env:DEV_LOOP_TOKEN = & $labPython -c "import secrets; print(secrets.token_urlsafe(32))"
Set-Clipboard $env:DEV_LOOP_TOKEN
& $labPython -m experiments.dev_loop --backend demo --serve
```

In n8n:

1. Import `experiments/dev_loop/n8n-workflow.json`.
2. In **Run LangGraph loop**, create a **Header Auth** credential with header name
   `X-Dev-Loop-Token` and the value of `DEV_LOOP_TOKEN`. To copy it, execute
   `Set-Clipboard $env:DEV_LOOP_TOKEN` in the original PowerShell window before
   starting the service; newly opened windows do not inherit that variable.
3. Check the service URL. `http://127.0.0.1:8765/runs` works when n8n runs
   directly on the same host.
4. Select **Execute workflow** and inspect the HTTP node output.

The imported workflow is inactive, uses a manual trigger and has no retry loop.
Its UUID derives from this n8n instance's numeric `$execution.id` (up to 12 digits).
The operator chooses the backend at service startup, not in the HTTP request.
The API accepts only a UUID and a known `task_id`, never commands or free-form prompts.

With Docker Desktop, n8n's `127.0.0.1` points at its own container. Change the URL
to `http://host.docker.internal:8765/runs` and start the service with
`--host 0.0.0.0 --allow-non-loopback` on a trusted local network. Linux may require host-gateway
configuration. n8n Cloud needs an otherwise reachable service; this lab does not
configure public hosting.

The HTTP call waits for the complete result; the workflow timeout is 420 seconds.
One service instance executes one run at a time; concurrent requests receive 409.
Results are atomically saved as `.runs/<UUID>/result.json`. The same UUID does not
execute again, including after a service restart. Incomplete runs return 409;
inspect their workspace before submitting a new UUID. Two distinct UUIDs mean two tasks.

## Live Codex

For new local runs, use [Codex in Docker with ChatGPT](#codex-in-docker-with-chatgpt).
The original host adapter below also executes candidate pytest directly on the host;
it is separate from the Docker profile. Its configuration uses the CLI on the same host:

```powershell
codex --version
codex login status
& $labPython -m experiments.dev_loop --backend codex
```

For n8n, stop the demo service and start it with `--backend codex --serve`.
Use a new UUID / workflow execution after switching backend.
The adapter runs `codex --ask-for-approval never exec --sandbox workspace-write`
with `--cd <workspace> --json -`. Instructions and relevant test failures go through
stdin, not shell interpolation. The CLI's configured model and authentication are used.
The adapter requires a zero exit code and `turn.completed`; worker completion
alone is not evidence of correct code.

Each Codex invocation has a 90-second limit; pytest has 20 seconds. On timeout
the runner terminates the process tree, using `taskkill` on Windows.
Codex JSONL and stderr remain in the local run directory. The worker does not
receive the HTTP-service token; common secret variable names are removed from
the test-process environment.

## Verification and limitations

```powershell
& $labPython -m pytest experiments/dev_loop/tests -q -p no:cacheprovider
```

- Verified: real LangGraph/pytest demo, repair after failure, attempt limits,
  infrastructure failures, scope checks, complete test evidence,
  authenticated API and request replay after restart.
  Before the Docker adapter, the lab suite including batch reporting had 42 passed
  on Python 3.12.14 (2026-10-31).
- Codex CLI transport is tested with a substitute process result.
  Live Codex and n8n import/execution were not verified in this environment:
  standalone Codex CLI and n8n are unavailable here.
- No RAG code changed; its original test suite was not rerun for this step.
- No commits, pushes, PRs, automatic merges or applying the result to RAG.
- Scope checks are an audit, not an independent security sandbox. Candidate Python
  executes as a local process. Untrusted tasks require an isolated runner;
  this small fixture is not a general public development service.
- Attempt/time limits are not a fixed financial limit. Live mode can consume
  paid usage; detailed events remain in JSONL.
- `.runs/` is Git-ignored. Retain it when continuing the experiment; deleting it
  removes history and replay protection for those UUIDs.

Sources: [Codex non-interactive](https://learn.chatgpt.com/docs/non-interactive-mode),
[Codex CLI](https://learn.chatgpt.com/docs/cli/reference),
[LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api),
[n8n HTTP Request](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.httprequest/).

## 20-run report

A batch is 20 independent tasks, each starting from the original fixture and
limited to three attempts; it does not increase the repair limit.

```powershell
& $labPython -m pip install -r experiments/dev_loop/requirements-report.txt
& $labPython -m experiments.dev_loop --backend demo --cycles 20 --report-dir experiments/dev_loop/.runs/reports/demo-20
```

Use a new destination directory. Outputs are `batch.json`, `cycles.png` and a
self-contained `report.html` with an embedded chart, per-run table and security
limitations. Infrastructure, baseline or scope failures stop the whole batch.
The summary excludes raw logs and workspace paths; do not publish `runs/`.

Measured on 2026-10-31: 20/20 `review_ready`, 40 attempts, 20 repairs,
20.819 s total, median 0.976 s, maximum 1.476 s. Each run's verification codes
were `[1, 0]`. First-attempt success: 0/20. No model calls.
The demo scripts both the first error and its repair; this does not measure
Codex capability, RAG quality or n8n integration. Timing includes test overhead,
not model latency. `--backend codex` selects live execution; 20 tasks can invoke
the worker up to 60 times. Tokens and cost are not measured; attempt limits are
not a financial cap.

## Public branch and security

A public branch shares repository visibility; public read access does not grant
write access. Branches and worktrees do not constrain processes. New code remains
uncommitted and unpushed.

Implemented: a fixed task list, API token (at least 24 characters), loopback
default with an explicit flag for other addresses, one active run per process,
completed UUID reuse without reexecution, time/attempt/batch limits and file
auditing. Processes run without a shell and with an environment allowlist;
tests use a separate HOME. The Codex adapter requests `workspace-write` and
disables command network access; live enforcement was not verified here.

**The default `--isolation host` mode has no OS isolation for candidate Python.** Tests run with the local user's
permissions and can read the host or use the network. Checks outside the workspace,
file hashes and JUnit are not protection against deliberate result forgery.
The Codex sandbox does not cover pytest launched by our controller.

Before accepting general or untrusted tasks, use an ephemeral isolated runner for
both worker and tests, separate model authentication, read-only checks, restricted
network and CPU/memory/disk limits. A global spending cap, rate limiting, HTTP
body limit and bounded subprocess output capture are missing. The API lock is
not distributed and does not cover multiple server processes.

The local repository contains Gitleaks, pip-audit and dependency-review workflows;
CI tests and dependency auditing cover RAG, not this lab. This step neither
confirms live CI results, rulesets or branch-protection enforcement nor changes
GitHub settings. Some workflows use mutable action tags. Verify required checks
and human review before adding further automation.

Do not connect public issues, comments or untrusted PRs to privileged execution.
GitHub warns against untrusted code on self-hosted runners in public repositories
and against running PR code with secrets through `pull_request_target`.
Keep tokens, auth files and `.runs/` private; `.gitignore` is not a security
boundary and cannot hide files already tracked by Git.

Sources: [GitHub Secure use](https://docs.github.com/en/actions/reference/security/secure-use),
[pull_request_target](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target),
[Codex security](https://developers.openai.com/codex/security/).

## Docker demo isolation

The optional `--isolation docker` profile reports backend `demo-docker` and
uses the fixed demo task. Live `--backend codex --isolation docker` uses a separate
networked worker and auth volume; see [the guide below](#codex-in-docker-with-chatgpt).
The offline worker profile below applies to demo; the offline checker profile applies to both backends.

Host LangGraph receives only JSON containing `question.py` text. Candidate
source is never imported on the host. Each implementation and each pytest
invocation runs in a new container, without shared writable storage. Checks
are baked into the image under `/opt/dev-loop/checks`, not supplied by the
worker. No repository, personal folders or Docker socket are mounted. No
credentials or host environment variables are forwarded into containers.
The host Docker CLI and its operator remain trusted.

Profile: network `none`, read-only root filesystem, UID/GID `10001:10001`,
`cap-drop ALL`, `no-new-privileges`, 1 CPU, 256 MiB memory with no additional
swap, 64 processes, and tmpfs `/work` 32 MiB and `/tmp` 16 MiB using
`noexec,nosuid,nodev`. Stdin/stdout carry data only. Candidates are limited to
64 KiB; combined Docker attach stdout/stderr is capped at 256 KiB. Attach has
a 30 s timeout; create, image inspect and cleanup each have 10 s. The named
container is force-removed on success, failure and timeout; cleanup failure
stops the run. There is no automatic fallback to host worker or pytest.

The build context is the lab, with a `.dockerignore` allowlist. The base tag
`python:3.11-slim-bookworm` and transitive Python dependencies are not yet
digest/lockfile pinned. A runner resolves its image to a fixed `sha256` image
ID once, recorded as `runner_image` in results.

From repository root `D:\AI_roadmap_autonomous`, build the image:

```powershell
docker build -t local-rag-dev-loop:1 -f experiments/dev_loop/docker/Dockerfile experiments/dev_loop
```

Run actual Docker tests in this PowerShell session:

```powershell
$labPython = ".\experiments\dev_loop\.venv\Scripts\python.exe"
$env:DEV_LOOP_DOCKER_TESTS = "1"
& $labPython -m pytest experiments/dev_loop/tests/test_docker.py -q -p no:cacheprovider
Remove-Item Env:DEV_LOOP_DOCKER_TESTS
```

Three opt-in tests cover the repair graph, isolation from a synthetic host
file/token, read-only checks, disabled networking, cgroup/tmpfs limits, and an infinite candidate's
timeout. Without opt-in, actual Docker is not invoked and these three tests
are skipped. Controller tests do not prove kernel enforcement. Docker CLI is
unavailable in the author's environment, so neither the image nor the three
live tests were executed there.

Single run and batch:

```powershell
& $labPython -m experiments.dev_loop --backend demo --isolation docker
& $labPython -m experiments.dev_loop --backend demo --isolation docker --cycles 20 --report-dir experiments/dev_loop/.runs/reports/docker-demo-20
```

Expect `review_ready`, two attempts, `backend: demo-docker`, `isolation: docker`,
`checker_isolation: docker` and a populated `runner_image`. A successful run
creates five sequential containers: baseline, worker, checks, worker, checks.
Docker overhead is included in reported durations.

For n8n, stop the old API with Ctrl+C. From the PowerShell session retaining
the **same** `DEV_LOOP_TOKEN`, restart with isolation enabled:

```powershell
& $labPython -m experiments.dev_loop --backend demo --isolation docker --serve --host 0.0.0.0 --allow-non-loopback
```

The n8n URL and Header Auth do not change. `/health` reports `demo-docker` and
both isolation fields as `docker`; health neither starts a container nor
confirms image availability. Keep execution private. Containers share the
Docker host kernel and are not VMs. A candidate can affect its own pytest
process; complete JUnit is not proof against deliberate result forgery.
This profile does not address global spending caps, distributed API locking,
public input or GitHub ruleset enforcement.

Sources: [Docker run](https://docs.docker.com/engine/containers/run/),
[Resource constraints](https://docs.docker.com/engine/containers/resource_constraints/),
[None network](https://docs.docker.com/engine/network/drivers/none/).

## One-shot Ollama probe

For a small local `qwen3.5:4b-q4_K_M` trial, run from the worktree root:

```powershell
& .\experiments\dev_loop\.venv\Scripts\python.exe -m experiments.dev_loop.ollama_probe
```

The script checks the original fixture with Docker baseline tests first; a Docker
failure prevents any Ollama call. It then makes one request to
`http://127.0.0.1:11434/api/generate`, bypassing host HTTP proxies, with `think: false`,
4096 context and a 256-token output limit. Generation times out after 90 seconds.
The Docker image does not need rebuilding.

Each attempt has its own `.runs/ollama-probe/<UUID>/` containing `request.json`,
raw `response.json`, optional `candidate/question.py` and atomically saved
`report.json`. Responses are saved immediately. Empty code, incomplete generation,
invalid Python or a missing top-level `normalize_question` function produce
`invalid_model_output` without creating a candidate file. Host validation uses AST
parsing, never execution. Valid source is saved exactly as UTF-8, without manual
repairs, Markdown removal or dependence on PowerShell variables.

The same six acceptance checks then execute in Docker. `review_ready` means they
passed; `verification_failed` means checks failed. `generation_requests` counts
attempted generation HTTP requests, `model_duration_s` is Ollama's reported time,
and `total_duration_s` covers the whole probe including Docker. This is a standalone
probe without a repair loop, not an n8n/LangGraph backend. Existing empty candidates
are not overwritten. Neither Codex nor ChatGPT sign-in is involved. No RAG changes,
staging or commits are performed.

[↑ Back to top](#top)


## Codex in Docker with ChatGPT

This backend connects the existing LangGraph repair loop to real `codex exec`.
It uses the fixed `normalize-question` task, at most three attempts and backend
`codex-docker`. Codex returns JSON with exactly one `code` field. The host accepts
only UTF-8 text into `question.py` (at most 64 KiB, a syntactically valid definition
of the required function). Candidate Python is never imported or executed on the
host. The same six independent checks run in a separate offline container. Invalid
protocol, CLI, authentication or cleanup failures stop without a host fallback.

The image pins Codex CLI `0.162.1`. Its default selects the model; user config,
rules and session history are not transferred. CLI uses `--ignore-user-config
--ignore-rules --ephemeral --sandbox read-only`, with shell tools, apps, plugins,
memories, additional agents and web search disabled. The controller also rejects
recorded tool activity. This is a narrowly scoped code generator with a repair
loop, rather than a general agent with terminal access.

First build the separate image in PowerShell. The existing checker image
`local-rag-dev-loop:1` must also be available; this addition needs no checker rebuild.
Node/npm are used inside the image build, so Windows needs neither installed.

```powershell
cd D:\AI_roadmap_autonomous
$labPython = '.\experiments\dev_loop\.venv\Scripts\python.exe'
& $labPython -m pytest experiments/dev_loop/tests -q -p no:cacheprovider
docker build -t local-rag-codex:0.162.1 -f experiments/dev_loop/docker/Codex.Dockerfile experiments/dev_loop
```

Windows sign-in is not automatically available inside the Linux container. Sign
in once inside this container; do not copy personal Windows auth files. Enable
device code login in ChatGPT security settings first, then run:

```powershell
docker volume create local-rag-codex-auth
docker run --rm -it --cap-drop ALL --security-opt no-new-privileges=true --mount type=volume,source=local-rag-codex-auth,target=/home/node/.codex local-rag-codex:0.162.1 -c cli_auth_credentials_store=file -c forced_login_method=chatgpt login --device-auth
```

Open the printed URL in your browser and confirm the one-time code. Do not share
the code or auth files. Verify the login method, then run one real task:

```powershell
docker run --rm --cap-drop ALL --security-opt no-new-privileges=true --mount type=volume,source=local-rag-codex-auth,target=/home/node/.codex local-rag-codex:0.162.1 -c cli_auth_credentials_store=file -c forced_login_method=chatgpt login status
& $labPython -m experiments.dev_loop --backend codex --isolation docker
```

Expect `backend: codex-docker`, both isolation fields `docker`, `authentication:
chatgpt`, distinct hashes `worker_image` and `runner_image`, and on success
`status: review_ready` with six acceptance checks. Attempts depend on the model,
unlike the scripted demo. `worker_attempts` stores only completion, code hash and
CLI-reported token counts. Missing telemetry is `null`, not zero. Cached input is
a subset of input tokens, not an extra amount to add. `model_cost` remains `null`;
these metrics do not establish remaining account allowance or price. Later batches
support 1–20 cycles, but verify one task first. One CLI invocation may involve more
than one model request.

For n8n, stop the previous Uvicorn with Ctrl+C. Your saved `DEV_LOOP_TOKEN` must be
set in the same PowerShell window; retain its existing value. Start one instance:

```powershell
& $labPython -m experiments.dev_loop --backend codex --isolation docker --serve --host 0.0.0.0 --allow-non-loopback
```

The URL `http://host.docker.internal:8765/runs` and Header Auth stay the same. Set
the HTTP Request node Timeout to `900000` ms (the updated import uses this value).
Changing the file does not update an already imported workflow. Use a new execution
and UUID. `/health` shows backend and isolation, but does not test images or login.

Worker limits: 90 s, 768 MiB RAM with no extra swap, 1 CPU, 128 PIDs, read-only root,
no capabilities, no-new-privileges, tmpfs `/work` 16 MiB and `/tmp` 64 MiB. It runs
as non-root UID 1000. No repository, personal directory or Docker socket is mounted.
The only mount is its own writable auth volume for ChatGPT token refresh. This
volume contains secrets, belongs only to this local worker, has no fixed size
limit and must never be published. The checker receives neither the volume nor
credentials and retains `--network none` and UID 10001. The worker uses `bridge`:
**outbound traffic is not restricted to OpenAI domains**. This does not secure
untrusted public tasks or a public CI runner. Docker operators and images are trusted.

The worker freezes its image ID after the first inspect for its lifetime. The base
image and transitive npm dependencies are not digest-locked. Docker attach has a
256 KiB combined-output cap; create/inspect/cleanup each have 10 s limits. Timeout
also triggers `docker rm --force`; cleanup failure prevents writing a candidate.
Raw authenticated CLI logs are not forwarded to n8n or the aggregate report.

Verification here covers substituted transport, protocol validation, separated
access, limits, cleanup, graph wiring and reports. Docker Engine and a real signed-in
call in this new image must be verified on your computer, not simulated as live
evidence by unit tests. The successful Windows CLI probe confirms login and a
response, not this new Docker profile. No RAG changes, commit, staging or push occur.

Sources: [Authentication and device login](https://learn.chatgpt.com/docs/auth),
[CLI structured output](https://learn.chatgpt.com/docs/non-interactive-mode),
[Shell tool configuration](https://learn.chatgpt.com/docs/config-file/config-reference).

### Connection error during device login

`error sending request ... /deviceauth/usercode` does not establish a cause.
The image explicitly installs `ca-certificates`, sets `SSL_CERT_FILE` and checks
for a nonempty system CA bundle at build time. The initial variant did not ensure
this. Rebuild the image with the same build command after the Dockerfile fix and
retry device login; keep the existing auth volume. If it still fails, test HTTPS
without credentials:

```powershell
docker run --rm --entrypoint curl local-rag-codex:0.162.1 --connect-timeout 10 --max-time 20 -sS -o /dev/null -w "HTTP=%{http_code}" https://auth.openai.com/api/accounts/deviceauth/usercode
```

GET can return 400, 403 or 405, for example. An HTTP response establishes HTTPS
connectivity, not that device login is permitted. Curl error 6 indicates DNS,
7 connection failure, 28 timeout and 60 certificate verification. Diagnose using
the actual output rather than the generic CLI message. A corporate proxy may
require a custom CA bundle (`CODEX_CA_CERTIFICATE` per OpenAI documentation);
do not disable TLS verification. Docker Engine and live connectivity for this
new image cannot be verified in this environment.


## Controlled repair probe

A batch with 20 successful first attempts does not exercise the repair branch.
This standalone scenario injects a known defect. The existing offline Docker
demo worker returns the first implementation: it checks emptiness before
`strip()`, so whitespace is not rejected. The real checker evaluates it with the
original checks. LangGraph then passes the unchanged failed-test output and
broken source to the real Docker Codex worker. Verification runs separately
again, without network access or credentials.

This is neither a spontaneous model mistake nor repair success across varied
tasks. Results must say `measurement: controlled-repair`; the initial candidate
origin is `scripted-demo-docker`. The existing limit remains three implementation
attempts in total: one injected defect and at most two Codex worker invocations.
Actual model request count remains unmeasured. Infrastructure errors stop the loop.

Use the existing `local-rag-codex-auth` sign-in, `local-rag-codex:0.162.1` worker
image and `local-rag-dev-loop:1` checker image. No n8n token change, new sign-in
or image rebuild is needed. Run in PowerShell:

```powershell
cd D:\AI_roadmap_autonomous
& .\experiments\dev_loop\.venv\Scripts\python.exe -m pytest experiments/dev_loop/tests -q -p no:cacheprovider
& .\experiments\dev_loop\.venv\Scripts\python.exe -m experiments.dev_loop.repair_probe
```

If the first Codex repair succeeds, expect:

- baseline: 2 passed, 4 skipped;
- injected candidate: 3 failed, 3 passed;
- Codex repair: 6 passed;
- `status: review_ready`, `attempts: 2`, `injected_attempts: 1`;
- `codex_worker_invocations: 1`, `codex_completed_invocations: 1`;
- `repair_path_observed: true`, `probe_passed: true`.

These are expectations, not claims of an already completed live run. If the
first repair fails, one more is allowed; success is not scripted. A final
`review_ready` without a recorded failure followed by a repair does not pass
this experiment: CLI exit success also requires `probe_passed: true`.

Every probe uses a fresh UUID under `.runs/repair-probe/`. Its `result.json`
records the injected defect's origin, token counts only for the actual Codex
worker, separate attempt counts and repair input hashes. `injected-question.py`
beside the result, outside the audited workspace, preserves the broken candidate.
Its `code_sha256` hashes exact file bytes; `prompt_source_sha256` hashes the UTF-8
text sent to Codex (with normalized line endings). `repair_inputs` must match
the initial repair source and exact failed-test feedback. No candidate is
imported on the host.

This is a separate CLI scenario. The normal backend, previous 20-run batch,
n8n workflow, original fixture and checks remain unchanged. Live Docker/Codex
execution must be verified on your computer. Automated tests use trusted
scripted transport/model substitutes and real pytest; they are not evidence of
a live Codex invocation or Docker isolation. No RAG changes, staging, commit or
push occur.


## Second task: build-search-request

The fixed task requests `build_search_request(query: str, top_k: int = 5) -> dict`.
This lab generates code that builds a request; it performs no actual retrieval or
RAG changes. Acceptance contract:

- Require a string `query`; otherwise raise `TypeError`.
- Replace each run of whitespace, including Unicode, with one ASCII space, remove
  outer whitespace, and preserve letter case and punctuation.
- Reject an empty normalized query with `ValueError`.
- Require exactly type `int` for `top_k`, rejecting `True`, `False` and `5.0` with
  `TypeError`. Reject values outside the inclusive 1–20 range with `ValueError`.
- Return a fresh dict with exactly `query` and `top_k`. Do not coerce inputs or
  clamp invalid values to allowed bounds. Keyword arguments must work.

For example, `build_search_request("  OSPF\t routes  ", 3)` returns
`{"query": "OSPF routes", "top_k": 3}`. This is not the bridge HTTP request body:
HTTP still selects only a task and UUID; the model implements the whole function.

`--task build-search-request` requires `--backend codex --isolation docker`.
The default remains `normalize-question`; host mode and demo reject the second
task. `tasks.py` allows only these two fixed specs, fixtures, function names and
checks. HTTP cannot supply test paths, prompts or commands. Both tasks retain
`question.py` as their sole writable candidate module; the second task defines
`build_search_request` inside it.

New checker image `local-rag-dev-loop:2` contains both suites and identifies the
checked task in its response. The second task requires the matching task ID and
complete JUnit evidence for **28 tests**; the original six cannot substitute for
them. Baseline preserves two existing properties and skips 26 new cases.
Acceptance skips nothing. The original task still defaults to verified image
`local-rag-dev-loop:1`. The Codex image and stored login stay the same; build only
the new checker:

```powershell
cd D:\AI_roadmap_autonomous
$labPython = '.\experiments\dev_loop\.venv\Scripts\python.exe'
& $labPython -m pytest experiments/dev_loop/tests -q -p no:cacheprovider
docker build -t local-rag-dev-loop:2 -f experiments/dev_loop/docker/Dockerfile experiments/dev_loop
```

Before calling a model, test both contracts inside the new Docker image without
model usage. These tests require neither Codex nor account authentication:

```powershell
$env:DEV_LOOP_SEARCH_DOCKER_TESTS = '1'
& $labPython -m pytest experiments/dev_loop/tests/test_search_task.py -q -p no:cacheprovider
Remove-Item Env:DEV_LOOP_SEARCH_DOCKER_TESTS
```

The two opt-in checks cover the new baseline, rejection of the broken fixture,
success of a trusted reference, and new-image compatibility with the original
task. They are skipped without this variable. Controller tests also check task
mismatches, incomplete evidence, stopping before the model on baseline errors,
and rejection of common incorrect implementations. Without real Docker, these
tests do not prove isolation enforcement.

Then run one real task:

```powershell
& $labPython -m experiments.dev_loop --task build-search-request --backend codex --isolation docker
```

Expect `task_id: build-search-request`, `backend: codex-docker`, baseline
`2 passed, 26 skipped` and, on success, `28 passed`, `status: review_ready`.
Attempts and repairs depend on the model; no defect is deliberately injected
here. The three-attempt limit applies. `runner_image` identifies the new checker;
`worker_image` identifies the existing Codex image. Docker CLI is unavailable in
this environment, so image build and real execution must be verified on your PC.

For n8n, stop the old Uvicorn with Ctrl+C and use its PowerShell window with the
existing `DEV_LOOP_TOKEN` to start a service configured for the second task:

```powershell
& $labPython -m experiments.dev_loop --task build-search-request --backend codex --isolation docker --serve --host 0.0.0.0 --allow-non-loopback
```

Import the separate `experiments/dev_loop/n8n-search-workflow.json` as an inactive
manual workflow and select your verified Header Auth. Its Windows/Docker URL is
already `http://host.docker.internal:8765/runs`, with a 900000 ms timeout. Start a
new full execution for a fresh UUID. The original workflow remains for task one.
Each server handles one configured task: a mismatched task ID returns 422 before
worker invocation. `/health` now also includes `task_id` for either task. Extra
HTTP fields remain forbidden. A green HTTP node alone is insufficient; check
`status: review_ready`.

Batches accept the same `--task` and include task ID in JSON and HTML reports.
Do not combine the two different tasks into one success-rate figure. Tokens are
still CLI telemetry; actual model request count and price remain unmeasured.
Only the networked Codex worker gets its auth volume. The checker has no network,
host mounts or credentials. Fixtures and checks remain separate; the host only
saves candidate Python as text.

## Two files: build-search-package

This third fixed task tests cooperation between two modules. Its only allowed
artifacts are `validation.py` and `search_request.py`, initialized from fixtures
in a separate workspace. It does not give an agent access to the repository.

| Module | Contract |
| --- | --- |
| `validation.py` | `normalize_query(query: str) -> str`: the same type checks and normalization as the second task. `validate_top_k(top_k: int) -> int`: exact `int`, range 1–20, returning the unchanged valid value. No imports. |
| `search_request.py` | Only `import validation` without an alias and `build_search_request(query: str, top_k: int = 5) -> dict`. Call `validation.normalize_query` first, then `validation.validate_top_k`; use both results in a fresh `query`/`top_k` dictionary. Propagate exceptions unchanged. |

The model returns `{"files":{"validation.py":"…","search_request.py":"…"}}`.
The controller requires the exact complete pair, nonempty UTF-8 sources, valid AST
and a combined 64 KiB limit. It rejects extra paths, missing modules, other imports
and unexpected module-level statements. AST validation is not a security sandbox;
candidate Python runs only inside the offline checker. The entire response is
validated before writing either file, after worker cleanup. Writing the pair is
not atomic: an I/O error can leave a partial artifact, but the graph stops with
`infrastructure_error` before verification. Inspect that workspace; a fresh ID
starts from fresh fixtures.

The checker uses `check-files`, protocol 2, verified task ID, a complete manifest
and JUnit evidence for all **52 tests**. Baseline is `2 passed, 50 skipped`;
acceptance allows no skips. Tests also exercise validators directly, delegation,
call order, returned values and exception identity. Protocol 1 and the default
images of the previous tasks remain supported.

In PowerShell, build new tags to preserve the existing images:

```powershell
cd D:\AI_roadmap_autonomous
$labPython = '.\experiments\dev_loop\.venv\Scripts\python.exe'
& $labPython -m pytest experiments/dev_loop/tests -q -p no:cacheprovider
docker build -t local-rag-dev-loop:3 -f experiments/dev_loop/docker/Dockerfile experiments/dev_loop
docker build -t local-rag-codex:0.162.1-multifile -f experiments/dev_loop/docker/Codex.Dockerfile experiments/dev_loop
```

First run four actual integration cases without a model call: the new suite,
checker compatibility with both previous tasks and readability of the new Codex
schema without network access or an auth volume. Tests without Docker do not
replace these checks.

```powershell
$env:DEV_LOOP_PACKAGE_DOCKER_TESTS = '1'
& $labPython -m pytest experiments/dev_loop/tests/test_multifile.py -q -p no:cacheprovider
Remove-Item Env:DEV_LOOP_PACKAGE_DOCKER_TESTS
& $labPython -m experiments.dev_loop --task build-search-package --backend codex --isolation docker
```

The final command is a real Codex call. It reuses `local-rag-codex-auth`; no new
login is needed. Expect task ID `build-search-package`, `review_ready`, `52 passed`,
both names in `allowed_files`, a diff for both modules and a `files_sha256` map
in `worker_attempts`. The number of attempts is not guaranteed; the limit is
three. `committed` and `applied_to_rag` remain `false`. One run is not a general
benchmark of project editing ability.

After success, stop the old server with Ctrl+C. In the window containing the
original `DEV_LOOP_TOKEN`, start:

```powershell
& $labPython -m experiments.dev_loop --task build-search-package --backend codex --isolation docker --serve --host 0.0.0.0 --allow-non-loopback
```

Import `experiments/dev_loop/n8n-package-workflow.json` and select the existing
Header Auth. This inactive manual workflow has one HTTP node without automatic
retries, a 900000 ms timeout and URL `http://host.docker.internal:8765/runs`.
Start a fresh full execution. Task ID must match the server; HTTP clients cannot
supply file contents or custom instructions. Reusing a request ID returns its
saved result and does not create another measurement.

For a separate batch, add e.g.
`--cycles 20 --report-dir experiments/dev_loop/.runs/reports/package-20-local`
to the CLI command without `--serve`. Keep success rates of different tasks
separate. Tokens are CLI telemetry; exact model request counts and cost remain
`null`. The worker has bridge networking and only its auth volume, without a
domain egress allowlist; the checker has no network, credentials or host mounts.
This experiment is for local fixed tasks, not a public endpoint or untrusted
branches.

## Real BM25: direct before/after comparison

`python -m experiments.dev_loop.real_bm25` reads the real
`rag_api_project/app/retrievers/bm25.py` from the repository. Its original constructor
tokenizes every document during validation and again when building the corpus.
Codex is asked to tokenize each document once and reuse those exact tokens. The
retrieval algorithm and configuration are preserved. This is not an intentionally
broken fixture.

Source is checked against public revision `a94150b0723df94cac5ea47a12fa364edb2e4798`
of `jyenten/local_rag_api`. The manifest records SHA-256 hashes of the source,
support modules and original tests. The command verifies the actual repository
files before running and again before exporting. Different contents stop the run
rather than overwriting local work. CRLF checkout is compared as canonical LF.

Inside the isolated worker, the transfer filename is `question.py`; its contents
are the complete real BM25 module. AST validation permits changes only to the
body of `BM25Retriever.__init__`; imports, constants, constructor signature and
`search` must remain semantically identical. Candidate code is not executed on
the host. The existing Codex image and auth volume are reused. This operation is
CLI-only and is not exposed through the n8n HTTP API.

### Exact comparison

- The same **68 original regression cases before and after**, copied unchanged.
- Actual tokenizer calls during initialization on 1000 documents: the original
  count is 2000; the required count is 1000.
- Complete results of six fixed queries: documents, order, scores and metadata must match.
- Seven paired initialization timings on the same 1000 × 128 token corpus. Both
  versions are warmed up and execution order alternates. Counting instrumentation
  is disabled during timing.

The checker uses real `rank_bm25` and NumPy. Chroma storage is replaced by a
synthetic collection, as in the original unit tests. It does not access user PDFs,
Chroma storage, `.env` or DEV/RANDOM/TEST datasets. This measures BM25 construction
on synthetic data, not full RAG quality or real-corpus latency. A timing improvement
is not guaranteed or required for acceptance; passing original tests, identical
outputs and fewer tokenizer calls are required. JSON retains raw times and data hash.

### One real run

From PowerShell in the experimental worktree root:

```powershell
cd D:\AI_roadmap_autonomous
$labPython = '.\experiments\dev_loop\.venv\Scripts\python.exe'
docker build -t local-rag-bm25-compare:1 -f experiments/dev_loop/real_bm25/Dockerfile experiments/dev_loop/real_bm25
& $labPython -m experiments.dev_loop.real_bm25
```

No `DEV_LOOP_TOKEN` or new login is needed. Avoid other heavy workloads during
measurement. Each run creates a fresh directory under
`experiments/dev_loop/.runs/real-bm25/<UUID>/` with `result.json`, `before.py`,
`workspace/question.py`, standalone `report.html` and, on `review_ready`,
`candidate.patch` naming the real project path. Open the latest report:

```powershell
$run = Get-ChildItem .\experiments\dev_loop\.runs\real-bm25 -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1
Start-Process (Join-Path $run.FullName 'report.html')
```

The report separates initialization milliseconds, elapsed Codex worker time
including its Docker overhead (`codex_worker_elapsed_s`) and the whole run
(`duration_s`). Model cost and exact model request count remain unmeasured. There
are at most three attempts; repairs use actual checker feedback. `candidate.patch`
is a proposal for review; project source remains untouched, without commits,
pushes or automatic application.

Controller verification without model calls uses the existing
`pytest experiments/dev_loop/tests` command. An optional live checker test (no
model call) can be enabled with `DEV_LOOP_REAL_BM25_DOCKER_TESTS=1` and run through
dev-loop's `tests/test_real_bm25.py`. Controller tests alone do not establish live
Docker/Codex success.

## Publish a verified real task through Git

The host-side publisher supports only `bm25-tokenize-once` in
`jyenten/local_rag_api` (repository ID `1236923375`). It creates a branch and draft
PR against `main` through GitHub's Git Data API. It does not stage or commit the
local worktree, run Git hooks, apply a patch, update an existing branch, or merge.
Fixtures such as `build-search-package` have no application destination and cannot
be published through this command.

GitHub CLI (`gh`) must be installed and authenticated on the **host**:

```powershell
gh --version
gh auth login --hostname github.com
gh auth status --hostname github.com
```

Use the browser login offered by `gh`. ChatGPT/Codex authentication and
`DEV_LOOP_TOKEN` do not authenticate GitHub. The logged-in account needs repository
Contents and Pull requests write access; no workflow/secrets administration is
needed. Host `gh` may use its credential store or an explicitly configured
`GH_TOKEN`/`GITHUB_TOKEN`; do not put tokens in commands, reports or n8n JSON.
The publisher alone gets this authentication. Neither the model worker nor the
offline checker receives it.

### Publish an existing run without another model call

From the updated experimental worktree root, point to the exact successful run.
Use an explicit UUID rather than selecting whichever directory happens to be newest:

```powershell
cd D:\AI_roadmap_autonomous
$labPython = '.\experiments\dev_loop\.venv\Scripts\python.exe'
$runDir = '.\experiments\dev_loop\.runs\real-bm25\a5739357-6da4-4118-be18-5c038306e0e9'
& $labPython -m experiments.dev_loop.publish --run-dir $runDir
& $labPython -m experiments.dev_loop.publish --run-dir $runDir --publish
```

The first invocation is an **offline preview**, without GitHub access or Docker
execution. `--publish` is the explicit publication action. It:

1. Validates the fixed task, UUID, successful result, source/candidate SHA-256 and
   constructor-only AST scope. Paths in saved JSON are not used to locate artifacts.
2. Checks the fixed GitHub repository ID, resolves `main` to a full commit, and
   verifies the original module, tokenizer/config and 68-test source against the
   reviewed hashes at both that base and the recorded source commit. Upstream
   source/test changes stop publication and need a new reviewed task baseline.
3. Reruns baseline and acceptance in the **original immutable checker image SHA**.
   Docker must be running and that image must still exist locally. The same 68
   tests must pass before/after, with identical six-query results and tokenizer
   calls reduced from 2000 to 1000. Candidate Python is not run on the host.
4. Reuses an identical open one-file BM25 PR, including an older manually created
   PR. A competing one-file BM25 PR with a different result stops publication.
5. Otherwise creates one commit changing only `rag_api_project/app/retrievers/bm25.py`
   on `agent/bm25-tokenize-once-<UUID>` and opens a **draft** PR. The new commit's
   remote diff and contents are checked before creating the branch; `main` moving
   during this step stops publication. Existing branch refs are never overwritten.

The original `result.json` is preserved as generation evidence. A separate
`publication.json` records the PR URL, actual head/base commits, immutable checker
image, fresh comparison evidence and whether an existing PR was reused. It does
not claim CI success: `ci_status` is `not_checked`, and merge is disabled.
Reports and local paths are not uploaded; the PR contains the public source diff,
fixed summary and selected run/hash provenance, without raw model/test logs.

For the already accepted BM25 result, this should return the existing PR #10 if
its base, one-file diff and candidate contents still match. No new Codex call is
made. A different valid candidate is not automatically treated as equivalent.

### Interrupted publication and new runs

Rerun the same `--run-dir ... --publish` after an interrupted request. The publisher
checks GitHub again rather than trusting a cached local receipt. If a branch was
created but PR creation failed, the exact branch can be reused after checking its
one-commit diff. A mismatched branch is left intact. A PR response lost in transit
is recovered by finding the matching open PR on retry. A closed/merged PR or a
changed upstream baseline requires inspection; do not force-reset refs.

`publication.lock` prevents concurrent publication of the same local run. If the
controller crashes and leaves it behind, first confirm that no publisher remains
active before manually removing that one lock file. GitHub writes are not a single
transaction: a failure can leave an unattached Git object or a branch without a PR.
No automatic cleanup deletes branches or PRs.

A new real run can opt into the same handoff after success:

```powershell
& $labPython -m experiments.dev_loop.real_bm25 --publish
```

This still requires the reviewed original source in the input repository; the
already optimized worktree is intentionally rejected. On publication failure the
successful run is retained; retry the separate publisher, without another paid or
account-limited model invocation.

### Review before merge and subsequent n8n integration

Before merging, review the diff, project and controller CI, and dependency/security
findings. A draft PR and passing checker do not approve a merge or waive findings.
The `Development loop controller` workflow runs unit/contract tests without model
calls or publication credentials; live Docker tests remain explicitly opt-in.

The host-side publisher can be called from the CLI after a real LangGraph run.
The original development API on port 8765 still accepts its existing fixed fixture
tasks. A separate loopback API on 8766 lets n8n select an explicitly registered
successful BM25 run, recheck it and obtain its PR URL. Real BM25 generation remains
CLI-only. See [n8n publication setup](DEV_LOOP_N8N_PUBLICATION.md) for the host service,
connection probe and manual workflow. HTTP payloads cannot carry arbitrary shell
commands, repository paths, source files or GitHub credentials.

To receive controller changes, fetch their reviewed branch through Git and update
the intended clean worktree. A separate review worktree can be created from the
remote branch without modifying existing work. No patch download/application is
required. Merging the controller's implementation PR into the experimental branch
and merging an application change into `main` remain separate decisions.
