"""Verify profile health after startup."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

try:
    from common import CheckResult, ROOT, http_get_json, load_healthchecks
except ImportError:  # pragma: no cover - package import path for tests.
    from .common import CheckResult, ROOT, http_get_json, load_healthchecks


def docker_compose_check() -> CheckResult:
    try:
        proc = subprocess.run(
            ["docker", "compose", "ps"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=20,
            check=True,
        )
        output = proc.stdout or ""
        return CheckResult("docker-compose-ps", "PASS", "docker compose ps succeeded", {"output": output[:600]})
    except Exception as exc:
        return CheckResult("docker-compose-ps", "FAIL", str(exc))


def verify_environment(profile: str) -> list[CheckResult]:
    results: list[CheckResult] = []
    if profile in {"server-docker", "staging", "production-like"}:
        results.append(docker_compose_check())
    if profile == "client-worker":
        config = ROOT / "worker_client/worker_config.yaml"
        results.append(CheckResult("worker_config.yaml", "PASS" if config.exists() else "WARNING", "exists" if config.exists() else "copy worker_config.example.yaml first"))
    if profile == "desktop-client":
        dist = ROOT / "worker_console_desktop/dist"
        icon = ROOT / "worker_console_desktop/src-tauri/icons/icon.ico"
        results.append(CheckResult("desktop-frontend-build", "PASS" if dist.exists() else "WARNING", "dist exists" if dist.exists() else "run npm run build"))
        results.append(CheckResult("tauri-icon", "PASS" if icon.exists() else "FAIL", "icon exists" if icon.exists() else "missing icon"))

    for item in load_healthchecks(profile):
        headers = item.get("headers") if isinstance(item.get("headers"), dict) else None
        ok, detail = http_get_json(str(item["url"]), headers=headers)
        required = bool(item.get("required"))
        status = "PASS" if ok else ("FAIL" if required else "WARNING")
        results.append(CheckResult(str(item["name"]), status, detail[:240], {"url": item["url"], "required": required}))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a deployment profile environment.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = verify_environment(args.profile)
    failed = any(item.status == "FAIL" for item in results)
    if args.json:
        print(json.dumps({"profile": args.profile, "success": not failed, "checks": [item.to_dict() for item in results]}, indent=2))
    else:
        for item in results:
            print(f"{item.status}: {item.name}: {item.message}")
        print("SUMMARY: PASS" if not failed else "SUMMARY: FAIL")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
