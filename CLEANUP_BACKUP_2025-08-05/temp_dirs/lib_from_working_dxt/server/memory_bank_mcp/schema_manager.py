#!/usr/bin/env python3
"""
server/memory_bank_mcp/schema_manager.py
Generated: 2025-07-29.0131
Purpose: Main schema management coordinator for Memory Bank v2.0

Provides unified interface for:
- Database version checking and migration
- User-friendly status reporting
- Integration with Memory Bank MCP system
- Clean workflow orchestration

Uses modular components from schema_manager_modules package
"""

import logging
from pathlib import Path

# Import modular components from schema_manager_modules package
from .schema_manager_modules import (
    DatabaseVersionDetector,
    SchemaInfo,
    SchemaTemplateManager,
    DatabaseMigrator,
    MigrationResult
)

logger = logging.getLogger(__name__)

class SchemaManager:
    """Main schema management coordinator"""
    
    def __init__(self, context_manager):
        """
        Initialize schema manager with context manager dependency
        
        Args:
            context_manager: Active context manager with database connection
        """
        self.context_manager = context_manager
        self.migrator = DatabaseMigrator(context_manager)
        
    async def check_and_upgrade_database(self) -> str:
        """
        Main entry point for database version checking and migration
        Called once at session start from work_on_project()
        """
        try:
            # Check if database exists first
            db_path = Path(self.context_manager.database_path)
            if not db_path.exists():
                return await self.create_new_project_database()
            
            if not self.context_manager.is_initialized():
                return "❌ Database not initialized. Context manager initialization failed."
            
            # Detect current version
            current_version = await DatabaseVersionDetector.detect_version(self.context_manager)
            schema_info = await DatabaseVersionDetector.get_schema_info(self.context_manager)
            
            logger.info(f"Database version: {current_version}, Tables: {schema_info.table_count}")
            
            # Version 4 is current target (v2.0)
            if current_version == 4:
                await self._ensure_template_stored()
                return f"✅ Database is current (v2.0, version {current_version})\n" + \
                       f"📊 Database: {Path(schema_info.database_path).name}\n" + \
                       f"📋 Tables: {schema_info.table_count}\n" + \
                       f"📄 Documents: {schema_info.record_counts.get('documents', 0)} records"
            
            # Version 0 needs migration to v2.0 - perform automatic migration
            elif current_version == 0:
                logger.info(f"Version 0 (v1.4.0) detected - performing automatic migration to v2.0")
                migration_result = await self.migrate_to_v2(confirm=True)
                return migration_result
            
            # New/empty database
            elif current_version == -1:
                return "ℹ️ Empty database detected. Schema will be created on first use."
            
            # Unknown version
            else:
                return f"⚠️ Unknown database version: {current_version}. Manual review needed."
                
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return f"❌ Database check failed: {str(e)}"
    
    async def migrate_to_v2(self, confirm: bool = False) -> str:
        """
        Perform migration from legacy to v2.0
        
        Args:
            confirm: User confirmation for migration
        """
        try:
            result = await self.migrator.migrate_unified_to_documents(confirm=confirm)
            
            if result.requires_confirmation:
                return f"""🔄 **Migration Ready**
                
{result.error_message}

**⚠️ Important:** This operation will modify your database structure. A backup will be created automatically.

**To proceed:** Call `migrate_to_v2(confirm=True)`
**To cancel:** Take no action - database remains unchanged
"""
            
            if result.success:
                # Store v2.0 template after successful migration
                await self._store_v2_template()
                
                return f"""✅ **Migration to v2.0 completed successfully!**
                
**📊 Migration Summary:**
• Records migrated: {result.records_migrated}
• Version: {result.version_from} → {result.version_to}  
• Tables affected: {len(result.tables_affected)}
• Backup created: {Path(result.backup_path).name if result.backup_path else 'None'}

**🔄 Changes Applied:**
• unified_documents → documents ({result.records_migrated} records)
• FTS tables renamed to match clean naming
• Database version set to 4 (v2.0)
• Schema template stored for future reference

**✅ Next Steps:**
• All Memory Bank v2.0 features now available
• Previous functionality preserved
• Backup available at: {result.backup_path if result.backup_path else 'N/A'}
"""
            else:
                return f"""❌ **Migration failed:** {result.error_message}
                
**🔄 Recovery Options:**
• Backup preserved: {Path(result.backup_path).name if result.backup_path else 'None'}  
• Database left in safe state
• Use `rollback_migration()` if needed
• **Revert to Memory Bank v1.4.0:** Switch back to original context if issues persist

**🆘 Support:** Contact support if you need assistance with recovery
"""
                
        except Exception as e:
            logger.error(f"Migration coordination failed: {e}")
            return f"❌ Migration failed: {str(e)}"
    
    async def rollback_migration(self, backup_path: str, confirm: bool = False) -> str:
        """
        Rollback failed migration using backup
        
        Args:
            backup_path: Path to backup file
            confirm: User confirmation required
        """
        result = await self.migrator.rollback_from_backup(backup_path, confirm=confirm)
        
        if result['status'] == 'confirmation_required':
            return f"""⚠️ **Rollback Confirmation Required**
            
{result['message']}

**Current Database:** {result['database_path']}
**Backup File:** {result['backup_path']}

{result['instructions']}

**⚠️ Warning:** This will overwrite all changes made since the backup was created.
"""
        elif result['status'] == 'success':
            return f"""✅ **Database Rollback Complete**
            
{result['message']}

**Restored From:** {result['restored_from']}
**Current Database:** {result['current_db']}

Your database has been restored to its pre-migration state.
"""
        else:
            return f"❌ **Rollback Failed:** {result['message']}"
    
    async def get_migration_status(self) -> str:
        """Get current migration status and recommendations"""
        try:
            schema_info = await DatabaseVersionDetector.get_schema_info(self.context_manager)
            
            status_report = f"""📊 **Database Migration Status**

**📍 Current Version:** {schema_info.version}
**📂 Database:** {Path(schema_info.database_path).name}
**📋 Tables:** {schema_info.table_count}
**🏗️ Architecture:** {"v2.0 (Clean)" if schema_info.has_clean_tables else "v1.4.0 (Legacy)" if schema_info.has_unified_tables else "Unknown"}

**📄 Content Summary:**
"""
            
            for table, count in schema_info.record_counts.items():
                status_report += f"• {table}: {count} records\n"
            
            # Add recommendations
            if schema_info.version == 0:
                status_report += f"""
**🔄 Recommendation:** Migration to v2.0 available
• Use `migrate_to_v2()` to upgrade to clean table naming
• Backup will be created automatically
• All data will be preserved
"""
            elif schema_info.version == 4:
                status_report += f"""
**✅ Status:** Database is current (v2.0)
• Clean table naming in use
• All v2.0 features available
"""
            else:
                status_report += f"""
**⚠️ Status:** Unknown version - manual review recommended
"""
            
            return status_report
            
        except Exception as e:
            return f"❌ Status check failed: {str(e)}"
    
    async def list_backups(self) -> str:
        """List available database backups"""
        try:
            backups = await self.migrator.list_backups()
            
            if not backups:
                return "📂 **No backups found**\n\nNo database backups are currently available."
            
            backup_list = "📂 **Available Database Backups**\n\n"
            
            for i, backup in enumerate(backups, 1):
                size_mb = backup['size'] / (1024 * 1024)
                backup_list += f"**{i}. {backup['filename']}**\n"
                backup_list += f"   • Size: {size_mb:.1f} MB\n"
                backup_list += f"   • Created: {backup['created'][:19]}\n"
                backup_list += f"   • Path: {backup['path']}\n\n"
            
            backup_list += "**Usage:** `rollback_migration('backup_path', confirm=True)`"
            return backup_list
            
        except Exception as e:
            return f"❌ Backup listing failed: {str(e)}"
    
    async def validate_database(self) -> str:
        """Validate current database state"""
        try:
            validation = await self.migrator.validate_migration()
            
            if validation['valid']:
                return f"""✅ **Database Validation Successful**

{validation['message']}

**Details:**
• Version: {validation['version']}
• Records: {validation['records']}
• Schema: Memory Bank v2.0 compliant
"""
            else:
                return f"""❌ **Database Validation Failed**

**Error:** {validation['error']}

**Recommendations:**
• Check if migration completed successfully
• Use `get_migration_status()` for detailed analysis
• Consider rollback if migration was incomplete
"""
                
        except Exception as e:
            return f"❌ Validation failed: {str(e)}"
    
    async def get_schema_templates(self) -> str:
        """List available schema templates"""
        try:
            templates = await SchemaTemplateManager.list_templates(self.context_manager)
            
            if not templates:
                return "📄 **No schema templates found**\n\nNo schema templates are currently stored."
            
            template_list = "📄 **Available Schema Templates**\n\n"
            
            for i, (title, created) in enumerate(templates, 1):
                template_list += f"**{i}. {title}**\n"
                template_list += f"   • Created: {created[:19] if created else 'Unknown'}\n\n"
            
            return template_list
            
        except Exception as e:
            return f"❌ Template listing failed: {str(e)}"
    
    async def create_new_project_database(self) -> str:
        """
        Create new project database from v2.0 DDL template
        Used when context.db doesn't exist for new project installations
        """
        try:
            if not self.context_manager.is_initialized():
                return "❌ Context manager not initialized"
            
            # Check if database already exists
            db_path = Path(self.context_manager.database_path)
            if db_path.exists():
                return f"⚠️ Database already exists: {db_path.name}\nUse migration tools instead of creation."
            
            # Read DDL template from package
            ddl_path = Path(__file__).parent / "schema_v2_0_template.sql"
            if not ddl_path.exists():
                return f"❌ Schema template not found: {ddl_path}\nEnsure schema_v2_0_template.sql is in the package."
            
            with open(ddl_path, 'r') as f:
                ddl_content = f.read()
            
            logger.info(f"Creating new v2.0 database: {db_path}")
            
            # Create database directory if needed
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Execute DDL to create v2.0 database
            import sqlite3
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Execute the complete DDL script
            cursor.executescript(ddl_content)
            conn.commit()
            
            # Verify creation
            cursor.execute('PRAGMA user_version')
            version = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Store v2.0 template in the new database
            await self.context_manager.database.initialize()  # Initialize connection
            await self._store_v2_template()
            
            logger.info(f"New v2.0 database created successfully: {table_count} tables, version {version}")
            
            return f"""✅ **New Project Database Created Successfully!**

**📊 Database Details:**
• Location: {db_path.name}
• Version: {version} (v2.0)
• Tables: {table_count}
• Schema: Clean v2.0 architecture with documents table

**🎯 Features Enabled:**
• Clean table naming (documents instead of unified_documents)
• Full-text search (FTS5) ready
• All Memory Bank v2.0 functionality available
• Schema template stored for reference

**✅ Ready for Use:**
Your new project is ready with the latest Memory Bank v2.0 architecture!
"""
            
        except Exception as e:
            logger.error(f"Database creation failed: {e}")
            return f"❌ Database creation failed: {str(e)}"
    
    async def _suggest_migration_to_v2(self, schema_info: SchemaInfo) -> str:
        """Suggest migration from legacy to v2.0"""
        records = schema_info.record_counts.get('unified_documents', 0)
        
        return f"""🔄 **Migration Available: v1.4.0 → v2.0**

**📊 Current Database:**
• Version: Legacy (0)
• Records: {records} in unified_documents table
• Tables: {schema_info.table_count}

**🎯 Migration Benefits:**
• Clean table naming (documents vs unified_documents)
• Improved performance and organization  
• Access to latest Memory Bank v2.0 features
• Backward compatibility maintained

**🚀 Next Steps:**
1. **Review:** Use `get_migration_status()` for detailed analysis
2. **Migrate:** Use `migrate_to_v2()` to start migration process
3. **Backup:** Automatic backup created before migration

**⚠️ Safety:** Database will be backed up automatically. Rollback available if needed.
"""
    
    async def _ensure_template_stored(self) -> bool:
        """Ensure v2.0 schema template is stored in current database"""
        existing = await SchemaTemplateManager.get_template(self.context_manager, "Memory Bank v2.0 Schema Template")
        
        if not existing:
            return await self._store_v2_template()
        
        return True
    
    async def _store_v2_template(self) -> bool:
        """Store the v2.0 schema template in documents table"""
        template_content = SchemaTemplateManager.get_v2_schema_template()
        
        return await SchemaTemplateManager.store_template(
            self.context_manager,
            "Memory Bank v2.0 Schema Template",
            template_content,
            "Clean v2.0 schema with documents table and unified architecture"
        )

# Export main class and re-export module components for backward compatibility
__all__ = [
    'SchemaManager',
    # Re-export from modules for convenience
    'DatabaseVersionDetector', 
    'SchemaTemplateManager',
    'DatabaseMigrator',
    'MigrationResult',
    'SchemaInfo'
]
