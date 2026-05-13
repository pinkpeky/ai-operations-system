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

    @property
    def browser_allowed_domain_set(self) -> set[str]:
        """Parse browser allowed-domain policy from CSV config."""

        return {item.strip().lower() for item in self.browser_allowed_domains.split(",") if item.strip()}

    @property
    def browser_blocked_domain_set(self) -> set[str]:
        """Parse browser blocked-domain policy from CSV config."""

        return {item.strip().lower() for item in self.browser_blocked_domains.split(",") if item.strip()}

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
