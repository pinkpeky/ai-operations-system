# Docs Runtime Verification

Last updated: 2026-05-12

This document explains how to verify that docs match the current runtime.

## Goal

Docs Runtime Verification prevents:

- APIs being added without API_REFERENCE updates.
- Config defaults changing without CURRENT_RUNTIME updates.
- docker-compose drifting from config.
- Incorrect phase status.
- File Upload Pipeline being implemented without docs updates.
- Documentation claiming features that do not exist.

## Run

From the repository root:

```powershell
python scripts/verify_docs_runtime.py
```

Expected output:

```text
PASS: required docs files exist
PASS: CURRENT_RUNTIME contains config defaults
PASS: OpenAPI exposes required paths
PASS: API_REFERENCE includes required paths and fields
PASS: PROJECT_OVERVIEW includes current architecture markers
PASS: Phase 11 status is documented
SUMMARY: PASS
```

## Output Levels

`PASS`:

- Check succeeded.

`WARNING`:

- Potential drift. Review manually.

`ERROR`:

- Must be fixed. The script exits with a non-zero status.

## Current Checks

The script reads:

- `app/core/config.py`
- `docker-compose.yml`
- FastAPI OpenAPI schema
- `docs/CURRENT_RUNTIME.md`
- `docs/PROJECT_OVERVIEW.md`
- `docs/zh/API_REFERENCE.md`
- `docs/en/API_REFERENCE.md`
- `docs/zh/PROJECT_STATUS.md`
- `docs/en/PROJECT_STATUS.md`

It checks:

- Provider defaults.
- Search defaults.
- Embedding dimension.
- Upload settings.
- Required API paths.
- `search_mode`, `dense_top_k`, `keyword_top_k`, `final_top_k`, and `duplicate_strategy`.
- Phase 11 status.

## Docs Sync Rules

When adding an API:

1. Update the route.
2. Update the schema.
3. Update tests.
4. Update zh/en API_REFERENCE.
5. Run the verifier.

When adding config:

1. Update `app/core/config.py`.
2. Update `.env.example`.
3. Update `docker-compose.yml`.
4. Update `docs/CURRENT_RUNTIME.md`.
5. Update zh/en DEPLOYMENT.
6. Run the verifier.

When completing a phase:

1. Update `docs/PROJECT_OVERVIEW.md`.
2. Update zh/en PROJECT_STATUS.
3. Update zh/en ARCHITECTURE.
4. Update zh/en API_REFERENCE.
5. Update zh/en DEPLOYMENT.
6. Update zh/en DEVELOPMENT_GUIDE.
7. Update the Word snapshot.
8. Run pytest, Docker verification, and docs verifier.

## Test Integration

`tests/test_docs_runtime_verification.py` runs:

```powershell
python scripts/verify_docs_runtime.py
```

Docs drift therefore fails pytest.

## Scope

The verifier is a lightweight consistency check. It does not replace:

- Full API contract testing.
- Migration validation.
- Docker smoke testing.
- Security review.
- Performance testing.

Its job is to keep docs synchronized with runtime.
