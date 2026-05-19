# Current Development State

## Current Active Branch

`codex/phase-60-overview-persona-simplification`

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate and after the post-merge stabilization branch landed. PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after verification. Phase 56 was reverted and is not active. Phase 56A-56D readiness work has also landed on `main`, adding CI gates, required-check documentation, release readiness artifacts, and scheduled server Docker smoke. Phase 57A-57D, Phase 58A-58E, Phase 59A-59C, and Phase 60A have landed on `main`, adding the Admin Dashboard Run Cockpit, guarded cockpit actions, operator controls, deep links, refresh UX, Playbooks context, Output Library context handoff, Phase 58 closeout, Run Cockpit search density, workflow handoff into Workflows and Replay Center, workflow focus/provenance, and the frontend language foundation.

Current effective phase: Phase 60 Overview Persona & Simplicity Foundation. The old reverted Phase 56 branch remains inactive and is not a valid continuation point.

## Current Recommended Next Phase

Readiness and PR cleanup are complete. The current step is normal product development on Overview role entry and dashboard simplification after PR #34 merged the frontend language foundation.

Post-merge stabilization tracking lives in `docs/POST_MERGE_STABILIZATION.md`. That document records the migrated server toolchain state, Docker/WSL repair status, stabilization branch/remote discipline, browser runtime screenshot fix, PR #1 disposition, and verification gates.

The next active branch is `codex/phase-60-overview-persona-simplification`. Its scope is adding a Chinese-first Overview role switch for workstation operators and server maintainers, role-specific entry cards, localized overview metrics, and concise snapshot labels without changing backend runtime semantics. CI readiness tracking lives in `docs/CI_READINESS_GATES.md`; branch protection guidance lives in `docs/BRANCH_PROTECTION.md`; scheduled smoke guidance lives in `docs/SCHEDULED_SMOKE.md`; run cockpit guidance lives in `docs/RUN_COCKPIT_FOUNDATION.md`.

## PR State

| PR | Title | Branch | Status / Note |
|---|---|---|---|
| #3 | Phase 43 Task Scheduler Persistence and Worker Recovery | `codex/phase-43-task-scheduler-recovery` | Marked merged after PR #17 |
| #4 | Phase 44 Output Artifact Pipeline and Export System | `codex/phase-44-output-artifact-pipeline` | Marked merged after PR #17 |
| #5 | Phase 45 Workflow State and Agent Memory Foundation | `codex/phase-45-workflow-state-memory` | Marked merged after PR #17 |
| #6 | Phase 46 Workflow Graph Runtime and Conditional Execution | `codex/phase-46-workflow-graph-runtime` | Marked merged after PR #17 |
| #7 | Phase 47 Workflow Template Registry and Versioning | `codex/phase-47-workflow-template-registry` | Marked merged after PR #17 |
| #8 | Phase 48 Workflow Template Marketplace and Governance Foundation | `codex/phase-48-template-marketplace-governance` | Marked merged after PR #17 |
| #9 | Phase 49 Workflow Observability and Replay Center | `codex/phase-49-workflow-observability-replay` | Marked merged after PR #17 |
| #10 | Phase 50 Desktop Runtime UX and Packaging Readiness | `codex/phase-50-desktop-runtime-ux-packaging-readiness` | Marked merged after PR #17 |
| #11 | Phase 51 Release Packaging and Deployment Bundle Foundation | `codex/phase-51-release-packaging-foundation` | Marked merged after PR #17 |
| #12 | Phase 52 Deployment Profiles and Environment Bootstrap | `codex/phase-52-deployment-profiles-bootstrap` | Marked merged after PR #17 |
| #13 | Docs Stabilization Sprint | `codex/docs-stabilization-sprint` | Marked merged after PR #17 |
| #14 | Phase 53 Release Smoke Test Matrix and Preflight Automation | `codex/phase-53-release-smoke-test-matrix-preflight` | Marked merged after PR #17 |
| #15 | Phase 54 Integration Branch and PR Chain Reconciliation | `codex/phase-54-integration-branch-pr-chain-reconciliation` | Closed as superseded after `main` advanced beyond the PR branch |
| #16 | Phase 55 Mainline Integration Release Candidate Readiness | `codex/phase-55-mainline-integration-release-candidate` | Merged into PR #15 branch |
| #17 | Phase 43-55 Combined Release Candidate | `codex/phase-54-integration-branch-pr-chain-reconciliation` | Merged to `main` |
| #1 | Fix browser worker runtime registration and launch | `codex/browser-worker-runtime-fix-20260515` | Closed as superseded by `main` plus post-merge stabilization |
| #18 | CI Readiness Gates | `codex/phase-56-ci-readiness-gates` | Merged to `main` |
| #19 | Required Checks & Branch Protection Readiness | `codex/phase-56-required-checks-docs` | Merged to `main` |
| #20 | Release Readiness Report Artifacts | `codex/phase-56-report-artifacts` | Merged to `main` |
| #21 | Scheduled Docker Smoke | `codex/phase-56-scheduled-docker-smoke` | Merged to `main` |
| #22 | Run Cockpit Foundation | `codex/phase-57-run-cockpit-foundation` | Merged to `main` |
| #23 | Run Cockpit Actions | `codex/phase-57-run-cockpit-actions` | Merged to `main` |
| #24 | Run Cockpit Operator Controls | `codex/phase-57-run-cockpit-operator-controls` | Merged to `main` |
| #25 | Run Cockpit Closeout & Docs Reconciliation | `codex/phase-57-run-cockpit-closeout` | Merged to `main` |
| #26 | Run Cockpit Deep Links | `codex/phase-58-run-cockpit-deep-links` | Merged to `main` |
| #27 | Run Cockpit Refresh UX | `codex/phase-58-run-cockpit-refresh-ux` | Merged to `main` |
| #28 | Run Cockpit Playbook Thread Context | `codex/phase-58-playbook-thread-context` | Merged to `main` |
| #29 | Run Cockpit Output Library Context | `codex/phase-58-output-library-context` | Merged to `main` |
| #30 | Run Cockpit Closeout & Docs Reconciliation | `codex/phase-58-run-cockpit-closeout` | Merged to `main` |
| #31 | Run Cockpit Search & Density | `codex/phase-59-run-cockpit-search-density` | Merged to `main` |
| #32 | Run Cockpit Workflow Handoff | `codex/phase-59-run-cockpit-workflow-handoff` | Merged to `main` |
| #33 | Run Cockpit Workflow Focus | `codex/phase-59-run-cockpit-workflow-focus` | Merged to `main` |
| #34 | Phase 60A Frontend Language & Simplicity Foundation | `codex/phase-60-frontend-i18n-foundation` | Merged to `main` |

The active pull request for Phase 60B is not opened yet at the time of this update.

## Current Architecture State

The system is an AI operations runtime with FastAPI, PostgreSQL, Redis, Qdrant, local/mock LLM and embedding providers, Agentic RAG, task execution, browser workers, worker client runtime, admin dashboard, worker console, desktop console, conversation runtime, approvals, playbooks, output artifacts, workflow graph foundations, template governance, observability, release packaging, and deployment profiles.

## Current Runtime Capabilities

- API health, runtime settings, docs runtime verification.
- Workspace isolation across RAG, tasks, tools, browser, conversations, artifacts, and workflows.
- Browser worker registration, heartbeat, remote browser runtime, screenshots, page snapshots, timeline, replay metadata.
- Conversation threads, messages, events, tool routing, approvals, playbooks, background execution, artifacts.
- Workflow state, graph runtime, templates, governance, observability, and replay center are accepted on `main`.
- Admin Dashboard now has a run cockpit for scanning conversations, task runs, approvals, diagnostics, playbook runs, and artifacts from one page.

## Current Deployment State

- `main` is Phase 55 stable after PR #17 plus Phase 56A-56D readiness closures.
- Phase 43-55 are present on `main` through the combined RC merge.
- Phase 57A-57D, Phase 58A-58E, Phase 59A-59C, and Phase 60A are present on `main` through PR #22-#34.
- PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`.
- PR #1 and PR #15 are closed as superseded.
- Phase 52 adds deployment profiles for local-dev, server-docker, client-worker, desktop-client, staging, and production-like.
- Phase 54 adds integration strategy, PR chain inventory, conflict surface detection, API/frontend drift checks, and integration report generation.
- Phase 55 adds mainline readiness, merge simulation, superseded PR decision reporting, and Release Candidate process documentation.
- The old reverted Phase 56 branch is not active and must not be reused.

## Current Packaging State

- Release packaging foundation is accepted on `main`.
- Deployment bootstrap foundation is accepted on `main`.
- There is no formal production installer, code signing, auto updater, MSI/EXE release, DMG, notarization, Kubernetes, Helm, Terraform, or Ansible automation.

## Current Desktop Runtime State

- Worker Console Desktop uses Tauri.
- It can validate frontend build and Tauri shell readiness.
- It controls the worker runtime on the local machine only.
- Running it on the server host starts or checks a server-local worker, not a remote customer machine worker.

## Deferred Features

- ComfyUI not integrated.
- No real social media publishing.
- No captcha bypass.
- No proxy pool.
- No Kubernetes.
- No HA orchestration.
- No production installer/signing.
- No real OpenClaw device execution.
- No stealth browser bypass framework.
- No WebSocket/SSE streaming for conversation/workflow events.

## Current Blockers

- DOC render QA must be consistently available or must emit an explicit LibreOffice/soffice WARNING.
- Tauri native packaging readiness still needs customer-machine validation beyond frontend build.
- UTF pollution cleanup must prevent repeated question-mark corruption and mojibake from re-entering docs.

## Recommended Next Steps

1. Finish Phase 60B Overview Persona & Simplicity Foundation on `codex/phase-60-overview-persona-simplification`.
2. Verify Admin Dashboard typecheck/build, docs runtime checks, and the focused run cockpit frontend guard.
3. Open a PR, wait for PR Quality Gates, and merge only after remote checks pass.
4. Keep Docker compose running only while manual inspection is useful; otherwise shut it down cleanly with `docker compose -f docker-compose.yml down`.
5. After this slice, continue toward richer cockpit workflow diagnostics, trace timeline density, or operator bookmarks.
