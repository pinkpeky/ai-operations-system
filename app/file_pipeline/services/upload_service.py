"""文件上传导入服务。"""

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import Settings
from app.file_pipeline.parsers.registry import FileParserRegistry
from app.file_pipeline.services.text_cleaner import ExtractedTextCleaner
from app.models.document import Document
from app.repositories.document_repository import DocumentRepository
from app.services.document_lifecycle import DocumentLifecycleIngestResult, DocumentLifecycleService

logger = logging.getLogger(__name__)

DuplicateStrategy = Literal["skip", "force_reingest"]


@dataclass(frozen=True, slots=True)
class FileUploadResult:
    """文件上传导入结果。"""

    filename: str
    file_type: str
    file_size: int
    file_hash: str
    collection_name: str
    source_id: str
    document_id: str | None
    version: int | None
    chunk_count: int
    chunk_ids: list[str] = field(default_factory=list)
    ingest_status: str = "completed"
    ingest_error: str | None = None
    skipped_duplicate: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


class FileUploadService:
    """文件上传、解析、去重和知识库写入编排服务。"""

    def __init__(
        self,
        *,
        settings: Settings,
        lifecycle_service: DocumentLifecycleService,
        document_repository: DocumentRepository,
        parser_registry: FileParserRegistry | None = None,
        cleaner: ExtractedTextCleaner | None = None,
    ) -> None:
        self.settings = settings
        self.lifecycle_service = lifecycle_service
        self.document_repository = document_repository
        self.parser_registry = parser_registry or FileParserRegistry()
        self.cleaner = cleaner or ExtractedTextCleaner()

    async def upload_file(
        self,
        *,
        upload_file: UploadFile,
        workspace_id: str,
        user_id: str | None,
        collection_name: str | None,
        duplicate_strategy: DuplicateStrategy = "skip",
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ) -> FileUploadResult:
        """执行文件上传到 RAG 的完整流程。"""

        temp_path: Path | None = None
        filename = Path(upload_file.filename or "uploaded-file").name
        file_type = self._detect_file_type(filename)
        self._validate_file_type(file_type)
        if duplicate_strategy not in {"skip", "force_reingest"}:
            raise ValueError("duplicate_strategy must be skip or force_reingest")
        try:
            temp_path, file_size, file_hash = await self._save_temp_file(upload_file, suffix=f".{file_type}")
            active_duplicate = await self.document_repository.get_active_document_by_file_hash(
                file_hash=file_hash,
                workspace_id=workspace_id,
                collection_name=collection_name,
            )
            if active_duplicate is not None and duplicate_strategy == "skip":
                logger.info(
                    "File upload skipped duplicate",
                    extra={"upload_filename": filename, "file_hash": file_hash, "workspace_id": workspace_id},
                )
                return self._build_duplicate_result(
                    document=active_duplicate,
                    filename=filename,
                    file_type=file_type,
                    file_size=file_size,
                    file_hash=file_hash,
                )

            parsed = self.parser_registry.parse(path=temp_path, file_type=file_type)
            cleaned_text = self.cleaner.clean(parsed.text)
            source_id = active_duplicate.source_id if active_duplicate is not None else self._build_source_id(file_hash)
            metadata = {
                **parsed.metadata,
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size,
                "file_hash": file_hash,
                "ingest_status": "pending",
                "ingest_error": None,
                "chunk_count": 0,
                "upload_pipeline": "file_upload",
            }
            ingest_result = await self.lifecycle_service.ingest_text(
                text=cleaned_text,
                metadata=metadata,
                source_id=source_id,
                source_name=filename,
                source_type=file_type,
                workspace_id=workspace_id,
                user_id=user_id,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                file_hash=file_hash,
            )
            completed_metadata = {
                **metadata,
                "ingest_status": "completed",
                "ingest_error": None,
                "chunk_count": ingest_result.chunk_count,
            }
            await self.document_repository.update_document_metadata(
                document_id=ingest_result.document_id,
                metadata=completed_metadata,
            )
            await self.lifecycle_service.session.commit()
            return self._build_ingest_result(
                ingest_result=ingest_result,
                filename=filename,
                file_type=file_type,
                file_size=file_size,
                file_hash=file_hash,
                metadata=completed_metadata,
            )
        except Exception as exc:
            logger.exception("File upload pipeline failed", extra={"upload_filename": filename})
            raise
        finally:
            if temp_path is not None:
                self._cleanup_temp_file(temp_path)

    def _detect_file_type(self, filename: str) -> str:
        """从文件名扩展名识别文件类型。"""

        file_type = Path(filename).suffix.lower().lstrip(".")
        if not file_type:
            raise ValueError("Uploaded file must have an extension")
        return file_type

    def _validate_file_type(self, file_type: str) -> None:
        """校验文件类型是否允许。"""

        if file_type not in self.settings.allowed_file_type_set:
            raise ValueError(f"Unsupported file type: {file_type}")

    async def _save_temp_file(self, upload_file: UploadFile, *, suffix: str) -> tuple[Path, int, str]:
        """保存临时文件并计算原始文件 hash。"""

        temp_dir = Path(self.settings.upload_temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_path = temp_dir / f"{uuid4()}{suffix}"
        max_size = self.settings.max_upload_file_size_mb * 1024 * 1024
        file_hash = hashlib.sha256()
        file_size = 0
        try:
            with temp_path.open("wb") as handle:
                while True:
                    chunk = await upload_file.read(1024 * 1024)
                    if not chunk:
                        break
                    file_size += len(chunk)
                    if file_size > max_size:
                        raise ValueError(f"Uploaded file exceeds {self.settings.max_upload_file_size_mb} MB")
                    file_hash.update(chunk)
                    handle.write(chunk)
            if file_size == 0:
                raise ValueError("Uploaded file is empty")
            return temp_path, file_size, file_hash.hexdigest()
        except Exception:
            self._cleanup_temp_file(temp_path)
            raise

    def _cleanup_temp_file(self, path: Path) -> None:
        """清理临时文件。"""

        try:
            if path.exists():
                path.unlink()
                logger.debug("Temporary upload file removed", extra={"path": str(path)})
        except Exception:
            logger.warning("Failed to cleanup temporary upload file", extra={"path": str(path)}, exc_info=True)

    def _build_source_id(self, file_hash: str) -> str:
        """基于文件 hash 自动生成稳定 source_id。"""

        return f"file:{file_hash[:32]}"

    def _build_duplicate_result(
        self,
        *,
        document: Document,
        filename: str,
        file_type: str,
        file_size: int,
        file_hash: str,
    ) -> FileUploadResult:
        """构建重复文件跳过结果。"""

        metadata = {
            **document.document_metadata,
            "filename": filename,
            "file_type": file_type,
            "file_size": file_size,
            "file_hash": file_hash,
            "ingest_status": document.ingest_status,
            "ingest_error": document.error_message,
            "chunk_count": document.chunk_count,
        }
        return FileUploadResult(
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            file_hash=file_hash,
            collection_name=document.collection_name,
            source_id=document.source_id,
            document_id=str(document.id),
            version=document.version,
            chunk_count=document.chunk_count,
            chunk_ids=[],
            ingest_status=document.ingest_status,
            ingest_error=document.error_message,
            skipped_duplicate=True,
            metadata=metadata,
        )

    def _build_ingest_result(
        self,
        *,
        ingest_result: DocumentLifecycleIngestResult,
        filename: str,
        file_type: str,
        file_size: int,
        file_hash: str,
        metadata: dict[str, Any],
    ) -> FileUploadResult:
        """构建成功写入结果。"""

        return FileUploadResult(
            filename=filename,
            file_type=file_type,
            file_size=file_size,
            file_hash=file_hash,
            collection_name=ingest_result.collection_name,
            source_id=ingest_result.source_id,
            document_id=ingest_result.document_id,
            version=ingest_result.version,
            chunk_count=ingest_result.chunk_count,
            chunk_ids=ingest_result.chunk_ids,
            ingest_status="completed",
            ingest_error=None,
            skipped_duplicate=False,
            metadata=metadata,
        )
