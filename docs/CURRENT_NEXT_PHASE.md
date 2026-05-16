# Current Development State

## Current Active Branch

`main`

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate. PR #3-#12 remain open for cleanup or superseded disposition. PR #13 is the Docs Stabilization Sprint, and PR #14/#15 remain reviewable until the follow-up PR cleanup phase. PR #1 remains open.

Current effective phase: Phase 55 Mainline Acceptance. Phase 56 was reverted and is not active, not included in the accepted baseline, and not a valid continuation point.

## Current Recommended Next Phase

Post-merge stabilization is the current step. It does not add runtime features; it verifies the accepted Phase 55 baseline on `main`, preserves the rollback path, and prepares a separate PR cleanup / superseded marking phase.

## Open PRs

| PR | Title | Branch | Status / Note |
|---|---|---|---|
| #1 | Fix browser worker runtime registration and launch | `codex/browser-worker-runtime-fix-20260515` | Open; verify before merge because later branches include this fix lineage. |
| #3 | Phase 43 Task Scheduler Persistence and Worker Recovery | `codex/phase-43-task-scheduler-recovery` | Open |
| #4 | Phase 44 Output Artifact Pipeline and Export System | `codex/phase-44-output-artifact-pipeline` | Open |
| #5 | Phase 45 Workflow State and Agent Memory Foundation | `codex/phase-45-workflow-state-memory` | Open |
| #6 | Phase 46 Workflow Graph Runtime and Conditional Execution | `codex/phase-46-workflow-graph-runtime` | Open |
| #7 | Phase 47 Workflow Template Registry and Versioning | `codex/phase-47-workflow-template-registry` | Open |
| #8 | Phase 48 Workflow Template Marketplace and Governance Foundation | `codex/phase-48-template-marketplace-governance` | Open |
| #9 | Phase 49 Workflow Observability and Replay Center | `codex/phase-49-workflow-observability-replay` | Open |
| #10 | Phase 50 Desktop Runtime UX and Packaging Readiness | `codex/phase-50-desktop-runtime-ux-packaging-readiness` | Open |
| #11 | Phase 51 Release Packaging and Deployment Bundle Foundation | `codex/phase-51-release-packaging-foundation` | Open |
| #12 | Phase 52 Deployment Profiles and Environment Bootstrap | `codex/phase-52-deployment-profiles-bootstrap` | Open |
| #13 | Docs Stabilization Sprint | `codex/docs-stabilization-sprint` | Open |
| #14 | Phase 53 Release Smoke Test Matrix and Preflight Automation | `codex/phase-53-release-smoke-test-matrix-preflight` | Open |
| #15 | Phase 54 Integration Branch and PR Chain Reconciliation | `codex/phase-54-integration-branch-pr-chain-reconciliation` | Open |
| #16 | Phase 55 Mainline Integration Release Candidate Readiness | `codex/phase-55-mainline-integration-release-candidate` | Merged into PR #15 branch |
| #17 | Phase 43-55 Combined Release Candidate | `codex/phase-54-integration-branch-pr-chain-reconciliation` | Merged to `main` |

## Current Architecture State

The system is an AI operations runtime with FastAPI, PostgreSQL, Redis, Qdrant, local/mock LLM and embedding providers, Agentic RAG, task execution, browser workers, worker client runtime, admin dashboard, worker console, desktop console, conversation runtime, approvals, playbooks, output artifacts, workflow graph foundations, template governance, observability, release packaging, and deployment profiles.

## Current Runtime Capabilities

- API health, runtime settings, docs runtime verification.
- Workspace isolation across RAG, tasks, tools, browser, conversations, artifacts, and workflows.
- Browser worker registration, heartbeat, remote browser runtime, screenshots, page snapshots, timeline, replay metadata.
- Conversation threads, messages, events, tool routing, approvals, playbooks, background execution, artifacts.
- Workflow state, graph runtime, templates, governance, observability, and replay center are implemented in open PRs #3-#9.

## Current Deployment State

- `main` is Phase 55 stable after PR #17.
- Phase 43-55 are present on `main` through the combined RC merge.
- Phase 43-52 remain open as reviewable historical PRs until the cleanup / superseded phase.
- Phase 52 adds deployment profiles for local-dev, server-docker, client-worker, desktop-client, staging, and production-like.
- Phase 54 adds integration strategy, PR chain inventory, conflict surface detection, API/frontend drift checks, and integration report generation.
- Phase 55 adds mainline readiness, merge simulation, superseded PR decision reporting, and Release Candidate process documentation.
- Phase 56 is reverted/not active and must not enter post-merge stabilization.

## Current Packaging State

- Release packaging foundation exists in PR #11.
- Deployment bootstrap foundation exists in PR #12.
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

1. Keep feature work paused until post-merge verification on `main` is complete.
2. Keep PR #3-#15 and PR #1 open until the separate cleanup / superseded marking phase.
3. Decide whether PR #1 should be closed as superseded or merged independently after comparing it with the accepted mainline runtime.
4. Add CI checks for docs encoding, DOCX render readiness, and release/deployment validation in a later maintenance phase.
5. Do not start Phase 56 until PR cleanup, rollback posture, and deferred-feature boundaries are explicitly accepted.
