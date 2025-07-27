#!/usr/bin/env python3
"""
Memory Bank v04 Enhanced - Content Tools Module
Filename: content_tools.py
Generated: 2025-07-27.1843
Purpose: Universal content search, import, and FTS management functionality

Content Tools Implementation:
- Universal full-text search across all content types with ranking and highlighting
- Markdown file import into database for full-text search
- FTS5 virtual table synchronization with main content tables
- Intelligent bulk markdown discovery and import with filtering
- Project documentation import with external source support
- Comprehensive markdown import reporting and statistics

v1.4.0 Features Preserved:
- Search prioritization (context.db content first)
- Enhanced metadata extraction and content signatures
- Multi-table content extraction with priority ordering
- Smart file filtering and duplicate detection
"""

import logging
import sqlite3
import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Set
from datetime import datetime
import mimetypes
import re

logger = logging.getLogger(__name__)

class ContentTools:
    """Content discovery, search, and import tools for Memory Bank v04"""
    
    def __init__(self, context_manager):
        """Initialize ContentTools with context manager dependency
        
        Args:
            context_manager: Active ContextManager instance with database connection
        """
        self.context_manager = context_manager
        self.logger = logger
        
        # Content type mappings for search
        self.content_tables = {
            'discussions': 'discussions_fts',
            'artifacts': 'artifacts_fts', 
            'code_iterations': 'code_iterations_fts',
            'plans': 'plans_fts',
            'markdown_files': 'markdown_search',
            'documents_v2': 'documents_v2_fts'
        }
        
        # Search result columns for each table type
        self.table_columns = {
            'discussions': ['uuid', 'summary', 'content', 'tags', 'updated_at'],
            'artifacts': ['uuid', 'title', 'content', 'artifact_type', 'filename', 'updated_at'],
            'code_iterations': ['uuid', 'filename', 'content', 'description', 'version_number', 'created_at'],
            'plans': ['uuid', 'title', 'description', 'phases', 'current_phase', 'updated_at'],
            'markdown_files': ['uuid', 'filename', 'file_path', 'content', 'updated_at'],
            'documents_v2': ['uuid', 'title', 'content', 'document_type', 'context_domain', 'spec_name', 'spec_phase', 'updated_at']
        }
        
        # File patterns for markdown discovery
        self.markdown_patterns = ['*.md', '*.markdown', '*.txt', '*.rst']
        self.exclude_patterns = {
            'node_modules', '.git', '__pycache__', '.pytest_cache', 
            'venv', 'env', '.env', 'dist', 'build', '.next',
            'coverage', '.coverage', '.nyc_output', 'logs'
        }
        
    async def search_all_content(self, query: str, limit: int = 20, content_types: str = "all") -> str:
        """Universal full-text search across all content types with ranking and highlighting
        
        Searches across: discussions, artifacts, code_iterations, plans, markdown_files, and documents_v2
        The documents_v2 table includes enhanced metadata for spec workflow integration.
        
        Args:
            query: Search query string
            limit: Maximum number of results to return (default: 20)
            content_types: Comma-separated content types or "all" (default: "all")
                          Options: discussions,artifacts,code_iterations,plans,markdown_files,documents_v2
        
        Returns:
            Formatted search results with ranking, highlighting, and metadata
        """
        try:
            if not self.context_manager or not self.context_manager.current_db_path:
                return "❌ **SEARCH FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            if not query.strip():
                return "❌ **SEARCH FAILED**\n\nQuery cannot be empty."
            
            # Parse content types
            if content_types.lower() == "all":
                search_tables = list(self.content_tables.keys())
            else:
                requested_types = [t.strip() for t in content_types.split(',')]
                search_tables = [t for t in requested_types if t in self.content_tables]
                if not search_tables:
                    return f"❌ **SEARCH FAILED**\n\nInvalid content types: {content_types}\nValid options: {', '.join(self.content_tables.keys())}"
            
            # Execute search across all requested tables
            all_results = []
            search_stats = {
                'query': query,
                'tables_searched': len(search_tables),
                'total_results': 0,
                'results_by_table': {}
            }
            
            conn = sqlite3.connect(self.context_manager.current_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            for table_name in search_tables:
                try:
                    fts_table = self.content_tables[table_name]
                    columns = self.table_columns[table_name]
                    
                    # Build FTS query with ranking
                    fts_query = f"""
                    SELECT 
                        main.{columns[0]} as uuid,
                        {', '.join([f'main.{col}' for col in columns[1:]])},
                        rank,
                        snippet({fts_table}, 2, '<mark>', '</mark>', '...', 64) as highlighted_content,
                        '{table_name}' as source_table
                    FROM {fts_table} fts
                    JOIN {table_name} main ON fts.uuid = main.uuid
                    WHERE {fts_table} MATCH ?
                    ORDER BY rank
                    LIMIT ?
                    """
                    
                    cursor.execute(fts_query, (query, limit))
                    table_results = cursor.fetchall()
                    
                    search_stats['results_by_table'][table_name] = len(table_results)
                    
                    # Process results with metadata
                    for row in table_results:
                        result = {
                            'uuid': row['uuid'],
                            'source_table': row['source_table'],
                            'rank': row['rank'],
                            'highlighted_content': row['highlighted_content'],
                            'metadata': {}
                        }
                        
                        # Add table-specific metadata
                        for col in columns[1:]:
                            if col in row.keys():
                                result['metadata'][col] = row[col]
                        
                        all_results.append(result)
                        
                except sqlite3.Error as e:
                    self.logger.warning(f"Search failed for table {table_name}: {e}")
                    search_stats['results_by_table'][table_name] = f"Error: {str(e)}"
            
            conn.close()
            
            # Sort all results by rank (lower rank = more relevant)
            all_results.sort(key=lambda x: x['rank'])
            final_results = all_results[:limit]
            search_stats['total_results'] = len(final_results)
            
            # Format results
            return self._format_search_results(final_results, search_stats, query)
            
        except Exception as e:
            self.logger.error(f"Universal search failed: {e}")
            return f"❌ **SEARCH FAILED**\n\nError: {str(e)}"
    
    def _format_search_results(self, results: List[Dict], stats: Dict, query: str) -> str:
        """Format search results with highlighting and metadata"""
        if not results:
            return f"""🔍 **SEARCH RESULTS**

**Query:** "{query}"
**Tables Searched:** {stats['tables_searched']}
**Total Results:** 0

❌ No results found.

**Search Statistics:**
{json.dumps(stats['results_by_table'], indent=2)}"""
        
        output = [f"""🔍 **SEARCH RESULTS**

**Query:** "{query}"
**Tables Searched:** {stats['tables_searched']}  
**Results Found:** {stats['total_results']}

"""]
        
        # Group results by source table for better organization
        results_by_table = {}
        for result in results:
            table = result['source_table']
            if table not in results_by_table:
                results_by_table[table] = []
            results_by_table[table].append(result)
        
        # Format results by table with v1.4.0 prioritization
        priority_order = ['documents_v2', 'discussions', 'artifacts', 'code_iterations', 'plans', 'markdown_files']
        
        for table in priority_order:
            if table not in results_by_table:
                continue
                
            table_results = results_by_table[table]
            output.append(f"## 📊 {table.upper()} ({len(table_results)} results)\n")
            
            for i, result in enumerate(table_results, 1):
                metadata = result['metadata']
                
                # Format title/summary based on table type
                if table == 'discussions':
                    title = metadata.get('summary', 'Untitled Discussion')
                elif table == 'artifacts':
                    title = metadata.get('title', metadata.get('filename', 'Untitled Artifact'))
                elif table == 'code_iterations':
                    title = f"{metadata.get('filename', 'Unknown File')} (v{metadata.get('version_number', '1')})"
                elif table == 'plans':
                    title = metadata.get('title', 'Untitled Plan')
                elif table == 'markdown_files':
                    title = metadata.get('filename', 'Unknown File')
                elif table == 'documents_v2':
                    title = metadata.get('title', 'Untitled Document')
                    if metadata.get('spec_name'):
                        title += f" ({metadata['spec_name']})"
                else:
                    title = 'Unknown Item'
                
                output.append(f"**{i}. {title}**")
                output.append(f"📍 *{table}* | UUID: `{result['uuid'][:8]}...` | Rank: {result['rank']}")
                
                # Add relevant metadata
                if table == 'documents_v2':
                    if metadata.get('document_type'):
                        output.append(f"🏷️ Type: {metadata['document_type']}")
                    if metadata.get('spec_phase'):
                        output.append(f"📋 Phase: {metadata['spec_phase']}")
                elif table == 'artifacts' and metadata.get('artifact_type'):
                    output.append(f"🏷️ Type: {metadata['artifact_type']}")
                elif table == 'plans':
                    if metadata.get('current_phase'):
                        output.append(f"📋 Phase: {metadata['current_phase']}")
                
                # Add highlighted content
                if result['highlighted_content']:
                    output.append(f"📄 {result['highlighted_content']}")
                
                output.append("")  # Empty line between results
        
        # Add search statistics
        output.append("## 📈 Search Statistics")
        for table, count in stats['results_by_table'].items():
            output.append(f"- **{table}**: {count} results")
        
        output.append(f"\n💡 **Tip**: Use `extract_large_document(\"title_search\")` to read complete content.")
        
        return "\n".join(output)
    
    async def sync_fts_tables(self) -> str:
        """Synchronize FTS5 virtual tables with main content tables
        
        Ensures all FTS indexes are up-to-date with the latest content from main tables.
        This should be run after bulk imports or when search results seem outdated.
        
        Returns:
            Status report of synchronization operation
        """
        try:
            if not self.context_manager or not self.context_manager.current_db_path:
                return "❌ **SYNC FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            conn = sqlite3.connect(self.context_manager.current_db_path)
            cursor = conn.cursor()
            
            sync_results = {
                'tables_synced': 0,
                'errors': [],
                'sync_details': {}
            }
            
            # Sync each FTS table
            for main_table, fts_table in self.content_tables.items():
                try:
                    # Check if tables exist
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (main_table,))
                    if not cursor.fetchone():
                        sync_results['errors'].append(f"Main table '{main_table}' not found")
                        continue
                    
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (fts_table,))
                    if not cursor.fetchone():
                        sync_results['errors'].append(f"FTS table '{fts_table}' not found")
                        continue
                    
                    # Get record counts before sync
                    cursor.execute(f"SELECT COUNT(*) FROM {main_table}")
                    main_count = cursor.fetchone()[0]
                    
                    cursor.execute(f"SELECT COUNT(*) FROM {fts_table}")
                    fts_count = cursor.fetchone()[0]
                    
                    # Perform sync by rebuilding FTS index
                    cursor.execute(f"INSERT INTO {fts_table}({fts_table}) VALUES('rebuild')")
                    
                    # Get record counts after sync
                    cursor.execute(f"SELECT COUNT(*) FROM {fts_table}")
                    fts_count_after = cursor.fetchone()[0]
                    
                    sync_results['sync_details'][main_table] = {
                        'main_records': main_count,
                        'fts_before': fts_count,
                        'fts_after': fts_count_after,
                        'status': 'success'
                    }
                    
                    sync_results['tables_synced'] += 1
                    self.logger.info(f"Synced {main_table} -> {fts_table}: {main_count} records")
                    
                except sqlite3.Error as e:
                    error_msg = f"Failed to sync {main_table}: {str(e)}"
                    sync_results['errors'].append(error_msg)
                    self.logger.error(error_msg)
            
            conn.commit()
            conn.close()
            
            # Format results
            output = [f"""🔄 **FTS SYNCHRONIZATION COMPLETE**

**Tables Synced:** {sync_results['tables_synced']}/{len(self.content_tables)}
**Errors:** {len(sync_results['errors'])}

"""]
            
            # Sync details
            if sync_results['sync_details']:
                output.append("## 📊 Synchronization Details\n")
                for table, details in sync_results['sync_details'].items():
                    status_icon = "✅" if details['status'] == 'success' else "❌"
                    output.append(f"{status_icon} **{table}**")
                    output.append(f"   - Main records: {details['main_records']}")
                    output.append(f"   - FTS before: {details['fts_before']}")
                    output.append(f"   - FTS after: {details['fts_after']}")
                    output.append("")
            
            # Errors
            if sync_results['errors']:
                output.append("## ❌ Errors\n")
                for error in sync_results['errors']:
                    output.append(f"- {error}")
                output.append("")
            
            if sync_results['tables_synced'] == len(self.content_tables):
                output.append("✅ **All FTS tables successfully synchronized!**")
            else:
                output.append(f"⚠️ **Partial sync completed**: {sync_results['tables_synced']}/{len(self.content_tables)} tables synced")
            
            return "\n".join(output)
            
        except Exception as e:
            self.logger.error(f"FTS sync failed: {e}")
            return f"❌ **SYNC FAILED**\n\nError: {str(e)}"
    
    async def import_markdown_files(self, directory_path: str, file_pattern: str = "*.md", recursive: bool = True) -> str:
        """Import markdown files into the database for full-text search
        
        Args:
            directory_path: Path to directory containing markdown files
            file_pattern: File pattern to match (default: "*.md")
            recursive: Whether to search subdirectories (default: True)
        
        Returns:
            Import status and statistics
        """
        try:
            if not self.context_manager or not self.context_manager.current_db_path:
                return "❌ **IMPORT FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            directory = Path(directory_path)
            if not directory.exists():
                return f"❌ **IMPORT FAILED**\n\nDirectory not found: {directory_path}"
            
            if not directory.is_dir():
                return f"❌ **IMPORT FAILED**\n\nPath is not a directory: {directory_path}"
            
            # Find markdown files
            import_stats = {
                'files_found': 0,
                'files_imported': 0,
                'files_skipped': 0,
                'files_updated': 0,
                'errors': [],
                'total_size': 0
            }
            
            # Collect files
            if recursive:
                files = list(directory.rglob(file_pattern))
            else:
                files = list(directory.glob(file_pattern))
            
            import_stats['files_found'] = len(files)
            
            if not files:
                return f"🔍 **NO FILES FOUND**\n\nNo files matching '{file_pattern}' in {directory_path}"
            
            conn = sqlite3.connect(self.context_manager.current_db_path)
            cursor = conn.cursor()
            
            # Get project UUID
            cursor.execute("SELECT uuid FROM projects LIMIT 1")
            project_result = cursor.fetchone()
            if not project_result:
                conn.close()
                return "❌ **IMPORT FAILED**\n\nNo project found in database"
            
            project_uuid = project_result[0]
            
            for file_path in files:
                try:
                    # Skip if file is too large (>10MB default)
                    file_size = file_path.stat().st_size
                    if file_size > 10 * 1024 * 1024:  # 10MB
                        import_stats['files_skipped'] += 1
                        import_stats['errors'].append(f"File too large (>10MB): {file_path.name}")
                        continue
                    
                    # Read file content
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                    except UnicodeDecodeError:
                        # Try other encodings
                        try:
                            with open(file_path, 'r', encoding='latin-1') as f:
                                content = f.read()
                        except:
                            import_stats['files_skipped'] += 1
                            import_stats['errors'].append(f"Encoding error: {file_path.name}")
                            continue
                    
                    if not content.strip():
                        import_stats['files_skipped'] += 1
                        continue
                    
                    # Generate content signature for duplicate detection
                    content_signature = hashlib.md5(content.encode('utf-8')).hexdigest()
                    
                    # Check if file already exists (by path or signature)
                    cursor.execute("""
                        SELECT uuid, content_signature FROM markdown_files 
                        WHERE file_path = ? OR content_signature = ?
                    """, (str(file_path), content_signature))
                    
                    existing = cursor.fetchone()
                    
                    file_stats = file_path.stat()
                    created_time = datetime.fromtimestamp(file_stats.st_ctime)
                    modified_time = datetime.fromtimestamp(file_stats.st_mtime)
                    
                    if existing:
                        # Update existing record if content changed
                        if existing[1] != content_signature:
                            cursor.execute("""
                                UPDATE markdown_files 
                                SET content = ?, content_signature = ?, file_size = ?, 
                                    updated_at = CURRENT_TIMESTAMP, file_modified = ?
                                WHERE uuid = ?
                            """, (content, content_signature, file_size, modified_time, existing[0]))
                            import_stats['files_updated'] += 1
                        else:
                            import_stats['files_skipped'] += 1
                    else:
                        # Insert new record
                        file_uuid = str(uuid.uuid4())
                        
                        cursor.execute("""
                            INSERT INTO markdown_files 
                            (uuid, project_uuid, filename, file_path, content, file_size, 
                             content_type, file_created, file_modified, content_signature)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            file_uuid, project_uuid, file_path.name, str(file_path),
                            content, file_size, 'markdown', created_time, modified_time,
                            content_signature
                        ))
                        import_stats['files_imported'] += 1
                    
                    import_stats['total_size'] += file_size
                    
                except Exception as e:
                    import_stats['errors'].append(f"Error processing {file_path.name}: {str(e)}")
                    self.logger.error(f"Error importing {file_path}: {e}")
            
            conn.commit()
            conn.close()
            
            # Sync FTS after import
            if import_stats['files_imported'] > 0 or import_stats['files_updated'] > 0:
                await self.sync_fts_tables()
            
            # Format results
            return self._format_import_results(import_stats, directory_path, file_pattern)
            
        except Exception as e:
            self.logger.error(f"Markdown import failed: {e}")
            return f"❌ **IMPORT FAILED**\n\nError: {str(e)}"
    
    def _format_import_results(self, stats: Dict, directory: str, pattern: str) -> str:
        """Format import results with statistics"""
        success_rate = 0
        total_processed = stats['files_found']
        if total_processed > 0:
            success_rate = ((stats['files_imported'] + stats['files_updated']) / total_processed) * 100
        
        size_mb = stats['total_size'] / (1024 * 1024)
        
        output = [f"""📁 **MARKDOWN IMPORT COMPLETE**

**Source:** {directory}
**Pattern:** {pattern}
**Files Found:** {stats['files_found']}
**Success Rate:** {success_rate:.1f}%

## 📊 Import Statistics
- ✅ **Imported:** {stats['files_imported']} new files
- 🔄 **Updated:** {stats['files_updated']} existing files  
- ⏭️ **Skipped:** {stats['files_skipped']} files
- 📦 **Total Size:** {size_mb:.2f} MB

"""]
        
        if stats['errors']:
            output.append(f"## ❌ Errors ({len(stats['errors'])})\n")
            for error in stats['errors'][:10]:  # Limit to first 10 errors
                output.append(f"- {error}")
            if len(stats['errors']) > 10:
                output.append(f"- ... and {len(stats['errors']) - 10} more errors")
            output.append("")
        
        if stats['files_imported'] + stats['files_updated'] > 0:
            output.append("✅ **Import successful!** Files are now searchable via `search_all_content()`.")
        else:
            output.append("ℹ️ **No new content imported.** All files were already up-to-date or skipped.")
        
        return "\n".join(output)
    
    async def discover_and_import_all_markdown(self, directory_path: str, exclude_patterns: str = "", max_file_size_mb: int = 10) -> str:
        """Discover and import all markdown files in a directory with intelligent filtering
        
        Args:
            directory_path: Root directory to search for markdown files
            exclude_patterns: Comma-separated patterns to exclude (e.g., "node_modules,*.log")
            max_file_size_mb: Maximum file size in MB to import (default: 10)
        
        Returns:
            Comprehensive discovery and import report
        """
        try:
            if not self.context_manager or not self.context_manager.current_db_path:
                return "❌ **DISCOVERY FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            directory = Path(directory_path)
            if not directory.exists():
                return f"❌ **DISCOVERY FAILED**\n\nDirectory not found: {directory_path}"
            
            # Parse exclude patterns
            user_excludes = set()
            if exclude_patterns.strip():
                user_excludes = {p.strip() for p in exclude_patterns.split(',') if p.strip()}
            
            # Combine with default exclude patterns
            all_excludes = self.exclude_patterns.union(user_excludes)
            max_size_bytes = max_file_size_mb * 1024 * 1024
            
            discovery_stats = {
                'directories_scanned': 0,
                'files_discovered': 0,
                'files_filtered_out': 0,
                'files_imported': 0,
                'files_updated': 0,
                'files_skipped': 0,
                'total_size': 0,
                'filter_reasons': {},
                'file_types': {},
                'errors': []
            }
            
            # Discover all potential files
            discovered_files = []
            
            for root, dirs, files in os.walk(directory):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not any(exclude in d for exclude in all_excludes)]
                discovery_stats['directories_scanned'] += 1
                
                for file in files:
                    file_path = Path(root) / file
                    
                    # Check file extension
                    if not any(file_path.match(pattern) for pattern in self.markdown_patterns):
                        continue
                    
                    discovery_stats['files_discovered'] += 1
                    
                    # Apply filters
                    filter_reason = self._should_exclude_file(file_path, all_excludes, max_size_bytes)
                    
                    if filter_reason:
                        discovery_stats['files_filtered_out'] += 1
                        if filter_reason not in discovery_stats['filter_reasons']:
                            discovery_stats['filter_reasons'][filter_reason] = 0
                        discovery_stats['filter_reasons'][filter_reason] += 1
                        continue
                    
                    # Track file types
                    suffix = file_path.suffix.lower()
                    if suffix not in discovery_stats['file_types']:
                        discovery_stats['file_types'][suffix] = 0
                    discovery_stats['file_types'][suffix] += 1
                    
                    discovered_files.append(file_path)
            
            if not discovered_files:
                return self._format_discovery_results(discovery_stats, directory_path, exclude_patterns, imported=False)
            
            # Import discovered files
            conn = sqlite3.connect(self.context_manager.current_db_path)
            cursor = conn.cursor()
            
            # Get project UUID
            cursor.execute("SELECT uuid FROM projects LIMIT 1")
            project_result = cursor.fetchone()
            if not project_result:
                conn.close()
                return "❌ **IMPORT FAILED**\n\nNo project found in database"
            
            project_uuid = project_result[0]
            
            for file_path in discovered_files:
                try:
                    # Read and process file
                    import_result = await self._import_single_file(file_path, project_uuid, cursor)
                    
                    if import_result == 'imported':
                        discovery_stats['files_imported'] += 1
                    elif import_result == 'updated':
                        discovery_stats['files_updated'] += 1
                    else:
                        discovery_stats['files_skipped'] += 1
                    
                    discovery_stats['total_size'] += file_path.stat().st_size
                    
                except Exception as e:
                    discovery_stats['errors'].append(f"Error processing {file_path.name}: {str(e)}")
                    self.logger.error(f"Error importing {file_path}: {e}")
            
            conn.commit()
            conn.close()
            
            # Sync FTS if files were imported
            if discovery_stats['files_imported'] > 0 or discovery_stats['files_updated'] > 0:
                await self.sync_fts_tables()
            
            return self._format_discovery_results(discovery_stats, directory_path, exclude_patterns, imported=True)
            
        except Exception as e:
            self.logger.error(f"Bulk discovery failed: {e}")
            return f"❌ **DISCOVERY FAILED**\n\nError: {str(e)}"
    
    def _should_exclude_file(self, file_path: Path, excludes: Set[str], max_size: int) -> Optional[str]:
        """Check if file should be excluded and return reason"""
        try:
            # Check size
            if file_path.stat().st_size > max_size:
                return "too_large"
            
            # Check path components for exclude patterns
            path_parts = file_path.parts
            for part in path_parts:
                if any(exclude in part.lower() for exclude in excludes):
                    return "excluded_pattern"
            
            # Check if file is empty
            if file_path.stat().st_size == 0:
                return "empty_file"
            
            # Check if it's a valid text file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(100)  # Try to read first 100 chars
            except (UnicodeDecodeError, PermissionError):
                return "not_readable"
            
            return None  # File should be included
            
        except (OSError, PermissionError):
            return "permission_error"
    
    async def _import_single_file(self, file_path: Path, project_uuid: str, cursor) -> str:
        """Import a single file and return status"""
        try:
            # Read file content
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            if not content.strip():
                return 'skipped'
            
            # Generate content signature
            content_signature = hashlib.md5(content.encode('utf-8')).hexdigest()
            
            # Check if file already exists
            cursor.execute("""
                SELECT uuid, content_signature FROM markdown_files 
                WHERE file_path = ? OR content_signature = ?
            """, (str(file_path), content_signature))
            
            existing = cursor.fetchone()
            
            file_stats = file_path.stat()
            created_time = datetime.fromtimestamp(file_stats.st_ctime)
            modified_time = datetime.fromtimestamp(file_stats.st_mtime)
            file_size = file_stats.st_size
            
            if existing:
                # Update if content changed
                if existing[1] != content_signature:
                    cursor.execute("""
                        UPDATE markdown_files 
                        SET content = ?, content_signature = ?, file_size = ?, 
                            updated_at = CURRENT_TIMESTAMP, file_modified = ?
                        WHERE uuid = ?
                    """, (content, content_signature, file_size, modified_time, existing[0]))
                    return 'updated'
                else:
                    return 'skipped'
            else:
                # Insert new record
                file_uuid = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO markdown_files 
                    (uuid, project_uuid, filename, file_path, content, file_size, 
                     content_type, file_created, file_modified, content_signature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_uuid, project_uuid, file_path.name, str(file_path),
                    content, file_size, 'markdown', created_time, modified_time,
                    content_signature
                ))
                return 'imported'
                
        except Exception as e:
            self.logger.error(f"Error importing {file_path}: {e}")
            raise
    
    def _format_discovery_results(self, stats: Dict, directory: str, excludes: str, imported: bool) -> str:
        """Format discovery and import results"""
        size_mb = stats['total_size'] / (1024 * 1024) if stats['total_size'] > 0 else 0
        
        output = [f"""🔍 **BULK MARKDOWN DISCOVERY COMPLETE**

**Source Directory:** {directory}
**Exclude Patterns:** {excludes or 'None (using defaults)'}
**Directories Scanned:** {stats['directories_scanned']}

## 📊 Discovery Statistics
- 📁 **Files Discovered:** {stats['files_discovered']}
- 🚫 **Files Filtered:** {stats['files_filtered_out']}
- 📦 **Total Size Processed:** {size_mb:.2f} MB

"""]
        
        if imported:
            success_count = stats['files_imported'] + stats['files_updated']
            total_processed = len([f for f in [stats['files_imported'], stats['files_updated'], stats['files_skipped']] if f])
            success_rate = (success_count / total_processed * 100) if total_processed > 0 else 0
            
            output.append(f"## 📈 Import Results\n")
            output.append(f"- ✅ **Imported:** {stats['files_imported']} new files")
            output.append(f"- 🔄 **Updated:** {stats['files_updated']} existing files")
            output.append(f"- ⏭️ **Skipped:** {stats['files_skipped']} files")
            output.append(f"- 📊 **Success Rate:** {success_rate:.1f}%\n")
        
        # File type breakdown
        if stats['file_types']:
            output.append("## 📋 File Types Discovered\n")
            for ext, count in sorted(stats['file_types'].items()):
                output.append(f"- **{ext}**: {count} files")
            output.append("")
        
        # Filter reasons
        if stats['filter_reasons']:
            output.append("## 🚫 Filter Breakdown\n")
            for reason, count in sorted(stats['filter_reasons'].items()):
                reason_text = {
                    'too_large': 'Files too large',
                    'excluded_pattern': 'Excluded by pattern',
                    'empty_file': 'Empty files',
                    'not_readable': 'Not readable/binary',
                    'permission_error': 'Permission denied'
                }.get(reason, reason)
                output.append(f"- **{reason_text}**: {count} files")
            output.append("")
        
        # Errors
        if stats['errors']:
            output.append(f"## ❌ Errors ({len(stats['errors'])})\n")
            for error in stats['errors'][:5]:  # Show first 5 errors
                output.append(f"- {error}")
            if len(stats['errors']) > 5:
                output.append(f"- ... and {len(stats['errors']) - 5} more errors")
            output.append("")
        
        if imported and (stats['files_imported'] + stats['files_updated']) > 0:
            output.append("✅ **Discovery and import successful!** New files are searchable via `search_all_content()`.")
        elif not imported:
            output.append("ℹ️ **Discovery complete.** Use `import_markdown_files()` to import discovered files.")
        else:
            output.append("ℹ️ **No new content imported.** All files were already up-to-date or filtered out.")
        
        return "\n".join(output)
    
    async def import_project_documentation(self, include_external: bool = True) -> str:
        """Import all documentation files from the current project for comprehensive FTS
        
        Args:
            include_external: Whether to include documentation from external directories (default: True)
        
        Returns:
            Import status and comprehensive statistics
        """
        try:
            if not self.context_manager or not self.context_manager.current_db_path:
                return "❌ **IMPORT FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            if not self.context_manager.current_project_path:
                return "❌ **IMPORT FAILED**\n\nNo project path available"
            
            project_root = Path(self.context_manager.current_project_path)
            if not project_root.exists():
                return f"❌ **IMPORT FAILED**\n\nProject directory not found: {project_root}"
            
            import_stats = {
                'directories_searched': [],
                'total_files_found': 0,
                'files_imported': 0,
                'files_updated': 0,
                'files_skipped': 0,
                'total_size': 0,
                'documentation_types': {},
                'errors': []
            }
            
            # Define documentation search patterns
            doc_patterns = [
                '*.md', '*.markdown', '*.txt', '*.rst', 
                'README*', 'CHANGELOG*', 'LICENSE*', 'INSTALL*',
                'CONTRIBUTING*', 'DOCS*', 'GUIDE*'
            ]
            
            # Search locations
            search_locations = [project_root]
            
            # Add common documentation directories
            doc_dirs = ['docs', 'documentation', 'guides', 'wiki', 'help']
            for doc_dir in doc_dirs:
                doc_path = project_root / doc_dir
                if doc_path.exists() and doc_path.is_dir():
                    search_locations.append(doc_path)
            
            # Find all documentation files
            all_files = []
            for location in search_locations:
                import_stats['directories_searched'].append(str(location))
                
                for pattern in doc_patterns:
                    # Search recursively in this location
                    files = list(location.rglob(pattern))
                    
                    # Filter out excluded directories
                    filtered_files = []
                    for file_path in files:
                        if not any(exclude in str(file_path).lower() for exclude in self.exclude_patterns):
                            filtered_files.append(file_path)
                            
                            # Categorize documentation type
                            doc_type = self._categorize_documentation(file_path)
                            if doc_type not in import_stats['documentation_types']:
                                import_stats['documentation_types'][doc_type] = 0
                            import_stats['documentation_types'][doc_type] += 1
                    
                    all_files.extend(filtered_files)
            
            # Remove duplicates (same file found via different patterns)
            unique_files = list(set(all_files))
            import_stats['total_files_found'] = len(unique_files)
            
            if not unique_files:
                return self._format_project_doc_results(import_stats, project_root)
            
            # Import files
            conn = sqlite3.connect(self.context_manager.current_db_path)
            cursor = conn.cursor()
            
            # Get project UUID
            cursor.execute("SELECT uuid FROM projects LIMIT 1")
            project_result = cursor.fetchone()
            if not project_result:
                conn.close()
                return "❌ **IMPORT FAILED**\n\nNo project found in database"
            
            project_uuid = project_result[0]
            
            for file_path in unique_files:
                try:
                    import_result = await self._import_single_file(file_path, project_uuid, cursor)
                    
                    if import_result == 'imported':
                        import_stats['files_imported'] += 1
                    elif import_result == 'updated':
                        import_stats['files_updated'] += 1
                    else:
                        import_stats['files_skipped'] += 1
                    
                    import_stats['total_size'] += file_path.stat().st_size
                    
                except Exception as e:
                    import_stats['errors'].append(f"Error processing {file_path.name}: {str(e)}")
                    self.logger.error(f"Error importing project doc {file_path}: {e}")
            
            conn.commit()
            conn.close()
            
            # Sync FTS if files were imported
            if import_stats['files_imported'] > 0 or import_stats['files_updated'] > 0:
                await self.sync_fts_tables()
            
            return self._format_project_doc_results(import_stats, project_root)
            
        except Exception as e:
            self.logger.error(f"Project documentation import failed: {e}")
            return f"❌ **IMPORT FAILED**\n\nError: {str(e)}"
    
    def _categorize_documentation(self, file_path: Path) -> str:
        """Categorize documentation file by type"""
        name_lower = file_path.name.lower()
        
        if name_lower.startswith('readme'):
            return 'README'
        elif name_lower.startswith('changelog') or name_lower.startswith('changes'):
            return 'Changelog'
        elif name_lower.startswith('license') or name_lower.startswith('licence'):
            return 'License'
        elif name_lower.startswith('install') or name_lower.startswith('setup'):
            return 'Installation'
        elif name_lower.startswith('contribut'):
            return 'Contributing'
        elif 'api' in name_lower:
            return 'API Documentation'
        elif 'guide' in name_lower or 'tutorial' in name_lower:
            return 'Guide/Tutorial'
        elif 'spec' in name_lower or 'specification' in name_lower:
            return 'Specification'
        elif file_path.parent.name.lower() in ['docs', 'documentation', 'wiki']:
            return 'Documentation'
        else:
            return 'General'
    
    def _format_project_doc_results(self, stats: Dict, project_root: Path) -> str:
        """Format project documentation import results"""
        size_mb = stats['total_size'] / (1024 * 1024) if stats['total_size'] > 0 else 0
        success_count = stats['files_imported'] + stats['files_updated']
        
        output = [f"""📚 **PROJECT DOCUMENTATION IMPORT COMPLETE**

**Project:** {project_root.name}
**Search Locations:** {len(stats['directories_searched'])}
**Files Found:** {stats['total_files_found']}
**Total Size:** {size_mb:.2f} MB

## 📊 Import Results
- ✅ **Imported:** {stats['files_imported']} new files
- 🔄 **Updated:** {stats['files_updated']} existing files
- ⏭️ **Skipped:** {stats['files_skipped']} files

"""]
        
        # Documentation types breakdown
        if stats['documentation_types']:
            output.append("## 📋 Documentation Types\n")
            for doc_type, count in sorted(stats['documentation_types'].items()):
                output.append(f"- **{doc_type}**: {count} files")
            output.append("")
        
        # Search locations
        output.append("## 📁 Searched Locations\n")
        for location in stats['directories_searched']:
            output.append(f"- {location}")
        output.append("")
        
        # Errors
        if stats['errors']:
            output.append(f"## ❌ Errors ({len(stats['errors'])})\n")
            for error in stats['errors'][:5]:
                output.append(f"- {error}")
            if len(stats['errors']) > 5:
                output.append(f"- ... and {len(stats['errors']) - 5} more errors")
            output.append("")
        
        if success_count > 0:
            output.append("✅ **Project documentation import successful!** All documentation is now searchable.")
        else:
            output.append("ℹ️ **No new documentation imported.** All files were already up-to-date.")
        
        return "\n".join(output)
    
    async def generate_markdown_import_report(self) -> str:
        """Generate a comprehensive report of imported markdown files
        
        Returns:
            Detailed report of all markdown files in the database with statistics and metadata
        """
        try:
            if not self.context_manager or not self.context_manager.current_db_path:
                return "❌ **REPORT FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            conn = sqlite3.connect(self.context_manager.current_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get comprehensive markdown file statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_files,
                    SUM(file_size) as total_size,
                    AVG(file_size) as avg_size,
                    MIN(file_created) as oldest_file,
                    MAX(file_modified) as newest_file,
                    COUNT(DISTINCT SUBSTR(file_path, 1, INSTR(file_path || '/', '/') - 1)) as unique_directories
                FROM markdown_files
                WHERE project_uuid = (SELECT uuid FROM projects LIMIT 1)
            """)
            
            stats = cursor.fetchone()
            
            if not stats or stats['total_files'] == 0:
                conn.close()
                return """📄 **MARKDOWN IMPORT REPORT**

❌ **No markdown files found in database.**

Use one of these commands to import files:
- `import_markdown_files(directory_path)` - Import from specific directory
- `discover_and_import_all_markdown(directory_path)` - Bulk discovery and import
- `import_project_documentation()` - Import all project documentation
"""
            
            # Get file breakdown by directory
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN INSTR(file_path, '/') > 0 THEN 
                            SUBSTR(file_path, 1, INSTR(file_path || '/', '/') - 1)
                        ELSE 'Root'
                    END as directory,
                    COUNT(*) as file_count,
                    SUM(file_size) as directory_size,
                    AVG(file_size) as avg_file_size
                FROM markdown_files
                WHERE project_uuid = (SELECT uuid FROM projects LIMIT 1)
                GROUP BY directory
                ORDER BY file_count DESC
                LIMIT 20
            """)
            
            directory_stats = cursor.fetchall()
            
            # Get file type distribution
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN filename LIKE '%.md' THEN '.md'
                        WHEN filename LIKE '%.markdown' THEN '.markdown'
                        WHEN filename LIKE '%.txt' THEN '.txt'
                        WHEN filename LIKE '%.rst' THEN '.rst'
                        ELSE 'other'
                    END as file_extension,
                    COUNT(*) as count
                FROM markdown_files
                WHERE project_uuid = (SELECT uuid FROM projects LIMIT 1)
                GROUP BY file_extension
                ORDER BY count DESC
            """)
            
            extension_stats = cursor.fetchall()
            
            # Get recently imported files
            cursor.execute("""
                SELECT filename, file_path, file_size, updated_at, file_modified
                FROM markdown_files
                WHERE project_uuid = (SELECT uuid FROM projects LIMIT 1)
                ORDER BY updated_at DESC
                LIMIT 10
            """)
            
            recent_files = cursor.fetchall()
            
            # Get largest files
            cursor.execute("""
                SELECT filename, file_path, file_size, file_modified
                FROM markdown_files
                WHERE project_uuid = (SELECT uuid FROM projects LIMIT 1)
                ORDER BY file_size DESC
                LIMIT 10
            """)
            
            largest_files = cursor.fetchall()
            
            # Check FTS synchronization status
            cursor.execute("SELECT COUNT(*) FROM markdown_search")
            fts_count = cursor.fetchone()[0]
            
            conn.close()
            
            # Format the comprehensive report
            return self._format_markdown_report(
                stats, directory_stats, extension_stats, 
                recent_files, largest_files, fts_count
            )
            
        except Exception as e:
            self.logger.error(f"Markdown report generation failed: {e}")
            return f"❌ **REPORT FAILED**\n\nError: {str(e)}"
    
    def _format_markdown_report(self, stats, directory_stats, extension_stats, 
                               recent_files, largest_files, fts_count) -> str:
        """Format comprehensive markdown import report"""
        total_size_mb = stats['total_size'] / (1024 * 1024) if stats['total_size'] else 0
        avg_size_kb = stats['avg_size'] / 1024 if stats['avg_size'] else 0
        
        # FTS sync status
        fts_status = "✅ Synchronized" if fts_count == stats['total_files'] else f"⚠️ Out of sync ({fts_count}/{stats['total_files']})"
        
        output = [f"""📄 **COMPREHENSIVE MARKDOWN IMPORT REPORT**

## 📊 Overview Statistics
- **Total Files:** {stats['total_files']} markdown files
- **Total Size:** {total_size_mb:.2f} MB
- **Average File Size:** {avg_size_kb:.1f} KB
- **Unique Directories:** {stats['unique_directories']}
- **Date Range:** {stats['oldest_file'][:10]} to {stats['newest_file'][:10]}
- **FTS Index Status:** {fts_status}

"""]
        
        # Directory breakdown
        if directory_stats:
            output.append("## 📁 Directory Breakdown\n")
            for dir_stat in directory_stats:
                dir_size_mb = dir_stat['directory_size'] / (1024 * 1024)
                avg_size_kb = dir_stat['avg_file_size'] / 1024
                output.append(f"**{dir_stat['directory']}**")
                output.append(f"   - Files: {dir_stat['file_count']}")
                output.append(f"   - Size: {dir_size_mb:.2f} MB")
                output.append(f"   - Avg: {avg_size_kb:.1f} KB per file")
                output.append("")
        
        # File type distribution
        if extension_stats:
            output.append("## 📋 File Type Distribution\n")
            for ext_stat in extension_stats:
                percentage = (ext_stat['count'] / stats['total_files']) * 100
                output.append(f"- **{ext_stat['file_extension']}**: {ext_stat['count']} files ({percentage:.1f}%)")
            output.append("")
        
        # Recently imported files
        if recent_files:
            output.append("## 🔄 Recently Imported Files\n")
            for file in recent_files:
                size_kb = file['file_size'] / 1024
                output.append(f"**{file['filename']}**")
                output.append(f"   - Path: `{file['file_path']}`")
                output.append(f"   - Size: {size_kb:.1f} KB")
                output.append(f"   - Modified: {file['file_modified'][:16]}")
                output.append(f"   - Imported: {file['updated_at'][:16]}")
                output.append("")
        
        # Largest files
        if largest_files:
            output.append("## 📦 Largest Files\n")
            for file in largest_files:
                size_kb = file['file_size'] / 1024
                output.append(f"**{file['filename']}** ({size_kb:.1f} KB)")
                output.append(f"   - Path: `{file['file_path']}`")
                output.append(f"   - Modified: {file['file_modified'][:16]}")
                output.append("")
        
        # Search and management tips
        output.append("## 🔍 Usage Tips\n")
        output.append("- **Search all content:** `search_all_content(\"your query\")`")
        output.append("- **Search only markdown:** `search_all_content(\"your query\", content_types=\"markdown_files\")`")
        output.append("- **Import more files:** `import_markdown_files(\"/path/to/directory\")`")
        output.append("- **Bulk discovery:** `discover_and_import_all_markdown(\"/path/to/directory\")`")
        output.append("- **Sync search index:** `sync_fts_tables()`")
        output.append("- **Extract full content:** `extract_large_document(\"filename\")`")
        
        if fts_count != stats['total_files']:
            output.append(f"\n⚠️ **Notice**: FTS index is out of sync. Run `sync_fts_tables()` to update search indexes.")
        
        output.append(f"\n✅ **Report generated successfully!** {stats['total_files']} files analyzed.")
        
        return "\n".join(output)
