import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot, Root } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  Bot,
  Brain,
  ClipboardList,
  Crosshair,
  Database,
  FileText,
  Gauge,
  GitBranch,
  HardDrive,
  History,
  KeyRound,
  LayoutDashboard,
  Megaphone,
  MessageSquareText,
  MonitorCheck,
  Package,
  PlayCircle,
  RefreshCcw,
  Search,
  Send,
  Server,
  Settings,
  ShieldCheck,
  Sparkles,
  Target,
  TerminalSquare,
  Users,
} from "lucide-react";
import {
  AdminSettings,
  auditApi,
  browserRuntimeApi,
  commercialOperationsApi,
  healthApi,
  JsonRecord,
  openclawApi,
  ragApi,
  readAdminSettings,
  safeRequest,
  tasksApi,
  toItems,
  workersApi,
  writeAdminSettings,
} from "./api/client";
import {
  conversationClient,
  ConversationApproval,
  ConversationEvent,
  ConversationMessage,
  ConversationPlaybook,
  ConversationPlaybookRun,
  ConversationThread,
} from "./api/conversationClient";
import { outputArtifactClient, OutputArtifact } from "./api/outputArtifactClient";
import { taskRunClient, TaskRun, TaskRunDiagnostics, TaskRunEvent, TaskSchedulerHealth } from "./api/taskRunClient";
import {
  workflowClient,
  AgentMemorySnapshot,
  WorkflowCheckpoint,
  WorkflowExecutionTrace,
  WorkflowGraph,
  WorkflowPlannerResult,
  WorkflowReplay,
  WorkflowReplaySession,
  WorkflowRuntimeDiagnostic,
  WorkflowRun,
  WorkflowStep,
} from "./api/workflowClient";
import {
  workflowTemplateClient,
  WorkflowTemplateAuditLog,
  WorkflowTemplateCompatibilityMatrixRow,
  WorkflowTemplate,
  WorkflowTemplateCompatibility,
  WorkflowTemplateMarketplaceItem,
  WorkflowTemplateReview,
  WorkflowTemplateRun,
} from "./api/workflowTemplateClient";
import "./styles.css";

type PageKey =
  | "overview"
  | "run-cockpit"
  | "commercial-operations"
  | "workers"
  | "browser-runtime"
  | "conversations"
  | "playbooks"
  | "output-library"
  | "tasks"
  | "workflows"
  | "workflow-observability"
  | "workflow-graphs"
  | "workflow-templates"
  | "template-governance"
  | "openclaw"
  | "audit-logs"
  | "rag-documents"
  | "settings";

interface PageDefinition {
  key: PageKey;
  label: string;
  icon: React.ReactNode;
}

interface DeepLinkTarget {
  threadId?: string;
  taskRunId?: string;
  artifactId?: string;
  workflowRunId?: string;
}

type UiLanguage = "zh-CN" | "en-US";
type OverviewPersona = "workstation" | "server";

type UiTextKey =
  | "brandSubtitle"
  | "languageLabel"
  | "foundationMode"
  | "operatorMode"
  | "readOnlyMode"
  | "boundaryTitle"
  | "boundaryBody"
  | "activeTasks"
  | "needsAttention"
  | "threads"
  | "selected"
  | "pendingApprovals"
  | "selectedThread"
  | "artifacts"
  | "linkedToSelection"
  | "playbookRuns"
  | "onSelectedThread"
  | "scheduler"
  | "active"
  | "searchHits"
  | "workflow"
  | "noWorkflowContext"
  | "actionStatus"
  | "taskView"
  | "searchQuery"
  | "filteredThreads"
  | "filteredTasks"
  | "autoRefresh"
  | "refreshState"
  | "interval"
  | "nextRefresh"
  | "selectedTask"
  | "linkedWorkflow"
  | "workflowSource"
  | "workflowFocus"
  | "recentRuns"
  | "recentRunsDescription"
  | "searchRunContext"
  | "clearSearch"
  | "activeTasksOption"
  | "needsAttentionOption"
  | "allTasksOption"
  | "conversationThreads"
  | "lastUpdated"
  | "workflowFocusSlice"
  | "workflowObsConsoleTitle"
  | "workflowObsConsoleDescription"
  | "workflowObsOperatorSummary"
  | "workflowObsSelectStep"
  | "workflowObsSummaryStep"
  | "workflowObsDiagnosticsStep"
  | "workflowObsReplayStep"
  | "workflowObsPanelTitle"
  | "workflowObsPanelDescription"
  | "workflowObsNoRuns"
  | "workflowObsReplayContext"
  | "workflowObsDetailTitle"
  | "workflowObsCreateReplayAction"
  | "workflowObsBoundaryNote"
  | "workflowObsRuntimeSummaryTitle"
  | "workflowObsAnalyticsTitle"
  | "workflowObsFallbacksMetric"
  | "workflowObsApprovalsMetric"
  | "workflowObsReplaysMetric"
  | "workflowObsTraceTimelineTitle"
  | "workflowObsNodeInspectionTitle"
  | "workflowObsDiagnosticsTitle"
  | "workflowObsReplaySessionsTitle"
  | "workflowObsSelectedRunMetric"
  | "workflowObsTraceMetric"
  | "workflowObsDiagnosticsMetric"
  | "workflowObsReplayMetric"
  | "workflowObsCurrentNode"
  | "workflowObsFailures"
  | "workflowObsProblems"
  | "workflowObsMetadataOnly"
  | "workflowObsTraceView"
  | "workflowObsTraceViewAll"
  | "workflowObsTraceViewAttention"
  | "workflowObsTraceViewApproval"
  | "workflowObsTraceViewReplay"
  | "workflowObsRunIdColumn"
  | "workflowObsSourceColumn"
  | "workflowObsStatusColumn"
  | "workflowObsNextColumn"
  | "workflowObsUpdatedColumn"
  | "overviewModeLabel"
  | "workstationMode"
  | "serverMode"
  | "overviewWorkstationTitle"
  | "overviewServerTitle"
  | "overviewWorkstationDescription"
  | "overviewServerDescription"
  | "primaryActions"
  | "apiHealth"
  | "workersMetric"
  | "online"
  | "offline"
  | "browserSessions"
  | "runtimeSessions"
  | "conversationsMetric"
  | "foundationThreads"
  | "taskRunsMetric"
  | "queued"
  | "running"
  | "failed"
  | "retrying"
  | "schedulerMetric"
  | "activeCount"
  | "recoveredCount"
  | "openclawMetric"
  | "mockAdapterOnly"
  | "operatorOpenCockpit"
  | "operatorOpenCockpitDetail"
  | "operatorConversations"
  | "operatorConversationsDetail"
  | "operatorOutputLibrary"
  | "operatorOutputLibraryDetail"
  | "operatorPlaybooks"
  | "operatorPlaybooksDetail"
  | "maintainerWorkers"
  | "maintainerWorkersDetail"
  | "maintainerBrowserRuntime"
  | "maintainerBrowserRuntimeDetail"
  | "maintainerTasks"
  | "maintainerTasksDetail"
  | "maintainerSettings"
  | "maintainerSettingsDetail"
  | "openPage"
  | "recentSystemSnapshot"
  | "recentSystemSnapshotDescription"
  | "conversationConsoleTitle"
  | "conversationConsoleDescription"
  | "conversationOperatorSummary"
  | "autoSafeModeSummary"
  | "reviewFirstModeSummary"
  | "backgroundModeSummary"
  | "conversationConnection"
  | "workspaceLabel"
  | "userLabel"
  | "selectedConversation"
  | "createConversationTitle"
  | "createThreadAction"
  | "noConversationThreads"
  | "conversationDetailTitle"
  | "conversationDetailDescription"
  | "runStatusLabel"
  | "routeSelectedLabel"
  | "selectedToolLabel"
  | "latestAssistantLabel"
  | "messageInputPlaceholder"
  | "sendMessageAction"
  | "runAutoSafeAction"
  | "runReviewFirstAction"
  | "queueBackgroundAction"
  | "refreshMessagesEventsAction"
  | "pollEventsAction"
  | "playbookSelectorTitle"
  | "playbookSelectorDescription"
  | "playbookListLabel"
  | "selectedPlaybookLabel"
  | "descriptionLabel"
  | "runPlaybookAction"
  | "runConversationWithPlaybookAction"
  | "playbookRunsTitle"
  | "pendingApprovalsTitle"
  | "pendingApprovalsDescription"
  | "noPendingApprovals"
  | "messagesTitle"
  | "noMessages"
  | "generatedArtifactsTitle"
  | "noGeneratedArtifacts"
  | "eventsTitle"
  | "latestEventPayloadTitle"
  | "resultMetadataTitle"
  | "ragConsoleTitle"
  | "ragConsoleDescription"
  | "ragOperatorSummary"
  | "ragValidationLoopTitle"
  | "ragValidationUploadStep"
  | "ragValidationInspectStep"
  | "ragValidationSearchStep"
  | "ragValidationDebugStep"
  | "ragValidationCleanupStep"
  | "ragEmbeddingStep"
  | "ragCollectionStep"
  | "ragDocumentsStep"
  | "ragSearchStep"
  | "ragEmbeddingMetric"
  | "ragCollectionsMetric"
  | "ragDocumentsMetric"
  | "ragChunksMetric"
  | "ragProblemDocumentsMetric"
  | "ragPanelTitle"
  | "ragPanelDescription"
  | "ragConnection"
  | "ragProviderLabel"
  | "ragModelLabel"
  | "ragReachableLabel"
  | "ragDimensionLabel"
  | "ragSelectedCollection"
  | "ragCollectionStatus"
  | "ragCollectionPoints"
  | "ragCollectionVectors"
  | "ragDocumentListTitle"
  | "ragNoDocuments"
  | "ragSearchTitle"
  | "ragSearchDescription"
  | "ragCollectionPlaceholder"
  | "ragSearchPlaceholder"
  | "ragSearchAction"
  | "ragSearchResultsTitle"
  | "ragNoSearchResults"
  | "ragRawHealthTitle"
  | "ragRawCollectionsTitle"
  | "ragDocumentIdColumn"
  | "ragSourceIdColumn"
  | "ragSourceNameColumn"
  | "ragStatusColumn"
  | "ragIngestStatusColumn"
  | "ragChunkCountColumn"
  | "ragCollectionColumn"
  | "ragUpdatedAtColumn"
  | "ragChunkIdColumn"
  | "ragSimilarityColumn"
  | "ragRerankColumn"
  | "ragTextColumn"
  | "ragMetadataColumn"
  | "ragUploadTitle"
  | "ragUploadDescription"
  | "ragFileLabel"
  | "ragDuplicateStrategy"
  | "ragDuplicateSkip"
  | "ragDuplicateForce"
  | "ragChunkSize"
  | "ragChunkOverlap"
  | "ragUploadAction"
  | "ragTextIngestTitle"
  | "ragTextIngestDescription"
  | "ragSourceId"
  | "ragSourceName"
  | "ragSourceType"
  | "ragMetadataJson"
  | "ragKnowledgeText"
  | "ragIngestTextAction"
  | "ragReingestTextAction"
  | "ragActionResultTitle"
  | "ragDocumentDetailTitle"
  | "ragDocumentDetailDescription"
  | "ragSelectDocumentHint"
  | "ragChunksTitle"
  | "ragNoChunks"
  | "ragDeleteDangerTitle"
  | "ragDeleteConfirmLabel"
  | "ragDeleteConfirmPlaceholder"
  | "ragDeleteSourceAction"
  | "ragDebugTitle"
  | "ragDebugDescription"
  | "ragDebugAction"
  | "ragDebugResultTitle"
  | "ragNoDebugResult";

interface AsyncState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  updatedAt: string | null;
}

const pages: PageDefinition[] = [
  { key: "overview", label: "Overview", icon: <LayoutDashboard size={18} /> },
  { key: "run-cockpit", label: "Run Cockpit", icon: <Crosshair size={18} /> },
  { key: "commercial-operations", label: "Commercial Ops", icon: <Target size={18} /> },
  { key: "workers", label: "Workers", icon: <Server size={18} /> },
  { key: "browser-runtime", label: "Browser Runtime", icon: <MonitorCheck size={18} /> },
  { key: "conversations", label: "Conversations", icon: <MessageSquareText size={18} /> },
  { key: "playbooks", label: "Playbooks", icon: <History size={18} /> },
  { key: "output-library", label: "Output Library", icon: <FileText size={18} /> },
  { key: "tasks", label: "Tasks", icon: <ClipboardList size={18} /> },
  { key: "workflows", label: "Workflows", icon: <GitBranch size={18} /> },
  { key: "workflow-observability", label: "Replay Center", icon: <Activity size={18} /> },
  { key: "workflow-graphs", label: "Workflow Graphs", icon: <GitBranch size={18} /> },
  { key: "workflow-templates", label: "Workflow Templates", icon: <GitBranch size={18} /> },
  { key: "template-governance", label: "Template Governance", icon: <ShieldCheck size={18} /> },
  { key: "openclaw", label: "OpenClaw", icon: <Bot size={18} /> },
  { key: "audit-logs", label: "Audit Logs", icon: <ShieldCheck size={18} /> },
  { key: "rag-documents", label: "RAG / Documents", icon: <Database size={18} /> },
  { key: "settings", label: "Settings", icon: <Settings size={18} /> },
];

const pageKeys = new Set<PageKey>(pages.map((page) => page.key));
const deepLinkParamKeys = ["thread_id", "task_run_id", "artifact_id", "workflow_run_id"];
const languageStorageKey = "aiops.admin.language";
const pageLabels: Record<UiLanguage, Record<PageKey, string>> = {
  "zh-CN": {
    overview: "总览",
    "run-cockpit": "运行驾驶舱",
    "commercial-operations": "商业运营",
    workers: "Worker 管理",
    "browser-runtime": "浏览器运行时",
    conversations: "对话",
    playbooks: "剧本",
    "output-library": "产物库",
    tasks: "任务",
    workflows: "工作流",
    "workflow-observability": "回放中心",
    "workflow-graphs": "工作流图",
    "workflow-templates": "工作流模板",
    "template-governance": "模板治理",
    openclaw: "OpenClaw",
    "audit-logs": "审计日志",
    "rag-documents": "RAG / 文档",
    settings: "设置",
  },
  "en-US": {
    overview: "Overview",
    "run-cockpit": "Run Cockpit",
    "commercial-operations": "Commercial Ops",
    workers: "Workers",
    "browser-runtime": "Browser Runtime",
    conversations: "Conversations",
    playbooks: "Playbooks",
    "output-library": "Output Library",
    tasks: "Tasks",
    workflows: "Workflows",
    "workflow-observability": "Replay Center",
    "workflow-graphs": "Workflow Graphs",
    "workflow-templates": "Workflow Templates",
    "template-governance": "Template Governance",
    openclaw: "OpenClaw",
    "audit-logs": "Audit Logs",
    "rag-documents": "RAG / Documents",
    settings: "Settings",
  },
};
const uiText: Record<UiLanguage, Record<UiTextKey, string>> = {
  "zh-CN": {
    brandSubtitle: "运维控制台",
    languageLabel: "语言",
    foundationMode: "基础模式",
    operatorMode: "运行处理",
    readOnlyMode: "只读查看",
    boundaryTitle: "Phase 61W",
    boundaryBody: "商业运营 ComfyUI 连接探测：从已批准或已模拟的执行预案创建受控健康检查和只读队列快照记录；当前仍不请求 ComfyUI、不读取队列、不上传文件、不提交任务、不生成媒体、不发布、不控制账号。",
    activeTasks: "运行中任务",
    needsAttention: "需要处理",
    threads: "对话",
    selected: "已选",
    pendingApprovals: "待审批",
    selectedThread: "当前对话",
    artifacts: "产物",
    linkedToSelection: "关联当前选择",
    playbookRuns: "剧本运行",
    onSelectedThread: "当前对话关联",
    scheduler: "调度器",
    active: "活跃",
    searchHits: "搜索命中",
    workflow: "工作流",
    noWorkflowContext: "无工作流上下文",
    actionStatus: "操作状态",
    taskView: "任务视图",
    searchQuery: "搜索词",
    filteredThreads: "筛选对话",
    filteredTasks: "筛选任务",
    autoRefresh: "自动刷新",
    refreshState: "刷新状态",
    interval: "间隔",
    nextRefresh: "下次刷新",
    selectedTask: "已选任务",
    linkedWorkflow: "关联工作流",
    workflowSource: "工作流来源",
    workflowFocus: "工作流状态",
    recentRuns: "近期运行",
    recentRunsDescription: "面向操作员的统一入口：查看对话、后台任务和需要处理的问题。",
    searchRunContext: "搜索运行上下文",
    clearSearch: "清除搜索",
    activeTasksOption: "运行中任务",
    needsAttentionOption: "需要处理",
    allTasksOption: "全部任务",
    conversationThreads: "对话列表",
    lastUpdated: "最后更新",
    workflowFocusSlice: "工作流来源与状态聚焦",
    workflowObsConsoleTitle: "工作流观测台",
    workflowObsConsoleDescription: "快速查看运行状态、执行轨迹、诊断、等待审批和回放记录。",
    workflowObsOperatorSummary: "先选中一条 workflow_run，再看摘要指标；异常、fallback、审批等待和 replay 都会在这里集中显示。",
    workflowObsSelectStep: "选择运行：定位 workflow_run",
    workflowObsSummaryStep: "看摘要：状态、节点、轨迹数量",
    workflowObsDiagnosticsStep: "查异常：失败、诊断、fallback",
    workflowObsReplayStep: "回放：创建 metadata-only 记录",
    workflowObsPanelTitle: "工作流观测",
    workflowObsPanelDescription: "执行轨迹、节点检查、重试/fallback、诊断、运行摘要和回放中心。不是 OpenTelemetry，也不是确定性重放引擎。",
    workflowObsNoRuns: "暂无可用于回放中心的工作流运行。",
    workflowObsReplayContext: "回放上下文：来自 Run Cockpit 跳转",
    workflowObsDetailTitle: "回放中心",
    workflowObsCreateReplayAction: "创建回放记录",
    workflowObsBoundaryNote: "回放记录是 metadata_only 或 dry_run，不会重新执行浏览器、OpenClaw 动作，也不会绕过审批。",
    workflowObsRuntimeSummaryTitle: "运行摘要",
    workflowObsAnalyticsTitle: "分析指标",
    workflowObsFallbacksMetric: "Fallback",
    workflowObsApprovalsMetric: "审批等待",
    workflowObsReplaysMetric: "回放",
    workflowObsTraceTimelineTitle: "执行轨迹",
    workflowObsNodeInspectionTitle: "节点检查",
    workflowObsDiagnosticsTitle: "诊断",
    workflowObsReplaySessionsTitle: "回放记录",
    workflowObsSelectedRunMetric: "当前运行",
    workflowObsTraceMetric: "轨迹",
    workflowObsDiagnosticsMetric: "诊断",
    workflowObsReplayMetric: "回放记录",
    workflowObsCurrentNode: "当前节点",
    workflowObsFailures: "失败",
    workflowObsProblems: "问题",
    workflowObsMetadataOnly: "metadata-only",
    workflowObsTraceView: "轨迹视图",
    workflowObsTraceViewAll: "全部轨迹",
    workflowObsTraceViewAttention: "只看需关注",
    workflowObsTraceViewApproval: "审批等待",
    workflowObsTraceViewReplay: "回放事件",
    workflowObsRunIdColumn: "运行 ID",
    workflowObsSourceColumn: "来源",
    workflowObsStatusColumn: "状态",
    workflowObsNextColumn: "下一节点",
    workflowObsUpdatedColumn: "更新时间",
    overviewModeLabel: "首页视角",
    workstationMode: "工作站人员",
    serverMode: "服务器维护",
    overviewWorkstationTitle: "工作站运行入口",
    overviewServerTitle: "服务器维护入口",
    overviewWorkstationDescription: "先看运行驾驶舱，再进入对话、剧本和产物。",
    overviewServerDescription: "先看 Worker、浏览器运行时、任务队列和连接配置。",
    primaryActions: "常用入口",
    apiHealth: "API 健康",
    workersMetric: "Worker",
    online: "在线",
    offline: "离线",
    browserSessions: "浏览器会话",
    runtimeSessions: "运行时会话",
    conversationsMetric: "对话",
    foundationThreads: "基础线程",
    taskRunsMetric: "任务运行",
    queued: "排队",
    running: "运行中",
    failed: "失败",
    retrying: "重试中",
    schedulerMetric: "调度器",
    activeCount: "活跃",
    recoveredCount: "已恢复",
    openclawMetric: "OpenClaw",
    mockAdapterOnly: "当前为 mock 适配",
    operatorOpenCockpit: "查看运行驾驶舱",
    operatorOpenCockpitDetail: "集中查看运行、审批、任务和工作流来源。",
    operatorConversations: "继续对话",
    operatorConversationsDetail: "查看对话消息、事件和待审批内容。",
    operatorOutputLibrary: "查看产物库",
    operatorOutputLibraryDetail: "检查运行产物并导出结果。",
    operatorPlaybooks: "查看剧本",
    operatorPlaybooksDetail: "检查剧本运行和线程上下文。",
    maintainerWorkers: "检查 Worker",
    maintainerWorkersDetail: "确认工作站在线、心跳和容量。",
    maintainerBrowserRuntime: "检查浏览器运行时",
    maintainerBrowserRuntimeDetail: "查看远程浏览器会话和快照状态。",
    maintainerTasks: "检查任务队列",
    maintainerTasksDetail: "查看失败、重试、恢复和调度状态。",
    maintainerSettings: "检查连接配置",
    maintainerSettingsDetail: "核对服务器地址、工作区和刷新间隔。",
    openPage: "打开",
    recentSystemSnapshot: "系统快照",
    recentSystemSnapshotDescription: "局部接口失败会直接显示，首页仍可继续使用。",
    conversationConsoleTitle: "对话运行台",
    conversationConsoleDescription: "创建对话、发送消息、触发安全运行，并查看审批、事件和产物。",
    conversationOperatorSummary: "先建立或选择对话，再发送消息，最后按风险选择自动运行、先审后跑或后台队列。",
    autoSafeModeSummary: "auto_safe：仅自动执行低风险动作。",
    reviewFirstModeSummary: "review_first：中高风险动作先进入人工审批。",
    backgroundModeSummary: "background：把运行交给后台任务队列。",
    conversationConnection: "AI 服务",
    workspaceLabel: "工作区",
    userLabel: "用户",
    selectedConversation: "当前对话",
    createConversationTitle: "对话标题",
    createThreadAction: "创建对话",
    noConversationThreads: "暂无对话线程。",
    conversationDetailTitle: "消息 / 事件",
    conversationDetailDescription: "基础界面：事件时间线通过轮询刷新；not WebSocket, not SSE, and not a full ChatGPT UI。",
    runStatusLabel: "运行状态",
    routeSelectedLabel: "路由",
    selectedToolLabel: "工具",
    latestAssistantLabel: "最新回复",
    messageInputPlaceholder: "输入用户消息，然后选择运行方式。",
    sendMessageAction: "发送消息",
    runAutoSafeAction: "自动安全运行",
    runReviewFirstAction: "先审后跑",
    queueBackgroundAction: "后台队列",
    refreshMessagesEventsAction: "刷新消息/事件",
    pollEventsAction: "每 5 秒轮询事件",
    playbookSelectorTitle: "剧本选择",
    playbookSelectorDescription: "剧本用于标准化常见流程；仍会遵守审批门禁，不是完整工作流构建器。",
    playbookListLabel: "剧本数量",
    selectedPlaybookLabel: "已选剧本",
    descriptionLabel: "说明",
    runPlaybookAction: "运行剧本",
    runConversationWithPlaybookAction: "按剧本运行对话",
    playbookRunsTitle: "剧本运行",
    pendingApprovalsTitle: "待审批",
    pendingApprovalsDescription: "中高风险动作会停在这里，人工确认后才会执行。",
    noPendingApprovals: "暂无待审批。可以用先审后跑模式触发需要审批的请求。",
    messagesTitle: "消息",
    noMessages: "暂无消息。",
    generatedArtifactsTitle: "生成产物",
    noGeneratedArtifacts: "暂无生成产物。剧本完成后会显示在这里。",
    eventsTitle: "事件",
    latestEventPayloadTitle: "最新事件数据",
    resultMetadataTitle: "运行元数据",
    ragConsoleTitle: "知识库操作台",
    ragConsoleDescription: "查看 embedding 健康、集合状态、文档索引和混合检索结果。",
    ragOperatorSummary: "维护人员先确认向量服务健康，再看集合容量和失败文档；工作站人员直接用集合与问题做检索验证。",
    ragValidationLoopTitle: "操作闭环",
    ragValidationUploadStep: "上传或写入",
    ragValidationInspectStep: "查看文档索引",
    ragValidationSearchStep: "检索验证",
    ragValidationDebugStep: "调试分数",
    ragValidationCleanupStep: "重写或删除确认",
    ragEmbeddingStep: "健康：Embedding Provider 可用性",
    ragCollectionStep: "集合：Qdrant collection 与向量数量",
    ragDocumentsStep: "文档：索引状态、chunk 数和错误",
    ragSearchStep: "检索：hybrid search 验证知识命中",
    ragEmbeddingMetric: "Embedding",
    ragCollectionsMetric: "集合",
    ragDocumentsMetric: "文档",
    ragChunksMetric: "Chunks",
    ragProblemDocumentsMetric: "异常文档",
    ragPanelTitle: "RAG / 文档",
    ragPanelDescription: "知识库基础入口；不是完整文档管理控制台。",
    ragConnection: "AI 服务",
    ragProviderLabel: "Provider",
    ragModelLabel: "模型",
    ragReachableLabel: "可用",
    ragDimensionLabel: "维度",
    ragSelectedCollection: "当前集合",
    ragCollectionStatus: "集合状态",
    ragCollectionPoints: "Points",
    ragCollectionVectors: "Vectors",
    ragDocumentListTitle: "文档索引",
    ragNoDocuments: "暂无文档。",
    ragSearchTitle: "混合检索",
    ragSearchDescription: "使用当前工作区、集合和问题验证知识库命中。",
    ragCollectionPlaceholder: "collection_name",
    ragSearchPlaceholder: "输入检索问题",
    ragSearchAction: "检索",
    ragSearchResultsTitle: "检索结果",
    ragNoSearchResults: "还没有检索结果。",
    ragRawHealthTitle: "Embedding 原始状态",
    ragRawCollectionsTitle: "Collection 原始状态",
    ragDocumentIdColumn: "文档 ID",
    ragSourceIdColumn: "来源 ID",
    ragSourceNameColumn: "来源名称",
    ragStatusColumn: "状态",
    ragIngestStatusColumn: "写入状态",
    ragChunkCountColumn: "Chunk 数",
    ragCollectionColumn: "集合",
    ragUpdatedAtColumn: "更新时间",
    ragChunkIdColumn: "Chunk ID",
    ragSimilarityColumn: "相似度",
    ragRerankColumn: "精排",
    ragTextColumn: "文本",
    ragMetadataColumn: "元数据",
    ragUploadTitle: "上传知识文件",
    ragUploadDescription: "支持 PDF、DOCX、TXT、MD、CSV。上传后会写入当前工作区和集合。",
    ragFileLabel: "知识文件",
    ragDuplicateStrategy: "重复策略",
    ragDuplicateSkip: "跳过重复文件",
    ragDuplicateForce: "强制重新写入",
    ragChunkSize: "切分长度",
    ragChunkOverlap: "重叠长度",
    ragUploadAction: "上传并写入",
    ragTextIngestTitle: "写入文本知识",
    ragTextIngestDescription: "适合录入短规则、FAQ、操作说明；重写需要填写 source_id。",
    ragSourceId: "来源 ID",
    ragSourceName: "来源名称",
    ragSourceType: "来源类型",
    ragMetadataJson: "元数据 JSON",
    ragKnowledgeText: "知识文本",
    ragIngestTextAction: "写入文本",
    ragReingestTextAction: "重写同一来源",
    ragActionResultTitle: "操作结果",
    ragDocumentDetailTitle: "文档详情",
    ragDocumentDetailDescription: "选择文档后查看版本、错误、metadata 和 chunk 内容。",
    ragSelectDocumentHint: "从文档索引表选择一行查看详情。",
    ragChunksTitle: "Chunks",
    ragNoChunks: "暂无 chunk。",
    ragDeleteDangerTitle: "危险操作",
    ragDeleteConfirmLabel: "输入 source_id 确认删除",
    ragDeleteConfirmPlaceholder: "输入当前文档的 source_id",
    ragDeleteSourceAction: "删除该来源",
    ragDebugTitle: "检索调试",
    ragDebugDescription: "查看 query embedding 维度、命中 chunk 和分数，定位为什么搜不到。",
    ragDebugAction: "调试检索",
    ragDebugResultTitle: "Debug 结果",
    ragNoDebugResult: "还没有 debug 结果。",
  },
  "en-US": {
    brandSubtitle: "Operations Console",
    languageLabel: "Language",
    foundationMode: "foundation",
    operatorMode: "operational",
    readOnlyMode: "read-only",
    boundaryTitle: "Phase 61W",
    boundaryBody: "Commercial operation ComfyUI adapter dispatch records: create reviewable, recoverable metadata-only dispatch handoffs from recorded connection probes while keeping ComfyUI calls, queue reads, uploads, job submission, media generation, publishing, and account control disabled.",
    activeTasks: "Active tasks",
    needsAttention: "needs attention",
    threads: "Threads",
    selected: "selected",
    pendingApprovals: "Pending approvals",
    selectedThread: "selected thread",
    artifacts: "Artifacts",
    linkedToSelection: "linked to selection",
    playbookRuns: "Playbook runs",
    onSelectedThread: "on selected thread",
    scheduler: "Scheduler",
    active: "active",
    searchHits: "Search hits",
    workflow: "Workflow",
    noWorkflowContext: "no workflow context",
    actionStatus: "Action status",
    taskView: "Task view",
    searchQuery: "Search query",
    filteredThreads: "Filtered threads",
    filteredTasks: "Filtered tasks",
    autoRefresh: "Auto refresh",
    refreshState: "Refresh state",
    interval: "Interval",
    nextRefresh: "Next refresh",
    selectedTask: "Selected task",
    linkedWorkflow: "Linked workflow",
    workflowSource: "Workflow source",
    workflowFocus: "Workflow focus",
    recentRuns: "Recent Runs",
    recentRunsDescription: "A single operator surface for conversation threads, background task runs, and problems needing attention.",
    searchRunContext: "Search run context",
    clearSearch: "Clear search",
    activeTasksOption: "active tasks",
    needsAttentionOption: "needs attention",
    allTasksOption: "all tasks",
    conversationThreads: "Conversation threads",
    lastUpdated: "Last updated",
    workflowFocusSlice: "Workflow focus slice",
    workflowObsConsoleTitle: "Workflow observability console",
    workflowObsConsoleDescription: "Scan run status, execution traces, diagnostics, approval waits, and replay records quickly.",
    workflowObsOperatorSummary: "Select one workflow_run, then read the summary cards; failures, fallbacks, approval waits, and replay records stay visible here.",
    workflowObsSelectStep: "Select: locate a workflow_run",
    workflowObsSummaryStep: "Summarize: status, node, trace count",
    workflowObsDiagnosticsStep: "Diagnose: failures, diagnostics, fallback",
    workflowObsReplayStep: "Replay: create metadata-only record",
    workflowObsPanelTitle: "Workflow Observability",
    workflowObsPanelDescription: "Execution trace timeline, node inspection, retry/fallback visualization, diagnostics, runtime summary, and Replay Center. This is not OpenTelemetry and not deterministic replay.",
    workflowObsNoRuns: "No workflow runs available for Replay Center.",
    workflowObsReplayContext: "Replay context: Run Cockpit handoff",
    workflowObsDetailTitle: "Replay Center",
    workflowObsCreateReplayAction: "Create replay session",
    workflowObsBoundaryNote: "Replay sessions are metadata_only or dry_run. They do not re-execute browser/OpenClaw actions or bypass approvals.",
    workflowObsRuntimeSummaryTitle: "Runtime Summary",
    workflowObsAnalyticsTitle: "Analytics",
    workflowObsFallbacksMetric: "Fallbacks",
    workflowObsApprovalsMetric: "Approvals",
    workflowObsReplaysMetric: "Replays",
    workflowObsTraceTimelineTitle: "Execution Trace Timeline",
    workflowObsNodeInspectionTitle: "Node Inspection",
    workflowObsDiagnosticsTitle: "Diagnostics",
    workflowObsReplaySessionsTitle: "Replay Sessions",
    workflowObsSelectedRunMetric: "Selected run",
    workflowObsTraceMetric: "Traces",
    workflowObsDiagnosticsMetric: "Diagnostics",
    workflowObsReplayMetric: "Replay sessions",
    workflowObsCurrentNode: "Current node",
    workflowObsFailures: "Failures",
    workflowObsProblems: "Problems",
    workflowObsMetadataOnly: "metadata-only",
    workflowObsTraceView: "Trace view",
    workflowObsTraceViewAll: "All traces",
    workflowObsTraceViewAttention: "Needs attention",
    workflowObsTraceViewApproval: "Approval waits",
    workflowObsTraceViewReplay: "Replay events",
    workflowObsRunIdColumn: "workflow_run_id",
    workflowObsSourceColumn: "source",
    workflowObsStatusColumn: "status",
    workflowObsNextColumn: "next",
    workflowObsUpdatedColumn: "updated_at",
    overviewModeLabel: "Overview mode",
    workstationMode: "Workstation operator",
    serverMode: "Server maintainer",
    overviewWorkstationTitle: "Workstation Run Entry",
    overviewServerTitle: "Server Maintenance Entry",
    overviewWorkstationDescription: "Start with Run Cockpit, then continue into conversations, playbooks, and output artifacts.",
    overviewServerDescription: "Start with workers, browser runtime, task queues, and connection settings.",
    primaryActions: "Primary actions",
    apiHealth: "API health",
    workersMetric: "Workers",
    online: "online",
    offline: "offline",
    browserSessions: "Browser sessions",
    runtimeSessions: "runtime sessions",
    conversationsMetric: "Conversations",
    foundationThreads: "foundation threads",
    taskRunsMetric: "Task runs",
    queued: "queued",
    running: "running",
    failed: "failed",
    retrying: "retrying",
    schedulerMetric: "Scheduler",
    activeCount: "active",
    recoveredCount: "recovered",
    openclawMetric: "OpenClaw",
    mockAdapterOnly: "mock adapter only",
    operatorOpenCockpit: "Open Run Cockpit",
    operatorOpenCockpitDetail: "Scan runs, approvals, tasks, and workflow provenance in one place.",
    operatorConversations: "Continue conversations",
    operatorConversationsDetail: "Review messages, events, and pending approvals.",
    operatorOutputLibrary: "Open Output Library",
    operatorOutputLibraryDetail: "Inspect run artifacts and export results.",
    operatorPlaybooks: "Open Playbooks",
    operatorPlaybooksDetail: "Review playbook runs and thread context.",
    maintainerWorkers: "Check Workers",
    maintainerWorkersDetail: "Confirm workstation online state, heartbeat, and capacity.",
    maintainerBrowserRuntime: "Check Browser Runtime",
    maintainerBrowserRuntimeDetail: "Inspect remote browser sessions and snapshot state.",
    maintainerTasks: "Check Task Queue",
    maintainerTasksDetail: "Review failures, retries, recovery, and scheduler state.",
    maintainerSettings: "Check Settings",
    maintainerSettingsDetail: "Confirm server URL, workspace, and refresh interval.",
    openPage: "Open",
    recentSystemSnapshot: "System Snapshot",
    recentSystemSnapshotDescription: "Partial API failures are shown inline so the dashboard remains usable.",
    conversationConsoleTitle: "Conversation Console",
    conversationConsoleDescription: "Create threads, send messages, trigger safe runs, and inspect approvals, events, and artifacts.",
    conversationOperatorSummary: "Create or select a thread, send a message, then choose auto-safe, review-first, or background execution based on risk.",
    autoSafeModeSummary: "auto_safe: only low-risk actions run automatically.",
    reviewFirstModeSummary: "review_first: medium/high-risk actions wait for human approval.",
    backgroundModeSummary: "background: queue execution into the task runner.",
    conversationConnection: "AI Server",
    workspaceLabel: "workspace",
    userLabel: "user",
    selectedConversation: "selected",
    createConversationTitle: "Conversation title",
    createThreadAction: "Create thread",
    noConversationThreads: "No conversation threads.",
    conversationDetailTitle: "Messages / Events",
    conversationDetailDescription: "Foundation UI only. Event timeline is polling based; this is not WebSocket, not SSE, and not a full ChatGPT UI.",
    runStatusLabel: "Run status",
    routeSelectedLabel: "Route selected",
    selectedToolLabel: "Selected tool",
    latestAssistantLabel: "Latest assistant",
    messageInputPlaceholder: "Send a user message, then run the conversation turn.",
    sendMessageAction: "Send message",
    runAutoSafeAction: "Run conversation auto_safe",
    runReviewFirstAction: "Run review_first",
    queueBackgroundAction: "Queue background",
    refreshMessagesEventsAction: "Refresh messages/events",
    pollEventsAction: "Poll events every 5 seconds",
    playbookSelectorTitle: "Playbook selector",
    playbookSelectorDescription: "Conversation Playbooks standardize common flows. This is not a full workflow builder and still respects approval gates.",
    playbookListLabel: "Playbook list",
    selectedPlaybookLabel: "Selected",
    descriptionLabel: "Description",
    runPlaybookAction: "Run playbook",
    runConversationWithPlaybookAction: "Run conversation with playbook",
    playbookRunsTitle: "Playbook runs",
    pendingApprovalsTitle: "Pending Approvals Panel",
    pendingApprovalsDescription: "Medium/high risk actions stay pending until a human approves and explicitly executes them.",
    noPendingApprovals: "No pending approvals yet. Try Run review_first with a browser request.",
    messagesTitle: "Messages",
    noMessages: "No messages yet.",
    generatedArtifactsTitle: "Generated artifacts",
    noGeneratedArtifacts: "No generated artifacts yet. Completed playbook runs will appear here.",
    eventsTitle: "Events",
    latestEventPayloadTitle: "Latest Event Payload",
    resultMetadataTitle: "Result Metadata",
    ragConsoleTitle: "Knowledge Console",
    ragConsoleDescription: "Inspect embedding health, collection state, document indexing, and hybrid retrieval results.",
    ragOperatorSummary: "Maintainers confirm vector service health, collection capacity, and failed documents; workstation users validate retrieval with a collection and query.",
    ragValidationLoopTitle: "Operation loop",
    ragValidationUploadStep: "Upload or ingest",
    ragValidationInspectStep: "Inspect document index",
    ragValidationSearchStep: "Search to verify",
    ragValidationDebugStep: "Debug scores",
    ragValidationCleanupStep: "Reingest or confirm delete",
    ragEmbeddingStep: "Health: Embedding Provider availability",
    ragCollectionStep: "Collections: Qdrant collection and vector counts",
    ragDocumentsStep: "Documents: index status, chunk count, and errors",
    ragSearchStep: "Retrieval: hybrid search verifies knowledge hits",
    ragEmbeddingMetric: "Embedding",
    ragCollectionsMetric: "Collections",
    ragDocumentsMetric: "Documents",
    ragChunksMetric: "Chunks",
    ragProblemDocumentsMetric: "Problem docs",
    ragPanelTitle: "RAG / Documents",
    ragPanelDescription: "Basic knowledge-base entry point. This is not a full document management console.",
    ragConnection: "AI Server",
    ragProviderLabel: "Provider",
    ragModelLabel: "Model",
    ragReachableLabel: "Reachable",
    ragDimensionLabel: "Dimension",
    ragSelectedCollection: "Selected collection",
    ragCollectionStatus: "Collection status",
    ragCollectionPoints: "Points",
    ragCollectionVectors: "Vectors",
    ragDocumentListTitle: "Document index",
    ragNoDocuments: "No documents.",
    ragSearchTitle: "Hybrid search",
    ragSearchDescription: "Use the active workspace, collection, and query to validate knowledge retrieval.",
    ragCollectionPlaceholder: "collection_name",
    ragSearchPlaceholder: "Search query",
    ragSearchAction: "Search",
    ragSearchResultsTitle: "Search results",
    ragNoSearchResults: "No search results yet.",
    ragRawHealthTitle: "Raw embedding state",
    ragRawCollectionsTitle: "Raw collection state",
    ragDocumentIdColumn: "document_id",
    ragSourceIdColumn: "source_id",
    ragSourceNameColumn: "source_name",
    ragStatusColumn: "status",
    ragIngestStatusColumn: "ingest_status",
    ragChunkCountColumn: "chunk_count",
    ragCollectionColumn: "collection_name",
    ragUpdatedAtColumn: "updated_at",
    ragChunkIdColumn: "chunk_id",
    ragSimilarityColumn: "similarity",
    ragRerankColumn: "rerank",
    ragTextColumn: "text",
    ragMetadataColumn: "metadata",
    ragUploadTitle: "Upload knowledge file",
    ragUploadDescription: "Supports PDF, DOCX, TXT, MD, and CSV. Uploaded files are ingested into the active workspace and collection.",
    ragFileLabel: "Knowledge file",
    ragDuplicateStrategy: "Duplicate strategy",
    ragDuplicateSkip: "Skip duplicate file",
    ragDuplicateForce: "Force reingest",
    ragChunkSize: "Chunk size",
    ragChunkOverlap: "Chunk overlap",
    ragUploadAction: "Upload and ingest",
    ragTextIngestTitle: "Ingest text knowledge",
    ragTextIngestDescription: "Use this for short rules, FAQs, and operating notes. Reingest requires source_id.",
    ragSourceId: "source_id",
    ragSourceName: "source_name",
    ragSourceType: "source_type",
    ragMetadataJson: "metadata JSON",
    ragKnowledgeText: "Knowledge text",
    ragIngestTextAction: "Ingest text",
    ragReingestTextAction: "Reingest same source",
    ragActionResultTitle: "Action result",
    ragDocumentDetailTitle: "Document detail",
    ragDocumentDetailDescription: "Select a document to inspect version, errors, metadata, and chunk content.",
    ragSelectDocumentHint: "Select a row from the document index to inspect details.",
    ragChunksTitle: "Chunks",
    ragNoChunks: "No chunks.",
    ragDeleteDangerTitle: "Danger zone",
    ragDeleteConfirmLabel: "Type source_id to confirm delete",
    ragDeleteConfirmPlaceholder: "Type the selected document source_id",
    ragDeleteSourceAction: "Delete this source",
    ragDebugTitle: "Retrieval debug",
    ragDebugDescription: "Inspect query embedding dimension, matching chunks, and scores to explain retrieval misses.",
    ragDebugAction: "Debug retrieval",
    ragDebugResultTitle: "Debug result",
    ragNoDebugResult: "No debug result yet.",
  },
};

function pageFromLocation(): PageKey {
  const page = new URLSearchParams(window.location.search).get("page");
  return page && pageKeys.has(page as PageKey) ? (page as PageKey) : "overview";
}

function targetFromLocation(): DeepLinkTarget {
  const params = new URLSearchParams(window.location.search);
  return {
    threadId: params.get("thread_id") ?? undefined,
    taskRunId: params.get("task_run_id") ?? undefined,
    artifactId: params.get("artifact_id") ?? undefined,
    workflowRunId: params.get("workflow_run_id") ?? undefined,
  };
}

function updateLocation(page: PageKey, target: DeepLinkTarget = {}) {
  const params = new URLSearchParams(window.location.search);
  params.set("page", page);
  deepLinkParamKeys.forEach((key) => params.delete(key));
  if (target.threadId) params.set("thread_id", target.threadId);
  if (target.taskRunId) params.set("task_run_id", target.taskRunId);
  if (target.artifactId) params.set("artifact_id", target.artifactId);
  if (target.workflowRunId) params.set("workflow_run_id", target.workflowRunId);
  const nextUrl = `${window.location.pathname}?${params.toString()}${window.location.hash}`;
  window.history.pushState({}, "", nextUrl);
}

function readUiLanguage(): UiLanguage {
  try {
    const stored = window.localStorage.getItem(languageStorageKey);
    return stored === "en-US" ? "en-US" : "zh-CN";
  } catch {
    return "zh-CN";
  }
}

function writeUiLanguage(language: UiLanguage): void {
  try {
    window.localStorage.setItem(languageStorageKey, language);
  } catch {
    // localStorage may be unavailable in hardened embedded browsers.
  }
}

function pageLabel(page: PageKey, language: UiLanguage): string {
  return pageLabels[language][page] ?? pageLabels["en-US"][page];
}

function textFor(language: UiLanguage, key: UiTextKey): string {
  return uiText[language][key] ?? uiText["en-US"][key];
}

const taskStatuses = ["pending", "queued", "running", "waiting_approval", "retrying", "failed", "completed", "cancelled", "expired"];

function emptyState<T>(): AsyncState<T> {
  return { data: null, error: null, loading: false, updatedAt: null };
}

function nowLabel(): string {
  return new Date().toLocaleString();
}

function valueAt(record: JsonRecord | null | undefined, keys: string[], fallback = "-"): string {
  if (!record) {
    return fallback;
  }
  for (const key of keys) {
    const value = record[key];
    if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
      return String(value);
    }
  }
  return fallback;
}

function rowId(record: JsonRecord, preferredKeys: string[]): string {
  return valueAt(record, preferredKeys, JSON.stringify(record).slice(0, 48));
}

function shortJson(value: unknown, limit = 110): string {
  if (value === null || value === undefined) {
    return "-";
  }
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  const rendered = JSON.stringify(value);
  return rendered.length > limit ? `${rendered.slice(0, limit)}...` : rendered;
}

function searchText(...values: unknown[]): string {
  return values
    .map((value) => {
      if (value === null || value === undefined) {
        return "";
      }
      if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") {
        return String(value);
      }
      return JSON.stringify(value);
    })
    .join(" ")
    .toLowerCase();
}

function matchesSearch(query: string, ...values: unknown[]): boolean {
  const normalized = query.trim().toLowerCase();
  return !normalized || searchText(...values).includes(normalized);
}

function useAutoRefresh(enabled: boolean, intervalMs: number, callback: () => void): void {
  useEffect(() => {
    if (!enabled) {
      return undefined;
    }
    callback();
    const timer = window.setInterval(callback, intervalMs);
    return () => window.clearInterval(timer);
  }, [callback, enabled, intervalMs]);
}

function StatusPill({ value }: { value: React.ReactNode }) {
  const label = String(value ?? "unknown");
  const variant = /online|active|healthy|completed|success|true/i.test(label)
    ? "ok"
    : /failed|error|offline|timeout|false|revoked/i.test(label)
      ? "bad"
      : "muted";
  return <span className={`status-pill status-pill-${variant}`}>{label}</span>;
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="field">
      <span className="field-label">{label}</span>
      <span className="field-value">{value ?? "-"}</span>
    </div>
  );
}

function DataCard({
  title,
  value,
  detail,
  icon,
  warning,
}: {
  title: string;
  value: React.ReactNode;
  detail?: React.ReactNode;
  icon: React.ReactNode;
  warning?: boolean;
}) {
  return (
    <section className={`metric-card ${warning ? "metric-card-warning" : ""}`}>
      <div className="metric-icon">{icon}</div>
      <div>
        <p>{title}</p>
        <strong>{value}</strong>
        {detail ? <span>{detail}</span> : null}
      </div>
    </section>
  );
}

function Panel({
  title,
  description,
  children,
  action,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
  action?: React.ReactNode;
}) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>{title}</h2>
          {description ? <p>{description}</p> : null}
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function LoadNotice<T>({ state }: { state: AsyncState<T> }) {
  if (state.error) {
    return (
      <div className="notice notice-error">
        <AlertTriangle size={16} />
        {state.error}
      </div>
    );
  }
  if (state.loading) {
    return <div className="notice">Loading...</div>;
  }
  return null;
}

function JsonPreview({ value }: { value: unknown }) {
  return <pre className="json-preview">{shortJson(value, 1600)}</pre>;
}

function formatDateLabel(value: string | null | undefined): string {
  if (!value) {
    return "-";
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

function isActiveStatus(status: string | null | undefined): boolean {
  return /pending|queued|running|waiting_approval|retrying/i.test(status ?? "");
}

function isProblemStatus(status: string | null | undefined): boolean {
  return /failed|error|expired|cancelled/i.test(status ?? "");
}

function Table({
  rows,
  columns,
  emptyLabel,
  selectedId,
  onSelect,
}: {
  rows: JsonRecord[];
  columns: { key: string; label: string; aliases?: string[] }[];
  emptyLabel: string;
  selectedId?: string | null;
  onSelect?: (row: JsonRecord) => void;
}) {
  if (!rows.length) {
    return <div className="empty-table">{emptyLabel}</div>;
  }
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={column.key}>{column.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const id = rowId(row, ["id", "worker_id", "session_id", "thread_id", "task_id"]);
            return (
              <tr
                key={id}
                className={`${onSelect ? "selectable-row" : ""} ${selectedId === id ? "selected-row" : ""}`}
                onClick={() => onSelect?.(row)}
              >
                {columns.map((column) => {
                  const keys = [column.key, ...(column.aliases || [])];
                  const value = keys.map((key) => row[key]).find((candidate) => candidate !== undefined);
                  return <td key={`${id}-${column.key}`}>{renderCell(value)}</td>;
                })}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function renderCell(value: unknown): React.ReactNode {
  if (typeof value === "string" && /^(active|online|offline|failed|completed|pending|running|healthy|warning|error|true|false)$/i.test(value)) {
    return <StatusPill value={value} />;
  }
  if (typeof value === "boolean") {
    return <StatusPill value={value} />;
  }
  if (value && typeof value === "object") {
    return <code>{shortJson(value)}</code>;
  }
  return <span>{String(value ?? "-")}</span>;
}

function OverviewPage({
  settings,
  language,
  onNavigate,
}: {
  settings: AdminSettings;
  language: UiLanguage;
  onNavigate: (page: PageKey, target?: DeepLinkTarget) => void;
}) {
  const t = useCallback((key: UiTextKey) => textFor(language, key), [language]);
  const [state, setState] = useState<AsyncState<JsonRecord>>(emptyState());
  const [persona, setPersona] = useState<OverviewPersona>("workstation");

  const load = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    const [health, workerSummary, taskSummary, taskRuns, schedulerHealth, openclawHealth, sessions, conversations] = await Promise.all([
      safeRequest<JsonRecord>("/health", {}, settings),
      safeRequest<JsonRecord>("/browser-workers/health/summary", {}, settings),
      safeRequest<JsonRecord>("/observability/summary", {}, settings),
      safeRequest<JsonRecord>("/task-runs", {}, settings),
      safeRequest<JsonRecord>("/task-scheduler/health", {}, settings),
      safeRequest<JsonRecord>("/openclaw/health", {}, settings),
      safeRequest<JsonRecord>("/browser-runtime/sessions", {}, settings),
      safeRequest<JsonRecord>("/conversations", {}, settings),
    ]);
    const data: JsonRecord = {
      health: health.ok ? health.data : { unavailable: health.error },
      workerSummary: workerSummary.ok ? workerSummary.data : { unavailable: workerSummary.error },
      taskSummary: taskSummary.ok ? taskSummary.data : { unavailable: taskSummary.error },
      taskRuns: taskRuns.ok ? taskRuns.data : { unavailable: taskRuns.error },
      schedulerHealth: schedulerHealth.ok ? schedulerHealth.data : { unavailable: schedulerHealth.error },
      openclawHealth: openclawHealth.ok ? openclawHealth.data : { unavailable: openclawHealth.error },
      browserRuntimeSessions: sessions.ok ? sessions.data : { unavailable: sessions.error },
      conversations: conversations.ok ? conversations.data : { unavailable: conversations.error },
    };
    setState({ data, error: null, loading: false, updatedAt: nowLabel() });
  }, [settings]);

  useAutoRefresh(true, settings.refreshIntervalMs, load);

  const sessionsCount = state.data ? toItems(state.data.browserRuntimeSessions).length : "-";
  const conversationCount = state.data ? toItems(state.data.conversations).length : "-";
  const taskRuns = state.data ? toItems(state.data.taskRuns) : [];
  const taskRunCounts = taskRuns.reduce<Record<string, number>>((counts, item) => {
    const status = String(item.status ?? "unknown");
    counts[status] = (counts[status] || 0) + 1;
    return counts;
  }, {});
  const workerSummary = (state.data?.workerSummary as JsonRecord | undefined) || null;
  const schedulerHealth = (state.data?.schedulerHealth as JsonRecord | undefined) || null;
  const health = (state.data?.health as JsonRecord | undefined) || null;
  const openclaw = (state.data?.openclawHealth as JsonRecord | undefined) || null;
  const overviewActions: { page: PageKey; title: string; detail: string }[] =
    persona === "workstation"
      ? [
          { page: "commercial-operations", title: language === "zh-CN" ? "创建商业运营项目" : "Create commercial operation", detail: language === "zh-CN" ? "把运营目标转成计划、知识集合、审批和执行入口。" : "Turn a business goal into plan, knowledge, approval, and execution entry points." },
          { page: "run-cockpit", title: t("operatorOpenCockpit"), detail: t("operatorOpenCockpitDetail") },
          { page: "conversations", title: t("operatorConversations"), detail: t("operatorConversationsDetail") },
          { page: "playbooks", title: t("operatorPlaybooks"), detail: t("operatorPlaybooksDetail") },
          { page: "output-library", title: t("operatorOutputLibrary"), detail: t("operatorOutputLibraryDetail") },
        ]
      : [
          { page: "workers", title: t("maintainerWorkers"), detail: t("maintainerWorkersDetail") },
          { page: "browser-runtime", title: t("maintainerBrowserRuntime"), detail: t("maintainerBrowserRuntimeDetail") },
          { page: "tasks", title: t("maintainerTasks"), detail: t("maintainerTasksDetail") },
          { page: "settings", title: t("maintainerSettings"), detail: t("maintainerSettingsDetail") },
        ];

  return (
    <div className="page-stack">
      <section className="overview-command-center">
        <div>
          <p className="section-eyebrow">{t("overviewModeLabel")}</p>
          <h2>{persona === "workstation" ? t("overviewWorkstationTitle") : t("overviewServerTitle")}</h2>
          <p>{persona === "workstation" ? t("overviewWorkstationDescription") : t("overviewServerDescription")}</p>
        </div>
        <div className="overview-mode-switch" role="group" aria-label={t("overviewModeLabel")}>
          <button className={persona === "workstation" ? "active" : ""} onClick={() => setPersona("workstation")}>
            {t("workstationMode")}
          </button>
          <button className={persona === "server" ? "active" : ""} onClick={() => setPersona("server")}>
            {t("serverMode")}
          </button>
        </div>
      </section>
      <Panel title={t("primaryActions")}>
        <div className="overview-action-grid">
          {overviewActions.map((action) => (
            <article className="overview-action-card" key={action.page}>
              <div>
                <h3>{action.title}</h3>
                <p>{action.detail}</p>
              </div>
              <button className="ghost-button" onClick={() => onNavigate(action.page)}>
                <PlayCircle size={15} />
                {t("openPage")}
              </button>
            </article>
          ))}
        </div>
      </Panel>
      <section className="metrics-grid">
        <DataCard title={t("apiHealth")} value={valueAt(health, ["status", "reachable", "success"])} icon={<Gauge size={20} />} />
        <DataCard
          title={t("workersMetric")}
          value={`${valueAt(workerSummary, ["online_count"], "0")} ${t("online")}`}
          detail={`${valueAt(workerSummary, ["offline_count"], "0")} ${t("offline")}`}
          icon={<Server size={20} />}
        />
        <DataCard title={t("browserSessions")} value={sessionsCount} detail={t("runtimeSessions")} icon={<MonitorCheck size={20} />} />
        <DataCard title={t("conversationsMetric")} value={conversationCount} detail={t("foundationThreads")} icon={<MessageSquareText size={20} />} />
        <DataCard
          title={t("taskRunsMetric")}
          value={`${taskRunCounts.queued ?? 0} ${t("queued")} / ${taskRunCounts.running ?? 0} ${t("running")}`}
          detail={`${taskRunCounts.failed ?? 0} ${t("failed")} / ${taskRunCounts.retrying ?? 0} ${t("retrying")}`}
          icon={<ClipboardList size={20} />}
        />
        <DataCard
          title={t("schedulerMetric")}
          value={valueAt(schedulerHealth, ["status"], "unavailable")}
          detail={`${valueAt(schedulerHealth, ["active_task_count"], "0")} ${t("activeCount")} / ${valueAt(schedulerHealth, ["recovered_task_count"], "0")} ${t("recoveredCount")}`}
          icon={<Gauge size={20} />}
        />
        <DataCard
          title={t("openclawMetric")}
          value={valueAt(openclaw, ["provider"], "unavailable")}
          detail={t("mockAdapterOnly")}
          icon={<Bot size={20} />}
        />
      </section>
      <LoadNotice state={state} />
      <Panel title={t("recentSystemSnapshot")} description={t("recentSystemSnapshotDescription")}>
        <div className="json-grid">
          <JsonPreview value={state.data?.health} />
          <JsonPreview value={state.data?.taskSummary} />
          <JsonPreview value={state.data?.taskRuns} />
          <JsonPreview value={state.data?.schedulerHealth} />
          <JsonPreview value={state.data?.workerSummary} />
          <JsonPreview value={state.data?.openclawHealth} />
        </div>
        <div className="last-updated">{t("lastUpdated")}: {state.updatedAt ?? "-"}</div>
      </Panel>
    </div>
  );
}

function WorkersPage({ settings }: { settings: AdminSettings }) {
  const [workers, setWorkers] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [available, setAvailable] = useState<JsonRecord[]>([]);
  const [summary, setSummary] = useState<JsonRecord | null>(null);

  const load = useCallback(async () => {
    setWorkers((current) => ({ ...current, loading: true, error: null }));
    try {
      const [list, availableList, healthSummary] = await Promise.all([
        workersApi.list(settings),
        workersApi.available(settings),
        workersApi.healthSummary(settings),
      ]);
      setWorkers({ data: toItems(list), error: null, loading: false, updatedAt: nowLabel() });
      setAvailable(toItems(availableList));
      setSummary(healthSummary);
    } catch (error) {
      setWorkers({
        data: null,
        error: error instanceof Error ? error.message : "Worker API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings]);

  useAutoRefresh(true, settings.refreshIntervalMs, load);

  return (
    <Panel
      title="Workers"
      description="Read-only browser worker inventory. Secret rotation and revoke controls stay outside this foundation UI."
      action={<RefreshButton onClick={load} />}
    >
      <LoadNotice state={workers} />
      <div className="summary-strip">
        <span>Available workers: {available.length}</span>
        <span>Health summary: {summary ? shortJson(summary, 180) : "-"}</span>
      </div>
      <Table
        rows={workers.data || []}
        emptyLabel="No workers found for this workspace."
        columns={[
          { key: "id", label: "worker_id", aliases: ["worker_id"] },
          { key: "worker_name", label: "worker_name" },
          { key: "status", label: "status" },
          { key: "worker_type", label: "worker_type" },
          { key: "base_url", label: "base_url" },
          { key: "capabilities", label: "capabilities" },
          { key: "active_sessions", label: "active_sessions" },
          { key: "max_sessions", label: "max_sessions" },
          { key: "last_heartbeat_at", label: "last_heartbeat_at" },
          { key: "auth_status", label: "auth_status" },
        ]}
      />
      <div className="last-updated">Last updated: {workers.updatedAt ?? "-"}</div>
    </Panel>
  );
}

function RunCockpitPage({
  settings,
  onNavigate,
  language,
}: {
  settings: AdminSettings;
  onNavigate: (page: PageKey, target?: DeepLinkTarget) => void;
  language: UiLanguage;
}) {
  const t = useCallback((key: UiTextKey) => textFor(language, key), [language]);
  const [state, setState] = useState<AsyncState<{
    threads: ConversationThread[];
    taskRuns: TaskRun[];
    playbookRuns: ConversationPlaybookRun[];
    artifacts: OutputArtifact[];
    schedulerHealth: TaskSchedulerHealth | null;
  }>>(emptyState());
  const [selectedThread, setSelectedThread] = useState<ConversationThread | null>(null);
  const [selectedTask, setSelectedTask] = useState<TaskRun | null>(null);
  const [threadMessages, setThreadMessages] = useState<ConversationMessage[]>([]);
  const [threadEvents, setThreadEvents] = useState<ConversationEvent[]>([]);
  const [threadApprovals, setThreadApprovals] = useState<ConversationApproval[]>([]);
  const [threadArtifacts, setThreadArtifacts] = useState<OutputArtifact[]>([]);
  const [taskEvents, setTaskEvents] = useState<TaskRunEvent[]>([]);
  const [taskDiagnostics, setTaskDiagnostics] = useState<TaskRunDiagnostics | null>(null);
  const [taskArtifacts, setTaskArtifacts] = useState<OutputArtifact[]>([]);
  const [linkedWorkflow, setLinkedWorkflow] = useState<WorkflowRun | null>(null);
  const [linkedWorkflowSummary, setLinkedWorkflowSummary] = useState<JsonRecord | null>(null);
  const [linkedWorkflowError, setLinkedWorkflowError] = useState<string | null>(null);
  const [linkedWorkflowLoading, setLinkedWorkflowLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);
  const [actionStatus, setActionStatus] = useState("idle");
  const [actionPreview, setActionPreview] = useState<JsonRecord | null>(null);
  const [taskView, setTaskView] = useState<"all" | "active" | "attention">("active");
  const [cockpitQuery, setCockpitQuery] = useState("");
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [lastRefreshAtMs, setLastRefreshAtMs] = useState<number | null>(null);
  const [refreshClockMs, setRefreshClockMs] = useState(() => Date.now());
  const selectedThreadId = selectedThread?.id ?? null;
  const selectedTaskId = selectedTask?.id ?? null;

  const load = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const [threadResponse, taskResponse, playbookRunResponse, artifactResponse, schedulerHealth] = await Promise.all([
        conversationClient.listThreads(settings),
        taskRunClient.listTaskRuns(settings),
        conversationClient.listPlaybookRuns(settings),
        outputArtifactClient.listArtifacts(settings),
        taskRunClient.schedulerHealth(settings).catch(() => null),
      ]);
      const data = {
        threads: threadResponse.items ?? [],
        taskRuns: taskResponse.items ?? [],
        playbookRuns: playbookRunResponse.items ?? [],
        artifacts: artifactResponse.items ?? [],
        schedulerHealth,
      };
      setLastRefreshAtMs(Date.now());
      setState({ data, error: null, loading: false, updatedAt: nowLabel() });
      if (!selectedThread && data.threads.length) {
        setSelectedThread(data.threads[0]);
      }
      if (!selectedTask && data.taskRuns.length) {
        setSelectedTask(data.taskRuns[0]);
      }
    } catch (error) {
      setLastRefreshAtMs(Date.now());
      setState((current) => ({
        ...current,
        error: error instanceof Error ? error.message : "Run cockpit data unavailable",
        loading: false,
        updatedAt: nowLabel(),
      }));
    }
  }, [selectedTask, selectedThread, settings]);

  const loadThread = useCallback(
    async (thread: ConversationThread) => {
      setSelectedThread(thread);
      setDetailError(null);
      try {
        const [messageList, eventList, approvalList, artifactList] = await Promise.all([
          conversationClient.listMessages(thread.id, settings),
          conversationClient.listEvents(thread.id, settings),
          conversationClient.listApprovals(thread.id, settings),
          outputArtifactClient.listArtifacts(settings, { threadId: thread.id }),
        ]);
        setThreadMessages(messageList.items ?? []);
        setThreadEvents(eventList.items ?? []);
        setThreadApprovals(approvalList.items ?? []);
        setThreadArtifacts(artifactList.items ?? []);
      } catch (error) {
        setThreadMessages([]);
        setThreadEvents([]);
        setThreadApprovals([]);
        setThreadArtifacts([]);
        setDetailError(error instanceof Error ? error.message : "Conversation detail unavailable");
      }
    },
    [settings],
  );

  const loadTask = useCallback(
    async (task: TaskRun) => {
      setSelectedTask(task);
      setDetailError(null);
      try {
        const [eventList, diagnostics, artifactList] = await Promise.all([
          taskRunClient.listEvents(task.id, settings),
          taskRunClient.diagnostics(task.id, settings).catch(() => null),
          outputArtifactClient.listArtifacts(settings, { taskRunId: task.id }),
        ]);
        setTaskEvents(eventList.items ?? []);
        setTaskDiagnostics(diagnostics);
        setTaskArtifacts(artifactList.items ?? []);
      } catch (error) {
        setTaskEvents([]);
        setTaskDiagnostics(null);
        setTaskArtifacts([]);
        setDetailError(error instanceof Error ? error.message : "Task detail unavailable");
      }
    },
    [settings],
  );

  const mutateCockpitApproval = async (approval: ConversationApproval, action: "approve" | "reject" | "cancel" | "execute") => {
    if (!selectedThread) {
      return;
    }
    setDetailError(null);
    setActionStatus(`${action} approval`);
    try {
      if (action === "approve") {
        const updated = await conversationClient.approveApproval(approval.id, "Approved from Run Cockpit.", settings);
        setActionPreview(updated as unknown as JsonRecord);
      } else if (action === "reject") {
        const updated = await conversationClient.rejectApproval(approval.id, "Rejected from Run Cockpit.", settings);
        setActionPreview(updated as unknown as JsonRecord);
      } else if (action === "cancel") {
        const updated = await conversationClient.cancelApproval(approval.id, "Cancelled from Run Cockpit.", settings);
        setActionPreview(updated as unknown as JsonRecord);
      } else {
        const response = await conversationClient.executeApproval(approval.id, settings);
        setActionPreview(response as unknown as JsonRecord);
      }
      await loadThread(selectedThread);
      await load();
      setActionStatus(`${action} approval completed`);
    } catch (error) {
      setDetailError(error instanceof Error ? error.message : `${action} approval failed`);
      setActionStatus("approval action failed");
    }
  };

  const mutateCockpitTask = async (action: "retry" | "cancel" | "resume" | "recover") => {
    if (!selectedTask) {
      return;
    }
    setDetailError(null);
    setActionStatus(`${action} task`);
    try {
      const updated =
        action === "retry"
          ? await taskRunClient.retry(selectedTask.id, "Manual retry from Run Cockpit", settings)
          : action === "cancel"
            ? await taskRunClient.cancel(selectedTask.id, "Manual cancel from Run Cockpit", settings)
            : action === "recover"
              ? await taskRunClient.recover(selectedTask.id, "Manual recovery from Run Cockpit", settings)
              : await taskRunClient.resume(selectedTask.id, settings);
      setSelectedTask(updated);
      setActionPreview(updated as unknown as JsonRecord);
      await loadTask(updated);
      await load();
      setActionStatus(`${action} task completed`);
    } catch (error) {
      setDetailError(error instanceof Error ? error.message : `${action} task failed`);
      setActionStatus("task action failed");
    }
  };

  const exportCockpitArtifact = async (artifact: OutputArtifact, format: "markdown" | "json" | "txt" = "markdown") => {
    setDetailError(null);
    setActionStatus(`export ${format}`);
    try {
      const exported = await outputArtifactClient.exportArtifact(artifact.id, format, settings);
      setActionPreview(exported as unknown as JsonRecord);
      await load();
      setActionStatus(`artifact exported as ${format}`);
    } catch (error) {
      setDetailError(error instanceof Error ? error.message : "Artifact export failed");
      setActionStatus("artifact export failed");
    }
  };

  useEffect(() => {
    void load();
  }, [load]);

  useAutoRefresh(autoRefresh, settings.refreshIntervalMs, load);

  useEffect(() => {
    if (!autoRefresh) {
      return undefined;
    }
    setRefreshClockMs(Date.now());
    const timer = window.setInterval(() => setRefreshClockMs(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, [autoRefresh]);

  useEffect(() => {
    if (selectedThread) {
      void loadThread(selectedThread);
    }
  }, [loadThread, selectedThread]);

  useEffect(() => {
    if (selectedTask) {
      void loadTask(selectedTask);
    }
  }, [loadTask, selectedTask]);

  const data = state.data;
  const activeTasks = data?.taskRuns.filter((task) => isActiveStatus(task.status)) ?? [];
  const problemTasks = data?.taskRuns.filter((task) => isProblemStatus(task.status) || task.recoverable) ?? [];
  const visibleTasks =
    taskView === "active"
      ? activeTasks
      : taskView === "attention"
        ? problemTasks
        : data?.taskRuns ?? [];
  const filteredThreads = (data?.threads ?? []).filter((thread) =>
    matchesSearch(cockpitQuery, thread.id, thread.title, thread.status, thread.metadata, thread.created_at, thread.updated_at),
  );
  const filteredTasks = visibleTasks.filter((task) =>
    matchesSearch(
      cockpitQuery,
      task.id,
      task.task_type,
      task.source_type,
      task.source_id,
      task.status,
      task.priority,
      task.error,
      task.failure_category,
      task.failure_reason,
      task.suggested_action,
      task.last_event_summary,
      task.workflow_run_id,
      task.workflow_template_run_id,
      task.metadata,
    ),
  );
  const filteredPlaybookRuns = (data?.playbookRuns ?? []).filter((run) =>
    matchesSearch(cockpitQuery, run.id, run.playbook_id, run.thread_id, run.status, run.error, run.input_payload, run.output_payload),
  );
  const filteredArtifacts = (data?.artifacts ?? []).filter((artifact) =>
    matchesSearch(
      cockpitQuery,
      artifact.id,
      artifact.title,
      artifact.summary,
      artifact.source_type,
      artifact.artifact_type,
      artifact.artifact_stage,
      artifact.status,
      artifact.thread_id,
      artifact.task_run_id,
      artifact.workflow_run_id,
      artifact.workflow_template_run_id,
      artifact.metadata,
    ),
  );
  const pendingApprovals = threadApprovals.filter((approval) => approval.approval_status === "pending");
  const selectedThreadPlaybookRuns = data?.playbookRuns.filter((run) => run.thread_id === selectedThreadId) ?? [];
  const selectedThreadArtifacts =
    selectedThreadId && data
      ? data.artifacts.filter((artifact) => artifact.thread_id === selectedThreadId || artifact.source_conversation_id === selectedThreadId)
      : threadArtifacts;
  const selectedTaskArtifacts =
    selectedTaskId && data
      ? data.artifacts.filter((artifact) => artifact.task_run_id === selectedTaskId || artifact.source_task_run_id === selectedTaskId)
      : taskArtifacts;
  const linkedArtifacts = [...selectedThreadArtifacts, ...selectedTaskArtifacts].filter(
    (artifact, index, items) => items.findIndex((candidate) => candidate.id === artifact.id) === index,
  );
  const linkedWorkflowCandidates = [
    ...(selectedTask?.workflow_run_id
      ? [
          {
            workflowRunId: selectedTask.workflow_run_id,
            sourceLabel: "selected task",
            sourceType: "task_run",
            sourceId: selectedTask.id,
            status: selectedTask.status,
            detail: selectedTask.task_type,
          },
        ]
      : []),
    ...selectedThreadPlaybookRuns
      .map((run) => ({
        workflowRunId: valueAt(run.output_payload, ["workflow_run_id"], ""),
        sourceLabel: "thread playbook",
        sourceType: "playbook_run",
        sourceId: run.id,
        status: run.status,
        detail: run.playbook_id,
      }))
      .filter((candidate) => candidate.workflowRunId.length > 0),
    ...linkedArtifacts.flatMap((artifact) =>
      artifact.workflow_run_id
        ? [
            {
              workflowRunId: artifact.workflow_run_id,
              sourceLabel: "linked artifact",
              sourceType: "output_artifact",
              sourceId: artifact.id,
              status: artifact.status,
              detail: artifact.title,
            },
          ]
        : [],
    ),
  ].filter(
    (candidate, index, items) =>
      items.findIndex(
        (item) =>
          item.workflowRunId === candidate.workflowRunId &&
          item.sourceType === candidate.sourceType &&
          item.sourceId === candidate.sourceId,
      ) === index,
  );
  const linkedWorkflowSource = linkedWorkflowCandidates[0] ?? null;
  const linkedWorkflowRunId: string | null = linkedWorkflowSource?.workflowRunId ?? null;
  const linkedWorkflowUniqueCount = new Set(linkedWorkflowCandidates.map((candidate) => candidate.workflowRunId)).size;
  const linkedWorkflowFocusState = !linkedWorkflowRunId
    ? "no context"
    : linkedWorkflowLoading
      ? "loading"
      : linkedWorkflowError
        ? linkedWorkflow || linkedWorkflowSummary
          ? "partial"
          : "unavailable"
        : linkedWorkflow || linkedWorkflowSummary
          ? "ready"
          : "pending";
  const visibleLinkedArtifacts = linkedArtifacts.filter((artifact) =>
    matchesSearch(
      cockpitQuery,
      artifact.id,
      artifact.title,
      artifact.summary,
      artifact.source_type,
      artifact.artifact_type,
      artifact.artifact_stage,
      artifact.status,
      artifact.thread_id,
      artifact.task_run_id,
      artifact.workflow_run_id,
      artifact.workflow_template_run_id,
      artifact.metadata,
    ),
  );
  const queryActive = Boolean(cockpitQuery.trim());
  const queryMatchCount = queryActive ? filteredThreads.length + filteredTasks.length + filteredPlaybookRuns.length + filteredArtifacts.length : "-";
  const latestMessage = threadMessages[threadMessages.length - 1];
  const latestTaskEvent = taskEvents[taskEvents.length - 1];
  const refreshIntervalSeconds = Math.max(1, Math.round(settings.refreshIntervalMs / 1000));
  const nextRefreshSeconds =
    autoRefresh && lastRefreshAtMs
      ? Math.max(0, Math.ceil((lastRefreshAtMs + settings.refreshIntervalMs - refreshClockMs) / 1000))
      : null;
  const refreshState = state.loading ? "refreshing" : state.error ? "stale data" : "idle";

  useEffect(() => {
    if (!linkedWorkflowRunId) {
      setLinkedWorkflow(null);
      setLinkedWorkflowSummary(null);
      setLinkedWorkflowError(null);
      setLinkedWorkflowLoading(false);
      return;
    }
    const workflowRunId = linkedWorkflowRunId;
    let cancelled = false;
    async function loadLinkedWorkflow() {
      setLinkedWorkflowError(null);
      setLinkedWorkflowLoading(true);
      try {
        const [workflowResult, runtimeSummaryResult] = await Promise.allSettled([
          workflowClient.getRun(workflowRunId, settings),
          workflowClient.getRuntimeSummary(workflowRunId, settings),
        ]);
        if (cancelled) {
          return;
        }
        const workflow = workflowResult.status === "fulfilled" ? workflowResult.value : null;
        const runtimeSummary = runtimeSummaryResult.status === "fulfilled" ? runtimeSummaryResult.value : null;
        setLinkedWorkflow(workflow);
        setLinkedWorkflowSummary(runtimeSummary?.summary ?? null);
        if (workflowResult.status === "rejected" && runtimeSummaryResult.status === "rejected") {
          const reason = workflowResult.reason ?? runtimeSummaryResult.reason;
          setLinkedWorkflowError(reason instanceof Error ? reason.message : "Linked workflow detail unavailable");
        } else if (workflowResult.status === "rejected") {
          setLinkedWorkflowError("Workflow metadata unavailable; runtime summary loaded.");
        } else if (runtimeSummaryResult.status === "rejected") {
          setLinkedWorkflowError("Runtime summary unavailable; workflow metadata loaded.");
        } else {
          setLinkedWorkflowError(null);
        }
      } catch (error) {
        if (!cancelled) {
          setLinkedWorkflow(null);
          setLinkedWorkflowSummary(null);
          setLinkedWorkflowError(error instanceof Error ? error.message : "Linked workflow unavailable");
        }
      } finally {
        if (!cancelled) {
          setLinkedWorkflowLoading(false);
        }
      }
    }
    void loadLinkedWorkflow();
    return () => {
      cancelled = true;
    };
  }, [linkedWorkflowRunId, settings]);

  return (
    <div className="page-stack">
      <section className="metrics-grid">
        <DataCard title={t("activeTasks")} value={activeTasks.length} detail={`${problemTasks.length} ${t("needsAttention")}`} icon={<Activity size={20} />} warning={problemTasks.length > 0} />
        <DataCard title={t("threads")} value={data?.threads.length ?? "-"} detail={`${t("selected")}: ${selectedThread?.title ?? "-"}`} icon={<MessageSquareText size={20} />} />
        <DataCard title={t("pendingApprovals")} value={pendingApprovals.length} detail={t("selectedThread")} icon={<ShieldCheck size={20} />} warning={pendingApprovals.length > 0} />
        <DataCard title={t("artifacts")} value={data?.artifacts.length ?? "-"} detail={`${selectedThreadArtifacts.length + selectedTaskArtifacts.length} ${t("linkedToSelection")}`} icon={<FileText size={20} />} />
        <DataCard title={t("playbookRuns")} value={data?.playbookRuns.length ?? "-"} detail={`${selectedThreadPlaybookRuns.length} ${t("onSelectedThread")}`} icon={<History size={20} />} />
        <DataCard title={t("scheduler")} value={data?.schedulerHealth?.status ?? "unavailable"} detail={`${t("active")}: ${data?.schedulerHealth?.active_task_count ?? 0}`} icon={<Gauge size={20} />} />
        <DataCard title={t("searchHits")} value={queryMatchCount} detail={`${filteredThreads.length} ${t("threads")} / ${filteredTasks.length} ${t("filteredTasks")} / ${filteredArtifacts.length} ${t("artifacts")}`} icon={<Search size={20} />} />
        <DataCard title={t("workflow")} value={linkedWorkflow?.status ?? (linkedWorkflowRunId ? linkedWorkflowFocusState : "none")} detail={linkedWorkflowSource ? `${linkedWorkflowSource.sourceLabel}: ${linkedWorkflowSource.sourceId}` : t("noWorkflowContext")} icon={<GitBranch size={20} />} />
      </section>
      <LoadNotice state={state} />
      <div className="summary-strip cockpit-action-strip">
        <span>{t("actionStatus")}: <StatusPill value={actionStatus} /></span>
        <span>{t("taskView")}: {taskView}</span>
        <span>{t("searchQuery")}: {cockpitQuery.trim() || "-"}</span>
        <span>{t("filteredThreads")}: {filteredThreads.length}/{data?.threads.length ?? 0}</span>
        <span>{t("filteredTasks")}: {filteredTasks.length}/{visibleTasks.length}</span>
        <span>{t("autoRefresh")}: <StatusPill value={autoRefresh} /></span>
        <span>{t("refreshState")}: <StatusPill value={refreshState} /></span>
        <span>{t("interval")}: {refreshIntervalSeconds}s</span>
        <span>{t("nextRefresh")}: {nextRefreshSeconds === null ? "-" : `${nextRefreshSeconds}s`}</span>
        <span>{t("selectedThread")}: {selectedThreadId ?? "-"}</span>
        <span>{t("selectedTask")}: {selectedTaskId ?? "-"}</span>
        <span>{t("linkedWorkflow")}: {linkedWorkflowRunId ?? "-"}</span>
        <span>{t("workflowSource")}: {linkedWorkflowSource ? `${linkedWorkflowSource.sourceType}:${linkedWorkflowSource.sourceId}` : "-"}</span>
        <span>{t("workflowFocus")}: <StatusPill value={linkedWorkflowFocusState} /></span>
      </div>
      {detailError ? (
        <div className="notice notice-error">
          <AlertTriangle size={16} />
          {detailError}
        </div>
      ) : null}
      <div className="cockpit-grid">
        <Panel
          title={t("recentRuns")}
          description={t("recentRunsDescription")}
          action={
            <div className="inline-controls">
              <label className="cockpit-search-field">
                <Search size={16} />
                <input
                  value={cockpitQuery}
                  onChange={(event) => setCockpitQuery(event.target.value)}
                  aria-label={t("searchRunContext")}
                  placeholder={t("searchRunContext")}
                />
              </label>
              <button className="ghost-button" onClick={() => setCockpitQuery("")} disabled={!queryActive}>
                {t("clearSearch")}
              </button>
              <select value={taskView} onChange={(event) => setTaskView(event.target.value as "all" | "active" | "attention")} aria-label={t("taskView")}>
                <option value="active">{t("activeTasksOption")}</option>
                <option value="attention">{t("needsAttentionOption")}</option>
                <option value="all">{t("allTasksOption")}</option>
              </select>
              <label className="checkbox-row">
                <input type="checkbox" checked={autoRefresh} onChange={(event) => setAutoRefresh(event.target.checked)} />
                {t("autoRefresh")}
              </label>
              <RefreshButton onClick={load} />
            </div>
          }
        >
          <h3>{t("conversationThreads")} ({filteredThreads.length}/{data?.threads.length ?? 0})</h3>
          <Table
            rows={filteredThreads as unknown as JsonRecord[]}
            selectedId={selectedThreadId}
            onSelect={(row) => void loadThread(row as unknown as ConversationThread)}
            emptyLabel={queryActive ? "No conversation threads match the cockpit search." : "No conversation threads."}
            columns={[
              { key: "id", label: "thread_id" },
              { key: "title", label: "title" },
              { key: "status", label: "status" },
              { key: "updated_at", label: "updated_at" },
            ]}
          />
          <h3>Task runs ({filteredTasks.length}/{visibleTasks.length})</h3>
          <Table
            rows={filteredTasks as unknown as JsonRecord[]}
            selectedId={selectedTaskId}
            onSelect={(row) => void loadTask(row as unknown as TaskRun)}
            emptyLabel={queryActive ? "No task runs match the cockpit search." : "No task runs for the selected view."}
            columns={[
              { key: "id", label: "task_run_id" },
              { key: "task_type", label: "task_type" },
              { key: "source_type", label: "source" },
              { key: "status", label: "status" },
              { key: "recoverable", label: "recoverable" },
              { key: "updated_at", label: "updated_at" },
            ]}
          />
          <div className="last-updated">
            {t("lastUpdated")}: {state.updatedAt ?? "-"} | {t("autoRefresh")}: {autoRefresh ? `every ${refreshIntervalSeconds}s` : "off"} | {t("nextRefresh")}: {nextRefreshSeconds === null ? "-" : `${nextRefreshSeconds}s`}
          </div>
        </Panel>
        <aside className="detail-panel cockpit-detail-panel">
          <div className="detail-title">
            <div>
              <h2>Run Detail</h2>
              <p className="foundation-note">Correlates selected thread, task, approvals, events, and artifacts without changing execution semantics.</p>
            </div>
          </div>
          <section className="cockpit-section">
            <h3>Selected thread</h3>
            <div className="summary-strip">
              <span>title: {selectedThread?.title ?? "-"}</span>
              <span>status: <StatusPill value={selectedThread?.status ?? "none"} /></span>
              <span>updated: {formatDateLabel(selectedThread?.updated_at)}</span>
            </div>
            <div className="run-summary-grid">
              <Field label="messages" value={threadMessages.length} />
              <Field label="events" value={threadEvents.length} />
              <Field label="approvals" value={threadApprovals.length} />
              <Field label="artifacts" value={selectedThreadArtifacts.length} />
            </div>
            <div className="conversation-actions">
              <button className="ghost-button" onClick={() => onNavigate("conversations", selectedThreadId ? { threadId: selectedThreadId } : undefined)}>
                Open Conversations
              </button>
              <button className="ghost-button" onClick={() => onNavigate("playbooks", selectedThreadId ? { threadId: selectedThreadId } : undefined)}>
                Open Playbooks
              </button>
            </div>
            <h3>Latest message</h3>
            <div className="empty-chat">{latestMessage ? `${latestMessage.role}: ${latestMessage.content}` : "No messages on selected thread."}</div>
            <h3>Pending approvals</h3>
            {pendingApprovals.length ? (
              pendingApprovals.map((approval) => (
                <div className={`approval-card approval-risk-${approval.risk_level}`} key={approval.id}>
                  <div className="approval-card-header">
                    <strong>{approval.proposed_action}</strong>
                    <StatusPill value={approval.risk_level} />
                    <StatusPill value={approval.approval_status} />
                </div>
                <p>{approval.selected_tool ?? approval.route_name}</p>
                <div className="conversation-actions">
                  <button className="ghost-button" onClick={() => void mutateCockpitApproval(approval, "approve")} disabled={approval.approval_status !== "pending"}>
                    Approve
                  </button>
                  <button className="ghost-button" onClick={() => void mutateCockpitApproval(approval, "reject")} disabled={approval.approval_status !== "pending"}>
                    Reject
                  </button>
                  <button className="ghost-button" onClick={() => void mutateCockpitApproval(approval, "cancel")} disabled={!["pending", "approved"].includes(approval.approval_status)}>
                    Cancel
                  </button>
                  <button className="primary-button" onClick={() => void mutateCockpitApproval(approval, "execute")} disabled={approval.approval_status !== "approved"}>
                    Execute
                  </button>
                </div>
              </div>
            ))
          ) : (
              <div className="empty-chat">No pending approvals on selected thread.</div>
            )}
          </section>
          <section className="cockpit-section">
            <h3>Selected task</h3>
            <div className="summary-strip">
              <span>task: {selectedTask?.task_type ?? "-"}</span>
              <span>status: <StatusPill value={selectedTask?.status ?? "none"} /></span>
              <span>updated: {formatDateLabel(selectedTask?.updated_at)}</span>
            </div>
            <div className="run-summary-grid">
              <Field label="retry" value={selectedTask ? `${selectedTask.retry_count}/${selectedTask.max_retries}` : "-"} />
              <Field label="recoverable" value={<StatusPill value={selectedTask?.recoverable ?? false} />} />
              <Field label="events" value={taskEvents.length} />
              <Field label="artifacts" value={selectedTaskArtifacts.length} />
            </div>
            <div className="conversation-actions">
              <button className="ghost-button" onClick={() => onNavigate("tasks", selectedTaskId ? { taskRunId: selectedTaskId } : undefined)}>
                Open Tasks
              </button>
              <button className="ghost-button" onClick={() => void mutateCockpitTask("retry")} disabled={!selectedTask}>
                Retry
              </button>
              <button className="ghost-button" onClick={() => void mutateCockpitTask("cancel")} disabled={!selectedTask}>
                Cancel
              </button>
              <button className="ghost-button" onClick={() => void mutateCockpitTask("resume")} disabled={!selectedTask}>
                Resume
              </button>
              <button className="ghost-button" onClick={() => void mutateCockpitTask("recover")} disabled={!selectedTask || !selectedTask.recoverable}>
                Recover
              </button>
            </div>
            <h3>Latest task event</h3>
            <div className="empty-chat">{latestTaskEvent ? `${latestTaskEvent.event_type}: ${latestTaskEvent.message ?? latestTaskEvent.status ?? "-"}` : "No task events for selected task."}</div>
            <h3>Diagnostics</h3>
            <JsonPreview value={taskDiagnostics || { status: "select a task run" }} />
          </section>
          <section className="cockpit-section">
            <h3>Linked workflow</h3>
            <div className="summary-strip">
              <span>workflow_run_id: {linkedWorkflowRunId ?? "-"}</span>
              <span>focus: <StatusPill value={linkedWorkflowFocusState} /></span>
              <span>status: <StatusPill value={linkedWorkflow?.status ?? "none"} /></span>
              <span>source: {linkedWorkflowSource ? `${linkedWorkflowSource.sourceLabel} / ${linkedWorkflowSource.sourceType}` : "-"}</span>
              <span>source_id: {linkedWorkflowSource?.sourceId ?? "-"}</span>
              <span>candidates: {linkedWorkflowCandidates.length} source / {linkedWorkflowUniqueCount} run</span>
              <span>current_node: {linkedWorkflow?.current_node_key ?? "-"}</span>
            </div>
            {linkedWorkflowLoading ? (
              <div className="notice">
                <RefreshCcw size={16} />
                Loading linked workflow details.
              </div>
            ) : null}
            {linkedWorkflowError ? <div className="notice notice-error">{linkedWorkflowError}</div> : null}
            <div className="conversation-actions">
              <button className="ghost-button" onClick={() => onNavigate("workflows", linkedWorkflowRunId ? { workflowRunId: linkedWorkflowRunId } : undefined)} disabled={!linkedWorkflowRunId}>
                Open Workflows
              </button>
              <button className="ghost-button" onClick={() => onNavigate("workflow-observability", linkedWorkflowRunId ? { workflowRunId: linkedWorkflowRunId } : undefined)} disabled={!linkedWorkflowRunId}>
                Open Replay Center
              </button>
            </div>
            {linkedWorkflowCandidates.length ? (
              <div className="timeline">
                {linkedWorkflowCandidates.slice(0, 4).map((candidate) => (
                  <div className="timeline-item" key={`${candidate.sourceType}:${candidate.sourceId}:${candidate.workflowRunId}`}>
                    <span>{candidate.sourceLabel}</span>
                    <p>{candidate.workflowRunId}</p>
                    <small>{candidate.sourceType}: {candidate.sourceId} / {candidate.status} / {candidate.detail}</small>
                  </div>
                ))}
              </div>
            ) : (
              <div className="empty-chat">No workflow context found on the selected task, selected thread playbook runs, or linked artifacts.</div>
            )}
            <JsonPreview value={linkedWorkflowSummary || linkedWorkflow || { status: "No workflow linked to the selected run context." }} />
          </section>
          <section className="cockpit-section">
            <h3>Linked artifacts</h3>
            <div className="summary-strip">
              <span>visible: {visibleLinkedArtifacts.length}</span>
              <span>linked: {linkedArtifacts.length}</span>
              <span>search artifacts: {filteredArtifacts.length}/{data?.artifacts.length ?? 0}</span>
            </div>
            <div className="conversation-actions">
              <button
                className="ghost-button"
                onClick={() => onNavigate("output-library", {
                  artifactId: linkedArtifacts[0]?.id,
                  threadId: selectedThreadId ?? undefined,
                  taskRunId: selectedTaskId ?? undefined,
                })}
              >
                Open Output Library
              </button>
            </div>
            {visibleLinkedArtifacts.slice(0, 8).map((artifact) => (
              <div className="approval-card" key={`${artifact.id}-${artifact.task_run_id ?? artifact.thread_id ?? "linked"}`}>
                <div className="approval-card-header">
                  <strong>{artifact.title}</strong>
                  <StatusPill value={artifact.artifact_type} />
                  <StatusPill value={artifact.status} />
                </div>
                <p>{artifact.summary ?? artifact.file_path ?? "No summary"}</p>
                <div className="conversation-actions">
                  <button className="ghost-button" onClick={() => void exportCockpitArtifact(artifact, "markdown")} disabled={!artifact.exportable}>
                    Export markdown
                  </button>
                  <button className="ghost-button" onClick={() => void exportCockpitArtifact(artifact, "json")} disabled={!artifact.exportable}>
                    Export JSON
                  </button>
                </div>
              </div>
            ))}
            {visibleLinkedArtifacts.length === 0 ? (
              <div className="empty-chat">{queryActive ? "No linked artifacts match the cockpit search." : "No artifacts linked to the selected run context."}</div>
            ) : null}
          </section>
          <section className="cockpit-section">
            <h3>Last action result</h3>
            <JsonPreview value={actionPreview || { status: "No cockpit action has run yet." }} />
          </section>
          <section className="cockpit-section">
            <h3>Thread events</h3>
            <Timeline rows={threadEvents as unknown as JsonRecord[]} primary="event_type" secondary="message" />
          </section>
        </aside>
      </div>
    </div>
  );
}

function BrowserRuntimePage({ settings }: { settings: AdminSettings }) {
  const [sessions, setSessions] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [selectedSession, setSelectedSession] = useState<JsonRecord | null>(null);
  const [events, setEvents] = useState<JsonRecord[]>([]);
  const [snapshots, setSnapshots] = useState<JsonRecord[]>([]);
  const [replay, setReplay] = useState<JsonRecord | null>(null);
  const selectedId = selectedSession ? rowId(selectedSession, ["id", "session_id"]) : null;

  const load = useCallback(async () => {
    setSessions((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await browserRuntimeApi.listSessions(settings);
      const rows = toItems(response);
      setSessions({ data: rows, error: null, loading: false, updatedAt: nowLabel() });
      if (!selectedSession && rows.length) {
        setSelectedSession(rows[0]);
      }
    } catch (error) {
      setSessions({
        data: null,
        error: error instanceof Error ? error.message : "Browser Runtime API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [selectedSession, settings]);

  const loadDetails = useCallback(
    async (row: JsonRecord) => {
      const id = rowId(row, ["id", "session_id"]);
      setSelectedSession(row);
      try {
        const [eventList, snapshotList] = await Promise.all([
          browserRuntimeApi.listEvents(id, settings),
          browserRuntimeApi.listSnapshots(id, settings),
        ]);
        setEvents(toItems(eventList));
        setSnapshots(toItems(snapshotList));
      } catch {
        setEvents([]);
        setSnapshots([]);
      }
    },
    [settings],
  );

  const createReplay = async () => {
    if (!selectedId) {
      return;
    }
    const created = await browserRuntimeApi.createReplay(selectedId, settings);
    const replayId = valueAt(created, ["id", "replay_id"]);
    const exported = replayId !== "-" ? await browserRuntimeApi.exportReplay(replayId, settings) : created;
    setReplay({ created, exported });
  };

  useAutoRefresh(true, settings.refreshIntervalMs, load);
  useEffect(() => {
    if (selectedSession) {
      void loadDetails(selectedSession);
    }
  }, [loadDetails, selectedSession]);

  return (
    <div className="split-page">
      <Panel title="Browser Runtime Sessions" description="Remote worker browser sessions and lifecycle metadata." action={<RefreshButton onClick={load} />}>
        <LoadNotice state={sessions} />
        <Table
          rows={sessions.data || []}
          selectedId={selectedId}
          onSelect={(row) => void loadDetails(row)}
          emptyLabel="No browser runtime sessions found."
          columns={[
            { key: "id", label: "session_id", aliases: ["session_id"] },
            { key: "worker_id", label: "worker_id" },
            { key: "browser", label: "browser" },
            { key: "session_status", label: "status" },
            { key: "created_at", label: "created_at" },
            { key: "last_activity_at", label: "last_activity_at" },
            { key: "metadata", label: "metadata" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <div className="detail-title">
          <h2>Timeline / Snapshots / Replay</h2>
          <button className="primary-button" onClick={() => void createReplay()} disabled={!selectedId}>
            <History size={15} />
            Create replay metadata
          </button>
        </div>
        <p className="foundation-note">Replay is metadata-only. It does not re-execute browser actions.</p>
        <h3>Events</h3>
        <Timeline rows={events} primary="event_type" secondary="message" />
        <h3>Snapshots</h3>
        <Table
          rows={snapshots}
          emptyLabel="No snapshots."
          columns={[
            { key: "snapshot_type", label: "type" },
            { key: "url", label: "url" },
            { key: "page_title", label: "page_title" },
            { key: "screenshot_path", label: "screenshot_path" },
            { key: "html_path", label: "html_path" },
          ]}
        />
        <h3>Replay Metadata</h3>
        <JsonPreview value={replay || { status: "not created" }} />
      </aside>
    </div>
  );
}

function ConversationsPage({
  settings,
  targetThreadId,
  language,
}: {
  settings: AdminSettings;
  targetThreadId?: string;
  language: UiLanguage;
}) {
  const t = useCallback((key: UiTextKey) => textFor(language, key), [language]);
  const [threads, setThreads] = useState<AsyncState<ConversationThread[]>>(emptyState());
  const [selectedThread, setSelectedThread] = useState<ConversationThread | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [events, setEvents] = useState<ConversationEvent[]>([]);
  const [approvals, setApprovals] = useState<ConversationApproval[]>([]);
  const [playbooks, setPlaybooks] = useState<ConversationPlaybook[]>([]);
  const [playbookRuns, setPlaybookRuns] = useState<ConversationPlaybookRun[]>([]);
  const [artifacts, setArtifacts] = useState<OutputArtifact[]>([]);
  const [selectedPlaybookName, setSelectedPlaybookName] = useState("browser_screenshot_report");
  const [newTitle, setNewTitle] = useState("Phase 37 frontend conversation test");
  const [messageInput, setMessageInput] = useState("Create a short operations update and show the execution events.");
  const [runStatus, setRunStatus] = useState("idle");
  const [connectionState, setConnectionState] = useState("unknown");
  const [detailError, setDetailError] = useState<string | null>(null);
  const [autoRefreshEvents, setAutoRefreshEvents] = useState(false);
  const [lastRunMetadata, setLastRunMetadata] = useState<JsonRecord | null>(null);
  const selectedId = selectedThread?.id ?? null;

  const load = useCallback(async () => {
    setThreads((current) => ({ ...current, loading: true, error: null }));
    try {
      const [response, playbookResponse, runResponse] = await Promise.all([
        conversationClient.listThreads(settings),
        conversationClient.listPlaybooks(settings),
        conversationClient.listPlaybookRuns(settings),
      ]);
      setConnectionState("connected");
      setThreads({ data: response.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
      setPlaybooks(playbookResponse.items ?? []);
      setPlaybookRuns(runResponse.items ?? []);
    } catch (error) {
      setConnectionState("disconnected");
      setThreads({
        data: null,
        error: error instanceof Error ? error.message : "AI Server unreachable",
        loading: false,
        updatedAt: nowLabel(),
      });
      setPlaybooks([]);
      setPlaybookRuns([]);
    }
  }, [settings]);

  const loadThread = useCallback(async (thread: ConversationThread) => {
    setSelectedThread(thread);
    setDetailError(null);
    try {
      const [messageList, eventList, approvalList, artifactList] = await Promise.all([
        conversationClient.listMessages(thread.id, settings),
        conversationClient.listEvents(thread.id, settings),
        conversationClient.listApprovals(thread.id, settings),
        outputArtifactClient.listArtifacts(settings, { threadId: thread.id }),
      ]);
      setMessages(messageList.items);
      setEvents(eventList.items);
      setApprovals(approvalList.items);
      setArtifacts(artifactList.items ?? []);
      const runResponse = await conversationClient.listPlaybookRuns(settings);
      setPlaybookRuns(runResponse.items ?? []);
      setConnectionState("connected");
    } catch (error) {
      setMessages([]);
      setEvents([]);
      setApprovals([]);
      setArtifacts([]);
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "AI Server unreachable");
    }
  }, [settings]);

  const createThread = async () => {
    const title = newTitle.trim() || `Conversation ${new Date().toLocaleString()}`;
    setRunStatus("creating thread");
    setDetailError(null);
    try {
      const thread = await conversationClient.createThread(
        { title, metadata: { source: "admin_dashboard", phase: "37" } },
        settings,
      );
      setSelectedThread(thread);
      setMessages([]);
      setEvents([]);
      setApprovals([]);
      setLastRunMetadata(null);
      setConnectionState("connected");
      await load();
      await loadThread(thread);
      setRunStatus("thread created");
    } catch (error) {
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "AI Server unreachable");
      setRunStatus("error");
    }
  };

  const refreshSelected = useCallback(async () => {
    if (selectedThread) {
      await loadThread(selectedThread);
    }
  }, [loadThread, selectedThread]);

  const sendMessage = async () => {
    if (!selectedThread) {
      setDetailError("Create or select a thread before sending a message.");
      return;
    }
    const content = messageInput.trim();
    if (!content) {
      return;
    }
    setRunStatus("sending message");
    setDetailError(null);
    try {
      await conversationClient.sendMessage(
        selectedThread.id,
        { role: "user", content, metadata: { source: "admin_dashboard", phase: "37" } },
        settings,
      );
      await refreshSelected();
      setConnectionState("connected");
      setRunStatus("message sent");
    } catch (error) {
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "AI Server unreachable");
      setRunStatus("error");
    }
  };

  const runConversation = async (
    mode: "auto_safe" | "review_first" = "auto_safe",
    executionMode: "immediate" | "background" | "scheduled" = "immediate",
  ) => {
    if (!selectedThread) {
      setDetailError("Create or select a thread before running conversation.");
      return;
    }
    const userMessages = messages.filter((message) => message.role === "user");
    const content = messageInput.trim() || userMessages[userMessages.length - 1]?.content || "";
    if (!content) {
      setDetailError("Run requires a message.");
      return;
    }
    setRunStatus(executionMode === "background" ? "queueing background task" : "running conversation");
    setDetailError(null);
    try {
      const response = await conversationClient.runConversation(
        selectedThread.id,
        content,
        settings,
        mode,
        selectedPlaybookName || null,
        executionMode,
      );
      setMessages((await conversationClient.listMessages(selectedThread.id, settings)).items);
      setApprovals((await conversationClient.listApprovals(selectedThread.id, settings)).items);
      setPlaybookRuns((await conversationClient.listPlaybookRuns(settings)).items ?? []);
      setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId: selectedThread.id })).items ?? []);
      setEvents(response.events);
      setLastRunMetadata(response.result_metadata);
      setConnectionState("connected");
      setRunStatus(
        `mode: ${response.execution_mode} | task: ${response.task_run_id ?? "-"} | route: ${response.route_name} | tool: ${response.selected_tool ?? "none"} | risk: ${response.risk_level ?? "-"} | approval: ${response.approval_status ?? "-"} | success: ${response.success}`,
      );
    } catch (error) {
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "AI Server unreachable");
      setRunStatus("error");
    }
  };

  const runSelectedPlaybook = async () => {
    const playbook = playbooks.find((item) => item.name === selectedPlaybookName);
    if (!playbook) {
      setDetailError("Select an available playbook before running.");
      return;
    }
    setRunStatus("running playbook");
    setDetailError(null);
    try {
      const run = await conversationClient.runPlaybook(
        playbook.id,
        { message: messageInput, url: "https://example.com", topic: messageInput || "AI automation operations" },
        settings,
        "review_first",
        selectedThread?.id ?? null,
      );
      setPlaybookRuns((await conversationClient.listPlaybookRuns(settings)).items ?? []);
      if (selectedThread) {
        await loadThread(selectedThread);
      }
      setRunStatus(`Playbook run ${run.status}: ${run.id}`);
    } catch (error) {
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "Playbook API unreachable");
      setRunStatus("error");
    }
  };

  const mutateApproval = async (approvalId: string, action: "approve" | "reject" | "cancel" | "execute") => {
    if (!selectedThread) {
      return;
    }
    setRunStatus(`${action} approval`);
    setDetailError(null);
    try {
      if (action === "approve") {
        await conversationClient.approveApproval(approvalId, "Looks safe to execute.", settings);
      } else if (action === "reject") {
        await conversationClient.rejectApproval(approvalId, "Need to rewrite before execution.", settings);
      } else if (action === "cancel") {
        await conversationClient.cancelApproval(approvalId, "Cancelled before execution.", settings);
      } else {
        const response = await conversationClient.executeApproval(approvalId, settings);
        setLastRunMetadata(response.result_metadata);
        setEvents(response.events);
      }
      await loadThread(selectedThread);
      setPlaybookRuns((await conversationClient.listPlaybookRuns(settings)).items ?? []);
      setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId: selectedThread.id })).items ?? []);
      setConnectionState("connected");
      setRunStatus(`${action} approval completed`);
    } catch (error) {
      setConnectionState("disconnected");
      setDetailError(error instanceof Error ? error.message : "Approval API unreachable");
      setRunStatus("error");
    }
  };

  const saveMessageAsArtifact = async (message: ConversationMessage) => {
    setRunStatus("saving artifact");
    setDetailError(null);
    try {
      await outputArtifactClient.createFromMessage(message.id, settings);
      if (selectedThread) {
        setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId: selectedThread.id })).items ?? []);
        await loadThread(selectedThread);
      }
      setRunStatus("artifact saved");
    } catch (error) {
      setDetailError(error instanceof Error ? error.message : "Output Artifact API unreachable");
      setRunStatus("artifact error");
    }
  };

  const exportArtifact = async (artifact: OutputArtifact) => {
    setRunStatus("exporting artifact");
    setDetailError(null);
    try {
      const exported = await outputArtifactClient.exportArtifact(artifact.id, "markdown", settings);
      setLastRunMetadata({ artifact_export: exported });
      setRunStatus(`artifact exported: ${exported.export_path}`);
    } catch (error) {
      setDetailError(error instanceof Error ? error.message : "Artifact export failed");
      setRunStatus("artifact export error");
    }
  };

  useEffect(() => {
    if (!autoRefreshEvents || !selectedThread) {
      return undefined;
    }
    const timer = window.setInterval(() => {
      void refreshSelected();
    }, 5000);
    return () => window.clearInterval(timer);
  }, [autoRefreshEvents, refreshSelected, selectedThread]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!targetThreadId || selectedId === targetThreadId) {
      return;
    }
    const listedThread = threads.data?.find((thread) => thread.id === targetThreadId);
    if (listedThread) {
      void loadThread(listedThread);
      return;
    }
    void conversationClient.getThread(targetThreadId, settings).then(loadThread).catch((error) => {
      setDetailError(error instanceof Error ? error.message : "Conversation deep link unavailable");
    });
  }, [loadThread, selectedId, settings, targetThreadId, threads.data]);

  const assistantMessages = messages.filter((message) => message.role === "assistant");
  const latestAssistantMessage = assistantMessages[assistantMessages.length - 1];
  const latestEventPayload = events.length > 0 ? events[events.length - 1].payload : { status: "no events" };
  const routeEvent = [...events].reverse().find((event) => event.event_type === "route_selected");
  const pendingApprovalCount = approvals.filter((approval) => approval.approval_status === "pending").length;

  return (
    <div className="page-stack">
      <section className="conversation-command-center">
        <div>
          <p className="section-eyebrow">{t("conversationConsoleTitle")}</p>
          <h2>{t("conversationConsoleTitle")}</h2>
          <p>{t("conversationOperatorSummary")}</p>
        </div>
        <div className="conversation-mode-grid">
          <span>{t("autoSafeModeSummary")}</span>
          <span>{t("reviewFirstModeSummary")}</span>
          <span>{t("backgroundModeSummary")}</span>
        </div>
      </section>
      <section className="metrics-grid compact">
        <DataCard title={t("conversationThreads")} value={threads.data?.length ?? "-"} detail={selectedThread?.title ?? t("selectedConversation")} icon={<MessageSquareText size={20} />} />
        <DataCard title={t("messagesTitle")} value={messages.length} detail={`${assistantMessages.length} assistant`} icon={<Send size={20} />} />
        <DataCard title={t("pendingApprovalsTitle")} value={pendingApprovalCount} detail={`${approvals.length} total`} icon={<ShieldCheck size={20} />} warning={pendingApprovalCount > 0} />
        <DataCard title={t("generatedArtifactsTitle")} value={artifacts.length} detail={selectedThread?.title ?? t("selectedConversation")} icon={<FileText size={20} />} />
      </section>
      <div className="split-page">
        <Panel
          title={t("conversationConsoleTitle")}
          description={t("conversationConsoleDescription")}
          action={<RefreshButton onClick={load} />}
        >
          <div className="conversation-toolbar">
            <input
              value={newTitle}
              onChange={(event) => setNewTitle(event.target.value)}
              aria-label={t("createConversationTitle")}
              placeholder={t("createConversationTitle")}
            />
            <button className="primary-button" onClick={() => void createThread()}>
              <MessageSquareText size={15} />
              {t("createThreadAction")}
            </button>
          </div>
          <div className="summary-strip">
            <span>{t("conversationConnection")}: <StatusPill value={connectionState} /></span>
            <span>{t("workspaceLabel")}: {settings.workspaceId}</span>
            <span>{t("userLabel")}: {settings.userId}</span>
            <span>{t("selectedConversation")}: {selectedThread?.id ?? "-"}</span>
          </div>
          <LoadNotice state={threads} />
          <Table
            rows={(threads.data || []) as unknown as JsonRecord[]}
            selectedId={selectedId}
            onSelect={(row) => void loadThread(row as unknown as ConversationThread)}
            emptyLabel={t("noConversationThreads")}
            columns={[
              { key: "id", label: "thread_id", aliases: ["thread_id"] },
              { key: "title", label: "title" },
              { key: "status", label: "status" },
              { key: "created_at", label: "created_at" },
              { key: "updated_at", label: "updated_at" },
            ]}
          />
        </Panel>
        <aside className="detail-panel">
          <h2>{t("conversationDetailTitle")}</h2>
          <p className="foundation-note">{t("conversationDetailDescription")}</p>
        <div className="chat-status-row">
          <span>{t("runStatusLabel")}: <StatusPill value={runStatus} /></span>
          <span>{t("routeSelectedLabel")}: {valueAt(routeEvent?.payload as JsonRecord, ["route_name"], "-")}</span>
          <span>{t("selectedToolLabel")}: {valueAt(routeEvent?.payload as JsonRecord, ["selected_tool"], "-")}</span>
          <span>{t("latestAssistantLabel")}: {latestAssistantMessage?.content ?? "-"}</span>
        </div>
        {detailError ? (
          <div className="notice notice-error">
            <AlertTriangle size={16} />
            {detailError}
          </div>
        ) : null}
        <div className="conversation-compose">
          <textarea
            value={messageInput}
            onChange={(event) => setMessageInput(event.target.value)}
            placeholder={t("messageInputPlaceholder")}
          />
          <div className="conversation-actions">
            <button className="ghost-button" onClick={() => void sendMessage()} disabled={!selectedThread}>
              <Send size={15} />
              {t("sendMessageAction")}
            </button>
            <button className="primary-button" onClick={() => void runConversation()} disabled={!selectedThread}>
              <Activity size={15} />
              {t("runAutoSafeAction")}
            </button>
            <button className="ghost-button" onClick={() => void runConversation("review_first")} disabled={!selectedThread}>
              <AlertTriangle size={15} />
              {t("runReviewFirstAction")}
            </button>
            <button className="ghost-button" onClick={() => void runConversation("review_first", "background")} disabled={!selectedThread}>
              <PlayCircle size={15} />
              {t("queueBackgroundAction")}
            </button>
            <button className="ghost-button" onClick={() => void refreshSelected()} disabled={!selectedThread}>
              <RefreshCcw size={15} />
              {t("refreshMessagesEventsAction")}
            </button>
          </div>
          <label className="checkbox-row">
            <input
              type="checkbox"
              checked={autoRefreshEvents}
              onChange={(event) => setAutoRefreshEvents(event.target.checked)}
            />
            {t("pollEventsAction")}
          </label>
        </div>
        <h3>{t("playbookSelectorTitle")}</h3>
        <p className="foundation-note">{t("playbookSelectorDescription")}</p>
        <div className="conversation-compose">
          <select value={selectedPlaybookName} onChange={(event) => setSelectedPlaybookName(event.target.value)}>
            {playbooks.map((playbook) => (
              <option key={playbook.id} value={playbook.name}>
                {playbook.name} | {playbook.risk_level} | {playbook.status}
              </option>
            ))}
          </select>
          <div className="summary-strip">
            <span>{t("playbookListLabel")}: {playbooks.length}</span>
            <span>{t("selectedPlaybookLabel")}: {selectedPlaybookName || "-"}</span>
            <span>{t("descriptionLabel")}: {playbooks.find((item) => item.name === selectedPlaybookName)?.description ?? "-"}</span>
          </div>
          <div className="conversation-actions">
            <button className="primary-button" onClick={() => void runSelectedPlaybook()}>
              <Activity size={15} />
              {t("runPlaybookAction")}
            </button>
            <button className="ghost-button" onClick={() => void runConversation("review_first")} disabled={!selectedThread}>
              <AlertTriangle size={15} />
              {t("runConversationWithPlaybookAction")}
            </button>
          </div>
        </div>
        <h3>{t("playbookRunsTitle")}</h3>
        <div className="approval-list">
          {playbookRuns.length > 0 ? (
            playbookRuns.slice(0, 6).map((run) => (
              <div key={run.id} className="approval-card">
                <div className="approval-card-header">
                  <strong>run: {run.id}</strong>
                  <StatusPill value={run.status} />
                  <span>current_step: {run.current_step}</span>
                </div>
                <div className="chat-status-row">
                  <span>playbook_id: {run.playbook_id}</span>
                  <span>thread_id: {run.thread_id}</span>
                </div>
                <h4>Step timeline</h4>
                <JsonPreview value={run.output_payload?.steps ?? []} />
              </div>
            ))
          ) : (
            <div className="empty-chat">No Playbook runs yet. Try browser_screenshot_report or content_generation.</div>
          )}
        </div>
        <h3>{t("pendingApprovalsTitle")}</h3>
        <p className="foundation-note">{t("pendingApprovalsDescription")}</p>
        <div className="approval-list">
          {approvals.length > 0 ? (
            approvals.map((approval) => (
              <div key={approval.id} className={`approval-card approval-risk-${approval.risk_level}`}>
                <div className="approval-card-header">
                  <strong>{approval.proposed_action}</strong>
                  <StatusPill value={`${approval.risk_level} risk`} />
                  <StatusPill value={approval.approval_status} />
                </div>
                <div className="chat-status-row">
                  <span>route: {approval.route_name}</span>
                  <span>tool: {approval.selected_tool ?? "none"}</span>
                  <span>approval_id: {approval.id}</span>
                </div>
                <JsonPreview value={approval.proposed_payload} />
                <div className="conversation-actions">
                  <button className="ghost-button" onClick={() => void mutateApproval(approval.id, "approve")} disabled={approval.approval_status !== "pending"}>
                    Approve
                  </button>
                  <button className="ghost-button" onClick={() => void mutateApproval(approval.id, "reject")} disabled={approval.approval_status !== "pending"}>
                    Reject
                  </button>
                  <button className="ghost-button" onClick={() => void mutateApproval(approval.id, "cancel")} disabled={!["pending", "approved"].includes(approval.approval_status)}>
                    Cancel
                  </button>
                  <button className="primary-button" onClick={() => void mutateApproval(approval.id, "execute")} disabled={approval.approval_status !== "approved"}>
                    Execute approved action
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="empty-chat">{t("noPendingApprovals")}</div>
          )}
        </div>
        <h3>{t("messagesTitle")}</h3>
        <div className="approval-list">
          {messages.length > 0 ? (
            messages.map((message) => (
              <div key={message.id} className="approval-card">
                <div className="approval-card-header">
                  <strong>{message.role}</strong>
                  <span>{message.created_at}</span>
                </div>
                <p>{message.content}</p>
                {message.role === "assistant" ? (
                  <button className="ghost-button" onClick={() => void saveMessageAsArtifact(message)}>
                    Save as Artifact
                  </button>
                ) : null}
              </div>
            ))
          ) : (
            <div className="empty-chat">{t("noMessages")}</div>
          )}
        </div>
        <h3>{t("generatedArtifactsTitle")}</h3>
        <div className="approval-list">
          {artifacts.length > 0 ? (
            artifacts.map((artifact) => (
              <div key={artifact.id} className="approval-card">
                <div className="approval-card-header">
                  <strong>{artifact.title}</strong>
                  <StatusPill value={artifact.artifact_type} />
                  <StatusPill value={artifact.source_type} />
                </div>
                <div className="chat-status-row">
                  <span>artifact_id: {artifact.id}</span>
                  <span>playbook_run_id: {artifact.playbook_run_id ?? "-"}</span>
                </div>
                <p>{artifact.summary ?? artifact.file_path ?? "No summary"}</p>
                <button className="ghost-button" onClick={() => void exportArtifact(artifact)}>
                  Export markdown
                </button>
              </div>
            ))
          ) : (
            <div className="empty-chat">{t("noGeneratedArtifacts")}</div>
          )}
        </div>
        <h3>{t("eventsTitle")}</h3>
        <Timeline rows={events as unknown as JsonRecord[]} primary="event_type" secondary="message" />
        <h3>{t("latestEventPayloadTitle")}</h3>
        <JsonPreview value={latestEventPayload} />
        <h3>{t("resultMetadataTitle")}</h3>
        <JsonPreview value={lastRunMetadata || { status: "run a conversation to see full bridge metadata" }} />
        </aside>
      </div>
    </div>
  );
}

function PlaybooksPage({
  settings,
  targetThreadId,
  onNavigate,
}: {
  settings: AdminSettings;
  targetThreadId?: string;
  onNavigate: (page: PageKey, target?: DeepLinkTarget) => void;
}) {
  const [playbooks, setPlaybooks] = useState<AsyncState<ConversationPlaybook[]>>(emptyState());
  const [runs, setRuns] = useState<AsyncState<ConversationPlaybookRun[]>>(emptyState());

  const load = useCallback(async () => {
    setPlaybooks((current) => ({ ...current, loading: true, error: null }));
    setRuns((current) => ({ ...current, loading: true, error: null }));
    try {
      const [playbookResponse, runResponse] = await Promise.all([
        conversationClient.listPlaybooks(settings),
        conversationClient.listPlaybookRuns(settings),
      ]);
      setPlaybooks({ data: playbookResponse.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
      setRuns({ data: runResponse.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Playbook API unreachable";
      setPlaybooks({ data: null, error: message, loading: false, updatedAt: nowLabel() });
      setRuns({ data: null, error: message, loading: false, updatedAt: nowLabel() });
    }
  }, [settings]);

  useEffect(() => {
    void load();
  }, [load]);

  const allRuns = runs.data ?? [];
  const visibleRuns = targetThreadId ? allRuns.filter((run) => run.thread_id === targetThreadId) : allRuns;

  return (
    <div className="page-stack">
      <Panel
        title="Playbooks"
        description="Conversation Execution Templates & Playbooks. Built-in templates plus run history; not a full workflow builder."
        action={<RefreshButton onClick={load} />}
      >
        <LoadNotice state={playbooks} />
        <Table
          rows={(playbooks.data || []) as unknown as JsonRecord[]}
          emptyLabel="No playbooks."
          columns={[
            { key: "name", label: "name" },
            { key: "category", label: "category" },
            { key: "status", label: "status" },
            { key: "risk_level", label: "risk" },
            { key: "description", label: "description" },
          ]}
        />
      </Panel>
      <Panel
        title="Playbook Runs"
        description={targetThreadId ? "Filtered by Run Cockpit thread context. Step timeline is stored in output_payload.steps." : "Step timeline is stored in output_payload.steps."}
        action={<RefreshButton onClick={load} />}
      >
        <div className="summary-strip">
          <span>Thread context: {targetThreadId ?? "all runs"}</span>
          <span>Visible runs: {visibleRuns.length}</span>
          <span>Total runs: {allRuns.length}</span>
        </div>
        {targetThreadId ? (
          <div className="conversation-actions">
            <button className="ghost-button" onClick={() => onNavigate("conversations", { threadId: targetThreadId })}>
              Open linked conversation
            </button>
            <button className="ghost-button" onClick={() => onNavigate("playbooks")}>
              Show all runs
            </button>
          </div>
        ) : null}
        <LoadNotice state={runs} />
        <Table
          rows={visibleRuns as unknown as JsonRecord[]}
          emptyLabel={targetThreadId ? "No playbook runs for linked thread." : "No playbook runs."}
          columns={[
            { key: "id", label: "run_id" },
            { key: "status", label: "status" },
            { key: "current_step", label: "current_step" },
            { key: "playbook_id", label: "playbook_id" },
            { key: "thread_id", label: "thread_id" },
          ]}
        />
        <div className="last-updated">Last updated: {runs.updatedAt ?? "-"}</div>
      </Panel>
    </div>
  );
}

function OutputLibraryPage({
  settings,
  targetArtifactId,
  targetThreadId,
  targetTaskRunId,
  onNavigate,
}: {
  settings: AdminSettings;
  targetArtifactId?: string;
  targetThreadId?: string;
  targetTaskRunId?: string;
  onNavigate: (page: PageKey, target?: DeepLinkTarget) => void;
}) {
  const [artifacts, setArtifacts] = useState<AsyncState<OutputArtifact[]>>(emptyState());
  const [selectedArtifact, setSelectedArtifact] = useState<OutputArtifact | null>(null);
  const [artifactType, setArtifactType] = useState("");
  const [sourceType, setSourceType] = useState("");
  const [artifactRole, setArtifactRole] = useState("");
  const [artifactStage, setArtifactStage] = useState("");
  const [retentionPolicy, setRetentionPolicy] = useState("");
  const [exportPreview, setExportPreview] = useState<JsonRecord | null>(null);
  const [lineagePreview, setLineagePreview] = useState<JsonRecord | null>(null);

  const load = useCallback(async () => {
    setArtifacts((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await outputArtifactClient.listArtifacts(settings, {
        artifactType: artifactType || undefined,
        sourceType: sourceType || undefined,
        artifactRole: artifactRole || undefined,
        artifactStage: artifactStage || undefined,
        retentionPolicy: retentionPolicy || undefined,
      });
      setArtifacts({ data: response.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setArtifacts({
        data: null,
        error: error instanceof Error ? error.message : "Output Artifact API unreachable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [artifactRole, artifactStage, artifactType, retentionPolicy, settings, sourceType]);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!targetArtifactId || selectedArtifact?.id === targetArtifactId) {
      return;
    }
    const listedArtifact = artifacts.data?.find((artifact) => artifact.id === targetArtifactId);
    if (listedArtifact) {
      setSelectedArtifact(listedArtifact);
      return;
    }
    void outputArtifactClient.getArtifact(targetArtifactId, settings).then(setSelectedArtifact).catch(() => undefined);
  }, [artifacts.data, selectedArtifact?.id, settings, targetArtifactId]);

  const allArtifacts = artifacts.data ?? [];
  const visibleArtifacts = allArtifacts.filter((artifact) => {
    const matchesThread =
      !targetThreadId || artifact.thread_id === targetThreadId || artifact.source_conversation_id === targetThreadId;
    const matchesTask =
      !targetTaskRunId || artifact.task_run_id === targetTaskRunId || artifact.source_task_run_id === targetTaskRunId;
    return matchesThread && matchesTask;
  });
  const hasArtifactContext = Boolean(targetThreadId || targetTaskRunId || targetArtifactId);

  const exportSelected = async (format: "markdown" | "json" | "txt") => {
    if (!selectedArtifact) {
      return;
    }
    const exported = await outputArtifactClient.exportArtifact(selectedArtifact.id, format, settings);
    setExportPreview(exported as unknown as JsonRecord);
    await load();
  };

  const exportPipelineSelected = async (format: "markdown" | "html" | "json" | "txt" | "bundle_zip") => {
    if (!selectedArtifact) {
      return;
    }
    const exported = await outputArtifactClient.exportArtifactPipeline(selectedArtifact.id, format, settings);
    setExportPreview(exported as unknown as JsonRecord);
    await load();
  };

  const packageSelected = async () => {
    if (!selectedArtifact) {
      return;
    }
    const packaged = await outputArtifactClient.packageArtifact(selectedArtifact.id, settings);
    setExportPreview(packaged as unknown as JsonRecord);
    await load();
  };

  const loadLineage = async () => {
    if (!selectedArtifact) {
      return;
    }
    const lineage = await outputArtifactClient.getLineage(selectedArtifact.id, settings);
    setLineagePreview(lineage as unknown as JsonRecord);
  };

  return (
    <div className="split-page">
      <Panel
        title="Output Library"
        description="Reusable Output Artifacts from Conversation, Playbook, Tool, Browser Runtime, RAG, ContentAgent, Planning, and OpenClaw mock. This is not a full DAM or cloud file manager."
        action={<RefreshButton onClick={load} />}
      >
        <div className="summary-strip">
          <span>Artifact context: {hasArtifactContext ? "linked run" : "all artifacts"}</span>
          <span>thread_id: {targetThreadId ?? "-"}</span>
          <span>task_run_id: {targetTaskRunId ?? "-"}</span>
          <span>artifact_id: {targetArtifactId ?? "-"}</span>
          <span>visible: {visibleArtifacts.length}</span>
          <span>total: {allArtifacts.length}</span>
        </div>
        {hasArtifactContext ? (
          <div className="conversation-actions">
            {targetThreadId ? (
              <button className="ghost-button" onClick={() => onNavigate("conversations", { threadId: targetThreadId })}>
                Open linked conversation
              </button>
            ) : null}
            {targetTaskRunId ? (
              <button className="ghost-button" onClick={() => onNavigate("tasks", { taskRunId: targetTaskRunId })}>
                Open linked task run
              </button>
            ) : null}
            <button className="ghost-button" onClick={() => onNavigate("output-library")}>
              Show all artifacts
            </button>
          </div>
        ) : null}
        <div className="conversation-toolbar">
          <select value={artifactType} onChange={(event) => setArtifactType(event.target.value)} aria-label="artifact_type filter">
            <option value="">All artifact_type</option>
            {["content_draft", "report", "rag_answer", "screenshot", "html_snapshot", "plan", "json", "markdown", "text"].map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
          <select value={sourceType} onChange={(event) => setSourceType(event.target.value)} aria-label="source_type filter">
            <option value="">All source_type</option>
            {["conversation", "playbook", "tool", "browser_runtime", "rag", "content_agent", "planning", "openclaw_mock"].map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
          <select value={artifactRole} onChange={(event) => setArtifactRole(event.target.value)} aria-label="artifact_role filter">
            <option value="">All artifact_role</option>
            {["screenshot", "report", "transcript", "markdown", "html", "json", "bundle", "debug", "replay", "dataset"].map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
          <select value={artifactStage} onChange={(event) => setArtifactStage(event.target.value)} aria-label="artifact_stage filter">
            <option value="">All artifact_stage</option>
            {["raw", "processed", "packaged", "exported", "archived"].map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
          <select value={retentionPolicy} onChange={(event) => setRetentionPolicy(event.target.value)} aria-label="retention_policy filter">
            <option value="">All retention_policy</option>
            {["temporary", "standard", "persistent", "compliance_hold"].map((value) => (
              <option key={value} value={value}>{value}</option>
            ))}
          </select>
        </div>
        <LoadNotice state={artifacts} />
        <Table
          rows={visibleArtifacts as unknown as JsonRecord[]}
          selectedId={selectedArtifact?.id ?? null}
          onSelect={(row) => setSelectedArtifact(row as unknown as OutputArtifact)}
          emptyLabel={hasArtifactContext ? "No output artifacts for linked run context." : "No output artifacts yet."}
          columns={[
            { key: "title", label: "title" },
            { key: "artifact_type", label: "artifact_type" },
            { key: "artifact_role", label: "role" },
            { key: "artifact_stage", label: "stage" },
            { key: "retention_policy", label: "retention" },
            { key: "source_type", label: "source_type" },
            { key: "status", label: "status" },
            { key: "created_at", label: "created_at" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <h2>Artifact Detail</h2>
        {selectedArtifact ? (
          <>
            <div className="chat-status-row">
              <span>artifact_id: {selectedArtifact.id}</span>
              <span>thread_id: {selectedArtifact.thread_id ?? "-"}</span>
              <span>playbook_run_id: {selectedArtifact.playbook_run_id ?? "-"}</span>
              <span>task_run_id: {selectedArtifact.task_run_id ?? "-"}</span>
              <span>workflow_run_id: {selectedArtifact.workflow_run_id ?? "-"}</span>
              <span>workflow_step_id: {selectedArtifact.workflow_step_id ?? "-"}</span>
              <span>checkpoint_id: {selectedArtifact.checkpoint_id ?? "-"}</span>
              <span>memory_snapshot_id: {selectedArtifact.memory_snapshot_id ?? "-"}</span>
              <span>workflow_template_id: {selectedArtifact.workflow_template_id ?? "-"}</span>
              <span>workflow_template_version_id: {selectedArtifact.workflow_template_version_id ?? "-"}</span>
              <span>workflow_template_run_id: {selectedArtifact.workflow_template_run_id ?? "-"}</span>
              <span>producing_node_key: {selectedArtifact.producing_node_key ?? "-"}</span>
              <span>replay_source: {selectedArtifact.replay_source ?? "-"}</span>
            </div>
            <div className="approval-card">
              <div className="approval-card-header">
                <strong>{selectedArtifact.title}</strong>
                <StatusPill value={selectedArtifact.artifact_type} />
                <StatusPill value={selectedArtifact.artifact_role ?? "no_role"} />
                <StatusPill value={selectedArtifact.artifact_stage} />
                <StatusPill value={selectedArtifact.retention_policy} />
                <StatusPill value={selectedArtifact.source_type} />
              </div>
              <div className="chat-status-row">
                <span>root_artifact_id: {selectedArtifact.root_artifact_id ?? "-"}</span>
                <span>parent_artifact_id: {selectedArtifact.parent_artifact_id ?? "-"}</span>
                <span>exportable: {String(selectedArtifact.exportable)}</span>
              </div>
              <p>{selectedArtifact.summary ?? selectedArtifact.file_path ?? "No summary"}</p>
            <JsonPreview value={selectedArtifact.metadata} />
            <h4>Graph lineage</h4>
            <JsonPreview value={selectedArtifact.graph_lineage || {}} />
            </div>
            <h3>Preview content</h3>
            <pre className="json-preview">{selectedArtifact.content || selectedArtifact.file_path || "File-only artifact; see metadata/path."}</pre>
            <div className="conversation-actions">
              <button className="ghost-button" onClick={() => void exportSelected("markdown")}>Export markdown</button>
              <button className="ghost-button" onClick={() => void exportSelected("json")}>Export json</button>
              <button className="ghost-button" onClick={() => void exportSelected("txt")}>Export txt</button>
              <button className="ghost-button" onClick={() => void exportPipelineSelected("html")}>Export HTML</button>
              <button className="ghost-button" onClick={() => void exportPipelineSelected("bundle_zip")}>Export bundle</button>
              <button className="ghost-button" onClick={() => void packageSelected()}>Package lineage</button>
              <button className="ghost-button" onClick={() => void loadLineage()}>Load lineage</button>
            </div>
            <h3>Export result</h3>
            <JsonPreview value={exportPreview ?? { status: "export an artifact to see output path" }} />
            <h3>Lineage graph</h3>
            <JsonPreview value={lineagePreview ?? { status: "load lineage to see relationship graph" }} />
          </>
        ) : (
          <div className="empty-chat">Select an artifact to preview content and export markdown/json/txt.</div>
        )}
      </aside>
    </div>
  );
}

function TasksPage({ settings, targetTaskRunId }: { settings: AdminSettings; targetTaskRunId?: string }) {
  const [status, setStatus] = useState("queued");
  const [recoveryFilter, setRecoveryFilter] = useState("all");
  const [tasks, setTasks] = useState<AsyncState<TaskRun[]>>(emptyState());
  const [schedulerHealth, setSchedulerHealth] = useState<TaskSchedulerHealth | null>(null);
  const [selectedTask, setSelectedTask] = useState<TaskRun | null>(null);
  const [diagnostics, setDiagnostics] = useState<TaskRunDiagnostics | null>(null);
  const [events, setEvents] = useState<TaskRunEvent[]>([]);
  const [linkedArtifacts, setLinkedArtifacts] = useState<OutputArtifact[]>([]);
  const [actionError, setActionError] = useState<string | null>(null);
  const selectedId = selectedTask?.id ?? null;

  const load = useCallback(async () => {
    setTasks((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await taskRunClient.listTaskRuns(settings, {
        status,
        recoverable: recoveryFilter === "recoverable" ? true : undefined,
        leaseExpired: recoveryFilter === "lease_expired" ? true : undefined,
        scheduledDue: recoveryFilter === "scheduled_due" ? true : undefined,
      });
      const health = await taskRunClient.schedulerHealth(settings);
      setSchedulerHealth(health);
      setTasks({ data: response.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setTasks({
        data: null,
        error: error instanceof Error ? error.message : "Task Runs API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings, status, recoveryFilter]);

  const loadTask = async (row: TaskRun) => {
    setSelectedTask(row);
    try {
      const [eventList, artifactList] = await Promise.all([
        taskRunClient.listEvents(row.id, settings),
        outputArtifactClient.listArtifacts(settings, { taskRunId: row.id }),
      ]);
      const taskDiagnostics = await taskRunClient.diagnostics(row.id, settings);
      setEvents(eventList.items ?? []);
      setLinkedArtifacts(artifactList.items ?? []);
      setDiagnostics(taskDiagnostics);
    } catch (error) {
      setEvents([]);
      setLinkedArtifacts([]);
      setDiagnostics(null);
      setActionError(error instanceof Error ? error.message : "Task Run detail unavailable");
    }
  };

  const mutateTask = async (action: "retry" | "cancel" | "resume" | "recover") => {
    if (!selectedTask) {
      return;
    }
    setActionError(null);
    try {
      const updated =
        action === "retry"
          ? await taskRunClient.retry(selectedTask.id, "Manual retry from Admin Dashboard", settings)
          : action === "cancel"
            ? await taskRunClient.cancel(selectedTask.id, "Manual cancel from Admin Dashboard", settings)
            : action === "recover"
              ? await taskRunClient.recover(selectedTask.id, "Manual recovery from Admin Dashboard", settings)
              : await taskRunClient.resume(selectedTask.id, settings);
      setSelectedTask(updated);
      await loadTask(updated);
      await load();
    } catch (error) {
      setActionError(error instanceof Error ? error.message : `${action} failed`);
    }
  };

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!targetTaskRunId || selectedId === targetTaskRunId) {
      return;
    }
    const listedTask = tasks.data?.find((task) => task.id === targetTaskRunId);
    if (listedTask) {
      void loadTask(listedTask);
      return;
    }
    void taskRunClient.getTaskRun(targetTaskRunId, settings).then(loadTask).catch((error) => {
      setActionError(error instanceof Error ? error.message : "Task run deep link unavailable");
    });
  }, [selectedId, settings, targetTaskRunId, tasks.data]);

  return (
    <div className="split-page">
      <Panel
        title="Task Runs"
        description="Task Orchestration Foundation for background Conversation and Playbook execution. In-process queue only; not Celery, not Kubernetes, not production HA."
        action={
          <div className="inline-controls">
            <select value={status} onChange={(event) => setStatus(event.target.value)}>
              {taskStatuses.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <select value={recoveryFilter} onChange={(event) => setRecoveryFilter(event.target.value)}>
              <option value="all">all</option>
              <option value="recoverable">recoverable</option>
              <option value="lease_expired">lease expired</option>
              <option value="scheduled_due">scheduled due</option>
            </select>
            <RefreshButton onClick={load} />
          </div>
        }
      >
        <section className="metrics-grid compact">
          <DataCard title="Scheduler status" value={schedulerHealth?.status ?? "unavailable"} detail={schedulerHealth?.scheduler_name ?? "in-process"} icon={<Gauge size={18} />} />
          <DataCard title="Heartbeat" value={schedulerHealth?.heartbeat_at ?? "-"} detail={`last scan: ${schedulerHealth?.last_scan_at ?? "-"}`} icon={<Activity size={18} />} />
          <DataCard title="Recovery" value={`${schedulerHealth?.recovered_task_count ?? 0} recovered`} detail={`${schedulerHealth?.active_task_count ?? 0} active`} icon={<RefreshCcw size={18} />} />
        </section>
        <LoadNotice state={tasks} />
        <Table
          rows={(tasks.data || []) as unknown as JsonRecord[]}
          selectedId={selectedId}
          onSelect={(row) => void loadTask(row as unknown as TaskRun)}
          emptyLabel="No task runs for selected status."
          columns={[
            { key: "id", label: "task_run_id" },
            { key: "task_type", label: "task_type" },
            { key: "source_type", label: "source_type" },
            { key: "status", label: "status" },
            { key: "retry_count", label: "retry" },
            { key: "recoverable", label: "recoverable" },
            { key: "lease_expires_at", label: "lease_expires_at" },
            { key: "current_step", label: "step" },
            { key: "workflow_run_id", label: "workflow_run_id" },
            { key: "scheduled_at", label: "scheduled_at" },
            { key: "created_at", label: "created_at" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <h2>Task Run Detail</h2>
        {actionError ? <div className="notice notice-error">{actionError}</div> : null}
        <JsonPreview value={selectedTask || { status: "select a task run" }} />
        <h3>Linked workflow</h3>
        <div className="empty-chat">{selectedTask?.workflow_run_id ?? "No workflow linked yet."}</div>
        <div className="conversation-actions">
          <button className="ghost-button" onClick={() => void mutateTask("retry")} disabled={!selectedTask}>
            Retry
          </button>
          <button className="ghost-button" onClick={() => void mutateTask("cancel")} disabled={!selectedTask}>
            Cancel
          </button>
          <button className="ghost-button" onClick={() => void mutateTask("resume")} disabled={!selectedTask}>
            Resume after approval
          </button>
          <button className="ghost-button" onClick={() => void mutateTask("recover")} disabled={!selectedTask}>
            Recover
          </button>
        </div>
        <h3>Diagnostics</h3>
        <JsonPreview value={diagnostics || { status: "select a task run" }} />
        <h3>Progress timeline</h3>
        <Timeline rows={events as unknown as JsonRecord[]} primary="event_type" secondary="message" />
        <h3>Linked artifacts</h3>
        {linkedArtifacts.length ? (
          linkedArtifacts.map((artifact) => (
            <div className="approval-card" key={artifact.id}>
              <div className="approval-card-header">
                <strong>{artifact.title}</strong>
                <StatusPill value={artifact.artifact_type} />
              </div>
              <p>{artifact.summary ?? artifact.file_path ?? "No summary"}</p>
            </div>
          ))
        ) : (
          <div className="empty-chat">No artifacts linked to this task run yet.</div>
        )}
      </aside>
    </div>
  );
}

function WorkflowsPage({ settings, targetWorkflowRunId }: { settings: AdminSettings; targetWorkflowRunId?: string }) {
  const [status, setStatus] = useState("running");
  const [runs, setRuns] = useState<AsyncState<WorkflowRun[]>>(emptyState());
  const [selectedRun, setSelectedRun] = useState<WorkflowRun | null>(null);
  const [steps, setSteps] = useState<WorkflowStep[]>([]);
  const [checkpoints, setCheckpoints] = useState<WorkflowCheckpoint[]>([]);
  const [memories, setMemories] = useState<AgentMemorySnapshot[]>([]);
  const [linkedArtifacts, setLinkedArtifacts] = useState<OutputArtifact[]>([]);
  const [planner, setPlanner] = useState<WorkflowPlannerResult | null>(null);
  const [runGraph, setRunGraph] = useState<WorkflowGraph | null>(null);
  const [replay, setReplay] = useState<WorkflowReplay | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setRuns((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await workflowClient.listRuns(settings, { status: status === "all" ? undefined : status });
      setRuns({ data: response.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setRuns({
        data: null,
        error: error instanceof Error ? error.message : "Workflow Runs API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings, status]);

  const loadWorkflow = useCallback(
    async (row: WorkflowRun) => {
      setSelectedRun(row);
      setActionError(null);
      try {
        const [stepList, checkpointList, memoryList, artifactList] = await Promise.all([
          workflowClient.listSteps(row.id, settings),
          workflowClient.listCheckpoints(row.id, settings),
          workflowClient.listMemorySnapshots(row.id, settings),
          outputArtifactClient.listArtifacts(settings, { workflowRunId: row.id }),
        ]);
        const [plannerResult, graphResult] = await Promise.all([
          workflowClient.getPlanner(row.id, settings).catch(() => null),
          workflowClient.getRunGraph(row.id, settings).catch(() => null),
        ]);
        setSteps(stepList.items ?? []);
        setCheckpoints(checkpointList.items ?? []);
        setMemories(memoryList.items ?? []);
        setLinkedArtifacts(artifactList.items ?? []);
        setPlanner(plannerResult);
        setRunGraph(graphResult);
        setReplay(null);
      } catch (error) {
        setSteps([]);
        setCheckpoints([]);
        setMemories([]);
        setLinkedArtifacts([]);
        setPlanner(null);
        setRunGraph(null);
        setReplay(null);
        setActionError(error instanceof Error ? error.message : "Workflow detail unavailable");
      }
    },
    [settings],
  );

  const mutateWorkflow = async (action: "pause" | "resume" | "checkpoint" | "replay") => {
    if (!selectedRun) {
      return;
    }
    setActionError(null);
    try {
      if (action === "pause") {
        const updated = await workflowClient.pause(selectedRun.id, settings);
        setSelectedRun(updated);
        await loadWorkflow(updated);
      } else if (action === "resume") {
        const updated = await workflowClient.resume(selectedRun.id, settings);
        setSelectedRun(updated);
        await loadWorkflow(updated);
      } else if (action === "replay") {
        const replayResult = await workflowClient.createReplay(selectedRun.id, settings);
        await loadWorkflow(selectedRun);
        setReplay(replayResult);
      } else {
        await workflowClient.createCheckpoint(selectedRun.id, settings);
        await loadWorkflow(selectedRun);
      }
      await load();
    } catch (error) {
      setActionError(error instanceof Error ? error.message : `Workflow ${action} failed`);
    }
  };

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!targetWorkflowRunId || selectedRun?.id === targetWorkflowRunId) {
      return;
    }
    const listedRun = runs.data?.find((run) => run.id === targetWorkflowRunId);
    if (listedRun) {
      void loadWorkflow(listedRun);
      return;
    }
    void workflowClient
      .getRun(targetWorkflowRunId, settings)
      .then(loadWorkflow)
      .catch((error) => {
        setActionError(error instanceof Error ? error.message : "Linked workflow run unavailable");
      });
  }, [loadWorkflow, runs.data, selectedRun?.id, settings, targetWorkflowRunId]);

  return (
    <div className="split-page">
      <Panel
        title="Workflow Runs"
        description="Recoverable Workflow State for Conversation, Playbook, Task, and Artifact lineage. Foundation only; not a full workflow builder and not ComfyUI."
        action={
          <div className="inline-controls">
            <select value={status} onChange={(event) => setStatus(event.target.value)}>
              {["all", "pending", "running", "paused", "waiting_approval", "completed", "failed", "cancelled"].map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
            <RefreshButton onClick={load} />
          </div>
        }
      >
        <LoadNotice state={runs} />
        {targetWorkflowRunId ? (
          <div className="summary-strip">
            <span>Workflow context: Run Cockpit handoff</span>
            <span>workflow_run_id: {targetWorkflowRunId}</span>
          </div>
        ) : null}
        <Table
          rows={(runs.data || []) as unknown as JsonRecord[]}
          selectedId={selectedRun?.id ?? null}
          onSelect={(row) => void loadWorkflow(row as unknown as WorkflowRun)}
          emptyLabel="No workflow runs for selected status."
          columns={[
            { key: "id", label: "workflow_run_id" },
            { key: "source_type", label: "source_type" },
            { key: "status", label: "status" },
            { key: "workflow_graph_id", label: "graph_id" },
            { key: "current_node_key", label: "current_node" },
            { key: "current_step", label: "current_step" },
            { key: "conversation_thread_id", label: "thread" },
            { key: "playbook_run_id", label: "playbook_run" },
            { key: "task_run_id", label: "task_run" },
            { key: "updated_at", label: "updated_at" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <h2>Workflow Detail</h2>
        {actionError ? <div className="notice notice-error">{actionError}</div> : null}
        <JsonPreview value={selectedRun || { status: "select a workflow run" }} />
        <div className="conversation-actions">
          <button className="ghost-button" onClick={() => void mutateWorkflow("pause")} disabled={!selectedRun}>
            Pause
          </button>
          <button className="ghost-button" onClick={() => void mutateWorkflow("resume")} disabled={!selectedRun}>
            Resume
          </button>
          <button className="ghost-button" onClick={() => void mutateWorkflow("checkpoint")} disabled={!selectedRun}>
            Create checkpoint
          </button>
          <button className="ghost-button" onClick={() => void mutateWorkflow("replay")} disabled={!selectedRun}>
            Create replay metadata
          </button>
        </div>
        <h3>Graph execution</h3>
        <JsonPreview
          value={{
            workflow_graph_id: selectedRun?.workflow_graph_id ?? null,
            graph_execution: selectedRun?.graph_execution ?? false,
            current_node_key: selectedRun?.current_node_key ?? null,
            planned_next_nodes: selectedRun?.planned_next_nodes ?? [],
            skipped_nodes: selectedRun?.skipped_nodes ?? [],
            retry_state: selectedRun?.retry_state ?? {},
            fallback_state: selectedRun?.fallback_state ?? {},
            planner,
            replay,
            linked_graph: runGraph ? { id: runGraph.id, name: runGraph.name, entry_node: runGraph.entry_node } : null,
          }}
        />
        <h3>Step timeline</h3>
        <Timeline rows={steps as unknown as JsonRecord[]} primary="step_name" secondary="status" />
        <h3>Variables / Context</h3>
        <JsonPreview value={{ variables: selectedRun?.variables ?? {}, context: selectedRun?.context ?? {} }} />
        <h3>Checkpoints</h3>
        <Timeline rows={checkpoints as unknown as JsonRecord[]} primary="checkpoint_name" secondary="checkpoint_type" />
        <h3>Agent Memory Snapshots</h3>
        <Timeline rows={memories as unknown as JsonRecord[]} primary="memory_type" secondary="summary" />
        <h3>Linked artifacts</h3>
        {linkedArtifacts.length ? (
          linkedArtifacts.map((artifact) => (
            <div className="approval-card" key={artifact.id}>
              <div className="approval-card-header">
                <strong>{artifact.title}</strong>
                <StatusPill value={artifact.artifact_type} />
              </div>
              <p>{artifact.summary ?? artifact.file_path ?? "No summary"}</p>
            </div>
          ))
        ) : (
          <div className="empty-chat">No artifacts linked to this workflow yet.</div>
        )}
      </aside>
    </div>
  );
}

function WorkflowObservabilityPage({ settings, targetWorkflowRunId, language }: { settings: AdminSettings; targetWorkflowRunId?: string; language: UiLanguage }) {
  const t = useCallback((key: UiTextKey) => textFor(language, key), [language]);
  const [runs, setRuns] = useState<AsyncState<WorkflowRun[]>>(emptyState());
  const [selectedRun, setSelectedRun] = useState<WorkflowRun | null>(null);
  const [traces, setTraces] = useState<WorkflowExecutionTrace[]>([]);
  const [diagnostics, setDiagnostics] = useState<WorkflowRuntimeDiagnostic[]>([]);
  const [analytics, setAnalytics] = useState<JsonRecord | null>(null);
  const [summary, setSummary] = useState<JsonRecord | null>(null);
  const [replaySessions, setReplaySessions] = useState<WorkflowReplaySession[]>([]);
  const [actionError, setActionError] = useState<string | null>(null);
  const [traceView, setTraceView] = useState<"all" | "attention" | "approval" | "replay">("all");

  const load = useCallback(async () => {
    setRuns((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await workflowClient.listRuns(settings, { status: undefined });
      const rows = response.items ?? [];
      setRuns({ data: rows, error: null, loading: false, updatedAt: nowLabel() });
      if (!selectedRun && rows.length > 0) {
        setSelectedRun(rows[0]);
      }
    } catch (error) {
      setRuns({
        data: null,
        error: error instanceof Error ? error.message : "Workflow observability API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [selectedRun, settings]);

  const loadObservability = useCallback(
    async (workflow: WorkflowRun | null) => {
      if (!workflow) {
        return;
      }
      setActionError(null);
      try {
        const [traceList, diagnosticList, analyticsResult, runtimeSummary, replayList] = await Promise.all([
          workflowClient.listTraces(workflow.id, settings),
          workflowClient.listDiagnostics(workflow.id, settings),
          workflowClient.getAnalytics(workflow.id, settings),
          workflowClient.getRuntimeSummary(workflow.id, settings),
          workflowClient.listReplaySessions(settings, workflow.id),
        ]);
        setTraces(traceList.items ?? []);
        setDiagnostics(diagnosticList.items ?? []);
        setAnalytics(analyticsResult.analytics ?? {});
        setSummary(runtimeSummary.summary ?? {});
        setReplaySessions(replayList.items ?? []);
      } catch (error) {
        setTraces([]);
        setDiagnostics([]);
        setAnalytics(null);
        setSummary(null);
        setReplaySessions([]);
        setActionError(error instanceof Error ? error.message : "Replay Center detail unavailable");
      }
    },
    [settings],
  );

  const createReplaySession = async () => {
    if (!selectedRun) {
      return;
    }
    setActionError(null);
    try {
      await workflowClient.createReplaySession(selectedRun.id, settings, "metadata_only");
      await loadObservability(selectedRun);
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Replay session creation failed");
    }
  };

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!targetWorkflowRunId || selectedRun?.id === targetWorkflowRunId) {
      return;
    }
    const listedRun = runs.data?.find((run) => run.id === targetWorkflowRunId);
    if (listedRun) {
      setSelectedRun(listedRun);
      return;
    }
    void workflowClient
      .getRun(targetWorkflowRunId, settings)
      .then(setSelectedRun)
      .catch((error) => {
        setActionError(error instanceof Error ? error.message : "Linked workflow observability unavailable");
      });
  }, [runs.data, selectedRun?.id, settings, targetWorkflowRunId]);

  useEffect(() => {
    void loadObservability(selectedRun);
  }, [loadObservability, selectedRun]);

  const traceFailureCount = traces.filter((trace) => isProblemStatus(trace.status) || /failed|error|timeout/i.test(trace.event_type)).length;
  const fallbackTraceCount = traces.filter((trace) => trace.fallback_triggered || /fallback/i.test(trace.event_type)).length;
  const retryTraceCount = traces.reduce((total, trace) => total + Number(trace.retry_count || 0), 0);
  const approvalWaitCount = traces.filter((trace) => /approval/i.test(trace.event_type)).length;
  const diagnosticProblemCount = diagnostics.filter((diagnostic) => /critical|error|warning|failed/i.test(diagnostic.severity)).length;
  const selectedRunNeedsAttention = isProblemStatus(selectedRun?.status) || traceFailureCount > 0 || diagnosticProblemCount > 0;
  const visibleTraces = traces.filter((trace) => {
    if (traceView === "all") {
      return true;
    }
    if (traceView === "approval") {
      return /approval/i.test(trace.event_type);
    }
    if (traceView === "replay") {
      return /replay/i.test(trace.event_type);
    }
    return isProblemStatus(trace.status) || /failed|error|timeout|fallback|retry/i.test(trace.event_type) || trace.fallback_triggered || Number(trace.retry_count || 0) > 0;
  });

  return (
    <div className="page-stack">
      <section className="workflow-observability-command-center">
        <div>
          <p className="section-eyebrow">{settings.aiServerUrl}</p>
          <h2>{t("workflowObsConsoleTitle")}</h2>
          <p>{t("workflowObsConsoleDescription")}</p>
          <p>{t("workflowObsOperatorSummary")}</p>
        </div>
        <div className="workflow-observability-flow-grid">
          <span>{t("workflowObsSelectStep")}</span>
          <span>{t("workflowObsSummaryStep")}</span>
          <span>{t("workflowObsDiagnosticsStep")}</span>
          <span>{t("workflowObsReplayStep")}</span>
        </div>
      </section>

      <div className="metrics-grid workflow-observability-metrics">
        <DataCard
          title={t("workflowObsSelectedRunMetric")}
          value={selectedRun?.status ? <StatusPill value={selectedRun.status} /> : "-"}
          detail={`${t("workflowObsCurrentNode")}: ${selectedRun?.current_node_key ?? "-"}`}
          icon={<Activity size={20} />}
          warning={selectedRunNeedsAttention}
        />
        <DataCard
          title={t("workflowObsTraceMetric")}
          value={String(traces.length)}
          detail={`${t("workflowObsFailures")}: ${traceFailureCount} / retry: ${retryTraceCount}`}
          icon={<GitBranch size={20} />}
          warning={traceFailureCount > 0 || retryTraceCount > 0}
        />
        <DataCard
          title={t("workflowObsDiagnosticsMetric")}
          value={String(diagnostics.length)}
          detail={`${t("workflowObsProblems")}: ${diagnosticProblemCount}`}
          icon={<AlertTriangle size={20} />}
          warning={diagnosticProblemCount > 0}
        />
        <DataCard
          title={t("workflowObsReplayMetric")}
          value={String(replaySessions.length)}
          detail={`${t("workflowObsMetadataOnly")}: ${replaySessions.filter((session) => session.replay_mode === "metadata_only").length}`}
          icon={<History size={20} />}
        />
      </div>

      <div className="split-page">
        <Panel
          title={t("workflowObsPanelTitle")}
          description={t("workflowObsPanelDescription")}
          action={<RefreshButton onClick={load} />}
        >
          <LoadNotice state={runs} />
          {targetWorkflowRunId ? (
            <div className="summary-strip">
              <span>{t("workflowObsReplayContext")}</span>
              <span>workflow_run_id: {targetWorkflowRunId}</span>
            </div>
          ) : null}
          <Table
            rows={(runs.data || []) as unknown as JsonRecord[]}
            selectedId={selectedRun?.id ?? null}
            onSelect={(row) => setSelectedRun(row as unknown as WorkflowRun)}
            emptyLabel={t("workflowObsNoRuns")}
            columns={[
              { key: "id", label: t("workflowObsRunIdColumn") },
              { key: "source_type", label: t("workflowObsSourceColumn") },
              { key: "status", label: t("workflowObsStatusColumn") },
              { key: "current_node_key", label: t("workflowObsCurrentNode") },
              { key: "planned_next_nodes", label: t("workflowObsNextColumn") },
              { key: "updated_at", label: t("workflowObsUpdatedColumn") },
            ]}
          />
        </Panel>
        <aside className="detail-panel">
          <div className="detail-title">
            <h2>{t("workflowObsDetailTitle")}</h2>
            <button className="primary-button" onClick={() => void createReplaySession()} disabled={!selectedRun}>
              <History size={15} />
              {t("workflowObsCreateReplayAction")}
            </button>
          </div>
          {actionError ? <div className="notice notice-error">{actionError}</div> : null}
          <p className="foundation-note">{t("workflowObsBoundaryNote")}</p>
          <h3>{t("workflowObsRuntimeSummaryTitle")}</h3>
          <JsonPreview value={summary || { status: "select a workflow run" }} />
          <h3>{t("workflowObsAnalyticsTitle")}</h3>
          <div className="metrics-grid compact">
            <DataCard title={t("workflowObsFallbacksMetric")} value={String(analytics?.fallback_frequency ?? fallbackTraceCount)} icon={<GitBranch size={20} />} warning={fallbackTraceCount > 0} />
            <DataCard title={t("workflowObsApprovalsMetric")} value={String(analytics?.approval_wait_frequency ?? approvalWaitCount)} icon={<ShieldCheck size={20} />} warning={approvalWaitCount > 0} />
            <DataCard title={t("workflowObsReplaysMetric")} value={String(analytics?.replay_frequency ?? replaySessions.length)} icon={<History size={20} />} />
          </div>
          <JsonPreview value={analytics || { status: "unavailable" }} />
          <div className="workflow-trace-toolbar">
            <h3>{t("workflowObsTraceTimelineTitle")}</h3>
            <label>
              {t("workflowObsTraceView")}
              <select value={traceView} onChange={(event) => setTraceView(event.target.value as "all" | "attention" | "approval" | "replay")}>
                <option value="all">{t("workflowObsTraceViewAll")}</option>
                <option value="attention">{t("workflowObsTraceViewAttention")}</option>
                <option value="approval">{t("workflowObsTraceViewApproval")}</option>
                <option value="replay">{t("workflowObsTraceViewReplay")}</option>
              </select>
            </label>
            <span>{visibleTraces.length}/{traces.length}</span>
          </div>
          <Timeline rows={visibleTraces as unknown as JsonRecord[]} primary="event_type" secondary="node_key" />
          <h3>{t("workflowObsNodeInspectionTitle")}</h3>
          <JsonPreview value={(visibleTraces[0] as unknown as JsonRecord) || (traces[0] as unknown as JsonRecord) || { status: "no traces" }} />
          <h3>{t("workflowObsDiagnosticsTitle")}</h3>
          <Timeline rows={diagnostics as unknown as JsonRecord[]} primary="diagnostic_type" secondary="summary" />
          <h3>{t("workflowObsReplaySessionsTitle")}</h3>
          <Timeline rows={replaySessions as unknown as JsonRecord[]} primary="replay_mode" secondary="replay_status" />
        </aside>
      </div>
    </div>
  );
}

function WorkflowGraphsPage({ settings }: { settings: AdminSettings }) {
  const [graphs, setGraphs] = useState<AsyncState<WorkflowGraph[]>>(emptyState());
  const [selectedGraph, setSelectedGraph] = useState<WorkflowGraph | null>(null);
  const [planner, setPlanner] = useState<WorkflowPlannerResult | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setGraphs((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await workflowClient.listGraphs(settings);
      setGraphs({ data: response.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setGraphs({
        data: null,
        error: error instanceof Error ? error.message : "Workflow Graphs API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings]);

  const loadGraph = async (graph: WorkflowGraph) => {
    setSelectedGraph(graph);
    setActionError(null);
    try {
      const result = await workflowClient.validateGraph(graph.id, settings);
      setPlanner(result);
    } catch (error) {
      setPlanner(null);
      setActionError(error instanceof Error ? error.message : "Graph validation unavailable");
    }
  };

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="split-page">
      <Panel
        title="Workflow Graphs"
        description="Workflow Graph Runtime with conditional routing, retry/fallback paths, and replay foundation. This is not a visual DAG builder or distributed orchestration engine."
        action={<RefreshButton onClick={load} />}
      >
        <LoadNotice state={graphs} />
        <Table
          rows={(graphs.data || []) as unknown as JsonRecord[]}
          selectedId={selectedGraph?.id ?? null}
          onSelect={(row) => void loadGraph(row as unknown as WorkflowGraph)}
          emptyLabel="No workflow graphs."
          columns={[
            { key: "id", label: "workflow_graph_id" },
            { key: "name", label: "name" },
            { key: "version", label: "version" },
            { key: "entry_node", label: "entry_node" },
            { key: "updated_at", label: "updated_at" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <h2>Graph Planner</h2>
        {actionError ? <div className="notice notice-error">{actionError}</div> : null}
        <JsonPreview value={planner || { status: "select a workflow graph" }} />
        <h3>Node list</h3>
        <Timeline rows={(selectedGraph?.nodes || []) as unknown as JsonRecord[]} primary="node_key" secondary="node_type" />
        <h3>Edge list</h3>
        <Timeline rows={(selectedGraph?.edges || []) as unknown as JsonRecord[]} primary="source_node_key" secondary="edge_type" />
        <h3>Dependency visualization</h3>
        <JsonPreview
          value={{
            dependency_state: planner?.dependency_state ?? {},
            conditional_routing_result: planner?.condition_results ?? [],
            retry_path: planner?.retry_paths ?? [],
            fallback_path: planner?.fallback_paths ?? [],
          }}
        />
      </aside>
    </div>
  );
}

function WorkflowTemplatesPage({ settings }: { settings: AdminSettings }) {
  const [templates, setTemplates] = useState<AsyncState<WorkflowTemplate[]>>(emptyState());
  const [runs, setRuns] = useState<AsyncState<WorkflowTemplateRun[]>>(emptyState());
  const [selectedTemplate, setSelectedTemplate] = useState<WorkflowTemplate | null>(null);
  const [compatibility, setCompatibility] = useState<WorkflowTemplateCompatibility | null>(null);
  const [exportPayload, setExportPayload] = useState<JsonRecord | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setTemplates((current) => ({ ...current, loading: true, error: null }));
    setRuns((current) => ({ ...current, loading: true, error: null }));
    try {
      const [templateResponse, runResponse] = await Promise.all([
        workflowTemplateClient.listTemplates(settings),
        workflowTemplateClient.listRuns(settings),
      ]);
      setTemplates({ data: templateResponse.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
      setRuns({ data: runResponse.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Workflow Template Registry API unavailable";
      setTemplates({ data: null, error: message, loading: false, updatedAt: nowLabel() });
      setRuns({ data: null, error: message, loading: false, updatedAt: nowLabel() });
    }
  }, [settings]);

  const inspectTemplate = async (template: WorkflowTemplate) => {
    setSelectedTemplate(template);
    setActionError(null);
    try {
      const result = await workflowTemplateClient.validateTemplate(template.id, settings);
      setCompatibility(result);
    } catch (error) {
      setCompatibility(null);
      setActionError(error instanceof Error ? error.message : "Compatibility check unavailable");
    }
  };

  const exportTemplate = async () => {
    if (!selectedTemplate) return;
    setActionError(null);
    try {
      setExportPayload(await workflowTemplateClient.exportTemplate(selectedTemplate.id, settings));
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Template export failed");
    }
  };

  const importDryRun = async () => {
    if (!exportPayload) return;
    setActionError(null);
    try {
      const imported = await workflowTemplateClient.importTemplateDryRun(
        { ...exportPayload, template_key: `${exportPayload.template_key ?? "template"}_dry_run` },
        settings,
      );
      setExportPayload({ ...exportPayload, import_dry_run_result: imported });
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Template import dry-run failed");
    }
  };

  const runTemplate = async () => {
    if (!selectedTemplate) return;
    setActionError(null);
    try {
      await workflowTemplateClient.runTemplate(selectedTemplate.id, settings, {
        url: "https://example.com",
        topic: "AI automation operations",
      });
      await load();
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Template run failed");
    }
  };

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="split-page">
      <Panel
        title="Template Library"
        description="Workflow Template Registry with versioning, built-in templates, import/export JSON, compatibility checks, and template runs. This is not a visual DAG builder and does not connect ComfyUI."
        action={<RefreshButton onClick={load} />}
      >
        <LoadNotice state={templates} />
        <Table
          rows={(templates.data || []) as unknown as JsonRecord[]}
          selectedId={selectedTemplate?.id ?? null}
          onSelect={(row) => void inspectTemplate(row as unknown as WorkflowTemplate)}
          emptyLabel="No workflow templates."
          columns={[
            { key: "template_key", label: "template_key" },
            { key: "name", label: "name" },
            { key: "category", label: "category" },
            { key: "status", label: "status" },
            { key: "current_version", label: "current_version" },
            { key: "risk_level", label: "risk_level" },
            { key: "verified", label: "verified" },
            { key: "featured", label: "featured" },
            { key: "recommended", label: "recommended" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <h2>Template Detail</h2>
        {actionError ? <div className="notice notice-error">{actionError}</div> : null}
        <div className="actions-row">
          <button className="ghost-button" disabled={!selectedTemplate} onClick={() => void exportTemplate()}>Export JSON</button>
          <button className="ghost-button" disabled={!exportPayload} onClick={() => void importDryRun()}>Import dry-run</button>
          <button className="primary-button" disabled={!selectedTemplate} onClick={() => void runTemplate()}>Run template</button>
        </div>
        <JsonPreview value={selectedTemplate || { status: "select a workflow template" }} />
        <h3>Governance badges</h3>
        <JsonPreview
          value={
            selectedTemplate
              ? {
                  status: selectedTemplate.status,
                  risk_level: selectedTemplate.risk_level,
                  verified: selectedTemplate.verified,
                  featured: selectedTemplate.featured,
                  recommended: selectedTemplate.recommended,
                  usage_count: selectedTemplate.usage_count,
                  success_rate: selectedTemplate.success_rate,
                  average_runtime_ms: selectedTemplate.average_runtime_ms,
                  average_step_count: selectedTemplate.average_step_count,
                }
              : { status: "select a workflow template" }
          }
        />
        <h3>Validation result</h3>
        <JsonPreview value={compatibility || { compatible: null, warnings: [], errors: [] }} />
        <h3>Version list</h3>
        <Timeline rows={(selectedTemplate?.versions || []) as unknown as JsonRecord[]} primary="version" secondary="validation_status" />
        <h3>Export / import JSON</h3>
        <JsonPreview value={exportPayload || { status: "export a template to inspect JSON" }} />
        <h3>Template runs</h3>
        <LoadNotice state={runs} />
        <Timeline rows={(runs.data || []) as unknown as JsonRecord[]} primary="id" secondary="status" />
      </aside>
    </div>
  );
}

function TemplateGovernancePage({ settings }: { settings: AdminSettings }) {
  const [reviews, setReviews] = useState<AsyncState<WorkflowTemplateReview[]>>(emptyState());
  const [marketplace, setMarketplace] = useState<AsyncState<WorkflowTemplateMarketplaceItem[]>>(emptyState());
  const [auditLogs, setAuditLogs] = useState<AsyncState<WorkflowTemplateAuditLog[]>>(emptyState());
  const [matrix, setMatrix] = useState<AsyncState<WorkflowTemplateCompatibilityMatrixRow[]>>(emptyState());
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  const [selectedVersionId, setSelectedVersionId] = useState("");
  const [actionError, setActionError] = useState<string | null>(null);

  const selectedTemplate = templates.find((template) => template.id === selectedTemplateId) ?? null;

  const load = useCallback(async () => {
    setReviews((current) => ({ ...current, loading: true, error: null }));
    setMarketplace((current) => ({ ...current, loading: true, error: null }));
    setAuditLogs((current) => ({ ...current, loading: true, error: null }));
    setMatrix((current) => ({ ...current, loading: true, error: null }));
    try {
      const [templateResponse, reviewResponse, marketplaceResponse, auditResponse, matrixResponse] = await Promise.all([
        workflowTemplateClient.listTemplates(settings),
        workflowTemplateClient.listReviews(settings),
        workflowTemplateClient.listMarketplace(settings),
        workflowTemplateClient.listAuditLogs(settings),
        workflowTemplateClient.listCompatibilityMatrix(settings),
      ]);
      setTemplates(templateResponse.items ?? []);
      setSelectedTemplateId((current) => current || templateResponse.items?.[0]?.id || "");
      setSelectedVersionId((current) => current || templateResponse.items?.[0]?.versions?.[0]?.id || "");
      setReviews({ data: reviewResponse.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
      setMarketplace({ data: marketplaceResponse.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
      setAuditLogs({ data: auditResponse.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
      setMatrix({ data: matrixResponse.items ?? [], error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Template Governance API unavailable";
      setReviews({ data: null, error: message, loading: false, updatedAt: nowLabel() });
      setMarketplace({ data: null, error: message, loading: false, updatedAt: nowLabel() });
      setAuditLogs({ data: null, error: message, loading: false, updatedAt: nowLabel() });
      setMatrix({ data: null, error: message, loading: false, updatedAt: nowLabel() });
    }
  }, [settings]);

  const mutate = async (operation: () => Promise<unknown>) => {
    setActionError(null);
    try {
      await operation();
      await load();
    } catch (error) {
      setActionError(error instanceof Error ? error.message : "Template governance action failed");
    }
  };

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    if (!selectedTemplate) {
      return;
    }
    setSelectedVersionId(selectedTemplate.versions?.[0]?.id || "");
  }, [selectedTemplateId, selectedTemplate]);

  return (
    <div className="split-page">
      <Panel
        title="Template Governance"
        description="Internal Workflow Template Marketplace foundation with review queue, lifecycle controls, audit trail, compatibility matrix, governance badges, and rollback. This is not a public marketplace and not a drag/drop workflow editor."
        action={<RefreshButton onClick={load} />}
      >
        {actionError ? <div className="notice notice-error">{actionError}</div> : null}
        <LoadNotice state={reviews} />
        <div className="actions-row">
          <select
            value={selectedTemplateId}
            onChange={(event) => setSelectedTemplateId(event.target.value)}
            aria-label="Template"
          >
            {templates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.template_key} | {template.status} | {template.risk_level}
              </option>
            ))}
          </select>
          <select
            value={selectedVersionId}
            onChange={(event) => setSelectedVersionId(event.target.value)}
            aria-label="Template version"
          >
            {(selectedTemplate?.versions || []).map((version) => (
              <option key={version.id} value={version.id}>
                {version.version} | {version.validation_status}
              </option>
            ))}
          </select>
        </div>
        <div className="actions-row">
          <button
            className="ghost-button"
            disabled={!selectedTemplateId || !selectedVersionId}
            onClick={() => void mutate(() => workflowTemplateClient.submitReview(selectedTemplateId, selectedVersionId, settings))}
          >
            Submit review
          </button>
          <button
            className="ghost-button"
            disabled={!selectedTemplateId || !selectedVersionId}
            onClick={() => void mutate(() => workflowTemplateClient.activateVersion(selectedTemplateId, selectedVersionId, settings))}
          >
            Activate approved
          </button>
          <button
            className="ghost-button"
            disabled={!selectedTemplateId || !selectedVersionId}
            onClick={() => void mutate(() => workflowTemplateClient.rollbackTemplate(selectedTemplateId, selectedVersionId, settings))}
          >
            Rollback
          </button>
          <button
            className="ghost-button"
            disabled={!selectedTemplateId}
            onClick={() => void mutate(() => workflowTemplateClient.deprecateTemplate(selectedTemplateId, settings))}
          >
            Deprecate
          </button>
          <button
            className="ghost-button"
            disabled={!selectedTemplateId}
            onClick={() => void mutate(() => workflowTemplateClient.archiveTemplate(selectedTemplateId, settings))}
          >
            Archive
          </button>
        </div>
        <h3>Review Queue</h3>
        <Table
          rows={(reviews.data || []) as unknown as JsonRecord[]}
          emptyLabel="No template reviews."
          columns={[
            { key: "review_status", label: "review_status" },
            { key: "template_id", label: "template_id" },
            { key: "template_version_id", label: "version_id" },
            { key: "reviewer_id", label: "reviewer" },
            { key: "created_at", label: "created_at" },
          ]}
        />
        <div className="actions-row">
          {(reviews.data || []).slice(0, 4).map((review) => (
            <span key={review.id} className="inline-actions">
              <button className="ghost-button" onClick={() => void mutate(() => workflowTemplateClient.approveReview(review.id, settings))}>Approve</button>
              <button className="ghost-button" onClick={() => void mutate(() => workflowTemplateClient.rejectReview(review.id, settings))}>Reject</button>
              <button className="ghost-button" onClick={() => void mutate(() => workflowTemplateClient.requestChanges(review.id, settings))}>Request changes</button>
            </span>
          ))}
        </div>
      </Panel>
      <aside className="detail-panel">
        <h2>Marketplace View</h2>
        <LoadNotice state={marketplace} />
        <Timeline
          rows={(marketplace.data || []).map((item) => ({
            template_key: item.template.template_key,
            governance_status: item.governance_status,
            badges: item.badges.join(", "),
            success_rate: item.metrics.success_rate,
            total_runs: item.metrics.total_runs,
          }))}
          primary="template_key"
          secondary="badges"
        />
        <h3>Compatibility Matrix</h3>
        <LoadNotice state={matrix} />
        <Table
          rows={(matrix.data || []) as unknown as JsonRecord[]}
          emptyLabel="No compatibility rows."
          columns={[
            { key: "runtime_capability", label: "runtime_capability" },
            { key: "supported", label: "supported" },
            { key: "notes", label: "notes" },
            { key: "template_version_id", label: "version_id" },
          ]}
        />
        <h3>Audit Log View</h3>
        <LoadNotice state={auditLogs} />
        <Timeline rows={(auditLogs.data || []) as unknown as JsonRecord[]} primary="action" secondary="actor_id" />
        <h3>Lifecycle View</h3>
        <JsonPreview
          value={
            selectedTemplate
              ? {
                  status: selectedTemplate.status,
                  current_version: selectedTemplate.current_version,
                  latest_version: selectedTemplate.latest_version,
                  featured: selectedTemplate.featured,
                  verified: selectedTemplate.verified,
                  recommended: selectedTemplate.recommended,
                  metrics: {
                    usage_count: selectedTemplate.usage_count,
                    success_rate: selectedTemplate.success_rate,
                    average_runtime_ms: selectedTemplate.average_runtime_ms,
                    average_step_count: selectedTemplate.average_step_count,
                  },
                }
              : { status: "select a template" }
          }
        />
      </aside>
    </div>
  );
}

function OpenClawPage({ settings }: { settings: AdminSettings }) {
  const [state, setState] = useState<AsyncState<JsonRecord>>(emptyState());

  const load = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const [health, capabilities] = await Promise.all([openclawApi.health(settings), openclawApi.capabilities(settings)]);
      setState({ data: { health, capabilities }, error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setState({
        data: null,
        error: error instanceof Error ? error.message : "OpenClaw API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <Panel
      title="OpenClaw"
      description="OpenClaw is currently a mock / placeholder adapter. No real OpenClaw or social platform automation is connected."
      action={<RefreshButton onClick={load} />}
    >
      <LoadNotice state={state} />
      <div className="metrics-grid compact">
        <DataCard title="Provider" value={valueAt(state.data?.health as JsonRecord, ["provider"], "mock")} icon={<Bot size={20} />} />
        <DataCard title="Mock status" value={valueAt(state.data?.health as JsonRecord, ["mock"], "true")} icon={<TerminalSquare size={20} />} />
      </div>
      <JsonPreview value={state.data || { status: "unavailable" }} />
    </Panel>
  );
}

function AuditLogsPage({ settings }: { settings: AdminSettings }) {
  const [filters, setFilters] = useState({ eventType: "", success: "", targetType: "" });
  const [logs, setLogs] = useState<AsyncState<JsonRecord[]>>(emptyState());

  const load = useCallback(async () => {
    setLogs((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await auditApi.list(
        {
          eventType: filters.eventType || undefined,
          success: filters.success || undefined,
          targetType: filters.targetType || undefined,
        },
        settings,
      );
      setLogs({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setLogs({
        data: null,
        error: error instanceof Error ? error.message : "Audit logs API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [filters, settings]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <Panel
      title="Audit Logs"
      description="Browser worker auth, UI access, policy blocks, and related browser security events."
      action={<RefreshButton onClick={load} />}
    >
      <div className="filter-row">
        <input placeholder="event_type" value={filters.eventType} onChange={(event) => setFilters({ ...filters, eventType: event.target.value })} />
        <select value={filters.success} onChange={(event) => setFilters({ ...filters, success: event.target.value })}>
          <option value="">success: any</option>
          <option value="true">success: true</option>
          <option value="false">success: false</option>
        </select>
        <input placeholder="target_type" value={filters.targetType} onChange={(event) => setFilters({ ...filters, targetType: event.target.value })} />
      </div>
      <LoadNotice state={logs} />
      <Table
        rows={logs.data || []}
        emptyLabel="No audit logs."
        columns={[
          { key: "event_type", label: "event_type" },
          { key: "actor_type", label: "actor_type" },
          { key: "target_type", label: "target_type" },
          { key: "target_id", label: "target_id" },
          { key: "success", label: "success" },
          { key: "error", label: "error" },
          { key: "created_at", label: "created_at" },
        ]}
      />
    </Panel>
  );
}

const commercialOperationCopy = {
  "zh-CN": {
    connection: "AI 服务",
    phaseLabel: "Phase 61R",
    title: "商业运营项目中心",
    description: "输入运营目标，保存为可追踪项目，并生成知识、内容、审批、执行和监控的保守计划草案。",
    summary: "当前只创建计划、审批、证据、内容草稿、素材请求、交付物、证据快照、执行请求、执行运行记录、商业结果、监控观察、优化决策和干运行记录；不会自动发布、不会控制真实账号、不会绕过审批。",
    flow: ["目标", "知识与素材", "内容草案", "人工审批", "安全执行", "结果复盘"],
    total: "项目",
    active: "进行中",
    attention: "高风险/需审",
    steps: "计划步骤",
    createTitle: "新建运营项目",
    createDescription: "适合录入一次营销活动、转化目标、内容生产目标或客户运营目标。",
    listTitle: "项目列表",
    detailTitle: "项目详情",
    detailDescription: "计划草案是可审阅的执行路线，不会触发 OpenClaw、ComfyUI、浏览器 Worker 或外部发布。",
    approvalsTitle: "审批门禁",
    approvalsDescription: "为计划步骤创建人工审批，只有审批记录通过后，后续阶段才允许把该步骤交给执行或干运行。",
    dryRunsTitle: "安全干运行",
    dryRunsDescription: "基于已批准审批创建 metadata-only 干运行记录，用于检查输入、目标、预期输出和交接结果，不触发外部动作。",
    linksTitle: "证据与交接",
    linksDescription: "把需求沟通、内容产物、任务运行、工作流、RAG 文档、审批记录或外部素材挂到当前项目，便于后续人员接手。",
    titleLabel: "项目名称",
    objectiveLabel: "运营目标",
    audienceLabel: "目标人群",
    channelsLabel: "渠道",
    metricsLabel: "成功指标",
    collectionLabel: "知识集合",
    priorityLabel: "优先级",
    riskLabel: "风险等级",
    budgetLabel: "预算",
    currencyLabel: "币种",
    constraintsLabel: "约束",
    approvalStepLabel: "计划步骤",
    dryRunApprovalLabel: "已批准审批",
    executionModeLabel: "执行模式",
    executionTargetLabel: "执行目标",
    inputSummaryLabel: "输入摘要",
    expectedOutputsLabel: "预期输出",
    readinessChecksLabel: "检查项",
    requestedActionLabel: "审批事项",
    linkTypeLabel: "关联类型",
    targetTypeLabel: "目标对象",
    targetIdLabel: "目标 ID",
    sourceNameLabel: "来源",
    linkSummaryLabel: "说明",
    createAction: "创建项目",
    requestApprovalAction: "创建审批",
    createDryRunAction: "创建干运行",
    completeDryRunAction: "完成",
    failDryRunAction: "失败",
    approveAction: "批准",
    rejectAction: "驳回",
    cancelAction: "取消",
    createLinkAction: "添加关联",
    deleteLinkAction: "移除",
    planAction: "重新生成计划",
    markReady: "标记就绪",
    activate: "启动跟踪",
    pause: "暂停",
    noOperations: "暂无商业运营项目。",
    noApprovals: "暂无审批记录。",
    noDryRuns: "暂无干运行记录。",
    noLinks: "暂无证据或交接关联。",
    noPlan: "还没有计划草案。",
    actionResult: "操作结果",
    selectedHint: "从项目列表选择一行查看计划。",
    approvalsSelectedHint: "先选择一个项目，再为计划步骤创建审批。",
    dryRunsSelectedHint: "先选择一个项目，并批准至少一个审批记录，再创建干运行。",
    dryRunRequiresApproval: "需要先批准一个审批记录。",
    linksSelectedHint: "先选择一个项目，再添加证据或交接关联。",
    planTitle: "计划草案",
    statusColumn: "状态",
    priorityColumn: "优先级",
    riskColumn: "风险",
    updatedColumn: "更新",
    objectivePlaceholder: "例如：在 30 天内提升某产品线有效询盘，并形成可复用内容资产。",
  },
  "en-US": {
    connection: "AI Server",
    phaseLabel: "Phase 61R",
    title: "Commercial operations center",
    description: "Capture a business goal as a trackable operation and draft the knowledge, content, approval, execution, and monitoring path.",
    summary: "This creates plans, approvals, evidence links, content drafts, asset requests, deliverables, evidence snapshots, execution requests, execution run records, results, monitoring observations, and dry-run records only. It does not publish, control real accounts, ingest platform analytics, or bypass approval.",
    flow: ["Goal", "Knowledge", "Drafts", "Approval", "Safe run", "Monitor"],
    total: "Operations",
    active: "In motion",
    attention: "High risk/review",
    steps: "Plan steps",
    createTitle: "Create operation",
    createDescription: "Use this for a campaign, conversion goal, content objective, or customer operation target.",
    listTitle: "Operation list",
    detailTitle: "Operation detail",
    detailDescription: "The plan outline is reviewable. It does not trigger OpenClaw, ComfyUI, Browser Worker, or external publishing.",
    approvalsTitle: "Approval gates",
    approvalsDescription: "Create human approvals for plan steps before later phases can hand them to execution or dry-run surfaces.",
    dryRunsTitle: "Safe dry-runs",
    dryRunsDescription: "Create metadata-only dry-run records from approved approvals to review inputs, targets, expected outputs, and handoff results without external actions.",
    linksTitle: "Evidence and handoff",
    linksDescription: "Attach intake notes, content artifacts, task runs, workflow runs, RAG documents, approvals, or external materials to the selected operation.",
    titleLabel: "Title",
    objectiveLabel: "Objective",
    audienceLabel: "Audience",
    channelsLabel: "Channels",
    metricsLabel: "Success metrics",
    collectionLabel: "Knowledge collection",
    priorityLabel: "Priority",
    riskLabel: "Risk",
    budgetLabel: "Budget",
    currencyLabel: "Currency",
    constraintsLabel: "Constraints",
    approvalStepLabel: "Plan step",
    dryRunApprovalLabel: "Approved approval",
    executionModeLabel: "Execution mode",
    executionTargetLabel: "Execution target",
    inputSummaryLabel: "Input summary",
    expectedOutputsLabel: "Expected outputs",
    readinessChecksLabel: "Readiness checks",
    requestedActionLabel: "Requested action",
    linkTypeLabel: "Link type",
    targetTypeLabel: "Target object",
    targetIdLabel: "Target ID",
    sourceNameLabel: "Source",
    linkSummaryLabel: "Summary",
    createAction: "Create operation",
    requestApprovalAction: "Create approval",
    createDryRunAction: "Create dry-run",
    completeDryRunAction: "Complete",
    failDryRunAction: "Fail",
    approveAction: "Approve",
    rejectAction: "Reject",
    cancelAction: "Cancel",
    createLinkAction: "Add link",
    deleteLinkAction: "Remove",
    planAction: "Regenerate plan",
    markReady: "Mark ready",
    activate: "Start tracking",
    pause: "Pause",
    noOperations: "No commercial operations yet.",
    noApprovals: "No approval gates yet.",
    noDryRuns: "No dry-runs yet.",
    noLinks: "No evidence or handoff links yet.",
    noPlan: "No plan outline yet.",
    actionResult: "Action result",
    selectedHint: "Select one row from the operation list to inspect the plan.",
    approvalsSelectedHint: "Select an operation before creating plan-step approvals.",
    dryRunsSelectedHint: "Select an operation and approve at least one gate before creating a dry-run.",
    dryRunRequiresApproval: "Approve one approval gate first.",
    linksSelectedHint: "Select an operation before adding evidence or handoff links.",
    planTitle: "Plan outline",
    statusColumn: "status",
    priorityColumn: "priority",
    riskColumn: "risk",
    updatedColumn: "updated",
    objectivePlaceholder: "Example: increase qualified leads for one product line in 30 days and create reusable content assets.",
  },
} as const;

function splitDraftList(value: string): string[] {
  return value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function draftListText(value: unknown): string {
  if (Array.isArray(value)) {
    return value
      .map((item) => {
        if (typeof item === "string") {
          return item;
        }
        if (item && typeof item === "object") {
          return valueAt(item as JsonRecord, ["step", "item", "title", "asset", "name"], "");
        }
        return "";
      })
      .map((item) => item.trim())
      .filter(Boolean)
      .join(", ");
  }
  return typeof value === "string" ? value : "";
}

function metricDraftList(value: string): JsonRecord[] {
  return splitDraftList(value).map((item) => {
    const separatorIndex = item.indexOf("=");
    const name = (separatorIndex >= 0 ? item.slice(0, separatorIndex) : item).trim();
    const metricValue = separatorIndex >= 0 ? item.slice(separatorIndex + 1).trim() : "";
    return {
      name,
      value: metricValue || undefined,
      source: "operator_observed",
    };
  });
}

function metricDraftText(value: unknown): string {
  if (!Array.isArray(value)) {
    return "";
  }
  return value
    .map((item) => {
      if (!item || typeof item !== "object") {
        return "";
      }
      const record = item as JsonRecord;
      const name = valueAt(record, ["name", "metric", "key"], "");
      const metricValue = valueAt(record, ["value"], "");
      return metricValue ? `${name}=${metricValue}` : name;
    })
    .map((item) => item.trim())
    .filter(Boolean)
    .join("\n");
}

function parseJsonRecordDraft(value: string): JsonRecord {
  if (!value.trim()) {
    return {};
  }
  const parsed = JSON.parse(value) as unknown;
  if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
    throw new Error("JSON input must be an object");
  }
  return parsed as JsonRecord;
}

function parseJsonArrayDraft(value: string): JsonRecord[] {
  if (!value.trim()) {
    return [];
  }
  const parsed = JSON.parse(value) as unknown;
  if (!Array.isArray(parsed)) {
    throw new Error("JSON input must be an array");
  }
  return parsed.filter((item): item is JsonRecord => Boolean(item) && typeof item === "object" && !Array.isArray(item));
}

function CommercialOperationsPage({ settings, language }: { settings: AdminSettings; language: UiLanguage }) {
  const copy = commercialOperationCopy[language];
  const contentCopy =
    language === "zh-CN"
      ? {
          title: "内容草稿",
          description: "为选中的计划步骤创建可审阅的渠道草稿和素材占位需求，只记录内容与审批状态，不发布、不启动 ComfyUI。",
          stepLabel: "计划步骤",
          channelLabel: "渠道",
          formatLabel: "内容格式",
          audienceLabel: "受众细分",
          bodyLabel: "正文草稿",
          summaryLabel: "摘要",
          ctaLabel: "行动引导",
          sourceMaterialsLabel: "素材/知识来源",
          queryLabel: "RAG 检索问题",
          searchModeLabel: "检索模式",
          assetRequestsLabel: "素材占位需求",
          generateAction: "从 RAG 生成草稿",
          createAction: "创建草稿",
          saveAction: "保存草稿",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          archiveAction: "归档",
          selectedHint: "先选择一个项目，再创建内容草稿。",
          noDrafts: "暂无内容草稿。",
        }
      : {
          title: "Content drafts",
          description: "Create reviewable channel drafts and asset placeholders for the selected plan step. This records content and approval state only; it does not publish or start ComfyUI.",
          stepLabel: "Plan step",
          channelLabel: "Channel",
          formatLabel: "Format",
          audienceLabel: "Audience segment",
          bodyLabel: "Draft body",
          summaryLabel: "Summary",
          ctaLabel: "Call to action",
          sourceMaterialsLabel: "Sources",
          queryLabel: "RAG query",
          searchModeLabel: "Search mode",
          assetRequestsLabel: "Asset placeholders",
          generateAction: "Generate draft from RAG",
          createAction: "Create draft",
          saveAction: "Save draft",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          archiveAction: "Archive",
          selectedHint: "Select an operation before creating content drafts.",
          noDrafts: "No content drafts yet.",
        };
  const assetCopy =
    language === "zh-CN"
      ? {
          title: "素材请求",
          description: "把图片、封面、视频、设计稿等素材需求登记为可审批、可准备、可恢复的记录；当前只做交接准备，不启动 ComfyUI。",
          sourceDraftLabel: "来源草稿",
          typeLabel: "素材类型",
          purposeLabel: "用途",
          dimensionsLabel: "尺寸/格式",
          styleLabel: "风格约束",
          promptLabel: "生成提示",
          negativePromptLabel: "排除项",
          queryLabel: "RAG 检索问题",
          searchModeLabel: "检索模式",
          readinessLabel: "检查项",
          generateAction: "从 RAG 生成素材请求",
          createAction: "创建请求",
          saveAction: "保存请求",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          prepareAction: "准备",
          failAction: "失败",
          archiveAction: "归档",
          selectedHint: "先选择一个项目，再创建素材请求。",
          noRequests: "暂无素材请求。",
        }
      : {
          title: "Asset requests",
          description: "Register image, cover, video, or design needs as reviewable and recoverable records. This prepares handoff only; it does not start ComfyUI.",
          sourceDraftLabel: "Source draft",
          typeLabel: "Asset type",
          purposeLabel: "Purpose",
          dimensionsLabel: "Size / format",
          styleLabel: "Style constraints",
          promptLabel: "Generation prompt",
          negativePromptLabel: "Negative prompt",
          queryLabel: "RAG query",
          searchModeLabel: "Search mode",
          readinessLabel: "Readiness checks",
          generateAction: "Generate request from RAG",
          createAction: "Create request",
          saveAction: "Save request",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          prepareAction: "Prepare",
          failAction: "Fail",
          archiveAction: "Archive",
          selectedHint: "Select an operation before creating asset requests.",
          noRequests: "No asset requests yet.",
        };
  const comfyuiCopy =
    language === "zh-CN"
      ? {
          title: "ComfyUI 交接",
          description: "把已批准或已准备的素材请求转成可审计的 ComfyUI 交接记录。当前只保存提示词、workflow payload、检查项和审批状态，不提交真实生成任务。",
          assetLabel: "素材请求",
          workflowLabel: "Workflow 名称",
          promptPayloadLabel: "Prompt payload JSON",
          workflowPayloadLabel: "Workflow payload JSON",
          readinessLabel: "交接检查项",
          createAction: "创建交接",
          saveAction: "保存交接",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          prepareAction: "准备",
          failAction: "失败",
          archiveAction: "归档",
          selectedHint: "先选择一个项目，并批准或准备至少一个素材请求。",
          requiresAsset: "先批准或准备一个素材请求。",
          noHandoffs: "暂无 ComfyUI 交接记录。",
        }
      : {
          title: "ComfyUI handoffs",
          description: "Turn approved or prepared asset requests into auditable ComfyUI handoff records. This stores prompts, workflow payloads, checks, and approval state only; no generation job is submitted.",
          assetLabel: "Asset request",
          workflowLabel: "Workflow name",
          promptPayloadLabel: "Prompt payload JSON",
          workflowPayloadLabel: "Workflow payload JSON",
          readinessLabel: "Handoff checks",
          createAction: "Create handoff",
          saveAction: "Save handoff",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          prepareAction: "Prepare",
          failAction: "Fail",
          archiveAction: "Archive",
          selectedHint: "Select an operation and approve or prepare at least one asset request first.",
          requiresAsset: "Approve or prepare one asset request first.",
          noHandoffs: "No ComfyUI handoffs yet.",
        };
  const comfyuiPreflightCopy =
    language === "zh-CN"
      ? {
          title: "ComfyUI 连接预检",
          description: "记录未来 ComfyUI 适配器的地址、队列、模型和 workflow 准备情况；当前只做本地配置检查，不请求 ComfyUI、不提交队列。",
          handoffLabel: "ComfyUI 交接",
          targetLabel: "目标地址",
          queueLabel: "队列名称",
          workflowLabel: "Workflow 名称",
          modelRefsLabel: "模型/Checkpoint",
          adapterConfigLabel: "Adapter config JSON",
          checkItemsLabel: "人工检查 JSON",
          createAction: "创建预检",
          saveAction: "保存并检查",
          checkAction: "重新检查",
          editAction: "编辑",
          failAction: "标记失败",
          archiveAction: "归档",
          selectedHint: "先选择项目，并批准或准备至少一个 ComfyUI 交接。",
          requiresHandoff: "先批准或准备一个 ComfyUI 交接。",
          noPreflights: "暂无 ComfyUI 预检记录。",
        }
      : {
          title: "ComfyUI preflights",
          description: "Record future ComfyUI adapter endpoint, queue, model, and workflow readiness. This performs local configuration checks only; it does not call ComfyUI or submit a queue job.",
          handoffLabel: "ComfyUI handoff",
          targetLabel: "Target URL",
          queueLabel: "Queue name",
          workflowLabel: "Workflow name",
          modelRefsLabel: "Models / checkpoints",
          adapterConfigLabel: "Adapter config JSON",
          checkItemsLabel: "Operator checks JSON",
          createAction: "Create preflight",
          saveAction: "Save and check",
          checkAction: "Check again",
          editAction: "Edit",
          failAction: "Fail",
          archiveAction: "Archive",
          selectedHint: "Select an operation and approve or prepare one ComfyUI handoff first.",
          requiresHandoff: "Approve or prepare one ComfyUI handoff first.",
          noPreflights: "No ComfyUI preflights yet.",
        };
  const comfyuiAdapterCopy =
    language === "zh-CN"
      ? {
          title: "ComfyUI 适配器配置",
          description: "给服务器维护人员登记未来受控适配器的地址、队列、workflow 白名单、模型清单和维护备注。这里只做本地元数据校验，不请求 ComfyUI，不提交队列。",
          targetLabel: "目标地址",
          authModeLabel: "认证模式",
          secretRefLabel: "密钥引用",
          queueLabel: "队列名称",
          workflowLabel: "默认 workflow",
          allowedWorkflowsLabel: "允许 workflow",
          modelInventoryLabel: "模型清单 JSON",
          runtimeLimitsLabel: "运行边界 JSON",
          notesLabel: "维护备注",
          checksLabel: "人工检查 JSON",
          createAction: "创建配置",
          saveAction: "保存并校验",
          validateAction: "重新校验",
          editAction: "编辑",
          failAction: "标记失败",
          archiveAction: "归档",
          selectedHint: "先选择项目，再创建 ComfyUI 适配器配置。",
          noConfigs: "暂无 ComfyUI 适配器配置。",
        }
      : {
          title: "ComfyUI adapter configs",
          description: "Maintain future guarded adapter endpoint, queue, workflow allowlist, model inventory, and notes. This performs local metadata validation only; it does not call ComfyUI or submit a queue job.",
          targetLabel: "Target URL",
          authModeLabel: "Auth mode",
          secretRefLabel: "Secret ref",
          queueLabel: "Queue name",
          workflowLabel: "Default workflow",
          allowedWorkflowsLabel: "Allowed workflows",
          modelInventoryLabel: "Model inventory JSON",
          runtimeLimitsLabel: "Runtime limits JSON",
          notesLabel: "Maintenance notes",
          checksLabel: "Operator checks JSON",
          createAction: "Create config",
          saveAction: "Save and validate",
          validateAction: "Validate again",
          editAction: "Edit",
          failAction: "Fail",
          archiveAction: "Archive",
          selectedHint: "Select an operation before creating ComfyUI adapter configs.",
          noConfigs: "No ComfyUI adapter configs yet.",
        };
  const comfyuiJobCopy =
    language === "zh-CN"
      ? {
          title: "ComfyUI 任务请求",
          description: "把已检查的 ComfyUI 预检整理成可审批的未来任务请求。这里只生成队列请求元数据、检查项和恢复建议，不调用 ComfyUI，也不提交队列。",
          preflightLabel: "已检查预检",
          priorityLabel: "优先级",
          runtimePayloadLabel: "运行边界 JSON",
          safetyChecksLabel: "安全检查 JSON",
          outputsLabel: "预期输出",
          recoveryLabel: "恢复计划 JSON",
          createAction: "创建任务请求",
          saveAction: "保存任务请求",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          queueAction: "标记排队",
          failAction: "失败",
          cancelAction: "取消",
          archiveAction: "归档",
          selectedHint: "先选择项目，并完成至少一个已检查的 ComfyUI 预检。",
          requiresPreflight: "先完成一个已检查的 ComfyUI 预检。",
          noRequests: "暂无 ComfyUI 任务请求。",
        }
      : {
          title: "ComfyUI job requests",
          description: "Turn checked ComfyUI preflights into reviewable future job requests. This creates queue request metadata, checks, and recovery guidance only; it does not call ComfyUI or submit a queue job.",
          preflightLabel: "Checked preflight",
          priorityLabel: "Priority",
          runtimePayloadLabel: "Runtime boundary JSON",
          safetyChecksLabel: "Safety checks JSON",
          outputsLabel: "Expected outputs",
          recoveryLabel: "Recovery plan JSON",
          createAction: "Create job request",
          saveAction: "Save job request",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          queueAction: "Mark queued",
          failAction: "Fail",
          cancelAction: "Cancel",
          archiveAction: "Archive",
          selectedHint: "Select an operation and complete at least one checked ComfyUI preflight first.",
          requiresPreflight: "Complete one checked ComfyUI preflight first.",
          noRequests: "No ComfyUI job requests yet.",
        };
  const comfyuiExecutionCopy =
    language === "zh-CN"
      ? {
          title: "ComfyUI 执行预案",
          description: "把已批准或已标记排队的 ComfyUI 任务请求整理成可审查的队列模拟预案。这里只保存执行步骤、检查清单、回滚方案和模拟 payload，不会请求 ComfyUI、上传文件或提交队列。",
          jobRequestLabel: "已批准/已排队任务请求",
          priorityLabel: "优先级",
          stepsLabel: "执行步骤 JSON",
          checksLabel: "模拟检查 JSON",
          checklistLabel: "操作清单",
          simulationPayloadLabel: "模拟 payload JSON",
          rollbackLabel: "回滚方案 JSON",
          createAction: "创建执行预案",
          saveAction: "保存执行预案",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          simulateAction: "模拟",
          failAction: "失败",
          cancelAction: "取消",
          archiveAction: "归档",
          selectedHint: "先选择项目，并批准或标记排队至少一个 ComfyUI 任务请求。",
          requiresJobRequest: "先批准或标记排队一个 ComfyUI 任务请求。",
          noPlans: "暂无 ComfyUI 执行预案。",
        }
      : {
          title: "ComfyUI execution plans",
          description: "Prepare metadata-only queue simulation plans from approved or queued ComfyUI job requests. This records steps, checks, rollback guidance, and simulation payloads only; it does not call ComfyUI, upload files, or submit queues.",
          jobRequestLabel: "Approved/queued job request",
          priorityLabel: "Priority",
          stepsLabel: "Execution steps JSON",
          checksLabel: "Simulation checks JSON",
          checklistLabel: "Operator checklist",
          simulationPayloadLabel: "Simulation payload JSON",
          rollbackLabel: "Rollback plan JSON",
          createAction: "Create execution plan",
          saveAction: "Save execution plan",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          simulateAction: "Simulate",
          failAction: "Fail",
          cancelAction: "Cancel",
          archiveAction: "Archive",
          selectedHint: "Select an operation and approve or queue at least one ComfyUI job request first.",
          requiresJobRequest: "Approve or queue one ComfyUI job request first.",
          noPlans: "No ComfyUI execution plans yet.",
        };
  const comfyuiProbeCopy =
    language === "zh-CN"
      ? {
          title: "ComfyUI 连接探测",
          description: "从已批准或已模拟的执行预案创建受控连接探测记录，准备健康端点和只读队列快照计划；当前只保存元数据，不请求 ComfyUI、不读取队列、不提交任务。",
          executionPlanLabel: "已批准/已模拟执行预案",
          modeLabel: "探测模式",
          healthEndpointLabel: "健康端点",
          queueEndpointLabel: "队列端点",
          routesLabel: "只读路由",
          checksLabel: "准备检查 JSON",
          payloadLabel: "探测 payload JSON",
          healthSnapshotLabel: "健康快照 JSON",
          queueSnapshotLabel: "队列快照 JSON",
          schemaLabel: "响应结构 JSON",
          createAction: "创建连接探测",
          saveAction: "保存连接探测",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          probeAction: "记录探测",
          failAction: "失败",
          cancelAction: "取消",
          archiveAction: "归档",
          selectedHint: "先选择项目，并批准或模拟至少一个 ComfyUI 执行预案。",
          requiresExecutionPlan: "先批准或模拟一个 ComfyUI 执行预案。",
          noProbes: "暂无 ComfyUI 连接探测。",
        }
      : {
          title: "ComfyUI connection probes",
          description: "Prepare controlled connection health and read-only queue snapshot records from approved or simulated execution plans. This stores metadata only; it does not call ComfyUI, read queues, upload files, or submit jobs.",
          executionPlanLabel: "Approved/simulated execution plan",
          modeLabel: "Probe mode",
          healthEndpointLabel: "Health endpoint",
          queueEndpointLabel: "Queue endpoint",
          routesLabel: "Read-only routes",
          checksLabel: "Readiness checks JSON",
          payloadLabel: "Probe payload JSON",
          healthSnapshotLabel: "Health snapshot JSON",
          queueSnapshotLabel: "Queue snapshot JSON",
          schemaLabel: "Response schema JSON",
          createAction: "Create connection probe",
          saveAction: "Save connection probe",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          probeAction: "Record probe",
          failAction: "Fail",
          cancelAction: "Cancel",
          archiveAction: "Archive",
          selectedHint: "Select an operation and approve or simulate at least one ComfyUI execution plan first.",
          requiresExecutionPlan: "Approve or simulate one ComfyUI execution plan first.",
          noProbes: "No ComfyUI connection probes yet.",
        };
  const comfyuiDispatchCopy =
    language === "zh-CN"
      ? {
          title: "ComfyUI 适配器调度记录",
          description: "从已记录的连接探测创建可审批的适配器调度交接。这里只保存 prompt、workflow、queue、护栏、重试和恢复元数据，不会请求 ComfyUI、上传文件、提交队列或生成媒体。",
          connectionProbeLabel: "已记录连接探测",
          modeLabel: "调度模式",
          promptPayloadLabel: "Prompt payload JSON",
          workflowPayloadLabel: "Workflow payload JSON",
          queuePayloadLabel: "Queue payload JSON",
          dispatchPayloadLabel: "Dispatch payload JSON",
          guardrailsLabel: "护栏 JSON",
          checklistLabel: "操作清单",
          retryPolicyLabel: "重试策略 JSON",
          recoveryPlanLabel: "恢复方案 JSON",
          createAction: "创建调度记录",
          saveAction: "保存调度记录",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          dispatchAction: "记录调度",
          failAction: "失败",
          cancelAction: "取消",
          archiveAction: "归档",
          selectedHint: "先选择项目，并记录至少一个 ComfyUI 连接探测。",
          requiresProbe: "先记录一个 ComfyUI 连接探测。",
          noDispatches: "暂无 ComfyUI 适配器调度记录。",
        }
      : {
          title: "ComfyUI adapter dispatches",
          description: "Create reviewable adapter dispatch handoffs from recorded connection probes. This stores prompt, workflow, queue, guardrail, retry, and recovery metadata only; it does not call ComfyUI, upload files, submit queues, or generate media.",
          connectionProbeLabel: "Recorded connection probe",
          modeLabel: "Dispatch mode",
          promptPayloadLabel: "Prompt payload JSON",
          workflowPayloadLabel: "Workflow payload JSON",
          queuePayloadLabel: "Queue payload JSON",
          dispatchPayloadLabel: "Dispatch payload JSON",
          guardrailsLabel: "Guardrails JSON",
          checklistLabel: "Operator checklist",
          retryPolicyLabel: "Retry policy JSON",
          recoveryPlanLabel: "Recovery plan JSON",
          createAction: "Create dispatch",
          saveAction: "Save dispatch",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          dispatchAction: "Record dispatch",
          failAction: "Fail",
          cancelAction: "Cancel",
          archiveAction: "Archive",
          selectedHint: "Select an operation and record at least one ComfyUI connection probe first.",
          requiresProbe: "Record one ComfyUI connection probe first.",
          noDispatches: "No ComfyUI adapter dispatches yet.",
        };
  const deliverableCopy =
    language === "zh-CN"
      ? {
          title: "交付物",
          description: "把已批准内容草稿和已批准/已准备素材请求组装成 Output Library 产物；当前只做交付记录，不发布、不执行外部动作。",
          sourceDraftLabel: "批准草稿",
          linkedAssetsLabel: "关联素材请求",
          typeLabel: "交付类型",
          summaryLabel: "交付摘要",
          notesLabel: "交付说明",
          qualityChecksLabel: "质量检查",
          createAction: "创建交付物",
          saveAction: "保存交付物",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          packageAction: "打包",
          failAction: "失败",
          archiveAction: "归档",
          selectedHint: "先选择一个项目，再创建交付物。",
          noDeliverables: "暂无交付物。",
        }
      : {
          title: "Deliverables",
          description: "Assemble approved content drafts and approved/prepared asset requests into Output Library artifacts. This records handoff only; it does not publish or execute external actions.",
          sourceDraftLabel: "Approved draft",
          linkedAssetsLabel: "Linked asset requests",
          typeLabel: "Deliverable type",
          summaryLabel: "Summary",
          notesLabel: "Delivery notes",
          qualityChecksLabel: "Quality checks",
          createAction: "Create deliverable",
          saveAction: "Save deliverable",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          packageAction: "Package",
          failAction: "Fail",
          archiveAction: "Archive",
          selectedHint: "Select an operation before creating deliverables.",
          noDeliverables: "No deliverables yet.",
        };
  const evidenceCopy =
    language === "zh-CN"
      ? {
          title: "证据快照",
          description: "从已有 RAG 知识检索或人工输入生成已打包交付物的可审阅证据快照。RAG 生成只创建草稿，不上传知识、不自动批准、不发布、不执行外部动作。",
          deliverableLabel: "已打包交付物",
          typeLabel: "证据类型",
          collectionLabel: "知识库集合",
          queryLabel: "查询/审阅问题",
          searchModeLabel: "检索模式",
          summaryLabel: "证据摘要",
          relevanceLabel: "相关性说明",
          documentsLabel: "文档 ID",
          linksLabel: "来源链接",
          itemsLabel: "证据条目",
          coverageLabel: "覆盖检查",
          createAction: "创建证据快照",
          generateAction: "从 RAG 生成草稿",
          saveAction: "保存快照",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          archiveAction: "归档",
          selectedHint: "先选择项目，并至少打包一个交付物。",
          requiresDeliverable: "需要先打包交付物。",
          noSnapshots: "暂无证据快照。",
        }
      : {
          title: "Evidence snapshots",
          description: "Generate or capture evidence behind a packaged deliverable. RAG generation searches existing knowledge only and creates a draft; it does not upload knowledge, approve, publish, or execute external actions.",
          deliverableLabel: "Packaged deliverable",
          typeLabel: "Evidence type",
          collectionLabel: "Knowledge collection",
          queryLabel: "Query / review question",
          searchModeLabel: "Search mode",
          summaryLabel: "Evidence summary",
          relevanceLabel: "Relevance notes",
          documentsLabel: "Document IDs",
          linksLabel: "Source links",
          itemsLabel: "Evidence items",
          coverageLabel: "Coverage checks",
          createAction: "Create snapshot",
          generateAction: "Generate from RAG",
          saveAction: "Save snapshot",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          archiveAction: "Archive",
          selectedHint: "Select an operation and package at least one deliverable first.",
          requiresDeliverable: "Package one deliverable first.",
          noSnapshots: "No evidence snapshots yet.",
        };
  const executionRequestCopy =
    language === "zh-CN"
      ? {
          title: "执行请求",
          description: "从已打包交付物创建可审批、可准备、可追踪的执行交接请求；当前只保存元数据和交接载荷，不调用平台、不发布、不控制账号。",
          deliverableLabel: "已打包交付物",
          typeLabel: "执行类型",
          modeLabel: "执行模式",
          targetLabel: "目标平台/账号",
          summaryLabel: "输入摘要",
          runbookLabel: "操作步骤",
          readinessLabel: "准备检查",
          outputsLabel: "预期输出",
          evidenceLabel: "证据快照",
          checklistLabel: "人工检查清单",
          createAction: "创建执行请求",
          saveAction: "保存执行请求",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          prepareAction: "准备",
          failAction: "失败",
          cancelAction: "取消",
          archiveAction: "归档",
          selectedHint: "先选择一个项目，并至少打包一个交付物，再创建执行请求。",
          noRequests: "暂无执行请求。",
        }
      : {
          title: "Execution requests",
          description: "Create reviewable, preparable, and traceable execution handoff requests from packaged deliverables. This stores metadata and handoff payloads only; it does not call platforms, publish, or control accounts.",
          deliverableLabel: "Packaged deliverable",
          typeLabel: "Execution type",
          modeLabel: "Execution mode",
          targetLabel: "Target platform/account",
          summaryLabel: "Input summary",
          runbookLabel: "Runbook",
          readinessLabel: "Readiness checks",
          outputsLabel: "Expected outputs",
          evidenceLabel: "Evidence snapshots",
          checklistLabel: "Operator checklist",
          createAction: "Create execution request",
          saveAction: "Save execution request",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          prepareAction: "Prepare",
          failAction: "Fail",
          cancelAction: "Cancel",
          archiveAction: "Archive",
          selectedHint: "Select an operation and package at least one deliverable before creating execution requests.",
          noRequests: "No execution requests yet.",
        };
  const executionRunCopy =
    language === "zh-CN"
      ? {
          title: "执行运行记录",
          description: "从 prepared 执行请求创建可启动、可完成、可失败、可重试、可归档的运行记录。当前只保存审计与恢复数据，不调用平台、OpenClaw、ComfyUI 或浏览器 Worker。",
          requestLabel: "Prepared 执行请求",
          targetLabel: "运行目标",
          payloadLabel: "输入 JSON",
          maxRetriesLabel: "最大重试",
          notesLabel: "操作备注",
          createAction: "创建运行",
          saveAction: "保存运行",
          editAction: "编辑",
          startAction: "启动",
          succeedAction: "成功",
          failAction: "失败",
          retryAction: "重试",
          cancelAction: "取消",
          archiveAction: "归档",
          selectedHint: "先选择项目，并准备好一个执行请求，再创建运行记录。",
          requiresRequest: "需要先把执行请求推进到 prepared。",
          noRuns: "暂无执行运行记录。",
        }
      : {
          title: "Execution runs",
          description: "Create startable, completable, failable, retryable, and archivable run records from prepared execution requests. This stores audit and recovery data only; it does not call platforms, OpenClaw, ComfyUI, or Browser Worker.",
          requestLabel: "Prepared execution request",
          targetLabel: "Run target",
          payloadLabel: "Input JSON",
          maxRetriesLabel: "Max retries",
          notesLabel: "Operator notes",
          createAction: "Create run",
          saveAction: "Save run",
          editAction: "Edit",
          startAction: "Start",
          succeedAction: "Succeed",
          failAction: "Fail",
          retryAction: "Retry",
          cancelAction: "Cancel",
          archiveAction: "Archive",
          selectedHint: "Select an operation and prepare one execution request before creating run records.",
          requiresRequest: "Prepare one execution request first.",
          noRuns: "No execution runs yet.",
        };
  const resultCopy =
    language === "zh-CN"
      ? {
          title: "商业结果",
          description: "从已结束的执行运行创建可复盘、可审批的商业结果记录。这里只记录人工观察到的指标、证据和后续动作，不自动抓取平台数据，也不宣称 ROI 归因。",
          runLabel: "已结束运行",
          typeLabel: "结果类型",
          summaryLabel: "结果摘要",
          outcomeLabel: "商业观察",
          metricsLabel: "观察指标",
          signalsLabel: "商业信号",
          evidenceLabel: "证据链接",
          followUpsLabel: "后续动作",
          createAction: "创建结果",
          saveAction: "保存结果",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          archiveAction: "归档",
          selectedHint: "先选择项目，并让至少一个执行运行进入成功、失败或取消状态。",
          requiresRun: "需要先完成、失败或取消一个执行运行。",
          noResults: "暂无商业结果记录。",
        }
      : {
          title: "Results",
          description: "Create reviewable commercial result records from terminal execution runs. This stores operator-observed metrics, evidence, and follow-up actions only; it does not ingest platform analytics or claim ROI attribution.",
          runLabel: "Terminal run",
          typeLabel: "Result type",
          summaryLabel: "Result summary",
          outcomeLabel: "Commercial observation",
          metricsLabel: "Observed metrics",
          signalsLabel: "Commercial signals",
          evidenceLabel: "Evidence links",
          followUpsLabel: "Follow-up actions",
          createAction: "Create result",
          saveAction: "Save result",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          archiveAction: "Archive",
          selectedHint: "Select an operation and finish, fail, or cancel at least one execution run first.",
          requiresRun: "Finish, fail, or cancel one execution run first.",
          noResults: "No commercial results yet.",
        };
  const monitoringCopy =
    language === "zh-CN"
      ? {
          title: "监控观察",
          description: "从已批准的商业结果创建可复核的效果观察快照。这里记录人工观察到的指标、证据、异常和建议动作，不自动接入平台分析，也不宣称 ROI 归因。",
          resultLabel: "已批准结果",
          typeLabel: "观察类型",
          windowStartLabel: "观察开始",
          windowEndLabel: "观察结束",
          metricsLabel: "指标快照",
          signalsLabel: "定性信号",
          evidenceLabel: "证据链接",
          anomaliesLabel: "异常标记",
          actionsLabel: "建议动作",
          createAction: "创建观察",
          saveAction: "保存观察",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          archiveAction: "归档",
          selectedHint: "先选择项目，并批准至少一个商业结果，再创建监控观察。",
          requiresResult: "需要先批准一个商业结果。",
          noObservations: "暂无监控观察记录。",
        }
      : {
          title: "Monitoring observations",
          description: "Create reviewable effect-monitoring snapshots from approved commercial results. This stores operator-observed metrics, evidence, anomalies, and recommended actions only; it does not ingest platform analytics or claim ROI attribution.",
          resultLabel: "Approved result",
          typeLabel: "Observation type",
          windowStartLabel: "Window start",
          windowEndLabel: "Window end",
          metricsLabel: "Metric snapshots",
          signalsLabel: "Qualitative signals",
          evidenceLabel: "Evidence links",
          anomaliesLabel: "Anomaly flags",
          actionsLabel: "Recommended actions",
          createAction: "Create observation",
          saveAction: "Save observation",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          archiveAction: "Archive",
          selectedHint: "Select an operation and approve at least one commercial result first.",
          requiresResult: "Approve one commercial result first.",
          noObservations: "No monitoring observations yet.",
        };
  const optimizationCopy =
    language === "zh-CN"
      ? {
          title: "优化决策",
          description: "从已批准的监控观察创建可审计的下一步优化决策。它只记录继续、调整内容、调整素材、调整受众、重试交接、暂停或升级审核等人工决定，不会自动优化或发布。",
          observationLabel: "已批准观察",
          typeLabel: "决策类型",
          priorityLabel: "优先级",
          rationaleLabel: "决策理由",
          objectiveLabel: "目标调整",
          contentLabel: "内容动作",
          assetLabel: "素材动作",
          audienceLabel: "受众动作",
          executionLabel: "执行动作",
          riskLabel: "风险控制",
          createAction: "创建决策",
          saveAction: "保存决策",
          editAction: "编辑",
          readyAction: "送审",
          approveAction: "批准",
          rejectAction: "驳回",
          archiveAction: "归档",
          selectedHint: "先选择项目，并批准至少一条监控观察，再创建优化决策。",
          requiresObservation: "需要先批准一条监控观察。",
          noDecisions: "暂无优化决策记录。",
        }
      : {
          title: "Optimization decisions",
          description: "Create auditable next-step decisions from approved monitoring observations. This records continue, content, asset, audience, retry, pause, or escalation choices only; it does not auto-optimize or publish.",
          observationLabel: "Approved observation",
          typeLabel: "Decision type",
          priorityLabel: "Priority",
          rationaleLabel: "Rationale",
          objectiveLabel: "Objective updates",
          contentLabel: "Content actions",
          assetLabel: "Asset actions",
          audienceLabel: "Audience actions",
          executionLabel: "Execution actions",
          riskLabel: "Risk controls",
          createAction: "Create decision",
          saveAction: "Save decision",
          editAction: "Edit",
          readyAction: "Ready",
          approveAction: "Approve",
          rejectAction: "Reject",
          archiveAction: "Archive",
          selectedHint: "Select an operation and approve at least one monitoring observation first.",
          requiresObservation: "Approve one monitoring observation first.",
          noDecisions: "No optimization decisions yet.",
        };
  const [state, setState] = useState<AsyncState<JsonRecord>>(emptyState());
  const [actionState, setActionState] = useState<AsyncState<JsonRecord>>(emptyState());
  const [approvalsState, setApprovalsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [dryRunsState, setDryRunsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [contentDraftsState, setContentDraftsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [assetRequestsState, setAssetRequestsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [comfyuiHandoffsState, setComfyuiHandoffsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [comfyuiPreflightsState, setComfyuiPreflightsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [comfyuiAdapterConfigsState, setComfyuiAdapterConfigsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [comfyuiJobRequestsState, setComfyuiJobRequestsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [comfyuiExecutionPlansState, setComfyuiExecutionPlansState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [comfyuiConnectionProbesState, setComfyuiConnectionProbesState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [comfyuiAdapterDispatchesState, setComfyuiAdapterDispatchesState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [deliverablesState, setDeliverablesState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [evidenceSnapshotsState, setEvidenceSnapshotsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [executionRequestsState, setExecutionRequestsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [executionRunsState, setExecutionRunsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [resultsState, setResultsState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [monitoringState, setMonitoringState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [optimizationState, setOptimizationState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [linksState, setLinksState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [selectedOperation, setSelectedOperation] = useState<JsonRecord | null>(null);
  const [title, setTitle] = useState(language === "zh-CN" ? "新品增长运营项目" : "Product growth operation");
  const [objective, setObjective] = useState<string>(copy.objectivePlaceholder);
  const [targetAudience, setTargetAudience] = useState(language === "zh-CN" ? "高意向企业客户" : "High-intent business customers");
  const [channelsDraft, setChannelsDraft] = useState("website, newsletter, short-video");
  const [metricsDraft, setMetricsDraft] = useState("qualified_leads, content_output, review_pass_rate");
  const [knowledgeCollection, setKnowledgeCollection] = useState("ai_knowledge_base");
  const [priority, setPriority] = useState<"low" | "normal" | "high">("normal");
  const [riskLevel, setRiskLevel] = useState<"low" | "medium" | "high">("medium");
  const [budgetAmount, setBudgetAmount] = useState("");
  const [budgetCurrency, setBudgetCurrency] = useState("CNY");
  const [constraintsDraft, setConstraintsDraft] = useState(language === "zh-CN" ? "人工审批后执行, 不自动发布" : "execute after human approval, no auto publish");
  const [approvalStepKey, setApprovalStepKey] = useState("human_review");
  const [approvalTitle, setApprovalTitle] = useState(language === "zh-CN" ? "执行前人工审批" : "Review before execution");
  const [requestedAction, setRequestedAction] = useState(language === "zh-CN" ? "审批通过后才允许进入干运行或外部执行准备。" : "Approve before dry-run or external execution preparation.");
  const [approvalRiskLevel, setApprovalRiskLevel] = useState<"low" | "medium" | "high">("medium");
  const [dryRunApprovalId, setDryRunApprovalId] = useState("");
  const [dryRunStepKey, setDryRunStepKey] = useState("execution_dry_run");
  const [dryRunTitle, setDryRunTitle] = useState(language === "zh-CN" ? "安全执行干运行" : "Safe execution dry-run");
  const [executionMode, setExecutionMode] = useState<"metadata_only" | "dry_run">("metadata_only");
  const [executionTarget, setExecutionTarget] = useState("newsletter");
  const [dryRunInputSummary, setDryRunInputSummary] = useState(language === "zh-CN" ? "检查审批后的执行输入、目标渠道和交接输出，不触发外部动作。" : "Review approved execution inputs, target channel, and handoff output without external actions.");
  const [expectedOutputsDraft, setExpectedOutputsDraft] = useState(language === "zh-CN" ? "payload preview, operator handoff" : "payload preview, operator handoff");
  const [readinessChecksDraft, setReadinessChecksDraft] = useState(language === "zh-CN" ? "approval gate, no external publish, operator review" : "approval gate, no external publish, operator review");
  const [contentStepKey, setContentStepKey] = useState("content_production");
  const [contentChannel, setContentChannel] = useState("newsletter");
  const [contentFormat, setContentFormat] = useState("email");
  const [contentTitle, setContentTitle] = useState(language === "zh-CN" ? "渠道内容草稿" : "Channel content draft");
  const [contentAudienceSegment, setContentAudienceSegment] = useState(language === "zh-CN" ? "核心目标客户" : "Core target customers");
  const [contentSummary, setContentSummary] = useState(language === "zh-CN" ? "根据运营目标生成可审阅内容草稿。" : "Reviewable draft generated from the operation goal.");
  const [contentBody, setContentBody] = useState("");
  const [contentCallToAction, setContentCallToAction] = useState(language === "zh-CN" ? "预约演示" : "Book a demo");
  const [sourceMaterialsDraft, setSourceMaterialsDraft] = useState("rag_document, intake_notes");
  const [contentRagQuery, setContentRagQuery] = useState(language === "zh-CN" ? "哪些知识能支撑这份内容草稿？" : "Which knowledge should support this content draft?");
  const [contentSearchMode, setContentSearchMode] = useState("hybrid");
  const [assetRequestsDraft, setAssetRequestsDraft] = useState("hero image, product proof point");
  const [selectedContentDraftId, setSelectedContentDraftId] = useState("");
  const [assetStepKey, setAssetStepKey] = useState("content_production");
  const [assetContentDraftId, setAssetContentDraftId] = useState("");
  const [assetChannel, setAssetChannel] = useState("newsletter");
  const [assetType, setAssetType] = useState("image");
  const [assetTitle, setAssetTitle] = useState(language === "zh-CN" ? "渠道头图素材请求" : "Channel hero asset request");
  const [assetPurpose, setAssetPurpose] = useState(language === "zh-CN" ? "用于已批准内容草稿的视觉头图。" : "Visual header for the approved content draft.");
  const [assetDimensions, setAssetDimensions] = useState("1200x628");
  const [assetStyleConstraints, setAssetStyleConstraints] = useState(language === "zh-CN" ? "清晰、可信、避免不一致品牌元素。" : "Clear, credible, avoid off-brand elements.");
  const [assetPrompt, setAssetPrompt] = useState(language === "zh-CN" ? "为 B2B 增长活动准备专业营销视觉。" : "Prepare a professional marketing visual for a B2B growth campaign.");
  const [assetNegativePrompt, setAssetNegativePrompt] = useState(language === "zh-CN" ? "不要真实商标，不要不可读文字。" : "No real logos, no unreadable text.");
  const [assetRagQuery, setAssetRagQuery] = useState(language === "zh-CN" ? "哪些知识能支持这份素材简报？" : "Which knowledge should support this asset brief?");
  const [assetSearchMode, setAssetSearchMode] = useState("hybrid");
  const [assetSourceMaterialsDraft, setAssetSourceMaterialsDraft] = useState("rag_document, approved_content_draft");
  const [assetReadinessChecksDraft, setAssetReadinessChecksDraft] = useState("approved draft, source materials, no ComfyUI job");
  const [selectedAssetRequestId, setSelectedAssetRequestId] = useState("");
  const [selectedComfyuiHandoffId, setSelectedComfyuiHandoffId] = useState("");
  const [comfyuiAssetRequestId, setComfyuiAssetRequestId] = useState("");
  const [comfyuiTitle, setComfyuiTitle] = useState(language === "zh-CN" ? "ComfyUI 交接记录" : "ComfyUI handoff record");
  const [comfyuiWorkflowName, setComfyuiWorkflowName] = useState("future_comfyui_handoff");
  const [comfyuiPromptPayloadDraft, setComfyuiPromptPayloadDraft] = useState('{"execution_mode":"metadata_only"}');
  const [comfyuiWorkflowPayloadDraft, setComfyuiWorkflowPayloadDraft] = useState('{"adapter":"future_guarded_comfyui_adapter"}');
  const [comfyuiReadinessChecksDraft, setComfyuiReadinessChecksDraft] = useState("asset approved, source reviewed, no ComfyUI job submitted");
  const [selectedComfyuiPreflightId, setSelectedComfyuiPreflightId] = useState("");
  const [comfyuiPreflightHandoffId, setComfyuiPreflightHandoffId] = useState("");
  const [comfyuiPreflightAdapterConfigId, setComfyuiPreflightAdapterConfigId] = useState("");
  const [comfyuiPreflightTitle, setComfyuiPreflightTitle] = useState(language === "zh-CN" ? "ComfyUI 连接预检" : "ComfyUI connection preflight");
  const [comfyuiPreflightTargetUrl, setComfyuiPreflightTargetUrl] = useState("http://comfyui:8188");
  const [comfyuiPreflightQueueName, setComfyuiPreflightQueueName] = useState("commercial-assets");
  const [comfyuiPreflightWorkflowName, setComfyuiPreflightWorkflowName] = useState("future_comfyui_handoff");
  const [comfyuiPreflightModelRefsDraft, setComfyuiPreflightModelRefsDraft] = useState("sdxl_base, brand_lora_placeholder");
  const [comfyuiPreflightAdapterConfigDraft, setComfyuiPreflightAdapterConfigDraft] = useState('{"adapter":"future_guarded_comfyui_adapter"}');
  const [comfyuiPreflightCheckItemsDraft, setComfyuiPreflightCheckItemsDraft] = useState("[]");
  const [selectedComfyuiAdapterConfigId, setSelectedComfyuiAdapterConfigId] = useState("");
  const [comfyuiAdapterTitle, setComfyuiAdapterTitle] = useState(language === "zh-CN" ? "ComfyUI 适配器配置" : "ComfyUI adapter config");
  const [comfyuiAdapterTargetUrl, setComfyuiAdapterTargetUrl] = useState("http://comfyui:8188");
  const [comfyuiAdapterAuthMode, setComfyuiAdapterAuthMode] = useState("none");
  const [comfyuiAdapterSecretRef, setComfyuiAdapterSecretRef] = useState("");
  const [comfyuiAdapterQueueName, setComfyuiAdapterQueueName] = useState("commercial-assets");
  const [comfyuiAdapterDefaultWorkflow, setComfyuiAdapterDefaultWorkflow] = useState("future_comfyui_handoff");
  const [comfyuiAdapterAllowedWorkflowsDraft, setComfyuiAdapterAllowedWorkflowsDraft] = useState("future_comfyui_handoff");
  const [comfyuiAdapterModelInventoryDraft, setComfyuiAdapterModelInventoryDraft] = useState(
    '[{"name":"sdxl_base","type":"checkpoint","status":"available"},{"name":"brand_lora_placeholder","type":"lora","status":"available"}]',
  );
  const [comfyuiAdapterRuntimeLimitsDraft, setComfyuiAdapterRuntimeLimitsDraft] = useState(
    '{"max_concurrency":1,"timeout_seconds":120,"execution_mode":"metadata_only","submit_jobs":false}',
  );
  const [comfyuiAdapterMaintenanceNotes, setComfyuiAdapterMaintenanceNotes] = useState("Maintainer reviewed endpoint and queue. No ComfyUI call is made here.");
  const [comfyuiAdapterValidationChecksDraft, setComfyuiAdapterValidationChecksDraft] = useState("[]");
  const [selectedComfyuiJobRequestId, setSelectedComfyuiJobRequestId] = useState("");
  const [comfyuiJobPreflightId, setComfyuiJobPreflightId] = useState("");
  const [comfyuiJobTitle, setComfyuiJobTitle] = useState(language === "zh-CN" ? "ComfyUI 任务请求" : "ComfyUI job request");
  const [comfyuiJobPriority, setComfyuiJobPriority] = useState<"low" | "normal" | "high">("normal");
  const [comfyuiJobRuntimePayloadDraft, setComfyuiJobRuntimePayloadDraft] = useState('{"execution_mode":"metadata_only","submit_job":false}');
  const [comfyuiJobSafetyChecksDraft, setComfyuiJobSafetyChecksDraft] = useState("[]");
  const [comfyuiJobOutputsDraft, setComfyuiJobOutputsDraft] = useState("reviewable queue payload, operator recovery guidance");
  const [comfyuiJobRecoveryDraft, setComfyuiJobRecoveryDraft] = useState('{"next_steps":["review preflight","adjust payload if needed"]}');
  const [selectedComfyuiExecutionPlanId, setSelectedComfyuiExecutionPlanId] = useState("");
  const [comfyuiExecutionJobRequestId, setComfyuiExecutionJobRequestId] = useState("");
  const [comfyuiExecutionTitle, setComfyuiExecutionTitle] = useState(language === "zh-CN" ? "ComfyUI 执行预案" : "ComfyUI execution plan");
  const [comfyuiExecutionPriority, setComfyuiExecutionPriority] = useState<"low" | "normal" | "high">("normal");
  const [comfyuiExecutionStepsDraft, setComfyuiExecutionStepsDraft] = useState(
    '[{"title":"Review approved job request","status":"planned"},{"title":"Simulate queue payload locally","status":"planned"}]',
  );
  const [comfyuiExecutionChecksDraft, setComfyuiExecutionChecksDraft] = useState("[]");
  const [comfyuiExecutionChecklistDraft, setComfyuiExecutionChecklistDraft] = useState("approval still valid, adapter disabled, rollback owner confirmed");
  const [comfyuiExecutionSimulationPayloadDraft, setComfyuiExecutionSimulationPayloadDraft] = useState('{"execution_mode":"metadata_only","queue_submission":false,"upload_files":false}');
  const [comfyuiExecutionRollbackDraft, setComfyuiExecutionRollbackDraft] = useState('{"next_steps":["review execution plan","adjust queue payload shape"]}');
  const [selectedComfyuiConnectionProbeId, setSelectedComfyuiConnectionProbeId] = useState("");
  const [comfyuiProbeExecutionPlanId, setComfyuiProbeExecutionPlanId] = useState("");
  const [comfyuiProbeTitle, setComfyuiProbeTitle] = useState(language === "zh-CN" ? "ComfyUI 连接探测" : "ComfyUI connection probe");
  const [comfyuiProbeMode, setComfyuiProbeMode] = useState("metadata_only");
  const [comfyuiProbeHealthEndpoint, setComfyuiProbeHealthEndpoint] = useState("/system_stats");
  const [comfyuiProbeQueueEndpoint, setComfyuiProbeQueueEndpoint] = useState("/queue");
  const [comfyuiProbeRoutesDraft, setComfyuiProbeRoutesDraft] = useState("/system_stats, /queue");
  const [comfyuiProbeChecksDraft, setComfyuiProbeChecksDraft] = useState("[]");
  const [comfyuiProbePayloadDraft, setComfyuiProbePayloadDraft] = useState('{"probe_mode":"metadata_only","network_probe":false,"read_only_probe":false}');
  const [comfyuiProbeHealthSnapshotDraft, setComfyuiProbeHealthSnapshotDraft] = useState('{"source":"metadata_only","reachable":"not_measured"}');
  const [comfyuiProbeQueueSnapshotDraft, setComfyuiProbeQueueSnapshotDraft] = useState('{"source":"metadata_only","queue_observed":false}');
  const [comfyuiProbeSchemaDraft, setComfyuiProbeSchemaDraft] = useState('{"health_response":{"expected_keys":["system","devices"]},"queue_response":{"expected_keys":["queue_running","queue_pending"]}}');
  const [selectedComfyuiAdapterDispatchId, setSelectedComfyuiAdapterDispatchId] = useState("");
  const [comfyuiDispatchConnectionProbeId, setComfyuiDispatchConnectionProbeId] = useState("");
  const [comfyuiDispatchTitle, setComfyuiDispatchTitle] = useState(language === "zh-CN" ? "ComfyUI 适配器调度记录" : "ComfyUI adapter dispatch");
  const [comfyuiDispatchMode, setComfyuiDispatchMode] = useState("metadata_only");
  const [comfyuiDispatchPromptPayloadDraft, setComfyuiDispatchPromptPayloadDraft] = useState('{"source":"metadata_only"}');
  const [comfyuiDispatchWorkflowPayloadDraft, setComfyuiDispatchWorkflowPayloadDraft] = useState('{"workflow_validation":"documented_only"}');
  const [comfyuiDispatchQueuePayloadDraft, setComfyuiDispatchQueuePayloadDraft] = useState('{"queue_submission":false,"queue_read":false}');
  const [comfyuiDispatchPayloadDraft, setComfyuiDispatchPayloadDraft] = useState('{"dispatch_mode":"metadata_only","queue_submission":false,"prompt_submission":false}');
  const [comfyuiDispatchGuardrailsDraft, setComfyuiDispatchGuardrailsDraft] = useState("[]");
  const [comfyuiDispatchChecklistDraft, setComfyuiDispatchChecklistDraft] = useState("connection probe recorded, operator approval required, no real adapter call");
  const [comfyuiDispatchRetryDraft, setComfyuiDispatchRetryDraft] = useState('{"retry_mode":"operator_review_only","max_attempts":1}');
  const [comfyuiDispatchRecoveryDraft, setComfyuiDispatchRecoveryDraft] = useState('{"next_steps":["review connection probe","keep dispatch metadata-only"]}');
  const [deliverableContentDraftId, setDeliverableContentDraftId] = useState("");
  const [deliverableAssetRequestIdsDraft, setDeliverableAssetRequestIdsDraft] = useState("");
  const [deliverableType, setDeliverableType] = useState("content_package");
  const [deliverableTitle, setDeliverableTitle] = useState(language === "zh-CN" ? "商业运营交付物" : "Commercial operation deliverable");
  const [deliverableSummary, setDeliverableSummary] = useState(language === "zh-CN" ? "面向操作员交接的内容产物。" : "Output artifact for operator handoff.");
  const [deliverableNotes, setDeliverableNotes] = useState(language === "zh-CN" ? "只进入 Output Library，不发布。" : "Store in Output Library only; do not publish.");
  const [deliverableQualityChecksDraft, setDeliverableQualityChecksDraft] = useState("approved content draft, linked assets reviewed, no external publish");
  const [selectedDeliverableId, setSelectedDeliverableId] = useState("");
  const [evidenceDeliverableId, setEvidenceDeliverableId] = useState("");
  const [selectedEvidenceSnapshotId, setSelectedEvidenceSnapshotId] = useState("");
  const [evidenceType, setEvidenceType] = useState("rag_snapshot");
  const [evidenceTitle, setEvidenceTitle] = useState(language === "zh-CN" ? "交付物证据快照" : "Deliverable evidence snapshot");
  const [evidenceCollection, setEvidenceCollection] = useState("ai_knowledge_base");
  const [evidenceQuery, setEvidenceQuery] = useState(language === "zh-CN" ? "哪些知识库材料支撑这次交付？" : "Which knowledge materials support this deliverable?");
  const [evidenceSearchMode, setEvidenceSearchMode] = useState("hybrid");
  const [evidenceSummary, setEvidenceSummary] = useState(language === "zh-CN" ? "人工确认的来源材料和关键依据。" : "Operator-confirmed source materials and key proof points.");
  const [evidenceRelevance, setEvidenceRelevance] = useState(language === "zh-CN" ? "用于执行前核对内容、素材和目标受众是否匹配。" : "Used to verify content, assets, and target audience before execution.");
  const [evidenceDocumentIdsDraft, setEvidenceDocumentIdsDraft] = useState("doc-knowledge-1");
  const [evidenceLinksDraft, setEvidenceLinksDraft] = useState("intake conversation, approved draft");
  const [evidenceItemsDraft, setEvidenceItemsDraft] = useState("customer pain point, offer proof, approval boundary");
  const [evidenceCoverageDraft, setEvidenceCoverageDraft] = useState("source reviewed, relevance confirmed, no upload or external execution");
  const [executionDeliverableId, setExecutionDeliverableId] = useState("");
  const [selectedExecutionRequestId, setSelectedExecutionRequestId] = useState("");
  const [executionRequestType, setExecutionRequestType] = useState("manual_handoff");
  const [executionRequestMode, setExecutionRequestMode] = useState("metadata_only");
  const [executionRequestTitle, setExecutionRequestTitle] = useState(language === "zh-CN" ? "执行交接请求" : "Execution handoff request");
  const [executionRequestTarget, setExecutionRequestTarget] = useState("newsletter_platform");
  const [executionRequestInputSummary, setExecutionRequestInputSummary] = useState(language === "zh-CN" ? "从已打包交付物准备后续人工确认的执行交接。" : "Prepare future operator-confirmed execution from a packaged deliverable.");
  const [executionRunbookDraft, setExecutionRunbookDraft] = useState("review packaged deliverable, confirm target account, prepare future guarded runtime handoff");
  const [executionReadinessDraft, setExecutionReadinessDraft] = useState("packaged deliverable, human approval, no external runtime call");
  const [executionOutputsDraft, setExecutionOutputsDraft] = useState("approved request, traceable handoff payload, operator result record");
  const [executionEvidenceSnapshotIdsDraft, setExecutionEvidenceSnapshotIdsDraft] = useState("");
  const [executionChecklistDraft, setExecutionChecklistDraft] = useState("review approved evidence snapshots, confirm target account, confirm approval gate");
  const [executionRunRequestId, setExecutionRunRequestId] = useState("");
  const [selectedExecutionRunId, setSelectedExecutionRunId] = useState("");
  const [executionRunTitle, setExecutionRunTitle] = useState(language === "zh-CN" ? "执行运行记录" : "Execution run record");
  const [executionRunTarget, setExecutionRunTarget] = useState("newsletter_platform");
  const [executionRunInputPayloadDraft, setExecutionRunInputPayloadDraft] = useState('{"source":"admin_dashboard"}');
  const [executionRunMaxRetries, setExecutionRunMaxRetries] = useState("1");
  const [executionRunOperatorNotes, setExecutionRunOperatorNotes] = useState(language === "zh-CN" ? "人工确认后运行，不调用外部平台。" : "Run after human review; no external platform call.");
  const [resultRunId, setResultRunId] = useState("");
  const [selectedResultId, setSelectedResultId] = useState("");
  const [resultTitle, setResultTitle] = useState(language === "zh-CN" ? "商业结果复盘" : "Commercial result review");
  const [resultType, setResultType] = useState("operator_report");
  const [resultSummary, setResultSummary] = useState(language === "zh-CN" ? "记录人工确认的执行结果与证据。" : "Record operator-confirmed execution result and evidence.");
  const [resultOutcomeSummary, setResultOutcomeSummary] = useState(language === "zh-CN" ? "尚未接入平台分析，仅记录观察结果。" : "Platform analytics are not ingested; this is an observed result only.");
  const [resultMetricsDraft, setResultMetricsDraft] = useState("qualified_leads=0\nreview_pass_rate=manual");
  const [resultSignalsDraft, setResultSignalsDraft] = useState("operator reviewed, needs next iteration");
  const [resultEvidenceDraft, setResultEvidenceDraft] = useState("execution run payload, operator screenshot");
  const [resultFollowUpsDraft, setResultFollowUpsDraft] = useState("review next audience segment, update content proof points");
  const [monitoringResultId, setMonitoringResultId] = useState("");
  const [selectedObservationId, setSelectedObservationId] = useState("");
  const [monitoringTitle, setMonitoringTitle] = useState(language === "zh-CN" ? "效果监控观察" : "Effect monitoring observation");
  const [monitoringType, setMonitoringType] = useState("manual_snapshot");
  const [monitoringWindowStart, setMonitoringWindowStart] = useState("");
  const [monitoringWindowEnd, setMonitoringWindowEnd] = useState("");
  const [monitoringMetricsDraft, setMonitoringMetricsDraft] = useState("qualified_leads=0\nengagement_signal=manual");
  const [monitoringSignalsDraft, setMonitoringSignalsDraft] = useState("manual review completed, watch next iteration");
  const [monitoringEvidenceDraft, setMonitoringEvidenceDraft] = useState("operator screenshot, platform note");
  const [monitoringAnomaliesDraft, setMonitoringAnomaliesDraft] = useState("no automated analytics ingestion");
  const [monitoringActionsDraft, setMonitoringActionsDraft] = useState("review next content angle, confirm handoff owner");
  const [optimizationObservationId, setOptimizationObservationId] = useState("");
  const [selectedOptimizationDecisionId, setSelectedOptimizationDecisionId] = useState("");
  const [optimizationTitle, setOptimizationTitle] = useState(language === "zh-CN" ? "下一轮优化决策" : "Next optimization decision");
  const [optimizationType, setOptimizationType] = useState("iterate");
  const [optimizationPriority, setOptimizationPriority] = useState("normal");
  const [optimizationRationale, setOptimizationRationale] = useState(language === "zh-CN" ? "基于已批准监控观察，准备人工确认的下一步优化。" : "Based on the approved monitoring observation, prepare the next operator-confirmed optimization.");
  const [optimizationObjectiveUpdatesDraft, setOptimizationObjectiveUpdatesDraft] = useState("focus on qualified leads");
  const [optimizationContentActionsDraft, setOptimizationContentActionsDraft] = useState("update content proof point, test next CTA");
  const [optimizationAssetActionsDraft, setOptimizationAssetActionsDraft] = useState("refresh hero visual brief");
  const [optimizationAudienceActionsDraft, setOptimizationAudienceActionsDraft] = useState("review next audience segment");
  const [optimizationExecutionActionsDraft, setOptimizationExecutionActionsDraft] = useState("prepare next manual handoff");
  const [optimizationRiskControlsDraft, setOptimizationRiskControlsDraft] = useState("human approval before runtime, no auto publish");
  const [linkType, setLinkType] = useState("conversation");
  const [targetType, setTargetType] = useState("conversation_thread");
  const [targetId, setTargetId] = useState("");
  const [linkTitle, setLinkTitle] = useState(language === "zh-CN" ? "需求沟通记录" : "Goal intake record");
  const [linkSummary, setLinkSummary] = useState("");
  const [linkSourceName, setLinkSourceName] = useState("admin_dashboard");

  const load = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const operations = await commercialOperationsApi.list("", settings);
      setState({ data: { operations }, error: null, loading: false, updatedAt: nowLabel() });
      const items = toItems(operations);
      setSelectedOperation((current) => {
        if (current && items.some((item) => valueAt(item, ["id"]) === valueAt(current, ["id"]))) {
          return items.find((item) => valueAt(item, ["id"]) === valueAt(current, ["id"])) ?? current;
        }
        return items[0] ?? null;
      });
    } catch (error) {
      setState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operations API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings]);

  useEffect(() => {
    void load();
  }, [load]);

  const selectedOperationId = selectedOperation ? valueAt(selectedOperation, ["id"], "") : "";

  const loadApprovals = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setApprovalsState(emptyState());
        return;
      }
      setApprovalsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.approvals(operationId, settings);
        setApprovalsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setApprovalsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation approvals API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadLinks = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setLinksState(emptyState());
        return;
      }
      setLinksState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.links(operationId, settings);
        setLinksState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setLinksState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation links API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadDryRuns = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setDryRunsState(emptyState());
        return;
      }
      setDryRunsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.dryRuns(operationId, settings);
        setDryRunsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setDryRunsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation dry-runs API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadContentDrafts = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setContentDraftsState(emptyState());
        return;
      }
      setContentDraftsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.contentDrafts(operationId, settings);
        setContentDraftsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setContentDraftsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation content drafts API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadAssetRequests = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setAssetRequestsState(emptyState());
        return;
      }
      setAssetRequestsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.assetRequests(operationId, settings);
        setAssetRequestsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setAssetRequestsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation asset requests API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadComfyuiHandoffs = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setComfyuiHandoffsState(emptyState());
        return;
      }
      setComfyuiHandoffsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.comfyuiHandoffs(operationId, settings);
        setComfyuiHandoffsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setComfyuiHandoffsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation ComfyUI handoffs API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadComfyuiPreflights = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setComfyuiPreflightsState(emptyState());
        return;
      }
      setComfyuiPreflightsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.comfyuiPreflights(operationId, settings);
        setComfyuiPreflightsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setComfyuiPreflightsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation ComfyUI preflights API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadComfyuiAdapterConfigs = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setComfyuiAdapterConfigsState(emptyState());
        return;
      }
      setComfyuiAdapterConfigsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.comfyuiAdapterConfigs(operationId, settings);
        setComfyuiAdapterConfigsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setComfyuiAdapterConfigsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation ComfyUI adapter configs API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadComfyuiJobRequests = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setComfyuiJobRequestsState(emptyState());
        return;
      }
      setComfyuiJobRequestsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.comfyuiJobRequests(operationId, settings);
        setComfyuiJobRequestsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setComfyuiJobRequestsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation ComfyUI job requests API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadComfyuiExecutionPlans = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setComfyuiExecutionPlansState(emptyState());
        return;
      }
      setComfyuiExecutionPlansState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.comfyuiExecutionPlans(operationId, settings);
        setComfyuiExecutionPlansState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setComfyuiExecutionPlansState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation ComfyUI execution plans API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadComfyuiConnectionProbes = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setComfyuiConnectionProbesState(emptyState());
        return;
      }
      setComfyuiConnectionProbesState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.comfyuiConnectionProbes(operationId, settings);
        setComfyuiConnectionProbesState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setComfyuiConnectionProbesState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation ComfyUI connection probes API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadComfyuiAdapterDispatches = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setComfyuiAdapterDispatchesState(emptyState());
        return;
      }
      setComfyuiAdapterDispatchesState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.comfyuiAdapterDispatches(operationId, settings);
        setComfyuiAdapterDispatchesState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setComfyuiAdapterDispatchesState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation ComfyUI adapter dispatches API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadDeliverables = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setDeliverablesState(emptyState());
        return;
      }
      setDeliverablesState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.deliverables(operationId, settings);
        setDeliverablesState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setDeliverablesState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation deliverables API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadEvidenceSnapshots = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setEvidenceSnapshotsState(emptyState());
        return;
      }
      setEvidenceSnapshotsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.evidenceSnapshots(operationId, settings);
        setEvidenceSnapshotsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setEvidenceSnapshotsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation evidence snapshots API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadExecutionRequests = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setExecutionRequestsState(emptyState());
        return;
      }
      setExecutionRequestsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.executionRequests(operationId, settings);
        setExecutionRequestsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setExecutionRequestsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation execution requests API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadExecutionRuns = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setExecutionRunsState(emptyState());
        return;
      }
      setExecutionRunsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.executionRuns(operationId, settings);
        setExecutionRunsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setExecutionRunsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation execution runs API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadResults = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setResultsState(emptyState());
        return;
      }
      setResultsState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.results(operationId, settings);
        setResultsState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setResultsState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation results API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadMonitoringObservations = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setMonitoringState(emptyState());
        return;
      }
      setMonitoringState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.monitoringObservations(operationId, settings);
        setMonitoringState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setMonitoringState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation monitoring observations API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  const loadOptimizationDecisions = useCallback(
    async (operationId: string) => {
      if (!operationId) {
        setOptimizationState(emptyState());
        return;
      }
      setOptimizationState((current) => ({ ...current, loading: true, error: null }));
      try {
        const response = await commercialOperationsApi.optimizationDecisions(operationId, settings);
        setOptimizationState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
      } catch (error) {
        setOptimizationState({
          data: null,
          error: error instanceof Error ? error.message : "Commercial operation optimization decisions API unavailable",
          loading: false,
          updatedAt: nowLabel(),
        });
      }
    },
    [settings],
  );

  useEffect(() => {
    if (selectedOperationId) {
      void loadApprovals(selectedOperationId);
      void loadDryRuns(selectedOperationId);
      void loadContentDrafts(selectedOperationId);
      void loadAssetRequests(selectedOperationId);
      void loadComfyuiHandoffs(selectedOperationId);
      void loadComfyuiPreflights(selectedOperationId);
      void loadComfyuiAdapterConfigs(selectedOperationId);
      void loadComfyuiJobRequests(selectedOperationId);
      void loadComfyuiExecutionPlans(selectedOperationId);
      void loadComfyuiConnectionProbes(selectedOperationId);
      void loadComfyuiAdapterDispatches(selectedOperationId);
      void loadDeliverables(selectedOperationId);
      void loadEvidenceSnapshots(selectedOperationId);
      void loadExecutionRequests(selectedOperationId);
      void loadExecutionRuns(selectedOperationId);
      void loadResults(selectedOperationId);
      void loadMonitoringObservations(selectedOperationId);
      void loadOptimizationDecisions(selectedOperationId);
      void loadLinks(selectedOperationId);
      return;
    }
    setApprovalsState(emptyState());
    setDryRunsState(emptyState());
    setContentDraftsState(emptyState());
    setAssetRequestsState(emptyState());
    setComfyuiHandoffsState(emptyState());
    setComfyuiPreflightsState(emptyState());
    setComfyuiAdapterConfigsState(emptyState());
    setComfyuiJobRequestsState(emptyState());
    setComfyuiExecutionPlansState(emptyState());
    setComfyuiConnectionProbesState(emptyState());
    setComfyuiAdapterDispatchesState(emptyState());
    setDeliverablesState(emptyState());
    setEvidenceSnapshotsState(emptyState());
    setExecutionRequestsState(emptyState());
    setExecutionRunsState(emptyState());
    setResultsState(emptyState());
    setMonitoringState(emptyState());
    setOptimizationState(emptyState());
    setLinksState(emptyState());
  }, [selectedOperationId, loadApprovals, loadDryRuns, loadContentDrafts, loadAssetRequests, loadComfyuiHandoffs, loadComfyuiPreflights, loadComfyuiAdapterConfigs, loadComfyuiJobRequests, loadComfyuiExecutionPlans, loadComfyuiConnectionProbes, loadComfyuiAdapterDispatches, loadDeliverables, loadEvidenceSnapshots, loadExecutionRequests, loadExecutionRuns, loadResults, loadMonitoringObservations, loadOptimizationDecisions, loadLinks]);

  const createOperation = async () => {
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const budget = budgetAmount.trim() ? Number(budgetAmount) : undefined;
      if (budget !== undefined && (!Number.isFinite(budget) || budget < 0)) {
        throw new Error("budget must be a positive number");
      }
      const payload: JsonRecord = {
        title: title.trim(),
        objective: objective.trim(),
        target_audience: targetAudience.trim() || undefined,
        channels: splitDraftList(channelsDraft),
        success_metrics: splitDraftList(metricsDraft),
        constraints: splitDraftList(constraintsDraft),
        knowledge_collection: knowledgeCollection.trim() || undefined,
        priority,
        risk_level: riskLevel,
        budget_amount: budget,
        budget_currency: budgetCurrency.trim() || "CNY",
        metadata: { source: "admin_dashboard", phase: "61C" },
      };
      const created = await commercialOperationsApi.create(payload, settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedOperation(created);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const createOperationApproval = async () => {
    if (!selectedOperationId) {
      setActionState({
        data: null,
        error: copy.approvalsSelectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    const outline = selectedOperation && Array.isArray(selectedOperation.plan_outline) ? (selectedOperation.plan_outline as JsonRecord[]) : [];
    const selectedStep = outline.find((step) => valueAt(step, ["step_key"], "") === approvalStepKey);
    const fallbackTitle = selectedStep ? valueAt(selectedStep, ["title"], approvalStepKey) : approvalStepKey;
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createApproval(
        selectedOperationId,
        {
          step_key: approvalStepKey.trim(),
          title: approvalTitle.trim() || fallbackTitle,
          requested_action: requestedAction.trim() || undefined,
          risk_level: approvalRiskLevel,
          metadata: { source: "admin_dashboard", phase: "61C" },
        },
        settings,
      );
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      await loadApprovals(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation approval create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateOperationApproval = async (approvalId: string, action: "approve" | "reject" | "cancel") => {
    if (!selectedOperationId || !approvalId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "approve"
          ? await commercialOperationsApi.approveApproval(selectedOperationId, approvalId, "Approved from Commercial Ops.", settings)
          : action === "reject"
            ? await commercialOperationsApi.rejectApproval(selectedOperationId, approvalId, "Rejected from Commercial Ops.", settings)
            : await commercialOperationsApi.cancelApproval(selectedOperationId, approvalId, "Cancelled from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadApprovals(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation approval action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editOperationContentDraft = (draft: JsonRecord) => {
    const draftId = valueAt(draft, ["id"], "");
    if (!draftId) {
      return;
    }
    setSelectedContentDraftId(draftId);
    setContentStepKey(valueAt(draft, ["step_key"], contentStepKey));
    setContentChannel(valueAt(draft, ["channel"], contentChannel));
    setContentFormat(valueAt(draft, ["content_format"], contentFormat));
    setContentTitle(valueAt(draft, ["title"], contentTitle));
    setContentAudienceSegment(valueAt(draft, ["audience_segment"], ""));
    setContentSummary(valueAt(draft, ["summary"], ""));
    setContentBody(valueAt(draft, ["content_body"], ""));
    setContentCallToAction(valueAt(draft, ["call_to_action"], ""));
    setSourceMaterialsDraft(draftListText(draft.source_materials));
    setAssetRequestsDraft(draftListText(draft.asset_requests));
  };

  const contentDraftPayload = (): JsonRecord => ({
    step_key: contentStepKey.trim() || "content_production",
    channel: contentChannel.trim() || "newsletter",
    content_format: contentFormat,
    title: contentTitle.trim(),
    audience_segment: contentAudienceSegment.trim() || undefined,
    content_body: contentBody.trim() || undefined,
    summary: contentSummary.trim() || undefined,
    call_to_action: contentCallToAction.trim() || undefined,
    source_materials: splitDraftList(sourceMaterialsDraft),
    asset_requests: splitDraftList(assetRequestsDraft).map((item) => ({ title: item, type: "asset_placeholder" })),
    metadata: { source: "admin_dashboard", phase: "61E" },
  });

  const createOperationContentDraft = async () => {
    if (!selectedOperationId) {
      setActionState({
        data: null,
        error: contentCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createContentDraft(selectedOperationId, contentDraftPayload(), settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedContentDraftId(valueAt(created, ["id"], ""));
      setContentBody(valueAt(created, ["content_body"], contentBody));
      await loadContentDrafts(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation content draft create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const generateOperationContentDraft = async () => {
    if (!selectedOperationId) {
      setActionState({
        data: null,
        error: contentCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const generated = await commercialOperationsApi.generateContentDraft(
        selectedOperationId,
        {
          step_key: contentStepKey.trim() || "content_production",
          channel: contentChannel.trim() || "newsletter",
          content_format: contentFormat,
          title: contentTitle.trim() || undefined,
          audience_segment: contentAudienceSegment.trim() || undefined,
          query: contentRagQuery.trim() || undefined,
          knowledge_collection: valueAt(selectedOperation, ["knowledge_collection"], knowledgeCollection).trim() || undefined,
          search_mode: contentSearchMode,
          summary: contentSummary.trim() || undefined,
          call_to_action: contentCallToAction.trim() || undefined,
          asset_requests: splitDraftList(assetRequestsDraft).map((item) => ({ title: item, type: "asset_placeholder" })),
          metadata: { source: "admin_dashboard", phase: "61O", generation_mode: "rag_content_draft" },
        },
        settings,
      );
      setActionState({ data: generated, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedContentDraftId(valueAt(generated, ["id"], ""));
      setContentBody(valueAt(generated, ["content_body"], contentBody));
      setContentSummary(valueAt(generated, ["summary"], contentSummary));
      setSourceMaterialsDraft(draftListText(generated.source_materials));
      setAssetRequestsDraft(draftListText(generated.asset_requests));
      await loadContentDrafts(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation RAG content draft generation unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateOperationContentDraft = async () => {
    if (!selectedOperationId || !selectedContentDraftId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateContentDraft(selectedOperationId, selectedContentDraftId, contentDraftPayload(), settings);
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      setContentBody(valueAt(updated, ["content_body"], contentBody));
      await loadContentDrafts(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation content draft update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateOperationContentDraft = async (draftId: string, action: "ready" | "approve" | "reject" | "archive") => {
    if (!selectedOperationId || !draftId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyContentDraft(selectedOperationId, draftId, "Ready for review from Commercial Ops.", settings)
          : action === "approve"
            ? await commercialOperationsApi.approveContentDraft(selectedOperationId, draftId, "Approved from Commercial Ops.", settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectContentDraft(selectedOperationId, draftId, "Rejected from Commercial Ops.", settings)
              : await commercialOperationsApi.archiveContentDraft(selectedOperationId, draftId, "Archived from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadContentDrafts(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation content draft action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editOperationAssetRequest = (assetRequest: JsonRecord) => {
    const assetRequestId = valueAt(assetRequest, ["id"], "");
    if (!assetRequestId) {
      return;
    }
    setSelectedAssetRequestId(assetRequestId);
    setAssetStepKey(valueAt(assetRequest, ["step_key"], assetStepKey));
    setAssetContentDraftId(valueAt(assetRequest, ["content_draft_id"], ""));
    setAssetChannel(valueAt(assetRequest, ["channel"], assetChannel));
    setAssetType(valueAt(assetRequest, ["asset_type"], assetType));
    setAssetTitle(valueAt(assetRequest, ["title"], assetTitle));
    setAssetPurpose(valueAt(assetRequest, ["purpose"], ""));
    setAssetDimensions(valueAt(assetRequest, ["dimensions"], ""));
    setAssetStyleConstraints(valueAt(assetRequest, ["style_constraints"], ""));
    setAssetPrompt(valueAt(assetRequest, ["generation_prompt"], ""));
    setAssetNegativePrompt(valueAt(assetRequest, ["negative_prompt"], ""));
    setAssetSourceMaterialsDraft(draftListText(assetRequest.source_materials));
    setAssetReadinessChecksDraft(draftListText(assetRequest.readiness_checks));
  };

  const assetRequestPayload = (): JsonRecord => ({
    step_key: assetStepKey.trim() || "content_production",
    content_draft_id: assetContentDraftId || undefined,
    channel: assetChannel.trim() || "newsletter",
    asset_type: assetType,
    title: assetTitle.trim(),
    purpose: assetPurpose.trim() || undefined,
    dimensions: assetDimensions.trim() || undefined,
    style_constraints: assetStyleConstraints.trim() || undefined,
    generation_prompt: assetPrompt.trim() || undefined,
    negative_prompt: assetNegativePrompt.trim() || undefined,
    source_materials: splitDraftList(assetSourceMaterialsDraft),
    readiness_checks: splitDraftList(assetReadinessChecksDraft),
    metadata: { source: "admin_dashboard", phase: "61F" },
  });

  const createOperationAssetRequest = async () => {
    if (!selectedOperationId) {
      setActionState({
        data: null,
        error: assetCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createAssetRequest(selectedOperationId, assetRequestPayload(), settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedAssetRequestId(valueAt(created, ["id"], ""));
      await loadAssetRequests(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation asset request create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const generateOperationAssetRequest = async () => {
    if (!selectedOperationId) {
      setActionState({
        data: null,
        error: assetCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const generated = await commercialOperationsApi.generateAssetRequest(
        selectedOperationId,
        {
          step_key: assetStepKey.trim() || "content_production",
          content_draft_id: assetContentDraftId || undefined,
          channel: assetChannel.trim() || "newsletter",
          asset_type: assetType,
          title: assetTitle.trim() || undefined,
          purpose: assetPurpose.trim() || undefined,
          dimensions: assetDimensions.trim() || undefined,
          style_constraints: assetStyleConstraints.trim() || undefined,
          query: assetRagQuery.trim() || undefined,
          knowledge_collection: valueAt(selectedOperation, ["knowledge_collection"], knowledgeCollection).trim() || undefined,
          search_mode: assetSearchMode,
          negative_prompt: assetNegativePrompt.trim() || undefined,
          readiness_checks: splitDraftList(assetReadinessChecksDraft),
          metadata: { source: "admin_dashboard", phase: "61P", generation_mode: "rag_asset_brief" },
        },
        settings,
      );
      setActionState({ data: generated, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedAssetRequestId(valueAt(generated, ["id"], ""));
      setAssetContentDraftId(valueAt(generated, ["content_draft_id"], assetContentDraftId));
      setAssetPurpose(valueAt(generated, ["purpose"], assetPurpose));
      setAssetStyleConstraints(valueAt(generated, ["style_constraints"], assetStyleConstraints));
      setAssetPrompt(valueAt(generated, ["generation_prompt"], assetPrompt));
      setAssetNegativePrompt(valueAt(generated, ["negative_prompt"], assetNegativePrompt));
      setAssetSourceMaterialsDraft(draftListText(generated.source_materials));
      setAssetReadinessChecksDraft(draftListText(generated.readiness_checks));
      await loadAssetRequests(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation RAG asset request generation unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateOperationAssetRequest = async () => {
    if (!selectedOperationId || !selectedAssetRequestId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateAssetRequest(selectedOperationId, selectedAssetRequestId, assetRequestPayload(), settings);
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadAssetRequests(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation asset request update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateOperationAssetRequest = async (
    assetRequestId: string,
    action: "ready" | "approve" | "reject" | "prepare" | "fail" | "archive",
  ) => {
    if (!selectedOperationId || !assetRequestId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyAssetRequest(selectedOperationId, assetRequestId, "Ready for review from Commercial Ops.", settings)
          : action === "approve"
            ? await commercialOperationsApi.approveAssetRequest(selectedOperationId, assetRequestId, "Approved from Commercial Ops.", settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectAssetRequest(selectedOperationId, assetRequestId, "Rejected from Commercial Ops.", settings)
              : action === "prepare"
                ? await commercialOperationsApi.prepareAssetRequest(selectedOperationId, assetRequestId, "Prepared for future ComfyUI handoff; no job started.", settings)
                : action === "fail"
                  ? await commercialOperationsApi.failAssetRequest(selectedOperationId, assetRequestId, "Failed during request preparation; operator review required.", settings)
                  : await commercialOperationsApi.archiveAssetRequest(selectedOperationId, assetRequestId, "Archived from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadAssetRequests(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation asset request action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editComfyuiHandoff = (handoff: JsonRecord) => {
    const handoffId = valueAt(handoff, ["id"], "");
    if (!handoffId) {
      return;
    }
    setSelectedComfyuiHandoffId(handoffId);
    setComfyuiAssetRequestId(valueAt(handoff, ["asset_request_id"], comfyuiAssetRequestId));
    setComfyuiTitle(valueAt(handoff, ["title"], comfyuiTitle));
    setComfyuiWorkflowName(valueAt(handoff, ["workflow_name"], comfyuiWorkflowName));
    setComfyuiPromptPayloadDraft(JSON.stringify((handoff.prompt_payload as JsonRecord) || {}, null, 2));
    setComfyuiWorkflowPayloadDraft(JSON.stringify((handoff.workflow_payload as JsonRecord) || {}, null, 2));
    setComfyuiReadinessChecksDraft(draftListText(handoff.readiness_checks));
  };

  const comfyuiHandoffPayload = (): JsonRecord => ({
    asset_request_id: comfyuiAssetRequestId,
    title: comfyuiTitle.trim() || undefined,
    workflow_name: comfyuiWorkflowName.trim() || "future_comfyui_handoff",
    prompt_payload: parseJsonRecordDraft(comfyuiPromptPayloadDraft),
    workflow_payload: parseJsonRecordDraft(comfyuiWorkflowPayloadDraft),
    readiness_checks: splitDraftList(comfyuiReadinessChecksDraft),
    metadata: { source: "admin_dashboard", phase: "61Q", execution_mode: "metadata_only" },
  });

  const createComfyuiHandoff = async () => {
    if (!selectedOperationId) {
      setActionState({
        data: null,
        error: comfyuiCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createComfyuiHandoff(selectedOperationId, comfyuiHandoffPayload(), settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedComfyuiHandoffId(valueAt(created, ["id"], ""));
      await loadComfyuiHandoffs(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI handoff create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateComfyuiHandoff = async () => {
    if (!selectedOperationId || !selectedComfyuiHandoffId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateComfyuiHandoff(
        selectedOperationId,
        selectedComfyuiHandoffId,
        comfyuiHandoffPayload(),
        settings,
      );
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiHandoffs(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI handoff update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateComfyuiHandoff = async (
    handoffId: string,
    action: "ready" | "approve" | "reject" | "prepare" | "fail" | "archive",
  ) => {
    if (!selectedOperationId || !handoffId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyComfyuiHandoff(selectedOperationId, handoffId, "Ready for review from Commercial Ops.", settings)
          : action === "approve"
            ? await commercialOperationsApi.approveComfyuiHandoff(selectedOperationId, handoffId, "Approved from Commercial Ops.", settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectComfyuiHandoff(selectedOperationId, handoffId, "Rejected from Commercial Ops.", settings)
              : action === "prepare"
                ? await commercialOperationsApi.prepareComfyuiHandoff(selectedOperationId, handoffId, "Prepared for future guarded ComfyUI adapter; no job submitted.", settings)
                : action === "fail"
                  ? await commercialOperationsApi.failComfyuiHandoff(selectedOperationId, handoffId, "Failed during handoff preparation; operator review required.", settings)
                  : await commercialOperationsApi.archiveComfyuiHandoff(selectedOperationId, handoffId, "Archived from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiHandoffs(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI handoff action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editComfyuiPreflight = (preflight: JsonRecord) => {
    const preflightId = valueAt(preflight, ["id"], "");
    if (!preflightId) {
      return;
    }
    setSelectedComfyuiPreflightId(preflightId);
    setComfyuiPreflightHandoffId(valueAt(preflight, ["handoff_id"], comfyuiPreflightHandoffId));
    setComfyuiPreflightAdapterConfigId(valueAt(preflight, ["adapter_config_id"], comfyuiPreflightAdapterConfigId));
    setComfyuiPreflightTitle(valueAt(preflight, ["title"], comfyuiPreflightTitle));
    setComfyuiPreflightTargetUrl(valueAt(preflight, ["target_url"], comfyuiPreflightTargetUrl));
    setComfyuiPreflightQueueName(valueAt(preflight, ["queue_name"], comfyuiPreflightQueueName));
    setComfyuiPreflightWorkflowName(valueAt(preflight, ["workflow_name"], comfyuiPreflightWorkflowName));
    setComfyuiPreflightModelRefsDraft(draftListText(preflight.model_refs));
    setComfyuiPreflightAdapterConfigDraft(JSON.stringify((preflight.adapter_config as JsonRecord) || {}, null, 2));
    setComfyuiPreflightCheckItemsDraft(JSON.stringify((preflight.check_items as JsonRecord[]) || [], null, 2));
  };

  const comfyuiPreflightPayload = (): JsonRecord => ({
    adapter_config_id: comfyuiPreflightAdapterConfigId || undefined,
    title: comfyuiPreflightTitle.trim() || undefined,
    target_url: comfyuiPreflightTargetUrl.trim() || undefined,
    queue_name: comfyuiPreflightQueueName.trim() || undefined,
    workflow_name: comfyuiPreflightWorkflowName.trim() || "future_comfyui_handoff",
    model_refs: splitDraftList(comfyuiPreflightModelRefsDraft),
    adapter_config: parseJsonRecordDraft(comfyuiPreflightAdapterConfigDraft),
    check_items: parseJsonArrayDraft(comfyuiPreflightCheckItemsDraft),
    metadata: { source: "admin_dashboard", phase: "61R", execution_mode: "metadata_only" },
  });

  const createComfyuiPreflight = async () => {
    if (!selectedOperationId || !comfyuiPreflightHandoffId) {
      setActionState({
        data: null,
        error: comfyuiPreflightCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createComfyuiPreflight(
        selectedOperationId,
        comfyuiPreflightHandoffId,
        comfyuiPreflightPayload(),
        settings,
      );
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedComfyuiPreflightId(valueAt(created, ["id"], ""));
      await loadComfyuiPreflights(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI preflight create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateComfyuiPreflight = async () => {
    if (!selectedOperationId || !selectedComfyuiPreflightId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateComfyuiPreflight(
        selectedOperationId,
        selectedComfyuiPreflightId,
        comfyuiPreflightPayload(),
        settings,
      );
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiPreflights(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI preflight update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateComfyuiPreflight = async (preflightId: string, action: "check" | "fail" | "archive") => {
    if (!selectedOperationId || !preflightId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "check"
          ? await commercialOperationsApi.checkComfyuiPreflight(selectedOperationId, preflightId, settings)
          : action === "fail"
            ? await commercialOperationsApi.failComfyuiPreflight(selectedOperationId, preflightId, "Failed during ComfyUI preflight; operator review required.", settings)
            : await commercialOperationsApi.archiveComfyuiPreflight(selectedOperationId, preflightId, settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiPreflights(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI preflight action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editComfyuiAdapterConfig = (config: JsonRecord) => {
    const configId = valueAt(config, ["id"], "");
    if (!configId) {
      return;
    }
    setSelectedComfyuiAdapterConfigId(configId);
    setComfyuiAdapterTitle(valueAt(config, ["title"], comfyuiAdapterTitle));
    setComfyuiAdapterTargetUrl(valueAt(config, ["target_url"], comfyuiAdapterTargetUrl));
    setComfyuiAdapterAuthMode(valueAt(config, ["auth_mode"], "none"));
    setComfyuiAdapterSecretRef(valueAt(config, ["secret_ref"], ""));
    setComfyuiAdapterQueueName(valueAt(config, ["queue_name"], comfyuiAdapterQueueName));
    setComfyuiAdapterDefaultWorkflow(valueAt(config, ["default_workflow_name"], comfyuiAdapterDefaultWorkflow));
    setComfyuiAdapterAllowedWorkflowsDraft(draftListText(config.allowed_workflows));
    setComfyuiAdapterModelInventoryDraft(JSON.stringify((config.model_inventory as JsonRecord[]) || [], null, 2));
    setComfyuiAdapterRuntimeLimitsDraft(JSON.stringify((config.runtime_limits as JsonRecord) || {}, null, 2));
    setComfyuiAdapterMaintenanceNotes(valueAt(config, ["maintenance_notes"], ""));
    setComfyuiAdapterValidationChecksDraft(JSON.stringify((config.validation_checks as JsonRecord[]) || [], null, 2));
  };

  const comfyuiAdapterConfigPayload = (): JsonRecord => ({
    title: comfyuiAdapterTitle.trim() || "ComfyUI adapter config",
    target_url: comfyuiAdapterTargetUrl.trim() || undefined,
    auth_mode: comfyuiAdapterAuthMode,
    secret_ref: comfyuiAdapterSecretRef.trim() || undefined,
    queue_name: comfyuiAdapterQueueName.trim() || undefined,
    default_workflow_name: comfyuiAdapterDefaultWorkflow.trim() || undefined,
    allowed_workflows: splitDraftList(comfyuiAdapterAllowedWorkflowsDraft),
    model_inventory: parseJsonArrayDraft(comfyuiAdapterModelInventoryDraft),
    runtime_limits: parseJsonRecordDraft(comfyuiAdapterRuntimeLimitsDraft),
    maintenance_notes: comfyuiAdapterMaintenanceNotes.trim() || undefined,
    validation_checks: parseJsonArrayDraft(comfyuiAdapterValidationChecksDraft),
    metadata: { source: "admin_dashboard", phase: "61S", execution_mode: "metadata_only" },
  });

  const createComfyuiAdapterConfig = async () => {
    if (!selectedOperationId) {
      setActionState({
        data: null,
        error: comfyuiAdapterCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createComfyuiAdapterConfig(selectedOperationId, comfyuiAdapterConfigPayload(), settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedComfyuiAdapterConfigId(valueAt(created, ["id"], ""));
      await loadComfyuiAdapterConfigs(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI adapter config create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateComfyuiAdapterConfig = async () => {
    if (!selectedOperationId || !selectedComfyuiAdapterConfigId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateComfyuiAdapterConfig(
        selectedOperationId,
        selectedComfyuiAdapterConfigId,
        comfyuiAdapterConfigPayload(),
        settings,
      );
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiAdapterConfigs(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI adapter config update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateComfyuiAdapterConfig = async (configId: string, action: "validate" | "fail" | "archive") => {
    if (!selectedOperationId || !configId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "validate"
          ? await commercialOperationsApi.validateComfyuiAdapterConfig(selectedOperationId, configId, settings)
          : action === "fail"
            ? await commercialOperationsApi.failComfyuiAdapterConfig(selectedOperationId, configId, "Failed during adapter config review; maintainer action required.", settings)
            : await commercialOperationsApi.archiveComfyuiAdapterConfig(selectedOperationId, configId, settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiAdapterConfigs(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI adapter config action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editComfyuiJobRequest = (jobRequest: JsonRecord) => {
    const jobRequestId = valueAt(jobRequest, ["id"], "");
    if (!jobRequestId) {
      return;
    }
    setSelectedComfyuiJobRequestId(jobRequestId);
    setComfyuiJobPreflightId(valueAt(jobRequest, ["preflight_id"], comfyuiJobPreflightId));
    setComfyuiJobTitle(valueAt(jobRequest, ["title"], comfyuiJobTitle));
    setComfyuiJobPriority(valueAt(jobRequest, ["priority"], "normal") as "low" | "normal" | "high");
    setComfyuiJobRuntimePayloadDraft(JSON.stringify((jobRequest.runtime_payload as JsonRecord) || {}, null, 2));
    setComfyuiJobSafetyChecksDraft(JSON.stringify((jobRequest.safety_checks as JsonRecord[]) || [], null, 2));
    setComfyuiJobOutputsDraft(draftListText(jobRequest.output_expectations));
    setComfyuiJobRecoveryDraft(JSON.stringify((jobRequest.recovery_plan as JsonRecord) || {}, null, 2));
  };

  const comfyuiJobRequestPayload = (): JsonRecord => ({
    title: comfyuiJobTitle.trim() || "ComfyUI job request",
    priority: comfyuiJobPriority,
    runtime_payload: parseJsonRecordDraft(comfyuiJobRuntimePayloadDraft),
    safety_checks: parseJsonArrayDraft(comfyuiJobSafetyChecksDraft),
    output_expectations: splitDraftList(comfyuiJobOutputsDraft),
    recovery_plan: parseJsonRecordDraft(comfyuiJobRecoveryDraft),
    metadata: { source: "admin_dashboard", phase: "61T", execution_mode: "metadata_only" },
  });

  const createComfyuiJobRequest = async () => {
    if (!selectedOperationId || !comfyuiJobPreflightId) {
      setActionState({
        data: null,
        error: comfyuiJobCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createComfyuiJobRequest(
        selectedOperationId,
        comfyuiJobPreflightId,
        comfyuiJobRequestPayload(),
        settings,
      );
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedComfyuiJobRequestId(valueAt(created, ["id"], ""));
      await loadComfyuiJobRequests(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI job request create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateComfyuiJobRequest = async () => {
    if (!selectedOperationId || !selectedComfyuiJobRequestId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateComfyuiJobRequest(
        selectedOperationId,
        selectedComfyuiJobRequestId,
        comfyuiJobRequestPayload(),
        settings,
      );
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiJobRequests(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI job request update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateComfyuiJobRequest = async (
    jobRequestId: string,
    action: "ready" | "approve" | "reject" | "queue" | "fail" | "cancel" | "archive",
  ) => {
    if (!selectedOperationId || !jobRequestId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyComfyuiJobRequest(selectedOperationId, jobRequestId, settings)
          : action === "approve"
            ? await commercialOperationsApi.approveComfyuiJobRequest(selectedOperationId, jobRequestId, settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectComfyuiJobRequest(selectedOperationId, jobRequestId, settings)
              : action === "queue"
                ? await commercialOperationsApi.queueComfyuiJobRequest(selectedOperationId, jobRequestId, settings)
                : action === "fail"
                  ? await commercialOperationsApi.failComfyuiJobRequest(selectedOperationId, jobRequestId, "Failed during ComfyUI job request review; operator action required.", settings)
                  : action === "cancel"
                    ? await commercialOperationsApi.cancelComfyuiJobRequest(selectedOperationId, jobRequestId, settings)
                    : await commercialOperationsApi.archiveComfyuiJobRequest(selectedOperationId, jobRequestId, settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiJobRequests(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI job request action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editComfyuiExecutionPlan = (plan: JsonRecord) => {
    const executionPlanId = valueAt(plan, ["id"], "");
    if (!executionPlanId) {
      return;
    }
    setSelectedComfyuiExecutionPlanId(executionPlanId);
    setComfyuiExecutionJobRequestId(valueAt(plan, ["job_request_id"], comfyuiExecutionJobRequestId));
    setComfyuiExecutionTitle(valueAt(plan, ["title"], comfyuiExecutionTitle));
    setComfyuiExecutionPriority(valueAt(plan, ["priority"], "normal") as "low" | "normal" | "high");
    setComfyuiExecutionStepsDraft(JSON.stringify((plan.execution_steps as JsonRecord[]) || [], null, 2));
    setComfyuiExecutionChecksDraft(JSON.stringify((plan.simulation_checks as JsonRecord[]) || [], null, 2));
    setComfyuiExecutionChecklistDraft(draftListText(plan.operator_checklist));
    setComfyuiExecutionSimulationPayloadDraft(JSON.stringify((plan.simulation_payload as JsonRecord) || {}, null, 2));
    setComfyuiExecutionRollbackDraft(JSON.stringify((plan.rollback_plan as JsonRecord) || {}, null, 2));
  };

  const comfyuiExecutionPlanPayload = (): JsonRecord => ({
    title: comfyuiExecutionTitle.trim() || "ComfyUI execution plan",
    priority: comfyuiExecutionPriority,
    execution_steps: parseJsonArrayDraft(comfyuiExecutionStepsDraft),
    simulation_checks: parseJsonArrayDraft(comfyuiExecutionChecksDraft),
    operator_checklist: splitDraftList(comfyuiExecutionChecklistDraft),
    simulation_payload: parseJsonRecordDraft(comfyuiExecutionSimulationPayloadDraft),
    rollback_plan: parseJsonRecordDraft(comfyuiExecutionRollbackDraft),
    metadata: { source: "admin_dashboard", phase: "61U", execution_mode: "metadata_only" },
  });

  const createComfyuiExecutionPlan = async () => {
    if (!selectedOperationId || !comfyuiExecutionJobRequestId) {
      setActionState({
        data: null,
        error: comfyuiExecutionCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createComfyuiExecutionPlan(
        selectedOperationId,
        comfyuiExecutionJobRequestId,
        comfyuiExecutionPlanPayload(),
        settings,
      );
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedComfyuiExecutionPlanId(valueAt(created, ["id"], ""));
      await loadComfyuiExecutionPlans(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI execution plan create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateComfyuiExecutionPlan = async () => {
    if (!selectedOperationId || !selectedComfyuiExecutionPlanId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateComfyuiExecutionPlan(
        selectedOperationId,
        selectedComfyuiExecutionPlanId,
        comfyuiExecutionPlanPayload(),
        settings,
      );
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiExecutionPlans(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI execution plan update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateComfyuiExecutionPlan = async (
    executionPlanId: string,
    action: "ready" | "approve" | "reject" | "simulate" | "fail" | "cancel" | "archive",
  ) => {
    if (!selectedOperationId || !executionPlanId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyComfyuiExecutionPlan(selectedOperationId, executionPlanId, settings)
          : action === "approve"
            ? await commercialOperationsApi.approveComfyuiExecutionPlan(selectedOperationId, executionPlanId, settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectComfyuiExecutionPlan(selectedOperationId, executionPlanId, settings)
              : action === "simulate"
                ? await commercialOperationsApi.simulateComfyuiExecutionPlan(selectedOperationId, executionPlanId, settings)
                : action === "fail"
                  ? await commercialOperationsApi.failComfyuiExecutionPlan(selectedOperationId, executionPlanId, "Failed during metadata-only ComfyUI execution simulation; operator action required.", settings)
                  : action === "cancel"
                    ? await commercialOperationsApi.cancelComfyuiExecutionPlan(selectedOperationId, executionPlanId, settings)
                    : await commercialOperationsApi.archiveComfyuiExecutionPlan(selectedOperationId, executionPlanId, settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiExecutionPlans(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI execution plan action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editComfyuiConnectionProbe = (probe: JsonRecord) => {
    const connectionProbeId = valueAt(probe, ["id"], "");
    if (!connectionProbeId) {
      return;
    }
    setSelectedComfyuiConnectionProbeId(connectionProbeId);
    setComfyuiProbeExecutionPlanId(valueAt(probe, ["execution_plan_id"], comfyuiProbeExecutionPlanId));
    setComfyuiProbeTitle(valueAt(probe, ["title"], comfyuiProbeTitle));
    setComfyuiProbeMode(valueAt(probe, ["probe_mode"], "metadata_only"));
    setComfyuiProbeHealthEndpoint(valueAt(probe, ["health_endpoint"], "/system_stats"));
    setComfyuiProbeQueueEndpoint(valueAt(probe, ["queue_endpoint"], "/queue"));
    setComfyuiProbeRoutesDraft(draftListText(probe.expected_routes));
    setComfyuiProbeChecksDraft(JSON.stringify((probe.readiness_checks as JsonRecord[]) || [], null, 2));
    setComfyuiProbePayloadDraft(JSON.stringify((probe.probe_payload as JsonRecord) || {}, null, 2));
    setComfyuiProbeHealthSnapshotDraft(JSON.stringify((probe.health_snapshot as JsonRecord) || {}, null, 2));
    setComfyuiProbeQueueSnapshotDraft(JSON.stringify((probe.queue_snapshot as JsonRecord) || {}, null, 2));
    setComfyuiProbeSchemaDraft(JSON.stringify((probe.response_schema as JsonRecord) || {}, null, 2));
  };

  const comfyuiConnectionProbePayload = (): JsonRecord => ({
    title: comfyuiProbeTitle.trim() || "ComfyUI connection probe",
    probe_mode: comfyuiProbeMode.trim() || "metadata_only",
    health_endpoint: comfyuiProbeHealthEndpoint.trim() || "/system_stats",
    queue_endpoint: comfyuiProbeQueueEndpoint.trim() || "/queue",
    expected_routes: splitDraftList(comfyuiProbeRoutesDraft),
    readiness_checks: parseJsonArrayDraft(comfyuiProbeChecksDraft),
    probe_payload: parseJsonRecordDraft(comfyuiProbePayloadDraft),
    health_snapshot: parseJsonRecordDraft(comfyuiProbeHealthSnapshotDraft),
    queue_snapshot: parseJsonRecordDraft(comfyuiProbeQueueSnapshotDraft),
    response_schema: parseJsonRecordDraft(comfyuiProbeSchemaDraft),
    metadata: { source: "admin_dashboard", phase: "61V", probe_mode: "metadata_only" },
  });

  const createComfyuiConnectionProbe = async () => {
    if (!selectedOperationId || !comfyuiProbeExecutionPlanId) {
      setActionState({
        data: null,
        error: comfyuiProbeCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createComfyuiConnectionProbe(
        selectedOperationId,
        comfyuiProbeExecutionPlanId,
        comfyuiConnectionProbePayload(),
        settings,
      );
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedComfyuiConnectionProbeId(valueAt(created, ["id"], ""));
      await loadComfyuiConnectionProbes(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI connection probe create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateComfyuiConnectionProbe = async () => {
    if (!selectedOperationId || !selectedComfyuiConnectionProbeId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateComfyuiConnectionProbe(
        selectedOperationId,
        selectedComfyuiConnectionProbeId,
        comfyuiConnectionProbePayload(),
        settings,
      );
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiConnectionProbes(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI connection probe update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateComfyuiConnectionProbe = async (
    connectionProbeId: string,
    action: "ready" | "approve" | "reject" | "probe" | "fail" | "cancel" | "archive",
  ) => {
    if (!selectedOperationId || !connectionProbeId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyComfyuiConnectionProbe(selectedOperationId, connectionProbeId, settings)
          : action === "approve"
            ? await commercialOperationsApi.approveComfyuiConnectionProbe(selectedOperationId, connectionProbeId, settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectComfyuiConnectionProbe(selectedOperationId, connectionProbeId, settings)
              : action === "probe"
                ? await commercialOperationsApi.probeComfyuiConnectionProbe(selectedOperationId, connectionProbeId, settings)
                : action === "fail"
                  ? await commercialOperationsApi.failComfyuiConnectionProbe(selectedOperationId, connectionProbeId, "Failed during metadata-only ComfyUI connection probe review; maintainer action required.", settings)
                  : action === "cancel"
                    ? await commercialOperationsApi.cancelComfyuiConnectionProbe(selectedOperationId, connectionProbeId, settings)
                    : await commercialOperationsApi.archiveComfyuiConnectionProbe(selectedOperationId, connectionProbeId, settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiConnectionProbes(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI connection probe action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editComfyuiAdapterDispatch = (dispatch: JsonRecord) => {
    const adapterDispatchId = valueAt(dispatch, ["id"], "");
    if (!adapterDispatchId) {
      return;
    }
    setSelectedComfyuiAdapterDispatchId(adapterDispatchId);
    setComfyuiDispatchConnectionProbeId(valueAt(dispatch, ["connection_probe_id"], comfyuiDispatchConnectionProbeId));
    setComfyuiDispatchTitle(valueAt(dispatch, ["title"], comfyuiDispatchTitle));
    setComfyuiDispatchMode(valueAt(dispatch, ["dispatch_mode"], "metadata_only"));
    setComfyuiDispatchPromptPayloadDraft(JSON.stringify((dispatch.prompt_payload as JsonRecord) || {}, null, 2));
    setComfyuiDispatchWorkflowPayloadDraft(JSON.stringify((dispatch.workflow_payload as JsonRecord) || {}, null, 2));
    setComfyuiDispatchQueuePayloadDraft(JSON.stringify((dispatch.queue_payload as JsonRecord) || {}, null, 2));
    setComfyuiDispatchPayloadDraft(JSON.stringify((dispatch.dispatch_payload as JsonRecord) || {}, null, 2));
    setComfyuiDispatchGuardrailsDraft(JSON.stringify((dispatch.guardrails as JsonRecord[]) || [], null, 2));
    setComfyuiDispatchChecklistDraft(draftListText(dispatch.operator_checklist));
    setComfyuiDispatchRetryDraft(JSON.stringify((dispatch.retry_policy as JsonRecord) || {}, null, 2));
    setComfyuiDispatchRecoveryDraft(JSON.stringify((dispatch.recovery_plan as JsonRecord) || {}, null, 2));
  };

  const comfyuiAdapterDispatchPayload = (): JsonRecord => ({
    title: comfyuiDispatchTitle.trim() || "ComfyUI adapter dispatch",
    dispatch_mode: comfyuiDispatchMode.trim() || "metadata_only",
    prompt_payload: parseJsonRecordDraft(comfyuiDispatchPromptPayloadDraft),
    workflow_payload: parseJsonRecordDraft(comfyuiDispatchWorkflowPayloadDraft),
    queue_payload: parseJsonRecordDraft(comfyuiDispatchQueuePayloadDraft),
    dispatch_payload: parseJsonRecordDraft(comfyuiDispatchPayloadDraft),
    guardrails: parseJsonArrayDraft(comfyuiDispatchGuardrailsDraft),
    operator_checklist: splitDraftList(comfyuiDispatchChecklistDraft),
    retry_policy: parseJsonRecordDraft(comfyuiDispatchRetryDraft),
    recovery_plan: parseJsonRecordDraft(comfyuiDispatchRecoveryDraft),
    metadata: { source: "admin_dashboard", phase: "61W", dispatch_mode: "metadata_only" },
  });

  const createComfyuiAdapterDispatch = async () => {
    if (!selectedOperationId || !comfyuiDispatchConnectionProbeId) {
      setActionState({
        data: null,
        error: comfyuiDispatchCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createComfyuiAdapterDispatch(
        selectedOperationId,
        comfyuiDispatchConnectionProbeId,
        comfyuiAdapterDispatchPayload(),
        settings,
      );
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedComfyuiAdapterDispatchId(valueAt(created, ["id"], ""));
      await loadComfyuiAdapterDispatches(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI adapter dispatch create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateComfyuiAdapterDispatch = async () => {
    if (!selectedOperationId || !selectedComfyuiAdapterDispatchId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateComfyuiAdapterDispatch(
        selectedOperationId,
        selectedComfyuiAdapterDispatchId,
        comfyuiAdapterDispatchPayload(),
        settings,
      );
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiAdapterDispatches(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI adapter dispatch update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateComfyuiAdapterDispatch = async (
    adapterDispatchId: string,
    action: "ready" | "approve" | "reject" | "dispatch" | "fail" | "cancel" | "archive",
  ) => {
    if (!selectedOperationId || !adapterDispatchId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyComfyuiAdapterDispatch(selectedOperationId, adapterDispatchId, settings)
          : action === "approve"
            ? await commercialOperationsApi.approveComfyuiAdapterDispatch(selectedOperationId, adapterDispatchId, settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectComfyuiAdapterDispatch(selectedOperationId, adapterDispatchId, settings)
              : action === "dispatch"
                ? await commercialOperationsApi.dispatchComfyuiAdapterDispatch(selectedOperationId, adapterDispatchId, settings)
                : action === "fail"
                  ? await commercialOperationsApi.failComfyuiAdapterDispatch(selectedOperationId, adapterDispatchId, "Failed during metadata-only ComfyUI adapter dispatch review; maintainer action required.", settings)
                  : action === "cancel"
                    ? await commercialOperationsApi.cancelComfyuiAdapterDispatch(selectedOperationId, adapterDispatchId, settings)
                    : await commercialOperationsApi.archiveComfyuiAdapterDispatch(selectedOperationId, adapterDispatchId, settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadComfyuiAdapterDispatches(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation ComfyUI adapter dispatch action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editOperationDeliverable = (deliverable: JsonRecord) => {
    const deliverableId = valueAt(deliverable, ["id"], "");
    if (!deliverableId) {
      return;
    }
    setSelectedDeliverableId(deliverableId);
    setDeliverableContentDraftId(valueAt(deliverable, ["content_draft_id"], deliverableContentDraftId));
    setDeliverableAssetRequestIdsDraft(draftListText(deliverable.asset_request_ids));
    setDeliverableType(valueAt(deliverable, ["deliverable_type"], deliverableType));
    setDeliverableTitle(valueAt(deliverable, ["title"], deliverableTitle));
    setDeliverableSummary(valueAt(deliverable, ["summary"], ""));
    setDeliverableNotes(valueAt(deliverable, ["delivery_notes"], ""));
    setDeliverableQualityChecksDraft(draftListText(deliverable.quality_checks));
  };

  const deliverablePayload = (): JsonRecord => {
    const explicitAssetIds = splitDraftList(deliverableAssetRequestIdsDraft);
    const fallbackAssetIds = assetRequests
      .filter((assetRequest) => {
        const status = valueAt(assetRequest, ["request_status"], "");
        const linkedDraft = valueAt(assetRequest, ["content_draft_id"], "");
        return ["approved", "prepared"].includes(status) && (!deliverableContentDraftId || !linkedDraft || linkedDraft === deliverableContentDraftId);
      })
      .map((assetRequest) => valueAt(assetRequest, ["id"], ""))
      .filter(Boolean);
    return {
      step_key: "content_production",
      content_draft_id: deliverableContentDraftId,
      asset_request_ids: explicitAssetIds.length ? explicitAssetIds : fallbackAssetIds,
      deliverable_type: deliverableType,
      title: deliverableTitle.trim(),
      summary: deliverableSummary.trim() || undefined,
      delivery_notes: deliverableNotes.trim() || undefined,
      quality_checks: splitDraftList(deliverableQualityChecksDraft),
      metadata: { source: "admin_dashboard", phase: "61G" },
    };
  };

  const createOperationDeliverable = async () => {
    if (!selectedOperationId) {
      setActionState({
        data: null,
        error: deliverableCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createDeliverable(selectedOperationId, deliverablePayload(), settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedDeliverableId(valueAt(created, ["id"], ""));
      await loadDeliverables(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation deliverable create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateOperationDeliverable = async () => {
    if (!selectedOperationId || !selectedDeliverableId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateDeliverable(selectedOperationId, selectedDeliverableId, deliverablePayload(), settings);
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadDeliverables(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation deliverable update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateOperationDeliverable = async (
    deliverableId: string,
    action: "ready" | "approve" | "reject" | "package" | "fail" | "archive",
  ) => {
    if (!selectedOperationId || !deliverableId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyDeliverable(selectedOperationId, deliverableId, "Ready for review from Commercial Ops.", settings)
          : action === "approve"
            ? await commercialOperationsApi.approveDeliverable(selectedOperationId, deliverableId, "Approved from Commercial Ops.", settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectDeliverable(selectedOperationId, deliverableId, "Rejected from Commercial Ops.", settings)
              : action === "package"
                ? await commercialOperationsApi.packageDeliverable(selectedOperationId, deliverableId, "Packaged for Output Library handoff; no publishing executed.", settings)
                : action === "fail"
                  ? await commercialOperationsApi.failDeliverable(selectedOperationId, deliverableId, "Failed during deliverable packaging; operator review required.", settings)
                  : await commercialOperationsApi.archiveDeliverable(selectedOperationId, deliverableId, "Archived from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadDeliverables(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation deliverable action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editOperationEvidenceSnapshot = (snapshot: JsonRecord) => {
    const snapshotId = valueAt(snapshot, ["id"], "");
    if (!snapshotId) {
      return;
    }
    setSelectedEvidenceSnapshotId(snapshotId);
    setEvidenceDeliverableId(valueAt(snapshot, ["deliverable_id"], evidenceDeliverableId));
    setEvidenceType(valueAt(snapshot, ["evidence_type"], evidenceType));
    setEvidenceTitle(valueAt(snapshot, ["title"], evidenceTitle));
    setEvidenceCollection(valueAt(snapshot, ["knowledge_collection"], ""));
    setEvidenceQuery(valueAt(snapshot, ["query"], ""));
    setEvidenceSearchMode(valueAt(snapshot, ["snapshot_payload", "search_mode"], evidenceSearchMode));
    setEvidenceSummary(valueAt(snapshot, ["evidence_summary"], ""));
    setEvidenceRelevance(valueAt(snapshot, ["relevance_notes"], ""));
    setEvidenceDocumentIdsDraft(draftListText(snapshot.source_document_ids));
    setEvidenceLinksDraft(draftListText(snapshot.source_links));
    setEvidenceItemsDraft(draftListText(snapshot.evidence_items));
    setEvidenceCoverageDraft(draftListText(snapshot.coverage_checks));
  };

  const evidenceSnapshotPayload = (): JsonRecord => ({
    deliverable_id: evidenceDeliverableId,
    evidence_type: evidenceType,
    title: evidenceTitle.trim(),
    knowledge_collection: evidenceCollection.trim() || undefined,
    query: evidenceQuery.trim() || undefined,
    evidence_summary: evidenceSummary.trim() || undefined,
    relevance_notes: evidenceRelevance.trim() || undefined,
    source_document_ids: splitDraftList(evidenceDocumentIdsDraft),
    source_links: splitDraftList(evidenceLinksDraft).map((item) => ({ title: item, target: item })),
    evidence_items: splitDraftList(evidenceItemsDraft).map((item) => ({ title: item, summary: item })),
    coverage_checks: splitDraftList(evidenceCoverageDraft),
    snapshot_payload: { source: "admin_dashboard", phase: "61N" },
    metadata: { source: "admin_dashboard", phase: "61N" },
  });

  const createOperationEvidenceSnapshot = async () => {
    if (!selectedOperationId || !evidenceDeliverableId) {
      setActionState({
        data: null,
        error: evidenceCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createEvidenceSnapshot(selectedOperationId, evidenceSnapshotPayload(), settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedEvidenceSnapshotId(valueAt(created, ["id"], ""));
      await loadEvidenceSnapshots(selectedOperationId);
      await loadDeliverables(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation evidence snapshot create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const generateOperationEvidenceSnapshot = async () => {
    if (!selectedOperationId || !evidenceDeliverableId) {
      setActionState({
        data: null,
        error: evidenceCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const generated = await commercialOperationsApi.generateEvidenceSnapshot(
        selectedOperationId,
        {
          deliverable_id: evidenceDeliverableId,
          title: evidenceTitle.trim() || undefined,
          knowledge_collection: evidenceCollection.trim() || undefined,
          query: evidenceQuery.trim() || undefined,
          search_mode: evidenceSearchMode,
          evidence_summary: evidenceSummary.trim() || undefined,
          relevance_notes: evidenceRelevance.trim() || undefined,
          coverage_checks: splitDraftList(evidenceCoverageDraft),
          metadata: { source: "admin_dashboard", phase: "61N" },
        },
        settings,
      );
      setActionState({ data: generated, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedEvidenceSnapshotId(valueAt(generated, ["id"], ""));
      setEvidenceDocumentIdsDraft(draftListText(generated.source_document_ids));
      setEvidenceLinksDraft(draftListText(generated.source_links));
      setEvidenceItemsDraft(draftListText(generated.evidence_items));
      setEvidenceCoverageDraft(draftListText(generated.coverage_checks));
      await loadEvidenceSnapshots(selectedOperationId);
      await loadDeliverables(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation RAG evidence generation unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateOperationEvidenceSnapshot = async () => {
    if (!selectedOperationId || !selectedEvidenceSnapshotId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateEvidenceSnapshot(selectedOperationId, selectedEvidenceSnapshotId, evidenceSnapshotPayload(), settings);
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadEvidenceSnapshots(selectedOperationId);
      await loadDeliverables(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation evidence snapshot update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateOperationEvidenceSnapshot = async (
    snapshotId: string,
    action: "ready" | "approve" | "reject" | "archive",
  ) => {
    if (!selectedOperationId || !snapshotId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyEvidenceSnapshot(selectedOperationId, snapshotId, "Ready for review from Commercial Ops.", settings)
          : action === "approve"
            ? await commercialOperationsApi.approveEvidenceSnapshot(selectedOperationId, snapshotId, "Approved from Commercial Ops.", settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectEvidenceSnapshot(selectedOperationId, snapshotId, "Rejected from Commercial Ops.", settings)
              : await commercialOperationsApi.archiveEvidenceSnapshot(selectedOperationId, snapshotId, "Archived from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadEvidenceSnapshots(selectedOperationId);
      await loadDeliverables(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation evidence snapshot action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editOperationExecutionRequest = (executionRequest: JsonRecord) => {
    const executionRequestId = valueAt(executionRequest, ["id"], "");
    if (!executionRequestId) {
      return;
    }
    setSelectedExecutionRequestId(executionRequestId);
    setExecutionDeliverableId(valueAt(executionRequest, ["deliverable_id"], executionDeliverableId));
    setExecutionRequestType(valueAt(executionRequest, ["execution_type"], executionRequestType));
    setExecutionRequestMode(valueAt(executionRequest, ["execution_mode"], executionRequestMode));
    setExecutionRequestTitle(valueAt(executionRequest, ["title"], executionRequestTitle));
    setExecutionRequestTarget(valueAt(executionRequest, ["execution_target"], ""));
    setExecutionRequestInputSummary(valueAt(executionRequest, ["input_summary"], ""));
    setExecutionRunbookDraft(draftListText(executionRequest.runbook));
    setExecutionReadinessDraft(draftListText(executionRequest.readiness_checks));
    setExecutionOutputsDraft(draftListText(executionRequest.expected_outputs));
    setExecutionEvidenceSnapshotIdsDraft(draftListText(executionRequest.evidence_snapshot_ids));
    setExecutionChecklistDraft(draftListText(executionRequest.operator_checklist));
  };

  const executionRequestPayload = (): JsonRecord => ({
    deliverable_id: executionDeliverableId,
    execution_type: executionRequestType,
    execution_mode: executionRequestMode,
    title: executionRequestTitle.trim(),
    execution_target: executionRequestTarget.trim() || undefined,
    input_summary: executionRequestInputSummary.trim() || undefined,
    runbook: splitDraftList(executionRunbookDraft).map((item) => ({ step: item })),
    readiness_checks: splitDraftList(executionReadinessDraft),
    expected_outputs: splitDraftList(executionOutputsDraft),
    evidence_snapshot_ids: splitDraftList(executionEvidenceSnapshotIdsDraft),
    operator_checklist: splitDraftList(executionChecklistDraft).map((item) => ({ item })),
    metadata: { source: "admin_dashboard", phase: "61M" },
  });

  const createOperationExecutionRequest = async () => {
    if (!selectedOperationId || !executionDeliverableId) {
      setActionState({
        data: null,
        error: executionRequestCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createExecutionRequest(selectedOperationId, executionRequestPayload(), settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedExecutionRequestId(valueAt(created, ["id"], ""));
      await loadExecutionRequests(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation execution request create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateOperationExecutionRequest = async () => {
    if (!selectedOperationId || !selectedExecutionRequestId) {
      return;
    }
    const { deliverable_id: _deliverableId, ...payload } = executionRequestPayload();
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateExecutionRequest(selectedOperationId, selectedExecutionRequestId, payload, settings);
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadExecutionRequests(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation execution request update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateOperationExecutionRequest = async (
    executionRequestId: string,
    action: "ready" | "approve" | "reject" | "prepare" | "fail" | "cancel" | "archive",
  ) => {
    if (!selectedOperationId || !executionRequestId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyExecutionRequest(selectedOperationId, executionRequestId, "Ready for review from Commercial Ops.", settings)
          : action === "approve"
            ? await commercialOperationsApi.approveExecutionRequest(selectedOperationId, executionRequestId, "Approved as metadata-only execution request.", settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectExecutionRequest(selectedOperationId, executionRequestId, "Rejected from Commercial Ops.", settings)
              : action === "prepare"
                ? await commercialOperationsApi.prepareExecutionRequest(selectedOperationId, executionRequestId, "Prepared for future guarded runtime adapter; no execution occurred.", settings)
                : action === "fail"
                  ? await commercialOperationsApi.failExecutionRequest(selectedOperationId, executionRequestId, "Failed before future runtime handoff; no execution occurred.", settings)
                  : action === "cancel"
                    ? await commercialOperationsApi.cancelExecutionRequest(selectedOperationId, executionRequestId, "Cancelled from Commercial Ops.", settings)
                  : await commercialOperationsApi.archiveExecutionRequest(selectedOperationId, executionRequestId, "Archived from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadExecutionRequests(selectedOperationId);
      await loadExecutionRuns(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation execution request action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editOperationExecutionRun = (executionRun: JsonRecord) => {
    const executionRunId = valueAt(executionRun, ["id"], "");
    if (!executionRunId) {
      return;
    }
    setSelectedExecutionRunId(executionRunId);
    setExecutionRunRequestId(valueAt(executionRun, ["execution_request_id"], executionRunRequestId));
    setExecutionRunTitle(valueAt(executionRun, ["title"], executionRunTitle));
    setExecutionRunTarget(valueAt(executionRun, ["execution_target"], ""));
    setExecutionRunInputPayloadDraft(JSON.stringify((executionRun.input_payload as JsonRecord | undefined) || {}, null, 2));
    setExecutionRunMaxRetries(valueAt(executionRun, ["max_retries"], executionRunMaxRetries));
    setExecutionRunOperatorNotes(valueAt(executionRun, ["operator_notes"], ""));
  };

  const executionRunPayload = (): JsonRecord => {
    const maxRetries = Number(executionRunMaxRetries || "0");
    if (!Number.isFinite(maxRetries) || maxRetries < 0) {
      throw new Error("max retries must be zero or greater");
    }
    return {
      execution_request_id: executionRunRequestId,
      title: executionRunTitle.trim(),
      execution_target: executionRunTarget.trim() || undefined,
      input_payload: parseJsonRecordDraft(executionRunInputPayloadDraft),
      max_retries: Math.floor(maxRetries),
      operator_notes: executionRunOperatorNotes.trim() || undefined,
      metadata: { source: "admin_dashboard", phase: "61I" },
    };
  };

  const createOperationExecutionRun = async () => {
    if (!selectedOperationId || !executionRunRequestId) {
      setActionState({
        data: null,
        error: executionRunCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createExecutionRun(selectedOperationId, executionRunPayload(), settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedExecutionRunId(valueAt(created, ["id"], ""));
      await loadExecutionRuns(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation execution run create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateOperationExecutionRun = async () => {
    if (!selectedOperationId || !selectedExecutionRunId) {
      return;
    }
    const { execution_request_id: _executionRequestId, ...payload } = executionRunPayload();
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateExecutionRun(selectedOperationId, selectedExecutionRunId, payload, settings);
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadExecutionRuns(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation execution run update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateOperationExecutionRun = async (
    executionRunId: string,
    action: "start" | "succeed" | "fail" | "retry" | "cancel" | "archive",
  ) => {
    if (!selectedOperationId || !executionRunId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "start"
          ? await commercialOperationsApi.startExecutionRun(selectedOperationId, executionRunId, "Started from Commercial Ops; no external runtime was called.", settings)
          : action === "succeed"
            ? await commercialOperationsApi.succeedExecutionRun(selectedOperationId, executionRunId, "Succeeded from Commercial Ops metadata run.", settings)
            : action === "fail"
              ? await commercialOperationsApi.failExecutionRun(selectedOperationId, executionRunId, "Failed from Commercial Ops metadata run; operator review required.", settings)
              : action === "retry"
                ? await commercialOperationsApi.retryExecutionRun(selectedOperationId, executionRunId, "Retry requested from Commercial Ops after human review.", settings)
                : action === "cancel"
                  ? await commercialOperationsApi.cancelExecutionRun(selectedOperationId, executionRunId, "Cancelled from Commercial Ops.", settings)
                  : await commercialOperationsApi.archiveExecutionRun(selectedOperationId, executionRunId, "Archived from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadExecutionRuns(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation execution run action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editOperationResult = (result: JsonRecord) => {
    const resultId = valueAt(result, ["id"], "");
    if (!resultId) {
      return;
    }
    setSelectedResultId(resultId);
    setResultRunId(valueAt(result, ["execution_run_id"], resultRunId));
    setResultTitle(valueAt(result, ["title"], resultTitle));
    setResultType(valueAt(result, ["result_type"], resultType));
    setResultSummary(valueAt(result, ["summary"], ""));
    setResultOutcomeSummary(valueAt(result, ["outcome_summary"], ""));
    setResultMetricsDraft(metricDraftText(result.observed_metrics));
    setResultSignalsDraft(draftListText(result.commercial_signals));
    setResultEvidenceDraft(draftListText(result.evidence_links));
    setResultFollowUpsDraft(draftListText(result.follow_up_actions));
  };

  const resultPayload = (): JsonRecord => ({
    execution_run_id: resultRunId,
    result_type: resultType.trim() || "operator_report",
    title: resultTitle.trim(),
    summary: resultSummary.trim() || undefined,
    outcome_summary: resultOutcomeSummary.trim() || undefined,
    observed_metrics: metricDraftList(resultMetricsDraft),
    commercial_signals: splitDraftList(resultSignalsDraft),
    evidence_links: splitDraftList(resultEvidenceDraft).map((item) => ({
      title: item,
      type: "operator_evidence",
    })),
    follow_up_actions: splitDraftList(resultFollowUpsDraft),
    result_payload: { source: "admin_dashboard" },
    recommendation_payload: {
      source: "admin_dashboard",
      boundary: "metadata-only; no platform analytics ingestion and no ROI attribution claim",
    },
    metadata: { source: "admin_dashboard", phase: "61J" },
  });

  const createOperationResult = async () => {
    if (!selectedOperationId || !resultRunId) {
      setActionState({
        data: null,
        error: resultCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createResult(selectedOperationId, resultPayload(), settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedResultId(valueAt(created, ["id"], ""));
      await loadResults(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation result create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateOperationResult = async () => {
    if (!selectedOperationId || !selectedResultId) {
      return;
    }
    const { execution_run_id: _executionRunId, ...payload } = resultPayload();
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateResult(selectedOperationId, selectedResultId, payload, settings);
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadResults(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation result update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateOperationResult = async (resultId: string, action: "ready" | "approve" | "reject" | "archive") => {
    if (!selectedOperationId || !resultId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyResult(selectedOperationId, resultId, "Ready for result review from Commercial Ops.", settings)
          : action === "approve"
            ? await commercialOperationsApi.approveResult(selectedOperationId, resultId, "Approved as operator-observed result; no ROI attribution claim.", settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectResult(selectedOperationId, resultId, "Rejected from Commercial Ops; revise evidence or metrics.", settings)
              : await commercialOperationsApi.archiveResult(selectedOperationId, resultId, "Archived from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadResults(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation result action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editMonitoringObservation = (observation: JsonRecord) => {
    const observationId = valueAt(observation, ["id"], "");
    if (!observationId) {
      return;
    }
    setSelectedObservationId(observationId);
    setMonitoringResultId(valueAt(observation, ["result_id"], monitoringResultId));
    setMonitoringTitle(valueAt(observation, ["title"], monitoringTitle));
    setMonitoringType(valueAt(observation, ["observation_type"], monitoringType));
    setMonitoringWindowStart(valueAt(observation, ["observation_window_start"], ""));
    setMonitoringWindowEnd(valueAt(observation, ["observation_window_end"], ""));
    setMonitoringMetricsDraft(metricDraftText(observation.metric_snapshots));
    setMonitoringSignalsDraft(draftListText(observation.qualitative_signals));
    setMonitoringEvidenceDraft(draftListText(observation.evidence_links));
    setMonitoringAnomaliesDraft(draftListText(observation.anomaly_flags));
    setMonitoringActionsDraft(draftListText(observation.recommended_actions));
  };

  const monitoringObservationPayload = (): JsonRecord => ({
    result_id: monitoringResultId,
    observation_type: monitoringType.trim() || "manual_snapshot",
    title: monitoringTitle.trim(),
    observation_window_start: monitoringWindowStart.trim() || undefined,
    observation_window_end: monitoringWindowEnd.trim() || undefined,
    metric_snapshots: metricDraftList(monitoringMetricsDraft),
    qualitative_signals: splitDraftList(monitoringSignalsDraft),
    evidence_links: splitDraftList(monitoringEvidenceDraft).map((item) => ({
      title: item,
      type: "monitoring_evidence",
    })),
    anomaly_flags: splitDraftList(monitoringAnomaliesDraft),
    recommended_actions: splitDraftList(monitoringActionsDraft),
    observation_payload: {
      source: "admin_dashboard",
      boundary: "metadata-only; no platform analytics ingestion and no ROI attribution claim",
    },
    metadata: { source: "admin_dashboard", phase: "61K" },
  });

  const createMonitoringObservation = async () => {
    if (!selectedOperationId || !monitoringResultId) {
      setActionState({
        data: null,
        error: monitoringCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createMonitoringObservation(
        selectedOperationId,
        monitoringObservationPayload(),
        settings,
      );
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedObservationId(valueAt(created, ["id"], ""));
      await loadMonitoringObservations(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation monitoring observation create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateMonitoringObservation = async () => {
    if (!selectedOperationId || !selectedObservationId) {
      return;
    }
    const { result_id: _resultId, ...payload } = monitoringObservationPayload();
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateMonitoringObservation(
        selectedOperationId,
        selectedObservationId,
        payload,
        settings,
      );
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadMonitoringObservations(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation monitoring observation update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateMonitoringObservation = async (
    observationId: string,
    action: "ready" | "approve" | "reject" | "archive",
  ) => {
    if (!selectedOperationId || !observationId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyMonitoringObservation(selectedOperationId, observationId, "Ready for monitoring observation review from Commercial Ops.", settings)
          : action === "approve"
            ? await commercialOperationsApi.approveMonitoringObservation(selectedOperationId, observationId, "Approved as operator-observed monitoring snapshot; no ROI attribution claim.", settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectMonitoringObservation(selectedOperationId, observationId, "Rejected from Commercial Ops; revise evidence, anomalies, or metric snapshots.", settings)
              : await commercialOperationsApi.archiveMonitoringObservation(selectedOperationId, observationId, "Archived from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadMonitoringObservations(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation monitoring observation action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const editOptimizationDecision = (decision: JsonRecord) => {
    const decisionId = valueAt(decision, ["id"], "");
    if (!decisionId) {
      return;
    }
    setSelectedOptimizationDecisionId(decisionId);
    setOptimizationObservationId(valueAt(decision, ["observation_id"], optimizationObservationId));
    setOptimizationTitle(valueAt(decision, ["title"], optimizationTitle));
    setOptimizationType(valueAt(decision, ["decision_type"], optimizationType));
    setOptimizationPriority(valueAt(decision, ["priority"], optimizationPriority));
    setOptimizationRationale(valueAt(decision, ["rationale"], ""));
    setOptimizationObjectiveUpdatesDraft(draftListText(decision.objective_updates));
    setOptimizationContentActionsDraft(draftListText(decision.content_actions));
    setOptimizationAssetActionsDraft(draftListText(decision.asset_actions));
    setOptimizationAudienceActionsDraft(draftListText(decision.audience_actions));
    setOptimizationExecutionActionsDraft(draftListText(decision.execution_actions));
    setOptimizationRiskControlsDraft(draftListText(decision.risk_controls));
  };

  const optimizationDecisionPayload = (): JsonRecord => ({
    observation_id: optimizationObservationId,
    decision_type: optimizationType.trim() || "iterate",
    title: optimizationTitle.trim(),
    priority: optimizationPriority.trim() || "normal",
    rationale: optimizationRationale.trim() || undefined,
    objective_updates: splitDraftList(optimizationObjectiveUpdatesDraft),
    content_actions: splitDraftList(optimizationContentActionsDraft),
    asset_actions: splitDraftList(optimizationAssetActionsDraft),
    audience_actions: splitDraftList(optimizationAudienceActionsDraft),
    execution_actions: splitDraftList(optimizationExecutionActionsDraft),
    risk_controls: splitDraftList(optimizationRiskControlsDraft),
    decision_payload: {
      source: "admin_dashboard",
      boundary: "metadata-only; no automatic optimization, publishing, or external runtime call",
    },
    metadata: { source: "admin_dashboard", phase: "61L" },
  });

  const createOptimizationDecision = async () => {
    if (!selectedOperationId || !optimizationObservationId) {
      setActionState({
        data: null,
        error: optimizationCopy.selectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createOptimizationDecision(
        selectedOperationId,
        optimizationDecisionPayload(),
        settings,
      );
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedOptimizationDecisionId(valueAt(created, ["id"], ""));
      await loadOptimizationDecisions(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation optimization decision create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateOptimizationDecision = async () => {
    if (!selectedOperationId || !selectedOptimizationDecisionId) {
      return;
    }
    const { observation_id: _observationId, ...payload } = optimizationDecisionPayload();
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const updated = await commercialOperationsApi.updateOptimizationDecision(
        selectedOperationId,
        selectedOptimizationDecisionId,
        payload,
        settings,
      );
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      await loadOptimizationDecisions(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation optimization decision update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateOptimizationDecision = async (
    decisionId: string,
    action: "ready" | "approve" | "reject" | "archive",
  ) => {
    if (!selectedOperationId || !decisionId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "ready"
          ? await commercialOperationsApi.readyOptimizationDecision(selectedOperationId, decisionId, "Ready for optimization decision review from Commercial Ops.", settings)
          : action === "approve"
            ? await commercialOperationsApi.approveOptimizationDecision(selectedOperationId, decisionId, "Approved as operator optimization decision; no automatic optimization or publishing.", settings)
            : action === "reject"
              ? await commercialOperationsApi.rejectOptimizationDecision(selectedOperationId, decisionId, "Rejected from Commercial Ops; revise rationale, actions, or risk controls.", settings)
              : await commercialOperationsApi.archiveOptimizationDecision(selectedOperationId, decisionId, "Archived from Commercial Ops.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadOptimizationDecisions(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation optimization decision action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const createOperationDryRun = async () => {
    if (!selectedOperationId) {
      setActionState({
        data: null,
        error: copy.dryRunsSelectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    const approved = (approvalsState.data || []).filter((approval) => valueAt(approval, ["approval_status"], "") === "approved");
    const approvalId = dryRunApprovalId || (approved[0] ? valueAt(approved[0], ["id"], "") : "");
    if (!approvalId) {
      setActionState({
        data: null,
        error: copy.dryRunRequiresApproval,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const created = await commercialOperationsApi.createDryRun(
        selectedOperationId,
        {
          approval_id: approvalId,
          step_key: dryRunStepKey.trim() || "execution_dry_run",
          title: dryRunTitle.trim(),
          execution_mode: executionMode,
          execution_target: executionTarget.trim() || undefined,
          input_summary: dryRunInputSummary.trim() || undefined,
          expected_outputs: splitDraftList(expectedOutputsDraft),
          readiness_checks: splitDraftList(readinessChecksDraft),
          metadata: { source: "admin_dashboard", phase: "61D" },
        },
        settings,
      );
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      await loadDryRuns(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation dry-run create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const mutateOperationDryRun = async (dryRunId: string, action: "complete" | "fail" | "cancel") => {
    if (!selectedOperationId || !dryRunId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response =
        action === "complete"
          ? await commercialOperationsApi.completeDryRun(selectedOperationId, dryRunId, "Completed from Commercial Ops; no external action executed.", settings)
          : action === "fail"
            ? await commercialOperationsApi.failDryRun(selectedOperationId, dryRunId, "Failed from Commercial Ops; operator review required.", settings)
            : await commercialOperationsApi.cancelDryRun(selectedOperationId, dryRunId, "Cancelled from Commercial Ops before execution.", settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await loadDryRuns(selectedOperationId);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation dry-run action unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const createOperationLink = async () => {
    if (!selectedOperationId) {
      setActionState({
        data: null,
        error: copy.linksSelectedHint,
        loading: false,
        updatedAt: nowLabel(),
      });
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const payload: JsonRecord = {
        link_type: linkType,
        target_type: targetType.trim(),
        target_id: targetId.trim(),
        title: linkTitle.trim(),
        summary: linkSummary.trim() || undefined,
        source_name: linkSourceName.trim() || undefined,
        metadata: { source: "admin_dashboard", phase: "61C" },
      };
      const created = await commercialOperationsApi.createLink(selectedOperationId, payload, settings);
      setActionState({ data: created, error: null, loading: false, updatedAt: nowLabel() });
      setTargetId("");
      await loadLinks(selectedOperationId);
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation link create unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const deleteOperationLink = async (linkId: string) => {
    if (!selectedOperationId || !linkId) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const deleted = await commercialOperationsApi.deleteLink(selectedOperationId, linkId, settings);
      setActionState({ data: deleted, error: null, loading: false, updatedAt: nowLabel() });
      await loadLinks(selectedOperationId);
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial operation link delete unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const regeneratePlan = async () => {
    if (!selectedOperation) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const operationId = valueAt(selectedOperation, ["id"]);
      const response = await commercialOperationsApi.planDraft(operationId, settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial plan draft unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const updateSelectedStatus = async (status: "ready" | "active" | "paused") => {
    if (!selectedOperation) {
      return;
    }
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const operationId = valueAt(selectedOperation, ["id"]);
      const updated = await commercialOperationsApi.update(operationId, { status }, settings);
      setActionState({ data: updated, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedOperation(updated);
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Commercial status update unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const operations = toItems(state.data?.operations);
  const activeCount = operations.filter((operation) => /planning|ready|active/i.test(String(operation.status ?? ""))).length;
  const attentionCount = operations.filter((operation) => {
    const status = String(operation.status ?? "");
    const risk = String(operation.risk_level ?? "");
    return /high/i.test(risk) || /draft|planning/i.test(status);
  }).length;
  const planStepCount = operations.reduce((total, operation) => {
    const outline = operation.plan_outline;
    return total + (Array.isArray(outline) ? outline.length : 0);
  }, 0);
  const planRows = selectedOperation && Array.isArray(selectedOperation.plan_outline) ? (selectedOperation.plan_outline as JsonRecord[]) : [];
  const approvals = approvalsState.data || [];
  const approvedApprovals = approvals.filter((approval) => valueAt(approval, ["approval_status"], "") === "approved");
  const dryRuns = dryRunsState.data || [];
  const contentDrafts = contentDraftsState.data || [];
  const assetRequests = assetRequestsState.data || [];
  const comfyuiHandoffs = comfyuiHandoffsState.data || [];
  const comfyuiPreflights = comfyuiPreflightsState.data || [];
  const checkedComfyuiPreflights = comfyuiPreflights.filter((preflight) => valueAt(preflight, ["preflight_status"], "") === "checked");
  const comfyuiAdapterConfigs = comfyuiAdapterConfigsState.data || [];
  const readyComfyuiAdapterConfigs = comfyuiAdapterConfigs.filter((config) => valueAt(config, ["config_status"], "") === "ready");
  const comfyuiJobRequests = comfyuiJobRequestsState.data || [];
  const actionableComfyuiJobRequests = comfyuiJobRequests.filter((jobRequest) => ["approved", "queued"].includes(valueAt(jobRequest, ["job_status"], "")));
  const comfyuiExecutionPlans = comfyuiExecutionPlansState.data || [];
  const actionableComfyuiExecutionPlans = comfyuiExecutionPlans.filter((plan) => ["approved", "simulated"].includes(valueAt(plan, ["plan_status"], "")));
  const comfyuiConnectionProbes = comfyuiConnectionProbesState.data || [];
  const actionableComfyuiConnectionProbes = comfyuiConnectionProbes.filter((probe) => valueAt(probe, ["probe_status"], "") === "probed");
  const comfyuiAdapterDispatches = comfyuiAdapterDispatchesState.data || [];
  const deliverables = deliverablesState.data || [];
  const evidenceSnapshots = evidenceSnapshotsState.data || [];
  const executionRequests = executionRequestsState.data || [];
  const executionRuns = executionRunsState.data || [];
  const results = resultsState.data || [];
  const monitoringObservations = monitoringState.data || [];
  const optimizationDecisions = optimizationState.data || [];
  const packagedDeliverables = deliverables.filter((deliverable) => valueAt(deliverable, ["deliverable_status"], "") === "packaged");
  const approvedEvidenceSnapshots = evidenceSnapshots.filter((snapshot) => valueAt(snapshot, ["snapshot_status"], "") === "approved");
  const approvedEvidenceSnapshotsForExecution = approvedEvidenceSnapshots.filter((snapshot) => {
    const linkedDeliverable = valueAt(snapshot, ["deliverable_id"], "");
    return !executionDeliverableId || linkedDeliverable === executionDeliverableId;
  });
  const approvedEvidenceSnapshotIdsForExecution = approvedEvidenceSnapshotsForExecution
    .map((snapshot) => valueAt(snapshot, ["id"], ""))
    .filter(Boolean);
  const preparedExecutionRequests = executionRequests.filter((executionRequest) => valueAt(executionRequest, ["request_status"], "") === "prepared");
  const terminalExecutionRuns = executionRuns.filter((executionRun) => ["succeeded", "failed", "cancelled"].includes(valueAt(executionRun, ["run_status"], "")));
  const approvedResults = results.filter((result) => valueAt(result, ["result_status"], "") === "approved");
  const approvedMonitoringObservations = monitoringObservations.filter((observation) => valueAt(observation, ["observation_status"], "") === "approved");
  const approvedContentDrafts = contentDrafts.filter((draft) => valueAt(draft, ["draft_status"], "") === "approved");
  const eligibleDeliverableAssets = assetRequests.filter((assetRequest) => {
    const status = valueAt(assetRequest, ["request_status"], "");
    const linkedDraft = valueAt(assetRequest, ["content_draft_id"], "");
    return ["approved", "prepared"].includes(status) && (!deliverableContentDraftId || !linkedDraft || linkedDraft === deliverableContentDraftId);
  });
  const eligibleComfyuiAssets = assetRequests.filter((assetRequest) => ["approved", "prepared"].includes(valueAt(assetRequest, ["request_status"], "")));
  const eligibleComfyuiHandoffs = comfyuiHandoffs.filter((handoff) => ["approved", "prepared"].includes(valueAt(handoff, ["handoff_status"], "")));
  const links = linksState.data || [];

  useEffect(() => {
    const approved = (approvalsState.data || []).filter((approval) => valueAt(approval, ["approval_status"], "") === "approved");
    if (dryRunApprovalId && approved.some((approval) => valueAt(approval, ["id"], "") === dryRunApprovalId)) {
      return;
    }
    setDryRunApprovalId(approved[0] ? valueAt(approved[0], ["id"], "") : "");
  }, [approvalsState.data, dryRunApprovalId]);

  useEffect(() => {
    if (comfyuiAssetRequestId && eligibleComfyuiAssets.some((assetRequest) => valueAt(assetRequest, ["id"], "") === comfyuiAssetRequestId)) {
      return;
    }
    const nextAsset = eligibleComfyuiAssets[0];
    const nextAssetId = nextAsset ? valueAt(nextAsset, ["id"], "") : "";
    setComfyuiAssetRequestId(nextAssetId);
    if (nextAsset && !selectedComfyuiHandoffId) {
      setComfyuiTitle(`${valueAt(nextAsset, ["title"], "Asset request")} ComfyUI handoff`);
      setComfyuiPromptPayloadDraft(
        JSON.stringify(
          {
            asset_request_id: nextAssetId,
            asset_type: valueAt(nextAsset, ["asset_type"], "image"),
            channel: valueAt(nextAsset, ["channel"], ""),
            generation_prompt: valueAt(nextAsset, ["generation_prompt"], ""),
          },
          null,
          2,
        ),
      );
    }
  }, [eligibleComfyuiAssets, comfyuiAssetRequestId, selectedComfyuiHandoffId]);

  useEffect(() => {
    if (comfyuiPreflightHandoffId && eligibleComfyuiHandoffs.some((handoff) => valueAt(handoff, ["id"], "") === comfyuiPreflightHandoffId)) {
      return;
    }
    const nextHandoff = eligibleComfyuiHandoffs[0];
    const nextHandoffId = nextHandoff ? valueAt(nextHandoff, ["id"], "") : "";
    setComfyuiPreflightHandoffId(nextHandoffId);
    if (nextHandoff && !selectedComfyuiPreflightId) {
      setComfyuiPreflightTitle(`${valueAt(nextHandoff, ["title"], "ComfyUI handoff")} preflight`);
      setComfyuiPreflightWorkflowName(valueAt(nextHandoff, ["workflow_name"], "future_comfyui_handoff"));
    }
  }, [eligibleComfyuiHandoffs, comfyuiPreflightHandoffId, selectedComfyuiPreflightId]);

  useEffect(() => {
    if (comfyuiPreflightAdapterConfigId && comfyuiAdapterConfigs.some((config) => valueAt(config, ["id"], "") === comfyuiPreflightAdapterConfigId)) {
      return;
    }
    const nextConfig = readyComfyuiAdapterConfigs[0] || comfyuiAdapterConfigs[0];
    const nextConfigId = nextConfig ? valueAt(nextConfig, ["id"], "") : "";
    setComfyuiPreflightAdapterConfigId(nextConfigId);
    if (nextConfig && !selectedComfyuiPreflightId) {
      setComfyuiPreflightTargetUrl(valueAt(nextConfig, ["target_url"], comfyuiPreflightTargetUrl));
      setComfyuiPreflightQueueName(valueAt(nextConfig, ["queue_name"], comfyuiPreflightQueueName));
      setComfyuiPreflightWorkflowName(valueAt(nextConfig, ["default_workflow_name"], comfyuiPreflightWorkflowName));
      setComfyuiPreflightModelRefsDraft(
        ((nextConfig.model_inventory as JsonRecord[]) || [])
          .map((item) => valueAt(item, ["name"], ""))
          .filter(Boolean)
          .join(", "),
      );
    }
  }, [comfyuiAdapterConfigs, readyComfyuiAdapterConfigs, comfyuiPreflightAdapterConfigId, selectedComfyuiPreflightId, comfyuiPreflightTargetUrl, comfyuiPreflightQueueName, comfyuiPreflightWorkflowName]);

  useEffect(() => {
    if (comfyuiJobPreflightId && checkedComfyuiPreflights.some((preflight) => valueAt(preflight, ["id"], "") === comfyuiJobPreflightId)) {
      return;
    }
    const nextPreflight = checkedComfyuiPreflights[0];
    const nextPreflightId = nextPreflight ? valueAt(nextPreflight, ["id"], "") : "";
    setComfyuiJobPreflightId(nextPreflightId);
    if (nextPreflight && !selectedComfyuiJobRequestId) {
      setComfyuiJobTitle(`${valueAt(nextPreflight, ["title"], "ComfyUI preflight")} job request`);
      setComfyuiJobRuntimePayloadDraft(
        JSON.stringify(
          {
            execution_mode: "metadata_only",
            queue_submission: false,
            submit_job: false,
            queue_name: valueAt(nextPreflight, ["queue_name"], ""),
            workflow_name: valueAt(nextPreflight, ["workflow_name"], ""),
          },
          null,
          2,
        ),
      );
    }
  }, [checkedComfyuiPreflights, comfyuiJobPreflightId, selectedComfyuiJobRequestId]);

  useEffect(() => {
    if (comfyuiExecutionJobRequestId && actionableComfyuiJobRequests.some((jobRequest) => valueAt(jobRequest, ["id"], "") === comfyuiExecutionJobRequestId)) {
      return;
    }
    const nextJobRequest = actionableComfyuiJobRequests[0];
    const nextJobRequestId = nextJobRequest ? valueAt(nextJobRequest, ["id"], "") : "";
    setComfyuiExecutionJobRequestId(nextJobRequestId);
    if (nextJobRequest && !selectedComfyuiExecutionPlanId) {
      setComfyuiExecutionTitle(`${valueAt(nextJobRequest, ["title"], "ComfyUI job request")} execution plan`);
      setComfyuiExecutionPriority(valueAt(nextJobRequest, ["priority"], "normal") as "low" | "normal" | "high");
      setComfyuiExecutionSimulationPayloadDraft(
        JSON.stringify(
          {
            execution_mode: "metadata_only",
            queue_submission: false,
            upload_files: false,
            job_request_id: nextJobRequestId,
            queue_name: valueAt(nextJobRequest, ["queue_name"], ""),
            workflow_name: valueAt(nextJobRequest, ["workflow_name"], ""),
          },
          null,
          2,
        ),
      );
    }
  }, [actionableComfyuiJobRequests, comfyuiExecutionJobRequestId, selectedComfyuiExecutionPlanId]);

  useEffect(() => {
    if (comfyuiProbeExecutionPlanId && actionableComfyuiExecutionPlans.some((plan) => valueAt(plan, ["id"], "") === comfyuiProbeExecutionPlanId)) {
      return;
    }
    const nextPlan = actionableComfyuiExecutionPlans[0];
    const nextPlanId = nextPlan ? valueAt(nextPlan, ["id"], "") : "";
    setComfyuiProbeExecutionPlanId(nextPlanId);
    if (nextPlan && !selectedComfyuiConnectionProbeId) {
      setComfyuiProbeTitle(`${valueAt(nextPlan, ["title"], "ComfyUI execution plan")} connection probe`);
      setComfyuiProbePayloadDraft(
        JSON.stringify(
          {
            probe_mode: "metadata_only",
            network_probe: false,
            read_only_probe: false,
            queue_name: valueAt(nextPlan, ["queue_name"], ""),
            workflow_name: valueAt(nextPlan, ["workflow_name"], ""),
          },
          null,
          2,
        ),
      );
    }
  }, [actionableComfyuiExecutionPlans, comfyuiProbeExecutionPlanId, selectedComfyuiConnectionProbeId]);

  useEffect(() => {
    if (comfyuiDispatchConnectionProbeId && actionableComfyuiConnectionProbes.some((probe) => valueAt(probe, ["id"], "") === comfyuiDispatchConnectionProbeId)) {
      return;
    }
    const nextProbe = actionableComfyuiConnectionProbes[0];
    const nextProbeId = nextProbe ? valueAt(nextProbe, ["id"], "") : "";
    setComfyuiDispatchConnectionProbeId(nextProbeId);
    if (nextProbe && !selectedComfyuiAdapterDispatchId) {
      setComfyuiDispatchTitle(`${valueAt(nextProbe, ["title"], "ComfyUI connection probe")} adapter dispatch`);
      setComfyuiDispatchPromptPayloadDraft(
        JSON.stringify(
          {
            source: "metadata_only",
            connection_probe_id: nextProbeId,
            workflow_name: valueAt(nextProbe, ["workflow_name"], ""),
          },
          null,
          2,
        ),
      );
      setComfyuiDispatchQueuePayloadDraft(
        JSON.stringify(
          {
            queue_submission: false,
            queue_read: false,
            queue_name: valueAt(nextProbe, ["queue_name"], ""),
            workflow_name: valueAt(nextProbe, ["workflow_name"], ""),
          },
          null,
          2,
        ),
      );
    }
  }, [actionableComfyuiConnectionProbes, comfyuiDispatchConnectionProbeId, selectedComfyuiAdapterDispatchId]);

  useEffect(() => {
    if (deliverableContentDraftId && approvedContentDrafts.some((draft) => valueAt(draft, ["id"], "") === deliverableContentDraftId)) {
      return;
    }
    const nextDraftId = approvedContentDrafts[0] ? valueAt(approvedContentDrafts[0], ["id"], "") : "";
    setDeliverableContentDraftId(nextDraftId);
  }, [approvedContentDrafts, deliverableContentDraftId]);

  useEffect(() => {
    if (evidenceDeliverableId && packagedDeliverables.some((deliverable) => valueAt(deliverable, ["id"], "") === evidenceDeliverableId)) {
      return;
    }
    const nextDeliverable = packagedDeliverables[0];
    const nextDeliverableId = nextDeliverable ? valueAt(nextDeliverable, ["id"], "") : "";
    setEvidenceDeliverableId(nextDeliverableId);
    if (nextDeliverable && !selectedEvidenceSnapshotId) {
      setEvidenceTitle(`${valueAt(nextDeliverable, ["title"], "Deliverable")} evidence`);
    }
  }, [packagedDeliverables, evidenceDeliverableId, selectedEvidenceSnapshotId]);

  useEffect(() => {
    if (executionDeliverableId && packagedDeliverables.some((deliverable) => valueAt(deliverable, ["id"], "") === executionDeliverableId)) {
      return;
    }
    const nextDeliverableId = packagedDeliverables[0] ? valueAt(packagedDeliverables[0], ["id"], "") : "";
    setExecutionDeliverableId(nextDeliverableId);
  }, [packagedDeliverables, executionDeliverableId]);

  useEffect(() => {
    if (selectedExecutionRequestId) {
      return;
    }
    setExecutionEvidenceSnapshotIdsDraft(approvedEvidenceSnapshotIdsForExecution.join(", "));
  }, [approvedEvidenceSnapshotIdsForExecution.join("|"), selectedExecutionRequestId]);

  useEffect(() => {
    if (executionRunRequestId && preparedExecutionRequests.some((request) => valueAt(request, ["id"], "") === executionRunRequestId)) {
      return;
    }
    const nextRequest = preparedExecutionRequests[0];
    const nextRequestId = nextRequest ? valueAt(nextRequest, ["id"], "") : "";
    setExecutionRunRequestId(nextRequestId);
    if (nextRequest && !selectedExecutionRunId) {
      setExecutionRunTitle(`${valueAt(nextRequest, ["title"], "Execution request")} run`);
      setExecutionRunTarget(valueAt(nextRequest, ["execution_target"], executionRunTarget));
    }
  }, [preparedExecutionRequests, executionRunRequestId, selectedExecutionRunId, executionRunTarget]);

  useEffect(() => {
    if (resultRunId && terminalExecutionRuns.some((run) => valueAt(run, ["id"], "") === resultRunId)) {
      return;
    }
    const nextRun = terminalExecutionRuns[0];
    const nextRunId = nextRun ? valueAt(nextRun, ["id"], "") : "";
    setResultRunId(nextRunId);
    if (nextRun && !selectedResultId) {
      setResultTitle(`${valueAt(nextRun, ["title"], "Execution run")} result`);
    }
  }, [terminalExecutionRuns, resultRunId, selectedResultId]);

  useEffect(() => {
    if (monitoringResultId && approvedResults.some((result) => valueAt(result, ["id"], "") === monitoringResultId)) {
      return;
    }
    const nextResult = approvedResults[0];
    const nextResultId = nextResult ? valueAt(nextResult, ["id"], "") : "";
    setMonitoringResultId(nextResultId);
    if (nextResult && !selectedObservationId) {
      setMonitoringTitle(`${valueAt(nextResult, ["title"], "Commercial result")} observation`);
    }
  }, [approvedResults, monitoringResultId, selectedObservationId]);

  useEffect(() => {
    if (optimizationObservationId && approvedMonitoringObservations.some((observation) => valueAt(observation, ["id"], "") === optimizationObservationId)) {
      return;
    }
    const nextObservation = approvedMonitoringObservations[0];
    const nextObservationId = nextObservation ? valueAt(nextObservation, ["id"], "") : "";
    setOptimizationObservationId(nextObservationId);
    if (nextObservation && !selectedOptimizationDecisionId) {
      setOptimizationTitle(`${valueAt(nextObservation, ["title"], "Monitoring observation")} decision`);
    }
  }, [approvedMonitoringObservations, optimizationObservationId, selectedOptimizationDecisionId]);

  return (
    <div className="page-stack">
      <section className="commercial-command-center">
        <div>
          <p className="section-eyebrow">{copy.connection}: {settings.aiServerUrl} / {copy.phaseLabel}</p>
          <h2>{copy.title}</h2>
          <p>{copy.description}</p>
          <p>{copy.summary}</p>
        </div>
        <div className="commercial-flow-grid" aria-label={copy.title}>
          {copy.flow.map((item) => (
            <span key={item}>{item}</span>
          ))}
        </div>
      </section>

      <div className="metrics-grid commercial-metrics-grid">
        <DataCard title={copy.total} value={String(operations.length)} detail={settings.workspaceId} icon={<Megaphone size={20} />} />
        <DataCard title={copy.active} value={String(activeCount)} detail="planning / ready / active" icon={<Sparkles size={20} />} />
        <DataCard title={copy.attention} value={String(attentionCount)} detail="draft / planning / high" icon={<AlertTriangle size={20} />} warning={attentionCount > 0} />
        <DataCard title={copy.steps} value={String(planStepCount)} detail={`${copy.approvalsTitle}: ${approvals.length} / ${contentCopy.title}: ${contentDrafts.length} / ${assetCopy.title}: ${assetRequests.length} / ${comfyuiCopy.title}: ${comfyuiHandoffs.length} / ${comfyuiAdapterCopy.title}: ${comfyuiAdapterConfigs.length} / ${comfyuiPreflightCopy.title}: ${comfyuiPreflights.length} / ${comfyuiJobCopy.title}: ${comfyuiJobRequests.length} / ${comfyuiExecutionCopy.title}: ${comfyuiExecutionPlans.length} / ${comfyuiProbeCopy.title}: ${comfyuiConnectionProbes.length} / ${comfyuiDispatchCopy.title}: ${comfyuiAdapterDispatches.length} / ${deliverableCopy.title}: ${deliverables.length} / ${evidenceCopy.title}: ${evidenceSnapshots.length} / ${executionRequestCopy.title}: ${executionRequests.length} / ${executionRunCopy.title}: ${executionRuns.length} / ${resultCopy.title}: ${results.length} / ${monitoringCopy.title}: ${monitoringObservations.length} / ${optimizationCopy.title}: ${optimizationDecisions.length} / ${copy.dryRunsTitle}: ${dryRuns.length} / ${copy.linksTitle}: ${links.length}`} icon={<BarChart3 size={20} />} />
      </div>

      <div className="commercial-grid">
        <Panel title={copy.createTitle} description={copy.createDescription}>
          <div className="commercial-form-grid">
            <label>
              {copy.titleLabel}
              <input value={title} onChange={(event) => setTitle(event.target.value)} />
            </label>
            <label>
              {copy.audienceLabel}
              <input value={targetAudience} onChange={(event) => setTargetAudience(event.target.value)} />
            </label>
            <label className="commercial-wide-label">
              {copy.objectiveLabel}
              <textarea value={objective} onChange={(event) => setObjective(event.target.value)} placeholder={copy.objectivePlaceholder} />
            </label>
            <label>
              {copy.channelsLabel}
              <input value={channelsDraft} onChange={(event) => setChannelsDraft(event.target.value)} />
            </label>
            <label>
              {copy.metricsLabel}
              <input value={metricsDraft} onChange={(event) => setMetricsDraft(event.target.value)} />
            </label>
            <label>
              {copy.collectionLabel}
              <input value={knowledgeCollection} onChange={(event) => setKnowledgeCollection(event.target.value)} />
            </label>
            <label>
              {copy.priorityLabel}
              <select value={priority} onChange={(event) => setPriority(event.target.value as "low" | "normal" | "high")}>
                <option value="low">low</option>
                <option value="normal">normal</option>
                <option value="high">high</option>
              </select>
            </label>
            <label>
              {copy.riskLabel}
              <select value={riskLevel} onChange={(event) => setRiskLevel(event.target.value as "low" | "medium" | "high")}>
                <option value="low">low</option>
                <option value="medium">medium</option>
                <option value="high">high</option>
              </select>
            </label>
            <label>
              {copy.budgetLabel}
              <input value={budgetAmount} onChange={(event) => setBudgetAmount(event.target.value)} placeholder="optional" />
            </label>
            <label>
              {copy.currencyLabel}
              <input value={budgetCurrency} onChange={(event) => setBudgetCurrency(event.target.value)} />
            </label>
            <label className="commercial-wide-label">
              {copy.constraintsLabel}
              <textarea value={constraintsDraft} onChange={(event) => setConstraintsDraft(event.target.value)} />
            </label>
          </div>
          <button className="primary-button" onClick={() => void createOperation()} disabled={!title.trim() || !objective.trim() || actionState.loading}>
            <Target size={15} />
            {copy.createAction}
          </button>
        </Panel>

        <Panel title={copy.actionResult} description={actionState.updatedAt ? `${textFor(language, "lastUpdated")}: ${actionState.updatedAt}` : undefined}>
          <LoadNotice state={actionState} />
          <JsonPreview value={actionState.data || { status: "no action yet" }} />
        </Panel>
      </div>

      <Panel title={copy.listTitle} action={<RefreshButton onClick={load} />}>
        <LoadNotice state={state} />
        {state.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {state.updatedAt}</div> : null}
        <Table
          rows={operations}
          emptyLabel={copy.noOperations}
          selectedId={selectedOperation ? valueAt(selectedOperation, ["id"]) : null}
          onSelect={(row) => setSelectedOperation(row)}
          columns={[
            { key: "title", label: copy.titleLabel },
            { key: "status", label: copy.statusColumn },
            { key: "priority", label: copy.priorityColumn },
            { key: "risk_level", label: copy.riskColumn },
            { key: "knowledge_collection", label: copy.collectionLabel },
            { key: "updated_at", label: copy.updatedColumn },
          ]}
        />
      </Panel>

      <Panel title={copy.detailTitle} description={copy.detailDescription}>
        {selectedOperation ? (
          <div className="commercial-detail-grid">
            <Field label={copy.titleLabel} value={valueAt(selectedOperation, ["title"])} />
            <Field label={copy.statusColumn} value={<StatusPill value={valueAt(selectedOperation, ["status"])} />} />
            <Field label={copy.priorityColumn} value={<StatusPill value={valueAt(selectedOperation, ["priority"])} />} />
            <Field label={copy.riskColumn} value={<StatusPill value={valueAt(selectedOperation, ["risk_level"])} />} />
            <Field label={copy.collectionLabel} value={valueAt(selectedOperation, ["knowledge_collection"])} />
            <Field label={copy.metricsLabel} value={shortJson(selectedOperation.success_metrics)} />
            <Field label={copy.channelsLabel} value={shortJson(selectedOperation.channels)} />
            <Field label={copy.constraintsLabel} value={shortJson(selectedOperation.constraints)} />
            <Field label={copy.objectiveLabel} value={valueAt(selectedOperation, ["objective"])} />
          </div>
        ) : (
          <div className="empty-table">{copy.selectedHint}</div>
        )}
        <div className="commercial-action-row">
          <button className="primary-button" onClick={() => void regeneratePlan()} disabled={!selectedOperation || actionState.loading}>
            <Sparkles size={15} />
            {copy.planAction}
          </button>
          <button className="ghost-button" onClick={() => void updateSelectedStatus("ready")} disabled={!selectedOperation || actionState.loading}>
            <ShieldCheck size={15} />
            {copy.markReady}
          </button>
          <button className="ghost-button" onClick={() => void updateSelectedStatus("active")} disabled={!selectedOperation || actionState.loading}>
            <PlayCircle size={15} />
            {copy.activate}
          </button>
          <button className="ghost-button" onClick={() => void updateSelectedStatus("paused")} disabled={!selectedOperation || actionState.loading}>
            <AlertTriangle size={15} />
            {copy.pause}
          </button>
        </div>
        <h3>{copy.planTitle}</h3>
        <Table
          rows={planRows}
          emptyLabel={copy.noPlan}
          columns={[
            { key: "step_key", label: "step_key" },
            { key: "title", label: copy.titleLabel },
            { key: "owner", label: "owner" },
            { key: "status", label: copy.statusColumn },
            { key: "checks", label: "checks" },
          ]}
        />
      </Panel>

      <Panel title={contentCopy.title} description={contentCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-content-grid">
              <label>
                {contentCopy.stepLabel}
                <select value={contentStepKey} onChange={(event) => setContentStepKey(event.target.value)}>
                  {planRows.length ? null : <option value={contentStepKey}>{contentStepKey}</option>}
                  {planRows.map((step) => {
                    const stepKey = valueAt(step, ["step_key"], "");
                    return (
                      <option value={stepKey} key={stepKey}>
                        {stepKey} / {valueAt(step, ["title"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {contentCopy.channelLabel}
                <input value={contentChannel} onChange={(event) => setContentChannel(event.target.value)} />
              </label>
              <label>
                {contentCopy.formatLabel}
                <select value={contentFormat} onChange={(event) => setContentFormat(event.target.value)}>
                  <option value="copy">copy</option>
                  <option value="email">email</option>
                  <option value="post">post</option>
                  <option value="script">script</option>
                  <option value="landing_page">landing_page</option>
                  <option value="ad">ad</option>
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={contentTitle} onChange={(event) => setContentTitle(event.target.value)} />
              </label>
              <label>
                {contentCopy.audienceLabel}
                <input value={contentAudienceSegment} onChange={(event) => setContentAudienceSegment(event.target.value)} />
              </label>
              <label>
                {contentCopy.ctaLabel}
                <input value={contentCallToAction} onChange={(event) => setContentCallToAction(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {contentCopy.summaryLabel}
                <textarea value={contentSummary} onChange={(event) => setContentSummary(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {contentCopy.bodyLabel}
                <textarea value={contentBody} onChange={(event) => setContentBody(event.target.value)} />
              </label>
              <label>
                {contentCopy.sourceMaterialsLabel}
                <textarea value={sourceMaterialsDraft} onChange={(event) => setSourceMaterialsDraft(event.target.value)} />
              </label>
              <label>
                {contentCopy.queryLabel}
                <textarea value={contentRagQuery} onChange={(event) => setContentRagQuery(event.target.value)} />
              </label>
              <label>
                {contentCopy.searchModeLabel}
                <select value={contentSearchMode} onChange={(event) => setContentSearchMode(event.target.value)}>
                  <option value="hybrid">hybrid</option>
                  <option value="keyword">keyword</option>
                  <option value="dense">dense</option>
                </select>
              </label>
              <label>
                {contentCopy.assetRequestsLabel}
                <textarea value={assetRequestsDraft} onChange={(event) => setAssetRequestsDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createOperationContentDraft()}
                disabled={!contentStepKey.trim() || !contentChannel.trim() || !contentTitle.trim() || actionState.loading}
              >
                <FileText size={15} />
                {contentCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void generateOperationContentDraft()}
                disabled={!contentStepKey.trim() || !contentChannel.trim() || !contentTitle.trim() || actionState.loading}
              >
                <Search size={15} />
                {contentCopy.generateAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateOperationContentDraft()}
                disabled={!selectedContentDraftId || !contentTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {contentCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={contentDraftsState} />
            {contentDraftsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {contentDraftsState.updatedAt}</div> : null}
            {contentDrafts.length ? (
              <div className="commercial-content-list">
                {contentDrafts.map((draft) => {
                  const draftId = valueAt(draft, ["id"], "");
                  const draftStatus = valueAt(draft, ["draft_status"], "");
                  return (
                    <article className="commercial-content-item" key={draftId}>
                      <div>
                        <strong>{valueAt(draft, ["title"])}</strong>
                        <span>{valueAt(draft, ["step_key"])} / {valueAt(draft, ["channel"])} / {valueAt(draft, ["content_format"])}</span>
                        <p>{valueAt(draft, ["summary"], valueAt(draft, ["content_body"], ""))}</p>
                        <p>{shortJson(draft.asset_requests, 90)}</p>
                        <StatusPill value={draftStatus} />
                      </div>
                      <div className="commercial-content-actions">
                        <button className="ghost-button" onClick={() => editOperationContentDraft(draft)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {contentCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationContentDraft(draftId, "ready")}
                          disabled={!["draft", "rejected"].includes(draftStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {contentCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationContentDraft(draftId, "approve")}
                          disabled={draftStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {contentCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationContentDraft(draftId, "reject")}
                          disabled={draftStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {contentCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationContentDraft(draftId, "archive")}
                          disabled={draftStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {contentCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{contentCopy.noDrafts}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{contentCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={assetCopy.title} description={assetCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-asset-grid">
              <label>
                {contentCopy.stepLabel}
                <select value={assetStepKey} onChange={(event) => setAssetStepKey(event.target.value)}>
                  {planRows.length ? null : <option value={assetStepKey}>{assetStepKey}</option>}
                  {planRows.map((step) => {
                    const stepKey = valueAt(step, ["step_key"], "");
                    return (
                      <option value={stepKey} key={stepKey}>
                        {stepKey} / {valueAt(step, ["title"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {assetCopy.sourceDraftLabel}
                <select value={assetContentDraftId} onChange={(event) => setAssetContentDraftId(event.target.value)}>
                  <option value="">-</option>
                  {contentDrafts.map((draft) => {
                    const draftId = valueAt(draft, ["id"], "");
                    return (
                      <option value={draftId} key={draftId}>
                        {valueAt(draft, ["title"])} / {valueAt(draft, ["draft_status"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {contentCopy.channelLabel}
                <input value={assetChannel} onChange={(event) => setAssetChannel(event.target.value)} />
              </label>
              <label>
                {assetCopy.typeLabel}
                <select value={assetType} onChange={(event) => setAssetType(event.target.value)}>
                  <option value="image">image</option>
                  <option value="video">video</option>
                  <option value="audio">audio</option>
                  <option value="document">document</option>
                  <option value="design">design</option>
                  <option value="copy_asset">copy_asset</option>
                  <option value="other">other</option>
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={assetTitle} onChange={(event) => setAssetTitle(event.target.value)} />
              </label>
              <label>
                {assetCopy.dimensionsLabel}
                <input value={assetDimensions} onChange={(event) => setAssetDimensions(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {assetCopy.purposeLabel}
                <textarea value={assetPurpose} onChange={(event) => setAssetPurpose(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {assetCopy.styleLabel}
                <textarea value={assetStyleConstraints} onChange={(event) => setAssetStyleConstraints(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {assetCopy.promptLabel}
                <textarea value={assetPrompt} onChange={(event) => setAssetPrompt(event.target.value)} />
              </label>
              <label>
                {assetCopy.negativePromptLabel}
                <textarea value={assetNegativePrompt} onChange={(event) => setAssetNegativePrompt(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {assetCopy.queryLabel}
                <textarea value={assetRagQuery} onChange={(event) => setAssetRagQuery(event.target.value)} />
              </label>
              <label>
                {assetCopy.searchModeLabel}
                <select value={assetSearchMode} onChange={(event) => setAssetSearchMode(event.target.value)}>
                  <option value="hybrid">hybrid</option>
                  <option value="keyword">keyword</option>
                  <option value="dense">dense</option>
                </select>
              </label>
              <label>
                {contentCopy.sourceMaterialsLabel}
                <textarea value={assetSourceMaterialsDraft} onChange={(event) => setAssetSourceMaterialsDraft(event.target.value)} />
              </label>
              <label>
                {assetCopy.readinessLabel}
                <textarea value={assetReadinessChecksDraft} onChange={(event) => setAssetReadinessChecksDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createOperationAssetRequest()}
                disabled={!assetStepKey.trim() || !assetChannel.trim() || !assetTitle.trim() || actionState.loading}
              >
                <FileText size={15} />
                {assetCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void generateOperationAssetRequest()}
                disabled={!assetStepKey.trim() || !assetChannel.trim() || actionState.loading}
              >
                <Search size={15} />
                {assetCopy.generateAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateOperationAssetRequest()}
                disabled={!selectedAssetRequestId || !assetTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {assetCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={assetRequestsState} />
            {assetRequestsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {assetRequestsState.updatedAt}</div> : null}
            {assetRequests.length ? (
              <div className="commercial-asset-list">
                {assetRequests.map((assetRequest) => {
                  const assetRequestId = valueAt(assetRequest, ["id"], "");
                  const requestStatus = valueAt(assetRequest, ["request_status"], "");
                  return (
                    <article className="commercial-asset-item" key={assetRequestId}>
                      <div>
                        <strong>{valueAt(assetRequest, ["title"])}</strong>
                        <span>{valueAt(assetRequest, ["step_key"])} / {valueAt(assetRequest, ["channel"])} / {valueAt(assetRequest, ["asset_type"])}</span>
                        <p>{valueAt(assetRequest, ["purpose"], valueAt(assetRequest, ["generation_prompt"], ""))}</p>
                        <p>{shortJson(assetRequest.handoff_payload, 90)}</p>
                        <StatusPill value={requestStatus} />
                      </div>
                      <div className="commercial-asset-actions">
                        <button className="ghost-button" onClick={() => editOperationAssetRequest(assetRequest)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {assetCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationAssetRequest(assetRequestId, "ready")}
                          disabled={!["draft", "rejected", "failed"].includes(requestStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {assetCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationAssetRequest(assetRequestId, "approve")}
                          disabled={requestStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {assetCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationAssetRequest(assetRequestId, "reject")}
                          disabled={requestStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {assetCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationAssetRequest(assetRequestId, "prepare")}
                          disabled={requestStatus !== "approved" || actionState.loading}
                        >
                          <PlayCircle size={15} />
                          {assetCopy.prepareAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationAssetRequest(assetRequestId, "fail")}
                          disabled={requestStatus !== "approved" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {assetCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationAssetRequest(assetRequestId, "archive")}
                          disabled={requestStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {assetCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{assetCopy.noRequests}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{assetCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={comfyuiCopy.title} description={comfyuiCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-asset-grid">
              <label>
                {comfyuiCopy.assetLabel}
                <select value={comfyuiAssetRequestId} onChange={(event) => setComfyuiAssetRequestId(event.target.value)}>
                  {eligibleComfyuiAssets.length ? null : <option value="">{comfyuiCopy.requiresAsset}</option>}
                  {eligibleComfyuiAssets.map((assetRequest) => {
                    const assetRequestId = valueAt(assetRequest, ["id"], "");
                    return (
                      <option value={assetRequestId} key={assetRequestId}>
                        {valueAt(assetRequest, ["title"])} / {valueAt(assetRequest, ["request_status"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={comfyuiTitle} onChange={(event) => setComfyuiTitle(event.target.value)} />
              </label>
              <label>
                {comfyuiCopy.workflowLabel}
                <input value={comfyuiWorkflowName} onChange={(event) => setComfyuiWorkflowName(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiCopy.promptPayloadLabel}
                <textarea value={comfyuiPromptPayloadDraft} onChange={(event) => setComfyuiPromptPayloadDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiCopy.workflowPayloadLabel}
                <textarea value={comfyuiWorkflowPayloadDraft} onChange={(event) => setComfyuiWorkflowPayloadDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiCopy.readinessLabel}
                <textarea value={comfyuiReadinessChecksDraft} onChange={(event) => setComfyuiReadinessChecksDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createComfyuiHandoff()}
                disabled={!comfyuiAssetRequestId || !comfyuiTitle.trim() || actionState.loading}
              >
                <Package size={15} />
                {comfyuiCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateComfyuiHandoff()}
                disabled={!selectedComfyuiHandoffId || !comfyuiTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {comfyuiCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={comfyuiHandoffsState} />
            {comfyuiHandoffsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {comfyuiHandoffsState.updatedAt}</div> : null}
            {comfyuiHandoffs.length ? (
              <div className="commercial-asset-list">
                {comfyuiHandoffs.map((handoff) => {
                  const handoffId = valueAt(handoff, ["id"], "");
                  const handoffStatus = valueAt(handoff, ["handoff_status"], "");
                  return (
                    <article className="commercial-asset-item" key={handoffId}>
                      <div>
                        <strong>{valueAt(handoff, ["title"])}</strong>
                        <span>{valueAt(handoff, ["channel"])} / {valueAt(handoff, ["asset_type"])} / {valueAt(handoff, ["workflow_name"])}</span>
                        <p>{shortJson(handoff.prompt_payload, 90)}</p>
                        <p>{shortJson(handoff.handoff_payload, 90)}</p>
                        <StatusPill value={handoffStatus} />
                      </div>
                      <div className="commercial-asset-actions">
                        <button className="ghost-button" onClick={() => editComfyuiHandoff(handoff)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {comfyuiCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiHandoff(handoffId, "ready")}
                          disabled={!["draft", "rejected", "failed"].includes(handoffStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {comfyuiCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiHandoff(handoffId, "approve")}
                          disabled={handoffStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {comfyuiCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiHandoff(handoffId, "reject")}
                          disabled={handoffStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiHandoff(handoffId, "prepare")}
                          disabled={handoffStatus !== "approved" || actionState.loading}
                        >
                          <PlayCircle size={15} />
                          {comfyuiCopy.prepareAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiHandoff(handoffId, "fail")}
                          disabled={handoffStatus !== "approved" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiHandoff(handoffId, "archive")}
                          disabled={handoffStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{eligibleComfyuiAssets.length ? comfyuiCopy.noHandoffs : comfyuiCopy.requiresAsset}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{comfyuiCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={comfyuiAdapterCopy.title} description={comfyuiAdapterCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-asset-grid">
              <label>
                {copy.titleLabel}
                <input value={comfyuiAdapterTitle} onChange={(event) => setComfyuiAdapterTitle(event.target.value)} />
              </label>
              <label>
                {comfyuiAdapterCopy.targetLabel}
                <input value={comfyuiAdapterTargetUrl} onChange={(event) => setComfyuiAdapterTargetUrl(event.target.value)} />
              </label>
              <label>
                {comfyuiAdapterCopy.authModeLabel}
                <select value={comfyuiAdapterAuthMode} onChange={(event) => setComfyuiAdapterAuthMode(event.target.value)}>
                  <option value="none">none</option>
                  <option value="token_ref">token_ref</option>
                  <option value="basic_ref">basic_ref</option>
                  <option value="custom_ref">custom_ref</option>
                </select>
              </label>
              <label>
                {comfyuiAdapterCopy.secretRefLabel}
                <input value={comfyuiAdapterSecretRef} onChange={(event) => setComfyuiAdapterSecretRef(event.target.value)} placeholder="secret://comfyui/token" />
              </label>
              <label>
                {comfyuiAdapterCopy.queueLabel}
                <input value={comfyuiAdapterQueueName} onChange={(event) => setComfyuiAdapterQueueName(event.target.value)} />
              </label>
              <label>
                {comfyuiAdapterCopy.workflowLabel}
                <input value={comfyuiAdapterDefaultWorkflow} onChange={(event) => setComfyuiAdapterDefaultWorkflow(event.target.value)} />
              </label>
              <label>
                {comfyuiAdapterCopy.allowedWorkflowsLabel}
                <textarea value={comfyuiAdapterAllowedWorkflowsDraft} onChange={(event) => setComfyuiAdapterAllowedWorkflowsDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiAdapterCopy.modelInventoryLabel}
                <textarea value={comfyuiAdapterModelInventoryDraft} onChange={(event) => setComfyuiAdapterModelInventoryDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiAdapterCopy.runtimeLimitsLabel}
                <textarea value={comfyuiAdapterRuntimeLimitsDraft} onChange={(event) => setComfyuiAdapterRuntimeLimitsDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiAdapterCopy.notesLabel}
                <textarea value={comfyuiAdapterMaintenanceNotes} onChange={(event) => setComfyuiAdapterMaintenanceNotes(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiAdapterCopy.checksLabel}
                <textarea value={comfyuiAdapterValidationChecksDraft} onChange={(event) => setComfyuiAdapterValidationChecksDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createComfyuiAdapterConfig()}
                disabled={!comfyuiAdapterTitle.trim() || actionState.loading}
              >
                <Settings size={15} />
                {comfyuiAdapterCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateComfyuiAdapterConfig()}
                disabled={!selectedComfyuiAdapterConfigId || !comfyuiAdapterTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {comfyuiAdapterCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={comfyuiAdapterConfigsState} />
            {comfyuiAdapterConfigsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {comfyuiAdapterConfigsState.updatedAt}</div> : null}
            {comfyuiAdapterConfigs.length ? (
              <div className="commercial-asset-list">
                {comfyuiAdapterConfigs.map((config) => {
                  const configId = valueAt(config, ["id"], "");
                  const configStatus = valueAt(config, ["config_status"], "");
                  return (
                    <article className="commercial-asset-item" key={configId}>
                      <div>
                        <strong>{valueAt(config, ["title"])}</strong>
                        <span>{valueAt(config, ["target_url"], "-")} / {valueAt(config, ["queue_name"], "-")} / {valueAt(config, ["default_workflow_name"], "-")}</span>
                        <p>{shortJson(config.runtime_limits, 90)}</p>
                        <p>{shortJson(config.config_payload, 90)}</p>
                        <StatusPill value={configStatus} />
                      </div>
                      <div className="commercial-asset-actions">
                        <button className="ghost-button" onClick={() => editComfyuiAdapterConfig(config)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {comfyuiAdapterCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiAdapterConfig(configId, "validate")}
                          disabled={configStatus === "archived" || actionState.loading}
                        >
                          <Gauge size={15} />
                          {comfyuiAdapterCopy.validateAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiAdapterConfig(configId, "fail")}
                          disabled={["failed", "archived"].includes(configStatus) || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiAdapterCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiAdapterConfig(configId, "archive")}
                          disabled={configStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiAdapterCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{comfyuiAdapterCopy.noConfigs}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{comfyuiAdapterCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={comfyuiPreflightCopy.title} description={comfyuiPreflightCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-asset-grid">
              <label>
                {comfyuiPreflightCopy.handoffLabel}
                <select value={comfyuiPreflightHandoffId} onChange={(event) => setComfyuiPreflightHandoffId(event.target.value)}>
                  {eligibleComfyuiHandoffs.length ? null : <option value="">{comfyuiPreflightCopy.requiresHandoff}</option>}
                  {eligibleComfyuiHandoffs.map((handoff) => {
                    const handoffId = valueAt(handoff, ["id"], "");
                    return (
                      <option value={handoffId} key={handoffId}>
                        {valueAt(handoff, ["title"])} / {valueAt(handoff, ["handoff_status"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {comfyuiAdapterCopy.title}
                <select value={comfyuiPreflightAdapterConfigId} onChange={(event) => setComfyuiPreflightAdapterConfigId(event.target.value)}>
                  <option value="">-</option>
                  {comfyuiAdapterConfigs.map((config) => {
                    const configId = valueAt(config, ["id"], "");
                    return (
                      <option value={configId} key={configId}>
                        {valueAt(config, ["title"])} / {valueAt(config, ["config_status"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={comfyuiPreflightTitle} onChange={(event) => setComfyuiPreflightTitle(event.target.value)} />
              </label>
              <label>
                {comfyuiPreflightCopy.targetLabel}
                <input value={comfyuiPreflightTargetUrl} onChange={(event) => setComfyuiPreflightTargetUrl(event.target.value)} />
              </label>
              <label>
                {comfyuiPreflightCopy.queueLabel}
                <input value={comfyuiPreflightQueueName} onChange={(event) => setComfyuiPreflightQueueName(event.target.value)} />
              </label>
              <label>
                {comfyuiPreflightCopy.workflowLabel}
                <input value={comfyuiPreflightWorkflowName} onChange={(event) => setComfyuiPreflightWorkflowName(event.target.value)} />
              </label>
              <label>
                {comfyuiPreflightCopy.modelRefsLabel}
                <input value={comfyuiPreflightModelRefsDraft} onChange={(event) => setComfyuiPreflightModelRefsDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiPreflightCopy.adapterConfigLabel}
                <textarea value={comfyuiPreflightAdapterConfigDraft} onChange={(event) => setComfyuiPreflightAdapterConfigDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiPreflightCopy.checkItemsLabel}
                <textarea value={comfyuiPreflightCheckItemsDraft} onChange={(event) => setComfyuiPreflightCheckItemsDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createComfyuiPreflight()}
                disabled={!comfyuiPreflightHandoffId || !comfyuiPreflightTitle.trim() || actionState.loading}
              >
                <Gauge size={15} />
                {comfyuiPreflightCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateComfyuiPreflight()}
                disabled={!selectedComfyuiPreflightId || !comfyuiPreflightTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {comfyuiPreflightCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={comfyuiPreflightsState} />
            {comfyuiPreflightsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {comfyuiPreflightsState.updatedAt}</div> : null}
            {comfyuiPreflights.length ? (
              <div className="commercial-asset-list">
                {comfyuiPreflights.map((preflight) => {
                  const preflightId = valueAt(preflight, ["id"], "");
                  const preflightStatus = valueAt(preflight, ["preflight_status"], "");
                  return (
                    <article className="commercial-asset-item" key={preflightId}>
                      <div>
                        <strong>{valueAt(preflight, ["title"])}</strong>
                        <span>{valueAt(preflight, ["target_url"], "-")} / {valueAt(preflight, ["queue_name"], "-")} / {valueAt(preflight, ["workflow_name"])}</span>
                        <p>{shortJson(preflight.check_items, 90)}</p>
                        <p>{shortJson(preflight.preflight_payload, 90)}</p>
                        <StatusPill value={preflightStatus} />
                      </div>
                      <div className="commercial-asset-actions">
                        <button className="ghost-button" onClick={() => editComfyuiPreflight(preflight)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {comfyuiPreflightCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiPreflight(preflightId, "check")}
                          disabled={preflightStatus === "archived" || actionState.loading}
                        >
                          <Gauge size={15} />
                          {comfyuiPreflightCopy.checkAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiPreflight(preflightId, "fail")}
                          disabled={["failed", "archived"].includes(preflightStatus) || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiPreflightCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiPreflight(preflightId, "archive")}
                          disabled={preflightStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiPreflightCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{eligibleComfyuiHandoffs.length ? comfyuiPreflightCopy.noPreflights : comfyuiPreflightCopy.requiresHandoff}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{comfyuiPreflightCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={comfyuiJobCopy.title} description={comfyuiJobCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-asset-grid">
              <label>
                {comfyuiJobCopy.preflightLabel}
                <select value={comfyuiJobPreflightId} onChange={(event) => setComfyuiJobPreflightId(event.target.value)}>
                  {checkedComfyuiPreflights.length ? null : <option value="">{comfyuiJobCopy.requiresPreflight}</option>}
                  {checkedComfyuiPreflights.map((preflight) => {
                    const preflightId = valueAt(preflight, ["id"], "");
                    return (
                      <option value={preflightId} key={preflightId}>
                        {valueAt(preflight, ["title"])} / {valueAt(preflight, ["queue_name"], "-")} / {valueAt(preflight, ["workflow_name"], "-")}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={comfyuiJobTitle} onChange={(event) => setComfyuiJobTitle(event.target.value)} />
              </label>
              <label>
                {comfyuiJobCopy.priorityLabel}
                <select value={comfyuiJobPriority} onChange={(event) => setComfyuiJobPriority(event.target.value as "low" | "normal" | "high")}>
                  <option value="low">low</option>
                  <option value="normal">normal</option>
                  <option value="high">high</option>
                </select>
              </label>
              <label>
                {comfyuiJobCopy.outputsLabel}
                <textarea value={comfyuiJobOutputsDraft} onChange={(event) => setComfyuiJobOutputsDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiJobCopy.runtimePayloadLabel}
                <textarea value={comfyuiJobRuntimePayloadDraft} onChange={(event) => setComfyuiJobRuntimePayloadDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiJobCopy.safetyChecksLabel}
                <textarea value={comfyuiJobSafetyChecksDraft} onChange={(event) => setComfyuiJobSafetyChecksDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiJobCopy.recoveryLabel}
                <textarea value={comfyuiJobRecoveryDraft} onChange={(event) => setComfyuiJobRecoveryDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createComfyuiJobRequest()}
                disabled={!comfyuiJobPreflightId || !comfyuiJobTitle.trim() || actionState.loading}
              >
                <Send size={15} />
                {comfyuiJobCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateComfyuiJobRequest()}
                disabled={!selectedComfyuiJobRequestId || !comfyuiJobTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {comfyuiJobCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={comfyuiJobRequestsState} />
            {comfyuiJobRequestsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {comfyuiJobRequestsState.updatedAt}</div> : null}
            {comfyuiJobRequests.length ? (
              <div className="commercial-asset-list">
                {comfyuiJobRequests.map((jobRequest) => {
                  const jobRequestId = valueAt(jobRequest, ["id"], "");
                  const jobStatus = valueAt(jobRequest, ["job_status"], "");
                  return (
                    <article className="commercial-asset-item" key={jobRequestId}>
                      <div>
                        <strong>{valueAt(jobRequest, ["title"])}</strong>
                        <span>{valueAt(jobRequest, ["queue_name"], "-")} / {valueAt(jobRequest, ["workflow_name"], "-")} / {valueAt(jobRequest, ["priority"], "normal")}</span>
                        <p>{shortJson(jobRequest.safety_checks, 90)}</p>
                        <p>{shortJson(jobRequest.job_payload, 90)}</p>
                        <StatusPill value={jobStatus} />
                      </div>
                      <div className="commercial-asset-actions">
                        <button className="ghost-button" onClick={() => editComfyuiJobRequest(jobRequest)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {comfyuiJobCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiJobRequest(jobRequestId, "ready")}
                          disabled={!["draft", "rejected", "failed"].includes(jobStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {comfyuiJobCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiJobRequest(jobRequestId, "approve")}
                          disabled={jobStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {comfyuiJobCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiJobRequest(jobRequestId, "reject")}
                          disabled={jobStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiJobCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiJobRequest(jobRequestId, "queue")}
                          disabled={jobStatus !== "approved" || actionState.loading}
                        >
                          <PlayCircle size={15} />
                          {comfyuiJobCopy.queueAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiJobRequest(jobRequestId, "fail")}
                          disabled={!["approved", "queued"].includes(jobStatus) || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiJobCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiJobRequest(jobRequestId, "cancel")}
                          disabled={["cancelled", "archived"].includes(jobStatus) || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiJobCopy.cancelAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiJobRequest(jobRequestId, "archive")}
                          disabled={jobStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiJobCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{checkedComfyuiPreflights.length ? comfyuiJobCopy.noRequests : comfyuiJobCopy.requiresPreflight}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{comfyuiJobCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={comfyuiExecutionCopy.title} description={comfyuiExecutionCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-asset-grid">
              <label>
                {comfyuiExecutionCopy.jobRequestLabel}
                <select value={comfyuiExecutionJobRequestId} onChange={(event) => setComfyuiExecutionJobRequestId(event.target.value)}>
                  {actionableComfyuiJobRequests.length ? null : <option value="">{comfyuiExecutionCopy.requiresJobRequest}</option>}
                  {actionableComfyuiJobRequests.map((jobRequest) => {
                    const jobRequestId = valueAt(jobRequest, ["id"], "");
                    return (
                      <option value={jobRequestId} key={jobRequestId}>
                        {valueAt(jobRequest, ["title"])} / {valueAt(jobRequest, ["job_status"], "-")} / {valueAt(jobRequest, ["workflow_name"], "-")}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={comfyuiExecutionTitle} onChange={(event) => setComfyuiExecutionTitle(event.target.value)} />
              </label>
              <label>
                {comfyuiExecutionCopy.priorityLabel}
                <select value={comfyuiExecutionPriority} onChange={(event) => setComfyuiExecutionPriority(event.target.value as "low" | "normal" | "high")}>
                  <option value="low">low</option>
                  <option value="normal">normal</option>
                  <option value="high">high</option>
                </select>
              </label>
              <label>
                {comfyuiExecutionCopy.checklistLabel}
                <textarea value={comfyuiExecutionChecklistDraft} onChange={(event) => setComfyuiExecutionChecklistDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiExecutionCopy.stepsLabel}
                <textarea value={comfyuiExecutionStepsDraft} onChange={(event) => setComfyuiExecutionStepsDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiExecutionCopy.checksLabel}
                <textarea value={comfyuiExecutionChecksDraft} onChange={(event) => setComfyuiExecutionChecksDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiExecutionCopy.simulationPayloadLabel}
                <textarea value={comfyuiExecutionSimulationPayloadDraft} onChange={(event) => setComfyuiExecutionSimulationPayloadDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiExecutionCopy.rollbackLabel}
                <textarea value={comfyuiExecutionRollbackDraft} onChange={(event) => setComfyuiExecutionRollbackDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createComfyuiExecutionPlan()}
                disabled={!comfyuiExecutionJobRequestId || !comfyuiExecutionTitle.trim() || actionState.loading}
              >
                <Send size={15} />
                {comfyuiExecutionCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateComfyuiExecutionPlan()}
                disabled={!selectedComfyuiExecutionPlanId || !comfyuiExecutionTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {comfyuiExecutionCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={comfyuiExecutionPlansState} />
            {comfyuiExecutionPlansState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {comfyuiExecutionPlansState.updatedAt}</div> : null}
            {comfyuiExecutionPlans.length ? (
              <div className="commercial-asset-list">
                {comfyuiExecutionPlans.map((executionPlan) => {
                  const executionPlanId = valueAt(executionPlan, ["id"], "");
                  const planStatus = valueAt(executionPlan, ["plan_status"], "");
                  return (
                    <article className="commercial-asset-item" key={executionPlanId}>
                      <div>
                        <strong>{valueAt(executionPlan, ["title"])}</strong>
                        <span>{valueAt(executionPlan, ["queue_name"], "-")} / {valueAt(executionPlan, ["workflow_name"], "-")} / {valueAt(executionPlan, ["priority"], "normal")}</span>
                        <p>{shortJson(executionPlan.simulation_checks, 90)}</p>
                        <p>{shortJson(executionPlan.plan_payload, 90)}</p>
                        <StatusPill value={planStatus} />
                      </div>
                      <div className="commercial-asset-actions">
                        <button className="ghost-button" onClick={() => editComfyuiExecutionPlan(executionPlan)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {comfyuiExecutionCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiExecutionPlan(executionPlanId, "ready")}
                          disabled={!["draft", "rejected", "failed"].includes(planStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {comfyuiExecutionCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiExecutionPlan(executionPlanId, "approve")}
                          disabled={planStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {comfyuiExecutionCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiExecutionPlan(executionPlanId, "reject")}
                          disabled={planStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiExecutionCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiExecutionPlan(executionPlanId, "simulate")}
                          disabled={planStatus !== "approved" || actionState.loading}
                        >
                          <PlayCircle size={15} />
                          {comfyuiExecutionCopy.simulateAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiExecutionPlan(executionPlanId, "fail")}
                          disabled={planStatus !== "approved" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiExecutionCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiExecutionPlan(executionPlanId, "cancel")}
                          disabled={["cancelled", "archived"].includes(planStatus) || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiExecutionCopy.cancelAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiExecutionPlan(executionPlanId, "archive")}
                          disabled={planStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiExecutionCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{actionableComfyuiJobRequests.length ? comfyuiExecutionCopy.noPlans : comfyuiExecutionCopy.requiresJobRequest}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{comfyuiExecutionCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={comfyuiProbeCopy.title} description={comfyuiProbeCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-asset-grid">
              <label>
                {comfyuiProbeCopy.executionPlanLabel}
                <select value={comfyuiProbeExecutionPlanId} onChange={(event) => setComfyuiProbeExecutionPlanId(event.target.value)}>
                  {actionableComfyuiExecutionPlans.length ? null : <option value="">{comfyuiProbeCopy.requiresExecutionPlan}</option>}
                  {actionableComfyuiExecutionPlans.map((executionPlan) => {
                    const executionPlanId = valueAt(executionPlan, ["id"], "");
                    return (
                      <option value={executionPlanId} key={executionPlanId}>
                        {valueAt(executionPlan, ["title"])} / {valueAt(executionPlan, ["plan_status"], "-")} / {valueAt(executionPlan, ["workflow_name"], "-")}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={comfyuiProbeTitle} onChange={(event) => setComfyuiProbeTitle(event.target.value)} />
              </label>
              <label>
                {comfyuiProbeCopy.modeLabel}
                <select value={comfyuiProbeMode} onChange={(event) => setComfyuiProbeMode(event.target.value)}>
                  <option value="metadata_only">metadata_only</option>
                  <option value="future_read_only_probe">future_read_only_probe</option>
                </select>
              </label>
              <label>
                {comfyuiProbeCopy.healthEndpointLabel}
                <input value={comfyuiProbeHealthEndpoint} onChange={(event) => setComfyuiProbeHealthEndpoint(event.target.value)} />
              </label>
              <label>
                {comfyuiProbeCopy.queueEndpointLabel}
                <input value={comfyuiProbeQueueEndpoint} onChange={(event) => setComfyuiProbeQueueEndpoint(event.target.value)} />
              </label>
              <label>
                {comfyuiProbeCopy.routesLabel}
                <textarea value={comfyuiProbeRoutesDraft} onChange={(event) => setComfyuiProbeRoutesDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiProbeCopy.checksLabel}
                <textarea value={comfyuiProbeChecksDraft} onChange={(event) => setComfyuiProbeChecksDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiProbeCopy.payloadLabel}
                <textarea value={comfyuiProbePayloadDraft} onChange={(event) => setComfyuiProbePayloadDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiProbeCopy.healthSnapshotLabel}
                <textarea value={comfyuiProbeHealthSnapshotDraft} onChange={(event) => setComfyuiProbeHealthSnapshotDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiProbeCopy.queueSnapshotLabel}
                <textarea value={comfyuiProbeQueueSnapshotDraft} onChange={(event) => setComfyuiProbeQueueSnapshotDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiProbeCopy.schemaLabel}
                <textarea value={comfyuiProbeSchemaDraft} onChange={(event) => setComfyuiProbeSchemaDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createComfyuiConnectionProbe()}
                disabled={!comfyuiProbeExecutionPlanId || !comfyuiProbeTitle.trim() || actionState.loading}
              >
                <Send size={15} />
                {comfyuiProbeCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateComfyuiConnectionProbe()}
                disabled={!selectedComfyuiConnectionProbeId || !comfyuiProbeTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {comfyuiProbeCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={comfyuiConnectionProbesState} />
            {comfyuiConnectionProbesState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {comfyuiConnectionProbesState.updatedAt}</div> : null}
            {comfyuiConnectionProbes.length ? (
              <div className="commercial-asset-list">
                {comfyuiConnectionProbes.map((probe) => {
                  const connectionProbeId = valueAt(probe, ["id"], "");
                  const probeStatus = valueAt(probe, ["probe_status"], "");
                  return (
                    <article className="commercial-asset-item" key={connectionProbeId}>
                      <div>
                        <strong>{valueAt(probe, ["title"])}</strong>
                        <span>{valueAt(probe, ["target_url"], "-")} / {valueAt(probe, ["health_endpoint"], "-")} / {valueAt(probe, ["queue_endpoint"], "-")}</span>
                        <p>{shortJson(probe.readiness_checks, 90)}</p>
                        <p>{shortJson(probe.probe_plan_payload, 90)}</p>
                        <StatusPill value={probeStatus} />
                      </div>
                      <div className="commercial-asset-actions">
                        <button className="ghost-button" onClick={() => editComfyuiConnectionProbe(probe)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {comfyuiProbeCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiConnectionProbe(connectionProbeId, "ready")}
                          disabled={!["draft", "rejected", "failed"].includes(probeStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {comfyuiProbeCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiConnectionProbe(connectionProbeId, "approve")}
                          disabled={probeStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {comfyuiProbeCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiConnectionProbe(connectionProbeId, "reject")}
                          disabled={probeStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiProbeCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiConnectionProbe(connectionProbeId, "probe")}
                          disabled={probeStatus !== "approved" || actionState.loading}
                        >
                          <PlayCircle size={15} />
                          {comfyuiProbeCopy.probeAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiConnectionProbe(connectionProbeId, "fail")}
                          disabled={probeStatus !== "approved" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiProbeCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiConnectionProbe(connectionProbeId, "cancel")}
                          disabled={["cancelled", "archived"].includes(probeStatus) || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiProbeCopy.cancelAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiConnectionProbe(connectionProbeId, "archive")}
                          disabled={probeStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiProbeCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{actionableComfyuiExecutionPlans.length ? comfyuiProbeCopy.noProbes : comfyuiProbeCopy.requiresExecutionPlan}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{comfyuiProbeCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={comfyuiDispatchCopy.title} description={comfyuiDispatchCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-asset-grid">
              <label>
                {comfyuiDispatchCopy.connectionProbeLabel}
                <select value={comfyuiDispatchConnectionProbeId} onChange={(event) => setComfyuiDispatchConnectionProbeId(event.target.value)}>
                  {actionableComfyuiConnectionProbes.length ? null : <option value="">{comfyuiDispatchCopy.requiresProbe}</option>}
                  {actionableComfyuiConnectionProbes.map((probe) => {
                    const connectionProbeId = valueAt(probe, ["id"], "");
                    return (
                      <option value={connectionProbeId} key={connectionProbeId}>
                        {valueAt(probe, ["title"])} / {valueAt(probe, ["probe_status"], "-")} / {valueAt(probe, ["workflow_name"], "-")}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={comfyuiDispatchTitle} onChange={(event) => setComfyuiDispatchTitle(event.target.value)} />
              </label>
              <label>
                {comfyuiDispatchCopy.modeLabel}
                <select value={comfyuiDispatchMode} onChange={(event) => setComfyuiDispatchMode(event.target.value)}>
                  <option value="metadata_only">metadata_only</option>
                  <option value="future_guarded_dispatch">future_guarded_dispatch</option>
                </select>
              </label>
              <label className="commercial-wide-label">
                {comfyuiDispatchCopy.promptPayloadLabel}
                <textarea value={comfyuiDispatchPromptPayloadDraft} onChange={(event) => setComfyuiDispatchPromptPayloadDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiDispatchCopy.workflowPayloadLabel}
                <textarea value={comfyuiDispatchWorkflowPayloadDraft} onChange={(event) => setComfyuiDispatchWorkflowPayloadDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiDispatchCopy.queuePayloadLabel}
                <textarea value={comfyuiDispatchQueuePayloadDraft} onChange={(event) => setComfyuiDispatchQueuePayloadDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiDispatchCopy.dispatchPayloadLabel}
                <textarea value={comfyuiDispatchPayloadDraft} onChange={(event) => setComfyuiDispatchPayloadDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiDispatchCopy.guardrailsLabel}
                <textarea value={comfyuiDispatchGuardrailsDraft} onChange={(event) => setComfyuiDispatchGuardrailsDraft(event.target.value)} />
              </label>
              <label>
                {comfyuiDispatchCopy.checklistLabel}
                <textarea value={comfyuiDispatchChecklistDraft} onChange={(event) => setComfyuiDispatchChecklistDraft(event.target.value)} />
              </label>
              <label>
                {comfyuiDispatchCopy.retryPolicyLabel}
                <textarea value={comfyuiDispatchRetryDraft} onChange={(event) => setComfyuiDispatchRetryDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {comfyuiDispatchCopy.recoveryPlanLabel}
                <textarea value={comfyuiDispatchRecoveryDraft} onChange={(event) => setComfyuiDispatchRecoveryDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createComfyuiAdapterDispatch()}
                disabled={!comfyuiDispatchConnectionProbeId || !comfyuiDispatchTitle.trim() || actionState.loading}
              >
                <Send size={15} />
                {comfyuiDispatchCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateComfyuiAdapterDispatch()}
                disabled={!selectedComfyuiAdapterDispatchId || !comfyuiDispatchTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {comfyuiDispatchCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={comfyuiAdapterDispatchesState} />
            {comfyuiAdapterDispatchesState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {comfyuiAdapterDispatchesState.updatedAt}</div> : null}
            {comfyuiAdapterDispatches.length ? (
              <div className="commercial-asset-list">
                {comfyuiAdapterDispatches.map((dispatch) => {
                  const adapterDispatchId = valueAt(dispatch, ["id"], "");
                  const dispatchStatus = valueAt(dispatch, ["dispatch_status"], "");
                  return (
                    <article className="commercial-asset-item" key={adapterDispatchId}>
                      <div>
                        <strong>{valueAt(dispatch, ["title"])}</strong>
                        <span>{valueAt(dispatch, ["target_url"], "-")} / {valueAt(dispatch, ["queue_name"], "-")} / {valueAt(dispatch, ["workflow_name"], "-")}</span>
                        <p>{shortJson(dispatch.guardrails, 90)}</p>
                        <p>{shortJson(dispatch.dispatch_plan_payload, 90)}</p>
                        <StatusPill value={dispatchStatus} />
                      </div>
                      <div className="commercial-asset-actions">
                        <button className="ghost-button" onClick={() => editComfyuiAdapterDispatch(dispatch)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {comfyuiDispatchCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiAdapterDispatch(adapterDispatchId, "ready")}
                          disabled={!["draft", "rejected", "failed"].includes(dispatchStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {comfyuiDispatchCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiAdapterDispatch(adapterDispatchId, "approve")}
                          disabled={dispatchStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {comfyuiDispatchCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiAdapterDispatch(adapterDispatchId, "reject")}
                          disabled={dispatchStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiDispatchCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiAdapterDispatch(adapterDispatchId, "dispatch")}
                          disabled={dispatchStatus !== "approved" || actionState.loading}
                        >
                          <PlayCircle size={15} />
                          {comfyuiDispatchCopy.dispatchAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateComfyuiAdapterDispatch(adapterDispatchId, "fail")}
                          disabled={dispatchStatus !== "approved" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiDispatchCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiAdapterDispatch(adapterDispatchId, "cancel")}
                          disabled={["cancelled", "archived", "dispatched"].includes(dispatchStatus) || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiDispatchCopy.cancelAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateComfyuiAdapterDispatch(adapterDispatchId, "archive")}
                          disabled={dispatchStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {comfyuiDispatchCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{actionableComfyuiConnectionProbes.length ? comfyuiDispatchCopy.noDispatches : comfyuiDispatchCopy.requiresProbe}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{comfyuiDispatchCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={deliverableCopy.title} description={deliverableCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-deliverable-grid">
              <label>
                {deliverableCopy.sourceDraftLabel}
                <select value={deliverableContentDraftId} onChange={(event) => setDeliverableContentDraftId(event.target.value)}>
                  {approvedContentDrafts.length ? null : <option value="">-</option>}
                  {approvedContentDrafts.map((draft) => {
                    const draftId = valueAt(draft, ["id"], "");
                    return (
                      <option value={draftId} key={draftId}>
                        {valueAt(draft, ["title"])} / {valueAt(draft, ["channel"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {deliverableCopy.typeLabel}
                <select value={deliverableType} onChange={(event) => setDeliverableType(event.target.value)}>
                  <option value="content_package">content_package</option>
                  <option value="post">post</option>
                  <option value="email">email</option>
                  <option value="landing_page">landing_page</option>
                  <option value="ad">ad</option>
                  <option value="script">script</option>
                  <option value="asset_brief">asset_brief</option>
                  <option value="report">report</option>
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={deliverableTitle} onChange={(event) => setDeliverableTitle(event.target.value)} />
              </label>
              <label>
                {deliverableCopy.linkedAssetsLabel}
                <select value={deliverableAssetRequestIdsDraft} onChange={(event) => setDeliverableAssetRequestIdsDraft(event.target.value)}>
                  <option value="">-</option>
                  {eligibleDeliverableAssets.map((assetRequest) => {
                    const assetRequestId = valueAt(assetRequest, ["id"], "");
                    return (
                      <option value={assetRequestId} key={assetRequestId}>
                        {valueAt(assetRequest, ["title"])} / {valueAt(assetRequest, ["request_status"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label className="commercial-wide-label">
                {deliverableCopy.summaryLabel}
                <textarea value={deliverableSummary} onChange={(event) => setDeliverableSummary(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {deliverableCopy.notesLabel}
                <textarea value={deliverableNotes} onChange={(event) => setDeliverableNotes(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {deliverableCopy.qualityChecksLabel}
                <textarea value={deliverableQualityChecksDraft} onChange={(event) => setDeliverableQualityChecksDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createOperationDeliverable()}
                disabled={!deliverableContentDraftId || !deliverableTitle.trim() || actionState.loading}
              >
                <Package size={15} />
                {deliverableCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateOperationDeliverable()}
                disabled={!selectedDeliverableId || !deliverableTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {deliverableCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={deliverablesState} />
            {deliverablesState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {deliverablesState.updatedAt}</div> : null}
            {deliverables.length ? (
              <div className="commercial-deliverable-list">
                {deliverables.map((deliverable) => {
                  const deliverableId = valueAt(deliverable, ["id"], "");
                  const deliverableStatus = valueAt(deliverable, ["deliverable_status"], "");
                  return (
                    <article className="commercial-deliverable-item" key={deliverableId}>
                      <div>
                        <strong>{valueAt(deliverable, ["title"])}</strong>
                        <span>{valueAt(deliverable, ["channel"])} / {valueAt(deliverable, ["deliverable_type"])}</span>
                        <p>{valueAt(deliverable, ["summary"], valueAt(deliverable, ["delivery_notes"], ""))}</p>
                        <p>{valueAt(deliverable, ["output_artifact_id"], "")}</p>
                        <StatusPill value={deliverableStatus} />
                      </div>
                      <div className="commercial-deliverable-actions">
                        <button className="ghost-button" onClick={() => editOperationDeliverable(deliverable)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {deliverableCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationDeliverable(deliverableId, "ready")}
                          disabled={!["draft", "rejected", "failed"].includes(deliverableStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {deliverableCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationDeliverable(deliverableId, "approve")}
                          disabled={deliverableStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {deliverableCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationDeliverable(deliverableId, "reject")}
                          disabled={deliverableStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {deliverableCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationDeliverable(deliverableId, "package")}
                          disabled={deliverableStatus !== "approved" || actionState.loading}
                        >
                          <Package size={15} />
                          {deliverableCopy.packageAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationDeliverable(deliverableId, "fail")}
                          disabled={deliverableStatus !== "approved" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {deliverableCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationDeliverable(deliverableId, "archive")}
                          disabled={deliverableStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {deliverableCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{deliverableCopy.noDeliverables}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{deliverableCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={evidenceCopy.title} description={evidenceCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-evidence-grid">
              <label>
                {evidenceCopy.deliverableLabel}
                <select value={evidenceDeliverableId} onChange={(event) => setEvidenceDeliverableId(event.target.value)}>
                  {packagedDeliverables.length ? null : <option value="">-</option>}
                  {packagedDeliverables.map((deliverable) => {
                    const deliverableId = valueAt(deliverable, ["id"], "");
                    return (
                      <option value={deliverableId} key={deliverableId}>
                        {valueAt(deliverable, ["title"])} / {valueAt(deliverable, ["channel"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {evidenceCopy.typeLabel}
                <select value={evidenceType} onChange={(event) => setEvidenceType(event.target.value)}>
                  <option value="rag_snapshot">rag_snapshot</option>
                  <option value="source_review">source_review</option>
                  <option value="operator_note">operator_note</option>
                  <option value="compliance_note">compliance_note</option>
                  <option value="other">other</option>
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={evidenceTitle} onChange={(event) => setEvidenceTitle(event.target.value)} />
              </label>
              <label>
                {evidenceCopy.collectionLabel}
                <input value={evidenceCollection} onChange={(event) => setEvidenceCollection(event.target.value)} />
              </label>
              <label>
                {evidenceCopy.searchModeLabel}
                <select value={evidenceSearchMode} onChange={(event) => setEvidenceSearchMode(event.target.value)}>
                  <option value="hybrid">hybrid</option>
                  <option value="keyword">keyword</option>
                  <option value="dense">dense</option>
                </select>
              </label>
              <label className="commercial-wide-label">
                {evidenceCopy.queryLabel}
                <textarea value={evidenceQuery} onChange={(event) => setEvidenceQuery(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {evidenceCopy.summaryLabel}
                <textarea value={evidenceSummary} onChange={(event) => setEvidenceSummary(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {evidenceCopy.relevanceLabel}
                <textarea value={evidenceRelevance} onChange={(event) => setEvidenceRelevance(event.target.value)} />
              </label>
              <label>
                {evidenceCopy.documentsLabel}
                <textarea value={evidenceDocumentIdsDraft} onChange={(event) => setEvidenceDocumentIdsDraft(event.target.value)} />
              </label>
              <label>
                {evidenceCopy.linksLabel}
                <textarea value={evidenceLinksDraft} onChange={(event) => setEvidenceLinksDraft(event.target.value)} />
              </label>
              <label>
                {evidenceCopy.itemsLabel}
                <textarea value={evidenceItemsDraft} onChange={(event) => setEvidenceItemsDraft(event.target.value)} />
              </label>
              <label>
                {evidenceCopy.coverageLabel}
                <textarea value={evidenceCoverageDraft} onChange={(event) => setEvidenceCoverageDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void generateOperationEvidenceSnapshot()}
                disabled={!evidenceDeliverableId || actionState.loading}
              >
                <Search size={15} />
                {evidenceCopy.generateAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void createOperationEvidenceSnapshot()}
                disabled={!evidenceDeliverableId || !evidenceTitle.trim() || actionState.loading}
              >
                <FileText size={15} />
                {evidenceCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateOperationEvidenceSnapshot()}
                disabled={!selectedEvidenceSnapshotId || !evidenceTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {evidenceCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={evidenceSnapshotsState} />
            {evidenceSnapshotsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {evidenceSnapshotsState.updatedAt}</div> : null}
            {evidenceSnapshots.length ? (
              <div className="commercial-evidence-list">
                {evidenceSnapshots.map((snapshot) => {
                  const snapshotId = valueAt(snapshot, ["id"], "");
                  const snapshotStatus = valueAt(snapshot, ["snapshot_status"], "");
                  return (
                    <article className="commercial-evidence-item" key={snapshotId}>
                      <div>
                        <strong>{valueAt(snapshot, ["title"])}</strong>
                        <span>{valueAt(snapshot, ["channel"])} / {valueAt(snapshot, ["evidence_type"])} / {valueAt(snapshot, ["knowledge_collection"], "-")}</span>
                        <p>{valueAt(snapshot, ["evidence_summary"], valueAt(snapshot, ["query"], ""))}</p>
                        <p>{shortJson(snapshot.snapshot_payload, 90)}</p>
                        <StatusPill value={snapshotStatus} />
                      </div>
                      <div className="commercial-evidence-actions">
                        <button className="ghost-button" onClick={() => editOperationEvidenceSnapshot(snapshot)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {evidenceCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationEvidenceSnapshot(snapshotId, "ready")}
                          disabled={!["draft", "rejected"].includes(snapshotStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {evidenceCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationEvidenceSnapshot(snapshotId, "approve")}
                          disabled={snapshotStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {evidenceCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationEvidenceSnapshot(snapshotId, "reject")}
                          disabled={snapshotStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {evidenceCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationEvidenceSnapshot(snapshotId, "archive")}
                          disabled={snapshotStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {evidenceCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{packagedDeliverables.length ? evidenceCopy.noSnapshots : evidenceCopy.requiresDeliverable}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{evidenceCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={executionRequestCopy.title} description={executionRequestCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-execution-grid">
              <label>
                {executionRequestCopy.deliverableLabel}
                <select value={executionDeliverableId} onChange={(event) => setExecutionDeliverableId(event.target.value)}>
                  {packagedDeliverables.length ? null : <option value="">-</option>}
                  {packagedDeliverables.map((deliverable) => {
                    const deliverableId = valueAt(deliverable, ["id"], "");
                    return (
                      <option value={deliverableId} key={deliverableId}>
                        {valueAt(deliverable, ["title"])} / {valueAt(deliverable, ["channel"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {executionRequestCopy.typeLabel}
                <select value={executionRequestType} onChange={(event) => setExecutionRequestType(event.target.value)}>
                  <option value="manual_handoff">manual_handoff</option>
                  <option value="browser_worker">browser_worker</option>
                  <option value="openclaw">openclaw</option>
                  <option value="platform_post">platform_post</option>
                  <option value="email_send">email_send</option>
                  <option value="other">other</option>
                </select>
              </label>
              <label>
                {executionRequestCopy.modeLabel}
                <select value={executionRequestMode} onChange={(event) => setExecutionRequestMode(event.target.value)}>
                  <option value="metadata_only">metadata_only</option>
                  <option value="approval_handoff">approval_handoff</option>
                  <option value="future_runtime">future_runtime</option>
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={executionRequestTitle} onChange={(event) => setExecutionRequestTitle(event.target.value)} />
              </label>
              <label>
                {executionRequestCopy.targetLabel}
                <input value={executionRequestTarget} onChange={(event) => setExecutionRequestTarget(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {executionRequestCopy.summaryLabel}
                <textarea value={executionRequestInputSummary} onChange={(event) => setExecutionRequestInputSummary(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {executionRequestCopy.runbookLabel}
                <textarea value={executionRunbookDraft} onChange={(event) => setExecutionRunbookDraft(event.target.value)} />
              </label>
              <label>
                {executionRequestCopy.readinessLabel}
                <textarea value={executionReadinessDraft} onChange={(event) => setExecutionReadinessDraft(event.target.value)} />
              </label>
              <label>
                {executionRequestCopy.outputsLabel}
                <textarea value={executionOutputsDraft} onChange={(event) => setExecutionOutputsDraft(event.target.value)} />
              </label>
              <label>
                {executionRequestCopy.evidenceLabel}
                <select
                  value={executionEvidenceSnapshotIdsDraft}
                  onChange={(event) => setExecutionEvidenceSnapshotIdsDraft(event.target.value)}
                >
                  <option value="">-</option>
                  {approvedEvidenceSnapshotIdsForExecution.length > 1 ? (
                    <option value={approvedEvidenceSnapshotIdsForExecution.join(", ")}>all approved snapshots</option>
                  ) : null}
                  {approvedEvidenceSnapshotsForExecution.map((snapshot) => {
                    const snapshotId = valueAt(snapshot, ["id"], "");
                    return (
                      <option value={snapshotId} key={snapshotId}>
                        {valueAt(snapshot, ["title"])} / {valueAt(snapshot, ["snapshot_status"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {executionRequestCopy.checklistLabel}
                <textarea value={executionChecklistDraft} onChange={(event) => setExecutionChecklistDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createOperationExecutionRequest()}
                disabled={!executionDeliverableId || !executionRequestTitle.trim() || actionState.loading}
              >
                <Send size={15} />
                {executionRequestCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateOperationExecutionRequest()}
                disabled={!selectedExecutionRequestId || !executionRequestTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {executionRequestCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={executionRequestsState} />
            {executionRequestsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {executionRequestsState.updatedAt}</div> : null}
            {executionRequests.length ? (
              <div className="commercial-execution-list">
                {executionRequests.map((executionRequest) => {
                  const executionRequestId = valueAt(executionRequest, ["id"], "");
                  const requestStatus = valueAt(executionRequest, ["request_status"], "");
                  return (
                    <article className="commercial-execution-item" key={executionRequestId}>
                      <div>
                        <strong>{valueAt(executionRequest, ["title"])}</strong>
                        <span>{valueAt(executionRequest, ["channel"])} / {valueAt(executionRequest, ["execution_type"])} / {valueAt(executionRequest, ["execution_mode"])}</span>
                        <p>{valueAt(executionRequest, ["input_summary"], valueAt(executionRequest, ["execution_target"], ""))}</p>
                        <p>{shortJson(executionRequest.handoff_payload, 90)}</p>
                        <StatusPill value={requestStatus} />
                      </div>
                      <div className="commercial-execution-actions">
                        <button className="ghost-button" onClick={() => editOperationExecutionRequest(executionRequest)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {executionRequestCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationExecutionRequest(executionRequestId, "ready")}
                          disabled={!["draft", "rejected", "failed"].includes(requestStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {executionRequestCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationExecutionRequest(executionRequestId, "approve")}
                          disabled={requestStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {executionRequestCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationExecutionRequest(executionRequestId, "reject")}
                          disabled={requestStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {executionRequestCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationExecutionRequest(executionRequestId, "prepare")}
                          disabled={requestStatus !== "approved" || actionState.loading}
                        >
                          <PlayCircle size={15} />
                          {executionRequestCopy.prepareAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationExecutionRequest(executionRequestId, "fail")}
                          disabled={requestStatus !== "approved" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {executionRequestCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationExecutionRequest(executionRequestId, "cancel")}
                          disabled={["prepared", "cancelled", "archived"].includes(requestStatus) || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {executionRequestCopy.cancelAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationExecutionRequest(executionRequestId, "archive")}
                          disabled={requestStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {executionRequestCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{executionRequestCopy.noRequests}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{executionRequestCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={executionRunCopy.title} description={executionRunCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-execution-run-grid">
              <label>
                {executionRunCopy.requestLabel}
                <select value={executionRunRequestId} onChange={(event) => setExecutionRunRequestId(event.target.value)}>
                  {preparedExecutionRequests.length ? null : <option value="">-</option>}
                  {preparedExecutionRequests.map((executionRequest) => {
                    const executionRequestId = valueAt(executionRequest, ["id"], "");
                    return (
                      <option value={executionRequestId} key={executionRequestId}>
                        {valueAt(executionRequest, ["title"])} / {valueAt(executionRequest, ["execution_target"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={executionRunTitle} onChange={(event) => setExecutionRunTitle(event.target.value)} />
              </label>
              <label>
                {executionRunCopy.targetLabel}
                <input value={executionRunTarget} onChange={(event) => setExecutionRunTarget(event.target.value)} />
              </label>
              <label>
                {executionRunCopy.maxRetriesLabel}
                <input type="number" min="0" max="10" value={executionRunMaxRetries} onChange={(event) => setExecutionRunMaxRetries(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {executionRunCopy.payloadLabel}
                <textarea value={executionRunInputPayloadDraft} onChange={(event) => setExecutionRunInputPayloadDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {executionRunCopy.notesLabel}
                <textarea value={executionRunOperatorNotes} onChange={(event) => setExecutionRunOperatorNotes(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createOperationExecutionRun()}
                disabled={!executionRunRequestId || !executionRunTitle.trim() || actionState.loading}
              >
                <PlayCircle size={15} />
                {executionRunCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateOperationExecutionRun()}
                disabled={!selectedExecutionRunId || !executionRunTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {executionRunCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={executionRunsState} />
            {executionRunsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {executionRunsState.updatedAt}</div> : null}
            {executionRuns.length ? (
              <div className="commercial-execution-run-list">
                {executionRuns.map((executionRun) => {
                  const executionRunId = valueAt(executionRun, ["id"], "");
                  const runStatus = valueAt(executionRun, ["run_status"], "");
                  const retryCount = Number(valueAt(executionRun, ["retry_count"], "0"));
                  const maxRetries = Number(valueAt(executionRun, ["max_retries"], "0"));
                  return (
                    <article className="commercial-execution-run-item" key={executionRunId}>
                      <div>
                        <strong>{valueAt(executionRun, ["title"])}</strong>
                        <span>{valueAt(executionRun, ["channel"])} / {valueAt(executionRun, ["execution_type"])} / {valueAt(executionRun, ["execution_mode"])}</span>
                        <p>{valueAt(executionRun, ["execution_target"], "-")} / retry {retryCount}/{maxRetries}</p>
                        <p>{shortJson(executionRun.runtime_payload, 90)}</p>
                        <StatusPill value={runStatus} />
                      </div>
                      <div className="commercial-execution-run-actions">
                        <button className="ghost-button" onClick={() => editOperationExecutionRun(executionRun)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {executionRunCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationExecutionRun(executionRunId, "start")}
                          disabled={!["queued", "retrying"].includes(runStatus) || actionState.loading}
                        >
                          <PlayCircle size={15} />
                          {executionRunCopy.startAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationExecutionRun(executionRunId, "succeed")}
                          disabled={runStatus !== "running" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {executionRunCopy.succeedAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationExecutionRun(executionRunId, "fail")}
                          disabled={runStatus !== "running" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {executionRunCopy.failAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationExecutionRun(executionRunId, "retry")}
                          disabled={runStatus !== "failed" || retryCount >= maxRetries || actionState.loading}
                        >
                          <RefreshCcw size={15} />
                          {executionRunCopy.retryAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationExecutionRun(executionRunId, "cancel")}
                          disabled={!["queued", "running", "retrying"].includes(runStatus) || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {executionRunCopy.cancelAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationExecutionRun(executionRunId, "archive")}
                          disabled={runStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {executionRunCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{preparedExecutionRequests.length ? executionRunCopy.noRuns : executionRunCopy.requiresRequest}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{executionRunCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={resultCopy.title} description={resultCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-result-grid">
              <label>
                {resultCopy.runLabel}
                <select value={resultRunId} onChange={(event) => setResultRunId(event.target.value)}>
                  {terminalExecutionRuns.length ? null : <option value="">-</option>}
                  {terminalExecutionRuns.map((executionRun) => {
                    const executionRunId = valueAt(executionRun, ["id"], "");
                    return (
                      <option value={executionRunId} key={executionRunId}>
                        {valueAt(executionRun, ["title"])} / {valueAt(executionRun, ["run_status"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={resultTitle} onChange={(event) => setResultTitle(event.target.value)} />
              </label>
              <label>
                {resultCopy.typeLabel}
                <input value={resultType} onChange={(event) => setResultType(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {resultCopy.summaryLabel}
                <textarea value={resultSummary} onChange={(event) => setResultSummary(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {resultCopy.outcomeLabel}
                <textarea value={resultOutcomeSummary} onChange={(event) => setResultOutcomeSummary(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {resultCopy.metricsLabel}
                <textarea value={resultMetricsDraft} onChange={(event) => setResultMetricsDraft(event.target.value)} />
              </label>
              <label>
                {resultCopy.signalsLabel}
                <textarea value={resultSignalsDraft} onChange={(event) => setResultSignalsDraft(event.target.value)} />
              </label>
              <label>
                {resultCopy.evidenceLabel}
                <textarea value={resultEvidenceDraft} onChange={(event) => setResultEvidenceDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {resultCopy.followUpsLabel}
                <textarea value={resultFollowUpsDraft} onChange={(event) => setResultFollowUpsDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createOperationResult()}
                disabled={!resultRunId || !resultTitle.trim() || actionState.loading}
              >
                <FileText size={15} />
                {resultCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateOperationResult()}
                disabled={!selectedResultId || !resultTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {resultCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={resultsState} />
            {resultsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {resultsState.updatedAt}</div> : null}
            {results.length ? (
              <div className="commercial-result-list">
                {results.map((result) => {
                  const resultId = valueAt(result, ["id"], "");
                  const resultStatus = valueAt(result, ["result_status"], "");
                  return (
                    <article className="commercial-result-item" key={resultId}>
                      <div>
                        <strong>{valueAt(result, ["title"])}</strong>
                        <span>{valueAt(result, ["channel"])} / {valueAt(result, ["result_type"])}</span>
                        <p>{valueAt(result, ["summary"], "-")}</p>
                        <p>{shortJson(result.observed_metrics, 90)}</p>
                        <StatusPill value={resultStatus} />
                      </div>
                      <div className="commercial-result-actions">
                        <button className="ghost-button" onClick={() => editOperationResult(result)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {resultCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationResult(resultId, "ready")}
                          disabled={!["draft", "rejected"].includes(resultStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {resultCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationResult(resultId, "approve")}
                          disabled={resultStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {resultCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationResult(resultId, "reject")}
                          disabled={resultStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {resultCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationResult(resultId, "archive")}
                          disabled={resultStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {resultCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{terminalExecutionRuns.length ? resultCopy.noResults : resultCopy.requiresRun}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{resultCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={monitoringCopy.title} description={monitoringCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-observation-grid">
              <label>
                {monitoringCopy.resultLabel}
                <select value={monitoringResultId} onChange={(event) => setMonitoringResultId(event.target.value)}>
                  {approvedResults.length ? null : <option value="">-</option>}
                  {approvedResults.map((result) => {
                    const resultId = valueAt(result, ["id"], "");
                    return (
                      <option value={resultId} key={resultId}>
                        {valueAt(result, ["title"])} / {valueAt(result, ["result_status"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={monitoringTitle} onChange={(event) => setMonitoringTitle(event.target.value)} />
              </label>
              <label>
                {monitoringCopy.typeLabel}
                <input value={monitoringType} onChange={(event) => setMonitoringType(event.target.value)} />
              </label>
              <label>
                {monitoringCopy.windowStartLabel}
                <input value={monitoringWindowStart} onChange={(event) => setMonitoringWindowStart(event.target.value)} placeholder="2026-05-20T09:00:00Z" />
              </label>
              <label>
                {monitoringCopy.windowEndLabel}
                <input value={monitoringWindowEnd} onChange={(event) => setMonitoringWindowEnd(event.target.value)} placeholder="2026-05-20T10:00:00Z" />
              </label>
              <label className="commercial-wide-label">
                {monitoringCopy.metricsLabel}
                <textarea value={monitoringMetricsDraft} onChange={(event) => setMonitoringMetricsDraft(event.target.value)} />
              </label>
              <label>
                {monitoringCopy.signalsLabel}
                <textarea value={monitoringSignalsDraft} onChange={(event) => setMonitoringSignalsDraft(event.target.value)} />
              </label>
              <label>
                {monitoringCopy.evidenceLabel}
                <textarea value={monitoringEvidenceDraft} onChange={(event) => setMonitoringEvidenceDraft(event.target.value)} />
              </label>
              <label>
                {monitoringCopy.anomaliesLabel}
                <textarea value={monitoringAnomaliesDraft} onChange={(event) => setMonitoringAnomaliesDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {monitoringCopy.actionsLabel}
                <textarea value={monitoringActionsDraft} onChange={(event) => setMonitoringActionsDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createMonitoringObservation()}
                disabled={!monitoringResultId || !monitoringTitle.trim() || actionState.loading}
              >
                <Activity size={15} />
                {monitoringCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateMonitoringObservation()}
                disabled={!selectedObservationId || !monitoringTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {monitoringCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={monitoringState} />
            {monitoringState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {monitoringState.updatedAt}</div> : null}
            {monitoringObservations.length ? (
              <div className="commercial-observation-list">
                {monitoringObservations.map((observation) => {
                  const observationId = valueAt(observation, ["id"], "");
                  const observationStatus = valueAt(observation, ["observation_status"], "");
                  return (
                    <article className="commercial-observation-item" key={observationId}>
                      <div>
                        <strong>{valueAt(observation, ["title"])}</strong>
                        <span>{valueAt(observation, ["channel"])} / {valueAt(observation, ["observation_type"])}</span>
                        <p>{shortJson(observation.metric_snapshots, 90)}</p>
                        <p>{shortJson(observation.anomaly_flags, 90)}</p>
                        <StatusPill value={observationStatus} />
                      </div>
                      <div className="commercial-observation-actions">
                        <button className="ghost-button" onClick={() => editMonitoringObservation(observation)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {monitoringCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateMonitoringObservation(observationId, "ready")}
                          disabled={!["draft", "rejected"].includes(observationStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {monitoringCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateMonitoringObservation(observationId, "approve")}
                          disabled={observationStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {monitoringCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateMonitoringObservation(observationId, "reject")}
                          disabled={observationStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {monitoringCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateMonitoringObservation(observationId, "archive")}
                          disabled={observationStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {monitoringCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{approvedResults.length ? monitoringCopy.noObservations : monitoringCopy.requiresResult}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{monitoringCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={optimizationCopy.title} description={optimizationCopy.description}>
        {selectedOperation ? (
          <>
            <div className="commercial-optimization-grid">
              <label>
                {optimizationCopy.observationLabel}
                <select value={optimizationObservationId} onChange={(event) => setOptimizationObservationId(event.target.value)}>
                  {approvedMonitoringObservations.length ? null : <option value="">-</option>}
                  {approvedMonitoringObservations.map((observation) => {
                    const observationId = valueAt(observation, ["id"], "");
                    return (
                      <option value={observationId} key={observationId}>
                        {valueAt(observation, ["title"])} / {valueAt(observation, ["observation_status"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={optimizationTitle} onChange={(event) => setOptimizationTitle(event.target.value)} />
              </label>
              <label>
                {optimizationCopy.typeLabel}
                <select value={optimizationType} onChange={(event) => setOptimizationType(event.target.value)}>
                  <option value="continue">continue</option>
                  <option value="iterate">iterate</option>
                  <option value="adjust_content">adjust_content</option>
                  <option value="adjust_assets">adjust_assets</option>
                  <option value="retarget_audience">retarget_audience</option>
                  <option value="retry_execution">retry_execution</option>
                  <option value="pause">pause</option>
                  <option value="escalate_review">escalate_review</option>
                  <option value="stop">stop</option>
                </select>
              </label>
              <label>
                {optimizationCopy.priorityLabel}
                <select value={optimizationPriority} onChange={(event) => setOptimizationPriority(event.target.value)}>
                  <option value="low">low</option>
                  <option value="normal">normal</option>
                  <option value="high">high</option>
                </select>
              </label>
              <label className="commercial-wide-label">
                {optimizationCopy.rationaleLabel}
                <textarea value={optimizationRationale} onChange={(event) => setOptimizationRationale(event.target.value)} />
              </label>
              <label>
                {optimizationCopy.objectiveLabel}
                <textarea value={optimizationObjectiveUpdatesDraft} onChange={(event) => setOptimizationObjectiveUpdatesDraft(event.target.value)} />
              </label>
              <label>
                {optimizationCopy.contentLabel}
                <textarea value={optimizationContentActionsDraft} onChange={(event) => setOptimizationContentActionsDraft(event.target.value)} />
              </label>
              <label>
                {optimizationCopy.assetLabel}
                <textarea value={optimizationAssetActionsDraft} onChange={(event) => setOptimizationAssetActionsDraft(event.target.value)} />
              </label>
              <label>
                {optimizationCopy.audienceLabel}
                <textarea value={optimizationAudienceActionsDraft} onChange={(event) => setOptimizationAudienceActionsDraft(event.target.value)} />
              </label>
              <label>
                {optimizationCopy.executionLabel}
                <textarea value={optimizationExecutionActionsDraft} onChange={(event) => setOptimizationExecutionActionsDraft(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {optimizationCopy.riskLabel}
                <textarea value={optimizationRiskControlsDraft} onChange={(event) => setOptimizationRiskControlsDraft(event.target.value)} />
              </label>
            </div>
            <div className="commercial-action-row">
              <button
                className="primary-button"
                onClick={() => void createOptimizationDecision()}
                disabled={!optimizationObservationId || !optimizationTitle.trim() || actionState.loading}
              >
                <Sparkles size={15} />
                {optimizationCopy.createAction}
              </button>
              <button
                className="ghost-button"
                onClick={() => void updateOptimizationDecision()}
                disabled={!selectedOptimizationDecisionId || !optimizationTitle.trim() || actionState.loading}
              >
                <ShieldCheck size={15} />
                {optimizationCopy.saveAction}
              </button>
            </div>
            <LoadNotice state={optimizationState} />
            {optimizationState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {optimizationState.updatedAt}</div> : null}
            {optimizationDecisions.length ? (
              <div className="commercial-optimization-list">
                {optimizationDecisions.map((decision) => {
                  const decisionId = valueAt(decision, ["id"], "");
                  const decisionStatus = valueAt(decision, ["decision_status"], "");
                  return (
                    <article className="commercial-optimization-item" key={decisionId}>
                      <div>
                        <strong>{valueAt(decision, ["title"])}</strong>
                        <span>{valueAt(decision, ["channel"])} / {valueAt(decision, ["decision_type"])} / {valueAt(decision, ["priority"])}</span>
                        <p>{valueAt(decision, ["rationale"], "-")}</p>
                        <p>{shortJson(decision.content_actions, 90)}</p>
                        <StatusPill value={decisionStatus} />
                      </div>
                      <div className="commercial-optimization-actions">
                        <button className="ghost-button" onClick={() => editOptimizationDecision(decision)} disabled={actionState.loading}>
                          <FileText size={15} />
                          {optimizationCopy.editAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOptimizationDecision(decisionId, "ready")}
                          disabled={!["draft", "rejected"].includes(decisionStatus) || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {optimizationCopy.readyAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOptimizationDecision(decisionId, "approve")}
                          disabled={decisionStatus !== "ready_for_review" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {optimizationCopy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOptimizationDecision(decisionId, "reject")}
                          disabled={decisionStatus !== "ready_for_review" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {optimizationCopy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOptimizationDecision(decisionId, "archive")}
                          disabled={decisionStatus === "archived" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {optimizationCopy.archiveAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{approvedMonitoringObservations.length ? optimizationCopy.noDecisions : optimizationCopy.requiresObservation}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{optimizationCopy.selectedHint}</div>
        )}
      </Panel>

      <Panel title={copy.approvalsTitle} description={copy.approvalsDescription}>
        {selectedOperation ? (
          <>
            <div className="commercial-approval-grid">
              <label>
                {copy.approvalStepLabel}
                <select
                  value={approvalStepKey}
                  onChange={(event) => {
                    const nextStepKey = event.target.value;
                    setApprovalStepKey(nextStepKey);
                    const step = planRows.find((row) => valueAt(row, ["step_key"], "") === nextStepKey);
                    if (step) {
                      setApprovalTitle(valueAt(step, ["title"], nextStepKey));
                    }
                  }}
                >
                  {planRows.map((step) => {
                    const stepKey = valueAt(step, ["step_key"], "");
                    return (
                      <option value={stepKey} key={stepKey}>
                        {stepKey} / {valueAt(step, ["title"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={approvalTitle} onChange={(event) => setApprovalTitle(event.target.value)} />
              </label>
              <label>
                {copy.riskLabel}
                <select value={approvalRiskLevel} onChange={(event) => setApprovalRiskLevel(event.target.value as "low" | "medium" | "high")}>
                  <option value="low">low</option>
                  <option value="medium">medium</option>
                  <option value="high">high</option>
                </select>
              </label>
              <label className="commercial-wide-label">
                {copy.requestedActionLabel}
                <textarea value={requestedAction} onChange={(event) => setRequestedAction(event.target.value)} />
              </label>
            </div>
            <button
              className="primary-button"
              onClick={() => void createOperationApproval()}
              disabled={!approvalStepKey.trim() || !approvalTitle.trim() || actionState.loading}
            >
              <ShieldCheck size={15} />
              {copy.requestApprovalAction}
            </button>
            <LoadNotice state={approvalsState} />
            {approvalsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {approvalsState.updatedAt}</div> : null}
            {approvals.length ? (
              <div className="commercial-approval-list">
                {approvals.map((approval) => {
                  const approvalId = valueAt(approval, ["id"], "");
                  const approvalStatus = valueAt(approval, ["approval_status"], "");
                  return (
                    <article className="commercial-approval-item" key={approvalId}>
                      <div>
                        <strong>{valueAt(approval, ["title"])}</strong>
                        <span>{valueAt(approval, ["step_key"])} / {valueAt(approval, ["risk_level"])}</span>
                        <p>{valueAt(approval, ["requested_action"])}</p>
                        <StatusPill value={approvalStatus} />
                      </div>
                      <div className="commercial-approval-actions">
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationApproval(approvalId, "approve")}
                          disabled={approvalStatus !== "pending" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {copy.approveAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationApproval(approvalId, "reject")}
                          disabled={approvalStatus !== "pending" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {copy.rejectAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationApproval(approvalId, "cancel")}
                          disabled={!["pending", "approved"].includes(approvalStatus) || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {copy.cancelAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{copy.noApprovals}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{copy.approvalsSelectedHint}</div>
        )}
      </Panel>

      <Panel title={copy.dryRunsTitle} description={copy.dryRunsDescription}>
        {selectedOperation ? (
          <>
            <div className="commercial-dry-run-grid">
              <label>
                {copy.dryRunApprovalLabel}
                <select value={dryRunApprovalId} onChange={(event) => setDryRunApprovalId(event.target.value)}>
                  {approvedApprovals.length ? null : <option value="">{copy.dryRunRequiresApproval}</option>}
                  {approvedApprovals.map((approval) => {
                    const approvalId = valueAt(approval, ["id"], "");
                    return (
                      <option value={approvalId} key={approvalId}>
                        {valueAt(approval, ["title"])} / {valueAt(approval, ["step_key"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.approvalStepLabel}
                <select value={dryRunStepKey} onChange={(event) => setDryRunStepKey(event.target.value)}>
                  {planRows.map((step) => {
                    const stepKey = valueAt(step, ["step_key"], "");
                    return (
                      <option value={stepKey} key={stepKey}>
                        {stepKey} / {valueAt(step, ["title"])}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label>
                {copy.titleLabel}
                <input value={dryRunTitle} onChange={(event) => setDryRunTitle(event.target.value)} />
              </label>
              <label>
                {copy.executionModeLabel}
                <select value={executionMode} onChange={(event) => setExecutionMode(event.target.value as "metadata_only" | "dry_run")}>
                  <option value="metadata_only">metadata_only</option>
                  <option value="dry_run">dry_run</option>
                </select>
              </label>
              <label>
                {copy.executionTargetLabel}
                <input value={executionTarget} onChange={(event) => setExecutionTarget(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {copy.inputSummaryLabel}
                <textarea value={dryRunInputSummary} onChange={(event) => setDryRunInputSummary(event.target.value)} />
              </label>
              <label>
                {copy.expectedOutputsLabel}
                <textarea value={expectedOutputsDraft} onChange={(event) => setExpectedOutputsDraft(event.target.value)} />
              </label>
              <label>
                {copy.readinessChecksLabel}
                <textarea value={readinessChecksDraft} onChange={(event) => setReadinessChecksDraft(event.target.value)} />
              </label>
            </div>
            <button
              className="primary-button"
              onClick={() => void createOperationDryRun()}
              disabled={!dryRunTitle.trim() || !dryRunStepKey.trim() || !approvedApprovals.length || actionState.loading}
            >
              <PlayCircle size={15} />
              {copy.createDryRunAction}
            </button>
            <LoadNotice state={dryRunsState} />
            {dryRunsState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {dryRunsState.updatedAt}</div> : null}
            {dryRuns.length ? (
              <div className="commercial-dry-run-list">
                {dryRuns.map((dryRun) => {
                  const dryRunId = valueAt(dryRun, ["id"], "");
                  const dryRunStatus = valueAt(dryRun, ["dry_run_status"], "");
                  return (
                    <article className="commercial-dry-run-item" key={dryRunId}>
                      <div>
                        <strong>{valueAt(dryRun, ["title"])}</strong>
                        <span>{valueAt(dryRun, ["step_key"])} / {valueAt(dryRun, ["execution_mode"])} / {valueAt(dryRun, ["execution_target"])}</span>
                        <p>{valueAt(dryRun, ["input_summary"])}</p>
                        <StatusPill value={dryRunStatus} />
                      </div>
                      <div className="commercial-dry-run-actions">
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationDryRun(dryRunId, "complete")}
                          disabled={dryRunStatus !== "created" || actionState.loading}
                        >
                          <ShieldCheck size={15} />
                          {copy.completeDryRunAction}
                        </button>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void mutateOperationDryRun(dryRunId, "fail")}
                          disabled={dryRunStatus !== "created" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {copy.failDryRunAction}
                        </button>
                        <button
                          className="ghost-button"
                          onClick={() => void mutateOperationDryRun(dryRunId, "cancel")}
                          disabled={dryRunStatus !== "created" || actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {copy.cancelAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{copy.noDryRuns}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{copy.dryRunsSelectedHint}</div>
        )}
      </Panel>

      <Panel title={copy.linksTitle} description={copy.linksDescription}>
        {selectedOperation ? (
          <>
            <div className="commercial-link-grid">
              <label>
                {copy.linkTypeLabel}
                <select value={linkType} onChange={(event) => setLinkType(event.target.value)}>
                  <option value="conversation">conversation</option>
                  <option value="artifact">artifact</option>
                  <option value="task_run">task_run</option>
                  <option value="workflow_run">workflow_run</option>
                  <option value="rag_document">rag_document</option>
                  <option value="knowledge_source">knowledge_source</option>
                  <option value="approval">approval</option>
                  <option value="external">external</option>
                </select>
              </label>
              <label>
                {copy.targetTypeLabel}
                <input value={targetType} onChange={(event) => setTargetType(event.target.value)} />
              </label>
              <label>
                {copy.targetIdLabel}
                <input value={targetId} onChange={(event) => setTargetId(event.target.value)} placeholder="thread / artifact / document id" />
              </label>
              <label>
                {copy.titleLabel}
                <input value={linkTitle} onChange={(event) => setLinkTitle(event.target.value)} />
              </label>
              <label>
                {copy.sourceNameLabel}
                <input value={linkSourceName} onChange={(event) => setLinkSourceName(event.target.value)} />
              </label>
              <label className="commercial-wide-label">
                {copy.linkSummaryLabel}
                <textarea value={linkSummary} onChange={(event) => setLinkSummary(event.target.value)} />
              </label>
            </div>
            <button
              className="primary-button"
              onClick={() => void createOperationLink()}
              disabled={!targetType.trim() || !targetId.trim() || !linkTitle.trim() || actionState.loading}
            >
              <FileText size={15} />
              {copy.createLinkAction}
            </button>
            <LoadNotice state={linksState} />
            {linksState.updatedAt ? <div className="last-updated">{textFor(language, "lastUpdated")}: {linksState.updatedAt}</div> : null}
            {links.length ? (
              <div className="commercial-link-list">
                {links.map((link) => {
                  const linkId = valueAt(link, ["id"], "");
                  return (
                    <article className="commercial-link-item" key={linkId}>
                      <div>
                        <strong>{valueAt(link, ["title"])}</strong>
                        <span>{valueAt(link, ["link_type"])} / {valueAt(link, ["target_type"])}</span>
                        <p>{valueAt(link, ["summary"])}</p>
                        <code>{valueAt(link, ["target_id"])}</code>
                      </div>
                      <div className="commercial-link-actions">
                        <span>{valueAt(link, ["source_name"])}</span>
                        <button
                          className="ghost-button danger-button"
                          onClick={() => void deleteOperationLink(linkId)}
                          disabled={actionState.loading}
                        >
                          <AlertTriangle size={15} />
                          {copy.deleteLinkAction}
                        </button>
                      </div>
                    </article>
                  );
                })}
              </div>
            ) : (
              <div className="empty-table">{copy.noLinks}</div>
            )}
          </>
        ) : (
          <div className="empty-table">{copy.linksSelectedHint}</div>
        )}
      </Panel>
    </div>
  );
}

function RagDocumentsPage({ settings, language }: { settings: AdminSettings; language: UiLanguage }) {
  const t = useCallback((key: UiTextKey) => textFor(language, key), [language]);
  const [query, setQuery] = useState("AI automation operations");
  const [collection, setCollection] = useState("ai_knowledge_base");
  const [state, setState] = useState<AsyncState<JsonRecord>>(emptyState());
  const [searchState, setSearchState] = useState<AsyncState<JsonRecord[]>>(emptyState());
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [duplicateStrategy, setDuplicateStrategy] = useState<"skip" | "force_reingest">("skip");
  const [chunkSize, setChunkSize] = useState("500");
  const [chunkOverlap, setChunkOverlap] = useState("50");
  const [sourceId, setSourceId] = useState("");
  const [sourceName, setSourceName] = useState("manual-note");
  const [sourceType, setSourceType] = useState("text");
  const [metadataDraft, setMetadataDraft] = useState("{\n  \"category\": \"manual\"\n}");
  const [knowledgeText, setKnowledgeText] = useState("AI Operations knowledge note.");
  const [actionState, setActionState] = useState<AsyncState<JsonRecord>>(emptyState());
  const [debugState, setDebugState] = useState<AsyncState<JsonRecord>>(emptyState());
  const [selectedDocument, setSelectedDocument] = useState<JsonRecord | null>(null);
  const [documentDetail, setDocumentDetail] = useState<AsyncState<JsonRecord>>(emptyState());
  const [deleteConfirmSource, setDeleteConfirmSource] = useState("");

  const load = useCallback(async () => {
    setState((current) => ({ ...current, loading: true, error: null }));
    try {
      const [embeddingHealth, documents, collections] = await Promise.all([
        ragApi.embeddingHealth(settings),
        ragApi.documents(settings),
        ragApi.collections(settings),
      ]);
      setState({ data: { embeddingHealth, documents, collections }, error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setState({
        data: null,
        error: error instanceof Error ? error.message : "RAG / Documents API unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  }, [settings]);

  const runSearch = async () => {
    setSearchState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await ragApi.search(
        {
          query,
          collection_name: collection,
          search_mode: "hybrid",
          dense_top_k: 20,
          keyword_top_k: 20,
          final_top_k: 5,
        },
        settings,
      );
      setSearchState({ data: toItems(response), error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setSearchState({
        data: null,
        error: error instanceof Error ? error.message : "RAG search unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const parseChunkOptions = () => {
    const parsedChunkSize = Number(chunkSize);
    const parsedChunkOverlap = Number(chunkOverlap);
    if (!Number.isFinite(parsedChunkSize) || parsedChunkSize < 1 || parsedChunkSize > 10000) {
      throw new Error("chunk_size must be between 1 and 10000");
    }
    if (!Number.isFinite(parsedChunkOverlap) || parsedChunkOverlap < 0 || parsedChunkOverlap > 9999) {
      throw new Error("chunk_overlap must be between 0 and 9999");
    }
    if (parsedChunkOverlap >= parsedChunkSize) {
      throw new Error("chunk_overlap must be smaller than chunk_size");
    }
    return { chunkSize: parsedChunkSize, chunkOverlap: parsedChunkOverlap };
  };

  const parseMetadata = () => {
    const trimmed = metadataDraft.trim();
    if (!trimmed) {
      return {};
    }
    const parsed = JSON.parse(trimmed) as unknown;
    if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
      throw new Error("metadata must be a JSON object");
    }
    return parsed as JsonRecord;
  };

  const runUpload = async () => {
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      if (!uploadFile) {
        throw new Error("Select a knowledge file first");
      }
      const options = parseChunkOptions();
      const response = await ragApi.uploadFile(
        {
          file: uploadFile,
          collectionName: collection.trim() || undefined,
          duplicateStrategy,
          ...options,
        },
        settings,
      );
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "RAG upload unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const runTextIngest = async (mode: "ingest" | "reingest") => {
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const options = parseChunkOptions();
      if (mode === "reingest" && !sourceId.trim()) {
        throw new Error("source_id is required for reingest");
      }
      const payload: JsonRecord = {
        text: knowledgeText,
        metadata: parseMetadata(),
        source_id: sourceId.trim() || undefined,
        source_name: sourceName.trim() || undefined,
        source_type: sourceType.trim() || "text",
        collection_name: collection.trim() || undefined,
        chunk_size: options.chunkSize,
        chunk_overlap: options.chunkOverlap,
      };
      const response = mode === "reingest" ? await ragApi.reingestText(payload, settings) : await ragApi.ingestText(payload, settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "RAG text ingest unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const loadDocumentDetail = async (document: JsonRecord) => {
    setSelectedDocument(document);
    setDeleteConfirmSource("");
    setSourceId(valueAt(document, ["source_id"], ""));
    setSourceName(valueAt(document, ["source_name"], ""));
    setSourceType(valueAt(document, ["source_type"], "text"));
    const nextCollection = valueAt(document, ["collection_name"], collection);
    if (nextCollection !== "-") {
      setCollection(nextCollection);
    }
    setDocumentDetail((current) => ({ ...current, loading: true, error: null }));
    try {
      const detail = await ragApi.documentDetail(valueAt(document, ["id"]), settings);
      setDocumentDetail({ data: detail, error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setDocumentDetail({
        data: null,
        error: error instanceof Error ? error.message : "Document detail unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const deleteSelectedSource = async () => {
    setActionState((current) => ({ ...current, loading: true, error: null }));
    try {
      const selectedSource = valueAt(selectedDocument, ["source_id"], "");
      if (!selectedSource || selectedSource === "-") {
        throw new Error("Select a document with source_id first");
      }
      if (deleteConfirmSource.trim() !== selectedSource) {
        throw new Error("source_id confirmation does not match");
      }
      const response = await ragApi.deleteBySource(selectedSource, collection.trim() || undefined, settings);
      setActionState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
      setSelectedDocument(null);
      setDocumentDetail(emptyState());
      setDeleteConfirmSource("");
      await load();
    } catch (error) {
      setActionState({
        data: null,
        error: error instanceof Error ? error.message : "Document delete unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  const runDebug = async () => {
    setDebugState((current) => ({ ...current, loading: true, error: null }));
    try {
      const response = await ragApi.debug(
        {
          query,
          collection_name: collection.trim() || undefined,
          top_k: 5,
        },
        settings,
      );
      setDebugState({ data: response, error: null, loading: false, updatedAt: nowLabel() });
    } catch (error) {
      setDebugState({
        data: null,
        error: error instanceof Error ? error.message : "RAG debug unavailable",
        loading: false,
        updatedAt: nowLabel(),
      });
    }
  };

  useEffect(() => {
    void load();
  }, [load]);

  const embeddingHealth = (state.data?.embeddingHealth as JsonRecord | null | undefined) ?? null;
  const documents = toItems(state.data?.documents);
  const collections = toItems(state.data?.collections);
  const selectedCollection = collections.find((item) => String(item.collection_name ?? "") === collection) ?? collections[0] ?? null;
  const totalChunks = documents.reduce((total, document) => {
    const count = Number(document.chunk_count ?? 0);
    return Number.isFinite(count) ? total + count : total;
  }, 0);
  const problemDocuments = documents.filter((document) => {
    const status = String(document.status ?? document.ingest_status ?? "");
    return isProblemStatus(status) || Boolean(document.error_message);
  }).length;
  const embeddingReachable = valueAt(embeddingHealth, ["reachable"], "unknown");
  const embeddingWarning = /false|error|unknown|unavailable/i.test(embeddingReachable);
  const documentChunks = documentDetail.data && Array.isArray(documentDetail.data.chunks) ? (documentDetail.data.chunks as JsonRecord[]) : [];
  const selectedSourceId = valueAt(selectedDocument, ["source_id"], "");

  return (
    <div className="page-stack">
      <section className="rag-command-center">
        <div>
          <p className="section-eyebrow">{t("ragConnection")}: {settings.aiServerUrl}</p>
          <h2>{t("ragConsoleTitle")}</h2>
          <p>{t("ragConsoleDescription")}</p>
          <p>{t("ragOperatorSummary")}</p>
        </div>
        <div className="rag-flow-grid">
          <span>{t("ragEmbeddingStep")}</span>
          <span>{t("ragCollectionStep")}</span>
          <span>{t("ragDocumentsStep")}</span>
          <span>{t("ragSearchStep")}</span>
        </div>
        <div className="rag-live-loop" aria-label={t("ragValidationLoopTitle")}>
          <strong>{t("ragValidationLoopTitle")}</strong>
          <span>{t("ragValidationUploadStep")}</span>
          <span>{t("ragValidationInspectStep")}</span>
          <span>{t("ragValidationSearchStep")}</span>
          <span>{t("ragValidationDebugStep")}</span>
          <span>{t("ragValidationCleanupStep")}</span>
        </div>
      </section>

      <div className="metrics-grid rag-metrics-grid">
        <DataCard
          title={t("ragEmbeddingMetric")}
          value={valueAt(embeddingHealth, ["provider"], "-")}
          detail={`${t("ragReachableLabel")}: ${embeddingReachable}`}
          icon={<Brain size={20} />}
          warning={embeddingWarning}
        />
        <DataCard title={t("ragCollectionsMetric")} value={String(collections.length)} detail={t("ragSelectedCollection")} icon={<Database size={20} />} />
        <DataCard title={t("ragDocumentsMetric")} value={String(documents.length)} detail={t("ragDocumentListTitle")} icon={<FileText size={20} />} />
        <DataCard title={t("ragChunksMetric")} value={String(totalChunks)} detail={t("ragProblemDocumentsMetric") + `: ${problemDocuments}`} icon={<HardDrive size={20} />} warning={problemDocuments > 0} />
      </div>

      <div className="rag-operations-grid">
        <Panel title={t("ragUploadTitle")} description={t("ragUploadDescription")}>
          <div className="rag-form-grid">
            <label>
              {t("ragFileLabel")}
              <input
                type="file"
                accept=".pdf,.docx,.txt,.md,.csv,text/plain,text/markdown,text/csv,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <label>
              {t("ragDuplicateStrategy")}
              <select value={duplicateStrategy} onChange={(event) => setDuplicateStrategy(event.target.value as "skip" | "force_reingest")}>
                <option value="skip">{t("ragDuplicateSkip")}</option>
                <option value="force_reingest">{t("ragDuplicateForce")}</option>
              </select>
            </label>
            <label>
              {t("ragChunkSize")}
              <input value={chunkSize} onChange={(event) => setChunkSize(event.target.value)} />
            </label>
            <label>
              {t("ragChunkOverlap")}
              <input value={chunkOverlap} onChange={(event) => setChunkOverlap(event.target.value)} />
            </label>
          </div>
          <button className="primary-button" onClick={() => void runUpload()} disabled={actionState.loading}>
            <FileText size={15} />
            {t("ragUploadAction")}
          </button>
        </Panel>

        <Panel title={t("ragTextIngestTitle")} description={t("ragTextIngestDescription")}>
          <div className="rag-form-grid">
            <label>
              {t("ragSourceId")}
              <input value={sourceId} onChange={(event) => setSourceId(event.target.value)} placeholder="optional for first ingest" />
            </label>
            <label>
              {t("ragSourceName")}
              <input value={sourceName} onChange={(event) => setSourceName(event.target.value)} />
            </label>
            <label>
              {t("ragSourceType")}
              <input value={sourceType} onChange={(event) => setSourceType(event.target.value)} />
            </label>
          </div>
          <label className="rag-wide-label">
            {t("ragMetadataJson")}
            <textarea value={metadataDraft} onChange={(event) => setMetadataDraft(event.target.value)} />
          </label>
          <label className="rag-wide-label">
            {t("ragKnowledgeText")}
            <textarea value={knowledgeText} onChange={(event) => setKnowledgeText(event.target.value)} />
          </label>
          <div className="conversation-actions">
            <button className="primary-button" onClick={() => void runTextIngest("ingest")} disabled={!knowledgeText.trim() || actionState.loading}>
              <FileText size={15} />
              {t("ragIngestTextAction")}
            </button>
            <button className="ghost-button" onClick={() => void runTextIngest("reingest")} disabled={!knowledgeText.trim() || !sourceId.trim() || actionState.loading}>
              <RefreshCcw size={15} />
              {t("ragReingestTextAction")}
            </button>
          </div>
        </Panel>
      </div>

      <Panel title={t("ragActionResultTitle")} description={actionState.updatedAt ? `${t("lastUpdated")}: ${actionState.updatedAt}` : undefined}>
        <LoadNotice state={actionState} />
        <JsonPreview value={actionState.data || { status: "no action yet" }} />
      </Panel>

      <Panel title={t("ragPanelTitle")} description={t("ragPanelDescription")} action={<RefreshButton onClick={load} />}>
        <LoadNotice state={state} />
        <div className="rag-status-grid">
          <Field label={t("ragProviderLabel")} value={valueAt(embeddingHealth, ["provider"], "-")} />
          <Field label={t("ragModelLabel")} value={valueAt(embeddingHealth, ["model"], "-")} />
          <Field label={t("ragReachableLabel")} value={<StatusPill value={embeddingReachable} />} />
          <Field label={t("ragDimensionLabel")} value={valueAt(embeddingHealth, ["dimension"], "-")} />
          <Field label={t("ragSelectedCollection")} value={collection} />
          <Field label={t("ragCollectionStatus")} value={<StatusPill value={valueAt(selectedCollection, ["status"], "unknown")} />} />
          <Field label={t("ragCollectionPoints")} value={valueAt(selectedCollection, ["points_count"], "0")} />
          <Field label={t("ragCollectionVectors")} value={valueAt(selectedCollection, ["vectors_count"], "0")} />
        </div>
        {state.updatedAt ? <div className="last-updated">{t("lastUpdated")}: {state.updatedAt}</div> : null}

        <h3>{t("ragDocumentListTitle")}</h3>
        <Table
          rows={documents}
          emptyLabel={t("ragNoDocuments")}
          selectedId={selectedDocument ? valueAt(selectedDocument, ["id"]) : null}
          onSelect={(row) => void loadDocumentDetail(row)}
          columns={[
            { key: "id", label: t("ragDocumentIdColumn") },
            { key: "source_id", label: t("ragSourceIdColumn") },
            { key: "source_name", label: t("ragSourceNameColumn") },
            { key: "status", label: t("ragStatusColumn") },
            { key: "ingest_status", label: t("ragIngestStatusColumn") },
            { key: "chunk_count", label: t("ragChunkCountColumn") },
            { key: "collection_name", label: t("ragCollectionColumn") },
            { key: "updated_at", label: t("ragUpdatedAtColumn") },
          ]}
        />

        <div className="rag-detail-grid">
          <section className="rag-inline-section">
            <h3>{t("ragDocumentDetailTitle")}</h3>
            <p className="foundation-note">{selectedDocument ? t("ragDocumentDetailDescription") : t("ragSelectDocumentHint")}</p>
            <LoadNotice state={documentDetail} />
            <div className="rag-detail-fields">
              <Field label={t("ragDocumentIdColumn")} value={valueAt(documentDetail.data || selectedDocument, ["id"], "-")} />
              <Field label={t("ragSourceId")} value={selectedSourceId || "-"} />
              <Field label={t("ragStatusColumn")} value={<StatusPill value={valueAt(documentDetail.data || selectedDocument, ["status"], "none")} />} />
              <Field label={t("ragIngestStatusColumn")} value={<StatusPill value={valueAt(documentDetail.data || selectedDocument, ["ingest_status"], "none")} />} />
              <Field label="version" value={valueAt(documentDetail.data || selectedDocument, ["version"], "-")} />
              <Field label="error" value={valueAt(documentDetail.data || selectedDocument, ["error_message"], "-")} />
            </div>
            <JsonPreview value={documentDetail.data?.metadata || selectedDocument?.metadata || { status: "select a document" }} />
            <h3>{t("ragChunksTitle")}</h3>
            <Table
              rows={documentChunks}
              emptyLabel={t("ragNoChunks")}
              columns={[
                { key: "id", label: t("ragChunkIdColumn") },
                { key: "chunk_index", label: "index" },
                { key: "status", label: t("ragStatusColumn") },
                { key: "text", label: t("ragTextColumn") },
              ]}
            />
          </section>
          <section className="rag-inline-section rag-danger-section">
            <h3>{t("ragDeleteDangerTitle")}</h3>
            <p className="foundation-note">{selectedSourceId ? `${t("ragSourceId")}: ${selectedSourceId}` : t("ragSelectDocumentHint")}</p>
            <label className="rag-wide-label">
              {t("ragDeleteConfirmLabel")}
              <input value={deleteConfirmSource} onChange={(event) => setDeleteConfirmSource(event.target.value)} placeholder={t("ragDeleteConfirmPlaceholder")} />
            </label>
            <button
              className="ghost-button danger-button"
              onClick={() => void deleteSelectedSource()}
              disabled={!selectedDocument || !selectedSourceId || deleteConfirmSource.trim() !== selectedSourceId || actionState.loading}
            >
              <AlertTriangle size={15} />
              {t("ragDeleteSourceAction")}
            </button>
          </section>
        </div>

        <h3>{t("ragSearchTitle")}</h3>
        <p className="foundation-note">{t("ragSearchDescription")}</p>
        <div className="rag-search-form">
          <label>
            {t("ragCollectionColumn")}
            <input value={collection} onChange={(event) => setCollection(event.target.value)} placeholder={t("ragCollectionPlaceholder")} />
          </label>
          <label>
            {t("searchQuery")}
            <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder={t("ragSearchPlaceholder")} />
          </label>
          <button className="primary-button" onClick={() => void runSearch()} disabled={!collection.trim() || !query.trim() || searchState.loading}>
            <Search size={15} />
            {t("ragSearchAction")}
          </button>
          <button className="ghost-button" onClick={() => void runDebug()} disabled={!collection.trim() || !query.trim() || debugState.loading}>
            <Search size={15} />
            {t("ragDebugAction")}
          </button>
        </div>
        <LoadNotice state={searchState} />
        {searchState.updatedAt ? <div className="last-updated">{t("lastUpdated")}: {searchState.updatedAt}</div> : null}
        <h3>{t("ragSearchResultsTitle")}</h3>
        <Table
          rows={searchState.data || []}
          emptyLabel={t("ragNoSearchResults")}
          columns={[
            { key: "id", label: t("ragChunkIdColumn") },
            { key: "similarity_score", label: t("ragSimilarityColumn") },
            { key: "rerank_score", label: t("ragRerankColumn") },
            { key: "text", label: t("ragTextColumn") },
            { key: "metadata", label: t("ragMetadataColumn") },
          ]}
        />

        <section className="rag-inline-section">
          <h3>{t("ragDebugTitle")}</h3>
          <p className="foundation-note">{t("ragDebugDescription")}</p>
          <LoadNotice state={debugState} />
          {debugState.updatedAt ? <div className="last-updated">{t("lastUpdated")}: {debugState.updatedAt}</div> : null}
          <h3>{t("ragDebugResultTitle")}</h3>
          <JsonPreview value={debugState.data || { status: t("ragNoDebugResult") }} />
        </section>

        <div className="json-grid">
          <div>
            <h3>{t("ragRawHealthTitle")}</h3>
            <JsonPreview value={embeddingHealth || { status: "unavailable" }} />
          </div>
          <div>
            <h3>{t("ragRawCollectionsTitle")}</h3>
            <JsonPreview value={state.data?.collections || { status: "unavailable" }} />
          </div>
        </div>
      </Panel>
    </div>
  );
}

function SettingsPage({
  settings,
  onSave,
}: {
  settings: AdminSettings;
  onSave: (settings: AdminSettings) => void;
}) {
  const [draft, setDraft] = useState(settings);
  const profileDocsPath = "docs/en/DEPLOYMENT_PROFILES.md";

  return (
    <Panel title="Settings" description="Local browser settings only. No authentication or permissions UI is implemented.">
      <div className="settings-grid">
        <label>
          AI Server URL
          <input value={draft.aiServerUrl} onChange={(event) => setDraft({ ...draft, aiServerUrl: event.target.value })} />
        </label>
        <label>
          Workspace ID
          <input value={draft.workspaceId} onChange={(event) => setDraft({ ...draft, workspaceId: event.target.value })} />
        </label>
        <label>
          User ID
          <input value={draft.userId} onChange={(event) => setDraft({ ...draft, userId: event.target.value })} />
        </label>
        <label>
          Refresh interval
          <input value={`${draft.refreshIntervalMs / 1000}s`} readOnly />
        </label>
      </div>
      <button
        className="primary-button"
        onClick={() => {
          writeAdminSettings(draft);
          onSave(draft);
        }}
      >
        <KeyRound size={15} />
        Save local settings
      </button>
      <section className="detail-panel">
        <h3>Deployment Profile Help</h3>
        <div className="field-grid compact">
          <Field label="recommended_profile" value="server-docker for API host; local-dev for development" />
          <Field label="ai_server_url" value={draft.aiServerUrl} />
          <Field label="workspace_id" value={draft.workspaceId} />
          <Field label="user_id" value={draft.userId} />
          <Field label="local_worker_api" value="Only required by Worker Console / Desktop Console" />
          <Field label="profile_bootstrap_docs" value={profileDocsPath} />
        </div>
        <p className="muted-copy">
          Server Docker runs API, browser-worker, PostgreSQL, Redis, and Qdrant. Client Worker runs worker_client on a customer machine. Desktop Client controls only that local machine worker runtime. Bootstrap scripts generate env files and verify dependencies, ports, and health without writing system environment variables.
        </p>
      </section>
      <section className="detail-panel">
        <h3>Release Readiness / Diagnostics</h3>
        <div className="field-grid compact">
          <Field label="current_profile" value="server-docker or local-dev" />
          <Field label="preflight_result" value="Run python scripts/release_preflight.py --profile server-docker" />
          <Field label="docs_verifier_status" value="python scripts/verify_docs_runtime.py" />
          <Field label="runtime_hygiene_status" value="python scripts/check_runtime_hygiene.py" />
          <Field label="deployment_verification_status" value="python deployment/scripts/verify_environment.py --profile server-docker" />
          <Field label="release_readiness_summary" value="docs/RELEASE_READINESS.md and docs/SMOKE_TEST_MATRIX.md" />
          <Field label="integration_preflight" value="python scripts/integration_preflight.py --profile server-docker" />
          <Field label="integration_strategy" value="docs/INTEGRATION_STRATEGY.md and docs/INTEGRATION_STATUS.md" />
        </div>
        <p className="muted-copy">
          Phase 53 provides a local Release Smoke Matrix and Preflight System. Phase 54 adds PR chain reconciliation, conflict surface detection, and API/frontend drift checks. This remains integration readiness, not CI/CD SaaS, Kubernetes, code signing, an auto updater, or a production installer.
        </p>
      </section>
    </Panel>
  );
}

function Timeline({ rows, primary, secondary }: { rows: JsonRecord[]; primary: string; secondary: string }) {
  if (!rows.length) {
    return <div className="empty-table">No records.</div>;
  }
  return (
    <div className="timeline">
      {rows.slice(0, 80).map((row) => {
        const id = rowId(row, ["id"]);
        return (
          <div key={id} className="timeline-item">
            <span>{String(row[primary] ?? "-")}</span>
            <p>{String(row[secondary] ?? "-")}</p>
            <small>{String(row.created_at ?? row.duration_ms ?? "-")}</small>
          </div>
        );
      })}
    </div>
  );
}

function RefreshButton({ onClick }: { onClick: () => void }) {
  return (
    <button className="ghost-button" onClick={() => void onClick()}>
      <RefreshCcw size={15} />
      Refresh
    </button>
  );
}

function App() {
  const [activePage, setActivePage] = useState<PageKey>(() => pageFromLocation());
  const [deepLinkTarget, setDeepLinkTarget] = useState<DeepLinkTarget>(() => targetFromLocation());
  const [settings, setSettings] = useState<AdminSettings>(() => readAdminSettings());
  const [language, setLanguage] = useState<UiLanguage>(() => readUiLanguage());
  const t = useCallback((key: UiTextKey) => textFor(language, key), [language]);
  const currentPage = useMemo(() => pages.find((page) => page.key === activePage) || pages[0], [activePage]);
  const currentPageLabel = pageLabel(currentPage.key, language);
  const navigate = useCallback((page: PageKey, target: DeepLinkTarget = {}) => {
    setActivePage(page);
    setDeepLinkTarget(target);
    updateLocation(page, target);
  }, []);
  const changeLanguage = useCallback((nextLanguage: UiLanguage) => {
    setLanguage(nextLanguage);
    writeUiLanguage(nextLanguage);
  }, []);

  useEffect(() => {
    const handlePopState = () => {
      setActivePage(pageFromLocation());
      setDeepLinkTarget(targetFromLocation());
    };
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  return (
    <div className="admin-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">
            <Brain size={22} />
          </span>
          <div>
            <strong>AI Ops Admin</strong>
            <small>{t("brandSubtitle")}</small>
          </div>
        </div>
        <nav>
          {pages.map((page) => (
            <button key={page.key} className={activePage === page.key ? "active" : ""} onClick={() => navigate(page.key)}>
              {page.icon}
              {pageLabel(page.key, language)}
            </button>
          ))}
        </nav>
        <div className="boundary-box">
          <strong>{t("boundaryTitle")}</strong>
          <span>{t("boundaryBody")}</span>
        </div>
      </aside>
      <main>
        <header className="topbar">
          <div>
            <h1>{currentPageLabel}</h1>
            <p>{settings.aiServerUrl} / workspace {settings.workspaceId} / user {settings.userId}</p>
          </div>
          <div className="topbar-actions">
            <label className="language-switch">
              <span>{t("languageLabel")}</span>
              <select value={language} onChange={(event) => changeLanguage(event.target.value as UiLanguage)} aria-label={t("languageLabel")}>
                <option value="zh-CN">中文</option>
                <option value="en-US">English</option>
              </select>
            </label>
            <StatusPill value={t("foundationMode")} />
            <StatusPill value={activePage === "run-cockpit" || activePage === "commercial-operations" ? t("operatorMode") : t("readOnlyMode")} />
          </div>
        </header>
        <div className="content">
          {activePage === "overview" ? <OverviewPage settings={settings} language={language} onNavigate={navigate} /> : null}
          {activePage === "run-cockpit" ? <RunCockpitPage settings={settings} onNavigate={navigate} language={language} /> : null}
          {activePage === "commercial-operations" ? <CommercialOperationsPage settings={settings} language={language} /> : null}
          {activePage === "workers" ? <WorkersPage settings={settings} /> : null}
          {activePage === "browser-runtime" ? <BrowserRuntimePage settings={settings} /> : null}
          {activePage === "conversations" ? <ConversationsPage settings={settings} targetThreadId={deepLinkTarget.threadId} language={language} /> : null}
          {activePage === "playbooks" ? <PlaybooksPage settings={settings} targetThreadId={deepLinkTarget.threadId} onNavigate={navigate} /> : null}
          {activePage === "output-library" ? (
            <OutputLibraryPage
              settings={settings}
              targetArtifactId={deepLinkTarget.artifactId}
              targetThreadId={deepLinkTarget.threadId}
              targetTaskRunId={deepLinkTarget.taskRunId}
              onNavigate={navigate}
            />
          ) : null}
          {activePage === "tasks" ? <TasksPage settings={settings} targetTaskRunId={deepLinkTarget.taskRunId} /> : null}
          {activePage === "workflows" ? <WorkflowsPage settings={settings} targetWorkflowRunId={deepLinkTarget.workflowRunId} /> : null}
          {activePage === "workflow-observability" ? <WorkflowObservabilityPage settings={settings} targetWorkflowRunId={deepLinkTarget.workflowRunId} language={language} /> : null}
          {activePage === "workflow-graphs" ? <WorkflowGraphsPage settings={settings} /> : null}
          {activePage === "workflow-templates" ? <WorkflowTemplatesPage settings={settings} /> : null}
          {activePage === "template-governance" ? <TemplateGovernancePage settings={settings} /> : null}
          {activePage === "openclaw" ? <OpenClawPage settings={settings} /> : null}
          {activePage === "audit-logs" ? <AuditLogsPage settings={settings} /> : null}
          {activePage === "rag-documents" ? <RagDocumentsPage settings={settings} language={language} /> : null}
          {activePage === "settings" ? <SettingsPage settings={settings} onSave={setSettings} /> : null}
        </div>
      </main>
    </div>
  );
}

const rootElement = document.getElementById("root") as HTMLElement;
const rootWindow = window as Window & { __aiOpsAdminRoot?: Root };
const root = rootWindow.__aiOpsAdminRoot ?? createRoot(rootElement);
rootWindow.__aiOpsAdminRoot = root;

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
