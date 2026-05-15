import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_pr_chain_inventory_schema_and_offline_mode() -> None:
    inventory = json.loads((ROOT / "release/reports/pr_chain_inventory.json").read_text(encoding="utf-8"))
    assert inventory["phase"] == "54"
    assert {item["phase"] for item in inventory["items"]} >= {"43", "44", "45", "46", "47", "48", "49", "50", "51", "52", "53"}
    assert all("expected_merge_order" in item for item in inventory["items"])


def test_analyze_pr_chain_offline_json() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/analyze_pr_chain.py", "--offline", "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["success"] is True
    assert payload["mode"] == "offline"
    assert any(item["pr"] == 14 for item in payload["items"])
