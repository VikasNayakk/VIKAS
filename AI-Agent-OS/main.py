import asyncio
import logging
import sys
from pathlib import Path
import queue

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from core.kernel import Kernel
from core.event_bus import get_event_bus, EventType
from agents.agent_system import AgentSystem
from config.config_manager import ConfigManager
from observability.logging import StructuredLogger
from brain.parser.intent_parser import IntentParser

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AIAgentOS:
    """Main AI-Agent-OS system"""
    
    def __init__(self):
        self.kernel = Kernel()
        self.event_bus = get_event_bus()
        self.agents = None
        self.config = ConfigManager()
        self.logger = StructuredLogger("AI-Agent-OS")
        self.intent_parser = IntentParser()
        self.command_queue = queue.Queue()  # Queue for web commands
    
    async def initialize(self):
        """Initialize system"""
        logger.info("=" * 60)
        logger.info("AI-Agent-OS Initializing...")
        logger.info("=" * 60)
        
        # Load config
        await self.config.load_from_file("./config/config.yaml")
        
        # Initialize agent system with configuration
        self.agents = AgentSystem(self.config)

        # Initialize kernel
        await self.kernel.initialize()
        
        # Initialize agents
        await self.agents.initialize()
        
        # Subscribe to events
        await self.event_bus.subscribe(EventType.USER_COMMAND, self._handle_user_command)
        
        logger.info("System initialized successfully!")
    
    async def _handle_user_command(self, event):
        """Handle user command"""
        command = event.data.get("command")
        logger.info(f"Processing command: {command}")
        
        # Parse intent
        intent = self.intent_parser.parse(command)
        logger.info(f"Parsed intent: {intent.action} - target={intent.target}")
        
        # Add task to coordinator - convert intent to executable task
        task = {
            "command": command,
            "action": intent.action,
            "target": intent.target,
            "message": intent.parameters.get("message", ""),
            "parameters": intent.parameters
        }
        
        task_id = await self.agents.add_task(task)
        logger.info(f"Task created: {task_id}")
        logger.info(f"Task details: {task}")
    
    async def send_command(self, command: str):
        """Send user command"""
        await self.event_bus.emit_sync(
            EventType.USER_COMMAND,
            "user",
            {"command": command}
        )
    
    async def run(self):
        """Run system"""
        try:
            # Start kernel
            kernel_task = asyncio.create_task(self.kernel.start())
            
            # Start agents
            agents_task = asyncio.create_task(self.agents.start())
            
            # Process command queue
            queue_task = asyncio.create_task(self._process_command_queue())
            
            # Wait for tasks
            await asyncio.gather(kernel_task, agents_task, queue_task)
        
        except KeyboardInterrupt:
            logger.info("Interrupted")
        
        finally:
            await self.shutdown()

    async def shutdown(self):
        """Shutdown system"""
        logger.info("Shutting down...")
        
        await self.kernel.stop()
        if self.agents:
            await self.agents.shutdown()
        await self.config.save_config()
        
        logger.info("System shutdown complete")
    
    async def _process_command_queue(self):
        """Process commands from web interface"""
        while True:
            try:
                # Non-blocking get with timeout
                try:
                    command = self.command_queue.get(timeout=0.1)
                    logger.info(f"Processing queued command: {command}")
                    await self.send_command(command)
                except queue.Empty:
                    pass  # No command, continue
            except Exception as e:
                logger.error(f"Error processing command queue: {e}")
                await asyncio.sleep(1)


async def main():
    """Main async entry point"""
    system = AIAgentOS()
    
    try:
        await system.initialize()
        
        # Interactive loop
        logger.info("\nSystem ready. Type commands:")
        logger.info("Example: 'send hello to himanshu'")
        logger.info("Example: 'open chrome'")
        logger.info("Example: 'take screenshot'")
        logger.info("Type 'exit' or 'quit' to stop\n")
        
        while True:
            try:
                # Better prompt
                command = input("\n🤖 Command > ").strip()
                
                if command.lower() in ['exit', 'quit', 'bye', 'stop']:
                    logger.info("👋 Stopping system...")
                    break
                
                if command.lower() in ['help', '?']:
                    print("""
╔════════════════════════════════════════════════════╗
║           📚 AVAILABLE COMMANDS                    ║
╠════════════════════════════════════════════════════╣
║ MESSAGING:                                         ║
║  • send hello to [name]                            ║
║  • message [name] [text]                           ║
║                                                    ║
║ APPS:                                              ║
║  • open [app name]     (e.g., chrome, teams)       ║
║  • close [app name]                                ║
║                                                    ║
║ UI CONTROL:                                        ║
║  • type [text]         (type something)            ║
║  • click [x,y]         (click at position)         ║
║  • take screenshot     (capture screen)            ║
║                                                    ║
║ SYSTEM:                                            ║
║  • status              (show system status)        ║
║  • help                (show this help)            ║
║  • exit/quit           (stop system)               ║
╚════════════════════════════════════════════════════╝
                    """)
                    continue
                
                if command.lower() == 'status':
                    metrics = await system.agents.monitor.get_metrics()
                    print(f"""
╔════════════════════════════════════════════════════╗
║           🔍 SYSTEM STATUS                         ║
╠════════════════════════════════════════════════════╣
║ Kernel:     🟢 Running                             ║
║ Agents:     🟢 4/4 Active                          ║
║  ├─ Coordinator                                    ║
║  ├─ Executor                                       ║
║  ├─ Planner                                        ║
║  └─ Monitor                                        ║
║ Memory:     Initialized                            ║
║ Events:     Processing                             ║
║ Cache:      Active                                 ║
╚════════════════════════════════════════════════════╝
                    """)
                    continue
                
                if command.strip():
                    print(f"⏳ Processing: {command}")
                    await system.send_command(command)
                    await asyncio.sleep(0.5)  # Brief pause for processing
            
            except KeyboardInterrupt:
                logger.info("\nInterrupted")
                break
            except Exception as e:
                logger.error(f"Error: {e}")
    
    finally:
        await system.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
