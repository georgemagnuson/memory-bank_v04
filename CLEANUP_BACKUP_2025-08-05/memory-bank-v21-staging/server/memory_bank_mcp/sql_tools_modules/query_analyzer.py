#!/usr/bin/env python3
"""
sql_tools_modules/query_analyzer.py
Generated: 2025-07-30.1848
Purpose: Smart SQL query analysis and intent detection for v2.0 documents table

Key v2.0 Updates:
- Updated patterns to recognize documents table instead of unified_documents
- Enhanced detection for project_uuid queries
- Support for v2.0 FTS table patterns (documents_fts)
- Status field awareness (status = 'active')
"""

import logging
import re
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class QueryAnalyzer:
    """Smart SQL query analysis system with v2.0 table awareness"""
    
    def __init__(self):
        """Initialize query analyzer with v2.0 patterns"""
        self.logger = logger
        
        # v2.0 Content-focused patterns (documents table)
        self.CONTENT_FOCUSED_PATTERNS = [
            r'SELECT.*content.*FROM.*documents',
            r'WHERE.*content.*LIKE',
            r'SELECT.*summary.*FROM.*documents',
            r'SELECT.*title.*content.*FROM.*documents',
            r'documents_fts.*MATCH',
            r'content.*MATCH.*documents',
        ]
        
        # v2.0 Overview patterns (metadata and counts)
        self.OVERVIEW_PATTERNS = [
            r'SELECT COUNT\(',
            r'SELECT.*COUNT\(',
            r'PRAGMA',
            r'SELECT.*name.*FROM.*sqlite_master',
            r'DESCRIBE',
            r'SHOW TABLES',
            r'SELECT.*\*.*LIMIT\s+[1-5]\b',
            r'table_info\(',
            r'SELECT.*document_type.*COUNT',
        ]
        
        # v2.0 Balanced patterns (titles, summaries, metadata)
        self.BALANCED_PATTERNS = [
            r'SELECT.*title.*FROM.*documents',
            r'SELECT.*summary.*FROM.*documents',
            r'SELECT.*uuid.*FROM.*documents',
            r'SELECT.*project_uuid.*FROM.*documents',
            r'ORDER BY.*created_at',
            r'ORDER BY.*updated_at',
            r'GROUP BY.*document_type',
            r'WHERE.*status.*=.*active',
        ]
        
        # v2.0 Cross-project patterns (higher limits needed)
        self.CROSS_PROJECT_PATTERNS = [
            r'project_uuid.*IN',
            r'SELECT.*FROM.*documents.*JOIN.*projects',
            r'WHERE.*project_uuid.*!=',
            r'GROUP BY.*project_uuid',
        ]
    
    def analyze_query_intent(self, query: str) -> Dict[str, Any]:
        """Analyze SQL query to determine optimal truncation strategy for v2.0"""
        query_upper = query.upper().strip()
        
        # Check for user override patterns first
        if 'LIMIT' in query_upper and any(x in query_upper for x in ['1', '2', '3', '4', '5']):
            return {
                'strategy': 'user_controlled',
                'limit': 200,
                'reason': 'User specified small LIMIT - moderate truncation',
                'table_version': self._detect_table_version(query)
            }
        
        # Check cross-project patterns (need higher limits)
        for pattern in self.CROSS_PROJECT_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return {
                    'strategy': 'cross_project',
                    'limit': 500,
                    'reason': 'Cross-project query detected - high character limit for multiple projects',
                    'table_version': 'v2.0'
                }
        
        # Check content-focused patterns (highest limit)
        for pattern in self.CONTENT_FOCUSED_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return {
                    'strategy': 'content_focused',
                    'limit': 400,
                    'reason': 'Content-focused query detected - high character limit',
                    'table_version': self._detect_table_version(query)
                }
        
        # Check overview patterns (lowest limit)
        for pattern in self.OVERVIEW_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return {
                    'strategy': 'overview',
                    'limit': 80,
                    'reason': 'Overview/metadata query detected - low character limit',
                    'table_version': self._detect_table_version(query)
                }
        
        # Check balanced patterns (medium limit)
        for pattern in self.BALANCED_PATTERNS:
            if re.search(pattern, query_upper, re.IGNORECASE):
                return {
                    'strategy': 'balanced',
                    'limit': 150,
                    'reason': 'Balanced query detected - medium character limit',
                    'table_version': self._detect_table_version(query)
                }
        
        # Default strategy
        return {
            'strategy': 'balanced',
            'limit': 150,
            'reason': 'Default strategy - medium character limit',
            'table_version': self._detect_table_version(query)
        }
    
    def _detect_table_version(self, query: str) -> str:
        """Detect if query is using v1.4.0 or v2.0 table structure"""
        query_upper = query.upper()
        
        # v2.0 indicators
        if any(indicator in query_upper for indicator in [
            'FROM DOCUMENTS',
            'JOIN DOCUMENTS',  
            'DOCUMENTS_FTS',
            'PROJECT_UUID',
            'STATUS = \'ACTIVE\''
        ]):
            return 'v2.0'
        
        # v1.4.0 indicators
        if any(indicator in query_upper for indicator in [
            'FROM UNIFIED_DOCUMENTS',
            'JOIN UNIFIED_DOCUMENTS',
            'UNIFIED_DOCUMENTS_FTS',
            'ORIGINAL_UUID'
        ]):
            return 'v1.4.0'
        
        # Default to v2.0 for new queries
        return 'v2.0'
    
    def detect_query_type(self, query: str) -> str:
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
    
    def get_query_recommendations(self, query: str) -> List[str]:
        """Get v2.0-specific query recommendations"""
        recommendations = []
        query_upper = query.upper()
        
        # Suggest v2.0 upgrades for v1.4.0 queries
        if 'UNIFIED_DOCUMENTS' in query_upper:
            recommendations.append("💡 Consider upgrading to v2.0: Use 'documents' table instead of 'unified_documents'")
        
        if 'ORIGINAL_UUID' in query_upper:
            recommendations.append("💡 v2.0 upgrade: Use 'uuid' field instead of 'original_uuid'")
        
        # Suggest project_uuid usage
        if 'FROM DOCUMENTS' in query_upper and 'PROJECT_UUID' not in query_upper:
            recommendations.append("💡 v2.0 feature: Add 'project_uuid' filter for better performance")
        
        # Suggest status filtering
        if 'FROM DOCUMENTS' in query_upper and 'STATUS' not in query_upper:
            recommendations.append("💡 v2.0 best practice: Add 'status = \"active\"' filter")
        
        return recommendations
    
    def get_supported_strategies(self) -> List[str]:
        """Get list of supported truncation strategies"""
        return ['content_focused', 'overview', 'balanced', 'cross_project', 'user_controlled']
