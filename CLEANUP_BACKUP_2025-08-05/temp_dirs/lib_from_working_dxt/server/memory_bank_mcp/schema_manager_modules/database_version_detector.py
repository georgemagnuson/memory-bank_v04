#!/usr/bin/env python3
"""
server/memory_bank_mcp/database_version_detector.py
Generated: 2025-07-29.0125
Purpose: Database version detection and schema analysis for Memory Bank v2.0

Handles:
- Version detection using PRAGMA user_version and schema introspection
- Comprehensive schema information gathering
- Database compatibility analysis
"""

import logging
from typing import Dict
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass  
class SchemaInfo:
    """Database schema information"""
    version: int
    table_count: int
    has_unified_tables: bool
    has_clean_tables: bool
    record_counts: Dict[str, int]
    database_path: str

class DatabaseVersionDetector:
    """Handles database version detection and validation"""
    
    @staticmethod
    async def detect_version(context_manager) -> int:
        """
        Detect database version using multiple methods
        
        Args:
            context_manager: Active context manager with database connection
            
        Returns:
            int: Database version (0=legacy, 4=v2.0, -1=empty/new)
        """
        try:
            if not context_manager.is_initialized():
                logger.warning("Context manager not initialized")
                return -1
            
            # Use direct SQLite connection instead of get_cursor()
            import sqlite3
            conn = sqlite3.connect(context_manager.database_path)
            cursor = conn.cursor()
            
            try:
                # Method 1: Check PRAGMA user_version (most reliable)
                cursor.execute('PRAGMA user_version')
                version = cursor.fetchone()[0]
                
                if version > 0:
                    logger.info(f"Database version detected via PRAGMA: {version}")
                    return version
                
                # Method 2: Schema introspection fallback  
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('unified_documents', 'documents')")
                tables = [row[0] for row in cursor.fetchall()]
                
                if 'documents' in tables:
                    logger.info("v2.0 schema detected (documents table present)")
                    # Update version if not set
                    cursor.execute('PRAGMA user_version = 4')
                    conn.commit()
                    return 4
                elif 'unified_documents' in tables:
                    logger.info("v1.4.0 schema detected (unified_documents table present)")
                    return 0
                else:
                    logger.info("Empty or unrecognized database schema")
                    return -1
                    
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"Version detection failed: {e}")
            return -1
            
            if 'documents' in tables and 'unified_documents' not in tables:
                logger.info("Database version detected via schema: v2.0 (clean tables)")
                return 4
            elif 'unified_documents' in tables:
                logger.info("Database version detected via schema: legacy (unified tables)")
                return 0
            else:
                logger.info("Database version detected: empty/new database")
                return -1
                
        except Exception as e:
            logger.error(f"Version detection failed: {e}")
            return -1
    
    @staticmethod
    async def get_schema_info(context_manager) -> SchemaInfo:
        """Get comprehensive schema information"""
        try:
            if not context_manager.is_initialized():
                return SchemaInfo(version=-1, table_count=0, has_unified_tables=False, 
                                has_clean_tables=False, record_counts={}, database_path="")
            
            # Use direct SQLite connection instead of get_cursor()
            import sqlite3
            conn = sqlite3.connect(context_manager.database_path)
            cursor = conn.cursor()
            
            try:
                # Get version
                version = await DatabaseVersionDetector.detect_version(context_manager)
                
                # Count tables
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                # Check table naming patterns
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                all_tables = [row[0] for row in cursor.fetchall()]
                
                has_unified = any('unified' in table for table in all_tables)
                has_clean = 'documents' in all_tables
                
                # Get record counts for key tables
                record_counts = {}
                for table in ['unified_documents', 'documents', 'discussions', 'artifacts']:
                    if table in all_tables:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        record_counts[table] = cursor.fetchone()[0]
                    else:
                        record_counts[table] = 0
                
                return SchemaInfo(
                    version=version,
                    table_count=table_count,
                    has_unified_tables=has_unified,
                    has_clean_tables=has_clean,
                    record_counts=record_counts,
                    database_path=context_manager.database_path
                )
                
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"Schema info collection failed: {e}")
            return SchemaInfo(version=-1, table_count=0, has_unified_tables=False, 
                            has_clean_tables=False, record_counts={}, database_path="")

    @staticmethod
    async def is_migration_needed(context_manager) -> bool:
        """
        Check if database migration is needed
        
        Returns:
            bool: True if migration from v1.4.0 to v2.0 is needed
        """
        try:
            version = await DatabaseVersionDetector.detect_version(context_manager)
            return version == 0  # Legacy version needs migration
        except Exception as e:
            logger.error(f"Migration check failed: {e}")
            return False
    
    @staticmethod
    async def is_v2_compatible(context_manager) -> bool:
        """
        Check if database is v2.0 compatible
        
        Returns:
            bool: True if database is v2.0 or can be migrated
        """
        try:
            version = await DatabaseVersionDetector.detect_version(context_manager)
            return version in [0, 4]  # Legacy (can migrate) or v2.0 (already compatible)
        except Exception as e:
            logger.error(f"Compatibility check failed: {e}")
            return False

# Export classes and dataclasses
__all__ = ['DatabaseVersionDetector', 'SchemaInfo']
