# production-server Profile

Use this profile only for a real single-server production runtime.

Before starting the API:

1. Replace all placeholder secrets outside Git.
2. Confirm the local LLM, embedding, reranker, ComfyUI, and browser worker services are already reachable.
3. Start the reranker runtime with `uvicorn worker.reranker_worker.main:app --host 0.0.0.0 --port 8002` or through the `reranker-worker` Docker Compose service.
4. Start the Browser Worker with `deployment/windows/start_browser_worker_aiops.ps1` and verify it with `deployment/windows/verify_browser_worker_aiops.ps1`.
5. After the API is running, register the Browser Worker in the target workspace with `deployment/windows/register_browser_worker_with_api.ps1 -WorkspaceId "<workspace-id>"`.
6. Run `python scripts/check_production_config.py`.
7. Keep `PRODUCTION_CONFIG_STRICT=true` after all blocking findings are cleared.

This profile is not HA, Kubernetes, Terraform, or a managed cloud deployment. It is the formal baseline for the current single-server architecture.
