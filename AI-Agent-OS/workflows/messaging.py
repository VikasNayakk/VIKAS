"""
SMS/Messaging Workflows - Execute sending messages to contacts
"""
import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from integrations.teams_integration import TeamsWorkflowExecutor

logger = logging.getLogger(__name__)


class MessageService:
    """Handle SMS/messaging operations"""
    
    def __init__(self):
        self.sent_messages = []
        self.contacts = {
            "himanshu": {"name": "Himanshu Nayak", "phone": "+91-XXXX-XXXX-01", "email": "himanshu@example.com"},
            "vikas": {"name": "Vikas Nayak", "phone": "+91-XXXX-XXXX-02", "email": "vikas@example.com"},
            "john": {"name": "John Doe", "phone": "+1-555-555-0100", "email": "john@example.com"},
        }
    
    async def send_sms(self, recipient: str, message: str, method: str = "sms") -> Dict[str, Any]:
        """
        Send SMS/Message to recipient
        
        Args:
            recipient: Name or phone number
            message: Message content
            method: "sms", "email", "whatsapp", "teams"
        """
        try:
            # Normalize recipient name
            recipient_key = recipient.lower().strip()
            
            # Get contact info
            contact = self.contacts.get(recipient_key)
            
            if not contact:
                # Fallback: treat as direct number/email
                contact = {"name": recipient, "phone": recipient, "email": recipient}
            
            # Simulate sending
            await asyncio.sleep(0.5)
            
            # Log message
            msg_record = {
                "timestamp": datetime.now().isoformat(),
                "recipient": contact.get("name") or recipient,
                "phone": contact.get("phone", ""),
                "email": contact.get("email", ""),
                "message": message,
                "method": method,
                "status": "sent"
            }
            
            self.sent_messages.append(msg_record)
            
            logger.info(f"[SMS] Sent via {method.upper()} to {contact.get('name', recipient)}: {message}")
            
            return {
                "success": True,
                "recipient": contact.get("name") or recipient,
                "message": message,
                "method": method,
                "timestamp": msg_record["timestamp"],
                "status": "sent"
            }
        
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return {
                "success": False,
                "error": str(e),
                "recipient": recipient,
                "message": message
            }
    
    async def find_contact(self, name: str) -> Optional[Dict]:
        """Find contact by name"""
        key = name.lower().strip()
        if key in self.contacts:
            return self.contacts[key]
        return None
    
    def get_history(self, limit: int = 10) -> list:
        """Get message history"""
        return self.sent_messages[-limit:]


class SMSWorkflowExecutor:
    """Execute SMS sending workflows"""
    
    def __init__(self):
        self.message_service = MessageService()
        self.teams_executor = TeamsWorkflowExecutor()
    
    async def execute_action(self, action: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action based on type"""
        if action == "send_message":
            return await self.execute_send_message(task)
        elif action == "send_teams_message":
            return await self.execute_send_teams_message(task)
        else:
            return {"success": False, "error": f"Unknown action: {action}"}
    
    async def execute_send_message(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute send message workflow
        
        Task format:
        {
            "action": "send_message",
            "target": "himanshu",
            "message": "hello",
            "method": "sms"  # optional
        }
        """
        try:
            target = task.get("target") or task.get("recipient", "")
            message = task.get("message", "")
            method = task.get("method", "sms")
            
            if not target or not message:
                return {"success": False, "error": "Missing target or message"}
            
            # Send message
            result = await self.message_service.send_sms(target, message, method)
            
            return result
        
        except Exception as e:
            logger.error(f"Workflow error: {e}")
            return {"success": False, "error": str(e)}
    
    async def execute_send_teams_message(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute send Teams message
        
        Task format:
        {
            "action": "send_teams_message",
            "target": "himanshu",
            "message": "hello"
        }
        """
        return await self.teams_executor.execute_send_teams_message(task)
    
    async def execute_workflow(self, workflow: Dict[str, Any], context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute a complete workflow (sequence of steps)
        
        Workflow format:
        {
            "name": "send_message",
            "steps": [
                {"action": "find_contact", "name": "himanshu"},
                {"action": "prepare_message", "text": "hello"},
                {"action": "send_message"}
            ]
        }
        """
        context = context or {}
        results = []
        
        try:
            for i, step in enumerate(workflow.get("steps", [])):
                action = step.get("action")
                
                logger.info(f"Step {i+1}: {action}")
                
                if action == "find_contact":
                    name = step.get("name")
                    contact = await self.message_service.find_contact(name)
                    context["contact"] = contact
                    results.append({"step": i, "action": action, "result": contact})
                
                elif action == "prepare_message":
                    text = step.get("text")
                    context["message"] = text
                    results.append({"step": i, "action": action, "message": text})
                
                elif action == "send_message":
                    target = context.get("contact", {}).get("name") or step.get("target", "")
                    message = context.get("message") or step.get("message", "")
                    method = step.get("method", "sms")
                    
                    result = await self.message_service.send_sms(target, message, method)
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
            logger.error(f"Workflow execution error: {e}")
            return {
                "success": False,
                "workflow": workflow.get("name"),
                "error": str(e),
                "steps_completed": len(results)
            }
    
    async def execute_action(self, action: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single action"""
        try:
            if action == "send_message":
                return await self.execute_send_message(payload)
            elif action == "send_teams_message":
                return await self.execute_send_teams_message(payload)
            elif action == "find_contact":
                name = payload.get("name", "")
                contact = await self.message_service.find_contact(name)
                return {"success": contact is not None, "contact": contact}
            elif action == "get_history":
                limit = payload.get("limit", 10)
                history = self.message_service.get_history(limit)
                return {"success": True, "history": history}
            else:
                return {"success": False, "error": f"Unknown action: {action}"}
        except Exception as e:
            logger.error(f"Action error: {e}")
            return {"success": False, "error": str(e)}
