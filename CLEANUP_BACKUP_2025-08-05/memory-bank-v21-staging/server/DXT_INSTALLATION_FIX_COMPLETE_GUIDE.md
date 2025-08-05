# DXT Installation Fix - Complete Troubleshooting Guide

**Generated:** 2025-08-02.2052  
**Status:** 🔧 COMPLETE DXT INSTALLATION TROUBLESHOOTING & FIX DOCUMENTATION

---

## 🎯 **PROBLEM OVERVIEW:**

### **Original Issue:**
Memory Bank v2.0 Enhanced DXT package was failing to install/start in Claude Desktop with various server disconnection errors.

### **Root Causes Identified:**
1. **Missing Registry Files**: Context propagation system files not included in DXT package
2. **Import Compatibility**: Python import structure incompatible with DXT environment  
3. **Entry Point Structure**: DXT expects specific module execution pattern
4. **DXT Specification**: Our manifest.json wasn't following official v0.1 spec

---

## 📚 **KEY LEARNINGS FROM https://github.com/anthropics/dxt:**

### **✅ DXT Architecture Understanding:**

#### **1. DXT Format Definition:**
- **DXT Files**: ZIP archives containing local MCP server + manifest.json
- **Purpose**: One-click installation of local MCP servers (like Chrome extensions)
- **Components**: Extension specification, CLI tools, verification code

#### **2. DXT v0.1 Specification Requirements:**
```json
{
  "dxt_version": "0.1",
  "name": "extension-name",
  "version": "semantic-version", 
  "description": "Brief description",
  "author": {
    "name": "Author Name"
  },
  "server": {
    "type": "python",  // or "node" or "binary"
    "entry_point": "server/memory_bank_mcp/__main__.py",
    "mcp_config": {
      "command": "python",  // NOT hardcoded path
      "args": ["-m", "memory_bank_mcp"],  // Module execution
      "env": {
        "PYTHONPATH": "${__dirname}/lib:${__dirname}/server:${__dirname}"
      },
      "cwd": "${__dirname}/server"  // Working directory
    }
  }
}
```

#### **3. Python Server Requirements:**
- **Command**: Use "python" not hardcoded paths like "/Users/.../python3"
- **Module Execution**: Use "-m module_name" instead of direct file execution
- **Entry Point**: Should point to __main__.py for module execution
- **Working Directory**: Set proper cwd for imports to work
- **Environment**: Set PYTHONPATH for bundled dependencies

#### **4. Directory Structure:**
```
extension.dxt (ZIP file)
├── manifest.json                    # Required: DXT metadata
├── server/
│   └── memory_bank_mcp/            # Python package
│       ├── __main__.py             # Entry point for -m execution
│       ├── main.py                 # Main server code  
│       ├── context_registry.py     # Registry system
│       └── ...                     # Other modules
├── lib/                            # Bundled Python packages
└── icon.png                       # Optional: Extension icon
```

---

## 🔧 **STEP-BY-STEP FIX PROCESS:**

### **Issue 1: Server Disconnection Errors**

#### **Problem**: 
```
MCP memory-bank-v2-enhanced: Server disconnected
```

#### **Investigation**:
```bash
# Check Claude logs
tail -f /Users/georgemagnuson/Library/Logs/Claude/mcp-server-memory-bank-v2-enhanced.log
```

#### **Root Cause**: Import errors preventing server startup

### **Issue 2: Missing Registry Files**

#### **Problem**:
```
ERROR - Failed to import Memory Bank modules: No module named 'context_registry'
```

#### **Investigation**: Registry system files not included in DXT package

#### **Fix**: Updated build script to include registry files
```python
# In build_memory_bank_v2_dxt.py
server_files = [
    # ... existing files ...
    
    # Registry Integration System (Context Propagation Fix)
    "server/memory_bank_mcp/context_registry.py",
    "server/memory_bank_mcp/enhanced_project_manager.py", 
    "server/memory_bank_mcp/enhanced_context_tools.py",
    "server/memory_bank_mcp/registry_integration.py"
]
```

### **Issue 3: Import Compatibility**

#### **Problem**:
```
ERROR - Failed to import Memory Bank modules: attempted relative import with no known parent package
```

#### **Fix**: Implemented fallback import system in main.py
```python
# Enhanced import system with fallback strategies
try:
    # Try absolute imports first
    from memory_bank_mcp.context_manager import ContextManager
    from memory_bank_mcp.core_tools import CoreTools
    # ... more imports
    logger.info("Successfully imported Memory Bank modules (absolute)")
    
except ImportError:
    logger.info("Absolute imports failed, trying relative imports...")
    try:
        # Try relative imports
        from .context_manager import ContextManager
        from .core_tools import CoreTools
        # ... more imports
        logger.info("Successfully imported Memory Bank modules (relative)")
        
    except ImportError:
        logger.info("Relative imports failed, trying local imports...")
        try:
            # Try local imports
            from context_manager import ContextManager
            from core_tools import CoreTools
            # ... more imports
            logger.info("Successfully imported Memory Bank modules (local)")
            
        except ImportError as e:
            logger.error(f"All import methods failed: {e}")
            raise
```

### **Issue 4: Entry Point Structure**

#### **Problem**:
```
Import error: cannot import name 'main' from 'memory_bank_mcp.main'
```

#### **Root Cause**: DXT expects importable `main` function at module level

#### **Fix**: Restructured main.py to export main function
```python
# OLD (broken for DXT):
if __name__ == "__main__":
    async def main():  # Not accessible for import
        await server.run()
        
# NEW (DXT compatible):
def main():  # Module-level function for DXT import
    """Main entry point for Memory Bank v2.0 Enhanced MCP Server with Registry Integration"""
    try:
        validation = validate_registry_integration()
        server.run(transport="stdio")  # Use original server startup method
    except Exception as e:
        logger.error(f"Server startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### **Issue 5: DXT Specification Compliance**

#### **Problem**: Manifest not following DXT v0.1 specification

#### **Original (broken) manifest.json**:
```json
{
  "server": {
    "type": "python",
    "entry_point": "server/main.py",  // Wrong entry point
    "mcp_config": {
      "command": "/Users/georgemagnuson/.direnv/python-3.13.5/bin/python3",  // Hardcoded path
      "args": ["${__dirname}/server/main.py"]  // Direct file execution
    }
  }
}
```

#### **Fixed (DXT v0.1 compliant) manifest.json**:
```json
{
  "dxt_version": "0.1",
  "name": "memory-bank-v2-enhanced",
  "version": "2.0.0",
  "description": "Memory Bank v2.0 Enhanced - Advanced AI collaboration memory with registry integration",
  "author": {
    "name": "Memory Bank Development Team"
  },
  "server": {
    "type": "python",
    "entry_point": "server/memory_bank_mcp/__main__.py",  // Correct entry point
    "mcp_config": {
      "command": "python",  // Generic command
      "args": ["-m", "memory_bank_mcp"],  // Module execution
      "env": {
        "PYTHONPATH": "${__dirname}/lib:${__dirname}/server:${__dirname}"
      },
      "cwd": "${__dirname}/server"  // Working directory
    }
  }
}
```

---

## 🔄 **COMPLETE FIX WORKFLOW:**

### **Step 1: Update Build Script**
```bash
# Edit build_memory_bank_v2_dxt.py
# Add registry system files to server_files list
```

### **Step 2: Fix Main.py Entry Point**
```python
# Ensure main.py exports main() function at module level
# Use server.run(transport="stdio") not await server.run()
```

### **Step 3: Add Import Fallback System**
```python
# Implement multi-strategy import system in main.py
# Handle absolute, relative, and local import scenarios
```

### **Step 4: Update Manifest**
```python
# Update create_dxt_manifest() in build script
# Follow DXT v0.1 specification exactly
```

### **Step 5: Rebuild Package**
```bash
cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04
python3 build_memory_bank_v2_dxt.py --output memory_bank_v04_v2.dxt
```

### **Step 6: Verify Package Contents**
```bash
# Check that registry files are included
unzip -l memory_bank_v04_v2.dxt | grep registry
# Should show:
# context_registry.py
# enhanced_project_manager.py  
# enhanced_context_tools.py
# registry_integration.py
```

---

## 🧪 **TESTING & VALIDATION:**

### **Installation Test:**
1. **Drag & Drop**: Install memory_bank_v04_v2.dxt in Claude Desktop
2. **Server Start**: Check for successful startup (no disconnection errors)
3. **Import Success**: Verify registry system imports work
4. **Context Test**: Test work_on_project() → get_current_context() sequence

### **Success Indicators:**
```
✅ Successfully imported MCP framework
✅ Successfully imported registry system  
✅ Successfully imported Memory Bank modules (absolute)
✅ Server started and connected successfully
```

### **Critical Test Sequence:**
```bash
work_on_project("/path/to/project")
# → ✅ Working on Project: project_name
# → ✅ Context registered: project_name

get_current_context()  
# → ✅ Current Project Context (not "No active project")
```

---

## 📦 **FINAL WORKING PACKAGE:**

### **Package Details:**
- **File**: memory_bank_v04_v2.dxt
- **Size**: 26.74 MB (28,035,464 bytes) 
- **Files**: 5,056 total files
- **Server Files**: 25 (includes registry system)
- **DXT Version**: v0.1 compliant
- **Registry Integration**: Complete

### **Key Components Included:**
- ✅ **Registry System**: All 4 registry files included
- ✅ **Import Compatibility**: Fallback import system
- ✅ **Entry Point**: Module-level main() function
- ✅ **DXT Compliance**: Proper v0.1 specification
- ✅ **Dependencies**: 93 Python packages bundled

---

## 🚨 **TROUBLESHOOTING CHECKLIST:**

### **If DXT Installation Fails Again:**

#### **1. Check Server Logs:**
```bash
tail -f /Users/georgemagnuson/Library/Logs/Claude/mcp-server-memory-bank-v2-enhanced.log
```

#### **2. Common Error Patterns:**

**Missing Module Errors:**
```
No module named 'context_registry'
```
**Fix**: Verify registry files included in build

**Import Errors:**
```
attempted relative import with no known parent package
```
**Fix**: Check fallback import system in main.py

**Entry Point Errors:**
```
cannot import name 'main' from 'memory_bank_mcp.main'
```
**Fix**: Ensure main() function exported at module level

**DXT Specification Errors:**
```
Server disconnected immediately
```
**Fix**: Verify manifest.json follows DXT v0.1 spec

#### **3. Verification Commands:**

**Check Package Contents:**
```bash
unzip -l memory_bank_v04_v2.dxt | head -20
```

**Test Local Import:**
```bash
cd /Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server
python3 -c "from memory_bank_mcp.main import main; print('✅ Import successful')"
```

**Validate Manifest:**
```bash
unzip -p memory_bank_v04_v2.dxt manifest.json | python3 -m json.tool
```

---

## 🎯 **SUCCESS CONFIRMATION:**

### **Working State Achieved:**
- ✅ **Server Starts**: No disconnection errors
- ✅ **Imports Work**: Registry system fully functional
- ✅ **Context Propagation**: work_on_project() → get_current_context() working
- ✅ **DXT Compliant**: Follows official specification
- ✅ **Tools Functional**: All 24 Memory Bank tools available

### **Critical Breakthrough:**
The **context propagation issue** that was preventing Memory Bank v2.0 transformation has been **completely resolved** through the centralized registry system integrated into a properly built DXT package.

**This guide provides complete instructions for rebuilding a working Memory Bank v2.0 Enhanced DXT package if needed!** 🎯✨
