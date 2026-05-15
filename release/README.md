# AI Operations System Release Packaging Foundation

Phase 51 adds a release packaging foundation for repeatable validation of server, frontend, worker console, and desktop console delivery assets.

This directory is intentionally a foundation only:

- No code signing.
- No auto updater.
- No MSI / EXE release installer.
- No macOS DMG / notarization.
- No Kubernetes / Helm packaging.
- No production HA object storage or CDN.

## Contents

- `manifest.json` describes release components, scripts, expected outputs, and boundaries.
- `version.json` stores version metadata for this packaging foundation.
- `env/aiops.release.env.template` is a deployment env template; copy it outside version control before adding secrets.
- `scripts/build_server_bundle.*` creates a local server deployment bundle under `release/build/server`.
- `scripts/build_frontend_bundles.*` builds and copies production frontend assets under `release/build/frontends`.
- `scripts/check_desktop_release_readiness.*` checks Tauri icon/config/package readiness without producing a signed installer.
- `scripts/validate_release_packaging.py` validates the release manifest, version metadata, script inventory, forbidden artifact boundaries, and desktop icon references.
- `windows/*.ps1` and `mac/*.sh` provide local startup helpers for server and console development/release validation.

Generated output under `release/build/` is ignored by git.

