"""
Microsoft Teams Integration - Send messages to Teams users/channels
"""
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class TeamsUser:
    """Teams user representation"""
    def __init__(self, name: str, email: str, teams_id: str = None):
        self.name = name
        self.email = email
        self.teams_id = teams_id or email.split('@')[0]


class TeamsChannel:
    """Teams channel representation"""
    def __init__(self, name: str, channel_id: str = None):
        self.name = name
        self.channel_id = channel_id or name.lower().replace(" ", "-")


class TeamsClient:
    """Microsoft Teams API Client (Mock/Real Implementation)"""
    
    def __init__(self, token: str = None):
        """
        Initialize Teams client
        
        Args:
            token: Microsoft Teams API token (optional for mock mode)
        """
        self.token = token
        self.base_url = "https://graph.microsoft.com/v1.0"
        self.users: Dict[str, TeamsUser] = {}
        self.channels: Dict[str, TeamsChannel] = {}
        self.messages: List[Dict] = []
        self._init_defaults()
    
    def _init_defaults(self):
        """Initialize default users and channels"""
        # Users
        self.users["himanshu"] = TeamsUser("Himanshu Nayak", "himanshu@aliens.com", "user-001")
        self.users["vikas"] = TeamsUser("Vikas Nayak", "vikas@aliens.com", "user-002")
        self.users["john"] = TeamsUser("John Doe", "john@example.com", "user-003")
        
        # Channels
        self.channels["general"] = TeamsChannel("General", "channel-general")
        self.channels["development"] = TeamsChannel("Development", "channel-dev")
        self.channels["projects"] = TeamsChannel("Projects", "channel-projects")
    
    async def send_direct_message(self, recipient: str, message: str) -> Dict[str, Any]:
        """
        Send direct message to Teams user
        
        Args:
            recipient: User name or email
            message: Message content
        
        Returns:
            Message delivery status
        """
        try:
            # Find user
            user = self._find_user(recipient)
            if not user:
                return {"success": False, "error": f"User '{recipient}' not found"}
            
            # Simulate API call
            await asyncio.sleep(0.3)
            
            # Create message record
            msg_record = {
                "id": f"msg-{len(self.messages) + 1000}",
                "timestamp": datetime.now().isoformat(),
                "to": user.name,
                "to_email": user.email,
                "to_teams_id": user.teams_id,
                "content": message,
                "type": "direct_message",
                "status": "delivered"
            }
            
            self.messages.append(msg_record)
            
            logger.info(f"[TEAMS-DM] Message delivered to {user.name} ({user.email})")
            logger.info(f"[TEAMS-DM] Content: {message}")
            
            return {
                "success": True,
                "message_id": msg_record["id"],
                "recipient": user.name,
                "recipient_email": user.email,
                "content": message,
                "type": "direct_message",
                "timestamp": msg_record["timestamp"],
                "status": "delivered"
            }
        
        except Exception as e:
            logger.error(f"Teams DM error: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_channel_message(self, channel: str, message: str) -> Dict[str, Any]:
        """
        Send message to Teams channel
        
        Args:
            channel: Channel name
            message: Message content
        
        Returns:
            Message delivery status
        """
        try:
            # Find channel
            ch = self._find_channel(channel)
            if not ch:
                return {"success": False, "error": f"Channel '{channel}' not found"}
            
            # Simulate API call
            await asyncio.sleep(0.3)
            
            # Create message record
            msg_record = {
                "id": f"msg-{len(self.messages) + 1000}",
                "timestamp": datetime.now().isoformat(),
                "channel": ch.name,
                "channel_id": ch.channel_id,
                "content": message,
                "type": "channel_message",
                "status": "posted"
            }
            
            self.messages.append(msg_record)
            
            logger.info(f"[TEAMS-CHANNEL] Message posted to #{ch.name}")
            logger.info(f"[TEAMS-CHANNEL] Content: {message}")
            
            return {
                "success": True,
                "message_id": msg_record["id"],
                "channel": ch.name,
                "channel_id": ch.channel_id,
                "content": message,
                "type": "channel_message",
                "timestamp": msg_record["timestamp"],
                "status": "posted"
            }
        
        except Exception as e:
            logger.error(f"Teams channel error: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_adaptive_card(self, recipient: str, card_data: Dict) -> Dict[str, Any]:
        """
        Send adaptive card (rich message) to user
        
        Args:
            recipient: User name or email
            card_data: Adaptive card JSON data
        
        Returns:
            Message delivery status
        """
        try:
            user = self._find_user(recipient)
            if not user:
                return {"success": False, "error": f"User '{recipient}' not found"}
            
            await asyncio.sleep(0.3)
            
            msg_record = {
                "id": f"msg-{len(self.messages) + 1000}",
                "timestamp": datetime.now().isoformat(),
                "to": user.name,
                "to_email": user.email,
                "content": json.dumps(card_data),
                "type": "adaptive_card",
                "status": "delivered"
            }
            
            self.messages.append(msg_record)
            
            logger.info(f"[TEAMS-CARD] Adaptive card delivered to {user.name}")
            
            return {
                "success": True,
                "message_id": msg_record["id"],
                "recipient": user.name,
                "type": "adaptive_card",
                "timestamp": msg_record["timestamp"],
                "status": "delivered"
            }
        
        except Exception as e:
            logger.error(f"Teams card error: {e}")
            return {"success": False, "error": str(e)}
    
    def _find_user(self, name_or_email: str) -> Optional[TeamsUser]:
        """Find user by name or email"""
        key = name_or_email.lower().strip()
        
        # Direct lookup
        if key in self.users:
            return self.users[key]
        
        # Search by email
        for user in self.users.values():
            if user.email.lower() == key or user.name.lower() == key:
                return user
        
        return None
    
    def _find_channel(self, name: str) -> Optional[TeamsChannel]:
        """Find channel by name"""
        key = name.lower().strip()
        
        if key in self.channels:
            return self.channels[key]
        
        for channel in self.channels.values():
            if channel.name.lower() == key:
                return channel
        
        return None
    
    def get_message_history(self, recipient: str = None, channel: str = None, limit: int = 10) -> List[Dict]:
        """Get message history"""
        history = self.messages
        
        if recipient:
            key = recipient.lower().strip()
            history = [m for m in history if m.get("to_email", "").lower() == key]
        
        if channel:
            key = channel.lower().strip()
            history = [m for m in history if m.get("channel", "").lower() == key]
        
        return history[-limit:]
    
    def add_user(self, name: str, email: str, teams_id: str = None):
        """Add new user to contact list"""
        key = name.lower().strip()
        self.users[key] = TeamsUser(name, email, teams_id)
        logger.info(f"Added Teams user: {name} ({email})")
    
    def add_channel(self, name: str, channel_id: str = None):
        """Add new channel to contact list"""
        key = name.lower().strip()
        self.channels[key] = TeamsChannel(name, channel_id)
        logger.info(f"Added Teams channel: {name}")


class TeamsWorkflowExecutor:
    """Execute Teams messaging workflows"""
    
    def __init__(self, token: str = None):
        self.client = TeamsClient(token)
    
    async def execute_send_teams_message(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute send Teams message workflow
        
        Task format:
        {
            "action": "send_teams_message",
            "recipient": "himanshu",  # or channel name
            "message": "hello",
            "type": "direct"  # "direct" or "channel"
        }
        """
        try:
            recipient = task.get("recipient") or task.get("target", "")
            message = task.get("message", "")
            msg_type = task.get("type", "direct")  # "direct" or "channel"
            
            if not recipient or not message:
                return {"success": False, "error": "Missing recipient or message"}
            
            if msg_type == "channel":
                result = await self.client.send_channel_message(recipient, message)
            else:
                result = await self.client.send_direct_message(recipient, message)
            
            return result
        
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_workflow(self, workflow: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute Teams messaging workflow
        
        Workflow format:
        {
            "name": "send_teams_message",
            "steps": [
                {"action": "send_teams_message", "recipient": "himanshu", "message": "Hello from bot!"},
                {"action": "wait", "duration": 1},
                {"action": "send_channel_message", "channel": "general", "message": "Update posted"}
            ]
        }
        """
        context = context or {}
        results = []
        
        try:
            for i, step in enumerate(workflow.get("steps", [])):
                action = step.get("action")
                
                logger.info(f"Teams Workflow Step {i+1}: {action}")
                
                if action == "send_teams_message":
                    recipient = step.get("recipient")
                    message = step.get("message")
                    result = await self.client.send_direct_message(recipient, message)
                    results.append({"step": i, "action": action, "result": result})
                
                elif action == "send_channel_message":
                    channel = step.get("channel")
                    message = step.get("message")
                    result = await self.client.send_channel_message(channel, message)
                    results.append({"step": i, "action": action, "result": result})
                
                elif action == "send_adaptive_card":
                    recipient = step.get("recipient")
                    card_data = step.get("card")
                    result = await self.client.send_adaptive_card(recipient, card_data)
                    results.append({"step": i, "action": action, "result": result})
                
                elif action == "wait":
                    duration = step.get("duration", 1)
                    await asyncio.sleep(duration)
                    results.append({"step": i, "action": action, "duration": duration})
                
                await asyncio.sleep(0.1)
            
            return {
                "success": True,
                "workflow": workflow.get("name"),
                "steps_completed": len(results),
                "results": results
            }
        
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            return {
                "success": False,
                "workflow": workflow.get("name"),
                "error": str(e),
                "steps_completed": len(results)
            }
    
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single Teams action"""
        try:
            if action == "send_teams_message":
                return await self.execute_send_teams_message(payload)
            elif action == "send_channel_message":
                channel = payload.get("channel")
                message = payload.get("message")
                return await self.client.send_channel_message(channel, message)
            elif action == "get_history":
                recipient = payload.get("recipient")
                channel = payload.get("channel")
                limit = payload.get("limit", 10)
                history = self.client.get_message_history(recipient, channel, limit)
                return {"success": True, "history": history}
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Action error: {e}")
            return {"success": False, "error": str(e)}
