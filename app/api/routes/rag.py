"""RAG API 路由模块。

提供文档写入、Dense/Keyword/Hybrid 检索、collection 健康检查和 debug 能力。
"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.rag.document_chunker import DocumentChunker
from app.rag.embedding_client import EmbeddingClient
from app.rag.hybrid_search import HybridSearchPipeline, KeywordSearch
from app.rag.ingestion import IngestionPipeline
from app.rag.retrieval import RetrievalPipeline
from app.rag.vector_store import QdrantVectorStore, VectorSearchResult
from app.repositories.collection_repository import CollectionRepository
from app.reranker.providers.base import RerankedChunk
from app.reranker.reranker_client import RerankerClient
from app.schemas.rag import (
    CollectionHealthResponse,
    CollectionListResponse,
    DebugScore,
    EmbeddingHealthResponse,
    IngestRequest,
    IngestResponse,
    RAGDebugResponse,
    RetrievedChunk,
    SearchRequest,
    SearchResponse,
)
from app.services.document_lifecycle import DocumentLifecycleService

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


def create_document_lifecycle_service(
    settings: Settings,
    session: AsyncSession,
    collection_name: str | None = None,
) -> DocumentLifecycleService:
    """创建文档生命周期服务。"""

    return DocumentLifecycleService(
        session=session,
        ingestion_pipeline=create_ingestion_pipeline(settings=settings, collection_name=collection_name),
    )


def create_retrieval_pipeline(settings: Settings, collection_name: str | None = None) -> RetrievalPipeline:
    """创建 Dense Retrieval 流水线。"""

    embedding_client = EmbeddingClient(settings=settings)
    vector_store = create_vector_store(settings=settings, collection_name=collection_name)
    return RetrievalPipeline(embedding_client=embedding_client, vector_store=vector_store)


def create_hybrid_search_pipeline(
    settings: Settings,
    session: AsyncSession,
    collection_name: str | None = None,
) -> HybridSearchPipeline:
    """创建 Hybrid Search 流水线。"""

    return HybridSearchPipeline(
        retrieval_pipeline=create_retrieval_pipeline(settings=settings, collection_name=collection_name),
        keyword_search=KeywordSearch(session=session),
    )


def build_retrieved_chunk(result: VectorSearchResult) -> RetrievedChunk:
    """将内部检索结果转换为 API 响应 chunk。"""

    return RetrievedChunk(
        id=result.id,
        text=result.text,
        similarity_score=result.similarity_score,
        raw_score=result.raw_score,
        dense_score=result.dense_score,
        keyword_score=result.keyword_score,
        hybrid_score=result.hybrid_score,
        metadata=result.metadata,
        chunk_index=result.chunk_index,
    )


def build_retrieved_chunk_from_reranked(result: RerankedChunk) -> RetrievedChunk:
    """将 Reranker 结果转换为 API 响应 chunk。"""

    return RetrievedChunk(
        id=result.id,
        text=result.text,
        similarity_score=result.similarity_score,
        raw_score=result.raw_score,
        rerank_score=result.rerank_score,
        original_similarity_score=result.similarity_score,
        dense_score=result.dense_score,
        keyword_score=result.keyword_score,
        hybrid_score=result.hybrid_score,
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
async def ingest_document(
    request: IngestRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> IngestResponse:
    """写入文本到 RAG 知识库。"""

    try:
        settings = get_settings()
        service = create_document_lifecycle_service(
            settings=settings,
            session=session,
            collection_name=request.collection_name,
        )
        result = await service.ingest_text(
            text=request.text,
            metadata=request.metadata,
            source_id=request.source_id,
            source_name=request.source_name,
            source_type=request.source_type,
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
        )
        logger.info(
            "RAG ingest API completed",
            extra={"collection": result.collection_name, "source_id": result.source_id, "chunk_count": result.chunk_count},
        )
        return IngestResponse(
            collection_name=result.collection_name,
            source_id=result.source_id,
            document_id=result.document_id,
            version=result.version,
            chunk_count=result.chunk_count,
            chunk_ids=result.chunk_ids,
        )
    except ValueError as exc:
        logger.warning("RAG ingest API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("RAG ingest API failed")
        raise AppError("RAG ingest failed", status_code=500) from exc


@router.get("/embedding/health", response_model=EmbeddingHealthResponse)
async def embedding_health() -> EmbeddingHealthResponse:
    """检查当前 Embedding Provider 是否可用，并返回真实向量维度。"""

    try:
        settings = get_settings()
        embedding_client = EmbeddingClient(settings=settings)
        return await embedding_client.health_check()
    except Exception as exc:
        logger.exception("RAG embedding health API failed")
        raise AppError(str(exc) or "RAG embedding health failed", status_code=500) from exc


@router.post("/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> SearchResponse:
    """按 dense / keyword / hybrid 模式检索相关 chunk。"""

    try:
        settings = get_settings()
        search_mode = request.search_mode or settings.default_search_mode
        if search_mode not in {"dense", "keyword", "hybrid"}:
            raise ValueError("search_mode must be dense, keyword, or hybrid")
        legacy_top_k = request.top_k if "top_k" in request.model_fields_set else None
        dense_top_k = request.dense_top_k or legacy_top_k or settings.dense_top_k
        keyword_top_k = request.keyword_top_k or legacy_top_k or settings.keyword_top_k
        final_top_k = request.final_top_k or legacy_top_k or settings.final_top_k
        pipeline = create_hybrid_search_pipeline(
            settings=settings,
            session=session,
            collection_name=request.collection_name,
        )
        bundle = await pipeline.search(
            query=request.query,
            search_mode=search_mode,
            dense_top_k=dense_top_k,
            keyword_top_k=keyword_top_k,
            source_id=request.source_id,
            workspace_id=context.workspace_id,
        )
        reranker = RerankerClient(settings=settings)
        reranked = await reranker.rerank(query=request.query, chunks=bundle.merged_results, top_n=final_top_k)
        logger.info(
            "RAG search API completed",
            extra={
                "collection": pipeline.vector_store.collection_name,
                "search_mode": search_mode,
                "dense_count": len(bundle.dense_results),
                "keyword_count": len(bundle.keyword_results),
                "merged_count": len(bundle.merged_results),
                "count": len(reranked),
            },
        )
        return SearchResponse(
            collection_name=pipeline.vector_store.collection_name,
            query=request.query,
            search_mode=search_mode,
            items=[build_retrieved_chunk_from_reranked(result) for result in reranked],
        )
    except ValueError as exc:
        logger.warning("RAG search API received invalid request", extra={"error": str(exc)})
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("RAG search API failed")
        raise AppError("RAG search failed", status_code=500) from exc


@router.get("/collections", response_model=CollectionListResponse)
async def list_collections(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CollectionListResponse:
    """列出当前 workspace 下的 Qdrant collections 并返回健康信息。"""

    try:
        settings = get_settings()
        collection_repository = CollectionRepository(session)
        collection_records = await collection_repository.list_by_workspace(context.workspace_id)
        collections = []
        for collection_record in collection_records:
            store = create_vector_store(settings=settings, collection_name=collection_record.collection_name)
            collections.append(build_collection_health_response(await store.get_collection_health()))
        return CollectionListResponse(collections=collections)
    except Exception as exc:
        logger.exception("RAG collection list API failed")
        raise AppError("RAG collection list failed", status_code=500) from exc


@router.get("/collections/{collection_name}", response_model=CollectionHealthResponse)
async def get_collection(
    collection_name: str,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CollectionHealthResponse:
    """获取单个 Qdrant collection 的健康信息。"""

    try:
        settings = get_settings()
        collection_repository = CollectionRepository(session)
        metadata = await collection_repository.get_by_name(collection_name, workspace_id=context.workspace_id)
        if metadata is None:
            raise AppError("Collection not found in workspace", status_code=404)
        store = create_vector_store(settings=settings, collection_name=collection_name)
        return build_collection_health_response(await store.get_collection_health())
    except AppError:
        raise
    except Exception as exc:
        logger.exception("RAG collection health API failed", extra={"collection": collection_name})
        raise AppError("RAG collection health failed", status_code=500) from exc


@router.post("/debug", response_model=RAGDebugResponse)
async def debug_retrieval(
    request: SearchRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
) -> RAGDebugResponse:
    """调试 Dense RAG 检索链路，返回 query embedding 维度和分数细节。"""

    try:
        settings = get_settings()
        embedding_client = EmbeddingClient(settings=settings)
        vector_store = create_vector_store(settings=settings, collection_name=request.collection_name)
        query_embedding = await embedding_client.embed_query(request.query)
        results = await vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=request.top_k,
            source_id=request.source_id,
            workspace_id=context.workspace_id,
        )
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
                    dense_score=result.dense_score,
                    keyword_score=result.keyword_score,
                    hybrid_score=result.hybrid_score,
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
