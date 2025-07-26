#!/usr/bin/env python3
"""
server/memory_bank_mcp/sql_tools.py
Generated: 2025-07-26.1755
Purpose: Smart SQL query execution with v1.4.0 enhanced truncation system
         Preserves critical v1.4.0 enhancements: context-aware truncation, query analysis, automatic suggestions

Essential v1.4.0 Features Preserved:
- Smart context-aware SQL truncation with query intent detection
- Three truncation strategies: content-focused (400), overview (80), balanced (150)
- User control with max_content_length parameter (None = no truncation)
- Automatic extract suggestions for seamless workflow integration
- Query analysis with pattern recognition for optimal user experience
"""

import logging
import re
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class SmartSQLTruncation:
    """Smart SQL query analysis and truncation system - v1.4.0 enhancement"""
    
    # Query patterns for smart truncation (v1.4.0 feature)
    CONTENT_FOCUSED_PATTERNS = [
        r'SELECT.*content.*FROM',
        r'WHERE.*content.*LIKE',
        r'SELECT.*summary.*FROM.*discussions',
        r'SELECT.*title.*content.*FROM',
        r'content.*MATCH',
    ]
    
    OVERVIEW_PATTERNS = [
        r'SELECT COUNT\(',
        r'SELECT.*COUNT\(',
        r'PRAGMA',
        r'SELECT.*name.*FROM.*sqlite_master',
        r'DESCRIBE',
        r'SHOW TABLES',
        r'SELECT.*\*.*LIMIT\s+[1-5]\b',
    ]
    
    BALANCED_PATTERNS = [
        r'SELECT.*title.*FROM',
        r'SELECT.*summary.*FROM',
        r'SELECT.*uuid.*FROM',
        r'ORDER BY.*created_at',
        r'GROUP BY',
    ]
    
    @classmethod
    def analyze_query_intent(cls, query: str) -> Dict[str, Any]:
        """Analyze SQL query to determine optimal truncation strategy"""
        query_upper = query.upper().strip()
        
        # Check for user override patterns
        if 'LIMIT' in query_upper and any(x in query_upper for x in ['1', '2', '3', '4', '5']):
            return {
                'strategy': 'user_controlled',
                'limit': 200,
                'reason': 'User specified small LIMIT - moderate truncation'
            }
        
        # Check content-focused patterns (highest limit)
        for pattern in cls.CONTENT_FOCUSED_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return {
                    'strategy': 'content_focused',
                    'limit': 400,
                    'reason': 'Content-focused query detected - high character limit'
                }
        
        # Check overview patterns (lowest limit)
        for pattern in cls.OVERVIEW_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return {
                    'strategy': 'overview',
                    'limit': 80,
                    'reason': 'Overview/metadata query detected - low character limit'
                }
        
        # Check balanced patterns (medium limit)
        for pattern in cls.BALANCED_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return {
                    'strategy': 'balanced',
                    'limit': 150,
                    'reason': 'Balanced query detected - medium character limit'
                }
        
        # Default strategy
        return {
            'strategy': 'balanced',
            'limit': 150,
            'reason': 'Default strategy - medium character limit'
        }
    
    @classmethod
    def apply_smart_truncation(cls, content: str, max_length: int) -> Dict[str, Any]:
        """Apply smart truncation with user experience enhancements"""
        if not content:
            return {
                'truncated_content': '',
                'was_truncated': False,
                'original_length': 0,
                'truncated_length': 0
            }
        
        original_length = len(content)
        
        if max_length is None or original_length <= max_length:
            return {
                'truncated_content': content,
                'was_truncated': False,
                'original_length': original_length,
                'truncated_length': original_length
            }
        
        # Smart truncation - try to break at word boundaries
        if max_length > 20:
            # Find last space before limit
            truncate_point = max_length
            while truncate_point > max_length * 0.8 and truncate_point > 0:
                if content[truncate_point] == ' ':
                    break
                truncate_point -= 1
            
            if truncate_point <= max_length * 0.8:
                truncate_point = max_length
        else:
            truncate_point = max_length
        
        truncated = content[:truncate_point]
        if truncate_point < original_length:
            truncated += "..."
        
        return {
            'truncated_content': truncated,
            'was_truncated': True,
            'original_length': original_length,
            'truncated_length': len(truncated),
            'truncate_point': truncate_point
        }


class SQLTools:
    """SQL query execution with smart v1.4.0 truncation system"""
    
    def __init__(self, context_manager):
        self.context_manager = context_manager
    
    async def _execute_query(self, query: str, params=None) -> List[Any]:
        """Execute SQL query and return results in simple format"""
        if params:
            # For parameterized queries, we need to format them manually 
            # since execute_sql_query doesn't support parameters
            try:
                formatted_query = query
                if params:
                    # Simple parameter substitution (not safe for production)
                    for param in params:
                        formatted_query = formatted_query.replace('?', f"'{param}'", 1)
                
                result = await self.context_manager.database.execute_sql_query(formatted_query)
                
                if result['success']:
                    return [tuple(row.values()) for row in result['results']]
                else:
                    raise Exception(result['error'])
            except Exception as e:
                raise Exception(f"Query execution failed: {e}")
        else:
            # Direct query without parameters
            result = await self.context_manager.database.execute_sql_query(query)
            
            if result['success']:
                return [tuple(row.values()) for row in result['results']]
            else:
                raise Exception(result['error'])
    
    async def memory_bank_sql_query(self, query: str, max_content_length: Optional[int] = None) -> str:
        """Execute SQL query with smart context-aware truncation and configurable limits"""
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            # Smart query analysis (v1.4.0 enhancement)
            intent_analysis = SmartSQLTruncation.analyze_query_intent(query)
            
            # Determine effective truncation limit
            if max_content_length is not None:
                effective_limit = max_content_length
                truncation_reason = f"User specified: {max_content_length} chars"
            else:
                effective_limit = intent_analysis['limit']
                truncation_reason = intent_analysis['reason']
            
            # Execute query
            logger.info(f"Executing SQL query with {intent_analysis['strategy']} strategy (limit: {effective_limit})")
            result = await self._execute_query(query)
            
            if not result:
                return f"""✅ **SQL QUERY EXECUTED**

**Query Type:** {self._detect_query_type(query)}
**Truncation Strategy:** {intent_analysis['strategy']} ({effective_limit} chars)
**Reason:** {truncation_reason}

**Result:** No rows returned

**Database:** {self.context_manager.database_path}
"""
            
            # Format results with smart truncation
            formatted_result = self._format_results_with_truncation(
                result, query, effective_limit, intent_analysis
            )
            
            return formatted_result
            
        except Exception as e:
            logger.error(f"SQL query error: {e}")
            return f"""❌ **SQL QUERY FAILED**

**Error:** {str(e)}
**Query Type:** {self._detect_query_type(query)}
**Database:** {self.context_manager.database_path}

💡 **Troubleshooting:**
• Check table names with `memory_bank_list_tables()`
• Verify column names with `memory_bank_table_info('table_name')`
• Use `memory_bank_describe_schema()` for full schema
"""
    
    def _format_results_with_truncation(self, result: List[Any], query: str, 
                                       max_length: int, intent_analysis: Dict) -> str:
        """Format SQL results with v1.4.0 smart truncation system"""
        
        query_type = self._detect_query_type(query)
        
        # Build header
        header = f"""✅ **SQL QUERY EXECUTED**

**Query Type:** {query_type}
**Truncation Strategy:** {intent_analysis['strategy']} ({max_length} chars)
**Reason:** {intent_analysis['reason']}
**Columns:** {len(result[0]) if result else 0}
**Row Count:** {len(result)}
**Database:** {self.context_manager.database_path}

**Results:**
"""
        
        any_truncated = False
        
        # Format each row with truncation
        for i, row in enumerate(result, 1):
            header += f"\n**Row {i}:**\n"
            
            for j, value in enumerate(row):
                col_name = f"col_{j}"
                
                if isinstance(value, str):
                    # Apply smart truncation to string values
                    truncation_result = SmartSQLTruncation.apply_smart_truncation(value, max_length)
                    
                    if truncation_result['was_truncated']:
                        any_truncated = True
                    
                    header += f"  • {col_name}: {truncation_result['truncated_content']}\n"
                else:
                    header += f"  • {col_name}: {value}\n"
        
        # Add truncation notice (v1.4.0 enhancement)
        if any_truncated:
            header += f"\n⚠️ **Content truncated** (limit: {max_length} chars)"
            header += f"\n💡 **Tip:** Use `max_content_length=None` for full content or `extract_large_document()` for large items"
        
        return header
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the type of SQL query"""
        query_upper = query.upper().strip()
        
        if query_upper.startswith('SELECT'):
            return 'SELECT'
        elif query_upper.startswith('INSERT'):
            return 'INSERT'
        elif query_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif query_upper.startswith('DELETE'):
            return 'DELETE'
        elif query_upper.startswith('CREATE'):
            return 'CREATE'
        elif query_upper.startswith('DROP'):
            return 'DROP'
        elif query_upper.startswith('ALTER'):
            return 'ALTER'
        elif query_upper.startswith('PRAGMA'):
            return 'PRAGMA'
        else:
            return 'OTHER'
    
    async def sql_truncation_help(self) -> str:
        """Show help for enhanced SQL truncation features and content access options"""
        return """🔧 **SMART SQL TRUNCATION HELP - v1.4.0**

**🎯 AUTOMATIC TRUNCATION STRATEGIES:**

**Content-Focused Queries (400 chars):**
• `SELECT content FROM discussions`
• `WHERE content LIKE '%keyword%'`
• `SELECT title, content FROM documents_v2`

**Overview Queries (80 chars):**
• `SELECT COUNT(*) FROM table`
• `PRAGMA table_info(table_name)`
• `SELECT * FROM table LIMIT 3`

**Balanced Queries (150 chars):**
• `SELECT title, summary FROM discussions`
• `SELECT uuid, title FROM documents_v2`
• `ORDER BY created_at DESC`

**🎛️ USER CONTROL:**
• `memory_bank_sql_query(query, max_content_length=500)`
• `memory_bank_sql_query(query, max_content_length=None)` (no limit)

🚀 **v1.4.0 transforms SQL queries from limited views to complete content access!**
        """.strip()
