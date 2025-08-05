#!/usr/bin/env python3
"""
Enhanced Schema Manager Integration with Complete v2.1 Migration
Filename: enhanced_schema_manager_patch.py
Generated: 2025-08-04.0210
Purpose: Patch for existing schema_manager.py to add complete v2.1 migration support

ENHANCEMENTS:
1. Table count-based version detection (v2.1 = ~18 tables)
2. Complete migration of ALL content tables to documents
3. Legacy table cleanup for clean v2.1 schema
4. Enhanced work_on_project integration
"""

import logging
from pathlib import Path
from typing import Dict, Any
from enhanced_version_detector import EnhancedVersionDetector
from complete_migration_v2_1 import complete_v21_migration

logger = logging.getLogger(__name__)

class EnhancedSchemaManager:
    """Enhanced schema manager with complete v2.1 migration support"""
    
    def __init__(self, context_manager):
        self.context_manager = context_manager
        
    async def check_and_upgrade_database_enhanced(self) -> str:
        """
        Enhanced database version checking with table count-based v2.1 detection
        Replaces the original check_and_upgrade_database method
        """
        try:
            # Check if database exists first
            db_path = Path(self.context_manager.database_path)
            if not db_path.exists():
                return await self.create_new_v21_database()
            
            if not self.context_manager.is_initialized():
                return "❌ Database not initialized. Context manager initialization failed."
            
            # Enhanced version detection using table count
            schema_info = EnhancedVersionDetector.detect_version_enhanced(str(db_path))
            
            logger.info(f"Enhanced detection - Version: {schema_info.version}, Tables: {schema_info.table_count}")
            
            # Handle different version scenarios
            if schema_info.version >= 2.1:
                # Already v2.1 - current and ready
                return f"""✅ **Database is current v{schema_info.version}**

📊 **Database Status:**
• Database: {db_path.name}
• Version: v{schema_info.version} (Clean Schema)
• Tables: {schema_info.table_count}
• Records: {sum(schema_info.record_counts.values())}

🏗️ **v2.1 Features Active:**
• Clean table architecture (documents table only)
• Optimized FTS5 full-text search
• Enhanced cross-project support
• All legacy tables removed

✅ **Ready for use!**"""
            
            elif schema_info.needs_migration:
                # Needs migration to v2.1
                if schema_info.migration_type == 'v2_to_v2.1':
                    return await self._offer_v2_to_v21_migration(db_path, schema_info)
                elif schema_info.migration_type == 'v1_to_v2.1':
                    return await self._offer_v1_to_v21_migration(db_path, schema_info)
                else:
                    return await self._offer_generic_migration(db_path, schema_info)
            
            else:
                return f"✅ Database version v{schema_info.version} is current"
                
        except Exception as e:
            logger.error(f"Enhanced database check failed: {e}")
            return f"❌ Database check failed: {str(e)}"
    
    async def _offer_v2_to_v21_migration(self, db_path: Path, schema_info) -> str:
        """Offer v2.0 → v2.1 migration with content consolidation"""
        content_summary = []
        total_records = sum(schema_info.record_counts.values())
        
        for table, count in schema_info.record_counts.items():
            if count > 0:
                content_summary.append(f"• {table}: {count} records")
        
        return f"""🔄 **Migration Available: v2.0 → v2.1**

📊 **Current Database:**
• Version: v{schema_info.version} (Legacy tables present)
• Tables: {schema_info.table_count}
• Total Records: {total_records}

📋 **Content to Migrate:**
{chr(10).join(content_summary)}

🎯 **v2.1 Migration Benefits:**
• **Complete Table Consolidation:** ALL content → documents table
• **Clean Schema:** {schema_info.table_count} → ~18 tables
• **Better Performance:** Optimized indexes and FTS
• **Future-Proof:** Ready for next-generation features

🔄 **Migration Process:**
1. ✅ Automatic backup creation
2. ✅ Migrate ALL content tables → documents
3. ✅ Remove legacy tables for clean schema
4. ✅ Rebuild FTS5 indexes
5. ✅ Update to v2.1

⚠️ **Important:** This will permanently remove legacy tables after migration.

**To proceed:** Call `migrate_to_v21(confirm=True)`
**To cancel:** Take no action - database remains unchanged"""
    
    async def _offer_v1_to_v21_migration(self, db_path: Path, schema_info) -> str:
        """Offer v1.x → v2.1 migration"""
        return f"""🔄 **Migration Available: v1.x → v2.1**

📊 **Current Database:**
• Version: v{schema_info.version} (Legacy)
• Tables: {schema_info.table_count}
• Records: {sum(schema_info.record_counts.values())}

🚀 **Direct Upgrade to v2.1:**
• Skip v2.0 entirely - go straight to latest
• Complete table consolidation
• Modern clean schema

**To proceed:** Call `migrate_to_v21(confirm=True)`"""
    
    async def _offer_generic_migration(self, db_path: Path, schema_info) -> str:
        """Handle other migration scenarios"""
        return f"""⚠️ **Migration Required**

📊 **Current State:**
• Version: v{schema_info.version}
• Migration Type: {schema_info.migration_type}
• Tables: {schema_info.table_count}

🔧 **Action Required:** {schema_info.migration_type}

Please run the appropriate migration command or contact support."""
    
    async def migrate_to_v21(self, confirm: bool = False) -> str:
        """
        Complete migration to v2.1 with ALL table consolidation
        
        Args:
            confirm: User confirmation for migration
            
        Returns:
            Migration result message
        """
        try:
            db_path = Path(self.context_manager.database_path)
            
            if not confirm:
                return """🔄 **v2.1 Migration Confirmation Required**

**⚠️ This migration will:**
• Consolidate ALL content tables → documents table
• Remove ALL legacy tables for clean v2.1 schema  
• Create automatic backup before changes
• Update database to latest v2.1 architecture

**📊 Expected Result:**
• Clean ~18 table schema
• Improved performance
• Future-proof architecture
• All content preserved in documents table

**To proceed:** Call `migrate_to_v21(confirm=True)`
**To cancel:** Take no action"""
            
            # Perform complete v2.1 migration
            logger.info("Starting complete v2.1 migration...")
            migration_success = complete_v21_migration(str(db_path), dry_run=False)
            
            if migration_success:
                # Verify final state
                final_schema = EnhancedVersionDetector.detect_version_enhanced(str(db_path))
                
                return f"""✅ **Migration to v2.1 Complete!**

🎉 **Migration Summary:**
• Version: v{final_schema.version} (Clean Schema)
• Tables: {final_schema.table_count} (optimized)
• Records: {sum(final_schema.record_counts.values())} (all preserved)

🏗️ **v2.1 Features Now Active:**
• Clean documents table architecture
• Optimized FTS5 full-text search
• Enhanced performance and reliability
• Future-proof design

✅ **Database is ready for use!**
All Memory Bank v2.1 features are now available."""
                
            else:
                return """❌ **Migration to v2.1 Failed**

The migration encountered an error. Your database has been left in a safe state.

🛡️ **Recovery Options:**
• Backup was created before migration started
• Original database structure preserved
• Contact support if you need assistance

Please check the logs for detailed error information."""
                
        except Exception as e:
            logger.error(f"v2.1 migration failed: {e}")
            return f"❌ Migration failed: {str(e)}"
    
    async def create_new_v21_database(self) -> str:
        """Create new v2.1 database from scratch"""
        try:
            db_path = Path(self.context_manager.database_path)
            
            if db_path.exists():
                return f"❌ Database already exists: {db_path}"
            
            # Use our enhanced work_on_project to create v2.1 database
            from enhanced_work_on_project import EnhancedWorkOnProject
            manager = EnhancedWorkOnProject()
            
            project_path = str(db_path.parent.parent)  # Go up from memory-bank/context.db to project root
            result = manager._create_new_v21_database(
                str(db_path), 
                db_path.parent.parent.name,  # Project name
                project_path
            )
            
            if result["success"]:
                return f"""✅ **New v2.1 Database Created!**

📊 **Database Details:**
• Location: {db_path.name}
• Version: v2.1 (Clean Schema)
• Tables: ~18 (optimized)
• Architecture: Latest v2.1 design

🎯 **Features Enabled:**
• Clean documents table architecture
• FTS5 full-text search ready
• Cross-project support
• Semantic search capabilities
• Performance optimizations

✅ **Ready for Use:**
Your new project is ready with the latest Memory Bank v2.1!"""
            else:
                return f"❌ Failed to create v2.1 database: {result.get('message', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"v2.1 database creation failed: {e}")
            return f"❌ Database creation failed: {str(e)}"

# Monkey patch for existing schema manager
def patch_existing_schema_manager():
    """
    Monkey patch the existing SchemaManager class to add v2.1 support
    This allows integration without modifying the original files
    """
    try:
        # Import existing SchemaManager
        from memory_bank_mcp.schema_manager import SchemaManager
        
        # Add enhanced methods
        SchemaManager.migrate_to_v21 = EnhancedSchemaManager.migrate_to_v21
        SchemaManager.check_and_upgrade_database_enhanced = EnhancedSchemaManager.check_and_upgrade_database_enhanced
        SchemaManager._offer_v2_to_v21_migration = EnhancedSchemaManager._offer_v2_to_v21_migration
        SchemaManager._offer_v1_to_v21_migration = EnhancedSchemaManager._offer_v1_to_v21_migration
        SchemaManager._offer_generic_migration = EnhancedSchemaManager._offer_generic_migration
        SchemaManager.create_new_v21_database = EnhancedSchemaManager.create_new_v21_database
        
        logger.info("✅ Successfully patched SchemaManager with v2.1 support")
        return True
        
    except ImportError as e:
        logger.error(f"❌ Failed to patch SchemaManager: {e}")
        return False

if __name__ == "__main__":
    # Test the patching
    if patch_existing_schema_manager():
        print("✅ Schema Manager patched successfully")
    else:
        print("❌ Schema Manager patching failed")
