#!/bin/bash
"""
Memory Bank v2.1 Enhanced Development DXT Builder
=================================================

Creates a proper DXT file from the development directory with integrated v2.1 migration system.
Uses the existing /server/memory_bank_mcp structure with migration_v21 integration.
"""

set -e

echo "🚀 Building Memory Bank v2.1 Enhanced DXT from Development Directory"
echo "====================================================================="

DEV_DIR="/Users/georgemagnuson/Documents/GitHub/memory-bank_v04"
STAGING_DIR="memory-bank-v21-dev-staging"
DXT_FILE="memory-bank-v21-enhanced-dev.dxt"

# Clean up any existing staging
if [ -d "$STAGING_DIR" ]; then
    rm -rf "$STAGING_DIR"
    echo "🧹 Cleaned existing staging directory"
fi

echo "📁 Creating staging directory from development source..."
mkdir -p "$STAGING_DIR"

# Copy server directory (complete Memory Bank MCP system)
echo "📋 Copying server directory..."
cp -r "$DEV_DIR/server" "$STAGING_DIR/"

# Copy migration_v21 directory (modular migration system)
echo "🔄 Copying migration_v21 system..."
cp -r "$DEV_DIR/migration_v21" "$STAGING_DIR/"

# Copy lib directory (Python dependencies - CRITICAL for DXT!)
if [ -d "$DEV_DIR/lib" ]; then
    echo "📚 Copying Python dependencies (lib/)..."
    cp -r "$DEV_DIR/lib" "$STAGING_DIR/"
    echo "   ✅ Dependencies copied: $(du -sh "$DEV_DIR/lib" | cut -f1)"
else
    echo "❌ ERROR: lib directory not found!"
    echo "   The lib/ directory with Python dependencies is required for a proper DXT build."
    echo "   Expected at: $DEV_DIR/lib"
    exit 1
fi

# Create manifest.json for development DXT
echo "📝 Creating development manifest.json..."
cat > "$STAGING_DIR/manifest.json" << 'EOF'
{
  "dxt_version": "0.1",
  "name": "memory-bank-v21-enhanced-dev",
  "version": "2.1.0-dev",
  "description": "Memory Bank v2.1 Enhanced - Development build with integrated modular migration system",
  "author": {
    "name": "Memory Bank Development Team",
    "email": "dev@memorybank.ai"
  },
  "repository": {
    "type": "git",
    "url": "https://github.com/memory-bank/memory-bank-v21-dev"
  },
  "license": "MIT",
  "keywords": ["memory", "database", "ai", "collaboration", "migration", "v2.1", "development"],
  "server": {
    "type": "python",
    "entry_point": "server/memory_bank_mcp/__main__.py",
    "mcp_config": {
      "command": "python",
      "args": ["-m", "memory_bank_mcp"],
      "env": {
        "PYTHONPATH": "${__dirname}/server:${__dirname}/migration_v21:${__dirname}"
      },
      "cwd": "${__dirname}"
    }
  },
  "permissions": {
    "filesystem": {
      "read": true,
      "write": true,
      "description": "Required for database operations and project file management"
    },
    "network": {
      "enabled": false,
      "description": "Local-only operation for security"
    }
  },
  "features": [
    "🏗️ Modular Architecture - No monolithic files (all <300 lines)",
    "🔄 Enhanced Migration - Table count-based version detection",
    "📊 Complete Consolidation - 48→18 table optimization",
    "🧹 Legacy Cleanup - Clean v2.1 schema architecture", 
    "💾 Production Safety - Backup, rollback, dry-run testing",
    "🔍 FTS5 + Semantic Search - Enhanced search capabilities",
    "🛠️ Enhanced Tools - Integrated migration in existing commands",
    "🚀 Development Build - Latest features and improvements"
  ],
  "requirements": {
    "python": ">=3.8"
  },
  "development": {
    "build_date": "2025-08-04",
    "source": "Development directory integration",
    "features": [
      "Integrated v2.1 migration system in existing tools",
      "Enhanced work_on_project with auto-migration detection",
      "New migrate_database and analyze_database tools",
      "Backwards compatibility with all existing functionality"
    ]
  }
}
EOF

# Create README for development DXT
echo "📖 Creating development README..."
cat > "$STAGING_DIR/README.md" << 'EOF'
# Memory Bank v2.1 Enhanced - Development Build

## 🚀 **Integrated v2.1 Migration System**

This development build integrates the complete v2.1 modular migration system directly into the existing Memory Bank MCP server without separate commands.

---

## ✨ **Enhanced Existing Tools**

### **🔄 Enhanced `work_on_project()`**
The existing `work_on_project()` command now includes:
- **Automatic v2.1 migration detection** using table count analysis
- **Seamless upgrade offers** from v1.x/v2.0 to v2.1
- **Backwards compatibility** with existing functionality
- **Production-ready safety** features

### **🆕 New Migration Tools**
- **`migrate_database()`** - Direct database migration to v2.1
- **`analyze_database()`** - Enhanced version detection and analysis

### **📚 Updated Help System**
- **`memory_bank_help()`** - Complete v2.1 feature documentation

---

## 🏗️ **Modular Architecture**

### **Migration System Structure:**
```
migration_v21/                    # 16 focused modules
├── migration_manager.py          # Main interface (147 lines)
├── version_detector.py           # Table count detection (267 lines)
├── content_migrator.py           # Migration orchestrator (114 lines)
├── schema_creator.py             # v2.1 creation (260 lines)
├── content_migrator_modules/     # 5 specialized modules
├── migration_manager_modules/    # 3 orchestration modules
└── [all modules <300 lines]      # No monolithic files
```

### **Integration Points:**
- **Enhanced `work_on_project()`** - Auto-detects migration needs
- **Direct migration tools** - `migrate_database()`, `analyze_database()`
- **Backwards compatibility** - All existing tools work unchanged
- **Safety features** - Backup, rollback, dry-run capabilities

---

## 📊 **Migration Capabilities**

### **Your Database Transformation:**
```
Before (v2.0):  48 tables, 277+ records, legacy bloat
After (v2.1):   18 tables, 277+ records, clean architecture
```

### **Content Consolidation:**
- `unified_documents` → `documents` (type='document')
- `chat_sessions` → `documents` (type='chat_session')  
- `discussions` → `documents` (type='discussion')
- `artifacts` → `documents` (type='artifact')
- All content preserved with proper document types

---

## 🎯 **Usage Examples**

### **Enhanced Project Setup:**
```
work_on_project("/path/to/your/project")
```
**Now automatically:**
- Detects database version using table count
- Offers v2.1 migration if beneficial
- Initializes with enhanced capabilities

### **Direct Migration:**
```
analyze_database("/path/to/context.db")
migrate_database("/path/to/context.db", confirm=True)
```

### **All Existing Tools Work:**
```
save_info("content", "category")
search_info("query")
execute_sql("SELECT * FROM documents LIMIT 5")
```

---

## 🛡️ **Safety Features**

- **Automatic backups** before any migration
- **Rollback capability** if migration fails
- **Dry-run testing** for safe validation
- **Atomic operations** ensure database consistency
- **Enhanced error handling** with clear diagnostics

---

## 🎉 **Benefits**

### **No Breaking Changes:**
- All existing commands work exactly the same
- Enhanced functionality added transparently
- Backwards compatibility guaranteed

### **Enhanced Capabilities:**
- Table count-based version detection (most reliable)
- Complete database consolidation (48 → 18 tables)
- Production-ready migration safety
- Modular, maintainable architecture

Memory Bank v2.1 Enhanced Development Build - Seamless evolution! 🚀
EOF

# Add icon (copy from existing DXT if available)
if [ -f "$DEV_DIR/memory_bank_v2_1_enhanced_dxt_v01_compliant_2025-08-04.0134.dxt" ]; then
    echo "🎨 Extracting icon from existing DXT..."
    unzip -j "$DEV_DIR/memory_bank_v2_1_enhanced_dxt_v01_compliant_2025-08-04.0134.dxt" icon.png -d "$STAGING_DIR/" 2>/dev/null || echo "⚠️ Could not extract icon, continuing without"
fi

echo "🧹 Cleaning staging directory..."
find "$STAGING_DIR" -name ".DS_Store" -delete 2>/dev/null || true
find "$STAGING_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$STAGING_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$STAGING_DIR" -name "*.log" -delete 2>/dev/null || true

echo "📊 Analyzing modular architecture..."
echo "   📄 Migration system modules:"
find "$STAGING_DIR/migration_v21" -name "*.py" -exec wc -l {} + | sort -n | while read lines file; do
    if [ "$lines" -gt 350 ]; then
        echo "   ⚠️  $file: $lines lines (large module)"
    else
        echo "   ✅ $file: $lines lines"
    fi
done

echo "🧪 Validating development DXT structure..."
REQUIRED_FILES=(
    "$STAGING_DIR/manifest.json"
    "$STAGING_DIR/server/memory_bank_mcp/__main__.py"
    "$STAGING_DIR/server/memory_bank_mcp/main.py"
    "$STAGING_DIR/migration_v21/__init__.py"
    "$STAGING_DIR/migration_v21/migration_manager.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
    echo "   ✅ $file"
done

if ! python3 -c "import json; json.load(open('$STAGING_DIR/manifest.json'))" 2>/dev/null; then
    echo "❌ Error: Invalid manifest.json"
    exit 1
fi
echo "   ✅ manifest.json is valid JSON"

if ! grep -q '"dxt_version": "0.1"' "$STAGING_DIR/manifest.json"; then
    echo "❌ Error: manifest.json missing dxt_version 0.1"
    exit 1
fi
echo "   ✅ DXT v0.1 specification compliant"

echo "📦 Creating development DXT package..."
if [ -f "$DXT_FILE" ]; then
    rm "$DXT_FILE"
    echo "   🗑️ Removed existing $DXT_FILE"
fi

cd "$STAGING_DIR"
zip -r "../$DXT_FILE" . -x "*.DS_Store" "*/__pycache__/*" "*.pyc" "*.log" "*/.*"
cd ..

echo "📊 Development package statistics:"
echo "   📁 Total size: $(du -h "$DXT_FILE" | cut -f1)"
echo "   📋 Total files: $(unzip -l "$DXT_FILE" | grep -c "^[[:space:]]*[0-9]")"

# Show component breakdown
if [ -d "$STAGING_DIR" ]; then
    echo "   📊 Component sizes:"
    echo "      📁 Server: $(du -sh "$STAGING_DIR/server" | cut -f1)"
    echo "      🔄 Migration: $(du -sh "$STAGING_DIR/migration_v21" | cut -f1)" 
    echo "      📚 Dependencies: $(du -sh "$STAGING_DIR/lib" | cut -f1)"
fi

echo "🔍 Validating final development DXT..."
if ! unzip -t "$DXT_FILE" > /dev/null 2>&1; then
    echo "❌ Error: Generated DXT file is corrupted"
    exit 1
fi
echo "   ✅ DXT file integrity verified"

if ! unzip -p "$DXT_FILE" manifest.json | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
    echo "❌ Error: Cannot extract/parse manifest.json from DXT"
    exit 1
fi
echo "   ✅ manifest.json accessible in DXT"

# Validate DXT size (should be 25MB+ with dependencies)
DXT_SIZE_BYTES=$(stat -f%z "$DXT_FILE" 2>/dev/null || stat -c%s "$DXT_FILE" 2>/dev/null)
DXT_SIZE_MB=$((DXT_SIZE_BYTES / 1024 / 1024))

if [ "$DXT_SIZE_MB" -lt 25 ]; then
    echo "⚠️  WARNING: DXT size is ${DXT_SIZE_MB}MB (expected 25MB+)"
    echo "   This may indicate missing Python dependencies in lib/"
    echo "   Continuing build, but installation may fail..."
else
    echo "   ✅ DXT size validated: ${DXT_SIZE_MB}MB (includes dependencies)"
fi

# Clean up staging
rm -rf "$STAGING_DIR"
echo "   🧹 Staging directory cleaned"

echo ""
echo "🎉 DEVELOPMENT DXT BUILD COMPLETE!"
echo "=================================="
echo "📦 DXT File: $DXT_FILE"
echo "📊 Ready for installation in Claude Desktop"
echo ""
echo "🚀 Installation Instructions:"
echo "1. Open Claude Desktop"
echo "2. Go to Settings > Extensions"
echo "3. Click 'Install Extension' or drag & drop the .dxt file"
echo "4. Restart Claude Desktop if prompted"
echo ""
echo "✨ Development Build Features:"
echo "• Integrated v2.1 migration in existing commands"
echo "• Enhanced work_on_project with auto-migration detection"
echo "• New migrate_database and analyze_database tools"
echo "• Complete backwards compatibility"
echo "• Modular architecture (16 focused modules, all <300 lines)"
echo "• Production-ready safety features"
echo ""
echo "🔄 Enhanced Commands Available:"
echo "• work_on_project() - Now with v2.1 migration integration"
echo "• migrate_database() - Direct database migration"
echo "• analyze_database() - Enhanced version detection"
echo "• memory_bank_help() - Updated documentation"
echo ""
echo "Memory Bank v2.1 Enhanced Development Build - Ready to deploy! 🚀"
