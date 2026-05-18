# CI Readiness Gates

Updated: 2026-05-18

This document records the first Phase 56 readiness slice. It starts from the post-merge stabilized Phase 55 `main` baseline and does not revive the reverted Phase 56 branch.

## Branch

- Source branch: `codex/phase-56-ci-readiness-gates`
- Base branch: `main`
- Scope: CI and repeatable readiness gates only.

## Workflows

### PR Quality Gates

File: `.github/workflows/pr-quality-gates.yml`

Runs on pull requests to `main`, pushes to `main`, and manual dispatch.

Checks:

- Python dependency installation.
- `python -m pytest -q`.
- `python scripts/verify_docs_runtime.py`, including DOCX render QA through LibreOffice.
- `python release/scripts/validate_release_packaging.py`.
- `python scripts/check_runtime_hygiene.py`.
- `python scripts/check_migration_continuity.py`.
- `python scripts/check_required_ci_gates.py`.
- Static release smoke group.
- `npm ci`, `npm run typecheck`, and `npm run build` for `admin_dashboard`, `worker_console`, and `worker_console_desktop`.

### Server Docker Smoke

File: `.github/workflows/server-docker-smoke.yml`

Runs by manual dispatch for `server-docker`, `staging`, or `production-like` profile verification.

Checks:

- `docker compose -f docker-compose.yml config --quiet`.
- `docker compose -f docker-compose.yml up -d --build`.
- API readiness through `/api/v1/health`.
- `python deployment/scripts/verify_environment.py --profile <profile>`.
- `python scripts/release_smoke_matrix.py --profile <profile> --strict`.
- Compose logs are printed on failure and the stack is shut down in an `always()` cleanup step.

## Local Verification

Before opening or merging a CI readiness PR, run:

```powershell
python scripts/verify_docs_runtime.py
python scripts/check_required_ci_gates.py
python scripts/release_smoke_matrix.py --group static --skip-docker --skip-build --skip-docs
```

## Remote Verification

PR #18 ran `PR Quality Gates` on GitHub Actions for commit `895cd40`.

Result:

```text
PR Quality Gates / Python docs and runtime gates: PASS
PR Quality Gates / Frontend build (admin_dashboard): PASS
PR Quality Gates / Frontend build (worker_console): PASS
PR Quality Gates / Frontend build (worker_console_desktop): PASS
```

Workflow run:

```text
26037766993
```

The manual `Server Docker Smoke` workflow is available through `workflow_dispatch`; trigger it from GitHub Actions when a remote Docker compose/profile smoke is needed.

Required branch-protection checks are tracked in `.github/required-checks.json` and documented in `docs/BRANCH_PROTECTION.md`.

For a full local server profile smoke, keep Docker Desktop running and run:

```powershell
docker compose -f docker-compose.yml config --quiet
python deployment/scripts/verify_environment.py --profile server-docker
python scripts/release_smoke_matrix.py --profile server-docker --strict
```

## Boundaries

- This is not a production release declaration.
- This does not add runtime business features.
- This does not add Kubernetes, Helm, Terraform, Ansible, code signing, installers, or auto update.
- The reverted Phase 56 branch remains inactive and must not be reused.
