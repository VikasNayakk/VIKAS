"""Response Cache - Cache LLM responses to avoid duplicate calls"""
import hashlib
import json
import logging
import time
from typing import Optional, Dict, Any

from . import LLMResponse

logger = logging.getLogger(__name__)


class ResponseCache:
    """
    Cache LLM responses by prompt hash
    Reduces API calls and latency
    """
    
    def __init__(self, ttl: int = 3600, max_size: int = 1000):
        self.ttl = ttl  # Time to live in seconds
        self.max_size = max_size
        self._cache: Dict[str, tuple] = {}  # hash -> (response, timestamp)
    
    def _hash_key(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Create cache key from prompt"""
        key = f"{system_prompt}||{prompt}"
        return hashlib.sha256(key.encode()).hexdigest()
    
    def get(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> Optional[LLMResponse]:
        """Get cached response if available and not expired"""
        
        key = self._hash_key(prompt, system_prompt)
        
        if key not in self._cache:
            return None
        
        response, timestamp = self._cache[key]
        
        # Check if expired
        if time.time() - timestamp > self.ttl:
            del self._cache[key]
            return None
        
        logger.debug(f"Cache hit for prompt (age: {time.time() - timestamp:.1f}s)")
        return response
    
    def set(
        self,
        prompt: str,
        response: LLMResponse,
        system_prompt: Optional[str] = None
    ):
        """Cache response"""
        
        # Cleanup old entries if cache is full
        if len(self._cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k][1])
            del self._cache[oldest_key]
            logger.debug("Cache full, removed oldest entry")
        
        key = self._hash_key(prompt, system_prompt)
        self._cache[key] = (response, time.time())
        logger.debug(f"Cached response (cache size: {len(self._cache)})")
    
    def clear(self):
        """Clear all cache"""
        self._cache.clear()
        logger.info("Cache cleared")
    
    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self._cache),
            "max_size": self.max_size,
            "ttl": self.ttl
        }
