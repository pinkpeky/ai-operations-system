# Commercial Operations Foundation

Updated: 2026-05-19

## Phase

Phase 61A starts the path toward the requested commercial automation system:

> A user provides an operating goal; the system plans, generates content, calls materials and knowledge, waits for approval, executes or publishes safely, monitors effects, recovers failures, and reports commercial results.

This phase builds the first durable project center for that goal. It does not attempt the whole autonomous loop yet.

## Branch

```text
codex/phase-60g-closeout-61a-operations-foundation
```

## What This Phase Adds

- Database table: `commercial_operations`.
- ORM model: `CommercialOperation`.
- Service layer: `CommercialOperationService`.
- API route group: `/api/v1/commercial-operations`.
- Admin Dashboard page: `?page=commercial-operations`.
- API client: `commercialOperationsApi`.
- Migration: `0035_phase61a_commercial_ops`.

Each commercial operation stores:

- workspace and creator context;
- title and business objective;
- target audience, channels, budget, constraints, and success metrics;
- optional RAG `knowledge_collection`;
- lifecycle status, priority, and risk level;
- a deterministic `plan_outline` that can be reviewed by a human operator.

## Operator Flow

1. Open Admin Dashboard and select Commercial Ops / 商业运营.
2. Enter a clear business objective.
3. Add channels, success metrics, constraints, risk level, and the RAG collection to use.
4. Create the operation.
5. Review the generated plan outline.
6. Regenerate the plan when the goal or constraints change.
7. Move the operation to ready, active, or paused when the human operating process changes.

The page is intentionally compact: form, list, selected detail, plan draft, and action result are visible without requiring operators to understand backend tables.

## Maintainer Flow

Server maintainers can verify the foundation with:

```text
GET /api/v1/commercial-operations
POST /api/v1/commercial-operations
GET /api/v1/commercial-operations/{operation_id}
PATCH /api/v1/commercial-operations/{operation_id}
POST /api/v1/commercial-operations/{operation_id}/plan-draft
```

All routes are workspace-scoped through `X-Workspace-Id`. A record created in one workspace is not visible from another workspace.

## Safety Boundary

Phase 61A is a planning and project-record foundation.

It does not publish to social platforms.

It does not execute OpenClaw actions.

It does not run ComfyUI jobs.

It does not control real accounts.

It does not bypass approval.

It does not claim ROI attribution, account analytics ingestion, or production marketing optimization.

The plan outline may mention future execution surfaces such as OpenClaw, ComfyUI, browser workers, approvals, artifacts, monitoring, and recovery, but those are reviewable plan items only in this phase.

## Next Development Path

Recommended follow-up slices:

1. Link commercial operations to conversation threads, playbooks, and output artifacts.
2. Add explicit approval objects for operation plan steps.
3. Attach RAG evidence snapshots to the plan outline.
4. Add content draft artifacts per channel.
5. Add ComfyUI asset-request placeholders before real ComfyUI execution.
6. Add OpenClaw/browser dry-run records before any real account action.
7. Add monitoring metrics and failure-recovery records.
8. Add final business-result reporting once execution and monitoring data exist.
