"""Unified Phase 53 release preflight runner."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
HEADERS = {"X-Workspace-Id": "demo-workspace", "X-User-Id": "demo-user"}


@dataclass(slots=True)
class PreflightCheck:
    name: str
    status: str
    message: str
    duration_ms: int
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_command(name: str, command: list[str], cwd: Path = ROOT, soft: bool = False, timeout: int = 900) -> PreflightCheck:
    import time

    started = time.monotonic()
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
        duration_ms = int((time.monotonic() - started) * 1000)
        output = (proc.stdout or proc.stderr or "").strip()
        if proc.returncode == 0:
            return PreflightCheck(name, "PASS", "command succeeded", duration_ms, {"command": executable_command, "output": output[-800:]})
        status = "WARNING" if soft else "FAIL"
        return PreflightCheck(
            name,
            status,
            f"command exited {proc.returncode}",
            duration_ms,
            {"command": executable_command, "output": output[-1200:]},
        )
    except Exception as exc:  # noqa: BLE001 - preflight should report exact local blocker.
        duration_ms = int((time.monotonic() - started) * 1000)
        return PreflightCheck(name, "WARNING" if soft else "FAIL", str(exc), duration_ms, {"command": executable_command})


def http_check(name: str, url: str, soft: bool = False) -> PreflightCheck:
    import time

    started = time.monotonic()
    try:
        request = Request(url, headers=HEADERS)
        with urlopen(request, timeout=8) as response:  # noqa: S310 - local release smoke route.
            body = response.read(600).decode("utf-8", errors="replace")
            duration_ms = int((time.monotonic() - started) * 1000)
            status = "PASS" if 200 <= response.status < 300 else ("WARNING" if soft else "FAIL")
            return PreflightCheck(name, status, f"HTTP {response.status}", duration_ms, {"url": url, "body": body})
    except URLError as exc:
        duration_ms = int((time.monotonic() - started) * 1000)
        return PreflightCheck(name, "WARNING" if soft else "FAIL", str(exc), duration_ms, {"url": url})
    except Exception as exc:  # noqa: BLE001
        duration_ms = int((time.monotonic() - started) * 1000)
        return PreflightCheck(name, "WARNING" if soft else "FAIL", str(exc), duration_ms, {"url": url})


def frontend_build_checks(skip_build: bool) -> list[PreflightCheck]:
    if skip_build:
        return [PreflightCheck("frontend-build", "SKIPPED", "--skip-build", 0)]
    checks: list[PreflightCheck] = []
    for project in ("admin_dashboard", "worker_console", "worker_console_desktop"):
        checks.append(run_command(f"{project}:npm-build", ["npm", "run", "build"], ROOT / project, timeout=900))
    return checks


def docker_checks(profile: str, skip_docker: bool, strict: bool) -> list[PreflightCheck]:
    if skip_docker:
        return [PreflightCheck("docker-runtime", "SKIPPED", "--skip-docker", 0)]
    soft = not strict
    checks = [
        run_command("docker-compose-ps", ["docker", "compose", "ps"], ROOT, soft=soft, timeout=60),
        http_check("api-health", "http://localhost:8000/api/v1/health", soft=soft),
        http_check("browser-worker-health", "http://localhost:8000/api/v1/browser-workers/health/summary", soft=soft),
        http_check("task-runs-smoke", "http://localhost:8000/api/v1/task-runs", soft=soft),
        http_check("output-artifacts-smoke", "http://localhost:8000/api/v1/output-artifacts", soft=soft),
        http_check("conversation-playbooks-smoke", "http://localhost:8000/api/v1/conversation-playbooks", soft=soft),
        run_command(
            "deployment-verify",
            [PYTHON, "deployment/scripts/verify_environment.py", "--profile", profile],
            ROOT,
            soft=soft,
            timeout=120,
        ),
    ]
    return checks


def run_preflight(args: argparse.Namespace) -> list[PreflightCheck]:
    checks: list[PreflightCheck] = []
    if getattr(args, "skip_pytest", False):
        checks.append(PreflightCheck("pytest", "SKIPPED", "--skip-pytest", 0))
    else:
        checks.append(run_command("pytest", [PYTHON, "-m", "pytest"], timeout=1200))

    if args.skip_docs:
        checks.append(PreflightCheck("docs-verifier", "SKIPPED", "--skip-docs", 0))
    else:
        checks.append(run_command("docs-verifier", [PYTHON, "scripts/verify_docs_runtime.py"], timeout=600))

    checks.extend(
        [
            run_command("release-packaging-validator", [PYTHON, "release/scripts/validate_release_packaging.py"], timeout=120),
            run_command("runtime-hygiene", [PYTHON, "scripts/check_runtime_hygiene.py"], timeout=120),
            run_command("migration-continuity", [PYTHON, "scripts/check_migration_continuity.py"], timeout=120),
        ]
    )
    checks.extend(frontend_build_checks(args.skip_build))
    checks.extend(docker_checks(args.profile, args.skip_docker, args.strict))
    return checks


def summarize(checks: list[PreflightCheck], strict: bool) -> bool:
    if any(check.status == "FAIL" for check in checks):
        return False
    if strict and any(check.status == "WARNING" for check in checks):
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run unified release preflight checks.")
    parser.add_argument("--profile", default="server-docker")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--skip-docker", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-docs", action="store_true")
    parser.add_argument("--skip-pytest", action="store_true", help="Developer shortcut for script tests; release runs should not use it.")
    args = parser.parse_args()

    checks = run_preflight(args)
    success = summarize(checks, args.strict)
    payload = {
        "success": success,
        "profile": args.profile,
        "strict": args.strict,
        "checks": [check.to_dict() for check in checks],
    }

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Release preflight profile: {args.profile}")
        for check in checks:
            print(f"{check.status}: {check.name}: {check.message} ({check.duration_ms} ms)")
        print("SUMMARY: PASS" if success else "SUMMARY: FAIL")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
