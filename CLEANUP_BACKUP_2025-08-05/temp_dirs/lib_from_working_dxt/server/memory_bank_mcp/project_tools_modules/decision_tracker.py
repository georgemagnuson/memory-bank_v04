#!/usr/bin/env python3
"""
server/memory_bank_mcp/project_tools_modules/decision_tracker.py
Generated: 2025-07-30.1912
Purpose: Decision logging and retrieval with v2.0 documents table architecture

Key v2.0 Features:
- Uses documents table with document_type='decision'
- Full project_uuid support for cross-project decision tracking
- Enhanced metadata structure with v2.0 fields
- Clean v2.0-only implementation (no backward compatibility)
"""

import logging
import uuid
from datetime import datetime
from typing import List, Any, Optional

logger = logging.getLogger(__name__)

class DecisionTracker:
    """Decision logging and retrieval with v2.0 documents table architecture"""
    
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
    
    async def log_decision(self, summary: str, rationale: str = "", tags: str = "") -> str:
        """
        Log architectural/implementation decision to v2.0 documents table
        
        Args:
            summary: Brief decision summary
            rationale: Detailed reasoning behind the decision
            tags: Comma-separated tags for categorization
            
        Returns:
            Formatted success/error message
        """
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            # Generate UUID for decision document
            decision_uuid = str(uuid.uuid4())
            
            # Get current project context for project_uuid
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', '')
            
            # Create v2.0 decision document content
            decision_content = {
                'summary': summary,
                'rationale': rationale,
                'tags': tags,
                'decision_type': 'architectural',  # Enhanced v2.0 metadata
                'decision_date': datetime.utcnow().isoformat(),
            }
            
            # Insert into v2.0 documents table with decision type
            query = """
            INSERT INTO documents (
                uuid, project_uuid, title, content, document_type, 
                status, created_at, updated_at, metadata
            ) VALUES (?, ?, ?, ?, 'decision', 'active', datetime('now'), datetime('now'), ?)
            """
            
            # Prepare metadata as JSON string for v2.0 compatibility
            import json
            metadata_json = json.dumps({
                'rationale': rationale,
                'tags': tags.split(',') if tags else [],
                'decision_type': 'architectural',
                'version': '2.0'
            })
            
            await self._execute_query(query, (
                decision_uuid, 
                project_uuid, 
                summary,  # title field
                json.dumps(decision_content),  # content field  
                metadata_json  # metadata field
            ))
            
            # Format tags for display
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
            tag_display = f" 🏷️ {', '.join(tag_list)}" if tag_list else ""
            
            return f"""✅ Decision logged to v2.0 documents table!
📝 **{summary}**{tag_display}
🆔 UUID: {decision_uuid}
📁 Project: {project_uuid[:8]}...
📊 Type: decision (v2.0 architecture)"""
            
        except Exception as e:
            logger.error(f"Error logging decision: {e}")
            return f"❌ Error logging decision: {str(e)}"
    
    async def query_decisions(self, search_term: str = "", limit: int = 10) -> str:
        """
        Search and retrieve logged decisions using v2.0 documents table
        
        Args:
            search_term: Optional search term for filtering decisions
            limit: Maximum number of decisions to return
            
        Returns:
            Formatted decision list or error message
        """
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            # Get current project context for filtering
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', '')
            
            if search_term:
                # Search decisions with term using v2.0 table structure
                query = """
                SELECT uuid, title, content, metadata, created_at, updated_at
                FROM documents 
                WHERE document_type = 'decision' 
                  AND project_uuid = ?
                  AND status = 'active'
                  AND (title LIKE ? OR content LIKE ? OR metadata LIKE ?)
                ORDER BY updated_at DESC, created_at DESC
                LIMIT ?
                """
                search_pattern = f"%{search_term}%"
                results = await self._execute_query(query, (
                    project_uuid, search_pattern, search_pattern, search_pattern, limit
                ))
            else:
                # Get all recent decisions for current project
                query = """
                SELECT uuid, title, content, metadata, created_at, updated_at
                FROM documents 
                WHERE document_type = 'decision' 
                  AND project_uuid = ?
                  AND status = 'active'
                ORDER BY updated_at DESC, created_at DESC
                LIMIT ?
                """
                results = await self._execute_query(query, (project_uuid, limit))
            
            if not results:
                search_info = f" matching '{search_term}'" if search_term else ""
                return f"""🔍 No decisions found{search_info}.

💡 Use `log_decision("Summary", "Rationale", "tag1,tag2")` to start tracking decisions.
📊 Using v2.0 documents table architecture."""
            
            # Format results with v2.0 enhanced display
            decisions_text = f"🔍 **DECISIONS FOUND: {len(results)}** (v2.0 architecture)"
            if search_term:
                decisions_text += f" (searching: '{search_term}')"
            decisions_text += f"\n📁 Project: {project_uuid[:8]}...\n\n"
            
            for decision_data in results:
                uuid_val, title, content, metadata, created_at, updated_at = decision_data
                
                # Parse metadata for enhanced v2.0 display
                try:
                    import json
                    metadata_obj = json.loads(metadata) if metadata else {}
                    tags = metadata_obj.get('tags', [])
                    rationale = metadata_obj.get('rationale', '')
                    decision_type = metadata_obj.get('decision_type', 'architectural')
                except:
                    tags = []
                    rationale = ''
                    decision_type = 'architectural'
                
                # Format tags display
                tag_display = f" 🏷️ {', '.join(tags)}" if tags else ""
                
                # Format date with enhanced v2.0 timestamps
                try:
                    date_obj = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    date_display = date_obj.strftime('%Y-%m-%d %H:%M')
                except:
                    date_display = updated_at
                
                decisions_text += f"📝 **{title}**{tag_display}\n"
                decisions_text += f"📅 {date_display} • 🆔 {uuid_val[:8]}... • 🔧 {decision_type}\n"
                
                if rationale:
                    # Truncate long rationale with smart truncation
                    display_rationale = rationale[:200] + "..." if len(rationale) > 200 else rationale
                    decisions_text += f"💭 {display_rationale}\n"
                
                decisions_text += "\n"
            
            return decisions_text.strip()
            
        except Exception as e:
            logger.error(f"Error querying decisions: {e}")
            return f"❌ Error retrieving decisions: {str(e)}"
    
    async def get_decision_stats(self) -> dict:
        """
        Get decision statistics for current project using v2.0 architecture
        
        Returns:
            Dictionary with decision counts and metadata
        """
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return {'error': 'Memory Bank not initialized'}
            
            # Get current project context
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', '')
            
            # Count decisions in v2.0 documents table
            query = """
            SELECT COUNT(*) as total_decisions,
                   COUNT(CASE WHEN created_at >= date('now', '-7 days') THEN 1 END) as recent_decisions
            FROM documents 
            WHERE document_type = 'decision' 
              AND project_uuid = ?
              AND status = 'active'
            """
            
            result = await self._execute_query(query, (project_uuid,))
            if result:
                total_decisions, recent_decisions = result[0]
                return {
                    'total_decisions': total_decisions,
                    'recent_decisions': recent_decisions,
                    'project_uuid': project_uuid,
                    'architecture_version': '2.0'
                }
            else:
                return {
                    'total_decisions': 0,
                    'recent_decisions': 0,
                    'project_uuid': project_uuid,
                    'architecture_version': '2.0'
                }
                
        except Exception as e:
            logger.error(f"Error getting decision stats: {e}")
            return {'error': str(e)}
