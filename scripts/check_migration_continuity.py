"""Validate Alembic migration revision continuity."""

from __future__ import annotations

import argparse
import ast
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclass(slots=True)
class MigrationInfo:
    path: str
    revision: str
    down_revisions: list[str]
    has_downgrade: bool


@dataclass(slots=True)
class MigrationCheck:
    name: str
    status: str
    message: str
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def literal_assignments(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    values: dict[str, Any] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in {"revision", "down_revision"}:
                    values[target.id] = ast.literal_eval(node.value)
        elif isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and target.id in {"revision", "down_revision"} and node.value is not None:
                values[target.id] = ast.literal_eval(node.value)
    values["has_downgrade"] = any(isinstance(node, ast.FunctionDef) and node.name == "downgrade" for node in tree.body)
    return values


def normalize_down_revision(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [item for item in value if isinstance(item, str)]
    return []


def load_migrations(root: Path) -> list[MigrationInfo]:
    versions = root / "alembic" / "versions"
    migrations: list[MigrationInfo] = []
    for path in sorted(versions.glob("*.py")):
        values = literal_assignments(path)
        revision = values.get("revision")
        if not isinstance(revision, str):
            continue
        migrations.append(
            MigrationInfo(
                path=path.relative_to(root).as_posix(),
                revision=revision,
                down_revisions=normalize_down_revision(values.get("down_revision")),
                has_downgrade=bool(values.get("has_downgrade")),
            )
        )
    return migrations


def validate(root: Path) -> list[MigrationCheck]:
    migrations = load_migrations(root)
    checks: list[MigrationCheck] = []
    revisions = [item.revision for item in migrations]
    revision_set = set(revisions)

    duplicates = sorted({revision for revision in revisions if revisions.count(revision) > 1})
    checks.append(
        MigrationCheck(
            "revision-ids-unique",
            "PASS" if not duplicates else "FAIL",
            "revision ids are unique" if not duplicates else "duplicate revision ids found",
            {"duplicates": duplicates},
        )
    )

    missing_down = sorted(
        {
            down
            for item in migrations
            for down in item.down_revisions
            if down not in revision_set
        }
    )
    checks.append(
        MigrationCheck(
            "down-revisions-exist",
            "PASS" if not missing_down else "FAIL",
            "all down revisions exist" if not missing_down else "missing down revision references",
            {"missing": missing_down},
        )
    )

    roots = [item.revision for item in migrations if not item.down_revisions]
    checks.append(
        MigrationCheck(
            "single-root",
            "PASS" if len(roots) == 1 else "FAIL",
            "single migration root" if len(roots) == 1 else "expected exactly one migration root",
            {"roots": roots},
        )
    )

    referenced = {down for item in migrations for down in item.down_revisions}
    heads = sorted(revision_set - referenced)
    checks.append(
        MigrationCheck(
            "single-head",
            "PASS" if len(heads) == 1 else "FAIL",
            "single migration head" if len(heads) == 1 else "expected exactly one migration head",
            {"heads": heads},
        )
    )

    missing_downgrade = [item.path for item in migrations if not item.has_downgrade]
    checks.append(
        MigrationCheck(
            "downgrade-functions",
            "PASS" if not missing_downgrade else "FAIL",
            "all migrations define downgrade" if not missing_downgrade else "migrations missing downgrade",
            {"missing": missing_downgrade},
        )
    )

    checks.append(MigrationCheck("migration-count", "PASS", f"{len(migrations)} migration files parsed"))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Alembic migration continuity.")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    checks = validate(root)
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
