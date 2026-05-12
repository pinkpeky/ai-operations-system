"""文件上传 API 数据模型。"""

from typing import Any, Literal

from pydantic import BaseModel, Field

DuplicateStrategy = Literal["skip", "force_reingest"]


class FileUploadResponse(BaseModel):
    """文件上传导入响应。"""

    filename: str
    file_type: str
    file_size: int
    file_hash: str
    collection_name: str
    source_id: str
    document_id: str | None = None
    version: int | None = None
    chunk_count: int
    chunk_ids: list[str] = Field(default_factory=list)
    ingest_status: str
    ingest_error: str | None = None
    skipped_duplicate: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
