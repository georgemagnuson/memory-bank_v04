"""
Filename: registry_integration.py
Generated: 2025-08-02.1721
Purpose: Main integration file for centralized context registry system
        Provides drop-in replacements for existing Memory Bank tools
"""

import os
import sys
from typing import Dict, Any, Optional

# Import all enhanced components
from context_registry import (
    ProjectContext,
    ContextRegistry,
    get_global_registry,
    has_active_context,
    get_active_database_path,
    get_active_project_name
)

from enhanced_project_manager import enhanced_work_on_project
from enhanced_context_tools import (
    enhanced_get_current_context,
    enhanced_save_info,
    enhanced_search_info,
    enhanced_save_document,
    enhanced_search_documents
)


class RegistryIntegration:
    """
    Main integration class that provides unified interface
    for all registry-enhanced Memory Bank operations
    """
    
    def __init__(self):
        self.registry = get_global_registry()
    
    def work_on_project(self, project_path: str) -> str:
        """
        Enhanced work_on_project that integrates with context registry
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Formatted status message
        """
        result = enhanced_work_on_project(project_path)
        
        if result["success"]:
            context = result["context"]
            migration_note = ""
            if result.get("migration_performed"):
                migration_note = "\n🔄 **Database Migration:** Successfully upgraded to v2.0"
            
            return f"""✅ **Working on Project: {context['project_name']}**

📁 **Project Path:** {context['project_path']}
💾 **Database:** {context['database_path']}

✅ Database is current ({context['database_version']}, version {context.get('version', 'unknown')})
📊 Database: context.db
📋 Tables: {context['table_count']}
📄 Documents: {context['document_count']} records{migration_note}

🛠️  **Tools Initialized:**
• Core Tools: ✅ Ready for content operations
• SQL Tools: ✅ Ready for database queries  
• Project Tools: ✅ Ready for project management
• Content Tools: ✅ Ready for document management
• Migration Tools: ✅ Ready for schema operations
• Backup Tools: ✅ Ready for data protection

🚀 **Memory Bank v2.0 Ready!** You can now use all Memory Bank tools for this project.

💡 **Quick Start:**
• `get_current_context()` - Check project status
• `save_info("content", "category")` - Save information  
• `search_info("query")` - Find saved content
• `execute_sql("SELECT * FROM documents LIMIT 5")` - Query database"""
        else:
            return f"""❌ **Error Working on Project**

{result['message']}

**Error Details:** {result.get('error', 'Unknown error')}

💡 **Troubleshooting:**
• Ensure the project path exists and is writable
• Check that the database file is not corrupted
• Verify sufficient disk space for database operations"""
    
    def get_current_context(self) -> str:
        """
        Enhanced get_current_context that uses registry
        
        Returns:
            Formatted context information or error message
        """
        result = enhanced_get_current_context()
        
        if result["success"]:
            context = result["context"]
            return f"""✅ **Current Project Context**

📝 **Project:** {context['project_name']}
📁 **Path:** {context['project_path']}
💾 **Database:** {context['database_path']}

📊 **Database Info:**
• Version: {context['database_version']}
• Tables: {context['table_count']}
• Documents: {context['document_count']}
• Initialized: {context['initialized_at']}

🔧 **Status:** {'✅ Valid' if context['is_valid'] else '❌ Invalid'}

**Database Path:** {context['database_path']}"""
        else:
            return result["message"]
    
    def save_info(self, content: str, category: str = "general", tags: str = "") -> str:
        """
        Enhanced save_info that uses registry
        
        Args:
            content: Content to save
            category: Category for organization
            tags: Tags for searching
            
        Returns:
            Formatted save result message
        """
        result = enhanced_save_info(content, category, tags)
        
        if result["success"]:
            return f"""✅ **Information Saved Successfully**

📝 **Project:** {get_active_project_name()}
📂 **Category:** {result['category']}
📄 **Content Length:** {result['content_length']} characters
💾 **Database:** {result['database_path']}

**Content Preview:** {content[:100]}{'...' if len(content) > 100 else ''}"""
        else:
            return result["message"]


# Global integration instance
_integration = RegistryIntegration()


# Drop-in replacement functions for existing Memory Bank tools
def work_on_project(project_path: str) -> str:
    """Drop-in replacement for work_on_project with registry integration"""
    return _integration.work_on_project(project_path)


def get_current_context() -> str:
    """Drop-in replacement for get_current_context with registry integration"""
    return _integration.get_current_context()


def save_info(content: str, category: str = "general", tags: str = "") -> str:
    """Drop-in replacement for save_info with registry integration"""
    return _integration.save_info(content, category, tags)


def get_registry_status() -> str:
    """New function to check registry status and debug context issues"""
    if has_active_context():
        registry = get_global_registry()
        context_info = registry.get_context_info()
        context = registry.get_active_context()
        
        return f"""✅ **Context Registry Status**

🔧 **Registry:** Active with valid context
📝 **Project:** {context_info['project_name']}
📁 **Path:** {context_info['project_path']}
💾 **Database:** {context_info['database_path']}

📊 **Context Details:**
• Database Version: {context_info['database_version']}
• Table Count: {context_info['table_count']}
• Document Count: {context_info['document_count']}
• Initialized: {context_info['initialized_at']}
• Context Valid: {'✅ Yes' if context_info['is_valid'] else '❌ No'}

🔍 **Database Connection Info:**
• Size: {context.connection_info.get('database_size', 'unknown')} bytes
• Readable: {'✅' if context.connection_info.get('readable') else '❌'}
• Writable: {'✅' if context.connection_info.get('writable') else '❌'}"""
    else:
        return """❌ **Context Registry Status**

🔧 **Registry:** No active context
📝 **Project:** None
💡 **Action:** Use work_on_project() to initialize a project context

**Available Commands:**
• work_on_project("/path/to/project") - Initialize project context
• get_registry_status() - Check registry status"""


def validate_registry_integration() -> Dict[str, Any]:
    """
    Validate that the registry integration is working correctly
    
    Returns:
        Dict with validation results
    """
    validation_results = {
        "registry_accessible": False,
        "context_active": False,
        "context_valid": False,
        "database_accessible": False,
        "integration_working": False
    }
    
    try:
        # Test registry access
        registry = get_global_registry()
        validation_results["registry_accessible"] = True
        
        # Test context status
        if has_active_context():
            validation_results["context_active"] = True
            
            context = registry.get_active_context()
            if context and context.is_valid():
                validation_results["context_valid"] = True
                
                # Test database access
                if os.path.exists(context.database_path) and os.access(context.database_path, os.R_OK):
                    validation_results["database_accessible"] = True
        
        # Overall integration status
        validation_results["integration_working"] = all([
            validation_results["registry_accessible"],
            validation_results["context_active"],
            validation_results["context_valid"],
            validation_results["database_accessible"]
        ])
        
    except Exception as e:
        validation_results["error"] = str(e)
    
    return validation_results


def debug_context_propagation() -> str:
    """
    Debug context propagation issues
    
    Returns:
        Formatted debug information
    """
    validation = validate_registry_integration()
    
    debug_info = f"""🔧 **Context Propagation Debug**

**Registry Integration Status:**
• Registry Accessible: {'✅' if validation['registry_accessible'] else '❌'}
• Context Active: {'✅' if validation['context_active'] else '❌'}
• Context Valid: {'✅' if validation['context_valid'] else '❌'}
• Database Accessible: {'✅' if validation['database_accessible'] else '❌'}
• Integration Working: {'✅' if validation['integration_working'] else '❌'}

**Current State:**
• Active Project: {get_active_project_name() or 'None'}
• Database Path: {get_active_database_path() or 'None'}
• Has Context: {'✅' if has_active_context() else '❌'}

**Next Steps:**
"""
    
    if not validation["registry_accessible"]:
        debug_info += "• ❌ Registry not accessible - check module imports\n"
    elif not validation["context_active"]:
        debug_info += "• ❌ No active context - run work_on_project() first\n"
    elif not validation["context_valid"]:
        debug_info += "• ❌ Context invalid - check project path and database\n"
    elif not validation["database_accessible"]:
        debug_info += "• ❌ Database not accessible - check file permissions\n"
    else:
        debug_info += "• ✅ All systems operational!\n"
    
    if "error" in validation:
        debug_info += f"• ⚠️  Error: {validation['error']}\n"
    
    return debug_info
