"""Read-only OpenClaw provider readiness smoke check."""

from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any

import httpx


DEFAULT_WORKER_BASE_URL = "http://127.0.0.1:9100"


async def _get_json(client: httpx.AsyncClient, base_url: str, path: str) -> tuple[dict[str, Any] | None, str | None]:
    try:
        response = await client.get(f"{base_url.rstrip('/')}{path}")
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return None, "invalid_json_payload"
        return payload, None
    except httpx.HTTPStatusError as exc:
        return None, f"http_status_{exc.response.status_code}"
    except httpx.RequestError as exc:
        return None, f"request_failed: {exc}"
    except ValueError as exc:
        return None, f"invalid_json_payload: {exc}"


def _capability_ready(capabilities: dict[str, Any] | None) -> bool:
    if not capabilities:
        return False
    inner = capabilities.get("capabilities")
    actions = capabilities.get("actions")
    if not isinstance(inner, dict) or not isinstance(actions, list):
        return False
    return (
        bool(capabilities.get("success"))
        and capabilities.get("mock") is False
        and inner.get("real_publish_submit") is True
        and inner.get("publish_submit_guarded") is True
        and "publish_submit_guarded" in actions
    )


def _health_ready(health: dict[str, Any] | None) -> bool:
    if not health:
        return False
    return (
        bool(health.get("success"))
        and bool(health.get("enabled"))
        and bool(health.get("reachable"))
        and health.get("mock") is False
    )


def _diagnostics_ready(diagnostics: dict[str, Any] | None) -> bool:
    if not diagnostics:
        return False
    return (
        bool(diagnostics.get("configured"))
        and diagnostics.get("mock") is False
        and diagnostics.get("readiness_status") == "openclaw_provider_configured_pending_capability_check"
    )


async def build_report(
    *,
    base_url: str = DEFAULT_WORKER_BASE_URL,
    timeout_seconds: float = 10.0,
    transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    """Build a sanitized provider readiness report without executing actions."""

    async with httpx.AsyncClient(timeout=timeout_seconds, transport=transport) as client:
        diagnostics, diagnostics_error = await _get_json(client, base_url, "/openclaw/provider-diagnostics")
        health, health_error = await _get_json(client, base_url, "/openclaw/health")
        capabilities, capabilities_error = await _get_json(client, base_url, "/openclaw/capabilities")

    errors = [
        error
        for error in [
            diagnostics_error and f"provider_diagnostics:{diagnostics_error}",
            health_error and f"health:{health_error}",
            capabilities_error and f"capabilities:{capabilities_error}",
        ]
        if error
    ]
    diagnostics_ready = _diagnostics_ready(diagnostics)
    health_ready = _health_ready(health)
    capabilities_ready = _capability_ready(capabilities)
    blockers: list[str] = []
    if not diagnostics_ready:
        blockers.append(str((diagnostics or {}).get("readiness_status") or "provider_diagnostics_not_ready"))
    if not health_ready:
        blockers.append(str((health or {}).get("error") or "openclaw_health_not_ready"))
    if not capabilities_ready:
        blockers.append(str((capabilities or {}).get("error") or "openclaw_capabilities_not_ready"))
    blockers.extend(errors)

    return {
        "success": diagnostics_ready and health_ready and capabilities_ready and not errors,
        "base_url": base_url,
        "contract": "openclaw_provider_readiness_smoke",
        "server_side_external_execution": False,
        "actual_publish_performed": False,
        "diagnostics": diagnostics,
        "health": health,
        "capabilities": capabilities,
        "blocking_reasons": blockers,
    }


def print_text_report(report: dict[str, Any]) -> None:
    status = "PASS" if report["success"] else "FAIL"
    print(f"{status}: OpenClaw provider readiness smoke")
    print(f"base_url={report['base_url']}")
    print(f"contract={report['contract']}")
    print("server_side_external_execution=false")
    print("actual_publish_performed=false")
    for blocker in report["blocking_reasons"]:
        print(f"- blocker: {blocker}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only OpenClaw provider readiness smoke.")
    parser.add_argument("--base-url", default=DEFAULT_WORKER_BASE_URL, help="Worker runtime base URL.")
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--report-only", action="store_true", help="Always exit 0.")
    args = parser.parse_args()

    report = asyncio.run(build_report(base_url=args.base_url, timeout_seconds=args.timeout_seconds))
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_text_report(report)
    if args.report_only:
        return 0
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
