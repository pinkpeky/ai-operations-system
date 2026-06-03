# Phase 71R Production Delivery Audit OpenClaw Provider Handoff

Phase 71R turns the hardest remaining production audit blocker into an operator-visible handoff package: the server and customer-machine worker must use a real OpenClaw publish provider before the closed loop can be considered production-deliverable.

## Backend Contract

- Endpoint: `GET /api/v1/commercial-operations/production-closed-loop/delivery-audit/openclaw-provider-handoff`
- Service: `CommercialOperationService.get_production_closed_loop_delivery_audit_openclaw_provider_handoff`
- Response schema: `CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffResponse`
- Config item schema: `CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoffConfigItemResponse`
- Contract marker: `production_closed_loop_delivery_audit_openclaw_provider_handoff`
- Phase metadata: `phase=71R`

The response joins production config findings with the existing server acceptance OpenClaw provider readiness gate. It returns `handoff_status`, `readiness_status`, `ready`, `provider`, `mock`, worker identity, missing config counts, sanitized config items, verification commands, manual steps, evidence requirements, restart boundaries, acceptance gates, and no-execution boundaries.

## Required Configuration

The handoff exposes these redacted requirements:

- `OPENCLAW_PROVIDER=worker_runtime` on the AI server.
- `WORKER_CLIENT_OPENCLAW_ENABLED=true` on the customer-machine worker.
- `WORKER_CLIENT_OPENCLAW_PROVIDER=openclaw_http` on the customer-machine worker.
- `WORKER_CLIENT_OPENCLAW_BASE_URL=<real OpenClaw adapter base URL>`.
- `WORKER_CLIENT_OPENCLAW_API_KEY=<set>` without ever returning the key value.

Secret fields use redacted state only. The UI and API must never display full API keys, cookies, verification codes, platform passwords, or account tokens.

## Frontend Surfaces

- `admin_dashboard` displays `Phase 71R OpenClaw Provider Handoff` through `commercial-delivery-audit-openclaw-provider-handoff`.
- `worker_console` displays `Phase 71R client production delivery audit OpenClaw provider handoff` through `client-production-delivery-audit-openclaw-provider-handoff`.
- `worker_console_desktop` mirrors the same customer-machine surface.
- The client API method is `productionClosedLoopDeliveryAuditOpenClawProviderHandoff`.
- The customer-machine type is `CommercialOperationProductionClosedLoopDeliveryAuditOpenClawProviderHandoff`.

These surfaces show provider status, mock state, missing config count, readiness status, worker name, and a short list of blocking/configured config items.

## Verification Commands

Operators should run the commands outside the app after manually setting environment variables and restarting the affected runtime:

```powershell
python scripts/check_production_config.py --require-production
python scripts/check_openclaw_provider.py --base-url http://127.0.0.1:9100
python scripts/check_production_closed_loop.py --api-base-url http://127.0.0.1:8000 --worker-base-url http://127.0.0.1:9100 --workspace-id production-workspace --platform douyin --force-metric-due --report-only
```

Acceptable evidence is sanitized output showing the provider is configured, non-mock, reachable, guarded, and ready. Evidence must not include secret values.

## Boundaries

Phase 71R is a handoff and visibility layer only. It does not store secrets, mutate environment variables, restart services, execute target endpoints, run OpenClaw, run Playwright, publish, click final submit, control accounts, collect credentials, collect verification codes, submit ComfyUI prompts, mark mock providers ready, or bypass approval.
