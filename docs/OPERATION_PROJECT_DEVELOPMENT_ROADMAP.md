# 运营项目闭环开发节奏规划

日期：2026-05-30

## 总原则

开发顺序不能继续围绕单个视频效果推进。当前更重要的是把“运营项目”作为主对象补完整，让文案、图片、影音、流选择、产出预览、审批、发布、数据回收都挂到同一条项目闭环上。

开发节奏采用“长步骤、可验收”的方式：每一阶段结束后都必须能被前端或 API 实际操作，而不是只新增底层表或零散接口。

## 开发边界

1. 客户机前端是工作人员主工作台。
2. 服务器前端是管理员和维护人员控制台。
3. 所有业务审批、素材导入、流选择、候选产出预览、最终选择、发布包确认都应在客户机前端完成。
4. 服务器前端负责 ComfyUI、模型、队列、工作流库、客户机状态、异常恢复和审计。
5. Agent 可以推荐方案和流，但不能绕过人工审批。
6. ComfyUI 工作流选择必须结构化、可解释、可追溯。
7. 音频必须作为影音流的一等能力，不应隐藏在视频备注里。

## 阶段 68B：运营项目核心对象

目标：先补后端业务骨架，让项目可以承载完整闭环。

新增或改造对象：

- `OperationPlan`：运营方案。
- `ProjectMaterial`：项目素材。
- `ProductionTask`：生产任务，类型包括 `copy`、`image`、`media`。
- `WorkflowSelection`：流选择记录。
- `OutputCandidate`：候选产出。
- `FinalSelection`：最终选择。
- `PublishPackage`：发布包。
- `PlatformMetricSnapshot`：平台数据快照。

主要文件：

- `app/models/commercial_operation.py` 或拆分新的项目模型文件。
- `app/schemas/commercial_operation.py` 或拆分新的项目 schema 文件。
- `app/commercial_operations/service.py` 或新增项目服务模块。
- `app/api/routes/commercial_operations.py` 或新增项目路由。
- `alembic/versions/*_operation_project_governance.py`
- `tests/test_operation_project_governance.py`

验收标准：

- 能创建运营方案并提交审批。
- 能上传或登记项目素材。
- 能从方案生成文案、图片、影音生产任务。
- 能登记流选择、候选产出、最终选择和发布包。
- 所有对象都有项目归属、状态、元数据、审计时间。
- 不要求真实调用 ComfyUI，不要求真实发布。

## 阶段 68C：主 Agent 接入新对象

目标：让主 Agent 不再只生成松散建议，而是生成可执行的项目对象。

工作内容：

- 输入运营主题后生成 `OperationPlan`。
- 方案审批通过后派生 `ProductionTask`。
- 根据任务类型推荐需要的流，但不自动确认。
- 主 Agent 的 next action 应指向具体对象，例如“等待方案审批”“等待流选择”“等待候选产出终选”。

主要文件：

- `app/commercial_operations/main_agent.py`
- `app/commercial_operations/service.py`
- `app/schemas/commercial_operation.py`
- `tests/test_commercial_operation_main_agent_advance.py`
- `tests/test_commercial_operation_main_agent.py`

验收标准：

- 主 Agent 能从一个运营目标生成方案草稿。
- 方案通过后能生成 `copy/image/media` 任务。
- Agent 输出不直接提交 ComfyUI、不发布、不绕过审批。

## 阶段 68D：客户机主工作台

目标：客户机成为工作人员真正入口。

客户机主导航：

1. 任务台
2. 素材
3. 审批
4. 流选择
5. 产出
6. 发布
7. 数据

主要文件：

- `worker_console/src/main.tsx`
- `worker_console_desktop/src/main.tsx`
- `worker_console/src/api/commercialOperationClient.ts`
- `worker_console_desktop/src/api/commercialOperationClient.ts`
- `tests/test_worker_console_client_ux.py`
- `tests/test_worker_console_desktop_docs.py`

验收标准：

- 工作人员能从客户机创建运营任务。
- 能导入素材并看到解析/归属/状态。
- 能看到所有待审批项。
- 能看到待选择的流。
- 能看到候选产出预览入口。
- 首页只显示当前项目、下一步、待审批、待选择流、最新产出、发布状态和一个主操作。

## 阶段 68E：工作流库和流选择

目标：让 Agent 推荐流、工作人员选择流，且选择过程可解释。

工作内容：

- 建立结构化工作流库。
- 从 ComfyUI RAG 文档提取候选流信息。
- 支持输出类型：`image`、`video`、`audio`、`audio_video`、`postprocess`。
- 为每个生产任务生成候选流列表。
- 客户机前端展示候选流卡片。

候选流卡片应展示：

- 工作流名称。
- 适合项目。
- 输入素材要求。
- 输出类型。
- 推荐原因。
- 预计耗时。
- 显存需求。
- 风险提示。
- 当前服务器是否验证可运行。

主要文件：

- `app/comfyui_runtime/workflow_materializer.py`
- `app/commercial_operations/service.py`
- `app/api/routes/commercial_operations.py`
- `worker_console/src/main.tsx`
- `worker_console_desktop/src/main.tsx`
- `tests/test_comfyui_workflow_materializer.py`
- `tests/test_commercial_operations_api.py`

验收标准：

- 客户机能看到每个任务的候选流。
- 工作人员能选择、驳回或要求换流。
- 选择结果写入 `WorkflowSelection`。
- 服务器前端只维护流库和运行状态，不承担普通工作人员选择动作。

## 阶段 68F：候选产出预览和最终选择

目标：所有生成结果先进入候选池，不能默认成为最终作品。

工作内容：

- 将图片、视频、音频、音视频组合产出统一登记为 `OutputCandidate`。
- 客户机前端支持图片预览、视频播放、音频播放、文案预览、发布包预览。
- 工作人员可选择最终作品或提交返工意见。
- 最终选择写入 `FinalSelection`。

主要文件：

- `app/models/output_artifact.py`
- `app/models/commercial_operation.py`
- `app/services/output_artifact_service.py`
- `worker_console/src/main.tsx`
- `worker_console_desktop/src/main.tsx`
- `tests/test_output_artifact_frontend.py`
- `tests/test_worker_console_client_ux.py`

验收标准：

- 每个候选产出可追踪来源任务和使用的流。
- 客户机可以预览候选作品。
- 只有人工终选的作品可以进入发布文案和发布包。

## 阶段 68G：影音流和音频 ComfyUI 链路

目标：把音频正式纳入影音流。

工作内容：

- 统一 `media` 任务，内部区分 `video`、`audio`、`audio_video`。
- 支持音频 ComfyUI 工作流登记和选择。
- 支持音频候选产出。
- 支持音视频合成关系。
- 支持最终混音确认。

主要文件：

- `app/comfyui_runtime/service.py`
- `app/schemas/comfyui_runtime.py`
- `app/api/routes/comfyui_runtime.py`
- `app/commercial_operations/service.py`
- `tests/test_comfyui_runtime_contract.py`
- `tests/test_commercial_operations_api.py`

验收标准：

- 音频任务和视频任务同属影音流。
- 音频候选能在客户机预览。
- 音频可以单独发布，也可以绑定到视频发布包。

## 阶段 68H：发布包和客户机执行准备

目标：真实发布前先形成可审批发布包。

工作内容：

- `PublishPackage` 绑定最终作品、平台、账号、标题、正文、话题、封面、发布时间和风险提示。
- 客户机前端展示完整发布包。
- 发布包审批通过后，客户机才生成 OpenClaw / Playwright 执行请求。
- 第一阶段只做 dry-run 或受控执行准备，不直接扩大到全平台自动发布。

主要文件：

- `app/openclaw/service.py`
- `app/browser/remote/services/browser_worker_service.py`
- `worker_client/openclaw/runtime.py`
- `worker_client/browser_runtime/playwright_provider.py`
- `worker_console/src/main.tsx`
- `worker_console_desktop/src/main.tsx`
- `tests/test_openclaw_worker_runtime.py`
- `tests/test_remote_worker_playwright_flow.py`

验收标准：

- 客户机只接收已审批发布包。
- 发布执行有明确状态和失败原因。
- 执行结果能回填到服务器。

## 阶段 68I：平台数据回收

目标：发布后按项目回收数据。

工作内容：

- 先定义抖音数据快照结构。
- 支持人工补录和自动 connector 两种入口。
- 每日按项目生成 `PlatformMetricSnapshot`。
- 快照汇总为 `MonitoringObservation`。

主要文件：

- `app/models/commercial_operation.py`
- `app/services/scheduler.py`
- `app/api/routes/commercial_operations.py`
- `worker_console/src/main.tsx`
- `worker_console_desktop/src/main.tsx`

验收标准：

- 每个发布作品能看到播放量、互动量、评论量、转化指标等数据快照。
- 数据来源可区分人工补录和自动拉取。
- 数据可以进入优化分析。

## 阶段 68J：优化决策和下一轮派生

目标：形成真正闭环。

工作内容：

- 根据数据快照生成优化建议。
- 人工审批优化建议。
- 审批后派生下一轮 `OperationPlan` 修订或新的 `ProductionTask`。
- 保留上一轮和下一轮关系。

主要文件：

- `app/commercial_operations/main_agent.py`
- `app/commercial_operations/service.py`
- `worker_console/src/main.tsx`
- `worker_console_desktop/src/main.tsx`
- `tests/test_commercial_operation_main_agent_advance.py`

验收标准：

- 数据能驱动下一轮任务。
- 下一轮任务能保留来源指标和优化原因。
- 工作人员可审批后继续执行。

## 阶段 68K：服务器前端收敛

目标：让服务器端从复杂操作台变成维护控制台。

服务器主导航：

1. 项目监控
2. ComfyUI
3. 工作流库
4. 客户机
5. 数据回收
6. 审计
7. 设置

工作内容：

- 保留管理员需要的资源、队列、模型、异常和审计。
- 将普通工作人员审批、素材导入、流选择、产出预览迁移到客户机前端。
- 降低 `admin_dashboard/src/main.tsx` 的业务操作密度。

验收标准：

- 服务器前端能定位故障和资源问题。
- 工作人员无需进入服务器前端完成日常运营。

## 推荐执行顺序

必须按以下顺序推进：

1. 68B：运营项目核心对象。
2. 68C：主 Agent 接入新对象。
3. 68D：客户机主工作台。
4. 68E：工作流库和流选择。
5. 68F：候选产出预览和最终选择。
6. 68G：影音流和音频 ComfyUI 链路。
7. 68H：发布包和客户机执行准备。
8. 68I：平台数据回收。
9. 68J：优化决策和下一轮派生。
10. 68K：服务器前端收敛。

不建议跳过 68B 直接做前端。没有后端一级对象，客户机前端只能继续拼接旧接口，后续返工成本会更高。

## Phase 68B 当前落地记录

本次开发已按推荐顺序先完成 68B 后端承载层，没有跳到视频效果或前端细节。

已落地内容：

- 新增 `OperationPlan`、`ProjectMaterial`、`ProductionTask`、`WorkflowSelection`、`OutputCandidate`、`FinalSelection`、`PublishPackage`、`PlatformMetricSnapshot` 对应数据库表、模型、Schema、Service 和 API。
- `ProductionTask` 统一文案、图片、影音任务；影音任务通过 `media_subtype` 区分 `video`、`audio`、`audio_video`、`digital_human`、`postprocess`。
- 素材、方案、生产任务、流选择、候选作品、最终选择、发布包、平台数据快照均具备项目归属、workspace 隔离、状态、元数据和人工决策入口。
- 发布包支持 `ready`、`approve`、`prepare`、`publish`、`fail`、`reject`、`archive` 状态；失败时记录 `failure_reason`。
- 平台数据快照支持手动或连接器来源，后续可作为优化闭环输入。

验收记录：

- `tests/test_operation_project_governance.py` 覆盖从运营方案到平台数据快照的一条完整 API 闭环。
- 详细设计与边界见 `docs/PHASE_68B_OPERATION_PROJECT_GOVERNANCE.md`。

下一步严格进入 68C：主 Agent 接入这些新对象，让 Agent 输出不再停留在松散建议，而是能创建方案、派生生产任务并等待人工审批。

## Phase 68C 当前落地记录

本次开发已完成 68C 主 Agent 接入项目对象。

已落地内容：

- `advance_main_agent_loop()` 的 `operation_strategy` 轨道不再 `noop`，会创建 `OperationPlan` 并进入 `ready_for_review`。
- `OperationPlan` 经人工批准后，主 Agent 会根据 `production_scope` 派生 `ProductionTask`，并进入 `ready_for_review`。
- Douyin、KTV、视频、音乐、音频等目标会默认派生 `copy`、`image`、`media(audio_video)` 三类任务；纯文本项目至少派生 `copy`。
- `operation-loop` 的 `task_planning` 阶段改为读取一级 `OperationPlan` 和 `ProductionTask`，不再只依赖旧 `plan_outline`。
- 为历史项目保留兼容：如果旧链路已有内容、交付、执行、结果、监控或优化记录，即使没有一级 `OperationPlan`，也不会被新的 `task_planning` 阶段卡死。

验收记录：

- `tests/test_commercial_operation_main_agent_advance.py` 覆盖方案生成、方案审批后派生任务、KTV/Douyin 派生 copy/image/media 三任务。
- `tests/test_commercial_operations_api.py` 已更新初始 loop 预期，确认新项目第一站是 `task_planning`。
- 详细设计与边界见 `docs/PHASE_68C_MAIN_AGENT_PROJECT_OBJECTS.md`。

下一步严格进入 68D：客户机主工作台，让工作人员能在客户机前端完成项目创建、方案审批、任务审批、素材导入、流选择、产出预览和发布包确认。
