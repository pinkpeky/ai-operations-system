"""Check that runtime/generated artifacts are not tracked by git."""

from __future__ import annotations

import argparse
import json
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(slots=True)
class HygieneCheck:
    name: str
    status: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        return asdict(self)


FORBIDDEN_EXACT = {
    ".env",
    ".env.generated",
    "worker_state.json",
    "worker_client/worker_state.json",
    "worker_client/worker_config.yaml",
    "release/reports/release_readiness_report.json",
    "release/reports/integration_readiness_report.json",
    "release/reports/integration_readiness_report.md",
    "release/reports/conflict_surface_report.json",
    "release/reports/conflict_surface_report.md",
}

FORBIDDEN_SEGMENTS = {
    "node_modules",
    "runtime_state",
    "logs",
    "__pycache__",
}

FORBIDDEN_PREFIXES = (
    "docs/rendered/",
    "release/build/",
    "storage/browser_screenshots/",
    "storage/browser_runtime_snapshots/",
    "storage/output_artifacts/",
    "storage/output_packages/",
    "storage/output_exports/",
    "worker/screenshots/",
    "worker_client/logs/",
    "worker_client/runtime_state/",
)


def tracked_files(root: Path) -> list[str]:
    proc = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    return [item for item in proc.stdout.decode("utf-8", errors="replace").split("\0") if item]


def is_forbidden(path: str) -> tuple[bool, str]:
    normalized = path.replace("\\", "/")
    if normalized in FORBIDDEN_EXACT:
        return True, "forbidden exact runtime or secret file"
    parts = set(normalized.split("/"))
    if parts & FORBIDDEN_SEGMENTS:
        return True, "forbidden runtime/build directory segment"
    if normalized.startswith(FORBIDDEN_PREFIXES):
        if normalized.endswith(".gitkeep"):
            return False, "allowed placeholder"
        return True, "forbidden generated runtime artifact prefix"
    if normalized.endswith(".env") and not normalized.endswith(".env.example"):
        return True, "committed environment file"
    return False, "ok"


def run_checks(root: Path) -> list[HygieneCheck]:
    checks: list[HygieneCheck] = []
    offenders: list[tuple[str, str]] = []
    for path in tracked_files(root):
        forbidden, reason = is_forbidden(path)
        if forbidden:
            offenders.append((path, reason))

    if offenders:
        for path, reason in offenders:
            checks.append(HygieneCheck("runtime-hygiene", "FAIL", reason, path))
    else:
        checks.append(HygieneCheck("runtime-hygiene", "PASS", "no forbidden runtime artifacts are tracked"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Check runtime artifact hygiene.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    checks = run_checks(root)
    success = not any(check.status == "FAIL" for check in checks)

    if args.json:
        print(json.dumps({"success": success, "checks": [check.to_dict() for check in checks]}, indent=2))
    else:
        for check in checks:
            suffix = f" ({check.path})" if check.path else ""
            print(f"{check.status}: {check.name}: {check.message}{suffix}")
        print("SUMMARY: PASS" if success else "SUMMARY: FAIL")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
