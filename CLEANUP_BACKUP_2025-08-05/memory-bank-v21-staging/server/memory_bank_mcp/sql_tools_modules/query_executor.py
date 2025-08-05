#!/usr/bin/env python3
"""
sql_tools_modules/query_executor.py
Generated: 2025-07-30.1848
Purpose: SQL execution engine with v2.0 table references and enhanced error handling

Key v2.0 Features:
- Project-aware query execution
- Enhanced error messages with v2.0 table suggestions
- Result formatting with v2.0 metadata
- Connection management for documents table
"""

import logging
import sqlite3
from typing import List, Any, Dict, Optional

logger = logging.getLogger(__name__)

class QueryExecutor:
    """SQL execution engine with v2.0 enhancements"""
    
    def __init__(self, context_manager):
        """Initialize query executor with context manager
        
        Args:
            context_manager: Active ContextManager instance with database connection
        """
        self.context_manager = context_manager
        self.logger = logger
    
    async def execute_query(self, query: str, params: Optional[List] = None) -> List[Any]:
        """Execute SQL query and return results in simple format
        
        Args:
            query: SQL query to execute
            params: Optional parameters for parameterized queries
            
        Returns:
            List of tuples representing query results
            
        Raises:
            Exception: If query execution fails
        """
        try:
            if not self.context_manager or not self.context_manager.database_path:
                raise Exception("No active database connection")
            
            # Connect directly to SQLite for v2.0 queries
            conn = sqlite3.connect(self.context_manager.database_path)
            conn.row_factory = sqlite3.Row  # Enable column name access
            cursor = conn.cursor()
            
            try:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                # Fetch results
                results = cursor.fetchall()
                
                # Convert to list of tuples for compatibility
                result_tuples = [tuple(row) for row in results]
                
                conn.close()
                return result_tuples
                
            except sqlite3.Error as e:
                conn.close()
                # Enhanced error handling with v2.0 suggestions
                error_msg = str(e)
                enhanced_error = self._enhance_error_message(error_msg, query)
                raise Exception(enhanced_error)
                
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    def _enhance_error_message(self, error_msg: str, query: str) -> str:
        """Enhance error messages with v2.0-specific suggestions"""
        
        enhanced_msg = error_msg
        
        # Common v1.4.0 → v2.0 migration errors
        if "no such table: unified_documents" in error_msg.lower():
            enhanced_msg += "\n💡 v2.0 Update: Use 'documents' table instead of 'unified_documents'"
        
        if "no such column: original_uuid" in error_msg.lower():
            enhanced_msg += "\n💡 v2.0 Update: Use 'uuid' column instead of 'original_uuid'"
        
        if "no such table: unified_documents_fts" in error_msg.lower():
            enhanced_msg += "\n💡 v2.0 Update: Use 'documents_fts' table instead of 'unified_documents_fts'"
        
        # Project UUID suggestions
        if "documents" in query.lower() and "project_uuid" not in query.lower():
            enhanced_msg += "\n💡 v2.0 Best Practice: Consider adding 'project_uuid' filter for better performance"
        
        # Status field suggestions
        if "documents" in query.lower() and "status" not in query.lower():
            enhanced_msg += "\n💡 v2.0 Best Practice: Consider adding 'status = \"active\"' filter"
        
        return enhanced_msg
    
    def get_column_info(self, results: List[Any], cursor_description = None) -> Dict[str, Any]:
        """Get column information from query results
        
        Args:
            results: Query results
            cursor_description: Optional cursor description
            
        Returns:
            Dictionary with column metadata
        """
        if not results:
            return {
                'column_count': 0,
                'row_count': 0,
                'columns': []
            }
        
        # If we have cursor description, use it
        if cursor_description:
            columns = [desc[0] for desc in cursor_description]
        else:
            # Generate generic column names
            columns = [f"col_{i}" for i in range(len(results[0]))]
        
        return {
            'column_count': len(columns),
            'row_count': len(results),
            'columns': columns
        }
    
    def format_results_for_display(self, results: List[Any], columns: List[str]) -> List[Dict[str, Any]]:
        """Format results for structured display
        
        Args:
            results: Raw query results
            columns: Column names
            
        Returns:
            List of dictionaries with column names as keys
        """
        if not results:
            return []
        
        formatted_results = []
        for row in results:
            row_dict = {}
            for i, value in enumerate(row):
                column_name = columns[i] if i < len(columns) else f"col_{i}"
                row_dict[column_name] = value
            formatted_results.append(row_dict)
        
        return formatted_results
    
    def validate_query_safety(self, query: str) -> Dict[str, Any]:
        """Validate query for safety and v2.0 compatibility
        
        Args:
            query: SQL query to validate
            
        Returns:
            Dictionary with validation results
        """
        validation = {
            'is_safe': True,
            'warnings': [],
            'suggestions': [],
            'v2_compatibility': True
        }
        
        query_upper = query.upper().strip()
        
        # Check for dangerous operations
        dangerous_patterns = ['DROP TABLE', 'DELETE FROM', 'UPDATE SET', 'ALTER TABLE']
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                validation['warnings'].append(f"Potentially dangerous operation: {pattern}")
        
        # Check for v2.0 compatibility
        if 'UNIFIED_DOCUMENTS' in query_upper:
            validation['v2_compatibility'] = False
            validation['suggestions'].append("Use 'documents' table instead of 'unified_documents'")
        
        if 'ORIGINAL_UUID' in query_upper:
            validation['v2_compatibility'] = False
            validation['suggestions'].append("Use 'uuid' field instead of 'original_uuid'")
        
        # Performance suggestions
        if 'FROM DOCUMENTS' in query_upper:
            if 'WHERE' not in query_upper:
                validation['suggestions'].append("Consider adding WHERE clause for better performance")
            
            if 'PROJECT_UUID' not in query_upper:
                validation['suggestions'].append("Consider adding project_uuid filter")
        
        return validation
    
    def get_database_info(self) -> Dict[str, Any]:
        """Get information about the current database
        
        Returns:
            Dictionary with database metadata
        """
        try:
            if not self.context_manager or not self.context_manager.database_path:
                return {'error': 'No database connection'}
            
            conn = sqlite3.connect(self.context_manager.database_path)
            cursor = conn.cursor()
            
            # Get basic database info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Check for v2.0 tables
            v2_tables = ['documents', 'documents_fts', 'projects', 'project_context']
            v2_present = [table for table in v2_tables if table in tables]
            
            # Check for v1.4.0 tables
            v1_tables = ['unified_documents', 'unified_documents_fts']
            v1_present = [table for table in v1_tables if table in tables]
            
            conn.close()
            
            return {
                'database_path': str(self.context_manager.database_path),
                'total_tables': len(tables),
                'all_tables': tables,
                'v2_tables_present': v2_present,
                'v1_tables_present': v1_present,
                'architecture_version': 'v2.0' if v2_present else 'v1.4.0' if v1_present else 'unknown'
            }
            
        except Exception as e:
            return {'error': str(e)}
