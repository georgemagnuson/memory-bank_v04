"""
migration_modules/core_migrator.py
Generated: 2025-07-29.2316
Purpose: Core migration engine for Memory Bank v2.0 unified document architecture
Handles Smart Merge capabilities and document type classification
"""

import re
import hashlib
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

logger = logging.getLogger("memory_bank_mcp.migration.core")


class UnifiedDocumentMigrator:
    """
    v2.0 Migration engine for unified document architecture
    
    Key Changes from v1.4.0:
    - Uses unified documents table with document_type field
    - Eliminates separate discussions, artifacts, plans tables
    - Maintains Smart Merge capabilities with unified approach
    """
    
    def __init__(self, project_path: Path, context_manager):
        self.project_path = project_path
        self.memory_bank_path = project_path / "memory-bank"
        self.context_manager = context_manager
        
        # Files to migrate with their expected document types for v2.0
        self.migration_targets = {
            'projectbrief.md': 'plan',
            'productContext.md': 'document', 
            'activeContext.md': 'note',
            'systemPatterns.md': 'artifact',
            'progress.md': 'discussion',
            'global_rules.md': 'artifact',
            '.membankrules': 'artifact'
        }
        
        logger.info(f"Unified Document Migrator initialized for: {project_path}")
    
    async def migrate_project(self, dry_run: bool = False, force: bool = False) -> Dict[str, Any]:
        """
        Migrate project files to unified document architecture
        
        Args:
            dry_run: If True, analyze files but don't write to database
            force: If True, re-migrate all files regardless of timestamps
            
        Returns:  
            Enhanced migration report with unified document statistics
        """
        if not self.memory_bank_path.exists():
            return {
                'error': f'No memory-bank directory found at {self.memory_bank_path}',
                'status': 'failed'
            }
        
        migration_report = {
            'project_path': str(self.project_path),
            'project_name': self.project_path.name,
            'dry_run': dry_run,
            'force_migration': force,
            'unified_document_architecture': True,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'files_processed': 0,
            'files_skipped_unchanged': 0,
            'files_new': 0,
            'files_updated': 0,
            # v2.0: Document type statistics instead of separate table counts
            'documents_migrated': 0,
            'documents_updated': 0, 
            'documents_superseded': 0,
            'document_types': {
                'discussion': {'new': 0, 'updated': 0, 'superseded': 0},
                'artifact': {'new': 0, 'updated': 0, 'superseded': 0},
                'plan': {'new': 0, 'updated': 0, 'superseded': 0},
                'code': {'new': 0, 'updated': 0, 'superseded': 0},
                'note': {'new': 0, 'updated': 0, 'superseded': 0},
                'document': {'new': 0, 'updated': 0, 'superseded': 0}
            },
            'context_updated': False,
            'errors': [],
            'warnings': [],
            'file_details': [],
            'change_summary': {}
        }
        
        try:
            # Process main memory-bank files with unified document approach
            for filename, document_type in self.migration_targets.items():
                file_path = self.memory_bank_path / filename
                if file_path.exists():
                    await self._migrate_file_to_unified_document(file_path, document_type, migration_report, dry_run, force)
            
            # Process journal files
            journal_path = self.memory_bank_path / "journal"
            if journal_path.exists():
                await self._migrate_journal_directory(journal_path, migration_report, dry_run, force)
            
            # Process any other markdown files
            await self._migrate_other_markdown(migration_report, dry_run, force)
            
            migration_report['status'] = 'completed'
            migration_report['end_time'] = datetime.now(timezone.utc).isoformat()
            
            # Generate change summary for unified architecture
            migration_report['change_summary'] = self._generate_unified_change_summary(migration_report)
            
            logger.info(f"Unified document migration {'analysis' if dry_run else 'completed'}: {migration_report}")
            
        except Exception as e:
            logger.error(f"Migration error: {e}")
            migration_report['errors'].append(f"Migration failed: {str(e)}")
            migration_report['status'] = 'failed'
        
        return migration_report
    
    async def _migrate_file_to_unified_document(self, file_path: Path, document_type: str, 
                                              report: Dict[str, Any], dry_run: bool, force: bool) -> None:
        """Migrate a single file to unified document architecture"""
        
        try:
            # Check if file needs migration based on modification time
            if not force and not dry_run:
                needs_migration = await self._should_migrate_file(file_path)
                if not needs_migration:
                    report['files_skipped_unchanged'] += 1
                    report['file_details'].append({
                        'filename': file_path.name,
                        'document_type': document_type,
                        'status': 'skipped_unchanged',
                        'reason': 'File unchanged since last migration'
                    })
                    return
            
            # Read and classify content
            content = file_path.read_text(encoding='utf-8')
            
            # Create unified document entry
            if not dry_run:
                await self._save_unified_document(
                    title=file_path.stem,
                    content=content,
                    document_type=document_type,
                    source_file=str(file_path),
                    report=report
                )
            
            report['files_processed'] += 1
            report['file_details'].append({
                'filename': file_path.name,
                'document_type': document_type,
                'status': 'migrated',
                'content_length': len(content)
            })
            
            logger.info(f"Migrated {file_path.name} as document_type='{document_type}'")
            
        except Exception as e:
            logger.error(f"Error migrating file {file_path}: {e}")
            report['errors'].append(f"Failed to migrate {file_path.name}: {str(e)}")
    
    async def _save_unified_document(self, title: str, content: str, document_type: str, 
                                   source_file: str, report: Dict[str, Any]) -> None:
        """Save document to unified documents table"""
        
        # Check if document already exists
        existing_docs = await self._find_existing_documents(title, document_type)
        
        if existing_docs:
            # Update existing document
            await self._update_unified_document(existing_docs[0]['uuid'], title, content, document_type, source_file)
            report['documents_updated'] += 1
            report['document_types'][document_type]['updated'] += 1
        else:
            # Create new document
            await self._create_unified_document(title, content, document_type, source_file)
            report['documents_migrated'] += 1
            report['document_types'][document_type]['new'] += 1
    
    async def _find_existing_documents(self, title: str, document_type: str) -> List[Dict[str, Any]]:
        """Find existing documents by title and type"""
        query = """
        SELECT uuid, title, content 
        FROM unified_documents 
        WHERE title = ? AND document_type = ? AND record_status = 'active'
        """
        
        result = await self.context_manager.database._execute_query(query, (title, document_type))
        return [{'uuid': row[0], 'title': row[1], 'content': row[2]} for row in result] if result else []
    
    async def _create_unified_document(self, title: str, content: str, document_type: str, source_file: str) -> None:
        """Create new unified document"""
        import uuid as uuid_module
        
        document_uuid = str(uuid_module.uuid4())
        project_uuid = self.context_manager.database.project_uuid
        
        query = """
        INSERT INTO unified_documents 
        (uuid, project_uuid, title, content, document_type, source_file, record_status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        
        await self.context_manager.database._execute_query(
            query, (document_uuid, project_uuid, title, content, document_type, source_file)
        )
        
        logger.info(f"Created unified document: {title} (type: {document_type})")
    
    async def _update_unified_document(self, document_uuid: str, title: str, content: str, 
                                     document_type: str, source_file: str) -> None:
        """Update existing unified document"""
        query = """
        UPDATE unified_documents 
        SET title = ?, content = ?, document_type = ?, source_file = ?, updated_at = CURRENT_TIMESTAMP
        WHERE uuid = ?
        """
        
        await self.context_manager.database._execute_query(
            query, (title, content, document_type, source_file, document_uuid)
        )
        
        logger.info(f"Updated unified document: {title} (type: {document_type})")
    
    async def _should_migrate_file(self, file_path: Path) -> bool:
        """Check if file should be migrated based on modification time"""
        # This is a simplified version - in the full implementation, 
        # this would check the database for the last migration timestamp
        return True  # For now, always migrate
    
    async def _migrate_journal_directory(self, journal_path: Path, report: Dict[str, Any], 
                                       dry_run: bool, force: bool) -> None:
        """Migrate journal files as discussion-type documents"""
        for journal_file in journal_path.glob("*.md"):
            await self._migrate_file_to_unified_document(journal_file, 'discussion', report, dry_run, force)
    
    async def _migrate_other_markdown(self, report: Dict[str, Any], dry_run: bool, force: bool) -> None:
        """Migrate other markdown files found in the project"""
        for md_file in self.memory_bank_path.rglob("*.md"):
            if md_file.name not in self.migration_targets:
                # Classify as 'note' by default for unknown markdown files
                await self._migrate_file_to_unified_document(md_file, 'note', report, dry_run, force)
    
    def _generate_unified_change_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate change summary for unified document architecture"""
        return {
            'total_documents_processed': report['documents_migrated'] + report['documents_updated'],
            'new_documents': report['documents_migrated'],
            'updated_documents': report['documents_updated'],
            'document_type_breakdown': report['document_types'],
            'files_processed': report['files_processed'],
            'architecture': 'unified_documents_v2.0'
        }
