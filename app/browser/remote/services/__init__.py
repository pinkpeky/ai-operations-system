"""Remote Browser Worker service exports.

The service package is imported by both the API provider layer and the worker
HTTP client. Keep exports lazy so importing a narrow utility, such as request
signing, does not pull the whole browser service stack into a circular import.
"""

from importlib import import_module
from typing import Any

__all__ = [
    "BrowserSessionCleanupService",
    "BrowserWorkerAuthService",
    "BrowserWorkerHealthService",
    "BrowserWorkerRepository",
    "BrowserWorkerSelector",
    "BrowserWorkerService",
]

_EXPORTS = {
    "BrowserSessionCleanupService": "app.browser.remote.services.browser_session_cleanup_service",
    "BrowserWorkerAuthService": "app.browser.remote.services.browser_worker_auth_service",
    "BrowserWorkerHealthService": "app.browser.remote.services.browser_worker_health_service",
    "BrowserWorkerRepository": "app.browser.remote.services.browser_worker_repository",
    "BrowserWorkerSelector": "app.browser.remote.services.browser_worker_selector",
    "BrowserWorkerService": "app.browser.remote.services.browser_worker_service",
}


def __getattr__(name: str) -> Any:
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module = import_module(_EXPORTS[name])
    value = getattr(module, name)
    globals()[name] = value
    return value
