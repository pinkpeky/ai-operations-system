# Current Development State

## Current Active Branch

`codex/phase-61q-commercial-comfyui-handoffs`

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate and after the post-merge stabilization branch landed. PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after verification. Phase 56 was reverted and is not active. Phase 56A-56D readiness work has also landed on `main`, adding CI gates, required-check documentation, release readiness artifacts, and scheduled server Docker smoke. Phase 57A-57D, Phase 58A-58E, Phase 59A-59C, Phase 60A-60G, and Phase 61A-61P have landed on `main`, adding the Admin Dashboard Run Cockpit, guarded cockpit actions, operator controls, deep links, refresh UX, Playbooks context, Output Library context handoff, Phase 58 closeout, Run Cockpit search density, workflow handoff into Workflows and Replay Center, workflow focus/provenance, the frontend language foundation, the Overview role entry, the Conversations operator console, the RAG Documents knowledge console, RAG knowledge maintenance controls, Replay Center workflow observability simplification, RAG live validation guidance, the Commercial Ops project center, commercial operation evidence/handoff links, commercial operation approval gates, commercial operation safe dry-runs, commercial operation content drafts, commercial operation asset requests, commercial operation deliverables, commercial operation execution requests, commercial operation execution runs, commercial operation results, commercial operation monitoring observations, commercial operation optimization decisions, commercial operation evidence snapshots, commercial operation RAG evidence generation, commercial operation RAG content draft generation, and commercial operation RAG asset brief generation.

Current effective phase: Phase 61Q Commercial Operation ComfyUI Handoffs. The old reverted Phase 56 branch remains inactive and is not a valid continuation point.

## Current Recommended Next Phase

Readiness and PR cleanup are complete. PR #56 merged Phase 61P commercial RAG asset brief generation. The current step is normal product development on metadata-only ComfyUI handoff records for approved/prepared commercial asset requests.

Post-merge stabilization tracking lives in `docs/POST_MERGE_STABILIZATION.md`. That document records the migrated server toolchain state, Docker/WSL repair status, stabilization branch/remote discipline, browser runtime screenshot fix, PR #1 disposition, and verification gates.

The next active branch is `codex/phase-61q-commercial-comfyui-handoffs`. Its scope is adding `commercial_operation_comfyui_handoffs`, `/api/v1/commercial-operations/{operation_id}/comfyui-handoffs`, lifecycle actions, prompt/workflow payload storage, readiness checks, plan-step handoff state, and an Admin Dashboard panel for creating and reviewing metadata-only ComfyUI handoff records from approved or prepared asset requests. It still creates traceable records only; it does not submit ComfyUI jobs, generate images/videos, upload or ingest new knowledge files, auto-approve assets, auto-publish, control real accounts, execute OpenClaw actions, run Browser Worker actions, ingest platform analytics, claim ROI attribution, or bypass approval. CI readiness tracking lives in `docs/CI_READINESS_GATES.md`; branch protection guidance lives in `docs/BRANCH_PROTECTION.md`; scheduled smoke guidance lives in `docs/SCHEDULED_SMOKE.md`; run cockpit guidance lives in `docs/RUN_COCKPIT_FOUNDATION.md`.

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
| #35 | Phase 60B Overview Persona & Simplicity Foundation | `codex/phase-60-overview-persona-simplification` | Merged to `main` |
| #36 | Phase 60C Conversation Operator & Simplicity Foundation | `codex/phase-60-conversation-operator-simplification` | Merged to `main` |
| #37 | Phase 60D RAG Documents & Simplicity Foundation | `codex/phase-60-rag-documents-simplification` | Merged to `main` |
| #38 | Phase 60E RAG Operations & Simplicity Foundation | `codex/phase-60-rag-operations-ui` | Merged to `main` |
| #39 | Phase 60F Workflow Observability Operator & Simplicity Foundation | `codex/phase-60-workflow-observability-simplification` | Merged to `main` |
| #40 | Phase 60G RAG Live Validation & Operator Guidance | `codex/phase-60-rag-live-validation` | Merged to `main` |
| #41 | Phase 61A Commercial Operations Foundation | `codex/phase-60g-closeout-61a-operations-foundation` | Merged to `main` |
| #42 | Phase 61B Commercial Operation Links | `codex/phase-61b-commercial-operation-links` | Merged to `main` |
| #43 | Phase 61C Commercial Operation Approvals | `codex/phase-61c-commercial-operation-approvals` | Merged to `main` |
| #44 | Phase 61D Commercial Operation Safe Dry-Runs | `codex/phase-61d-commercial-operation-dry-runs` | Merged to `main` |
| #45 | Phase 61E Commercial Operation Content Drafts | `codex/phase-61e-commercial-operation-content-drafts` | Merged to `main` |
| #46 | Phase 61F Commercial Operation Asset Requests | `codex/phase-61f-commercial-operation-asset-requests` | Merged to `main` |
| #47 | Phase 61G Commercial Operation Deliverables | `codex/phase-61g-commercial-operation-deliverables` | Merged to `main` |
| #48 | Phase 61H Commercial Operation Execution Requests | `codex/phase-61h-commercial-operation-execution-requests` | Merged to `main` |
| #49 | Phase 61I Commercial Operation Execution Runs | `codex/phase-61i-commercial-operation-execution-runs` | Merged to `main` |
| #50 | Phase 61J Commercial Operation Results | `codex/phase-61j-commercial-operation-results` | Merged to `main` |
| #51 | Phase 61K Commercial Operation Monitoring Observations | `codex/phase-61k-commercial-monitoring-observations` | Merged to `main` |
| #52 | Phase 61L Commercial Operation Optimization Decisions | `codex/phase-61l-commercial-optimization-decisions` | Merged to `main` |
| #53 | Phase 61M Commercial Operation Evidence Snapshots | `codex/phase-61m-commercial-evidence-snapshots` | Merged to main |
| #54 | Phase 61N Commercial Operation RAG Evidence Generation | `codex/phase-61n-commercial-rag-evidence-generation` | Merged to main |
| #55 | Phase 61O Commercial Operation RAG Content Draft Generation | `codex/phase-61o-commercial-rag-content-drafts` | Merged to main |
| #56 | Phase 61P Commercial Operation RAG Asset Brief Generation | `codex/phase-61p-commercial-rag-asset-briefs` | Merged to main |
| #57 | Phase 61Q Commercial Operation ComfyUI Handoffs | `codex/phase-61q-commercial-comfyui-handoffs` | Draft PR |

PR #56 was merged to `main`; Phase 61Q is the current development slice and will open as PR #57 from `codex/phase-61q-commercial-comfyui-handoffs`.

## Current Architecture State

The system is an AI operations runtime with FastAPI, PostgreSQL, Redis, Qdrant, local/mock LLM and embedding providers, Agentic RAG, task execution, browser workers, worker client runtime, admin dashboard, worker console, desktop console, conversation runtime, approvals, playbooks, output artifacts, workflow graph foundations, template governance, observability, release packaging, and deployment profiles.

## Current Runtime Capabilities

- API health, runtime settings, docs runtime verification.
- Workspace isolation across RAG, tasks, tools, browser, conversations, artifacts, and workflows.
- Browser worker registration, heartbeat, remote browser runtime, screenshots, page snapshots, timeline, replay metadata.
- Conversation threads, messages, events, tool routing, approvals, playbooks, background execution, artifacts.
- Workflow state, graph runtime, templates, governance, observability, and replay center are accepted on `main`.
- Admin Dashboard now has a run cockpit for scanning conversations, task runs, approvals, diagnostics, playbook runs, and artifacts from one page.
- Admin Dashboard now has a Commercial Ops project center for turning an operating goal into a workspace-scoped project and reviewable plan draft.
- Phase 61B adds evidence and handoff links so a commercial operation can reference conversations, artifacts, task runs, workflow runs, RAG documents, approvals, knowledge sources, and external materials.
- Phase 61C adds approval gates so a plan step can be explicitly requested, approved, rejected, or cancelled by a human operator before later dry-run or execution phases.
- Phase 61D adds safe dry-runs so approved gates can produce metadata-only execution preparation records before any external action exists.
- Phase 61E adds content drafts so each channel can have a reviewable draft and source-material references before any publishing exists.
- Phase 61F adds first-class asset requests so images, videos, covers, design files, and supporting assets can be reviewed and prepared before any ComfyUI execution exists.
- Phase 61G adds deliverables so approved drafts and approved/prepared assets can be packaged into Output Library handoff artifacts before any publishing or external execution exists.
- Phase 61H adds execution requests so packaged deliverables can become metadata-only, approval-backed future runtime handoffs before any publishing or external execution exists.
- Phase 61I adds execution runs so prepared execution requests can have queued/running/succeeded/failed/retrying/cancelled/archived audit and recovery records before any publishing or external execution exists.
- Phase 61J adds commercial results so terminal execution runs can have draft/ready/approved/rejected/archived operator-observed result records before any platform analytics ingestion or ROI attribution exists.
- Phase 61K adds monitoring observations so approved commercial results can have draft/ready/approved/rejected/archived operator-observed monitoring snapshots before any platform analytics ingestion or ROI attribution exists.
- Phase 61L adds optimization decisions so approved monitoring observations can have draft/ready/approved/rejected/archived operator-decided next actions before any automatic optimization, publishing, or runtime execution exists.
- Phase 61M adds evidence snapshots so packaged deliverables can carry approved RAG/source evidence, evidence snapshot IDs, and operator checklists into execution requests and execution runs before any live RAG retrieval, knowledge ingestion, publishing, or external execution exists.
- Phase 61N adds RAG evidence generation so existing knowledge search can create a draft evidence snapshot with retrieved chunks, source document IDs, search metadata, and explicit human review requirements before any knowledge ingestion, approval bypass, publishing, or external execution exists.
- Phase 61O adds RAG content draft generation so existing knowledge search can create a draft content record with retrieved chunk source materials, search metadata, and explicit human review requirements before any knowledge ingestion, approval bypass, publishing, or external execution exists.
- Phase 61P adds RAG asset brief generation so existing knowledge search can create a draft asset request record with retrieved chunk source materials, readiness checks, search metadata, and explicit human review requirements before any knowledge ingestion, approval bypass, ComfyUI job, publishing, or external execution exists.
- Phase 61Q adds ComfyUI handoff records so approved/prepared asset requests can carry prompt payloads, workflow payloads, readiness checks, and human lifecycle decisions toward a future guarded adapter before any ComfyUI job submission, media generation, publishing, or account control exists.

## Current Deployment State

- `main` is Phase 55 stable after PR #17 plus Phase 56A-56D readiness closures.
- Phase 43-55 are present on `main` through the combined RC merge.
- Phase 57A-57D, Phase 58A-58E, Phase 59A-59C, Phase 60A-60G, and Phase 61A-61P are present on `main` through PR #22-#56.
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

1. Finish the Phase 61Q commercial ComfyUI handoff backend/API/frontend/docs slice.
2. Run backend, frontend, docs, migration, and browser verification gates.
3. Open PR #57 as a draft from `codex/phase-61q-commercial-comfyui-handoffs`.
4. Keep Docker compose running only while manual inspection is useful; otherwise shut it down cleanly with `docker compose -f docker-compose.yml down`.
5. After this slice, continue toward guarded ComfyUI/OpenClaw adapters, richer knowledge upload ergonomics, monitoring metrics, failure recovery, and commercial result reporting.
