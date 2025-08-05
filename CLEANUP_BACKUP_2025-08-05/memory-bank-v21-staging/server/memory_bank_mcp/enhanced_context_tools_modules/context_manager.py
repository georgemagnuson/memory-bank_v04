#!/usr/bin/env python3
"""
Filename: enhanced_context_tools_modules/context_manager.py
Generated: 2025-08-03.1749
Purpose: Enhanced context management tools using centralized context registry

This module provides context validation, project management, and registry integration
for the Memory Bank v2.0 Enhanced system.
"""

from typing import Optional, Dict, Any


class EnhancedContextTools:
    """
    Enhanced context tools that use the centralized context registry
    Provides registry-aware implementations of core context operations
    """
    
    def __init__(self):
        # Import registry functions with the same pattern as main.py (working)
        from context_registry import (
            get_global_registry, 
            has_active_context,
            get_active_project_name,
            get_active_database_path
        )
        
        self.registry = get_global_registry()
        self.has_active_context = has_active_context
        self.get_active_project_name = get_active_project_name
        self.get_active_database_path = get_active_database_path
    
    def get_current_context(self) -> Dict[str, Any]:
        """
        Get current project context information from registry
        
        Returns:
            Dict with context information or error message
        """
        if not self.has_active_context():
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
        if not self.has_active_context():
            return False, "No active project context. Use work_on_project() first."
        
        context = self.registry.get_active_context()
        if not context.is_valid():
            return False, f"Project context for '{context.project_name}' is no longer valid."
        
        return True, f"Context valid for project '{context.project_name}'"
    
    def get_database_path(self) -> Optional[str]:
        """Get the database path from active context"""
        return self.get_active_database_path()
    
    def get_project_name(self) -> Optional[str]:
        """Get the project name from active context"""
        return self.get_active_project_name()
    
    def refresh_context(self) -> Dict[str, Any]:
        """
        Refresh the active context with updated information
        
        Returns:
            Dict with refresh results
        """
        if not self.has_active_context():
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
