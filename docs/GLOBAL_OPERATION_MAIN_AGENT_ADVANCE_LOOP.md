# 全局运营主 Agent 闭环推进实现记录

更新日期：2026-05-28

本文记录本阶段新增的“主 Agent 闭环推进器”。它的目标不是替代各个业务 API，而是把已有的运营记录串起来，让 `commercial_operation_agent` 可以根据当前闭环状态创建下一步可审阅产物，并在审批、客户机执行、外部运行时边界前停住。

## 本阶段目标

上一阶段主 Agent 已经能做全局路由：

```text
operation -> loop summary -> routing decision -> specialist track -> executable contract
```

但它仍然只是“告诉系统下一步应该做什么”。本阶段新增的是安全推进动作：

```text
POST /api/v1/commercial-operations/{operation_id}/main-agent/advance-loop
```

它会读取当前 operation loop 和 Agent/Skill orchestration，然后只做一个动作：

1. 如果缺前置条件，返回 `blocked`。
2. 如果已有待审记录，返回 `reused`，避免重复创建。
3. 如果可以推进，创建或更新一个 metadata-only / reviewable 记录。
4. 如果 `dry_run=true`，只返回计划创建的记录，不写数据库。

## 新增/修改文件

| 文件 | 作用 |
|---|---|
| `app/commercial_operations/service.py` | 新增 `CommercialOperationService.advance_main_agent_loop()` 和各 track 推进器 |
| `app/api/routes/commercial_operations.py` | 新增 `POST /main-agent/advance-loop` |
| `app/schemas/commercial_operation.py` | 新增 `CommercialOperationMainAgentAdvanceRequest/Response` |
| `tests/test_commercial_operation_main_agent_advance.py` | 覆盖 blocked、route smoke、完整 metadata 闭环 |
| `docs/GLOBAL_OPERATION_MAIN_AGENT_ADVANCE_LOOP.md` | 本文档 |

## 推进器边界

这个接口不会做以下事情：

- 不自动审批。
- 不发布到社媒或邮件平台。
- 不控制真实账号。
- 不执行 OpenClaw。
- 不运行 Playwright。
- 不提交 ComfyUI 队列。
- 不下载模型或安装 workflow。
- 不绕过验证码、代理、指纹、登录、secret 或人工确认。

它只创建下一步可审阅记录，让人工或客户机控制台继续推进。

Boundary markers:

```text
does not publish
does not execute OpenClaw
does not run Playwright
does not submit ComfyUI queues
```

## 请求与响应

请求：

```json
{
  "dry_run": false,
  "operator_note": "optional note",
  "metadata": {}
}
```

响应核心字段：

| 字段 | 说明 |
|---|---|
| `advance_status` | `created` / `updated` / `reused` / `dry_run` / `blocked` / `noop` |
| `advanced_track` | 本次主 Agent 选择的 track |
| `before_stage_key` | 推进前 operation loop 当前阶段 |
| `after_stage_key` | 推进后 operation loop 当前阶段 |
| `routing_decision` | 本次推进使用的主 Agent 路由决策 |
| `created_records` | 本次创建的记录 |
| `updated_records` | 本次推进状态的记录，如 approved deliverable -> packaged |
| `reused_records` | 已存在的待审/待执行记录 |
| `blocked_by` | 无法推进的硬性阻塞 |
| `operation_loop` | 推进后的闭环摘要 |

## Track 到记录的映射

| Track | 推进动作 | 生成/更新记录 | 停止点 |
|---|---|---|---|
| `operation_strategy` | 创建一级运营方案；方案批准后派生生产任务 | `OperationPlan` / `ProductionTask` | 等人工审批方案和生产任务 |
| `knowledge_retrieval` | 创建知识覆盖审阅 gate | `CommercialOperationApproval(step_key=knowledge_research)` | 等人工批准知识来源 |
| `content_strategy` | 创建内容策略草稿 | `CommercialOperationContentDraft` | 等人工审核草稿 |
| `text_content` | 创建文本内容草稿 | `CommercialOperationContentDraft` | 等人工审核草稿 |
| `visual_asset` | 创建视觉素材 brief | `CommercialOperationAssetRequest` | 等人工审核和运行时准备 |
| `video_content` | 创建视频/数字人 brief | `CommercialOperationAssetRequest(asset_type=video)` | 等模型、workflow、运行时 gate |
| `workflow_selection` | 创建 workflow 选择 brief | `CommercialOperationAssetRequest(asset_type=other)` | 等 workflow 知识和运行时确认 |
| `review_gate` | 创建人工审阅 gate | `CommercialOperationApproval(step_key=human_review)` | 等人工审批 |
| `client_execution` | 包装交付物、创建执行请求、或创建执行 run | `Deliverable` / `ExecutionRequest` / `ExecutionRun` | 等人工审批或客户机执行 |
| `result_recording` | 从终态 run 创建结果记录 | `CommercialOperationResult` | 等人工审核结果 |
| `analytics_observation` | 从 approved result 创建观察记录 | `CommercialOperationMonitoringObservation` | 等人工审核观察 |
| `analytics_optimization` | 从 approved observation 创建优化决策 | `CommercialOperationOptimizationDecision` | 等人工审核决策 |
| `next_cycle_content` | 从 approved decision 创建下一轮项目包 | `CommercialOperationPlan` + `CommercialOperationProductionTask` | 等人工审核下一轮方案和任务 |

## 当前可跑通的闭环

测试中已经覆盖的最小闭环：

```text
create operation with knowledge_collection
advance -> knowledge approval pending
approve knowledge approval
advance -> content draft ready_for_review
approve content draft
advance -> deliverable ready_for_review
approve + package deliverable
advance -> execution request ready_for_review
approve + prepare execution request
advance -> execution run queued
start + succeed execution run
advance -> result ready_for_review
approve result
advance -> monitoring observation ready_for_review
approve observation
advance -> optimization decision ready_for_review
approve optimization decision
advance -> next-cycle OperationPlan ready_for_review
advance -> next-cycle ProductionTask ready_for_review
```

这个闭环仍是 metadata-only。客户机 OpenClaw/Playwright 真执行、ComfyUI 真渲染、平台数据自动拉取都还在后续运行时接入阶段。

## Phase 68C 项目对象接入

Phase 68C 后，`operation_strategy` 不再只是提示“已经有 plan_outline”。主 Agent 会先创建 `OperationPlan` 并置为 `ready_for_review`。人工批准方案后，再由主 Agent 根据 `production_scope` 派生 `ProductionTask`，并置为 `ready_for_review`。

新增顺序：

```text
advance -> OperationPlan ready_for_review
human approve OperationPlan
advance -> ProductionTask ready_for_review
human approve ProductionTask
advance -> knowledge/content/workflow/publish closed loop
```

对于 Douyin、KTV、短视频、音乐、音频等目标，默认会派生 `copy`、`image`、`media(audio_video)` 三类生产任务。对于纯文案运营，至少派生 `copy` 任务。

这仍然是 metadata-only：主 Agent 不审批方案，不审批任务，不执行 ComfyUI，不发布，不运行 OpenClaw/Playwright。

## 关键设计修正

知识阶段不能再只停留在“配置了 knowledge_collection”。本阶段新增了 `knowledge_research` 审阅 gate：

- `pending` 时，`knowledge_context` 进入 `review_required`。
- `approved` 后，`knowledge_context` 才进入 `complete`。
- 这个 gate 只批准知识覆盖，不等同于发布/执行审批。

同时，`human_approval` 阶段只统计 `human_review` gate 和已审批的内容/交付/执行记录，不会把知识审阅误认为最终执行审批。

## 后续开发入口

下一阶段应在这个推进器之上继续补：

1. 前端按钮：显示主 Agent 推荐动作，并调用 `advance-loop`。
2. RAG 自动检索：知识阶段不只创建 approval，还能附带 evidence/source coverage。
3. 客户机执行：把 prepared execution request 显示到 OpenClaw/Playwright 控制台。
4. 结果回流：让客户机提交截图、URL、平台指标、失败原因。
5. ComfyUI 专项：视频/数字人 track 只在 runtime gate 完成后进入真实队列。
