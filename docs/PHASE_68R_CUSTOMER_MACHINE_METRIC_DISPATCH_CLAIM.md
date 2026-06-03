# Phase 68R Customer-Machine Metric Dispatch Claim

## Purpose

Phase 68R turns the 68Q dispatch queue into an operational customer-machine task loop. A customer machine can claim one ready metric dispatch item, receive a lease, heartbeat or update progress, and mark the task completed only after metric submission or evidence exists.

This is the production-MVP bridge between server scheduling and customer-machine work. It remains metadata and handoff only: the server does not log in to platforms, scrape analytics pages, control accounts, publish, run OpenClaw/Playwright, bypass verification, or collect credentials.

## API Contract

- `GET /api/v1/commercial-operations/metric-analysis-dispatch/claims`
- `POST /api/v1/commercial-operations/metric-analysis-dispatch/claims`
- `POST /api/v1/commercial-operations/metric-analysis-dispatch/claims/{claim_id}/status`

Schemas:

- `CommercialOperationMetricDispatchClaimRequest`
- `CommercialOperationMetricDispatchClaimStatusRequest`
- `CommercialOperationMetricDispatchClaimResponse`
- `CommercialOperationMetricDispatchClaimListResponse`

Claim records are stored in `CommercialOperation.operation_metadata.metric_analysis_dispatch_claim_history` for the MVP. Each claim includes `claim_id`, `dispatch_idempotency_key`, `customer_machine_id`, `collection_mode`, `claim_status`, `lease_expires_at`, heartbeat timestamps, progress, evidence links, events, and a safe dispatch snapshot.

## Lease And Heartbeat

The claim lease prevents two customer machines from working the same dispatch item at the same time. Active `claimed` or `running` records block another claim for the same dispatch idempotency key until the claim is completed, failed, released, or lease-expired.

The status endpoint acts as the heartbeat:

- `running` extends the lease and records progress.
- `completed` requires metric submission metadata or evidence.
- `failed` records the operator-visible failure.
- `released` makes the dispatch item claimable again.

## Customer-Machine Workflow

1. Customer machine polls the 68Q dispatch queue.
2. Operator confirms the real platform-account boundary.
3. Customer machine calls the 68R claim endpoint.
4. Customer machine uses manual entry, export import, or browser assist.
5. Metrics are submitted through 68M.
6. Claim is marked completed with 68M submission metadata or evidence.
7. 68K analysis and human review continue the optimization loop.

## Review Gates

- operator approval is required before claiming a real customer-machine task.
- one active claim is allowed per dispatch idempotency key.
- active claims must heartbeat before lease expiry.
- completed claims require metric submission metadata or evidence.
- server-side browser execution, scraping, credential handling, account control, and verification bypass remain forbidden.

## Frontend Surface

`worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` expose `claimMetricAnalysisDispatchTask`, `updateMetricAnalysisDispatchClaimStatus`, `metricDispatchClaim`, `metricDispatchClaimList`, and a Phase 68R card in the daily analysis panel. Operators can claim a task, see active/expired counts, and update claim status without leaving the customer-machine console.
