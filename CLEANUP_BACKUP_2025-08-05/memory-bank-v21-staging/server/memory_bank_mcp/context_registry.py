"""
Filename: context_registry.py
Generated: 2025-08-02.1721
Purpose: Centralized context registry for Memory Bank v2.0 Enhanced
        Provides singleton pattern for sharing active project context across all tool modules
"""

import threading
import sqlite3
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectContext:
    """Complete project context information"""
    project_name: str
    project_path: str
    database_path: str
    database_version: str
    table_count: int
    document_count: int
    connection_info: Dict[str, Any]
    initialized_at: str
    
    def is_valid(self) -> bool:
        """Validate that the context is still usable"""
        return (
            os.path.exists(self.database_path) and
            os.path.exists(self.project_path) and
            os.access(self.database_path, os.R_OK | os.W_OK)
        )


class ContextRegistry:
    """
    Singleton registry for managing active project context
    Ensures all tool modules can access the same project context
    """
    
    _instance: Optional['ContextRegistry'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'ContextRegistry':
        """Ensure singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._active_context = None
                    cls._instance._context_lock = threading.Lock()
        return cls._instance
    
    def register_context(self, context: ProjectContext) -> bool:
        """
        Register a new active project context
        
        Args:
            context: ProjectContext object with complete project information
            
        Returns:
            bool: True if registration successful, False otherwise
        """
        with self._context_lock:
            try:
                # Validate context before registering
                if not context.is_valid():
                    print(f"❌ Context validation failed for {context.project_name}")
                    return False
                
                self._active_context = context
                print(f"✅ Context registered: {context.project_name}")
                return True
                
            except Exception as e:
                print(f"❌ Error registering context: {e}")
                return False
    
    def get_active_context(self) -> Optional[ProjectContext]:
        """
        Get the currently active project context
        
        Returns:
            ProjectContext or None if no active context
        """
        with self._context_lock:
            if self._active_context and self._active_context.is_valid():
                return self._active_context
            elif self._active_context:
                # Context exists but is no longer valid
                print(f"⚠️  Context for {self._active_context.project_name} is no longer valid")
                self._active_context = None
            return None
    
    def clear_context(self) -> None:
        """Clear the active context (used when switching projects)"""
        with self._context_lock:
            if self._active_context:
                print(f"🔄 Clearing context: {self._active_context.project_name}")
            self._active_context = None
    
    def get_context_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the active context
        
        Returns:
            Dict with context details or empty dict if no context
        """
        context = self.get_active_context()
        if not context:
            return {}
        
        return {
            "project_name": context.project_name,
            "project_path": context.project_path,
            "database_path": context.database_path,
            "database_version": context.database_version,
            "table_count": context.table_count,
            "document_count": context.document_count,
            "initialized_at": context.initialized_at,
            "is_valid": context.is_valid()
        }
    
    def refresh_context_stats(self) -> bool:
        """
        Refresh document count and other dynamic stats for active context
        
        Returns:
            bool: True if refresh successful, False otherwise
        """
        context = self.get_active_context()
        if not context:
            return False
        
        try:
            # Update document count from database
            conn = sqlite3.connect(context.database_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM documents")
            context.document_count = cursor.fetchone()[0]
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Error refreshing context stats: {e}")
            return False


# Global registry instance
_global_registry = ContextRegistry()


def get_global_registry() -> ContextRegistry:
    """Get the global context registry instance"""
    return _global_registry


def has_active_context() -> bool:
    """Quick check if there's an active context"""
    return _global_registry.get_active_context() is not None


def get_active_database_path() -> Optional[str]:
    """Get the database path from active context"""
    context = _global_registry.get_active_context()
    return context.database_path if context else None


def get_active_project_name() -> Optional[str]:
    """Get the project name from active context"""
    context = _global_registry.get_active_context()
    return context.project_name if context else None
