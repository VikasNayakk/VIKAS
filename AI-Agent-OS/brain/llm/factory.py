"""LLM provider factory for AI-Agent-OS."""
from typing import Any

from .local_provider import LocalLLMProvider
from .gemini_provider import GeminiProvider


def create_llm_provider(config: Any):
    """Create the configured LLM provider."""
    provider_name = config.get("llm.provider", "openai")

    # If Gemini is configured and no explicit provider override is set,
    # prefer Gemini for searches and generation.
    if provider_name == "openai" and config.get("llm.gemini_api_key"):
        provider_name = "gemini"

    if provider_name == "gemini":
        return GeminiProvider(
            api_key=config.get("llm.gemini_api_key"),
            project_id=config.get("llm.gemini_project_id"),
            model=config.get("llm.gemini_model", "gemini-flash-latest")
        )

    if provider_name == "local":
        return LocalLLMProvider(model=config.get("llm.local_model", "mistral"))

    try:
        from .openai_provider import OpenAIProvider
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI provider is not available because the 'openai' package is missing. "
            "Install it with 'pip install openai' or switch the config provider to 'gemini' or 'local'."
        ) from exc

    return OpenAIProvider(
        api_key=config.get("llm.openai_api_key"),
        model=config.get("llm.openai_model", "gpt-4")
    )
