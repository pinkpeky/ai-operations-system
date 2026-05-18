# Mainline Integration Plan

Phase 55 prepared and completed a controlled mainline Release Candidate merge window. PR #17 merged the Phase 43-55 Combined Release Candidate into `main`. This did not add runtime features beyond the accepted stack and does not declare the system production-ready.

PR #16 was accepted into the Phase 54 branch before PR #17 merged to `main`. Phase 56 was reverted and is not active, not part of this plan, and not a valid base for post-merge stabilization.

## Current Baseline

`main` is the Phase 55 stable baseline after PR #17.

## Integration Candidate Stack

The Phase 43-55 stack is accepted on `main` through PR #17. GitHub marked PR #3-#14 as merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 were later closed as superseded after post-merge verification.

- PR #13: Docs Stabilization Sprint.
- PR #3-#12: Phase 43-52 functional, release, deployment, and packaging stack.
- PR #14: Phase 53 Release Smoke Test Matrix and Preflight Automation.
- PR #15: Phase 54 Integration Branch and PR Chain Reconciliation.
- PR #16: Phase 55 Mainline Integration Release Candidate Readiness; merged into the Phase 54 branch.
- PR #17: Phase 43-55 Combined Release Candidate; merged to `main`.

Phase 55 built the mainline readiness layer on top of PR #15, then PR #17 accepted the combined stack into `main`.

## Recommended Merge Window

Post-merge verification should remain explicit and short. It should confirm:

- `scripts/mainline_readiness.py --profile server-docker` passes or expected post-merge warnings are documented.
- `scripts/release_preflight.py --profile server-docker` passes.
- `scripts/release_smoke_matrix.py` passes.
- Docs/render QA, migration continuity, runtime hygiene, frontend builds, pytest, and Docker verification pass.
- All generated readiness reports remain local QA artifacts unless explicitly requested.

## Recommended Release Candidate Branch

Accepted RC source:

`codex/phase-54-integration-branch-pr-chain-reconciliation`

Accepted target:

`main`

## Recommended Merge Path

1. Confirm `main` contains the accepted Phase 43-55 RC and post-merge stabilization fixes.
2. Keep superseded PRs closed with explanatory comments.
3. Do not reuse the reverted Phase 56 branch.
4. Begin any future Phase 56 only from a fresh `codex/` branch with explicit acceptance criteria.

## Review Order

1. Docs stabilization and phase index consistency.
2. Migration continuity and schema/API deltas from Phase 43-49.
3. Desktop runtime readiness and packaging boundaries from Phase 50.
4. Release/deployment profiles and smoke/preflight tooling from Phase 51-53.
5. Phase 54 integration reconciliation reports.
6. Phase 55 mainline readiness and merge simulation output.

## PR Disposition

- PR #3-#14 are already marked merged by GitHub after PR #17 because their changes are contained in `main`.
- PR #15 is closed as superseded after `main` advanced beyond the PR branch.
- PR #1 is closed as superseded after runtime-fix disposition was reviewed.
- No PR should be deleted. Superseded PRs should remain closed with their disposition comments.

## Manual Confirmation Risks

- Alembic migration ordering and downgrade review.
- API route drift across docs, OpenAPI, and frontends.
- Generated artifacts are ignored and not committed.
- Docker/browser-worker health stays stable after combined branch.
- No production installer, code signing, auto updater, Kubernetes, or HA orchestration is implied.

## Rollback Strategy

If the accepted RC must be rolled back, revert PR #17's merge commit from `main`. If phases are later disentangled separately, revert in reverse dependency order: Phase 55 back to Phase 43, then docs stabilization if needed. Do not force push `main`.

## Boundary

Phase 55 is accepted as the mainline Release Candidate baseline only. It is not a production release, not a formal installer, not code signed, not an auto updater, not Kubernetes/Helm/Terraform, not production HA orchestration, not real OpenClaw, and not real social automation.
