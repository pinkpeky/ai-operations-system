# Phase 68K Scheduled Metric Analysis Runner

Date: 2026-05-31

## Goal

Phase 68K turns the configurable daily analysis schedule into a runnable project contract.

The operator workflow is:

1. Staff configure a project daily analysis time in Phase 68J.
2. At or after `next_run_at`, the customer machine, connector, or server operator runs `metric-analysis-schedule/run`.
3. The run checks whether the schedule is enabled, due, and backed by published packages.
4. If real collected metrics are provided, the server creates `PlatformMetricSnapshot(collected)` records.
5. If metrics already exist inside the lookback window, the run compiles them into an analysis package.
6. The analysis package waits for operator review, operator approval, and metric approval before optimization decisions or next-cycle content changes.

This phase does not log in to social platforms, pull Douyin data by itself, publish content, run OpenClaw or Playwright on the server, control accounts, bypass approval, submit ComfyUI prompts, mutate workflow JSON, restart services, or change runtime configuration.

## Implemented Scope

- `POST /api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/run`
- `CommercialOperationMetricAnalysisRun`
- `CommercialOperationMetricAnalysisRunRequest`
- `CommercialOperationService.run_metric_analysis_schedule()`
- Due-state check against project `metric_analysis_schedule`
- Published `PublishPackage` eligibility check
- Optional customer-machine or connector metric payload ingestion
- `created_metric_snapshots` for supplied real metrics
- `usable_metric_snapshots` for metrics inside the schedule lookback window
- `analysis_package` with package ids, snapshot ids, metric keys, scope, and approval boundary
- Run history stored in `CommercialOperation.metadata.metric_analysis_run_history`
- Customer-machine `runMetricAnalysisSchedule` client method
- Web and Desktop "Run analysis" controls in the daily analysis panel
- Tests in `tests/test_operation_project_governance.py`
- Frontend contract/documentation tests in `tests/test_worker_console_client_ux.py`

## Result Contract

`metric-analysis-schedule/run` accepts:

- `force`;
- optional `collected_metrics`;
- operator notes;
- metadata.

Each collected metric item can include:

- `publish_package_id`;
- platform and platform content id;
- source type;
- collected time and metric date;
- metric values;
- summary;
- evidence links;
- metadata.

The response returns:

- run status;
- schedule status before and after;
- updated schedule;
- eligible publish packages;
- created metric snapshots;
- usable metric snapshots;
- analysis package;
- review gates and next actions.

## Run Statuses

- `disabled`: schedule is not enabled.
- `not_due`: schedule is enabled but `next_run_at` has not arrived and the run was not forced.
- `blocked_no_published_package`: no published package is available for analysis.
- `waiting_for_metric_pullback`: the schedule is due, but no usable metrics were found.
- `collected`: supplied real metrics were stored as collected snapshots.
- `ready_for_analysis`: existing snapshots inside the lookback window can be used for analysis.

## Review Boundary

The required gates are:

- daily analysis must use the configured project time;
- platform metrics must come from a connector or customer-machine evidence;
- created snapshots require operator review;
- optimization waits for approved metrics;
- server-side account control is not allowed.

## Project Fit

Phase 68K is project-wide. It supports KTV video campaigns now and later image, audio, text, or multi-platform projects through the same published package and metric snapshot records.

It is intentionally connector-ready: when a Douyin or other platform analytics adapter is added, it should call this run contract with real collected metrics rather than writing directly into unrelated records.

## Verification

- Backend syntax compile must pass for service, schemas, and routes.
- `tests/test_operation_project_governance.py` must verify forced scheduled analysis creates collected metric snapshots and a review-gated analysis package.
- `tests/test_worker_console_client_ux.py` must verify web/desktop client methods, frontend state, controls, and documentation.
- Web and Desktop typecheck/build must pass.

## Next Step

The next project slice should add a real or customer-machine platform analytics adapter that calls this runner automatically when a configured schedule is due.
