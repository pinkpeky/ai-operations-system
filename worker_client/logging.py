"""Worker Client 本地日志封装。"""

from __future__ import annotations

import logging
import re
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Iterable

DEFAULT_LOG_PATH = Path("worker_client/logs/worker.log")
DEFAULT_MAX_BYTES = 1_000_000
DEFAULT_BACKUP_COUNT = 3

_LOGGER_NAME = "worker_client.local"
_SENSITIVE_PATTERNS = (
    re.compile(r"(worker_secret\s*[=:]\s*)[^\s,}]+", re.IGNORECASE),
    re.compile(r"(X-Worker-Secret\s*[=:]\s*)[^\s,}]+", re.IGNORECASE),
    re.compile(r"(\bsecret\s*[=:]\s*)[^\s,}]+", re.IGNORECASE),
)


def redact_secret(value: object) -> str:
    """对日志文本做轻量脱敏，避免写入 worker_secret。"""

    text = str(value)
    for pattern in _SENSITIVE_PATTERNS:
        text = pattern.sub(r"\1[redacted]", text)
    return text


class SecretRedactionFilter(logging.Filter):
    """日志过滤器，确保 message / args 中不直接落 secret。"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_secret(record.msg)
        if record.args:
            record.args = tuple(redact_secret(arg) for arg in record.args)  # type: ignore[assignment]
        return True


def configure_worker_logging(
    log_path: str | Path = DEFAULT_LOG_PATH,
    *,
    level: int = logging.INFO,
    max_bytes: int = DEFAULT_MAX_BYTES,
    backup_count: int = DEFAULT_BACKUP_COUNT,
) -> logging.Logger:
    """配置 Worker Client 文件日志，支持简单轮转。"""

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = True

    for handler in list(logger.handlers):
        if isinstance(handler, RotatingFileHandler) and Path(handler.baseFilename) == path:
            return logger

    handler = RotatingFileHandler(
        path,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    handler.addFilter(SecretRedactionFilter())
    logger.addHandler(handler)
    return logger


def get_worker_logger() -> logging.Logger:
    """返回 Worker Client 本地 logger。"""

    return configure_worker_logging()


def get_recent_logs(lines: int = 100, log_path: str | Path = DEFAULT_LOG_PATH) -> list[str]:
    """读取最近 N 行日志，供本地 Console API 使用。"""

    path = Path(log_path)
    if not path.exists():
        return []
    safe_lines = max(1, min(lines, 1000))
    with path.open("r", encoding="utf-8", errors="replace") as file:
        content = file.readlines()
    return [redact_secret(line.rstrip("\n")) for line in content[-safe_lines:]]


def log_event(message: str, *, level: int = logging.INFO, extra: dict[str, object] | None = None) -> None:
    """记录一条本地事件日志。"""

    logger = get_worker_logger()
    suffix = ""
    if extra:
        suffix = " " + " ".join(f"{key}={redact_secret(value)}" for key, value in extra.items())
    logger.log(level, "%s%s", message, suffix)


def redact_mapping(items: Iterable[tuple[str, object]]) -> dict[str, str]:
    """将键值对转换为安全日志字典。"""

    return {key: redact_secret(value) for key, value in items}
