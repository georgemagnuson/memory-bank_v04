"""
Memory Bank v2.1 Migration System
==================================

Consolidated migration system for upgrading any Memory Bank database to clean v2.1 schema.

Key Features:
- Table count-based version detection
- Complete content table consolidation
- Legacy table cleanup
- Automatic backup and recovery
- Integration with existing Memory Bank systems

Modules:
- version_detector: Enhanced version detection with table count analysis
- content_migrator: Handles migration of all content tables to documents
- schema_creator: Creates clean v2.1 database schemas
- integration: Integration helpers for existing Memory Bank systems

Usage:
    from migration_v21 import MigrationManager
    
    manager = MigrationManager()
    result = manager.migrate_to_v21("/path/to/context.db")
"""

from .version_detector import VersionDetector, DatabaseInfo
from .content_migrator import ContentMigrator  
from .schema_creator import SchemaCreator
from .migration_manager import MigrationManager
from .integration import integrate_with_memory_bank

__version__ = "2.1.0"
__all__ = [
    'MigrationManager',
    'VersionDetector', 
    'ContentMigrator',
    'SchemaCreator',
    'DatabaseInfo',
    'integrate_with_memory_bank'
]
