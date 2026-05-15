# Deployment Profiles

Phase 52 新增 Deployment Profiles & Environment Bootstrap，用于可重复的环境配置和启动前检查。

Profiles:

- `local-dev`：开发机，本地 API / 前端，可选 Docker 服务。
- `server-docker`：服务器 Docker Compose，包含 API、browser-worker、PostgreSQL、Redis、Qdrant。
- `client-worker`：客户机运行 `worker_client` 和本地浏览器 runtime。
- `desktop-client`：Worker Console Desktop 控制当前本机 worker runtime。
- `staging`：受控预发布验证环境。
- `production-like`：生产相似演练配置，不声明生产 HA。

Bootstrap 文件：

- `deployment/profiles/<profile>/profile.json`
- `deployment/profiles/<profile>/env.template`
- `deployment/profiles/<profile>/ports.json`
- `deployment/profiles/<profile>/services.json`
- `deployment/profiles/<profile>/healthchecks.json`
- `deployment/profiles/<profile>/README.md`

脚本：

- `python deployment/scripts/generate_env.py --profile server-docker --output .env.generated`
- `python deployment/scripts/check_dependencies.py --profile server-docker`
- `python deployment/scripts/check_ports.py --profile server-docker`
- `python deployment/scripts/verify_environment.py --profile server-docker`

启动辅助：

- Windows：`deployment/windows/*.ps1`
- Mac/Linux：`deployment/mac/*.sh`

边界：当前不是 Kubernetes/Helm/Terraform，不是 Ansible，不是生产级 HA，不做 code signing，不做 auto updater，不是正式 installer，不接 ComfyUI，不做真实社媒发布。
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
