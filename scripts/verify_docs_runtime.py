"""验证 docs 与当前 runtime / OpenAPI 是否一致。"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass(frozen=True, slots=True)
class CheckResult:
    """单项校验结果。"""

    level: str
    message: str


class DocsRuntimeVerifier:
    """Docs Runtime Verification 主类。"""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.docs = root / "docs"
        self.results: list[CheckResult] = []

    def run(self) -> int:
        """执行所有校验并输出结果。"""

        self.check_required_docs()
        self.check_runtime_config()
        self.check_openapi_and_api_docs()
        self.check_project_overview()
        self.check_phase_status()
        self.print_results()
        return 1 if any(result.level == "ERROR" for result in self.results) else 0

    def pass_(self, message: str) -> None:
        self.results.append(CheckResult("PASS", message))

    def warning(self, message: str) -> None:
        self.results.append(CheckResult("WARNING", message))

    def error(self, message: str) -> None:
        self.results.append(CheckResult("ERROR", message))

    def read_text(self, relative_path: str) -> str:
        path = self.root / relative_path
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.error(f"Missing file: {relative_path}")
            return ""

    def check_required_docs(self) -> None:
        """检查 Phase 10.5/11 docs 结构是否存在。"""

        required = [
            "docs/PROJECT_OVERVIEW.md",
            "docs/CURRENT_RUNTIME.md",
            "docs/zh/PROJECT_STATUS.md",
            "docs/zh/ARCHITECTURE.md",
            "docs/zh/API_REFERENCE.md",
            "docs/zh/DEPLOYMENT.md",
            "docs/zh/DEVELOPMENT_GUIDE.md",
            "docs/zh/DOCS_RUNTIME_VERIFICATION.md",
            "docs/en/PROJECT_STATUS.md",
            "docs/en/ARCHITECTURE.md",
            "docs/en/API_REFERENCE.md",
            "docs/en/DEPLOYMENT.md",
            "docs/en/DEVELOPMENT_GUIDE.md",
            "docs/en/DOCS_RUNTIME_VERIFICATION.md",
            "worker_client/main.py",
            "worker_client/config.py",
            "worker_client/registration.py",
            "worker_client/heartbeat.py",
            "worker_client/runtime.py",
            "worker_client/cli.py",
            "worker_client/worker_config.example.yaml",
        ]
        missing = [path for path in required if not (self.root / path).exists()]
        if missing:
            for path in missing:
                self.error(f"Missing required docs file: {path}")
        else:
            self.pass_("Required zh/en docs structure exists")

    def check_runtime_config(self) -> None:
        """检查 CURRENT_RUNTIME 与 Settings / docker-compose 默认值是否一致。"""

        from app.core.config import Settings

        settings = Settings()
        current_runtime = self.read_text("docs/CURRENT_RUNTIME.md")
        compose = self.read_text("docker-compose.yml")
        expected_values = {
            "LLM_PROVIDER": settings.llm_provider,
            "LOCAL_LLM_MODEL": settings.local_llm_model,
            "EMBEDDING_PROVIDER": settings.embedding_provider,
            "LOCAL_EMBEDDING_MODEL": settings.local_embedding_model,
            "RERANKER_PROVIDER": settings.reranker_provider,
            "DEFAULT_SEARCH_MODE": settings.default_search_mode,
            "EMBEDDING_DIMENSION": str(settings.embedding_dimension),
            "MAX_UPLOAD_FILE_SIZE_MB": str(settings.max_upload_file_size_mb),
            "UPLOAD_TEMP_DIR": settings.upload_temp_dir,
            "ALLOWED_FILE_TYPES": settings.allowed_file_types,
            "BROWSER_PROVIDER": settings.browser_provider,
            "BROWSER_TIMEOUT_SECONDS": str(settings.browser_timeout_seconds),
            "BROWSER_HEADLESS": str(settings.browser_headless),
            "BROWSER_TYPE": settings.browser_type,
            "BROWSER_VIEWPORT_WIDTH": str(settings.browser_viewport_width),
            "BROWSER_VIEWPORT_HEIGHT": str(settings.browser_viewport_height),
            "BROWSER_SCREENSHOT_DIR": settings.browser_screenshot_dir,
            "BROWSER_PROFILE_ROOT": settings.browser_profile_root,
            "BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS": str(settings.browser_profile_lock_timeout_seconds),
            "BROWSER_PROFILE_BACKUP_ENABLED": str(settings.browser_profile_backup_enabled),
            "BROWSER_PROFILE_MAX_BACKUPS": str(settings.browser_profile_max_backups),
            "BROWSER_PROFILE_UNUSED_DAYS": str(settings.browser_profile_unused_days),
            "BROWSER_PROFILE_BACKUP_ROOT": settings.browser_profile_backup_root,
            "BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS": str(settings.browser_human_control_timeout_seconds),
            "BROWSER_UI_ACCESS_TIMEOUT_SECONDS": str(settings.browser_ui_access_timeout_seconds),
            "BROWSER_WORKER_AUTH_ENABLED": str(settings.browser_worker_auth_enabled),
            "BROWSER_WORKER_AUTH_STRICT": str(settings.browser_worker_auth_strict),
            "BROWSER_ALLOWED_DOMAINS": settings.browser_allowed_domains,
            "BROWSER_BLOCKED_DOMAINS": settings.browser_blocked_domains,
            "BROWSER_ALLOW_EXTERNAL_DOMAINS": str(settings.browser_allow_external_domains),
            "BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS": str(settings.browser_worker_default_timeout_seconds),
            "BROWSER_WORKER_RETRY_COUNT": str(settings.browser_worker_retry_count),
            "BROWSER_WORKER_DEFAULT_URL": settings.browser_worker_default_url,
            "BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS": str(settings.browser_worker_heartbeat_timeout_seconds),
            "BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS": str(
                settings.browser_worker_health_check_interval_seconds
            ),
            "BROWSER_SESSION_TIMEOUT_SECONDS": str(settings.browser_session_timeout_seconds),
            "BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS": str(settings.browser_session_cleanup_interval_seconds),
            "BROWSER_ACTION_TIMEOUT_SECONDS": str(settings.browser_action_timeout_seconds),
            "BROWSER_ACTION_RETRY_COUNT": str(settings.browser_action_retry_count),
            "BROWSER_ACTION_RETRY_BACKOFF_SECONDS": str(settings.browser_action_retry_backoff_seconds),
            "SCREENSHOT_RETENTION_DAYS": str(settings.screenshot_retention_days),
        }
        for key, value in expected_values.items():
            if key not in current_runtime or str(value) not in current_runtime:
                self.error(f"CURRENT_RUNTIME.md does not document {key}={value}")
            else:
                self.pass_(f"CURRENT_RUNTIME documents {key}={value}")
            if key not in compose:
                self.error(f"docker-compose.yml does not expose {key}")
        if "MAX_UPLOAD_FILE_SIZE_MB" in compose and "ALLOWED_FILE_TYPES" in compose:
            self.pass_("docker-compose.yml exposes upload runtime settings")

    def check_openapi_and_api_docs(self) -> None:
        """检查真实 OpenAPI 路径是否已写入 API_REFERENCE。"""

        from app.main import create_app

        app = create_app()
        openapi = app.openapi()
        paths = set(openapi.get("paths", {}).keys())
        zh_api = self.read_text("docs/zh/API_REFERENCE.md")
        en_api = self.read_text("docs/en/API_REFERENCE.md")
        required_paths = [
            "/api/v1/health",
            "/api/v1/llm/health",
            "/api/v1/llm/test",
            "/api/v1/rag/embedding/health",
            "/api/v1/rag/ingest",
            "/api/v1/rag/search",
            "/api/v1/rag/debug",
            "/api/v1/files/upload",
            "/api/v1/reranker/health",
            "/api/v1/agentic-rag/query",
            "/api/v1/tasks",
            "/api/v1/tasks/{task_id}/cancel",
            "/api/v1/tasks/{task_id}/retry",
            "/api/v1/tasks/{task_id}/events",
            "/api/v1/tasks/{task_id}/logs",
            "/api/v1/observability/summary",
            "/api/v1/tools",
            "/api/v1/tools/{tool_name}",
            "/api/v1/tools/{tool_name}/execute",
            "/api/v1/tool-calls",
            "/api/v1/memory/sessions",
            "/api/v1/memory/sessions/{session_id}",
            "/api/v1/memory/messages",
            "/api/v1/memory/messages/{session_id}",
            "/api/v1/memory/memories",
            "/api/v1/memory/memories/{memory_id}",
            "/api/v1/agents/registry",
            "/api/v1/multi-agent/runs",
            "/api/v1/multi-agent/runs/{run_id}",
            "/api/v1/multi-agent/runs/{run_id}/execute-chain",
            "/api/v1/multi-agent/runs/{run_id}/messages",
            "/api/v1/multi-agent/runs/{run_id}/handoffs",
            "/api/v1/plans",
            "/api/v1/plans/{plan_id}",
            "/api/v1/plans/{plan_id}/execute",
            "/api/v1/plans/{plan_id}/cancel",
            "/api/v1/plans/{plan_id}/steps",
            "/api/v1/plans/{plan_id}/reviews",
            "/api/v1/browser/sessions",
            "/api/v1/browser/sessions/{session_id}/close",
            "/api/v1/browser/profiles",
            "/api/v1/browser/profiles/recover-stale-locks",
            "/api/v1/browser/profiles/cleanup",
            "/api/v1/browser/profiles/health/summary",
            "/api/v1/browser/profiles/{profile_id}",
            "/api/v1/browser/profiles/{profile_id}/health-check",
            "/api/v1/browser/profiles/{profile_id}/backup",
            "/api/v1/browser/profiles/{profile_id}/backups",
            "/api/v1/browser/profiles/{profile_id}/restore",
            "/api/v1/browser/profiles/{profile_id}/usage-logs",
            "/api/v1/browser/profiles/{profile_id}/lock",
            "/api/v1/browser/profiles/{profile_id}/release",
            "/api/v1/browser/human-control/request",
            "/api/v1/browser/human-control",
            "/api/v1/browser/human-control/{control_session_id}",
            "/api/v1/browser/human-control/{control_session_id}/approve",
            "/api/v1/browser/human-control/{control_session_id}/start",
            "/api/v1/browser/human-control/{control_session_id}/complete",
            "/api/v1/browser/human-control/{control_session_id}/cancel",
            "/api/v1/browser/human-control/{control_session_id}/events",
            "/api/v1/browser/ui-access",
            "/api/v1/browser/ui-access/expire",
            "/api/v1/browser/ui-access/{access_session_id}",
            "/api/v1/browser/ui-access/{access_session_id}/revoke",
            "/api/v1/browser/ui-access/{access_session_id}/validate",
            "/api/v1/browser/security/audit-logs",
            "/api/v1/browser/security/policy/check",
            "/api/v1/browser/actions",
            "/api/v1/browser/actions/{session_id}",
            "/api/v1/browser/screenshot/{session_id}/{filename}",
            "/api/v1/browser/logs/{session_id}",
            "/api/v1/browser-workers/register",
            "/api/v1/browser-workers/{worker_id}/heartbeat",
            "/api/v1/browser-workers/{worker_id}/rotate-secret",
            "/api/v1/browser-workers/{worker_id}/revoke",
            "/api/v1/browser-workers",
            "/api/v1/browser-workers/health/summary",
            "/api/v1/browser-workers/available",
            "/api/v1/browser-workers/{worker_id}/mark-offline",
            "/api/v1/browser-workers/cleanup-sessions",
            "/api/v1/browser-workers/{worker_id}/sessions",
            "/api/v1/browser-worker-runtime/health",
            "/api/v1/browser-worker-runtime/sessions",
            "/api/v1/browser-worker-runtime/actions",
            "/api/v1/browser-worker-runtime/sessions/{session_id}/close",
            "/api/v1/browser-worker-runtime/human-control/start",
            "/api/v1/browser-worker-runtime/human-control/complete",
            "/api/v1/browser-worker-runtime/human-control/status/{session_id}",
            "/api/v1/browser-worker-runtime/ui-access/capabilities",
            "/api/v1/browser/screenshots/cleanup",
            "/api/v1/documents",
            "/api/v1/rag/eval/runs",
        ]
        for path in required_paths:
            if path not in paths:
                self.error(f"OpenAPI path missing: {path}")
                continue
            self.pass_(f"OpenAPI contains {path}")
            if path not in zh_api:
                self.error(f"zh/API_REFERENCE.md does not document {path}")
            if path not in en_api:
                self.error(f"en/API_REFERENCE.md does not document {path}")
        for field in (
            "search_mode",
            "dense_top_k",
            "keyword_top_k",
            "final_top_k",
            "duplicate_strategy",
            "task_events",
            "task_logs",
            "duration_ms",
            "tool_call_logs",
            "tool_name",
            "tool_input",
            "tool_output",
            "conversation_sessions",
            "conversation_messages",
            "agent_memories",
            "memory_trace",
            "recent_messages_count",
            "retrieved_memories_count",
            "agent_runs",
            "agent_messages",
            "agent_handoffs",
            "AgentRegistry",
            "agents_involved",
            "handoff_trace",
            "plans",
            "plan_steps",
            "plan_reviews",
            "PlanStep",
            "PlanReview",
            "SimplePlannerAgent",
            "browser_sessions",
            "browser_actions",
            "browser_action_logs",
            "browser_tool",
            "BrowserProvider",
            "MockBrowserProvider",
            "PlaywrightBrowserProvider",
            "PlaywrightLocalProvider",
            "playwright_local",
            "BROWSER_PROVIDER",
            "BROWSER_TIMEOUT_SECONDS",
            "BROWSER_SCREENSHOT_DIR",
            "browser_id",
            "page_id",
            "provider_session_metadata",
            "selector",
            "target_url",
            "screenshot_path",
            "page_title",
            "get_page_content",
            "RemoteBrowserProvider",
            "BrowserWorkerClient",
            "browser_workers",
            "browser_worker_sessions",
            "browser_worker_actions",
            "remote_session_id",
            "remote_action_id",
            "BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS",
            "BROWSER_WORKER_RETRY_COUNT",
            "BROWSER_WORKER_DEFAULT_URL",
            "Real Browser Worker Service",
            "browser-worker",
            "worker/main.py",
            "worker/browser_worker/playwright_runtime.py",
            "http://browser-worker:9100",
            "WORKER_TIMEOUT_SECONDS",
            "WORKER_SCREENSHOT_DIR",
            "BrowserWorkerHealthService",
            "BrowserWorkerSelector",
            "BrowserSessionCleanupService",
            "ScreenshotCleanupService",
            "max_sessions",
            "active_sessions",
            "max_actions_per_minute",
            "current_load",
            "priority",
            "error_message",
            "last_seen",
            "retry_count",
            "max_retries",
            "BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS",
            "BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS",
            "BROWSER_SESSION_TIMEOUT_SECONDS",
            "BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS",
            "BROWSER_ACTION_TIMEOUT_SECONDS",
            "BROWSER_ACTION_RETRY_COUNT",
            "BROWSER_ACTION_RETRY_BACKOFF_SECONDS",
            "SCREENSHOT_RETENTION_DAYS",
            "BrowserProfileService",
            "browser_profiles",
            "profile_id",
            "profile_path",
            "persistent_context_enabled",
            "locked_by_session_id",
            "locked_at",
            "last_used_at",
            "launch_persistent_context",
            "BROWSER_PROFILE_ROOT",
            "BrowserProfileHealthService",
            "BrowserProfileBackupService",
            "BrowserProfileCleanupService",
            "browser_profile_usage_logs",
            "health_status",
            "last_health_check_at",
            "last_error",
            "usage_count",
            "corrupted_at",
            "backup_path",
            "last_backup_at",
            "recover-stale-locks",
            "health/summary",
            "BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS",
            "BROWSER_PROFILE_BACKUP_ENABLED",
            "BROWSER_PROFILE_MAX_BACKUPS",
            "BROWSER_PROFILE_UNUSED_DAYS",
            "BROWSER_PROFILE_BACKUP_ROOT",
            "BrowserHumanControlService",
            "browser_human_control_sessions",
            "browser_human_control_events",
            "human_control_status",
            "human_control_session_id",
            "paused_at",
            "resumed_at",
            "request_human_control",
            "complete_human_control",
            "BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS",
            "BrowserUIAccessService",
            "browser_ui_access_sessions",
            "access_token_hash",
            "scopes",
            "one_time",
            "used_at",
            "revoked_reason",
            "client_ip",
            "user_agent",
            "remote_control_url",
            "live_view_url",
            "devtools_url",
            "create_ui_access",
            "revoke_ui_access",
            "BROWSER_UI_ACCESS_TIMEOUT_SECONDS",
            "BrowserWorkerAuthService",
            "BrowserActionPolicyService",
            "BrowserSecurityAuditLog",
            "browser_security_audit_logs",
            "worker_secret_hash",
            "api_key_hash",
            "last_auth_at",
            "auth_status",
            "allowed_actions",
            "allowed_domains",
            "worker_secret",
            "X-Worker-Signature",
            "X-Worker-Timestamp",
            "X-Worker-Nonce",
            "BROWSER_WORKER_AUTH_ENABLED",
            "BROWSER_WORKER_AUTH_STRICT",
            "BROWSER_ALLOWED_DOMAINS",
            "BROWSER_BLOCKED_DOMAINS",
            "BROWSER_ALLOW_EXTERNAL_DOMAINS",
            "worker_client",
            "worker_config.example.yaml",
            "worker_config.yaml",
            "worker_state.json",
            "python -m worker_client.cli register",
            "python -m worker_client.cli heartbeat",
            "python -m worker_client.cli serve",
            "python -m worker_client.cli start",
            "Customer Machine Worker Bootstrap",
            "registration flow",
            "heartbeat flow",
            "local worker runtime",
            "UI Access Placeholder",
            "WORKER_PROFILE_DIR",
        ):
            if field not in zh_api or field not in en_api:
                self.error(f"API_REFERENCE missing field: {field}")
            else:
                self.pass_(f"API_REFERENCE documents {field}")

    def check_project_overview(self) -> None:
        """检查项目入口文档是否记录关键架构。"""

        overview = self.read_text("docs/PROJECT_OVERVIEW.md")
        required_terms = [
            "Phase 11",
            "File Upload Pipeline",
            "Docs Runtime Verification",
            "PDF",
            "DOCX",
            "TXT",
            "MD",
            "CSV",
            "Dense + Keyword",
            "Reranker",
            "Phase 12",
            "Task Reliability",
            "task_events",
            "task_logs",
            "cancelled",
            "timeout",
            "Phase 13",
            "Tool Calling",
            "ToolRegistry",
            "builtin tools",
            "tool_call_logs",
            "Phase 14",
            "Memory Foundation",
            "conversation_sessions",
            "conversation_messages",
            "agent_memories",
            "memory_trace",
            "Phase 15",
            "Multi-Agent Foundation",
            "AgentRegistry",
            "agent_runs",
            "agent_messages",
            "agent_handoffs",
            "content_planner",
            "rag_agent",
            "ToolAgent",
            "fixed Agent Chain",
            "Phase 16",
            "Agent Planning Foundation",
            "SimplePlannerAgent",
            "plans",
            "plan_steps",
            "plan_reviews",
            "Plan Execution Flow",
            "Phase 17",
            "Browser Automation Adapter Foundation",
            "BrowserProvider",
            "MockBrowserProvider",
            "PlaywrightBrowserProvider",
            "browser_sessions",
            "browser_actions",
            "browser_action_logs",
            "browser_tool",
            "Phase 18",
            "Playwright Local Provider Integration",
            "PlaywrightLocalProvider",
            "playwright_local",
            "Screenshot System",
            "screenshot_path",
            "get_page_content",
            "Phase 19",
            "Remote Browser Worker Foundation",
            "RemoteBrowserProvider",
            "BrowserWorkerClient",
            "browser_workers",
            "browser_worker_sessions",
            "browser_worker_actions",
            "Worker Registration",
            "Worker Heartbeat",
            "Worker Runtime Mock",
            "Phase 20",
            "Real Browser Worker Service",
            "browser-worker",
            "worker/main.py",
            "worker/browser_worker/playwright_runtime.py",
            "API Server -> Worker",
            "http://browser-worker:9100",
            "Playwright Chromium",
            "worker/screenshots",
            "Phase 21",
            "Browser Worker Reliability",
            "BrowserWorkerHealthService",
            "BrowserWorkerSelector",
            "BrowserSessionCleanupService",
            "ScreenshotCleanupService",
            "max_sessions",
            "active_sessions",
            "least loaded worker",
            "stale worker",
            "action retry",
            "screenshot cleanup",
            "Phase 22",
            "Persistent Browser Profile Foundation",
            "BrowserProfileService",
            "browser_profiles",
            "profile_id",
            "profile_path",
            "persistent_context_enabled",
            "launch_persistent_context",
            "worker/profiles",
            "Profile Lock",
            "Profile Release",
            "Phase 23",
            "Browser Profile Health & Recovery",
            "BrowserProfileHealthService",
            "BrowserProfileBackupService",
            "BrowserProfileCleanupService",
            "browser_profile_usage_logs",
            "health_status",
            "usage_count",
            "profile backup",
            "stale lock recovery",
            "Phase 24",
            "Human-in-the-loop Browser Control",
            "BrowserHumanControlService",
            "browser_human_control_sessions",
            "browser_human_control_events",
            "session paused",
            "session resumed",
            "request_human_control",
            "complete_human_control",
            "Phase 25",
            "Browser Worker UI Access Placeholder",
            "BrowserUIAccessService",
            "browser_ui_access_sessions",
            "access token hash",
            "placeholder URL",
            "create_ui_access",
            "revoke_ui_access",
            "Phase 26",
            "Browser Worker Security & Access Control",
            "BrowserWorkerAuthService",
            "BrowserActionPolicyService",
            "browser_security_audit_logs",
            "worker_secret_hash",
            "signed worker request",
            "UI Access Scope",
            "Browser Action Policy",
            "Phase 27",
            "Customer Machine Worker Bootstrap",
            "worker_client",
            "worker_config.example.yaml",
            "worker_config.yaml",
            "worker_state.json",
            "python -m worker_client.cli register",
            "python -m worker_client.cli heartbeat",
            "python -m worker_client.cli serve",
            "python -m worker_client.cli start",
            "customer machine",
            "registration flow",
            "heartbeat flow",
            "local worker runtime",
        ]
        for term in required_terms:
            if term not in overview:
                self.error(f"PROJECT_OVERVIEW.md missing term: {term}")
            else:
                self.pass_(f"PROJECT_OVERVIEW documents {term}")

    def check_phase_status(self) -> None:
        """检查中英文状态文档是否声明最新 Phase。"""

        zh_status = self.read_text("docs/zh/PROJECT_STATUS.md")
        en_status = self.read_text("docs/en/PROJECT_STATUS.md")
        for name, text in (("zh", zh_status), ("en", en_status)):
            if not re.search(r"Phase\s+27", text):
                self.error(f"{name}/PROJECT_STATUS.md missing Phase 27")
            elif "Customer Machine Worker Bootstrap" not in text or "worker_client" not in text:
                self.error(f"{name}/PROJECT_STATUS.md does not describe Phase 27 scope")
            else:
                self.pass_(f"{name}/PROJECT_STATUS documents Phase 27")

    def print_results(self) -> None:
        """输出 PASS / WARNING / ERROR。"""

        for result in self.results:
            print(f"{result.level}: {result.message}")
        errors = sum(1 for result in self.results if result.level == "ERROR")
        warnings = sum(1 for result in self.results if result.level == "WARNING")
        if errors:
            print(f"SUMMARY: ERROR ({errors} errors, {warnings} warnings)")
        elif warnings:
            print(f"SUMMARY: WARNING ({warnings} warnings)")
        else:
            print("SUMMARY: PASS")


def main(argv: Iterable[str] | None = None) -> int:
    """命令行入口。"""

    _ = list(argv or [])
    return DocsRuntimeVerifier(ROOT).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
