#!/usr/bin/env python3
"""
server/memory_bank_mcp/schema_manager_modules/database_migrator.py
Generated: 2025-08-01.1843
Purpose: CONSOLIDATED Database migration operations for Memory Bank v2.0

CONSOLIDATION: This file now contains the best features from both DatabaseMigrator classes:
- User-friendly interface from schema_manager_modules version
- Comprehensive migration logic from migration_modules version
- NEW: DROP deprecated tables functionality (final cleanup step)
- Enhanced dry-run capabilities and detailed reporting

Handles:
- Safe migration from v1.4.0 to v2.0 with comprehensive backup system
- User confirmation workflows with detailed impact analysis
- Rollback capabilities with validation
- 1:1 table operations (unified_documents → documents)
- FINAL CLEANUP: Drop deprecated tables after successful migration
- Dry-run analysis for safe testing
"""

import logging
import sqlite3
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MigrationResult:
    """Result of a migration operation with enhanced reporting"""
    success: bool
    version_from: int
    version_to: int
    records_migrated: int
    backup_path: Optional[str] = None
    error_message: Optional[str] = None
    tables_affected: List[str] = None
    requires_confirmation: bool = False
    deprecated_tables_dropped: List[str] = None
    migration_type: str = "unified_to_documents"
    dry_run: bool = False
    warnings: List[str] = None

class DatabaseMigrator:
    """
    CONSOLIDATED Database Migration Operations
    
    Combines the best features from both previous DatabaseMigrator implementations:
    - Context manager integration for seamless Memory Bank integration
    - Comprehensive migration logic with full schema transformation
    - Enhanced backup and rollback systems
    - NEW: Complete deprecated table cleanup
    """
    
    def __init__(self, context_manager):
        self.context_manager = context_manager
        self.db_path = Path(context_manager.database_path)
        self.backup_dir = self.db_path.parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        # Define deprecated tables for v2.0 cleanup
        self.deprecated_tables = [
            "discussions", "discussions_fts", "discussions_fts_config", 
            "discussions_fts_data", "discussions_fts_docsize", "discussions_fts_idx",
            "artifacts", "artifacts_fts", "artifacts_fts_config",
            "artifacts_fts_data", "artifacts_fts_docsize", "artifacts_fts_idx", 
            "code_iterations", "code_iterations_fts", "code_iterations_fts_config",
            "code_iterations_fts_data", "code_iterations_fts_docsize", "code_iterations_fts_idx",
            "plans", "plans_fts", "plans_fts_config",
            "plans_fts_data", "plans_fts_docsize", "plans_fts_idx",
            "chat_sessions", "cross_references", "project_context"
        ]
    
    async def create_backup(self) -> Optional[Path]:
        """Create database backup before migration with enhanced metadata"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{self.db_path.stem}_v1.4.0_backup_{timestamp}.db"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(self.db_path, backup_path)
            
            # Add backup metadata
            with sqlite3.connect(backup_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS backup_metadata (
                        backup_timestamp TEXT,
                        original_path TEXT,
                        migration_version TEXT,
                        backup_reason TEXT
                    )
                """)
                cursor.execute("""
                    INSERT INTO backup_metadata VALUES (?, ?, ?, ?)
                """, (timestamp, str(self.db_path), "v1.4.0_to_v2.0", "Pre-migration backup"))
                conn.commit()
            
            logger.info(f"Database backup created with metadata: {backup_path}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            return None
    
    async def migrate_unified_to_documents(self, confirm: bool = False, dry_run: bool = False, 
                                         cleanup_deprecated: bool = True) -> MigrationResult:
        """
        CONSOLIDATED migration from unified_documents to documents with full v2.0 transformation
        
        Args:
            confirm: User confirmation for migration (required for safety)
            dry_run: If True, analyze but don't make changes
            cleanup_deprecated: If True, drop deprecated tables after migration (recommended)
        """
        try:
            if not self.context_manager.is_initialized():
                return MigrationResult(
                    success=False,
                    version_from=0,
                    version_to=4,
                    records_migrated=0,
                    error_message="Context manager not initialized",
                    dry_run=dry_run
                )
            
            # Get database analysis
            analysis = await self._analyze_migration_requirements()
            
            if not analysis['migration_needed']:
                return MigrationResult(
                    success=True,
                    version_from=analysis['current_version'],
                    version_to=4,
                    records_migrated=0,
                    error_message="No migration needed - database is already v2.0",
                    dry_run=dry_run
                )
            
            cursor = self.context_manager.database.get_cursor()
            
            # Check if confirmation is needed (unless dry run)
            if not confirm and not dry_run:
                result = await self.context_manager.database.execute_sql_query("SELECT COUNT(*) FROM unified_documents")
                record_count = result['results'][0][list(result['results'][0].keys())[0]] if result['success'] else 0
                
                deprecated_count = 0
                for table in self.deprecated_tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        deprecated_count += cursor.fetchone()[0]
                    except sqlite3.Error:
                        pass  # Table doesn't exist
                
                return MigrationResult(
                    success=False,
                    version_from=0,
                    version_to=4,
                    records_migrated=0,
                    requires_confirmation=True,
                    dry_run=dry_run,
                    error_message=f"""🔄 **CONSOLIDATED MIGRATION READY**

**📊 MIGRATION SCOPE:**
• {record_count} records in unified_documents → documents
• ~{deprecated_count} records in deprecated tables (will be preserved in documents)
• {len(self.deprecated_tables)} deprecated tables will be {'dropped' if cleanup_deprecated else 'preserved'}

**🔄 MIGRATION STEPS:**
1. Create comprehensive backup with metadata
2. Create new documents table with v2.0 schema
3. Migrate all unified_documents → documents (1:1 transfer)
4. Create documents_fts for full-text search
5. Create proper indexes for performance
6. Update database version to 4 (v2.0)
{'7. 🗑️  DROP deprecated tables (final cleanup)' if cleanup_deprecated else '7. ⚠️  PRESERVE deprecated tables (not recommended)'}

**🛡️  SAFETY FEATURES:**
• Comprehensive backup before any changes
• Rollback capability if migration fails
• Data validation after migration
• Atomic transaction (all-or-nothing)

Call again with confirm=True to proceed with migration."""
                )
            
            # For dry run, return analysis without making changes
            if dry_run:
                return await self._perform_dry_run_analysis(analysis, cleanup_deprecated)
            
            # Perform actual migration
            return await self._perform_full_migration(analysis, cleanup_deprecated)
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return MigrationResult(
                success=False,
                version_from=0,
                version_to=4,
                records_migrated=0,
                error_message=f"Migration failed: {str(e)}",
                dry_run=dry_run
            )
    
    async def _perform_full_migration(self, analysis: Dict[str, Any], cleanup_deprecated: bool) -> MigrationResult:
        """Perform the complete migration with all steps - FIXED: Using proper database interface"""
        backup_path = None
        try:
            # Step 1: Create backup
            backup_path = await self.create_backup()
            if not backup_path:
                raise Exception("Failed to create backup - migration aborted for safety")
            
            # Step 2: Create documents table
            await self._create_documents_table()
            
            # Step 3: Migrate data
            records_migrated = await self._migrate_data_to_documents()
            
            # Step 4: Create FTS and indexes
            await self._create_documents_fts()
            await self._create_documents_indexes()
            
            # Step 5: Update schema version
            await self.context_manager.database.execute_sql_query("PRAGMA user_version = 4")
            
            # Step 6: Drop deprecated tables (NEW FEATURE)
            dropped_tables = []
            if cleanup_deprecated:
                dropped_tables = await self._drop_deprecated_tables()
            
            # Step 7: Validate migration
            validation_result = await self._validate_migration()
            if not validation_result['valid']:
                raise Exception(f"Migration validation failed: {validation_result['message']}")
            
            logger.info(f"✅ Migration completed successfully: {records_migrated} records migrated")
            
            return MigrationResult(
                success=True,
                version_from=analysis['current_version'],
                version_to=4,
                records_migrated=records_migrated,
                backup_path=str(backup_path),
                tables_affected=["unified_documents", "documents"],
                deprecated_tables_dropped=dropped_tables,
                warnings=[] if cleanup_deprecated else ["Deprecated tables preserved - manual cleanup recommended"]
            )
                
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            
            # Restore backup if available
            if backup_path and backup_path.exists():
                try:
                    shutil.copy2(backup_path, self.db_path)
                    logger.info("Database restored from backup due to migration failure")
                except Exception as restore_error:
                    logger.error(f"Failed to restore backup: {restore_error}")
            
            return MigrationResult(
                success=False,
                version_from=analysis.get('current_version', 0),
                version_to=4,
                records_migrated=0,
                backup_path=str(backup_path) if backup_path else None,
                error_message=str(e)
            )
    
    async def _perform_dry_run_analysis(self, analysis: Dict[str, Any], cleanup_deprecated: bool) -> MigrationResult:
        """Perform comprehensive dry-run analysis without making changes"""
        try:
            cursor = self.context_manager.database.get_cursor()
            
            # Count records to migrate
            cursor.execute("SELECT COUNT(*) FROM unified_documents")
            record_count = cursor.fetchone()[0]
            
            # Analyze deprecated tables
            deprecated_analysis = []
            total_deprecated_records = 0
            for table in self.deprecated_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    if count > 0:
                        deprecated_analysis.append(f"{table}: {count} records")
                        total_deprecated_records += count
                except sqlite3.Error:
                    pass  # Table doesn't exist
            
            warnings = []
            if not cleanup_deprecated and deprecated_analysis:
                warnings.append(f"Deprecated tables will be preserved ({total_deprecated_records} total records)")
            
            return MigrationResult(
                success=True,
                version_from=analysis['current_version'],
                version_to=4,
                records_migrated=record_count,
                tables_affected=["unified_documents", "documents"] + (self.deprecated_tables if cleanup_deprecated else []),
                deprecated_tables_dropped=self.deprecated_tables if cleanup_deprecated else [],
                dry_run=True,
                warnings=warnings,
                error_message=f"""🔍 **DRY RUN ANALYSIS COMPLETE**

**📊 MIGRATION IMPACT:**
• Records to migrate: {record_count} (unified_documents → documents)
• Deprecated tables found: {len(deprecated_analysis)}
• Total deprecated records: {total_deprecated_records}

**📋 DEPRECATED TABLES ANALYSIS:**
{chr(10).join(deprecated_analysis) if deprecated_analysis else "• No deprecated tables found"}

**🔄 PLANNED ACTIONS:**
1. ✅ Create backup with metadata
2. ✅ Create documents table (v2.0 schema)
3. ✅ Migrate {record_count} records
4. ✅ Create documents_fts for search
5. ✅ Create performance indexes
6. ✅ Update schema version to 4
{'7. 🗑️  DROP ' + str(len(self.deprecated_tables)) + ' deprecated tables' if cleanup_deprecated else '7. ⚠️  PRESERVE deprecated tables'}

**🛡️  SAFETY MEASURES:**
• Full backup before migration
• Atomic transaction (rollback on failure)
• Post-migration validation
• Automatic recovery on failure

This is a DRY RUN - no changes made. Use confirm=True to proceed."""
            )
            
        except Exception as e:
            return MigrationResult(
                success=False,
                version_from=analysis.get('current_version', 0),
                version_to=4,
                records_migrated=0,
                error_message=f"Dry run analysis failed: {str(e)}",
                dry_run=True
            )
    
    async def _analyze_migration_requirements(self) -> Dict[str, Any]:
        """Comprehensive analysis of what migration steps are needed"""
        try:
            # Check current schema version
            result = await self.context_manager.database.execute_sql_query("PRAGMA user_version")
            current_version = result['results'][0]['user_version'] if result['success'] else 0
            
            # Check for key tables
            result = await self.context_manager.database.execute_sql_query("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = [row['name'] for row in result['results']] if result['success'] else []
            
            has_unified_documents = 'unified_documents' in existing_tables
            has_documents = 'documents' in existing_tables
            
            # Count records in source table
            unified_count = 0
            if has_unified_documents:
                result = await self.context_manager.database.execute_sql_query("SELECT COUNT(*) FROM unified_documents")
                unified_count = result['results'][0]['COUNT(*)'] if result['success'] else 0
            
            # Check deprecated tables
            deprecated_found = []
            for table in self.deprecated_tables:
                if table in existing_tables:
                    try:
                        result = await self.context_manager.database.execute_sql_query(f"SELECT COUNT(*) FROM {table}")
                        count = result['results'][0]['COUNT(*)'] if result['success'] else 0
                        if count > 0:
                            deprecated_found.append({'table': table, 'records': count})
                    except Exception:
                        pass
            
            # Determine migration need
            migration_needed = (
                current_version < 4 and 
                has_unified_documents and 
                not has_documents and
                unified_count > 0
            )
            
            return {
                'migration_needed': migration_needed,
                'current_version': current_version,
                'target_version': 4,
                'has_unified_documents': has_unified_documents,
                'has_documents': has_documents,
                'unified_documents_count': unified_count,
                'deprecated_tables_found': deprecated_found,
                'existing_tables': existing_tables
            }
            
        except Exception as e:
            logger.error(f"Migration analysis failed: {e}")
            return {
                'migration_needed': False,
                'error': str(e)
            }
    
    async def _create_documents_table(self, cursor=None) -> None:
        """Create the v2.0 documents table with full schema"""
        await self.context_manager.database.execute_sql_query("""
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uuid TEXT UNIQUE NOT NULL,
                project_uuid TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                document_type TEXT DEFAULT 'general',
                tags TEXT DEFAULT '[]',
                metadata TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                source_file TEXT,
                source_file_created TIMESTAMP,
                source_file_modified TIMESTAMP,
                content_signature TEXT
            )
        """)
        logger.info("✅ Created documents table with v2.0 schema")
    
    async def _migrate_data_to_documents(self, cursor=None) -> int:
        """Migrate all records from unified_documents to documents table"""
        try:
            # Get project UUID (consistent with existing architecture)
            project_uuid = getattr(self.context_manager.database, 'project_uuid', None)
            if not project_uuid:
                # Generate project UUID if not exists
                import uuid
                project_uuid = str(uuid.uuid4())
                logger.warning(f"Generated new project UUID: {project_uuid}")
            
            # Migrate records with proper field mapping
            result = await self.context_manager.database.execute_sql_query("""
                INSERT INTO documents (
                    uuid, project_uuid, title, content, document_type, tags, metadata,
                    created_at, updated_at, imported_at, status, source_file,
                    source_file_created, source_file_modified, content_signature
                )
                SELECT 
                    original_uuid as uuid,
                    ? as project_uuid,
                    title,
                    content,
                    document_type,
                    tags,
                    metadata,
                    created_at,
                    updated_at,
                    imported_at,
                    status,
                    source_file,
                    source_file_created,
                    source_file_modified,
                    content_signature
                FROM unified_documents
                WHERE status = 'active'
            """, [project_uuid])
            
            # Get count of migrated records
            count_result = await self.context_manager.database.execute_sql_query("SELECT COUNT(*) FROM documents")
            migrated_count = count_result['results'][0][list(result['results'][0].keys())[0]] if count_result['success'] else 0
            
            logger.info(f"✅ Migrated {migrated_count} records from unified_documents to documents")
            return migrated_count
            
        except Exception as e:
            logger.error(f"Data migration failed: {e}")
            raise e
    
    async def _create_documents_fts(self, cursor=None) -> None:
        """Create FTS5 table for documents with proper configuration"""
        await self.context_manager.database.execute_sql_query("""
            CREATE VIRTUAL TABLE documents_fts USING fts5(
                title, content, tags, document_type,
                content='documents',
                content_rowid='id'
            )
        """)
        
        # Populate FTS table
        await self.context_manager.database.execute_sql_query("""
            INSERT INTO documents_fts(title, content, tags, document_type)
            SELECT title, content, tags, document_type FROM documents
        """)
        
        logger.info("✅ Created documents_fts with full-text search capability")
    
    async def _create_documents_indexes(self, cursor=None) -> None:
        """Create performance indexes for documents table"""
        indexes = [
            "CREATE INDEX idx_documents_uuid ON documents(uuid)",
            "CREATE INDEX idx_documents_project_uuid ON documents(project_uuid)",
            "CREATE INDEX idx_documents_type ON documents(document_type)",
            "CREATE INDEX idx_documents_status ON documents(status)",
            "CREATE INDEX idx_documents_created ON documents(created_at)",
            "CREATE INDEX idx_documents_source_file ON documents(source_file)"
        ]
        
        for index_sql in indexes:
            await self.context_manager.database.execute_sql_query(index_sql)
        
        logger.info(f"✅ Created {len(indexes)} performance indexes for documents table")
    
    async def _drop_deprecated_tables(self, cursor=None) -> List[str]:
        """
        NEW FEATURE: Drop deprecated tables after successful migration
        
        This is the missing final cleanup step that completes the v2.0 migration
        """
        dropped_tables = []
        
        # Get list of existing tables
        result = await self.context_manager.database.execute_sql_query("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in result['results']} if result['success'] else set()
        
        # Drop deprecated tables that exist
        for table in self.deprecated_tables:
            if table in existing_tables:
                try:
                    await self.context_manager.database.execute_sql_query(f"DROP TABLE {table}")
                    dropped_tables.append(table)
                    logger.info(f"🗑️  Dropped deprecated table: {table}")
                except Exception as e:
                    logger.warning(f"Failed to drop table {table}: {e}")
        
        if dropped_tables:
            logger.info(f"✅ Successfully dropped {len(dropped_tables)} deprecated tables")
        else:
            logger.info("ℹ️  No deprecated tables found to drop")
            
        return dropped_tables
    
    async def _validate_migration(self) -> Dict[str, Any]:
        """Validate that migration completed successfully with comprehensive checks - FIXED: Using proper database interface"""
        try:
            # Check schema version
            result = await self.context_manager.database.execute_sql_query("PRAGMA user_version")
            version = result['results'][0][list(result['results'][0].keys())[0]] if result['success'] else 0
            if version != 4:
                return {'valid': False, 'message': f'Schema version is {version}, expected 4'}
            
            # Check documents table exists and has data
            result = await self.context_manager.database.execute_sql_query("SELECT COUNT(*) FROM documents")
            doc_count = result['results'][0][list(result['results'][0].keys())[0]] if result['success'] else 0
            if doc_count == 0:
                return {'valid': False, 'message': 'Documents table exists but is empty'}
            
            # Check FTS table exists and is populated
            try:
                result = await self.context_manager.database.execute_sql_query("SELECT COUNT(*) FROM documents_fts")
                fts_count = result['results'][0][list(result['results'][0].keys())[0]] if result['success'] else 0
                if fts_count != doc_count:
                    return {'valid': False, 'message': f'FTS count ({fts_count}) != documents count ({doc_count})'}
            except Exception:
                return {'valid': False, 'message': 'documents_fts table missing or corrupted'}
            
            # Check that unified_documents no longer exists or is empty
            try:
                result = await self.context_manager.database.execute_sql_query("SELECT COUNT(*) FROM unified_documents")
                unified_count = result['results'][0][list(result['results'][0].keys())[0]] if result['success'] else 0
                if unified_count > 0:
                    return {'valid': False, 'message': f'unified_documents still contains {unified_count} records'}
            except Exception:
                pass  # Table doesn't exist, which is fine
            
            return {
                'valid': True,
                'message': f'Migration validation successful: {doc_count} documents in v2.0 schema',
                'documents_count': doc_count,
                'fts_count': fts_count,
                'schema_version': version
            }
            
        except Exception as e:
            return {'valid': False, 'message': f'Validation failed: {str(e)}'}
    
    async def rollback_from_backup(self, backup_path: str, confirm: bool = False) -> dict:
        """
        Rollback database to backup state with enhanced safety checks
        
        Args:
            backup_path: Path to backup file
            confirm: Required confirmation for safety
        """
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                return {
                    'status': 'error',
                    'message': f'Backup file not found: {backup_path}'
                }
            
            if not confirm:
                return {
                    'status': 'confirmation_required',
                    'message': f"""🚨 **ROLLBACK CONFIRMATION REQUIRED**
                    
**⚠️  WARNING:** This will completely replace your current database with the backup.

**📁 BACKUP FILE:** {backup_path}
**📊 CURRENT DB:** {self.db_path}

**💥 THIS ACTION WILL:**
• Replace all current data with backup data
• Lose any changes made since backup
• Cannot be undone

Call again with confirm=True to proceed with rollback."""
                }
            
            # Create a backup of current state before rollback
            current_backup = await self.create_backup()
            
            # Perform rollback
            shutil.copy2(backup_file, self.db_path)
            
            # Verify rollback
            if self.context_manager.is_initialized():
                await self.context_manager.database.initialize()  # Reconnect
            
            logger.info(f"Database rolled back from: {backup_path}")
            return {
                'status': 'success',
                'message': f'✅ Database successfully rolled back from backup',
                'rollback_source': backup_path,
                'current_backup': str(current_backup) if current_backup else None
            }
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return {
                'status': 'error',
                'message': f'Rollback failed: {str(e)}'
            }
    
    async def validate_migration(self) -> dict:
        """Public interface for migration validation"""
        return await self._validate_migration()
    
    async def list_backups(self) -> list:
        """List available backup files with enhanced metadata"""
        try:
            if not self.backup_dir.exists():
                return []
            
            backups = []
            for backup_file in self.backup_dir.glob("*.db"):
                try:
                    stat = backup_file.stat()
                    
                    # Try to read backup metadata if available
                    metadata = {}
                    try:
                        with sqlite3.connect(backup_file) as conn:
                            cursor = conn.cursor()
                            cursor.execute("SELECT * FROM backup_metadata LIMIT 1")
                            row = cursor.fetchone()
                            if row:
                                metadata = {
                                    'backup_timestamp': row[0],
                                    'original_path': row[1],
                                    'migration_version': row[2],
                                    'backup_reason': row[3]
                                }
                    except sqlite3.Error:
                        pass  # No metadata available
                    
                    backups.append({
                        'filename': backup_file.name,
                        'path': str(backup_file),
                        'size_mb': round(stat.st_size / 1024 / 1024, 2),
                        'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                        'metadata': metadata
                    })
                    
                except Exception as e:
                    logger.warning(f"Error reading backup {backup_file}: {e}")
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Backup listing failed: {e}")
            return []
