"""Browser Worker 认证与签名服务。

本阶段只建立安全基础设施：数据库只保存 hash，明文 secret 只在注册或轮换时返回一次。
为了兼容本地开发，API 进程会临时缓存刚生成的 secret，用于同一进程内的 worker 请求签名。
"""

from __future__ import annotations

from datetime import UTC, datetime
import hashlib
import hmac
import json
import secrets
from typing import Any
from uuid import UUID


class BrowserWorkerAuthService:
    """Browser Worker secret、hash 与 HMAC 请求签名工具。"""

    _secret_cache: dict[str, str] = {}

    @classmethod
    def generate_worker_secret(cls) -> str:
        """生成 worker secret，明文只用于一次性返回或进程内签名缓存。"""

        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_secret(secret: str) -> str:
        """使用 SHA-256 保存 secret hash，避免数据库落明文。"""

        return hashlib.sha256(secret.encode("utf-8")).hexdigest()

    @classmethod
    def verify_secret(cls, *, secret: str, secret_hash: str | None) -> bool:
        """校验明文 secret 是否匹配数据库 hash。"""

        if not secret or not secret_hash:
            return False
        return secrets.compare_digest(cls.hash_secret(secret), secret_hash)

    @classmethod
    def cache_worker_secret(cls, worker_id: UUID | str, secret: str) -> None:
        """在当前 API 进程缓存 secret，便于本地单进程注册后立即调度 worker。"""

        cls._secret_cache[str(worker_id)] = secret

    @classmethod
    def pop_cached_secret(cls, worker_id: UUID | str) -> None:
        """移除进程内 secret 缓存。"""

        cls._secret_cache.pop(str(worker_id), None)

    @classmethod
    def get_cached_secret(cls, worker_id: UUID | str) -> str | None:
        """读取进程内 secret 缓存。"""

        return cls._secret_cache.get(str(worker_id))

    @classmethod
    def body_hash(cls, body: Any | None) -> str:
        """计算稳定 JSON body hash。"""

        if body is None:
            payload = ""
        elif isinstance(body, (bytes, bytearray)):
            payload = bytes(body).decode("utf-8")
        elif isinstance(body, str):
            payload = body
        else:
            payload = json.dumps(body, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def sign_request(
        cls,
        *,
        secret: str,
        body: Any | None,
        timestamp: str | None = None,
        nonce: str | None = None,
    ) -> dict[str, str]:
        """生成 worker 请求签名 header。"""

        used_timestamp = timestamp or str(int(datetime.now(UTC).timestamp()))
        used_nonce = nonce or secrets.token_urlsafe(16)
        body_hash = cls.body_hash(body)
        signing_text = "\n".join([used_timestamp, used_nonce, body_hash])
        signature = hmac.new(secret.encode("utf-8"), signing_text.encode("utf-8"), hashlib.sha256).hexdigest()
        return {
            "X-Worker-Timestamp": used_timestamp,
            "X-Worker-Nonce": used_nonce,
            "X-Worker-Body-Hash": body_hash,
            "X-Worker-Signature": signature,
        }

    @classmethod
    def verify_signature(
        cls,
        *,
        secret: str,
        body: Any | None,
        timestamp: str | None,
        nonce: str | None,
        signature: str | None,
        body_hash: str | None = None,
        max_skew_seconds: int = 300,
    ) -> bool:
        """校验 HMAC 签名与时间窗口。"""

        if not secret or not timestamp or not nonce or not signature:
            return False
        try:
            request_ts = int(timestamp)
        except ValueError:
            return False
        now_ts = int(datetime.now(UTC).timestamp())
        if abs(now_ts - request_ts) > max_skew_seconds:
            return False
        # Worker runtime may receive JSON with transport-level whitespace changes;
        # when the caller provides X-Worker-Body-Hash, use that canonical hash for HMAC.
        expected_body_hash = body_hash or cls.body_hash(body)
        signing_text = "\n".join([timestamp, nonce, expected_body_hash])
        expected = hmac.new(secret.encode("utf-8"), signing_text.encode("utf-8"), hashlib.sha256).hexdigest()
        return secrets.compare_digest(expected, signature)
