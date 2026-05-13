"""当前运行配置内置工具。"""

from pathlib import Path

from pydantic import BaseModel, Field

from app.tools.base import BaseTool, ToolExecutionContext


class CurrentRuntimeToolInput(BaseModel):
    """当前运行配置工具输入。"""

    include_document: bool = Field(default=True, description="是否尝试读取 docs/CURRENT_RUNTIME.md")


class CurrentRuntimeToolOutput(BaseModel):
    """当前运行配置工具输出。"""

    runtime: dict[str, str | int | float | bool]
    docs_available: bool
    current_runtime_path: str | None = None
    current_runtime_excerpt: str | None = None


class CurrentRuntimeTool(BaseTool):
    """读取当前运行配置和 CURRENT_RUNTIME 文档摘要的工具。"""

    name = "current_runtime_tool"
    description = "Read current runtime provider/search/upload settings and CURRENT_RUNTIME.md when available."
    input_schema = CurrentRuntimeToolInput
    output_schema = CurrentRuntimeToolOutput
    permission_scopes = ["runtime:read"]

    async def execute(self, tool_input: BaseModel, context: ToolExecutionContext) -> BaseModel:
        """返回当前 runtime 信息。"""

        request = CurrentRuntimeToolInput.model_validate(tool_input.model_dump())
        settings = context.effective_settings
        runtime: dict[str, str | int | float | bool] = {
            "LLM_PROVIDER": settings.llm_provider,
            "LOCAL_LLM_MODEL": settings.local_llm_model,
            "EMBEDDING_PROVIDER": settings.embedding_provider,
            "LOCAL_EMBEDDING_MODEL": settings.local_embedding_model,
            "EMBEDDING_DIMENSION": settings.embedding_dimension,
            "RERANKER_PROVIDER": settings.reranker_provider,
            "LOCAL_RERANKER_MODEL": settings.local_reranker_model,
            "DEFAULT_SEARCH_MODE": settings.default_search_mode,
            "DENSE_TOP_K": settings.dense_top_k,
            "KEYWORD_TOP_K": settings.keyword_top_k,
            "FINAL_TOP_K": settings.final_top_k,
            "MAX_UPLOAD_FILE_SIZE_MB": settings.max_upload_file_size_mb,
            "ALLOWED_FILE_TYPES": settings.allowed_file_types,
            "BROWSER_PROVIDER": settings.browser_provider,
            "BROWSER_TIMEOUT_SECONDS": settings.browser_timeout_seconds,
            "BROWSER_HEADLESS": settings.browser_headless,
            "BROWSER_TYPE": settings.browser_type,
            "BROWSER_VIEWPORT_WIDTH": settings.browser_viewport_width,
            "BROWSER_VIEWPORT_HEIGHT": settings.browser_viewport_height,
            "BROWSER_SCREENSHOT_DIR": settings.browser_screenshot_dir,
            "BROWSER_PROFILE_ROOT": settings.browser_profile_root,
            "BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS": settings.browser_profile_lock_timeout_seconds,
            "BROWSER_PROFILE_BACKUP_ENABLED": settings.browser_profile_backup_enabled,
            "BROWSER_PROFILE_MAX_BACKUPS": settings.browser_profile_max_backups,
            "BROWSER_PROFILE_UNUSED_DAYS": settings.browser_profile_unused_days,
            "BROWSER_PROFILE_BACKUP_ROOT": settings.browser_profile_backup_root,
            "BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS": settings.browser_human_control_timeout_seconds,
            "BROWSER_UI_ACCESS_TIMEOUT_SECONDS": settings.browser_ui_access_timeout_seconds,
            "BROWSER_WORKER_AUTH_ENABLED": settings.browser_worker_auth_enabled,
            "BROWSER_WORKER_AUTH_STRICT": settings.browser_worker_auth_strict,
            "BROWSER_ALLOWED_DOMAINS": settings.browser_allowed_domains,
            "BROWSER_BLOCKED_DOMAINS": settings.browser_blocked_domains,
            "BROWSER_ALLOW_EXTERNAL_DOMAINS": settings.browser_allow_external_domains,
            "BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS": settings.browser_worker_default_timeout_seconds,
            "BROWSER_WORKER_RETRY_COUNT": settings.browser_worker_retry_count,
            "BROWSER_WORKER_DEFAULT_URL": settings.browser_worker_default_url,
            "BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS": settings.browser_worker_heartbeat_timeout_seconds,
            "BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS": settings.browser_worker_health_check_interval_seconds,
            "BROWSER_SESSION_TIMEOUT_SECONDS": settings.browser_session_timeout_seconds,
            "BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS": settings.browser_session_cleanup_interval_seconds,
            "BROWSER_ACTION_TIMEOUT_SECONDS": settings.browser_action_timeout_seconds,
            "BROWSER_ACTION_RETRY_COUNT": settings.browser_action_retry_count,
            "BROWSER_ACTION_RETRY_BACKOFF_SECONDS": settings.browser_action_retry_backoff_seconds,
            "SCREENSHOT_RETENTION_DAYS": settings.screenshot_retention_days,
        }
        current_runtime_path = Path(__file__).resolve().parents[3] / "docs" / "CURRENT_RUNTIME.md"
        excerpt: str | None = None
        docs_available = current_runtime_path.exists()
        if request.include_document and docs_available:
            # 只返回前 2000 字，避免工具输出过大影响 Agent prompt。
            excerpt = current_runtime_path.read_text(encoding="utf-8")[:2000]
        return CurrentRuntimeToolOutput(
            runtime=runtime,
            docs_available=docs_available,
            current_runtime_path=str(current_runtime_path) if docs_available else None,
            current_runtime_excerpt=excerpt,
        )
