#!/usr/bin/env python3
"""
show_help_simple.py
Generated: 2025-07-28.1530
Purpose: Simple CLI script to display Memory Bank help without unicode issues
"""

def show_memory_bank_help():
    """Display Memory Bank help information"""
    
    help_text = """
MEMORY BANK v04 ENHANCED - MODULAR ARCHITECTURE

QUICK START:
• work_on_project('/path/to/project') - Initialize Memory Bank for project
• get_memory_bank_status() - Check current status and statistics  
• memory_bank_help() - This comprehensive help system

SMART CONTENT CREATION (Phase 2 - NEW!):
• save_to_memory(content, title, type) - Save content with auto-detection
• save_discussion(content, title, decision_made) - Save discussions/meetings
• save_document(content, title, doc_type, phase) - Save formal documents
• save_plan(content, title, phases, priority) - Save plans/roadmaps
• save_code(content, title, language, filename) - Save code snippets
• save_note(content, title, note_type) - Save quick notes/ideas
• save_chat_session(content, session_id, participants) - Save chat logs
• save_markdown_file(content, filename, path) - Import markdown files

UNIFIED SEARCH & CONTENT (Phase 1):
• search_all_content(query, limit, content_types) - Universal content search
• sync_fts_tables() - Synchronize full-text search indexes

PROJECT MANAGEMENT:
• log_decision(summary, rationale, tags) - Track architectural decisions
• query_decisions(search_term, limit) - Search decision history
• generate_enhanced_session_starter(goal, type) - Context-aware session prep

DATABASE & MAINTENANCE:
• memory_bank_describe_schema() - Show database schema
• memory_bank_sql_query(query, max_length) - Execute SQL queries
• verify_and_repair_schema() - Database integrity management
• get_memory_bank_system_info() - Detailed system information

BACKUP & TEMPLATES:
• backup_context_db(type, force, verify) - Create database backups
• list_backups(type, metadata, verify) - List available backups
• store_template_spec(name, content, version) - Store templates
• discover_templates(query, type, phase) - Find templates

RECOMMENDED WORKFLOW:
1. work_on_project('/path/to/project') - Initialize
2. search_all_content('topic') - Explore existing content
3. save_discussion('content', 'title') - Add new content easily
4. query_decisions('topic') - Track decisions
5. backup_context_db() - Regular backups

KEY FEATURES:
• Auto-Detection: Smart content type detection reduces user decisions
• Unified Backend: Single unified_documents table for all content
• Rich Responses: Detailed, helpful responses with tips and formatting
• Modular Design: 5 focused command modules for easy maintenance

Total Commands Available: 38 (organized in modular architecture)
"""
    
    print("=" * 60)
    print("MEMORY BANK MCP SERVER - HELP")
    print("=" * 60)
    print(help_text)
    print("=" * 60)
    print("\nHOW TO USE:")
    print("1. Configure Memory Bank in your MCP client (Claude Desktop)")
    print("2. Or run the server: python server/memory_bank_mcp/main.py")
    print("3. Call commands through your MCP client")
    print("\nFor development/testing:")
    print("  cd server/memory_bank_mcp && python main.py")

if __name__ == "__main__":
    show_memory_bank_help()
