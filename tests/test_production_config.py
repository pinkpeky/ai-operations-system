"""Production configuration guardrail tests."""

import pytest

from app.core.config import ProductionConfigError, Settings


def formal_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "_env_file": None,
        "APP_ENV": "production",
        "PRODUCTION_CONFIG_STRICT": True,
        "POSTGRES_PASSWORD": "postgres-secret-value-32",
        "REDIS_PASSWORD": "redis-secret-value-32",
        "QDRANT_API_KEY": "qdrant-secret-value-32",
        "LLM_PROVIDER": "local",
        "LOCAL_LLM_BASE_URL": "http://127.0.0.1:11434",
        "LOCAL_LLM_MODEL": "qwen2.5:14b",
        "EMBEDDING_PROVIDER": "local",
        "LOCAL_EMBEDDING_BASE_URL": "http://127.0.0.1:11434",
        "LOCAL_EMBEDDING_MODEL": "bge-m3",
        "RERANKER_PROVIDER": "local",
        "LOCAL_RERANKER_BASE_URL": "http://127.0.0.1:8002",
        "LOCAL_RERANKER_MODEL": "bge-m3-embedding-reranker",
        "LOCAL_RERANKER_ALLOW_FALLBACK": False,
        "BROWSER_PROVIDER": "remote",
        "BROWSER_WORKER_AUTH_ENABLED": True,
        "BROWSER_WORKER_AUTH_STRICT": True,
        "BROWSER_WORKER_SHARED_SECRET": "browser-worker-shared-secret-value-32",
        "BROWSER_ALLOWED_DOMAINS": "douyin.com,v.douyin.com,open.douyin.com",
        "BROWSER_ALLOW_EXTERNAL_DOMAINS": False,
        "CORS_ALLOWED_ORIGINS": "https://client.example.cn",
        "OPENCLAW_ENABLED": True,
        "OPENCLAW_PROVIDER": "worker_runtime",
        "WORKER_CLIENT_OPENCLAW_ENABLED": True,
        "WORKER_CLIENT_OPENCLAW_PROVIDER": "openclaw_http",
        "WORKER_CLIENT_OPENCLAW_BASE_URL": "http://127.0.0.1:17900",
        "WORKER_CLIENT_OPENCLAW_API_KEY": "openclaw-adapter-secret-value-32",
        "COMFYUI_RUNTIME_PROVIDER": "guarded",
        "COMFYUI_RUNTIME_ENABLED": True,
        "COMFYUI_RUNTIME_BASE_URL": "http://127.0.0.1:8188",
        "COMFYUI_RUNTIME_ALLOW_NETWORK": True,
        "COMFYUI_RUNTIME_ALLOWED_HOSTS": "127.0.0.1,localhost",
        "COMFYUI_RUNTIME_PROMPT_SUBMISSION_ENABLED": True,
        "COMFYUI_RUNTIME_ALLOWED_EXECUTION_PATHS": "/prompt,/history,/queue",
        "DIGITAL_HUMAN_ENABLED": True,
        "DIGITAL_HUMAN_PROVIDER": "local_musetalk_liveportrait",
        "DIGITAL_HUMAN_ALLOW_EXTERNAL_API": False,
    }
    values.update(overrides)
    return Settings(**values)


def finding_keys(settings: Settings) -> set[str]:
    return {item["key"] for item in settings.production_config_findings()}


def test_formal_production_config_has_no_blocking_findings() -> None:
    settings = formal_settings()

    findings = settings.production_config_findings()

    assert [item for item in findings if item["severity"] == "error"] == []


def test_production_config_flags_mock_runtime_values() -> None:
    settings = formal_settings(
        POSTGRES_PASSWORD="change_me",
        RERANKER_PROVIDER="mock",
        BROWSER_PROVIDER="mock",
        BROWSER_WORKER_AUTH_STRICT=False,
        BROWSER_ALLOWED_DOMAINS="example.com,localhost,127.0.0.1",
        OPENCLAW_PROVIDER="mock",
        WORKER_CLIENT_OPENCLAW_PROVIDER="mock",
        WORKER_CLIENT_OPENCLAW_BASE_URL="",
        WORKER_CLIENT_OPENCLAW_API_KEY="",
    )

    keys = finding_keys(settings)

    assert {
        "POSTGRES_PASSWORD",
        "RERANKER_PROVIDER",
        "BROWSER_PROVIDER",
        "BROWSER_WORKER_AUTH_STRICT",
        "BROWSER_ALLOWED_DOMAINS",
        "OPENCLAW_PROVIDER",
        "WORKER_CLIENT_OPENCLAW_PROVIDER",
    }.issubset(keys)


def test_production_config_rejects_incomplete_worker_openclaw_http_provider() -> None:
    settings = formal_settings(
        WORKER_CLIENT_OPENCLAW_PROVIDER="openclaw_http",
        WORKER_CLIENT_OPENCLAW_BASE_URL="",
        WORKER_CLIENT_OPENCLAW_API_KEY="change_me",
    )

    keys = finding_keys(settings)

    assert "WORKER_CLIENT_OPENCLAW_BASE_URL" in keys
    assert "WORKER_CLIENT_OPENCLAW_API_KEY" in keys


def test_production_config_rejects_local_reranker_fallback() -> None:
    settings = formal_settings(LOCAL_RERANKER_ALLOW_FALLBACK=True)

    assert "LOCAL_RERANKER_ALLOW_FALLBACK" in finding_keys(settings)


def test_non_production_requires_explicit_production_when_requested() -> None:
    settings = formal_settings(APP_ENV="staging")

    assert settings.production_config_findings() == []
    assert finding_keys(settings) == set()
    assert settings.production_config_findings(require_production=True)[0]["key"] == "APP_ENV"


def test_strict_production_config_raises_on_errors() -> None:
    settings = formal_settings(BROWSER_PROVIDER="mock")

    with pytest.raises(ProductionConfigError) as exc_info:
        settings.raise_for_production_config()

    assert exc_info.value.findings[0]["key"] == "BROWSER_PROVIDER"
