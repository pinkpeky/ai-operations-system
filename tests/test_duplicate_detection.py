"""文件重复检测测试。"""

from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi import UploadFile

from app.file_pipeline.parsers.base import ParsedFile
from app.file_pipeline.services.upload_service import FileUploadService
from app.services.document_lifecycle import DocumentLifecycleIngestResult


class FakeParserRegistry:
    """固定返回解析文本。"""

    def parse(self, *, path, file_type):  # type: ignore[no-untyped-def]
        return ParsedFile(text="uploaded file text", metadata={"parser": "fake"})


class FakeSession:
    """记录 commit 调用。"""

    def __init__(self) -> None:
        self.commits = 0

    async def commit(self) -> None:
        self.commits += 1


class FakeLifecycleService:
    """生命周期服务替身。"""

    def __init__(self) -> None:
        self.session = FakeSession()
        self.calls: list[dict[str, object]] = []

    async def ingest_text(self, **kwargs):  # type: ignore[no-untyped-def]
        self.calls.append(kwargs)
        return DocumentLifecycleIngestResult(
            collection_name="upload_collection",
            source_id=str(kwargs["source_id"]),
            document_id="11111111-1111-4111-8111-111111111111",
            version=2,
            chunk_count=1,
            chunk_ids=["point-1"],
        )


class FakeDocumentRepository:
    """可配置重复文档的 repository 替身。"""

    def __init__(self, duplicate=None) -> None:  # type: ignore[no-untyped-def]
        self.duplicate = duplicate
        self.updated_metadata: dict[str, object] | None = None

    async def get_active_document_by_file_hash(self, **kwargs):  # type: ignore[no-untyped-def]
        return self.duplicate

    async def update_document_metadata(self, *, document_id: str, metadata: dict[str, object]) -> None:
        self.updated_metadata = metadata


def create_settings(tmp_path):  # type: ignore[no-untyped-def]
    """创建上传服务所需的最小 settings。"""

    return SimpleNamespace(
        upload_temp_dir=str(tmp_path),
        max_upload_file_size_mb=1,
        allowed_file_type_set={"txt"},
    )


def create_upload_file(content: bytes = b"hello duplicate") -> UploadFile:
    """创建测试 UploadFile。"""

    return UploadFile(filename="demo.txt", file=BytesIO(content))


@pytest.mark.asyncio
async def test_file_upload_skips_duplicate_by_file_hash_and_workspace(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """重复文件默认应跳过，不污染知识库。"""

    duplicate = SimpleNamespace(
        id="22222222-2222-4222-8222-222222222222",
        source_id="file:existing",
        collection_name="upload_collection",
        version=1,
        chunk_count=3,
        ingest_status="completed",
        error_message=None,
        document_metadata={"filename": "old.txt"},
    )
    lifecycle = FakeLifecycleService()
    repository = FakeDocumentRepository(duplicate=duplicate)
    service = FileUploadService(
        settings=create_settings(tmp_path),
        lifecycle_service=lifecycle,  # type: ignore[arg-type]
        document_repository=repository,  # type: ignore[arg-type]
        parser_registry=FakeParserRegistry(),  # type: ignore[arg-type]
    )

    result = await service.upload_file(
        upload_file=create_upload_file(),
        workspace_id="workspace-a",
        user_id="user-a",
        collection_name="upload_collection",
        duplicate_strategy="skip",
    )

    assert result.skipped_duplicate is True
    assert result.source_id == "file:existing"
    assert result.chunk_count == 3
    assert lifecycle.calls == []


@pytest.mark.asyncio
async def test_file_upload_force_reingest_reuses_existing_source_id(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """force_reingest 应复用旧 source_id，让生命周期版本递增。"""

    duplicate = SimpleNamespace(
        id="22222222-2222-4222-8222-222222222222",
        source_id="file:existing",
        collection_name="upload_collection",
        version=1,
        chunk_count=1,
        ingest_status="completed",
        error_message=None,
        document_metadata={},
    )
    lifecycle = FakeLifecycleService()
    repository = FakeDocumentRepository(duplicate=duplicate)
    service = FileUploadService(
        settings=create_settings(tmp_path),
        lifecycle_service=lifecycle,  # type: ignore[arg-type]
        document_repository=repository,  # type: ignore[arg-type]
        parser_registry=FakeParserRegistry(),  # type: ignore[arg-type]
    )

    result = await service.upload_file(
        upload_file=create_upload_file(),
        workspace_id="workspace-a",
        user_id="user-a",
        collection_name="upload_collection",
        duplicate_strategy="force_reingest",
    )

    assert result.skipped_duplicate is False
    assert result.source_id == "file:existing"
    assert result.version == 2
    assert lifecycle.calls[0]["source_id"] == "file:existing"
    assert lifecycle.calls[0]["file_hash"] == result.file_hash
    assert repository.updated_metadata is not None
    assert repository.updated_metadata["ingest_status"] == "completed"

