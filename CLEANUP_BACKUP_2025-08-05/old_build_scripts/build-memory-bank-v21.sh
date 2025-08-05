#!/bin/bash
"""
Memory Bank v2.1 Enhanced DXT Builder
======================================

Creates a proper DXT (Desktop Extension) file for Memory Bank v2.1.
DXT files are ZIP archives with .dxt extension containing manifest.json and server files.
"""

set -e

echo "🚀 Building Memory Bank v2.1 Enhanced DXT Package"
echo "=================================================="

STAGING_DIR="memory-bank-v21-staging"
DXT_FILE="memory-bank-v21-enhanced.dxt"

# Verify staging directory exists
if [ ! -d "$STAGING_DIR" ]; then
    echo "❌ Error: $STAGING_DIR directory not found"
    exit 1
fi

echo "📋 Verifying DXT package structure..."

# Check required files
REQUIRED_FILES=(
    "$STAGING_DIR/manifest.json"
    "$STAGING_DIR/server/memory_bank_mcp/__main__.py"
    "$STAGING_DIR/migration_v21/__init__.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
    echo "   ✅ $file"
done

echo "🧪 Validating manifest.json..."
if ! python3 -c "import json; json.load(open('$STAGING_DIR/manifest.json'))" 2>/dev/null; then
    echo "❌ Error: Invalid manifest.json"
    exit 1
fi
echo "   ✅ manifest.json is valid JSON"

# Check DXT v0.1 specification compliance
if ! grep -q '"dxt_version": "0.1"' "$STAGING_DIR/manifest.json"; then
    echo "❌ Error: manifest.json missing dxt_version 0.1"
    exit 1
fi
echo "   ✅ DXT v0.1 specification compliant"

echo "🧹 Cleaning staging directory..."
# Remove any system files and caches
find "$STAGING_DIR" -name ".DS_Store" -delete 2>/dev/null || true
find "$STAGING_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$STAGING_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$STAGING_DIR" -name "*.log" -delete 2>/dev/null || true

echo "📦 Creating DXT package (ZIP with .dxt extension)..."

# Remove existing DXT file
if [ -f "$DXT_FILE" ]; then
    rm "$DXT_FILE"
    echo "   🗑️ Removed existing $DXT_FILE"
fi

# Create DXT file (ZIP archive with .dxt extension)
cd "$STAGING_DIR"
zip -r "../$DXT_FILE" . -x "*.DS_Store" "*/__pycache__/*" "*.pyc" "*.log"
cd ..

echo "📊 Package statistics:"
echo "   📁 Size: $(du -h "$DXT_FILE" | cut -f1)"
echo "   📋 Files: $(unzip -l "$DXT_FILE" | grep -c "^[[:space:]]*[0-9]")"

echo "🔍 Validating final DXT package..."
if ! unzip -t "$DXT_FILE" > /dev/null 2>&1; then
    echo "❌ Error: Generated DXT file is corrupted"
    exit 1
fi
echo "   ✅ DXT file integrity verified"

# Test manifest extraction
if ! unzip -p "$DXT_FILE" manifest.json | python3 -c "import json, sys; json.load(sys.stdin)" 2>/dev/null; then
    echo "❌ Error: Cannot extract/parse manifest.json from DXT"
    exit 1
fi
echo "   ✅ manifest.json accessible in DXT"

echo ""
echo "🎉 DXT BUILD COMPLETE!"
echo "======================"
echo "📦 DXT File: $DXT_FILE"
echo "📊 Ready for installation in Claude Desktop"
echo ""
echo "🚀 Installation Instructions:"
echo "1. Open Claude Desktop"
echo "2. Go to Settings > Extensions"
echo "3. Click 'Install Extension' or drag & drop the .dxt file"
echo "4. Restart Claude Desktop if prompted"
echo ""
echo "✨ v2.1 Enhanced Features:"
echo "• Modular migration system (16 focused modules)"
echo "• Enhanced work_on_project with auto-migration"
echo "• Table count-based version detection"
echo "• Complete table consolidation (48 → 18 tables)"
echo "• Production-ready safety features"
echo "• CLI interface integration"
echo "• Backwards compatibility with all existing tools"
echo ""
echo "Memory Bank v2.1 Enhanced DXT - Ready to deploy! 🚀"
