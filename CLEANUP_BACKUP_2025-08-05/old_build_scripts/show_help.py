#!/usr/bin/env python3
"""
show_help.py
Generated: 2025-07-28.1530
Purpose: Quick CLI script to display Memory Bank help

Usage: python show_help.py
"""

import sys
import asyncio
from pathlib import Path

# Add the server directory to path
server_dir = Path(__file__).parent / "server" / "memory_bank_mcp"
sys.path.insert(0, str(server_dir))

async def show_help():
    """Display the Memory Bank help command output"""
    try:
        # Import the help function
        from main import memory_bank_help
        
        print("🚀 Memory Bank v04 Enhanced - Help Command")
        print("=" * 50)
        
        # Call the help function
        help_text = await memory_bank_help()
        print(help_text)
        
        print("\n" + "=" * 50)
        print("💡 To use Memory Bank MCP:")
        print("1. Configure it in your MCP client (Claude Desktop, etc.)")
        print("2. Or run: python server/memory_bank_mcp/main.py")
        print("3. Then call commands like: work_on_project('/path/to/project')")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the Memory Bank root directory")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(show_help())
