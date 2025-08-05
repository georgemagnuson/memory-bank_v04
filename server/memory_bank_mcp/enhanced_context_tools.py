#!/usr/bin/env python3
"""
Filename: enhanced_context_tools.py
Generated: 2025-08-03.1749 (Modularized)
Purpose: Enhanced context management tools using centralized context registry (Modular Version)

MODULARIZATION COMPLETE:
This file has been refactored into focused modules:
- enhanced_context_tools_modules/context_manager.py: Context validation and management
- enhanced_context_tools_modules/content_operations.py: Information storage and search
- enhanced_context_tools_modules/document_operations.py: Document storage and search

This main file provides the same interface as before while delegating to specialized modules.
Future enhancements (FTS5 + semantic search) will be added as additional modules.
"""

from typing import Dict, Any

# Import modular components
try:
    from memory_bank_mcp.enhanced_context_tools_modules import (
        EnhancedContextTools,
        EnhancedContentTools, 
        EnhancedDocumentTools
    )
except ImportError:
    try:
        from .enhanced_context_tools_modules import (
            EnhancedContextTools,
            EnhancedContentTools, 
            EnhancedDocumentTools
        )
    except ImportError:
        from enhanced_context_tools_modules import (
            EnhancedContextTools,
            EnhancedContentTools, 
            EnhancedDocumentTools
        )

# Global instances for tool integration - maintains backward compatibility
_enhanced_context_tools = EnhancedContextTools()
_enhanced_content_tools = EnhancedContentTools()
_enhanced_document_tools = EnhancedDocumentTools()


# Global functions for MCP tool integration - same interface as before
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


# Export classes for direct use (backward compatibility)
__all__ = [
    'EnhancedContextTools',
    'EnhancedContentTools',
    'EnhancedDocumentTools',
    'enhanced_get_current_context',
    'enhanced_save_info',
    'enhanced_search_info',
    'enhanced_save_document',
    'enhanced_search_documents'
]
