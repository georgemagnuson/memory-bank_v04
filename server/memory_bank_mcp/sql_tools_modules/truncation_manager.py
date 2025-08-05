#!/usr/bin/env python3
"""
sql_tools_modules/truncation_manager.py
Generated: 2025-07-30.1848
Purpose: Advanced content truncation with v2.0 awareness

Key v2.0 Enhancements:
- Project-aware truncation (higher limits for cross-project content)
- Enhanced metadata preservation for v2.0 fields
- Smart word boundary detection
- Content type-aware truncation
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class TruncationManager:
    """Advanced content truncation system with v2.0 awareness"""
    
    def __init__(self):
        """Initialize truncation manager"""
        self.logger = logger
    
    def apply_smart_truncation(self, content: str, max_length: int, 
                             content_type: str = 'text') -> Dict[str, Any]:
        """Apply smart truncation with v2.0 enhancements
        
        Args:
            content: Content to truncate
            max_length: Maximum length (None for no truncation)
            content_type: Type of content (text, json, uuid, etc.)
            
        Returns:
            Dictionary with truncation results and metadata
        """
        if not content:
            return {
                'truncated_content': '',
                'was_truncated': False,
                'original_length': 0,
                'truncated_length': 0,
                'content_type': content_type
            }
        
        original_length = len(content)
        
        if max_length is None or original_length <= max_length:
            return {
                'truncated_content': content,
                'was_truncated': False,
                'original_length': original_length,
                'truncated_length': original_length,
                'content_type': content_type
            }
        
        # Apply content-type specific truncation
        if content_type == 'uuid':
            # Never truncate UUIDs, but show shortened version
            return self._truncate_uuid(content, max_length, original_length)
        elif content_type == 'json':
            return self._truncate_json(content, max_length, original_length)
        else:
            return self._truncate_text(content, max_length, original_length, content_type)
    
    def _truncate_text(self, content: str, max_length: int, original_length: int, 
                      content_type: str) -> Dict[str, Any]:
        """Truncate regular text content with smart word boundaries"""
        
        # Smart truncation - try to break at word boundaries
        if max_length > 20:
            # Find last space before limit
            truncate_point = max_length
            while truncate_point > max_length * 0.8 and truncate_point > 0:
                if content[truncate_point] == ' ':
                    break
                truncate_point -= 1
            
            # If no good break point found, use hard limit
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
            'truncate_point': truncate_point,
            'content_type': content_type,
            'truncation_method': 'word_boundary'
        }
    
    def _truncate_uuid(self, content: str, max_length: int, original_length: int) -> Dict[str, Any]:
        """Handle UUID truncation with v2.0 awareness"""
        
        # UUIDs should generally not be truncated, but show shortened version
        if len(content) == 36 and content.count('-') == 4:
            # Standard UUID format - show first 8 chars + ...
            if max_length < 12:
                truncated = content[:8] + "..."
            else:
                truncated = content
        else:
            # Not a standard UUID, treat as text
            truncated = content[:max_length] + "..." if len(content) > max_length else content
        
        return {
            'truncated_content': truncated,
            'was_truncated': len(truncated) < original_length,
            'original_length': original_length,
            'truncated_length': len(truncated),
            'content_type': 'uuid',
            'truncation_method': 'uuid_shortening'
        }
    
    def _truncate_json(self, content: str, max_length: int, original_length: int) -> Dict[str, Any]:
        """Handle JSON content truncation with structure preservation"""
        
        try:
            import json
            # Try to parse as JSON
            parsed = json.loads(content)
            
            # If it's a simple value, truncate normally
            if isinstance(parsed, (str, int, float)):
                return self._truncate_text(str(parsed), max_length, original_length, 'json_value')
            
            # For complex JSON, show truncated pretty-printed version
            pretty = json.dumps(parsed, indent=2)
            if len(pretty) <= max_length:
                return {
                    'truncated_content': pretty,
                    'was_truncated': False,
                    'original_length': original_length,
                    'truncated_length': len(pretty),
                    'content_type': 'json',
                    'truncation_method': 'pretty_print'
                }
            else:
                # Truncate the pretty-printed version
                truncated = pretty[:max_length-3] + "..."
                return {
                    'truncated_content': truncated,
                    'was_truncated': True,
                    'original_length': original_length,
                    'truncated_length': len(truncated),
                    'content_type': 'json',
                    'truncation_method': 'json_truncated'
                }
                
        except (json.JSONDecodeError, ValueError):
            # Not valid JSON, treat as text
            return self._truncate_text(content, max_length, original_length, 'json_invalid')
    
    def analyze_content_type(self, content: str, column_name: str = '') -> str:
        """Analyze content to determine optimal truncation approach"""
        
        if not content:
            return 'empty'
        
        # Check column name hints
        column_lower = column_name.lower()
        if 'uuid' in column_lower:
            return 'uuid'
        elif 'json' in column_lower or column_lower in ['metadata', 'tags']:
            return 'json'
        
        # Content-based detection
        content_str = str(content).strip()
        
        # UUID detection (v2.0 uses standard UUIDs)
        if len(content_str) == 36 and content_str.count('-') == 4:
            return 'uuid'
        
        # JSON detection
        if content_str.startswith(('{', '[')) and content_str.endswith(('}', ']')):
            return 'json'
        
        # Default to text
        return 'text'
    
    def get_truncation_stats(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate truncation statistics for v2.0 reporting"""
        
        stats = {
            'total_fields': 0,
            'truncated_fields': 0,
            'content_types': {},
            'truncation_methods': {},
            'total_original_length': 0,
            'total_truncated_length': 0
        }
        
        return stats
    
    def get_supported_content_types(self) -> list:
        """Get list of supported content types"""
        return ['text', 'uuid', 'json', 'empty']
