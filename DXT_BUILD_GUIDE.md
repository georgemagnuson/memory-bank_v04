# Memory Bank v1.4.0 - DXT Build Instructions
**Generated:** 2025-07-28.0027  
**Purpose:** Complete guide for building DXT packages from source

---

## 📋 **Overview**

DXT (Desktop eXtension Tool) packages allow Memory Bank to be distributed as self-contained bundles that include all dependencies and can be easily installed in Claude Desktop or other MCP clients.

## 🏗️ **Build Process**

### **Automated Build Script**

The recommended way to build a DXT package is using the automated build script:

```bash
# Navigate to project directory
cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04

# Run the build script
python3 build_dxt.py
```

### **Manual Build Process**

If you need to build manually or customize the process:

#### **1. Prepare Build Environment**
```bash
# Ensure all dependencies are current
pip install -r requirements.txt

# Verify project structure
python3 -c "import server.memory_bank_mcp.main; print('✅ Server imports OK')"
```

#### **2. Bundle Dependencies**
```bash
# Create temporary lib directory
mkdir -p temp_build/lib

# Install dependencies into lib/
pip install --target temp_build/lib -r requirements.txt
```

#### **3. Copy Source Files**
```bash
# Copy server code
cp -r server/ temp_build/
cp -r memory-bank/ temp_build/

# Copy essential files
cp manifest.json temp_build/
cp icon.png temp_build/
cp README.md temp_build/
cp requirements.txt temp_build/
```

#### **4. Create DXT Package**
```bash
# Create ZIP archive with .dxt extension
cd temp_build
zip -r ../memory-bank-v04-enhanced-v1.4.0.dxt ./*

# Clean up
cd ..
rm -rf temp_build
```

---

## 🔧 **Build Script Reference**

### **Current Build Script**

Create `build_dxt.py` in the project root:

```python
#!/usr/bin/env python3
"""
Memory Bank v1.4.0 DXT Package Builder
Filename: build_dxt.py
Generated: 2025-07-28.0027
Purpose: Build production-ready DXT package for Memory Bank v1.4.0
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
    """Bundle Python dependencies into lib/ directory"""
    print("📦 Bundling Python dependencies...")
    
    lib_dir = temp_dir / "lib"
    lib_dir.mkdir(exist_ok=True)
    
    requirements_file = source_dir / "requirements.txt"
    
    if requirements_file.exists():
        print(f"   Installing from {requirements_file}")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install",
            "--target", str(lib_dir),
            "--requirement", str(requirements_file),
            "--upgrade", "--force-reinstall"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Dependencies bundled successfully")
        else:
            print(f"   ⚠️ Some dependencies may be missing: {result.stderr}")
    
    return lib_dir

def copy_server_files(source_dir, temp_dir):
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
    for file_path in server_files:
        source_file = source_dir / file_path
        if source_file.exists():
            dest_file = temp_dir / file_path
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, dest_file)
            copied_count += 1
        else:
            print(f"   ⚠️ Missing: {file_path}")
    
    print(f"   ✅ Copied {copied_count}/{len(server_files)} server files")
    return copied_count

def copy_essential_files(source_dir, temp_dir):
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
    for file_path in essential_files:
        source_file = source_dir / file_path
        if source_file.exists():
            dest_file = temp_dir / file_path
            shutil.copy2(source_file, dest_file)
            copied_count += 1
            print(f"   ✅ Copied: {file_path}")
    
    return copied_count

def create_dxt_package():
    """Create the DXT package"""
    
    print("🚀 Building Memory Bank v1.4.0 DXT Package...")
    
    source_dir = Path("/Users/georgemagnuson/Documents/GitHub/memory-bank_v04")
    dxt_filename = source_dir / "memory-bank-v04-enhanced-v1.4.0.dxt"
    
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        print(f"📁 Working directory: {temp_dir}")
        
        # Bundle dependencies
        bundle_dependencies(source_dir, temp_dir)
        
        # Copy server files
        copy_server_files(source_dir, temp_dir)
        
        # Copy essential files
        copy_essential_files(source_dir, temp_dir)
        
        # Create DXT package
        print("📦 Creating DXT package...")
        with zipfile.ZipFile(dxt_filename, 'w', zipfile.ZIP_DEFLATED) as dxt:
            for item in temp_dir.rglob("*"):
                if item.is_file():
                    arcname = item.relative_to(temp_dir)
                    dxt.write(item, arcname)
        
        # Report results
        package_size = dxt_filename.stat().st_size
        size_mb = package_size / (1024 * 1024)
        
        print(f"\n🎉 DXT Package Created Successfully!")
        print(f"📁 File: {dxt_filename}")
        print(f"📊 Size: {size_mb:.2f} MB")
        
        with zipfile.ZipFile(dxt_filename, 'r') as dxt:
            file_count = len(dxt.infolist())
            print(f"📋 Total files: {file_count}")
        
        return dxt_filename

if __name__ == "__main__":
    create_dxt_package()
```

---

## 📦 **Package Structure**

A complete DXT package contains:

```
memory-bank-v04-enhanced-v1.4.0.dxt
├── manifest.json                 # MCP configuration
├── icon.png                     # Package icon
├── README.md                    # Documentation
├── requirements.txt             # Dependencies list
├── lib/                        # Bundled dependencies
│   ├── mcp/                   # MCP framework
│   ├── aiosqlite/            # SQLite async
│   ├── pydantic/             # Data validation
│   └── ...                   # Other dependencies
└── server/                     # Source code
    ├── main.py               # Entry point
    └── memory_bank_mcp/      # Core modules
        ├── main.py          # MCP server
        ├── database.py      # Database layer
        ├── core_tools.py    # Core tools
        ├── sql_tools.py     # SQL tools
        ├── project_tools.py # Project tools
        ├── content_tools.py # Content tools
        ├── migration_tools.py # Migration tools
        └── backup_tools.py  # Backup tools
```

---

## ⚙️ **Build Configuration**

### **Manifest.json Key Fields**

- **version**: Must match current release (1.4.0)
- **server.mcp_config.command**: Python interpreter path
- **server.mcp_config.env.PYTHONPATH**: Includes bundled lib/ directory
- **tools**: All 30 available tools listed

### **Python Path Configuration**

The DXT package uses:
```
PYTHONPATH: ${__dirname}/lib:${__dirname}/server:${__dirname}
```

This ensures:
- Bundled dependencies are found first (`lib/`)
- Server modules are accessible (`server/`)
- Package root is available (`${__dirname}`)

---

## 🧪 **Testing the Build**

### **Verify Package Contents**
```bash
# List package contents
unzip -l memory-bank-v04-enhanced-v1.4.0.dxt

# Extract and test locally
unzip memory-bank-v04-enhanced-v1.4.0.dxt -d test_extract/
cd test_extract/
python3 server/main.py --help
```

### **Installation Test**
```bash
# Test with Claude Desktop
# 1. Drag and drop DXT file to Claude Desktop
# 2. Verify all 30 tools appear
# 3. Test basic functionality:
work_on_project("/tmp/test_project")
memory_bank_help()
```

---

## 🚨 **Troubleshooting**

### **Common Build Issues**

**Missing Dependencies**
- Ensure `requirements.txt` is current
- Check Python version compatibility (3.8+)

**Import Errors**  
- Verify PYTHONPATH configuration in manifest.json
- Check server module structure

**Package Size Too Large**
- Exclude unnecessary files with `.dxtignore`
- Remove dev dependencies from requirements.txt

### **Build Validation**

Before distribution, verify:
- [ ] All 30 tools listed in manifest.json
- [ ] Dependencies bundled in lib/
- [ ] Server modules copied correctly
- [ ] Package imports successfully
- [ ] Memory Bank initializes properly

---

## 📝 **Build History**

### **Previous Build Scripts**

Historical build scripts are archived in `archive/old_versions/`:
- `build_v1.4.0_complete_dxt.py` - Complete Phase 3 build
- `build_v1.4.0_fixed_dxt.py` - Bug fix build  
- `build_v1.4.0_dxt.py` - Initial v1.4.0 build

These can be referenced for advanced build customization.

---

## 🎯 **Quick Build Commands**

```bash
# Standard build
python3 build_dxt.py

# Build with custom output location
python3 build_dxt.py --output /path/to/output.dxt

# Build with verbose logging
python3 build_dxt.py --verbose

# Verify build without creating package
python3 build_dxt.py --dry-run
```

---

**Memory Bank v1.4.0** - Professional DXT packaging for seamless distribution! 📦
