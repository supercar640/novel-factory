"""Ollama provider — local models via OpenAI-compatible API."""

from __future__ import annotations

from typing import Optional

from .openai_provider import OpenAIProvider


OLLAMA_BASE_URL = "http://localhost:11434/v1"


class OllamaProvider(OpenAIProvider):
    """Ollama local model provider (OpenAI-compatible endpoint)."""

    def __init__(
        self,
        model: str = "llama3.1",
        base_url: str = OLLAMA_BASE_URL,
    ):
        super().__init__(
            model=model,
            api_key="ollama",  # Ollama doesn't require a real API key
            base_url=base_url,
        )

    def name(self) -> str:
        return f"ollama/{self.model}"

    def supports_long_context(self) -> bool:
        return False  # Depends on model, conservative default

    def validate(self) -> Optional[str]:
        # Check if Ollama is running
        try:
            import urllib.request
            req = urllib.request.Request(
                self._base_url.replace("/v1", "/api/tags"),
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    return None
        except Exception:
            pass
        return f"Ollama가 실행 중이지 않습니다 ({self._base_url}). 'ollama serve'를 실행하세요."
