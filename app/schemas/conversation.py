"""Conversation Runtime API 数据模型。"""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.conversation import ConversationApproval, ConversationEvent, ConversationThread
from app.models.memory import ConversationMessage


ConversationRoleLiteral = Literal["user", "assistant", "system", "tool", "event"]
ConversationRunModeLiteral = Literal["auto_safe", "review_first", "execute_after_approval"]
ConversationExecutionModeLiteral = Literal["immediate", "background", "scheduled"]


class ConversationThreadCreateRequest(BaseModel):
    """创建对话线程请求。"""

    title: str = Field(min_length=1, max_length=255, description="对话标题")
    metadata: dict[str, Any] = Field(default_factory=dict, description="线程元数据")


class ConversationThreadResponse(BaseModel):
    """对话线程响应。"""

    id: UUID
    workspace_id: str
    user_id: str | None
    title: str
    status: str
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, thread: ConversationThread) -> "ConversationThreadResponse":
        """从 ORM 模型构造响应。"""

        return cls(
            id=thread.id,
            workspace_id=thread.workspace_id,
            user_id=thread.user_id,
            title=thread.title,
            status=thread.status,
            metadata=thread.thread_metadata,
            created_at=thread.created_at,
            updated_at=thread.updated_at,
        )


class ConversationThreadListResponse(BaseModel):
    """对话线程列表响应。"""

    items: list[ConversationThreadResponse]


class ConversationMessageCreateRequest(BaseModel):
    """追加对话消息请求。"""

    role: ConversationRoleLiteral = Field(default="user", description="消息角色")
    content: str = Field(min_length=1, description="消息内容")
    metadata: dict[str, Any] = Field(default_factory=dict, description="消息元数据")


class ConversationMessageResponse(BaseModel):
    """对话消息响应。"""

    id: UUID
    workspace_id: str
    thread_id: UUID | None
    role: str
    content: str
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, message: ConversationMessage) -> "ConversationMessageResponse":
        """从 ORM 模型构造响应。"""

        return cls(
            id=message.id,
            workspace_id=message.workspace_id,
            thread_id=message.thread_id,
            role=message.role,
            content=message.content,
            metadata=message.message_metadata,
            created_at=message.created_at,
        )


class ConversationMessageListResponse(BaseModel):
    """对话消息列表响应。"""

    thread_id: UUID
    items: list[ConversationMessageResponse]


class ConversationEventResponse(BaseModel):
    """对话事件响应。"""

    id: UUID
    workspace_id: str
    thread_id: UUID
    event_type: str
    message: str | None
    payload: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, event: ConversationEvent) -> "ConversationEventResponse":
        """从 ORM 模型构造响应。"""

        return cls(
            id=event.id,
            workspace_id=event.workspace_id,
            thread_id=event.thread_id,
            event_type=event.event_type,
            message=event.message,
            payload=event.payload,
            created_at=event.created_at,
        )


class ConversationEventListResponse(BaseModel):
    """对话事件列表响应。"""

    thread_id: UUID
    items: list[ConversationEventResponse]


class ConversationRunRequest(BaseModel):
    """执行一轮对话请求。"""

    input: dict[str, Any] = Field(default_factory=dict, description="运行输入，通常包含 message")
    playbook_name: str | None = Field(default=None, description="Optional playbook name to run before rule-based routing")
    mode: ConversationRunModeLiteral = Field(
        default="auto_safe",
        description="auto_safe / review_first / execute_after_approval",
    )
    execution_mode: ConversationExecutionModeLiteral = Field(
        default="immediate",
        description="immediate / background / scheduled",
    )
    scheduled_at: datetime | None = Field(default=None, description="Required for scheduled background execution")


class ConversationRunResponse(BaseModel):
    """执行一轮对话响应。"""

    thread_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID
    assistant_message: ConversationMessageResponse
    route: str
    route_name: str
    selected_tool: str | None = None
    events: list[ConversationEventResponse]
    events_created: int = 0
    success: bool = True
    summary: str = ""
    result_metadata: dict[str, Any] = Field(default_factory=dict)
    output: dict[str, Any]
    approval_required: bool = False
    approval_id: UUID | None = None
    approval_status: str | None = None
    risk_level: str | None = None
    proposed_action: str | None = None
    playbook_run_id: UUID | None = None
    playbook_name: str | None = None
    playbook_status: str | None = None
    task_run_id: UUID | None = None
    task_status: str | None = None
    workflow_run_id: UUID | None = None
    workflow_step_id: UUID | None = None
    checkpoint_id: UUID | None = None
    memory_snapshot_id: UUID | None = None
    execution_mode: str = "immediate"
    websocket_placeholder: bool = True
    sse_placeholder: bool = True


class ConversationApprovalResponse(BaseModel):
    """Conversation execution approval response."""

    id: UUID
    workspace_id: str
    thread_id: UUID
    message_id: UUID | None
    route_name: str
    selected_tool: str | None
    risk_level: str
    approval_status: str
    proposed_action: str
    proposed_payload: dict[str, Any]
    reviewer_notes: str | None
    approved_by: str | None
    approved_at: datetime | None
    rejected_at: datetime | None
    cancelled_at: datetime | None
    expires_at: datetime | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, approval: ConversationApproval) -> "ConversationApprovalResponse":
        """Build an API response from an ORM approval."""

        return cls(
            id=approval.id,
            workspace_id=approval.workspace_id,
            thread_id=approval.thread_id,
            message_id=approval.message_id,
            route_name=approval.route_name,
            selected_tool=approval.selected_tool,
            risk_level=approval.risk_level,
            approval_status=approval.approval_status,
            proposed_action=approval.proposed_action,
            proposed_payload=approval.proposed_payload,
            reviewer_notes=approval.reviewer_notes,
            approved_by=approval.approved_by,
            approved_at=approval.approved_at,
            rejected_at=approval.rejected_at,
            cancelled_at=approval.cancelled_at,
            expires_at=approval.expires_at,
            metadata=approval.approval_metadata,
            created_at=approval.created_at,
            updated_at=approval.updated_at,
        )


class ConversationApprovalListResponse(BaseModel):
    """Conversation approval list response."""

    thread_id: UUID | None = None
    items: list[ConversationApprovalResponse]


class ConversationApprovalDecisionRequest(BaseModel):
    """Approve/reject/cancel request."""

    reviewer_notes: str | None = Field(default=None, description="Human reviewer notes")


class ConversationApprovalExecuteRequest(BaseModel):
    """Execute an approved conversation action."""

    input: dict[str, Any] = Field(default_factory=dict, description="Execution input, usually approval_id")
