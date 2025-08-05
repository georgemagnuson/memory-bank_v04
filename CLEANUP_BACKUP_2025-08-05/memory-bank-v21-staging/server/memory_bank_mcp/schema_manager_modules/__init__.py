#!/usr/bin/env python3
"""
server/memory_bank_mcp/schema_manager_modules/__init__.py
Generated: 2025-07-29.0125
Purpose: Schema manager modules package for Memory Bank v2.0

Provides modular components for database schema management:
- DatabaseVersionDetector: Version detection and schema analysis
- SchemaTemplateManager: Template storage and retrieval
- DatabaseMigrator: Migration operations and backup management
"""

# Import all public classes for easy access
from .database_version_detector import DatabaseVersionDetector, SchemaInfo
from .schema_template_manager import SchemaTemplateManager
from .database_migrator import DatabaseMigrator, MigrationResult

# Package metadata
__version__ = "2.0.0"
__author__ = "Memory Bank Development Team"

# Export all classes for schema_manager.py
__all__ = [
    'DatabaseVersionDetector',
    'SchemaInfo', 
    'SchemaTemplateManager',
    'DatabaseMigrator',
    'MigrationResult'
]
