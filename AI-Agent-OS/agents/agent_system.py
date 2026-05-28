"""Agent System - HAT (Hierarchical Agent Tree) Architecture"""
import asyncio
import logging
import uuid
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from workflows.messaging import SMSWorkflowExecutor
from core.event_bus import get_event_bus, EventType
from brain.llm.factory import create_llm_provider

logger = logging.getLogger(__name__)


class AgentState(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    THINKING = "thinking"
    EXECUTING = "executing"


@dataclass
class AgentMessage:
    """Message between agents"""
    sender_id: str
    receiver_id: str
    message_type: str  # "request", "response", "event"
    payload: Dict[str, Any]
    message_id: str = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.message_id is None:
            self.message_id = str(uuid.uuid4())
        if self.timestamp is None:
            import time
            self.timestamp = time.time()


class BaseAgent(ABC):
    """Base agent class"""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.state = AgentState.IDLE
        self._message_queue: asyncio.Queue = asyncio.Queue()
        self._handlers: Dict[str, callable] = {}
    
    async def initialize(self):
        """Initialize agent"""
        logger.info(f"Agent {self.agent_id} initializing")
    
    async def send_message(self, receiver_id: str, message_type: str, payload: Dict):
        """Send message to another agent"""
        msg = AgentMessage(
            sender_id=self.agent_id,
            receiver_id=receiver_id,
            message_type=message_type,
            payload=payload
        )
        logger.debug(f"Agent {self.agent_id} sending {message_type} to {receiver_id}")
        # Message routing handled by coordinator
    
    async def receive_message(self, message: AgentMessage):
        """Receive message from another agent"""
        logger.info(f"Agent {self.agent_id} received {message.message_type}")
        await self._message_queue.put(message)
    
    async def process_messages(self):
        """Process message queue"""
        while True:
            try:
                message = await asyncio.wait_for(self._message_queue.get(), timeout=1.0)
                await self._handle_message(message)
            except asyncio.TimeoutError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
    
    async def _handle_message(self, message: AgentMessage):
        """Handle incoming message"""
        logger.info(f"Agent {self.agent_id} handling {message.message_type}")
        handler = self._handlers.get(message.message_type)
        if handler:
            await handler(message)
        else:
            logger.warning(f"No handler for {message.message_type}")
    
    def register_handler(self, message_type: str, handler: callable):
        """Register message handler"""
        self._handlers[message_type] = handler
    
    @abstractmethod
    async def run(self):
        """Main agent loop"""
        pass
    
    async def shutdown(self):
        """Shutdown agent"""
        logger.info(f"Agent {self.agent_id} shutting down")


class CoordinatorAgent(BaseAgent):
    """
    Central coordinator - Routes messages between agents
    Manages task flow
    """
    
    def __init__(self):
        super().__init__("coordinator", "coordinator")
        self._agents: Dict[str, BaseAgent] = {}
        self._task_queue: List[Dict] = []
    
    async def register_agent(self, agent: BaseAgent):
        """Register child agent"""
        self._agents[agent.agent_id] = agent
        logger.info(f"Registered agent: {agent.agent_id}")
    
    async def route_message(self, message: AgentMessage):
        """Route message to target agent"""
        logger.info(f"Routing message {message.message_type} to {message.receiver_id}")
        if message.receiver_id in self._agents:
            await self._agents[message.receiver_id].receive_message(message)
        else:
            logger.warning(f"Agent {message.receiver_id} not found")
    
    async def add_task(self, task: Dict):
        """Add task to queue"""
        task["id"] = str(uuid.uuid4())
        self._task_queue.append(task)
        logger.info(f"Task added: {task['id']}")
        return task["id"]
    
    async def run(self):
        """Coordinator main loop"""
        logger.info("Coordinator agent started")
        
        while True:
            try:
                # Process pending tasks
                if self._task_queue:
                    logger.info(f"Coordinator processing {len(self._task_queue)} tasks")
                    task = self._task_queue.pop(0)
                    await self._dispatch_task(task)
                
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Coordinator error: {e}")
    
    async def _dispatch_task(self, task: Dict):
        """Dispatch task to appropriate executor"""
        logger.info(f"Dispatching task {task.get('id')} to executor")
        # Route to executor agent
        await self.route_message(AgentMessage(
            sender_id=self.agent_id,
            receiver_id="executor",
            message_type="execute_task",
            payload=task
        ))


class ExecutorAgent(BaseAgent):
    """Execute tasks - Low-level action execution"""
    
    def __init__(self, config: Any):
        super().__init__("executor", "executor")
        self.current_task = None
        self.config = config
        self.sms_executor = SMSWorkflowExecutor()
        self.llm_provider = create_llm_provider(config)
        self.register_handler("execute_task", self._handle_execute_task)
        self.register_handler("schedule_tasks", self._handle_schedule_tasks)
    
    async def _handle_execute_task(self, message: AgentMessage):
        """Handle task execution request"""
        self.current_task = message.payload
        self.state = AgentState.EXECUTING
        logger.info(f"Executing task: {self.current_task}")
        
        # Execute task based on action type
        intent = self.current_task.get("intent")
        if intent:
            action = intent.action
            # Update task with intent data
            self.current_task.update(intent.parameters)
            self.current_task["action"] = action
            if intent.target:
                self.current_task["target"] = intent.target
        else:
            action = self.current_task.get("action", "")
        
        logger.info(f"Executing action: {action} for task: {self.current_task}")
        
        if action == "send_message":
            result = await self.sms_executor.execute_send_message(self.current_task)
            logger.info(f"Task result: {result}")
        elif action == "send_teams_message":
            result = await self.sms_executor.execute_send_teams_message(self.current_task)
            logger.info(f"Task result: {result}")
        elif action == "search":
            query = self.current_task.get("parameters", {}).get("query") or self.current_task.get("command", "")
            result = await self._execute_search(query)
            logger.info(f"Search result: {result}")
        elif action == "screenshot":
            result = await self._execute_screenshot()
            logger.info(f"Screenshot result: {result}")
        elif action == "type":
            text = self.current_task.get("text", "")
            result = await self._execute_type(text)
            logger.info(f"Type result: {result}")
        elif action == "open_app":
            result = await self._execute_open_app(self.current_task)
            logger.info(f"Open app result: {result}")
        elif action == "close_app":
            result = await self._execute_close_app(self.current_task)
            logger.info(f"Close app result: {result}")
        else:
            result = await self.sms_executor.execute_action(action, self.current_task)
            logger.info(f"Task result: {result}")
        
        self.state = AgentState.IDLE
    
    async def _handle_schedule_tasks(self, message: AgentMessage):
        """Handle multiple tasks scheduling"""
        tasks = message.payload.get("tasks", [])
        logger.info(f"Scheduling {len(tasks)} tasks")
        
        for task in tasks:
            await self._handle_execute_task(AgentMessage(
                sender_id=message.sender_id,
                receiver_id=self.agent_id,
                message_type="execute_task",
                payload=task
            ))
    
    async def run(self):
        """Executor main loop"""
        logger.info("Executor agent started")
        
        while True:
            await self.process_messages()
            await asyncio.sleep(0.1)
    
    async def _execute_screenshot(self):
        """Take screenshot"""
        try:
            from actions.executor import ScreenshotController
            return await ScreenshotController.take()
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_type(self, text: str):
        """Type text"""
        try:
            from actions.executor import KeyboardController
            return await KeyboardController.type(text)
        except Exception as e:
            logger.error(f"Type error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_open_app(self, task: Dict):
        """Open application"""
        app = task.get("target", "") or task.get("app", "")
        if not app:
            return {"success": False, "error": "No app specified"}
        try:
            from actions.executor import AppController
            return await AppController.launch_app(app)
        except Exception as e:
            logger.error(f"Open app error: {e}")
            return {"success": False, "error": str(e)}
    
    async def _execute_close_app(self, task: Dict):
        """Close application"""
        app = task.get("target", "") or task.get("app", "")
        if not app:
            return {"success": False, "error": "No app specified"}
        try:
            from actions.executor import AppController
            return await AppController.close_app(app)
        except Exception as e:
            logger.error(f"Close app error: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_search(self, query: str) -> Dict[str, Any]:
        """Execute a search query using the configured LLM provider."""
        if not query:
            return {"success": False, "error": "Search query missing"}

        try:
            logger.info(f"Executing search via LLM provider: {query}")
            response = await self.llm_provider.generate(
                prompt=query,
                temperature=0.2,
                max_tokens=256
            )

            if not response.success:
                return {"success": False, "error": response.error or "LLM provider failed"}

            return {
                "success": True,
                "query": query,
                "answer": response.content,
                "provider": type(self.llm_provider).__name__,
                "model": response.model
            }

        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"success": False, "error": str(e)}


class PlannerAgent(BaseAgent):
    """Plan task execution - Break down high-level tasks into steps"""
    
    def __init__(self):
        super().__init__("planner", "planner")
        self.register_handler("plan_task", self._handle_plan_task)
    
    async def _handle_plan_task(self, message: AgentMessage):
        """Plan task execution"""
        self.state = AgentState.THINKING
        logger.info(f"Planning task: {message.payload}")
        
        # Generate execution plan
        plan = self._generate_plan(message.payload)
        
        # Send plan to executor
        await self.send_message("executor", "schedule_tasks", {"tasks": plan})
        
        self.state = AgentState.IDLE
    
    def _generate_plan(self, task: Dict) -> List[Dict]:
        """Generate execution plan for task"""
        # Would use AI to generate plan
        return [task]  # For now, just return single task
    
    async def run(self):
        """Planner main loop"""
        logger.info("Planner agent started")
        
        while True:
            await self.process_messages()
            await asyncio.sleep(0.1)


class MonitorAgent(BaseAgent):
    """Monitor system - Watch for errors and performance"""
    
    def __init__(self):
        super().__init__("monitor", "monitor")
        self._metrics = {}
    
    async def record_metric(self, name: str, value: float):
        """Record system metric"""
        if name not in self._metrics:
            self._metrics[name] = []
        
        self._metrics[name].append(value)
        
        # Keep only last 100 values
        if len(self._metrics[name]) > 100:
            self._metrics[name] = self._metrics[name][-100:]
    
    async def get_metrics(self) -> Dict:
        """Get system metrics"""
        return self._metrics.copy()
    
    async def run(self):
        """Monitor main loop"""
        logger.info("Monitor agent started")
        
        while True:
            # Record system metrics
            try:
                import psutil
                await self.record_metric("cpu_percent", psutil.cpu_percent())
                await self.record_metric("memory_percent", psutil.virtual_memory().percent)
            except:
                pass
            
            await asyncio.sleep(1)


class AgentSystem:
    """Manage all agents"""
    
    def __init__(self, config: Any):
        self.coordinator = CoordinatorAgent()
        self.executor = ExecutorAgent(config)
        self.planner = PlannerAgent()
        self.monitor = MonitorAgent()
        self._agents = [self.coordinator, self.executor, self.planner, self.monitor]
    
    async def initialize(self):
        """Initialize agent system"""
        logger.info("Initializing agent system...")
        
        # Register agents with coordinator
        for agent in self._agents:
            await self.coordinator.register_agent(agent)
            await agent.initialize()
        
        # Subscribe to user commands
        event_bus = get_event_bus()
        await event_bus.subscribe(EventType.USER_COMMAND, self._handle_user_command)
    
    async def _handle_user_command(self, event):
        """Handle user command event"""
        command = event.data.get("command", "")
        logger.info(f"Received user command: {command}")
        
        # Parse intent
        from brain.parser.intent_parser import IntentParser
        parser = IntentParser()
        intent = parser.parse(command)
        
        # Create task
        task = {
            "type": "user_command",
            "intent": intent,
            "command": command,
            "timestamp": event.timestamp
        }
        
        await self.add_task(task)
    
    async def start(self):
        """Start all agents"""
        logger.info("Starting agent system...")
        
        tasks = [agent.run() for agent in self._agents]
        await asyncio.gather(*tasks)
    
    async def add_task(self, task: Dict) -> str:
        """Add task to coordinator"""
        return await self.coordinator.add_task(task)
    
    async def shutdown(self):
        """Shutdown agent system"""
        logger.info("Shutting down agent system...")
        
        for agent in self._agents:
            await agent.shutdown()
