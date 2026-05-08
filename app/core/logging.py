import logging
import sys
from logging.config import dictConfig

LOGGER_NAME = "aiops"
logger = logging.getLogger(__name__)


def setup_logging(level: str = "INFO") -> None:
    try:
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
        logging.basicConfig(level=logging.INFO)
        logging.getLogger(__name__).exception("Failed to configure logging")
        raise RuntimeError("Failed to configure application logging") from exc
