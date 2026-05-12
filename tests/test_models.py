"""ORM 模型测试模块。

该模块验证 Phase 2 三张核心表都具备统一字段，并可被 SQLAlchemy metadata 正确识别。
"""

from app.models.account import Account
from app.models.api_key import APIKey
from app.models.collection_metadata import CollectionMetadata
from app.models.document import Document, DocumentChunk
from app.models.publish_log import PublishLog
from app.models.rag_eval import RAGEvalItem, RAGEvalRun
from app.models.task import Task
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember


def test_core_models_have_required_fields() -> None:
    """核心模型必须包含 id、created_at、updated_at、status。"""

    required_fields = {"id", "created_at", "updated_at", "status"}
    for model in (Account, Task, PublishLog):
        column_names = set(model.__table__.columns.keys())
        assert required_fields.issubset(column_names)


def test_knowledge_lifecycle_models_have_required_fields() -> None:
    """知识库生命周期模型必须具备关键生命周期字段。"""

    document_fields = set(Document.__table__.columns.keys())
    chunk_fields = set(DocumentChunk.__table__.columns.keys())
    collection_fields = set(CollectionMetadata.__table__.columns.keys())

    assert {"source_id", "version", "status", "collection_name", "metadata", "ingest_status"}.issubset(document_fields)
    assert {"document_id", "chunk_index", "qdrant_point_id", "metadata", "status"}.issubset(chunk_fields)
    assert {"collection_name", "embedding_provider", "embedding_model_name", "embedding_dimension"}.issubset(
        collection_fields
    )


def test_workspace_isolation_models_have_required_fields() -> None:
    """Workspace 隔离基础模型必须包含关键字段。"""

    assert {"username", "email", "status"}.issubset(set(User.__table__.columns.keys()))
    assert {"name", "slug", "status"}.issubset(set(Workspace.__table__.columns.keys()))
    assert {"workspace_id", "user_id", "role", "status"}.issubset(set(WorkspaceMember.__table__.columns.keys()))
    assert {"workspace_id", "user_id", "key_hash", "name", "status", "last_used_at"}.issubset(
        set(APIKey.__table__.columns.keys())
    )
    assert {"workspace_id", "user_id"}.issubset(set(Task.__table__.columns.keys()))


def test_rag_eval_models_have_required_fields() -> None:
    """RAG Eval 模型必须包含 run 和 item 的核心 trace 字段。"""

    run_fields = set(RAGEvalRun.__table__.columns.keys())
    item_fields = set(RAGEvalItem.__table__.columns.keys())

    assert {
        "workspace_id",
        "name",
        "description",
        "collection_name",
        "embedding_provider",
        "embedding_model_name",
        "llm_provider",
        "llm_model",
        "reranker_provider",
        "reranker_model",
    }.issubset(run_fields)
    assert {
        "run_id",
        "query",
        "expected_answer",
        "retrieved_chunks",
        "final_prompt",
        "final_answer",
        "similarity_scores",
        "eval_mode",
        "reranker_provider",
        "reranker_model",
        "reranked_chunks",
        "rerank_scores",
        "retrieval_before_rerank",
        "retrieval_after_rerank",
        "latency_ms",
        "manual_score",
        "notes",
    }.issubset(item_fields)
