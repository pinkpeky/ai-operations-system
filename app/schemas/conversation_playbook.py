"""Conversation Playbook API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.conversation import ConversationPlaybook, ConversationPlaybookRun


PlaybookStatusLiteral = Literal["active", "disabled", "archived"]
PlaybookRunStatusLiteral = Literal["pending", "running", "waiting_approval", "completed", "failed", "cancelled"]


class ConversationPlaybookCreateRequest(BaseModel):
    """Create a custom playbook."""

    name: str = Field(min_length=1, max_length=128)
    description: str | None = None
    category: str | None = None
    status: PlaybookStatusLiteral = "active"
    risk_level: Literal["low", "medium", "high"] = "low"
    steps: list[dict[str, Any]] = Field(default_factory=list)
    default_inputs: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationPlaybookUpdateRequest(BaseModel):
    """Patch a playbook."""

    name: str | None = None
    description: str | None = None
    category: str | None = None
    status: PlaybookStatusLiteral | None = None
    risk_level: Literal["low", "medium", "high"] | None = None
    steps: list[dict[str, Any]] | None = None
    default_inputs: dict[str, Any] | None = None
    metadata: dict[str, Any] | None = None


class ConversationPlaybookRunRequest(BaseModel):
    """Run a playbook."""

    input: dict[str, Any] = Field(default_factory=dict)
    thread_id: UUID | None = None
    mode: Literal["auto_safe", "review_first", "execute_after_approval"] = "auto_safe"


class ConversationPlaybookResponse(BaseModel):
    """Playbook response."""

    id: UUID
    workspace_id: str
    name: str
    description: str | None
    category: str | None
    status: str
    risk_level: str
    steps: list[dict[str, Any]]
    default_inputs: dict[str, Any]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, playbook: ConversationPlaybook) -> "ConversationPlaybookResponse":
        return cls(
            id=playbook.id,
            workspace_id=playbook.workspace_id,
            name=playbook.name,
            description=playbook.description,
            category=playbook.category,
            status=playbook.status,
            risk_level=playbook.risk_level,
            steps=playbook.steps,
            default_inputs=playbook.default_inputs,
            metadata=playbook.playbook_metadata,
            created_at=playbook.created_at,
            updated_at=playbook.updated_at,
        )


class ConversationPlaybookListResponse(BaseModel):
    """Playbook list response."""

    items: list[ConversationPlaybookResponse]


class ConversationPlaybookRunResponse(BaseModel):
    """Playbook run response."""

    id: UUID
    workspace_id: str
    playbook_id: UUID
    thread_id: UUID
    status: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    current_step: int
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, run: ConversationPlaybookRun) -> "ConversationPlaybookRunResponse":
        return cls(
            id=run.id,
            workspace_id=run.workspace_id,
            playbook_id=run.playbook_id,
            thread_id=run.thread_id,
            status=run.status,
            input_payload=run.input_payload,
            output_payload=run.output_payload,
            current_step=run.current_step,
            error=run.error,
            started_at=run.started_at,
            completed_at=run.completed_at,
            created_at=run.created_at,
            updated_at=run.updated_at,
        )


class ConversationPlaybookRunListResponse(BaseModel):
    """Playbook run list response."""

    items: list[ConversationPlaybookRunResponse]
