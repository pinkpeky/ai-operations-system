import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot, Root } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
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
  MessageSquareText,
  MonitorCheck,
  PlayCircle,
  RefreshCcw,
  Search,
  Send,
  Server,
  Settings,
  ShieldCheck,
  TerminalSquare,
  Users,
} from "lucide-react";
import {
  AdminSettings,
  auditApi,
  browserRuntimeApi,
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
    boundaryTitle: "Phase 60E",
    boundaryBody: "RAG 知识库操作简洁化。上传、写入、重写、删除和调试入口更清楚。",
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
    boundaryTitle: "Phase 60E",
    boundaryBody: "RAG operations simplification: clearer upload, ingest, reingest, delete, and debug entry points.",
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

function WorkflowObservabilityPage({ settings, targetWorkflowRunId }: { settings: AdminSettings; targetWorkflowRunId?: string }) {
  const [runs, setRuns] = useState<AsyncState<WorkflowRun[]>>(emptyState());
  const [selectedRun, setSelectedRun] = useState<WorkflowRun | null>(null);
  const [traces, setTraces] = useState<WorkflowExecutionTrace[]>([]);
  const [diagnostics, setDiagnostics] = useState<WorkflowRuntimeDiagnostic[]>([]);
  const [analytics, setAnalytics] = useState<JsonRecord | null>(null);
  const [summary, setSummary] = useState<JsonRecord | null>(null);
  const [replaySessions, setReplaySessions] = useState<WorkflowReplaySession[]>([]);
  const [actionError, setActionError] = useState<string | null>(null);

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

  return (
    <div className="split-page">
      <Panel
        title="Workflow Observability"
        description="Execution trace timeline, node inspection, retry/fallback visualization, diagnostics, runtime summary, and Replay Center. This is not OpenTelemetry and not deterministic replay."
        action={<RefreshButton onClick={load} />}
      >
        <LoadNotice state={runs} />
        {targetWorkflowRunId ? (
          <div className="summary-strip">
            <span>Replay context: Run Cockpit handoff</span>
            <span>workflow_run_id: {targetWorkflowRunId}</span>
          </div>
        ) : null}
        <Table
          rows={(runs.data || []) as unknown as JsonRecord[]}
          selectedId={selectedRun?.id ?? null}
          onSelect={(row) => setSelectedRun(row as unknown as WorkflowRun)}
          emptyLabel="No workflow runs available for Replay Center."
          columns={[
            { key: "id", label: "workflow_run_id" },
            { key: "source_type", label: "source" },
            { key: "status", label: "status" },
            { key: "current_node_key", label: "current_node" },
            { key: "planned_next_nodes", label: "next" },
            { key: "updated_at", label: "updated_at" },
          ]}
        />
      </Panel>
      <aside className="detail-panel">
        <div className="detail-title">
          <h2>Replay Center</h2>
          <button className="primary-button" onClick={() => void createReplaySession()} disabled={!selectedRun}>
            <History size={15} />
            Create replay session
          </button>
        </div>
        {actionError ? <div className="notice notice-error">{actionError}</div> : null}
        <p className="foundation-note">Replay sessions are metadata_only or dry_run. They do not re-execute browser/OpenClaw actions or bypass approvals.</p>
        <h3>Runtime Summary</h3>
        <JsonPreview value={summary || { status: "select a workflow run" }} />
        <h3>Analytics</h3>
        <div className="metrics-grid compact">
          <DataCard title="Fallbacks" value={String(analytics?.fallback_frequency ?? 0)} icon={<GitBranch size={20} />} />
          <DataCard title="Approvals" value={String(analytics?.approval_wait_frequency ?? 0)} icon={<ShieldCheck size={20} />} />
          <DataCard title="Replays" value={String(analytics?.replay_frequency ?? 0)} icon={<History size={20} />} />
        </div>
        <JsonPreview value={analytics || { status: "unavailable" }} />
        <h3>Execution Trace Timeline</h3>
        <Timeline rows={traces as unknown as JsonRecord[]} primary="event_type" secondary="node_key" />
        <h3>Node Inspection</h3>
        <JsonPreview value={(traces[0] as unknown as JsonRecord) || { status: "no traces" }} />
        <h3>Diagnostics</h3>
        <Timeline rows={diagnostics as unknown as JsonRecord[]} primary="diagnostic_type" secondary="summary" />
        <h3>Replay Sessions</h3>
        <Timeline rows={replaySessions as unknown as JsonRecord[]} primary="replay_mode" secondary="replay_status" />
      </aside>
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
            <StatusPill value={activePage === "run-cockpit" ? t("operatorMode") : t("readOnlyMode")} />
          </div>
        </header>
        <div className="content">
          {activePage === "overview" ? <OverviewPage settings={settings} language={language} onNavigate={navigate} /> : null}
          {activePage === "run-cockpit" ? <RunCockpitPage settings={settings} onNavigate={navigate} language={language} /> : null}
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
          {activePage === "workflow-observability" ? <WorkflowObservabilityPage settings={settings} targetWorkflowRunId={deepLinkTarget.workflowRunId} /> : null}
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
