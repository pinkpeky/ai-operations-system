"""Docs coverage for Phase 35B real client worker E2E validation."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_real_client_worker_e2e_docs_exist_and_cover_safety() -> None:
    """Chinese and English E2E docs include safety and Swagger flow."""

    zh = (ROOT / "docs/zh/REAL_CLIENT_WORKER_E2E.md").read_text(encoding="utf-8")
    en = (ROOT / "docs/en/REAL_CLIENT_WORKER_E2E.md").read_text(encoding="utf-8")
    combined = zh + "\n" + en

    for term in [
        "validate_real_client_worker_e2e.py",
        "X-Workspace-Id",
        "X-User-Id",
        "GET /api/v1/browser-workers/health/summary",
        "POST /api/v1/browser-runtime/sessions",
        "POST /api/v1/browser-runtime/sessions/{session_id}/navigate",
        "POST /api/v1/browser-runtime/sessions/{session_id}/screenshot",
        "GET /api/v1/browser-runtime/sessions/{session_id}/page",
        "POST /api/v1/browser-runtime/sessions/{session_id}/close",
        "do not expose port 9100 to the public internet",
        "Tailscale",
        "VPN",
        "TikTok",
        "YouTube",
        "captcha",
    ]:
        assert term in combined


def test_docs_verifier_tracks_real_client_worker_e2e_docs() -> None:
    """Docs verifier should treat the Phase 35B docs and script as required."""

    verifier = (ROOT / "scripts/verify_docs_runtime.py").read_text(encoding="utf-8")

    assert "scripts/validate_real_client_worker_e2e.py" in verifier
    assert "docs/zh/REAL_CLIENT_WORKER_E2E.md" in verifier
    assert "docs/en/REAL_CLIENT_WORKER_E2E.md" in verifier
