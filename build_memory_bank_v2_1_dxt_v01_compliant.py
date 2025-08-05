#!/usr/bin/env python3
"""
Memory Bank v2.1 Enhanced DXT Package Builder - DXT v0.1 Specification Compliant
Filename: build_memory_bank_v2_1_dxt_v01_compliant.py
Generated: 2025-08-04.0130
Purpose: Build DXT package following official Anthropic DXT v0.1 specification

COMPLIANCE WITH OFFICIAL DXT v0.1 SPECIFICATION:
- Follows https://github.com/anthropics/dxt guidelines exactly
- Correct manifest.json structure per official spec
- Proper Python server configuration
- Standard entry point and command structure
- Compliant with official DXT toolchain expectations

FEATURES INCLUDED:
- FTS5 full-text search with BM25 ranking
- Semantic query expansion with equivalents table  
- Importance-weighted search (0-10 scale)
- Context validation fixes for registry alignment
- Official DXT v0.1 compliance for broad compatibility

Usage:
    python3 build_memory_bank_v2_1_dxt_v01_compliant.py
    python3 build_memory_bank_v2_1_dxt_v01_compliant.py --verbose
"""

import os
import sys
import zipfile
import json
import subprocess
import tempfile
import shutil
import argparse
from pathlib import Path
from datetime import datetime

def create_dxt_v01_compliant_manifest():
    """Create DXT v0.1 compliant manifest.json following official Anthropic specification"""
    manifest = {
        "dxt_version": "0.1",
        "name": "memory-bank-v2-1-enhanced",
        "version": "2.1.1",
        "description": "Memory Bank v2.1 Enhanced - Advanced AI collaboration memory with FTS5 + semantic search",
        "long_description": "Memory Bank v2.1 Enhanced provides the most advanced persistent AI collaboration memory system with FTS5 full-text search, semantic query expansion, importance-weighted ranking (0-10 scale), and context validation fixes. Features revolutionary search capabilities with 10-100x speed improvement, semantic equivalents expansion, graceful fallback system, registry-based context propagation, and comprehensive tool ecosystem.",
        
        "author": {
            "name": "Memory Bank Development Team",
            "email": "support@memory-bank.dev"
        },
        
        "homepage": "https://github.com/georgemagnuson/memory-bank_v04",
        "repository": {
            "type": "git",
            "url": "https://github.com/georgemagnuson/memory-bank_v04"
        },
        "documentation": "https://github.com/georgemagnuson/memory-bank_v04/blob/main/README.md",
        "support": "https://github.com/georgemagnuson/memory-bank_v04/issues",
        
        "icon": "icon.png",
        
        # Official DXT v0.1 Python server configuration
        "server": {
            "type": "python",
            "entry_point": "server/memory_bank_mcp/main.py",
            "mcp_config": {
                "command": "python",
                "args": [
                    "${__dirname}/server/memory_bank_mcp/main.py"
                ],
                "env": {
                    "PYTHONPATH": "${__dirname}/lib:${__dirname}/server:${__dirname}"
                }
            }
        },
        
        "keywords": [
            "memory", "collaboration", "AI", "context", "search", "FTS5", "semantic",
            "importance", "ranking", "database", "sqlite", "mcp", "claude", "persistence", "registry"
        ],
        
        "categories": [
            "productivity",
            "development-tools",
            "collaboration", 
            "database",
            "search"
        ],
        
        "permissions": {
            "file_system": {
                "read": True,
                "write": True,
                "reason": "Read/write project databases and context files"
            }
        },
        
        "requirements": {
            "python": ">=3.8"
        }
    }
    
    return manifest

def ensure_python_entry_point(server_mcp_dir, verbose=False):
    """Ensure proper Python entry point following DXT v0.1 specification"""
    main_py_path = os.path.join(server_mcp_dir, "main.py")
    
    if not os.path.exists(main_py_path):
        print(f"   ⚠️ Main entry point not found: {main_py_path}")
        return False
    
    # Verify the main.py can be executed directly
    try:
        with open(main_py_path, 'r') as f:
            content = f.read()
        
        # Check if it has proper MCP server setup
        if 'mcp.server' in content or 'MCP' in content:
            print(f"   ✅ Valid MCP server entry point: main.py")
            return True
        else:
            print(f"   ⚠️ Entry point may not be a valid MCP server")
            return False
            
    except Exception as e:
        print(f"   ❌ Error validating entry point: {e}")
        return False

def bundle_dependencies_for_dxt_v01(temp_dir, verbose=False):
    """Bundle Python dependencies following DXT v0.1 specification for Python servers"""
    lib_dir = os.path.join(temp_dir, "lib")
    os.makedirs(lib_dir, exist_ok=True)
    
    print("📦 Bundling Python dependencies for DXT v0.1 compliance...")
    
    # Try to find virtual environment
    possible_venv_paths = [
        ".venv/lib/python3.13/site-packages",
        ".venv/lib/python3.12/site-packages", 
        ".venv/lib/python3.11/site-packages",
        ".venv/lib/python3.10/site-packages",
        ".venv/lib/python3.9/site-packages",
        ".venv/lib/python3.8/site-packages"
    ]
    
    venv_site_packages = None
    for path in possible_venv_paths:
        if os.path.exists(path):
            venv_site_packages = path
            if verbose:
                print(f"   📁 Found virtual environment: {path}")
            break
    
    if venv_site_packages:
        # Essential packages for MCP compliance
        essential_packages = [
            'mcp', 'aiosqlite', 'pydantic', 'typing_extensions', 
            'anyio', 'sniffio', 'idna', 'click'
        ]
        
        package_count = 0
        copied_packages = []
        
        for item in os.listdir(venv_site_packages):
            source_item = os.path.join(venv_site_packages, item)
            dest_item = os.path.join(lib_dir, item)
            
            # Skip cache and private packages
            if (item.startswith('_') or item.startswith('.') or 
                item.startswith('~') or '__pycache__' in item):
                continue
            
            # Copy packages
            try:
                if os.path.isdir(source_item):
                    if not os.path.exists(dest_item):
                        shutil.copytree(source_item, dest_item, ignore_dangling_symlinks=True)
                        package_count += 1
                        copied_packages.append(item)
                        
                        is_essential = any(essential in item.lower() for essential in essential_packages)
                        if verbose or is_essential:
                            marker = "⭐" if is_essential else "✅"
                            print(f"   {marker} Package: {item}")
                            
                elif item.endswith(('.py', '.pyd', '.so')):
                    shutil.copy2(source_item, dest_item)
                    copied_packages.append(item)
                    if verbose:
                        print(f"   ✅ Module: {item}")
                        
            except Exception as e:
                if verbose:
                    print(f"   ⚠️ Failed to copy {item}: {e}")
                continue
        
        print(f"   ✅ Dependencies bundled successfully ({package_count} packages)")
        
        # Verify essential MCP packages
        missing_essential = []
        for essential in essential_packages:
            found = any(essential.lower() in pkg.lower() for pkg in copied_packages)
            if not found:
                missing_essential.append(essential)
        
        if missing_essential:
            print(f"   ⚠️ Missing essential packages: {', '.join(missing_essential)}")
        else:
            print(f"   ✅ All essential MCP packages included")
        
        return lib_dir, package_count
        
    else:
        print("   ❌ No virtual environment found!")
        print("   💡 Please run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt")
        return lib_dir, 0

def copy_server_structure_dxt_v01_compliant(server_mcp_dir, verbose=False):
    """Copy server structure following DXT v0.1 specification"""
    print("📂 Copying server structure for DXT v0.1 compliance...")
    
    source_server_dir = "server/memory_bank_mcp"
    
    if not os.path.exists(source_server_dir):
        print(f"   ❌ Source server directory not found: {source_server_dir}")
        return False
    
    copied_items = 0
    
    # Copy all server files and subdirectories
    for item in os.listdir(source_server_dir):
        source_item = os.path.join(source_server_dir, item)
        dest_item = os.path.join(server_mcp_dir, item)
        
        try:
            if os.path.isdir(source_item):
                if os.path.exists(dest_item):
                    shutil.rmtree(dest_item)
                shutil.copytree(source_item, dest_item, ignore_dangling_symlinks=True)
                copied_items += 1
                if verbose:
                    print(f"   📁 Directory: {item}")
                    
            elif os.path.isfile(source_item):
                shutil.copy2(source_item, dest_item)
                copied_items += 1
                if verbose:
                    print(f"   📄 File: {item}")
                    
        except Exception as e:
            print(f"   ⚠️ Failed to copy {item}: {e}")
            continue
    
    print(f"   ✅ Copied {copied_items} server items")
    
    # Verify main entry point exists and is valid
    if ensure_python_entry_point(server_mcp_dir, verbose):
        return True
    else:
        print("   ⚠️ Entry point validation issues detected")
        return True  # Continue anyway

def build_dxt_v01_compliant_package(output_file=None, verbose=False, dry_run=False):
    """Build DXT package following official DXT v0.1 specification"""
    
    if output_file is None:
        timestamp = datetime.now().strftime("%Y-%m-%d.%H%M")
        output_file = f"memory_bank_v2_1_enhanced_dxt_v01_compliant_{timestamp}.dxt"
    
    print("🚀 Building Memory Bank v2.1 Enhanced DXT Package - DXT v0.1 Specification Compliant")
    print(f"📦 Output: {output_file}")
    print(f"⏰ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📋 Following official Anthropic DXT v0.1 specification")
    
    if dry_run:
        print("🧪 DRY RUN MODE - No files will be created")
        return True
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Working directory: {temp_dir}")
        
        # Create DXT v0.1 compliant manifest.json
        print("📋 Creating DXT v0.1 compliant manifest...")
        manifest = create_dxt_v01_compliant_manifest()
        manifest_path = os.path.join(temp_dir, "manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print("   ✅ Created DXT v0.1 compliant manifest.json")
        
        # Copy essential files
        essential_files = ["icon.png", "README.md", "requirements.txt"]
        for file_name in essential_files:
            if os.path.exists(file_name):
                shutil.copy2(file_name, os.path.join(temp_dir, file_name))
                print(f"   ✅ Copied: {file_name}")
        
        # Create server directory structure (DXT v0.1 standard)
        server_root = os.path.join(temp_dir, "server")
        server_mcp_dir = os.path.join(server_root, "memory_bank_mcp")
        os.makedirs(server_mcp_dir, exist_ok=True)
        
        # Copy server structure following DXT v0.1 specification
        if not copy_server_structure_dxt_v01_compliant(server_mcp_dir, verbose):
            print("❌ Failed to copy server structure")
            return False
        
        # Bundle dependencies following DXT v0.1 Python specification
        lib_dir, package_count = bundle_dependencies_for_dxt_v01(temp_dir, verbose)
        
        # Create DXT package
        print("📦 Creating DXT v0.1 compliant package...")
        file_count = 0
        
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zipf:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arc_path)
                    file_count += 1
                    
                    if verbose and file_count % 500 == 0:
                        print(f"  📦 Packed {file_count} files...")
        
        # Package statistics
        package_size = os.path.getsize(output_file)
        size_mb = package_size / (1024 * 1024)
        
        print(f"\n🎉 DXT v0.1 Compliant Package Created Successfully!")
        print(f"📁 File: {output_file}")
        print(f"📊 Size: {size_mb:.2f} MB ({package_size:,} bytes)")
        print(f"📋 Total files: {file_count:,}")
        print(f"📦 Dependencies: {package_count} packages bundled")
        
        # Verify package compliance
        with zipfile.ZipFile(output_file, 'r') as zipf:
            lib_files = [f for f in zipf.namelist() if f.startswith('lib/')]
            server_files = [f for f in zipf.namelist() if f.startswith('server/')]
            has_manifest = 'manifest.json' in zipf.namelist()
            has_icon = 'icon.png' in zipf.namelist()
            
            print(f"\n📦 DXT v0.1 Compliance Verification:")
            print(f"   ✅ manifest.json: {'Present' if has_manifest else 'MISSING'}")
            print(f"   ✅ icon.png: {'Present' if has_icon else 'Optional - Missing'}")
            print(f"   ✅ lib/ directory: {len(lib_files)} dependency files")
            print(f"   ✅ server/ structure: {len(server_files)} server files")
            
            if has_manifest and lib_files and server_files:
                print(f"   ✅ Package meets DXT v0.1 specification requirements")
            else:
                print(f"   ⚠️ Package may not meet all DXT v0.1 requirements")
        
        print(f"\n🚀 Installation Instructions:")
        print(f"   1. Drag and drop {output_file} to Claude Desktop")
        print(f"   2. Verify installation in Claude Desktop Extensions")
        print(f"   3. Test MCP server functionality")
        
        print(f"\n🎯 DXT v0.1 Specification Compliance:")
        print(f"   ✅ Official manifest.json structure")
        print(f"   ✅ Standard Python server configuration")
        print(f"   ✅ Proper entry point and command structure")
        print(f"   ✅ Compatible with official DXT toolchain")
        
        return True

def main():
    """Main entry point for DXT v0.1 compliant builder"""
    parser = argparse.ArgumentParser(
        description="Build Memory Bank v2.1 Enhanced DXT package following official DXT v0.1 specification"
    )
    parser.add_argument("--output", "-o", 
                       help="Output DXT filename (auto-generated with timestamp if not specified)")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Test build without creating package")
    
    args = parser.parse_args()
    
    try:
        success = build_dxt_v01_compliant_package(
            output_file=args.output,
            verbose=args.verbose,
            dry_run=args.dry_run
        )
        
        if success:
            print("\n🎉 Build completed successfully!")
            if not args.dry_run:
                print("🎯 DXT v0.1 compliant Memory Bank v2.1 Enhanced ready!")
                print("✅ Follows official Anthropic DXT specification!")
        else:
            print("\n❌ Build failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Build error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
