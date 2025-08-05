#!/usr/bin/env python3
"""
Table Analyzer Module
=====================

Analyzes table structures and discovers content tables for migration.
"""

import sqlite3
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class TableAnalyzer:
    """Analyzes database tables for migration planning"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        
        # Content table mappings (table_name → document_type)
        self.content_mapping = {
            'unified_documents': 'document',
            'discussions': 'discussion',
            'artifacts': 'artifact', 
            'plans': 'plan',
            'code_iterations': 'code',
            'chat_sessions': 'chat_session',
            'decisions': 'decision',
            'notes': 'note',
            'ideas': 'note',
            'requirements': 'requirement',
            'specifications': 'specification',
            'tasks': 'task',
            'issues': 'issue',
            'meetings': 'meeting',
            'research': 'research',
            'analysis': 'analysis'
        }
    
    def discover_content_tables(self) -> Dict[str, str]:
        """
        Discover content tables that exist and have data
        
        Returns:
            Dict mapping table_name → document_type
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        content_tables = {}
        
        for table_name, doc_type in self.content_mapping.items():
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if not cursor.fetchone():
                continue
            
            # Check if table has content
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                if count > 0:
                    content_tables[table_name] = doc_type
                    print(f"   📄 Found: {table_name} ({count} records) → {doc_type}")
            except Exception as e:
                print(f"   ⚠️ Could not check {table_name}: {e}")
        
        conn.close()
        return content_tables
    
    def analyze_table_structure(self, table_name: str) -> Dict[str, Any]:
        """
        Analyze table structure to understand column mapping
        
        Args:
            table_name: Name of table to analyze
            
        Returns:
            Dict with table structure information
        """
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            sample_row = cursor.fetchone()
            
            return {
                'columns': list(columns.keys()),
                'column_types': columns,
                'has_sample': sample_row is not None,
                'sample_data': dict(zip(columns.keys(), sample_row)) if sample_row else {}
            }
        finally:
            conn.close()
    
    def get_table_record_count(self, table_name: str) -> int:
        """Get record count for a specific table"""
        conn = sqlite3.connect(self.database_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            conn.close()
