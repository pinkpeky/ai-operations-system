"""RAG API 路由模块。

当前阶段仅提供文档写入、Top-K 检索、collection 健康检查和 debug 能力，不接入 LLM Client 或 Scheduler。
"""

import logging

from fastapi import APIRouter

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.rag.document_chunker import DocumentChunker
from app.rag.embedding_client import EmbeddingClient
from app.rag.ingestion import IngestionPipeline
from app.rag.retrieval import RetrievalPipeline
from app.rag.vector_store import QdrantVectorStore, VectorSearchResult
from app.schemas.rag import (
    CollectionHealthResponse,
    CollectionListResponse,
    DebugScore,
    IngestRequest,
    IngestResponse,
    RAGDebugResponse,
    RetrievedChunk,
    SearchRequest,
    SearchResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])


def create_vector_store(settings: Settings, collection_name: str | None = None) -> QdrantVectorStore:
    """创建 Qdrant VectorStore。"""

    selected_collection = collection_name or settings.qdrant_collection_name
    return QdrantVectorStore(
        collection_name=selected_collection,
        embedding_dimension=settings.embedding_dimension,
        allow_collection_delete=settings.app_env == "test",
    )


def create_ingestion_pipeline(settings: Settings, collection_name: str | None = None) -> IngestionPipeline:
    """创建 RAG 写入流水线。"""

    embedding_client = EmbeddingClient(settings=settings)
    vector_store = create_vector_store(settings=settings, collection_name=collection_name)
    return IngestionPipeline(
        embedding_client=embedding_client,
        vector_store=vector_store,
        chunker=DocumentChunker(),
    )


def create_retrieval_pipeline(settings: Settings, collection_name: str | None = None) -> RetrievalPipeline:
    """创建 RAG 检索流水线。"""

    embedding_client = EmbeddingClient(settings=settings)
    vector_store = create_vector_store(settings=settings, collection_name=collection_name)
    return RetrievalPipeline(embedding_client=embedding_client, vector_store=vector_store)


def build_retrieved_chunk(result: VectorSearchResult) -> RetrievedChunk:
    """将内部检索结果转换为 API 响应 chunk。"""

    return RetrievedChunk(
        id=result.id,
        text=result.text,
        similarity_score=result.similarity_score,
        raw_score=result.raw_score,
        metadata=result.metadata,
        chunk_index=result.chunk_index,
    )


def build_collection_health_response(health) -> CollectionHealthResponse:  # type: ignore[no-untyped-def]
    """将内部 collection 健康信息转换为 API 响应。"""

    return CollectionHealthResponse(
        collection_name=health.collection_name,
        exists=health.exists,
        status=health.status,
        points_count=health.points_count,
        vectors_count=health.vectors_count,
        embedding_dimension=health.embedding_dimension,
    )


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(request: IngestRequest) -> IngestResponse:
    """写入文本到 Qdrant 知识库。"""

    try:
        settings = get_settings()
        pipeline = create_ingestion_pipeline(settings=settings, collection_name=request.collection_name)
        result = await pipeline.ingest_text(
            text=request.text,
            metadata=request.metadata,
            source_id=request.source_id,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
        logger.info(
            "RAG ingest API completed",
            extra={
                "collection": result.collection_name,
                "source_id": result.source_id,
                "chunk_count": result.chunk_count,
            },
        )
        return IngestResponse(
            collection_name=result.collection_name,
            source_id=result.source_id,
            chunk_count=result.chunk_count,
            chunk_ids=result.chunk_ids,
        )
    except ValueError as exc:
        logger.warning("RAG ingest API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("RAG ingest API failed")
        raise AppError("RAG ingest failed", status_code=500) from exc


@router.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest) -> SearchResponse:
    """从 Qdrant 知识库检索相关 chunk。"""

    try:
        settings = get_settings()
        pipeline = create_retrieval_pipeline(settings=settings, collection_name=request.collection_name)
        results = await pipeline.search(query=request.query, top_k=request.top_k)
        logger.info(
            "RAG search API completed",
            extra={
                "collection": pipeline.vector_store.collection_name,
                "top_k": request.top_k,
                "count": len(results),
            },
        )
        return SearchResponse(
            collection_name=pipeline.vector_store.collection_name,
            query=request.query,
            items=[build_retrieved_chunk(result) for result in results],
        )
    except ValueError as exc:
        logger.warning("RAG search API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("RAG search API failed")
        raise AppError("RAG search failed", status_code=500) from exc


@router.get("/collections", response_model=CollectionListResponse)
async def list_collections() -> CollectionListResponse:
    """列出 Qdrant collections 并返回健康信息。"""

    try:
        settings = get_settings()
        base_store = create_vector_store(settings=settings)
        collection_names = await base_store.list_collection_names()
        collections = []
        for collection_name in collection_names:
            store = create_vector_store(settings=settings, collection_name=collection_name)
            collections.append(build_collection_health_response(await store.get_collection_health()))
        return CollectionListResponse(collections=collections)
    except Exception as exc:
        logger.exception("RAG collection list API failed")
        raise AppError("RAG collection list failed", status_code=500) from exc


@router.get("/collections/{collection_name}", response_model=CollectionHealthResponse)
async def get_collection(collection_name: str) -> CollectionHealthResponse:
    """获取单个 Qdrant collection 的健康信息。"""

    try:
        settings = get_settings()
        store = create_vector_store(settings=settings, collection_name=collection_name)
        return build_collection_health_response(await store.get_collection_health())
    except Exception as exc:
        logger.exception("RAG collection health API failed", extra={"collection": collection_name})
        raise AppError("RAG collection health failed", status_code=500) from exc


@router.post("/debug", response_model=RAGDebugResponse)
async def debug_retrieval(request: SearchRequest) -> RAGDebugResponse:
    """调试 RAG 检索链路，返回 query embedding 维度和分数细节。"""

    try:
        settings = get_settings()
        embedding_client = EmbeddingClient(settings=settings)
        vector_store = create_vector_store(settings=settings, collection_name=request.collection_name)
        query_embedding = await embedding_client.embed_query(request.query)
        results = await vector_store.similarity_search(query_embedding=query_embedding, top_k=request.top_k)
        retrieved_chunks = [build_retrieved_chunk(result) for result in results]
        return RAGDebugResponse(
            query=request.query,
            query_embedding_dimension=len(query_embedding),
            collection_name=vector_store.collection_name,
            retrieved_chunks=retrieved_chunks,
            scores=[
                DebugScore(
                    id=result.id,
                    similarity_score=result.similarity_score,
                    raw_score=result.raw_score,
                )
                for result in results
            ],
        )
    except ValueError as exc:
        logger.warning("RAG debug API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("RAG debug API failed")
        raise AppError("RAG debug failed", status_code=500) from exc
