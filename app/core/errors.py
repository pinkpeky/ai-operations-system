import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500) -> None:
        try:
            super().__init__(message)
            self.message = message
            self.status_code = status_code
        except Exception as exc:
            logger.exception("Failed to initialize application error")
            raise RuntimeError("Failed to initialize application error") from exc


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    try:
        logger.warning(
            "Handled application error",
            extra={"path": request.url.path, "status_code": exc.status_code},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message},
        )
    except Exception as handler_exc:
        logger.exception("Failed to handle application error")
        raise RuntimeError("Application error handler failed") from handler_exc


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    try:
        logger.exception(
            "Unhandled application error",
            extra={"path": request.url.path},
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
    except Exception as handler_exc:
        logger.exception("Failed to handle unhandled error")
        raise RuntimeError("Unhandled error handler failed") from handler_exc
