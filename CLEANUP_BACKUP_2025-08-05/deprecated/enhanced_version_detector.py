#!/usr/bin/env python3
"""
Enhanced database version detector with table count-based detection
Filename: enhanced_version_detector.py
Generated: 2025-08-04.0150
Purpose: Enhanced version detection that considers table count for proper v2.1 identification

VERSION LOGIC:
- v1.x: 40+ tables (legacy: artifacts, discussions, plans, code_iterations, etc.)
- v2.0: 45+ tables (added unified_documents + FTS, but legacy tables still present)
- v2.1: ~18 tables (clean: only documents, projects, semantic_equivalents, FTS5 tables)
"""

import sqlite3
import logging
from typing import Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class EnhancedSchemaInfo:
    """Enhanced schema information with table count analysis"""
    version: float  # Allow decimal versions like 2.1
    table_count: int
    has_documents_table: bool
    has_unified_documents_table: bool
    has_legacy_tables: bool
    needs_migration: bool
    migration_type: str  # 'none', 'v1_to_v2', 'v2_to_v2.1'
    record_counts: Dict[str, int]
    database_path: str

class EnhancedVersionDetector:
    """Enhanced version detection with table count analysis"""
    
    # Define table count thresholds
    V1_TABLE_THRESHOLD = 35  # v1.x has 40+ tables
    V2_LEGACY_THRESHOLD = 35  # v2.0 with legacy tables has 45+ tables  
    V2_1_MAX_TABLES = 25  # v2.1 clean has ~18 tables
    
    # Expected v2.1 core tables
    V2_1_CORE_TABLES = {
        'projects', 'documents', 'markdown_files', 'chat_sessions', 
        'cross_references', 'project_context', 'semantic_equivalents'
    }
    
    # Expected v2.1 FTS tables
    V2_1_FTS_TABLES = {
        'documents_fts', 'documents_fts_data', 'documents_fts_idx', 
        'documents_fts_docsize', 'documents_fts_config',
        'markdown_search', 'markdown_search_data', 'markdown_search_idx',
        'markdown_search_docsize', 'markdown_search_config'
    }
    
    # Legacy tables that should be removed in v2.1
    LEGACY_TABLES = {
        'artifacts', 'artifacts_fts', 'artifacts_fts_config', 'artifacts_fts_data', 'artifacts_fts_docsize', 'artifacts_fts_idx',
        'discussions', 'discussions_fts', 'discussions_fts_config', 'discussions_fts_data', 'discussions_fts_docsize', 'discussions_fts_idx',
        'plans', 'plans_fts', 'plans_fts_config', 'plans_fts_data', 'plans_fts_docsize', 'plans_fts_idx',
        'code_iterations', 'code_iterations_fts', 'code_iterations_fts_config', 'code_iterations_fts_data', 'code_iterations_fts_docsize', 'code_iterations_fts_idx',
        'unified_documents', 'unified_documents_fts', 'unified_documents_fts_config', 'unified_documents_fts_data', 'unified_documents_fts_docsize', 'unified_documents_fts_idx'
    }

    @classmethod
    def detect_version_enhanced(cls, database_path: str) -> EnhancedSchemaInfo:
        """
        Enhanced version detection using table count and schema analysis
        
        Args:
            database_path: Path to the SQLite database
            
        Returns:
            EnhancedSchemaInfo with detailed version analysis
        """
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            all_tables = {row[0] for row in cursor.fetchall()}
            table_count = len(all_tables)
            
            # Check for key tables
            has_documents = 'documents' in all_tables
            has_unified_documents = 'unified_documents' in all_tables
            has_legacy_tables = bool(cls.LEGACY_TABLES & all_tables)
            legacy_table_count = len(cls.LEGACY_TABLES & all_tables)
            
            # Get record counts for key tables
            record_counts = {}
            
            for table in ['documents', 'unified_documents', 'artifacts', 'discussions', 'plans']:
                if table in all_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        record_counts[table] = cursor.fetchone()[0]
                    except:
                        record_counts[table] = 0
            
            conn.close()
            
            # Version detection logic with table count
            version, needs_migration, migration_type = cls._determine_version_and_migration(
                table_count, has_documents, has_unified_documents, has_legacy_tables, legacy_table_count
            )
            
            return EnhancedSchemaInfo(
                version=version,
                table_count=table_count,
                has_documents_table=has_documents,
                has_unified_documents_table=has_unified_documents,
                has_legacy_tables=has_legacy_tables,
                needs_migration=needs_migration,
                migration_type=migration_type,
                record_counts=record_counts,
                database_path=database_path
            )
            
        except Exception as e:
            logger.error(f"Enhanced version detection failed: {e}")
            return EnhancedSchemaInfo(
                version=-1, table_count=0, has_documents_table=False,
                has_unified_documents_table=False, has_legacy_tables=False,
                needs_migration=False, migration_type='error',
                record_counts={}, database_path=database_path
            )
    
    @classmethod
    def _determine_version_and_migration(cls, table_count: int, has_documents: bool, 
                                       has_unified_documents: bool, has_legacy_tables: bool,
                                       legacy_table_count: int) -> Tuple[float, bool, str]:
        """
        Determine version and migration requirements based on table analysis
        
        Returns:
            Tuple of (version, needs_migration, migration_type)
        """
        
        # v2.1 Clean (target state)
        if (has_documents and not has_legacy_tables and 
            table_count <= cls.V2_1_MAX_TABLES):
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
        
        # Edge case: has documents but still has some legacy tables (partial migration)
        elif (has_documents and has_legacy_tables and 
              legacy_table_count < 10):  # Just a few legacy tables remaining
            return 2.05, True, 'cleanup_legacy'
        
        # Empty/new database
        elif table_count == 0:
            return 0.0, False, 'create_new'
        
        # Unknown state
        else:
            return -1, True, 'manual_review'

def analyze_database_version(database_path: str) -> str:
    """
    Analyze database version and provide migration recommendations
    
    Args:
        database_path: Path to the SQLite database
        
    Returns:
        Formatted analysis report with migration recommendations
    """
    schema_info = EnhancedVersionDetector.detect_version_enhanced(database_path)
    
    # Format analysis report
    report = f"""🔍 **Enhanced Database Version Analysis**

📁 **Database:** {schema_info.database_path.split('/')[-1]}
📊 **Table Count:** {schema_info.table_count}
🏷️ **Detected Version:** v{schema_info.version}

**📋 Schema Analysis:**
• Documents table: {'✅ Present' if schema_info.has_documents_table else '❌ Missing'}
• Unified documents: {'⚠️ Present (legacy)' if schema_info.has_unified_documents_table else '✅ Absent'}
• Legacy tables: {'⚠️ {legacy_count} present'.format(legacy_count=len(EnhancedVersionDetector.LEGACY_TABLES & set())) if schema_info.has_legacy_tables else '✅ Clean'}

**📈 Content Analysis:**"""
    
    total_records = sum(schema_info.record_counts.values())
    for table, count in schema_info.record_counts.items():
        if count > 0:
            report += f"\n• {table}: {count:,} records"
    
    report += f"\n• **Total Content:** {total_records:,} records"
    
    # Migration recommendations
    if schema_info.needs_migration:
        report += f"""

🔄 **Migration Required: {schema_info.migration_type}**

**Migration Path:**"""
        
        if schema_info.migration_type == 'v1_to_v2.1':
            report += """
• **Source:** v1.x legacy tables (artifacts, discussions, plans, etc.)
• **Target:** v2.1 clean schema (documents table only)
• **Process:** Consolidate all content → documents table, remove legacy tables
• **Command:** `migrate_to_v2(confirm=True)`"""
        
        elif schema_info.migration_type == 'v2_to_v2.1':
            report += """
• **Source:** v2.0 with legacy tables still present
• **Target:** v2.1 clean schema (documents table only)  
• **Process:** Remove deprecated legacy tables, keep consolidated documents
• **Command:** `cleanup_legacy_tables(confirm=True)`"""
        
        elif schema_info.migration_type == 'cleanup_legacy':
            report += """
• **Source:** Mostly migrated v2.0 with some legacy remnants
• **Target:** v2.1 clean schema
• **Process:** Remove remaining legacy tables
• **Command:** `cleanup_legacy_tables(confirm=True)`"""
        
        else:
            report += f"""
• **Type:** {schema_info.migration_type}
• **Action:** Manual review recommended"""
    
    else:
        report += """

✅ **No Migration Required**
Database is current v2.1 with clean schema."""
    
    return report

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
        print(analyze_database_version(db_path))
    else:
        print("Usage: python enhanced_version_detector.py /path/to/context.db")
