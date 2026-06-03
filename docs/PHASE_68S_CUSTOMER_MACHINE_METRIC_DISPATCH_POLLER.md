# Phase 68S Customer-Machine Metric Dispatch Poller

## Purpose

Phase 68S turns the metric dispatch claim loop into a customer-machine poller contract. A customer machine can poll one server endpoint to see the current dispatch queue, its assigned active claims, expired claims, redispatch candidates, and the recommended next poll interval.

This phase keeps the production boundary strict. The server only returns queue, claim, and recovery metadata. It does not log in to platforms, scrape analytics pages, collect credentials, bypass verification, publish, control accounts, run OpenClaw/Playwright, or perform customer-machine browser work.

## API Contract

- `POST /api/v1/commercial-operations/metric-analysis-dispatch/customer-poll`

Schemas:

- `CommercialOperationMetricDispatchCustomerPollRequest`
- `CommercialOperationMetricDispatchCustomerPollResponse`
- `CommercialOperationMetricDispatchCustomerPoll`

The request supports `platform`, `force`, `collection_mode`, `customer_machine_id`, `auto_claim`, `operator_confirmed`, `lease_seconds`, `target_operation_id`, and `limit`.

When `auto_claim=false`, the endpoint is read-only. When `auto_claim=true`, it reuses the Phase 68R claim logic and still requires `operator_confirmed=true` before creating or reusing a claim. This protects the real-account boundary and keeps one active claim per dispatch idempotency key.

Every real platform access path still requires operator approval on the customer machine before collection starts.

## Response Shape

The response includes:

- `dispatch_queue`: the Phase 68Q workspace dispatch queue.
- `claim_list`: the Phase 68R active, expired, and completed claim list.
- `assigned_claims`: active `claimed` or `running` claims for the requesting `customer_machine_id`.
- `expired_claims`: lease-expired claims that need operator recovery.
- `redispatch_candidates`: safe redispatch candidates from expired, failed, released, or unclaimed-ready dispatch items.
- `claim_result`: optional Phase 68R claim response when auto claim is requested.
- `poll_interval_seconds`: recommended customer-machine polling cadence.
- `review_gates` and `next_actions`: operator-visible guardrails.

## Poll Statuses

- `active_claim_in_progress`: this customer machine already has a live claim.
- `auto_claimed`: the poll request created or reused a claim.
- `ready_to_claim`: ready queue items exist but no auto claim was requested.
- `recovery_required`: expired claims need operator review before redispatch.
- `blocked_operator_confirmation_required`: auto claim was requested without human confirmation.
- `claim_blocked`: claim creation was blocked by queue or mode state.
- `idle`: no due dispatch item is available.

## Customer-Machine Workflow

1. Customer machine calls the poll endpoint with its machine id.
2. If `assigned_claims` exists, it continues collection and heartbeats through Phase 68R.
3. If `ready_to_claim`, an operator can either manually claim or enable auto claim with confirmation.
4. If `recovery_required`, the operator reviews expired or failed claim events before reclaiming.
5. Metrics still return through Phase 68M with evidence.
6. Phase 68K analysis and human review continue the optimization loop.

## Frontend Surface

`worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` expose `pollMetricAnalysisDispatchForCustomerMachine`, `metricDispatchCustomerPoll`, `metricDispatchPollStatus`, and a Phase 68S card in the daily analysis panel. Operators can see assigned versus expired claim counts, recommended next actions, and poll status without losing the manual claim and status controls from Phase 68R.
