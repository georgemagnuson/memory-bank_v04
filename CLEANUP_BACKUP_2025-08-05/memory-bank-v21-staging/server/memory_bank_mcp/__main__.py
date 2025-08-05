#!/usr/bin/env python3
"""
Memory Bank v2.1 Enhanced MCP Server - Main Entry Point
========================================================

Enhanced entry point for Memory Bank v2.1 with integrated modular migration system.
Designed for DXT (Desktop Extension) packaging and deployment.

Features:
- Complete v2.1 migration system integration
- Enhanced work_on_project with automatic migration detection
- Modular architecture with production-ready safety features
- Table count-based version detection
- CLI interface integration
"""

import sys
import os
import logging
from pathlib import Path

# Configure logging for DXT environment
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger("memory_bank_v21_dxt")

def setup_dxt_paths():
    """Setup Python paths for DXT environment with v2.1 migration system"""
    try:
        current_dir = Path(__file__).parent
        dxt_root = current_dir.parent.parent  # Go up to DXT root
        
        # Add migration_v21 to path
        migration_path = dxt_root / "migration_v21"
        if migration_path.exists():
            sys.path.insert(0, str(migration_path))
            logger.info(f"✅ Added migration_v21 to path: {migration_path}")
        else:
            logger.warning(f"⚠️ migration_v21 path not found: {migration_path}")
        
        # Add server path
        server_path = current_dir
        if server_path not in [Path(p) for p in sys.path]:
            sys.path.insert(0, str(server_path))
            logger.info(f"✅ Added server to path: {server_path}")
        
        # Add DXT root to path
        if str(dxt_root) not in sys.path:
            sys.path.insert(0, str(dxt_root))
            logger.info(f"✅ Added DXT root to path: {dxt_root}")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to setup DXT paths: {e}")
        return False

def check_migration_system():
    """Check if v2.1 migration system is available"""
    try:
        from migration_v21 import MigrationManager, integrate_with_memory_bank
        logger.info("✅ v2.1 Migration system available")
        
        # Test integration
        integration_results = integrate_with_memory_bank()
        logger.info(f"✅ Migration system integration: {integration_results}")
        return True
        
    except ImportError as e:
        logger.warning(f"⚠️ v2.1 Migration system not available: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Migration system integration failed: {e}")
        return False

def main():
    """Main entry point for Memory Bank v2.1 Enhanced MCP Server"""
    try:
        logger.info("🚀 Starting Memory Bank v2.1 Enhanced MCP Server (DXT)")
        logger.info("📦 Package: Desktop Extension with modular migration system")
        
        # Setup DXT environment paths
        if not setup_dxt_paths():
            logger.error("❌ Failed to setup DXT environment")
            sys.exit(1)
        
        # Check migration system availability
        migration_available = check_migration_system()
        if migration_available:
            logger.info("✨ v2.1 Enhanced features: Migration system ready")
        else:
            logger.info("📋 Fallback mode: Legacy Memory Bank tools only")
        
        # Import and start main server
        try:
            from memory_bank_mcp.main import main as server_main
            logger.info("✅ Memory Bank MCP server imported successfully")
            
            # Start the server
            logger.info("🚀 Launching Memory Bank v2.1 Enhanced MCP Server...")
            server_main()
            
        except ImportError as e:
            logger.error(f"❌ Failed to import Memory Bank MCP server: {e}")
            logger.error("Please ensure all required modules are present in the DXT package")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Memory Bank v2.1 server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Memory Bank v2.1 server failed to start: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    main()
