# Branch Protection

Updated: 2026-05-18

This document records the recommended branch protection posture for the stabilized Phase 55 `main` baseline and the Phase 56 readiness work.

## Protected Branch

Protect:

```text
main
```

Recommended settings:

- Require a pull request before merging.
- Require status checks to pass before merging.
- Require branches to be up to date before merging when GitHub offers that option.
- Do not allow force pushes.
- Do not allow branch deletion.
- Keep administrators under the same rules if repository governance allows it.

## Required Checks

The machine-readable source of truth is:

```text
.github/required-checks.json
```

Required status checks for `main`:

```text
Python docs and runtime gates
Frontend build (admin_dashboard)
Frontend build (worker_console)
Frontend build (worker_console_desktop)
```

These names come from `.github/workflows/pr-quality-gates.yml`. If workflow job names change, update `.github/required-checks.json` in the same PR.

Validate locally with:

```powershell
python scripts/check_required_ci_gates.py
```

## Advisory Checks

`Server Docker Smoke` is intentionally manual through `workflow_dispatch`.

Use it before release-sensitive merges, server migration, Docker/WSL repair work, or deployment profile changes. It is not currently a required pull-request status check because it starts a Docker compose stack and runs heavier profile smoke.

## Boundaries

- This does not configure GitHub branch protection automatically.
- This does not add deployment secrets.
- This does not make the system production-ready.
- This does not add Kubernetes, Helm, Terraform, or external CI/CD SaaS configuration.
