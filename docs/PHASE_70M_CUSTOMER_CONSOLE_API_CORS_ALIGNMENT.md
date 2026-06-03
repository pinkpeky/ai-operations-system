# Phase 70M Customer Console API CORS Alignment

Phase 70M fixes the customer-console API connectivity gap found during Phase 70L browser verification. The running customer console is served from `http://127.0.0.1:5181`, but the API CORS allowlist only covered ports `5173`, `5174`, and `5180`. The page could render while commercial-operation and digital-human API calls failed in the browser as `Failed to fetch`.

## What Changed

- `.env` now includes `http://localhost:5181` and `http://127.0.0.1:5181` in `CORS_ALLOWED_ORIGINS`.
- `.env.example` includes the same 5181 origins.
- `docker-compose.yml` includes the same 5181 origins in the API service default.
- `app/core/config.py` includes the same 5181 origins in the application default.
- `docs/CURRENT_RUNTIME.md` documents the runtime CORS line with 5181.
- `tests/test_conversation_frontend_config.py` asserts all customer-console/admin local origins, including `5174` and `5181`.

## Why It Matters

The production closed loop depends on the customer machine being able to call the server API from the exact frontend origin that operators use. Missing CORS origins make the UI look partially available while silently blocking project data, digital-human progress, publish handoff, and metric feedback calls.

Phase 70M keeps the CORS policy explicit instead of using a wildcard. This preserves the production boundary while allowing the current local customer-console origin to operate.

## Boundaries

This phase does not widen CORS to `*`, does not expose credentials, does not change authentication, does not publish, does not execute OpenClaw or Playwright, does not submit ComfyUI prompts, does not mutate workflow JSON, and does not bypass approval.

## Runtime Apply

After editing `.env`, restart the API service so Docker Compose reloads `CORS_ALLOWED_ORIGINS`:

```powershell
docker compose restart api
```

## Verification

- `tests/test_conversation_frontend_config.py` validates CORS origin documentation and defaults.
- Browser verification should no longer show `Failed to fetch` for `http://127.0.0.1:5181` once the API service is restarted.
