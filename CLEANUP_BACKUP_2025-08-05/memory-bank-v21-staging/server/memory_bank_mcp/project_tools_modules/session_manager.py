#!/usr/bin/env python3
"""
server/memory_bank_mcp/project_tools_modules/session_manager.py
Generated: 2025-07-30.1912
Purpose: Enhanced session management with v2.0 documents table architecture

Key v2.0 Features:
- Uses documents table instead of unified_documents
- Enhanced project_uuid support for cross-project sessions
- Smart document type filtering with v2.0 structure
- Clean v2.0-only implementation (no backward compatibility)
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SessionManager:
    """Enhanced session management with v2.0 documents table architecture"""
    
    def __init__(self, context_manager):
        """Initialize with context manager for v2.0 database access"""
        self.context_manager = context_manager
    
    async def _execute_query(self, query: str, params: tuple = ()) -> List[Any]:
        """Execute SQL query using context manager with v2.0 error handling"""
        try:
            # Use the context manager's SQL query capability
            if hasattr(self.context_manager, 'database') and hasattr(self.context_manager.database, 'execute_query'):
                result = await self.context_manager.database.execute_query(query, params)
                if isinstance(result, dict) and result.get('success'):
                    return [tuple(row.values()) for row in result.get('results', [])]
                elif isinstance(result, list):
                    return result
                else:
                    raise Exception(f"Query failed: {result.get('error', 'Unknown error')}")
            else:
                # Fallback for testing or simplified execution
                return []
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
    
    async def generate_enhanced_session_starter(self, session_goal: str = "", session_type: str = "Implementation") -> str:
        """
        Generate comprehensive session starter with v2.0 database context
        
        Args:
            session_goal: Optional specific goal for the session
            session_type: Type of session (Implementation, Analysis, Planning, etc.)
            
        Returns:
            Formatted session starter with v2.0 context information
        """
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            # Get v2.0 project statistics and context
            db_stats = await self._get_v2_database_stats()
            project_info = await self.context_manager.get_current_session_info()
            
            # Get recent decisions using v2.0 documents table
            recent_decisions = await self._get_recent_decisions()
            
            # Get recent discussions using v2.0 documents table  
            recent_discussions = await self._get_recent_discussions()
            
            # Get recent important documents
            recent_documents = await self._get_recent_documents()
            
            # Build enhanced session starter with v2.0 context
            starter = f"""🚀 **ENHANCED SESSION STARTER - {session_type.upper()}** (v2.0)

**📁 Project Context:**
• Project: {project_info.get('project_name', 'Unknown')}
• Path: {self.context_manager.project_path}
• Project UUID: {project_info.get('project_uuid', 'Not set')[:8]}...
• Session Type: {session_type}"""
            
            if session_goal:
                starter += f"\n• Goal: {session_goal}"
            
            # Add v2.0 knowledge base statistics
            starter += f"""

**📊 Knowledge Base (v2.0 Architecture):**
• 📄 Total Documents: {db_stats.get('total_documents', 0)}
  - 💭 Discussions: {db_stats.get('discussions', 0)}
  - 🎯 Artifacts: {db_stats.get('artifacts', 0)}
  - 📋 Plans: {db_stats.get('plans', 0)}
  - 💻 Code: {db_stats.get('code', 0)}
  - 📝 Notes: {db_stats.get('notes', 0)}
  - 📄 Documents: {db_stats.get('documents', 0)}
  - 🔧 Decisions: {db_stats.get('decisions', 0)}
  - 📋 Markdown: {db_stats.get('markdown', 0)}

**🚀 v2.0 UNIFIED DOCUMENT ARCHITECTURE:**
Claude automatically recognizes all Memory Bank commands:
• Single documents table with smart document_type filtering
• Enhanced project_uuid support for cross-project functionality  
• Smart SQL queries with advanced truncation strategies
• Multi-table content extraction with intelligent prioritization
• Search prioritization (context.db content first)
• Seamless workflow integration with modular architecture"""
            
            # Add recent context information
            if recent_decisions:
                starter += "\n\n**📝 Recent Decisions:**"
                for decision in recent_decisions:
                    title, tags, created_at = decision
                    tag_display = f" ({tags})" if tags else ""
                    starter += f"\n• {title}{tag_display}"
            
            if recent_discussions:
                starter += "\n\n**💭 Recent Discussions:**"
                for discussion in recent_discussions:
                    title, created_at = discussion
                    starter += f"\n• {title}"
            
            if recent_documents:
                starter += "\n\n**📄 Recent Documents:**"
                for doc in recent_documents:
                    title, doc_type, created_at = doc
                    type_icon = self._get_document_type_icon(doc_type)
                    starter += f"\n• {type_icon} {title}"
            
            # Add v2.0 ready message
            starter += f"""

**🎯 Ready for {session_type}!**
Memory Bank v2.0 enhanced features are active and ready to assist:
✅ Modular architecture with focused components
✅ Enhanced document management with project_uuid support
✅ Smart content extraction and search capabilities  
✅ Cross-project decision tracking and context management
✅ All content searchable with intelligent truncation

Start with any Memory Bank command - all tools recognize v2.0 architecture automatically!"""
            
            return starter
            
        except Exception as e:
            logger.error(f"Error generating session starter: {e}")
            return f"❌ Error generating session starter: {str(e)}"
    
    async def _get_v2_database_stats(self) -> Dict[str, int]:
        """Get comprehensive database statistics using v2.0 documents table"""
        try:
            # Get current project context
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', '')
            
            # Count documents by type using v2.0 table structure
            stats_query = """
            SELECT 
                document_type,
                COUNT(*) as count
            FROM documents 
            WHERE project_uuid = ? AND status = 'active'
            GROUP BY document_type
            """
            
            results = await self._execute_query(stats_query, (project_uuid,))
            
            # Initialize stats dictionary with v2.0 document types
            stats = {
                'total_documents': 0,
                'discussions': 0,
                'artifacts': 0,
                'plans': 0,
                'code': 0,
                'notes': 0,
                'documents': 0,
                'decisions': 0,
                'markdown': 0
            }
            
            # Process results and populate stats
            for doc_type, count in results:
                if doc_type == 'discussion':
                    stats['discussions'] = count
                elif doc_type == 'artifact':
                    stats['artifacts'] = count
                elif doc_type == 'plan':
                    stats['plans'] = count
                elif doc_type == 'code':
                    stats['code'] = count
                elif doc_type == 'note':
                    stats['notes'] = count
                elif doc_type == 'document':
                    stats['documents'] = count
                elif doc_type == 'decision':
                    stats['decisions'] = count
                elif doc_type == 'markdown':
                    stats['markdown'] = count
                
                stats['total_documents'] += count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'total_documents': 0}
    
    async def _get_recent_decisions(self) -> List[tuple]:
        """Get recent decisions using v2.0 documents table"""
        try:
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', '')
            
            query = """
            SELECT title, metadata, created_at 
            FROM documents 
            WHERE document_type = 'decision' 
              AND project_uuid = ?
              AND status = 'active'
            ORDER BY created_at DESC 
            LIMIT 3
            """
            
            results = await self._execute_query(query, (project_uuid,))
            
            # Extract tags from metadata for display
            decisions = []
            for title, metadata, created_at in results:
                try:
                    import json
                    metadata_obj = json.loads(metadata) if metadata else {}
                    tags = ', '.join(metadata_obj.get('tags', []))
                except:
                    tags = ''
                decisions.append((title, tags, created_at))
            
            return decisions
            
        except Exception as e:
            logger.error(f"Error getting recent decisions: {e}")
            return []
    
    async def _get_recent_discussions(self) -> List[tuple]:
        """Get recent discussions using v2.0 documents table"""
        try:
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', '')
            
            query = """
            SELECT title, created_at 
            FROM documents 
            WHERE document_type = 'discussion'
              AND project_uuid = ?
              AND status = 'active'
            ORDER BY created_at DESC 
            LIMIT 3
            """
            
            return await self._execute_query(query, (project_uuid,))
            
        except Exception as e:
            logger.error(f"Error getting recent discussions: {e}")
            return []
    
    async def _get_recent_documents(self) -> List[tuple]:
        """Get recent important documents using v2.0 documents table"""
        try:
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', '')
            
            query = """
            SELECT title, document_type, created_at 
            FROM documents 
            WHERE document_type IN ('plan', 'artifact', 'code')
              AND project_uuid = ?
              AND status = 'active'
            ORDER BY created_at DESC 
            LIMIT 5
            """
            
            return await self._execute_query(query, (project_uuid,))
            
        except Exception as e:
            logger.error(f"Error getting recent documents: {e}")
            return []
    
    def _get_document_type_icon(self, doc_type: str) -> str:
        """Get appropriate icon for document type"""
        icons = {
            'discussion': '💭',
            'artifact': '🎯', 
            'plan': '📋',
            'code': '💻',
            'note': '📝',
            'document': '📄',
            'decision': '🔧',
            'markdown': '📋'
        }
        return icons.get(doc_type, '📄')
    
    async def get_session_context(self) -> Dict[str, Any]:
        """
        Get comprehensive session context for v2.0 architecture
        
        Returns:
            Dictionary with session context information
        """
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return {'error': 'Memory Bank not initialized'}
            
            # Get project and database information
            project_info = await self.context_manager.get_current_session_info()
            db_stats = await self._get_v2_database_stats()
            
            # Get recent activity
            recent_decisions = await self._get_recent_decisions()
            recent_discussions = await self._get_recent_discussions()
            recent_documents = await self._get_recent_documents()
            
            return {
                'project_info': project_info,
                'database_stats': db_stats,
                'recent_activity': {
                    'decisions': recent_decisions,
                    'discussions': recent_discussions,
                    'documents': recent_documents
                },
                'architecture_version': '2.0',
                'session_timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting session context: {e}")
            return {'error': str(e)}
