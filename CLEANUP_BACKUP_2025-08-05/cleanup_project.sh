#!/bin/bash
# Memory Bank v2.1 Project Cleanup Script
# Generated: 2025-08-05.1334
# Purpose: Clean up unnecessary files while preserving essential components

echo "🧹 Starting Memory Bank v2.1 Project Cleanup..."

# Create backup directory for removed files
BACKUP_DIR="CLEANUP_BACKUP_2025-08-05"
mkdir -p "$BACKUP_DIR/old_dxt_files"
mkdir -p "$BACKUP_DIR/old_docs"
mkdir -p "$BACKUP_DIR/old_build_scripts"
mkdir -p "$BACKUP_DIR/test_files"
mkdir -p "$BACKUP_DIR/temp_dirs"

echo "📦 Moving old DXT files to backup..."
# Keep only the latest working DXT file
mv memory-bank-v04-enhanced-v1.4.0.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory-bank-v21-enhanced-dev.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory-bank-v21-enhanced.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v04_v2_all_db_functions_fixed.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_context_fixed_2025-08-04.0116.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_dxt_v01_compliant_2025-08-04.0134.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_final.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_fixed.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_fixed_2025-08-03.1721.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_fts5_semantic_2025-08-03.1824.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_fts5_semantic_COMPLETE_2025-08-03.1854.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_fts5_semantic_CONTEXT_FIXED_2025-08-03.1906.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_fts5_semantic_FIXED_2025-08-03.1840.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_fts5_semantic_FIXED_2025-08-03.1844.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null
mv memory_bank_v2_1_enhanced_full.dxt "$BACKUP_DIR/old_dxt_files/" 2>/dev/null

echo "📝 Moving old documentation files to backup..."
# Keep essential docs, move development logs
mv CONSOLIDATION_COMPLETE.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv DXT_COMPREHENSIVE_FIX_SUMMARY.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv DXT_FIX_SUMMARY.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv DXT_REBUILD_COMPLETE_DXT_V01_SPECIFICATION_COMPLIANT.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv DXT_REBUILD_COMPLETE_FTS5_SEMANTIC.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv DXT_REBUILD_CONTEXT_VALIDATION_FIXED_COMPLETE.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv DXT_REBUILD_FIXED_COMPLETE.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv FTS5_SEMANTIC_SEARCH_INTEGRATION_COMPLETE.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv INSTALLATION_FIX_SUMMARY.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv INSTALLATION_GUIDE_v1.4.0.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv MEMORY_BANK_V21_DXT_COMPLETE.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv MEMORY_BANK_V21_INTEGRATION_COMPLETE.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv MEMORY_BANK_WORKING_FINAL.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv MIGRATION_COMPLETE.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv NEXT_SESSION_FTS5_INTEGRATION_COMPLETE.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv NEXT_SESSION_STARTER.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv PRODUCTION_RELEASE_v2.0.3.md "$BACKUP_DIR/old_docs/" 2>/dev/null
mv SCHEMA_TEMPLATE_LOCATIONS.md "$BACKUP_DIR/old_docs/" 2>/dev/null

echo "🔧 Moving old build scripts to backup..."
# Keep only the current working build script
mv build-dev-dxt.sh "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv build-dxt-v21.sh "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv build-memory-bank-v21.sh "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv build_dxt.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv build_memory_bank_v2_1_dxt.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv build_memory_bank_v2_1_enhanced_fixed.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv build_memory_bank_v2_dxt.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null

echo "🧪 Moving test files to backup..."
mv test_final_verification.py "$BACKUP_DIR/test_files/" 2>/dev/null
mv test_modular_integration.py "$BACKUP_DIR/test_files/" 2>/dev/null
mv test_modular_structure.py "$BACKUP_DIR/test_files/" 2>/dev/null
mv test_phase2_creation.py "$BACKUP_DIR/test_files/" 2>/dev/null
mv test_phase3a_consolidation.py "$BACKUP_DIR/test_files/" 2>/dev/null
mv test_unified_search.py "$BACKUP_DIR/test_files/" 2>/dev/null

echo "🗂️ Moving temporary directories to backup..."
mv lib_temp "$BACKUP_DIR/temp_dirs/" 2>/dev/null
mv lib_incomplete "$BACKUP_DIR/temp_dirs/" 2>/dev/null
mv lib_from_working_dxt "$BACKUP_DIR/temp_dirs/" 2>/dev/null

echo "🗑️ Removing cache and temporary files..."
rm -rf __pycache__ 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null

echo "📜 Moving old development files to backup..."
mv cli_usage_guide.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv mcp_command_analysis.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv mcp_command_modules.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv migrate_v1_4_to_v2_0.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv migration_20250730_132704.log "$BACKUP_DIR/old_docs/" 2>/dev/null
mv migration_20250730_133200.log "$BACKUP_DIR/old_docs/" 2>/dev/null
mv phase3a_mcp_updates.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv setup.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv show_help.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv show_help_simple.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv temp_server_files.py "$BACKUP_DIR/old_build_scripts/" 2>/dev/null
mv memory_bank_v04.log "$BACKUP_DIR/old_docs/" 2>/dev/null

echo "📁 Moving large archive directories to backup..."
mv archive "$BACKUP_DIR/" 2>/dev/null
mv deprecated "$BACKUP_DIR/" 2>/dev/null
mv memory-bank-v21-staging "$BACKUP_DIR/" 2>/dev/null
mv migration_v21 "$BACKUP_DIR/" 2>/dev/null

echo "✅ Cleanup completed!"
echo ""
echo "📊 Cleanup Summary:"
echo "   🗂️ Backed up old DXT files to: $BACKUP_DIR/old_dxt_files/"
echo "   📝 Backed up old documentation to: $BACKUP_DIR/old_docs/"
echo "   🔧 Backed up old build scripts to: $BACKUP_DIR/old_build_scripts/"
echo "   🧪 Backed up test files to: $BACKUP_DIR/test_files/"
echo "   📁 Backed up archive directories to: $BACKUP_DIR/"
echo ""
echo "🎯 Remaining Essential Files:"
echo "   ✅ server/ (source code)"
echo "   ✅ build_memory_bank_v2_1_dxt_v01_compliant.py (current build script)"
echo "   ✅ memory_bank_v2_1_enhanced_dxt_v01_compliant_2025-08-05.1158.dxt (latest DXT)"
echo "   ✅ README.md, requirements.txt, icon.png (essential config)"
echo "   ✅ manifest_dxt_v01_compliant.json (DXT manifest)"
echo "   ✅ .venv, .git (development environment)"
echo ""
echo "💡 The project is now clean and organized!"
