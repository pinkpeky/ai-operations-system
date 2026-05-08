"""Redis 任务队列模块。

该模块封装 Redis List 队列操作，Scheduler 只依赖这里的抽象方法，便于单独测试。
"""

import json
import logging
from dataclasses import dataclass, field
from typing import Any, Protocol
from uuid import UUID

from redis.asyncio import Redis

from app.db.redis import get_redis_client

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class QueuedTask:
    """队列中的任务消息。"""

    task_id: UUID
    payload: dict[str, Any] = field(default_factory=dict)


class TaskQueue(Protocol):
    """任务队列协议，方便 Scheduler 在测试中替换 Redis。"""

    async def enqueue_task(self, task_id: UUID, payload: dict[str, Any] | None = None) -> None:
        """将任务加入队列。"""

    async def dequeue_task(self, timeout_seconds: int = 5) -> QueuedTask | None:
        """从队列取出任务。"""


class RedisQueue:
    """基于 Redis List 的 FIFO 任务队列。"""

    def __init__(self, queue_name: str, client: Redis | None = None) -> None:
        # client 可注入，单测时不需要连接真实 Redis。
        self.queue_name = queue_name
        self._client = client

    @property
    def client(self) -> Redis:
        """获取 Redis 客户端。"""

        try:
            return self._client or get_redis_client()
        except Exception as exc:
            logger.exception("Failed to get Redis queue client")
            raise RuntimeError("Redis queue client is unavailable") from exc

    async def enqueue_task(self, task_id: UUID, payload: dict[str, Any] | None = None) -> None:
        """将任务写入 Redis 队列。"""

        try:
            message = {
                "task_id": str(task_id),
                "payload": payload or {},
            }
            # ensure_ascii=False 便于后续中文任务内容在 Redis 中保持可读。
            encoded_message = json.dumps(message, ensure_ascii=False)
            await self.client.rpush(self.queue_name, encoded_message)
            logger.info("Task enqueued", extra={"task_id": str(task_id), "queue": self.queue_name})
        except Exception as exc:
            logger.exception("Failed to enqueue task", extra={"task_id": str(task_id)})
            raise RuntimeError("Failed to enqueue task") from exc

    async def dequeue_task(self, timeout_seconds: int = 5) -> QueuedTask | None:
        """从 Redis 队列阻塞式取出任务。"""

        try:
            result = await self.client.blpop(self.queue_name, timeout=timeout_seconds)
            if result is None:
                logger.debug("No task dequeued", extra={"queue": self.queue_name})
                return None

            _, raw_message = result
            message_text = raw_message.decode("utf-8") if isinstance(raw_message, bytes) else raw_message
            message = json.loads(message_text)
            queued_task = QueuedTask(
                task_id=UUID(message["task_id"]),
                payload=dict(message.get("payload") or {}),
            )
            logger.info("Task dequeued", extra={"task_id": str(queued_task.task_id)})
            return queued_task
        except Exception as exc:
            logger.exception("Failed to dequeue task", extra={"queue": self.queue_name})
            raise RuntimeError("Failed to dequeue task") from exc
