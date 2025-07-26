# Phase 1 Completion Tools Integration for Memory Bank v04
# Add these tools to main.py by importing and registering them

import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Import the Phase 1 managers
from .backup_manager import BackupManager
from .template_spec_manager import TemplateSpecManager

# Global managers for Phase 1 features  
backup_manager = None
template_spec_manager = None

def initialize_phase1_managers(context_manager):
    """Initialize Phase 1 feature managers when context is available"""
    global backup_manager, template_spec_manager
    
    if context_manager and context_manager.is_initialized():
        try:
            backup_manager = BackupManager(str(context_manager.project_path))
            template_spec_manager = TemplateSpecManager(str(context_manager.database_path))
            
            logger.info("Phase 1 completion managers initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Phase 1 managers: {e}")
            return False
    return False

# Tool functions that can be added to the FastMCP server
async def backup_context_db_tool(context_manager, backup_type="manual", force=False, verify=True):
    """Tool function for creating backups"""
    global backup_manager
    
    if not context_manager or not context_manager.is_initialized():
        return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
    
    if not backup_manager:
        if not initialize_phase1_managers(context_manager):
            return "❌ Failed to initialize backup system."
    
    try:
        result = await backup_manager.create_backup(backup_type, force)
        
        if verify and result.get('status') == 'success':
            backup_path = result['backup_path']
            verification = backup_manager._verify_backup_integrity(Path(backup_path))
            result['verification_passed'] = verification
            
            if not verification:
                result['status'] = 'warning'
                result['warning'] = 'Backup created but verification failed'
        
        await context_manager.auto_save_context(f"Created {backup_type} backup")
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Backup creation failed: {e}")
        return json.dumps({'status': 'error', 'error': str(e)}, indent=2)

async def list_backups_tool(context_manager, backup_type=None, include_metadata=True, verify_integrity=False):
    """Tool function for listing backups"""
    global backup_manager
    
    if not context_manager or not context_manager.is_initialized():
        return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
    
    if not backup_manager:
        if not initialize_phase1_managers(context_manager):
            return "❌ Failed to initialize backup system."
    
    try:
        backups = await backup_manager.list_backups()
        
        if backup_type:
            backups = {backup_type: backups.get(backup_type, [])}
        
        if verify_integrity:
            for btype, backup_list in backups.items():
                for backup in backup_list:
                    backup['integrity_verified'] = backup_manager._verify_backup_integrity(Path(backup['path']))
        
        total_backups = sum(len(backup_list) for backup_list in backups.values())
        total_size = sum(backup['size_bytes'] for backup_list in backups.values() for backup in backup_list)
        
        result = {
            'status': 'success',
            'backups': backups,
            'summary': {
                'total_backups': total_backups,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / 1024 / 1024, 2),
                'backup_types_found': list(backups.keys())
            },
            'retention_policies': backup_manager.retention_policies
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Backup listing failed: {e}")
        return json.dumps({'status': 'error', 'error': str(e)}, indent=2)

async def store_template_spec_tool(context_manager, template_name, template_content, workflow_system="spec-workflow", 
                                  spec_phase=None, project_types="general", description="", 
                                  template_version="1.0", update_existing=True):
    """Tool function for storing template specifications"""
    global template_spec_manager
    
    if not context_manager or not context_manager.is_initialized():
        return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
    
    if not template_spec_manager:
        if not initialize_phase1_managers(context_manager):
            return "❌ Failed to initialize template system."
    
    try:
        project_types_list = [pt.strip() for pt in project_types.split(',') if pt.strip()]
        
        validation = await template_spec_manager.validate_template_content(template_content)
        if validation['status'] == 'error':
            return json.dumps({
                'status': 'error',
                'error': f"Template validation failed: {validation['error']}"
            }, indent=2)
        
        template_metadata = {
            'template_version': template_version,
            'project_types': project_types_list,
            'variables': [],
            'description': description,
            'usage_count': 0,
            'success_rating': 5.0,
            'validation_results': validation
        }
        
        if validation.get('variables'):
            template_metadata['variables'] = [
                {'name': var, 'required': True, 'type': 'string', 'description': f'Variable: {var}'}
                for var in validation['variables']
            ]
        
        result = await template_spec_manager.store_template_spec(
            template_name=template_name,
            template_content=template_content,
            template_metadata=template_metadata,
            workflow_system=workflow_system,
            project_uuid=str(context_manager.database.project_uuid),
            spec_phase=spec_phase,
            update_existing=update_existing
        )
        
        if result['status'] == 'success':
            result['validation'] = validation
            result['auto_extracted_variables'] = len(validation.get('variables', []))
            await context_manager.auto_save_context(f"Stored template specification: {template_name}")
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Template storage failed: {e}")
        return json.dumps({'status': 'error', 'error': str(e)}, indent=2)

async def phase1_completion_status_tool(context_manager):
    """Tool function for checking Phase 1 completion status"""
    global backup_manager, template_spec_manager
    
    if not context_manager or not context_manager.is_initialized():
        return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
    
    try:
        initialize_phase1_managers(context_manager)
        
        import sqlite3
        with sqlite3.connect(context_manager.database_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("PRAGMA table_info(documents_v2)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            spec_workflow_fields = ['spec_name', 'spec_phase', 'spec_status', 'task_id', 'parent_spec_uuid']
            schema_complete = all(field in columns for field in spec_workflow_fields)
            
            cursor.execute("SELECT COUNT(*) FROM semantic_equivalents WHERE context_domain = 'spec_workflow'")
            semantic_mappings_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM documents_v2 WHERE document_type = 'template_spec'")
            template_specs_count = cursor.fetchone()[0]
        
        phase1_items = {
            'enhanced_documents_v2_schema': {
                'status': 'complete' if schema_complete else 'incomplete',
                'details': f"Required fields present: {schema_complete}",
                'required_fields': spec_workflow_fields
            },
            'semantic_mappings': {
                'status': 'complete' if semantic_mappings_count >= 6 else 'incomplete',
                'details': f"{semantic_mappings_count} spec workflow semantic mappings found",
                'target': '6+ semantic mappings for spec workflow'
            },
            'template_specification_support': {
                'status': 'complete' if template_spec_manager is not None else 'incomplete',
                'details': f"{template_specs_count} template specifications stored",
                'description': 'Template storage and management system operational'
            },
            'backup_system': {
                'status': 'complete' if backup_manager is not None else 'incomplete',
                'details': 'Comprehensive backup system with local and centralized storage',
                'backup_system_initialized': backup_manager is not None
            }
        }
        
        completed_items = sum(1 for item in phase1_items.values() if item['status'] == 'complete')
        total_items = len(phase1_items)
        completion_percentage = (completed_items / total_items) * 100
        
        result = {
            'status': 'success',
            'phase1_completion': {
                'overall_status': 'complete' if completion_percentage == 100 else 'in_progress',
                'completion_percentage': completion_percentage,
                'completed_items': completed_items,
                'total_items': total_items,
                'items': phase1_items
            },
            'next_steps': [
                'Complete SPEC-WORKFLOW MCP development',
                'Implement template processing engine in SPEC-WORKFLOW',
                'Test full integration between Memory Bank and SPEC-WORKFLOW',
                'Begin Phase 2: Core Integration features'
            ] if completion_percentage == 100 else [
                'Complete remaining Phase 1 items',
                'Test all Phase 1 features',
                'Verify integration readiness'
            ]
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        logger.error(f"Phase 1 status check failed: {e}")
        return json.dumps({'status': 'error', 'error': str(e)}, indent=2)
