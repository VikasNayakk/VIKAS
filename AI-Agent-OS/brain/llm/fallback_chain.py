"""Fallback Chain - Try multiple models if one fails"""
import logging
import asyncio
from typing import List, Optional

from . import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class FallbackChain:
    """
    Try providers in sequence until one succeeds
    Primary → Secondary → Tertiary
    """
    
    def __init__(self, providers: List[LLMProvider], name: str = "chain"):
        self.providers = providers
        self.name = name
        self.provider_stats = {
            i: {"attempts": 0, "successes": 0, "failures": 0}
            for i in range(len(providers))
        }
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Try providers in order until success"""
        
        last_error = None
        
        for idx, provider in enumerate(self.providers):
            try:
                logger.info(f"Trying provider {idx} ({provider.__class__.__name__})...")
                
                self.provider_stats[idx]["attempts"] += 1
                
                response = await provider.generate(
                    prompt=prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    system_prompt=system_prompt
                )
                
                if response.success:
                    self.provider_stats[idx]["successes"] += 1
                    logger.info(f"Provider {idx} succeeded")
                    return response
                else:
                    last_error = response.error
                    self.provider_stats[idx]["failures"] += 1
                    logger.warning(f"Provider {idx} failed: {response.error}")
            
            except Exception as e:
                last_error = str(e)
                self.provider_stats[idx]["failures"] += 1
                logger.warning(f"Provider {idx} exception: {e}")
                continue
        
        # All providers failed
        logger.error(f"All {len(self.providers)} providers failed")
        
        return LLMResponse(
            content="",
            model="fallback_chain",
            tokens_used=0,
            latency_ms=0,
            success=False,
            error=f"All providers failed. Last error: {last_error}"
        )
    
    async def health_check(self) -> dict:
        """Check health of all providers"""
        results = {}
        
        for idx, provider in enumerate(self.providers):
            try:
                health = await provider.health_check()
                results[idx] = {
                    "provider": provider.__class__.__name__,
                    "healthy": health
                }
            except Exception as e:
                results[idx] = {
                    "provider": provider.__class__.__name__,
                    "healthy": False,
                    "error": str(e)
                }
        
        return results
    
    def get_stats(self) -> dict:
        """Get provider statistics"""
        return {
            "chain": self.name,
            "providers": self.provider_stats
        }
