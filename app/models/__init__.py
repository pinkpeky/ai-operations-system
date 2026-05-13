"""ORM 模型聚合模块。

Alembic 和测试可以从这里一次性导入所有模型，确保 metadata 完整注册。
"""

from app.models.account import Account
from app.models.api_key import APIKey
from app.models.browser import (
    BrowserAction,
    BrowserActionLog,
    BrowserHumanControlEvent,
    BrowserHumanControlSession,
    BrowserProfile,
    BrowserProfileUsageLog,
    BrowserSecurityAuditLog,
    BrowserSession,
    BrowserUIAccessSession,
)
from app.models.browser_worker import BrowserWorker, BrowserWorkerAction, BrowserWorkerSession
from app.models.collection_metadata import CollectionMetadata
from app.models.document import Document, DocumentChunk
from app.models.enums import (
    AccountStatus,
    AgentMemoryType,
    AgentHandoffStatus,
    AgentRunStatus,
    APIKeyStatus,
    BrowserActionStatus,
    BrowserHumanControlEventType,
    BrowserHumanControlStatus,
    BrowserProfileHealthStatus,
    BrowserProfileStatus,
    BrowserSessionStatus,
    BrowserUIAccessStatus,
    BrowserWorkerActionStatus,
    BrowserWorkerAuthStatus,
    BrowserWorkerSessionStatus,
    BrowserWorkerStatus,
    CollectionMetadataStatus,
    ConversationRole,
    ConversationSessionStatus,
    DocumentIngestStatus,
    DocumentStatus,
    PublishLogStatus,
    PlanStatus,
    PlanStepStatus,
    TaskStatus,
    UserStatus,
    WorkspaceMemberRole,
    WorkspaceMemberStatus,
    WorkspaceStatus,
)
from app.models.memory import AgentMemory, ConversationMessage, ConversationSession, MemoryOperationLog
from app.models.multi_agent import AgentHandoff, AgentMessage, AgentRun
from app.models.openclaw import OpenClawActionLog
from app.models.planning import Plan, PlanReview, PlanStep
from app.models.publish_log import PublishLog
from app.models.rag_eval import RAGEvalItem, RAGEvalRun
from app.models.task import Task
from app.models.task_observability import TaskEvent, TaskLog
from app.models.tool_call import ToolCallLog
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember

__all__ = [
    "Account",
    "AccountStatus",
    "AgentMemory",
    "AgentMemoryType",
    "AgentHandoff",
    "AgentHandoffStatus",
    "AgentMessage",
    "AgentRun",
    "AgentRunStatus",
    "APIKey",
    "APIKeyStatus",
    "BrowserAction",
    "BrowserActionLog",
    "BrowserActionStatus",
    "BrowserHumanControlEvent",
    "BrowserHumanControlEventType",
    "BrowserHumanControlSession",
    "BrowserHumanControlStatus",
    "BrowserProfile",
    "BrowserProfileHealthStatus",
    "BrowserProfileStatus",
    "BrowserProfileUsageLog",
    "BrowserSecurityAuditLog",
    "BrowserSession",
    "BrowserSessionStatus",
    "BrowserUIAccessSession",
    "BrowserUIAccessStatus",
    "BrowserWorker",
    "BrowserWorkerAction",
    "BrowserWorkerActionStatus",
    "BrowserWorkerAuthStatus",
    "BrowserWorkerSession",
    "BrowserWorkerSessionStatus",
    "BrowserWorkerStatus",
    "CollectionMetadata",
    "CollectionMetadataStatus",
    "ConversationMessage",
    "ConversationRole",
    "ConversationSession",
    "ConversationSessionStatus",
    "Document",
    "DocumentChunk",
    "DocumentIngestStatus",
    "DocumentStatus",
    "MemoryOperationLog",
    "OpenClawActionLog",
    "Plan",
    "PlanReview",
    "PlanStatus",
    "PlanStep",
    "PlanStepStatus",
    "PublishLog",
    "PublishLogStatus",
    "RAGEvalItem",
    "RAGEvalRun",
    "Task",
    "TaskEvent",
    "TaskLog",
    "TaskStatus",
    "ToolCallLog",
    "User",
    "UserStatus",
    "Workspace",
    "WorkspaceMember",
    "WorkspaceMemberRole",
    "WorkspaceMemberStatus",
    "WorkspaceStatus",
]
