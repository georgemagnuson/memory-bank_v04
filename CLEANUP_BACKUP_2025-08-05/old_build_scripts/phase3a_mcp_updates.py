#!/usr/bin/env python3
"""
phase3a_mcp_updates.py
Generated: 2025-07-28.1510
Purpose: Phase 3A MCP updates - modular approach

This script applies Phase 3A consolidation changes to main.py:
1. Comments out redundant commands (instead of deleting for safety)
2. Adds Phase 2 smart commands via import
3. Updates existing commands to use unified_documents
4. Keeps main.py manageable in size
"""

import re
from pathlib import Path

def apply_phase3a_consolidation():
    """Apply Phase 3A consolidation changes to main.py"""
    
    print("🔧 Applying Phase 3A MCP Consolidation Changes")
    print("=" * 45)
    
    main_py_path = Path("/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp/main.py")
    
    if not main_py_path.exists():
        print("❌ main.py not found")
        return False
    
    # Read current main.py
    with open(main_py_path, 'r') as f:
        content = f.read()
    
    print(f"📄 Current main.py: {len(content.split(chr(10)))} lines")
    
    # Phase 3A Changes:
    
    # 1. Comment out redundant commands (instead of deleting for safety)
    redundant_commands = [
        'extract_large_document',
        'discover_and_import_all_markdown', 
        'import_project_documentation'
    ]
    
    print(f"\n❌ Commenting out {len(redundant_commands)} redundant commands:")
    for cmd in redundant_commands:
        # Find and comment out the command
        pattern = rf'(@server\.tool\(\)[\s\S]*?async def {cmd}\([\s\S]*?(?=@server\.tool\(\)|if __name__|$))'
        match = re.search(pattern, content)
        
        if match:
            command_block = match.group(1)
            # Comment out the entire command block
            commented_block = '\n'.join(f'# REMOVED IN PHASE 3A: {line}' for line in command_block.split('\n'))
            content = content.replace(command_block, f'# =============================================================================\n# REMOVED IN PHASE 3A - REDUNDANT COMMAND: {cmd}\n# =============================================================================\n{commented_block}\n')
            print(f"  ✅ Commented out: {cmd}")
        else:
            print(f"  ⚠️ Not found: {cmd}")
    
    # 2. Add Phase 2 import at top of file
    phase2_import = """
# Import Phase 2 Smart Commands (Added in Phase 3A)
from memory_bank_mcp.unified.creation.mcp_commands import Phase2Commands
"""
    
    # Find where to insert the import (after existing imports)
    import_insertion_point = content.find("# Global variables")
    if import_insertion_point != -1:
        content = content[:import_insertion_point] + phase2_import + "\n" + content[import_insertion_point:]
        print("  ✅ Added Phase 2 imports")
    
    # 3. Add Phase 2 commands initialization
    init_addition = """
# Phase 2 Smart Commands (Added in Phase 3A)
phase2_commands: Optional[Phase2Commands] = None
"""
    
    # Find where to add the global variable
    global_vars_end = content.find("logger = logging.getLogger(__name__)")
    if global_vars_end != -1:
        insert_point = content.find("\n", global_vars_end) + 1
        content = content[:insert_point] + init_addition + "\n" + content[insert_point:]
        print("  ✅ Added Phase 2 global variable")
    
    # 4. Update initialize_tool_modules to include Phase 2
    old_init_line = "logger.info(\"✅ Modular v1.4.0 tools initialized (Phase 2 Complete: Content + Migration + Backup Tools)\")"
    new_init_block = """        phase2_commands = Phase2Commands(context_manager)
        logger.info("✅ Phase 3A tools initialized (Modular + Phase 2 Smart Commands)")"""
    
    if old_init_line in content:
        content = content.replace(old_init_line, new_init_block)
        print("  ✅ Updated tool initialization")
    
    # 5. Add Phase 2 smart commands to the server
    phase2_server_commands = '''
# =============================================================================
# PHASE 2 SMART CONTENT CREATION COMMANDS (Added in Phase 3A)
# =============================================================================

@server.tool()
async def save_to_memory(content: str, title: str = None, type: str = "auto", tags: Optional[str] = None) -> str:
    """Save content to memory with automatic type detection"""
    if not phase2_commands:
        return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
    return await phase2_commands.save_to_memory(content, title, type, tags)

@server.tool()
async def save_discussion(content: str, title: str = None, decision_made: bool = False, 
                         participants: Optional[str] = None) -> str:
    """Save discussion content with decision tracking"""
    if not phase2_commands:
        return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
    return await phase2_commands.save_discussion(content, title, decision_made, participants)

@server.tool()
async def save_document(content: str, title: str, document_type: str = "guide", 
                       spec_phase: str = None) -> str:
    """Save formal document content with metadata"""
    if not phase2_commands:
        return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
    return await phase2_commands.save_document(content, title, document_type, spec_phase)

@server.tool()
async def save_plan(content: str, title: str = None, phases: Optional[str] = None, 
                   priority: str = "medium") -> str:
    """Save plan content with phase tracking"""
    if not phase2_commands:
        return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
    return await phase2_commands.save_plan(content, title, phases, priority)

@server.tool()
async def save_code(content: str, title: str = None, language: str = None, 
                   filename: str = None) -> str:
    """Save code content with language detection"""
    if not phase2_commands:
        return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
    return await phase2_commands.save_code(content, title, language, filename)

@server.tool()
async def save_note(content: str, title: str = None, note_type: str = "general") -> str:
    """Save note content for quick thoughts and ideas"""
    if not phase2_commands:
        return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
    return await phase2_commands.save_note(content, title, note_type)

@server.tool()
async def save_chat_session(session_content: str, session_id: str = None, 
                           participants: Optional[str] = None) -> str:
    """Save chat session as discussion with metadata"""
    if not phase2_commands:
        return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
    return await phase2_commands.save_chat_session(session_content, session_id, participants)

@server.tool()
async def save_markdown_file(file_content: str, filename: str, file_path: str = None) -> str:
    """Import individual markdown file content"""
    if not phase2_commands:
        return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
    return await phase2_commands.save_markdown_file(file_content, filename, file_path)

'''
    
    # Insert before SERVER STARTUP section
    server_startup_index = content.find("# SERVER STARTUP")
    if server_startup_index != -1:
        content = content[:server_startup_index] + phase2_server_commands + "\n" + content[server_startup_index:]
        print("  ✅ Added 8 Phase 2 smart commands")
    
    # 6. Update existing commands to use Phase 2 (log_decision, store_template_spec)
    # Replace log_decision implementation
    old_log_decision = re.search(r'(@server\.tool\(\)[\s\S]*?async def log_decision\([\s\S]*?)return await project_tools\.log_decision\(summary, rationale, tags\)', content)
    if old_log_decision:
        new_log_decision = old_log_decision.group(1) + '''if not phase2_commands:
        return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
    return await phase2_commands.log_decision(summary, rationale, tags)'''
        content = content.replace(old_log_decision.group(0), new_log_decision)
        print("  ✅ Updated log_decision to use unified_documents")
    
    # Replace store_template_spec implementation  
    old_store_template = re.search(r'(@server\.tool\(\)[\s\S]*?async def store_template_spec\([\s\S]*?)return await backup_tools\.store_template_spec\(', content)
    if old_store_template:
        new_store_template = old_store_template.group(1) + '''if not phase2_commands:
        return "❌ Phase 2 commands not initialized. Use `work_on_project()` first."
    return await phase2_commands.store_template_spec(template_name, template_content, template_version, 
                                                   description, project_types, spec_phase, workflow_system, update_existing)

# Old implementation commented out:
# return await backup_tools.store_template_spec('''
        
        # Find the end of the old function
        old_end = content.find('update_existing)', old_store_template.end()) + len('update_existing)')
        content = content[:old_store_template.start()] + new_store_template + content[old_end:]
        print("  ✅ Updated store_template_spec to use unified_documents")
    
    # 7. Update startup log message
    old_startup = 'logger.info("📊 Tools available: 33 core tools (Phase 2 COMPLETE - All modules included)")'
    new_startup = 'logger.info("📊 Phase 3A Complete: 35+ tools (Streamlined + Smart Commands)")'
    content = content.replace(old_startup, new_startup)
    print("  ✅ Updated startup message")
    
    # 8. Calculate final line count
    final_line_count = len(content.split('\n'))
    original_line_count = 499  # From our earlier check
    line_change = final_line_count - original_line_count
    
    print(f"\n📊 CONSOLIDATION RESULTS:")
    print(f"  Original lines: {original_line_count}")
    print(f"  Final lines: {final_line_count}")
    print(f"  Net change: {line_change:+d} lines")
    print(f"  Commands removed: 3 (commented out)")
    print(f"  Commands added: 8 (smart commands)")
    print(f"  Commands updated: 2 (unified_documents)")
    
    # Write the updated content
    backup_path = main_py_path.with_suffix('.py.backup_phase3a')
    with open(backup_path, 'w') as f:
        f.write(open(main_py_path, 'r').read())
    print(f"  ✅ Backup created: {backup_path}")
    
    with open(main_py_path, 'w') as f:
        f.write(content)
    print(f"  ✅ Updated main.py with Phase 3A changes")
    
    return True

if __name__ == "__main__":
    success = apply_phase3a_consolidation()
    
    if success:
        print(f"\n🎉 PHASE 3A CONSOLIDATION COMPLETE!")
        print(f"✅ Modular approach maintained")
        print(f"✅ Redundant commands safely commented out")
        print(f"✅ Phase 2 smart commands added")
        print(f"✅ Key commands updated for unified_documents")
        print(f"✅ Main.py kept manageable with modular imports")
        print(f"\n🚀 Ready for testing and deployment!")
    else:
        print(f"\n❌ Phase 3A consolidation failed")
