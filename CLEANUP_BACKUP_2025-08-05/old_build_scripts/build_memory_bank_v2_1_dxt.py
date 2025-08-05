#!/usr/bin/env python3
"""
Memory Bank v2.1 Enhanced DXT Package Builder
Filename: build_memory_bank_v2_1_dxt.py
Generated: 2025-08-03.0130
Purpose: Build production-ready DXT package for Memory Bank v2.1 Enhanced with importance-weighted search

NEW v2.1 FEATURES:
- Importance-weighted search system (0-10 scale)
- FTS5 integration with ranking boost
- Natural language importance parsing
- Enhanced search performance with BM25 weighting
- Updated schema with importance column

UPDATED FOR ANTHROPIC DXT v0.1 SPECIFICATION:
- Fixed duplicate manifest entries
- Modern DXT v0.1 manifest format
- Proper Python server configuration  
- Registry integration system
- Consolidated Memory Bank v2.1 Enhanced modules

Usage:
    python3 build_memory_bank_v2_1_dxt.py                    # Standard build
    python3 build_memory_bank_v2_1_dxt.py --verbose          # Verbose output
    python3 build_memory_bank_v2_1_dxt.py --dry-run          # Test without building
    python3 build_memory_bank_v2_1_dxt.py --output custom.dxt # Custom output name
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
    """Create DXT v0.1 compliant manifest.json for Memory Bank v2.1 Enhanced"""
    manifest = {
        "dxt_version": "0.1",
        "name": "memory-bank-v2-1-enhanced", 
        "version": "2.1.0",
        "description": "Memory Bank v2.1 Enhanced - Advanced AI collaboration memory with importance-weighted search",
        "long_description": "Memory Bank v2.1 Enhanced provides the most advanced persistent AI collaboration memory system with importance-weighted search (0-10 scale), FTS5 integration, natural language importance parsing, context propagation registry, enhanced schema management, and comprehensive tool ecosystem. Features automatic migration workflow, centralized context registry for proper tool communication, enhanced backup system with metadata, and seamless DXT deployment. Production-ready with comprehensive error handling, smart migration analysis, and live testing capabilities.",
        
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
                "command": "python",  # Generic command, not hardcoded path
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
        
        "tools": [
            {"name": "memory_bank_help", "description": "Show comprehensive help for Memory Bank v2.1 Enhanced"},
            {"name": "work_on_project", "description": "Switch to working on a specific project with memory-bank integration and schema auto-migration"},
            {"name": "create_context", "description": "Create a new project context"},
            {"name": "switch_context", "description": "Switch to an existing project context"},
            {"name": "save_info", "description": "Save information to current context with importance ranking"},
            {"name": "search_info", "description": "Search saved information with importance-weighted ranking"},
            {"name": "save_document", "description": "Save document with importance level (0-10 scale)"},
            {"name": "search_documents", "description": "Search documents with FTS5 and importance weighting"},
            {"name": "execute_sql", "description": "Execute SQL queries on project database"},
            {"name": "show_schema", "description": "Display current database schema"},
            {"name": "list_contexts", "description": "List all available project contexts"},
            {"name": "get_current_context", "description": "Get current project context and status"},
            {"name": "analyze_database", "description": "Analyze database structure and statistics"},
            {"name": "show_project_info", "description": "Show current project information"},
            {"name": "migrate_to_v2", "description": "Migrate database from v1.x to v2.0 schema"},
            {"name": "create_backup", "description": "Create database backup"},
            {"name": "restore_backup", "description": "Restore from database backup"},
            {"name": "check_migration_status", "description": "Check migration completion status"}
        ],
        
        "keywords": [
            "memory", "collaboration", "AI", "context", "search", "importance", "FTS5", 
            "database", "sqlite", "mcp", "claude", "persistence", "registry"
        ],
        
        "categories": [
            "productivity",
            "development-tools", 
            "collaboration",
            "database"
        ],
        
        "permissions": {
            "file_system": {
                "read": True,
                "write": True,
                "reason": "Read/write project databases and context files"
            }
        },
        
        "requirements": {
            "python": ">=3.8",
            "claude_desktop": ">=1.0.0"
        }
    }
    
    return manifest

def get_server_files():
    """Define all server files to include in DXT package - Updated for actual file structure"""
    base_path = "server/memory_bank_mcp"
    
    server_files = [
        # Core MCP Server Files
        f"{base_path}/__init__.py",
        f"{base_path}/__main__.py",
        f"{base_path}/main.py",
        
        # Enhanced Core System (v2.1)
        f"{base_path}/database.py",
        f"{base_path}/context_manager.py",
        f"{base_path}/core_tools.py",
        f"{base_path}/content_tools.py",
        f"{base_path}/migration_tools.py",
        f"{base_path}/backup_tools.py",
        
        # Registry Integration System (Context Propagation Fix)
        f"{base_path}/context_registry.py",
        f"{base_path}/enhanced_project_manager.py", 
        f"{base_path}/enhanced_context_tools.py",
        f"{base_path}/registry_integration.py",
        
        # Additional Tools
        f"{base_path}/project_manager.py",
        f"{base_path}/project_tools.py",
        f"{base_path}/schema_manager.py",
        f"{base_path}/sql_tools.py",
        f"{base_path}/migration.py",
        
        # Core Tools Modules (actual files)
        f"{base_path}/core_tools_modules/__init__.py",
        f"{base_path}/core_tools_modules/content_search_engine.py",
        f"{base_path}/core_tools_modules/content_extractor.py",
        f"{base_path}/core_tools_modules/database_interface.py",
        
        # Content Tools Modules (actual files)
        f"{base_path}/content_tools_modules/__init__.py",
        f"{base_path}/content_tools_modules/search_engine.py",
        f"{base_path}/content_tools_modules/fts_manager.py",
        f"{base_path}/content_tools_modules/import_manager.py",
        
        # Migration Tools Modules (actual files)
        f"{base_path}/migration_tools_modules/__init__.py",
        f"{base_path}/migration_tools_modules/migration_analyzer.py",
        f"{base_path}/migration_tools_modules/content_importer.py",
        f"{base_path}/migration_tools_modules/project_migrator.py",
        
        # Backup Tools Modules
        f"{base_path}/backup_tools_modules/__init__.py",
        f"{base_path}/backup_tools_modules/backup_manager.py",
        f"{base_path}/backup_tools_modules/template_manager.py",
        
        # Schema Manager Modules
        f"{base_path}/schema_manager_modules/__init__.py",
        f"{base_path}/schema_manager_modules/schema_template_manager.py",
        
        # Migration Modules
        f"{base_path}/migration_modules/__init__.py",
        f"{base_path}/migration_modules/content_extractors.py",
        f"{base_path}/migration_modules/smart_merge.py",
        f"{base_path}/migration_modules/markdown_importer.py",
        
        # SQL Tools Modules
        f"{base_path}/sql_tools_modules/__init__.py",
        
        # Project Tools Modules
        f"{base_path}/project_tools_modules/__init__.py",
        
        # Schema Templates (v2.1 with importance)
        f"{base_path}/context_template_v2.0.ddl",
        f"{base_path}/context_template_v2.0.db",
        f"{base_path}/schema_v2_0_template.sql",
        
        # Version Detection and Utilities
        f"{base_path}/schema_version_detector.py"
    ]
    
    return server_files

def create_v2_1_modules():
    """Create new v2.1 modules for importance-weighted search"""
    modules = {}
    
    # Enhanced search engine with importance weighting
    modules["importance_search_engine.py"] = '''#!/usr/bin/env python3
"""
importance_search_engine.py
Generated: 2025-08-03.0130
Purpose: Enhanced search engine with importance-weighted ranking for Memory Bank v2.1

Features:
- FTS5 integration with importance boosting
- BM25 ranking with importance multiplier
- Natural language importance parsing
- Advanced search operators
"""

import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ImportanceWeightedSearchEngine:
    """Enhanced search engine with importance ranking for v2.1"""
    
    def __init__(self, context_manager):
        self.context_manager = context_manager
        self.logger = logger
    
    def search_with_importance(self, query: str, min_importance: int = 0, 
                             limit: int = 20) -> List[Dict[str, Any]]:
        """Search with importance-weighted ranking"""
        try:
            conn = sqlite3.connect(self.context_manager.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Enhanced FTS query with importance weighting
            cursor.execute("""
                SELECT 
                    d.uuid, d.title, d.document_type, d.importance, d.created_at,
                    snippet(documents_fts, 1, '<mark>', '</mark>', '...', 64) as highlighted_content,
                    bm25(documents_fts) as base_rank,
                    (bm25(documents_fts) * (d.importance + 1)) as weighted_rank
                FROM documents_fts fts
                JOIN documents d ON fts.rowid = d.rowid
                WHERE documents_fts MATCH ? 
                AND d.project_uuid = ? 
                AND d.status = 'active'
                AND d.importance >= ?
                ORDER BY weighted_rank DESC, d.importance DESC
                LIMIT ?
            """, (query, self.context_manager.project_uuid, min_importance, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'uuid': row['uuid'],
                    'title': row['title'],
                    'document_type': row['document_type'],
                    'importance': row['importance'],
                    'highlighted_content': row['highlighted_content'],
                    'base_rank': row['base_rank'],
                    'weighted_rank': row['weighted_rank'],
                    'created_at': row['created_at']
                })
            
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"Importance search failed: {e}")
            return []
    
    def get_importance_icon(self, importance: int) -> str:
        """Get emoji icon for importance level"""
        if importance >= 9:
            return "🔥"  # Vital/Critical
        elif importance >= 7:
            return "⭐"  # Important
        elif importance >= 5:
            return "📋"  # Normal
        elif importance >= 3:
            return "📝"  # Low
        else:
            return "💤"  # Very low/ignore
'''
    
    # Natural language importance parser
    modules["natural_language_parser.py"] = '''#!/usr/bin/env python3
"""
natural_language_parser.py
Generated: 2025-08-03.0130
Purpose: Natural language parsing for importance levels in Memory Bank v2.1

Features:
- Parse "mark it critical information, level 10" style commands
- Extract importance from natural language
- Support multiple importance indicators
"""

import re
from typing import Optional

class NaturalLanguageImportanceParser:
    """Parse importance levels from natural language instructions"""
    
    # Natural language importance patterns
    IMPORTANCE_PATTERNS = {
        r'(?i)\\b(critical|vital|essential|crucial)\\b': 10,
        r'(?i)\\b(very\\s+important|high\\s+priority)\\b': 9,
        r'(?i)\\b(important|significant|key)\\b': 8,
        r'(?i)\\b(useful|relevant|moderate)\\b': 6,
        r'(?i)\\b(low\\s+priority|minor|trivial)\\b': 3,
        r'(?i)\\b(ignore|skip|unimportant)\\b': 0,
        r'(?i)\\blevel\\s+(\\d+)\\b': None,  # Extract explicit level
        r'(?i)\\bimportance\\s+(\\d+)\\b': None,  # Extract explicit importance
        r'(?i)\\bpriority\\s+(\\d+)\\b': None,  # Extract explicit priority
    }
    
    # Document type importance defaults
    DOCUMENT_TYPE_IMPORTANCE = {
        'critical_technique': 10,    # Vital
        'decision': 9,               # Very high
        'plan': 8,                   # High
        'document': 7,               # Important
        'code': 6,                   # Above normal
        'discussion': 6,             # Above normal
        'project_management': 5,     # Normal
        'migration_report': 5,       # Normal
        'migration_test': 4,         # Below normal
        'markdown': 4,               # Below normal
        'note': 3,                   # Low
        'default': 5                 # Normal fallback
    }
    
    def parse_importance(self, instruction: str, document_type: str = None) -> int:
        """Parse importance from natural language instruction"""
        if not instruction:
            return self.get_type_default_importance(document_type)
        
        instruction_lower = instruction.lower()
        
        # Check for explicit numeric levels first
        for pattern, _ in self.IMPORTANCE_PATTERNS.items():
            if 'level' in pattern or 'importance' in pattern or 'priority' in pattern:
                match = re.search(pattern, instruction)
                if match:
                    try:
                        level = int(match.group(1))
                        return max(0, min(10, level))  # Clamp to 0-10 range
                    except (ValueError, IndexError):
                        continue
        
        # Check for text-based importance indicators
        for pattern, importance in self.IMPORTANCE_PATTERNS.items():
            if importance is not None:  # Skip the numeric extraction patterns
                if re.search(pattern, instruction):
                    return importance
        
        # Fall back to document type default
        return self.get_type_default_importance(document_type)
    
    def get_type_default_importance(self, document_type: str) -> int:
        """Get default importance for document type"""
        if not document_type:
            return self.DOCUMENT_TYPE_IMPORTANCE['default']
        return self.DOCUMENT_TYPE_IMPORTANCE.get(document_type, self.DOCUMENT_TYPE_IMPORTANCE['default'])
    
    def get_importance_label(self, importance: int) -> str:
        """Get human-readable importance label"""
        labels = {
            10: "VITAL",
            9: "VERY HIGH", 
            8: "HIGH",
            7: "IMPORTANT",
            6: "ABOVE NORMAL",
            5: "NORMAL",
            4: "BELOW NORMAL",
            3: "LOW",
            2: "VERY LOW",
            1: "MINIMAL",
            0: "IGNORE"
        }
        return labels.get(importance, "NORMAL")
'''
    
    return modules

def bundle_dependencies(temp_dir):
    """Bundle Python dependencies by copying from working .venv"""
    lib_dir = os.path.join(temp_dir, "lib")
    os.makedirs(lib_dir, exist_ok=True)
    
    print("📦 Bundling Python dependencies...")
    
    # Copy dependencies from our working .venv site-packages
    venv_site_packages = ".venv/lib/python3.13/site-packages"
    
    if os.path.exists(venv_site_packages):
        print(f"   📁 Copying from {venv_site_packages}")
        
        # Copy all packages from venv site-packages
        package_count = 0
        for item in os.listdir(venv_site_packages):
            source_item = os.path.join(venv_site_packages, item)
            dest_item = os.path.join(lib_dir, item)
            
            # Skip private/system packages
            if item.startswith('_') or item.startswith('.'):
                continue
                
            if os.path.isdir(source_item):
                if not os.path.exists(dest_item):
                    shutil.copytree(source_item, dest_item)
                    package_count += 1
                    print(f"   ✅ Copied package: {item}")
            elif item.endswith('.py'):
                shutil.copy2(source_item, dest_item)
                print(f"   ✅ Copied module: {item}")
        
        print(f"   ✅ Dependencies bundled successfully ({package_count} packages)")
        
    else:
        print(f"   ❌ .venv site-packages not found at {venv_site_packages}")
        
        # Fallback: Try alternative Python versions
        alt_paths = [
            ".venv/lib/python3.12/site-packages",
            ".venv/lib/python3.11/site-packages", 
            ".venv/lib/python3.10/site-packages"
        ]
        
        found_venv = False
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                print(f"   🔄 Found alternative venv: {alt_path}")
                venv_site_packages = alt_path
                found_venv = True
                break
        
        if found_venv:
            # Copy from alternative venv
            package_count = 0
            for item in os.listdir(venv_site_packages):
                source_item = os.path.join(venv_site_packages, item)
                dest_item = os.path.join(lib_dir, item)
                
                if item.startswith('_') or item.startswith('.'):
                    continue
                    
                if os.path.isdir(source_item):
                    if not os.path.exists(dest_item):
                        shutil.copytree(source_item, dest_item)
                        package_count += 1
                        print(f"   ✅ Copied package: {item}")
                elif item.endswith('.py'):
                    shutil.copy2(source_item, dest_item)
                    print(f"   ✅ Copied module: {item}")
            
            print(f"   ✅ Dependencies bundled from alternative venv ({package_count} packages)")
        else:
            # Final fallback: minimal pip install
            print("   🔄 Fallback: Installing minimal dependencies with pip...")
            minimal_deps = ["aiosqlite", "mcp"]
            
            for dep in minimal_deps:
                try:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", 
                        "--target", lib_dir, 
                        dep
                    ], check=True, capture_output=True, text=True)
                    print(f"   ✅ Installed: {dep}")
                except subprocess.CalledProcessError as e:
                    print(f"   ⚠️  Failed to install {dep}: {e}")
    
    return lib_dir

def build_dxt_package(output_file="memory_bank_v2_1_enhanced.dxt", verbose=False, dry_run=False):
    """Build the complete DXT package for Memory Bank v2.1 Enhanced"""
    
    print("🚀 Building Memory Bank v2.1 Enhanced DXT Package...")
    print(f"📦 Output: {output_file}")
    
    if dry_run:
        print("🧪 DRY RUN MODE - No files will be created")
        return True
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"📁 Working directory: {temp_dir}")
        
        # Create manifest.json
        manifest = create_dxt_manifest()
        manifest_path = os.path.join(temp_dir, "manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print("✅ Created manifest.json")
        
        # Copy icon
        icon_src = "icon.png"
        if os.path.exists(icon_src):
            shutil.copy2(icon_src, os.path.join(temp_dir, "icon.png"))
            print("✅ Copied icon.png")
        
        # Create server directory structure
        server_root = os.path.join(temp_dir, "server")
        server_mcp_dir = os.path.join(server_root, "memory_bank_mcp")
        os.makedirs(server_mcp_dir, exist_ok=True)
        
        # Copy entire server/memory_bank_mcp directory
        source_server_dir = "server/memory_bank_mcp"
        if os.path.exists(source_server_dir):
            # Copy all files and subdirectories
            for item in os.listdir(source_server_dir):
                source_item = os.path.join(source_server_dir, item)
                dest_item = os.path.join(server_mcp_dir, item)
                
                if os.path.isdir(source_item):
                    shutil.copytree(source_item, dest_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_item, dest_item)
            
            print(f"✅ Copied entire server directory structure")
        else:
            print(f"❌ Source server directory not found: {source_server_dir}")
            return False
        
        # Create v2.1 enhancement modules
        v2_1_modules = create_v2_1_modules()
        for filename, content in v2_1_modules.items():
            module_path = os.path.join(server_mcp_dir, filename)
            with open(module_path, 'w') as f:
                f.write(content)
            print(f"✅ Created v2.1 module: {filename}")
        
        # Bundle dependencies
        lib_dir = bundle_dependencies(temp_dir)
        
        # Create __main__.py if it doesn't exist
        main_py_path = os.path.join(server_mcp_dir, "__main__.py")
        if not os.path.exists(main_py_path):
            main_py_content = '''#!/usr/bin/env python3
"""
__main__.py - Entry point for Memory Bank v2.1 Enhanced MCP Server
"""

from .main import main

if __name__ == "__main__":
    main()
'''
            with open(main_py_path, 'w') as f:
                f.write(main_py_content)
            print("✅ Created __main__.py entry point")
        
        # Create DXT package
        print("📦 Creating DXT package...")
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all files from temp directory
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arc_path)
                    
                    if verbose:
                        print(f"  📦 Added: {arc_path}")
        
        # Get package statistics
        package_size = os.path.getsize(output_file)
        with zipfile.ZipFile(output_file, 'r') as zipf:
            file_count = len(zipf.namelist())
        
        print(f"✅ DXT package created successfully!")
        print(f"📊 Package size: {package_size:,} bytes ({package_size/1024/1024:.2f} MB)")
        print(f"📊 Total files: {file_count}")
        print(f"📦 Output: {output_file}")
        
        return True

def main():
    """Main entry point for DXT builder"""
    parser = argparse.ArgumentParser(description="Build Memory Bank v2.1 Enhanced DXT package")
    parser.add_argument("--output", "-o", default="memory_bank_v2_1_enhanced.dxt", 
                       help="Output DXT filename")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Test build without creating package")
    
    args = parser.parse_args()
    
    try:
        success = build_dxt_package(
            output_file=args.output,
            verbose=args.verbose,
            dry_run=args.dry_run
        )
        
        if success:
            print("🎉 Build completed successfully!")
            if not args.dry_run:
                print(f"🎯 Ready to install: {args.output}")
        else:
            print("❌ Build failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Build error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
