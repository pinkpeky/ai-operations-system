"""Conversation Runtime Repository。"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import ConversationApproval, ConversationEvent, ConversationPlaybook, ConversationPlaybookRun, ConversationThread
from app.models.enums import ConversationPlaybookRunStatus, ConversationPlaybookStatus, ConversationRole, ConversationThreadStatus
from app.models.memory import ConversationMessage


class ConversationRuntimeRepository:
    """对话运行时数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_thread(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        title: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationThread:
        """创建对话线程。"""

        thread = ConversationThread(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            status=ConversationThreadStatus.ACTIVE.value,
            thread_metadata=metadata or {},
        )
        self.session.add(thread)
        await self.session.flush()
        return thread

    async def get_thread(self, *, workspace_id: str, thread_id: UUID) -> ConversationThread | None:
        """按 workspace 查询线程。"""

        statement = select(ConversationThread).where(
            ConversationThread.workspace_id == workspace_id,
            ConversationThread.id == thread_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_threads(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ConversationThread]:
        """列出当前 workspace 线程。"""

        statement = select(ConversationThread).where(ConversationThread.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(ConversationThread.status == status)
        statement = statement.order_by(ConversationThread.updated_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def archive_thread(self, *, thread: ConversationThread) -> ConversationThread:
        """归档线程。"""

        thread.status = ConversationThreadStatus.ARCHIVED.value
        await self.session.flush()
        return thread

    async def append_message(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationMessage:
        """向线程追加消息。

        conversation_messages 已被 Memory 使用，因此这里不写 session_id，只写 thread_id。
        """

        if role not in {item.value for item in ConversationRole}:
            raise ValueError("role must be user, assistant, system, tool, or event")
        message = ConversationMessage(
            session_id=None,
            thread_id=thread_id,
            workspace_id=workspace_id,
            role=role,
            content=content,
            token_count=self._estimate_token_count(content),
            message_metadata=metadata or {},
        )
        self.session.add(message)
        await self.session.flush()
        return message

    async def list_messages(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        limit: int = 100,
    ) -> list[ConversationMessage]:
        """列出线程消息。"""

        statement = (
            select(ConversationMessage)
            .where(
                ConversationMessage.workspace_id == workspace_id,
                ConversationMessage.thread_id == thread_id,
            )
            .order_by(ConversationMessage.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def append_event(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        event_type: str,
        message: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> ConversationEvent:
        """追加线程事件。"""

        event = ConversationEvent(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type=event_type,
            message=message,
            payload=payload or {},
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def list_events(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        limit: int = 200,
    ) -> list[ConversationEvent]:
        """列出线程事件。"""

        statement = (
            select(ConversationEvent)
            .where(
                ConversationEvent.workspace_id == workspace_id,
                ConversationEvent.thread_id == thread_id,
            )
            .order_by(ConversationEvent.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_approval(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        message_id: UUID | None,
        route_name: str,
        selected_tool: str | None,
        risk_level: str,
        proposed_action: str,
        proposed_payload: dict[str, Any],
        metadata: dict[str, Any] | None = None,
        expires_at: datetime | None = None,
    ) -> ConversationApproval:
        """Create a pending approval for a proposed conversation action."""

        approval = ConversationApproval(
            workspace_id=workspace_id,
            thread_id=thread_id,
            message_id=message_id,
            route_name=route_name,
            selected_tool=selected_tool,
            risk_level=risk_level,
            proposed_action=proposed_action,
            proposed_payload=proposed_payload,
            approval_metadata=metadata or {},
            expires_at=expires_at,
        )
        self.session.add(approval)
        await self.session.flush()
        return approval

    async def get_approval(self, *, workspace_id: str, approval_id: UUID) -> ConversationApproval | None:
        """Get one approval in the current workspace."""

        statement = select(ConversationApproval).where(
            ConversationApproval.workspace_id == workspace_id,
            ConversationApproval.id == approval_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_approvals(
        self,
        *,
        workspace_id: str,
        thread_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ConversationApproval]:
        """List approvals scoped by workspace and optional thread/status."""

        statement = select(ConversationApproval).where(ConversationApproval.workspace_id == workspace_id)
        if thread_id is not None:
            statement = statement.where(ConversationApproval.thread_id == thread_id)
        if status is not None:
            statement = statement.where(ConversationApproval.approval_status == status)
        statement = statement.order_by(ConversationApproval.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_playbook(
        self,
        *,
        workspace_id: str,
        name: str,
        description: str | None,
        category: str | None,
        risk_level: str,
        steps: list[dict[str, Any]],
        default_inputs: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        status: str = ConversationPlaybookStatus.ACTIVE.value,
    ) -> ConversationPlaybook:
        """Create one conversation playbook."""

        playbook = ConversationPlaybook(
            workspace_id=workspace_id,
            name=name,
            description=description,
            category=category,
            status=status,
            risk_level=risk_level,
            steps=steps,
            default_inputs=default_inputs or {},
            playbook_metadata=metadata or {},
        )
        self.session.add(playbook)
        await self.session.flush()
        return playbook

    async def get_playbook(self, *, workspace_id: str, playbook_id: UUID) -> ConversationPlaybook | None:
        """Get one playbook by id in the current workspace."""

        statement = select(ConversationPlaybook).where(
            ConversationPlaybook.workspace_id == workspace_id,
            ConversationPlaybook.id == playbook_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_playbook_by_name(self, *, workspace_id: str, name: str) -> ConversationPlaybook | None:
        """Get one playbook by name in the current workspace."""

        statement = select(ConversationPlaybook).where(
            ConversationPlaybook.workspace_id == workspace_id,
            ConversationPlaybook.name == name,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_playbooks(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        category: str | None = None,
        limit: int = 100,
    ) -> list[ConversationPlaybook]:
        """List playbooks in the current workspace."""

        statement = select(ConversationPlaybook).where(ConversationPlaybook.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(ConversationPlaybook.status == status)
        if category is not None:
            statement = statement.where(ConversationPlaybook.category == category)
        statement = statement.order_by(ConversationPlaybook.name.asc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def create_playbook_run(
        self,
        *,
        workspace_id: str,
        playbook_id: UUID,
        thread_id: UUID,
        input_payload: dict[str, Any],
        output_payload: dict[str, Any] | None = None,
    ) -> ConversationPlaybookRun:
        """Create one playbook run."""

        run = ConversationPlaybookRun(
            workspace_id=workspace_id,
            playbook_id=playbook_id,
            thread_id=thread_id,
            status=ConversationPlaybookRunStatus.PENDING.value,
            input_payload=input_payload,
            output_payload=output_payload or {"steps": []},
            current_step=0,
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def get_playbook_run(self, *, workspace_id: str, run_id: UUID) -> ConversationPlaybookRun | None:
        """Get one playbook run in the current workspace."""

        statement = select(ConversationPlaybookRun).where(
            ConversationPlaybookRun.workspace_id == workspace_id,
            ConversationPlaybookRun.id == run_id,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_playbook_runs(
        self,
        *,
        workspace_id: str,
        thread_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ConversationPlaybookRun]:
        """List playbook runs in the current workspace."""

        statement = select(ConversationPlaybookRun).where(ConversationPlaybookRun.workspace_id == workspace_id)
        if thread_id is not None:
            statement = statement.where(ConversationPlaybookRun.thread_id == thread_id)
        if status is not None:
            statement = statement.where(ConversationPlaybookRun.status == status)
        statement = statement.order_by(ConversationPlaybookRun.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    def _estimate_token_count(self, content: str) -> int:
        """粗略 token 估算，避免在 runtime 基础层引入 tokenizer。"""

        return max(1, len(content.split()) or len(content) // 4)
