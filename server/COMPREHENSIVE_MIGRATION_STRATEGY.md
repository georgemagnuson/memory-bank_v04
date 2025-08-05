# Comprehensive Memory Bank Migration Strategy - All Versions

**Generated:** 2025-08-02.2035  
**Status:** 🎯 COMPLETE MIGRATION STRATEGY FOR ALL DATABASE VERSIONS

---

## 🗂️ **DATABASE VERSION HISTORY & MIGRATION SCENARIOS:**

### **✅ Database Evolution Timeline:**

1. **Pre-v1.4.0** (Original separate tables)
   - **Content**: Stored in separate tables (`discussions`, `artifacts`, `plans`, etc.)
   - **Schema**: Each content type had its own table structure
   - **Migration**: Direct table → documents migration

2. **v1.4.0** (Unified documents)
   - **Content**: All content consolidated into `unified_documents` table
   - **Schema**: Single table with `source_table` and `source_id` references
   - **Migration**: unified_documents → documents migration

3. **v2.0** (Target state)
   - **Content**: All content in `documents` table with composite primary key
   - **Schema**: `(project_uuid, uuid, version)` primary key with proper versioning
   - **Features**: Cross-project support, document versioning, clean metadata

### **🔍 Migration Scenarios to Handle:**

1. **Pure Pre-v1.4.0**: Data only in legacy tables (`discussions`, `artifacts`, etc.)
2. **Pure v1.4.0**: Data only in `unified_documents` (our current case)
3. **Mixed State**: Data in both legacy tables AND `unified_documents` (partial migration)
4. **Already v2.0**: Documents table exists with proper schema (no migration needed)
5. **Corrupted State**: Inconsistent data across multiple tables

---

## 🔧 **COMPREHENSIVE MIGRATION ALGORITHM:**

### **Phase 1: Database State Detection**

```sql
-- Detect database version and content location
CREATE TEMPORARY TABLE migration_analysis AS
SELECT 
    'discussions' as table_name,
    (SELECT COUNT(*) FROM discussions) as record_count,
    (SELECT name FROM sqlite_master WHERE type='table' AND name='discussions') as exists_check
UNION ALL
SELECT 'artifacts', (SELECT COUNT(*) FROM artifacts), 
       (SELECT name FROM sqlite_master WHERE type='table' AND name='artifacts')
UNION ALL  
SELECT 'plans', (SELECT COUNT(*) FROM plans),
       (SELECT name FROM sqlite_master WHERE type='table' AND name='plans')
UNION ALL
SELECT 'code_iterations', (SELECT COUNT(*) FROM code_iterations),
       (SELECT name FROM sqlite_master WHERE type='table' AND name='code_iterations')
UNION ALL
SELECT 'unified_documents', (SELECT COUNT(*) FROM unified_documents),
       (SELECT name FROM sqlite_master WHERE type='table' AND name='unified_documents')
UNION ALL
SELECT 'documents', (SELECT COUNT(*) FROM documents),
       (SELECT name FROM sqlite_master WHERE type='table' AND name='documents');
```

### **Phase 2: Migration Strategy Selection**

```python
def determine_migration_strategy(analysis_results):
    """
    Determine the appropriate migration strategy based on database state
    """
    legacy_tables = ['discussions', 'artifacts', 'plans', 'code_iterations']
    legacy_count = sum(analysis_results[table] for table in legacy_tables if table in analysis_results)
    unified_count = analysis_results.get('unified_documents', 0)
    documents_count = analysis_results.get('documents', 0)
    
    if documents_count > 0:
        # Check if documents table has proper v2.0 schema
        if has_proper_v2_schema():
            return "already_v2"
        else:
            return "documents_schema_upgrade"
    
    elif legacy_count > 0 and unified_count > 0:
        return "mixed_state_migration"
    
    elif legacy_count > 0:
        return "pre_v1_4_migration"
    
    elif unified_count > 0:
        return "v1_4_migration"
    
    else:
        return "fresh_database"
```

### **Phase 3: Multi-Source Migration Implementation**

#### **Strategy A: Pre-v1.4.0 Migration (Direct from Legacy Tables)**

```sql
-- Migrate discussions table
INSERT INTO documents (
    project_uuid, uuid, version, document_type, title, content,
    summary, tags, metadata, created_at, updated_at, status
)
SELECT 
    (SELECT uuid FROM projects LIMIT 1) as project_uuid,
    COALESCE(uuid, 'disc-' || id || '-' || substr(content, 1, 8)) as uuid,
    1 as version,
    'discussion' as document_type,
    title,
    content,
    summary,
    COALESCE(tags, '[]') as tags,
    json_object(
        'legacy', json_object(
            'source_table', 'discussions',
            'source_id', id,
            'migration_date', datetime('now'),
            'migration_type', 'pre_v1_4'
        )
    ) as metadata,
    created_at,
    updated_at,
    COALESCE(status, 'active') as status
FROM discussions;

-- Migrate artifacts table  
INSERT INTO documents (
    project_uuid, uuid, version, document_type, title, content,
    summary, tags, metadata, created_at, updated_at, status
)
SELECT 
    (SELECT uuid FROM projects LIMIT 1) as project_uuid,
    COALESCE(uuid, 'art-' || id || '-' || substr(content, 1, 8)) as uuid,
    1 as version,
    'artifact' as document_type,
    title,
    content,
    summary,
    COALESCE(tags, '[]') as tags,
    json_object(
        'legacy', json_object(
            'source_table', 'artifacts',
            'source_id', id,
            'migration_date', datetime('now'),
            'migration_type', 'pre_v1_4'
        )
    ) as metadata,
    created_at,
    updated_at,
    COALESCE(status, 'active') as status
FROM artifacts;

-- Migrate plans table
INSERT INTO documents (
    project_uuid, uuid, version, document_type, title, content,
    summary, tags, metadata, created_at, updated_at, status
)
SELECT 
    (SELECT uuid FROM projects LIMIT 1) as project_uuid,
    COALESCE(uuid, 'plan-' || id || '-' || substr(content, 1, 8)) as uuid,
    1 as version,
    'plan' as document_type,
    title,
    content,
    summary,
    COALESCE(tags, '[]') as tags,
    json_object(
        'legacy', json_object(
            'source_table', 'plans',
            'source_id', id,
            'migration_date', datetime('now'),
            'migration_type', 'pre_v1_4'
        )
    ) as metadata,
    created_at,
    updated_at,
    COALESCE(status, 'active') as status
FROM plans;

-- Migrate code_iterations table
INSERT INTO documents (
    project_uuid, uuid, version, document_type, title, content,
    summary, tags, metadata, created_at, updated_at, status
)
SELECT 
    (SELECT uuid FROM projects LIMIT 1) as project_uuid,
    COALESCE(uuid, 'code-' || id || '-' || substr(content, 1, 8)) as uuid,
    1 as version,
    'code_iteration' as document_type,
    title,
    content,
    summary,
    COALESCE(tags, '[]') as tags,
    json_object(
        'legacy', json_object(
            'source_table', 'code_iterations',
            'source_id', id,
            'migration_date', datetime('now'),
            'migration_type', 'pre_v1_4'
        )
    ) as metadata,
    created_at,
    updated_at,
    COALESCE(status, 'active') as status
FROM code_iterations;
```

#### **Strategy B: v1.4.0 Migration (From unified_documents)**

```sql
-- Migrate unified_documents (our current case)
INSERT INTO documents (
    project_uuid, uuid, version, document_type, title, content,
    summary, tags, metadata, created_at, updated_at, status
)
SELECT 
    (SELECT uuid FROM projects LIMIT 1) as project_uuid,
    original_uuid as uuid,
    1 as version,
    document_type,
    title,
    content,
    summary,
    tags,
    json_set(
        COALESCE(metadata, '{}'),
        '$.legacy', json_object(
            'source_table', source_table,
            'source_id', source_id,
            'original_uuid', original_uuid,
            'migration_date', datetime('now'),
            'migration_type', 'v1_4'
        )
    ) as metadata,
    created_at,
    updated_at,
    status
FROM unified_documents;
```

#### **Strategy C: Mixed State Migration (Both Sources)**

```python
def mixed_state_migration():
    """
    Handle databases with both legacy tables and unified_documents
    Prioritize unified_documents, use legacy tables for missing content
    """
    
    # 1. Get all UUIDs from unified_documents
    unified_uuids = get_unified_document_uuids()
    
    # 2. Migrate unified_documents first (Strategy B)
    migrate_unified_documents()
    
    # 3. For each legacy table, migrate only records NOT in unified_documents
    for table in ['discussions', 'artifacts', 'plans', 'code_iterations']:
        migrate_legacy_table_excluding_unified(table, unified_uuids)
```

### **Phase 4: Duplicate Detection & Resolution**

```sql
-- Detect potential duplicates across migration sources
CREATE TEMPORARY TABLE duplicate_analysis AS
SELECT 
    project_uuid, uuid, COUNT(*) as version_count,
    GROUP_CONCAT(DISTINCT json_extract(metadata, '$.legacy.migration_type')) as migration_types
FROM documents 
GROUP BY project_uuid, uuid
HAVING COUNT(*) > 1;

-- Strategy for handling duplicates:
-- 1. Keep unified_documents version (higher quality)
-- 2. Merge metadata from multiple sources
-- 3. Preserve all legacy references
```

### **Phase 5: Post-Migration Validation**

```sql
-- Validation queries
SELECT 
    'Total documents migrated' as metric,
    COUNT(*) as value
FROM documents

UNION ALL

SELECT 
    'Migration sources',
    COUNT(DISTINCT json_extract(metadata, '$.legacy.migration_type'))
FROM documents

UNION ALL

SELECT 
    'Projects with data',
    COUNT(DISTINCT project_uuid)
FROM documents;
```

---

## 🎯 **CURRENT DATABASE MIGRATION PLAN:**

### **For Our Specific Case (Pure v1.4.0):**

```sql
-- 1. Create proper v2.0 documents table
CREATE TABLE documents_new (
    project_uuid TEXT NOT NULL,
    uuid TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    document_type TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    tags TEXT DEFAULT '[]',
    metadata TEXT DEFAULT '{}',
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    created_by TEXT,
    status TEXT DEFAULT 'active',
    PRIMARY KEY (project_uuid, uuid, version),
    FOREIGN KEY (project_uuid) REFERENCES projects(uuid)
);

-- 2. Migrate 187 records from unified_documents
INSERT INTO documents_new (
    project_uuid, uuid, version, document_type, title, content,
    summary, tags, metadata, created_at, updated_at, status
)
SELECT 
    'fa3a666f-286e-4210-b24b-f22f6229a48a' as project_uuid,
    original_uuid as uuid,
    1 as version,
    document_type, title, content, summary, tags,
    json_set(
        COALESCE(metadata, '{}'),
        '$.legacy', json_object(
            'source_table', source_table,
            'source_id', source_id,
            'original_uuid', original_uuid,
            'migration_date', datetime('now'),
            'migration_type', 'v1_4'
        )
    ) as metadata,
    created_at, updated_at, status
FROM unified_documents;

-- 3. Replace old table
DROP TABLE documents;
ALTER TABLE documents_new RENAME TO documents;

-- 4. Clean up legacy tables (all empty)
DROP TABLE discussions;
DROP TABLE artifacts;
DROP TABLE plans;
DROP TABLE code_iterations;
DROP TABLE unified_documents;
-- + all associated FTS tables
```

---

## 🚀 **BENEFITS OF COMPREHENSIVE MIGRATION:**

### **✅ Handles All Database States:**
- **Pre-v1.4.0**: Direct legacy table migration
- **v1.4.0**: Unified documents migration  
- **Mixed**: Intelligent conflict resolution
- **v2.0**: Schema validation and updates

### **✅ Data Preservation:**
- **No Data Loss**: All content preserved regardless of source
- **Legacy Tracking**: Complete audit trail in metadata
- **Conflict Resolution**: Handles duplicates and inconsistencies
- **UUID Generation**: Safe UUID handling for missing values

### **✅ Future-Proof:**
- **Version Detection**: Automatic database version identification
- **Incremental Updates**: Can handle partial migrations
- **Rollback Support**: Migration metadata enables rollback
- **Cross-Project Ready**: Supports three-project architecture

**This comprehensive migration strategy ensures we can handle any Memory Bank database state and safely upgrade to v2.0!** 🎯✨
