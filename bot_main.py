"""
Legacy entry point for the Telegram bot.

This file is kept for backward compatibility.
Please use: python -m cad_p
"""

import sys
from pathlib import Path

# Add src to path if needed
src_path = Path(__file__).parent / "src"
if src_path.exists() and str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

# Import and run the main bot
from cad_p.bot import main

if __name__ == '__main__':
    print("Note: This is the legacy entrypoint. Please use: python -m cad_p")
    main()
