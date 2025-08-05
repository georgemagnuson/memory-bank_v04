"""
migration_modules/markdown_importer.py
Generated: 2025-07-29.2316
Purpose: Markdown file discovery and import for Memory Bank v2.0 unified document architecture
Handles bulk markdown file processing and classification
"""

import logging
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger("memory_bank_mcp.migration.markdown")


class MarkdownImporter:
    """Markdown file discovery and import for unified document architecture"""
    
    def __init__(self, context_manager=None):
        self.context_manager = context_manager
        self.max_file_size = 10 * 1024 * 1024  # 10MB default
        
    def discover_and_import_all_markdown(self, directory_path: str, 
                                       exclude_patterns: List[str] = None,
                                       max_file_size_mb: int = 10) -> Dict[str, Any]:
        """
        Discover and import all markdown files in a directory tree
        
        Args:
            directory_path: Root directory to search
            exclude_patterns: Patterns to exclude from import
            max_file_size_mb: Maximum file size to process
            
        Returns:
            Import results with statistics
        """
        from .content_extractors import ContentExtractors
        from .migration_cli import MigrationUtilities
        
        results = {
            'directory_path': directory_path,
            'files_found': 0,
            'files_imported': 0,
            'files_skipped': 0,
            'files_failed': 0,
            'total_size_mb': 0,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'file_details': [],
            'errors': [],
            'warnings': []
        }
        
        exclude_patterns = exclude_patterns or []
        self.max_file_size = max_file_size_mb * 1024 * 1024
        
        try:
            directory = Path(directory_path)
            if not directory.exists() or not directory.is_dir():
                results['errors'].append(f"Directory not found: {directory_path}")
                return results
            
            # Discover all markdown files
            markdown_files = list(directory.rglob("*.md"))
            results['files_found'] = len(markdown_files)
            
            logger.info(f"Found {len(markdown_files)} markdown files in {directory_path}")
            
            # Process each file
            for md_file in markdown_files:
                try:
                    # Check exclusion patterns
                    if self._should_exclude_file(md_file, exclude_patterns):
                        results['files_skipped'] += 1
                        continue
                    
                    # Check file size
                    file_size = md_file.stat().st_size
                    if file_size > self.max_file_size:
                        results['warnings'].append(f"File too large, skipped: {md_file.name} ({file_size/1024/1024:.1f}MB)")
                        results['files_skipped'] += 1
                        continue
                    
                    # Import the file
                    import_result = self._import_markdown_file(md_file)
                    
                    if import_result['success']:
                        results['files_imported'] += 1
                        results['total_size_mb'] += file_size / (1024 * 1024)
                        
                        results['file_details'].append({
                            'filename': md_file.name,
                            'path': str(md_file.relative_to(directory)),
                            'size_kb': round(file_size / 1024, 1),
                            'document_type': import_result.get('document_type', 'unknown'),
                            'status': 'imported'
                        })
                    else:
                        results['files_failed'] += 1
                        results['errors'].append(f"Failed to import {md_file.name}: {import_result.get('error', 'Unknown error')}")
                        
                        results['file_details'].append({
                            'filename': md_file.name,
                            'path': str(md_file.relative_to(directory)),
                            'size_kb': round(file_size / 1024, 1),
                            'status': 'failed',
                            'error': import_result.get('error', 'Unknown error')
                        })
                
                except Exception as e:
                    results['files_failed'] += 1
                    error_msg = f"Error processing {md_file.name}: {str(e)}"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
            
            results['end_time'] = datetime.now(timezone.utc).isoformat()
            results['status'] = 'completed'
            
            logger.info(f"Markdown import completed: {results['files_imported']} imported, "
                       f"{results['files_skipped']} skipped, {results['files_failed']} failed")
            
        except Exception as e:
            error_msg = f"Failed to discover markdown files: {str(e)}"
            results['errors'].append(error_msg)
            results['status'] = 'failed'
            logger.error(error_msg)
        
        return results
    
    def _should_exclude_file(self, file_path: Path, exclude_patterns: List[str]) -> bool:
        """Check if file should be excluded based on patterns"""
        file_str = str(file_path).lower()
        
        # Default exclusions
        default_exclusions = [
            'node_modules',
            '.git',
            '__pycache__',
            '.vscode',
            'build',
            'dist',
            '.next',
            'coverage'
        ]
        
        all_patterns = default_exclusions + exclude_patterns
        
        for pattern in all_patterns:
            if pattern.lower() in file_str:
                return True
        
        return False
    
    def _import_markdown_file(self, file_path: Path) -> Dict[str, Any]:
        """Import a single markdown file to unified documents"""
        from .content_extractors import ContentExtractors
        from .migration_cli import MigrationUtilities
        
        result = {
            'success': False,
            'document_type': 'unknown',
            'error': None
        }
        
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='replace')
            
            # Classify content to determine document type
            classification = ContentExtractors.classify_markdown_content(content, file_path)
            document_type = classification['document_type']
            
            # Use filename-based classification as fallback
            if classification['confidence'] == 0:
                document_type = MigrationUtilities.categorize_file_by_name(file_path)
            
            # Create title from filename
            title = file_path.stem.replace('_', ' ').replace('-', ' ').title()
            
            # Save to unified documents table
            if self.context_manager:
                import asyncio
                asyncio.run(self._save_markdown_as_document(
                    title=title,
                    content=content,
                    document_type=document_type,
                    source_file=str(file_path),
                    classification=classification
                ))
            
            result['success'] = True
            result['document_type'] = document_type
            
            logger.debug(f"Imported {file_path.name} as {document_type}")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Failed to import {file_path.name}: {e}")
        
        return result
    
    async def _save_markdown_as_document(self, title: str, content: str, document_type: str,
                                       source_file: str, classification: Dict[str, Any]) -> None:
        """Save markdown content as unified document"""
        import uuid as uuid_module
        import json
        
        document_uuid = str(uuid_module.uuid4())
        project_uuid = self.context_manager.database.project_uuid
        
        # Generate content signature
        from .smart_merge import SmartMergeEngine
        merge_engine = SmartMergeEngine(self.context_manager)
        content_signature = merge_engine._generate_content_signature(content)
        
        # Build metadata
        metadata = {
            'imported_from': 'markdown_file',
            'source_file': source_file,
            'import_timestamp': datetime.now(timezone.utc).isoformat(),
            'classification': classification,
            'file_size': len(content),
            'confidence_score': classification.get('confidence', 0)
        }
        
        query = """
        INSERT INTO unified_documents 
        (uuid, project_uuid, title, content, document_type, source_file, 
         content_signature, record_status, created_at, updated_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
        """
        
        await self.context_manager.database._execute_query(
            query, (document_uuid, project_uuid, title, content, document_type, 
                   source_file, content_signature, json.dumps(metadata))
        )
        
        logger.debug(f"Saved markdown as document: {title} (type: {document_type})")
    
    def import_markdown_files(self, directory_path: str, file_pattern: str = "*.md",
                            recursive: bool = True) -> Dict[str, Any]:
        """
        Import markdown files matching a specific pattern
        
        Args:
            directory_path: Directory to search
            file_pattern: File pattern to match (default: *.md)
            recursive: Whether to search recursively
            
        Returns:
            Import results
        """
        results = {
            'directory_path': directory_path,
            'pattern': file_pattern,
            'recursive': recursive,
            'files_found': 0,
            'files_imported': 0,
            'files_failed': 0,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'errors': []
        }
        
        try:
            directory = Path(directory_path)
            if not directory.exists():
                results['errors'].append(f"Directory not found: {directory_path}")
                return results
            
            # Find matching files
            if recursive:
                markdown_files = list(directory.rglob(file_pattern))
            else:
                markdown_files = list(directory.glob(file_pattern))
            
            results['files_found'] = len(markdown_files)
            
            # Import each file
            for md_file in markdown_files:
                import_result = self._import_markdown_file(md_file)
                
                if import_result['success']:
                    results['files_imported'] += 1
                else:
                    results['files_failed'] += 1
                    results['errors'].append(f"Failed to import {md_file.name}: {import_result.get('error', 'Unknown error')}")
            
            results['end_time'] = datetime.now(timezone.utc).isoformat()
            results['status'] = 'completed'
            
        except Exception as e:
            results['errors'].append(f"Import failed: {str(e)}")
            results['status'] = 'failed'
        
        return results
    
    def generate_import_report(self, context_manager) -> Dict[str, Any]:
        """Generate comprehensive report of imported markdown files"""
        
        try:
            # Query for imported markdown documents
            query = """
            SELECT title, document_type, source_file, created_at, metadata
            FROM unified_documents
            WHERE metadata LIKE '%markdown_file%' OR metadata LIKE '%imported_from%'
            ORDER BY document_type, title
            """
            
            import asyncio
            result = asyncio.run(context_manager.database._execute_query(query))
            
            report = {
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'total_imported': len(result) if result else 0,
                'by_document_type': {},
                'by_source_directory': {},
                'files': []
            }
            
            if result:
                import json
                
                for row in result:
                    title, doc_type, source_file, created_at, metadata_json = row
                    
                    # Parse metadata
                    metadata = {}
                    try:
                        metadata = json.loads(metadata_json) if metadata_json else {}
                    except:
                        pass
                    
                    # Count by document type
                    if doc_type not in report['by_document_type']:
                        report['by_document_type'][doc_type] = 0
                    report['by_document_type'][doc_type] += 1
                    
                    # Count by source directory
                    if source_file:
                        source_dir = str(Path(source_file).parent)
                        if source_dir not in report['by_source_directory']:
                            report['by_source_directory'][source_dir] = 0
                        report['by_source_directory'][source_dir] += 1
                    
                    # Add file details
                    report['files'].append({
                        'title': title,
                        'document_type': doc_type,
                        'source_file': source_file,
                        'created_at': created_at,
                        'file_size': metadata.get('file_size', 0),
                        'confidence': metadata.get('confidence_score', 0)
                    })
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate import report: {e}")
            return {'error': str(e), 'status': 'failed'}


# Legacy compatibility class
class MemoryBankMigrator:
    """
    Legacy compatibility wrapper for Memory Bank migration
    Maintains backward compatibility while using new unified architecture
    """
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.migrator = None
    
    def migrate_project(self, dry_run: bool = False) -> Dict[str, Any]:
        """Legacy interface for project migration"""
        from .migration_cli import MigrationCLI
        
        logger.warning("Using legacy MemoryBankMigrator interface. "
                      "Consider updating to UnifiedDocumentMigrator for v2.0 features.")
        
        return MigrationCLI.migrate_project_cli(
            project_path=str(self.project_path),
            dry_run=dry_run,
            force=False
        )
