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
