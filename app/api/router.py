"""API 路由聚合模块。

该模块集中挂载所有版本化 API 路由，当前 Phase 1 先提供健康检查能力。
"""

import logging

from fastapi import APIRouter

from app.api.routes.agentic_rag import router as agentic_rag_router
from app.api.routes.agents import router as agents_router
from app.api.routes.api_keys import router as api_keys_router
from app.api.routes.browser import router as browser_router
from app.api.routes.browser_runtime import router as browser_runtime_router
from app.api.routes.browser_workers import router as browser_workers_router
from app.api.routes.browser_workers import runtime_router as browser_worker_runtime_router
from app.api.routes.conversation_approvals import router as conversation_approvals_router
from app.api.routes.conversation_playbooks import router as conversation_playbooks_router
from app.api.routes.conversation_playbooks import runs_router as conversation_playbook_runs_router
from app.api.routes.conversations import router as conversations_router
from app.api.routes.documents import router as documents_router
from app.api.routes.files import router as files_router
from app.api.routes.health import router as health_router
from app.api.routes.llm import router as llm_router
from app.api.routes.memory import router as memory_router
from app.api.routes.multi_agent import router as multi_agent_router
from app.api.routes.observability import router as observability_router
from app.api.routes.openclaw import router as openclaw_router
from app.api.routes.output_artifacts import router as output_artifacts_router
from app.api.routes.planning import router as planning_router
from app.api.routes.rag import router as rag_router
from app.api.routes.rag_eval import router as rag_eval_router
from app.api.routes.reranker import router as reranker_router
from app.api.routes.task_scheduler import router as task_scheduler_router
from app.api.routes.task_runs import router as task_runs_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.tools import router as tools_router
from app.api.routes.users import router as users_router
from app.api.routes.workspaces import router as workspaces_router

logger = logging.getLogger(__name__)


def create_api_router() -> APIRouter:
    try:
        # 统一使用 /api/v1 前缀，为后续接口版本演进预留空间。
        router = APIRouter(prefix="/api/v1")
        router.include_router(agentic_rag_router)
        router.include_router(agents_router)
        router.include_router(api_keys_router)
        router.include_router(browser_router)
        router.include_router(browser_runtime_router)
        router.include_router(browser_workers_router)
        router.include_router(browser_worker_runtime_router)
        router.include_router(conversation_approvals_router)
        router.include_router(conversation_playbooks_router)
        router.include_router(conversation_playbook_runs_router)
        router.include_router(conversations_router)
        router.include_router(documents_router)
        router.include_router(files_router)
        router.include_router(health_router)
        router.include_router(llm_router)
        router.include_router(memory_router)
        router.include_router(multi_agent_router)
        router.include_router(observability_router)
        router.include_router(openclaw_router)
        router.include_router(output_artifacts_router)
        router.include_router(planning_router)
        router.include_router(rag_router)
        router.include_router(rag_eval_router)
        router.include_router(reranker_router)
        router.include_router(task_scheduler_router)
        router.include_router(task_runs_router)
        router.include_router(tasks_router)
        router.include_router(tools_router)
        router.include_router(users_router)
        router.include_router(workspaces_router)
        logger.info("API router configured")
        return router
    except Exception as exc:
        logger.exception("Failed to configure API router")
        raise RuntimeError("API router configuration failed") from exc
