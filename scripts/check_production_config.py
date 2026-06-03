"""Check formal production configuration without printing secrets."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.config import Settings  # noqa: E402


def build_report(*, require_production: bool) -> dict[str, Any]:
    settings = Settings()
    findings = settings.production_config_findings(require_production=require_production)
    errors = [item for item in findings if item.get("severity") == "error"]
    warnings = [item for item in findings if item.get("severity") == "warning"]
    return {
        "success": not errors,
        "app_env": settings.app_env,
        "production_config_strict": settings.production_config_strict,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "findings": findings,
    }


def print_text_report(report: dict[str, Any]) -> None:
    status = "PASS" if report["success"] else "FAIL"
    print(f"{status}: production configuration audit")
    print(f"APP_ENV={report['app_env']}")
    print(f"PRODUCTION_CONFIG_STRICT={str(report['production_config_strict']).lower()}")
    print(f"errors={report['error_count']} warnings={report['warning_count']}")
    for item in report["findings"]:
        severity = str(item["severity"]).upper()
        key = item["key"]
        message = item["message"]
        expected = item["expected"]
        actual = item["actual"]
        print(f"- [{severity}] {key}: {message} expected={expected}; actual={actual}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit production configuration guardrails.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Always exit 0; useful when inspecting a live server before changing .env.",
    )
    parser.add_argument(
        "--no-require-production",
        action="store_true",
        help="Do not fail when APP_ENV is not production.",
    )
    args = parser.parse_args()

    report = build_report(require_production=not args.no_require_production)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_text_report(report)
    if args.report_only:
        return 0
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
