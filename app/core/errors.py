"""统一异常处理模块。

该模块定义业务异常和全局异常处理器，避免接口直接暴露内部错误细节。
"""

import logging

from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppError(Exception):
    """应用内可预期业务异常。"""

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
        # 可预期错误只记录警告，并按业务指定状态码返回。
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
        # 未预期错误记录完整堆栈，但对外只返回通用错误信息。
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
