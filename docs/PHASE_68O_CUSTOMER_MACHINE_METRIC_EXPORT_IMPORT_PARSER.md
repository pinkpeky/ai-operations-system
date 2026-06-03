# Phase 68O Customer-Machine Metric Export Import Parser

## Goal

Phase 68O turns the Phase 68N Douyin Metric Adapter Profile into a usable customer-machine import path. Operators can import or paste metric export rows, preview how the rows map to the current Phase 68L pullback tasks, and submit only reviewed rows through the existing Phase 68M metric result intake.

This phase is intentionally a parser/preview contract. It does not fetch platform export files, log in to social platforms, scrape pages, bypass verification, or control real accounts.

## API Contract

- Endpoint: `POST /api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff/adapter-profile/parse-export`
- Request model: `CommercialOperationMetricPullbackExportImportPreviewRequest`
- Response model: `CommercialOperationMetricPullbackExportImportPreview`
- Upstream dependency: Phase 68L pullback tasks and Phase 68N field aliases.
- Downstream dependency: Phase 68M `submit-result`.

Supported input formats:

- `csv`: CSV or TSV-style text with a header row.
- `json`: a JSON array, a single JSON object, or `{ "rows": [...] }`.
- `manual_rows`: already structured rows from a customer-machine form.
- `xlsx_rows`: rows parsed locally by the customer machine from an XLSX file.

The server does not store the raw export file. The customer-machine frontend reads the selected CSV/JSON file locally, sends text for preview, and includes a file evidence reference.

## Mapping Rules

Each row is matched to a Phase 68L pullback task by:

- `publish_package_id`
- `platform_content_id`
- `published_url`
- Single-task fallback when the handoff contains exactly one pullback task

Metric columns are mapped through the 68N field aliases. Important examples:

- `views`: playback volume, play count, views, plays, `play_count`
- `likes`: likes, `like_count`
- `comments`: comments, `comment_count`
- `shares`: shares, reposts, `share_count`
- `saves`: saves, collects, `favorite_count`
- `completion_rate`: completion percentage
- `avg_watch_time`: average watch duration

The parser normalizes common values such as `7,300`, `1.2万`, `3k`, and percentage values for rate metrics.

## Preview Response

`CommercialOperationMetricPullbackExportImportPreview` contains:

- `preview_status`: `ready_for_68m_submission`, `blocked_operator_confirmation_required`, `blocked_adapter_profile_not_ready`, or `blocked_no_accepted_metrics`.
- `adapter_profile`: the 68N profile used for aliases and evidence policy.
- `parsed_row_count`: number of source rows parsed.
- `accepted_metric_count`: number of rows that can be submitted.
- `rejected_rows`: row-level rejection reasons.
- `accepted_metrics`: normalized collected metric rows.
- `submission_payload`: the exact 68M submission payload when the preview is operator-confirmed and ready.

The 68M submission payload uses:

- `adapter_mode=douyin_customer_machine_export_import_v1`
- `source=phase_68o_customer_machine_metric_export_import_parser`
- `collected_metrics[]` rows that already include matched `publish_package_id`, normalized metrics, and evidence links.

## Customer-Machine UI

`worker_console` and `worker_console_desktop` expose a "Parse export" action in the daily analysis panel. The operator selects a CSV/JSON file, confirms the export came from the real account for the current project, previews the accepted/rejected rows, and can submit the generated 68M submission payload.

This keeps the frontend simple and explicit:

- File reading happens on the customer machine.
- The server receives only preview text/rows and evidence references.
- The operator must confirm before the payload can be submitted.
- Created metric snapshots still require operator approval before optimization.

## Review Gates

- Operator must confirm the real account and export source.
- Export rows must match Phase 68L pullback tasks.
- Metric columns must match Phase 68N field aliases.
- Numeric values must be normalized before 68M submission.
- Export file or screenshot evidence is required.
- Server does not fetch or scrape platform export files.

## Boundaries

Phase 68O does not:

- Log in to Douyin or any social platform.
- Download export files from a platform.
- Scrape analytics pages.
- Bypass captcha, QR, SMS, or other verification.
- Publish, delete, edit, or switch accounts.
- Execute OpenClaw or Playwright on the server.
- Replace operator approval.

## Next Step

Phase 68P can add a guarded customer-machine browser assist executor that follows the 68N browser assist plan. It should still require operator confirmation before navigation, before reading visible values, and before submitting the generated 68M payload.
