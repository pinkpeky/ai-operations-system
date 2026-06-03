# Phase 68Z8 Production Closed-Loop Next Cycle Draft

Phase 68Z8 turns `ready_for_next_cycle` into a concrete, reviewable next-cycle project package.

## Purpose

Phase 68Z7 made the optimization decision lifecycle valid: a decision must move from `draft` to `ready_for_review` to `approved`, and only then can the production loop report `ready_for_next_cycle`.

Phase 68Z8 adds the next step after that status:

```text
ready_for_next_cycle
-> prepare_next_approved_operation_cycle
-> OperationPlan ready_for_review
-> ProductionTask ready_for_review
-> human approval before the new cycle starts
```

The system no longer treats the next cycle as a single content draft. It creates a first-class next-cycle `OperationPlan` and derives reviewable `ProductionTask` records for copy, image, and media when the operation goal requires them.

## Backend

- `POST /api/v1/commercial-operations/{operation_id}/production-closed-loop/next-cycle-draft`
- `CommercialOperationNextCycleDraftRequest`
- `CommercialOperationNextCycleDraftResponse`
- `CommercialOperationService.prepare_next_operation_cycle`
- `CommercialOperationService.get_production_closed_loop_next_action`
- `CommercialOperationService.advance_main_agent_loop`

The endpoint requires:

```text
operator_confirmed=true
source_decision_id=<approved CommercialOperationOptimizationDecision id>
```

When `source_decision_id` is omitted, the latest approved optimization decision is used. The service still requires the production closed loop to be `ready_for_next_cycle`.

## Result Contract

The next action `prepare_next_approved_operation_cycle` now points to:

```text
POST /production-closed-loop/next-cycle-draft
```

Expected result:

```text
record_type=OperationPlan
plan_status=ready_for_review
production_task_status=ready_for_review
next_cycle_ready_for_human_approval=true
```

The created plan carries:

```text
metadata.production_closed_loop_next_cycle.contract=production_closed_loop_next_cycle_draft
metadata.production_closed_loop_next_cycle.source_decision_id=<approved decision id>
```

The generated tasks carry the same source-decision lineage in metadata and target specs.

## Idempotency

If the same approved optimization decision already has an active next-cycle plan, the endpoint reuses that plan instead of creating a duplicate. If the plan exists but has no active generated tasks, it can create the missing tasks.

## Customer Console

No separate panel is required for this phase. Existing `worker_console` and `worker_console_desktop` surfaces can use:

- the production next-action panel to show `prepare_next_approved_operation_cycle`
- the project workbench approval queue to show the next-cycle `OperationPlan`
- the production task list to show next-cycle copy, image, and media tasks

The customer-machine still does not execute social actions until the new plan, tasks, workflow selections, outputs, and publish package pass review.

## Boundaries

- Does not approve the next-cycle operation plan.
- Does not approve generated production tasks.
- Does not submit ComfyUI prompts.
- Does not mutate workflow JSON.
- Does not publish from the server.
- Does not run OpenClaw or Playwright on the server.
- Does not control real accounts.
- Does not store credentials, session tokens, cookies, verification codes, or account passwords.
- Does not bypass operator approval.

## Test Coverage

- `tests/test_operation_project_governance.py` verifies the full path from `ready_for_next_cycle` to `POST /production-closed-loop/next-cycle-draft`, created `OperationPlan`, generated copy/image/media `ProductionTask` records, and idempotent reuse.
- `tests/test_commercial_operation_main_agent_advance.py` verifies `advance_main_agent_loop` now creates the next-cycle plan and tasks instead of only a content draft.
- `tests/test_worker_console_client_ux.py` verifies recovery docs include Phase 68Z8.
- `tests/test_commercial_operations_docs.py` verifies the foundation documentation covers the next-cycle draft contract.
