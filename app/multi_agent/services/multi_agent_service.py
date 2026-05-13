"""Multi-Agent 编排服务。

当前只实现固定链路与手动 agent/tool 调用，不做 autonomous planning、ReAct 或 Browser Agent。
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.content_agent import ContentAgent
from app.agents.llm_client import LLMClient
from app.api.routes.rag import create_hybrid_search_pipeline
from app.core.config import Settings, get_settings
from app.memory.services import MemoryExecutionContext, MemoryService
from app.models.enums import AgentHandoffStatus
from app.models.multi_agent import AgentHandoff, AgentMessage, AgentRun
from app.multi_agent.repositories import AgentRunRepository
from app.multi_agent.services.agent_registry import AgentRegistry, build_default_agent_registry
from app.rag.agentic_orchestrator import AgenticRAGOrchestrator
from app.reranker.reranker_client import RerankerClient
from app.schemas.agentic_rag import AgenticRAGRequest
from app.tools.base import ToolExecutionContext
from app.tools.registry import ToolRegistry, build_default_tool_registry

logger = logging.getLogger(__name__)


class MultiAgentService:
    """Multi-Agent 基础服务。"""

    CONTENT_PLANNING_CHAIN = ["content_planner", "rag_agent", "content_agent", "review_agent"]

    def __init__(
        self,
        session: AsyncSession,
        *,
        settings: Settings | None = None,
        agent_registry: AgentRegistry | None = None,
        tool_registry: ToolRegistry | None = None,
    ) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.repository = AgentRunRepository(session)
        self.agent_registry = agent_registry or build_default_agent_registry()
        self.tool_registry = tool_registry or build_default_tool_registry()

    async def create_run(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        session_id: UUID | None,
        root_agent: str,
        run_input: dict[str, Any],
    ) -> AgentRun:
        """创建 Multi-Agent run。"""

        self.agent_registry.get_agent(root_agent)
        run = await self.repository.create_run(
            workspace_id=workspace_id,
            user_id=user_id,
            session_id=session_id,
            root_agent=root_agent,
            run_input=run_input,
        )
        await self.repository.append_message(
            workspace_id=workspace_id,
            run_id=run.id,
            from_agent=None,
            to_agent=root_agent,
            role="system",
            content=f"Multi-Agent run created for root_agent={root_agent}",
            metadata={"agents_involved": [root_agent]},
        )
        await self.session.commit()
        await self.session.refresh(run)
        logger.info("Multi-Agent run created", extra={"run_id": str(run.id), "workspace_id": workspace_id})
        return run

    async def append_message(
        self,
        *,
        run: AgentRun,
        from_agent: str | None,
        to_agent: str | None,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> AgentMessage:
        """追加 run message。"""

        message = await self.repository.append_message(
            workspace_id=run.workspace_id,
            run_id=run.id,
            from_agent=from_agent,
            to_agent=to_agent,
            role=role,
            content=content,
            metadata=metadata,
        )
        await self.session.flush()
        return message

    async def handoff(
        self,
        *,
        run: AgentRun,
        from_agent: str,
        to_agent: str,
        reason: str,
        payload: dict[str, Any],
        status: str = AgentHandoffStatus.COMPLETED.value,
    ) -> AgentHandoff:
        """记录 Agent handoff。"""

        self.agent_registry.get_agent(from_agent)
        self.agent_registry.get_agent(to_agent)
        handoff = await self.repository.create_handoff(
            workspace_id=run.workspace_id,
            run_id=run.id,
            from_agent=from_agent,
            to_agent=to_agent,
            reason=reason,
            payload=payload,
            status=status,
        )
        await self.repository.append_message(
            workspace_id=run.workspace_id,
            run_id=run.id,
            from_agent=from_agent,
            to_agent=to_agent,
            role="handoff",
            content=reason,
            metadata={"payload": payload, "status": status},
        )
        return handoff

    async def execute_single_agent(
        self,
        *,
        agent_name: str,
        agent_input: dict[str, Any],
        workspace_id: str,
        user_id: str | None = None,
        session_id: UUID | None = None,
        run_id: UUID | None = None,
        current_plan_id: UUID | None = None,
        current_step_id: UUID | None = None,
    ) -> dict[str, Any]:
        """执行一个已注册 Agent。"""

        self.agent_registry.get_agent(agent_name)
        agent_input = {
            **agent_input,
            "current_plan_id": current_plan_id,
            "current_step_id": current_step_id,
        }
        if agent_name == "content_planner":
            return await self._execute_content_planner(agent_input=agent_input)
        if agent_name == "rag_agent":
            return await self._execute_rag_agent(
                agent_input=agent_input,
                workspace_id=workspace_id,
                user_id=user_id,
                session_id=session_id,
                run_id=run_id,
                current_step_id=current_step_id,
            )
        if agent_name == "content_agent":
            return await self._execute_content_agent(
                agent_input=agent_input,
                workspace_id=workspace_id,
                user_id=user_id,
                session_id=session_id,
            )
        if agent_name == "review_agent":
            return await self._execute_review_agent(agent_input=agent_input)
        if agent_name == "runtime_agent":
            return await self._execute_runtime_agent(workspace_id=workspace_id, user_id=user_id)
        if agent_name == "tool_agent":
            return await self._execute_tool_agent(
                agent_input=agent_input,
                workspace_id=workspace_id,
                user_id=user_id,
                run_id=run_id,
                current_step_id=current_step_id,
            )
        raise KeyError(f"Agent executor not implemented: {agent_name}")

    async def execute_agent_chain(
        self,
        *,
        run: AgentRun,
        chain_name: str = "content_planning",
        chain_input: dict[str, Any] | None = None,
    ) -> tuple[AgentRun, list[str]]:
        """执行固定 Content Planning Chain。"""

        if chain_name != "content_planning":
            raise ValueError("Only content_planning chain is supported in Phase 15")

        started_at = time.perf_counter()
        agents_involved = list(self.CONTENT_PLANNING_CHAIN)
        input_data = dict(run.run_input)
        if chain_input:
            input_data.update(chain_input)

        try:
            await self.repository.mark_running(run)
            await self.repository.append_message(
                workspace_id=run.workspace_id,
                run_id=run.id,
                from_agent=None,
                to_agent=run.root_agent,
                role="system",
                content="Content Planning Chain started",
                metadata={"chain_name": chain_name, "agents_involved": agents_involved},
            )

            planner_output = await self.execute_single_agent(
                agent_name="content_planner",
                agent_input=input_data,
                workspace_id=run.workspace_id,
                user_id=run.user_id,
                session_id=run.session_id,
                run_id=run.id,
            )
            await self._append_agent_output(run=run, agent_name="content_planner", output=planner_output)
            await self.handoff(
                run=run,
                from_agent="content_planner",
                to_agent="rag_agent",
                reason="Plan needs knowledge grounding",
                payload={"query": planner_output.get("rag_query")},
            )

            rag_output = await self.execute_single_agent(
                agent_name="rag_agent",
                agent_input={**input_data, **planner_output},
                workspace_id=run.workspace_id,
                user_id=run.user_id,
                session_id=run.session_id,
                run_id=run.id,
            )
            await self._append_agent_output(run=run, agent_name="rag_agent", output=rag_output)
            await self.handoff(
                run=run,
                from_agent="rag_agent",
                to_agent="content_agent",
                reason="RAG context ready for content generation",
                payload={"rag_answer": rag_output.get("answer"), "used_retrieval": rag_output.get("used_retrieval")},
            )

            content_output = await self.execute_single_agent(
                agent_name="content_agent",
                agent_input={**input_data, "rag_context": rag_output},
                workspace_id=run.workspace_id,
                user_id=run.user_id,
                session_id=run.session_id,
                run_id=run.id,
            )
            await self._append_agent_output(run=run, agent_name="content_agent", output=content_output)
            await self.handoff(
                run=run,
                from_agent="content_agent",
                to_agent="review_agent",
                reason="Generated content requires lightweight review",
                payload={"title": content_output.get("title"), "tags": content_output.get("tags")},
            )

            review_output = await self.execute_single_agent(
                agent_name="review_agent",
                agent_input={"content": content_output, "planner": planner_output, "rag": rag_output},
                workspace_id=run.workspace_id,
                user_id=run.user_id,
                session_id=run.session_id,
                run_id=run.id,
            )
            await self._append_agent_output(run=run, agent_name="review_agent", output=review_output)

            output = {
                "chain_name": chain_name,
                "agents_involved": agents_involved,
                "planner": planner_output,
                "rag": rag_output,
                "content": content_output,
                "review": review_output,
                "handoff_trace": [
                    "content_planner->rag_agent",
                    "rag_agent->content_agent",
                    "content_agent->review_agent",
                ],
            }
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            await self.repository.complete_run(run, output=output, duration_ms=duration_ms)
            await self.session.commit()
            await self.session.refresh(run)
            logger.info("Multi-Agent chain completed", extra={"run_id": str(run.id), "duration_ms": duration_ms})
            return run, agents_involved
        except Exception as exc:
            await self.session.rollback()
            duration_ms = int((time.perf_counter() - started_at) * 1000)
            fresh_run = await self.repository.get_run(run_id=run.id, workspace_id=run.workspace_id)
            if fresh_run is not None:
                await self.repository.fail_run(fresh_run, error=str(exc), duration_ms=duration_ms)
                await self.session.commit()
                run = fresh_run
            logger.exception("Multi-Agent chain failed", extra={"run_id": str(run.id), "error": str(exc)})
            raise

    async def get_run(self, *, run_id: UUID, workspace_id: str) -> AgentRun | None:
        """查询 run。"""

        return await self.repository.get_run(run_id=run_id, workspace_id=workspace_id)

    async def list_runs(self, *, workspace_id: str, limit: int = 100) -> list[AgentRun]:
        """列出 runs。"""

        return await self.repository.list_runs(workspace_id=workspace_id, limit=limit)

    async def list_messages(self, *, run_id: UUID, workspace_id: str, limit: int = 200) -> list[AgentMessage]:
        """列出 messages。"""

        return await self.repository.list_messages(run_id=run_id, workspace_id=workspace_id, limit=limit)

    async def list_handoffs(self, *, run_id: UUID, workspace_id: str, limit: int = 200) -> list[AgentHandoff]:
        """列出 handoffs。"""

        return await self.repository.list_handoffs(run_id=run_id, workspace_id=workspace_id, limit=limit)

    async def _append_agent_output(self, *, run: AgentRun, agent_name: str, output: dict[str, Any]) -> None:
        """将 Agent 输出写入消息流。"""

        await self.repository.append_message(
            workspace_id=run.workspace_id,
            run_id=run.id,
            from_agent=agent_name,
            to_agent=None,
            role="assistant",
            content=str(output)[:4000],
            metadata={"output": output},
        )

    async def _execute_content_planner(self, *, agent_input: dict[str, Any]) -> dict[str, Any]:
        """轻量 deterministic content planner。"""

        topic = str(agent_input.get("topic") or agent_input.get("query") or "AI 自动化运营")
        platform = str(agent_input.get("platform") or "tiktok")
        style = str(agent_input.get("style") or "专业简洁")
        rag_query = str(agent_input.get("rag_query") or agent_input.get("query") or f"{topic} 的知识背景和关键要点")
        return {
            "topic": topic,
            "platform": platform,
            "style": style,
            "rag_query": rag_query,
            "content_brief": f"围绕 {topic} 生成适合 {platform} 的{style}内容。",
            "planning_mode": "fixed_chain_mock",
        }

    async def _execute_rag_agent(
        self,
        *,
        agent_input: dict[str, Any],
        workspace_id: str,
        user_id: str | None,
        session_id: UUID | None,
        run_id: UUID | None,
        current_step_id: UUID | None = None,
    ) -> dict[str, Any]:
        """执行 AgenticRAGOrchestrator 包装。"""

        query = str(agent_input.get("rag_query") or agent_input.get("query") or agent_input.get("topic") or "ping")
        collection_name = agent_input.get("collection_name")
        try:
            hybrid_pipeline = create_hybrid_search_pipeline(
                settings=self.settings,
                session=self.session,
                collection_name=str(collection_name) if collection_name else None,
            )
            orchestrator = AgenticRAGOrchestrator(
                llm_client=LLMClient(settings=self.settings),
                hybrid_search_pipeline=hybrid_pipeline,
                reranker_client=RerankerClient(settings=self.settings),
                memory_service=MemoryService(self.session),
                retrieval_top_k=self.settings.dense_top_k,
                keyword_top_k=self.settings.keyword_top_k,
                search_mode=self.settings.default_search_mode,  # type: ignore[arg-type]
                rerank_top_n=self.settings.rerank_top_n,
            )
            response = await orchestrator.query(
                AgenticRAGRequest(
                    query=query,
                    collection_name=str(collection_name) if collection_name else None,
                    top_k=int(agent_input.get("top_k") or 3),
                    debug=True,
                    session_id=str(session_id) if session_id else None,
                ),
                workspace_id=workspace_id,
                task_id=str(current_step_id or run_id) if (current_step_id or run_id) else None,
            )
            return {
                "answer": response.answer,
                "used_retrieval": response.used_retrieval,
                "retrieved_chunks": [chunk.model_dump(mode="json") for chunk in response.retrieved_chunks],
                "provider": response.provider,
                "model": response.model,
                "debug": response.debug.model_dump(mode="json") if response.debug else None,
            }
        except Exception as exc:
            logger.warning("rag_agent fallback activated", extra={"workspace_id": workspace_id, "error": str(exc)})
            return {
                "answer": "",
                "used_retrieval": False,
                "retrieved_chunks": [],
                "provider": "mock",
                "model": "mock-fallback",
                "error": str(exc),
                "fallback": True,
            }

    async def _execute_content_agent(
        self,
        *,
        agent_input: dict[str, Any],
        workspace_id: str,
        user_id: str | None,
        session_id: UUID | None,
    ) -> dict[str, Any]:
        """执行 ContentAgent。"""

        payload = {
            "topic": str(agent_input.get("topic") or "AI 自动化运营"),
            "platform": str(agent_input.get("platform") or "tiktok"),
            "style": str(agent_input.get("style") or "专业简洁"),
            "current_plan_id": agent_input.get("current_plan_id"),
            "current_step_id": agent_input.get("current_step_id"),
        }
        if session_id is not None:
            payload["session_id"] = session_id
            payload["memory_context"] = MemoryExecutionContext(
                service=MemoryService(self.session),
                workspace_id=workspace_id,
                user_id=user_id,
                session_id=session_id,
                agent_name="ContentAgent",
            )
        return await ContentAgent(llm_client=LLMClient(settings=self.settings)).run(payload)

    async def _execute_review_agent(self, *, agent_input: dict[str, Any]) -> dict[str, Any]:
        """轻量 mock review。"""

        content = dict(agent_input.get("content") or {})
        has_title = bool(content.get("title"))
        has_description = bool(content.get("description"))
        return {
            "review_status": "approved" if has_title and has_description else "needs_revision",
            "review_agent": "review_agent",
            "notes": [
                "Phase 15 mock review only checks basic structured fields.",
                "No autonomous planning, ReAct, or external platform validation was performed.",
            ],
        }

    async def _execute_runtime_agent(self, *, workspace_id: str, user_id: str | None) -> dict[str, Any]:
        """读取 CURRENT_RUNTIME 的轻量 Agent。"""

        record = await self.tool_registry.execute_tool(
            tool_name="current_runtime_tool",
            tool_input={"include_document": True},
            context=ToolExecutionContext(
                workspace_id=workspace_id,
                user_id=user_id,
                session=self.session,
                settings=self.settings,
                agent_name="runtime_agent",
            ),
            agent_name="runtime_agent",
        )
        return {
            "tool_result": record.model_dump(),
            "current_runtime_path": str(Path("docs") / "CURRENT_RUNTIME.md"),
        }

    async def _execute_tool_agent(
        self,
        *,
        agent_input: dict[str, Any],
        workspace_id: str,
        user_id: str | None,
        run_id: UUID | None,
        current_step_id: UUID | None = None,
    ) -> dict[str, Any]:
        """调用现有 ToolRegistry 的 ToolAgent。"""

        tool_name = str(agent_input.get("tool_name") or "current_runtime_tool")
        tool_input = dict(agent_input.get("tool_input") or {"include_document": False})
        record = await self.tool_registry.execute_tool(
            tool_name=tool_name,
            tool_input=tool_input,
            context=ToolExecutionContext(
                workspace_id=workspace_id,
                user_id=user_id,
                session=self.session,
                settings=self.settings,
                agent_name="tool_agent",
                task_id=str(current_step_id or run_id) if (current_step_id or run_id) else None,
            ),
            agent_name="tool_agent",
        )
        return record.model_dump()
