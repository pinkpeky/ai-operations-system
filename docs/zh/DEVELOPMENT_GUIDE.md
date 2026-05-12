# 开发指南

更新时间：2026-05-12

本文用于后续 Codex 对话和开发者继续迭代项目。

## 基本原则

- 不修改 Scheduler 核心逻辑，除非阶段明确要求。
- 不修改 TaskExecutor 核心逻辑，除非阶段明确要求。
- RAG、LLM、Reranker、File Upload 都保持独立服务层。
- Workspace Isolation 不能被绕过。
- 不写不存在的功能到 docs。
- 每个 Phase 完成后必须同步 docs。

## 代码分层约定

API：

- 放在 `app/api/routes/`。
- 只做请求解析、依赖注入、错误转换。
- 业务逻辑下沉到 service。

Service：

- 放在 `app/services/` 或特定领域目录如 `app/file_pipeline/services/`。
- 负责业务流程编排。

Repository：

- 放在 `app/repositories/`。
- 负责数据库查询和更新。

Provider：

- LLM provider 在 `app/agents/providers/`。
- Embedding provider 在 `app/rag/providers/`。
- Reranker provider 在 `app/reranker/providers/`。

Schema：

- 放在 `app/schemas/`。
- API request/response 必须显式定义。

Tests：

- 放在 `tests/`。
- 单元测试不依赖真实 Ollama。
- Docker smoke test 可以验证真实容器服务。

## File Upload Pipeline 开发规则

文件上传相关代码：

```text
app/file_pipeline/
  parsers/
  services/
app/api/routes/files.py
app/schemas/file.py
```

规则：

- Parser 只负责提取文本，不做 embedding。
- Text cleaner 只做清洗，不做 chunk。
- Upload service 负责文件保存、hash、重复检测、parser 调度、调用 DocumentLifecycle。
- DocumentLifecycle 仍是唯一负责创建 document/chunk/Qdrant 写入的入口。
- 新增文件类型时必须新增 parser 测试。
- 不支持的格式不能写进 API_REFERENCE。

## Docs-as-Code 规则

docs 是项目 Single Source of Truth。

每个 Phase 完成后必须更新：

- `docs/PROJECT_OVERVIEW.md`
- `docs/CURRENT_RUNTIME.md`
- `docs/zh/PROJECT_STATUS.md`
- `docs/zh/ARCHITECTURE.md`
- `docs/zh/API_REFERENCE.md`
- `docs/zh/DEPLOYMENT.md`
- `docs/zh/DEVELOPMENT_GUIDE.md`
- `docs/en/*`
- `docs/Aiops Project Documentation Update Request For Codex.docx`

新增 API 时必须同步：

- API path。
- method。
- request JSON 或 form fields。
- response JSON。
- required headers。
- workspace requirements。
- debug fields。
- production / experimental / planned 状态。

新增配置时必须同步：

- `app/core/config.py`
- `.env.example`
- `docker-compose.yml`
- `docs/CURRENT_RUNTIME.md`
- `docs/zh/DEPLOYMENT.md`
- `docs/en/DEPLOYMENT.md`

## Docs Runtime Verification 流程

运行：

```powershell
python scripts/verify_docs_runtime.py
```

脚本检查：

- config 默认值。
- docker-compose 环境变量。
- FastAPI OpenAPI routes。
- `CURRENT_RUNTIME.md`。
- `PROJECT_OVERVIEW.md`。
- zh/en API_REFERENCE。
- Phase 状态。
- File Upload Pipeline 字段。

通过标准：

```text
SUMMARY: PASS
```

如果失败：

1. 阅读 `ERROR`。
2. 判断是代码缺失还是 docs 过期。
3. 修复对应文件。
4. 重新运行 verifier。

## 固定交付流程

每次完成一个阶段后必须执行：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

推荐 smoke test：

- `GET /api/v1/health`
- `POST /api/v1/files/upload`
- `POST /api/v1/rag/search`
- `POST /api/v1/agentic-rag/query`

## 测试策略

必须保持：

- 单元测试不依赖真实外部模型。
- LocalProvider / LocalEmbeddingProvider 使用 mock HTTP client 测试。
- 文件 parser 测试使用小型内存样例或 fake reader。
- Workspace isolation 必须覆盖不同 workspace 无法互查。
- Docs verifier 必须作为测试的一部分。

## 当前不要做的事

- 不接真实 reranker。
- 不接 Elasticsearch / OpenSearch。
- 不做 OCR。
- 不支持 PPTX / XLSX / 图片。
- 不接 Browser Agent / OpenClaw / Playwright。
- 不做完整 RBAC / JWT / OAuth。
- 不修改 Scheduler 核心逻辑。
- 不修改 TaskExecutor 核心逻辑。
