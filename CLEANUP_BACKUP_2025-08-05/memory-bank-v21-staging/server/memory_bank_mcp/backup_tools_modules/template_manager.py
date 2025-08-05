#!/usr/bin/env python3
"""
server/memory_bank_mcp/backup_tools_modules/template_manager.py
Generated: 2025-07-30.1927
Purpose: Template specification storage and discovery with v2.0 enhanced metadata

Key v2.0 Features:
- Templates stored in documents table with document_type='template'
- Enhanced project_uuid support for cross-project template sharing
- Rich metadata structure with v2.0 compatibility
- Future-proof template management aligned with unified documents architecture
"""

import logging
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class TemplateManager:
    """Template specification storage and discovery with v2.0 enhanced metadata"""
    
    def __init__(self, context_manager):
        """Initialize with context manager for v2.0 database access"""
        self.context_manager = context_manager
    
    async def _execute_query(self, query: str, params: tuple = ()) -> List[Any]:
        """Execute SQL query using context manager with v2.0 error handling"""
        try:
            if hasattr(self.context_manager, 'database') and hasattr(self.context_manager.database, 'execute_query'):
                result = await self.context_manager.database.execute_query(query, params)
                if isinstance(result, dict) and result.get('success'):
                    return [tuple(row.values()) for row in result.get('results', [])]
                elif isinstance(result, list):
                    return result
                else:
                    raise Exception(f"Query failed: {result.get('error', 'Unknown error')}")
            else:
                return []
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
    
    async def store_template_spec(self, template_name: str, template_content: str, 
                                 template_version: str = "1.0", description: str = "",
                                 project_types: str = "general", spec_phase: Optional[str] = None,
                                 workflow_system: str = "spec-workflow", update_existing: bool = True) -> str:
        """
        Store complete template specification in v2.0 documents table
        
        Args:
            template_name: Name of the template
            template_content: Complete template content/specification
            template_version: Version of the template
            description: Template description
            project_types: Applicable project types (comma-separated)
            spec_phase: Optional specification phase
            workflow_system: Workflow system identifier
            update_existing: Whether to update existing templates
            
        Returns:
            Formatted storage report with v2.0 details
        """
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            # Get current project context for v2.0
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', str(uuid.uuid4()))
            
            # Check if template already exists
            existing_template = await self._find_existing_template(template_name, project_uuid)
            
            if existing_template and not update_existing:
                return f"""⚠️ **TEMPLATE EXISTS** (v2.0)

**Template:** {template_name}
**Existing UUID:** {existing_template['uuid'][:8]}...
**Use update_existing=True** to update the existing template.

💡 Use `discover_templates(search_query="{template_name}")` to view existing templates."""
            
            # Generate template UUID
            template_uuid = existing_template['uuid'] if existing_template else str(uuid.uuid4())
            
            # Create enhanced v2.0 metadata
            metadata = {
                'template_version': template_version,
                'description': description,
                'project_types': [t.strip() for t in project_types.split(',')],
                'spec_phase': spec_phase,
                'workflow_system': workflow_system,
                'created_date': datetime.utcnow().isoformat(),
                'architecture_version': '2.0',
                'content_type': 'template_specification'
            }
            
            if existing_template:
                # Update existing template in documents table
                query = """
                UPDATE documents 
                SET title = ?, content = ?, updated_at = datetime('now'), metadata = ?
                WHERE uuid = ? AND project_uuid = ? AND document_type = 'template'
                """
                
                await self._execute_query(query, (
                    template_name,
                    template_content,
                    json.dumps(metadata),
                    template_uuid,
                    project_uuid
                ))
                
                action = "UPDATED"
            else:
                # Insert new template into v2.0 documents table
                query = """
                INSERT INTO documents (
                    uuid, project_uuid, title, content, document_type,
                    status, created_at, updated_at, metadata
                ) VALUES (?, ?, ?, ?, 'template', 'active', datetime('now'), datetime('now'), ?)
                """
                
                await self._execute_query(query, (
                    template_uuid,
                    project_uuid,
                    template_name,
                    template_content,
                    json.dumps(metadata)
                ))
                
                action = "STORED"
            
            return f"""✅ **TEMPLATE {action}** (v2.0 Architecture)

**📋 Template:** {template_name}
**🆔 UUID:** {template_uuid[:8]}...
**📁 Project UUID:** {project_uuid[:8]}...
**📊 Version:** {template_version}
**🏷️ Project Types:** {project_types}

**🚀 v2.0 Benefits Applied:**
• ✅ Stored in unified documents table with document_type='template'
• ✅ Enhanced metadata with cross-project compatibility
• ✅ Full-text search ready across all templates
• ✅ Future-proof design aligned with v2.0 architecture

**💡 Template is now searchable and discoverable across projects!**"""
            
        except Exception as e:
            logger.error(f"Error storing template: {e}")
            return f"❌ Error storing template '{template_name}': {str(e)}"
    
    async def discover_templates(self, search_query: Optional[str] = None, project_type: Optional[str] = None,
                                spec_phase: Optional[str] = None, workflow_system: Optional[str] = None,
                                sort_by: str = "updated_at", limit: int = 20) -> str:
        """
        Discover templates based on criteria with v2.0 FTS search
        
        Args:
            search_query: Optional search term for template content/name
            project_type: Filter by project type
            spec_phase: Filter by specification phase
            workflow_system: Filter by workflow system
            sort_by: Sort field (updated_at, created_at, title)
            limit: Maximum number of results
            
        Returns:
            Formatted template discovery report with v2.0 details
        """
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            # Build dynamic query for v2.0 documents table
            query_conditions = ["document_type = 'template'", "status = 'active'"]
            query_params = []
            
            # Add search conditions
            if search_query:
                query_conditions.append("(title LIKE ? OR content LIKE ?)")
                search_pattern = f"%{search_query}%"
                query_params.extend([search_pattern, search_pattern])
            
            if project_type:
                query_conditions.append("metadata LIKE ?")
                query_params.append(f'%"project_types":%"{project_type}"%')
            
            if spec_phase:
                query_conditions.append("metadata LIKE ?")
                query_params.append(f'%"spec_phase":"{spec_phase}"%')
            
            if workflow_system:
                query_conditions.append("metadata LIKE ?")
                query_params.append(f'%"workflow_system":"{workflow_system}"%')
            
            # Build final query
            base_query = f"""
            SELECT uuid, project_uuid, title, content, created_at, updated_at, metadata
            FROM documents 
            WHERE {' AND '.join(query_conditions)}
            ORDER BY {sort_by} DESC
            LIMIT ?
            """
            query_params.append(limit)
            
            results = await self._execute_query(base_query, tuple(query_params))
            
            if not results:
                filter_info = []
                if search_query: filter_info.append(f"search: '{search_query}'")
                if project_type: filter_info.append(f"type: {project_type}")
                if spec_phase: filter_info.append(f"phase: {spec_phase}")
                filter_text = f" ({', '.join(filter_info)})" if filter_info else ""
                
                return f"""🔍 **TEMPLATE DISCOVERY** (v2.0)

❌ No templates found{filter_text}.

**💡 Available Actions:**
• Use `store_template_spec()` to create templates
• Try broader search criteria
• Check `discover_templates()` without filters

**🚀 v2.0 Architecture:**
• Templates stored in documents table with document_type='template'
• Enhanced search across all projects with project_uuid support"""
            
            # Format discovery results
            discovery_report = f"""🔍 **TEMPLATE DISCOVERY RESULTS** (v2.0)

**📊 Found {len(results)} template(s)**"""
            
            if search_query:
                discovery_report += f" matching '{search_query}'"
            
            discovery_report += "\n"
            
            for i, template_data in enumerate(results, 1):
                uuid_val, project_uuid, title, content, created_at, updated_at, metadata_json = template_data
                
                # Parse metadata
                try:
                    metadata = json.loads(metadata_json) if metadata_json else {}
                except:
                    metadata = {}
                
                template_version = metadata.get('template_version', '1.0')
                description = metadata.get('description', 'No description')
                project_types = ', '.join(metadata.get('project_types', ['general']))
                workflow_system = metadata.get('workflow_system', 'unknown')
                
                # Format template entry
                content_preview = content[:150] + "..." if len(content) > 150 else content
                
                discovery_report += f"""

**{i}. {title}** (v{template_version})
   🆔 UUID: {uuid_val[:8]}... | 📁 Project: {project_uuid[:8]}...
   📅 Updated: {updated_at} | 🏷️ Types: {project_types}
   🔧 Workflow: {workflow_system}
   📝 Description: {description}
   
   **Content Preview:**
   {content_preview}"""
                
                if i >= 5:  # Limit detailed display to first 5
                    remaining = len(results) - 5
                    if remaining > 0:
                        discovery_report += f"\n\n... and {remaining} more templates"
                    break
            
            discovery_report += f"""

**🚀 v2.0 Features:**
• ✅ Enhanced template metadata with cross-project compatibility
• ✅ Full-text search across template content and descriptions
• ✅ Project UUID support for template sharing
• ✅ Future-proof storage in unified documents table

**💡 Usage:**
• Copy template UUIDs for direct reference
• Use broader/narrower search terms to refine results
• Templates are searchable across all projects"""
            
            return discovery_report
            
        except Exception as e:
            logger.error(f"Error discovering templates: {e}")
            return f"❌ Error discovering templates: {str(e)}"
    
    async def _find_existing_template(self, template_name: str, project_uuid: str) -> Optional[Dict]:
        """Find existing template by name in v2.0 documents table"""
        try:
            query = """
            SELECT uuid, title, updated_at 
            FROM documents 
            WHERE title = ? AND project_uuid = ? AND document_type = 'template' AND status = 'active'
            LIMIT 1
            """
            
            result = await self._execute_query(query, (template_name, project_uuid))
            if result:
                uuid_val, title, updated_at = result[0]
                return {
                    'uuid': uuid_val,
                    'title': title,
                    'updated_at': updated_at
                }
            return None
            
        except Exception as e:
            logger.error(f"Error finding existing template: {e}")
            return None
    
    async def get_template_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive template statistics from v2.0 documents table
        
        Returns:
            Dictionary with template statistics and metadata
        """
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return {'error': 'Memory Bank not initialized'}
            
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', '')
            
            # Get template statistics from documents table
            stats_query = """
            SELECT 
                COUNT(*) as total_templates,
                COUNT(CASE WHEN created_at >= date('now', '-7 days') THEN 1 END) as recent_templates,
                AVG(LENGTH(content)) as avg_content_length,
                MAX(updated_at) as latest_update
            FROM documents 
            WHERE document_type = 'template' AND project_uuid = ? AND status = 'active'
            """
            
            result = await self._execute_query(stats_query, (project_uuid,))
            
            if result:
                total, recent, avg_length, latest = result[0]
                return {
                    'total_templates': total or 0,
                    'recent_templates': recent or 0,
                    'avg_content_length': int(avg_length) if avg_length else 0,
                    'latest_update': latest,
                    'project_uuid': project_uuid,
                    'architecture_version': '2.0'
                }
            else:
                return {
                    'total_templates': 0,
                    'recent_templates': 0,
                    'avg_content_length': 0,
                    'latest_update': None,
                    'project_uuid': project_uuid,
                    'architecture_version': '2.0'
                }
                
        except Exception as e:
            logger.error(f"Error getting template statistics: {e}")
            return {'error': str(e)}
