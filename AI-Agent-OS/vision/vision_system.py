"""Vision System - Screen capture and detection with caching"""
import asyncio
import logging
import time
import hashlib
from typing import Optional, Dict, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ScreenCapture:
    """Screen capture data"""
    width: int
    height: int
    data: bytes
    timestamp: float
    hash: str


class ScreenCapturer:
    """Capture screen efficiently"""
    
    @staticmethod
    async def capture() -> Optional[ScreenCapture]:
        """Capture current screen"""
        start = time.time()
        try:
            import mss
            
            with mss.mss() as sct:
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = sct.grab(monitor)
                
                # Convert to bytes
                img_data = bytes(screenshot.rgb)
                
                # Calculate hash for caching
                img_hash = hashlib.md5(img_data).hexdigest()
                
                return ScreenCapture(
                    width=screenshot.width,
                    height=screenshot.height,
                    data=img_data,
                    timestamp=time.time(),
                    hash=img_hash
                )
        except Exception as e:
            logger.error(f"Screen capture error: {e}")
            return None


class VisionCache:
    """Cache vision analysis results by screen hash"""
    
    def __init__(self, ttl: int = 5):  # 5 seconds
        self.ttl = ttl
        self._cache: Dict[str, Dict] = {}
    
    async def get(self, screen_hash: str) -> Optional[Dict]:
        """Get cached analysis"""
        if screen_hash not in self._cache:
            return None
        
        data, timestamp = self._cache[screen_hash]
        
        if time.time() - timestamp > self.ttl:
            del self._cache[screen_hash]
            return None
        
        return data
    
    async def set(self, screen_hash: str, data: Dict):
        """Cache analysis"""
        self._cache[screen_hash] = (data, time.time())
    
    async def clear(self):
        """Clear cache"""
        self._cache.clear()


class UIDetector:
    """Detect UI elements on screen"""
    
    @staticmethod
    async def detect_buttons(capture: ScreenCapture) -> List[Dict]:
        """Detect clickable buttons"""
        # Placeholder - would use OpenCV/ML model in production
        return []


class OCREngine:
    """Extract text from screen"""
    
    def __init__(self):
        self._tesseract_available = self._check_tesseract()
    
    def _check_tesseract(self) -> bool:
        """Check if tesseract OCR is available"""
        try:
            import pytesseract
            return True
        except ImportError:
            logger.warning("Tesseract OCR not available")
            return False
    
    async def extract_text(self, capture: ScreenCapture) -> str:
        """Extract text from screen capture"""
        if not self._tesseract_available:
            return ""
        
        try:
            import pytesseract
            from PIL import Image
            import numpy as np
            
            # Convert bytes to image
            img_array = np.frombuffer(capture.data, dtype=np.uint8).reshape(
                capture.height, capture.width, 3
            )
            img = Image.fromarray(img_array)
            
            # Extract text
            text = pytesseract.image_to_string(img)
            return text
        except Exception as e:
            logger.error(f"OCR error: {e}")
            return ""


class VisionSystem:
    """Unified vision system"""
    
    def __init__(self):
        self.capturer = ScreenCapturer()
        self.cache = VisionCache()
        self.ui_detector = UIDetector()
        self.ocr = OCREngine()
        self._last_capture_hash = None
    
    async def analyze_screen(self) -> Dict:
        """Analyze current screen with caching"""
        # Capture screen
        capture = await self.capturer.capture()
        if not capture:
            return {}
        
        # Check cache
        cached = await self.cache.get(capture.hash)
        if cached:
            logger.debug("Using cached vision analysis")
            return cached
        
        # Run analysis
        analysis = {
            "width": capture.width,
            "height": capture.height,
            "hash": capture.hash,
            "timestamp": capture.timestamp,
            "ui_elements": await self.ui_detector.detect_buttons(capture),
            "text": await self.ocr.extract_text(capture)
        }
        
        # Cache result
        await self.cache.set(capture.hash, analysis)
        
        return analysis
