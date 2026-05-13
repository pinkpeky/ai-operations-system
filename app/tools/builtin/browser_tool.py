"""Browser Adapter 内置工具。

该工具只暴露安全的 browser action 子集，并统一走 BrowserService。Phase 17
默认使用 MockBrowserProvider，因此不会执行真实浏览器自动化。
"""

from __future__ import annotations

from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.browser.services import BrowserHumanControlService, BrowserService, BrowserUIAccessService
from app.schemas.browser import (
    BrowserActionResponse,
    BrowserHumanControlSessionResponse,
    BrowserSessionResponse,
    BrowserUIAccessResponse,
)
from app.tools.base import BaseTool, ToolExecutionContext


class BrowserToolInput(BaseModel):
    """Browser tool 输入。"""

    action_type: Literal[
        "navigate",
        "click",
        "type_text",
        "screenshot",
        "get_page_content",
        "request_human_control",
        "complete_human_control",
        "create_ui_access",
        "revoke_ui_access",
    ] = Field(description="Browser action type")
    session_id: UUID | None = Field(default=None, description="Optional existing browser session")
    control_session_id: UUID | None = Field(default=None, description="Human control session for completion")
    human_control_session_id: UUID | None = Field(default=None, description="Human control session for UI access")
    access_session_id: UUID | None = Field(default=None, description="UI access session for revoke")
    scopes: list[Literal["view", "control", "screenshot", "devtools_placeholder"]] = Field(
        default_factory=lambda: ["view"],
        description="UI access scopes for create_ui_access",
    )
    one_time: bool = Field(default=False, description="Whether UI access token is single-use")
    target: str | None = Field(default=None, description="URL, selector, or semantic target")
    selector: str | None = Field(default=None, description="DOM selector for click/type_text")
    text: str | None = Field(default=None, description="Text for type_text")
    reason: str | None = Field(default=None, description="Reason for request_human_control")
    note: str | None = Field(default=None, description="Completion note for complete_human_control")
    screenshot_name: str | None = Field(default=None, description="Screenshot filename without extension")
    input_payload: dict[str, Any] = Field(default_factory=dict, description="Action payload")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Session metadata when auto-creating a session")


class BrowserToolOutput(BaseModel):
    """Browser tool 输出。"""

    success: bool
    session: dict[str, Any]
    action: dict[str, Any]
    error: str | None
    latency_ms: int | None


class BrowserTool(BaseTool):
    """在当前 workspace 内执行安全的 mock browser action。"""

    name = "browser_tool"
    description = "Execute browser actions, human-control handoffs, and placeholder UI access requests through browser services."
    input_schema = BrowserToolInput
    output_schema = BrowserToolOutput
    permission_scopes = ["browser:execute"]

    async def execute(self, tool_input: BaseModel, context: ToolExecutionContext) -> BaseModel:
        """通过 BrowserService 执行 browser action。"""

        request = BrowserToolInput.model_validate(tool_input.model_dump())
        session = context.require_session()
        service = BrowserService(session, settings=context.effective_settings)
        human_control_service = BrowserHumanControlService(session, settings=context.effective_settings)
        ui_access_service = BrowserUIAccessService(session, settings=context.effective_settings)
        browser_session = None

        if request.action_type == "complete_human_control":
            if request.control_session_id is None:
                raise ValueError("control_session_id is required for complete_human_control")
            control_session = await human_control_service.complete_control(
                workspace_id=context.require_workspace(),
                control_session_id=request.control_session_id,
                note=request.note,
                metadata={
                    **request.metadata,
                    "completed_by": self.name,
                    "task_id": context.task_id,
                    "agent_name": context.agent_name,
                },
            )
            browser_session = await service.repository.get_session(
                session_id=control_session.browser_session_id,
                workspace_id=context.require_workspace(),
            )
            if browser_session is None:
                raise ValueError("Browser session not found")
            return BrowserToolOutput(
                success=True,
                session=BrowserSessionResponse.from_model(browser_session).model_dump(mode="json"),
                action={"human_control": BrowserHumanControlSessionResponse.from_model(control_session).model_dump(mode="json")},
                error=None,
                latency_ms=None,
            )

        if request.action_type == "revoke_ui_access":
            if request.access_session_id is None:
                raise ValueError("access_session_id is required for revoke_ui_access")
            access_session = await ui_access_service.revoke_access_session(
                workspace_id=context.require_workspace(),
                access_session_id=request.access_session_id,
                reason=request.reason or "revoked by browser_tool",
            )
            browser_session = await service.repository.get_session(
                session_id=access_session.browser_session_id,
                workspace_id=context.require_workspace(),
            )
            if browser_session is None:
                raise ValueError("Browser session not found")
            return BrowserToolOutput(
                success=True,
                session=BrowserSessionResponse.from_model(browser_session).model_dump(mode="json"),
                action={"ui_access": BrowserUIAccessResponse.from_model(access_session).model_dump(mode="json")},
                error=None,
                latency_ms=None,
            )

        if request.session_id is None:
            browser_session = await service.create_browser_session(
                workspace_id=context.require_workspace(),
                user_id=context.user_id,
                metadata={
                    **request.metadata,
                    "created_by": self.name,
                    "task_id": context.task_id,
                    "agent_name": context.agent_name,
                },
            )
            session_id = browser_session.id
        else:
            session_id = request.session_id
            browser_session = await service.repository.get_session(
                session_id=session_id,
                workspace_id=context.require_workspace(),
            )
            if browser_session is None:
                raise ValueError("Browser session not found")

        if request.action_type == "request_human_control":
            control_session = await human_control_service.request_control(
                workspace_id=context.require_workspace(),
                browser_session_id=session_id,
                reason=request.reason or request.target or "human control requested",
                requested_by=context.user_id,
                metadata={
                    **request.metadata,
                    "requested_by_tool": self.name,
                    "task_id": context.task_id,
                    "agent_name": context.agent_name,
                },
            )
            browser_session = await service.repository.get_session(
                session_id=session_id,
                workspace_id=context.require_workspace(),
            )
            if browser_session is None:
                raise ValueError("Browser session not found")
            return BrowserToolOutput(
                success=True,
                session=BrowserSessionResponse.from_model(browser_session).model_dump(mode="json"),
                action={"human_control": BrowserHumanControlSessionResponse.from_model(control_session).model_dump(mode="json")},
                error=None,
                latency_ms=None,
            )

        if request.action_type == "create_ui_access":
            result = await ui_access_service.create_access_session(
                workspace_id=context.require_workspace(),
                browser_session_id=session_id,
                human_control_session_id=request.human_control_session_id or request.control_session_id,
                scopes=request.scopes,
                one_time=request.one_time,
                metadata={
                    **request.metadata,
                    "created_by_tool": self.name,
                    "task_id": context.task_id,
                    "agent_name": context.agent_name,
                    "placeholder": True,
                },
            )
            browser_session = await service.repository.get_session(
                session_id=session_id,
                workspace_id=context.require_workspace(),
            )
            if browser_session is None:
                raise ValueError("Browser session not found")
            return BrowserToolOutput(
                success=True,
                session=BrowserSessionResponse.from_model(browser_session).model_dump(mode="json"),
                action={
                    "ui_access": BrowserUIAccessResponse.from_model(
                        result.access_session,
                        access_token=result.access_token,
                    ).model_dump(mode="json"),
                    "placeholder": True,
                },
                error=None,
                latency_ms=None,
            )

        payload = dict(request.input_payload)
        if request.selector is not None:
            payload["selector"] = request.selector
        if request.text is not None:
            payload["text"] = request.text
        if request.screenshot_name is not None:
            payload["screenshot_name"] = request.screenshot_name
        action = await service.execute_action(
            workspace_id=context.require_workspace(),
            session_id=session_id,
            action_type=request.action_type,
            target=request.target,
            input_payload=payload,
        )
        return BrowserToolOutput(
            success=action.status == "completed",
            session=BrowserSessionResponse.from_model(browser_session).model_dump(mode="json"),
            action=BrowserActionResponse.from_model(action).model_dump(mode="json"),
            error=action.error,
            latency_ms=action.duration_ms,
        )
