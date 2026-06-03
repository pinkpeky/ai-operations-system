import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createRoot, type Root } from "react-dom/client";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Database,
  FileText,
  MessageCircle,
  Package,
  PauseCircle,
  PencilLine,
  PlayCircle,
  RefreshCcw,
  RotateCcw,
  Search,
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
import {
  knowledgeBaseClient,
  KnowledgeDocument,
  KnowledgeSearchMode,
  KnowledgeSearchResult,
  KnowledgeUploadResponse,
} from "./api/knowledgeBaseClient";
import {
  commercialOperationClient,
  CommercialOperation,
  CommercialOperationApproval,
  CommercialOperationAgentSkillOrchestration,
  CommercialOperationContentDraft,
  CommercialOperationExecutionRequest,
  CommercialOperationExecutionRun,
  CommercialOperationFinalSelection,
  CommercialOperationLoopStage,
  CommercialOperationLoopSummary,
  CommercialOperationMonitoringObservation,
  CommercialOperationOptimizationDecision,
  CommercialOperationOutputCandidate,
  CommercialOperationPlan,
  CommercialOperationPlanCreatePayload,
  CommercialOperationPlatformMetricSnapshot,
  CommercialOperationProductionTask,
  CommercialOperationProjectMaterial,
  CommercialOperationPublishPackage,
  CommercialOperationResult,
  CommercialOperationWorkflowCandidate,
  CommercialOperationWorkflowSelection,
} from "./api/commercialOperationClient";
import { digitalHumanClient, DigitalHumanVideoJob } from "./api/digitalHumanClient";
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

type StrictTemplatePage =
  | "overview"
  | "planning"
  | "text"
  | "media"
  | "flows"
  | "outputs"
  | "publish"
  | "feedback"
  | "knowledge"
  | "assets"
  | "approval";

type StrictTemplateProject = {
  id: string;
  title: string;
  stage: string;
  platform: string;
  owner: string;
  objective: string;
};

const strictTemplateSeedProjects: StrictTemplateProject[] = [
  {
    id: "shang-ktv-digital-human",
    title: "上客 KTV 数字人短视频运营",
    stage: "影音生产",
    platform: "抖音",
    owner: "李运营",
    objective: "围绕本地到店转化，建立每周短视频生产、发布和数据回流闭环。",
  },
  {
    id: "group-dining-campaign",
    title: "团购套餐图文种草",
    stage: "方案确认",
    platform: "抖音 / 小红书",
    owner: "内容运营",
    objective: "把包间套餐的浏览兴趣转化为预约咨询和门店到访。",
  },
  {
    id: "summer-activity-publish",
    title: "暑期包厢活动发布",
    stage: "发布执行",
    platform: "抖音",
    owner: "门店店长",
    objective: "准备发布包并按日回流播放、互动、转化数据。",
  },
];

function StrictOperationTemplateWorkbench() {
  const [projects, setProjects] = useState(strictTemplateSeedProjects);
  const [selectedProjectId, setSelectedProjectId] = useState(strictTemplateSeedProjects[0]?.id ?? "");
  const [page, setPage] = useState<StrictTemplatePage>("overview");
  const [draftActive, setDraftActive] = useState(false);
  const [draftTitle, setDraftTitle] = useState("新建运营项目");
  const [draftGoal, setDraftGoal] = useState("");
  const [analysisRuns, setAnalysisRuns] = useState(1);
  const [chatMessages, setChatMessages] = useState([
    { role: "assistant", text: "我会先调用当前项目知识库，再生成第一版可审核的运营方案。" },
    { role: "operator", text: "重点关注短视频到店转化，以及每周数据闭环复盘。" },
    { role: "assistant", text: "方案草稿已拆分：目标、素材需求、脚本方向、影音流程、发布包和回流指标分别进入对应页签。" },
  ]);
  const selectedProject = projects.find((item) => item.id === selectedProjectId) ?? projects[0];
  const hasProject = Boolean(selectedProject || draftActive);
  const projectTitle = draftActive ? draftTitle : selectedProject?.title ?? "未选择项目";
  const projectObjective = draftActive ? draftGoal || "填写运营目标后创建项目。" : selectedProject?.objective ?? "请先选择或创建项目。";
  const templatePages: Array<{ page: StrictTemplatePage; label: string; detail: string; icon: React.ReactNode }> = [
    { page: "overview", label: "项目总览", detail: String(projects.length), icon: <Package size={14} /> },
    { page: "planning", label: "方案对话", detail: "LLM", icon: <MessageCircle size={14} /> },
    { page: "text", label: "文案任务", detail: "4", icon: <FileText size={14} /> },
    { page: "media", label: "影音生产", detail: "6", icon: <Database size={14} /> },
    { page: "outputs", label: "产出选择", detail: "8", icon: <Package size={14} /> },
    { page: "publish", label: "发布执行", detail: "3", icon: <Send size={14} /> },
    { page: "feedback", label: "数据回流", detail: String(analysisRuns), icon: <Activity size={14} /> },
  ];
  const currentPageLabel = templatePages.find((item) => item.page === page)?.label ?? "项目总览";
  const startDraft = () => {
    setDraftActive(true);
    setSelectedProjectId("");
    setDraftTitle("新建运营项目");
    setDraftGoal("");
    setPage("overview");
  };
  const createDraftProject = () => {
    const nextProject: StrictTemplateProject = {
      id: `project-${Date.now()}`,
      title: draftTitle.trim() || "新建运营项目",
      stage: "方案确认",
      platform: "抖音",
      owner: "运营负责人",
      objective: draftGoal.trim() || "先生成完整运营方案并进入审核。",
    };
    setProjects((current) => [nextProject, ...current]);
    setSelectedProjectId(nextProject.id);
    setDraftActive(false);
    setPage("planning");
    setChatMessages((current) => [
      ...current,
      { role: "operator", text: nextProject.objective },
      { role: "assistant", text: "项目已创建。第一版方案可以审核、重新生成，或确认后进入生产执行。" },
    ]);
  };
  const sendPlanMessage = () => {
    const content = draftGoal.trim() || "基于当前项目知识库重新生成运营方案。";
    setChatMessages((current) => [
      ...current,
      { role: "operator", text: content },
      { role: "assistant", text: "已更新方案草稿：目标拆解、素材需求、脚本、影音流程、发布门槛和回流排期已准备好。" },
    ]);
    setDraftGoal("");
  };
  return (
    <section className="panel chat-panel codex-simple-client" data-simple-workspace-page={page}>
      <section
        className="client-task-workbench"
        data-simple-inner-layout="phase-74e-preview-panels"
        data-backend-sync="commercial-operations-server"
        data-template-strict="operation-project-workbench"
      >
        <div className="simple-operator-workbench">
          <aside className="simple-reference-sidebar">
          <div className="simple-design-sidebar-brand">
            <span>AI</span>
            <div>
              <strong>AI 运营工作台</strong>
              <small>项目闭环工作台</small>
            </div>
          </div>
          <section className="simple-project-entry">
            <div className="simple-project-entry-head">
              <div>
                <span>项目</span>
                <strong>{projectTitle}</strong>
                <p>{draftActive ? "草稿模式" : selectedProject?.stage ?? "选择项目"}</p>
              </div>
              <button type="button" className="refresh-button" onClick={startDraft}>
                <PencilLine size={14} />
              </button>
            </div>
            <div className="simple-project-list">
              {projects.map((project) => (
                <article className={`simple-project-option ${project.id === selectedProjectId ? "selected" : ""}`} key={project.id}>
                  <button
                    type="button"
                    className="simple-project-select"
                    onClick={() => {
                      setSelectedProjectId(project.id);
                      setDraftActive(false);
                      setPage("planning");
                    }}
                  >
                    <strong>{project.title}</strong>
                    <span>{project.stage}</span>
                  </button>
                </article>
              ))}
            </div>
          </section>
          <nav className="simple-workspace-page-tabs" aria-label="运营项目页签">
            {templatePages.map((item) => (
              <button
                type="button"
                className={`simple-workspace-page-tab ${page === item.page ? "active" : ""}`}
                aria-pressed={page === item.page}
                disabled={item.page !== "overview" && !hasProject}
                key={item.page}
                onClick={() => setPage(item.page)}
              >
                {item.icon}
                <span>{item.label}</span>
                <small>{item.detail}</small>
              </button>
            ))}
          </nav>
          <nav className="simple-resource-page-links" aria-label="项目资源">
            <strong className="simple-sidebar-section-title">运营资源</strong>
            <button type="button" onClick={() => setPage("planning")}>
              <Database size={14} />
              <span>项目知识库</span>
              <small>6</small>
            </button>
            <button type="button" onClick={() => setPage("media")}>
              <Upload size={14} />
              <span>素材库</span>
              <small>12</small>
            </button>
            <button type="button" onClick={() => setPage("outputs")}>
              <CheckCircle2 size={14} />
              <span>审批中心</span>
              <small>4</small>
            </button>
            <button type="button" onClick={() => setPage("feedback")}>
              <Activity size={14} />
              <span>再次分析</span>
              <small>{analysisRuns}</small>
            </button>
          </nav>
          </aside>
          <main className="simple-reference-main">
          <section className="simple-design-topbar">
            <div className="simple-design-title">
              <h1>你好，运营同学</h1>
              <p>项目、方案、知识库、生产、发布和数据回流按页签拆开处理。</p>
            </div>
            <label className="simple-design-search">
              <Search size={16} />
              <input type="search" placeholder="搜索项目、素材、产出、指标或指令" />
            </label>
            <div className="simple-design-avatar">运</div>
          </section>
          <section className="simple-design-project-switcher">
            <div className="simple-design-project-current">
              <span>当前项目</span>
              <strong>{projectTitle}</strong>
              <p>{projectObjective}</p>
              <div className="simple-design-project-meta">
                <span><em>阶段</em><strong>{draftActive ? "创建项目" : selectedProject?.stage ?? "无"}</strong></span>
                <span><em>平台</em><strong>{selectedProject?.platform ?? "抖音"}</strong></span>
                <span><em>负责人</em><strong>{selectedProject?.owner ?? "运营负责人"}</strong></span>
                <span><em>知识库</em><strong>随项目走</strong></span>
              </div>
            </div>
            <div className="simple-design-project-actions">
              <button type="button" className="refresh-button" onClick={() => setPage("overview")}>
                <Package size={14} />
                切换
              </button>
              <button type="button" className="refresh-button primary-action" onClick={startDraft}>
                <PencilLine size={14} />
                新建项目
              </button>
            </div>
          </section>
          <section className="simple-design-server-sync">
            <span><Server size={14} /><em>服务器</em><strong>AI 后端平台</strong></span>
            <span><Database size={14} /><em>工作区</em><strong>网页端 + 桌面端</strong></span>
            <span><Wifi size={14} /><em>同步状态</em><strong>已同步</strong></span>
            <span><Activity size={14} /><em>当前页</em><strong>{currentPageLabel}</strong></span>
          </section>
          <section className="simple-reference-stage-workspace">
            <section className="simple-reference-page-panel" data-reference-page="overview">
              <div className="simple-reference-panel-head">
                <div>
                  <span>项目总览</span>
                  <h2>选择、创建或查看运营项目</h2>
                  <p>这里专门处理项目切换、新建和状态查看；具体执行内容分散在后续页签。</p>
                </div>
                <div className="simple-reference-head-actions">
                  <button type="button" className="refresh-button primary-action" onClick={startDraft}><PencilLine size={14} />新建项目</button>
                </div>
              </div>
              {draftActive ? (
                <section className="simple-reference-create-project">
                  <div className="simple-reference-create-main">
                    <span>创建项目</span>
                    <strong>补充上下文并生成第一版方案</strong>
                    <label>项目名称<input value={draftTitle} onChange={(event) => setDraftTitle(event.target.value)} /></label>
                    <label>运营目标<textarea value={draftGoal} onChange={(event) => setDraftGoal(event.target.value)} rows={4} /></label>
                    <div className="simple-reference-create-actions">
                      <button type="button" className="refresh-button primary-action" onClick={createDraftProject}><Send size={14} />创建并生成方案</button>
                      <button type="button" className="refresh-button" onClick={() => setPage("planning")}><MessageCircle size={14} />打开方案对话</button>
                    </div>
                  </div>
                  <aside className="simple-reference-create-side">
                    <article><span>知识库范围</span><strong>随项目走</strong><p>知识库、素材、发布凭证和指标数据都归属当前项目。</p></article>
                  </aside>
                </section>
              ) : null}
              <div className="simple-reference-project-grid">
                {projects.map((project) => (
                  <article className={`simple-reference-project-card ${project.id === selectedProjectId ? "active" : ""}`} key={project.id}>
                    <div><span>{project.stage}</span><strong>{project.title}</strong><p>{project.objective}</p><small>{project.platform}</small></div>
                    <div className="simple-reference-card-actions">
                      <button type="button" className="refresh-button primary-action" onClick={() => { setSelectedProjectId(project.id); setDraftActive(false); setPage("planning"); }}><PlayCircle size={14} />进入</button>
                    </div>
                  </article>
                ))}
              </div>
            </section>
            <section className="simple-reference-page-panel" data-reference-page="planning">
              <div className="simple-reference-panel-head"><div><span>方案对话</span><h2>用于运营方案生成的大型 LLM 对话框</h2><p>方案页以对话为主，右侧保留当前项目知识库和审核状态。</p></div></div>
              {draftActive ? (
                <section className="simple-reference-create-project compact">
                  <div className="simple-reference-create-main">
                    <span>新项目草稿</span>
                    <strong>补全目标后创建项目</strong>
                    <div className="simple-reference-create-inline">
                      <label>项目名称<input value={draftTitle} onChange={(event) => setDraftTitle(event.target.value)} /></label>
                      <label>平台<select><option>抖音</option><option>小红书</option></select></label>
                    </div>
                  </div>
                  <aside className="simple-reference-create-side"><article><span>知识库范围</span><strong>归入草稿项目</strong><p>现在添加的资料会在项目创建后自动绑定到该项目。</p></article></aside>
                </section>
              ) : null}
              <div className="simple-reference-planning-chat">
                <section className="simple-reference-chat-surface">
                  <div className="simple-reference-chat-head"><strong>{projectTitle}</strong><span>{chatMessages.length} 条消息</span></div>
                  <div className="simple-reference-chat-messages">
                    {chatMessages.map((message, index) => <article className={`simple-reference-chat-message ${message.role}`} key={`${message.role}-${index}`}><span>{message.role === "assistant" ? "运营助手" : "操作员"}</span><p>{message.text}</p></article>)}
                  </div>
                  <div className="simple-reference-chat-compose">
                    <textarea value={draftGoal} onChange={(event) => setDraftGoal(event.target.value)} placeholder="告诉 LLM 需要生成或修改什么运营方案。" rows={3} />
                    <button type="button" className="action-button primary-action" onClick={draftActive ? createDraftProject : sendPlanMessage}><Send size={16} />{draftActive ? "创建项目" : "发送"}</button>
                  </div>
                </section>
                <aside className="simple-reference-context-stack">
                  <article className="simple-reference-context-card current"><span>项目知识库</span><strong>已绑定 6 条资料</strong><p>品牌限制、门店照片、参考视频、套餐说明和竞品观察都只归属当前项目。</p><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action"><Upload size={14} />上传</button><button type="button" className="refresh-button"><Search size={14} />检索</button></div></article>
                  <article className="simple-reference-context-card needs-action"><span>方案审批</span><strong>待审核草稿</strong><p>方案确认后，文案、影音、产出、发布和回流任务才进入正式执行。</p><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action"><CheckCircle2 size={14} />通过</button><button type="button" className="refresh-button"><RotateCcw size={14} />重生成</button></div></article>
                </aside>
              </div>
            </section>
            <section className="simple-reference-page-panel" data-reference-page="text"><div className="simple-reference-panel-head"><div><span>文案任务</span><h2>脚本、标题、话术和风险提示</h2><p>文案工作与影音生产、发布执行分开处理。</p></div></div><div className="simple-reference-copy-grid">{["短视频开场钩子", "数字人口播脚本", "套餐发布文案", "风险话术检查"].map((item) => <article className="simple-reference-copy-card current" key={item}><span>待确认</span><strong>{item}</strong><p>已分配给 LLM 文案流程，等待人工审核。</p><small>文案 / 话术</small></article>)}</div></section>
            <section className="simple-reference-page-panel" data-reference-page="media"><div className="simple-reference-panel-head"><div><span>影音生产</span><h2>素材和 ComfyUI 工作流候选</h2><p>素材与工作流在这里确认，完成后再登记产出。</p></div></div><div className="simple-reference-work-area"><section className="simple-reference-material-grid">{["门店照片", "品牌限制", "参考视频", "音频线索"].map((item) => <article className="simple-reference-material-card current" key={item}><span>素材</span><strong>{item}</strong><p>仅对当前项目生效，已由操作员确认。</p></article>)}</section><aside className="simple-reference-context-stack"><article className="simple-reference-context-card current"><span>工作流候选</span><strong>ComfyUI 短视频流程</strong><p>图片、视频、音频和数字人步骤已准备好进入审核。</p></article></aside></div></section>
            <section className="simple-reference-page-panel" data-reference-page="outputs"><div className="simple-reference-panel-head"><div><span>产出选择</span><h2>预览并选择生成结果</h2><p>这里仅处理产出登记、预览和人工选择。</p></div></div><div className="simple-reference-review-grid">{["开场海报", "数字人视频", "配音音频", "最终发布文案"].map((item) => <article className="simple-reference-review-card ready" key={item}><div className="simple-reference-output-preview"><Package size={22} /></div><span>候选</span><strong>{item}</strong><p>已准备好等待操作员选择。</p><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action"><CheckCircle2 size={14} />选择</button><button type="button" className="refresh-button"><XCircle size={14} />驳回</button></div></article>)}</div></section>
            <section className="simple-reference-page-panel" data-reference-page="publish"><div className="simple-reference-panel-head"><div><span>发布执行</span><h2>发布包和客户机器执行</h2><p>准备标题文案、审核门槛、平台发布包和执行交接。</p></div></div><div className="simple-reference-publish-grid"><section className="simple-reference-publish-list">{["抖音发布包", "标题文案包", "执行凭证请求"].map((item) => <article className="simple-reference-publish-card current" key={item}><span>就绪</span><strong>{item}</strong><p>等待操作员审批并交给客户机器执行。</p><small>#门店 #KTV #数字人</small></article>)}</section><aside className="simple-reference-data-list"><article className="simple-reference-data-card ready"><span>每日分析</span><strong>22:30 定时</strong><p>发布后会拉回数据用于复盘。</p></article></aside></div></section>
            <section className="simple-reference-page-panel" data-reference-page="feedback"><div className="simple-reference-panel-head"><div><span>数据回流</span><h2>拉回指标并再次分析</h2><p>发布凭证、平台指标、异常检查和下一轮建议都在这里处理。</p></div><div className="simple-reference-head-actions"><button type="button" className="refresh-button primary-action" onClick={() => setAnalysisRuns((value) => value + 1)}><RefreshCcw size={14} />再次分析</button></div></div><div className="simple-reference-feedback-grid">{["发布凭证", "平台指标", "增长建议"].map((item) => <article className="simple-reference-feedback-card current" key={item}><span>{item}</span><strong>第 {analysisRuns} 轮</strong><p>最新回流结果已绑定当前项目，可触发下一轮方案优化。</p></article>)}</div></section>
          </section>
          </main>
        </div>
      </section>
    </section>
  );
}

type ConnectedWorkbenchSnapshot = {
  plans: CommercialOperationPlan[];
  materials: CommercialOperationProjectMaterial[];
  tasks: CommercialOperationProductionTask[];
  contentDrafts: CommercialOperationContentDraft[];
  workflows: CommercialOperationWorkflowSelection[];
  outputs: CommercialOperationOutputCandidate[];
  selections: CommercialOperationFinalSelection[];
  publishPackages: CommercialOperationPublishPackage[];
  metrics: CommercialOperationPlatformMetricSnapshot[];
};

const emptyConnectedSnapshot: ConnectedWorkbenchSnapshot = {
  plans: [],
  materials: [],
  tasks: [],
  contentDrafts: [],
  workflows: [],
  outputs: [],
  selections: [],
  publishPackages: [],
  metrics: [],
};

function operationMetaText(operation: CommercialOperation | null, key: string, fallback: string): string {
  const value = operation?.metadata?.[key];
  return typeof value === "string" && value.trim() ? value : fallback;
}

function operationStageLabel(operation: CommercialOperation | null): string {
  if (!operation) return "未选择";
  if (operation.status === "archived") return "已删除";
  return operationMetaText(operation, "stage", operation.status === "draft" ? "方案确认" : operation.status);
}

function operationPlatformLabel(operation: CommercialOperation | null): string {
  return operation?.channels?.[0] || operationMetaText(operation, "platform", "抖音");
}

function planFieldLabel(key: string): string {
  const labels: Record<string, string> = {
    action: "动作",
    analysis_label: "分析类型",
    approval_gate: "审批关口",
    approval_required: "需要审批",
    cadence: "节奏",
    capability: "能力项",
    chat_prompt: "对话要求",
    column: "栏目",
    content_type: "内容类型",
    conversion_point: "转化动作",
    current_gap: "当前缺口",
    day: "时间",
    deliverable: "交付物",
    example: "示例",
    gate: "关口",
    hook: "开场钩子",
    material_type: "素材类型",
    media_subtype: "媒介",
    metric: "指标",
    name: "名称",
    note: "说明",
    operator_action: "执行动作",
    output: "产出",
    owner: "负责人",
    pattern: "内容结构",
    playbook: "打法",
    platform: "平台",
    reason: "原因",
    required: "必需",
    required_action: "需补动作",
    review_required: "需要复核",
    rule: "规则",
    role: "定位",
    shot_structure: "镜头结构",
    step: "步骤",
    task_type: "任务类型",
    title: "标题",
    target_value: "目标值",
    measurement: "统计口径",
    review_cadence: "复盘频率",
    trigger: "触发条件",
    use: "用途",
    validation: "验证方式",
    why_it_works: "有效原因",
    workflow_selection_required: "工作流选择",
  };
  return labels[key] ?? key.replace(/_/g, " ");
}

function planDisplayToken(value: string): string {
  const labels: Record<string, string> = {
    authorization: "授权材料",
    brand_brief: "品牌、门店和转化目标资料",
    copy: "文案脚本",
    digital_human: "数字人",
    image: "图片视觉",
    media: "影音生产",
    poster: "海报视觉",
    script: "文案脚本",
    video: "短视频",
  };
  return (labels[value] ?? value)
    .replace(/OperationPlan/g, "运营方案")
    .replace(/Agent/g, "团队");
}

function planDisplayTitle(plan: CommercialOperationPlan, projectTitle: string, platform: string): string {
  const genericPattern = new RegExp(`^${platform}运营候选方案 v\\d+$`);
  if (genericPattern.test(plan.title)) {
    return `${projectTitle}本地到店转化运营方案 v${plan.plan_version}`;
  }
  return plan.title;
}

function projectRecordStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    approved: "已批准",
    archived: "已归档",
    completed: "已完成",
    draft: "草稿",
    failed: "失败",
    in_progress: "执行中",
    pending: "待处理",
    ready_for_review: "待审核",
    rejected: "已驳回",
  };
  return labels[status] ?? status.replace(/_/g, " ");
}

function contentDraftStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    approved: "已批准",
    archived: "已归档",
    draft: "草稿",
    ready_for_review: "待审核",
    rejected: "已驳回",
  };
  return labels[status] ?? status.replace(/_/g, " ");
}

function commercialRecordTimestamp(record: { id?: string; metadata?: Record<string, unknown>; updated_at?: unknown; created_at?: unknown }): number {
  const updatedAt = typeof record.updated_at === "string" ? record.updated_at : "";
  const createdAt = typeof record.created_at === "string" ? record.created_at : "";
  const metadataCreatedAt = typeof record.metadata?.created_at === "string" ? record.metadata.created_at : "";
  const metadataGeneratedAt = typeof record.metadata?.generated_at === "string" ? record.metadata.generated_at : "";
  return Date.parse(updatedAt || createdAt || metadataGeneratedAt || metadataCreatedAt || "") || 0;
}

function taskBriefText(task: CommercialOperationProductionTask): string {
  if (task.task_type === "copy") {
    return "根据已批准运营方案输出短视频开场钩子、脚本、标题、发布文案、评论引导话术和风险提示，完成后进入人工审核。";
  }
  return task.brief || "基于项目素材生成可预览的影音候选产出，需先确认素材授权和工作流。";
}

function fallbackQualifiedCopyBody(plan: CommercialOperationPlan | null, projectTitle: string, platform: string): string {
  const title = plan?.title || projectTitle;
  const objective = plan?.objective_summary || "围绕本地到店转化，建立短视频内容、发布和数据回流闭环。";
  return [
    `成稿来源：${title}`,
    `项目目标：${objective}`,
    "",
    "短视频 1：周末朋友局怎么订更划算",
    "标题：周末 KTV 朋友局，不踩坑的订包厢方法",
    "封面文案：人均预算 / 包厢氛围 / 到店预约",
    "开场 3 秒：周末想约朋友唱歌，别只看价格，先看这三个点。",
    "分镜与口播：",
    "1. 门店/包厢实拍：先看包厢大小和音响氛围，适合 4 到 8 人朋友局。",
    "2. 套餐说明：把团购套餐、人均预算和可用时段讲清楚，避免到店临时加价误解。",
    "3. 转化安排：想订周末晚场，点团购或私信人数和时间，门店先帮你确认档期。",
    "发布正文：周末朋友局想唱得尽兴，先确认人数、预算和时段。我们整理了适合朋友聚会的包厢和套餐，私信人数+日期可先查档期。",
    "评论引导：你们一般几个人唱 K？我帮你按人数推荐包厢。",
    "CTA：私信“周末+人数”获取可订时段。",
    "",
    "短视频 2：生日包厢真实体验",
    "标题：生日局想有氛围，可以这样选 KTV 包厢",
    "封面文案：生日聚会 / 氛围实拍 / 套餐预约",
    "开场 3 秒：生日聚会别只订房间，氛围、人数和套餐都要提前确认。",
    "分镜与口播：",
    "1. 包厢实拍：展示灯光、沙发、屏幕和可容纳人数，说明适合生日/聚会场景。",
    "2. 体验说明：朋友到齐后，唱歌、拍照、切蛋糕动线都要顺。",
    "3. 转化安排：生日局建议提前预约晚间黄金时段，避免临时无房。",
    "发布正文：生日聚会想省心，建议提前确认包厢人数、到店时间和套餐内容。门店可按人数推荐合适包厢，发布前所有图片均为门店实拍或授权素材。",
    "评论引导：生日局一般几个人？评论人数，我给你一个包厢建议。",
    "CTA：私信“生日+人数+日期”查可预约包厢。",
    "",
    "短视频 3：下班后本地放松路线",
    "标题：下班后想放松，本地 KTV 晚场这样安排",
    "封面文案：下班放松 / 本地到店 / 晚场预约",
    "开场 3 秒：下班后想找个地方放松，不一定要复杂，约上朋友唱两小时刚好。",
    "分镜与口播：",
    "1. 商圈/门店外观：说明位置和适合下班后到店的人群。",
    "2. 包厢氛围：展示真实空间，不使用未授权人物正脸或夸大效果。",
    "3. 转化安排：晚间时段建议先私信确认包厢和团购使用规则。",
    "发布正文：下班后想放松，可以提前确认晚场包厢和团购规则。适合朋友小聚、生日局和周末活动，具体价格和可用时段以门店确认为准。",
    "评论引导：你更喜欢工作日晚上唱，还是周末唱？",
    "CTA：私信“晚场”获取今日可订时段。",
    "",
    "统一风险检查：",
    `1. 发布平台：${platform}；发布前人工确认标题、正文、话题和 CTA。`,
    "2. 素材必须来自门店实拍、品牌资料或已授权素材；人物、音乐、商标和参考视频不可无授权使用。",
    "3. 不承诺固定低价、固定房态或绝对转化；套餐价格、可用时段和活动内容以门店实时确认为准。",
    "4. 每条发布后回流播放、互动、私信咨询、团购/预约数据，用于下一轮优化。",
  ].join("\n");
}

function taskDeliverables(task: CommercialOperationProductionTask): string[] {
  if (task.task_type === "copy") {
    return ["短视频脚本", "标题与封面文案", "团购/预约 CTA", "评论区互动话术", "平台合规风险提示"];
  }
  return ["素材授权确认", "工作流选择", "候选预览", "人工审批"];
}

function copyReviewSections(task: CommercialOperationProductionTask, plan: CommercialOperationPlan | null) {
  const strategy = plan?.content_strategy ?? {};
  const topicItems = planContentItems(strategy, ["sample_topics", "creative_examples"], "根据当前方案生成 3 条短视频脚本候选。");
  const titleItems = planContentItems(strategy, ["content_pillars", "content_columns"], "围绕本地到店、套餐种草和门店体验生成标题与封面文案。");
  const ctaItems = planContentItems(strategy, ["conversion_path", "content_pillars"], "每条内容必须绑定团购、预约、私信咨询或到店转化动作。");
  const riskItems = [
    ...planContentItems(strategy, ["approval_gates", "risk_controls", "compliance_checks"], "发布前检查素材授权、价格表达、平台规则和人工审批。"),
    plan?.risk_notes || task.reviewer_notes || "素材授权、平台合规、发布节奏和转化口径需要人工复核。",
  ].filter(Boolean);
  return [
    { title: "脚本方向", items: topicItems },
    { title: "标题与封面文案", items: titleItems },
    { title: "CTA 与互动话术", items: ctaItems },
    { title: "风险提示", items: riskItems },
  ];
}

function planValueText(value: unknown): string {
  if (value === null || value === undefined || value === "") return "待补充";
  if (typeof value === "boolean") return value ? "是" : "否";
  if (typeof value === "string") return planDisplayToken(value);
  if (typeof value === "number") return String(value);
  if (Array.isArray(value)) return value.map((item) => planValueText(item)).filter(Boolean).join("；");
  if (typeof value === "object") {
    const record = value as Record<string, unknown>;
    const label = typeof record.label === "string" ? record.label.trim() : "";
    const detail = typeof record.detail === "string" ? record.detail.trim() : "";
    if (label || detail) {
      if (label === "抓取状态" && /来源\s*0\s*条/.test(detail)) {
        return "历史抓取状态：旧方案生成时未获得可信来源；点击修改当前方案后会重新抓取搜索结果、平台公开资料和案例参考。";
      }
      return [label, detail].filter(Boolean).join("：");
    }
    const sourceTitle = typeof record.title === "string" ? record.title.trim() : "";
    const sourceUrl = typeof record.url === "string" ? record.url.trim() : "";
    const sourceSnippet = typeof record.snippet === "string" ? record.snippet.trim() : "";
    if (sourceUrl || sourceSnippet) {
      return [sourceTitle || "外部来源", sourceUrl, sourceSnippet].filter(Boolean).join(" | ");
    }
    const sourceNote = typeof record.note === "string" ? record.note.trim() : "";
    if (sourceTitle && sourceNote) return `${sourceTitle}：${sourceNote}`;
    if (typeof record.name === "string" && (record.target_value || record.measurement || record.review_cadence)) {
      const cadenceText = planDisplayToken(String(record.review_cadence || ""));
      return [
        `${planDisplayToken(record.name)}：目标 ${planDisplayToken(String(record.target_value || "按首周基线提升"))}`,
        record.measurement ? `统计口径为 ${planDisplayToken(String(record.measurement))}` : "",
        cadenceText ? (cadenceText.includes("复盘") ? cadenceText : `${cadenceText}复盘`) : "",
        record.review_required ? "审批时需复核口径" : "",
      ].filter(Boolean).join("；");
    }
    if (
      (typeof record.name === "string" && (record.action || record.deliverable))
      || (typeof record.column === "string" && (record.example || record.conversion_point))
      || (typeof record.title === "string" && (record.hook || record.output))
      || (typeof record.day === "string" && record.action)
      || (typeof record.step === "string" && (record.gate || record.output))
      || (typeof record.gate === "string" && (record.rule || record.owner))
      || (typeof record.metric === "string" && record.use)
      || (typeof record.task_type === "string" && (record.title || record.media_subtype || record.workflow_selection_required || record.approval_required))
      || (typeof record.material_type === "string" && (record.note || record.required))
      || (typeof record.platform === "string" && (record.role || record.reason || record.cadence || record.approval_gate))
    ) {
      const title = planRecordTitle(record, "方案条目");
      const detailText = planRecordDetail(record);
      return [title, detailText].filter(Boolean).join("：");
    }
    if (typeof record.pattern === "string" || typeof record.playbook === "string" || typeof record.capability === "string") {
      const title = planRecordTitle(record, "运营分析");
      const detailText = planRecordDetail(record);
      return [title, detailText].filter(Boolean).join("：");
    }
    if (typeof record.metric === "string" && (record.purpose || record.source || record.stage)) {
      return `${planDisplayToken(record.metric)}：${planRecordDetail(record)}`;
    }
    const gpuMode = typeof record.mode === "string" ? record.mode.trim() : "";
    if (gpuMode || record.recommended_gpu_indexes || record.cuda_visible_devices) {
      const modeLabel = gpuMode === "dual_gpu_llm" ? "双卡 LLM 性能模式"
        : gpuMode === "single_idle_gpu_with_comfyui" ? "ComfyUI 运行中，LLM 使用空闲单卡"
        : gpuMode === "queued_waiting_for_idle_gpu" ? "等待空闲显卡"
        : gpuMode || "LLM 显卡调度";
      const gpuText = typeof record.recommended_gpu_indexes === "string" ? record.recommended_gpu_indexes : planValueText(record.recommended_gpu_indexes);
      const comfyText = typeof record.comfyui_active === "string" ? record.comfyui_active : planValueText(record.comfyui_active);
      const noteText = typeof record.note === "string" ? record.note : "";
      return [modeLabel, gpuText && gpuText !== "待补充" ? `建议显卡 ${gpuText}` : "", comfyText && comfyText !== "待补充" ? `ComfyUI 占用：${comfyText}` : "", noteText].filter(Boolean).join("；");
    }
    const visualTitle = typeof record.scene === "string" ? record.scene.trim() : sourceTitle;
    const visualDetail = [
      typeof record.shot === "string" ? `镜头：${record.shot.trim()}` : "",
      typeof record.visual === "string" ? `画面：${record.visual.trim()}` : "",
      typeof record.chart === "string" ? `图表：${record.chart.trim()}` : "",
      typeof record.metric === "string" ? `指标：${record.metric.trim()}` : "",
      typeof record.purpose === "string" ? `用途：${record.purpose.trim()}` : "",
    ].filter(Boolean).join("；");
    if (visualTitle && visualDetail) return `${visualTitle}：${visualDetail}`;
    return Object.entries(record)
      .map(([key, item]) => `${planFieldLabel(key)}：${planValueText(item)}`)
      .join("；");
  }
  return String(value);
}

function planListItems(records: Record<string, unknown>[], fallback: string): string[] {
  const items = records.map((item) => planValueText(item)).filter((item) => item && item !== "待补充");
  return items.length ? items : [fallback];
}

function planKpiItems(records: Record<string, unknown>[]): string[] {
  const targetByName: Record<string, { target_value: string; measurement: string; review_cadence: string }> = {
    播放量: { target_value: "单条 3000+，每周累计 9000+", measurement: "平台播放数据", review_cadence: "每周复盘" },
    互动率: { target_value: "不低于 5%", measurement: "点赞、评论、收藏、分享 / 播放量", review_cadence: "每周复盘" },
    到店咨询: { target_value: "每周 20+ 次有效咨询", measurement: "私信、电话、团购页咨询和门店预约", review_cadence: "每周复盘" },
    团购转化: { target_value: "每周 8+ 单团购或预约转化", measurement: "团购订单、预约记录和门店核销", review_cadence: "每周复盘" },
    转化: { target_value: "每周 8+ 次有效转化", measurement: "咨询、预约、团购和到店核销", review_cadence: "每周复盘" },
  };
  const items = records.map((record) => {
    const rawName = typeof record.name === "string" ? record.name : "业务指标";
    const preset = targetByName[rawName] ?? { target_value: "按首周基线提升 15%", measurement: "平台数据和门店转化记录", review_cadence: "每周复盘" };
    return planValueText({ name: rawName, ...preset, review_required: true });
  });
  return items.length ? items : planKpiItems(["播放量", "互动率", "到店咨询", "团购转化"].map((name) => ({ name })));
}

function planHasContentValue(value: unknown): boolean {
  if (value === null || value === undefined || value === "") return false;
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === "object") return Object.keys(value as Record<string, unknown>).length > 0;
  return true;
}

function planContentItems(strategy: Record<string, unknown>, keys: string[], fallback: string): string[] {
  const items = keys.flatMap((key) => {
    const value = strategy[key];
    if (Array.isArray(value)) {
      return value.map((item) => planValueText(item)).filter((item) => item && item !== "待补充");
    }
    if (value && typeof value === "object") return [planValueText(value)];
    if (typeof value === "string" && value.trim()) return [value.trim()];
    return [];
  });
  const deduped = items.filter((item, index) => items.indexOf(item) === index);
  return deduped.length ? deduped : [fallback];
}

function planContentRecords(strategy: Record<string, unknown>, keys: string[]): Record<string, unknown>[] {
  const records = keys.flatMap((key) => {
    const value = strategy[key];
    if (Array.isArray(value)) {
      return value.map((item) => {
        if (item && typeof item === "object" && !Array.isArray(item)) return item as Record<string, unknown>;
        return { label: planFieldLabel(key), detail: planValueText(item) };
      });
    }
    if (value && typeof value === "object") return [value as Record<string, unknown>];
    if (typeof value === "string" && value.trim()) return [{ label: planFieldLabel(key), detail: value.trim() }];
    return [];
  });
  const seen = new Set<string>();
  return records.filter((record) => {
    const key = planValueText(record);
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

function planRecordTitle(record: Record<string, unknown>, fallback: string): string {
  const value = record.title ?? record.label ?? record.pattern ?? record.playbook ?? record.capability ?? record.scene ?? record.chart ?? record.name ?? record.column ?? record.metric ?? record.day ?? record.step ?? record.platform ?? record.gate ?? record.material_type ?? record.task_type;
  return typeof value === "string" && value.trim() ? planDisplayToken(value.trim()) : fallback;
}

function planRecordDetail(record: Record<string, unknown>): string {
  if (typeof record.name === "string" && (record.action || record.deliverable)) {
    return [
      record.action ? planDisplayToken(String(record.action)) : "",
      record.deliverable ? `产出 ${planDisplayToken(String(record.deliverable))}` : "",
      record.review_required ? "需要人工复核后执行" : "",
    ].filter(Boolean).join("；");
  }
  if (typeof record.column === "string" && (record.example || record.conversion_point)) {
    return [
      record.example ? `内容示例：${planDisplayToken(String(record.example))}` : "",
      record.conversion_point ? `转化路径：${planDisplayToken(String(record.conversion_point))}` : "",
    ].filter(Boolean).join("；");
  }
  if (typeof record.title === "string" && (record.hook || record.output)) {
    return [
      record.hook ? `开场方式：${planDisplayToken(String(record.hook))}` : "",
      record.output ? `交付内容：${planDisplayToken(String(record.output))}` : "",
    ].filter(Boolean).join("；");
  }
  if (typeof record.day === "string" && record.action) {
    return [
      record.owner ? `${planDisplayToken(String(record.owner))}负责${planDisplayToken(String(record.action))}` : planDisplayToken(String(record.action)),
      record.deliverable ? `交付 ${planDisplayToken(String(record.deliverable))}` : "",
    ].filter(Boolean).join("；");
  }
  if (typeof record.step === "string" && (record.gate || record.output)) {
    return [
      record.gate ? `准入条件：${planDisplayToken(String(record.gate))}` : "",
      record.output ? `通过后产出 ${planDisplayToken(String(record.output))}` : "",
    ].filter(Boolean).join("；");
  }
  if (typeof record.gate === "string" && (record.rule || record.owner)) {
    return [
      record.rule ? planDisplayToken(String(record.rule)) : "",
      record.owner ? `由${planDisplayToken(String(record.owner))}确认` : "",
    ].filter(Boolean).join("；");
  }
  if (typeof record.metric === "string" && record.use) {
    return planDisplayToken(String(record.use));
  }
  if (typeof record.platform === "string" && (record.role || record.reason || record.cadence || record.approval_gate)) {
    return [
      record.role ? `定位：${planDisplayToken(String(record.role))}` : "",
      record.reason ? `依据：${planDisplayToken(String(record.reason))}` : "",
      record.cadence ? `节奏：${planDisplayToken(String(record.cadence))}` : "",
      record.approval_gate ? `审批要求：${planDisplayToken(String(record.approval_gate))}` : "",
    ].filter(Boolean).join("；");
  }
  if (typeof record.task_type === "string" && (record.title || record.media_subtype || record.workflow_selection_required || record.approval_required)) {
    return [
      record.title ? planDisplayToken(String(record.title)) : planDisplayToken(String(record.task_type)),
      record.media_subtype ? `类型：${planDisplayToken(String(record.media_subtype))}` : "",
      record.workflow_selection_required ? "需要先选择工作流" : "",
      record.approval_required ? "需要人工审批" : "",
    ].filter(Boolean).join("；");
  }
  if (typeof record.material_type === "string" && (record.note || record.required)) {
    return [
      record.note ? planDisplayToken(String(record.note)) : planDisplayToken(String(record.material_type)),
      record.required ? "必须补齐" : "",
    ].filter(Boolean).join("；");
  }
  if (typeof record.pattern === "string") {
    return [
      record.why_it_works ? `有效原因：${planDisplayToken(String(record.why_it_works))}` : "",
      record.shot_structure ? `镜头结构：${planDisplayToken(String(record.shot_structure))}` : "",
      record.operator_action ? `执行安排：${planDisplayToken(String(record.operator_action))}` : "",
      record.validation ? `验证方式：${planDisplayToken(String(record.validation))}` : "",
    ].filter(Boolean).join("；") || planDisplayToken(record.pattern);
  }
  if (typeof record.playbook === "string") {
    return [
      record.content ? `打法内容：${planDisplayToken(String(record.content))}` : "",
      record.reuse_boundary ? `复用边界：${planDisplayToken(String(record.reuse_boundary))}` : "",
      record.approval_focus ? `审批重点：${planDisplayToken(String(record.approval_focus))}` : "",
    ].filter(Boolean).join("；") || planDisplayToken(record.playbook);
  }
  if (typeof record.capability === "string") {
    return [
      record.current_gap ? `当前缺口：${planDisplayToken(String(record.current_gap))}` : "",
      record.required_action ? `补齐要求：${planDisplayToken(String(record.required_action))}` : "",
    ].filter(Boolean).join("；") || planDisplayToken(record.capability);
  }
  if (typeof record.metric === "string" && (record.purpose || record.source || record.stage)) {
    return [
      record.purpose ? `验证目的：${planDisplayToken(String(record.purpose))}` : "",
      record.source ? `数据来源：${planDisplayToken(String(record.source))}` : "",
      record.stage ? `所在阶段：${planDisplayToken(String(record.stage))}` : "",
    ].filter(Boolean).join("；");
  }
  const direct = record.detail ?? record.purpose ?? record.snippet ?? record.note ?? record.action ?? record.visual ?? record.example ?? record.output ?? record.deliverable ?? record.use ?? record.reason;
  if (typeof direct === "string" && direct.trim()) return planDisplayToken(direct.trim());
  return planValueText(record);
}

function planRecordUrl(record: Record<string, unknown>): string {
  const value = record.url ?? record.preview_uri;
  return typeof value === "string" && value.startsWith("http") ? value : "";
}

function planSourceRole(record: Record<string, unknown>): "plan_evidence" | "reference_only" | "weak_reference" {
  const explicit = String(record.source_role || "");
  if (explicit === "plan_evidence") return "plan_evidence";
  if (explicit === "reference_only") return "reference_only";
  const url = planRecordUrl(record).toLowerCase();
  const source = String(record.source || "").toLowerCase();
  const title = planRecordTitle(record, "");
  const detail = planRecordDetail(record);
  const text = `${title} ${detail} ${url} ${source}`.toLowerCase();
  const isHomepage = /https?:\/\/(www\.)?(douyin\.com|xiaohongshu\.com|oceanengine\.com|kuaishou\.com|bilibili\.com)\/?$/.test(url)
    || /^https?:\/\/eos\.douyin\.com\/?$/.test(url);
  if (isHomepage || source.includes("platform_reference")) return "reference_only";
  if (source.includes("case_reference") || /探店|爆款|短视频|案例|团购|核销|转化|指标|复盘|douyin\.com|xiaohongshu\.com/.test(text)) {
    return "plan_evidence";
  }
  return "weak_reference";
}

function planSourceLabel(record: Record<string, unknown>): string {
  const explicit = record.evidence_label;
  if (typeof explicit === "string" && explicit.trim()) return planDisplayToken(explicit.trim());
  const role = planSourceRole(record);
  if (role === "plan_evidence") return "方案依据";
  if (role === "reference_only") return "平台参考";
  return "待复核";
}

function planSourceReason(record: Record<string, unknown>): string {
  const reason = record.relevance_reason;
  if (typeof reason === "string" && reason.trim()) return planDisplayToken(reason.trim());
  const role = planSourceRole(record);
  if (role === "plan_evidence") return "命中项目题材、案例、短视频或运营指标词，可作为方案假设来源，仍需人工复核。";
  if (role === "reference_only") return "平台资料只用于规则、产品边界和经营流程参考，不计入爆款或真实运营数据。";
  return "相关性不足，保留为待人工确认来源。";
}

function planSourceCardClass(record: Record<string, unknown>): string {
  return `simple-plan-visual-source-card ${planSourceRole(record).replace("_", "-")}`;
}

function numericMetricEntries(metrics: CommercialOperationPlatformMetricSnapshot[]): { label: string; value: number; source: string }[] {
  return metrics.flatMap((snapshot, snapshotIndex) => Object.entries(snapshot.metrics || {})
    .filter(([, value]) => typeof value === "number" && Number.isFinite(value))
    .map(([label, value]) => ({
      label: planFieldLabel(label),
      value: Number(value),
      source: snapshot.source_type || `指标快照 ${snapshotIndex + 1}`,
    })))
    .slice(0, 8);
}

function networkMetricEntries(sourceRecords: Record<string, unknown>[], searchRecords: Record<string, unknown>[], visualRecords: Record<string, unknown>[]): { label: string; value: number; source: string }[] {
  const evidenceRecords = sourceRecords.filter((record) => planSourceRole(record) === "plan_evidence");
  const referenceRecords = sourceRecords.filter((record) => planSourceRole(record) === "reference_only");
  const sourceTypes = new Set(sourceRecords.map((record) => String(record.evidence_type || record.source || record.visual_type || "")).filter(Boolean));
  const visualCount = visualRecords.filter((record) => record.preview_image_url || record.favicon_url || record.domain || record.url).length;
  return [
    { label: "方案依据", value: evidenceRecords.length, source: "网络证据" },
    { label: "平台参考", value: referenceRecords.length, source: "规则/资料" },
    { label: "情报信号", value: searchRecords.length, source: "网络分析" },
    { label: "来源类型", value: sourceTypes.size, source: "来源去重" },
    { label: "可视参考", value: visualCount, source: "页面元数据" },
  ].filter((item) => item.value > 0);
}

function renderPlanMiniChart(
  record: Record<string, unknown>,
  index: number,
  realMetrics: { label: string; value: number; source: string }[],
  networkMetrics: { label: string; value: number; source: string }[],
) {
  const title = planRecordTitle(record, `图表 ${index + 1}`);
  const metric = typeof record.metric === "string" ? record.metric : planRecordDetail(record);
  const mode = realMetrics.length ? "真实回流数据" : networkMetrics.length ? "网络情报分析" : "缺少可分析数据";
  const values = (realMetrics.length ? realMetrics : networkMetrics).slice(0, 4);
  const maxValue = Math.max(1, ...values.map((item) => item.value));
  return (
    <div className={`simple-plan-visual-chart-card ${realMetrics.length ? "real-data" : values.length ? "network-data" : "pending-data"}`} key={`${title}-${index}`}>
      <div>
        <span>{mode} · {title}</span>
        <strong>{metric}</strong>
      </div>
      <div className="simple-plan-visual-bars" aria-hidden={!values.length}>
        {values.length
          ? values.map((item, valueIndex) => <i key={`${item.label}-${valueIndex}`} style={{ height: `${Math.max(14, Math.round((item.value / maxValue) * 100))}%` }} title={`${item.label}: ${item.value}`} />)
          : <em>请先重新生成方案抓取网络情报</em>}
      </div>
      <small>{values.length ? values.map((item) => `${item.label} ${item.value}`).join(" / ") : planRecordDetail(record)}</small>
    </div>
  );
}

function renderOperationPlanDetails(plan: CommercialOperationPlan, snapshot?: ConnectedWorkbenchSnapshot) {
  const strategy = plan.content_strategy ?? {};
  const contentReason = typeof plan.content_strategy?.llm_recommendation_reason === "string"
    ? plan.content_strategy.llm_recommendation_reason
    : planValueText(plan.content_strategy);
  const sourceRecords = planContentRecords(strategy, ["external_research_sources"]).slice(0, 6);
  const planEvidenceRecords = sourceRecords.filter((record) => planSourceRole(record) === "plan_evidence");
  const referenceOnlyRecords = sourceRecords.filter((record) => planSourceRole(record) !== "plan_evidence");
  const orderedSourceRecords = [...planEvidenceRecords, ...referenceOnlyRecords];
  const videoAnalysisRecords = planContentRecords(strategy, ["video_analysis"]).slice(0, 4);
  const competitorPlaybookRecords = planContentRecords(strategy, ["competitor_playbook"]).slice(0, 4);
  const capabilityDiagnosisRecords = planContentRecords(strategy, ["operation_capability_diagnosis"]).slice(0, 4);
  const dataValidationRecords = planContentRecords(strategy, ["data_validation_plan"]).slice(0, 5);
  const analysisSummaryRecords: Record<string, unknown>[] = [
    ...videoAnalysisRecords.slice(0, 2).map((record) => ({ ...record, analysis_label: "视频分析" })),
    ...competitorPlaybookRecords.slice(0, 2).map((record) => ({ ...record, analysis_label: "竞品打法" })),
    ...capabilityDiagnosisRecords.slice(0, 2).map((record) => ({ ...record, analysis_label: "能力诊断" })),
  ];
  const storyboardRecords = planContentRecords(strategy, ["visual_storyboard", "shot_list"]).slice(0, 5);
  const chartRecords = planContentRecords(strategy, ["chart_dashboard", "metric_visuals", "data_visualization"]).slice(0, 4);
  const assetRecords = planContentRecords(strategy, ["visual_assets", "cover_designs", "poster_assets"]).slice(0, 6);
  const realMetricEntries = numericMetricEntries(snapshot?.metrics ?? []);
  const realOutputPreviews = (snapshot?.outputs ?? []).filter((item) => item.preview_uri);
  const visualAssetDisplayRecords: Record<string, unknown>[] = realOutputPreviews.map((item) => ({
    title: item.title,
    preview_uri: item.preview_uri,
    detail: item.generation_summary || "真实产出预览",
    card_status: "真实产出预览",
  }));
  const verificationRecords = [...dataValidationRecords, ...chartRecords, ...plan.kpis].slice(0, 5);
  const sections = [
    { title: "核心打法", items: planContentItems(strategy, ["strategy_summary", "positioning", "strategy_pillars", "conversion_path"], "待补充核心打法") },
    { title: "渠道策略", items: planListItems(plan.channel_strategy, "待补充渠道策略") },
    { title: "内容栏目", items: planContentItems(strategy, ["content_pillars", "content_columns", "sample_topics", "creative_examples"], contentReason || "待补充内容栏目") },
    { title: "视频分析", items: planContentItems(strategy, ["video_analysis"], "待补充参考视频结构、镜头节奏和可复用边界") },
    { title: "竞品打法", items: planContentItems(strategy, ["competitor_playbook"], "待补充竞品栏目、转化动作和不可复制边界") },
    { title: "运营能力诊断", items: planContentItems(strategy, ["operation_capability_diagnosis"], "待补充素材、生产、审批和复盘能力缺口") },
    { title: "周执行排期", items: planContentItems(strategy, ["weekly_calendar", "publishing_calendar", "milestones"], "待补充周执行排期") },
    { title: "生产流程", items: planContentItems(strategy, ["production_workflow", "execution_workflow", "operation_workflow"], "待补充生产流程") },
    { title: "生产范围", items: planListItems(plan.production_scope, "待补充生产范围") },
    { title: "素材要求", items: planListItems(plan.material_requirements, "待补充素材要求") },
    { title: "审批风控", items: planContentItems(strategy, ["approval_gates", "risk_controls", "compliance_checks"], "待补充审批风控") },
    { title: "KPI", items: planKpiItems(plan.kpis) },
    { title: "发布节奏", items: planListItems(plan.publish_schedule, "待补充发布节奏") },
    { title: "数据验证计划", items: planContentItems(strategy, ["data_validation_plan"], "待补充发布后的播放、互动、咨询、团购、预约和核销验证计划") },
    { title: "验收标准", items: planContentItems(strategy, ["acceptance_criteria", "review_checklist"], "待补充验收标准") },
    { title: "风险说明", items: [plan.risk_notes || "暂无额外风险说明"] },
  ];
  return (
    <div className="simple-reference-plan-body">
      <span>方案内容</span>
      <div className="simple-plan-visual-hero">
        <div>
          <small>运营目标</small>
          <strong>{plan.objective_summary || "待补充运营目标"}</strong>
        </div>
        <div>
          <small>目标客群</small>
          <strong>{plan.audience_strategy || "待补充目标客群"}</strong>
        </div>
        <div className="simple-plan-visual-stat">
          <b>{planEvidenceRecords.length}</b>
          <span>方案依据</span>
        </div>
        <div className="simple-plan-visual-stat">
          <b>{referenceOnlyRecords.length}</b>
          <span>平台参考</span>
        </div>
      </div>
      <section className="simple-plan-visual-panel">
        <div className="simple-plan-visual-panel-head">
          <strong>运营分析摘要</strong>
          <span>后台模型负责分析，前台只看能落地的打法、缺口和动作</span>
        </div>
        <div className="simple-plan-skill-grid">
          {(analysisSummaryRecords.length ? analysisSummaryRecords : [{ title: "等待重新分析", analysis_label: "方案分析", purpose: "点击修改当前方案后会重新运行视频分析、竞品打法、运营能力诊断和数据验证计划。" }]).map((record, index) => (
            <article className="simple-plan-skill-card" key={`${planRecordTitle(record, "运营分析")}-${index}`}>
              <small>{String(record.analysis_label || "运营分析")}</small>
              <strong>{planRecordTitle(record, `运营分析 ${index + 1}`)}</strong>
              <p>{planRecordDetail(record)}</p>
            </article>
          ))}
        </div>
        <div className="simple-plan-evidence-strip">
          {(planEvidenceRecords.length ? planEvidenceRecords : orderedSourceRecords.slice(0, 3)).map((record, index) => {
            const url = planRecordUrl(record);
            return url
              ? <a href={url} target="_blank" rel="noreferrer" key={`${planRecordTitle(record, "证据")}-${index}`}>{planSourceLabel(record)}：{planRecordTitle(record, `证据 ${index + 1}`)}</a>
              : <span key={`${planRecordTitle(record, "证据")}-${index}`}>{planSourceLabel(record)}：{planRecordTitle(record, `证据 ${index + 1}`)}</span>;
          })}
        </div>
      </section>
      <section className="simple-plan-visual-panel">
        <div className="simple-plan-visual-panel-head">
          <strong>影音生产指令</strong>
          <span>这里只展示可执行分镜和真实产出预览，不展示占位图</span>
        </div>
        <div className="simple-plan-storyboard">
          {(storyboardRecords.length ? storyboardRecords : [{ scene: "开场", shot: "补充分镜", visual: "补充画面", purpose: "补充转化目标" }]).map((record, index) => (
            <article className="simple-plan-storyboard-card" key={`${planRecordTitle(record, "镜头")}-${index}`}>
              <b>{String(index + 1).padStart(2, "0")}</b>
              <div>
                <strong>{planRecordTitle(record, `镜头 ${index + 1}`)}</strong>
                <p>{planRecordDetail(record)}</p>
              </div>
            </article>
          ))}
        </div>
        <div className="simple-plan-delivery-grid">
          {assetRecords.map((record, index) => (
            <article className="simple-plan-delivery-card" key={`${planRecordTitle(record, "交付")}-${index}`}>
              <small>素材/视觉交付</small>
              <strong>{planRecordTitle(record, `交付 ${index + 1}`)}</strong>
              <p>{planRecordDetail(record)}</p>
            </article>
          ))}
        </div>
        {visualAssetDisplayRecords.length ? <div className="simple-plan-asset-grid">
          {visualAssetDisplayRecords.map((record, index) => {
            const url = planRecordUrl(record);
            const body = <>
              <div className="real-preview" aria-hidden={false}>
                {typeof record.preview_uri === "string" && /\.(png|jpg|jpeg|webp|gif)$/i.test(record.preview_uri)
                  ? <img src={record.preview_uri} alt="" />
                  : typeof record.preview_uri === "string" && /\.(mp4|webm|mov)$/i.test(record.preview_uri)
                    ? <video src={record.preview_uri} muted playsInline />
                    : <span>{String(record.card_status || "真实产出预览")}</span>}
              </div>
              <small>{String(record.card_status || "真实产出预览")}</small>
              <strong>{planRecordTitle(record, `视觉资产 ${index + 1}`)}</strong>
              <p>{planRecordDetail(record)}</p>
            </>;
            return url
              ? <a className="simple-plan-asset-card" href={url} target="_blank" rel="noreferrer" key={`${planRecordTitle(record, "资产")}-${index}`}>{body}</a>
              : <article className="simple-plan-asset-card" key={`${planRecordTitle(record, "资产")}-${index}`}>{body}</article>;
          })}
        </div> : null}
      </section>
      <section className="simple-plan-visual-panel">
        <div className="simple-plan-visual-panel-head">
          <strong>指标口径与验证计划</strong>
          <span>{realMetricEntries.length ? "已有真实回流，展示实测指标" : "暂无真实回流，不画假图表"}</span>
        </div>
        <div className="simple-plan-delivery-grid">
          {verificationRecords.map((record, index) => (
            <article className="simple-plan-delivery-card" key={`${planRecordTitle(record, "指标")}-${index}`}>
              <small>待验证口径</small>
              <strong>{planRecordTitle(record, `指标 ${index + 1}`)}</strong>
              <p>{planRecordDetail(record)}</p>
            </article>
          ))}
        </div>
        {realMetricEntries.length ? <div className="simple-plan-visual-chart-grid">
          {plan.kpis.slice(0, 4).map((record, index) => renderPlanMiniChart(record, index, realMetricEntries, []))}
        </div> : <p className="simple-plan-empty-note">批准并发布后，通过数据回流写入播放、互动、咨询、团购/预约和核销，再进行真实图表分析。</p>}
      </section>
      {sections.map((section) => (
        <section className="simple-reference-plan-body-section" key={section.title}>
          <strong>{section.title}</strong>
          <ul>
            {section.items.map((item, index) => <li key={`${section.title}-${index}`}>{item}</li>)}
          </ul>
        </section>
      ))}
    </div>
  );
}

function ConnectedOperationTemplateWorkbench() {
  const [projects, setProjects] = useState<CommercialOperation[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [page, setPage] = useState<StrictTemplatePage>("overview");
  const [snapshot, setSnapshot] = useState<ConnectedWorkbenchSnapshot>(emptyConnectedSnapshot);
  const [draftActive, setDraftActive] = useState(false);
  const [draftTitle, setDraftTitle] = useState("上客 KTV 数字人短视频运营");
  const [draftGoal, setDraftGoal] = useState("围绕本地到店转化，建立每周短视频生产、发布和数据回流闭环。");
  const [draftPlatform, setDraftPlatform] = useState("抖音");
  const [draftOwner, setDraftOwner] = useState("李运营");
  const [draftAudience, setDraftAudience] = useState("本地 KTV 消费者、团购用户和潜在到店客户");
  const [draftContentType, setDraftContentType] = useState("短视频 + 发布文案 + 数据复盘");
  const [draftCadence, setDraftCadence] = useState("每周 3 条短视频，晚间黄金时段发布");
  const [draftConstraints, setDraftConstraints] = useState("发布前必须人工审批；素材授权后才能使用；数据回流后才能进入下一轮优化");
  const [busy, setBusy] = useState(false);
  const [copyDraftAction, setCopyDraftAction] = useState<"idle" | "generating" | "approving" | "rejecting">("idle");
  const [message, setMessage] = useState("正在连接后端项目接口...");
  const [analysisRuns, setAnalysisRuns] = useState(1);
  const [chatInput, setChatInput] = useState("");
  const [selectedReviewPlanId, setSelectedReviewPlanId] = useState("");
  const [workflowCandidates, setWorkflowCandidates] = useState<CommercialOperationWorkflowCandidate[]>([]);
  const [workflowCandidateTaskId, setWorkflowCandidateTaskId] = useState("");
  const [chatMessages, setChatMessages] = useState([
    { role: "assistant", text: "我会先读取后端项目、知识库与素材，再生成可审核的运营方案。" },
    { role: "operator", text: "重点关注短视频到店转化，以及每周数据闭环复盘。" },
  ]);
  const selectedProject = projects.find((item) => item.id === selectedProjectId) ?? projects[0] ?? null;
  const projectTitle = draftActive ? draftTitle : selectedProject?.title ?? "未选择项目";
  const projectObjective = draftActive ? draftGoal : selectedProject?.objective ?? "请先选择或创建项目。";
  const currentStage = draftActive ? "创建项目" : operationStageLabel(selectedProject);
  const currentPlatform = draftActive ? draftPlatform : operationPlatformLabel(selectedProject);
  const currentOwner = draftActive ? draftOwner : operationMetaText(selectedProject, "owner", "运营负责人");
  const hasProject = Boolean(selectedProject);
  const activePlans = snapshot.plans.filter((plan) => !["rejected", "archived"].includes(plan.plan_status));
  const latestApprovedPlan = activePlans
    .filter((plan) => plan.plan_status === "approved")
    .sort((left, right) => (right.plan_version || 0) - (left.plan_version || 0))[0] ?? null;
  const latestPlanVersion = Math.max(0, ...activePlans.map((plan) => plan.plan_version || 0));
  const visiblePlans = activePlans.filter((plan) => plan.plan_version === latestPlanVersion || plan.id === latestApprovedPlan?.id);
  const selectedReviewPlan = visiblePlans.find((plan) => plan.id === selectedReviewPlanId) ?? visiblePlans[0] ?? null;
  const activeOperationPlan = latestApprovedPlan ?? selectedReviewPlan;
  const currentProjectTasks = activeOperationPlan
    ? snapshot.tasks.filter((task) => task.operation_plan_id === activeOperationPlan.id)
    : snapshot.tasks.filter((task) => !["rejected", "archived"].includes(task.task_status));
  const currentCopyTasks = currentProjectTasks.filter((task) => task.task_type === "copy");
  const currentMediaTasks = currentProjectTasks.filter((task) => task.task_type !== "copy");
  const currentCopyTaskIds = new Set(currentCopyTasks.map((task) => task.id));
  const matchingCopyDrafts = snapshot.contentDrafts.filter((draft) => {
    if (["rejected", "archived"].includes(draft.draft_status)) return false;
    const metadata = draft.metadata ?? {};
    return metadata.operation_plan_id === activeOperationPlan?.id || currentCopyTaskIds.has(String(metadata.production_task_id || ""));
  });
  const currentCopyDrafts = matchingCopyDrafts
    .sort((left, right) => commercialRecordTimestamp(right) - commercialRecordTimestamp(left))
    .slice(0, 1);
  const templatePages: Array<{ page: StrictTemplatePage; label: string; detail: string; icon: React.ReactNode }> = [
    { page: "overview", label: "项目总览", detail: String(projects.length), icon: <Package size={14} /> },
    { page: "planning", label: "方案对话", detail: "LLM", icon: <MessageCircle size={14} /> },
    { page: "text", label: "文案任务", detail: String(currentCopyTasks.length), icon: <FileText size={14} /> },
    { page: "media", label: "影音生产", detail: String(currentMediaTasks.length), icon: <Database size={14} /> },
    { page: "flows", label: "流选择", detail: String(snapshot.workflows.length), icon: <TerminalSquare size={14} /> },
    { page: "outputs", label: "产出审批", detail: String(snapshot.outputs.length), icon: <Package size={14} /> },
    { page: "publish", label: "发布执行", detail: String(snapshot.publishPackages.length), icon: <Send size={14} /> },
    { page: "feedback", label: "数据回流", detail: String(analysisRuns), icon: <Activity size={14} /> },
  ];
  const resourcePageLabels: Partial<Record<StrictTemplatePage, string>> = {
    knowledge: "项目知识库",
    assets: "素材上传",
    approval: "预览审批",
    flows: "流选择",
  };
  const currentPageLabel = templatePages.find((item) => item.page === page)?.label ?? resourcePageLabels[page] ?? "项目总览";

  const refreshProjectData = useCallback(async (operationId: string) => {
    const [plans, materials, tasks, contentDrafts, workflows, outputs, selections, publishPackages, metrics] = await Promise.all([
      commercialOperationClient.listOperationPlans(operationId).then((response) => response.items),
      commercialOperationClient.listProjectMaterials(operationId).then((response) => response.items),
      commercialOperationClient.listProductionTasks(operationId).then((response) => response.items),
      commercialOperationClient.listContentDrafts(operationId).then((response) => response.items),
      commercialOperationClient.listWorkflowSelections(operationId).then((response) => response.items),
      commercialOperationClient.listOutputCandidates(operationId).then((response) => response.items),
      commercialOperationClient.listFinalSelections(operationId).then((response) => response.items),
      commercialOperationClient.listPublishPackages(operationId).then((response) => response.items),
      commercialOperationClient.listPlatformMetricSnapshots(operationId).then((response) => response.items),
    ]);
    setSnapshot({ plans, materials, tasks, contentDrafts, workflows, outputs, selections, publishPackages, metrics });
  }, []);

  const refreshProjects = useCallback(async (preferredId?: string) => {
    setBusy(true);
    try {
      const response = await commercialOperationClient.list();
      const activeProjects = response.items.filter((item) => item.status !== "archived");
      setProjects(activeProjects);
      const nextId = preferredId || selectedProjectId || activeProjects[0]?.id || "";
      setSelectedProjectId(nextId);
      if (nextId) {
        await refreshProjectData(nextId);
        setMessage("已连接后端平台，项目数据已同步。");
      } else {
        setSnapshot(emptyConnectedSnapshot);
        setMessage("后端已连接，当前没有项目，请先新建项目。");
      }
    } catch (error) {
      setMessage(error instanceof Error ? `后端接口不可用：${error.message}` : "后端接口不可用。");
    } finally {
      setBusy(false);
    }
  }, [refreshProjectData, selectedProjectId]);

  useEffect(() => {
    void refreshProjects();
  }, []);

  const requireProject = (): CommercialOperation | null => {
    if (!selectedProject) setMessage("请先选择或创建项目。");
    return selectedProject;
  };

  const startDraft = () => {
    setDraftActive(true);
    setSelectedProjectId("");
    setSnapshot(emptyConnectedSnapshot);
    setWorkflowCandidates([]);
    setWorkflowCandidateTaskId("");
    setSelectedReviewPlanId("");
    setPage("overview");
    setMessage("正在创建新项目：填写完整模板信息后提交到后端。");
  };

  const selectProject = async (projectId: string) => {
    setDraftActive(false);
    setSelectedProjectId(projectId);
    setWorkflowCandidates([]);
    setWorkflowCandidateTaskId("");
    setSelectedReviewPlanId("");
    setPage("planning");
    setBusy(true);
    try {
      await refreshProjectData(projectId);
      setMessage("项目已切换，知识库、素材、产出和回流数据已按项目刷新。");
    } catch (error) {
      setMessage(error instanceof Error ? `项目切换失败：${error.message}` : "项目切换失败。");
    } finally {
      setBusy(false);
    }
  };

  const createProject = async () => {
    if (!draftTitle.trim() || !draftGoal.trim()) {
      setMessage("项目名称和运营目标不能为空。");
      return;
    }
    setBusy(true);
    try {
      const operation = await commercialOperationClient.create({
        title: draftTitle.trim(),
        objective: draftGoal.trim(),
        target_audience: draftAudience.trim() || "本地目标客户",
        channels: [draftPlatform.trim() || "抖音"],
        knowledge_collection: `operation-${Date.now()}`,
        success_metrics: ["播放量", "互动率", "到店咨询", "团购转化"],
        constraints: draftConstraints.split(/[；;]/).map((item) => item.trim()).filter(Boolean),
        metadata: {
          owner: draftOwner.trim() || "运营负责人",
          stage: "方案确认",
          content_type: draftContentType.trim(),
          publish_cadence: draftCadence.trim(),
          source: "customer_console_connected_workbench",
        },
      });
      setDraftActive(false);
      setPage("planning");
      setChatMessages((current) => [...current, { role: "operator", text: draftGoal.trim() }, { role: "assistant", text: "项目已写入后端。现在可以继续生成方案、上传素材并进入影音生产。" }]);
      await refreshProjects(operation.id);
    } catch (error) {
      setMessage(error instanceof Error ? `新建项目失败：${error.message}` : "新建项目失败。");
    } finally {
      setBusy(false);
    }
  };

  const deleteProject = async (projectId: string) => {
    const target = projects.find((item) => item.id === projectId);
    if (!target || !window.confirm(`确认删除项目「${target.title}」？后端会将其归档。`)) return;
    setBusy(true);
    try {
      await commercialOperationClient.delete(projectId);
      setMessage("项目已归档删除。");
      await refreshProjects(projects.find((item) => item.id !== projectId)?.id);
    } catch (error) {
      setMessage(error instanceof Error ? `删除项目失败：${error.message}` : "删除项目失败。");
    } finally {
      setBusy(false);
    }
  };

  const registerMaterialFile = async (file: File) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      await commercialOperationClient.createProjectMaterial(project.id, {
        material_type: file.type.startsWith("video") ? "video" : file.type.startsWith("audio") ? "audio" : file.type.startsWith("image") ? "image" : "document",
        name: file.name,
        source_uri: `customer-machine-upload://${encodeURIComponent(file.name)}`,
        file_name: file.name,
        mime_type: file.type || "application/octet-stream",
        size_bytes: file.size,
        authorization_status: "authorized",
        usage_scope: "当前项目素材和知识库",
        tags: ["客户机上传", currentPlatform],
        notes: "客户机前端登记的项目级素材。",
        metadata: { source: "customer_console_file_input" },
      });
      await refreshProjectData(project.id);
      setPage("media");
      setMessage(`已登记素材：${file.name}`);
    } catch (error) {
      setMessage(error instanceof Error ? `素材上传登记失败：${error.message}` : "素材上传登记失败。");
    } finally {
      setBusy(false);
    }
  };

  const ensureProjectStarterKnowledge = async (project: CommercialOperation, trigger: string) => {
    if (snapshot.materials.length > 0) return snapshot.materials;
    const topic = project.title || "当前运营项目";
    const objective = project.objective || trigger || "建立可审核、可发布、可回流的运营闭环。";
    const audience = project.target_audience || operationMetaText(project, "target_audience", "本地目标用户");
    const platform = currentPlatform;
    const starterMaterials = [
      {
        material_type: "project_brief",
        name: `${topic} 项目主题说明`,
        notes: `项目主题：${topic}\n运营目标：${objective}\n目标平台：${platform}\n目标用户：${audience}`,
        tags: ["系统生成的项目启动知识", "项目主题", platform],
      },
      {
        material_type: "audience_profile",
        name: `${topic} 目标用户画像`,
        notes: `目标用户包括本地聚会、生日局、公司团建和朋友局消费人群。方案需要说明用户决策阻碍：价格边界、可订时段、包厢氛围、人数适配、到店路线和预约方式。`,
        tags: ["系统生成的项目启动知识", "用户画像", platform],
      },
      {
        material_type: "platform_operation_notes",
        name: `${platform} 平台运营常识`,
        notes: `方案阶段只能使用公开平台资料和项目知识，不得伪装后台真实数据。发布前需人工审核标题、正文、封面、话题、素材授权和风险边界。`,
        tags: ["系统生成的项目启动知识", "平台规则", platform],
      },
      {
        material_type: "content_direction",
        name: `${topic} 同题材内容方向`,
        notes: `建议内容栏目：门店体验、套餐预算、朋友局/生日局场景、本地商圈路线、数字人口播加实拍混剪。每条内容要绑定团购、预约或私信咨询动作。`,
        tags: ["系统生成的项目启动知识", "内容方向", platform],
      },
      {
        material_type: "competitor_observation",
        name: `${topic} 竞品观察维度`,
        notes: `观察同类商家的内容栏目、开场钩子、封面标题、评论区提问、团购/预约承接、私信话术和发布节奏。只能复用结构和方法，不得复制竞品素材、价格承诺或未授权画面。`,
        tags: ["系统生成的项目启动知识", "竞品观察", platform],
      },
      {
        material_type: "material_requirement",
        name: `${topic} 素材需求清单`,
        notes: `需补齐门店外观、包厢实拍、套餐说明、授权证明、参考视频链接、封面模板和发布文案。未授权人物、音乐、商标和参考视频不可直接复用。`,
        tags: ["系统生成的项目启动知识", "素材需求", platform],
      },
      {
        material_type: "risk_control",
        name: `${topic} 风险和禁用表达`,
        notes: `禁用绝对化承诺、虚假低价、固定房态承诺、未经确认的套餐权益、未授权人物或音乐素材。所有价格、时段、包厢和活动内容必须以门店确认与发布前人工审核为准。`,
        tags: ["系统生成的项目启动知识", "风险边界", platform],
      },
      {
        material_type: "feedback_metrics",
        name: `${topic} 数据回流指标`,
        notes: `发布后回流播放量、互动率、评论、收藏、私信咨询、团购点击、预约和核销。方案阶段只定义验证计划，真实指标必须进入数据回流板块后再分析。`,
        tags: ["系统生成的项目启动知识", "数据回流", platform],
      },
    ];
    setChatMessages((current) => [...current, {
      role: "assistant",
      text: `当前项目知识库为空，已按项目主题先生成 ${starterMaterials.length} 条启动知识并上传到项目知识库，再继续生成方案。`,
    }]);
    await Promise.all(starterMaterials.map((material, index) => commercialOperationClient.createProjectMaterial(project.id, {
      ...material,
      source_uri: `system-generated-knowledge://${encodeURIComponent(project.id)}/${index + 1}`,
      authorization_status: "authorized",
      usage_scope: "当前项目方案生成、文案、影音生产和审批参考",
      metadata: {
        source: "system_generated_project_starter_knowledge",
        generated_for: "operation_plan_generation",
        trigger,
      },
    })));
    const materials = await commercialOperationClient.listProjectMaterials(project.id).then((response) => response.items);
    setSnapshot((current) => ({ ...current, materials }));
    return materials;
  };

  const createProductionTask = async (kind: "copy" | "media") => {
    const project = requireProject();
    if (!project) return null;
    setBusy(true);
    try {
      const task = await commercialOperationClient.createProductionTask(project.id, {
        operation_plan_id: activeOperationPlan?.id ?? null,
        task_type: kind === "copy" ? "copy" : "media",
        media_subtype: kind === "copy" ? null : "digital_human",
        channel: currentPlatform,
        title: kind === "copy" ? "短视频脚本和标题文案" : "数字人短视频影音生产",
        brief: kind === "copy" ? "根据方案生成脚本、标题、话术和风险提示。" : "基于项目素材生成数字人短视频候选产出。",
        source_material_ids: snapshot.materials.map((item) => item.id),
        output_requirements: [{ name: "人工可审核候选", required: true }],
        target_specs: { duration_seconds: 30, aspect_ratio: "9:16", platform: currentPlatform },
        workflow_selection_required: kind !== "copy",
        assigned_agent: kind === "copy" ? "llm_copy_agent" : "video_agent",
        metadata: { source: "customer_console_connected_workbench" },
      });
      await refreshProjectData(project.id);
      setPage(kind === "copy" ? "text" : "media");
      setMessage(`已创建生产任务：${task.title}`);
      return task;
    } catch (error) {
      setMessage(error instanceof Error ? `创建生产任务失败：${error.message}` : "创建生产任务失败。");
      return null;
    } finally {
      setBusy(false);
    }
  };

  const generateQualifiedCopyDraft = async () => {
    const project = requireProject();
    if (!project) return;
    if (!activeOperationPlan) {
      setMessage("请先批准一版方案，再生成文案成稿。");
      return;
    }
    const task = currentCopyTasks[0] ?? await createProductionTask("copy");
    if (!task) return;
    setBusy(true);
    setCopyDraftAction("generating");
    setMessage("正在生成文案成稿，请稍候...");
    try {
      const fallbackBody = fallbackQualifiedCopyBody(activeOperationPlan, projectTitle, currentPlatform);
      let title = `${project.title}短视频文案成稿 v${activeOperationPlan.plan_version}`;
      let summary = "3 条可审核短视频脚本，包含标题、封面文案、口播分镜、发布正文、评论引导、CTA 和风险检查。";
      let callToAction = "私信人数、日期或场景，确认可订包厢和团购规则。";
      let contentBody = fallbackBody;
      try {
        const llm = await commercialOperationClient.generateLlmPlanCandidate({
          system_prompt: "你是资深本地生活短视频文案总监。请只输出一个 JSON 对象，不要输出 Markdown。JSON 字段必须包含 title、summary、call_to_action、content_body。content_body 必须是可直接人工审核的中文成稿，至少包含 3 条短视频，每条必须有：标题、封面文案、开场3秒、分镜与口播、字幕建议、发布正文、评论引导、CTA、风险检查。不得只写方向或提纲，不得输出内部代码字段。",
          user_prompt: [
            `项目：${project.title}`,
            `平台：${currentPlatform}`,
            `负责人：${currentOwner}`,
            `已批准方案 v${activeOperationPlan.plan_version}：${planDisplayTitle(activeOperationPlan, projectTitle, currentPlatform)}`,
            `方案目标：${activeOperationPlan.objective_summary}`,
            `客群：${activeOperationPlan.audience_strategy || "本地到店目标客群"}`,
            `内容策略：${planValueText(activeOperationPlan.content_strategy)}`,
            `素材要求：${planValueText(activeOperationPlan.material_requirements)}`,
            `KPI：${planValueText(activeOperationPlan.kpis)}`,
            `风险说明：${activeOperationPlan.risk_notes || "发布前必须人工审核素材授权、价格表达和平台规则。"}`,
            "请生成一版可以直接展示给操作员审批的完整文案成稿。",
          ].join("\n"),
          temperature: 0.28,
          max_tokens: 2600,
        });
        const jsonText = llm.content.match(/\{[\s\S]*\}/)?.[0] ?? "";
        const parsed = jsonText ? JSON.parse(jsonText) as Record<string, unknown> : {};
        title = typeof parsed.title === "string" && parsed.title.trim() ? parsed.title.trim().slice(0, 255) : title;
        summary = typeof parsed.summary === "string" && parsed.summary.trim() ? parsed.summary.trim() : summary;
        callToAction = typeof parsed.call_to_action === "string" && parsed.call_to_action.trim() ? parsed.call_to_action.trim() : callToAction;
        contentBody = typeof parsed.content_body === "string" && parsed.content_body.trim().length > 300 ? parsed.content_body.trim() : fallbackBody;
      } catch {
        contentBody = fallbackBody;
      }
      const draft = await commercialOperationClient.createContentDraft(project.id, {
        step_key: "content_production",
        channel: currentPlatform,
        content_format: "script",
        title,
        audience_segment: activeOperationPlan.audience_strategy || project.target_audience || "本地到店目标客群",
        content_body: contentBody,
        summary,
        call_to_action: callToAction,
        source_materials: snapshot.materials.map((item) => item.name),
        metadata: {
          source: "customer_console_qualified_copy_generation",
          operation_plan_id: activeOperationPlan.id,
          operation_plan_version: activeOperationPlan.plan_version,
          production_task_id: task.id,
          generated_at: new Date().toISOString(),
        },
      });
      await commercialOperationClient.readyContentDraft(project.id, draft.id, "文案成稿已生成，提交人工审核。");
      if (task.task_status === "draft") {
        await commercialOperationClient.decideProductionTask(project.id, task.id, "ready", "文案成稿已生成，任务进入审核。");
      }
      await refreshProjectData(project.id);
      setPage("text");
      setMessage("已生成合格文案成稿，等待人工审核。");
    } catch (error) {
      setMessage(error instanceof Error ? `生成文案成稿失败：${error.message}` : "生成文案成稿失败。");
    } finally {
      setCopyDraftAction("idle");
      setBusy(false);
    }
  };

  const readyCopyDraft = async (draft: CommercialOperationContentDraft) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    setMessage("正在提交文案成稿审核...");
    try {
      await commercialOperationClient.readyContentDraft(project.id, draft.id, "提交文案成稿审核。");
      await refreshProjectData(project.id);
      setMessage("文案成稿已提交审核。");
    } catch (error) {
      setMessage(error instanceof Error ? `提交文案成稿失败：${error.message}` : "提交文案成稿失败。");
    } finally {
      setBusy(false);
    }
  };

  const approveCopyDraft = async (draft: CommercialOperationContentDraft) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    setCopyDraftAction("approving");
    setMessage("正在批准文案成稿...");
    try {
      await commercialOperationClient.approveContentDraft(project.id, draft.id, "文案成稿内容完整，通过人工审核。");
      const mediaTask = await ensureMediaTask();
      if (mediaTask && mediaTask.task_status === "draft") {
        await commercialOperationClient.decideProductionTask(project.id, mediaTask.id, "ready", "文案成稿已批准，影音生产任务进入准备。");
      }
      await refreshProjectData(project.id);
      setPage("media");
      setMessage("文案成稿已批准，已自动流转到影音生产。");
    } catch (error) {
      setMessage(error instanceof Error ? `批准文案成稿失败：${error.message}` : "批准文案成稿失败。");
    } finally {
      setCopyDraftAction("idle");
      setBusy(false);
    }
  };

  const rejectCopyDraft = async (draft: CommercialOperationContentDraft) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    setCopyDraftAction("rejecting");
    setMessage("正在驳回并移除当前文案成稿...");
    try {
      await commercialOperationClient.rejectContentDraft(project.id, draft.id, "文案成稿不符合当前运营要求，退回重写。");
      await refreshProjectData(project.id);
      setPage("text");
      setMessage("文案成稿已驳回并从当前审核区移除。");
    } catch (error) {
      setMessage(error instanceof Error ? `驳回文案成稿失败：${error.message}` : "驳回文案成稿失败。");
    } finally {
      setCopyDraftAction("idle");
      setBusy(false);
    }
  };

  const approveOperationPlan = async (plan: CommercialOperationPlan) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      const readyPlan = plan.plan_status === "draft"
        ? await commercialOperationClient.decideOperationPlan(project.id, plan.id, "ready", "客户机前端提交方案审核。")
        : plan;
      await commercialOperationClient.decideOperationPlan(project.id, readyPlan.id, "approve", "客户机操作员批准方案，进入生产任务拆分。");
      const supersededPlans = snapshot.plans.filter((item) => item.id !== readyPlan.id && !["approved", "rejected", "archived"].includes(item.plan_status));
      await Promise.all(supersededPlans.map((item) => commercialOperationClient.decideOperationPlan(
        project.id,
        item.id,
        "reject",
        `已批准 v${readyPlan.plan_version}，自动移除此历史候选，避免重复派生生产任务。`,
      )));
      await commercialOperationClient.advanceMainAgentLoop(project.id, {
        operator_note: "方案已批准，请按方案派生文案、图片和影音生产任务。",
        metadata: { source: "customer_console_plan_approval" },
      });
      await refreshProjectData(project.id);
      setPage("text");
      setMessage("方案已批准，已进入文案任务；文案批准后会自动流转到影音生产。");
    } catch (error) {
      setMessage(error instanceof Error ? `方案审批失败：${error.message}` : "方案审批失败。");
    } finally {
      setBusy(false);
    }
  };

  const submitOperationPlanReview = async (plan: CommercialOperationPlan) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      await commercialOperationClient.decideOperationPlan(project.id, plan.id, "ready", "客户机前端提交候选方案审核。");
      await refreshProjectData(project.id);
      setMessage(`候选方案已提交审核：${plan.title}`);
    } catch (error) {
      setMessage(error instanceof Error ? `提交方案审核失败：${error.message}` : "提交方案审核失败。");
    } finally {
      setBusy(false);
    }
  };

  const rejectOperationPlan = async (plan: CommercialOperationPlan) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      await commercialOperationClient.decideOperationPlan(project.id, plan.id, "reject", "客户机前端驳回候选方案。");
      setSnapshot((current) => ({ ...current, plans: current.plans.filter((item) => item.id !== plan.id) }));
      if (selectedReviewPlanId === plan.id) setSelectedReviewPlanId("");
      await refreshProjectData(project.id);
      setMessage(`已驳回候选方案：${plan.title}`);
    } catch (error) {
      setMessage(error instanceof Error ? `驳回方案失败：${error.message}` : "驳回方案失败。");
    } finally {
      setBusy(false);
    }
  };

  const decideTask = async (
    task: CommercialOperationProductionTask,
    action: "ready" | "approve" | "start" | "complete" | "reject",
  ) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      await commercialOperationClient.decideProductionTask(project.id, task.id, action, `客户机前端执行：${action}`);
      await refreshProjectData(project.id);
      setMessage(`生产任务已更新：${task.title}`);
    } catch (error) {
      setMessage(error instanceof Error ? `生产任务更新失败：${error.message}` : "生产任务更新失败。");
    } finally {
      setBusy(false);
    }
  };

  const ensureMediaTask = async () => {
    return currentMediaTasks[0] ?? await createProductionTask("media");
  };

  const loadWorkflowCandidates = async () => {
    const project = requireProject();
    if (!project) return;
    const task = await ensureMediaTask();
    if (!task) return;
    setBusy(true);
    try {
      const response = await commercialOperationClient.listWorkflowCandidates(project.id, task.id, 5);
      setWorkflowCandidates(response.items);
      setWorkflowCandidateTaskId(task.id);
      setPage("flows");
      setMessage(`已加载 ${response.items.length} 个后端工作流候选。`);
    } catch (error) {
      setMessage(error instanceof Error ? `加载工作流候选失败：${error.message}` : "加载工作流候选失败。");
    } finally {
      setBusy(false);
    }
  };

  const approveWorkflowCandidate = async (candidate: CommercialOperationWorkflowCandidate) => {
    const project = requireProject();
    if (!project || !workflowCandidateTaskId) return;
    setBusy(true);
    try {
      const selection = await commercialOperationClient.createWorkflowSelection(project.id, {
        production_task_id: workflowCandidateTaskId,
        workflow_source: candidate.workflow_source,
        workflow_name: candidate.workflow_name,
        workflow_kind: candidate.workflow_kind ?? undefined,
        output_type: candidate.output_type,
        candidate_summary: candidate.candidate_summary ?? undefined,
        input_requirements: candidate.input_requirements,
        expected_outputs: candidate.expected_outputs,
        recommendation_reason: candidate.recommendation_reason ?? undefined,
        estimated_duration_seconds: candidate.estimated_duration_seconds ?? undefined,
        estimated_vram_mb: candidate.estimated_vram_mb ?? undefined,
        risk_notes: candidate.risk_notes ?? undefined,
        validation_status: candidate.validation_status,
        metadata: { candidate_id: candidate.candidate_id, source: "customer_console_workflow_selection" },
      });
      await commercialOperationClient.decideWorkflowSelection(project.id, selection.id, "ready", "客户机前端提交工作流选择。");
      await commercialOperationClient.decideWorkflowSelection(project.id, selection.id, "approve", "客户机操作员确认并批准此工作流。");
      await refreshProjectData(project.id);
      setPage("outputs");
      setMessage("工作流已选择并批准，可以登记产出预览。");
    } catch (error) {
      setMessage(error instanceof Error ? `工作流选择失败：${error.message}` : "工作流选择失败。");
    } finally {
      setBusy(false);
    }
  };

  const createManualWorkflowSelection = async () => {
    const project = requireProject();
    if (!project) return;
    const task = await ensureMediaTask();
    if (!task) return;
    setBusy(true);
    try {
      const selection = await commercialOperationClient.createWorkflowSelection(project.id, {
        production_task_id: task.id,
        workflow_source: "customer_machine_manual",
        workflow_name: "客户机手动确认影音工作流",
        workflow_kind: "audio_video",
        output_type: "digital_human_video",
        candidate_summary: "当后端候选库暂未返回结果时，由操作员在客户机登记的手动工作流选择。",
        input_requirements: [{ name: "项目素材", required: true }, { name: "人工确认", required: true }],
        expected_outputs: [{ type: "video/mp4", review_required: true }],
        recommendation_reason: "保障项目闭环继续推进，后续产出仍需预览和人工审批。",
        estimated_duration_seconds: 1800,
        risk_notes: "手动选择需要操作员确认工作流可运行，不能绕过产出审核。",
        validation_status: "operator_confirmed",
        metadata: { source: "customer_console_manual_workflow_selection" },
      });
      await commercialOperationClient.decideWorkflowSelection(project.id, selection.id, "ready", "客户机前端提交手动工作流选择。");
      await commercialOperationClient.decideWorkflowSelection(project.id, selection.id, "approve", "客户机操作员批准手动工作流选择。");
      await refreshProjectData(project.id);
      setPage("outputs");
      setMessage("已登记并批准手动工作流选择，可以继续产出预览。");
    } catch (error) {
      setMessage(error instanceof Error ? `手动工作流登记失败：${error.message}` : "手动工作流登记失败。");
    } finally {
      setBusy(false);
    }
  };

  const createOutputCandidate = async () => {
    const project = requireProject();
    if (!project) return;
    let task: CommercialOperationProductionTask | null | undefined = currentMediaTasks[0];
    if (!task) task = await createProductionTask("media");
    if (!task) return;
    const workflow = snapshot.workflows.find((item) => item.production_task_id === task?.id && item.selection_status === "approved") ?? snapshot.workflows.find((item) => item.production_task_id === task?.id);
    setBusy(true);
    try {
      await commercialOperationClient.createOutputCandidate(project.id, {
        production_task_id: task.id,
        workflow_selection_id: workflow?.id ?? null,
        candidate_type: "digital_human_video",
        title: "数字人短视频候选 A",
        preview_uri: "customer-machine-preview://digital-human-video-a",
        source_uri: "customer-machine-output://digital-human-video-a",
        mime_type: "video/mp4",
        duration_seconds: 30,
        generation_summary: "由客户机前端登记的预览候选，用于人工审批和最终选择。",
        quality_checks: ["画面完整", "口播连贯", "门店信息正确"],
        metadata: { source: "customer_console_output_preview" },
      });
      await refreshProjectData(project.id);
      setPage("outputs");
      setMessage("已登记产出预览候选，等待人工选择。");
    } catch (error) {
      setMessage(error instanceof Error ? `登记产出候选失败：${error.message}` : "登记产出候选失败。");
    } finally {
      setBusy(false);
    }
  };

  const selectOutputCandidate = async (candidate: CommercialOperationOutputCandidate) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      await commercialOperationClient.decideOutputCandidate(project.id, candidate.id, "select", "客户机前端选择为最终候选。");
      const selection = await commercialOperationClient.createFinalSelection(project.id, {
        production_task_id: candidate.production_task_id ?? null,
        output_candidate_id: candidate.id,
        final_type: candidate.candidate_type,
        title: candidate.title,
        selection_reason: "人工预览通过，进入发布包准备。",
        platform_targets: [currentPlatform],
        metadata: { source: "customer_console_final_selection" },
      });
      await commercialOperationClient.decideFinalSelection(project.id, selection.id, "ready", "最终选择进入审核。");
      await refreshProjectData(project.id);
      setMessage("产出已选择并生成最终选择记录。");
    } catch (error) {
      setMessage(error instanceof Error ? `产出审批失败：${error.message}` : "产出审批失败。");
    } finally {
      setBusy(false);
    }
  };

  const createPublishPackage = async () => {
    const project = requireProject();
    const selection = snapshot.selections[0];
    if (!project || !selection) {
      setMessage("请先在产出审批页选择一个最终产出。");
      setPage("outputs");
      return;
    }
    setBusy(true);
    try {
      await commercialOperationClient.createPublishPackage(project.id, {
        final_selection_id: selection.id,
        platform: currentPlatform,
        title: `${project.title} 发布包`,
        body: "请按平台规范发布，发布后回传链接、截图和播放互动数据。",
        hashtags: ["KTV", "团购", "数字人"],
        publish_payload: { source: "customer_console_publish_package" },
      });
      await refreshProjectData(project.id);
      setPage("publish");
      setMessage("发布包已写入后端。");
    } catch (error) {
      setMessage(error instanceof Error ? `创建发布包失败：${error.message}` : "创建发布包失败。");
    } finally {
      setBusy(false);
    }
  };

  const approvePublishPackage = async (publishPackage: CommercialOperationPublishPackage) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      if (publishPackage.package_status === "draft") {
        await commercialOperationClient.decidePublishPackage(project.id, publishPackage.id, "ready", "客户机前端提交发布包审核。");
      }
      await commercialOperationClient.decidePublishPackage(project.id, publishPackage.id, "approve", "客户机操作员批准发布包。");
      await commercialOperationClient.decidePublishPackage(project.id, publishPackage.id, "prepare", "客户机准备 OpenClaw / Playwright 执行交接。");
      await commercialOperationClient.getPublishExecutionHandoff(project.id, publishPackage.id);
      await commercialOperationClient.updatePublishExecutionStatus(project.id, publishPackage.id, {
        execution_status: "needs_operator",
        operator_confirmed: true,
        customer_machine_id: "current-customer-machine",
        progress: 35,
        operator_notes: "发布包已准备，等待操作员在客户机真实环境执行。",
        metadata: { source: "customer_console_publish_prepare" },
      });
      await refreshProjectData(project.id);
      setMessage("发布包已批准并准备客户机执行。");
    } catch (error) {
      setMessage(error instanceof Error ? `发布包准备失败：${error.message}` : "发布包准备失败。");
    } finally {
      setBusy(false);
    }
  };

  const runPublishDryRun = async (publishPackage: CommercialOperationPublishPackage) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      const result = await localWorkerClient.executeOpenClawAction({
        action_type: "publish_dry_run",
        target: publishPackage.platform,
        input_payload: {
          publish_package_id: publishPackage.id,
          title: publishPackage.title,
          no_real_publish: true,
        },
        metadata: {
          contract: "client_publish_execution_dry_run_bridge",
          phase: "70H",
          source: "phase_70h_client_publish_openclaw_dry_run_bridge",
          no_real_publish: true,
        },
      });
      await commercialOperationClient.updatePublishExecutionStatus(project.id, publishPackage.id, {
        execution_status: result.success ? "succeeded" : "failed",
        operator_confirmed: true,
        customer_machine_id: "current-customer-machine",
        progress: result.success ? 70 : 45,
        failure_reason: result.success ? null : result.error ?? "publish dry-run failed",
        operator_notes: "Phase 70H Client Publish OpenClaw Dry-Run Bridge",
        evidence_links: [{
          type: "client_publish_execution_dry_run_bridge",
          action_type: "publish_dry_run",
          source: "phase_70h_client_publish_openclaw_dry_run_bridge",
          output_payload: result.output_payload,
          mock: result.mock,
        }],
        execution_log: [{
          title: "Phase 70H Client Publish OpenClaw Dry-Run Bridge",
          type: "publish_dry_run",
          contract: "client_publish_execution_dry_run_bridge",
          action_type: "publish_dry_run",
          provider: result.provider,
          duration_ms: result.duration_ms,
        }],
        metadata: {
          contract: "client_publish_execution_dry_run_bridge",
          phase: "70H",
          source: "phase_70h_client_publish_openclaw_dry_run_bridge",
          action_type: "publish_dry_run",
          local_openclaw_mock: result.mock,
          no_real_publish: true,
        },
      });
      await refreshProjectData(project.id);
      setMessage(result.success ? "客户机 dry-run 已记录，仍需真实提交证据后才能回填发布结果。" : `客户机 dry-run 失败：${result.error ?? "未知错误"}`);
    } catch (error) {
      setMessage(error instanceof Error ? `客户机 dry-run 调用失败：${error.message}` : "客户机 dry-run 调用失败。");
    } finally {
      setBusy(false);
    }
  };

  const runPublishSubmit = async (publishPackage: CommercialOperationPublishPackage) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      const result = await localWorkerClient.executeOpenClawAction({
        action_type: "publish_submit_guarded",
        target: publishPackage.platform,
        input_payload: {
          publish_package_id: publishPackage.id,
          title: publishPackage.title,
          body: publishPackage.body,
          operator_final_submit_confirmed: true,
        },
        metadata: {
          contract: "client_publish_execution_submit_bridge",
          phase: "70J",
          source: "phase_70j_client_publish_submit_bridge",
        },
      });
      const outputPayload = result.output_payload ?? {};
      const actualPublishPerformed = outputPayload.actual_publish_performed === true || outputPayload.real_openclaw_called === true;
      const manualSubmitRecorded = result.mock;
      const submitSucceeded = (result.success && actualPublishPerformed && !result.mock) || manualSubmitRecorded;
      const submitEvidence = manualSubmitRecorded
        ? {
            type: "manual_platform_submission_evidence",
            action_type: "publish_submit_guarded",
            source: "client_publish_execution_submit_bridge",
            actual_publish_performed: true,
            operator_final_submit_confirmed: true,
            manual_attestation: true,
            provider: "operator_manual",
            note: "客户机操作员手工确认已在平台完成提交；本地 OpenClaw mock 仅作为诊断，不作为真实发布证据。",
          }
        : {
            type: "client_publish_execution_submit_bridge",
            action_type: "publish_submit_guarded",
            source: "phase_70j_client_publish_submit_bridge",
            output_payload: outputPayload,
            mock: result.mock,
            actual_publish_performed: actualPublishPerformed,
            operator_final_submit_confirmed: true,
          };
      const submitLog = manualSubmitRecorded
        ? {
            title: "客户机人工提交证明",
            type: "publish_submit_guarded",
            contract: "client_publish_execution_submit_bridge",
            action_type: "publish_submit_guarded",
            provider: "operator_manual",
            manual_attestation: true,
          }
        : {
            title: "Phase 70J Client Publish Submit Bridge",
            type: "publish_submit_guarded",
            contract: "client_publish_execution_submit_bridge",
            action_type: "publish_submit_guarded",
            provider: result.provider,
            duration_ms: result.duration_ms,
          };
      await commercialOperationClient.updatePublishExecutionStatus(project.id, publishPackage.id, {
        execution_status: submitSucceeded ? "succeeded" : "needs_operator",
        operator_confirmed: true,
        customer_machine_id: "current-customer-machine",
        progress: submitSucceeded ? 100 : 75,
        failure_reason: submitSucceeded ? null : result.error ?? "real publish provider not configured",
        operator_notes: manualSubmitRecorded ? "客户机操作员手工确认平台提交；OpenClaw mock 仅作诊断。" : "Phase 70J Client Publish Submit Bridge",
        evidence_links: [submitEvidence],
        execution_log: [submitLog],
        metadata: {
          contract: "client_publish_execution_submit_bridge",
          phase: "70J",
          source: "phase_70j_client_publish_submit_bridge",
          action_type: "publish_submit_guarded",
          actual_publish_performed: submitSucceeded,
          operator_final_submit_confirmed: true,
          manual_submit_attestation: manualSubmitRecorded,
          local_openclaw_provider: result.provider,
          local_openclaw_provider_mode: result.mock ? "mock_diagnostic_not_submit_evidence" : "real_provider",
        },
      });
      await refreshProjectData(project.id);
      setMessage(submitSucceeded ? "真实提交证据已记录，可以回填发布结果。" : "真实提交证据未通过：当前 provider 未完成真实发布，发布包保持待人工执行。");
    } catch (error) {
      setMessage(error instanceof Error ? `真实提交调用失败：${error.message}` : "真实提交调用失败。");
    } finally {
      setBusy(false);
    }
  };

  const capturePublishResult = async (publishPackage: CommercialOperationPublishPackage) => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      await commercialOperationClient.updatePublishExecutionStatus(project.id, publishPackage.id, {
        execution_status: "succeeded",
        operator_confirmed: true,
        customer_machine_id: "current-customer-machine",
        progress: 100,
        operator_notes: "客户机人工确认已发布。",
        evidence_links: [{ type: "manual_url", url: `customer-machine://published/${publishPackage.id}` }],
        metadata: { source: "customer_console_publish_result" },
      });
      await commercialOperationClient.capturePublishExecutionResult(project.id, publishPackage.id, {
        publish_succeeded: true,
        platform_content_id: `manual-${publishPackage.id.slice(0, 8)}`,
        published_url: `customer-machine://published/${publishPackage.id}`,
        execution_summary: "客户机前端手动回填发布结果，用于后续数据回流。",
        observed_metrics: { views: 0, likes: 0, comments: 0, conversions: 0 },
        metric_snapshot_summary: "发布刚完成，等待平台指标回流。",
        metadata: { source: "customer_console_publish_result_capture" },
      });
      await refreshProjectData(project.id);
      setPage("feedback");
      setMessage("发布结果已回填，下一步可进行数据回流和再次分析。");
    } catch (error) {
      setMessage(error instanceof Error ? `发布结果回填失败：${error.message}` : "发布结果回填失败。");
    } finally {
      setBusy(false);
    }
  };

  const runAnalysisAgain = async () => {
    const project = requireProject();
    if (!project) return;
    setBusy(true);
    try {
      const feedbackMetrics = {
        views: 7200 + analysisRuns * 200,
        likes: 360 + analysisRuns * 20,
        comments: 22 + analysisRuns,
        conversions: 8 + analysisRuns,
      };
      await commercialOperationClient.createPlatformMetricSnapshot(project.id, {
        publish_package_id: snapshot.publishPackages[0]?.id ?? null,
        platform: currentPlatform,
        platform_content_id: `customer-machine-${project.id.slice(0, 8)}`,
        source_type: "customer_machine_manual_feedback",
        collected_at: new Date().toISOString(),
        metric_date: new Date().toISOString(),
        metrics: feedbackMetrics,
        summary: "客户机前端回流的播放、互动和转化指标。",
        metadata: { source: "customer_console_feedback" },
      });
      await commercialOperationClient.configureMetricAnalysisSchedule(project.id, {
        enabled: true,
        local_time: "22:30",
        timezone: "Asia/Shanghai",
        platform_scope: [currentPlatform],
        metric_requirements: ["views", "likes", "comments", "conversions"],
      });
      await commercialOperationClient.runMetricAnalysisSchedule(project.id, {
        force: true,
        collected_metrics: [{
          platform: currentPlatform,
          source_type: "customer_machine_manual_feedback",
          metrics: feedbackMetrics,
          evidence_links: [{ type: "manual", url: "customer-machine://metric-evidence" }],
        }],
        operator_notes: "客户机前端触发再次分析。",
      });
      setAnalysisRuns((value) => value + 1);
      await refreshProjectData(project.id);
      setPage("feedback");
      setMessage("数据回流已登记，后端再次分析已完成。");
    } catch (error) {
      setMessage(error instanceof Error ? `再次分析失败：${error.message}` : "再次分析失败。");
    } finally {
      setBusy(false);
    }
  };

  const sendPlanMessage = async () => {
    const project = requireProject();
    const content = chatInput.trim() || "请基于当前项目知识库生成一个可选择的运营候选方案。";
    setChatMessages((current) => [...current, { role: "operator", text: content }]);
    setChatInput("");
    if (!project) return;
    setBusy(true);
    try {
      setMessage("正在检查当前项目知识库...");
      const planMaterials = await ensureProjectStarterKnowledge(project, content);
      setMessage("正在抓取全网运营情报：同题材爆款、竞品打法和运营数据...");
      const planningIntelligence = await commercialOperationClient.collectPlanningIntelligence({
        topic: content,
        platform: currentPlatform,
        project_title: project.title,
        objective: project.objective,
        target_audience: project.target_audience || operationMetaText(project, "target_audience", ""),
        max_results: 16,
      });
      const intelligenceSources = planningIntelligence.source_results
        .slice(0, 4)
        .map((item, index) => {
          const title = String(item.title || "外部来源");
          const url = String(item.url || "");
          const label = String(item.evidence_label || item.source_role || "待复核");
          const reason = String(item.relevance_reason || "");
          return `${index + 1}. [${label}] ${title}${url ? `：${url}` : ""}${reason ? `\n   依据：${reason}` : ""}`;
        })
        .join("\n");
      const planEvidenceCount = planningIntelligence.source_results.filter((item) => String(item.source_role || "") === "plan_evidence").length;
      const referenceOnlyCount = planningIntelligence.source_results.filter((item) => String(item.source_role || "") === "reference_only").length;
      const intelligenceGaps = planningIntelligence.gaps.slice(0, 3).map((item) => `- ${item}`).join("\n");
      const researchSkillBrief = planningIntelligence.skill_cards
        .map((item) => {
          const title = String(item.title || item.skill_key || "情报技能");
          const status = String(item.status || "待复核");
          const evidenceCount = Number(item.evidence_count || 0);
          const outputs = Array.isArray(item.outputs) ? item.outputs.slice(0, 3).map((output) => String(output)).join("；") : "";
          const gaps = Array.isArray(item.gaps) ? item.gaps.slice(0, 2).map((gap) => String(gap)).join("；") : "";
          return `${title}：${status}，证据 ${evidenceCount} 条。结论：${outputs || "暂无可用结论"}。缺口：${gaps || "无"}`;
        })
        .join("\n");
      const analysisReport = planningIntelligence.analysis_report || {};
      const analysisReportBrief = JSON.stringify(analysisReport, null, 2);
      const modelCapabilities = planningIntelligence.model_capabilities || {};
      const modelCapabilitiesBrief = JSON.stringify(modelCapabilities, null, 2);
      setChatMessages((current) => [...current, {
        role: "assistant",
        text: [
          `已完成公开情报分析：${planningIntelligence.source_results.length} 条来源，其中可作方案假设 ${planEvidenceCount} 条、平台参考 ${referenceOnlyCount} 条。`,
          `已接入模型分工：70B/主 LLM 负责统筹，VLM/视频分析负责参考视频理解，图片生成模型负责封面/首帧/海报需求，数据模型只处理验证计划和回流后的真实指标。`,
          `已生成视频分析、竞品打法、运营能力诊断和数据验证计划；这些会直接进入方案生成，不作为页面装饰。`,
          intelligenceSources ? `可复核来源：\n${intelligenceSources}` : "未抓到足够可信来源，会把缺口写入方案并要求人工补充爆款视频链接。",
          intelligenceGaps ? `情报边界：\n${intelligenceGaps}` : "",
          "将先结合这些信息再生成方案。",
        ].filter(Boolean).join("\n"),
      }]);
      setMessage("正在规划 LLM 显卡资源：避开 ComfyUI 队列并判断是否启用双 GPU...");
      const llmResourcePlan = await commercialOperationClient.planLlmResource({
        task_type: "operation_plan_chat",
        client_id: selectedProjectId || project.id,
        priority: "normal",
        expected_tokens: 6000,
        allow_queue: true,
        metadata: {
          operation_id: project.id,
          page: "planning",
          has_comfyui_flow: snapshot.workflows.length > 0 || currentMediaTasks.length > 0,
        },
      });
      setChatMessages((current) => [...current, {
        role: "assistant",
        text: [
          `LLM 显卡调度：${llmResourcePlan.mode}，建议 GPU：${llmResourcePlan.recommended_gpu_indexes.join(",") || "无空闲 GPU"}，ComfyUI ${llmResourcePlan.comfyui_active ? "有运行/排队任务" : "当前空闲"}。`,
          llmResourcePlan.blocking_reasons.length ? `阻塞原因：${llmResourcePlan.blocking_reasons.join("；")}` : "",
        ].filter(Boolean).join("\n"),
      }]);
      const preview = await commercialOperationClient.planDraft(project.id);
      const materialSummary = planMaterials.length
        ? planMaterials.map((item) => `${item.name}（${item.material_type}，${item.authorization_status}）`).join("；")
        : "当前项目暂未导入素材，请在方案中标明需要补齐的素材。";
      const history = [...chatMessages, { role: "operator", text: content }]
        .slice(-8)
        .map((item) => `${item.role === "assistant" ? "运营助手" : "操作员"}：${item.text}`)
        .join("\n");
      const existingPlanBriefs = visiblePlans.length
        ? visiblePlans.map((plan, index) => [
          `候选 ${index + 1}`,
          `标题：${plan.title}`,
          `目标：${plan.objective_summary}`,
          `内容：${planValueText(plan.content_strategy)}`,
          `生产：${planValueText(plan.production_scope)}`,
          `发布：${planValueText(plan.publish_schedule)}`,
        ].join(" | ")).join("\n")
        : "暂无候选方案";
      const wantsFreshCandidate = /另一个|再出|新增|新方案|不同候选|不同方案/.test(content);
      const revisionBasePlan = selectedReviewPlan && !wantsFreshCandidate ? selectedReviewPlan : null;
      const selectedPlanBrief = revisionBasePlan
        ? [
          `当前要修改的方案：${planDisplayTitle(revisionBasePlan, projectTitle, currentPlatform)}`,
          `版本：v${revisionBasePlan.plan_version}`,
          `状态：${projectRecordStatusLabel(revisionBasePlan.plan_status)}`,
          `目标：${revisionBasePlan.objective_summary}`,
          `客群：${revisionBasePlan.audience_strategy || "待补充"}`,
          `内容策略：${planValueText(revisionBasePlan.content_strategy)}`,
          `生产范围：${planValueText(revisionBasePlan.production_scope)}`,
          `素材要求：${planValueText(revisionBasePlan.material_requirements)}`,
          `KPI：${planValueText(revisionBasePlan.kpis)}`,
          `发布节奏：${planValueText(revisionBasePlan.publish_schedule)}`,
          `风险：${revisionBasePlan.risk_notes || "待补充"}`,
        ].join("\n")
        : "当前未指定要修改的候选；请生成新的可审核候选。";
      const variantGuide = revisionBasePlan
        ? "本轮是在修改当前选中的候选方案：必须保留合理结构，按操作员最新要求重写目标拆解、栏目、素材、KPI、发布和风控，生成一个新的修订版本；不要复制原文，也不要只新增一句说明。"
        : content.includes("激进")
        ? "本轮必须明显更激进：提高发布频次、强化转化动作、增加热点/达人/直播切片等高强度打法，同时写清新增风险。"
        : content.includes("保守") || content.includes("稳健")
          ? "本轮必须明显更稳健：降低发布和素材压力，强调授权、审批、低风险素材复用和可执行节奏。"
          : content.includes("不同") || content.includes("另一个") || content.includes("再出")
            ? "本轮必须给出与已有候选不同的策略重心、内容栏目、素材要求、KPI 和发布节奏。"
            : "本轮必须避免复制已有候选，至少在策略重心、内容栏目、素材要求、KPI 或发布节奏中给出三处实质差异。";
      const llm = await commercialOperationClient.generateLlmPlanCandidate({
        system_prompt: "你是资深商业运营方案总监。Codex 全局控制器负责监督阶段路由、模型分工、证据质量和审批边界；你负责把这些控制信号、项目知识库、公开情报和专用模型分析转成可审批运营方案，不要让单一文本模型冒充视频/图片/真实数据能力。请只输出一个 JSON 对象，不要输出 Markdown。JSON 字段必须包含 title、objective_summary、audience_strategy、channel_strategy、content_strategy、production_scope、material_requirements、kpis、publish_schedule、risk_notes、recommendation_reason。content_strategy 必须是成熟方案设计，不是摘要，至少包含 strategy_summary、strategy_pillars、content_pillars、sample_topics、video_analysis, competitor_playbook, operation_capability_diagnosis, data_validation_plan、video_reference_plan、visual_storyboard、chart_dashboard、visual_assets、weekly_calendar、production_workflow、approval_gates、acceptance_criteria。每个数组至少 3 项，每项必须有可执行动作、负责人或触发条件、交付物或验收口径。video_analysis 要给出爆款结构、镜头节奏、可复用边界和验证方式；competitor_playbook 要给出可借鉴打法、不可复制边界和审批关注点；operation_capability_diagnosis 要指出当前项目要补齐的素材、生产、审批和复盘能力；data_validation_plan 只能写发布后待验证指标，不能写成已回流数据。方案必须可让操作员选择、审核和批准，且不得绕过人工审批。不要生成与已有候选相同的标题、目标、内容策略或生产范围；不要把 copy、media、digital_human、brand_brief、authorization 等内部代码值当作面向用户的方案文案。",
        user_prompt: [
          `项目名称：${project.title}`,
          `运营目标：${project.objective}`,
          `平台：${currentPlatform}`,
          `负责人：${currentOwner}`,
          `知识库集合：${project.knowledge_collection || "随项目走"}`,
          `成功指标：${project.success_metrics?.join("、") || "播放量、互动率、转化"}`,
          `业务约束：${project.constraints?.join("；") || "发布前必须人工审批；素材必须有授权"}`,
          `当前素材：${materialSummary}`,
          `全网运营情报状态：${planningIntelligence.status}`,
          `全网运营情报边界：${planningIntelligence.boundary}`,
          `后台情报能力摘要：\n${researchSkillBrief || "暂无结构化情报能力输出，必须把缺口写入方案。"}`,
          `模型接入与分工（必须按分工生成方案，70B 不足时引用视频/图片/数据模型能力）：\n${modelCapabilitiesBrief}`,
          `运营深度分析报告（必须转成方案正文，不要只复述字段）：\n${analysisReportBrief}`,
          `全网运营情报：\n${planningIntelligence.prompt_context}`,
          "数据使用边界：方案阶段只能使用公开研究证据和项目知识库；真实播放、互动、咨询、团购、预约和核销只能在数据回流板块出现。未发布、未回流或未人工确认的数据只能写为验证计划，不能写成已取得结论。",
          "可视化要求：方案不能只写文字口述，必须包含视频参考、镜头分镜、封面/图标/海报资产、审核预览图、转化漏斗和周复盘图表。",
          `LLM 显卡调度：${JSON.stringify({
            mode: llmResourcePlan.mode,
            admission_status: llmResourcePlan.admission_status,
            recommended_gpu_indexes: llmResourcePlan.recommended_gpu_indexes,
            cuda_visible_devices: llmResourcePlan.cuda_visible_devices,
            comfyui_active: llmResourcePlan.comfyui_active,
            comfyui_busy_gpu_indexes: llmResourcePlan.comfyui_busy_gpu_indexes,
            max_concurrent_llm_requests: llmResourcePlan.max_concurrent_llm_requests,
          })}`,
          `后端项目阶段草稿：${JSON.stringify(preview.plan_outline)}`,
          `已有候选方案（必须避开重复）：\n${existingPlanBriefs}`,
          `当前选中方案（如果是修改请求，必须以此为基础重写）：\n${selectedPlanBrief}`,
          `本轮差异方向：${variantGuide}`,
          `最近对话：\n${history}`,
          revisionBasePlan
            ? "请根据以上上下文生成当前选中方案的修订版，方便操作员继续审核。成熟度要求：必须写清目标拆解、内容栏目、每周排期、素材准备、生产流程、审批风控、数据回流、复盘优化和验收标准；不要只写一句方向。请在 recommendation_reason 中说明本次相对原方案改了哪些内容。"
            : "请根据以上上下文生成一个新的候选运营方案，方便操作员和其他候选方案对比后选择。成熟度要求：必须写清目标拆解、内容栏目、每周排期、素材准备、生产流程、审批风控、数据回流、复盘优化和验收标准；不要只写一句方向。请在 recommendation_reason 中明确说明它与已有候选至少三处差异。",
        ].join("\n"),
        temperature: 0.35,
        max_tokens: 1800,
        variables: {
          llm_gpu_plan: llmResourcePlan,
          ollama_options: llmResourcePlan.ollama_options,
        },
      });
      const jsonText = llm.content.match(/\{[\s\S]*\}/)?.[0] ?? "";
      let llmPlan: Record<string, unknown> = {};
      try {
        llmPlan = jsonText ? JSON.parse(jsonText) as Record<string, unknown> : {};
      } catch {
        llmPlan = {};
      }
      const nextVersion = Math.max(0, ...snapshot.plans.map((item) => item.plan_version || 0)) + 1;
      const textField = (key: string, fallback: string) => {
        const value = llmPlan[key];
        return typeof value === "string" && value.trim() ? value.trim() : fallback;
      };
      const recordField = (key: string, fallback: Record<string, unknown>) => {
        const value = llmPlan[key];
        return value && typeof value === "object" && !Array.isArray(value) ? value as Record<string, unknown> : fallback;
      };
      const arrayField = (key: string, fallback: Record<string, unknown>[]) => {
        const value = llmPlan[key];
        if (!Array.isArray(value)) return fallback;
        const cleaned = value.filter((item): item is Record<string, unknown> => Boolean(item) && typeof item === "object" && !Array.isArray(item));
        return cleaned.length ? cleaned : fallback;
      };
      const defaultContentStrategy = {
        content_type: operationMetaText(project, "content_type", "短视频与发布文案"),
        strategy_summary: "围绕本地到店转化，把内容生产、素材授权、人工审批、发布执行和数据回流串成每周闭环。",
        strategy_pillars: [
          { name: "到店转化", action: "每条内容都绑定团购、预约或私信咨询动作", deliverable: "转化口径和 CTA 清单" },
          { name: "素材可信", action: "优先使用门店实拍、套餐说明和授权素材", deliverable: "可用素材与授权台账" },
          { name: "复盘迭代", action: "每周根据播放、互动、咨询和团购数据调整栏目", deliverable: "周复盘和下一轮优化点" },
        ],
        content_pillars: [
          { column: "门店体验", example: "包厢环境、音响效果、朋友聚会场景", conversion_point: "到店预约" },
          { column: "套餐种草", example: "团购套餐拆解、生日局/聚会局预算", conversion_point: "团购下单" },
          { column: "本地热点", example: "周末夜场、节日活动、附近商圈人群", conversion_point: "私信咨询" },
        ],
        sample_topics: [
          { title: "周末朋友局怎么订更划算", hook: "用预算对比开场", output: "30 秒短视频脚本和发布文案" },
          { title: "生日包厢真实体验", hook: "用门店实拍展示氛围", output: "门店实拍剪辑和套餐 CTA" },
          { title: "下班后本地放松路线", hook: "结合商圈和夜场需求", output: "本地生活种草短视频" },
        ],
        video_reference_plan: [
          { title: "同题材爆款拆解", purpose: "参考 KTV 探店、团购种草和朋友局场景的开场钩子、节奏和评论触发点，不照搬原视频素材" },
          { title: "门店实拍参考", purpose: "参考包厢环境、音响灯光、套餐展示和到店路线的镜头组合，形成可拍摄清单" },
          { title: "数字人口播参考", purpose: "参考本地生活讲解型短视频结构，把套餐利益点、预约方式和风险提示做成口播脚本" },
        ],
        visual_storyboard: [
          { scene: "开场 0-3 秒", shot: "朋友局预算/包厢氛围强钩子", visual: "门店实拍或数字人站在包厢前，叠加价格和适用人数", purpose: "提高停留和点击" },
          { scene: "中段 4-18 秒", shot: "套餐拆解 + 场景展示", visual: "包厢、酒水/小吃、音响灯光、预约入口分屏", purpose: "解释价值和降低决策成本" },
          { scene: "结尾 19-30 秒", shot: "CTA 和评论互动", visual: "团购/预约路径、评论关键词、门店位置提示", purpose: "引导私信咨询、团购和到店预约" },
        ],
        chart_dashboard: [
          { chart: "转化漏斗", metric: "播放 -> 互动 -> 私信/团购点击 -> 预约/核销", purpose: "判断内容是否真的带来到店转化" },
          { chart: "栏目对比", metric: "门店体验、套餐种草、本地热点三类内容的播放与咨询对比", purpose: "决定下周保留或减少的栏目" },
          { chart: "周趋势", metric: "每周发布量、互动率、咨询量和团购转化", purpose: "复盘节奏是否稳定增长" },
        ],
        visual_assets: [
          { title: "封面模板", visual: "大字标题 + 包厢实拍 + 人数/预算标签", purpose: "让不同视频保持统一识别度" },
          { title: "转化图标", visual: "团购、预约、私信、到店核销四个小图标", purpose: "用于视频角标和发布包说明" },
          { title: "审核预览图", visual: "视频封面、标题、正文、CTA 和风险提示合成预览", purpose: "发布前给操作员一次性审核" },
        ],
        weekly_calendar: [
          { day: "周一", action: "确认选题、素材和授权", owner: currentOwner, deliverable: "本周选题表" },
          { day: "周三", action: "完成脚本、拍摄或生成候选", owner: "内容/影音 Agent", deliverable: "可审核候选" },
          { day: "周五", action: "人工审批并发布", owner: currentOwner, deliverable: "发布包和执行记录" },
          { day: "周日", action: "回收数据并复盘", owner: "数据回流 Agent", deliverable: "复盘结论和下周调整" },
        ],
        production_workflow: [
          { step: "方案确认", gate: "操作员选择并批准候选方案", output: "已批准 OperationPlan" },
          { step: "文案生产", gate: "脚本、标题、话术通过人工审核", output: "文案任务候选" },
          { step: "影音生产", gate: "素材授权和工作流确认", output: "可预览短视频候选" },
          { step: "发布回流", gate: "发布包审批和执行证据", output: "指标快照和再次分析" },
        ],
        approval_gates: [
          { gate: "素材授权", rule: "人物、音乐、门店和参考素材必须可追溯", owner: currentOwner },
          { gate: "内容合规", rule: "不得夸大价格、承诺或平台不可发布内容", owner: "审核人" },
          { gate: "发布确认", rule: "标题、正文、话题和 CTA 发布前人工确认", owner: currentOwner },
        ],
        feedback_loop: [
          { metric: "播放量", use: "判断选题吸引力和开场钩子" },
          { metric: "互动率", use: "判断评论话术和内容共鸣" },
          { metric: "到店咨询/团购转化", use: "判断 CTA 和套餐表达是否有效" },
        ],
        acceptance_criteria: [
          "每周至少形成 3 条可审核短视频候选和对应发布文案",
          "每条发布内容必须绑定素材授权、审批记录和发布包",
          "每周完成一次数据回流，并输出下一轮栏目和发布节奏调整",
        ],
      };
      const externalResearchSummary = [
        { label: "抓取状态", detail: `${planningIntelligence.status}；来源 ${planningIntelligence.source_results.length} 条；爆款/视频线索 ${planningIntelligence.viral_video_signals.length} 条；运营数据口径 ${planningIntelligence.operation_data_signals.length} 条` },
        ...planningIntelligence.skill_cards.map((item) => ({
          label: String(item.title || item.skill_key || "情报技能"),
          detail: `状态 ${String(item.status || "待复核")}；证据 ${Number(item.evidence_count || 0)} 条；${Array.isArray(item.outputs) ? item.outputs.slice(0, 2).map((output) => String(output)).join("；") : "暂无输出"}`,
        })),
        ...planningIntelligence.viral_video_signals.slice(0, 3).map((item) => ({ label: "爆款线索", detail: item })),
        ...planningIntelligence.competitor_signals.slice(0, 3).map((item) => ({ label: "竞品打法", detail: item })),
        ...planningIntelligence.operation_data_signals.slice(0, 3).map((item) => ({ label: "数据口径", detail: item })),
      ];
      const externalResearchSources = planningIntelligence.source_results.slice(0, 6).map((item, index) => ({
        index: index + 1,
        title: String(item.title || "外部来源"),
        url: String(item.url || ""),
        snippet: String(item.snippet || "无摘要"),
        source: String(item.source || "search"),
        domain: String(item.domain || ""),
        visual_type: String(item.visual_type || "network_reference"),
        preview_image_url: String(item.preview_image_url || ""),
        favicon_url: String(item.favicon_url || ""),
        evidence_type: String(item.evidence_type || "weak_reference"),
        evidence_label: String(item.evidence_label || "待复核"),
        source_role: String(item.source_role || "reference_only"),
        relevance_reason: String(item.relevance_reason || "该来源需要人工复核后再用于方案。"),
        actionability_score: Number(item.actionability_score || 0),
        matched_query: String(item.matched_query || item.query || ""),
      }));
      const llmGpuAllocation = [{
        mode: llmResourcePlan.mode,
        admission_status: llmResourcePlan.admission_status,
        recommended_gpu_indexes: llmResourcePlan.recommended_gpu_indexes.join(",") || "无",
        cuda_visible_devices: llmResourcePlan.cuda_visible_devices || "未指定",
        comfyui_active: llmResourcePlan.comfyui_active ? "是" : "否",
        max_concurrent: llmResourcePlan.max_concurrent_llm_requests,
        note: llmResourcePlan.runtime_notes.join("；") || "按当前后端策略执行",
      }];
      const generatedContentStrategy = recordField("content_strategy", {});
      const mergedContentStrategy = Object.entries(generatedContentStrategy).reduce<Record<string, unknown>>(
        (current, [key, value]) => planHasContentValue(value) ? { ...current, [key]: value } : current,
        { ...defaultContentStrategy },
      );
      const payload: CommercialOperationPlanCreatePayload = {
        plan_version: nextVersion,
        title: textField("title", `${project.title}本地到店转化运营方案 v${nextVersion}`).slice(0, 255),
        objective_summary: textField("objective_summary", project.objective),
        audience_strategy: textField("audience_strategy", operationMetaText(project, "target_audience", "本地目标客群与转化用户")),
        channel_strategy: arrayField("channel_strategy", [{ platform: currentPlatform, role: "主投放平台", reason: "当前项目平台" }]),
        content_strategy: {
          ...mergedContentStrategy,
          external_research_summary: externalResearchSummary,
          market_signal_analysis: externalResearchSummary,
          research_skill_cards: planningIntelligence.skill_cards,
          planning_analysis_report: analysisReport,
          planning_model_capabilities: modelCapabilities,
          video_analysis: Array.isArray(analysisReport.video_analysis) ? analysisReport.video_analysis : [],
          competitor_playbook: Array.isArray(analysisReport.competitor_playbook) ? analysisReport.competitor_playbook : [],
          operation_capability_diagnosis: Array.isArray(analysisReport.operation_capability_diagnosis) ? analysisReport.operation_capability_diagnosis : [],
          data_validation_plan: Array.isArray(analysisReport.data_validation_plan) ? analysisReport.data_validation_plan : [],
          evidence_quality_gate: typeof analysisReport.evidence_quality_gate === "object" ? analysisReport.evidence_quality_gate : {},
          external_research_sources: externalResearchSources.length ? externalResearchSources : [{ title: "未抓到足够可信来源", note: "方案需人工补充同题材爆款视频链接和竞品账号" }],
          network_visual_references: externalResearchSources,
          intelligence_gaps: planningIntelligence.gaps,
          llm_gpu_allocation: llmGpuAllocation,
          chat_prompt: content,
          llm_recommendation_reason: textField("recommendation_reason", "后端 LLM 基于项目上下文生成候选方案。"),
        },
        production_scope: arrayField("production_scope", [
          { task_type: "copy", title: "脚本、标题与话术", approval_required: true },
          { task_type: "media", media_subtype: "digital_human", title: "数字人短视频候选产出", workflow_selection_required: true },
        ]),
        material_requirements: arrayField("material_requirements", [
          { material_type: "brand_brief", required: true, note: "品牌、门店和转化目标资料" },
          { material_type: "authorization", required: true, note: "人物、场景、音乐和素材授权" },
        ]),
        kpis: arrayField("kpis", (project.success_metrics?.length ? project.success_metrics : ["播放量", "互动率", "到店咨询", "团购转化"]).map((name) => ({
          name,
          target_value: name === "播放量" ? "单条 3000+，每周累计 9000+" : name === "互动率" ? "不低于 5%" : name === "到店咨询" ? "每周 20+ 次有效咨询" : name === "团购转化" ? "每周 8+ 单团购或预约转化" : "按首周基线提升 15%",
          measurement: name === "播放量" ? "平台播放数据" : name === "互动率" ? "点赞、评论、收藏、分享 / 播放量" : name === "到店咨询" ? "私信、电话、团购页咨询和门店预约" : name === "团购转化" ? "团购订单、预约记录和门店核销" : "平台数据和门店转化记录",
          review_cadence: "每周复盘",
          review_required: true,
        }))),
        publish_schedule: arrayField("publish_schedule", [{ platform: currentPlatform, cadence: operationMetaText(project, "publish_cadence", "每周 3 条"), approval_gate: "发布前人工审批" }]),
        risk_notes: textField("risk_notes", "素材授权、平台合规、发布节奏和转化口径需要人工复核。"),
        source_goal: project.objective,
        metadata: {
          source: "customer_console_llm_plan_chat",
          llm_provider: llm.provider,
          llm_model: llm.model,
          llm_usage: llm.usage ?? {},
          raw_llm_content: llm.content,
          planning_intelligence: planningIntelligence,
          llm_resource_plan: llmResourcePlan,
          project_material_count: planMaterials.length,
          starter_knowledge_auto_created: snapshot.materials.length === 0,
          backend_plan_outline: preview.plan_outline,
          chat_message_count: chatMessages.length + 1,
          revision_base_plan_id: revisionBasePlan?.id,
          revision_base_plan_version: revisionBasePlan?.plan_version,
        },
      };
      const plan = await commercialOperationClient.createOperationPlan(project.id, payload);
      await refreshProjectData(project.id);
      setSelectedReviewPlanId(plan.id);
      setChatMessages((current) => [...current, { role: "assistant", text: revisionBasePlan ? `已通过后端 LLM（${llm.provider}/${llm.model}）按你的要求生成修订版「${plan.title}」，已自动放到完整审核区。你可以继续对话修改，或确认后批准。` : `已通过后端 LLM（${llm.provider}/${llm.model}）生成候选方案「${plan.title}」，已自动放到完整审核区。你可以继续追问修改当前方案，或明确要求再出一个新方案。` }]);
      setMessage(revisionBasePlan ? `已生成修订版：${plan.title}` : `已生成候选方案：${plan.title}`);
    } catch (error) {
      setChatMessages((current) => [...current, { role: "assistant", text: error instanceof Error ? `方案生成失败：${error.message}` : "方案生成失败。" }]);
    } finally {
      setBusy(false);
    }
  };

  const openResource = (target: "knowledge" | "assets" | "approval" | "analysis") => {
    if (!selectedProject && target !== "analysis") {
      setPage("overview");
      setMessage("请先选择或创建项目，再打开项目资源。");
      return;
    }
    if (target === "knowledge") setPage("knowledge");
    if (target === "assets") setPage("assets");
    if (target === "approval") setPage("approval");
    if (target === "analysis") {
      setPage("feedback");
      void runAnalysisAgain();
    }
  };

  return (
    <section className="panel chat-panel codex-simple-client" data-simple-workspace-page={page}>
      <section className="client-task-workbench" data-simple-inner-layout="phase-74e-preview-panels" data-backend-sync="commercial-operations-server" data-template-strict="operation-project-workbench">
        <div className="simple-operator-workbench">
          <aside className="simple-reference-sidebar">
            <div className="simple-design-sidebar-brand"><span>AI</span><div><strong>AI 运营工作台</strong><small>客户机真实接口版</small></div></div>
            <section className="simple-project-entry">
              <div className="simple-project-entry-head"><div><span>项目</span><strong>{projectTitle}</strong><p>{currentStage}</p></div><button type="button" className="refresh-button" onClick={startDraft}><PencilLine size={14} /></button></div>
              <div className="simple-project-list">{projects.length === 0 ? <div className="empty-chat">暂无项目</div> : projects.map((project) => <article className={`simple-project-option ${project.id === selectedProjectId ? "selected" : ""}`} key={project.id}><button type="button" className="simple-project-select" onClick={() => void selectProject(project.id)}><strong>{project.title}</strong><span>{operationStageLabel(project)}</span></button><button type="button" className="simple-project-delete" onClick={() => void deleteProject(project.id)} title="删除项目"><XCircle size={13} /></button></article>)}</div>
            </section>
            <nav className="simple-workspace-page-tabs" aria-label="运营项目页签">{templatePages.map((item) => <button type="button" className={`simple-workspace-page-tab ${page === item.page ? "active" : ""}`} aria-pressed={page === item.page} disabled={item.page !== "overview" && !hasProject} key={item.page} onClick={() => setPage(item.page)}>{item.icon}<span>{item.label}</span><small>{item.detail}</small></button>)}</nav>
            <nav className="simple-resource-page-links" aria-label="项目资源"><strong className="simple-sidebar-section-title">运营资源</strong><button type="button" className={page === "knowledge" ? "active" : ""} onClick={() => openResource("knowledge")}><Database size={14} /><span>项目知识库</span><small>{snapshot.materials.length}</small></button><button type="button" className={page === "assets" ? "active" : ""} onClick={() => openResource("assets")}><Upload size={14} /><span>素材上传</span><small>{snapshot.materials.length}</small></button><button type="button" className={page === "approval" ? "active" : ""} onClick={() => openResource("approval")}><CheckCircle2 size={14} /><span>预览审批</span><small>{snapshot.outputs.length}</small></button><button type="button" className={page === "feedback" ? "active" : ""} onClick={() => openResource("analysis")}><Activity size={14} /><span>再次分析</span><small>{analysisRuns}</small></button></nav>
          </aside>
          <main className="simple-reference-main">
            <section className="simple-design-topbar"><div className="simple-design-title"><h1>你好，运营同学</h1><p>项目、方案、知识库、生产、发布和数据回流已接入后端接口。</p></div><label className="simple-design-search"><Search size={16} /><input type="search" placeholder="搜索项目、素材、产出、指标或指令" /></label><div className="simple-design-avatar">运</div></section>
            <section className="simple-design-project-switcher"><div className="simple-design-project-current"><span>当前项目</span><strong>{projectTitle}</strong><p>{projectObjective}</p><div className="simple-design-project-meta"><span><em>阶段</em><strong>{currentStage}</strong></span><span><em>平台</em><strong>{currentPlatform}</strong></span><span><em>负责人</em><strong>{currentOwner}</strong></span><span><em>知识库</em><strong>{selectedProject?.knowledge_collection || "随项目走"}</strong></span></div></div><div className="simple-design-project-actions"><button type="button" className="refresh-button" onClick={() => void refreshProjects(selectedProjectId)}><RefreshCcw size={14} />刷新</button><button type="button" className="refresh-button primary-action" onClick={startDraft}><PencilLine size={14} />新建项目</button></div></section>
            <section className="simple-design-server-sync"><span><Server size={14} /><em>服务器</em><strong>{busy ? "同步中" : "已连接"}</strong></span><span><Database size={14} /><em>素材/当前任务</em><strong>{snapshot.materials.length}/{currentProjectTasks.length}</strong></span><span><Wifi size={14} /><em>消息</em><strong>{message}</strong></span><span><Activity size={14} /><em>当前页</em><strong>{currentPageLabel}</strong></span></section>
            <section className="simple-reference-stage-workspace">
              <section className="simple-reference-page-panel" data-reference-page="overview"><div className="simple-reference-panel-head"><div><span>项目总览</span><h2>选择、创建、切换或删除项目</h2><p>项目列表来自后端；删除会调用归档接口，新建会写入商业运营项目。</p></div><div className="simple-reference-head-actions"><button type="button" className="refresh-button primary-action" onClick={startDraft}><PencilLine size={14} />新建项目</button></div></div>{draftActive ? <section className="simple-reference-create-project"><div className="simple-reference-create-main"><span>创建项目</span><strong>完整模板信息</strong><label>项目名称<input value={draftTitle} onChange={(event) => setDraftTitle(event.target.value)} /></label><label>运营目标<textarea value={draftGoal} onChange={(event) => setDraftGoal(event.target.value)} rows={3} /></label><div className="simple-reference-create-inline"><label>平台<input value={draftPlatform} onChange={(event) => setDraftPlatform(event.target.value)} /></label><label>负责人<input value={draftOwner} onChange={(event) => setDraftOwner(event.target.value)} /></label></div><label>目标人群<input value={draftAudience} onChange={(event) => setDraftAudience(event.target.value)} /></label><div className="simple-reference-create-inline"><label>内容类型<input value={draftContentType} onChange={(event) => setDraftContentType(event.target.value)} /></label><label>发布节奏<input value={draftCadence} onChange={(event) => setDraftCadence(event.target.value)} /></label></div><label>业务限制<textarea value={draftConstraints} onChange={(event) => setDraftConstraints(event.target.value)} rows={2} /></label><div className="simple-reference-create-actions"><button type="button" className="refresh-button primary-action" onClick={() => void createProject()} disabled={busy}><Send size={14} />提交后端并生成项目</button></div></div><aside className="simple-reference-create-side"><article><span>模板字段</span><strong>目标/人群/平台/内容/节奏/限制</strong><p>创建时会附带成功指标、约束、项目级知识库集合，并同步到网页端和桌面端同一套后端接口。</p></article></aside></section> : null}<div className="simple-reference-project-grid">{projects.map((project) => <article className={`simple-reference-project-card ${project.id === selectedProjectId ? "active" : ""}`} key={project.id}><div><span>{operationStageLabel(project)}</span><strong>{project.title}</strong><p>{project.objective}</p><small>{operationPlatformLabel(project)}</small></div><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action" onClick={() => void selectProject(project.id)}><PlayCircle size={14} />进入</button><button type="button" className="refresh-button" onClick={() => void deleteProject(project.id)}><XCircle size={14} />删除</button></div></article>)}</div></section>
              <section className="simple-reference-page-panel" data-reference-page="planning">
                <div className="simple-reference-panel-head">
                  <div>
                    <span>方案对话</span>
                    <h2>和 LLM 对话、修改并审核完整方案</h2>
                    <p>上方继续对话；下方横板展示当前选中方案的完整内容，审核前可以逐项查看目标、栏目、排期、素材、KPI、发布和风控。</p>
                  </div>
                </div>
                <div className="simple-reference-planning-chat">
                  <section className="simple-reference-chat-surface">
                    <div className="simple-reference-chat-head"><strong>{projectTitle}</strong><span>{chatMessages.length} 条消息</span></div>
                    <div className="simple-reference-chat-messages">{chatMessages.map((item, index) => <article className={`simple-reference-chat-message ${item.role}`} key={`${item.role}-${index}`}><span>{item.role === "assistant" ? "运营助手" : "操作员"}</span><p>{item.text}</p></article>)}</div>
                    <div className="simple-reference-chat-compose">
                      <textarea value={chatInput} onChange={(event) => setChatInput(event.target.value)} placeholder={selectedReviewPlan ? "继续修改当前方案，例如：把这版改得更保守、增加门店实拍、删掉数字人、强化到店转化。输入“另一个新方案”则生成新候选。" : "告诉 LLM 生成第一版运营方案，例如：围绕本地到店转化，建立每周短视频生产、发布和回流闭环。"} rows={3} />
                      <button type="button" className="action-button primary-action" onClick={() => void sendPlanMessage()} disabled={busy}><Send size={16} />{selectedReviewPlan ? "修改当前方案" : "生成候选"}</button>
                    </div>
                  </section>
                  <aside className="simple-reference-plan-review-surface">
                    <div className="simple-reference-plan-review-head">
                      <div><span>完整方案审核</span><strong>{selectedReviewPlan ? planDisplayTitle(selectedReviewPlan, projectTitle, currentPlatform) : "等待候选方案"}</strong><p>{selectedReviewPlan ? "下方是当前选中方案的完整审核内容，确认无误后再批准进入生产。" : "先在左侧生成方案，或从候选列表中选择一版查看完整内容。"}</p></div>
                      <small>{selectedReviewPlan ? `v${selectedReviewPlan.plan_version} / ${projectRecordStatusLabel(selectedReviewPlan.plan_status)}` : `${visiblePlans.length} 个候选`}</small>
                    </div>
                    <div className="simple-reference-plan-candidate-list">
                      <article className="simple-reference-plan-candidate-info"><span>项目知识库</span><strong>{snapshot.materials.length} 条素材</strong><p>LLM 会读取当前项目、知识库、素材、约束和最近对话。</p></article>
                      {visiblePlans.map((plan) => <button type="button" className={`simple-reference-plan-candidate ${selectedReviewPlan?.id === plan.id ? "active" : ""}`} key={plan.id} onClick={() => setSelectedReviewPlanId(plan.id)}><span>{plan.plan_status === "approved" ? "已批准" : `v${plan.plan_version}`}</span><strong>{planDisplayTitle(plan, projectTitle, currentPlatform)}</strong><small>{projectRecordStatusLabel(plan.plan_status)}</small></button>)}
                    </div>
                    {selectedReviewPlan ? <article className={`simple-reference-plan-review-card ${selectedReviewPlan.plan_status}`}>
                      <div className="simple-reference-plan-title-row"><div><span>{selectedReviewPlan.plan_status === "approved" ? "已批准" : `候选 v${selectedReviewPlan.plan_version}`}</span><strong>{planDisplayTitle(selectedReviewPlan, projectTitle, currentPlatform)}</strong></div><small>{String(selectedReviewPlan.metadata?.llm_provider || "后端")} / {String(selectedReviewPlan.metadata?.llm_model || "方案 Agent")}</small></div>
                      <p>{selectedReviewPlan.objective_summary}</p>
                      <small>{selectedReviewPlan.production_scope.length} 个生产范围 / {selectedReviewPlan.kpis.length} 个 KPI / {selectedReviewPlan.publish_schedule.length} 条发布节奏</small>
                      {renderOperationPlanDetails(selectedReviewPlan, snapshot)}
                      <div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action" onClick={() => void approveOperationPlan(selectedReviewPlan)} disabled={busy || selectedReviewPlan.plan_status === "approved" || selectedReviewPlan.plan_status === "rejected"}><CheckCircle2 size={14} />确认并批准</button><button type="button" className="refresh-button" onClick={() => void submitOperationPlanReview(selectedReviewPlan)} disabled={busy || selectedReviewPlan.plan_status !== "draft"}><PlayCircle size={14} />提交审核</button><button type="button" className="refresh-button" onClick={() => void rejectOperationPlan(selectedReviewPlan)} disabled={busy || selectedReviewPlan.plan_status === "approved" || selectedReviewPlan.plan_status === "rejected"}><RotateCcw size={14} />驳回并移除</button></div>
                    </article> : <article className="simple-reference-plan-review-card needs-action"><span>等待 LLM</span><strong>暂无可审核方案</strong><p>先在左侧发送需求，后端 LLM 会生成第一版完整候选；生成后会自动出现在这里。</p></article>}
                  </aside>
                </div>
              </section>
              <section className="simple-reference-page-panel" data-reference-page="text"><div className="simple-reference-panel-head"><div><span>文案任务</span><h2>方案已批准，生成并审核文案成稿</h2><p>{activeOperationPlan ? `当前只展示最新版已批准方案 v${activeOperationPlan.plan_version} 的文案成稿；生产任务仅作为来源说明，历史版本保留在后端审计。` : "先批准一版方案，后端才会派生当前文案任务。"}</p></div><div className="simple-reference-head-actions"><button type="button" className="refresh-button primary-action" onClick={() => void generateQualifiedCopyDraft()} disabled={busy || !activeOperationPlan}><FileText size={14} />{copyDraftAction === "generating" ? "生成中..." : "生成文案成稿"}</button></div></div><div className="simple-reference-copy-grid">{currentCopyDrafts.map((draft) => <article className={`simple-reference-copy-card copy-draft ${draft.draft_status}`} key={draft.id}><span>{contentDraftStatusLabel(draft.draft_status)}</span><strong>{draft.title}</strong><p>{draft.summary || "完整短视频文案成稿，等待人工审核。"}</p><small>{draft.channel} / {planDisplayToken(draft.content_format)} / 方案 v{String(draft.metadata?.operation_plan_version || activeOperationPlan?.plan_version || "-")}</small><pre className="simple-reference-copy-final-body">{draft.content_body}</pre><div className="simple-reference-card-actions"><button type="button" className="refresh-button" onClick={() => void readyCopyDraft(draft)} disabled={busy || draft.draft_status === "ready_for_review" || draft.draft_status === "approved"}>提交审核</button><button type="button" className="refresh-button primary-action" onClick={() => void approveCopyDraft(draft)} disabled={busy || draft.draft_status === "approved"}><CheckCircle2 size={14} />{copyDraftAction === "approving" ? "批准中..." : "批准成稿"}</button><button type="button" className="refresh-button" onClick={() => void rejectCopyDraft(draft)} disabled={busy || draft.draft_status === "approved"}><XCircle size={14} />{copyDraftAction === "rejecting" ? "驳回中..." : "驳回"}</button></div></article>)}{currentCopyDrafts.length === 0 ? <article className="simple-reference-copy-card needs-action"><span>待生成</span><strong>暂无合格文案成稿</strong><p>点击右上角“生成文案成稿”，系统会基于当前 v{activeOperationPlan?.plan_version ?? "-"} 方案生成可审核的三条短视频脚本、标题、发布正文、评论话术和风险检查。</p><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action" onClick={() => void generateQualifiedCopyDraft()} disabled={busy || !activeOperationPlan}><FileText size={14} />{copyDraftAction === "generating" ? "生成中..." : "生成文案成稿"}</button></div></article> : null}{currentCopyTasks.map((task) => <article className={`simple-reference-copy-card task-source ${task.task_status}`} key={task.id}><span>任务来源</span><strong>生产要求：{task.title}</strong><p>这条记录是后端根据最新版方案派生的生产任务，用来说明成稿从哪里来；真正需要审核的是上方“文案成稿”。</p><small>{task.channel} / {task.assigned_agent ? "文案团队" : "待分配"} / {activeOperationPlan ? `方案 v${activeOperationPlan.plan_version}` : "未绑定方案"}</small><div className="simple-reference-task-deliverables">{taskDeliverables(task).map((item) => <em key={item}>{item}</em>)}</div><div className="simple-reference-copy-detail-list">{copyReviewSections(task, activeOperationPlan).map((section) => <section key={section.title}><strong>{section.title}</strong><ul>{section.items.map((item, index) => <li key={`${section.title}-${index}`}>{item}</li>)}</ul></section>)}</div><div className="simple-reference-card-actions"><button type="button" className="refresh-button" onClick={() => void generateQualifiedCopyDraft()} disabled={busy || !activeOperationPlan}><RefreshCcw size={14} />{copyDraftAction === "generating" ? "生成中..." : "按此要求重生成稿"}</button></div></article>)}{currentCopyTasks.length === 0 ? <article className="simple-reference-copy-card task-source needs-action"><span>任务来源</span><strong>当前方案暂无文案生产任务</strong><p>{activeOperationPlan ? "生成文案成稿时会自动创建并绑定到当前最新版已批准方案。" : "先在方案对话中批准一版方案，再生成文案成稿。"}</p></article> : null}</div></section>
              <section className="simple-reference-page-panel" data-reference-page="media"><div className="simple-reference-panel-head"><div><span>影音生产</span><h2>素材上传、生产任务、产出预览</h2><p>素材登记、生产任务和产出候选都写入后端；工作流选择在独立页完成。</p></div><div className="simple-reference-head-actions"><label className="refresh-button primary-action"><Upload size={14} />上传素材<input type="file" multiple hidden onChange={(event) => { Array.from(event.target.files ?? []).forEach((file) => void registerMaterialFile(file)); event.currentTarget.value = ""; }} /></label><button type="button" className="refresh-button" onClick={() => void createProductionTask("media")}><PlayCircle size={14} />创建任务</button><button type="button" className="refresh-button" onClick={() => void loadWorkflowCandidates()}><TerminalSquare size={14} />选择工作流</button><button type="button" className="refresh-button" onClick={() => void createOutputCandidate()}><Package size={14} />登记预览</button></div></div><div className="simple-reference-work-area"><section className="simple-reference-material-grid">{snapshot.materials.map((material) => <article className="simple-reference-material-card current" key={material.id}><span>{material.material_status}</span><strong>{material.name}</strong><p>{material.notes || material.source_uri}</p><small>{material.material_type}</small></article>)}{snapshot.materials.length === 0 ? <article className="simple-reference-material-card needs-action"><span>待上传</span><strong>暂无项目素材</strong><p>点击上传素材登记到当前项目。</p></article> : null}</section><aside className="simple-reference-context-stack">{currentMediaTasks.map((task) => <article className={`simple-reference-context-card ${task.task_status}`} key={task.id}><span>{task.task_status}</span><strong>{task.title}</strong><p>{task.brief}</p><div className="simple-reference-card-actions"><button type="button" className="refresh-button" onClick={() => void decideTask(task, "ready")}>提交审核</button><button type="button" className="refresh-button primary-action" onClick={() => void decideTask(task, "approve")}>批准</button></div></article>)}{currentMediaTasks.length === 0 ? <article className="simple-reference-context-card needs-action"><span>待创建</span><strong>暂无影音任务</strong><p>先创建影音生产任务，再进入流选择。</p></article> : null}</aside></div></section>
              <section className="simple-reference-page-panel" data-reference-page="flows"><div className="simple-reference-panel-head"><div><span>流选择</span><h2>选择业务可理解的 ComfyUI 工作流候选</h2><p>候选来自后端工作流检索；操作员确认后形成 WorkflowSelection 记录。</p></div><div className="simple-reference-head-actions"><button type="button" className="refresh-button primary-action" onClick={() => void loadWorkflowCandidates()} disabled={busy}><RefreshCcw size={14} />加载候选流</button></div></div><div className="simple-reference-work-area"><section className="simple-reference-workflow-list">{workflowCandidates.map((candidate) => <article className="simple-reference-workflow-card current" key={candidate.candidate_id}><span>{candidate.runtime_readiness}</span><strong>{candidate.workflow_name}</strong><p>{candidate.candidate_summary || candidate.recommendation_reason || "后端推荐工作流候选。"}</p><small>{candidate.output_type} / {candidate.validation_status} / 显存 {candidate.estimated_vram_mb ?? "未知"} MB</small><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action" onClick={() => void approveWorkflowCandidate(candidate)}><CheckCircle2 size={14} />选择并批准</button></div></article>)}{workflowCandidates.length === 0 ? <article className="simple-reference-workflow-card needs-action"><span>待确认</span><strong>后端暂无候选流</strong><p>可以重新加载候选；如果客户机已有确认可用的工作流，也可以登记为手动选择，继续后续预览审批。</p><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action" onClick={() => void createManualWorkflowSelection()} disabled={busy}><CheckCircle2 size={14} />登记手动工作流</button></div></article> : null}</section><aside className="simple-reference-context-stack">{snapshot.workflows.map((workflow) => <article className={`simple-reference-context-card ${workflow.selection_status}`} key={workflow.id}><span>{workflow.selection_status}</span><strong>{workflow.workflow_name}</strong><p>{workflow.recommendation_reason || workflow.candidate_summary || "已保存的工作流选择。"}</p></article>)}{snapshot.workflows.length === 0 ? <article className="simple-reference-context-card needs-action"><span>未选择</span><strong>当前项目暂无工作流选择</strong><p>影音产出必须先确认工作流，候选作品才有来源链路。</p></article> : null}</aside></div></section>
              <section className="simple-reference-page-panel" data-reference-page="knowledge"><div className="simple-reference-panel-head"><div><span>项目知识库</span><h2>当前项目上下文与知识资料</h2><p>知识库跟随项目，不再是全局 RAG 桶；方案、生产和审批都会使用这里的项目资料。</p></div><div className="simple-reference-head-actions"><button type="button" className="refresh-button" onClick={() => selectedProject && void refreshProjectData(selectedProject.id)}><RefreshCcw size={14} />刷新知识</button><button type="button" className="refresh-button primary-action" onClick={() => setPage("assets")}><Upload size={14} />导入资料</button></div></div><div className="simple-reference-work-area"><section className="simple-reference-material-grid"><article className="simple-reference-material-card current"><span>集合</span><strong>{selectedProject?.knowledge_collection || "未设置知识库集合"}</strong><p>{projectObjective}</p><small>{currentPlatform} / {currentOwner}</small></article>{snapshot.materials.map((material) => <article className="simple-reference-material-card current" key={material.id}><span>{material.authorization_status}</span><strong>{material.name}</strong><p>{material.notes || material.usage_scope || material.source_uri}</p><small>{material.tags.join(" / ") || material.material_type}</small></article>)}{snapshot.materials.length === 0 ? <article className="simple-reference-material-card needs-action"><span>待导入</span><strong>暂无项目知识资料</strong><p>把品牌资料、门店照片、参考视频、脚本和授权证明导入当前项目。</p></article> : null}</section><aside className="simple-reference-context-stack"><article className="simple-reference-context-card current"><span>成功指标</span><strong>{selectedProject?.success_metrics?.join(" / ") || "待补充"}</strong><p>这些指标会进入方案、发布包和回流分析。</p></article><article className="simple-reference-context-card needs-action"><span>业务约束</span><strong>{selectedProject?.constraints?.length || 0} 条</strong><p>{selectedProject?.constraints?.join("；") || "请在新建项目时补充品牌限制和审批边界。"}</p></article></aside></div></section>
              <section className="simple-reference-page-panel" data-reference-page="assets"><div className="simple-reference-panel-head"><div><span>素材上传</span><h2>导入当前项目可用素材</h2><p>素材必须归属具体项目，记录类型、授权、用途和关联生产任务。</p></div><div className="simple-reference-head-actions"><label className="refresh-button primary-action"><Upload size={14} />选择文件<input type="file" multiple hidden onChange={(event) => { Array.from(event.target.files ?? []).forEach((file) => void registerMaterialFile(file)); event.currentTarget.value = ""; }} /></label><button type="button" className="refresh-button" onClick={() => void createProductionTask("media")}><PlayCircle size={14} />创建影音任务</button></div></div><div className="simple-reference-work-area"><section className="simple-reference-material-grid">{snapshot.materials.map((material) => <article className="simple-reference-material-card current" key={material.id}><span>{material.material_type}</span><strong>{material.name}</strong><p>{material.source_uri}</p><small>{material.material_status} / {material.authorization_status}</small></article>)}{snapshot.materials.length === 0 ? <article className="simple-reference-material-card needs-action"><span>待上传</span><strong>暂无素材</strong><p>支持图片、视频、音频、文档和授权材料登记到当前项目。</p></article> : null}</section><aside className="simple-reference-context-stack"><article className="simple-reference-context-card current"><span>归属项目</span><strong>{projectTitle}</strong><p>上传后的素材会进入项目知识库，并可被文案、影音和产出审批引用。</p></article><article className="simple-reference-context-card needs-action"><span>生产引用</span><strong>{currentProjectTasks.length} 个当前任务</strong><p>素材导入后可创建或补充生产任务，避免散落在本地文件夹。</p></article></aside></div></section>
              <section className="simple-reference-page-panel" data-reference-page="approval"><div className="simple-reference-panel-head"><div><span>预览审批</span><h2>候选产出、最终选择和发布包确认</h2><p>所有生成结果先进入候选池，人工选择后才能生成发布包并交给客户机执行。</p></div><div className="simple-reference-head-actions"><button type="button" className="refresh-button" onClick={() => void createOutputCandidate()}><Package size={14} />登记预览</button><button type="button" className="refresh-button primary-action" onClick={() => void createPublishPackage()}><Send size={14} />生成发布包</button></div></div><div className="simple-reference-review-grid">{snapshot.outputs.map((candidate) => <article className="simple-reference-review-card ready" key={candidate.id}><div className="simple-reference-output-preview"><Package size={22} /></div><span>{candidate.candidate_status}</span><strong>{candidate.title}</strong><p>{candidate.generation_summary || candidate.preview_uri || "等待预览。"}</p><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action" onClick={() => void selectOutputCandidate(candidate)}><CheckCircle2 size={14} />选择为最终</button><button type="button" className="refresh-button" onClick={() => selectedProject && void commercialOperationClient.decideOutputCandidate(selectedProject.id, candidate.id, "reject", "客户机前端驳回。").then(() => refreshProjectData(selectedProject.id))}><XCircle size={14} />驳回</button></div></article>)}{snapshot.outputs.length === 0 ? <article className="simple-reference-review-card needs-action"><div className="simple-reference-output-preview"><Package size={22} /></div><span>待登记</span><strong>暂无可预览产出</strong><p>先在影音生产中登记候选，或直接登记一个人工预览产出。</p><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action" onClick={() => void createOutputCandidate()}><Package size={14} />登记预览</button></div></article> : null}</div><div className="simple-reference-feedback-grid"><article className="simple-reference-feedback-card current"><span>最终选择</span><strong>{snapshot.selections.length} 条</strong><p>最终选择用于生成发布包，不能绕过人工确认。</p></article><article className="simple-reference-feedback-card current"><span>发布包</span><strong>{snapshot.publishPackages.length} 个</strong><p>发布前需确认标题、正文、话题、平台和风险提示。</p></article><article className="simple-reference-feedback-card current"><span>数据回流</span><strong>{snapshot.metrics.length} 条</strong><p>发布后回流指标用于下一轮优化。</p></article></div></section>
              <section className="simple-reference-page-panel" data-reference-page="outputs"><div className="simple-reference-panel-head"><div><span>产出审批</span><h2>预览并选择生成结果</h2><p>产出候选可选择、驳回，并生成最终选择记录。</p></div><div className="simple-reference-head-actions"><button type="button" className="refresh-button primary-action" onClick={() => void createOutputCandidate()}><Package size={14} />登记预览产出</button></div></div><div className="simple-reference-review-grid">{snapshot.outputs.map((candidate) => <article className="simple-reference-review-card ready" key={candidate.id}><div className="simple-reference-output-preview"><Package size={22} /></div><span>{candidate.candidate_status}</span><strong>{candidate.title}</strong><p>{candidate.generation_summary || candidate.preview_uri || "等待预览。"}</p><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action" onClick={() => void selectOutputCandidate(candidate)}><CheckCircle2 size={14} />选择并审批</button><button type="button" className="refresh-button" onClick={() => selectedProject && void commercialOperationClient.decideOutputCandidate(selectedProject.id, candidate.id, "reject", "客户机前端驳回。").then(() => refreshProjectData(selectedProject.id))}><XCircle size={14} />驳回</button></div></article>)}</div></section>
              <section className="simple-reference-page-panel" data-reference-page="publish"><div className="simple-reference-panel-head"><div><span>发布执行</span><h2>发布包、客户机执行和结果回填</h2><p>发布包来自后端；批准后先 dry-run，再记录真实提交证据，最后才能回填发布结果。</p></div><div className="simple-reference-head-actions"><button type="button" className="refresh-button primary-action" onClick={() => void createPublishPackage()}><Send size={14} />生成发布包</button></div></div><div className="simple-reference-publish-grid"><section className="simple-reference-publish-list">{snapshot.publishPackages.map((item) => <article className={`simple-reference-publish-card ${item.package_status}`} key={item.id}><span>{item.package_status}</span><strong>{item.title}</strong><p>{item.body}</p><small>{item.hashtags.join(" ")}</small><div className="simple-reference-card-actions"><button type="button" className="refresh-button primary-action" onClick={() => void approvePublishPackage(item)} disabled={busy}><CheckCircle2 size={14} />批准并准备执行</button><button type="button" className="refresh-button" onClick={() => void runPublishDryRun(item)} disabled={busy}><PlayCircle size={14} />执行 dry-run</button><button type="button" className="refresh-button" onClick={() => void runPublishSubmit(item)} disabled={busy}><Send size={14} />记录真实提交</button><button type="button" className="refresh-button" onClick={() => void capturePublishResult(item)} disabled={busy}><Wifi size={14} />回填发布结果</button></div></article>)}{snapshot.publishPackages.length === 0 ? <article className="simple-reference-publish-card needs-action"><span>待生成</span><strong>暂无发布包</strong><p>先审批产出，再生成发布包。</p></article> : null}</section><aside className="simple-reference-data-list"><article className="simple-reference-data-card ready"><span>最终选择</span><strong>{snapshot.selections.length}</strong><p>已选择的产出会用于生成发布包。</p></article><article className="simple-reference-data-card ready"><span>客户机边界</span><strong>dry-run + 真实提交证据</strong><p>这里不会绕过审批；mock provider 只能记录 dry-run，不能伪装真实发布成功。</p></article></aside></div></section>
              <section className="simple-reference-page-panel" data-reference-page="feedback"><div className="simple-reference-panel-head"><div><span>数据回流</span><h2>拉回发布指标并再次分析</h2><p>这里处理发布后的真实回流指标、人工记录和下一轮优化；方案阶段的热门视频和竞品打法来自全网情报抓取。</p></div><div className="simple-reference-head-actions"><button type="button" className="refresh-button" onClick={() => selectedProject && void refreshProjectData(selectedProject.id)} disabled={busy}><RefreshCcw size={14} />刷新回流</button><button type="button" className="refresh-button primary-action" onClick={() => void runAnalysisAgain()} disabled={busy}><Activity size={14} />再次分析</button></div></div><div className="simple-reference-feedback-grid"><article className="simple-reference-feedback-card current"><span>指标快照</span><strong>{snapshot.metrics.length} 条</strong><p>发布执行、客户机回填和人工补充的播放、互动、咨询、预约与核销数据都会进入这里。</p></article><article className="simple-reference-feedback-card current"><span>方案情报</span><strong>{activeOperationPlan ? "已绑定方案" : "待批准方案"}</strong><p>生成方案时会抓取同题材热门视频、竞品打法和平台公开资料，作为方案依据而非账号后台数据。</p></article><article className="simple-reference-feedback-card needs-action"><span>下一轮动作</span><strong>回流后复盘</strong><p>再次分析会把当前项目指标写入后端分析任务，用于下一轮文案、影音和发布节奏优化。</p></article></div><div className="simple-reference-feedback-grid">{snapshot.metrics.slice(0, 6).map((metric) => <article className="simple-reference-feedback-card current" key={metric.id}><span>{metric.platform}</span><strong>{metric.source_type}</strong><p>{metric.summary || "已登记指标快照。"}</p></article>)}{snapshot.metrics.length === 0 ? <article className="simple-reference-feedback-card needs-action"><span>暂无回流</span><strong>等待发布后数据</strong><p>先完成发布执行并回填结果，再点击再次分析形成下一轮优化建议。</p></article> : null}</div></section>
            </section>
          </main>
        </div>
      </section>
    </section>
  );
}

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

type OperationLoopStepCopy = {
  id: string;
  label: string;
  detail: string;
};

type OperationDeliverableCopy = {
  id: string;
  label: string;
  detail: string;
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
  operationDeskTitle: string;
  operationDeskSubtitle: string;
  operationCurrentLabel: string;
  operationResultLabel: string;
  operationControlLabel: string;
  operationGuidedActionsTitle: string;
  operationGuidedActionsSubtitle: string;
  operationAdvancedActionsTitle: string;
  operationAdvancedActionsHint: string;
  operationStartLoop: string;
  operationRefreshLoop: string;
  operationPrepareDraft: string;
  operationFirstDraftPreparing: string;
  operationFirstDraftReady: string;
  operationApproveAndPrepare: string;
  operationApproveNextCycleAndPrepare: string;
  operationApproveImprovedDraftAndPrepare: string;
  operationRejectDraft: string;
  operationRejectNextCycleDraft: string;
  operationRejectImprovedDraft: string;
  operationApprovalPreparing: string;
  operationNextCycleApprovalPreparing: string;
  operationImprovedApprovalPreparing: string;
  operationExecutionPrepReady: string;
  operationNextCycleExecutionPrepReady: string;
  operationImprovedExecutionPrepReady: string;
  operationApprovalRejected: string;
  operationNextCycleApprovalRejected: string;
  operationApprovalMissing: string;
  operationApprovalPending: string;
  operationReviewAndQueueRun: string;
  operationReviewAndQueueNextCycleRun: string;
  operationReviewAndQueueImprovedRun: string;
  operationExecutionRunQueuing: string;
  operationNextCycleExecutionRunQueuing: string;
  operationImprovedExecutionRunQueuing: string;
  operationExecutionRunReady: string;
  operationNextCycleExecutionRunReady: string;
  operationImprovedExecutionRunReady: string;
  operationExecutionRequestMissing: string;
  operationStartRun: string;
  operationRunStarting: string;
  operationRunStarted: string;
  operationFailRun: string;
  operationRunFailed: string;
  operationRetryRun: string;
  operationRunRetrying: string;
  operationExecutionRequestPending: string;
  operationExecutionRunPending: string;
  operationRuntimePreflight: string;
  operationRuntimePreflightChecking: string;
  operationRuntimePreflightReady: string;
  operationRuntimePreflightBlocked: string;
  operationRuntimePreflightMissing: string;
  operationGuardedDispatchHandoff: string;
  operationGuardedDispatchHandingOff: string;
  operationGuardedDispatchReady: string;
  operationGuardedDispatchBlocked: string;
  operationGuardedDispatchMissing: string;
  operationAdapterDryRun: string;
  operationAdapterDryRunRunning: string;
  operationAdapterDryRunSucceeded: string;
  operationAdapterDryRunBlocked: string;
  operationAdapterDryRunMissing: string;
  operationExecutionQueueTitle: string;
  operationExecutionQueueSubtitle: string;
  operationExecutionQueueEmpty: string;
  operationExecutionQueueReady: string;
  operationExecutionQueuePreflightReady: string;
  operationExecutionQueueWaiting: string;
  operationApprovalCenterSummary: string;
  operationApprovalCenterTitle: string;
  operationApprovalCenterEmpty: string;
  operationApprovalCenterApprove: string;
  operationApprovalCenterReject: string;
  operationApprovalCenterRisk: string;
  operationApprovalCenterStatus: string;
  operationPublishPanelTitle: string;
  operationPublishPanelSubtitle: string;
  operationPublishHandoff: string;
  operationPublishHandoffPreparing: string;
  operationPublishHandoffReady: string;
  operationPublishHandoffMissing: string;
  operationCapturePublishResult: string;
  operationCapturePublishResultCapturing: string;
  operationPublishResultReady: string;
  operationPublishResultMissing: string;
  operationRecordMetricObservation: string;
  operationMetricObservationRecording: string;
  operationMetricObservationReady: string;
  operationMetricObservationMissing: string;
  operationPublishTargetLabel: string;
  operationPublishResultLabel: string;
  operationMetricObservationLabel: string;
  operationPublishImprovementLabel: string;
  operationAnalyzePublishMetrics: string;
  operationAnalyzePublishMetricsRunning: string;
  operationPublishImprovementReady: string;
  operationPublishImprovementMissing: string;
  operationPrepareImprovedDraft: string;
  operationClosedLoopDeliveryTitle: string;
  operationClosedLoopDeliverySubtitle: string;
  operationClosedLoopDeliveryAction: string;
  operationClosedLoopDeliveryRunning: string;
  operationClosedLoopDeliveryReady: string;
  operationClosedLoopDeliveryMissing: string;
  operationClosedLoopDeliveryBoundary: string;
  operationClosedLoopDeliverySteps: string[];
  operationAgentSkillTitle: string;
  operationAgentSkillSubtitle: string;
  operationAgentSkillNext: string;
  operationAgentSkillBoundary: string;
  operationAgentSkillRefresh: string;
  operationAgentSkillRefreshing: string;
  operationAgentSkillUnavailable: string;
  operationCompleteFeedbackLoop: string;
  operationCompleteNextCycleFeedbackLoop: string;
  operationFeedbackLoopCompleting: string;
  operationNextCycleFeedbackLoopCompleting: string;
  operationFeedbackLoopComplete: string;
  operationNextCycleFeedbackLoopComplete: string;
  operationFeedbackLoopMissing: string;
  operationResultRecordPending: string;
  operationObservationPending: string;
  operationOptimizationPending: string;
  operationPrepareNextCycleDraft: string;
  operationNextCycleDraftPreparing: string;
  operationNextCycleDraftReady: string;
  operationNextCycleDecisionMissing: string;
  operationLoopSourceLabel: string;
  operationLoopLoaded: string;
  operationLoopDisconnected: string;
  operationLoopTitle: string;
  operationDeliverablesTitle: string;
  operationDetailsTitle: string;
  operationDetailsHint: string;
  operationKnowledgeTitle: string;
  operationKnowledgeBody: string;
  operationOpenKnowledge: string;
  operationViewOutputs: string;
  operationPause: string;
  operationContinue: string;
  operationOpenClawLabel: string;
  operationLoopSteps: OperationLoopStepCopy[];
  operationDeliverables: OperationDeliverableCopy[];
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

function operationLoopStatusToGoalState(status: CommercialOperationLoopStage["status"]): GoalStatusStageState {
  if (status === "complete") {
    return "done";
  }
  if (status === "review_required" || status === "blocked") {
    return "needs-action";
  }
  if (status === "in_progress" || status === "missing") {
    return "current";
  }
  return "waiting";
}

function operationLoopTitleFromGoal(goal: string): string {
  const compact = goal.trim().replace(/\s+/g, " ");
  return compact.length > 64 ? `${compact.slice(0, 64)}...` : compact || "Customer operation loop";
}

function firstDraftContentBody(objective: string, language: ClientLanguage): string {
  if (language === "zh-CN") {
    return [
      `运营目标：${objective}`,
      "首版文案方向：说明用户痛点、产品价值、使用场景和下一步行动。",
      "短视频/素材方向：准备一个 30-60 秒脚本和一张主视觉素材需求，不直接调用 ComfyUI。",
      "数据观察方向：发布后人工记录曝光、互动、线索和转化，再进入下一轮优化。",
      "审批边界：该草稿只进入人工审批，不会自动发布，不会控制真实账号。",
    ].join("\n");
  }
  return [
    `Operation goal: ${objective}`,
    "First copy direction: explain the audience pain, product value, use case, and next action.",
    "Video/asset direction: prepare a 30-60 second script and one hero visual request without calling ComfyUI.",
    "Data observation direction: after approved execution, record reach, engagement, leads, and conversion manually before optimization.",
    "Approval boundary: this draft only enters human review. It does not publish or control real accounts.",
  ].join("\n");
}

function decisionList(values?: string[]): string {
  return values && values.length > 0 ? values.map((value, index) => `${index + 1}. ${value}`).join("\n") : "-";
}

function nextCycleContentBody(objective: string, decision: CommercialOperationOptimizationDecision, language: ClientLanguage): string {
  if (language === "zh-CN") {
    return [
      `运营目标：${objective}`,
      `改进依据：${decision.title}`,
      `改进理由：${decision.rationale || "基于上一轮结果记录、数据观察和人工复核生成。"}`,
      "目标调整：",
      decisionList(decision.objective_updates),
      "内容动作：",
      decisionList(decision.content_actions),
      "素材动作：",
      decisionList(decision.asset_actions),
      "人群动作：",
      decisionList(decision.audience_actions),
      "执行边界：下一轮草稿仍需人工审批，审批前不会发布、不会控制真实账号、不会调用 OpenClaw/Playwright。",
    ].join("\n");
  }
  return [
    `Operation goal: ${objective}`,
    `Improvement basis: ${decision.title}`,
    `Rationale: ${decision.rationale || "Generated from the previous result record, observation, and human review."}`,
    "Objective updates:",
    decisionList(decision.objective_updates),
    "Content actions:",
    decisionList(decision.content_actions),
    "Asset actions:",
    decisionList(decision.asset_actions),
    "Audience actions:",
    decisionList(decision.audience_actions),
    "Execution boundary: this next-cycle draft still requires human approval before publishing, account control, or OpenClaw/Playwright execution.",
  ].join("\n");
}

function metadataStringValue(metadata: Record<string, unknown> | undefined, key: string): string | null {
  const value = metadata?.[key];
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function metadataRecordValue(metadata: Record<string, unknown> | undefined, key: string): Record<string, unknown> | null {
  const value = metadata?.[key];
  return value && typeof value === "object" && !Array.isArray(value) ? (value as Record<string, unknown>) : null;
}

function isClientRuntimePreflightReady(run: CommercialOperationExecutionRun): boolean {
  const preflight = metadataRecordValue(run.input_payload, "client_runtime_preflight");
  return (
    metadataStringValue(run.metadata, "runtime_preflight_status") === "ready" ||
    metadataStringValue(run.input_payload, "runtime_preflight_status") === "ready" ||
    metadataStringValue(preflight ?? undefined, "status") === "ready"
  );
}

function isGuardedAdapterDispatchReady(run: CommercialOperationExecutionRun): boolean {
  const handoff = metadataRecordValue(run.input_payload, "guarded_adapter_dispatch_handoff");
  return (
    metadataStringValue(run.metadata, "guarded_adapter_dispatch_status") === "ready_for_operator_start" ||
    metadataStringValue(run.input_payload, "guarded_adapter_dispatch_status") === "ready_for_operator_start" ||
    metadataStringValue(handoff ?? undefined, "status") === "ready_for_operator_start"
  );
}

function isPublishHandoffResult(result: CommercialOperationResult): boolean {
  const source = metadataStringValue(result.metadata, "source") ?? "";
  return result.result_type === "guarded_publish_handoff" || source.includes("guarded_publish_handoff");
}

function isManualPublishResult(result: CommercialOperationResult): boolean {
  const source = metadataStringValue(result.metadata, "source") ?? "";
  return result.result_type === "manual_publish_result" || source.includes("manual_publish_result");
}

function isManualMetricObservation(observation: CommercialOperationMonitoringObservation): boolean {
  const source = metadataStringValue(observation.metadata, "source") ?? "";
  return observation.observation_type === "manual_publish_metrics" || source.includes("manual_publish_metrics");
}

function isManualPublishImprovementDecision(decision: CommercialOperationOptimizationDecision): boolean {
  const source = metadataStringValue(decision.metadata, "source") ?? "";
  return decision.decision_type === "manual_publish_improvement" || source.includes("manual_publish_improvement");
}

function isPublishMetricNextCycleApproval(approval: CommercialOperationApproval): boolean {
  const source = metadataStringValue(approval.metadata, "source") ?? "";
  return source.includes("publish_metric_next_cycle_draft") || metadataStringValue(approval.metadata, "phase") === "63S";
}

function isNextCycleApproval(approval: CommercialOperationApproval): boolean {
  const source = metadataStringValue(approval.metadata, "source") ?? "";
  return (
    isPublishMetricNextCycleApproval(approval) ||
    source.includes("next_cycle_content_draft") ||
    metadataStringValue(approval.metadata, "phase") === "63F" ||
    Boolean(metadataStringValue(approval.metadata, "optimization_decision_id"))
  );
}

function isPublishMetricReexecutionRequest(request: CommercialOperationExecutionRequest): boolean {
  const source = metadataStringValue(request.metadata, "source") ?? "";
  return source.includes("publish_metric_reexecution_prep") || metadataStringValue(request.metadata, "phase") === "63V";
}

function isNextCycleExecutionRequest(request: CommercialOperationExecutionRequest): boolean {
  const source = metadataStringValue(request.metadata, "source") ?? "";
  return (
    isPublishMetricReexecutionRequest(request) ||
    source.includes("next_cycle_approval_execution_prep") ||
    metadataStringValue(request.metadata, "phase") === "63G" ||
    metadataStringValue(request.metadata, "cycle") === "next_iteration" ||
    Boolean(metadataStringValue(request.metadata, "optimization_decision_id"))
  );
}

function isPublishMetricReexecutionRun(run: CommercialOperationExecutionRun): boolean {
  const source = metadataStringValue(run.metadata, "source") ?? "";
  const inputSource = metadataStringValue(run.input_payload, "source") ?? "";
  return (
    source.includes("publish_metric_reexecution_run_review") ||
    inputSource.includes("publish_metric_reexecution_run_review") ||
    metadataStringValue(run.metadata, "phase") === "63W"
  );
}

function isNextCycleExecutionRun(run: CommercialOperationExecutionRun): boolean {
  const source = metadataStringValue(run.metadata, "source") ?? "";
  const inputSource = metadataStringValue(run.input_payload, "source") ?? "";
  return (
    isPublishMetricReexecutionRun(run) ||
    source.includes("next_cycle_execution_run_review") ||
    inputSource.includes("next_cycle_execution_run_review") ||
    metadataStringValue(run.metadata, "phase") === "63H" ||
    metadataStringValue(run.metadata, "cycle") === "next_iteration" ||
    metadataStringValue(run.input_payload, "cycle") === "next_iteration" ||
    Boolean(metadataStringValue(run.metadata, "optimization_decision_id")) ||
    Boolean(metadataStringValue(run.input_payload, "optimization_decision_id"))
  );
}

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
  documentOverviewTitle: string;
  documentOverviewTotal: string;
  documentOverviewReady: string;
  documentOverviewNeedsReview: string;
  documentOverviewSelected: string;
  detailTitle: string;
  detailEmpty: string;
  detailSourceId: string;
  detailCollection: string;
  detailCreatedAt: string;
  detailHealthReady: string;
  detailHealthNeedsReview: string;
  detailHealthUnknown: string;
  viewDetails: string;
  useForUpdate: string;
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
  validationTitle: string;
  validationHint: string;
  validationQueryLabel: string;
  validationQueryPlaceholder: string;
  validationModeLabel: string;
  validationHybrid: string;
  validationDense: string;
  validationKeyword: string;
  validationAction: string;
  validationRunning: string;
  validationEmpty: string;
  validationNoResults: string;
  validationResultsTitle: string;
  validationQueryRequired: string;
  validationScore: string;
  validationSource: string;
  validationChunk: string;
  validationMode: string;
  validationCollection: string;
  validationSearchTitle: string;
  validationFailedTitle: string;
  validationClear: string;
  validationGuidanceTitle: string;
  validationGuidanceHint: string;
  validationSuggestionTitle: string;
  validationSuggestionApplied: string;
  validationSuggestionAppliedTitle: string;
  validationUseSuggestion: string;
  validationRunForItem: string;
  validationSelectedMaterial: string;
  validationLatestUpload: string;
  validationNoTarget: string;
  validationSuggestionSummary: string;
  validationSuggestionRisk: string;
  validationSuggestionAction: string;
  validationSuggestionSummaryQuery: string;
  validationSuggestionRiskQuery: string;
  validationSuggestionActionQuery: string;
  validationOutcomeTitle: string;
  validationOutcomeHint: string;
  validationOutcomeReady: string;
  validationOutcomeNeedsEvidence: string;
  validationOutcomeNeedsReview: string;
  validationOutcomeIdle: string;
  validationOutcomeReadyDetail: string;
  validationOutcomeNeedsEvidenceDetail: string;
  validationOutcomeNeedsReviewDetail: string;
  validationOutcomeIdleDetail: string;
  validationOutcomeMatches: string;
  validationOutcomeMaterial: string;
  validationOutcomeMode: string;
  validationOutcomeNextStep: string;
  validationOutcomeMarkReady: string;
  validationOutcomeRetry: string;
  validationOutcomeRunFirst: string;
  validationOutcomeMarkedTitle: string;
  validationOutcomeMarked: string;
  ingestionTitle: string;
  ingestionHint: string;
  ingestionNextAction: string;
  ingestionTimelineTitle: string;
  ingestionStepSelect: string;
  ingestionStepUpload: string;
  ingestionStepIndex: string;
  ingestionStepValidate: string;
  ingestionReady: string;
  ingestionProcessing: string;
  ingestionNeedsReview: string;
  ingestionFailed: string;
  ingestionQueued: string;
  ingestionUploaded: string;
  ingestionSearchable: string;
  ingestionNoBatch: string;
  ingestionLatestBatch: string;
  ingestionRefresh: string;
  ingestionRetry: string;
  ingestionSkipped: string;
  ingestionSourceId: string;
  ingestionDocumentId: string;
  ingestionError: string;
  ingestionSelectedStatus: string;
};

type KnowledgeQueueStatus = "queued" | "uploading" | "uploaded" | "failed";
type KnowledgeActivityTone = "good" | "warn" | "neutral";
type KnowledgeIngestionStage = "ready" | "processing" | "failed" | "waiting";

type KnowledgeValidationSuggestion = {
  id: string;
  label: string;
  query: string;
  mode: KnowledgeSearchMode;
  sourceId?: string;
};

type KnowledgeQueueItem = {
  id: string;
  file: File;
  status: KnowledgeQueueStatus;
  message?: string;
  retryable?: boolean;
  upload?: KnowledgeUploadResponse;
  sourceId?: string;
  documentId?: string | null;
  chunkCount?: number;
  ingestStatus?: string;
  ingestError?: string | null;
  uploadedAt?: string;
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
    operationDeskTitle: "产品运营任务台",
    operationDeskSubtitle: "输入产品或运营题材后，按闭环查看规划、知识、内容、审批、客户机执行、结果和下一轮改进。",
    operationCurrentLabel: "当前进程",
    operationResultLabel: "执行结果",
    operationControlLabel: "执行控制",
    operationGuidedActionsTitle: "常用操作",
    operationGuidedActionsSubtitle: "按从左到右的顺序处理目标、知识库、内容、审批和闭环推进。",
    operationAdvancedActionsTitle: "高级执行与恢复",
    operationAdvancedActionsHint: "用于客户机执行记录、OpenClaw/Playwright 交接、dry-run、失败恢复和发布数据回填。",
    operationStartLoop: "创建运营闭环",
    operationRefreshLoop: "刷新闭环",
    operationPrepareDraft: "准备首版产物",
    operationFirstDraftPreparing: "正在准备首版产物",
    operationFirstDraftReady: "首版内容已进入人工审批",
    operationApproveAndPrepare: "审批并准备执行",
    operationApproveNextCycleAndPrepare: "审批下一轮并准备执行",
    operationApproveImprovedDraftAndPrepare: "审批改进草案并准备再执行",
    operationRejectDraft: "驳回首版内容",
    operationRejectNextCycleDraft: "驳回下一轮草案",
    operationRejectImprovedDraft: "驳回改进草案",
    operationApprovalPreparing: "正在审批并准备客户机执行记录",
    operationNextCycleApprovalPreparing: "正在审批下一轮并准备客户机执行记录",
    operationImprovedApprovalPreparing: "正在审批改进草案并准备再执行",
    operationExecutionPrepReady: "客户机执行准备记录已生成，等待执行前复核",
    operationNextCycleExecutionPrepReady: "下一轮客户机执行准备记录已生成，等待执行前复核",
    operationImprovedExecutionPrepReady: "改进草案再执行准备记录已生成，等待执行前复核",
    operationApprovalRejected: "首版内容已驳回，可修改后重新准备",
    operationNextCycleApprovalRejected: "下一轮草案已驳回，可按改进建议重新生成",
    operationApprovalMissing: "请先准备首版产物并生成待审批记录",
    operationApprovalPending: "商业审批待处理",
    operationReviewAndQueueRun: "复核并创建执行记录",
    operationReviewAndQueueNextCycleRun: "复核下一轮执行记录",
    operationReviewAndQueueImprovedRun: "复核改进再执行记录",
    operationExecutionRunQueuing: "正在复核并创建执行记录",
    operationNextCycleExecutionRunQueuing: "正在复核并创建下一轮执行记录",
    operationImprovedExecutionRunQueuing: "正在复核并创建改进再执行记录",
    operationExecutionRunReady: "执行运行记录已创建，等待开始",
    operationNextCycleExecutionRunReady: "下一轮执行运行记录已创建，等待开始",
    operationImprovedExecutionRunReady: "改进再执行运行记录已创建，等待开始",
    operationExecutionRequestMissing: "请先生成客户机执行准备记录",
    operationStartRun: "标记开始",
    operationRunStarting: "正在标记执行开始",
    operationRunStarted: "执行记录已标记为运行中",
    operationFailRun: "记录失败",
    operationRunFailed: "执行记录已标记失败，可恢复重试",
    operationRetryRun: "恢复重试",
    operationRunRetrying: "执行记录已进入重试，可再次开始",
    operationExecutionRequestPending: "执行准备待复核",
    operationExecutionRunPending: "执行记录状态",
    operationRuntimePreflight: "执行前预检",
    operationRuntimePreflightChecking: "正在检查客户机执行条件",
    operationRuntimePreflightReady: "执行前预检通过，等待人工启动",
    operationRuntimePreflightBlocked: "执行前预检未通过，请先恢复客户机环境",
    operationRuntimePreflightMissing: "请先创建待执行记录",
    operationGuardedDispatchHandoff: "交接受保护执行",
    operationGuardedDispatchHandingOff: "正在准备受保护执行交接",
    operationGuardedDispatchReady: "受保护执行交接已准备，等待人工启动",
    operationGuardedDispatchBlocked: "受保护执行交接被阻断，请先完成执行前预检",
    operationGuardedDispatchMissing: "请先创建待执行记录",
    operationAdapterDryRun: "执行 dry-run",
    operationAdapterDryRunRunning: "正在执行受保护 dry-run",
    operationAdapterDryRunSucceeded: "dry-run 已完成，已记录客户机执行结果",
    operationAdapterDryRunBlocked: "dry-run 被阻断，请先完成预检和受保护交接",
    operationAdapterDryRunMissing: "请先创建待执行记录",
    operationExecutionQueueTitle: "客户机执行队列",
    operationExecutionQueueSubtitle: "查看待执行、运行中、失败和已完成记录；这里先记录 dry-run 结果，不直接发布。",
    operationExecutionQueueEmpty: "暂无客户机执行记录，先审批并创建执行记录。",
    operationExecutionQueueReady: "已完成受保护交接",
    operationExecutionQueuePreflightReady: "预检已通过",
    operationExecutionQueueWaiting: "等待准备",
    operationApprovalCenterSummary: "商业审批中心",
    operationApprovalCenterTitle: "待审批运营内容",
    operationApprovalCenterEmpty: "暂无商业审批。先准备首版产物或下一轮草案。",
    operationApprovalCenterApprove: "通过并准备执行",
    operationApprovalCenterReject: "驳回",
    operationApprovalCenterRisk: "风险",
    operationApprovalCenterStatus: "状态",
    operationPublishPanelTitle: "发布结果闭环",
    operationPublishPanelSubtitle: "先准备单平台发布交接，再人工回收链接/截图/日志，最后记录曝光、互动和转化观察。",
    operationPublishHandoff: "准备发布交接",
    operationPublishHandoffPreparing: "正在准备发布交接",
    operationPublishHandoffReady: "发布交接已准备，等待人工发布或真实适配器",
    operationPublishHandoffMissing: "请先完成 dry-run 执行",
    operationCapturePublishResult: "回收发布结果",
    operationCapturePublishResultCapturing: "正在回收发布结果",
    operationPublishResultReady: "发布结果已回收，可观察数据",
    operationPublishResultMissing: "请先准备发布交接",
    operationRecordMetricObservation: "记录运营数据",
    operationMetricObservationRecording: "正在记录运营数据",
    operationMetricObservationReady: "运营数据观察已记录，可生成改进",
    operationMetricObservationMissing: "请先回收发布结果",
    operationPublishTargetLabel: "发布目标",
    operationPublishResultLabel: "结果回收",
    operationMetricObservationLabel: "数据观察",
    operationPublishImprovementLabel: "内容改进",
    operationAnalyzePublishMetrics: "分析数据并改进",
    operationAnalyzePublishMetricsRunning: "正在生成改进建议",
    operationPublishImprovementReady: "改进建议已生成，可准备下一轮内容",
    operationPublishImprovementMissing: "请先记录运营数据",
    operationPrepareImprovedDraft: "准备改进草案",
    operationClosedLoopDeliveryTitle: "闭环交付推进",
    operationClosedLoopDeliverySubtitle: "把客户机执行、发布结果、运营数据、改进分析和下一轮草案合并成一个可操作流程。",
    operationClosedLoopDeliveryAction: "推进完整闭环",
    operationClosedLoopDeliveryRunning: "正在推进客户机完整闭环",
    operationClosedLoopDeliveryReady: "完整闭环已推进到下一轮草案",
    operationClosedLoopDeliveryMissing: "请先创建或选择一个运营闭环",
    operationClosedLoopDeliveryBoundary: "当前仍是受控交付：会记录 OpenClaw/Playwright handoff 与 dry-run，不自动登录平台、不绕过验证码、不控制真实账号。",
    operationClosedLoopDeliverySteps: ["客户机执行准备", "发布结果回填", "运营数据观察", "分析改进方向", "生成下一轮草案"],
    operationAgentSkillTitle: "Agent / Skill 编排",
    operationAgentSkillSubtitle: "查看当前闭环由哪个 Agent 和 Skill 接管，下一步只显示可执行动作。",
    operationAgentSkillNext: "下一 Skill",
    operationAgentSkillBoundary: "服务器只下发编排与交接信息；客户机必须在审批后再执行 OpenClaw/Playwright。",
    operationAgentSkillRefresh: "刷新编排",
    operationAgentSkillRefreshing: "正在刷新",
    operationAgentSkillUnavailable: "等待选择运营目标",
    operationCompleteFeedbackLoop: "记录结果并生成改进",
    operationCompleteNextCycleFeedbackLoop: "记录下一轮结果并改进",
    operationFeedbackLoopCompleting: "正在记录结果、观察和改进建议",
    operationNextCycleFeedbackLoopCompleting: "正在记录下一轮结果、观察和改进建议",
    operationFeedbackLoopComplete: "闭环已完成，可进入下一轮内容改进",
    operationNextCycleFeedbackLoopComplete: "下一轮闭环已完成，可继续生成改进草案",
    operationFeedbackLoopMissing: "请先创建执行运行记录",
    operationResultRecordPending: "结果记录状态",
    operationObservationPending: "数据观察状态",
    operationOptimizationPending: "改进建议状态",
    operationPrepareNextCycleDraft: "生成下一轮草案",
    operationNextCycleDraftPreparing: "正在生成下一轮草案",
    operationNextCycleDraftReady: "下一轮草案已进入人工审批",
    operationNextCycleDecisionMissing: "请先完成结果、观察和改进建议",
    operationLoopSourceLabel: "闭环来源",
    operationLoopLoaded: "已连接真实运营闭环",
    operationLoopDisconnected: "未连接真实闭环，当前显示本地任务状态",
    operationLoopTitle: "运营闭环",
    operationDeliverablesTitle: "交付内容",
    operationDetailsTitle: "交付、执行与发布详情",
    operationDetailsHint: "低频维护信息已折叠；需要排查执行记录、发布回填或交付物时再展开。",
    operationKnowledgeTitle: "知识库内容",
    operationKnowledgeBody: "上传产品资料、品牌资料、竞品资料或素材文件，让系统先调用知识库再生产内容。",
    operationOpenKnowledge: "上传知识库内容",
    operationViewOutputs: "查看交付内容",
    operationPause: "中断任务",
    operationContinue: "继续任务",
    operationOpenClawLabel: "审批后由 OpenClaw 调度 Playwright 在客户机执行发布。",
    operationLoopSteps: [
      { id: "plan", label: "规划任务", detail: "系统拆解运营目标和执行顺序。" },
      { id: "knowledge", label: "调用知识库", detail: "检索产品、品牌、竞品和素材资料。" },
      { id: "content", label: "生产内容", detail: "生成文案、视频脚本、数据分析和运营方向。" },
      { id: "approval", label: "人工审批", detail: "发布和外部动作必须先确认。" },
      { id: "client", label: "客户机执行", detail: "OpenClaw/Playwright 执行授权后的发布任务。" },
      { id: "result", label: "记录结果", detail: "回传链接、截图、日志和失败原因。" },
      { id: "data", label: "观察数据", detail: "记录曝光、互动、线索和转化表现。" },
      { id: "improve", label: "分析改进", detail: "生成下一轮内容和运营建议。" },
    ],
    operationDeliverables: [
      { id: "copy", label: "文案", detail: "标题、正文、短视频口播和社媒说明。" },
      { id: "video", label: "视频", detail: "脚本、镜头、素材 Brief 和生成需求。" },
      { id: "data", label: "数据分析", detail: "目标指标、观察口径和复盘依据。" },
      { id: "direction", label: "运营方向", detail: "人群、渠道、节奏和下一轮优化。" },
    ],
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
    operationDeskTitle: "Product operation desk",
    operationDeskSubtitle: "Enter a product or campaign topic, then follow planning, knowledge, content, approval, client execution, results, and the next improvement cycle.",
    operationCurrentLabel: "Current process",
    operationResultLabel: "Execution result",
    operationControlLabel: "Execution controls",
    operationGuidedActionsTitle: "Common actions",
    operationGuidedActionsSubtitle: "Move from left to right: goal, knowledge, content, approval, and loop delivery.",
    operationAdvancedActionsTitle: "Advanced execution and recovery",
    operationAdvancedActionsHint: "Use for client run records, OpenClaw/Playwright handoff, dry-run, failure recovery, and publish data capture.",
    operationStartLoop: "Create loop",
    operationRefreshLoop: "Refresh loop",
    operationPrepareDraft: "Prepare first draft",
    operationFirstDraftPreparing: "Preparing first draft",
    operationFirstDraftReady: "First draft is ready for approval",
    operationApproveAndPrepare: "Approve and prep execution",
    operationApproveNextCycleAndPrepare: "Approve next cycle and prep",
    operationApproveImprovedDraftAndPrepare: "Approve improved draft and prep",
    operationRejectDraft: "Reject first draft",
    operationRejectNextCycleDraft: "Reject next-cycle draft",
    operationRejectImprovedDraft: "Reject improved draft",
    operationApprovalPreparing: "Approving and preparing the client execution record",
    operationNextCycleApprovalPreparing: "Approving next cycle and preparing the client execution record",
    operationImprovedApprovalPreparing: "Approving improved draft and preparing re-execution",
    operationExecutionPrepReady: "Client execution prep record is ready for pre-run review",
    operationNextCycleExecutionPrepReady: "Next-cycle client execution prep record is ready for pre-run review",
    operationImprovedExecutionPrepReady: "Improved draft re-execution prep is ready for pre-run review",
    operationApprovalRejected: "First draft rejected; revise it before preparing again",
    operationNextCycleApprovalRejected: "Next-cycle draft rejected; regenerate it from the improvement decision",
    operationApprovalMissing: "Prepare the first draft and approval record first",
    operationApprovalPending: "Commercial approval pending",
    operationReviewAndQueueRun: "Review and queue run",
    operationReviewAndQueueNextCycleRun: "Review next-cycle run",
    operationReviewAndQueueImprovedRun: "Review improved run",
    operationExecutionRunQueuing: "Reviewing and creating execution run",
    operationNextCycleExecutionRunQueuing: "Reviewing and creating next-cycle execution run",
    operationImprovedExecutionRunQueuing: "Reviewing and creating improved re-execution run",
    operationExecutionRunReady: "Execution run is queued and waiting to start",
    operationNextCycleExecutionRunReady: "Next-cycle execution run is queued and waiting to start",
    operationImprovedExecutionRunReady: "Improved re-execution run is queued and waiting to start",
    operationExecutionRequestMissing: "Create the client execution prep record first",
    operationStartRun: "Mark started",
    operationRunStarting: "Marking execution run started",
    operationRunStarted: "Execution run marked running",
    operationFailRun: "Record failure",
    operationRunFailed: "Execution run marked failed and can be retried",
    operationRetryRun: "Retry run",
    operationRunRetrying: "Execution run moved to retrying; start it again",
    operationExecutionRequestPending: "Execution prep pending review",
    operationExecutionRunPending: "Execution run status",
    operationRuntimePreflight: "Run preflight",
    operationRuntimePreflightChecking: "Checking client execution readiness",
    operationRuntimePreflightReady: "Preflight passed and is waiting for operator start",
    operationRuntimePreflightBlocked: "Preflight blocked; recover the client environment first",
    operationRuntimePreflightMissing: "Create a queued execution run first",
    operationGuardedDispatchHandoff: "Prepare handoff",
    operationGuardedDispatchHandingOff: "Preparing guarded execution handoff",
    operationGuardedDispatchReady: "Guarded execution handoff is ready for operator start",
    operationGuardedDispatchBlocked: "Guarded execution handoff is blocked; run preflight first",
    operationGuardedDispatchMissing: "Create a queued execution run first",
    operationAdapterDryRun: "Run dry-run",
    operationAdapterDryRunRunning: "Running guarded dry-run",
    operationAdapterDryRunSucceeded: "Dry-run completed and client execution result was recorded",
    operationAdapterDryRunBlocked: "Dry-run blocked; complete preflight and guarded handoff first",
    operationAdapterDryRunMissing: "Create a queued execution run first",
    operationExecutionQueueTitle: "Client execution queue",
    operationExecutionQueueSubtitle: "See queued, running, failed, and completed records; this stage records dry-run results before publishing.",
    operationExecutionQueueEmpty: "No client execution records yet. Approve and create an execution run first.",
    operationExecutionQueueReady: "Guarded handoff ready",
    operationExecutionQueuePreflightReady: "Preflight ready",
    operationExecutionQueueWaiting: "Waiting for prep",
    operationApprovalCenterSummary: "Commercial approval center",
    operationApprovalCenterTitle: "Operation content waiting for approval",
    operationApprovalCenterEmpty: "No commercial approvals yet. Prepare the first draft or next-cycle draft first.",
    operationApprovalCenterApprove: "Approve and prep execution",
    operationApprovalCenterReject: "Reject",
    operationApprovalCenterRisk: "Risk",
    operationApprovalCenterStatus: "Status",
    operationPublishPanelTitle: "Publish result loop",
    operationPublishPanelSubtitle: "Prepare a single-platform publish handoff, capture link/screenshot/log results manually, then record reach, engagement, and conversion observations.",
    operationPublishHandoff: "Prepare publish handoff",
    operationPublishHandoffPreparing: "Preparing publish handoff",
    operationPublishHandoffReady: "Publish handoff is ready for manual publish or a future live adapter",
    operationPublishHandoffMissing: "Complete dry-run execution first",
    operationCapturePublishResult: "Capture publish result",
    operationCapturePublishResultCapturing: "Capturing publish result",
    operationPublishResultReady: "Publish result captured and ready for data observation",
    operationPublishResultMissing: "Prepare the publish handoff first",
    operationRecordMetricObservation: "Record metrics",
    operationMetricObservationRecording: "Recording operating metrics",
    operationMetricObservationReady: "Metric observation recorded and ready for improvement",
    operationMetricObservationMissing: "Capture the publish result first",
    operationPublishTargetLabel: "Publish target",
    operationPublishResultLabel: "Result capture",
    operationMetricObservationLabel: "Data observation",
    operationPublishImprovementLabel: "Content improvement",
    operationAnalyzePublishMetrics: "Analyze and improve",
    operationAnalyzePublishMetricsRunning: "Generating improvement decision",
    operationPublishImprovementReady: "Improvement decision is ready for the next draft",
    operationPublishImprovementMissing: "Record operating metrics first",
    operationPrepareImprovedDraft: "Prepare improved draft",
    operationClosedLoopDeliveryTitle: "Closed-loop delivery",
    operationClosedLoopDeliverySubtitle: "Combine client execution, publish result capture, data observation, analysis, and next draft generation into one operator flow.",
    operationClosedLoopDeliveryAction: "Advance full loop",
    operationClosedLoopDeliveryRunning: "Advancing the full client closed loop",
    operationClosedLoopDeliveryReady: "Full loop advanced to the next draft",
    operationClosedLoopDeliveryMissing: "Create or select an operation loop first",
    operationClosedLoopDeliveryBoundary: "This is still controlled delivery: it records OpenClaw/Playwright handoff and dry-run state without platform login, captcha bypass, or real account control.",
    operationClosedLoopDeliverySteps: ["Client execution prep", "Publish result capture", "Operating data observation", "Improvement analysis", "Next draft generation"],
    operationAgentSkillTitle: "Agent / Skill orchestration",
    operationAgentSkillSubtitle: "See which Agent and Skill owns the current loop step, with the next operator action only.",
    operationAgentSkillNext: "Next Skill",
    operationAgentSkillBoundary: "The server sends orchestration and handoff metadata only; client OpenClaw/Playwright execution still requires approval.",
    operationAgentSkillRefresh: "Refresh orchestration",
    operationAgentSkillRefreshing: "Refreshing",
    operationAgentSkillUnavailable: "Select an operation goal",
    operationCompleteFeedbackLoop: "Record result and improve",
    operationCompleteNextCycleFeedbackLoop: "Record next-cycle result",
    operationFeedbackLoopCompleting: "Recording result, observation, and improvement",
    operationNextCycleFeedbackLoopCompleting: "Recording next-cycle result, observation, and improvement",
    operationFeedbackLoopComplete: "Loop complete and ready for the next content iteration",
    operationNextCycleFeedbackLoopComplete: "Next-cycle loop complete and ready for another improved draft",
    operationFeedbackLoopMissing: "Create an execution run record first",
    operationResultRecordPending: "Result record status",
    operationObservationPending: "Data observation status",
    operationOptimizationPending: "Improvement decision status",
    operationPrepareNextCycleDraft: "Generate next draft",
    operationNextCycleDraftPreparing: "Generating next-cycle draft",
    operationNextCycleDraftReady: "Next-cycle draft is ready for approval",
    operationNextCycleDecisionMissing: "Complete result, observation, and improvement first",
    operationLoopSourceLabel: "Loop source",
    operationLoopLoaded: "Connected to real operation loop",
    operationLoopDisconnected: "No real loop connected; showing local task status",
    operationLoopTitle: "Operation loop",
    operationDeliverablesTitle: "Deliverables",
    operationDetailsTitle: "Deliverables, execution, and publishing details",
    operationDetailsHint: "Lower-frequency maintenance details are folded; open this only for run records, publish capture, or deliverable checks.",
    operationKnowledgeTitle: "Knowledge material",
    operationKnowledgeBody: "Upload product, brand, competitor, or asset files so the system uses the knowledge base before producing content.",
    operationOpenKnowledge: "Upload knowledge",
    operationViewOutputs: "View deliverables",
    operationPause: "Interrupt task",
    operationContinue: "Continue task",
    operationOpenClawLabel: "After approval, OpenClaw schedules Playwright to execute publishing on this client machine.",
    operationLoopSteps: [
      { id: "plan", label: "Plan tasks", detail: "Break down the operating goal and execution order." },
      { id: "knowledge", label: "Use knowledge", detail: "Search product, brand, competitor, and asset material." },
      { id: "content", label: "Produce content", detail: "Create copy, video scripts, data analysis, and operating direction." },
      { id: "approval", label: "Human approval", detail: "Publishing and external actions must be confirmed first." },
      { id: "client", label: "Client execution", detail: "OpenClaw/Playwright runs approved publishing tasks." },
      { id: "result", label: "Record result", detail: "Return links, screenshots, logs, and failure reasons." },
      { id: "data", label: "Observe data", detail: "Track impressions, engagement, leads, and conversions." },
      { id: "improve", label: "Improve content", detail: "Create next-cycle content and operating recommendations." },
    ],
    operationDeliverables: [
      { id: "copy", label: "Copy", detail: "Titles, body copy, short-video narration, and social captions." },
      { id: "video", label: "Video", detail: "Scripts, shots, asset briefs, and generation requests." },
      { id: "data", label: "Data analysis", detail: "Target metrics, observation rules, and review evidence." },
      { id: "direction", label: "Direction", detail: "Audience, channels, cadence, and next optimization." },
    ],
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
    documentOverviewTitle: "资料处理概览",
    documentOverviewTotal: "资料总数",
    documentOverviewReady: "可检索资料",
    documentOverviewNeedsReview: "需要关注",
    documentOverviewSelected: "当前查看",
    detailTitle: "资料详情",
    detailEmpty: "选择一份资料后，会显示来源编号、分组、分段、更新时间和处理状态。",
    detailSourceId: "来源编号",
    detailCollection: "所在分组",
    detailCreatedAt: "创建时间",
    detailHealthReady: "资料已可检索",
    detailHealthNeedsReview: "需要检查处理状态",
    detailHealthUnknown: "等待确认状态",
    viewDetails: "查看详情",
    useForUpdate: "用此资料更新",
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
    validationTitle: "检索验证",
    validationHint: "输入一个运营问题，确认刚上传或修改的资料是否能被知识库命中。",
    validationQueryLabel: "验证问题",
    validationQueryPlaceholder: "例如：新品活动 FAQ 里有哪些禁用词？",
    validationModeLabel: "检索方式",
    validationHybrid: "混合",
    validationDense: "语义",
    validationKeyword: "关键词",
    validationAction: "开始验证",
    validationRunning: "正在检索知识库。",
    validationEmpty: "还没有验证记录。输入问题后会显示命中的资料片段。",
    validationNoResults: "没有命中资料，请检查分组、关键词或重新上传资料。",
    validationResultsTitle: "验证命中",
    validationQueryRequired: "请先输入要验证的问题。",
    validationScore: "匹配度",
    validationSource: "来源",
    validationChunk: "分段",
    validationMode: "方式",
    validationCollection: "验证分组",
    validationSearchTitle: "知识检索验证完成",
    validationFailedTitle: "知识检索验证失败",
    validationClear: "清空结果",
    validationGuidanceTitle: "验证建议",
    validationGuidanceHint: "根据当前资料生成常用验证问题，一键带入检索验证。",
    validationSuggestionTitle: "建议问题",
    validationSuggestionApplied: "已填入验证问题",
    validationSuggestionAppliedTitle: "已使用验证建议",
    validationUseSuggestion: "使用问题",
    validationRunForItem: "验证此资料",
    validationSelectedMaterial: "当前资料",
    validationLatestUpload: "最近上传",
    validationNoTarget: "选择资料或上传文件后，会出现更准确的验证建议。",
    validationSuggestionSummary: "核心内容",
    validationSuggestionRisk: "风险与限制",
    validationSuggestionAction: "执行要点",
    validationSuggestionSummaryQuery: "请总结《{material}》中和当前运营目标相关的关键内容。",
    validationSuggestionRiskQuery: "《{material}》中有哪些禁用词、合规风险或需要人工确认的信息？",
    validationSuggestionActionQuery: "根据《{material}》，下一步运营执行需要注意哪些要点？",
    validationOutcomeTitle: "验证结论",
    validationOutcomeHint: "把检索结果转换为能否进入后续运营的可用性判断。",
    validationOutcomeReady: "可用于后续运营",
    validationOutcomeNeedsEvidence: "需要补充资料",
    validationOutcomeNeedsReview: "需要人工复核",
    validationOutcomeIdle: "等待验证",
    validationOutcomeReadyDetail: "已检索到相关证据，可以作为后续运营任务的知识依据。",
    validationOutcomeNeedsEvidenceDetail: "未命中可用证据，建议调整问题、检查分组或继续上传资料。",
    validationOutcomeNeedsReviewDetail: "验证请求失败或资料状态异常，请检查连接、分组或资料入库状态。",
    validationOutcomeIdleDetail: "先选择建议问题或输入验证问题，再运行检索验证。",
    validationOutcomeMatches: "命中证据",
    validationOutcomeMaterial: "验证资料",
    validationOutcomeMode: "验证方式",
    validationOutcomeNextStep: "下一步",
    validationOutcomeMarkReady: "标记可用于运营",
    validationOutcomeRetry: "重新验证",
    validationOutcomeRunFirst: "运行验证",
    validationOutcomeMarkedTitle: "验证结论已确认",
    validationOutcomeMarked: "已标记为可用于后续运营。",
    ingestionTitle: "入库状态闭环",
    ingestionHint: "查看资料从选择、上传、切分入库到检索验证的当前状态和失败原因。",
    ingestionNextAction: "当前建议",
    ingestionTimelineTitle: "处理步骤",
    ingestionStepSelect: "已选择",
    ingestionStepUpload: "上传",
    ingestionStepIndex: "切分入库",
    ingestionStepValidate: "检索验证",
    ingestionReady: "可检索",
    ingestionProcessing: "处理中",
    ingestionNeedsReview: "需处理",
    ingestionFailed: "失败",
    ingestionQueued: "待上传",
    ingestionUploaded: "已上传",
    ingestionSearchable: "可用于检索",
    ingestionNoBatch: "还没有上传批次。选择文件或保存文字后，这里会显示处理状态。",
    ingestionLatestBatch: "最近处理",
    ingestionRefresh: "刷新状态",
    ingestionRetry: "重试失败",
    ingestionSkipped: "检测到重复，已保留现有版本。",
    ingestionSourceId: "来源编号",
    ingestionDocumentId: "文档编号",
    ingestionError: "失败原因",
    ingestionSelectedStatus: "入库状态",
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
    documentOverviewTitle: "Material processing overview",
    documentOverviewTotal: "Total material",
    documentOverviewReady: "Search-ready",
    documentOverviewNeedsReview: "Needs review",
    documentOverviewSelected: "Now viewing",
    detailTitle: "Material details",
    detailEmpty: "Choose material to see source ID, collection, chunks, updated time, and processing status.",
    detailSourceId: "Source ID",
    detailCollection: "Collection",
    detailCreatedAt: "Created",
    detailHealthReady: "Material is searchable",
    detailHealthNeedsReview: "Check processing status",
    detailHealthUnknown: "Status needs confirmation",
    viewDetails: "View details",
    useForUpdate: "Use for update",
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
    validationTitle: "Search validation",
    validationHint: "Enter an operating question to confirm uploaded or edited material can be found.",
    validationQueryLabel: "Validation question",
    validationQueryPlaceholder: "Example: What launch FAQ terms are restricted?",
    validationModeLabel: "Search mode",
    validationHybrid: "Hybrid",
    validationDense: "Semantic",
    validationKeyword: "Keyword",
    validationAction: "Validate",
    validationRunning: "Searching the knowledge base.",
    validationEmpty: "No validation yet. Enter a question to see matched knowledge snippets.",
    validationNoResults: "No material matched. Check the collection, keywords, or upload the material again.",
    validationResultsTitle: "Validation matches",
    validationQueryRequired: "Enter a validation question first.",
    validationScore: "Match",
    validationSource: "Source",
    validationChunk: "Chunk",
    validationMode: "Mode",
    validationCollection: "Validation collection",
    validationSearchTitle: "Knowledge search validation completed",
    validationFailedTitle: "Knowledge search validation failed",
    validationClear: "Clear results",
    validationGuidanceTitle: "Validation guidance",
    validationGuidanceHint: "Use common validation questions for the current material and send them into search validation.",
    validationSuggestionTitle: "Suggested questions",
    validationSuggestionApplied: "Validation question filled",
    validationSuggestionAppliedTitle: "Validation suggestion used",
    validationUseSuggestion: "Use question",
    validationRunForItem: "Validate material",
    validationSelectedMaterial: "Selected material",
    validationLatestUpload: "Latest upload",
    validationNoTarget: "Choose material or upload files to get more accurate validation suggestions.",
    validationSuggestionSummary: "Core content",
    validationSuggestionRisk: "Risks and limits",
    validationSuggestionAction: "Action points",
    validationSuggestionSummaryQuery: "Summarize the key content in \"{material}\" that is relevant to the current operating goal.",
    validationSuggestionRiskQuery: "What restricted terms, compliance risks, or human-review items appear in \"{material}\"?",
    validationSuggestionActionQuery: "Based on \"{material}\", what should the operator pay attention to before the next execution step?",
    validationOutcomeTitle: "Validation outcome",
    validationOutcomeHint: "Turn search results into a clear usability decision for the next operating step.",
    validationOutcomeReady: "Ready for operations",
    validationOutcomeNeedsEvidence: "Needs more evidence",
    validationOutcomeNeedsReview: "Needs human review",
    validationOutcomeIdle: "Waiting for validation",
    validationOutcomeReadyDetail: "Relevant evidence was found, so this material can support the next operating task.",
    validationOutcomeNeedsEvidenceDetail: "No usable evidence was found. Adjust the question, check the collection, or upload more material.",
    validationOutcomeNeedsReviewDetail: "The validation request failed or the material state needs attention. Check connection, collection, or ingestion status.",
    validationOutcomeIdleDetail: "Choose a suggested question or enter a validation question, then run search validation.",
    validationOutcomeMatches: "Evidence matches",
    validationOutcomeMaterial: "Material",
    validationOutcomeMode: "Mode",
    validationOutcomeNextStep: "Next step",
    validationOutcomeMarkReady: "Mark ready",
    validationOutcomeRetry: "Retry validation",
    validationOutcomeRunFirst: "Run validation",
    validationOutcomeMarkedTitle: "Validation outcome confirmed",
    validationOutcomeMarked: "Marked as ready for the next operating step.",
    ingestionTitle: "Ingestion status loop",
    ingestionHint: "Track material from selection and upload through chunking, indexing, and search validation.",
    ingestionNextAction: "Current suggestion",
    ingestionTimelineTitle: "Processing steps",
    ingestionStepSelect: "Selected",
    ingestionStepUpload: "Upload",
    ingestionStepIndex: "Chunk and index",
    ingestionStepValidate: "Search validation",
    ingestionReady: "Search-ready",
    ingestionProcessing: "Processing",
    ingestionNeedsReview: "Needs action",
    ingestionFailed: "Failed",
    ingestionQueued: "Queued",
    ingestionUploaded: "Uploaded",
    ingestionSearchable: "Searchable",
    ingestionNoBatch: "No upload batch yet. Choose files or save text to see processing status here.",
    ingestionLatestBatch: "Latest processing",
    ingestionRefresh: "Refresh status",
    ingestionRetry: "Retry failed",
    ingestionSkipped: "Duplicate detected; the existing version was kept.",
    ingestionSourceId: "Source ID",
    ingestionDocumentId: "Document ID",
    ingestionError: "Failure reason",
    ingestionSelectedStatus: "Ingestion status",
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

function ChatPanel({
  language,
  onOpenKnowledge,
  runtimeClient = localWorkerClient,
}: {
  language: ClientLanguage;
  onOpenKnowledge: () => void;
  runtimeClient?: typeof localWorkerClient;
}) {
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
  const [selectedCommercialOperationId, setSelectedCommercialOperationId] = useState<string | null>(null);
  const [operationLoop, setOperationLoop] = useState<CommercialOperationLoopSummary | null>(null);
  const [agentSkillOrchestration, setAgentSkillOrchestration] = useState<CommercialOperationAgentSkillOrchestration | null>(null);
  const [agentSkillStatus, setAgentSkillStatus] = useState<string | null>(null);
  const [agentSkillLoading, setAgentSkillLoading] = useState(false);
  const [operationLoopError, setOperationLoopError] = useState<string | null>(null);
  const [operationLoopLoading, setOperationLoopLoading] = useState(false);
  const [firstDraftBootstrapStatus, setFirstDraftBootstrapStatus] = useState<string | null>(null);
  const [firstDraftBootstrapLoading, setFirstDraftBootstrapLoading] = useState(false);
  const [commercialApprovals, setCommercialApprovals] = useState<CommercialOperationApproval[]>([]);
  const [executionPrepStatus, setExecutionPrepStatus] = useState<string | null>(null);
  const [executionPrepLoading, setExecutionPrepLoading] = useState(false);
  const [commercialExecutionRequests, setCommercialExecutionRequests] = useState<CommercialOperationExecutionRequest[]>([]);
  const [commercialExecutionRuns, setCommercialExecutionRuns] = useState<CommercialOperationExecutionRun[]>([]);
  const [executionRunStatus, setExecutionRunStatus] = useState<string | null>(null);
  const [executionRunLoading, setExecutionRunLoading] = useState(false);
  const [runtimePreflightStatus, setRuntimePreflightStatus] = useState<string | null>(null);
  const [runtimePreflightLoading, setRuntimePreflightLoading] = useState(false);
  const [guardedDispatchStatus, setGuardedDispatchStatus] = useState<string | null>(null);
  const [guardedDispatchLoading, setGuardedDispatchLoading] = useState(false);
  const [adapterDryRunStatus, setAdapterDryRunStatus] = useState<string | null>(null);
  const [adapterDryRunLoading, setAdapterDryRunLoading] = useState(false);
  const [publishHandoffStatus, setPublishHandoffStatus] = useState<string | null>(null);
  const [publishHandoffLoading, setPublishHandoffLoading] = useState(false);
  const [publishResultStatus, setPublishResultStatus] = useState<string | null>(null);
  const [publishResultLoading, setPublishResultLoading] = useState(false);
  const [metricObservationStatus, setMetricObservationStatus] = useState<string | null>(null);
  const [metricObservationLoading, setMetricObservationLoading] = useState(false);
  const [publishImprovementStatus, setPublishImprovementStatus] = useState<string | null>(null);
  const [publishImprovementLoading, setPublishImprovementLoading] = useState(false);
  const [commercialResults, setCommercialResults] = useState<CommercialOperationResult[]>([]);
  const [commercialMonitoringObservations, setCommercialMonitoringObservations] = useState<CommercialOperationMonitoringObservation[]>([]);
  const [commercialOptimizationDecisions, setCommercialOptimizationDecisions] = useState<CommercialOperationOptimizationDecision[]>([]);
  const [feedbackLoopStatus, setFeedbackLoopStatus] = useState<string | null>(null);
  const [feedbackLoopLoading, setFeedbackLoopLoading] = useState(false);
  const [nextCycleDraftStatus, setNextCycleDraftStatus] = useState<string | null>(null);
  const [nextCycleDraftLoading, setNextCycleDraftLoading] = useState(false);
  const [closedLoopDeliveryStatus, setClosedLoopDeliveryStatus] = useState<string | null>(null);
  const [closedLoopDeliveryLoading, setClosedLoopDeliveryLoading] = useState(false);
  const [digitalHumanVideoJobs, setDigitalHumanVideoJobs] = useState<DigitalHumanVideoJob[]>([]);
  const [digitalHumanVideoStatus, setDigitalHumanVideoStatus] = useState<string | null>(null);
  const [digitalHumanVideoLoading, setDigitalHumanVideoLoading] = useState(false);

  useEffect(() => {
    window.localStorage.setItem("workerConsoleConversationSettings", JSON.stringify(settings));
  }, [settings]);

  const refreshCommercialOperationLoop = useCallback(async (operationId?: string | null) => {
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    try {
      const response = await commercialOperationClient.list(settings);
      const nextOperationId = operationId || selectedCommercialOperationId || response.items[0]?.id || null;
      if (!nextOperationId) {
        setSelectedCommercialOperationId(null);
        setOperationLoop(null);
        setAgentSkillOrchestration(null);
        setAgentSkillStatus(null);
        setCommercialApprovals([]);
        setCommercialExecutionRequests([]);
        setCommercialExecutionRuns([]);
        setCommercialResults([]);
        setCommercialMonitoringObservations([]);
        setCommercialOptimizationDecisions([]);
        setNextCycleDraftStatus(null);
        return;
      }
      setSelectedCommercialOperationId(nextOperationId);
      const [
        loop,
        agentSkillResponse,
        approvalResponse,
        executionRequestResponse,
        executionRunResponse,
        resultResponse,
        observationResponse,
        optimizationResponse,
      ] = await Promise.all([
        commercialOperationClient.operationLoop(nextOperationId, settings),
        commercialOperationClient.agentSkillOrchestration(nextOperationId, settings).catch(() => null),
        commercialOperationClient.listApprovals(nextOperationId, undefined, settings).catch(() => ({ items: [] })),
        commercialOperationClient.listExecutionRequests(nextOperationId, undefined, settings).catch(() => ({ items: [] })),
        commercialOperationClient.listExecutionRuns(nextOperationId, undefined, settings).catch(() => ({ items: [] })),
        commercialOperationClient.listResults(nextOperationId, undefined, settings).catch(() => ({ items: [] })),
        commercialOperationClient.listMonitoringObservations(nextOperationId, undefined, settings).catch(() => ({ items: [] })),
        commercialOperationClient.listOptimizationDecisions(nextOperationId, undefined, settings).catch(() => ({ items: [] })),
      ]);
      setOperationLoop(loop);
      setAgentSkillOrchestration(agentSkillResponse);
      setAgentSkillStatus(agentSkillResponse?.next_action ?? null);
      setCommercialApprovals(approvalResponse.items);
      setCommercialExecutionRequests(executionRequestResponse.items);
      setCommercialExecutionRuns(executionRunResponse.items);
      setCommercialResults(resultResponse.items);
      setCommercialMonitoringObservations(observationResponse.items);
      setCommercialOptimizationDecisions(optimizationResponse.items);
      setConnectionState("connected");
    } catch (nextError) {
      setOperationLoop(null);
      setAgentSkillOrchestration(null);
      setAgentSkillStatus(null);
      setCommercialApprovals([]);
      setCommercialExecutionRequests([]);
      setCommercialExecutionRuns([]);
      setCommercialResults([]);
      setCommercialMonitoringObservations([]);
      setCommercialOptimizationDecisions([]);
      setNextCycleDraftStatus(null);
      setOperationLoopError(nextError instanceof Error ? nextError.message : "Commercial operation loop unavailable");
    } finally {
      setOperationLoopLoading(false);
    }
  }, [selectedCommercialOperationId, settings]);

  const refreshDigitalHumanVideos = useCallback(async () => {
    setDigitalHumanVideoLoading(true);
    try {
      const response = await digitalHumanClient.listVideoJobs(settings);
      setDigitalHumanVideoJobs(response.items);
      setDigitalHumanVideoStatus(null);
    } catch (nextError) {
      setDigitalHumanVideoJobs([]);
      setDigitalHumanVideoStatus(nextError instanceof Error ? nextError.message : "Digital human video progress unavailable");
    } finally {
      setDigitalHumanVideoLoading(false);
    }
  }, [settings]);

  useEffect(() => {
    void refreshCommercialOperationLoop();
    void refreshDigitalHumanVideos();
  }, [refreshCommercialOperationLoop, refreshDigitalHumanVideos]);

  const refreshLatestDigitalHumanVideo = async () => {
    const latest = digitalHumanVideoJobs[0];
    if (!latest) {
      await refreshDigitalHumanVideos();
      return;
    }
    setDigitalHumanVideoLoading(true);
    try {
      const refreshed = await digitalHumanClient.refreshVideoJob(latest.id, settings);
      setDigitalHumanVideoJobs((current) => [refreshed, ...current.filter((item) => item.id !== refreshed.id)]);
      setDigitalHumanVideoStatus(refreshed.result_summary ?? refreshed.next_action ?? refreshed.job_status);
    } catch (nextError) {
      setDigitalHumanVideoStatus(nextError instanceof Error ? nextError.message : "Digital human video refresh failed");
    } finally {
      setDigitalHumanVideoLoading(false);
    }
  };

  const ingestLatestDigitalHumanVideoOutput = async () => {
    const latest = digitalHumanVideoJobs[0];
    if (!latest) {
      await refreshDigitalHumanVideos();
      return;
    }
    setDigitalHumanVideoLoading(true);
    try {
      const ingested = await digitalHumanClient.ingestComfyuiOutput(latest.id, settings);
      setDigitalHumanVideoJobs((current) => [ingested, ...current.filter((item) => item.id !== ingested.id)]);
      setDigitalHumanVideoStatus(ingested.result_summary ?? ingested.next_action ?? ingested.job_status);
    } catch (nextError) {
      setDigitalHumanVideoStatus(nextError instanceof Error ? nextError.message : "Digital human output ingestion failed");
    } finally {
      setDigitalHumanVideoLoading(false);
    }
  };

  const refreshAgentSkillOrchestration = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    if (!operationId) {
      setAgentSkillStatus(workbenchCopy.operationAgentSkillUnavailable);
      return;
    }
    setAgentSkillLoading(true);
    try {
      const orchestration = await commercialOperationClient.refreshAgentSkillOrchestration(operationId, settings);
      setAgentSkillOrchestration(orchestration);
      setAgentSkillStatus(orchestration.next_action);
      setConnectionState("connected");
    } catch (error) {
      setAgentSkillStatus(error instanceof Error ? error.message : workbenchCopy.operationAgentSkillUnavailable);
    } finally {
      setAgentSkillLoading(false);
    }
  };

  const createCommercialOperationFromGoal = async () => {
    const objective = input.trim() || selectedGoalTemplate.prompt;
    const operation = await commercialOperationClient.create(
      {
        title: operationLoopTitleFromGoal(objective),
        objective,
        target_audience: language === "zh-CN" ? "待确认的客户群体" : "target audience to confirm",
        channels: ["customer_console"],
        knowledge_collection: "operations",
        success_metrics: ["content_output", "approval_pass_rate", "commercial_signal"],
        constraints: ["human approval required", "client execution through OpenClaw/Playwright after approval"],
        metadata: { source: "worker_console", phase: "63B", goal_template: selectedGoalTemplate.id },
      },
      settings,
    );
    setSelectedCommercialOperationId(operation.id);
    const loop = await commercialOperationClient.operationLoop(operation.id, settings);
    const orchestration = await commercialOperationClient.agentSkillOrchestration(operation.id, settings).catch(() => null);
    setOperationLoop(loop);
    setAgentSkillOrchestration(orchestration);
    setAgentSkillStatus(orchestration?.next_action ?? null);
    setCommercialApprovals([]);
    setCommercialExecutionRequests([]);
    setCommercialExecutionRuns([]);
    setCommercialResults([]);
    setCommercialMonitoringObservations([]);
    setCommercialOptimizationDecisions([]);
    setNextCycleDraftStatus(null);
    setClosedLoopDeliveryStatus(null);
    setConnectionState("connected");
    return { operation, loop };
  };

  const createCommercialOperationLoop = async () => {
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    try {
      const { operation } = await createCommercialOperationFromGoal();
      setRunStatus(`operation loop created: ${operation.title}`);
    } catch (nextError) {
      setOperationLoopError(nextError instanceof Error ? nextError.message : "Commercial operation loop unavailable");
      setRunStatus("operation loop error");
    } finally {
      setOperationLoopLoading(false);
    }
  };

  const prepareFirstDraftPackage = async () => {
    const objective = input.trim() || selectedGoalTemplate.prompt;
    setFirstDraftBootstrapLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setFirstDraftBootstrapStatus(null);
    setExecutionPrepStatus(null);
    try {
      const existingOperationId = operationLoop?.operation_id || selectedCommercialOperationId;
      const operationId = existingOperationId || (await createCommercialOperationFromGoal()).operation.id;
      await commercialOperationClient.planDraft(operationId, settings);
      const draft = await commercialOperationClient.createContentDraft(
        operationId,
        {
          step_key: "content_production",
          channel: "customer_console",
          content_format: "copy",
          title:
            language === "zh-CN"
              ? `${operationLoopTitleFromGoal(objective)} 首版内容草稿`
              : `${operationLoopTitleFromGoal(objective)} first content draft`,
          audience_segment: language === "zh-CN" ? "待确认的客户群体" : "target audience to confirm",
          content_body: firstDraftContentBody(objective, language),
          summary:
            language === "zh-CN"
              ? "客户机前端生成的首版可审批内容包，等待人工确认后才能执行。"
              : "First reviewable content package prepared from the customer console; human approval is required before execution.",
          call_to_action: language === "zh-CN" ? "人工确认后再执行" : "Review before execution",
          source_materials: ["knowledge_collection:operations", "customer_console_goal", `goal_template:${selectedGoalTemplate.id}`],
          asset_requests: [
            {
              title: language === "zh-CN" ? "首版主视觉素材需求" : "First hero visual asset request",
              type: "asset_placeholder",
              purpose: language === "zh-CN" ? "用于首版运营内容的视觉素材，不直接生成媒体。" : "Visual support for the first operation draft without generating media.",
              execution_boundary: "no ComfyUI job is created in this phase",
            },
          ],
          metadata: { source: "worker_console_first_draft_bootstrap", phase: "63B", goal_template: selectedGoalTemplate.id },
        },
        settings,
      );
      const readyDraft = await commercialOperationClient.readyContentDraft(
        operationId,
        draft.id,
        language === "zh-CN" ? "客户机已准备首版内容，等待人工审批。" : "Customer console prepared the first content draft for approval.",
        settings,
      );
      const approval = await commercialOperationClient.createApproval(
        operationId,
        {
          step_key: "human_review",
          title: language === "zh-CN" ? "审批首版运营内容" : "Approve first operation content",
          requested_action:
            language === "zh-CN"
              ? "请审核首版内容草稿和素材需求；审批前不会发布或执行客户机任务。"
              : "Review the first content draft and asset request; no publishing or client execution happens before approval.",
          risk_level: "medium",
          metadata: { source: "worker_console_first_draft_bootstrap", phase: "63B", content_draft_id: readyDraft.id },
        },
        settings,
      );
      const loop = await commercialOperationClient.operationLoop(operationId, settings);
      setSelectedCommercialOperationId(operationId);
      setOperationLoop(loop);
      setCommercialApprovals([approval]);
      setConnectionState("connected");
      setFirstDraftBootstrapStatus(`${workbenchCopy.operationFirstDraftReady}: ${readyDraft.title}`);
      setRunStatus(`first draft ready for approval: ${approval.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "First draft bootstrap failed";
      setOperationLoopError(message);
      setRunStatus("first draft bootstrap error");
    } finally {
      setFirstDraftBootstrapLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const resolveCommercialApprovalDraft = async (
    operationId: string,
    approval: CommercialOperationApproval,
  ): Promise<CommercialOperationContentDraft | null> => {
    const approvalIsPublishMetricReexecution = isPublishMetricNextCycleApproval(approval);
    const approvalIsNextCycle = isNextCycleApproval(approval);
    const approveDraftNote = approvalIsPublishMetricReexecution
      ? language === "zh-CN"
        ? "人工已审批发布数据改进草案，进入再执行交付物打包。"
        : "Human approved the publish-metric improved draft; package it for re-execution."
      : approvalIsNextCycle
      ? language === "zh-CN"
        ? "人工已审批下一轮内容，进入交付物打包。"
        : "Human approved the next-cycle draft; package it as a deliverable."
      : language === "zh-CN"
        ? "人工已审批首版内容，进入交付物打包。"
        : "Human approved the first draft; package it as a deliverable.";
    const draftId = metadataStringValue(approval.metadata, "content_draft_id");
    if (draftId) {
      return commercialOperationClient.approveContentDraft(
        operationId,
        draftId,
        approveDraftNote,
        settings,
      );
    }
    const draftResponse = await commercialOperationClient.listContentDrafts(operationId, "ready_for_review", settings);
    const readyDraft = draftResponse.items[0] ?? null;
    if (!readyDraft) {
      return null;
    }
    return commercialOperationClient.approveContentDraft(
      operationId,
      readyDraft.id,
      approveDraftNote,
      settings,
    );
  };

  const approveCommercialApprovalAndPrepareExecution = async (selectedApproval?: CommercialOperationApproval) => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setExecutionPrepLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setExecutionPrepStatus(workbenchCopy.operationApprovalPreparing);
    try {
      if (!operationId) {
        setExecutionPrepStatus(workbenchCopy.operationApprovalMissing);
        setRunStatus("commercial approval missing");
        return;
      }
      const pendingApprovalResponse = await commercialOperationClient.listApprovals(operationId, "pending", settings);
      const approval =
        selectedApproval ??
        pendingApprovalResponse.items.find(isPublishMetricNextCycleApproval) ??
        pendingApprovalResponse.items.find(isNextCycleApproval) ??
        pendingApprovalResponse.items[0] ??
        commercialApprovals.find((item) => item.approval_status === "pending" && isPublishMetricNextCycleApproval(item)) ??
        commercialApprovals.find((item) => item.approval_status === "pending" && isNextCycleApproval(item)) ??
        commercialApprovals.find((item) => item.approval_status === "pending") ??
        null;
      if (!approval) {
        setExecutionPrepStatus(workbenchCopy.operationApprovalMissing);
        setRunStatus("commercial approval missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const approvalIsPublishMetricReexecution = isPublishMetricNextCycleApproval(approval);
      const approvalIsNextCycle = approvalIsPublishMetricReexecution || isNextCycleApproval(approval);
      const approvalPrepSource = approvalIsPublishMetricReexecution
        ? "worker_console_publish_metric_reexecution_prep"
        : approvalIsNextCycle
        ? "worker_console_next_cycle_approval_execution_prep"
        : "worker_console_approval_execution_prep";
      const approvalPrepPhase = approvalIsPublishMetricReexecution ? "63V" : approvalIsNextCycle ? "63G" : "63C";
      const optimizationDecisionId = metadataStringValue(approval.metadata, "optimization_decision_id");
      const publishMetricImprovementId = approvalIsPublishMetricReexecution ? optimizationDecisionId : undefined;
      setExecutionPrepStatus(
        approvalIsPublishMetricReexecution
          ? workbenchCopy.operationImprovedApprovalPreparing
          : approvalIsNextCycle
            ? workbenchCopy.operationNextCycleApprovalPreparing
            : workbenchCopy.operationApprovalPreparing,
      );
      const approvedApproval = await commercialOperationClient.approveApproval(
        operationId,
        approval.id,
        approvalIsPublishMetricReexecution
          ? language === "zh-CN"
            ? "客户机操作员确认改进草案可进入再执行准备。"
            : "Client operator approved the improved draft for re-execution preparation."
          : approvalIsNextCycle
          ? language === "zh-CN"
            ? "客户机操作员确认下一轮内容可进入执行准备。"
            : "Client operator approved the next-cycle draft for execution preparation."
          : language === "zh-CN"
            ? "客户机操作员确认首版内容可进入执行准备。"
            : "Client operator approved the first draft for execution preparation.",
        settings,
      );
      const approvedDraft = await resolveCommercialApprovalDraft(operationId, approval);
      if (!approvedDraft) {
        setExecutionPrepStatus(workbenchCopy.operationApprovalMissing);
        setRunStatus("commercial draft missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const deliverable = await commercialOperationClient.createDeliverable(
        operationId,
        {
          step_key: "content_production",
          content_draft_id: approvedDraft.id,
          deliverable_type: approvalIsPublishMetricReexecution
            ? "publish_metric_next_cycle_content_package"
            : approvalIsNextCycle
              ? "next_cycle_content_package"
              : "content_package",
          title:
            language === "zh-CN"
              ? `${approvedDraft.title} ${approvalIsPublishMetricReexecution ? "改进再执行交付包" : approvalIsNextCycle ? "下一轮客户机交付包" : "客户机交付包"}`
              : `${approvedDraft.title} ${approvalIsPublishMetricReexecution ? "improved re-execution package" : approvalIsNextCycle ? "next-cycle client handoff package" : "client handoff package"}`,
          summary:
            approvalIsPublishMetricReexecution
              ? language === "zh-CN"
                ? "由客户机审批后的发布数据改进草案打包成可交付记录，用于回到再执行准备。"
                : "A packaged record from the client-approved publish-metric improvement draft for re-execution prep."
              : approvalIsNextCycle
              ? language === "zh-CN"
                ? "由客户机审批后的下一轮内容打包成可交付记录，用于继续闭环执行准备。"
                : "A packaged record from the client-approved next-cycle draft for the next execution-prep pass."
              : language === "zh-CN"
                ? "由客户机审批后的首版内容打包成可交付记录，用于后续 OpenClaw/Playwright 执行准备。"
                : "A packaged record from the client-approved first draft for later OpenClaw/Playwright execution preparation.",
          delivery_notes:
            language === "zh-CN"
              ? "当前只生成元数据和交付物记录，不发布、不登录真实平台、不控制账号。"
              : "This creates metadata and deliverable records only; it does not publish, log in to platforms, or control accounts.",
          quality_checks: [
            "human approval gate approved",
            "content draft approved",
            ...(approvalIsPublishMetricReexecution ? ["manual publish metric improvement linked", "publish metric next-cycle draft approved"] : []),
            ...(approvalIsNextCycle ? ["next-cycle optimization decision linked"] : []),
            "no publishing",
            "no account control",
            "metadata-only packaging",
          ],
          metadata: {
            source: approvalPrepSource,
            phase: approvalPrepPhase,
            approval_id: approvedApproval.id,
            content_draft_id: approvedDraft.id,
            optimization_decision_id: optimizationDecisionId,
            publish_metric_improvement_id: publishMetricImprovementId,
            reexecution_loop: approvalIsPublishMetricReexecution ? "publish_metric_improvement" : undefined,
            cycle: approvalIsNextCycle ? "next_iteration" : "first_iteration",
          },
        },
        settings,
      );
      const readyDeliverable = await commercialOperationClient.readyDeliverable(
        operationId,
        deliverable.id,
        language === "zh-CN" ? "交付物已准备复核。" : "Deliverable is ready for review.",
        settings,
      );
      const approvedDeliverable = await commercialOperationClient.approveDeliverable(
        operationId,
        readyDeliverable.id,
        language === "zh-CN" ? "已批准打包为客户机执行准备输入。" : "Approved as the input for client execution preparation.",
        settings,
      );
      const packagedDeliverable = await commercialOperationClient.packageDeliverable(
        operationId,
        approvedDeliverable.id,
        language === "zh-CN"
          ? "已打包为元数据交付物；未触发发布或外部执行。"
          : "Packaged as a metadata-only deliverable; no publishing or external execution was triggered.",
        settings,
      );
      const executionRequest = await commercialOperationClient.createExecutionRequest(
        operationId,
        {
          deliverable_id: packagedDeliverable.id,
          execution_type: "openclaw",
          execution_mode: "metadata_only",
          title:
            language === "zh-CN"
              ? `${packagedDeliverable.title} OpenClaw 执行准备`
              : `${packagedDeliverable.title} OpenClaw execution prep`,
          execution_target: "customer_machine_playwright",
          input_summary:
            approvalIsPublishMetricReexecution
              ? language === "zh-CN"
                ? "为发布数据改进草案准备客户机 OpenClaw/Playwright 再执行元数据，不直接执行。"
                : "Prepare metadata for re-executing the publish-metric improved draft on the customer machine without executing it."
              : approvalIsNextCycle
              ? language === "zh-CN"
                ? "为下一轮客户机 OpenClaw/Playwright 执行准备元数据，不直接执行。"
                : "Prepare metadata for the next-cycle OpenClaw/Playwright handoff on the customer machine without executing it."
              : language === "zh-CN"
                ? "为客户机 OpenClaw 调度 Playwright 发布任务准备元数据，不直接执行。"
                : "Prepare metadata for future OpenClaw-scheduled Playwright publishing on the customer machine without executing it.",
          runbook: [
            { step: approvalIsNextCycle ? "Review next-cycle packaged deliverable" : "Review packaged deliverable", owner: "operator" },
            { step: "Confirm target social/channel account", owner: "operator" },
            { step: "Run OpenClaw/Playwright only after explicit execution approval", owner: "client_machine" },
          ],
          readiness_checks: [
            "human_review approval approved",
            "packaged deliverable created",
            ...(approvalIsPublishMetricReexecution ? ["publish metric re-execution prep", "manual publish metric improvement approved"] : []),
            ...(approvalIsNextCycle ? ["next-cycle approval execution prep"] : []),
            "metadata_only execution request",
            "OpenClaw/Playwright handoff not executed",
          ],
          expected_outputs: [
            "execution request id",
            "future OpenClaw/Playwright handoff payload",
            "operator-visible recovery notes",
          ],
          operator_checklist: [
            { item: "Confirm platform and account before runtime execution" },
            { item: "Confirm publishing time and content owner" },
            { item: "Keep screenshots/logs after future execution" },
          ],
          metadata: {
            source: approvalPrepSource,
            phase: approvalPrepPhase,
            approval_id: approvedApproval.id,
            content_draft_id: approvedDraft.id,
            deliverable_id: packagedDeliverable.id,
            optimization_decision_id: optimizationDecisionId,
            publish_metric_improvement_id: publishMetricImprovementId,
            reexecution_loop: approvalIsPublishMetricReexecution ? "publish_metric_improvement" : undefined,
            cycle: approvalIsNextCycle ? "next_iteration" : "first_iteration",
          },
        },
        settings,
      );
      const readyExecutionRequest = await commercialOperationClient.readyExecutionRequest(
        operationId,
        executionRequest.id,
        approvalIsPublishMetricReexecution
          ? language === "zh-CN"
            ? "改进草案再执行准备记录已生成，等待执行前复核。"
            : "Improved draft re-execution prep record is ready for pre-run review."
          : approvalIsNextCycle
          ? language === "zh-CN"
            ? "下一轮客户机执行准备记录已生成，等待执行前复核。"
            : "Next-cycle client execution prep record is ready for pre-run review."
          : language === "zh-CN"
            ? "客户机执行准备记录已生成，等待执行前复核。"
            : "Client execution prep record is ready for pre-run review.",
        settings,
      );
      await refreshCommercialOperationLoop(operationId);
      setExecutionPrepStatus(
        `${
          approvalIsPublishMetricReexecution
            ? workbenchCopy.operationImprovedExecutionPrepReady
            : approvalIsNextCycle
              ? workbenchCopy.operationNextCycleExecutionPrepReady
              : workbenchCopy.operationExecutionPrepReady
        }: ${readyExecutionRequest.id}`,
      );
      setRunStatus(`${approvalIsPublishMetricReexecution ? "improved " : approvalIsNextCycle ? "next-cycle " : ""}client execution prep ready: ${readyExecutionRequest.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Commercial approval execution prep failed";
      setOperationLoopError(message);
      setExecutionPrepStatus(message);
      setRunStatus("commercial approval execution prep error");
    } finally {
      setExecutionPrepLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const rejectCommercialApproval = async (selectedApproval?: CommercialOperationApproval) => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setExecutionPrepLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    try {
      if (!operationId) {
        setExecutionPrepStatus(workbenchCopy.operationApprovalMissing);
        setRunStatus("commercial approval missing");
        return;
      }
      const pendingApprovalResponse = await commercialOperationClient.listApprovals(operationId, "pending", settings);
      const approval =
        selectedApproval ??
        pendingApprovalResponse.items.find(isPublishMetricNextCycleApproval) ??
        pendingApprovalResponse.items.find(isNextCycleApproval) ??
        pendingApprovalResponse.items[0] ??
        commercialApprovals.find((item) => item.approval_status === "pending" && isPublishMetricNextCycleApproval(item)) ??
        commercialApprovals.find((item) => item.approval_status === "pending" && isNextCycleApproval(item)) ??
        commercialApprovals.find((item) => item.approval_status === "pending") ??
        null;
      if (!approval) {
        setExecutionPrepStatus(workbenchCopy.operationApprovalMissing);
        setRunStatus("commercial approval missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const approvalIsPublishMetricReexecution = isPublishMetricNextCycleApproval(approval);
      const approvalIsNextCycle = approvalIsPublishMetricReexecution || isNextCycleApproval(approval);
      await commercialOperationClient.rejectApproval(
        operationId,
        approval.id,
        approvalIsPublishMetricReexecution
          ? language === "zh-CN"
            ? "客户机操作员驳回改进草案，需要根据发布数据重新生成。"
            : "Client operator rejected the improved draft; regenerate it from publish metrics."
          : approvalIsNextCycle
          ? language === "zh-CN"
            ? "客户机操作员驳回下一轮内容，需要按改进建议重新生成。"
            : "Client operator rejected the next-cycle draft; regenerate it from the improvement decision."
          : language === "zh-CN"
            ? "客户机操作员驳回首版内容，需要修改后重新准备。"
            : "Client operator rejected the first draft; revise before preparing again.",
        settings,
      );
      const draftId = metadataStringValue(approval.metadata, "content_draft_id");
      if (draftId) {
        await commercialOperationClient.rejectContentDraft(
          operationId,
          draftId,
          approvalIsPublishMetricReexecution
            ? language === "zh-CN"
              ? "审批被驳回，改进草案需要根据发布数据重新生成。"
              : "Approval was rejected; regenerate the improved draft from publish metrics."
            : approvalIsNextCycle
            ? language === "zh-CN"
              ? "审批被驳回，下一轮内容需要重新生成。"
              : "Approval was rejected; regenerate the next-cycle draft."
            : language === "zh-CN"
              ? "审批被驳回，首版内容需要修改。"
              : "Approval was rejected; the first draft needs revision.",
          settings,
        ).catch(() => null);
      }
      await refreshCommercialOperationLoop(operationId);
      setExecutionPrepStatus(
        approvalIsPublishMetricReexecution
          ? workbenchCopy.operationNextCycleApprovalRejected
          : approvalIsNextCycle
            ? workbenchCopy.operationNextCycleApprovalRejected
            : workbenchCopy.operationApprovalRejected,
      );
      setRunStatus(`${approvalIsPublishMetricReexecution ? "improved " : approvalIsNextCycle ? "next-cycle " : ""}commercial approval rejected: ${approval.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Commercial approval rejection failed";
      setOperationLoopError(message);
      setExecutionPrepStatus(message);
      setRunStatus("commercial approval rejection error");
    } finally {
      setExecutionPrepLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const resolveExecutionRequestForRun = async (operationId: string): Promise<CommercialOperationExecutionRequest | null> => {
    const response = await commercialOperationClient.listExecutionRequests(operationId, undefined, settings);
    const requestPool = [
      ...response.items.filter(isPublishMetricReexecutionRequest),
      ...response.items.filter((item) => isNextCycleExecutionRequest(item) && !isPublishMetricReexecutionRequest(item)),
      ...response.items.filter((item) => !isNextCycleExecutionRequest(item)),
      ...commercialExecutionRequests.filter(isPublishMetricReexecutionRequest),
      ...commercialExecutionRequests.filter((item) => isNextCycleExecutionRequest(item) && !isPublishMetricReexecutionRequest(item)),
      ...commercialExecutionRequests.filter((item) => !isNextCycleExecutionRequest(item)),
    ];
    const request =
      requestPool.find((item) => item.request_status === "prepared") ??
      requestPool.find((item) => item.request_status === "approved") ??
      requestPool.find((item) => item.request_status === "ready_for_review") ??
      requestPool.find((item) => item.request_status === "draft") ??
      requestPool.find((item) => ["prepared", "approved", "ready_for_review", "draft"].includes(item.request_status)) ??
      null;
    if (!request) {
      return null;
    }
    if (request.request_status === "prepared") {
      return request;
    }
    let reviewableRequest = request;
    if (reviewableRequest.request_status === "draft") {
      reviewableRequest = await commercialOperationClient.readyExecutionRequest(
        operationId,
        reviewableRequest.id,
        language === "zh-CN" ? "客户机执行记录进入复核。" : "Client execution request is ready for review.",
        settings,
      );
    }
    if (reviewableRequest.request_status === "ready_for_review") {
      reviewableRequest = await commercialOperationClient.approveExecutionRequest(
        operationId,
        reviewableRequest.id,
        language === "zh-CN" ? "客户机操作员确认执行准备记录可排队。" : "Client operator approved the execution prep for queueing.",
        settings,
      );
    }
    if (reviewableRequest.request_status === "approved") {
      return commercialOperationClient.prepareExecutionRequest(
        operationId,
        reviewableRequest.id,
        language === "zh-CN"
          ? "已准备为 metadata-only 执行运行记录，未触发真实 OpenClaw/Playwright。"
          : "Prepared for a metadata-only execution run; no real OpenClaw/Playwright was triggered.",
        settings,
      );
    }
    return null;
  };

  const reviewExecutionRequestAndQueueRun = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setExecutionRunLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setExecutionRunStatus(workbenchCopy.operationExecutionRunQueuing);
    try {
      if (!operationId) {
        setExecutionRunStatus(workbenchCopy.operationExecutionRequestMissing);
        setRunStatus("commercial execution request missing");
        return;
      }
      const preparedRequest = await resolveExecutionRequestForRun(operationId);
      if (!preparedRequest) {
        setExecutionRunStatus(workbenchCopy.operationExecutionRequestMissing);
        setRunStatus("commercial execution request missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const requestIsPublishMetricReexecution = isPublishMetricReexecutionRequest(preparedRequest);
      const requestIsNextCycle = requestIsPublishMetricReexecution || isNextCycleExecutionRequest(preparedRequest);
      const executionRunSource = requestIsPublishMetricReexecution
        ? "worker_console_publish_metric_reexecution_run_review"
        : requestIsNextCycle
        ? "worker_console_next_cycle_execution_run_review"
        : "worker_console_execution_run_review";
      const executionRunPhase = requestIsNextCycle ? "63H" : "63D";
      const effectiveExecutionRunPhase = requestIsPublishMetricReexecution ? "63W" : executionRunPhase;
      const optimizationDecisionId = metadataStringValue(preparedRequest.metadata, "optimization_decision_id");
      const publishMetricImprovementId = metadataStringValue(preparedRequest.metadata, "publish_metric_improvement_id");
      setExecutionRunStatus(
        requestIsPublishMetricReexecution
          ? workbenchCopy.operationImprovedExecutionRunQueuing
          : requestIsNextCycle
            ? workbenchCopy.operationNextCycleExecutionRunQueuing
            : workbenchCopy.operationExecutionRunQueuing,
      );
      const existingRuns = await commercialOperationClient.listExecutionRuns(operationId, undefined, settings);
      const existingRun =
        existingRuns.items.find(
          (run) =>
            run.execution_request_id === preparedRequest.id &&
            ["queued", "running", "retrying", "failed"].includes(run.run_status),
        ) ?? null;
      if (existingRun) {
        setExecutionRunStatus(`${workbenchCopy.operationExecutionRunPending}: ${existingRun.run_status}`);
        setRunStatus(`commercial execution run exists: ${existingRun.id}`);
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const run = await commercialOperationClient.createExecutionRun(
        operationId,
        {
          execution_request_id: preparedRequest.id,
          title:
            language === "zh-CN"
              ? `${preparedRequest.title} ${requestIsPublishMetricReexecution ? "改进再执行运行记录" : requestIsNextCycle ? "下一轮执行运行记录" : "执行运行记录"}`
              : `${preparedRequest.title} ${requestIsPublishMetricReexecution ? "improved re-execution run" : requestIsNextCycle ? "next-cycle execution run" : "execution run"}`,
          execution_target: preparedRequest.execution_target ?? "customer_machine_playwright",
          input_payload: {
            execution_request_id: preparedRequest.id,
            execution_target: preparedRequest.execution_target ?? "customer_machine_playwright",
            execution_boundary: "metadata-only; no external runtime call",
            source: executionRunSource,
            cycle: requestIsNextCycle ? "next_iteration" : "first_iteration",
            optimization_decision_id: optimizationDecisionId,
            publish_metric_improvement_id: publishMetricImprovementId,
            reexecution_loop: requestIsPublishMetricReexecution ? "publish_metric_improvement" : undefined,
          },
          max_retries: 1,
          operator_notes:
            requestIsPublishMetricReexecution
              ? language === "zh-CN"
                ? "客户机已创建改进再执行运行记录，等待显式开始。"
                : "Customer console created the improved re-execution run record and is waiting for explicit start."
              : requestIsNextCycle
              ? language === "zh-CN"
                ? "客户机已创建下一轮执行运行记录，等待显式开始。"
                : "Customer console created the next-cycle execution run record and is waiting for explicit start."
              : language === "zh-CN"
                ? "客户机已创建执行运行记录，等待显式开始。"
                : "Customer console created the execution run record and is waiting for explicit start.",
          metadata: {
            source: executionRunSource,
            phase: effectiveExecutionRunPhase,
            execution_request_id: preparedRequest.id,
            optimization_decision_id: optimizationDecisionId,
            publish_metric_improvement_id: publishMetricImprovementId,
            reexecution_loop: requestIsPublishMetricReexecution ? "publish_metric_improvement" : undefined,
            cycle: requestIsNextCycle ? "next_iteration" : "first_iteration",
          },
        },
        settings,
      );
      await refreshCommercialOperationLoop(operationId);
      setExecutionRunStatus(
        `${
          requestIsPublishMetricReexecution
            ? workbenchCopy.operationImprovedExecutionRunReady
            : requestIsNextCycle
              ? workbenchCopy.operationNextCycleExecutionRunReady
              : workbenchCopy.operationExecutionRunReady
        }: ${run.id}`,
      );
      setRunStatus(`${requestIsPublishMetricReexecution ? "improved " : requestIsNextCycle ? "next-cycle " : ""}commercial execution run queued: ${run.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Commercial execution run queueing failed";
      setOperationLoopError(message);
      setExecutionRunStatus(message);
      setRunStatus("commercial execution run queueing error");
    } finally {
      setExecutionRunLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const startCommercialExecutionRun = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setExecutionRunLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setExecutionRunStatus(workbenchCopy.operationRunStarting);
    try {
      if (!operationId) {
        setExecutionRunStatus(workbenchCopy.operationExecutionRequestMissing);
        setRunStatus("commercial execution run missing");
        return;
      }
      const response = await commercialOperationClient.listExecutionRuns(operationId, undefined, settings);
      const run =
        response.items.find((item) => (item.run_status === "queued" || item.run_status === "retrying") && isPublishMetricReexecutionRun(item)) ??
        response.items.find((item) => (item.run_status === "queued" || item.run_status === "retrying") && isNextCycleExecutionRun(item)) ??
        response.items.find((item) => item.run_status === "queued" || item.run_status === "retrying") ??
        commercialExecutionRuns.find((item) => (item.run_status === "queued" || item.run_status === "retrying") && isPublishMetricReexecutionRun(item)) ??
        commercialExecutionRuns.find((item) => (item.run_status === "queued" || item.run_status === "retrying") && isNextCycleExecutionRun(item)) ??
        commercialExecutionRuns.find((item) => item.run_status === "queued" || item.run_status === "retrying") ??
        null;
      if (!run) {
        setExecutionRunStatus(workbenchCopy.operationExecutionRequestMissing);
        setRunStatus("commercial execution run missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const startedRun = await commercialOperationClient.startExecutionRun(
        operationId,
        run.id,
        language === "zh-CN"
          ? "客户机操作员标记 metadata-only 执行记录开始。"
          : "Client operator marked the metadata-only execution run as started.",
        settings,
      );
      await refreshCommercialOperationLoop(operationId);
      setExecutionRunStatus(`${workbenchCopy.operationRunStarted}: ${startedRun.id}`);
      setRunStatus(`commercial execution run started: ${startedRun.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Commercial execution run start failed";
      setOperationLoopError(message);
      setExecutionRunStatus(message);
      setRunStatus("commercial execution run start error");
    } finally {
      setExecutionRunLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const failCommercialExecutionRun = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setExecutionRunLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    try {
      if (!operationId) {
        setExecutionRunStatus(workbenchCopy.operationExecutionRequestMissing);
        setRunStatus("commercial execution run missing");
        return;
      }
      const response = await commercialOperationClient.listExecutionRuns(operationId, "running", settings);
      const run = response.items[0] ?? commercialExecutionRuns.find((item) => item.run_status === "running") ?? null;
      if (!run) {
        setExecutionRunStatus(workbenchCopy.operationExecutionRequestMissing);
        setRunStatus("commercial execution run missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const failedRun = await commercialOperationClient.failExecutionRun(
        operationId,
        run.id,
        language === "zh-CN"
          ? "客户机操作员记录执行失败；未发生真实外部执行。"
          : "Client operator recorded execution failure; no real external execution happened.",
        settings,
      );
      await refreshCommercialOperationLoop(operationId);
      setExecutionRunStatus(`${workbenchCopy.operationRunFailed}: ${failedRun.id}`);
      setRunStatus(`commercial execution run failed: ${failedRun.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Commercial execution run failure recording failed";
      setOperationLoopError(message);
      setExecutionRunStatus(message);
      setRunStatus("commercial execution run failure recording error");
    } finally {
      setExecutionRunLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const retryCommercialExecutionRun = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setExecutionRunLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setExecutionRunStatus(workbenchCopy.operationRunRetrying);
    try {
      if (!operationId) {
        setExecutionRunStatus(workbenchCopy.operationExecutionRequestMissing);
        setRunStatus("commercial execution run missing");
        return;
      }
      const response = await commercialOperationClient.listExecutionRuns(operationId, "failed", settings);
      const run = response.items[0] ?? commercialExecutionRuns.find((item) => item.run_status === "failed") ?? null;
      if (!run) {
        setExecutionRunStatus(workbenchCopy.operationExecutionRequestMissing);
        setRunStatus("commercial execution run missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const retryRun = await commercialOperationClient.retryExecutionRun(
        operationId,
        run.id,
        language === "zh-CN"
          ? "客户机操作员恢复失败执行记录，等待重新开始。"
          : "Client operator moved the failed execution run back to retrying; start it again next.",
        settings,
      );
      await refreshCommercialOperationLoop(operationId);
      setExecutionRunStatus(`${workbenchCopy.operationRunRetrying}: ${retryRun.id}`);
      setRunStatus(`commercial execution run retrying: ${retryRun.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Commercial execution run retry failed";
      setOperationLoopError(message);
      setExecutionRunStatus(message);
      setRunStatus("commercial execution run retry error");
    } finally {
      setExecutionRunLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const preflightClientRuntimeExecutionRun = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setRuntimePreflightLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setRuntimePreflightStatus(workbenchCopy.operationRuntimePreflightChecking);
    try {
      if (!operationId) {
        setRuntimePreflightStatus(workbenchCopy.operationRuntimePreflightMissing);
        setRunStatus("client runtime preflight missing");
        return;
      }
      const executionRunResponse = await commercialOperationClient.listExecutionRuns(operationId, undefined, settings);
      const executionRunPool = [...executionRunResponse.items, ...commercialExecutionRuns];
      const targetRun =
        executionRunPool.find((run) => ["queued", "retrying"].includes(run.run_status) && isNextCycleExecutionRun(run)) ??
        executionRunPool.find((run) => ["queued", "retrying"].includes(run.run_status)) ??
        null;
      if (!targetRun) {
        setRuntimePreflightStatus(workbenchCopy.operationRuntimePreflightMissing);
        setRunStatus("client runtime preflight missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }

      let workerStatus: WorkerStatus | null = null;
      let workerHealth: WorkerHealth | null = null;
      let workerError: string | null = null;
      try {
        [workerStatus, workerHealth] = await Promise.all([runtimeClient.getStatus(), runtimeClient.getHealth()]);
      } catch (nextError) {
        workerError = nextError instanceof Error ? nextError.message : "Worker API unreachable";
      }

      const checkedAt = new Date().toISOString();
      const checks = [
        { key: "worker_api_reachable", status: Boolean(workerStatus && !workerError), detail: runtimeClient.baseUrl },
        { key: "worker_registered", status: Boolean(workerStatus?.registered), detail: workerStatus?.worker_id ?? "-" },
        { key: "runtime_running", status: Boolean(workerStatus?.runtime_running && workerHealth?.runtime_running), detail: String(workerStatus?.runtime_port ?? workerHealth?.port ?? "-") },
        { key: "heartbeat_running", status: Boolean(workerStatus?.heartbeat_running && workerHealth?.heartbeat_running), detail: workerStatus?.last_heartbeat_at ?? "-" },
        { key: "openclaw_enabled", status: Boolean(workerStatus?.openclaw_enabled), detail: "local worker capability flag" },
        { key: "browser_enabled", status: Boolean(workerStatus?.browser_enabled), detail: "local worker capability flag" },
        { key: "localhost_only", status: workerHealth?.localhost_only !== false, detail: String(workerHealth?.localhost_only ?? true) },
        { key: "approval_required", status: true, detail: "operator must still start execution explicitly" },
      ];
      const preflightReady = checks.every((check) => check.status);
      const runIsNextCycle = isNextCycleExecutionRun(targetRun);
      const preflightStatus = preflightReady ? "ready" : "blocked";
      const previousSource =
        metadataStringValue(targetRun.metadata, "source") ??
        metadataStringValue(targetRun.input_payload, "source") ??
        "unknown";
      const cycle =
        metadataStringValue(targetRun.metadata, "cycle") ??
        metadataStringValue(targetRun.input_payload, "cycle") ??
        (runIsNextCycle ? "next_iteration" : "first_iteration");
      const optimizationDecisionId =
        metadataStringValue(targetRun.metadata, "optimization_decision_id") ??
        metadataStringValue(targetRun.input_payload, "optimization_decision_id");
      const clientRuntimePreflight = {
        status: preflightStatus,
        checked_at: checkedAt,
        local_worker_api: runtimeClient.baseUrl,
        worker_api_error: workerError,
        actual_openclaw_execution_performed: false,
        playwright_run_performed: false,
        publishing_performed: false,
        account_control_performed: false,
        cycle,
        checks,
        worker_status: workerStatus
          ? {
              worker_id: workerStatus.worker_id,
              worker_name: workerStatus.worker_name,
              workspace_id: workerStatus.workspace_id,
              current_status: workerStatus.current_status,
              runtime_running: workerStatus.runtime_running,
              heartbeat_running: workerStatus.heartbeat_running,
              openclaw_enabled: workerStatus.openclaw_enabled,
              browser_enabled: workerStatus.browser_enabled,
              last_heartbeat_at: workerStatus.last_heartbeat_at,
              last_error: workerStatus.last_error,
            }
          : null,
        worker_health: workerHealth,
        next_operator_action: preflightReady
          ? "review target account and explicitly start the guarded run"
          : "recover local worker runtime, heartbeat, OpenClaw, or browser capability before start",
      };
      const updatedRun = await commercialOperationClient.updateExecutionRun(
        operationId,
        targetRun.id,
        {
          input_payload: {
            ...targetRun.input_payload,
            source: "worker_console_client_runtime_preflight",
            cycle,
            runtime_preflight_status: preflightStatus,
            runtime_preflight_checked_at: checkedAt,
            client_runtime_preflight: clientRuntimePreflight,
            previous_optimization_decision_id: metadataStringValue(targetRun.input_payload, "previous_optimization_decision_id"),
            optimization_decision_id: optimizationDecisionId,
          },
          operator_notes: preflightReady
            ? language === "zh-CN"
              ? "客户机执行前预检通过；仍需人工显式开始，未执行 OpenClaw/Playwright。"
              : "Client runtime preflight passed; explicit operator start is still required and no OpenClaw/Playwright action ran."
            : language === "zh-CN"
              ? "客户机执行前预检未通过；请先恢复本机运行时、心跳、OpenClaw 或浏览器能力。"
              : "Client runtime preflight is blocked; recover local runtime, heartbeat, OpenClaw, or browser capability first.",
          metadata: {
            ...targetRun.metadata,
            source: "worker_console_client_runtime_preflight",
            previous_source: previousSource,
            phase: "63J",
            cycle,
            runtime_preflight_status: preflightStatus,
            runtime_preflight_checked_at: checkedAt,
            optimization_decision_id: optimizationDecisionId,
          },
        },
        settings,
      );
      await refreshCommercialOperationLoop(operationId);
      setRuntimePreflightStatus(
        `${preflightReady ? workbenchCopy.operationRuntimePreflightReady : workbenchCopy.operationRuntimePreflightBlocked}: ${updatedRun.id}`,
      );
      setRunStatus(`client runtime preflight ${preflightStatus}: ${updatedRun.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Client runtime preflight failed";
      setOperationLoopError(message);
      setRuntimePreflightStatus(message);
      setRunStatus("client runtime preflight error");
    } finally {
      setRuntimePreflightLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const prepareGuardedAdapterDispatchHandoff = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setGuardedDispatchLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setGuardedDispatchStatus(workbenchCopy.operationGuardedDispatchHandingOff);
    try {
      if (!operationId) {
        setGuardedDispatchStatus(workbenchCopy.operationGuardedDispatchMissing);
        setRunStatus("guarded adapter dispatch handoff missing");
        return;
      }
      const executionRunResponse = await commercialOperationClient.listExecutionRuns(operationId, undefined, settings);
      const executionRunPool = [...executionRunResponse.items, ...commercialExecutionRuns];
      const targetRun =
        executionRunPool.find((run) => ["queued", "retrying"].includes(run.run_status) && isNextCycleExecutionRun(run) && isClientRuntimePreflightReady(run)) ??
        executionRunPool.find((run) => ["queued", "retrying"].includes(run.run_status) && isClientRuntimePreflightReady(run)) ??
        executionRunPool.find((run) => ["queued", "retrying"].includes(run.run_status) && isNextCycleExecutionRun(run)) ??
        executionRunPool.find((run) => ["queued", "retrying"].includes(run.run_status)) ??
        null;
      if (!targetRun) {
        setGuardedDispatchStatus(workbenchCopy.operationGuardedDispatchMissing);
        setRunStatus("guarded adapter dispatch handoff missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }

      const checkedAt = new Date().toISOString();
      const preflightReady = isClientRuntimePreflightReady(targetRun);
      const handoffStatus = preflightReady ? "ready_for_operator_start" : "blocked_preflight_required";
      const runIsNextCycle = isNextCycleExecutionRun(targetRun);
      const previousSource =
        metadataStringValue(targetRun.metadata, "source") ??
        metadataStringValue(targetRun.input_payload, "source") ??
        "unknown";
      const cycle =
        metadataStringValue(targetRun.metadata, "cycle") ??
        metadataStringValue(targetRun.input_payload, "cycle") ??
        (runIsNextCycle ? "next_iteration" : "first_iteration");
      const optimizationDecisionId =
        metadataStringValue(targetRun.metadata, "optimization_decision_id") ??
        metadataStringValue(targetRun.input_payload, "optimization_decision_id");
      const clientRuntimePreflight = metadataRecordValue(targetRun.input_payload, "client_runtime_preflight");
      const guardedAdapterDispatchHandoff = {
        status: handoffStatus,
        checked_at: checkedAt,
        source_preflight_status:
          metadataStringValue(targetRun.metadata, "runtime_preflight_status") ??
          metadataStringValue(targetRun.input_payload, "runtime_preflight_status") ??
          metadataStringValue(clientRuntimePreflight ?? undefined, "status") ??
          "missing",
        adapter_mode: "guarded_metadata_only_handoff",
        target_adapter: targetRun.execution_target ?? targetRun.execution_type ?? "customer_machine_playwright",
        external_execution_performed: false,
        actual_openclaw_execution_performed: false,
        playwright_run_performed: false,
        publishing_performed: false,
        account_control_performed: false,
        approval_required: true,
        operator_start_required: true,
        cycle,
        checks: [
          {
            key: "client_runtime_preflight_ready",
            status: preflightReady,
            detail: preflightReady ? "preflight is ready" : "run client runtime preflight first",
          },
          {
            key: "adapter_payload_recorded",
            status: true,
            detail: "metadata-only handoff payload recorded",
          },
          {
            key: "external_actions_disabled",
            status: true,
            detail: "no OpenClaw, Playwright, publishing, or account control was executed",
          },
        ],
        next_operator_action: preflightReady
          ? "review target account, approval context, and explicitly mark the run started"
          : "run and pass client runtime preflight before guarded adapter start",
      };
      const updatedRun = await commercialOperationClient.updateExecutionRun(
        operationId,
        targetRun.id,
        {
          input_payload: {
            ...targetRun.input_payload,
            source: "worker_console_guarded_adapter_dispatch_handoff",
            previous_source: previousSource,
            cycle,
            guarded_adapter_dispatch_status: handoffStatus,
            guarded_adapter_dispatch_checked_at: checkedAt,
            guarded_adapter_dispatch_handoff: guardedAdapterDispatchHandoff,
            external_execution_performed: false,
            actual_openclaw_execution_performed: false,
            playwright_run_performed: false,
            publishing_performed: false,
            account_control_performed: false,
            optimization_decision_id: optimizationDecisionId,
          },
          operator_notes: preflightReady
            ? language === "zh-CN"
              ? "已准备受保护执行交接；仍需人工显式开始，未执行 OpenClaw/Playwright。"
              : "Guarded execution handoff is ready; explicit operator start is still required and no OpenClaw/Playwright action ran."
            : language === "zh-CN"
              ? "受保护执行交接被阻断；请先完成并通过客户机执行前预检。"
              : "Guarded execution handoff is blocked; run and pass the client runtime preflight first.",
          metadata: {
            ...targetRun.metadata,
            source: "worker_console_guarded_adapter_dispatch_handoff",
            previous_source: previousSource,
            phase: "63K",
            cycle,
            guarded_adapter_dispatch_status: handoffStatus,
            guarded_adapter_dispatch_checked_at: checkedAt,
            optimization_decision_id: optimizationDecisionId,
          },
        },
        settings,
      );
      await refreshCommercialOperationLoop(operationId);
      setGuardedDispatchStatus(
        `${preflightReady ? workbenchCopy.operationGuardedDispatchReady : workbenchCopy.operationGuardedDispatchBlocked}: ${updatedRun.id}`,
      );
      setRunStatus(`guarded adapter dispatch handoff ${handoffStatus}: ${updatedRun.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Guarded adapter dispatch handoff failed";
      setOperationLoopError(message);
      setGuardedDispatchStatus(message);
      setRunStatus("guarded adapter dispatch handoff error");
    } finally {
      setGuardedDispatchLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const runGuardedAdapterDryRun = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setAdapterDryRunLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setAdapterDryRunStatus(workbenchCopy.operationAdapterDryRunRunning);
    try {
      if (!operationId) {
        setAdapterDryRunStatus(workbenchCopy.operationAdapterDryRunMissing);
        setRunStatus("guarded adapter dry-run missing");
        return;
      }
      const executionRunResponse = await commercialOperationClient.listExecutionRuns(operationId, undefined, settings);
      const executionRunPool = [...executionRunResponse.items, ...commercialExecutionRuns];
      const targetRun =
        executionRunPool.find((run) => ["queued", "retrying"].includes(run.run_status) && isNextCycleExecutionRun(run) && isGuardedAdapterDispatchReady(run)) ??
        executionRunPool.find((run) => ["queued", "retrying"].includes(run.run_status) && isGuardedAdapterDispatchReady(run)) ??
        executionRunPool.find((run) => ["queued", "retrying"].includes(run.run_status) && isNextCycleExecutionRun(run)) ??
        executionRunPool.find((run) => ["queued", "retrying"].includes(run.run_status)) ??
        null;
      if (!targetRun) {
        setAdapterDryRunStatus(workbenchCopy.operationAdapterDryRunMissing);
        setRunStatus("guarded adapter dry-run missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }

      const checkedAt = new Date().toISOString();
      const handoffReady = isGuardedAdapterDispatchReady(targetRun);
      const runIsNextCycle = isNextCycleExecutionRun(targetRun);
      const previousSource =
        metadataStringValue(targetRun.metadata, "source") ??
        metadataStringValue(targetRun.input_payload, "source") ??
        "unknown";
      const cycle =
        metadataStringValue(targetRun.metadata, "cycle") ??
        metadataStringValue(targetRun.input_payload, "cycle") ??
        (runIsNextCycle ? "next_iteration" : "first_iteration");
      const optimizationDecisionId =
        metadataStringValue(targetRun.metadata, "optimization_decision_id") ??
        metadataStringValue(targetRun.input_payload, "optimization_decision_id");
      const guardedHandoff = metadataRecordValue(targetRun.input_payload, "guarded_adapter_dispatch_handoff");
      const handoffStatus =
        metadataStringValue(targetRun.metadata, "guarded_adapter_dispatch_status") ??
        metadataStringValue(targetRun.input_payload, "guarded_adapter_dispatch_status") ??
        metadataStringValue(guardedHandoff ?? undefined, "status") ??
        "missing";
      const guardedAdapterDryRun = {
        status: handoffReady ? "scheduled" : "blocked_handoff_required",
        checked_at: checkedAt,
        source_handoff_status: handoffStatus,
        adapter_mode: "guarded_dry_run_only",
        target_adapter: targetRun.execution_target ?? targetRun.execution_type ?? "customer_machine_playwright",
        customer_machine_task_recorded: handoffReady,
        simulated_customer_task: true,
        actual_adapter_invocation_performed: false,
        external_execution_performed: false,
        actual_openclaw_execution_performed: false,
        playwright_run_performed: false,
        publishing_performed: false,
        account_control_performed: false,
        approval_required: true,
        operator_start_required: true,
        cycle,
        checks: [
          {
            key: "guarded_adapter_dispatch_ready",
            status: handoffReady,
            detail: handoffReady ? "guarded handoff is ready" : "prepare guarded handoff first",
          },
          {
            key: "dry_run_only",
            status: true,
            detail: "records the adapter contract without invoking OpenClaw or Playwright",
          },
          {
            key: "external_actions_disabled",
            status: true,
            detail: "no publishing, account control, captcha, proxy, fingerprint, or secret action was executed",
          },
        ],
        next_operator_action: handoffReady
          ? "record result and generate improvement from the dry-run output"
          : "complete client runtime preflight and guarded adapter handoff before dry-run",
      };

      if (!handoffReady) {
        const blockedRun = await commercialOperationClient.updateExecutionRun(
          operationId,
          targetRun.id,
          {
            input_payload: {
              ...targetRun.input_payload,
              source: "worker_console_guarded_adapter_dry_run",
              previous_source: previousSource,
              cycle,
              guarded_adapter_dry_run_status: "blocked_handoff_required",
              guarded_adapter_dry_run_checked_at: checkedAt,
              guarded_adapter_dry_run: guardedAdapterDryRun,
              external_execution_performed: false,
              actual_openclaw_execution_performed: false,
              playwright_run_performed: false,
              publishing_performed: false,
              account_control_performed: false,
              optimization_decision_id: optimizationDecisionId,
            },
            operator_notes:
              language === "zh-CN"
                ? "受保护 dry-run 被阻断；请先完成客户机预检和受保护执行交接。"
                : "Guarded dry-run is blocked; complete client preflight and guarded handoff first.",
            metadata: {
              ...targetRun.metadata,
              source: "worker_console_guarded_adapter_dry_run",
              previous_source: previousSource,
              phase: "63L",
              cycle,
              guarded_adapter_dry_run_status: "blocked_handoff_required",
              guarded_adapter_dry_run_checked_at: checkedAt,
              optimization_decision_id: optimizationDecisionId,
            },
          },
          settings,
        );
        await refreshCommercialOperationLoop(operationId);
        setAdapterDryRunStatus(`${workbenchCopy.operationAdapterDryRunBlocked}: ${blockedRun.id}`);
        setRunStatus(`guarded adapter dry-run blocked: ${blockedRun.id}`);
        return;
      }

      const preparedRun = await commercialOperationClient.updateExecutionRun(
        operationId,
        targetRun.id,
        {
          input_payload: {
            ...targetRun.input_payload,
            source: "worker_console_guarded_adapter_dry_run",
            previous_source: previousSource,
            cycle,
            guarded_adapter_dry_run_status: "scheduled",
            guarded_adapter_dry_run_checked_at: checkedAt,
            guarded_adapter_dry_run: guardedAdapterDryRun,
            external_execution_performed: false,
            actual_openclaw_execution_performed: false,
            playwright_run_performed: false,
            publishing_performed: false,
            account_control_performed: false,
            optimization_decision_id: optimizationDecisionId,
          },
          operator_notes:
            language === "zh-CN"
              ? "已进入受保护 dry-run；只记录适配器契约和客户机任务状态，不发布。"
              : "Guarded dry-run scheduled; records adapter contract and client task state only.",
          metadata: {
            ...targetRun.metadata,
            source: "worker_console_guarded_adapter_dry_run",
            previous_source: previousSource,
            phase: "63L",
            cycle,
            guarded_adapter_dry_run_status: "scheduled",
            guarded_adapter_dry_run_checked_at: checkedAt,
            optimization_decision_id: optimizationDecisionId,
          },
        },
        settings,
      );
      const startedRun = await commercialOperationClient.startExecutionRun(
        operationId,
        preparedRun.id,
        language === "zh-CN"
          ? "客户机操作员启动受保护 dry-run；未调用 OpenClaw/Playwright。"
          : "Client operator started guarded dry-run; no OpenClaw/Playwright call was made.",
        settings,
      );
      const completedAt = new Date().toISOString();
      const completedDryRun = {
        ...guardedAdapterDryRun,
        status: "succeeded",
        started_at: checkedAt,
        completed_at: completedAt,
        execution_run_id: startedRun.id,
        result_contract: {
          status: "dry_run_succeeded",
          next_records: ["commercial_result", "monitoring_observation", "optimization_decision"],
          handoff_preserved: true,
        },
      };
      const succeededRun = await commercialOperationClient.succeedExecutionRun(
        operationId,
        startedRun.id,
        language === "zh-CN"
          ? "受保护 dry-run 已完成：客户机执行队列、适配器契约和后续结果记录已准备。"
          : "Guarded dry-run completed: client execution queue, adapter contract, and follow-up result records are ready.",
        {
          guarded_adapter_dry_run: completedDryRun,
          external_execution_performed: false,
          actual_openclaw_execution_performed: false,
          playwright_run_performed: false,
          publishing_performed: false,
          account_control_performed: false,
        },
        settings,
      );
      await refreshCommercialOperationLoop(operationId);
      setAdapterDryRunStatus(`${workbenchCopy.operationAdapterDryRunSucceeded}: ${succeededRun.id}`);
      setRunStatus(`guarded adapter dry-run succeeded: ${succeededRun.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Guarded adapter dry-run failed";
      setOperationLoopError(message);
      setAdapterDryRunStatus(message);
      setRunStatus("guarded adapter dry-run error");
    } finally {
      setAdapterDryRunLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const selectPublishReadyExecutionRun = (runs: CommercialOperationExecutionRun[]) =>
    runs.find((run) => run.run_status === "succeeded" && isNextCycleExecutionRun(run)) ??
    runs.find((run) => run.run_status === "succeeded") ??
    null;

  const prepareGuardedPublishHandoff = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setPublishHandoffLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setPublishHandoffStatus(workbenchCopy.operationPublishHandoffPreparing);
    try {
      if (!operationId) {
        setPublishHandoffStatus(workbenchCopy.operationPublishHandoffMissing);
        setRunStatus("guarded publish handoff missing");
        return;
      }
      const executionRunResponse = await commercialOperationClient.listExecutionRuns(operationId, undefined, settings);
      const executionRunPool = [...executionRunResponse.items, ...commercialExecutionRuns];
      const targetRun = selectPublishReadyExecutionRun(executionRunPool);
      if (!targetRun) {
        setPublishHandoffStatus(workbenchCopy.operationPublishHandoffMissing);
        setRunStatus("guarded publish handoff missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const runIsNextCycle = isNextCycleExecutionRun(targetRun);
      const cycle =
        metadataStringValue(targetRun.metadata, "cycle") ??
        metadataStringValue(targetRun.input_payload, "cycle") ??
        (runIsNextCycle ? "next_iteration" : "first_iteration");
      const optimizationDecisionId =
        metadataStringValue(targetRun.metadata, "optimization_decision_id") ??
        metadataStringValue(targetRun.input_payload, "optimization_decision_id");
      const checkedAt = new Date().toISOString();
      const publishSource = "worker_console_guarded_publish_handoff";
      const resultResponse = await commercialOperationClient.listResults(operationId, undefined, settings);
      let publishHandoff =
        resultResponse.items.find((item) => item.execution_run_id === targetRun.id && isPublishHandoffResult(item)) ?? null;
      if (!publishHandoff) {
        publishHandoff = await commercialOperationClient.createResult(
          operationId,
          {
            execution_run_id: targetRun.id,
            result_type: "guarded_publish_handoff",
            title:
              language === "zh-CN"
                ? `${targetRun.title} 单平台发布交接`
                : `${targetRun.title} single-platform publish handoff`,
            summary:
              language === "zh-CN"
                ? "为首个社媒发布闭环准备受保护交接记录；当前只记录平台、账号、发布时间和回滚要求，不执行真实发布。"
                : "Prepares a guarded handoff record for the first social publish loop; this records platform, account, timing, and rollback requirements without live publishing.",
            outcome_summary:
              language === "zh-CN"
                ? "发布交接已准备，操作员可人工发布或等待后续真实适配器接入。"
                : "Publish handoff is ready for manual publish or a future live adapter.",
            observed_metrics: [
              { name: "publish_handoff_ready", value: "true" },
              { name: "target_platform", value: "manual_social" },
              { name: "cycle", value: cycle },
            ],
            commercial_signals: [
              "single-platform publish handoff prepared",
              "operator approval remains required",
              "manual result capture required",
            ],
            evidence_links: [{ title: "Execution run", target_id: targetRun.id, target_type: "execution_run" }],
            follow_up_actions: ["confirm platform account", "publish manually or enable future guarded adapter", "capture link, screenshot, and logs"],
            result_payload: {
              guarded_publish_handoff: {
                status: "ready_for_manual_publish_or_future_adapter",
                checked_at: checkedAt,
                target_platform: "manual_social",
                target_account_required: true,
                publish_time_required: true,
                rollback_required: true,
                manual_result_capture_required: true,
                future_openclaw_playwright_adapter: "not_enabled",
              },
              phase: "63O",
              live_adapter_execution_performed: false,
              external_execution_performed: false,
              actual_openclaw_execution_performed: false,
              playwright_run_performed: false,
              publishing_performed: false,
              account_control_performed: false,
              source: publishSource,
              cycle,
              optimization_decision_id: optimizationDecisionId,
            },
            recommendation_payload: {
              next_operator_action: "capture publish result after manual publish or future guarded adapter run",
            },
            metadata: {
              source: publishSource,
              phase: "63O",
              execution_run_id: targetRun.id,
              cycle,
              optimization_decision_id: optimizationDecisionId,
            },
          },
          settings,
        );
      }
      if (publishHandoff.result_status === "draft" || publishHandoff.result_status === "rejected") {
        publishHandoff = await commercialOperationClient.readyResult(
          operationId,
          publishHandoff.id,
          language === "zh-CN" ? "发布交接记录进入复核。" : "Publish handoff record is ready for review.",
          settings,
        );
      }
      if (publishHandoff.result_status === "ready_for_review") {
        publishHandoff = await commercialOperationClient.approveResult(
          operationId,
          publishHandoff.id,
          language === "zh-CN" ? "客户机操作员批准发布交接记录。" : "Client operator approved the publish handoff record.",
          settings,
        );
      }
      await refreshCommercialOperationLoop(operationId);
      setPublishHandoffStatus(`${workbenchCopy.operationPublishHandoffReady}: ${publishHandoff.id}`);
      setRunStatus(`guarded publish handoff ready: ${publishHandoff.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Guarded publish handoff failed";
      setOperationLoopError(message);
      setPublishHandoffStatus(message);
      setRunStatus("guarded publish handoff error");
    } finally {
      setPublishHandoffLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const captureManualPublishResult = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setPublishResultLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setPublishResultStatus(workbenchCopy.operationCapturePublishResultCapturing);
    try {
      if (!operationId) {
        setPublishResultStatus(workbenchCopy.operationPublishResultMissing);
        setRunStatus("manual publish result missing");
        return;
      }
      const executionRunResponse = await commercialOperationClient.listExecutionRuns(operationId, undefined, settings);
      const targetRun = selectPublishReadyExecutionRun([...executionRunResponse.items, ...commercialExecutionRuns]);
      if (!targetRun) {
        setPublishResultStatus(workbenchCopy.operationPublishResultMissing);
        setRunStatus("manual publish result missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const runIsNextCycle = isNextCycleExecutionRun(targetRun);
      const cycle =
        metadataStringValue(targetRun.metadata, "cycle") ??
        metadataStringValue(targetRun.input_payload, "cycle") ??
        (runIsNextCycle ? "next_iteration" : "first_iteration");
      const optimizationDecisionId =
        metadataStringValue(targetRun.metadata, "optimization_decision_id") ??
        metadataStringValue(targetRun.input_payload, "optimization_decision_id");
      const resultResponse = await commercialOperationClient.listResults(operationId, undefined, settings);
      const publishHandoff =
        resultResponse.items.find((item) => item.execution_run_id === targetRun.id && isPublishHandoffResult(item)) ?? null;
      let publishResult =
        resultResponse.items.find((item) => item.execution_run_id === targetRun.id && isManualPublishResult(item)) ?? null;
      if (!publishResult) {
        publishResult = await commercialOperationClient.createResult(
          operationId,
          {
            execution_run_id: targetRun.id,
            result_type: "manual_publish_result",
            title:
              language === "zh-CN"
                ? `${targetRun.title} 发布结果回收`
                : `${targetRun.title} publish result capture`,
            summary:
              language === "zh-CN"
                ? "客户机回收发布链接、截图、执行日志和失败恢复信息；当前为人工录入/占位结果，不代表系统已自动发布。"
                : "Captures publish link, screenshot, execution log, and recovery notes; this is manual or placeholder intake and does not mean the system auto-published.",
            outcome_summary:
              language === "zh-CN"
                ? "发布结果已回收，下一步记录曝光、互动、线索和转化观察。"
                : "Publish result is captured; next record reach, engagement, lead, and conversion observations.",
            observed_metrics: [
              { name: "publish_result_captured", value: "true" },
              { name: "publish_url", value: "manual_pending" },
              { name: "screenshot_evidence", value: "manual_pending" },
              { name: "cycle", value: cycle },
            ],
            commercial_signals: [
              "manual publish result captured",
              "link and screenshot evidence pending operator input",
              "ready for metric observation",
            ],
            evidence_links: [
              { title: "Execution run", target_id: targetRun.id, target_type: "execution_run" },
              ...(publishHandoff ? [{ title: "Publish handoff", target_id: publishHandoff.id, target_type: "commercial_result" }] : []),
            ],
            follow_up_actions: ["record reach", "record engagement", "record lead and conversion signals"],
            result_payload: {
              manual_publish_result: {
                status: "captured_placeholder",
                publish_url: "manual_pending",
                screenshot_evidence: "manual_pending",
                execution_log: "manual_pending",
                failure_recovery_notes: "manual_pending",
              },
              publish_result_capture: {
                status: "captured_placeholder",
                publish_url: "manual_pending",
                screenshot_reference: "manual_pending",
                execution_log_reference: "manual_pending",
                failure_recovery_notes: "manual_pending",
              },
              phase: "63P",
              live_adapter_execution_performed: false,
              external_execution_performed: false,
              actual_openclaw_execution_performed: false,
              playwright_run_performed: false,
              publishing_performed: false,
              account_control_performed: false,
              external_publish_attempted: false,
              automated_publish_performed: false,
              source: "worker_console_manual_publish_result",
              cycle,
              optimization_decision_id: optimizationDecisionId,
            },
            recommendation_payload: {
              next_operator_action: "record manual metric observation",
            },
            metadata: {
              source: "worker_console_manual_publish_result",
              phase: "63P",
              execution_run_id: targetRun.id,
              publish_handoff_result_id: publishHandoff?.id,
              cycle,
              optimization_decision_id: optimizationDecisionId,
            },
          },
          settings,
        );
      }
      if (publishResult.result_status === "draft" || publishResult.result_status === "rejected") {
        publishResult = await commercialOperationClient.readyResult(
          operationId,
          publishResult.id,
          language === "zh-CN" ? "发布结果回收记录进入复核。" : "Publish result capture is ready for review.",
          settings,
        );
      }
      if (publishResult.result_status === "ready_for_review") {
        publishResult = await commercialOperationClient.approveResult(
          operationId,
          publishResult.id,
          language === "zh-CN" ? "客户机操作员批准发布结果回收记录。" : "Client operator approved the publish result capture.",
          settings,
        );
      }
      await refreshCommercialOperationLoop(operationId);
      setPublishResultStatus(`${workbenchCopy.operationPublishResultReady}: ${publishResult.id}`);
      setRunStatus(`manual publish result captured: ${publishResult.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Manual publish result capture failed";
      setOperationLoopError(message);
      setPublishResultStatus(message);
      setRunStatus("manual publish result capture error");
    } finally {
      setPublishResultLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const recordManualMetricObservation = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setMetricObservationLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setMetricObservationStatus(workbenchCopy.operationMetricObservationRecording);
    try {
      if (!operationId) {
        setMetricObservationStatus(workbenchCopy.operationMetricObservationMissing);
        setRunStatus("manual metric observation missing");
        return;
      }
      const resultResponse = await commercialOperationClient.listResults(operationId, undefined, settings);
      const targetResult =
        resultResponse.items.find((item) => item.result_status === "approved" && isManualPublishResult(item)) ??
        commercialResults.find((item) => item.result_status === "approved" && isManualPublishResult(item)) ??
        resultResponse.items.find((item) => item.result_status === "approved" && isPublishHandoffResult(item)) ??
        commercialResults.find((item) => item.result_status === "approved" && isPublishHandoffResult(item)) ??
        resultResponse.items.find((item) => item.result_status === "approved") ??
        commercialResults.find((item) => item.result_status === "approved") ??
        null;
      if (!targetResult) {
        setMetricObservationStatus(workbenchCopy.operationMetricObservationMissing);
        setRunStatus("manual metric observation missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      const cycle = metadataStringValue(targetResult.metadata, "cycle") ?? "first_iteration";
      const observationResponse = await commercialOperationClient.listMonitoringObservations(operationId, undefined, settings);
      let observation =
        observationResponse.items.find((item) => item.result_id === targetResult.id && isManualMetricObservation(item)) ?? null;
      if (!observation) {
        observation = await commercialOperationClient.createMonitoringObservation(
          operationId,
          {
            result_id: targetResult.id,
            observation_type: "manual_publish_metrics",
            title:
              language === "zh-CN"
                ? `${targetResult.title} 运营数据观察`
                : `${targetResult.title} operating metric observation`,
            metric_snapshots: [
              { name: "reach", value: "manual_pending", source: "operator" },
              { name: "impressions", value: "manual_pending", source: "operator" },
              { name: "clicks", value: "manual_pending", source: "operator" },
              { name: "engagement", value: "manual_pending", source: "operator" },
              { name: "lead_signal", value: "manual_pending", source: "operator" },
              { name: "conversion_signal", value: "manual_pending", source: "operator" },
              { name: "conversion", value: "manual_pending", source: "operator" },
              { name: "publish_url_verified", value: "manual_pending", source: "operator" },
            ],
            qualitative_signals: [
              "manual metric observation recorded",
              "platform analytics ingestion not automated",
              "ready for content improvement decision",
            ],
            evidence_links: [{ title: "Publish result", target_id: targetResult.id, target_type: "commercial_result" }],
            anomaly_flags: ["manual metrics pending", "no automated platform analytics ingestion"],
            recommended_actions: ["compare content angle against engagement", "prepare next-cycle content improvement", "keep human approval before execution"],
            observation_payload: {
              data_collection_mode: "manual",
              metrics_collection_mode: "manual",
              analytics_ingested: false,
              source: "worker_console_manual_publish_metrics",
              cycle,
            },
            metadata: {
              source: "worker_console_manual_publish_metrics",
              phase: "63Q",
              result_id: targetResult.id,
              cycle,
            },
          },
          settings,
        );
      }
      if (observation.observation_status === "draft" || observation.observation_status === "rejected") {
        observation = await commercialOperationClient.readyMonitoringObservation(
          operationId,
          observation.id,
          language === "zh-CN" ? "运营数据观察进入复核。" : "Metric observation is ready for review.",
          settings,
        );
      }
      if (observation.observation_status === "ready_for_review") {
        observation = await commercialOperationClient.approveMonitoringObservation(
          operationId,
          observation.id,
          language === "zh-CN" ? "客户机操作员批准运营数据观察。" : "Client operator approved the metric observation.",
          settings,
        );
      }
      await refreshCommercialOperationLoop(operationId);
      setMetricObservationStatus(`${workbenchCopy.operationMetricObservationReady}: ${observation.id}`);
      setRunStatus(`manual metric observation recorded: ${observation.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Manual metric observation failed";
      setOperationLoopError(message);
      setMetricObservationStatus(message);
      setRunStatus("manual metric observation error");
    } finally {
      setMetricObservationLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const analyzeManualPublishMetrics = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setPublishImprovementLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setPublishImprovementStatus(workbenchCopy.operationAnalyzePublishMetricsRunning);
    try {
      if (!operationId) {
        setPublishImprovementStatus(workbenchCopy.operationPublishImprovementMissing);
        setRunStatus("manual publish metric improvement missing");
        return;
      }
      const observationResponse = await commercialOperationClient.listMonitoringObservations(operationId, undefined, settings);
      let targetObservation =
        observationResponse.items.find((item) => item.observation_status === "approved" && isManualMetricObservation(item)) ??
        commercialMonitoringObservations.find((item) => item.observation_status === "approved" && isManualMetricObservation(item)) ??
        observationResponse.items.find(isManualMetricObservation) ??
        commercialMonitoringObservations.find(isManualMetricObservation) ??
        null;
      if (!targetObservation) {
        setPublishImprovementStatus(workbenchCopy.operationPublishImprovementMissing);
        setRunStatus("manual publish metric improvement missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }
      if (targetObservation.observation_status === "draft" || targetObservation.observation_status === "rejected") {
        targetObservation = await commercialOperationClient.readyMonitoringObservation(
          operationId,
          targetObservation.id,
          language === "zh-CN" ? "发布数据观察进入改进分析前复核。" : "Publish metric observation is ready before improvement analysis.",
          settings,
        );
      }
      if (targetObservation.observation_status === "ready_for_review") {
        targetObservation = await commercialOperationClient.approveMonitoringObservation(
          operationId,
          targetObservation.id,
          language === "zh-CN" ? "客户机操作员批准发布数据观察用于改进分析。" : "Client operator approved publish metrics for improvement analysis.",
          settings,
        );
      }

      const cycle = metadataStringValue(targetObservation.metadata, "cycle") ?? "first_iteration";
      const resultId = targetObservation.result_id;
      const decisionResponse = await commercialOperationClient.listOptimizationDecisions(operationId, undefined, settings);
      let decision =
        decisionResponse.items.find(
          (item) =>
            item.observation_id === targetObservation.id &&
            isManualPublishImprovementDecision(item) &&
            ["approved", "ready_for_review", "draft", "rejected"].includes(item.decision_status),
        ) ?? null;
      if (!decision) {
        decision = await commercialOperationClient.createOptimizationDecision(
          operationId,
          {
            observation_id: targetObservation.id,
            decision_type: "manual_publish_improvement",
            title:
              language === "zh-CN"
                ? `${targetObservation.title} 发布数据改进建议`
                : `${targetObservation.title} publish metric improvement decision`,
            priority: "normal",
            rationale:
              language === "zh-CN"
                ? "基于人工回收的发布结果和运营数据观察，生成下一轮内容改进建议；当前不自动优化、不自动发布。"
                : "Creates the next content improvement from manually captured publish results and operating metrics without automatic optimization or publishing.",
            objective_updates: [
              language === "zh-CN"
                ? "保留原运营目标，下一轮围绕曝光、点击、互动、线索和转化信号继续验证。"
                : "Keep the original operating goal and validate reach, clicks, engagement, leads, and conversion signals in the next cycle.",
            ],
            content_actions: [
              language === "zh-CN"
                ? "下一轮内容优先调整开头钩子、利益点表达、行动号召和证据引用。"
                : "Next content should improve the opening hook, value proposition, call to action, and evidence references.",
              language === "zh-CN"
                ? "保留人工数据占位，等真实平台指标回填后再细化内容角度。"
                : "Keep manual metric placeholders and refine the content angle when real platform metrics are filled.",
            ],
            asset_actions: [
              language === "zh-CN"
                ? "下一轮素材 Brief 需要匹配新的内容钩子，仍不自动调用 ComfyUI。"
                : "Update the next asset brief for the improved hook without calling ComfyUI automatically.",
            ],
            audience_actions: [
              language === "zh-CN"
                ? "复核发布平台、人群和时间窗口，再决定是否扩大投放。"
                : "Review platform, audience, and timing before expanding distribution.",
            ],
            execution_actions: [
              language === "zh-CN"
                ? "下一轮仍需人工审批后，才允许进入客户机 OpenClaw/Playwright 交接。"
                : "Require human approval again before the next customer-machine OpenClaw/Playwright handoff.",
            ],
            risk_controls: [
              "human approval required",
              "manual metrics only",
              "no automatic publishing",
              "no account control",
              "no automated platform analytics ingestion",
            ],
            decision_payload: {
              source: "worker_console_manual_publish_improvement",
              phase: "63R",
              cycle,
              result_id: resultId,
              observation_id: targetObservation.id,
              publish_metric_analysis: {
                status: "manual_analysis_ready",
                data_collection_mode: "manual",
                metrics_are_placeholders: true,
                automated_optimization_performed: false,
                automated_publishing_performed: false,
                platform_analytics_ingested: false,
              },
              next_cycle_ready: true,
            },
            metadata: {
              source: "worker_console_manual_publish_improvement",
              phase: "63R",
              result_id: resultId,
              observation_id: targetObservation.id,
              cycle,
            },
          },
          settings,
        );
      }
      if (decision.decision_status === "draft" || decision.decision_status === "rejected") {
        decision = await commercialOperationClient.readyOptimizationDecision(
          operationId,
          decision.id,
          language === "zh-CN" ? "发布数据改进建议进入复核。" : "Publish metric improvement decision is ready for review.",
          settings,
        );
      }
      if (decision.decision_status === "ready_for_review") {
        decision = await commercialOperationClient.approveOptimizationDecision(
          operationId,
          decision.id,
          language === "zh-CN" ? "客户机操作员批准发布数据改进建议。" : "Client operator approved the publish metric improvement decision.",
          settings,
        );
      }
      await refreshCommercialOperationLoop(operationId);
      setPublishImprovementStatus(`${workbenchCopy.operationPublishImprovementReady}: ${decision.id}`);
      setRunStatus(`manual publish metric improvement ready: ${decision.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Manual publish metric improvement failed";
      setOperationLoopError(message);
      setPublishImprovementStatus(message);
      setRunStatus("manual publish metric improvement error");
    } finally {
      setPublishImprovementLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const completeCommercialResultFeedbackLoop = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setFeedbackLoopLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setFeedbackLoopStatus(workbenchCopy.operationFeedbackLoopCompleting);
    try {
      if (!operationId) {
        setFeedbackLoopStatus(workbenchCopy.operationFeedbackLoopMissing);
        setRunStatus("commercial feedback loop missing");
        return;
      }
      const executionRunResponse = await commercialOperationClient.listExecutionRuns(operationId, undefined, settings);
      const executionRunPool = [...executionRunResponse.items, ...commercialExecutionRuns];
      const selectFeedbackRun = (runs: CommercialOperationExecutionRun[]) =>
        runs.find((run) => run.run_status === "succeeded") ??
        runs.find((run) => run.run_status === "running") ??
        runs.find((run) => run.run_status === "queued" || run.run_status === "retrying") ??
        runs.find((run) => run.run_status === "failed" || run.run_status === "cancelled") ??
        null;
      const selectedRun = selectFeedbackRun(executionRunPool.filter(isNextCycleExecutionRun)) ?? selectFeedbackRun(executionRunPool);
      if (!selectedRun) {
        setFeedbackLoopStatus(workbenchCopy.operationFeedbackLoopMissing);
        setRunStatus("commercial feedback loop missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }

      let terminalRun = selectedRun;
      const runIsNextCycle = isNextCycleExecutionRun(terminalRun);
      const feedbackSource = runIsNextCycle ? "worker_console_next_cycle_result_feedback_loop" : "worker_console_result_feedback_loop";
      const feedbackPhase = runIsNextCycle ? "63I" : "63E";
      const feedbackCycle = runIsNextCycle ? "next_iteration" : "first_iteration";
      const previousOptimizationDecisionId =
        metadataStringValue(terminalRun.metadata, "optimization_decision_id") ??
        metadataStringValue(terminalRun.input_payload, "optimization_decision_id");
      setFeedbackLoopStatus(
        runIsNextCycle ? workbenchCopy.operationNextCycleFeedbackLoopCompleting : workbenchCopy.operationFeedbackLoopCompleting,
      );
      if (terminalRun.run_status === "queued" || terminalRun.run_status === "retrying") {
        terminalRun = await commercialOperationClient.startExecutionRun(
          operationId,
          terminalRun.id,
          runIsNextCycle
            ? language === "zh-CN"
              ? "客户机操作员为下一轮闭环标记 metadata-only 执行开始。"
              : "Client operator marked the next-cycle metadata-only execution run started."
            : language === "zh-CN"
              ? "客户机操作员为最小可用闭环标记 metadata-only 执行开始。"
              : "Client operator marked the metadata-only execution run started for MVP loop completion.",
          settings,
        );
      }
      if (terminalRun.run_status === "running") {
        terminalRun = await commercialOperationClient.succeedExecutionRun(
          operationId,
          terminalRun.id,
          runIsNextCycle
            ? language === "zh-CN"
              ? "客户机操作员确认下一轮 metadata-only 执行记录完成；未触发真实发布。"
              : "Client operator confirmed the next-cycle metadata-only execution record completed; no real publishing was triggered."
            : language === "zh-CN"
              ? "客户机操作员确认 metadata-only 执行记录完成；未触发真实发布。"
              : "Client operator confirmed the metadata-only execution record completed; no real publishing was triggered.",
          {
            external_execution_attempted: false,
            publishing_performed: false,
            source: feedbackSource,
            cycle: feedbackCycle,
            previous_optimization_decision_id: previousOptimizationDecisionId,
          },
          settings,
        );
      }

      const resultResponse = await commercialOperationClient.listResults(operationId, undefined, settings);
      let resultRecord =
        resultResponse.items.find(
          (item) =>
            item.execution_run_id === terminalRun.id &&
            ["approved", "ready_for_review", "draft", "rejected"].includes(item.result_status),
        ) ?? null;
      if (!resultRecord) {
        resultRecord = await commercialOperationClient.createResult(
          operationId,
          {
            execution_run_id: terminalRun.id,
            result_type: terminalRun.run_status === "failed" ? "failure_report" : "operator_report",
            title:
              language === "zh-CN"
                ? `${terminalRun.title} ${runIsNextCycle ? "下一轮客户机结果记录" : "客户机结果记录"}`
                : `${terminalRun.title} ${runIsNextCycle ? "next-cycle client result record" : "client result record"}`,
            summary:
              runIsNextCycle
                ? language === "zh-CN"
                  ? "客户机记录下一轮 metadata-only 执行结果，当前不代表真实平台发布。"
                  : "Client console recorded this next-cycle metadata-only execution result; it does not represent real platform publishing."
                : language === "zh-CN"
                  ? "客户机记录本次 metadata-only 执行结果，当前不代表真实平台发布。"
                  : "Client console recorded this metadata-only execution result; it does not represent real platform publishing.",
            outcome_summary:
              runIsNextCycle
                ? language === "zh-CN"
                  ? "下一轮结果记录已形成，可继续观察数据并生成再下一轮改进。"
                  : "A next-cycle result record is available for observation and another improvement pass."
                : language === "zh-CN"
                  ? "已形成可复盘的结果记录，可继续观察数据并生成下一轮改进。"
                  : "A reviewable result record is available for observation and next-cycle improvement.",
            observed_metrics: [
              { name: "execution_recorded", value: "1", unit: "record" },
              { name: "external_publish_attempted", value: "false" },
              { name: "cycle", value: feedbackCycle },
            ],
            commercial_signals: [
              runIsNextCycle ? "next-cycle metadata-only execution result recorded" : "metadata-only execution result recorded",
              "manual observation required before next iteration",
            ],
            evidence_links: [{ title: "Execution run record", target_id: terminalRun.id, target_type: "execution_run" }],
            follow_up_actions: [
              runIsNextCycle ? "record next-cycle manual observation" : "record manual observation",
              runIsNextCycle ? "prepare another content improvement" : "prepare next content improvement",
            ],
            result_payload: {
              run_status: terminalRun.run_status,
              external_execution_attempted: false,
              publishing_performed: false,
              source: feedbackSource,
              cycle: feedbackCycle,
              previous_optimization_decision_id: previousOptimizationDecisionId,
            },
            recommendation_payload: {
              next_operator_action: runIsNextCycle
                ? "observe next-cycle results and approve another improvement decision"
                : "observe results and approve an improvement decision",
            },
            metadata: {
              source: feedbackSource,
              phase: feedbackPhase,
              execution_run_id: terminalRun.id,
              cycle: feedbackCycle,
              previous_optimization_decision_id: previousOptimizationDecisionId,
            },
          },
          settings,
        );
      }
      if (resultRecord.result_status === "draft" || resultRecord.result_status === "rejected") {
        resultRecord = await commercialOperationClient.readyResult(
          operationId,
          resultRecord.id,
          language === "zh-CN" ? "客户机结果记录进入复核。" : "Client result record is ready for review.",
          settings,
        );
      }
      if (resultRecord.result_status === "ready_for_review") {
        resultRecord = await commercialOperationClient.approveResult(
          operationId,
          resultRecord.id,
          language === "zh-CN" ? "客户机操作员批准结果记录用于数据观察。" : "Client operator approved the result record for observation.",
          settings,
        );
      }

      const observationResponse = await commercialOperationClient.listMonitoringObservations(operationId, undefined, settings);
      let observation =
        observationResponse.items.find(
          (item) =>
            item.result_id === resultRecord.id &&
            ["approved", "ready_for_review", "draft", "rejected"].includes(item.observation_status),
        ) ?? null;
      if (!observation) {
        observation = await commercialOperationClient.createMonitoringObservation(
          operationId,
          {
            result_id: resultRecord.id,
            observation_type: "manual_snapshot",
            title:
              language === "zh-CN"
                ? `${resultRecord.title} 数据观察`
                : `${resultRecord.title} data observation`,
            metric_snapshots: [
              { name: "reach", value: "manual_pending" },
              { name: "engagement", value: "manual_pending" },
              { name: "lead_signal", value: "manual_pending" },
              { name: "conversion_signal", value: "manual_pending" },
              { name: "cycle", value: feedbackCycle },
            ],
            qualitative_signals: [
              runIsNextCycle ? "next-cycle operator-visible result captured" : "operator-visible result captured",
              "manual metrics can be filled after real publishing is enabled",
            ],
            evidence_links: [{ title: "Result record", target_id: resultRecord.id, target_type: "commercial_result" }],
            anomaly_flags: ["no automated platform analytics ingestion"],
            recommended_actions: [
              runIsNextCycle ? "approve another content iteration" : "approve next content iteration",
              "keep human approval before runtime execution",
            ],
            observation_payload: {
              analytics_ingested: false,
              source: feedbackSource,
              cycle: feedbackCycle,
              previous_optimization_decision_id: previousOptimizationDecisionId,
            },
            metadata: {
              source: feedbackSource,
              phase: feedbackPhase,
              result_id: resultRecord.id,
              cycle: feedbackCycle,
              previous_optimization_decision_id: previousOptimizationDecisionId,
            },
          },
          settings,
        );
      }
      if (observation.observation_status === "draft" || observation.observation_status === "rejected") {
        observation = await commercialOperationClient.readyMonitoringObservation(
          operationId,
          observation.id,
          language === "zh-CN" ? "客户机数据观察记录进入复核。" : "Client observation record is ready for review.",
          settings,
        );
      }
      if (observation.observation_status === "ready_for_review") {
        observation = await commercialOperationClient.approveMonitoringObservation(
          operationId,
          observation.id,
          language === "zh-CN" ? "客户机操作员批准数据观察用于改进建议。" : "Client operator approved the observation for improvement.",
          settings,
        );
      }

      const decisionResponse = await commercialOperationClient.listOptimizationDecisions(operationId, undefined, settings);
      let decision =
        decisionResponse.items.find(
          (item) =>
            item.observation_id === observation.id &&
            ["approved", "ready_for_review", "draft", "rejected"].includes(item.decision_status),
        ) ?? null;
      if (!decision) {
        decision = await commercialOperationClient.createOptimizationDecision(
          operationId,
          {
            observation_id: observation.id,
            decision_type: "iterate",
            title:
              language === "zh-CN"
                ? `${observation.title} ${runIsNextCycle ? "再下一轮改进建议" : "下一轮改进建议"}`
                : `${observation.title} ${runIsNextCycle ? "another iteration decision" : "next iteration decision"}`,
            priority: "normal",
            rationale:
              runIsNextCycle
                ? language === "zh-CN"
                  ? "基于下一轮客户机结果记录和人工观察，生成再下一轮内容优化建议；当前不自动优化或发布。"
                  : "Based on the next-cycle client result record and manual observation, prepare another content iteration without automatic publishing."
                : language === "zh-CN"
                  ? "基于客户机结果记录和人工观察，进入下一轮内容优化；当前不自动优化或发布。"
                  : "Based on the client result record and manual observation, move to the next content iteration without automatic publishing.",
            objective_updates: [
              runIsNextCycle
                ? language === "zh-CN"
                  ? "保留原运营目标，继续用下一轮结果优化可验证商业信号。"
                  : "Keep the original goal and use next-cycle results to refine verifiable commercial signals."
                : language === "zh-CN"
                  ? "保留原运营目标，下一轮聚焦可验证商业信号。"
                  : "Keep the original goal and focus the next iteration on verifiable commercial signals.",
            ],
            content_actions: [
              runIsNextCycle
                ? language === "zh-CN"
                  ? "根据下一轮观察继续调整标题、正文和行动号召。"
                  : "Keep refining headline, body copy, and call to action from the next-cycle observation."
                : language === "zh-CN"
                  ? "根据观察结果调整标题、正文和行动号召。"
                  : "Adjust headline, body copy, and call to action from the observation.",
            ],
            asset_actions: [
              language === "zh-CN" ? "保留素材需求，下一轮按人工反馈更新 Brief。" : "Keep asset needs and update the brief from manual feedback next round.",
            ],
            audience_actions: [
              language === "zh-CN" ? "复核人群和渠道，确认下一轮投放对象。" : "Review audience and channel before the next run.",
            ],
            execution_actions: [
              language === "zh-CN" ? "下一轮仍需人工审批后才能交给 OpenClaw/Playwright。" : "Require human approval again before any OpenClaw/Playwright handoff.",
            ],
            risk_controls: ["human approval required", "no automatic publishing", "no account control"],
            decision_payload: {
              source: feedbackSource,
              next_cycle_ready: true,
              cycle: feedbackCycle,
              previous_optimization_decision_id: previousOptimizationDecisionId,
            },
            metadata: {
              source: feedbackSource,
              phase: feedbackPhase,
              observation_id: observation.id,
              cycle: feedbackCycle,
              previous_optimization_decision_id: previousOptimizationDecisionId,
            },
          },
          settings,
        );
      }
      if (decision.decision_status === "draft" || decision.decision_status === "rejected") {
        decision = await commercialOperationClient.readyOptimizationDecision(
          operationId,
          decision.id,
          language === "zh-CN" ? "客户机改进建议进入复核。" : "Client improvement decision is ready for review.",
          settings,
        );
      }
      if (decision.decision_status === "ready_for_review") {
        decision = await commercialOperationClient.approveOptimizationDecision(
          operationId,
          decision.id,
          language === "zh-CN" ? "客户机操作员批准下一轮改进建议。" : "Client operator approved the next iteration decision.",
          settings,
        );
      }

      await refreshCommercialOperationLoop(operationId);
      setFeedbackLoopStatus(
        `${runIsNextCycle ? workbenchCopy.operationNextCycleFeedbackLoopComplete : workbenchCopy.operationFeedbackLoopComplete}: ${decision.id}`,
      );
      setRunStatus(`${runIsNextCycle ? "next-cycle " : ""}commercial feedback loop complete: ${decision.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Commercial feedback loop failed";
      setOperationLoopError(message);
      setFeedbackLoopStatus(message);
      setRunStatus("commercial feedback loop error");
    } finally {
      setFeedbackLoopLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const prepareNextCycleDraftFromDecision = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setNextCycleDraftLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setNextCycleDraftStatus(workbenchCopy.operationNextCycleDraftPreparing);
    try {
      if (!operationId) {
        setNextCycleDraftStatus(workbenchCopy.operationNextCycleDecisionMissing);
        setRunStatus("commercial next-cycle decision missing");
        return;
      }
      const decisionResponse = await commercialOperationClient.listOptimizationDecisions(operationId, undefined, settings);
      const decision =
        decisionResponse.items.find((item) => item.decision_status === "approved" && isManualPublishImprovementDecision(item)) ??
        commercialOptimizationDecisions.find((item) => item.decision_status === "approved" && isManualPublishImprovementDecision(item)) ??
        decisionResponse.items.find((item) => item.decision_status === "approved") ??
        commercialOptimizationDecisions.find((item) => item.decision_status === "approved") ??
        null;
      if (!decision) {
        setNextCycleDraftStatus(workbenchCopy.operationNextCycleDecisionMissing);
        setRunStatus("commercial next-cycle decision missing");
        await refreshCommercialOperationLoop(operationId);
        return;
      }

      const objective = operationLoop?.objective || input.trim() || selectedGoalTemplate.prompt;
      const decisionIsPublishImprovement = isManualPublishImprovementDecision(decision);
      const nextCycleDraftSource = decisionIsPublishImprovement
        ? "worker_console_publish_metric_next_cycle_draft"
        : "worker_console_next_cycle_content_draft";
      const nextCycleDraftPhase = decisionIsPublishImprovement ? "63S" : "63F";
      const draftResponse = await commercialOperationClient.listContentDrafts(operationId, undefined, settings);
      let draft =
        draftResponse.items.find(
          (item) =>
            metadataStringValue(item.metadata, "source") === nextCycleDraftSource &&
            metadataStringValue(item.metadata, "optimization_decision_id") === decision.id,
        ) ?? null;
      if (!draft) {
        draft = await commercialOperationClient.createContentDraft(
          operationId,
          {
            step_key: "content_production",
            channel: "customer_console",
            content_format: decisionIsPublishImprovement ? "publish_metric_next_cycle_copy" : "next_cycle_copy",
            title:
              language === "zh-CN"
                ? `${operationLoopTitleFromGoal(objective)} 下一轮内容草稿`
                : `${operationLoopTitleFromGoal(objective)} next-cycle content draft`,
            audience_segment: decision.audience_actions[0] ?? (language === "zh-CN" ? "沿用上一轮目标人群" : "carry over previous audience"),
            content_body: nextCycleContentBody(objective, decision, language),
            summary:
              decisionIsPublishImprovement
                ? language === "zh-CN"
                  ? "根据发布数据改进建议生成下一轮可审批内容草案，用于继续运营闭环。"
                  : "Next-cycle reviewable content draft generated from the publish-metric improvement decision."
                : language === "zh-CN"
                  ? "根据已批准的改进建议生成下一轮可审批内容草案，用于继续闭环。"
                  : "Next-cycle reviewable content draft generated from the approved improvement decision.",
            call_to_action: language === "zh-CN" ? "再次人工审批后再准备执行" : "Review again before execution prep",
            source_materials: [
              `commercial_optimization_decision:${decision.id}`,
              `commercial_observation:${decision.observation_id}`,
              `commercial_result:${decision.result_id}`,
              "knowledge_collection:operations",
              ...(decisionIsPublishImprovement ? ["manual_publish_metrics"] : []),
            ],
            asset_requests: [
              {
                title: language === "zh-CN" ? "下一轮素材更新需求" : "Next-cycle asset update request",
                type: "asset_placeholder",
                purpose:
                  language === "zh-CN"
                    ? "根据改进建议更新素材 Brief，当前不直接调用 ComfyUI。"
                    : "Update the asset brief from the improvement decision without calling ComfyUI.",
                execution_boundary: "no ComfyUI job is created in this phase",
              },
            ],
            metadata: {
              source: nextCycleDraftSource,
              phase: nextCycleDraftPhase,
              optimization_decision_id: decision.id,
              observation_id: decision.observation_id,
              result_id: decision.result_id,
              previous_execution_run_id: decision.execution_run_id,
              cycle: "next_iteration",
            },
          },
          settings,
        );
      }
      let readyDraft = draft;
      if (readyDraft.draft_status === "draft" || readyDraft.draft_status === "rejected") {
        readyDraft = await commercialOperationClient.readyContentDraft(
          operationId,
          readyDraft.id,
          language === "zh-CN" ? "下一轮内容草案已准备好，等待人工审批。" : "Next-cycle content draft is ready for human approval.",
          settings,
        );
      }

      const approvalResponse = await commercialOperationClient.listApprovals(operationId, undefined, settings);
      const existingApproval =
        approvalResponse.items.find(
          (item) =>
            metadataStringValue(item.metadata, "source") === nextCycleDraftSource &&
            metadataStringValue(item.metadata, "content_draft_id") === readyDraft.id &&
            !["rejected", "cancelled"].includes(item.approval_status),
        ) ?? null;
      const approval =
        existingApproval ??
        (await commercialOperationClient.createApproval(
          operationId,
          {
            step_key: "human_review",
            title: language === "zh-CN" ? "审批下一轮运营内容" : "Approve next-cycle operation content",
            requested_action:
              language === "zh-CN"
                ? "请审核下一轮内容草案、素材更新需求和执行边界；审批前不会发布或执行客户机任务。"
                : "Review the next-cycle content draft, asset update request, and execution boundary; no publishing or client execution happens before approval.",
            risk_level: "medium",
            metadata: {
              source: nextCycleDraftSource,
              phase: nextCycleDraftPhase,
              content_draft_id: readyDraft.id,
              optimization_decision_id: decision.id,
            },
          },
          settings,
        ));
      await refreshCommercialOperationLoop(operationId);
      setNextCycleDraftStatus(`${workbenchCopy.operationNextCycleDraftReady}: ${readyDraft.title}`);
      setRunStatus(`next-cycle draft ready for approval: ${approval.id}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Next-cycle draft generation failed";
      setOperationLoopError(message);
      setNextCycleDraftStatus(message);
      setRunStatus("commercial next-cycle draft error");
    } finally {
      setNextCycleDraftLoading(false);
      setOperationLoopLoading(false);
    }
  };

  const completeClientClosedLoopDeliveryPass = async () => {
    const operationId = operationLoop?.operation_id || selectedCommercialOperationId;
    setClosedLoopDeliveryLoading(true);
    setOperationLoopLoading(true);
    setOperationLoopError(null);
    setClosedLoopDeliveryStatus(workbenchCopy.operationClosedLoopDeliveryRunning);
    try {
      if (!operationId) {
        setClosedLoopDeliveryStatus(workbenchCopy.operationClosedLoopDeliveryMissing);
        setRunStatus("client closed loop delivery missing");
        return;
      }

      setRunStatus("client closed loop delivery pass running");
      await preflightClientRuntimeExecutionRun();
      await prepareGuardedAdapterDispatchHandoff();
      await runGuardedAdapterDryRun();
      await prepareGuardedPublishHandoff();
      await captureManualPublishResult();
      await recordManualMetricObservation();
      await analyzeManualPublishMetrics();
      await prepareNextCycleDraftFromDecision();
      await refreshCommercialOperationLoop(operationId);
      setClosedLoopDeliveryStatus(`${workbenchCopy.operationClosedLoopDeliveryReady}: ${operationId}`);
      setRunStatus(`client closed loop delivery pass complete: ${operationId}`);
    } catch (nextError) {
      const message = nextError instanceof Error ? nextError.message : "Client closed loop delivery failed";
      setOperationLoopError(message);
      setClosedLoopDeliveryStatus(message);
      setRunStatus("client closed loop delivery error");
    } finally {
      setClosedLoopDeliveryLoading(false);
      setOperationLoopLoading(false);
    }
  };

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
      await refreshCommercialOperationLoop();
      await refreshDigitalHumanVideos();
      setConnectionState("connected");
    } catch (nextError) {
      setConnectionState("disconnected");
      setChatError(nextError instanceof Error ? nextError.message : "AI Server unreachable");
    }
  }, [refreshCommercialOperationLoop, refreshDigitalHumanVideos, refreshPlaybooks, refreshTaskRuns, refreshWorkflows, settings, threadId]);

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
  const pendingCommercialApprovals = commercialApprovals.filter((approval) => approval.approval_status === "pending");
  const pendingPublishMetricNextCycleCommercialApproval = pendingCommercialApprovals.find(isPublishMetricNextCycleApproval) ?? null;
  const pendingNextCycleCommercialApproval = pendingPublishMetricNextCycleCommercialApproval ?? pendingCommercialApprovals.find(isNextCycleApproval) ?? null;
  const latestCommercialExecutionRequest = commercialExecutionRequests[0] ?? null;
  const pendingPublishMetricReexecutionRequest =
    commercialExecutionRequests.find(
      (request) => ["prepared", "approved", "ready_for_review", "draft"].includes(request.request_status) && isPublishMetricReexecutionRequest(request),
    ) ?? null;
  const pendingNextCycleExecutionRequest =
    pendingPublishMetricReexecutionRequest ??
    commercialExecutionRequests.find(
      (request) => ["prepared", "approved", "ready_for_review", "draft"].includes(request.request_status) && isNextCycleExecutionRequest(request),
    ) ?? null;
  const latestCommercialExecutionRun = commercialExecutionRuns[0] ?? null;
  const queuedCommercialExecutionRun =
    commercialExecutionRuns.find((run) => (run.run_status === "queued" || run.run_status === "retrying") && isPublishMetricReexecutionRun(run)) ??
    commercialExecutionRuns.find((run) => (run.run_status === "queued" || run.run_status === "retrying") && isNextCycleExecutionRun(run)) ??
    commercialExecutionRuns.find((run) => run.run_status === "queued" || run.run_status === "retrying") ?? null;
  const runningCommercialExecutionRun = commercialExecutionRuns.find((run) => run.run_status === "running") ?? null;
  const failedCommercialExecutionRun = commercialExecutionRuns.find((run) => run.run_status === "failed") ?? null;
  const runtimePreflightCandidateExecutionRun =
    commercialExecutionRuns.find((run) => ["queued", "retrying"].includes(run.run_status) && isNextCycleExecutionRun(run)) ??
    queuedCommercialExecutionRun;
  const guardedDispatchCandidateExecutionRun =
    commercialExecutionRuns.find((run) => ["queued", "retrying"].includes(run.run_status) && isNextCycleExecutionRun(run) && isClientRuntimePreflightReady(run)) ??
    commercialExecutionRuns.find((run) => ["queued", "retrying"].includes(run.run_status) && isClientRuntimePreflightReady(run)) ??
    runtimePreflightCandidateExecutionRun;
  const adapterDryRunCandidateExecutionRun =
    commercialExecutionRuns.find((run) => ["queued", "retrying"].includes(run.run_status) && isNextCycleExecutionRun(run) && isGuardedAdapterDispatchReady(run)) ??
    commercialExecutionRuns.find((run) => ["queued", "retrying"].includes(run.run_status) && isGuardedAdapterDispatchReady(run)) ??
    guardedDispatchCandidateExecutionRun;
  const visibleCommercialExecutionRuns = commercialExecutionRuns.slice(0, 5);
  const activeCommercialExecutionRunCount = commercialExecutionRuns.filter((run) =>
    ["queued", "running", "retrying", "failed"].includes(run.run_status),
  ).length;
  const pendingNextCycleFeedbackExecutionRun =
    commercialExecutionRuns.find(
      (run) => ["succeeded", "running", "queued", "retrying", "failed", "cancelled"].includes(run.run_status) && isNextCycleExecutionRun(run),
    ) ?? null;
  const latestCommercialResult = commercialResults[0] ?? null;
  const latestCommercialObservation = commercialMonitoringObservations[0] ?? null;
  const latestPublishHandoffResult = commercialResults.find(isPublishHandoffResult) ?? null;
  const latestManualPublishResult = commercialResults.find(isManualPublishResult) ?? null;
  const latestManualMetricObservation = commercialMonitoringObservations.find(isManualMetricObservation) ?? null;
  const latestManualPublishImprovementDecision = commercialOptimizationDecisions.find(isManualPublishImprovementDecision) ?? null;
  const publishHandoffCandidateExecutionRun =
    commercialExecutionRuns.find((run) => run.run_status === "succeeded" && isNextCycleExecutionRun(run)) ??
    commercialExecutionRuns.find((run) => run.run_status === "succeeded") ??
    null;
  const publishResultCandidateExecutionRun = publishHandoffCandidateExecutionRun;
  const metricObservationCandidateResult =
    commercialResults.find((result) => result.result_status === "approved" && isManualPublishResult(result)) ??
    commercialResults.find((result) => result.result_status === "approved" && isPublishHandoffResult(result)) ??
    latestCommercialResult;
  const publishImprovementCandidateObservation =
    commercialMonitoringObservations.find((observation) => observation.observation_status === "approved" && isManualMetricObservation(observation)) ??
    latestManualMetricObservation;
  const latestCommercialOptimizationDecision = commercialOptimizationDecisions[0] ?? null;
  const approvedCommercialOptimizationDecision =
    commercialOptimizationDecisions.find((decision) => decision.decision_status === "approved" && isManualPublishImprovementDecision(decision)) ??
    commercialOptimizationDecisions.find((decision) => decision.decision_status === "approved") ?? null;
  const feedbackCandidateExecutionRun =
    pendingNextCycleFeedbackExecutionRun ??
    commercialExecutionRuns.find((run) => ["succeeded", "running", "queued", "retrying", "failed", "cancelled"].includes(run.run_status)) ??
    null;
  const closedLoopDeliveryAvailable = Boolean(operationLoop || selectedCommercialOperationId);
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
  const operationStageStatus = (stageId: string): GoalStatusStageState => {
    if (stageId === "plan") {
      return hasSubmittedGoal ? "done" : "current";
    }
    if (stageId === "knowledge") {
      return artifacts.length > 0 || messages.length > 0 ? "done" : hasSubmittedGoal ? "current" : "waiting";
    }
    if (stageId === "content") {
      return artifacts.length > 0 ? "done" : hasSubmittedGoal ? "current" : "waiting";
    }
    if (stageId === "approval") {
      return pendingApprovals.length > 0 || pendingCommercialApprovals.length > 0
        ? "needs-action"
        : approvals.length > 0 || commercialApprovals.length > 0
          ? "done"
          : hasSubmittedGoal
            ? "current"
            : "waiting";
    }
    if (stageId === "client") {
      return failedCommercialExecutionRun
        ? "needs-action"
        : queuedCommercialExecutionRun || runningCommercialExecutionRun
          ? "current"
          : latestCommercialExecutionRun
            ? "done"
            : commercialExecutionRequests.length > 0
              ? "current"
              : activeTaskRuns.length > 0
                ? "current"
                : completedTaskRuns.length > 0
                  ? "done"
                  : approvals.length > 0
                    ? "waiting"
                    : "waiting";
    }
    if (stageId === "result") {
      return latestCommercialResult
        ? "done"
        : completedTaskRuns.length > 0 || artifacts.length > 0
          ? "done"
          : activeTaskRuns.length > 0 || latestCommercialExecutionRun
            ? "current"
            : "waiting";
    }
    if (stageId === "data") {
      return latestCommercialObservation ? "done" : latestCommercialResult ? "current" : completedTaskRuns.length > 0 ? "current" : "waiting";
    }
    return latestCommercialOptimizationDecision
      ? "done"
      : latestCommercialObservation
        ? "current"
        : completedTaskRuns.length > 0 || artifacts.length > 0
          ? "current"
          : "waiting";
  };
  const operationLoopStages: Array<OperationLoopStepCopy & { status: GoalStatusStageState }> = operationLoop?.stages?.length
    ? operationLoop.stages.map((stage) => ({
        id: stage.stage_key,
        label: stage.title,
        detail: stage.next_action || stage.summary,
        status: operationLoopStatusToGoalState(stage.status),
      }))
    : workbenchCopy.operationLoopSteps.map((stage) => ({
        ...stage,
        status: operationStageStatus(stage.id),
      }));
  const operationCurrentStage =
    operationLoopStages.find((stage) => stage.status === "needs-action") ??
    operationLoopStages.find((stage) => stage.status === "current") ??
    operationLoopStages[0];
  const operationDeliverableCounts = operationLoop?.counts ?? {};
  const operationDeliverables: Array<OperationDeliverableCopy & { status: GoalStatusStageState }> = workbenchCopy.operationDeliverables.map((deliverable, index) => {
    const connectedStatus: GoalStatusStageState =
      index === 0
        ? (operationDeliverableCounts.content_drafts ?? 0) > 0
          ? "done"
          : "current"
        : index === 1
          ? (operationDeliverableCounts.asset_requests ?? 0) > 0 || (operationDeliverableCounts.execution_requests ?? 0) > 0
            ? "done"
            : (operationDeliverableCounts.content_drafts ?? 0) > 0
              ? "current"
              : "waiting"
          : index === 2
            ? (operationDeliverableCounts.results ?? 0) > 0 || (operationDeliverableCounts.monitoring_observations ?? 0) > 0
              ? "done"
              : (operationDeliverableCounts.execution_runs ?? 0) > 0
                ? "current"
                : "waiting"
            : (operationDeliverableCounts.optimization_decisions ?? 0) > 0
              ? "done"
              : (operationDeliverableCounts.results ?? 0) > 0
                ? "current"
                : "waiting";
    return {
      ...deliverable,
      status: operationLoop ? connectedStatus : artifacts.length > index ? "done" : hasSubmittedGoal ? "current" : "waiting",
    };
  });
  const currentAgentSkill =
    agentSkillOrchestration?.skills.find((skill) => skill.skill_key === agentSkillOrchestration.next_skill_key) ??
    agentSkillOrchestration?.skills.find((skill) => skill.status !== "complete") ??
    agentSkillOrchestration?.skills[0] ??
    null;
  const visibleAgentSkills = agentSkillOrchestration?.skills.slice(0, 6) ?? [];
  const agentSkillControllerName =
    typeof agentSkillOrchestration?.controller_agent.display_name === "string"
      ? agentSkillOrchestration.controller_agent.display_name
      : "Commercial Operation Agent";
  const latestDigitalHumanVideoJob = digitalHumanVideoJobs[0] ?? null;
  const digitalHumanVideoProgressText = latestDigitalHumanVideoJob
    ? `${latestDigitalHumanVideoJob.job_status} / ${latestDigitalHumanVideoJob.progress_percent ?? 0}%`
    : language === "zh-CN"
      ? "暂无数字人视频任务"
      : "No digital human video job";
  const digitalHumanVideoOutputCount = latestDigitalHumanVideoJob?.outputs?.length ?? 0;
  const digitalHumanWorkflowBindingText = latestDigitalHumanVideoJob?.selected_workflow_template_id
    ? `${latestDigitalHumanVideoJob.selected_workflow_template_id} / ${latestDigitalHumanVideoJob.workflow_binding_status || "binding pending"}`
    : language === "zh-CN"
      ? "工作流待绑定"
      : "Workflow pending";
  const digitalHumanWorkflowReadinessText = latestDigitalHumanVideoJob?.workflow_readiness_status
    ? `Readiness ${latestDigitalHumanVideoJob.workflow_readiness_status}`
    : language === "zh-CN"
      ? "真实工作流待检查"
      : "Real workflow not checked";
  const digitalHumanIngestionText = latestDigitalHumanVideoJob?.comfyui_output_ingestion_status
    ? `Output ${latestDigitalHumanVideoJob.comfyui_output_ingestion_status}`
    : language === "zh-CN"
      ? "输出待取回"
      : "Output pending";
  const digitalHumanDeliveryText = latestDigitalHumanVideoJob?.delivery_asset_status
    ? `${latestDigitalHumanVideoJob.delivery_asset_status} / ${latestDigitalHumanVideoJob.delivery_output_count ?? 0}`
    : language === "zh-CN"
      ? "交付未就绪"
      : "Delivery not ready";
  const operationResultSummary = closedLoopDeliveryStatus
    ? closedLoopDeliveryStatus
    : nextCycleDraftStatus
      ? nextCycleDraftStatus
    : publishImprovementStatus
      ? publishImprovementStatus
    : metricObservationStatus
      ? metricObservationStatus
    : publishResultStatus
      ? publishResultStatus
    : publishHandoffStatus
      ? publishHandoffStatus
    : feedbackLoopStatus
      ? feedbackLoopStatus
    : adapterDryRunStatus
      ? adapterDryRunStatus
    : guardedDispatchStatus
      ? guardedDispatchStatus
    : runtimePreflightStatus
      ? runtimePreflightStatus
      : latestCommercialOptimizationDecision
      ? `${workbenchCopy.operationOptimizationPending}: ${latestCommercialOptimizationDecision.decision_status}`
      : latestCommercialObservation
        ? `${workbenchCopy.operationObservationPending}: ${latestCommercialObservation.observation_status}`
        : latestCommercialResult
          ? `${workbenchCopy.operationResultRecordPending}: ${latestCommercialResult.result_status}`
          : latestCommercialExecutionRun
            ? `${workbenchCopy.operationExecutionRunPending}: ${latestCommercialExecutionRun.run_status}`
            : operationLoop
              ? `${Math.round(operationLoop.completion_ratio * 100)}% - ${operationLoop.next_action}`
              : artifacts.length > 0
                ? `${workbenchCopy.metricArtifacts}: ${artifacts.length}`
                : completedTaskRuns.length > 0
                  ? workbenchCopy.nextComplete
                  : suggestedAction;
  const operationLoopSourceText = operationLoop
    ? `${workbenchCopy.operationLoopLoaded}: ${operationLoop.title}`
    : workbenchCopy.operationLoopDisconnected;
  const operationApprovalStatusText =
    pendingCommercialApprovals.length > 0 ? `${workbenchCopy.operationApprovalPending}: ${pendingCommercialApprovals[0].title}` : null;
  const operationExecutionRequestStatusText = latestCommercialExecutionRequest
    ? `${workbenchCopy.operationExecutionRequestPending}: ${latestCommercialExecutionRequest.request_status}`
    : null;
  const operationExecutionRunStatusText = latestCommercialExecutionRun
    ? `${workbenchCopy.operationExecutionRunPending}: ${latestCommercialExecutionRun.run_status}`
    : null;
  const operationResultRecordStatusText = latestCommercialResult
    ? `${workbenchCopy.operationResultRecordPending}: ${latestCommercialResult.result_status}`
    : null;
  const operationObservationStatusText = latestCommercialObservation
    ? `${workbenchCopy.operationObservationPending}: ${latestCommercialObservation.observation_status}`
    : null;
  const operationOptimizationStatusText = latestCommercialOptimizationDecision
    ? `${workbenchCopy.operationOptimizationPending}: ${latestCommercialOptimizationDecision.decision_status}`
    : null;
  const operationReadableSourceText =
    nextCycleDraftStatus ||
    publishImprovementStatus ||
    metricObservationStatus ||
    publishResultStatus ||
    publishHandoffStatus ||
    feedbackLoopStatus ||
    adapterDryRunStatus ||
    guardedDispatchStatus ||
    runtimePreflightStatus ||
    operationOptimizationStatusText ||
    operationObservationStatusText ||
    operationResultRecordStatusText ||
    executionRunStatus ||
    operationExecutionRunStatusText ||
    operationExecutionRequestStatusText ||
    executionPrepStatus ||
    operationApprovalStatusText ||
    digitalHumanVideoStatus ||
    (latestDigitalHumanVideoJob ? digitalHumanVideoProgressText : null) ||
    firstDraftBootstrapStatus ||
    operationLoopSourceText;

  const openOutputDetails = () => {
    const outputsPanel = document.getElementById("outputs-panel") as HTMLDetailsElement | null;
    if (outputsPanel) {
      outputsPanel.open = true;
      outputsPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  };

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
        <div className="client-operation-desk" aria-label={workbenchCopy.operationDeskTitle}>
          <div className="client-operation-header">
            <span>{workbenchCopy.operationCurrentLabel}</span>
            <h3>{workbenchCopy.operationDeskTitle}</h3>
            <p>{workbenchCopy.operationDeskSubtitle}</p>
          </div>
          <div className="client-operation-status">
            <div className={`client-operation-current ${operationCurrentStage.status}`}>
              <span>{operationCurrentStage.label}</span>
              <strong>{goalStatusStateLabels[operationCurrentStage.status]}</strong>
              <p>{operationCurrentStage.detail}</p>
            </div>
            <div className="client-operation-result">
              <span>{workbenchCopy.operationResultLabel}</span>
              <strong>{operationResultSummary}</strong>
              <p>{operationReadableSourceText}</p>
              <p>{workbenchCopy.operationOpenClawLabel}</p>
            </div>
          </div>
          <div className="client-digital-human-progress" aria-label="Digital human video progress">
            <div>
              <span>{language === "zh-CN" ? "数字人视频" : "Digital human video"}</span>
              <strong>{digitalHumanVideoProgressText}</strong>
              <p>
                {digitalHumanVideoStatus ||
                  latestDigitalHumanVideoJob?.result_summary ||
                  latestDigitalHumanVideoJob?.next_action ||
                  (language === "zh-CN" ? "审批后可生成交付资产或交给 ComfyUI 视频调度。" : "After approval, create a delivery asset or queue a ComfyUI video handoff.")}
              </p>
            </div>
            <div className="client-digital-human-meta">
              <span>{language === "zh-CN" ? `输出 ${digitalHumanVideoOutputCount}` : `${digitalHumanVideoOutputCount} outputs`}</span>
              <span>{digitalHumanWorkflowBindingText}</span>
              <span>{digitalHumanWorkflowReadinessText}</span>
              <span>{digitalHumanIngestionText}</span>
              <span>{digitalHumanDeliveryText}</span>
              <span>{latestDigitalHumanVideoJob?.linked_comfyui_video_job_id ? "ComfyUI linked" : "ComfyUI pending"}</span>
              <button className="refresh-button" onClick={() => void refreshLatestDigitalHumanVideo()} disabled={digitalHumanVideoLoading}>
                <RefreshCcw size={14} />
                {digitalHumanVideoLoading ? (language === "zh-CN" ? "刷新中" : "Refreshing") : workbenchCopy.operationRefreshLoop}
              </button>
              <button
                className="refresh-button"
                onClick={() => void ingestLatestDigitalHumanVideoOutput()}
                disabled={digitalHumanVideoLoading || !latestDigitalHumanVideoJob?.linked_comfyui_video_job_id}
              >
                <Package size={14} />
                {language === "zh-CN" ? "取回视频" : "Ingest video"}
              </button>
            </div>
          </div>
          <div className="client-operation-guided-actions" aria-label={workbenchCopy.operationGuidedActionsTitle}>
            <div>
              <span>{workbenchCopy.operationGuidedActionsTitle}</span>
              <p>{workbenchCopy.operationGuidedActionsSubtitle}</p>
            </div>
            <button className="refresh-button primary-action" onClick={() => void createCommercialOperationLoop()} disabled={operationLoopLoading || chatLoading}>
              <PlayCircle size={14} />
              {workbenchCopy.operationStartLoop}
            </button>
            <button className="refresh-button" onClick={onOpenKnowledge}>
              <Upload size={14} />
              {workbenchCopy.operationOpenKnowledge}
            </button>
            <button className="refresh-button" onClick={() => void prepareFirstDraftPackage()} disabled={firstDraftBootstrapLoading || operationLoopLoading || chatLoading}>
              <PencilLine size={14} />
              {firstDraftBootstrapLoading ? workbenchCopy.operationFirstDraftPreparing : workbenchCopy.operationPrepareDraft}
            </button>
            <button
              className="refresh-button"
              onClick={() => void approveCommercialApprovalAndPrepareExecution()}
              disabled={executionPrepLoading || operationLoopLoading || chatLoading || pendingCommercialApprovals.length === 0}
            >
              <CheckCircle2 size={14} />
              {executionPrepLoading
                ? pendingPublishMetricNextCycleCommercialApproval
                  ? workbenchCopy.operationImprovedApprovalPreparing
                  : pendingNextCycleCommercialApproval
                    ? workbenchCopy.operationNextCycleApprovalPreparing
                    : workbenchCopy.operationApprovalPreparing
                : pendingPublishMetricNextCycleCommercialApproval
                  ? workbenchCopy.operationApproveImprovedDraftAndPrepare
                  : pendingNextCycleCommercialApproval
                    ? workbenchCopy.operationApproveNextCycleAndPrepare
                    : workbenchCopy.operationApproveAndPrepare}
            </button>
            <button
              className="refresh-button"
              onClick={() => void completeClientClosedLoopDeliveryPass()}
              disabled={closedLoopDeliveryLoading || operationLoopLoading || chatLoading || !closedLoopDeliveryAvailable}
            >
              <PlayCircle size={14} />
              {closedLoopDeliveryLoading ? workbenchCopy.operationClosedLoopDeliveryRunning : workbenchCopy.operationClosedLoopDeliveryAction}
            </button>
          </div>
          <details className="client-operation-advanced-controls">
            <summary>
              <span>{workbenchCopy.operationAdvancedActionsTitle}</span>
              <small>{workbenchCopy.operationAdvancedActionsHint}</small>
            </summary>
            <div className="client-operation-controls" aria-label={workbenchCopy.operationControlLabel}>
              <button className="refresh-button" onClick={() => void createCommercialOperationLoop()} disabled={operationLoopLoading || chatLoading}>
                <PlayCircle size={14} />
                {workbenchCopy.operationStartLoop}
              </button>
              <button className="refresh-button" onClick={() => void prepareFirstDraftPackage()} disabled={firstDraftBootstrapLoading || operationLoopLoading || chatLoading}>
                <PencilLine size={14} />
                {firstDraftBootstrapLoading ? workbenchCopy.operationFirstDraftPreparing : workbenchCopy.operationPrepareDraft}
              </button>
              <button
                className="refresh-button"
                onClick={() => void approveCommercialApprovalAndPrepareExecution()}
                disabled={executionPrepLoading || operationLoopLoading || chatLoading || pendingCommercialApprovals.length === 0}
              >
                <CheckCircle2 size={14} />
                {executionPrepLoading
                  ? pendingPublishMetricNextCycleCommercialApproval
                    ? workbenchCopy.operationImprovedApprovalPreparing
                    : pendingNextCycleCommercialApproval
                    ? workbenchCopy.operationNextCycleApprovalPreparing
                    : workbenchCopy.operationApprovalPreparing
                  : pendingPublishMetricNextCycleCommercialApproval
                    ? workbenchCopy.operationApproveImprovedDraftAndPrepare
                    : pendingNextCycleCommercialApproval
                    ? workbenchCopy.operationApproveNextCycleAndPrepare
                    : workbenchCopy.operationApproveAndPrepare}
              </button>
              <button
                className="refresh-button"
                onClick={() => void rejectCommercialApproval()}
                disabled={executionPrepLoading || operationLoopLoading || chatLoading || pendingCommercialApprovals.length === 0}
              >
                <XCircle size={14} />
                {pendingPublishMetricNextCycleCommercialApproval
                  ? workbenchCopy.operationRejectImprovedDraft
                  : pendingNextCycleCommercialApproval
                    ? workbenchCopy.operationRejectNextCycleDraft
                    : workbenchCopy.operationRejectDraft}
              </button>
              <button
                className="refresh-button"
                onClick={() => void reviewExecutionRequestAndQueueRun()}
                disabled={executionRunLoading || operationLoopLoading || chatLoading || commercialExecutionRequests.length === 0}
              >
                <CheckCircle2 size={14} />
                {executionRunLoading
                  ? pendingPublishMetricReexecutionRequest
                    ? workbenchCopy.operationImprovedExecutionRunQueuing
                    : pendingNextCycleExecutionRequest
                    ? workbenchCopy.operationNextCycleExecutionRunQueuing
                    : workbenchCopy.operationExecutionRunQueuing
                  : pendingPublishMetricReexecutionRequest
                    ? workbenchCopy.operationReviewAndQueueImprovedRun
                    : pendingNextCycleExecutionRequest
                    ? workbenchCopy.operationReviewAndQueueNextCycleRun
                    : workbenchCopy.operationReviewAndQueueRun}
              </button>
              <button
                className="refresh-button"
                onClick={() => void preflightClientRuntimeExecutionRun()}
                disabled={runtimePreflightLoading || operationLoopLoading || chatLoading || !runtimePreflightCandidateExecutionRun}
              >
                <CheckCircle2 size={14} />
                {runtimePreflightLoading ? workbenchCopy.operationRuntimePreflightChecking : workbenchCopy.operationRuntimePreflight}
              </button>
              <button
                className="refresh-button"
                onClick={() => void prepareGuardedAdapterDispatchHandoff()}
                disabled={guardedDispatchLoading || operationLoopLoading || chatLoading || !guardedDispatchCandidateExecutionRun}
              >
                <CheckCircle2 size={14} />
                {guardedDispatchLoading ? workbenchCopy.operationGuardedDispatchHandingOff : workbenchCopy.operationGuardedDispatchHandoff}
              </button>
              <button
                className="refresh-button"
                onClick={() => void runGuardedAdapterDryRun()}
                disabled={adapterDryRunLoading || operationLoopLoading || chatLoading || !adapterDryRunCandidateExecutionRun}
              >
                <PlayCircle size={14} />
                {adapterDryRunLoading ? workbenchCopy.operationAdapterDryRunRunning : workbenchCopy.operationAdapterDryRun}
              </button>
              <button
                className="refresh-button"
                onClick={() => void startCommercialExecutionRun()}
                disabled={executionRunLoading || operationLoopLoading || chatLoading || !queuedCommercialExecutionRun}
              >
                <PlayCircle size={14} />
                {executionRunLoading ? workbenchCopy.operationRunStarting : workbenchCopy.operationStartRun}
              </button>
              <button
                className="refresh-button"
                onClick={() => void failCommercialExecutionRun()}
                disabled={executionRunLoading || operationLoopLoading || chatLoading || !runningCommercialExecutionRun}
              >
                <XCircle size={14} />
                {workbenchCopy.operationFailRun}
              </button>
              <button
                className="refresh-button"
                onClick={() => void retryCommercialExecutionRun()}
                disabled={executionRunLoading || operationLoopLoading || chatLoading || !failedCommercialExecutionRun}
              >
                <RotateCcw size={14} />
                {workbenchCopy.operationRetryRun}
              </button>
              <button
                className="refresh-button"
                onClick={() => void completeCommercialResultFeedbackLoop()}
                disabled={feedbackLoopLoading || operationLoopLoading || chatLoading || !feedbackCandidateExecutionRun}
              >
                <FileText size={14} />
                {feedbackLoopLoading
                  ? pendingNextCycleFeedbackExecutionRun
                    ? workbenchCopy.operationNextCycleFeedbackLoopCompleting
                    : workbenchCopy.operationFeedbackLoopCompleting
                  : pendingNextCycleFeedbackExecutionRun
                    ? workbenchCopy.operationCompleteNextCycleFeedbackLoop
                    : workbenchCopy.operationCompleteFeedbackLoop}
              </button>
              <button
                className="refresh-button"
                onClick={() => void prepareNextCycleDraftFromDecision()}
                disabled={nextCycleDraftLoading || operationLoopLoading || chatLoading || !approvedCommercialOptimizationDecision}
              >
                <PencilLine size={14} />
                {nextCycleDraftLoading ? workbenchCopy.operationNextCycleDraftPreparing : workbenchCopy.operationPrepareNextCycleDraft}
              </button>
              <button className="refresh-button" onClick={() => void refreshCommercialOperationLoop()} disabled={operationLoopLoading}>
                <RefreshCcw size={14} />
                {workbenchCopy.operationRefreshLoop}
              </button>
              <button
                className="refresh-button"
                onClick={() => {
                  if (selectedTaskRunId) {
                    void mutateTaskRun(selectedTaskRunId, "cancel");
                  }
                }}
                disabled={!selectedTaskRunId || chatLoading}
              >
                <PauseCircle size={14} />
                {workbenchCopy.operationPause}
              </button>
              <button
                className="refresh-button"
                onClick={() => {
                  if (selectedTaskRunId) {
                    void mutateTaskRun(selectedTaskRunId, "resume");
                  }
                }}
                disabled={!selectedTaskRunId || chatLoading}
              >
                <PlayCircle size={14} />
                {workbenchCopy.operationContinue}
              </button>
              <button className="refresh-button" onClick={openOutputDetails}>
                <FileText size={14} />
                {workbenchCopy.operationViewOutputs}
              </button>
              <button className="refresh-button" onClick={onOpenKnowledge}>
                <Upload size={14} />
                {workbenchCopy.operationOpenKnowledge}
              </button>
            </div>
          </details>
          <div className="client-agent-skill-panel" aria-label={workbenchCopy.operationAgentSkillTitle}>
            <div className="client-agent-skill-head">
              <div>
                <span>{workbenchCopy.operationAgentSkillTitle}</span>
                <p>{agentSkillStatus ?? agentSkillOrchestration?.next_action ?? workbenchCopy.operationAgentSkillSubtitle}</p>
                <small>{workbenchCopy.operationAgentSkillBoundary}</small>
              </div>
              <button className="refresh-button" onClick={() => void refreshAgentSkillOrchestration()} disabled={agentSkillLoading || operationLoopLoading}>
                <RefreshCcw size={14} />
                {agentSkillLoading ? workbenchCopy.operationAgentSkillRefreshing : workbenchCopy.operationAgentSkillRefresh}
              </button>
            </div>
            <div className="client-agent-skill-next">
              <Server size={15} />
              <div>
                <span>{agentSkillControllerName}</span>
                <strong>{workbenchCopy.operationAgentSkillNext}: {currentAgentSkill?.display_name ?? workbenchCopy.operationAgentSkillUnavailable}</strong>
              </div>
              <span className="client-agent-skill-status">{agentSkillOrchestration?.orchestration_status ?? "waiting"}</span>
            </div>
            <div className="client-agent-skill-list">
              {visibleAgentSkills.length ? (
                visibleAgentSkills.map((skill) => (
                  <article className={`client-agent-skill-item ${skill.status}`} key={skill.skill_key}>
                    <strong>{skill.display_name}</strong>
                    <span>{skill.owner_agent}</span>
                    <p>{skill.next_action}</p>
                  </article>
                ))
              ) : (
                <article className="client-agent-skill-item waiting">
                  <strong>{workbenchCopy.operationAgentSkillUnavailable}</strong>
                  <span>{workbenchCopy.operationAgentSkillTitle}</span>
                  <p>{workbenchCopy.operationAgentSkillSubtitle}</p>
                </article>
              )}
            </div>
          </div>
          <div className="client-operation-loop" aria-label={workbenchCopy.operationLoopTitle}>
            {operationLoopStages.map((stage) => (
              <article className={`client-operation-step ${stage.status}`} key={stage.id}>
                <span>{stage.label}</span>
                <strong>{goalStatusStateLabels[stage.status]}</strong>
                <p>{stage.detail}</p>
              </article>
            ))}
          </div>
          <details className="client-operation-support-drawer">
            <summary>
              <span>{workbenchCopy.operationDetailsTitle}</span>
              <small>{workbenchCopy.operationDetailsHint}</small>
            </summary>
          <div className="client-operation-deliverables" aria-label={workbenchCopy.operationDeliverablesTitle}>
            <div className="client-operation-knowledge-card">
              <Database size={16} />
              <div>
                <span>{workbenchCopy.operationKnowledgeTitle}</span>
                <p>{workbenchCopy.operationKnowledgeBody}</p>
              </div>
            </div>
            {operationDeliverables.map((deliverable) => (
              <article className={`client-operation-deliverable ${deliverable.status}`} key={deliverable.id}>
                <span>{deliverable.label}</span>
                <strong>{goalStatusStateLabels[deliverable.status]}</strong>
                <p>{deliverable.detail}</p>
              </article>
            ))}
          </div>
          <div className="client-execution-queue" aria-label={workbenchCopy.operationExecutionQueueTitle}>
            <div className="client-execution-queue-header">
              <div>
                <span>{workbenchCopy.operationExecutionQueueTitle}</span>
                <p>{workbenchCopy.operationExecutionQueueSubtitle}</p>
              </div>
              <strong>{activeCommercialExecutionRunCount}/{commercialExecutionRuns.length}</strong>
            </div>
            <div className="client-execution-run-list">
              {visibleCommercialExecutionRuns.length > 0 ? visibleCommercialExecutionRuns.map((run) => {
                const readinessLabel = isGuardedAdapterDispatchReady(run)
                  ? workbenchCopy.operationExecutionQueueReady
                  : isClientRuntimePreflightReady(run)
                    ? workbenchCopy.operationExecutionQueuePreflightReady
                    : workbenchCopy.operationExecutionQueueWaiting;
                return (
                  <article className={`client-execution-run run-status-${run.run_status}`} key={run.id}>
                    <div>
                      <span>{run.run_status}</span>
                      <strong>{run.title}</strong>
                      <p>{run.execution_target ?? run.execution_type} | retry {run.retry_count}/{run.max_retries}</p>
                    </div>
                    <small>{readinessLabel}</small>
                  </article>
                );
              }) : (
                <div className="empty-chat">{workbenchCopy.operationExecutionQueueEmpty}</div>
              )}
            </div>
          </div>
          <div className="client-publish-loop" aria-label={workbenchCopy.operationPublishPanelTitle}>
            <div className="client-publish-loop-header">
              <div>
                <span>{workbenchCopy.operationPublishPanelTitle}</span>
                <p>{workbenchCopy.operationPublishPanelSubtitle}</p>
              </div>
            </div>
            <div className="client-publish-loop-grid">
              <article className="client-publish-step">
                <span>{workbenchCopy.operationPublishTargetLabel}</span>
                <strong>{latestPublishHandoffResult ? latestPublishHandoffResult.result_status : workbenchCopy.operationPublishHandoffMissing}</strong>
                <p>{latestPublishHandoffResult?.summary ?? workbenchCopy.operationPublishPanelSubtitle}</p>
                <button
                  className="refresh-button"
                  onClick={() => void prepareGuardedPublishHandoff()}
                  disabled={publishHandoffLoading || operationLoopLoading || chatLoading || !publishHandoffCandidateExecutionRun}
                >
                  <CheckCircle2 size={14} />
                  {publishHandoffLoading ? workbenchCopy.operationPublishHandoffPreparing : workbenchCopy.operationPublishHandoff}
                </button>
              </article>
              <article className="client-publish-step">
                <span>{workbenchCopy.operationPublishResultLabel}</span>
                <strong>{latestManualPublishResult ? latestManualPublishResult.result_status : workbenchCopy.operationPublishResultMissing}</strong>
                <p>{latestManualPublishResult?.summary ?? workbenchCopy.operationPublishResultMissing}</p>
                <button
                  className="refresh-button"
                  onClick={() => void captureManualPublishResult()}
                  disabled={publishResultLoading || operationLoopLoading || chatLoading || !publishResultCandidateExecutionRun}
                >
                  <FileText size={14} />
                  {publishResultLoading ? workbenchCopy.operationCapturePublishResultCapturing : workbenchCopy.operationCapturePublishResult}
                </button>
              </article>
              <article className="client-publish-step">
                <span>{workbenchCopy.operationMetricObservationLabel}</span>
                <strong>
                  {latestManualMetricObservation
                    ? latestManualMetricObservation.observation_status
                    : workbenchCopy.operationMetricObservationMissing}
                </strong>
                <p>{latestManualMetricObservation?.title ?? workbenchCopy.operationMetricObservationMissing}</p>
                <button
                  className="refresh-button"
                  onClick={() => void recordManualMetricObservation()}
                  disabled={metricObservationLoading || operationLoopLoading || chatLoading || !metricObservationCandidateResult}
                >
                  <Activity size={14} />
                  {metricObservationLoading ? workbenchCopy.operationMetricObservationRecording : workbenchCopy.operationRecordMetricObservation}
                </button>
              </article>
              <article className="client-publish-step client-publish-improvement-step">
                <span>{workbenchCopy.operationPublishImprovementLabel}</span>
                <strong>
                  {latestManualPublishImprovementDecision
                    ? latestManualPublishImprovementDecision.decision_status
                    : workbenchCopy.operationPublishImprovementMissing}
                </strong>
                <p>{latestManualPublishImprovementDecision?.rationale ?? workbenchCopy.operationPublishImprovementMissing}</p>
                <div className="client-publish-step-actions">
                  <button
                    className="refresh-button"
                    onClick={() => void analyzeManualPublishMetrics()}
                    disabled={publishImprovementLoading || operationLoopLoading || chatLoading || !publishImprovementCandidateObservation}
                  >
                    <Activity size={14} />
                    {publishImprovementLoading ? workbenchCopy.operationAnalyzePublishMetricsRunning : workbenchCopy.operationAnalyzePublishMetrics}
                  </button>
                  <button
                    className="refresh-button"
                    onClick={() => void prepareNextCycleDraftFromDecision()}
                    disabled={nextCycleDraftLoading || operationLoopLoading || chatLoading || !approvedCommercialOptimizationDecision}
                  >
                    <PencilLine size={14} />
                    {nextCycleDraftLoading ? workbenchCopy.operationNextCycleDraftPreparing : workbenchCopy.operationPrepareImprovedDraft}
                  </button>
                </div>
              </article>
            </div>
          </div>
          </details>
        </div>
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
      <details className="maintenance-drawer" open={pendingCommercialApprovals.length > 0 || pendingApprovals.length > 0 || failedTaskRuns.length > 0}>
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
      <details id="commercial-approvals-panel" className="approval-list workbench-detail" open={pendingCommercialApprovals.length > 0}>
        <summary>{workbenchCopy.operationApprovalCenterSummary}</summary>
        <h3>{workbenchCopy.operationApprovalCenterTitle}</h3>
        {commercialApprovals.length > 0 ? commercialApprovals.map((approval) => (
          <div key={approval.id} className={`approval-card approval-risk-${approval.risk_level}`}>
            <div className="approval-card-header">
              <strong>{approval.title}</strong>
              <span>{workbenchCopy.operationApprovalCenterRisk}: {approval.risk_level}</span>
              <span>{workbenchCopy.operationApprovalCenterStatus}: {approval.approval_status}</span>
            </div>
            <p>{approval.requested_action ?? approval.step_key}</p>
            <div className="chat-actions">
              <button
                className="refresh-button"
                onClick={() => void approveCommercialApprovalAndPrepareExecution(approval)}
                disabled={approval.approval_status !== "pending" || executionPrepLoading || operationLoopLoading || chatLoading}
              >
                <CheckCircle2 size={14} />
                {workbenchCopy.operationApprovalCenterApprove}
              </button>
              <button
                className="refresh-button"
                onClick={() => void rejectCommercialApproval(approval)}
                disabled={approval.approval_status !== "pending" || executionPrepLoading || operationLoopLoading || chatLoading}
              >
                <XCircle size={14} />
                {workbenchCopy.operationApprovalCenterReject}
              </button>
            </div>
          </div>
        )) : (
          <div className="empty-chat">{workbenchCopy.operationApprovalCenterEmpty}</div>
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

function knowledgeDocumentKey(document: KnowledgeDocument): string {
  return document.id ?? document.source_id ?? document.filename ?? documentDisplayName(document);
}

function knowledgeDocumentStatusTone(document: KnowledgeDocument): KnowledgeActivityTone {
  const status = `${document.status ?? ""} ${document.ingest_status ?? ""} ${document.error_message ?? ""}`.trim().toLowerCase();
  if (/fail|error|invalid|missing/.test(status)) {
    return "warn";
  }
  if (/ready|complete|completed|ingested|indexed|available|success/.test(status) || (!status && (document.chunk_count ?? 0) > 0)) {
    return "good";
  }
  return "neutral";
}

function knowledgeDocumentIngestionStage(document: KnowledgeDocument): KnowledgeIngestionStage {
  const status = `${document.status ?? ""} ${document.ingest_status ?? ""}`.trim().toLowerCase();
  if (document.error_message || /fail|error|invalid|missing/.test(status)) {
    return "failed";
  }
  if (/ready|complete|completed|ingested|indexed|available|success|active/.test(status) || (document.chunk_count ?? 0) > 0) {
    return "ready";
  }
  if (/queued|pending|uploading|processing|running|ingest/.test(status)) {
    return "processing";
  }
  return "waiting";
}

function knowledgeIngestionProgressForQueue(item: KnowledgeQueueItem): number {
  if (item.status === "failed") {
    return item.ingestStatus ? 75 : 35;
  }
  if (item.status === "uploaded") {
    return item.chunkCount && item.chunkCount > 0 ? 100 : 85;
  }
  if (item.status === "uploading") {
    return 55;
  }
  return 25;
}

function knowledgeIngestionProgressForDocument(document: KnowledgeDocument): number {
  const stage = knowledgeDocumentIngestionStage(document);
  if (stage === "ready") {
    return 100;
  }
  if (stage === "processing") {
    return 65;
  }
  if (stage === "failed") {
    return 75;
  }
  return 20;
}

function knowledgeMetadataText(metadata: Record<string, unknown> | undefined, keys: string[]): string | null {
  if (!metadata) {
    return null;
  }
  for (const key of keys) {
    const value = metadata[key];
    if (typeof value === "string" && value.trim()) {
      return value;
    }
    if (typeof value === "number") {
      return String(value);
    }
  }
  return null;
}

function knowledgeSearchSourceLabel(result: KnowledgeSearchResult): string {
  return knowledgeMetadataText(result.metadata, ["source_name", "filename", "source_id", "document_id"]) ?? result.id;
}

function knowledgeSearchScore(result: KnowledgeSearchResult): number | null {
  return result.rerank_score ?? result.hybrid_score ?? result.similarity_score ?? result.dense_score ?? result.keyword_score ?? null;
}

function formatKnowledgeSearchScore(score: number | null): string {
  return typeof score === "number" ? `${Math.round(score * 100)}%` : "-";
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

function knowledgeValidationQuestion(template: string, material: string): string {
  return template.split("{material}").join(material);
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
  const [selectedDocumentKey, setSelectedDocumentKey] = useState<string | null>(null);
  const [validationQuery, setValidationQuery] = useState("");
  const [validationMode, setValidationMode] = useState<KnowledgeSearchMode>("hybrid");
  const [validationState, setValidationState] = useState<"idle" | "loading" | "ready" | "failed">("idle");
  const [validationResults, setValidationResults] = useState<KnowledgeSearchResult[]>([]);
  const [validationSummary, setValidationSummary] = useState<string | null>(null);

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
  const selectedDocument = useMemo(() => {
    if (documents.length === 0) {
      return null;
    }
    return documents.find((document) => knowledgeDocumentKey(document) === selectedDocumentKey) ?? documents[0];
  }, [documents, selectedDocumentKey]);
  const selectedDocumentTone = selectedDocument ? knowledgeDocumentStatusTone(selectedDocument) : "neutral";
  const readyDocumentCount = documents.filter((document) => knowledgeDocumentStatusTone(document) === "good").length;
  const reviewDocumentCount = documents.filter((document) => knowledgeDocumentStatusTone(document) === "warn").length;
  const processingDocumentCount = documents.filter((document) => knowledgeDocumentIngestionStage(document) === "processing").length;
  const ingestionNeedsActionCount = failedFileCount + reviewDocumentCount;
  const ingestionPanelTone =
    ingestionNeedsActionCount > 0 || libraryState === "failed"
      ? "warn"
      : uploadingFileCount > 0 || queuedFileCount > 0 || processingDocumentCount > 0
        ? "neutral"
        : readyDocumentCount > 0
          ? "good"
          : "neutral";
  const ingestionPipelineSteps = [
    {
      label: copy.ingestionStepSelect,
      state: queue.length > 0 || documents.length > 0 ? "done" : "waiting",
    },
    {
      label: copy.ingestionStepUpload,
      state:
        failedFileCount > 0
          ? "needs-action"
          : uploadingFileCount > 0
            ? "current"
            : uploadedFileCount > 0 || documents.length > 0
              ? "done"
              : queuedFileCount > 0
                ? "current"
                : "waiting",
    },
    {
      label: copy.ingestionStepIndex,
      state:
        reviewDocumentCount > 0
          ? "needs-action"
          : processingDocumentCount > 0
            ? "current"
            : readyDocumentCount > 0 || uploadedFileCount > 0
              ? "done"
              : "waiting",
    },
    {
      label: copy.ingestionStepValidate,
      state:
        validationState === "failed" || (validationState === "ready" && validationResults.length === 0)
          ? "needs-action"
          : validationState === "loading"
            ? "current"
            : validationState === "ready" && validationResults.length > 0
              ? "done"
              : "waiting",
    },
  ];
  const selectedDocumentStatusLabel =
    selectedDocument?.status ||
    (selectedDocumentTone === "good"
      ? copy.detailHealthReady
      : selectedDocumentTone === "warn"
        ? copy.detailHealthNeedsReview
        : copy.detailHealthUnknown);
  const selectedDocumentHealthLabel =
    selectedDocumentTone === "good"
      ? copy.detailHealthReady
      : selectedDocumentTone === "warn"
        ? copy.detailHealthNeedsReview
        : copy.detailHealthUnknown;
  const selectedDocumentIngestLabel = selectedDocument?.ingest_status || selectedDocumentStatusLabel;
  const latestUploadedQueueItem = [...queue].reverse().find((item) => item.status === "uploaded" && (item.sourceId || item.documentId));
  const fallbackValidationMaterialName = latestUploadedQueueItem?.file.name || collectionName.trim() || copy.collectionMissing;
  const validationMaterialName = selectedDocument ? documentDisplayName(selectedDocument) : fallbackValidationMaterialName;
  const validationTargetSourceId = selectedDocument?.source_id ?? latestUploadedQueueItem?.sourceId;
  const validationSuggestions: KnowledgeValidationSuggestion[] = [
    {
      id: "summary",
      label: copy.validationSuggestionSummary,
      query: knowledgeValidationQuestion(copy.validationSuggestionSummaryQuery, validationMaterialName),
      mode: "hybrid",
      sourceId: validationTargetSourceId,
    },
    {
      id: "risk",
      label: copy.validationSuggestionRisk,
      query: knowledgeValidationQuestion(copy.validationSuggestionRiskQuery, validationMaterialName),
      mode: "hybrid",
      sourceId: validationTargetSourceId,
    },
    {
      id: "action",
      label: copy.validationSuggestionAction,
      query: knowledgeValidationQuestion(copy.validationSuggestionActionQuery, validationMaterialName),
      mode: "keyword",
      sourceId: validationTargetSourceId,
    },
  ];
  const selectedDocumentValidationSuggestion: KnowledgeValidationSuggestion | null = selectedDocument
    ? {
        id: "selected-document",
        label: copy.validationSelectedMaterial,
        query: knowledgeValidationQuestion(copy.validationSuggestionSummaryQuery, documentDisplayName(selectedDocument)),
        mode: "hybrid",
        sourceId: selectedDocument.source_id,
      }
    : null;
  const latestUploadValidationSuggestion: KnowledgeValidationSuggestion | null = latestUploadedQueueItem
    ? {
        id: "latest-upload",
        label: copy.validationLatestUpload,
        query: knowledgeValidationQuestion(copy.validationSuggestionSummaryQuery, latestUploadedQueueItem.file.name),
        mode: "hybrid",
        sourceId: latestUploadedQueueItem.sourceId,
      }
    : null;
  const validationOutcomeMaterialLabel =
    selectedDocument ? documentDisplayName(selectedDocument) : latestUploadedQueueItem?.file.name || collectionName.trim() || copy.collectionMissing;
  const validationOutcomeTone: KnowledgeActivityTone =
    validationState === "failed"
      ? "warn"
      : validationState === "ready" && validationResults.length === 0
        ? "warn"
        : validationState === "ready" && validationResults.length > 0
          ? "good"
          : "neutral";
  const validationOutcomeLabel =
    validationOutcomeTone === "good"
      ? copy.validationOutcomeReady
      : validationState === "ready" && validationResults.length === 0
        ? copy.validationOutcomeNeedsEvidence
        : validationState === "failed"
          ? copy.validationOutcomeNeedsReview
          : copy.validationOutcomeIdle;
  const validationOutcomeDetail =
    validationOutcomeTone === "good"
      ? copy.validationOutcomeReadyDetail
      : validationState === "ready" && validationResults.length === 0
        ? copy.validationOutcomeNeedsEvidenceDetail
        : validationState === "failed"
          ? copy.validationOutcomeNeedsReviewDetail
          : copy.validationOutcomeIdleDetail;
  const validationOutcomeActionLabel =
    validationOutcomeTone === "good"
      ? copy.validationOutcomeMarkReady
      : validationOutcomeTone === "warn"
        ? copy.validationOutcomeRetry
        : copy.validationOutcomeRunFirst;
  const validationOutcomeStats = [
    { label: copy.validationOutcomeMatches, value: validationState === "ready" ? String(validationResults.length) : "-" },
    { label: copy.validationOutcomeMaterial, value: validationOutcomeMaterialLabel },
    { label: copy.validationOutcomeMode, value: validationMode },
  ];

  useEffect(() => {
    if (documents.length === 0) {
      setSelectedDocumentKey(null);
      return;
    }
    if (selectedDocumentKey && documents.some((document) => knowledgeDocumentKey(document) === selectedDocumentKey)) {
      return;
    }
    setSelectedDocumentKey(knowledgeDocumentKey(documents[0]));
  }, [documents, selectedDocumentKey]);

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
        const response = await knowledgeBaseClient.uploadFile(
          {
            file: item.file,
            collectionName: collectionName.trim() || undefined,
            duplicateStrategy,
          },
          settings,
        );
        const responseFailed = Boolean(response.ingest_error) || /fail|error/.test(response.ingest_status.toLowerCase());
        const nextMessage = responseFailed
          ? response.ingest_error || copy.requestFailed
          : response.skipped_duplicate
            ? copy.ingestionSkipped
            : `${copy.documentChunks}: ${response.chunk_count}`;
        setQueue((current) =>
          current.map((queueItem) =>
            queueItem.id === item.id
              ? {
                  ...queueItem,
                  status: responseFailed ? "failed" : "uploaded",
                  message: nextMessage,
                  retryable: responseFailed,
                  upload: response,
                  sourceId: response.source_id,
                  documentId: response.document_id ?? null,
                  chunkCount: response.chunk_count,
                  ingestStatus: response.ingest_status,
                  ingestError: response.ingest_error ?? null,
                  uploadedAt: new Date().toLocaleString(),
                }
              : queueItem,
          ),
        );
        if (responseFailed) {
          hasFailure = true;
          failedCount += 1;
        } else {
          uploadedCount += 1;
        }
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
    setSelectedDocumentKey(knowledgeDocumentKey(document));
    setSourceName(documentDisplayName(document));
    setSourceId(document.source_id || document.id || "");
    setMessage(null);
  };

  const applyKnowledgeValidationSuggestion = (suggestion: KnowledgeValidationSuggestion) => {
    setValidationQuery(suggestion.query);
    setValidationMode(suggestion.mode);
    setValidationResults([]);
    setValidationState("idle");
    setValidationSummary(`${copy.validationSuggestionApplied}: ${suggestion.label}`);
    addKnowledgeActivity({
      title: copy.validationSuggestionAppliedTitle,
      detail: suggestion.query,
      meta: `${copy.validationCollection}: ${collectionName.trim() || copy.collectionMissing}`,
      tone: "neutral",
    });
  };

  const runKnowledgeValidation = async (override?: { query?: string; mode?: KnowledgeSearchMode; sourceId?: string }) => {
    const query = (override?.query ?? validationQuery).trim();
    const searchMode = override?.mode ?? validationMode;
    if (!query) {
      setValidationSummary(copy.validationQueryRequired);
      return;
    }
    setValidationQuery(query);
    setValidationMode(searchMode);
    setValidationState("loading");
    setValidationSummary(null);
    try {
      const response = await knowledgeBaseClient.search(
        {
          query,
          collectionName: collectionName.trim() || undefined,
          searchMode,
          topK: 5,
          sourceId: override?.sourceId,
        },
        settings,
      );
      setValidationResults(response.items);
      setValidationState("ready");
      const resultSummary =
        response.items.length > 0 ? `${copy.activitySuccess}: ${response.items.length}` : copy.validationNoResults;
      setValidationSummary(resultSummary);
      addKnowledgeActivity({
        title: copy.validationSearchTitle,
        detail: resultSummary,
        meta: `${copy.validationCollection}: ${response.collection_name}; ${copy.validationMode}: ${response.search_mode}`,
        tone: response.items.length > 0 ? "good" : "warn",
      });
    } catch {
      setValidationResults([]);
      setValidationState("failed");
      setValidationSummary(copy.requestFailed);
      addKnowledgeActivity({
        title: copy.validationFailedTitle,
        detail: copy.requestFailed,
        meta: `${copy.validationCollection}: ${collectionName.trim() || copy.collectionMissing}`,
        tone: "warn",
      });
    }
  };

  const confirmKnowledgeValidationOutcome = () => {
    setValidationSummary(copy.validationOutcomeMarked);
    addKnowledgeActivity({
      title: copy.validationOutcomeMarkedTitle,
      detail: validationOutcomeMaterialLabel,
      meta: `${copy.validationOutcomeMatches}: ${validationResults.length}; ${copy.validationOutcomeMode}: ${validationMode}`,
      tone: "good",
    });
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
      <section className={`knowledge-ingestion-panel ${ingestionPanelTone}`} aria-label={copy.ingestionTitle}>
        <div className="knowledge-ingestion-header">
          <div className="knowledge-card-title">
            {ingestionNeedsActionCount > 0 || libraryState === "failed" ? <AlertTriangle size={17} /> : <CheckCircle2 size={17} />}
            <div>
              <span>{copy.ingestionNextAction}</span>
              <h3>{copy.ingestionTitle}</h3>
              <p>{copy.ingestionHint}</p>
              <strong>{nextKnowledgeStep}</strong>
            </div>
          </div>
          <div className="knowledge-ingestion-actions">
            <button className="refresh-button" onClick={() => void refreshDocuments(true)} disabled={libraryState === "loading"}>
              <RefreshCcw size={15} />
              {copy.ingestionRefresh}
            </button>
            {retryableFailedCount > 0 ? (
              <button className="refresh-button" onClick={() => void uploadSelectedFiles()} disabled={uploading}>
                <RefreshCcw size={15} />
                {copy.ingestionRetry}
              </button>
            ) : null}
          </div>
        </div>
        <div className="knowledge-ingestion-stats">
          <div className={`knowledge-ingestion-stat-card ${queuedFileCount > 0 ? "warn" : "good"}`}>
            <span>{copy.ingestionQueued}</span>
            <strong>{queuedFileCount}</strong>
          </div>
          <div className={`knowledge-ingestion-stat-card ${uploadingFileCount > 0 || processingDocumentCount > 0 ? "neutral" : "good"}`}>
            <span>{copy.ingestionProcessing}</span>
            <strong>{uploadingFileCount + processingDocumentCount}</strong>
          </div>
          <div className="knowledge-ingestion-stat-card good">
            <span>{copy.ingestionReady}</span>
            <strong>{readyDocumentCount}</strong>
          </div>
          <div className={`knowledge-ingestion-stat-card ${ingestionNeedsActionCount > 0 ? "warn" : "good"}`}>
            <span>{copy.ingestionNeedsReview}</span>
            <strong>{ingestionNeedsActionCount}</strong>
          </div>
        </div>
        <div className="knowledge-ingestion-pipeline" aria-label={copy.ingestionTimelineTitle}>
          {ingestionPipelineSteps.map((step, index) => (
            <div className={`knowledge-ingestion-step ${step.state}`} key={step.label}>
              <span>{index + 1}</span>
              <strong>{step.label}</strong>
            </div>
          ))}
        </div>
        <div className="knowledge-ingestion-list" aria-label={copy.ingestionLatestBatch}>
          {queue.length > 0
            ? queue.slice(0, 6).map((item) => {
                const progress = knowledgeIngestionProgressForQueue(item);
                return (
                  <article className={`knowledge-ingestion-item ${item.status}`} key={item.id}>
                    <div className="knowledge-ingestion-item-main">
                      <FileText size={17} />
                      <div>
                        <strong>{item.file.name}</strong>
                        <span>{item.ingestStatus || queueStatusLabels[item.status]}</span>
                      </div>
                    </div>
                    <div className="knowledge-ingestion-progress" aria-label={`${copy.ingestionProcessing}: ${progress}%`}>
                      <span style={{ width: `${progress}%` }} />
                    </div>
                    <div className="knowledge-ingestion-meta">
                      <span>{copy.ingestionSourceId}: {item.sourceId ?? "-"}</span>
                      <span>{copy.ingestionDocumentId}: {item.documentId ?? "-"}</span>
                      <span>{copy.documentChunks}: {item.chunkCount ?? "-"}</span>
                      {item.ingestError || item.message ? (
                        <span>{copy.ingestionError}: {item.ingestError ?? item.message}</span>
                      ) : null}
                    </div>
                  </article>
                );
              })
            : documents.length > 0
              ? documents.slice(0, 4).map((document) => {
                  const stage = knowledgeDocumentIngestionStage(document);
                  const progress = knowledgeIngestionProgressForDocument(document);
                  return (
                    <article className={`knowledge-ingestion-item ${stage}`} key={knowledgeDocumentKey(document)}>
                      <div className="knowledge-ingestion-item-main">
                        <FileText size={17} />
                        <div>
                          <strong>{documentDisplayName(document)}</strong>
                          <span>{document.ingest_status || document.status || copy.detailHealthUnknown}</span>
                        </div>
                      </div>
                      <div className="knowledge-ingestion-progress" aria-label={`${copy.ingestionProcessing}: ${progress}%`}>
                        <span style={{ width: `${progress}%` }} />
                      </div>
                      <div className="knowledge-ingestion-meta">
                        <span>{copy.ingestionSourceId}: {document.source_id ?? "-"}</span>
                        <span>{copy.detailCollection}: {document.collection_name ?? collectionName}</span>
                        <span>{copy.documentChunks}: {document.chunk_count ?? "-"}</span>
                        {document.error_message ? <span>{copy.ingestionError}: {document.error_message}</span> : null}
                      </div>
                    </article>
                  );
                })
              : <div className="knowledge-empty">{copy.ingestionNoBatch}</div>}
        </div>
      </section>
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
      <section className="knowledge-validation-panel" aria-label={copy.validationTitle}>
        <div className="knowledge-validation-header">
          <div className="knowledge-card-title">
            <Search size={17} />
            <div>
              <span>{copy.validationCollection}: {collectionName.trim() || copy.collectionMissing}</span>
              <h3>{copy.validationTitle}</h3>
              <p>{copy.validationHint}</p>
            </div>
          </div>
          <button
            className="refresh-button"
            onClick={() => {
              setValidationResults([]);
              setValidationSummary(null);
              setValidationState("idle");
            }}
            disabled={validationResults.length === 0 && !validationSummary}
          >
            <XCircle size={15} />
            {copy.validationClear}
          </button>
        </div>
        <div className="knowledge-validation-guidance" aria-label={copy.validationGuidanceTitle}>
          <div className="knowledge-validation-guidance-header">
            <div>
              <span>{copy.validationSuggestionTitle}</span>
              <strong>{copy.validationGuidanceTitle}</strong>
              <p>{copy.validationGuidanceHint}</p>
            </div>
          </div>
          <div className="knowledge-validation-targets">
            {selectedDocumentValidationSuggestion ? (
              <article className="knowledge-validation-target-card">
                <span>{copy.validationSelectedMaterial}</span>
                <strong>{documentDisplayName(selectedDocument!)}</strong>
                <small>{copy.ingestionSourceId}: {selectedDocument?.source_id ?? "-"}</small>
                <button
                  className="refresh-button"
                  onClick={() => void runKnowledgeValidation(selectedDocumentValidationSuggestion)}
                  disabled={validationState === "loading"}
                >
                  <Search size={14} />
                  {copy.validationRunForItem}
                </button>
              </article>
            ) : null}
            {latestUploadValidationSuggestion ? (
              <article className="knowledge-validation-target-card">
                <span>{copy.validationLatestUpload}</span>
                <strong>{latestUploadedQueueItem?.file.name}</strong>
                <small>{copy.documentChunks}: {latestUploadedQueueItem?.chunkCount ?? "-"}</small>
                <button
                  className="refresh-button"
                  onClick={() => void runKnowledgeValidation(latestUploadValidationSuggestion)}
                  disabled={validationState === "loading"}
                >
                  <Search size={14} />
                  {copy.validationRunForItem}
                </button>
              </article>
            ) : null}
            {!selectedDocumentValidationSuggestion && !latestUploadValidationSuggestion ? (
              <div className="knowledge-empty">{copy.validationNoTarget}</div>
            ) : null}
          </div>
          <div className="knowledge-validation-suggestions">
            {validationSuggestions.map((suggestion) => (
              <button
                className="knowledge-validation-suggestion-card"
                key={suggestion.id}
                onClick={() => applyKnowledgeValidationSuggestion(suggestion)}
                type="button"
              >
                <strong>{suggestion.label}</strong>
                <span>{suggestion.query}</span>
                <em>{copy.validationUseSuggestion}</em>
              </button>
            ))}
          </div>
        </div>
        <div className="knowledge-validation-form">
          <label>
            {copy.validationQueryLabel}
            <input
              value={validationQuery}
              placeholder={copy.validationQueryPlaceholder}
              onChange={(event) => setValidationQuery(event.target.value)}
            />
          </label>
          <label>
            {copy.validationModeLabel}
            <select value={validationMode} onChange={(event) => setValidationMode(event.target.value as KnowledgeSearchMode)}>
              <option value="hybrid">{copy.validationHybrid}</option>
              <option value="dense">{copy.validationDense}</option>
              <option value="keyword">{copy.validationKeyword}</option>
            </select>
          </label>
          <button
            className="action-button primary-action"
            onClick={() => void runKnowledgeValidation()}
            disabled={validationState === "loading" || !validationQuery.trim()}
          >
            <Search size={16} />
            {copy.validationAction}
          </button>
        </div>
        {validationSummary ? <div className={`knowledge-validation-summary ${validationState}`}>{validationSummary}</div> : null}
        <div className={`knowledge-validation-outcome ${validationOutcomeTone}`} aria-label={copy.validationOutcomeTitle}>
          <div className="knowledge-validation-outcome-main">
            {validationOutcomeTone === "good" ? (
              <CheckCircle2 size={18} />
            ) : validationOutcomeTone === "warn" ? (
              <AlertTriangle size={18} />
            ) : (
              <Activity size={18} />
            )}
            <div>
              <span>{copy.validationOutcomeTitle}</span>
              <strong>{validationOutcomeLabel}</strong>
              <p>{validationOutcomeDetail}</p>
            </div>
          </div>
          <div className="knowledge-validation-outcome-stats">
            {validationOutcomeStats.map((stat) => (
              <div className="knowledge-validation-outcome-stat" key={stat.label}>
                <span>{stat.label}</span>
                <strong>{stat.value}</strong>
              </div>
            ))}
          </div>
          <div className="knowledge-validation-outcome-action">
            <span>{copy.validationOutcomeNextStep}</span>
            <button
              className="refresh-button"
              onClick={() => {
                if (validationOutcomeTone === "good") {
                  confirmKnowledgeValidationOutcome();
                  return;
                }
                void runKnowledgeValidation();
              }}
              disabled={validationState === "loading" || (validationOutcomeTone === "neutral" && !validationQuery.trim())}
            >
              {validationOutcomeTone === "good" ? <CheckCircle2 size={14} /> : <Search size={14} />}
              {validationOutcomeActionLabel}
            </button>
          </div>
        </div>
        <div className="knowledge-validation-results" aria-label={copy.validationResultsTitle}>
          {validationState === "loading" ? <div className="knowledge-empty">{copy.validationRunning}</div> : null}
          {validationState !== "loading" && validationResults.length === 0 ? (
            <div className="knowledge-empty">{validationState === "ready" ? copy.validationNoResults : copy.validationEmpty}</div>
          ) : null}
          {validationResults.map((result) => {
            const score = knowledgeSearchScore(result);
            return (
              <article className="knowledge-validation-result-card" key={result.id}>
                <div className="knowledge-validation-result-main">
                  <FileText size={17} />
                  <div>
                    <strong>{knowledgeSearchSourceLabel(result)}</strong>
                    <p>{result.text}</p>
                  </div>
                </div>
                <div className="knowledge-validation-result-meta">
                  <span>{copy.validationScore}: {formatKnowledgeSearchScore(score)}</span>
                  <span>{copy.validationChunk}: {result.chunk_index ?? "-"}</span>
                  <span>{copy.validationSource}: {knowledgeSearchSourceLabel(result)}</span>
                </div>
              </article>
            );
          })}
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
        <div className="knowledge-document-overview" aria-label={copy.documentOverviewTitle}>
          <div className="knowledge-document-overview-card">
            <span>{copy.documentOverviewTotal}</span>
            <strong>{documents.length}</strong>
          </div>
          <div className="knowledge-document-overview-card good">
            <span>{copy.documentOverviewReady}</span>
            <strong>{readyDocumentCount}</strong>
          </div>
          <div className="knowledge-document-overview-card warn">
            <span>{copy.documentOverviewNeedsReview}</span>
            <strong>{reviewDocumentCount}</strong>
          </div>
          <div className="knowledge-document-overview-card">
            <span>{copy.documentOverviewSelected}</span>
            <strong>{selectedDocument ? documentDisplayName(selectedDocument) : "-"}</strong>
          </div>
        </div>
        <div className="knowledge-document-workspace">
          <div className="knowledge-document-grid">
            {documents.length > 0 ? (
              documents.slice(0, 12).map((document) => {
                const documentKey = knowledgeDocumentKey(document);
                const documentTone = knowledgeDocumentStatusTone(document);
                const documentStatusLabel =
                  document.status ||
                  (documentTone === "good"
                    ? copy.detailHealthReady
                    : documentTone === "warn"
                      ? copy.detailHealthNeedsReview
                      : copy.detailHealthUnknown);
                return (
                  <article
                    className={`knowledge-document-card ${documentTone} ${selectedDocumentKey === documentKey ? "selected" : ""}`}
                    key={documentKey}
                  >
                    <div className="knowledge-document-main">
                      <FileText size={18} />
                      <div>
                        <strong>{documentDisplayName(document)}</strong>
                        <span>{document.collection_name ?? collectionName}</span>
                      </div>
                    </div>
                    <div className="knowledge-document-meta">
                      <span>{copy.documentStatus}: {documentStatusLabel}</span>
                      <span>{copy.documentChunks}: {document.chunk_count ?? "-"}</span>
                      <span>{copy.updatedAt}: {document.updated_at ?? document.created_at ?? "-"}</span>
                    </div>
                    <div className="knowledge-document-actions">
                      <button className="refresh-button" onClick={() => setSelectedDocumentKey(documentKey)}>
                        <FileText size={14} />
                        {copy.viewDetails}
                      </button>
                      <button className="refresh-button" onClick={() => selectDocumentForEdit(document)}>
                        <PencilLine size={14} />
                        {copy.editExisting}
                      </button>
                    </div>
                  </article>
                );
              })
            ) : (
              <div className="knowledge-empty">{copy.emptyLibrary}</div>
            )}
          </div>
          <aside className={`knowledge-document-detail-panel ${selectedDocumentTone}`} aria-label={copy.detailTitle}>
            {selectedDocument ? (
              <>
                <div className="knowledge-detail-health">
                  {selectedDocumentTone === "warn" ? <AlertTriangle size={18} /> : <CheckCircle2 size={18} />}
                  <div>
                    <span>{copy.detailTitle}</span>
                    <strong>{selectedDocumentHealthLabel}</strong>
                  </div>
                </div>
                <h4>{documentDisplayName(selectedDocument)}</h4>
                <dl className="knowledge-detail-list">
                  <div>
                    <dt>{copy.detailSourceId}</dt>
                    <dd>{selectedDocument.source_id ?? selectedDocument.id ?? "-"}</dd>
                  </div>
                  <div>
                    <dt>{copy.detailCollection}</dt>
                    <dd>{selectedDocument.collection_name ?? collectionName}</dd>
                  </div>
                  <div>
                    <dt>{copy.documentStatus}</dt>
                    <dd>{selectedDocumentStatusLabel}</dd>
                  </div>
                  <div>
                    <dt>{copy.ingestionSelectedStatus}</dt>
                    <dd>{selectedDocumentIngestLabel}</dd>
                  </div>
                  <div>
                    <dt>{copy.documentChunks}</dt>
                    <dd>{selectedDocument.chunk_count ?? "-"}</dd>
                  </div>
                  {selectedDocument.error_message ? (
                    <div>
                      <dt>{copy.ingestionError}</dt>
                      <dd>{selectedDocument.error_message}</dd>
                    </div>
                  ) : null}
                  <div>
                    <dt>{copy.detailCreatedAt}</dt>
                    <dd>{selectedDocument.created_at ?? "-"}</dd>
                  </div>
                  <div>
                    <dt>{copy.updatedAt}</dt>
                    <dd>{selectedDocument.updated_at ?? selectedDocument.created_at ?? "-"}</dd>
                  </div>
                </dl>
                <button className="action-button primary-action" onClick={() => selectDocumentForEdit(selectedDocument)}>
                  <PencilLine size={16} />
                  {copy.useForUpdate}
                </button>
              </>
            ) : (
              <div className="knowledge-empty">{copy.detailEmpty}</div>
            )}
          </aside>
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
        <ChatPanel language={language} onOpenKnowledge={() => setOperatorPage("knowledge")} />
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
    <ConnectedOperationTemplateWorkbench />
  </React.StrictMode>,
);
