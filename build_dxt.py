#!/usr/bin/env python3
"""
Memory Bank v1.4.0 DXT Package Builder
Filename: build_dxt.py
Generated: 2025-07-28.0027
Purpose: Build production-ready DXT package for Memory Bank v1.4.0

Usage:
    python3 build_dxt.py                    # Standard build
    python3 build_dxt.py --verbose          # Verbose output
    python3 build_dxt.py --dry-run          # Test without building
    python3 build_dxt.py --output custom.dxt # Custom output name
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

def bundle_dependencies(source_dir, temp_dir, verbose=False):
    """Bundle Python dependencies into lib/ directory"""
    print("📦 Bundling Python dependencies...")
    
    lib_dir = temp_dir / "lib"
    lib_dir.mkdir(exist_ok=True)
    
    requirements_file = source_dir / "requirements.txt"
    
    if requirements_file.exists():
        if verbose:
            print(f"   Installing from {requirements_file}")
        
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "--target", str(lib_dir),
            "--requirement", str(requirements_file),
            "--upgrade", "--force-reinstall"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Dependencies bundled successfully")
            if verbose:
                # Count installed packages
                package_count = len([d for d in lib_dir.iterdir() if d.is_dir() and not d.name.startswith('.')])
                print(f"   📊 Installed {package_count} packages")
        else:
            print(f"   ⚠️ Some dependencies may be missing: {result.stderr}")
            if verbose:
                print(f"   📋 Full error output: {result.stdout}")
    else:
        print(f"   ❌ requirements.txt not found at {requirements_file}")
        return None
    
    return lib_dir

def copy_server_files(source_dir, temp_dir, verbose=False):
    """Copy all server code and modules"""
    print("📂 Copying server code...")
    
    server_files = [
        "server/main.py",
        "server/memory_bank_mcp/__init__.py",
        "server/memory_bank_mcp/__main__.py", 
        "server/memory_bank_mcp/main.py",
        "server/memory_bank_mcp/database.py",
        "server/memory_bank_mcp/context_manager.py",
        "server/memory_bank_mcp/project_manager.py",
        "server/memory_bank_mcp/backup_manager.py",
        "server/memory_bank_mcp/template_spec_manager.py",
        "server/memory_bank_mcp/migration.py",
        "server/memory_bank_mcp/core_tools.py",
        "server/memory_bank_mcp/sql_tools.py",
        "server/memory_bank_mcp/project_tools.py", 
        "server/memory_bank_mcp/content_tools.py",
        "server/memory_bank_mcp/migration_tools.py",
        "server/memory_bank_mcp/backup_tools.py",
        "server/memory_bank_mcp/phase1_tools.py",
    ]
    
    copied_count = 0
    missing_files = []
    
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
    
    print(f"   ✅ Copied {copied_count}/{len(server_files)} server files")
    
    if missing_files:
        print(f"   ⚠️ Missing {len(missing_files)} files:")
        for missing in missing_files[:5]:  # Show first 5
            print(f"      - {missing}")
        if len(missing_files) > 5:
            print(f"      ... and {len(missing_files) - 5} more")
    
    return copied_count, missing_files

def copy_essential_files(source_dir, temp_dir, verbose=False):
    """Copy essential project files"""
    print("📋 Copying essential files...")
    
    essential_files = [
        "manifest.json",
        "icon.png", 
        "README.md",
        "requirements.txt",
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
            if verbose:
                print(f"   ⚠️ Missing: {file_path}")
    
    print(f"   ✅ Copied {copied_count}/{len(essential_files)} essential files")
    
    if missing_files:
        print(f"   ⚠️ Missing: {', '.join(missing_files)}")
    
    return copied_count, missing_files

def validate_manifest(temp_dir, verbose=False):
    """Validate manifest.json structure"""
    if verbose:
        print("🔍 Validating manifest.json...")
    
    manifest_file = temp_dir / "manifest.json"
    if not manifest_file.exists():
        print("   ❌ manifest.json not found")
        return False
    
    try:
        with open(manifest_file, 'r') as f:
            manifest = json.load(f)
        
        required_fields = ['name', 'version', 'description', 'server', 'tools']
        missing_fields = [field for field in required_fields if field not in manifest]
        
        if missing_fields:
            print(f"   ❌ Missing required fields: {', '.join(missing_fields)}")
            return False
        
        tool_count = len(manifest.get('tools', []))
        version = manifest.get('version', 'unknown')
        
        if verbose:
            print(f"   ✅ Manifest valid: v{version} with {tool_count} tools")
        
        return True
        
    except json.JSONDecodeError as e:
        print(f"   ❌ Invalid JSON in manifest: {e}")
        return False

def create_dxt_package(output_filename=None, verbose=False, dry_run=False):
    """Create the DXT package"""
    
    print("🚀 Building Memory Bank v1.4.0 DXT Package...")
    
    # Determine source directory (where this script is located)
    source_dir = Path(__file__).parent.absolute()
    
    if output_filename:
        dxt_filename = Path(output_filename)
    else:
        dxt_filename = source_dir / "memory-bank-v04-enhanced-v1.4.0.dxt"
    
    print(f"📁 Source: {source_dir}")
    print(f"📦 Output: {dxt_filename}")
    
    if dry_run:
        print("🧪 DRY RUN MODE - No package will be created")
    
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        if verbose:
            print(f"📁 Working directory: {temp_dir}")
        
        # Bundle dependencies
        lib_dir = bundle_dependencies(source_dir, temp_dir, verbose)
        if lib_dir is None:
            print("❌ Failed to bundle dependencies")
            return None
        
        # Copy server files
        server_copied, server_missing = copy_server_files(source_dir, temp_dir, verbose)
        
        # Copy essential files
        essential_copied, essential_missing = copy_essential_files(source_dir, temp_dir, verbose)
        
        # Validate manifest
        if not validate_manifest(temp_dir, verbose):
            print("❌ Manifest validation failed")
            return None
        
        # Show summary
        print(f"\n📊 Build Summary:")
        print(f"   📂 Server files: {server_copied} copied")
        print(f"   📋 Essential files: {essential_copied} copied")
        
        if server_missing or essential_missing:
            total_missing = len(server_missing) + len(essential_missing)
            print(f"   ⚠️ Missing files: {total_missing}")
        
        if dry_run:
            print("\n🧪 DRY RUN COMPLETE - Build validation successful")
            return temp_dir
        
        # Create DXT package
        print("\n📦 Creating DXT package...")
        
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
            
            print(f"\n🎉 DXT Package Created Successfully!")
            print(f"📁 File: {dxt_filename}")
            print(f"📊 Size: {size_mb:.2f} MB ({package_size:,} bytes)")
            print(f"📋 Total files: {file_count}")
            
            # Verify package
            with zipfile.ZipFile(dxt_filename, 'r') as dxt:
                lib_files = [f for f in dxt.namelist() if f.startswith('lib/')]
                server_files = [f for f in dxt.namelist() if f.startswith('server/')]
                
                if verbose:
                    print(f"\n📦 Package Contents:")
                    print(f"   📚 Library files: {len(lib_files)}")
                    print(f"   🐍 Server files: {len(server_files)}")
            
            print(f"\n🚀 Ready for installation:")
            print(f"   Drag and drop to Claude Desktop")
            print(f"   Or use: claude install {dxt_filename.name}")
            
            return dxt_filename
            
        except Exception as e:
            print(f"❌ Failed to create DXT package: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='Build Memory Bank v1.4.0 DXT Package')
    parser.add_argument('--output', '-o', help='Output filename for DXT package')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--dry-run', '-d', action='store_true', help='Test build without creating package')
    
    args = parser.parse_args()
    
    result = create_dxt_package(
        output_filename=args.output,
        verbose=args.verbose,
        dry_run=args.dry_run
    )
    
    if result is None:
        sys.exit(1)
    else:
        print("\n✅ Build completed successfully!")

if __name__ == "__main__":
    main()
