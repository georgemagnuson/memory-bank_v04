#!/usr/bin/env python3
"""
Memory Bank v1.4.0 DXT Package Builder
Generated: 2025-07-26.1440
Purpose: Build comprehensive DXT package with all v1.4.0 enhancements
         Following proven v1.3.0 pattern with bundled dependencies

This script creates the memory-bank-v04-enhanced-v1.4.0.dxt package
using the exact pattern that worked for v1.3.0:
- Complete lib/ directory with all dependencies
- Python bytecode compilation
- Proper PYTHONPATH configuration
- Enhanced manifest.json
"""

import os
import sys
import zipfile
import json
import subprocess
import tempfile
import shutil
import py_compile
from pathlib import Path

def bundle_dependencies(source_dir, temp_dir):
    """Bundle all Python dependencies into lib/ directory"""
    print("📦 Bundling Python dependencies...")
    
    lib_dir = temp_dir / "lib"
    lib_dir.mkdir(exist_ok=True)
    
    # Use pip to install all dependencies into lib/
    requirements_file = source_dir / "requirements.txt"
    
    if requirements_file.exists():
        print(f"   Installing from {requirements_file}")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "--target", str(lib_dir),
            "--requirement", str(requirements_file),
            "--no-deps"  # Avoid dependency conflicts
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"⚠️ Pip install warning: {result.stderr}")
        
        # Also install with dependencies to ensure completeness
        result2 = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "--target", str(lib_dir),
            "--requirement", str(requirements_file),
            "--upgrade", "--force-reinstall"
        ], capture_output=True, text=True)
        
        if result2.returncode == 0:
            print("   ✅ Dependencies bundled successfully")
        else:
            print(f"   ⚠️ Some dependencies may be missing: {result2.stderr}")
    
    # Copy any additional lib files from current project
    project_lib = source_dir / "lib"
    if project_lib.exists():
        print("   📁 Copying existing lib/ directory...")
        for item in project_lib.iterdir():
            if item.is_dir():
                shutil.copytree(item, lib_dir / item.name, dirs_exist_ok=True)
            else:
                shutil.copy2(item, lib_dir / item.name)
    
    return lib_dir

def compile_python_bytecode(directory):
    """Compile Python files to bytecode for optimization"""
    print("⚡ Compiling Python bytecode...")
    
    compiled_count = 0
    for py_file in directory.rglob("*.py"):
        try:
            py_compile.compile(py_file, doraise=True)
            compiled_count += 1
        except py_compile.PyCompileError as e:
            print(f"   ⚠️ Could not compile {py_file}: {e}")
    
    print(f"   ✅ Compiled {compiled_count} Python files")

def create_enhanced_manifest(source_dir, temp_dir):
    """Create manifest.json with proper PYTHONPATH and v1.4.0 enhancements"""
    print("📝 Creating enhanced manifest.json...")
    
    # Detect Python interpreter (prioritize the one used for v1.3.0)
    python_path = "/Users/georgemagnuson/.direnv/python-3.13.5/bin/python3"
    if not Path(python_path).exists():
        python_path = sys.executable
    
    manifest = {
        "dxt_version": "0.1",
        "name": "Memory Bank v04 Enhanced",
        "version": "1.4.0",
        "description": "Enhanced Memory Bank MCP with revolutionary smart context-aware SQL truncation system",
        "long_description": "Memory Bank v04 Enhanced provides persistent AI collaboration memory with revolutionary smart context-aware SQL truncation system. Features intelligent query pattern analysis, automatic content prioritization, and seamless full/truncated result switching. Includes comprehensive schema verification with automatic repair, backup system, template specifications, enhanced documents_v2 schema, semantic mappings, and full-text search across all content types. Bundled dependencies ensure reliable installation.",
        "author": {
            "name": "Memory Bank Development Team",
            "email": "support@memory-bank.dev"
        },
        "repository": {
            "type": "git",
            "url": "https://github.com/georgemagnuson/memory-bank_v04"
        },
        "homepage": "https://github.com/georgemagnuson/memory-bank_v04",
        "documentation": "https://github.com/georgemagnuson/memory-bank_v04/blob/main/README.md",
        "support": "https://github.com/georgemagnuson/memory-bank_v04/issues",
        "icon": "icon.png",
        "server": {
            "type": "python",
            "entry_point": "server/main.py",
            "mcp_config": {
                "command": python_path,
                "args": [
                    "${__dirname}/server/main.py"
                ],
                "env": {
                    "PYTHONPATH": "${__dirname}/lib:${__dirname}/server:${__dirname}"
                }
            }
        },
        "user_config": {
            "default_project_path": {
                "type": "directory",
                "title": "Default Project Directory",
                "description": "Default directory for Memory Bank project initialization",
                "required": False,
                "default": "${HOME}/Documents/Projects"
            },
            "auto_save_enabled": {
                "type": "boolean",
                "title": "Enable Auto-Save",
                "description": "Automatically save context after each exchange",
                "required": False,
                "default": True
            },
            "centralized_backup_path": {
                "type": "directory",
                "title": "Centralized Backup Directory",
                "description": "Directory for centralized weekly/monthly backups (defaults to ~/Documents/MemoryBankBackups)",
                "required": False,
                "default": "${HOME}/Documents/MemoryBankBackups"
            }
        },
        "tools": [
            {
                "name": "memory_bank_help",
                "description": "Show comprehensive help for all Memory Bank MCP commands and features"
            },
            {
                "name": "work_on_project", 
                "description": "Switch to working on a specific project with memory-bank integration"
            },
            {
                "name": "search_all_content",
                "description": "Universal full-text search across all content types with ranking and highlighting (includes documents_v2)"
            },
            {
                "name": "log_decision",
                "description": "Log an architectural or implementation decision with tags and rationale"
            },
            {
                "name": "query_decisions", 
                "description": "Search and retrieve logged decisions with full-text search"
            },
            {
                "name": "get_memory_bank_status",
                "description": "Get current status and statistics of the memory bank database"
            },
            {
                "name": "memory_bank_sql_query",
                "description": "Execute SQL query on current project's context.db database with smart context-aware truncation"
            },
            {
                "name": "extract_large_document",
                "description": "Extract large document content to file for complete reading (bypasses SQL truncation limits)"
            },
            {
                "name": "migrate_project_md_files",
                "description": "Migrate existing .md files from a project to Memory Bank MCP v2 database"
            },
            {
                "name": "import_markdown_files",
                "description": "Import markdown files into the database for full-text search"
            },
            {
                "name": "generate_enhanced_session_starter",
                "description": "Generate session starter with database-enhanced context"
            },
            {
                "name": "backup_context_db",
                "description": "Create manual or scheduled backups of context.db with integrity verification"
            },
            {
                "name": "list_backups",
                "description": "List all available backups with metadata and integrity status"
            },
            {
                "name": "store_template_spec",
                "description": "Store complete template specifications with metadata for spec-workflow systems"
            },
            {
                "name": "discover_templates",
                "description": "Discover templates using FTS search and filtering by workflow system, phase, and project type"
            },
            {
                "name": "verify_and_repair_schema",
                "description": "Manually verify and repair project schema to ensure complete Memory Bank v04 structure"
            }
        ],
        "keywords": [
            "memory-bank",
            "context-management", 
            "full-text-search",
            "project-intelligence",
            "session-persistence",
            "schema-verification",
            "schema-repair",
            "auto-repair",
            "database-management",
            "spec-workflow",
            "documents-v2",
            "semantic-search",
            "backup-system",
            "template-specifications",
            "smart-truncation",
            "context-aware",
            "query-analysis"
        ],
        "license": "MIT",
        "changelog": {
            "1.4.0": {
                "date": "2025-07-26",
                "changes": [
                    "Revolutionary smart context-aware SQL truncation system with query pattern analysis",
                    "Intelligent content prioritization based on query context and user intent",
                    "Automatic switching between full and truncated results based on content size and query complexity",
                    "Enhanced content presentation with smart highlighting and section organization",
                    "Improved user experience with clear indicators for truncated vs full results",
                    "Performance optimizations for large database queries",
                    "Bundled dependencies for reliable installation across different environments",
                    "Enhanced PYTHONPATH configuration following official DXT specifications",
                    "Python bytecode compilation for improved runtime performance"
                ]
            },
            "1.3.0": {
                "date": "2025-07-23",
                "changes": [
                    "Added comprehensive automatic schema verification and repair system",
                    "Integrated auto-repair into work_on_project() for seamless schema completion",
                    "Added verify_and_repair_schema() manual tool for troubleshooting",
                    "Implemented safe additive schema repair (adds missing tables/indexes without modifying existing data)",
                    "Added automatic backup creation before schema repairs for safety",
                    "Enhanced project status messages to show schema verification results",
                    "Created Memory Bank v04 Complete Schema template for authoritative reference",
                    "Added detection and repair of missing core tables (documents_v2, semantic_equivalents)",
                    "Implemented FTS table verification and repair for full-text search capabilities",
                    "Added comprehensive error handling and repair reporting"
                ]
            }
        }
    }
    
    # Write manifest to temp directory
    manifest_file = temp_dir / "manifest.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    print(f"   ✅ Enhanced manifest created with PYTHONPATH: {manifest['server']['mcp_config']['env']['PYTHONPATH']}")
    return manifest_file

def create_dxt_package():
    """Create the DXT package with all v1.4.0 components following v1.3.0 pattern"""
    
    print("🚀 Building Memory Bank v1.4.0 DXT Package (v1.3.0 Pattern)...")
    
    # Source directory
    source_dir = Path("/Users/georgemagnuson/Documents/GitHub/memory-bank_v04")
    
    # DXT package filename
    dxt_filename = source_dir / "memory-bank-v04-enhanced-v1.4.0.dxt"
    
    # Create temporary directory for building
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        print(f"📁 Working in temporary directory: {temp_dir}")
        
        # Step 1: Bundle dependencies into lib/
        lib_dir = bundle_dependencies(source_dir, temp_dir)
        
        # Step 2: Copy server code
        print("📂 Copying server code...")
        server_dir = temp_dir / "server"
        server_dir.mkdir(exist_ok=True)
        
        # Copy main server files
        server_files = [
            "server/main.py",
            "server/memory_bank_mcp/__init__.py", 
            "server/memory_bank_mcp/main.py",
            "server/memory_bank_mcp/database.py",
            "server/memory_bank_mcp/context_manager.py",
            "server/memory_bank_mcp/project_manager.py",
            "server/memory_bank_mcp/backup_manager.py",
            "server/memory_bank_mcp/template_spec_manager.py",
            "server/memory_bank_mcp/migration.py",
            "server/memory_bank_mcp/phase1_tools.py",
        ]
        
        for file_path in server_files:
            source_file = source_dir / file_path
            if source_file.exists():
                # Create subdirectories as needed
                dest_file = temp_dir / file_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                print(f"   ✅ Copied: {file_path}")
            else:
                print(f"   ⚠️ Missing: {file_path}")
        
        # Step 3: Compile Python bytecode
        compile_python_bytecode(temp_dir)
        
        # Step 4: Create enhanced manifest.json
        manifest_file = create_enhanced_manifest(source_dir, temp_dir)
        
        # Step 5: Copy additional files
        print("📋 Copying additional files...")
        additional_files = [
            "icon.png",
            "README.md", 
            "requirements.txt",
            "setup.py",
            "server/user_feedback/RESPONSE_sql_truncation_bug_FIXED.md",
            "server/user_feedback/TECHNICAL_RESPONSE_sql_analysis_RESOLVED.md",
            "server/user_feedback/USER_FEEDBACK_RESPONSE_SUMMARY.md",
        ]
        
        for file_path in additional_files:
            source_file = source_dir / file_path
            if source_file.exists():
                dest_file = temp_dir / file_path
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, dest_file)
                print(f"   ✅ Copied: {file_path}")
        
        # Step 6: Create DXT package (ZIP file)
        print("📦 Creating DXT package...")
        with zipfile.ZipFile(dxt_filename, 'w', zipfile.ZIP_DEFLATED) as dxt:
            for item in temp_dir.rglob("*"):
                if item.is_file():
                    arcname = item.relative_to(temp_dir)
                    dxt.write(item, arcname)
        
        # Step 7: Verify the package
        package_size = dxt_filename.stat().st_size
        size_mb = package_size / (1024 * 1024)
        
        print(f"\n🎉 DXT Package Created Successfully!")
        print(f"📁 File: {dxt_filename}")
        print(f"📊 Size: {size_mb:.2f} MB ({package_size:,} bytes)")
        
        # List contents summary
        print(f"\n📋 Package Contents Summary:")
        with zipfile.ZipFile(dxt_filename, 'r') as dxt:
            file_count = len(dxt.infolist())
            lib_files = [f for f in dxt.namelist() if f.startswith('lib/')]
            server_files = [f for f in dxt.namelist() if f.startswith('server/')]
            pycache_files = [f for f in dxt.namelist() if '__pycache__' in f]
            
            print(f"   📁 Total files: {file_count}")
            print(f"   📦 Library files: {len(lib_files)}")
            print(f"   🐍 Server files: {len(server_files)}")
            print(f"   ⚡ Bytecode files: {len(pycache_files)}")
        
        print(f"\n🚀 Ready for installation:")
        print(f"   Drag and drop to Claude Desktop or use: claude install {dxt_filename}")
        print(f"\n✨ Key improvements in v1.4.0:")
        print(f"   • Smart context-aware SQL truncation")
        print(f"   • Bundled dependencies ({size_mb:.1f}MB)")
        print(f"   • Python bytecode compilation")
        print(f"   • Enhanced PYTHONPATH configuration")
        
        return dxt_filename

if __name__ == "__main__":
    create_dxt_package()
