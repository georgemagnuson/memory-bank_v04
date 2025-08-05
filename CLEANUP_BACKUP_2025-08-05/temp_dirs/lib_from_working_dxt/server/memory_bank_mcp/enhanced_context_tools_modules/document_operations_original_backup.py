#!/usr/bin/env python3
"""
Filename: enhanced_context_tools_modules/document_operations.py
Generated: 2025-08-03.1749
Purpose: Enhanced document operations for document storage and search

This module provides document management capabilities using the centralized 
context registry system for Memory Bank v2.0 Enhanced.
"""

from typing import Dict, Any


class EnhancedDocumentTools:
    """
    Enhanced document tools that use the centralized context registry
    Provides registry-aware implementations of save_document, search_documents, etc.
    """
    
    def __init__(self):
        # Import registry and context tools with fallback pattern
        try:
            from memory_bank_mcp.context_registry import get_global_registry
            from memory_bank_mcp.enhanced_context_tools_modules.context_manager import EnhancedContextTools
        except ImportError:
            try:
                from ..context_registry import get_global_registry
                from .context_manager import EnhancedContextTools
            except ImportError:
                from context_registry import get_global_registry
                from context_manager import EnhancedContextTools
        
        self.registry = get_global_registry()
        self.context_tools = EnhancedContextTools()
    
    def save_document(self, title: str, content: str, doc_type: str = "general", 
                     tags: str = "") -> Dict[str, Any]:
        """
        Save document using active context from registry - ACTUAL DATABASE IMPLEMENTATION
        
        Args:
            title: Document title
            content: Document content
            doc_type: Document type
            tags: Optional tags
            
        Returns:
            Dict with save operation results
        """
        # Validate context first
        is_valid, message = self.context_tools.validate_context()
        if not is_valid:
            return {
                "success": False,
                "message": f"❌ Context Error: {message}",
                "document_saved": False
            }
        
        database_path = self.context_tools.get_database_path()
        project_name = self.context_tools.get_project_name()
        
        try:
            # Get project UUID from database
            import sqlite3
            import uuid
            from datetime import datetime
            
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            # Get project UUID
            cursor.execute("SELECT uuid FROM projects WHERE name = ?", (project_name,))
            project_result = cursor.fetchone()
            
            if not project_result:
                conn.close()
                return {
                    "success": False,
                    "message": f"❌ Project '{project_name}' not found in database",
                    "document_saved": False
                }
            
            project_uuid = project_result[0]
            
            # Generate document UUID and prepare data
            doc_uuid = str(uuid.uuid4())
            doc_version = 1
            timestamp = datetime.now().isoformat()
            
            # Prepare tags as JSON
            if isinstance(tags, str):
                if tags:
                    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                else:
                    tag_list = []
            else:
                tag_list = tags if isinstance(tags, list) else []
            
            import json
            tags_json = json.dumps(tag_list)
            
            # Create summary from content
            summary = content[:300] + "..." if len(content) > 300 else content
            
            # Insert into v2.0 documents table
            cursor.execute("""
                INSERT INTO documents (
                    project_uuid, uuid, version, document_type, title, content,
                    summary, tags, metadata, created_at, updated_at, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_uuid,
                doc_uuid,
                doc_version,
                doc_type,
                title,
                content,
                summary,
                tags_json,
                '{"source": "enhanced_save_document"}',  # Metadata
                timestamp,
                timestamp,
                'active'
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"✅ Document '{title}' saved to {project_name}",
                "database_path": database_path,
                "title": title,
                "doc_type": doc_type,
                "content_length": len(content),
                "document_uuid": doc_uuid,
                "project_uuid": project_uuid
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error saving document: {str(e)}",
                "error": str(e)
            }
    
    def search_documents(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search documents using active context from registry - ACTUAL DATABASE IMPLEMENTATION
        
        Args:
            query: Search query
            limit: Maximum results to return
            
        Returns:
            Dict with search results
        """
        # Validate context first
        is_valid, message = self.context_tools.validate_context()
        if not is_valid:
            return {
                "success": False,
                "message": f"❌ Context Error: {message}",
                "results": []
            }
        
        database_path = self.context_tools.get_database_path()
        project_name = self.context_tools.get_project_name()
        
        try:
            import sqlite3
            
            conn = sqlite3.connect(database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get project UUID
            cursor.execute("SELECT uuid FROM projects WHERE name = ?", (project_name,))
            project_result = cursor.fetchone()
            
            if not project_result:
                conn.close()
                return {
                    "success": False,
                    "message": f"❌ Project '{project_name}' not found in database",
                    "results": []
                }
            
            project_uuid = project_result[0]
            
            # Search documents with more detailed results
            search_query = f"%{query}%"
            cursor.execute("""
                SELECT uuid, version, document_type, title, content,
                       summary, tags, created_at, updated_at, status
                FROM documents 
                WHERE project_uuid = ? 
                AND (
                    content LIKE ? OR 
                    title LIKE ? OR 
                    summary LIKE ? OR
                    tags LIKE ?
                ) 
                AND status = 'active'
                ORDER BY updated_at DESC 
                LIMIT ?
            """, (project_uuid, search_query, search_query, search_query, search_query, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            # Format results with full document info
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "uuid": row["uuid"],
                    "version": row["version"],
                    "document_type": row["document_type"],
                    "title": row["title"],
                    "content": row["content"],
                    "summary": row["summary"],
                    "tags": row["tags"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "status": row["status"]
                })
            
            return {
                "success": True,
                "message": f"✅ Found {len(formatted_results)} documents in {project_name}",
                "database_path": database_path,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error searching documents: {str(e)}",
                "error": str(e),
                "results": []
            }
