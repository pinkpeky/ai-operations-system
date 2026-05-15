# Release Reports

`scripts/generate_release_report.py` writes release readiness summaries here by default.

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
