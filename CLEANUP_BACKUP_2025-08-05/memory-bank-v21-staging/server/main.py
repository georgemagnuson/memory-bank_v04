#!/usr/bin/env python3
"""
server/main.py
Generated: 2025-07-22.0040
Purpose: DXT Entry Point for Memory Bank MCP v2 with Bundled Dependencies

Desktop Extension entry point implementing the Model Context Protocol (MCP) server
with enhanced documents_v2 full-text search capabilities and spec workflow integration.

DXT Architecture:
- Single entry point for Claude Desktop extension loading
- Bundled dependencies in lib/ directory for self-contained operation
- Defensive programming with comprehensive error handling
- Proper MCP protocol compliance via stdio transport
- Enhanced FTS search across all content types including documents_v2
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Add lib directory and server directory to path for imports (DXT bundled dependencies)
script_dir = Path(__file__).parent
lib_dir = script_dir.parent / "lib"
sys.path.insert(0, str(lib_dir))  # Bundled dependencies first
sys.path.insert(0, str(script_dir))  # Server directory second

# Configure logging for DXT environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(script_dir.parent / 'memory_bank_v04.log'),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger("memory_bank_v04.dxt")

def main():
    """
    DXT entry point for Memory Bank MCP v2 server
    
    Implements enhanced MCP server with documents_v2 search capabilities
    following DXT best practices for defensive programming and error handling.
    Uses bundled dependencies from lib/ directory for self-contained operation.
    """
    try:
        # Import and run the FastMCP server from memory_bank_mcp
        from memory_bank_mcp.main import server
        
        logger.info("Memory Bank v04 DXT Extension starting...")
        logger.info(f"Script directory: {script_dir}")
        logger.info(f"Lib directory: {lib_dir}")
        logger.info(f"Python path: {sys.path[:5]}...")  # Show first 5 paths
        
        # Run the FastMCP server with stdio transport (required for DXT)
        server.run()
        
    except ImportError as e:
        logger.error(f"Failed to import memory_bank_mcp: {e}")
        logger.error(f"Current directory: {os.getcwd()}")
        logger.error(f"Script directory: {script_dir}")
        logger.error(f"Lib directory: {lib_dir}")
        logger.error(f"Available files in script dir: {list(script_dir.iterdir()) if script_dir.exists() else 'Directory not found'}")
        logger.error(f"Available files in lib dir: {list(lib_dir.iterdir()) if lib_dir.exists() else 'Directory not found'}")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error in Memory Bank DXT: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
