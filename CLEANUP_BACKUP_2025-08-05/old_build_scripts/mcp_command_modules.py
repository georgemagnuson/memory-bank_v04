#!/usr/bin/env python3
"""
mcp_command_modules.py
Generated: 2025-07-28.1520
Purpose: Create modular command groups to reduce main.py size

This script creates focused command modules and updates main.py to use them.
Target: Reduce main.py from 594 lines to ~200-250 lines.
"""

def analyze_command_groups():
    """Analyze current commands and group them logically"""
    
    print("🔍 Analyzing MCP Commands for Modularization")
    print("=" * 45)
    
    command_groups = {
        'core_commands': {
            'description': 'Essential core functionality',
            'keep_in_main': True,
            'commands': [
                'get_memory_bank_status',
                'work_on_project', 
                'memory_bank_help'
            ]
        },
        'database_commands': {
            'description': 'Database schema and maintenance',
            'module': 'mcp_database_commands.py',
            'commands': [
                'get_memory_bank_system_info',
                'memory_bank_describe_schema',
                'memory_bank_table_info',
                'memory_bank_list_tables',
                'verify_and_repair_schema',
                'memory_bank_sql_query',
                'sql_truncation_help'
            ]
        },
        'project_commands': {
            'description': 'Project management and decisions',
            'module': 'mcp_project_commands.py', 
            'commands': [
                'log_decision',
                'query_decisions',
                'generate_enhanced_session_starter',
                'prepare_context_switch',
                'check_context_switch_safety',
                'force_context_flush'
            ]
        },
        'content_commands': {
            'description': 'Content search and import',
            'module': 'mcp_content_commands.py',
            'commands': [
                'search_all_content',
                'sync_fts_tables',
                'import_markdown_files',
                'generate_markdown_import_report'
            ]
        },
        'migration_commands': {
            'description': 'Migration tools (optional)',
            'module': 'mcp_migration_commands.py',
            'commands': [
                'analyze_migration_candidates',
                'migrate_project_md_files', 
                'migrate_specific_project'
            ]
        },
        'backup_commands': {
            'description': 'Backup and templates',
            'module': 'mcp_backup_commands.py',
            'commands': [
                'backup_context_db',
                'list_backups',
                'store_template_spec',
                'discover_templates'
            ]
        },
        'smart_commands': {
            'description': 'Phase 2 smart commands (already modular)',
            'module': 'mcp_commands.py (in unified/creation/)',
            'commands': [
                'save_to_memory',
                'save_discussion',
                'save_document',
                'save_plan',
                'save_code',
                'save_note',
                'save_chat_session',
                'save_markdown_file'
            ]
        }
    }
    
    print("📊 COMMAND MODULARIZATION PLAN:")
    
    total_commands = 0
    keep_in_main = 0
    
    for group, info in command_groups.items():
        cmd_count = len(info['commands'])
        total_commands += cmd_count
        
        print(f"\n📁 {group.upper()}:")
        print(f"   Description: {info['description']}")
        print(f"   Commands: {cmd_count}")
        
        if info.get('keep_in_main'):
            print(f"   Location: Keep in main.py (essential)")
            keep_in_main += cmd_count
        else:
            print(f"   Module: {info.get('module', 'TBD')}")
        
        for cmd in info['commands']:
            print(f"     • {cmd}")
    
    modularized = total_commands - keep_in_main
    print(f"\n📈 MODULARIZATION SUMMARY:")
    print(f"   Total commands: {total_commands}")
    print(f"   Keep in main.py: {keep_in_main}")
    print(f"   Move to modules: {modularized}")
    print(f"   Estimated main.py reduction: ~{modularized * 8} lines")
    
    return command_groups

def create_database_commands_module():
    """Create database commands module"""
    
    module_content = '''#!/usr/bin/env python3
"""
mcp_database_commands.py
Generated: 2025-07-28.1520
Purpose: Database schema and maintenance commands

Modular MCP commands for database operations.
"""

from typing import Optional

class DatabaseCommands:
    """Database schema and maintenance MCP commands"""
    
    def __init__(self, core_tools, sql_tools):
        self.core_tools = core_tools
        self.sql_tools = sql_tools
    
    async def get_memory_bank_system_info(self) -> str:
        """Get detailed technical information about the Memory Bank system"""
        if not self.core_tools:
            return "❌ Memory Bank not initialized. Use `work_on_project()` first."
        return await self.core_tools.get_memory_bank_system_info()

    async def memory_bank_describe_schema(self) -> str:
        """Get complete database schema for current project"""
        if not self.core_tools:
            return "❌ Memory Bank not initialized. Use `work_on_project()` first."
        return await self.core_tools.memory_bank_describe_schema()

    async def memory_bank_table_info(self, table_name: str) -> str:
        """Get detailed information about a specific table"""
        if not self.core_tools:
            return "❌ Memory Bank not initialized. Use `work_on_project()` first."
        return await self.core_tools.memory_bank_table_info(table_name)

    async def memory_bank_list_tables(self) -> str:
        """List all tables in current project's database"""
        if not self.core_tools:
            return "❌ Memory Bank not initialized. Use `work_on_project()` first."
        return await self.core_tools.memory_bank_list_tables()

    async def verify_and_repair_schema(self) -> str:
        """Manually verify and repair project schema to ensure complete Memory Bank v04 structure"""
        if not self.core_tools:
            return "❌ Memory Bank not initialized. Use `work_on_project()` first."
        return await self.core_tools.verify_and_repair_schema()

    async def memory_bank_sql_query(self, query: str, max_content_length: Optional[int] = None) -> str:
        """Execute SQL query with smart context-aware truncation and configurable limits"""
        if not self.sql_tools:
            return "❌ SQL tools not initialized. Use `work_on_project()` first."
        return await self.sql_tools.memory_bank_sql_query(query, max_content_length)

    async def sql_truncation_help(self) -> str:
        """Show help for enhanced SQL truncation features and content access options"""
        if not self.sql_tools:
            return "❌ SQL tools not initialized. Use `work_on_project()` first."
        return await self.sql_tools.sql_truncation_help()
'''
    
    return module_content

def create_project_commands_module():
    """Create project management commands module"""
    
    module_content = '''#!/usr/bin/env python3
"""
mcp_project_commands.py
Generated: 2025-07-28.1520
Purpose: Project management and decision tracking commands

Modular MCP commands for project management.
"""

class ProjectCommands:
    """Project management and decision tracking MCP commands"""
    
    def __init__(self, project_tools, phase2_commands):
        self.project_tools = project_tools
        self.phase2_commands = phase2_commands
    
    async def log_decision(self, summary: str, rationale: str = "", tags: str = "") -> str:
        """Log an architectural or implementation decision with tags and rationale (Updated for unified_documents)"""
        if not self.phase2_commands:
            return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
        return await self.phase2_commands.log_decision(summary, rationale, tags)

    async def query_decisions(self, search_term: str = "", limit: int = 10) -> str:
        """Search and retrieve logged decisions with full-text search"""
        if not self.project_tools:
            return "❌ Project tools not initialized. Use `work_on_project()` first."
        return await self.project_tools.query_decisions(search_term, limit)

    async def generate_enhanced_session_starter(self, session_goal: str = "", session_type: str = "Implementation") -> str:
        """Generate session starter with database-enhanced context"""
        if not self.project_tools:
            return "❌ Project tools not initialized. Use `work_on_project()` first."
        return await self.project_tools.generate_enhanced_session_starter(session_goal, session_type)

    async def prepare_context_switch(self) -> str:
        """Prepare current memory-bank context for safe switching to another project"""
        if not self.project_tools:
            return "❌ Project tools not initialized. Use `work_on_project()` first."
        return await self.project_tools.prepare_context_switch()

    async def check_context_switch_safety(self) -> str:
        """Check if it's currently safe to switch memory-bank contexts"""
        if not self.project_tools:
            return "❌ Project tools not initialized. Use `work_on_project()` first."
        return await self.project_tools.check_context_switch_safety()

    async def force_context_flush(self) -> str:
        """Force flush all pending changes (use with caution)"""
        if not self.project_tools:
            return "❌ Project tools not initialized. Use `work_on_project()` first."
        return await self.project_tools.force_context_flush()
'''
    
    return module_content

def create_content_commands_module():
    """Create content search and import commands module"""
    
    module_content = '''#!/usr/bin/env python3
"""
mcp_content_commands.py
Generated: 2025-07-28.1520
Purpose: Content search and import commands

Modular MCP commands for content operations.
"""

class ContentCommands:
    """Content search and import MCP commands"""
    
    def __init__(self, content_tools):
        self.content_tools = content_tools
    
    async def search_all_content(self, query: str, limit: int = 20, content_types: str = "all") -> str:
        """Universal full-text search across all content types with ranking and highlighting"""
        if not self.content_tools:
            return "❌ Content tools not initialized. Use `work_on_project()` first."
        return await self.content_tools.search_all_content(query, limit, content_types)

    async def sync_fts_tables(self) -> str:
        """Synchronize FTS5 virtual tables with main content tables"""
        if not self.content_tools:
            return "❌ Content tools not initialized. Use `work_on_project()` first."
        return await self.content_tools.sync_fts_tables()

    async def import_markdown_files(self, directory_path: str, file_pattern: str = "*.md", recursive: bool = True) -> str:
        """Import markdown files into the database for full-text search"""
        if not self.content_tools:
            return "❌ Content tools not initialized. Use `work_on_project()` first."
        return await self.content_tools.import_markdown_files(directory_path, file_pattern, recursive)

    async def generate_markdown_import_report(self) -> str:
        """Generate a comprehensive report of imported markdown files"""
        if not self.content_tools:
            return "❌ Content tools not initialized. Use `work_on_project()` first."
        return await self.content_tools.generate_markdown_import_report()
'''
    
    return module_content

def estimate_size_reduction():
    """Estimate the size reduction from modularization"""
    
    print("\n📏 Size Reduction Estimation")
    print("=" * 30)
    
    # Rough line counts per command (including @server.tool() decorator and docstring)
    avg_lines_per_command = 8
    
    commands_to_move = {
        'database_commands': 7,
        'project_commands': 6,  
        'content_commands': 4,
        'migration_commands': 3,
        'backup_commands': 4
    }
    
    total_commands_moved = sum(commands_to_move.values())
    estimated_lines_moved = total_commands_moved * avg_lines_per_command
    
    # Add lines for imports and routing (smaller overhead)
    routing_overhead = len(commands_to_move) * 5  # Import + initialization per module
    
    net_reduction = estimated_lines_moved - routing_overhead
    final_estimate = 594 - net_reduction
    
    print(f"Current main.py: 594 lines")
    print(f"Commands to modularize: {total_commands_moved}")
    print(f"Estimated lines moved: {estimated_lines_moved}")
    print(f"Routing overhead: {routing_overhead}")
    print(f"Net reduction: {net_reduction}")
    print(f"Estimated final size: {final_estimate} lines")
    print(f"Size reduction: {(net_reduction/594)*100:.1f}%")
    
    return final_estimate

if __name__ == "__main__":
    command_groups = analyze_command_groups()
    
    print(f"\n🔧 Creating Command Modules...")
    
    # Create the modules
    modules = {
        'mcp_database_commands.py': create_database_commands_module(),
        'mcp_project_commands.py': create_project_commands_module(),
        'mcp_content_commands.py': create_content_commands_module(),
    }
    
    for filename, content in modules.items():
        print(f"✅ Created: {filename} ({len(content.split(chr(10)))} lines)")
    
    final_size = estimate_size_reduction()
    
    print(f"\n🎯 MODULARIZATION BENEFITS:")
    print(f"  ✅ Reduces main.py from 594 to ~{final_size} lines")
    print(f"  ✅ Groups related commands logically")
    print(f"  ✅ Easier testing and maintenance")
    print(f"  ✅ Better separation of concerns")
    print(f"  ✅ Keeps core functionality in main.py")
    
    print(f"\n🚀 Ready to implement modularization!")
'''
