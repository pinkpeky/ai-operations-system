import logging
from collections.abc import Awaitable, Callable

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.db.postgres import check_postgres
from app.db.qdrant import check_qdrant
from app.db.redis import check_redis
from app.schemas.health import ComponentHealth, HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])
Checker = Callable[[], Awaitable[bool]]


async def _run_component_check(name: str, checker: Checker) -> ComponentHealth:
    try:
        await checker()
        logger.debug("Component health check passed", extra={"component": name})
        return ComponentHealth(name=name, status="ok", detail="ready")
    except Exception as exc:
        logger.warning(
            "Component health check failed",
            extra={"component": name, "error": str(exc)},
        )
        return ComponentHealth(name=name, status="error", detail=str(exc))


@router.get("", response_model=HealthResponse)
async def health_check() -> JSONResponse | HealthResponse:
    try:
        checks: list[tuple[str, Checker]] = [
            ("postgres", check_postgres),
            ("redis", check_redis),
            ("qdrant", check_qdrant),
        ]
        components = [
            await _run_component_check(name, checker)
            for name, checker in checks
        ]
        overall_status = "ok" if all(item.status == "ok" for item in components) else "degraded"
        response = HealthResponse(status=overall_status, components=components)
        status_code = 200 if overall_status == "ok" else 503
        logger.info("Health check completed", extra={"status": overall_status})
        return JSONResponse(status_code=status_code, content=response.model_dump())
    except Exception as exc:
        logger.exception("Health endpoint failed")
        response = HealthResponse(
            status="degraded",
            components=[
                ComponentHealth(
                    name="api",
                    status="error",
                    detail="Health endpoint failed",
                )
            ],
        )
        return JSONResponse(status_code=500, content=response.model_dump())
