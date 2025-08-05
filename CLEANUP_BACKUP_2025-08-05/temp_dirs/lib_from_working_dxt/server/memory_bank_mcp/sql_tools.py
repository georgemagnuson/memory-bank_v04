#!/usr/bin/env python3
"""
sql_tools.py
Generated: 2025-08-02.2303 (Registry Integration Rewrite)
Purpose: Registry-native SQL query execution with v2.0 documents table architecture

REGISTRY INTEGRATION REWRITE:
- Works directly with registry system (no legacy context_manager dependency)
- Optimized for v2.0 documents table with composite primary keys
- Uses existing sql_tools_modules (QueryAnalyzer, TruncationManager, QueryExecutor)
- Proper async/await handling for MCP server
- Direct database access through registry context

v2.0 FEATURES:
- Composite key awareness: (project_uuid, uuid, version)
- Document versioning support
- Project-aware query execution
- Cross-project query capabilities
- Performance optimized for new indexes
"""

import logging
import sqlite3
from typing import Optional, Dict, Any, List
from pathlib import Path

logger = logging.getLogger(__name__)

class RegistryCompatibleQueryExecutor:
    """Registry-compatible version of QueryExecutor that gets database path from registry"""
    
    def __init__(self):
        """Initialize query executor for registry system"""
        self.logger = logger
    
    def get_database_path(self) -> Optional[str]:
        """Get database path from registry system"""
        try:
            # Import registry functions with fallback pattern
            try:
                from memory_bank_mcp.context_registry import has_active_context, get_active_database_path
            except ImportError:
                try:
                    from .context_registry import has_active_context, get_active_database_path
                except ImportError:
                    from context_registry import has_active_context, get_active_database_path
            
            if has_active_context():
                return get_active_database_path()
            else:
                self.logger.error("No active registry context")
                return None
        except Exception as e:
            self.logger.error(f"Failed to get database path from registry: {e}")
            return None
    
    async def execute_query(self, query: str, params: Optional[List[Any]] = None) -> List[Dict[str, Any]]:
        """Execute SQL query using registry database connection
        
        Args:
            query: SQL query to execute
            params: Optional query parameters
            
        Returns:
            List of dictionaries representing query results
        """
        database_path = self.get_database_path()
        if not database_path:
            raise Exception("No active database connection - use work_on_project() first")
        
        # Verify database file exists
        if not Path(database_path).exists():
            raise Exception(f"Database file not found: {database_path}")
        
        # Connect directly to SQLite for v2.0 queries
        conn = sqlite3.connect(database_path)
        conn.row_factory = sqlite3.Row  # Enable column name access
        cursor = conn.cursor()
        
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Fetch results
            results = cursor.fetchall()
            
            # Convert to list of dictionaries for better compatibility
            result_dicts = [dict(row) for row in results]
            
            self.logger.info(f"Query executed successfully, returned {len(result_dicts)} rows")
            return result_dicts
            
        except sqlite3.Error as e:
            error_msg = f"SQL execution error: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
        finally:
            cursor.close()
            conn.close()
    
    def validate_query_safety(self, query: str) -> Dict[str, Any]:
        """Validate query safety for v2.0 schema
        
        Args:
            query: SQL query to validate
            
        Returns:
            Dict with validation results
        """
        query_lower = query.lower().strip()
        
        # Allow common read operations
        safe_operations = ['select', 'with', 'explain']
        is_safe = any(query_lower.startswith(op) for op in safe_operations)
        
        # Check for dangerous operations
        dangerous_patterns = ['drop', 'delete', 'update', 'insert', 'alter', 'create']
        has_dangerous = any(pattern in query_lower for pattern in dangerous_patterns)
        
        # Special case: allow CREATE TEMP TABLE for complex queries
        if 'create temp' in query_lower or 'create temporary' in query_lower:
            has_dangerous = False
            is_safe = True
        
        return {
            'is_safe': is_safe and not has_dangerous,
            'dangerous_operations': [op for op in dangerous_patterns if op in query_lower],
            'query_type': 'read' if is_safe and not has_dangerous else 'write'
        }


class SQLTools:
    """Registry-native SQL query execution with v2.0 smart truncation and analysis system"""
    
    def __init__(self, context_manager=None):
        """Initialize SQLTools with registry integration
        
        Args:
            context_manager: Optional, kept for compatibility but not used
        """
        # Note: context_manager parameter kept for compatibility but ignored
        # This class works directly with the registry system
        self.logger = logger
        
        # Import and initialize modular components for v2.0 architecture
        try:
            try:
                from memory_bank_mcp.sql_tools_modules import QueryAnalyzer, TruncationManager
            except ImportError:
                try:
                    from .sql_tools_modules import QueryAnalyzer, TruncationManager
                except ImportError:
                    from sql_tools_modules import QueryAnalyzer, TruncationManager
            
            self.query_analyzer = QueryAnalyzer()
            self.truncation_manager = TruncationManager()
        except ImportError as e:
            self.logger.error(f"Failed to import sql_tools_modules: {e}")
            # Create minimal fallback implementations
            self.query_analyzer = self._create_fallback_analyzer()
            self.truncation_manager = self._create_fallback_truncation()
        
        # Use registry-compatible query executor
        self.query_executor = RegistryCompatibleQueryExecutor()
        
        self.logger.info("SQLTools initialized with registry integration")
    
    def _create_fallback_analyzer(self):
        """Create fallback query analyzer if module import fails"""
        class FallbackAnalyzer:
            def analyze_query_intent(self, query):
                return {
                    'strategy': 'standard',
                    'limit': 5000,
                    'reason': 'Fallback analyzer (modules not available)'
                }
        return FallbackAnalyzer()
    
    def _create_fallback_truncation(self):
        """Create fallback truncation manager if module import fails"""
        class FallbackTruncation:
            def truncate_content(self, content, max_length):
                if len(content) <= max_length:
                    return content
                return content[:max_length] + "... [truncated]"
        return FallbackTruncation()
    
    # =============================================================================
    # PRIMARY SQL INTERFACE (v2.0 Registry Integration)
    # =============================================================================
    
    async def execute_sql(self, query: str) -> str:
        """Execute SQL query (main.py interface compatibility)"""
        return await self.memory_bank_sql_query(query)
    
    async def memory_bank_sql_query(self, query: str, max_content_length: Optional[int] = None) -> str:
        """Execute SQL query with smart context-aware truncation for v2.0 architecture
        
        Args:
            query: SQL query to execute
            max_content_length: Override truncation limit (None = smart detection)
            
        Returns:
            Formatted query results with truncation applied
        """
        try:
            # Check if registry context is active
            try:
                from memory_bank_mcp.context_registry import has_active_context
            except ImportError:
                try:
                    from .context_registry import has_active_context
                except ImportError:
                    from context_registry import has_active_context
            
            if not has_active_context():
                return "❌ **SQL QUERY FAILED**\n\nMemory Bank not initialized. Use `work_on_project()` to start."
            
            # Smart query analysis with v2.0 awareness
            intent_analysis = self.query_analyzer.analyze_query_intent(query)
            
            # Determine effective truncation limit
            if max_content_length is not None:
                effective_limit = max_content_length
                truncation_reason = f"User specified: {max_content_length} chars"
            else:
                effective_limit = intent_analysis['limit']
                truncation_reason = intent_analysis['reason']
            
            # Validate query for v2.0 compatibility
            validation = self.query_executor.validate_query_safety(query)
            
            if not validation['is_safe']:
                return f"❌ **SQL QUERY REJECTED**\n\nUnsafe operations detected: {', '.join(validation['dangerous_operations'])}\nOnly SELECT queries are allowed for safety."
            
            # Execute query
            self.logger.info(f"Executing v2.0 SQL query with {intent_analysis['strategy']} strategy")
            results = await self.query_executor.execute_query(query)
            
            # Format results with v2.0 enhancements
            formatted_result = self._format_query_results(results, query, effective_limit, truncation_reason)
            
            return formatted_result
            
        except Exception as e:
            error_msg = f"SQL query execution failed: {str(e)}"
            self.logger.error(error_msg)
            return f"❌ **SQL QUERY FAILED**\n\n{error_msg}"
    
    def _format_query_results(self, results: List[Dict[str, Any]], query: str, 
                            max_length: int, truncation_reason: str) -> str:
        """Format query results with v2.0 schema awareness and smart truncation"""
        
        if not results:
            return "📊 **SQL Query Results**\n\n*No results found.*"
        
        # Build formatted output
        output_parts = ["📊 **SQL Query Results**\n"]
        
        # Add query info
        output_parts.append(f"**Query:** `{query[:100]}{'...' if len(query) > 100 else ''}`")
        output_parts.append(f"**Results:** {len(results)} row(s)")
        output_parts.append("")
        
        # Format results
        if len(results) == 1 and len(results[0]) == 1:
            # Single value result
            value = list(results[0].values())[0]
            output_parts.append(f"**Result:** {value}")
        else:
            # Table format for multiple results
            if results:
                # Get column names
                columns = list(results[0].keys())
                
                # Format header
                header = " | ".join(columns)
                output_parts.append(header)
                output_parts.append("-" * len(header))
                
                # Format data rows
                for row in results[:20]:  # Limit to 20 rows for readability
                    row_values = []
                    for col in columns:
                        value = row[col]
                        if value is None:
                            row_values.append("NULL")
                        elif isinstance(value, str) and len(value) > 50:
                            # Truncate long text fields
                            row_values.append(value[:47] + "...")
                        else:
                            row_values.append(str(value))
                    output_parts.append(" | ".join(row_values))
                
                if len(results) > 20:
                    output_parts.append(f"... and {len(results) - 20} more rows")
        
        # Join all parts
        formatted_output = "\n".join(output_parts)
        
        # Apply truncation if needed
        if len(formatted_output) > max_length:
            truncated = self.truncation_manager.truncate_content(formatted_output, max_length)
            truncated += f"\n\n*Truncated due to length. Reason: {truncation_reason}*"
            return truncated
        
        return formatted_output
    
    # =============================================================================
    # v2.0 SCHEMA HELPER METHODS
    # =============================================================================
    
    async def show_v2_schema(self) -> str:
        """Show v2.0 database schema with focus on documents table"""
        schema_query = """
        SELECT name, type, sql 
        FROM sqlite_master 
        WHERE type IN ('table', 'index') 
        AND name NOT LIKE 'sqlite_%'
        ORDER BY 
            CASE WHEN name = 'documents' THEN 0 
                 WHEN name = 'projects' THEN 1 
                 ELSE 2 END,
            name
        """
        return await self.memory_bank_sql_query(schema_query)
    
    async def show_document_stats(self) -> str:
        """Show v2.0 document statistics"""
        stats_query = """
        SELECT 
            document_type,
            COUNT(*) as count,
            COUNT(DISTINCT uuid) as unique_docs,
            MAX(version) as max_version
        FROM documents 
        GROUP BY document_type 
        ORDER BY count DESC
        """
        return await self.memory_bank_sql_query(stats_query)
    
    async def show_project_info(self) -> str:
        """Show current project information"""
        try:
            try:
                from memory_bank_mcp.context_registry import get_active_project_name
            except ImportError:
                try:
                    from .context_registry import get_active_project_name
                except ImportError:
                    from context_registry import get_active_project_name
            
            project_name = get_active_project_name()
            
            project_query = """
            SELECT 
                p.uuid as project_uuid,
                p.name as project_name,
                COUNT(d.uuid) as document_count,
                COUNT(DISTINCT d.document_type) as document_types
            FROM projects p
            LEFT JOIN documents d ON p.uuid = d.project_uuid
            WHERE p.name = ?
            GROUP BY p.uuid, p.name
            """
            
            result = await self.query_executor.execute_query(project_query, [project_name])
            if result:
                info = result[0]
                return f"""📋 **Current Project Info**

**Project:** {info['project_name']}
**UUID:** {info['project_uuid']}
**Documents:** {info['document_count']} total
**Document Types:** {info['document_types']} different types"""
            else:
                return "❌ Project information not found"
                
        except Exception as e:
            return f"❌ Error getting project info: {str(e)}"


# =============================================================================
# REGISTRY INTEGRATION FUNCTIONS
# =============================================================================

def create_registry_sql_tools() -> SQLTools:
    """Create SQL tools instance that works with registry system
    
    Returns:
        SQLTools instance configured for registry integration
    """
    return SQLTools()


# Compatibility alias for legacy code
MemoryBankSQLQuery = SQLTools
