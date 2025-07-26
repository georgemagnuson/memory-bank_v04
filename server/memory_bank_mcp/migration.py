#!/usr/bin/env python3
"""
memory_bank_mcp/migration.py
Generated: 2025-07-15.1730
Purpose: Enhanced migration tool with Smart Merge capabilities for converting .md files to context.db
Preserves original files while intelligently handling duplicates and changes

Enhanced Features:
- Smart Merge with source file tracking and timestamps
- Intelligent change detection using content signatures
- Record status tracking (active, superseded, obsolete)
- File modification date-based re-migration
- Content-based duplicate prevention
- Comprehensive migration reporting with change analysis
"""

import re
import hashlib
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

from .database import MemoryBankDatabase


logger = logging.getLogger("memory_bank_mcp.migration")


class SmartMergeMigrator:
    """
    Enhanced migration tool with Smart Merge capabilities for memory-bank markdown files
    
    Features:
    - Non-destructive migration (preserves original .md files)
    - Smart Merge with intelligent change detection
    - Source file tracking with creation and modification timestamps
    - Content signature-based duplicate prevention
    - Record status management (active, superseded, obsolete)
    - Selective re-migration of only changed files
    - Comprehensive reporting with change analysis
    """
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.memory_bank_path = project_path / "memory-bank"
        self.database = MemoryBankDatabase(project_path)
        
        # Files to migrate with their expected content types
        self.migration_targets = {
            'projectbrief.md': 'project_overview',
            'productContext.md': 'project_overview', 
            'activeContext.md': 'current_focus',
            'systemPatterns.md': 'patterns',
            'progress.md': 'progress',
            'global_rules.md': 'rules',
            '.membankrules': 'rules'
        }
        
        logger.info(f"Smart Merge Migrator initialized for: {project_path}")
    
    async def migrate_project(self, dry_run: bool = False, force: bool = False) -> Dict[str, Any]:
        """
        Migrate project files with Smart Merge capabilities
        
        Args:
            dry_run: If True, analyze files but don't write to database
            force: If True, re-migrate all files regardless of timestamps
            
        Returns:
            Enhanced migration report with change analysis
        """
        if not self.memory_bank_path.exists():
            return {
                'error': f'No memory-bank directory found at {self.memory_bank_path}',
                'status': 'failed'
            }
        
        # Initialize database (but don't write if dry_run)
        if not dry_run:
            await self.database.initialize()
        
        migration_report = {
            'project_path': str(self.project_path),
            'project_name': self.project_path.name,
            'dry_run': dry_run,
            'force_migration': force,
            'smart_merge_enabled': True,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'files_processed': 0,
            'files_skipped_unchanged': 0,
            'files_new': 0,
            'files_updated': 0,
            'discussions_migrated': 0,
            'discussions_updated': 0,
            'discussions_superseded': 0,
            'artifacts_migrated': 0,
            'artifacts_updated': 0,
            'artifacts_superseded': 0,
            'context_updated': False,
            'errors': [],
            'warnings': [],
            'file_details': [],
            'change_summary': {}
        }
        
        try:
            # Process main memory-bank files with Smart Merge
            for filename, content_type in self.migration_targets.items():
                file_path = self.memory_bank_path / filename
                if file_path.exists():
                    await self._smart_migrate_file(file_path, content_type, migration_report, dry_run, force)
            
            # Process journal files with Smart Merge
            journal_path = self.memory_bank_path / "journal"
            if journal_path.exists():
                await self._smart_migrate_journal_directory(journal_path, migration_report, dry_run, force)
            
            # Process any other markdown files
            await self._smart_migrate_other_markdown(migration_report, dry_run, force)
            
            migration_report['status'] = 'completed'
            migration_report['end_time'] = datetime.now(timezone.utc).isoformat()
            
            # Generate change summary
            migration_report['change_summary'] = self._generate_change_summary(migration_report)
            
            logger.info(f"Smart Merge migration {'analysis' if dry_run else 'completed'}: {migration_report}")
            
        except Exception as e:
            logger.error(f"Migration error: {e}")
            migration_report['errors'].append(f"Migration failed: {str(e)}")
            migration_report['status'] = 'failed'
        
        return migration_report    
    async def _smart_migrate_file(self, file_path: Path, content_type: str, 
                                report: Dict[str, Any], dry_run: bool, force: bool) -> None:
        """Smart Merge migration for a single file"""
        
        try:
            # Check if file needs migration
            if not force and not dry_run:
                needs_migration = await self.database.should_migrate_file(file_path)
                if not needs_migration:
                    report['files_skipped_unchanged'] += 1
                    report['file_details'].append({
                        'filename': file_path.name,
                        'content_type': content_type,
                        'status': 'skipped_unchanged',
                        'reason': 'File unchanged since last migration'
                    })
                    logger.info(f"Skipping unchanged file: {file_path.name}")
                    return
            
            content = file_path.read_text(encoding='utf-8')
            file_detail = {
                'filename': file_path.name,
                'content_type': content_type,
                'size_bytes': len(content),
                'items_extracted': 0,
                'items_new': 0,
                'items_updated': 0,
                'items_superseded': 0,
                'errors': [],
                'status': 'new' if force else 'updated'
            }
            
            if content_type == 'project_overview':
                await self._smart_migrate_context_file(file_path, content, 'overview', report, dry_run)
                file_detail['items_extracted'] = 1
                report['context_updated'] = True
                
            elif content_type == 'current_focus':
                await self._smart_migrate_context_file(file_path, content, 'current_focus', report, dry_run)
                file_detail['items_extracted'] = 1
                report['context_updated'] = True
                
            elif content_type == 'patterns':
                merge_result = await self._smart_migrate_patterns(file_path, content, report, dry_run)
                file_detail.update(merge_result)
                
            elif content_type == 'progress':
                merge_result = await self._smart_migrate_progress(file_path, content, report, dry_run)
                file_detail.update(merge_result)
                
            elif content_type == 'rules':
                merge_result = await self._smart_migrate_rules_file(file_path, content, report, dry_run)
                file_detail.update(merge_result)
            
            report['file_details'].append(file_detail)
            report['files_processed'] += 1
            
            # Determine if this was a new file or update
            if file_detail['items_new'] > 0 and file_detail['items_updated'] == 0:
                report['files_new'] += 1
            elif file_detail['items_updated'] > 0 or file_detail['items_superseded'] > 0:
                report['files_updated'] += 1
            
        except Exception as e:
            error_msg = f"Error in Smart Merge for {file_path.name}: {str(e)}"
            logger.error(error_msg)
            report['errors'].append(error_msg)
    
    async def _smart_migrate_patterns(self, file_path: Path, content: str, 
                                    report: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Smart Merge migration for patterns"""
        
        result = {
            'items_extracted': 0,
            'items_new': 0,
            'items_updated': 0,
            'items_superseded': 0
        }
        
        # Extract current patterns from file
        current_patterns = await self._extract_patterns(content, file_path)
        
        if not dry_run:
            # Get existing patterns from this file
            existing_records = await self.database.get_records_by_source_file(file_path, "artifacts")
            existing_patterns = existing_records["artifacts"]
            
            # Perform Smart Merge comparison
            merge_analysis = self._analyze_content_changes(current_patterns, existing_patterns, "title")
            
            # Handle new patterns
            for pattern in merge_analysis['new_items']:
                await self.database.save_artifact(
                    title=pattern['name'],
                    content=pattern['content'],
                    artifact_type='pattern',
                    filename=pattern.get('filename', 'unknown'),
                    source_file=file_path
                )
                result['items_new'] += 1
            
            # Handle updated patterns
            for pattern_data in merge_analysis['updated_items']:
                current_pattern, existing_uuid = pattern_data['current'], pattern_data['existing_uuid']
                
                # Mark old version as superseded
                await self.database.mark_records_as_superseded([existing_uuid], "artifacts")
                
                # Add new version
                await self.database.save_artifact(
                    title=current_pattern['name'],
                    content=current_pattern['content'],
                    artifact_type='pattern',
                    filename=current_pattern.get('filename', 'unknown'),
                    source_file=file_path
                )
                result['items_updated'] += 1
                result['items_superseded'] += 1
            
            # Handle obsolete patterns (mark as obsolete)
            if merge_analysis['obsolete_items']:
                obsolete_uuids = [item['uuid'] for item in merge_analysis['obsolete_items']]
                await self.database.mark_records_as_superseded(obsolete_uuids, "artifacts")
                result['items_superseded'] += len(obsolete_uuids)
        
        result['items_extracted'] = len(current_patterns)
        report['artifacts_migrated'] += result['items_new']
        report['artifacts_updated'] += result['items_updated']
        report['artifacts_superseded'] += result['items_superseded']
        
        return result
    
    async def _smart_migrate_progress(self, file_path: Path, content: str,
                                    report: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Smart Merge migration for progress items"""
        
        result = {
            'items_extracted': 0,
            'items_new': 0,
            'items_updated': 0,
            'items_superseded': 0
        }
        
        # Extract current progress items
        current_progress = await self._extract_progress(content, file_path)
        
        if not dry_run:
            # Get existing progress items from this file
            existing_records = await self.database.get_records_by_source_file(file_path, "discussions")
            existing_progress = existing_records["discussions"]
            
            # Perform Smart Merge comparison
            merge_analysis = self._analyze_content_changes(current_progress, existing_progress, "summary")
            
            # Handle new progress items
            for item in merge_analysis['new_items']:
                await self.database.save_discussion(
                    summary=item['summary'],
                    content=item['content'],
                    implemented=item.get('implemented'),
                    tags=item.get('tags', []),
                    source_file=file_path
                )
                result['items_new'] += 1
            
            # Handle updated progress items
            for item_data in merge_analysis['updated_items']:
                current_item, existing_uuid = item_data['current'], item_data['existing_uuid']
                
                # Mark old version as superseded
                await self.database.mark_records_as_superseded([existing_uuid], "discussions")
                
                # Add new version
                await self.database.save_discussion(
                    summary=current_item['summary'],
                    content=current_item['content'],
                    implemented=current_item.get('implemented'),
                    tags=current_item.get('tags', []),
                    source_file=file_path
                )
                result['items_updated'] += 1
                result['items_superseded'] += 1
            
            # Handle obsolete items
            if merge_analysis['obsolete_items']:
                obsolete_uuids = [item['uuid'] for item in merge_analysis['obsolete_items']]
                await self.database.mark_records_as_superseded(obsolete_uuids, "discussions")
                result['items_superseded'] += len(obsolete_uuids)
        
        result['items_extracted'] = len(current_progress)
        report['discussions_migrated'] += result['items_new']
        report['discussions_updated'] += result['items_updated']
        report['discussions_superseded'] += result['items_superseded']
        
        return result
    
    async def _smart_migrate_journal_directory(self, journal_path: Path, 
                                             report: Dict[str, Any], dry_run: bool, force: bool) -> None:
        """Smart Merge migration for journal files"""
        
        for journal_file in journal_path.glob("*.md"):
            try:
                # Check if file needs migration
                if not force and not dry_run:
                    needs_migration = await self.database.should_migrate_file(journal_file)
                    if not needs_migration:
                        report['files_skipped_unchanged'] += 1
                        continue
                
                content = journal_file.read_text(encoding='utf-8')
                
                file_detail = {
                    'filename': journal_file.name,
                    'content_type': 'journal',
                    'size_bytes': len(content),
                    'items_extracted': 0,
                    'items_new': 0,
                    'items_updated': 0,
                    'items_superseded': 0,
                    'errors': [],
                    'status': 'processed'
                }
                
                # Extract content from journal
                decisions = await self._extract_journal_decisions(content, journal_file)
                progress_items = await self._extract_progress(content, journal_file)
                
                if not dry_run:
                    # Get existing records from this journal file
                    existing_records = await self.database.get_records_by_source_file(journal_file, "discussions")
                    existing_discussions = existing_records["discussions"]
                    
                    # Combine decisions and progress for analysis
                    all_current_items = decisions + progress_items
                    
                    # Perform Smart Merge
                    merge_analysis = self._analyze_content_changes(all_current_items, existing_discussions, "summary")
                    
                    # Process new items
                    for item in merge_analysis['new_items']:
                        await self.database.save_discussion(
                            summary=item['summary'],
                            content=item['content'],
                            implemented=item.get('implemented'),
                            tags=item.get('tags', []),
                            source_file=journal_file
                        )
                        file_detail['items_new'] += 1
                    
                    # Process updated items
                    for item_data in merge_analysis['updated_items']:
                        current_item, existing_uuid = item_data['current'], item_data['existing_uuid']
                        
                        # Mark old as superseded
                        await self.database.mark_records_as_superseded([existing_uuid], "discussions")
                        
                        # Add new version
                        await self.database.save_discussion(
                            summary=current_item['summary'],
                            content=current_item['content'],
                            implemented=current_item.get('implemented'),
                            tags=current_item.get('tags', []),
                            source_file=journal_file
                        )
                        file_detail['items_updated'] += 1
                        file_detail['items_superseded'] += 1
                    
                    # Handle obsolete items
                    if merge_analysis['obsolete_items']:
                        obsolete_uuids = [item['uuid'] for item in merge_analysis['obsolete_items']]
                        await self.database.mark_records_as_superseded(obsolete_uuids, "discussions")
                        file_detail['items_superseded'] += len(obsolete_uuids)
                
                file_detail['items_extracted'] = len(decisions) + len(progress_items)
                
                report['discussions_migrated'] += file_detail['items_new']
                report['discussions_updated'] += file_detail['items_updated']
                report['discussions_superseded'] += file_detail['items_superseded']
                report['files_processed'] += 1
                report['file_details'].append(file_detail)
                
                # Determine file status
                if file_detail['items_new'] > 0 and file_detail['items_updated'] == 0:
                    report['files_new'] += 1
                elif file_detail['items_updated'] > 0 or file_detail['items_superseded'] > 0:
                    report['files_updated'] += 1
                
            except Exception as e:
                error_msg = f"Error migrating journal {journal_file.name}: {str(e)}"
                logger.error(error_msg)
                report['errors'].append(error_msg)
    
    def _generate_change_summary(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of changes made during migration"""
        
        return {
            'total_files_analyzed': report['files_processed'] + report['files_skipped_unchanged'],
            'files_processed': report['files_processed'],
            'files_skipped': report['files_skipped_unchanged'],
            'files_new': report['files_new'],
            'files_updated': report['files_updated'],
            'total_discussions': report['discussions_migrated'] + report['discussions_updated'],
            'discussions_new': report['discussions_migrated'],
            'discussions_updated': report['discussions_updated'],
            'discussions_superseded': report['discussions_superseded'],
            'total_artifacts': report['artifacts_migrated'] + report['artifacts_updated'],
            'artifacts_new': report['artifacts_migrated'],
            'artifacts_updated': report['artifacts_updated'],
            'artifacts_superseded': report['artifacts_superseded'],
            'efficiency_ratio': round(
                (report['files_skipped_unchanged'] / max(1, report['files_processed'] + report['files_skipped_unchanged'])) * 100, 1
            )
        }
    
    # =============================================================================
    # MISSING SMART MIGRATE METHODS - IMPLEMENTATION
    # Generated: 2025-07-16.1321
    # Purpose: Implement missing smart_migrate_context_file, smart_migrate_rules_file, smart_migrate_other_markdown
    # =============================================================================
    
    async def _smart_migrate_context_file(self, file_path: Path, content: str, context_type: str,
                                       report: Dict[str, Any], dry_run: bool) -> None:
        """
        Smart Merge migration for context files (projectbrief.md, productContext.md, activeContext.md)
        
        Updates the project_context table with extracted content based on context_type:
        - 'overview': Updates overview field
        - 'current_focus': Updates current_focus field
        """
        
        try:
            if not dry_run:
                # Get current context from database
                existing_context = await self.database.get_project_context()
                
                # Create content signature for change detection
                content_signature = self._create_content_signature(content)
                
                # Update the appropriate context field
                if context_type == 'overview':
                    if existing_context.get('overview_signature') != content_signature:
                        await self.database.update_project_context(
                            overview=content,
                            source_file=file_path,
                            overview_signature=content_signature
                        )
                        logger.info(f"Updated project overview from {file_path.name}")
                    else:
                        logger.info(f"Project overview unchanged: {file_path.name}")
                        
                elif context_type == 'current_focus':
                    if existing_context.get('current_focus_signature') != content_signature:
                        await self.database.update_project_context(
                            current_focus=content,
                            source_file=file_path,
                            current_focus_signature=content_signature
                        )
                        logger.info(f"Updated current focus from {file_path.name}")
                    else:
                        logger.info(f"Current focus unchanged: {file_path.name}")
                        
            logger.info(f"Context file processed: {file_path.name} ({context_type})")
            
        except Exception as e:
            error_msg = f"Error in smart_migrate_context_file for {file_path.name}: {str(e)}"
            logger.error(error_msg)
            report['errors'].append(error_msg)
    
    async def _smart_migrate_rules_file(self, file_path: Path, content: str, 
                                     report: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """
        Smart Merge migration for rules files (global_rules.md, .membankrules)
        
        Stores rules as artifacts with artifact_type='rules' and handles different rule formats
        """
        
        result = {
            'items_extracted': 0,
            'items_new': 0,
            'items_updated': 0,
            'items_superseded': 0
        }
        
        try:
            # Extract rules based on file format
            if file_path.suffix == '.md':
                # Markdown rules file - extract as sections
                current_rules = await self._extract_markdown_rules(content, file_path)
            else:
                # Config-style rules file - treat as single rule set
                current_rules = await self._extract_config_rules(content, file_path)
            
            if not dry_run:
                # Get existing rules from this file
                existing_records = await self.database.get_records_by_source_file(file_path, "artifacts")
                existing_rules = existing_records["artifacts"]
                
                # Perform Smart Merge comparison
                merge_analysis = self._analyze_content_changes(current_rules, existing_rules, "title")
                
                # Handle new rules
                for rule in merge_analysis['new_items']:
                    await self.database.save_artifact(
                        title=rule['title'],
                        content=rule['content'],
                        artifact_type='rules',
                        filename=rule.get('filename', file_path.name),
                        source_file=file_path
                    )
                    result['items_new'] += 1
                
                # Handle updated rules
                for rule_data in merge_analysis['updated_items']:
                    current_rule, existing_uuid = rule_data['current'], rule_data['existing_uuid']
                    
                    # Mark old version as superseded
                    await self.database.mark_records_as_superseded([existing_uuid], "artifacts")
                    
                    # Add new version
                    await self.database.save_artifact(
                        title=current_rule['title'],
                        content=current_rule['content'],
                        artifact_type='rules',
                        filename=current_rule.get('filename', file_path.name),
                        source_file=file_path
                    )
                    result['items_updated'] += 1
                    result['items_superseded'] += 1
                
                # Handle obsolete rules
                if merge_analysis['obsolete_items']:
                    obsolete_uuids = [item['uuid'] for item in merge_analysis['obsolete_items']]
                    await self.database.mark_records_as_superseded(obsolete_uuids, "artifacts")
                    result['items_superseded'] += len(obsolete_uuids)
            
            result['items_extracted'] = len(current_rules)
            report['artifacts_migrated'] += result['items_new']
            report['artifacts_updated'] += result['items_updated']
            report['artifacts_superseded'] += result['items_superseded']
            
            logger.info(f"Rules file processed: {file_path.name} ({result['items_extracted']} rules)")
            
        except Exception as e:
            error_msg = f"Error in smart_migrate_rules_file for {file_path.name}: {str(e)}"
            logger.error(error_msg)
            report['errors'].append(error_msg)
        
        return result
    
    async def _smart_migrate_other_markdown(self, report: Dict[str, Any], dry_run: bool, force: bool) -> None:
        """
        Smart Merge migration for any remaining markdown files not handled by specific methods
        
        Scans memory-bank directory for .md files and applies generic content extraction
        """
        
        try:
            # Get list of files already processed by specific methods
            processed_files = set(self.migration_targets.keys())
            
            # Find all .md files in memory-bank directory
            all_md_files = list(self.memory_bank_path.glob("*.md"))
            
            # Filter out already processed files
            unprocessed_files = [
                file_path for file_path in all_md_files 
                if file_path.name not in processed_files
            ]
            
            logger.info(f"Found {len(unprocessed_files)} unprocessed markdown files")
            
            for file_path in unprocessed_files:
                try:
                    # Check if file needs migration
                    if not force and not dry_run:
                        needs_migration = await self.database.should_migrate_file(file_path)
                        if not needs_migration:
                            report['files_skipped_unchanged'] += 1
                            continue
                    
                    content = file_path.read_text(encoding='utf-8')
                    
                    file_detail = {
                        'filename': file_path.name,
                        'content_type': 'other_markdown',
                        'size_bytes': len(content),
                        'items_extracted': 0,
                        'items_new': 0,
                        'items_updated': 0,
                        'items_superseded': 0,
                        'errors': [],
                        'status': 'processed'
                    }
                    
                    # Classify content and extract accordingly
                    content_classification = self._classify_markdown_content(content, file_path)
                    
                    if content_classification['type'] == 'artifacts':
                        # Extract as artifacts (code, patterns, templates)
                        merge_result = await self._extract_and_merge_artifacts(
                            file_path, content, content_classification, report, dry_run
                        )
                        file_detail.update(merge_result)
                        
                    elif content_classification['type'] == 'discussions':
                        # Extract as discussions (notes, decisions, progress)
                        merge_result = await self._extract_and_merge_discussions(
                            file_path, content, content_classification, report, dry_run
                        )
                        file_detail.update(merge_result)
                        
                    else:
                        # Mixed or unclear content - extract both types
                        artifacts_result = await self._extract_and_merge_artifacts(
                            file_path, content, content_classification, report, dry_run
                        )
                        discussions_result = await self._extract_and_merge_discussions(
                            file_path, content, content_classification, report, dry_run
                        )
                        
                        # Combine results
                        file_detail['items_extracted'] = (
                            artifacts_result.get('items_extracted', 0) + 
                            discussions_result.get('items_extracted', 0)
                        )
                        file_detail['items_new'] = (
                            artifacts_result.get('items_new', 0) + 
                            discussions_result.get('items_new', 0)
                        )
                        file_detail['items_updated'] = (
                            artifacts_result.get('items_updated', 0) + 
                            discussions_result.get('items_updated', 0)
                        )
                        file_detail['items_superseded'] = (
                            artifacts_result.get('items_superseded', 0) + 
                            discussions_result.get('items_superseded', 0)
                        )
                    
                    report['file_details'].append(file_detail)
                    report['files_processed'] += 1
                    
                    # Determine file status
                    if file_detail['items_new'] > 0 and file_detail['items_updated'] == 0:
                        report['files_new'] += 1
                    elif file_detail['items_updated'] > 0 or file_detail['items_superseded'] > 0:
                        report['files_updated'] += 1
                    
                    logger.info(f"Other markdown processed: {file_path.name} "
                              f"({file_detail['items_extracted']} items, {content_classification['type']})")
                    
                except Exception as e:
                    error_msg = f"Error processing other markdown {file_path.name}: {str(e)}"
                    logger.error(error_msg)
                    report['errors'].append(error_msg)
            
        except Exception as e:
            error_msg = f"Error in smart_migrate_other_markdown: {str(e)}"
            logger.error(error_msg)
            report['errors'].append(error_msg)

    # =============================================================================
    # CONTENT EXTRACTION METHODS (Enhanced from original migration.py)
    # =============================================================================
    
    async def _extract_patterns(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract patterns from systemPatterns.md or similar files"""
        
        patterns = []
        sections = self._split_into_sections(content)
        
        for section in sections:
            if section.get('title') and section.get('content'):
                title = section['title']
                section_content = section['content']
                
                # Look for pattern indicators
                is_pattern = any(keyword in title.lower() for keyword in 
                               ['pattern', 'template', 'component', 'approach', 'method'])
                
                if is_pattern or len(section_content) > 100:  # Substantial content
                    
                    # Extract code blocks
                    code_blocks = re.findall(r'```(\w+)?\n(.*?)```', section_content, re.DOTALL)
                    language = code_blocks[0][0] if code_blocks and code_blocks[0][0] else 'text'
                    
                    # Extract tags from content
                    tags = self._extract_tags_from_text(title + ' ' + section_content)
                    
                    patterns.append({
                        'name': title,
                        'content': section_content,
                        'language': language,
                        'tags': tags,
                        'filename': file_path.name
                    })
        
        return patterns
    
    async def _extract_progress(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract progress items from progress.md or journal files"""
        
        progress_items = []
        lines = content.split('\n')
        
        # Look for task patterns
        task_patterns = [
            r'^\s*[-*]\s*\[([x ])\]\s*(.+)$',  # - [x] Task or - [ ] Task
            r'^\s*[-*]\s*(TODO|DONE|IN PROGRESS|BLOCKED):\s*(.+)$',  # - TODO: Task
            r'^#{1,3}\s*(TODO|DONE|IN PROGRESS|BLOCKED):\s*(.+)$'   # ## TODO: Task
        ]
        
        for line_num, line in enumerate(lines, 1):
            for pattern in task_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 2 and match.group(1) in ['x', ' ']:
                        # Checkbox pattern
                        implemented = match.group(1) == 'x'
                        summary = match.group(2).strip()
                    else:
                        # Status pattern
                        status = match.group(1).upper()
                        summary = match.group(2).strip()
                        implemented = status == 'DONE'
                    
                    # Get additional context from following lines
                    context_lines = []
                    for i in range(line_num, min(line_num + 3, len(lines))):
                        if i < len(lines) and lines[i].strip() and not lines[i].startswith(('#', '-', '*')):
                            context_lines.append(lines[i].strip())
                    
                    progress_items.append({
                        'summary': summary,
                        'content': '\n'.join(context_lines) if context_lines else summary,
                        'implemented': implemented,
                        'tags': self._extract_tags_from_text(summary)
                    })
                    break
        
        return progress_items
    
    async def _extract_journal_decisions(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract decisions from journal entries"""
        
        decisions = []
        
        # Look for decision patterns
        decision_patterns = [
            r'^#{1,3}\s*(?:Decision|DECISION):\s*(.+?)$',
            r'^\*\*(?:Decision|DECISION):\*\*\s*(.+?)$',
            r'^\s*[-*]\s*(?:Decision|DECISION):\s*(.+?)$',
        ]
        
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for pattern in decision_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    summary = match.group(1).strip()
                    
                    # Extract following content as rationale
                    rationale_lines = []
                    for i in range(line_num, min(line_num + 5, len(lines))):
                        if i < len(lines):
                            following_line = lines[i].strip()
                            if following_line and not following_line.startswith(('#', '-', '*', '**')):
                                rationale_lines.append(following_line)
                    
                    decisions.append({
                        'summary': summary,
                        'content': '\n'.join(rationale_lines) if rationale_lines else summary,
                        'implemented': None,  # Unknown from journal
                        'tags': self._extract_tags_from_text(summary)
                    })
                    break
        
        return decisions
    
    # =============================================================================
    # SMART MERGE ANALYSIS METHODS
    # =============================================================================
    
    def _analyze_content_changes(self, current_items: List[Dict], existing_items: List[Dict], 
                                key_field: str) -> Dict[str, List]:
        """
        Analyze changes between current file content and existing database records
        
        Uses filesystem metadata approach - when file has changed, we do full replacement
        rather than complex content diffing. This is simpler and more reliable.
        
        Args:
            current_items: Items extracted from current file
            existing_items: Items from database for this source file
            key_field: Field to use for matching (e.g., 'title', 'summary')
            
        Returns:
            Dict with 'new_items', 'updated_items', 'obsolete_items'
        """
        
        # Build lookup maps for comparison
        current_by_key = {item.get(key_field, ''): item for item in current_items}
        existing_by_key = {item.get(key_field, ''): item for item in existing_items}
        
        # Find new items (in current but not in existing)
        new_items = []
        for key, item in current_by_key.items():
            if key not in existing_by_key:
                new_items.append(item)
        
        # Find updated items (in both, but content may have changed)
        updated_items = []
        for key, current_item in current_by_key.items():
            if key in existing_by_key:
                existing_item = existing_by_key[key]
                
                # Compare content signatures to detect changes
                current_signature = self._create_content_signature(current_item.get('content', ''))
                existing_signature = existing_item.get('content_signature', '')
                
                if current_signature != existing_signature:
                    updated_items.append({
                        'current': current_item,
                        'existing_uuid': existing_item.get('uuid', '')
                    })
        
        # Find obsolete items (in existing but not in current)
        obsolete_items = []
        for key, item in existing_by_key.items():
            if key not in current_by_key:
                obsolete_items.append(item)
        
        return {
            'new_items': new_items,
            'updated_items': updated_items,
            'obsolete_items': obsolete_items
        }
    
    def _create_content_signature(self, content: str) -> str:
        """
        Create a hash signature of content for change detection
        
        Args:
            content: Content to hash
            
        Returns:
            SHA-256 hash of the content
        """
        
        if not content:
            return ''
        
        # Normalize content by removing extra whitespace and line endings
        normalized_content = re.sub(r'\s+', ' ', content.strip())
        
        # Create SHA-256 hash
        return hashlib.sha256(normalized_content.encode('utf-8')).hexdigest()[:16]  # First 16 chars for brevity

    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def _parse_markdown_structure(self, content: str) -> Dict[str, Any]:
        """Parse markdown into structured data"""
        
        structure = {}
        sections = self._split_into_sections(content)
        
        for section in sections:
            title = section.get('title', '').lower().replace(' ', '_')
            if title:
                structure[title] = section.get('content', '')
        
        # Extract lists as structured data
        active_items = []
        for section in sections:
            if 'todo' in section.get('title', '').lower() or 'progress' in section.get('title', '').lower():
                items = re.findall(r'^\s*[-*]\s*(.+)$', section.get('content', ''), re.MULTILINE)
                active_items.extend(items)
        
        structure['active_items'] = active_items
        
        return structure
    
    def _split_into_sections(self, content: str) -> List[Dict[str, str]]:
        """Split markdown content into sections by headers"""
        
        sections = []
        lines = content.split('\n')
        current_section = {'title': '', 'content': ''}
        
        for line in lines:
            if line.startswith('#'):
                # Save previous section
                if current_section['title'] or current_section['content']:
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': line.lstrip('#').strip(),
                    'content': ''
                }
            else:
                current_section['content'] += line + '\n'
        
        # Save final section
        if current_section['title'] or current_section['content']:
            sections.append(current_section)
        
        return sections
    
    def _extract_tags_from_text(self, text: str) -> List[str]:
        """Extract meaningful tags from text"""
        
        # Ensure we have valid text input
        if not text or not isinstance(text, str):
            return []
        
        # Common technology and methodology keywords
        keywords = [
            'django', 'python', 'bootstrap', 'postgresql', 'sqlite', 'javascript', 'css', 'html',
            'api', 'rest', 'database', 'frontend', 'backend', 'ui', 'ux', 'responsive',
            'authentication', 'security', 'performance', 'testing', 'deployment', 'pattern',
            'component', 'template', 'config', 'rules', 'guidelines', 'documentation'
        ]
        
        text_lower = text.lower()
        found_tags = []
        
        for keyword in keywords:
            if keyword in text_lower:
                found_tags.append(keyword)
        
        # Add file-based tags
        if 'todo' in text_lower or 'task' in text_lower:
            found_tags.append('task')
        if 'bug' in text_lower or 'fix' in text_lower:
            found_tags.append('bugfix')
        if 'feature' in text_lower:
            found_tags.append('feature')
        
        return list(set(found_tags))[:5]  # Return unique tags, max 5
        
    
    # =============================================================================
    # HELPER METHODS FOR MISSING SMART MIGRATE FUNCTIONS
    # Generated: 2025-07-16.1321
    # =============================================================================
    
    async def _extract_markdown_rules(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract rules from markdown files like global_rules.md"""
        
        rules = []
        sections = self._split_into_sections(content)
        
        for section in sections:
            if section.get('title') and section.get('content'):
                title = section['title']
                section_content = section['content'].strip()
                
                # Skip empty sections
                if not section_content:
                    continue
                
                # Extract tags from rule content
                tags = self._extract_tags_from_text(title + ' ' + section_content)
                tags.append('rules')  # Always add rules tag
                
                rules.append({
                    'title': f"Rule: {title}",
                    'content': section_content,
                    'filename': file_path.name,
                    'tags': tags,
                    'rule_category': self._classify_rule_category(title, section_content)
                })
        
        # If no sections found, treat entire content as single rule
        if not rules and content.strip():
            rules.append({
                'title': f"Rules from {file_path.name}",
                'content': content.strip(),
                'filename': file_path.name,
                'tags': ['rules'],
                'rule_category': 'general'
            })
        
        return rules
    
    async def _extract_config_rules(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract rules from config-style files like .membankrules"""
        
        rules = []
        
        # Try to parse as line-based configuration
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if lines:
            # Group related lines into rule sections
            current_rule = {'lines': [], 'title': ''}
            rule_sections = []
            
            for line in lines:
                # Check if this looks like a section header
                if line.startswith('#') or line.endswith(':') or line.upper() == line:
                    # Save previous rule if it has content
                    if current_rule['lines']:
                        rule_sections.append(current_rule)
                    
                    # Start new rule section
                    current_rule = {
                        'title': line.strip('#: '),
                        'lines': []
                    }
                else:
                    current_rule['lines'].append(line)
            
            # Add final rule
            if current_rule['lines']:
                rule_sections.append(current_rule)
            
            # Convert rule sections to rule objects
            for i, rule_section in enumerate(rule_sections):
                title = rule_section['title'] or f"Config Rule {i+1}"
                content = '\n'.join(rule_section['lines'])
                
                if content:  # Only add non-empty rules
                    rules.append({
                        'title': f"Config: {title}",
                        'content': content,
                        'filename': file_path.name,
                        'tags': ['rules', 'config'],
                        'rule_category': 'configuration'
                    })
        
        # Fallback: treat entire file as single rule
        if not rules and content.strip():
            rules.append({
                'title': f"Configuration from {file_path.name}",
                'content': content.strip(),
                'filename': file_path.name,
                'tags': ['rules', 'config'],
                'rule_category': 'configuration'
            })
        
        return rules
    
    def _classify_rule_category(self, title: str, content: str) -> str:
        """Classify rule into category based on title and content"""
        
        title_lower = title.lower()
        content_lower = content.lower()
        
        # Coding standards
        if any(keyword in title_lower for keyword in ['code', 'coding', 'style', 'format', 'syntax']):
            return 'coding_standards'
        
        # Workflow rules
        if any(keyword in title_lower for keyword in ['workflow', 'process', 'procedure', 'steps']):
            return 'workflow'
        
        # Documentation rules
        if any(keyword in title_lower for keyword in ['doc', 'comment', 'readme', 'documentation']):
            return 'documentation'
        
        # Security rules
        if any(keyword in title_lower for keyword in ['security', 'auth', 'permission', 'access']):
            return 'security'
        
        # Testing rules
        if any(keyword in title_lower for keyword in ['test', 'testing', 'spec', 'validation']):
            return 'testing'
        
        # Deployment rules
        if any(keyword in title_lower for keyword in ['deploy', 'build', 'release', 'production']):
            return 'deployment'
        
        return 'general'
    
    def _classify_markdown_content(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Classify markdown content to determine extraction approach"""
        
        content_lower = content.lower()
        filename_lower = file_path.name.lower()
        
        # Count different content indicators
        code_blocks = len(re.findall(r'```', content))
        task_items = len(re.findall(r'^\s*[-*]\s*\[([x ])\]', content, re.MULTILINE))
        decision_markers = len(re.findall(r'decision|todo|done|progress', content_lower))
        sections = len(re.findall(r'^#{1,3}\s', content, re.MULTILINE))
        
        # Classification scoring
        artifact_score = 0
        discussion_score = 0
        
        # Artifacts indicators
        if code_blocks > 2:
            artifact_score += 3
        if 'template' in filename_lower or 'pattern' in filename_lower:
            artifact_score += 2
        if 'component' in content_lower or 'class' in content_lower:
            artifact_score += 2
        if sections > 3:  # Well-structured content
            artifact_score += 1
        
        # Discussions indicators  
        if task_items > 0:
            discussion_score += 3
        if decision_markers > 2:
            discussion_score += 3
        if 'journal' in filename_lower or 'notes' in filename_lower:
            discussion_score += 2
        if 'progress' in filename_lower or 'status' in filename_lower:
            discussion_score += 2
        
        # Determine classification
        if artifact_score > discussion_score + 1:
            content_type = 'artifacts'
        elif discussion_score > artifact_score + 1:
            content_type = 'discussions'
        else:
            content_type = 'mixed'
        
        return {
            'type': content_type,
            'artifact_score': artifact_score,
            'discussion_score': discussion_score,
            'code_blocks': code_blocks,
            'task_items': task_items,
            'sections': sections
        }
    
    async def _extract_and_merge_artifacts(self, file_path: Path, content: str, 
                                         classification: Dict[str, Any], report: Dict[str, Any], 
                                         dry_run: bool) -> Dict[str, Any]:
        """Extract and merge artifacts from markdown content"""
        
        result = {
            'items_extracted': 0,
            'items_new': 0,
            'items_updated': 0,
            'items_superseded': 0
        }
        
        # Extract artifacts using existing pattern extraction logic
        current_artifacts = await self._extract_patterns(content, file_path)
        
        # Also look for code blocks as separate artifacts
        code_artifacts = self._extract_code_blocks_as_artifacts(content, file_path)
        current_artifacts.extend(code_artifacts)
        
        if not dry_run and current_artifacts:
            # Get existing artifacts from this file
            existing_records = await self.database.get_records_by_source_file(file_path, "artifacts")
            existing_artifacts = existing_records["artifacts"]
            
            # Perform Smart Merge
            merge_analysis = self._analyze_content_changes(current_artifacts, existing_artifacts, "title")
            
            # Process new artifacts
            for artifact in merge_analysis['new_items']:
                await self.database.save_artifact(
                    title=artifact['title'],
                    content=artifact['content'],
                    artifact_type=artifact.get('artifact_type', 'general'),
                    filename=artifact.get('filename', file_path.name),
                    source_file=file_path
                )
                result['items_new'] += 1
            
            # Process updated artifacts
            for artifact_data in merge_analysis['updated_items']:
                current_artifact, existing_uuid = artifact_data['current'], artifact_data['existing_uuid']
                
                # Mark old as superseded
                await self.database.mark_records_as_superseded([existing_uuid], "artifacts")
                
                # Add new version
                await self.database.save_artifact(
                    title=current_artifact['title'],
                    content=current_artifact['content'],
                    artifact_type=current_artifact.get('artifact_type', 'general'),
                    filename=current_artifact.get('filename', file_path.name),
                    source_file=file_path
                )
                result['items_updated'] += 1
                result['items_superseded'] += 1
            
            # Handle obsolete artifacts
            if merge_analysis['obsolete_items']:
                obsolete_uuids = [item['uuid'] for item in merge_analysis['obsolete_items']]
                await self.database.mark_records_as_superseded(obsolete_uuids, "artifacts")
                result['items_superseded'] += len(obsolete_uuids)
        
        result['items_extracted'] = len(current_artifacts)
        report['artifacts_migrated'] += result['items_new']
        report['artifacts_updated'] += result['items_updated']
        report['artifacts_superseded'] += result['items_superseded']
        
        return result
    
    async def _extract_and_merge_discussions(self, file_path: Path, content: str,
                                           classification: Dict[str, Any], report: Dict[str, Any],
                                           dry_run: bool) -> Dict[str, Any]:
        """Extract and merge discussions from markdown content"""
        
        result = {
            'items_extracted': 0,
            'items_new': 0,
            'items_updated': 0,
            'items_superseded': 0
        }
        
        # Extract discussions using existing logic
        current_discussions = await self._extract_progress(content, file_path)
        
        # Also extract decisions if present
        decisions = await self._extract_journal_decisions(content, file_path)
        current_discussions.extend(decisions)
        
        if not dry_run and current_discussions:
            # Get existing discussions from this file
            existing_records = await self.database.get_records_by_source_file(file_path, "discussions")
            existing_discussions = existing_records["discussions"]
            
            # Perform Smart Merge
            merge_analysis = self._analyze_content_changes(current_discussions, existing_discussions, "summary")
            
            # Process new discussions
            for discussion in merge_analysis['new_items']:
                await self.database.save_discussion(
                    summary=discussion['summary'],
                    content=discussion['content'],
                    implemented=discussion.get('implemented'),
                    tags=discussion.get('tags', []),
                    source_file=file_path
                )
                result['items_new'] += 1
            
            # Process updated discussions
            for discussion_data in merge_analysis['updated_items']:
                current_discussion, existing_uuid = discussion_data['current'], discussion_data['existing_uuid']
                
                # Mark old as superseded
                await self.database.mark_records_as_superseded([existing_uuid], "discussions")
                
                # Add new version
                await self.database.save_discussion(
                    summary=current_discussion['summary'],
                    content=current_discussion['content'],
                    implemented=current_discussion.get('implemented'),
                    tags=current_discussion.get('tags', []),
                    source_file=file_path
                )
                result['items_updated'] += 1
                result['items_superseded'] += 1
            
            # Handle obsolete discussions
            if merge_analysis['obsolete_items']:
                obsolete_uuids = [item['uuid'] for item in merge_analysis['obsolete_items']]
                await self.database.mark_records_as_superseded(obsolete_uuids, "discussions")
                result['items_superseded'] += len(obsolete_uuids)
        
        result['items_extracted'] = len(current_discussions)
        report['discussions_migrated'] += result['items_new']
        report['discussions_updated'] += result['items_updated']
        report['discussions_superseded'] += result['items_superseded']
        
        return result
    
    def _extract_code_blocks_as_artifacts(self, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Extract standalone code blocks as artifacts"""
        
        artifacts = []
        
        # Find all code blocks with optional language and preceding context
        code_pattern = r'(?:^|\n)(?:.*?)```(?:(\w+))?\n(.*?)```'
        matches = re.findall(code_pattern, content, re.DOTALL)
        
        for i, (language, code) in enumerate(matches):
            if code.strip():  # Only non-empty code blocks
                # Try to find a title from preceding text
                title = f"Code Block {i+1}"
                if language:
                    title = f"{language.title()} Code Block {i+1}"
                
                # Extract tags
                tags = self._extract_tags_from_text(code) or []
                if language:
                    tags.append(language)
                
                artifacts.append({
                    'title': title,
                    'content': code.strip(),
                    'language': language or 'text',
                    'artifact_type': 'code',
                    'filename': file_path.name,
                    'tags': tags
                })
        
        return artifacts


# =============================================================================
# BACKWARD COMPATIBILITY - Legacy MemoryBankMigrator class
# =============================================================================

class MemoryBankMigrator(SmartMergeMigrator):
    """
    Legacy compatibility class - redirects to SmartMergeMigrator
    
    This maintains backward compatibility with existing code that uses MemoryBankMigrator
    while providing all the enhanced Smart Merge capabilities.
    """
    
    def __init__(self, project_path: Path):
        super().__init__(project_path)
        logger.info(f"Legacy MemoryBankMigrator initialized (using SmartMergeMigrator)")


# =============================================================================
# CLI INTERFACE FOR MIGRATION TOOL
# =============================================================================

async def migrate_project_cli(project_path: str, dry_run: bool = False, force: bool = False) -> None:
    """CLI interface for migrating a project with Smart Merge"""
    
    migrator = SmartMergeMigrator(Path(project_path))
    report = await migrator.migrate_project(dry_run=dry_run, force=force)
    
    print(f"\n{'='*60}")
    print(f"SMART MERGE MIGRATION {'ANALYSIS' if dry_run else 'REPORT'}")
    print(f"{'='*60}")
    
    print(f"Project: {report['project_name']}")
    print(f"Path: {report['project_path']}")
    print(f"Status: {report['status'].upper()}")
    print(f"Smart Merge: {'ENABLED' if report.get('smart_merge_enabled') else 'DISABLED'}")
    
    if report['status'] == 'completed':
        print(f"\n📊 FILE ANALYSIS:")
        print(f"  • Files Analyzed: {report.get('files_processed', 0) + report.get('files_skipped_unchanged', 0)}")
        print(f"  • Files Processed: {report.get('files_processed', 0)}")
        print(f"  • Files Skipped (Unchanged): {report.get('files_skipped_unchanged', 0)}")
        print(f"  • Files New: {report.get('files_new', 0)}")
        print(f"  • Files Updated: {report.get('files_updated', 0)}")
        
        print(f"\n💭 DISCUSSIONS:")
        print(f"  • New Discussions: {report.get('discussions_migrated', 0)}")
        print(f"  • Updated Discussions: {report.get('discussions_updated', 0)}")
        print(f"  • Superseded Discussions: {report.get('discussions_superseded', 0)}")
        
        print(f"\n📄 ARTIFACTS:")
        print(f"  • New Artifacts: {report.get('artifacts_migrated', 0)}")
        print(f"  • Updated Artifacts: {report.get('artifacts_updated', 0)}")
        print(f"  • Superseded Artifacts: {report.get('artifacts_superseded', 0)}")
        
        if report.get('change_summary'):
            summary = report['change_summary']
            print(f"\n⚡ EFFICIENCY:")
            print(f"  • Skip Ratio: {summary.get('efficiency_ratio', 0)}% (files unchanged)")
        
        if report['file_details']:
            print(f"\n📋 FILE DETAILS:")
            for detail in report['file_details']:
                status_icon = "🆕" if detail.get('status') == 'new' else "🔄" if detail.get('items_updated', 0) > 0 else "📄"
                print(f"  {status_icon} {detail['filename']} ({detail['content_type']}): "
                      f"{detail.get('items_extracted', 0)} items extracted")
    
    if report['errors']:
        print(f"\n❌ ERRORS ({len(report['errors'])}):")
        for error in report['errors']:
            print(f"  • {error}")
    
    if report.get('warnings'):
        print(f"\n⚠️ WARNINGS ({len(report['warnings'])}):")
        for warning in report['warnings']:
            print(f"  • {warning}")
    
async def discover_and_import_all_markdown(project_path: Path, 
                                         exclude_patterns: List[str] = None,
                                         max_file_size: int = 10 * 1024 * 1024) -> Dict[str, Any]:
    """
    Discover and import all markdown files in a project with intelligent filtering
    
    Args:
        project_path: Path to project root
        exclude_patterns: List of glob patterns to exclude (e.g., ['node_modules/*', '.git/*'])
        max_file_size: Maximum file size in bytes (default: 10MB)
        
    Returns:
        Dict with comprehensive discovery and import results
    """
    
    project_path = Path(project_path)
    
    # Default exclusion patterns
    if exclude_patterns is None:
        exclude_patterns = [
            '.git/*',
            'node_modules/*',
            'venv/*',
            '.venv/*',
            '__pycache__/*',
            '*.egg-info/*',
            'build/*',
            'dist/*',
            '.idea/*',
            '.vscode/*',
            'target/*',
            'out/*'
        ]
    
    results = {
        "success": True,
        "project_path": str(project_path),
        "total_discovered": 0,
        "total_imported": 0,
        "excluded_count": 0,
        "oversized_count": 0,
        "errors": [],
        "categories": {
            "documentation": {"count": 0, "files": []},
            "readme": {"count": 0, "files": []},
            "changelog": {"count": 0, "files": []},
            "memory_bank": {"count": 0, "files": []},
            "general": {"count": 0, "files": []}
        }
    }
    
    # Initialize database
    database = MemoryBankDatabase(project_path)
    await database.initialize()
    
    try:
        # Discover all markdown files
        all_md_files = list(project_path.rglob("*.md"))
        results["total_discovered"] = len(all_md_files)
        
        # Filter and categorize files
        for file_path in all_md_files:
            try:
                # Check exclusion patterns
                relative_path = file_path.relative_to(project_path)
                excluded = False
                
                for pattern in exclude_patterns:
                    if relative_path.match(pattern):
                        excluded = True
                        break
                
                if excluded:
                    results["excluded_count"] += 1
                    continue
                
                # Check file size
                file_size = file_path.stat().st_size
                if file_size > max_file_size:
                    results["oversized_count"] += 1
                    continue
                
                # Categorize file
                category = _categorize_markdown_file(file_path)
                
                # Read and import file
                content = file_path.read_text(encoding='utf-8')
                filename = file_path.name
                
                # Check if already imported
                existing = await database.execute_sql_query(
                    f"SELECT uuid FROM markdown_files WHERE file_path = '{file_path}' AND project_uuid = '{database.project_uuid}'"
                )
                
                if existing.get('results'):
                    continue
                
                # Import file
                file_uuid = await database.save_markdown_file(
                    filename=filename,
                    file_path=str(file_path),
                    content=content,
                    content_type=category
                )
                
                # Track in results
                file_info = {
                    "filename": filename,
                    "file_path": str(file_path),
                    "uuid": file_uuid,
                    "size": file_size,
                    "content_length": len(content)
                }
                
                results["categories"][category]["count"] += 1
                results["categories"][category]["files"].append(file_info)
                results["total_imported"] += 1
                
                logger.info(f"Imported {category} file: {filename}")
                
            except Exception as e:
                error_msg = f"Error processing {file_path}: {str(e)}"
                results["errors"].append(error_msg)
                logger.error(error_msg)
        
        # Sync FTS tables
        await database.sync_fts_tables()
        
        # Set success status
        results["success"] = len(results["errors"]) == 0
        
    except Exception as e:
        logger.error(f"Error in comprehensive markdown discovery: {e}")
        results["success"] = False
        results["errors"].append(str(e))
    finally:
        await database.close()
    
    return results


def _categorize_markdown_file(file_path: Path) -> str:
    """Categorize a markdown file based on its name and location"""
    
    filename_lower = file_path.name.lower()
    parent_name = file_path.parent.name.lower()
    
    # Memory bank files
    if 'memory-bank' in str(file_path):
        return 'memory_bank'
    
    # README files
    if filename_lower.startswith('readme'):
        return 'readme'
    
    # Changelog files
    if any(name in filename_lower for name in ['changelog', 'changes', 'history', 'news']):
        return 'changelog'
    
    # Documentation files
    if any(keyword in parent_name for keyword in ['doc', 'documentation', 'guide', 'manual', 'spec', 'wiki']):
        return 'documentation'
    
    if any(keyword in filename_lower for keyword in ['guide', 'manual', 'spec', 'tutorial', 'howto', 'faq']):
        return 'documentation'
    
    # Default category
    return 'general'


async def cleanup_duplicate_markdown_files(project_path: Path) -> Dict[str, Any]:
    """
    Clean up duplicate markdown file entries based on file path and content signature
    
    Args:
        project_path: Path to project root
        
    Returns:
        Dict with cleanup results
    """
    
    # Initialize database
    database = MemoryBankDatabase(project_path)
    await database.initialize()
    
    results = {
        "success": True,
        "duplicates_found": 0,
        "duplicates_removed": 0,
        "errors": []
    }
    
    try:
        # Find duplicate file paths
        duplicate_query = """
        SELECT file_path, COUNT(*) as count, GROUP_CONCAT(uuid) as uuids
        FROM markdown_files 
        WHERE project_uuid = ?
        GROUP BY file_path 
        HAVING COUNT(*) > 1
        """
        
        duplicates_result = await database.execute_sql_query(
            duplicate_query.replace('?', f"'{database.project_uuid}'")
        )
        
        if duplicates_result.get('results'):
            for row in duplicates_result['results']:
                file_path = row['file_path']
                count = row['count']
                uuids = row['uuids'].split(',')
                
                results["duplicates_found"] += count - 1  # Keep one, remove others
                
                # Keep the most recent entry, remove others
                for uuid_to_remove in uuids[1:]:  # Skip first UUID
                    delete_result = await database.execute_sql_query(
                        f"DELETE FROM markdown_files WHERE uuid = '{uuid_to_remove}'"
                    )
                    
                    if delete_result.get('success'):
                        results["duplicates_removed"] += 1
                        logger.info(f"Removed duplicate markdown file: {file_path}")
                    else:
                        error_msg = f"Failed to remove duplicate: {uuid_to_remove}"
                        results["errors"].append(error_msg)
        
        # Sync FTS tables after cleanup
        await database.sync_fts_tables()
        
    except Exception as e:
        logger.error(f"Error during duplicate cleanup: {e}")
        results["success"] = False
        results["errors"].append(str(e))
    finally:
        await database.close()
    
    return results


async def generate_markdown_import_report(project_path: Path) -> str:
    """
    Generate a comprehensive report of imported markdown files
    
    Args:
        project_path: Path to project root
        
    Returns:
        Formatted report string
    """
    
    # Initialize database
    database = MemoryBankDatabase(project_path)
    await database.initialize()
    
    try:
        # Get markdown file statistics
        stats_query = """
        SELECT 
            content_type,
            COUNT(*) as count,
            SUM(file_size) as total_size,
            AVG(file_size) as avg_size,
            MIN(created_at) as first_imported,
            MAX(created_at) as last_imported
        FROM markdown_files 
        WHERE project_uuid = ?
        GROUP BY content_type
        ORDER BY count DESC
        """
        
        stats_result = await database.execute_sql_query(
            stats_query.replace('?', f"'{database.project_uuid}'")
        )
        
        # Get total count
        total_query = f"SELECT COUNT(*) as total FROM markdown_files WHERE project_uuid = '{database.project_uuid}'"
        total_result = await database.execute_sql_query(total_query)
        total_count = total_result.get('results', [{}])[0].get('total', 0)
        
        # Generate report
        report = f"""
📝 **MARKDOWN FILES IMPORT REPORT**
Project: {project_path.name}
Path: {project_path}

📊 **OVERVIEW:**
• Total Files: {total_count}
• Categories: {len(stats_result.get('results', []))}
• Full-Text Search: ✅ Enabled

📋 **BY CATEGORY:**
"""
        
        if stats_result.get('results'):
            for row in stats_result['results']:
                content_type = row['content_type']
                count = row['count']
                total_size = row['total_size'] or 0
                avg_size = row['avg_size'] or 0
                
                # Format sizes
                if total_size > 1024 * 1024:
                    size_str = f"{total_size / (1024 * 1024):.1f} MB"
                elif total_size > 1024:
                    size_str = f"{total_size / 1024:.1f} KB"
                else:
                    size_str = f"{total_size} bytes"
                
                report += f"""
🏷️ **{content_type.title()}**
  • Files: {count}
  • Total Size: {size_str}
  • Avg Size: {avg_size:.0f} bytes
"""
        
        # Get recent imports
        recent_query = f"""
        SELECT filename, content_type, created_at, file_size
        FROM markdown_files 
        WHERE project_uuid = '{database.project_uuid}'
        ORDER BY created_at DESC 
        LIMIT 10
        """
        
        recent_result = await database.execute_sql_query(recent_query)
        
        if recent_result.get('results'):
            report += "\n📅 **RECENT IMPORTS:**\n"
            for row in recent_result['results']:
                filename = row['filename']
                content_type = row['content_type']
                created_at = row['created_at']
                file_size = row['file_size']
                
                size_str = f"{file_size} bytes" if file_size < 1024 else f"{file_size / 1024:.1f} KB"
                report += f"• {filename} ({content_type}) - {size_str} - {created_at}\n"
        
        report += f"\n🔍 **All files are now searchable with full-text search capabilities!**"
        
        return report.strip()
        
    except Exception as e:
        logger.error(f"Error generating markdown import report: {e}")
        return f"❌ Error generating report: {str(e)}"
    finally:
        await database.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python migration.py <project_path> [--dry-run] [--force]")
        print("  --dry-run: Analyze files but don't write to database")
        print("  --force: Re-migrate all files regardless of timestamps")
        sys.exit(1)
    
    project_path = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    force = '--force' in sys.argv
    
    asyncio.run(migrate_project_cli(project_path, dry_run, force))
