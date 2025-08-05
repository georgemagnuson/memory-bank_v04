#!/usr/bin/env python3
"""
v2.0 to v2.1 Migration Tool
Filename: migrate_v2_to_v2_1.py  
Generated: 2025-08-04.0155
Purpose: Migrate from v2.0 with legacy tables to clean v2.1 schema

MIGRATION PROCESS:
1. Backup database before migration
2. Migrate content from unified_documents → documents  
3. Migrate content from legacy tables → documents
4. Remove all legacy tables
5. Update schema version to v2.1
"""

import sqlite3
import shutil
import json
from datetime import datetime
from pathlib import Path
from enhanced_version_detector import EnhancedVersionDetector, analyze_database_version

def create_backup(db_path: str) -> str:
    """Create backup before migration"""
    backup_path = f"{db_path}.v2_to_v21_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"💾 Backup created: {backup_path}")
    return backup_path

def migrate_unified_documents_to_documents(cursor, project_uuid="legacy-project"):
    """Migrate content from unified_documents to documents table"""
    print("🔄 Migrating unified_documents → documents...")
    
    # Check if unified_documents has content
    cursor.execute("SELECT COUNT(*) FROM unified_documents")
    unified_count = cursor.fetchone()[0]
    
    if unified_count == 0:
        print("   ✅ No unified_documents content to migrate")
        return 0
    
    # Migrate unified_documents to documents
    migration_query = """
    INSERT INTO documents (
        project_uuid, uuid, version, document_type, title, content, 
        summary, tags, metadata, created_at, updated_at, status, importance
    )
    SELECT 
        ? as project_uuid,
        COALESCE(uuid, 'unified-' || rowid) as uuid,
        COALESCE(version, 1) as version,
        COALESCE(document_type, 'document') as document_type,
        COALESCE(title, 'Migrated Document') as title,
        content,
        COALESCE(summary, '') as summary,
        COALESCE(tags, '[]') as tags,
        COALESCE(metadata, '{}') as metadata,
        COALESCE(created_at, datetime('now')) as created_at,
        COALESCE(updated_at, datetime('now')) as updated_at,
        COALESCE(status, 'active') as status,
        COALESCE(importance, 5) as importance
    FROM unified_documents
    WHERE NOT EXISTS (
        SELECT 1 FROM documents d 
        WHERE d.uuid = COALESCE(unified_documents.uuid, 'unified-' || unified_documents.rowid)
        AND d.project_uuid = ?
    )
    """
    
    cursor.execute(migration_query, (project_uuid, project_uuid))
    migrated_count = cursor.rowcount
    print(f"   ✅ Migrated {migrated_count} records from unified_documents")
    return migrated_count

def migrate_legacy_tables_to_documents(cursor, project_uuid="legacy-project"):
    """Migrate content from legacy tables to documents"""
    legacy_tables = {
        'artifacts': 'artifact',
        'discussions': 'discussion', 
        'plans': 'plan',
        'code_iterations': 'code'
    }
    
    total_migrated = 0
    
    for table_name, document_type in legacy_tables.items():
        # Check if table exists and has content
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            continue
            
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        table_count = cursor.fetchone()[0]
        
        if table_count == 0:
            print(f"   ✅ No content in {table_name}")
            continue
            
        print(f"🔄 Migrating {table_name} → documents...")
        
        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        
        # Build migration query based on available columns
        if 'uuid' in columns and 'project_uuid' in columns:
            # Modern table structure
            migration_query = f"""
            INSERT INTO documents (
                project_uuid, uuid, version, document_type, title, content, 
                summary, tags, metadata, created_at, updated_at, status, importance
            )
            SELECT 
                project_uuid,
                uuid,
                COALESCE(version, 1) as version,
                '{document_type}' as document_type,
                COALESCE(title, 'Migrated from {table_name}') as title,
                content,
                COALESCE(summary, '') as summary,
                COALESCE(tags, '[]') as tags,
                COALESCE(metadata, '{{}}') as metadata,
                COALESCE(created_at, datetime('now')) as created_at,
                COALESCE(updated_at, datetime('now')) as updated_at,
                COALESCE(status, 'active') as status,
                COALESCE(importance, 5) as importance
            FROM {table_name}
            WHERE NOT EXISTS (
                SELECT 1 FROM documents d 
                WHERE d.project_uuid = {table_name}.project_uuid 
                AND d.uuid = {table_name}.uuid
            )
            """
        else:
            # Legacy table structure - generate UUIDs
            migration_query = f"""
            INSERT INTO documents (
                project_uuid, uuid, version, document_type, title, content, 
                summary, tags, metadata, created_at, updated_at, status, importance
            )
            SELECT 
                '{project_uuid}' as project_uuid,
                '{table_name}-' || rowid as uuid,
                1 as version,
                '{document_type}' as document_type,
                COALESCE(title, 'Migrated from {table_name}') as title,
                content,
                COALESCE(summary, '') as summary,
                COALESCE(tags, '[]') as tags,
                COALESCE(metadata, '{{}}') as metadata,
                COALESCE(created_at, datetime('now')) as created_at,
                COALESCE(updated_at, datetime('now')) as updated_at,
                'active' as status,
                5 as importance
            FROM {table_name}
            """
        
        cursor.execute(migration_query)
        migrated_count = cursor.rowcount
        total_migrated += migrated_count
        print(f"   ✅ Migrated {migrated_count} records from {table_name}")
    
    return total_migrated

def cleanup_legacy_tables(cursor):
    """Remove all legacy tables after successful migration"""
    legacy_tables = [
        'artifacts', 'artifacts_fts', 'artifacts_fts_config', 'artifacts_fts_data', 'artifacts_fts_docsize', 'artifacts_fts_idx',
        'discussions', 'discussions_fts', 'discussions_fts_config', 'discussions_fts_data', 'discussions_fts_docsize', 'discussions_fts_idx',
        'plans', 'plans_fts', 'plans_fts_config', 'plans_fts_data', 'plans_fts_docsize', 'plans_fts_idx',
        'code_iterations', 'code_iterations_fts', 'code_iterations_fts_config', 'code_iterations_fts_data', 'code_iterations_fts_docsize', 'code_iterations_fts_idx',
        'unified_documents', 'unified_documents_fts', 'unified_documents_fts_config', 'unified_documents_fts_data', 'unified_documents_fts_docsize', 'unified_documents_fts_idx'
    ]
    
    print("🧹 Cleaning up legacy tables...")
    
    # Check which tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    existing_tables = {row[0] for row in cursor.fetchall()}
    
    tables_to_drop = [table for table in legacy_tables if table in existing_tables]
    
    dropped_count = 0
    for table in tables_to_drop:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            dropped_count += 1
            print(f"   🗑️ Dropped: {table}")
        except Exception as e:
            print(f"   ⚠️ Failed to drop {table}: {e}")
    
    print(f"   ✅ Cleaned up {dropped_count} legacy tables")
    return dropped_count

def rebuild_fts_indexes(cursor):
    """Rebuild FTS5 indexes after migration"""
    print("🔍 Rebuilding FTS5 indexes...")
    
    fts_tables = ['documents_fts', 'markdown_search']
    
    for fts_table in fts_tables:
        try:
            # Check if FTS table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (fts_table,))
            if cursor.fetchone():
                cursor.execute(f"INSERT INTO {fts_table}({fts_table}) VALUES('rebuild')")
                print(f"   ✅ Rebuilt {fts_table} index")
        except Exception as e:
            print(f"   ⚠️ Failed to rebuild {fts_table}: {e}")

def update_schema_version(cursor, version=2.1):
    """Update schema version in database"""
    # Use integer version for PRAGMA (multiply by 10)
    version_int = int(version * 10)
    cursor.execute(f'PRAGMA user_version = {version_int}')
    print(f"   ✅ Updated schema version to v{version}")

def migrate_v2_to_v21(db_path: str, dry_run: bool = False) -> bool:
    """
    Main migration function from v2.0 to v2.1
    
    Args:
        db_path: Path to the database
        dry_run: If True, analyze but don't make changes
        
    Returns:
        bool: Success status
    """
    print(f"🚀 Memory Bank v2.0 → v2.1 Migration")
    print(f"📁 Database: {db_path}")
    print(f"🧪 Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
    print()
    
    # Analyze current state
    print("🔍 Analyzing current database state...")
    schema_info = EnhancedVersionDetector.detect_version_enhanced(db_path)
    
    print(f"   📊 Current version: v{schema_info.version}")
    print(f"   📋 Table count: {schema_info.table_count}")
    print(f"   📄 Total records: {sum(schema_info.record_counts.values())}")
    
    if schema_info.version >= 2.1:
        print("✅ Database is already v2.1 or newer - no migration needed")
        return True
    
    if schema_info.migration_type not in ['v2_to_v2.1', 'cleanup_legacy']:
        print(f"❌ Migration type '{schema_info.migration_type}' not supported by this tool")
        return False
    
    if dry_run:
        print("🧪 DRY RUN - Migration plan:")
        unified_records = schema_info.record_counts.get('unified_documents', 0)
        legacy_records = sum(schema_info.record_counts.get(table, 0) 
                           for table in ['artifacts', 'discussions', 'plans', 'code_iterations'])
        
        print(f"   📄 Would migrate {unified_records} unified_documents records")
        print(f"   📄 Would migrate {legacy_records} legacy table records")
        print(f"   🗑️ Would remove ~{schema_info.table_count - 18} legacy tables")
        print(f"   📊 Final table count: ~18 tables")
        return True
    
    # Create backup
    backup_path = create_backup(db_path)
    
    # Confirm migration
    confirm = input("\\nProceed with v2.0 → v2.1 migration? (yes/no): ").lower().strip()
    if confirm != 'yes':
        print("❌ Migration cancelled")
        return False
    
    # Perform migration
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        total_migrated = 0
        
        # Step 1: Migrate unified_documents to documents
        migrated_unified = migrate_unified_documents_to_documents(cursor)
        total_migrated += migrated_unified
        
        # Step 2: Migrate legacy tables to documents
        migrated_legacy = migrate_legacy_tables_to_documents(cursor)
        total_migrated += migrated_legacy
        
        # Step 3: Clean up legacy tables
        dropped_tables = cleanup_legacy_tables(cursor)
        
        # Step 4: Rebuild FTS indexes
        rebuild_fts_indexes(cursor)
        
        # Step 5: Update schema version
        update_schema_version(cursor, 2.1)
        
        # Commit all changes
        conn.commit()
        
        # Verify final state
        final_schema = EnhancedVersionDetector.detect_version_enhanced(db_path)
        
        print(f"\\n🎉 Migration Complete!")
        print(f"   📄 Records migrated: {total_migrated}")
        print(f"   🗑️ Legacy tables removed: {dropped_tables}")
        print(f"   📊 Final table count: {final_schema.table_count}")
        print(f"   🏷️ Final version: v{final_schema.version}")
        print(f"   💾 Backup available: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migrate_v2_to_v21.py <database_path> [--dry-run]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        sys.exit(1)
    
    success = migrate_v2_to_v21(db_path, dry_run)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
