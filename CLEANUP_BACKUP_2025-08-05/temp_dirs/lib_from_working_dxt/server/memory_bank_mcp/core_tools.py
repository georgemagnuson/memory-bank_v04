#!/usr/bin/env python3
"""
core_tools.py
Generated: 2025-07-30.1439
Purpose: Core database operations and content extraction tools for v2.0 documents table architecture

v2.0 CLEAN VERSION (No Backward Compatibility):
- Uses documents table exclusively  
- Modular architecture with core_tools_modules/
- Uses uuid field and project_uuid throughout
- Updated FTS table references (documents_fts only)

Modular Components:
- ContentSearchEngine: Enhanced search for v2.0 documents table
- ContentExtractor: Content extraction tools for v2.0 architecture
- DatabaseInterface: Core database operations for v2.0
"""

import logging
from typing import Dict, List, Optional, Any

# Import modular components for v2.0 architecture (DXT compatible)
from .core_tools_modules import ContentSearchEngine, ContentExtractor, DatabaseInterface

logger = logging.getLogger(__name__)

class CoreTools:
    """Core database operations and content tools for v2.0 documents table architecture"""
    
    def __init__(self, context_manager):
        """Initialize CoreTools with v2.0 modular architecture
        
        Args:
            context_manager: Active ContextManager instance with database connection
        """
        self.context_manager = context_manager
        self.logger = logger
        
        # Initialize modular components
        self.search_engine = ContentSearchEngine(context_manager)
        self.extractor = ContentExtractor(context_manager)
        self.database = DatabaseInterface(context_manager)
    
    # =============================================================================
    # PRIMARY SEARCH INTERFACE (v2.0)
    # =============================================================================
    
    async def search_content(self, title_search=None, uuid_search=None, document_type="auto", 
                           project_uuid=None):
        """Search for content in v2.0 documents table with priority ordering
        
        Args:
            title_search: Title/summary to search for (fuzzy matching)
            uuid_search: Specific UUID to find (exact match)
            document_type: Specific document type to search, or "auto" for all types
            project_uuid: Optional project UUID for cross-project search
            
        Returns:
            Dict with content data or None if not found
        """
        return await self.search_engine.search_content(
            title_search=title_search,
            uuid_search=uuid_search,
            document_type=document_type,
            project_uuid=project_uuid
        )
    
    # =============================================================================
    # CONTENT EXTRACTION INTERFACE (v2.0)
    # =============================================================================
    
    async def extract_large_document(self, title_search, output_dir="/tmp"):
        """Extract content from v2.0 documents table to temporary files
        
        Args:
            title_search: Search query to find content (title, UUID, or FTS query)
            output_dir: Directory to write extracted files (default: /tmp)
            
        Returns:
            Dict with extraction results and file paths
        """
        return await self.extractor.extract_content_to_temp(title_search, output_dir)
    
    # =============================================================================
    # DATABASE INTERFACE (v2.0)
    # =============================================================================
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics for v2.0 architecture
        
        Returns:
            Dictionary with detailed database statistics
        """
        return await self.database.get_database_stats()
    
    async def get_project_info(self) -> Dict[str, Any]:
        """Get detailed project information from v2.0 architecture
        
        Returns:
            Dictionary with project details
        """
        return await self.database.get_project_info()
    
    async def check_database_health(self) -> Dict[str, Any]:
        """Check v2.0 database health and integrity
        
        Returns:
            Dictionary with health check results
        """
        return await self.database.check_database_health()
    
    # =============================================================================
    # UTILITY AND INFORMATION METHODS
    # =============================================================================
    
    def get_supported_document_types(self) -> List[str]:
        """Get list of supported document types for v2.0 architecture"""
        return self.search_engine.get_supported_document_types()
    
    def get_priority_order(self) -> List[Dict[str, Any]]:
        """Get document type priority order for search results"""
        return self.search_engine.get_priority_order()
    
    def get_supported_operations(self) -> List[str]:
        """Get list of supported database operations"""
        return self.database.get_supported_operations()
    
    # =============================================================================
    # SYSTEM STATUS AND DIAGNOSTICS
    # =============================================================================
    
    # =============================================================================
    # CONTEXT MANAGEMENT METHODS
    # =============================================================================
    
    async def create_context(self, project_name: str) -> str:
        """Create a new project context
        
        Args:
            project_name: Name of the new project
            
        Returns:
            Success message or error details
        """
        try:
            # Check if context already exists
            existing_contexts = await self.list_contexts()
            if project_name.lower() in [ctx.lower() for ctx in existing_contexts if isinstance(existing_contexts, list)]:
                return f"⚠️ Project '{project_name}' already exists. Use switch_context to work on it."
            
            # Create new context using context manager
            result = await self.context_manager.create_new_context(project_name)
            if result:
                return f"✅ Created new project context: '{project_name}'"
            else:
                return f"❌ Failed to create project context: '{project_name}'"
                
        except Exception as e:
            self.logger.error(f"Create context failed: {e}")
            return f"❌ Error creating context '{project_name}': {str(e)}"
    
    async def switch_context(self, project_name: str) -> str:
        """Switch to an existing project context
        
        Args:
            project_name: Name of the project to switch to
            
        Returns:
            Success message or error details
        """
        try:
            # Switch context using context manager
            result = await self.context_manager.switch_to_context(project_name)
            if result:
                return f"✅ Switched to project: '{project_name}'"
            else:
                return f"❌ Project '{project_name}' not found. Use create_context to create it."
                
        except Exception as e:
            self.logger.error(f"Switch context failed: {e}")
            return f"❌ Error switching to context '{project_name}': {str(e)}"
    
    async def list_contexts(self) -> str:
        """List all available project contexts
        
        Returns:
            Formatted list of contexts or error message
        """
        try:
            contexts = await self.context_manager.get_available_contexts()
            if not contexts:
                return "📋 No project contexts found. Use create_context to create your first project."
            
            context_list = []
            current_context = getattr(self.context_manager, 'current_project', None)
            
            for context in contexts:
                indicator = "👉" if context == current_context else "📁"
                context_list.append(f"{indicator} {context}")
            
            return f"📋 **Available Projects:**\n\n" + "\n".join(context_list)
            
        except Exception as e:
            self.logger.error(f"List contexts failed: {e}")
            return f"❌ Error listing contexts: {str(e)}"
    
    async def get_current_context(self) -> str:
        """Get current project context information
        
        Returns:
            Current context details or error message
        """
        try:
            current_project = getattr(self.context_manager, 'current_project', None)
            if not current_project:
                return "❌ No active project. Use create_context or switch_context to start working."
            
            # Get context stats
            db_stats = await self.database.get_database_stats()
            
            return f"""📊 **Current Project: {current_project}**

📈 **Statistics:**
- Documents: {db_stats.get('document_count', 0)}
- Database: {db_stats.get('database_size', 'Unknown')}
- Status: {'✅ Active' if db_stats.get('success') else '❌ Error'}

Use save_info() to add content or search_info() to find existing content."""
            
        except Exception as e:
            self.logger.error(f"Get current context failed: {e}")
            return f"❌ Error getting current context: {str(e)}"
    
    async def save_info(self, content: str, category: str = "general", tags: str = "") -> str:
        """Save information to current context
        
        Args:
            content: Information to save
            category: Category for organization (default: "general")
            tags: Comma-separated tags
            
        Returns:
            Success message or error details
        """
        try:
            if not self.context_manager.current_project:
                return "❌ No active project. Use create_context or switch_context first."
            
            # Save using database interface
            result = await self.database.save_document(
                title=f"{category.title()} Info",
                content=content,
                doc_type=category,
                tags=tags
            )
            
            if result.get('success'):
                return f"✅ Saved information to '{self.context_manager.current_project}' project"
            else:
                return f"❌ Failed to save information: {result.get('error', 'Unknown error')}"
                
        except Exception as e:
            self.logger.error(f"Save info failed: {e}")
            return f"❌ Error saving information: {str(e)}"
    
    async def search_info(self, query: str, limit: int = 10) -> str:
        """Search saved information
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            Search results or error message
        """
        try:
            if not self.context_manager.current_project:
                return "❌ No active project. Use create_context or switch_context first."
            
            # Search using search engine
            results = await self.search_engine.search_documents(query, limit=limit)
            
            if not results:
                return f"🔍 No results found for '{query}' in current project."
            
            # Format results
            result_lines = [f"🔍 **Search Results for '{query}':**\n"]
            
            for i, result in enumerate(results[:limit], 1):
                title = result.get('title', 'Untitled')
                content_preview = result.get('content', '')[:100] + "..." if len(result.get('content', '')) > 100 else result.get('content', '')
                result_lines.append(f"{i}. **{title}**\n   {content_preview}\n")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            self.logger.error(f"Search info failed: {e}")
            return f"❌ Error searching information: {str(e)}"

    async def get_core_tools_status(self) -> str:
        """Get comprehensive status of core tools v2.0 system
        
        Returns:
            Detailed status report of all core tools components
        """
        try:
            if not self.context_manager or not self.context_manager.database_path:
                return "❌ **CORE TOOLS STATUS FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            # Get project UUID
            project_uuid = getattr(self.context_manager, 'project_uuid', None)
            
            # Get database stats
            db_stats = await self.database.get_database_stats()
            
            # Get document type icons from search engine
            priority_order = self.search_engine.get_priority_order()
            
            # Format status report
            status_lines = [
                "📊 **CORE TOOLS v2.0 STATUS**",
                "",
                f"**Project:** {project_uuid[:8] if project_uuid else 'Unknown'}...",
                "",
                "**v2.0 Architecture:**",
                "- Primary Table: `documents`",
                "- UUID Field: `uuid` (not original_uuid)",
                "- Cross-Project: `project_uuid` support",
                "- FTS Table: `documents_fts`",
                "",
                f"**Document Type Priority Order:**"
            ]
            
            for i, type_info in enumerate(priority_order, 1):
                status_lines.append(f"{i}. {type_info['icon']} **{type_info['type']}** (priority {type_info['priority']})")
            
            status_lines.extend([
                "",
                "**v2.0 Modular Components:**",
                "- ✅ ContentSearchEngine (documents table with priority ordering)",
                "- ✅ ContentExtractor (enhanced metadata extraction)",
                "- ✅ DatabaseInterface (comprehensive health checks)",
                "",
                "**Available Operations:**",
                "- `search_content()` - Advanced search with priority ordering",
                "- `extract_large_document()` - Content extraction with v2.0 metadata",
                "- `get_database_stats()` - Comprehensive database analytics",
                "- `check_database_health()` - Database integrity verification",
                "",
                "**Database Status:**"
            ])
            
            if db_stats.get('success'):
                status_lines.append(f"✅ Database connection active")
            else:
                status_lines.append(f"❌ Database connection failed: {db_stats.get('error', 'Unknown error')}")
            
            return "\n".join(status_lines)
            
        except Exception as e:
            self.logger.error(f"Core tools status failed: {e}")
            return f"❌ **CORE TOOLS STATUS FAILED**\n\nError: {str(e)}"
