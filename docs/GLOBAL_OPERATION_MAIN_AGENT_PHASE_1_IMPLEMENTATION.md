# 全局运营主 Agent Phase 1 实现记录

更新日期：2026-05-28

本阶段目标：在不提交 GitHub、不依赖 ComfyUI 模型下载、不启动外部发布执行的前提下，把现有 `commercial_operation_agent` 从“阶段状态展示”推进为“全局路由决策输出”。视频、ComfyUI、OpenClaw、Playwright 仍然只是专业分支和受控执行能力，不作为系统主线。

## 背景判断

现有工程已经有完整的商业运营闭环对象：

- operation topic
- task planning
- knowledge context
- content production
- human approval
- client execution
- result recording
- data observation
- data analysis
- content improvement

对应接口主要在：

```text
GET /api/v1/commercial-operations/{operation_id}/operation-loop
GET /api/v1/commercial-operations/{operation_id}/agent-skill-orchestration
POST /api/v1/commercial-operations/{operation_id}/agent-skill-orchestration/refresh
```

但此前 `agent-skill-orchestration` 主要返回：

```text
当前第一个未完成 skill 是什么
```

它还没有显式表达：

```text
全局主 Agent 推荐走哪个专业分支
为什么这么选
需要哪些知识库和输入
当前被什么阻塞
下一步执行包边界是什么
```

## 本阶段代码改动

### 0. 主 Agent 从 Service 中抽离为一等模块

补充修正：主 Agent 本体必须先成为独立工程模块，不能长期把路由判断散落在 `CommercialOperationService` 里。否则后续接入视频、工作流、发布和数据分析时，会变成 service 承担 Agent 决策职责，边界不清。

新增文件：

[app/commercial_operations/main_agent.py](D:/ai-operations-system/app/commercial_operations/main_agent.py)

新增类：

```text
CommercialOperationMainAgent
```

它现在负责：

```text
controller_agent 描述
specialist_tracks 构建
routing_decision 构建
route_next_skill 决策记录
运营目标/渠道/约束的确定性信号识别
不同 track 的执行边界声明
```

`CommercialOperationService` 现在只负责：

```text
读取 operation loop 状态
整理 skills
调用 CommercialOperationMainAgent.plan()
返回 API response
```

这一步的目的不是增加新功能，而是修正职责边界：主 Agent 的判断逻辑归主 Agent，service 不继续膨胀为隐形 Agent。

### 1. 扩展 API 响应 Schema

修改文件：

[app/schemas/commercial_operation.py](D:/ai-operations-system/app/schemas/commercial_operation.py)

新增：

```text
CommercialOperationSpecialistTrackResponse
CommercialOperationRoutingDecisionResponse
```

并在：

```text
CommercialOperationAgentSkillOrchestrationResponse
```

新增字段：

```text
routing_decision
specialist_tracks
```

保持旧字段不删除：

```text
operation_id
workspace_id
controller_agent
orchestration_status
next_skill_key
next_action
completion_ratio
skills
decisions
boundaries
generated_at
```

这样前端和旧调用方仍然可以读取原有字段，新调用方可以读取全局路由决策。

### 2. 增强全局 Agent 服务层

修改文件：

[app/commercial_operations/service.py](D:/ai-operations-system/app/commercial_operations/service.py)

服务层现在调用：

```text
CommercialOperationMainAgent().plan()
```

`get_agent_skill_orchestration()` 现在除了原有 skills/decisions，也会返回：

```json
{
  "routing_decision": {
    "decision_key": "operation_routing_decision",
    "controller_agent": "commercial_operation_agent",
    "current_stage": "knowledge_context",
    "recommended_track": "knowledge_retrieval",
    "selected_agents": [
      "commercial_operation_agent",
      "rag_agent",
      "rag_agent"
    ],
    "required_knowledge_collections": [],
    "required_inputs": [
      "knowledge_collection",
      "source_documents",
      "operation_query"
    ],
    "blocked_by": [],
    "next_executable_contract": {
      "track": "knowledge_retrieval",
      "selected_agent": "rag_agent",
      "selected_workflow": null,
      "input_assets": [],
      "parameters": {
        "current_stage": "knowledge_context",
        "next_skill_key": "knowledge_retrieval_skill"
      },
      "approval_required": true,
      "execution_boundary": "metadata_only_review_required"
    },
    "rationale": "...",
    "next_action": "...",
    "evidence": []
  }
}
```

### 3. 新增专业分支视图

当前返回的 `specialist_tracks` 包括：

| Track | Owner Agent | 作用 |
|---|---|---|
| `operation_strategy` | `operation_strategy_agent` | 目标、人群、渠道、指标 |
| `knowledge_retrieval` | `rag_agent` | 业务知识、证据快照、来源覆盖 |
| `content_strategy` | `content_strategy_agent` | 内容形式选择和 brief |
| `text_content` | `text_content_agent` | 文案、脚本、评论、私信 |
| `visual_asset` | `visual_asset_agent` | 图片、封面、海报、素材需求 |
| `video_content` | `video_content_agent` | 视频、数字人、分镜、视频执行计划 |
| `workflow_selection` | `workflow_selection_agent` | 工具/工作流候选选择 |
| `review_gate` | `review_agent` | 人工审核、风险控制和审批记录 |
| `client_execution` | `client_execution_agent` | 客户机 OpenClaw/Playwright 执行交接 |
| `result_recording` | `publish_result_agent` | 结果、证据和商业信号记录 |
| `analytics_observation` | `analytics_agent` | 指标快照、评论主题、异常信号 |
| `analytics_optimization` | `analytics_agent` | 优化决策和下一轮建议 |
| `next_cycle_content` | `content_strategy_agent` | 下一轮内容生产 |

注意：这些 track 当前是确定性路由视图，不代表所有专业 Agent 都已有独立完整实现。

## 当前路由规则

本阶段故意不用 LLM 做路由，先用确定性规则保证可审计、可测试。

### 视频触发信号

如果 operation 的标题、目标、渠道、指标或约束包含：

```text
video
short video
reel
tiktok
douyin
数字人
短视频
视频
口播
直播
ktv
商k
抖音
```

并且当前阶段在内容生产附近，则推荐：

```text
video_content
```

同时 `blocked_by` 会加入：

```text
video_analysis_model_not_verified
```

因为目前视频解析模型还未最终确认。

### 图片/视觉触发信号

如果包含：

```text
image
poster
cover
banner
图文
图片
海报
封面
素材
小红书
```

则可能推荐：

```text
visual_asset
workflow_selection
```

### 客户机执行触发

如果当前阶段进入：

```text
client_execution
result_recording
```

则推荐：

```text
client_execution
```

边界为：

```text
client_machine_after_approval
```

### 数据优化触发

如果当前阶段进入：

```text
data_observation
data_analysis
content_improvement
```

则推荐：

```text
analytics_optimization
```

### 默认内容生产

如果没有明确视频或视觉信号，内容生产阶段默认推荐：

```text
text_content
```

这是为了避免系统无理由地把所有运营任务都推向视频。

## 边界声明

本阶段不做：

1. 不调用 ComfyUI。
2. 不提交 ComfyUI prompt。
3. 不启动 OpenClaw。
4. 不启动 Playwright 发布。
5. 不接入真实社媒账号。
6. 不自动抓取平台数据。
7. 不用 LLM 自动改写路由决策。
8. 不把视频分支作为默认主线。

本阶段只做：

1. 全局主 Agent 返回可审计的路由决策。
2. 明确专业 track。
3. 明确下一步执行包边界。
4. 保持旧接口兼容。

## 测试改动

修改文件：

[tests/test_commercial_operations_api.py](D:/ai-operations-system/tests/test_commercial_operations_api.py)

新增断言：

```text
routing_decision.controller_agent == commercial_operation_agent
routing_decision.recommended_track == knowledge_retrieval
routing_decision.next_executable_contract.track == knowledge_retrieval
routing_decision.next_executable_contract.execution_boundary == metadata_only_review_required
rag_agent in routing_decision.selected_agents
specialist_tracks 包含 video_content
specialist_tracks 包含 workflow_selection
refresh 后 routing_decision 仍然稳定
```

这个测试刻意验证：普通商业运营任务不会默认进入视频分支。

## 与后续阶段的关系

### Phase 2：接入 workflow_selection_agent

把已有文件接入后端服务层：

```text
deployment/comfyui/commercial_ktv_workflow/cu130_workflow_rag_documents.jsonl
scripts/select_comfyui_workflows.py
```

目标：

```text
routing_decision.recommended_track == workflow_selection 或 video_content 时
返回 ranked_workflows / rejected_workflows / workflow_execution_package_draft
```

### Phase 3：接入视频解析结果

等 ComfyUI 模型下载完成或独立视频解析服务可用后，引入：

```text
VideoAnalysisResult
```

然后让全局主 Agent 根据解析结果决定：

```text
文本复刻
图文复刻
短视频复刻
数字人视频
素材清理
只做运营分析
```

### Phase 4：统一 ExecutionPackage

把文本、图文、视频、发布、分析都收敛到统一执行包：

```json
{
  "track": "knowledge_retrieval | content_strategy | text_content | visual_asset | video_content | workflow_selection | review_gate | client_execution | result_recording | analytics_observation | analytics_optimization | next_cycle_content",
  "selected_agent": "...",
  "selected_workflow": null,
  "input_assets": [],
  "parameters": {},
  "approval_required": true,
  "execution_boundary": "metadata_only | guarded_runtime | client_machine"
}
```

## 当前完成度更新

本阶段完成后：

```text
全局主 Agent 智能路由：20% -> 30%
工作流自动选择：20% 不变，等待 Phase 2 接入
视频解析：10% 不变，等待模型或独立服务
运营闭环状态流：60% -> 65%
```

客观判断：这一步不是让系统马上自动生产内容，而是把“全局主 Agent 应该先做路由判断”这个工程位置固定下来。
