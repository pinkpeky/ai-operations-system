"""应用配置模块。

该模块从环境变量或 .env 文件读取配置，并生成 PostgreSQL、Redis、Qdrant 的连接地址。
"""

import logging
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    # 允许本地开发通过 .env 覆盖默认值，同时忽略暂未使用的扩展配置。
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="AI Operations System", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    cors_allowed_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174,http://localhost:5180,http://127.0.0.1:5180,tauri://localhost",
        alias="CORS_ALLOWED_ORIGINS",
    )

    postgres_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, alias="POSTGRES_PORT")
    postgres_db: str = Field(default="aiops", alias="POSTGRES_DB")
    postgres_user: str = Field(default="aiops", alias="POSTGRES_USER")
    postgres_password: str = Field(default="change_me", alias="POSTGRES_PASSWORD")
    postgres_pool_size: int = Field(default=5, alias="POSTGRES_POOL_SIZE")
    postgres_max_overflow: int = Field(default=10, alias="POSTGRES_MAX_OVERFLOW")

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: str = Field(default="change_me", alias="REDIS_PASSWORD")
    redis_queue_name: str = Field(default="aiops:tasks", alias="REDIS_QUEUE_NAME")

    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_http_port: int = Field(default=6333, alias="QDRANT_HTTP_PORT")
    qdrant_grpc_port: int = Field(default=6334, alias="QDRANT_GRPC_PORT")
    qdrant_api_key: str = Field(default="change_me", alias="QDRANT_API_KEY")

    scheduler_enabled: bool = Field(default=True, alias="SCHEDULER_ENABLED")
    scheduler_interval_seconds: float = Field(default=5.0, alias="SCHEDULER_INTERVAL_SECONDS")
    scheduler_batch_size: int = Field(default=20, alias="SCHEDULER_BATCH_SIZE")
    scheduler_running_timeout_seconds: int = Field(
        default=300,
        alias="SCHEDULER_RUNNING_TIMEOUT_SECONDS",
    )
    task_executor_enabled: bool = Field(default=True, alias="TASK_EXECUTOR_ENABLED")
    task_executor_dequeue_timeout_seconds: int = Field(default=5, alias="TASK_EXECUTOR_DEQUEUE_TIMEOUT_SECONDS")
    task_orchestrator_enabled: bool = Field(default=True, alias="TASK_ORCHESTRATOR_ENABLED")
    task_orchestrator_poll_interval_seconds: float = Field(
        default=2.0,
        ge=0.2,
        le=60.0,
        alias="TASK_ORCHESTRATOR_POLL_INTERVAL_SECONDS",
    )
    task_orchestrator_batch_size: int = Field(default=5, ge=1, le=100, alias="TASK_ORCHESTRATOR_BATCH_SIZE")
    task_run_default_max_retries: int = Field(default=3, ge=0, le=20, alias="TASK_RUN_DEFAULT_MAX_RETRIES")
    task_scheduler_name: str = Field(default="api-in-process-task-scheduler", alias="TASK_SCHEDULER_NAME")
    task_lease_seconds: int = Field(default=120, ge=10, le=3600, alias="TASK_LEASE_SECONDS")
    task_stuck_timeout_seconds: int = Field(default=300, ge=30, le=86400, alias="TASK_STUCK_TIMEOUT_SECONDS")
    task_scheduler_recovery_interval_seconds: float = Field(
        default=10.0,
        ge=1.0,
        le=3600.0,
        alias="TASK_SCHEDULER_RECOVERY_INTERVAL_SECONDS",
    )
    llm_provider: str = Field(default="mock", alias="LLM_PROVIDER")
    local_llm_base_url: str = Field(
        default="http://host.docker.internal:11434",
        alias="LOCAL_LLM_BASE_URL",
    )
    local_llm_model: str = Field(default="mistral", alias="LOCAL_LLM_MODEL")
    server_llm_base_url: str = Field(
        default="http://host.docker.internal:8001/v1",
        alias="SERVER_LLM_BASE_URL",
    )
    server_llm_model: str = Field(default="llama-70b", alias="SERVER_LLM_MODEL")
    llm_timeout_seconds: float = Field(default=120.0, alias="LLM_TIMEOUT_SECONDS")
    embedding_provider: str = Field(default="mock", alias="EMBEDDING_PROVIDER")
    embedding_dimension: int = Field(default=384, ge=1, alias="EMBEDDING_DIMENSION")
    local_embedding_base_url: str = Field(
        default="http://host.docker.internal:11434",
        alias="LOCAL_EMBEDDING_BASE_URL",
    )
    local_embedding_model: str = Field(default="bge-m3", alias="LOCAL_EMBEDDING_MODEL")
    qdrant_collection_name: str = Field(default="ai_knowledge_base", alias="QDRANT_COLLECTION_NAME")
    reranker_provider: str = Field(default="mock", alias="RERANKER_PROVIDER")
    local_reranker_base_url: str = Field(
        default="http://host.docker.internal:11434",
        alias="LOCAL_RERANKER_BASE_URL",
    )
    local_reranker_model: str = Field(default="local-reranker-model", alias="LOCAL_RERANKER_MODEL")
    rerank_top_n: int = Field(default=5, ge=1, le=50, alias="RERANK_TOP_N")
    default_search_mode: str = Field(default="hybrid", alias="DEFAULT_SEARCH_MODE")
    dense_top_k: int = Field(default=20, ge=1, le=100, alias="DENSE_TOP_K")
    keyword_top_k: int = Field(default=20, ge=1, le=100, alias="KEYWORD_TOP_K")
    final_top_k: int = Field(default=5, ge=1, le=50, alias="FINAL_TOP_K")
    max_upload_file_size_mb: int = Field(default=20, ge=1, le=1024, alias="MAX_UPLOAD_FILE_SIZE_MB")
    upload_temp_dir: str = Field(default="/tmp/aiops_uploads", alias="UPLOAD_TEMP_DIR")
    allowed_file_types: str = Field(default="pdf,docx,txt,md,csv", alias="ALLOWED_FILE_TYPES")
    browser_provider: str = Field(default="mock", alias="BROWSER_PROVIDER")
    browser_timeout_seconds: float = Field(default=30.0, ge=1.0, le=300.0, alias="BROWSER_TIMEOUT_SECONDS")
    browser_headless: bool = Field(default=True, alias="BROWSER_HEADLESS")
    browser_type: str = Field(default="chromium", alias="BROWSER_TYPE")
    browser_viewport_width: int = Field(default=1280, ge=320, le=3840, alias="BROWSER_VIEWPORT_WIDTH")
    browser_viewport_height: int = Field(default=720, ge=240, le=2160, alias="BROWSER_VIEWPORT_HEIGHT")
    browser_screenshot_dir: str = Field(default="screenshots", alias="BROWSER_SCREENSHOT_DIR")
    browser_runtime_screenshot_dir: str = Field(
        default="storage/browser_screenshots",
        alias="BROWSER_RUNTIME_SCREENSHOT_DIR",
    )
    browser_runtime_snapshot_dir: str = Field(
        default="storage/browser_runtime_snapshots",
        alias="BROWSER_RUNTIME_SNAPSHOT_DIR",
    )
    output_artifact_dir: str = Field(default="storage/output_artifacts", alias="OUTPUT_ARTIFACT_DIR")
    output_package_dir: str = Field(default="storage/output_packages", alias="OUTPUT_PACKAGE_DIR")
    output_export_dir: str = Field(default="storage/output_exports", alias="OUTPUT_EXPORT_DIR")
    browser_profile_root: str = Field(default="worker/profiles", alias="BROWSER_PROFILE_ROOT")
    browser_profile_lock_timeout_seconds: int = Field(
        default=1800,
        ge=1,
        le=86400,
        alias="BROWSER_PROFILE_LOCK_TIMEOUT_SECONDS",
    )
    browser_profile_backup_enabled: bool = Field(default=True, alias="BROWSER_PROFILE_BACKUP_ENABLED")
    browser_profile_max_backups: int = Field(default=3, ge=1, le=100, alias="BROWSER_PROFILE_MAX_BACKUPS")
    browser_profile_unused_days: int = Field(default=30, ge=1, le=3650, alias="BROWSER_PROFILE_UNUSED_DAYS")
    browser_profile_backup_root: str = Field(default="worker/profile_backups", alias="BROWSER_PROFILE_BACKUP_ROOT")
    browser_human_control_timeout_seconds: int = Field(
        default=900,
        ge=1,
        le=86400,
        alias="BROWSER_HUMAN_CONTROL_TIMEOUT_SECONDS",
    )
    browser_ui_access_timeout_seconds: int = Field(
        default=900,
        ge=1,
        le=86400,
        alias="BROWSER_UI_ACCESS_TIMEOUT_SECONDS",
    )
    browser_worker_auth_enabled: bool = Field(default=True, alias="BROWSER_WORKER_AUTH_ENABLED")
    browser_worker_auth_strict: bool = Field(default=False, alias="BROWSER_WORKER_AUTH_STRICT")
    browser_allowed_domains: str = Field(default="example.com,localhost,127.0.0.1", alias="BROWSER_ALLOWED_DOMAINS")
    browser_blocked_domains: str = Field(default="", alias="BROWSER_BLOCKED_DOMAINS")
    browser_allow_external_domains: bool = Field(default=False, alias="BROWSER_ALLOW_EXTERNAL_DOMAINS")
    browser_worker_default_timeout_seconds: float = Field(
        default=30.0,
        ge=1.0,
        le=300.0,
        alias="BROWSER_WORKER_DEFAULT_TIMEOUT_SECONDS",
    )
    browser_worker_retry_count: int = Field(default=2, ge=0, le=10, alias="BROWSER_WORKER_RETRY_COUNT")
    browser_worker_default_url: str = Field(default="http://browser-worker:9100", alias="BROWSER_WORKER_DEFAULT_URL")
    browser_worker_heartbeat_timeout_seconds: int = Field(
        default=60,
        ge=1,
        le=3600,
        alias="BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS",
    )
    browser_worker_health_check_interval_seconds: int = Field(
        default=30,
        ge=1,
        le=3600,
        alias="BROWSER_WORKER_HEALTH_CHECK_INTERVAL_SECONDS",
    )
    browser_session_timeout_seconds: int = Field(default=1800, ge=1, le=86400, alias="BROWSER_SESSION_TIMEOUT_SECONDS")
    browser_session_cleanup_interval_seconds: int = Field(
        default=300,
        ge=1,
        le=86400,
        alias="BROWSER_SESSION_CLEANUP_INTERVAL_SECONDS",
    )
    browser_action_timeout_seconds: float = Field(default=60.0, ge=1.0, le=600.0, alias="BROWSER_ACTION_TIMEOUT_SECONDS")
    browser_action_retry_count: int = Field(default=2, ge=0, le=10, alias="BROWSER_ACTION_RETRY_COUNT")
    browser_action_retry_backoff_seconds: float = Field(
        default=2.0,
        ge=0.0,
        le=60.0,
        alias="BROWSER_ACTION_RETRY_BACKOFF_SECONDS",
    )
    screenshot_retention_days: int = Field(default=7, ge=1, le=3650, alias="SCREENSHOT_RETENTION_DAYS")
    openclaw_provider: str = Field(default="mock", alias="OPENCLAW_PROVIDER")
    openclaw_enabled: bool = Field(default=True, alias="OPENCLAW_ENABLED")
    openclaw_action_timeout_seconds: float = Field(default=60.0, ge=1.0, le=600.0, alias="OPENCLAW_ACTION_TIMEOUT_SECONDS")
    comfyui_runtime_provider: str = Field(default="disabled", alias="COMFYUI_RUNTIME_PROVIDER")
    comfyui_runtime_enabled: bool = Field(default=False, alias="COMFYUI_RUNTIME_ENABLED")
    comfyui_runtime_base_url: str = Field(default="http://127.0.0.1:8188", alias="COMFYUI_RUNTIME_BASE_URL")
    comfyui_runtime_timeout_seconds: float = Field(default=30.0, ge=1.0, le=600.0, alias="COMFYUI_RUNTIME_TIMEOUT_SECONDS")
    comfyui_runtime_allow_network: bool = Field(default=False, alias="COMFYUI_RUNTIME_ALLOW_NETWORK")
    comfyui_runtime_allowed_hosts: str = Field(default="127.0.0.1,localhost", alias="COMFYUI_RUNTIME_ALLOWED_HOSTS")
    comfyui_runtime_read_only_probe_enabled: bool = Field(
        default=False,
        alias="COMFYUI_RUNTIME_READ_ONLY_PROBE_ENABLED",
    )
    comfyui_runtime_health_path: str = Field(default="/system_stats", alias="COMFYUI_RUNTIME_HEALTH_PATH")
    comfyui_runtime_allowed_health_paths: str = Field(
        default="/system_stats",
        alias="COMFYUI_RUNTIME_ALLOWED_HEALTH_PATHS",
    )
    comfyui_runtime_prompt_submission_enabled: bool = Field(
        default=False,
        alias="COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED",
    )
    comfyui_runtime_allowed_execution_paths: str = Field(
        default="/prompt,/history,/queue",
        alias="COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS",
    )
    comfyui_video_max_concurrent_jobs: int = Field(default=1, ge=1, le=16, alias="COMFYUI_VIDEO_MAX_CONCURRENT_JOBS")
    comfyui_video_queue_pending_limit: int = Field(default=2, ge=0, le=100, alias="COMFYUI_VIDEO_QUEUE_PENDING_LIMIT")
    comfyui_video_min_free_vram_mb: int = Field(default=2048, ge=0, le=131072, alias="COMFYUI_VIDEO_MIN_FREE_VRAM_MB")
    comfyui_video_default_vram_estimate_mb: int = Field(
        default=8192,
        ge=1024,
        le=131072,
        alias="COMFYUI_VIDEO_DEFAULT_VRAM_ESTIMATE_MB",
    )
    comfyui_video_gpu_endpoints: str = Field(default="", alias="COMFYUI_VIDEO_GPU_ENDPOINTS")
    digital_human_provider: str = Field(default="mock", alias="DIGITAL_HUMAN_PROVIDER")
    digital_human_enabled: bool = Field(default=False, alias="DIGITAL_HUMAN_ENABLED")
    digital_human_allow_external_api: bool = Field(default=False, alias="DIGITAL_HUMAN_ALLOW_EXTERNAL_API")
    digital_human_asset_dir: str = Field(default="storage/digital_human_assets", alias="DIGITAL_HUMAN_ASSET_DIR")
    digital_human_output_dir: str = Field(default="storage/digital_human_outputs", alias="DIGITAL_HUMAN_OUTPUT_DIR")
    digital_human_default_voice_id: str = Field(default="zh-CN-default", alias="DIGITAL_HUMAN_DEFAULT_VOICE_ID")
    digital_human_default_aspect_ratio: str = Field(default="9:16", alias="DIGITAL_HUMAN_DEFAULT_ASPECT_RATIO")

    @property
    def browser_allowed_domain_set(self) -> set[str]:
        """Parse browser allowed-domain policy from CSV config."""

        return {item.strip().lower() for item in self.browser_allowed_domains.split(",") if item.strip()}

    @property
    def browser_blocked_domain_set(self) -> set[str]:
        """Parse browser blocked-domain policy from CSV config."""

        return {item.strip().lower() for item in self.browser_blocked_domains.split(",") if item.strip()}

    @property
    def comfyui_runtime_allowed_host_set(self) -> set[str]:
        """Parse ComfyUI runtime host allowlist from CSV config."""

        return {item.strip().lower() for item in self.comfyui_runtime_allowed_hosts.split(",") if item.strip()}

    @property
    def comfyui_runtime_allowed_health_path_set(self) -> set[str]:
        """Parse ComfyUI runtime read-only health path allowlist from CSV config."""

        paths: set[str] = set()
        for item in self.comfyui_runtime_allowed_health_paths.split(","):
            candidate = item.strip()
            if not candidate:
                continue
            paths.add(candidate if candidate.startswith("/") else f"/{candidate}")
        return paths

    @property
    def comfyui_runtime_allowed_execution_path_set(self) -> set[str]:
        """Parse ComfyUI runtime execution path allowlist from CSV config."""

        paths: set[str] = set()
        for item in self.comfyui_runtime_allowed_execution_paths.split(","):
            candidate = item.strip()
            if not candidate:
                continue
            paths.add(candidate if candidate.startswith("/") else f"/{candidate}")
        return paths

    @property
    def allowed_file_type_set(self) -> set[str]:
        try:
            return {
                item.strip().lower().lstrip(".")
                for item in self.allowed_file_types.split(",")
                if item.strip()
            }
        except Exception as exc:
            logger.exception("Failed to parse allowed file types")
            raise RuntimeError("Invalid upload file type settings") from exc

    @property
    def cors_allowed_origin_list(self) -> list[str]:
        """Parse development CORS origins from CSV config."""

        return [item.strip() for item in self.cors_allowed_origins.split(",") if item.strip()]

    @property
    def database_url(self) -> str:
        try:
            # 对用户名和密码进行 URL 编码，避免特殊字符破坏连接串。
            user = quote_plus(self.postgres_user)
            password = quote_plus(self.postgres_password)
            return (
                f"postgresql+asyncpg://{user}:{password}"
                f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
            )
        except Exception as exc:
            logger.exception("Failed to build PostgreSQL connection URL")
            raise RuntimeError("Invalid PostgreSQL settings") from exc

    @property
    def redis_url(self) -> str:
        try:
            # Redis 密码同样需要 URL 编码，保证复杂密码可以正常使用。
            password = quote_plus(self.redis_password)
            return f"redis://:{password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        except Exception as exc:
            logger.exception("Failed to build Redis connection URL")
            raise RuntimeError("Invalid Redis settings") from exc

    @property
    def qdrant_url(self) -> str:
        try:
            return f"http://{self.qdrant_host}:{self.qdrant_http_port}"
        except Exception as exc:
            logger.exception("Failed to build Qdrant URL")
            raise RuntimeError("Invalid Qdrant settings") from exc


@lru_cache
def get_settings() -> Settings:
    try:
        # 配置对象缓存后可被全局复用，避免重复解析环境变量。
        settings = Settings()
        logger.info("Settings loaded", extra={"app_env": settings.app_env})
        return settings
    except ValidationError as exc:
        logger.exception("Configuration validation failed")
        raise RuntimeError("Application configuration is invalid") from exc
    except Exception as exc:
        logger.exception("Unexpected configuration error")
        raise RuntimeError("Failed to load application configuration") from exc
