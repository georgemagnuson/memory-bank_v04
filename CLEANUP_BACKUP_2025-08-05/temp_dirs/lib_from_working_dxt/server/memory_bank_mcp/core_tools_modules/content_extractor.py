#!/usr/bin/env python3
"""
core_tools_modules/content_extractor.py
Generated: 2025-07-30.1439
Purpose: Content extraction tools for v2.0 documents table architecture

Key v2.0 Changes:
- Uses documents table instead of unified_documents
- Uses uuid field instead of original_uuid
- Supports project_uuid for cross-project extraction
- Updated FTS table references (documents_fts)
- Enhanced metadata in extracted files
"""

import logging
import tempfile
import sqlite3
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class ContentExtractor:
    """Content extraction tools for v2.0 documents table architecture"""
    
    def __init__(self, context_manager):
        """Initialize content extractor
        
        Args:
            context_manager: Active ContextManager instance with database connection
        """
        self.context_manager = context_manager
        self.logger = logger
    
    async def extract_content_to_temp(self, search_query, output_dir="/tmp", project_uuid=None):
        """Extract content from v2.0 documents table to temporary files
        
        Args:
            search_query: Search query to find content (title, UUID, or FTS query)
            output_dir: Directory to write extracted files (default: /tmp)
            project_uuid: Optional project UUID for cross-project extraction
            
        Returns:
            Dict with extraction results and file paths
        """
        try:
            if not self.context_manager or not self.context_manager.database_path:
                return {
                    'success': False,
                    'error': 'No active database connection'
                }
            
            # Use current project UUID if not specified
            target_project_uuid = project_uuid or getattr(self.context_manager, 'project_uuid', None)
            if not target_project_uuid:
                return {
                    'success': False,
                    'error': 'No project UUID available'
                }
            
            # Create timestamped output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            extract_dir = Path(output_dir) / f"memory_bank_v2_extract_{timestamp}"
            extract_dir.mkdir(exist_ok=True)
            
            conn = sqlite3.connect(self.context_manager.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Search for matching content
            results = await self._find_content_for_extraction(cursor, search_query, target_project_uuid)
            
            if not results:
                conn.close()
                return {
                    'success': False,
                    'error': f'No content found for query: {search_query}'
                }
            
            # Extract each result to a separate file
            extracted_files = []
            for i, result in enumerate(results, 1):
                filename = self._generate_safe_filename(result, i)
                file_path = extract_dir / filename
                
                # Create file content with v2.0 metadata header
                file_content = self._format_extracted_content(result, search_query)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)
                
                extracted_files.append({
                    'filename': filename,
                    'path': str(file_path),
                    'title': result['title'],
                    'document_type': result['document_type'],
                    'content_length': len(result['content']),
                    'uuid': result['uuid'],
                    'project_uuid': result['project_uuid']
                })
            
            # Create v2.0 summary file
            summary_content = self._create_extraction_summary(search_query, extracted_files, timestamp, target_project_uuid)
            summary_path = extract_dir / "extraction_summary_v2.md"
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            
            conn.close()
            
            return {
                'success': True,
                'extract_dir': str(extract_dir),
                'summary_file': str(summary_path),
                'extracted_files': extracted_files,
                'total_files': len(extracted_files),
                'search_query': search_query,
                'project_uuid': target_project_uuid
            }
            
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _find_content_for_extraction(self, cursor, search_query, project_uuid):
        """Find content matching the search query for extraction from v2.0 documents table"""
        results = []
        
        # Try different search strategies
        
        # 1. UUID search
        try:
            cursor.execute("""
                SELECT id, uuid, project_uuid, source_table, document_type, title, content, 
                       summary, tags, metadata, created_at, updated_at, status
                FROM documents 
                WHERE uuid = ? AND project_uuid = ? AND status = 'active'
                LIMIT 10
            """, (search_query, project_uuid))
            
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    result = self._format_extraction_result(row, 'uuid_extraction')
                    if result:
                        results.append(result)
                return results
                
        except Exception as e:
            logger.warning(f"UUID extraction search failed: {e}")
        
        # 2. Title search
        try:
            cursor.execute("""
                SELECT id, uuid, project_uuid, source_table, document_type, title, content, 
                       summary, tags, metadata, created_at, updated_at, status
                FROM documents 
                WHERE title LIKE ? AND project_uuid = ? AND status = 'active'
                ORDER BY CASE document_type 
                    WHEN 'document' THEN 1 
                    WHEN 'discussion' THEN 2 
                    WHEN 'plan' THEN 3 
                    WHEN 'artifact' THEN 4 
                    ELSE 5 
                END
                LIMIT 10
            """, (f'%{search_query}%', project_uuid))
            
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    result = self._format_extraction_result(row, 'title_extraction')
                    if result:
                        results.append(result)
                return results
                
        except Exception as e:
            logger.warning(f"Title extraction search failed: {e}")
        
        # 3. FTS search using v2.0 documents_fts
        try:
            cursor.execute("""
                SELECT d.id, d.uuid, d.project_uuid, d.source_table, d.document_type, d.title, d.content, 
                       d.summary, d.tags, d.metadata, d.created_at, d.updated_at, d.status
                FROM documents_fts fts
                JOIN documents d ON fts.rowid = d.id
                WHERE documents_fts MATCH ? AND d.project_uuid = ? AND d.status = 'active'
                ORDER BY CASE d.document_type 
                    WHEN 'document' THEN 1 
                    WHEN 'discussion' THEN 2 
                    WHEN 'plan' THEN 3 
                    WHEN 'artifact' THEN 4 
                    ELSE 5 
                END, rank
                LIMIT 10
            """, (search_query, project_uuid))
            
            rows = cursor.fetchall()
            for row in rows:
                result = self._format_extraction_result(row, 'fts_extraction')
                if result:
                    results.append(result)
                    
        except Exception as e:
            logger.warning(f"FTS extraction search failed: {e}")
        
        return results
    
    def _format_extraction_result(self, row, match_type):
        """Format database row for extraction with v2.0 structure"""
        try:
            # Parse JSON fields safely
            try:
                tags = json.loads(row['tags']) if row['tags'] else []
            except (json.JSONDecodeError, TypeError):
                tags = []
            
            try:
                metadata = json.loads(row['metadata']) if row['metadata'] else {}
            except (json.JSONDecodeError, TypeError):
                metadata = {}
            
            return {
                'id': row['id'],
                'title': row['title'] or 'Untitled',
                'content': row['content'] or '',
                'uuid': row['uuid'],  # v2.0: uses uuid field
                'project_uuid': row['project_uuid'],  # v2.0: project UUID
                'source_table': row['source_table'],
                'document_type': row['document_type'],
                'summary': row['summary'],
                'tags': tags,
                'metadata': metadata,
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'status': row['status'],  # v2.0: status field
                'match_type': match_type,
                'content_length': len(row['content']) if row['content'] else 0
            }
            
        except Exception as e:
            logger.error(f"Error formatting extraction result: {e}")
            return None
    
    def _generate_safe_filename(self, result, index):
        """Generate a safe filename for extracted content"""
        # Use title as base, clean for filesystem
        title = result['title'] or 'untitled'
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '_', safe_title)
        safe_title = safe_title[:50]  # Limit length
        
        doc_type = result['document_type']
        extension = 'md' if doc_type in ['markdown', 'document'] else 'txt'
        
        return f"{index:03d}_{safe_title}_{doc_type}_v2.{extension}"
    
    def _format_extracted_content(self, result, search_query):
        """Format content for extraction file with v2.0 metadata header"""
        metadata_lines = [
            f"# Extracted Content (v2.0): {result['title']}",
            f"",
            f"**Extraction Details:**",
            f"- Search Query: `{search_query}`",
            f"- Document Type: {result['document_type']}",
            f"- Source Table: {result['source_table']}",
            f"- UUID: {result['uuid']}",
            f"- Project UUID: {result['project_uuid']}",
            f"- Status: {result['status']}",
            f"- Match Type: {result['match_type']}",
            f"- Created: {result['created_at']}",
            f"- Updated: {result['updated_at']}",
            f"- Content Length: {result['content_length']:,} characters",
            f"",
            f"**Tags:** {', '.join(result['tags']) if result['tags'] else 'None'}",
            f"",
            f"**v2.0 Metadata:**",
            f"```json",
            json.dumps(result['metadata'], indent=2),
            f"```",
            f"",
            f"---",
            f"",
            f"## Content",
            f"",
            result['content']
        ]
        
        return '\n'.join(metadata_lines)
    
    def _create_extraction_summary(self, search_query, extracted_files, timestamp, project_uuid):
        """Create a v2.0 summary file for the extraction"""
        summary_lines = [
            f"# Memory Bank v2.0 Content Extraction Summary",
            f"",
            f"**Extraction Details:**",
            f"- Search Query: `{search_query}`",
            f"- Project UUID: {project_uuid}",
            f"- Timestamp: {timestamp}",
            f"- Total Files: {len(extracted_files)}",
            f"- Architecture: v2.0 (documents table)",
            f"",
            f"## Extracted Files",
            f""
        ]
        
        for i, file_info in enumerate(extracted_files, 1):
            summary_lines.extend([
                f"### {i}. {file_info['title']}",
                f"- **File:** `{file_info['filename']}`",
                f"- **Type:** {file_info['document_type']}",
                f"- **Size:** {file_info['content_length']:,} characters",
                f"- **UUID:** `{file_info['uuid']}`",
                f"- **Project:** `{file_info['project_uuid'][:8]}...`",
                f"- **Path:** `{file_info['path']}`",
                f""
            ])
        
        summary_lines.extend([
            f"## v2.0 Features",
            f"",
            f"- **Cross-project support:** Each file includes project UUID",
            f"- **Enhanced metadata:** Improved structure with status tracking",
            f"- **UUID-based references:** Stable document identification",
            f"- **Search improvements:** FTS5 with documents_fts table",
            f"",
            f"## Usage Tips",
            f"",
            f"- Use `grep -r \"search_term\" .` to search across all files",
            f"- Use `wc -l *.txt *.md` to see line counts",
            f"- Each file includes v2.0 metadata header with extraction details",
            f"- Files are named with index, title, document type, and v2 indicator",
            f"- UUIDs in metadata can be used for precise document lookup",
            f""
        ])
        
        return '\n'.join(summary_lines)
