"""Phase 42 task retry policy tests."""

from __future__ import annotations

from app.task_orchestration.retry_policy import TaskRetryPolicy


def test_task_retry_policy_uses_backoff_and_non_retryable_errors() -> None:
    policy = TaskRetryPolicy(base_delay_seconds=2, max_delay_seconds=30)

    assert policy.should_retry(error="temporary network timeout", retry_count=0, max_retries=3) is True
    assert policy.should_retry(error="approval rejected by reviewer", retry_count=0, max_retries=3) is False
    assert policy.should_retry(error="temporary network timeout", retry_count=3, max_retries=3) is False
    assert policy.next_delay_seconds(0) == 2
    assert policy.next_delay_seconds(2) == 8
