"""Validate Phase 51 release packaging foundation files."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Check:
    name: str
    success: bool
    message: str


REQUIRED_FILES = [
    "release/manifest.json",
    "release/version.json",
    "release/env/aiops.release.env.template",
    "release/scripts/build_server_bundle.ps1",
    "release/scripts/build_server_bundle.sh",
    "release/scripts/build_frontend_bundles.ps1",
    "release/scripts/build_frontend_bundles.sh",
    "release/scripts/check_desktop_release_readiness.ps1",
    "release/scripts/check_desktop_release_readiness.sh",
    "release/windows/start_server.ps1",
    "release/windows/start_admin_dashboard.ps1",
    "release/windows/start_worker_console.ps1",
    "release/windows/start_desktop_console.ps1",
    "release/mac/start_server.sh",
    "release/mac/start_admin_dashboard.sh",
    "release/mac/start_worker_console.sh",
    "release/mac/start_desktop_console.sh",
    "deployment/README.md",
    "deployment/scripts/generate_env.py",
    "deployment/scripts/check_dependencies.py",
    "deployment/scripts/check_ports.py",
    "deployment/scripts/verify_environment.py",
    "deployment/windows/start_server_docker.ps1",
    "deployment/windows/start_admin_dashboard.ps1",
    "deployment/windows/start_worker_console.ps1",
    "deployment/windows/start_desktop_console.ps1",
    "deployment/windows/start_client_worker.ps1",
    "deployment/windows/verify_profile.ps1",
    "deployment/mac/start_server_docker.sh",
    "deployment/mac/start_admin_dashboard.sh",
    "deployment/mac/start_worker_console.sh",
    "deployment/mac/start_desktop_console.sh",
    "deployment/mac/start_client_worker.sh",
    "deployment/mac/verify_profile.sh",
]

DEPLOYMENT_PROFILES = [
    "local-dev",
    "server-docker",
    "client-worker",
    "desktop-client",
    "staging",
    "production-like",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def validate(repo_root: Path) -> list[Check]:
    checks: list[Check] = []

    for relative in REQUIRED_FILES:
        path = repo_root / relative
        checks.append(Check(f"file:{relative}", path.exists(), "exists" if path.exists() else "missing"))

    try:
        manifest = load_json(repo_root / "release/manifest.json")
        checks.append(Check("manifest:json", True, "valid JSON"))
    except Exception as exc:  # noqa: BLE001 - validator should report all file format errors.
        manifest = {}
        checks.append(Check("manifest:json", False, str(exc)))

    try:
        version = load_json(repo_root / "release/version.json")
        checks.append(Check("version:json", True, "valid JSON"))
    except Exception as exc:  # noqa: BLE001
        version = {}
        checks.append(Check("version:json", False, str(exc)))

    boundaries = manifest.get("boundaries", {})
    expected_false = [
        "formal_installer",
        "code_signing",
        "auto_updater",
        "msi_exe_release",
        "macos_dmg_notarization",
        "kubernetes_helm",
        "terraform_ansible",
        "comfyui",
        "real_social_publishing",
    ]
    for key in expected_false:
        checks.append(
            Check(
                f"boundary:{key}",
                boundaries.get(key) is False,
                "disabled" if boundaries.get(key) is False else "must be false",
            )
        )

    components = {component.get("name") for component in manifest.get("components", []) if isinstance(component, dict)}
    for name in {"api-server", "admin-dashboard", "worker-console", "worker-console-desktop"}:
        checks.append(Check(f"component:{name}", name in components, "declared" if name in components else "missing"))

    if version.get("phase") == "51" and version.get("status") == "packaging_foundation":
        checks.append(Check("version:phase51", True, "phase 51 packaging foundation"))
    else:
        checks.append(Check("version:phase51", False, "version metadata must declare phase 51 packaging foundation"))

    tauri_config_path = repo_root / "worker_console_desktop/src-tauri/tauri.conf.json"
    icon_path = repo_root / "worker_console_desktop/src-tauri/icons/icon.ico"
    try:
        tauri_config = load_json(tauri_config_path)
        icons = tauri_config.get("bundle", {}).get("icon", [])
        checks.append(Check("desktop:icon-config", "icons/icon.ico" in icons, "icons/icon.ico configured"))
    except Exception as exc:  # noqa: BLE001
        checks.append(Check("desktop:icon-config", False, str(exc)))
    checks.append(Check("desktop:icon-file", icon_path.exists() and icon_path.stat().st_size > 0, "icon exists and is non-empty"))

    forbidden = [".env", "worker_state.json", "node_modules/", "runtime_state/", "logs/"]
    manifest_forbidden = manifest.get("forbidden_artifacts", [])
    for item in forbidden:
        checks.append(Check(f"forbidden:{item}", item in manifest_forbidden, "listed" if item in manifest_forbidden else "missing"))

    manifest_profiles = set(manifest.get("deployment_profiles", {}).get("profiles", []))
    version_profiles = set(version.get("components", {}).get("deployment_profiles", {}).get("profiles", []))
    for profile in DEPLOYMENT_PROFILES:
        profile_root = repo_root / "deployment" / "profiles" / profile
        profile_files = ["profile.json", "env.template", "ports.json", "services.json", "healthchecks.json", "README.md"]
        checks.append(Check(f"deployment-profile:{profile}:manifest", profile in manifest_profiles, "declared in manifest"))
        checks.append(Check(f"deployment-profile:{profile}:version", profile in version_profiles, "declared in version metadata"))
        for filename in profile_files:
            path = profile_root / filename
            checks.append(Check(f"deployment-profile:{profile}:{filename}", path.exists(), "exists" if path.exists() else "missing"))

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Phase 51 release packaging foundation.")
    parser.add_argument("--repo-root", default=".", help="Repository root. Defaults to current directory.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    checks = validate(repo_root)
    success = all(check.success for check in checks)

    if args.json:
        print(
            json.dumps(
                {
                    "success": success,
                    "checks": [asdict(check) for check in checks],
                },
                indent=2,
            )
        )
    else:
        for check in checks:
            label = "PASS" if check.success else "FAIL"
            print(f"{label}: {check.name}: {check.message}")
        print("SUMMARY: PASS" if success else "SUMMARY: FAIL")

    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
