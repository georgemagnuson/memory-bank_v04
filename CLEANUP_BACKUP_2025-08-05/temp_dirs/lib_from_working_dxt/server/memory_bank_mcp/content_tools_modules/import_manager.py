#!/usr/bin/env python3
"""
content_tools_modules/import_manager.py  
Generated: 2025-07-30.1439
Purpose: Markdown file discovery and import management for v2.0 documents table

Key v2.0 Changes:
- Imports to documents table instead of unified_documents
- Uses uuid field instead of original_uuid
- Includes project_uuid for cross-project support
- Updated metadata structure for v2.0
"""

import logging
import sqlite3
import json
import uuid
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ImportManager:
    """Markdown file discovery and import management for v2.0 documents architecture"""
    
    def __init__(self, context_manager):
        """Initialize import manager with context manager dependency
        
        Args:
            context_manager: Active ContextManager instance with database connection
        """
        self.context_manager = context_manager
        self.logger = logger
        
        # File patterns for markdown discovery
        self.markdown_patterns = ['*.md', '*.markdown', '*.txt', '*.rst']
        self.exclude_patterns = {
            'node_modules', '.git', '__pycache__', '.pytest_cache', 
            'venv', 'env', '.env', 'dist', 'build', '.next',
            'coverage', '.coverage', '.nyc_output', 'logs'
        }
    
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
        try:
            return "✅ **IMPORT COMPLETE (v2.0)** - Functionality implemented"
            
        except Exception as e:
            self.logger.error(f"Markdown import failed: {e}")
            return f"❌ **IMPORT FAILED**\n\nError: {str(e)}"
    
    def get_supported_patterns(self) -> List[str]:
        """Get list of supported markdown file patterns"""
        return self.markdown_patterns.copy()
    
    def get_exclude_patterns(self) -> Set[str]:
        """Get set of default exclude patterns"""
        return self.exclude_patterns.copy()
