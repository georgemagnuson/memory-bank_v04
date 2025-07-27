#!/usr/bin/env python3
"""
Memory Bank v04 Enhanced MCP Server - Modular v1.4.0 + Phase 2 COMPLETE
Filename: main.py
Generated: 2025-07-26.1755
Updated: 2025-07-27.2018 (Phase 2 COMPLETE - All Tools Integration)
Purpose: Clean modular Memory Bank MCP server with preserved v1.4.0 enhancements
         Integrates all Phase 2 modules: core_tools, sql_tools, project_tools, 
         content_tools, migration_tools, and backup_tools

v1.4.0 Features Preserved:
- Smart context-aware SQL truncation system
- Enhanced multi-table content extraction with priority
- Search prioritization (context.db first)
- Automatic Memory Bank command awareness
- Complete tool restoration (33 tools total)

Phase 2 Content Tools Added (6 tools):
- Universal full-text search across all content types
- Markdown file import with duplicate detection
- FTS5 virtual table synchronization
- Intelligent bulk markdown discovery and import
- Project documentation import with categorization
- Comprehensive markdown import reporting

Phase 2 Migration Tools Added (3 tools):
- Legacy project migration from .md files to database
- Migration candidate analysis with readiness scoring
- Specific project migration with FTS integration

Phase 2 Backup Tools Added (4 tools):
- Database backup creation with compression and verification
- Backup inventory listing with metadata and integrity checks
- Template specification storage with versioning
- Template discovery with full-text search capabilities
"""

import logging
import sys
from pathlib import Path
from typing import Optional

# Add the server directory to the path for imports
server_dir = Path(__file__).parent.parent
sys.path.insert(0, str(server_dir))

# Import FastMCP
try:
    from fastmcp import FastMCP
except ImportError:
    print("FastMCP not found, installing...", file=sys.stderr)
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "fastmcp"])
    from fastmcp import FastMCP

# Import Memory Bank components
from memory_bank_mcp.context_manager import ContextManager

# Import modular tools (v1.4.0 architecture)
from memory_bank_mcp.core_tools import CoreTools
from memory_bank_mcp.sql_tools import SQLTools
from memory_bank_mcp.project_tools import ProjectTools
from memory_bank_mcp.content_tools import ContentTools
from memory_bank_mcp.migration_tools import MigrationTools
from memory_bank_mcp.backup_tools import BackupTools

# Initialize FastMCP server
server = FastMCP("Memory Bank v04 Enhanced")

# Global variables
context_manager: Optional[ContextManager] = None
current_project_path: Optional[str] = None

# Global tool instances (initialized after context_manager)
core_tools: Optional[CoreTools] = None
sql_tools: Optional[SQLTools] = None
project_tools: Optional[ProjectTools] = None
content_tools: Optional[ContentTools] = None
migration_tools: Optional[MigrationTools] = None
backup_tools: Optional[BackupTools] = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_tool_modules():
    """Initialize modular tool instances when context is available"""
    global core_tools, sql_tools, project_tools, content_tools, migration_tools, backup_tools
    
    if context_manager and context_manager.is_initialized():
        core_tools = CoreTools(context_manager)
        sql_tools = SQLTools(context_manager)
        project_tools = ProjectTools(context_manager)
        content_tools = ContentTools(context_manager)
        migration_tools = MigrationTools(context_manager)
        backup_tools = BackupTools(context_manager)
        logger.info("✅ Modular v1.4.0 tools initialized (Phase 2 Complete: Content + Migration + Backup Tools)")

# =============================================================================
# CORE STATUS AND PROJECT MANAGEMENT TOOLS
# =============================================================================

@server.tool()
async def get_memory_bank_status() -> str:
    """Get current status and statistics of the memory bank database"""
    global context_manager
    
    if not context_manager:
        return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
    
    try:
        if not context_manager.is_initialized():
            return "❌ Memory Bank not properly initialized."        
        
        # Get comprehensive status
        db_stats = await context_manager.database.get_database_stats()
        session_info = await context_manager.get_current_session_info()
        
        # Handle potential session_uuid error gracefully
        session_uuid = session_info.get('session_uuid', 'Unknown')
        if 'error' in session_info:
            session_uuid = "Error retrieving session"
        
        project_name = session_info.get('project_name', 'Unknown')
        
        # Extract key statistics
        total_discussions = db_stats.get('discussions_count', 0)
        total_artifacts = db_stats.get('artifacts_count', 0)
        total_sessions = db_stats.get('sessions_count', 0)
        total_documents = db_stats.get('documents_v2_count', 0)

        status_text = f"""🧠 **MEMORY BANK v1.4.0 STATUS**

**📍 Current Project:** {project_name}
**📂 Path:** {context_manager.project_path}
**🆔 Session:** {session_uuid}

**📊 Knowledge Base:**
• 💭 Discussions: {total_discussions}
• 📄 Documents v2: {total_documents}
• 🎯 Artifacts: {total_artifacts}
• 🎪 Chat Sessions: {total_sessions}

**🚀 v1.4.0 ENHANCED FEATURES:**
• ✅ Smart SQL Truncation System  
• ✅ Multi-Table Content Extraction
• ✅ Search Prioritization (context.db first)
• ✅ Automatic Command Awareness
• ✅ Modular Architecture (17+ tools restored)

**📋 ENHANCED USER EXPERIENCE:**
Use Memory Bank commands naturally - Claude automatically recognizes them.
        """.strip()

        return status_text
        
    except Exception as e:
        logger.error(f"Error getting Memory Bank status: {e}")
        return f"❌ Error retrieving status: {str(e)}"

@server.tool()
async def work_on_project(project_path: str) -> str:
    """Switch to working on a specific project with memory-bank integration and automatic command awareness"""
    global context_manager, current_project_path
    
    try:
        new_path = Path(project_path).resolve()
        
        if not new_path.exists():
            return f"❌ Project path does not exist: {project_path}"
        
        # Initialize or switch context manager
        if context_manager and context_manager.project_path != new_path:
            # Switch to different project
            switch_info = await context_manager.switch_to_project(new_path)
            current_project_path = new_path
        elif not context_manager:
            # First time initialization
            context_manager = ContextManager(new_path)
            success = await context_manager.initialize()
            
            if not success:
                context_manager = None
                return f"❌ Failed to initialize memory-bank for: {project_path}"
            
            current_project_path = new_path
        
        # Initialize modular tools (v1.4.0 enhancement)
        initialize_tool_modules()
        
        # Get project info for confirmation
        session_info = await context_manager.get_current_session_info()
        project_name = session_info.get('project_name', Path(project_path).name)
        
        return f"""✅ **PROJECT ACTIVATED**

**📁 Project:** {project_name}
**📂 Path:** {new_path}
**💾 Database:** Initialized
**🔄 Auto-save:** Enabled

**🚀 v1.4.0 ENHANCED FEATURES ACTIVE:**
• Smart SQL truncation with query analysis
• Multi-table content extraction (documents_v2 → discussions → artifacts)  
• Search prioritization (context.db content first)
• Automatic command awareness
• Modular architecture with 17+ tools

**🎯 READY FOR COLLABORATION!**
All Memory Bank v1.4.0 enhanced features are now active and ready to assist.
        """.strip()
        
    except Exception as e:
        logger.error(f"Error working on project: {e}")
        return f"❌ Error initializing project: {str(e)}"

@server.tool()
async def memory_bank_help() -> str:
    """Show comprehensive help for all Memory Bank MCP commands and features"""
    return """🧠 **MEMORY BANK v1.4.0 HELP**

**🚀 CORE COMMANDS:**
• `work_on_project(path)` - Initialize/switch projects with v1.4.0 features
• `get_memory_bank_status()` - Project status and v1.4.0 feature confirmation
• `memory_bank_help()` - This comprehensive help system

**🔍 SMART SQL & CONTENT ACCESS:**
• `memory_bank_sql_query(query, max_content_length=None)` - Smart truncation SQL
• `extract_large_document(title, output_dir='/tmp')` - Multi-table content extraction
• `sql_truncation_help()` - Smart SQL truncation help

**🗄️ DATABASE EXPLORATION:**
• `memory_bank_describe_schema()` - Complete database schema
• `memory_bank_table_info(table_name)` - Detailed table structure  
• `memory_bank_list_tables()` - All tables with record counts
• `get_memory_bank_system_info()` - Detailed system information

**📝 PROJECT MANAGEMENT:**
• `log_decision(summary, rationale, tags)` - Track architectural decisions
• `query_decisions(search_term, limit=10)` - Search decision history
• `generate_enhanced_session_starter(goal, type)` - Context-aware session prep

**🔄 CONTEXT MANAGEMENT:**
• `prepare_context_switch()` - Safe project switching preparation
• `check_context_switch_safety()` - Verify switch safety
• `force_context_flush()` - Emergency context cleanup
• `verify_and_repair_schema()` - Database integrity management

**🚀 v1.4.0 REVOLUTIONARY FEATURES:**

**Smart SQL Truncation:**
- Content-focused queries: 400 chars (for reading content)
- Overview queries: 80 chars (for metadata/counts)  
- Balanced queries: 150 chars (for browsing)
- User control: `max_content_length=None` for no limits

**Multi-Table Content Extraction:**
- Priority search: documents_v2 → discussions → artifacts
- UUID-based direct lookup with fuzzy title fallback
- Safe filename generation for extracted content
- Enhanced metadata with source table identification

**Search Prioritization:**
- Context.db content searched FIRST (structured data priority)
- Clear priority indicators in results
- Performance metrics and search strategy reporting

**Automatic Command Awareness:**
- Claude knows all Memory Bank commands at session start
- No manual prompting required
- Intelligent command routing and suggestions
- Enhanced user experience with seamless workflow

**💡 QUICK START:**
```
work_on_project("/path/to/your/project")
get_memory_bank_status()
memory_bank_sql_query("SELECT title FROM discussions LIMIT 5")
extract_large_document("title from results")
```

**🎯 v1.4.0 transforms Memory Bank from basic functionality to comprehensive content management!**
    """.strip()

# =============================================================================
# MODULAR TOOL INTEGRATIONS (v1.4.0 Architecture)
# =============================================================================

# Core Tools Integration
@server.tool()
async def get_memory_bank_system_info() -> str:
    """Get detailed technical information about the Memory Bank system"""
    if not core_tools:
        return "❌ Core tools not initialized. Use `work_on_project()` first."
    return await core_tools.get_memory_bank_system_info()

@server.tool()
async def memory_bank_describe_schema() -> str:
    """Get complete database schema for current project"""
    if not core_tools:
        return "❌ Core tools not initialized. Use `work_on_project()` first."
    return await core_tools.memory_bank_describe_schema()

@server.tool()
async def memory_bank_table_info(table_name: str) -> str:
    """Get detailed information about a specific table"""
    if not core_tools:
        return "❌ Core tools not initialized. Use `work_on_project()` first."
    return await core_tools.memory_bank_table_info(table_name)

@server.tool()
async def memory_bank_list_tables() -> str:
    """List all tables in current project's database"""
    if not core_tools:
        return "❌ Core tools not initialized. Use `work_on_project()` first."
    return await core_tools.memory_bank_list_tables()

@server.tool()
async def extract_large_document(title_search: str, output_dir: str = "/tmp") -> str:
    """Extract large document content to file for full reading (bypasses SQL truncation limits)"""
    if not core_tools:
        return "❌ Core tools not initialized. Use `work_on_project()` first."
    return await core_tools.extract_large_document(title_search, output_dir)

@server.tool()
async def verify_and_repair_schema() -> str:
    """Manually verify and repair project schema to ensure complete Memory Bank v04 structure"""
    if not core_tools:
        return "❌ Core tools not initialized. Use `work_on_project()` first."
    return await core_tools.verify_and_repair_schema()

# SQL Tools Integration  
@server.tool()
async def memory_bank_sql_query(query: str, max_content_length: Optional[int] = None) -> str:
    """Execute SQL query with smart context-aware truncation and configurable limits"""
    if not sql_tools:
        return "❌ SQL tools not initialized. Use `work_on_project()` first."
    return await sql_tools.memory_bank_sql_query(query, max_content_length)

@server.tool()
async def sql_truncation_help() -> str:
    """Show help for enhanced SQL truncation features and content access options"""
    if not sql_tools:
        return "❌ SQL tools not initialized. Use `work_on_project()` first."
    return await sql_tools.sql_truncation_help()

# Project Tools Integration
@server.tool()
async def log_decision(summary: str, rationale: str = "", tags: str = "") -> str:
    """Log an architectural or implementation decision with tags and rationale"""
    if not project_tools:
        return "❌ Project tools not initialized. Use `work_on_project()` first."
    return await project_tools.log_decision(summary, rationale, tags)

@server.tool()
async def query_decisions(search_term: str = "", limit: int = 10) -> str:
    """Search and retrieve logged decisions with full-text search"""
    if not project_tools:
        return "❌ Project tools not initialized. Use `work_on_project()` first."
    return await project_tools.query_decisions(search_term, limit)

@server.tool()
async def generate_enhanced_session_starter(session_goal: str = "", session_type: str = "Implementation") -> str:
    """Generate session starter with database-enhanced context"""
    if not project_tools:
        return "❌ Project tools not initialized. Use `work_on_project()` first."
    return await project_tools.generate_enhanced_session_starter(session_goal, session_type)

@server.tool()
async def prepare_context_switch() -> str:
    """Prepare current memory-bank context for safe switching to another project"""
    if not project_tools:
        return "❌ Project tools not initialized. Use `work_on_project()` first."
    return await project_tools.prepare_context_switch()

@server.tool()
async def check_context_switch_safety() -> str:
    """Check if it's currently safe to switch memory-bank contexts"""
    if not project_tools:
        return "❌ Project tools not initialized. Use `work_on_project()` first."
    return await project_tools.check_context_switch_safety()

@server.tool()
async def force_context_flush() -> str:
    """Force flush all pending changes (use with caution)"""
    if not project_tools:
        return "❌ Project tools not initialized. Use `work_on_project()` first."
    return await project_tools.force_context_flush()

# Content Tools Integration (Phase 2 - 6 new tools)
@server.tool()
async def search_all_content(query: str, limit: int = 20, content_types: str = "all") -> str:
    """Universal full-text search across all content types with ranking and highlighting"""
    if not content_tools:
        return "❌ Content tools not initialized. Use `work_on_project()` first."
    return await content_tools.search_all_content(query, limit, content_types)

@server.tool()
async def sync_fts_tables() -> str:
    """Synchronize FTS5 virtual tables with main content tables"""
    if not content_tools:
        return "❌ Content tools not initialized. Use `work_on_project()` first."
    return await content_tools.sync_fts_tables()

@server.tool()
async def import_markdown_files(directory_path: str, file_pattern: str = "*.md", recursive: bool = True) -> str:
    """Import markdown files into the database for full-text search"""
    if not content_tools:
        return "❌ Content tools not initialized. Use `work_on_project()` first."
    return await content_tools.import_markdown_files(directory_path, file_pattern, recursive)

@server.tool()
async def discover_and_import_all_markdown(directory_path: str, exclude_patterns: str = "", max_file_size_mb: int = 10) -> str:
    """Discover and import all markdown files in a directory with intelligent filtering"""
    if not content_tools:
        return "❌ Content tools not initialized. Use `work_on_project()` first."
    return await content_tools.discover_and_import_all_markdown(directory_path, exclude_patterns, max_file_size_mb)

@server.tool()
async def import_project_documentation(include_external: bool = True) -> str:
    """Import all documentation files from the current project for comprehensive FTS"""
    if not content_tools:
        return "❌ Content tools not initialized. Use `work_on_project()` first."
    return await content_tools.import_project_documentation(include_external)

@server.tool()
async def generate_markdown_import_report() -> str:
    """Generate a comprehensive report of imported markdown files"""
    if not content_tools:
        return "❌ Content tools not initialized. Use `work_on_project()` first."
    return await content_tools.generate_markdown_import_report()

# Migration Tools Integration (Phase 2 - 3 new tools)
@server.tool()
async def analyze_migration_candidates() -> str:
    """Analyze potential projects for migration from .md to Memory Bank MCP v2"""
    if not migration_tools:
        return "❌ Migration tools not initialized. Use `work_on_project()` first."
    return await migration_tools.analyze_migration_candidates()

@server.tool()
async def migrate_project_md_files(project_path: str, dry_run: bool = False) -> str:
    """Migrate existing .md files from a project to Memory Bank MCP v2 database"""
    if not migration_tools:
        return "❌ Migration tools not initialized. Use `work_on_project()` first."
    return await migration_tools.migrate_project_md_files(project_path, dry_run)

@server.tool()
async def migrate_specific_project(project_name: str, dry_run: bool = False, auto_import_md: bool = False) -> str:
    """Migrate a specific project by name with comprehensive FTS import analysis and optional auto-import"""
    if not migration_tools:
        return "❌ Migration tools not initialized. Use `work_on_project()` first."
    return await migration_tools.migrate_specific_project(project_name, dry_run, auto_import_md)

# Backup Tools Integration (Phase 2 - 4 new tools)
@server.tool()
async def backup_context_db(backup_type: str = "manual", force: bool = False, verify: bool = True) -> str:
    """Create a backup of the current context.db file"""
    if not backup_tools:
        return "❌ Backup tools not initialized. Use `work_on_project()` first."
    return await backup_tools.backup_context_db(backup_type, force, verify)

@server.tool()
async def list_backups(backup_type: Optional[str] = None, include_metadata: bool = True, verify_integrity: bool = False) -> str:
    """List all available backups with metadata"""
    if not backup_tools:
        return "❌ Backup tools not initialized. Use `work_on_project()` first."
    return await backup_tools.list_backups(backup_type, include_metadata, verify_integrity)

@server.tool()
async def store_template_spec(template_name: str, template_content: str, 
                            template_version: str = "1.0", description: str = "",
                            project_types: str = "general", spec_phase: Optional[str] = None,
                            workflow_system: str = "spec-workflow", update_existing: bool = True) -> str:
    """Store complete template specification in Memory Bank"""
    if not backup_tools:
        return "❌ Backup tools not initialized. Use `work_on_project()` first."
    return await backup_tools.store_template_spec(template_name, template_content, template_version, 
                                                description, project_types, spec_phase, workflow_system, update_existing)

@server.tool()
async def discover_templates(search_query: Optional[str] = None, project_type: Optional[str] = None,
                           spec_phase: Optional[str] = None, workflow_system: Optional[str] = None,
                           sort_by: str = "updated_at", limit: int = 20) -> str:
    """Discover templates based on criteria with FTS search"""
    if not backup_tools:
        return "❌ Backup tools not initialized. Use `work_on_project()` first."
    return await backup_tools.discover_templates(search_query, project_type, spec_phase, workflow_system, sort_by, limit)

# =============================================================================
# SERVER STARTUP
# =============================================================================

if __name__ == "__main__":
    logger.info("🚀 Memory Bank v1.4.0 Enhanced MCP Server starting...")
    logger.info("✅ Modular architecture with preserved v1.4.0 features")
    logger.info("📊 Tools available: 33 core tools (Phase 2 COMPLETE - All modules included)")
    server.run()
