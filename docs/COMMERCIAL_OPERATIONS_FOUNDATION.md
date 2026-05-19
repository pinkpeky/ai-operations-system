# Commercial Operations Foundation

Updated: 2026-05-19

## Phase

Phase 61A started the path toward the requested commercial automation system:

> A user provides an operating goal; the system plans, generates content, calls materials and knowledge, waits for approval, executes or publishes safely, monitors effects, recovers failures, and reports commercial results.

Phase 61B adds evidence and handoff links to that project center. It still does not attempt the whole autonomous loop yet.

## Branch

```text
codex/phase-61b-commercial-operation-links
```

## What This Phase Adds

- Database table: `commercial_operations`.
- Database table: `commercial_operation_links`.
- ORM model: `CommercialOperation`.
- ORM model: `CommercialOperationLink`.
- Service layer: `CommercialOperationService`.
- API route group: `/api/v1/commercial-operations`.
- API route group: `/api/v1/commercial-operations/{operation_id}/links`.
- Admin Dashboard page: `?page=commercial-operations`.
- API client: `commercialOperationsApi`.
- Migration: `0035_phase61a_commercial_ops`.
- Migration: `0036_phase61b_commercial_links`.

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

## Evidence and Handoff Links

Phase 61B treats these links as operator-readable evidence and handoff context. They are deliberately lightweight references so later phases can build approval-backed plan steps, content artifacts, RAG snapshots, safe dry-runs, monitoring, and result reports on top of a durable project record.

## Operator Flow

1. Open Admin Dashboard and select Commercial Ops / 商业运营.
2. Enter a clear business objective.
3. Add channels, success metrics, constraints, risk level, and the RAG collection to use.
4. Create the operation.
5. Review the generated plan outline.
6. Regenerate the plan when the goal or constraints change.
7. Move the operation to ready, active, or paused when the human operating process changes.
8. Attach evidence or handoff links so the next operator can find the source conversation, RAG document, generated artifact, task run, workflow run, approval record, or external material.

The page is intentionally compact: form, list, selected detail, plan draft, evidence/handoff links, and action result are visible without requiring operators to understand backend tables.

## Maintainer Flow

Server maintainers can verify the foundation with:

```text
GET /api/v1/commercial-operations
POST /api/v1/commercial-operations
GET /api/v1/commercial-operations/{operation_id}
PATCH /api/v1/commercial-operations/{operation_id}
POST /api/v1/commercial-operations/{operation_id}/plan-draft
GET /api/v1/commercial-operations/{operation_id}/links
POST /api/v1/commercial-operations/{operation_id}/links
DELETE /api/v1/commercial-operations/{operation_id}/links/{link_id}
```

All routes are workspace-scoped through `X-Workspace-Id`. A record created in one workspace is not visible from another workspace.

## Safety Boundary

Phase 61A is a planning and project-record foundation. Phase 61B is an evidence and handoff-link foundation.

It does not publish to social platforms.

It does not execute OpenClaw actions.

It does not run ComfyUI jobs.

It does not control real accounts.

It does not bypass approval.

It does not claim ROI attribution, account analytics ingestion, or production marketing optimization.

The plan outline may mention future execution surfaces such as OpenClaw, ComfyUI, browser workers, approvals, artifacts, monitoring, and recovery, but those are reviewable plan items only in this phase.

## Next Development Path

Recommended follow-up slices:

1. Add explicit approval objects for operation plan steps.
2. Attach RAG evidence snapshots to the plan outline.
3. Add content draft artifacts per channel.
4. Add ComfyUI asset-request placeholders before real ComfyUI execution.
5. Add OpenClaw/browser dry-run records before any real account action.
6. Add monitoring metrics and failure-recovery records.
7. Add final business-result reporting once execution and monitoring data exist.
