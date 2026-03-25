"""Circuit Breaker for API calls - Prevents cascading failures"""
import time
import asyncio
import logging
from enum import Enum
from typing import Callable, Any

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject all calls
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """Circuit Breaker Pattern - Prevents cascading failures"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        name: str = "circuit_breaker"
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        self.last_check_time = time.time()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Call function through circuit breaker"""
        
        # Check if should attempt recovery
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                logger.info(f"{self.name}: Moving to HALF_OPEN state")
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
            else:
                raise RuntimeError(f"Circuit breaker {self.name} is OPEN")
        
        # Try to execute
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Success
            self.failure_count = 0
            
            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= 2:  # Need 2 successes to close
                    logger.info(f"{self.name}: Recovered, moving to CLOSED state")
                    self.state = CircuitState.CLOSED
            
            return result
        
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            logger.error(f"{self.name}: Failed ({self.failure_count}/{self.failure_threshold}): {e}")
            
            if self.failure_count >= self.failure_threshold:
                logger.warning(f"{self.name}: Opening circuit after {self.failure_count} failures")
                self.state = CircuitState.OPEN
            
            raise
    
    def get_status(self) -> dict:
        """Get circuit status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time
        }
