"""Validate a real customer-machine Worker end-to-end browser runtime flow.

This script is intentionally conservative: when the expected real client worker
is not online, it returns SKIPPED (exit code 2) and does not execute browser
actions. It never fabricates a successful client-machine validation.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXIT_PASS = 0
EXIT_FAIL = 1
EXIT_SKIPPED = 2


@dataclass(slots=True)
class CheckResult:
    """One validation check result."""

    name: str
    status: str
    message: str
    data: dict[str, Any] = field(default_factory=dict)


class HTTPClient:
    """Small JSON HTTP client based on stdlib urllib."""

    def __init__(self, *, timeout_seconds: float) -> None:
        self.timeout_seconds = timeout_seconds

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> dict[str, Any]:
        return self._request("GET", url, headers=headers)

    def post(
        self,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return self._request("POST", url, headers=headers, payload=payload)

    def _request(
        self,
        method: str,
        url: str,
        *,
        headers: dict[str, str] | None = None,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            method=method,
            headers={
                "Accept": "application/json",
                **({"Content-Type": "application/json"} if payload is not None else {}),
                **(headers or {}),
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"{method} {url} failed with HTTP {exc.code}: {error_body}") from exc
        except urllib.error.URLError as exc:
            raise RuntimeError(f"{method} {url} failed: {exc.reason}") from exc
        return json.loads(raw) if raw else {}


class RealClientWorkerE2EValidator:
    """Run E2E checks against AI Server and a real client worker."""

    def __init__(
        self,
        *,
        server_url: str,
        workspace_id: str,
        user_id: str,
        expected_worker_name: str | None,
        timeout_seconds: float = 30.0,
        http_client: HTTPClient | None = None,
    ) -> None:
        self.server_url = self._normalize_server_url(server_url)
        self.workspace_id = workspace_id
        self.user_id = user_id
        self.expected_worker_name = expected_worker_name
        self.timeout_seconds = timeout_seconds
        self.http = http_client or HTTPClient(timeout_seconds=timeout_seconds)
        self.checks: list[CheckResult] = []
        self.warnings: list[str] = []
        self.runtime_session_id: str | None = None

    def run(self) -> tuple[int, dict[str, Any]]:
        """Run all checks and return exit code plus JSON-safe payload."""

        started_at = time.perf_counter()
        exit_code = EXIT_FAIL
        summary_message = "Validation failed"
        try:
            self._check_local_config()
            self._check_api_health()
            self._check_openapi_browser_runtime_routes()
            health_summary = self._check_worker_health_summary()
            available_workers = self._check_available_workers()
            worker = self._find_expected_worker(available_workers, health_summary)
            if worker is None:
                self._add_check(
                    "expected_worker_online",
                    "SKIPPED",
                    "real client worker not online",
                    {"expected_worker_name": self.expected_worker_name},
                )
                exit_code = EXIT_SKIPPED
                summary_message = "SKIPPED: real client worker not online"
                return exit_code, self._build_output(exit_code, summary_message, started_at)

            self._add_check(
                "expected_worker_online",
                "PASS",
                "expected worker is online and available",
                {"worker_id": worker.get("id"), "worker_name": worker.get("worker_name")},
            )
            self._create_runtime_session()
            self._navigate_example()
            self._capture_screenshot()
            self._get_page()
            self._close_session()
            self._add_check("summary", "PASS", "real client worker E2E validation completed")
            exit_code = EXIT_PASS
            summary_message = "PASS"
        except Exception as exc:
            self._add_check("fatal_error", "FAIL", str(exc))
            if self.runtime_session_id:
                self._best_effort_close()
            exit_code = EXIT_FAIL
            summary_message = f"FAIL: {exc}"
        return exit_code, self._build_output(exit_code, summary_message, started_at)

    def _check_local_config(self) -> None:
        """Best-effort local server configuration checks."""

        try:
            from app.core.config import Settings

            settings = Settings()
        except Exception as exc:
            self.warnings.append(f"local settings unavailable: {exc}")
            self._add_check("server_config", "WARNING", "local settings unavailable", {"error": str(exc)})
            return

        data = {
            "BROWSER_PROVIDER": settings.browser_provider,
            "BROWSER_WORKER_AUTH_ENABLED": settings.browser_worker_auth_enabled,
            "BROWSER_ALLOWED_DOMAINS": settings.browser_allowed_domains,
            "BROWSER_RUNTIME_SCREENSHOT_DIR": settings.browser_runtime_screenshot_dir,
        }
        if settings.browser_provider != "remote":
            self.warnings.append(
                "BROWSER_PROVIDER is not remote; browser runtime API is testable, but legacy browser action API may still use mock"
            )
        if "example.com" not in settings.browser_allowed_domains:
            self.warnings.append("BROWSER_ALLOWED_DOMAINS does not include example.com")
        screenshot_dir = Path(settings.browser_runtime_screenshot_dir)
        data["screenshot_dir_exists"] = screenshot_dir.exists()
        self._add_check("server_config", "PASS", "local server configuration inspected", data)

    def _check_api_health(self) -> None:
        payload = self.http.get(self._url("/health"))
        self._add_check("api_health", "PASS", "API health reachable", payload)

    def _check_openapi_browser_runtime_routes(self) -> None:
        payload = self.http.get(self._root_url("/openapi.json"))
        paths = payload.get("paths", {})
        required = [
            "/api/v1/browser-runtime/sessions",
            "/api/v1/browser-runtime/sessions/{session_id}/navigate",
            "/api/v1/browser-runtime/sessions/{session_id}/screenshot",
            "/api/v1/browser-runtime/sessions/{session_id}/page",
            "/api/v1/browser-runtime/sessions/{session_id}/close",
        ]
        missing = [path for path in required if path not in paths]
        if missing:
            raise RuntimeError(f"browser runtime routes missing from OpenAPI: {missing}")
        self._add_check("browser_runtime_routes", "PASS", "browser runtime routes exist", {"routes": required})

    def _check_worker_health_summary(self) -> dict[str, Any]:
        payload = self.http.get(self._url("/browser-workers/health/summary"), headers=self._workspace_headers())
        self._add_check("worker_health_summary", "PASS", "worker health summary reachable", payload)
        return payload

    def _check_available_workers(self) -> list[dict[str, Any]]:
        payload = self.http.get(
            self._url("/browser-workers/available?capability=browser_runtime"),
            headers=self._workspace_headers(),
        )
        workers = list(payload.get("items", []))
        self._add_check("available_workers", "PASS", "available workers fetched", {"count": len(workers), "items": workers})
        return workers

    def _find_expected_worker(
        self,
        available_workers: list[dict[str, Any]],
        health_summary: dict[str, Any],
    ) -> dict[str, Any] | None:
        """Find an explicitly named worker or the first available browser-runtime worker."""

        candidates = available_workers
        if self.expected_worker_name:
            candidates = [worker for worker in candidates if worker.get("worker_name") == self.expected_worker_name]
        candidates = [
            worker
            for worker in candidates
            if worker.get("status") == "online"
            and bool((worker.get("capabilities") or {}).get("browser_runtime"))
            and str((worker.get("capabilities") or {}).get("browser", "chromium")).lower() == "chromium"
        ]
        if candidates:
            return candidates[0]
        worker_names = [worker.get("worker_name") for worker in health_summary.get("workers", [])]
        self.warnings.append(f"real client worker not online; seen workers: {worker_names}")
        return None

    def _create_runtime_session(self) -> None:
        payload = self.http.post(
            self._url("/browser-runtime/sessions"),
            headers=self._workspace_headers(),
            payload={"browser": "chromium", "metadata": {"validator": "real_client_worker_e2e"}},
        )
        self.runtime_session_id = str(payload.get("id") or "")
        if not self.runtime_session_id:
            raise RuntimeError("runtime session id missing")
        self._add_check("browser_runtime_create_session", "PASS", "runtime session created", payload)

    def _navigate_example(self) -> None:
        payload = self.http.post(
            self._url(f"/browser-runtime/sessions/{self.runtime_session_id}/navigate"),
            headers=self._workspace_headers(),
            payload={"url": "https://example.com"},
        )
        self._add_check("navigate_example", "PASS", "navigate https://example.com completed", payload)

    def _capture_screenshot(self) -> None:
        payload = self.http.post(
            self._url(f"/browser-runtime/sessions/{self.runtime_session_id}/screenshot"),
            headers=self._workspace_headers(),
            payload={"full_page": True, "screenshot_name": "real-client-worker-e2e-example"},
        )
        screenshot_path = payload.get("screenshot_path") or (payload.get("metadata") or {}).get("last_screenshot_path")
        if not screenshot_path or not str(screenshot_path).endswith(".png"):
            raise RuntimeError("screenshot metadata missing or invalid")
        data = {"screenshot_path": screenshot_path}
        path = Path(str(screenshot_path))
        if path.exists():
            data["screenshot_file_exists"] = True
            data["screenshot_file_size"] = path.stat().st_size
        else:
            data["screenshot_file_exists"] = False
            data["note"] = "path may be inside API container or remote filesystem"
        self._add_check("screenshot", "PASS", "screenshot captured and metadata verified", data)

    def _get_page(self) -> None:
        payload = self.http.get(
            self._url(f"/browser-runtime/sessions/{self.runtime_session_id}/page"),
            headers=self._workspace_headers(),
        )
        title = str(payload.get("title") or "")
        content = str(payload.get("content") or "")
        if "Example Domain" not in title and "Example Domain" not in content:
            raise RuntimeError("example.com page content/title not returned")
        self._add_check(
            "get_page",
            "PASS",
            "page title/content returned",
            {"title": payload.get("title"), "url": payload.get("url")},
        )

    def _close_session(self) -> None:
        payload = self.http.post(
            self._url(f"/browser-runtime/sessions/{self.runtime_session_id}/close"),
            headers=self._workspace_headers(),
        )
        if payload.get("session_status") != "closed":
            raise RuntimeError(f"runtime session close did not return closed status: {payload.get('session_status')}")
        self._add_check("close_session", "PASS", "runtime session closed", payload)

    def _best_effort_close(self) -> None:
        try:
            self.http.post(
                self._url(f"/browser-runtime/sessions/{self.runtime_session_id}/close"),
                headers=self._workspace_headers(),
            )
        except Exception:
            return

    def _workspace_headers(self) -> dict[str, str]:
        return {"X-Workspace-Id": self.workspace_id, "X-User-Id": self.user_id}

    def _url(self, path: str) -> str:
        return f"{self.server_url}{path}"

    def _root_url(self, path: str) -> str:
        parsed = urllib.parse.urlparse(self.server_url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        return f"{root}{path}"

    def _normalize_server_url(self, server_url: str) -> str:
        value = server_url.rstrip("/")
        return value if value.endswith("/api/v1") else f"{value}/api/v1"

    def _add_check(self, name: str, status: str, message: str, data: dict[str, Any] | None = None) -> None:
        self.checks.append(CheckResult(name=name, status=status, message=message, data=data or {}))

    def _build_output(self, exit_code: int, summary_message: str, started_at: float) -> dict[str, Any]:
        statuses = [check.status for check in self.checks]
        status = "PASS"
        if exit_code == EXIT_SKIPPED:
            status = "SKIPPED"
        elif "FAIL" in statuses or exit_code == EXIT_FAIL:
            status = "FAIL"
        return {
            "status": status,
            "exit_code": exit_code,
            "summary": summary_message,
            "server_url": self.server_url,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "expected_worker_name": self.expected_worker_name,
            "warnings": self.warnings,
            "duration_ms": max(0, int((time.perf_counter() - started_at) * 1000)),
            "checks": [asdict(check) for check in self.checks],
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate real client worker browser runtime E2E flow.")
    parser.add_argument("--server-url", default="http://localhost:8000", help="AI Server root or /api/v1 URL.")
    parser.add_argument("--workspace-id", required=True, help="Workspace id sent as X-Workspace-Id.")
    parser.add_argument("--user-id", required=True, help="User id sent as X-User-Id.")
    parser.add_argument("--expected-worker-name", default=None, help="Expected real client worker name.")
    parser.add_argument("--timeout-seconds", type=float, default=30.0, help="HTTP timeout per request.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    validator = RealClientWorkerE2EValidator(
        server_url=args.server_url,
        workspace_id=args.workspace_id,
        user_id=args.user_id,
        expected_worker_name=args.expected_worker_name,
        timeout_seconds=args.timeout_seconds,
    )
    exit_code, output = validator.run()
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
