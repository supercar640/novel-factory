"""OpenAI (GPT) provider implementation."""

from __future__ import annotations

import os
from typing import Optional

from .base import AIProvider, AIResponse


LONG_CONTEXT_MODELS = {
    "gpt-4o", "gpt-4o-2024-11-20", "gpt-4o-mini",
    "gpt-4-turbo", "gpt-4-turbo-2024-04-09",
    "o1", "o1-mini", "o1-preview", "o3", "o3-mini", "o4-mini",
}


class OpenAIProvider(AIProvider):
    """OpenAI API provider (GPT-4o, o1, etc.)."""

    def __init__(
        self,
        model: str = "gpt-4o",
        api_key: Optional[str] = None,
        api_key_env: str = "OPENAI_API_KEY",
        base_url: Optional[str] = None,
    ):
        self.model = model
        self._api_key = api_key or os.environ.get(api_key_env, "")
        self._base_url = base_url
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import openai
            except ImportError:
                raise ImportError(
                    "openai package not installed. Run: pip install openai"
                )
            kwargs = {"api_key": self._api_key}
            if self._base_url:
                kwargs["base_url"] = self._base_url
            self._client = openai.OpenAI(**kwargs)
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
        # o1/o3 models don't support system messages or temperature
        is_reasoning = self.model.startswith(("o1", "o3", "o4"))
        messages = []
        if is_reasoning:
            messages.append({
                "role": "user",
                "content": f"{system_prompt}\n\n---\n\n{user_message}",
            })
        else:
            messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_message})

        kwargs = {
            "model": self.model,
            "messages": messages,
        }
        if not is_reasoning:
            kwargs["temperature"] = temperature
            kwargs["max_tokens"] = max_tokens
        else:
            kwargs["max_completion_tokens"] = max_tokens

        response = client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        content = choice.message.content or ""
        usage = {}
        if response.usage:
            usage = {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
            }
        return AIResponse(
            content=content,
            model=response.model,
            usage=usage,
            raw=response.model_dump() if hasattr(response, "model_dump") else {},
        )

    def name(self) -> str:
        return f"openai/{self.model}"

    def supports_long_context(self) -> bool:
        return self.model in LONG_CONTEXT_MODELS

    def validate(self) -> Optional[str]:
        if not self._api_key:
            return "OPENAI_API_KEY not set"
        return None
