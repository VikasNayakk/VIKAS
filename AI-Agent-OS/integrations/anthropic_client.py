"""
Anthropic Claude integration for AI-Agent-OS.

Loads ANTHROPIC_API_KEY from environment / .env file.
Never hardcode the key here.

Usage:
    from integrations.anthropic_client import ClaudeClient
    claude = ClaudeClient()
    print(claude.ask("Hello, who are you?"))
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore

try:
    from anthropic import Anthropic
except ImportError:  # pragma: no cover
    Anthropic = None  # type: ignore


_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_env() -> None:
    """Load .env from project root if python-dotenv is installed."""
    if load_dotenv is None:
        return
    env_path = _PROJECT_ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)


class ClaudeClient:
    """Thin wrapper around the official anthropic SDK."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> None:
        _load_env()

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "").strip()
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-5").strip()
        self.max_tokens = max_tokens

        if not self.api_key or self.api_key.startswith("PASTE_"):
            raise RuntimeError(
                "ANTHROPIC_API_KEY is missing. Set it in the .env file "
                "(AI-Agent-OS/.env) or as a system environment variable. "
                "Get the full key from https://console.anthropic.com/settings/keys"
            )

        if not self.api_key.startswith("sk-ant-"):
            raise RuntimeError(
                "ANTHROPIC_API_KEY does not look like a real key "
                "(must start with 'sk-ant-...'). Did you paste the partial hint?"
            )

        if Anthropic is None:
            raise RuntimeError(
                "The 'anthropic' package is not installed. Run:\n"
                "    pip install anthropic python-dotenv"
            )

        self._client = Anthropic(api_key=self.api_key)

    def ask(self, prompt: str, system: Optional[str] = None) -> str:
        """Send a single user prompt and return the text response."""
        kwargs = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system

        msg = self._client.messages.create(**kwargs)
        # Concatenate any text blocks
        return "".join(
            block.text for block in msg.content if getattr(block, "type", "") == "text"
        )


if __name__ == "__main__":
    client = ClaudeClient()
    print(client.ask("Say hello in one short sentence."))
