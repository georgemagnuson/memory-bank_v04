#!/usr/bin/env python3
"""
Migration Manager Module
========================

Main orchestrator for Memory Bank v2.1 migrations using modular architecture.
Provides high-level interface for all migration operations.
"""

import logging
from typing import Dict, Any

from .version_detector import VersionDetector, DatabaseInfo
from .schema_creator import SchemaCreator
from .migration_manager_modules import MigrationOrchestrator, WorkOnProjectHandler

logger = logging.getLogger(__name__)

class MigrationManager:
    """Main migration manager with modular architecture"""
    
    def __init__(self):
        self.version_detector = VersionDetector()
        self.schema_creator = SchemaCreator()
        self.migration_orchestrator = MigrationOrchestrator()
        self.work_on_project_handler = WorkOnProjectHandler()
    
    def analyze_database(self, database_path: str) -> str:
        """
        Analyze database and provide migration recommendations
        
        Args:
            database_path: Path to SQLite database
            
        Returns:
            Formatted analysis report
        """
        db_info = self.version_detector.analyze_database(database_path)
        return self.version_detector.format_analysis_report(db_info)
    
    def migrate_to_v21(self, database_path: str, dry_run: bool = False, 
                      project_uuid: str = "legacy-project") -> Dict[str, Any]:
        """
        Complete migration to v2.1 with ALL table consolidation
        
        Args:
            database_path: Path to database to migrate
            dry_run: If True, analyze but don't make changes
            project_uuid: Project UUID for migrated content
            
        Returns:
            Migration result dictionary
        """
        try:
            # Analyze current state
            db_info = self.version_detector.analyze_database(database_path)
            
            if db_info.version == -1:
                return {
                    'success': False,
                    'error': 'Database analysis failed',
                    'database_path': database_path
                }
            
            if db_info.version >= 2.1:
                return {
                    'success': True,
                    'action': 'no_migration_needed',
                    'message': f'Database is already v{db_info.version}',
                    'database_path': database_path
                }
            
            total_records = sum(db_info.content_tables.values())
            
            print(f"🚀 Memory Bank v2.1 Migration")
            print(f"📁 Database: {database_path.split('/')[-1]}")
            print(f"📊 Current: v{db_info.version}, {db_info.table_count} tables, {total_records} records")
            print(f"🎯 Target: v2.1, ~{db_info.estimated_final_tables} tables")
            print(f"🧪 Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
            print()
            
            if dry_run:
                return self._perform_dry_run_analysis(db_info)
            
            # Confirm migration
            if not self.migration_orchestrator.confirm_migration(db_info):
                return {
                    'success': False,
                    'action': 'cancelled_by_user',
                    'message': 'Migration cancelled by user',
                    'database_path': database_path
                }
            
            # Perform migration using orchestrator
            return self.migration_orchestrator.perform_full_migration(database_path, db_info, project_uuid)
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'database_path': database_path,
                'action': 'migration_failed'
            }
    
    def create_v21_database(self, database_path: str, project_name: str, 
                           project_path: str) -> Dict[str, Any]:
        """Create new v2.1 database from scratch"""
        return self.schema_creator.create_v21_database(database_path, project_name, project_path)
    
    def validate_v21_database(self, database_path: str) -> Dict[str, Any]:
        """Validate that database has proper v2.1 schema"""
        return self.schema_creator.validate_v21_schema(database_path)
    
    def work_on_project(self, project_path: str) -> Dict[str, Any]:
        """Enhanced work_on_project with automatic v2.1 migration"""
        return self.work_on_project_handler.work_on_project(project_path)
    
    def _perform_dry_run_analysis(self, db_info: DatabaseInfo) -> Dict[str, Any]:
        """Perform dry run analysis"""
        content_summary = []
        total_records = sum(db_info.content_tables.values())
        
        for table_name, count in db_info.content_tables.items():
            doc_type = self.version_detector.CONTENT_TABLE_MAPPING.get(table_name, 'unknown')
            content_summary.append(f"   📄 {table_name}: {count} records → documents (type='{doc_type}')")
        
        print("🧪 DRY RUN - Migration Plan:")
        print("\n".join(content_summary))
        print(f"\n📊 Summary:")
        print(f"   📄 Total records to migrate: {total_records}")
        print(f"   🗑️ Legacy tables to remove: {len(db_info.legacy_tables)}")
        print(f"   📋 Final table count: ~{db_info.estimated_final_tables}")
        
        return {
            'success': True,
            'action': 'dry_run_complete',
            'database_path': db_info.database_path,
            'current_version': db_info.version,
            'target_version': 2.1,
            'records_to_migrate': total_records,
            'tables_to_remove': len(db_info.legacy_tables),
            'estimated_final_tables': db_info.estimated_final_tables,
            'content_tables': db_info.content_tables,
            'message': f'Dry run complete: {total_records} records would be migrated from {len(db_info.content_tables)} tables'
        }
