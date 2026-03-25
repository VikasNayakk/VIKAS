#!/usr/bin/env python3
"""
Run AI-Agent-OS
"""

import asyncio
import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from main import AIAgentOS


async def main():
    """Main entry point"""
    print("=" * 70)
    print("       🚀 AI-Agent-OS - Autonomous Agent System 🚀")
    print("=" * 70)
    print()
    
    try:
        system = AIAgentOS()
        await system.initialize()
        print("\n✅ System ready!\n")
        
        # Interactive loop
        while True:
            try:
                cmd = input("🤖 > ")
                
                if cmd.lower() in ['exit', 'quit', 'bye', 'stop']:
                    print("👋 Stopping...")
                    break
                
                if cmd.strip():
                    print(f"⏳ Processing: {cmd}")
                    await system.send_command(cmd)
                    await asyncio.sleep(0.5)
            
            except KeyboardInterrupt:
                print("\n👋 Interrupted")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    finally:
        await system.shutdown()
        print("\n✅ System shutdown complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bye!")
        sys.exit(0)
