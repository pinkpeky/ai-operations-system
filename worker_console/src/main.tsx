import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  FileText,
  MessageCircle,
  PauseCircle,
  PencilLine,
  PlayCircle,
  RefreshCcw,
  RotateCcw,
  Server,
  Send,
  Square,
  TerminalSquare,
  Upload,
  XCircle,
  Wifi,
  WifiOff,
} from "lucide-react";
import {
  browserRuntimeClient,
  BrowserRuntimeEvent,
  BrowserRuntimeReplay,
  BrowserRuntimeSession,
  BrowserRuntimeSnapshot,
} from "./api/browserRuntimeClient";
import {
  conversationClient,
  ConversationApproval,
  ConversationEvent,
  ConversationMessage,
  ConversationPlaybook,
  ConversationPlaybookRun,
  ConversationSettings,
} from "./api/conversationClient";
import { outputArtifactClient, OutputArtifact } from "./api/outputArtifactClient";
import { taskRunClient, TaskRun, TaskRunEvent } from "./api/taskRunClient";
import {
  workflowClient,
  AgentMemorySnapshot,
  WorkflowExecutionTrace,
  WorkflowPlannerResult,
  WorkflowReplaySession,
  WorkflowRuntimeDiagnostic,
  WorkflowRun,
  WorkflowStep,
} from "./api/workflowClient";
import { workflowTemplateClient, WorkflowTemplate, WorkflowTemplateRun } from "./api/workflowTemplateClient";
import { localWorkerClient, WorkerHealth, WorkerLogs, WorkerStatus } from "./api/localWorkerClient";
import { knowledgeBaseClient, KnowledgeDocument } from "./api/knowledgeBaseClient";
import "./styles.css";

const fallbackStatus: WorkerStatus = {
  worker_id: null,
  worker_name: null,
  workspace_id: null,
  server_url: null,
  worker_base_url: null,
  runtime_port: null,
  registered: false,
  runtime_running: false,
  heartbeat_running: false,
  current_status: "unknown",
  last_heartbeat_at: null,
  last_error: null,
  openclaw_enabled: false,
  browser_enabled: false,
};

type ControlAction =
  | "startRuntime"
  | "stopRuntime"
  | "restartRuntime"
  | "startHeartbeat"
  | "stopHeartbeat";

type ClientLanguage = "zh-CN" | "en-US";

type OperatorPage = "operations" | "knowledge";

type ClientCopy = {
  phase: string;
  appTitle: string;
  runtimeLabel: string;
  heartbeatLabel: string;
  homeTitle: string;
  homeSummary: string;
  languageLabel: string;
  connectionCard: string;
  runtimeCard: string;
  heartbeatCard: string;
  recoveryCard: string;
  connected: string;
  disconnected: string;
  running: string;
  stopped: string;
  actionStartRuntime: string;
  actionStartHeartbeat: string;
  actionRefresh: string;
  quickTitle: string;
  quickChat: string;
  quickPlaybooks: string;
  quickApprovals: string;
  quickOutputs: string;
  quickTasks: string;
  quickLogs: string;
  commandTitle: string;
  commandHint: string;
  nextStepTitle: string;
  nextStepConnect: string;
  nextStepRuntime: string;
  nextStepHeartbeat: string;
  nextStepWork: string;
  openConversation: string;
  openApprovals: string;
  advancedSummary: string;
  recoveryTitle: string;
  recoverySteps: string[];
  boundaryTitle: string;
  boundaryBody: string;
  pageOperations: string;
  pageKnowledge: string;
};

type TaskWorkbenchCopy = {
  title: string;
  subtitle: string;
  operatorModeLabel: string;
  simpleTitle: string;
  simpleSubtitle: string;
  simpleTemplateTitle: string;
  simpleProgressTitle: string;
  detailDrawerTitle: string;
  maintenanceModeTitle: string;
  simpleStart: string;
  templateTitle: string;
  selectedTemplateLabel: string;
  templatePlaybookLabel: string;
  templateModeNow: string;
  templateModeBackground: string;
  planTitle: string;
  planOutcomeLabel: string;
  planGateLabel: string;
  planStepLabel: string;
  statusTrackerTitle: string;
  statusTrackerSubtitle: string;
  statusPrepared: string;
  statusApproval: string;
  statusExecution: string;
  statusRecovery: string;
  statusOutput: string;
  statusDone: string;
  statusCurrent: string;
  statusWaiting: string;
  statusNeedsAction: string;
  statusRunLabel: string;
  statusThreadLabel: string;
  statusTaskLabel: string;
  goalPlaceholder: string;
  metricApprovals: string;
  metricActiveTasks: string;
  metricFailedTasks: string;
  metricArtifacts: string;
  nextActionTitle: string;
  nextSubmit: string;
  nextApproval: string;
  nextRecover: string;
  nextRunning: string;
  nextComplete: string;
  immediateRun: string;
  backgroundRun: string;
  refreshWork: string;
  createThread: string;
  connectionSettings: string;
  runDetails: string;
  latestAssistant: string;
  pollEvents: string;
  playbookSummary: string;
  templateSummary: string;
  approvalsSummary: string;
  messagesSummary: string;
  outputsSummary: string;
  workflowSummary: string;
  tasksSummary: string;
};

type WorkbenchRunMode = "now" | "background";

type GoalStatusStageState = "done" | "current" | "waiting" | "needs-action";

type GoalStatusStage = {
  id: string;
  label: string;
  status: GoalStatusStageState;
  detail: string;
};

type WorkbenchGoalTemplate = {
  id: string;
  title: string;
  description: string;
  prompt: string;
  playbookName: string;
  runMode: WorkbenchRunMode;
  planSteps: string[];
  reviewGate: string;
  outcome: string;
};

type KnowledgeBaseCopy = {
  title: string;
  subtitle: string;
  flowSteps: { title: string; body: string }[];
  uploadTitle: string;
  uploadHint: string;
  chooseFiles: string;
  collectionLabel: string;
  collectionPlaceholder: string;
  duplicateLabel: string;
  duplicateSkip: string;
  duplicateReplace: string;
  uploadSelected: string;
  emptyQueue: string;
  editTitle: string;
  sourceNameLabel: string;
  sourceNamePlaceholder: string;
  sourceIdLabel: string;
  sourceIdPlaceholder: string;
  contentLabel: string;
  contentPlaceholder: string;
  addText: string;
  replaceText: string;
  saveKnowledge: string;
  textRequired: string;
  sourceIdRequired: string;
  libraryTitle: string;
  refreshLibrary: string;
  emptyLibrary: string;
  editExisting: string;
  queued: string;
  uploading: string;
  uploaded: string;
  failed: string;
  loading: string;
  saved: string;
  ready: string;
  documentStatus: string;
  documentChunks: string;
  updatedAt: string;
  requestFailed: string;
  readinessTitle: string;
  connectionLabel: string;
  collectionStatusLabel: string;
  queueStatusLabel: string;
  libraryStatusLabel: string;
  fileRulesTitle: string;
  fileRulesBody: string;
  nextStepTitle: string;
  nextStepChoose: string;
  nextStepUpload: string;
  nextStepWait: string;
  nextStepRecover: string;
  nextStepReady: string;
  connectionReady: string;
  connectionIssue: string;
  collectionReady: string;
  collectionMissing: string;
  queueReady: string;
  queueNeedsUpload: string;
  libraryReady: string;
  libraryEmpty: string;
  unsupportedFile: string;
  fileTooLarge: string;
  retryFailed: string;
  clearCompleted: string;
  removeFile: string;
  activityTitle: string;
  activityEmpty: string;
  activitySelectedTitle: string;
  activityUploadTitle: string;
  activityTextSavedTitle: string;
  activityRefreshTitle: string;
  activityRemovedTitle: string;
  activityClearedTitle: string;
  activityFiles: string;
  activitySuccess: string;
  activityFailed: string;
  activityInvalid: string;
  activityCollection: string;
  clearActivity: string;
};

type KnowledgeQueueStatus = "queued" | "uploading" | "uploaded" | "failed";
type KnowledgeActivityTone = "good" | "warn" | "neutral";

type KnowledgeQueueItem = {
  id: string;
  file: File;
  status: KnowledgeQueueStatus;
  message?: string;
  retryable?: boolean;
};

type KnowledgeActivityItem = {
  id: string;
  title: string;
  detail: string;
  meta: string;
  time: string;
  tone: KnowledgeActivityTone;
};

const clientCopy: Record<ClientLanguage, ClientCopy> = {
  "zh-CN": {
    phase: "Phase 62I",
    appTitle: "工作站 Worker 控制台",
    runtimeLabel: "运行时",
    heartbeatLabel: "心跳",
    homeTitle: "工作站操作入口",
    homeSummary:
      "给客户机/工作站使用人员的简洁入口：先确认本机 Worker 连接，再处理对话、剧本、审批、任务、产物和日志。",
    languageLabel: "语言",
    connectionCard: "本机连接",
    runtimeCard: "Worker 运行",
    heartbeatCard: "心跳上报",
    recoveryCard: "异常恢复",
    connected: "已连接",
    disconnected: "未连接",
    running: "运行中",
    stopped: "未运行",
    actionStartRuntime: "启动运行时",
    actionStartHeartbeat: "启动心跳",
    actionRefresh: "刷新状态",
    quickTitle: "常用入口",
    quickChat: "对话与执行",
    quickPlaybooks: "剧本运行",
    quickApprovals: "待审批",
    quickOutputs: "产物库",
    quickTasks: "任务恢复",
    quickLogs: "本机日志",
    commandTitle: "今天要让客户机做什么？",
    commandHint: "输入运营目标、检查审批、运行剧本，或者处理失败任务。",
    nextStepTitle: "下一步",
    nextStepConnect: "先确认本机 Worker API 可以访问。",
    nextStepRuntime: "先启动本机 Worker 运行时。",
    nextStepHeartbeat: "运行时已启动，继续开启心跳上报。",
    nextStepWork: "连接正常，可以进入对话、剧本或审批。",
    openConversation: "进入对话",
    openApprovals: "查看审批",
    advancedSummary: "高级维护与诊断",
    recoveryTitle: "如果不可用",
    recoverySteps: [
      "确认本机 worker_client 已启动并监听 127.0.0.1:9100。",
      "确认 AI Server、Workspace ID、User ID 与客户机配置一致。",
      "先处理待审批和失败任务，再重新运行剧本或对话。",
    ],
    boundaryTitle: "边界说明",
    boundaryBody:
      "这个页面只控制当前客户机/工作站的本地 Worker。它不会直接调用 ComfyUI、OpenClaw、真实平台账号，也不会绕过审批。",
    pageOperations: "任务操作",
    pageKnowledge: "知识库修改与上传",
  },
  "en-US": {
    phase: "Phase 62I",
    appTitle: "Workstation Worker Console",
    runtimeLabel: "Runtime",
    heartbeatLabel: "Heartbeat",
    homeTitle: "Workstation Operator Home",
    homeSummary:
      "A simple customer-machine entrypoint: confirm the local Worker first, then handle conversations, playbooks, approvals, tasks, outputs, and logs.",
    languageLabel: "Language",
    connectionCard: "Local connection",
    runtimeCard: "Worker runtime",
    heartbeatCard: "Heartbeat",
    recoveryCard: "Recovery",
    connected: "connected",
    disconnected: "disconnected",
    running: "running",
    stopped: "stopped",
    actionStartRuntime: "Start Runtime",
    actionStartHeartbeat: "Start Heartbeat",
    actionRefresh: "Refresh status",
    quickTitle: "Shortcuts",
    quickChat: "Conversation run",
    quickPlaybooks: "Playbooks",
    quickApprovals: "Approvals",
    quickOutputs: "Output Library",
    quickTasks: "Task recovery",
    quickLogs: "Local logs",
    commandTitle: "What should this client machine do?",
    commandHint: "Enter an operating goal, review approvals, run a playbook, or recover failed work.",
    nextStepTitle: "Next step",
    nextStepConnect: "Confirm the local Worker API is reachable first.",
    nextStepRuntime: "Start the local Worker runtime first.",
    nextStepHeartbeat: "Runtime is running; start heartbeat reporting next.",
    nextStepWork: "Connection is ready. Continue with conversation, playbooks, or approvals.",
    openConversation: "Open conversation",
    openApprovals: "Review approvals",
    advancedSummary: "Advanced maintenance and diagnostics",
    recoveryTitle: "When unavailable",
    recoverySteps: [
      "Confirm worker_client is running locally on 127.0.0.1:9100.",
      "Confirm AI Server, Workspace ID, and User ID match the customer-machine config.",
      "Clear approvals and failed tasks before rerunning playbooks or conversations.",
    ],
    boundaryTitle: "Boundary",
    boundaryBody:
      "This page controls only the local Worker on the current customer machine. It does not call ComfyUI, execute OpenClaw, control real accounts, or bypass approvals.",
    pageOperations: "Task operation",
    pageKnowledge: "Knowledge upload/edit",
  },
};

const taskWorkbenchCopy: Record<ClientLanguage, TaskWorkbenchCopy> = {
  "zh-CN": {
    title: "客户机任务工作台",
    subtitle: "把运营目标、审批、后台任务和失败恢复放在同一个入口，适合普通使用人员按下一步处理。",
    operatorModeLabel: "操作模式",
    simpleTitle: "今天要完成什么？",
    simpleSubtitle: "输入目标，选择常用任务，然后开始。",
    simpleTemplateTitle: "常用任务",
    simpleProgressTitle: "当前进度",
    detailDrawerTitle: "查看计划和状态细节",
    maintenanceModeTitle: "审批、结果与维护",
    simpleStart: "开始",
    templateTitle: "目标模板",
    selectedTemplateLabel: "当前模板",
    templatePlaybookLabel: "推荐剧本",
    templateModeNow: "立即",
    templateModeBackground: "后台",
    planTitle: "计划预览",
    planOutcomeLabel: "预期产物",
    planGateLabel: "审批边界",
    planStepLabel: "步骤",
    statusTrackerTitle: "目标状态",
    statusTrackerSubtitle: "从准备、审批、执行、恢复到输出，按顺序查看当前卡点。",
    statusPrepared: "准备",
    statusApproval: "审批",
    statusExecution: "执行",
    statusRecovery: "恢复",
    statusOutput: "输出",
    statusDone: "已完成",
    statusCurrent: "进行中",
    statusWaiting: "等待",
    statusNeedsAction: "需处理",
    statusRunLabel: "运行状态",
    statusThreadLabel: "会话",
    statusTaskLabel: "任务",
    goalPlaceholder: "输入一个运营目标，例如：为新品活动生成三条短视频文案，并先进入审批。",
    metricApprovals: "待审批",
    metricActiveTasks: "运行中",
    metricFailedTasks: "需恢复",
    metricArtifacts: "产物",
    nextActionTitle: "建议动作",
    nextSubmit: "输入运营目标，然后选择立即执行或后台运行。",
    nextApproval: "先处理待审批项，再继续执行或发布。",
    nextRecover: "先恢复或重试失败任务，避免重复提交。",
    nextRunning: "已有任务在运行，查看任务状态或等待结果。",
    nextComplete: "暂无阻塞，可以提交新的运营目标。",
    immediateRun: "立即执行",
    backgroundRun: "后台运行",
    refreshWork: "刷新任务",
    createThread: "新建会话",
    connectionSettings: "连接设置",
    runDetails: "运行详情与事件",
    latestAssistant: "最新助手结果",
    pollEvents: "每 5 秒刷新事件",
    playbookSummary: "剧本运行",
    templateSummary: "模板库",
    approvalsSummary: "审批队列",
    messagesSummary: "对话与事件",
    outputsSummary: "产物库",
    workflowSummary: "工作流状态",
    tasksSummary: "后台任务与恢复",
  },
  "en-US": {
    title: "Client Task Workbench",
    subtitle: "One entrypoint for goals, approvals, background tasks, and recovery so operators can follow the next action.",
    operatorModeLabel: "Operator mode",
    simpleTitle: "What should this machine do?",
    simpleSubtitle: "Enter the goal, choose a common task, then start.",
    simpleTemplateTitle: "Common tasks",
    simpleProgressTitle: "Current progress",
    detailDrawerTitle: "Show plan and status details",
    maintenanceModeTitle: "Approvals, results, and maintenance",
    simpleStart: "Start",
    templateTitle: "Goal templates",
    selectedTemplateLabel: "Selected template",
    templatePlaybookLabel: "Recommended playbook",
    templateModeNow: "Now",
    templateModeBackground: "Background",
    planTitle: "Plan preview",
    planOutcomeLabel: "Expected output",
    planGateLabel: "Approval boundary",
    planStepLabel: "Step",
    statusTrackerTitle: "Goal status",
    statusTrackerSubtitle: "Track the goal from preparation through approval, execution, recovery, and output.",
    statusPrepared: "Prepare",
    statusApproval: "Approval",
    statusExecution: "Execution",
    statusRecovery: "Recovery",
    statusOutput: "Output",
    statusDone: "Done",
    statusCurrent: "Current",
    statusWaiting: "Waiting",
    statusNeedsAction: "Action needed",
    statusRunLabel: "Run status",
    statusThreadLabel: "Thread",
    statusTaskLabel: "Task",
    goalPlaceholder: "Tell this client machine what to do... Enter an operating goal, for example: generate three short-video drafts for a product launch and send them to approval first.",
    metricApprovals: "Approvals",
    metricActiveTasks: "Active",
    metricFailedTasks: "Recover",
    metricArtifacts: "Artifacts",
    nextActionTitle: "Suggested action",
    nextSubmit: "Enter an operating goal, then choose immediate or background execution.",
    nextApproval: "Clear pending approvals before continuing execution or publishing.",
    nextRecover: "Recover or retry failed tasks before submitting duplicates.",
    nextRunning: "A task is already running. Watch task status or wait for output.",
    nextComplete: "No blockers. Submit the next operating goal.",
    immediateRun: "Send and run",
    backgroundRun: "Run background",
    refreshWork: "Refresh messages/events",
    createThread: "Create thread",
    connectionSettings: "Connection settings",
    runDetails: "Run details and events",
    latestAssistant: "Latest assistant message",
    pollEvents: "Poll events every 5 seconds",
    playbookSummary: "Playbook run",
    templateSummary: "Template Library",
    approvalsSummary: "Approval queue",
    messagesSummary: "Conversation and events",
    outputsSummary: "Output Library",
    workflowSummary: "Workflow State",
    tasksSummary: "Background tasks and recovery",
  },
};

const knowledgeBaseCopy: Record<ClientLanguage, KnowledgeBaseCopy> = {
  "zh-CN": {
    title: "知识库修改与上传",
    subtitle: "把文档上传、文字补充、已有资料更新和入库状态放在一个可视化页面里。",
    flowSteps: [
      { title: "选择文件", body: "选择 PDF、Word、表格或文本资料。" },
      { title: "检查与修改", body: "补充来源名称、分组和替换方式。" },
      { title: "上传入库", body: "提交后自动切分并写入 RAG。" },
      { title: "验证可用", body: "刷新列表确认资料已可检索。" },
    ],
    uploadTitle: "上传知识文件",
    uploadHint: "拖放或选择要加入知识库的资料。",
    chooseFiles: "选择文件",
    collectionLabel: "知识分组",
    collectionPlaceholder: "例如：marketing 或 operations",
    duplicateLabel: "遇到重复资料",
    duplicateSkip: "保留现有版本",
    duplicateReplace: "替换并重新入库",
    uploadSelected: "上传选中文件",
    emptyQueue: "还没有选择文件。",
    editTitle: "修改或补充文字资料",
    sourceNameLabel: "资料名称",
    sourceNamePlaceholder: "例如：新品活动 FAQ",
    sourceIdLabel: "资料编号",
    sourceIdPlaceholder: "更新已有资料时填写",
    contentLabel: "资料内容",
    contentPlaceholder: "粘贴需要加入知识库的文字内容。",
    addText: "新增资料",
    replaceText: "更新已有资料",
    saveKnowledge: "保存到知识库",
    textRequired: "请先填写资料内容。",
    sourceIdRequired: "更新已有资料时需要填写资料编号。",
    libraryTitle: "当前知识资料",
    refreshLibrary: "刷新资料",
    emptyLibrary: "暂未读取到知识资料。",
    editExisting: "修改",
    queued: "等待上传",
    uploading: "上传中",
    uploaded: "已入库",
    failed: "需重试",
    loading: "读取中",
    saved: "已保存",
    ready: "可用",
    documentStatus: "状态",
    documentChunks: "分段",
    updatedAt: "更新时间",
    requestFailed: "知识库服务暂时不可用，请检查 AI Server 连接后重试。",
    readinessTitle: "上传就绪状态",
    connectionLabel: "知识库连接",
    collectionStatusLabel: "知识分组",
    queueStatusLabel: "上传队列",
    libraryStatusLabel: "资料列表",
    fileRulesTitle: "上传前检查",
    fileRulesBody: "支持 PDF、DOCX、TXT、MD、CSV；单个文件不超过 20 MB。",
    nextStepTitle: "下一步",
    nextStepChoose: "选择文件或粘贴文字资料，然后保存到知识库。",
    nextStepUpload: "已有待上传文件，确认分组后点击上传选中文件。",
    nextStepWait: "文件正在上传入库，请等待状态完成。",
    nextStepRecover: "先处理失败项：检查连接、移除不支持的文件，或重试可恢复文件。",
    nextStepReady: "资料已可用，可以回到任务操作页选择知识证据或内容生成。",
    connectionReady: "连接可用",
    connectionIssue: "需要检查连接",
    collectionReady: "已设置",
    collectionMissing: "建议填写",
    queueReady: "队列空闲",
    queueNeedsUpload: "待处理",
    libraryReady: "已读取",
    libraryEmpty: "暂无资料",
    unsupportedFile: "文件类型暂不支持。",
    fileTooLarge: "文件超过 20 MB。",
    retryFailed: "重试失败项",
    clearCompleted: "清理已完成",
    removeFile: "移除",
    activityTitle: "最近上传与修改记录",
    activityEmpty: "还没有操作记录。选择文件、上传或保存文字后会显示在这里。",
    activitySelectedTitle: "已选择文件",
    activityUploadTitle: "上传批次完成",
    activityTextSavedTitle: "文字资料已保存",
    activityRefreshTitle: "资料列表已刷新",
    activityRemovedTitle: "已移除队列文件",
    activityClearedTitle: "已清理完成项",
    activityFiles: "文件",
    activitySuccess: "成功",
    activityFailed: "失败",
    activityInvalid: "不可用",
    activityCollection: "知识分组",
    clearActivity: "清空记录",
  },
  "en-US": {
    title: "Knowledge Base Upload and Edit",
    subtitle: "Upload files, add text, update existing sources, and confirm ingestion from one visual page.",
    flowSteps: [
      { title: "Choose files", body: "Select PDFs, Word files, sheets, or text sources." },
      { title: "Review and edit", body: "Add source name, collection, and duplicate handling." },
      { title: "Upload to RAG", body: "Submit files for chunking and ingestion." },
      { title: "Confirm ready", body: "Refresh the library to verify search readiness." },
    ],
    uploadTitle: "Upload knowledge files",
    uploadHint: "Drop or choose material for the knowledge base.",
    chooseFiles: "Choose files",
    collectionLabel: "Collection",
    collectionPlaceholder: "Example: marketing or operations",
    duplicateLabel: "When duplicated",
    duplicateSkip: "Keep existing version",
    duplicateReplace: "Replace and re-ingest",
    uploadSelected: "Upload selected files",
    emptyQueue: "No files selected yet.",
    editTitle: "Edit or add text material",
    sourceNameLabel: "Source name",
    sourceNamePlaceholder: "Example: Launch FAQ",
    sourceIdLabel: "Source ID",
    sourceIdPlaceholder: "Required when updating an existing source",
    contentLabel: "Source content",
    contentPlaceholder: "Paste text that should become searchable knowledge.",
    addText: "Add material",
    replaceText: "Update existing",
    saveKnowledge: "Save to knowledge base",
    textRequired: "Add source content first.",
    sourceIdRequired: "Source ID is required when updating existing material.",
    libraryTitle: "Current knowledge material",
    refreshLibrary: "Refresh library",
    emptyLibrary: "No knowledge material loaded yet.",
    editExisting: "Edit",
    queued: "Queued",
    uploading: "Uploading",
    uploaded: "Ingested",
    failed: "Retry needed",
    loading: "Loading",
    saved: "Saved",
    ready: "Ready",
    documentStatus: "Status",
    documentChunks: "Chunks",
    updatedAt: "Updated",
    requestFailed: "Knowledge service is unavailable. Check AI Server connection and retry.",
    readinessTitle: "Upload readiness",
    connectionLabel: "Knowledge connection",
    collectionStatusLabel: "Collection",
    queueStatusLabel: "Upload queue",
    libraryStatusLabel: "Library list",
    fileRulesTitle: "Before upload",
    fileRulesBody: "Supported: PDF, DOCX, TXT, MD, CSV. Each file must be 20 MB or smaller.",
    nextStepTitle: "Next step",
    nextStepChoose: "Choose files or paste text material, then save it to the knowledge base.",
    nextStepUpload: "Files are waiting. Confirm the collection, then upload selected files.",
    nextStepWait: "Files are being uploaded and ingested. Wait for completion.",
    nextStepRecover: "Handle failed items first: check connection, remove unsupported files, or retry recoverable files.",
    nextStepReady: "Knowledge is ready. Return to Task operation and choose evidence or content generation.",
    connectionReady: "Connection ready",
    connectionIssue: "Check connection",
    collectionReady: "Set",
    collectionMissing: "Recommended",
    queueReady: "Queue idle",
    queueNeedsUpload: "Needs action",
    libraryReady: "Loaded",
    libraryEmpty: "No material",
    unsupportedFile: "Unsupported file type.",
    fileTooLarge: "File is larger than 20 MB.",
    retryFailed: "Retry failed",
    clearCompleted: "Clear completed",
    removeFile: "Remove",
    activityTitle: "Recent upload and edit activity",
    activityEmpty: "No activity yet. Choosing files, uploading, or saving text will appear here.",
    activitySelectedTitle: "Files selected",
    activityUploadTitle: "Upload batch completed",
    activityTextSavedTitle: "Text material saved",
    activityRefreshTitle: "Library refreshed",
    activityRemovedTitle: "Queue file removed",
    activityClearedTitle: "Completed items cleared",
    activityFiles: "Files",
    activitySuccess: "Succeeded",
    activityFailed: "Failed",
    activityInvalid: "Unavailable",
    activityCollection: "Collection",
    clearActivity: "Clear activity",
  },
};

const workbenchGoalTemplates: Record<ClientLanguage, WorkbenchGoalTemplate[]> = {
  "zh-CN": [
    {
      id: "launch_content",
      title: "新品内容",
      description: "生成可审批的多渠道内容草稿。",
      prompt: "请为一个新品活动生成 3 条短视频文案和 1 条图文说明，列出目标受众、卖点、审批风险、需要引用的知识库材料，以及最终应保存到产物库的内容。",
      playbookName: "content_generation",
      runMode: "now",
      planSteps: ["确认目标受众和卖点", "生成多渠道内容草稿", "列出审批风险和引用材料", "保存可审核产物"],
      reviewGate: "内容草稿必须先进入人工审批，不能直接发布。",
      outcome: "可审批内容草稿",
    },
    {
      id: "rag_evidence",
      title: "知识证据",
      description: "整理 RAG 证据和引用来源。",
      prompt: "请围绕当前运营目标检索知识库，整理可用于内容创作的证据摘要、来源文档、引用风险和缺失信息，先输出给人工审核，不要发布或执行外部动作。",
      playbookName: "content_generation",
      runMode: "now",
      planSteps: ["拆解运营问题", "检索知识库来源", "整理证据和缺失信息", "输出审核用证据摘要"],
      reviewGate: "证据摘要只供人工审核和后续创作，不触发外部动作。",
      outcome: "RAG 证据摘要",
    },
    {
      id: "asset_brief",
      title: "素材 Brief",
      description: "准备图片或视频素材请求。",
      prompt: "请把当前运营目标拆成素材需求 brief，包括画面方向、尺寸、文案、参考信息、审核标准和 ComfyUI 前置检查项；只生成可审批的素材请求，不要调用 ComfyUI。",
      playbookName: "content_generation",
      runMode: "background",
      planSteps: ["提取素材目标", "定义画面和尺寸", "补充参考与审核标准", "生成素材请求记录"],
      reviewGate: "只创建素材请求和 ComfyUI 前置检查项，不调用 ComfyUI。",
      outcome: "素材请求 Brief",
    },
    {
      id: "page_report",
      title: "页面报告",
      description: "生成页面截图和要点报告。",
      prompt: "请对 https://example.com 做浏览器截图报告，提取页面标题、关键信息、截图说明和后续内容建议；所有浏览器动作必须先经过审批。",
      playbookName: "browser_screenshot_report",
      runMode: "background",
      planSteps: ["确认目标页面", "请求浏览器审批", "采集截图和页面信息", "输出页面报告"],
      reviewGate: "浏览器动作必须保持审批受控，不能绕过人工确认。",
      outcome: "页面截图报告",
    },
  ],
  "en-US": [
    {
      id: "launch_content",
      title: "Launch content",
      description: "Draft reviewable multi-channel content.",
      prompt: "Generate 3 short-video scripts and 1 social post for a product launch. Include audience, selling points, approval risks, knowledge-base references needed, and the final outputs that should be saved to the Output Library.",
      playbookName: "content_generation",
      runMode: "now",
      planSteps: ["Confirm audience and selling points", "Draft multi-channel content", "List approval risks and references", "Save reviewable outputs"],
      reviewGate: "Drafts must go through human approval before publishing.",
      outcome: "Reviewable content drafts",
    },
    {
      id: "rag_evidence",
      title: "Knowledge evidence",
      description: "Collect RAG evidence and source notes.",
      prompt: "Search the knowledge base for the current operating goal and summarize useful evidence, source documents, citation risks, and missing information for human review. Do not publish or execute external actions.",
      playbookName: "content_generation",
      runMode: "now",
      planSteps: ["Break down the operating question", "Search knowledge sources", "Summarize evidence and gaps", "Prepare review evidence"],
      reviewGate: "Evidence is for review and later drafting only; it does not trigger external actions.",
      outcome: "RAG evidence summary",
    },
    {
      id: "asset_brief",
      title: "Asset brief",
      description: "Prepare image or video asset requests.",
      prompt: "Turn the current operating goal into an asset request brief with visual direction, dimensions, copy, reference information, review criteria, and ComfyUI preflight checks. Only create a reviewable request; do not call ComfyUI.",
      playbookName: "content_generation",
      runMode: "background",
      planSteps: ["Extract asset objective", "Define visuals and dimensions", "Add references and review criteria", "Create the asset request record"],
      reviewGate: "Only create an asset request and ComfyUI preflight notes; do not call ComfyUI.",
      outcome: "Asset request brief",
    },
    {
      id: "page_report",
      title: "Page report",
      description: "Create a page screenshot and summary report.",
      prompt: "Create a browser screenshot report for https://example.com with page title, key information, screenshot notes, and content recommendations. Browser actions must stay approval-gated.",
      playbookName: "browser_screenshot_report",
      runMode: "background",
      planSteps: ["Confirm target page", "Request browser approval", "Capture screenshot and page facts", "Produce the page report"],
      reviewGate: "Browser actions remain approval-gated and cannot bypass human confirmation.",
      outcome: "Page screenshot report",
    },
  ],
};

function StatusBadge({ label, active }: { label: string; active: boolean }) {
  return (
    <span className={`status-badge ${active ? "status-badge-active" : "status-badge-muted"}`}>
      {active ? <CheckCircle2 size={14} /> : <PauseCircle size={14} />}
      {label}
    </span>
  );
}

function Field({ label, value }: { label: string; value: React.ReactNode }) {
  return (
    <div className="field">
      <span className="field-label">{label}</span>
      <span className="field-value">{value ?? "-"}</span>
    </div>
  );
}

function ActionButton({
  icon,
  label,
  onClick,
  disabled,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  disabled: boolean;
}) {
  return (
    <button className="action-button" onClick={onClick} disabled={disabled}>
      {icon}
      <span>{label}</span>
    </button>
  );
}

function isErrorLog(line: string): boolean {
  return /error|failed|exception|traceback/i.test(line);
}

function WorkstationHome({
  status,
  health,
  error,
  localApi,
  actionLoading,
  language,
  onLanguageChange,
  onRefresh,
  onRunControl,
}: {
  status: WorkerStatus;
  health: WorkerHealth | null;
  error: string | null;
  localApi: string;
  actionLoading: ControlAction | null;
  language: ClientLanguage;
  onLanguageChange: (language: ClientLanguage) => void;
  onRefresh: () => void;
  onRunControl: (action: ControlAction) => void;
}) {
  const copy = clientCopy[language];
  const connected = Boolean(health?.success);
  const ready = connected && status.runtime_running && status.heartbeat_running;
  const recoveryState = error || status.last_error ? copy.recoveryCard : copy.connected;
  const nextStep = !connected
    ? copy.nextStepConnect
    : !status.runtime_running
      ? copy.nextStepRuntime
      : !status.heartbeat_running
        ? copy.nextStepHeartbeat
        : copy.nextStepWork;

  return (
    <section className="operator-home codex-like-client-shell" aria-labelledby="operator-home-title">
      <aside className="client-status-rail" aria-label={copy.connectionCard}>
        <div className="language-switch" aria-label={copy.languageLabel}>
          <span>{copy.languageLabel}</span>
          <button className={language === "zh-CN" ? "active" : ""} onClick={() => onLanguageChange("zh-CN")}>
            中文
          </button>
          <button className={language === "en-US" ? "active" : ""} onClick={() => onLanguageChange("en-US")}>
            English
          </button>
        </div>
        <div className="operator-status-grid">
          <div className={`operator-status-card ${connected ? "good" : "warn"}`}>
            <span>{copy.connectionCard}</span>
            <strong>{connected ? copy.connected : copy.disconnected}</strong>
            <small>{localApi}</small>
          </div>
          <div className={`operator-status-card ${status.runtime_running ? "good" : "warn"}`}>
            <span>{copy.runtimeCard}</span>
            <strong>{status.runtime_running ? copy.running : copy.stopped}</strong>
            <small>{status.current_status ?? "-"}</small>
          </div>
          <div className={`operator-status-card ${status.heartbeat_running ? "good" : "warn"}`}>
            <span>{copy.heartbeatCard}</span>
            <strong>{status.heartbeat_running ? copy.running : copy.stopped}</strong>
            <small>{status.last_heartbeat_at ?? "-"}</small>
          </div>
          <div className={`operator-status-card ${error || status.last_error ? "warn" : "good"}`}>
            <span>{copy.recoveryCard}</span>
            <strong>{recoveryState}</strong>
            <small>{error ?? status.last_error ?? "-"}</small>
          </div>
        </div>
      </aside>

      <div className="client-command-center">
        <div className="operator-home-header">
          <div>
            <p className="eyeline">{copy.phase}</p>
            <h2 id="operator-home-title">{copy.homeTitle}</h2>
            <p>{copy.homeSummary}</p>
          </div>
        </div>

        <div className={`client-next-step ${ready ? "ready" : "pending"}`}>
          <span>{copy.nextStepTitle}</span>
          <strong>{nextStep}</strong>
        </div>

        <div className="client-command-box" aria-label={copy.commandTitle}>
          <div className="client-command-copy">
            <MessageCircle size={18} />
            <div>
              <span>{copy.commandTitle}</span>
              <p>{copy.commandHint}</p>
            </div>
          </div>
          <div className="operator-actions">
            <a className="action-button primary-action" href="#chat-panel">
              <MessageCircle size={16} />
              {copy.openConversation}
            </a>
            <button className="action-button" onClick={() => onRunControl("startRuntime")} disabled={Boolean(actionLoading)}>
              <PlayCircle size={16} />
              {copy.actionStartRuntime}
            </button>
            <button className="action-button" onClick={() => onRunControl("startHeartbeat")} disabled={Boolean(actionLoading)}>
              <Wifi size={16} />
              {copy.actionStartHeartbeat}
            </button>
            <button className="refresh-button" onClick={onRefresh}>
              <RefreshCcw size={15} />
              {copy.actionRefresh}
            </button>
          </div>
        </div>

        <div className="operator-support-grid">
          <div>
            <h3>{copy.quickTitle}</h3>
            <div className="quick-link-grid">
              <a href="#chat-panel">{copy.quickChat}</a>
              <a href="#playbook-panel">{copy.quickPlaybooks}</a>
              <a href="#approvals-panel">{copy.quickApprovals}</a>
              <a href="#outputs-panel">{copy.quickOutputs}</a>
              <a href="#tasks-panel">{copy.quickTasks}</a>
              <a href="#logs-panel">{copy.quickLogs}</a>
            </div>
          </div>
          <div>
            <h3>{copy.recoveryTitle}</h3>
            <ol className="recovery-list">
              {copy.recoverySteps.map((step) => (
                <li key={step}>{step}</li>
              ))}
            </ol>
          </div>
          <div>
            <h3>{copy.boundaryTitle}</h3>
            <p>{copy.boundaryBody}</p>
          </div>
        </div>
      </div>
    </section>
  );
}

function ChatPanel({ language }: { language: ClientLanguage }) {
  const workbenchCopy = taskWorkbenchCopy[language];
  const goalTemplates = workbenchGoalTemplates[language];
  const [threadId, setThreadId] = useState<string | null>(null);
  const [title, setTitle] = useState("Worker Console conversation");
  const [input, setInput] = useState("请帮我生成一条短视频文案，并展示执行事件。");
  const [settings, setSettings] = useState<ConversationSettings>(() => {
    const stored = window.localStorage.getItem("workerConsoleConversationSettings");
    return stored ? { ...conversationClient.defaultSettings, ...JSON.parse(stored) } : conversationClient.defaultSettings;
  });
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [events, setEvents] = useState<ConversationEvent[]>([]);
  const [approvals, setApprovals] = useState<ConversationApproval[]>([]);
  const [playbooks, setPlaybooks] = useState<ConversationPlaybook[]>([]);
  const [playbookRuns, setPlaybookRuns] = useState<ConversationPlaybookRun[]>([]);
  const [artifacts, setArtifacts] = useState<OutputArtifact[]>([]);
  const [taskRuns, setTaskRuns] = useState<TaskRun[]>([]);
  const [taskEvents, setTaskEvents] = useState<TaskRunEvent[]>([]);
  const [schedulerHealth, setSchedulerHealth] = useState<Record<string, unknown> | null>(null);
  const [selectedTaskRunId, setSelectedTaskRunId] = useState<string | null>(null);
  const [workflowRuns, setWorkflowRuns] = useState<WorkflowRun[]>([]);
  const [workflowSteps, setWorkflowSteps] = useState<WorkflowStep[]>([]);
  const [memorySnapshots, setMemorySnapshots] = useState<AgentMemorySnapshot[]>([]);
  const [workflowTraces, setWorkflowTraces] = useState<WorkflowExecutionTrace[]>([]);
  const [workflowDiagnostics, setWorkflowDiagnostics] = useState<WorkflowRuntimeDiagnostic[]>([]);
  const [workflowReplaySessions, setWorkflowReplaySessions] = useState<WorkflowReplaySession[]>([]);
  const [workflowAnalytics, setWorkflowAnalytics] = useState<Record<string, unknown> | null>(null);
  const [selectedWorkflowRunId, setSelectedWorkflowRunId] = useState<string | null>(null);
  const [workflowPlanner, setWorkflowPlanner] = useState<WorkflowPlannerResult | null>(null);
  const [workflowTemplates, setWorkflowTemplates] = useState<WorkflowTemplate[]>([]);
  const [workflowTemplateRuns, setWorkflowTemplateRuns] = useState<WorkflowTemplateRun[]>([]);
  const [selectedWorkflowTemplateId, setSelectedWorkflowTemplateId] = useState<string | null>(null);
  const [selectedPlaybookName, setSelectedPlaybookName] = useState("browser_screenshot_report");
  const [chatError, setChatError] = useState<string | null>(null);
  const [chatLoading, setChatLoading] = useState(false);
  const [lastRoute, setLastRoute] = useState<string | null>(null);
  const [lastSelectedTool, setLastSelectedTool] = useState<string | null>(null);
  const [lastRunMetadata, setLastRunMetadata] = useState<Record<string, unknown> | null>(null);
  const [connectionState, setConnectionState] = useState("unknown");
  const [runStatus, setRunStatus] = useState("idle");
  const [pollEvents, setPollEvents] = useState(false);
  const [selectedGoalTemplateId, setSelectedGoalTemplateId] = useState("launch_content");

  useEffect(() => {
    window.localStorage.setItem("workerConsoleConversationSettings", JSON.stringify(settings));
  }, [settings]);

  const refreshPlaybooks = useCallback(async () => {
    try {
      const [playbookResponse, runResponse] = await Promise.all([
        conversationClient.listPlaybooks(settings),
        conversationClient.listPlaybookRuns(settings),
      ]);
      setPlaybooks(playbookResponse.items);
      setPlaybookRuns(runResponse.items);
    } catch {
      setPlaybooks([]);
      setPlaybookRuns([]);
    }
  }, [settings]);

  const refreshTaskRuns = useCallback(async () => {
    try {
      const response = await taskRunClient.listTaskRuns(settings);
      const health = await taskRunClient.schedulerHealth(settings);
      setTaskRuns(response.items);
      setSchedulerHealth(health as unknown as Record<string, unknown>);
      const taskId = selectedTaskRunId || response.items[0]?.id;
      if (taskId) {
        setSelectedTaskRunId(taskId);
        setTaskEvents((await taskRunClient.listEvents(taskId, settings)).items);
      }
    } catch {
      setTaskRuns([]);
      setTaskEvents([]);
    }
  }, [selectedTaskRunId, settings]);

  const refreshWorkflows = useCallback(async () => {
    try {
      const [response, templateResponse, templateRunResponse] = await Promise.all([
        workflowClient.listRuns(settings),
        workflowTemplateClient.listTemplates(settings),
        workflowTemplateClient.listRuns(settings),
      ]);
      setWorkflowRuns(response.items);
      setWorkflowTemplates(templateResponse.items);
      setWorkflowTemplateRuns(templateRunResponse.items);
      setSelectedWorkflowTemplateId((current) => current || templateResponse.items[0]?.id || null);
      const workflowId =
        selectedWorkflowRunId ||
        response.items.find((item) => item.status === "running" || item.status === "waiting_approval")?.id ||
        response.items[0]?.id;
      if (workflowId) {
        setSelectedWorkflowRunId(workflowId);
        const [steps, memories, planner] = await Promise.all([
          workflowClient.listSteps(workflowId, settings),
          workflowClient.listMemorySnapshots(workflowId, settings),
          workflowClient.getPlanner(workflowId, settings).catch(() => null),
        ]);
        const [traces, diagnostics, analytics] = await Promise.all([
          workflowClient.listTraces(workflowId, settings).catch(() => ({ items: [] })),
          workflowClient.listDiagnostics(workflowId, settings).catch(() => ({ items: [] })),
          workflowClient.getAnalytics(workflowId, settings).catch(() => ({ analytics: {} })),
        ]);
        setWorkflowSteps(steps.items);
        setMemorySnapshots(memories.items);
        setWorkflowPlanner(planner);
        setWorkflowTraces(traces.items);
        setWorkflowDiagnostics(diagnostics.items);
        setWorkflowAnalytics(analytics.analytics);
      }
    } catch {
      setWorkflowRuns([]);
      setWorkflowSteps([]);
      setMemorySnapshots([]);
      setWorkflowTraces([]);
      setWorkflowDiagnostics([]);
      setWorkflowReplaySessions([]);
      setWorkflowAnalytics(null);
      setWorkflowPlanner(null);
      setWorkflowTemplates([]);
      setWorkflowTemplateRuns([]);
    }
  }, [selectedWorkflowRunId, settings]);

  useEffect(() => {
    void refreshPlaybooks();
    void refreshTaskRuns();
    void refreshWorkflows();
  }, [refreshPlaybooks, refreshTaskRuns, refreshWorkflows]);

  const refreshConversation = useCallback(async () => {
    if (!threadId) {
      return;
    }
    try {
      setChatError(null);
      const [nextMessages, nextEvents, nextApprovals] = await Promise.all([
        conversationClient.listMessages(threadId, settings),
        conversationClient.listEvents(threadId, settings),
        conversationClient.listApprovals(threadId, settings),
      ]);
      setMessages(nextMessages.items);
      setEvents(nextEvents.items);
      setApprovals(nextApprovals.items);
      setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId })).items);
      await refreshPlaybooks();
      await refreshTaskRuns();
      await refreshWorkflows();
      setConnectionState("connected");
    } catch (nextError) {
      setConnectionState("disconnected");
      setChatError(nextError instanceof Error ? nextError.message : "AI Server unreachable");
    }
  }, [refreshPlaybooks, refreshTaskRuns, refreshWorkflows, settings, threadId]);

  useEffect(() => {
    if (!pollEvents || !threadId) {
      return undefined;
    }
    const timer = window.setInterval(() => {
      void refreshConversation();
    }, 5000);
    return () => window.clearInterval(timer);
  }, [pollEvents, refreshConversation, threadId]);

  const createThread = async () => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus("creating thread");
    try {
      const thread = await conversationClient.createThread(title.trim() || "Worker Console conversation", settings);
      setThreadId(thread.id);
      setMessages([]);
      setEvents([]);
      setApprovals([]);
      setLastRoute(null);
      setLastSelectedTool(null);
      setLastRunMetadata(null);
      setConnectionState("connected");
      setRunStatus("thread created");
    } catch (nextError) {
      setConnectionState("disconnected");
      setRunStatus("error");
      setChatError(nextError instanceof Error ? nextError.message : "AI Server unreachable");
    } finally {
      setChatLoading(false);
    }
  };

  const sendConversationMessage = async () => {
    const content = input.trim();
    if (!content) {
      return;
    }
    setChatLoading(true);
    setChatError(null);
    setRunStatus("running conversation");
    try {
      const thread = threadId
        ? { id: threadId }
        : await conversationClient.createThread(title.trim() || `Worker Console Chat ${new Date().toLocaleString()}`, settings);
      if (!threadId) {
        setThreadId(thread.id);
      }
      await conversationClient.sendMessage(thread.id, content, settings);
      const run = await conversationClient.runConversation(thread.id, content, settings, "review_first", selectedPlaybookName);
      setMessages((await conversationClient.listMessages(thread.id, settings)).items);
      setApprovals((await conversationClient.listApprovals(thread.id, settings)).items);
      setPlaybookRuns((await conversationClient.listPlaybookRuns(settings)).items);
      setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId: thread.id })).items);
      setEvents(run.events);
      setLastRoute(run.route_name);
      setLastSelectedTool(run.selected_tool);
      setLastRunMetadata(run.result_metadata);
      if (run.workflow_run_id) {
        setSelectedWorkflowRunId(run.workflow_run_id);
      }
      if (run.task_run_id) {
        setSelectedTaskRunId(run.task_run_id);
        await refreshTaskRuns();
      }
      await refreshWorkflows();
      setConnectionState("connected");
      setRunStatus(`route: ${run.route_name} | tool: ${run.selected_tool ?? "none"} | risk: ${run.risk_level ?? "-"} | approval: ${run.approval_status ?? "-"} | success: ${run.success}`);
      setInput("");
    } catch (nextError) {
      setConnectionState("disconnected");
      setRunStatus("error");
      setChatError(nextError instanceof Error ? nextError.message : "AI Server unreachable");
    } finally {
      setChatLoading(false);
    }
  };

  const sendBackgroundConversation = async () => {
    const content = input.trim();
    if (!content) {
      return;
    }
    setChatLoading(true);
    setChatError(null);
    setRunStatus("queueing background task");
    try {
      const thread = threadId
        ? { id: threadId }
        : await conversationClient.createThread(title.trim() || `Worker Console Background ${new Date().toLocaleString()}`, settings);
      if (!threadId) {
        setThreadId(thread.id);
      }
      const run = await conversationClient.runConversation(thread.id, content, settings, "review_first", selectedPlaybookName, "background");
      if (run.task_run_id) {
        setSelectedTaskRunId(run.task_run_id);
      }
      if (run.workflow_run_id) {
        setSelectedWorkflowRunId(run.workflow_run_id);
      }
      await refreshConversation();
      await refreshTaskRuns();
      await refreshWorkflows();
      setLastRunMetadata(run.result_metadata);
      setRunStatus(`background task queued: ${run.task_run_id ?? "-"} | status: ${run.task_status ?? "-"}`);
    } catch (nextError) {
      setConnectionState("disconnected");
      setRunStatus("error");
      setChatError(nextError instanceof Error ? nextError.message : "Background task API unreachable");
    } finally {
      setChatLoading(false);
    }
  };

  const mutateTaskRun = async (taskRunId: string, action: "retry" | "cancel" | "resume" | "recover") => {
    setChatLoading(true);
    setChatError(null);
    try {
      if (action === "retry") {
        await taskRunClient.retry(taskRunId, settings);
      } else if (action === "cancel") {
        await taskRunClient.cancel(taskRunId, settings);
      } else if (action === "recover") {
        await taskRunClient.recover(taskRunId, settings);
      } else {
        await taskRunClient.resume(taskRunId, settings);
      }
      await refreshTaskRuns();
      setRunStatus(`task ${action} submitted`);
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : `Task ${action} failed`);
      setRunStatus("task control error");
    } finally {
      setChatLoading(false);
    }
  };

  const mutateApproval = async (approvalId: string, action: "approve" | "reject" | "cancel" | "execute") => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus(`${action} approval`);
    try {
      if (action === "approve") {
        await conversationClient.approveApproval(approvalId, "Looks safe to execute.", settings);
      } else if (action === "reject") {
        await conversationClient.rejectApproval(approvalId, "Need to rewrite before execution.", settings);
      } else if (action === "cancel") {
        await conversationClient.cancelApproval(approvalId, "Cancelled before execution.", settings);
      } else {
        const run = await conversationClient.executeApproval(approvalId, settings);
        setEvents(run.events);
        setLastRunMetadata(run.result_metadata);
      }
      await refreshConversation();
      setConnectionState("connected");
      setRunStatus(`${action} approval completed`);
    } catch (nextError) {
      setConnectionState("disconnected");
      setRunStatus("error");
      setChatError(nextError instanceof Error ? nextError.message : "Approval API unreachable");
    } finally {
      setChatLoading(false);
    }
  };

  const saveMessageAsArtifact = async (messageId: string) => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus("saving artifact");
    try {
      await outputArtifactClient.createFromMessage(messageId, settings);
      if (threadId) {
        setArtifacts((await outputArtifactClient.listArtifacts(settings, { threadId })).items);
      }
      setRunStatus("artifact saved");
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Output Artifact API unreachable");
      setRunStatus("artifact error");
    } finally {
      setChatLoading(false);
    }
  };

  const exportArtifact = async (artifactId: string) => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus("exporting artifact");
    try {
      const exported = await outputArtifactClient.exportArtifact(artifactId, "markdown", settings);
      setLastRunMetadata({ artifact_export: exported });
      setRunStatus(`artifact exported: ${exported.export_path}`);
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Artifact export failed");
      setRunStatus("artifact export error");
    } finally {
      setChatLoading(false);
    }
  };

  const packageArtifact = async (artifactId: string) => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus("packaging artifact");
    try {
      const packaged = await outputArtifactClient.packageArtifact(artifactId, settings);
      setLastRunMetadata({ artifact_package: packaged });
      setRunStatus(`artifact packaged: ${packaged.output_path ?? packaged.export_path ?? "bundle created"}`);
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Artifact package failed");
      setRunStatus("artifact package error");
    } finally {
      setChatLoading(false);
    }
  };

  const showArtifactLineage = async (artifactId: string) => {
    setChatLoading(true);
    setChatError(null);
    setRunStatus("loading artifact lineage");
    try {
      const lineage = await outputArtifactClient.getLineage(artifactId, settings);
      setLastRunMetadata({ artifact_lineage: lineage });
      setRunStatus(`lineage loaded: ${lineage.relationships.length} relationships`);
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Artifact lineage failed");
      setRunStatus("artifact lineage error");
    } finally {
      setChatLoading(false);
    }
  };

  const runSelectedPlaybook = async () => {
    const playbook = playbooks.find((item) => item.name === selectedPlaybookName);
    if (!playbook) {
      setChatError("Select an available playbook before running.");
      return;
    }
    setChatLoading(true);
    setChatError(null);
    setRunStatus("running playbook");
    try {
      await conversationClient.runPlaybook(
        playbook.id,
        { message: input, url: "https://example.com", topic: input || "AI automation operations" },
        settings,
        "review_first",
        threadId,
      );
      await refreshPlaybooks();
      if (threadId) {
        await refreshConversation();
      }
      setRunStatus("Playbook run submitted");
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Playbook API unreachable");
      setRunStatus("error");
    } finally {
      setChatLoading(false);
    }
  };

  const runSelectedWorkflowTemplate = async () => {
    if (!selectedWorkflowTemplateId) {
      setChatError("Select a workflow template first");
      return;
    }
    setChatLoading(true);
    setChatError(null);
    try {
      const run = await workflowTemplateClient.runTemplate(selectedWorkflowTemplateId, settings, {
        message: input,
        url: "https://example.com",
        topic: "AI automation operations",
      });
      setLastRoute("workflow_template");
      setLastSelectedTool(null);
      setLastRunMetadata(run as unknown as Record<string, unknown>);
      await refreshWorkflows();
      setRunStatus(`template run ${run.status}`);
    } catch (nextError) {
      setChatError(nextError instanceof Error ? nextError.message : "Workflow template run failed");
      setRunStatus("error");
    } finally {
      setChatLoading(false);
    }
  };

  const assistantMessages = messages.filter((message) => message.role === "assistant");
  const latestAssistantMessage = assistantMessages[assistantMessages.length - 1];
  const selectedGoalTemplate = goalTemplates.find((template) => template.id === selectedGoalTemplateId) ?? goalTemplates[0];
  const pendingApprovals = approvals.filter((approval) => approval.approval_status === "pending");
  const activeTaskRuns = taskRuns.filter((task) => ["queued", "running", "retrying", "waiting_approval"].includes(task.status));
  const failedTaskRuns = taskRuns.filter((task) => task.recoverable || ["failed", "expired"].includes(task.status));
  const completedTaskRuns = taskRuns.filter((task) => task.status === "completed");
  const hasRuntimeProgress = Boolean(messages.length > 0 || activeTaskRuns.length > 0 || completedTaskRuns.length > 0 || failedTaskRuns.length > 0 || artifacts.length > 0);
  const hasSubmittedGoal = Boolean(
    chatLoading ||
      threadId ||
      messages.length > 0 ||
      approvals.length > 0 ||
      taskRuns.length > 0 ||
      artifacts.length > 0,
  );
  const statusStageNeedsAction = workbenchCopy.statusNeedsAction;
  const goalStatusStateLabels: Record<GoalStatusStageState, string> = {
    done: workbenchCopy.statusDone,
    current: workbenchCopy.statusCurrent,
    waiting: workbenchCopy.statusWaiting,
    "needs-action": statusStageNeedsAction,
  };
  const goalStatusStages: GoalStatusStage[] = [
    {
      id: "prepared",
      label: workbenchCopy.statusPrepared,
      status: hasSubmittedGoal ? "done" : "current",
      detail: selectedGoalTemplate.title,
    },
    {
      id: "approval",
      label: workbenchCopy.statusApproval,
      status: pendingApprovals.length > 0 ? "needs-action" : approvals.length > 0 || hasRuntimeProgress ? "done" : hasSubmittedGoal ? "current" : "waiting",
      detail: `${pendingApprovals.length}/${approvals.length} ${workbenchCopy.metricApprovals}`,
    },
    {
      id: "execution",
      label: workbenchCopy.statusExecution,
      status: activeTaskRuns.length > 0 ? "current" : completedTaskRuns.length > 0 ? "done" : "waiting",
      detail: `${activeTaskRuns.length} ${workbenchCopy.metricActiveTasks}`,
    },
    {
      id: "recovery",
      label: workbenchCopy.statusRecovery,
      status: failedTaskRuns.length > 0 ? "needs-action" : taskRuns.length > 0 ? "done" : "waiting",
      detail: `${failedTaskRuns.length} ${workbenchCopy.metricFailedTasks}`,
    },
    {
      id: "output",
      label: workbenchCopy.statusOutput,
      status: artifacts.length > 0 ? "done" : completedTaskRuns.length > 0 ? "current" : "waiting",
      detail: `${artifacts.length} ${workbenchCopy.metricArtifacts}`,
    },
  ];
  const simpleCurrentStage =
    goalStatusStages.find((stage) => stage.status === "needs-action") ??
    goalStatusStages.find((stage) => stage.status === "current") ??
    goalStatusStages.find((stage) => stage.status === "done") ??
    goalStatusStages[0];
  const suggestedAction =
    pendingApprovals.length > 0
      ? workbenchCopy.nextApproval
      : failedTaskRuns.length > 0
        ? workbenchCopy.nextRecover
        : activeTaskRuns.length > 0
          ? workbenchCopy.nextRunning
          : taskRuns.some((task) => task.status === "completed")
            ? workbenchCopy.nextComplete
            : workbenchCopy.nextSubmit;

  const applyGoalTemplate = (template: WorkbenchGoalTemplate) => {
    setSelectedGoalTemplateId(template.id);
    setInput(template.prompt);
    setSelectedPlaybookName(template.playbookName);
    setRunStatus(`template selected: ${template.id}`);
  };

  return (
    <section id="chat-panel" className="panel chat-panel">
      <div className="panel-title logs-title">
        <span>
          <MessageCircle size={18} />
          <h2>{workbenchCopy.title}</h2>
        </span>
        <div className="chat-actions">
          <button className="refresh-button" onClick={() => void createThread()} disabled={chatLoading}>
            <MessageCircle size={15} />
            {workbenchCopy.createThread}
          </button>
          <button className="refresh-button" onClick={() => void refreshConversation()} disabled={!threadId}>
            <RefreshCcw size={15} />
            {workbenchCopy.refreshWork}
          </button>
        </div>
      </div>
      <section className="client-task-workbench" aria-label={workbenchCopy.title}>
        <div className="simple-operator-workbench">
          <div className="simple-operator-header">
            <span>{workbenchCopy.operatorModeLabel}</span>
            <h3>{workbenchCopy.simpleTitle}</h3>
            <p>{workbenchCopy.simpleSubtitle}</p>
          </div>
          <div className="simple-template-row" aria-label={workbenchCopy.simpleTemplateTitle}>
            {goalTemplates.map((template) => (
              <button
                key={template.id}
                type="button"
                className={`simple-template-chip ${selectedGoalTemplate.id === template.id ? "selected" : ""}`}
                aria-pressed={selectedGoalTemplate.id === template.id}
                onClick={() => applyGoalTemplate(template)}
              >
                {template.title}
              </button>
            ))}
          </div>
        </div>
        <div className="chat-input-row command-input-row simple-goal-box">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder={workbenchCopy.goalPlaceholder}
          />
          <div className="simple-action-row">
            <button className="action-button primary-action" onClick={() => void sendConversationMessage()} disabled={chatLoading}>
              <Send size={16} />
              {workbenchCopy.simpleStart}
            </button>
            <button className="action-button" onClick={() => void sendBackgroundConversation()} disabled={chatLoading}>
              <PlayCircle size={16} />
              {workbenchCopy.backgroundRun}
            </button>
          </div>
        </div>
        <div className={`simple-progress-card ${simpleCurrentStage.status}`} aria-label={workbenchCopy.simpleProgressTitle}>
          <div className="simple-progress-header">
            <span>{workbenchCopy.simpleProgressTitle}</span>
            <strong>{simpleCurrentStage.label}: {goalStatusStateLabels[simpleCurrentStage.status]}</strong>
          </div>
          <p>{suggestedAction}</p>
          <div className="simple-progress-stages">
            {goalStatusStages.map((stage) => (
              <span key={stage.id} className={`simple-progress-stage ${stage.status}`}>
                {stage.label}
              </span>
            ))}
          </div>
        </div>
        <details className="operator-detail-drawer">
          <summary>{workbenchCopy.detailDrawerTitle}</summary>
          <div className="workbench-intro">
            <p>{workbenchCopy.subtitle}</p>
            <div className="workbench-next-action">
              <span>{workbenchCopy.nextActionTitle}</span>
              <strong>{suggestedAction}</strong>
            </div>
          </div>
          <div className="workbench-metrics" aria-label="Client task workbench status">
            <div className={pendingApprovals.length > 0 ? "needs-action" : ""}>
              <span>{workbenchCopy.metricApprovals}</span>
              <strong>{pendingApprovals.length}</strong>
            </div>
            <div className={activeTaskRuns.length > 0 ? "in-progress" : ""}>
              <span>{workbenchCopy.metricActiveTasks}</span>
              <strong>{activeTaskRuns.length}</strong>
            </div>
            <div className={failedTaskRuns.length > 0 ? "needs-action" : ""}>
              <span>{workbenchCopy.metricFailedTasks}</span>
              <strong>{failedTaskRuns.length}</strong>
            </div>
            <div>
              <span>{workbenchCopy.metricArtifacts}</span>
              <strong>{artifacts.length}</strong>
            </div>
          </div>
          <div className="workbench-template-strip" aria-label={workbenchCopy.templateTitle}>
            <div className="workbench-template-header">
              <span>{workbenchCopy.templateTitle}</span>
              <strong>{workbenchCopy.selectedTemplateLabel}: {selectedGoalTemplate.title}</strong>
            </div>
            <div className="workbench-template-grid">
              {goalTemplates.map((template) => (
                <button
                  key={template.id}
                  type="button"
                  className={`workbench-template-card ${selectedGoalTemplate.id === template.id ? "selected" : ""}`}
                  aria-pressed={selectedGoalTemplate.id === template.id}
                  onClick={() => applyGoalTemplate(template)}
                >
                  <span>{template.title}</span>
                  <p>{template.description}</p>
                  <small>
                    {workbenchCopy.templatePlaybookLabel}: {template.playbookName} | {template.runMode === "background" ? workbenchCopy.templateModeBackground : workbenchCopy.templateModeNow}
                  </small>
                </button>
              ))}
            </div>
          </div>
          <div className="workbench-plan-preview" aria-label={workbenchCopy.planTitle}>
            <div className="workbench-plan-header">
              <span>{workbenchCopy.planTitle}</span>
              <strong>{workbenchCopy.planOutcomeLabel}: {selectedGoalTemplate.outcome}</strong>
            </div>
            <ol className="workbench-plan-steps">
              {selectedGoalTemplate.planSteps.map((step, index) => (
                <li key={step}>
                  <span>{workbenchCopy.planStepLabel} {index + 1}</span>
                  <strong>{step}</strong>
                </li>
              ))}
            </ol>
            <p className="workbench-plan-gate">
              <span>{workbenchCopy.planGateLabel}</span>
              {selectedGoalTemplate.reviewGate}
            </p>
          </div>
          <div className="workbench-status-tracker" aria-label={workbenchCopy.statusTrackerTitle}>
            <div className="workbench-status-header">
              <div>
                <span>{workbenchCopy.statusTrackerTitle}</span>
                <p>{workbenchCopy.statusTrackerSubtitle}</p>
              </div>
              <strong>{workbenchCopy.statusRunLabel}: {runStatus}</strong>
            </div>
            <div className="workbench-status-stages">
              {goalStatusStages.map((stage) => (
                <div key={stage.id} className={`workbench-status-stage ${stage.status}`}>
                  <span>{stage.label}</span>
                  <strong>{goalStatusStateLabels[stage.status]}</strong>
                  <p>{stage.detail}</p>
                </div>
              ))}
            </div>
            <div className="workbench-status-meta">
              <span>{workbenchCopy.statusThreadLabel}: {threadId ?? "-"}</span>
              <span>{workbenchCopy.statusTaskLabel}: {selectedTaskRunId ?? "-"}</span>
            </div>
          </div>
        </details>
      </section>
      <details className="maintenance-drawer" open={pendingApprovals.length > 0 || failedTaskRuns.length > 0}>
        <summary>{workbenchCopy.maintenanceModeTitle}</summary>
      <details className="chat-settings-panel">
        <summary>{workbenchCopy.connectionSettings}</summary>
        <div className="chat-config-grid">
          <label>
            AI Server URL
            <input
              value={settings.aiServerUrl}
              onChange={(event) => setSettings((current) => ({ ...current, aiServerUrl: event.target.value }))}
            />
          </label>
          <label>
            Workspace ID
            <input
              value={settings.workspaceId}
              onChange={(event) => setSettings((current) => ({ ...current, workspaceId: event.target.value }))}
            />
          </label>
          <label>
            User ID
            <input
              value={settings.userId}
              onChange={(event) => setSettings((current) => ({ ...current, userId: event.target.value }))}
            />
          </label>
          <label>
            Thread title
            <input value={title} onChange={(event) => setTitle(event.target.value)} />
          </label>
        </div>
      </details>
      {connectionState === "disconnected" ? (
        <div className="inline-error">
          <AlertTriangle size={16} />
          AI Server unreachable. Check VITE_AI_SERVER_API, workspace headers, and that the API server is running.
        </div>
      ) : null}
      {chatError ? (
        <div className="inline-error">
          <AlertTriangle size={16} />
          {chatError}
        </div>
      ) : null}
      <details className="workbench-run-details">
        <summary>{workbenchCopy.runDetails}</summary>
        <div className="chat-meta">
          AI Server {connectionState} | thread: {threadId ?? "-"} | run status: {runStatus} | route: {lastRoute ?? "-"} | selected tool: {lastSelectedTool ?? "-"}
        </div>
        <div className="latest-assistant">{workbenchCopy.latestAssistant}: {latestAssistantMessage?.content ?? "-"}</div>
        <pre className="event-payload">
          {JSON.stringify(lastRunMetadata ?? { status: "run a conversation to see full bridge metadata" }, null, 2)}
        </pre>
        <label className="chat-checkbox">
          <input type="checkbox" checked={pollEvents} onChange={(event) => setPollEvents(event.target.checked)} />
          {workbenchCopy.pollEvents}
        </label>
        <div className="chat-note">
          Worker Console remains a local runtime console. This Chat Panel uses approval review_first by default, polling only, not WebSocket, not SSE, and not a full ChatGPT UI.
        </div>
      </details>
      <details id="playbook-panel" className="approval-list workbench-detail">
        <summary>{workbenchCopy.playbookSummary}</summary>
        <h3>Playbook selector</h3>
        <select value={selectedPlaybookName} onChange={(event) => setSelectedPlaybookName(event.target.value)}>
          {playbooks.map((playbook) => (
            <option key={playbook.id} value={playbook.name}>
              {playbook.name} | {playbook.risk_level}
            </option>
          ))}
        </select>
        <div className="chat-note">
          Run playbook keeps the Phase 39 approval gate. Built-ins include browser_screenshot_report and content_generation.
        </div>
        <div className="chat-actions">
          <button className="action-button" onClick={() => void runSelectedPlaybook()} disabled={chatLoading}>
            Run playbook
          </button>
          <button className="refresh-button" onClick={() => void refreshPlaybooks()}>
            Refresh playbooks
          </button>
        </div>
        <h3>Playbook runs</h3>
        {playbookRuns.length > 0 ? playbookRuns.slice(0, 4).map((run) => (
          <div key={run.id} className="approval-card">
            <div className="approval-card-header">
              <strong>{run.id}</strong>
              <span className="status-badge status-badge-muted">{run.status}</span>
            </div>
            <p>Step timeline</p>
            <pre className="event-payload">{JSON.stringify(run.output_payload?.steps ?? [], null, 2)}</pre>
          </div>
        )) : (
          <div className="empty-chat">No Playbook runs yet.</div>
        )}
      </details>
      <details id="templates-panel" className="approval-list workbench-detail">
        <summary>{workbenchCopy.templateSummary}</summary>
        <h3>Template Library</h3>
        <div className="chat-note">
          Workflow Template Registry foundation with governance status, verification badges, and compatibility summary. This is not a public marketplace, not a visual DAG builder, and not a ComfyUI integration.
        </div>
        <select value={selectedWorkflowTemplateId ?? ""} onChange={(event) => setSelectedWorkflowTemplateId(event.target.value || null)}>
          {workflowTemplates.map((template) => (
            <option key={template.id} value={template.id}>
              {template.template_key} | v{template.current_version ?? template.latest_version ?? "-"} | {template.risk_level}
            </option>
          ))}
        </select>
        <div className="chat-actions">
          <button className="action-button" onClick={() => void runSelectedWorkflowTemplate()} disabled={chatLoading || !selectedWorkflowTemplateId}>
            Run template
          </button>
          <button className="refresh-button" onClick={() => void refreshWorkflows()}>
            Refresh templates
          </button>
        </div>
        {workflowTemplates.slice(0, 4).map((template) => (
          <div key={template.id} className="approval-card">
            <div className="approval-card-header">
              <strong>{template.template_key}</strong>
              <span>{template.status}</span>
              <span>{template.category ?? "uncategorized"}</span>
              <span>{template.risk_level}</span>
              <span>{template.verified ? "verified" : "unverified"}</span>
              <span>{template.featured ? "featured" : "standard"}</span>
              <span>{template.recommended ? "recommended" : "manual-review"}</span>
            </div>
            <p>{template.description ?? "No description"}</p>
            <div className="chat-meta">
              Governance status: {template.status} | success_rate: {Math.round((template.success_rate ?? 0) * 100)}% | runs: {template.usage_count ?? 0} | compatibility: {(template.versions?.[0]?.validation_status ?? "pending")}
            </div>
          </div>
        ))}
        <h4>Template runs</h4>
        {workflowTemplateRuns.length > 0 ? workflowTemplateRuns.slice(0, 4).map((run) => (
          <div key={run.id} className="approval-card">
            <div className="approval-card-header">
              <strong>{run.id}</strong>
              <span>{run.status}</span>
              <span>workflow {run.workflow_run_id ?? "-"}</span>
            </div>
            <pre className="event-payload">{JSON.stringify(run.output_payload, null, 2)}</pre>
          </div>
        )) : (
          <div className="empty-chat">No workflow template runs yet.</div>
        )}
      </details>
      <details id="approvals-panel" className="approval-list workbench-detail" open={pendingApprovals.length > 0}>
        <summary>{workbenchCopy.approvalsSummary}</summary>
        <h3>Pending approvals panel</h3>
        {approvals.length > 0 ? approvals.map((approval) => (
          <div key={approval.id} className={`approval-card approval-risk-${approval.risk_level}`}>
            <div className="approval-card-header">
              <strong>{approval.proposed_action}</strong>
              <span className="status-badge status-badge-muted">{approval.risk_level} risk</span>
              <span className="status-badge status-badge-muted">{approval.approval_status}</span>
            </div>
            <pre className="event-payload">{JSON.stringify(approval.proposed_payload, null, 2)}</pre>
            <div className="chat-actions">
              <button className="refresh-button" onClick={() => void mutateApproval(approval.id, "approve")} disabled={approval.approval_status !== "pending"}>Approve</button>
              <button className="refresh-button" onClick={() => void mutateApproval(approval.id, "reject")} disabled={approval.approval_status !== "pending"}>Reject</button>
              <button className="refresh-button" onClick={() => void mutateApproval(approval.id, "cancel")} disabled={!["pending", "approved"].includes(approval.approval_status)}>Cancel</button>
              <button className="action-button" onClick={() => void mutateApproval(approval.id, "execute")} disabled={approval.approval_status !== "approved"}>Execute approved action</button>
            </div>
          </div>
        )) : (
          <div className="empty-chat">No pending approvals yet. Medium/high risk tools wait here before execution.</div>
        )}
      </details>
      <details className="approval-list workbench-detail">
        <summary>{workbenchCopy.messagesSummary}</summary>
      <div className="chat-grid">
        <div className="message-list">
          {messages.length > 0 ? (
            messages.map((message) => (
              <div key={message.id} className={`chat-message chat-message-${message.role}`}>
                <strong>{message.role}</strong>
                <p>{message.content}</p>
                {message.role === "assistant" ? (
                  <button className="refresh-button" onClick={() => void saveMessageAsArtifact(message.id)} disabled={chatLoading}>
                    Save as Artifact
                  </button>
                ) : null}
              </div>
            ))
          ) : (
            <div className="empty-chat">No messages yet. Create a thread, send a message, then run conversation.</div>
          )}
        </div>
        <div className="event-timeline">
          {events.length > 0 ? (
            events.slice(-12).map((event) => (
              <div key={event.id} className="event-item">
                <span>{event.event_type}</span>
                <p>{event.message ?? "-"}</p>
                <small>{event.created_at}</small>
                <pre className="event-payload">{JSON.stringify(event.payload, null, 2)}</pre>
              </div>
            ))
          ) : (
            <div className="empty-chat">No events yet.</div>
          )}
        </div>
      </div>
      </details>
      <details id="outputs-panel" className="approval-list workbench-detail">
        <summary>{workbenchCopy.outputsSummary}</summary>
        <h3>Output Library</h3>
        <div className="chat-note">Generated artifacts from Playbook runs and saved assistant messages. This is not a full DAM.</div>
        {artifacts.length > 0 ? artifacts.slice(0, 5).map((artifact) => (
          <div key={artifact.id} className="approval-card">
            <div className="approval-card-header">
              <strong>{artifact.title}</strong>
              <span>{artifact.artifact_type}</span>
              <span>{artifact.artifact_role ?? "no_role"}</span>
              <span>{artifact.artifact_stage}</span>
              <span>{artifact.retention_policy}</span>
              <span>{artifact.source_type}</span>
            </div>
            <div className="chat-meta">
              artifact_id: {artifact.id} | root: {artifact.root_artifact_id ?? "-"} | playbook_run_id: {artifact.playbook_run_id ?? "-"} | task_run_id: {artifact.task_run_id ?? "-"} | workflow_run_id: {artifact.workflow_run_id ?? "-"} | producing_node_key: {artifact.producing_node_key ?? "-"} | replay_source: {artifact.replay_source ?? "-"}
            </div>
            <p>{artifact.summary ?? artifact.file_path ?? "No summary"}</p>
            <div className="chat-actions">
              <button className="refresh-button" onClick={() => void exportArtifact(artifact.id)} disabled={chatLoading}>
                Export markdown
              </button>
              <button className="refresh-button" onClick={() => void packageArtifact(artifact.id)} disabled={chatLoading}>
                Package
              </button>
              <button className="refresh-button" onClick={() => void showArtifactLineage(artifact.id)} disabled={chatLoading}>
                Lineage
              </button>
            </div>
          </div>
        )) : (
          <div className="empty-chat">No generated artifacts yet.</div>
        )}
      </details>
      <details id="workflow-panel" className="approval-list workbench-detail">
        <summary>{workbenchCopy.workflowSummary}</summary>
        <h3>Workflow State</h3>
        <div className="chat-note">
          Workflow State tracks current step, checkpoints, and Agent Memory Snapshots for Conversation / Playbook / Task execution. Foundation only; not a full workflow editor and not ComfyUI.
        </div>
        <div className="chat-actions">
          <button className="refresh-button" onClick={() => void refreshWorkflows()}>
            <RefreshCcw size={15} />
            Refresh workflows
          </button>
        </div>
        {workflowRuns.length > 0 ? workflowRuns.slice(0, 5).map((workflow) => (
          <div key={workflow.id} className="approval-card">
            <div className="approval-card-header">
              <strong>{workflow.source_type}</strong>
              <span>{workflow.status}</span>
              <span>step {workflow.current_step}</span>
              <span>node {workflow.current_node_key ?? "-"}</span>
            </div>
            <div className="chat-meta">
              workflow_run_id: {workflow.id} | graph_execution: {String(workflow.graph_execution)} | workflow_graph_id: {workflow.workflow_graph_id ?? "-"} | next: {(workflow.planned_next_nodes ?? []).join(",") || "-"} | checkpoints: {workflow.checkpoints.length}
            </div>
            <div className="chat-actions">
              <button className="refresh-button" onClick={() => { setSelectedWorkflowRunId(workflow.id); void refreshWorkflows(); }}>Inspect</button>
              <button className="refresh-button" onClick={() => void workflowClient.pause(workflow.id, settings).then(() => refreshWorkflows())} disabled={chatLoading}>Pause</button>
              <button className="refresh-button" onClick={() => void workflowClient.resume(workflow.id, settings).then(() => refreshWorkflows())} disabled={chatLoading}>Resume</button>
              <button className="refresh-button" onClick={() => void workflowClient.createReplay(workflow.id, settings).then(() => refreshWorkflows())} disabled={chatLoading}>Replay metadata</button>
              <button className="refresh-button" onClick={() => void workflowClient.createReplaySession(workflow.id, settings).then((replay) => { setWorkflowReplaySessions((current) => [replay, ...current]); return refreshWorkflows(); })} disabled={chatLoading}>Replay Center</button>
            </div>
          </div>
        )) : (
          <div className="empty-chat">No workflow runs yet.</div>
        )}
        <h4>Workflow timeline {selectedWorkflowRunId ? `for ${selectedWorkflowRunId}` : ""}</h4>
        <div className="chat-note">
          Graph execution panel: current node, planned next nodes, skipped nodes, retry/fallback state. This is not a visual DAG editor.
        </div>
        <pre className="metadata-preview">{JSON.stringify({
          current_node: workflowPlanner?.current_node ?? null,
          next_nodes: workflowPlanner?.next_nodes ?? [],
          skipped_nodes: workflowPlanner?.skipped_nodes ?? [],
          retry_paths: workflowPlanner?.retry_paths ?? [],
          fallback_paths: workflowPlanner?.fallback_paths ?? [],
          condition_results: workflowPlanner?.condition_results ?? [],
          analytics: workflowAnalytics ?? {},
          trace_count: workflowTraces.length,
          diagnostics: workflowDiagnostics.map((item) => ({ type: item.diagnostic_type, severity: item.severity, summary: item.summary })),
          replay_sessions: workflowReplaySessions.map((item) => ({ id: item.id, mode: item.replay_mode, status: item.replay_status })),
        }, null, 2)}</pre>
        <h4>Execution Traces / Diagnostics</h4>
        {workflowTraces.length > 0 ? workflowTraces.slice(0, 8).map((trace) => (
          <div key={trace.id} className="event-item">
            <strong>{trace.event_type}</strong>
            <span>{trace.node_key ?? "-"} | retry: {trace.retry_count} | fallback: {String(trace.fallback_triggered)}</span>
          </div>
        )) : (
          <div className="empty-chat">No execution traces yet.</div>
        )}
        {workflowDiagnostics.length > 0 ? workflowDiagnostics.slice(0, 4).map((diagnostic) => (
          <div key={diagnostic.id} className="event-item">
            <strong>{diagnostic.severity}: {diagnostic.diagnostic_type}</strong>
            <span>{diagnostic.summary}</span>
          </div>
        )) : null}
        {workflowSteps.length > 0 ? workflowSteps.map((step) => (
          <div key={step.id} className="event-item">
            <strong>{step.step_name}</strong>
            <span>{step.status} | {step.step_type} | node: {step.node_key ?? "-"} | duration: {step.duration_ms ?? "-"}ms</span>
            {step.error ? <code>{step.error}</code> : null}
          </div>
        )) : (
          <div className="empty-chat">Select a workflow run to inspect steps.</div>
        )}
        <h4>Agent Memory Snapshots</h4>
        {memorySnapshots.length > 0 ? memorySnapshots.map((snapshot) => (
          <div key={snapshot.id} className="event-item">
            <strong>{snapshot.memory_type}</strong>
            <span>{snapshot.summary ?? "-"}</span>
          </div>
        )) : (
          <div className="empty-chat">No memory snapshots yet.</div>
        )}
      </details>
      <details id="tasks-panel" className="approval-list workbench-detail" open={failedTaskRuns.length > 0 || activeTaskRuns.length > 0}>
        <summary>{workbenchCopy.tasksSummary}</summary>
        <h3>Task Runs</h3>
        <div className="chat-note">
          Background execution uses the in-process queue with lease, recovery, retry, cancel, approval resume, task timeline, and artifact linkage. It is not Celery, not Kubernetes, and not production HA.
        </div>
        <div className="chat-note">
          Scheduler: {String(schedulerHealth?.status ?? "unavailable")} | heartbeat: {String(schedulerHealth?.heartbeat_at ?? "-")} | recovered: {String(schedulerHealth?.recovered_task_count ?? 0)}
        </div>
        <div className="chat-actions">
          <button className="refresh-button" onClick={() => void refreshTaskRuns()}>
            <RefreshCcw size={15} />
            Refresh task status
          </button>
        </div>
        {taskRuns.length > 0 ? taskRuns.slice(0, 8).map((task) => (
          <div key={task.id} className="approval-card">
            <div className="approval-card-header">
              <strong>{task.task_type}</strong>
              <span>{task.status}</span>
            </div>
            <div className="chat-meta">
              task_run_id: {task.id} | workflow_run_id: {task.workflow_run_id ?? "-"} | step: {task.current_step} | retry: {task.retry_count}/{task.max_retries} | recoverable: {String(task.recoverable)} | lease: {task.lease_expires_at ?? "-"}
            </div>
            <p>{String(task.error ?? task.suggested_action ?? task.output_payload.summary ?? "No error")}</p>
            <div className="chat-actions">
              <button className="refresh-button" onClick={() => { setSelectedTaskRunId(task.id); void refreshTaskRuns(); }}>Events</button>
              <button className="refresh-button" onClick={() => void mutateTaskRun(task.id, "retry")} disabled={chatLoading}>Retry</button>
              <button className="refresh-button" onClick={() => void mutateTaskRun(task.id, "cancel")} disabled={chatLoading}>Cancel</button>
              <button className="refresh-button" onClick={() => void mutateTaskRun(task.id, "resume")} disabled={chatLoading}>Resume</button>
              <button className="refresh-button" onClick={() => void mutateTaskRun(task.id, "recover")} disabled={chatLoading}>Recover</button>
            </div>
          </div>
        )) : (
          <div className="empty-chat">No background task runs yet.</div>
        )}
        <h4>Task timeline {selectedTaskRunId ? `for ${selectedTaskRunId}` : ""}</h4>
        {taskEvents.length > 0 ? taskEvents.map((event) => (
          <div key={event.id} className="event-item">
            <strong>{event.event_type}</strong>
            <span>{event.message ?? "-"}</span>
            <code>{JSON.stringify(event.payload)}</code>
          </div>
        )) : (
          <div className="empty-chat">Select a task run to inspect its timeline.</div>
        )}
      </details>
      </details>
    </section>
  );
}
function BrowserSessionsPanel() {
  const [sessions, setSessions] = useState<BrowserRuntimeSession[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [events, setEvents] = useState<BrowserRuntimeEvent[]>([]);
  const [snapshots, setSnapshots] = useState<BrowserRuntimeSnapshot[]>([]);
  const [replay, setReplay] = useState<BrowserRuntimeReplay | null>(null);
  const [replayExportPath, setReplayExportPath] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  const refreshSessions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await browserRuntimeClient.listSessions();
      setSessions(response.items);
      setLastUpdated(new Date().toLocaleString());
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Browser Runtime API unreachable");
    } finally {
      setLoading(false);
    }
  }, []);

  const refreshTimeline = useCallback(
    async (sessionId: string) => {
      setLoading(true);
      setError(null);
      try {
        const [nextEvents, nextSnapshots] = await Promise.all([
          browserRuntimeClient.listEvents(sessionId),
          browserRuntimeClient.listSnapshots(sessionId),
        ]);
        setSelectedSessionId(sessionId);
        setEvents(nextEvents.items);
        setSnapshots(nextSnapshots.items);
        setLastUpdated(new Date().toLocaleString());
      } catch (nextError) {
        setError(nextError instanceof Error ? nextError.message : "Browser Runtime timeline API unreachable");
      } finally {
        setLoading(false);
      }
    },
    [],
  );

  const createReplay = async () => {
    if (!selectedSessionId) {
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const nextReplay = await browserRuntimeClient.createReplay(selectedSessionId);
      const exported = await browserRuntimeClient.exportReplay(nextReplay.id);
      setReplay(exported.replay);
      setReplayExportPath(exported.export_path);
      await refreshTimeline(selectedSessionId);
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Create browser runtime replay failed");
    } finally {
      setLoading(false);
    }
  };

  const closeSession = async (sessionId: string) => {
    setLoading(true);
    setError(null);
    try {
      await browserRuntimeClient.closeSession(sessionId);
      await refreshSessions();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Close browser runtime session failed");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refreshSessions();
  }, [refreshSessions]);

  return (
    <section className="panel browser-sessions-panel">
      <div className="panel-title logs-title">
        <span>
          <Server size={18} />
          <h2>Browser Sessions</h2>
        </span>
        <button className="refresh-button" onClick={() => void refreshSessions()} disabled={loading}>
          <RefreshCcw size={15} />
          Refresh
        </button>
      </div>
      <div className="chat-meta">
        API: {browserRuntimeClient.baseUrl} | workspace: {browserRuntimeClient.workspaceId} | last updated: {lastUpdated ?? "-"}
      </div>
      {error ? (
        <div className="inline-error">
          <AlertTriangle size={16} />
          {error}
        </div>
      ) : null}
      <div className="session-table">
        <div className="session-row session-row-head">
          <span>session</span>
          <span>worker</span>
          <span>browser</span>
          <span>status</span>
          <span>current_url</span>
          <span>created_at</span>
          <span>action</span>
        </div>
        {sessions.length > 0 ? (
          sessions.map((session) => (
            <div className="session-row" key={session.id}>
              <span>{session.id}</span>
              <span>{session.worker_id}</span>
              <span>{session.browser}</span>
              <span>{session.session_status}</span>
              <span>{session.current_url ?? "-"}</span>
              <span>{session.created_at}</span>
              <span className="session-actions">
                <button className="icon-button" onClick={() => void refreshTimeline(session.id)} disabled={loading}>
                  <RefreshCcw size={15} />
                  Inspect
                </button>
                <button className="icon-button" onClick={() => void closeSession(session.id)} disabled={loading}>
                  <XCircle size={15} />
                  Close
                </button>
              </span>
            </div>
          ))
        ) : (
          <div className="empty-chat session-empty">No active remote browser runtime sessions.</div>
        )}
      </div>
      <div className="runtime-debug-grid">
        <section className="runtime-debug-card">
          <div className="runtime-debug-title">
            <strong>Timeline</strong>
            <button className="refresh-button" onClick={() => selectedSessionId && void refreshTimeline(selectedSessionId)} disabled={!selectedSessionId || loading}>
              <RefreshCcw size={14} />
              Refresh events
            </button>
          </div>
          {events.length > 0 ? (
            <div className="runtime-timeline">
              {events.map((event) => (
                <div key={event.id} className={`runtime-event runtime-event-${event.status}`}>
                  <span>{event.event_type}</span>
                  <p>{event.message ?? "-"}</p>
                  <small>
                    {event.duration_ms ?? "-"}ms | {event.created_at}
                  </small>
                  {event.error ? <em>{event.error}</em> : null}
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-chat">Select a browser session to view timeline events.</div>
          )}
        </section>
        <section className="runtime-debug-card">
          <div className="runtime-debug-title">
            <strong>Snapshots</strong>
            <button className="refresh-button" onClick={() => selectedSessionId && void refreshTimeline(selectedSessionId)} disabled={!selectedSessionId || loading}>
              <RefreshCcw size={14} />
              Refresh snapshots
            </button>
          </div>
          {snapshots.length > 0 ? (
            <div className="snapshot-list">
              {snapshots.map((snapshot) => (
                <div key={snapshot.id} className="snapshot-item">
                  <span>{snapshot.snapshot_type}</span>
                  <p>{snapshot.page_title ?? snapshot.url ?? "-"}</p>
                  <small>
                    html: {snapshot.html_path ?? "-"} | text: {snapshot.text_path ?? "-"} | screenshot:{" "}
                    {snapshot.screenshot_path ?? "-"}
                  </small>
                </div>
              ))}
            </div>
          ) : (
            <div className="empty-chat">No page snapshots or screenshot history loaded.</div>
          )}
        </section>
        <section className="runtime-debug-card replay-card">
          <div className="runtime-debug-title">
            <strong>Replay metadata</strong>
            <button className="refresh-button" onClick={() => void createReplay()} disabled={!selectedSessionId || loading}>
              <RotateCcw size={14} />
              Create replay
            </button>
          </div>
          <p className="chat-note">Replay is metadata-only. It does not re-run browser actions.</p>
          <pre className="replay-view">
            {replay ? JSON.stringify({ replay, export_path: replayExportPath }, null, 2) : "No replay metadata generated."}
          </pre>
        </section>
      </div>
    </section>
  );
}

function loadStoredConversationSettings(storageKey: string): ConversationSettings {
  const stored = window.localStorage.getItem(storageKey);
  if (!stored) {
    return conversationClient.defaultSettings;
  }
  try {
    return { ...conversationClient.defaultSettings, ...JSON.parse(stored) };
  } catch {
    return conversationClient.defaultSettings;
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function documentDisplayName(document: KnowledgeDocument): string {
  return document.source_name || document.filename || document.source_id || document.id || "Untitled material";
}

const KNOWLEDGE_MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024;
const SUPPORTED_KNOWLEDGE_EXTENSIONS = [".pdf", ".docx", ".txt", ".md", ".csv"];

function knowledgeFileExtension(fileName: string): string {
  const extension = fileName.slice(fileName.lastIndexOf(".")).toLowerCase();
  return extension.startsWith(".") ? extension : "";
}

function knowledgeQueueId(file: File): string {
  return `${file.name}-${file.lastModified}-${Math.random().toString(36).slice(2)}`;
}

function knowledgeActivityId(): string {
  return `knowledge-activity-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function KnowledgeBasePanel({
  language,
  settingsStorageKey,
}: {
  language: ClientLanguage;
  settingsStorageKey: string;
}) {
  const copy = knowledgeBaseCopy[language];
  const [settings] = useState<ConversationSettings>(() => loadStoredConversationSettings(settingsStorageKey));
  const [collectionName, setCollectionName] = useState("operations");
  const [duplicateStrategy, setDuplicateStrategy] = useState<"skip" | "force_reingest">("skip");
  const [queue, setQueue] = useState<KnowledgeQueueItem[]>([]);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [libraryState, setLibraryState] = useState<"idle" | "loading" | "ready" | "failed">("idle");
  const [message, setMessage] = useState<string | null>(null);
  const [editMode, setEditMode] = useState<"add" | "replace">("add");
  const [sourceName, setSourceName] = useState("");
  const [sourceId, setSourceId] = useState("");
  const [sourceText, setSourceText] = useState("");
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [activities, setActivities] = useState<KnowledgeActivityItem[]>([]);

  const addKnowledgeActivity = useCallback((activity: Omit<KnowledgeActivityItem, "id" | "time">) => {
    setActivities((current) => [
      {
        ...activity,
        id: knowledgeActivityId(),
        time: new Date().toLocaleString(),
      },
      ...current,
    ].slice(0, 6));
  }, []);

  const queueStatusLabels: Record<KnowledgeQueueStatus, string> = {
    queued: copy.queued,
    uploading: copy.uploading,
    uploaded: copy.uploaded,
    failed: copy.failed,
  };
  const queuedFileCount = queue.filter((item) => item.status === "queued").length;
  const uploadingFileCount = queue.filter((item) => item.status === "uploading").length;
  const uploadedFileCount = queue.filter((item) => item.status === "uploaded").length;
  const failedFileCount = queue.filter((item) => item.status === "failed").length;
  const retryableFailedCount = queue.filter((item) => item.status === "failed" && item.retryable !== false).length;
  const totalUploadableFileCount = queuedFileCount + retryableFailedCount;
  const knowledgeConnectionReady = libraryState !== "failed";
  const nextKnowledgeStep =
    libraryState === "failed" || failedFileCount > 0
      ? copy.nextStepRecover
      : uploading || uploadingFileCount > 0
        ? copy.nextStepWait
        : queuedFileCount > 0
          ? copy.nextStepUpload
          : documents.length > 0
            ? copy.nextStepReady
            : copy.nextStepChoose;
  const readinessCards = [
    {
      label: copy.connectionLabel,
      value: knowledgeConnectionReady ? copy.connectionReady : copy.connectionIssue,
      state: knowledgeConnectionReady ? "good" : "warn",
    },
    {
      label: copy.collectionStatusLabel,
      value: collectionName.trim() ? copy.collectionReady : copy.collectionMissing,
      state: collectionName.trim() ? "good" : "warn",
    },
    {
      label: copy.queueStatusLabel,
      value: queuedFileCount > 0 || failedFileCount > 0 ? `${queuedFileCount + failedFileCount} ${copy.queueNeedsUpload}` : copy.queueReady,
      state: totalUploadableFileCount > 0 || failedFileCount > 0 ? "warn" : "good",
    },
    {
      label: copy.libraryStatusLabel,
      value: documents.length > 0 ? `${documents.length} ${copy.libraryReady}` : copy.libraryEmpty,
      state: documents.length > 0 ? "good" : "warn",
    },
  ];

  const refreshDocuments = useCallback(async (recordActivity = false) => {
    setLibraryState("loading");
    try {
      const response = await knowledgeBaseClient.documents(settings);
      setDocuments(response.items);
      setLibraryState("ready");
      if (recordActivity) {
        addKnowledgeActivity({
          title: copy.activityRefreshTitle,
          detail: `${copy.activitySuccess}: ${response.items.length}`,
          meta: `${copy.activityCollection}: ${collectionName.trim() || copy.collectionMissing}`,
          tone: "good",
        });
      }
    } catch {
      setDocuments([]);
      setLibraryState("failed");
      setMessage(copy.requestFailed);
      if (recordActivity) {
        addKnowledgeActivity({
          title: copy.activityRefreshTitle,
          detail: copy.requestFailed,
          meta: `${copy.activityCollection}: ${collectionName.trim() || copy.collectionMissing}`,
          tone: "warn",
        });
      }
    }
  }, [
    addKnowledgeActivity,
    collectionName,
    copy.activityCollection,
    copy.activityRefreshTitle,
    copy.activitySuccess,
    copy.collectionMissing,
    copy.requestFailed,
    settings,
  ]);

  useEffect(() => {
    void refreshDocuments();
  }, [refreshDocuments]);

  const addFiles = (files: FileList | File[]) => {
    const nextFiles = Array.from(files);
    if (nextFiles.length === 0) {
      return;
    }
    let invalidFileCount = 0;
    setQueue((current) => [
      ...nextFiles.map((file) => {
        const extension = knowledgeFileExtension(file.name);
        const validationMessage = !SUPPORTED_KNOWLEDGE_EXTENSIONS.includes(extension)
          ? copy.unsupportedFile
          : file.size > KNOWLEDGE_MAX_FILE_SIZE_BYTES
            ? copy.fileTooLarge
            : null;
        if (validationMessage) {
          invalidFileCount += 1;
        }
        return {
          id: knowledgeQueueId(file),
          file,
          status: (validationMessage ? "failed" : "queued") as KnowledgeQueueStatus,
          message: validationMessage ?? undefined,
          retryable: !validationMessage,
        };
      }),
      ...current,
    ]);
    addKnowledgeActivity({
      title: copy.activitySelectedTitle,
      detail: `${copy.activityFiles}: ${nextFiles.length}; ${copy.activityInvalid}: ${invalidFileCount}`,
      meta: `${copy.activityCollection}: ${collectionName.trim() || copy.collectionMissing}`,
      tone: invalidFileCount > 0 ? "warn" : "neutral",
    });
    setMessage(invalidFileCount > 0 ? copy.nextStepRecover : null);
  };

  const uploadSelectedFiles = async () => {
    const pendingItems = queue.filter((item) => item.status === "queued" || (item.status === "failed" && item.retryable !== false));
    if (pendingItems.length === 0) {
      return;
    }
    setUploading(true);
    setMessage(null);
    let hasFailure = false;
    let uploadedCount = 0;
    let failedCount = 0;
    for (const item of pendingItems) {
      setQueue((current) =>
        current.map((queueItem) =>
          queueItem.id === item.id ? { ...queueItem, status: "uploading", message: undefined } : queueItem,
        ),
      );
      try {
        await knowledgeBaseClient.uploadFile(
          {
            file: item.file,
            collectionName: collectionName.trim() || undefined,
            duplicateStrategy,
          },
          settings,
        );
        setQueue((current) =>
          current.map((queueItem) =>
            queueItem.id === item.id ? { ...queueItem, status: "uploaded", message: copy.uploaded } : queueItem,
          ),
        );
        uploadedCount += 1;
      } catch {
        hasFailure = true;
        failedCount += 1;
        setQueue((current) =>
          current.map((queueItem) =>
            queueItem.id === item.id ? { ...queueItem, status: "failed", message: copy.requestFailed, retryable: true } : queueItem,
          ),
        );
      }
    }
    setUploading(false);
    addKnowledgeActivity({
      title: copy.activityUploadTitle,
      detail: `${copy.activitySuccess}: ${uploadedCount}; ${copy.activityFailed}: ${failedCount}`,
      meta: `${copy.activityCollection}: ${collectionName.trim() || copy.collectionMissing}`,
      tone: failedCount > 0 ? "warn" : "good",
    });
    setMessage(hasFailure ? copy.nextStepRecover : copy.uploaded);
    await refreshDocuments();
  };

  const removeKnowledgeQueueItem = (queueItemId: string) => {
    const removedItem = queue.find((item) => item.id === queueItemId);
    setQueue((current) => current.filter((item) => item.id !== queueItemId));
    if (removedItem) {
      addKnowledgeActivity({
        title: copy.activityRemovedTitle,
        detail: removedItem.file.name,
        meta: `${copy.activityCollection}: ${collectionName.trim() || copy.collectionMissing}`,
        tone: "neutral",
      });
    }
  };

  const clearCompletedKnowledgeFiles = () => {
    const completedCount = queue.filter((item) => item.status === "uploaded").length;
    setQueue((current) => current.filter((item) => item.status !== "uploaded"));
    addKnowledgeActivity({
      title: copy.activityClearedTitle,
      detail: `${copy.activitySuccess}: ${completedCount}`,
      meta: `${copy.activityCollection}: ${collectionName.trim() || copy.collectionMissing}`,
      tone: "neutral",
    });
  };

  const saveTextKnowledge = async () => {
    const text = sourceText.trim();
    const resolvedSourceId = sourceId.trim();
    if (!text) {
      setMessage(copy.textRequired);
      return;
    }
    if (editMode === "replace" && !resolvedSourceId) {
      setMessage(copy.sourceIdRequired);
      return;
    }
    setSaving(true);
    setMessage(null);
    try {
      if (editMode === "replace") {
        await knowledgeBaseClient.reingestText(
          {
            text,
            sourceId: resolvedSourceId,
            sourceName: sourceName.trim() || resolvedSourceId,
            collectionName: collectionName.trim() || undefined,
          },
          settings,
        );
      } else {
        await knowledgeBaseClient.ingestText(
          {
            text,
            sourceName: sourceName.trim() || undefined,
            sourceId: resolvedSourceId || undefined,
            collectionName: collectionName.trim() || undefined,
          },
          settings,
        );
      }
      setSourceText("");
      setMessage(copy.saved);
      addKnowledgeActivity({
        title: copy.activityTextSavedTitle,
        detail: sourceName.trim() || resolvedSourceId || copy.activityTextSavedTitle,
        meta: `${copy.activityCollection}: ${collectionName.trim() || copy.collectionMissing}`,
        tone: "good",
      });
      await refreshDocuments();
    } catch {
      setMessage(copy.requestFailed);
      addKnowledgeActivity({
        title: copy.activityTextSavedTitle,
        detail: copy.requestFailed,
        meta: `${copy.activityCollection}: ${collectionName.trim() || copy.collectionMissing}`,
        tone: "warn",
      });
    } finally {
      setSaving(false);
    }
  };

  const selectDocumentForEdit = (document: KnowledgeDocument) => {
    setEditMode("replace");
    setSourceName(documentDisplayName(document));
    setSourceId(document.source_id || document.id || "");
    setMessage(null);
  };

  return (
    <section id="knowledge-base-panel" className="panel knowledge-base-panel">
      <div className="panel-title logs-title">
        <span>
          <Database size={18} />
          <h2>{copy.title}</h2>
        </span>
        <button className="refresh-button" onClick={() => void refreshDocuments(true)} disabled={libraryState === "loading"}>
          <RefreshCcw size={15} />
          {copy.refreshLibrary}
        </button>
      </div>
      <div className="knowledge-hero">
        <p>{copy.subtitle}</p>
        <div className="knowledge-flow-grid">
          {copy.flowSteps.map((step, index) => (
            <div className="knowledge-flow-step" key={step.title}>
              <span>{index + 1}</span>
              <strong>{step.title}</strong>
              <p>{step.body}</p>
            </div>
          ))}
        </div>
        <div className="knowledge-readiness-strip" aria-label={copy.readinessTitle}>
          {readinessCards.map((card) => (
            <div className={`knowledge-readiness-card ${card.state}`} key={card.label}>
              <span>{card.label}</span>
              <strong>{card.value}</strong>
            </div>
          ))}
        </div>
        <div className={`knowledge-next-step-card ${knowledgeConnectionReady ? "ready" : "warn"}`}>
          <span>{copy.nextStepTitle}</span>
          <strong>{nextKnowledgeStep}</strong>
        </div>
      </div>
      <div className="knowledge-action-grid">
        <section className="knowledge-upload-card" aria-label={copy.uploadTitle}>
          <div className="knowledge-card-title">
            <Upload size={17} />
            <div>
              <h3>{copy.uploadTitle}</h3>
              <p>{copy.uploadHint}</p>
            </div>
          </div>
          <label
            className="knowledge-upload-drop"
            onDragOver={(event) => event.preventDefault()}
            onDrop={(event) => {
              event.preventDefault();
              addFiles(event.dataTransfer.files);
            }}
          >
            <Upload size={24} />
            <strong>{copy.chooseFiles}</strong>
            <span>{copy.uploadHint}</span>
            <input
              type="file"
              multiple
              onChange={(event) => {
                if (event.target.files) {
                  addFiles(event.target.files);
                  event.currentTarget.value = "";
                }
              }}
            />
          </label>
          <div className="knowledge-file-rules">
            <strong>{copy.fileRulesTitle}</strong>
            <span>{copy.fileRulesBody}</span>
          </div>
          <div className="knowledge-form-row">
            <label>
              {copy.collectionLabel}
              <input
                value={collectionName}
                placeholder={copy.collectionPlaceholder}
                onChange={(event) => setCollectionName(event.target.value)}
              />
            </label>
            <label>
              {copy.duplicateLabel}
              <select
                value={duplicateStrategy}
                onChange={(event) => setDuplicateStrategy(event.target.value as "skip" | "force_reingest")}
              >
                <option value="skip">{copy.duplicateSkip}</option>
                <option value="force_reingest">{copy.duplicateReplace}</option>
              </select>
            </label>
          </div>
          <div className="knowledge-button-row">
            <button className="action-button primary-action" onClick={() => void uploadSelectedFiles()} disabled={uploading || totalUploadableFileCount === 0}>
              <Upload size={16} />
              {copy.uploadSelected}
            </button>
            {retryableFailedCount > 0 ? (
              <button className="refresh-button" onClick={() => void uploadSelectedFiles()} disabled={uploading}>
                <RefreshCcw size={15} />
                {copy.retryFailed}
              </button>
            ) : null}
            {uploadedFileCount > 0 ? (
              <button className="refresh-button" onClick={clearCompletedKnowledgeFiles}>
                <XCircle size={15} />
                {copy.clearCompleted}
              </button>
            ) : null}
          </div>
          <div className="knowledge-queue">
            {queue.length > 0 ? (
              queue.map((item) => (
                <div className={`knowledge-file-card ${item.status}`} key={item.id}>
                  <FileText size={17} />
                  <div>
                    <strong>{item.file.name}</strong>
                    <span>{formatFileSize(item.file.size)}</span>
                    {item.message ? <p>{item.message}</p> : null}
                  </div>
                  <span className={`knowledge-status-badge ${item.status}`}>{queueStatusLabels[item.status]}</span>
                  <button
                    className="knowledge-file-remove"
                    onClick={() => removeKnowledgeQueueItem(item.id)}
                    disabled={item.status === "uploading"}
                    aria-label={`${copy.removeFile} ${item.file.name}`}
                  >
                    <XCircle size={14} />
                    {copy.removeFile}
                  </button>
                </div>
              ))
            ) : (
              <div className="knowledge-empty">{copy.emptyQueue}</div>
            )}
          </div>
        </section>
        <section className="knowledge-edit-card" aria-label={copy.editTitle}>
          <div className="knowledge-card-title">
            <PencilLine size={17} />
            <div>
              <h3>{copy.editTitle}</h3>
              <p>{editMode === "replace" ? copy.replaceText : copy.addText}</p>
            </div>
          </div>
          <div className="knowledge-mode-toggle">
            <button className={editMode === "add" ? "active" : ""} onClick={() => setEditMode("add")} type="button">
              {copy.addText}
            </button>
            <button className={editMode === "replace" ? "active" : ""} onClick={() => setEditMode("replace")} type="button">
              {copy.replaceText}
            </button>
          </div>
          <div className="knowledge-form-row">
            <label>
              {copy.sourceNameLabel}
              <input
                value={sourceName}
                placeholder={copy.sourceNamePlaceholder}
                onChange={(event) => setSourceName(event.target.value)}
              />
            </label>
            <label>
              {copy.sourceIdLabel}
              <input
                value={sourceId}
                placeholder={copy.sourceIdPlaceholder}
                onChange={(event) => setSourceId(event.target.value)}
              />
            </label>
          </div>
          <label className="knowledge-textarea-label">
            {copy.contentLabel}
            <textarea
              value={sourceText}
              placeholder={copy.contentPlaceholder}
              onChange={(event) => setSourceText(event.target.value)}
            />
          </label>
          <button className="action-button primary-action" onClick={() => void saveTextKnowledge()} disabled={saving}>
            <FileText size={16} />
            {copy.saveKnowledge}
          </button>
          {message ? <div className="knowledge-message">{message}</div> : null}
        </section>
      </div>
      <section className="knowledge-activity-panel" aria-label={copy.activityTitle}>
        <div className="knowledge-activity-header">
          <div className="knowledge-card-title">
            <Activity size={17} />
            <div>
              <span>{copy.ready}</span>
              <h3>{copy.activityTitle}</h3>
            </div>
          </div>
          <button className="refresh-button" onClick={() => setActivities([])} disabled={activities.length === 0}>
            <XCircle size={15} />
            {copy.clearActivity}
          </button>
        </div>
        <div className="knowledge-activity-list">
          {activities.length > 0 ? (
            activities.map((activity) => (
              <article className={`knowledge-activity-item ${activity.tone}`} key={activity.id}>
                <span className="knowledge-activity-dot" />
                <div>
                  <strong>{activity.title}</strong>
                  <p>{activity.detail}</p>
                  <span>{activity.meta}</span>
                </div>
                <time>{activity.time}</time>
              </article>
            ))
          ) : (
            <div className="knowledge-empty">{copy.activityEmpty}</div>
          )}
        </div>
      </section>
      <section className="knowledge-library-section" aria-label={copy.libraryTitle}>
        <div className="knowledge-library-header">
          <div>
            <span>{libraryState === "loading" ? copy.loading : libraryState === "failed" ? copy.failed : copy.ready}</span>
            <h3>{copy.libraryTitle}</h3>
          </div>
          <button className="refresh-button" onClick={() => void refreshDocuments(true)} disabled={libraryState === "loading"}>
            <RefreshCcw size={15} />
            {copy.refreshLibrary}
          </button>
        </div>
        <div className="knowledge-document-grid">
          {documents.length > 0 ? (
            documents.slice(0, 12).map((document) => (
              <article className="knowledge-document-card" key={document.id ?? document.source_id ?? documentDisplayName(document)}>
                <div className="knowledge-document-main">
                  <FileText size={18} />
                  <div>
                    <strong>{documentDisplayName(document)}</strong>
                    <span>{document.collection_name ?? collectionName}</span>
                  </div>
                </div>
                <div className="knowledge-document-meta">
                  <span>{copy.documentStatus}: {document.status ?? copy.ready}</span>
                  <span>{copy.documentChunks}: {document.chunk_count ?? "-"}</span>
                  <span>{copy.updatedAt}: {document.updated_at ?? document.created_at ?? "-"}</span>
                </div>
                <button className="refresh-button" onClick={() => selectDocumentForEdit(document)}>
                  <PencilLine size={14} />
                  {copy.editExisting}
                </button>
              </article>
            ))
          ) : (
            <div className="knowledge-empty">{copy.emptyLibrary}</div>
          )}
        </div>
      </section>
    </section>
  );
}

function App() {
  const [status, setStatus] = useState<WorkerStatus>(fallbackStatus);
  const [health, setHealth] = useState<WorkerHealth | null>(null);
  const [logs, setLogs] = useState<WorkerLogs>({ lines: [] });
  const [language, setLanguage] = useState<ClientLanguage>(() => {
    const stored = window.localStorage.getItem("workerConsoleLanguage");
    return stored === "en-US" ? "en-US" : "zh-CN";
  });
  const [operatorPage, setOperatorPage] = useState<OperatorPage>("operations");
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<ControlAction | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<string | null>(null);
  const copy = clientCopy[language];

  const refresh = useCallback(async () => {
    try {
      setError(null);
      const [nextStatus, nextHealth, nextLogs] = await Promise.all([
        localWorkerClient.getStatus(),
        localWorkerClient.getHealth(),
        localWorkerClient.getLogs(200),
      ]);
      setStatus({ ...fallbackStatus, ...nextStatus });
      setHealth(nextHealth);
      setLogs(nextLogs);
      setLastRefresh(new Date().toLocaleString());
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Worker API unreachable");
      setHealth(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
    const timer = window.setInterval(() => void refresh(), 5000);
    return () => window.clearInterval(timer);
  }, [refresh]);

  useEffect(() => {
    window.localStorage.setItem("workerConsoleLanguage", language);
  }, [language]);

  const runControl = async (action: ControlAction) => {
    setActionLoading(action);
    setError(null);
    try {
      const nextStatus = await localWorkerClient[action]();
      setStatus({ ...fallbackStatus, ...nextStatus });
      await refresh();
    } catch (nextError) {
      setError(nextError instanceof Error ? nextError.message : "Worker API unreachable");
    } finally {
      setActionLoading(null);
    }
  };

  const latestLogs = useMemo(() => logs.lines.slice(-120), [logs.lines]);
  const apiUnreachable = Boolean(error && !health);

  return (
    <main className="app-shell min-h-screen">
      <section className="topbar">
        <div>
          <p className="eyeline">AI Ops Worker Console</p>
          <h1>{copy.appTitle}</h1>
        </div>
        <div className="topbar-status">
          <StatusBadge label={copy.runtimeLabel} active={status.runtime_running} />
          <StatusBadge label={copy.heartbeatLabel} active={status.heartbeat_running} />
        </div>
      </section>

      {apiUnreachable ? (
        <section className="alert-panel">
          <WifiOff size={22} />
          <div>
            <strong>Worker API unreachable</strong>
            <p>
              Worker Runtime is not running. 请确认 worker_client 是否启动；请确认端口是否为 9100.
            </p>
            <code>{localWorkerClient.baseUrl}</code>
          </div>
        </section>
      ) : null}

      <WorkstationHome
        status={status}
        health={health}
        error={error}
        localApi={localWorkerClient.baseUrl}
        actionLoading={actionLoading}
        language={language}
        onLanguageChange={setLanguage}
        onRefresh={() => void refresh()}
        onRunControl={(action) => void runControl(action)}
      />

      <section className="operator-page-tabs" aria-label="Client operation pages">
        <button
          className={operatorPage === "operations" ? "active" : ""}
          onClick={() => setOperatorPage("operations")}
          type="button"
        >
          <MessageCircle size={16} />
          {copy.pageOperations}
        </button>
        <button
          className={operatorPage === "knowledge" ? "active" : ""}
          onClick={() => setOperatorPage("knowledge")}
          type="button"
        >
          <Database size={16} />
          {copy.pageKnowledge}
        </button>
      </section>

      {operatorPage === "knowledge" ? (
        <KnowledgeBasePanel language={language} settingsStorageKey="workerConsoleConversationSettings" />
      ) : (
        <ChatPanel language={language} />
      )}

      <details className="advanced-diagnostics">
        <summary>{copy.advancedSummary}</summary>
      <section className="layout-grid">
        <section className="panel dashboard-panel">
          <div className="panel-title">
            <Server size={18} />
            <h2>Dashboard</h2>
          </div>
          <div className="field-grid">
            <Field label="worker_name" value={status.worker_name} />
            <Field label="worker_id" value={status.worker_id} />
            <Field label="workspace_id" value={status.workspace_id} />
            <Field label="server_url" value={status.server_url} />
            <Field label="registered" value={String(status.registered)} />
            <Field label="runtime_running" value={String(status.runtime_running)} />
            <Field label="heartbeat_running" value={String(status.heartbeat_running)} />
            <Field label="current_status" value={status.current_status} />
            <Field label="last_heartbeat_at" value={status.last_heartbeat_at} />
            <Field label="last_error" value={status.last_error ?? "-"} />
          </div>
        </section>

        <section className="panel control-panel">
          <div className="panel-title">
            <Activity size={18} />
            <h2>Runtime Control</h2>
          </div>
          <div className="control-grid">
            <ActionButton
              icon={<PlayCircle size={16} />}
              label="Start Runtime"
              disabled={Boolean(actionLoading)}
              onClick={() => void runControl("startRuntime")}
            />
            <ActionButton
              icon={<Square size={16} />}
              label="Stop Runtime"
              disabled={Boolean(actionLoading)}
              onClick={() => void runControl("stopRuntime")}
            />
            <ActionButton
              icon={<RotateCcw size={16} />}
              label="Restart Runtime"
              disabled={Boolean(actionLoading)}
              onClick={() => void runControl("restartRuntime")}
            />
            <ActionButton
              icon={<Wifi size={16} />}
              label="Start Heartbeat"
              disabled={Boolean(actionLoading)}
              onClick={() => void runControl("startHeartbeat")}
            />
            <ActionButton
              icon={<WifiOff size={16} />}
              label="Stop Heartbeat"
              disabled={Boolean(actionLoading)}
              onClick={() => void runControl("stopHeartbeat")}
            />
          </div>
          <div className="control-note">
            {actionLoading ? `Running ${actionLoading}...` : loading ? "Loading local worker state..." : `Last refresh: ${lastRefresh ?? "-"}`}
          </div>
        </section>

        <section className="panel connection-panel">
          <div className="panel-title">
            <Wifi size={18} />
            <h2>Connection Info</h2>
          </div>
          <div className="field-grid compact">
            <Field label="local_api" value={localWorkerClient.baseUrl} />
            <Field label="server_url" value={status.server_url} />
            <Field label="worker_base_url" value={status.worker_base_url} />
            <Field label="runtime_port" value={status.runtime_port} />
            <Field label="openclaw_enabled" value={String(status.openclaw_enabled)} />
            <Field label="browser_enabled" value={String(status.browser_enabled)} />
          </div>
        </section>

        <section className="panel connection-panel">
          <div className="panel-title">
            <Server size={18} />
            <h2>Deployment Profile Help</h2>
          </div>
          <div className="field-grid compact">
            <Field label="recommended_profile" value="client-worker for worker_client; desktop-client for Tauri Desktop" />
            <Field label="ai_server_url" value={status.server_url ?? "set VITE_AI_SERVER_API / chat settings"} />
            <Field label="workspace_id" value={status.workspace_id ?? "set VITE_WORKSPACE_ID"} />
            <Field label="user_id" value="set VITE_USER_ID for conversation features" />
            <Field label="local_worker_api" value={localWorkerClient.baseUrl} />
            <Field label="profile_bootstrap_docs" value="docs/en/DEPLOYMENT_PROFILES.md" />
          </div>
          <p className="chat-note">
            Server Docker is the API/backing-services host. Client Worker is the machine running worker_client. Desktop Client controls only the local machine runtime. The deployment bootstrap scripts can generate env files, check dependencies, check ports, and verify health without writing system environment variables.
          </p>
        </section>

        <section className="panel connection-panel">
          <div className="panel-title">
            <Activity size={18} />
            <h2>Release Readiness / Diagnostics</h2>
          </div>
          <div className="field-grid compact">
            <Field label="current_profile" value="client-worker or desktop-client" />
            <Field label="preflight_result" value="python scripts/release_preflight.py --profile server-docker" />
            <Field label="docs_verifier_status" value="python scripts/verify_docs_runtime.py" />
            <Field label="runtime_hygiene_status" value="python scripts/check_runtime_hygiene.py" />
            <Field label="deployment_verification_status" value="python deployment/scripts/verify_environment.py --profile client-worker" />
            <Field label="release_readiness_summary" value="docs/RELEASE_READINESS.md" />
            <Field label="integration_preflight" value="python scripts/integration_preflight.py --profile server-docker" />
            <Field label="integration_strategy" value="docs/INTEGRATION_STATUS.md" />
          </div>
          <p className="chat-note">
            Phase 53 smoke checks are local preflight automation. Phase 54 adds PR chain reconciliation and drift checks. They do not create installers, code signing, auto updater, Kubernetes, or production HA orchestration.
          </p>
        </section>

        <BrowserSessionsPanel />

        <section id="logs-panel" className="panel logs-panel">
          <div className="panel-title logs-title">
            <span>
              <TerminalSquare size={18} />
              <h2>Logs</h2>
            </span>
            <button className="refresh-button" onClick={() => void refresh()}>
              <RefreshCcw size={15} />
              Refresh
            </button>
          </div>
          {error ? (
            <div className="inline-error">
              <AlertTriangle size={16} />
              {error}
            </div>
          ) : null}
          <pre className="log-view">
            {latestLogs.length > 0
              ? latestLogs.map((line, index) => (
                  <span key={`${line}-${index}`} className={isErrorLog(line) ? "log-error" : undefined}>
                    {line}
                    {"\n"}
                  </span>
                ))
              : "No logs available."}
          </pre>
        </section>
      </section>
      </details>
    </main>
  );
}

const rootElement = document.getElementById("root") as HTMLElement & { aiOpsRoot?: Root };
const root = rootElement.aiOpsRoot ?? createRoot(rootElement);
rootElement.aiOpsRoot = root;

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);

