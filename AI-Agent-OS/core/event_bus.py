"""
Central Event Bus - No circular dependencies
All communication happens through events
"""
import asyncio
from typing import Callable, Any, Dict, List
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    """All system events"""
    # Input events
    USER_COMMAND = "user_command"
    SCREEN_UPDATE = "screen_update"
    
    # Processing events
    INTENT_DETECTED = "intent_detected"
    PLAN_GENERATED = "plan_generated"
    TASK_CREATED = "task_created"
    
    # Execution events
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    ACTION_EXECUTED = "action_executed"
    
    # Memory events
    MEMORY_STORED = "memory_stored"
    MEMORY_RETRIEVED = "memory_retrieved"
    
    # System events
    ERROR_OCCURRED = "error_occurred"
    RECOVERY_ATTEMPTED = "recovery_attempted"
    SYSTEM_STATUS = "system_status"


@dataclass
class Event:
    """Immutable event"""
    type: EventType
    source: str
    data: Dict[str, Any]
    timestamp: float = None
    event_id: str = None
    
    def to_dict(self):
        return asdict(self)


class EventBus:
    """
    Central pub/sub bus - Decouples all components
    No direct imports between modules, all through events
    """
    
    def __init__(self):
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._lock = asyncio.Lock()
        self._max_history = 1000
        
    async def subscribe(self, event_type: EventType, handler: Callable) -> Callable:
        """
        Subscribe to events
        Returns: unsubscribe function
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed handler for {event_type}")
        
        # Return unsubscribe function
        return lambda: self._subscribers[event_type].remove(handler)
    
    async def emit(self, event: Event):
        """
        Emit event to all subscribers
        Thread-safe and async-safe
        """
        async with self._lock:
            # Store in history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history = self._event_history[-self._max_history:]
            
            logger.info(f"Event emitted: {event.type} from {event.source}")
        
        # Notify subscribers (non-blocking)
        if event.type in self._subscribers:
            tasks = []
            for handler in self._subscribers[event.type]:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    handler(event)
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def emit_sync(self, event_type: EventType, source: str, data: Dict):
        """Helper to emit event with auto-timestamp"""
        import time
        import uuid
        
        event = Event(
            type=event_type,
            source=source,
            data=data,
            timestamp=time.time(),
            event_id=str(uuid.uuid4())
        )
        await self.emit(event)
        return event.event_id
    
    def get_history(self, event_type: EventType = None, limit: int = 50) -> List[Event]:
        """Get event history"""
        if event_type:
            return [e for e in self._event_history if e.type == event_type][-limit:]
        return self._event_history[-limit:]
    
    async def clear_history(self):
        """Clear event history"""
        async with self._lock:
            self._event_history = []


# Global event bus instance
_global_event_bus: EventBus = None


def get_event_bus() -> EventBus:
    """Get global event bus"""
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = EventBus()
    return _global_event_bus
