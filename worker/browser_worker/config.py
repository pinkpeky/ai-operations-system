"""Browser Worker 独立服务配置。"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkerSettings(BaseSettings):
    """Browser Worker runtime settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    worker_host: str = Field(default="0.0.0.0", alias="WORKER_HOST")
    worker_port: int = Field(default=9100, alias="WORKER_PORT")
    worker_timeout_seconds: float = Field(default=30.0, ge=1.0, le=300.0, alias="WORKER_TIMEOUT_SECONDS")
    worker_headless: bool = Field(default=True, alias="WORKER_HEADLESS")
    worker_browser_type: str = Field(default="chromium", alias="WORKER_BROWSER_TYPE")
    worker_screenshot_dir: str = Field(default="worker/screenshots", alias="WORKER_SCREENSHOT_DIR")
    worker_profile_dir: str = Field(default="worker/profiles", alias="WORKER_PROFILE_DIR")
    worker_viewport_width: int = Field(default=1280, ge=320, le=3840, alias="WORKER_VIEWPORT_WIDTH")
    worker_viewport_height: int = Field(default=720, ge=240, le=2160, alias="WORKER_VIEWPORT_HEIGHT")
    browser_worker_auth_enabled: bool = Field(default=True, alias="BROWSER_WORKER_AUTH_ENABLED")
    browser_worker_auth_strict: bool = Field(default=False, alias="BROWSER_WORKER_AUTH_STRICT")
    browser_worker_secret: str = Field(default="", alias="BROWSER_WORKER_SECRET")


@lru_cache
def get_worker_settings() -> WorkerSettings:
    """返回缓存后的 worker settings。"""

    return WorkerSettings()
