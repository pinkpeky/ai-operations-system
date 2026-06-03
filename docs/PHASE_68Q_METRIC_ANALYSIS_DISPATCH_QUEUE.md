# Phase 68Q Metric Analysis Dispatch Queue

## Purpose

Phase 68Q adds the production-MVP scheduler bridge between configured project metric schedules and customer-machine execution. It introduces a workspace-level dispatch queue so operators can see which operation projects are ready for daily metric pullback, which are blocked, and which customer-machine action should happen next.

This phase does not run OpenClaw, Playwright, platform login, scraping, social publishing, ComfyUI generation, or account control on the server. It only returns a reviewed dispatch queue contract.

## API Contract

- `GET /api/v1/commercial-operations/metric-analysis-dispatch`
- Query parameters:
  - `platform`: optional platform filter, such as `douyin`.
  - `force`: optional due-state override for operator-supervised recovery or testing.
  - `limit`: queue item limit.
- Response schema: `CommercialOperationMetricAnalysisDispatchQueue`.

The response includes:

- workspace dispatch status.
- due, ready, blocked, and idle counts.
- queue items keyed to operation project, schedule window, handoff status, target platform, and target metric keys.
- `customer_machine_actions` for the handoff, adapter profile, export import parser, browser assist session, 68M submission, and 68K analysis run endpoints.
- `scheduler_poll_contract` so a customer-machine or future background scheduler can poll the server safely.

## Customer-Machine Action Boundary

Each dispatch item exposes the next customer-machine action, but still requires operator approval before platform access or metric submission. The server queue can recommend:

- `manual_metric_entry_with_screenshot_evidence`
- `customer_machine_export_import_parser`
- `customer_machine_browser_assist`

The customer machine remains responsible for real platform access, account confirmation, export import file selection, browser assist navigation, and evidence capture. The server validates returned metrics through the 68M intake before the 68K runner creates reviewable metric snapshots.

## Review Gates

- operator approval is required before using the dispatch queue for real metric collection.
- customer-machine action must confirm the real platform account.
- metric values must return with evidence links or screenshots.
- 68M validates submitted metrics before analysis.
- optimization waits for reviewable or approved metric snapshots.
- the server does not log in, scrape, publish, control accounts, or bypass platform verification.

## Frontend Surface

`worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` expose `refreshMetricAnalysisDispatchQueue`, `metricDispatchQueue`, `metricDispatchStatus`, and a Phase 68Q card in the daily analysis panel. The card shows ready/due counts and queue next actions so operators can prioritize pullback work before running analysis.

## Production-MVP Role

68Q makes the closed loop more production-grade by adding a pollable bridge:

1. Project configures daily metric analysis time in 68J.
2. 68Q lists due/forced dispatch items across the workspace.
3. Customer machine chooses a guarded collection mode from the dispatch item.
4. 68O or 68P prepares metrics and evidence.
5. 68M submits accepted metrics into 68K.
6. Human review approves metric snapshots before optimization continues.
