#!/usr/bin/env python3
"""
Content Migration Module
========================

Main content migrator that orchestrates table migration using modular components.
"""

import sqlite3
import logging
from typing import Dict, List, Any

from .content_migrator_modules import TableAnalyzer, QueryBuilder, LegacyCleaner, FTSRebuilder

logger = logging.getLogger(__name__)

class ContentMigrator:
    """Main content migrator using modular architecture"""
    
    def __init__(self, database_path: str):
        self.database_path = database_path
        
        # Initialize modular components
        self.table_analyzer = TableAnalyzer(database_path)
        self.query_builder = QueryBuilder()
        self.legacy_cleaner = LegacyCleaner(database_path)
        self.fts_rebuilder = FTSRebuilder(database_path)
    
    def migrate_all_content_tables(self, project_uuid: str = "legacy-project") -> Dict[str, Any]:
        """
        Migrate all discovered content tables to documents table
        
        Args:
            project_uuid: Project UUID to use for migrated content
            
        Returns:
            Dict with migration results
        """
        try:
            # Discover content tables using analyzer
            content_tables = self.table_analyzer.discover_content_tables()
            
            if not content_tables:
                return {
                    'success': True,
                    'tables_processed': 0,
                    'records_migrated': 0,
                    'message': 'No content tables found to migrate'
                }
            
            print(f"🔄 Migrating {len(content_tables)} content tables to documents...")
            
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            migration_results = {}
            total_migrated = 0
            
            for table_name, doc_type in content_tables.items():
                print(f"\\n📄 Processing {table_name} → documents (type='{doc_type}')")
                
                try:
                    # Analyze table structure
                    structure = self.table_analyzer.analyze_table_structure(table_name)
                    print(f"   📋 Columns: {', '.join(structure['columns'])}")
                    
                    # Build migration query using query builder
                    migration_query = self.query_builder.build_migration_query(
                        table_name, doc_type, structure, project_uuid
                    )
                    
                    # Execute migration
                    cursor.execute(migration_query)
                    migrated_count = cursor.rowcount
                    migration_results[table_name] = migrated_count
                    total_migrated += migrated_count
                    
                    print(f"   ✅ Migrated {migrated_count} records from {table_name}")
                    
                except Exception as e:
                    print(f"   ❌ Failed to migrate {table_name}: {e}")
                    migration_results[table_name] = 0
                    logger.error(f"Migration failed for {table_name}: {e}")
            
            conn.commit()
            conn.close()
            
            print(f"\\n✅ Content migration complete: {total_migrated} total records")
            
            return {
                'success': True,
                'tables_processed': len(content_tables),
                'records_migrated': total_migrated,
                'migration_results': migration_results,
                'message': f'Successfully migrated {total_migrated} records from {len(content_tables)} tables'
            }
            
        except Exception as e:
            logger.error(f"Content migration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tables_processed': 0,
                'records_migrated': 0
            }
    
    def cleanup_legacy_tables(self, tables_to_remove: List[str]) -> Dict[str, Any]:
        """Remove legacy tables after successful migration"""
        return self.legacy_cleaner.cleanup_legacy_tables(tables_to_remove)
    
    def rebuild_fts_indexes(self) -> Dict[str, Any]:
        """Rebuild FTS5 indexes after migration"""
        return self.fts_rebuilder.rebuild_fts_indexes()
