"""Google (Gemini) provider implementation."""

from __future__ import annotations

import os
from typing import Optional

from .base import AIProvider, AIResponse


LONG_CONTEXT_MODELS = {
    "gemini-1.5-pro", "gemini-1.5-flash",
    "gemini-2.0-pro", "gemini-2.0-flash",
    "gemini-2.5-pro", "gemini-2.5-flash",
}


class GoogleProvider(AIProvider):
    """Google Gemini API provider."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash",
        api_key: Optional[str] = None,
        api_key_env: str = "GOOGLE_API_KEY",
    ):
        self.model = model
        self._api_key = api_key or os.environ.get(api_key_env, "")
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. "
                    "Run: pip install google-generativeai"
                )
            genai.configure(api_key=self._api_key)
            self._client = genai.GenerativeModel(self.model)
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
        try:
            import google.generativeai as genai
        except ImportError:
            raise ImportError("google-generativeai not installed")

        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        # Gemini uses system_instruction for system prompt
        model = genai.GenerativeModel(
            self.model,
            system_instruction=system_prompt,
            generation_config=generation_config,
        )
        response = model.generate_content(user_message)
        content = response.text if response.text else ""
        usage = {}
        if hasattr(response, "usage_metadata") and response.usage_metadata:
            usage = {
                "input_tokens": getattr(response.usage_metadata, "prompt_token_count", 0),
                "output_tokens": getattr(response.usage_metadata, "candidates_token_count", 0),
            }
        return AIResponse(
            content=content,
            model=self.model,
            usage=usage,
            raw={},
        )

    def name(self) -> str:
        return f"google/{self.model}"

    def supports_long_context(self) -> bool:
        return self.model in LONG_CONTEXT_MODELS

    def validate(self) -> Optional[str]:
        if not self._api_key:
            return "GOOGLE_API_KEY not set"
        return None
