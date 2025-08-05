#!/usr/bin/env python3
"""
Memory Bank v2.1 Enhanced MCP Server - Module Entry Point
=========================================================

Enhanced entry point with v2.1 migration system integration.
Supports both standalone execution and DXT environment deployment.
"""

import sys
import os
from pathlib import Path

# Setup paths for both standalone and DXT environments
def setup_paths():
    """Setup Python paths for v2.1 migration system"""
    current_dir = Path(__file__).parent
    
    # Ensure the memory_bank_mcp directory is in the Python path
    mcp_dir = current_dir.parent
    if str(mcp_dir) not in sys.path:
        sys.path.insert(0, str(mcp_dir))
    
    # Add migration_v21 to path (for DXT environment)
    dxt_root = mcp_dir.parent  # Go up to potential DXT root
    migration_path = dxt_root / "migration_v21"
    if migration_path.exists() and str(migration_path) not in sys.path:
        sys.path.insert(0, str(migration_path))
        print(f"✅ Added migration_v21 to path: {migration_path}", file=sys.stderr)

# Setup paths before imports
setup_paths()

try:
    from memory_bank_mcp.main import main
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    print(f"Python path: {sys.path}", file=sys.stderr)
    print(f"Current directory: {os.getcwd()}", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
