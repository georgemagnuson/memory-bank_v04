#!/usr/bin/env python3
"""
Legacy Cleaner Module
======================

Handles cleanup of legacy tables after successful migration.
"""

import sqlite3
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class LegacyCleaner:
    """Handles cleanup of legacy tables"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
    
    def cleanup_legacy_tables(self, tables_to_remove: List[str]) -> Dict[str, Any]:
        """
        Remove legacy tables after successful migration
        
        Args:
            tables_to_remove: List of table names to remove
            
        Returns:
            Dict with cleanup results
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Get existing tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            # Filter to tables that actually exist
            tables_to_drop = [table for table in tables_to_remove if table in existing_tables]
            
            print(f"🧹 Cleaning up {len(tables_to_drop)} legacy tables...")
            
            dropped_count = 0
            failed_drops = []
            
            for table in tables_to_drop:
                try:
                    cursor.execute(f"DROP TABLE IF EXISTS {table}")
                    dropped_count += 1
                    print(f"   🗑️ Dropped: {table}")
                except Exception as e:
                    failed_drops.append(f"{table}: {e}")
                    print(f"   ⚠️ Failed to drop {table}: {e}")
            
            conn.commit()
            conn.close()
            
            print(f"   ✅ Cleaned up {dropped_count} legacy tables")
            
            return {
                'success': True,
                'tables_dropped': dropped_count,
                'failed_drops': failed_drops,
                'message': f'Successfully removed {dropped_count} legacy tables'
            }
            
        except Exception as e:
            logger.error(f"Legacy table cleanup failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tables_dropped': 0
            }
