# Integration Strategy

The current stable mainline remains `main` at the Phase 42 stable baseline. Phase 43-53 are an open PR chain and should be treated as an Integration Candidate stack, not as production-ready mainline state.

## Current PR Stack

- PR #13: Docs Stabilization Sprint.
- PR #3-#12: Phase 43-52 runtime, workflow, artifact, release, and deployment stack.
- PR #14: Phase 53 Release Smoke Test Matrix and Preflight Automation.

## Recommended Integration Branch

Use `codex/integration-phase-43-53-candidate` as the temporary branch for final merge rehearsal after the open PR chain is refreshed.

## Recommended Merge Order

1. PR #13 docs stabilization.
2. PR #3 Phase 43 task scheduler recovery.
3. PR #4 Phase 44 artifact pipeline.
4. PR #5 Phase 45 workflow state.
5. PR #6 Phase 46 workflow graph runtime.
6. PR #7 Phase 47 template registry.
7. PR #8 Phase 48 template governance.
8. PR #9 Phase 49 workflow observability.
9. PR #10 Phase 50 desktop runtime UX.
10. PR #11 Phase 51 release packaging.
11. PR #12 Phase 52 deployment profiles.
12. PR #14 Phase 53 smoke/preflight.
13. Phase 54 reconciliation.

## Dependency Notes

- Phase 43 extends Phase 42 task orchestration and must land before recovery-aware task UI is trusted.
- Phase 44 depends on task/artifact linkage and should land before workflow lineage.
- Phase 45-49 are a workflow stack and should remain ordered.
- Phase 50-53 are readiness, packaging, deployment, and smoke orchestration layers.
- PR #14 depends on docs stabilization and deployment profiles.

## Rebase / Refresh Guidance

- PRs #3-#12 target `main`, so they may show overlapping diffs until the chain is integrated.
- PR #13 and PR #14 should be refreshed before final merge rehearsal if docs status or release matrices change.
- Later PRs may cover earlier PR files in frontend surfaces, docs, and tests. Prefer reviewing in dependency order instead of squashing the entire stack into one main PR.

## Conflict-Prone Areas

- `alembic/versions`
- `app/models`, `app/schemas`, `app/api/routes`
- `app/workflow`, `app/task_orchestration`
- `admin_dashboard/src/api`
- `worker_console/src/api`
- `worker_console_desktop/src/api`
- `release`, `deployment`, and `docs`

## Review Strategy

Avoid pushing all Phase 43-53 differences directly into a single main review. Use the open PR chain for phase-by-phase review, and use the integration branch only to verify combined behavior, migration continuity, frontend builds, Docker health, docs render QA, and release smoke readiness.

## Rollback Strategy

Rollback the integration candidate merge commit if the full stack lands as one rehearsal merge. If phases are merged individually, revert in reverse dependency order: Phase 53 back to Phase 43, then docs stabilization if needed. Do not roll back `main` with force push.

## Boundary

This stack is an Integration Candidate. It is not Production Ready, not a production installer, not code signed, not Kubernetes/Helm/Terraform, and not production HA orchestration.

## Phase 55 Extension

Phase 55 builds on this strategy with `docs/MAINLINE_INTEGRATION_PLAN.md`, `docs/RELEASE_CANDIDATE_PROCESS.md`, `release/integration/release_candidate_model.json`, `scripts/mainline_readiness.py`, `scripts/simulate_mainline_merge.py`, `scripts/generate_superseded_pr_report.py`, and `scripts/generate_mainline_integration_report.py`. Phase 55 still does not modify `main`; it only prepares the Release Candidate decision package.
