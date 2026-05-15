"""Retry policy for Phase 42 task orchestration."""

from __future__ import annotations


class TaskRetryPolicy:
    """Small deterministic retry policy for background task runs."""

    TEMPORARY_MARKERS = (
        "timeout",
        "temporar",
        "connection",
        "network",
        "unreachable",
        "rate limit",
        "worker",
        "browser",
    )
    NON_RETRYABLE_MARKERS = (
        "approval rejected",
        "approval cancelled",
        "validation",
        "not found",
        "does not belong",
        "not executable",
    )

    def __init__(self, *, base_delay_seconds: int = 5, max_delay_seconds: int = 300) -> None:
        self.base_delay_seconds = base_delay_seconds
        self.max_delay_seconds = max_delay_seconds

    def next_delay_seconds(self, retry_count: int) -> int:
        """Return exponential backoff delay for the next retry."""

        return min(self.max_delay_seconds, self.base_delay_seconds * (2 ** max(0, retry_count)))

    def should_retry(self, *, error: str | None, retry_count: int, max_retries: int) -> bool:
        """Return whether a failure is retryable."""

        if retry_count >= max_retries:
            return False
        normalized = (error or "").lower()
        if any(marker in normalized for marker in self.NON_RETRYABLE_MARKERS):
            return False
        if not normalized:
            return True
        return any(marker in normalized for marker in self.TEMPORARY_MARKERS)
