"""Action Execution Layer - Mouse, Keyboard, App Control"""
import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class ActionResult:
    """Result of action execution"""
    success: bool
    action_type: str
    duration_ms: float
    error: Optional[str] = None
    output: Optional[str] = None


class MouseController:
    """Control mouse"""
    
    @staticmethod
    async def move(x: int, y: int, duration: float = 0.5) -> ActionResult:
        """Move mouse to position"""
        start = time.time()
        try:
            import pyautogui
            pyautogui.moveTo(x, y, duration=duration)
            
            return ActionResult(
                success=True,
                action_type="mouse_move",
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            logger.error(f"Mouse move error: {e}")
            return ActionResult(
                success=False,
                action_type="mouse_move",
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            )
    
    @staticmethod
    async def click(x: int, y: int, button: str = "left") -> ActionResult:
        """Click at position"""
        start = time.time()
        try:
            import pyautogui
            pyautogui.click(x, y, button=button)
            
            return ActionResult(
                success=True,
                action_type="mouse_click",
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            logger.error(f"Click error: {e}")
            return ActionResult(
                success=False,
                action_type="mouse_click",
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            )
    
    @staticmethod
    async def drag(x1: int, y1: int, x2: int, y2: int, duration: float = 1.0) -> ActionResult:
        """Drag from one position to another"""
        start = time.time()
        try:
            import pyautogui
            pyautogui.drag(x2 - x1, y2 - y1, duration=duration)
            
            return ActionResult(
                success=True,
                action_type="mouse_drag",
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            logger.error(f"Drag error: {e}")
            return ActionResult(
                success=False,
                action_type="mouse_drag",
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            )


class KeyboardController:
    """Control keyboard"""
    
    @staticmethod
    async def type(text: str, interval: float = 0.05) -> ActionResult:
        """Type text"""
        start = time.time()
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=interval, exceptionOnFailure=False)
            
            return ActionResult(
                success=True,
                action_type="keyboard_type",
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            logger.error(f"Type error: {e}")
            return ActionResult(
                success=False,
                action_type="keyboard_type",
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            )
    
    @staticmethod
    async def hotkey(*keys) -> ActionResult:
        """Press hotkey combination"""
        start = time.time()
        try:
            import pyautogui
            pyautogui.hotkey(*keys)
            
            return ActionResult(
                success=True,
                action_type="keyboard_hotkey",
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            logger.error(f"Hotkey error: {e}")
            return ActionResult(
                success=False,
                action_type="keyboard_hotkey",
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            )


class AppController:
    """Control applications"""
    
    @staticmethod
    async def launch_app(app_name: str) -> ActionResult:
        """Launch application"""
        start = time.time()
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.Popen(f"start {app_name}", shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(f"open -a '{app_name}'", shell=True)
            else:  # Linux
                subprocess.Popen(app_name, shell=True)
            
            await asyncio.sleep(2)  # Wait for app to open
            
            return ActionResult(
                success=True,
                action_type="app_launch",
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            logger.error(f"App launch error: {e}")
            return ActionResult(
                success=False,
                action_type="app_launch",
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            )
    
    @staticmethod
    async def close_app(app_name: str) -> ActionResult:
        """Close application"""
        start = time.time()
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.Popen(f"taskkill /im {app_name}.exe /f", shell=True)
            else:
                subprocess.Popen(f"killall {app_name}", shell=True)
            
            await asyncio.sleep(1)
            
            return ActionResult(
                success=True,
                action_type="app_close",
                duration_ms=(time.time() - start) * 1000
            )
        except Exception as e:
            logger.error(f"App close error: {e}")
            return ActionResult(
                success=False,
                action_type="app_close",
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            )


class ScreenshotController:
    """Control screenshots"""
    
    @staticmethod
    async def take() -> ActionResult:
        """Take screenshot"""
        start = time.time()
        try:
            import mss
            with mss.mss() as sct:
                screenshot = sct.shot()
                
            return ActionResult(
                success=True,
                action_type="screenshot",
                duration_ms=(time.time() - start) * 1000,
                data={"filename": screenshot}
            )
        except Exception as e:
            logger.error(f"Screenshot error: {e}")
            return ActionResult(
                success=False,
                action_type="screenshot",
                duration_ms=(time.time() - start) * 1000,
                error=str(e)
            )


class ActionExecutor:
    """Execute actions on system"""
    
    def __init__(self):
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.app = AppController()
