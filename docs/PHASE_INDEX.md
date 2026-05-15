# AI Operations System - Phase Index

## Current Stable Baseline

`main` remains the Phase 42 stable baseline. It includes the runtime, browser worker, worker console, admin dashboard, conversation runtime, approval flow, playbooks, output artifacts, and task orchestration foundation that were squash-merged through PR #2.

`main` remains the Phase 42 stable baseline. PR #3-#12 cover Phase 43-52 and remain open. PR #13 is the Docs Stabilization Sprint. This documentation branch records the complete Phase 1-52 development state, but that does not mean all phases are merged into `main`.

## Current Active Development Branch

`codex/phase-54-integration-branch-pr-chain-reconciliation` is the active integration stabilization branch. It is based on `codex/phase-53-release-smoke-test-matrix-preflight`, not on `main`.

## Open PR List

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
| #15 | Phase 54 Integration Branch and PR Chain Reconciliation | `codex/phase-54-integration-branch-pr-chain-reconciliation` | Planned/Open after push |

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
| 43 | Task Scheduler Persistence & Worker Recovery | `codex/phase-43-task-scheduler-recovery` | #3 | Open PR | Task lease, scheduler state, recovery service, diagnostics. |
| 44 | Output Artifact Pipeline & Export System | `codex/phase-44-output-artifact-pipeline` | #4 | Open PR | Artifact lineage, relationship graph, export/package/retention services. |
| 45 | Workflow State & Agent Memory Foundation | `codex/phase-45-workflow-state-memory` | #5 | Open PR | Workflow runs, steps, checkpoints, agent memory snapshots. |
| 46 | Workflow Graph Runtime & Conditional Execution | `codex/phase-46-workflow-graph-runtime` | #6 | Open PR | Workflow graphs, planner, conditional routing, retry/fallback, replay foundation. |
| 47 | Workflow Template Registry & Versioning | `codex/phase-47-workflow-template-registry` | #7 | Open PR | Workflow templates, versions, built-in templates, import/export. |
| 48 | Workflow Template Marketplace & Governance Foundation | `codex/phase-48-template-marketplace-governance` | #8 | Open PR | Reviews, lifecycle, rollback, compatibility matrix, internal marketplace. |
| 49 | Workflow Run Observability & Replay Center | `codex/phase-49-workflow-observability-replay` | #9 | Open PR | Execution traces, diagnostics, replay sessions, runtime analytics. |
| 50 | Desktop Console Runtime UX & Client Packaging Readiness | `codex/phase-50-desktop-runtime-ux-packaging-readiness` | #10 | Open PR | Tauri icon fix, Start Runtime diagnostics, server/client boundary UX. |
| 51 | Release Packaging & Deployment Bundle Foundation | `codex/phase-51-release-packaging-foundation` | #11 | Open PR | Release manifest, version metadata, bundle scripts, startup scripts. |
| 52 | Deployment Profiles & Environment Bootstrap | `codex/phase-52-deployment-profiles-bootstrap` | #12 | Open PR | Deployment profiles, env generator, dependency/port/env verification. |
| 53 | Release Smoke Test Matrix & Preflight Automation | `codex/phase-53-release-smoke-test-matrix-preflight` | #14 | Open PR | Unified preflight, smoke matrix, release report, migration continuity, runtime hygiene. |
| 54 | Integration Branch & PR Chain Reconciliation | `codex/phase-54-integration-branch-pr-chain-reconciliation` | #15 | Planned/Open after push | Integration strategy, PR inventory, dependency matrix, conflict detection, drift checks, integration report. |

## Runtime Evolution

The runtime evolved from a FastAPI service with PostgreSQL, Redis, Qdrant, local LLM/embedding providers, and Agentic RAG into a browser/worker-enabled automation runtime. Phase 33 added Conversation Runtime, Phase 34 promoted browser execution to remote worker runtime, and Phase 42 added background task orchestration.

## Workflow Evolution

Workflow capability begins with plans and playbooks, then moves into approvals, background tasks, persistent workflow state, graph execution, templates, governance, and observability. Phases 43-49 remain open PRs and should be merged only after review in dependency order.

## Artifact Evolution

Artifacts begin as playbook/conversation outputs in Phase 41, become lineage-aware export/package entities in Phase 44, and later connect to workflow state, templates, governance, replay, and diagnostics.

## Deployment Evolution

Deployment starts with Docker-based local/server operation, adds worker client packaging and desktop readiness, then gains release metadata in Phase 51 and deployment profiles in Phase 52. The current system is not Kubernetes, Helm, Terraform, Ansible, or production HA deployment automation.

## Governance Evolution

Governance starts with conversation approval gates and risk policy in Phase 39, then extends to playbook/template approval, template reviews, audit logs, compatibility matrices, and internal marketplace labels in Phases 47-48.

## Desktop Runtime Evolution

The desktop track moves from Web GUI to Tauri shell, tray controls, runtime UX diagnostics, icon resource readiness, and packaging readiness. It is still not a signed installer, not an auto-updater, and not a production desktop distribution.
