"""Generate Phase 54 integration readiness reports."""

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


def load_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def build_report(profile: str, include_live_checks: bool) -> dict[str, Any]:
    inventory = run_json([PYTHON, "scripts/analyze_pr_chain.py", "--offline", "--json"])
    conflicts = run_json([PYTHON, "scripts/detect_integration_conflicts.py", "--json"])
    drift = run_json([PYTHON, "scripts/check_api_frontend_drift.py", "--json"])
    report: dict[str, Any] = {
        "schema_version": "1.0",
        "phase": "54",
        "generated_at": datetime.now(UTC).isoformat(),
        "integration_branch": "codex/phase-54-integration-branch-pr-chain-reconciliation",
        "base_branch": "codex/phase-53-release-smoke-test-matrix-preflight",
        "phase_range": "43-53",
        "profile": profile,
        "status": "integration_candidate",
        "pr_chain_inventory": inventory,
        "dependency_matrix": load_json("release/integration/phase_dependency_matrix.json"),
        "conflict_surface_summary": conflicts,
        "api_frontend_drift": drift,
        "known_blockers": [
            "Phase 43-53 PR chain is still open and should be merged deliberately.",
            "Production installer, code signing, auto-update, Kubernetes, and HA orchestration remain deferred.",
        ],
        "known_warnings": [
            "PR #14 should remain the Phase 54 base unless it is merged first.",
            "Generated reports are QA artifacts and should not be committed.",
        ],
        "recommended_merge_order": load_json("release/integration/phase_dependency_matrix.json")["recommended_merge_order"],
        "rollback_plan": "Rollback the integration candidate merge or revert individual phase PRs in reverse dependency order.",
        "next_phase_recommendation": "Merge/rebase reconciliation decisions before starting new runtime features.",
    }
    if include_live_checks:
        report["migration_continuity"] = run_json([PYTHON, "scripts/check_migration_continuity.py", "--json"])
        report["runtime_hygiene"] = run_json([PYTHON, "scripts/check_runtime_hygiene.py", "--json"])
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


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Integration Readiness Report",
        "",
        f"Integration branch: `{report['integration_branch']}`",
        f"Base branch: `{report['base_branch']}`",
        f"Phase range: `{report['phase_range']}`",
        f"Status: `{report['status']}`",
        "",
        "## Recommended Merge Order",
        "",
    ]
    lines.extend(f"- {item}" for item in report["recommended_merge_order"])
    lines.extend(["", "## Known Blockers", ""])
    lines.extend(f"- {item}" for item in report["known_blockers"])
    lines.extend(["", "## Rollback Plan", "", report["rollback_plan"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate integration readiness report.")
    parser.add_argument("--profile", default="server-docker")
    parser.add_argument("--json-output", default="release/reports/integration_readiness_report.json")
    parser.add_argument("--markdown-output", default="release/reports/integration_readiness_report.md")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--include-live-checks", action="store_true")
    args = parser.parse_args()

    report = build_report(args.profile, args.include_live_checks)
    json_path = ROOT / args.json_output
    md_path = ROOT / args.markdown_output
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(to_markdown(report), encoding="utf-8")

    payload = {"success": True, "json_output": str(json_path), "markdown_output": str(md_path), "report": report}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"PASS: integration readiness report written to {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
