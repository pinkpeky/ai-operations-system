"""Run Phase 55 mainline release candidate readiness checks."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


@dataclass(slots=True)
class ReadinessCheck:
    name: str
    status: str
    message: str
    blocking: bool
    duration_ms: int = 0
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def run_command(
    name: str,
    command: list[str],
    *,
    blocking: bool = True,
    soft: bool = False,
    timeout: int = 1200,
) -> ReadinessCheck:
    started = time.monotonic()
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
        duration_ms = int((time.monotonic() - started) * 1000)
        output = (proc.stdout or proc.stderr or "").strip()
        if proc.returncode == 0:
            return ReadinessCheck(name, "PASS", "command succeeded", blocking, duration_ms, {"command": command, "output": output[-1000:]})
        return ReadinessCheck(
            name,
            "WARNING" if soft else "FAIL",
            f"exit {proc.returncode}",
            blocking,
            duration_ms,
            {"command": command, "output": output[-1500:]},
        )
    except Exception as exc:  # noqa: BLE001 - readiness should report local blockers.
        duration_ms = int((time.monotonic() - started) * 1000)
        return ReadinessCheck(name, "WARNING" if soft else "FAIL", str(exc), blocking, duration_ms, {"command": command})


def git_output(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return proc.returncode, (proc.stdout or proc.stderr).strip()


def git_cleanliness() -> ReadinessCheck:
    code, output = git_output(["status", "--short"])
    if code != 0:
        return ReadinessCheck("git-cleanliness", "WARNING", output, False)
    if output:
        return ReadinessCheck("git-cleanliness", "WARNING", "working tree has uncommitted files", False, metadata={"status": output})
    return ReadinessCheck("git-cleanliness", "PASS", "working tree clean", False)


def branch_lineage() -> ReadinessCheck:
    _, current = git_output(["branch", "--show-current"])
    _, main_head = git_output(["rev-parse", "main"])
    _, merge_base = git_output(["merge-base", "main", "HEAD"])
    base_code, phase54_ancestor = git_output(
        ["merge-base", "--is-ancestor", "codex/phase-54-integration-branch-pr-chain-reconciliation", "HEAD"]
    )
    status = "PASS" if current.startswith("codex/phase-55-") and base_code == 0 else "WARNING"
    message = "Phase 55 branch descends from Phase 54" if status == "PASS" else "branch lineage should be reviewed"
    return ReadinessCheck(
        "branch-lineage",
        status,
        message,
        blocking=False,
        metadata={"current_branch": current, "main_head": main_head, "merge_base": merge_base, "phase54_is_ancestor": base_code == 0, "raw": phase54_ancestor},
    )


def ignored_artifact_check() -> ReadinessCheck:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    required_patterns = [
        "/release/reports/mainline_integration_report.json",
        "/release/reports/mainline_integration_report.md",
        "/release/reports/superseded_prs.json",
        "/docs/rendered/",
        "node_modules/",
        "/storage/output_artifacts/",
    ]
    missing = [pattern for pattern in required_patterns if pattern not in gitignore]
    if missing:
        return ReadinessCheck("ignored-artifact-check", "FAIL", "missing generated artifact ignore patterns", True, metadata={"missing": missing})
    return ReadinessCheck("ignored-artifact-check", "PASS", "generated report/runtime artifact patterns are ignored", True)


def command_with_common_flags(base: list[str], args: argparse.Namespace) -> list[str]:
    command = base[:]
    if "--profile" not in command:
        command.extend(["--profile", args.profile])
    if args.strict:
        command.append("--strict")
    if args.skip_docker:
        command.append("--skip-docker")
    if args.skip_build or args.skip_frontend:
        command.append("--skip-build")
    if args.skip_docs:
        command.append("--skip-docs")
    if args.skip_pytest:
        command.append("--skip-pytest")
    return command


def run_readiness(args: argparse.Namespace) -> list[ReadinessCheck]:
    checks: list[ReadinessCheck] = [git_cleanliness(), ignored_artifact_check(), branch_lineage()]

    checks.append(
        run_command(
            "integration-preflight",
            command_with_common_flags([PYTHON, "scripts/integration_preflight.py"], args),
            blocking=True,
            timeout=1800,
        )
    )
    checks.append(
        run_command(
            "release-preflight",
            command_with_common_flags([PYTHON, "scripts/release_preflight.py"], args),
            blocking=True,
            timeout=1800,
        )
    )

    if args.skip_smoke:
        checks.append(ReadinessCheck("release-smoke-matrix", "SKIPPED", "--skip-smoke", blocking=False))
    else:
        checks.append(run_command("release-smoke-matrix", [PYTHON, "scripts/release_smoke_matrix.py"], blocking=True, timeout=1200))

    if args.skip_docs:
        checks.append(ReadinessCheck("docs-verifier", "SKIPPED", "--skip-docs", blocking=True))
    else:
        checks.append(run_command("docs-verifier", [PYTHON, "scripts/verify_docs_runtime.py"], blocking=True, timeout=600))

    checks.extend(
        [
            run_command("migration-continuity", [PYTHON, "scripts/check_migration_continuity.py"], blocking=True),
            run_command("runtime-hygiene", [PYTHON, "scripts/check_runtime_hygiene.py"], blocking=True),
            run_command("release-packaging-validator", [PYTHON, "release/scripts/validate_release_packaging.py"], blocking=True),
            run_command("api-frontend-drift", [PYTHON, "scripts/check_api_frontend_drift.py", "--json"], blocking=True),
            run_command(
                "pr-chain-inventory",
                [PYTHON, "scripts/analyze_pr_chain.py", "--offline", "--json"] if args.offline or args.skip_github else [PYTHON, "scripts/analyze_pr_chain.py", "--json"],
                blocking=False,
                soft=args.offline or args.skip_github,
            ),
            run_command("conflict-surface-detection", [PYTHON, "scripts/detect_integration_conflicts.py", "--json"], blocking=False, soft=not args.strict),
        ]
    )

    if args.skip_docker:
        checks.append(ReadinessCheck("deployment-verification", "SKIPPED", "--skip-docker", blocking=True))
    else:
        checks.append(
            run_command(
                "deployment-verification",
                [PYTHON, "deployment/scripts/verify_environment.py", "--profile", args.profile],
                blocking=True,
                timeout=300,
            )
        )
    return checks


def summarize(checks: list[ReadinessCheck], strict: bool) -> bool:
    for check in checks:
        if check.status == "FAIL" and check.blocking:
            return False
        if strict and check.status in {"FAIL", "WARNING"}:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Run mainline release candidate readiness checks.")
    parser.add_argument("--profile", default="server-docker")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--skip-docker", action="store_true")
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--skip-docs", action="store_true")
    parser.add_argument("--skip-pytest", action="store_true")
    parser.add_argument("--skip-github", action="store_true")
    parser.add_argument("--skip-frontend", action="store_true")
    parser.add_argument("--skip-smoke", action="store_true")
    args = parser.parse_args()

    checks = run_readiness(args)
    success = summarize(checks, args.strict)
    payload = {
        "success": success,
        "phase": "55",
        "profile": args.profile,
        "strict": args.strict,
        "checks": [check.to_dict() for check in checks],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"Mainline readiness profile: {args.profile}")
        for check in checks:
            blocking = "blocking" if check.blocking else "non-blocking"
            print(f"{check.status}: {check.name}: {check.message} ({blocking})")
        print("SUMMARY: PASS" if success else "SUMMARY: FAIL")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
