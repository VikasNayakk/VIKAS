"""
AI-Agent-OS Kernel
Main event loop and component orchestration
"""
import asyncio
import logging
from typing import Optional, List
from .event_bus import EventBus, EventType, get_event_bus
from .state_manager import StateManager

logger = logging.getLogger(__name__)


class Kernel:
    """
    Central kernel - Manages event loop, lifecycle, and resource cleanup
    """
    
    def __init__(self):
        self.event_bus = get_event_bus()
        self.state_manager = StateManager()
        self._running = False
        self._tasks: List[asyncio.Task] = []
        self._shutdown_handlers = []
        
    async def initialize(self):
        """Initialize system"""
        logger.info("Kernel initializing...")
        
        # Setup initial state
        await self.state_manager.set_state('system.status', 'initializing', source='kernel')
        await self.state_manager.set_state('system.version', '1.0.0', source='kernel')
        
        # Subscribe to system events
        await self.event_bus.subscribe(EventType.ERROR_OCCURRED, self._handle_error)
        
        logger.info("Kernel initialized")
    
    async def start(self):
        """Start kernel"""
        if self._running:
            logger.warning("Kernel already running")
            return
        
        self._running = True
        await self.state_manager.set_state('system.status', 'running', source='kernel')
        logger.info("Kernel started")
        
        # Main event loop
        while self._running:
            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
    
    async def stop(self):
        """Stop kernel gracefully"""
        logger.info("Kernel stopping...")
        self._running = False
        
        # Call shutdown handlers
        for handler in self._shutdown_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler()
                else:
                    handler()
            except Exception as e:
                logger.error(f"Error in shutdown handler: {e}")
        
        # Cancel pending tasks
        for task in self._tasks:
            if not task.done():
                task.cancel()
        
        await asyncio.gather(*self._tasks, return_exceptions=True)
        
        await self.state_manager.set_state('system.status', 'stopped', source='kernel')
        logger.info("Kernel stopped")
    
    def register_task(self, task: asyncio.Task):
        """Register long-running task for tracking"""
        self._tasks.append(task)
        task.add_done_callback(lambda t: self._tasks.remove(t) if t in self._tasks else None)
    
    def on_shutdown(self, handler):
        """Register shutdown handler"""
        self._shutdown_handlers.append(handler)
    
    async def _handle_error(self, event):
        """Handle system errors"""
        error = event.data.get('error')
        severity = event.data.get('severity', 'error')
        logger.error(f"System error ({severity}): {error}")


async def run_kernel():
    """Run kernel in async context"""
    kernel = Kernel()
    await kernel.initialize()
    
    try:
        await kernel.start()
    except KeyboardInterrupt:
        logger.info("Interrupted")
    finally:
        await kernel.stop()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_kernel())
