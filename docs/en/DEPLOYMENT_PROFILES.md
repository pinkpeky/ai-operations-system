# Deployment Profiles

Phase 52 adds Deployment Profiles & Environment Bootstrap for repeatable environment setup.

Profiles:

- `local-dev`: developer workstation with local API/frontends and optional Docker services.
- `server-docker`: server-side Docker Compose profile for API, browser-worker, PostgreSQL, Redis, and Qdrant.
- `client-worker`: customer machine running `worker_client` and the local browser runtime.
- `desktop-client`: Worker Console Desktop controlling the local machine worker runtime.
- `staging`: controlled validation environment with staging-only placeholders.
- `production-like`: production-like rehearsal profile without production HA claims.

Bootstrap files:

- `deployment/profiles/<profile>/profile.json`
- `deployment/profiles/<profile>/env.template`
- `deployment/profiles/<profile>/ports.json`
- `deployment/profiles/<profile>/services.json`
- `deployment/profiles/<profile>/healthchecks.json`
- `deployment/profiles/<profile>/README.md`

Scripts:

- `python deployment/scripts/generate_env.py --profile server-docker --output .env.generated`
- `python deployment/scripts/check_dependencies.py --profile server-docker`
- `python deployment/scripts/check_ports.py --profile server-docker`
- `python deployment/scripts/verify_environment.py --profile server-docker`

Startup helpers:

- Windows: `deployment/windows/*.ps1`
- Mac/Linux: `deployment/mac/*.sh`

Boundaries: this is not Kubernetes/Helm/Terraform, not Ansible, not production HA, not code signing, not an auto updater, not a formal installer, not ComfyUI, and not real social platform publishing.
<!-- PHASE52_SYNC:START -->
## Phase 52: Deployment Profiles & Environment Bootstrap

Status: completed.

Phase 52 adds Deployment Profiles & Environment Bootstrap on top of Phase 51 release packaging. It introduces `deployment/` with profile-based configuration for `local-dev`, `server-docker`, `client-worker`, `desktop-client`, `staging`, and `production-like`. Each profile contains `profile.json`, `env.template`, `ports.json`, `services.json`, `healthchecks.json`, and `README.md`.

Completed scope:

- `deployment/scripts/generate_env.py` generates `.env.generated` or a specified output from a profile `env.template`, supports override JSON, validates required keys, and refuses to overwrite existing env files without `--force`.
- `deployment/scripts/check_dependencies.py` checks Python, Docker, Docker Compose, Node/npm, Git, Playwright/client worker advisories, Rust/cargo, MSVC/link.exe on Windows, Tauri icon readiness, and WebView2 advisory by profile.
- `deployment/scripts/check_ports.py` checks API 8000, Admin Dashboard 5180, Worker Console 5173, Desktop Console 5174, Worker Runtime 9100, PostgreSQL 5432, Redis 6379, and Qdrant 6333 from each profile `ports.json`; it reports process hints and never kills processes.
- `deployment/scripts/verify_environment.py` verifies `server-docker`, `client-worker`, and `desktop-client` health: docker compose ps, API health, browser-worker health, workflow routes smoke, task-runs smoke, output-artifacts smoke, local worker status/health, Tauri config/icon, and frontend build presence where applicable.
- Added Windows / Mac startup scripts under `deployment/windows/` and `deployment/mac/` for server Docker, Admin Dashboard, Worker Console, Desktop Console, client worker, and profile verification.
- Release integration updates `release/manifest.json`, `release/version.json`, `release/README.md`, and `release/scripts/validate_release_packaging.py` to include deployment profiles, bootstrap scripts, dependency checks, port checks, and profile verification.
- Admin Dashboard, Worker Console, and Worker Console Desktop Settings / Help now show recommended profile, AI Server URL, Workspace ID, User ID, Local Worker API, server/client/desktop role differences, and profile bootstrap docs link.

Boundaries: Phase 52 is not Kubernetes/Helm/Terraform, not Ansible, not production HA, not code signing, not an auto updater, not a formal installer, not ComfyUI, and not real social platform publishing.

Keywords: Phase 52; Deployment Profiles & Environment Bootstrap; local-dev; server-docker; client-worker; desktop-client; staging; production-like; generate_env.py; check_dependencies.py; check_ports.py; verify_environment.py; env generation; dependency checks; port checks; health verification; profile bootstrap docs; Kubernetes/Helm/Terraform.
<!-- PHASE52_SYNC:END -->
