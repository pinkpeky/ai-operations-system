import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_release_manifest_and_version_metadata() -> None:
    manifest = json.loads((ROOT / "release/manifest.json").read_text(encoding="utf-8"))
    version = json.loads((ROOT / "release/version.json").read_text(encoding="utf-8"))

    assert manifest["phase"] == "51"
    assert manifest["release_type"] == "packaging_foundation"
    assert manifest["boundaries"]["formal_installer"] is False
    assert manifest["boundaries"]["code_signing"] is False
    assert manifest["boundaries"]["auto_updater"] is False
    assert manifest["boundaries"]["kubernetes_helm"] is False
    assert version["phase"] == "51"
    assert version["status"] == "packaging_foundation"


def test_release_scripts_and_templates_exist() -> None:
    required = [
        "release/README.md",
        "release/env/aiops.release.env.template",
        "release/scripts/build_server_bundle.ps1",
        "release/scripts/build_server_bundle.sh",
        "release/scripts/build_frontend_bundles.ps1",
        "release/scripts/build_frontend_bundles.sh",
        "release/scripts/check_desktop_release_readiness.ps1",
        "release/scripts/check_desktop_release_readiness.sh",
        "release/scripts/validate_release_packaging.py",
        "release/windows/start_server.ps1",
        "release/windows/start_admin_dashboard.ps1",
        "release/windows/start_worker_console.ps1",
        "release/windows/start_desktop_console.ps1",
        "release/mac/start_server.sh",
        "release/mac/start_admin_dashboard.sh",
        "release/mac/start_worker_console.sh",
        "release/mac/start_desktop_console.sh",
    ]

    missing = [path for path in required if not (ROOT / path).exists()]
    assert missing == []


def test_release_validation_script_passes_json_mode() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "release/scripts/validate_release_packaging.py"),
            "--repo-root",
            str(ROOT),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert any(check["name"] == "desktop:icon-file" for check in payload["checks"])


def test_release_foundation_does_not_claim_final_packaging() -> None:
    text = "\n".join(
        [
            (ROOT / "release/README.md").read_text(encoding="utf-8"),
            (ROOT / "release/manifest.json").read_text(encoding="utf-8"),
            (ROOT / "release/version.json").read_text(encoding="utf-8"),
        ]
    )

    assert "No code signing" in text or "no code signing" in text
    assert "No auto updater" in text or "no auto updater" in text
    assert "No MSI / EXE release installer" in text or "no MSI or EXE installer" in text
    assert "No macOS DMG" in text or "no macOS DMG" in text


def test_release_build_output_is_gitignored() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "/release/build/" in gitignore

