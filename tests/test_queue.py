"""Redis Queue 测试模块。

该模块使用内存假 Redis 验证队列编码和解码逻辑，不依赖真实 Redis 服务。
"""

from uuid import uuid4

import pytest

from app.services.queue import QueuedTask, RedisQueue


class FakeRedis:
    """用于测试的最小 Redis 替身。"""

    def __init__(self) -> None:
        self.items: list[str] = []

    async def rpush(self, queue_name: str, message: str) -> None:
        """模拟 Redis rpush。"""

        self.items.append(message)

    async def blpop(self, queue_name: str, timeout: int = 5) -> tuple[str, str] | None:
        """模拟 Redis blpop。"""

        if not self.items:
            return None
        return queue_name, self.items.pop(0)


@pytest.mark.asyncio
async def test_redis_queue_enqueue_and_dequeue() -> None:
    """队列应能写入并读出同一个任务 ID。"""

    fake_redis = FakeRedis()
    queue = RedisQueue("test:tasks", client=fake_redis)  # type: ignore[arg-type]
    task_id = uuid4()

    await queue.enqueue_task(task_id, {"task_type": "publish"})
    result = await queue.dequeue_task(timeout_seconds=1)

    assert isinstance(result, QueuedTask)
    assert result.task_id == task_id
    assert result.payload["task_type"] == "publish"
