"""业务状态枚举模块。

集中定义系统中跨模块共享的状态值，避免魔法字符串散落在业务代码中。
"""

from enum import StrEnum


class AccountStatus(StrEnum):
    """账号状态。"""

    ACTIVE = "active"
    DISABLED = "disabled"


class TaskStatus(StrEnum):
    """中央任务调度状态。"""

    PENDING = "pending"
    RUNNING = "running"
    RETRY = "retry"
    FAILED = "failed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class PublishLogStatus(StrEnum):
    """发布日志状态。"""

    PENDING = "pending"
    RUNNING = "running"
    FAILED = "failed"
    COMPLETED = "completed"


class DocumentStatus(StrEnum):
    """知识库文档生命周期状态。"""

    ACTIVE = "active"
    DELETED = "deleted"
    OUTDATED = "outdated"


class DocumentIngestStatus(StrEnum):
    """知识库文档写入状态。"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class CollectionMetadataStatus(StrEnum):
    """Collection 元数据状态。"""

    ACTIVE = "active"
    DELETED = "deleted"


class UserStatus(StrEnum):
    """用户状态。"""

    ACTIVE = "active"
    DISABLED = "disabled"


class WorkspaceStatus(StrEnum):
    """工作区状态。"""

    ACTIVE = "active"
    DISABLED = "disabled"


class WorkspaceMemberRole(StrEnum):
    """工作区成员角色。"""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"


class WorkspaceMemberStatus(StrEnum):
    """工作区成员状态。"""

    ACTIVE = "active"
    DISABLED = "disabled"


class APIKeyStatus(StrEnum):
    """API Key 状态。"""

    ACTIVE = "active"
    REVOKED = "revoked"


class ConversationSessionStatus(StrEnum):
    """会话生命周期状态。"""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ConversationRole(StrEnum):
    """会话消息角色。"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    EVENT = "event"


class ConversationThreadStatus(StrEnum):
    """Conversation Runtime thread lifecycle status."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class ConversationApprovalStatus(StrEnum):
    """Conversation approval lifecycle status."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    EXECUTED = "executed"


class ConversationApprovalRiskLevel(StrEnum):
    """Conversation approval risk level."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ConversationRunMode(StrEnum):
    """Conversation execution review mode."""

    AUTO_SAFE = "auto_safe"
    REVIEW_FIRST = "review_first"
    EXECUTE_AFTER_APPROVAL = "execute_after_approval"


class ConversationPlaybookStatus(StrEnum):
    """Conversation playbook lifecycle status."""

    ACTIVE = "active"
    DISABLED = "disabled"
    ARCHIVED = "archived"


class ConversationPlaybookRunStatus(StrEnum):
    """Conversation playbook run lifecycle status."""

    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class OutputArtifactStatus(StrEnum):
    """Output artifact lifecycle status."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"


class OutputArtifactSourceType(StrEnum):
    """Source system that produced an output artifact."""

    CONVERSATION = "conversation"
    PLAYBOOK = "playbook"
    TOOL = "tool"
    BROWSER_RUNTIME = "browser_runtime"
    RAG = "rag"
    CONTENT_AGENT = "content_agent"
    PLANNING = "planning"
    OPENCLAW_MOCK = "openclaw_mock"


class OutputArtifactType(StrEnum):
    """Reusable artifact type."""

    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    SCREENSHOT = "screenshot"
    HTML_SNAPSHOT = "html_snapshot"
    REPORT = "report"
    PLAN = "plan"
    RAG_ANSWER = "rag_answer"
    CONTENT_DRAFT = "content_draft"
    BUNDLE = "bundle"
    DEBUG = "debug"
    REPLAY = "replay"
    DATASET = "dataset"


class OutputArtifactRole(StrEnum):
    """Role an artifact plays in an output pipeline."""

    SCREENSHOT = "screenshot"
    REPORT = "report"
    TRANSCRIPT = "transcript"
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    BUNDLE = "bundle"
    DEBUG = "debug"
    REPLAY = "replay"
    DATASET = "dataset"


class OutputArtifactStage(StrEnum):
    """Output artifact pipeline stage."""

    RAW = "raw"
    PROCESSED = "processed"
    PACKAGED = "packaged"
    EXPORTED = "exported"
    ARCHIVED = "archived"


class OutputArtifactRetentionPolicy(StrEnum):
    """Output artifact retention policy."""

    TEMPORARY = "temporary"
    STANDARD = "standard"
    PERSISTENT = "persistent"
    COMPLIANCE_HOLD = "compliance_hold"


class WorkflowRunStatus(StrEnum):
    """Workflow run lifecycle status."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class WorkflowStepStatus(StrEnum):
    """Workflow step lifecycle status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WAITING_APPROVAL = "waiting_approval"


class WorkflowCheckpointType(StrEnum):
    """Workflow checkpoint type."""

    AUTO = "auto"
    MANUAL = "manual"
    APPROVAL = "approval"
    FAILURE = "failure"
    RESUME = "resume"


class AgentMemorySnapshotType(StrEnum):
    """Agent memory snapshot type."""

    CONVERSATION_SUMMARY = "conversation_summary"
    TASK_CONTEXT = "task_context"
    TOOL_RESULT = "tool_result"
    DECISION = "decision"
    APPROVAL_CONTEXT = "approval_context"
    ARTIFACT_SUMMARY = "artifact_summary"


class WorkflowGraphEdgeType(StrEnum):
    """Workflow graph edge routing type."""

    SUCCESS = "success"
    FAILURE = "failure"
    CONDITIONAL = "conditional"
    RETRY = "retry"
    FALLBACK = "fallback"
    ALWAYS = "always"


class WorkflowNodeType(StrEnum):
    """Supported workflow graph node type."""

    PLAYBOOK_STEP = "playbook_step"
    APPROVAL_GATE = "approval_gate"
    TOOL_CALL = "tool_call"
    ARTIFACT_TRANSFORM = "artifact_transform"
    CONDITIONAL_ROUTER = "conditional_router"
    DELAY = "delay"
    RETRY = "retry"
    WORKFLOW_CHECKPOINT = "workflow_checkpoint"
    MEMORY_SNAPSHOT = "memory_snapshot"
    NO_OP = "no_op"


class WorkflowNodeExecutionMode(StrEnum):
    """Workflow graph node execution mode."""

    SYNC = "sync"
    ASYNC = "async"
    BACKGROUND = "background"


class WorkflowReplayStatus(StrEnum):
    """Workflow replay metadata lifecycle."""

    CREATED = "created"
    PLANNED = "planned"
    FAILED = "failed"


class TaskRunStatus(StrEnum):
    """Task orchestration run lifecycle status."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class TaskRunPriority(StrEnum):
    """Task orchestration priority."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class TaskSchedulerStatus(StrEnum):
    """In-process task scheduler health status."""

    ACTIVE = "active"
    PAUSED = "paused"
    DEGRADED = "degraded"
    STOPPED = "stopped"


class AgentMemoryType(StrEnum):
    """Agent Memory 类型。"""

    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    TASK_MEMORY = "task_memory"
    RETRIEVAL_MEMORY = "retrieval_memory"


class AgentRunStatus(StrEnum):
    """Multi-Agent run 状态。"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentHandoffStatus(StrEnum):
    """Agent handoff 状态。"""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class PlanStatus(StrEnum):
    """Plan 生命周期状态。"""

    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PlanStepStatus(StrEnum):
    """Plan step 执行状态。"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class BrowserSessionStatus(StrEnum):
    """Browser session lifecycle status."""

    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    FAILED = "failed"


class BrowserProfileStatus(StrEnum):
    """Browser profile lifecycle status."""

    AVAILABLE = "available"
    LOCKED = "locked"
    DISABLED = "disabled"
    CORRUPTED = "corrupted"
    DELETED = "deleted"


class BrowserProfileHealthStatus(StrEnum):
    """Browser profile health status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CORRUPTED = "corrupted"
    STALE = "stale"
    DELETED = "deleted"


class BrowserActionStatus(StrEnum):
    """Browser action execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BrowserWorkerStatus(StrEnum):
    """Remote browser worker status."""

    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"


class BrowserWorkerAuthStatus(StrEnum):
    """Browser worker authentication status."""

    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    REVOKED = "revoked"
    FAILED = "failed"


class BrowserWorkerSessionStatus(StrEnum):
    """Remote browser worker session status."""

    ACTIVE = "active"
    CLOSED = "closed"
    FAILED = "failed"


class BrowserWorkerActionStatus(StrEnum):
    """Remote browser worker action status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BrowserRuntimeSessionStatus(StrEnum):
    """Remote browser runtime session lifecycle status."""

    ACTIVE = "active"
    CLOSED = "closed"
    ERROR = "error"
    STALE = "stale"


class BrowserHumanControlStatus(StrEnum):
    """Human-in-the-loop browser control lifecycle status."""

    REQUESTED = "requested"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    FAILED = "failed"


class BrowserHumanControlEventType(StrEnum):
    """Human control event type."""

    REQUESTED = "requested"
    APPROVED = "approved"
    STARTED = "started"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    TIMEOUT = "timeout"
    NOTE = "note"


class BrowserUIAccessStatus(StrEnum):
    """Browser UI access placeholder session status."""

    REQUESTED = "requested"
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    FAILED = "failed"
