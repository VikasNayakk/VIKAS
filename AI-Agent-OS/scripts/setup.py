"""
Quick setup script
Run once to initialize the system
"""

import os
import shutil
from pathlib import Path

def setup():
    """Setup AI-Agent-OS"""
    print("🚀 Setting up AI-Agent-OS...\n")
    
    base_dir = Path(__file__).parent.parent
    
    # Create directories
    dirs = [
        "data/logs",
        "data/cache",
        "data/vector_db",
    ]
    
    for dir_path in dirs:
        path = base_dir / dir_path
        path.mkdir(parents=True, exist_ok=True)
        print(f"✓ Created {dir_path}")
    
    # Copy config template
    config_template = base_dir / "config/config.example.yaml"
    config_file = base_dir / "config/config.yaml"
    
    if not config_file.exists() and config_template.exists():
        shutil.copy(config_template, config_file)
        print(f"✓ Copied config template")
    
    # Copy .env template
    env_template = base_dir / ".env.example"
    env_file = base_dir / ".env"
    
    if not env_file.exists() and env_template.exists():
        shutil.copy(env_template, env_file)
        print(f"✓ Copied .env template")
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env and add your OpenAI API key")
    print("2. Edit config/config.yaml for your preferences")
    print("3. Run: python scripts/run.py")


if __name__ == "__main__":
    setup()
