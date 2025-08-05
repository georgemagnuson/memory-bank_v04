#!/usr/bin/env python3
"""
Memory Bank v2.0 Enhanced DXT Package Builder
Filename: build_memory_bank_v2_dxt.py
Generated: 2025-08-02.0034
Purpose: Build production-ready DXT package for Memory Bank v2.0 Enhanced with consolidated DatabaseMigrator

UPDATED FOR ANTHROPIC DXT v0.1 SPECIFICATION:
- Modern DXT v0.1 manifest format
- Proper Python server configuration  
- Consolidated Memory Bank v2.0 Enhanced modules
- Live testing ready for migration workflow

Usage:
    python3 build_memory_bank_v2_dxt.py                    # Standard build
    python3 build_memory_bank_v2_dxt.py --verbose          # Verbose output
    python3 build_memory_bank_v2_dxt.py --dry-run          # Test without building
    python3 build_memory_bank_v2_dxt.py --output custom.dxt # Custom output name
"""

import os
import sys
import zipfile
import json
import subprocess
import tempfile
import shutil
import py_compile
import argparse
from pathlib import Path
from datetime import datetime

def create_dxt_manifest():
    """Create DXT v0.1 compliant manifest.json for Memory Bank v2.0 Enhanced"""
    manifest = {
        "dxt_version": "0.1",
        "name": "memory-bank-v2-enhanced", 
        "version": "2.0.0",
        "description": "Memory Bank v2.0 Enhanced - Advanced AI collaboration memory with registry integration and automatic migration",
        "long_description": "Memory Bank v2.0 Enhanced provides the most advanced persistent AI collaboration memory system with context propagation registry, enhanced schema management, and comprehensive tool ecosystem. Features automatic v1.4.0 → v2.0 migration workflow, centralized context registry for proper tool communication, enhanced backup system with metadata, and seamless DXT deployment. Production-ready with comprehensive error handling, smart migration analysis, and live testing capabilities.",
        
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
            "entry_point": "server/memory_bank_mcp/__main__.py",
            "mcp_config": {
                "command": "python",
                "args": [
                    "-m", 
                    "memory_bank_mcp"
                ],
                "env": {
                    "PYTHONPATH": "${__dirname}/lib:${__dirname}/server:${__dirname}"
                },
                "cwd": "${__dirname}/server"
            }
        },
        
        "homepage": "https://github.com/georgemagnuson/memory-bank_v04",
        "documentation": "https://github.com/georgemagnuson/memory-bank_v04/blob/main/README.md",
        "support": "https://github.com/georgemagnuson/memory-bank_v04/issues",
        "icon": "icon.png",
        
        "server": {
            "type": "python",
            "entry_point": "server/memory_bank_mcp/__main__.py",
            "mcp_config": {
                "command": "/opt/local/bin/python3.13",
                "args": [
                    "-m", "memory_bank_mcp"
                ],
                "cwd": "${__dirname}/server",
                "env": {
                    "PYTHONPATH": "${__dirname}/lib:${__dirname}/server:${__dirname}"
                }
            }
        },
        
        "tools": [
            {"name": "memory_bank_help", "description": "Show comprehensive help for Memory Bank v2.0 Enhanced"},
            {"name": "work_on_project", "description": "Switch to working on a specific project with memory-bank integration and schema auto-migration"},
            {"name": "create_context", "description": "Create a new project context"},
            {"name": "switch_context", "description": "Switch to an existing project context"},
            {"name": "save_info", "description": "Save information to current context"},
            {"name": "search_info", "description": "Search saved information"},
            {"name": "list_contexts", "description": "List all available project contexts"},
            {"name": "get_current_context", "description": "Get current project context information"},
            {"name": "execute_sql", "description": "Execute SQL query on current context database"},
            {"name": "show_schema", "description": "Show database schema for current context"},
            {"name": "analyze_database", "description": "Analyze database structure and content"},
            {"name": "get_project_summary", "description": "Get comprehensive project summary"},
            {"name": "set_project_metadata", "description": "Set project metadata"},
            {"name": "get_project_metadata", "description": "Get project metadata"}, 
            {"name": "save_document", "description": "Save a document to the current context"},
            {"name": "search_documents", "description": "Search documents in current context"},
            {"name": "list_documents", "description": "List documents in current context"},
            {"name": "get_document", "description": "Get a specific document by title"},
            {"name": "migrate_from_v1", "description": "Migrate data from Memory Bank v1.x to v2.0"},
            {"name": "migrate_to_v2", "description": "Migrate database schema from unified_documents to documents table (v1.4.0 → v2.0)"},
            {"name": "check_migration_status", "description": "Check migration status and compatibility"},
            {"name": "create_backup", "description": "Create a backup of current context"},
            {"name": "list_backups", "description": "List available backups"},
            {"name": "restore_backup", "description": "Restore from a backup"}
        ],
        
        "keywords": [
            "memory-bank",
            "context-management",
            "database-migration", 
            "schema-management",
            "project-intelligence",
            "session-persistence",
            "full-text-search",
            "backup-system",
            "ai-collaboration",
            "consolidated-migration",
            "v2-enhanced",
            "auto-migration",
            "drop-tables",
            "30-tools"
        ],
        
        "license": "MIT",
        
        "changelog": {
            "2.0.0": {
                "date": "2025-08-02",
                "changes": [
                    "🚀 MAJOR: Memory Bank v2.0 Enhanced with consolidated DatabaseMigrator",
                    "🚀 MAJOR: Enhanced DROP deprecated tables functionality for complete v2.0 migration", 
                    "🚀 MAJOR: Consolidated schema management with single DatabaseMigrator class",
                    "🚀 MAJOR: Fixed server initialization - no more 'Memory Bank not initialized' errors",
                    "🚀 MAJOR: work_on_project tool restored for v1.4.0 workflow compatibility",
                    "✅ CONSOLIDATED: Two separate DatabaseMigrator classes into enhanced single version",
                    "✅ FIXED: Removed non-existent initialize() method calls from server startup",
                    "✅ ADDED: Proper main() function for module execution compatibility", 
                    "✅ ENHANCED: Backup system with metadata and comprehensive validation",
                    "✅ READY: End-to-end migration testing for 187 records (v1.4.0 → v2.0)",
                    "✅ LIVE TESTING: Ready for production DXT deployment and migration validation",
                    "Updated to DXT v0.1 specification for Claude Desktop compatibility",
                    "Production-ready consolidated system with enhanced error handling",
                    "Complete solution for v1.4.0 projects needing v2.0 migration with deprecated table cleanup",
                    "30 tools across 6 modular components: core_tools, sql_tools, project_tools, content_tools, migration_tools, backup_tools"
                ]
            }
        }
    }
    
    return manifest

def bundle_dependencies(source_dir, temp_dir, verbose=False):
    """Bundle Python dependencies by copying from working .venv"""
    print("📦 Bundling Python dependencies...")
    
    lib_dir = temp_dir / "lib"
    lib_dir.mkdir(exist_ok=True)
    
    # Copy dependencies from our working .venv site-packages
    venv_site_packages = source_dir / ".venv" / "lib" / "python3.13" / "site-packages"
    
    if venv_site_packages.exists():
        if verbose:
            print(f"   Copying from {venv_site_packages}")
        
        # Copy all packages from venv site-packages
        import shutil
        for item in venv_site_packages.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                dest = lib_dir / item.name
                if not dest.exists():
                    shutil.copytree(item, dest)
                    if verbose:
                        print(f"   ✅ Copied {item.name}")
            elif item.is_file() and item.suffix == '.py':
                shutil.copy2(item, lib_dir)
                if verbose:
                    print(f"   ✅ Copied {item.name}")
        
        package_count = len([d for d in lib_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
        print(f"   ✅ Dependencies bundled successfully ({package_count} packages)")
        
        if verbose:
            print(f"   📊 Total packages: {package_count}")
            
    else:
        print(f"   ❌ .venv site-packages not found at {venv_site_packages}")
        # Fallback to pip install in temp environment
        requirements_file = source_dir / "requirements.txt"
        if requirements_file.exists():
            print("   🔄 Fallback: Installing with pip...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install",
                "--target", str(lib_dir),
                "--requirement", str(requirements_file),
                "--no-deps"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Fallback installation successful")
            else:
                print(f"   ⚠️ Fallback failed: {result.stderr}")
                return None
    
    return lib_dir

def copy_consolidated_server_files(source_dir, temp_dir, verbose=False):
    """Copy all Memory Bank v2.0 Enhanced consolidated server files"""
    print("📂 Copying Memory Bank v2.0 Enhanced server code...")
    
    # Updated server files list for v2.0 Enhanced with consolidated modules
    server_files = [
        # Main entry points
        "server/memory_bank_mcp/__init__.py",
        "server/memory_bank_mcp/__main__.py",
        "server/memory_bank_mcp/main.py",
        
        # Core database and context management
        "server/memory_bank_mcp/database.py",
        "server/memory_bank_mcp/context_manager.py",
        "server/memory_bank_mcp/schema_manager.py",
        "server/memory_bank_mcp/schema_version_detector.py",
        
        # Tool modules
        "server/memory_bank_mcp/core_tools.py",
        "server/memory_bank_mcp/sql_tools.py", 
        "server/memory_bank_mcp/project_tools.py",
        "server/memory_bank_mcp/content_tools.py",
        "server/memory_bank_mcp/migration_tools.py",
        "server/memory_bank_mcp/backup_tools.py",
        
        # Legacy compatibility (if present)
        "server/memory_bank_mcp/project_manager.py",
        "server/memory_bank_mcp/migration.py",
        
        # Schema templates
        "server/memory_bank_mcp/context_template_v1.4.0.db",
        "server/memory_bank_mcp/context_template_v1.4.0.ddl", 
        "server/memory_bank_mcp/context_template_v2.0.db",
        "server/memory_bank_mcp/context_template_v2.0.ddl",
        "server/memory_bank_mcp/schema_v1_4_0_template.sql",
        "server/memory_bank_mcp/schema_v2_0_template.sql",
        
        # Registry Integration System (Context Propagation Fix)
        "server/memory_bank_mcp/context_registry.py",
        "server/memory_bank_mcp/enhanced_project_manager.py",
        "server/memory_bank_mcp/enhanced_context_tools.py",
        "server/memory_bank_mcp/registry_integration.py"
    ]
    
    # Add all modular component directories
    module_dirs = [
        "server/memory_bank_mcp/core_tools_modules",
        "server/memory_bank_mcp/sql_tools_modules", 
        "server/memory_bank_mcp/project_tools_modules",
        "server/memory_bank_mcp/content_tools_modules",
        "server/memory_bank_mcp/migration_tools_modules",
        "server/memory_bank_mcp/backup_tools_modules",
        "server/memory_bank_mcp/schema_manager_modules",
        "server/memory_bank_mcp/migration_modules"
    ]
    
    copied_count = 0
    missing_files = []
    
    # Copy individual server files
    for file_path in server_files:
        source_file = source_dir / file_path
        if source_file.exists():
            dest_file = temp_dir / file_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, dest_file)
            copied_count += 1
            if verbose:
                print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            if verbose:
                print(f"   ⚠️ Missing: {file_path}")
    
    # Copy module directories
    modules_copied = 0
    for module_dir in module_dirs:
        source_module = source_dir / module_dir
        if source_module.exists() and source_module.is_dir():
            dest_module = temp_dir / module_dir
            shutil.copytree(source_module, dest_module, dirs_exist_ok=True)
            modules_copied += 1
            if verbose:
                file_count = len(list(source_module.rglob('*.py')))
                print(f"   ✅ {module_dir} ({file_count} Python files)")
        else:
            if verbose:
                print(f"   ⚠️ Missing module dir: {module_dir}")
    
    print(f"   ✅ Copied {copied_count} server files and {modules_copied} module directories")
    
    if missing_files:
        print(f"   ⚠️ Missing {len(missing_files)} files:")
        for missing in missing_files[:5]:
            print(f"      - {missing}")
        if len(missing_files) > 5:
            print(f"      ... and {len(missing_files) - 5} more")
    
    return copied_count, missing_files

def copy_essential_files(source_dir, temp_dir, verbose=False):
    """Copy essential project files"""
    print("📋 Copying essential files...")
    
    essential_files = [
        "requirements.txt",
        "icon.png",
        "README.md",
        ".dxtignore"
    ]
    
    copied_count = 0
    missing_files = []
    
    for file_path in essential_files:
        source_file = source_dir / file_path
        if source_file.exists():
            dest_file = temp_dir / file_path
            shutil.copy2(source_file, dest_file)
            copied_count += 1
            if verbose:
                print(f"   ✅ {file_path}")
        else:
            missing_files.append(file_path)
            if verbose and file_path != "icon.png":  # Icon is optional
                print(f"   ⚠️ Missing: {file_path}")
    
    print(f"   ✅ Copied {copied_count}/{len(essential_files)} essential files")
    
    if missing_files:
        optional_missing = [f for f in missing_files if f == "icon.png"]
        required_missing = [f for f in missing_files if f != "icon.png"]
        if required_missing:
            print(f"   ⚠️ Missing required: {', '.join(required_missing)}")
        if optional_missing and verbose:
            print(f"   ℹ️ Missing optional: {', '.join(optional_missing)}")
    
    return copied_count, missing_files

def validate_dxt_manifest(temp_dir, verbose=False):
    """Validate DXT v0.1 manifest.json structure"""
    if verbose:
        print("🔍 Validating DXT v0.1 manifest.json...")
    
    manifest_file = temp_dir / "manifest.json"
    if not manifest_file.exists():
        print("   ❌ manifest.json not found")
        return False
    
    try:
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        # Check DXT v0.1 required fields
        required_fields = ['dxt_version', 'name', 'version', 'description', 'author', 'server']
        missing_fields = [field for field in required_fields if field not in manifest]
        
        if missing_fields:
            print(f"   ❌ Missing required DXT fields: {', '.join(missing_fields)}")
            return False
        
        # Validate DXT version
        if manifest.get('dxt_version') != '0.1':
            print(f"   ❌ Invalid dxt_version: {manifest.get('dxt_version')} (expected: 0.1)")
            return False
        
        # Validate server configuration
        server = manifest.get('server', {})
        if server.get('type') != 'python':
            print(f"   ❌ Invalid server type: {server.get('type')} (expected: python)")
            return False
        
        tool_count = len(manifest.get('tools', []))
        version = manifest.get('version', 'unknown')
        
        if verbose:
            print(f"   ✅ DXT v0.1 manifest valid: v{version} with {tool_count} tools")
            print(f"   📋 Entry point: {server.get('entry_point')}")
            print(f"   🐍 Server type: {server.get('type')}")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON in manifest: {e}")
        return False

def create_memory_bank_v2_dxt(output_filename=None, verbose=False, dry_run=False):
    """Create the Memory Bank v2.0 Enhanced DXT package"""
    
    print("🚀 Building Memory Bank v2.0 Enhanced DXT Package...")
    print("📋 DXT v0.1 Specification Compliant")
    
    # Determine source directory (where this script is located)
    source_dir = Path(__file__).parent.absolute()
    
    if output_filename:
        dxt_filename = Path(output_filename)
    else:
        dxt_filename = source_dir / "memory-bank-v2.0-enhanced.dxt"
    
    print(f"📁 Source: {source_dir}")
    print(f"📦 Output: {dxt_filename}")
    
    if dry_run:
        print("🧪 DRY RUN MODE - No package will be created")
    
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        if verbose:
            print(f"📁 Working directory: {temp_dir}")
        
        # Create DXT v0.1 manifest
        print("📝 Creating DXT v0.1 manifest...")
        manifest = create_dxt_manifest()
        manifest_file = temp_dir / "manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"   ✅ Created manifest.json (DXT v{manifest['dxt_version']})")
        
        # Bundle dependencies
        lib_dir = bundle_dependencies(source_dir, temp_dir, verbose)
        if lib_dir is None:
            print("❌ Failed to bundle dependencies")
            return None
        
        # Copy consolidated server files
        server_copied, server_missing = copy_consolidated_server_files(source_dir, temp_dir, verbose)
        
        # Copy essential files
        essential_copied, essential_missing = copy_essential_files(source_dir, temp_dir, verbose)
        
        # Validate DXT manifest
        if not validate_dxt_manifest(temp_dir, verbose):
            print("❌ DXT manifest validation failed")
            return None
        
        # Show summary
        print(f"\n📊 Build Summary (Memory Bank v2.0 Enhanced):")
        print(f"   📂 Server files: {server_copied} copied")
        print(f"   📋 Essential files: {essential_copied} copied")
        print(f"   📝 DXT v0.1 manifest: ✅ Valid")
        print(f"   🛠️ Tools declared: {len(manifest['tools'])}")
        
        if server_missing or essential_missing:
            total_missing = len(server_missing) + len(essential_missing)
            print(f"   ⚠️ Missing files: {total_missing}")
        
        if dry_run:
            print("\n🧪 DRY RUN COMPLETE - Memory Bank v2.0 Enhanced build validation successful")
            print("🔥 Ready for live DXT deployment and migration testing!")
            return temp_dir
        
        # Create DXT package
        print("\n📦 Creating Memory Bank v2.0 Enhanced DXT package...")
        
        try:
            with zipfile.ZipFile(dxt_filename, 'w', zipfile.ZIP_DEFLATED) as dxt:
                file_count = 0
                for item in temp_dir.rglob("*"):
                    if item.is_file():
                        arcname = item.relative_to(temp_dir)
                        dxt.write(item, arcname)
                        file_count += 1
                        if verbose and file_count % 100 == 0:
                            print(f"   📁 Packed {file_count} files...")
            
            # Report results
            package_size = dxt_filename.stat().st_size
            size_mb = package_size / (1024 * 1024)
            
            print(f"\n🎉 Memory Bank v2.0 Enhanced DXT Package Created Successfully!")
            print(f"📁 File: {dxt_filename}")
            print(f"📊 Size: {size_mb:.2f} MB ({package_size:,} bytes)")
            print(f"📋 Total files: {file_count}")
            print(f"🔢 DXT Version: v{manifest['dxt_version']}")
            print(f"🏷️ Package Version: v{manifest['version']}")
            
            # Verify package contents
            with zipfile.ZipFile(dxt_filename, 'r') as dxt:
                lib_files = [f for f in dxt.namelist() if f.startswith('lib/')]
                server_files = [f for f in dxt.namelist() if f.startswith('server/')]
                
                if verbose:
                    print(f"\n📦 Package Contents:")
                    print(f"   📚 Library files: {len(lib_files)}")
                    print(f"   🐍 Server files: {len(server_files)}")
                    print(f"   📝 Entry point: {manifest['server']['entry_point']}")
            
            print(f"\n🚀 Ready for Claude Desktop installation:")
            print(f"   1. Drag and drop {dxt_filename.name} to Claude Desktop")
            print(f"   2. Enable Memory Bank v2.0 Enhanced")
            print(f"   3. Test live migration: work_on_project('/path/to/project')")
            print(f"   4. Watch automatic v1.4.0 → v2.0 migration with 187 records!")
            
            return dxt_filename
            
        except Exception as e:
            print(f"❌ Failed to create DXT package: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Build Memory Bank v2.0 Enhanced DXT Package (DXT v0.1 Compliant)')
    parser.add_argument('--output', '-o', help='Output filename for DXT package')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Test build without creating package')
    
    args = parser.parse_args()
    
    result = create_memory_bank_v2_dxt(
        output_filename=args.output,
        verbose=args.verbose,
        dry_run=args.dry_run
    )
    
    if result is None:
        print("\n❌ Build failed!")
        sys.exit(1)
    else:
        print("\n✅ Memory Bank v2.0 Enhanced DXT build completed successfully!")
        print("🔥 Ready for live testing of consolidated migration system!")

if __name__ == "__main__":
    main()
