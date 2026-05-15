# Current Development State

## Current Active Branch

`codex/docs-stabilization-sprint`

## Current Recommended Next Phase

Pause feature development and finish Docs Stabilization Sprint. After this PR is reviewed, reconcile the open PR stack in order or create an explicit integration branch strategy before adding runtime features.

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

## Current Architecture State

The system is an AI operations runtime with FastAPI, PostgreSQL, Redis, Qdrant, local/mock LLM and embedding providers, Agentic RAG, task execution, browser workers, worker client runtime, admin dashboard, worker console, desktop console, conversation runtime, approvals, playbooks, output artifacts, workflow graph foundations, template governance, observability, release packaging, and deployment profiles.

## Current Runtime Capabilities

- API health, runtime settings, docs runtime verification.
- Workspace isolation across RAG, tasks, tools, browser, conversations, artifacts, and workflows.
- Browser worker registration, heartbeat, remote browser runtime, screenshots, page snapshots, timeline, replay metadata.
- Conversation threads, messages, events, tool routing, approvals, playbooks, background execution, artifacts.
- Workflow state, graph runtime, templates, governance, observability, and replay center are implemented in open PRs #3-#9.

## Current Deployment State

- `main` is Phase 42 stable.
- Phase 43-52 are open PRs layered on top of each other.
- Phase 52 adds deployment profiles for local-dev, server-docker, client-worker, desktop-client, staging, and production-like.

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

1. Keep feature work paused until docs verifier, render QA, and phase indexes are stable.
2. Review PR #3 through PR #12 in dependency order before merging any later branch.
3. Decide whether PR #1 should be closed as superseded or merged independently after comparing with the later runtime branches.
4. Add CI checks for docs encoding, DOCX render readiness, and release/deployment validation.
5. After the docs sprint, create a clean integration plan for Phase 43-52 or continue with a new feature branch from the latest approved integration branch.
