"""Generate a release readiness report for the accepted mainline baseline."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


def run_json(command: list[str]) -> dict[str, Any]:
    proc = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {"success": proc.returncode == 0, "raw_output": (proc.stdout or proc.stderr)[-1200:]}
    payload["exit_code"] = proc.returncode
    return payload


def build_report(profile: str, include_live_checks: bool) -> dict[str, Any]:
    smoke_matrix = json.loads((ROOT / "release/smoke/smoke_matrix.json").read_text(encoding="utf-8"))
    profile_matrix = json.loads((ROOT / "release/smoke/profile_matrix.json").read_text(encoding="utf-8"))
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": "56",
        "baseline_phase": "55",
        "generated_at": datetime.now(UTC).isoformat(),
        "profile": profile,
        "status": "ci_readiness_snapshot",
        "smoke_matrix": smoke_matrix,
        "profile_matrix": profile_matrix.get("profiles", {}).get(profile, {}),
        "mainline_state": {
            "main": "Phase 55 stable baseline after PR #17 and post-merge stabilization",
            "post_merge_stabilization": "accepted on main",
            "ci_readiness_gates": "accepted on main",
            "required_checks": "tracked in .github/required-checks.json",
        },
        "remaining_risks": [
            "Tauri native packaging still needs customer-machine validation beyond frontend build.",
            "Server Docker Smoke is scheduled for daily server-docker coverage but should still be triggered manually for release-sensitive profile changes.",
            "GitHub branch protection must be configured in repository settings; this report only records the expected required checks.",
        ],
        "deferred_features": [
            "no production installer",
            "no code signing",
            "no auto updater",
            "no Kubernetes/Helm/Terraform",
            "no production HA orchestration",
            "no ComfyUI",
            "no real OpenClaw",
            "no real social media automation",
        ],
    }
    if include_live_checks:
        report["runtime_hygiene"] = run_json([PYTHON, "scripts/check_runtime_hygiene.py", "--json"])
        report["migration_continuity"] = run_json([PYTHON, "scripts/check_migration_continuity.py", "--json"])
        report["release_preflight_static"] = run_json(
            [
                PYTHON,
                "scripts/release_preflight.py",
                "--profile",
                profile,
                "--json",
                "--skip-pytest",
                "--skip-build",
                "--skip-docker",
                "--skip-docs",
            ]
        )
        report["required_ci_gates"] = run_json([PYTHON, "scripts/check_required_ci_gates.py", "--json"])
        report["release_smoke_static"] = run_json(
            [
                PYTHON,
                "scripts/release_smoke_matrix.py",
                "--profile",
                profile,
                "--json",
                "--group",
                "static",
                "--skip-docker",
                "--skip-build",
                "--skip-docs",
            ]
        )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate release readiness report JSON.")
    parser.add_argument("--profile", default="server-docker")
    parser.add_argument("--output", default="release/reports/release_readiness_report.json")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--include-live-checks", action="store_true")
    args = parser.parse_args()

    report = build_report(args.profile, args.include_live_checks)
    output_path = (ROOT / args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps({"success": True, "output": str(output_path), "report": report}, indent=2))
    else:
        print(f"PASS: release readiness report written to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
