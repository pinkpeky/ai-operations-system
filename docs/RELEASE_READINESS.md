# Release Readiness

Phase 53 introduced Release Smoke Test Matrix & Preflight Automation for the integration candidate branch. After PR #17, those gates are part of the accepted Phase 55 baseline on `main`.

## Status

- Current stable `main`: Phase 55.
- Current effective phase: Phase 55 Mainline Acceptance / post-merge verification.
- Phase 43-55: accepted into `main` through PR #17.
- PR #3-#14: marked merged after PR #17 because their changes are contained in `main`.
- PR #15: Phase 54 Integration Branch & PR Chain Reconciliation; remains open.
- PR #1: remains open.
- PR #16: merged into the Phase 54 branch.
- PR #17: merged Phase 43-55 Combined Release Candidate into `main`.
- Phase 56: reverted/not active; excluded from the RC decision.

This branch records the accepted Phase 1-55 development state. It is still not a production release.

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

This is a Phase 55 stable baseline on `main`, not a production release. It is smoke verified, deployment verified, and docs/render QA verified when the above checks pass.

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

## Phase 54 Integration Reconciliation

Phase 54 uses release readiness as one input to the integration candidate decision. It adds PR chain inventory, dependency matrix, conflict surface detection, OpenAPI/frontend drift checks, and integration report generation.

The integration readiness report is generated with:

```powershell
python scripts/generate_integration_report.py
```

Generated integration reports under `release/reports/` are ignored QA artifacts unless explicitly requested for archival.

## Phase 55 Mainline Readiness

Phase 55 adds mainline readiness tooling: `mainline_readiness.py`, `simulate_mainline_merge.py`, `generate_superseded_pr_report.py`, `generate_mainline_integration_report.py`, and `release_candidate_model.json`. These gates prepare a Release Candidate merge window and do not create a production release.
