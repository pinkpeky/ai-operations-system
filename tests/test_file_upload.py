"""文件上传 API 测试。"""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import files as file_routes
from app.core.errors import AppError, app_error_handler
from app.db.postgres import get_session
from app.file_pipeline.services.upload_service import FileUploadResult
from app.middleware.workspace_middleware import WorkspaceContextMiddleware


class FakeFileUploadService:
    """文件上传服务替身。"""

    async def upload_file(self, **kwargs):  # type: ignore[no-untyped-def]
        return FileUploadResult(
            filename=kwargs["upload_file"].filename,
            file_type="txt",
            file_size=11,
            file_hash="hash-1",
            collection_name=kwargs["collection_name"] or "default_collection",
            source_id="file:hash-1",
            document_id="11111111-1111-4111-8111-111111111111",
            version=1,
            chunk_count=1,
            chunk_ids=["point-1"],
            ingest_status="completed",
            metadata={"filename": kwargs["upload_file"].filename},
        )


def create_client() -> TestClient:
    """创建只挂载 files route 的测试应用。"""

    app = FastAPI()
    app.add_middleware(WorkspaceContextMiddleware)
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(file_routes.router, prefix="/api/v1")

    async def fake_get_session():  # type: ignore[no-untyped-def]
        yield object()

    app.dependency_overrides[get_session] = fake_get_session
    return TestClient(app)


def test_file_upload_api_accepts_multipart(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """文件上传 API 应支持 multipart/form-data。"""

    monkeypatch.setattr(
        file_routes,
        "create_file_upload_service",
        lambda settings, session, collection_name: FakeFileUploadService(),
    )
    client = create_client()

    response = client.post(
        "/api/v1/files/upload",
        headers={"X-Workspace-Id": "workspace-file", "X-User-Id": "user-file"},
        files={"file": ("demo.txt", b"hello upload", "text/plain")},
        data={
            "collection_name": "file_collection",
            "duplicate_strategy": "skip",
            "chunk_size": "100",
            "chunk_overlap": "10",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["filename"] == "demo.txt"
    assert body["collection_name"] == "file_collection"
    assert body["source_id"] == "file:hash-1"
    assert body["ingest_status"] == "completed"


def test_file_upload_api_requires_workspace_header(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """上传文件必须携带 workspace header。"""

    monkeypatch.setattr(
        file_routes,
        "create_file_upload_service",
        lambda settings, session, collection_name: FakeFileUploadService(),
    )
    client = create_client()

    response = client.post(
        "/api/v1/files/upload",
        files={"file": ("demo.txt", b"hello upload", "text/plain")},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "X-Workspace-Id header is required"

