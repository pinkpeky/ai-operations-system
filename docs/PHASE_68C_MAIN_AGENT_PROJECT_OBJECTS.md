# Phase 68C Main Agent Project Objects

日期：2026-05-30

## 目标

Phase 68C 让 `commercial_operation_agent` 正式接入 Phase 68B 的项目对象。主 Agent 不再只返回“下一步建议”，而是在 `advance-loop` 中写入可审批、可追踪、可被客户机前端展示的业务对象。

本阶段只推进项目对象和人工审批链路，不执行 ComfyUI，不生成真实媒体，不发布社媒，不运行 OpenClaw/Playwright。

## 新行为

`POST /api/v1/commercial-operations/{operation_id}/main-agent/advance-loop` 的 `operation_strategy` 轨道现在会执行两步：

1. 当项目没有一级运营方案时，创建 `OperationPlan`，并置为 `ready_for_review`。
2. 当 `OperationPlan` 被人工批准后，按方案的 `production_scope` 派生 `ProductionTask`，并置为 `ready_for_review`。

主 Agent 仍然不会自动审批。方案和生产任务都必须由工作人员确认后才能进入后续内容、图片、影音、工作流选择或发布链路。

## 方案生成

主 Agent 创建的 `OperationPlan` 包含：

- `objective_summary`：来自运营项目目标。
- `audience_strategy`：来自目标人群。
- `channel_strategy`：按渠道生成主/辅渠道策略，并标记发布包审批边界。
- `content_strategy`：记录内容模式、媒体类型、人工审批边界和运行时边界。
- `production_scope`：后续要派生的生产任务清单。
- `material_requirements`：品牌文档、场景图、参考音频等可选素材要求。
- `kpis`：来自 `success_metrics`，没有指标时使用默认审批/产出指标。
- `publish_schedule`：草稿状态的发布排期要求。
- `risk_notes`：明确人工审批、ComfyUI、客户机发布、平台数据回收边界。

## 任务派生

方案批准后，主 Agent 从 `production_scope` 创建 `ProductionTask`。

任务类型：

- `copy`：文案任务，默认分配给 `text_content_agent`，不要求工作流选择。
- `image`：图片/海报/首帧任务，默认分配给 `visual_asset_agent`，要求工作流选择。
- `media`：影音任务，默认 `media_subtype=audio_video`，分配给 `video_content_agent`，要求工作流选择。

对于 Douyin、KTV、短视频、音乐、音频、视频等目标，默认方案会同时生成 `copy`、`image`、`media(audio_video)` 三类任务。对于纯文本或邮件运营，默认至少生成 `copy` 任务。

## Loop Summary 变化

`operation-loop` 的 `task_planning` 阶段不再只看旧的 `plan_outline`。新项目会按以下状态推进：

- 没有 `OperationPlan`：`task_planning=missing`，主 Agent 下一步是生成方案。
- 有 `OperationPlan(ready_for_review)`：`task_planning=review_required`，等待人工审批。
- 有 `OperationPlan(approved)` 但没有生产任务：`task_planning=in_progress`，主 Agent 下一步派生任务。
- 有已批准方案和生产任务：`task_planning=complete`。

为了兼容历史项目，如果项目已经存在旧的内容草稿、素材请求、交付物、执行请求、结果、监控或优化记录，但没有新的 `OperationPlan`，`task_planning` 会视为 `complete`。新项目和下一轮优化仍应使用一级方案和生产任务。

## 与旧闭环关系

旧闭环记录继续保留：

- `CommercialOperationApproval`
- `CommercialOperationContentDraft`
- `CommercialOperationAssetRequest`
- `CommercialOperationDeliverable`
- `CommercialOperationExecutionRequest`
- `CommercialOperationExecutionRun`
- `CommercialOperationResult`
- `CommercialOperationMonitoringObservation`
- `CommercialOperationOptimizationDecision`

Phase 68C 不是删除旧链路，而是在旧链路前面补上更强的项目治理层。后续 68D 客户机前端和 68E 工作流选择应优先围绕 `OperationPlan`、`ProductionTask`、`WorkflowSelection`、`OutputCandidate`、`FinalSelection`、`PublishPackage` 展示。

## 验收

新增/更新测试：

- `tests/test_commercial_operation_main_agent_advance.py`
- `tests/test_commercial_operations_api.py`

覆盖点：

1. 没有知识库的项目也会先生成 `OperationPlan`，批准方案并派生任务后，才在知识阶段被 `knowledge_source_missing` 阻塞。
2. 有知识库的项目会先生成方案，方案批准后派生生产任务，再进入知识审批 gate。
3. KTV/Douyin/视频目标会从批准方案派生 `copy`、`image`、`media(audio_video)` 三类任务。
4. 旧 API 闭环保持可用；已有下游记录的历史项目不会被新 `task_planning` 阶段卡死。

验证命令：

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_commercial_operation_main_agent.py tests\test_commercial_operation_main_agent_advance.py -q
.\.venv\Scripts\python.exe -m pytest tests\test_commercial_operations_api.py tests\test_operation_project_governance.py tests\test_commercial_operation_main_agent_advance.py -q
```

## 边界

Phase 68C 不自动审批 `OperationPlan` 或 `ProductionTask`，不调用 ComfyUI，不提交队列，不修改工作流 JSON，不下载模型，不上传素材，不生成真实图片/视频/音频，不发布社媒，不控制账号，不运行 OpenClaw/Playwright，不拉取真实平台数据，不绕过人工审批。

下一阶段应进入 Phase 68D：客户机主工作台。客户机前端需要把 68B/68C 的方案、任务、素材、审批、流选择、候选产出、发布包和数据快照变成工作人员可操作的简洁界面。
