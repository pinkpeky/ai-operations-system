"""Detect high-risk integration conflict surfaces for the Phase 43-53 stack."""

from __future__ import annotations

import argparse
import json
import subprocess
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = "release/reports/conflict_surface_report.json"
DEFAULT_MD = "release/reports/conflict_surface_report.md"


def load_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def git_files() -> list[str]:
    proc = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True)
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def classify_surface(path: str) -> str | None:
    surfaces = [
        ("alembic/versions/", "migration sequence risk"),
        ("app/models/", "schema drift risk"),
        ("app/schemas/", "schema drift risk"),
        ("app/api/routes/", "duplicate route risk"),
        ("app/workflow/", "workflow runtime integration risk"),
        ("app/task_orchestration/", "task orchestration integration risk"),
        ("app/services/output_artifact_service.py", "artifact service integration risk"),
        ("admin_dashboard/src/api/", "frontend client drift risk"),
        ("worker_console/src/api/", "frontend client drift risk"),
        ("worker_console_desktop/src/api/", "frontend client drift risk"),
        ("deployment/", "release/deployment drift"),
        ("release/", "release/deployment drift"),
        ("docs/", "docs phase status drift"),
        ("tests/", "test matrix drift"),
    ]
    for prefix, label in surfaces:
        if path.startswith(prefix):
            return label
    return None


def build_report() -> dict[str, Any]:
    matrix = load_json("release/integration/conflict_surface_matrix.json")
    inventory = load_json("release/reports/pr_chain_inventory.json")
    files = git_files()
    grouped: dict[str, list[str]] = defaultdict(list)
    for path in files:
        label = classify_surface(path)
        if label:
            grouped[label].append(path)

    findings = []
    for surface in matrix["high_risk_surfaces"]:
        label = str(surface["risk"])
        touched = grouped.get(label, [])
        severity = "WARNING" if touched else "INFO"
        findings.append(
            {
                "surface": surface["surface"],
                "risk": label,
                "severity": severity,
                "phases": surface["phases"],
                "checks": surface["checks"],
                "tracked_files_sample": touched[:20],
                "tracked_file_count": len(touched),
            }
        )

    return {
        "schema_version": "1.0",
        "phase": "54",
        "generated_at": datetime.now(UTC).isoformat(),
        "success": True,
        "summary": {
            "finding_count": len(findings),
            "warning_count": sum(1 for item in findings if item["severity"] == "WARNING"),
            "pr_count": len(inventory.get("items", [])),
        },
        "findings": findings,
    }


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Conflict Surface Report",
        "",
        "| Surface | Risk | Severity | File Count |",
        "|---|---|---|---|",
    ]
    for item in report["findings"]:
        lines.append(f"| {item['surface']} | {item['risk']} | {item['severity']} | {item['tracked_file_count']} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect Phase 43-53 integration conflict surfaces.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--output-json", default=DEFAULT_JSON)
    parser.add_argument("--output-md", default=DEFAULT_MD)
    args = parser.parse_args()

    report = build_report()
    if not args.no_write:
        json_path = ROOT / args.output_json
        md_path = ROOT / args.output_md
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        md_path.write_text(to_markdown(report), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(to_markdown(report), end="")
        print("SUMMARY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
