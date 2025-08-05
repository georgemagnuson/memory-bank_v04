#!/usr/bin/env python3
"""
Memory Bank MCP v2 - Module Entry Point
Generated: 2025-07-13.1843
Enhanced AI collaboration memory system with persistent database storage
"""

import sys
import os
from pathlib import Path

# Ensure the memory_bank_mcp directory is in the Python path
mcp_dir = Path(__file__).parent.parent
if str(mcp_dir) not in sys.path:
    sys.path.insert(0, str(mcp_dir))

try:
    from memory_bank_mcp.main import main
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    print(f"Current directory: {os.getcwd()}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
