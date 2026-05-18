"""Validate required CI gate names against GitHub Actions workflows."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]


@dataclass(slots=True)
class CiGateCheck:
    name: str
    status: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} did not parse as a YAML mapping")
    return payload


def matrix_values(job: dict[str, Any]) -> dict[str, list[str]]:
    strategy = job.get("strategy")
    if not isinstance(strategy, dict):
        return {}
    matrix = strategy.get("matrix")
    if not isinstance(matrix, dict):
        return {}
    values: dict[str, list[str]] = {}
    for key, value in matrix.items():
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            values[str(key)] = [str(item) for item in value]
    return values


def expand_job_name(template: str, job: dict[str, Any]) -> set[str]:
    matrices = matrix_values(job)
    if not matrices:
        return {template}

    expanded = {template}
    for key, values in matrices.items():
        token = "${{ matrix." + key + " }}"
        if not any(token in name for name in expanded):
            continue
        expanded = {name.replace(token, value) for name in expanded for value in values}
    return expanded


def workflow_job_names(workflow_path: Path) -> set[str]:
    workflow = load_yaml(workflow_path)
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict):
        raise ValueError(f"{workflow_path} has no jobs mapping")

    names: set[str] = set()
    for job_id, raw_job in jobs.items():
        if not isinstance(raw_job, dict):
            continue
        template = str(raw_job.get("name") or job_id)
        names.update(expand_job_name(template, raw_job))
    return names


def run_checks(root: Path) -> list[CiGateCheck]:
    config = load_json(root / ".github/required-checks.json")
    required = config.get("required_status_checks")
    if not isinstance(required, list) or not all(isinstance(item, str) for item in required):
        return [CiGateCheck("required-ci-gates", "FAIL", "required_status_checks must be a string list")]

    discovered = workflow_job_names(root / ".github/workflows/pr-quality-gates.yml")
    missing = sorted(set(required) - discovered)
    extra = sorted(discovered - set(required))

    checks: list[CiGateCheck] = []
    if missing:
        checks.append(CiGateCheck("required-ci-gates", "FAIL", f"missing workflow job names: {', '.join(missing)}"))
    else:
        checks.append(CiGateCheck("required-ci-gates", "PASS", "all required checks match workflow job names"))

    if extra:
        checks.append(CiGateCheck("required-ci-gates-extra", "PASS", f"non-required workflow jobs: {', '.join(extra)}"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate required CI gates against workflow job names.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    checks = run_checks(Path(args.repo_root).resolve())
    success = not any(check.status == "FAIL" for check in checks)

    if args.json:
        print(json.dumps({"success": success, "checks": [check.to_dict() for check in checks]}, indent=2))
    else:
        for check in checks:
            print(f"{check.status}: {check.name}: {check.message}")
        print("SUMMARY: PASS" if success else "SUMMARY: FAIL")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
