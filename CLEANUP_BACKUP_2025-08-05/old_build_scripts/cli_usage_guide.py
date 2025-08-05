#!/usr/bin/env python3
"""
cli_usage_guide.py
Generated: 2025-07-28.1530
Purpose: Complete CLI usage guide for Memory Bank MCP

This script provides all the ways to access Memory Bank help and commands from CLI.
"""

def show_cli_usage_guide():
    """Show comprehensive CLI usage guide"""
    
    print("""
==================================================================
MEMORY BANK MCP - CLI USAGE GUIDE
==================================================================

📋 WAYS TO ACCESS HELP:

1. SIMPLE HELP DISPLAY (RECOMMENDED):
   cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04
   python show_help_simple.py

2. FULL HELP (WITH UNICODE):
   cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04
   python show_help.py

3. DIRECT COMMAND HELP:
   cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp
   python -c "
   import asyncio
   from main import memory_bank_help
   asyncio.run(print(memory_bank_help()))"

==================================================================
🚀 RUNNING THE MCP SERVER:

1. START MCP SERVER:
   cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp
   python main.py

2. TEST SERVER STARTUP:
   cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp
   python -c "
   import logging
   logging.basicConfig(level=logging.INFO)
   from main import logger
   logger.info('Testing Memory Bank MCP startup...')
   print('✅ Server modules load correctly')"

==================================================================
🔧 DEVELOPMENT & TESTING:

1. VALIDATE SYNTAX:
   cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp
   python -c "import ast; ast.parse(open('main.py').read()); print('✅ Syntax OK')"

2. TEST IMPORTS:
   cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp
   python -c "
   from mcp_database_commands import DatabaseCommands
   from unified.creation.mcp_commands import Phase2Commands
   print('✅ All imports working')"

3. COUNT COMMANDS:
   cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp
   python -c "
   import re
   content = open('main.py').read()
   commands = re.findall(r'@server\.tool\(\).*?async def (\w+)\(', content, re.DOTALL)
   print(f'📊 Found {len(commands)} MCP commands')"

==================================================================
💾 DATABASE TESTING:

1. CHECK DATABASE:
   cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04
   sqlite3 memory-bank/context.db "SELECT COUNT(*) as total_records FROM unified_documents;"

2. TEST UNIFIED SEARCH:
   cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp
   python -c "
   import sys
   sys.path.append('.')
   from unified.search import UnifiedSearch
   from unified.types import SearchConfig
   # Test search functionality (requires database)
   print('✅ Search modules load correctly')"

==================================================================
📦 CONFIGURATION FOR MCP CLIENTS:

1. CLAUDE DESKTOP CONFIGURATION:
   Add to your Claude Desktop config:
   {
     \"mcpServers\": {
       \"memory-bank\": {
         \"command\": \"python\",
         \"args\": [\"/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp/main.py\"],
         \"env\": {}
       }
     }
   }

2. COMMAND LINE MCP CLIENT (if available):
   mcp connect memory-bank
   memory_bank_help()

==================================================================
🎯 QUICK COMMAND REFERENCE:

ESSENTIAL COMMANDS:
• work_on_project('/path/to/project')  - Initialize
• get_memory_bank_status()             - Check status
• memory_bank_help()                   - Show help

SMART COMMANDS (Phase 2):
• save_to_memory(content, title)       - Smart saving
• save_discussion(content, title)      - Save discussions  
• save_document(content, title)        - Save documents
• search_all_content(query)            - Universal search

DATABASE COMMANDS:
• memory_bank_sql_query(query)         - SQL interface
• backup_context_db()                  - Create backup

==================================================================
🚨 TROUBLESHOOTING:

1. IMPORT ERRORS:
   - Ensure you're in the correct directory
   - Check Python path includes server/memory_bank_mcp
   - Verify all modular command files exist

2. SYNTAX ERRORS:
   - Run: python -m py_compile main.py
   - Check for unicode characters in strings
   - Verify proper indentation

3. DATABASE ERRORS:
   - Check memory-bank/context.db exists
   - Verify unified_documents table exists
   - Run verify_and_repair_schema() command

==================================================================
📊 CURRENT STATUS:
• Total MCP Commands: 38
• Modular Files: 5
• Architecture: Phase 3A Complete
• Backend: Unified Documents Table
• Frontend: Smart Commands + Direct Access

==================================================================
""")

if __name__ == "__main__":
    show_cli_usage_guide()
