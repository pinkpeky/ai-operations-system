import logging
import asyncio
from typing import Optional

from qdrant_client import AsyncQdrantClient

from app.core.config import Settings

logger = logging.getLogger(__name__)

qdrant_client: Optional[AsyncQdrantClient] = None


async def init_qdrant(settings: Settings) -> None:
    global qdrant_client

    try:
        qdrant_client = AsyncQdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=10,
        )
        for attempt in range(1, 11):
            try:
                await check_qdrant()
                break
            except Exception:
                if attempt == 10:
                    raise
                logger.warning("Qdrant not ready, retrying", extra={"attempt": attempt})
                await asyncio.sleep(2)
        logger.info("Qdrant connection initialized")
    except Exception as exc:
        logger.exception("Failed to initialize Qdrant connection")
        await close_qdrant()
        raise RuntimeError("Qdrant initialization failed") from exc


async def check_qdrant() -> bool:
    try:
        if qdrant_client is None:
            raise RuntimeError("Qdrant client is not initialized")
        await qdrant_client.get_collections()
        logger.debug("Qdrant health check passed")
        return True
    except Exception as exc:
        logger.exception("Qdrant health check failed")
        raise RuntimeError("Qdrant health check failed") from exc


async def close_qdrant() -> None:
    global qdrant_client

    try:
        if qdrant_client is not None:
            await qdrant_client.close()
            logger.info("Qdrant connection closed")
    except Exception as exc:
        logger.exception("Failed to close Qdrant connection")
        raise RuntimeError("Qdrant shutdown failed") from exc
    finally:
        qdrant_client = None
