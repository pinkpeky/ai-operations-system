# AI Operations System - Phase Index

## Current Stable Baseline

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate. It includes the Phase 42 runtime foundation plus the accepted Phase 43-55 scheduler, artifact, workflow, template, observability, packaging, deployment, smoke, integration, and readiness layers.

PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after post-merge verification. PR #16 was accepted into the Phase 54 branch, and PR #17 merged the combined Phase 43-55 RC into `main`.

## Current Active Development Branch

`main` is the active accepted baseline branch after Phase 56A-56D readiness closures, Phase 57A-59C Run Cockpit product slices, and Phase 60A-60C frontend simplification slices.

Current effective phase: Phase 60 RAG Documents & Simplicity Foundation. Phase 56 was reverted and is not active. The old reverted Phase 56 branch is not active, not part of the accepted baseline, and should not be reused.

The current fresh branch is `codex/phase-60-rag-documents-simplification`. This makes the RAG / Documents page easier for workstation users and server maintainers to use with Chinese-first health, collection, document indexing, and hybrid retrieval status.

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
| 60D | RAG Documents & Simplicity Foundation | `codex/phase-60-rag-documents-simplification` | TBD | In progress | RAG / Documents knowledge console, localized health/collection/document/search labels, operator summary cards, and clearer hybrid retrieval feedback. |

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
