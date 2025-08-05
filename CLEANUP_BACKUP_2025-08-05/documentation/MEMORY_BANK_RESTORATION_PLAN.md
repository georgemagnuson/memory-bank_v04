# Memory Bank v1.4.0 Tool Restoration Plan
**Filename:** MEMORY_BANK_RESTORATION_PLAN.md  
**Generated:** 2025-07-26.1516  
**Purpose:** Comprehensive plan to restore 27+ missing tools through modular architecture

## Crisis Summary

**Current State:** Memory Bank MCP has only **4 active tools** (should have 31+)
**Root Cause:** Syntax fix removed 27+ essential tools to resolve IndentationError
**Impact:** Severely limited functionality, missing core features
**Solution:** Systematic modular restoration with improved architecture

---

## Tool Inventory Analysis

### ✅ **PRESERVED TOOLS (4/31)**
1. `get_memory_bank_status` - Basic status reporting
2. `work_on_project` - Project initialization  
3. `memory_bank_sql_query` - SQL execution with truncation
4. `memory_bank_help` - Minimal help system

### ❌ **MISSING CRITICAL TOOLS (27+)**

#### **Phase 1: Core System Tools (Priority 1)**
- `get_memory_bank_system_info` - System diagnostics & metadata
- `memory_bank_describe_schema` - Database schema exploration  
- `memory_bank_table_info` - Individual table details
- `memory_bank_list_tables` - Database table listing
- `extract_large_document` - Bypass SQL truncation for large content
- `verify_and_repair_schema` - Database integrity management

#### **Phase 2: Project Management (Priority 1)**  
- `log_decision` - Decision tracking system
- `query_decisions` - Decision search & retrieval
- `generate_enhanced_session_starter` - Session context generation
- `prepare_context_switch` - Safe project switching prep
- `check_context_switch_safety` - Context switch validation
- `force_context_flush` - Emergency context management

#### **Phase 3: Content Discovery (Priority 2)**
- `search_all_content` - Universal FTS across all tables
- `import_markdown_files` - Markdown content import
- `sync_fts_tables` - Full-text search index maintenance  
- `discover_and_import_all_markdown` - Bulk content discovery
- `import_project_documentation` - Project documentation import
- `generate_markdown_import_report` - Import status reporting

#### **Phase 4: Migration & Legacy (Priority 2)**
- `migrate_project_md_files` - Legacy markdown migration
- `analyze_migration_candidates` - Migration planning & analysis
- `migrate_specific_project` - Targeted project migration

#### **Phase 5: Backup & Templates (Priority 3)**
- `backup_context_db` - Database backup management
- `list_backups` - Backup inventory & metadata
- `store_template_spec` - Template specification storage
- `discover_templates` - Template discovery & search
- `phase1_completion_status` - Phase 1 feature status

#### **Phase 6: Advanced Features (Priority 3)**
- `resume_project` - Enhanced project resumption
- `continue_project` - Session continuation management
- `switch_to_project` - Alternative project switching

---

## Modular Architecture Plan

### **Module 1: `core_tools.py` (Priority 1)**
**Purpose:** Essential system operations  
**Functions:** 6 tools
- `get_memory_bank_system_info()`
- `memory_bank_describe_schema()`  
- `memory_bank_table_info(table_name)`
- `memory_bank_list_tables()`
- `extract_large_document(title_search, output_dir)`
- `verify_and_repair_schema()`

### **Module 2: `project_tools.py` (Priority 1)**
**Purpose:** Project & session management  
**Functions:** 6 tools
- `log_decision(summary, rationale, tags)`
- `query_decisions(search_term, limit)`
- `generate_enhanced_session_starter(session_goal, session_type)`
- `prepare_context_switch()`
- `check_context_switch_safety()`
- `force_context_flush()`

### **Module 3: `content_tools.py` (Priority 2)**
**Purpose:** Content discovery & import  
**Functions:** 6 tools
- `search_all_content(query, limit, content_types)`
- `import_markdown_files(directory_path, file_pattern, recursive)`
- `sync_fts_tables()`
- `discover_and_import_all_markdown(directory_path, exclude_patterns, max_file_size_mb)`
- `import_project_documentation(include_external)`
- `generate_markdown_import_report()`

### **Module 4: `migration_tools.py` (Priority 2)**
**Purpose:** Legacy migration & project conversion  
**Functions:** 3 tools
- `migrate_project_md_files(project_path, dry_run)`
- `analyze_migration_candidates()`
- `migrate_specific_project(project_name, dry_run, auto_import_md)`

### **Module 5: `backup_tools.py` (Priority 3)**
**Purpose:** Backup & template management  
**Functions:** 5 tools
- `backup_context_db(backup_type, force, verify)`
- `list_backups(backup_type, include_metadata, verify_integrity)`
- `store_template_spec(...)`
- `discover_templates(...)`
- `phase1_completion_status()`

### **Module 6: `advanced_tools.py` (Priority 3)**
**Purpose:** Advanced session & project features  
**Functions:** 3 tools
- `resume_project(project_path, load_depth)`
- `continue_project(session_id)`
- `switch_to_project(project_path)`

### **Updated `main.py` (Core Orchestration)**
**Purpose:** FastMCP setup, tool registration, global state  
**Functions:** 4 tools (existing)
- `work_on_project()` - Central project initialization
- `get_memory_bank_status()` - Status reporting
- `memory_bank_sql_query()` - SQL execution
- `memory_bank_help()` - Enhanced help system

---

## Implementation Strategy

### **Phase 1: Foundation (Days 1-2)**
1. **Extract Core Tools** → `core_tools.py`
2. **Extract Project Tools** → `project_tools.py`  
3. **Test essential functionality**
4. **Update main.py imports & registration**

### **Phase 2: Content Management (Days 3-4)**
1. **Create** → `content_tools.py`
2. **Implement FTS and import tools**
3. **Test content discovery workflows**

### **Phase 3: Migration Support (Day 5)**
1. **Create** → `migration_tools.py`
2. **Implement legacy migration tools**
3. **Test with existing projects**

### **Phase 4: Advanced Features (Day 6)**
1. **Create** → `backup_tools.py` + `advanced_tools.py`
2. **Implement remaining tools**
3. **Full system integration testing**

### **Phase 5: Documentation & Polish (Day 7)**
1. **Enhanced help system**
2. **Updated documentation**
3. **Final DXT rebuild and testing**

---

## Implementation Guidelines

### **Code Organization Principles**
- **Each module ≤ 150 lines** (easy to edit)
- **Clear separation of concerns**
- **Consistent error handling patterns**
- **Comprehensive logging**
- **Type hints throughout**

### **Testing Strategy**
- **Progressive testing** after each module
- **Integration tests** for cross-module functionality
- **Backup & restore validation**
- **Performance regression testing**

### **Quality Assurance**
- **Syntax validation** before each commit
- **Import dependency checking**
- **Tool registration verification**
- **DXT rebuild testing**

---

## Risk Mitigation

### **Backup Strategy**
- **Preserve working main.py** before changes
- **Incremental backups** during development  
- **Rollback plan** for each phase

### **Minimal Disruption**
- **Keep current 4 tools working** throughout process
- **Add tools incrementally** without breaking existing
- **Test each module independently**

### **Validation Checkpoints**
- **Tool count verification** after each phase
- **Functionality testing** with real projects
- **Performance monitoring** throughout

---

## Success Criteria

### **Completion Metrics**
- ✅ **31+ tools active** (vs current 4)
- ✅ **All modules ≤ 150 lines** each
- ✅ **Zero syntax errors**
- ✅ **DXT builds successfully**
- ✅ **Full test suite passes**

### **Quality Metrics**
- ✅ **Improved maintainability** (modular structure)
- ✅ **Enhanced reliability** (better error handling)
- ✅ **Better developer experience** (easier to edit)
- ✅ **Complete functionality** (all v1.4.0 features)

---

## Next Steps

1. **Begin Phase 1** - Extract `core_tools.py`
2. **Create tool registration system** in main.py  
3. **Test fundamental operations**
4. **Proceed through phases systematically**

**Target Completion:** 7 days  
**Priority:** HIGH - System currently severely limited
**Dependencies:** None - can begin immediately
