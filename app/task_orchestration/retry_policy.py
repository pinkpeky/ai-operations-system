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
        "permission",
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

    def category_for_error(self, error: str | None) -> str:
        """Classify failures for diagnostics."""

        normalized = (error or "").lower()
        if not normalized:
            return "unknown"
        if any(marker in normalized for marker in ("approval", "cancelled")):
            return "approval"
        if any(marker in normalized for marker in self.NON_RETRYABLE_MARKERS):
            return "validation"
        if any(marker in normalized for marker in ("timeout", "temporar", "connection", "network", "unreachable", "rate limit")):
            return "temporary"
        if "browser" in normalized or "worker" in normalized:
            return "worker_runtime"
        return "execution"

    def suggested_action_for_error(self, *, error: str | None, recoverable: bool) -> str:
        """Return a human-readable next action for Admin Dashboard."""

        category = self.category_for_error(error)
        if recoverable:
            return "Retry or recover the task after confirming the dependency is healthy."
        if category == "approval":
            return "Review the linked approval and create a new task if execution is still needed."
        if category == "validation":
            return "Fix the task input, source object, or workspace reference before retrying."
        return "Inspect task events and logs, then create a new task if the failure is expected."
