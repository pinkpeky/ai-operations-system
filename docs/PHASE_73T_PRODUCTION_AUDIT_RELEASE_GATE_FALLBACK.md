# Phase 73T Production Audit Release Gate Fallback

Phase 73T hardens the production closed-loop audit after Phase 73R. In the live environment the API may still be running an older acceptance-summary contract until the server is restarted or redeployed. The audit must not report `release_gate_total_count=0` or an empty blocked-gate list in that state.

## Runtime Changes

- `scripts/check_production_closed_loop.py` now detects a missing or empty `release_gate_checklist` with `_release_gate_contract_missing`.
- When the API contract is missing, the audit synthesizes the same six release gates from the existing acceptance-summary fields through `_synthesized_release_gate_checklist` and marks `release_gate_source=audit_synthesized_from_acceptance_summary`.
- The delivery-audit summary now exposes `release_gate_contract_missing` and `release_gate_source`.
- The audit adds blocker `acceptance_summary:release_gate_checklist_missing` and next action `deploy_release_gate_acceptance_summary_contract` so operators know to deploy or restart the API contract.
- Text and JSON summaries continue to expose `release_gate_blocked_keys`, `release_gate_ready_count`, and `release_gate_total_count`.

## Boundary

Phase 73T is audit hardening only. It does not mark an old API contract as production-ready, does not configure providers, does not mark mock providers ready, does not change env vars, does not store secrets, does not restart services by itself, does not call target endpoints, does not approve records without an operator click, does not run OpenClaw actions, does not run Playwright, does not publish, does not submit ComfyUI prompts, does not mutate workflow JSON, does not ingest analytics, and does not bypass approval.
