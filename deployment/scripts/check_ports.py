"""Check deployment profile port occupancy without killing processes."""

from __future__ import annotations

import argparse
import json

try:
    from common import CheckResult, load_ports, port_open, port_process_hint
except ImportError:  # pragma: no cover - package import path for tests.
    from .common import CheckResult, load_ports, port_open, port_process_hint


def check_ports(profile: str, host: str = "127.0.0.1") -> list[CheckResult]:
    results: list[CheckResult] = []
    for item in load_ports(profile):
        port = int(item["port"])
        occupied = port_open(host, port)
        status = "WARNING" if occupied else "PASS"
        message = "port is currently in use" if occupied else "port is available"
        metadata = {
            "port": port,
            "required": bool(item.get("required")),
            "description": item.get("description"),
            "process": port_process_hint(port) if occupied else None,
        }
        results.append(CheckResult(str(item["name"]), status, message, metadata))
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Check ports declared by a deployment profile.")
    parser.add_argument("--profile", required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = check_ports(args.profile, args.host)
    if args.json:
        print(json.dumps({"profile": args.profile, "checks": [item.to_dict() for item in results]}, indent=2))
    else:
        for item in results:
            print(f"{item.status}: {item.name}: {item.message} {item.metadata or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
