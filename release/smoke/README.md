# Release Smoke Matrix

Phase 53 introduces a unified smoke matrix for release readiness and preflight checks.

The matrix is intentionally local and foundation-level. It coordinates existing checks:

- pytest
- frontend builds
- Docker Compose health
- deployment profile verification
- docs runtime verification and DOCX render QA
- release packaging validation
- runtime hygiene
- Alembic migration continuity
- smoke API routes

## Files

- `smoke_matrix.json` defines check groups and boundaries.
- `profile_matrix.json` maps deployment profiles to required groups.
- `runtime_matrix.json` defines HTTP smoke routes.

## Commands

```powershell
python scripts/release_preflight.py --profile server-docker
python scripts/release_smoke_matrix.py
python scripts/generate_release_report.py
```

## Boundaries

This is not Kubernetes, Helm, Terraform, GitHub Actions, a production HA scheduler, a real installer, code signing, or an auto updater.
