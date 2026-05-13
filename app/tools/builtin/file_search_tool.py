"""文档元数据查询内置工具。"""

from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import DocumentStatus
from app.repositories.document_repository import DocumentRepository
from app.schemas.document import DocumentResponse
from app.tools.base import BaseTool, ToolExecutionContext


class FileSearchToolInput(BaseModel):
    """文件/文档查询工具输入。"""

    status: str | None = Field(default=None, description="文档状态过滤，默认不限制")
    source_id: str | None = Field(default=None, min_length=1, max_length=255, description="source_id 过滤")
    collection_name: str | None = Field(default=None, min_length=1, max_length=128, description="collection 过滤")
    limit: int = Field(default=20, ge=1, le=200, description="返回数量")


class FileSearchToolOutput(BaseModel):
    """文件/文档查询工具输出。"""

    items: list[dict[str, Any]]


class FileSearchTool(BaseTool):
    """查询 documents 表和 metadata 的工具。"""

    name = "file_search_tool"
    description = "List documents and metadata inside the current workspace."
    input_schema = FileSearchToolInput
    output_schema = FileSearchToolOutput
    permission_scopes = ["documents:read"]

    async def execute(self, tool_input: BaseModel, context: ToolExecutionContext) -> BaseModel:
        """按 workspace 查询文档元数据。"""

        request = FileSearchToolInput.model_validate(tool_input.model_dump())
        status = request.status
        if status is not None and status not in {item.value for item in DocumentStatus}:
            raise ValueError("status must be active, deleted, or outdated")
        repository = DocumentRepository(context.require_session())
        documents = await repository.list_documents(
            status=status,
            source_id=request.source_id,
            collection_name=request.collection_name,
            workspace_id=context.require_workspace(),
            limit=request.limit,
        )
        return FileSearchToolOutput(
            items=[DocumentResponse.from_model(document).model_dump(mode="json") for document in documents],
        )
