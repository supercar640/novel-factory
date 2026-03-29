"""AI Provider base class — all providers implement this interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AIResponse:
    """Standardized response from any AI provider."""
    content: str
    model: str
    usage: dict = field(default_factory=dict)  # {"input_tokens": N, "output_tokens": N}
    raw: dict = field(default_factory=dict)     # Provider-specific raw response


class AIProvider(ABC):
    """Abstract base class for all AI providers.

    Each provider wraps a specific API (OpenAI, Anthropic, Google, etc.)
    and exposes a uniform generate() interface.
    """

    @abstractmethod
    def generate(
        self,
        system_prompt: str,
        user_message: str,
        *,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AIResponse:
        """Generate text from a system prompt + user message."""
        ...

    @abstractmethod
    def name(self) -> str:
        """Provider/model identifier (e.g., 'anthropic/claude-sonnet-4-20250514')."""
        ...

    def supports_long_context(self) -> bool:
        """Whether this provider supports 128K+ token context."""
        return False

    def validate(self) -> Optional[str]:
        """Check if the provider is correctly configured.

        Returns None if valid, or an error message string.
        """
        return None
