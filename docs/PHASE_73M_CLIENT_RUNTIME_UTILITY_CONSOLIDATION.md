# Phase 73M Client Runtime Utility Consolidation

## Scope

Phase 73M continues the customer-machine Codex-like UI simplification after Phase 73L. It moves the existing `WorkstationHome` runtime companion surface into `client-top-utility-body` in both `worker_console` and `worker_console_desktop`, so the default page body starts with the real operating workspace instead of a separate local-runtime block.

## Implementation

- `worker_console/src/main.tsx` and `worker_console_desktop/src/main.tsx` keep `client-top-utility-drawer` as the single default top utility entry and add `data-phase="Phase 73M Client Runtime Utility Consolidation"` to `client-top-utility-body`.
- The existing `WorkstationHome` call now renders inside `client-top-utility-body`, after `client-shell-diagnostics-drawer` and `operator-page-mode-drawer`.
- The existing `client-runtime-companion-drawer`, `client-runtime-companion-body`, `client-runtime-summary`, `client-runtime-controls-drawer`, and `client-home-detail-drawer` remain unchanged inside `WorkstationHome`.
- `worker_console/src/styles.css` and `worker_console_desktop/src/styles.css` add scoped rules for `.client-top-utility-body .operator-home.client-runtime-companion` and `.client-top-utility-body .client-runtime-companion-drawer` so the folded runtime companion fits the compact utility drawer.

## Boundary

This is frontend information architecture only. It does not remove local runtime controls, remove language switching, remove advanced maintenance details, change local worker APIs, change conversation APIs, change upload APIs, start runtime automatically, start heartbeat automatically, refresh status automatically, approve records, call target endpoints, run OpenClaw actions, run Playwright, publish, click final submit, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, auto-refresh readiness, or bypass approval.

## Verification

- `tests/test_worker_console_client_ux.py::test_phase_73m_client_runtime_utility_consolidation_contract`
- `tests/test_commercial_operations_docs.py::test_phase_73m_client_runtime_utility_consolidation_is_documented`
