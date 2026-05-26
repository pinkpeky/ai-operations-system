# Deployment Profiles & Environment Bootstrap

Phase 52 adds profile-based deployment bootstrap files for local development, Docker server validation, customer worker machines, desktop clients, staging, and production-like rehearsal.

This is not Kubernetes, Helm, Terraform, Ansible, a production HA deployment, code signing, an auto updater, or a formal installer.

## Profiles

- `local-dev`: developer laptop or workstation.
- `server-docker`: API server plus backing services via Docker Compose.
- `client-worker`: customer machine worker runtime.
- `desktop-client`: Worker Console Desktop runtime host.
- `staging`: controlled validation environment.
- `production-like`: rehearsal profile for production-like settings without claiming production HA.

Each profile contains `profile.json`, `env.template`, `ports.json`, `services.json`, `healthchecks.json`, and `README.md`.

## Scripts

- `deployment/scripts/generate_env.py`
- `deployment/scripts/check_dependencies.py`
- `deployment/scripts/check_ports.py`
- `deployment/scripts/verify_environment.py`
- `deployment/windows/start_comfyui_aiops.ps1`
- `deployment/windows/register_comfyui_aiops_task.ps1`
- `deployment/windows/apply_comfyui_musetalk_server_fixes.ps1`
- `deployment/windows/verify_comfyui_musetalk_aiops.ps1`

Generated `.env.generated` files are ignored by git.

## ComfyUI MuseTalk Server

The Windows production-server ComfyUI/MuseTalk runtime is documented in `docs/COMFYUI_MUSETALK_SERVER_RUNBOOK.md`.

The repository now includes scripts for starting `E:\ComfyUI`, registering the `AI Ops ComfyUI E Drive` startup task, applying the MuseTalk Windows/PyTorch compatibility fixes, and verifying the guarded AI Ops runtime handoff.

