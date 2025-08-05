#!/usr/bin/env python3
"""
content_tools_modules/fts_manager.py
Generated: 2025-07-30.1439
Purpose: Full-text search index synchronization for v2.0 documents table

Key v2.0 Changes:
- Uses documents_fts instead of unified_documents_fts
- Supports multiple FTS tables (documents_fts, markdown_search, etc.)
- Project-aware synchronization
"""

import logging
import sqlite3
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class FTSManager:
    """Full-text search index management for v2.0 documents architecture"""
    
    def __init__(self, context_manager):
        """Initialize FTS manager with context manager dependency
        
        Args:
            context_manager: Active ContextManager instance with database connection
        """
        self.context_manager = context_manager
        self.logger = logger
        
        # v2.0 FTS tables mapping
        self.fts_tables = {
            'documents_fts': 'documents',
            'markdown_search': 'markdown_files',
            'discussions_fts': 'discussions',
            'artifacts_fts': 'artifacts',
            'code_iterations_fts': 'code_iterations',
            'plans_fts': 'plans'
        }
    
    async def sync_fts_tables(self) -> str:
        """Synchronize all FTS5 virtual tables - Updated for v2.0 documents architecture
        
        Rebuilds FTS indexes to ensure search indexes are current.
        
        Returns:
            Status report of synchronization operation
        """
        try:
            if not self.context_manager or not self.context_manager.database_path:
                return "❌ **FTS SYNC FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            conn = sqlite3.connect(self.context_manager.database_path)
            cursor = conn.cursor()
            
            sync_results = {}
            total_synced = 0
            
            # Sync each FTS table that exists
            for fts_table, main_table in self.fts_tables.items():
                try:
                    # Check if FTS table exists
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (fts_table,)
                    )
                    if not cursor.fetchone():
                        sync_results[fts_table] = "❌ Table not found"
                        continue
                    
                    # Get record counts before sync
                    cursor.execute(f"SELECT COUNT(*) FROM {main_table}")
                    main_count = cursor.fetchone()[0]
                    
                    cursor.execute(f"SELECT COUNT(*) FROM {fts_table}")
                    fts_count_before = cursor.fetchone()[0]
                    
                    # Perform sync by rebuilding FTS index
                    cursor.execute(f"INSERT INTO {fts_table}({fts_table}) VALUES('rebuild')")
                    
                    # Get record counts after sync  
                    cursor.execute(f"SELECT COUNT(*) FROM {fts_table}")
                    fts_count_after = cursor.fetchone()[0]
                    
                    # Record sync result
                    status = "✅ Synced" if main_count == fts_count_after else "⚠️ Count mismatch"
                    sync_results[fts_table] = {
                        'main_table': main_table,
                        'main_count': main_count,
                        'fts_before': fts_count_before,
                        'fts_after': fts_count_after,
                        'status': status
                    }
                    total_synced += 1
                    
                except sqlite3.Error as e:
                    sync_results[fts_table] = f"❌ Error: {str(e)}"
                    self.logger.warning(f"FTS sync failed for {fts_table}: {e}")
            
            conn.close()
            
            # Format results
            output_lines = [
                "✅ **FTS SYNC COMPLETE**",
                "",
                f"**Tables Synchronized:** {total_synced}/{len(self.fts_tables)}",
                ""
            ]
            
            for fts_table, result in sync_results.items():
                if isinstance(result, dict):
                    output_lines.extend([
                        f"**{fts_table}:**",
                        f"- Main table: {result['main_table']} ({result['main_count']:,} records)",
                        f"- FTS before: {result['fts_before']:,} records",
                        f"- FTS after: {result['fts_after']:,} records",
                        f"- Status: {result['status']}",
                        ""
                    ])
                else:
                    output_lines.extend([
                        f"**{fts_table}:** {result}",
                        ""
                    ])
            
            output_lines.extend([
                "**Next Steps:**",
                "- Test search functionality with `search_all_content()`",
                "- Use `extract_large_document()` for content analysis",
                "- Import more content with `import_markdown_files()`"
            ])
            
            return "\n".join(output_lines)
            
        except Exception as e:
            self.logger.error(f"FTS sync failed: {e}")
            return f"❌ **FTS SYNC FAILED**\n\nError: {str(e)}"
    
    async def get_fts_status(self) -> str:
        """Get detailed status of all FTS tables
        
        Returns:
            Status report of FTS table health
        """
        try:
            if not self.context_manager or not self.context_manager.database_path:
                return "❌ **FTS STATUS FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            conn = sqlite3.connect(self.context_manager.database_path)
            cursor = conn.cursor()
            
            fts_status = {}
            
            # Check each FTS table
            for fts_table, main_table in self.fts_tables.items():
                try:
                    # Check if tables exist
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (fts_table,)
                    )
                    fts_exists = bool(cursor.fetchone())
                    
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (main_table,)
                    )
                    main_exists = bool(cursor.fetchone())
                    
                    if not fts_exists:
                        fts_status[fts_table] = "❌ FTS table missing"
                        continue
                    
                    if not main_exists:
                        fts_status[fts_table] = "❌ Main table missing"
                        continue
                    
                    # Get record counts
                    cursor.execute(f"SELECT COUNT(*) FROM {main_table}")
                    main_count = cursor.fetchone()[0]
                    
                    cursor.execute(f"SELECT COUNT(*) FROM {fts_table}")
                    fts_count = cursor.fetchone()[0]
                    
                    # Determine status
                    if main_count == fts_count:
                        status = "✅ Synchronized"
                    elif fts_count == 0:
                        status = "⚠️ Empty FTS table"
                    else:
                        status = f"⚠️ Count mismatch ({main_count} vs {fts_count})"
                    
                    fts_status[fts_table] = {
                        'main_table': main_table,
                        'main_count': main_count,
                        'fts_count': fts_count,
                        'status': status
                    }
                    
                except sqlite3.Error as e:
                    fts_status[fts_table] = f"❌ Error: {str(e)}"
            
            conn.close()
            
            # Format status report
            output_lines = [
                "📊 **FTS STATUS REPORT**",
                ""
            ]
            
            for fts_table, status in fts_status.items():
                if isinstance(status, dict):
                    output_lines.extend([
                        f"**{fts_table}:**",
                        f"- Main: {status['main_table']} ({status['main_count']:,} records)",
                        f"- FTS: {status['fts_count']:,} records",
                        f"- {status['status']}",
                        ""
                    ])
                else:
                    output_lines.extend([
                        f"**{fts_table}:** {status}",
                        ""
                    ])
            
            return "\n".join(output_lines)
            
        except Exception as e:
            self.logger.error(f"FTS status check failed: {e}")
            return f"❌ **FTS STATUS FAILED**\n\nError: {str(e)}"
    
    def get_supported_fts_tables(self) -> Dict[str, str]:
        """Get mapping of supported FTS tables to their main tables"""
        return self.fts_tables.copy()
