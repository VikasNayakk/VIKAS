"""Configuration management"""
import json
import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover
    load_dotenv = None  # type: ignore

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manage system configuration"""
    
    def __init__(self, config_dir: str = "./config"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        self.config: Dict[str, Any] = {}
        self._load_defaults()
    
    def _load_defaults(self):
        """Load default configuration"""
        self.config = {
            "system": {
                "version": "1.0.0",
                "debug": False,
                "max_retries": 3,
                "timeout": 30
            },
            "llm": {
                "provider": "openai",
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 2000,
                "enable_cache": True,
                "gemini_api_key": None,
                "gemini_project_id": None,
                "gemini_model": "gemini-flash-latest"
            },
            "vision": {
                "capture_interval": 0.5,
                "cache_ttl": 5,
                "use_ocr": True
            },
            "security": {
                "sandbox_enabled": True,
                "permission_checks": True,
                "audit_logging": True
            },
            "ui": {
                "show_overlay": True,
                "theme": "dark",
                "refresh_rate": 30
            }
        }
    
    async def load_from_file(self, file_path: str):
        """Load configuration from file"""
        self._load_env()
        path = Path(file_path)
        
        if not path.exists():
            logger.warning(f"Config file not found: {file_path}")
            return
        
        try:
            if file_path.endswith('.yaml') or file_path.endswith('.yml'):
                with open(path) as f:
                    user_config = yaml.safe_load(f)
            else:
                with open(path) as f:
                    user_config = json.load(f)
            
            user_config = self._resolve_env_vars(user_config)
            
            # Merge with defaults
            self._merge_config(user_config)
            logger.info(f"Configuration loaded from {file_path}")
        
        except Exception as e:
            logger.error(f"Error loading config: {e}")

    def _load_env(self):
        """Load .env from project root if available."""
        if load_dotenv is None:
            return

        env_path = Path(__file__).resolve().parent.parent / ".env"
        if env_path.exists():
            try:
                load_dotenv(env_path, override=False)
                logger.info(f"Loaded environment variables from {env_path}")
            except Exception as e:
                logger.warning(f"Could not load .env: {e}")
    
    def _merge_config(self, user_config: Dict):
        """Merge user config with defaults"""
        for key, value in user_config.items():
            if isinstance(value, dict) and key in self.config:
                self.config[key].update(value)
            else:
                self.config[key] = value

    def _resolve_env_vars(self, value: Any) -> Any:
        """Resolve ${VAR} placeholders from environment variables."""
        if isinstance(value, dict):
            return {k: self._resolve_env_vars(v) for k, v in value.items()}
        if isinstance(value, list):
            return [self._resolve_env_vars(v) for v in value]
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_key = value[2:-1]
            return os.getenv(env_key, value)
        return value
    
    async def save_config(self, file_path: str = None):
        """Save configuration to file"""
        path = Path(file_path or self.config_dir / "config.yaml")
        path.parent.mkdir(exist_ok=True)
        
        try:
            if str(path).endswith('.yaml') or str(path).endswith('.yml'):
                with open(path, 'w') as f:
                    yaml.dump(self.config, f)
            else:
                with open(path, 'w') as f:
                    json.dump(self.config, f, indent=2)
            
            logger.info(f"Configuration saved to {path}")
        
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get config value by path (e.g., 'llm.provider')"""
        parts = path.split('.')
        value = self.config
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
        
        return value
    
    def set(self, path: str, value: Any):
        """Set config value by path"""
        parts = path.split('.')
        current = self.config
        
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        current[parts[-1]] = value
