#!/usr/bin/env python3
"""
Filename: enhanced_context_tools_modules/content_operations.py
Generated: 2025-08-03.1758 (Updated: 2025-08-03.1825)
Purpose: Enhanced content operations with FTS5 + semantic search capabilities

This is the enhanced version of content_operations.py that replaces basic LIKE queries
with sophisticated FTS5 + semantic search using the query expander and search engine.
"""

from typing import Dict, Any


class EnhancedContentTools:
    """
    Enhanced content tools with FTS5 + semantic search capabilities
    Provides advanced search using semantic equivalents and importance weighting
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
            
            # Insert into v2.0 documents table with importance scoring
            # Auto-assign importance based on content characteristics
            importance = self._calculate_content_importance(content, category)
            
            cursor.execute("""
                INSERT INTO documents (
                    project_uuid, uuid, version, document_type, title, content,
                    summary, tags, metadata, created_at, updated_at, status, importance
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                project_uuid, doc_uuid, doc_version, doc_type, title, content,
                content[:200] + "..." if len(content) > 200 else content,  # Summary
                tags_json,
                '{"source": "enhanced_save_info", "category": "' + category + '"}',  # Metadata
                timestamp, timestamp, 'active', importance
            ))
            
            conn.commit()
            conn.close()
            
            return {
                "success": True,
                "message": f"✅ Information saved to {project_name} (importance: {importance})",
                "database_path": database_path,
                "category": category,
                "content_length": len(content),
                "document_uuid": doc_uuid,
                "project_uuid": project_uuid,
                "importance": importance
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error saving information: {str(e)}",
                "error": str(e)
            }
    
    def _calculate_content_importance(self, content: str, category: str) -> int:
        """
        Calculate importance score (0-10) based on content characteristics
        
        Args:
            content: Content text
            category: Content category
            
        Returns:
            Importance score (0-10)
        """
        importance = 5  # Default importance
        
        # Adjust based on category
        category_weights = {
            "critical": 9,
            "important": 8,
            "decision": 8,
            "architecture": 7,
            "design": 6,
            "plan": 6,
            "note": 5,
            "general": 5,
            "temp": 3,
            "test": 2
        }
        
        importance = category_weights.get(category.lower(), 5)
        
        # Adjust based on content length and characteristics
        content_length = len(content)
        if content_length > 1000:
            importance += 1  # Longer content tends to be more important
        elif content_length < 100:
            importance -= 1  # Very short content might be less important
        
        # Look for importance indicators in content
        content_lower = content.lower()
        high_importance_keywords = ['critical', 'urgent', 'important', 'decision', 'architecture', 'breaking']
        low_importance_keywords = ['test', 'temp', 'temporary', 'debug', 'scratch']
        
        for keyword in high_importance_keywords:
            if keyword in content_lower:
                importance += 1
                break
        
        for keyword in low_importance_keywords:
            if keyword in content_lower:
                importance -= 1
                break
        
        # Clamp to valid range
        return max(0, min(10, importance))
    
    def search_info(self, query: str, limit: int = 10, min_importance: int = 0, 
                   context_domain: str = None, use_semantic: bool = True) -> Dict[str, Any]:
        """
        Enhanced search using FTS5 + semantic expansion - ADVANCED SEARCH IMPLEMENTATION
        
        Args:
            query: Search query
            limit: Maximum results to return
            min_importance: Minimum importance level (0-10)
            context_domain: Optional semantic context domain filter
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
                    return self._enhanced_fts5_search(
                        search_engine, query, project_uuid, limit, 
                        min_importance, context_domain, project_name
                    )
            
            # Fallback to basic LIKE search
            return self._fallback_like_search(
                query, project_uuid, limit, min_importance, project_name, database_path
            )
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error searching information: {str(e)}",
                "error": str(e),
                "results": []
            }
    
    def _enhanced_fts5_search(self, search_engine, query: str, project_uuid: str, 
                             limit: int, min_importance: int, context_domain: str, 
                             project_name: str) -> Dict[str, Any]:
        """
        Perform enhanced FTS5 + semantic search
        
        Args:
            search_engine: FTS5SearchEngine instance
            query: Search query
            project_uuid: Project UUID
            limit: Result limit
            min_importance: Minimum importance level
            context_domain: Semantic context domain
            project_name: Project name for display
            
        Returns:
            Dict with enhanced search results
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
            # Format results for compatibility with existing interface
            formatted_results = []
            for result in search_result["results"]:
                formatted_results.append({
                    "uuid": result["uuid"],
                    "version": result["version"],
                    "document_type": result["document_type"],
                    "title": result["title"],
                    "content_preview": result.get("snippet", result["summary"]),
                    "tags": result["tags"],
                    "created_at": result["created_at"],
                    "updated_at": result["updated_at"],
                    "importance": result["importance"],
                    "relevance_score": result["weighted_score"],
                    "fts_rank": result["fts_rank"]
                })
            
            return {
                "success": True,
                "message": f"🔍 Found {len(formatted_results)} results using FTS5 + semantic search",
                "search_type": "FTS5 + Semantic",
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
                    "semantic_enabled": True
                }
            }
        else:
            return {
                "success": False,
                "message": f"❌ FTS5 search failed: {search_result.get('error', 'Unknown error')}",
                "results": []
            }
    
    def _fallback_like_search(self, query: str, project_uuid: str, limit: int, 
                             min_importance: int, project_name: str, database_path: str) -> Dict[str, Any]:
        """
        Fallback LIKE-based search when FTS5 is not available
        
        Args:
            query: Search query
            project_uuid: Project UUID
            limit: Result limit
            min_importance: Minimum importance
            project_name: Project name
            database_path: Database path
            
        Returns:
            Dict with search results
        """
        import sqlite3
        
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Enhanced LIKE search with importance filtering
        search_query = f"%{query}%"
        cursor.execute("""
            SELECT uuid, version, document_type, title, 
                   substr(content, 1, 200) as content_preview,
                   tags, created_at, updated_at, importance
            FROM documents 
            WHERE project_uuid = ? 
            AND importance >= ?
            AND (
                content LIKE ? OR 
                title LIKE ? OR 
                tags LIKE ?
            ) 
            AND status = 'active'
            ORDER BY importance DESC, updated_at DESC 
            LIMIT ?
        """, (project_uuid, min_importance, search_query, search_query, search_query, limit))
        
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
                "updated_at": row["updated_at"],
                "importance": row["importance"]
            })
        
        return {
            "success": True,
            "message": f"📝 Found {len(formatted_results)} results using LIKE search (FTS5 unavailable)",
            "search_type": "LIKE (Fallback)",
            "original_query": query,
            "results": formatted_results,
            "count": len(formatted_results),
            "project_name": project_name,
            "search_params": {
                "min_importance": min_importance,
                "semantic_enabled": False
            }
        }
    
    def search_by_importance(self, min_importance: int = 7, limit: int = 20) -> Dict[str, Any]:
        """
        Search for high-importance content in the current project
        
        Args:
            min_importance: Minimum importance level (0-10)
            limit: Maximum results
            
        Returns:
            Dict with high-importance results
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
            search_engine = self._get_search_engine()
            if search_engine:
                database_path = self.context_tools.get_database_path()
                project_name = self.context_tools.get_project_name()
                
                import sqlite3
                conn = sqlite3.connect(database_path)
                cursor = conn.cursor()
                
                cursor.execute("SELECT uuid FROM projects WHERE name = ?", (project_name,))
                project_result = cursor.fetchone()
                conn.close()
                
                if project_result:
                    project_uuid = project_result[0]
                    return search_engine.search_by_importance_range(
                        project_uuid, min_importance, 10, limit
                    )
            
            return {
                "success": False,
                "message": "❌ Search engine not available",
                "results": []
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error searching by importance: {str(e)}",
                "results": []
            }
