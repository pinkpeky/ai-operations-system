# Phase 68U Local Metric Dispatch Scheduler

## Purpose

Phase 68U turns the Phase 68T `client_timer_payload` into a customer-machine local worker capability. The server still creates the schedule contract, but `worker_client` now persists it locally, exposes local management APIs, can run a guarded `customer-poll` tick, and keeps notification records for the customer console.

This is the first production-shaped bridge between the server-side dispatch plan and the client-side recurring daily metric pullback loop.

## Local Worker Contract

New local-only endpoints:

- `GET /local/metric-dispatch-scheduler`
- `POST /local/metric-dispatch-scheduler/configure`
- `POST /local/metric-dispatch-scheduler/tick`
- `POST /local/metric-dispatch-scheduler/start`
- `POST /local/metric-dispatch-scheduler/stop`
- `POST /local/metric-dispatch-scheduler/clear`

The configure endpoint accepts the full Phase 68T scheduler response or a direct `client_timer_payload`. The only accepted remote endpoint is:

- `/api/v1/commercial-operations/metric-analysis-dispatch/customer-poll`

Any other endpoint is rejected so the local scheduler cannot become a generic server command runner.

## State File

`worker_client.metric_dispatch_scheduler.WorkerMetricDispatchScheduler` writes local state beside the worker state file:

- `configured`
- `running`
- `scheduler_status`
- `scheduler_enabled`
- `customer_machine_id`
- `workspace_id`
- `next_poll_at`
- `recommended_poll_interval_seconds`
- `client_timer_payload`
- `notification_records`
- `history`
- `last_poll_result`
- `last_error`

Secret-like keys in persisted state are redacted.

## Customer Console Surface

`worker_console` and `worker_console_desktop` now:

- save the Phase 68T scheduler payload into the local worker after the operator creates a poll schedule.
- start or stop the local scheduler based on `scheduler_enabled`.
- expose a `phase_68u_local_metric_dispatch_scheduler` action/card.
- allow a manual forced local tick with the “本机轮询 / Local poll” action.
- reflect returned `customer-poll` results back into the dispatch, claim, and daily analysis panels.

## Boundaries

Phase 68U does not publish content, control platform accounts, collect credentials, bypass verification, scrape analytics pages, run OpenClaw/Playwright, mutate ComfyUI workflows, submit ComfyUI prompts, restart services, or rebuild packages.

The local worker only calls the server’s metric dispatch `customer-poll` endpoint using the operator-approved timer payload. Real platform data collection still happens on the customer machine through the approved export/import, browser-assist, or manual evidence path, and metric values still return through Phase 68M before Phase 68K analysis.

## Verification

Coverage added in this phase:

- `tests/test_metric_dispatch_local_scheduler.py`
- `tests/test_worker_local_api.py`
- `tests/test_local_api_client.py`
- `tests/test_worker_runtime_manager.py`
- `tests/test_worker_console_client_ux.py`
