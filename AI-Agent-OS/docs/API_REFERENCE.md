"""
Quick reference for API usage
"""

class AIAgentOSAPI:
    """
    Quick API reference
    
    Usage:
    ------
    from main import AIAgentOS
    import asyncio
    
    async def demo():
        system = AIAgentOS()
        await system.initialize()
        
        # Send command
        await system.send_command("send hello to himanshu")
        
        # Wait for processing
        await asyncio.sleep(2)
        
        await system.shutdown()
    
    asyncio.run(demo())
    """
    
    @staticmethod
    async def send_command(command: str):
        """Send natural language command
        
        Examples:
        - "send hello to himanshu"
        - "open chrome and search python"
        - "take screenshot"
        - "click at 100,200"
        """
        pass
    
    @staticmethod
    async def execute_task(task: dict):
        """Execute structured task
        
        Example:
        {
            "action": "send_message",
            "target": "himanshu",
            "parameters": {
                "message": "hello",
                "app": "teams"
            }
        }
        """
        pass
    
    @staticmethod
    async def add_workflow(workflow: dict):
        """Register custom workflow
        
        Example:
        {
            "name": "my_workflow",
            "steps": [
                {"action": "open_app", "target": "chrome"},
                {"action": "wait", "duration": 2}
            ]
        }
        """
        pass


# Command Examples
COMMAND_EXAMPLES = {
    "messaging": [
        "send hello to himanshu",
        "message john about the project",
        "tell alice good morning"
    ],
    "web": [
        "open chrome and search python",
        "go to google.com",
        "search for machine learning course"
    ],
    "files": [
        "create file notes.txt",
        "open document.docx",
        "save screenshot"
    ],
    "apps": [
        "launch vs code",
        "close chrome",
        "open teams"
    ],
    "ui": [
        "click at 100,200",
        "type hello world",
        "take screenshot",
        "scroll down"
    ]
}
