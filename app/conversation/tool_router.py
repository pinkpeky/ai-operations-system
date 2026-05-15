"""Rule-based router for the Conversation Tool Execution Bridge.

The router intentionally stays deterministic. It selects one limited route from
the user message, prepares structured input for the bridge layer, and leaves
real execution to ConversationService.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import urlparse


RouteType = Literal["tool", "agent", "planning", "fallback"]


@dataclass(slots=True)
class ConversationRouteDecision:
    """Structured route decision used by ConversationService."""

    route_name: str
    selected_tool: str | None
    reason: str
    confidence: float
    tool_input: dict[str, Any]
    route_type: RouteType
    fallback_route: str = "default"

    def to_payload(self) -> dict[str, Any]:
        """Return a JSON-safe event payload."""

        return {
            "route_name": self.route_name,
            "selected_tool": self.selected_tool,
            "reason": self.reason,
            "confidence": self.confidence,
            "tool_input": self.tool_input,
            "route_type": self.route_type,
            "fallback_route": self.fallback_route,
        }


class ConversationToolRouter:
    """Select a bounded bridge route from a user message."""

    URL_PATTERN = re.compile(r"https?://[^\s\u3002\uff0c,]+", flags=re.IGNORECASE)

    PLANNING_KEYWORDS = ("计划", "规划", "拆解", "步骤", "step", "steps", "plan", "planning")
    BROWSER_KEYWORDS = (
        "搜索",
        "浏览器",
        "打开网页",
        "打开",
        "网页",
        "截图",
        "screenshot",
        "browser",
        "browse",
        "search",
    )
    OPENCLAW_KEYWORDS = ("openclaw", "open claw", "手机", "设备", "device", "app")
    RAG_KEYWORDS = ("知识库", "检索", "文档", "资料", "rag", "knowledge", "document", "docs")
    TASK_KEYWORDS = ("任务", "创建任务", "后台执行", "task", "background")
    CONTENT_KEYWORDS = ("文案", "内容", "标题", "生成", "短视频", "content", "copywriting", "generate", "title")

    def route(
        self,
        message: str,
        *,
        metadata: dict[str, Any] | None = None,
        run_input: dict[str, Any] | None = None,
    ) -> ConversationRouteDecision:
        """Create a deterministic route decision.

        More specific orchestration requests are checked before broad content
        generation keywords so messages such as "create a plan to generate..."
        reach PlanningService.
        """

        normalized = message.lower()
        metadata = metadata or {}
        run_input = run_input or {}

        if self._contains(normalized, self.PLANNING_KEYWORDS):
            return self._planning_route(message)
        if self._contains(normalized, self.BROWSER_KEYWORDS):
            return self._browser_route(message)
        if self._contains(normalized, self.OPENCLAW_KEYWORDS):
            return self._openclaw_route(message)
        if self._contains(normalized, self.RAG_KEYWORDS):
            return self._rag_route(message, metadata=metadata, run_input=run_input)
        if self._contains(normalized, self.TASK_KEYWORDS):
            return self._task_route(message)
        if self._contains(normalized, self.CONTENT_KEYWORDS):
            return self._content_route(message, metadata=metadata, run_input=run_input)
        return ConversationRouteDecision(
            route_name="fallback",
            selected_tool=None,
            reason="No bridge keyword matched; returning a safe conversational fallback.",
            confidence=0.2,
            tool_input={"message": message},
            route_type="fallback",
        )

    def _browser_route(self, message: str) -> ConversationRouteDecision:
        target = self._extract_url(message) or "https://example.com"
        return ConversationRouteDecision(
            route_name="browser",
            selected_tool="browser_tool",
            reason="Message asks for browser/search/page/screenshot work.",
            confidence=0.86,
            tool_input={
                "action_type": "navigate_and_screenshot",
                "target": target,
                "url": target,
                "screenshot_name": self._screenshot_name(target),
                "metadata": {"bridge": "conversation", "composite": True},
            },
            route_type="tool",
        )

    def _openclaw_route(self, message: str) -> ConversationRouteDecision:
        return ConversationRouteDecision(
            route_name="openclaw",
            selected_tool="openclaw_tool",
            reason="Message mentions OpenClaw/device/app; only mock OpenClaw is enabled.",
            confidence=0.82,
            tool_input={
                "action_type": "execute_action",
                "openclaw_action_type": "mock_inspect",
                "target": "mock-device",
                "input_payload": {"message": message},
                "metadata": {"bridge": "conversation", "mock": True},
            },
            route_type="tool",
        )

    def _rag_route(
        self,
        message: str,
        *,
        metadata: dict[str, Any],
        run_input: dict[str, Any],
    ) -> ConversationRouteDecision:
        collection_name = self._first_non_empty(
            self._nested(run_input, "input", "collection_name"),
            run_input.get("collection_name"),
            metadata.get("collection_name"),
        )
        return ConversationRouteDecision(
            route_name="rag_search",
            selected_tool="rag_search_tool",
            reason="Message asks for knowledge-base or RAG retrieval.",
            confidence=0.78,
            tool_input={
                "query": message,
                "collection_name": collection_name,
                "top_k": 5,
                "final_top_k": 5,
                "search_mode": self._first_non_empty(
                    self._nested(run_input, "input", "search_mode"),
                    metadata.get("search_mode"),
                    "hybrid",
                ),
            },
            route_type="tool",
        )

    def _task_route(self, message: str) -> ConversationRouteDecision:
        return ConversationRouteDecision(
            route_name="create_task",
            selected_tool="create_task_tool",
            reason="Message asks to create or run a background task.",
            confidence=0.72,
            tool_input={
                "title": "Conversation generated task",
                "task_type": "content_generation",
                "payload": {
                    "topic": message,
                    "platform": "tiktok",
                    "style": "professional concise",
                    "source": "conversation_runtime",
                },
                "max_retries": 3,
            },
            route_type="tool",
        )

    def _content_route(
        self,
        message: str,
        *,
        metadata: dict[str, Any],
        run_input: dict[str, Any],
    ) -> ConversationRouteDecision:
        return ConversationRouteDecision(
            route_name="content",
            selected_tool=None,
            reason="Message asks for content/copy/title generation.",
            confidence=0.8,
            tool_input={
                "topic": message[:255],
                "platform": self._first_non_empty(
                    self._nested(run_input, "input", "platform"),
                    metadata.get("platform"),
                    "tiktok",
                ),
                "style": self._first_non_empty(
                    self._nested(run_input, "input", "style"),
                    metadata.get("style"),
                    "professional concise",
                ),
            },
            route_type="agent",
        )

    def _planning_route(self, message: str) -> ConversationRouteDecision:
        return ConversationRouteDecision(
            route_name="planning",
            selected_tool=None,
            reason="Message asks to break down a goal into steps.",
            confidence=0.84,
            tool_input={"root_goal": message, "metadata": {"bridge": "conversation", "phase": "38"}},
            route_type="planning",
        )

    def _contains(self, normalized_message: str, keywords: tuple[str, ...]) -> bool:
        return any(keyword.lower() in normalized_message for keyword in keywords)

    def _extract_url(self, message: str) -> str | None:
        match = self.URL_PATTERN.search(message)
        return match.group(0).rstrip("。.,，") if match else None

    def _screenshot_name(self, url: str) -> str:
        parsed = urlparse(url)
        host = (parsed.netloc or "page").replace(".", "-")
        return f"conversation-{host}"[:80]

    def _nested(self, payload: dict[str, Any], *keys: str) -> Any:
        current: Any = payload
        for key in keys:
            if not isinstance(current, dict):
                return None
            current = current.get(key)
        return current

    def _first_non_empty(self, *values: Any) -> Any:
        for value in values:
            if value not in (None, ""):
                return value
        return None
