"""Worker Client 本地配置读取与 state 管理。"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml


DEFAULT_CONFIG_PATH = Path("worker_client/worker_config.yaml")
DEFAULT_EXAMPLE_CONFIG_PATH = Path("worker_client/worker_config.example.yaml")
DEFAULT_STATE_PATH = Path("worker_client/worker_state.json")


def _env(name: str) -> str | None:
    """读取 WORKER_CLIENT_* 环境变量。"""

    value = os.getenv(f"WORKER_CLIENT_{name}")
    return value if value not in {None, ""} else None


def _to_bool(value: str | bool | None, default: bool) -> bool:
    """把 env/yaml 中的 bool-like 值转换为 bool。"""

    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _to_int(value: str | int | None, default: int) -> int:
    """把 env/yaml 中的 int-like 值转换为 int。"""

    if value is None:
        return default
    return int(value)


@dataclass(slots=True)
class WorkerClientConfig:
    """客户机 Worker Client 配置。"""

    server_url: str
    worker_name: str
    worker_type: str
    workspace_id: str
    worker_secret: str | None = None
    heartbeat_interval_seconds: int = 30
    capabilities: dict[str, Any] = field(default_factory=dict)
    worker_base_url: str | None = None
    runtime_host: str = "0.0.0.0"
    runtime_port: int = 9100
    state_path: Path = DEFAULT_STATE_PATH
    max_sessions: int = 5
    max_actions_per_minute: int = 60
    priority: int = 100
    allowed_actions: list[str] = field(
        default_factory=lambda: ["navigate", "click", "type_text", "scroll", "screenshot", "get_page_content"]
    )
    allowed_domains: list[str] = field(default_factory=lambda: ["example.com", "localhost", "127.0.0.1"])
    auth_enabled: bool = True
    auth_strict: bool = False
    timeout_seconds: float = 30.0
    screenshot_dir: str = "worker/screenshots"
    profile_dir: str = "worker/profiles"

    @property
    def normalized_server_url(self) -> str:
        """返回无尾斜杠 server URL。"""

        return self.server_url.rstrip("/")

    @property
    def effective_worker_base_url(self) -> str:
        """返回注册到 AI Server 的本机 worker runtime URL。"""

        return (self.worker_base_url or f"http://localhost:{self.runtime_port}").rstrip("/")

    def headers(self) -> dict[str, str]:
        """构造 AI Server workspace header。"""

        return {"X-Workspace-Id": self.workspace_id}

    def redacted(self) -> dict[str, Any]:
        """返回可安全打印的配置，不包含明文 secret。"""

        data = asdict(self)
        data["state_path"] = str(self.state_path)
        if data.get("worker_secret"):
            data["worker_secret"] = "***"
        return data


@dataclass(slots=True)
class WorkerClientState:
    """客户机本地 state，保存一次性 worker_secret。"""

    worker_id: str
    worker_secret: str
    server_url: str
    worker_name: str
    workspace_id: str
    worker_base_url: str
    registered_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def redacted(self) -> dict[str, Any]:
        """返回可安全打印的 state，不包含明文 secret。"""

        data = asdict(self)
        data["worker_secret"] = "***"
        return data


def load_worker_client_config(config_path: str | Path | None = None) -> WorkerClientConfig:
    """从 yaml 读取配置，并应用 WORKER_CLIENT_* 环境变量覆盖。"""

    path = Path(config_path or os.getenv("WORKER_CLIENT_CONFIG") or DEFAULT_CONFIG_PATH)
    if not path.exists():
        raise FileNotFoundError(
            f"Worker config not found: {path}. Copy worker_client/worker_config.example.yaml to worker_client/worker_config.yaml first."
        )
    with path.open("r", encoding="utf-8") as file:
        raw = yaml.safe_load(file) or {}
    if not isinstance(raw, dict):
        raise ValueError("Worker config yaml must be a mapping")

    capabilities = raw.get("capabilities") or {}
    env_capabilities = _env("CAPABILITIES")
    if env_capabilities:
        capabilities = json.loads(env_capabilities)

    state_path = Path(_env("STATE_PATH") or raw.get("state_path") or DEFAULT_STATE_PATH)
    config = WorkerClientConfig(
        server_url=_env("SERVER_URL") or str(raw.get("server_url") or "http://localhost:8000"),
        worker_name=_env("WORKER_NAME") or str(raw.get("worker_name") or "local-worker"),
        worker_type=_env("WORKER_TYPE") or str(raw.get("worker_type") or "playwright"),
        workspace_id=_env("WORKSPACE_ID") or str(raw.get("workspace_id") or "demo-workspace"),
        worker_secret=_env("WORKER_SECRET") or raw.get("worker_secret"),
        heartbeat_interval_seconds=_to_int(_env("HEARTBEAT_INTERVAL_SECONDS") or raw.get("heartbeat_interval_seconds"), 30),
        capabilities=dict(capabilities),
        worker_base_url=_env("WORKER_BASE_URL") or raw.get("worker_base_url"),
        runtime_host=_env("RUNTIME_HOST") or str(raw.get("runtime_host") or "0.0.0.0"),
        runtime_port=_to_int(_env("RUNTIME_PORT") or raw.get("runtime_port"), 9100),
        state_path=state_path,
        max_sessions=_to_int(_env("MAX_SESSIONS") or raw.get("max_sessions"), 5),
        max_actions_per_minute=_to_int(_env("MAX_ACTIONS_PER_MINUTE") or raw.get("max_actions_per_minute"), 60),
        priority=_to_int(_env("PRIORITY") or raw.get("priority"), 100),
        allowed_actions=list(raw.get("allowed_actions") or ["navigate", "click", "type_text", "scroll", "screenshot", "get_page_content"]),
        allowed_domains=list(raw.get("allowed_domains") or ["example.com", "localhost", "127.0.0.1"]),
        auth_enabled=_to_bool(_env("AUTH_ENABLED") or raw.get("auth_enabled"), True),
        auth_strict=_to_bool(_env("AUTH_STRICT") or raw.get("auth_strict"), False),
        timeout_seconds=float(_env("TIMEOUT_SECONDS") or raw.get("timeout_seconds") or 30.0),
        screenshot_dir=str(raw.get("screenshot_dir") or "worker/screenshots"),
        profile_dir=str(raw.get("profile_dir") or "worker/profiles"),
    )
    return config


def load_worker_state(path: str | Path) -> WorkerClientState | None:
    """读取本地 worker_state.json。"""

    state_path = Path(path)
    if not state_path.exists():
        return None
    with state_path.open("r", encoding="utf-8") as file:
        raw = json.load(file)
    return WorkerClientState(
        worker_id=str(raw["worker_id"]),
        worker_secret=str(raw["worker_secret"]),
        server_url=str(raw["server_url"]),
        worker_name=str(raw["worker_name"]),
        workspace_id=str(raw["workspace_id"]),
        worker_base_url=str(raw["worker_base_url"]),
        registered_at=str(raw.get("registered_at") or datetime.now(UTC).isoformat()),
    )


def save_worker_state(path: str | Path, state: WorkerClientState) -> None:
    """保存 worker_state.json，并尽量设置为仅当前用户可读写。"""

    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with state_path.open("w", encoding="utf-8") as file:
        json.dump(asdict(state), file, ensure_ascii=False, indent=2)
    try:
        os.chmod(state_path, 0o600)
    except OSError:
        # Windows 上 chmod 语义有限，失败时不影响功能；不要打印 secret。
        pass

