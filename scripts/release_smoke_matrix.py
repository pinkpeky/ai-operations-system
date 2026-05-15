"""Run the Phase 53 release smoke matrix."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


@dataclass(slots=True)
class SmokeResult:
    group: str
    name: str
    status: str
    message: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def run_command(group: str, name: str, command: list[str], cwd: Path = ROOT, soft: bool = False, timeout: int = 900) -> SmokeResult:
    executable_command = command[:]
    if sys.platform.startswith("win") and executable_command and executable_command[0].lower() == "npm":
        executable_command[0] = "npm.cmd"
    try:
        proc = subprocess.run(
            executable_command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        output = (proc.stdout or proc.stderr or "").strip()
        if proc.returncode == 0:
            return SmokeResult(group, name, "PASS", "command succeeded", {"command": executable_command, "output": output[-800:]})
        return SmokeResult(group, name, "WARNING" if soft else "FAIL", f"exit {proc.returncode}", {"command": executable_command, "output": output[-1200:]})
    except Exception as exc:  # noqa: BLE001
        return SmokeResult(group, name, "WARNING" if soft else "FAIL", str(exc), {"command": executable_command})


def route_check(route: dict[str, Any], soft: bool = False) -> SmokeResult:
    runtime = load_json("release/smoke/runtime_matrix.json")
    base_url = str(runtime.get("base_url", "http://localhost:8000")).rstrip("/")
    headers = runtime.get("headers", {}) if isinstance(runtime.get("headers"), dict) else {}
    url = base_url + str(route["path"])
    try:
        request = Request(url, headers={str(key): str(value) for key, value in headers.items()})
        with urlopen(request, timeout=8) as response:  # noqa: S310 - local smoke route.
            body = response.read(500).decode("utf-8", errors="replace")
            status = "PASS" if 200 <= response.status < 300 else ("WARNING" if soft else "FAIL")
            return SmokeResult(str(route.get("group", "runtime")), str(route["name"]), status, f"HTTP {response.status}", {"url": url, "body": body})
    except Exception as exc:  # noqa: BLE001
        return SmokeResult(str(route.get("group", "runtime")), str(route["name"]), "WARNING" if soft else "FAIL", str(exc), {"url": url})


def run_static() -> list[SmokeResult]:
    return [
        run_command("static", "runtime_hygiene", [PYTHON, "scripts/check_runtime_hygiene.py"]),
        run_command("static", "migration_continuity", [PYTHON, "scripts/check_migration_continuity.py"]),
        run_command("static", "release_packaging_validator", [PYTHON, "release/scripts/validate_release_packaging.py"]),
    ]


def run_docs(skip_docs: bool) -> list[SmokeResult]:
    if skip_docs:
        return [SmokeResult("docs", "docs_verifier", "SKIPPED", "--skip-docs")]
    return [run_command("docs", "docs_verifier", [PYTHON, "scripts/verify_docs_runtime.py"], timeout=600)]


def run_builds(skip_build: bool) -> list[SmokeResult]:
    if skip_build:
        return [SmokeResult("frontend-build", "frontend_builds", "SKIPPED", "--skip-build")]
    return [
        run_command("frontend-build", "admin_dashboard_build", ["npm", "run", "build"], ROOT / "admin_dashboard"),
        run_command("frontend-build", "worker_console_build", ["npm", "run", "build"], ROOT / "worker_console"),
        run_command("frontend-build", "worker_console_desktop_build", ["npm", "run", "build"], ROOT / "worker_console_desktop"),
    ]


def run_docker(profile: str, skip_docker: bool, strict: bool) -> list[SmokeResult]:
    if skip_docker:
        return [SmokeResult("docker-runtime", "docker_runtime", "SKIPPED", "--skip-docker")]
    soft = not strict
    runtime = load_json("release/smoke/runtime_matrix.json")
    routes = [item for item in runtime.get("routes", []) if isinstance(item, dict)]
    results = [run_command("docker-runtime", "docker_compose_ps", ["docker", "compose", "ps"], soft=soft, timeout=60)]
    results.extend(route_check(route, soft=soft) for route in routes)
    return results


def run_deployment(profile: str, skip_docker: bool, strict: bool) -> list[SmokeResult]:
    if skip_docker:
        return [SmokeResult("deployment", "deployment_verify_profile", "SKIPPED", "--skip-docker")]
    return [
        run_command(
            "deployment",
            "deployment_verify_profile",
            [PYTHON, "deployment/scripts/verify_environment.py", "--profile", profile],
            soft=not strict,
            timeout=120,
        )
    ]


def run_matrix(args: argparse.Namespace) -> list[SmokeResult]:
    requested_groups = set(args.group or [])
    results: list[SmokeResult] = []
    runners = {
        "static": lambda: run_static(),
        "docs": lambda: run_docs(args.skip_docs),
        "frontend-build": lambda: run_builds(args.skip_build),
        "docker-runtime": lambda: run_docker(args.profile, args.skip_docker, args.strict),
        "deployment": lambda: run_deployment(args.profile, args.skip_docker, args.strict),
    }
    for group, runner in runners.items():
        if requested_groups and group not in requested_groups:
            continue
        results.extend(runner())
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run release smoke matrix.")
    parser.add_argument("--profile", default="server-docker")
    parser.add_argument("--group", action="append", help="Run only a named group. Can be repeated.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--skip-docker", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-docs", action="store_true")
    args = parser.parse_args()

    results = run_matrix(args)
    success = not any(result.status == "FAIL" for result in results)
    if args.strict and any(result.status == "WARNING" for result in results):
        success = False

    payload = {"success": success, "profile": args.profile, "results": [result.to_dict() for result in results]}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Release smoke matrix profile: {args.profile}")
        print("| Group | Check | Status | Message |")
        print("|---|---|---|---|")
        for result in results:
            print(f"| {result.group} | {result.name} | {result.status} | {result.message.replace('|', '/')} |")
        print("SUMMARY: PASS" if success else "SUMMARY: FAIL")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
