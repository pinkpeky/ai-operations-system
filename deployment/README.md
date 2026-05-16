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

Generated `.env.generated` files are ignored by git.

