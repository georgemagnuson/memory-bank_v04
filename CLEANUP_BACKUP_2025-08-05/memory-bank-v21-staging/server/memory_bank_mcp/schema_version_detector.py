#!/usr/bin/env python3
"""
schema_version_detector.py
Generated: 2025-07-30.1337
Purpose: Detect Memory Bank database schema versions and provide comparison utilities
Supports v1.4.0 (unified_documents) and v2.0 (documents) detection
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone

logger = logging.getLogger("memory_bank_mcp.schema_detector")


class SchemaVersionDetector:
    """Utility for detecting and comparing Memory Bank database schema versions"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        
    def detect_schema_version(self) -> Dict[str, any]:
        """
        Detect the schema version of a Memory Bank database
        
        Returns:
            Dictionary with version info, schema details, and migration recommendations
        """
        if not self.db_path.exists():
            return {
                'status': 'error',
                'error': f'Database not found: {self.db_path}',
                'version': 'unknown'
            }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get PRAGMA user_version
                cursor.execute("PRAGMA user_version")
                user_version = cursor.fetchone()[0]
                
                # Get table list
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                
                # Analyze schema structure
                analysis = self._analyze_schema_structure(cursor, tables, user_version)
                
                return {
                    'status': 'success',
                    'database_path': str(self.db_path),
                    'detected_at': datetime.now(timezone.utc).isoformat(),
                    **analysis
                }
                
        except Exception as e:
            logger.error(f"Schema detection failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'version': 'unknown'
            }
    
    def _analyze_schema_structure(self, cursor, tables: List[str], user_version: int) -> Dict[str, any]:
        """Analyze database structure to determine version"""
        
        has_unified_documents = 'unified_documents' in tables
        has_documents = 'documents' in tables
        has_legacy_tables = any(table in tables for table in ['discussions', 'artifacts', 'plans'])
        
        # Check unified_documents structure if it exists
        unified_docs_schema = None
        if has_unified_documents:
            cursor.execute("PRAGMA table_info(unified_documents)")
            unified_docs_schema = {row[1]: row[2] for row in cursor.fetchall()}
        
        # Check documents structure if it exists
        documents_schema = None
        if has_documents:
            cursor.execute("PRAGMA table_info(documents)")
            documents_schema = {row[1]: row[2] for row in cursor.fetchall()}
        
        # Version detection logic
        if user_version == 4 and has_documents and 'uuid' in (documents_schema or {}):
            return self._analyze_v2_0_schema(cursor, tables, documents_schema)
        elif user_version <= 3 and has_unified_documents and 'original_uuid' in (unified_docs_schema or {}):
            return self._analyze_v1_4_0_schema(cursor, tables, unified_docs_schema)
        elif has_legacy_tables and not has_unified_documents and not has_documents:
            return self._analyze_legacy_schema(cursor, tables, user_version)
        else:
            return self._analyze_unknown_schema(cursor, tables, user_version)
    
    def _analyze_v2_0_schema(self, cursor, tables: List[str], documents_schema: Dict[str, str]) -> Dict[str, any]:
        """Analyze v2.0 (documents table) schema"""
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM documents")
        document_count = cursor.fetchone()[0]
        
        # Check for project_uuid support
        has_cross_project_support = 'project_uuid' in documents_schema
        
        # Check FTS5 support
        has_documents_fts = 'documents_fts' in tables
        
        return {
            'version': 'v2.0',
            'schema_version': 4,
            'architecture': 'documents_table',
            'primary_table': 'documents',
            'document_count': document_count,
            'cross_project_support': has_cross_project_support,
            'fts_enabled': has_documents_fts,
            'migration_needed': False,
            'schema_fields': list(documents_schema.keys()),
            'recommendations': [
                'Schema is up-to-date for v2.0',
                'Cross-project references supported' if has_cross_project_support else 'Consider adding project_uuid for cross-project support',
                'Full-text search available' if has_documents_fts else 'Consider enabling FTS5 for better search'
            ]
        }
    
    def _analyze_v1_4_0_schema(self, cursor, tables: List[str], unified_docs_schema: Dict[str, str]) -> Dict[str, any]:
        """Analyze v1.4.0 (unified_documents table) schema"""
        
        # Count records
        cursor.execute("SELECT COUNT(*) FROM unified_documents")
        document_count = cursor.fetchone()[0]
        
        # Check legacy table usage
        legacy_counts = {}
        for table in ['discussions', 'artifacts', 'plans', 'code_iterations']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                legacy_counts[table] = cursor.fetchone()[0]
        
        # Check FTS5 support
        has_unified_fts = 'unified_documents_fts' in tables
        
        return {
            'version': 'v1.4.0',
            'schema_version': 3,
            'architecture': 'unified_documents',
            'primary_table': 'unified_documents',
            'document_count': document_count,
            'legacy_table_counts': legacy_counts,
            'cross_project_support': False,
            'fts_enabled': has_unified_fts,
            'migration_needed': True,
            'schema_fields': list(unified_docs_schema.keys()),
            'recommendations': [
                'Database can be migrated to v2.0 for enhanced features',
                'Migration will preserve all data with improved cross-project support',
                'Backup recommended before migration',
                f'Ready to migrate {document_count} documents to v2.0 architecture'
            ]
        }
    
    def _analyze_legacy_schema(self, cursor, tables: List[str], user_version: int) -> Dict[str, any]:
        """Analyze pre-v1.4.0 legacy schema"""
        
        legacy_counts = {}
        for table in ['discussions', 'artifacts', 'plans', 'code_iterations']:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                legacy_counts[table] = cursor.fetchone()[0]
        
        total_records = sum(legacy_counts.values())
        
        return {
            'version': f'pre-v1.4.0 (legacy)',
            'schema_version': user_version,
            'architecture': 'separate_tables',
            'primary_table': 'multiple',
            'total_records': total_records,
            'table_counts': legacy_counts,
            'cross_project_support': False,
            'fts_enabled': False,
            'migration_needed': True,
            'recommendations': [
                'Legacy schema detected - significant migration needed',
                'Recommend migrating to v1.4.0 first, then to v2.0',
                'Data consolidation required for unified document architecture',
                f'Total {total_records} records across {len(legacy_counts)} tables'
            ]
        }
    
    def _analyze_unknown_schema(self, cursor, tables: List[str], user_version: int) -> Dict[str, any]:
        """Analyze unknown or mixed schema"""
        
        return {
            'version': 'unknown',
            'schema_version': user_version,
            'architecture': 'mixed_or_unknown',
            'tables_found': tables,
            'migration_needed': 'uncertain',
            'recommendations': [
                'Schema does not match known Memory Bank versions',
                'Manual analysis required',
                'Consider creating fresh database with v2.0 schema',
                'Contact support if this is an official Memory Bank database'
            ]
        }
    
    def compare_with_template(self, template_version: str = "v2.0") -> Dict[str, any]:
        """
        Compare current database schema with a template version
        
        Args:
            template_version: "v1.4.0" or "v2.0"
            
        Returns:
            Comparison report with differences and recommendations
        """
        current_analysis = self.detect_schema_version()
        
        if current_analysis['status'] != 'success':
            return current_analysis
        
        template_path = Path(__file__).parent / f"schema_{template_version.replace('.', '_')}_template.sql"
        
        comparison = {
            'current_version': current_analysis.get('version', 'unknown'),
            'template_version': template_version,
            'template_path': str(template_path),
            'template_exists': template_path.exists(),
            'comparison_date': datetime.now(timezone.utc).isoformat()
        }
        
        if template_path.exists():
            comparison['schema_compatible'] = current_analysis.get('version') == template_version
            comparison['migration_recommendation'] = self._get_migration_path(
                current_analysis.get('version'), template_version
            )
        else:
            comparison['error'] = f'Template not found: {template_path}'
        
        return {**current_analysis, 'template_comparison': comparison}
    
    def _get_migration_path(self, current_version: str, target_version: str) -> str:
        """Get migration path recommendation"""
        
        if current_version == target_version:
            return "No migration needed - versions match"
        elif current_version == "v1.4.0" and target_version == "v2.0":
            return "Direct migration available - use migrate_v1_4_to_v2_0.py"
        elif "pre-v1.4.0" in current_version and target_version == "v2.0":
            return "Two-step migration: legacy → v1.4.0 → v2.0"
        elif current_version == "v2.0" and target_version == "v1.4.0":
            return "Downgrade not recommended - data loss may occur"
        else:
            return "Migration path unknown - manual analysis required"
    
    def print_analysis_report(self, analysis: Dict[str, any]) -> None:
        """Print formatted analysis report"""
        
        print(f"\n🔍 **MEMORY BANK SCHEMA ANALYSIS**")
        print(f"════════════════════════════════════")
        
        if analysis['status'] != 'success':
            print(f"❌ **Error:** {analysis.get('error', 'Unknown error')}")
            return
        
        print(f"📁 **Database:** {analysis['database_path']}")
        print(f"📊 **Version:** {analysis['version']}")
        print(f"🏗️  **Architecture:** {analysis['architecture']}")
        print(f"📚 **Schema Version:** {analysis['schema_version']}")
        
        if 'document_count' in analysis:
            print(f"📄 **Documents:** {analysis['document_count']}")
        
        if 'cross_project_support' in analysis:
            support_icon = "✅" if analysis['cross_project_support'] else "❌"
            print(f"🔗 **Cross-Project Support:** {support_icon}")
        
        if 'fts_enabled' in analysis:
            fts_icon = "✅" if analysis['fts_enabled'] else "❌"
            print(f"🔍 **Full-Text Search:** {fts_icon}")
        
        if 'migration_needed' in analysis:
            migration_icon = "⚠️" if analysis['migration_needed'] else "✅"
            status = "Required" if analysis['migration_needed'] else "Not needed"
            print(f"🔄 **Migration:** {migration_icon} {status}")
        
        if 'recommendations' in analysis:
            print(f"\n💡 **RECOMMENDATIONS:**")
            for i, rec in enumerate(analysis['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print(f"\n" + "═" * 35)


def main():
    """CLI interface for schema detection"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python schema_version_detector.py <database_path>")
        sys.exit(1)
    
    db_path = Path(sys.argv[1])
    detector = SchemaVersionDetector(db_path)
    
    # Run analysis
    analysis = detector.detect_schema_version()
    detector.print_analysis_report(analysis)
    
    # Compare with v2.0 template
    if analysis['status'] == 'success':
        print(f"\n🔧 **TEMPLATE COMPARISON (v2.0):**")
        comparison = detector.compare_with_template("v2.0")
        template_comp = comparison.get('template_comparison', {})
        
        if template_comp.get('schema_compatible'):
            print(f"✅ Schema matches v2.0 template")
        else:
            print(f"⚠️  Schema differs from v2.0 template")
            print(f"📋 Migration: {template_comp.get('migration_recommendation', 'Unknown')}")


if __name__ == "__main__":
    main()
