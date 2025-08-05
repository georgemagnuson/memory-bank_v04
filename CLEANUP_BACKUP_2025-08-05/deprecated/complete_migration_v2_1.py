#!/usr/bin/env python3
"""
Complete v2.1 Migration with ALL Table Types
Filename: complete_migration_v2_1.py
Generated: 2025-08-04.0200
Purpose: Complete migration from v1/v2 to v2.1 handling ALL table types

COMPLETE TABLE MIGRATION:
- unified_documents → documents (type='document')
- discussions → documents (type='discussion')  
- artifacts → documents (type='artifact')
- plans → documents (type='plan')
- code_iterations → documents (type='code')
- chat_sessions → documents (type='chat_session')
- decisions → documents (type='decision') [if exists]
- Any other content tables → documents (with appropriate type)

Then cleanup ALL legacy tables for clean v2.1 schema.
"""

import sqlite3
import shutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any

def get_all_content_tables(cursor) -> Dict[str, str]:
    """
    Discover all content tables and their appropriate document_type mapping
    
    Args:
        cursor: SQLite cursor
        
    Returns:
        Dict mapping table_name → document_type
    """
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = {row[0] for row in cursor.fetchall()}
    
    # Define content table mappings (table_name → document_type)
    content_table_mapping = {
        'unified_documents': 'document',  # Keep existing document_type if available
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
    
    # Filter to only tables that actually exist and have content
    existing_content_tables = {}
    
    for table_name, doc_type in content_table_mapping.items():
        if table_name in all_tables:
            try:
                # Check if table has content
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                if count > 0:
                    existing_content_tables[table_name] = doc_type
                    print(f"   📄 Found content table: {table_name} ({count} records) → {doc_type}")
            except Exception as e:
                print(f"   ⚠️ Could not check {table_name}: {e}")
    
    return existing_content_tables

def analyze_table_structure(cursor, table_name: str) -> Dict[str, Any]:
    """Analyze table structure to understand column mapping"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = {row[1]: row[2] for row in cursor.fetchall()}  # column_name → type
    
    # Check for sample data to understand structure
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
    sample_row = cursor.fetchone()
    
    return {
        'columns': list(columns.keys()),
        'column_types': columns,
        'has_sample': sample_row is not None,
        'sample_data': dict(zip(columns.keys(), sample_row)) if sample_row else {}
    }

def build_migration_query(table_name: str, document_type: str, structure: Dict[str, Any], 
                         project_uuid: str = "legacy-project") -> str:
    """
    Build appropriate migration query based on table structure
    
    Args:
        table_name: Source table name
        document_type: Target document_type
        structure: Table structure info
        project_uuid: Project UUID to use
        
    Returns:
        SQL query for migration
    """
    columns = structure['columns']
    
    # Handle unified_documents specially (might already have document_type)
    if table_name == 'unified_documents':
        if 'document_type' in columns:
            # Use existing document_type
            migration_query = f"""
            INSERT INTO documents (
                project_uuid, uuid, version, document_type, title, content, 
                summary, tags, metadata, created_at, updated_at, status, importance
            )
            SELECT 
                COALESCE(project_uuid, '{project_uuid}') as project_uuid,
                COALESCE(uuid, '{table_name}-' || rowid) as uuid,
                COALESCE(version, 1) as version,
                COALESCE(document_type, '{document_type}') as document_type,
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
                WHERE d.uuid = COALESCE({table_name}.uuid, '{table_name}-' || {table_name}.rowid)
                AND d.project_uuid = COALESCE({table_name}.project_uuid, '{project_uuid}')
            )
            """
        else:
            # No document_type column - use default
            migration_query = f"""
            INSERT INTO documents (
                project_uuid, uuid, version, document_type, title, content, 
                summary, tags, metadata, created_at, updated_at, status, importance
            )
            SELECT 
                '{project_uuid}' as project_uuid,
                COALESCE(uuid, '{table_name}-' || rowid) as uuid,
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
            """
    
    # Handle other content tables
    elif all(col in columns for col in ['uuid', 'project_uuid']):
        # Modern table with proper UUID structure
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
        # Legacy table - generate UUIDs
        title_column = 'title' if 'title' in columns else "'Migrated from " + table_name + "'"
        content_column = 'content' if 'content' in columns else "'Legacy content from " + table_name + "'"
        
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
            COALESCE({title_column}, 'Migrated from {table_name}') as title,
            COALESCE({content_column}, 'Legacy content') as content,
            COALESCE(summary, '') as summary,
            COALESCE(tags, '[]') as tags,
            COALESCE(metadata, '{{}}') as metadata,
            COALESCE(created_at, datetime('now')) as created_at,
            COALESCE(updated_at, datetime('now')) as updated_at,
            'active' as status,
            5 as importance
        FROM {table_name}
        """
    
    return migration_query

def migrate_all_content_tables(cursor, content_tables: Dict[str, str], 
                              project_uuid: str = "legacy-project") -> Dict[str, int]:
    """
    Migrate all content tables to documents table
    
    Args:
        cursor: SQLite cursor
        content_tables: Dict of table_name → document_type
        project_uuid: Project UUID to use
        
    Returns:
        Dict of table_name → records_migrated
    """
    migration_results = {}
    total_migrated = 0
    
    print("🔄 Migrating all content tables to documents...")
    
    for table_name, document_type in content_tables.items():
        print(f"\\n📄 Processing {table_name} → documents (type='{document_type}')")
        
        # Analyze table structure
        structure = analyze_table_structure(cursor, table_name)
        print(f"   📋 Columns: {', '.join(structure['columns'])}")
        
        # Build migration query
        migration_query = build_migration_query(table_name, document_type, structure, project_uuid)
        
        # Execute migration
        try:
            cursor.execute(migration_query)
            migrated_count = cursor.rowcount
            migration_results[table_name] = migrated_count
            total_migrated += migrated_count
            print(f"   ✅ Migrated {migrated_count} records from {table_name}")
        except Exception as e:
            print(f"   ❌ Failed to migrate {table_name}: {e}")
            migration_results[table_name] = 0
    
    print(f"\\n✅ Total migration complete: {total_migrated} records migrated from {len(content_tables)} tables")
    return migration_results

def get_all_legacy_tables(cursor) -> List[str]:
    """Get complete list of legacy tables to cleanup"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    all_tables = {row[0] for row in cursor.fetchall()}
    
    # Core v2.1 tables to keep
    v21_core_tables = {
        'documents', 'documents_fts', 'documents_fts_data', 'documents_fts_idx', 
        'documents_fts_docsize', 'documents_fts_config',
        'projects', 'project_context', 
        'markdown_files', 'markdown_search', 'markdown_search_data', 'markdown_search_idx',
        'markdown_search_docsize', 'markdown_search_config',
        'cross_references', 'semantic_equivalents',
        'sqlite_sequence'  # SQLite system table
    }
    
    # Everything else is legacy
    legacy_tables = [table for table in all_tables 
                    if table not in v21_core_tables 
                    and not table.startswith('sqlite_')]
    
    return sorted(legacy_tables)

def complete_v21_migration(db_path: str, dry_run: bool = False) -> bool:
    """
    Complete migration to v2.1 with ALL table types
    
    Args:
        db_path: Path to database
        dry_run: If True, analyze but don't migrate
        
    Returns:
        bool: Success status
    """
    print(f"🚀 Complete Memory Bank v2.1 Migration")
    print(f"📁 Database: {db_path}")
    print(f"🧪 Mode: {'DRY RUN' if dry_run else 'LIVE MIGRATION'}")
    print()
    
    if not Path(db_path).exists():
        print(f"❌ Database not found: {db_path}")
        return False
    
    # Create backup
    if not dry_run:
        backup_path = f"{db_path}.complete_v21_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy2(db_path, backup_path)
        print(f"💾 Backup created: {backup_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Step 1: Discover all content tables
        print("🔍 Step 1: Discovering content tables...")
        content_tables = get_all_content_tables(cursor)
        
        if not content_tables:
            print("✅ No content tables found to migrate")
            return True
        
        print(f"   📊 Found {len(content_tables)} content tables with data")
        
        # Step 2: Get legacy tables for cleanup
        print("\\n🔍 Step 2: Analyzing legacy tables...")
        legacy_tables = get_all_legacy_tables(cursor)
        print(f"   🗑️ Found {len(legacy_tables)} legacy tables to cleanup")
        
        if dry_run:
            print(f"\\n🧪 DRY RUN - Migration Plan:")
            total_records = 0
            for table_name, doc_type in content_tables.items():
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                total_records += count
                print(f"   📄 {table_name}: {count} records → documents (type='{doc_type}')")
            
            print(f"\\n📊 Summary:")
            print(f"   📄 Total records to migrate: {total_records}")
            print(f"   🗑️ Legacy tables to remove: {len(legacy_tables)}")
            print(f"   📋 Final table count: ~{len(get_all_legacy_tables(cursor)) - len(legacy_tables) + 7} tables")
            return True
        
        # Confirm migration
        total_records = sum(cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] 
                          for table in content_tables.keys())
        
        print(f"\\n⚠️ MIGRATION SUMMARY:")
        print(f"   📄 {len(content_tables)} tables → documents table")
        print(f"   📊 {total_records} total records to migrate")
        print(f"   🗑️ {len(legacy_tables)} legacy tables to remove")
        
        confirm = input("\\nProceed with complete v2.1 migration? (yes/no): ").lower().strip()
        if confirm != 'yes':
            print("❌ Migration cancelled")
            return False
        
        # Step 3: Migrate all content
        print("\\n🔄 Step 3: Migrating all content tables...")
        migration_results = migrate_all_content_tables(cursor, content_tables)
        
        # Step 4: Cleanup legacy tables
        print("\\n🧹 Step 4: Cleaning up legacy tables...")
        dropped_count = 0
        for table in legacy_tables:
            try:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
                dropped_count += 1
                print(f"   🗑️ Dropped: {table}")
            except Exception as e:
                print(f"   ⚠️ Failed to drop {table}: {e}")
        
        # Step 5: Rebuild FTS
        print("\\n🔍 Step 5: Rebuilding FTS indexes...")
        try:
            cursor.execute("INSERT INTO documents_fts(documents_fts) VALUES('rebuild')")
            print("   ✅ Rebuilt documents_fts index")
        except Exception as e:
            print(f"   ⚠️ FTS rebuild issue: {e}")
        
        # Step 6: Update schema version
        print("\\n🏷️ Step 6: Updating schema version...")
        cursor.execute('PRAGMA user_version = 21')  # v2.1 = version 21
        print("   ✅ Updated to v2.1")
        
        # Commit all changes
        conn.commit()
        
        # Final verification
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        final_tables = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT COUNT(*) FROM documents")
        final_doc_count = cursor.fetchone()[0]
        
        print(f"\\n🎉 Migration Complete!")
        print(f"   📄 Total records in documents: {final_doc_count}")
        print(f"   📋 Final table count: {len(final_tables)}")
        print(f"   🗑️ Legacy tables removed: {dropped_count}")
        print(f"   💾 Backup available: {backup_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if not dry_run:
            conn.rollback()
        return False
        
    finally:
        conn.close()

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python complete_migration_v2_1.py <database_path> [--dry-run]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    success = complete_v21_migration(db_path, dry_run)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
