from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_67a_status_docs_are_current() -> None:
    required = [
        "codex/phase-67a-digital-human-foundation",
        "Phase 67A Digital Human Foundation",
        "/api/v1/digital-humans/capabilities",
        "/api/v1/digital-humans/assets",
        "/api/v1/digital-humans/video-jobs",
        "DIGITAL_HUMAN_PROVIDER",
        "DIGITAL_HUMAN_ALLOW_EXTERNAL_API",
    ]
    for path in [
        "docs/PHASE_INDEX.md",
        "docs/PROJECT_STATUS.md",
        "docs/en/PROJECT_STATUS.md",
        "docs/zh/PROJECT_STATUS.md",
        "docs/CURRENT_NEXT_PHASE.md",
        "docs/CURRENT_RUNTIME.md",
        "docs/PROJECT_OVERVIEW.md",
    ]:
        text = _read(path)
        for marker in required:
            assert marker in text, f"{marker} missing from {path}"


def test_digital_human_api_docs_cover_public_paths() -> None:
    paths = [
        "/api/v1/digital-humans/capabilities",
        "/api/v1/digital-humans/assets",
        "/api/v1/digital-humans/assets/{asset_id}",
        "/api/v1/digital-humans/video-jobs",
        "/api/v1/digital-humans/video-jobs/{job_id}",
        "/api/v1/digital-humans/video-jobs/{job_id}/refresh",
        "/api/v1/digital-humans/video-jobs/{job_id}/{action}",
    ]
    for path in ["docs/en/API_REFERENCE.md", "docs/zh/API_REFERENCE.md"]:
        text = _read(path)
        for api_path in paths:
            assert api_path in text, f"{api_path} missing from {path}"
