# Current Runtime

Last updated: 2026-06-02

This document records the current real runtime defaults for `E:\ai-operations-system`. Values are based on `app/core/config.py`, `.env.example`, and `docker-compose.yml`.

The repository currently has no committed `.env` file. Without local overrides, the application uses the defaults below.

## Phase 74E Client Inner Panel Alignment

The current customer-machine workbench UI in `worker_console` and `worker_console_desktop` now uses `data-simple-inner-layout="phase-74e-preview-panels"` to align the inner workbench with the Phase 74D preview shell. The visible inner UI is `simple-reference-stage-workspace`, split into overview, planning, text, media, outputs, publish, and `feedback` data-return pages. The workspace uses fixed-height rules with internal scroll areas so long chat, project, workflow, output, publish, and data records do not stretch the full page. The old `simple-conversation-workspace`, `simple-plan-rag-row`, `simple-production-guide`, `simple-approval-workbench`, `simple-approval-output-preview`, `simple-production-details-drawer`, and `simple-production-details-body` remain hidden compatibility anchors. This is a frontend design/runtime surface update only: it does not change ComfyUI runtime gates, submit prompts, run OpenClaw/Playwright, publish, collect analytics, restart services, or bypass approval.

## Phase 74D Client Design Preview Alignment

The current customer-machine workbench UI in `worker_console` and `worker_console_desktop` is aligned with `docs/operation_project_ui_design_preview.html`. The live workbench now includes `simple-design-sidebar-brand`, `simple-design-topbar`, `simple-design-project-switcher`, `simple-design-action-hero`, and `simple-resource-page-links` around the existing operation-project handlers. This is a frontend design/runtime surface update only: it does not change ComfyUI runtime gates, submit prompts, run OpenClaw/Playwright, publish, collect analytics, restart services, or bypass approval.

## Production Server ComfyUI CU130 Runtime

The current production server has a guarded ComfyUI CU130 runtime on `E:\ComfyUI_cu130\ComfyUI` with the AI Ops repository on `D:\ai-operations-system`. The active verification entrypoint is `deployment/windows/verify_comfyui_cu130_aiops.ps1`, which checks the running API, critical video-analysis nodes, key model paths, and regenerates the runtime workflow audit/RAG files.

Current verified state:

- ComfyUI version: `0.21.1`
- PyTorch: `2.9.1+cu130`
- GPU: `NVIDIA GeForce RTX 5090`
- Model audit: 340 executable model files, approximately 950GB
- Workflow audit: 114 JSON workflows
- Runtime RAG file: `deployment/comfyui/commercial_ktv_workflow/cu130_runtime_workflow_rag_documents.jsonl`
- Startup task: `AI Ops ComfyUI CU130`

2026-05-30 environment repair evidence:

- Master ComfyUI is running on `http://127.0.0.1:8188` from `E:\ComfyUI_cu130\ComfyUI` with `--preview-method auto --use-sage-attention --cuda-malloc --enable-manager --disable-auto-launch`.
- GPU1 worker is running on `http://127.0.0.1:8189` through ComfyUI-Distributed Worker 1. It uses `CUDA_VISIBLE_DEVICES=1`, so its `/system_stats` reports local `cuda:0` while `nvidia-smi` maps the process to physical GPU 1.
- Worker 1 uses `--preview-method auto --use-sage-attention --cuda-malloc --user-directory E:/ComfyUI_cu130/ComfyUI/user_worker_8189 --database-url sqlite:///E:/ComfyUI_cu130/ComfyUI/user_worker_8189/comfyui.db`.
- `E:\ComfyUI_cu130\.launcher\preference.json` now has `cuda_allocator_backend=1`, preventing the launcher from starting future sessions with `--disable-cuda-malloc`.
- `deployment/windows/start_comfyui_aiops.ps1` and the copied scheduled-task script at `E:\ComfyUI_cu130\ComfyUI\start-comfyui-aiops.ps1` now default to `--preview-method auto --use-sage-attention --cuda-malloc --enable-manager`.
- `E:\ComfyUI_cu130\ComfyUI\custom_nodes\ComfyUI-Distributed\utils\process.py` now handles Windows `tasklist` output as bytes and tolerates empty output, which fixes the previous `NoneType is not iterable` import failure.
- `E:\ComfyUI_cu130\ComfyUI\custom_nodes\ComfyUI-Distributed\gpu_config.json` has stale `managed_processes` cleared, Worker 1 configured with the formal runtime flags above, and `auto_launch_workers=true` so the worker can come back after the scheduled master startup.
- Verification after restart: `/queue` is empty on both 8188 and 8189, `/distributed/local-worker-status` reports Worker 1 `online=true`, and both endpoints report `cudaMallocAsync`.
- Residual unrelated custom-node failures remain: `raylight` requires `ray`, and `comfyui-easy-sam3` has a `timm.layers.DropPath` import mismatch. They are not on the current Wan/InfiniteTalk video execution path.
- This dual-instance setup does not merge two RTX 5090 cards into one 64GB device. It gives the platform a physical GPU0 master plus physical GPU1 worker foundation for endpoint routing, chunked jobs, or distributed-capable workflows.

The older MuseTalk validation on `E:\ComfyUI` remains historical evidence for a previous digital-human ingestion path, not the current primary ComfyUI project.

Historical MuseTalk validation path: AI Ops guarded ComfyUI video job -> `MuseTalkLoadVideo -> MuseTalk -> PreViewVideo` -> generated MP4 with H.264 video and AAC audio -> `POST /api/v1/digital-humans/video-jobs/{job_id}/comfyui-output-ingestion` -> generated digital-human delivery asset. The validation output was `E:\ComfyUI\output\aiops_ops_story_avatar_aiops_ops_story_avatar.mp4`, with ComfyUI video job `71ac53f3-62e1-4f73-a283-7c3c690ed138`, runtime prompt `7aeebb02-b671-413d-8e67-62d6e42d61f5`, digital-human job `8d8f9e14-096e-42c8-8777-3c06cbcb0f03`, and delivery asset `4c7e6f70-ad87-4d4c-b631-39b559189af7`.

Current server overrides include:

```env
LLM_PROVIDER=local
LOCAL_LLM_MODEL=llama70b
EMBEDDING_DIMENSION=1024
COMFYUI_RUNTIME_PROVIDER=guarded
COMFYUI_RUNTIME_ENABLED=True
COMFYUI_RUNTIME_BASE_URL=http://host.docker.internal:8188
COMFYUI_RUNTIME_ALLOWED_HOSTS=host.docker.internal,127.0.0.1,localhost
COMFYUI_RUNTIME_ALLOW_NETWORK=True
COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=True
COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=True
COMFYUI_VIDEO_GPU_ENDPOINTS=default|http://127.0.0.1:8188|0
BROWSER_ALLOWED_DOMAINS=douyin.com,v.douyin.com,open.douyin.com,iesdouyin.com,amemv.com,localhost,127.0.0.1
DIGITAL_HUMAN_PROVIDER=local_musetalk_liveportrait
DIGITAL_HUMAN_ENABLED=True
DIGITAL_HUMAN_ALLOW_EXTERNAL_API=False
```

Contract tests can override only the endpoint-pool value with `COMFYUI_VIDEO_GPU_ENDPOINTS=default|http://localhost:8188|` so mocked ComfyUI calls remain local and deterministic. That test-only value is not the production server routing contract above.

## Commercial Operations Runtime

Phase 74C Client Reference UI Browser Fixes runtime note: customer-machine workers should see a fixed left rail and a right main workspace that starts at the top of the workbench card. Stage detail buttons now use `openSimpleProductionDetailsAndScroll` and keep `simple-production-details-drawer` available on text/media/output/publish pages, so `查看详情` opens the compact production-flow drawer instead of jumping into hidden maintenance panels. The operations and knowledge pages are mounted behind `operator-page-host` wrappers with `hidden={operatorPage !== ...}`, which preserves the selected project and current `simple-workspace-page-tabs` page after opening RAG upload/review and clicking `返回工作台`. The validated browser path at `http://127.0.0.1:5181/` covered project overview, project entry, stage tabs, production detail opening, and knowledge return context. This remains UI routing only and does not approve records, call ComfyUI, mutate workflow JSON, run OpenClaw/Playwright, publish, collect analytics, or bypass approval.

Phase 74B Client Project Overview Stage Tabs runtime note: customer-machine workers should start from `simple-project-overview-page` in `worker_console` or `worker_console_desktop`, select or create an operation project, then use `simple-workspace-page-tabs` for planning, text tasks, media flow, outputs, and publish. Detail buttons call `openClientProjectRecordsAndScroll`, which maps targets through `simpleWorkspacePageForTarget`, opens parent drawers, and scrolls to the guarded record section. `simple-production-guide` filters stages through `data-guide-step`, and project knowledge upload/review has an explicit `onBackToWorkspace` return path. Visible changes to this UI must be verified in a real browser at `http://127.0.0.1:5181/`; this phase is UI routing only and does not approve records, call ComfyUI, mutate workflow JSON, run OpenClaw/Playwright, publish, collect analytics, or bypass approval.

Phase 74A Client Production Start Guide runtime note: customer-machine workers should use the implementation page `simple-production-guide` as the first production entry after an `OperationPlan` is approved. The guide exposes the ordered path from project material import to production-task approval, ComfyUI workflow selection, content-output registration, selected-output confirmation, and publish-package preparation. The content-output step uses `simple-production-output-form` for the candidate title and file path, preview link, or copy text, instead of requiring a browser prompt. The publish-preparation step can create a reviewable publish package from server `package_blueprints` defaults, but still requires approval before customer-machine execution. This is an operator-click guide only; it does not approve tasks, call ComfyUI, mutate workflow JSON, select outputs without an operator click, run OpenClaw/Playwright, publish, collect analytics, or bypass approval.

Phase 73Z Client Workbench Large Pages runtime note: customer-machine workers should use the planning page for project selection, project knowledge, LLM conversation, operation-plan regeneration, and plan approval. After an `OperationPlan` is approved, the workbench switches to the implementation page for production tasks, ComfyUI workflow selection, output review, publish packages, and metric feedback. This is page organization only; it does not approve tasks, call ComfyUI, mutate workflow JSON, run OpenClaw/Playwright, publish, collect analytics, or bypass approval.

Phase 73Y Project Knowledge and Plan Implementation Gate runtime note: customer-machine workers should treat project knowledge as the current operation project's context in the plan-first UI. Approving an `OperationPlan` through `/operation-plans/{plan_id}/approve` now also asks the Main Agent to derive reviewable implementation `ProductionTask` records. An approved plan is a locked version; changes should create a new version and require approval again. This transition still does not approve tasks, call ComfyUI, mutate workflow JSON, run OpenClaw/Playwright, publish, collect analytics, or bypass approval.

Phase 73X Main Agent LLM operation-plan runtime note: the first plan generated from the customer-machine command workspace should now create an `OperationPlan` whose `plan_metadata.main_agent_advance.plan_generation_source` is `llm` when the configured `LLMClient` provider is reachable and returns parseable structured JSON. If the value is `fallback`, inspect `llm_generation_status`, `llm_error`, `llm_provider`, and `llm_model` before changing frontend wording. Regeneration carries `regeneration_attempt` and rejected-plan context into the prompt. RAG is intentionally marked as `collection_name_only_no_retrieved_chunks` until retrieved knowledge chunks are actually injected into this Main Agent plan prompt.

Phase 73W customer-machine workbench runtime note: the current visible console at `http://127.0.0.1:5181/` must be validated with a real browser after frontend changes that affect project deletion, empty project state, goal submission, approval, or plan rendering. Deleting all projects should leave a stable empty project picker, `0/5` project progress, no stale selected operation, and no old operation-plan card. `refreshCommercialOperationLoop(null)` is the intentional empty-selection path. Submitting a new operating goal should create/select a commercial operation, advance the Main Agent with `plan_first_goal_submit=true`, and render detailed operation-plan sections through `simple-plan-detail-grid` before manual approval.

Phase 61A added the `commercial_operations` table, `CommercialOperationService`, and `/api/v1/commercial-operations` route group. These APIs are workspace-scoped and create reviewable plan outlines only.

Phase 61B adds `commercial_operation_links` and `/api/v1/commercial-operations/{operation_id}/links` so operators can attach evidence and handoff references to an operation. Supported link categories are `conversation`, `artifact`, `task_run`, `workflow_run`, `rag_document`, `knowledge_source`, `approval`, and `external`.

Phase 61C adds `commercial_operation_approvals` and `/api/v1/commercial-operations/{operation_id}/approvals` so operators can request, approve, reject, or cancel human approval for a specific operation plan step. Approval decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61D adds `commercial_operation_dry_runs` and `/api/v1/commercial-operations/{operation_id}/dry-runs` so operators can create, complete, fail, or cancel metadata-only dry-run records from approved approval gates. Dry-run decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61E adds `commercial_operation_content_drafts` and `/api/v1/commercial-operations/{operation_id}/content-drafts` so operators can create, edit, send for review, approve, reject, or archive per-channel content drafts. Draft decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61F adds `commercial_operation_asset_requests` and `/api/v1/commercial-operations/{operation_id}/asset-requests` so operators can create, edit, send for review, approve, reject, prepare, fail, or archive first-class asset requests linked to an operation and optionally a content draft. Asset request decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61G adds `commercial_operation_deliverables` and `/api/v1/commercial-operations/{operation_id}/deliverables` so operators can package approved content drafts and approved/prepared asset requests into reviewable commercial handoff deliverables. Creating a deliverable also creates a linked Output Library artifact with `source_type=commercial_operation`; packaging the deliverable moves that artifact into the packaged stage. Deliverable decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61H adds `commercial_operation_execution_requests` and `/api/v1/commercial-operations/{operation_id}/execution-requests` so operators can create metadata-only future runtime handoff requests from packaged deliverables. Execution request decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61I adds `commercial_operation_execution_runs` and `/api/v1/commercial-operations/{operation_id}/execution-runs` so operators can create, start, complete, fail, retry, cancel, or archive metadata-only run audit and recovery records from prepared execution requests. Execution run decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61J adds `commercial_operation_results` and `/api/v1/commercial-operations/{operation_id}/results` so operators can create, edit, send for review, approve, reject, or archive operator-observed result records from terminal execution runs. Result decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61K adds `commercial_operation_monitoring_observations` and `/api/v1/commercial-operations/{operation_id}/monitoring-observations` so operators can create, edit, send for review, approve, reject, or archive operator-observed monitoring snapshots from approved commercial results. Observation decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61L adds `commercial_operation_optimization_decisions` and `/api/v1/commercial-operations/{operation_id}/optimization-decisions` so operators can create, edit, send for review, approve, reject, or archive operator-decided next actions from approved monitoring observations. Optimization decisions are reflected back into `plan_outline` metadata for operator visibility.

Phase 61M adds `commercial_operation_evidence_snapshots` and `/api/v1/commercial-operations/{operation_id}/evidence-snapshots` so operators can create, edit, send for review, approve, reject, or archive reviewed knowledge/source evidence snapshots from packaged deliverables. Approved snapshot IDs and operator checklists can be attached to execution requests and copied into execution runs for handoff visibility.

Phase 61N adds `/api/v1/commercial-operations/{operation_id}/evidence-snapshots/generate-rag` so operators can create a draft evidence snapshot from existing RAG search results. The generated draft records retrieved chunks, source document IDs, collection/query/search metadata, and explicit forbidden actions.

Phase 61O adds `/api/v1/commercial-operations/{operation_id}/content-drafts/generate-rag` so operators can create a draft content record from existing RAG search results. The generated draft records retrieved chunk source materials, collection/query/search metadata, and explicit forbidden actions.

Phase 61P adds `/api/v1/commercial-operations/{operation_id}/asset-requests/generate-rag` so operators can create a draft asset request brief from existing RAG search results and optional linked content draft context. The generated draft records retrieved chunk source materials, collection/query/search metadata, readiness checks, and explicit forbidden actions.

Phase 61Q adds `commercial_operation_comfyui_handoffs` and `/api/v1/commercial-operations/{operation_id}/comfyui-handoffs` so operators can create, edit, send for review, approve, reject, prepare, fail, or archive metadata-only ComfyUI handoff records from approved/prepared asset requests. Handoff records store prompt payloads, workflow payloads, readiness checks, result/failure notes, and plan-step handoff state without submitting generation jobs.

Phase 61R adds `commercial_operation_comfyui_preflights` and `/api/v1/commercial-operations/{operation_id}/comfyui-preflights` so operators and server maintainers can record endpoint, queue, model, workflow, and guarded adapter readiness for approved/prepared ComfyUI handoffs. Preflight records normalize adapter config back to metadata-only and do not call ComfyUI endpoints or submit queues.

Phase 61S adds `commercial_operation_comfyui_adapter_configs` and `/api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs` so server maintainers can record endpoint, queue, workflow allowlist, model inventory, runtime limits, maintenance notes, and secret references for a future guarded ComfyUI adapter. Adapter config records normalize runtime limits back to metadata-only, can be selected by preflights, and do not store secret values, call ComfyUI endpoints, or submit queues.

Phase 61T adds `commercial_operation_comfyui_job_requests` and `/api/v1/commercial-operations/{operation_id}/comfyui-job-requests` so operators can turn checked preflights into reviewable future queue payloads with safety checks, output expectations, lifecycle decisions, and recovery guidance. Job request records normalize runtime payloads back to metadata-only and do not call ComfyUI endpoints, upload files, submit queues, or generate media.

Phase 61U adds `commercial_operation_comfyui_execution_plans` and `/api/v1/commercial-operations/{operation_id}/comfyui-execution-plans` so operators can turn approved or queued job requests into reviewable metadata-only queue simulation plans with execution steps, simulation checks, operator checklists, rollback guidance, lifecycle decisions, and plan-step execution-plan state. Execution plan records normalize simulation payloads back to metadata-only and do not call ComfyUI endpoints, upload files, submit queues, or generate media.

Phase 61V adds `commercial_operation_comfyui_connection_probes` and `/api/v1/commercial-operations/{operation_id}/comfyui-connection-probes` so operators can turn approved or simulated execution plans into reviewable metadata-only connection probe records with documented health and queue endpoints, readiness checks, sanitized probe payloads, metadata-only health snapshots, metadata-only queue snapshots, lifecycle decisions, and plan-step connection-probe state. Connection probe records normalize probe payloads back to metadata-only and do not call ComfyUI endpoints, read queues, upload files, submit queues, or generate media.

Phase 61W adds `commercial_operation_comfyui_adapter_dispatches` and `/api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches` so operators can turn recorded connection probes into reviewable metadata-only adapter dispatch records with prompt/workflow/queue payloads, sanitized dispatch payloads, guardrails, operator checklists, retry policy, recovery plan, lifecycle decisions, and plan-step dispatch state. Adapter dispatch records normalize dispatch payloads back to metadata-only and do not call ComfyUI endpoints, submit prompts, upload files, submit queues, or generate media.

Phase 61X adds `commercial_operation_comfyui_runtime_gates` and `/api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates` so operators and server maintainers can turn recorded adapter dispatches into reviewable metadata-only runtime gate records with runtime switch metadata, network policy, queue policy, secret-reference policy, approval policy, validation checks, rollback guidance, lifecycle decisions, and plan-step runtime-gate state. Runtime gate records normalize runtime calls, network requests, queue reads/submissions, prompt submissions, uploads, secret lookup/storage, and approval bypass back to disabled.

Phase 61Y adds `commercial_operation_comfyui_runtime_dry_runs` and `/api/v1/commercial-operations/{operation_id}/comfyui-runtime-dry-runs` so operators and server maintainers can turn armed runtime gates into reviewable metadata-only runtime dry-run records with adapter contract metadata, dry-run request fixtures, expected response contracts, explicit server switch policy, validation checks, rollback guidance, lifecycle decisions, and plan-step runtime-dry-run state. Runtime dry-run records normalize adapter imports/calls, runtime calls, server switch enablement, network requests, queue reads/submissions, prompt submissions, uploads, secret lookup/storage, generated media, and approval bypass back to disabled.

Phase 61Z adds `commercial_operation_comfyui_runtime_activations` and `/api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations` so operators and server maintainers can turn validated runtime dry-runs into reviewable metadata-only runtime activation request records with activation request metadata, switch audit records, runtime guardrails, validation checks, rollback guidance, lifecycle decisions, and plan-step runtime-activation state. Runtime activation records normalize adapter imports/calls, runtime calls, server switch enablement, network requests, queue reads/submissions, prompt submissions, uploads, secret lookup/storage, generated media, and approval bypass back to disabled.

Phase 62A adds a disabled-by-default ComfyUI runtime adapter contract: `GET /api/v1/comfyui-runtime/health`, `GET /api/v1/comfyui-runtime/capabilities`, `ComfyUIRuntimeService`, `COMFYUI_RUNTIME_PROVIDER`, `COMFYUI_RUNTIME_ENABLED`, `COMFYUI_RUNTIME_BASE_URL`, `COMFYUI_RUNTIME_TIMEOUT_SECONDS`, `COMFYUI_RUNTIME_ALLOW_NETWORK`, and `COMFYUI_RUNTIME_ALLOWED_HOSTS`. It exposes provider/configuration/allowlist/guardrail state for operators and server maintainers, but it still does not import adapters, call ComfyUI, read queues, submit prompts, upload files, generate media, enable runtime switches, or resolve secrets.

Phase 62B adds a guarded read-only ComfyUI health probe on top of the Phase 62A contract. The health endpoint still performs no network request by default. It attempts exactly one `GET /system_stats` request only when `COMFYUI_RUNTIME_PROVIDER=guarded`, `COMFYUI_RUNTIME_ENABLED=true`, `COMFYUI_RUNTIME_ALLOW_NETWORK=true`, `COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=true`, the base URL host is in `COMFYUI_RUNTIME_ALLOWED_HOSTS`, and the health path is in `COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS`. The probe reports `read_only_probe_enabled`, `read_only_probe_attempted`, `health_path`, `allowed_health_paths`, `probe_status_code`, and `probe_latency_ms`; it still does not import adapters, submit prompts, read queues, submit queues, upload files, generate media, enable runtime switches, mutate runtime configuration, or resolve secrets.

Phase 62C adds `GET /api/v1/comfyui-runtime/diagnostics`, a no-network readiness report for server maintainers. It returns `readiness_status`, `blocking_reasons`, `recommended_actions`, `read_only_probe_ready`, `external_request_attempted=false`, `runtime_calls_enabled=false`, and per-gate checks for `provider_guarded`, `runtime_enabled`, `network_gate`, `base_url_scheme`, `base_url_host_allowlist`, `read_only_probe_gate`, `health_path_allowlist`, and `execution_boundary`. This endpoint never calls ComfyUI; it only explains whether the guarded Phase 62B read-only probe would be ready if an operator refreshed health.

Phase 62D adds `comfyui_runtime_diagnostic_snapshots`, `POST /api/v1/comfyui-runtime/diagnostic-snapshots`, and `GET /api/v1/comfyui-runtime/diagnostic-snapshots` so server maintainers can persist before/after no-network readiness snapshots with operator notes and metadata. Snapshot creation reuses Phase 62C diagnostics and never calls ComfyUI; it records `readiness_status`, `blocking_reasons`, `recommended_actions`, `read_only_probe_ready`, diagnostic checks, forbidden actions, and the full diagnostic payload for audit trails.

Phase 62E adds `GET /api/v1/comfyui-runtime/maintenance-runbook`, a no-network maintainer runbook that reuses Phase 62C diagnostics and returns ordered operator steps, `next_operator_action`, `recovery_actions`, `configuration_summary`, `snapshot_recommended`, disabled actions, and the source diagnostics payload. It never calls ComfyUI; it is a human-readable bridge between raw diagnostics and the next safe maintenance action.

Phase 62F adds `comfyui_runtime_config_change_requests`, `ComfyUIRuntimeConfigChangeRequest`, `POST /api/v1/comfyui-runtime/config-change-requests`, `GET /api/v1/comfyui-runtime/config-change-requests`, and ready/approve/reject/cancel/archive review actions. A request is derived from the Phase 62E runbook and stores current configuration, `requested_changes`, runbook steps, recovery actions, disabled actions, reviewer notes, `change_status`, and `config_mutation_performed=false`. It never writes environment variables, enables runtime switches, restarts services, or calls ComfyUI.

Phase 62G adds `comfyui_runtime_manual_apply_evidence`, `ComfyUIRuntimeManualApplyEvidence`, `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/manual-apply-evidence`, `GET /api/v1/comfyui-runtime/manual-apply-evidence`, and ready/verify/reject/fail/archive review actions. Evidence can only be created from an approved Phase 62F request and records before/after snapshot ids, manual steps, restart evidence, rollback notes, verification notes, no-network diagnostics, `manual_config_applied=true`, `service_restart_reported`, and `api_config_mutation_performed=false`. It never writes environment variables, enables runtime switches, restarts services, mutates runtime configuration through the API, or calls ComfyUI.

Phase 62H adds `comfyui_runtime_post_manual_readiness_checks`, `ComfyUIRuntimePostManualReadinessCheck`, `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/post-manual-readiness-checks`, `GET /api/v1/comfyui-runtime/post-manual-readiness-checks`, and ready/approve/reject/fail/archive review actions. A readiness check can only be created from verified Phase 62G evidence and compares before/after/current readiness, current no-network diagnostics, blockers, recommended actions, `comparison_status`, `guarded_probe_ready`, `health_probe_executed=false`, `external_request_attempted=false`, `runtime_calls_enabled=false`, and `api_config_mutation_performed=false`. It never runs `/system_stats`, writes environment variables, enables runtime switches, restarts services, mutates runtime configuration through the API, or calls ComfyUI.

Phase 62I aligns the customer-machine frontends before additional live probe escalation. `worker_console` and `worker_console_desktop` now expose a simplified workstation/customer operator home with local connection/runtime/heartbeat/recovery status cards, runtime and heartbeat controls, shortcuts for conversation/playbook/approval/output/task/log workflows, setup/help panels, recovery guidance, Chinese/English language switching, and explicit server-vs-client boundary warnings. It does not add live ComfyUI calls, OpenClaw execution, publishing, account control, installer signing, auto-update, captcha bypass, proxy pools, fingerprint bypass, secret resolution, or approval bypass.

Phase 62J adds `comfyui_runtime_guarded_probe_executions`, `ComfyUIRuntimeGuardedProbeExecution`, `POST /api/v1/comfyui-runtime/post-manual-readiness-checks/{check_id}/guarded-probe-executions`, `GET /api/v1/comfyui-runtime/guarded-probe-executions`, ready/approve/reject/fail/cancel/archive review actions, and `POST /api/v1/comfyui-runtime/guarded-probe-executions/{execution_id}/execute`. Creation, listing, and review remain no-network. The Admin Dashboard ComfyUI page auto-loads diagnostics instead of `/health`, so page refresh does not run a probe. The execute endpoint rechecks current no-network diagnostics and then calls only the existing guarded `GET /system_stats` health path when the execution was explicitly approved; it records `external_request_attempted`, `health_probe_executed`, `read_only_probe_attempted`, `probe_status_code`, `probe_latency_ms`, `probe_result_status`, and `probe_response` while keeping `runtime_calls_enabled=false` and `api_config_mutation_performed=false`.

Phase 65A adds the guarded real ComfyUI prompt adapter. `POST /api/v1/comfyui-runtime/prompt-jobs` submits a prompt to ComfyUI `/prompt`, `GET /api/v1/comfyui-runtime/prompt-jobs/{prompt_id}/history` reads `/history/{prompt_id}`, and `GET /api/v1/comfyui-runtime/queue` reads `/queue`. Phase 65B connects approved commercial operation ComfyUI adapter dispatches to that adapter through `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/submit-runtime` and `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/refresh-runtime`. These calls are off by default and require `COMFYUI_RUNTIME_PROVIDER=guarded`, `COMFYUI_RUNTIME_ENABLED=true`, `COMFYUI_RUNTIME_ALLOW_NETWORK=true`, `COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED=true`, allowed host/health path gates, `COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED=true`, `COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS` containing the target path, and commercial approval. The Admin Dashboard ComfyUI tab exposes queue status and a smoke prompt control for maintainers, and Commercial Operations exposes Submit ComfyUI / Refresh output controls on approved dispatches. Local verification submitted an EmptyImage/SaveImage prompt to real ComfyUI on `http://127.0.0.1:8188` and produced a PNG output. Phase 65B does not upload files, download models, resolve secrets, publish, control accounts, mutate configuration, restart services, bypass approvals, or rebuild packages.

Phase 66A adds the ComfyUI video resource line. `POST /api/v1/comfyui-runtime/video-resource-plans` reads guarded `/system_stats` and `/queue`, estimates required free VRAM from resolution, frames, fps, profile, and reserve settings, then returns `admission_status`, `should_submit_now`, `selected_endpoint`, `endpoint_plans`, `selected_gpu`, queue counts, blockers, and recommended actions. `POST /api/v1/comfyui-runtime/prompt-jobs` now accepts `media_type=video` and the same resource fields; video prompts are not submitted to `/prompt` unless the resource plan is admitted. If `COMFYUI_VIDEO_GPU_ENDPOINTS` is configured, Phase 66A treats each entry as a separate ComfyUI instance, checks each instance's GPU and queue state, selects the best admitted endpoint, and submits `/prompt` to that endpoint. Approved commercial ComfyUI adapter dispatches also pass video asset requests through the same admission gate, persist `runtime_base_url`, and keep queued video jobs approved for retry instead of falsely marking them generated. Defaults remain safe: video admission and prompt submission still require the Phase 65A/65B guarded runtime gates plus `COMFYUI_VIDEO_MAX_CONCURRENT_JOBS`, `COMFYUI_VIDEO_QUEUE_PENDING_LIMIT`, `COMFYUI_VIDEO_MIN_FREE_VRAM_MB`, `COMFYUI_VIDEO_DEFAULT_VRAM_ESTIMATE_MB`, and optional `COMFYUI_VIDEO_GPU_ENDPOINTS`. Phase 66A does not upload files, download models, install video workflows, publish, control accounts, mutate runtime configuration, restart services, bypass approvals, or rebuild packages.

Phase 66B adds the ComfyUI Video Job Loop. `POST /api/v1/comfyui-runtime/video-jobs` persists a workspace-scoped video job, runs the Phase 66A GPU/queue admission plan, submits guarded `/prompt` only when admitted, stores `runtime_prompt_id`, `runtime_base_url`, `resource_plan`, `selected_endpoint`, `selected_gpu`, submit/history/queue payloads, `outputs`, `job_status`, `failure_reason`, and `result_summary`, then can refresh through `POST /api/v1/comfyui-runtime/video-jobs/{job_id}/refresh`. `GET /api/v1/comfyui-runtime/video-jobs` and `GET /api/v1/comfyui-runtime/video-jobs/{job_id}` provide the server and client frontends a single recoverable status object for video progress. Defaults still block external calls unless the same guarded runtime and resource gates are enabled. Phase 66B does not upload files, download models, install or mutate ComfyUI workflows, restart services, publish, execute OpenClaw/Playwright account actions, ingest platform analytics, or bypass human approval.

Phase 67A adds the Digital Human Foundation. `GET /api/v1/digital-humans/capabilities` reports provider readiness and disabled actions, `POST /api/v1/digital-humans/assets` stores consent-tracked portrait/material uploads under `DIGITAL_HUMAN_ASSET_DIR`, `GET /api/v1/digital-humans/assets` and `GET /api/v1/digital-humans/assets/{asset_id}` list stored assets, `POST /api/v1/digital-humans/video-jobs` creates a script-based video job plan, `GET /api/v1/digital-humans/video-jobs` and `GET /api/v1/digital-humans/video-jobs/{job_id}` expose recoverable status, `POST /api/v1/digital-humans/video-jobs/{job_id}/refresh` recomputes readiness, and `POST /api/v1/digital-humans/video-jobs/{job_id}/{action}` records approve/reject/cancel decisions. Defaults are `DIGITAL_HUMAN_PROVIDER=mock`, `DIGITAL_HUMAN_ENABLED=False`, and `DIGITAL_HUMAN_ALLOW_EXTERNAL_API=False`; no HeyGen, Tavus, D-ID, local MuseTalk/LivePortrait, or ComfyUI workflow call is made by default. Phase 67A does not publish, execute OpenClaw/Playwright account actions, ingest analytics, mutate runtime configuration, restart services, bypass approvals, install workflows, download models, or rebuild packages.

Phase 67B adds the Digital Human Execution Loop. Approved jobs can call `POST /api/v1/digital-humans/video-jobs/{job_id}/execute` in `mock_render` mode to create a local delivery manifest asset under `DIGITAL_HUMAN_OUTPUT_DIR`, or in `comfyui_handoff` mode to create a guarded `/api/v1/comfyui-runtime/video-jobs` record with GPU/queue admission, selected endpoint/GPU metadata, linked ComfyUI video job id, progress, and recovery details. Responses expose `progress_percent`, `current_stage`, `next_action`, and `linked_comfyui_video_job_id`. Generated placeholder ComfyUI prompts are not submitted by default; submission still requires an operator-supplied real prompt plus the existing guarded ComfyUI runtime gates. Phase 67B does not call HeyGen, Tavus, D-ID, local MuseTalk/LivePortrait by default, publish, execute OpenClaw/Playwright account actions, control accounts, ingest analytics, mutate runtime configuration, restart services, bypass approvals, install workflows, download models, or rebuild packages.

Phase 67D adds Digital Human Workflow Readiness. `GET /api/v1/digital-humans/workflow-templates` and `GET /api/v1/digital-humans/workflow-templates/{template_id}` still expose operator-verifiable ComfyUI workflow contracts such as `liveportrait-musetalk-broll`, and `POST /api/v1/digital-humans/video-jobs/{job_id}/workflow-binding` still binds an authorized portrait plus selected material/reference assets into a reviewable ComfyUI input contract. The new `POST /api/v1/digital-humans/video-jobs/{job_id}/workflow-readiness-check` records imported real ComfyUI graph evidence, installed nodes/models, uploaded bound assets, output watch path, GPU/queue evidence, `workflow_readiness_status`, `workflow_asset_upload_status`, `workflow_output_watch_status`, `workflow_missing_nodes`, and `workflow_missing_models`. Bound contracts can be handed to Phase 67B `comfyui_handoff`, but real prompt submission now requires an operator-supplied real prompt plus the existing guarded ComfyUI runtime gates and a ready workflow-readiness check. Phase 67D does not install workflows, download models, upload files to ComfyUI automatically, mutate runtime configuration, restart services, publish, execute OpenClaw/Playwright account actions, control accounts, ingest analytics, bypass approvals, or rebuild packages.

Phase 67E adds Digital Human Output Ingestion. `POST /api/v1/digital-humans/video-jobs/{job_id}/comfyui-output-ingestion` safely refreshes the linked ComfyUI video job, reads recorded output files, and creates or updates a generated digital-human `video` asset. Responses expose `comfyui_output_ingestion_status`, `delivery_asset_id`, `delivery_asset_status`, `delivery_source_uri`, and `delivery_output_count`; completed ingestions store `digital_human_comfyui_output_ingestion` and `digital_human_comfyui_delivery_asset` outputs. The default refresh polls history and queue but does not resubmit waiting jobs unless `resubmit_if_waiting=true`. Phase 67E does not upload files to ComfyUI, install workflows, download models, mutate runtime configuration, restart services, publish, execute OpenClaw/Playwright account actions, control accounts, ingest analytics, bypass approvals, or rebuild packages.

Phase 62K simplifies the customer-machine consoles after real user feedback. `worker_console` and `worker_console_desktop` now present a Codex-like command surface first: left status rail, central next-step guidance, first-screen conversation input, neutral operational styling, and collapsed advanced maintenance/diagnostics. It preserves local runtime and heartbeat controls, Chinese/English switching, approvals, playbooks, outputs, tasks, logs, and server/client boundary warnings. It does not add live runtime execution beyond existing local worker controls.

Phase 62L Customer Console Task Workbench on `codex/phase-62l-client-task-workbench` adds a customer-console task workbench on top of the simplified command surface. `worker_console` and `worker_console_desktop` now present operating-goal input, suggested next action, pending approvals, active background tasks, failed/recoverable tasks, artifacts, and expandable execution details in one operator-first surface. It remains frontend-only and does not add live runtime execution beyond existing local worker controls.

Phase 62M Customer Console Goal Templates on `codex/phase-62m-client-goal-templates` adds launch content, RAG evidence, asset brief, and page report templates to the same customer-console task workbench. Selecting a template preloads the operating goal and recommended playbook in `worker_console` and `worker_console_desktop`. It remains frontend-only and does not add live runtime execution beyond existing local worker controls.

Phase 62N Customer Console Goal Plan Preview on `codex/phase-62n-client-goal-plan-preview` adds a compact plan preview to the selected customer-console goal template. `worker_console` and `worker_console_desktop` now show planned steps, approval boundary, and expected output before an operator runs the goal. It remains frontend-only and does not add live runtime execution beyond existing local worker controls.

Phase 62O Customer Console Goal Status Tracker on `codex/phase-62o-client-goal-status-tracker` adds a compact lifecycle tracker to the selected customer-console goal. `worker_console` and `worker_console_desktop` now show prepare, approval, execution, recovery, and output stages with current run status, thread id, task id, pending approvals, active tasks, failed/recoverable tasks, and artifacts. It remains frontend-only and does not add live runtime execution beyond existing local worker controls.

Phase 62P Customer Console Simple Operator Mode on `codex/phase-62p-client-simple-operator-mode` adds a compact customer-console default page and a separate knowledge base upload/edit page to `worker_console` and `worker_console_desktop`. The task page shows a goal input, common task chips, visual current progress, and collapsed maintenance details. The knowledge base upload/edit page provides file upload, text add/update, upload queue, document cards, and refresh controls without displaying code or JSON. It remains frontend-only and does not add live runtime execution beyond existing local worker controls or existing RAG ingest APIs.

Phase 62Q Customer Console Knowledge Upload Readiness on `codex/phase-62q-knowledge-upload-readiness` adds knowledge upload readiness to the separate visual knowledge page in `worker_console` and `worker_console_desktop`. It shows connection, collection, queue, and library readiness cards; explains supported PDF/DOCX/TXT/MD/CSV files and the 20 MB file limit; blocks unsupported or oversized files before upload; and gives operators failed retry, individual queue removal, and clear-completed controls. It remains frontend-only and does not add live runtime execution beyond existing local worker controls or existing RAG ingest APIs.

Phase 62R Customer Console Knowledge Activity Timeline on `codex/phase-62r-knowledge-activity-timeline` adds a visual recent activity timeline to the same knowledge page in `worker_console` and `worker_console_desktop`. It records selected file batches, upload success/failure counts, text material saves, manual refreshes, queue item removal, and clear-completed actions with simple status colors and timestamps. It remains frontend-only and does not add live runtime execution beyond existing local worker controls or existing RAG ingest APIs.

Phase 62S Customer Console Knowledge Document Details on `codex/phase-62s-knowledge-document-details` adds a visual document processing overview and selected-document detail panel to the same knowledge page in `worker_console` and `worker_console_desktop`. It shows total/ready/review counts, selected material, source id, collection, status, chunks, created/updated timestamps, and a direct update action without displaying code or JSON. It remains frontend-only and does not add live runtime execution beyond existing local worker controls or existing RAG ingest APIs.

Phase 62T Customer Console Knowledge Search Validation on `codex/phase-62t-knowledge-search-validation` adds a visual validation query panel to the same knowledge page in `worker_console` and `worker_console_desktop`. It uses the existing `/rag/search` API so customer-machine operators can choose hybrid, semantic, or keyword search and see matched snippets, source labels, chunk indexes, score summaries, empty-result guidance, and local activity records without displaying code or JSON. It remains frontend-only and does not add live runtime execution beyond existing local worker controls or existing RAG search APIs.

Phase 62U Customer Console Knowledge Ingestion Status Loop on `codex/phase-62u-knowledge-ingestion-status` adds a visual ingestion status loop to the same knowledge page in `worker_console` and `worker_console_desktop`. It uses existing upload, document list, text ingest, reingest, and RAG search APIs so customer-machine operators can see queued/uploading/processing/search-ready/needs-review counts, processing steps, latest upload results, duplicate-skip notes, source/document ids, chunk counts, failure reasons, refresh/retry actions, and selected-document ingestion status without displaying code or JSON. It remains frontend-only and does not add live runtime execution beyond existing local worker controls or existing RAG APIs.

Phase 62V Customer Console Knowledge Validation Guidance on `codex/phase-62v-knowledge-validation-guidance` adds visual validation guidance to the same knowledge page in `worker_console` and `worker_console_desktop`. It uses existing document list, upload metadata, and RAG search APIs so customer-machine operators can validate selected material or the latest upload with suggested core-content, risk/limits, and execution-note questions, plus one-click fill/run actions, without displaying code or JSON. It remains frontend-only and does not add live runtime execution beyond existing local worker controls or existing RAG APIs.

Phase 62W Customer Console Knowledge Validation Outcomes on `codex/phase-62w-knowledge-validation-outcomes` adds a visual validation outcome card to the same knowledge page in `worker_console` and `worker_console_desktop`. It uses existing RAG search results and local activity records so customer-machine operators can see ready/needs-evidence/needs-review decisions, evidence counts, material context, validation mode, and next-step actions without displaying code or JSON. It remains frontend-only and does not add live runtime execution beyond existing local worker controls or existing RAG APIs.

Phase 62X Customer Console Product Operation Desk on `codex/phase-62x-client-operation-desk` adds a product operation desk to `worker_console` and `worker_console_desktop`. It gives ordinary customer-machine users a visual product operation desk with product/campaign topic input, process status, copy/video/data-analysis/operation-direction deliverables, interrupt/continue controls, knowledge upload access, and explicit OpenClaw/Playwright client-execution positioning. It remains frontend-only and does not execute OpenClaw, run Playwright, publish to social media, control accounts, call ComfyUI, or bypass approval.

Phase 62Y Commercial Operation Loop Protocol on `codex/phase-62y-operation-loop-protocol` adds `GET /api/v1/commercial-operations/{operation_id}/operation-loop`. It aggregates the existing operation, knowledge, content, approval, execution, result, monitoring, and optimization records into one read-only loop summary for server and customer-machine frontends. The endpoint identifies the current stage, next action, blocked reasons, record counts, and the future OpenClaw/Playwright execution protocol without running external actions.

Phase 63A Customer Console Loop Protocol Binding on `codex/phase-63a-client-loop-protocol-binding` connects `worker_console` and `worker_console_desktop` to the commercial operation APIs. Customer-machine operators can create an operation from the current goal, refresh `operation-loop`, and see the shared closed-loop stage, next action, and deliverable progress while still falling back to local task state when no server loop is available.

Phase 63B Customer Console First Draft Bootstrap on `codex/phase-63b-client-first-draft-bootstrap` connects the customer-machine consoles to the next usable loop step. A single action regenerates the commercial operation plan, creates a first content draft, marks it ready for review, creates a human approval gate, and refreshes `operation-loop`. The first draft remains review-only and does not publish or execute external work.

Phase 63C Customer Console Approval and Execution Prep on `codex/phase-63c-client-approval-execution-prep` connects the next customer-machine loop step. `worker_console` and `worker_console_desktop` can approve or reject the pending commercial approval gate, approve the linked content draft, package a deliverable, and create a metadata-only OpenClaw/Playwright execution prep request. The execution prep request remains ready-for-review and does not publish, execute OpenClaw, run Playwright, or control real accounts.

Phase 63D Customer Console Execution Run Review on `codex/phase-63d-client-execution-run-review` connects execution prep to a recoverable customer-machine run record. `worker_console` and `worker_console_desktop` can review the execution prep request, approve/prepare it, create a metadata-only execution run, mark the run started, record failure, and retry failed runs. The run record remains metadata-only and does not publish, execute OpenClaw, run Playwright, or control real accounts.

Phase 63I Customer Console Next-Cycle Result Feedback Loop on `codex/phase-63i-next-cycle-result-feedback-loop` connects next-cycle execution runs back into result, observation, and optimization tracking. `worker_console` and `worker_console_desktop` can prefer next-cycle execution runs, complete metadata-only next-cycle result feedback, create approved result/observation/optimization records, and preserve previous optimization lineage for another iteration. The records remain operator-reviewed and do not publish, ingest platform analytics, auto-optimize, execute OpenClaw, run Playwright, or control real accounts.

Phase 63J Customer Console Client Runtime Preflight on `codex/phase-63j-client-runtime-preflight` connects queued/retrying execution runs to customer-machine runtime readiness. `worker_console` and `worker_console_desktop` can run a client runtime preflight, read local Worker API health/status, record runtime/heartbeat/OpenClaw/browser readiness, and patch the queued execution run with a metadata-only `client_runtime_preflight` payload. The client runtime preflight remains record-only and does not execute OpenClaw, run Playwright, publish, call ComfyUI, ingest platform analytics, or control real accounts.

Phase 63K Customer Console Guarded Adapter Dispatch Handoff on `codex/phase-63k-guarded-adapter-dispatch-handoff` connects client runtime preflight readiness to a guarded adapter handoff record. `worker_console` and `worker_console_desktop` can prefer preflight-ready queued/retrying execution runs, record a metadata-only `guarded_adapter_dispatch_handoff` payload, keep explicit operator start required, and preserve readiness/cycle lineage for later result tracking. The guarded adapter dispatch handoff remains record-only and does not execute OpenClaw, run Playwright, publish, call ComfyUI, ingest platform analytics, or control real accounts.

Customer console phase anchors for `worker_console` and `worker_console_desktop`: Phase 62K Customer Console Codex-like UX Simplification (`codex/phase-62k-customer-console-codex-ux`), Phase 62L Customer Console Task Workbench (`codex/phase-62l-client-task-workbench`), Phase 62M Customer Console Goal Templates (`codex/phase-62m-client-goal-templates`), Phase 62N Customer Console Goal Plan Preview (`codex/phase-62n-client-goal-plan-preview`), Phase 62O Customer Console Goal Status Tracker (`codex/phase-62o-client-goal-status-tracker`), Phase 62P Customer Console Simple Operator Mode (`codex/phase-62p-client-simple-operator-mode`) with the knowledge base upload/edit page, Phase 62Q Customer Console Knowledge Upload Readiness (`codex/phase-62q-knowledge-upload-readiness`) with knowledge upload readiness, Phase 62R Customer Console Knowledge Activity Timeline (`codex/phase-62r-knowledge-activity-timeline`) with knowledge activity timeline, Phase 62S Customer Console Knowledge Document Details (`codex/phase-62s-knowledge-document-details`) with knowledge document details, Phase 62T Customer Console Knowledge Search Validation (`codex/phase-62t-knowledge-search-validation`) with knowledge search validation, Phase 62U Customer Console Knowledge Ingestion Status Loop (`codex/phase-62u-knowledge-ingestion-status`) with knowledge ingestion status loop, Phase 62V Customer Console Knowledge Validation Guidance (`codex/phase-62v-knowledge-validation-guidance`) with knowledge validation guidance, Phase 62W Customer Console Knowledge Validation Outcomes (`codex/phase-62w-knowledge-validation-outcomes`) with knowledge validation outcomes, Phase 62X Customer Console Product Operation Desk (`codex/phase-62x-client-operation-desk`) with the product operation desk, Phase 63A Customer Console Loop Protocol Binding (`codex/phase-63a-client-loop-protocol-binding`) with operation-loop binding, Phase 63B Customer Console First Draft Bootstrap (`codex/phase-63b-client-first-draft-bootstrap`) with first draft approval bootstrap, Phase 63C Customer Console Approval and Execution Prep (`codex/phase-63c-client-approval-execution-prep`) with approval and metadata-only execution prep, Phase 63D Customer Console Execution Run Review (`codex/phase-63d-client-execution-run-review`) with execution run review, Phase 63E Customer Console Result Feedback Loop (`codex/phase-63e-client-result-feedback-loop`) with the minimum usable closed loop, Phase 63F Customer Console Next-Cycle Content Drafts (`codex/phase-63f-next-cycle-content-drafts`) with next-cycle content draft generation, Phase 63G Customer Console Next-Cycle Execution Prep (`codex/phase-63g-next-cycle-execution-prep`) with next-cycle execution prep, Phase 63H Customer Console Next-Cycle Execution Run Review (`codex/phase-63h-next-cycle-execution-run-review`) with next-cycle execution run tracking, Phase 63I Customer Console Next-Cycle Result Feedback Loop (`codex/phase-63i-next-cycle-result-feedback-loop`) with next-cycle result feedback, Phase 63J Customer Console Client Runtime Preflight (`codex/phase-63j-client-runtime-preflight`) with client runtime preflight, Phase 63K Customer Console Guarded Adapter Dispatch Handoff (`codex/phase-63k-guarded-adapter-dispatch-handoff`) with guarded adapter dispatch handoff, Phase 63L-63N Customer Console Execution and Approval Loop (`codex/phase-63l-63n-execution-approval-loop`) with guarded adapter dry-run, client execution queue, and commercial approval center, Phase 63O-63Q Customer Console Publish Result Observation Loop (`codex/phase-63o-63q-publish-result-observation-loop`) with guarded publish handoff, manual publish result, and manual metric observation, Phase 63R-63T Customer Console Publish Metric Improvement Loop (`codex/phase-63r-63t-publish-metric-improvement-loop`) with manual publish metric improvement and publish metric next-cycle draft preparation, Phase 63U-63W Customer Console Improved Draft Re-execution Loop (`codex/phase-63u-63w-improved-draft-reexecution-loop`) with improved draft re-execution and publish metric re-execution prep, Phase 63X-64B Customer Console Closed Loop Delivery Pass (`codex/phase-63x-64b-client-closed-loop-delivery`) with client closed-loop delivery, OpenClaw/Playwright handoff, publish result capture, and next draft generation, Phase 64C Commercial Agent/Skill Orchestration (`codex/phase-64c-commercial-agent-skill-orchestration`) with Agent/Skill panels, Phase 64D Server/Client Frontend Operability Optimization (`codex/phase-64d-frontend-operability-optimization`) with common actions visible and advanced execution/recovery controls folded, and Phase 64E Layout Declutter (`codex/phase-64e-layout-declutter`) with `client-operation-support-drawer`, `commercial-action-result-drawer`, and removal of the duplicate closed-loop delivery panel.

Commercial operations still do not auto-optimize, publish, execute OpenClaw actions, run Browser Worker actions, upload files to ComfyUI, enable runtime server switches, write environment variables, restart services, mutate runtime configuration, store or resolve ComfyUI secret values, control real accounts, ingest platform analytics, claim ROI attribution, upload knowledge through generated evidence snapshots, content drafts, or asset briefs without approval, or bypass approval. Phase 65B permits only approved commercial dispatches to call guarded ComfyUI `/prompt`, `/history/{prompt_id}`, and `/queue` after every explicit runtime gate is enabled, then records prompt/output metadata and prepares linked asset requests when outputs arrive. Phase 66B adds standalone `/comfyui-runtime/video-jobs` records for recoverable video progress. Phase 67A adds standalone `/digital-humans/*` asset and video-job records for portrait/material/script planning. Phase 67B adds approved `/digital-humans/video-jobs/{job_id}/execute` handoff into local delivery assets or guarded ComfyUI video-job records. Phase 67C adds `/digital-humans/workflow-templates` and `/digital-humans/video-jobs/{job_id}/workflow-binding` so digital-human jobs can carry a real ComfyUI workflow contract before execution. Phase 67D adds `/digital-humans/video-jobs/{job_id}/workflow-readiness-check` so imported graph, node/model, upload, output-watch, and GPU evidence are recorded before real prompt submission. Phase 67E adds `/digital-humans/video-jobs/{job_id}/comfyui-output-ingestion`, `comfyui_output_ingestion_status`, `delivery_asset_id`, `delivery_asset_status`, `delivery_source_uri`, and `delivery_output_count` so recorded ComfyUI outputs become reviewable digital-human delivery assets while provider execution remains mock/disabled by default. The next runtime step remains monitored analytics adapters, explicit provider adapters, and later guarded live OpenClaw/Playwright work.

## Provider Defaults

| Key | Current default | Meaning |
| --- | --- | --- |
| `LLM_PROVIDER` | `mock` | Default LLM provider. Does not call a real model. |
| `LOCAL_LLM_BASE_URL` | `http://host.docker.internal:11434` | Ollama base URL for local LLM mode. |
| `LOCAL_LLM_MODEL` | `mistral` | Ollama local LLM model. |
| `EMBEDDING_PROVIDER` | `mock` | Default embedding provider. Does not call a real embedding model. |
| `EMBEDDING_DIMENSION` | `384` | Mock embedding dimension. |
| `LOCAL_EMBEDDING_BASE_URL` | `http://host.docker.internal:11434` | Ollama base URL for local embedding mode. |
| `LOCAL_EMBEDDING_MODEL` | `bge-m3` | Ollama local embedding model. |
| `RERANKER_PROVIDER` | `mock` | Default reranker provider. |
| `LOCAL_RERANKER_BASE_URL` | `http://host.docker.internal:8002` | Local reranker worker endpoint. |
| `LOCAL_RERANKER_MODEL` | `bge-m3-embedding-reranker` | Local reranker runtime label. |
| `LOCAL_RERANKER_ALLOW_FALLBACK` | `true` | Development fallback to mock scores when the local reranker is unavailable. Production must set `false`. |
| `BROWSER_PROVIDER` | `mock` | Default Browser Adapter provider. Does not start a real browser. |
| `BROWSER_TIMEOUT_SECONDS` | `30.0` | Browser action timeout for Playwright local mode. |
| `BROWSER_HEADLESS` | `True` | Runs Chromium headless in Playwright local mode. |
| `BROWSER_TYPE` | `chromium` | Browser type used by Playwright local mode. |
| `BROWSER_VIEWPORT_WIDTH` | `1280` | Default browser viewport width. |
| `BROWSER_VIEWPORT_HEIGHT` | `720` | Default browser viewport height. |
| `BROWSER_SCREENSHOT_DIR` | `screenshots` | Host/container screenshot storage root. |
| `BROWSER_RUNTIME_SCREENSHOT_DIR` | `storage/browser_screenshots` | Phase 34 remote browser runtime screenshot storage root. |
| `BROWSER_RUNTIME_SNAPSHOT_DIR` | `storage/browser_runtime_snapshots` | Phase 35A page/text/error/replay metadata snapshot storage root. |
| `BROWSER_PROFILE_ROOT` | `worker/profiles` | API-side profile path root stored on `browser_profiles.profile_path`. |
| `BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS` | `1800` | Stale profile lock recovery threshold. |
| `BROWSER_PROFILE_BACKUP_ENABLED` | `True` | Enables profile zip backup APIs. |
| `BROWSER_PROFILE_MAX_BACKUPS` | `3` | Maximum retained backups per profile. |
| `BROWSER_PROFILE_UNUSED_DAYS` | `30` | Unused profile cleanup age threshold. |
| `BROWSER_PROFILE_BACKUP_ROOT` | `worker/profile_backups` | Profile backup zip storage root. |
| `BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS` | `900` | Human-in-the-loop browser control timeout. |
| `BROWSER_UI_ACCESS_TIMEOUT_SECONDS` | `900` | Browser UI Access Placeholder token expiry timeout. |
| `BROWSER_WORKER_AUTH_ENABLED` | `True` | Enables Browser Worker signed-request authentication plumbing. |
| `BROWSER_WORKER_AUTH_STRICT` | `False` | Local development mode accepts unsigned worker runtime calls when no shared secret is configured. |
| `BROWSER_ALLOWED_DOMAINS` | `example.com,localhost,127.0.0.1` | Default allowed browser navigation domains. |
| `BROWSER_BLOCKED_DOMAINS` | `` | Optional blocked browser navigation domains. |
| `BROWSER_ALLOW_EXTERNAL_DOMAINS` | `False` | Default policy blocks arbitrary external browser navigation. |
| `BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS` | `30.0` | Remote Browser Worker client timeout. |
| `BROWSER_WORKER_RETRY_COUNT` | `2` | Remote Browser Worker client retry count. |
| `BROWSER_WORKER_DEFAULT_URL` | `http://browser-worker:9100` | Default Docker network URL for the independent Phase 20 `browser-worker` service. |
| `BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS` | `60` | Worker heartbeat staleness threshold. |
| `BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS` | `30` | Intended worker health monitor interval. |
| `BROWSER_SESSION_TIMEOUT_SECONDS` | `1800` | Browser session stale timeout used by cleanup. |
| `BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS` | `300` | Intended browser session cleanup interval. |
| `BROWSER_ACTION_TIMEOUT_SECONDS` | `60.0` | Remote browser action timeout. |
| `BROWSER_ACTION_RETRY_COUNT` | `2` | Remote browser action retry count. |
| `BROWSER_ACTION_RETRY_BACKOFF_SECONDS` | `2.0` | Remote browser action retry backoff seconds. |
| `SCREENSHOT_RETENTION_DAYS` | `7` | Default screenshot cleanup retention. |
| `OPENCLAW_PROVIDER` | `mock` | OpenClaw worker adapter provider. Current default is mock only. |
| `OPENCLAW_ENABLED` | `True` | Enables the OpenClaw adapter foundation APIs and tool. |
| `OPENCLAW_ACTION_TIMEOUT_SECONDS` | `60.0` | Timeout for OpenClaw worker runtime calls. |
| `COMFYUI_RUNTIME_PROVIDER` | `disabled` | ComfyUI runtime adapter provider. Phase 65A keeps the default disabled. |
| `COMFYUI_RUNTIME_ENABLED` | `False` | Master switch for future ComfyUI runtime adapter work. Current default blocks runtime calls. |
| `COMFYUI_RUNTIME_BASE_URL` | `http://127.0.0.1:8188` | Guarded ComfyUI base URL, reported by default and used only by the explicit read-only probe gate. |
| `COMFYUI_RUNTIME_TIMEOUT_SECONDS` | `30.0` | ComfyUI read-only probe timeout when every explicit gate is enabled. |
| `COMFYUI_RUNTIME_ALLOW_NETWORK` | `False` | Explicit network-call gate. Current default prevents external requests. |
| `COMFYUI_RUNTIME_ALLOWED_HOSTS` | `127.0.0.1,localhost` | Host allowlist required before the read-only health probe can be attempted. |
| `COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED` | `False` | Final explicit gate for the Phase 62B `GET /system_stats` read-only health probe; Phase 62C diagnostics, Phase 62D snapshots, Phase 62E maintenance runbook, Phase 62F config change requests, Phase 62G manual apply evidence, Phase 62H post-manual readiness checks, and Phase 62J guarded probe execution creation/execute readiness checks report whether this gate blocks readiness. |
| `COMFYUI_RUNTIME_HEALTH_PATH` | `/system_stats` | Read-only ComfyUI health path candidate. It must also be listed in `COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS`. |
| `COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS` | `/system_stats` | Exact path allowlist for Phase 62B read-only health probes; Phase 62C diagnostics, Phase 62D snapshots, Phase 62E maintenance runbook, Phase 62F config change requests, Phase 62G manual apply evidence, Phase 62H post-manual readiness checks, and Phase 62J guarded probe executions report health path allowlist failures before any execute call can proceed. |
| `COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED` | `False` | Final explicit gate before Phase 65A submits real `/prompt` jobs or reads execution paths. |
| `COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS` | `/prompt,/history,/queue` | Exact path allowlist for Phase 65A guarded prompt submission, prompt history, and queue reads. |
| `COMFYUI_VIDEO_MAX_CONCURRENT_JOBS` | `1` | Maximum running video jobs allowed per ComfyUI endpoint before a video request is queued. |
| `COMFYUI_VIDEO_QUEUE_PENDING_LIMIT` | `2` | Maximum pending queue length allowed per ComfyUI endpoint before a video request is queued. |
| `COMFYUI_VIDEO_MIN_FREE_VRAM_MB` | `2048` | Reserve VRAM added to the video estimate before admission. |
| `COMFYUI_VIDEO_DEFAULT_VRAM_ESTIMATE_MB` | `8192` | Default video VRAM estimate floor when the request does not provide an explicit estimate. |
| `COMFYUI_VIDEO_GPU_ENDPOINTS` | empty | Optional semicolon-separated endpoint pool for dynamic video routing, for example `gpu0|http://127.0.0.1:8188|0;gpu1|http://127.0.0.1:8189|0`. Each endpoint should be a separate ComfyUI process pinned to the intended GPU by the maintainer. |
| `DIGITAL_HUMAN_PROVIDER` | `mock` | Digital human provider selector. Current Phase 67E behavior supports local delivery manifests, guarded ComfyUI handoff, reviewable workflow binding, operator-recorded workflow readiness, and ComfyUI output ingestion while external provider calls remain disabled by default. |
| `DIGITAL_HUMAN_ENABLED` | `False` | Master switch for future digital human provider execution. Current default keeps execution disabled. |
| `DIGITAL_HUMAN_ALLOW_EXTERNAL_API` | `False` | External digital human provider API gate. Current default blocks HeyGen/Tavus/D-ID/local-provider calls. |
| `DIGITAL_HUMAN_ASSET_DIR` | `storage/digital_human_assets` | Server-side storage root for uploaded portrait and material assets. |
| `DIGITAL_HUMAN_OUTPUT_DIR` | `storage/digital_human_outputs` | Server-side storage root for generated digital-human delivery manifests and local handoff assets. |
| `DIGITAL_HUMAN_DEFAULT_VOICE_ID` | `zh-CN-default` | Default voice id copied into new digital human video jobs when no voice is supplied. |
| `DIGITAL_HUMAN_DEFAULT_ASPECT_RATIO` | `9:16` | Default aspect ratio copied into new digital human video jobs when no ratio is supplied. |

## Search Defaults

| Key | Current default | Meaning |
| --- | --- | --- |
| `DEFAULT_SEARCH_MODE` | `hybrid` | Default search mode. |
| `DENSE_TOP_K` | `20` | Dense candidate count. |
| `KEYWORD_TOP_K` | `20` | Keyword candidate count. |
| `FINAL_TOP_K` | `5` | Final search response count. |
| `RERANK_TOP_N` | `5` | Agentic RAG context count after reranking. |

Current retrieval chain:

```text
Dense Vector Search
+ Keyword Search
-> Hybrid Merge
-> Reranker
-> LLM
```

## File Upload Defaults

| Key | Current default | Meaning |
| --- | --- | --- |
| `MAX_UPLOAD_FILE_SIZE_MB` | `20` | Maximum uploaded file size. |
| `UPLOAD_TEMP_DIR` | `/tmp/aiops_uploads` | Temporary upload directory inside the API container. |
| `ALLOWED_FILE_TYPES` | `pdf,docx,txt,md,csv` | Supported upload extensions. |

Supported in Phase 11:

- PDF
- DOCX
- TXT
- MD
- CSV

Not implemented:

- PPTX
- XLSX
- OCR
- Image parsing

## Task Reliability Runtime

Phase 12 does not add new environment variables. It adds runtime tables and APIs:

- `task_events`
- `task_logs`
- `tasks.duration_ms`
- `POST /api/v1/tasks/{task_id}/cancel`
- `POST /api/v1/tasks/{task_id}/retry`
- `GET /api/v1/tasks/{task_id}/events`
- `GET /api/v1/tasks/{task_id}/logs`
- `GET /api/v1/observability/summary`

Supported task status values:

```text
pending
running
retry
failed
completed
cancelled
timeout
```

All task control, events, logs, and summary APIs require `X-Workspace-Id`.

## Tool Calling Runtime

Phase 13 does not add new environment variables. Tool Calling is enabled through code-level builtin registration.

Runtime table:

- `tool_call_logs`

Core APIs:

- `GET /api/v1/tools`
- `GET /api/v1/tools/{tool_name}`
- `POST /api/v1/tools/{tool_name}/execute`
- `GET /api/v1/tool-calls`

Builtin tools:

| Tool | Status | Scope |
| --- | --- | --- |
| `rag_search_tool` | completed | Calls current Hybrid Search + Reranker. |
| `file_search_tool` | completed | Queries `documents` metadata inside the current workspace. |
| `create_task_tool` | completed | Creates a task in the current workspace. |
| `get_task_status_tool` | completed | Reads task status in the current workspace. |
| `current_runtime_tool` | completed | Returns provider/search/upload settings and reads `CURRENT_RUNTIME.md` when available. |
| `openclaw_tool` | completed foundation | Calls the mock OpenClaw worker adapter through registered Browser Workers. |

All tool execution and tool call log APIs require `X-Workspace-Id`.

Current limitations:

- `browser_tool` is available and can use the configured BrowserProvider.
- `openclaw_tool` is available as a mock/placeholder worker adapter only; it does not call real OpenClaw.
- No Selenium or external API tools.
- No autonomous planner, ReAct loop, or LLM-native function calling.
- Tool enable/disable and permission scopes exist at Registry level, but no management API or full RBAC is implemented yet.

## Memory Runtime

Phase 14 does not add new environment variables. Memory is enabled through the backend service and database tables.

Runtime tables:

- `conversation_sessions`
- `conversation_messages`
- `agent_memories`
- `memory_operation_logs`

Core APIs:

- `POST /api/v1/memory/sessions`
- `GET /api/v1/memory/sessions`
- `GET /api/v1/memory/sessions/{session_id}`
- `POST /api/v1/memory/messages`
- `GET /api/v1/memory/messages/{session_id}`
- `POST /api/v1/memory/memories`
- `GET /api/v1/memory/memories`
- `DELETE /api/v1/memory/memories/{memory_id}`

Supported message roles:

```text
system
user
assistant
tool
```

Supported memory types:

```text
short_term
long_term
task_memory
retrieval_memory
```

Current memory retrieval uses PostgreSQL text matching over `agent_memories.content`. Agentic RAG `debug=true` now returns `session_id`, `recent_messages_count`, `retrieved_memories_count`, `recent_messages`, `retrieved_memories`, and `memory_trace`.

Current limitations:

- No vector memory.
- No graph memory.
- No autonomous memory planning.
- No personality memory.
- `summarize_session` is a lightweight deterministic text summary and does not call an LLM.

## Multi-Agent Runtime

Phase 15 does not add new environment variables. Multi-Agent is enabled through code-level `AgentRegistry` registration and database-backed run tracking.

Runtime tables:

- `agent_runs`
- `agent_messages`
- `agent_handoffs`

Core APIs:

- `GET /api/v1/agents/registry`
- `POST /api/v1/multi-agent/runs`
- `GET /api/v1/multi-agent/runs`
- `GET /api/v1/multi-agent/runs/{run_id}`
- `POST /api/v1/multi-agent/runs/{run_id}/execute-chain`
- `GET /api/v1/multi-agent/runs/{run_id}/messages`
- `GET /api/v1/multi-agent/runs/{run_id}/handoffs`

Registered agents:

| Agent | Status | Runtime role |
| --- | --- | --- |
| `content_planner` | completed foundation | Lightweight mock planner for content chain inputs. |
| `rag_agent` | completed foundation | Wraps `AgenticRAGOrchestrator`. |
| `content_agent` | completed foundation | Wraps `ContentAgent`. |
| `review_agent` | completed foundation | Lightweight mock reviewer. |
| `runtime_agent` | completed foundation | Reads runtime information through `current_runtime_tool`. |
| `tool_agent` | completed foundation | Calls existing `ToolRegistry` builtin tools. |

Current fixed Agent Chain:

```text
content_planner
-> rag_agent
-> content_agent
-> review_agent
```

All Multi-Agent APIs require `X-Workspace-Id`. `X-User-Id` is optional and is stored on `agent_runs.user_id` when provided.

Current limitations:

- No autonomous planner.
- No ReAct loop.
- No Browser Agent.
- No Playwright, OpenClaw, Selenium, or external platform automation.
- Agent enable/disable is currently code-level registry state, not a management API.

## Planning Runtime

Phase 16 does not add new environment variables. Planning is enabled through `SimplePlannerAgent`, `PlanningService`, `AgentRegistry`, and `ToolRegistry`.

Runtime tables:

- `plans`
- `plan_steps`
- `plan_reviews`

Core APIs:

- `POST /api/v1/plans`
- `GET /api/v1/plans`
- `GET /api/v1/plans/{plan_id}`
- `POST /api/v1/plans/{plan_id}/execute`
- `POST /api/v1/plans/{plan_id}/cancel`
- `GET /api/v1/plans/{plan_id}/steps`
- `GET /api/v1/plans/{plan_id}/reviews`

Supported plan status values:

```text
pending
planning
executing
completed
failed
cancelled
```

Supported plan step status values:

```text
pending
running
completed
failed
skipped
```

Current Plan Execution Flow:

```text
SimplePlannerAgent
-> plans / plan_steps
-> AgentRegistry or ToolRegistry
-> step output / duration_ms / error
-> plan_reviews
-> plan status + memory_trace
```

Current limitations:

- Planning is rule-based only.
- No autonomous AGI planner.
- No tree-of-thought.
- No recursive planning.
- No infinite Agent loop.
- No ReAct.
- No Browser Agent, Playwright, OpenClaw, Selenium, or external platform automation.

## Browser Runtime

Phase 17 adds Browser Automation Adapter Foundation. Phase 18 adds `PlaywrightLocalProvider` for bounded local Chromium execution.
Phase 19 adds `RemoteBrowserProvider` and the in-project Remote Browser Worker mock runtime.
Phase 20 adds a real independent `browser-worker` FastAPI service backed by Playwright Chromium.
Phase 21 adds Browser Worker Reliability: health monitoring, capacity tracking, least loaded worker selection, stale session cleanup, action retry, and manual screenshot cleanup.
Phase 22 adds Persistent Browser Profile Foundation: `browser_profiles`, profile lock/release, session profile binding, and worker-side `launch_persistent_context`.
Phase 23 adds Browser Profile Health & Recovery: `BrowserProfileHealthService`, `BrowserProfileBackupService`, `BrowserProfileCleanupService`, `browser_profile_usage_logs`, health fields, `health/summary`, stale lock recovery, profile backup, and profile cleanup.
Phase 24 adds Human-in-the-loop Browser Control: `BrowserHumanControlService`, `browser_human_control_sessions`, `browser_human_control_events`, session paused/resumed fields, worker metadata-level `/human-control/*` routes, and `browser_tool` actions `request_human_control` / `complete_human_control`.
Phase 25 adds Browser Worker UI Access Placeholder: `BrowserUIAccessService`, `browser_ui_access_sessions`, access token hash storage, placeholder URL generation, `/ui-access/capabilities`, and `browser_tool` actions `create_ui_access` / `revoke_ui_access`. It does not provide real VNC, noVNC, DevTools UI, live browser video, login, captcha handling, or platform automation.
Phase 26 adds Browser Worker Security & Access Control: `BrowserWorkerAuthService`, signed worker request headers, worker secret hash storage, UI Access Scope validation, `BrowserActionPolicyService`, `BrowserSecurityAuditLog`, and `browser_security_audit_logs`. It does not provide real social-platform account security, login, proxy, fingerprint, captcha, or platform automation.
Phase 27 adds Customer Machine Worker Bootstrap through the local `worker_client` package. It does not add new API Server environment variables; it adds customer-machine config, CLI, registration, heartbeat, and local runtime behavior.
Phase 28 adds OpenClaw Worker Adapter Foundation: `worker_client/openclaw`, `BaseOpenClawProvider`, `MockOpenClawProvider`, `OpenClawRuntime`, server-side `OpenClawWorkerClient`, `openclaw_tool`, `openclaw_action_logs`, and `/api/v1/openclaw/*` APIs. It is mock/placeholder only and does not call real OpenClaw or perform platform automation.

Runtime setting:

```text
BROWSER_PROVIDER=mock
BROWSER_TIMEOUT_SECONDS=30.0
BROWSER_HEADLESS=True
BROWSER_TYPE=chromium
BROWSER_VIEWPORT_WIDTH=1280
BROWSER_VIEWPORT_HEIGHT=720
BROWSER_SCREENSHOT_DIR=screenshots
BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
BROWSER_PROFILE_ROOT=worker/profiles
BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS=1800
BROWSER_PROFILE_BACKUP_ENABLED=True
BROWSER_PROFILE_MAX_BACKUPS=3
BROWSER_PROFILE_UNUSED_DAYS=30
BROWSER_PROFILE_BACKUP_ROOT=worker/profile_backups
BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS=900
BROWSER_UI_ACCESS_TIMEOUT_SECONDS=900
BROWSER_WORKER_AUTH_ENABLED=True
BROWSER_WORKER_AUTH_STRICT=False
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=False
BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30.0
BROWSER_WORKER_RETRY_COUNT=2
BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100
BROWSER_WORKER_AUTH_ENABLED=true
BROWSER_WORKER_AUTH_STRICT=false
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=false
BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60
BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS=30
BROWSER_SESSION_TIMEOUT_SECONDS=1800
BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS=300
BROWSER_ACTION_TIMEOUT_SECONDS=60.0
BROWSER_ACTION_RETRY_COUNT=2
BROWSER_ACTION_RETRY_BACKOFF_SECONDS=2.0
SCREENSHOT_RETENTION_DAYS=7
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=True
OPENCLAW_ACTION_TIMEOUT_SECONDS=60.0
```

Phase 20 worker service runtime:

```text
WORKER_HOST=0.0.0.0
WORKER_PORT=9100
WORKER_TIMEOUT_SECONDS=30
WORKER_HEADLESS=true
WORKER_BROWSER_TYPE=chromium
WORKER_SCREENSHOT_DIR=worker/screenshots
WORKER_PROFILE_DIR=worker/profiles
WORKER_VIEWPORT_WIDTH=1280
WORKER_VIEWPORT_HEIGHT=720
BROWSER_WORKER_PORT=9100
```

Runtime tables:

- `browser_sessions`
- `browser_actions`
- `browser_action_logs`
- `browser_profiles`
- `browser_profile_usage_logs`

Core APIs:

- `POST /api/v1/browser/sessions`
- `POST /api/v1/browser/sessions/{session_id}/close`
- `POST /api/v1/browser/profiles`
- `GET /api/v1/browser/profiles`
- `POST /api/v1/browser/profiles/recover-stale-locks`
- `POST /api/v1/browser/profiles/cleanup`
- `GET /api/v1/browser/profiles/health/summary`
- `GET /api/v1/browser/profiles/{profile_id}`
- `POST /api/v1/browser/profiles/{profile_id}/health-check`
- `POST /api/v1/browser/profiles/{profile_id}/backup`
- `GET /api/v1/browser/profiles/{profile_id}/backups`
- `POST /api/v1/browser/profiles/{profile_id}/restore`
- `GET /api/v1/browser/profiles/{profile_id}/usage-logs`
- `POST /api/v1/browser/profiles/{profile_id}/lock`
- `POST /api/v1/browser/profiles/{profile_id}/release`
- `DELETE /api/v1/browser/profiles/{profile_id}`
- `POST /api/v1/browser/human-control/request`
- `GET /api/v1/browser/human-control`
- `GET /api/v1/browser/human-control/{control_session_id}`
- `POST /api/v1/browser/human-control/{control_session_id}/approve`
- `POST /api/v1/browser/human-control/{control_session_id}/start`
- `POST /api/v1/browser/human-control/{control_session_id}/complete`
- `POST /api/v1/browser/human-control/{control_session_id}/cancel`
- `GET /api/v1/browser/human-control/{control_session_id}/events`
- `POST /api/v1/browser/ui-access`
- `GET /api/v1/browser/ui-access/{access_session_id}`
- `POST /api/v1/browser/ui-access/{access_session_id}/revoke`
- `POST /api/v1/browser/ui-access/expire`
- `GET /api/v1/browser/ui-access/{access_session_id}/validate`
- `GET /api/v1/browser/sessions`
- `POST /api/v1/browser/actions`
- `GET /api/v1/browser/actions/{session_id}`
- `GET /api/v1/browser/screenshot/{session_id}/{filename}`
- `GET /api/v1/browser/logs/{session_id}`
- `POST /api/v1/browser-workers/register`
- `POST /api/v1/browser-workers/{worker_id}/heartbeat`
- `GET /api/v1/browser-workers`
- `GET /api/v1/browser-workers/health/summary`
- `GET /api/v1/browser-workers/available`
- `POST /api/v1/browser-workers/{worker_id}/mark-offline`
- `POST /api/v1/browser-workers/cleanup-sessions`
- `GET /api/v1/browser-workers/{worker_id}/sessions`
- `POST /api/v1/browser/screenshots/cleanup`
- `GET /api/v1/browser-worker-runtime/health`
- `POST /api/v1/browser-worker-runtime/sessions`
- `POST /api/v1/browser-worker-runtime/actions`
- `POST /api/v1/browser-worker-runtime/sessions/{session_id}/close`
- `POST /api/v1/browser-worker-runtime/human-control/start`
- `POST /api/v1/browser-worker-runtime/human-control/complete`
- `GET /api/v1/browser-worker-runtime/human-control/status/{session_id}`
- `GET /api/v1/browser-worker-runtime/ui-access/capabilities`
- `GET /api/v1/browser-worker-runtime/openclaw/health`
- `GET /api/v1/browser-worker-runtime/openclaw/capabilities`
- `POST /api/v1/browser-worker-runtime/openclaw/actions`
- `GET /api/v1/openclaw/health`
- `GET /api/v1/openclaw/capabilities`
- `POST /api/v1/openclaw/actions`

Current browser provider state:

- `MockBrowserProvider` is completed and active by default.
- `PlaywrightBrowserProvider` is a placeholder only.
- `PlaywrightLocalProvider` is completed for local Chromium smoke tests through `BROWSER_PROVIDER=playwright_local`.
- `RemoteBrowserProvider` is completed as a protocol foundation through `BROWSER_PROVIDER=remote`.
- `BrowserWorkerClient` dispatches to registered worker `base_url` values.
- `Worker Runtime Mock` is available inside this API process at `/api/v1/browser-worker-runtime`.
- `browser_tool` can execute `navigate`, `click`, `type_text`, `screenshot`, `get_page_content`, `request_human_control`, `complete_human_control`, `create_ui_access`, and `revoke_ui_access` through the configured provider/services.
- Planning steps can target `tool_name=browser_tool`.

Playwright local runtime fields:

- `browser_sessions.browser_id`
- `browser_sessions.page_id`
- `browser_sessions.profile_id`
- `browser_sessions.profile_path`
- `browser_sessions.persistent_context_enabled`
- `browser_sessions.provider_session_metadata`
- `browser_actions.selector`
- `browser_actions.target_url`
- `browser_actions.screenshot_path`
- `browser_actions.page_title`

Screenshot System:

```text
screenshots/{workspace_id}/{session_id}/{filename}.png
```

Persistent Profile System:

```text
browser_profiles
-> profile_id / profile_path
-> Profile Lock by locked_by_session_id
-> BrowserSession persistent_context_enabled=true
-> browser-worker launch_persistent_context
-> worker/profiles/{workspace_id}/{profile_id}
-> Profile Release on session close
```

Phase 23 health fields:

```text
health_status
last_health_check_at
last_error
usage_count
corrupted_at
backup_path
last_backup_at
browser_profile_usage_logs
```

Phase 23 services:

```text
BrowserProfileHealthService
BrowserProfileBackupService
BrowserProfileCleanupService
stale lock recovery
profile backup
profile cleanup
```

Phase 24 human control fields:

```text
browser_human_control_sessions
browser_human_control_events
human_control_status
human_control_session_id
paused_at
resumed_at
```

Phase 24 service and actions:

```text
BrowserHumanControlService
request_human_control
complete_human_control
BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS
```

Phase 25 UI access fields:

```text
browser_ui_access_sessions
access_token_hash
scopes
one_time
used_at
revoked_reason
client_ip
user_agent
remote_control_url
live_view_url
devtools_url
BROWSER_UI_ACCESS_TIMEOUT_SECONDS
```

Phase 25 service and actions:

```text
BrowserUIAccessService
create_ui_access
revoke_ui_access
access token hash
placeholder URL
```

Phase 26 Browser Worker Security fields:

```text
worker_secret_hash
api_key_hash
last_auth_at
auth_status
allowed_actions
allowed_domains
browser_security_audit_logs
BrowserSecurityAuditLog
```

Phase 26 services and policy:

```text
BrowserWorkerAuthService
signed worker request
X-Worker-Signature
X-Worker-Timestamp
X-Worker-Nonce
BrowserActionPolicyService
UI Access Scope
BROWSER_WORKER_AUTH_ENABLED=True
BROWSER_WORKER_AUTH_STRICT=False
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=False
```

Phase 27 Worker Client runtime:

```text
worker_client
worker_config.example.yaml
worker_config.yaml
worker_state.json
python -m worker_client.cli register
python -m worker_client.cli heartbeat
python -m worker_client.cli serve
python -m worker_client.cli start
registration flow
heartbeat flow
local worker runtime
```

Phase 28 OpenClaw Worker Adapter runtime:

```text
worker_client/openclaw
BaseOpenClawProvider
MockOpenClawProvider
OpenClawRuntime
OpenClawWorkerClient
openclaw_tool
openclaw_action_logs
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=True
OPENCLAW_ACTION_TIMEOUT_SECONDS=60.0
```

OpenClaw flow:

```text
API Server / openclaw_tool
-> OpenClawService
-> BrowserWorkerSelector capability=openclaw
-> OpenClawWorkerClient
-> worker_client /openclaw/* mock runtime
-> openclaw_action_logs + browser_security_audit_logs
```

`worker_client/worker_config.example.yaml` defaults:

```yaml
server_url: http://127.0.0.1:8000
worker_name: local-windows-worker-1
worker_type: playwright
workspace_id: production-workspace
worker_secret: null
worker_base_url: http://host.docker.internal:9100
runtime_host: 127.0.0.1
runtime_port: 9100
state_path: worker_client/worker_state.json
heartbeat_interval_seconds: 30
capabilities:
  browser: chromium
  screenshot: true
  page_content: true
  persistent_profile: true
```

Security note: `worker_state.json` stores the customer-machine plaintext `worker_secret` locally because the server returns it only once. It is ignored by Git and must not be committed or printed in logs. The client sends heartbeat with `X-Worker-Secret` plus signed request headers from Phase 26.

Phase 68X customer frontend defaults:

```env
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
VITE_AI_SERVER_API=http://127.0.0.1:8000
VITE_WORKSPACE_ID=production-workspace
VITE_USER_ID=production-operator
```

`worker_console` and `worker_console_desktop` now show `Phase 68X Production Runtime Alignment` on the customer-machine home screen and `client-production-runtime-panel` inside the project workbench. These panels compare the frontend server workspace with `/local/status` fields such as `workspace_id`, `registered`, `heartbeat_running`, `metric_dispatch_scheduler_running`, and `metric_dispatch_scheduler_next_poll_at`.

The standalone local worker CORS allowlist covers the current web/admin/desktop development origins on ports `5173`, `5174`, `5180`, and `5181`, so those customer-machine screens can query `/local/status` directly without weakening the production workspace contract.

Phase 68Y production closed-loop readiness:

- `GET /api/v1/commercial-operations/{operation_id}/production-closed-loop/readiness` returns the read-only `CommercialOperationProductionClosedLoopReadinessResponse`.
- `CommercialOperationService.get_production_closed_loop_readiness` aggregates plan approval, materials, production tasks, workflow selections, output candidates, final selections, publish packages, customer-machine execution evidence, metric schedules, metric dispatch claims, metric snapshots, and next-cycle improvement readiness.
- `worker_console` and `worker_console_desktop` show `Phase 68Y Production Closed-Loop E2E Readiness` inside the project workbench through `client-production-closed-loop-readiness`.
- The endpoint reports `readiness_status`, `completion_ratio`, `current_stage_key`, `ready_for_customer_machine_execution`, `ready_for_metric_feedback`, `ready_for_next_cycle`, `acceptance_gates`, and boundary markers such as `does_not_run_openclaw_or_playwright_on_server`.
- It is readiness-only and does not submit ComfyUI prompts, mutate workflow JSON, publish, run server-side OpenClaw/Playwright, collect credentials, control accounts, mutate runtime configuration, restart services, or bypass operator approval.

Phase 68Z production closed-loop controlled next action:

- `GET /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action` returns the read-only `CommercialOperationProductionClosedLoopNextActionResponse`.
- `CommercialOperationService.get_production_closed_loop_next_action` derives the selected action from 68Y readiness and returns `action_key`, `stage_key`, `action_type`, `method`, `endpoint`, `payload_template`, `evidence_requirements`, `review_gates`, `expected_result`, and `boundary`.
- `worker_console` and `worker_console_desktop` show `Phase 68Z Production Closed-Loop Controlled Next Action` inside the project workbench through `client-production-next-action-panel`.
- It is contract-only and does not execute the selected action automatically, submit ComfyUI prompts, mutate workflow JSON, publish, run server-side OpenClaw/Playwright, collect credentials, control accounts, mutate runtime configuration, restart services, or bypass operator approval.

Phase 68Z1 production closed-loop action audit:

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records` records metadata-only action review, confirmation, submission, evidence, blocked, cancelled, or failed events using `CommercialOperationProductionClosedLoopActionAuditCreateRequest`.
- `GET /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records` returns `CommercialOperationProductionClosedLoopActionAuditListResponse` with `audit_count`, `latest_record`, `counts_by_status`, `evidence_coverage`, and `production_closed_loop_next_action_audit` metadata.
- `CommercialOperationService.record_production_closed_loop_action_audit` validates the action against the current 68Z next-action contract and rejects sensitive credential/token/cookie/verifier payloads.
- `worker_console` and `worker_console_desktop` show `Phase 68Z1 Controlled Action Audit` inside the project workbench through `client-production-action-audit-panel`.
- It is audit-only and does not execute target endpoints, submit ComfyUI prompts, mutate workflow JSON, publish, run server-side OpenClaw/Playwright, collect credentials, control accounts, mutate runtime configuration, restart services, or bypass operator approval.

Phase 68Z2 production closed-loop action result binding:

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{audit_id}/result-binding` records metadata-only result bindings using `CommercialOperationProductionClosedLoopActionResultBindingRequest`.
- The endpoint returns `CommercialOperationProductionClosedLoopActionResultBindingResponse` and updates the related audit record with `result_binding_status`, `result_record_type`, `result_record_id`, `result_status`, `result_endpoint`, and evidence.
- `CommercialOperationService.bind_production_closed_loop_action_result` requires operator confirmation, validates the expected result record type when available, rejects sensitive payloads, and keeps the `production_closed_loop_action_result_binding` contract metadata.
- `worker_console` and `worker_console_desktop` expose the result binding state and `bindProductionClosedLoopActionResult` API through `client-production-action-audit-panel`.
- It is binding-only and does not execute target endpoints, submit ComfyUI prompts, mutate workflow JSON, publish, run server-side OpenClaw/Playwright, collect credentials, control accounts, mutate runtime configuration, restart services, or bypass operator approval.

Phase 68Z3 production closed-loop action readiness refresh:

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{audit_id}/result-binding/readiness-refresh` records metadata-only readiness refresh snapshots using `CommercialOperationProductionClosedLoopActionReadinessRefreshRequest`.
- The endpoint returns `CommercialOperationProductionClosedLoopActionReadinessRefreshResponse` with the refreshed `CommercialOperationProductionClosedLoopReadinessResponse`, refreshed `CommercialOperationProductionClosedLoopNextActionResponse`, `refresh_status`, current stage, next action key, and operator next actions.
- `CommercialOperationService.refresh_production_closed_loop_action_result_readiness` requires operator confirmation and a previous result binding, rejects sensitive payloads, and keeps the `production_closed_loop_action_result_readiness_refresh` contract metadata.
- `worker_console` and `worker_console_desktop` expose the refresh state and `refreshProductionClosedLoopActionReadinessAfterResultBinding` API through `client-production-action-audit-panel`.
- It is refresh-only and does not execute target endpoints, execute the next action, submit ComfyUI prompts, mutate workflow JSON, publish, run server-side OpenClaw/Playwright, collect credentials, control accounts, mutate runtime configuration, restart services, force project stages complete, or bypass operator approval.

Phase 68Z4 production closed-loop action result record validation:

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records/{audit_id}/result-binding/record-validation` records metadata-only result-record validation snapshots using `CommercialOperationProductionClosedLoopActionResultRecordValidationRequest`.
- The endpoint returns `CommercialOperationProductionClosedLoopActionResultRecordValidationResponse` with `validation_status`, result record type/id, `record_exists`, workspace and operation scope checks, status checks, `record_summary`, and supported record types.
- `CommercialOperationService.validate_production_closed_loop_action_result_record` requires operator confirmation and a previous result binding, rejects sensitive payloads, and keeps the `production_closed_loop_action_result_record_validation` contract metadata.
- `worker_console` and `worker_console_desktop` expose the validation state and `validateProductionClosedLoopActionResultRecord` API through `client-production-action-audit-panel`.
- It is validation-only and does not execute target endpoints, execute the next action, create or mutate the bound record, submit ComfyUI prompts, mutate workflow JSON, publish, run server-side OpenClaw/Playwright, collect credentials, control accounts, mutate runtime configuration, restart services, force project stages complete, or bypass operator approval.

Phase 68Z5 production closed-loop action result record gate:

- The readiness refresh endpoint now applies `production_closed_loop_action_result_record_validation_gate` before exposing progress.
- `CommercialOperationProductionClosedLoopActionReadinessRefreshResponse` includes `underlying_refresh_status`, `record_validation_gate_status`, `record_validation_required`, `record_validation_passed`, `record_validation_blocking_reasons`, `result_record_validation_status`, and `result_record_validation`.
- If the bound record is not `record_verified`, `refresh_status` becomes `record_validation_required` or `record_validation_blocked` while still returning the underlying readiness snapshot for operator context.
- `worker_console` and `worker_console_desktop` block the progress refresh action until the bound result record is verified.
- It is gate-only and does not execute target endpoints, execute the next action, create or mutate the bound record, submit ComfyUI prompts, mutate workflow JSON, publish, run server-side OpenClaw/Playwright, collect credentials, control accounts, mutate runtime configuration, restart services, force project stages complete, or bypass operator approval.

Phase 68Z6 production closed-loop verified result record pass:

- The same readiness refresh endpoint now has a tested positive path where a real `CommercialOperationOptimizationDecision` with upstream content, deliverable, execution, result, and observation records is bound to the action audit and validates as `record_verified`.
- `CommercialOperationProductionClosedLoopActionReadinessRefreshResponse` reports `record_validation_gate_status=record_validation_passed`, `record_validation_passed=true`, `record_validation_required=false`, `record_validation_blocking_reasons=[]`, and `refresh_status=underlying_refresh_status`.
- The tested loop keeps the stage incomplete and refreshes a draft optimization decision to the `mark_optimization_decision_ready` next action.
- `worker_console` and `worker_console_desktop` continue to use the existing result binding, record validation, and readiness refresh controls; no automatic endpoint execution is added.
- It is positive-gate verification only and does not execute target endpoints, execute the next action, create or mutate the bound record, submit ComfyUI prompts, mutate workflow JSON, publish, run server-side OpenClaw/Playwright, collect credentials, control accounts, mutate runtime configuration, restart services, force project stages complete, or bypass operator approval.

Phase 68Z7 production closed-loop optimization decision lifecycle:

- `CommercialOperationService.get_production_closed_loop_next_action` returns `mark_optimization_decision_ready` for `draft` or `rejected` optimization decisions and `approve_optimization_decision` only for `ready_for_review` optimization decisions.
- Both lifecycle actions carry `expected_result.record_type=OptimizationDecision` so result binding and record validation stay type-aware.
- The tested loop audits the ready action, calls `/optimization-decisions/{optimization_decision_id}/ready`, binds and validates the ready record, refreshes to the approve action, audits the approve action, calls `/optimization-decisions/{optimization_decision_id}/approve`, binds and validates the approved record, and refreshes to `ready_for_next_cycle`.
- Final readiness refresh reports `refresh_status=stage_completed`, `stage_completed_after_binding=true`, `readiness.ready_for_next_cycle=true`, `readiness.readiness_status=ready_for_next_cycle`, and `next_action_key=prepare_next_approved_operation_cycle`.
- It is lifecycle alignment only and does not execute target endpoints from audit endpoints, execute the next action automatically, submit ComfyUI prompts, mutate workflow JSON, publish, run server-side OpenClaw/Playwright, collect credentials, control accounts, mutate runtime configuration, restart services, force project stages complete without an approved decision, or bypass operator approval.

Phase 68Z8 production closed-loop next-cycle draft:

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-cycle-draft` creates or reuses a next-cycle `OperationPlan` and optional copy/image/media `ProductionTask` records after the loop is `ready_for_next_cycle`.
- `CommercialOperationNextCycleDraftRequest` requires `operator_confirmed=true`; `CommercialOperationNextCycleDraftResponse` returns `draft_status`, `source_decision_id`, `operation_plan`, `production_tasks`, `readiness_status_before`, and `next_action_key_before`.
- `prepare_next_approved_operation_cycle` now has `method=POST`, endpoint `/production-closed-loop/next-cycle-draft`, and expected result fields `record_type=OperationPlan`, `plan_status=ready_for_review`, and `production_task_status=ready_for_review`.
- `CommercialOperationService.advance_main_agent_loop` now uses the same next-cycle package path for `next_cycle_content`, so the main Agent prepares a next-cycle plan and tasks instead of only a content draft.
- It is next-cycle drafting only and does not approve the plan, approve tasks, submit ComfyUI prompts, mutate workflow JSON, publish, run server-side OpenClaw/Playwright, collect credentials, control accounts, mutate runtime configuration, restart services, or bypass operator approval.

Phase 69A customer-machine publish execution status:

- `POST /api/v1/commercial-operations/{operation_id}/publish-packages/{publish_package_id}/execution-status` records customer-machine publishing progress before final result capture.
- `CommercialOperationPublishExecutionStatusUpdateRequest` accepts `queued`, `running`, `needs_operator`, `succeeded`, `failed`, and `cancelled` with `operator_confirmed=true`, `customer_machine_id`, optional `attempt_id`, progress, failure reason, evidence links, execution log, and metadata.
- `CommercialOperationPublishExecutionStatusResponse` returns the current attempt, latest status, bounded execution history, retry policy, review gates, next actions, and the updated `PublishPackage`.
- The persisted status contract is `customer_machine_publish_execution_status`.
- `CommercialOperationPublishExecutionHandoffResponse` includes the latest `execution_status` so `worker_console` and `worker_console_desktop` can display the publishing state before `execution-result` is submitted.
- It is status tracking only and does not run OpenClaw or Playwright on the server, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, or ingest metrics without evidence.

Phase 69B customer-console publish execution status controls:

- `worker_console` and `worker_console_desktop` both expose `Phase 69B Customer-Machine Publish Execution Status` inside `client-publish-execution-panel`.
- The API clients expose `CommercialOperationPublishExecutionStatus`, `CommercialOperationPublishExecutionStatusValue`, `CommercialOperationPublishExecutionHandoff.execution_status`, and `updatePublishExecutionStatus`.
- The UI state includes `publishExecutionStatusRecord`, `publishExecutionStatusLoading`, latest progress, and latest attempt id.
- Operators can record `queued`, `running`, `needs_operator`, `succeeded`, and `failed` after confirming customer-machine id, progress, and optional evidence.
- It remains operator-driven status capture only and does not run OpenClaw or Playwright on the server, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, restart services, or mark final publish evidence complete without `execution-result`.

Phase 69C production closed-loop publish execution status readiness:

- `CommercialOperationService.get_production_closed_loop_readiness` includes `latest_records.publish_execution_status`, `counts.publish_execution_statuses`, `metadata.latest_publish_execution_status`, and the acceptance gate `publish_execution_status_tracks_customer_machine_progress_before_result_capture`.
- The publish package stage completes when a package is `prepared` or `published`; `client_execution_result` remains open until `publish_execution_result` is captured.
- Blocking reasons distinguish `customer_machine_publish_execution_status_missing`, `customer_machine_publish_execution_needs_operator`, `customer_machine_publish_execution_failed_or_cancelled`, and `customer_machine_publish_execution_result_missing`.
- `CommercialOperationService.get_production_closed_loop_next_action` returns `record_customer_machine_publish_execution_status` or `update_customer_machine_publish_execution_status` with endpoint `/publish-packages/{publish_package_id}/execution-status` until latest status is `succeeded`.
- After `execution_status=succeeded`, next action returns `submit_customer_machine_execution_result` with endpoint `/publish-packages/{publish_package_id}/execution-result`.
- It remains readiness aggregation only and does not run OpenClaw or Playwright on the server, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, restart services, or mark final evidence complete without `execution-result`.

Phase 69D customer-console publish execution readiness visibility:

- `worker_console` and `worker_console_desktop` show `Phase 69D Publish Execution Status Visibility` in the production closed-loop readiness panel.
- `productionClosedLoopPublishExecutionStatusRecord`, `productionClosedLoopPublishExecutionStatus`, `productionClosedLoopPublishExecutionProgress`, `productionClosedLoopPublishExecutionBlockingReason`, and `productionClosedLoopPublishExecutionStatusBlocked` derive the visible card state from `latest_records.publish_execution_status`.
- `client-production-closed-loop-grid` shows publish execution status, progress, and blocking reason or next action.
- The publish package display now reads `package_status`.
- `.client-production-closed-loop-grid article.ready` and `.client-production-closed-loop-grid article.blocked` mark the status card.
- It remains visibility only and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69E production closed-loop publish execution status record validation:

- `production_closed_loop_action_result_record_validation` now supports `PublishExecutionStatus`.
- `customer_machine_publish_execution_status` is accepted as an alias.
- The validation spec resolves `CommercialOperationPublishPackage` by the bound package id and reads `package_metadata` with `metadata_record_key=publish_execution_status`.
- Missing metadata returns `metadata_record_missing`; valid metadata returns `record_verified`.
- `record_summary` includes `metadata_record_key` and `metadata_record` so operators can see the exact customer-machine status that was validated.
- It remains validation only and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69F customer-console action audit guided validation:

- `worker_console` and `worker_console_desktop` show `Phase 69F Action Audit Guided Validation` inside the controlled action-audit panel.
- `expectedActionResultStatusValue` reads expected status fields, including `execution_status`, before binding result metadata.
- `actionResultEndpointFor` keeps target endpoints stable when the endpoint already includes the result record id.
- `productionClosedLoopActionRecordValidationReady` enables record validation after result binding.
- `productionClosedLoopActionReadinessRefreshReady` keeps readiness refresh disabled until `record_verified`.
- It remains UI guidance only and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69G customer-console action audit operator checklist:

- `worker_console` and `worker_console_desktop` show `Phase 69G Action Audit Operator Checklist` in the action-audit panel.
- `productionClosedLoopActionAuditChecklist` derives confirm, bind, validate, and refresh steps from latest audit metadata.
- `productionClosedLoopActionAuditChecklistNext` identifies the next executable operator step.
- `client-production-action-audit-checklist` renders the checklist below the audit cards.
- `.client-production-action-audit-checklist article.done`, `.client-production-action-audit-checklist article.next`, and `.client-production-action-audit-checklist article.blocked` mark state.
- It remains UI guidance only and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69H production closed-loop action audit operator checklist contract:

- `CommercialOperationProductionClosedLoopActionAuditListResponse.operator_checklist` carries the server-derived checklist.
- `CommercialOperationService._production_closed_loop_action_operator_checklist` builds confirm, bind, validate, and refresh step states from the latest audit record.
- Metadata includes `operator_checklist_contract=production_closed_loop_action_audit_operator_checklist`.
- `worker_console` and `worker_console_desktop` prefer `productionClosedLoopServerActionAuditChecklist`.
- `productionClosedLoopLocalActionAuditChecklist` remains a fallback for older servers.
- It remains contract and UI consumption only and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69I customer-console action audit primary step:

- `worker_console` and `worker_console_desktop` show `Phase 69I Action Audit Primary Step` in the action-audit panel.
- `productionClosedLoopActionAuditPrimaryStep` selects the first checklist item with `state=next`.
- The primary button routes `confirm`, `bind`, `validate`, and `refresh` to `recordProductionClosedLoopActionConfirmation`, `bindProductionClosedLoopActionResultFromLatest`, `validateProductionClosedLoopActionResultRecordFromLatest`, and `refreshProductionClosedLoopActionReadinessAfterBinding`.
- Individual buttons remain visible for audit clarity.
- It remains human-click guidance only and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69J production closed-loop action audit primary step contract:

- `CommercialOperationProductionClosedLoopActionAuditListResponse.primary_step` carries the server-selected next checklist step.
- `primary_step_contract=production_closed_loop_action_audit_primary_step` is exposed in metadata.
- `productionClosedLoopServerActionAuditPrimaryStep` is preferred by `worker_console` and `worker_console_desktop`.
- Local checklist scanning remains a fallback when the server field is absent.
- It remains state exposure only and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69K server closed-loop primary step dashboard:

- `admin_dashboard` exposes `Phase 69K Server Primary Step Dashboard`.
- `commercialOperationsApi.productionClosedLoopActionAudits` calls `/commercial-operations/{operation_id}/production-closed-loop/next-action/audit-records`.
- `productionActionAuditState` stores the read-only list response.
- `productionClosedLoopPrimaryStep` displays the current server-selected confirm, bind, validate, or refresh step.
- `productionClosedLoopOperatorChecklist` displays the full checklist with `done`, `next`, and `blocked` states.
- `primary_step_contract` remains visible for recovery checks.
- It remains read-only server visibility and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69L production closed-loop primary step staleness:

- `CommercialOperationProductionClosedLoopActionAuditListResponse.primary_step_staleness` is returned by the action-audit list API.
- `primary_step_staleness_contract=production_closed_loop_action_audit_primary_step_staleness` is exposed in metadata.
- `CommercialOperationService._production_closed_loop_action_primary_step_staleness` derives `fresh`, `watch`, `stale`, or `none`.
- `productionClosedLoopPrimaryStepStaleness` is displayed by `admin_dashboard`.
- Server dashboard fields include `staleness_status`, `waiting_seconds`, `escalation_recommended`, and `escalation_reason`.
- It remains read-only state analysis and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69M operation list closed-loop staleness priority:

- `CommercialOperationService.production_closed_loop_action_audit_summary_for_operation` builds the list-level action-audit summary without mutating records.
- `CommercialOperationResponse.production_closed_loop_action_audit_summary` carries the summary.
- Flat operation-list fields include `production_closed_loop_primary_step_key`, `production_closed_loop_staleness_status`, `production_closed_loop_waiting_seconds`, and `production_closed_loop_escalation_recommended`.
- `admin_dashboard` sorts `operationsForTable` through `closedLoopStalenessPriority`, counts `staleClosedLoopCount`, and shows `closed_loop_step`, `staleness`, and `waiting_s` columns.
- It remains read-only list prioritization and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69N production closed-loop intervention queue:

- `CommercialOperationService.get_production_closed_loop_intervention_queue` returns workspace-level stale/watch operations without mutating records.
- `GET /api/v1/commercial-operations/production-closed-loop/intervention-queue` returns `CommercialOperationProductionClosedLoopInterventionQueueResponse`.
- Queue item records use `CommercialOperationProductionClosedLoopInterventionQueueItemResponse`.
- Items include `operation`, `action_audit_summary`, `primary_step_key`, `staleness_status`, `waiting_seconds`, `escalation_recommended`, `priority_score`, and `recommended_action_key`.
- `admin_dashboard` calls `commercialOperationsApi.productionClosedLoopInterventionQueue`, stores `productionInterventionQueueState`, refreshes through `loadProductionClosedLoopInterventionQueue`, and renders `Phase 69N Production Closed-Loop Intervention Queue` with `productionClosedLoopInterventionQueueItems`, `productionClosedLoopInterventionQueueRows`, and `productionClosedLoopInterventionQueueCount`.
- It remains read-only queue prioritization and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69O production closed-loop intervention acknowledgement:

- `CommercialOperationService.record_production_closed_loop_intervention_acknowledgement` records operator ownership for a stale/watch queue item.
- `CommercialOperationService.list_production_closed_loop_intervention_acknowledgements` returns acknowledgement history for one operation.
- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/acknowledgements` accepts `CommercialOperationProductionClosedLoopInterventionAcknowledgementRequest`.
- The acknowledgement create endpoint returns `CommercialOperationProductionClosedLoopInterventionAcknowledgementResponse`.
- `GET /api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/acknowledgements` returns `CommercialOperationProductionClosedLoopInterventionAcknowledgementListResponse`.
- Queue items expose `latest_intervention_acknowledgement`, `acknowledgement_status`, and `acknowledgement_assignee`.
- `admin_dashboard` calls `commercialOperationsApi.createProductionClosedLoopInterventionAcknowledgement` and `commercialOperationsApi.productionClosedLoopInterventionAcknowledgements`, with `acknowledgeProductionClosedLoopInterventionQueueItem`, `interventionAssignee`, `interventionNotes`, and `ack_status`.
- It remains acknowledgement metadata only and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69P production closed-loop intervention SLA:

- `CommercialOperationService._production_closed_loop_intervention_acknowledgement_sla` derives queue-item SLA state.
- Queue items expose `acknowledgement_sla`.
- SLA states include `unassigned`, `within_sla`, `due_soon`, `overdue`, `dismissed`, and `unknown`.
- SLA fields include `waiting_seconds`, `reminder_after_seconds`, `overdue_after_seconds`, `reminder_recommended`, and `reminder_reason`.
- `admin_dashboard` counts `productionClosedLoopInterventionReminderCount` and shows `ack_sla_status`, `ack_waiting_seconds`, and `reminder_recommended`.
- It remains SLA/reminder visibility only and does not run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69Q production closed-loop intervention reminder dispatch:

- `CommercialOperationService.record_production_closed_loop_intervention_reminder_dispatch` stores an operator-confirmed reminder record only when the queue item is stale/watch and the acknowledgement SLA recommends a reminder.
- `CommercialOperationService.list_production_closed_loop_intervention_reminder_dispatches` returns dispatch history for one operation.
- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/reminder-dispatches` accepts `CommercialOperationProductionClosedLoopInterventionReminderDispatchRequest`.
- The create endpoint returns `CommercialOperationProductionClosedLoopInterventionReminderDispatchResponse`.
- `GET /api/v1/commercial-operations/{operation_id}/production-closed-loop/intervention-queue/reminder-dispatches` returns `CommercialOperationProductionClosedLoopInterventionReminderDispatchListResponse`.
- Queue items expose `latest_intervention_reminder_dispatch`, `reminder_dispatch_status`, and `reminder_dispatch_channel`.
- `admin_dashboard` calls `commercialOperationsApi.createProductionClosedLoopInterventionReminderDispatch` and `commercialOperationsApi.productionClosedLoopInterventionReminderDispatches`, with `recordProductionClosedLoopInterventionReminderDispatch`, `interventionReminderChannel`, `interventionReminderRecipient`, and `interventionReminderMessage`.
- It is record-only and does not send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69R production closed-loop intervention reminder cooldown:

- `CommercialOperationService._production_closed_loop_intervention_reminder_dispatch_cooldown` derives cooldown state from the latest reminder dispatch and current acknowledgement SLA.
- Queue items expose `reminder_dispatch_cooldown`, `reminder_follow_up_recommended`, and `reminder_next_allowed_at`.
- Cooldown states include `not_due`, `not_dispatched`, `cooling_down`, `cooldown_elapsed`, `dismissed`, and `unknown`.
- The reminder dispatch create endpoint rejects duplicate non-dismissed reminders during cooldown while allowing lifecycle progression such as `ready_for_review` to `routed_to_operator`.
- `admin_dashboard` counts `productionClosedLoopInterventionFollowUpCount` and shows `reminder_cooldown_status` and `next_reminder_allowed`.
- It is throttle metadata only and does not send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69S production closed-loop intervention queue summary:

- The intervention queue response includes `queue_summary` with `contract=production_closed_loop_intervention_queue_summary`.
- Top-level summary fields include `acknowledgement_sla_status_counts`, `reminder_dispatch_status_counts`, `reminder_cooldown_status_counts`, `acknowledgement_overdue_count`, and `reminder_follow_up_count`.
- `admin_dashboard` reads `productionClosedLoopInterventionQueueSummary`, `productionClosedLoopInterventionServerFollowUpCount`, and `productionClosedLoopInterventionOverdueCount`.
- The maintenance cockpit shows server-side overdue/follow-up pressure and dispatch/cooldown distribution without requiring row-by-row scanning.
- It is aggregate metadata only and does not send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69T production closed-loop intervention recommended action:

- `CommercialOperationService._production_closed_loop_intervention_queue_recommended_action` converts the highest-priority queue item into one reviewable next-action recommendation.
- The queue response exposes `recommended_action` with `contract=production_closed_loop_intervention_queue_recommended_action`.
- Supported action keys include `acknowledge_intervention_queue_item`, `record_intervention_reminder_dispatch`, `wait_for_reminder_cooldown`, and the item-level production closed-loop action key.
- `recommended_action.operator_confirmed_required` stays true for actionable recommendations.
- `admin_dashboard` reads `productionClosedLoopInterventionRecommendedAction` and shows the action key and reason in the maintenance cockpit.
- It is recommendation-only and does not execute target endpoints, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69U main Agent intervention recommendation routing:

- `CommercialOperationService.get_agent_skill_orchestration` calls the production intervention queue and builds `production_intervention_queue`.
- `production_intervention_queue.contract` is `production_closed_loop_intervention_main_agent_input`.
- `CommercialOperationMainAgent` adds the `production_intervention` specialist track.
- Routing decisions expose `production_intervention_required`, `production_intervention_recommended_action`, and `production_intervention_queue_summary`.
- Main Agent advance treats `production_intervention` as recommendation-only and returns operator next actions instead of acknowledging, reminding, or executing the dedicated endpoint.

Phase 69V customer-machine production intervention visibility:

- `worker_console` and `worker_console_desktop` now type `CommercialOperationRoutingDecision` in their commercial operation clients.
- Both clients consume `production_intervention_queue`, `production_intervention_required`, and `production_intervention_recommended_action` from `agent-skill-orchestration`.
- Both frontends derive `clientProductionInterventionQueue`, `clientProductionInterventionRecommendedAction`, and `clientProductionInterventionRequired`.
- Both frontends render `client-production-intervention-panel` in the project workbench with queue status, action key, reason, operator-confirmation requirement, and OpenClaw/Playwright boundary text.
- The panel is read-only visibility. It does not acknowledge queue items, send reminders, execute target endpoints, run server-side OpenClaw/Playwright, publish, control accounts, store credentials, submit ComfyUI prompts, mutate workflow JSON, restart services, or bypass approval.

Phase 69W customer-machine intervention acknowledgement:

- `worker_console` and `worker_console_desktop` now type `CommercialOperationProductionClosedLoopInterventionAcknowledgement` and its list response.
- Both clients expose `productionClosedLoopInterventionAcknowledgements` and `createProductionClosedLoopInterventionAcknowledgement`.
- Both frontends add `acknowledgeClientProductionIntervention`.
- Both frontends track `clientProductionInterventionAcknowledgementStatus` and `clientProductionInterventionAcknowledgementLoading`.
- The `Phase 69W Client Intervention Acknowledgement` action records `acknowledgement_status=assigned`, `assignee=settings.userId`, and `operator_confirmed=true` only when `clientProductionInterventionRequired` is true.
- The action refreshes Agent/Skill orchestration and production closed-loop readiness, but does not send reminders, send messages, execute target endpoints, run server-side OpenClaw/Playwright, publish, control accounts, store credentials, submit ComfyUI prompts, mutate workflow JSON, restart services, or bypass approval.
- It does not execute target endpoints, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69X customer-machine intervention acknowledgement history:

- `worker_console` and `worker_console_desktop` consume `CommercialOperationProductionClosedLoopInterventionAcknowledgementList`.
- Initial project workbench loading calls `productionClosedLoopInterventionAcknowledgements` so persisted ownership is visible after refresh.
- Both frontends keep `clientProductionInterventionAcknowledgements` and expose `refreshClientProductionInterventionAcknowledgements`.
- Both frontends track `clientProductionInterventionAcknowledgementHistoryStatus` and `clientProductionInterventionAcknowledgementHistoryLoading`.
- The `Phase 69X Client Intervention Acknowledgement History` surface renders latest owner/count/time plus recent records in `client-production-intervention-history` and `client-production-intervention-history-list`.
- `client-production-intervention-actions` keeps history refresh beside the guarded Phase 69W acknowledgement action.
- It is history visibility only and does not execute target endpoints, send reminders, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69Y customer-machine intervention status controls:

- `worker_console` and `worker_console_desktop` share `recordClientProductionInterventionAcknowledgementStatus`.
- `acknowledgeClientProductionIntervention` records `assigned` ownership with Phase 69W metadata.
- `markClientProductionInterventionInProgress` records `in_progress` ownership with Phase 69Y metadata.
- `dismissClientProductionIntervention` records `dismissed` ownership with Phase 69Y metadata.
- The grouped controls are labeled `Phase 69Y Client Intervention Status Controls` in `client-production-intervention-actions`.
- Every status write keeps `operator_confirmed=true`, updates the local acknowledgement projection, refreshes `productionClosedLoopInterventionAcknowledgements`, refreshes Agent/Skill orchestration, and refreshes production closed-loop readiness.
- It is status recording only and does not execute target endpoints, send reminders, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 69Z customer-machine intervention SLA visibility:

- `worker_console` and `worker_console_desktop` derive `clientProductionInterventionAcknowledgementSla`.
- Both frontends derive `clientProductionInterventionAcknowledgementSlaStatus`, `clientProductionInterventionWaitingSeconds`, `clientProductionInterventionReminderRecommended`, `clientProductionInterventionReminderCooldownStatus`, and `clientProductionInterventionReminderDispatchStatus`.
- The customer-machine project workbench renders `Phase 69Z Client Intervention SLA Visibility`.
- `client-production-intervention-sla-grid` shows SLA status, waiting seconds, reminder recommendation, reminder cooldown status, and latest reminder dispatch status.
- It is visibility only and does not execute target endpoints, send reminders, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70A customer-machine intervention pressure overview:

- `worker_console` and `worker_console_desktop` derive `productionInterventionPressureQueue`, `productionInterventionPressureSummary`, and `productionInterventionPressureRequired`.
- Both frontends derive `productionInterventionPressureQueueCount`, `productionInterventionPressureSlaStatus`, and `productionInterventionPressureReminderRecommended`.
- Both frontends derive `productionInterventionPressureLevel` and `productionInterventionPressureScore`.
- `serverPressureScore` includes `productionInterventionPressureScore`.
- `serverPressureCards` include `intervention_pressure`.
- `projectProcessStages` includes an `intervention` step between publish and metrics.
- It is summary visibility only and does not acknowledge queue items, change acknowledgement status, execute target endpoints, send reminders, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70B server intervention pressure overview:

- `admin_dashboard` derives `productionClosedLoopInterventionPressureScore`.
- `admin_dashboard` derives `productionClosedLoopInterventionPressureLevel`.
- `admin_dashboard` derives `productionClosedLoopInterventionPressureDrivers`.
- `admin_dashboard` derives `productionClosedLoopInterventionPressureRecommendation`.
- The server Commercial Ops page renders `Phase 70B Server Intervention Pressure Overview` with `commercial-intervention-pressure-overview`.
- `commercial-intervention-pressure-grid` shows queue, SLA, reminder, and recommended-action cards from the existing intervention queue response.
- The visible boundary marker remains `server_read_only_no_openclaw_no_playwright_no_publish`.
- It is server visibility only and does not acknowledge queue items, change acknowledgement status, execute target endpoints, send reminders, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70C server intervention acknowledgement controls:

- `admin_dashboard` adds `productionInterventionAcknowledgementState`.
- `admin_dashboard` adds `loadProductionClosedLoopInterventionAcknowledgements`.
- `admin_dashboard` derives `productionClosedLoopInterventionAcknowledgementRecords`.
- `admin_dashboard` derives `productionClosedLoopInterventionLatestAcknowledgement`.
- `admin_dashboard` adds `recordProductionClosedLoopInterventionAcknowledgementStatus`.
- The intervention queue panel renders `Phase 70C Server Intervention Acknowledgement History`.
- Recent records render in `commercial-intervention-ack-history` and `commercial-intervention-ack-history-list`.
- `commercial-intervention-status-actions` records `in_progress` and `dismissed` status updates with `operator_confirmed=true`.
- It is acknowledgement-status recording only and does not execute target endpoints, send reminders, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70D server project stage blocking overview:

- `admin_dashboard` derives `productionClosedLoopProjectStageCounts`.
- `admin_dashboard` derives `productionClosedLoopProjectBlockerRows`.
- `admin_dashboard` derives `productionClosedLoopProjectBlockedCount`.
- `admin_dashboard` derives `productionClosedLoopProjectStageOverview`.
- The Commercial Ops page renders `Phase 70D Server Project Stage Blocking Overview`.
- `commercial-project-stage-overview` shows the global stage summary.
- `commercial-project-stage-grid` shows plan review, active delivery, watch, stale, intervention, and escalation counts.
- `commercial-project-blocker-list` provides blocker shortcuts that select the corresponding operation.
- It is server visibility and navigation only and does not execute target endpoints, send reminders, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70E workspace acceptance summary:

- `GET /api/v1/commercial-operations/production-closed-loop/acceptance-summary` returns `CommercialOperationProductionClosedLoopAcceptanceSummaryResponse`.
- The response contract is `production_closed_loop_acceptance_summary`.
- `CommercialOperationService.get_production_closed_loop_acceptance_summary` aggregates Phase 68Y readiness, Phase 69N intervention queue state, current stage blockers, and primary-step staleness.
- `admin_dashboard` calls `commercialOperationsApi.productionClosedLoopAcceptanceSummary`.
- `admin_dashboard` stores `productionAcceptanceSummaryState`.
- `admin_dashboard` derives `productionClosedLoopAcceptanceSummary`, `productionClosedLoopAcceptanceOperations`, `productionClosedLoopAcceptanceTopBlockers`, `productionClosedLoopAcceptanceStatus`, and `productionClosedLoopAcceptanceCards`.
- The Commercial Ops page renders `Phase 70E Workspace Acceptance Summary`.
- `commercial-acceptance-summary-panel` shows the acceptance shell.
- `commercial-acceptance-summary-grid` shows accepted, client-ready, metric-ready, next-cycle, and blocker counts.
- `commercial-acceptance-blocker-list` provides blocker shortcuts that select the corresponding operation.
- It is server acceptance aggregation and navigation only and does not execute target endpoints, send reminders, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70F objective completion score:

- `CommercialOperationService.get_production_closed_loop_acceptance_summary` now includes `production_closed_loop_completion_score`.
- The same response includes `completion_percent`.
- The same response includes `completion_level`.
- The same response includes `score_breakdown`.
- The same response includes `remaining_gates`.
- The same response includes `next_focus`.
- `admin_dashboard` derives `productionClosedLoopCompletionPercent`.
- `admin_dashboard` derives `productionClosedLoopCompletionLevel`.
- `admin_dashboard` derives `productionClosedLoopCompletionNextFocus`.
- `admin_dashboard` derives `productionClosedLoopRemainingGates`.
- `admin_dashboard` derives `productionClosedLoopScoreBreakdown`.
- The Commercial Ops page renders `Phase 70F Objective Completion Score`.
- `commercial-acceptance-completion-strip` shows the objective score.
- `commercial-acceptance-progress` shows the progress bar.
- `commercial-acceptance-gates` shows the remaining gates.
- It is server scoring and operator guidance only and does not execute target endpoints, send reminders, send messages, run OpenClaw or Playwright, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70G client objective completion score:

- `worker_console` and `worker_console_desktop` type `CommercialOperationProductionClosedLoopAcceptanceSummary`.
- Both clients call `productionClosedLoopAcceptanceSummary`.
- Both clients keep `productionClosedLoopAcceptanceSummary`.
- Both clients keep `productionClosedLoopAcceptanceStatus`.
- Both clients derive `clientObjectiveCompletionPercent`.
- Both clients derive `clientObjectiveCompletionLevel`.
- Both clients derive `clientObjectiveCompletionNextFocus`.
- Both clients derive `clientObjectiveRemainingGates`.
- Both clients derive `clientObjectiveScoreBreakdown`.
- Both client consoles render `Phase 70G client objective completion score`.
- `client-production-objective-completion` shows the objective customer-machine score.
- `client-production-objective-meter` shows the progress bar.
- `client-production-objective-gates` shows the remaining gates.
- The visible contract marker remains `production_closed_loop_completion_score`.
- It is customer-machine visibility and operator guidance only and does not execute target endpoints, send reminders, send messages, run OpenClaw or Playwright automatically, publish from the server, control accounts, store credentials, collect tokens/cookies/verification codes, bypass approval, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70H client publish OpenClaw dry-run bridge:

- `worker_console` and `worker_console_desktop` expose `runPublishExecutionDryRunFromClient`.
- Both consoles keep `publishExecutionDryRunStatus`.
- Both consoles keep `publishExecutionDryRunLoading`.
- Both consoles keep `publishExecutionDryRunResult`.
- Both consoles call `localWorkerClient.executeOpenClawAction`.
- The local worker clients type `LocalWorkerOpenClawActionResponse`.
- The local worker clients expose `openClawHealth`.
- The local worker clients expose `openClawCapabilities`.
- The local worker clients expose `executeOpenClawAction`.
- The local worker clients call `/openclaw/actions`, `/openclaw/health`, and `/openclaw/capabilities`.
- The dry-run action type is `publish_dry_run`.
- The publish execution status metadata contract is `client_publish_execution_dry_run_bridge`.
- The action marker is `phase_70h_client_publish_openclaw_dry_run_bridge`.
- The status UI uses `client-publish-dry-run-status`.
- The result UI uses `client-publish-dry-run-result`.
- It is customer-machine dry-run and audit recording only and does not click the real publish button, log in automatically, bypass verification, collect credentials, send messages, publish from the server, run server-side OpenClaw or Playwright, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70I publish dry-run evidence gate:

- The backend gate contract is `client_publish_execution_dry_run_result_gate`.
- `CommercialOperationService._publish_execution_client_dry_run_gate` scans `publish_execution_status_history`.
- The gate accepts Phase 70H `client_publish_execution_dry_run_bridge` status metadata.
- The gate also accepts the execution-log marker `Phase 70H Client Publish OpenClaw Dry-Run Bridge`.
- `capture_publish_execution_result` blocks successful result capture with `client_publish_openclaw_dry_run_required_before_result_capture` when dry-run evidence is missing.
- Verified result capture carries `client_publish_openclaw_dry_run_verified_before_result_capture`.
- Production readiness exposes `latest_records.publish_execution_dry_run_gate`.
- Controlled next action can return `record_client_publish_openclaw_dry_run_bridge_status`.
- It is evidence validation only and does not run OpenClaw or Playwright on the server, click the real publish button, control accounts, store credentials, publish from the server, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70J publish submit evidence gate:

- The submit bridge status metadata contract is `client_publish_execution_submit_bridge`.
- The backend gate contract is `client_publish_execution_submit_result_gate`.
- `CommercialOperationService._publish_execution_client_submit_gate` scans `publish_execution_status_history`.
- `capture_publish_execution_result` blocks successful result capture with `client_publish_submit_evidence_required_before_result_capture` until submit evidence is verified.
- Verified result capture carries `client_publish_submit_evidence_verified_before_result_capture`.
- Production readiness exposes `latest_records.publish_execution_submit_gate`.
- Controlled next action can return `record_client_publish_submit_bridge_status`.
- `worker_console` and `worker_console_desktop` expose `runPublishExecutionSubmitFromClient`, `publishExecutionSubmitStatus`, `publishExecutionSubmitLoading`, and `publishExecutionSubmitResult`.
- The local worker action is `publish_submit_guarded`.
- Submit evidence must include `actual_publish_performed=true` and `operator_final_submit_confirmed=true`.
- The mock OpenClaw provider returns `real_publish_provider_not_configured` and does not count as real publishing.
- It is customer-machine submit evidence validation only and does not run OpenClaw or Playwright on the server, click the real publish button from the server, control accounts, store credentials, publish from the server, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70K standalone worker OpenClaw compatibility:

- `worker.main:app` exposes `/openclaw/health`.
- `worker.main:app` exposes `/openclaw/capabilities`.
- `worker.main:app` exposes `/openclaw/actions`.
- The standalone browser-worker compatibility process still marks responses with `standalone_browser_worker_compatibility`.
- The OpenClaw runtime is the same `OpenClawRuntime` used by worker_client.
- The default provider remains `MockOpenClawProvider`.
- `publish_submit_guarded` is available but mock submit returns `real_publish_provider_not_configured`.
- `worker_console` and `worker_console_desktop` can call the OpenClaw bridge against the current 9100 process.
- It does not implement real publishing, run server-side OpenClaw or Playwright, control accounts, collect credentials, bypass verification, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70L client publish provider readiness gate:

- `worker_console` and `worker_console_desktop` import `LocalWorkerOpenClawHealth`.
- `worker_console` and `worker_console_desktop` import `LocalWorkerOpenClawCapabilities`.
- The customer-machine publish execution panel exposes `refreshPublishProviderReadiness`.
- The local worker calls are `localWorkerClient.openClawHealth` and `localWorkerClient.openClawCapabilities`.
- The UI marker is `Phase 70L Client Publish Provider Readiness Gate`.
- The action marker is `phase_70l_client_publish_provider_readiness_gate`.
- The status marker is `client-publish-provider-readiness-status`.
- The result panel marker is `client-publish-provider-readiness`.
- A ready provider requires `mock=false`, `real_publish_submit=true`, and `publish_submit_guarded`.
- If the provider is not ready, final submit records `needs_operator` with `client_publish_provider_readiness_gate`.
- The controlled blocker remains `real_publish_provider_not_configured`.
- It does not implement real publishing, run server-side OpenClaw or Playwright, control accounts, collect credentials, bypass verification, submit ComfyUI prompts, mutate workflow JSON, or restart services.

Phase 70M Customer Console API CORS Alignment:

- The current customer console can run on `http://127.0.0.1:5181`.
- `CORS_ALLOWED_ORIGINS` includes `http://localhost:5181`.
- `CORS_ALLOWED_ORIGINS` includes `http://127.0.0.1:5181`.
- `.env`, `.env.example`, `docker-compose.yml`, and `app/core/config.py` carry the same explicit 5181 origins.
- `tests/test_conversation_frontend_config.py` asserts `5173`, `5174`, `5180`, `5181`, and `tauri://localhost`.
- This keeps explicit local origins instead of wildcard CORS.
- It removes the browser-side `Failed to fetch` blocker for the current customer console origin after API restart.
- It does not change authentication, expose credentials, run OpenClaw or Playwright, publish, submit ComfyUI prompts, mutate workflow JSON, or bypass approval.

Phase 70N OpenClaw HTTP Provider Contract:

- `worker_client.openclaw.http_provider.HttpOpenClawProvider` is available.
- `OpenClawRuntime` accepts `provider_config`.
- Non-mock provider names no longer silently downgrade to `MockOpenClawProvider`.
- Missing HTTP provider config returns `openclaw_http_base_url_required`.
- HTTP provider routes default to `/openclaw/health`, `/openclaw/capabilities`, and `/openclaw/actions`.
- `WORKER_CLIENT_OPENCLAW_BASE_URL` configures the real provider endpoint.
- `WORKER_CLIENT_OPENCLAW_API_KEY` is masked by `WorkerClientConfig.redacted()`.
- `WORKER_CLIENT_OPENCLAW_TIMEOUT_SECONDS` and path override variables are available.
- Real submit responses must include `actual_publish_performed=true` or `real_openclaw_called=true`.
- Missing real submit evidence fails as `real_publish_evidence_missing_from_provider`.
- It does not ship a third-party OpenClaw server, store platform credentials, bypass verification, run Playwright on the API server, publish from the server, submit ComfyUI prompts, mutate workflow JSON, or bypass approval.

Phase 70O Server Acceptance OpenClaw Provider Readiness Gate:

- `CommercialOperationService._get_server_acceptance_openclaw_provider_readiness` reads the registered `openclaw` Browser Worker capability endpoint.
- `GET /api/v1/commercial-operations/production-closed-loop/acceptance-summary` returns `openclaw_provider_readiness`.
- The provider readiness contract is `server_acceptance_openclaw_provider_readiness_gate`.
- `score_breakdown` includes `real_publish_provider_ready`.
- `remaining_gates` can include `configure_real_openclaw_publish_provider`.
- The acceptance gates include `real_openclaw_publish_provider_ready_for_customer_machine_submit`.
- `admin_dashboard` derives `productionClosedLoopOpenClawProviderReadiness` and `productionClosedLoopOpenClawProviderStatus`.
- `worker_console` and `worker_console_desktop` derive `serverOpenClawProviderReadiness` and `serverOpenClawProviderStatus`.
- A ready provider requires `mock=false`, `real_publish_submit=true`, and `publish_submit_guarded`.
- This gate prevents the production closed-loop score from reaching 100% while the live provider remains mock, missing, unreachable, or capability-incomplete.
- It does not deploy a third-party OpenClaw server, store credentials, run server-side OpenClaw or Playwright, publish from the server, click final submit, submit ComfyUI prompts, mutate workflow JSON, or bypass approval.

Phase 70P Browser Worker Heartbeat Supervision:

- `deployment/windows/start_browser_worker_aiops.ps1` now starts heartbeat through `Start-WorkerHeartbeatLoop` after the Browser Worker runtime is healthy.
- The same script also starts heartbeat when port 9100 is already healthy, including the current Docker-backed runtime path.
- The script exposes `-SkipHeartbeat` for maintenance-only runtime starts.
- Heartbeat logs are written to `storage/logs/browser_worker_heartbeat_stdout.log` and `storage/logs/browser_worker_heartbeat_stderr.log`.
- `deployment/windows/register_browser_worker_aiops_task.ps1` describes the scheduled task as starting both the Browser Worker and heartbeat loop.
- `worker_client.heartbeat.heartbeat_loop` writes `heartbeat_running=true` while active and clears it on graceful exit.
- This keeps the API-side `BrowserWorkerSelector` from seeing a stale offline worker while the local runtime itself is still alive.
- It does not create a real OpenClaw provider, publish, run Playwright actions automatically, store new secrets, control accounts, submit ComfyUI prompts, mutate workflow JSON, or bypass approval.

Phase 70Q OpenClaw Provider Configuration Preflight:

- `OpenClawRuntime.provider_diagnostics()` returns `openclaw_provider_configuration_preflight` without calling the provider or exposing secrets.
- `worker_client.runtime` and standalone `worker.main` expose `GET /openclaw/provider-diagnostics`.
- The response shows `openclaw_provider_is_mock`, `openclaw_http_base_url_required`, `WORKER_CLIENT_OPENCLAW_PROVIDER`, `WORKER_CLIENT_OPENCLAW_BASE_URL`, `WORKER_CLIENT_OPENCLAW_API_KEY`, redacted secret fields, provider paths, missing config, and next actions.
- `worker_console` and `worker_console_desktop` show `client-openclaw-provider-diagnostics` beside the Phase 70L publish provider gate.
- It does not store credentials, configure secrets from the UI, launch OpenClaw, run Playwright, publish, click final submit, mark mock providers as ready, or bypass approval.

Phase 70R Production Config OpenClaw Provider Guard:

- `Settings` reads `WORKER_CLIENT_OPENCLAW_ENABLED`, `WORKER_CLIENT_OPENCLAW_PROVIDER`, `WORKER_CLIENT_OPENCLAW_BASE_URL`, and `WORKER_CLIENT_OPENCLAW_API_KEY`.
- `Settings.production_config_findings()` blocks production when `OPENCLAW_ENABLED=true` but the worker provider is disabled, mock, missing the `openclaw_http` base URL, or missing a non-placeholder adapter API key.
- `scripts/check_production_config.py` now reports those worker-side OpenClaw provider findings without printing secret values.
- `deployment/profiles/production-server/env.template` and `profile.json` list the real worker OpenClaw provider keys.
- It does not create, install, or launch an OpenClaw adapter, print secrets, run Playwright, publish, click final submit, mark mock providers as ready, or bypass approval.

Phase 70S OpenClaw Provider Readiness Smoke:

- `scripts/check_openclaw_provider.py` provides a read-only smoke for a configured worker runtime.
- It checks `/openclaw/provider-diagnostics`, `/openclaw/health`, and `/openclaw/capabilities`.
- The `openclaw_provider_readiness_smoke` report passes only when the provider is configured, reachable, non-mock, declares `real_publish_submit=true`, and exposes `publish_submit_guarded`.
- The report always includes `server_side_external_execution=false` and `actual_publish_performed=false`.
- It does not execute OpenClaw actions, run Playwright, publish, click final submit, collect credentials, print secrets, or bypass approval.

Phase 70T Production Closed-Loop Delivery Audit:

- `scripts/check_production_closed_loop.py` provides the `production_closed_loop_delivery_audit` report.
- It composes `scripts/check_production_config.py`, `scripts/check_openclaw_provider.py`, `/api/v1/health`, `/local/status`, and `/api/v1/commercial-operations/production-closed-loop/acceptance-summary`.
- It requires production config, API health, worker runtime/heartbeat/registration, real OpenClaw provider smoke, and workspace acceptance summary readiness.
- It records blockers such as `production_config:*`, `openclaw_smoke:*`, `worker_heartbeat_not_running`, `remaining_gate:*`, `operation_blocker:*`, and `openclaw_provider:*`.
- It always includes `server_side_external_execution=false` and `actual_publish_performed=false`.
- It does not approve plans, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, modify schedules, or bypass approval.

Phase 70U Production Closed-Loop Delivery Plan:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-plan` provides the `production_closed_loop_delivery_plan` contract.
- `CommercialOperationService.get_production_closed_loop_delivery_plan` derives the plan from `/api/v1/commercial-operations/production-closed-loop/acceptance-summary`.
- `CommercialOperationProductionClosedLoopDeliveryPlanResponse` and `CommercialOperationProductionClosedLoopDeliveryPlanGateResponse` define the response shape.
- Each gate includes owner, priority, completion impact, blocking reasons, evidence requirements, related operation ids, and operator/server/client next actions.
- `admin_dashboard` exposes `Phase 70U Production Closed-Loop Delivery Plan` through `commercial-delivery-plan-panel`, `commercial-delivery-plan-grid`, and `commercial-delivery-plan-list`.
- `worker_console` and `worker_console_desktop` expose `Phase 70U client production closed-loop delivery plan` through `client-production-delivery-plan` and `client-production-delivery-plan-list`.
- It does not approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, or bypass approval.

Phase 70V Main Agent Delivery Plan Routing:

- `CommercialOperationService.get_agent_skill_orchestration` now passes `production_closed_loop_delivery_plan_main_agent_input` to `CommercialOperationMainAgent`.
- `CommercialOperationMainAgent` exposes the `production_delivery` track for explicit delivery-plan skill routing while keeping normal closed-loop stages on their native tracks.
- `routing_decision` includes `production_delivery_plan_required`, `production_delivery_recommended_gate`, and `production_delivery_plan_summary`.
- `next_executable_contract.parameters` carries the recommended delivery gate for operator-facing surfaces.
- `decisions` includes `production_delivery_plan_recommended_gate`.
- It does not call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, or bypass approval.

Phase 70W Production Delivery Action Packages:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-action-packages` provides the `production_closed_loop_delivery_action_packages` contract.
- `CommercialOperationService.get_production_closed_loop_delivery_action_packages` derives action packages from `production_closed_loop_delivery_plan`.
- `CommercialOperationProductionClosedLoopDeliveryActionPackageListResponse`, `CommercialOperationProductionClosedLoopDeliveryActionPackageResponse`, and `CommercialOperationProductionClosedLoopDeliveryActionStepResponse` define the response shape.
- Each package includes target console, action status, endpoint, evidence requirements, payload template, guardrails, and blocking reasons.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose Phase 70W action packages beside the Phase 70U delivery plan.
- It does not call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, configure providers, mark mock providers ready, or bypass approval.

Phase 70X Production Delivery Action Evidence:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-action-packages/evidence-records` lists `production_closed_loop_delivery_action_evidence` records.
- `POST /api/v1/commercial-operations/production-closed-loop/delivery-action-packages/evidence-records` records operator evidence for one delivery action package.
- `CommercialOperationService.record_production_closed_loop_delivery_action_evidence` validates the current delivery action package contract before storing evidence.
- `CommercialOperationService.list_production_closed_loop_delivery_action_evidence` aggregates records from commercial operation metadata.
- `CommercialOperationProductionClosedLoopDeliveryActionEvidenceRequest`, `CommercialOperationProductionClosedLoopDeliveryActionEvidenceRecordResponse`, and `CommercialOperationProductionClosedLoopDeliveryActionEvidenceListResponse` define the API payloads.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose the latest Phase 70X evidence status beside Phase 70W action packages.
- It does not call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, configure providers, mark mock providers ready, or bypass approval.

Phase 70Y Delivery Action Evidence Controls:

- `admin_dashboard` calls `createProductionClosedLoopDeliveryActionEvidenceRecord`.
- `worker_console` and `worker_console_desktop` call `recordProductionClosedLoopDeliveryActionEvidence`.
- Delivery action package cards expose `Record blocked evidence`.
- The controls submit `evidence_status=blocked`, `operator_confirmed=false`, package gate/action keys, operation id when present, and blocking reasons as the evidence summary.
- After submission, the frontends refresh `production_closed_loop_delivery_action_evidence` records.
- It does not resolve gates, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, configure providers, mark mock providers ready, or bypass approval.

Phase 70Z Production Delivery Remediation Map:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-remediation-map` exposes the `production_closed_loop_delivery_remediation_map` contract.
- `CommercialOperationService.get_production_closed_loop_delivery_remediation_map` derives remediation guidance from `production_closed_loop_delivery_action_packages` and `production_closed_loop_delivery_action_evidence_list`.
- `CommercialOperationProductionClosedLoopDeliveryRemediationMapResponse` and `CommercialOperationProductionClosedLoopDeliveryRemediationResponse` define the response shape.
- Each remediation item includes target console, primary endpoint, secondary endpoints, expected evidence, existing records needed, latest evidence status, completion gate, runbook references, and no-execution guardrails.
- `admin_dashboard` exposes `Phase 70Z Production Delivery Remediation Map`.
- `worker_console` and `worker_console_desktop` expose `Phase 70Z client delivery remediation map`.
- It does not resolve gates, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, configure providers, mark mock providers ready, or bypass approval.

Phase 71A Production Delivery Remediation Work Orders:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-orders` lists the `production_closed_loop_delivery_remediation_work_order` records.
- `POST /api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-orders` records operator ownership/status for one Phase 70Z remediation item.
- `CommercialOperationService.record_production_closed_loop_delivery_remediation_work_order` and `CommercialOperationService.list_production_closed_loop_delivery_remediation_work_orders` persist and recover work-order history.
- `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRequest`, `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderRecordResponse`, and `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderListResponse` define the request/list response shape.
- `admin_dashboard` exposes `Phase 71A Production Delivery Remediation Work Orders`.
- `worker_console` and `worker_console_desktop` expose `Phase 71A client delivery remediation work orders` and `Mark in progress`.
- It does not resolve gates, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, configure providers, mark mock providers ready, or bypass approval.

Phase 71B Production Delivery Remediation Work Order Coverage:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-coverage` exposes the `production_closed_loop_delivery_remediation_work_order_coverage` contract.
- `CommercialOperationService.get_production_closed_loop_delivery_remediation_work_order_coverage` combines `production_closed_loop_delivery_remediation_map` and `production_closed_loop_delivery_remediation_work_order_list`.
- `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageResponse` and `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCoverageItemResponse` define the response shape.
- The response includes `coverage_percent`, `unassigned_count`, `in_progress_count`, `completed_count`, `blocked_count`, `next_focus`, latest work-order assignee/status, and item-level coverage state.
- `admin_dashboard` exposes `Phase 71B Production Delivery Remediation Work Order Coverage`.
- `worker_console` and `worker_console_desktop` expose `Phase 71B client delivery remediation work-order coverage`.
- It does not create work orders, resolve gates, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, configure providers, mark mock providers ready, or bypass approval.

Phase 71C Production Delivery Remediation Work Order Assignment:

- `POST /api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-coverage/assign-missing` exposes the `production_closed_loop_delivery_remediation_work_order_assignment` contract.
- `CommercialOperationService.assign_missing_production_closed_loop_delivery_remediation_work_orders` creates `assigned` metadata work orders for currently unassigned remediation items.
- `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentRequest` and `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderAssignmentResponse` define the assignment request/response shape.
- The request requires `assignee` and `operator_confirmed=true`; the response returns `assignment_status`, `created_count`, generated records, and `coverage_after`.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose `Assign missing work orders`.
- It does not resolve gates, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, configure providers, mark mock providers ready, or bypass approval.

Phase 71D Production Delivery Remediation Work Order Execution Prep:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-execution-prep` exposes the `production_closed_loop_delivery_remediation_work_order_execution_prep` contract.
- `CommercialOperationService.get_production_closed_loop_delivery_remediation_work_order_execution_prep` combines the remediation map, work-order coverage, and work-order records into read-only execution-prep packages.
- `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepResponse` and `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderExecutionPrepItemResponse` define the response shape.
- The response includes `prep_status`, `ready_count`, `waiting_assignment_count`, `customer_machine_count`, `server_operator_count`, evidence requirements, prerequisites, operator checklist, and an inert `execution_payload_template`.
- `admin_dashboard` exposes `Phase 71D Production Delivery Remediation Work Order Execution Prep`.
- `worker_console` and `worker_console_desktop` expose `Phase 71D client delivery remediation work-order execution prep`.
- It does not resolve gates, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, configure providers, mark mock providers ready, or bypass approval.

Phase 71E Production Delivery Remediation Work Order Completion:

- `POST /api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-execution-prep/complete` exposes the `production_closed_loop_delivery_remediation_work_order_completion` contract.
- `CommercialOperationService.complete_production_closed_loop_delivery_remediation_work_order` records completion evidence from a ready execution-prep item.
- `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionRequest` and `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderCompletionResponse` define the request/response shape.
- The request requires `operator_confirmed=true` plus `work_order_id`, `remediation_key`, or `gate_key`, and `evidence_links` or `completion_summary`.
- The response includes the completed work-order record, `coverage_after`, `execution_prep_after`, `completion_status`, `readiness_refresh_required`, and `readiness_refresh_next_action`.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose `Record completion evidence`.
- It does not resolve gates, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, configure providers, mark mock providers ready, or bypass approval.

Phase 71F Production Delivery Remediation Work Order Readiness Refresh:

- `POST /api/v1/commercial-operations/production-closed-loop/delivery-remediation-map/work-order-completion/readiness-refresh` exposes the `production_closed_loop_delivery_remediation_work_order_readiness_refresh` contract.
- `CommercialOperationService.refresh_production_closed_loop_delivery_remediation_work_order_readiness` records an audited refresh after completed remediation work-order evidence.
- `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshRequest` and `CommercialOperationProductionClosedLoopDeliveryRemediationWorkOrderReadinessRefreshResponse` define the request/response shape.
- The request requires `operator_confirmed=true` plus a completed remediation work order in `completed_pending_readiness_refresh`.
- The response includes `coverage_after`, `execution_prep_after`, `readiness`, `next_action`, `refresh_record`, `next_action_key`, and `readiness_refreshed_count`; refreshed items become `completed_readiness_refreshed`.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose `Refresh readiness after completion`.
- It does not resolve gates directly, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, configure providers, mark mock providers ready, or bypass approval.

Phase 71G Production Delivery Audit Blocker Clearance Plan:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-clearance-plan` exposes the `production_closed_loop_delivery_audit_blocker_clearance_plan` contract.
- `CommercialOperationService.get_production_closed_loop_delivery_audit_blocker_clearance_plan` maps production audit blockers to clearance ownership and remediation work-order state.
- `CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearancePlanResponse` and `CommercialOperationProductionClosedLoopDeliveryAuditBlockerClearanceItemResponse` define the response shape.
- The response includes `clearance_status`, `blocker_count`, `external_dependency_count`, external dependency ownership, `ui_clearable_count`, `work_ordered_count`, `ready_for_execution_count`, `readiness_refreshed_count`, `next_focus`, `production_config_findings`, `acceptance_summary`, `remediation_map`, `work_order_coverage`, and `execution_prep`.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose `Phase 71G Blocker Clearance`.
- It does not change env vars, store secrets, configure providers, resolve gates directly, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, or bypass approval.

Phase 71H Production Delivery Audit Blocker Work Order Assignment:

- `POST /api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-clearance-plan/assign-work-orders` exposes the `production_closed_loop_delivery_audit_blocker_work_order_assignment` contract.
- `CommercialOperationService.assign_production_closed_loop_delivery_audit_blocker_clearance_work_orders` converts Phase 71G clearance items into deduplicated assigned remediation work orders.
- `CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentRequest` and `CommercialOperationProductionClosedLoopDeliveryAuditBlockerWorkOrderAssignmentResponse` define the request/response shape.
- The request requires `operator_confirmed=true`, an assignee, and can include external dependency blockers so OpenClaw/provider gaps become accountable work without being automatically resolved.
- The response includes assignment status, assigned gate keys, skipped blocker reasons, created records, `clearance_plan_before`, `clearance_plan_after`, `coverage_after`, and `execution_prep_after`.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose `Assign blocker work orders`.
- It does not change env vars, store secrets, configure providers, resolve gates directly, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, or bypass approval.

Phase 71I Production Delivery Audit Blocker Runbook Handoff:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages` exposes the `production_closed_loop_delivery_audit_blocker_runbook_handoff` contract.
- `CommercialOperationService.get_production_closed_loop_delivery_audit_blocker_runbook_packages` converts Phase 71G blocker groups into operator runbook handoff packages.
- `CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageResponse` and `CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookPackageListResponse` define the response shape.
- The response includes `handoff_status`, package counts, external dependency package counts, work-ordered package counts, required inputs, manual steps, verification commands, evidence requirements, runbook references, and the source clearance plan.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose `Phase 71I Runbook Handoff`.
- It does not change env vars, store secrets, configure providers, resolve gates directly, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, or bypass approval.

Phase 71J Production Delivery Audit Blocker Runbook Evidence:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records` lists `production_closed_loop_delivery_audit_blocker_runbook_evidence` records.
- `POST /api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records` records operator evidence against a Phase 71I runbook package.
- `CommercialOperationService.record_production_closed_loop_delivery_audit_blocker_runbook_evidence` and `CommercialOperationService.list_production_closed_loop_delivery_audit_blocker_runbook_evidence` implement the backend contract.
- `CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRequest`, `CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceRecordResponse`, and `CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceListResponse` define the request/response shape.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose `Record runbook evidence`.
- It does not change env vars, store secrets, configure providers, resolve gates directly, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, or bypass approval.

Phase 71K Production Delivery Audit Blocker Runbook Evidence Coverage:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage` exposes the `production_closed_loop_delivery_audit_blocker_runbook_evidence_coverage` contract.
- `CommercialOperationService.get_production_closed_loop_delivery_audit_blocker_runbook_evidence_coverage` joins Phase 71I runbook packages with Phase 71J evidence records.
- `CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageItemResponse` and `CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceCoverageResponse` define the response shape.
- The response includes `coverage_status`, `coverage_percent`, package counts, evidenced counts, missing evidence counts, blocked counts, resolved counts, next focus, item-level latest evidence status, the source runbook packages, and the source evidence records.
- `admin_dashboard` exposes `commercial-delivery-audit-runbook-coverage-list`; `worker_console` and `worker_console_desktop` expose `clientDeliveryAuditBlockerRunbookEvidenceCoverageStatus` and `client-production-delivery-audit-runbook-coverage-list`.
- It does not change env vars, store secrets, configure providers, resolve gates directly, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, or bypass approval.

Phase 71L Production Delivery Audit Blocker Runbook Evidence Readiness Refresh:

- `POST /api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage/readiness-refresh` exposes the `production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness_refresh` contract.
- `CommercialOperationService.refresh_production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness` records a readiness refresh only when Phase 71K has no missing, blocked, follow-up, dismissed, or submitted runbook evidence and all packages are resolved.
- `CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRequest`, `CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshRecordResponse`, and `CommercialOperationProductionClosedLoopDeliveryAuditBlockerRunbookEvidenceReadinessRefreshResponse` define the request/response shape.
- The response includes coverage before/after, acceptance summary after, clearance plan after, runbook packages after, readiness, next action, and an audited refresh record.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose `Refresh runbook readiness` and `clientDeliveryAuditBlockerRunbookReadinessRefreshStatus`.
- It does not change env vars, store secrets, configure providers, resolve gates directly, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, or bypass approval.

Phase 71M Production Closed-Loop Delivery Audit Runbook Evidence Gate:

- `scripts/check_production_closed_loop.py` extends the `production_closed_loop_delivery_audit` report by calling `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage`.
- The audit readiness map now includes `runbook_evidence_coverage_ready`.
- The audit response and text output include `runbook_evidence_readiness_refresh_required`, `runbook_evidence_coverage_status`, `runbook_evidence_coverage_percent`, `runbook_evidence_package_count`, `runbook_evidence_missing_count`, and `runbook_evidence_blocked_count`.
- Blocking reasons include `runbook_evidence_coverage:missing_evidence_count`, `runbook_evidence_coverage:blocked_count`, `runbook_evidence_coverage:resolved_count`, `runbook_evidence_coverage_status`, and `runbook_evidence_readiness_refresh_required`.
- It does not call the Phase 71L POST endpoint, change env vars, store secrets, configure providers, resolve gates directly, call target endpoints, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, or bypass approval.

Phase 71N Production Closed-Loop Audit Next Action Plan:

- `scripts/check_production_closed_loop.py` extends the `production_closed_loop_delivery_audit` report with `next_actions` and `next_action_count`.
- Each action includes `action_key`, `title`, `owner`, `priority`, `source_blockers`, `target`, `required_endpoint`, `verification_commands`, and `external_dependency_required`.
- Text output includes the `next_action` marker so operators can read the owner-routed closure plan without opening JSON.
- Known actions include `configure_real_openclaw_provider`, `resolve_runbook_evidence_coverage`, `refresh_runbook_evidence_readiness`, `clear_operation_project_blockers`, and `clear_acceptance_gate`.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, call readiness-refresh POST endpoints, or bypass approval.

Phase 71O Production Delivery Audit Next Action Plan API:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan` exposes the `production_closed_loop_delivery_audit_next_action_plan` contract.
- `CommercialOperationService.get_production_closed_loop_delivery_audit_next_action_plan` composes the acceptance summary, Phase 71G blocker clearance plan, and Phase 71K runbook evidence coverage.
- `CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanResponse` and `CommercialOperationProductionClosedLoopDeliveryAuditNextActionPlanActionResponse` define the response shape.
- The response includes `audit_status`, `acceptance_status`, `completion_percent`, `next_focus`, blocker/action counts, `runbook_evidence_coverage_ready`, `runbook_evidence_readiness_refresh_required`, `blocking_reasons`, `next_actions`, `first_action`, embedded source summaries, acceptance gates, boundaries, and metadata.
- `admin_dashboard` exposes `Phase 71O Production Delivery Audit Next Action Plan`; `worker_console` and `worker_console_desktop` expose `Phase 71O client production delivery audit next action plan`.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, call readiness-refresh POST endpoints, or bypass approval.

Phase 71P Production Delivery Audit Operator Queue:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue` exposes the `production_closed_loop_delivery_audit_operator_queue` contract.
- `CommercialOperationService.get_production_closed_loop_delivery_audit_operator_queue` groups the Phase 71O source plan by owner.
- `CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueResponse`, `CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueGroupResponse`, and `CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueItemResponse` define the response shape.
- The response includes `queue_status`, `owner_count`, `action_count`, `ui_resolvable_count`, `external_dependency_count`, `next_owner`, `first_item`, grouped `owner_groups`, and the embedded `source_plan`.
- Queue items include `resolution_mode`, `resolution_status`, `primary_console`, `primary_label`, `ui_anchor`, `endpoint_method`, `endpoint_path`, `operator_next_step`, and `blocked_by_external_dependency`.
- `admin_dashboard` exposes `Phase 71P Production Delivery Audit Operator Queue`; `worker_console` and `worker_console_desktop` expose `Phase 71P client production delivery audit operator queue`.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, call readiness-refresh POST endpoints, or bypass approval.

Phase 71Q Production Delivery Audit Operator Queue Records:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue/records` lists `production_closed_loop_delivery_audit_operator_queue_record` records.
- `POST /api/v1/commercial-operations/production-closed-loop/delivery-audit/next-action-plan/operator-queue/records` records operator-supplied status/evidence for a queue item.
- `CommercialOperationService.list_production_closed_loop_delivery_audit_operator_queue_records` and `CommercialOperationService.record_production_closed_loop_delivery_audit_operator_queue_record` implement the backend contract.
- `CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordRequest`, `CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordResponse`, and `CommercialOperationProductionClosedLoopDeliveryAuditOperatorQueueRecordListResponse` define the schema.
- The Phase 71P queue now includes `record_count`, `latest_record_id`, `latest_record_status`, `latest_record_summary`, `latest_record_created_at`, and `latest_record_operator_confirmed` on each queue item.
- `admin_dashboard`, `worker_console`, and `worker_console_desktop` expose `Mark in progress` controls for Phase 71Q.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, call readiness-refresh POST endpoints, or bypass approval.

Phase 71R Production Delivery Audit OpenClaw Provider Handoff:

- `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/openclaw-provider-handoff` returns `production_closed_loop_delivery_audit_openclaw_provider_handoff`.
- `CommercialOperationService.get_production_closed_loop_delivery_audit_openclaw_provider_handoff` joins production config findings with the server acceptance OpenClaw provider readiness gate.
- `CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffResponse` and `CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffConfigItemResponse` define the sanitized handoff payload.
- The handoff maps `OPENCLAW_PROVIDER`, `WORKER_CLIENT_OPENCLAW_ENABLED`, `WORKER_CLIENT_OPENCLAW_PROVIDER`, `WORKER_CLIENT_OPENCLAW_BASE_URL`, and redacted `WORKER_CLIENT_OPENCLAW_API_KEY`.
- `admin_dashboard` exposes `Phase 71R OpenClaw Provider Handoff` through `commercial-delivery-audit-openclaw-provider-handoff`.
- `worker_console` and `worker_console_desktop` expose `Phase 71R OpenClaw Provider Handoff` through `client-production-delivery-audit-openclaw-provider-handoff`.
- Verification commands include `python scripts/check_production_config.py --require-production`, `python scripts/check_openclaw_provider.py --base-url http://127.0.0.1:9100`, and the production closed-loop audit command.
- It does not call target endpoints, change env vars, store secrets, configure providers from the UI, resolve gates directly, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, restart services, or bypass approval.

Phase 71S Client Operator UI Simplification:

- `worker_console` and `worker_console_desktop` keep the same APIs and customer-machine execution contracts, but the default surface is simplified for operators.
- `production-runtime-strip` is a collapsed readiness drawer by default instead of a first-screen grid of runtime details.
- `client-home-detail-drawer` folds quick links, recovery guidance, and boundary notes behind explicit advanced help.
- `client-task-workbench` now orders the simple operating surface first: `simple-operator-workbench`, `simple-goal-box`, `simple-progress-card`, then `operator-detail-drawer`, then the full production loop.
- `client-operation-desk-drawer` wraps the large product-operation desk, digital-human progress, guided actions, Agent/Skill orchestration, execution queue, publish loop, and delivery details.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, restart services, or bypass approval.

Phase 71T Client Codex Minimal UI:

- `worker_console` and `worker_console_desktop` add `codex-simple-client` to the task page so the first viewport is treated as a focused task composer.
- The main textarea starts empty, relying on the operating-goal placeholder instead of prefilled demo copy.
- `simple-template-row` is a horizontal quick-start strip, not a stacked mobile grid.
- `simple-focus-strip` exposes only four first-screen counters: approvals, active work, recovery, and artifacts.
- `maintenance-drawer` stays collapsed by default and uses `data-has-work` to show whether pending work exists.
- The page shell/topbar spacing is reduced so the task composer and `simple-progress-card` stay visible sooner.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, restart services, or bypass approval.

Phase 71U Client Codex Focus Shell:

- `worker_console` and `worker_console_desktop` keep the Phase 71T task composer as the primary surface.
- `operator-home` now also carries `client-runtime-companion`, reducing local Worker status to a compact `client-runtime-summary` row.
- Language switching, start-runtime, start-heartbeat, and refresh controls remain available in the compact runtime row.
- Worker connection cards, production workspace alignment, quick links, recovery steps, and boundary notes remain available inside the collapsed `client-home-detail-drawer`.
- `simple-focus-strip` now reads as an inline status line, and `simple-progress-card` is visually secondary to the main textarea.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, restart services, or bypass approval.

Phase 71V Client Action Inbox:

- `worker_console` and `worker_console_desktop` keep the Phase 71U focus shell and add a compact `simple-action-inbox` inside the task composer.
- `simpleInboxItems` groups existing client state into approvals, recovery, output review, and active-run attention rows.
- `openClientDetailPanel` opens existing guarded panels such as `commercial-approvals-panel`, `approvals-panel`, `tasks-panel`, `outputs-panel`, or `client-project-workbench`.
- `client-project-workbench` has a stable id so output candidate review can be reached from the simple inbox.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, reject records, retry tasks, recover tasks, select output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mark mock providers ready, restart services, or bypass approval.

Phase 71W Client Creation Review Shortcuts:

- `worker_console` and `worker_console_desktop` keep the Phase 71V action inbox and add `simple-review-strip` to the task composer.
- `simpleReviewCards` derives two compact `simple-review-card` buttons from existing workflow/output state.
- The workflow card summarizes approved and pending `workflowSelections`.
- The output card summarizes selected and pending `outputCandidates`.
- Both cards open the existing `client-project-workbench` through `openClientDetailPanel`; actual decisions remain in the guarded project workbench.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve workflow selections, reject workflow selections, select output candidates, reject output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, mark mock providers ready, restart services, or bypass approval.

Phase 71X Client First Screen Priority:

- `worker_console` and `worker_console_desktop` keep the Phase 71W creation review shortcuts but reorder the simple task composer around operator attention.
- `simple-action-inbox` appears immediately after the goal input.
- `simple-review-strip` follows the inbox so flow selection and output preview are visible before broad status.
- `simple-progress-card` now follows the action and review surfaces.
- DOM order and CSS `order` values are aligned for the first-screen sequence: input, action inbox, creation review, project progress.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, reject records, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, mark mock providers ready, restart services, or bypass approval.

Phase 71Y Client Project Focus Navigation:

- `worker_console` and `worker_console_desktop` keep the Phase 71X simple first screen and add focus navigation inside `client-project-workbench`.
- `clientProjectFocusCards` summarizes approval, material, workflow, output, publish, and data areas.
- `client-project-focus-strip`, `client-project-focus-grid`, and `client-project-focus-card` render compact navigation buttons near the top of the project workbench.
- `scrollClientProjectFocus` scrolls to existing guarded sections such as `client-project-section-workflows` and `client-project-section-outputs`.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, reject records, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, mark mock providers ready, restart services, or bypass approval.

Phase 71Z Client Project Support Diagnostics Drawer:

- `worker_console` and `worker_console_desktop` keep Phase 71Y focus navigation and add `client-project-support-drawer` after the project focus strip.
- `clientProjectSupportAttention` and `clientProjectSupportStatus` summarize whether runtime, intervention, readiness, or pressure context needs attention.
- `data-has-attention` marks the support drawer summary when support diagnostics need review.
- `client-project-support-grid` contains support panels such as `client-production-runtime-panel`, `client-production-intervention-panel`, `client-production-closed-loop-readiness`, `client-production-next-action-panel`, `client-production-action-audit-panel`, `client-server-pressure-panel`, and `client-project-process-panel`.
- Action buttons and guarded project sections remain outside the support drawer.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, reject records, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, mark mock providers ready, restart services, or bypass approval.

Phase 72A Client Project Primary Action Lane:

- `worker_console` and `worker_console_desktop` keep Phase 71Z support diagnostics folded and add `client-project-primary-actions` after the support drawer.
- `ClientProjectPrimaryAction`, `clientProjectPrimaryActions`, and `clientProjectPrimaryReadyCount` derive a compact lane for main Agent advance, material, workflow, output, publish, and data actions.
- `client-project-primary-action-grid` and `client-project-primary-action` render the high-signal actions before lower-frequency controls.
- `client-project-action-drawer` keeps the previous full `client-project-actions` list available but collapsed by default.
- Guarded project sections remain outside the action drawer.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, reject records, select output candidates, create output candidates without an operator click, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, mark mock providers ready, restart services, or bypass approval.

Phase 72B Client Project Decision Queue:

- `worker_console` and `worker_console_desktop` keep Phase 72A priority actions and add `client-project-decision-lane`.
- `ClientProjectDecisionCard`, `clientProjectDecisionCandidates`, `clientProjectDecisionCards`, and `clientProjectDecisionTotalCount` derive pending human decisions from plans, materials, tasks, workflows, outputs, final selections, publish packages, and metric snapshots.
- `client-project-decision-grid` renders compact decision cards before the full record list.
- `openClientProjectRecordsAndScroll` opens `client-project-records-drawer` and jumps to the existing guarded section.
- The existing `client-project-grid` now lives inside `client-project-records-drawer`, hidden by default until the operator opens it.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, reject records, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, mark mock providers ready, restart services, or bypass approval.

Phase 72C Client Project Current Decision Focus:

- `worker_console` and `worker_console_desktop` keep Phase 72B decision records folded while making the first review item the primary surface.
- `clientProjectCurrentDecision` derives the single current decision, and `clientProjectSecondaryDecisionCards` keeps the remaining backlog compact.
- `client-project-decision-focus` renders `projectDecisionCurrent`, the record detail, status context, and guarded primary/secondary actions.
- `client-project-decision-focus-actions` contains the operator-click primary action, optional reject action, and `projectDecisionDetail` to open the exact guarded section.
- Full evidence still lives in `client-project-records-drawer`, and secondary controls still live behind the existing drawers.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records without an operator click, reject records without an operator click, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, mark mock providers ready, restart services, or bypass approval.

Phase 72D Client Attention Current Task:

- `worker_console` and `worker_console_desktop` keep the first-screen task composer simple while making the attention area task-focused.
- `simpleCurrentInboxItem`, `simpleSecondaryInboxItems`, and `simpleInboxTotalCount` derive the current attention item and compact backlog from existing `simpleInboxItems`.
- `simple-action-current` renders the current attention detail with an operator-click detail button.
- `simple-action-secondary-list` keeps remaining approvals, recovery, output, or active-run items visually secondary.
- `maintenanceCurrent` appears in the collapsed `maintenance-drawer` summary so `审批与产出` names the current item, not only the count.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, mark mock providers ready, restart services, or bypass approval.

Phase 72E Client Creation Current Review:

- `worker_console` and `worker_console_desktop` keep `simpleReviewCards` as the workflow/output source list while making only one creation review item primary.
- `simpleReviewStatePriority` chooses the current creative review in this order: `needs-action`, `current`, `waiting`, `done`.
- `simpleCurrentReviewCard`, `simpleSecondaryReviewCards`, and `simpleReviewAttentionCount` derive the current review, compact secondary item, and attention count.
- `simple-review-current` renders the current creative decision with an operator-click project-workbench button.
- `simple-review-secondary-list` keeps the remaining workflow/output state secondary.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, approve workflow selections, reject workflow selections, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, mark mock providers ready, restart services, or bypass approval.

Phase 72F Client Progress Current Stage:

- `worker_console` and `worker_console_desktop` keep `goalStatusStages` and `simpleCurrentStage` as the project-progress source of truth.
- `simpleProgressDoneCount` and `simpleProgressCurrentSummary` derive the compact completed/total header count.
- `simpleProgressCurrent` labels the current stage focus, and `simpleProgressTrail` labels the compact stage trail.
- `simple-progress-current` renders the current stage label, detail, status, and suggested action.
- `simple-progress-stages` remains visible as a horizontal trail instead of a tall stage board.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, mark mock providers ready, restart services, or bypass approval.

Phase 72G Client First Viewport Action Priority:

- `worker_console` and `worker_console_desktop` keep stats and quick-start templates available but remove them from the default first-viewport reading path.
- `simpleContextTitle` and `simpleContextSummary` label the folded startup context.
- `simple-start-drawer` appears in the simple operator workbench before the goal box.
- `simple-start-drawer-body` contains the existing `simple-focus-strip` and `simple-template-row`.
- The drawer body is hidden while the drawer is closed, letting the current attention card appear earlier.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, mark mock providers ready, restart services, or bypass approval.

Phase 72H Client Single Focus Context Drawer:

- `worker_console` and `worker_console_desktop` keep creation review and project progress available but remove them from the default visible work path.
- `simpleProjectContextTitle`, `simpleProjectContextSummary`, `simpleProjectContextReview`, and `simpleProjectContextProgress` label the folded project context.
- `simple-project-context-drawer` appears after the current attention inbox.
- `simple-project-context-body` contains the existing `simple-review-strip` and `simple-progress-card`.
- The drawer body is hidden while the drawer is closed, leaving the goal input and current attention task as the only always-visible work objects.
- It does not call target endpoints, change env vars, store secrets, configure providers, resolve gates directly, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, mark mock providers ready, restart services, or bypass approval.

Phase 72I Production Audit Delivery Summary:

- `scripts/check_production_closed_loop.py` keeps the full `production_closed_loop_delivery_audit` payload and adds a compact `delivery_audit_summary`.
- The summary contract is `production_closed_loop_delivery_audit_summary`.
- The summary reports completion percent, failed readiness keys, blocker category counts, `primary_next_action`, `next_external_dependency_action`, `next_operator_action`, and runbook evidence counts.
- `--summary-json` prints only that compact summary for release operators and automation.
- It does not call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, resolve gates directly, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, call readiness-refresh POST endpoints, or bypass approval.

Phase 72J Client Delivery Audit Focus:

- `worker_console` and `worker_console_desktop` derive a compact delivery-audit focus from `productionClosedLoopDeliveryAuditNextActionPlan`, `productionClosedLoopDeliveryAuditOperatorQueue`, and acceptance/readiness state.
- The first-screen `simple-delivery-audit-card` appears after `simple-action-inbox` and before `simple-project-context-drawer`.
- `simpleDeliveryAuditTitle`, `simpleDeliveryAuditReady`, `simpleDeliveryAuditBlocked`, `simpleDeliveryAuditWaiting`, `simpleDeliveryAuditExternal`, `simpleDeliveryAuditOperator`, `simpleDeliveryAuditBlockers`, `simpleDeliveryAuditActions`, `simpleDeliveryAuditNext`, and `simpleDeliveryAuditRefresh` label the compact delivery status.
- `simpleDeliveryAuditLoaded`, `simpleDeliveryAuditBlockerCount`, `simpleDeliveryAuditExternalCount`, `simpleDeliveryAuditOperatorCount`, and `simpleDeliveryAuditPrimaryAction` keep the first-screen answer focused on completion, blocker pressure, and the next operator path.
- It does not call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, resolve gates directly, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, call readiness-refresh POST endpoints, or bypass approval.

Phase 72K Client Delivery Audit Quick Action:

- `worker_console` and `worker_console_desktop` derive `simpleDeliveryAuditQueueItem` from the delivery audit operator queue.
- `simpleDeliveryAuditRecordStatus`, `simpleDeliveryAuditRecordInProgress`, `simpleDeliveryAuditRecordDisabled`, and `simpleDeliveryAuditRecordLabel` keep the quick action state readable.
- `simpleDeliveryAuditRecordAction`, `simpleDeliveryAuditRecordingAction`, and `simpleDeliveryAuditInProgress` label the card-level action.
- The first-screen card calls `recordClientDeliveryAuditOperatorQueueInProgress(simpleDeliveryAuditQueueItem)` only after an operator click and writes the existing `production_closed_loop_delivery_audit_operator_queue_record` evidence.
- It does not call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, resolve gates directly, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, call readiness-refresh POST endpoints, or bypass approval.

Phase 72L Client Runbook Evidence Quick Path:

- `worker_console` and `worker_console_desktop` derive `simpleDeliveryAuditRunbookPackage` from delivery audit blocker runbook packages.
- `simpleDeliveryAuditRunbookMissingCount`, `simpleDeliveryAuditRunbookBlockedCount`, `simpleDeliveryAuditRunbookEvidenceCount`, `simpleDeliveryAuditRunbookCoverageStatus`, `simpleDeliveryAuditEvidenceDisabled`, and `simpleDeliveryAuditEvidenceLabel` keep evidence pressure visible on the first-screen card.
- `simpleDeliveryAuditEvidence`, `simpleDeliveryAuditRecordEvidence`, and `simpleDeliveryAuditRecordingEvidence` label the compact evidence count and evidence-status action.
- The first-screen card calls `recordClientDeliveryAuditBlockerRunbookEvidence(simpleDeliveryAuditRunbookPackage)` only after an operator click and writes the existing `production_closed_loop_delivery_audit_blocker_runbook_evidence` status path.
- It does not call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, resolve gates directly, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, call readiness-refresh POST endpoints, or bypass approval.

Phase 72M Client Runbook Evidence Submission:

- `worker_console` and `worker_console_desktop` define `ClientRunbookEvidenceStatus`, `ClientRunbookEvidenceDraft`, `initialClientRunbookEvidenceDraft`, `clientRunbookEvidenceDraft`, and `setClientRunbookEvidenceDraft`.
- The project workbench runbook section exposes `client-production-delivery-audit-runbook-evidence-form` for status, evidence summary, evidence link, operator notes, and operator confirmation.
- `submitClientDeliveryAuditBlockerRunbookEvidence` calls the existing `production_closed_loop_delivery_audit_blocker_runbook_evidence` API and refreshes evidence records, coverage, and runbook packages after success.
- The UI returns `operator_confirmation_required_for_runbook_evidence` or `evidence_summary_or_link_required_for_runbook_evidence` before calling the API when `submitted` or `resolved` lacks confirmation or evidence text/link.
- It does not call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, resolve gates directly without evidence, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, call readiness-refresh POST endpoints, or bypass approval.

Phase 72N Client Runbook Readiness Refresh Gate:

- `worker_console` and `worker_console_desktop` derive `clientDeliveryAuditBlockerRunbookRefreshReady`, `clientDeliveryAuditBlockerRunbookRefreshRequired`, `clientDeliveryAuditBlockerRunbookRefreshGateReason`, `clientDeliveryAuditBlockerRunbookRefreshDisabled`, and `clientDeliveryAuditBlockerRunbookRefreshLabel`.
- The runbook section shows `client-production-delivery-audit-runbook-refresh-gate` with the current refresh blocker or readiness state.
- `refreshClientDeliveryAuditBlockerRunbookEvidenceReadiness` returns `runbook_evidence_readiness_refresh_blocked:{reason}` locally until all runbook evidence coverage is resolved or no runbook evidence is required.
- The only backend write remains `production_closed_loop_delivery_audit_blocker_runbook_evidence_readiness_refresh`, reached after an explicit operator click.
- It does not call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, mark evidence resolved, submit evidence, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72O Client Codex Minimal Workspace:

- `worker_console` and `worker_console_desktop` derive `simpleServerPressureState`, `SimpleMinimalStatusCard`, and `simpleMinimalStatusCards`.
- The first screen renders `simple-command-status-strip` and `simple-command-status-pill` under `Phase 72O Client Codex Minimal Workspace`.
- The strip surfaces server pressure, project progress, creation review, and delivery readiness from `serverPressureScore`, `serverPressureLabel`, `simpleProgressCurrentSummary`, `simpleReviewAttentionCount`, and `clientObjectiveCompletionPercent`.
- The Codex-style surface hides `simple-start-drawer` by default, compresses `simple-goal-box`, hides secondary inbox rows by default, and keeps delivery audit actions compact while retaining detail drawers for approvals, outputs, workflow selection, and diagnostics.
- It does not call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, mark evidence resolved, submit evidence, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72P Client Session Controls Drawer:

- `worker_console` and `worker_console_desktop` mark the title-bar session controls with `client-session-title-actions`.
- `.codex-simple-client .client-session-title-actions` hides `createThread` and `refreshConversation` from the default first-screen title bar.
- `simple-session-drawer` and `simple-session-actions` keep the same session controls available inside the folded maintenance drawer under `Phase 72P Client Session Controls Drawer`.
- It does not change conversation API contracts, create threads automatically, refresh conversations automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, mark evidence resolved, submit evidence, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72Q Client Mode Switch Drawer:

- `worker_console` and `worker_console_desktop` replace the always-visible operation/knowledge two-button switch with `operator-page-mode-drawer`.
- The `operator-page-tabs` summary shows the current mode while `operator-page-tab-actions` keeps `setOperatorPage("operations")` and `setOperatorPage("knowledge")` available after expansion.
- The knowledge base page, material upload, RAG ingestion, and document management surfaces remain available through the drawer.
- It does not remove the knowledge base page, change upload APIs, create documents automatically, change conversation API contracts, create threads automatically, refresh conversations automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, mark evidence resolved, submit evidence, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72R Client Runtime Action Compression:

- `worker_console` and `worker_console_desktop` wrap language switching, runtime start, heartbeat start, and status refresh in `client-runtime-controls-drawer` under `Phase 72R Client Runtime Controls Drawer`.
- The runtime drawer summary keeps connection state visible while `client-runtime-summary-actions` stays available after expansion.
- The delivery audit card keeps the primary operator action in `simple-delivery-audit-primary-row` and moves runbook evidence, readiness refresh, and detail navigation into `simple-delivery-audit-more` / `simple-delivery-audit-more-actions` under `Phase 72R Client Delivery Audit Secondary Actions`.
- It does not remove runtime controls, start runtime automatically, start heartbeat automatically, refresh status automatically, record operator progress automatically, submit runbook evidence automatically, refresh production readiness automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, mark evidence resolved, submit evidence, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72S Client Compact Shell:

- `worker_console` and `worker_console_desktop` mark the outer shell as `client-shell-topbar` under `Phase 72S Client Compact Shell`.
- `client-shell-title` replaces the Worker-console first impression with customer-facing task-workspace text.
- Runtime and heartbeat badges remain visible in `client-shell-diagnostics-drawer`; detailed diagnostics live in `client-shell-diagnostics-body` and are hidden until expansion.
- `worker_console_desktop` folds normal `connection-state`, `Desktop Runtime Foundation`, and server/client boundary details into the diagnostics drawer while preserving the API-unreachable alert outside the drawer.
- It does not remove runtime status, remove heartbeat status, hide API-unreachable errors, change local worker APIs, start runtime automatically, start heartbeat automatically, refresh status automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, mark evidence resolved, submit evidence, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72T Client Delivery Next Action Focus:

- `worker_console` and `worker_console_desktop` derive `simpleDeliveryFocusTitle`, `simpleDeliveryFocusHeadline`, `simpleDeliveryFocusDetail`, and `simpleDeliveryFocusNextLabel` from existing delivery-audit and readiness data.
- The first-screen delivery card keeps `simple-delivery-audit-card` while adding `Phase 72T Client Delivery Next Action Focus` to its aria label.
- `simple-delivery-next-action-focus` and `simple-delivery-focus-detail` make the card lead with current blockers, operator-visible detail, and the recommended action.
- The existing primary operator-queue action, runbook evidence action, readiness refresh, and detail navigation remain unchanged.
- It does not change delivery-audit APIs, change readiness scoring, create or clear blockers automatically, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, mark evidence resolved, submit evidence, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72U Client Delivery Blocker Deep Link:

- `worker_console` and `worker_console_desktop` derive `simpleDeliveryFocusPanelId` from existing delivery-audit and readiness data.
- `clientProjectDeliveryAuditPanelIds` identifies the delivery-audit subsection targets.
- `clientProjectDetailPanelIds` lets `openClientDetailPanel` expand the existing project drawer when the target is a delivery-audit subsection.
- `projectSupportDrawer` is opened for delivery-audit subsection targets so the destination is visible.
- The `delivery-readiness` entry in `simpleMinimalStatusCards` now uses `panelId: simpleDeliveryFocusPanelId`, and the folded delivery detail action calls `openClientDetailPanel(simpleDeliveryFocusPanelId)`.
- `window.requestAnimationFrame` delays the final `scrollIntoView` until the project and support drawers have opened.
- The existing delivery-audit sections expose stable ids for `client-production-delivery-audit-blocker-clearance`, `client-production-delivery-audit-runbooks`, `client-production-delivery-audit-next-action-plan`, `client-production-delivery-audit-operator-queue`, and `client-production-delivery-audit-openclaw-provider-handoff`, with `scroll-margin-top: 18px` for landing.
- It does not change delivery-audit APIs, change readiness scoring, create or clear blockers automatically, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, mark evidence resolved, submit evidence, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72V Client Unified Current Work Panel:

- `worker_console` and `worker_console_desktop` add `SimpleCurrentWorkItem`, `simpleCurrentWorkItems`, `simpleCurrentWorkItem`, `simpleSecondaryWorkItems`, `simpleCurrentWorkTitle`, `simpleCurrentWorkMoreLabel`, `simpleCurrentWorkOpenPanelId`, and `simpleCurrentWorkIsDelivery`.
- `simpleCurrentWorkItems` merges the current inbox item, delivery readiness, and current creation review into one priority-ranked queue using `simpleReviewStatePriority`.
- The first-screen customer-machine UI renders `simple-current-work-panel` under `Phase 72V Client Unified Current Work Panel`.
- The panel keeps the delivery operator-queue record action when delivery is the current item and otherwise routes the primary open action through `openClientDetailPanel(simpleCurrentWorkOpenPanelId)`.
- `simple-current-work-more` and `simple-current-work-more-actions` fold secondary current-work navigation, runbook evidence, and readiness refresh.
- `.codex-simple-client .simple-action-inbox` and `.codex-simple-client .simple-delivery-audit-card` hide the legacy main cards from the default first screen while preserving their DOM contracts.
- `simple-current-work-panel` is included in the responsive single-column list.
- It does not change delivery-audit APIs, change readiness scoring, create or clear blockers automatically, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, mark evidence resolved, submit evidence, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72W Client Essential Status Strip:

- `worker_console` and `worker_console_desktop` add `simpleVisibleStatusCards`.
- `simpleVisibleStatusCards` filters `simpleMinimalStatusCards` to `server-pressure` and `project-progress`.
- `simple-command-status-strip` renders `simpleVisibleStatusCards.map((card) => ...)` under `Phase 72W Client Essential Status Strip / Phase 72O Client Codex Minimal Workspace`.
- `simpleMinimalStatusCards` still retains `creation-review` and `delivery-readiness` as structured data.
- `simple-current-work-panel` remains the first-screen action context for creation review and delivery readiness.
- `.simple-command-status-strip` now uses `grid-template-columns: repeat(2, minmax(0, 1fr))`.
- It does not remove server pressure visibility, remove project progress visibility, remove creation review data, remove delivery readiness data, change delivery-audit APIs, change readiness scoring, create or clear blockers automatically, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, mark evidence resolved, submit evidence, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72X Client Command Run Options Drawer:

- `worker_console` and `worker_console_desktop` wrap `sendBackgroundConversation` in `simple-run-options-drawer`.
- The drawer is labelled `Phase 72X Client Command Run Options Drawer`.
- After Phase 73V, `submitSimpleOperationGoal` is the visible primary command action for the plan-first workspace, while `sendBackgroundConversation` and `workbenchCopy.backgroundRun` remain folded inside run options.
- `sendBackgroundConversation` and `workbenchCopy.backgroundRun` remain available inside `simple-run-options-actions`.
- CSS adds `simple-run-options-drawer`, `simple-run-options-drawer > summary`, `simple-run-options-actions`, and `.simple-run-options-drawer:not([open]) .simple-run-options-actions`.
- It does not change conversation APIs, remove background execution, start background execution automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72Y Client Current Work Single Action:

- `worker_console` and `worker_console_desktop` keep `simple-current-work-panel` as the first-screen current-work surface.
- Delivery work now exposes `recordClientDeliveryAuditOperatorQueueInProgress(simpleDeliveryAuditQueueItem)` as the only default visible primary action.
- Non-delivery work now exposes `openClientDetailPanel(simpleCurrentWorkOpenPanelId)` as the only default visible primary action.
- `simple-current-work-more` is labelled `Phase 72Y Client Current Work Single Action / Phase 72V Client Unified Current Work Secondary Actions`.
- Delivery detail navigation is preserved inside `simple-current-work-more-actions`.
- Secondary current-work navigation, runbook evidence recording, and readiness refresh remain folded inside the same drawer.
- It does not change delivery-audit APIs, change readiness scoring, remove detail navigation, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 72Z Client Current Work Metrics Drawer:

- `worker_console` and `worker_console_desktop` move `simple-current-work-metrics` inside `simple-current-work-more-actions`.
- The metrics keep the existing inbox, creation-review, and delivery-audit values.
- The metrics block now also has `simple-current-work-more-metrics` and the aria label `Phase 72Z Client Current Work Metrics Drawer`.
- `simple-current-work-panel` changes from `grid-template-columns: minmax(0, 1fr) auto minmax(220px, 0.7fr)` to `grid-template-columns: minmax(0, 1fr) minmax(220px, 0.7fr)`.
- `worker_console` and `worker_console_desktop` styles add `simple-current-work-more-metrics` rules so the metrics fill the drawer cleanly.
- It does not remove inbox metrics, remove review metrics, remove delivery metrics, change delivery-audit APIs, change readiness scoring, change the current-work priority queue, record operator queue progress automatically, submit runbook evidence automatically, refresh production readiness automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73A Client Secondary Panels Drawer:

- `worker_console` and `worker_console_desktop` add `simple-secondary-panels-drawer` with aria label `Phase 73A Client Secondary Panels Drawer`.
- The grouped drawer summary exposes one default entry labelled `更多面板` / `More panels`.
- The existing `simple-project-context-drawer` remains inside `simple-secondary-panels-body`.
- The existing `operator-detail-drawer` remains inside `simple-secondary-panels-body`.
- Styles add `simple-secondary-panels-drawer`, `simple-secondary-panels-body`, `.simple-secondary-panels-drawer:not([open]) .simple-secondary-panels-body`, and nested margin reset rules.
- It does not remove project context, remove plan/status details, remove approval panels, remove output panels, change current-work priority, change delivery-audit APIs, change readiness scoring, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73B Client Top Utility Drawer:

- `worker_console` and `worker_console_desktop` add `client-top-utility-drawer` with aria label `Phase 73B Client Top Utility Drawer`.
- The utility summary exposes `工作区工具` / `Workspace tools`, the current operation/knowledge mode, and concise runtime readiness text.
- The existing `client-shell-diagnostics-drawer` remains inside `client-top-utility-body`.
- The existing `operator-page-mode-drawer` remains inside `client-top-utility-body`.
- Styles add `client-top-utility-drawer`, `client-top-utility-body`, `.client-top-utility-drawer:not([open]) .client-top-utility-body`, and nested drawer sizing rules.
- It does not remove runtime diagnostics, remove runtime status, remove heartbeat status, remove the knowledge base page, remove mode switching, change local worker APIs, change upload APIs, change conversation APIs, change current-work priority, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73C Client Runtime Companion Drawer:

- `worker_console` and `worker_console_desktop` add `client-runtime-companion-drawer` with aria label `Phase 73C Client Runtime Companion Drawer`.
- The drawer summary exposes the local connection label and current readiness headline, such as `客户机已就绪` / `Client ready`.
- The existing `client-runtime-summary` remains inside `client-runtime-companion-body`.
- The existing `client-runtime-controls-drawer` remains inside `client-runtime-companion-body`.
- The existing `client-home-detail-drawer` remains inside `client-runtime-companion-body`.
- Styles add `client-runtime-companion-drawer`, `client-runtime-companion-body`, `.client-runtime-companion-drawer:not([open]) .client-runtime-companion-body`, and compact summary rules.
- It does not remove local runtime controls, remove language switching, remove advanced maintenance details, remove runtime status, remove heartbeat status, change local worker APIs, start runtime automatically, start heartbeat automatically, refresh status automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73D Client Workbench First Action Focus:

- `worker_console` and `worker_console_desktop` hide the duplicated `panel-title` inside `.chat-panel.codex-simple-client`.
- `worker_console` and `worker_console_desktop` hide the explanatory `simple-operator-header` inside `.codex-simple-client`.
- The existing `simple-command-status-strip` remains the first visible workbench context surface.
- The existing `simple-goal-box` remains the primary input and run action surface.
- The existing `client-operation-desk-drawer` remains available but moves to `order: 6`.
- It does not remove the workbench, remove operation details, remove status cards, remove the goal input, remove current-work actions, change conversation APIs, change local worker APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73E Client Quiet Maintenance Entry:

- `worker_console` and `worker_console_desktop` label the global advanced diagnostics drawer as `Phase 73E Client Quiet Maintenance Entry`.
- The closed summary shows compact `维护` / `Maintenance` and `日志与诊断` / `Logs and diagnostics` text.
- `copy.advancedSummary` remains the summary title and accessible label.
- The existing `layout-grid`, dashboard, runtime controls, browser sessions, and `logs-panel` remain inside `advanced-diagnostics`.
- Styles make `.advanced-diagnostics` right-aligned with `order: 7` and `width: fit-content` while closed.
- Styles restore full-width diagnostics when `.advanced-diagnostics[open]`.
- It does not remove advanced diagnostics, remove logs, remove browser session visibility, remove dashboard fields, remove runtime controls, change local worker APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73F Client Codex Quiet Workbench:

- `worker_console` and `worker_console_desktop` label the compact status row as `Phase 73F Client Quiet Status Rail`.
- The same frontends label `client-operation-desk-drawer`, `simple-secondary-panels-drawer`, and `maintenance-drawer` as the Phase 73F quiet operation/detail, secondary-panel, and approval/output focus entries.
- Styles convert `.simple-command-status-strip` under `.codex-simple-client` into a compact flex rail.
- Styles make `client-operation-desk-drawer` and `simple-secondary-panels-drawer` quiet right-aligned entries while closed, then restore full-width drawer content when opened.
- `maintenance-drawer` remains the customer-machine approval/output review entry, with tighter spacing so it stays close to current work.
- It does not remove status visibility, remove operation details, remove secondary panels, remove approval or output review surfaces, change local worker APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, create tasks, approve records, reject records, retry failed work, recover failed work, select output candidates without an operator click, create output candidates, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73G Server Codex Quiet Cockpit:

- `admin_dashboard` adds `commercial-server-quiet-cockpit` with aria label `Phase 73G Server Codex Quiet Cockpit`.
- The quiet cockpit summarizes production closed-loop completion, server pressure, intervention queue pressure, and the selected operation primary step.
- `commercial-maintenance-cockpit`, `commercial-intervention-pressure-overview`, `commercial-acceptance-summary-panel`, `commercial-delivery-plan-panel`, `commercial-project-stage-overview`, and the production closed-loop intervention queue panel remain in the DOM.
- Those detailed server maintenance sections are now folded by default inside `commercial-server-maintenance-drawer` and `commercial-server-maintenance-body`.
- It does not remove server maintenance details, remove acceptance or delivery diagnostics, change commercial operation APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, create tasks, approve records, reject records, acknowledge intervention records without an operator click, send reminders, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73H Server Quiet Create Drawer:

- `admin_dashboard` adds `commercial-server-create-drawer` with aria label `Phase 73H Server Quiet Create Operation Drawer`.
- The existing create-operation `Panel`, `createOperation()` action, and action result drawer remain available inside `commercial-server-create-body`.
- The create-operation form is folded by default so the server first screen stays focused on status, maintenance, operation list, and selected-operation context.
- It does not remove create-operation capability, change commercial operation APIs, create operations automatically, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, approve records, reject records, acknowledge intervention records without an operator click, send reminders, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73I Server Operation Context Drawer:

- `admin_dashboard` adds `commercial-server-operation-context-drawer` with aria label `Phase 73I Server Operation Context Drawer`.
- The existing operation detail `Panel`, plan table, status action buttons, Agent/Skill summary, skill table, and routing decision table remain available inside `commercial-server-operation-context-body`.
- The operation context drawer is folded by default below the operation list so selected-operation context no longer appears as two always-open panels.
- It does not remove operation details, remove Agent/Skill orchestration, remove plan regeneration, remove status actions, change commercial operation APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, approve records, reject records, acknowledge intervention records without an operator click, send reminders, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73J Server Action Audit Drawer:

- `admin_dashboard` adds `commercial-server-action-audit-drawer` with aria label `Phase 73J Server Action Audit Drawer`.
- The existing `Production closed-loop action audit` `Panel`, refresh control, `productionClosedLoopActionAudits` fields, primary-step detail grid, and operator checklist table remain available inside `commercial-server-action-audit-body`.
- The action-audit drawer is folded by default below the operation context drawer so production audit detail no longer appears as an always-open dashboard panel.
- It does not remove action-audit visibility, remove the operator checklist, remove the refresh control, change commercial operation APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, approve records, reject records, acknowledge intervention records without an operator click, send reminders, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73K Server Production Workstream Drawers:

- `admin_dashboard` adds `commercial-server-production-upstream-drawer` with aria label `Phase 73K Server Production Upstream Drawer`.
- The ComfyUI entry panel, content drafts panel, and asset requests panel remain available inside `commercial-server-production-upstream-body`.
- `admin_dashboard` adds `commercial-server-production-closed-loop-drawer` with aria label `Phase 73K Server Production Closed Loop Drawer`.
- Deliverables, evidence snapshots, execution requests, execution runs, results, monitoring observations, optimization decisions, approvals, dry-runs, and links remain available inside `commercial-server-production-closed-loop-body`.
- Both drawers keep the Commercial Ops server page Codex-like by default while preserving the full production workstream after expansion.
- It does not remove content drafts, remove asset requests, remove deliverables, remove approvals, remove dry-runs, remove links, change commercial operation APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, approve records, reject records, acknowledge intervention records without an operator click, send reminders, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73L Server Operation List Drawer:

- `admin_dashboard` adds `commercial-server-operation-list-drawer` with aria label `Phase 73L Server Operation List Drawer`.
- The drawer summary exposes `Operation queue`, the `operationsForTable` count, and the selected operation title.
- The existing operation list `Panel`, refresh button, operation table, selected-row marker, and `setSelectedOperation(row)` behavior remain available inside `commercial-server-operation-list-body`.
- The operation selector is folded by default so the Commercial Ops server page opens on status and deliberate action entries instead of a wide table.
- It does not remove operations, remove operation selection, remove refresh, change `operationsForTable`, change commercial operation APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, approve records, reject records, acknowledge intervention records without an operator click, send reminders, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73M Client Runtime Utility Consolidation:

- `worker_console` and `worker_console_desktop` keep `client-top-utility-drawer` as the single compact utility entry and add `data-phase="Phase 73M Client Runtime Utility Consolidation"` to `client-top-utility-body`.
- The existing `WorkstationHome` call now renders inside `client-top-utility-body`, after `client-shell-diagnostics-drawer` and `operator-page-mode-drawer`.
- The existing `client-runtime-companion-drawer`, `client-runtime-companion-body`, runtime controls, language switching, and advanced maintenance details remain reachable inside that compact top utility flow.
- The default customer-machine page body no longer shows the runtime companion as a separate block before the business workbench, making the UI more Codex-like while preserving troubleshooting controls after expansion.
- It does not remove local runtime controls, remove language switching, remove advanced maintenance details, change local worker APIs, change conversation APIs, change upload APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, approve records, reject records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73N Client Production Detail Drawer:

- `worker_console` and `worker_console_desktop` add `simpleProductionDetailCount`, `simpleProductionDetailOutputCount`, `simple-production-details-drawer`, and `simple-production-details-body`.
- The existing `simple-secondary-panels-drawer` and `maintenance-drawer` remain available inside the folded production detail drawer, preserving project context, delivery details, approvals, output preview, and operator selection controls.
- `openClientDetailPanel` walks `detailsAncestor` through `target.closest("details")`, so deep-link actions open all parent detail drawers before scrolling.
- CSS folds `simple-production-details-body` while the drawer is closed, restyles nested detail drawers for the compact body, and hides the closed `client-operation-desk-drawer` from the default first screen while keeping it available for deep-link actions.
- This keeps the customer-machine first screen more Codex-like: status, current goal, current work, and one production detail entry instead of multiple visible lower-frequency panels.
- It does not remove operation details, remove project context, remove approvals, remove output preview, remove material import, remove workflow selection, change local worker APIs, change conversation APIs, change upload APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, approve records, reject records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73O Client Production Index:

- `worker_console` and `worker_console_desktop` add `simple-production-index` inside `simple-production-details-body` with aria label `Phase 73O Client Production Index`.
- The index reuses `clientProjectFocusCards` instead of introducing a second project-state summary.
- Each `simple-production-index-card` calls `openClientDetailPanel(card.targetId)`, giving one compact route to `client-project-section-materials`, `client-project-section-workflows`, `client-project-section-outputs`, `client-project-section-publish`, and the other project record sections.
- CSS adds compact `simple-production-index-head`, `simple-production-index-grid`, and `simple-production-index-card` rules so the expanded production detail drawer remains scannable.
- It does not add a new project state source, remove approvals, remove output preview, remove workflow selection, change local worker APIs, change conversation APIs, change upload APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, approve records, reject records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73P Server Production Index:

- `admin_dashboard` adds `commercial-server-production-index` with aria label `Phase 73P Server Production Index` below the quiet cockpit.
- `commercialServerProductionIndexCards` reuses existing Commercial Ops state for maintenance pressure, `operationsForTable`, selected operation context, `productionClosedLoopActionAudits`, upstream production counts, deliverables, execution runs, and results.
- Each `commercial-server-production-index-card` calls `openCommercialServerDrawer` after an explicit operator click, opening the existing maintenance, operation list, operation context, action audit, upstream production, or closed-loop delivery drawer.
- CSS adds `commercial-server-production-index-head`, `commercial-server-production-index-grid`, and `commercial-server-production-index-card` rules so the server Commercial Ops first screen remains Codex-like and scannable.
- It does not add a new backend state source, remove maintenance details, remove operation selection, remove operation context, remove action audit visibility, change commercial operation APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, approve records, reject records, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73Q Client Production Action Summary:

- `worker_console` and `worker_console_desktop` add the Codex-like `simple-production-action-summary` with aria label `Phase 73Q Client Production Action Summary` before the Phase 73O production index.
- The summary reuses `clientProjectDecisionCards`, `clientProjectCurrentDecision`, `clientProjectSecondaryDecisionCards`, and `clientProjectDecisionTotalCount` instead of introducing a second production review source.
- The current action shows the review label, detail, status badge, primary operator action, optional secondary operator action, and a detail-open button that calls `openClientDetailPanel(clientProjectCurrentDecision.targetId)`.
- Secondary review items render as compact `simple-production-action-chip` buttons that open the existing project sections.
- It does not add a new project state source, remove approvals, remove output preview, remove workflow selection, change local worker APIs, change conversation APIs, change upload APIs, call target endpoints, change env vars, store secrets, configure providers, mark mock providers ready, restart services, auto-refresh readiness, approve records without an operator click, reject records without an operator click, select output candidates without an operator click, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

Phase 73R Production Release Gate Checklist:

- `CommercialOperationProductionClosedLoopAcceptanceSummaryResponse` now exposes `release_ready`, `release_gate_ready_count`, `release_gate_total_count`, `release_gate_status_counts`, and `release_gate_checklist`.
- `app/commercial_operations/service.py` builds `operation_project_readiness`, `customer_machine_execution_handoff`, `real_openclaw_publish_provider`, `customer_machine_publish_result_evidence`, `metric_feedback_and_next_cycle`, and `intervention_queue_clear`.
- The acceptance gates include `production_release_gate_checklist_is_machine_readable`.
- `scripts/check_production_closed_loop.py` reads the checklist into `delivery_audit_summary` and reports `release_gate_blocked_keys`.
- `admin_dashboard` renders `commercial-release-gate-checklist` under `Phase 73R Production Release Gate Checklist`.
- It does not configure providers, run OpenClaw, run Playwright, publish, submit ComfyUI prompts, ingest analytics, restart services, or bypass approval.

Phase 73S Client Codex Single Focus UI:

- `worker_console` and `worker_console_desktop` add `simpleProductionDetailSummary` and `simpleProductionDetailFullSummary`.
- The closed `simple-production-details-drawer` now shows a compact `Production flow` pending count while keeping full approval/material/workflow/output counts in the summary title.
- CSS visually orders `simple-current-work-panel` before `simple-goal-box`, turns `client-top-utility-drawer` into a quiet top utility entry, and makes `simple-production-details-drawer` a lightweight flow link until opened.
- It does not remove approvals, remove output preview, remove material import, remove workflow selection, run OpenClaw, run Playwright, publish, submit ComfyUI prompts, ingest analytics, or bypass approval.

Phase 73T Production Audit Release Gate Fallback:

- `scripts/check_production_closed_loop.py` adds `_release_gate_contract_missing`, `_synthesized_release_gate_checklist`, and `_release_gate_status_counts`.
- If acceptance summary omits `release_gate_checklist`, the audit exposes `release_gate_contract_missing=true`, `release_gate_source=audit_synthesized_from_acceptance_summary`, six synthesized gates, and meaningful `release_gate_blocked_keys`.
- The audit adds blocker `acceptance_summary:release_gate_checklist_missing` and next action `deploy_release_gate_acceptance_summary_contract`.
- It does not mark old API contracts production-ready, restart services automatically, configure providers, run OpenClaw, run Playwright, publish, submit ComfyUI prompts, ingest analytics, or bypass approval.

Phase 73U Client Visual Approval Workbench:

- `worker_console` and `worker_console_desktop` derive `simpleApprovalDeskPlan`, `simpleApprovalDeskWorkflow`, `simpleApprovalDeskOutputCandidates`, and `simpleApprovalDeskKnowledgeState`.
- The first customer-machine workbench flow is now goal input, `simple-approval-workbench`, current work, and folded production detail.
- The workbench surfaces operation plan visual approval, ComfyUI image/video output previews, workflow selection, and RAG knowledge update access from one compact area.
- It reuses existing operator-click handlers and does not approve records automatically, submit ComfyUI prompts, mutate workflow JSON, run OpenClaw, run Playwright, publish, ingest analytics, restart services automatically, or bypass approval.

Phase 73V Client Project Conversation Workspace:

- `worker_console` and `worker_console_desktop` keep `commercialOperations` and derive `simpleProjectOptions`, `simpleSelectedCommercialOperation`, `simpleConversationMessages`, and `simplePlanReviewState`; `simpleNewProjectDraftActive` prevents refresh from auto-selecting the first existing project while the worker is drafting a new operation.
- The first customer-machine layer is now project selection, one large chat workspace, RAG context access, and the overall operation plan review card.
- `submitSimpleOperationGoal` records the user message and calls `advanceMainAgentLoop` with `plan_first_goal_submit=true`; it does not use the generic conversation playbook as the primary operation-plan path, and the backend forces this flag to `operation_strategy` when another router track would otherwise take over.
- `simple-project-delete` uses `commercialOperationClient.delete` to archive-delete a project and hide it from the default project picker without physically cascading child records.
- `advanceMainAgentProjectStep` is the generate-plan path; `regenerateOperationPlanFromSimpleWorkspace` rejects the current pending plan before requesting a regenerated reviewable plan.
- manual approval remains required before the worker moves from the overall operation plan into downstream image/video/audio/workflow production.
- It does not guarantee RAG citation quality, approve plans automatically, physically delete project children, submit ComfyUI prompts, mutate workflow JSON, run OpenClaw, run Playwright, publish, ingest analytics, restart services automatically, or bypass approval.

Profile status values:

```text
available
locked
disabled
corrupted
deleted
```

Profile health status values:

```text
healthy
warning
corrupted
stale
deleted
```

Playwright safety boundary:

- Allowed: `example.com`, local test pages, static `file://` URLs.
- Not allowed: TikTok, YouTube, X, automatic login, cookie injection, fingerprint bypass, proxy pools, captcha automation, OCR, visual AI, autonomous browser planning, or remote Browser Worker execution.

Remote Browser Worker tables:

- `browser_workers`
- `browser_worker_sessions`
- `browser_worker_actions`
- `openclaw_action_logs`

Phase 21 worker reliability fields:

- `browser_workers.max_sessions`
- `browser_workers.active_sessions`
- `browser_workers.max_actions_per_minute`
- `browser_workers.current_load`
- `browser_workers.priority`
- `browser_workers.error_message`
- `browser_workers.last_heartbeat_at` is exposed as `last_seen`
- `browser_worker_actions.retry_count`
- `browser_worker_actions.max_retries`

Reliability services:

- `BrowserWorkerHealthService`
- `BrowserWorkerSelector`
- `BrowserSessionCleanupService`
- `ScreenshotCleanupService`

Selection flow:

```text
workspace_id
-> online workers
-> capability filter
-> active_sessions < max_sessions
-> least loaded worker by current_load / active_sessions / priority
```

Cleanup flow:

```text
stale worker -> offline + error_message
stale session -> closed
offline/error worker session -> failed
screenshot cleanup -> dry_run by default
```

Remote Browser Worker status values:

```text
online
offline
busy
error
```

Remote mode:

```env
BROWSER_PROVIDER=remote
BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30
BROWSER_WORKER_RETRY_COUNT=2
BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100
BROWSER_WORKER_AUTH_ENABLED=true
BROWSER_WORKER_AUTH_STRICT=true
BROWSER_WORKER_SHARED_SECRET=<server-private-secret>
BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60
BROWSER_ACTION_TIMEOUT_SECONDS=60
BROWSER_ACTION_RETRY_COUNT=2
BROWSER_ACTION_RETRY_BACKOFF_SECONDS=2
SCREENSHOT_RETENTION_DAYS=7
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=true
OPENCLAW_ACTION_TIMEOUT_SECONDS=60
```

Real Browser Worker Service:

```text
API Server
-> RemoteBrowserProvider
-> BrowserWorkerClient
-> http://browser-worker:9100
-> worker/main.py
-> worker/browser_worker/playwright_runtime.py
-> Playwright Chromium
-> worker/screenshots/{workspace_id}/{remote_session_id}/{filename}.png
```

The worker exposes:

```http
GET http://localhost:9100/health
POST http://localhost:9100/sessions
POST http://localhost:9100/actions
POST http://localhost:9100/sessions/{session_id}/close
POST http://localhost:9100/browser/session/create
POST http://localhost:9100/browser/session/{session_id}/navigate
POST http://localhost:9100/browser/session/{session_id}/screenshot
GET  http://localhost:9100/browser/session/{session_id}/page
POST http://localhost:9100/browser/session/{session_id}/close
```

The API Server still uses the database-backed registration flow. Register the worker with:

```json
{
  "worker_name": "browser-worker",
  "worker_type": "playwright",
  "base_url": "http://browser-worker:9100",
  "capabilities": {
    "browser": "chromium",
    "screenshot": true,
    "page_content": true
  },
  "metadata": {
    "phase": "20"
  }
}
```

Remote worker safety boundary:

- Current runtime now includes an independent local Docker `browser-worker` service.
- The old in-process mock worker runtime remains available for protocol tests.
- On the production server, the local Browser Worker is managed by the `AI Ops Browser Worker` Windows startup task and verified by `deployment/windows/verify_browser_worker_aiops.ps1`.
- Strict signed requests are enabled for mutating/session endpoints. The API and worker must share `BROWSER_WORKER_SHARED_SECRET`; the worker process receives it as `BROWSER_WORKER_SECRET`.
- Production external worker fleets, worker scheduling, autoscaling, and remote machine deployment are not included.
- No TikTok, YouTube, X, automatic login, cookie injection, fingerprint bypass, proxy pool, captcha automation, OCR, visual AI, or autonomous browser planning.

Current limitations:

- Real browser execution is available through `playwright_local` and the remote Browser Worker runtime, but the remote provider still requires database worker registration in the target workspace before Main Agent selection.
- No Selenium, real OpenClaw, TikTok, YouTube, X, OCR, visual AI, login automation, or real platform publishing automation.
- No autonomous browser agent or browser planning loop.

## Mock vs Local

Current default mock components:

- `LLM_PROVIDER=mock`
- `EMBEDDING_PROVIDER=mock`
- `RERANKER_PROVIDER=mock`

Supported local components:

- Ollama LLM: `LOCAL_LLM_MODEL=mistral`
- Ollama embedding: `LOCAL_EMBEDDING_MODEL=bge-m3`
- Local semantic reranker worker: `worker.reranker_worker.main:app` on port `8002`, using `RERANKER_RUNTIME_ENGINE=ollama_embedding`.

The local reranker worker calls the configured Ollama embedding model and returns `/api/rerank` scores. It is a formal semantic reranker baseline, not a cross-encoder model.

## Embedding Dimension

In mock mode:

```text
EMBEDDING_DIMENSION=384
```

In local `bge-m3` mode, the embedding dimension is detected from the first health or embedding call and stored in `collections_metadata.embedding_dimension`. If an existing collection has a different dimension, the system rejects the write to avoid mixed vectors.

## Docker Runtime

Start services:

```powershell
docker compose up --build -d
```

Swagger:

```text
http://localhost:8000/docs
```

Core health checks:

```http
GET /api/v1/health
GET /api/v1/llm/health
GET /api/v1/rag/embedding/health
GET /api/v1/reranker/health
GET /api/v1/observability/summary
GET /api/v1/tools
GET /api/v1/tool-calls
GET /api/v1/openclaw/health
GET /api/v1/openclaw/capabilities
POST /api/v1/memory/sessions
POST /api/v1/memory/messages
POST /api/v1/memory/memories
GET /api/v1/agents/registry
POST /api/v1/multi-agent/runs
POST /api/v1/multi-agent/runs/{run_id}/execute-chain
POST /api/v1/plans
POST /api/v1/plans/{plan_id}/execute
GET /api/v1/plans/{plan_id}/steps
GET /api/v1/plans/{plan_id}/reviews
GET http://localhost:9100/health
```

## Switching to Local Ollama

Create a local `.env` file or set environment variables:

```env
LLM_PROVIDER=local
LOCAL_LLM_BASE_URL=http://host.docker.internal:11434
LOCAL_LLM_MODEL=mistral

EMBEDDING_PROVIDER=local
LOCAL_EMBEDDING_BASE_URL=http://host.docker.internal:11434
LOCAL_EMBEDDING_MODEL=bge-m3

RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
BROWSER_PROVIDER=mock
BROWSER_TIMEOUT_SECONDS=30.0
BROWSER_HEADLESS=True
BROWSER_TYPE=chromium
BROWSER_VIEWPORT_WIDTH=1280
BROWSER_VIEWPORT_HEIGHT=720
BROWSER_SCREENSHOT_DIR=screenshots
BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
BROWSER_PROFILE_ROOT=worker/profiles
BROWSER_WORKER_AUTH_ENABLED=true
BROWSER_WORKER_AUTH_STRICT=false
BROWSER_ALLOWED_DOMAINS=example.com,localhost,127.0.0.1
BROWSER_BLOCKED_DOMAINS=
BROWSER_ALLOW_EXTERNAL_DOMAINS=false
BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30
BROWSER_WORKER_RETRY_COUNT=2
BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100
BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60
BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS=30
BROWSER_SESSION_TIMEOUT_SECONDS=1800
BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS=300
BROWSER_ACTION_TIMEOUT_SECONDS=60
BROWSER_ACTION_RETRY_COUNT=2
BROWSER_ACTION_RETRY_BACKOFF_SECONDS=2
SCREENSHOT_RETENTION_DAYS=7
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=true
OPENCLAW_ACTION_TIMEOUT_SECONDS=60
```

Restart:

```powershell
docker compose up --build -d
```

To test Playwright local mode:

```env
BROWSER_PROVIDER=playwright_local
BROWSER_TIMEOUT_SECONDS=30
BROWSER_HEADLESS=true
BROWSER_TYPE=chromium
BROWSER_VIEWPORT_WIDTH=1280
BROWSER_VIEWPORT_HEIGHT=720
BROWSER_SCREENSHOT_DIR=screenshots
BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
BROWSER_PROFILE_ROOT=worker/profiles
```

Restart with Docker Compose and smoke test `POST /api/v1/browser/sessions`, `POST /api/v1/browser/actions` with `navigate` to `https://example.com`, `screenshot`, `get_page_content`, and `GET /api/v1/browser/screenshot/{session_id}/{filename}`.

## Switching Back to Mock

```env
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
BROWSER_PROVIDER=mock
BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS=30
BROWSER_WORKER_RETRY_COUNT=2
BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100
BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS=60
BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS=30
BROWSER_SESSION_TIMEOUT_SECONDS=1800
BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS=300
BROWSER_ACTION_TIMEOUT_SECONDS=60
BROWSER_ACTION_RETRY_COUNT=2
BROWSER_ACTION_RETRY_BACKOFF_SECONDS=2
SCREENSHOT_RETENTION_DAYS=7
OPENCLAW_PROVIDER=mock
OPENCLAW_ENABLED=true
OPENCLAW_ACTION_TIMEOUT_SECONDS=60
```

Restart:

```powershell
docker compose up --build -d
```

## Docs Runtime Verification

Run:

```powershell
python scripts/verify_docs_runtime.py
```

Expected final line:

```text
SUMMARY: PASS
```

## Phase 29 Worker Client Local Runtime

Current customer-machine Worker Client defaults:

```text
worker_client runtime_host=127.0.0.1
worker_client runtime_port=9100
worker_client status=worker_client/runtime_state/status.json
worker_client logs=worker_client/logs/worker.log
```

Completed Phase 29 runtime files:

- `Worker Runtime Manager`: `worker_client/runtime_manager.py`
- local status: `worker_client/status.py`
- local logging: `worker_client/logging.py`
- local API client: `worker_client/local_api_client.py`
- status file: `worker_client/runtime_state/status.json`
- log file: `worker_client/logs/worker.log`
- packaging scripts: `packaging/windows_start_worker.ps1`, `packaging/mac_start_worker.sh`
- desktop placeholder: `worker_client/desktop/README.md`

Local management API exposed by `worker_client.runtime`:

- `GET /local/status`
- `GET /local/health`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`
- `GET /local/logs`

Phase 29 is `Worker Console Foundation` only: no GUI, no Electron, no Tauri, no PySide, no system tray, no EXE/DMG packaging, and no real platform automation.

## Phase 30 Worker Console Runtime

Worker Console frontend defaults:

```text
worker_console stack=Vite + React + TypeScript + Tailwind
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
worker_console dev_url=http://localhost:5173
```

Runtime relationship:

- `worker_console` calls the local Worker Client API from Phase 29.
- Default local status URL: `http://127.0.0.1:9100/local/status`.
- Frontend client: `worker_console/src/api/localWorkerClient.ts`.
- If the API is down, the UI shows `Worker API unreachable`, `请确认 worker_client 是否启动`, and `请确认端口是否为 9100`.

Current boundary: Worker Console GUI Foundation only; no system tray, no auto update, no Electron, no Tauri, no PySide, no exe / dmg packaging.

## Phase 31 Worker Console Desktop Runtime

Worker Console Desktop defaults:

```text
worker_console_desktop stack=Tauri + React + Vite + TypeScript + Tailwind
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
worker_console_desktop dev_url=http://127.0.0.1:5174
worker_console_desktop status_url=http://127.0.0.1:9100/local/status
```

Runtime relationship:

- `worker_console_desktop` calls the same local Worker Client API as `worker_console`.
- Desktop local API client: `worker_console_desktop/src/api/localWorkerClient.ts`.
- Tauri config: `worker_console_desktop/src-tauri/tauri.conf.json`.
- Development command: `npm run tauri dev`.
- Frontend validation command: `npm run build`.
- If the local Worker API is down, the UI shows `Worker API unreachable`, `Worker Runtime 未启动`, `请先启动 worker_client`, and `packaging 脚本启动`.

Current boundary: Worker Console Desktop App Foundation only; no exe / dmg, no system tray, no auto update, no autostart, and no formal installer release.

## Phase 32 Worker Console System Tray & Desktop Runtime Foundation

Worker Console Desktop runtime defaults:

```text
worker_console_desktop stack=Tauri System Tray + React + Vite + TypeScript + Tailwind
localWorkerApi=http://127.0.0.1:9100
minimizeToTray=true
refreshIntervalMs=5000
desktop_runtime_config=worker_console_desktop/src-tauri/desktop-runtime.json
settings_example=worker_console_desktop/settings.example.json
```

Runtime behavior:

- System Tray menu: Show Console, Hide Window, Start Runtime, Stop Runtime, Restart Runtime, Start Heartbeat, Stop Heartbeat, Refresh Status, Quit.
- Minimize To Tray: closing the window hides it instead of exiting.
- Tray Runtime Control calls only local Worker Client API endpoints.
- Desktop Status Sync calls `GET /local/status` and `GET /local/health`.
- Tooltip fields: `worker_name`, `current_status`, `runtime_running`, `heartbeat_running`.
- Connection states shown in UI: connected, reconnecting, disconnected, online, offline, error.
- AutoStart Placeholder docs exist, but no real start-on-login registration is performed.

Current boundary: no formal installer, no exe / dmg, no real autostart registration, no auto-update, no remote shell, and no arbitrary command execution.

## Phase 33 Runtime Notes

Conversation Runtime adds no new environment variable. It depends on the existing workspace headers and existing provider defaults.

Current defaults remain:

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
BROWSER_PROVIDER=mock
OPENCLAW_PROVIDER=mock
```

Conversation APIs require:

```text
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

Worker Console chat clients use:

```text
VITE_AI_SERVER_API=http://localhost:8000/api/v1
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

Event feed mode: polling only through `GET /api/v1/conversations/{thread_id}/events`. WebSocket and SSE are placeholders only.

## Phase 34 Remote Browser Runtime

Remote Browser Runtime adds one runtime storage setting and keeps the existing browser safety boundaries.

```text
BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
```

Current runtime behavior:

- API Server dispatches browser runtime actions through `RemoteBrowserProvider`.
- Remote worker browser runtime lives under `worker_client/browser_runtime`.
- Worker runtime API uses `/browser/session/create`, `/browser/session/{session_id}/navigate`, `/browser/session/{session_id}/screenshot`, `/browser/session/{session_id}/page`, and `/browser/session/{session_id}/close`.
- Runtime sessions are stored in `browser_runtime_sessions`.
- Screenshots are stored locally under `storage/browser_screenshots`.
- Customer machines must install Playwright Chromium with `playwright install chromium`.

Current boundary: no stealth browser, no proxy rotation, no cookie injection, no captcha bypass, no TikTok / YouTube / X automation, no remote desktop streaming, and no DevTools remote control.

## Phase 35A Browser Runtime Observability & Replay

Phase 35A adds runtime observability storage and APIs. It does not add live streaming, VNC/noVNC, DevTools remote control, or replay re-execution.

Runtime setting:

```text
BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
```

Runtime tables:

- `browser_runtime_events`
- `browser_runtime_snapshots`
- `browser_runtime_replays`

Runtime APIs:

- `GET /api/v1/browser-runtime/sessions/{session_id}/events`
- `GET /api/v1/browser-runtime/sessions/{session_id}/snapshots`
- `POST /api/v1/browser-runtime/sessions/{session_id}/replay`
- `GET /api/v1/browser-runtime/replays/{replay_id}`
- `GET /api/v1/browser-runtime/replays/{replay_id}/export`

Storage:

```text
storage/browser_runtime_snapshots/{workspace_id}/{session_id}/page-{snapshot_id}.html
storage/browser_runtime_snapshots/{workspace_id}/{session_id}/page-{snapshot_id}.txt
storage/browser_runtime_snapshots/{workspace_id}/{session_id}/error-{snapshot_id}.json
storage/browser_runtime_snapshots/{workspace_id}/{session_id}/replay-{replay_id}.json
```

Timeline events include `session_created`, `navigate_started`, `navigate_completed`, `screenshot_started`, `screenshot_completed`, `page_snapshot_captured`, `action_failed`, `session_closed`, and `replay_requested`.

Replay is metadata-only. It exports readable timeline and snapshot references; it does not re-run browser actions.

## Phase 35B Real Client Worker E2E Runtime Notes

Phase 35B adds no new service environment variable. It adds `scripts/validate_real_client_worker_e2e.py`, a validation script that checks whether a real customer-machine worker is online before executing browser actions.

Runtime facts:

```text
Expected remote worker capability: browser_runtime=true
Expected browser: chromium
Expected test domain: example.com
Screenshot directory: BROWSER_RUNTIME_SCREENSHOT_DIR=storage/browser_screenshots
Snapshot directory: BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots
```

If `BROWSER_PROVIDER` is not `remote`, the script prints a WARNING only. The browser runtime API is still directly testable, but legacy browser action APIs may continue to use the configured provider.

If the configured `expected_worker_name` is not online, the script returns `SKIPPED` with exit code `2` and reason `real client worker not online`. This is intentional because Phase 35B is a validation plan and script, not a fabricated real-client E2E result.

## Phase 36 Admin Dashboard Runtime

Phase 36 adds a frontend-only Admin Dashboard Foundation. It does not add new backend environment variables.

Frontend runtime config:

```text
VITE_AI_SERVER_API=http://localhost:8000
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

Runtime facts:

- Project path: `admin_dashboard`
- API client: `admin_dashboard/src/api/client.ts`
- Default AI Server URL: `http://localhost:8000`
- Required headers: `X-Workspace-Id` and `X-User-Id`
- Stored local settings: `aiServerUrl`, `workspaceId`, `userId`
- Auto refresh default: 10000 ms
- Pages: Overview, Workers, Browser Runtime, Conversations, Tasks, OpenClaw, Audit Logs, RAG / Documents, Settings
- API modules: `workersApi`, `browserRuntimeApi`, `conversationsApi`, `tasksApi`, `openclawApi`, `auditApi`, `ragApi`

The dashboard is a read-only monitoring foundation. It has no login UI, no permission UI, no publishing business flow, no real social platform control, and no production-grade operations backend.

## Phase 37 Conversation Frontend Runtime

Phase 37 adds no production authentication layer and no real streaming transport. It adds frontend configuration and development CORS for Conversation Runtime UI integration.

Frontend runtime defaults:

```text
VITE_AI_SERVER_API=http://localhost:8000
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
VITE_LOCAL_WORKER_API=http://127.0.0.1:9100
```

Backend CORS runtime:

```text
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5180,http://127.0.0.1:5180,http://localhost:5181,http://127.0.0.1:5181,tauri://localhost
```

Conversation frontend API coverage:

```text
POST /api/v1/conversations
GET /api/v1/conversations
GET /api/v1/conversations/{thread_id}
POST /api/v1/conversations/{thread_id}/messages
GET /api/v1/conversations/{thread_id}/messages
GET /api/v1/conversations/{thread_id}/events
POST /api/v1/conversations/{thread_id}/run
```

Current mode: Polling Event Timeline only. The implementation is not WebSocket, not SSE, and not a full ChatGPT UI.

## Phase 38 Runtime: Conversation Tool Execution Bridge

Current bridge mode:
- `ConversationToolRouter`: enabled.
- Routing mode: deterministic rule-based routing, not autonomous agent planning.
- Tool bridge events: `route_selected`, `tool_execution_started`, `tool_execution_completed`, `tool_execution_failed`, `agent_execution_started`, `agent_execution_completed`, `planning_execution_started`, `planning_execution_completed`, `bridge_fallback`, `bridge_error`.
- Run response fields: `route_name`, `selected_tool`, `events_created`, `success`, `summary`, `result_metadata`.
- Browser bridge: uses `browser_tool` composite flow for create session, navigate, screenshot, get page, and close session when browser runtime is available.
- OpenClaw bridge: mock only through `openclaw_tool`; no real OpenClaw and no real device execution.
- RAG bridge: requires `collection_name` from thread metadata or run input.
- Content bridge: calls `ContentAgent`.
- Planning bridge: calls `PlanningService` to create a plan and steps.

Current limitations: not WebSocket, not SSE, not an autonomous agent, not real OpenClaw, not ComfyUI, and not real platform publishing.

## Phase 39 Runtime: Conversation Approval Flow

Current approval mode:
- `conversation_approvals`: enabled.
- `ConversationApprovalService`: enabled for create / approve / reject / cancel / execute state flow.
- `ConversationRiskPolicy`: enabled for `low`, `medium`, and `high` risk classification.
- Run modes: `auto_safe`, `review_first`, `execute_after_approval`.
- Default run mode: `auto_safe`.
- Tool Execution Gate: medium/high risk actions remain pending until approval; approved actions are executed through `POST /api/v1/conversation-approvals/{approval_id}/execute`.

Approval API coverage:

```text
GET /api/v1/conversations/{thread_id}/approvals
GET /api/v1/conversation-approvals/{approval_id}
POST /api/v1/conversation-approvals/{approval_id}/approve
POST /api/v1/conversation-approvals/{approval_id}/reject
POST /api/v1/conversation-approvals/{approval_id}/cancel
POST /api/v1/conversation-approvals/{approval_id}/execute
```

Approval event coverage:

```text
approval_required
approval_created
approval_approved
approval_rejected
approval_cancelled
approval_expired
approval_executed
execution_blocked_pending_approval
execution_after_approval_started
execution_after_approval_completed
execution_after_approval_failed
```

Current limitations: this is not a full permission system, not WebSocket/SSE streaming, not real platform publishing, not real OpenClaw, and not autonomous agent execution.
## Phase 40 Runtime Addendum: Conversation Playbooks

Current Playbook runtime is enabled in the API server and uses the existing Conversation Runtime, ToolRegistry, ContentAgent, PlanningService, browser_tool, rag_search_tool, and openclaw_tool mock bridge.

Database tables:
- `conversation_playbooks`
- `conversation_playbook_runs`

API routes:
- `GET /api/v1/conversation-playbooks`
- `GET /api/v1/conversation-playbooks/{playbook_id}`
- `POST /api/v1/conversation-playbooks`
- `PATCH /api/v1/conversation-playbooks/{playbook_id}`
- `POST /api/v1/conversation-playbooks/{playbook_id}/run`
- `GET /api/v1/conversation-playbook-runs`
- `GET /api/v1/conversation-playbook-runs/{run_id}`
- `POST /api/v1/conversation-playbook-runs/{run_id}/cancel`

Conversation run supports `playbook_name`, `playbook_run_id`, and `playbook_status`. Playbook steps still respect `review_first`, `auto_safe`, and `execute_after_approval`.

Current defaults remain unchanged: no real OpenClaw, no real social-platform publishing, no proxy/fingerprint/captcha handling, and no full workflow editor.

## Phase 41 Runtime Addendum: Output Library

Current Output Library runtime is enabled in the API server and stores reusable execution outputs in `output_artifacts`.

Storage:
- `OUTPUT_ARTIFACT_DIR=storage/output_artifacts`
- Exported markdown/json/txt files use `storage/output_artifacts/{workspace_id}/{artifact_id}/`
- Screenshot and HTML snapshot artifacts reference existing file paths; large files are not copied.

API routes:
- `GET /api/v1/output-artifacts`
- `GET /api/v1/output-artifacts/{artifact_id}`
- `PATCH /api/v1/output-artifacts/{artifact_id}`
- `DELETE /api/v1/output-artifacts/{artifact_id}`
- `POST /api/v1/output-artifacts/from-message/{message_id}`
- `POST /api/v1/output-artifacts/from-playbook-run/{run_id}`
- `GET /api/v1/output-artifacts/{artifact_id}/export`

Events:
- `artifact_created`
- `artifact_exported`
- `artifact_deleted`
- `artifact_linked_to_playbook_run`

Current boundaries remain unchanged: no S3, no MinIO, no full DAM, no production-grade file manager, no real platform publishing, and no social-platform automation.
## Phase 42 Runtime Configuration

Task Orchestration defaults are now part of runtime config and docker-compose:

- `TASK_ORCHESTRATOR_ENABLED=true`
- `TASK_ORCHESTRATOR_POLL_INTERVAL_SECONDS=2.0`
- `TASK_ORCHESTRATOR_BATCH_SIZE=5`
- `TASK_RUN_DEFAULT_MAX_RETRIES=3`

The background executor is `BackgroundTaskExecutor`, started from FastAPI lifespan when enabled. It polls `task_runs` in-process and executes Conversation / Playbook work through `TaskOrchestratorService`. This is not Celery, not RabbitMQ, not Kubernetes, and not production HA.
## Phase 43 Runtime Configuration: Task Scheduler Persistence & Worker Recovery

Task Scheduler Persistence is enabled through the existing in-process `BackgroundTaskExecutor`; it remains a foundation, not Celery, not Kubernetes, and not production HA distributed queue.

| Key | Current default | Meaning |
| --- | --- | --- |
| `TASK_SCHEDULER_NAME` | `api-in-process-task-scheduler` | Stable scheduler identity used for `task_scheduler_state` and task lease ownership. |
| `TASK_LEASE_SECONDS` | `120` | Lease duration assigned to running `task_runs`. Expired lease is eligible for recovery. |
| `TASK_STUCK_TIMEOUT_SECONDS` | `300` | Heartbeat staleness threshold for stuck running task recovery. |
| `TASK_SCHEDULER_RECOVERY_INTERVAL_SECONDS` | `10.0` | Background recovery scan interval for scheduled, retrying, and stuck tasks. |

Runtime tables and fields:

- `task_scheduler_state` stores scheduler status, heartbeat, last scan, active task count, recovered task count, and metadata.
- `task_runs` now includes `lease_owner`, `lease_token`, `lease_expires_at`, `heartbeat_at`, `recovery_count`, `last_recovered_at`, `recovery_reason`, `failure_category`, `failure_reason`, `recoverable`, `suggested_action`, and `last_event_summary`.

Core APIs:

- `GET /api/v1/task-scheduler/health`
- `POST /api/v1/task-scheduler/scan`
- `GET /api/v1/task-runs/{task_run_id}/diagnostics`
- `POST /api/v1/task-runs/{task_run_id}/recover`

Recovery rules:

- `running` task with expired lease or stale heartbeat becomes `retrying` when retry budget remains, otherwise `failed`.
- `pending` task with `scheduled_at <= now` becomes `queued`.
- `retrying` task with retry delay elapsed becomes `queued`.
- `waiting_approval` is not auto-executed and must resume through approval flow.
- `completed`, `cancelled`, and `expired` tasks are not recovered.

Admin Dashboard now shows Scheduler Health, lease status, recoverable badge, diagnostics panel, and manual recover control. Worker Console Web/Desktop show simplified scheduler and task recovery status.

Runtime verifier marker: TASK_SCHEDULER_RECOVERY_INTERVAL_SECONDS=10.0

<!-- PHASE44_RUNTIME:START -->
## Phase 44 Output Artifact Pipeline Runtime

| Key | Current default | Meaning |
| --- | --- | --- |
| `OUTPUT_ARTIFACT_DIR` | `storage/output_artifacts` | Output Artifact text/export metadata root. |
| `OUTPUT_PACKAGE_DIR` | `storage/output_packages` | Package artifact and bundle metadata root. |
| `OUTPUT_EXPORT_DIR` | `storage/output_exports` | Exported markdown/html/json/txt/bundle output root. |

Phase 44 adds Artifact lineage, relationship graph, `artifact_relationships`, `ArtifactExportService`, `ArtifactPackagingService`, and `ArtifactRetentionService`. Exports are based only on existing artifacts; they do not re-run Browser Runtime, Playbook, Conversation, Task, or OpenClaw mock actions.

New APIs:

- `GET /api/v1/output-artifacts/{artifact_id}/lineage`
- `GET /api/v1/output-artifacts/{artifact_id}/relationships`
- `POST /api/v1/output-artifacts/{artifact_id}/export`
- `POST /api/v1/output-artifacts/{artifact_id}/package`
- `POST /api/v1/output-artifacts/cleanup/preview`

Current boundaries: not a full DAM, not a production object storage platform, no production S3 / MinIO / CDN, no real social platform publishing, no real OpenClaw, and no ComfyUI.
<!-- PHASE44_RUNTIME:END -->

<!-- PHASE45_RUNTIME:START -->
## Phase 45 Runtime: Workflow State & Agent Memory Foundation

Runtime database tables:

- `workflow_runs`
- `workflow_steps`
- `workflow_checkpoints`
- `agent_memory_snapshots`

Runtime service: `WorkflowStateService` is used by Conversation, Playbook, Task Orchestration, and Output Artifact lineage integration. It records `workflow_run_created`, `workflow_step_started`, `workflow_step_completed`, `workflow_checkpoint_created`, `workflow_paused`, `workflow_resumed`, and `memory_snapshot_created` events when a workflow is linked to a conversation thread.

Runtime API routes:

- `GET /api/v1/workflow-runs`
- `GET /api/v1/workflow-runs/{workflow_run_id}`
- `GET /api/v1/workflow-runs/{workflow_run_id}/steps`
- `GET /api/v1/workflow-runs/{workflow_run_id}/checkpoints`
- `POST /api/v1/workflow-runs/{workflow_run_id}/pause`
- `POST /api/v1/workflow-runs/{workflow_run_id}/resume`
- `GET /api/v1/workflow-runs/{workflow_run_id}/memory-snapshots`
- `GET /api/v1/agent-memory-snapshots`

Artifact lineage fields: `workflow_run_id`, `workflow_step_id`, `checkpoint_id`, and `memory_snapshot_id`.

Boundaries: not a full workflow builder, not ComfyUI, not WebSocket/SSE streaming, not real platform automation.
<!-- PHASE45_RUNTIME:END -->

<!-- PHASE46_RUNTIME:START -->
## Phase 46 Runtime: Workflow Graph Runtime & Conditional Execution

Runtime database tables:

- `workflow_graphs`
- `workflow_graph_nodes`
- `workflow_graph_edges`
- `workflow_replays`

Runtime services:

- `WorkflowExecutionPlanner` validates graphs, resolves entry nodes, performs topological traversal, detects cycles, plans next nodes, tracks dependency state, and exposes retry/fallback paths.
- `SafeConditionEvaluator` evaluates only safe condition expressions over `workflow.variables`, `workflow.status`, `step.output`, `artifact.metadata`, and `approval.status`. It supports `==`, `!=`, `and`, `or`, `in`, and `exists`, and does not use Python `eval`.
- `WorkflowGraphService` creates, lists, gets, and validates workflow graph definitions.
- `WorkflowStateService` records graph execution metadata on workflow runs and steps.

Runtime API routes:

- `GET /api/v1/workflow-graphs`
- `POST /api/v1/workflow-graphs`
- `GET /api/v1/workflow-graphs/{graph_id}`
- `POST /api/v1/workflow-graphs/{graph_id}/validate`
- `POST /api/v1/workflow-runs/{workflow_run_id}/replay`
- `GET /api/v1/workflow-runs/{workflow_run_id}/graph`
- `GET /api/v1/workflow-runs/{workflow_run_id}/planner`

Runtime fields:

- `workflow_runs.workflow_graph_id`
- `workflow_runs.graph_execution`
- `workflow_runs.current_node_key`
- `workflow_runs.planned_next_nodes`
- `workflow_runs.skipped_nodes`
- `workflow_runs.retry_state`
- `workflow_runs.fallback_state`
- `workflow_steps.node_key`
- `workflow_steps.parent_node_key`
- `workflow_steps.dependency_state`
- `output_artifacts.producing_node_key`
- `output_artifacts.replay_source`
- `output_artifacts.graph_lineage`
- `agent_memory_snapshots.node_key`

Boundaries: current replay is metadata-only and does not re-run actions. The runtime is not a visual DAG builder, not a distributed orchestration engine, not ComfyUI, not WebSocket/SSE streaming, and not real platform automation.
<!-- PHASE46_RUNTIME:END -->

<!-- PHASE47_RUNTIME:START -->
## Phase 47 Runtime: Workflow Template Registry & Versioning

Runtime database tables:

- `workflow_templates`
- `workflow_template_versions`
- `workflow_template_runs`

Runtime services:

- `WorkflowTemplateRegistryService` manages template listing, creation, immutable version creation, active version activation, validation, import/export, template runs, and built-in template seeding.
- `WorkflowTemplateCompatibilityService` checks required node types, input_schema, output_schema, graph definition validation, risk_level, runtime capabilities, warnings, errors, and missing capabilities.

Built-in template keys:

- `browser_screenshot_report_graph`
- `content_generation_graph`
- `rag_answer_graph`
- `approval_then_browser_graph`
- `openclaw_mock_inspect_graph`
- `task_retry_demo_graph`

Runtime API routes:

- `GET /api/v1/workflow-templates`
- `POST /api/v1/workflow-templates`
- `GET /api/v1/workflow-templates/{template_id}`
- `POST /api/v1/workflow-templates/{template_id}/versions`
- `GET /api/v1/workflow-templates/{template_id}/versions/{version_id}`
- `POST /api/v1/workflow-templates/{template_id}/activate-version/{version_id}`
- `POST /api/v1/workflow-templates/{template_id}/validate`
- `POST /api/v1/workflow-templates/{template_id}/run`
- `GET /api/v1/workflow-template-runs`
- `GET /api/v1/workflow-template-runs/{run_id}`
- `POST /api/v1/workflow-templates/import`
- `GET /api/v1/workflow-templates/{template_id}/export`

Runtime fields:

- `workflow_templates.template_key`
- `workflow_templates.current_version`
- `workflow_templates.latest_version`
- `workflow_template_versions.validation_status`
- `workflow_template_versions.compatibility`
- `task_runs.workflow_template_id`
- `task_runs.workflow_template_version_id`
- `task_runs.workflow_template_run_id`
- `output_artifacts.workflow_template_id`
- `output_artifacts.workflow_template_version_id`
- `output_artifacts.workflow_template_run_id`
- `agent_memory_snapshots.workflow_template_id`
- `agent_memory_snapshots.workflow_template_version_id`
- `agent_memory_snapshots.workflow_template_run_id`

Frontend clients:

- `admin_dashboard/src/api/workflowTemplateClient.ts`
- `worker_console/src/api/workflowTemplateClient.ts`
- `worker_console_desktop/src/api/workflowTemplateClient.ts`

Boundaries: Template Library is a registry and run foundation only. It is not a visual DAG builder, not a drag/drop graph editor, not ComfyUI, not WebSocket/SSE streaming, and not real platform automation.
<!-- PHASE47_RUNTIME:END -->

<!-- PHASE48_SYNC:START -->
## Phase 48: Workflow Template Marketplace & Governance Foundation

Status: completed.

Phase 48 adds an internal Workflow Template Marketplace & Governance foundation on top of Phase 47 Workflow Template Registry & Versioning. It is an internal template library and governance layer, not public marketplace, not a paid marketplace, not multi-tenant SaaS marketplace, not a visual DAG editor, and not ComfyUI.

Completed scope:

- Added `workflow_template_reviews` for review queue, `review_status`, `risk_assessment`, `compatibility_report`, approve / reject / request changes.
- Added `workflow_template_promotions` to record activate, rollback, deprecate, and archive lifecycle events with `promotion_type`, source version, target version, and reason.
- Added `workflow_template_audit_logs` for governance audit trail, actor, previous_state, new_state, and metadata.
- Added `workflow_template_compatibility_matrix` for runtime capabilities: `browser_runtime`, `approval_gate`, `task_scheduler`, `artifact_pipeline`, `workflow_graph_runtime`, `openclaw_mock`, and `rag_pipeline`.
- Added `WorkflowTemplateGovernanceService` with `submit_for_review`, `approve_review`, `reject_review`, `request_changes`, `activate_template_version`, `rollback_template_version`, `deprecate_template`, `archive_template`, `list_review_queue`, and `list_governance_events`.
- Template lifecycle is draft -> review -> approved -> active -> deprecated -> archived. Activation requires approved review; only one active version is default; deprecated templates are not default-runnable; archived templates cannot run; rollback does not delete old versions.
- Marketplace foundation records `featured`, `verified`, `recommended`, `usage_count`, `success_rate`, `average_runtime_ms`, and `average_step_count` on `workflow_templates`, then exposes governance badges, risk badge, verified badge, featured templates, and recommended templates.
- Output Artifact lineage adds `source_template_review_id` and `governance_state`; Workflow Runs can record template governance state and compatibility snapshot.
- Admin Dashboard adds Template Governance with Review Queue, Approval / Reject / Request Changes, Template Lifecycle View, Audit Log View, Marketplace View, Compatibility Matrix View, and Rollback UI.
- Worker Console and Worker Console Desktop show governance status, template verification status, and compatibility summary in Template Library.

API coverage:

- `GET /api/v1/workflow-template-reviews`
- `POST /api/v1/workflow-template-reviews`
- `POST /api/v1/workflow-template-reviews/{review_id}/approve`
- `POST /api/v1/workflow-template-reviews/{review_id}/reject`
- `POST /api/v1/workflow-template-reviews/{review_id}/request-changes`
- `POST /api/v1/workflow-templates/{template_id}/rollback/{version_id}`
- `POST /api/v1/workflow-templates/{template_id}/deprecate`
- `POST /api/v1/workflow-templates/{template_id}/archive`
- `GET /api/v1/workflow-template-audit-logs`
- `GET /api/v1/workflow-template-marketplace`
- `GET /api/v1/workflow-template-compatibility-matrix`

Boundaries: Phase 48 is not public marketplace, not a visual DAG builder, not a distributed orchestration platform, not ComfyUI, not TikTok / YouTube / X automation, not real platform publishing, not automatic login, not CAPTCHA automation, not proxy pool, and not fingerprint bypass.
<!-- PHASE48_SYNC:END -->

## Phase 49: Workflow Run Observability & Replay Center

Completed the Workflow Run Observability & Replay Center foundation: added `workflow_execution_traces`, `workflow_runtime_diagnostics`, `workflow_replay_sessions`, and integrated `WorkflowExecutionTraceService` plus `WorkflowDiagnosticsService`. The runtime now records node_started / node_completed / node_failed / planner_decision / retry_triggered / fallback_triggered / approval_wait / approval_resume / replay_started / replay_completed for Execution Trace, Runtime Summary, Failure Hotspots, Replay Center, and metadata_only / dry_run replay sessions.

New APIs: `GET /api/v1/workflow-runs/{workflow_run_id}/traces`, `GET /api/v1/workflow-runs/{workflow_run_id}/diagnostics`, `GET /api/v1/workflow-runs/{workflow_run_id}/analytics`, `POST /api/v1/workflow-runs/{workflow_run_id}/replay-sessions`, `GET /api/v1/workflow-runs/{workflow_run_id}/runtime-summary`, `GET /api/v1/workflow-replay-sessions`, and `GET /api/v1/workflow-replay-sessions/{replay_session_id}`.

Admin Dashboard now includes Replay Center / Workflow Observability views for Execution Trace Timeline, Node Inspection Panel, Retry/Fallback Visualization, Diagnostics Panel, Runtime Summary, Replay Session View, Failure Hotspots, and Approval Wait Visualization. Worker Console / Desktop show a simplified trace timeline, replay session status, diagnostics summary, and retry/fallback counters.

Boundaries: this is not a distributed tracing platform, not an OpenTelemetry stack, not WebSocket/SSE realtime, not a deterministic replay engine, not a visual DAG editor, does not connect ComfyUI, does not perform real social publishing, and does not implement Kubernetes orchestration.

Keywords: not distributed tracing platform; not deterministic replay engine; not ComfyUI.

## Phase 50: Desktop Console Runtime UX & Client Packaging Readiness

Phase 50 adds Desktop Console Runtime UX & Client Packaging Readiness. The Tauri icon resource is now explicit: `worker_console_desktop/src-tauri/icons/icon.ico` is a valid local placeholder icon and `bundle.icon` points to `["icons/icon.ico"]`.

Start Runtime diagnostics now surface clear states: `starting`, `started`, `failed`, `unavailable`, `port_conflict`, `missing_config`, and `server_environment_warning`. The Desktop Console shows local worker diagnostics for `/local/status`, `/local/health`, runtime port, `server_url`, `worker_base_url`, last attempted action, last error detail, and last successful sync.

Server/client boundary: Desktop Console controls the worker runtime on this local machine. If running on the server host, Start Runtime starts a server-local worker, not a remote customer machine. For real client E2E, run this app on the customer machine.

This phase is packaging readiness only: not final installer, no code signing, no auto updater, no MSI/EXE release packaging, and not ComfyUI.

Keywords: Desktop Console Runtime UX & Client Packaging Readiness; Tauri icon resource; icons/icon.ico; bundle.icon; Start Runtime diagnostics; missing_config; port_conflict; server_environment_warning; local worker diagnostics; customer machine; not final installer; no code signing; no auto updater.
<!-- PHASE51_SYNC:START -->
## Phase 51: Release Packaging & Deployment Bundle Foundation

Status: completed.

Phase 51 adds the Release Packaging & Deployment Bundle Foundation. It introduces a `release/` directory with `release/manifest.json`, `release/version.json`, `release/env/aiops.release.env.template`, server deployment bundle scripts, frontend production build bundle scripts, desktop release readiness scripts, Windows / Mac startup scripts, and `release/scripts/validate_release_packaging.py`.

Packaging architecture:

- Server deployment bundle: `release/scripts/build_server_bundle.ps1` and `release/scripts/build_server_bundle.sh` collect API server, worker, worker_client, Alembic, Docker, docs runtime metadata, and env template sources under ignored `release/build/server`.
- Frontend production build bundle: `release/scripts/build_frontend_bundles.ps1` and `release/scripts/build_frontend_bundles.sh` run production builds for Admin Dashboard, Worker Console, and Worker Console Desktop frontend assets, then copy `dist` output under ignored `release/build/frontends`.
- Desktop release readiness: `release/scripts/check_desktop_release_readiness.ps1` and `.sh` verify Tauri config, `icons/icon.ico`, package metadata, and Cargo/toolchain presence without producing a signed installer.
- Version metadata: `release/version.json` records Phase 51 package metadata and component readiness.
- Release manifest: `release/manifest.json` is the packaging SSOT for components, outputs, startup scripts, validation script, and forbidden runtime artifacts.
- Validation: `release/scripts/validate_release_packaging.py` checks required files, manifest JSON, version JSON, desktop icon config, boundaries, and forbidden artifact declarations.

Boundaries: Phase 51 is not a formal production release, no code signing, no auto updater, no MSI/EXE formal installer, no DMG/notarization, no Kubernetes/Helm packaging, no ComfyUI, and no real social platform publishing.

 Phase 51  release readiness  code signing, auto updater, MSI/EXE, DMG/notarization, Kubernetes/Helm.

Keywords: Phase 51; Release Packaging & Deployment Bundle Foundation; release/manifest.json; release/version.json; server deployment bundle; frontend production build bundle; desktop release readiness; aiops.release.env.template; validate_release_packaging.py; Windows / Mac startup scripts; not a formal production release; no code signing; no auto updater; no MSI/EXE; no DMG/notarization; no Kubernetes/Helm.
<!-- PHASE51_SYNC:END -->
<!-- PHASE52_SYNC:START -->
## Phase 52: Deployment Profiles & Environment Bootstrap

Status: completed.

Phase 52 adds Deployment Profiles & Environment Bootstrap on top of Phase 51 release packaging. It introduces `deployment/` with profile-based configuration for `local-dev`, `server-docker`, `client-worker`, `desktop-client`, `staging`, and `production-like`. Each profile contains `profile.json`, `env.template`, `ports.json`, `services.json`, `healthchecks.json`, and `README.md`.

Completed scope:

- `deployment/scripts/generate_env.py` generates `.env.generated` or a specified output from a profile `env.template`, supports override JSON, validates required keys, and refuses to overwrite existing env files without `--force`.
- `deployment/scripts/check_dependencies.py` checks Python, Docker, Docker Compose, Node/npm, Git, Playwright/client worker advisories, Rust/cargo, MSVC/link.exe on Windows, Tauri icon readiness, and WebView2 advisory by profile.
- `deployment/scripts/check_ports.py` checks API 8000, Admin Dashboard 5180, Worker Console 5173, Desktop Console 5174, Worker Runtime 9100, PostgreSQL 5432, Redis 6379, and Qdrant 6333 from each profile `ports.json`; it reports process hints and never kills processes.
- `deployment/scripts/verify_environment.py` verifies `server-docker`, `client-worker`, and `desktop-client` health: docker compose ps, API health, browser-worker health, workflow routes smoke, task-runs smoke, output-artifacts smoke, local worker status/health, Tauri config/icon, and frontend build presence where applicable.
- Added Windows / Mac startup scripts under `deployment/windows/` and `deployment/mac/` for server Docker, Admin Dashboard, Worker Console, Desktop Console, client worker, and profile verification.
- Release integration updates `release/manifest.json`, `release/version.json`, `release/README.md`, and `release/scripts/validate_release_packaging.py` to include deployment profiles, bootstrap scripts, dependency checks, port checks, and profile verification.
- Admin Dashboard, Worker Console, and Worker Console Desktop Settings / Help now show recommended profile, AI Server URL, Workspace ID, User ID, Local Worker API, server/client/desktop role differences, and profile bootstrap docs link.

Boundaries: Phase 52 is not Kubernetes/Helm/Terraform, not Ansible, not production HA, not code signing, not an auto updater, not a formal installer, not ComfyUI, and not real social platform publishing.

Keywords: Phase 52; Deployment Profiles & Environment Bootstrap; local-dev; server-docker; client-worker; desktop-client; staging; production-like; generate_env.py; check_dependencies.py; check_ports.py; verify_environment.py; env generation; dependency checks; port checks; health verification; profile bootstrap docs; Kubernetes/Helm/Terraform.
<!-- PHASE52_SYNC:END -->

<!-- PHASE53_SYNC:BEGIN -->
## Phase 53: Release Smoke Test Matrix & Preflight Automation

Phase 53 adds release readiness orchestration on top of Phase 51 packaging and Phase 52 deployment profiles.

Runtime-facing additions:

- `release/smoke/smoke_matrix.json`
- `release/smoke/profile_matrix.json`
- `release/smoke/runtime_matrix.json`
- `scripts/release_preflight.py`
- `scripts/release_smoke_matrix.py`
- `scripts/generate_release_report.py`
- `scripts/check_migration_continuity.py`
- `scripts/check_runtime_hygiene.py`

The preflight runner coordinates pytest, docs verifier, release validator, frontend builds, Docker health, deployment verification, runtime hygiene, migration continuity, and smoke routes. The smoke matrix checks health, browser-worker summary, conversation playbooks, task runs, output artifacts, workflow templates, and workflow replay sessions.

Boundaries: this is not Kubernetes, Helm, Terraform, CI/CD SaaS, a real installer, code signing, an auto updater, production HA orchestration, ComfyUI, real OpenClaw, or real social media automation.
<!-- PHASE53_SYNC:END -->

<!-- PHASE54_SYNC:BEGIN -->
## Phase 54: Integration Branch & PR Chain Reconciliation

Phase 54 adds integration reconciliation on top of the Phase 43-53 stack. It introduces `docs/INTEGRATION_STRATEGY.md`, `docs/INTEGRATION_STATUS.md`, `release/integration/*`, `release/reports/pr_chain_inventory.json`, `scripts/analyze_pr_chain.py`, `scripts/integration_preflight.py`, `scripts/detect_integration_conflicts.py`, `scripts/check_api_frontend_drift.py`, and `scripts/generate_integration_report.py`.

The integration preflight coordinates release preflight, smoke matrix, docs verifier, migration continuity, runtime hygiene, release packaging validation, deployment verification, OpenAPI/frontend client drift checks, phase index consistency, PR chain inventory validation, and conflict surface detection.

Boundaries: Phase 54 does not add runtime features, does not merge PRs automatically, does not resolve conflicts automatically, and is not Kubernetes, Helm, Terraform, CI/CD SaaS, production HA orchestration, a real installer, code signing, or auto update.
<!-- PHASE54_SYNC:END -->

<!-- PHASE55_SYNC:BEGIN -->
## Phase 55: Mainline Integration & Release Candidate Merge Window

Phase 55 does not add runtime features. It adds Mainline Release Candidate preparation: `docs/MAINLINE_INTEGRATION_PLAN.md`, `docs/RELEASE_CANDIDATE_PROCESS.md`, `release/integration/release_candidate_model.json`, `scripts/mainline_readiness.py`, `scripts/simulate_mainline_merge.py`, `scripts/generate_superseded_pr_report.py`, and `scripts/generate_mainline_integration_report.py`.

The runtime remains smoke verified and integration preflight verified, but not production-ready. Phase 55 keeps `main` unchanged and prepares the manual RC decision package.
<!-- PHASE55_SYNC:END -->

## Docs Stabilization Sprint

This document is now indexed by `docs/PHASE_INDEX.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/SYSTEM_BOUNDARIES.md`, `docs/DOC_RENDER_QA.md`, and `docs/ARCHITECTURE_TIMELINE.md`.

The canonical project recovery state is: `main` is the Phase 55 accepted baseline after PR #17 merged the Phase 43-55 Combined Release Candidate. Phase 56 was reverted and is not active. Post-merge stabilization is tracked in `docs/POST_MERGE_STABILIZATION.md`. Current non-goals remain: no ComfyUI integration, no real social media publishing, no captcha bypass, no proxy pool, no Kubernetes/Helm/Terraform, no HA orchestration, and no production installer/signing.

## Phase 63L-63N Customer Console Execution and Approval Loop

Branch: `codex/phase-63l-63n-execution-approval-loop`

Phase 63L-63N Customer Console Execution and Approval Loop is the active customer-machine runtime slice for `worker_console` and `worker_console_desktop`. It adds a guarded adapter dry-run action, a visual client execution queue, and a commercial approval center on top of the existing metadata-only commercial operation execution run APIs. The dry-run uses the existing start/succeed lifecycle with `guarded_adapter_dry_run` result payloads and leaves live OpenClaw, Playwright, publishing, account control, analytics ingestion, ComfyUI, secret resolution, captcha/proxy/fingerprint bypass, and approval bypass disabled.

## Phase 63O-63Q Customer Console Publish Result Observation Loop

Branch: `codex/phase-63o-63q-publish-result-observation-loop`

Phase 63O-63Q Customer Console Publish Result Observation Loop is the active customer-machine runtime slice for `worker_console` and `worker_console_desktop`. It adds a guarded publish handoff after succeeded guarded dry-run records, a manual publish result capture record, and a manual metric observation entry so operators can see the publish/result/data portion of the closed loop without reading JSON.

The new customer-console path records `guarded_publish_handoff`, `manual_publish_result`, and `manual_publish_metrics` records. The UI exposes a compact publish result loop panel with Prepare publish handoff, Capture publish result, and Record metrics actions. It remains manual and metadata-only: no live OpenClaw execution, no Playwright run, no publishing, no account control, no ComfyUI call, no automated platform analytics ingestion, and no approval bypass.

## Phase 63R-63T Customer Console Publish Metric Improvement Loop

Branch: `codex/phase-63r-63t-publish-metric-improvement-loop`

Phase 63R-63T Customer Console Publish Metric Improvement Loop is the active customer-machine runtime slice for `worker_console` and `worker_console_desktop`. It adds a manual publish metric improvement action after the manual metric observation, prefers that approved improvement when preparing a publish metric next-cycle draft, and shows content improvement as the fourth publish-loop step.

The new customer-console path records `manual_publish_improvement` decisions and `publish_metric_next_cycle_draft` content drafts. It remains manual and metadata-only: no live OpenClaw execution, no Playwright run, no publishing, no account control, no ComfyUI call, no automated platform analytics ingestion, no automated optimization, and no approval bypass.

## Phase 63U-63W Customer Console Improved Draft Re-execution Loop

Branch: `codex/phase-63u-63w-improved-draft-reexecution-loop`

Phase 63U-63W Customer Console Improved Draft Re-execution Loop is the active customer-machine runtime slice for `worker_console` and `worker_console_desktop`. It recognizes publish metric next-cycle approvals, prioritizes them in the commercial approval center, packages the approved improved draft into publish metric re-execution prep, and queues an improved draft re-execution run record for the next customer-machine pass.

The new customer-console path records `publish_metric_reexecution_prep` execution requests and `publish_metric_reexecution_run_review` execution runs. It remains manual and metadata-only: no live OpenClaw execution, no Playwright run, no publishing, no account control, no ComfyUI call, no automated platform analytics ingestion, and no approval bypass.

## Phase 63X-64B Customer Console Closed Loop Delivery Pass

Branch: `codex/phase-63x-64b-client-closed-loop-delivery`

Phase 63X-64B Customer Console Closed Loop Delivery Pass is the active customer-machine runtime slice for `worker_console` and `worker_console_desktop`. It adds a client closed-loop delivery action that combines client runtime preflight, OpenClaw/Playwright handoff, guarded dry-run, publish result capture, manual metric observation, improvement analysis, and next draft generation into one operator-facing flow.

The new customer-console path records the same guarded/manual records as the separate actions and shows the combined path as one five-step delivery pass. It remains controlled and metadata/manual-record only: no live OpenClaw execution, no live Playwright publishing, no social publishing, no account control, no ComfyUI call, no automated platform analytics ingestion, and no approval bypass.

## Phase 64C Commercial Agent/Skill Orchestration

Branch: `codex/phase-64c-commercial-agent-skill-orchestration`

Phase 64C Commercial Agent/Skill Orchestration adds Agent/Skill orchestration through the metadata-only `agent-skill-orchestration` runtime view for commercial operations. The backend exposes `/api/v1/commercial-operations/{operation_id}/agent-skill-orchestration` and `/agent-skill-orchestration/refresh`, returning `CommercialOperationAgentSkillOrchestrationResponse` with the `commercial_operation_agent`, routed skills, owner agents, tool names, next action, decisions, and boundaries.

The server `admin_dashboard` now shows the orchestration for maintainers, and `worker_console` / `worker_console_desktop` show a compact customer-machine Agent/Skill panel near the closed-loop delivery pass. It remains metadata-only: no live OpenClaw execution, no live Playwright publishing, no social publishing, no account control, no ComfyUI call, no automated platform analytics ingestion, no approval bypass, and no repackaging.

## Phase 64D Server/Client Frontend Operability Optimization

Branch: `codex/phase-64d-frontend-operability-optimization`

Phase 64D keeps the runtime unchanged and optimizes frontend operability. `admin_dashboard` adds a server maintenance cockpit that summarizes AI Server connection, customer-machine frontend state, selected commercial operation, and Agent/Skill next action. `worker_console` and `worker_console_desktop` make the commercial operations first screen simpler: common actions are visible in a short action strip, while advanced execution/recovery controls are folded behind a details panel.

Boundary: Phase 64D is frontend display and operator ergonomics only. It does not execute live OpenClaw, run Playwright, publish to social media, ingest platform analytics, auto-optimize, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, bypass approval, mutate runtime configuration, or rebuild client packages.

## Phase 64E Layout Declutter

Branch: `codex/phase-64e-layout-declutter`

Phase 64E keeps the runtime unchanged and removes unnecessary visible components from the server and customer-machine frontends. `worker_console` and `worker_console_desktop` remove the duplicate closed-loop delivery panel because the primary "advance full loop" action already lives in the common action strip. Deliverables, the client execution queue, and publish result controls move into `client-operation-support-drawer`. `admin_dashboard` moves raw action result JSON into `commercial-action-result-drawer` so raw payloads are not visible unless maintainers explicitly expand them.

Boundary: Phase 64E is layout declutter only. It does not execute live OpenClaw, run Playwright, publish to social media, ingest platform analytics, auto-optimize, control real accounts, call ComfyUI, bypass captcha, use proxy pools, bypass fingerprints, resolve secrets, bypass approval, mutate runtime configuration, or rebuild client packages.

## Phase 65A ComfyUI Real Adapter

Branch: `codex/phase-65a-comfyui-real-adapter`

Phase 65A adds the first guarded real ComfyUI runtime adapter path. The backend exposes `POST /api/v1/comfyui-runtime/prompt-jobs`, `GET /api/v1/comfyui-runtime/prompt-jobs/{prompt_id}/history`, and `GET /api/v1/comfyui-runtime/queue`; the Admin Dashboard ComfyUI tab can refresh queue status and submit a minimal smoke prompt when all runtime gates are enabled. The local smoke used `EmptyImage` -> `SaveImage` and confirmed a real PNG output from ComfyUI.

Boundary: Phase 65A is real ComfyUI prompt/queue/history only, guarded by provider, network, read-only, host, health path, prompt submission, and execution path gates. It does not upload files, install or download models from the app, resolve secrets, publish, control real accounts, mutate configuration, restart services, bypass approval, run OpenClaw/Playwright publishing, ingest analytics, or rebuild client packages.

## Phase 65B Commercial ComfyUI Execution Link

Branch: `codex/phase-65b-commercial-comfyui-execution-link`

Phase 65B binds approved commercial operation ComfyUI adapter dispatches to the Phase 65A guarded runtime adapter. `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/submit-runtime` submits the approved ComfyUI prompt graph and records `runtime_prompt_id`, submission status, queue status, history output metadata, and generated filenames. `POST /api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/refresh-runtime` re-reads history and queue state for the stored prompt ID. When outputs are present, the linked asset request receives a prepared handoff payload with the prompt ID and output filenames.

Boundary: Phase 65B still requires commercial approval and every Phase 65A runtime gate. It does not upload files, download models, resolve secrets, mutate runtime configuration, restart services, publish, control accounts, bypass approvals, run OpenClaw/Playwright publishing, ingest analytics, or rebuild client packages.

## Phase 67A Digital Human Foundation

Branch: `codex/phase-67a-digital-human-foundation`

Phase 67A adds a separate digital-human production foundation instead of extending the already long Commercial Operations or ComfyUI pages. The backend exposes `/api/v1/digital-humans/capabilities`, `/api/v1/digital-humans/assets`, `/api/v1/digital-humans/assets/{asset_id}`, `/api/v1/digital-humans/video-jobs`, `/api/v1/digital-humans/video-jobs/{job_id}`, `/api/v1/digital-humans/video-jobs/{job_id}/refresh`, and `/api/v1/digital-humans/video-jobs/{job_id}/{action}`. The Admin Dashboard exposes a dedicated Digital Humans page for uploading an authorized portrait, uploading supporting materials, creating a script-based video job, refreshing status, and approving/rejecting the job without showing raw JSON.

Boundary: Phase 67A is upload, planning, audit, and approval foundation only. Defaults are `DIGITAL_HUMAN_PROVIDER=mock`, `DIGITAL_HUMAN_ENABLED=False`, and `DIGITAL_HUMAN_ALLOW_EXTERNAL_API=False`. It does not call HeyGen, Tavus, D-ID, local MuseTalk/LivePortrait, or ComfyUI workflows; it does not download models, install workflows, publish, control accounts, mutate configuration, restart services, bypass approvals, run OpenClaw/Playwright publishing, ingest analytics, or rebuild packages.

## Phase 67B Digital Human Execution Loop

Branch: `codex/phase-67b-digital-human-execution-loop`

Phase 67B moves approved digital-human jobs from review into a recoverable execution handoff. The backend exposes `POST /api/v1/digital-humans/video-jobs/{job_id}/execute`; `mock_render` writes a delivery manifest under `DIGITAL_HUMAN_OUTPUT_DIR` and registers it as a generated video asset, while `comfyui_handoff` creates a guarded `/api/v1/comfyui-runtime/video-jobs` record that captures GPU/queue admission, selected endpoint/GPU, runtime prompt id when present, outputs, blocker reasons, and linked ComfyUI job id. Responses include `progress_percent`, `current_stage`, `next_action`, and `linked_comfyui_video_job_id` for Admin Dashboard and customer-machine progress views.

Boundary: Phase 67B still requires approved digital-human jobs and authorized portrait consent before execution. Generated placeholder ComfyUI prompts are not submitted unless an operator supplies a real prompt and the existing ComfyUI guarded runtime gates allow submission. It does not call HeyGen, Tavus, D-ID, local MuseTalk/LivePortrait by default, publish, control accounts, mutate configuration, restart services, bypass approvals, run OpenClaw/Playwright publishing, ingest analytics, install workflows, download models, or rebuild packages.

## Phase 67C Digital Human Workflow Binding

Branch: `codex/phase-67c-digital-human-workflow-binding`

Phase 67C binds digital-human jobs to reviewable ComfyUI workflow contracts before execution. The backend exposes `GET /api/v1/digital-humans/workflow-templates`, `GET /api/v1/digital-humans/workflow-templates/{template_id}`, and `POST /api/v1/digital-humans/video-jobs/{job_id}/workflow-binding`. Built-in contracts include `liveportrait-musetalk-broll`, `wan-i2v-reference-avatar`, and `talking-head-fast-proof`; each reports required assets, custom nodes, models, install checklist metadata, input/output slots, guardrails, default resource profile, and VRAM guidance. Binding a job stores a `digital_human_comfyui_input_binding` output, a `comfyui_workflow_binding` metadata payload, `selected_workflow_template_id`, and `workflow_binding_status`, then lets the guarded ComfyUI video handoff use the bound prompt/workflow contract.

Boundary: Phase 67C is a workflow contract and input binding layer only. It requires authorized portrait consent and refuses terminal jobs, but it does not install ComfyUI nodes, download models, upload media files into ComfyUI, submit prompts without the existing guarded gates, publish, control accounts, mutate runtime configuration, restart services, bypass approval, run OpenClaw/Playwright publishing, ingest analytics, or rebuild packages.

## Phase 67D Digital Human Workflow Readiness

Branch: `codex/phase-67d-digital-human-workflow-readiness`

Phase 67D makes the bound digital-human ComfyUI workflow operationally checkable before real execution. The backend adds `POST /api/v1/digital-humans/video-jobs/{job_id}/workflow-readiness-check`; it requires an existing Phase 67C binding and records operator evidence for real graph import, installed custom nodes, installed model files, uploaded bound assets, output watch path, ComfyUI base URL, GPU name, free VRAM, and queue depth. Responses expose `workflow_readiness_status`, `workflow_asset_upload_status`, `workflow_output_watch_status`, `workflow_missing_nodes`, and `workflow_missing_models`, and store a `digital_human_comfyui_workflow_readiness` output plus `comfyui_workflow_readiness` metadata. Bound prompt submission now refuses real prompt submission unless this readiness status is `ready_for_guarded_comfyui_execution`.

Admin Dashboard Digital Humans adds a no-raw-JSON readiness panel for maintainers to fill the selected template checklist, confirm current assets, record GPU/output evidence, and inspect the upload manifest. `worker_console` and `worker_console_desktop` show readiness status next to the digital-human video progress card so customer-machine operators can see whether the video line is ready, blocked, or still waiting for server-side workflow evidence.

Boundary: Phase 67D records operator evidence only. It does not install nodes, download models, upload files automatically, submit prompts by default, publish, control accounts, mutate runtime configuration, restart services, bypass approval, execute OpenClaw/Playwright account work, ingest platform analytics, or rebuild packages.

## Phase 67E Digital Human Output Ingestion

Branch: `codex/phase-67e-digital-human-output-ingestion`

Phase 67E turns linked ComfyUI outputs into reviewable digital-human delivery assets. The backend adds `POST /api/v1/digital-humans/video-jobs/{job_id}/comfyui-output-ingestion`; it accepts an optional `comfyui_video_job_id`, safe refresh controls (`refresh_comfyui_job`, `poll_history`, `resubmit_if_waiting`), `asset_name`, operator notes, and metadata. When ComfyUI outputs exist, the job becomes `completed`, a generated `DigitalHumanAsset` with `asset_type=video` is created or updated, and responses expose `comfyui_output_ingestion_status`, `delivery_asset_id`, `delivery_asset_status`, `delivery_source_uri`, and `delivery_output_count`. When outputs are not ready, the job records waiting, prompt-submission, resource-blocked, or failed ingestion state for recovery.

Admin Dashboard Digital Humans adds a no-raw-JSON output-ingestion panel for maintainers to refresh the linked ComfyUI job, see delivery asset status, and name the generated asset. `worker_console` and `worker_console_desktop` show ingestion/delivery status next to the digital-human video progress card and expose a compact "Ingest video" action for customer-machine operators.

Boundary: Phase 67E reads the linked ComfyUI video job state and uses the guarded refresh path. It does not upload source files to ComfyUI, install nodes, download models, resubmit jobs by default, publish, control accounts, mutate runtime configuration, restart services, bypass approval, execute OpenClaw/Playwright account work, ingest platform analytics, or rebuild packages.
