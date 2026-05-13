"""OpenClaw worker adapter foundation."""

from app.openclaw.client import OpenClawWorkerClient, OpenClawWorkerClientResult
from app.openclaw.service import OpenClawService

__all__ = ["OpenClawService", "OpenClawWorkerClient", "OpenClawWorkerClientResult"]
