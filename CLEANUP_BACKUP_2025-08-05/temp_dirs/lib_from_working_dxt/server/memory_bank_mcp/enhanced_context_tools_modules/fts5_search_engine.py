#!/usr/bin/env python3
"""
Filename: enhanced_context_tools_modules/fts5_search_engine.py
Generated: 2025-08-03.1757
Purpose: FTS5 full-text search engine with importance weighting and semantic integration

This module provides advanced FTS5-based search capabilities with importance weighting,
relevance ranking, and semantic query expansion for Memory Bank v2.0 Enhanced.
"""

import logging
import sqlite3
from typing import List, Dict, Any, Tuple
from enhanced_context_tools_modules.query_expander import SemanticQueryExpander

logger = logging.getLogger(__name__)


class FTS5SearchEngine:
    """
    Advanced FTS5 search engine with semantic expansion and importance weighting
    
    Provides sophisticated search capabilities that leverage:
    - FTS5 full-text search with relevance ranking
    - Semantic query expansion via equivalents table
    - Importance-weighted scoring (0-10 scale)
    - Advanced result ranking and filtering
    """
    
    def __init__(self, database_path: str):
        """
        Initialize FTS5 search engine
        
        Args:
            database_path: Path to database containing documents and documents_fts tables
        """
        self.database_path = database_path
        self.query_expander = SemanticQueryExpander(database_path)
        self.logger = logger
    
    def search_with_fts5(self, query: str, project_uuid: str, limit: int = 10,
                        min_importance: int = 0, context_domain: str = None,
                        include_snippets: bool = True) -> Dict[str, Any]:
        """
        Perform advanced FTS5 search with semantic expansion and importance weighting
        
        Args:
            query: Search query string
            project_uuid: Project UUID to search within
            limit: Maximum number of results
            min_importance: Minimum importance level (0-10)
            context_domain: Optional semantic context domain
            include_snippets: Whether to include highlighted snippets
            
        Returns:
            Dict with search results and metadata
        """
        try:
            # Step 1: Expand query using semantic equivalents
            expansion_result = self.query_expander.expand_query(
                query, context_domain=context_domain
            )
            
            if not expansion_result["success"]:
                # Fallback to simple search if expansion fails
                fts5_query = query
                expanded_terms = query.split()
            else:
                fts5_query = expansion_result["fts5_query"]
                expanded_terms = expansion_result["expanded_terms"]
            
            # Step 2: Execute FTS5 search with importance weighting
            search_results = self._execute_fts5_search(
                fts5_query, project_uuid, limit, min_importance, include_snippets
            )
            
            # Step 3: Format and rank results
            ranked_results = self._rank_and_format_results(
                search_results, query, expanded_terms
            )
            
            return {
                "success": True,
                "original_query": query,
                "fts5_query": fts5_query,
                "expanded_terms": expanded_terms,
                "expansion_metadata": expansion_result if expansion_result["success"] else None,
                "results": ranked_results,
                "result_count": len(ranked_results),
                "search_metadata": {
                    "min_importance": min_importance,
                    "context_domain": context_domain,
                    "snippets_included": include_snippets
                }
            }
            
        except Exception as e:
            self.logger.error(f"FTS5 search error for query '{query}': {e}")
            return {
                "success": False,
                "error": str(e),
                "original_query": query,
                "results": []
            }
    
    def _execute_fts5_search(self, fts5_query: str, project_uuid: str, 
                           limit: int, min_importance: int, 
                           include_snippets: bool) -> List[sqlite3.Row]:
        """
        Execute the FTS5 search query against documents_fts table
        
        Args:
            fts5_query: FTS5-formatted query string
            project_uuid: Project UUID filter
            limit: Maximum results
            min_importance: Minimum importance level
            include_snippets: Whether to include snippets
            
        Returns:
            List of database rows with results
        """
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Build the FTS5 search query with importance weighting
        if include_snippets:
            snippet_select = "snippet(documents_fts, 1, '<mark>', '</mark>', '...', 32) as snippet,"
        else:
            snippet_select = ""
        
        search_sql = f"""
            SELECT 
                d.uuid, d.version, d.document_type, d.title, d.content,
                d.summary, d.tags, d.created_at, d.updated_at, d.importance,
                {snippet_select}
                fts.rank,
                (fts.rank * d.importance) as weighted_score
            FROM documents d
            JOIN documents_fts fts ON d.rowid = fts.rowid
            WHERE d.project_uuid = ?
            AND d.status = 'active'
            AND d.importance >= ?
            AND documents_fts MATCH ?
            ORDER BY weighted_score DESC, d.importance DESC, fts.rank DESC
            LIMIT ?
        """
        
        cursor.execute(search_sql, (project_uuid, min_importance, fts5_query, limit))
        results = cursor.fetchall()
        
        conn.close()
        return results
    
    def _rank_and_format_results(self, results: List[sqlite3.Row], 
                                original_query: str, expanded_terms: List[str]) -> List[Dict[str, Any]]:
        """
        Rank and format search results with additional metadata
        
        Args:
            results: Raw database results
            original_query: Original search query
            expanded_terms: Expanded search terms
            
        Returns:
            List of formatted result dictionaries
        """
        formatted_results = []
        
        for i, row in enumerate(results):
            # Calculate additional relevance metrics
            title_matches = self._count_term_matches(row['title'], expanded_terms)
            content_matches = self._count_term_matches(row['content'], expanded_terms)
            
            result = {
                "rank": i + 1,
                "uuid": row['uuid'],
                "version": row['version'],
                "document_type": row['document_type'],
                "title": row['title'],
                "content": row['content'],
                "summary": row['summary'],
                "tags": row['tags'],
                "created_at": row['created_at'],
                "updated_at": row['updated_at'],
                "importance": row['importance'],
                "fts_rank": row['rank'],
                "weighted_score": row['weighted_score'],
                "relevance_metrics": {
                    "title_matches": title_matches,
                    "content_matches": content_matches,
                    "total_matches": title_matches + content_matches
                }
            }
            
            # Add snippet if available
            if 'snippet' in row.keys():
                result['snippet'] = row['snippet']
            
            formatted_results.append(result)
        
        return formatted_results
    
    def _count_term_matches(self, text: str, terms: List[str]) -> int:
        """
        Count how many search terms appear in the given text
        
        Args:
            text: Text to search in
            terms: List of search terms
            
        Returns:
            Number of term matches found
        """
        if not text or not terms:
            return 0
        
        text_lower = text.lower()
        matches = 0
        
        for term in terms:
            if term.lower() in text_lower:
                matches += 1
        
        return matches
    
    def search_by_importance_range(self, project_uuid: str, min_importance: int, 
                                 max_importance: int, limit: int = 20) -> Dict[str, Any]:
        """
        Search documents by importance range (useful for finding high-priority content)
        
        Args:
            project_uuid: Project UUID to search within
            min_importance: Minimum importance level
            max_importance: Maximum importance level
            limit: Maximum results
            
        Returns:
            Dict with results sorted by importance
        """
        try:
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT uuid, version, document_type, title, summary, 
                       importance, created_at, updated_at
                FROM documents
                WHERE project_uuid = ?
                AND status = 'active'
                AND importance BETWEEN ? AND ?
                ORDER BY importance DESC, updated_at DESC
                LIMIT ?
            """, (project_uuid, min_importance, max_importance, limit))
            
            results = cursor.fetchall()
            conn.close()
            
            formatted_results = []
            for row in results:
                formatted_results.append({
                    "uuid": row['uuid'],
                    "version": row['version'],
                    "document_type": row['document_type'],
                    "title": row['title'],
                    "summary": row['summary'],
                    "importance": row['importance'],
                    "created_at": row['created_at'],
                    "updated_at": row['updated_at']
                })
            
            return {
                "success": True,
                "results": formatted_results,
                "count": len(formatted_results),
                "search_params": {
                    "min_importance": min_importance,
                    "max_importance": max_importance,
                    "limit": limit
                }
            }
            
        except Exception as e:
            self.logger.error(f"Importance range search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def get_fts5_statistics(self, project_uuid: str) -> Dict[str, Any]:
        """
        Get FTS5 indexing and search statistics for the project
        
        Args:
            project_uuid: Project UUID
            
        Returns:
            Dict with FTS5 statistics
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Total documents in FTS index
            cursor.execute("SELECT COUNT(*) FROM documents_fts")
            total_fts_docs = cursor.fetchone()[0]
            
            # Project-specific document counts
            cursor.execute("""
                SELECT COUNT(*) FROM documents 
                WHERE project_uuid = ? AND status = 'active'
            """, (project_uuid,))
            project_docs = cursor.fetchone()[0]
            
            # Importance distribution
            cursor.execute("""
                SELECT importance, COUNT(*) as count
                FROM documents 
                WHERE project_uuid = ? AND status = 'active'
                GROUP BY importance
                ORDER BY importance DESC
            """, (project_uuid,))
            importance_dist = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "total_fts_documents": total_fts_docs,
                "project_documents": project_docs,
                "importance_distribution": importance_dist,
                "fts5_enabled": total_fts_docs > 0,
                "semantic_equivalents": self.query_expander.get_equivalents_stats()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting FTS5 statistics: {e}")
            return {"error": str(e)}
