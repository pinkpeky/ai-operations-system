"""Simulate Phase 43-55 mainline merge blast radius without mutating main."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def git(args: list[str]) -> tuple[int, str]:
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


def load_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def changed_files(base: str, head: str) -> list[str]:
    _, output = git(["diff", "--name-only", f"{base}..{head}"])
    return [line.strip() for line in output.splitlines() if line.strip()]


def classify(files: list[str]) -> dict[str, list[str]]:
    groups = {
        "migrations": [],
        "api": [],
        "frontend": [],
        "release_deployment": [],
        "docs": [],
        "tests": [],
        "other": [],
    }
    for path in files:
        normalized = path.replace("\\", "/")
        if normalized.startswith("alembic/versions/"):
            groups["migrations"].append(path)
        elif normalized.startswith("app/api/") or normalized.startswith("app/schemas/") or normalized.startswith("app/models/"):
            groups["api"].append(path)
        elif normalized.startswith(("admin_dashboard/", "worker_console/", "worker_console_desktop/")):
            groups["frontend"].append(path)
        elif normalized.startswith(("release/", "deployment/", "packaging/")):
            groups["release_deployment"].append(path)
        elif normalized.startswith("docs/"):
            groups["docs"].append(path)
        elif normalized.startswith("tests/"):
            groups["tests"].append(path)
        else:
            groups["other"].append(path)
    return groups


def build_simulation(base: str, head: str, offline: bool) -> dict[str, Any]:
    if head == "current":
        head = "HEAD"
    _, current_branch = git(["branch", "--show-current"])
    _, merge_base = git(["merge-base", base, head])
    _, base_commit = git(["rev-parse", base])
    _, head_commit = git(["rev-parse", head])
    files = changed_files(base, head)
    groups = classify(files)
    inventory = load_json("release/reports/pr_chain_inventory.json")
    integration_matrix = load_json("release/integration/integration_matrix.json")
    superseded = [
        {"pr": item.get("pr"), "phase": item.get("phase"), "recommendation": "supersede after RC accepted"}
        for item in inventory.get("items", [])
        if item.get("pr") not in {13, 14}
    ]
    superseded.extend(
        [
            {"pr": 13, "phase": "docs-stabilization", "recommendation": "keep until RC accepted"},
            {"pr": 14, "phase": "53", "recommendation": "keep as smoke/preflight source until RC accepted"},
            {"pr": 15, "phase": "54", "recommendation": "keep as Phase 55 base"},
        ]
    )
    return {
        "success": True,
        "mutates_main": False,
        "offline": offline,
        "current_branch": current_branch,
        "base": base,
        "head": head,
        "base_commit": base_commit,
        "head_commit": head_commit,
        "merge_base": merge_base,
        "changed_file_count": len(files),
        "changed_file_summary": {key: len(value) for key, value in groups.items()},
        "review_blast_radius": groups,
        "likely_superseded_prs": superseded,
        "migration_delta": groups["migrations"],
        "release_deployment_delta": groups["release_deployment"],
        "docs_delta": groups["docs"],
        "frontend_delta": groups["frontend"],
        "tests_delta": groups["tests"],
        "included_phases": [phase.get("phase") for phase in integration_matrix.get("phases", [])] + ["54", "55"],
    }


def to_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Mainline Merge Simulation",
        "",
        f"Base: `{report['base']}`",
        f"Head: `{report['head']}`",
        f"Mutates main: `{report['mutates_main']}`",
        f"Changed files: `{report['changed_file_count']}`",
        "",
        "## Changed File Summary",
        "",
    ]
    for key, value in report["changed_file_summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Likely Superseded PRs", ""])
    for item in report["likely_superseded_prs"]:
        lines.append(f"- PR #{item['pr']} ({item['phase']}): {item['recommendation']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Simulate mainline merge impact without modifying main.")
    parser.add_argument("--base", default="main")
    parser.add_argument("--head", default="current")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    report = build_simulation(args.base, args.head, args.offline)
    if args.json:
        print(json.dumps(report, indent=2))
    elif args.markdown:
        print(to_markdown(report))
    else:
        print(f"Mainline merge simulation {args.base}..{args.head}")
        print(f"Changed files: {report['changed_file_count']}")
        for key, value in report["changed_file_summary"].items():
            print(f"{key}: {value}")
        print("SUMMARY: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
