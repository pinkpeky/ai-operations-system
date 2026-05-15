"""Analyze the Phase 43-53 PR chain and produce an integration inventory."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO = "pinkpeky/ai-operations-system"
INVENTORY_PATH = ROOT / "release/reports/pr_chain_inventory.json"


def load_offline_inventory() -> dict[str, Any]:
    payload = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    payload["mode"] = "offline"
    payload["generated_at"] = datetime.now(UTC).isoformat()
    return payload


def run_gh_json(repo: str) -> list[dict[str, Any]]:
    proc = subprocess.run(
        [
            "gh",
            "pr",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--json",
            "number,title,headRefName,baseRefName,state,url,headRefOid,files",
            "--limit",
            "50",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "gh pr list failed")
    return json.loads(proc.stdout)


def phase_from_title(title: str, branch: str) -> str:
    match = re.search(r"Phase\s+(\d+[A-Z]?)", title)
    if match:
        return match.group(1)
    match = re.search(r"phase-(\d+[a-z]?)", branch, re.IGNORECASE)
    if match:
        return match.group(1).upper()
    if "docs-stabilization" in branch:
        return "docs-stabilization"
    return "unknown"


def classify_files(files: list[dict[str, Any]]) -> dict[str, Any]:
    names = [str(item.get("path", "")) for item in files]
    return {
        "docs_touched": any(path.startswith("docs/") for path in names),
        "migrations_touched": any(path.startswith("alembic/versions/") for path in names),
        "api_routes_touched": any(path.startswith("app/api/routes/") for path in names),
        "frontend_surfaces_touched": any(path.startswith(("admin_dashboard/", "worker_console/", "worker_console_desktop/")) for path in names),
        "release_deployment_touched": any(path.startswith(("release/", "deployment/")) for path in names),
        "likely_conflict_areas": sorted(
            {
                area
                for path, area in [
                    ("alembic/versions/", "alembic/versions"),
                    ("app/api/routes/", "app/api/routes"),
                    ("app/workflow/", "app/workflow"),
                    ("app/task_orchestration/", "app/task_orchestration"),
                    ("admin_dashboard/", "admin_dashboard"),
                    ("worker_console/", "worker_console"),
                    ("worker_console_desktop/", "worker_console_desktop"),
                    ("release/", "release"),
                    ("deployment/", "deployment"),
                    ("docs/", "docs"),
                    ("tests/", "tests"),
                ]
                if any(name.startswith(path) for name in names)
            }
        ),
    }


def build_online_inventory(repo: str) -> dict[str, Any]:
    offline_items = {str(item["pr"]): item for item in load_offline_inventory()["items"]}
    prs = run_gh_json(repo)
    items: list[dict[str, Any]] = []
    for pr in sorted(prs, key=lambda item: int(item["number"])):
        phase = phase_from_title(str(pr["title"]), str(pr["headRefName"]))
        baseline = offline_items.get(str(pr["number"]), {})
        classified = classify_files(pr.get("files") or [])
        items.append(
            {
                "pr": pr["number"],
                "phase": phase,
                "title": pr["title"],
                "branch": pr["headRefName"],
                "status": str(pr["state"]).lower(),
                "base_branch": pr["baseRefName"],
                "head_commit": pr.get("headRefOid"),
                "url": pr.get("url"),
                "dependency_phase": baseline.get("dependency_phase", "unknown"),
                "expected_merge_order": baseline.get("expected_merge_order", 99),
                **classified,
            }
        )
    return {
        "schema_version": "1.0",
        "phase": "54",
        "mode": "github",
        "repo": repo,
        "generated_at": datetime.now(UTC).isoformat(),
        "items": items,
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# PR Chain Inventory",
        "",
        f"Generated mode: `{payload.get('mode')}`",
        "",
        "| PR | Phase | Branch | Base | Status | Expected Order |",
        "|---|---|---|---|---|---|",
    ]
    for item in payload.get("items", []):
        lines.append(
            f"| #{item.get('pr')} | {item.get('phase')} | `{item.get('branch')}` | `{item.get('base_branch')}` | {item.get('status')} | {item.get('expected_merge_order')} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze Phase 43-53 PR chain inventory.")
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    if args.offline:
        payload = load_offline_inventory()
    else:
        try:
            payload = build_online_inventory(args.repo)
        except Exception as exc:  # noqa: BLE001 - inventory should degrade to offline mode.
            payload = load_offline_inventory()
            payload["mode"] = "offline-fallback"
            payload["warning"] = str(exc)

    if args.output:
        output_path = (ROOT / args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        if args.markdown:
            output_path.write_text(to_markdown(payload), encoding="utf-8")
        else:
            output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.markdown and not args.json:
        print(to_markdown(payload), end="")
    else:
        print(json.dumps({"success": True, **payload}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
