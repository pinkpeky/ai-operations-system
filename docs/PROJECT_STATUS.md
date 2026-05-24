# Project Status

## Branch Status

`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate and after post-merge stabilization landed. PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after verification. PR #16 was accepted into the Phase 54 branch before PR #17 merged to `main`. Phase 56 was reverted and is not active. Phase 56A-56D readiness work has landed on `main`, adding CI gates, required-check documentation, release readiness artifacts, and scheduled server Docker smoke. Phase 57A-57D, Phase 58A-58E, Phase 59A-59C, Phase 60A-60G, and Phase 61A-61P have also landed on `main`, adding the Admin Dashboard Run Cockpit, guarded cockpit actions, operator controls, deep links, refresh UX, Playbooks context, Output Library context handoff, Phase 58 closeout, Run Cockpit search density, workflow handoff, workflow focus/provenance, the frontend language foundation, the Overview role entry, the Conversations operator console, the RAG Documents knowledge console, RAG knowledge maintenance controls, Replay Center workflow observability simplification, RAG live validation guidance, the Commercial Ops project center, commercial operation evidence/handoff links, commercial operation approval gates, commercial operation safe dry-runs, commercial operation content drafts, commercial operation asset requests, commercial operation deliverables, commercial operation execution requests, commercial operation execution runs, commercial operation results, commercial operation monitoring observations, commercial operation optimization decisions, commercial operation evidence snapshots, commercial operation RAG evidence generation, commercial operation RAG content draft generation, and commercial operation RAG asset brief generation.

## Localized Status Docs

- English: `docs/en/PROJECT_STATUS.md`
- Chinese: `docs/zh/PROJECT_STATUS.md`

## Notes

Use `docs/PHASE_INDEX.md` as the complete phase index and `docs/CURRENT_NEXT_PHASE.md` as the next-conversation recovery state file.

## Active Next Slice

`codex/phase-63l-63n-execution-approval-loop` is the active next branch after draft PR #101 / Phase 63K Customer Console Guarded Adapter Dispatch Handoff and is now draft PR #102. It adds Phase 63L-63N Customer Console Execution and Approval Loop: `worker_console` and `worker_console_desktop` now add a guarded adapter dry-run action, a visual client execution queue, and a commercial approval center for specific operation approvals. This moves the repeatable closed loop from handoff readiness into a usable dry-run execution record and approval surface before future real adapter work. It does not execute live OpenClaw, run Playwright, publish to social media, control real accounts, call ComfyUI, ingest platform analytics, enable runtime switches, write environment variables, restart services, mutate runtime configuration, resolve secrets, bypass captcha, use proxy pools, bypass fingerprints, or bypass approval.

The active runtime surface includes `/api/v1/comfyui-runtime/health`, `/api/v1/comfyui-runtime/capabilities`, `/api/v1/comfyui-runtime/diagnostics`, `/api/v1/comfyui-runtime/maintenance-runbook`, `/api/v1/comfyui-runtime/config-change-requests`, `/api/v1/comfyui-runtime/manual-apply-evidence`, `/api/v1/comfyui-runtime/post-manual-readiness-checks`, `/api/v1/comfyui-runtime/guarded-probe-executions`, and `/api/v1/comfyui-runtime/diagnostic-snapshots`, with `api_config_mutation_performed=false`, `guarded_probe_ready`, `health_probe_executed`, `external_request_attempted`, and `probe_result_status` audit fields.

Phase 63K Customer Console Guarded Adapter Dispatch Handoff from `codex/phase-63k-guarded-adapter-dispatch-handoff` is the immediate UI/API predecessor, and Phase 63L-63N adds the guarded adapter dry-run, client execution queue, and commercial approval center on top of queued/retrying execution runs. Phase 63J Customer Console Client Runtime Preflight from `codex/phase-63j-client-runtime-preflight` remains the runtime readiness predecessor. Phase 63I Customer Console Next-Cycle Result Feedback Loop from `codex/phase-63i-next-cycle-result-feedback-loop` remains the result predecessor. Phase 63H Customer Console Next-Cycle Execution Run Review from `codex/phase-63h-next-cycle-execution-run-review` remains the next-cycle run predecessor. Phase 63G Customer Console Next-Cycle Execution Prep from `codex/phase-63g-next-cycle-execution-prep` remains the next-cycle execution prep predecessor. Phase 63F Customer Console Next-Cycle Content Drafts from `codex/phase-63f-next-cycle-content-drafts` remains the second-draft predecessor. Phase 63E Customer Console Result Feedback Loop from `codex/phase-63e-client-result-feedback-loop` remains the first result/observation/improvement predecessor. Phase 63D Customer Console Execution Run Review from `codex/phase-63d-client-execution-run-review` remains the first execution run predecessor. Phase 63C Customer Console Approval and Execution Prep from `codex/phase-63c-client-approval-execution-prep` remains the first execution prep predecessor. Phase 63B Customer Console First Draft Bootstrap from `codex/phase-63b-client-first-draft-bootstrap` remains the first draft predecessor. Phase 63A Customer Console Loop Protocol Binding from `codex/phase-63a-client-loop-protocol-binding` remains the operation-loop binding predecessor. Phase 62Y Commercial Operation Loop Protocol from `codex/phase-62y-operation-loop-protocol` remains the protocol predecessor. Phase 62X Customer Console Product Operation Desk from `codex/phase-62x-client-operation-desk` remains the earlier customer-console UX predecessor. Phase 62J remains the immediate runtime predecessor: the server-side ComfyUI guarded probe audit is approval-gated, while Phase 63L-63N keeps OpenClaw/Playwright and analytics as guarded dry-run and metadata-only customer-console records.

Phase 62I Workstation/Customer Client Frontend UX Alignment from `codex/phase-62i-workstation-client-ux` remains the earlier customer-console baseline for `worker_console` and `worker_console_desktop`, including Chinese/English language switching, local runtime/heartbeat visibility, and server-vs-customer-machine boundary guidance.

## Customer Console Phase Anchors

These anchors keep `worker_console` and `worker_console_desktop` progress searchable across status docs:

- Phase 62K Customer Console Codex-like UX Simplification on `codex/phase-62k-customer-console-codex-ux`.
- Phase 62L Customer Console Task Workbench on `codex/phase-62l-client-task-workbench`.
- Phase 62M Customer Console Goal Templates on `codex/phase-62m-client-goal-templates`.
- Phase 62N Customer Console Goal Plan Preview on `codex/phase-62n-client-goal-plan-preview`.
- Phase 62O Customer Console Goal Status Tracker on `codex/phase-62o-client-goal-status-tracker`.
- Phase 62P Customer Console Simple Operator Mode on `codex/phase-62p-client-simple-operator-mode`, including the knowledge base upload/edit page.
- Phase 62Q Customer Console Knowledge Upload Readiness on `codex/phase-62q-knowledge-upload-readiness`, including knowledge upload readiness.
- Phase 62R Customer Console Knowledge Activity Timeline on `codex/phase-62r-knowledge-activity-timeline`, including knowledge activity timeline.
- Phase 62S Customer Console Knowledge Document Details on `codex/phase-62s-knowledge-document-details`, including knowledge document details.
- Phase 62T Customer Console Knowledge Search Validation on `codex/phase-62t-knowledge-search-validation`, including knowledge search validation.
- Phase 62U Customer Console Knowledge Ingestion Status Loop on `codex/phase-62u-knowledge-ingestion-status`, including knowledge ingestion status loop.
- Phase 62V Customer Console Knowledge Validation Guidance on `codex/phase-62v-knowledge-validation-guidance`, including knowledge validation guidance.
- Phase 62W Customer Console Knowledge Validation Outcomes on `codex/phase-62w-knowledge-validation-outcomes`, including knowledge validation outcomes.
- Phase 62X Customer Console Product Operation Desk on `codex/phase-62x-client-operation-desk`, including the product operation desk.
- Phase 63A Customer Console Loop Protocol Binding on `codex/phase-63a-client-loop-protocol-binding`, including operation-loop binding.
- Phase 63B Customer Console First Draft Bootstrap on `codex/phase-63b-client-first-draft-bootstrap`, including first draft approval bootstrap.
- Phase 63C Customer Console Approval and Execution Prep on `codex/phase-63c-client-approval-execution-prep`, including approval and metadata-only execution prep.
- Phase 63D Customer Console Execution Run Review on `codex/phase-63d-client-execution-run-review`, including execution request review, metadata-only run creation, start/failure recording, and retry controls.
- Phase 63E Customer Console Result Feedback Loop on `codex/phase-63e-client-result-feedback-loop`, including the minimum usable closed loop through result, observation, and improvement decision records.
- Phase 63F Customer Console Next-Cycle Content Drafts on `codex/phase-63f-next-cycle-content-drafts`, including next-cycle content draft generation from an approved optimization decision and a new human approval gate.
- Phase 63G Customer Console Next-Cycle Execution Prep on `codex/phase-63g-next-cycle-execution-prep`, including next-cycle execution prep from a pending next-cycle approval, next-cycle deliverable packaging, and metadata-only execution request creation.
- Phase 63H Customer Console Next-Cycle Execution Run Review on `codex/phase-63h-next-cycle-execution-run-review`, including next-cycle execution run review from next-cycle execution prep requests and queued metadata-only execution run creation.
- Phase 63I Customer Console Next-Cycle Result Feedback Loop on `codex/phase-63i-next-cycle-result-feedback-loop`, including next-cycle result feedback from next-cycle execution runs and approved result, observation, and optimization records for another iteration.
- Phase 63J Customer Console Client Runtime Preflight on `codex/phase-63j-client-runtime-preflight`, including client runtime preflight for queued/retrying execution runs, local Worker API health/status checks, and metadata-only `client_runtime_preflight` ready/blocked records for `worker_console` and `worker_console_desktop`.
- Phase 63K Customer Console Guarded Adapter Dispatch Handoff on `codex/phase-63k-guarded-adapter-dispatch-handoff`, including guarded adapter dispatch handoff for preflight-ready queued/retrying execution runs and metadata-only `guarded_adapter_dispatch_handoff` records for `worker_console` and `worker_console_desktop`.
- Phase 63L-63N Customer Console Execution and Approval Loop on `codex/phase-63l-63n-execution-approval-loop`, including a guarded adapter dry-run action, a visual client execution queue, and a commercial approval center for `worker_console` and `worker_console_desktop`.

Phase 62J still depends on Phase 62H ComfyUI Runtime Post-Manual Readiness Checks for the approved guarded read-only probe chain; Phase 62Y does not loosen that runtime boundary.
