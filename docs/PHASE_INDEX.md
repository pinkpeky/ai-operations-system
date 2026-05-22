# AI Operations System - Phase Index

## Current Stable Baseline

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate. It includes the Phase 42 runtime foundation plus the accepted Phase 43-55 scheduler, artifact, workflow, template, observability, packaging, deployment, smoke, integration, and readiness layers.

PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after post-merge verification. PR #16 was accepted into the Phase 54 branch, and PR #17 merged the combined Phase 43-55 RC into `main`.

## Current Active Development Branch

`main` is the active accepted baseline branch after Phase 56A-56D readiness closures, Phase 57A-59C Run Cockpit product slices, Phase 60A-60G frontend/RAG validation slices, Phase 61A Commercial Operations Foundation, Phase 61B Commercial Operation Evidence & Handoff Links, Phase 61C Commercial Operation Approval Gates, Phase 61D Commercial Operation Safe Dry-Runs, Phase 61E Commercial Operation Content Drafts, Phase 61F Commercial Operation Asset Requests, Phase 61G Commercial Operation Deliverables, Phase 61H Commercial Operation Execution Requests, Phase 61I Commercial Operation Execution Runs, Phase 61J Commercial Operation Results, Phase 61K Commercial Operation Monitoring Observations, Phase 61L Commercial Operation Optimization Decisions, Phase 61M Commercial Operation Evidence Snapshots, Phase 61N Commercial Operation RAG Evidence Generation, Phase 61O Commercial Operation RAG Content Draft Generation, and Phase 61P Commercial Operation RAG Asset Brief Generation.

Current effective phase: Phase 62I Workstation/Customer Client Frontend UX Alignment. Phase 56 was reverted and is not active. The old reverted Phase 56 branch is not active, not part of the accepted baseline, and should not be reused.

The current fresh branch is `codex/phase-62i-workstation-client-ux`. It stacks after draft PR #74 and aligns `worker_console` and `worker_console_desktop` for workstation/customer-machine operators before additional live ComfyUI probe escalation: simple status, runtime and heartbeat controls, conversation/playbook/task/output shortcuts, approval visibility, failure recovery guidance, setup/help panels, Chinese/English language switching, and explicit server/client boundary messaging. It is not a ComfyUI adapter, OpenClaw execution, publishing, account-control, installer-signing, auto-update, captcha/proxy/fingerprint, or live-platform automation phase.

## Open PR List

| PR | Title | Branch | Status / Note |
|---|---|---|---|
| #1 | Fix browser worker runtime registration and launch | `codex/browser-worker-runtime-fix-20260515` | Closed as superseded |
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
| #15 | Phase 54 Integration Branch and PR Chain Reconciliation | `codex/phase-54-integration-branch-pr-chain-reconciliation` | Closed as superseded |
| #16 | Phase 55 Mainline Integration Release Candidate Readiness | `codex/phase-55-mainline-integration-release-candidate` | Merged into PR #15 branch |
| #17 | Phase 43-55 Combined Release Candidate | `codex/phase-54-integration-branch-pr-chain-reconciliation` | Merged to `main` |
| #18 | CI Readiness Gates | `codex/phase-56-ci-readiness-gates` | Merged to main |
| #19 | Required Checks & Branch Protection Readiness | `codex/phase-56-required-checks-docs` | Merged to main |
| #20 | Release Readiness Report Artifacts | `codex/phase-56-report-artifacts` | Merged to main |
| #21 | Scheduled Docker Smoke | `codex/phase-56-scheduled-docker-smoke` | Merged to main |
| #22 | Run Cockpit Foundation | `codex/phase-57-run-cockpit-foundation` | Merged to main |
| #23 | Run Cockpit Actions | `codex/phase-57-run-cockpit-actions` | Merged to main |
| #24 | Run Cockpit Operator Controls | `codex/phase-57-run-cockpit-operator-controls` | Merged to main |
| #25 | Run Cockpit Closeout & Docs Reconciliation | `codex/phase-57-run-cockpit-closeout` | Merged to main |
| #26 | Run Cockpit Deep Links | `codex/phase-58-run-cockpit-deep-links` | Merged to main |
| #27 | Run Cockpit Refresh UX | `codex/phase-58-run-cockpit-refresh-ux` | Merged to main |
| #28 | Run Cockpit Playbook Thread Context | `codex/phase-58-playbook-thread-context` | Merged to main |
| #29 | Run Cockpit Output Library Context | `codex/phase-58-output-library-context` | Merged to main |
| #30 | Run Cockpit Closeout & Docs Reconciliation | `codex/phase-58-run-cockpit-closeout` | Merged to main |
| #31 | Run Cockpit Search & Density | `codex/phase-59-run-cockpit-search-density` | Merged to main |
| #32 | Run Cockpit Workflow Handoff | `codex/phase-59-run-cockpit-workflow-handoff` | Merged to main |
| #33 | Run Cockpit Workflow Focus | `codex/phase-59-run-cockpit-workflow-focus` | Merged to main |
| #34 | Phase 60A Frontend Language & Simplicity Foundation | `codex/phase-60-frontend-i18n-foundation` | Merged to main |
| #35 | Phase 60B Overview Persona & Simplicity Foundation | `codex/phase-60-overview-persona-simplification` | Merged to main |
| #36 | Phase 60C Conversation Operator & Simplicity Foundation | `codex/phase-60-conversation-operator-simplification` | Merged to main |
| #37 | Phase 60D RAG Documents & Simplicity Foundation | `codex/phase-60-rag-documents-simplification` | Merged to main |
| #38 | Phase 60E RAG Operations & Simplicity Foundation | `codex/phase-60-rag-operations-ui` | Merged to main |
| #39 | Phase 60F Workflow Observability Operator & Simplicity Foundation | `codex/phase-60-workflow-observability-simplification` | Merged to main |
| #40 | Phase 60G RAG Live Validation & Operator Guidance | `codex/phase-60-rag-live-validation` | Merged to main |
| #41 | Phase 61A Commercial Operations Foundation | `codex/phase-60g-closeout-61a-operations-foundation` | Merged to main |
| #42 | Phase 61B Commercial Operation Links | `codex/phase-61b-commercial-operation-links` | Merged to main |
| #43 | Phase 61C Commercial Operation Approvals | `codex/phase-61c-commercial-operation-approvals` | Merged to main |
| #44 | Phase 61D Commercial Operation Safe Dry-Runs | `codex/phase-61d-commercial-operation-dry-runs` | Merged to main |
| #45 | Phase 61E Commercial Operation Content Drafts | `codex/phase-61e-commercial-operation-content-drafts` | Merged to main |
| #46 | Phase 61F Commercial Operation Asset Requests | `codex/phase-61f-commercial-operation-asset-requests` | Merged to main |
| #47 | Phase 61G Commercial Operation Deliverables | `codex/phase-61g-commercial-operation-deliverables` | Merged to main |
| #48 | Phase 61H Commercial Operation Execution Requests | `codex/phase-61h-commercial-operation-execution-requests` | Merged to main |
| #49 | Phase 61I Commercial Operation Execution Runs | `codex/phase-61i-commercial-operation-execution-runs` | Merged to main |
| #50 | Phase 61J Commercial Operation Results | `codex/phase-61j-commercial-operation-results` | Merged to main |
| #51 | Phase 61K Commercial Operation Monitoring Observations | `codex/phase-61k-commercial-monitoring-observations` | Merged to main |
| #52 | Phase 61L Commercial Operation Optimization Decisions | `codex/phase-61l-commercial-optimization-decisions` | Merged to main |
| #53 | Phase 61M Commercial Operation Evidence Snapshots | `codex/phase-61m-commercial-evidence-snapshots` | Merged to main |
| #54 | Phase 61N Commercial Operation RAG Evidence Generation | `codex/phase-61n-commercial-rag-evidence-generation` | Merged to main |
| #55 | Phase 61O Commercial Operation RAG Content Draft Generation | `codex/phase-61o-commercial-rag-content-drafts` | Merged to main |
| #56 | Phase 61P Commercial Operation RAG Asset Brief Generation | `codex/phase-61p-commercial-rag-asset-briefs` | Merged to main |
| #57 | Phase 61Q Commercial Operation ComfyUI Handoffs | `codex/phase-61q-commercial-comfyui-handoffs` | Draft PR |
| #58 | Phase 61R Commercial Operation ComfyUI Preflights | `codex/phase-61r-commercial-comfyui-preflight` | Draft PR |
| #59 | Phase 61S Commercial Operation ComfyUI Adapter Configs | `codex/phase-61s-commercial-comfyui-adapter-configs` | Draft PR |
| #60 | Phase 61T Commercial Operation ComfyUI Job Requests | `codex/phase-61t-commercial-comfyui-job-requests` | Draft PR |
| #61 | Phase 61U Commercial Operation ComfyUI Execution Plans | `codex/phase-61u-commercial-comfyui-execution-plans` | Draft PR |
| #62 | Phase 61V Commercial Operation ComfyUI Connection Probes | `codex/phase-61v-commercial-comfyui-connection-probes` | Draft PR |
| #63 | Phase 61W Commercial Operation ComfyUI Adapter Dispatches | `codex/phase-61w-commercial-comfyui-adapter-dispatches` | Draft PR |
| #64 | Phase 61X Commercial Operation ComfyUI Runtime Gates | `codex/phase-61x-commercial-comfyui-runtime-gates` | Draft PR |
| #65 | Phase 61Y Commercial Operation ComfyUI Runtime Dry-Runs | `codex/phase-61y-commercial-comfyui-runtime-dry-runs` | Draft PR |
| #66 | Phase 61Z Commercial Operation ComfyUI Runtime Activations | `codex/phase-61z-commercial-comfyui-runtime-activations` | Draft PR |
| #67 | Phase 62A ComfyUI Runtime Adapter Contract | `codex/phase-62a-comfyui-runtime-adapter-contract` | Draft PR |
| #68 | Phase 62B ComfyUI Guarded Read-Only Probe | `codex/phase-62b-comfyui-guarded-readonly-probe` | Draft PR |
| #69 | Phase 62C ComfyUI Runtime Diagnostics | `codex/phase-62c-comfyui-runtime-diagnostics` | Draft PR |
| #70 | Phase 62D ComfyUI Runtime Diagnostic Snapshots | `codex/phase-62d-comfyui-runtime-diagnostic-snapshots` | Draft PR |
| #71 | Phase 62E ComfyUI Runtime Maintenance Runbook | `codex/phase-62e-comfyui-maintenance-console` | Draft PR |
| #72 | Phase 62F ComfyUI Runtime Configuration Change Requests | `codex/phase-62f-comfyui-config-change-requests` | Draft PR |
| #73 | Phase 62G ComfyUI Runtime Manual Apply Evidence | `codex/phase-62g-comfyui-manual-apply-evidence` | Draft PR |
| #74 | Phase 62H ComfyUI Runtime Post-Manual Readiness Checks | `codex/phase-62h-comfyui-post-manual-readiness` | Draft PR |
| Planned | Phase 62I Workstation/Customer Client Frontend UX Alignment | `codex/phase-62i-workstation-client-ux` | In progress after PR #74 |

## Phase Timeline Table

| Phase | Title | Branch | PR | Status | Key Features |
|---|---|---|---|---|---|
| 1 | FastAPI Foundation | `historical/main` | N/A | Merged baseline | Initial API service skeleton and runtime conventions. |
| 2 | PostgreSQL Persistence | `historical/main` | N/A | Merged baseline | Database-backed persistence foundation. |
| 3 | Redis Runtime Cache | `historical/main` | N/A | Merged baseline | Redis integration for runtime state and queue support. |
| 4 | Qdrant Vector Store | `historical/main` | N/A | Merged baseline | Vector database foundation for retrieval. |
| 5 | Ollama / Mistral Local LLM | `historical/main` | N/A | Merged baseline | Local LLM provider wiring with mock-safe defaults. |
| 6 | bge-m3 Embedding Foundation | `historical/main` | N/A | Merged baseline | Embedding provider abstraction and local embedding defaults. |
| 7 | Agentic RAG | `historical/main` | N/A | Merged baseline | Agentic RAG orchestration and query trace foundations. |
| 8 | Workspace Isolation | `historical/main` | N/A | Merged baseline | Workspace-scoped middleware and storage filtering. |
| 9 | Knowledge Lifecycle | `historical/main` | N/A | Merged baseline | Document lifecycle, ingest, active filtering, and duplicate handling. |
| 10 | Hybrid Search | `historical/main` | N/A | Merged baseline | Dense + keyword retrieval and scoring. |
| 11 | Reranker Layer | `historical/main` | N/A | Merged baseline | Mock/local reranker client and result normalization. |
| 12 | Eval / Trace | `historical/main` | N/A | Merged baseline | Evaluation runs, trace payloads, and debug surfaces. |
| 13 | File Upload Pipeline | `historical/main` | N/A | Merged baseline | Upload validation, parsing, and file lifecycle. |
| 14 | Docs Runtime Verification | `historical/main` | N/A | Merged baseline | Docs/runtime consistency verifier. |
| 15 | Task Queue | `historical/main` | N/A | Merged baseline | Task queue primitives and API surface. |
| 16 | Task Executor | `historical/main` | N/A | Merged baseline | Task execution handlers and structured task results. |
| 17 | Task Observability | `historical/main` | N/A | Merged baseline | Task logs, task events, and observability summary. |
| 18 | Tool Calling | `historical/main` | N/A | Merged baseline | ToolRegistry, tool execution API, and tool call logs. |
| 19 | Memory Foundation | `historical/main` | N/A | Merged baseline | Conversation memory sessions, messages, and memories. |
| 20 | Multi-Agent Foundation | `historical/main` | N/A | Merged baseline | Agent registry, multi-agent runs, messages, and handoffs. |
| 21 | Agent Planning Foundation | `historical/main` | N/A | Merged baseline | Plan creation, steps, reviews, and planning API. |
| 22 | Browser Automation Adapter | `historical/main` | N/A | Merged baseline | Browser provider abstraction and browser_tool foundation. |
| 23 | Browser Profile Health & Recovery | `historical/main` | N/A | Merged baseline | Persistent profile health, recovery, backup, cleanup, and usage logs. |
| 24 | Human-in-the-loop Browser Control | `historical/main` | N/A | Merged baseline | Human control sessions, events, pause/resume, and browser_tool action. |
| 25 | Browser UI Access Placeholder | `historical/main` | N/A | Merged baseline | UI access sessions, token hashing, scoped placeholder URLs. |
| 26 | Browser Worker Security & Access Control | `historical/main` | N/A | Merged baseline | Worker secrets, signed requests, UI scopes, action policy, and audit logs. |
| 27 | Customer Machine Worker Bootstrap | `historical/main` | N/A | Merged baseline | worker_client CLI, registration, heartbeat, runtime server. |
| 28 | OpenClaw Worker Adapter Foundation | `historical/main` | N/A | Merged baseline | Mock OpenClaw provider, worker runtime routes, OpenClaw tool and logs. |
| 29 | Worker Client Packaging & Worker Console Foundation | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Runtime manager, local API, local status/logs, packaging scripts. |
| 30 | Worker Console GUI Foundation | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Worker Console Web GUI with local worker controls and logs. |
| 31 | Worker Console Desktop App Foundation | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Tauri desktop shell foundation. |
| 32 | Worker Console System Tray & Desktop Runtime Foundation | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | System tray, minimize-to-tray, status sync, desktop settings. |
| 33 | Conversation Runtime Foundation | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Threads, messages, events, polling timeline, chat panel foundation. |
| 34 | Remote Browser Runtime Foundation | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | RemoteBrowserProvider, worker browser runtime, Playwright Chromium lifecycle. |
| 35A | Browser Runtime Observability & Replay | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Browser runtime timeline, snapshots, replay metadata, failure debug. |
| 35B | Real Client Worker E2E Validation Plan | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Real client E2E validation script and checklist; no fabricated client result. |
| 36 | Server Admin Dashboard Foundation | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Admin Dashboard monitoring UI and API clients. |
| 37 | Conversation Runtime Frontend Integration | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Admin/Worker/Desktop conversation panels and polling event timeline. |
| 38 | Conversation Runtime Tool Execution Bridge | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Rule-based routing to browser, OpenClaw mock, RAG, content, planning. |
| 39 | Conversation Execution Review & Approval Flow | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Approval model, risk policy, run modes, frontend approval panel. |
| 40 | Conversation Execution Templates & Playbooks | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Built-in playbooks, step executor, playbook runs, approval integration. |
| 41 | Playbook Run Artifacts & Output Library | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Output artifacts, export markdown/json/txt, Output Library UI. |
| 42 | Task Orchestration & Background Execution | `codex/phase-31-worker-console-desktop` | #2 | Merged to main | Task runs, task events, background executor, retry policy, artifact linkage. |
| 43 | Task Scheduler Persistence & Worker Recovery | `codex/phase-43-task-scheduler-recovery` | #3 | Merged to main | Task lease, scheduler state, recovery service, diagnostics. |
| 44 | Output Artifact Pipeline & Export System | `codex/phase-44-output-artifact-pipeline` | #4 | Merged to main | Artifact lineage, relationship graph, export/package/retention services. |
| 45 | Workflow State & Agent Memory Foundation | `codex/phase-45-workflow-state-memory` | #5 | Merged to main | Workflow runs, steps, checkpoints, agent memory snapshots. |
| 46 | Workflow Graph Runtime & Conditional Execution | `codex/phase-46-workflow-graph-runtime` | #6 | Merged to main | Workflow graphs, planner, conditional routing, retry/fallback, replay foundation. |
| 47 | Workflow Template Registry & Versioning | `codex/phase-47-workflow-template-registry` | #7 | Merged to main | Workflow templates, versions, built-in templates, import/export. |
| 48 | Workflow Template Marketplace & Governance Foundation | `codex/phase-48-template-marketplace-governance` | #8 | Merged to main | Reviews, lifecycle, rollback, compatibility matrix, internal marketplace. |
| 49 | Workflow Run Observability & Replay Center | `codex/phase-49-workflow-observability-replay` | #9 | Merged to main | Execution traces, diagnostics, replay sessions, runtime analytics. |
| 50 | Desktop Console Runtime UX & Client Packaging Readiness | `codex/phase-50-desktop-runtime-ux-packaging-readiness` | #10 | Merged to main | Tauri icon fix, Start Runtime diagnostics, server/client boundary UX. |
| 51 | Release Packaging & Deployment Bundle Foundation | `codex/phase-51-release-packaging-foundation` | #11 | Merged to main | Release manifest, version metadata, bundle scripts, startup scripts. |
| 52 | Deployment Profiles & Environment Bootstrap | `codex/phase-52-deployment-profiles-bootstrap` | #12 | Merged to main | Deployment profiles, env generator, dependency/port/env verification. |
| 53 | Release Smoke Test Matrix & Preflight Automation | `codex/phase-53-release-smoke-test-matrix-preflight` | #14 | Merged to main | Unified preflight, smoke matrix, release report, migration continuity, runtime hygiene. |
| 54 | Integration Branch & PR Chain Reconciliation | `codex/phase-54-integration-branch-pr-chain-reconciliation` | #15 | Closed as superseded | Integration strategy, PR inventory, dependency matrix, conflict detection, drift checks, integration report. |
| 55 | Mainline Integration & Release Candidate Merge Window | `codex/phase-55-mainline-integration-release-candidate` | #16/#17 | Merged to main | Mainline readiness, merge simulation, release candidate model, superseded PR report. |
| 56A | CI Readiness Gates | `codex/phase-56-ci-readiness-gates` | #18 | Merged to main | GitHub Actions gates for docs/runtime verification, packaging, hygiene, migration continuity, frontend builds, and manual Docker smoke. |
| 56B | Required Checks & Branch Protection Readiness | `codex/phase-56-required-checks-docs` | #19 | Merged to main | Machine-readable required checks, branch protection documentation, and required-check validation. |
| 56C | Release Readiness Report Artifacts | `codex/phase-56-report-artifacts` | #20 | Merged to main | CI readiness report generation and artifact upload for PR and Docker smoke workflows. |
| 56D | Scheduled Docker Smoke | `codex/phase-56-scheduled-docker-smoke` | #21 | Merged to main | Daily server-docker smoke schedule, default scheduled profile, concurrency guard, and scheduled-smoke documentation. |
| 57A | Run Cockpit Foundation | `codex/phase-57-run-cockpit-foundation` | #22 | Merged to main | Admin Dashboard run cockpit for conversations, task runs, approvals, diagnostics, playbook runs, scheduler health, and linked artifacts. |
| 57B | Run Cockpit Actions | `codex/phase-57-run-cockpit-actions` | #23 | Merged to main | Guarded approval actions, task control/recovery actions, linked artifact export, and last-action result feedback from the Run Cockpit. |
| 57C | Run Cockpit Operator Controls | `codex/phase-57-run-cockpit-operator-controls` | #24 | Merged to main | Task view filters, optional auto refresh, and navigation from the cockpit to Conversations, Playbooks, Tasks, and Output Library. |
| 57D | Run Cockpit Closeout & Docs Reconciliation | `codex/phase-57-run-cockpit-closeout` | #25 | Merged to main | Phase 57 documentation closeout, current-state reconciliation, and checks that prevent merged run cockpit slices from staying marked as active. |
| 58A | Run Cockpit Deep Links | `codex/phase-58-run-cockpit-deep-links` | #26 | Merged to main | URL query state, selected thread/task/artifact handoff, and deep links from the cockpit into Conversations, Tasks, and Output Library. |
| 58B | Run Cockpit Refresh UX | `codex/phase-58-run-cockpit-refresh-ux` | #27 | Merged to main | Auto-refresh visibility, countdown/status labels, refresh interval display, and stale-data preservation on cockpit load failures. |
| 58C | Run Cockpit Playbook Thread Context | `codex/phase-58-playbook-thread-context` | #28 | Merged to main | Playbooks page thread context, run-history filtering, linked conversation navigation, and clear-context controls for Run Cockpit handoff. |
| 58D | Run Cockpit Output Library Context | `codex/phase-58-output-library-context` | #29 | Merged to main | Output Library thread/task/artifact context, linked-run artifact filtering, linked conversation/task navigation, and clear-context controls. |
| 58E | Run Cockpit Closeout & Docs Reconciliation | `codex/phase-58-run-cockpit-closeout` | #30 | Merged to main | Phase 58 documentation closeout, current-state reconciliation, and guard checks that prevent completed Run Cockpit slices from staying marked active. |
| 59A | Run Cockpit Search & Density | `codex/phase-59-run-cockpit-search-density` | #31 | Merged to main | Run Cockpit search, filtered density counters, and operator scan ergonomics across threads, task runs, playbook runs, and output artifacts. |
| 59B | Run Cockpit Workflow Handoff | `codex/phase-59-run-cockpit-workflow-handoff` | #32 | Merged to main | Workflow run context handoff from Run Cockpit into Workflows and Replay Center, linked workflow summary, and workflow deep-link restoration. |
| 59C | Run Cockpit Workflow Focus | `codex/phase-59-run-cockpit-workflow-focus` | #33 | Merged to main | Workflow provenance, focus/loading/unavailable states, and linked source candidates for selected task, playbook, and artifact contexts. |
| 60A | Frontend Language & Simplicity Foundation | `codex/phase-60-frontend-i18n-foundation` | #34 | Merged to main | Admin Dashboard language switch, Chinese default shell labels, localized Run Cockpit operator labels, and simplification foundation. |
| 60B | Overview Persona & Simplicity Foundation | `codex/phase-60-overview-persona-simplification` | #35 | Merged to main | Overview role switch for workstation operators and server maintainers, role-specific entry points, localized overview metrics, and concise status snapshot labels. |
| 60C | Conversation Operator & Simplicity Foundation | `codex/phase-60-conversation-operator-simplification` | #36 | Merged to main | Conversations page command summary, localized create/send/run controls, run-mode guidance, approval/event/artifact section labels, and operator-friendly conversation metrics. |
| 60D | RAG Documents & Simplicity Foundation | `codex/phase-60-rag-documents-simplification` | #37 | Merged to main | RAG / Documents knowledge console, localized health/collection/document/search labels, operator summary cards, and clearer hybrid retrieval feedback. |
| 60E | RAG Operations & Simplicity Foundation | `codex/phase-60-rag-operations-ui` | #38 | Merged to main | RAG upload, text ingest, document detail, reingest, delete confirmation, retrieval debug, and operator result feedback. |
| 60F | Workflow Observability Operator & Simplicity Foundation | `codex/phase-60-workflow-observability-simplification` | #39 | Merged to main | Replay Center command center, localized scan labels, attention metrics, trace filters, and clearer replay boundaries. |
| 60G | RAG Live Validation & Operator Guidance | `codex/phase-60-rag-live-validation` | #40 | Merged to main | Live RAG upload/search/debug/reingest/delete validation, operator guide, and a concise RAG operation loop hint. |
| 61A | Commercial Operations Foundation | `codex/phase-60g-closeout-61a-operations-foundation` | #41 | Merged to main | `commercial_operations`, `/api/v1/commercial-operations`, goal-to-plan API, Admin Dashboard Commercial Ops page, and clear boundary that planning does not publish or execute external actions. |
| 61B | Commercial Operation Evidence & Handoff Links | `codex/phase-61b-commercial-operation-links` | #42 | Merged to main | `commercial_operation_links`, operation link create/list/delete APIs, Admin Dashboard Evidence and handoff panel, and manual links to conversations, artifacts, task runs, workflow runs, RAG documents, approvals, knowledge sources, and external materials. |
| 61C | Commercial Operation Approval Gates | `codex/phase-61c-commercial-operation-approvals` | #43 | Merged to main | `commercial_operation_approvals`, operation approval create/list/approve/reject/cancel APIs, Admin Dashboard Approval gates panel, and plan-step approval state written back to `plan_outline` without external execution. |
| 61D | Commercial Operation Safe Dry-Runs | `codex/phase-61d-commercial-operation-dry-runs` | #44 | Merged to main | `commercial_operation_dry_runs`, approved-approval gated dry-run create/list/complete/fail/cancel APIs, Admin Dashboard Safe dry-runs panel, and plan-step dry-run state written back to `plan_outline` without OpenClaw, ComfyUI, browser worker, account, or publishing execution. |
| 61E | Commercial Operation Content Drafts | `codex/phase-61e-commercial-operation-content-drafts` | #45 | Merged to main | `commercial_operation_content_drafts`, content-draft create/list/update/ready/approve/reject/archive APIs, Admin Dashboard Content drafts panel, and plan-step content draft state written back to `plan_outline` without publishing, OpenClaw, ComfyUI, browser worker, or account execution. |
| 61F | Commercial Operation Asset Requests | `codex/phase-61f-commercial-operation-asset-requests` | #46 | Merged to main | `commercial_operation_asset_requests`, asset-request create/list/update/ready/approve/reject/prepare/fail/archive APIs, Admin Dashboard Asset requests panel, and plan-step asset request state written back to `plan_outline` without ComfyUI, publishing, OpenClaw, browser worker, or account execution. |
| 61G | Commercial Operation Deliverables | `codex/phase-61g-commercial-operation-deliverables` | #47 | Merged to main | `commercial_operation_deliverables`, deliverable create/list/update/ready/approve/reject/package/fail/archive APIs, linked Output Library artifacts with `source_type=commercial_operation`, Admin Dashboard Deliverables panel, and plan-step deliverable state written back to `plan_outline` without publishing, ComfyUI, OpenClaw, browser worker, or account execution. |
| 61H | Commercial Operation Execution Requests | `codex/phase-61h-commercial-operation-execution-requests` | #48 | Merged to main | `commercial_operation_execution_requests`, execution-request create/list/update/ready/approve/reject/prepare/fail/cancel/archive APIs, Admin Dashboard Execution requests panel, and plan-step execution request state written back to `plan_outline` without publishing, ComfyUI, OpenClaw, browser worker, or account execution. |
| 61I | Commercial Operation Execution Runs | `codex/phase-61i-commercial-operation-execution-runs` | #49 | Merged to main | `commercial_operation_execution_runs`, execution-run create/list/update/start/succeed/fail/retry/cancel/archive APIs, Admin Dashboard Execution runs panel, and plan-step execution run state written back to `plan_outline` without publishing, ComfyUI, OpenClaw, browser worker, or account execution. |
| 61J | Commercial Operation Results | `codex/phase-61j-commercial-operation-results` | #50 | Merged to main | `commercial_operation_results`, result create/list/update/ready/approve/reject/archive APIs, Admin Dashboard Results panel, and plan-step result state written back to `plan_outline` without platform analytics ingestion, ROI attribution, publishing, ComfyUI, OpenClaw, browser worker, or account execution. |
| 61K | Commercial Operation Monitoring Observations | `codex/phase-61k-commercial-monitoring-observations` | #51 | Merged to main | `commercial_operation_monitoring_observations`, monitoring observation create/list/update/ready/approve/reject/archive APIs, Admin Dashboard Monitoring observations panel, and plan-step monitoring state written back to `plan_outline` without platform analytics ingestion, ROI attribution, publishing, ComfyUI, OpenClaw, browser worker, or account execution. |
| 61L | Commercial Operation Optimization Decisions | `codex/phase-61l-commercial-optimization-decisions` | #52 | Merged to main | `commercial_operation_optimization_decisions`, optimization decision create/list/update/ready/approve/reject/archive APIs, Admin Dashboard Optimization decisions panel, and plan-step optimization decision state written back to `plan_outline` without automatic optimization, platform analytics ingestion, ROI attribution, publishing, ComfyUI, OpenClaw, browser worker, or account execution. |
| 61M | Commercial Operation Evidence Snapshots | `codex/phase-61m-commercial-evidence-snapshots` | #53 | Merged to main | `commercial_operation_evidence_snapshots`, evidence-snapshot create/list/update/ready/approve/reject/archive APIs, execution request/run evidence snapshot IDs and operator checklists, Admin Dashboard Evidence snapshots panel, and plan-step evidence state written back to `plan_outline` without live RAG retrieval, knowledge ingestion, publishing, ComfyUI, OpenClaw, browser worker, or account execution. |
| 61N | Commercial Operation RAG Evidence Generation | `codex/phase-61n-commercial-rag-evidence-generation` | #54 | Merged to main | `/api/v1/commercial-operations/{operation_id}/evidence-snapshots/generate-rag`, Admin Dashboard RAG generation action, retrieved chunk evidence items, source document IDs, query/search metadata, and draft-only evidence snapshots from existing RAG search without knowledge ingestion, approval bypass, publishing, ComfyUI, OpenClaw, browser worker, or account execution. |
| 61O | Commercial Operation RAG Content Draft Generation | `codex/phase-61o-commercial-rag-content-drafts` | #55 | Merged to main | `/api/v1/commercial-operations/{operation_id}/content-drafts/generate-rag`, Admin Dashboard RAG content draft action, retrieved chunk source materials, query/search metadata, and draft-only content records from existing RAG search without knowledge ingestion, approval bypass, publishing, ComfyUI, OpenClaw, browser worker, or account execution. |
| 61P | Commercial Operation RAG Asset Brief Generation | `codex/phase-61p-commercial-rag-asset-briefs` | #56 | Merged to main | `/api/v1/commercial-operations/{operation_id}/asset-requests/generate-rag`, Admin Dashboard RAG asset request action, retrieved chunk source materials, query/search metadata, readiness checks, and draft-only asset request records from existing RAG search without knowledge ingestion, approval bypass, publishing, ComfyUI, OpenClaw, browser worker, or account execution. |
| 61Q | Commercial Operation ComfyUI Handoffs | `codex/phase-61q-commercial-comfyui-handoffs` | #57 | Draft PR | `commercial_operation_comfyui_handoffs`, `/api/v1/commercial-operations/{operation_id}/comfyui-handoffs`, Admin Dashboard ComfyUI handoffs panel, metadata-only prompt/workflow payloads, readiness checks, lifecycle decisions, and plan-step handoff state without submitting ComfyUI jobs, generating media, publishing, OpenClaw, browser worker, or account execution. |
| 61R | Commercial Operation ComfyUI Preflights | `codex/phase-61r-commercial-comfyui-preflight` | #58 | Draft PR | `commercial_operation_comfyui_preflights`, `/api/v1/commercial-operations/{operation_id}/comfyui-preflights`, Admin Dashboard ComfyUI preflight panel, endpoint/queue/model/workflow readiness checks, adapter config normalization, and plan-step preflight state without calling ComfyUI, submitting queues, generating media, publishing, OpenClaw, browser worker, or account execution. |
| 61S | Commercial Operation ComfyUI Adapter Configs | `codex/phase-61s-commercial-comfyui-adapter-configs` | #59 | Draft PR | `commercial_operation_comfyui_adapter_configs`, `/api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs`, Admin Dashboard ComfyUI adapter config panel, endpoint/queue/workflow allowlist/model inventory/runtime-limit/secret-reference validation, optional preflight config selection, and plan-step adapter config state without calling ComfyUI, submitting queues, storing secret values, generating media, publishing, OpenClaw, browser worker, or account execution. |
| 61T | Commercial Operation ComfyUI Job Requests | `codex/phase-61t-commercial-comfyui-job-requests` | #60 | Draft PR | `commercial_operation_comfyui_job_requests`, `/api/v1/commercial-operations/{operation_id}/comfyui-job-requests`, Admin Dashboard ComfyUI job request panel, checked-preflight-to-job-request review lifecycle, safety checks, output expectations, recovery guidance, and plan-step job request state without calling ComfyUI, submitting queues, uploading files, generating media, publishing, OpenClaw, browser worker, or account execution. |
| 61U | Commercial Operation ComfyUI Execution Plans | `codex/phase-61u-commercial-comfyui-execution-plans` | #61 | Draft PR | `commercial_operation_comfyui_execution_plans`, `/api/v1/commercial-operations/{operation_id}/comfyui-execution-plans`, Admin Dashboard ComfyUI execution plan panel, approved/queued-job-request-to-execution-plan lifecycle, queue simulation payload normalization, operator checklist, rollback guidance, and plan-step execution plan state without calling ComfyUI, submitting queues, uploading files, generating media, publishing, OpenClaw, browser worker, or account execution. |
| 61V | Commercial Operation ComfyUI Connection Probes | `codex/phase-61v-commercial-comfyui-connection-probes` | #62 | Draft PR | `commercial_operation_comfyui_connection_probes`, `/api/v1/commercial-operations/{operation_id}/comfyui-connection-probes`, Admin Dashboard ComfyUI connection probe panel, approved/simulated-execution-plan-to-probe lifecycle, metadata-only health and queue snapshot plans, sanitized route/readiness checks, and plan-step connection probe state without calling ComfyUI, reading queues, submitting queues, uploading files, generating media, publishing, OpenClaw, browser worker, or account execution. |
| 61W | Commercial Operation ComfyUI Adapter Dispatches | `codex/phase-61w-commercial-comfyui-adapter-dispatches` | #63 | Draft PR | `commercial_operation_comfyui_adapter_dispatches`, `/api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches`, Admin Dashboard ComfyUI adapter dispatch panel, probed-connection-to-dispatch lifecycle, sanitized prompt/workflow/queue/dispatch payloads, guardrails, retry policy, recovery plan, and plan-step adapter dispatch state without calling ComfyUI, reading queues, submitting queues, uploading files, generating media, publishing, OpenClaw, browser worker, or account execution. |
| 61X | Commercial Operation ComfyUI Runtime Gates | `codex/phase-61x-commercial-comfyui-runtime-gates` | #64 | Draft PR | `commercial_operation_comfyui_runtime_gates`, `/api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates`, Admin Dashboard ComfyUI runtime gate panel, dispatched-adapter-to-runtime-gate lifecycle, metadata-only runtime switch, network/queue/secret/approval policies, validation checks, rollback guidance, and plan-step runtime gate state without calling ComfyUI, reading queues, submitting prompts or queues, uploading files, generating media, publishing, OpenClaw, browser worker, or account execution. |
| 61Y | Commercial Operation ComfyUI Runtime Dry-Runs | `codex/phase-61y-commercial-comfyui-runtime-dry-runs` | #65 | Draft PR | `commercial_operation_comfyui_runtime_dry_runs`, `/api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs`, Admin Dashboard ComfyUI runtime dry-run panel, armed-gate-to-runtime-dry-run lifecycle, metadata-only adapter contract, request fixture, expected response contract, explicit server switch policy, validation checks, rollback guidance, and plan-step runtime dry-run state without importing or calling a ComfyUI adapter, calling ComfyUI, reading queues, submitting prompts or queues, uploading files, generating media, enabling runtime switches, publishing, OpenClaw, browser worker, or account execution. |
| 61Z | Commercial Operation ComfyUI Runtime Activations | `codex/phase-61z-commercial-comfyui-runtime-activations` | #66 | Draft PR | `commercial_operation_comfyui_runtime_activations`, `/api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations`, dedicated Admin Dashboard ComfyUI tab/runtime activation controls, validated-dry-run-to-runtime-activation lifecycle, metadata-only activation request, switch audit, runtime guardrails, validation checks, rollback guidance, and plan-step runtime activation state without importing or calling a ComfyUI adapter, calling ComfyUI, reading queues, submitting prompts or queues, uploading files, generating media, enabling runtime switches, publishing, OpenClaw, browser worker, or account execution. |
| 62A | ComfyUI Runtime Adapter Contract | `codex/phase-62a-comfyui-runtime-adapter-contract` | #67 | Draft PR | `/api/v1/comfyui-runtime/health`, `/api/v1/comfyui-runtime/capabilities`, `ComfyUIRuntimeService`, `COMFYUI_RUNTIME_*` settings, Docker env exposure, dedicated Admin Dashboard ComfyUI tab runtime adapter contract panel, provider/switch/base URL/allowlist/guardrail visibility, and disabled-by-default contract checks without importing or calling adapters, calling ComfyUI, reading queues, submitting prompts or queues, uploading files, generating media, enabling runtime switches, mutating config, resolving secrets, publishing, OpenClaw, browser worker, or account execution. |
| 62B | ComfyUI Guarded Read-Only Probe | `codex/phase-62b-comfyui-guarded-readonly-probe` | #68 | Draft PR | `COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED`, `COMFYUI_RUNTIME_HEALTH_PATH`, `COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS`, guarded `GET /system_stats` only after provider/enabled/network/host/path gates are all true, response status/latency visibility, and Admin Dashboard ComfyUI tab probe fields without importing or calling adapters, submitting prompts, reading/submitting queues, uploading files, generating media, enabling runtime switches, mutating config, resolving secrets, publishing, OpenClaw, browser worker, or account execution. |
| 62C | ComfyUI Runtime Diagnostics | `codex/phase-62c-comfyui-runtime-diagnostics` | #69 | Draft PR | `/api/v1/comfyui-runtime/diagnostics`, no-network readiness report, `readiness_status`, `blocking_reasons`, `recommended_actions`, `read_only_probe_ready`, and per-gate diagnostic checks for provider/switch/network/host/path readiness without importing/calling adapters, submitting prompts, reading/submitting queues, uploading files, generating media, enabling switches, mutating config, resolving secrets, publishing, OpenClaw, browser worker, or account execution. |
| 62D | ComfyUI Runtime Diagnostic Snapshots | `codex/phase-62d-comfyui-runtime-diagnostic-snapshots` | #70 | Draft PR | `comfyui_runtime_diagnostic_snapshots`, `POST /api/v1/comfyui-runtime/diagnostic-snapshots`, `GET /api/v1/comfyui-runtime/diagnostic-snapshots`, operator notes, snapshot metadata, recent snapshot fields, and Admin Dashboard ComfyUI page save action without importing/calling adapters, submitting prompts, reading/submitting queues, uploading files, generating media, enabling switches, mutating config, resolving secrets, publishing, OpenClaw, browser worker, or account execution. |
| 62E | ComfyUI Runtime Maintenance Runbook | `codex/phase-62e-comfyui-maintenance-console` | #71 | Draft PR | `GET /api/v1/comfyui-runtime/maintenance-runbook`, no-network ordered maintainer steps, `next_operator_action`, `recovery_actions`, `configuration_summary`, `snapshot_recommended`, disabled-action visibility, and Admin Dashboard ComfyUI page runbook table without importing/calling adapters, submitting prompts, reading/submitting queues, uploading files, generating media, enabling switches, mutating config, resolving secrets, publishing, OpenClaw, browser worker, or account execution. |
| 62F | ComfyUI Runtime Configuration Change Requests | `codex/phase-62f-comfyui-config-change-requests` | #72 | Draft PR | `comfyui_runtime_config_change_requests`, `ComfyUIRuntimeConfigChangeRequest`, `POST /api/v1/comfyui-runtime/config-change-requests`, `GET /api/v1/comfyui-runtime/config-change-requests`, ready/approve/reject/cancel/archive review actions, `change_status`, `requested_changes`, and `config_mutation_performed=false` audit records derived from the maintenance runbook without writing environment variables, enabling switches, importing/calling adapters, submitting prompts, reading/submitting queues, uploading files, generating media, resolving secrets, publishing, OpenClaw, browser worker, or account execution. |
| 62G | ComfyUI Runtime Manual Apply Evidence | `codex/phase-62g-comfyui-manual-apply-evidence` | #73 | Draft PR | `comfyui_runtime_manual_apply_evidence`, `ComfyUIRuntimeManualApplyEvidence`, `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/manual-apply-evidence`, `GET /api/v1/comfyui-runtime/manual-apply-evidence`, ready/verify/reject/fail/archive review actions, restart evidence, rollback notes, verification notes, `manual_config_applied`, `service_restart_reported`, and `api_config_mutation_performed=false` audit records derived from approved config change requests without writing environment variables, restarting services, enabling switches, importing/calling adapters, submitting prompts, reading/submitting queues, uploading files, generating media, resolving secrets, publishing, OpenClaw, browser worker, or account execution. |
| 62H | ComfyUI Runtime Post-Manual Readiness Checks | `codex/phase-62h-comfyui-post-manual-readiness` | #74 | Draft PR | `comfyui_runtime_post_manual_readiness_checks`, `ComfyUIRuntimePostManualReadinessCheck`, `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/post-manual-readiness-checks`, `GET /api/v1/comfyui-runtime/post-manual-readiness-checks`, ready/approve/reject/fail/archive review actions, readiness before/after/current comparison, `comparison_status`, `guarded_probe_ready`, `health_probe_executed=false`, and `api_config_mutation_performed=false` records derived from verified manual apply evidence without running `/system_stats`, writing environment variables, restarting services, enabling switches, importing/calling adapters, submitting prompts, reading/submitting queues, uploading files, generating media, resolving secrets, publishing, OpenClaw, browser worker, or account execution. |
| 62I | Workstation/Customer Client Frontend UX Alignment | `codex/phase-62i-workstation-client-ux` | In progress | Stacked after PR #74 | Simplify and align `worker_console` and `worker_console_desktop` for customer-machine/workstation operators: operator home, local worker connection state, runtime/heartbeat controls, conversation/playbook/task/output shortcuts, approval queue visibility, recovery guidance, setup/help panels, Chinese/English language switching, and server/client boundary warnings without adding ComfyUI calls, OpenClaw execution, publishing, account control, installer signing, auto-update, captcha bypass, proxy pools, or fingerprint bypass. |

## Runtime Evolution

The runtime evolved from a FastAPI service with PostgreSQL, Redis, Qdrant, local LLM/embedding providers, and Agentic RAG into a browser/worker-enabled automation runtime. Phase 33 added Conversation Runtime, Phase 34 promoted browser execution to remote worker runtime, and Phase 42 added background task orchestration.

## Workflow Evolution

Workflow capability begins with plans and playbooks, then moves into approvals, background tasks, persistent workflow state, graph execution, templates, governance, and observability. Phases 43-49 are accepted on `main`.

## Artifact Evolution

Artifacts begin as playbook/conversation outputs in Phase 41, become lineage-aware export/package entities in Phase 44, and later connect to workflow state, templates, governance, replay, and diagnostics.

## Deployment Evolution

Deployment starts with Docker-based local/server operation, adds worker client packaging and desktop readiness, then gains release metadata in Phase 51 and deployment profiles in Phase 52. The current system is not Kubernetes, Helm, Terraform, Ansible, or production HA deployment automation.

## Governance Evolution

Governance starts with conversation approval gates and risk policy in Phase 39, then extends to playbook/template approval, template reviews, audit logs, compatibility matrices, and internal marketplace labels in Phases 47-48.

## Desktop Runtime Evolution

The desktop track moves from Web GUI to Tauri shell, tray controls, runtime UX diagnostics, icon resource readiness, and packaging readiness. It is still not a signed installer, not an auto-updater, and not a production desktop distribution.

## Mainline Integration Evolution

Phase 54 adds the integration reconciliation layer. Phase 55 adds the mainline Release Candidate preparation layer, including the RC branch model, mainline readiness runner, merge simulation, superseded PR decision report, and rollback plan.
