#!/usr/bin/env python3
"""
Filename: enhanced_context_tools_modules/document_operations.py
Generated: 2025-08-03.1800 (Updated: 2025-08-03.1825)
Purpose: Enhanced document operations with FTS5 + semantic search capabilities

This is the enhanced version of document_operations.py that replaces basic LIKE queries
with sophisticated FTS5 + semantic search using the query expander and search engine.
"""

from typing import Dict, Any


class EnhancedDocumentTools:
    """
    Enhanced document tools with FTS5 + semantic search capabilities
    Provides advanced document search using semantic equivalents and importance weighting
    """
    
    def __init__(self):
        # Import registry and context tools with same pattern as main.py (working)
        from context_registry import get_global_registry
        from enhanced_context_tools_modules.context_manager import EnhancedContextTools
        
        self.registry = get_global_registry()
        self.context_tools = EnhancedContextTools()
        self.search_engine = None  # Initialize when database path is available
    
    def _get_search_engine(self) -> 'FTS5SearchEngine':
        """Get or create FTS5 search engine instance"""
        if self.search_engine is None:
            database_path = self.context_tools.get_database_path()
            if database_path:
                from enhanced_context_tools_modules.fts5_search_engine import FTS5SearchEngine
                self.search_engine = FTS5SearchEngine(database_path)
        
        return self.search_engine
    
    def save_document(self, title: str, content: str, doc_type: str = "general", 
                     tags: str = "", importance: int = None) -> Dict[str, Any]:
        """
        Save document using active context from registry with enhanced importance scoring
        
        Args:
            title: Document title
            content: Document content
            doc_type: Document type
            tags: Optional tags
            importance: Optional explicit importance (0-10), auto-calculated if None
            
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
            
            # Calculate importance if not provided
            if importance is None:
                importance = self._calculate_document_importance(title, content, doc_type)
            else:
                importance = max(0, min(10, importance))  # Clamp to valid range
            
            # Create summary from content
            summary = content[:300] + "..." if len(content) > 300 else content
            
            # Insert into v2.0 documents table with enhanced importance
            cursor.execute("""
                INSERT INTO documents (
                    project_uuid, uuid, version, document_type, title, content,
                    summary, tags, metadata, created_at, updated_at, status, importance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_uuid, doc_uuid, doc_version, doc_type, title, content,
                summary, tags_json,
                '{"source": "enhanced_save_document"}',  # Metadata
                timestamp, timestamp, 'active', importance
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"✅ Document '{title}' saved to {project_name} (importance: {importance})",
                "database_path": database_path,
                "title": title,
                "doc_type": doc_type,
                "content_length": len(content),
                "document_uuid": doc_uuid,
                "project_uuid": project_uuid,
                "importance": importance
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error saving document: {str(e)}",
                "error": str(e)
            }
    
    def _calculate_document_importance(self, title: str, content: str, doc_type: str) -> int:
        """
        Calculate document importance score (0-10) based on characteristics
        
        Args:
            title: Document title
            content: Document content
            doc_type: Document type
            
        Returns:
            Importance score (0-10)
        """
        importance = 5  # Default
        
        # Document type weights
        type_weights = {
            "architecture": 9,
            "critical": 9,
            "decision": 8,
            "design": 7,
            "plan": 7,
            "document": 6,
            "code": 6,
            "note": 5,
            "general": 5,
            "markdown": 4,
            "temp": 2,
            "test": 2
        }
        
        importance = type_weights.get(doc_type.lower(), 5)
        
        # Title importance indicators
        title_lower = title.lower()
        if any(word in title_lower for word in ['critical', 'urgent', 'important', 'breaking']):
            importance += 2
        elif any(word in title_lower for word in ['architecture', 'design', 'decision']):
            importance += 1
        elif any(word in title_lower for word in ['temp', 'test', 'scratch', 'debug']):
            importance -= 2
        
        # Content length consideration
        content_length = len(content)
        if content_length > 2000:
            importance += 1  # Substantial documents
        elif content_length < 200:
            importance -= 1  # Very brief documents
        
        # Clamp to valid range
        return max(0, min(10, importance))
    
    def search_documents(self, query: str, limit: int = 10, min_importance: int = 0,
                        context_domain: str = None, document_type: str = None,
                        use_semantic: bool = True) -> Dict[str, Any]:
        """
        Enhanced document search using FTS5 + semantic expansion
        
        Args:
            query: Search query
            limit: Maximum results to return
            min_importance: Minimum importance level (0-10)
            context_domain: Optional semantic context domain filter
            document_type: Optional document type filter
            use_semantic: Whether to use semantic expansion
            
        Returns:
            Dict with enhanced search results
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
            conn.close()
            
            # Use FTS5 + semantic search if enabled, otherwise fallback to LIKE
            if use_semantic:
                search_engine = self._get_search_engine()
                if search_engine:
                    return self._enhanced_document_search(
                        search_engine, query, project_uuid, limit, 
                        min_importance, context_domain, document_type, project_name
                    )
            
            # Fallback to basic LIKE search with document type filter
            return self._fallback_document_search(
                query, project_uuid, limit, min_importance, 
                document_type, project_name, database_path
            )
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error searching documents: {str(e)}",
                "error": str(e),
                "results": []
            }
    
    def _enhanced_document_search(self, search_engine, query: str, project_uuid: str,
                                 limit: int, min_importance: int, context_domain: str,
                                 document_type: str, project_name: str) -> Dict[str, Any]:
        """
        Perform enhanced FTS5 + semantic document search
        """
        search_result = search_engine.search_with_fts5(
            query=query,
            project_uuid=project_uuid,
            limit=limit,
            min_importance=min_importance,
            context_domain=context_domain,
            include_snippets=True
        )
        
        if search_result["success"]:
            # Filter by document type if specified
            results = search_result["results"]
            if document_type:
                results = [r for r in results if r["document_type"].lower() == document_type.lower()]
            
            # Format results for document interface
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "uuid": result["uuid"],
                    "version": result["version"],
                    "document_type": result["document_type"],
                    "title": result["title"],
                    "content": result["content"],
                    "summary": result["summary"],
                    "snippet": result.get("snippet", result["summary"]),
                    "tags": result["tags"],
                    "created_at": result["created_at"],
                    "updated_at": result["updated_at"],
                    "status": "active",
                    "importance": result["importance"],
                    "relevance_score": result["weighted_score"],
                    "fts_rank": result["fts_rank"],
                    "relevance_metrics": result["relevance_metrics"]
                })
            
            return {
                "success": True,
                "message": f"🔍 Found {len(formatted_results)} documents using FTS5 + semantic search",
                "search_type": "FTS5 + Semantic (Documents)",
                "original_query": search_result["original_query"],
                "expanded_query": search_result["fts5_query"],
                "expanded_terms": search_result["expanded_terms"],
                "expansion_metadata": search_result.get("expansion_metadata"),
                "results": formatted_results,
                "count": len(formatted_results),
                "project_name": project_name,
                "search_params": {
                    "min_importance": min_importance,
                    "context_domain": context_domain,
                    "document_type": document_type,
                    "semantic_enabled": True
                }
            }
        else:
            return {
                "success": False,
                "message": f"❌ FTS5 document search failed: {search_result.get('error', 'Unknown error')}",
                "results": []
            }
    
    def _fallback_document_search(self, query: str, project_uuid: str, limit: int,
                                 min_importance: int, document_type: str, 
                                 project_name: str, database_path: str) -> Dict[str, Any]:
        """
        Fallback LIKE-based document search when FTS5 is not available
        """
        import sqlite3
        
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build query with optional document type filter
        where_conditions = [
            "project_uuid = ?",
            "importance >= ?",
            "status = 'active'",
            "(content LIKE ? OR title LIKE ? OR summary LIKE ? OR tags LIKE ?)"
        ]
        params = [project_uuid, min_importance, f"%{query}%", f"%{query}%", f"%{query}%", f"%{query}%"]
        
        if document_type:
            where_conditions.append("document_type = ?")
            params.append(document_type)
        
        search_sql = f"""
            SELECT uuid, version, document_type, title, content,
                   summary, tags, created_at, updated_at, status, importance
            FROM documents 
            WHERE {" AND ".join(where_conditions)}
            ORDER BY importance DESC, updated_at DESC 
            LIMIT ?
        """
        params.append(limit)
        
        cursor.execute(search_sql, params)
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
                "content": row["content"],
                "summary": row["summary"],
                "tags": row["tags"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "status": row["status"],
                "importance": row["importance"]
            })
        
        return {
            "success": True,
            "message": f"📄 Found {len(formatted_results)} documents using LIKE search (FTS5 unavailable)",
            "search_type": "LIKE (Fallback)",
            "original_query": query,
            "results": formatted_results,
            "count": len(formatted_results),
            "project_name": project_name,
            "search_params": {
                "min_importance": min_importance,
                "document_type": document_type,
                "semantic_enabled": False
            }
        }
    
    def get_documents_by_type(self, document_type: str, limit: int = 20) -> Dict[str, Any]:
        """
        Get documents filtered by type with importance ranking
        
        Args:
            document_type: Type of documents to retrieve
            limit: Maximum results
            
        Returns:
            Dict with filtered documents
        """
        # Validate context first
        is_valid, message = self.context_tools.validate_context()
        if not is_valid:
            return {
                "success": False,
                "message": f"❌ Context Error: {message}",
                "results": []
            }
        
        try:
            database_path = self.context_tools.get_database_path()
            project_name = self.context_tools.get_project_name()
            
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
            
            # Get documents by type
            cursor.execute("""
                SELECT uuid, version, document_type, title, summary,
                       tags, created_at, updated_at, importance
                FROM documents
                WHERE project_uuid = ?
                AND document_type = ?
                AND status = 'active'
                ORDER BY importance DESC, updated_at DESC
                LIMIT ?
            """, (project_uuid, document_type, limit))
            
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
                    "summary": row["summary"],
                    "tags": row["tags"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "importance": row["importance"]
                })
            
            return {
                "success": True,
                "message": f"📋 Found {len(formatted_results)} {document_type} documents",
                "document_type": document_type,
                "results": formatted_results,
                "count": len(formatted_results),
                "project_name": project_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error getting documents by type: {str(e)}",
                "results": []
            }
