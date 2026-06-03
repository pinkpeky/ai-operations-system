# Phase 68M Customer-Machine Metric Pullback Result Intake

Phase 68M turns the metric pullback handoff into a submit-ready customer-machine and connector intake contract.

## Goal

Customer-machine operators or future platform connectors can submit collected platform metrics against the `pullback_tasks` created in Phase 68L. The server validates task lineage, numeric metric values, and evidence links before delegating accepted metrics to the Phase 68K scheduled analysis runner.

## Implemented Scope

- `POST /api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff/submit-result`
- `CommercialOperationMetricPullbackResult`
- Handoff readiness checks using the existing Phase 68L contract.
- accepted/rejected metric item reporting.
- Numeric metric normalization, including numeric strings such as `"7300"`.
- evidence-link requirement for each accepted metric submission.
- Automatic delegation into `/metric-analysis-schedule/run` for accepted submissions.
- Customer console action for submitting collected metrics and evidence after preparing metric pullback tasks.

## Result Contract

The response includes:

- `submission_status`: `submitted_to_analysis_runner`, `blocked_handoff_not_ready`, or `blocked_no_accepted_metrics`.
- `accepted_metrics`: normalized metric submissions that were sent to the scheduled analysis runner.
- `rejected_metrics`: item-level rejection reasons.
- `metric_analysis_run`: the linked `CommercialOperationMetricAnalysisRun` when accepted metrics were submitted.
- `review_gates`: evidence, task-lineage, numeric-metric, and operator approval boundaries.

## Boundary

This phase does not log in to social platforms, scrape analytics pages, bypass platform verification, control real accounts, publish content, mutate ComfyUI workflows, or bypass operator approval.

It is an intake and validation layer. Actual collection still happens on the customer machine or through a future registered connector, and every created metric snapshot still requires operator approval before optimization.

## Project Fit

68J configures when analysis should happen. 68K runs analysis when metrics are available. 68L prepares the metric pullback tasks. 68M accepts the real customer-machine or connector metric result and feeds it into the review-gated analysis runner.

## Verification

- `tests/test_operation_project_governance.py` validates end-to-end handoff preparation, metric submission, accepted metric normalization, evidence gates, and linked analysis-run snapshot creation.
- `tests/test_worker_console_client_ux.py` validates customer-console API and UI exposure.

## Next Step

Phase 68N should implement the first platform-specific customer-machine metric adapter profile, starting with a guarded Douyin manual/export-assisted profile that consumes `pullback_tasks`, opens only operator-approved pages or imported exports, captures evidence, and submits through this intake endpoint.
