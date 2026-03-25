"""Intent Parser - Parse natural language into actionable intents"""
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Intent:
    """Parsed user intent"""
    action: str  # e.g., "send_message", "open_app"
    target: Optional[str] = None  # e.g., "Himanshu"
    parameters: Dict = None  # e.g., {"message": "hello"}
    confidence: float = 1.0
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}


class IntentParser:
    """
    Parse natural language into structured intents
    
    Example:
        "Hello Himanshu" -> Intent(action="send_message", target="Himanshu", parameters={"message": "hello"})
    """
    
    # Define action patterns
    ACTIONS = {
        "send_message": ["send", "message", "tell", "say", "msg", "chat", "sms"],
        "send_teams_message": ["teams", "team message", "teams message"],
        "open_file": ["open file", "open document"],
        "open_app": ["open", "launch", "start", "run"],
        "click": ["click", "tap", "press"],
        "type": ["type", "write", "enter"],
        "search": ["search", "find", "google", "look"],
        "screenshot": ["screenshot", "capture", "snap"],
        "close_app": ["close", "exit", "quit"],
    }
    
    def __init__(self):
        # Build reverse mapping for faster lookup
        self.action_keywords = {}
        for action, keywords in self.ACTIONS.items():
            for keyword in keywords:
                self.action_keywords[keyword.lower()] = action
    
    def parse(self, text: str) -> Intent:
        """Parse text into intent"""
        text_lower = text.lower().strip()
        
        # Detect action
        action = self._detect_action(text_lower)
        
        # Extract parameters
        target, parameters = self._extract_entities(text_lower, action)
        
        logger.info(f"Parsed intent: action={action}, target={target}, text='{text}'")
        
        return Intent(
            action=action,
            target=target,
            parameters=parameters,
            confidence=0.9  # Confidence score
        )
    
    def _detect_action(self, text: str) -> str:
        """Detect primary action from text"""
        words = text.split()
        
        # Check for specific patterns first (higher priority)
        if "teams" in text.lower():
            return "send_teams_message"
        
        if "channel" in text.lower():
            return "send_teams_message"
        
        # Then check individual keywords
        for word in words:
            if word in self.action_keywords:
                return self.action_keywords[word]
        
        # Default action
        return "send_message"
    
    def _extract_entities(self, text: str, action: str) -> tuple:
        """Extract target and parameters"""
        target = None
        parameters = {}
        
        if action == "send_teams_message":
            # Extract Teams recipient and message
            # "send hello on teams to himanshu" -> target="himanshu", message="hello"
            parts = text.split()
            message_text = ""
            
            # Simple extraction - look for "to" keyword
            if "to" in parts:
                to_idx = parts.index("to")
                if to_idx + 1 < len(parts):
                    target = parts[to_idx + 1]
                    # Get message from the beginning up to "on teams"/"to"
                    before_teams = " ".join(parts[: to_idx])
                    # Remove "send" and "on teams" from message
                    for word in ["send", "on", "teams"]:
                        before_teams = before_teams.replace(word, "").strip()
                    message_text = before_teams
            
            if not message_text:
                message_text = " ".join(parts[1:]).replace("on teams", "").replace("to", "").strip()
            
            parameters["message"] = message_text if message_text else "message"
        
        elif action == "send_message":
            # Extract message target and content
            # "send hello to himanshu" -> target="himanshu", message="hello"
            parts = text.split()
            
            # Simple extraction - look for "to" keyword
            if "to" in parts:
                to_idx = parts.index("to")
                if to_idx + 1 < len(parts):
                    target = parts[to_idx + 1]
                    message = " ".join(parts[: to_idx])
                    parameters["message"] = message
            else:
                # Assume everything after first word is the message
                if len(parts) > 1:
                    parameters["message"] = " ".join(parts[1:])
        
        elif action == "open_app":
            # "open chrome" -> target="chrome"
            action_words = ["open", "launch", "start", "run"]
            for word in action_words:
                if word in text:
                    idx = text.index(word)
                    target = text[idx + len(word):].strip().split()[0] if idx + len(word) < len(text) else None
                    break
        
        elif action == "search":
            # "search python tutorial" -> parameters={"query": "python tutorial"}
            search_words = ["search", "find", "google"]
            for word in search_words:
                if word in text:
                    idx = text.index(word)
                    query = text[idx + len(word):].strip()
                    parameters["query"] = query
                    break
        
        return target, parameters
