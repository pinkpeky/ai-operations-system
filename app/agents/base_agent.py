"""中央 Agent 基类模块。

BaseAgent 统一定义输入校验、Prompt 构建、LLM 调用、输出格式化和错误处理流程。
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, ClassVar, Protocol

from app.agents.llm_client import LLMClient
from app.memory.services import MemoryExecutionContext
from app.schemas.llm import LLMRequest, LLMResponse
from app.tools.base import ToolExecutionContext, ToolExecutionRecord
from app.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class AgentLLMClient(Protocol):
    """Agent 依赖的 LLM Client 协议，便于测试替换。"""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        """执行一次 LLM 生成。"""


class BaseAgent(ABC):
    """中央 Agent 基类。"""

    agent_name: ClassVar[str]
    agent_type: ClassVar[str]

    def __init__(
        self,
        llm_client: AgentLLMClient | None = None,
        tool_registry: ToolRegistry | None = None,
        available_tools: list[str] | None = None,
    ) -> None:
        self.llm_client = llm_client or LLMClient()
        self.tool_registry = tool_registry
        self.available_tools = available_tools or []
        self.tool_call_trace: list[dict[str, Any]] = []
        self.memory_trace: list[dict[str, Any]] = []
        self.current_plan_id: Any | None = None
        self.current_step_id: Any | None = None

    async def run(self, agent_input: dict[str, Any]) -> dict[str, Any]:
        """执行 Agent 标准流程。"""

        try:
            started_at = time.perf_counter()
            logger.info(
                "Agent run started",
                extra={
                    "agent_name": self.agent_name,
                    "agent_type": self.agent_type,
                    "workspace_id": agent_input.get("workspace_id"),
                    "task_id": agent_input.get("task_id"),
                    "current_plan_id": str(self.current_plan_id) if self.current_plan_id else None,
                    "current_step_id": str(self.current_step_id) if self.current_step_id else None,
                },
            )
            self.tool_call_trace = []
            self.memory_trace = []
            self.current_plan_id = agent_input.get("current_plan_id")
            self.current_step_id = agent_input.get("current_step_id")
            tool_results = await self._execute_requested_tools(agent_input)
            memory_context = await self.load_memory(agent_input)
            validated_input = self.validate_input(agent_input)
            prompt = self.build_prompt(validated_input)
            if memory_context:
                prompt = self._append_memory_context_to_prompt(prompt=prompt, memory_context=memory_context)
            if tool_results:
                prompt = self._append_tool_results_to_prompt(prompt=prompt, tool_results=tool_results)
            llm_response = await self.call_llm(prompt=prompt, validated_input=validated_input)
            output = self.format_output(validated_input=validated_input, llm_response=llm_response)
            await self.save_memory(agent_input=agent_input, output=output)
            if tool_results:
                output["tool_call_trace"] = self.tool_call_trace
            if self.memory_trace:
                output["memory_trace"] = self.memory_trace
            logger.info(
                "Agent run completed",
                extra={
                    "agent_name": self.agent_name,
                    "agent_type": self.agent_type,
                    "provider": llm_response.provider,
                    "model": llm_response.model,
                    "latency_ms": int((time.perf_counter() - started_at) * 1000),
                    "error": None,
                    "workspace_id": agent_input.get("workspace_id"),
                    "task_id": agent_input.get("task_id"),
                    "current_plan_id": str(self.current_plan_id) if self.current_plan_id else None,
                    "current_step_id": str(self.current_step_id) if self.current_step_id else None,
                },
            )
            return output
        except ValueError:
            logger.exception(
                "Agent input validation failed",
                extra={"agent_name": self.agent_name, "agent_type": self.agent_type},
            )
            raise
        except Exception as exc:
            logger.exception(
                "Agent run failed",
                extra={
                    "agent_name": self.agent_name,
                    "agent_type": self.agent_type,
                    "workspace_id": agent_input.get("workspace_id"),
                    "task_id": agent_input.get("task_id"),
                    "current_plan_id": str(self.current_plan_id) if self.current_plan_id else None,
                    "current_step_id": str(self.current_step_id) if self.current_step_id else None,
                    "error": str(exc),
                },
            )
            raise RuntimeError(str(exc) or f"{self.agent_name} failed") from exc

    @abstractmethod
    def validate_input(self, agent_input: dict[str, Any]) -> dict[str, Any]:
        """校验并标准化 Agent 输入。"""

    @abstractmethod
    def build_prompt(self, validated_input: dict[str, Any]) -> str:
        """根据输入构建 Prompt。"""

    async def call_llm(self, prompt: str, validated_input: dict[str, Any]) -> LLMResponse:
        """调用 LLM Client。"""

        try:
            return await self.llm_client.generate(
                LLMRequest(
                    system_prompt=self.get_system_prompt(),
                    user_prompt=prompt,
                )
            )
        except Exception as exc:
            logger.exception("Agent LLM call failed", extra={"agent_name": self.agent_name})
            raise RuntimeError(f"Agent LLM call failed: {exc}") from exc

    async def execute_tool(
        self,
        *,
        tool_name: str,
        tool_input: dict[str, Any],
        context: ToolExecutionContext,
    ) -> ToolExecutionRecord:
        """手动执行一个已注册工具，并写入 Agent trace。"""

        if self.tool_registry is None:
            raise RuntimeError("Tool registry is not configured for this agent")
        if self.available_tools and tool_name not in self.available_tools:
            raise PermissionError(f"Tool is not available for agent: {tool_name}")
        record = await self.tool_registry.execute_tool(
            tool_name=tool_name,
            tool_input=tool_input,
            context=context,
            agent_name=self.agent_name,
        )
        self.tool_call_trace.append(record.model_dump())
        return record

    async def _execute_requested_tools(self, agent_input: dict[str, Any]) -> list[ToolExecutionRecord]:
        """执行输入中手动指定的工具调用。"""

        tool_calls = self._extract_tool_calls(agent_input)
        if not tool_calls:
            return []
        context = agent_input.get("tool_context")
        if not isinstance(context, ToolExecutionContext):
            raise ValueError("tool_context is required when tool_calls are provided")
        context.agent_name = self.agent_name
        results: list[ToolExecutionRecord] = []
        for tool_call in tool_calls:
            results.append(
                await self.execute_tool(
                    tool_name=str(tool_call["tool_name"]),
                    tool_input=dict(tool_call.get("tool_input") or {}),
                    context=context,
                )
            )
        return results

    def _extract_tool_calls(self, agent_input: dict[str, Any]) -> list[dict[str, Any]]:
        """解析手动指定的工具调用。"""

        calls = agent_input.get("tool_calls")
        if isinstance(calls, list):
            normalized: list[dict[str, Any]] = []
            for item in calls:
                if not isinstance(item, dict):
                    raise ValueError("Each tool call must be an object")
                tool_name = item.get("tool_name") or item.get("name")
                if not tool_name:
                    raise ValueError("tool_name is required for each tool call")
                normalized.append(
                    {
                        "tool_name": tool_name,
                        "tool_input": item.get("tool_input") or item.get("input") or {},
                    }
                )
            return normalized
        if "tool_name" in agent_input:
            return [
                {
                    "tool_name": agent_input["tool_name"],
                    "tool_input": agent_input.get("tool_input") or {},
                }
            ]
        return []

    def _append_tool_results_to_prompt(self, prompt: str, tool_results: list[ToolExecutionRecord]) -> str:
        """把工具结果附加到 prompt，供 LLM 生成时参考。"""

        trace = [result.model_dump() for result in tool_results]
        return (
            f"{prompt}\n\n"
            "工具调用结果如下，请在生成答案时参考这些结构化结果：\n"
            f"{trace}"
        )

    async def load_memory(self, agent_input: dict[str, Any]) -> dict[str, Any]:
        """加载会话最近消息和 Agent Memory。"""

        context = agent_input.get("memory_context")
        if not isinstance(context, MemoryExecutionContext):
            return {}
        started_at = time.perf_counter()
        recent_messages = []
        retrieved_memories = []
        session_id = agent_input.get("session_id") or context.session_id
        try:
            if session_id is not None:
                recent_messages = await context.service.get_recent_messages(
                    workspace_id=context.workspace_id,
                    session_id=session_id,
                    limit=context.recent_limit,
                )
            query = self._memory_query(agent_input)
            if query:
                retrieved_memories = await context.service.search_memory(
                    workspace_id=context.workspace_id,
                    query=query,
                    agent_name=context.agent_name or self.agent_name,
                    limit=context.memory_limit,
                )
            self.memory_trace.append(
                {
                    "operation": "load_memory",
                    "session_id": str(session_id) if session_id is not None else None,
                    "recent_messages_count": len(recent_messages),
                    "retrieved_memories_count": len(retrieved_memories),
                    "latency_ms": int((time.perf_counter() - started_at) * 1000),
                    "success": True,
                    "error": None,
                }
            )
            return {"recent_messages": recent_messages, "retrieved_memories": retrieved_memories}
        except Exception as exc:
            self.memory_trace.append(
                {
                    "operation": "load_memory",
                    "session_id": str(session_id) if session_id is not None else None,
                    "recent_messages_count": 0,
                    "retrieved_memories_count": 0,
                    "latency_ms": int((time.perf_counter() - started_at) * 1000),
                    "success": False,
                    "error": str(exc),
                }
            )
            raise

    async def save_memory(self, *, agent_input: dict[str, Any], output: dict[str, Any]) -> None:
        """按需保存 Agent Memory。"""

        context = agent_input.get("memory_context")
        if not isinstance(context, MemoryExecutionContext):
            return
        memory_to_save = agent_input.get("memory_to_save")
        should_save = bool(agent_input.get("save_memory")) or isinstance(memory_to_save, dict)
        if not should_save:
            return
        started_at = time.perf_counter()
        memory_type = "short_term"
        content = ""
        metadata: dict[str, Any] = {"agent_type": self.agent_type}
        importance_score = 0.5
        if isinstance(memory_to_save, dict):
            memory_type = str(memory_to_save.get("memory_type") or memory_type)
            content = str(memory_to_save.get("content") or "")
            metadata.update(dict(memory_to_save.get("metadata") or {}))
            importance_score = float(memory_to_save.get("importance_score") or importance_score)
        if not content:
            content = str(output.get("raw_response") or output)[:4000]
        try:
            memory = await context.service.save_memory(
                workspace_id=context.workspace_id,
                agent_name=context.agent_name or self.agent_name,
                memory_type=memory_type,
                content=content,
                metadata=metadata,
                importance_score=importance_score,
            )
            self.memory_trace.append(
                {
                    "operation": "save_memory",
                    "memory_id": str(memory.id),
                    "memory_type": memory.memory_type,
                    "latency_ms": int((time.perf_counter() - started_at) * 1000),
                    "success": True,
                    "error": None,
                }
            )
        except Exception as exc:
            self.memory_trace.append(
                {
                    "operation": "save_memory",
                    "memory_type": memory_type,
                    "latency_ms": int((time.perf_counter() - started_at) * 1000),
                    "success": False,
                    "error": str(exc),
                }
            )
            raise

    def _append_memory_context_to_prompt(self, prompt: str, memory_context: dict[str, Any]) -> str:
        """把 Memory 上下文附加到 prompt。"""

        recent_messages = memory_context.get("recent_messages") or []
        retrieved_memories = memory_context.get("retrieved_memories") or []
        message_lines = [
            f"{getattr(message, 'role', 'unknown')}: {getattr(message, 'content', '')}"
            for message in recent_messages
        ]
        memory_lines = [
            f"{getattr(memory, 'memory_type', 'memory')}: {getattr(memory, 'content', '')}"
            for memory in retrieved_memories
        ]
        return (
            f"{prompt}\n\n"
            "会话最近消息：\n"
            f"{message_lines or ['无']}\n\n"
            "检索到的 Agent Memory：\n"
            f"{memory_lines or ['无']}"
        )

    def _memory_query(self, agent_input: dict[str, Any]) -> str:
        """从 Agent 输入中推断 memory 检索 query。"""

        for key in ("query", "topic", "value", "input"):
            value = agent_input.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    @abstractmethod
    def format_output(self, validated_input: dict[str, Any], llm_response: LLMResponse) -> dict[str, Any]:
        """格式化 Agent 输出。"""

    def get_system_prompt(self) -> str:
        """返回 Agent 默认 system prompt。"""

        return "你是 AI Operations System 的中央 Agent，请按当前 Agent 职责输出结构化结果。"
