# Phase 68B Operation Project Governance

日期：2026-05-30

## 目标

Phase 68B 把“运营项目”从单一商业运营记录补成可承载完整闭环的业务骨架。它不继续深挖某一个 ComfyUI 视频效果，而是先建立主 Agent、客户机前端、ComfyUI 工作流选择、候选产出、发布包和平台数据回流都能依赖的正式对象层。

本阶段完成后，一个运营目标可以被拆成方案、素材、文案/图片/影音生产任务、工作流选择、候选作品、最终作品、发布包和平台数据快照。后续 68C 主 Agent、68D 客户机工作台、68E 工作流库、68F 产出预览、68G 影音流都应挂到这些对象上。

## 新增数据库对象

- `commercial_operation_plans`：运营方案。记录方案版本、目标摘要、渠道策略、内容策略、生产范围、素材要求、KPI、发布时间表和审批状态。
- `commercial_operation_project_materials`：项目素材。记录场景图、参考视频、音频、品牌文档、人物授权等素材的来源、授权状态、标签、归属任务和审核状态。
- `commercial_operation_production_tasks`：生产任务。统一承载 `copy`、`image`、`media` 三类任务；`media` 内部通过 `media_subtype` 区分 `video`、`audio`、`audio_video`、`digital_human`、`postprocess`。
- `commercial_operation_workflow_selections`：工作流选择。记录 Agent 推荐或人工选择的 ComfyUI/其他工作流、输入要求、输出类型、推荐原因、预计耗时、预计显存和人工确认状态。
- `commercial_operation_output_candidates`：候选产出。记录每次生成的文案、图片、视频、音频或音视频候选作品，支持预览、质量检查和人工选择。
- `commercial_operation_final_selections`：最终选择。只有人工确认后的候选作品才进入最终选择，再进入发布文案和发布包阶段。
- `commercial_operation_publish_packages`：发布包。记录平台、账号引用、标题、正文、话题、封面、排期、发布 payload、发布状态和失败原因。
- `commercial_operation_platform_metric_snapshots`：平台数据快照。记录发布后的播放量、互动量、评论量、转化指标等手动或自动回收的数据。

迁移文件：`alembic/versions/20260530_0065_phase68b_operation_project_governance.py`。

## 后端对象

模型集中在 `app/models/commercial_operation.py`，枚举集中在 `app/models/enums.py`。新增模型已导出到 `app/models/__init__.py`，供测试、迁移和服务层统一注册。

核心状态枚举：

- `CommercialOperationPlanStatus`
- `CommercialOperationProjectMaterialStatus`
- `CommercialOperationProductionTaskStatus`
- `CommercialOperationWorkflowSelectionStatus`
- `CommercialOperationOutputCandidateStatus`
- `CommercialOperationFinalSelectionStatus`
- `CommercialOperationPublishPackageStatus`
- `CommercialOperationPlatformMetricSnapshotStatus`

## API 契约

新增接口都挂在 `/api/v1/commercial-operations/{operation_id}` 下，并继承 workspace 隔离。

- `POST /api/v1/commercial-operations/{operation_id}/operation-plans`、`GET /api/v1/commercial-operations/{operation_id}/operation-plans`、`POST /api/v1/commercial-operations/{operation_id}/operation-plans/{plan_id}/{action}`
- `POST /api/v1/commercial-operations/{operation_id}/project-materials`、`GET /api/v1/commercial-operations/{operation_id}/project-materials`、`POST /api/v1/commercial-operations/{operation_id}/project-materials/{material_id}/{action}`
- `POST /api/v1/commercial-operations/{operation_id}/production-tasks`、`GET /api/v1/commercial-operations/{operation_id}/production-tasks`、`POST /api/v1/commercial-operations/{operation_id}/production-tasks/{production_task_id}/{action}`
- `POST /api/v1/commercial-operations/{operation_id}/workflow-selections`、`GET /api/v1/commercial-operations/{operation_id}/workflow-selections`、`POST /api/v1/commercial-operations/{operation_id}/workflow-selections/{workflow_selection_id}/{action}`
- `POST /api/v1/commercial-operations/{operation_id}/output-candidates`、`GET /api/v1/commercial-operations/{operation_id}/output-candidates`、`POST /api/v1/commercial-operations/{operation_id}/output-candidates/{output_candidate_id}/{action}`
- `POST /api/v1/commercial-operations/{operation_id}/final-selections`、`GET /api/v1/commercial-operations/{operation_id}/final-selections`、`POST /api/v1/commercial-operations/{operation_id}/final-selections/{final_selection_id}/{action}`
- `POST /api/v1/commercial-operations/{operation_id}/publish-packages`、`GET /api/v1/commercial-operations/{operation_id}/publish-packages`、`POST /api/v1/commercial-operations/{operation_id}/publish-packages/{publish_package_id}/{action}`
- `POST /api/v1/commercial-operations/{operation_id}/platform-metric-snapshots`、`GET /api/v1/commercial-operations/{operation_id}/platform-metric-snapshots`、`POST /api/v1/commercial-operations/{operation_id}/platform-metric-snapshots/{snapshot_id}/{action}`

`action` 采用受控状态转移。计划、素材、流选择、最终选择、数据快照支持 `ready`、`approve`、`reject`、`archive`；生产任务额外支持 `start`、`block`、`complete`；候选产出支持 `select`；发布包支持 `prepare`、`publish`、`fail`。

## 服务层行为

`CommercialOperationService` 新增创建、列表、状态决策方法。服务层负责：

- 校验记录归属同一个 workspace 和 operation。
- 校验 `media` 生产任务必须提供 `media_subtype`。
- 校验工作流选择、候选产出、最终选择、发布包、数据快照的上游对象存在。
- 在审批、选择、开始、完成、发布、失败、归档时写入对应时间戳和操作者字段。
- 只记录业务状态，不执行真实 ComfyUI，不发布社媒，不调用 OpenClaw 或 Playwright。

## 闭环位置

Phase 68B 是 68C-68K 的后端承载层：

- 68C 主 Agent 应创建 `OperationPlan`，方案审批后派生 `ProductionTask`。
- 68D 客户机前端应围绕这些对象展示任务台、素材、审批、流选择、产出、发布、数据。
- 68E 工作流库应写入 `WorkflowSelection`，由人工最终确认。
- 68F 产出预览应写入 `OutputCandidate` 和 `FinalSelection`。
- 68G 影音流应使用 `ProductionTask(task_type=media)`，音频不再隐藏在视频备注中。
- 68H 客户机发布前应生成并审批 `PublishPackage`。
- 68I 平台数据回收应写入 `PlatformMetricSnapshot`。
- 68J 优化闭环应基于数据快照生成下一轮方案或生产任务。

## 验收

新增测试：`tests/test_operation_project_governance.py`。

测试覆盖一条可操作闭环：

1. 创建商业运营项目。
2. 创建运营方案并送审、审批。
3. 登记项目素材并审批。
4. 创建 `media/audio_video` 生产任务。
5. 登记并审批工作流选择。
6. 登记候选音视频产出并人工选择。
7. 创建并审批最终选择。
8. 创建发布包并标记发布成功。
9. 创建平台数据快照并审批。
10. 通过列表接口按状态过滤校验归属和状态。

本阶段验收命令：

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_operation_project_governance.py -q
.\.venv\Scripts\python.exe -m pytest tests\test_commercial_operations_docs.py -q
```

## 边界

Phase 68B 不修改 ComfyUI 工作流，不提交真实 ComfyUI 队列，不下载模型，不安装节点，不上传素材到 ComfyUI，不生成真实视频，不发布社媒，不控制真实账号，不运行 OpenClaw/Playwright，不绕过人工审批，不重启服务，不改运行时配置。

这一步的价值是把“能不能生成某个视频”上升为“运营项目能不能被完整管理”。视频、图片、文案和音频后续都应作为生产任务和候选产出进入同一套项目治理链路。
