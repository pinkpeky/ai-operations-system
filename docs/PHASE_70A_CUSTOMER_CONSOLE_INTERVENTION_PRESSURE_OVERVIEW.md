# Phase 70A Customer Console Intervention Pressure Overview

Phase 70A lifts the intervention queue/SLA signal from the dedicated production intervention panel into the project-wide pressure and process surfaces. Operators should not have to open a single subsection to know that the production closed loop is waiting on human intervention.

## Scope

- `worker_console` and `worker_console_desktop` derive `productionInterventionPressureQueue`.
- Both frontends derive `productionInterventionPressureSummary`.
- Both frontends derive `productionInterventionPressureRequired`.
- Both frontends derive `productionInterventionPressureQueueCount`.
- Both frontends derive `productionInterventionPressureSlaStatus`.
- Both frontends derive `productionInterventionPressureReminderRecommended`.
- Both frontends derive `productionInterventionPressureLevel`.
- Both frontends derive `productionInterventionPressureScore`.
- `serverPressureScore` now includes `productionInterventionPressureScore`.
- `serverPressureCards` now include `intervention_pressure`.
- `projectProcessStages` now includes an `intervention` step between publish and metrics.
- Server pressure layout supports seven cards and the project process rail supports ten steps.

## Boundary

This phase is summary visibility only. It does not acknowledge queue items, change acknowledgement status, send reminders, send messages, execute target endpoints, publish from the server, call OpenClaw, call Playwright, control accounts, store credentials, collect tokens or cookies, bypass operator approval, submit ComfyUI prompts, mutate workflow JSON, restart services, download models, install workflows, upload files, or rebuild client packages.

## Verification

- `tests/test_worker_console_client_ux.py::test_worker_consoles_expose_phase_70a_intervention_pressure_overview`
- `tests/test_commercial_operations_docs.py::test_commercial_operations_foundation_covers_phase_70a_intervention_pressure_overview`
- `tests/test_commercial_operations_docs.py::test_phase_70a_intervention_pressure_overview_is_documented`
