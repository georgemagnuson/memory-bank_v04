#!/usr/bin/env python3
"""
content_tools.py
Generated: 2025-07-30.1439
Purpose: Content search and management tools for v2.0 documents table architecture

v2.0 CLEAN VERSION (No Backward Compatibility):
- Uses documents table exclusively
- Modular architecture with content_tools_modules/
- Uses uuid field and project_uuid throughout
- Updated FTS table references (documents_fts only)

Modular Components:
- SearchEngine: Core v2.0 search functionality
- ImportManager: Markdown file discovery and import
- FTSManager: Full-text search synchronization
"""

import logging
from typing import Optional, List, Dict, Any

# Import modular components for v2.0 architecture (DXT compatible)
from .content_tools_modules import SearchEngine, ImportManager, FTSManager

logger = logging.getLogger(__name__)

class ContentTools:
    """Content search and management tools for v2.0 documents table architecture"""
    
    def __init__(self, context_manager):
        """Initialize ContentTools with v2.0 modular architecture
        
        Args:
            context_manager: Active ContextManager instance with database connection
        """
        self.context_manager = context_manager
        self.logger = logger
        
        # Initialize modular components
        self.search_engine = SearchEngine(context_manager)
        self.import_manager = ImportManager(context_manager)
        self.fts_manager = FTSManager(context_manager)
    
    # =============================================================================
    # PRIMARY SEARCH INTERFACE (v2.0)
    # =============================================================================
    
    async def search_all_content(self, query: str, limit: int = 20, content_types: str = "all") -> str:
        """Universal full-text search across v2.0 documents table with type filtering
        
        Args:
            query: Search query string
            limit: Maximum number of results to return (default: 20)
            content_types: Comma-separated document types or "all" (default: "all")
                          Options: discussion,document,plan,code,note,markdown,artifact,chat_session
        
        Returns:
            Formatted search results with ranking, highlighting, and metadata
        """
        return await self.search_engine.search_all_content(query, limit, content_types)
    
    # =============================================================================
    # FTS MANAGEMENT INTERFACE (v2.0)
    # =============================================================================
    
    async def sync_fts_tables(self) -> str:
        """Synchronize FTS5 virtual tables for v2.0 documents architecture
        
        Returns:
            Status report of synchronization operation
        """
        return await self.fts_manager.sync_fts_tables()
    
    async def get_fts_status(self) -> str:
        """Get detailed status of all FTS tables
        
        Returns:
            Status report of FTS table health
        """
        return await self.fts_manager.get_fts_status()
    
    # =============================================================================
    # IMPORT MANAGEMENT INTERFACE (v2.0)
    # =============================================================================
    
    async def import_markdown_files(self, directory_path: str, file_pattern: str = "*.md", 
                                  recursive: bool = True) -> str:
        """Import markdown files into v2.0 documents table
        
        Args:
            directory_path: Directory to scan for markdown files
            file_pattern: File pattern to match (default: "*.md")
            recursive: Whether to scan subdirectories recursively
            
        Returns:
            Import status report
        """
        return await self.import_manager.import_markdown_files(directory_path, file_pattern, recursive)
    
    async def discover_and_import_all_markdown(self, directory_path: str, exclude_patterns: str = "", 
                                             max_file_size_mb: int = 10) -> str:
        """Discover and import all markdown files with intelligent filtering
        
        Args:
            directory_path: Root directory to scan
            exclude_patterns: Comma-separated patterns to exclude
            max_file_size_mb: Maximum file size in MB
            
        Returns:
            Discovery and import report
        """
        return await self.import_manager.discover_and_import_all_markdown(
            directory_path, exclude_patterns, max_file_size_mb
        )
    
    async def import_project_documentation(self, include_external: bool = True) -> str:
        """Import all documentation from current project into v2.0 documents table
        
        Args:
            include_external: Whether to include external documentation
            
        Returns:
            Import status report
        """
        return await self.import_manager.import_project_documentation(include_external)
    
    async def generate_markdown_import_report(self) -> str:
        """Generate comprehensive report of imported markdown files from v2.0 documents table
        
        Returns:
            Detailed markdown import report
        """
        return await self.import_manager.generate_markdown_import_report()
    
    # =============================================================================
    # UTILITY AND INFORMATION METHODS
    # =============================================================================
    
    def get_supported_document_types(self) -> List[str]:
        """Get list of supported document types for v2.0 architecture"""
        return self.search_engine.get_supported_document_types()
    
    def get_priority_order(self) -> List[str]:
        """Get document type priority order for search results"""
        return self.search_engine.get_priority_order()
    
    def get_supported_fts_tables(self) -> Dict[str, str]:
        """Get mapping of supported FTS tables to their main tables"""
        return self.fts_manager.get_supported_fts_tables()
    
    def get_supported_patterns(self) -> List[str]:
        """Get list of supported markdown file patterns"""
        return self.import_manager.get_supported_patterns()
    
    def get_exclude_patterns(self) -> set:
        """Get set of default exclude patterns"""
        return self.import_manager.get_exclude_patterns()
    
    # =============================================================================
    # SYSTEM STATUS AND DIAGNOSTICS
    # =============================================================================
    
    async def get_content_tools_status(self) -> str:
        """Get comprehensive status of content tools v2.0 system
        
        Returns:
            Detailed status report of all content tools components
        """
        try:
            if not self.context_manager or not self.context_manager.database_path:
                return "❌ **CONTENT TOOLS STATUS FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            # Get project UUID
            project_uuid = getattr(self.context_manager, 'project_uuid', None)
            
            # Get FTS status
            fts_status = await self.fts_manager.get_fts_status()
            
            # Get document counts by type
            import sqlite3
            conn = sqlite3.connect(self.context_manager.database_path)
            cursor = conn.cursor()
            
            # Count documents by type
            cursor.execute("""
                SELECT document_type, COUNT(*) as count
                FROM documents 
                WHERE project_uuid = ? AND status = 'active'
                GROUP BY document_type
                ORDER BY count DESC
            """, (project_uuid,))
            
            doc_counts = cursor.fetchall()
            
            # Total document count
            cursor.execute("""
                SELECT COUNT(*) as total
                FROM documents 
                WHERE project_uuid = ? AND status = 'active'
            """, (project_uuid,))
            
            total_docs = cursor.fetchone()[0]
            
            conn.close()
            
            # Get type icons from search engine
            type_icons = self.search_engine.type_icons
            
            # Format status report
            status_lines = [
                "📊 **CONTENT TOOLS v2.0 STATUS**",
                "",
                f"**Project:** {project_uuid[:8] if project_uuid else 'Unknown'}...",
                f"**Total Documents:** {total_docs:,}",
                "",
                "**Document Types:**"
            ]
            
            for doc_type, count in doc_counts:
                icon = type_icons.get(doc_type, '📄')
                status_lines.append(f"- {icon} **{doc_type}**: {count:,} documents")
            
            status_lines.extend([
                "",
                "**v2.0 Modular Components:**",
                "- ✅ SearchEngine (documents table with project_uuid)",
                "- ✅ ImportManager (enhanced metadata with content hashing)",
                "- ✅ FTSManager (multi-table FTS support)",
                "",
                "**Available Operations:**",
                "- `search_all_content()` - Universal search across all document types",
                "- `import_markdown_files()` - Import with v2.0 metadata structure",
                "- `sync_fts_tables()` - Synchronize search indexes",
                "- `generate_markdown_import_report()` - Import analytics",
                "",
                f"**FTS Status:**",
                f"{fts_status}"
            ])
            
            return "\n".join(status_lines)
            
        except Exception as e:
            self.logger.error(f"Content tools status failed: {e}")
            return f"❌ **CONTENT TOOLS STATUS FAILED**\n\nError: {str(e)}"
