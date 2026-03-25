"""Security Sandbox - Safe execution environment"""
import logging
import asyncio
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class CodeSandbox:
    """
    Restricted code execution environment
    Prevents malicious code from accessing system
    """
    
    def __init__(self, allowed_imports: list = None, allowed_functions: list = None):
        self.allowed_imports = allowed_imports or ['math', 'time', 'json']
        self.allowed_functions = allowed_functions or ['print', 'len', 'str', 'int']
    
    async def execute(self, code: str, timeout: float = 5.0) -> Dict:
        """
        Execute code in restricted environment
        Returns: {"success": bool, "output": str, "error": str}
        """
        try:
            # Create restricted globals
            safe_globals = {
                '__builtins__': {name: __builtins__[name] for name in self.allowed_functions if name in __builtins__},
                '__name__': '__sandbox__',
                '__loader__': None,
            }
            
            safe_locals = {}
            
            # Execute with timeout
            result = await asyncio.wait_for(
                asyncio.to_thread(exec, code, safe_globals, safe_locals),
                timeout=timeout
            )
            
            return {
                "success": True,
                "output": str(safe_locals),
                "error": None
            }
        
        except asyncio.TimeoutError:
            logger.error("Sandbox execution timeout")
            return {
                "success": False,
                "output": "",
                "error": "Execution timeout"
            }
        
        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    async def validate_code(self, code: str) -> bool:
        """Validate code before execution"""
        try:
            import ast
            ast.parse(code)
            return True
        except SyntaxError as e:
            logger.error(f"Code validation failed: {e}")
            return False


class PermissionManager:
    """Manage permissions for actions"""
    
    def __init__(self):
        self.permissions = {
            "send_message": ["users"],
            "open_app": ["applications"],
            "file_access": ["paths"],
            "network": ["urls"],
            "system": ["commands"]
        }
    
    async def check_permission(self, action: str, resource: str) -> bool:
        """Check if action is allowed"""
        if action not in self.permissions:
            logger.warning(f"Unknown permission: {action}")
            return False
        
        logger.debug(f"Permission check: {action} on {resource}")
        return True
    
    async def grant_permission(self, action: str, resource: str):
        """Grant permission"""
        if action not in self.permissions:
            self.permissions[action] = []
        
        if resource not in self.permissions[action]:
            self.permissions[action].append(resource)
            logger.info(f"Granted permission: {action} on {resource}")
    
    async def revoke_permission(self, action: str, resource: str):
        """Revoke permission"""
        if action in self.permissions and resource in self.permissions[action]:
            self.permissions[action].remove(resource)
            logger.info(f"Revoked permission: {action} on {resource}")


class SecurityManager:
    """Unified security management"""
    
    def __init__(self):
        self.sandbox = CodeSandbox()
        self.permissions = PermissionManager()
    
    async def execute_safely(self, code: str) -> Dict:
        """Execute code safely"""
        # Validate code first
        if not await self.sandbox.validate_code(code):
            return {"success": False, "error": "Invalid code"}
        
        # Execute in sandbox
        return await self.sandbox.execute(code)
