"""Check profile dependencies for deployment bootstrap."""

from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

try:
    from common import CheckResult, ROOT, command_exists, env_file_exists, http_get_json, port_open
except ImportError:  # pragma: no cover - package import path for tests.
    from .common import CheckResult, ROOT, command_exists, env_file_exists, http_get_json, port_open


def dependency_checks(profile: str, env_file: str | None = None) -> list[CheckResult]:
    checks: list[CheckResult] = []

    def command(name: str, required: bool = True) -> None:
        exists = command_exists(name)
        checks.append(CheckResult(name, "PASS" if exists else ("FAIL" if required else "WARNING"), "found" if exists else "missing"))

    if profile in {"server-docker", "staging", "production-like"}:
        for item in ["python", "docker", "node", "npm", "git"]:
            command(item)
        checks.append(CheckResult("docker-compose", "PASS" if command_exists("docker") else "FAIL", "use docker compose plugin"))
        checks.append(CheckResult("env-file", "PASS" if env_file_exists(env_file) else "WARNING", "env file exists" if env_file_exists(env_file) else "env file not provided"))
    elif profile == "client-worker":
        command("python")
        checks.append(CheckResult("worker_config.yaml", "PASS" if (ROOT / "worker_client/worker_config.yaml").exists() else "WARNING", "worker_config.yaml exists" if (ROOT / "worker_client/worker_config.yaml").exists() else "copy worker_config.example.yaml first"))
        ok, detail = http_get_json("http://localhost:8000/api/v1/health")
        checks.append(CheckResult("ai-server-reachable", "PASS" if ok else "WARNING", detail[:160]))
        checks.append(CheckResult("runtime-port", "WARNING" if port_open("127.0.0.1", 9100) else "PASS", "9100 in use" if port_open("127.0.0.1", 9100) else "9100 available"))
        checks.append(CheckResult("firewall-advisory", "WARNING", "Do not expose port 9100 publicly; prefer VPN/Tailscale/LAN."))
    elif profile == "desktop-client":
        for item in ["node", "npm"]:
            command(item)
        command("cargo", required=False)
        if platform.system().lower() == "windows":
            command("link", required=False)
        checks.append(CheckResult("tauri-icon", "PASS" if (ROOT / "worker_console_desktop/src-tauri/icons/icon.ico").exists() else "FAIL", "Tauri icon present"))
        checks.append(CheckResult("webview2-advisory", "WARNING", "Ensure WebView2 runtime is installed on Windows client machines."))
    else:
        for item in ["python", "node", "npm", "git"]:
            command(item)
        command("docker", required=False)

    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Check deployment profile dependencies.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--env-file")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = dependency_checks(args.profile, args.env_file)
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
