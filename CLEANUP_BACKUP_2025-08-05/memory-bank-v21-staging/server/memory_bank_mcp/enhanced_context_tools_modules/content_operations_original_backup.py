#!/usr/bin/env python3
"""
Filename: enhanced_context_tools_modules/content_operations.py
Generated: 2025-08-03.1749
Purpose: Enhanced content operations for information storage and search

This module provides information management capabilities using the centralized 
context registry system for Memory Bank v2.0 Enhanced.
"""

from typing import Dict, Any


class EnhancedContentTools:
    """
    Enhanced content tools that use the centralized context registry
    Provides registry-aware implementations of save_info, search_info, etc.
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
    
    def save_info(self, content: str, category: str = "general", tags: str = "") -> Dict[str, Any]:
        """
        Save information using active context from registry - ACTUAL DATABASE IMPLEMENTATION
        
        Args:
            content: Information to save
            category: Category for organization
            tags: Optional tags for searching
            
        Returns:
            Dict with save operation results
        """
        # Validate context first
        is_valid, message = self.context_tools.validate_context()
        if not is_valid:
            return {
                "success": False,
                "message": f"❌ Context Error: {message}",
                "content_saved": False
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
                    "content_saved": False
                }
            
            project_uuid = project_result[0]
            
            # Generate document UUID and prepare data
            doc_uuid = str(uuid.uuid4())
            doc_version = 1
            doc_type = category if category else "note"
            title = f"{category.title()} Info - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
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
                content[:200] + "..." if len(content) > 200 else content,  # Summary
                tags_json,
                '{"source": "enhanced_save_info", "category": "' + category + '"}',  # Metadata
                timestamp,
                timestamp,
                'active'
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"✅ Information saved to {project_name}",
                "database_path": database_path,
                "category": category,
                "content_length": len(content),
                "document_uuid": doc_uuid,
                "project_uuid": project_uuid
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error saving information: {str(e)}",
                "error": str(e)
            }
    
    def search_info(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search information using active context from registry - ACTUAL DATABASE IMPLEMENTATION
        
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
            conn.row_factory = sqlite3.Row  # Enable column access by name
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
            
            # Search in documents table using LIKE for content, title, and tags
            search_query = f"%{query}%"
            cursor.execute("""
                SELECT uuid, version, document_type, title, 
                       substr(content, 1, 200) as content_preview,
                       tags, created_at, updated_at
                FROM documents 
                WHERE project_uuid = ? 
                AND (
                    content LIKE ? OR 
                    title LIKE ? OR 
                    tags LIKE ?
                ) 
                AND status = 'active'
                ORDER BY updated_at DESC 
                LIMIT ?
            """, (project_uuid, search_query, search_query, search_query, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            # Format results
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "uuid": row["uuid"],
                    "version": row["version"],
                    "document_type": row["document_type"],
                    "title": row["title"],
                    "content_preview": row["content_preview"],
                    "tags": row["tags"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"]
                })
            
            return {
                "success": True,
                "message": f"✅ Found {len(formatted_results)} results in {project_name}",
                "database_path": database_path,
                "query": query,
                "results": formatted_results,
                "count": len(formatted_results)
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error searching information: {str(e)}",
                "error": str(e),
                "results": []
            }
