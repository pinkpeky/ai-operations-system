# Smoke Test Matrix

Phase 53 defines a local Release Smoke Matrix under `release/smoke/`.

## Matrix Files

- `release/smoke/smoke_matrix.json`
- `release/smoke/profile_matrix.json`
- `release/smoke/runtime_matrix.json`
- `release/smoke/README.md`

## Profiles

| Profile | Purpose | Primary Checks |
|---|---|---|
| `server-docker` | API host with Docker services | pytest, docs verifier, frontend build, docker health, deployment verify, smoke routes |
| `local-dev` | Local developer checkout | pytest, docs verifier, frontend build, static hygiene |
| `desktop-client` | Tauri desktop console readiness | frontend build, desktop diagnostics, runtime hygiene |
| `client-worker` | Customer machine worker bootstrap | worker config, local worker health, AI Server reachability |
| `staging` | production-like rehearsal | server-docker checks with staging profile |
| `production-like` | release rehearsal without HA claims | server-docker checks with production-like profile |

## Execution Groups

- `static`: runtime hygiene, migration continuity, release packaging validator
- `docs`: docs verifier and DOCX render QA
- `frontend-build`: three frontend production builds
- `docker-runtime`: Docker Compose health and API smoke routes
- `deployment`: deployment profile verification

## Runtime Routes

The matrix covers:

- `/api/v1/health`
- `/api/v1/browser-workers/health/summary`
- `/api/v1/conversation-playbooks`
- `/api/v1/task-runs`
- `/api/v1/output-artifacts`
- `/api/v1/workflow-templates`
- `/api/v1/workflow-replay-sessions`

## Commands

```powershell
python scripts/release_smoke_matrix.py
python scripts/release_smoke_matrix.py --profile server-docker --json
python scripts/release_preflight.py --profile server-docker
```

## Boundaries

The smoke matrix is not a GitHub Actions pipeline, Kubernetes scheduler, Helm chart, Terraform deployment, formal installer, code signing system, auto updater, or production HA orchestration layer.

## Phase 54 Integration Use

Phase 54 integration preflight calls this matrix as one verification group. The matrix remains read-only smoke orchestration: it does not merge PRs, rebase branches, or resolve conflicts.

## Phase 55 Mainline Use

Phase 55 mainline readiness calls this matrix as one Release Candidate gate. `scripts/mainline_readiness.py --profile server-docker` wraps integration preflight, release preflight, release smoke matrix, docs verifier, migration continuity, runtime hygiene, release packaging validator, deployment verification, API/frontend drift, PR chain inventory, conflict surface detection, git cleanliness, ignored artifact checks, and branch lineage checks.
