# 运营项目工程实现差距审计

审计日期：2026-05-30

## 审计口径

本审计按当前工作区代码与文档整理，不等同于远端 `main` 稳定分支能力。当前工作区存在大量未提交和未跟踪文件，因此结论以本机 `D:\ai-operations-system` 的实际文件为准。

本审计重点对齐新的全局需求：

1. 输入运营主题和目标。
2. 生成运营方案。
3. 人工审批运营方案。
4. 按运营方案拆分文案流、图片流、影音流、运营方案输出。
5. 人工选择海报、视频和音频的 ComfyUI 工作流。
6. 生成候选成品。
7. 人工挑选最终作品。
8. 针对最终图片、视频或音频成品编写社媒发布文案。
9. 人工审批发布文案和发布包。
10. 客户机通过 OpenClaw 和 Playwright 执行真实社媒发布。
11. 定时拉取社媒数据，例如抖音播放量、互动量等。
12. 数据回传服务器分析并生成优化决策，进入下一轮闭环。
13. 每个运营项目需要独立管理素材、输出、审批、发布、监控和优化记录。

## 总体结论

项目已经具备“运营闭环底座”，但还没有形成完整的“运营项目产品化工作流”。

已实现较多的是后端记录、审批、执行准备、结果记录、监控观察、优化决策、ComfyUI 受控运行、数字人视频产出回流这些基础能力。也就是说，工程已经能表达很多闭环节点，并能把数字人视频资产回接到商业运营资产请求中。音频目前只作为素材类型被局部提到，还没有形成正式的音频生产流。

缺口主要在项目管理层和人机协同层：运营方案还不是一级业务产物；文案、图片、视频、音频没有统一的生产任务层；素材库和输出库没有按运营项目形成治理闭环；候选作品挑选、最终作品确认、平台发布文案审批、真实客户机发布、平台数据自动回收还没有达到可直接运营的程度。

## 已实现能力

### 1. 商业运营项目基础

当前已有 `CommercialOperation` 模型、创建/查询/更新接口和运营循环汇总接口。

相关位置：

- `app/models/commercial_operation.py`
- `app/schemas/commercial_operation.py`
- `app/api/routes/commercial_operations.py`
- `CommercialOperationService.get_operation_loop_summary`
- `GET /api/v1/commercial-operations/{operation_id}/operation-loop`

覆盖情况：基础可用，但更接近“商业运营记录”，还不是完整的“运营项目管理空间”。它能承载目标、状态、优先级、计划概要和循环摘要，但缺少项目级素材目录、输出目录、生产任务看板、候选作品池和发布计划。

### 2. 主 Agent 与闭环推进

当前已有主 Agent 推进接口和 Agent/Skill 编排接口。

相关位置：

- `app/commercial_operations/main_agent.py`
- `CommercialOperationService.advance_main_agent_loop`
- `GET /api/v1/commercial-operations/{operation_id}/agent-skill-orchestration`
- `POST /api/v1/commercial-operations/{operation_id}/main-agent/advance-loop`
- `docs/GLOBAL_OPERATION_MAIN_AGENT_ADVANCE_LOOP.md`

覆盖情况：已经有“下一步动作判断”和闭环阶段推进能力，但目前更偏元数据编排。它能判断知识检索、客户执行、数据观察、下一轮内容等阶段，但还没有把运营方案、生产任务、候选作品和发布包作为强约束状态机串起来。

### 3. 审批门

当前已有商业运营审批模型和接口。

相关位置：

- `CommercialOperationApproval`
- `POST /api/v1/commercial-operations/{operation_id}/approvals`
- `GET /api/v1/commercial-operations/{operation_id}/approvals`
- 审批通过、驳回、归档等动作接口

覆盖情况：审批底座存在。缺口是审批对象需要进一步细分，例如运营方案审批、工作流选择审批、候选作品终选审批、发布文案审批、发布包审批。目前审批更像通用审批记录，尚未绑定完整的运营项目阶段状态机。

### 4. 文案草稿

当前已有内容草稿模型、人工审核、RAG 生成接口。

相关位置：

- `CommercialOperationContentDraft`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts`
- `POST /api/v1/commercial-operations/{operation_id}/content-drafts/generate-rag`

覆盖情况：文案底座可用。缺口是它还没有被明确拆成两个层次：

- 运营方案阶段的策略文案、脚本、分镜、素材需求。
- 成品确定后的平台发布文案，例如抖音标题、话题、封面文案、评论区引导、发布时间建议。

### 5. 图片/视频资产需求

当前已有资产请求模型、人工审核、RAG 资产简报生成接口。

相关位置：

- `CommercialOperationAssetRequest`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests`
- `POST /api/v1/commercial-operations/{operation_id}/asset-requests/generate-rag`

覆盖情况：能表达图片、视频、音频等资产需求，也能进入 ComfyUI 或数字人产出的后续链路。缺口是缺少统一的“生产任务”实体来管理每个图片、视频、音频任务的输入素材、所选工作流、候选输出、最终选择和返工记录。

### 6. ComfyUI 商业运营交接链路

当前已有较完整的 ComfyUI 商业运营交接模型。

相关位置：

- `CommercialOperationComfyUIHandoff`
- `CommercialOperationComfyUIPreflight`
- `CommercialOperationComfyUIAdapterConfig`
- `CommercialOperationComfyUIJobRequest`
- `CommercialOperationComfyUIExecutionPlan`
- `CommercialOperationComfyUIConnectionProbe`
- `CommercialOperationComfyUIAdapterDispatch`
- `CommercialOperationComfyUIRuntimeGate`
- `CommercialOperationComfyUIRuntimeDryRun`
- `CommercialOperationComfyUIRuntimeActivation`
- `POST /api/v1/commercial-operations/{operation_id}/comfyui-*`

覆盖情况：工程层很完整，尤其强调审批、预检、运行保护和审计。但它偏“运行安全链路”，不是运营人员视角的“选择一个图片/视频/音频工作流并生成候选作品”。后续需要在它上面加产品化选择层，而不是让 Agent 或人工直接面对底层 ComfyUI 调度对象。

### 7. ComfyUI 真实运行适配

当前已有 ComfyUI runtime 健康检查、诊断、配置变更、受控探测、prompt job、视频 job 等接口。

相关位置：

- `app/models/comfyui_runtime.py`
- `app/schemas/comfyui_runtime.py`
- `app/api/routes/comfyui_runtime.py`
- `GET /api/v1/comfyui-runtime/health`
- `GET /api/v1/comfyui-runtime/capabilities`
- `GET /api/v1/comfyui-runtime/diagnostics`
- `POST /api/v1/comfyui-runtime/prompt-jobs`
- `POST /api/v1/comfyui-runtime/video-resource-plans`
- `POST /api/v1/comfyui-runtime/video-jobs`
- `GET /api/v1/comfyui-runtime/video-jobs/{job_id}`
- `POST /api/v1/comfyui-runtime/video-jobs/{job_id}/refresh`

覆盖情况：受控提交和视频任务记录已存在。缺口是对运营项目来说，还需要“工作流模板库、工作流参数快照、输入素材绑定、候选输出入库、最终作品选择”这一层业务抽象。

### 8. 影音流中的数字人和音频子链路

视频流应升级为“影音流”：它同时覆盖视频和音频。音频不是备注字段，而应作为正式生产类型，包含配音、歌曲、背景音乐、音效、音频分离、混音、口型驱动音频、参考视频音频提取等任务。

数字人链路在业务架构上归属于影音流，不应与影音流并列。当前代码把它拆成独立模块，是因为数字人视频有独立的资产授权、人物一致性、音频/口型/动作、工作流绑定和输出摄取要求；但在运营项目闭环中，它应作为 `media` 生产任务的一种实现方式或供应商分支。

当前已有数字人资产、视频任务、工作流模板绑定、工作流就绪检查、分镜执行计划、ComfyUI 输出摄取。

相关位置：

- `app/models/digital_human.py`
- `app/schemas/digital_human.py`
- `app/api/routes/digital_humans.py`
- `POST /api/v1/digital-humans/assets`
- `POST /api/v1/digital-humans/video-jobs`
- `POST /api/v1/digital-humans/video-jobs/{job_id}/workflow-binding`
- `POST /api/v1/digital-humans/video-jobs/{job_id}/workflow-readiness-check`
- `POST /api/v1/digital-humans/video-jobs/{job_id}/shot-execution-plan`
- `POST /api/v1/digital-humans/video-jobs/{job_id}/comfyui-output-ingestion`

覆盖情况：数字人视频作为影音流内部的一条专门子链路已经比较清晰。上一阶段新增的商业交接接口可以把已完成数字人视频资产回连到商业运营资产请求。

相关接口：

- `POST /api/v1/commercial-operations/{operation_id}/digital-human-delivery-link`

缺口是数字人目前在代码层仍更像独立视频生产分支，还没有被统一纳入运营项目的 `media` 生产任务、候选作品池和最终发布包管理。音频链路目前缺口更大：尚缺音频 ComfyUI 工作流登记、音频生产任务、音频候选输出、音视频合成关系、最终混音确认和发布包绑定。

### 9. 成品、执行、结果、监控、优化

当前已有交付物、执行请求、执行运行、结果、监控观察、优化决策和证据快照。

相关位置：

- `CommercialOperationDeliverable`
- `CommercialOperationExecutionRequest`
- `CommercialOperationExecutionRun`
- `CommercialOperationResult`
- `CommercialOperationMonitoringObservation`
- `CommercialOperationOptimizationDecision`
- `CommercialOperationEvidenceSnapshot`
- `POST /api/v1/commercial-operations/{operation_id}/deliverables`
- `POST /api/v1/commercial-operations/{operation_id}/execution-requests`
- `POST /api/v1/commercial-operations/{operation_id}/execution-runs`
- `POST /api/v1/commercial-operations/{operation_id}/results`
- `POST /api/v1/commercial-operations/{operation_id}/monitoring-observations`
- `POST /api/v1/commercial-operations/{operation_id}/optimization-decisions`
- `POST /api/v1/commercial-operations/{operation_id}/evidence-snapshots`

覆盖情况：闭环骨架已经在。关键限制是当前很多客户机执行、发布结果、平台数据观察仍偏人工记录或元数据记录，不能等同于已经完成真实社媒发布和自动数据回收。

## 按目标流程逐项对照

| 目标阶段 | 当前实现 | 覆盖判断 | 主要缺口 |
|---|---|---|---|
| 输入运营主题目标 | `CommercialOperation` 创建接口、客户机运营目标入口文档 | 部分可用 | 缺少项目级 brief 表单、目标指标、平台账号、预算、周期等结构化字段 |
| 生成运营方案 | `plan-draft`、主 Agent advance loop、RAG 草稿生成 | 部分可用 | 运营方案不是一级持久化产物，缺少版本、审批、变更记录 |
| 人工审批运营方案 | 通用 `CommercialOperationApproval` | 底座可用 | 缺少 `operation_plan` 专属审批对象和阶段锁 |
| 文案流 | `CommercialOperationContentDraft` | 部分可用 | 缺少脚本/分镜/平台发布文案分层 |
| 图片流 | `CommercialOperationAssetRequest`、ComfyUI handoff/runtime | 部分可用 | 缺少图片生产任务、工作流选择、候选图、终选图 |
| 影音流 | 视频 Agent、ComfyUI video job、数字人 video job；数字人和音频应作为影音流内部子链路 | 部分可用 | 缺少统一影音生产任务、音频生产任务、候选视频/音频池、人工终选、返工记录 |
| 人工选择 ComfyUI 工作流 | 数字人 workflow binding、ComfyUI handoff/preflight | 部分可用 | 缺少运营人员可理解的图片/视频/音频工作流候选库和选择状态 |
| 生成候选成品 | ComfyUI runtime outputs、digital human output ingestion | 部分可用 | 缺少候选成品实体、评分、预览、版本关系 |
| 挑选最终作品 | 交付物和资产请求可表达结果 | 不完整 | 缺少明确的 final selection API、选择理由、审批记录 |
| 针对作品写社媒文案 | 内容草稿可复用 | 不完整 | 缺少 asset-bound social copy，即绑定最终图片/视频的发布文案 |
| 发布前审批 | 通用审批、交付物审批、执行请求审批 | 部分可用 | 缺少按平台发布包审批，例如抖音发布包 |
| 客户机 OpenClaw/Playwright 发布 | execution request/run、worker/client loop 文档 | 不完整 | 目前大多为元数据/手工记录，真实发布适配还未闭合 |
| 定时拉取社媒数据 | monitoring observations | 不完整 | 缺少真实平台数据 connector、调度任务、账号级数据权限 |
| 数据回传分析优化 | result/observation/optimization decision | 部分可用 | 缺少自动化分析入口和下一轮生产任务自动派生 |
| 运营项目独立管理 | 商业运营记录、links、deliverables | 部分可用 | 缺少项目空间、素材库、输出库、发布日历、指标看板 |
| 素材规范管理 | digital human assets、links、OutputArtifact 相关文档 | 部分可用 | 缺少按项目归档的 material registry |
| 输出规范管理 | deliverables、asset requests、runtime outputs | 部分可用 | 缺少 candidate/final/published/performance 生命周期 |

## 核心缺口

### P0：必须先补的业务骨架

1. 运营方案一级产物

需要新增或明确 `OperationPlan` 业务对象，支持目标、受众、平台、内容策略、产出清单、素材需求、排期、KPI、风险和版本。审批通过后才能进入生产任务。

2. 运营项目生产任务层

需要新增统一的 `ProductionTask` 或等价模型，把文案、图片、影音任务统一管理。每个任务应包含任务类型、来源方案、输入素材、选定工作流、执行状态、候选输出、返工次数和最终结果。影音任务内部应区分 `video`、`audio`、`audio_video`，避免把音频隐藏在视频任务备注里。

3. 项目素材库

需要新增 `ProjectMaterial` 或等价模型，用于规范管理客户上传素材、参考视频、场景图、人物图、音频、品牌资料、脚本资料等。素材需要有用途、授权、来源、标签、项目归属和可用状态。

4. 候选输出和最终选择

需要新增 `OutputCandidate` / `FinalSelection` 或等价模型。ComfyUI、数字人、图片生成、视频生成、音频生成、文案生成都应先进入候选池，再由人工选择最终作品。

### P1：影响可运营性的关键层

1. 工作流选择产品层

底层 ComfyUI 调度对象已经多，但运营人员需要看到的是“适合什么项目、输入需要什么、输出是什么、耗时和显存预估、失败风险、推荐用途”。这层应来自 workflow RAG 文档和固定模板注册表，而不是让主 Agent 自由猜。

2. 成品绑定发布文案

发布文案必须绑定最终图片、视频或音频成品，而不是只存在一个泛化内容草稿。一个视频可能有抖音版、小红书版、视频号版不同文案和封面策略；一个音频也可能用于视频配乐、直播预热、播客片段或短视频原声。

3. 发布包合同

客户机执行前应生成 `PublishPackage`：平台、账号、素材、标题、正文、话题、封面、发布时间、风控提示、审批状态、执行约束。客户机只接收审批通过的发布包。

4. 前端操作台

当前后端对象多，前端需要把这些对象收敛成几个关键界面：项目总览、素材导入、方案审批、生产任务、候选作品预览、最终选择、发布包、数据回收、优化建议。

客户机前端应是工作人员的主工作台，必须包含：

- 运营任务创建和提交到服务器。
- 项目素材导入，包括参考视频、场景图、人物/产品素材、音频、品牌资料、脚本文档。
- 所有业务审批，包括运营方案、生产任务、工作流选择、候选作品终选、发布文案、发布包和执行结果确认。
- 流的选择，包括图片流、视频流、数字人流、音频流、音视频合成流和后处理流；客户机只展示业务化候选卡，不展示 ComfyUI 原始节点。
- 图片、视频、音频、音视频组合的候选产出预览。
- 最终作品挑选、返工意见和发布包确认。
- 客户机 OpenClaw / Playwright 执行前后的状态、结果和人工补录入口。

服务器前端应偏管理员视角，用于资源、队列、模型、ComfyUI 运行、异常处理、审计和后台配置，不应让普通工作人员面对底层工程对象。

### P2：闭环自动化增强

1. 平台数据拉取 connector

需要按平台实现数据获取，不宜先做泛化。抖音应先定义可获取字段、认证方式、频率、失败策略和人工补录兜底。

2. 定时分析任务

需要每日按项目拉取数据，生成 `MonitoringObservation`，并触发分析任务生成 `OptimizationDecision`。

3. 下一轮任务派生

优化决策审批后，应能自动派生下一轮 `OperationPlan` 修订或新的生产任务，而不是只停留在文字建议。

## 当前不应误判的点

1. 不是“没有主 Agent”。主 Agent 和 advance loop 已经存在，但它还缺少运营项目产品对象作为强约束。

2. 不是“没有 ComfyUI 集成”。ComfyUI runtime、video job、commercial handoff、digital-human binding 都存在，但还没有完成运营人员视角的工作流选择和候选成品管理。

3. 不是“影音流已经等于运营视频系统”。数字人视频和音频都应归入影音流，但它们只是影音流内部的子链路；全局项目还需要把普通视频生成、数字人视频、音频生成、图片、文案、发布包、数据回收和优化闭环统一到同一个运营项目状态机里。

4. 不是“客户机真实发布已经完成”。现有 execution request/run 和 worker/client loop 提供执行记录和交接骨架，但真实 OpenClaw/Playwright 发布、账号控制、平台数据拉取仍需要单独完成，并且必须保留人工审批。

5. 不是“让 Agent 自由选择工作流就是最好方案”。在当前阶段，更可靠的方式是建立工作流知识库和模板注册表，让 Agent 在有限、结构化、可解释的候选集中推荐，再由人工确认。

## 推荐下一阶段

推荐下一阶段定为：Phase 68B Operation Project Governance。

目标不是继续深挖单个视频效果，而是先把全局运营闭环的业务对象补齐：

1. 新增运营方案一级产物和审批门。
2. 新增项目素材库。
3. 新增统一生产任务层，覆盖文案、图片、影音。
4. 新增候选输出和最终选择层，覆盖图片、视频、音频和音视频组合。
5. 定义发布包合同，但真实发布 connector 可放到后续阶段。

完成 Phase 68B 后，影音 Agent、图片 Agent、文案 Agent 才能稳定挂到同一条项目闭环上；否则继续补单点视频流会让系统变成多个孤立功能，而不是运营项目系统。
