#!/usr/bin/env python3
"""
FTS Rebuilder Module
====================

Manages FTS5 index rebuilding after migration.
"""

import sqlite3
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class FTSRebuilder:
    """Handles FTS5 index rebuilding"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
    
    def rebuild_fts_indexes(self) -> Dict[str, Any]:
        """
        Rebuild FTS5 indexes after migration
        
        Returns:
            Dict with rebuild results
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            print("🔍 Rebuilding FTS5 indexes...")
            
            fts_tables = ['documents_fts', 'markdown_search']
            rebuilt_count = 0
            
            for fts_table in fts_tables:
                try:
                    # Check if FTS table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (fts_table,))
                    if cursor.fetchone():
                        cursor.execute(f"INSERT INTO {fts_table}({fts_table}) VALUES('rebuild')")
                        rebuilt_count += 1
                        print(f"   ✅ Rebuilt {fts_table} index")
                except Exception as e:
                    print(f"   ⚠️ Failed to rebuild {fts_table}: {e}")
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'indexes_rebuilt': rebuilt_count,
                'message': f'Successfully rebuilt {rebuilt_count} FTS indexes'
            }
            
        except Exception as e:
            logger.error(f"FTS rebuild failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'indexes_rebuilt': 0
            }
