"""日志配置模块。

该模块集中配置应用日志格式和输出位置，保证所有服务模块都能输出统一日志。
"""

import logging
import sys
from logging.config import dictConfig

LOGGER_NAME = "aiops"
logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    try:
        # 将环境变量传入的日志级别标准化，避免大小写导致配置不生效。
        normalized_level = level.upper()
        dictConfig(
            {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "formatter": "default",
                        "stream": sys.stdout,
                    }
                },
                "root": {
                    "handlers": ["console"],
                    "level": normalized_level,
                },
            }
        )
        logger.info("Logging configured", extra={"level": normalized_level})
    except Exception as exc:
        # 日志系统本身出错时退回默认日志，确保错误仍可被看到。
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).exception("Failed to configure logging")
        raise RuntimeError("Failed to configure application logging") from exc
