import logging
from functools import lru_cache
from urllib.parse import quote_plus

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
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

    qdrant_host: str = Field(default="localhost", alias="QDRANT_HOST")
    qdrant_http_port: int = Field(default=6333, alias="QDRANT_HTTP_PORT")
    qdrant_grpc_port: int = Field(default=6334, alias="QDRANT_GRPC_PORT")
    qdrant_api_key: str = Field(default="change_me", alias="QDRANT_API_KEY")

    @property
    def database_url(self) -> str:
        try:
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
        settings = Settings()
        logger.info("Settings loaded", extra={"app_env": settings.app_env})
        return settings
    except ValidationError as exc:
        logger.exception("Configuration validation failed")
        raise RuntimeError("Application configuration is invalid") from exc
    except Exception as exc:
        logger.exception("Unexpected configuration error")
        raise RuntimeError("Failed to load application configuration") from exc
