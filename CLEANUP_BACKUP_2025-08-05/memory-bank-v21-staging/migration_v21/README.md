# Memory Bank v2.1 Migration System

**Complete migration system for upgrading any Memory Bank database to clean v2.1 schema.**

## 🎯 **What This Solves**

Your Memory Bank database has **48 tables with 277 records** spread across legacy tables. This system:

- ✅ **Consolidates ALL content tables** → single `documents` table
- ✅ **Reduces 48 tables** → ~18 clean v2.1 tables  
- ✅ **Preserves all 277 records** with proper document types
- ✅ **Removes legacy bloat** for better performance
- ✅ **Future-proofs** your database architecture

## 📊 **Your Database Analysis**

```
Current State:  48 tables, v2.0 with legacy tables
Content:        187 unified_documents + 90 chat_sessions  
Migration Type: v2_to_v2.1
Target:         ~18 tables, clean v2.1 schema
```

---

## 🚀 **Quick Start**

### **Option 1: Command Line (Recommended)**

```bash
# Analyze your database
python -m migration_v21.cli analyze "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp/memory-bank/context.db"

# Dry run to see what would happen
python -m migration_v21.cli migrate "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp/memory-bank/context.db" --dry-run

# Perform the migration
python -m migration_v21.cli migrate "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp/memory-bank/context.db"
```

### **Option 2: Python API**

```python
from migration_v21 import MigrationManager

manager = MigrationManager()

# Analyze database
report = manager.analyze_database("/path/to/context.db")
print(report)

# Perform migration
result = manager.migrate_to_v21("/path/to/context.db")
if result['success']:
    print(f"✅ Migration complete! {result['records_migrated']} records migrated")
```

### **Option 3: Enhanced work_on_project**

```python
from migration_v21 import MigrationManager

manager = MigrationManager()
result = manager.work_on_project("/path/to/project")

# Automatically handles:
# - New database creation (v2.1)
# - Existing database migration (v2.0 → v2.1)
# - Current database opening (v2.1)
```

---

## 📋 **Migration Details**

### **Content Table Consolidation**
All content tables migrate to `documents` with proper `document_type`:

| Source Table | → | Document Type | Your Records |
|--------------|---|---------------|--------------|
| `unified_documents` | → | `document` | 187 records |
| `chat_sessions` | → | `chat_session` | 90 records |
| `discussions` | → | `discussion` | (if any) |
| `artifacts` | → | `artifact` | (if any) |
| `plans` | → | `plan` | (if any) |
| `decisions` | → | `decision` | (if any) |

### **Legacy Table Cleanup**
Removes ~30 legacy tables including:
- All FTS tables for deprecated content types
- All `*_fts_config`, `*_fts_data`, `*_fts_idx` tables
- Deprecated content tables after migration

### **Final v2.1 Schema**
Clean architecture with ~18 tables:
- **Core**: `projects`, `documents`, `markdown_files`, `semantic_equivalents`, `cross_references`, `project_context`
- **Search**: `documents_fts`, `markdown_search` + associated FTS5 tables
- **System**: `sqlite_sequence` and other SQLite system tables

---

## 🛡️ **Safety Features**

1. **Automatic Backup**: Creates timestamped backup before migration
2. **Dry Run Mode**: Test migration without making changes
3. **Rollback Capability**: Restore from backup if needed
4. **Validation**: Verifies migration success
5. **Atomic Operations**: All-or-nothing transaction safety

---

## 🔧 **Module Structure**

```
migration_v21/
├── __init__.py              # Main exports
├── version_detector.py      # Table count-based version detection
├── content_migrator.py      # Content table migration logic
├── schema_creator.py        # Clean v2.1 database creation
├── migration_manager.py     # Main orchestrator
├── integration.py           # Memory Bank integration helpers
└── cli.py                   # Command-line interface
```

### **Key Classes:**

- **`MigrationManager`**: Main interface for all operations
- **`VersionDetector`**: Enhanced version detection using table count
- **`ContentMigrator`**: Handles migration of all content tables
- **`SchemaCreator`**: Creates clean v2.1 databases

---

## 📖 **Usage Examples**

### **Analyze Before Migration**
```python
from migration_v21 import MigrationManager

manager = MigrationManager()
analysis = manager.analyze_database("/path/to/context.db")
print(analysis)
```

Output:
```
🔍 Database Version Analysis
📊 Table Count: 48
🏷️ Version: v2.0
📋 Schema Analysis:
• Documents table: ✅ Present
• Legacy tables: ⚠️ 30 present
📈 Content Analysis:
• unified_documents: 187 records → documents (type='document')
• chat_sessions: 90 records → documents (type='chat_session')
🔄 Migration Required: v2_to_v2.1
```

### **Complete Migration**
```python
# Perform migration
result = manager.migrate_to_v21("/path/to/context.db")

if result['success']:
    print(f"✅ Migration complete!")
    print(f"Records migrated: {result['records_migrated']}")
    print(f"Tables: {result['tables_before']} → {result['tables_after']}")
    print(f"Backup: {result['backup_path']}")
```

### **Enhanced Project Management**
```python
# Use enhanced work_on_project that handles migration automatically
result = manager.work_on_project("/path/to/project")

if result['success']:
    if result['action'] == 'migrated_to_v21':
        print("✅ Project opened and migrated to v2.1!")
    elif result['action'] == 'created_new_database':
        print("✅ New v2.1 project created!")
    else:
        print("✅ Current v2.1 project opened!")
```

---

## 🔗 **Integration with Existing Memory Bank**

### **Patch Existing Systems**
```python
from migration_v21 import integrate_with_memory_bank

# Monkey patch existing Memory Bank systems
results = integrate_with_memory_bank()

# Now existing tools have v2.1 migration support:
# - schema_manager.migrate_to_v21()
# - enhanced work_on_project with auto-migration
```

### **MCP Server Integration**
Add to your Memory Bank MCP server:

```python
from migration_v21.integration import MemoryBankIntegration

integration = MemoryBankIntegration()
mcp_tools = integration.create_mcp_tool_integration()

# Add tools to your MCP server
@server.tool()
async def migrate_to_v21(confirm: bool = False) -> str:
    return await mcp_tools['migrate_to_v21'](confirm)

@server.tool() 
async def analyze_database_v21() -> str:
    return await mcp_tools['analyze_database_v21']()
```

---

## ⚡ **Performance Benefits**

**Before Migration (v2.0 with legacy):**
- 48 tables to maintain
- Multiple FTS systems
- Fragmented content across tables
- Legacy indexes and constraints

**After Migration (v2.1 clean):**
- ~18 optimized tables
- Single FTS5 system
- Unified content in documents table
- Clean, modern indexes

**Expected improvements:**
- 🚀 **Faster queries** (unified content)
- 🔍 **Better search** (single FTS5 system)
- 💾 **Smaller database** (removed redundancy)
- 🛠️ **Easier maintenance** (clean schema)

---

## 🎯 **Migration Validation**

After migration, validate with:

```bash
python -m migration_v21.cli validate "/path/to/context.db"
```

Expected output:
```
✅ Database validation passed
Version: 21 (expected: 21)
Tables: 18 (expected: ~18)
```

---

## 🆘 **Troubleshooting**

### **Migration Fails**
- ✅ **Backup preserved** - your data is safe
- ✅ **Database restored** to original state automatically
- ✅ **Check logs** for specific error details

### **Partial Migration**
- Use `--dry-run` first to identify issues
- Check file permissions on database
- Ensure database isn't locked by other processes

### **Integration Issues**
- Some Memory Bank components may need manual integration
- Use direct API calls as fallback
- Check import paths for your specific setup

---

## 📈 **What's Next**

After successful migration to v2.1:

1. **✅ All content preserved** in documents table with proper types
2. **🔍 Enhanced search** with unified FTS5 system
3. **🚀 Better performance** with optimized schema
4. **🔮 Future-ready** for next-generation Memory Bank features

Your Memory Bank is now running the latest v2.1 architecture! 🎉

---

## 📞 **Support**

- **Issues**: Check logs and use `--dry-run` mode first
- **Questions**: Review this README and module documentation
- **Integration**: Use the provided integration helpers

The migration system is designed to be safe, reliable, and preserve all your valuable Memory Bank content while modernizing the underlying architecture.
