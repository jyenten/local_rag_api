# ChromaDB Security Risk Assessment

Status: OPEN
Scope: Local development only
Dependency: chromadb==1.5.9

## Architecture

The application uses chromadb.PersistentClient
with local filesystem persistence.

Repository inspection found no Chroma HTTP client
or Chroma server configuration.

The application itself exposes a FastAPI interface.
This is a separate security boundary.

## Known risks

ChromaDB 1.5.9 has published security advisories,
including critical code injection vulnerabilities
and authorization vulnerabilities.

No patched PyPI release has been confirmed.

## Current restrictions

- ChromaDB is approved only for isolated local development.
- Do not expose a Chroma HTTP server.
- Do not enable trust_remote_code for untrusted models.
- Do not disable pip-audit or Dependency Review.
- Do not use this assessment as production approval.

## Production exit criteria

Before production deployment:

1. Reassess all applicable ChromaDB advisories.
2. Upgrade to a verified patched version or replace the dependency.
3. Regenerate and validate dependency locks.
4. Run regression and retrieval evaluation tests.
5. Review the application API and document ingestion security.
6. Obtain explicit approval for any remaining risk.

Review status: Pending.
