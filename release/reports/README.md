# Release Reports

`scripts/generate_release_report.py` writes release readiness summaries here by default. `scripts/generate_integration_report.py` writes integration readiness summaries here by default.

Generated `release_readiness_report.json` files are local QA artifacts and should not be committed. The report aggregates:

- build status
- smoke status
- docs verifier status
- deployment status
- DOCX render QA status
- migration continuity
- open PR chain notes
- known blockers
- deferred features

The report is a readiness snapshot for integration candidates, not a production release attestation.

`pr_chain_inventory.json` is the committed offline PR inventory seed for Phase 54. Generated `integration_readiness_report.*` and `conflict_surface_report.*` files are local QA artifacts and should not be committed.
