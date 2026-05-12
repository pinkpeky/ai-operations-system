"""验证 docs 与当前 runtime / OpenAPI 是否一致。"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@dataclass(frozen=True, slots=True)
class CheckResult:
    """单项校验结果。"""

    level: str
    message: str


class DocsRuntimeVerifier:
    """Docs Runtime Verification 主类。"""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.docs = root / "docs"
        self.results: list[CheckResult] = []

    def run(self) -> int:
        """执行所有校验并输出结果。"""

        self.check_required_docs()
        self.check_runtime_config()
        self.check_openapi_and_api_docs()
        self.check_project_overview()
        self.check_phase_status()
        self.print_results()
        return 1 if any(result.level == "ERROR" for result in self.results) else 0

    def pass_(self, message: str) -> None:
        self.results.append(CheckResult("PASS", message))

    def warning(self, message: str) -> None:
        self.results.append(CheckResult("WARNING", message))

    def error(self, message: str) -> None:
        self.results.append(CheckResult("ERROR", message))

    def read_text(self, relative_path: str) -> str:
        path = self.root / relative_path
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            self.error(f"Missing file: {relative_path}")
            return ""

    def check_required_docs(self) -> None:
        """检查 Phase 10.5/11 docs 结构是否存在。"""

        required = [
            "docs/PROJECT_OVERVIEW.md",
            "docs/CURRENT_RUNTIME.md",
            "docs/zh/PROJECT_STATUS.md",
            "docs/zh/ARCHITECTURE.md",
            "docs/zh/API_REFERENCE.md",
            "docs/zh/DEPLOYMENT.md",
            "docs/zh/DEVELOPMENT_GUIDE.md",
            "docs/zh/DOCS_RUNTIME_VERIFICATION.md",
            "docs/en/PROJECT_STATUS.md",
            "docs/en/ARCHITECTURE.md",
            "docs/en/API_REFERENCE.md",
            "docs/en/DEPLOYMENT.md",
            "docs/en/DEVELOPMENT_GUIDE.md",
            "docs/en/DOCS_RUNTIME_VERIFICATION.md",
        ]
        missing = [path for path in required if not (self.root / path).exists()]
        if missing:
            for path in missing:
                self.error(f"Missing required docs file: {path}")
        else:
            self.pass_("Required zh/en docs structure exists")

    def check_runtime_config(self) -> None:
        """检查 CURRENT_RUNTIME 与 Settings / docker-compose 默认值是否一致。"""

        from app.core.config import Settings

        settings = Settings()
        current_runtime = self.read_text("docs/CURRENT_RUNTIME.md")
        compose = self.read_text("docker-compose.yml")
        expected_values = {
            "LLM_PROVIDER": settings.llm_provider,
            "LOCAL_LLM_MODEL": settings.local_llm_model,
            "EMBEDDING_PROVIDER": settings.embedding_provider,
            "LOCAL_EMBEDDING_MODEL": settings.local_embedding_model,
            "RERANKER_PROVIDER": settings.reranker_provider,
            "DEFAULT_SEARCH_MODE": settings.default_search_mode,
            "EMBEDDING_DIMENSION": str(settings.embedding_dimension),
            "MAX_UPLOAD_FILE_SIZE_MB": str(settings.max_upload_file_size_mb),
            "UPLOAD_TEMP_DIR": settings.upload_temp_dir,
            "ALLOWED_FILE_TYPES": settings.allowed_file_types,
        }
        for key, value in expected_values.items():
            if key not in current_runtime or str(value) not in current_runtime:
                self.error(f"CURRENT_RUNTIME.md does not document {key}={value}")
            else:
                self.pass_(f"CURRENT_RUNTIME documents {key}={value}")
            if key not in compose:
                self.error(f"docker-compose.yml does not expose {key}")
        if "MAX_UPLOAD_FILE_SIZE_MB" in compose and "ALLOWED_FILE_TYPES" in compose:
            self.pass_("docker-compose.yml exposes upload runtime settings")

    def check_openapi_and_api_docs(self) -> None:
        """检查真实 OpenAPI 路径是否已写入 API_REFERENCE。"""

        from app.main import create_app

        app = create_app()
        openapi = app.openapi()
        paths = set(openapi.get("paths", {}).keys())
        zh_api = self.read_text("docs/zh/API_REFERENCE.md")
        en_api = self.read_text("docs/en/API_REFERENCE.md")
        required_paths = [
            "/api/v1/health",
            "/api/v1/llm/health",
            "/api/v1/llm/test",
            "/api/v1/rag/embedding/health",
            "/api/v1/rag/ingest",
            "/api/v1/rag/search",
            "/api/v1/rag/debug",
            "/api/v1/files/upload",
            "/api/v1/reranker/health",
            "/api/v1/agentic-rag/query",
            "/api/v1/tasks",
            "/api/v1/documents",
            "/api/v1/rag/eval/runs",
        ]
        for path in required_paths:
            if path not in paths:
                self.error(f"OpenAPI path missing: {path}")
                continue
            self.pass_(f"OpenAPI contains {path}")
            if path not in zh_api:
                self.error(f"zh/API_REFERENCE.md does not document {path}")
            if path not in en_api:
                self.error(f"en/API_REFERENCE.md does not document {path}")
        for field in ("search_mode", "dense_top_k", "keyword_top_k", "final_top_k", "duplicate_strategy"):
            if field not in zh_api or field not in en_api:
                self.error(f"API_REFERENCE missing field: {field}")
            else:
                self.pass_(f"API_REFERENCE documents {field}")

    def check_project_overview(self) -> None:
        """检查项目入口文档是否记录关键架构。"""

        overview = self.read_text("docs/PROJECT_OVERVIEW.md")
        required_terms = [
            "Phase 11",
            "File Upload Pipeline",
            "Docs Runtime Verification",
            "PDF",
            "DOCX",
            "TXT",
            "MD",
            "CSV",
            "Dense + Keyword",
            "Reranker",
        ]
        for term in required_terms:
            if term not in overview:
                self.error(f"PROJECT_OVERVIEW.md missing term: {term}")
            else:
                self.pass_(f"PROJECT_OVERVIEW documents {term}")

    def check_phase_status(self) -> None:
        """检查中英文状态文档是否声明 Phase 11。"""

        zh_status = self.read_text("docs/zh/PROJECT_STATUS.md")
        en_status = self.read_text("docs/en/PROJECT_STATUS.md")
        for name, text in (("zh", zh_status), ("en", en_status)):
            if not re.search(r"Phase\s+11", text):
                self.error(f"{name}/PROJECT_STATUS.md missing Phase 11")
            elif "File Upload" not in text or "Docs Runtime Verification" not in text:
                self.error(f"{name}/PROJECT_STATUS.md does not describe Phase 11 scope")
            else:
                self.pass_(f"{name}/PROJECT_STATUS documents Phase 11")

    def print_results(self) -> None:
        """输出 PASS / WARNING / ERROR。"""

        for result in self.results:
            print(f"{result.level}: {result.message}")
        errors = sum(1 for result in self.results if result.level == "ERROR")
        warnings = sum(1 for result in self.results if result.level == "WARNING")
        if errors:
            print(f"SUMMARY: ERROR ({errors} errors, {warnings} warnings)")
        elif warnings:
            print(f"SUMMARY: WARNING ({warnings} warnings)")
        else:
            print("SUMMARY: PASS")


def main(argv: Iterable[str] | None = None) -> int:
    """命令行入口。"""

    _ = list(argv or [])
    return DocsRuntimeVerifier(ROOT).run()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
