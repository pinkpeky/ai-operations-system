"""Prompt 管理服务模块。

该模块负责 system prompt、user prompt 和模板变量的组合渲染，避免 Provider 层关心提示词拼装细节。
"""

import logging
from collections.abc import Mapping
from typing import Any

from app.agents.providers.base import LLMPrompt

logger = logging.getLogger(__name__)


class PromptManager:
    """Prompt 渲染管理器。"""

    def build_prompt(
        self,
        system_prompt: str | None,
        user_prompt: str | None,
        template: str | None = None,
        variables: Mapping[str, Any] | None = None,
    ) -> LLMPrompt:
        """构建最终传给 Provider 的 Prompt。"""

        try:
            rendered_user_prompt = self._render_user_prompt(
                user_prompt=user_prompt,
                template=template,
                variables=variables,
            )
            normalized_system_prompt = self._normalize_optional_prompt(system_prompt)

            if not rendered_user_prompt.strip():
                raise ValueError("Rendered user prompt cannot be empty")

            full_prompt = self._compose_full_prompt(
                system_prompt=normalized_system_prompt,
                user_prompt=rendered_user_prompt,
            )
            logger.info(
                "Prompt rendered",
                extra={
                    "has_system_prompt": normalized_system_prompt is not None,
                    "has_template": bool(template),
                },
            )
            return LLMPrompt(
                system_prompt=normalized_system_prompt,
                user_prompt=rendered_user_prompt,
                full_prompt=full_prompt,
            )
        except ValueError:
            logger.exception("Prompt validation failed")
            raise
        except Exception as exc:
            logger.exception("Prompt rendering failed")
            raise RuntimeError("Prompt rendering failed") from exc

    def _render_user_prompt(
        self,
        user_prompt: str | None,
        template: str | None,
        variables: Mapping[str, Any] | None,
    ) -> str:
        """渲染用户 Prompt，模板中可通过 {user_prompt} 引用原始用户输入。"""

        raw_user_prompt = user_prompt or ""
        if not template:
            return raw_user_prompt

        render_variables = dict(variables or {})
        render_variables.setdefault("user_prompt", raw_user_prompt)

        try:
            return template.format(**render_variables)
        except KeyError as exc:
            missing_key = str(exc).strip("'")
            raise ValueError(f"Missing prompt template variable: {missing_key}") from exc
        except Exception as exc:
            raise ValueError("Invalid prompt template") from exc

    def _compose_full_prompt(self, system_prompt: str | None, user_prompt: str) -> str:
        """组合 system 和 user 两段 Prompt，保留清晰边界便于后续 Provider 适配。"""

        if system_prompt is None:
            return user_prompt
        return f"System:\n{system_prompt}\n\nUser:\n{user_prompt}"

    def _normalize_optional_prompt(self, prompt: str | None) -> str | None:
        """将空白可选 Prompt 统一视为未提供。"""

        if prompt is None:
            return None
        normalized = prompt.strip()
        return normalized or None
