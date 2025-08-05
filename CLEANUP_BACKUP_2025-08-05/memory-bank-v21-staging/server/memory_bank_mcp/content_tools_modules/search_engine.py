#!/usr/bin/env python3
"""
content_tools_modules/search_engine.py
Generated: 2025-07-30.1439
Purpose: Core v2.0 search functionality using documents table architecture

Key v2.0 Changes:
- Uses documents table instead of unified_documents
- Uses uuid field instead of original_uuid
- Supports project_uuid for cross-project searches
- Updated FTS table references (documents_fts)
"""

import logging
import sqlite3
import json
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SearchEngine:
    """Core search functionality for v2.0 documents table architecture"""
    
    def __init__(self, context_manager):
        """Initialize search engine with context manager dependency
        
        Args:
            context_manager: Active ContextManager instance with database connection
        """
        self.context_manager = context_manager
        self.logger = logger
        
        # Document type mappings for documents table search
        self.document_types = {
            'discussion': 'discussion',
            'document': 'document', 
            'plan': 'plan',
            'code': 'code',
            'note': 'note',
            'markdown': 'markdown',
            'artifact': 'artifact',
            'chat_session': 'chat_session'
        }
        
        # Search prioritization order (higher priority first)
        self.priority_order = [
            'document', 'discussion', 'plan', 'code', 
            'artifact', 'note', 'markdown', 'chat_session'
        ]
        
        # Document type icons for display
        self.type_icons = {
            'discussion': '💭',
            'document': '📄',
            'plan': '📋',
            'code': '💻',
            'note': '📝',
            'markdown': '📄',
            'artifact': '🎯',
            'chat_session': '💬'
        }
    
    async def search_all_content(self, query: str, limit: int = 20, 
                               content_types: str = "all", 
                               project_uuid: Optional[str] = None) -> str:
        """Universal full-text search across documents table with type filtering
        
        Args:
            query: Search query string
            limit: Maximum number of results to return (default: 20)
            content_types: Comma-separated document types or "all" (default: "all")
                          Options: discussion,document,plan,code,note,markdown,artifact,chat_session
            project_uuid: Optional project UUID for cross-project search
        
        Returns:
            Formatted search results with ranking, highlighting, and metadata
        """
        try:
            if not self.context_manager or not self.context_manager.database_path:
                return "❌ **SEARCH FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            if not query.strip():
                return "❌ **SEARCH FAILED**\n\nQuery cannot be empty."
            
            # Parse content types for documents table
            if content_types.lower() == "all":
                search_types = list(self.document_types.keys())
            else:
                requested_types = [t.strip() for t in content_types.split(',')]
                search_types = [t for t in requested_types if t in self.document_types]
                if not search_types:
                    return f"❌ **SEARCH FAILED**\n\nInvalid content types: {content_types}\nValid options: {', '.join(self.document_types.keys())}"
            
            # Use current project UUID if not specified
            target_project_uuid = project_uuid or getattr(self.context_manager, 'project_uuid', None)
            if not target_project_uuid:
                return "❌ **SEARCH FAILED**\n\nNo project UUID available."
            
            # Execute v2.0 search with type filtering
            search_stats = {
                'query': query,
                'document_types_searched': len(search_types),
                'total_results': 0,
                'results_by_type': {},
                'extraction_available': False,
                'project_uuid': target_project_uuid
            }
            
            conn = sqlite3.connect(self.context_manager.database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            try:
                # Build v2.0 FTS query with document type filtering
                type_filter = "all" if content_types.lower() == "all" else " OR ".join([f"document_type = '{t}'" for t in search_types])
                
                # v2.0 query using documents table and documents_fts
                documents_query = f"""
                SELECT 
                    d.id,
                    d.uuid,
                    d.project_uuid,
                    d.source_table,
                    d.document_type,
                    d.title,
                    d.content,
                    d.summary,
                    d.tags,
                    d.metadata,
                    d.created_at,
                    d.updated_at,
                    snippet(documents_fts, 1, '<mark>', '</mark>', '...', 64) as highlighted_content
                FROM documents_fts fts
                JOIN documents d ON fts.rowid = d.id
                WHERE documents_fts MATCH ?
                AND d.project_uuid = ?
                {"" if type_filter == "all" else f"AND ({type_filter})"}
                AND d.status = 'active'
                ORDER BY rank
                LIMIT ?
                """
                
                cursor.execute(documents_query, (query, target_project_uuid, limit))
                all_results = cursor.fetchall()
                
                # Process results and gather statistics
                processed_results = []
                for row in all_results:
                    # Parse metadata JSON
                    try:
                        metadata = json.loads(row['metadata']) if row['metadata'] else {}
                    except json.JSONDecodeError:
                        metadata = {}
                    
                    result = {
                        'id': row['id'],
                        'uuid': row['uuid'],
                        'project_uuid': row['project_uuid'],
                        'source_table': row['source_table'],
                        'document_type': row['document_type'],
                        'title': row['title'] or 'Untitled',
                        'content': row['content'],
                        'summary': row['summary'],
                        'tags': json.loads(row['tags']) if row['tags'] else [],
                        'metadata': metadata,
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at'],
                        'highlighted_content': row['highlighted_content'],
                        'content_length': len(row['content']) if row['content'] else 0
                    }
                    processed_results.append(result)
                    
                    # Update statistics
                    doc_type = row['document_type']
                    if doc_type not in search_stats['results_by_type']:
                        search_stats['results_by_type'][doc_type] = 0
                    search_stats['results_by_type'][doc_type] += 1
                
                search_stats['total_results'] = len(processed_results)
                
                # Check if extraction is needed (large content)
                large_results = [r for r in processed_results if r['content_length'] > 2000]
                if large_results:
                    search_stats['extraction_available'] = True
                    search_stats['large_results_count'] = len(large_results)
                
                conn.close()
                
                # Format and return results
                return self._format_search_results(processed_results, search_stats, query)
                
            except sqlite3.Error as e:
                conn.close()
                self.logger.error(f"v2.0 search SQL error: {e}")
                return f"❌ **SEARCH FAILED**\n\nDatabase error: {str(e)}"
            
        except Exception as e:
            self.logger.error(f"v2.0 search failed: {e}")
            return f"❌ **SEARCH FAILED**\n\nError: {str(e)}"
    
    def _format_search_results(self, results: List[Dict], stats: Dict, query: str) -> str:
        """Format v2.0 search results with enhanced metadata and prioritization"""
        if not results:
            return f"""🔍 **v2.0 SEARCH RESULTS**

**Query:** "{query}"
**Project:** {stats['project_uuid'][:8]}...
**Document Types Searched:** {stats['document_types_searched']}
**Total Results:** 0

❌ No results found.

**Search Statistics:**
{json.dumps(stats['results_by_type'], indent=2)}"""
        
        output = [f"""🔍 **v2.0 SEARCH RESULTS**

**Query:** "{query}"
**Project:** {stats['project_uuid'][:8]}...
**Document Types Searched:** {stats['document_types_searched']}  
**Results Found:** {stats['total_results']}

"""]
        
        # Group results by document type with priority ordering
        results_by_type = {}
        for result in results:
            doc_type = result['document_type']
            if doc_type not in results_by_type:
                results_by_type[doc_type] = []
            results_by_type[doc_type].append(result)
        
        # Display results in priority order
        for doc_type in self.priority_order:
            if doc_type not in results_by_type:
                continue
                
            type_results = results_by_type[doc_type]
            icon = self.type_icons.get(doc_type, '📄')
            output.append(f"## {icon} {doc_type.upper()} ({len(type_results)} results)\n")
            
            for i, result in enumerate(type_results, 1):
                # Format title with metadata context
                title = result['title']
                if result['metadata'].get('spec_name'):
                    title += f" ({result['metadata']['spec_name']})"
                elif result['metadata'].get('filename'):
                    title = result['metadata']['filename']
                
                output.append(f"**{i}. {title}**")
                
                # Add source information with v2.0 structure
                source_info = f"📍 *{result['source_table']}* → *{result['document_type']}*"
                source_info += f" | ID: `{result['id']}` | UUID: `{result['uuid'][:8]}...`"
                if result['project_uuid'] != stats['project_uuid']:
                    source_info += f" | Project: `{result['project_uuid'][:8]}...`"
                output.append(source_info)
                
                # Add type-specific metadata
                metadata = result['metadata']
                if doc_type == 'document' and metadata.get('spec_phase'):
                    output.append(f"📋 Phase: {metadata['spec_phase']} | Status: {metadata.get('spec_status', 'unknown')}")
                elif doc_type == 'plan' and metadata.get('current_phase'):
                    output.append(f"📋 Current Phase: {metadata['current_phase']} | Priority: {metadata.get('priority', 'medium')}")
                elif doc_type == 'code' and metadata.get('language'):
                    output.append(f"💻 Language: {metadata['language']}")
                elif doc_type == 'artifact' and metadata.get('artifact_type'):
                    output.append(f"🎯 Type: {metadata['artifact_type']}")
                
                # Add content size indicator
                content_length = result['content_length']
                if content_length > 2000:
                    output.append(f"📏 Size: {content_length:,} chars (Large - extraction recommended)")
                elif content_length > 500:
                    output.append(f"📏 Size: {content_length:,} chars (Medium)")
                
                # Add highlighted content
                if result['highlighted_content']:
                    output.append(f"📄 {result['highlighted_content']}")
                
                # Add tags if present
                if result['tags']:
                    tags_str = ', '.join(result['tags'][:5])  # Show first 5 tags
                    output.append(f"🏷️ Tags: {tags_str}")
                
                output.append("")  # Empty line between results
        
        # Add search statistics
        output.append("## 📈 Search Statistics")
        for doc_type, count in stats['results_by_type'].items():
            icon = self.type_icons.get(doc_type, '📄')
            output.append(f"- {icon} **{doc_type}**: {count} results")
        
        # Add extraction tip for large results
        if stats.get('extraction_available'):
            output.append(f"\n⚡ **Large Results Detected**: {stats['large_results_count']} results with >2K chars")
            output.append(f"💡 **Tip**: Use `extract_large_document(\"{query}\")` to export full content to /tmp/")
        else:
            output.append(f"\n💡 **Tip**: Use `extract_large_document(\"{query}\")` to export complete content for analysis.")
        
        return "\n".join(output)
    
    def get_supported_document_types(self) -> List[str]:
        """Get list of supported document types for v2.0 architecture"""
        return list(self.document_types.keys())
    
    def get_priority_order(self) -> List[str]:
        """Get document type priority order for search results"""
        return self.priority_order.copy()
