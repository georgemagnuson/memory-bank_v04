#!/usr/bin/env python3
"""
Query Builder Module
====================

Builds SQL migration queries based on table structures.
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

class QueryBuilder:
    """Builds migration queries for different table types"""
    
    def build_migration_query(self, table_name: str, document_type: str, 
                             structure: Dict[str, Any], project_uuid: str) -> str:
        """
        Build migration query based on table structure
        
        Args:
            table_name: Source table name
            document_type: Target document_type
            structure: Table structure info from TableAnalyzer
            project_uuid: Project UUID to use
            
        Returns:
            SQL query string for migration
        """
        columns = structure['columns']
        
        # Handle unified_documents specially (might have existing document_type)
        if table_name == 'unified_documents':
            return self._build_unified_documents_query(table_name, document_type, columns, project_uuid)
        
        # Handle tables with proper UUID structure
        elif all(col in columns for col in ['uuid', 'project_uuid']):
            return self._build_modern_table_query(table_name, document_type, columns)
        
        # Handle legacy tables without UUIDs
        else:
            return self._build_legacy_table_query(table_name, document_type, columns, project_uuid)
    
    def _build_unified_documents_query(self, table_name: str, document_type: str, 
                                     columns: List[str], project_uuid: str) -> str:
        """Build query for unified_documents table"""
        if 'document_type' in columns:
            # Use existing document_type if available
            return f"""
            INSERT INTO documents (
                project_uuid, uuid, version, document_type, title, content, 
                summary, tags, metadata, created_at, updated_at, status, importance
            )
            SELECT 
                COALESCE(project_uuid, '{project_uuid}') as project_uuid,
                COALESCE(uuid, '{table_name}-' || rowid) as uuid,
                COALESCE(version, 1) as version,
                COALESCE(document_type, '{document_type}') as document_type,
                COALESCE(title, 'Migrated from {table_name}') as title,
                content,
                COALESCE(summary, '') as summary,
                COALESCE(tags, '[]') as tags,
                COALESCE(metadata, '{{}}') as metadata,
                COALESCE(created_at, datetime('now')) as created_at,
                COALESCE(updated_at, datetime('now')) as updated_at,
                COALESCE(status, 'active') as status,
                COALESCE(importance, 5) as importance
            FROM {table_name}
            WHERE NOT EXISTS (
                SELECT 1 FROM documents d 
                WHERE d.uuid = COALESCE({table_name}.uuid, '{table_name}-' || {table_name}.rowid)
                AND d.project_uuid = COALESCE({table_name}.project_uuid, '{project_uuid}')
            )
            """
        else:
            # No document_type column - use default
            return f"""
            INSERT INTO documents (
                project_uuid, uuid, version, document_type, title, content, 
                summary, tags, metadata, created_at, updated_at, status, importance
            )
            SELECT 
                '{project_uuid}' as project_uuid,
                COALESCE(uuid, '{table_name}-' || rowid) as uuid,
                COALESCE(version, 1) as version,
                '{document_type}' as document_type,
                COALESCE(title, 'Migrated from {table_name}') as title,
                content,
                COALESCE(summary, '') as summary,
                COALESCE(tags, '[]') as tags,
                COALESCE(metadata, '{{}}') as metadata,
                COALESCE(created_at, datetime('now')) as created_at,
                COALESCE(updated_at, datetime('now')) as updated_at,
                COALESCE(status, 'active') as status,
                COALESCE(importance, 5) as importance
            FROM {table_name}
            """
    
    def _build_modern_table_query(self, table_name: str, document_type: str, columns: List[str]) -> str:
        """Build query for modern tables with UUID structure"""
        return f"""
        INSERT INTO documents (
            project_uuid, uuid, version, document_type, title, content, 
            summary, tags, metadata, created_at, updated_at, status, importance
        )
        SELECT 
            project_uuid,
            uuid,
            COALESCE(version, 1) as version,
            '{document_type}' as document_type,
            COALESCE(title, 'Migrated from {table_name}') as title,
            content,
            COALESCE(summary, '') as summary,
            COALESCE(tags, '[]') as tags,
            COALESCE(metadata, '{{}}') as metadata,
            COALESCE(created_at, datetime('now')) as created_at,
            COALESCE(updated_at, datetime('now')) as updated_at,
            COALESCE(status, 'active') as status,
            COALESCE(importance, 5) as importance
        FROM {table_name}
        WHERE NOT EXISTS (
            SELECT 1 FROM documents d 
            WHERE d.project_uuid = {table_name}.project_uuid 
            AND d.uuid = {table_name}.uuid
        )
        """
    
    def _build_legacy_table_query(self, table_name: str, document_type: str, 
                                 columns: List[str], project_uuid: str) -> str:
        """Build query for legacy tables without proper UUID structure"""
        # Determine best columns to use
        title_column = 'title' if 'title' in columns else f"'Migrated from {table_name}'"
        content_column = 'content' if 'content' in columns else f"'Legacy content from {table_name}'"
        
        # Handle tables that might not have content column
        if 'content' not in columns:
            # Try to find text-like columns
            text_columns = [col for col in columns if any(keyword in col.lower() 
                           for keyword in ['text', 'description', 'body', 'message', 'note'])]
            if text_columns:
                content_column = text_columns[0]
        
        return f"""
        INSERT INTO documents (
            project_uuid, uuid, version, document_type, title, content, 
            summary, tags, metadata, created_at, updated_at, status, importance
        )
        SELECT 
            '{project_uuid}' as project_uuid,
            '{table_name}-' || rowid as uuid,
            1 as version,
            '{document_type}' as document_type,
            COALESCE({title_column}, 'Migrated from {table_name}') as title,
            COALESCE({content_column}, 'Legacy content') as content,
            COALESCE(summary, '') as summary,
            COALESCE(tags, '[]') as tags,
            COALESCE(metadata, '{{}}') as metadata,
            COALESCE(created_at, datetime('now')) as created_at,
            COALESCE(updated_at, datetime('now')) as updated_at,
            'active' as status,
            5 as importance
        FROM {table_name}
        """
