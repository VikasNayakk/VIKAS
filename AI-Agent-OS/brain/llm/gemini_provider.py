"""Google Gemini API Provider"""
import os
import time
import logging
import aiohttp
from typing import Optional, Any, Dict

from . import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider(LLMProvider):
    """Gemini generative language provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        project_id: Optional[str] = None,
        model: str = "gemini-flash-latest"
    ):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.project_id = project_id or os.getenv("GEMINI_PROJECT_ID")
        self.model = model

    def _build_url(self) -> str:
        return f"{GEMINI_BASE_URL}/{self.model}:generateContent"

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate response from Gemini."""
        start_time = time.time()

        if not self.api_key:
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                latency_ms=0,
                success=False,
                error="Gemini API key not configured"
            )

        headers = {
            "Content-Type": "application/json",
            "X-goog-api-key": self.api_key
        }

        payload: Dict[str, Any] = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt if not system_prompt else f"{system_prompt}\n\n{prompt}"
                        }
                    ]
                }
            ]
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._build_url(),
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    body = await resp.text()

                    if resp.status != 200:
                        logger.error(f"Gemini request failed: {resp.status} {body}")
                        return LLMResponse(
                            content="",
                            model=self.model,
                            tokens_used=0,
                            latency_ms=(time.time() - start_time) * 1000,
                            success=False,
                            error=f"Gemini request failed: {resp.status}"
                        )

                    data = await resp.json()

            content = self._extract_text(data)
            latency_ms = (time.time() - start_time) * 1000

            return LLMResponse(
                content=content,
                model=self.model,
                tokens_used=len(content.split()),
                latency_ms=latency_ms,
                success=True
            )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Gemini error: {e}")
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                latency_ms=latency_ms,
                success=False,
                error=str(e)
            )

    def _extract_text(self, data: Dict[str, Any]) -> str:
        """Extract final text from Gemini response."""
        if not data:
            return ""

        candidates = data.get("candidates") or []
        if candidates:
            candidate = candidates[0]
            if isinstance(candidate, dict):
                if "content" in candidate:
                    return candidate.get("content", "")
                if "output" in candidate:
                    output = candidate.get("output")
                    if isinstance(output, list) and output:
                        first = output[0]
                        if isinstance(first, dict) and "content" in first:
                            content_parts = first.get("content") or []
                            if isinstance(content_parts, list):
                                return "".join(
                                    str(part.get("text", "")) for part in content_parts if isinstance(part, dict)
                                )
        return ""

    async def health_check(self) -> bool:
        """Check Gemini availability."""
        response = await self.generate("Hello", temperature=0.2, max_tokens=10)
        return response.success
