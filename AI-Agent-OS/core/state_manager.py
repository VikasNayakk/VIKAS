"""
Event-Sourced State Manager
All state changes are immutable events
Prevents race conditions using versioning
"""
import asyncio
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class StateEvent:
    """Immutable state event"""
    event_id: str
    version: int
    timestamp: datetime
    path: str  # e.g., "agent.executor.status"
    old_value: Any
    new_value: Any
    source: str  # which agent/component made change
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'version': self.version,
            'timestamp': self.timestamp.isoformat(),
            'path': self.path,
            'old_value': str(self.old_value),
            'new_value': str(self.new_value),
            'source': self.source
        }


class StateManager:
    """
    Event-sourced state with versioning
    - Thread-safe (async)
    - Supports rollback
    - Immutable event log
    """
    
    def __init__(self):
        self._state: Dict[str, Any] = {}
        self._event_log: List[StateEvent] = []
        self._version = 0
        self._lock = asyncio.Lock()
        self._snapshots: Dict[int, Dict] = {}  # version -> state
        self._max_events = 10000
        
    async def set_state(self, path: str, value: Any, source: str = "system") -> int:
        """
        Set state at path (e.g., "agent.status" = "running")
        Returns: new version number
        """
        async with self._lock:
            import uuid
            
            # Get old value
            old_value = self._get_nested(self._state, path)
            
            # Set new value
            self._set_nested(self._state, path, value)
            self._version += 1
            
            # Create event
            event = StateEvent(
                event_id=str(uuid.uuid4()),
                version=self._version,
                timestamp=datetime.now(),
                path=path,
                old_value=old_value,
                new_value=value,
                source=source
            )
            
            self._event_log.append(event)
            
            # Cleanup old events
            if len(self._event_log) > self._max_events:
                # Keep recent 5000 events
                self._event_log = self._event_log[-5000:]
            
            logger.debug(f"State changed: {path} = {value} (v{self._version})")
            return self._version
    
    async def get_state(self, path: str = None) -> Any:
        """Get state at path"""
        async with self._lock:
            if path is None:
                return self._state.copy()
            return self._get_nested(self._state, path)
    
    async def get_version(self) -> int:
        """Get current state version"""
        async with self._lock:
            return self._version
    
    async def create_snapshot(self) -> int:
        """Create snapshot at current version"""
        async with self._lock:
            self._snapshots[self._version] = self._state.copy()
            logger.info(f"Snapshot created at version {self._version}")
            return self._version
    
    async def rollback_to_version(self, version: int) -> bool:
        """Rollback to specific version"""
        async with self._lock:
            if version not in self._snapshots:
                logger.error(f"No snapshot at version {version}")
                return False
            
            self._state = self._snapshots[version].copy()
            self._version = version
            logger.warning(f"Rolled back to version {version}")
            return True
    
    async def rollback_events(self, count: int) -> bool:
        """Rollback last N events"""
        async with self._lock:
            if count > len(self._event_log):
                return False
            
            # Re-apply all events except last N
            events_to_keep = self._event_log[:-count]
            
            # Rebuild state
            self._state = {}
            for event in events_to_keep:
                self._set_nested(self._state, event.path, event.new_value)
            
            self._version = len(events_to_keep)
            self._event_log = events_to_keep
            
            logger.warning(f"Rolled back {count} events")
            return True
    
    async def get_event_log(self, start: int = None, end: int = None) -> List[StateEvent]:
        """Get event log range"""
        async with self._lock:
            if start is None:
                start = 0
            if end is None:
                end = len(self._event_log)
            
            return self._event_log[start:end]
    
    def _get_nested(self, obj: Dict, path: str) -> Any:
        """Get value from nested dict using dot notation"""
        parts = path.split('.')
        current = obj
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        return current
    
    def _set_nested(self, obj: Dict, path: str, value: Any):
        """Set value in nested dict using dot notation"""
        parts = path.split('.')
        current = obj
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
    
    async def export_state(self) -> Dict:
        """Export current state for debugging"""
        async with self._lock:
            return {
                'version': self._version,
                'state': self._state.copy(),
                'event_count': len(self._event_log),
                'snapshot_count': len(self._snapshots)
            }
