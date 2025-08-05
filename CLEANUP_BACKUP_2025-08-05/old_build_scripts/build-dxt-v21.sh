#!/bin/bash
"""
Memory Bank v2.1 DXT Build Script
==================================

Builds the complete Memory Bank v2.1 DXT package with modular migration system.
"""

set -e

echo "🚀 Building Memory Bank v2.1 Enhanced DXT Package"
echo "=================================================="

DXT_DIR="memory-bank-v21.dxt"
OUTPUT_FILE="memory-bank-v21.dxt.zip"

# Verify DXT directory exists
if [ ! -d "$DXT_DIR" ]; then
    echo "❌ Error: $DXT_DIR directory not found"
    exit 1
fi

echo "📋 Verifying DXT package structure..."

# Check required files
REQUIRED_FILES=(
    "$DXT_DIR/manifest.json"
    "$DXT_DIR/README.md"
    "$DXT_DIR/server/memory_bank_mcp/__main__.py"
    "$DXT_DIR/server/memory_bank_mcp/main.py"
    "$DXT_DIR/migration_v21/__init__.py"
    "$DXT_DIR/migration_v21/migration_manager.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
    echo "   ✅ $file"
done

echo "📊 Checking modular architecture..."

# Count lines in key modules to verify modular architecture
echo "   📄 Key module sizes:"
find "$DXT_DIR/migration_v21" -name "*.py" -exec wc -l {} + | sort -n | while read lines file; do
    if [ "$lines" -gt 350 ]; then
        echo "   ⚠️  $file: $lines lines (consider breaking down further)"
    else
        echo "   ✅ $file: $lines lines"
    fi
done

echo "🧪 Validating manifest.json..."
if ! python3 -c "import json; json.load(open('$DXT_DIR/manifest.json'))" 2>/dev/null; then
    echo "❌ Error: Invalid manifest.json"
    exit 1
fi
echo "   ✅ manifest.json is valid JSON"

# Check DXT v0.1 specification compliance
if ! grep -q '"dxt_version": "0.1"' "$DXT_DIR/manifest.json"; then
    echo "❌ Error: manifest.json missing dxt_version 0.1"
    exit 1
fi
echo "   ✅ DXT v0.1 specification compliant"

echo "📦 Creating DXT package..."

# Remove existing output file
if [ -f "$OUTPUT_FILE" ]; then
    rm "$OUTPUT_FILE"
    echo "   🗑️ Removed existing $OUTPUT_FILE"
fi

# Create ZIP archive (DXT files are ZIP archives)
cd "$DXT_DIR"
zip -r "../$OUTPUT_FILE" . -x "*.DS_Store" "*/__pycache__/*" "*.pyc" "*.log"
cd ..

echo "📊 Package statistics:"
echo "   📁 Size: $(du -h "$OUTPUT_FILE" | cut -f1)"
echo "   📋 Files: $(unzip -l "$OUTPUT_FILE" | grep -c "^[[:space:]]*[0-9]")"

echo "🔍 Validating final package..."
if ! unzip -t "$OUTPUT_FILE" > /dev/null 2>&1; then
    echo "❌ Error: Generated ZIP file is corrupted"
    exit 1
fi
echo "   ✅ ZIP file integrity verified"

echo ""
echo "🎉 BUILD COMPLETE!"
echo "=================="
echo "📦 DXT Package: $OUTPUT_FILE"
echo "📊 Ready for installation in Claude Desktop"
echo ""
echo "🚀 Installation Instructions:"
echo "1. Open Claude Desktop Settings"
echo "2. Go to Extensions tab"  
echo "3. Click 'Install Extension'"
echo "4. Select $OUTPUT_FILE"
echo "5. Restart Claude Desktop"
echo ""
echo "✨ Features included:"
echo "• Modular v2.1 migration system"
echo "• Enhanced work_on_project with auto-migration"
echo "• Table count-based version detection"
echo "• Complete table consolidation (48 → 18 tables)"
echo "• Production-ready safety features"
echo "• CLI interface integration"
echo ""
echo "Memory Bank v2.1 Enhanced DXT - Ready to deploy! 🚀"
