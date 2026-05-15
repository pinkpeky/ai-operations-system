"""Run Phase 54 integration preflight checks for the Phase 43-53 PR stack."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


@dataclass(slots=True)
class IntegrationCheck:
    name: str
    status: str
    message: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_command(name: str, command: list[str], soft: bool = False, timeout: int = 1200) -> IntegrationCheck:
    try:
        proc = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        output = (proc.stdout or proc.stderr or "").strip()
        if proc.returncode == 0:
            return IntegrationCheck(name, "PASS", "command succeeded", {"command": command, "output": output[-1000:]})
        return IntegrationCheck(name, "WARNING" if soft else "FAIL", f"exit {proc.returncode}", {"command": command, "output": output[-1500:]})
    except Exception as exc:  # noqa: BLE001 - integration preflight reports local blockers.
        return IntegrationCheck(name, "WARNING" if soft else "FAIL", str(exc), {"command": command})


def add_optional_flags(command: list[str], args: argparse.Namespace, include_pytest: bool = False) -> list[str]:
    command = command[:]
    if args.profile:
        command.extend(["--profile", args.profile])
    if args.json_child:
        command.append("--json")
    if args.strict:
        command.append("--strict")
    if args.skip_docker:
        command.append("--skip-docker")
    if args.skip_build:
        command.append("--skip-build")
    if args.skip_docs:
        command.append("--skip-docs")
    if include_pytest and args.skip_pytest:
        command.append("--skip-pytest")
    return command


def run_preflight(args: argparse.Namespace) -> list[IntegrationCheck]:
    checks: list[IntegrationCheck] = []
    checks.append(
        run_command(
            "release-preflight",
            add_optional_flags([PYTHON, "scripts/release_preflight.py"], args, include_pytest=True),
            timeout=1800,
        )
    )
    checks.append(
        run_command(
            "release-smoke-matrix",
            add_optional_flags([PYTHON, "scripts/release_smoke_matrix.py"], args),
            timeout=1200,
        )
    )
    if args.skip_docs:
        checks.append(IntegrationCheck("docs-verifier", "SKIPPED", "--skip-docs"))
        checks.append(IntegrationCheck("phase-index-consistency", "SKIPPED", "--skip-docs"))
    else:
        checks.append(run_command("docs-verifier", [PYTHON, "scripts/verify_docs_runtime.py"], timeout=600))
        checks.append(run_command("phase-index-consistency", [PYTHON, "scripts/verify_docs_runtime.py"], timeout=600))

    checks.extend(
        [
            run_command("migration-continuity", [PYTHON, "scripts/check_migration_continuity.py"]),
            run_command("runtime-hygiene", [PYTHON, "scripts/check_runtime_hygiene.py"]),
            run_command("release-packaging-validator", [PYTHON, "release/scripts/validate_release_packaging.py"]),
            run_command("api-frontend-drift", [PYTHON, "scripts/check_api_frontend_drift.py", "--json"]),
            run_command("pr-chain-inventory", [PYTHON, "scripts/analyze_pr_chain.py", "--offline", "--json"]),
            run_command("conflict-surface-detection", [PYTHON, "scripts/detect_integration_conflicts.py", "--json"]),
        ]
    )
    if args.skip_docker:
        checks.append(IntegrationCheck("deployment-profile-verify", "SKIPPED", "--skip-docker"))
    else:
        checks.append(run_command("deployment-profile-verify", [PYTHON, "deployment/scripts/verify_environment.py", "--profile", args.profile], soft=not args.strict))
    return checks


def summarize(checks: list[IntegrationCheck], strict: bool) -> bool:
    if any(check.status == "FAIL" for check in checks):
        return False
    if strict and any(check.status == "WARNING" for check in checks):
        return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run integration preflight for Phase 43-53 reconciliation.")
    parser.add_argument("--from-phase", default="43")
    parser.add_argument("--to-phase", default="53")
    parser.add_argument("--profile", default="server-docker")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--skip-docker", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-docs", action="store_true")
    parser.add_argument("--skip-pytest", action="store_true")
    parser.add_argument("--skip-github", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--json-child", action="store_true", help="Ask child commands for JSON output.")
    args = parser.parse_args()

    checks = run_preflight(args)
    success = summarize(checks, args.strict)
    payload = {
        "success": success,
        "from_phase": args.from_phase,
        "to_phase": args.to_phase,
        "profile": args.profile,
        "strict": args.strict,
        "checks": [check.to_dict() for check in checks],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Integration preflight Phase {args.from_phase}-{args.to_phase} profile: {args.profile}")
        for check in checks:
            print(f"{check.status}: {check.name}: {check.message}")
        print("SUMMARY: PASS" if success else "SUMMARY: FAIL")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
