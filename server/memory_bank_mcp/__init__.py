# memory_bank_mcp/__init__.py
# Generated: 2025-07-13.1843
# Purpose: Memory Bank MCP v2 Package Initialization
# Enhanced AI collaboration memory system with persistent database storage

"""
Memory Bank MCP v2 - Enhanced AI Collaboration Memory System

A next-generation Model Context Protocol (MCP) server that provides persistent,
project-specific AI memory with cross-project intelligence capabilities.

Key Features:
- Project-specific SQLite databases with UUID-based cross-referencing
- Comprehensive memory storage (discussions, code iterations, artifacts, sessions)
- Automatic context saving after every exchange
- Session continuity across chat restarts
- Multi-browser project isolation with cross-project pattern referencing

Usage:
    python -m memory_bank_mcp --project_path /path/to/project --mode stdio
"""

__version__ = "2.0.0"
__author__ = "Memory Bank MCP v2"
__license__ = "MIT"

# Import core components
from .database import MemoryBankDatabase
from .context_manager import ContextManager
from .project_manager import ProjectManager

__all__ = [
    'MemoryBankDatabase',
    'ContextManager',
    'ProjectManager'
]
