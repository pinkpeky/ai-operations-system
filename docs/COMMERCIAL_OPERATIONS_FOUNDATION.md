# Commercial Operations Foundation

Updated: 2026-05-20

## Phase

Phase 61A started the path toward the requested commercial automation system:

> A user provides an operating goal; the system plans, generates content, calls materials and knowledge, waits for approval, executes or publishes safely, monitors effects, recovers failures, and reports commercial results.

Phase 61B adds evidence and handoff links to that project center. Phase 61C adds approval gates for individual plan steps. Phase 61D adds approved, metadata-only dry-run records before any real execution. Phase 61E adds reviewable content drafts per channel. Phase 61F promotes asset requests into first-class records. Phase 61G packages approved drafts and approved/prepared asset requests into reviewable commercial operation deliverables that also appear in the Output Library. Phase 61H adds first-class metadata-only execution requests from packaged deliverables. The system still does not attempt the whole autonomous loop yet.

## Branch

```text
codex/phase-61h-commercial-operation-execution-requests
```

## What This Phase Adds

- Database table: `commercial_operations`.
- Database table: `commercial_operation_links`.
- Database table: `commercial_operation_approvals`.
- Database table: `commercial_operation_dry_runs`.
- Database table: `commercial_operation_content_drafts`.
- Database table: `commercial_operation_asset_requests`.
- Database table: `commercial_operation_deliverables`.
- Database table: `commercial_operation_execution_requests`.
- ORM model: `CommercialOperation`.
- ORM model: `CommercialOperationLink`.
- ORM model: `CommercialOperationApproval`.
- ORM model: `CommercialOperationDryRun`.
- ORM model: `CommercialOperationContentDraft`.
- ORM model: `CommercialOperationAssetRequest`.
- ORM model: `CommercialOperationDeliverable`.
- ORM model: `CommercialOperationExecutionRequest`.
- Service layer: `CommercialOperationService`.
- API route group: `/api/v1/commercial-operations`.
- API route group: `/api/v1/commercial-operations/{operation_id}/links`.
- API route group: `/api/v1/commercial-operations/{operation_id}/approvals`.
- API route group: `/api/v1/commercial-operations/{operation_id}/dry-runs`.
- API route group: `/api/v1/commercial-operations/{operation_id}/content-drafts`.
- API route group: `/api/v1/commercial-operations/{operation_id}/asset-requests`.
- API route group: `/api/v1/commercial-operations/{operation_id}/deliverables`.
- API route group: `/api/v1/commercial-operations/{operation_id}/execution-requests`.
- Admin Dashboard page: `?page=commercial-operations`.
- API client: `commercialOperationsApi`.
- Migration: `0035_phase61a_commercial_ops`.
- Migration: `0036_phase61b_commercial_links`.
- Migration: `0037_phase61c_op_approvals`.
- Migration: `0038_phase61d_op_dry_runs`.
- Migration: `0039_phase61e_content_drafts`.
- Migration: `0040_phase61f_asset_requests`.
- Migration: `0041_phase61g_deliverables`.
- Migration: `0042_phase61h_exec_requests`.

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

Each commercial operation deliverable stores:

- workspace, operation, approved content draft, linked asset request ids, and plan-step context;
- channel, deliverable type, title, summary, delivery notes, quality checks, package payload, result summary, failure reason, reviewer notes, and metadata;
- creator, updater, approver, packager, decision timestamps, failure timestamp, and archive timestamp;
- `output_artifact_id` for the linked Output Library artifact with `source_type=commercial_operation`;
- `deliverable_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `packaged`, `failed`, or `archived`.

Each commercial operation execution request stores:

- workspace, operation, packaged deliverable, linked Output Library artifact, and plan-step context;
- channel, execution type, execution mode, title, target platform/account, input summary, runbook, readiness checks, expected outputs, handoff payload, reviewer notes, result summary, failure reason, and metadata;
- requester, updater, approver, preparer, canceller, decision timestamps, failure timestamp, cancellation timestamp, and archive timestamp;
- `request_status`: `draft`, `ready_for_review`, `approved`, `rejected`, `prepared`, `failed`, `cancelled`, or `archived`.

## Evidence and Handoff Links

Phase 61B treats these links as operator-readable evidence and handoff context. They are deliberately lightweight references so later phases can build approval-backed plan steps, content artifacts, RAG snapshots, safe dry-runs, monitoring, and result reports on top of a durable project record.

## Approval Gates

Phase 61C treats approvals as explicit human decisions on the plan outline. Creating or deciding an approval writes the approval state back to the matching `plan_outline` step so operators can see which step is gated, approved, rejected, or cancelled.

## Safe Dry-Runs

Phase 61D treats dry-runs as metadata-only execution preparation records. Creating a dry-run requires an approved commercial operation approval in the same workspace and operation. Completing, failing, or cancelling the dry-run writes the dry-run state back to the matching `plan_outline` step so operators can see whether the execution preparation is ready for later handoff.

Dry-runs do not call OpenClaw, ComfyUI, Browser Worker, real accounts, or publishing platforms. They only record the proposed target, expected outputs, readiness checks, and operator result.

## Content Drafts

Phase 61E treats content drafts as reviewable artifacts for a specific operation plan step. A draft can be created, edited, marked ready for review, approved, rejected, or archived. Creating or deciding a draft writes the draft state back to the matching `plan_outline` step so operators can see which content step already has a draft and whether it is approved.

Content drafts do not publish content, call OpenClaw, run ComfyUI jobs, control browser workers, or contact external accounts. Asset requests are placeholders only; they prepare the later ComfyUI handoff shape without starting a real generation job.

## Asset Requests

Phase 61F treats asset requests as first-class, reviewable records. A request can be created from a plan step and optionally linked to a content draft, edited, marked ready for review, approved, rejected, prepared for future ComfyUI handoff, failed during preparation, or archived. Creating or deciding an asset request writes the latest request state back to the matching `plan_outline` step so operators can see whether a channel needs visual, video, design, or supporting content assets.

Asset requests do not start ComfyUI, publish assets, run OpenClaw, control Browser Worker actions, or contact external accounts. The `handoff_payload` is intentionally metadata-only and carries the later ComfyUI shape, source materials, checks, and safety boundary.

## Deliverables

Phase 61G treats deliverables as the operator-facing handoff package for an approved content draft and approved/prepared asset requests. A deliverable can be created, edited, marked ready for review, approved, rejected, packaged, failed during packaging, or archived. Creating or deciding a deliverable writes the latest deliverable state back to the matching `plan_outline` step.

Creating a deliverable also creates a linked Output Library artifact with `source_type=commercial_operation`, `artifact_type=markdown`, and a metadata-only content package. Packaging the deliverable moves that artifact to the packaged stage so the next operator can find the commercial handoff in the same artifact surface used by conversations, playbooks, tasks, and workflows.

Deliverables do not publish content, execute OpenClaw actions, run Browser Worker actions, run ComfyUI jobs, contact external accounts, or bypass approval. The `package_payload` describes the future handoff shape only; the next runtime step remains a future monitored execution request.

## Execution Requests

Phase 61H treats execution requests as first-class, reviewable records created from packaged deliverables. A request can be created, edited, marked ready for review, approved, rejected, prepared for future guarded runtime handoff, failed before handoff, cancelled before preparation, or archived. Creating or deciding an execution request writes the latest request state back to the matching `plan_outline` step.

Execution requests are still metadata-only. They do not publish content, execute OpenClaw actions, run Browser Worker actions, run ComfyUI jobs, contact external accounts, or bypass approval. The `handoff_payload` records the future runtime shape, `future_guarded_runtime_adapter`, and the forbidden actions list so workstation operators and server maintainers can see exactly what has and has not happened.

## Operator Flow

1. Open Admin Dashboard and select Commercial Ops / 商业运营.
2. Enter a clear business objective.
3. Add channels, success metrics, constraints, risk level, and the RAG collection to use.
4. Create the operation.
5. Review the generated plan outline.
6. Regenerate the plan when the goal or constraints change.
7. Move the operation to ready, active, or paused when the human operating process changes.
8. Create content drafts for the relevant channels, edit them, send them for review, approve/reject them, and archive obsolete drafts.
9. Create asset requests for images, videos, covers, design files, or supporting assets; approve, prepare, fail, or archive them without starting generation.
10. Package approved drafts and approved/prepared asset requests into deliverables, then approve, package, fail, or archive the handoff package.
11. Create execution requests from packaged deliverables, then send them for review, approve/reject them, prepare/cancel/fail them, or archive them without external execution.
12. Create approval gates for risky plan steps, approve/reject/cancel them, and keep the plan outline updated.
13. Create safe dry-runs from approved approval records, then mark them completed, failed, or cancelled after operator review.
14. Attach evidence or handoff links so the next operator can find the source conversation, RAG document, generated artifact, task run, workflow run, approval record, content draft, asset request, deliverable, execution request, dry-run record, or external material.

The page is intentionally compact: form, list, selected detail, plan draft, content drafts, asset requests, deliverables, execution requests, approval gates, safe dry-runs, evidence/handoff links, and action result are visible without requiring operators to understand backend tables.

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
PATCH /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}
POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/ready
POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/approve
POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/reject
POST /api/v1/commercial-operations/{operation_id}/content-drafts/{draft_id}/archive
GET /api/v1/commercial-operations/{operation_id}/asset-requests
POST /api/v1/commercial-operations/{operation_id}/asset-requests
PATCH /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/ready
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/approve
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/reject
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/prepare
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/fail
POST /api/v1/commercial-operations/{operation_id}/asset-requests/{asset_request_id}/archive
GET /api/v1/commercial-operations/{operation_id}/deliverables
POST /api/v1/commercial-operations/{operation_id}/deliverables
PATCH /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/ready
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/approve
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/reject
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/package
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/fail
POST /api/v1/commercial-operations/{operation_id}/deliverables/{deliverable_id}/archive
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
GET /api/v1/commercial-operations/{operation_id}/links
POST /api/v1/commercial-operations/{operation_id}/links
DELETE /api/v1/commercial-operations/{operation_id}/links/{link_id}
```

All routes are workspace-scoped through `X-Workspace-Id`. A record created in one workspace is not visible from another workspace.

## Safety Boundary

Phase 61A is a planning and project-record foundation. Phase 61B is an evidence and handoff-link foundation. Phase 61C is an approval-gate foundation. Phase 61D is a metadata-only dry-run foundation. Phase 61E is a content-draft foundation. Phase 61F is a first-class asset request foundation. Phase 61G is a deliverable packaging and Output Library handoff foundation. Phase 61H is a metadata-only execution request foundation.

It does not publish to social platforms.

It does not execute OpenClaw actions.

It does not run ComfyUI jobs.

It does not control real accounts.

It does not bypass approval.

It does not claim ROI attribution, account analytics ingestion, or production marketing optimization.

The plan outline may mention future execution surfaces such as OpenClaw, ComfyUI, browser workers, approvals, artifacts, monitoring, and recovery, but those are reviewable plan items only in this phase.

## Next Development Path

Recommended follow-up slices:

1. Attach RAG evidence snapshots to the deliverable package and plan outline.
2. Attach approval-gate evidence and operator checklists to execution requests.
3. Add a guarded ComfyUI job adapter after asset request approvals, preparation, deliverable packaging, and execution request handoff are stable.
4. Add guarded OpenClaw/browser worker adapters only after execution requests can enforce explicit approval and target checks.
5. Add monitoring metrics and failure-recovery records.
6. Add final business-result reporting once execution and monitoring data exist.
