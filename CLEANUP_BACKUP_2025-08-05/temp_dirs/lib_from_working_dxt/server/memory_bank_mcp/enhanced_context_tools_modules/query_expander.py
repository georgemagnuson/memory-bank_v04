#!/usr/bin/env python3
"""
Filename: enhanced_context_tools_modules/query_expander.py
Generated: 2025-08-03.1756
Purpose: Semantic query expansion using equivalents table for enhanced search

This module provides intelligent query expansion by leveraging the semantic_equivalents
table to find related terms and concepts, dramatically improving search recall.
"""

import logging
from typing import List, Dict, Any, Set, Tuple
import sqlite3

logger = logging.getLogger(__name__)


class SemanticQueryExpander:
    """
    Semantic query expansion engine using the semantic_equivalents table
    
    Expands search queries with related terms based on semantic equivalents,
    context domains, and confidence levels for improved search results.
    """
    
    def __init__(self, database_path: str):
        """
        Initialize semantic query expander
        
        Args:
            database_path: Path to the database containing semantic_equivalents table
        """
        self.database_path = database_path
        self.logger = logger
        
    def expand_query(self, query: str, context_domain: str = None, 
                    min_confidence: int = 7) -> Dict[str, Any]:
        """
        Expand a search query using semantic equivalents
        
        Args:
            query: Original search query
            context_domain: Optional context domain filter ('dxt', 'spec_workflow', etc.)
            min_confidence: Minimum confidence level for equivalents (0-10)
            
        Returns:
            Dict containing expanded terms and metadata
        """
        try:
            # Tokenize the original query
            query_terms = self._tokenize_query(query)
            
            # Find semantic equivalents for each term
            expanded_terms = set(query_terms)  # Start with original terms
            equivalents_found = {}
            
            conn = sqlite3.connect(self.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            for term in query_terms:
                # Find equivalents where this term is the primary term
                equivalents = self._find_equivalents_for_term(
                    cursor, term, context_domain, min_confidence
                )
                
                if equivalents:
                    equivalents_found[term] = equivalents
                    expanded_terms.update(equivalents['equivalent_terms'])
            
            conn.close()
            
            # Build FTS5 query components
            fts5_query = self._build_fts5_query(list(expanded_terms))
            
            return {
                "success": True,
                "original_query": query,
                "original_terms": query_terms,
                "expanded_terms": list(expanded_terms),
                "equivalents_found": equivalents_found,
                "fts5_query": fts5_query,
                "expansion_count": len(expanded_terms) - len(query_terms),
                "total_terms": len(expanded_terms)
            }
            
        except Exception as e:
            self.logger.error(f"Error expanding query '{query}': {e}")
            return {
                "success": False,
                "error": str(e),
                "original_query": query,
                "expanded_terms": query.split(),  # Fallback to simple tokenization
                "fts5_query": query  # Fallback to original query
            }
    
    def _tokenize_query(self, query: str) -> List[str]:
        """
        Tokenize query into searchable terms
        
        Args:
            query: Search query string
            
        Returns:
            List of cleaned, normalized terms
        """
        import re
        
        # Convert to lowercase and extract words
        terms = re.findall(r'\b\w+\b', query.lower())
        
        # Remove common stop words (basic set)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        # Filter out stop words and short terms
        filtered_terms = [term for term in terms if term not in stop_words and len(term) > 2]
        
        return filtered_terms
    
    def _find_equivalents_for_term(self, cursor: sqlite3.Cursor, term: str, 
                                  context_domain: str = None, 
                                  min_confidence: int = 7) -> Dict[str, Any]:
        """
        Find semantic equivalents for a specific term
        
        Args:
            cursor: Database cursor
            term: Term to find equivalents for
            context_domain: Optional context domain filter
            min_confidence: Minimum confidence level
            
        Returns:
            Dict with equivalents data or None if not found
        """
        import json
        
        # Build query with optional context domain filter
        base_query = """
            SELECT primary_term, equivalent_terms, context_domain, confidence_level, description
            FROM semantic_equivalents 
            WHERE confidence_level >= ?
            AND (
                primary_term = ? OR 
                equivalent_terms LIKE ?
            )
        """
        
        params = [min_confidence, term, f'%"{term}"%']
        
        if context_domain:
            base_query += " AND context_domain = ?"
            params.append(context_domain)
        
        base_query += " ORDER BY confidence_level DESC"
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        if not results:
            return None
        
        # Combine all equivalent terms from matching rows
        all_equivalents = set()
        matched_entries = []
        
        for row in results:
            try:
                equivalent_terms = json.loads(row['equivalent_terms'])
                all_equivalents.update(equivalent_terms)
                matched_entries.append({
                    "primary_term": row['primary_term'],
                    "context_domain": row['context_domain'],
                    "confidence_level": row['confidence_level'],
                    "description": row['description']
                })
            except json.JSONDecodeError:
                # Handle non-JSON format if any
                continue
        
        return {
            "term": term,
            "equivalent_terms": list(all_equivalents),
            "matched_entries": matched_entries,
            "total_equivalents": len(all_equivalents)
        }
    
    def _build_fts5_query(self, terms: List[str]) -> str:
        """
        Build FTS5 MATCH query from expanded terms
        
        Args:
            terms: List of search terms
            
        Returns:
            FTS5-compatible query string
        """
        if not terms:
            return ""
        
        # Escape terms for FTS5
        escaped_terms = []
        for term in terms:
            # Basic FTS5 escaping - wrap in quotes and escape internal quotes
            escaped_term = f'"{term.replace('"', '""')}"'
            escaped_terms.append(escaped_term)
        
        # Join terms with OR for broader matching
        fts5_query = " OR ".join(escaped_terms)
        
        return fts5_query
    
    def get_context_domains(self) -> List[str]:
        """
        Get all available context domains from semantic_equivalents table
        
        Returns:
            List of context domain names
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT context_domain FROM semantic_equivalents ORDER BY context_domain")
            domains = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return domains
            
        except Exception as e:
            self.logger.error(f"Error getting context domains: {e}")
            return []
    
    def get_equivalents_stats(self) -> Dict[str, Any]:
        """
        Get statistics about semantic equivalents in the database
        
        Returns:
            Dict with equivalents statistics
        """
        try:
            conn = sqlite3.connect(self.database_path)
            cursor = conn.cursor()
            
            # Total count
            cursor.execute("SELECT COUNT(*) FROM semantic_equivalents")
            total_count = cursor.fetchone()[0]
            
            # By domain
            cursor.execute("""
                SELECT context_domain, COUNT(*) as count 
                FROM semantic_equivalents 
                GROUP BY context_domain 
                ORDER BY count DESC
            """)
            by_domain = dict(cursor.fetchall())
            
            # By confidence level
            cursor.execute("""
                SELECT confidence_level, COUNT(*) as count 
                FROM semantic_equivalents 
                GROUP BY confidence_level 
                ORDER BY confidence_level DESC
            """)
            by_confidence = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                "total_equivalents": total_count,
                "by_domain": by_domain,
                "by_confidence": by_confidence,
                "domains_available": list(by_domain.keys())
            }
            
        except Exception as e:
            self.logger.error(f"Error getting equivalents stats: {e}")
            return {"error": str(e)}
