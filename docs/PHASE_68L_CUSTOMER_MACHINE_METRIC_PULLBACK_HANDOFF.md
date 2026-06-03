# Phase 68L Customer-Machine Metric Pullback Handoff

Phase 68L adds the handoff package that sits between the configured daily analysis time and the scheduled metric analysis runner.

## Goal

The server can now tell the customer machine or a registered connector exactly which published packages need metric pullback, which metric keys are expected, and which evidence must be returned before the daily analysis runner creates reviewable metric snapshots.

## Implemented Scope

- `GET /api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff`
- `CommercialOperationMetricPullbackHandoff`
- Due-state and force-preparation checks against the project daily analysis schedule.
- Published package eligibility.
- Per-package `pullback_tasks` with platform, package id, content id or published URL, metric keys, collection steps, evidence requirements, and an `analysis_metric_template`.
- `client_adapter_plan` describing supported customer-machine/manual, OpenClaw/Playwright-assisted, or connector import modes.
- Customer console buttons to prepare metric pullback before running daily analysis.

## Result Contract

The handoff returns:

- `handoff_status`: `disabled`, `not_due`, `blocked_no_published_package`, or `ready_for_customer_machine_metric_pullback`.
- `pullback_tasks`: one task per published package when ready.
- `target_metric_keys`: the configured metric requirements or platform policy fallback.
- `evidence_requirements`: platform content reference, analytics screenshot/export, collection timestamp, and operator/connector identity.
- `analysis_run_request_template`: the payload shape expected by `/metric-analysis-schedule/run`.

These target metric keys are still evidence inputs, not final optimization authority; metric snapshots require operator approval before downstream optimization.

## Boundary

This phase does not log in to social platforms, scrape analytics pages, bypass verification, control real accounts, publish content, mutate ComfyUI workflows, or bypass operator approval.

The customer machine or connector must supply real metric values and evidence links. The server only turns submitted evidence into `PlatformMetricSnapshot` records for operator review.

## Project Fit

68J configured the daily analysis time. 68K made the run endpoint create or compile metric snapshots. 68L gives the customer machine a concrete pullback task package so the closed loop can move from "wait for metrics" to "collect metrics, submit evidence, review, then optimize."

## Verification

- `tests/test_operation_project_governance.py` validates force-prepared pullback handoff, task content, metric keys, evidence gates, and compatibility with the 68K run endpoint.
- `tests/test_worker_console_client_ux.py` validates the customer console API and UI exposure.

## Next Step

Phase 68M should implement a real customer-machine metric adapter worker that consumes `pullback_tasks`, uses approved browser/OpenClaw capabilities or platform exports under operator control, and submits the collected metrics back to the 68K runner.
