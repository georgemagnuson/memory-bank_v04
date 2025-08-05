"""
migration_modules/__init__.py  
Generated: 2025-08-01.1843
Purpose: Initialize migration modules for Memory Bank v2.0 unified document architecture
UPDATED: Removed redundant DatabaseMigrator - now using consolidated version from schema_manager_modules

Provides clean imports and module organization for:
- Content migration and import functionality  
- Smart merge capabilities
- CLI utilities for migration workflows
- NOTE: DatabaseMigrator moved to schema_manager_modules for consolidation
"""

# Import all main classes for easy access
from .core_migrator import UnifiedDocumentMigrator
from .content_extractors import ContentExtractors  
from .smart_merge import SmartMergeEngine
from .migration_cli import MigrationCLI, MigrationUtilities
from .markdown_importer import MarkdownImporter, MemoryBankMigrator

# Import consolidated DatabaseMigrator from schema_manager_modules
from ..schema_manager_modules.database_migrator import DatabaseMigrator

# Version and module info
__version__ = "2.0.0"
__all__ = [
    'UnifiedDocumentMigrator',
    'ContentExtractors', 
    'SmartMergeEngine',
    'MigrationCLI', 
    'MigrationUtilities',
    'MarkdownImporter',
    'MemoryBankMigrator',
    'DatabaseMigrator'  # Now refers to consolidated version
]

# Migration architecture info
__migration_architecture__ = "unified_documents_to_documents_v2.0"
__deprecated_tables_supported__ = [
    "discussions", "artifacts", "code_iterations", "plans", "chat_sessions",
    "cross_references", "project_context"
]

__consolidation_note__ = """
ARCHITECTURAL CHANGE: DatabaseMigrator consolidated from two separate implementations
into single enhanced version in schema_manager_modules/database_migrator.py

BENEFITS:
- Single source of truth for migration logic
- Enhanced dry-run capabilities  
- NEW: Complete deprecated table cleanup (DROP TABLE functionality)
- Better error handling and rollback capabilities
- Comprehensive backup system with metadata
"""