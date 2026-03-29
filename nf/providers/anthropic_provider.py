"""Anthropic (Claude) provider implementation."""

from __future__ import annotations

import os
from typing import Optional

from .base import AIProvider, AIResponse


# Long-context models (128K+)
LONG_CONTEXT_MODELS = {
    "claude-opus-4-6", "claude-opus-4-20250514",
    "claude-sonnet-4-6", "claude-sonnet-4-20250514",
    "claude-haiku-4-5-20251001",
    "claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022",
}


class AnthropicProvider(AIProvider):
    """Anthropic Claude API provider."""

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        api_key: Optional[str] = None,
        api_key_env: str = "ANTHROPIC_API_KEY",
    ):
        self.model = model
        self._api_key = api_key or os.environ.get(api_key_env, "")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. Run: pip install anthropic"
                )
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AIResponse:
        client = self._get_client()
        response = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        content = response.content[0].text if response.content else ""
        usage = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
        return AIResponse(
            content=content,
            model=response.model,
            usage=usage,
            raw=response.model_dump() if hasattr(response, "model_dump") else {},
        )

    def name(self) -> str:
        return f"anthropic/{self.model}"

    def supports_long_context(self) -> bool:
        return self.model in LONG_CONTEXT_MODELS

    def validate(self) -> Optional[str]:
        if not self._api_key:
            return "ANTHROPIC_API_KEY not set"
        return None
