# Phase 68N Douyin Metric Adapter Profile

## Goal

Phase 68N adds a platform-specific metric pullback adapter profile for Douyin/TikTok-style projects. It sits after Phase 68L Customer-Machine Metric Pullback Handoff and before Phase 68M Customer-Machine Metric Pullback Result Intake.

The profile lets the customer-machine frontend and future local adapters understand which published packages need data, which metric names are acceptable, what evidence is required, and how a reviewed submission should be shaped for the 68M intake.

This is a RAG knowledge document for Agent/workflow selection. It documents the role and safe use of the flow, not a server-side social-platform automation.

## API Contract

- Endpoint: `GET /api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff/adapter-profile`
- Query: `platform=douyin` by default, `force=true` can be used when an operator explicitly wants to prepare the profile outside the normal due window.
- Response model: `CommercialOperationMetricPullbackAdapterProfile`
- Upstream dependency: `CommercialOperationMetricPullbackHandoff` from Phase 68L.
- Downstream dependency: `POST /metric-analysis-schedule/pullback-handoff/submit-result` from Phase 68M.

The response includes:

- `adapter_profile_id`: stable profile identifier, currently `douyin_metric_pullback_v1`.
- `profile_status`: readiness state such as `ready_for_customer_machine_adapter`, `blocked_handoff_not_ready`, `blocked_no_matching_platform_task`, or `unsupported_platform`.
- `field_aliases`: field aliases for metric keys such as views, plays, likes, comments, shares, saves, follows, completion rate, and average watch time.
- `normalization_rules`: guidance for separators, ten-thousand units, percentages, empty values, and evidence requirements.
- `evidence_requirements`: analytics screenshot, published content reference, collection timestamp, and operator confirmation.
- `runbook`: operator steps from preparing pullback tasks through submitting evidence into 68M.
- `browser_assist_plan`: guardrails for any future customer-machine browser assist.
- `export_import_contract`: file/manual form expectations for future local import parsing.
- `submission_template`: example 68M payload with `adapter_mode=douyin_customer_machine_profile_v1`.

## Suitable Projects

Use this profile when an operation has approved/published Douyin content and needs scheduled metric pullback into the project loop. It is suitable for:

- Short-video operating projects where published URLs or platform content IDs are already captured.
- KTV/commercial video projects that need day-by-day performance feedback.
- Projects that need repeatable metric naming so Agent analysis can compare outputs across cycles.
- Customer-machine workflows where an operator can provide screenshots or exported analytics files.

It is not useful before content is published, before a metric analysis schedule exists, or when the platform has no matching pullback task.

## Field Aliases

The profile supplies field aliases so local forms, imported files, or browser-assisted reads can map visible labels into normalized metric keys.

Important aliases:

- `views`: playback volume, play count, views, plays, play_count.
- `likes`: likes, like_count.
- `comments`: comments, comment_count.
- `shares`: shares, reposts, share_count.
- `saves`: saves, collects, favorite_count.
- `follows`: new followers or follow count.
- `completion_rate`: completion percentage.
- `avg_watch_time`: average watch duration.

The system still requires numeric values and evidence before a submission is accepted by Phase 68M.

## Browser Assist Boundary

The browser assist section is a profile only. It defines what a customer-machine adapter may do after operator approval:

- Open an operator-confirmed analytics page.
- Read visible metric values after the operator confirms the account and page.
- Capture screenshot evidence.
- Record an export file reference.

Forbidden actions:

- Credential collection.
- Captcha or verification bypass.
- Account switching without operator confirmation.
- Publishing or deleting content.
- Server-side browser execution.

This phase does not run OpenClaw, Playwright, Chrome, or any browser on the server. Any future browser assist must run on the customer machine with explicit operator approval.

## Export/Import Contract

After Phase 68O, the parser status is `customer_machine_preview_parser_enabled`. The profile defines the import shape, while the 68O `parse-export` endpoint previews CSV/JSON/manual rows and produces a reviewed 68M submission payload.

Supported future input modes:

- Manual metric entry with analytics screenshot.
- Operator-imported platform export file.
- OpenClaw/Playwright-assisted navigation after operator confirmation.

Required identity fields:

- `publish_package_id`
- `platform_content_id_or_published_url`

Evidence fields:

- `evidence_url`
- `screenshot_path`
- `export_file_path`

## Submission Path

The profile includes a `submission_template` for the existing Phase 68M endpoint:

`POST /api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff/submit-result`

The submitted metrics must match a pullback task, contain numeric metric values, include evidence links, and remain tied to a published package. Phase 68M then delegates accepted rows into the scheduled analysis runner so metric snapshots can be reviewed before optimization.

## Review Gates

- Operator must confirm the real Douyin account before metric pullback.
- Browser assist must not collect credentials or bypass verification.
- Metric values must match profile field aliases or go to manual review.
- Analytics screenshot or export evidence is required.
- Results must be submitted through Phase 68M intake.
- Created metric snapshots require operator approval before optimization.

## Boundaries

Phase 68N does not:

- Log in to Douyin or any social platform.
- Scrape analytics pages from the server.
- Control real accounts.
- Bypass captcha, SMS, QR, or other verification.
- Publish, delete, edit, or switch accounts.
- Execute OpenClaw or Playwright on the server.
- Replace operator approval.

## Next Step

Phase 68O can safely choose between two useful continuations:

- Add a local customer-machine export-file parser that reads CSV/XLSX/JSON files according to this profile and sends normalized evidence into 68M.
- Add a guarded customer-machine browser assist executor that obeys the 68N browser assist plan and still requires operator confirmation before navigation and before submission.
