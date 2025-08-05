"""
Migration Manager Modules
=========================

Modular components for migration management operations.

Modules:
- backup_manager: Handles database backup operations
- migration_orchestrator: Orchestrates the complete migration process
- work_on_project_handler: Handles enhanced work_on_project functionality
"""

from .backup_manager import BackupManager
from .migration_orchestrator import MigrationOrchestrator
from .work_on_project_handler import WorkOnProjectHandler

__all__ = [
    'BackupManager',
    'MigrationOrchestrator',
    'WorkOnProjectHandler'
]
