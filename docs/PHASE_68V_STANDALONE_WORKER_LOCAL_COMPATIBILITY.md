# Phase 68V Standalone Worker Local Compatibility

## Purpose

Phase 68V makes the existing production launch shape compatible with the newer customer-machine control plane.

The live server was running:

`python -m uvicorn worker.main:app --host 0.0.0.0 --port 9100`

That entrypoint exposed the browser worker protocol but not the newer `worker_client` local management APIs. Phase 68U was correct in code, but the currently deployed 9100 process would still return `404` for `/local/metric-dispatch-scheduler` until the runtime entrypoint changed.

Phase 68V fixes that by adding a compatibility layer directly to `worker.main:app`.

## Added Local Compatibility Endpoints

`worker.main:create_app` now exposes:

- `GET /local/status`
- `GET /local/health`
- `POST /local/runtime/start`
- `POST /local/runtime/stop`
- `POST /local/runtime/restart`
- `POST /local/heartbeat/start`
- `POST /local/heartbeat/stop`
- `GET /local/logs`
- `GET /local/metric-dispatch-scheduler`
- `POST /local/metric-dispatch-scheduler/configure`
- `POST /local/metric-dispatch-scheduler/tick`
- `POST /local/metric-dispatch-scheduler/start`
- `POST /local/metric-dispatch-scheduler/stop`
- `POST /local/metric-dispatch-scheduler/clear`

The metric scheduler endpoints reuse the Phase 68U `WorkerRuntimeManager` and `WorkerMetricDispatchScheduler`, so the accepted remote endpoint is still only:

- `/api/v1/commercial-operations/metric-analysis-dispatch/customer-poll`

## Runtime Control Boundary

Because `worker.main:app` is usually managed by an external process manager, its `/local/runtime/stop` and `/local/runtime/restart` endpoints do not kill the current process. They return `runtime_control_mode=external_process_control_required` so the operator knows the service manager must perform a controlled restart.

This avoids accidentally killing the real customer-machine worker from inside a browser request.

## Configuration Fallback

The compatibility layer prefers `worker_client/worker_config.yaml` or `WORKER_CLIENT_CONFIG` when present. If neither exists, it builds a safe fallback config from environment variables and browser-worker settings:

- server URL from `WORKER_CLIENT_SERVER_URL`, `AI_OPS_SERVER_URL`, `SERVER_URL`, or `http://localhost:8000`
- workspace from `WORKER_CLIENT_WORKSPACE_ID`, `WORKSPACE_ID`, or `demo-workspace`
- worker name from `WORKER_CLIENT_WORKER_NAME`, `WORKER_NAME`, or `browser-worker-compat`
- local worker base URL from `WORKER_CLIENT_WORKER_BASE_URL` or `http://localhost:9100`

## Boundaries

Phase 68V does not change the browser worker action protocol, signed request verification, Playwright session behavior, OpenClaw behavior, publishing, platform account control, ComfyUI execution, scheduler server contracts, or metric evidence requirements.

It only makes the already-running standalone worker service compatible with the local customer-console control plane.

## Operator Note

After deploying this code, the existing 9100 process must be restarted by its service manager for the new local endpoints to appear. Until that controlled restart happens, the current live process will still return `404` for the new `/local/*` routes because it is running the old loaded module.

## Live Server Smoke - 2026-05-31

The server was smoke-tested after a controlled restart of the standalone worker entrypoint.

Verified:

- `GET http://127.0.0.1:9100/health` returns browser worker reachability.
- `GET http://127.0.0.1:9100/local/status` returns `runtime_running=true` and `standalone_browser_worker_compatibility=true`.
- `GET http://127.0.0.1:9100/local/metric-dispatch-scheduler` returns the Phase 68U local scheduler state.
- `OPTIONS http://127.0.0.1:9100/local/status` with origin `http://127.0.0.1:5174` returns CORS 200.
- A disabled scheduler configure/start/clear smoke succeeded without calling the server poll endpoint.
- `worker_console` on `http://127.0.0.1:5174/` no longer shows Worker API unreachable and still renders the `phase_68u_local_metric_dispatch_scheduler` action.
- Local reranker worker on `http://127.0.0.1:8002` was restored and verified with `/health` and `/api/rerank`.

Regression after the live smoke:

- `138 passed` across commercial operations, worker local APIs, worker.main compatibility, local scheduler, signed worker requests, and browser worker flow tests.

Remaining production configuration gap:

- The compatibility fallback reports `worker_name=browser-worker-compat`, `workspace_id=demo-workspace`, and `registered=false` when no `worker_client/worker_config.yaml` is present. The next production step should create or load the formal worker_client config and register the customer-machine worker against the real workspace.
