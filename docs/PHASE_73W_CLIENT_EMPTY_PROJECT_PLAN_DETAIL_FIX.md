# Phase 73W Client Empty Project and Detailed Plan Review Fix

Phase 73W fixes two production-facing customer-machine issues found through real page use on `http://127.0.0.1:5181/`: stable empty-project handling and detailed operation-plan review.

## Scope

- Empty project state is now explicit. When all commercial operation projects are archive-deleted, `refreshCommercialOperationLoop(null)` treats the `null` as an intentional no-selection state instead of falling back to a stale selected operation id.
- The project picker clears `selectedCommercialOperationId`, `operationLoop`, approvals, plans, materials, tasks, workflow selections, output candidates, publish packages, metrics, execution state, delivery status, and pending delete confirmation when no active project remains.
- The first-screen project progress pill uses `hasActiveCommercialOperation`; with no selected operation it shows `0/5` and a waiting state instead of deriving `2/5` from old generic conversation history.
- Operation-plan rendering now expands structured fields in the main plan card through `operationPlanDetailSections`, `compactPlanValue`, `simpleApprovalDeskPlanSections`, `simple-plan-detail-grid`, and `simple-plan-detail-section`.
- Main Agent operation-plan creation now uses `_main_agent_objective_summary` plus richer channel strategy, content strategy, production scope, material requirements, KPIs, and publish schedule fields. The generated plan is still approval-only and does not execute production.

## Operator Flow

1. Staff deletes every project from the project picker.
2. The workbench remains stable in the empty state: no old title, no old plan card, no stale progress, no selection flicker.
3. Staff enters a new operating goal in the large chat box.
4. The console creates a new `CommercialOperation`, advances the Main Agent with `plan_first_goal_submit=true`, and displays a reviewable overall operation plan.
5. The visible plan includes target audience, channel strategy, content/output scope, material/RAG requirements, KPI/schedule, and risk boundary before the staff approves or regenerates it.

## Runtime Boundaries

Phase 73W does not physically delete project children, does not bypass approval, does not approve records automatically, does not submit ComfyUI prompts, does not mutate workflow JSON, does not run OpenClaw or Playwright, does not publish, does not collect platform analytics, and does not restart services automatically.

## Verification Requirement

Future frontend changes to the customer-machine workbench must include real browser verification against the running page when the issue is visible in the UI. Static type checks and token-contract tests are not enough for project selection, deletion, approval, or plan-generation interaction changes.
