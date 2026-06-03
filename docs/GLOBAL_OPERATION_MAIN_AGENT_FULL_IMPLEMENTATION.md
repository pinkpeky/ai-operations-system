# 全局运营主 Agent 完整实现记录

更新日期：2026-05-28

本文记录本轮“先把主 Agent 补完整”的开发结果。这里的“完整”指：主 Agent 已经可以作为全局运营闭环的统一路由器使用，能根据运营阶段、目标信号、知识状态、审批状态和执行边界，输出可审计的路由决策、专业分支列表和下一步执行包。它不表示所有专业 Agent、ComfyUI 模型、OpenClaw 发布和平台数据采集都已经生产可用。

## 目标

本轮目标不是继续加视频能力，也不是先接 ComfyUI 工作流，而是把：

```text
commercial_operation_agent
```

从“接口返回里的 controller 名称”变成独立的、可测试的主 Agent 模块。

主 Agent 现在必须能回答：

1. 当前运营任务处于哪个阶段。
2. 下一步应该走哪个专业分支。
3. 为什么选择这个分支。
4. 需要哪些输入和知识库。
5. 当前被什么条件阻塞。
6. 下一步执行包是什么。
7. 哪些动作允许，哪些动作禁止。
8. 需要哪些质量门和人工审核。

## 修改文件

### 主 Agent

[app/commercial_operations/main_agent.py](D:/ai-operations-system/app/commercial_operations/main_agent.py)

新增/重写：

```text
CommercialOperationMainAgent
TrackDefinition
```

### 服务层接入

[app/commercial_operations/service.py](D:/ai-operations-system/app/commercial_operations/service.py)

`CommercialOperationService.get_agent_skill_orchestration()` 现在只负责：

```text
读取 operation loop
构建 skills
调用 CommercialOperationMainAgent.plan()
返回 API response
```

主 Agent 判断逻辑不再散落在 service 私有方法里。

### API Schema

[app/schemas/commercial_operation.py](D:/ai-operations-system/app/schemas/commercial_operation.py)

增强：

```text
CommercialOperationSpecialistTrackResponse
CommercialOperationRoutingDecisionResponse
CommercialOperationAgentSkillOrchestrationResponse
```

### 测试

[tests/test_commercial_operation_main_agent.py](D:/ai-operations-system/tests/test_commercial_operation_main_agent.py)

新增主 Agent 独立单元测试。

[tests/test_commercial_operations_api.py](D:/ai-operations-system/tests/test_commercial_operations_api.py)

更新 API 集成断言。

## 主 Agent 当前覆盖的完整 Track

| Track | Owner Agent | 触发阶段 | 作用 |
|---|---|---|---|
| `operation_strategy` | `operation_strategy_agent` | `operation_topic` / `task_planning` | 目标、人群、渠道、指标和约束 |
| `knowledge_retrieval` | `rag_agent` | `knowledge_context` | 业务知识、证据快照、来源覆盖 |
| `content_strategy` | `content_strategy_agent` | `content_production` | 内容形式选择和 brief |
| `text_content` | `text_content_agent` | `content_production` / `content_improvement` | 文案、脚本、评论、私信 |
| `visual_asset` | `visual_asset_agent` | `content_production` | 图片、海报、封面、视觉素材 |
| `video_content` | `video_content_agent` | `content_production` | 视频、数字人、分镜、视频执行计划 |
| `workflow_selection` | `workflow_selection_agent` | `content_production` | 工具/工作流候选和执行包草案 |
| `review_gate` | `review_agent` | `human_approval` | 人工审核、风险控制和审批记录 |
| `client_execution` | `client_execution_agent` | `client_execution` | 客户机 OpenClaw/Playwright 交接 |
| `result_recording` | `publish_result_agent` | `result_recording` | 结果、证据和商业信号记录 |
| `analytics_observation` | `analytics_agent` | `data_observation` | 指标快照、评论主题、异常信号 |
| `analytics_optimization` | `analytics_agent` | `data_analysis` | 优化决策和下一轮建议 |
| `next_cycle_content` | `content_strategy_agent` | `content_improvement` | 下一轮内容生产 |

## 路由规则

主 Agent 首先按当前闭环阶段路由：

| 当前阶段 | 默认 Track |
|---|---|
| `operation_topic` | `operation_strategy` |
| `task_planning` | `operation_strategy` |
| `knowledge_context` | `knowledge_retrieval` |
| `content_production` | 根据信号选择内容分支 |
| `human_approval` | `review_gate` |
| `client_execution` | `client_execution` |
| `result_recording` | `result_recording` |
| `data_observation` | `analytics_observation` |
| `data_analysis` | `analytics_optimization` |
| `content_improvement` | `next_cycle_content` |

内容生产阶段再按信号细分：

| 信号 | Track |
|---|---|
| 视频、抖音、数字人、口播、直播、KTV、TikTok | `video_content` |
| 图片、图文、海报、封面、小红书、素材 | `visual_asset` |
| ComfyUI、workflow、工作流、生成 | `workflow_selection` |
| 文案、邮件、脚本、评论、私信、话术 | `text_content` |
| 没有明确内容形式 | `content_strategy` |

这个顺序是刻意设计的：不再把所有内容任务默认推向视频，也不在知识阶段提前进入内容生产。

## 主 Agent 输出结构

API：

```text
GET /api/v1/commercial-operations/{operation_id}/agent-skill-orchestration
POST /api/v1/commercial-operations/{operation_id}/agent-skill-orchestration/refresh
```

现在返回：

```json
{
  "controller_agent": {
    "agent_name": "commercial_operation_agent",
    "mode": "deterministic_global_orchestrator",
    "uses_existing_agents": [
      "rag_agent",
      "operation_strategy_agent",
      "content_strategy_agent",
      "text_content_agent",
      "visual_asset_agent",
      "video_content_agent",
      "workflow_selection_agent",
      "review_agent",
      "client_execution_agent",
      "publish_result_agent",
      "analytics_agent"
    ]
  },
  "routing_decision": {
    "decision_key": "operation_routing_decision",
    "decision_mode": "deterministic_stage_and_signal_router",
    "confidence": 0.9,
    "current_stage": "knowledge_context",
    "recommended_track": "knowledge_retrieval",
    "selected_track_status": "recommended",
    "selected_skill_key": "knowledge_retrieval_skill",
    "selected_agents": [
      "commercial_operation_agent",
      "rag_agent"
    ],
    "required_knowledge_collections": [
      "ai_knowledge_base"
    ],
    "required_inputs": [
      "knowledge_collection",
      "source_documents",
      "operation_query"
    ],
    "blocked_by": [],
    "reason_codes": [
      "stage:knowledge_context",
      "track:knowledge_retrieval"
    ],
    "quality_gates": [
      "sources_are_reviewable",
      "claims_have_evidence",
      "workspace_scope_is_enforced"
    ],
    "next_executable_contract": {}
  },
  "specialist_tracks": []
}
```

## 下一步执行包

`routing_decision.next_executable_contract` 是统一执行包草案。

示例：

```json
{
  "contract_version": "1.0",
  "track": "video_content",
  "selected_agent": "video_content_agent",
  "selected_skill_key": "content_production_skill",
  "selected_workflow": null,
  "handoff_target": "guarded_runtime_after_review",
  "input_assets": [],
  "parameters": {
    "operation_id": "operation-id",
    "current_stage": "content_production",
    "next_skill_key": "content_generation_skill",
    "knowledge_collections": [
      "ai_knowledge_base",
      "comfyui_cu130_workflows"
    ],
    "matched_signals": [
      "douyin",
      "video",
      "digital human"
    ]
  },
  "requested_outputs": [
    "shot_plan",
    "workflow_candidates",
    "video_execution_package"
  ],
  "allowed_actions": [
    "prepare_video_brief",
    "request_video_analysis",
    "rank_video_workflows"
  ],
  "forbidden_actions": [
    "no_approval_bypass",
    "no_secret_exposure",
    "no_comfyui_queue_submit_without_runtime_gate",
    "no_model_download_or_install"
  ],
  "quality_gates": [
    "video_analysis_verified",
    "model_readiness_verified",
    "human_review_before_render"
  ],
  "approval_required": true,
  "execution_boundary": "metadata_only_until_guarded_runtime",
  "status": "blocked"
}
```

## 阻塞判断

主 Agent 现在会显式输出 `blocked_by`：

| 条件 | 阻塞码 |
|---|---|
| 知识阶段没有知识库或知识链接 | `knowledge_source_missing` |
| 内容分支被选中但知识证据未完成 | `knowledge_evidence_not_approved` |
| 视频分支被选中 | `video_analysis_model_not_verified` |
| 视频分支被选中 | `video_generation_models_not_verified` |
| 工作流选择分支被选中 | `workflow_rag_ingestion_not_verified` |
| 客户机执行前审批未完成 | `human_approval_required` |
| 结果记录前执行未完成 | `completed_execution_run_required` |
| 数据观察前结果未批准 | `approved_result_required` |
| 优化分析前观察未批准 | `approved_observation_required` |
| 下一轮内容前优化决策未批准 | `approved_optimization_decision_required` |

这些阻塞不会被自动绕过。

## 为什么这算主 Agent 可用

现在主 Agent 已经能独立完成以下工作：

1. 读取当前 operation loop 状态。
2. 判断运营生命周期阶段。
3. 识别文本、视觉、视频、工作流、发布、数据分析信号。
4. 选择正确专业 track。
5. 返回专业 Agent 链路。
6. 返回 required inputs。
7. 返回 required knowledge collections。
8. 返回 blocked_by。
9. 返回 allowed actions。
10. 返回 forbidden actions。
11. 返回 quality gates。
12. 返回统一 next executable contract。
13. 保持所有外部执行在审批和 runtime gate 之后。

它已经不再只是“展示下一个 skill”，而是可被前端、客户机和后续专业 Agent 使用的全局调度入口。

## 仍然没有做的事

以下内容不是主 Agent 本体，不在本轮强行完成：

1. 不真实调用 ComfyUI。
2. 不提交 ComfyUI prompt。
3. 不真实执行 OpenClaw。
4. 不真实执行 Playwright 发布。
5. 不自动抓取社媒数据。
6. 不下载或安装模型。
7. 不把 LLM 接入为自动路由决策者。
8. 不绕过人工审批。

这些属于专业 Agent 或 runtime adapter 的实现范围。

## 测试覆盖

新增测试：

```text
tests/test_commercial_operation_main_agent.py
```

覆盖：

1. `knowledge_context` 阶段优先路由到 `knowledge_retrieval`。
2. 没有知识源时输出 `knowledge_source_missing`。
3. 视频信号路由到 `video_content`，并明确阻塞模型验证。
4. 内容形式不明确时路由到 `content_strategy`。
5. 后续阶段分别路由到审核、客户机执行、结果记录、数据观察、优化和下一轮内容。

更新测试：

```text
tests/test_commercial_operations_api.py
```

覆盖 API 返回：

```text
routing_decision
specialist_tracks
next_executable_contract
```

## 验证命令

```powershell
python -m py_compile app\commercial_operations\main_agent.py app\commercial_operations\service.py app\schemas\commercial_operation.py tests\test_commercial_operation_main_agent.py

.\.venv\Scripts\python.exe -m pytest tests\test_commercial_operation_main_agent.py tests\test_commercial_operations_api.py -q
```

## 客观完成度

本轮后，主 Agent 本体状态：

```text
独立模块：完成
完整 track 表：完成
阶段路由：完成
内容形式路由：完成
阻塞判断：完成
统一执行包草案：完成
API 接入：完成
测试覆盖：完成
真实专业 Agent 执行：未开始
ComfyUI 工作流选择真实接入：未开始
客户机真实发布：未开始
社媒数据自动回流：未开始
```

下一步如果继续开发，才应该进入专业分支：先接 `workflow_selection_agent` 或 `knowledge_retrieval` 的批量入库能力。

## 2026-05-28 追加：闭环推进器

本轮在主 Agent 路由之上新增了真正可调用的闭环推进接口：

```text
POST /api/v1/commercial-operations/{operation_id}/main-agent/advance-loop
```

对应实现：

```text
CommercialOperationService.advance_main_agent_loop()
CommercialOperationMainAgentAdvanceRequest
CommercialOperationMainAgentAdvanceResponse
tests/test_commercial_operation_main_agent_advance.py
docs/GLOBAL_OPERATION_MAIN_AGENT_ADVANCE_LOOP.md
```

它会根据 `routing_decision.recommended_track` 创建下一步可审阅记录：

```text
knowledge_retrieval -> knowledge_research approval gate
content_strategy/text_content -> content draft
visual_asset/video_content/workflow_selection -> asset/workflow brief
client_execution -> deliverable / execution request / execution run
result_recording -> result
analytics_observation -> monitoring observation
analytics_optimization -> optimization decision
next_cycle_content -> next-cycle draft
```

该接口一次只推进一个安全步骤。它不会自动审批，不会发布，不会控制账号，不会执行 OpenClaw/Playwright，不会提交 ComfyUI 队列。完整细节见 `docs/GLOBAL_OPERATION_MAIN_AGENT_ADVANCE_LOOP.md`。
