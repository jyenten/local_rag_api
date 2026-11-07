# Publish verified runs from n8n

[Česky](../cs/DEV_LOOP_N8N_PUBLICATION.md) · [Development loop](DEV_LOOP.md)

This integration publishes an **existing successful real-BM25 run**. n8n chooses
its registered UUID, the host publisher repeats offline Docker checks, and the
HTTP node displays the resulting draft/existing PR URL. It does not invoke Codex,
generate a new candidate, apply local files or merge. LangGraph remains responsible
for generation and repair in the original CLI run.

## Host service

Use the clean worktree containing this integration. The examples use
`D:\AI_roadmap_n8n_publication` and reuse the existing experimental Python environment.
GitHub CLI must already be authenticated on the host, Docker must be running, and
the run's immutable checker image must remain available. No new model login is needed.

Restore the **same saved token used by the n8n Header Auth credential** in this
PowerShell window. Do not generate a replacement unless you also update that credential:

```powershell
$secureToken = Read-Host 'Saved DEV_LOOP_TOKEN' -AsSecureString
$env:DEV_LOOP_TOKEN = [System.Net.NetworkCredential]::new('', $secureToken).Password
Remove-Variable secureToken
```

Start the service in a window that stays open:

```powershell
cd D:\AI_roadmap_n8n_publication
$labPython = 'D:\AI_roadmap_autonomous\experiments\dev_loop\.venv\Scripts\python.exe'
$runRoot = 'D:\AI_roadmap_autonomous\experiments\dev_loop\.runs\real-bm25'
& $labPython -m experiments.dev_loop.publication_api --runs-root $runRoot --allow-run a5739357-6da4-4118-be18-5c038306e0e9
```

The CLI validates each registered saved run before listening. Repeat `--allow-run`
for up to 20 exact UUIDs if needed. The parent directory is host configuration,
never an HTTP field. The server binds **only `127.0.0.1:8766`**, one worker, with
proxy-header processing disabled. There is no non-loopback override. Port 8765
and the old fixture API remain separate and are unnecessary for this workflow.
No container, firewall, n8n volume or RAG index is recreated or changed.

## Verify the connection before importing

In a second PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:8766/health
Get-NetTCPConnection -State Listen -LocalPort 8766 |
    Select-Object LocalAddress,LocalPort,OwningProcess
docker exec rag-lab-n8n node -e "fetch('http://host.docker.internal:8766/health').then(async r=>{console.log(r.status,await r.text());if(!r.ok)process.exitCode=1}).catch(e=>{console.error(e.message);process.exitCode=1})"
```

Expect `127.0.0.1` as the listening address and HTTP 200 from **inside the existing
n8n container**. `/health` is liveness only: it does not claim Docker/GitHub readiness
and exposes no registered UUIDs or account details. The probe contains no token.
Docker documents [`host.docker.internal`](https://docs.docker.com/desktop/features/networking/networking-how-tos/)
for container-to-host traffic; reachability of this loopback-only server still
needs verification on the actual Docker Desktop backend.

If the native request succeeds but the container probe fails, stop at that
connection issue. Do not switch to `0.0.0.0`, add broad firewall exceptions or
recreate n8n to bypass it. Inspect Docker Desktop/VPN/proxy routing and choose a
separately reviewed local transport if this backend cannot reach host loopback.
The editing environment did not verify the owner's Docker Desktop routing.

## Manual n8n workflow

Import `experiments/dev_loop/n8n-publication-workflow.json` from this Git worktree
using n8n's **Import from File**. The workflow is inactive and has:

1. **Publish verified run** — manual trigger, with no schedule/webhook.
2. **Choose registered run** — Edit Fields node with `task_id: bm25-tokenize-once`
   and the exact successful `run_id`. Change only to another host-registered UUID.
   Do not use `$execution.id`: this selects stored evidence, not a fresh generation.
3. **Recheck and get draft PR** — one HTTP POST to
   `http://host.docker.internal:8766/publications`, no automatic retries and a
   900000 ms timeout. Choose the existing Header Auth credential containing
   `X-Dev-Loop-Token`. No GitHub credential belongs in n8n or the workflow JSON.

Execute the workflow manually. For the recorded accepted result, expect PR #10
with `reused_existing_pr: true` if it still matches. The output includes
`pull_request`, `draft`, branch/head/base, candidate hash, and explicit
`merge_allowed: false`, `merged: false`, `local_source_changed: false` and
`ci_status: not_checked`. Raw model/test logs, full comparison records, credentials
and filesystem paths are excluded from this HTTP response. Fresh evidence remains
in the host run's `publication.json`.

Repeating a request repeats the independent checker, then reuses a matching open
PR; it does not consume model tokens. Only matching results are reused. A different
candidate or changed remote baseline stops publication. No live new-PR creation is
required merely to demonstrate the n8n connection.

## HTTP boundary and errors

| Method/path | Purpose |
| --- | --- |
| `GET /health` | Minimal unauthenticated liveness |
| `GET /tasks` | Token-protected fixed task and registered run IDs |
| `POST /publications/preview` | Token-protected offline plan, no Docker/GitHub writes |
| `POST /publications` | Token-protected recheck and create/reuse draft PR |

POST JSON contains **exactly** `task_id` and `run_id`. Extra fields, arbitrary
commands/prompts, repository/file paths, unsupported tasks and malformed UUIDs are
rejected. Unregistered UUIDs return 404. Authentication is checked before parsing
the body. Browser Origin requests and unexpected Host headers are rejected;
Content-Type must be JSON, and a fixed declared Content-Length of at most 1024 bytes
is required. CORS, public docs, webhooks and arbitrary operations are not exposed.
The loopback restriction does not protect against compromised local processes or
trusted containers: keep this service and token within the local lab.

| Status | Meaning / next action |
| --- | --- |
| 401 | Token is missing or differs from the service window |
| 409 | Another HTTP publication is active; do not resubmit |
| 422 | Invalid input, failed run validation or rejected publication; inspect host CLI/remote state |
| 503 | Docker/GitHub infrastructure unavailable; inspect the host CLI |
| 500 | Other publication failure; inspect both host and GitHub before retrying |

Response bodies do not include raw exception text, host paths or gh stderr. After
a timeout/error, inspect the existing PR and `publication.json` before repeating the
same UUID; a remote branch/PR may already exist. There are no automatic retries.
Before merge, independently review diff, CI and security findings. The service
cannot merge, waive an audit finding or approve its own result.

## Verification scope

Controller tests cover token/scope/run registration, concurrency, error redaction,
receipt filtering, loopback-only startup and workflow structure without model calls
or GitHub writes. They do not prove a live n8n import or Docker Desktop connection.
Real BM25 generation remains CLI-only; adding another real task or an HTTP
run-and-publish operation requires a separate registered task with reviewed source,
allowed files and independent checker. It is not enabled by this publication API.
