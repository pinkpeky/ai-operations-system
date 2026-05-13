"""Worker Client 本地运行状态管理。"""

from __future__ import annotations

import json
import threading
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_STATUS_PATH = Path("worker_client/runtime_state/status.json")
_STATUS_LOCK = threading.RLock()


def _now_iso() -> str:
    """返回 UTC ISO 时间，便于跨平台日志和状态对齐。"""

    return datetime.now(UTC).isoformat()


def _default_status() -> dict[str, Any]:
    """构造默认状态；不包含 worker_secret 等敏感字段。"""

    return {
        "worker_id": None,
        "worker_name": None,
        "workspace_id": None,
        "server_url": None,
        "worker_base_url": None,
        "runtime_port": None,
        "runtime_running": False,
        "heartbeat_running": False,
        "registered": False,
        "last_heartbeat_at": None,
        "last_error": None,
        "current_status": "stopped",
        "openclaw_enabled": False,
        "browser_enabled": True,
        "updated_at": _now_iso(),
    }


def _sanitize_status(status: dict[str, Any]) -> dict[str, Any]:
    """移除敏感字段，避免本地状态泄露 worker_secret。"""

    clean = dict(status)
    clean.pop("worker_secret", None)
    clean.pop("secret", None)
    return clean


def get_status(path: str | Path = DEFAULT_STATUS_PATH) -> dict[str, Any]:
    """读取本地 runtime status；文件不存在时返回默认状态。"""

    status_path = Path(path)
    with _STATUS_LOCK:
        if not status_path.exists():
            return _default_status()
        with status_path.open("r", encoding="utf-8") as file:
            raw = json.load(file)
    if not isinstance(raw, dict):
        return _default_status()
    status = _default_status()
    status.update(_sanitize_status(raw))
    return status


def write_status(status: dict[str, Any], path: str | Path = DEFAULT_STATUS_PATH) -> dict[str, Any]:
    """写入完整状态并返回安全后的状态。"""

    status_path = Path(path)
    with _STATUS_LOCK:
        status_path.parent.mkdir(parents=True, exist_ok=True)
        clean = _sanitize_status(status)
        clean["updated_at"] = _now_iso()
        temp_path = status_path.with_suffix(f"{status_path.suffix}.tmp")
        with temp_path.open("w", encoding="utf-8") as file:
            json.dump(clean, file, ensure_ascii=False, indent=2)
        temp_path.replace(status_path)
        return clean


def update_status(updates: dict[str, Any], path: str | Path = DEFAULT_STATUS_PATH) -> dict[str, Any]:
    """局部更新本地状态。"""

    with _STATUS_LOCK:
        status = get_status(path)
        status.update(_sanitize_status(updates))
        return write_status(status, path)


def clear_status(path: str | Path = DEFAULT_STATUS_PATH) -> dict[str, Any]:
    """清理本地状态文件并返回默认状态。"""

    status_path = Path(path)
    with _STATUS_LOCK:
        if status_path.exists():
            status_path.unlink()
        return _default_status()
