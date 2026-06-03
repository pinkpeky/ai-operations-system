# Deployment Profiles & Environment Bootstrap

Phase 52 adds profile-based deployment bootstrap files for local development, Docker server validation, customer worker machines, desktop clients, staging, production-like rehearsal, and the formal single-server production baseline.

This is not Kubernetes, Helm, Terraform, Ansible, a production HA deployment, code signing, an auto updater, or a formal installer.

## Profiles

- `local-dev`: developer laptop or workstation.
- `server-docker`: API server plus backing services via Docker Compose.
- `client-worker`: customer machine worker runtime.
- `desktop-client`: Worker Console Desktop runtime host.
- `staging`: controlled validation environment.
- `production-like`: rehearsal profile for production-like settings without claiming production HA.
- `production-server`: formal single-server production baseline with real providers, guarded ComfyUI, strict worker auth, and explicit browser domains.

Each profile contains `profile.json`, `env.template`, `ports.json`, `services.json`, `healthchecks.json`, and `README.md`.

## Scripts

- `deployment/scripts/generate_env.py`
- `deployment/scripts/check_dependencies.py`
- `deployment/scripts/check_ports.py`
- `deployment/scripts/verify_environment.py`
- `deployment/windows/start_comfyui_aiops.ps1`
- `deployment/windows/register_comfyui_aiops_task.ps1`
- `deployment/windows/verify_comfyui_cu130_aiops.ps1`
- `deployment/windows/apply_comfyui_musetalk_server_fixes.ps1`
- `deployment/windows/verify_comfyui_musetalk_aiops.ps1`
- `deployment/windows/start_ollama_aiops.ps1`
- `deployment/windows/register_ollama_aiops_task.ps1`
- `deployment/windows/start_reranker_aiops.ps1`
- `deployment/windows/register_reranker_aiops_task.ps1`
- `deployment/windows/verify_ollama_reranker_aiops.ps1`
- `deployment/windows/start_browser_worker_aiops.ps1`
- `deployment/windows/register_browser_worker_aiops_task.ps1`
- `deployment/windows/register_browser_worker_with_api.ps1`
- `deployment/windows/verify_browser_worker_aiops.ps1`
- `scripts/check_production_config.py`

Generated `.env.generated` files are ignored by git.

## ComfyUI CU130 Server

The current Windows production-server ComfyUI runtime is `E:\ComfyUI_cu130\ComfyUI`, documented by `docs/COMFYUI_CU130_RUNTIME_MODEL_AUDIT.md` and `docs/COMFYUI_CU130_VIDEO_ANALYSIS_MODEL_AUDIT.md`.

The repository includes scripts for starting the CU130 runtime, registering the `AI Ops ComfyUI CU130` startup task, verifying the running node/model surface, and regenerating the runtime workflow RAG JSONL.

## Legacy ComfyUI MuseTalk Server

The Windows production-server ComfyUI/MuseTalk runtime is documented in `docs/COMFYUI_MUSETALK_SERVER_RUNBOOK.md`.

The legacy runbook refers to the older `E:\ComfyUI` MuseTalk environment. Keep it for historical validation; use the CU130 scripts for current workflow/model operations.

## Browser Worker Production Runtime

The Windows production-server Browser Worker runtime is documented in `docs/BROWSER_WORKER_PRODUCTION_RUNTIME.md`.

The repository now includes scripts for starting the local Playwright Browser Worker on port 9100, registering the `AI Ops Browser Worker` startup task, and verifying strict signed requests against the worker.

