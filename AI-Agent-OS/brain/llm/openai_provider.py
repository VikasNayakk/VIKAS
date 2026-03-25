"""OpenAI API Provider"""
import os
import time
import logging
from typing import Optional
import openai

from . import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        self.model = model
        
        if self.api_key:
            openai.api_key = self.api_key
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate response from OpenAI"""
        start_time = time.time()
        
        if not self.api_key:
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                latency_ms=0,
                success=False,
                error="OpenAI API key not configured"
            )
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            latency_ms = (time.time() - start_time) * 1000
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self.model,
                tokens_used=response.usage.total_tokens,
                latency_ms=latency_ms,
                success=True
            )
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"OpenAI error: {e}")
            
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                latency_ms=latency_ms,
                success=False,
                error=str(e)
            )
    
    async def health_check(self) -> bool:
        """Check OpenAI API availability"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=10
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI health check failed: {e}")
            return False
