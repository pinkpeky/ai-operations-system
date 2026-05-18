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

Known host risk:

- `DISM /Online /Cleanup-Image /RestoreHealth` still requires a matching Windows IoT Enterprise LTSC 2024 `26100.x` source when the component store needs repair. Docker and WSL are currently functional, but OS servicing should be revisited with a matching install source.

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

## Documentation Expectations

Post-merge stabilization documentation must stay complete enough to recover the project on a new machine:

- Keep `docs/CURRENT_NEXT_PHASE.md` as the entry point for what should happen next.
- Keep `docs/CURRENT_RUNTIME.md` aligned with runtime defaults and host validation notes.
- Keep this document updated with environment repair results, test status, and branch/remote decisions.
- Do not reintroduce stale Phase 42 recovery language into current-state docs; `main` is now the Phase 55 accepted baseline.
- Avoid mojibake or replacement-character pollution in docs. If a file shows encoding corruption, fix the encoding source before editing content.

## Next Stabilization Gates

1. Run Docker compose service health / smoke checks with the repaired Docker Desktop backend.
2. Compare PR #1 against `main` and decide whether it is superseded or still needs an independent merge.
3. Only after these gates pass, move to PR cleanup or the next accepted phase.
