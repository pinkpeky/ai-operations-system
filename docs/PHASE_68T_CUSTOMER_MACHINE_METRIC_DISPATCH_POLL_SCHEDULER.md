# Phase 68T Customer-Machine Metric Dispatch Poll Scheduler

## Purpose

Phase 68T turns the Phase 68S customer-machine poller into a scheduler and notification bridge contract. It gives the customer console or local worker a concrete timer payload, recommended interval, next poll time, notification events, and guardrails for recurring metric dispatch checks.

The server still does not run the customer-machine timer. It returns metadata only. The customer machine owns the schedule, local notification display, browser assist, export import, and any real platform access after operator approval.

## API Contract

- `POST /api/v1/commercial-operations/metric-analysis-dispatch/customer-poll/scheduler`

Schemas:

- `CommercialOperationMetricDispatchPollSchedulerRequest`
- `CommercialOperationMetricDispatchPollSchedulerResponse`
- `CommercialOperationMetricDispatchPollScheduler`

The request supports `scheduler_enabled`, `requested_poll_interval_seconds`, `notification_channels`, `notify_on`, `run_poll_now`, and the same poll and claim controls used by Phase 68S: `platform`, `force`, `collection_mode`, `customer_machine_id`, `auto_claim`, `operator_confirmed`, `lease_seconds`, `target_operation_id`, and `limit`.

## Response Shape

The response includes:

- `scheduler_status`: the customer-machine scheduling state.
- `recommended_poll_interval_seconds`: the next interval the client should use.
- `next_poll_at`: the next suggested poll timestamp.
- `poll_result`: the Phase 68S poll result when `run_poll_now=true`.
- `notification_events`: local notification bridge events such as ready, active, blocked, and recovery-required.
- `scheduler_policy`: min/max interval, active/recovery cadence, and server execution boundary.
- `client_timer_payload`: the exact customer-machine timer request template for the next `customer-poll`.
- `review_gates` and `next_actions`: operator-visible guardrails.

## Scheduler Statuses

- `scheduler_active_claim_created`: auto claim created or reused a metric dispatch claim.
- `scheduler_active_claim_in_progress`: this customer machine already has an active claim.
- `scheduler_operator_recovery_required`: expired claims need operator review before redispatch.
- `scheduler_ready_to_claim`: queue items are ready and should be claimed or reviewed.
- `scheduler_blocked`: the claim or poll is blocked by confirmation, queue, or collection mode.
- `scheduler_idle`: no due dispatch task exists now.
- `scheduler_configured_waiting_for_first_tick`: schedule metadata was generated without an immediate poll.
- `scheduler_disabled`: the customer-machine schedule is intentionally disabled.

## Notification Bridge

`notification_events` are local guidance only. They can be displayed in the customer console or consumed by a local worker, but they are not platform actions and they do not send messages to social accounts.

Common event types:

- `metric_dispatch_auto_claimed`
- `metric_dispatch_active_claim`
- `metric_dispatch_ready_to_claim`
- `metric_dispatch_recovery_required`
- `metric_dispatch_claim_blocked`
- `metric_dispatch_idle`

## Customer-Machine Workflow

1. Operator configures the poll schedule in the customer console.
2. The console calls the scheduler endpoint and receives `client_timer_payload`.
3. The customer machine schedules the next `customer-poll` request locally.
4. Notification events tell the operator whether to continue collection, claim a ready item, or recover an expired claim.
5. Metrics still return through Phase 68M with evidence.
6. Phase 68K analysis and human review continue the optimization loop.

## Review Gates

- operator approval is still required before real platform access.
- auto claim still requires `operator_confirmed=true`.
- local notification events are not browser, OpenClaw, or social-platform actions.
- the server does not push browser actions, scrape analytics pages, publish, control accounts, collect credentials, or bypass verification.
- metric values must still return through Phase 68M with evidence.

## Frontend Surface

`worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` expose `scheduleMetricDispatchCustomerPoll`, `metricDispatchPollScheduler`, `metricDispatchPollSchedulerStatus`, and a Phase 68T card in the daily analysis panel. Operators can configure the poll interval, decide whether auto claim is allowed, and see the next local timer contract beside the existing Phase 68S poll and Phase 68R claim controls.
