import logging

from fastapi import APIRouter

from app.api.routes.health import router as health_router

logger = logging.getLogger(__name__)


def create_api_router() -> APIRouter:
    try:
        router = APIRouter(prefix="/api/v1")
        router.include_router(health_router)
        logger.info("API router configured")
        return router
    except Exception as exc:
        logger.exception("Failed to configure API router")
        raise RuntimeError("API router configuration failed") from exc
