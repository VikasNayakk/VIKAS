#!/usr/bin/env python3
"""
AI-Agent-OS with Web Dashboard
Run with: python scripts/run_with_dashboard.py
Then open: http://localhost:5000
"""

import asyncio
import sys
import threading
import logging
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import AIAgentOS
from ui.web_dashboard import DashboardServer


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_system():
    """Run AI-Agent-OS system"""
    print("=" * 70)
    print("[LOGO] AI-Agent-OS with Web Dashboard")
    print("=" * 70)
    print("\n[INFO] Starting system...\n")
    
    system = AIAgentOS()
    await system.initialize()
    
    # Create dashboard server
    dashboard = DashboardServer(ai_system=system, command_queue=system.command_queue)
    
    # Run dashboard in background thread
    logger.info("Starting dashboard server...")
    dashboard_thread = threading.Thread(
        target=lambda: dashboard.run(host='0.0.0.0', port=5000),
        daemon=True
    )
    dashboard_thread.start()
    
    print("\n[OK] System Started!")
    print("\n" + "=" * 70)
    print("[DASH] WEB DASHBOARD: http://localhost:5000")
    print("[CLI]  TERMINAL MODE:  Type commands below")
    print("=" * 70 + "\n")
    
    # Run system
    try:
        await system.run()
    except KeyboardInterrupt:
        logger.info("Interrupted")
    finally:
        await system.shutdown()


if __name__ == "__main__":
    try:
        asyncio.run(run_system())
    except KeyboardInterrupt:
        print("\n[EXIT] Goodbye!")
        sys.exit(0)
