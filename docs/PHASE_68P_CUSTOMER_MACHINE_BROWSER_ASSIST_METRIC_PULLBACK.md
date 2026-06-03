# Phase 68P Customer-Machine Browser Assist Metric Pullback

## Goal

Phase 68P adds a guarded browser assist session plan for customer-machine metric pullback. It extends Phase 68N's Douyin metric adapter profile and Phase 68O's export parser by giving the customer-machine frontend an explicit browser-assist checklist, navigation targets, extraction fields, evidence requirements, and a 68M submission template.

This is still a customer-machine controlled workflow. The server creates a plan only. The server does not run a browser, log in to a social platform, scrape analytics pages, collect credentials, bypass verification, or control real accounts.

## API Contract

- Endpoint: `POST /api/v1/commercial-operations/{operation_id}/metric-analysis-schedule/pullback-handoff/adapter-profile/browser-assist-session`
- Request model: `CommercialOperationMetricPullbackBrowserAssistSessionRequest`
- Response model: `CommercialOperationMetricPullbackBrowserAssistSession`
- Upstream dependency: Phase 68L pullback tasks and Phase 68N browser assist plan.
- Downstream dependency: Phase 68M `submit-result`.

The request requires `operator_confirmed=true` before the session can become ready. Without confirmation, the response is blocked with `blocked_operator_confirmation_required`.

## Session Response

`CommercialOperationMetricPullbackBrowserAssistSession` contains:

- `browser_assist_session_id`: stable run/session identifier.
- `session_status`: `ready_for_customer_machine_browser_assist`, `blocked_operator_confirmation_required`, `blocked_adapter_profile_not_ready`, or `blocked_no_target_pullback_task`.
- `adapter_profile`: the 68N profile used for aliases, allowed domains, and browser boundaries.
- `target_tasks`: Phase 68L pullback tasks selected for the session.
- `navigation targets`: local browser URLs and fallback URLs for the operator-confirmed customer-machine browser.
- `extraction_fields`: metric keys and field aliases the operator/browser assist should read.
- `evidence_plan`: screenshot/account/timestamp evidence requirements.
- `forbidden actions`: credential collection, captcha or verification bypass, account switching without confirmation, publishing/deleting content, and server-side browser execution.
- `operator_checklist`: required local checks before reading or submitting metrics.
- `submission_template`: a 68M payload shape using `adapter_mode=douyin_customer_machine_browser_assist_v1`.

## Customer-Machine UI

`worker_console` and `worker_console_desktop` expose a "Browser pullback" action in the daily analysis panel. The customer-machine operator must confirm:

- The browser action is local to the customer machine.
- The real platform account is visible and correct.
- No passwords, SMS codes, QR codes, captcha answers, or verification data will be sent to the agent.
- Screenshot or export evidence will be captured before 68M submission.

If the operator chooses to open a target page, the frontend opens the first navigation target in the local browser only. The server never opens or controls that page.

## Review Gates

- Operator must confirm the real account before navigation.
- No credential collection or verification bypass is allowed.
- Visible metrics must match Phase 68N field aliases.
- Screenshot or export evidence is required before 68M submission.
- Browser assist runs only on the customer machine.
- Created metric snapshots require operator approval before analysis optimization.

## Boundaries

Phase 68P does not:

- Log in to Douyin or any social platform.
- Read passwords, QR codes, SMS codes, cookies, sessions, or captcha answers.
- Bypass verification.
- Scrape analytics pages from the server.
- Publish, delete, edit, or switch accounts.
- Execute OpenClaw or Playwright on the server.
- Replace operator approval.

## Next Step

Phase 68Q should add the background scheduler bridge: at the configured daily analysis time, identify due operation projects, create metric pullback handoffs, notify the customer machine, and track whether 68O export import or 68P browser assist completed before running analysis.
