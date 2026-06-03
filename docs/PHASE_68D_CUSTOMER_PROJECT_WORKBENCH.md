# Phase 68D Customer Project Workbench

日期：2026-05-30

## 目标

Phase 68D 的目标是让客户机前端成为工作人员的日常运营入口，而不是继续把审批、素材导入、流选择、产出挑选分散在服务器后台或旧的内容草稿链路里。

本阶段不解决 ComfyUI 流库自动推荐算法，也不直接提交真实生成任务。它先把 68B/68C 已经落库的一线项目对象接入客户机，让工作人员能看到并处理完整项目闭环。

## 已落地范围

- `worker_console/src/api/commercialOperationClient.ts`
- `worker_console_desktop/src/api/commercialOperationClient.ts`
- `worker_console/src/main.tsx`
- `worker_console_desktop/src/main.tsx`
- `worker_console/src/styles.css`
- `worker_console_desktop/src/styles.css`
- `tests/test_worker_console_client_ux.py`

## 客户机 API 能力

客户机商业运营 client 已补齐以下对象的类型和调用方法：

- `OperationPlan`
- `ProjectMaterial`
- `ProductionTask`
- `WorkflowSelection`
- `OutputCandidate`
- `FinalSelection`
- `PublishPackage`
- `PlatformMetricSnapshot`
- `CommercialOperationMainAgentAdvance`

新增前端调用覆盖：

- `advanceMainAgentLoop`
- `listOperationPlans` / `decideOperationPlan`
- `createProjectMaterial` / `listProjectMaterials` / `decideProjectMaterial`
- `listProductionTasks` / `decideProductionTask`
- `createWorkflowSelection` / `listWorkflowSelections` / `decideWorkflowSelection`
- `listOutputCandidates` / `decideOutputCandidate`
- `createFinalSelection` / `listFinalSelections` / `decideFinalSelection`
- `listPublishPackages` / `decidePublishPackage`
- `listPlatformMetricSnapshots` / `decidePlatformMetricSnapshot`

## 客户机工作台行为

`ChatPanel` 内新增 `Phase 68D Customer Project Workbench`。

工作台会随运营项目刷新以下状态：

- 运营方案数量与最新审批状态
- 项目素材数量与待复核素材
- 生产任务数量与待审批任务
- ComfyUI 流选择数量与待确认流
- 候选产出数量与已选择产出
- 终选作品、发布包、平台数据快照状态

工作人员可执行的动作：

- 请求主 Agent 推进一个可审批项目步骤
- 批准或驳回 `OperationPlan`
- 登记客户机侧素材入口并进入素材复核
- 批准、开始、完成 `ProductionTask`
- 为任务记录一个待确认 ComfyUI 流选择
- 确认或驳回 `WorkflowSelection`
- 预览并选择 `OutputCandidate`
- 将被选择的候选产出生成 `FinalSelection`
- 批准终选作品
- 批准、准备、标记 `PublishPackage`
- 确认 `PlatformMetricSnapshot`

## 边界

- 客户机不绕过人工审批。
- 客户机不在本阶段自动提交 ComfyUI 真实生成任务。
- 客户机不在审批前执行 OpenClaw 或 Playwright 真实发布。
- `WorkflowSelection` 在 68D 只提供人工确认入口；真实流库推荐和验证属于 68E。
- `OutputCandidate` 的预览只渲染可被浏览器访问的图片、视频、音频 URL；本地 Windows 路径仍需要后续资产服务或静态文件映射。

## 验收

- Web 客户机和 Desktop 客户机均暴露项目工作台。
- 工作台能读取并展示 68B/68C 的一线项目对象。
- 工作台能调用主 Agent 推进方案/任务。
- 工作台能处理方案审批、任务审批、素材登记、流选择、候选产出挑选、终选审批、发布包状态和数据快照确认。
- `tests/test_worker_console_client_ux.py` 覆盖前端契约和文档标记。

## 下一步

Phase 68E：工作流库和流选择。

68E 需要把 ComfyUI RAG 文档、工作流节点图、输入素材要求、显存需求、预计耗时、验证状态整理成结构化候选流，让工作人员选择的不再是占位流，而是真实可解释、可追踪、可验证的流。
