#!/usr/bin/env python3
"""
Memory Bank v2.0 Enhanced MCP Server - Production Version
Filename: main.py
Generated: 2025-08-01.0056 (Server startup fix)
Purpose: Production-ready Memory Bank v2.0 MCP server with corrected server startup

FINAL FIX: Corrected stdio server startup to use FastMCP's built-in run() method
"""

import logging
import asyncio
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("memory_bank_v2.dxt")

def setup_dxt_environment():
    """Setup proper Python path for DXT environment"""
    try:
        # Get the DXT extension directory
        script_path = Path(__file__).resolve()
        script_dir = script_path.parent
        dxt_root = script_dir.parent.parent  # Go up to DXT root
        lib_dir = dxt_root / "lib"
        
        logger.info(f"Setting up DXT environment:")
        logger.info(f"Script path: {script_path}")
        logger.info(f"Script dir: {script_dir}")
        logger.info(f"DXT root: {dxt_root}")
        logger.info(f"Lib dir: {lib_dir}")
        
        # Add directories to Python path
        paths_to_add = [
            str(script_dir),          # Current directory (memory_bank_mcp)
            str(lib_dir),             # Bundled libraries
            str(dxt_root),            # DXT root
        ]
        
        for path in paths_to_add:
            if path not in sys.path:
                sys.path.insert(0, path)
                logger.info(f"Added to Python path: {path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup DXT environment: {e}")
        return False

# Setup DXT environment before any imports
if not setup_dxt_environment():
    logger.error("Failed to setup DXT environment - exiting")
    sys.exit(1)

# Now try to import MCP framework
try:
    from mcp import types
    from mcp.server.fastmcp import FastMCP
    logger.info("Successfully imported MCP framework")
except ImportError as e:
    logger.error(f"Failed to import MCP framework: {e}")
    sys.exit(1)

# Import Memory Bank modules with error handling
try:
    # Try absolute imports first
    from memory_bank_mcp.context_manager import ContextManager
    from memory_bank_mcp.core_tools import CoreTools
    from memory_bank_mcp.sql_tools import SQLTools
    from memory_bank_mcp.project_tools import ProjectTools
    from memory_bank_mcp.content_tools import ContentTools
    from memory_bank_mcp.migration_tools import MigrationTools
    from memory_bank_mcp.backup_tools import BackupTools
    logger.info("Successfully imported Memory Bank modules (absolute)")
    
except ImportError:
    logger.info("Absolute imports failed, trying relative imports...")
    try:
        # Try relative imports
        from .context_manager import ContextManager
        from .core_tools import CoreTools
        from .sql_tools import SQLTools
        from .project_tools import ProjectTools
        from .content_tools import ContentTools
        from .migration_tools import MigrationTools
        from .backup_tools import BackupTools
        logger.info("Successfully imported Memory Bank modules (relative)")
        
    except ImportError:
        logger.info("Relative imports failed, trying local imports...")
        try:
            # Try local imports without package prefixes
            from context_manager import ContextManager
            from core_tools import CoreTools
            from sql_tools import SQLTools
            from project_tools import ProjectTools
            from content_tools import ContentTools
            from migration_tools import MigrationTools
            from backup_tools import BackupTools
            logger.info("Successfully imported Memory Bank modules (local)")
            
        except ImportError as e:
            logger.error(f"All import attempts failed: {e}")
            logger.error("Cannot start Memory Bank v2.0 - missing required modules")
            sys.exit(1)

# Global variables for components
context_manager = None
core_tools = None
sql_tools = None
project_tools = None
content_tools = None
migration_tools = None
backup_tools = None

async def initialize_memory_bank():
    """Initialize all Memory Bank components - FIXED: No longer calls non-existent initialize() methods"""
    global context_manager, core_tools, sql_tools, project_tools, content_tools, migration_tools, backup_tools
    
    try:
        logger.info("Initializing Memory Bank v2.0 Enhanced...")
        
        # Note: Context Manager will be initialized per-project via work_on_project()
        # Global tools are created but not bound to specific project until work_on_project() is called
        
        logger.info("✅ Memory Bank v2.0 Enhanced ready for work_on_project() calls")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Memory Bank: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

async def initialize_project_tools(project_context_manager):
    """Initialize all tool modules for a specific project context"""
    global core_tools, sql_tools, project_tools, content_tools, migration_tools, backup_tools
    
    try:
        # Initialize tool modules with project context
        core_tools = CoreTools(project_context_manager)
        logger.info("✓ Core Tools initialized for project")
        
        sql_tools = SQLTools(project_context_manager)
        logger.info("✓ SQL Tools initialized for project")
        
        project_tools = ProjectTools(project_context_manager)  
        logger.info("✓ Project Tools initialized for project")
        
        content_tools = ContentTools(project_context_manager)
        logger.info("✓ Content Tools initialized for project")
        
        migration_tools = MigrationTools(project_context_manager)
        logger.info("✓ Migration Tools initialized for project")
        
        backup_tools = BackupTools(project_context_manager)
        logger.info("✓ Backup Tools initialized for project")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize project tools: {e}")
        return False

# Define lifespan context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Memory Bank v2.0 Enhanced starting up...")
    success = await initialize_memory_bank()
    if success:
        logger.info("Memory Bank v2.0 Enhanced startup complete")
    else:
        logger.error("Memory Bank v2.0 Enhanced startup failed")
    
    yield  # Server runs here
    
    # Shutdown
    global context_manager
    if context_manager:
        try:
            await context_manager.save_context()
            await context_manager.close()
            logger.info("Context saved and closed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    logger.info("Memory Bank v2.0 Enhanced shutdown complete")

# Initialize FastMCP server with lifespan
server = FastMCP(
    name="Memory Bank v2.0 Enhanced",
    lifespan=lifespan
)

# Tool definitions
@server.tool()
async def memory_bank_help() -> str:
    """Show comprehensive help for Memory Bank v2.0 Enhanced"""
    return """
# Memory Bank v2.0 Enhanced - Help Guide

## Primary Tool:
- work_on_project(project_path) - Switch to working on a specific project (REQUIRED FIRST STEP)

## Core Operations:
- create_context(project_name) - Create new project context
- switch_context(project_name) - Switch to existing project  
- save_info(content, category, tags) - Save information
- search_info(query, limit) - Search saved content
- list_contexts() - Show all projects
- get_current_context() - Current project info

## SQL & Database:
- execute_sql(query) - Run SQL on current database
- show_schema() - Display database structure
- analyze_database() - Analyze content and structure

## Project Management:
- get_project_summary() - Comprehensive project overview
- set_project_metadata(key, value) - Set project properties
- get_project_metadata(key) - Get project properties

## Document Management:
- save_document(title, content, type, tags) - Save documents
- search_documents(query, limit) - Search documents
- list_documents(type, limit) - List documents
- get_document(title) - Retrieve specific document

## Migration & Backup:
- migrate_from_v1() - Migrate from v1.x to v2.0
- check_migration_status() - Check migration status
- create_backup(name) - Create backup
- list_backups() - Show available backups
- restore_backup(name) - Restore from backup

## Features:
✅ 30+ tools across 6 modular components
✅ Smart context-aware operations
✅ Full-text search capabilities
✅ Cross-project compatibility
✅ Automated backup system
✅ Migration support from v1.x

Memory Bank v2.0 Enhanced - Your AI collaboration memory, evolved.
"""

# Primary project management tool (v1.4.0 compatibility)
@server.tool()
async def work_on_project(project_path: str) -> str:
    """
    Switch to working on a specific project with memory-bank integration and schema auto-migration
    
    This is the primary tool for starting work on any project. It will:
    1. Save current context if active
    2. Switch to new project path  
    3. Load project_path/memory-bank/context.db if exists
    4. If no context.db, create one with v2.0 schema
    5. If context.db exists but is v1.4.0 schema, offer migration to v2.0
    6. Initialize all Memory Bank tools for the project
    
    Args:
        project_path: Path to the project directory (will look for memory-bank/context.db inside)
    """
    global context_manager, core_tools, sql_tools, project_tools, content_tools, migration_tools, backup_tools
    
    try:
        from pathlib import Path
        from .schema_manager import SchemaManager
        from .context_manager import ContextManager
        
        # Validate project path
        project_dir = Path(project_path).resolve()
        if not project_dir.exists():
            return f"❌ Project path does not exist: {project_path}"
        
        if not project_dir.is_dir():
            return f"❌ Project path is not a directory: {project_path}"
        
        # Define memory-bank directory and database path
        memory_bank_dir = project_dir / "memory-bank"
        context_db_path = memory_bank_dir / "context.db"
        
        # Create memory-bank directory if it doesn't exist
        memory_bank_dir.mkdir(exist_ok=True)
        
        # Save current context if we have an active one
        if context_manager and context_manager.is_initialized():
            try:
                await context_manager.save_context()
                await context_manager.close()
                logger.info("✅ Saved and closed previous context")
            except Exception as e:
                logger.warning(f"Error saving previous context: {e}")
        
        # Initialize new context manager for this project
        context_manager = ContextManager(project_dir)
        await context_manager.initialize()
        
        # Initialize project tools
        success = await initialize_project_tools(context_manager)
        if not success:
            return f"❌ Failed to initialize project tools for: {project_path}"
        
        # Check and handle database schema
        schema_manager = SchemaManager(context_manager)
        schema_status = await schema_manager.check_and_upgrade_database()
        
        project_name = project_dir.name
        
        return f"""✅ **Working on Project: {project_name}**

📁 **Project Path:** {project_path}
💾 **Database:** {context_db_path}

{schema_status}

🛠️  **Tools Initialized:**
• Core Tools: ✅ Ready for content operations
• SQL Tools: ✅ Ready for database queries  
• Project Tools: ✅ Ready for project management
• Content Tools: ✅ Ready for document management
• Migration Tools: ✅ Ready for schema operations
• Backup Tools: ✅ Ready for data protection

🚀 **Memory Bank v2.0 Ready!** You can now use all Memory Bank tools for this project.

💡 **Quick Start:**
• `get_current_context()` - Check project status
• `save_info("content", "category")` - Save information  
• `search_info("query")` - Find saved content
• `execute_sql("SELECT * FROM documents LIMIT 5")` - Query database
"""
        
    except Exception as e:
        logger.error(f"Error working on project '{project_path}': {e}")
        return f"❌ Error initializing project: {str(e)}"

# Core tool implementations
@server.tool()
async def create_context(project_name: str) -> str:
    """Create a new project context"""
    if not core_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await core_tools.create_context(project_name)

@server.tool()
async def switch_context(project_name: str) -> str:
    """Switch to an existing project context"""
    if not core_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await core_tools.switch_context(project_name)

@server.tool()
async def save_info(content: str, category: str = "general", tags: str = "") -> str:
    """Save information to current context"""
    if not core_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await core_tools.save_info(content, category, tags)

@server.tool()
async def search_info(query: str, limit: int = 10) -> str:
    """Search saved information"""
    if not core_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await core_tools.search_info(query, limit)

@server.tool()
async def list_contexts() -> str:
    """List all available project contexts"""
    if not core_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await core_tools.list_contexts()

@server.tool() 
async def get_current_context() -> str:
    """Get current project context information"""
    if not core_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await core_tools.get_current_context()

@server.tool()
async def execute_sql(query: str) -> str:
    """Execute SQL query on current context database"""
    if not sql_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await sql_tools.execute_sql(query)

@server.tool()
async def show_schema() -> str:
    """Show database schema for current context"""
    if not sql_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await sql_tools.show_schema()

@server.tool()
async def analyze_database() -> str:
    """Analyze database structure and content"""
    if not sql_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await sql_tools.analyze_database()

@server.tool()
async def get_project_summary() -> str:
    """Get comprehensive project summary"""
    if not project_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await project_tools.get_project_summary()

@server.tool()
async def set_project_metadata(key: str, value: str) -> str:
    """Set project metadata"""
    if not project_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await project_tools.set_project_metadata(key, value)

@server.tool()
async def get_project_metadata(key: str = "") -> str:
    """Get project metadata"""
    if not project_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await project_tools.get_project_metadata(key)

@server.tool()
async def save_document(title: str, content: str, doc_type: str = "general", tags: str = "") -> str:
    """Save a document to the current context"""
    if not content_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await content_tools.save_document(title, content, doc_type, tags)

@server.tool()
async def search_documents(query: str, limit: int = 10) -> str:
    """Search documents in current context"""
    if not content_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await content_tools.search_documents(query, limit)

@server.tool()
async def list_documents(doc_type: str = "", limit: int = 20) -> str:
    """List documents in current context"""
    if not content_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await content_tools.list_documents(doc_type, limit)

@server.tool()
async def get_document(title: str) -> str:
    """Get a specific document by title"""
    if not content_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await content_tools.get_document(title)

@server.tool()
async def migrate_from_v1() -> str:
    """Migrate data from Memory Bank v1.x to v2.0"""
    if not migration_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await migration_tools.migrate_from_v1()

@server.tool()
async def migrate_to_v2(confirm: bool = False) -> str:
    """Migrate database schema from unified_documents to documents table (v1.4.0 → v2.0)"""
    if not schema_manager:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await schema_manager.migrate_to_v2(confirm=confirm)

@server.tool()
async def check_migration_status() -> str:
    """Check migration status and compatibility"""
    if not migration_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await migration_tools.check_migration_status()

@server.tool()
async def create_backup(backup_name: str = "") -> str:
    """Create a backup of current context"""
    if not backup_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await backup_tools.create_backup(backup_name)

@server.tool()
async def list_backups() -> str:
    """List available backups"""
    if not backup_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await backup_tools.list_backups()

@server.tool()
async def restore_backup(backup_name: str) -> str:
    """Restore from a backup"""
    if not backup_tools:
        return "❌ Memory Bank not initialized. Please restart Claude Desktop."
    return await backup_tools.restore_backup(backup_name)

# Main function for module execution
def main():
    """Main entry point for Memory Bank v2.0 Enhanced MCP Server"""
    logger.info("Starting Memory Bank v2.0 Enhanced MCP Server...")
    try:
        # Use FastMCP's built-in run method for stdio
        server.run(transport="stdio")
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

# Main execution
if __name__ == "__main__":
    main()
