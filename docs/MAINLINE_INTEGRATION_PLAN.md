# Mainline Integration Plan

Phase 55 prepares a controlled mainline Release Candidate merge window. It does not merge into `main`, does not add runtime features, and does not declare the system production-ready.

PR #16 is the active Phase 55 RC readiness PR. Phase 56 was reverted and is not active, not part of this plan, and not a valid base for the RC decision.

## Current Baseline

`main` remains the Phase 42 stable baseline.

## Integration Candidate Stack

The Phase 43-54 stack is represented by open PRs and integration branches:

- PR #13: Docs Stabilization Sprint.
- PR #3-#12: Phase 43-52 functional, release, deployment, and packaging stack.
- PR #14: Phase 53 Release Smoke Test Matrix and Preflight Automation.
- PR #15: Phase 54 Integration Branch and PR Chain Reconciliation.
- PR #16: Phase 55 Mainline Integration Release Candidate Readiness.

Phase 55 builds the mainline readiness layer on top of PR #15.

## Recommended Merge Window

Open a short, explicit mainline merge window only after:

- `scripts/mainline_readiness.py --profile server-docker` passes.
- `scripts/simulate_mainline_merge.py --base main --head current --json` has been reviewed.
- `release/reports/superseded_prs.md` has been reviewed.
- All generated readiness reports remain local QA artifacts unless explicitly requested.

## Recommended Release Candidate Branch

Use:

`codex/phase-43-55-release-candidate`

The RC source should be:

`codex/phase-55-mainline-integration-release-candidate`

The target should remain:

`main`

## Recommended Merge Path

1. Keep PR #15 as the Phase 54 base for Phase 55.
2. Land Phase 55 as a preparation PR against PR #15.
3. After manual review, create a dedicated RC branch from the approved Phase 55 branch.
4. Open a separate RC PR toward `main`.
5. Do not merge the RC PR until all blocking gates pass.

## Review Order

1. Docs stabilization and phase index consistency.
2. Migration continuity and schema/API deltas from Phase 43-49.
3. Desktop runtime readiness and packaging boundaries from Phase 50.
4. Release/deployment profiles and smoke/preflight tooling from Phase 51-53.
5. Phase 54 integration reconciliation reports.
6. Phase 55 mainline readiness and merge simulation output.

## PR Disposition

- PR #13 should remain reviewable as the docs stabilization source.
- PR #3-#12 may be superseded by a final RC PR if the RC is reviewed as a combined integration merge.
- PR #14 remains the release preflight source and may be superseded by the RC after acceptance.
- PR #15 remains the integration reconciliation source and is the correct base for Phase 55.
- No PR should be deleted. Superseded PRs should be closed only after the RC is accepted or the manual review owner decides to keep phase-by-phase merges.

## Manual Confirmation Risks

- Alembic migration ordering and downgrade review.
- API route drift across docs, OpenAPI, and frontends.
- Generated artifacts are ignored and not committed.
- Docker/browser-worker health stays stable after combined branch.
- No production installer, code signing, auto updater, Kubernetes, or HA orchestration is implied.

## Rollback Strategy

If the final RC lands as one merge, revert the RC merge commit. If phases are merged separately, revert in reverse dependency order: Phase 55 back to Phase 43, then docs stabilization if needed. Do not force push `main`.

## Boundary

Phase 55 is Mainline Release Candidate preparation only. It is not a production release, not a formal installer, not code signed, not an auto updater, not Kubernetes/Helm/Terraform, not production HA orchestration, not real OpenClaw, and not real social automation.
