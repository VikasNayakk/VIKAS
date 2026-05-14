"""
Quick smoke test for the Anthropic integration.

Run:
    cd VIKAS/AI-Agent-OS
    pip install -r requirements.txt
    python scripts/test_anthropic.py
"""

import sys
from pathlib import Path

# Make project root importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from integrations.anthropic_client import ClaudeClient  # noqa: E402


def main() -> int:
    try:
        claude = ClaudeClient()
    except RuntimeError as exc:
        print(f"[SETUP ERROR] {exc}")
        return 1

    print(f"[OK] Using model: {claude.model}")
    print("[..] Sending test prompt...")
    try:
        reply = claude.ask("Reply with exactly: 'Aliens AI online.'")
    except Exception as exc:  # noqa: BLE001
        print(f"[API ERROR] {exc}")
        return 2

    print(f"[Claude] {reply}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
