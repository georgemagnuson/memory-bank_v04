# Memory Bank Schema Template Locations and Management

**Generated:** 2025-07-30.1337  
**Purpose:** Comprehensive guide to schema template locations and version management

## 📍 **Schema Template Files**

### ✅ **v2.0 Templates (Current - uuid + project_uuid)**
1. **`/server/memory_bank_mcp/schema_v2_0_template.sql`**
   - **Purpose**: Main v2.0 schema template for new database creation
   - **Status**: ✅ Updated with `uuid` and `project_uuid` fields
   - **Usage**: Used by database creation and migration tools

2. **`/server/memory_bank_mcp/schema_manager_modules/schema_template_manager.py`**
   - **Purpose**: Programmatic schema template management
   - **Status**: ✅ Updated with correct v2.0 schema
   - **Usage**: Used by MCP server for dynamic schema operations

3. **`/server/memory_bank_mcp/migration_modules/database_migrator.py`**
   - **Purpose**: Fallback schema for migration operations
   - **Status**: ✅ Updated with correct v2.0 schema
   - **Usage**: Used when schema template file is not found

### 📚 **v1.4.0 Templates (Historical - original_uuid)**
1. **`/server/memory_bank_mcp/schema_v1_4_0_template.sql`**
   - **Purpose**: Historical record and version detection
   - **Status**: ✅ Created from v1.4.0 backup analysis
   - **Usage**: Schema comparison, database version detection, migration validation

2. **`/memory-bank/context.db`** (Live v1.4.0 database)
   - **Purpose**: Active v1.4.0 database with unified_documents schema
   - **Records**: 187 unified_documents
   - **Status**: Original v1.4.0 template database

3. **`/memory-bank/test_development_context.db`** (v1.4.0 template)
   - **Purpose**: Development template database
   - **Status**: Clean v1.4.0 schema for testing

4. **`/server/memory_bank_mcp/memory-bank/context_backup_v1.4.0_*.db`**
   - **Purpose**: Migration backup databases
   - **Records**: 191 unified_documents (pre-migration state)
   - **Usage**: Migration verification and rollback

## 🔧 **Schema Management Tools**

### **Schema Version Detector**
- **File**: `/server/memory_bank_mcp/schema_version_detector.py`
- **Purpose**: Detect database schema versions and compare with templates
- **Usage**: `python3 schema_version_detector.py <database_path>`
- **Features**:
  - Automatic version detection (v1.4.0, v2.0, legacy, unknown)
  - Template comparison and migration recommendations
  - Cross-project support detection
  - Record count analysis

### **Migration Tools**
- **File**: `/migrate_v1_4_to_v2_0.py`
- **Purpose**: Migrate v1.4.0 → v2.0 with backup and verification
- **Usage**: `python3 migrate_v1_4_to_v2_0.py`
- **Features**:
  - Automatic backup creation
  - Dry-run analysis
  - Field mapping: `original_uuid` → `uuid`
  - Cross-project support: Add `project_uuid`

## 📊 **Raw SQL Verification Results**

### **Migration Data Integrity Confirmed:**
```sql
-- v1.4.0 unified_documents: 191 records
SELECT original_uuid, document_type FROM unified_documents LIMIT 3;
-- Results: plan-migration-unified-docs|plan, plan-sqlite-fts-tmp-extraction|plan, ...

-- v2.0 documents: 191 records (same data, new schema)
SELECT uuid, project_uuid, document_type FROM documents LIMIT 3;
-- Results: plan-migration-unified-docs|fe494766-f538-4d48-ac17-f1fb4e83c984|plan, ...
```

### **Document Type Distribution (Identical):**
- 44 notes, 43 plans, 30 documents, 24 code, 24 markdown, 20 discussions
- 2 decisions, 1 each: analysis, critical_technique, project_management, template

## ⚠️ **Code Consistency Issues Identified**

### **Files Still Using `original_uuid` (Need Updates):**
- `/server/memory_bank_mcp/content_tools.py`
- `/server/memory_bank_mcp/unified/search.py`
- `/server/memory_bank_mcp/core_tools.py`
- Multiple other files with mixed field references

### **Next Steps Required:**
1. **Update all SQL queries** from `original_uuid` → `uuid`
2. **Add `project_uuid` support** to cross-project queries
3. **Test MCP server** against v2.0 database
4. **Verify all functionality** works with new schema

## 🎯 **Template Usage Guidelines**

### **For Database Creation:**
- Use `/server/memory_bank_mcp/schema_v2_0_template.sql` for new v2.0 databases
- Use `/memory-bank/test_development_context.db` as v1.4.0 reference

### **For Version Detection:**
- Use `schema_version_detector.py` to identify database versions
- Compare against both v1.4.0 and v2.0 templates

### **For Migration:**
- Use `migrate_v1_4_to_v2_0.py` for automated v1.4.0 → v2.0 migration
- Verify using SQL queries against template databases

This comprehensive template management ensures proper version control, migration safety, and database compatibility across the three-project ecosystem (MBSW, memory-bank_v04, SPEC-WORKFLOW).
