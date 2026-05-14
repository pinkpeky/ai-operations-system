"""Tests for the real client worker E2E validator script."""

from __future__ import annotations

from scripts.validate_real_client_worker_e2e import (
    EXIT_SKIPPED,
    RealClientWorkerE2EValidator,
    build_parser,
)


class FakeHTTPClient:
    """Minimal fake HTTP client for validator tests."""

    def __init__(self) -> None:
        self.post_calls: list[tuple[str, dict | None]] = []

    def get(self, url: str, *, headers: dict[str, str] | None = None) -> dict:
        if url.endswith("/health"):
            return {"status": "ok"}
        if url.endswith("/openapi.json"):
            return {
                "paths": {
                    "/api/v1/browser-runtime/sessions": {},
                    "/api/v1/browser-runtime/sessions/{session_id}/navigate": {},
                    "/api/v1/browser-runtime/sessions/{session_id}/screenshot": {},
                    "/api/v1/browser-runtime/sessions/{session_id}/page": {},
                    "/api/v1/browser-runtime/sessions/{session_id}/close": {},
                }
            }
        if "/browser-workers/health/summary" in url:
            return {
                "workspace_id": "demo-workspace",
                "total_workers": 1,
                "online_workers": 1,
                "workers": [
                    {
                        "id": "worker-1",
                        "worker_name": "other-worker",
                        "status": "online",
                        "capabilities": {"browser_runtime": True, "browser": "chromium"},
                    }
                ],
            }
        if "/browser-workers/available" in url:
            return {
                "items": [
                    {
                        "id": "worker-1",
                        "worker_name": "other-worker",
                        "status": "online",
                        "capabilities": {"browser_runtime": True, "browser": "chromium"},
                    }
                ]
            }
        raise AssertionError(f"Unexpected GET {url}")

    def post(self, url: str, *, headers: dict[str, str] | None = None, payload: dict | None = None) -> dict:
        self.post_calls.append((url, payload))
        raise AssertionError("Browser action should not run when expected worker is missing")


def test_parser_accepts_required_arguments() -> None:
    """The script exposes required CLI arguments."""

    args = build_parser().parse_args(
        [
            "--server-url",
            "http://localhost:8000",
            "--workspace-id",
            "demo-workspace",
            "--user-id",
            "demo-user",
            "--expected-worker-name",
            "real-client-worker",
        ]
    )

    assert args.server_url == "http://localhost:8000"
    assert args.workspace_id == "demo-workspace"
    assert args.user_id == "demo-user"
    assert args.expected_worker_name == "real-client-worker"


def test_expected_worker_missing_returns_skipped() -> None:
    """Missing real client worker must return SKIPPED and avoid browser actions."""

    fake_http = FakeHTTPClient()
    validator = RealClientWorkerE2EValidator(
        server_url="http://localhost:8000",
        workspace_id="demo-workspace",
        user_id="demo-user",
        expected_worker_name="real-client-worker",
        http_client=fake_http,  # type: ignore[arg-type]
    )

    exit_code, output = validator.run()

    assert exit_code == EXIT_SKIPPED
    assert output["status"] == "SKIPPED"
    assert "real client worker not online" in output["summary"]
    assert fake_http.post_calls == []
