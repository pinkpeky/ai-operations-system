# Commercial Operations Foundation

Updated: 2026-05-22

## Phase

Phase 61A started the path toward the requested commercial automation system:

> A user provides an operating goal; the system plans, generates content, calls materials and knowledge, waits for approval, executes or publishes safely, monitors effects, recovers failures, and reports commercial results.

Phase 61B adds evidence and handoff links to that project center. Phase 61C adds approval gates for individual plan steps. Phase 61D adds approved, metadata-only dry-run records before any real execution. Phase 61E adds reviewable content drafts per channel. Phase 61F promotes asset requests into first-class records. Phase 61G packages approved drafts and approved/prepared asset requests into reviewable commercial operation deliverables that also appear in the Output Library. Phase 61H adds first-class metadata-only execution requests from packaged deliverables. Phase 61I adds metadata-only execution run records with lifecycle, retry, result, and recovery state. Phase 61J adds first-class commercial result records for operator-observed metrics, evidence, outcomes, and follow-up actions after a terminal execution run. Phase 61K adds first-class monitoring observations for approved commercial results. Phase 61L adds first-class optimization decisions from approved monitoring observations. Phase 61M adds first-class evidence snapshots from packaged deliverables so approved knowledge/source evidence and operator checklists can travel into execution requests and execution runs. Phase 61N adds draft evidence snapshot generation from existing RAG search results. Phase 61O adds draft content generation from existing RAG search results. Phase 61P adds draft asset request brief generation from existing RAG search results. Phase 61Q adds metadata-only ComfyUI handoff records from approved or prepared asset requests. Phase 61R adds metadata-only ComfyUI connection preflights from approved or prepared handoffs. Phase 61S adds metadata-only ComfyUI adapter config records for server maintainer endpoint, queue, workflow allowlist, model inventory, runtime-limit, maintenance-note, and secret-reference readiness. Phase 61T adds metadata-only ComfyUI job request records so checked preflights can become reviewable future queue payloads with approval, safety checks, output expectations, and recovery guidance. Phase 61U adds metadata-only ComfyUI execution plan records so approved or queued job requests can become reviewable queue simulation plans with execution steps, local checks, operator checklist, and rollback guidance. Phase 61V adds metadata-only ComfyUI connection probe records so approved or simulated execution plans can become reviewable health and queue snapshot plans with route/readiness checks, sanitized probe payloads, and lifecycle state before any real HTTP request or queue read. Phase 61W adds metadata-only ComfyUI adapter dispatch records so recorded connection probes can become reviewable guarded dispatch handoffs with prompt/workflow/queue payloads, guardrails, retry policy, recovery plan, and lifecycle state before any real adapter call. Phase 61X adds metadata-only ComfyUI runtime gates so recorded adapter dispatches can become server-maintainer reviewed runtime switch, network boundary, queue policy, secret-reference, approval, and rollback records before any real runtime adapter is enabled. Phase 61Y adds metadata-only ComfyUI runtime dry-runs so armed runtime gates can become reviewable adapter contracts, request fixtures, expected response contracts, explicit server-switch policies, validation checks, and rollback records before any real adapter import or ComfyUI call exists. Phase 61Z adds metadata-only ComfyUI runtime activation requests so validated runtime dry-runs can become reviewable activation request, switch audit, runtime guardrail, validation, operator checklist, and rollback records before any runtime switch or adapter call exists. The system still does not attempt the whole autonomous loop yet.

Phase 62B adds a guarded read-only ComfyUI health probe with provider, switch, base URL, timeout, host/path allowlists, disabled action, required configuration, probe status, and guardrail visibility. It makes no network request by default and only attempts `GET /system_stats` when every explicit gate is enabled. Phase 62C adds no-network ComfyUI Runtime Diagnostics so server maintainers can see `readiness_status`, `blocking_reasons`, `recommended_actions`, `read_only_probe_ready`, and each provider/switch/network/host/path gate before any probe is attempted. Phase 62D adds persisted no-network ComfyUI Runtime Diagnostic Snapshots so maintainers can save before/after readiness records with operator notes and metadata. Phase 62E adds a no-network ComfyUI Runtime Maintenance Runbook so maintainers can see ordered steps, the next safe action, recovery actions, configuration summary, and disabled actions in the dedicated ComfyUI page.

## Branch

```text
codex/phase-62e-comfyui-maintenance-console
```

## What This Phase Adds

- Database table: `commercial_operations`.
- Database table: `commercial_operation_links`.
- Database table: `commercial_operation_approvals`.
- Database table: `commercial_operation_dry_runs`.
- Database table: `commercial_operation_content_drafts`.
- Database table: `commercial_operation_asset_requests`.
- Database table: `commercial_operation_comfyui_handoffs`.
- Database table: `commercial_operation_comfyui_preflights`.
- Database table: `commercial_operation_comfyui_adapter_configs`.
- Database table: `commercial_operation_comfyui_job_requests`.
- Database table: `commercial_operation_comfyui_execution_plans`.
- Database table: `commercial_operation_comfyui_connection_probes`.
- Database table: `commercial_operation_comfyui_adapter_dispatches`.
- Database table: `commercial_operation_comfyui_runtime_gates`.
- Database table: `commercial_operation_comfyui_runtime_dry_runs`.
- Database table: `commercial_operation_comfyui_runtime_activations`.
- Database table: `comfyui_runtime_diagnostic_snapshots`.
- Database table: `commercial_operation_deliverables`.
- Database table: `commercial_operation_execution_requests`.
- Database table: `commercial_operation_execution_runs`.
- Database table: `commercial_operation_results`.
- Database table: `commercial_operation_monitoring_observations`.
- Database table: `commercial_operation_optimization_decisions`.
- Database table: `commercial_operation_evidence_snapshots`.
- ORM model: `CommercialOperation`.
- ORM model: `CommercialOperationLink`.
- ORM model: `CommercialOperationApproval`.
- ORM model: `CommercialOperationDryRun`.
- ORM model: `CommercialOperationContentDraft`.
- ORM model: `CommercialOperationAssetRequest`.
- ORM model: `CommercialOperationComfyUIHandoff`.
- ORM model: `CommercialOperationComfyUIPreflight`.
- ORM model: `CommercialOperationComfyUIAdapterConfig`.
- ORM model: `CommercialOperationComfyUIJobRequest`.
- ORM model: `CommercialOperationComfyUIExecutionPlan`.
- ORM model: `CommercialOperationComfyUIConnectionProbe`.
- ORM model: `CommercialOperationComfyUIAdapterDispatch`.
- ORM model: `CommercialOperationComfyUIRuntimeGate`.
- ORM model: `CommercialOperationComfyUIRuntimeDryRun`.
- ORM model: `CommercialOperationComfyUIRuntimeActivation`.
- ORM model: `ComfyUIRuntimeDiagnosticSnapshot`.
- ORM model: `CommercialOperationDeliverable`.
- ORM model: `CommercialOperationExecutionRequest`.
- ORM model: `CommercialOperationExecutionRun`.
- ORM model: `CommercialOperationResult`.
- ORM model: `CommercialOperationMonitoringObservation`.
- ORM model: `CommercialOperationOptimizationDecision`.
- ORM model: `CommercialOperationEvidenceSnapshot`.
- Service layer: `CommercialOperationService`.
- Service layer: `ComfyUIRuntimeService`.
- API route group: `/api/v1/commercial-operations`.
- API route group: `/api/v1/commercial-operations/{operation_id}/links`.
- API route group: `/api/v1/commercial-operations/{operation_id}/approvals`.
- API route group: `/api/v1/commercial-operations/{operation_id}/dry-runs`.
- API route group: `/api/v1/commercial-operations/{operation_id}/content-drafts`.
- RAG content draft route: `/api/v1/commercial-operations/{operation_id}/content-drafts/generate-rag`.
- API route group: `/api/v1/commercial-operations/{operation_id}/asset-requests`.
- RAG asset request route: `/api/v1/commercial-operations/{operation_id}/asset-requests/generate-rag`.
- API route group: `/api/v1/commercial-operations/{operation_id}/comfyui-handoffs`.
- API route group: `/api/v1/commercial-operations/{operation_id}/comfyui-preflights`.
- API route group: `/api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs`.
- API route group: `/api/v1/commercial-operations/{operation_id}/comfyui-job-requests`.
- API route group: `/api/v1/commercial-operations/{operation_id}/comfyui-execution-plans`.
- API route group: `/api/v1/commercial-operations/{operation_id}/comfyui-connection-probes`.
- API route group: `/api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches`.
- API route group: `/api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates`.
- API route group: `/api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs`.
- API route group: `/api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations`.
- API route group: `/api/v1/comfyui-runtime/health`.
- API route group: `/api/v1/comfyui-runtime/capabilities`.
- API route group: `/api/v1/comfyui-runtime/diagnostics`.
- API route group: `/api/v1/comfyui-runtime/maintenance-runbook`.
- API route group: `/api/v1/comfyui-runtime/diagnostic-snapshots`.
- API route group: `/api/v1/commercial-operations/{operation_id}/deliverables`.
- API route group: `/api/v1/commercial-operations/{operation_id}/execution-requests`.
- API route group: `/api/v1/commercial-operations/{operation_id}/execution-runs`.
- API route group: `/api/v1/commercial-operations/{operation_id}/results`.
- API route group: `/api/v1/commercial-operations/{operation_id}/monitoring-observations`.
- API route group: `/api/v1/commercial-operations/{operation_id}/optimization-decisions`.
- API route group: `/api/v1/commercial-operations/{operation_id}/evidence-snapshots`.
- RAG generation route: `/api/v1/commercial-operations/{operation_id}/evidence-snapshots/generate-rag`.
- Admin Dashboard page: `?page=commercial-operations`.
- Admin Dashboard ComfyUI page: `?page=comfyui-operations`.
- API client: `commercialOperationsApi`.
- Migration: `0035_phase61a_commercial_ops`.
- Migration: `0036_phase61b_commercial_links`.
- Migration: `0037_phase61c_op_approvals`.
- Migration: `0038_phase61d_op_dry_runs`.
- Migration: `0039_phase61e_content_drafts`.
- Migration: `0040_phase61f_asset_requests`.
- Migration: `0041_phase61g_deliverables`.
- Migration: `0042_phase61h_exec_requests`.
- Migration: `0043_phase61i_exec_runs`.
- Migration: `0044_phase61j_results`.
- Migration: `0045_phase61k_observations`.
- Migration: `0046_phase61l_opt_decisions`.
- Migration: `0047_phase61m_evidence_snapshots`.
- Migration: `0048_phase61q_comfyui_handoff`.
- Migration: `0049_phase61r_comfyui_preflights`.
- Migration: `0050_phase61s_comfyui_configs`.
- Migration: `0051_phase61t_comfyui_jobs`.
- Migration: `0052_phase61u_comfyui_plans`.
- Migration: `0053_phase61v_comfyui_probes`.
- Migration: `0054_phase61w_comfyui_dispatches`.
- Migration: `0055_phase61x_comfyui_gates`.
- Migration: `0056_phase61y_comfyui_dryruns`.
- Migration: `0057_phase61z_comfyui_active`.
- Migration: `0058_phase62d_comfyui_snaps`.

Each commercial operation stores:

- workspace and creator context;
- title and business objective;
- target audience, channels, budget, constraints, and success metrics;
- optional RAG `knowledge_collection`;
- lifecycle status, priority, and risk level;
- a deterministic `plan_outline` that can be reviewed by a human operator.

Each commercial operation link stores:

- workspace and operation context;
- `link_type`: `conversation`, `artifact`, `task_run`, `workflow_run`, `rag_document`, `knowledge_source`, `approval`, or `external`;
- `target_type` and `target_id` for the referenced object;
- operator-facing title, optional summary, source name, and metadata.

Each commercial operation approval stores:

- workspace and operation context;
- `step_key` for the plan step being gated;
- approval title, requested action, risk level, requester, reviewer, reviewer notes, decision timestamps, and metadata;
- `approval_status`: `pending`, `approved`, `rejected`, or `cancelled`.

Each commercial operation dry-run stores:

- workspace, operation, approval, and plan-step context;
- `execution_mode`: `metadata_only` or `dry_run`;
- execution target, input summary, runbook, expected outputs, readiness checks, result summary, failure reason, requester, completer, decision timestamps, and metadata;
- `dry_run_status`: `created`, `completed`, `failed`, or `cancelled`.

Each commercial operation content draft stores:

- workspace, operation, and plan-step context;
- channel, content format, title, audience segment, draft body, summary, call to action, source materials, asset request placeholders, reviewer notes, and metadata;
- creator, updater, approver, decision timestamps, and archive timestamp;
- `draft_status`: `draft`, `ready_for_review`, `approved`, `rejected`, or `archived`.

Each commercial operation asset request stores:

- workspace, operation, optional content draft, and plan-step context;
- channel, asset type, title, purpose, dimensions, style constraints, future generation prompt, negative prompt, source materials, readiness checks, and handoff payload;
- requester, updater, approver, preparer, reviewer notes, result summary, failure reason, decision timestamps, archive timestamp, and metadata;
- `request_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `prepared`, `failed`, or `archived`.

Each commercial operation ComfyUI handoff stores:

- workspace, operation, approved/prepared asset request, optional content draft, and plan-step context;
- channel, asset type, title, workflow name, dimensions, future generation prompt, negative prompt, prompt payload, workflow payload, source materials, readiness checks, and handoff payload;
- requester, updater, approver, preparer, reviewer notes, result summary, failure reason, decision timestamps, archive timestamp, and metadata;
- `handoff_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `prepared`, `failed`, or `archived`.

Each commercial operation ComfyUI adapter config stores:

- workspace, operation, maintainer-facing title, endpoint URL, auth mode, secret reference, queue name, default workflow, allowed workflows, model inventory, runtime limits, maintenance notes, validation checks, and config payload;
- creator, updater, validator, archiver, validation/failure/archive timestamps, result summary, failure reason, and metadata;
- `config_status`: `draft`, `ready`, `blocked`, `failed`, or `archived`.

Each commercial operation ComfyUI job request stores:

- workspace, operation, checked preflight, linked handoff, optional adapter config, approved/prepared asset request, and plan-step context;
- queue name, workflow name, prompt/workflow payloads, runtime payload, safety checks, output expectations, recovery plan, job payload, result summary, failure reason, reviewer notes, and metadata;
- requester, updater, approver, queuer, canceller, archiver, decision timestamps, failure timestamp, and cancellation timestamp;
- `job_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `queued`, `failed`, `cancelled`, or `archived`.

Each commercial operation ComfyUI execution plan stores:

- workspace, operation, approved/queued job request, checked preflight, linked handoff, optional adapter config, approved/prepared asset request, and plan-step context;
- queue name, workflow name, execution mode, queue payload, execution steps, simulation checks, operator checklist, rollback plan, simulation payload, plan payload, result summary, failure reason, reviewer notes, and metadata;
- planner, updater, approver, simulator, canceller, archiver, decision timestamps, simulation timestamp, failure timestamp, and cancellation timestamp;
- `plan_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `simulated`, `failed`, `cancelled`, or `archived`.

Each commercial operation ComfyUI connection probe stores:

- workspace, operation, approved/simulated execution plan, approved/queued job request, checked preflight, linked handoff, optional adapter config, approved/prepared asset request, and plan-step context;
- target URL, queue name, workflow name, metadata-only probe mode, documented health and queue endpoints, expected routes, readiness checks, sanitized probe payload, metadata-only health snapshot, metadata-only queue snapshot, response schema, probe plan payload, result summary, failure reason, reviewer notes, and metadata;
- planner, updater, approver, probe marker, canceller, archiver, decision timestamps, probe timestamp, failure timestamp, and cancellation timestamp;
- `probe_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `probed`, `failed`, `cancelled`, or `archived`.

Each commercial operation ComfyUI adapter dispatch stores:

- workspace, operation, probed connection probe, approved/simulated execution plan, approved/queued job request, checked preflight, linked handoff, optional adapter config, approved/prepared asset request, and plan-step context;
- target URL, queue name, workflow name, metadata-only dispatch mode, prompt payload, workflow payload, queue payload, sanitized dispatch payload, guardrails, operator checklist, retry policy, recovery plan, dispatch plan payload, result summary, failure reason, reviewer notes, and metadata;
- planner, updater, approver, dispatch marker, canceller, archiver, decision timestamps, dispatch timestamp, failure timestamp, and cancellation timestamp;
- `dispatch_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `dispatched`, `failed`, `cancelled`, or `archived`.

Each commercial operation ComfyUI runtime gate stores:

- workspace, operation, recorded adapter dispatch, connection probe, execution plan, job request, checked preflight, linked handoff, optional adapter config, approved/prepared asset request, and plan-step context;
- target URL, queue name, workflow name, metadata-only runtime mode, environment payload, network policy, queue policy, secret-reference policy, approval policy, validation checks, operator checklist, rollback plan, gate payload, result summary, failure reason, reviewer notes, and metadata;
- planner, updater, approver, arming marker, disabler, archiver, approval/rejection/arming/disable/failure/archive timestamps;
- `gate_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `armed`, `disabled`, `failed`, or `archived`.

Each commercial operation ComfyUI runtime dry-run stores:

- workspace, operation, armed runtime gate, adapter dispatch, connection probe, execution plan, job request, checked preflight, linked handoff, optional adapter config, approved/prepared asset request, and plan-step context;
- target URL, queue name, workflow name, metadata-only dry-run mode, adapter contract, dry-run request fixture, expected response contract, explicit server-switch runtime policy, validation checks, operator checklist, rollback plan, dry-run payload, result summary, failure reason, reviewer notes, and metadata;
- planner, updater, approver, validator, canceller, archiver, approval/rejection/validation/failure/cancellation/archive timestamps;
- `dry_run_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `validated`, `failed`, `cancelled`, or `archived`.

Each commercial operation ComfyUI runtime activation stores:

- workspace, operation, validated runtime dry-run, runtime gate, adapter dispatch, connection probe, execution plan, job request, checked preflight, linked handoff, optional adapter config, approved/prepared asset request, and plan-step context;
- target URL, queue name, workflow name, metadata-only activation mode, activation request, switch audit, runtime guardrails, validation checks, operator checklist, rollback plan, activation payload, result summary, failure reason, reviewer notes, and metadata;
- planner, updater, approver, scheduler, canceller, archiver, approval/rejection/schedule/failure/cancellation/archive timestamps;
- `activation_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `scheduled`, `failed`, `cancelled`, or `archived`.

Each commercial operation deliverable stores:

- workspace, operation, approved content draft, linked asset request ids, and plan-step context;
- channel, deliverable type, title, summary, delivery notes, quality checks, package payload, result summary, failure reason, reviewer notes, and metadata;
- creator, updater, approver, packager, decision timestamps, failure timestamp, and archive timestamp;
- `output_artifact_id` for the linked Output Library artifact with `source_type=commercial_operation`;
- `deliverable_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `packaged`, `failed`, or `archived`.

Each commercial operation execution request stores:

- workspace, operation, packaged deliverable, linked Output Library artifact, and plan-step context;
- channel, execution type, execution mode, title, target platform/account, input summary, runbook, readiness checks, expected outputs, approved evidence snapshot IDs, operator checklist items, handoff payload, reviewer notes, result summary, failure reason, and metadata;
- requester, updater, approver, preparer, canceller, decision timestamps, failure timestamp, cancellation timestamp, and archive timestamp;
- `request_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `prepared`, `failed`, `cancelled`, or `archived`.

Each commercial operation execution run stores:

- workspace, operation, prepared execution request, packaged deliverable, linked Output Library artifact, and plan-step context;
- channel, execution type, execution mode, target platform/account, title, input payload, runbook snapshot, readiness checks, expected outputs, approved evidence snapshot IDs, operator checklist snapshot, runtime payload, result payload, recovery plan, operator notes, and metadata;
- queuer, starter, completer, canceller, lifecycle timestamps, retry count, and maximum retries;
- `run_status`: `queued`, `running`, `succeeded`, `failed`, `retrying`, `cancelled`, or `archived`.

Each commercial operation result stores:

- workspace, operation, terminal execution run, execution request, packaged deliverable, linked Output Library artifact, and plan-step context;
- channel, result type, title, result summary, observed outcome, operator-observed metrics, commercial signals, evidence links, follow-up actions, result payload, recommendation payload, reviewer notes, and metadata;
- creator, updater, approver, approval/rejection/archive timestamps;
- `result_status`: `draft`, `ready_for_review`, `approved`, `rejected`, or `archived`.

Each commercial operation monitoring observation stores:

- workspace, operation, approved result, terminal execution run, execution request, packaged deliverable, linked Output Library artifact, and plan-step context;
- channel, observation type, title, optional observation window, operator-observed metric snapshots, qualitative signals, evidence links, anomaly flags, recommended actions, observation payload, reviewer notes, and metadata;
- creator, updater, approver, approval/rejection/archive timestamps;
- `observation_status`: `draft`, `ready_for_review`, `approved`, `rejected`, or `archived`.

Each commercial operation optimization decision stores:

- workspace, operation, approved monitoring observation, approved result, terminal execution run, execution request, packaged deliverable, linked Output Library artifact, and plan-step context;
- channel, decision type, title, priority, rationale, objective updates, content actions, asset actions, audience actions, execution actions, risk controls, decision payload, reviewer notes, optional next review time, and metadata;
- creator, updater, approver, approval/rejection/archive timestamps;
- `decision_status`: `draft`, `ready_for_review`, `approved`, `rejected`, or `archived`.

Each commercial operation evidence snapshot stores:

- workspace, operation, packaged deliverable, optional content draft, optional linked Output Library artifact, and plan-step context;
- channel, evidence type, title, knowledge collection, query, evidence summary, relevance notes, source document ids, source links, evidence items, coverage checks, snapshot payload, reviewer notes, and metadata;
- creator, updater, approver, approval/rejection/archive timestamps;
- `snapshot_status`: `draft`, `ready_for_review`, `approved`, `rejected`, or `archived`.

## Evidence and Handoff Links

Phase 61B treats these links as operator-readable evidence and handoff context. They are deliberately lightweight references so later phases can build approval-backed plan steps, content artifacts, RAG snapshots, safe dry-runs, monitoring, and result reports on top of a durable project record.

## Approval Gates

Phase 61C treats approvals as explicit human decisions on the plan outline. Creating or deciding an approval writes the approval state back to the matching `plan_outline` step so operators can see which step is gated, approved, rejected, or cancelled.

## Safe Dry-Runs

Phase 61D treats dry-runs as metadata-only execution preparation records. Creating a dry-run requires an approved commercial operation approval in the same workspace and operation. Completing, failing, or cancelling the dry-run writes the dry-run state back to the matching `plan_outline` step so operators can see whether the execution preparation is ready for later handoff.

Dry-runs do not call OpenClaw, ComfyUI, Browser Worker, real accounts, or publishing platforms. They only record the proposed target, expected outputs, readiness checks, and operator result.

## Content Drafts

Phase 61E treats content drafts as reviewable artifacts for a specific operation plan step. A draft can be created, edited, marked ready for review, approved, rejected, or archived. Creating or deciding a draft writes the draft state back to the matching `plan_outline` step so operators can see which content step already has a draft and whether it is approved.

Phase 61O adds controlled RAG content draft generation. Operators can call `/content-drafts/generate-rag` with a plan step, channel, format, query, collection, and search mode. The route searches the existing RAG index, reranks results, records retrieved chunks as source materials, captures search metadata, and creates a draft content record that still requires human review before approval.

Content drafts do not publish content, call OpenClaw, run ComfyUI jobs, control browser workers, or contact external accounts. Asset requests are placeholders only; they prepare the later ComfyUI handoff shape without starting a real generation job.

## Asset Requests

Phase 61F treats asset requests as first-class, reviewable records. A request can be created from a plan step and optionally linked to a content draft, edited, marked ready for review, approved, rejected, prepared for future ComfyUI handoff, failed during preparation, or archived. Creating or deciding an asset request writes the latest request state back to the matching `plan_outline` step so operators can see whether a channel needs visual, video, design, or supporting content assets.

Phase 61P adds controlled RAG asset brief generation. Operators can call `/asset-requests/generate-rag` with a plan step, optional content draft, channel, asset type, query, collection, and search mode. The route searches the existing RAG index, reranks results, records retrieved chunks as source materials, captures search metadata, builds readiness checks, and creates a draft asset request record that still requires human review before approval or preparation.

Asset requests do not start ComfyUI, publish assets, run OpenClaw, control Browser Worker actions, or contact external accounts. The `handoff_payload` is intentionally metadata-only and carries the later ComfyUI shape, source materials, checks, and safety boundary.

## ComfyUI Handoffs

Phase 61Q treats ComfyUI handoffs as first-class, operator-reviewed metadata records created from approved or prepared asset requests. A handoff can be created, edited, marked ready for review, approved, rejected, prepared for a future guarded adapter, failed during preparation, or archived. Creating or deciding a handoff writes the latest ComfyUI handoff state back to the matching `plan_outline` step.

ComfyUI handoffs do not submit jobs to ComfyUI, generate images or videos, publish assets, run OpenClaw, control Browser Worker actions, contact external accounts, or bypass approval. The `handoff_payload` records the operation, source asset request, workflow name, prompt payload, workflow payload, readiness checks, `future_guarded_comfyui_adapter`, and forbidden actions so both workstation operators and server maintainers can understand what is prepared and what is still blocked.

## ComfyUI Preflights

Phase 61R treats ComfyUI preflights as first-class, metadata-only readiness records created from approved or prepared ComfyUI handoffs. A preflight can be created, edited, rechecked, marked failed, or archived. Creating or checking a preflight writes the latest preflight state back to the matching `plan_outline` step.

Preflights record target URL, queue name, workflow name, model/checkpoint references, guarded adapter config, local check items, result summary, and failure reason. The service normalizes adapter config back to `execution_mode=metadata_only`, `network_probe=disabled`, and `queue_submission=disabled` so client input cannot accidentally open live execution. Preflights do not call ComfyUI, submit queue jobs, generate media, publish, run OpenClaw, control Browser Worker actions, contact external accounts, or bypass approval. The `preflight_payload` is designed for workstation users and server maintainers to understand what configuration is ready and what remains blocked before a future guarded adapter is allowed.

## ComfyUI Adapter Config

Phase 61S treats ComfyUI adapter configs as first-class, metadata-only maintenance records for server maintainers. A config can be created, edited, validated, marked failed, or archived. Creating or validating a config writes the latest adapter config state back to the `content_production` step in `plan_outline`, and a ready config can be selected by a ComfyUI preflight to prefill endpoint, queue, workflow, model references, and guarded adapter metadata.

Adapter configs record target URL, auth mode, secret reference, queue name, default workflow, allowed workflow names, model inventory, runtime limits, maintenance notes, local validation checks, result summary, and failure reason. The service normalizes runtime limits back to `execution_mode=metadata_only`, `network_probe=false`, `queue_submission=false`, and `submit_jobs=false` so client input cannot accidentally open live execution. Adapter configs do not store secret values, call ComfyUI, submit queue jobs, generate media, publish, run OpenClaw, control Browser Worker actions, contact external accounts, or bypass approval. The `config_payload` is designed for workstation users and server maintainers to see whether the future guarded adapter is available, blocked, failed, or archived.

## ComfyUI Job Requests

Phase 61T treats ComfyUI job requests as first-class, metadata-only operating records created from checked ComfyUI preflights. A request can be drafted, edited, sent for review, approved, rejected, marked queued, marked failed, cancelled, or archived. Creating or deciding a job request writes the latest job-request state back to the matching `plan_outline` step.

Job requests record the checked preflight, linked handoff, optional adapter config and asset request, queue name, workflow name, prompt/workflow payload, runtime payload, safety checks, output expectations, recovery plan, result summary, failure reason, reviewer notes, and operator attribution. The service normalizes runtime payloads back to `execution_mode=metadata_only`, `connection_mode=metadata_only`, `network_probe=false`, `queue_submission=false`, `submit_job=false`, and `external_calls=disabled` so client input cannot accidentally open live execution. Job requests do not call ComfyUI, submit queue jobs, upload files, generate media, publish, run OpenClaw, control Browser Worker actions, contact external accounts, store secret values, or bypass approval. The `job_payload` is designed for workstation users and server maintainers to review the future queue shape and recovery steps before any guarded adapter exists.

## ComfyUI Execution Plans

Phase 61U treats ComfyUI Execution Plans as first-class, metadata-only operating records created from approved or queued ComfyUI job requests. A plan can be drafted, edited, sent for review, approved, rejected, simulated, marked failed, cancelled, or archived. Creating or deciding an execution plan writes the latest execution-plan state back to the matching `plan_outline` step.

Execution plans record the approved/queued job request, checked preflight, linked handoff, optional adapter config and asset request, queue/workflow names, queue payload, execution steps, simulation checks, operator checklist, rollback plan, simulation payload, result summary, failure reason, reviewer notes, and operator attribution. The service normalizes simulation payloads back to `execution_mode=metadata_only`, `connection_mode=metadata_only`, `network_probe=false`, `queue_submission=false`, `submit_job=false`, `upload_files=false`, and `external_calls=disabled` so client input cannot accidentally open live execution. Execution plans do not call ComfyUI, submit queue jobs, upload files, generate media, publish, run OpenClaw, control Browser Worker actions, contact external accounts, store secret values, or bypass approval. The `plan_payload` is designed for workstation users and server maintainers to review the future queue simulation shape and rollback steps before any guarded adapter exists.

## ComfyUI Connection Probes

Phase 61V treats ComfyUI Connection Probes as first-class, metadata-only operating records created from approved or simulated ComfyUI execution plans. A probe can be drafted, edited, sent for review, approved, rejected, marked probed, marked failed, cancelled, or archived. Creating or deciding a connection probe writes the latest connection-probe state back to the matching `plan_outline` step.

Connection probes record the approved/simulated execution plan, job request, checked preflight, linked handoff, optional adapter config and asset request, target URL, queue/workflow names, health endpoint, queue endpoint, expected routes, readiness checks, sanitized probe payload, metadata-only health snapshot, metadata-only queue snapshot, response schema, result summary, failure reason, reviewer notes, and operator attribution. The service normalizes probe payloads back to `probe_mode=metadata_only`, `network_probe=false`, `read_only_probe=false`, `queue_submission=false`, `submit_job=false`, `upload_files=false`, `secret_value_present=false`, and `external_calls=disabled` so client input cannot accidentally open live probing. Connection probes do not call ComfyUI, read ComfyUI queues, submit queue jobs, upload files, generate media, publish, run OpenClaw, control Browser Worker actions, contact external accounts, store secret values, or bypass approval. The `probe_plan_payload` is designed for workstation users and server maintainers to review the future health/queue probe shape before any guarded adapter exists.

## ComfyUI Adapter Dispatches

Phase 61W treats ComfyUI Adapter Dispatches as first-class, metadata-only operating records created from probed ComfyUI connection probes. A dispatch can be drafted, edited, sent for review, approved, rejected, marked dispatched, marked failed, cancelled, or archived. Creating or deciding an adapter dispatch writes the latest dispatch state back to the matching `plan_outline` step.

Adapter dispatches record the probed connection probe, approved/simulated execution plan, job request, checked preflight, linked handoff, optional adapter config and asset request, target URL, queue/workflow names, prompt payload, workflow payload, queue payload, sanitized dispatch payload, guardrails, operator checklist, retry policy, recovery plan, result summary, failure reason, reviewer notes, and operator attribution. The service normalizes dispatch payloads back to `dispatch_mode=metadata_only`, `network_request=false`, `queue_submission=false`, `prompt_submission=false`, `submit_job=false`, `upload_files=false`, `generation_started=false`, `secret_value_present=false`, and `external_calls=disabled` so client input cannot accidentally open live dispatch. Adapter dispatches do not call ComfyUI, read ComfyUI queues, submit prompts, submit queue jobs, upload files, generate media, publish, run OpenClaw, control Browser Worker actions, contact external accounts, store secret values, or bypass approval. The `dispatch_plan_payload` is designed for workstation users and server maintainers to review the future guarded adapter dispatch shape before any runtime adapter exists.

## ComfyUI Runtime Gates

Phase 61X treats ComfyUI Runtime Gates as first-class, metadata-only operating records created from recorded ComfyUI adapter dispatches. A gate can be drafted, edited, sent for review, approved, rejected, marked armed, marked failed, disabled, or archived. Creating or deciding a runtime gate writes the latest runtime-gate state back to the matching `plan_outline` step.

Runtime gates record the adapter dispatch, connection probe, execution plan, job request, checked preflight, linked handoff, optional adapter config and asset request, target URL, queue/workflow names, environment payload, network policy, queue policy, secret-reference policy, approval policy, validation checks, operator checklist, rollback plan, result summary, failure reason, reviewer notes, and operator attribution. The service normalizes runtime gate payloads back to `runtime_mode=metadata_only`, `runtime_calls_enabled=false`, `adapter_runtime_enabled=false`, `allow_network_requests=false`, `http_client_enabled=false`, `queue_read=false`, `queue_submission=false`, `submit_job=false`, `prompt_submission=false`, `upload_files=false`, `secret_value_present=false`, `secret_lookup_enabled=false`, and `approval_bypass_allowed=false` so client input cannot accidentally open live runtime execution. Runtime gates do not call ComfyUI, read queues, submit prompts, submit queue jobs, upload files, generate media, publish, run OpenClaw, control Browser Worker actions, contact external accounts, store or resolve secret values, or bypass approval. The `gate_payload` is designed for workstation users and server maintainers to review the future controlled runtime cutover before any real adapter runtime exists.

## ComfyUI Runtime Dry-Runs

Phase 61Y treats ComfyUI Runtime Dry-Runs as first-class, metadata-only operating records created from armed ComfyUI runtime gates. A dry-run can be drafted, edited, sent for review, approved, rejected, marked validated, marked failed, cancelled, or archived. Creating or deciding a runtime dry-run writes the latest runtime-dry-run state back to the matching `plan_outline` step.

Runtime dry-runs record the armed runtime gate, adapter dispatch, connection probe, execution plan, job request, checked preflight, linked handoff, optional adapter config and asset request, target URL, queue/workflow names, adapter contract, dry-run request fixture, expected response contract, explicit server-switch runtime policy, validation checks, operator checklist, rollback plan, result summary, failure reason, reviewer notes, and operator attribution. The service normalizes runtime dry-run payloads back to `dry_run_mode=metadata_only`, `contract_mode=metadata_only`, `adapter_call_executed=false`, `network_request=false`, `queue_read=false`, `queue_submission=false`, `prompt_submission=false`, `upload_files=false`, `generation_started=false`, `server_switch_enabled=false`, `runtime_calls_enabled=false`, `http_client_enabled=false`, `secret_value_present=false`, `secret_lookup_enabled=false`, and `approval_bypass_allowed=false` so client input cannot accidentally open live runtime execution. Runtime dry-runs do not import or call a ComfyUI adapter, call ComfyUI, read queues, submit prompts, submit queue jobs, upload files, generate media, enable runtime switches, publish, run OpenClaw, control Browser Worker actions, contact external accounts, store or resolve secret values, or bypass approval. The `dry_run_payload` is designed for workstation users and server maintainers to review the future explicitly enabled runtime adapter contract before any real adapter runtime exists.

## ComfyUI Runtime Activations

Phase 61Z treats ComfyUI Runtime Activations as first-class, metadata-only operating records created from validated ComfyUI runtime dry-runs. An activation can be drafted, edited, sent for review, approved, rejected, scheduled as a metadata-only handoff, marked failed, cancelled, or archived. Creating or deciding a runtime activation writes the latest runtime-activation state back to the matching `plan_outline` step.

Runtime activations record the validated runtime dry-run, runtime gate, adapter dispatch, connection probe, execution plan, job request, checked preflight, linked handoff, optional adapter config and asset request, target URL, queue/workflow names, activation request, switch audit, runtime guardrails, validation checks, operator checklist, rollback plan, result summary, failure reason, reviewer notes, and operator attribution. The service normalizes runtime activation payloads back to `activation_mode=metadata_only`, `adapter_import_executed=false`, `adapter_call_executed=false`, `network_request=false`, `queue_read=false`, `queue_submission=false`, `prompt_submission=false`, `upload_files=false`, `generation_started=false`, `server_switch_enabled=false`, `runtime_config_written=false`, `environment_updated=false`, `secret_value_present=false`, `secret_lookup_enabled=false`, and `approval_bypass_allowed=false` so client input cannot accidentally open live runtime execution. Runtime activations do not import or call a ComfyUI adapter, call ComfyUI, read queues, submit prompts, submit queue jobs, upload files, generate media, enable runtime switches, mutate environment/config, publish, run OpenClaw, control Browser Worker actions, contact external accounts, store or resolve secret values, or bypass approval. The `activation_payload` is designed for workstation users and server maintainers to review the future explicit cutover request before any real adapter runtime exists.

## ComfyUI Runtime Adapter Contract

Phase 62A adds a disabled-by-default runtime adapter contract surface for server maintainers. `GET /api/v1/comfyui-runtime/health` reports provider, enabled switch, reachability false, external request false, runtime calls disabled, base URL, timeout, allowed hosts, workspace, and a contract error. `GET /api/v1/comfyui-runtime/capabilities` reports allowed contract-review actions, disabled live actions, required future configuration, and guardrails.

## ComfyUI Guarded Read-Only Probe

Phase 62B extends that surface with a guarded read-only health probe. The health endpoint still performs no network request by default. It attempts exactly one `GET /system_stats` only when `COMFYUI_RUNTIME_PROVIDER=guarded`, `COMFYUI_RUNTIME_ENABLED=true`, `COMFYUI_RUNTIME_ALLOW_NETWORK=true`, `COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=true`, the host is listed in `COMFYUI_RUNTIME_ALLOWED_HOSTS`, and the path is listed in `COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS`. The response adds `read_only_probe_enabled`, `read_only_probe_attempted`, `health_path`, `allowed_health_paths`, `probe_status_code`, and `probe_latency_ms`. Runtime calls remain disabled: no adapter import/call, prompt submission, queue read/submission, upload, generation, runtime switch mutation, secret resolution, publishing, OpenClaw, Browser Worker action, or account control.

## ComfyUI Runtime Diagnostics

Phase 62C adds `GET /api/v1/comfyui-runtime/diagnostics` for no-network maintainer readiness checks. The response includes `readiness_status`, `blocking_reasons`, `recommended_actions`, `read_only_probe_ready`, `external_request_attempted=false`, `runtime_calls_enabled=false`, and per-gate checks for `provider_guarded`, `runtime_enabled`, `network_gate`, `base_url_scheme`, `base_url_host_allowlist`, `read_only_probe_gate`, `health_path_allowlist`, and `execution_boundary`. It never calls ComfyUI; it only explains whether the guarded Phase 62B read-only probe is ready.

## ComfyUI Runtime Diagnostic Snapshots

Phase 62D adds `comfyui_runtime_diagnostic_snapshots`, `POST /api/v1/comfyui-runtime/diagnostic-snapshots`, and `GET /api/v1/comfyui-runtime/diagnostic-snapshots` for persisted no-network maintainer audit trails. Snapshot creation reuses Phase 62C diagnostics and stores `readiness_status`, `blocking_reasons`, `recommended_actions`, `read_only_probe_ready`, diagnostic checks, forbidden actions, the full diagnostic payload, operator note, and metadata. It never calls ComfyUI; it only records the current guarded readiness state so server maintainers can compare before/after configuration changes.

## ComfyUI Runtime Maintenance Runbook

Phase 62E adds `GET /api/v1/comfyui-runtime/maintenance-runbook` for a no-network maintainer runbook. The response reuses Phase 62C diagnostics and returns ordered operator steps, `next_operator_action`, `recovery_actions`, `configuration_summary`, `snapshot_recommended`, disabled actions, and the source diagnostics payload. It never calls ComfyUI; it gives workstation operators and server maintainers a concise checklist for what to fix or verify next.

The `ComfyUIRuntimeService` does not import or call a ComfyUI adapter, call ComfyUI endpoints, read queues, submit prompts, submit queue jobs, upload files, generate media, enable runtime switches, mutate environment/config, publish, run OpenClaw, control Browser Worker actions, contact external accounts, store or resolve secret values, or bypass approval. The Admin Dashboard exposes the contract, runbook, and snapshots in the dedicated `?page=comfyui-operations` tab so server maintainers can inspect and retain the future live-adapter boundary without making a network request.

## Deliverables

Phase 61G treats deliverables as the operator-facing handoff package for an approved content draft and approved/prepared asset requests. A deliverable can be created, edited, marked ready for review, approved, rejected, packaged, failed during packaging, or archived. Creating or deciding a deliverable writes the latest deliverable state back to the matching `plan_outline` step.

Creating a deliverable also creates a linked Output Library artifact with `source_type=commercial_operation`, `artifact_type=markdown`, and a metadata-only content package. Packaging the deliverable moves that artifact to the packaged stage so the next operator can find the commercial handoff in the same artifact surface used by conversations, playbooks, tasks, and workflows.

Deliverables do not publish content, execute OpenClaw actions, run Browser Worker actions, run ComfyUI jobs, contact external accounts, or bypass approval. The `package_payload` describes the future handoff shape only; the next runtime step remains a future monitored execution request.

## Evidence Snapshots

Phase 61M treats evidence snapshots as first-class, operator-reviewed knowledge packages created from packaged deliverables. A snapshot can be created only after a deliverable is `packaged`; it can then be edited while draft or rejected, marked ready for review, approved, rejected, or archived. Creating or deciding a snapshot writes the latest evidence state back to the matching `plan_outline` step and the deliverable package payload.

Phase 61N adds controlled RAG evidence generation. Operators can call `/evidence-snapshots/generate-rag` with a packaged deliverable, query, collection, and search mode. The route searches the existing RAG index, reranks results, records retrieved chunks as evidence items, captures source document IDs and search metadata, and creates a draft evidence snapshot that still requires human review before approval.

Approved evidence snapshots can be attached to execution requests. When an execution run is created, the approved evidence snapshot IDs and operator checklist are copied into the run so a workstation operator or server maintainer can see exactly which knowledge/source evidence was reviewed before future execution.

Evidence snapshots are still guarded records. Manual snapshots do not run live RAG retrieval. Generated snapshots run only existing RAG search and do not upload or ingest knowledge files, execute OpenClaw actions, run Browser Worker actions, run ComfyUI jobs, contact external accounts, publish content, ingest platform analytics, claim ROI attribution, auto-approve evidence, or bypass approval. The `snapshot_payload` records the reviewed source evidence shape, retrieved chunk counts, search mode, and forbidden actions.

## Execution Requests

Phase 61H treats execution requests as first-class, reviewable records created from packaged deliverables. A request can be created, edited, marked ready for review, approved, rejected, prepared for future guarded runtime handoff, failed before handoff, cancelled before preparation, or archived. Creating or deciding an execution request writes the latest request state back to the matching `plan_outline` step.

Execution requests are still metadata-only. They do not publish content, execute OpenClaw actions, run Browser Worker actions, run ComfyUI jobs, contact external accounts, or bypass approval. The `handoff_payload` records the future runtime shape, approved evidence snapshot IDs, operator checklist, `future_guarded_runtime_adapter`, and the forbidden actions list so workstation operators and server maintainers can see exactly what has and has not happened.

## Execution Runs

Phase 61I treats execution runs as first-class audit and recovery records created from prepared execution requests. A run can be created, edited while queued or retrying, started, marked succeeded, marked failed, retried when the retry limit allows it, cancelled, or archived. Creating or deciding a run writes the latest run state back to the matching `plan_outline` step.

Execution runs are still metadata-only. They do not publish content, execute OpenClaw actions, run Browser Worker actions, run ComfyUI jobs, contact external accounts, or bypass approval. The `runtime_payload` records the future guarded runtime shape and the forbidden actions list; the `recovery_plan` records retry availability and operator recovery steps.

## Results

Phase 61J treats results as first-class operator review records created from terminal execution runs. A result can be created only after a run is `succeeded`, `failed`, or `cancelled`; it can then be edited while draft or rejected, marked ready for review, approved, rejected, or archived. Creating or deciding a result writes the latest result state back to the matching `plan_outline` step.

Results are still metadata-only. They do not ingest platform analytics, claim ROI attribution, publish content, execute OpenClaw actions, run Browser Worker actions, run ComfyUI jobs, contact external accounts, or bypass approval. The `recommendation_payload` records operator next steps and explicitly preserves the boundary that metrics are operator-observed unless a later monitored analytics adapter is added.

## Monitoring Observations

Phase 61K treats monitoring observations as first-class operator review records created from approved commercial results. An observation can be created only after the result is approved; it can then be edited while draft or rejected, marked ready for review, approved, rejected, or archived. Creating or deciding an observation writes the latest monitoring state back to the matching `plan_outline` step.

Monitoring observations are still metadata-only. They do not ingest platform analytics, claim ROI attribution, publish content, execute OpenClaw actions, run Browser Worker actions, run ComfyUI jobs, contact external accounts, or bypass approval. The `observation_payload` records operator next steps and explicitly preserves the boundary that metric snapshots are operator-observed unless a later monitored analytics adapter is approved.

## Optimization Decisions

Phase 61L treats optimization decisions as first-class operator review records created from approved monitoring observations. A decision can be created only after the observation is approved; it can then be edited while draft or rejected, marked ready for review, approved, rejected, or archived. Creating or deciding an optimization decision writes the latest decision state back to the matching `plan_outline` step.

Optimization decisions are still metadata-only. They do not auto-optimize content, assets, audiences, budgets, or execution handoffs. They do not publish content, execute OpenClaw actions, run Browser Worker actions, run ComfyUI jobs, contact external accounts, ingest platform analytics, claim ROI attribution, or bypass approval. The `decision_payload` records operator next steps and explicitly preserves the boundary that every future optimization must still pass a separate approved execution path.

## Operator Flow

1. Open Admin Dashboard and select Commercial Ops / 商业运营.
2. Enter a clear business objective.
3. Add channels, success metrics, constraints, risk level, and the RAG collection to use.
4. Create the operation.
5. Review the generated plan outline.
6. Regenerate the plan when the goal or constraints change.
7. Move the operation to ready, active, or paused when the human operating process changes.
8. Create content drafts for the relevant channels manually or from existing RAG search, edit them, send them for review, approve/reject them, and archive obsolete drafts.
9. Create asset requests for images, videos, covers, design files, or supporting assets manually or from existing RAG search; approve, prepare, fail, or archive them without starting generation.
10. Create ComfyUI handoffs from approved/prepared asset requests, approve or prepare them, and keep prompt/workflow payloads reviewable without submitting jobs.
11. Create ComfyUI adapter configs for maintainer-reviewed endpoint, queue, workflow allowlist, model inventory, runtime limits, and secret references; validate them locally without calling ComfyUI.
12. Create ComfyUI preflights from approved/prepared handoffs, optionally select a ready adapter config, and recheck local readiness without submitting queues.
13. Create ComfyUI job requests from checked preflights, review safety checks/output expectations/recovery guidance, then approve, reject, mark queued, fail, cancel, or archive them without submitting queues.
14. Create ComfyUI execution plans from approved/queued job requests, review execution steps, simulation checks, operator checklist, and rollback guidance, then approve, reject, simulate, fail, cancel, or archive them without submitting queues.
15. Create ComfyUI connection probes from approved/simulated execution plans, review documented health and queue endpoints, readiness checks, metadata-only health snapshots, metadata-only queue snapshots, and response schemas, then approve, reject, mark probed, fail, cancel, or archive them without making HTTP requests or reading queues.
16. Package approved drafts and approved/prepared asset requests into deliverables, then approve, package, fail, or archive the handoff package.
17. Create execution requests from packaged deliverables, then send them for review, approve/reject them, prepare/cancel/fail them, or archive them without external execution.
18. Create execution runs from prepared execution requests, then start/succeed/fail/retry/cancel/archive them as metadata-only operating records.
19. Create result records from succeeded, failed, or cancelled execution runs; record observed metrics, evidence, outcomes, and follow-up actions; then send them for review, approve/reject, or archive them.
20. Create monitoring observations from approved result records; record metric snapshots, qualitative signals, evidence, anomalies, and recommended actions; then send them for review, approve/reject, or archive them.
21. Create optimization decisions from approved monitoring observations; record rationale, content, asset, audience, execution, and risk-control actions; then send them for review, approve/reject, or archive them.
22. Create evidence snapshots from packaged deliverables; record reviewed knowledge collection, source document ids, source links, evidence items, coverage checks, and relevance notes; then send them for review, approve/reject, or archive them.
23. Create approval gates for risky plan steps, approve/reject/cancel them, and keep the plan outline updated.
24. Create safe dry-runs from approved approval records, then mark them completed, failed, or cancelled after operator review.
25. Attach evidence or handoff links so the next operator can find the source conversation, RAG document, generated artifact, task run, workflow run, approval record, content draft, asset request, ComfyUI handoff, ComfyUI preflight, ComfyUI adapter config, ComfyUI job request, ComfyUI execution plan, ComfyUI connection probe, deliverable, evidence snapshot, execution request, execution run, result record, monitoring observation, optimization decision, dry-run record, or external material.

The page is intentionally compact: form, list, selected detail, plan draft, content drafts, asset requests, ComfyUI handoffs, ComfyUI adapter configs, ComfyUI preflights, ComfyUI job requests, ComfyUI execution plans, ComfyUI connection probes, deliverables, evidence snapshots, execution requests, execution runs, results, monitoring observations, optimization decisions, approval gates, safe dry-runs, evidence/handoff links, and action result are visible without requiring operators to understand backend tables.

## Maintainer Flow

Server maintainers can verify the foundation with:

```text
GET /api/v1/commercial-operations
POST /api/v1/commercial-operations
GET /api/v1/commercial-operations/{operation_id}
PATCH /api/v1/commercial-operations/{operation_id}
POST /api/v1/commercial-operations/{operation_id}/plan-draft
GET /api/v1/commercial-operations/{operation_id}/approvals
POST /api/v1/commercial-operations/{operation_id}/approvals
POST /api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/approve
POST /api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/reject
POST /api/v1/commercial-operations/{operation_id}/approvals/{approval_id}/cancel
GET /api/v1/commercial-operations/{operation_id}/dry-runs
POST /api/v1/commercial-operations/{operation_id}/dry-runs
POST /api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/complete
POST /api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/fail
POST /api/v1/commercial-operations/{operation_id}/dry-runs/{dry_run_id}/cancel
GET /api/v1/commercial-operations/{operation_id}/content-drafts
POST /api/v1/commercial-operations/{operation_id}/content-drafts
POST /api/v1/commercial-operations/{operation_id}/content-drafts/generate-rag
PATCH /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}
POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/ready
POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/approve
POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/reject
POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/archive
GET /api/v1/commercial-operations/{operation_id}/asset-requests
POST /api/v1/commercial-operations/{operation_id}/asset-requests
POST /api/v1/commercial-operations/{operation_id}/asset-requests/generate-rag
PATCH /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/ready
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/approve
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/reject
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/prepare
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/fail
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/archive
GET /api/v1/commercial-operations/{operation_id}/comfyui-handoffs
POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs
PATCH /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}
POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/ready
POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/approve
POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/reject
POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/prepare
POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/fail
POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/archive
POST /api/v1/commercial-operations/{operation_id}/comfyui-handoffs/{handoff_id}/preflights
GET /api/v1/commercial-operations/{operation_id}/comfyui-preflights
PATCH /api/v1/commercial-operations/{operation_id}/comfyui-preflights/{preflight_id}
POST /api/v1/commercial-operations/{operation_id}/comfyui-preflights/{preflight_id}/check
POST /api/v1/commercial-operations/{operation_id}/comfyui-preflights/{preflight_id}/fail
POST /api/v1/commercial-operations/{operation_id}/comfyui-preflights/{preflight_id}/archive
GET /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs
PATCH /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs/{config_id}
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs/{config_id}/validate
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs/{config_id}/fail
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs/{config_id}/archive
POST /api/v1/commercial-operations/{operation_id}/comfyui-preflights/{preflight_id}/job-requests
GET /api/v1/commercial-operations/{operation_id}/comfyui-job-requests
PATCH /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}
POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/ready
POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/approve
POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/reject
POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/queue
POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/fail
POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/cancel
POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/archive
POST /api/v1/commercial-operations/{operation_id}/comfyui-job-requests/{job_request_id}/execution-plans
GET /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans
PATCH /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}
POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/ready
POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/approve
POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/reject
POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/simulate
POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/fail
POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/cancel
POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/archive
POST /api/v1/commercial-operations/{operation_id}/comfyui-execution-plans/{execution_plan_id}/connection-probes
GET /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes
PATCH /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}
POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/ready
POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/approve
POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/reject
POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/probe
POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/fail
POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/cancel
POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/archive
POST /api/v1/commercial-operations/{operation_id}/comfyui-connection-probes/{connection_probe_id}/adapter-dispatches
GET /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches
PATCH /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/ready
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/approve
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/reject
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/dispatch
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/fail
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/cancel
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/archive
POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/runtime-gates
GET /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates
PATCH /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/ready
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/approve
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/reject
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/arm
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/fail
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/disable
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/archive
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/runtime-dry-runs
GET /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs
PATCH /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/ready
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/approve
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/reject
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/validate
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/fail
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/cancel
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/archive
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/runtime-activations
GET /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations
PATCH /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/ready
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/approve
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/reject
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/schedule
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/fail
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/cancel
POST /api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations/{runtime_activation_id}/archive
GET /api/v1/comfyui-runtime/health
GET /api/v1/comfyui-runtime/capabilities
GET /api/v1/comfyui-runtime/diagnostics
GET /api/v1/comfyui-runtime/maintenance-runbook
GET /api/v1/comfyui-runtime/diagnostic-snapshots
POST /api/v1/comfyui-runtime/diagnostic-snapshots
GET /api/v1/commercial-operations/{operation_id}/deliverables
POST /api/v1/commercial-operations/{operation_id}/deliverables
PATCH /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/ready
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/approve
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/reject
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/package
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/fail
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/archive
GET /api/v1/commercial-operations/{operation_id}/evidence-snapshots
POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots
POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots/generate-rag
PATCH /api/v1/commercial-operations/{operation_id}/evidence-snapshots/{snapshot_id}
POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots/{snapshot_id}/ready
POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots/{snapshot_id}/approve
POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots/{snapshot_id}/reject
POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots/{snapshot_id}/archive
GET /api/v1/commercial-operations/{operation_id}/execution-requests
POST /api/v1/commercial-operations/{operation_id}/execution-requests
PATCH /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}
POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/ready
POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/approve
POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/reject
POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/prepare
POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/fail
POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/cancel
POST /api/v1/commercial-operations/{operation_id}/execution-requests/{execution_request_id}/archive
GET /api/v1/commercial-operations/{operation_id}/execution-runs
POST /api/v1/commercial-operations/{operation_id}/execution-runs
PATCH /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}
POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/start
POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/succeed
POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/fail
POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/retry
POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/cancel
POST /api/v1/commercial-operations/{operation_id}/execution-runs/{execution_run_id}/archive
GET /api/v1/commercial-operations/{operation_id}/results
POST /api/v1/commercial-operations/{operation_id}/results
PATCH /api/v1/commercial-operations/{operation_id}/results/{result_id}
POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/ready
POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/approve
POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/reject
POST /api/v1/commercial-operations/{operation_id}/results/{result_id}/archive
GET /api/v1/commercial-operations/{operation_id}/monitoring-observations
POST /api/v1/commercial-operations/{operation_id}/monitoring-observations
PATCH /api/v1/commercial-operations/{operation_id}/monitoring-observations/{observation_id}
POST /api/v1/commercial-operations/{operation_id}/monitoring-observations/{observation_id}/ready
POST /api/v1/commercial-operations/{operation_id}/monitoring-observations/{observation_id}/approve
POST /api/v1/commercial-operations/{operation_id}/monitoring-observations/{observation_id}/reject
POST /api/v1/commercial-operations/{operation_id}/monitoring-observations/{observation_id}/archive
GET /api/v1/commercial-operations/{operation_id}/optimization-decisions
POST /api/v1/commercial-operations/{operation_id}/optimization-decisions
PATCH /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}
POST /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/ready
POST /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/approve
POST /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/reject
POST /api/v1/commercial-operations/{operation_id}/optimization-decisions/{optimization_decision_id}/archive
GET /api/v1/commercial-operations/{operation_id}/links
POST /api/v1/commercial-operations/{operation_id}/links
DELETE /api/v1/commercial-operations/{operation_id}/links/{link_id}
```

All routes are workspace-scoped through `X-Workspace-Id`. A record created in one workspace is not visible from another workspace.

Admin Dashboard separates the operator surfaces: `?page=commercial-operations` keeps the goal, plan, content, asset request, approval, delivery, execution, result, monitoring, optimization, evidence, dry-run, and link workflow concise, while `?page=comfyui-operations` hosts the ComfyUI handoff, preflight, adapter config, job request, execution plan, connection probe, adapter dispatch, runtime gate, runtime dry-run, runtime activation, runtime diagnostics, and diagnostic snapshot controls.

## Safety Boundary

Phase 61A is a planning and project-record foundation. Phase 61B is an evidence and handoff-link foundation. Phase 61C is an approval-gate foundation. Phase 61D is a metadata-only dry-run foundation. Phase 61E is a content-draft foundation. Phase 61F is a first-class asset request foundation. Phase 61G is a deliverable packaging and Output Library handoff foundation. Phase 61H is a metadata-only execution request foundation. Phase 61I is a metadata-only execution run and recovery foundation. Phase 61J is an operator-observed commercial result foundation. Phase 61K is an operator-observed monitoring observation foundation. Phase 61L is an operator optimization decision foundation. Phase 61M is an operator-reviewed evidence snapshot foundation. Phase 61N is a draft RAG evidence generation foundation. Phase 61O is a draft RAG content generation foundation. Phase 61P is a draft RAG asset brief foundation. Phase 61Q is a metadata-only ComfyUI handoff foundation. Phase 61R is a metadata-only ComfyUI preflight foundation. Phase 61S is a metadata-only ComfyUI adapter config foundation. Phase 61T is a metadata-only ComfyUI job request foundation. Phase 61U is a metadata-only ComfyUI execution plan foundation. Phase 61V is a metadata-only ComfyUI connection probe foundation. Phase 61W is a metadata-only ComfyUI adapter dispatch foundation. Phase 61X is a metadata-only ComfyUI runtime gate foundation. Phase 61Y is a metadata-only ComfyUI runtime dry-run foundation. Phase 61Z is a metadata-only ComfyUI runtime activation foundation. Phase 62A is a disabled-by-default ComfyUI runtime adapter contract foundation. Phase 62B is a guarded read-only ComfyUI health probe foundation. Phase 62C is a no-network ComfyUI runtime diagnostics foundation. Phase 62D is a no-network ComfyUI runtime diagnostic snapshots foundation. Phase 62E is a no-network ComfyUI runtime maintenance runbook foundation.

It does not publish to social platforms.

It does not execute OpenClaw actions.

It does not run ComfyUI jobs.

It does not call ComfyUI health, prompt, history, upload, or queue endpoints during preflight, job-request preparation, execution-plan simulation, or connection-probe review.

It does not read ComfyUI queues or run read-only queue probes.

It does not upload files to ComfyUI.

It does not store ComfyUI secret values; adapter configs store references only.

It does not ingest knowledge files from evidence snapshots, content draft generation, or asset brief generation, and generated snapshots, content drafts, or asset briefs do not bypass review.

It does not control real accounts.

It does not bypass approval.

It does not claim ROI attribution, account analytics ingestion, or production marketing optimization.

The plan outline may mention future execution surfaces such as OpenClaw, ComfyUI, browser workers, approvals, artifacts, monitoring, and recovery, but those are reviewable plan items only in this phase.

## Next Development Path

Recommended follow-up slices:

1. Extend RAG-generated content, evidence, and asset brief review ergonomics after the draft-only paths are stable.
2. Add guarded ComfyUI job adapter stubs only after RAG-generated asset requests, manual asset request approvals, preparation, deliverable packaging, evidence snapshots, execution request handoff, and execution run recovery are stable.
3. Add guarded OpenClaw/browser worker adapters only after execution requests and execution runs can enforce explicit approval, evidence snapshot, checklist, and target checks.
4. Add monitored analytics adapter stubs that can populate monitoring observations after explicit approval.
5. Add final business-result reporting once real execution and monitored analytics data exist.
