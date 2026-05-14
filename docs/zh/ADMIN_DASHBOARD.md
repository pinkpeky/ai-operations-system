# Admin Dashboard Foundation

Phase 36 已完成：`admin_dashboard` 是服务器端 Admin Dashboard Foundation，用于在浏览器中查看 AI Server、Browser Worker、Browser Runtime、Timeline、Snapshots、Replay metadata、Tasks、Conversation、OpenClaw mock、Audit Logs、RAG / Documents 等核心运行状态。

## 当前定位

- 已完成：read-only monitoring foundation。
- 已完成：独立 Vite + React + TypeScript + Tailwind 前端项目。
- 已完成：通过 `X-Workspace-Id` 和 `X-User-Id` header 访问现有 AI Server API。
- 已完成：Settings 页面把 `aiServerUrl`、`workspaceId`、`userId` 保存到 localStorage。
- 实验性：Browser Runtime 页面可以创建 metadata-only replay，用于调试，不重新执行浏览器动作。
- 规划中：生产级运营后台、登录 UI、权限 UI、发布业务流、复杂编辑。

当前明确没有：no login UI、no permission UI、no publishing business flow、no real social platform control、no production-grade operations backend。

## 目录

```text
admin_dashboard/
├── package.json
├── .env.example
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── src/main.tsx
├── src/styles.css
└── src/api/client.ts
```

## Runtime 配置

```env
VITE_AI_SERVER_API=http://localhost:8000
VITE_WORKSPACE_ID=demo-workspace
VITE_USER_ID=demo-user
```

默认访问：

```text
http://localhost:8000
```

开发启动：

```powershell
cd admin_dashboard
npm install
npm run dev
```

静态构建：

```powershell
cd admin_dashboard
npm run build
```

## 页面列表

| Page | 状态 | 说明 |
| --- | --- | --- |
| Overview | 已完成 | API health、Worker online/offline、Browser runtime session count、Task summary、Conversation count、OpenClaw mock status、Recent errors |
| Workers | 已完成 | browser worker inventory、available workers、health summary；只读，不做 rotate secret / revoke |
| Browser Runtime | 已完成 | sessions、events timeline、snapshots、metadata-only replay |
| Conversations | 已完成 | threads、messages、events；标记为 foundation |
| Tasks | 已完成 | task list、events、logs、payload summary；只读，不做 retry/cancel |
| OpenClaw | 已完成 | health、capabilities、mock status；未接真实 OpenClaw |
| Audit Logs | 已完成 | browser security audit logs，支持 event_type / success / target_type 基础过滤 |
| RAG / Documents | 已完成 | embedding health、documents、collections、simple hybrid search form |
| Settings | 已完成 | AI Server URL、Workspace ID、User ID、Refresh interval |

## API Client

`admin_dashboard/src/api/client.ts` 提供：

- `workersApi`
- `browserRuntimeApi`
- `conversationsApi`
- `tasksApi`
- `openclawApi`
- `auditApi`
- `ragApi`

所有请求默认包含：

```http
X-Workspace-Id: demo-workspace
X-User-Id: demo-user
```

## Auto Refresh

- Overview：10 秒刷新。
- Workers：10 秒刷新。
- Browser Runtime：10 秒刷新。
- Logs / Events / Snapshots：手动刷新或选择详情时刷新。
- API error 不会让整个页面崩溃，页面会显示 unavailable 或错误信息。

## 边界

Admin Dashboard Foundation 不实现：

- no login UI
- no permission UI
- no publishing business flow
- no real social platform control
- no production-grade operations backend
- no TikTok / YouTube / X automation
- no auto login
- no cookie injection
- no proxy pool
- no fingerprint bypass
- no captcha automation

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
## Phase 38：Conversation Tool Bridge 前端集成

Admin Dashboard Conversation 页面已显示 route selected、selected tool、tool status、result summary、event timeline 和 full metadata panel。事件包括 `route_selected`、`tool_execution_started`、`tool_execution_completed`、`agent_execution_started`、`planning_execution_started`、`bridge_fallback`、`bridge_error`。当前仍是 polling，不是 WebSocket，不是 SSE，不是完整 ChatGPT UI，也不是 autonomous agent。

## Phase 39：Conversation Approval Panel

Admin Dashboard Conversations 页面已支持 Approval Flow Foundation：

- pending approvals panel
- proposed action preview
- proposed payload JSON
- risk badge
- approve / reject / cancel buttons
- execute approved action button
- approval events timeline

相关 API：`GET /api/v1/conversations/{thread_id}/approvals`、`POST /api/v1/conversation-approvals/{approval_id}/approve`、`/reject`、`/cancel`、`/execute`。当前是审核门禁基础，不是完整权限系统，not a full permission system；不做真实平台发布、真实 OpenClaw、登录、验证码、代理、指纹绕过或社媒自动化。
## Phase 40：Playbooks 页面与 Conversation Playbook UI

Admin Dashboard 新增 `Playbooks` 页面，并在 `Conversations` 页面增加：

- Playbook selector
- Playbook list / description
- Run playbook button
- Playbook Runs
- Step Timeline
- Approval-aware execution controls

## Phase 41：Output Library

Admin Dashboard 新增 Output Library 页面：
- artifact list
- artifact detail
- artifact type badge
- source type
- related thread
- related Playbook Run
- preview content
- Export markdown / json / txt
- filter by `artifact_type` / `source_type`

Conversation 页面同步显示 generated artifacts，并且 assistant message 支持 Save as Artifact。Playbook Run 完成后自动生成的 artifacts 会出现在 Output Library。

当前边界：Output Library 不是完整素材管理系统（not a full DAM），不接 S3 / MinIO，不做真实平台发布资产管理。

可查看内置模板：`browser_search_summary`、`browser_screenshot_report`、`rag_answer`、`content_generation`、`trend_research_draft`、`openclaw_mock_device_check`。

当前只提供基础运行和监控入口，不提供复杂可视化 workflow editor，不做真实社媒发布，不绕过 Phase 39 approval gate。
