# Release Candidate Process

The Release Candidate process defines how the Phase 43-55 integration stack can be prepared for `main` without directly changing `main` during preparation.

## Branch Model

- Candidate branch: `codex/phase-43-55-release-candidate`
- Source branch: `codex/phase-55-mainline-integration-release-candidate`
- Target branch: `main`

The model is recorded in `release/integration/release_candidate_model.json`.

## Required Gates

- Mainline readiness runner
- Integration preflight
- Release preflight
- Release smoke matrix
- Docs runtime verifier
- Migration continuity
- Runtime hygiene
- Release packaging validator
- Deployment verification
- API/frontend drift check
- PR chain inventory
- Conflict surface detection
- Pytest
- Three frontend builds
- Docker compose verification

## Optional Gates

- LibreOffice DOCX render QA
- Tauri native dev window
- Real client worker E2E

Optional gates may produce warnings. They do not automatically block the RC unless the manual reviewer marks them blocking.

## Blocking Failures

- Migration continuity failure
- Runtime hygiene failure
- Docs verifier error
- Release preflight failure
- Integration preflight failure
- API/frontend drift failure
- Pytest failure
- Frontend build failure

## Warning-Only Failures

- GitHub unavailable while offline inventory is available
- Conflict surface warnings without strict mode
- Optional native desktop dependency missing
- Real client worker unavailable

## Manual Review Gates

- Superseded PR decision
- Migration review
- OpenAPI surface review
- Desktop packaging boundary review
- Release readiness sign-off
- Rollback plan sign-off

## Rollback Model

Preferred rollback is a single revert of the RC merge commit. If phases are merged one by one, rollback should happen from Phase 55 down to Phase 43 in reverse dependency order.

Never force push `main`, delete phase branches, or remove migration files without an explicit migration rollback review.

## Non-Goals

This process is not a production release process, not code signing, not an auto updater, not Kubernetes, not Helm, not Terraform, not production HA orchestration, not real OpenClaw, not real social automation, and not ComfyUI integration.
