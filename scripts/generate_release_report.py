"""Generate a Phase 53 release readiness report."""

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
        "phase": "53",
        "generated_at": datetime.now(UTC).isoformat(),
        "profile": profile,
        "status": "integration_candidate",
        "smoke_matrix": smoke_matrix,
        "profile_matrix": profile_matrix.get("profiles", {}).get(profile, {}),
        "open_pr_chain": {
            "main": "Phase 42 stable baseline",
            "phase_43_to_52": "open PR chain",
            "docs_stabilization": "PR #13",
        },
        "known_blockers": [
            "Phase 43-52 PR chain remains open and must be integrated deliberately.",
            "Tauri native packaging still needs customer-machine validation.",
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
