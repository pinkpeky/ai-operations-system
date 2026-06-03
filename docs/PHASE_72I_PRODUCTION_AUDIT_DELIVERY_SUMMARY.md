# Phase 72I Production Audit Delivery Summary

Phase 72I continues the production closed-loop hardening after the customer-machine UI simplification phases. The live production audit already returns full readiness, acceptance, runbook, provider, and next-action evidence, but the raw JSON is too large for a release operator to quickly decide what blocks 100% delivery. This phase adds a compact delivery summary while preserving the full audit payload.

## Scope

- `scripts/check_production_closed_loop.py` now adds `delivery_audit_summary` to the `production_closed_loop_delivery_audit` report.
- The summary contract is `production_closed_loop_delivery_audit_summary`.
- The summary exposes completion status, failed readiness keys, blocker category counts, action counts, and `primary_next_action`.
- It separates `next_external_dependency_action` from `next_operator_action` so a real provider blocker cannot hide internal work that can still progress.
- The CLI adds `--summary-json` for compact machine-readable output without dropping the existing full `--json` report.
- Text output now prints completion percent, blocker count, external/internal action counts, and the current primary next actions.

## Operator Use

Recommended production check:

```powershell
python scripts/check_production_closed_loop.py --report-only --summary-json
```

Use `next_external_dependency_action` for environment/provider work such as real OpenClaw configuration, and use `next_operator_action` for project work such as approval, intervention acknowledgement, runbook evidence, or readiness refresh. A failed audit remains failed until both classes are cleared.

## Boundaries

Phase 72I is read-only audit summarization. It does not configure OpenClaw, mark mock providers ready, mutate environment variables, store secrets, restart services, approve records, reject records, execute target endpoints, call readiness-refresh POST endpoints, run OpenClaw actions, run Playwright, publish, click final submit, collect credentials, submit ComfyUI prompts, mutate workflow JSON, ingest analytics, or bypass approval.

## Verification

Required checks:

```powershell
python -m pytest tests/test_production_closed_loop_audit.py -q
python -m pytest tests/test_commercial_operations_docs.py -q
python scripts/check_production_closed_loop.py --report-only --summary-json
```

Expected behavior:

- Passing audit summaries report `release_ready=true`, `blocker_count=0`, and no primary next action.
- Failed audit summaries report `release_ready=false`, grouped blockers, failed readiness keys, and one primary action.
- External provider blockers appear under `next_external_dependency_action`.
- Internal project or evidence work appears under `next_operator_action`.
