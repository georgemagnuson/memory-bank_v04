"""
Template Specification System - Phase 1 Completion Feature

Filename: template_spec_manager.py
Generated: 2025-07-22.1721
Purpose: Template specification storage and management for Memory Bank with full template content and metadata

Features:
- Store complete template content and metadata in documents_v2
- Track workflow system (spec-workflow, future systems)
- Template discovery via FTS and semantic search
- Template versioning and synchronization support
- Documentation record of complete processes
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class TemplateSpecManager:
    """
    Template specification manager for Memory Bank
    
    Stores complete template content and metadata as documentation records
    Enables template discovery, versioning, and cross-system compatibility
    """
    
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.template_document_type = 'template_spec'
    
    async def store_template_spec(
        self,
        template_name: str,
        template_content: str,
        template_metadata: Dict[str, Any],
        workflow_system: str = 'spec-workflow',
        project_uuid: str = None,
        spec_phase: str = None,
        update_existing: bool = True
    ) -> Dict[str, Any]:
        """
        Store complete template specification in Memory Bank
        
        Args:
            template_name: Unique name for the template
            template_content: Full template content with variables
            template_metadata: Template configuration and metadata
            workflow_system: System that owns this template (spec-workflow, etc.)
            project_uuid: Optional project association
            spec_phase: Phase this template applies to (requirements, design, etc.)
            update_existing: Whether to update if template already exists
            
        Returns:
            Dict with storage result and template details
        """
        try:
            # Validate inputs
            if not template_name or not template_content:
                return {
                    'status': 'error',
                    'error': 'Template name and content are required'
                }
            
            # Prepare enhanced metadata
            enhanced_metadata = {
                'workflow_system': workflow_system,
                'template_version': template_metadata.get('template_version', '1.0'),
                'project_types': template_metadata.get('project_types', ['general']),
                'variables': template_metadata.get('variables', []),
                'description': template_metadata.get('description', ''),
                'usage_count': template_metadata.get('usage_count', 0),
                'success_rating': template_metadata.get('success_rating', 5),
                'created_date': datetime.now().isoformat(),
                'last_updated': datetime.now().isoformat(),
                'content_hash': self._generate_content_hash(template_content),
                'original_metadata': template_metadata
            }
            
            # Check if template already exists
            existing_template = await self.find_template_by_name(template_name, workflow_system)
            
            if existing_template and not update_existing:
                return {
                    'status': 'exists',
                    'message': f'Template {template_name} already exists',
                    'existing_template_uuid': existing_template['uuid']
                }
            
            # Generate document title and content
            title = f'{workflow_system} Template: {template_name}'
            if spec_phase:
                title += f' ({spec_phase})'
            
            # Store in documents_v2
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                if existing_template:
                    # Update existing template
                    enhanced_metadata['created_date'] = existing_template['metadata'].get('created_date')
                    enhanced_metadata['usage_count'] = existing_template['metadata'].get('usage_count', 0)
                    
                    cursor.execute("""
                        UPDATE documents_v2 
                        SET content = ?, metadata = ?, updated_at = CURRENT_TIMESTAMP,
                            title = ?, spec_phase = ?, change_reason = ?
                        WHERE uuid = ?
                    """, (
                        template_content,
                        json.dumps(enhanced_metadata),
                        title,
                        spec_phase,
                        'Template content updated',
                        existing_template['uuid']
                    ))
                    
                    template_uuid = existing_template['uuid']
                    action = 'updated'
                    
                else:
                    # Create new template
                    import uuid
                    template_uuid = str(uuid.uuid4())
                    
                    cursor.execute("""
                        INSERT INTO documents_v2 (
                            uuid, project_uuid, title, content, content_hash,
                            document_type, document_subtype, context_domain,
                            spec_name, spec_phase, metadata, importance_score,
                            source_type, source_reference, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (
                        template_uuid,
                        project_uuid,
                        title,
                        template_content,
                        enhanced_metadata['content_hash'],
                        self.template_document_type,
                        workflow_system,
                        'spec_workflow',
                        template_name,
                        spec_phase,
                        json.dumps(enhanced_metadata),
                        8,  # High importance for templates
                        'workflow_system',
                        workflow_system
                    ))
                    
                    action = 'created'
                
                conn.commit()
            
            return {
                'status': 'success',
                'action': action,
                'template_uuid': template_uuid,
                'template_name': template_name,
                'workflow_system': workflow_system,
                'spec_phase': spec_phase,
                'content_size': len(template_content),
                'metadata': enhanced_metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to store template spec: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }    
    async def find_template_by_name(self, template_name: str, workflow_system: str = None) -> Optional[Dict]:
        """Find template by name and optionally workflow system"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                if workflow_system:
                    cursor.execute("""
                        SELECT uuid, title, content, metadata, spec_phase, created_at, updated_at
                        FROM documents_v2
                        WHERE document_type = ? AND spec_name = ? AND document_subtype = ?
                        ORDER BY updated_at DESC
                        LIMIT 1
                    """, (self.template_document_type, template_name, workflow_system))
                else:
                    cursor.execute("""
                        SELECT uuid, title, content, metadata, spec_phase, created_at, updated_at
                        FROM documents_v2
                        WHERE document_type = ? AND spec_name = ?
                        ORDER BY updated_at DESC
                        LIMIT 1
                    """, (self.template_document_type, template_name))
                
                row = cursor.fetchone()
                if row:
                    metadata = json.loads(row[3]) if row[3] else {}
                    return {
                        'uuid': row[0],
                        'title': row[1],
                        'content': row[2],
                        'metadata': metadata,
                        'spec_phase': row[4],
                        'created_at': row[5],
                        'updated_at': row[6]
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to find template: {e}")
            return None
    
    async def discover_templates(
        self,
        workflow_system: str = None,
        spec_phase: str = None,
        project_type: str = None,
        search_query: str = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Discover templates based on various criteria
        
        Args:
            workflow_system: Filter by workflow system
            spec_phase: Filter by spec phase
            project_type: Filter by project type
            search_query: FTS search in content and metadata
            limit: Maximum number of results
            
        Returns:
            List of template specifications matching criteria
        """
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Build query conditions
                conditions = ["document_type = ?"]
                params = [self.template_document_type]
                
                if workflow_system:
                    conditions.append("document_subtype = ?")
                    params.append(workflow_system)
                
                if spec_phase:
                    conditions.append("spec_phase = ?")
                    params.append(spec_phase)
                
                if project_type:
                    conditions.append("json_extract(metadata, '$.project_types') LIKE ?")
                    params.append(f'%{project_type}%')
                
                # Base query
                if search_query:
                    # Use FTS search
                    query = f"""
                        SELECT d.uuid, d.title, d.content, d.metadata, d.spec_phase, 
                               d.document_subtype, d.created_at, d.updated_at,
                               d.spec_name, d.importance_score
                        FROM documents_v2 d
                        JOIN documents_v2_fts fts ON d.uuid = fts.uuid
                        WHERE fts MATCH ? AND {' AND '.join(conditions)}
                        ORDER BY bm25(fts) ASC
                        LIMIT ?
                    """
                    params = [search_query] + params + [limit]
                else:
                    # Regular query
                    query = f"""
                        SELECT uuid, title, content, metadata, spec_phase,
                               document_subtype, created_at, updated_at,
                               spec_name, importance_score
                        FROM documents_v2
                        WHERE {' AND '.join(conditions)}
                        ORDER BY updated_at DESC
                        LIMIT ?
                    """
                    params.append(limit)
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                templates = []
                for row in rows:
                    try:
                        metadata = json.loads(row[3]) if row[3] else {}
                        template = {
                            'uuid': row[0],
                            'title': row[1],
                            'content': row[2],
                            'metadata': metadata,
                            'spec_phase': row[4],
                            'workflow_system': row[5],
                            'created_at': row[6],
                            'updated_at': row[7],
                            'template_name': row[8],
                            'importance_score': row[9],
                            'content_preview': row[2][:200] + '...' if len(row[2]) > 200 else row[2],
                            'variable_count': len(metadata.get('variables', [])),
                            'project_types': metadata.get('project_types', []),
                            'template_version': metadata.get('template_version', '1.0'),
                            'usage_count': metadata.get('usage_count', 0),
                            'success_rating': metadata.get('success_rating', 5)
                        }
                        templates.append(template)
                    except Exception as e:
                        logger.warning(f"Error processing template row: {e}")
                        continue
                
                return templates
                
        except Exception as e:
            logger.error(f"Failed to discover templates: {e}")
            return []    
    async def get_template_spec(self, template_uuid: str) -> Optional[Dict]:
        """Get complete template specification by UUID"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT uuid, title, content, metadata, spec_phase, document_subtype,
                           created_at, updated_at, spec_name, importance_score, content_hash
                    FROM documents_v2
                    WHERE uuid = ? AND document_type = ?
                """, (template_uuid, self.template_document_type))
                
                row = cursor.fetchone()
                if not row:
                    return None
                
                metadata = json.loads(row[3]) if row[3] else {}
                
                return {
                    'uuid': row[0],
                    'title': row[1],
                    'content': row[2],
                    'metadata': metadata,
                    'spec_phase': row[4],
                    'workflow_system': row[5],
                    'created_at': row[6],
                    'updated_at': row[7],
                    'template_name': row[8],
                    'importance_score': row[9],
                    'content_hash': row[10],
                    'variables': metadata.get('variables', []),
                    'project_types': metadata.get('project_types', []),
                    'description': metadata.get('description', ''),
                    'usage_count': metadata.get('usage_count', 0),
                    'success_rating': metadata.get('success_rating', 5),
                    'template_version': metadata.get('template_version', '1.0'),
                    'content_size': len(row[2])
                }
                
        except Exception as e:
            logger.error(f"Failed to get template spec: {e}")
            return None
    
    async def update_template_usage(self, template_uuid: str, success_rating: float = None) -> Dict:
        """Update template usage statistics"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Get current metadata
                cursor.execute("""
                    SELECT metadata FROM documents_v2
                    WHERE uuid = ? AND document_type = ?
                """, (template_uuid, self.template_document_type))
                
                row = cursor.fetchone()
                if not row:
                    return {
                        'status': 'error',
                        'error': 'Template not found'
                    }
                
                metadata = json.loads(row[0]) if row[0] else {}
                
                # Update usage statistics
                metadata['usage_count'] = metadata.get('usage_count', 0) + 1
                metadata['last_used'] = datetime.now().isoformat()
                
                if success_rating is not None:
                    # Update running average of success rating
                    current_rating = metadata.get('success_rating', 5)
                    usage_count = metadata['usage_count']
                    
                    # Weighted average with more weight on recent usage
                    new_rating = ((current_rating * (usage_count - 1)) + success_rating) / usage_count
                    metadata['success_rating'] = round(new_rating, 2)
                
                # Update database
                cursor.execute("""
                    UPDATE documents_v2
                    SET metadata = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE uuid = ?
                """, (json.dumps(metadata), template_uuid))
                
                conn.commit()
                
                return {
                    'status': 'success',
                    'usage_count': metadata['usage_count'],
                    'success_rating': metadata.get('success_rating', 5)
                }
                
        except Exception as e:
            logger.error(f"Failed to update template usage: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def list_workflow_systems(self) -> List[Dict]:
        """List all workflow systems that have templates stored"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT document_subtype, COUNT(*) as template_count,
                           MAX(updated_at) as last_updated
                    FROM documents_v2
                    WHERE document_type = ?
                    GROUP BY document_subtype
                    ORDER BY template_count DESC
                """, (self.template_document_type,))
                
                systems = []
                for row in cursor.fetchall():
                    systems.append({
                        'workflow_system': row[0],
                        'template_count': row[1],
                        'last_updated': row[2]
                    })
                
                return systems
                
        except Exception as e:
            logger.error(f"Failed to list workflow systems: {e}")
            return []
    
    async def get_template_statistics(self) -> Dict:
        """Get comprehensive template system statistics"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Total template count
                cursor.execute("""
                    SELECT COUNT(*) FROM documents_v2
                    WHERE document_type = ?
                """, (self.template_document_type,))
                total_templates = cursor.fetchone()[0]
                
                # Templates by workflow system
                cursor.execute("""
                    SELECT document_subtype, COUNT(*) 
                    FROM documents_v2
                    WHERE document_type = ?
                    GROUP BY document_subtype
                """, (self.template_document_type,))
                by_system = dict(cursor.fetchall())
                
                # Templates by spec phase
                cursor.execute("""
                    SELECT spec_phase, COUNT(*)
                    FROM documents_v2
                    WHERE document_type = ? AND spec_phase IS NOT NULL
                    GROUP BY spec_phase
                """, (self.template_document_type,))
                by_phase = dict(cursor.fetchall())
                
                # Usage statistics
                cursor.execute("""
                    SELECT 
                        AVG(CAST(json_extract(metadata, '$.usage_count') AS INTEGER)) as avg_usage,
                        AVG(CAST(json_extract(metadata, '$.success_rating') AS REAL)) as avg_rating,
                        MAX(CAST(json_extract(metadata, '$.usage_count') AS INTEGER)) as max_usage
                    FROM documents_v2
                    WHERE document_type = ? AND metadata IS NOT NULL
                """, (self.template_document_type,))
                usage_stats = cursor.fetchone()
                
                return {
                    'total_templates': total_templates,
                    'by_workflow_system': by_system,
                    'by_spec_phase': by_phase,
                    'usage_statistics': {
                        'average_usage_count': round(usage_stats[0] or 0, 2),
                        'average_success_rating': round(usage_stats[1] or 5, 2),
                        'highest_usage_count': usage_stats[2] or 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Failed to get template statistics: {e}")
            return {}
    
    def _generate_content_hash(self, content: str) -> str:
        """Generate hash of template content for change detection"""
        import hashlib
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    async def validate_template_content(self, template_content: str) -> Dict:
        """Validate template content and extract variables"""
        try:
            import re
            
            # Extract variables ({{variable_name}} format)
            variable_pattern = r'\{\{([^}]+)\}\}'
            variables = re.findall(variable_pattern, template_content)
            
            # Remove duplicates and sort
            unique_variables = sorted(list(set(variables)))
            
            # Check for conditional blocks
            conditional_pattern = r'\{\{#if\s+([^}]+)\}\}(.*?)\{\{/if\}\}'
            conditionals = re.findall(conditional_pattern, template_content, re.DOTALL)
            
            # Basic validation
            issues = []
            
            # Check for unmatched braces
            open_braces = template_content.count('{{')
            close_braces = template_content.count('}}')
            if open_braces != close_braces:
                issues.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
            
            # Check for empty variables
            if '{{}}' in template_content:
                issues.append("Empty variable placeholders found")
            
            return {
                'status': 'valid' if not issues else 'warning',
                'variables': unique_variables,
                'variable_count': len(unique_variables),
                'conditionals': len(conditionals),
                'issues': issues,
                'content_length': len(template_content),
                'line_count': template_content.count('\n') + 1
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
