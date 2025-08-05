#!/usr/bin/env python3
"""
mcp_command_analysis.py
Generated: 2025-07-28.1500
Purpose: Analyze existing MCP commands for consolidation opportunities

This script analyzes all MCP commands to identify redundancy and 
superseded functionality after Phase 1 & 2 implementation.
"""

def analyze_mcp_commands():
    """Analyze current MCP commands and identify consolidation opportunities"""
    
    print("🔍 Memory Bank MCP Command Analysis")
    print("=" * 40)
    
    # Current MCP commands from main.py
    current_commands = [
        # Core Status & Management (Keep - Essential)
        ("get_memory_bank_status", "✅ KEEP", "Essential status information"),
        ("work_on_project", "✅ KEEP", "Core project initialization"),
        ("memory_bank_help", "✅ KEEP", "Essential help system"),
        
        # Database Schema & Info (Keep - Useful for debugging)
        ("get_memory_bank_system_info", "✅ KEEP", "System debugging information"),
        ("memory_bank_describe_schema", "✅ KEEP", "Database schema inspection"),
        ("memory_bank_table_info", "⚠️ CONSIDER REMOVAL", "Low-level debugging, rarely used"),
        ("memory_bank_list_tables", "⚠️ CONSIDER REMOVAL", "Low-level debugging, rarely used"),
        ("verify_and_repair_schema", "✅ KEEP", "Database maintenance"),
        
        # SQL & Query Tools (Keep - Developer tools)
        ("memory_bank_sql_query", "✅ KEEP", "Developer SQL interface"),
        ("sql_truncation_help", "⚠️ CONSIDER REMOVAL", "Documentation command, rarely used"),
        
        # Legacy Content Extraction (SUPERSEDED by unified architecture)
        ("extract_large_document", "❌ REMOVE", "SUPERSEDED by unified search + extraction"),
        
        # Project Management (Keep - Core functionality)
        ("log_decision", "🔄 UPDATED", "Updated to use unified_documents (Phase 2)"),
        ("query_decisions", "✅ KEEP", "Essential decision tracking"),
        ("generate_enhanced_session_starter", "✅ KEEP", "Useful workflow tool"),
        ("prepare_context_switch", "✅ KEEP", "Essential for project switching"),
        ("check_context_switch_safety", "✅ KEEP", "Safety check"),
        ("force_context_flush", "✅ KEEP", "Emergency tool"),
        
        # Unified Content System (Keep - Core Phase 1 & 2 functionality)
        ("search_all_content", "✅ KEEP", "Core unified search (Phase 1)"),
        ("sync_fts_tables", "✅ KEEP", "FTS maintenance"),
        
        # Markdown Import System (Consolidate - Too many similar commands)
        ("import_markdown_files", "🔄 CONSOLIDATE", "Basic markdown import"),
        ("discover_and_import_all_markdown", "❌ REMOVE", "REDUNDANT with import_markdown_files"),
        ("import_project_documentation", "❌ REMOVE", "REDUNDANT with import_markdown_files"),
        ("generate_markdown_import_report", "⚠️ CONSIDER REMOVAL", "Reporting only, low value"),
        
        # Migration Tools (Consolidate - Too specialized)
        ("analyze_migration_candidates", "⚠️ CONSIDER REMOVAL", "One-time migration tool"),
        ("migrate_project_md_files", "⚠️ CONSIDER REMOVAL", "One-time migration tool"),
        ("migrate_specific_project", "⚠️ CONSIDER REMOVAL", "One-time migration tool"),
        
        # Backup & Templates (Keep - Essential)
        ("backup_context_db", "✅ KEEP", "Essential backup functionality"),
        ("list_backups", "✅ KEEP", "Backup management"),
        ("store_template_spec", "🔄 UPDATED", "Updated to use unified_documents (Phase 2)"),
        ("discover_templates", "✅ KEEP", "Template discovery"),
    ]
    
    # Phase 2 Smart Commands (Not yet in MCP - Should be added)
    phase2_smart_commands = [
        ("save_to_memory", "➕ ADD", "User-friendly content saving with auto-detection"),
        ("save_discussion", "➕ ADD", "Save discussions with decision tracking"),
        ("save_document", "➕ ADD", "Save formal documents with metadata"),
        ("save_plan", "➕ ADD", "Save plans with phase tracking"),
        ("save_code", "➕ ADD", "Save code with language detection"),
        ("save_note", "➕ ADD", "Save quick notes"),
        ("save_chat_session", "➕ ADD", "Save chat logs as discussions"),
        ("save_markdown_file", "➕ ADD", "Import individual markdown files"),
    ]
    
    print("\n📊 COMMAND ANALYSIS RESULTS:")
    print("=" * 35)
    
    keep_count = 0
    remove_count = 0
    update_count = 0
    consolidate_count = 0
    consider_count = 0
    add_count = 0
    
    print("\n✅ COMMANDS TO KEEP:")
    for cmd, action, reason in current_commands:
        if action == "✅ KEEP":
            print(f"  • {cmd}: {reason}")
            keep_count += 1
    
    print("\n🔄 COMMANDS TO UPDATE:")
    for cmd, action, reason in current_commands:
        if action == "🔄 UPDATED" or action == "🔄 CONSOLIDATE":
            print(f"  • {cmd}: {reason}")
            if action == "🔄 UPDATED":
                update_count += 1
            else:
                consolidate_count += 1
    
    print("\n❌ COMMANDS TO REMOVE:")
    for cmd, action, reason in current_commands:
        if action == "❌ REMOVE":
            print(f"  • {cmd}: {reason}")
            remove_count += 1
    
    print("\n⚠️ COMMANDS TO CONSIDER REMOVING:")
    for cmd, action, reason in current_commands:
        if action == "⚠️ CONSIDER REMOVAL":
            print(f"  • {cmd}: {reason}")
            consider_count += 1
    
    print("\n➕ PHASE 2 COMMANDS TO ADD:")
    for cmd, action, reason in phase2_smart_commands:
        print(f"  • {cmd}: {reason}")
        add_count += 1
    
    print(f"\n📈 SUMMARY:")
    print(f"  Current Commands: {len(current_commands)}")
    print(f"  Keep: {keep_count}")
    print(f"  Update: {update_count}")
    print(f"  Consolidate: {consolidate_count}")
    print(f"  Remove: {remove_count}")
    print(f"  Consider Removal: {consider_count}")
    print(f"  Add from Phase 2: {add_count}")
    
    net_change = add_count - remove_count - consider_count
    final_count = len(current_commands) + add_count - remove_count - consider_count
    print(f"  Estimated Final Count: {final_count} commands")
    print(f"  Net Change: {net_change:+d} commands")
    
    return {
        'remove': [cmd for cmd, action, _ in current_commands if action == "❌ REMOVE"],
        'consider_remove': [cmd for cmd, action, _ in current_commands if action == "⚠️ CONSIDER REMOVAL"],
        'update': [cmd for cmd, action, _ in current_commands if action == "🔄 UPDATED"],
        'consolidate': [cmd for cmd, action, _ in current_commands if action == "🔄 CONSOLIDATE"],
        'add': [cmd for cmd, _, _ in phase2_smart_commands],
        'keep': [cmd for cmd, action, _ in current_commands if action == "✅ KEEP"]
    }

def generate_consolidation_recommendations():
    """Generate specific consolidation recommendations"""
    
    print("\n\n🎯 CONSOLIDATION RECOMMENDATIONS:")
    print("=" * 38)
    
    recommendations = [
        {
            'category': 'IMMEDIATE REMOVALS',
            'items': [
                'extract_large_document → Use search_all_content + extraction functionality',
                'discover_and_import_all_markdown → Redundant with import_markdown_files',
                'import_project_documentation → Redundant with import_markdown_files'
            ]
        },
        {
            'category': 'CONSOLIDATE MARKDOWN IMPORTS',
            'items': [
                'Keep: import_markdown_files (enhanced with discovery features)',
                'Remove: discover_and_import_all_markdown, import_project_documentation',
                'Consider: generate_markdown_import_report (low value)'
            ]
        },
        {
            'category': 'MIGRATION TOOLS CLEANUP',
            'items': [
                'Consider removing: analyze_migration_candidates, migrate_project_md_files, migrate_specific_project',
                'Reason: One-time migration tools, not needed for ongoing operation',
                'Alternative: Keep as separate utility scripts outside MCP'
            ]
        },
        {
            'category': 'ADD PHASE 2 SMART COMMANDS',
            'items': [
                'Add 8 user-friendly smart commands from Phase 2',
                'These provide intuitive content creation interface',
                'Much more user-friendly than SQL or low-level commands'
            ]
        },
        {
            'category': 'DEBUGGING TOOLS REVIEW',
            'items': [
                'Consider removing: memory_bank_table_info, memory_bank_list_tables',
                'Reason: Low-level debugging, rarely used by end users',
                'Keep: memory_bank_describe_schema (more useful for schema overview)'
            ]
        }
    ]
    
    for rec in recommendations:
        print(f"\n📋 {rec['category']}:")
        for item in rec['items']:
            print(f"  • {item}")
    
    print(f"\n💡 FINAL RECOMMENDATION:")
    print(f"  • Remove 5-8 redundant/low-value commands")
    print(f"  • Add 8 user-friendly Phase 2 smart commands")
    print(f"  • Result: Cleaner, more focused command set")
    print(f"  • Focus on unified architecture and user experience")

if __name__ == "__main__":
    analysis = analyze_mcp_commands()
    generate_consolidation_recommendations()
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"  1. Remove clearly redundant commands")
    print(f"  2. Add Phase 2 smart commands to MCP interface")
    print(f"  3. Update documentation")
    print(f"  4. Test consolidated command set")
