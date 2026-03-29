"""OpenRouter provider — multi-model gateway using OpenAI-compatible API."""

from __future__ import annotations

import os
from typing import Optional

from .openai_provider import OpenAIProvider


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter provider (wraps OpenAI-compatible API with OpenRouter base URL)."""

    def __init__(
        self,
        model: str = "anthropic/claude-sonnet-4",
        api_key: Optional[str] = None,
        api_key_env: str = "OPENROUTER_API_KEY",
    ):
        super().__init__(
            model=model,
            api_key=api_key,
            api_key_env=api_key_env,
            base_url=OPENROUTER_BASE_URL,
        )

    def name(self) -> str:
        return f"openrouter/{self.model}"

    def supports_long_context(self) -> bool:
        # Most models on OpenRouter support long context
        return True

    def validate(self) -> Optional[str]:
        api_key = self._api_key or os.environ.get("OPENROUTER_API_KEY", "")
        if not api_key:
            return "OPENROUTER_API_KEY not set"
        return None
