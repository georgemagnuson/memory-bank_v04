#!/usr/bin/env python3
"""
core_tools_modules/content_search_engine.py
Generated: 2025-07-30.1439
Purpose: Enhanced content search for v2.0 documents table architecture

Key v2.0 Changes:
- Uses documents table instead of unified_documents
- Uses uuid field instead of original_uuid  
- Supports project_uuid for cross-project searches
- Updated FTS table references (documents_fts)
- Enhanced search result formatting
"""

import logging
import sqlite3
import json
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class ContentSearchEngine:
    """Enhanced search engine for v2.0 documents table architecture"""
    
    def __init__(self, context_manager):
        """Initialize content search engine
        
        Args:
            context_manager: Active ContextManager instance with database connection
        """
        self.context_manager = context_manager
        self.logger = logger
        
        # Document type priority order (higher priority first)
        self.PRIORITY_ORDER = [
            {'type': 'document', 'icon': '📄', 'priority': 1},
            {'type': 'discussion', 'icon': '💭', 'priority': 2},
            {'type': 'plan', 'icon': '📋', 'priority': 3},
            {'type': 'code', 'icon': '💻', 'priority': 4},
            {'type': 'artifact', 'icon': '🎯', 'priority': 5},
            {'type': 'note', 'icon': '📝', 'priority': 6},
            {'type': 'markdown', 'icon': '📄', 'priority': 7},
            {'type': 'chat_session', 'icon': '💬', 'priority': 8}
        ]
    
    async def search_content(self, title_search=None, uuid_search=None, document_type="auto", 
                           project_uuid=None):
        """Search for content in v2.0 documents table with priority ordering
        
        Args:
            title_search: Title/summary to search for (fuzzy matching)
            uuid_search: Specific UUID to find (exact match)
            document_type: Specific document type to search, or "auto" for all types
            project_uuid: Optional project UUID for cross-project search
            
        Returns:
            Dict with content data or None if not found
        """
        try:
            if not self.context_manager or not self.context_manager.database_path:
                logger.error("No active database connection")
                return None
            
            # Use current project UUID if not specified
            target_project_uuid = project_uuid or getattr(self.context_manager, 'project_uuid', None)
            if not target_project_uuid:
                logger.error("No project UUID available")
                return None
            
            conn = sqlite3.connect(self.context_manager.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Search by UUID first (most specific)
            if uuid_search:
                result = await self._search_by_uuid(cursor, uuid_search, document_type, target_project_uuid)
                if result:
                    conn.close()
                    return result
            
            # Search by title with fuzzy matching
            if title_search:
                result = await self._search_by_title(cursor, title_search, document_type, target_project_uuid)
                if result:
                    conn.close()
                    return result
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Content search failed: {e}")
            return None
    
    async def _search_by_uuid(self, cursor, uuid_search, document_type="auto", project_uuid=None):
        """Search by UUID in v2.0 documents table"""
        try:
            # Build query with optional document type filter and project UUID
            type_filter = "" if document_type == "auto" else "AND document_type = ?"
            query = f"""
            SELECT id, uuid, project_uuid, source_table, document_type, title, content, 
                   summary, tags, metadata, created_at, updated_at, status
            FROM documents 
            WHERE uuid = ? AND project_uuid = ? AND status = 'active' {type_filter}
            ORDER BY CASE document_type 
                WHEN 'document' THEN 1 
                WHEN 'discussion' THEN 2 
                WHEN 'plan' THEN 3 
                WHEN 'artifact' THEN 4
                ELSE 5 
            END
            LIMIT 1
            """
            
            params = [uuid_search, project_uuid] + ([document_type] if document_type != "auto" else [])
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                return self._format_search_result(row, 'exact_uuid')
            
        except Exception as e:
            logger.warning(f"UUID search failed: {e}")
        
        return None
    
    async def _search_by_title(self, cursor, title_search, document_type="auto", project_uuid=None):
        """Search by title with fuzzy matching in v2.0 documents table"""
        # Try exact title match first
        try:
            type_filter = "" if document_type == "auto" else "AND document_type = ?"
            query = f"""
            SELECT id, uuid, project_uuid, source_table, document_type, title, content, 
                   summary, tags, metadata, created_at, updated_at, status
            FROM documents 
            WHERE title = ? AND project_uuid = ? AND status = 'active' {type_filter}
            ORDER BY CASE document_type 
                WHEN 'document' THEN 1 
                WHEN 'discussion' THEN 2 
                WHEN 'plan' THEN 3 
                WHEN 'artifact' THEN 4
                ELSE 5 
            END
            LIMIT 1
            """
            
            params = [title_search, project_uuid] + ([document_type] if document_type != "auto" else [])
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                return self._format_search_result(row, 'exact_title')
                
        except Exception as e:
            logger.warning(f"Exact title search failed: {e}")
        
        # Try fuzzy title match
        try:
            type_filter = "" if document_type == "auto" else "AND document_type = ?"
            query = f"""
            SELECT id, uuid, project_uuid, source_table, document_type, title, content, 
                   summary, tags, metadata, created_at, updated_at, status
            FROM documents 
            WHERE title LIKE ? AND project_uuid = ? AND status = 'active' {type_filter}
            ORDER BY CASE document_type 
                WHEN 'document' THEN 1 
                WHEN 'discussion' THEN 2 
                WHEN 'plan' THEN 3 
                WHEN 'artifact' THEN 4
                ELSE 5 
            END
            LIMIT 1
            """
            
            params = [f'%{title_search}%', project_uuid] + ([document_type] if document_type != "auto" else [])
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                return self._format_search_result(row, 'fuzzy_title')
                
        except Exception as e:
            logger.warning(f"Fuzzy title search failed: {e}")
        
        # Try FTS search as last resort
        try:
            type_filter = "" if document_type == "auto" else "AND d.document_type = ?"
            query = f"""
            SELECT d.id, d.uuid, d.project_uuid, d.source_table, d.document_type, d.title, d.content, 
                   d.summary, d.tags, d.metadata, d.created_at, d.updated_at, d.status
            FROM documents_fts fts
            JOIN documents d ON fts.rowid = d.id
            WHERE documents_fts MATCH ? AND d.project_uuid = ? AND d.status = 'active' {type_filter}
            ORDER BY CASE d.document_type 
                WHEN 'document' THEN 1 
                WHEN 'discussion' THEN 2 
                WHEN 'plan' THEN 3 
                WHEN 'artifact' THEN 4
                ELSE 5 
            END, rank
            LIMIT 1
            """
            
            params = [title_search, project_uuid] + ([document_type] if document_type != "auto" else [])
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                return self._format_search_result(row, 'fts_search')
                
        except Exception as e:
            logger.warning(f"FTS search failed: {e}")
        
        return None
    
    def _format_search_result(self, row, match_type):
        """Format database row into standardized result structure for v2.0"""
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
            
            # Get icon for document type
            type_info = next((t for t in self.PRIORITY_ORDER if t['type'] == row['document_type']), {'icon': '📄'})
            
            return {
                'id': row['id'],
                'title': row['title'] or 'Untitled',
                'content': row['content'] or '',
                'uuid': row['uuid'],  # v2.0: uses uuid instead of original_uuid
                'project_uuid': row['project_uuid'],  # v2.0: project UUID support
                'source_table': row['source_table'],
                'document_type': row['document_type'],
                'summary': row['summary'],
                'tags': tags,
                'metadata': metadata,
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'status': row['status'],  # v2.0: status field
                'icon': type_info['icon'],
                'match_type': match_type,
                'content_length': len(row['content']) if row['content'] else 0
            }
            
        except Exception as e:
            logger.error(f"Error formatting search result: {e}")
            return None
    
    def get_priority_order(self):
        """Get document type priority order"""
        return self.PRIORITY_ORDER.copy()
    
    def get_supported_document_types(self):
        """Get list of supported document types"""
        return [item['type'] for item in self.PRIORITY_ORDER]
