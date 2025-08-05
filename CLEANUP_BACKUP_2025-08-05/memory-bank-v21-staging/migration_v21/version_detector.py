#!/usr/bin/env python3
"""
Version Detection Module
========================

Enhanced version detection using table count and schema analysis.
Determines exact version and migration requirements.

Version Logic:
- v1.x: 40+ tables (legacy: artifacts, discussions, plans, etc.)
- v2.0: 45+ tables (added unified_documents + FTS, legacy tables still present)  
- v2.1: ~18 tables (clean: only documents, projects, semantic_equivalents, FTS5)
"""

import sqlite3
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class DatabaseInfo:
    """Complete database information for migration planning"""
    version: float
    table_count: int
    has_documents_table: bool
    has_unified_documents_table: bool  
    has_legacy_tables: bool
    needs_migration: bool
    migration_type: str
    content_tables: Dict[str, int]  # table_name → record_count
    legacy_tables: List[str]
    estimated_final_tables: int
    database_path: str

class VersionDetector:
    """Enhanced version detection with table count analysis"""
    
    # Version thresholds
    V1_TABLE_THRESHOLD = 35
    V2_LEGACY_THRESHOLD = 35  
    V21_MAX_TABLES = 25
    
    # Expected v2.1 core tables
    V21_CORE_TABLES = {
        'projects', 'documents', 'markdown_files', 'cross_references', 
        'project_context', 'semantic_equivalents'
    }
    
    # Expected v2.1 FTS tables
    V21_FTS_TABLES = {
        'documents_fts', 'documents_fts_data', 'documents_fts_idx', 
        'documents_fts_docsize', 'documents_fts_config',
        'markdown_search', 'markdown_search_data', 'markdown_search_idx',
        'markdown_search_docsize', 'markdown_search_config'
    }
    
    # Content tables that should migrate to documents
    CONTENT_TABLE_MAPPING = {
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
    
    # All possible legacy tables (including FTS)
    LEGACY_TABLES = {
        'artifacts', 'artifacts_fts', 'artifacts_fts_config', 'artifacts_fts_data', 'artifacts_fts_docsize', 'artifacts_fts_idx',
        'discussions', 'discussions_fts', 'discussions_fts_config', 'discussions_fts_data', 'discussions_fts_docsize', 'discussions_fts_idx',
        'plans', 'plans_fts', 'plans_fts_config', 'plans_fts_data', 'plans_fts_docsize', 'plans_fts_idx',
        'code_iterations', 'code_iterations_fts', 'code_iterations_fts_config', 'code_iterations_fts_data', 'code_iterations_fts_docsize', 'code_iterations_fts_idx',
        'unified_documents', 'unified_documents_fts', 'unified_documents_fts_config', 'unified_documents_fts_data', 'unified_documents_fts_docsize', 'unified_documents_fts_idx',
        'chat_sessions', 'decisions', 'notes', 'ideas', 'requirements', 'specifications', 'tasks', 'issues', 'meetings', 'research', 'analysis'
    }

    @classmethod
    def analyze_database(cls, database_path: str) -> DatabaseInfo:
        """
        Complete database analysis for migration planning
        
        Args:
            database_path: Path to SQLite database
            
        Returns:
            DatabaseInfo with complete analysis
        """
        try:
            if not Path(database_path).exists():
                raise FileNotFoundError(f"Database not found: {database_path}")
            
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            all_tables = {row[0] for row in cursor.fetchall()}
            table_count = len(all_tables)
            
            # Analyze table types
            has_documents = 'documents' in all_tables
            has_unified_documents = 'unified_documents' in all_tables
            legacy_tables_present = list(cls.LEGACY_TABLES & all_tables)
            has_legacy_tables = bool(legacy_tables_present)
            
            # Find content tables with data
            content_tables = {}
            for table_name, doc_type in cls.CONTENT_TABLE_MAPPING.items():
                if table_name in all_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        if count > 0:
                            content_tables[table_name] = count
                    except Exception:
                        pass
            
            conn.close()
            
            # Determine version and migration requirements
            version, needs_migration, migration_type = cls._determine_version_and_migration(
                table_count, has_documents, has_unified_documents, has_legacy_tables, len(legacy_tables_present)
            )
            
            # Estimate final table count after migration
            estimated_final = len(cls.V21_CORE_TABLES) + len(cls.V21_FTS_TABLES) + 2  # +2 for sqlite_sequence, etc.
            
            return DatabaseInfo(
                version=version,
                table_count=table_count,
                has_documents_table=has_documents,
                has_unified_documents_table=has_unified_documents,
                has_legacy_tables=has_legacy_tables,
                needs_migration=needs_migration,
                migration_type=migration_type,
                content_tables=content_tables,
                legacy_tables=legacy_tables_present,
                estimated_final_tables=estimated_final,
                database_path=database_path
            )
            
        except Exception as e:
            logger.error(f"Database analysis failed: {e}")
            return DatabaseInfo(
                version=-1, table_count=0, has_documents_table=False,
                has_unified_documents_table=False, has_legacy_tables=False,
                needs_migration=False, migration_type='error',
                content_tables={}, legacy_tables=[],
                estimated_final_tables=0, database_path=database_path
            )
    
    @classmethod
    def _determine_version_and_migration(cls, table_count: int, has_documents: bool,
                                       has_unified_documents: bool, has_legacy_tables: bool,
                                       legacy_table_count: int) -> Tuple[float, bool, str]:
        """Determine version and migration requirements"""
        
        # v2.1 Clean (target state)
        if (has_documents and not has_legacy_tables and 
            table_count <= cls.V21_MAX_TABLES):
            return 2.1, False, 'none'
        
        # v2.0 with legacy tables (needs migration to v2.1)  
        elif (has_documents and has_legacy_tables and 
              table_count > cls.V2_LEGACY_THRESHOLD):
            return 2.0, True, 'v2_to_v2.1'
        
        # v1.x legacy (needs migration to v2.1)
        elif (not has_documents and 
              (has_unified_documents or has_legacy_tables) and
              table_count > cls.V1_TABLE_THRESHOLD):
            return 1.0, True, 'v1_to_v2.1'
        
        # Edge case: partial migration
        elif (has_documents and has_legacy_tables and 
              legacy_table_count < 10):
            return 2.05, True, 'cleanup_legacy'
        
        # Empty/new database
        elif table_count == 0:
            return 0.0, False, 'create_new'
        
        # Unknown state
        else:
            return -1, True, 'manual_review'
    
    @classmethod
    def format_analysis_report(cls, db_info: DatabaseInfo) -> str:
        """Format detailed analysis report"""
        
        report = f"""🔍 **Database Version Analysis**

📁 **Database:** {Path(db_info.database_path).name}
📊 **Table Count:** {db_info.table_count}
🏷️ **Version:** v{db_info.version}

**📋 Schema Analysis:**
• Documents table: {'✅ Present' if db_info.has_documents_table else '❌ Missing'}
• Unified documents: {'⚠️ Present (legacy)' if db_info.has_unified_documents_table else '✅ Absent'}
• Legacy tables: {'⚠️ {count} present'.format(count=len(db_info.legacy_tables)) if db_info.has_legacy_tables else '✅ Clean'}

**📈 Content Analysis:**"""
        
        total_records = sum(db_info.content_tables.values())
        for table, count in db_info.content_tables.items():
            if count > 0:
                doc_type = cls.CONTENT_TABLE_MAPPING.get(table, 'unknown')
                report += f"\n• {table}: {count:,} records → documents (type='{doc_type}')"
        
        report += f"\n• **Total Content:** {total_records:,} records"
        
        # Migration recommendations
        if db_info.needs_migration:
            report += f"""

🔄 **Migration Required: {db_info.migration_type}**

**Migration Path:**"""
            
            if db_info.migration_type == 'v1_to_v2.1':
                report += """
• **Source:** v1.x legacy tables
• **Target:** v2.1 clean schema (documents table only)
• **Process:** Consolidate all content → documents, remove legacy tables"""
            
            elif db_info.migration_type == 'v2_to_v2.1':
                report += """
• **Source:** v2.0 with legacy tables present
• **Target:** v2.1 clean schema (documents table only)  
• **Process:** Consolidate remaining content → documents, cleanup legacy tables"""
            
            elif db_info.migration_type == 'cleanup_legacy':
                report += """
• **Source:** Mostly migrated with legacy remnants
• **Target:** v2.1 clean schema
• **Process:** Remove remaining legacy tables"""
            
            report += f"""

**📊 Expected Result:**
• Tables: {db_info.table_count} → ~{db_info.estimated_final_tables}
• Content: {total_records} records preserved in documents table
• Schema: Clean v2.1 architecture"""
        
        else:
            report += """

✅ **No Migration Required**
Database is current v2.1 with clean schema."""
        
        return report

# Backwards compatibility alias
EnhancedVersionDetector = VersionDetector
