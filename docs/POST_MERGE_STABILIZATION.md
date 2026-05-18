# Post-Merge Stabilization

Updated: 2026-05-18

This document records the post-merge stabilization state after the server migration and Docker repair. It is a stabilization record for the accepted Phase 55 `main` baseline; it does not start Phase 56 and does not add new runtime features.

## Branch And Remote Discipline

- Stable baseline: `main`, tracking `origin/main`.
- Stabilization work branch: `codex/post-merge-stabilization`.
- Remote: `origin` -> `https://github.com/pinkpeky/ai-operations-system.git`.
- Do not force-push `main`.
- Use feature/stabilization branches with the `codex/` prefix.
- Keep PR #15 and PR #1 open until the separate PR cleanup / superseded decision phase.
- Push stabilization work only after local verification has a clear report.

## Server Toolchain State

Verified on the migrated Windows server:

- Python: installed and able to run project tests.
- Node/npm: installed and able to run frontend typecheck/build.
- LibreOffice: installed and available for DOCX render QA.
- Rust/cargo: installed for Worker Console Desktop / Tauri checks.
- Visual Studio Build Tools: installed for Windows native build checks.
- WSL: installed, `wsl --version` reports `2.6.3.0`.
- Docker Desktop: installed and running with WSL2 backend.
- Docker Engine: `29.4.3`.
- Docker Compose: `v5.1.3`.
- Docker runtime smoke: `docker run --rm hello-world` passed.
- Compose syntax smoke: `docker compose -f docker-compose.yml config --quiet` passed.
- Docker compose service smoke: `docker compose -f docker-compose.yml up -d --build` started PostgreSQL, Redis, Qdrant, browser-worker, and API successfully.
- Server Docker profile verification: `python deployment/scripts/verify_environment.py --profile server-docker` passed.
- Release smoke matrix: `python scripts/release_smoke_matrix.py --profile server-docker` passed.
- Browser runtime HTTP E2E through the API passed: worker registration, runtime session creation, navigation to `https://example.com`, screenshot storage, page content retrieval, and session close.

Known host risk:

- `DISM /Online /Cleanup-Image /RestoreHealth` still requires a matching Windows IoT Enterprise LTSC 2024 `26100.x` source when the component store needs repair. Docker and WSL are currently functional, but OS servicing should be revisited with a matching install source.
- Local Docker Qdrant uses an API key over HTTP, so the Qdrant Python client emits an insecure-connection warning during API startup. This is expected for the local `server-docker` profile and is not a production TLS posture.

## Stabilization Fixes

### Browser Runtime Screenshot Response

The customer-machine browser runtime screenshot flow must return `data.screenshot_base64` so the API server can store screenshots through `RemoteBrowserProvider`.

The fix makes screenshot capture more tolerant across real Playwright and test doubles:

- Prefer a path-based screenshot and read the resulting PNG when the runtime writes one.
- Fall back to direct screenshot bytes when the path write is unsupported or produces no file.
- Raise a clear runtime error only when neither a file nor bytes are produced.
- Update the shared fake Playwright fixture so `FakePage.screenshot()` matches Playwright behavior: `path` is optional, no-path calls return PNG bytes, and path calls write a PNG.

Verified tests:

```text
python -m pytest tests/test_browser_runtime_playwright.py tests/test_browser_runtime_worker.py -q
3 passed
```

```text
python -m pytest <browser_runtime_related_files> -q
17 passed
```

### Redis Queue Idle Polling

The API container initially logged repeated task executor errors while the Redis queue was empty. Root cause: the Redis client's `socket_timeout=5` matched the task executor's `BLPOP timeout=5`, so Redis socket timeout could fire before `BLPOP` returned a normal empty result.

The fix keeps `socket_connect_timeout=5` and sets `socket_timeout=None`, allowing blocking Redis commands to use their command-level timeout. After rebuilding the API image, idle queue polling no longer logs `Failed to dequeue task` / `Timeout reading from redis:6379`.

Verified tests:

```text
python -m pytest tests/test_queue.py tests/test_task_executor.py tests/test_task_events.py tests/test_task_logs.py -q
6 passed
```

### Qdrant Client Compatibility

The first Docker service smoke installed `qdrant-client 1.18.0` while the compose service uses `qdrant:v1.16.3`, which emitted a client/server minor-version compatibility warning at API startup.

The fix pins the Python dependency to `qdrant-client>=1.16.0,<1.18.0`. Local and rebuilt Docker images now use `qdrant-client 1.17.1`, which is within the compatibility range for Qdrant `1.16.3`.

Verified tests:

```text
python -m pytest tests/test_queue.py tests/test_task_executor.py tests/test_vector_store.py tests/test_embedding_health.py -q
11 passed
```

## Verification Results

Completed on 2026-05-18:

```text
python -m pytest -q
497 passed
```

```text
python scripts/verify_docs_runtime.py
SUMMARY: PASS
```

```text
python release/scripts/validate_release_packaging.py
SUMMARY: PASS
```

```text
npm --prefix admin_dashboard run typecheck
npm --prefix admin_dashboard run build
PASS
```

```text
npm --prefix worker_console run typecheck
npm --prefix worker_console run build
PASS
```

```text
npm --prefix worker_console_desktop run typecheck
npm --prefix worker_console_desktop run build
PASS
```

```text
python scripts/check_migration_continuity.py
SUMMARY: PASS
```

```text
python scripts/check_runtime_hygiene.py
SUMMARY: PASS
```

```text
docker compose -f docker-compose.yml config --quiet
PASS
```

```text
python deployment/scripts/verify_environment.py --profile server-docker
SUMMARY: PASS
```

```text
python scripts/release_smoke_matrix.py --profile server-docker
SUMMARY: PASS
```

```text
Browser runtime API E2E
registered=online
created=active
page_title=Example Domain
screenshot_path_present=true
page_contains_example=true
closed=closed
```

## PR #1 Disposition

PR #1: `Fix browser worker runtime registration and launch`

- Branch: `codex/browser-worker-runtime-fix-20260515`
- Commit: `9ea26a6`
- Compared against: `codex/post-merge-stabilization` at `d775d5d`
- Status: superseded by the accepted mainline plus post-merge stabilization fixes.

Review result:

- PR #1 added worker registration state matching for `worker_base_url`; the current code already includes that behavior.
- PR #1 added browser runtime Playwright provider coverage; the current code already includes the provider and now has additional screenshot fallback hardening.
- PR #1 added tests for registration refresh and browser runtime screenshot flow; those tests exist and pass on the stabilization branch.
- Current stabilization branch includes one extra registration status improvement: successful registration status now records `worker_base_url`.
- Current stabilization branch has passed real Docker service smoke, including Browser Worker registration and API-driven browser runtime screenshot E2E.

Verification:

```text
python -m pytest tests/test_worker_client_registration.py tests/test_browser_runtime_playwright.py tests/test_browser_runtime_worker.py -q
6 passed
```

Recommendation: close PR #1 as superseded after the `codex/post-merge-stabilization` branch is reviewed or merged. Do not merge PR #1 directly into `main`, because it is based on an older branch and would reintroduce stale branch history without adding unique runtime value.

## Documentation Expectations

Post-merge stabilization documentation must stay complete enough to recover the project on a new machine:

- Keep `docs/CURRENT_NEXT_PHASE.md` as the entry point for what should happen next.
- Keep `docs/CURRENT_RUNTIME.md` aligned with runtime defaults and host validation notes.
- Keep this document updated with environment repair results, test status, and branch/remote decisions.
- Do not reintroduce stale Phase 42 recovery language into current-state docs; `main` is now the Phase 55 accepted baseline.
- Avoid mojibake or replacement-character pollution in docs. If a file shows encoding corruption, fix the encoding source before editing content.

## Next Stabilization Gates

1. Decide whether to keep the local Docker compose stack running for manual inspection or shut it down after review.
2. Review or merge `codex/post-merge-stabilization`.
3. Close PR #1 as superseded after the stabilization branch lands.
4. Only after these gates pass, move to broader PR cleanup or the next accepted phase.
