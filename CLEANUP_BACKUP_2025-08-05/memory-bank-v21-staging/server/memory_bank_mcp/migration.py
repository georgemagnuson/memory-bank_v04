"""
memory_bank_mcp/migration.py
Generated: 2025-07-29.2316  
Purpose: Simplified migration interface for Memory Bank v2.0 unified document architecture
Delegates to modular migration system while maintaining API compatibility

This file replaces the original 1778-line migration.py with a clean modular approach.
All deprecated table references have been removed for v2.0 compatibility.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import modular migration system
from .migration_modules import (
    UnifiedDocumentMigrator,
    ContentExtractors,
    SmartMergeEngine, 
    MigrationCLI,
    MigrationUtilities,
    MarkdownImporter,
    MemoryBankMigrator  # Legacy compatibility
)

logger = logging.getLogger("memory_bank_mcp.migration")


class SmartMergeMigrator:
    """
    v2.0 Migration interface with unified document architecture
    
    This replaces the original SmartMergeMigrator class with a clean implementation
    that delegates to the modular migration system.
    
    Key v2.0 Changes:
    - Uses unified documents table instead of discussions/artifacts/plans tables
    - Maintains Smart Merge capabilities
    - Eliminates all deprecated table references
    - Provides modular, maintainable architecture
    """
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.memory_bank_path = project_path / "memory-bank"
        self._context_manager = None
        
        logger.info(f"Smart Merge Migrator v2.0 initialized for: {project_path}")
    
    def _get_context_manager(self):
        """Lazy initialization of context manager"""
        if not self._context_manager:
            from .context_manager import ContextManager
            self._context_manager = ContextManager(self.project_path)
        return self._context_manager
    
    async def migrate_project(self, dry_run: bool = False, force: bool = False) -> Dict[str, Any]:
        """
        Migrate project files to unified document architecture
        
        Args:
            dry_run: If True, analyze files but don't write to database
            force: If True, re-migrate all files regardless of timestamps
            
        Returns:
            Migration report with unified document statistics
        """
        try:
            # Use the modular migration system
            context_manager = self._get_context_manager()
            migrator = UnifiedDocumentMigrator(self.project_path, context_manager)
            
            return await migrator.migrate_project(dry_run=dry_run, force=force)
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'project_path': str(self.project_path)
            }


# =============================================================================
# CLI INTERFACE AND UTILITY FUNCTIONS
# =============================================================================

def migrate_project_cli(project_path: str, dry_run: bool = False, 
                        force: bool = False) -> Dict[str, Any]:
    """
    CLI interface for migrating a project to unified document architecture
    
    Args:
        project_path: Path to the project directory
        dry_run: If True, analyze files but don't write to database
        force: If True, re-migrate all files regardless of timestamps
        
    Returns:
        Migration report
    """
    return MigrationCLI.migrate_project_cli(project_path, dry_run, force)


def discover_and_import_all_markdown(directory_path: str, 
                                   exclude_patterns: List[str] = None,
                                   max_file_size_mb: int = 10) -> Dict[str, Any]:
    """
    Discover and import all markdown files in a directory
    
    Args:
        directory_path: Directory to search for markdown files
        exclude_patterns: Patterns to exclude from import
        max_file_size_mb: Maximum file size to process
        
    Returns:
        Import results
    """
    exclude_str = ','.join(exclude_patterns) if exclude_patterns else ""
    return MigrationCLI.discover_and_import_all_markdown(
        directory_path, exclude_str, max_file_size_mb
    )


def categorize_file_by_name(file_path: Path) -> str:
    """Categorize a markdown file based on its name and location"""
    return MigrationUtilities.categorize_file_by_name(file_path)


def clean_duplicate_entries(context_manager, document_type: str = None) -> Dict[str, Any]:
    """Clean up duplicate document entries based on content signatures"""
    return MigrationUtilities.clean_duplicate_entries(context_manager, document_type)


def generate_markdown_import_report(context_manager) -> Dict[str, Any]:
    """Generate comprehensive report of imported markdown files"""
    importer = MarkdownImporter(context_manager)
    return importer.generate_import_report(context_manager)


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

# Maintain backward compatibility for existing code
def migrate_project(project_path: str, dry_run: bool = False) -> Dict[str, Any]:
    """Legacy function - redirects to new migration system"""
    logger.warning("Using legacy migrate_project function. "
                  "Consider updating to migrate_project_cli for v2.0 features.")
    
    return migrate_project_cli(project_path, dry_run=dry_run, force=False)


# =============================================================================
# MODULE INFORMATION
# =============================================================================

__version__ = "2.0.0"
__migration_architecture__ = "unified_documents"
__deprecated_tables_removed__ = ["discussions", "artifacts", "code_iterations", "plans", "chat_sessions"]

logger.info(f"Memory Bank Migration v{__version__} loaded - Unified Document Architecture")
logger.info(f"Deprecated tables removed: {', '.join(__deprecated_tables_removed__)}")
