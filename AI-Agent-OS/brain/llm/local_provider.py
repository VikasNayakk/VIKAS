"""Local LLM Provider - Using ollama/transformers"""
import time
import logging
from typing import Optional

from . import LLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class LocalLLMProvider(LLMProvider):
    """Local LLM using ollama or huggingface transformers"""
    
    def __init__(self, model: str = "mistral"):
        self.model = model
        self.pipeline = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize local model"""
        try:
            # Try ollama first (faster, external service)
            import requests
            self.use_ollama = True
            self.ollama_url = "http://localhost:11434"
            self._test_ollama()
        except:
            # Fallback to transformer
            try:
                from transformers import pipeline
                logger.info(f"Loading {self.model} model...")
                self.pipeline = pipeline("text-generation", model=self.model)
                self.use_ollama = False
            except Exception as e:
                logger.error(f"Could not initialize local model: {e}")
                raise
    
    def _test_ollama(self):
        """Test ollama connectivity"""
        import requests
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            response.raise_for_status()
        except:
            raise RuntimeError("Ollama not available")
    
    async def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> LLMResponse:
        """Generate response using local model"""
        start_time = time.time()
        
        try:
            if self.use_ollama:
                return await self._generate_ollama(
                    prompt, temperature, max_tokens, system_prompt
                )
            else:
                return await self._generate_transformers(
                    prompt, temperature, max_tokens, system_prompt
                )
        
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            logger.error(f"Local LLM error: {e}")
            
            return LLMResponse(
                content="",
                model=self.model,
                tokens_used=0,
                latency_ms=latency_ms,
                success=False,
                error=str(e)
            )
    
    async def _generate_ollama(
        self, prompt, temperature, max_tokens, system_prompt
    ) -> LLMResponse:
        """Generate using ollama"""
        import requests
        import aiohttp
        
        start_time = time.time()
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "temperature": temperature,
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                response_text = ""
                async for line in resp.content:
                    import json
                    data = json.loads(line)
                    response_text += data.get("response", "")
                
                latency_ms = (time.time() - start_time) * 1000
                
                return LLMResponse(
                    content=response_text,
                    model=self.model,
                    tokens_used=len(response_text.split()),
                    latency_ms=latency_ms,
                    success=True
                )
    
    async def _generate_transformers(
        self, prompt, temperature, max_tokens, system_prompt
    ) -> LLMResponse:
        """Generate using transformers"""
        start_time = time.time()
        
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        result = self.pipeline(
            full_prompt,
            max_length=max_tokens,
            temperature=temperature,
            do_sample=True,
            top_p=0.9
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        return LLMResponse(
            content=result[0]['generated_text'],
            model=self.model,
            tokens_used=len(result[0]['generated_text'].split()),
            latency_ms=latency_ms,
            success=True
        )
    
    async def health_check(self) -> bool:
        """Check local model availability"""
        if self.use_ollama:
            try:
                import requests
                response = requests.get(
                    f"{self.ollama_url}/api/tags",
                    timeout=2
                )
                return response.status_code == 200
            except:
                return False
        else:
            return self.pipeline is not None
