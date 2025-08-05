# Memory Bank MCP v1.4.0 - Installation Guide
**Enhanced AI Collaboration Memory System**  
**Generated:** 2025-07-27.2350

---

## 📋 **System Requirements**

- **Python:** 3.8 or higher
- **Operating System:** macOS, Linux, or Windows
- **MCP Client:** Claude Desktop or compatible MCP client
- **Git:** For repository management (optional)

---

## 🚀 **Installation Instructions**

### **Option 1: Install from Requirements (Recommended)**

This is the standard installation method that ensures you have the latest compatible dependencies:

```bash
# Clone the repository
git clone <repository-url>
cd memory-bank_v04

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

### **Option 2: DXT Package Installation**

If you prefer using the pre-built DXT package:

1. Download `memory-bank-v04-enhanced-v1.4.0.dxt`
2. Install via your MCP client's package manager
3. Dependencies will be automatically handled

### **Option 3: Manual Dependency Installation**

For custom environments or troubleshooting:

```bash
# Core dependencies
pip install mcp>=1.12.0 aiosqlite>=0.21.0
pip install pydantic>=2.11.7 httpx>=0.28.1
pip install uvicorn>=0.35.0 starlette>=0.47.2

# See requirements.txt for complete list
```

---

## ⚙️ **Configuration**

### **Claude Desktop Integration**

Add to your Claude Desktop MCP configuration:

```json
{
  "memory-bank-v04": {
    "command": "python",
    "args": ["-m", "memory_bank_mcp"],
    "env": {
      "MEMORY_BANK_PROJECT_PATH": "/path/to/your/projects"
    }
  }
}
```

### **Environment Variables**

- `MEMORY_BANK_PROJECT_PATH`: Default project directory (optional)
- `MEMORY_BANK_LOG_LEVEL`: Logging level (default: INFO)

---

## 📁 **Directory Structure**

After installation, your project will contain:

```
memory-bank_v04/
├── README.md                                    # Project overview
├── INSTALLATION_GUIDE_v1.4.0.md               # This file
├── requirements.txt                            # Python dependencies
├── setup.py                                   # Package configuration
├── memory-bank-v04-enhanced-v1.4.0.dxt       # DXT package
├── manifest.json                              # MCP manifest
├── server/                                    # Core server code
│   ├── main.py                               # Entry point
│   └── memory_bank_mcp/                      # MCP implementation
├── memory-bank/                              # Database storage
│   └── context.db                           # SQLite database
├── documentation/                            # Historical docs
└── archive/                                 # Old versions & dev files
```

**Note:** The `lib/` directory is excluded from git and should be ignored. Dependencies are managed via `requirements.txt`.

---

## 🛠 **v1.4.0 Enhanced Tool Suite**

Memory Bank MCP v1.4.0 provides 30 specialized tools organized into 6 categories:

### **Core Database Tools (6)**
### **Core Database Tools (6)**
- `memory_bank_sql_query()` - Smart SQL with context-aware truncation
- `extract_large_document()` - Full document extraction for large content
- `memory_bank_describe_schema()` - Complete database schema overview
- `memory_bank_table_info()` - Detailed table structure and relationships
- `memory_bank_list_tables()` - All tables with record counts
- `verify_and_repair_schema()` - Schema verification and repair

### **Project Management Tools (6)**
- `log_decision()` - Track architectural and implementation decisions
- `query_decisions()` - Search and retrieve logged decisions
- `generate_enhanced_session_starter()` - Context-aware session preparation
- `prepare_context_switch()` - Safe project switching preparation
- `check_context_switch_safety()` - Validate context switch readiness
- `force_context_flush()` - Emergency context management

### **Content & Search Tools (6)**
- `search_all_content()` - Universal full-text search with prioritization
- `import_markdown_files()` - Import external documentation for search
- `sync_fts_tables()` - Maintain full-text search indexes
- `discover_and_import_all_markdown()` - Bulk intelligent content import
- `import_project_documentation()` - Auto-discover and import project docs
- `generate_markdown_import_report()` - Comprehensive import reporting

### **Migration Tools (3)**
- `migrate_project_md_files()` - Convert legacy .md files to database
- `analyze_migration_candidates()` - Discover projects ready for migration
- `migrate_specific_project()` - Targeted migration with FTS integration

### **Backup & Template Tools (4)**
- `backup_context_db()` - Create verified database backups
- `list_backups()` - Inventory all available backups
- `store_template_spec()` - Store template specifications for workflows
- `discover_templates()` - Find templates with full-text search

### **Help & Guidance Tools (1)**
- `sql_truncation_help()` - Enhanced SQL help and truncation guidance

---

## 🚀 **Quick Start Workflow**

### **1. Initialize Your First Project**
```
work_on_project("/Users/yourname/Documents/Projects/my_project")
# Auto-creates project structure and initializes Memory Bank
```

### **2. Explore Available Tools**
```
memory_bank_help()
# Shows comprehensive guide to all 30 tools
```

### **3. Log Important Decisions**
```
log_decision("Chose React for frontend", "Better TypeScript support", "architecture,frontend")
```

### **4. Search Across All Content**
```
search_all_content("authentication")
# Finds relevant discussions, decisions, and documentation
```

---

## ⚠️ **Important Notes**

### **Dependencies Management**

- **lib/ directory**: Excluded from git - use `requirements.txt` instead
- **Virtual environments**: Strongly recommended for isolation
- **Requirements file**: Contains all necessary dependencies with versions

### **Git Configuration**

The project is configured to exclude:
- `lib/` directory (dependencies managed via requirements.txt)
- `archive/` directory (old versions and development files)
- Standard Python artifacts (`__pycache__`, `.pyc` files, etc.)

### **Common Issues & Solutions:**

**Issue:** Tools not appearing after installation  
**Solution:** Restart Claude Desktop completely

**Issue:** Project won't initialize  
**Solution:** Check directory permissions and path accessibility

**Issue:** Search returns no results  
**Solution:**
```
sync_fts_tables()  # Rebuild search indexes
import_project_documentation()  # Ensure content is imported
```

**Issue:** SQL queries truncated too aggressively  
**Solution:**
```
memory_bank_sql_query("YOUR_QUERY", max_content_length=None)  # No truncation
# Or follow auto-suggested extract commands
```

**Issue:** Schema appears incomplete  
**Solution:**
```
verify_and_repair_schema()  # Auto-repairs missing components
```

---

## 🔧 **Development Setup**

For contributors or advanced users:

```bash
# Clone with development dependencies
git clone <repository-url>
cd memory-bank_v04

# Install with development extras (when available)
pip install -e ".[dev]"

# Run tests (when test suite is available)
# pytest tests/

# Format code (when formatting tools are configured)
# black . && mypy .
```

---

## 📞 **Support & Resources**

- **Documentation**: See `documentation/` folder for detailed guides
- **Archive**: Historical versions and development files in `archive/`
- **Schema Help**: Use `memory_bank_help()` for comprehensive tool reference
- **Troubleshooting**: Use `get_memory_bank_system_info()` for diagnostics

---

**Memory Bank MCP v1.4.0** - Your enhanced AI collaboration companion! 🚀
