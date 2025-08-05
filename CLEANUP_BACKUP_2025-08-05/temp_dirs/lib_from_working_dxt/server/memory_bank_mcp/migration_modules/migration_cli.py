"""
migration_modules/migration_cli.py
Generated: 2025-07-29.2337
Purpose: CLI interface and utilities for Memory Bank v2.0 migration
Provides command-line tools and reporting functions for unified document architecture
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger("memory_bank_mcp.migration.cli")


class MigrationCLI:
    """Command-line interface for Memory Bank v2.0 migration"""
    
    @staticmethod
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
        from .core_migrator import UnifiedDocumentMigrator
        
        try:
            # Import context manager here to avoid circular imports
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            
            from context_manager import ContextManager
            
            # Initialize context manager for the project
            context_manager = ContextManager(Path(project_path))
            
            # Create migrator instance
            migrator = UnifiedDocumentMigrator(Path(project_path), context_manager)
            
            # Run migration
            import asyncio
            report = asyncio.run(migrator.migrate_project(dry_run=dry_run, force=force))
            
            # Print results
            MigrationCLI.print_migration_report(report)
            
            return report
            
        except Exception as e:
            error_report = {
                'status': 'failed',
                'error': str(e),
                'project_path': project_path
            }
            
            print(f"❌ Migration failed: {e}")
            return error_report
    
    @staticmethod
    def print_migration_report(report: Dict[str, Any]) -> None:
        """Print formatted migration report"""
        
        print(f"\n🧠 **MEMORY BANK v2.0 MIGRATION REPORT**")
        print(f"═══════════════════════════════════════")
        
        # Project info
        print(f"📁 **Project:** {report.get('project_name', 'Unknown')}")
        print(f"📂 **Path:** {report.get('project_path', 'Unknown')}")
        print(f"⏰ **Started:** {report.get('start_time', 'Unknown')}")
        
        # Migration type
        if report.get('dry_run', False):
            print(f"🔍 **Mode:** Analysis Only (Dry Run)")
        else:
            print(f"🚀 **Mode:** Full Migration")
        
        if report.get('force_migration', False):
            print(f"⚡ **Force:** All files re-migrated")
        
        print(f"\n📊 **RESULTS SUMMARY:**")
        print(f"─────────────────────")
        
        # File statistics
        print(f"• 📄 Files Processed: {report.get('files_processed', 0)}")
        print(f"• ⏭️  Files Skipped: {report.get('files_skipped_unchanged', 0)}")
        print(f"• 🆕 Files New: {report.get('files_new', 0)}")
        print(f"• 🔄 Files Updated: {report.get('files_updated', 0)}")
        
        # Document statistics
        print(f"\n📚 **UNIFIED DOCUMENTS:**")
        total_docs = report.get('documents_migrated', 0) + report.get('documents_updated', 0)
        print(f"• 📄 Total Documents: {total_docs}")
        print(f"• 🆕 New Documents: {report.get('documents_migrated', 0)}")
        print(f"• 🔄 Updated Documents: {report.get('documents_updated', 0)}")
        print(f"• 🔄 Superseded Documents: {report.get('documents_superseded', 0)}")
        
        # Document type breakdown
        if 'document_types' in report:
            print(f"\n🏷️  **DOCUMENT TYPE BREAKDOWN:**")
            for doc_type, stats in report['document_types'].items():
                total_type = stats.get('new', 0) + stats.get('updated', 0)
                if total_type > 0:
                    icon = MigrationCLI._get_document_type_icon(doc_type)
                    print(f"  {icon} {doc_type.title()}: {total_type} "
                          f"({stats.get('new', 0)} new, {stats.get('updated', 0)} updated)")
        
        # Status
        status = report.get('status', 'unknown')
        if status == 'completed':
            print(f"\n✅ **Migration Completed Successfully**")
        elif status == 'failed':
            print(f"\n❌ **Migration Failed**")
        else:
            print(f"\n⚠️  **Migration Status:** {status}")
        
        # Errors and warnings
        if report.get('errors'):
            print(f"\n🚨 **ERRORS:**")
            for error in report['errors']:
                print(f"  • {error}")
        
        if report.get('warnings'):
            print(f"\n⚠️  **WARNINGS:**")
            for warning in report['warnings']:
                print(f"  • {warning}")
        
        # File details (if requested)
        if report.get('file_details') and len(report['file_details']) <= 10:
            print(f"\n📋 **FILE DETAILS:**")
            for file_detail in report['file_details']:
                status_icon = "✅" if file_detail.get('status') == 'migrated' else "⏭️"
                print(f"  {status_icon} {file_detail.get('filename', 'Unknown')} "
                      f"({file_detail.get('document_type', 'unknown')})")
        
        print(f"\n" + "═" * 40)
    
    @staticmethod
    def _get_document_type_icon(doc_type: str) -> str:
        """Get icon for document type"""
        icons = {
            'discussion': '💭',
            'artifact': '🎯',
            'plan': '📋',
            'code': '💻',
            'note': '📝',
            'document': '📄',
            'markdown': '📋'
        }
        return icons.get(doc_type, '📄')
    
    @staticmethod
    def discover_and_import_all_markdown(directory_path: str, 
                                       exclude_patterns: str = "",
                                       max_file_size_mb: int = 10) -> Dict[str, Any]:
        """
        Discover and import all markdown files in a directory
        
        Args:
            directory_path: Directory to search for markdown files
            exclude_patterns: Comma-separated patterns to exclude
            max_file_size_mb: Maximum file size to process
            
        Returns:
            Import results
        """
        from .markdown_importer import MarkdownImporter
        
        try:
            # Import context manager
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            
            from context_manager import ContextManager
            
            # Initialize context manager and importer
            context_manager = ContextManager(Path(directory_path))
            importer = MarkdownImporter(context_manager)
            
            # Parse exclude patterns
            exclude_list = [p.strip() for p in exclude_patterns.split(',')] if exclude_patterns else []
            
            # Run import
            results = importer.discover_and_import_all_markdown(
                directory_path=directory_path,
                exclude_patterns=exclude_list,
                max_file_size_mb=max_file_size_mb
            )
            
            # Print results
            MigrationCLI.print_markdown_import_report(results)
            
            return results
            
        except Exception as e:
            error_msg = f"Failed to import markdown files: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {'status': 'failed', 'error': error_msg}
    
    @staticmethod
    def print_markdown_import_report(results: Dict[str, Any]) -> None:
        """Print formatted markdown import report"""
        
        print(f"\n📋 **MARKDOWN IMPORT REPORT**")
        print(f"═══════════════════════════════")
        
        print(f"📁 **Directory:** {results.get('directory_path', 'Unknown')}")
        print(f"📊 **Files Found:** {results.get('files_found', 0)}")
        print(f"📄 **Files Imported:** {results.get('files_imported', 0)}")
        print(f"⏭️  **Files Skipped:** {results.get('files_skipped', 0)}")
        print(f"❌ **Files Failed:** {results.get('files_failed', 0)}")
        
        if results.get('file_details'):
            print(f"\n📋 **IMPORT DETAILS:**")
            for detail in results['file_details']:
                status_icon = "✅" if detail.get('status') == 'imported' else "❌"
                print(f"  {status_icon} {detail.get('filename', 'Unknown')} "
                      f"({detail.get('size_kb', 0)}KB)")
        
        if results.get('errors'):
            print(f"\n🚨 **ERRORS:**")
            for error in results['errors']:
                print(f"  • {error}")
        
        print(f"\n" + "═" * 30)
    
    @staticmethod
    def generate_migration_report(context_manager) -> Dict[str, Any]:
        """Generate comprehensive migration status report"""
        
        try:
            # Get current database statistics
            import asyncio
            db_stats = asyncio.run(context_manager.database.get_database_stats())
            
            report = {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'project_path': str(context_manager.project_path),
                'database_path': str(context_manager.database_path),
                'unified_architecture': True,
                'statistics': db_stats,
                'document_breakdown': {},
                'migration_status': 'completed'
            }
            
            # Calculate document breakdown
            total_docs = db_stats.get('documents_total_count', 0)
            if total_docs > 0:
                for doc_type in ['discussion', 'artifact', 'plan', 'code', 'note', 'document']:
                    count = db_stats.get(f'documents_{doc_type}_count', 0)
                    if count > 0:
                        report['document_breakdown'][doc_type] = {
                            'count': count,
                            'percentage': round((count / total_docs) * 100, 1)
                        }
            
            MigrationCLI.print_status_report(report)
            return report
            
        except Exception as e:
            error_msg = f"Failed to generate migration report: {str(e)}"
            logger.error(error_msg)
            return {'status': 'failed', 'error': error_msg}
    
    @staticmethod
    def print_status_report(report: Dict[str, Any]) -> None:
        """Print formatted status report"""
        
        print(f"\n📊 **MEMORY BANK v2.0 STATUS REPORT**")
        print(f"═══════════════════════════════════════")
        
        print(f"📁 **Project:** {Path(report['project_path']).name}")
        print(f"📂 **Path:** {report['project_path']}")
        print(f"💾 **Database:** {report['database_path']}")
        print(f"⏰ **Generated:** {report['generated_at']}")
        
        stats = report.get('statistics', {})
        
        print(f"\n📚 **UNIFIED DOCUMENT ARCHITECTURE:**")
        print(f"• 📄 Total Documents: {stats.get('documents_total_count', 0)}")
        print(f"• 📝 Decisions: {stats.get('decisions_count', 0)}")
        print(f"• 🔗 Cross References: {stats.get('cross_references_count', 0)}")
        
        if 'document_breakdown' in report:
            print(f"\n🏷️  **DOCUMENT TYPE DISTRIBUTION:**")
            for doc_type, breakdown in report['document_breakdown'].items():
                icon = MigrationCLI._get_document_type_icon(doc_type)
                print(f"  {icon} {doc_type.title()}: {breakdown['count']} "
                      f"({breakdown['percentage']}%)")
        
        print(f"\n✅ **Status:** {report.get('migration_status', 'Unknown')}")
        print(f"\n" + "═" * 40)


class MigrationUtilities:
    """Utility functions for migration operations"""
    
    @staticmethod
    def categorize_file_by_name(file_path: Path) -> str:
        """Categorize a markdown file based on its name and location"""
        filename_lower = file_path.name.lower()
        parent_dir = file_path.parent.name.lower()
        
        # Specific filename mappings
        filename_mappings = {
            'readme.md': 'document',
            'changelog.md': 'document',
            'todo.md': 'plan',
            'notes.md': 'note',
            'scratch.md': 'note',
            'journal.md': 'discussion',
            'meeting.md': 'discussion',
            'patterns.md': 'artifact',
            'templates.md': 'artifact',
            'rules.md': 'artifact',
            'config.md': 'artifact'
        }
        
        if filename_lower in filename_mappings:
            return filename_mappings[filename_lower]
        
        # Pattern-based categorization
        if any(pattern in filename_lower for pattern in ['pattern', 'template', 'rule', 'config']):
            return 'artifact'
        
        if any(pattern in filename_lower for pattern in ['plan', 'roadmap', 'strategy', 'brief']):
            return 'plan'
        
        if any(pattern in filename_lower for pattern in ['progress', 'journal', 'meeting', 'discussion']):
            return 'discussion'
        
        if any(pattern in filename_lower for pattern in ['note', 'scratch', 'idea', 'draft']):
            return 'note'
        
        if any(pattern in filename_lower for pattern in ['code', 'script', 'example']):
            return 'code'
        
        # Directory-based hints
        if any(pattern in parent_dir for pattern in ['doc', 'documentation']):
            return 'document'
        
        if any(pattern in parent_dir for pattern in ['template', 'pattern']):
            return 'artifact'
        
        if any(pattern in parent_dir for pattern in ['journal', 'log']):
            return 'discussion'
        
        # Default fallback
        return 'note'
    
    @staticmethod
    def clean_duplicate_entries(context_manager, document_type: str = None) -> Dict[str, Any]:
        """Clean up duplicate document entries"""
        from .smart_merge import SmartMergeEngine
        
        try:
            merge_engine = SmartMergeEngine(context_manager)
            import asyncio
            results = asyncio.run(merge_engine.deduplicate_by_content_signature(document_type))
            
            print(f"\n🧹 **DUPLICATE CLEANUP RESULTS**")
            print(f"═══════════════════════════════")
            print(f"• 🔍 Duplicates Found: {results.get('duplicates_found', 0)}")
            print(f"• 🗑️  Duplicates Removed: {results.get('duplicates_removed', 0)}")
            
            if results.get('errors'):
                print(f"\n❌ **ERRORS:**")
                for error in results['errors']:
                    print(f"  • {error}")
            else:
                print(f"\n✅ **Cleanup Completed Successfully**")
            
            return results
            
        except Exception as e:
            error_msg = f"Cleanup failed: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return {'status': 'failed', 'error': error_msg}
