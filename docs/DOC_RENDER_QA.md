# DOCX/PDF Render QA

DOCX/PDF Render QA is the required gate for documentation bundles that include Word documents. It verifies that the source DOCX exists, LibreOffice is available, PDF conversion succeeds, and the produced PDF is non-empty.

# Required Checks

- DOCX exists.
- `soffice` exists.
- PDF conversion succeeds.
- PDF exists.
- PDF is non-empty.
- exit code == 0.

# Validation Commands

Windows examples:

```powershell
New-Item -ItemType Directory -Force -Path "docs\rendered" | Out-Null
& "C:\Program Files\LibreOffice\program\soffice.exe" --headless --convert-to pdf --outdir "docs\rendered" "docs\Aiops Project Documentation Update Request For Codex.docx"
Get-Item "docs\rendered\Aiops Project Documentation Update Request For Codex.pdf"
```

The `docs\rendered` directory is an ignored QA output directory and must not be committed.

Cross-platform shape:

```bash
mkdir -p docs/rendered
soffice --headless --convert-to pdf --outdir docs/rendered "docs/Aiops Project Documentation Update Request For Codex.docx"
test -s "docs/rendered/Aiops Project Documentation Update Request For Codex.pdf"
```

# Failure Modes

- `soffice` missing: verifier must emit `WARNING`, not fake `PASS`.
- Conversion exit code non-zero: verifier must emit `ERROR`.
- PDF missing: verifier must emit `ERROR`.
- PDF empty: verifier must emit `ERROR`.
- Permission or profile error: retry with a writable temporary/profile directory before declaring failure.

# CI Integration

CI should run `python scripts/verify_docs_runtime.py`. If LibreOffice is installed, the verifier performs DOCX->PDF conversion. If LibreOffice is not installed, CI may pass with a warning only if that environment intentionally omits render QA dependencies.

# Release Requirements

Before an archival release, render QA should be run in an environment with LibreOffice installed. Rendered PDFs under `docs/rendered/` are QA artifacts and must not be committed.
