# Memory Bank v2.0 Proper Schema Design & Migration Plan

**Generated:** 2025-08-02.2030  
**Status:** 🎯 PROPER v2.0 SCHEMA DESIGN BASED ON THREE-PROJECT ARCHITECTURE

---

## 🏗️ **CORRECTED v2.0 ARCHITECTURE UNDERSTANDING:**

### **✅ Three-Project Ecosystem (from documentation):**

1. **MBSW (memory-bank-spec-workflow)** - COORDINATOR HUB
   - **Role**: Coordination hub with knowledge of multiple project UUIDs
   - **Projects Table**: Contains multiple project UUIDs for coordination
   - **Metadata**: Stores cross-project relationships and coordination info

2. **memory-bank_v04** - FOUNDATION LAYER (Current Project)
   - **Role**: Foundation layer with single project context
   - **Projects Table**: Should have ONE entry for current project
   - **Project UUID**: `fa3a666f-286e-4210-b24b-f22f6229a48a`

3. **SPEC-WORKFLOW** - METHODOLOGY LAYER
   - **Role**: Methodology layer with own project context
   - **Projects Table**: Will have its own single project entry

### **✅ Current Projects Table State (Fixed):**
- **Single Entry**: `memory_bank_mcp` (`fa3a666f-286e-4210-b24b-f22f6229a48a`)
- **Path**: `/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp`
- **Architecture**: Correctly follows single-project-per-database model

---

## 📋 **PROPER v2.0 DOCUMENTS TABLE DESIGN:**

### **✅ Corrected Schema with Composite Primary Key:**

```sql
CREATE TABLE documents (
    project_uuid TEXT NOT NULL,          -- Links to projects.uuid
    uuid TEXT NOT NULL,                  -- Document UUID within project  
    version INTEGER NOT NULL DEFAULT 1,  -- Document version for revision history
    document_type TEXT NOT NULL,         -- Type: 'discussion', 'artifact', 'plan', 'code', 'note'
    title TEXT,                          -- Document title
    content TEXT NOT NULL,               -- Main document content
    summary TEXT,                        -- Optional summary/description
    tags TEXT DEFAULT '[]',              -- JSON array of tags
    metadata TEXT DEFAULT '{}',          -- JSON metadata including legacy fields
    created_at TIMESTAMP,               -- Original creation time
    updated_at TIMESTAMP,               -- Last modification time
    created_by TEXT,                     -- Author/creator identifier
    status TEXT DEFAULT 'active',       -- 'active', 'archived', 'deleted'
    
    PRIMARY KEY (project_uuid, uuid, version),
    FOREIGN KEY (project_uuid) REFERENCES projects(uuid)
);
```

### **🔧 Key Design Features:**

#### **1. Composite Primary Key Benefits:**
- **Multi-Project Support**: Each project isolated by `project_uuid`
- **Document Versioning**: Multiple versions of same document supported
- **Cross-Project References**: Can reference documents in other projects via full key
- **Example Keys**: 
  - `(fa3a666f..., doc-123, 1)` - Version 1 of document
  - `(fa3a666f..., doc-123, 2)` - Version 2 of same document

#### **2. Versioning System:**
- **Revision History**: Keep all versions of documents as they evolve
- **Latest Version**: Query `MAX(version)` to get current version
- **Rollback**: Can revert to any previous version
- **Audit Trail**: Complete history of document changes

#### **3. Legacy Data in Metadata:**
```json
{
  "legacy": {
    "source_table": "discussions",
    "source_id": 42,
    "original_uuid": "legacy-uuid-here",
    "migration_date": "2025-08-02T20:30:00Z"
  },
  "spec_workflow": {
    "spec_name": "user-auth-system",
    "spec_phase": "requirements",
    "spec_status": "draft"
  },
  "cross_references": [
    {
      "project_uuid": "other-project-uuid",
      "document_uuid": "related-doc-uuid", 
      "relationship": "depends_on"
    }
  ]
}
```

---

## 🔄 **MIGRATION STRATEGY:**

### **Phase 1: Schema Recreation**
```sql
-- Drop current documents table (empty anyway)
DROP TABLE documents;
DROP TABLE documents_fts;

-- Create proper v2.0 documents table
CREATE TABLE documents (
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

-- Create FTS virtual table
CREATE VIRTUAL TABLE documents_fts USING fts5(
    content, title, summary, tags,
    content='documents',
    content_rowid='rowid'
);
```

### **Phase 2: Data Migration (187 Records)**
```sql
INSERT INTO documents (
    project_uuid, 
    uuid, 
    version,
    document_type,
    title, 
    content,
    summary,
    tags,
    metadata,
    created_at,
    updated_at,
    status
)
SELECT 
    'fa3a666f-286e-4210-b24b-f22f6229a48a' as project_uuid,
    original_uuid as uuid,
    1 as version,
    document_type,
    title,
    content,
    summary,
    tags,
    json_set(
        COALESCE(metadata, '{}'),
        '$.legacy.source_table', source_table,
        '$.legacy.source_id', source_id,
        '$.legacy.original_uuid', original_uuid,
        '$.legacy.migration_date', datetime('now')
    ) as metadata,
    created_at,
    updated_at,
    status
FROM unified_documents;
```

### **Phase 3: Legacy Table Cleanup**
```sql
-- Drop all legacy tables (confirmed empty except unified_documents)
DROP TABLE discussions;
DROP TABLE discussions_fts;
DROP TABLE discussions_fts_config;
DROP TABLE discussions_fts_data;
DROP TABLE discussions_fts_docsize;
DROP TABLE discussions_fts_idx;

DROP TABLE artifacts;
DROP TABLE artifacts_fts;
DROP TABLE artifacts_fts_config;
DROP TABLE artifacts_fts_data;
DROP TABLE artifacts_fts_docsize;
DROP TABLE artifacts_fts_idx;

DROP TABLE plans;
DROP TABLE plans_fts;
DROP TABLE plans_fts_config;
DROP TABLE plans_fts_data;
DROP TABLE plans_fts_docsize;
DROP TABLE plans_fts_idx;

DROP TABLE code_iterations;
DROP TABLE code_iterations_fts;
DROP TABLE code_iterations_fts_config;
DROP TABLE code_iterations_fts_data;
DROP TABLE code_iterations_fts_docsize;
DROP TABLE code_iterations_fts_idx;

-- Finally drop unified_documents after successful migration
DROP TABLE unified_documents;
DROP TABLE unified_documents_fts;
DROP TABLE unified_documents_fts_config;
DROP TABLE unified_documents_fts_data;
DROP TABLE unified_documents_fts_docsize;
DROP TABLE unified_documents_fts_idx;
```

---

## 🎯 **EXPECTED RESULTS:**

### **After Migration:**
- **Documents Table**: 187 records with proper v2.0 schema
- **Primary Key**: `(fa3a666f-286e-4210-b24b-f22f6229a48a, uuid, 1)`
- **Versioning Ready**: All documents at version 1, ready for future revisions
- **Legacy Preserved**: All `source_table`/`source_id` data preserved in metadata
- **Clean Schema**: Only essential v2.0 tables remain

### **Table Count Reduction:**
- **Before**: 48 tables (includes legacy tables and FTS)
- **After**: ~18 tables (clean v2.0 schema without legacy)

### **Cross-Project Capability:**
- **Current Project**: All documents have `project_uuid` = `fa3a666f...`
- **Future Coordination**: MBSW can reference this project's documents
- **Cross-References**: Can link to documents in other coordinating projects

---

## 🚀 **IMPLEMENTATION DECISION:**

**Should we proceed with this proper v2.0 schema migration?**

**Benefits:**
- ✅ Proper composite primary key design
- ✅ Document versioning system
- ✅ Clean legacy data handling  
- ✅ Cross-project coordination ready
- ✅ Follows three-project architecture

**Current State:**
- ✅ Projects table cleaned (single entry)
- ✅ 187 records ready for migration
- ✅ Legacy tables confirmed empty (safe to drop)
- ✅ Context propagation working (registry system)

**The foundation is ready for proper v2.0 schema implementation!** 🎯✨
