# Current Development State

## Current Active Branch

`codex/phase-62j-comfyui-guarded-probe-executions`

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate and after the post-merge stabilization branch landed. PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after verification. Phase 56 was reverted and is not active. Phase 56A-56D readiness work has also landed on `main`, adding CI gates, required-check documentation, release readiness artifacts, and scheduled server Docker smoke. Phase 57A-57D, Phase 58A-58E, Phase 59A-59C, Phase 60A-60G, and Phase 61A-61P have landed on `main`, adding the Admin Dashboard Run Cockpit, guarded cockpit actions, operator controls, deep links, refresh UX, Playbooks context, Output Library context handoff, Phase 58 closeout, Run Cockpit search density, workflow handoff into Workflows and Replay Center, workflow focus/provenance, the frontend language foundation, the Overview role entry, the Conversations operator console, the RAG Documents knowledge console, RAG knowledge maintenance controls, Replay Center workflow observability simplification, RAG live validation guidance, the Commercial Ops project center, commercial operation evidence/handoff links, commercial operation approval gates, commercial operation safe dry-runs, commercial operation content drafts, commercial operation asset requests, commercial operation deliverables, commercial operation execution requests, commercial operation execution runs, commercial operation results, commercial operation monitoring observations, commercial operation optimization decisions, commercial operation evidence snapshots, commercial operation RAG evidence generation, commercial operation RAG content draft generation, and commercial operation RAG asset brief generation.

Current effective phase: Phase 62J ComfyUI Runtime Guarded Probe Execution Audit. The old reverted Phase 56 branch remains inactive and is not a valid continuation point.

## Current Recommended Next Phase

Readiness and PR cleanup are complete. PR #57 is the draft Phase 61Q commercial ComfyUI handoff slice, PR #58 is the draft Phase 61R ComfyUI preflight slice, PR #59 is the draft Phase 61S ComfyUI adapter config slice, PR #60 is the draft Phase 61T ComfyUI job request slice, PR #61 is the draft Phase 61U ComfyUI execution plan slice, PR #62 is the draft Phase 61V ComfyUI connection probe slice, PR #63 is the draft Phase 61W ComfyUI adapter dispatch slice, PR #64 is the draft Phase 61X ComfyUI runtime gate slice, PR #65 is the draft Phase 61Y ComfyUI runtime dry-run slice, PR #66 is the draft Phase 61Z ComfyUI runtime activation slice, PR #67 is the draft Phase 62A ComfyUI runtime adapter contract slice, PR #68 is the draft Phase 62B guarded read-only probe slice, PR #69 is the draft Phase 62C runtime diagnostics slice, PR #70 is the draft Phase 62D diagnostic snapshots slice, PR #71 is the draft Phase 62E maintenance runbook slice, PR #72 is the draft Phase 62F configuration change request slice, PR #73 is the draft Phase 62G manual apply evidence slice, PR #74 is the draft Phase 62H post-manual readiness slice, PR #75 is the draft Phase 62I workstation/customer client frontend UX slice, and Phase 62J is being prepared on `codex/phase-62j-comfyui-guarded-probe-executions`. The current step is to add a separately approved, auditable guarded read-only probe execution record after readiness checks explicitly show `guarded_probe_ready=true`.

Post-merge stabilization tracking lives in `docs/POST_MERGE_STABILIZATION.md`. That document records the migrated server toolchain state, Docker/WSL repair status, stabilization branch/remote discipline, browser runtime screenshot fix, PR #1 disposition, and verification gates.

The next active branch is `codex/phase-62j-comfyui-guarded-probe-executions`. Its scope is Phase 62J ComfyUI Runtime Guarded Probe Execution Audit: it adds `comfyui_runtime_guarded_probe_executions`, service methods, API routes, Admin Dashboard ComfyUI tab controls, and tests for creating, reviewing, approving, executing, failing, cancelling, and archiving a guarded read-only `/system_stats` probe record. Creation and review remain no-network, and the Admin Dashboard ComfyUI page now auto-loads diagnostics instead of calling `/health`, so page refresh does not run a probe. Only `POST /api/v1/comfyui-runtime/guarded-probe-executions/{execution_id}/execute` may call the existing guarded health path, and only after Phase 62H readiness is approved and current diagnostics still show `read_only_probe_ready=true`. It still does not import ComfyUI adapters, submit prompts, read or submit queues, upload files, generate media, enable runtime switches, write environment variables, restart services, mutate runtime configuration, resolve secrets, publish, run OpenClaw, control accounts, or bypass approval. CI readiness tracking lives in `docs/CI_READINESS_GATES.md`; branch protection guidance lives in `docs/BRANCH_PROTECTION.md`; scheduled smoke guidance lives in `docs/SCHEDULED_SMOKE.md`; run cockpit guidance lives in `docs/RUN_COCKPIT_FOUNDATION.md`.

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
| #75 | Phase 62I Workstation/Customer Client Frontend UX Alignment | `codex/phase-62i-workstation-client-ux` | Draft PR |
| TBD | Phase 62J ComfyUI Runtime Guarded Probe Execution Audit | `codex/phase-62j-comfyui-guarded-probe-executions` | In progress |

PR #57 is open as a draft from `codex/phase-61q-commercial-comfyui-handoffs`; PR #58 is open as a draft from `codex/phase-61r-commercial-comfyui-preflight`; PR #59 is open as a draft from `codex/phase-61s-commercial-comfyui-adapter-configs`; PR #60 is open as a draft from `codex/phase-61t-commercial-comfyui-job-requests`; PR #61 is open as a draft from `codex/phase-61u-commercial-comfyui-execution-plans`; PR #62 is open as a draft from `codex/phase-61v-commercial-comfyui-connection-probes`; PR #63 is open as a draft from `codex/phase-61w-commercial-comfyui-adapter-dispatches`; PR #64 is open as a draft from `codex/phase-61x-commercial-comfyui-runtime-gates`; PR #65 is open as a draft from `codex/phase-61y-commercial-comfyui-runtime-dry-runs`; PR #66 is open as a draft from `codex/phase-61z-commercial-comfyui-runtime-activations`; PR #67 is open as a draft from `codex/phase-62a-comfyui-runtime-adapter-contract`; PR #68 is open as a draft from `codex/phase-62b-comfyui-guarded-readonly-probe`; PR #69 is open as a draft from `codex/phase-62c-comfyui-runtime-diagnostics`; PR #70 is open as a draft from `codex/phase-62d-comfyui-runtime-diagnostic-snapshots`; PR #71 is open as a draft from `codex/phase-62e-comfyui-maintenance-console`; PR #72 is open as a draft from `codex/phase-62f-comfyui-config-change-requests`; PR #73 is open as a draft from `codex/phase-62g-comfyui-manual-apply-evidence`; PR #74 is open as a draft from `codex/phase-62h-comfyui-post-manual-readiness`; PR #75 is open as a draft from `codex/phase-62i-workstation-client-ux`; Phase 62J is in progress on `codex/phase-62j-comfyui-guarded-probe-executions`.

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
- Phase 61R adds ComfyUI preflight records so approved/prepared handoffs can carry endpoint, queue, model, workflow, adapter config, and local readiness checks toward a future guarded adapter before any ComfyUI API call, queue submission, media generation, publishing, or account control exists.
- Phase 61S adds ComfyUI adapter config records so server maintainers can carry endpoint, queue, workflow allowlist, model inventory, runtime limits, maintenance notes, and secret references toward a future guarded adapter before any ComfyUI API call, queue submission, secret value storage, media generation, publishing, or account control exists.
- Phase 61T adds ComfyUI job request records so checked preflights can become reviewable future queue payloads with safety checks, output expectations, lifecycle decisions, and recovery guidance before any ComfyUI API call, queue submission, file upload, media generation, publishing, or account control exists.
- Phase 61U adds ComfyUI execution plan records so approved or queued job requests can become reviewable metadata-only queue simulation plans with execution steps, local checks, operator checklists, rollback guidance, lifecycle decisions, and plan-step execution-plan state before any ComfyUI API call, queue submission, file upload, media generation, publishing, or account control exists.
- Phase 61V adds ComfyUI connection probe records so approved or simulated execution plans can become reviewable metadata-only health and queue snapshot plans with route normalization, readiness checks, lifecycle decisions, and plan-step connection-probe state before any ComfyUI HTTP request, queue read, queue submission, file upload, media generation, publishing, or account control exists.
- Phase 61W adds ComfyUI adapter dispatch records so recorded connection probes can become reviewable metadata-only dispatch handoffs with prompt/workflow/queue payloads, guardrails, retry policy, recovery plan, lifecycle decisions, and plan-step dispatch state before any ComfyUI adapter call, prompt submission, queue submission, file upload, media generation, publishing, or account control exists.
- Phase 61X adds ComfyUI runtime gate records so recorded adapter dispatches can become reviewable metadata-only runtime switch, network boundary, queue policy, secret-reference, approval, and rollback records with lifecycle decisions and plan-step runtime-gate state before any ComfyUI runtime adapter, HTTP request, queue read, queue submission, file upload, media generation, publishing, or account control exists.
- Phase 61Y adds ComfyUI runtime dry-run records so armed runtime gates can become reviewable metadata-only adapter contract, request fixture, expected response, server switch policy, validation, and rollback records with lifecycle decisions and plan-step runtime-dry-run state before any ComfyUI adapter import, HTTP request, queue read, queue submission, file upload, media generation, runtime switch enablement, publishing, or account control exists.
- Phase 61Z adds ComfyUI runtime activation request records so validated runtime dry-runs can become reviewable metadata-only activation, switch audit, runtime guardrail, validation, operator checklist, and rollback records with lifecycle decisions and plan-step runtime-activation state before any adapter import/call, HTTP request, queue read/submission, file upload, media generation, runtime switch enablement, publishing, or account control exists.
- Phase 62A adds a disabled-by-default ComfyUI runtime adapter contract with `/api/v1/comfyui-runtime/health`, `/api/v1/comfyui-runtime/capabilities`, `ComfyUIRuntimeService`, `COMFYUI_RUNTIME_*` settings, Docker env exposure, and dedicated Admin Dashboard ComfyUI tab contract visibility before any adapter import/call, HTTP request, queue read/submission, file upload, media generation, runtime switch enablement, config mutation, secret resolution, publishing, or account control exists.
- Phase 62B adds a guarded read-only ComfyUI health probe with `COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED`, `COMFYUI_RUNTIME_HEALTH_PATH`, `COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS`, host/path allowlist enforcement, `GET /system_stats` only when every explicit gate is enabled, and Admin Dashboard probe status visibility without adapter import/call, prompt submission, queue reads/submissions, uploads, media generation, runtime switch enablement, config mutation, secret resolution, publishing, or account control.
- Phase 62C adds no-network ComfyUI runtime diagnostics with `/api/v1/comfyui-runtime/diagnostics`, `readiness_status`, `blocking_reasons`, `recommended_actions`, `read_only_probe_ready`, and per-gate diagnostic checks so server maintainers can see exactly which provider/switch/network/host/path gate blocks readiness without calling ComfyUI.
- Phase 62D adds persisted no-network ComfyUI runtime diagnostic snapshots with `comfyui_runtime_diagnostic_snapshots`, `POST /api/v1/comfyui-runtime/diagnostic-snapshots`, `GET /api/v1/comfyui-runtime/diagnostic-snapshots`, operator notes, snapshot metadata, recent snapshot visibility, and an Admin Dashboard ComfyUI page save action so server maintainers can retain before/after diagnostics without calling ComfyUI.
- Phase 62E adds a no-network ComfyUI runtime maintenance runbook with `GET /api/v1/comfyui-runtime/maintenance-runbook`, ordered operator steps, `next_operator_action`, `recovery_actions`, `configuration_summary`, `snapshot_recommended`, disabled-action visibility, and Admin Dashboard ComfyUI page runbook visibility so workstation operators and server maintainers know the next safe action.
- Phase 62F adds metadata-only ComfyUI runtime configuration change requests with `comfyui_runtime_config_change_requests`, `POST /api/v1/comfyui-runtime/config-change-requests`, `GET /api/v1/comfyui-runtime/config-change-requests`, ready/approve/reject/cancel/archive review actions, requested changes derived from the maintenance runbook, and Admin Dashboard ComfyUI page create/list controls without writing environment variables or enabling ComfyUI.
- Phase 62G adds metadata-only ComfyUI runtime manual apply evidence with `comfyui_runtime_manual_apply_evidence`, `ComfyUIRuntimeManualApplyEvidence`, `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/manual-apply-evidence`, `GET /api/v1/comfyui-runtime/manual-apply-evidence`, ready/verify/reject/fail/archive review actions, restart evidence, rollback notes, and `api_config_mutation_performed=false` records without writing environment variables, restarting services, enabling ComfyUI, or calling ComfyUI.
- Phase 62H adds metadata-only ComfyUI runtime post-manual readiness checks with `comfyui_runtime_post_manual_readiness_checks`, `ComfyUIRuntimePostManualReadinessCheck`, `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/post-manual-readiness-checks`, `GET /api/v1/comfyui-runtime/post-manual-readiness-checks`, ready/approve/reject/fail/archive review actions, `comparison_status`, `guarded_probe_ready`, `health_probe_executed=false`, and `api_config_mutation_performed=false` records without calling `/system_stats`, writing environment variables, restarting services, enabling ComfyUI, or calling ComfyUI.
- Phase 62I aligns the customer-machine frontends before live probe escalation: `worker_console` and `worker_console_desktop` get a simplified workstation operator home, clearer status cards, runtime/heartbeat controls, conversation/playbook/task/output shortcuts, approvals and recovery guidance, setup/help copy, Chinese/English language switching, and server-vs-client boundary messaging. It remains a UX/readiness slice and does not add real ComfyUI calls, OpenClaw execution, publishing, account control, installer signing, auto-update, captcha bypass, proxy pools, or fingerprint bypass.
- Phase 62J adds auditable guarded read-only probe execution records with `comfyui_runtime_guarded_probe_executions`, `ComfyUIRuntimeGuardedProbeExecution`, `POST /api/v1/comfyui-runtime/post-manual-readiness-checks/{check_id}/guarded-probe-executions`, `GET /api/v1/comfyui-runtime/guarded-probe-executions`, ready/approve/reject/fail/cancel/archive review actions, `probe_result_status`, `external_request_attempted`, and a separate `POST /api/v1/comfyui-runtime/guarded-probe-executions/{execution_id}/execute` endpoint. Create/review/list paths remain no-network; execute can call only the existing guarded `GET /system_stats` health probe after explicit approval and current diagnostics readiness.

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

1. Review and keep PR #75 / Phase 62I Workstation/Customer Client Frontend UX Alignment aligned above PR #74, including Web Worker Console and Tauri Desktop Console verification.
2. Review Phase 62J guarded probe execution records above PR #75 and verify only the explicit execute endpoint can trigger the existing guarded `/system_stats` health call.
3. Add monitored analytics/result feedback adapters only after the probe execution audit trail is reviewable and failure recovery is visible to server maintainers.
4. Keep Docker compose running only while manual inspection is useful; otherwise shut it down cleanly with `docker compose -f docker-compose.yml down`.
5. Continue toward guarded ComfyUI/OpenClaw adapters, richer knowledge upload ergonomics, monitoring metrics, failure recovery, and commercial result reporting after the probe audit loop is reviewable.
