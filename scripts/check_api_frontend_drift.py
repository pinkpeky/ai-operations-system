"""Check OpenAPI and frontend API client drift for Phase 43-53 readiness routes."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass(slots=True)
class DriftCheck:
    name: str
    status: str
    message: str
    metadata: dict[str, object] | None = None

    def to_dict(self) -> dict[str, object | None]:
        return asdict(self)


KEY_OPENAPI_ROUTES = [
    "/api/v1/task-runs",
    "/api/v1/task-scheduler/health",
    "/api/v1/output-artifacts",
    "/api/v1/workflow-runs",
    "/api/v1/workflow-templates",
    "/api/v1/workflow-template-marketplace",
    "/api/v1/workflow-replay-sessions",
    "/api/v1/conversation-playbooks",
]

CLIENT_EXPECTATIONS = {
    "admin-dashboard": {
        "files": ["admin_dashboard/src/api/client.ts", "admin_dashboard/src/api/outputArtifactClient.ts", "admin_dashboard/src/api/workflowClient.ts", "admin_dashboard/src/api/workflowTemplateClient.ts", "admin_dashboard/src/api/conversationClient.ts"],
        "terms": ["/task-runs", "/task-scheduler/health", "/output-artifacts", "/workflow-runs", "/workflow-templates", "/workflow-template-marketplace", "/workflow-replay-sessions", "/conversation-playbooks"],
    },
    "worker-console": {
        "files": ["worker_console/src/api/taskRunClient.ts", "worker_console/src/api/outputArtifactClient.ts", "worker_console/src/api/workflowClient.ts", "worker_console/src/api/workflowTemplateClient.ts", "worker_console/src/api/conversationClient.ts"],
        "terms": ["/task-runs", "/output-artifacts", "/workflow-runs", "/workflow-templates", "/workflow-template-marketplace", "/conversation-playbooks"],
    },
    "desktop-console": {
        "files": ["worker_console_desktop/src/api/localWorkerClient.ts", "worker_console_desktop/src/api/taskRunClient.ts", "worker_console_desktop/src/api/outputArtifactClient.ts", "worker_console_desktop/src/api/workflowClient.ts", "worker_console_desktop/src/api/workflowTemplateClient.ts"],
        "terms": ["/local/status", "/local/runtime/start", "/local/logs", "/task-runs", "/output-artifacts", "/workflow-runs", "/workflow-templates"],
    },
}


def load_openapi_paths() -> set[str]:
    from app.main import app

    return set(app.openapi().get("paths", {}).keys())


def check_openapi() -> DriftCheck:
    paths = load_openapi_paths()
    missing = [route for route in KEY_OPENAPI_ROUTES if route not in paths]
    return DriftCheck(
        "openapi-key-routes",
        "PASS" if not missing else "FAIL",
        "OpenAPI contains Phase 43-53 readiness routes" if not missing else "OpenAPI missing key readiness routes",
        {"missing": missing},
    )


def check_api_reference_docs() -> DriftCheck:
    docs_text = "\n".join(
        [
            (ROOT / "docs/en/API_REFERENCE.md").read_text(encoding="utf-8"),
            (ROOT / "docs/zh/API_REFERENCE.md").read_text(encoding="utf-8"),
        ]
    )
    missing = [route for route in KEY_OPENAPI_ROUTES if route not in docs_text]
    return DriftCheck(
        "api-reference-key-routes",
        "PASS" if not missing else "WARNING",
        "API reference documents key readiness routes" if not missing else "API reference is missing optional readiness routes",
        {"missing": missing},
    )


def check_client(name: str, files: list[str], terms: list[str]) -> DriftCheck:
    text = "\n".join((ROOT / path).read_text(encoding="utf-8") for path in files)
    missing = [term for term in terms if term not in text]
    return DriftCheck(
        f"{name}-api-client",
        "PASS" if not missing else "WARNING",
        f"{name} references expected readiness routes" if not missing else f"{name} is missing optional route references",
        {"missing": missing, "files": files},
    )


def run_checks() -> list[DriftCheck]:
    checks = [check_openapi(), check_api_reference_docs()]
    for name, expectation in CLIENT_EXPECTATIONS.items():
        checks.append(check_client(name, list(expectation["files"]), list(expectation["terms"])))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser(description="Check API/frontend drift for integration readiness.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    checks = run_checks()
    success = not any(check.status == "FAIL" for check in checks)
    if args.strict and any(check.status == "WARNING" for check in checks):
        success = False
    payload = {"success": success, "checks": [check.to_dict() for check in checks]}
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        for check in checks:
            print(f"{check.status}: {check.name}: {check.message}")
        print("SUMMARY: PASS" if success else "SUMMARY: FAIL")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
