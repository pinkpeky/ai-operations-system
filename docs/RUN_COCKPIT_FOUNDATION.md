# Run Cockpit Foundation

Updated: 2026-05-20

This document records the Phase 57 return to normal product development after the Phase 56 readiness and CI closure work.

## Branch

```text
codex/phase-61s-commercial-comfyui-adapter-configs
```

## Scope

Phase 57 adds an Admin Dashboard `Run Cockpit` page that correlates existing runtime surfaces:

- Conversation threads.
- Background task runs.
- Pending approvals for the selected thread.
- Playbook runs.
- Output artifacts linked to the selected thread or task run.
- Task run events and diagnostics.
- Scheduler health.

The page is a frontend composition layer over existing APIs. It does not introduce a new backend aggregate model.

The current action slice adds guarded operations directly inside the cockpit detail panel:

- Approve, reject, cancel, or execute a selected thread approval.
- Retry, cancel, resume, or recover a selected task run.
- Export linked artifacts as markdown or JSON.
- Show a compact last-action result preview after an operation.

The current operator-controls slice adds:

- Task view filters for active, attention, and all task runs.
- Optional auto refresh using the dashboard refresh interval.
- Navigation buttons from the cockpit detail panel to Conversations, Playbooks, Tasks, and Output Library.

The current closeout slice records Phase 57 status after PR #24:

- Phase 57A, 57B, and 57C are merged to `main`.
- Phase 57D reconciles status docs so the completed 57C branch is no longer listed as active.
- A lightweight test guards the phase index against leaving merged run cockpit slices as `TBD` or `In progress`.

The current deep-link slice adds:

- URL query state for the active Admin Dashboard page.
- Run Cockpit handoff links with `thread_id`, `task_run_id`, and `artifact_id`.
- Specialist pages that open the linked Conversation, Task Run, or Output Artifact detail directly.

The current refresh-UX slice adds:

- Auto-refresh state labels in the Run Cockpit summary strip.
- Refresh interval and next-refresh countdown labels.
- Stale-data preservation when a cockpit refresh fails after prior data loaded.

The current playbook-context slice adds:

- Playbooks page awareness of `thread_id` deep-link context.
- Filtered Playbook Runs when opened from a selected Run Cockpit thread.
- Controls to open the linked Conversation or clear the Playbooks thread context.

The current output-library-context slice adds:

- Output Library awareness of `thread_id`, `task_run_id`, and `artifact_id` deep-link context.
- Filtered artifact lists when opened from a selected Run Cockpit thread or task.
- Controls to open the linked Conversation, open the linked Task Run, or clear the Output Library context.

The Phase 58 closeout slice recorded:

- Phase 58A, 58B, 58C, and 58D are merged to `main`.
- PR #29 completed the Output Library context handoff.
- PR #30 reconciled Phase 58 closeout and marked `codex/phase-58-run-cockpit-closeout` as merged.

The current search-density slice adds:

- Run Cockpit search across thread titles/status, task ids/types/status/errors, playbook run ids/status, and artifact titles/summaries/context ids.
- Filtered density counters for visible threads, visible tasks, search hits, and matching artifacts.
- Linked artifact display that respects the current cockpit search while preserving selected run context.

The current workflow-handoff slice adds:

- `workflow_run_id` deep-link state for Workflows and Replay Center.
- Linked workflow summary in Run Cockpit when the selected task, playbook run, or artifact has workflow context.
- Navigation from Run Cockpit to Workflows or Replay Center with the linked workflow selected.

The current workflow-focus slice adds:

- Workflow focus state labels for no context, loading, ready, and unavailable linked workflow details.
- Linked workflow provenance from the selected task, selected thread playbook runs, and linked artifacts.
- A compact source-candidate list so operators can see why a `workflow_run_id` was selected before opening Workflows or Replay Center.

The current frontend language and simplification slice adds:

- An Admin Dashboard language switch with Chinese as the default and English as the fallback.
- Localized dashboard shell, navigation, topbar status, and Run Cockpit operator scan labels.
- A small i18n foundation for later full-interface simplification without changing runtime APIs or execution semantics.

The current overview persona and simplification slice adds:

- A Chinese-first Overview role switch for workstation operators and server maintainers.
- Role-specific entry cards for Run Cockpit, Conversations, Playbooks, Output Library, Workers, Browser Runtime, Tasks, and Settings.
- Localized overview metric labels and concise system snapshot labels while preserving the existing raw JSON diagnostics.

The current conversation operator and simplification slice adds:

- A Chinese-first Conversations command summary with run-mode guidance for `auto_safe`, `review_first`, and background execution.
- Localized create, send, run, refresh, playbook, approval, event, and artifact labels on the Conversations page.
- Operator summary cards for thread count, messages, pending approvals, and generated artifacts.

The current RAG Documents and simplification slice adds:

- A Chinese-first RAG / Documents knowledge console for embedding health, collection state, document indexing, and hybrid retrieval.
- Localized health, collection, document, search, result, and raw diagnostics labels on the RAG / Documents page.
- Operator summary cards for embedding provider, collections, documents, chunk count, and problem documents.
- Inline hybrid search loading/error state so failed retrieval attempts are visible without opening browser dev tools.

The current RAG operations and simplification slice adds:

- File upload controls for `/files/upload`, including duplicate handling and chunk size/overlap options.
- Text ingest and reingest controls for `/rag/ingest` and `/documents/reingest`.
- Document detail and chunk inspection through `/documents/{document_id}`.
- A guarded delete-by-source flow for `/documents/by-source/{source_id}` with typed `source_id` confirmation.
- Retrieval debug controls for `/rag/debug` plus inline action result feedback for operators.

The current workflow observability and simplification slice adds:

- A Replay Center command center that explains the select, summarize, diagnose, and replay workflow.
- Localized workflow observability labels for Chinese-first operators and English fallback users.
- Summary cards for selected run status, trace count, diagnostics, replay sessions, failures, retries, and problem diagnostics.
- Trace filtering for all traces, attention items, approval waits, and replay events.
- Clearer metadata-only replay boundaries so operators know replay records do not re-execute actions or bypass approvals.

The current RAG live-validation slice adds:

- A live validation guide for `/files/upload`, `/rag/ingest`, `/rag/search`, `/rag/debug`, `/documents/reingest`, and `/documents/by-source/{source_id}`.
- A documented test collection, `phase60g_live_validation`, so validation data stays isolated from real knowledge.
- A validated workstation flow for upload or text ingest, document inspection, hybrid search, debug, reingest, and source cleanup.
- A validated server-maintainer flow for API health, embedding health, Qdrant collection health, and delete-by-source cleanup.
- A concise RAG / Documents operation-loop hint in Chinese and English.

## User Outcome

An operator can open one screen and answer:

- Which conversation or background task is active.
- Whether a selected thread needs human approval.
- Which task run has failed or can be recovered.
- Which artifacts were produced by the selected run context.
- What the latest thread event or task event says.
- Whether the most common approval, task, or artifact action succeeded.
- Which task runs need attention without leaving the cockpit.
- Where to continue deeper inspection in the existing specialist pages.
- A shareable URL for the selected specialist page context after leaving the cockpit.
- Whether cockpit data is idle, refreshing, or stale without losing the previous scan result.
- A Playbooks page that stays scoped to the selected cockpit thread until the operator clears that context.
- An Output Library page that stays scoped to the selected cockpit thread/task/artifact until the operator clears that context.
- A Run Cockpit search layer for scanning large local result sets without leaving the cockpit.
- A workflow handoff path from Run Cockpit into Workflows and Replay Center for deeper runtime inspection.
- Workflow focus context that explains which selected runtime object supplied the linked workflow and whether detail loading is ready or unavailable.
- A Chinese-first dashboard shell with an English switch so workstation operators and server maintainers can orient themselves quickly.
- An Overview page that separates workstation operation from server maintenance and opens the most relevant dashboard pages directly.
- A Conversations page that explains how to create, send, safely run, review approvals, and inspect event/artifact output.
- A RAG / Documents page that lets a maintainer verify vector health, collection status, document indexing, and retrieval results from one concise screen.
- A RAG / Documents page that lets a maintainer upload files, write text knowledge, inspect chunks, reingest sources, delete a confirmed source, and debug retrieval from the same concise screen.
- A Replay Center page that lets an operator select a workflow run, scan attention metrics, filter traces, inspect diagnostics, and create a metadata-only replay record from one concise screen.
- A RAG live-validation guide that a workstation user or server maintainer can follow to prove upload, search, debug, reingest, and delete behavior end to end.
- A Commercial Ops deliverable package that links approved drafts and prepared assets into an Output Library artifact without publishing or executing.
- A Commercial Ops evidence snapshot that links packaged deliverables to approved RAG/source evidence, execution request/run evidence snapshot IDs, and operator checklists without live retrieval, knowledge ingestion, publishing, or executing.
- A Commercial Ops RAG content draft action that turns existing knowledge search results into a reviewable content draft without uploading knowledge, approving, publishing, or executing.
- A Commercial Ops RAG asset request action that turns existing knowledge search results into a reviewable asset brief without uploading knowledge, approving, starting ComfyUI, publishing, or executing.

## Boundaries

- No new production publishing flow.
- No login or permission UI.
- No WebSocket or SSE event stream.
- No replacement for the existing Conversations, Tasks, Playbooks, or Output Library pages.
- No new workflow execution semantics.
- No real OpenClaw or social media execution.
- No bulk action mode; every action is scoped to the selected run context.
- Deep links do not add authentication, permissions, or share-token semantics; they only restore local dashboard page context.
- Auto refresh remains polling-based; no WebSocket or SSE stream is introduced.
- Playbooks filtering is local to the Admin Dashboard list; it does not add new backend query semantics.
- Output Library context filtering is local to the Admin Dashboard list; it does not add new backend query semantics.
- Run Cockpit search is local to the Admin Dashboard list; it does not add new backend query semantics.
- Workflow handoff does not add new workflow execution semantics, replay semantics, or backend query semantics.
- Workflow focus is a frontend provenance and state layer; it does not change workflow selection, replay, or execution behavior on the server.
- The Phase 60A language slice is a frontend foundation only; it does not provide full translation coverage, RBAC, workflow execution changes, or production publishing.
- The Phase 60B Overview slice is a frontend navigation and clarity layer only; it does not add permissions, new backend APIs, or new runtime execution behavior.
- The Phase 60C Conversations slice is a frontend clarity layer only; it does not add streaming, WebSocket/SSE, new approvals semantics, or new execution behavior.
- The Phase 60D RAG Documents slice is a frontend clarity layer only; it does not add new ingest/delete/reingest APIs, new retrieval semantics, or full document management.
- The Phase 60E RAG operations slice is a frontend operation layer only; it does not add new parser support, OCR, PPTX/XLSX ingestion, auth or permission UI, new retrieval semantics, or backend lifecycle behavior.
- The Phase 60F Workflow Observability slice is a frontend clarity layer only; it does not add OpenTelemetry, WebSocket/SSE streaming, deterministic replay, new workflow execution semantics, or action re-execution.
- The Phase 60G RAG live-validation slice is validation and guidance only; it does not add OCR, PPTX/XLSX ingestion, new parser support, new retrieval semantics, auth/RBAC, or production knowledge-quality scoring.
- Phase 61J Commercial Operation Results adds operator-observed result reports after terminal execution runs; it does not ingest platform analytics or claim ROI attribution.
- Phase 61K Commercial Operation Monitoring Observations adds operator-observed monitoring snapshots after approved commercial results; it does not ingest platform analytics or claim ROI attribution.
- Phase 61L Commercial Operation Optimization Decisions adds operator-decided next actions after approved monitoring observations; it does not auto-optimize, publish, or execute external actions.
- Phase 61N Commercial Operation RAG Evidence Generation adds draft evidence snapshots generated from existing RAG search; it does not ingest knowledge files, auto-approve evidence, publish, or execute external actions.
- Phase 61O Commercial Operation RAG Content Draft Generation adds draft content records generated from existing RAG search; it does not ingest knowledge files, auto-approve content, publish, or execute external actions.
- Phase 61P Commercial Operation RAG Asset Brief Generation adds draft asset request records generated from existing RAG search; it does not ingest knowledge files, auto-approve assets, start ComfyUI, publish, or execute external actions.
- Phase 61Q Commercial Operation ComfyUI Handoffs adds metadata-only handoff records from approved/prepared asset requests; it does not submit ComfyUI jobs, generate media, publish, or execute external actions.
- Phase 61R Commercial Operation ComfyUI Preflights adds metadata-only endpoint, queue, model, workflow, and adapter readiness records from approved/prepared handoffs; it does not call ComfyUI endpoints, submit queues, generate media, publish, or execute external actions.
- Phase 61S Commercial Operation ComfyUI Adapter Configs adds metadata-only endpoint, queue, workflow allowlist, model inventory, runtime limit, maintenance note, and secret-reference records for server maintainers; it does not call ComfyUI endpoints, submit queues, store secret values, generate media, publish, or execute external actions.
- Phase 61A adds the adjacent Commercial Ops project center. Phase 61B adds manual evidence and handoff links from Commercial Ops back to conversations, artifacts, tasks, workflows, RAG documents, approvals, and external materials. Phase 61C adds `commercial_operation_approvals` and `/api/v1/commercial-operations/{operation_id}/approvals` for individual Commercial Ops plan-step approval gates. Phase 61D adds `commercial_operation_dry_runs` and `/api/v1/commercial-operations/{operation_id}/dry-runs` for approved, metadata-only execution preparation records. Phase 61E adds `commercial_operation_content_drafts` and `/api/v1/commercial-operations/{operation_id}/content-drafts` for reviewable channel drafts. Phase 61F adds `commercial_operation_asset_requests` and `/api/v1/commercial-operations/{operation_id}/asset-requests` for first-class asset handoff preparation records. Phase 61G adds `commercial_operation_deliverables` and `/api/v1/commercial-operations/{operation_id}/deliverables` for approved commercial handoff packages linked to Output Library artifacts. Phase 61H adds `commercial_operation_execution_requests` and `/api/v1/commercial-operations/{operation_id}/execution-requests` for metadata-only future runtime handoff records from packaged deliverables. Phase 61I adds `commercial_operation_execution_runs` and `/api/v1/commercial-operations/{operation_id}/execution-runs` for metadata-only run lifecycle, retry, result, and recovery records from prepared execution requests. Phase 61J adds `commercial_operation_results` and `/api/v1/commercial-operations/{operation_id}/results` for operator-observed commercial result reports from terminal execution runs. Phase 61K adds `commercial_operation_monitoring_observations` and `/api/v1/commercial-operations/{operation_id}/monitoring-observations` for operator-observed monitoring snapshots from approved commercial results. Phase 61L adds `commercial_operation_optimization_decisions` and `/api/v1/commercial-operations/{operation_id}/optimization-decisions` for operator-decided optimization actions from approved monitoring observations. Phase 61M adds `commercial_operation_evidence_snapshots` and `/api/v1/commercial-operations/{operation_id}/evidence-snapshots` for approved evidence packages, execution request/run evidence IDs, and operator checklists. Phase 61N adds `/api/v1/commercial-operations/{operation_id}/evidence-snapshots/generate-rag` for draft evidence generated from existing RAG search. Phase 61O adds `/api/v1/commercial-operations/{operation_id}/content-drafts/generate-rag` for draft content generated from existing RAG search. Phase 61P adds `/api/v1/commercial-operations/{operation_id}/asset-requests/generate-rag` for draft asset briefs generated from existing RAG search. Phase 61Q adds `commercial_operation_comfyui_handoffs` and `/api/v1/commercial-operations/{operation_id}/comfyui-handoffs` for metadata-only ComfyUI handoff records. Phase 61R adds `commercial_operation_comfyui_preflights` and `/api/v1/commercial-operations/{operation_id}/comfyui-preflights` for metadata-only ComfyUI readiness records. Phase 61S adds `commercial_operation_comfyui_adapter_configs` and `/api/v1/commercial-operations/{operation_id}/comfyui-adapter-configs` for metadata-only ComfyUI adapter config records. Run Cockpit still remains the execution-monitoring surface; Commercial Ops is the goal-to-plan, handoff, approval-gate, content-draft, asset-request, ComfyUI-handoff, ComfyUI-preflight, ComfyUI-adapter-config, deliverable, evidence-snapshot, execution-request, execution-run, result, monitoring observation, optimization decision, and dry-run entry point and does not publish, execute external actions, ingest platform analytics, or claim ROI attribution.

## Acceptance

Local acceptance requires:

```powershell
npm run typecheck
npm run build
python scripts/verify_docs_runtime.py
python -m pytest -q
```

Remote acceptance requires the PR Quality Gates workflow to pass before merge.
