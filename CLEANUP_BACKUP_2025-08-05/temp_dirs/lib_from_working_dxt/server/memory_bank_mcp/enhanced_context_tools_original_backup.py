"""
Filename: enhanced_context_tools.py
Generated: 2025-08-02.1721 (Updated: 2025-08-03.0040 - Complete Database Implementation)
Purpose: Enhanced context management tools that use centralized context registry
        Replaces legacy context tools with registry-aware versions
        
COMPLETE DATABASE IMPLEMENTATION: Fixed ALL database functions to actually perform SQL operations:
        - save_info(): Real INSERT into v2.0 documents table
        - save_document(): Real INSERT with proper v2.0 schema  
        - search_info(): Real SELECT with LIKE queries across content/title/tags
        - search_documents(): Real SELECT with comprehensive document search
        All functions use proper composite primary keys (project_uuid, uuid, version)
"""

from typing import Optional, Dict, Any
from context_registry import (
    get_global_registry, 
    has_active_context,
    get_active_project_name,
    get_active_database_path
)


class EnhancedContextTools:
    """
    Enhanced context tools that use the centralized context registry
    Provides registry-aware implementations of core context operations
    """
    
    def __init__(self):
        self.registry = get_global_registry()
    
    def get_current_context(self) -> Dict[str, Any]:
        """
        Get current project context information from registry
        
        Returns:
            Dict with context information or error message
        """
        if not has_active_context():
            return {
                "success": False,
                "message": "❌ No active project. Use work_on_project() to start working.",
                "context": None
            }
        
        context_info = self.registry.get_context_info()
        
        return {
            "success": True,
            "message": f"✅ Active project: {context_info['project_name']}",
            "context": context_info
        }
    
    def validate_context(self) -> tuple[bool, str]:
        """
        Validate that we have a working context
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not has_active_context():
            return False, "No active project context. Use work_on_project() first."
        
        context = self.registry.get_active_context()
        if not context.is_valid():
            return False, f"Project context for '{context.project_name}' is no longer valid."
        
        return True, f"Context valid for project '{context.project_name}'"
    
    def get_database_path(self) -> Optional[str]:
        """Get the database path from active context"""
        return get_active_database_path()
    
    def get_project_name(self) -> Optional[str]:
        """Get the project name from active context"""
        return get_active_project_name()
    
    def refresh_context(self) -> Dict[str, Any]:
        """
        Refresh the active context with updated information
        
        Returns:
            Dict with refresh results
        """
        if not has_active_context():
            return {
                "success": False,
                "message": "❌ No active context to refresh"
            }
        
        if self.registry.refresh_context_stats():
            return {
                "success": True,
                "message": "✅ Context refreshed successfully",
                "context": self.registry.get_context_info()
            }
        else:
            return {
                "success": False,
                "message": "❌ Failed to refresh context"
            }


class EnhancedContentTools:
    """
    Enhanced content tools that use the centralized context registry
    Provides registry-aware implementations of save_info, search_info, etc.
    """
    
    def __init__(self):
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
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error searching information: {str(e)}",
                "error": str(e)
            }


class EnhancedDocumentTools:
    """
    Enhanced document tools that use the centralized context registry
    Provides registry-aware implementations of save_document, search_documents, etc.
    """
    
    def __init__(self):
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
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error searching documents: {str(e)}",
                "error": str(e)
            }


# Global instances for tool integration
_enhanced_context_tools = EnhancedContextTools()
_enhanced_content_tools = EnhancedContentTools()
_enhanced_document_tools = EnhancedDocumentTools()


def enhanced_get_current_context() -> Dict[str, Any]:
    """Global function for enhanced get_current_context"""
    return _enhanced_context_tools.get_current_context()


def enhanced_save_info(content: str, category: str = "general", tags: str = "") -> Dict[str, Any]:
    """Global function for enhanced save_info"""
    return _enhanced_content_tools.save_info(content, category, tags)


def enhanced_search_info(query: str, limit: int = 10) -> Dict[str, Any]:
    """Global function for enhanced search_info"""
    return _enhanced_content_tools.search_info(query, limit)


def enhanced_save_document(title: str, content: str, doc_type: str = "general", 
                          tags: str = "") -> Dict[str, Any]:
    """Global function for enhanced save_document"""
    return _enhanced_document_tools.save_document(title, content, doc_type, tags)


def enhanced_search_documents(query: str, limit: int = 10) -> Dict[str, Any]:
    """Global function for enhanced search_documents"""
    return _enhanced_document_tools.search_documents(query, limit)
