"""Standalone local reranker FastAPI service."""

from __future__ import annotations

import logging

from fastapi import Depends, FastAPI, HTTPException, status

from worker.reranker_worker.config import get_reranker_worker_settings
from worker.reranker_worker.runtime import OllamaEmbeddingRerankerRuntime
from worker.reranker_worker.schemas import RerankerRuntimeHealthResponse, RerankRequest, RerankResponse

logger = logging.getLogger(__name__)

_runtime: OllamaEmbeddingRerankerRuntime | None = None


def get_runtime() -> OllamaEmbeddingRerankerRuntime:
    """Return the process-local reranker runtime singleton."""

    global _runtime
    if _runtime is None:
        _runtime = OllamaEmbeddingRerankerRuntime(settings=get_reranker_worker_settings())
    return _runtime


def create_app(runtime: OllamaEmbeddingRerankerRuntime | None = None) -> FastAPI:
    """Create the reranker worker app, optionally with a test runtime."""

    app = FastAPI(title="AI Ops Local Reranker Worker")

    if runtime is not None:
        app.dependency_overrides[get_runtime] = lambda: runtime

    @app.get("/health", response_model=RerankerRuntimeHealthResponse)
    async def health(current_runtime: OllamaEmbeddingRerankerRuntime = Depends(get_runtime)) -> RerankerRuntimeHealthResponse:
        return await current_runtime.health_check()

    @app.post("/api/rerank", response_model=RerankResponse)
    async def rerank(
        request: RerankRequest,
        current_runtime: OllamaEmbeddingRerankerRuntime = Depends(get_runtime),
    ) -> RerankResponse:
        try:
            return await current_runtime.rerank(request)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except Exception as exc:
            logger.exception("Reranker runtime request failed")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc

    return app


app = create_app()
