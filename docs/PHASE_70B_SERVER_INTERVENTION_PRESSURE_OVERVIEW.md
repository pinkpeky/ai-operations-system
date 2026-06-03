# Phase 70B Server Intervention Pressure Overview

Phase 70B mirrors the customer-machine intervention pressure signal into the server Admin Dashboard. Maintainers can see whether the production closed loop has stale/watch queue pressure, overdue acknowledgement SLA, reminder follow-up pressure, cooldown pressure, and the current recommended intervention action without opening the customer console first.

## Scope

- `admin_dashboard` derives `productionClosedLoopInterventionPressureScore`.
- `admin_dashboard` derives `productionClosedLoopInterventionPressureLevel`.
- `admin_dashboard` derives `productionClosedLoopInterventionPressureDrivers`.
- `admin_dashboard` derives `productionClosedLoopInterventionPressureRecommendation`.
- `admin_dashboard` renders `Phase 70B Server Intervention Pressure Overview`.
- The new surface uses `commercial-intervention-pressure-overview`.
- The metric cards use `commercial-intervention-pressure-grid`.
- The overview reads the existing production intervention queue response, including `queue_summary`, `acknowledgement_sla_status_counts`, `reminder_dispatch_status_counts`, `reminder_cooldown_status_counts`, `acknowledgement_overdue_count`, `reminder_follow_up_count`, and `recommended_action`.

## Boundary

This phase is server visibility only. It does not acknowledge queue items, change acknowledgement status, send reminders, send messages, execute target endpoints, publish from the server, call OpenClaw, call Playwright, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, download models, install workflows, upload files, or rebuild client packages.

The visible boundary marker remains `server_read_only_no_openclaw_no_playwright_no_publish`.

## Verification

- `tests/test_admin_dashboard_commercial_operations.py::test_admin_dashboard_exposes_commercial_operations_page`
- `tests/test_commercial_operations_docs.py::test_commercial_operations_foundation_covers_phase_70b_server_intervention_pressure_overview`
- `tests/test_commercial_operations_docs.py::test_phase_70b_server_intervention_pressure_overview_is_documented`
