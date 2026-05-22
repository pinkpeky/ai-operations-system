# 项目状态

## Branch Status

Current update (2026-05-22): active next branch `codex/phase-62w-knowledge-validation-outcomes` after draft PR #88 / Phase 62V Customer Console Knowledge Validation Guidance and now draft PR #89. It adds Phase 62W Customer Console Knowledge Validation Outcomes for `worker_console` and `worker_console_desktop`: ready/needs-evidence/needs-review decisions, evidence counts, material context, validation mode, and next-step actions on the separate visual knowledge base upload/edit page. The knowledge validation outcomes do not show code or JSON. It preserves local runtime/heartbeat controls, Chinese/English language switching, approvals, playbooks, outputs, tasks, logs, and server/client boundary warnings. It does not import ComfyUI adapters, call ComfyUI, submit prompts, read or submit queues beyond existing RAG search, generate media, enable runtime switches, mutate runtime configuration, resolve secrets, publish, run OpenClaw, control accounts, or bypass approval.

Active runtime surface: `/api/v1/comfyui-runtime/health`, `/api/v1/comfyui-runtime/capabilities`, `/api/v1/comfyui-runtime/diagnostics`, `/api/v1/comfyui-runtime/maintenance-runbook`, `/api/v1/comfyui-runtime/config-change-requests`, `/api/v1/comfyui-runtime/manual-apply-evidence`, `/api/v1/comfyui-runtime/post-manual-readiness-checks`, `/api/v1/comfyui-runtime/guarded-probe-executions`, and `/api/v1/comfyui-runtime/diagnostic-snapshots`, with `api_config_mutation_performed=false`, `guarded_probe_ready`, `health_probe_executed`, `external_request_attempted`, and `probe_result_status` audit fields.

Phase 62V Customer Console Knowledge Validation Guidance from `codex/phase-62v-knowledge-validation-guidance` remains the immediate customer-console UX predecessor, and Phase 62W preserves the Phase 62V knowledge validation guidance while adding knowledge validation outcomes. Phase 62U Customer Console Knowledge Ingestion Status Loop from `codex/phase-62u-knowledge-ingestion-status` remains the earlier knowledge ingestion status loop predecessor. Phase 62T Customer Console Knowledge Search Validation from `codex/phase-62t-knowledge-search-validation` remains the earlier knowledge search validation predecessor. Phase 62S Customer Console Knowledge Document Details from `codex/phase-62s-knowledge-document-details` remains the earlier knowledge document details predecessor. Phase 62R Customer Console Knowledge Activity Timeline from `codex/phase-62r-knowledge-activity-timeline` remains the earlier knowledge activity timeline predecessor. Phase 62Q Customer Console Knowledge Upload Readiness from `codex/phase-62q-knowledge-upload-readiness` remains the earlier knowledge upload readiness predecessor. Phase 62P Customer Console Simple Operator Mode from `codex/phase-62p-client-simple-operator-mode` remains the earlier simple-operator predecessor. Phase 62O Customer Console Goal Status Tracker from `codex/phase-62o-client-goal-status-tracker` remains the earlier tracker predecessor. Phase 62N Customer Console Goal Plan Preview from `codex/phase-62n-client-goal-plan-preview` remains the earlier plan preview predecessor. Phase 62M Customer Console Goal Templates from `codex/phase-62m-client-goal-templates` remains the earlier template predecessor. Phase 62L Customer Console Task Workbench from `codex/phase-62l-client-task-workbench` remains the earlier workbench predecessor, Phase 62K Customer Console Codex-like UX Simplification from `codex/phase-62k-customer-console-codex-ux` remains the earlier simplification predecessor, and Phase 62J ComfyUI Runtime Guarded Probe Execution Audit remains the immediate runtime predecessor: the server-side guarded probe is approval-gated, while Phase 62W keeps the customer-machine UI focused on simple task operation and visual knowledge maintenance before advanced diagnostics.

Phase 62I Workstation/Customer Client Frontend UX Alignment from `codex/phase-62i-workstation-client-ux` remains the earlier customer-console baseline for `worker_console` and `worker_console_desktop`, including Chinese/English language switching, local runtime/heartbeat visibility, and server-vs-customer-machine boundary guidance.

Previous update (2026-05-22): PR #73 is the draft Phase 62G ComfyUI runtime manual apply evidence slice. The active next branch is `codex/phase-62h-comfyui-post-manual-readiness`, scoped to Phase 62H ComfyUI Runtime Post-Manual Readiness Checks: `/api/v1/comfyui-runtime/health`, `/api/v1/comfyui-runtime/capabilities`, `/api/v1/comfyui-runtime/diagnostics`, `/api/v1/comfyui-runtime/maintenance-runbook`, `POST /api/v1/comfyui-runtime/config-change-requests`, `GET /api/v1/comfyui-runtime/config-change-requests`, ready/approve/reject/cancel/archive request actions, `POST /api/v1/comfyui-runtime/config-change-requests/{request_id}/manual-apply-evidence`, `GET /api/v1/comfyui-runtime/manual-apply-evidence`, ready/verify/reject/fail/archive evidence actions, `POST /api/v1/comfyui-runtime/manual-apply-evidence/{evidence_id}/post-manual-readiness-checks`, `GET /api/v1/comfyui-runtime/post-manual-readiness-checks`, ready/approve/reject/fail/archive readiness-check actions, `POST /api/v1/comfyui-runtime/diagnostic-snapshots`, `GET /api/v1/comfyui-runtime/diagnostic-snapshots`, `comfyui_runtime_post_manual_readiness_checks`, `ComfyUIRuntimePostManualReadinessCheck`, `ComfyUIRuntimeService`, `readiness_status`, `blocking_reasons`, `recommended_actions`, `next_operator_action`, `recovery_actions`, `configuration_summary`, `snapshot_recommended`, `change_status`, `requested_changes`, `manual_config_applied=true`, `service_restart_reported`, `comparison_status`, `guarded_probe_ready`, `health_probe_executed=false`, and `api_config_mutation_performed=false`; the Admin Dashboard ComfyUI page exposes maintainer create/review controls. Diagnostics, runbook, snapshots, config change requests, manual apply evidence, and post-manual readiness checks never attempt network calls. The only permitted live request remains `GET /system_stats` from health after every explicit provider/enabled/network/host/path/read-only gate is true. This phase does not import or call ComfyUI adapters, call execution endpoints, read queues, submit prompts or queues, upload files, generate media, enable runtime switches, write environment variables, restart services, mutate runtime configuration, store or resolve secrets, publish, control real accounts, ingest platform analytics, claim ROI attribution, or bypass approval.

当前更新（2026-05-21）：PR #65 是 Phase 61Y ComfyUI runtime dry-run 草稿，PR #66 是 Phase 61Z ComfyUI runtime activation 草稿；当前开发分支是 `codex/phase-61z-commercial-comfyui-runtime-activations`，范围是 Phase 61Z Commercial Operation ComfyUI Runtime Activations：`commercial_operation_comfyui_runtime_activations`、`/api/v1/commercial-operations/{operation_id}/comfyui-runtime-activations`、Admin Dashboard 独立 ComfyUI 页签/runtime activation 操作、从 validated runtime dry-run 生成可审查的 metadata-only runtime activation request、switch audit、runtime guardrails、validation checks、rollback guidance 和 runtime activation lifecycle state。该阶段不会 import 或调用 ComfyUI adapter、不会请求 ComfyUI、不会提交 prompt、不会读取队列、不会上传文件、不会提交队列、不会启用 runtime switch、不会保存或解析密钥值、不会生成媒体、不会发布、不会控制真实账号、不会接入平台分析、不会宣称 ROI 归因，也不会绕过审批。

当前更新（2026-05-21）：PR #63 是 Phase 61W ComfyUI adapter dispatch 草稿；当前开发分支是 `codex/phase-61x-commercial-comfyui-runtime-gates`，范围是 Phase 61X Commercial Operation ComfyUI Runtime Gates：`commercial_operation_comfyui_runtime_gates`、`/api/v1/commercial-operations/{operation_id}/comfyui-runtime-gates`、Admin Dashboard ComfyUI runtime gate 操作面板、从 dispatched adapter dispatch 生成可审查的 metadata-only runtime gate、runtime switch、network/queue/secret/approval policy、validation checks、rollback guidance 和 gate lifecycle state。该阶段不会请求 ComfyUI、不会提交 prompt、不会读取队列、不会上传文件、不会提交队列、不会保存或解析密钥值、不会生成媒体、不会发布、不会控制真实账号、不会接入平台分析、不会宣称 ROI 归因，也不会绕过审批。

当前更新（2026-05-21）：PR #62 是 Phase 61V ComfyUI connection probe 草稿；当前开发分支是 `codex/phase-61w-commercial-comfyui-adapter-dispatches`，范围是 Phase 61W Commercial Operation ComfyUI Adapter Dispatches：`commercial_operation_comfyui_adapter_dispatches`、`/api/v1/commercial-operations/{operation_id}/comfyui-adapter-dispatches`、Admin Dashboard ComfyUI adapter dispatch 操作面板、从 probed connection probe 生成可审查的 metadata-only dispatch handoff、prompt/workflow/queue/dispatch payload、guardrails、retry/recovery metadata 和 dispatch lifecycle state。该阶段不会请求 ComfyUI、不会提交 prompt、不会读取队列、不会上传文件、不会提交队列、不会保存密钥值、不会生成媒体、不会发布、不会控制真实账号、不会接入平台分析、不会宣称 ROI 归因，也不会绕过审批。

当前更新（2026-05-21）：PR #57 是 Phase 61Q ComfyUI handoff 草稿，PR #58 是 Phase 61R ComfyUI preflight 草稿，PR #59 是 Phase 61S ComfyUI adapter config 草稿，PR #60 是 Phase 61T ComfyUI job request 草稿，PR #61 是 Phase 61U ComfyUI execution plan 草稿。当前开发分支是 `codex/phase-61v-commercial-comfyui-connection-probes`，范围是 Phase 61V Commercial Operation ComfyUI Connection Probes：`commercial_operation_comfyui_connection_probes`、`/api/v1/commercial-operations/{operation_id}/comfyui-connection-probes`、Admin Dashboard ComfyUI connection probe 操作面板、从 approved/simulated execution plan 生成可审查的 metadata-only health/queue snapshot plan、route/readiness normalization 和 probe lifecycle state。该阶段不会请求 ComfyUI、不会读取 ComfyUI 队列、不会上传文件、不会提交队列、不会保存密钥值、不会生成媒体、不会发布、不会控制真实账号、不会接入平台分析、不会宣称 ROI 归因，也不会绕过审批。

当前更新（2026-05-21）：PR #60 是 Phase 61T ComfyUI 作业请求草稿，当前开发分支是 `codex/phase-61u-commercial-comfyui-execution-plans`，范围是 Phase 61U 商业运营 ComfyUI 执行预案：`commercial_operation_comfyui_execution_plans`、`/api/v1/commercial-operations/{operation_id}/comfyui-execution-plans`、Admin Dashboard ComfyUI execution plan 操作面板、从 approved/queued job request 生成可审查的 metadata-only 队列模拟预案、执行步骤、模拟检查、操作清单和回滚指引。该阶段不会请求 ComfyUI、不会上传文件、不会提交队列、不会保存密钥值、不会生成媒体、不会发布、不会控制真实账号、不会接入平台分析、不会宣称 ROI 归因，也不会绕过审批。

当前更新（2026-05-20）：PR #57 是 Phase 61Q ComfyUI 交接记录草稿，PR #58 是 Phase 61R ComfyUI 预检草稿，PR #59 是 Phase 61S ComfyUI 适配器配置草稿。当前开发分支是 `codex/phase-61t-commercial-comfyui-job-requests`，范围是 Phase 61T 商业运营 ComfyUI 作业请求：`commercial_operation_comfyui_job_requests`、`/api/v1/commercial-operations/{operation_id}/comfyui-job-requests`、Admin Dashboard ComfyUI job request 操作面板、从 checked preflight 生成可审查的未来队列 payload、安全检查、输出预期、生命周期决策和恢复指引。该阶段只保存 metadata-only 记录，不会请求 ComfyUI、不会上传文件、不会提交队列、不会保存密钥值、不会生成媒体、不会发布、不会控制真实账号、不会接入平台分析、不会宣称 ROI 归因，也不会绕过审批。

当前更新（2026-05-20）：Phase 57A-59C、Phase 60A-60G 和 Phase 61A-61P 已通过 PR #22-#56 合并到 `main`。当前下一分支是 `codex/phase-61q-commercial-comfyui-handoffs`，范围是 Phase 61Q 商业运营 ComfyUI 交接记录：`/api/v1/commercial-operations/{operation_id}/comfyui-handoffs`、Admin Dashboard ComfyUI 交接操作、prompt/workflow payload、准备检查和人工生命周期决策。该阶段只保存元数据交接记录，不会提交 ComfyUI 任务、不会生成媒体、不会自动发布、不会控制真实账号、不会接入平台分析、不会宣称 ROI 归因，也不会绕过审批。

当前更新（2026-05-20）：Phase 57A-59C、Phase 60A-60G 和 Phase 61A-61O 已通过 PR #22-#55 合并到 `main`。当前下一分支是 `codex/phase-61p-commercial-rag-asset-briefs`，范围是 Phase 61P 商业运营 RAG 素材简报生成：`/api/v1/commercial-operations/{operation_id}/asset-requests/generate-rag`、Admin Dashboard 从 RAG 生成素材请求操作、检索 chunk 来源材料、准备检查和检索元数据。该阶段只从已有 RAG 知识检索生成草稿素材请求记录，不会上传或摄取知识文件、不会自动批准素材、不会自动发布内容、不会运行 ComfyUI/OpenClaw/Browser Worker、不会控制真实账号、不会接入平台分析、不会宣称 ROI 归因，也不会绕过审批。


`main` is the Phase 55 stable baseline after PR #17 merged the Phase 43-55 Combined Release Candidate and after post-merge stabilization landed. PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`; PR #1 and PR #15 are closed as superseded after verification. PR #16 was accepted into the Phase 54 branch before PR #17 merged to `main`. Phase 56 was reverted and is not active.

当前更新（2026-05-20）：Phase 57A-59C、Phase 60A-60G 和 Phase 61A-61H 已通过 PR #22-#48 合并到 `main`。当前下一分支是 `codex/phase-61i-commercial-operation-execution-runs`，范围是 Phase 61I 商业运营执行运行记录：`commercial_operation_execution_runs`、`/api/v1/commercial-operations/{operation_id}/execution-runs`、Admin Dashboard 执行运行操作，以及执行运行的创建、编辑、启动、成功、失败、重试、取消或归档。该阶段仍不会发布内容、不会运行 ComfyUI/OpenClaw/Browser Worker、不会控制真实账号，也不会绕过审批。



## Phase 28 OpenClaw Worker Adapter Foundation

状态：已完成。

Phase 28 在客户机 Browser Worker 侧预留 OpenClaw 执行适配层：

- 新增 `worker_client/openclaw/`，包含 `BaseOpenClawProvider`、`MockOpenClawProvider`、`OpenClawRuntime`、OpenClaw action schemas。
- `worker_client runtime` 新增 `GET /openclaw/health`、`GET /openclaw/capabilities`、`POST /openclaw/actions`，当前全部返回 mock。
- 主应用新增 `app/openclaw/`，包含 `OpenClawWorkerClient`、schemas、repository、service。
- 新增 `openclaw_action_logs` 表，用于记录 workspace、worker、action、payload、provider、mock、duration 与 error。
- 新增 API：`GET /api/v1/openclaw/health`、`GET /api/v1/openclaw/capabilities`、`POST /api/v1/openclaw/actions`。
- 新增内置工具 `openclaw_tool`，通过已注册 Browser Worker 调用 mock OpenClaw runtime，并写入 `tool_call_logs`、`openclaw_action_logs`、`browser_security_audit_logs`。
- 新增配置：`OPENCLAW_PROVIDER=mock`、`OPENCLAW_ENABLED=true`、`OPENCLAW_ACTION_TIMEOUT_SECONDS=60`。

边界：Phase 28 只做 OpenClaw Adapter Foundation，不调用真实 OpenClaw，不接 TikTok / YouTube / X，不做账号登录、自动发布、验证码、代理池、指纹绕过或真实平台自动化。

## Phase 27 Customer Machine Worker Bootstrap

状态：已完成。

Phase 27 建立客户机 / Windows / Mac 机器作为 Browser Worker 接入 AI Server 的本地启动基础：

- 新增 `worker_client` 包，包含 `config.py`、`registration.py`、`heartbeat.py`、`runtime.py`、`cli.py` 和 `main.py`。
- 新增 `worker_client/worker_config.example.yaml`，客户机可复制为本地 `worker_config.yaml` 后配置 `server_url`、`workspace_id`、`worker_name`、capabilities、runtime port 和 heartbeat interval。
- 新增 CLI 命令：`python -m worker_client.cli register`、`python -m worker_client.cli heartbeat`、`python -m worker_client.cli serve`、`python -m worker_client.cli start`。
- `registration flow` 调用 `POST /api/v1/browser-workers/register`，一次性接收明文 `worker_secret`，并保存到客户机本地 `worker_state.json`。
- `heartbeat flow` 读取 `worker_state.json`，调用 `POST /api/v1/browser-workers/{worker_id}/heartbeat`，发送 `X-Worker-Secret` 与 Phase 26 signed request headers。
- `local worker runtime` 复用现有 browser-worker 协议，支持 `GET /health`、`POST /sessions`、`POST /actions`、`POST /sessions/{session_id}/close`、`GET /ui-access/capabilities`。
- `worker_config.yaml` 与 `worker_state.json` 已加入 `.gitignore`；`worker_secret` 只允许保存在客户机本地，不写入日志和 docs。

边界：Phase 27 只是 Customer Machine Worker Bootstrap；Phase 28 在此基础上增加 mock OpenClaw Adapter，但仍不调用真实 OpenClaw，不做 TikTok / YouTube / X 自动化、自动登录、Cookie 注入、代理池、指纹绕过、验证码处理或真实平台自动化。

## Phase 26 Browser Worker Security & Access Control

Phase 26 建立 Browser Worker、UI Access、Browser Profile、Browser Action 的基础安全控制层：

- 扩展 `browser_workers`，新增 `worker_secret_hash`、`api_key_hash`、`last_auth_at`、`auth_status`、`allowed_actions`、`allowed_domains`。
- 新增 `BrowserWorkerAuthService`，支持 worker secret 生成、hash、校验、请求签名和签名校验。
- Worker 请求签名使用 `X-Worker-Signature`、`X-Worker-Timestamp`、`X-Worker-Nonce` 和 body hash。
- `browser-worker` 的 `/sessions`、`/actions`、`/sessions/{session_id}/close` 支持签名校验；`/health` 保持无需鉴权。
- 扩展 `browser_ui_access_sessions`，新增 `scopes`、`one_time`、`used_at`、`revoked_reason`、`client_ip`、`user_agent`。
- UI Access Scope 支持 `view`、`control`、`screenshot`、`devtools_placeholder`，token 校验时会检查 scope 和 one-time 状态。
- 新增 `BrowserActionPolicyService`，校验 action type、target domain、profile access、worker capability 和 UI access scope。
- 新增 `BrowserSecurityAuditLog` / `browser_security_audit_logs`，记录 worker auth、UI token、policy block 和 profile access 安全事件。
- 新增 API：`POST /api/v1/browser-workers/{worker_id}/rotate-secret`、`POST /api/v1/browser-workers/{worker_id}/revoke`、`GET /api/v1/browser/security/audit-logs`、`POST /api/v1/browser/security/policy/check`。

边界：Phase 26 是安全基础设施，不实现真实平台账号安全、TikTok / YouTube / X 自动化、自动登录、Cookie 注入、代理池、指纹绕过、验证码处理或完整 RBAC/JWT/OAuth。

## Phase 25 Browser Worker UI Access Placeholder

Phase 25 建立浏览器 UI 接管占位访问层：

- 新增 `browser_ui_access_sessions`。
- 新增 `BrowserUIAccessService`，支持 create / get / revoke / expire / generate_access_token / validate_access_token。
- 数据库只保存 `access_token_hash`，明文 token 只在创建接口返回一次。
- 生成 `remote_control_url`、`live_view_url`、`devtools_url=null`，全部都是 placeholder URL。
- 新增 API：`POST /api/v1/browser/ui-access`、get、revoke、expire、validate。
- browser-worker 新增 `/ui-access/capabilities`，返回 `vnc=false`、`novnc=false`、`devtools=false`、`placeholder=true`。
- `browser_tool` 新增 `create_ui_access` 和 `revoke_ui_access`。

边界：Phase 25 不实现真实 VNC / noVNC / DevTools UI，不做实时浏览器远程画面、平台登录、验证码处理、Cookie 注入、代理池、指纹绕过、TikTok / YouTube / X 或真实平台自动化。

## Phase 24 Human-in-the-loop Browser Control

Phase 24 建立人工接管浏览器控制基础层：

- 新增 `browser_human_control_sessions`，记录 `browser_session_id`、`profile_id`、`worker_id`、`status`、`reason`、`requested_by`、`approved_by`、`started_at`、`completed_at`、`expires_at`。
- 新增 `browser_human_control_events`，记录 `requested`、`approved`、`started`、`completed`、`cancelled`、`expired`、`timeout`、`note` 等事件。
- 扩展 `browser_sessions`：`human_control_status`、`human_control_session_id`、`paused_at`、`resumed_at`。
- 新增 `BrowserHumanControlService`，支持 request / approve / start / complete / cancel / expire / list / get / events。
- 新增 API：`POST /api/v1/browser/human-control/request`、approve、start、complete、cancel、list、get、events。
- `browser_tool` 新增 `request_human_control` 和 `complete_human_control`。
- browser-worker 新增 metadata-level `/human-control/start`、`/human-control/complete`、`/human-control/status/{session_id}`。

边界：Phase 24 不实现 VNC / noVNC / DevTools 真实远程 UI，不做 TikTok / YouTube / X 自动化、自动登录、Cookie 注入、代理池、指纹绕过、验证码自动化或真实平台自动化。

## Phase 23 Browser Profile Health & Recovery

Phase 23 增强 Persistent Browser Profile 的稳定性、恢复能力和生命周期管理：

- 扩展 `browser_profiles`：`health_status`、`last_health_check_at`、`last_error`、`usage_count`、`corrupted_at`、`backup_path`、`last_backup_at`。
- 新增 `browser_profile_usage_logs`，记录 `lock`、`release`、`session_start`、`session_close`、`backup`、`restore`、`recovery`、`cleanup` 等操作。
- 新增 `BrowserProfileHealthService`，支持 health check、warning/corrupted 标记、stale lock recovery、profile path/runtime 校验和 usage count。
- 新增 `BrowserProfileBackupService`，支持 profile backup / restore / list / cleanup，备份路径为 `worker/profile_backups/{workspace_id}/{profile_id}`。
- 新增 `BrowserProfileCleanupService`，支持 deleted / corrupted / unused profiles 的 dry-run 与实际清理。
- 新增 API：`GET /api/v1/browser/profiles/health/summary`、`POST /api/v1/browser/profiles/recover-stale-locks`、`POST /api/v1/browser/profiles/{profile_id}/backup`、`POST /api/v1/browser/profiles/cleanup`、health-check、backups、restore、usage-logs。

边界：Phase 23 不做 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码、真实平台自动化或 autonomous browser planning。

## Phase 22 Persistent Browser Profile Foundation

状态：已完成。

Phase 22 新增持久化 Browser Profile 基础层：

- 新增 `browser_profiles` 表，记录 `profile_name`、`profile_type`、`provider`、`profile_path`、`status`、`locked_by_session_id`、`locked_at`、`last_used_at`。
- 新增 `BrowserProfileService`，支持 `create_profile`、`list_profiles`、`get_profile`、`lock_profile`、`release_profile`、`mark_corrupted`、`delete_profile`、`get_available_profile`。
- `browser_sessions` 新增 `profile_id`、`profile_path`、`persistent_context_enabled`。
- `POST /api/v1/browser/sessions` 支持 `profile_id` 与 `use_persistent_profile=true`。
- `POST /api/v1/browser/sessions/{session_id}/close` 会释放 profile lock。
- `browser-worker` 在 profile-backed session 下使用 Playwright `launch_persistent_context`，profile 文件位于 `worker/profiles/{workspace_id}/{profile_id}`。

边界：Phase 22 不做 TikTok / YouTube / X 自动化、账号登录、Cookie 注入、代理池、指纹绕过、验证码、真实平台自动化或 OpenClaw。

## Phase 21 Browser Worker Reliability

状态：已完成。

Phase 21 在 Phase 19/20 的 Remote Browser Worker 与真实 `browser-worker` 服务之上补齐可靠性基础：

- 新增 `BrowserWorkerHealthService`，按 `BROWSER_WORKER_HEARTBEAT_TIMEOUT_SECONDS` 检测 stale worker，并将过期 worker 标记为 `offline`，写入 `error_message`。
- 新增 `BrowserWorkerSelector`，按 `workspace_id`、`status=online`、capability、capacity 过滤，并选择 least loaded worker。
- 扩展 `browser_workers`：`max_sessions`、`active_sessions`、`max_actions_per_minute`、`current_load`、`priority`、`error_message`，`last_heartbeat_at` 作为 `last_seen` 返回。
- 扩展 `browser_worker_actions`：`retry_count`、`max_retries`。
- 新增 `BrowserSessionCleanupService`，支持 stale session 清理、worker offline/error 后关联 session 标记失败，并写 browser logs。
- 新增 `ScreenshotCleanupService`，支持按 workspace 与 age 手动清理截图，默认 `dry_run=true`。
- 新增 API：`GET /api/v1/browser-workers/health/summary`、`GET /api/v1/browser-workers/available`、`POST /api/v1/browser-workers/{worker_id}/mark-offline`、`POST /api/v1/browser-workers/cleanup-sessions`、`GET /api/v1/browser-workers/{worker_id}/sessions`、`POST /api/v1/browser/screenshots/cleanup`。

边界：Phase 21 只做 Worker Reliability，不做 TikTok / YouTube / X 自动化、登录、Cookie 注入、代理池、指纹绕过、验证码、OCR、视觉 AI、OpenClaw、真实平台自动化或 autonomous browser planning。

## Phase 20 Real Browser Worker Service

状态：已完成。

Phase 20 新增真正独立运行的 `browser-worker` 服务：

- `worker/main.py` 暴露 `GET /health`、`POST /sessions`、`POST /actions`、`POST /sessions/{session_id}/close`。
- `worker/browser_worker/playwright_runtime.py` 使用 headless Playwright Chromium。
- Docker Compose 新增 `browser-worker` 服务并暴露 `9100`。
- API Server 调用链路为 `RemoteBrowserProvider -> BrowserWorkerClient -> http://browser-worker:9100`。
- 新增运行配置 `BROWSER_WORKER_DEFAULT_URL=http://browser-worker:9100`。
- 截图保存到 `worker/screenshots/{workspace_id}/{remote_session_id}/{filename}.png`。

边界：Phase 20 仍不支持 TikTok / YouTube / X 自动化、登录、Cookie 注入、代理池、指纹绕过、验证码、OCR、视觉 AI、OpenClaw 或 autonomous browser agent。当前是本地 Docker Worker 基础，不是生产级外部 Worker 集群。

更新日期：2026-05-12

本文是中文主开发状态文档，记录 `E:\ai-operations-system` 的真实工程状态。当前状态：Phase 1 到 Phase 28 已完成。

## 总体状态

当前系统已经具备：

- FastAPI、PostgreSQL、Redis、Qdrant、Docker Compose。
- SQLAlchemy ORM、Alembic migration、Workspace/User/API Key 隔离。
- Redis Queue、Scheduler、TaskExecutor、任务事件、任务日志、取消、重试、超时与观测 summary。
- LLM Client Layer，默认 `mock`，支持本地 Ollama `mistral`。
- Embedding Pipeline，默认 `mock`，支持本地 Ollama `bge-m3`。
- Knowledge Lifecycle：`documents`、`document_chunks`、`collections_metadata`。
- Agentic RAG、Hybrid Search、Reranker Layer、RAG Eval / Debug Trace。
- File Upload Pipeline：PDF、DOCX、TXT、MD、CSV。
- Tool Calling Foundation：`BaseTool`、`ToolRegistry`、builtin tools、`tool_call_logs`。
- Memory Foundation：`conversation_sessions`、`conversation_messages`、`agent_memories`、`memory_operation_logs`。
- Multi-Agent Foundation：`AgentRegistry`、`agent_runs`、`agent_messages`、`agent_handoffs`、固定 Agent Chain。
- Agent Planning Foundation：`plans`、`plan_steps`、`plan_reviews`、`SimplePlannerAgent`、Plan Execution Flow。
- ContentAgent 示例 Agent。
- 中英文 Docs System、`PROJECT_OVERVIEW.md`、`CURRENT_RUNTIME.md`、Docs Runtime Verification。
- Customer Machine Worker Bootstrap：`worker_client`、`worker_config.example.yaml`、本地 `worker_config.yaml`、本地 `worker_state.json`、registration flow、heartbeat flow、local worker runtime。

## 已完成 Phase

| Phase | 状态 | 说明 |
| --- | --- | --- |
| Phase 1 | 已完成 | Docker、PostgreSQL、Redis、Qdrant、FastAPI、health check。 |
| Phase 2 | 已完成 | ORM、Task System、Redis Queue、Scheduler、Task API。 |
| Phase 2.5 | 已完成 | LLM Client Layer、MockProvider、LocalProvider、ServerProvider、Prompt Manager。 |
| Phase 3 | 已完成 | Embedding Pipeline、Qdrant Collection Layer、RAG ingest/search。 |
| Phase 3.5 | 已完成 | embedding 归一化、score normalizer、collection health、RAG debug API。 |
| Phase 4 | 已完成 | 单一 Agentic RAG Orchestrator。 |
| Phase 4.5 | 已完成 | Agentic RAG Task Executor handler 与 task API。 |
| Phase 4.6 | 已完成 | Ollama Mistral local LLM 接口与 LLM health check。 |
| Phase 5 | 已完成 | BaseAgent、ContentAgent、content_generation task。 |
| Phase 6 | 已完成 | Knowledge Lifecycle、source versioning、delete/reingest、active-only retrieval。 |
| Phase 6.5 | 已完成 | users、workspaces、workspace_members、api_keys、workspace middleware。 |
| Phase 7 | 已完成 | Ollama bge-m3 local embedding，自动检测 embedding dimension。 |
| Phase 8 | 已完成 | `rag_eval_runs`、`rag_eval_items`、Agentic RAG trace。 |
| Phase 9 | 已完成 | Reranker Provider Layer，mock/local provider，rerank trace。 |
| Phase 10 | 已完成 | Dense + Keyword -> Merge -> Rerank -> LLM 的 Hybrid Search。 |
| Phase 10.5 | 已完成 | 中英文 Docs System、PROJECT_OVERVIEW、CURRENT_RUNTIME、Docs SSOT。 |
| Phase 11 | 已完成 | File Upload Pipeline 与 Docs Runtime Verification。 |
| Phase 12 | 已完成 | Task Reliability & Observability，`task_events`、`task_logs`、cancel/retry、timeout、duration_ms、summary API。 |
| Phase 13 | 已完成 | Tool Calling Foundation，`BaseTool`、`ToolRegistry`、builtin tools、`tool_call_logs`、Tool API、Agent 手动 tool call。 |
| Phase 14 | 已完成 | Memory Foundation，`conversation_sessions`、`conversation_messages`、`agent_memories`、`memory_operation_logs`、Memory API、Agentic RAG `memory_trace`。 |
| Phase 15 | 已完成 | Multi-Agent Foundation，`AgentRegistry`、`agent_runs`、`agent_messages`、`agent_handoffs`、固定 Agent Chain、ToolAgent、Memory 集成基础。 |
| Phase 16 | 已完成 | Agent Planning Foundation，`plans`、`plan_steps`、`plan_reviews`、`SimplePlannerAgent`、可观测 Plan Execution Flow、step duration/error、cancel、memory_trace。 |
| Phase 17 | 已完成 | Browser Automation Adapter Foundation，`browser_sessions`、`browser_actions`、`browser_action_logs`、`BrowserProvider`、`MockBrowserProvider`、`PlaywrightBrowserProvider` placeholder、`BrowserService`、`browser_tool`、Browser API。 |
| Phase 18 | 已完成 | Playwright Local Provider Integration，`PlaywrightLocalProvider`、`BROWSER_PROVIDER=playwright_local`、本地 headless Chromium、`browser_id`、`page_id`、`provider_session_metadata`、`selector`、`target_url`、`screenshot_path`、`page_title`、Screenshot System、`get_page_content`。 |
| Phase 19 | 已完成 | Remote Browser Worker Foundation，`RemoteBrowserProvider`、`BrowserWorkerClient`、`browser_workers`、`browser_worker_sessions`、`browser_worker_actions`、Worker Registration、Worker Heartbeat、Worker Runtime Mock、`BROWSER_PROVIDER=remote`。 |
| Phase 20 | 已完成 | Real Browser Worker Service，独立 `browser-worker` Docker 服务、`worker/main.py`、`worker/browser_worker/playwright_runtime.py`、Playwright Chromium、`http://browser-worker:9100`、`worker/screenshots`。 |
| Phase 21 | 已完成 | Browser Worker Reliability，`BrowserWorkerHealthService`、`BrowserWorkerSelector`、`BrowserSessionCleanupService`、`ScreenshotCleanupService`、capacity、least loaded selection、action retry、screenshot cleanup。 |
| Phase 22 | 已完成 | Persistent Browser Profile Foundation，`browser_profiles`、`BrowserProfileService`、Profile Lock / Profile Release、`profile_id`、`profile_path`、`persistent_context_enabled`、`launch_persistent_context`、`worker/profiles`。 |
| Phase 23 | 已完成 | Browser Profile Health & Recovery，`BrowserProfileHealthService`、`BrowserProfileBackupService`、`BrowserProfileCleanupService`、`browser_profile_usage_logs`、`health_status`、`usage_count`、stale lock recovery、profile backup、profile cleanup。 |
| Phase 24 | 已完成 | Human-in-the-loop Browser Control，`BrowserHumanControlService`、`browser_human_control_sessions`、`browser_human_control_events`、session paused/resumed、`request_human_control`、`complete_human_control`。 |
| Phase 25 | 已完成 | Browser Worker UI Access Placeholder，`BrowserUIAccessService`、`browser_ui_access_sessions`、`access_token_hash`、placeholder URL、token validate/revoke/expire、`/ui-access/capabilities`、`create_ui_access`、`revoke_ui_access`。 |
| Phase 26 | 已完成 | Browser Worker Security & Access Control，`BrowserWorkerAuthService`、`worker_secret_hash`、signed worker request、UI Access Scope、`BrowserActionPolicyService`、`browser_security_audit_logs`。 |
| Phase 27 | 已完成 | Customer Machine Worker Bootstrap，`worker_client`、`worker_config.example.yaml`、本地 `worker_config.yaml`、本地 `worker_state.json`、`python -m worker_client.cli register`、`heartbeat`、`serve`、`start`、registration flow、heartbeat flow、local worker runtime。 |
| Phase 28 | 已完成 | OpenClaw Worker Adapter Foundation，`worker_client/openclaw`、`MockOpenClawProvider`、`OpenClawRuntime`、服务端 `OpenClawWorkerClient`、`openclaw_tool`、`openclaw_action_logs`、mock `/openclaw/*` runtime routes。 |

## Phase 15 完成内容

Multi-Agent Foundation：

- 新增 `app/multi_agent/`，包含 `services` 与 `repositories`。
- 新增 `AgentRegistry`，支持 `register_agent`、`get_agent`、`list_agents`、enable/disable 和 agent metadata。
- 新增数据库表：`agent_runs`、`agent_messages`、`agent_handoffs`。
- 新增 `MultiAgentService`，支持 `create_run`、`append_message`、`handoff`、`execute_single_agent`、`execute_agent_chain`、`get_run`、`list_runs`。
- 注册 Agent：`content_planner`、`rag_agent`、`content_agent`、`review_agent`、`runtime_agent`、`tool_agent`。
- 固定 Agent Chain：`content_planner -> rag_agent -> content_agent -> review_agent`。
- `ToolAgent` 可调用已有 `ToolRegistry` 内置工具：`rag_search_tool`、`file_search_tool`、`create_task_tool`、`get_task_status_tool`、`current_runtime_tool`。
- 新增 API：`GET /api/v1/agents/registry`、`POST /api/v1/multi-agent/runs`、`GET /api/v1/multi-agent/runs`、`GET /api/v1/multi-agent/runs/{run_id}`、`POST /api/v1/multi-agent/runs/{run_id}/execute-chain`、`GET /api/v1/multi-agent/runs/{run_id}/messages`、`GET /api/v1/multi-agent/runs/{run_id}/handoffs`。
- run output 包含 `agents_involved`、message history、handoff records 和 `handoff_trace`。
- 支持 `session_id`，并可复用 Phase 14 Memory Foundation 的 recent messages 与 memory context。

Phase 15 明确不包含：

- autonomous planner。
- ReAct。
- Browser Agent。
- Playwright、OpenClaw、Selenium。
- 外部平台 API 或真实自动化执行。

## Phase 16 完成内容

Agent Planning Foundation：

- 新增 `app/planning/`，包含 `services` 与 `repositories`。
- 新增数据库表：`plans`、`plan_steps`、`plan_reviews`。
- 新增 `SimplePlannerAgent`，当前为 rule-based planner，输出有限、确定性的结构化 plan。
- 新增 `PlanningService`，支持 `create_plan`、`create_steps`、`execute_step`、`execute_plan`、`review_plan`、`cancel_plan`、`get_plan`、`list_plans`。
- 新增 API：`POST /api/v1/plans`、`GET /api/v1/plans`、`GET /api/v1/plans/{plan_id}`、`POST /api/v1/plans/{plan_id}/execute`、`POST /api/v1/plans/{plan_id}/cancel`、`GET /api/v1/plans/{plan_id}/steps`、`GET /api/v1/plans/{plan_id}/reviews`。
- Plan Execution Flow：plan -> steps -> AgentRegistry 或 ToolRegistry -> step output / duration / error -> review -> final result。
- step 支持 `pending`、`running`、`completed`、`failed`、`skipped`，并在 service 层支持 retry / skip。
- Planning 支持 `session_id` 与 `memory_trace`，但不做高级长期记忆规划。

Phase 16 明确不包含：

- autonomous AGI planner。
- tree-of-thought。
- recursive planning。
- 无限 Agent loop。
- ReAct。
- Browser Agent / Playwright / OpenClaw / Selenium。

## Phase 17 完成内容

Browser Automation Adapter Foundation：

- 新增 `app/browser/`，包含 providers、repositories、services。
- 新增数据库表：`browser_sessions`、`browser_actions`、`browser_action_logs`。
- 新增 `BrowserProvider` 接口：`create_session`、`close_session`、`navigate`、`click`、`type_text`、`scroll`、`screenshot`、`get_page_content`。
- 新增 `MockBrowserProvider`，当前默认使用，不启动真实浏览器。
- 新增 `PlaywrightBrowserProvider` placeholder，只返回清晰的未执行响应。
- 新增 `BrowserService`，支持 workspace 隔离的 session 创建、action 执行、session/action 查询、log 查询、`duration_ms` 和错误记录。
- 新增 API：`POST /api/v1/browser/sessions`、`GET /api/v1/browser/sessions`、`POST /api/v1/browser/actions`、`GET /api/v1/browser/actions/{session_id}`、`GET /api/v1/browser/logs/{session_id}`。
- 新增内置工具 `browser_tool`，支持 `navigate`、`click`、`type_text`、`screenshot`，全部走 `MockBrowserProvider`。
- Planning step 支持 `tool_name=browser_tool`。

Phase 17 明确不包含：

- Browser Agent。
- autonomous browser planning。
- Playwright / Selenium / OpenClaw 真实执行。

## Phase 18 完成内容

Playwright Local Provider Integration：

- 新增 `app/browser/providers/playwright_provider.py`，实现 `PlaywrightLocalProvider`，provider name 为 `playwright_local`。
- 支持 `create_session`、`close_session`、`navigate`、`click`、`type_text`、`screenshot`、`get_page_content`。
- `BrowserSession` 新增 `browser_id`、`page_id`、`provider_session_metadata`。
- `BrowserAction` 新增 `selector`、`target_url`、`screenshot_path`、`page_title`。
- 新增 Screenshot System：`screenshots/{workspace_id}/{session_id}/{filename}.png`。
- 新增 API：`GET /api/v1/browser/screenshot/{session_id}/{filename}`。
- `browser_tool` 扩展支持 `get_page_content`，并继续记录 `tool_call_logs`。
- Docker 镜像安装 Playwright Python 与 Chromium，仅安装 Chromium。

Phase 18 安全边界：

- 默认仍为 `BROWSER_PROVIDER=mock`。
- 使用 `BROWSER_PROVIDER=playwright_local` 时只允许 `example.com`、本地测试页面、静态 `file://` 页面。
- 不做 TikTok / YouTube / X 自动化。
- 不做自动登录、Cookie 注入、指纹绕过、代理池、验证码自动化。
- 不做 OCR、视觉 AI、autonomous browser planning、Browser Worker 或真实平台自动化。

## Phase 19 完成内容

Remote Browser Worker Foundation：

- 新增 `app/browser/remote/`，包含 `client`、`schemas`、`services`。
- 新增 `BrowserWorkerClient`，支持 `create_session`、`close_session`、`execute_action`、`health_check`。
- 新增 `RemoteBrowserProvider`，provider name 为 `remote`，通过注册 worker 的 `base_url` 分发 browser action。
- 新增数据库表：`browser_workers`、`browser_worker_sessions`、`browser_worker_actions`。
- 新增 API：`POST /api/v1/browser-workers/register`、`POST /api/v1/browser-workers/{worker_id}/heartbeat`、`GET /api/v1/browser-workers`。
- 新增 mock worker runtime：`GET /api/v1/browser-worker-runtime/health`、`POST /api/v1/browser-worker-runtime/sessions`、`POST /api/v1/browser-worker-runtime/actions`、`POST /api/v1/browser-worker-runtime/sessions/{session_id}/close`。
- `BrowserService` 支持 `BROWSER_PROVIDER=remote`。
- `browser_tool` 继续通过 `BrowserService` 执行，因此 remote provider 模式下仍保留 `tool_call_logs` 与 `browser_action_logs`。

Phase 19 明确不包含：

- 真实外部 Worker 部署。
- TikTok / YouTube / X 自动化。
- 账号登录、自动发布、Cookie 注入、指纹绕过、代理池、验证码。
- autonomous browser agent。
- TikTok / YouTube / X 平台自动化。
- OCR、视觉 AI、真实登录流程。

## 当前运行默认值

```text
LLM_PROVIDER=mock
EMBEDDING_PROVIDER=mock
RERANKER_PROVIDER=mock
DEFAULT_SEARCH_MODE=hybrid
BROWSER_PROVIDER=mock
```

本地模型接口已支持：

- `LOCAL_LLM_MODEL=mistral`
- `LOCAL_EMBEDDING_MODEL=bge-m3`

当前 Multi-Agent 不新增环境变量。完整运行态见 `docs/CURRENT_RUNTIME.md`。

## 当前限制

- Multi-Agent 当前是固定链路基础层，不做动态规划、自动路由或 ReAct。
- local reranker 仍是 placeholder。
- Keyword retrieval 仍是 PostgreSQL `ILIKE` 和简单关键词评分。
- Memory 仍是 PostgreSQL 文本检索基础层，不包含 vector memory、graph memory 或 autonomous memory planning。
- 不包含 Browser Agent、Playwright、OpenClaw、Selenium。
- 不包含 Elasticsearch、OpenSearch、真实 BM25。
- 不包含完整 RBAC、JWT、OAuth。
- 不包含前端 Dashboard、Prometheus、Grafana。

## 固定验证流程

每个 Phase 完成后必须执行：

```powershell
python -m pytest
docker compose up --build -d
python scripts/verify_docs_runtime.py
```

只有 docs verifier 输出 `SUMMARY: PASS` 后，docs 才视为与当前 runtime 同步。

## Phase 29 Worker Client Packaging & Worker Console Foundation

已完成：

- 新增 `Worker Runtime Manager`：`worker_client/runtime_manager.py`，支持 `start_runtime`、`stop_runtime`、`restart_runtime`、`runtime_health`、`start_heartbeat`、`stop_heartbeat`、`runtime_state`。
- 新增本地状态层：`worker_client/status.py`，运行时写入 `worker_client/runtime_state/status.json`，记录 `worker_id`、`worker_name`、`workspace_id`、`server_url`、`runtime_running`、`heartbeat_running`、`registered`、`last_heartbeat_at`、`last_error`、`current_status`、`openclaw_enabled`、`browser_enabled`。
- 新增本地日志层：`worker_client/logging.py`，写入 `worker_client/logs/worker.log`，支持简单轮转和 secret 脱敏。
- 扩展 `worker_client/runtime.py` 本地管理 API：`GET /local/status`、`GET /local/health`、`POST /local/runtime/start`、`POST /local/runtime/stop`、`POST /local/runtime/restart`、`POST /local/heartbeat/start`、`POST /local/heartbeat/stop`、`GET /local/logs`。
- 新增 `worker_client/local_api_client.py`，作为未来 Worker Console Foundation / GUI 的 Python client。
- 新增 Packaging Scripts：`packaging/windows_start_worker.ps1`、`packaging/mac_start_worker.sh` 等 Windows/Mac 基础脚本。
- 新增 `Desktop Runtime Placeholder`：`worker_client/desktop/README.md` 与 `placeholder.py`。

明确不包含：GUI、系统托盘、Electron、Tauri、PySide、exe/dmg 打包、真实浏览器远程画面、真实平台自动化、TikTok / YouTube / X 自动化、登录自动化、Cookie 注入、指纹绕过、代理池或验证码自动化。

## Phase 30 Worker Console GUI Foundation

已完成：

- 新增 `worker_console` 独立前端项目，技术栈为 Vite、React、TypeScript、Tailwind。
- 默认本地 API：`VITE_LOCAL_WORKER_API=http://127.0.0.1:9100`。
- 新增 Dashboard、Runtime Control、Logs、Connection Info 页面区域。
- 新增 `worker_console/src/api/localWorkerClient.ts`，支持 `getStatus`、`getHealth`、`getLogs`、`startRuntime`、`stopRuntime`、`restartRuntime`、`startHeartbeat`、`stopHeartbeat`。
- 本地 API 不可用时显示 `Worker API unreachable`、`请确认 worker_client 是否启动`、`请确认端口是否为 9100`。

明确不包含：system tray、auto update、Electron、Tauri、PySide、no exe / dmg、TikTok / YouTube / X 自动化、登录自动化、Cookie 注入、代理池、指纹绕过、验证码自动化或真实平台自动化。
## Phase 31：Worker Console Desktop App Foundation

状态：已完成。

本阶段新增 `worker_console_desktop`，使用 Tauri + React + Vite + TypeScript + Tailwind 建立本地 Worker Console 桌面壳基础。桌面端默认通过 `VITE_LOCAL_WORKER_API=http://127.0.0.1:9100` 调用 Phase 29 的 Local API，并显示 Worker status、runtime state、heartbeat state、connection info 和 logs。

关键文件：

- `worker_console_desktop/package.json`
- `worker_console_desktop/src/api/localWorkerClient.ts`
- `worker_console_desktop/src/main.tsx`
- `worker_console_desktop/src-tauri/tauri.conf.json`
- `worker_console_desktop/src-tauri/src/main.rs`

开发命令：

```powershell
cd worker_console_desktop
npm install
npm run build
npm run tauri dev
```

边界：当前没有正式安装包、no exe / dmg、no system tray、no auto update、无开机自启、无真实平台自动化。

## Phase 32：Worker Console System Tray & Desktop Runtime Foundation

状态：已完成。

本阶段将 `worker_console_desktop` 升级为桌面 Runtime 基础，新增 Tauri System Tray、Minimize To Tray、Tray Runtime Control、Desktop Status Sync 和 AutoStart Placeholder。

已完成：

- `worker_console_desktop/src-tauri/src/main.rs` 中接入 System Tray。
- 托盘菜单：Show Console、Hide Window、Start Runtime、Stop Runtime、Restart Runtime、Start Heartbeat、Stop Heartbeat、Refresh Status、Quit。
- `worker_console_desktop/src-tauri/desktop-runtime.json` 默认 `minimize_to_tray=true`。
- `worker_console_desktop/src/settings.ts` 和 `settings.example.json` 支持 `localWorkerApi`、`minimizeToTray`、`refreshIntervalMs`。
- UI 显示 connected、reconnecting、disconnected、online、offline、error、last successful sync 和 last error。
- Logs Panel 支持 auto refresh、manual refresh、error highlight、clear display 和 last updated time。
- `worker_console_desktop/autostart/` 仅作为 AutoStart Placeholder。

边界：当前没有正式 installer、没有 exe / dmg、没有真正开机自启、没有 auto-update、没有远程 shell、没有任意命令执行、没有真实平台自动化。

## Phase 33: Conversation Runtime Foundation



 `conversation_threads`, `conversation_events`  `conversation_messages.thread_id`, `ConversationService`, `run_conversation_turn`, Conversation APIs, Worker Console Chat Panel Foundation, Event Timeline, polling event feed.

 `message_received`, `planning_started`, `plan_created`, `agent_started`, `tool_called`, `worker_action_started`, `worker_action_completed`, `assistant_response`, `error`.

  Conversation Runtime Foundation  WebSocket/SSE  OpenClaw  ComfyUI  TikTok / YouTube / X Cookie

## Phase 34: Remote Browser Runtime Foundation

状态：已完成。

Phase 34 建立真正的远程浏览器运行时基础。AI Server 现在可以通过 `app/browser/providers/remote_provider.py` 选择远程 Worker，把 Browser Action 分发给客户机 Worker，由 `worker_client/browser_runtime` 里的 Playwright Runtime 执行基础浏览器动作。

已完成：

- 新增数据库表和模型：`browser_runtime_sessions`。
- 新增服务：`BrowserRuntimeSessionService`，负责远程 session 创建、查询、导航、截图、页面内容获取、关闭和 activity 更新。
- 新增 API：`/api/v1/browser-runtime/sessions` 及 navigate / screenshot / page / close 子接口。
- 新增 Worker Runtime API：`/browser/session/create`、`/browser/session/{session_id}/navigate`、`/browser/session/{session_id}/screenshot`、`/browser/session/{session_id}/page`、`/browser/session/{session_id}/close`。
- 新增截图存储：`storage/browser_screenshots`，由 `BROWSER_RUNTIME_SCREENSHOT_DIR` 配置。
- Worker Console Web / Desktop 新增 Browser Sessions Panel。
- 客户机安装文档新增 `playwright install chromium`。

边界：当前不做 stealth browser、代理池、Cookie 注入、验证码绕过、TikTok / YouTube / X 自动化、远程桌面流、DevTools 远程控制、真实 OpenClaw 或 ComfyUI。

## Phase 35B: Real Client Worker E2E Validation Plan

状态：已完成验证计划与脚本。

本阶段新增 `scripts/validate_real_client_worker_e2e.py`，用于真实客户机 Worker 在线后验证完整链路：AI Server -> RemoteBrowserProvider -> BrowserWorkerSelector -> 真实客户机 `worker_client` -> 本地 `browser_runtime` -> 本地 Playwright Chromium -> 截图 / 页面内容 / 状态回传。

已完成：

- E2E 验证脚本，支持 `server_url`、`workspace_id`、`user_id`、`expected_worker_name`。
- JSON 输出和 exit code：`0=PASS`、`1=FAIL`、`2=SKIPPED`。
- 找不到 `expected_worker_name` 时返回 `SKIPPED`，原因是 `real client worker not online`，不会执行浏览器动作。
- 新增 `docs/zh/REAL_CLIENT_WORKER_E2E.md` 与 `docs/en/REAL_CLIENT_WORKER_E2E.md`。
- Swagger validation flow 和 Worker Console validation checklist 已文档化。

边界：当前不伪造真实客户机 E2E 成功，不做 TikTok / YouTube / X 自动化、登录、Cookie 注入、代理池、指纹绕过、验证码自动化、真实平台自动化、OpenClaw real device 或 ComfyUI。

## Phase 35A: Browser Runtime Observability & Replay

状态：已完成。

Phase 35A 增强 Phase 34 Remote Browser Runtime 的可观测性和调试能力，新增 `browser_runtime_events`、`browser_runtime_snapshots`、`browser_runtime_replays`，并新增 `BrowserRuntimeObservabilityService`。

已完成：

- Timeline Event Flow：`session_created`、`navigate_started`、`navigate_completed`、`screenshot_started`、`screenshot_completed`、`page_snapshot_captured`、`action_failed`、`session_closed`、`replay_requested`。
- Snapshot Storage：页面 HTML/TXT、错误 JSON 和 replay JSON 写入 `BROWSER_RUNTIME_SNAPSHOT_DIR=storage/browser_runtime_snapshots`；截图继续使用 `storage/browser_screenshots`。
- Replay Metadata Flow：只生成 metadata-only replay，不重新执行浏览器动作。
- Failure Debug：失败动作记录 worker_id、action_type、target/url、error、duration_ms、last known url、last page title。
- 新增 API：events、snapshots、replay、replay export。
- Worker Console Web/Desktop Browser Sessions Panel 新增 Timeline、Screenshot history、Page snapshots、Replay metadata、Refresh events、Refresh snapshots。

边界：当前不是 live stream，不是 VNC/noVNC，不是 DevTools remote control，不重新执行 replay，不做 TikTok / YouTube / X、登录、Cookie 注入、代理池、指纹绕过、验证码或真实平台自动化。

## Phase 36: Server Admin Dashboard Foundation

Status: completed.

Phase 36 新增 `admin_dashboard`，这是一个独立的 Vite + React + TypeScript + Tailwind Admin Dashboard Foundation，用于 read-only monitoring AI Server、Browser Workers、Browser Runtime、Timeline、Snapshots、Replay metadata、Tasks、Conversation、OpenClaw mock、Audit Logs、RAG / Documents。

Completed:

- `admin_dashboard/package.json`
- `admin_dashboard/src/main.tsx`
- `admin_dashboard/src/styles.css`
- `admin_dashboard/src/api/client.ts`
- `docs/zh/ADMIN_DASHBOARD.md`
- `docs/en/ADMIN_DASHBOARD.md`

Pages: Overview, Workers, Browser Runtime, Conversations, Tasks, OpenClaw, Audit Logs, RAG / Documents, Settings.

API modules: `workersApi`, `browserRuntimeApi`, `conversationsApi`, `tasksApi`, `openclawApi`, `auditApi`, `ragApi`.

Runtime config: `VITE_AI_SERVER_API=http://localhost:8000`, `VITE_WORKSPACE_ID=demo-workspace`, `VITE_USER_ID=demo-user`.

Boundary: read-only monitoring foundation, no login UI, no permission UI, no publishing business flow, no real social platform control, no production-grade operations backend.

## Phase 37：Conversation Runtime Frontend Integration

状态：已完成，Phase 37。

Phase 37 将 Conversation Runtime 接入 Server Admin Dashboard、Worker Console Web 与 Worker Console Desktop。当前能力是 Conversation frontend integration 和基础对话入口，不是完整 ChatGPT UI，也不是 WebSocket / SSE streaming。

已完成：

- Admin Dashboard Conversation page：`admin_dashboard` 的 Conversations 页面支持 create thread、thread list、thread detail、message list、event timeline、send message、run conversation、refresh messages、refresh events。
- Admin Dashboard client：新增 `admin_dashboard/src/api/conversationClient.ts`，支持 `createThread`、`listThreads`、`getThread`、`sendMessage`、`listMessages`、`listEvents`、`runConversation`。
- Worker Console Chat Panel：`worker_console` 支持 AI Server URL、Workspace ID、User ID 配置，支持 create thread、send and run、Polling Event Timeline、AI Server connected / disconnected / unreachable 状态。
- Desktop Chat Panel：`worker_console_desktop` 同步 Chat Panel 基础能力；Tauri native validation 仍取决于客户机 Rust/MSVC 环境。
- Polling Event Timeline：前端通过 `GET /api/v1/conversations/{thread_id}/events` 手动刷新或 5 秒 polling，展示 `event_type`、`message`、`created_at`、`payload JSON`。
- Frontend config：`VITE_AI_SERVER_API=http://localhost:8000`，`VITE_WORKSPACE_ID=demo-workspace`，`VITE_USER_ID=demo-user`。
- Development CORS：后端通过 `CORS_ALLOWED_ORIGINS` 允许 `http://localhost:5173`、`http://127.0.0.1:5173`、`http://localhost:5180`、`http://127.0.0.1:5180`、`tauri://localhost` 等开发来源。

边界：当前不是 WebSocket，not WebSocket；当前不是 SSE，not SSE；当前不是完整 ChatGPT UI，not a full ChatGPT UI；不做 TikTok / YouTube / X 自动化，不做登录、Cookie 注入、代理池、指纹绕过、验证码自动化、真实平台自动化、真实 OpenClaw 或 ComfyUI。

## Phase 38：Conversation Runtime Tool Execution Bridge（已完成）

已完成：
- 新增 `ConversationToolRouter`（`app/conversation/tool_router.py`），按用户消息进行 deterministic rule-based routing，不是 autonomous agent。
- Conversation run 支持 `route_selected`、`tool_execution_started`、`tool_execution_completed`、`tool_execution_failed`、`agent_execution_started`、`agent_execution_completed`、`planning_execution_started`、`planning_execution_completed`、`bridge_fallback`、`bridge_error` 等事件。
- `POST /api/v1/conversations/{thread_id}/run` 返回 `route_name`、`selected_tool`、`events_created`、`success`、`summary`、`result_metadata`。
- Browser Bridge 支持把“打开网页并截图”组合为 `browser_tool` create session -> navigate -> screenshot -> get page -> close session。
- OpenClaw mock bridge 只调用 `openclaw_tool` mock，不调用真实 OpenClaw 或真实设备。
- RAG bridge 调用 `rag_search_tool`，缺少 `collection_name` 时返回清晰提示。
- Content bridge 调用 `ContentAgent`。
- Planning bridge 调用 `PlanningService` 创建 plan 和 steps，不自动执行真实平台发布。
- Admin Dashboard、Worker Console、Worker Console Desktop 均展示 route selected、selected tool、tool status、result summary、metadata panel。

边界：当前不是 autonomous agent，not autonomous agent；不是 WebSocket，not WebSocket；不是 SSE，not SSE；不做 TikTok / YouTube / X 自动化、登录、Cookie 注入、代理池、指纹绕过、验证码自动化、真实平台发布、真实 OpenClaw 或 ComfyUI。

## Phase 39：Conversation Execution Review & Approval Flow（已完成）

状态：已完成。

Phase 39 为 Conversation Runtime 增加执行前审核 / 人工确认 / 修改 / 取消的基础门禁，避免一句话直接触发高风险 Tool、Browser、OpenClaw mock 或未来平台动作。

已完成：

- 新增 `conversation_approvals` 表，记录 `route_name`、`selected_tool`、`risk_level`、`approval_status`、`proposed_action`、`proposed_payload`、reviewer 信息和状态时间。
- 新增 `ConversationApprovalService`，支持 create approval、approve、reject、cancel、expire pending、mark executed。
- 新增 `ConversationRiskPolicy`，支持 low / medium / high 风险策略。
- `POST /api/v1/conversations/{thread_id}/run` 支持 `auto_safe`、`review_first`、`execute_after_approval`。
- Tool Execution Gate：medium/high risk 未审批时不得执行；approved 后通过 execute API 执行；executed 后不能重复执行。
- 新增 approval events：`approval_required`、`approval_created`、`approval_approved`、`approval_rejected`、`approval_cancelled`、`approval_expired`、`approval_executed`、`execution_blocked_pending_approval`、`execution_after_approval_started`、`execution_after_approval_completed`、`execution_after_approval_failed`。
- 新增 Approval API：`GET /api/v1/conversations/{thread_id}/approvals`、`GET /api/v1/conversation-approvals/{approval_id}`、approve、reject、cancel、execute。
- Admin Dashboard、Worker Console、Worker Console Desktop 增加 pending approvals panel，展示 proposed action preview、proposed payload JSON、risk badge、approve / reject / cancel / execute approved action。

边界：当前不是完整权限系统，not a full permission system；不是 WebSocket/SSE；不做真实平台发布、TikTok / YouTube / X 自动化、登录、Cookie 注入、代理池、指纹绕过、验证码自动化、真实 OpenClaw 或 ComfyUI。
## Phase 40：Conversation Execution Templates & Playbooks

状态：已完成。

本阶段新增 `conversation_playbooks` 与 `conversation_playbook_runs`，把常见 Conversation 执行流程沉淀为可复用模板。核心实现包括 `ConversationPlaybookService`、`ConversationPlaybookExecutor`、内置 Playbooks、Playbook Runs、Step Timeline 和 Approval integration。

已完成内置模板：
- `browser_search_summary`
- `browser_screenshot_report`
- `rag_answer`
- `content_generation`
- `trend_research_draft`
- `openclaw_mock_device_check`

安全边界：
- medium / high risk step 必须继续走 Phase 39 approval gate。
- `review_first`、`auto_safe`、`execute_after_approval` 继续生效。
- 当前不是完整 workflow builder。
- Current boundary marker: not a full workflow builder.
- 当前不是 autonomous agent。
- 当前不做真实社媒发布、登录、验证码、代理、指纹或真实 OpenClaw。

## Phase 41：Playbook Run Artifacts & Output Library

状态：已完成。

Phase 41 新增 `output_artifacts`，把 Conversation、Playbook、Tool、Browser Runtime、RAG、ContentAgent、Planning 和 OpenClaw mock 的执行结果沉淀为 Output Library。

已完成：
- `OutputArtifactService`：支持 create / list / get / update / soft delete / export / create from Playbook Run / create from Conversation message / create from Browser Runtime snapshot。
- Playbook 完成后自动生成 artifact：`content_generation` 生成 `content_draft`，`browser_screenshot_report` 生成 `screenshot` 和 `report`，`rag_answer` 生成 `rag_answer`，planning 生成 `plan`，OpenClaw mock 生成 `json`。
- Conversation assistant message 支持 Save as Artifact。
- 导出支持 markdown / json / txt。
- 输出文件写入 `storage/output_artifacts/{workspace_id}/{artifact_id}/`。
- 事件包括 `artifact_created`、`artifact_exported`、`artifact_deleted`、`artifact_linked_to_playbook_run`。
- Admin Dashboard / Worker Console / Worker Console Desktop 增加 Output Library / generated artifacts 展示。

边界：
- 当前不是完整素材管理系统，not a full DAM。
- 不接 S3 / MinIO。
- 不做真实平台发布资产管理。
- 不做 TikTok / YouTube / X、登录、验证码、代理、指纹、真实 OpenClaw 或 ComfyUI。
## Phase 42: Task Orchestration & Background Execution

  `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, `TaskRetryPolicy`, `/api/v1/task-runs` API, Conversation Runtime, `POST /api/v1/conversations/{thread_id}/run`  `execution_mode=immediate|background|scheduled`, `scheduled_at`  `task_run_id`  polling  task timeline, Playbook / Conversation  queued / running / waiting_approval / retrying / completed / failed / cancelled / expired  retry, cancel, approval resume  Output Library artifacts  `task_run_id`

  in-process queue foundation  Celery, RabbitMQ, Kubernetes scheduler  HA distributed queue  TikTok / YouTube / X  OpenClaw, ComfyUI.

Phase 42 verifier markers: not Celery, not Kubernetes, Task Orchestration & Background Execution, `task_runs`, `task_run_events`, `TaskOrchestratorService`, `BackgroundTaskExecutor`, `TaskRetryPolicy`, `execution_mode`.
## Phase 43: Task Scheduler Persistence & Worker Recovery

 Task Scheduler Persistence, `task_scheduler_state`, `task_runs`, Task Lease  `TaskRecoveryService`, Scheduler Health API, manual recovery API, Failed Diagnostics  scheduler health

Task Lease, running task run  `lease_owner`, `lease_token`, `lease_expires_at`, `heartbeat_at`, expired lease, stale heartbeat  scan, manual recover

Recovery rules, running + expired lease, stale heartbeat -> retrying  retry budget, failed, pending scheduled due -> queued, retrying delay elapsed -> queued, waiting_approval  completed/cancelled/expired

Admin Dashboard  Scheduler Health, lease status, recoverable badge, diagnostics panel, scheduled due indicator, manual recover, Worker Console, Worker Console Desktop  Task recovery

  in-process scheduler foundation  Celery  Kubernetes  production HA distributed queue?

Phase 43 boundary marker: not Celery, not Kubernetes, not production HA.

<!-- PHASE44_STATUS:START -->
## Phase 44 - Output Artifact Pipeline & Export System



  Artifact lineage, `artifact_relationships`, `ArtifactExportService`, `ArtifactPackagingService`, `ArtifactRetentionService`, export/package APIs, Artifact Explorer UI, lineage graph  relationship graph  retention preview, bundle metadata  `storage/output_artifacts`, `storage/output_packages`, `storage/output_exports`.

  DAM  production object storage platform  S3 / MinIO / CDN
<!-- PHASE44_STATUS:END -->

<!-- PHASE44_SYNC:START -->
## Phase 44: Output Artifact Pipeline & Export System

Phase 44, Phase 41 Output Library, Phase 42/43 task runtime  Output Artifact Pipeline  Artifact lineage, relationship graph retention policy preview  Artifact Explorer



- `output_artifacts`  `parent_artifact_id`, `root_artifact_id`, `source_task_run_id`, `source_playbook_run_id`, `source_conversation_id`, `source_runtime_session_id`, `artifact_role`, `artifact_stage`, `generated_by`, `exportable`, `retention_policy`, `expires_at`.
- `artifact_relationships`  relationship graph  `derived_from`, `packaged_into`, `summarized_from`, `exported_from`, `replay_of`.
- `ArtifactExportService`  `export_markdown`, `export_html`, `export_json`, `export_bundle_zip`, `export_report_package`  browser runtime, playbook.
- `ArtifactPackagingService`  `package_playbook_run`, `package_task_run`, `package_browser_runtime_session`, `package_conversation`  package artifact, `bundle.zip` metadata.
- `ArtifactRetentionService`  retention policy, expiration scan, cleanup preview, soft archive  preview
- API  `GET /api/v1/output-artifacts/{artifact_id}/lineage`, `GET /api/v1/output-artifacts/{artifact_id}/relationships`, `POST /api/v1/output-artifacts/{artifact_id}/export`, `POST /api/v1/output-artifacts/{artifact_id}/package`, `POST /api/v1/output-artifacts/cleanup/preview`.
- Storage roots  `storage/output_artifacts`, `storage/output_packages`, `storage/output_exports`.
- Admin Dashboard  Artifact Explorer, lineage graph panel, export actions, package actions, retention badge, archived indicator, bundle metadata preview.
- Worker Console / Desktop  export, package, lineage summary, retention status



-   DAM
-   production object storage platform?
-   S3 / MinIO / CDN?
- Export  Browser Runtime, Playbook, Conversation, OpenClaw, Task action.
-  TikTok / YouTube / X automation  OpenClaw, ComfyUI.
<!-- PHASE44_SYNC:END -->

<!-- PHASE45_SYNC:START -->
## Phase 45: Workflow State & Agent Memory Foundation

Status: completed.

Phase 45 adds recoverable Workflow State and Agent Memory Snapshots across Conversation, Playbook, Task, and Artifact runtime. It is a foundation for long multi-step automation, not a full workflow builder and not ComfyUI.

Completed scope:

- `workflow_runs` stores workflow status, source links, `conversation_thread_id`, `playbook_run_id`, `task_run_id`, `current_step`, variables, context, checkpoints, pause/resume/failure timestamps, and metadata.
- `workflow_steps` stores ordered step execution with `step_index`, `step_name`, `step_type`, status, input/output payloads, error, duration, and metadata.
- `workflow_checkpoints` stores immutable checkpoint records with auto/manual/approval/failure/resume checkpoint types plus state, variables, and context snapshots.
- `agent_memory_snapshots` stores durable memory snapshots for `conversation_summary`, `task_context`, `tool_result`, `decision`, `approval_context`, and `artifact_summary`.
- `WorkflowStateService` supports create workflow, list/get workflow, variables/context update, start/complete/fail step, pause workflow, resume workflow, complete workflow, fail workflow, create/restore checkpoint, create memory snapshot, and list memory snapshots.
- Conversation events now include `workflow_run_created`, `workflow_step_started`, `workflow_step_completed`, `workflow_checkpoint_created`, `workflow_paused`, `workflow_resumed`, and `memory_snapshot_created`.
- Playbook and Task execution now optionally link to `workflow_run_id`; each playbook step can create a `workflow_step`; waiting approval moves workflow status to `waiting_approval`; completion/failure creates final/failure checkpoints.
- Output Artifact lineage now supports `workflow_run_id`, `workflow_step_id`, `checkpoint_id`, and `memory_snapshot_id` so artifacts can be traced back to workflow state. Workflow lineage is available in artifact detail and workflow panels.
- Admin Dashboard adds Workflow Runs with step timeline, variables viewer, context viewer, checkpoints list, Agent Memory Snapshots, and Pause / Resume controls.
- Worker Console and Worker Console Desktop show simplified Workflow State, current step, checkpoint count, memory summary, and linked workflow ids.

API coverage:

- `GET /api/v1/workflow-runs`
- `GET /api/v1/workflow-runs/{workflow_run_id}`
- `GET /api/v1/workflow-runs/{workflow_run_id}/steps`
- `GET /api/v1/workflow-runs/{workflow_run_id}/checkpoints`
- `POST /api/v1/workflow-runs/{workflow_run_id}/pause`
- `POST /api/v1/workflow-runs/{workflow_run_id}/resume`
- `POST /api/v1/workflow-runs/{workflow_run_id}/checkpoints`
- `GET /api/v1/workflow-runs/{workflow_run_id}/memory-snapshots`
- `POST /api/v1/workflow-runs/{workflow_run_id}/memory-snapshots`
- `GET /api/v1/agent-memory-snapshots`

Boundaries: this is not a full workflow builder, not ComfyUI, not WebSocket/SSE streaming, not real OpenClaw, not real social-platform publishing, and not TikTok / YouTube / X automation. It does not add automatic login, CAPTCHA automation, proxy pools, or fingerprint bypass.
<!-- PHASE45_SYNC:END -->

<!-- PHASE46_SYNC:START -->
## Phase 46: Workflow Graph Runtime & Conditional Execution

Status: completed.

Phase 46 adds a graph-capable workflow runtime on top of the Phase 45 Workflow State foundation. It introduces `workflow_graphs`, `workflow_graph_nodes`, `workflow_graph_edges`, and `workflow_replays`, plus `WorkflowExecutionPlanner` for graph validation, dependency resolution, conditional routing, retry/fallback planning, and replay metadata.

Completed:

- Workflow Graph Runtime stores graph definitions, nodes, edges, entry node, version, retry policy, timeout metadata, and execution mode.
- Conditional Execution uses `SafeConditionEvaluator` for `workflow.variables`, `workflow.status`, `step.output`, `artifact.metadata`, and `approval.status` conditions. Supported operators are `==`, `!=`, `and`, `or`, `in`, and `exists`.
- Workflow runs now track `workflow_graph_id`, `graph_execution`, `current_node_key`, `planned_next_nodes`, `skipped_nodes`, `retry_state`, and `fallback_state`.
- Workflow steps now track `node_key`, `parent_node_key`, and `dependency_state`.
- Replay Foundation creates `workflow_replays` metadata from checkpoints; it does not re-execute actions.
- Output Artifact graph lineage adds `producing_node_key`, `replay_source`, and `graph_lineage`; Agent Memory Snapshots can store `node_key`.
- Admin Dashboard adds Workflow Graphs with node list, edge list, planner result, conditional routing result, Retry/Fallback Path, and replay panel.
- Worker Console and Desktop show simplified graph execution state.

Boundaries: not a visual DAG builder, not a drag/drop workflow editor, not distributed orchestration engine, not ComfyUI, not WebSocket/SSE streaming, not real platform publishing, and not TikTok / YouTube / X automation.
<!-- PHASE46_SYNC:END -->

<!-- PHASE47_SYNC:START -->
## Phase 47: Workflow Template Registry & Versioning

Status: completed.

Phase 47 在 Phase 46 Workflow Graph Runtime 之上新增 Workflow Template Registry & Versioning。新增 `workflow_templates`、`workflow_template_versions`、`workflow_template_runs`，并通过 `WorkflowTemplateRegistryService` 管理模板注册、版本创建、启用版本、导入导出、模板运行和内置模板种子数据。`WorkflowTemplateCompatibilityService` 负责 required node types、input_schema、output_schema、graph validation、risk_level、runtime capabilities、warnings、errors、missing_capabilities 检查。

内置模板包括 `browser_screenshot_report_graph`、`content_generation_graph`、`rag_answer_graph`、`approval_then_browser_graph`、`openclaw_mock_inspect_graph`、`task_retry_demo_graph`。

状态与版本字段包括 `template_key`、`current_version`、`latest_version`、`validation_status`、`compatibility`。Conversation / Task / Output Artifact / Agent Memory 可记录 `workflow_template_id`、`workflow_template_version_id`、`workflow_template_run_id`。

前端新增 Template Library：Admin Dashboard 支持 template detail、Version list、Validation result、Compatibility result、Import / Export JSON、Run template、Template runs；Worker Console 和 Worker Console Desktop 提供简化 Template Library、select template、run template、template run status。

边界：当前不是可视化 DAG builder，不是 drag/drop workflow editor，不接 ComfyUI，不做 WebSocket/SSE streaming，不做 TikTok / YouTube / X 自动化，不做真实平台发布，不做自动登录、验证码、代理池、指纹绕过或真实 OpenClaw。
<!-- PHASE47_SYNC:END -->

<!-- PHASE48_SYNC:START -->
## Phase 48: Workflow Template Marketplace & Governance Foundation

Status: completed.

Phase 48, Phase 47 Workflow Template Registry & Versioning  Marketplace foundation  public marketplace  SaaS marketplace  DAG editor  ComfyUI.

Completed scope:

-  `workflow_template_reviews`  review queue, `review_status`, `risk_assessment`, `compatibility_report`, approve / reject / request changes.
-  `workflow_template_promotions`  activate, rollback, deprecate, archive, `promotion_type`  reason.
-  `workflow_template_audit_logs`  audit trail, actor, previous_state, new_state, metadata.
-  `workflow_template_compatibility_matrix`  runtime capability  `browser_runtime`, `approval_gate`, `task_scheduler`, `artifact_pipeline`, `workflow_graph_runtime`, `openclaw_mock`, `rag_pipeline`
-  `WorkflowTemplateGovernanceService`  `submit_for_review`, `approve_review`, `reject_review`, `request_changes`, `activate_template_version`, `rollback_template_version`, `deprecate_template`, `archive_template`, `list_review_queue`, `list_governance_events`.
- Template lifecycle, draft -> review -> approved -> active -> deprecated -> archived, review  activate, active version  deprecated  archived  rollback
- Marketplace foundation, `workflow_templates`  `featured`, `verified`, `recommended`, `usage_count`, `success_rate`, `average_runtime_ms`, `average_step_count`  governance badges, risk badge, verified badge, featured templates, recommended templates.
- Output Artifact lineage  `source_template_review_id`, `governance_state`, Workflow Runs  template governance state, compatibility snapshot.
- Admin Dashboard  Template Governance  Review Queue, Approval / Reject / Request Changes, Template Lifecycle View, Audit Log View, Marketplace View, Compatibility Matrix View, Rollback UI.
- Worker Console, Worker Console Desktop, Template Library  governance status, template verification status, compatibility summary.

API coverage:

- `GET /api/v1/workflow-template-reviews`
- `POST /api/v1/workflow-template-reviews`
- `POST /api/v1/workflow-template-reviews/{review_id}/approve`
- `POST /api/v1/workflow-template-reviews/{review_id}/reject`
- `POST /api/v1/workflow-template-reviews/{review_id}/request-changes`
- `POST /api/v1/workflow-templates/{template_id}/rollback/{version_id}`
- `POST /api/v1/workflow-templates/{template_id}/deprecate`
- `POST /api/v1/workflow-templates/{template_id}/archive`
- `GET /api/v1/workflow-template-audit-logs`
- `GET /api/v1/workflow-template-marketplace`
- `GET /api/v1/workflow-template-compatibility-matrix`

Boundaries: Phase 48 is not public marketplace, not a visual DAG builder, not a distributed orchestration platform, not ComfyUI, not TikTok / YouTube / X automation, not real platform publishing, not automatic login, not CAPTCHA automation, not proxy pool, and not fingerprint bypass.
<!-- PHASE48_SYNC:END -->

## Phase 49：Workflow Run Observability & Replay Center

已完成 Workflow Run Observability & Replay Center foundation：新增 `workflow_execution_traces`、`workflow_runtime_diagnostics`、`workflow_replay_sessions`，并接入 `WorkflowExecutionTraceService` 与 `WorkflowDiagnosticsService`。系统现在可以记录 node_started / node_completed / node_failed / planner_decision / retry_triggered / fallback_triggered / approval_wait / approval_resume / replay_started / replay_completed，形成 Execution Trace、Runtime Summary、Failure Hotspots、Replay Center 与 metadata_only / dry_run replay session。

新增 API：`GET /api/v1/workflow-runs/{workflow_run_id}/traces`、`GET /api/v1/workflow-runs/{workflow_run_id}/diagnostics`、`GET /api/v1/workflow-runs/{workflow_run_id}/analytics`、`POST /api/v1/workflow-runs/{workflow_run_id}/replay-sessions`、`GET /api/v1/workflow-runs/{workflow_run_id}/runtime-summary`、`GET /api/v1/workflow-replay-sessions`、`GET /api/v1/workflow-replay-sessions/{replay_session_id}`。

前端更新 Admin Dashboard 的 Replay Center / Workflow Observability 页面，展示 Execution Trace Timeline、Node Inspection Panel、Retry/Fallback Visualization、Diagnostics Panel、Runtime Summary、Replay Session View、Failure Hotspots 与 Approval Wait Visualization。Worker Console / Desktop 显示简化 trace timeline、replay session status、diagnostics summary、retry/fallback counters。

边界：当前不是 distributed tracing platform，不是 OpenTelemetry stack，不是 WebSocket/SSE realtime，不是 deterministic replay engine，不是 visual DAG editor，不接 ComfyUI，不做真实社媒发布，不做 Kubernetes orchestration。

Keywords: not distributed tracing platform; not deterministic replay engine; not ComfyUI.

## Phase 50: Desktop Console Runtime UX & Client Packaging Readiness

Phase 50  Desktop Console Runtime UX & Client Packaging Readiness, Tauri icon resource  `worker_console_desktop/src-tauri/icons/icon.ico`  `bundle.icon`  `["icons/icon.ico"]`.

Start Runtime diagnostics  `starting`, `started`, `failed`, `unavailable`, `port_conflict`, `missing_config`, `server_environment_warning`, Desktop Console  local worker diagnostics  `/local/status`, `/local/health`, runtime port, `server_url`, `worker_base_url`, last attempted action, last error detail, last successful sync.

 /  Worker Runtime  worker  worker  E2E   Desktop Console?

  packaging readiness, not final installer, no code signing, no auto updater, no MSI/EXE release packaging  not ComfyUI.

Keywords: Desktop Console Runtime UX & Client Packaging Readiness; Tauri icon resource; icons/icon.ico; bundle.icon; Start Runtime diagnostics; missing_config; port_conflict; server_environment_warning; local worker diagnostics; customer machine; not final installer; no code signing; no auto updater.
<!-- PHASE51_SYNC:START -->
## Phase 51: Release Packaging & Deployment Bundle Foundation

Status: completed.

Phase 51 adds the Release Packaging & Deployment Bundle Foundation. It introduces a `release/` directory with `release/manifest.json`, `release/version.json`, `release/env/aiops.release.env.template`, server deployment bundle scripts, frontend production build bundle scripts, desktop release readiness scripts, Windows / Mac startup scripts, and `release/scripts/validate_release_packaging.py`.

Packaging architecture:

- Server deployment bundle: `release/scripts/build_server_bundle.ps1` and `release/scripts/build_server_bundle.sh` collect API server, worker, worker_client, Alembic, Docker, docs runtime metadata, and env template sources under ignored `release/build/server`.
- Frontend production build bundle: `release/scripts/build_frontend_bundles.ps1` and `release/scripts/build_frontend_bundles.sh` run production builds for Admin Dashboard, Worker Console, and Worker Console Desktop frontend assets, then copy `dist` output under ignored `release/build/frontends`.
- Desktop release readiness: `release/scripts/check_desktop_release_readiness.ps1` and `.sh` verify Tauri config, `icons/icon.ico`, package metadata, and Cargo/toolchain presence without producing a signed installer.
- Version metadata: `release/version.json` records Phase 51 package metadata and component readiness.
- Release manifest: `release/manifest.json` is the packaging SSOT for components, outputs, startup scripts, validation script, and forbidden runtime artifacts.
- Validation: `release/scripts/validate_release_packaging.py` checks required files, manifest JSON, version JSON, desktop icon config, boundaries, and forbidden artifact declarations.

Boundaries: Phase 51 is not a formal production release, no code signing, no auto updater, no MSI/EXE formal installer, no DMG/notarization, no Kubernetes/Helm packaging, no ComfyUI, and no real social platform publishing.

 Phase 51  release readiness  code signing, auto updater, MSI/EXE, DMG/notarization, Kubernetes/Helm.

Keywords: Phase 51; Release Packaging & Deployment Bundle Foundation; release/manifest.json; release/version.json; server deployment bundle; frontend production build bundle; desktop release readiness; aiops.release.env.template; validate_release_packaging.py; Windows / Mac startup scripts; not a formal production release; no code signing; no auto updater; no MSI/EXE; no DMG/notarization; no Kubernetes/Helm.
<!-- PHASE51_SYNC:END -->
<!-- PHASE52_SYNC:START -->
## Phase 52: Deployment Profiles & Environment Bootstrap

Status: completed.

Phase 52 adds Deployment Profiles & Environment Bootstrap on top of Phase 51 release packaging. It introduces `deployment/` with profile-based configuration for `local-dev`, `server-docker`, `client-worker`, `desktop-client`, `staging`, and `production-like`. Each profile contains `profile.json`, `env.template`, `ports.json`, `services.json`, `healthchecks.json`, and `README.md`.

Completed scope:

- `deployment/scripts/generate_env.py` generates `.env.generated` or a specified output from a profile `env.template`, supports override JSON, validates required keys, and refuses to overwrite existing env files without `--force`.
- `deployment/scripts/check_dependencies.py` checks Python, Docker, Docker Compose, Node/npm, Git, Playwright/client worker advisories, Rust/cargo, MSVC/link.exe on Windows, Tauri icon readiness, and WebView2 advisory by profile.
- `deployment/scripts/check_ports.py` checks API 8000, Admin Dashboard 5180, Worker Console 5173, Desktop Console 5174, Worker Runtime 9100, PostgreSQL 5432, Redis 6379, and Qdrant 6333 from each profile `ports.json`; it reports process hints and never kills processes.
- `deployment/scripts/verify_environment.py` verifies `server-docker`, `client-worker`, and `desktop-client` health: docker compose ps, API health, browser-worker health, workflow routes smoke, task-runs smoke, output-artifacts smoke, local worker status/health, Tauri config/icon, and frontend build presence where applicable.
- Added Windows / Mac startup scripts under `deployment/windows/` and `deployment/mac/` for server Docker, Admin Dashboard, Worker Console, Desktop Console, client worker, and profile verification.
- Release integration updates `release/manifest.json`, `release/version.json`, `release/README.md`, and `release/scripts/validate_release_packaging.py` to include deployment profiles, bootstrap scripts, dependency checks, port checks, and profile verification.
- Admin Dashboard, Worker Console, and Worker Console Desktop Settings / Help now show recommended profile, AI Server URL, Workspace ID, User ID, Local Worker API, server/client/desktop role differences, and profile bootstrap docs link.

Boundaries: Phase 52 is not Kubernetes/Helm/Terraform, not Ansible, not production HA, not code signing, not an auto updater, not a formal installer, not ComfyUI, and not real social platform publishing.

Keywords: Phase 52; Deployment Profiles & Environment Bootstrap; local-dev; server-docker; client-worker; desktop-client; staging; production-like; generate_env.py; check_dependencies.py; check_ports.py; verify_environment.py; env generation; dependency checks; port checks; health verification; profile bootstrap docs; Kubernetes/Helm/Terraform.
<!-- PHASE52_SYNC:END -->

## Docs Stabilization Sprint

This document is now indexed by `docs/PHASE_INDEX.md`, `docs/CURRENT_NEXT_PHASE.md`, `docs/SYSTEM_BOUNDARIES.md`, `docs/DOC_RENDER_QA.md`, and `docs/ARCHITECTURE_TIMELINE.md`.

The canonical project recovery state is: `main` is the Phase 55 stable baseline after PR #17 and post-merge stabilization, PR #3-#14 are marked merged after PR #17 because their changes are contained in `main`, PR #1 and PR #15 are closed as superseded, and Phase 56 remains reverted and inactive. Current non-goals remain: no ComfyUI integration, no real social media publishing, no captcha bypass, no proxy pool, no Kubernetes/Helm/Terraform, no HA orchestration, and no production installer/signing.
## 当前更新（2026-05-20）

PR #57 是 Phase 61Q ComfyUI handoff 草稿，PR #58 是 Phase 61R ComfyUI preflight 草稿，PR #59 是 Phase 61S ComfyUI adapter config 草稿。当前开发分支是 `codex/phase-61t-commercial-comfyui-job-requests`，范围是 Phase 61T 商业运营 ComfyUI 作业请求：`commercial_operation_comfyui_job_requests`、`/api/v1/commercial-operations/{operation_id}/comfyui-job-requests`、Admin Dashboard ComfyUI job request 操作面板、从 checked preflight 生成可审查的未来队列 payload、安全检查、输出预期、生命周期决策和恢复指引。该阶段仍然只保存 metadata-only 记录，不会请求 ComfyUI、不会上传文件、不会提交队列、不会生成媒体、不会发布、不会控制真实账号、不会接入平台分析、不会宣称 ROI 归因，也不会绕过审批。
