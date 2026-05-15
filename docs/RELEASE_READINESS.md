# Release Readiness

Phase 53 introduces Release Smoke Test Matrix & Preflight Automation for the current integration candidate branch.

## Status

- Current stable `main`: Phase 42.
- Phase 43-52: open PR chain.
- PR #13: Docs Stabilization Sprint.
- Phase 53: Release smoke matrix and preflight automation on top of the docs stabilization branch.

This branch records the Phase 1-53 development state, but it does not mean all phases are merged into `main`.

## Readiness Categories

- pytest: `python -m pytest`
- Frontend build: `npm run build` in `admin_dashboard`, `worker_console`, and `worker_console_desktop`
- Docker verification: `docker compose up --build -d`
- Deployment verification: `python deployment/scripts/verify_environment.py --profile server-docker`
- Docs verifier and render QA: `python scripts/verify_docs_runtime.py`
- Release packaging validator: `python release/scripts/validate_release_packaging.py`
- Runtime hygiene: `python scripts/check_runtime_hygiene.py`
- Migration continuity: `python scripts/check_migration_continuity.py`
- Smoke matrix: `python scripts/release_smoke_matrix.py`
- Unified preflight: `python scripts/release_preflight.py --profile server-docker`

## Release Report

Generate a local readiness report:

```powershell
python scripts/generate_release_report.py --profile server-docker
```

The generated `release/reports/release_readiness_report.json` is a local QA artifact and is ignored by git.

## Current Boundaries

This is an Integration Candidate, not a production release. It is smoke verified, deployment verified, and docs/render QA verified when the above checks pass.

It is not:

- Kubernetes / Helm / Terraform
- CI/CD SaaS
- a real installer
- code signing
- an auto updater
- production HA orchestration
- ComfyUI
- real OpenClaw
- real social media automation
- stealth browser framework
