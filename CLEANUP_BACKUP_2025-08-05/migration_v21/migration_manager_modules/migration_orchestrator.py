#!/usr/bin/env python3
"""
Migration Orchestrator Module
==============================

Orchestrates the complete migration process from start to finish.
"""

import sqlite3
import logging
from typing import Dict, Any

from ..version_detector import DatabaseInfo
from ..content_migrator import ContentMigrator
from .backup_manager import BackupManager

logger = logging.getLogger(__name__)

class MigrationOrchestrator:
    """Orchestrates complete migration process"""
    
    def __init__(self):
        self.backup_manager = BackupManager()
    
    def perform_full_migration(self, database_path: str, db_info: DatabaseInfo, 
                              project_uuid: str) -> Dict[str, Any]:
        """
        Perform complete migration to v2.1
        
        Args:
            database_path: Path to database
            db_info: Database information from version detector
            project_uuid: Project UUID for migrated content
            
        Returns:
            Migration result dictionary
        """
        # Step 1: Create backup
        backup_path = self.backup_manager.create_backup(database_path, "v21_migration")
        if not backup_path:
            return {
                'success': False,
                'error': 'Failed to create backup',
                'database_path': database_path,
                'action': 'backup_failed'
            }
        
        try:
            # Step 2: Migrate content tables
            print("\n🔄 Step 1: Migrating content tables...")
            content_migrator = ContentMigrator(database_path)
            content_result = content_migrator.migrate_all_content_tables(project_uuid)
            
            if not content_result['success']:
                raise Exception(f"Content migration failed: {content_result.get('error', 'Unknown error')}")
            
            # Step 3: Clean up legacy tables
            print("\n🧹 Step 2: Cleaning up legacy tables...")
            cleanup_result = content_migrator.cleanup_legacy_tables(db_info.legacy_tables)
            
            # Step 4: Rebuild FTS indexes
            print("\n🔍 Step 3: Rebuilding FTS indexes...")
            fts_result = content_migrator.rebuild_fts_indexes()
            
            # Step 5: Update schema version
            print("\n🏷️ Step 4: Updating schema version...")
            self._update_schema_version(database_path, 2.1)
            
            # Step 6: Get final statistics
            from ..version_detector import VersionDetector
            final_db_info = VersionDetector.analyze_database(database_path)
            
            print(f"\n🎉 Migration Complete!")
            print(f"   📄 Records migrated: {content_result['records_migrated']}")
            print(f"   🗑️ Legacy tables removed: {cleanup_result.get('tables_dropped', 0)}")
            print(f"   📊 Final table count: {final_db_info.table_count}")
            print(f"   🏷️ Final version: v{final_db_info.version}")
            print(f"   💾 Backup available: {backup_path}")
            
            return {
                'success': True,
                'action': 'migration_complete',
                'database_path': database_path,
                'backup_path': backup_path,
                'version_from': db_info.version,
                'version_to': final_db_info.version,
                'tables_before': db_info.table_count,
                'tables_after': final_db_info.table_count,
                'records_migrated': content_result['records_migrated'],
                'tables_removed': cleanup_result.get('tables_dropped', 0),
                'indexes_rebuilt': fts_result.get('indexes_rebuilt', 0),
                'message': f'Successfully migrated to v{final_db_info.version}!'
            }
            
        except Exception as e:
            # Attempt to restore backup
            logger.error(f"Migration failed: {e}")
            print(f"\n❌ Migration failed: {e}")
            
            if backup_path:
                print(f"🔄 Attempting to restore backup...")
                if self.backup_manager.restore_backup(database_path, backup_path):
                    print(f"✅ Database restored from backup")
                else:
                    print(f"❌ Failed to restore backup")
            
            return {
                'success': False,
                'error': str(e),
                'database_path': database_path,
                'backup_path': backup_path,
                'action': 'migration_failed_with_backup'
            }
    
    def _update_schema_version(self, database_path: str, version: float):
        """Update database schema version"""
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        try:
            version_code = int(version * 10)  # 2.1 → 21
            cursor.execute(f'PRAGMA user_version = {version_code}')
            conn.commit()
            print(f"   ✅ Updated schema version to v{version}")
        except Exception as e:
            logger.error(f"Failed to update schema version: {e}")
            print(f"   ⚠️ Failed to update schema version: {e}")
        finally:
            conn.close()
    
    def confirm_migration(self, db_info: DatabaseInfo) -> bool:
        """Get user confirmation for migration"""
        total_records = sum(db_info.content_tables.values())
        
        print(f"⚠️ MIGRATION SUMMARY:")
        print(f"   📄 {len(db_info.content_tables)} content tables → documents table")
        print(f"   📊 {total_records} total records to migrate")
        print(f"   🗑️ {len(db_info.legacy_tables)} legacy tables to remove")
        print(f"   📋 Tables: {db_info.table_count} → ~{db_info.estimated_final_tables}")
        
        confirm = input("\nProceed with v2.1 migration? (yes/no): ").lower().strip()
        return confirm == 'yes'
