# Docs Runtime Verification

更新时间：2026-05-12

本文说明如何验证 docs 与当前 runtime 是否一致。

## 目标

Docs Runtime Verification 的目标是防止：

- API 已新增但 API_REFERENCE 没更新。
- config 默认值变了但 CURRENT_RUNTIME 没更新。
- docker-compose 环境变量和 config 不一致。
- Phase 状态写错。
- File Upload Pipeline 已实现但 docs 没同步。
- docs 写了当前代码不存在的能力。

## 运行方式

在项目根目录执行：

```powershell
python scripts/verify_docs_runtime.py
```

通过时输出示例：

```text
PASS: required docs files exist
PASS: CURRENT_RUNTIME contains config defaults
PASS: OpenAPI exposes required paths
PASS: API_REFERENCE includes required paths and fields
PASS: PROJECT_OVERVIEW includes current architecture markers
PASS: Phase 11 status is documented
SUMMARY: PASS
```

## 输出级别

`PASS`：

- 检查项通过。

`WARNING`：

- 有潜在不一致，需要人工确认。

`ERROR`：

- 必须修复。
- 脚本以非 0 状态退出。

## 当前检查范围

脚本读取：

- `app/core/config.py`
- `docker-compose.yml`
- FastAPI OpenAPI schema
- `docs/CURRENT_RUNTIME.md`
- `docs/PROJECT_OVERVIEW.md`
- `docs/zh/API_REFERENCE.md`
- `docs/en/API_REFERENCE.md`
- `docs/zh/PROJECT_STATUS.md`
- `docs/en/PROJECT_STATUS.md`

脚本检查：

- provider 默认值。
- search 默认值。
- embedding dimension。
- upload 配置。
- required API path。
- `search_mode`、`dense_top_k`、`keyword_top_k`、`final_top_k`、`duplicate_strategy`。
- Phase 11 状态。

## Docs Sync 规则

新增 API 时：

1. 更新 route。
2. 更新 schema。
3. 更新 tests。
4. 更新 zh/en API_REFERENCE。
5. 运行 verifier。

新增配置时：

1. 更新 `app/core/config.py`。
2. 更新 `.env.example`。
3. 更新 `docker-compose.yml`。
4. 更新 `docs/CURRENT_RUNTIME.md`。
5. 更新 zh/en DEPLOYMENT。
6. 运行 verifier。

新增 Phase 时：

1. 更新 `docs/PROJECT_OVERVIEW.md`。
2. 更新 zh/en PROJECT_STATUS。
3. 更新 zh/en ARCHITECTURE。
4. 更新 zh/en API_REFERENCE。
5. 更新 zh/en DEPLOYMENT。
6. 更新 zh/en DEVELOPMENT_GUIDE。
7. 更新 Word 文档。
8. 运行 pytest、docker、docs verifier。

## 与测试的关系

`tests/test_docs_runtime_verification.py` 会调用：

```powershell
python scripts/verify_docs_runtime.py
```

因此 docs 漂移会导致 pytest 失败。

## 当前边界

该脚本是轻量级一致性检查，不替代：

- 完整 API 契约测试。
- 数据库 migration 校验。
- Docker 真实 smoke test。
- 安全审计。
- 性能测试。

它的职责是让 docs 不落后于 runtime。
