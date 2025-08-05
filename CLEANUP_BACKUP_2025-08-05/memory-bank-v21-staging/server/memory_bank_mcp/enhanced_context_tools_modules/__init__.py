#!/usr/bin/env python3
"""
Filename: enhanced_context_tools_modules/__init__.py
Generated: 2025-08-03.1801 (Updated with FTS5 + Semantic Search)
Purpose: Enhanced Context Tools modular components initialization with FTS5 capabilities

This module provides modular components for the Enhanced Context Tools system:
- context_manager: Context validation and management
- content_operations: Information storage and FTS5 + semantic search 
- document_operations: Document storage and FTS5 + semantic search
- query_expander: Semantic query expansion using equivalents table
- fts5_search_engine: Advanced FTS5 search with importance weighting
"""

# Import enhanced versions with FTS5 + semantic search
from .context_manager import EnhancedContextTools
from .content_operations import EnhancedContentTools  
from .document_operations import EnhancedDocumentTools
from .query_expander import SemanticQueryExpander
from .fts5_search_engine import FTS5SearchEngine

__all__ = [
    'EnhancedContextTools',
    'EnhancedContentTools', 
    'EnhancedDocumentTools',
    'SemanticQueryExpander',
    'FTS5SearchEngine'
]

__version__ = "2.1.0"
__author__ = "Memory Bank Development Team"
__description__ = "Enhanced Context Tools with FTS5 + Semantic Search"
