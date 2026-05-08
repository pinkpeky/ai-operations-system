import logging
from typing import Literal

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ComponentHealth(BaseModel):
    name: str = Field(description="Component name")
    status: Literal["ok", "error"] = Field(description="Component health status")
    detail: str = Field(default="ready", description="Human readable status detail")


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    components: list[ComponentHealth]
