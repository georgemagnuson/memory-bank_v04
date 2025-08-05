"""
Content Migrator Modules
========================

Modular components for content table migration operations.

Modules:
- table_analyzer: Analyzes table structures and discovers content tables
- query_builder: Builds migration queries based on table structures  
- legacy_cleaner: Handles cleanup of legacy tables
- fts_rebuilder: Manages FTS index rebuilding
"""

from .table_analyzer import TableAnalyzer
from .query_builder import QueryBuilder
from .legacy_cleaner import LegacyCleaner
from .fts_rebuilder import FTSRebuilder

__all__ = [
    'TableAnalyzer',
    'QueryBuilder', 
    'LegacyCleaner',
    'FTSRebuilder'
]
