# Phase 68J Configurable Daily Metric Analysis Schedule

Date: 2026-05-30

## Goal

Phase 68J makes daily operation analysis configurable per commercial operation project.

The operator workflow is:

1. A project reaches published-package or metric-snapshot readiness.
2. Staff configure the project daily analysis `local_time`, `timezone`, lookback window, platform scope, and metric requirements.
3. The server stores the schedule in `CommercialOperation.metadata.metric_analysis_schedule`.
4. The schedule response exposes `next_run_at` in UTC plus the operator-facing local time and due status.
5. The scheduler, platform connector, or customer-machine pullback step can later poll the schedule and collect metrics for the configured window.
6. Improvement analysis still waits for reviewed platform metric snapshots and operator approval.

This phase does not ingest platform analytics by itself, log in to social accounts, run OpenClaw or Playwright on the server, bypass operator approval, mutate ComfyUI workflows, submit prompts, restart services, or change runtime configuration.

## Implemented Scope

- `GET /api/v1/commercial-operations/{operation_id}/metric-analysis-schedule`
- `POST /api/v1/commercial-operations/{operation_id}/metric-analysis-schedule`
- `CommercialOperationMetricAnalysisSchedule`
- `CommercialOperationService.get_metric_analysis_schedule()`
- `CommercialOperationService.configure_metric_analysis_schedule()`
- Per-project schedule storage under `CommercialOperation.metadata.metric_analysis_schedule`
- Configurable `local_time`, `timezone`, `lookback_hours`, `platform_scope`, and `metric_requirements`
- UTC `next_run_at` calculation from operator local time
- Schedule statuses: `disabled`, `waiting_for_published_package`, `scheduled`, and `due`
- Customer-machine `getMetricAnalysisSchedule` and `configureMetricAnalysisSchedule` client methods
- `Phase 68J Configurable Daily Metric Analysis Schedule` panel in `worker_console/src/main.tsx`
- Matching desktop panel in `worker_console_desktop/src/main.tsx`
- Tests in `tests/test_operation_project_governance.py`
- Frontend contract/documentation tests in `tests/test_worker_console_client_ux.py`

## Result Contract

`metric-analysis-schedule` accepts:

- `enabled`;
- `local_time` as 24-hour `HH:MM`;
- `timezone` as an IANA timezone name;
- `lookback_hours`;
- `platform_scope`;
- `metric_requirements`;
- metadata for operator/client traceability.

The response returns:

- schedule status;
- local analysis time and timezone;
- next UTC run time;
- last run time placeholder;
- published package count;
- latest metric snapshot;
- analysis contract, review gates, and next actions.

## Review Boundary

The required gates are:

- the operator can configure time per project;
- published package evidence should exist before daily analysis becomes useful;
- metric snapshots must be collected and reviewed before improvement analysis;
- the schedule is a control contract, not a platform analytics connector;
- operator approval remains required before content changes or publishing.

## Project Fit

Phase 68J is project-wide. It applies to KTV video campaigns and later image, audio, text, or multi-platform operations.

It solves the scheduling requirement without hardcoding a universal daily analysis time. Each project can analyze at a time that matches the client's operating rhythm, platform traffic window, and staff review process.

## Verification

- Backend syntax compile must pass for service, schemas, and routes.
- `tests/test_operation_project_governance.py` must verify schedule configuration and schedule readback.
- `tests/test_worker_console_client_ux.py` must verify web/desktop client methods, frontend state, panel classes, and documentation.
- Web and Desktop typecheck/build must pass.

## Next Step

The next project slice should connect due schedules to a collection/analysis runner that creates metric snapshots from the approved platform connector or customer-machine pullback evidence, then prepares an approval-gated optimization package.
