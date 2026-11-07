# ChromaDB findings and local deployment boundaries

[Česky](../cs/CHROMA_SECURITY.md) · [Operations](OPERATIONS.md) · [Documentation](../README.md)

Assessment date: **2026-11-07** (following the November 4 review). Reviewed project baseline:
`a94150b0723df94cac5ea47a12fa364edb2e4798`; PR #10 only changes BM25 construction.
This assessment does not grant a security-audit exception.

## Confirmed findings

The [PR #10 audit](https://github.com/jyenten/local_rag_api/actions/runs/41788293914)
reports five entries for freshly resolved ChromaDB **1.5.9**, representing four
distinct CVEs: `PYSEC-2026-311` occurs twice. The rows match the
[2026-11-02 main audit](https://github.com/jyenten/local_rag_api/actions/runs/41445441166).
This does not identify the version actually installed on the owner's machine.

At review time, [PyPI](https://pypi.org/project/chromadb/) lists 1.5.9 as the latest
stable release. The GitHub Reviewed advisories below list no patched version.
Pinning 1.5.9, downgrading, or using a development build is not a verified fix.

| CVE / advisory | Described attack path | Published affected range |
| --- | --- | --- |
| [CVE-2026-45829](https://github.com/advisories/GHSA-f4j7-r4q5-qw2c) | Loading a malicious model through collection creation with `trust_remote_code=true`, before authentication. | 1.0.0 through 1.5.9 |
| [CVE-2026-45833](https://github.com/advisories/GHSA-36p7-vc44-83pf) | Similar code execution through collection updates requiring `UPDATE_COLLECTION`. | 0.4.17 through 1.5.9 |
| [CVE-2026-45830](https://github.com/advisories/GHSA-2wm9-hf6c-p5cr) | Insufficient authorization across tenants/collections. | 0.4.17 through 1.5.9 |
| [CVE-2026-45831](https://github.com/advisories/GHSA-xph7-9rjv-w5fr) | SimpleRBAC authorizes actions without adequately scoping tenant/database/collection access. | 0.5.0 through 1.5.9 |

## Project usage and limits of the conclusion

Reviewed calls in `app/retrieval.py`, `app/retrievers/vector.py`,
`app/retrievers/bm25.py`, `scripts/ingest.py` and `scripts/create_test_db.py`
use `chromadb.PersistentClient(path=...)`. The application API in `app/main.py`
accepts a question at `/ask`; it does not expose Chroma collection creation/update
endpoints or accept embedding-function configuration from HTTP callers.
Compose defines only the RAG API, without a Chroma server service. Project code
does not enable `trust_remote_code=true` or configure a SimpleRBAC/multitenant server.

This limits direct reachability of the described server scenarios in this profile.
**It does not establish that the library is unaffected or that arbitrary deployments
are safe.** Upstream [issue #6717](https://github.com/chroma-core/chroma/issues/6717)
also describes a client-side scenario. Client code at tag 1.5.9 reconstructs
embedding functions from collection configuration; database contents and model
configuration must therefore remain trusted. Do not load third-party Chroma
indexes, allow other accounts to modify the index directory, or connect to an
untrusted Chroma server without a new assessment.

This review covers code and published advisories, not RCE reproduction,
penetration testing or inspection of all Windows services. Installed versions,
environment settings, firewall rules, other containers and tunnels require
runtime verification.

## Restricting the published port

Compose now uses `127.0.0.1:8001:8000` instead of `8001:8000`. This restricts the
published RAG API port to host loopback under standard Docker bridge/NAT settings.
Uvicorn inside the container continues listening on `0.0.0.0:8000`. The change
does not patch the four CVEs or add application authentication. Other local
processes and containers remain part of the trusted environment.

[Docker documentation](https://docs.docker.com/engine/network/port-publishing/)
notes that hosts on the same L2 segment could reach localhost-published ports
before Engine 28.0.0. Verify the actual server version, not only the CLI version.
Custom direct-routing/NAT settings need separate network verification.

Inspect running services without changing them, from PowerShell:

```powershell
docker version --format "{{.Server.Version}}"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"
```

A service created from this Compose should show `127.0.0.1:8001->8000/tcp`.
Another API container showing `0.0.0.0` or `[::]` has not been restricted merely
by editing this YAML. n8n on port 5678 and dev-loop on 8765 are separate services.
The direct BM25 command does not require the dev-loop HTTP service.

Before recreating the API, identify its actual Compose project and original
`chroma_db`/model-cache mounts. **Do not blindly start Compose from another
worktree**: relative paths could select a different index. Applying the port
change requires recreating the correct container; saving YAML does not modify
an existing process. Ingestion and collection deletion are outside this change.

## Owner-reported local state at review time

The owner supplied local command output; this was not a remote inspection of the machine:

- Docker Engine reports server version **29.9.2**.
- The old API publishing port 8000 on all interfaces is stopped
  (`Status=exited`) with `Restart=no`. It has no mounts (`[]`); its data was not deleted.
- The running-container listing contained only n8n, publishing
  `127.0.0.1:5678->5678/tcp`.
- The Windows TCP-listener check returned no rows for ports 8000, 8001 or 8765:

```powershell
Get-NetTCPConnection -State Listen -LocalPort 8000,8001,8765 -ErrorAction SilentlyContinue |
    Select-Object LocalAddress,LocalPort,OwningProcess
```

This establishes the reported state of those services and ports at that time,
not a ChromaDB fix, whole-machine security, or the state after restarting services.
The Compose restriction takes effect only for a container created from the updated configuration.
Direct lab CLI commands do not need the dev-loop API; n8n tasks calling port 8765
need that separate service to be made safely reachable again.

## Audit status and the next decision

This change preserves `requirements.txt` and `.github/workflows/pip-audit.yml`.
Auditing stays enabled and findings remain visible. No `ignore-vuln`,
`continue-on-error`, or VEX assertion of an unaffected product is introduced.

Before merging, establish the actual local deployment profile and decide how to
handle residual risk. This assessment does not itself accept that risk. A green
audit without an exception requires a verified patched version or a separately
approved dependency change. New Chroma HTTP APIs, shared databases, untrusted
models, or public deployment require a new assessment before use.
