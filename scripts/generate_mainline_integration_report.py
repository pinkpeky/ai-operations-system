"""Generate Phase 55 mainline integration readiness reports."""

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
        payload = {"success": proc.returncode == 0, "raw_output": (proc.stdout or proc.stderr)[-1500:]}
    payload["exit_code"] = proc.returncode
    return payload


def load_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def build_report(profile: str) -> dict[str, Any]:
    readiness = run_json(
        [
            PYTHON,
            "scripts/mainline_readiness.py",
            "--profile",
            profile,
            "--offline",
            "--json",
            "--skip-docker",
            "--skip-build",
            "--skip-docs",
            "--skip-pytest",
            "--skip-smoke",
        ]
    )
    simulation = run_json([PYTHON, "scripts/simulate_mainline_merge.py", "--base", "main", "--head", "current", "--json", "--offline"])
    superseded = run_json([PYTHON, "scripts/generate_superseded_pr_report.py", "--json"])
    conflicts = run_json([PYTHON, "scripts/detect_integration_conflicts.py", "--json"])
    drift = run_json([PYTHON, "scripts/check_api_frontend_drift.py", "--json"])
    inventory = run_json([PYTHON, "scripts/analyze_pr_chain.py", "--offline", "--json"])

    return {
        "schema_version": "1.0",
        "phase": "55",
        "generated_at": datetime.now(UTC).isoformat(),
        "source_branch": "codex/phase-55-mainline-integration-release-candidate",
        "target_branch": "main",
        "candidate_branch": "codex/phase-43-55-release-candidate",
        "included_phases": load_json("release/integration/release_candidate_model.json")["included_phases"],
        "included_prs": [item.get("pr") for item in inventory.get("items", [])] + [15],
        "superseded_pr_recommendations": superseded,
        "readiness_gate_summary": readiness,
        "merge_simulation": simulation,
        "migration_continuity_status": "run scripts/check_migration_continuity.py for live status",
        "runtime_hygiene_status": "run scripts/check_runtime_hygiene.py for live status",
        "docs_verifier_status": "run scripts/verify_docs_runtime.py for live status",
        "release_preflight_status": "run scripts/release_preflight.py --profile server-docker for live status",
        "smoke_matrix_status": "run scripts/release_smoke_matrix.py for live status",
        "integration_preflight_status": "run scripts/integration_preflight.py --profile server-docker for live status",
        "api_frontend_drift_status": drift,
        "conflict_surface_summary": conflicts,
        "known_blockers": [],
        "known_warnings": [
            "This report is a QA artifact and should not be committed by default.",
            "The final RC PR toward main requires manual review before merge.",
        ],
        "manual_review_checklist": load_json("release/integration/release_candidate_model.json")["manual_review_gates"],
        "rollback_plan": load_json("release/integration/release_candidate_model.json")["rollback_model"],
        "recommended_pr_base": "main for the final RC PR after manual confirmation",
        "recommended_next_phase": "Create the final RC branch/PR only after Phase 55 gates are reviewed.",
    }


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Mainline Integration Report",
        "",
        f"Source branch: `{report['source_branch']}`",
        f"Target branch: `{report['target_branch']}`",
        f"Candidate branch: `{report['candidate_branch']}`",
        "",
        "## Included Phases",
        "",
    ]
    lines.extend(f"- {phase}" for phase in report["included_phases"])
    lines.extend(["", "## Known Warnings", ""])
    lines.extend(f"- {warning}" for warning in report["known_warnings"])
    lines.extend(["", "## Rollback Plan", "", report["rollback_plan"]["preferred"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate mainline integration readiness report.")
    parser.add_argument("--profile", default="server-docker")
    parser.add_argument("--json-output", default="release/reports/mainline_integration_report.json")
    parser.add_argument("--markdown-output", default="release/reports/mainline_integration_report.md")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    report = build_report(args.profile)
    json_path = ROOT / args.json_output
    md_path = ROOT / args.markdown_output
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    md_path.write_text(to_markdown(report), encoding="utf-8")
    payload = {"success": True, "json_output": str(json_path), "markdown_output": str(md_path), "report": report}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"PASS: mainline integration report written to {json_path} and {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
