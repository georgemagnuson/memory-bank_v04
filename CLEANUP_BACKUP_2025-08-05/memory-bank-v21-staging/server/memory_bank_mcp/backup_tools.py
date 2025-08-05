#!/usr/bin/env python3
"""
server/memory_bank_mcp/backup_tools.py
Generated: 2025-07-30.1927
Purpose: Database backup management and template specification tools for Memory Bank v2.0
         Clean modular architecture with enhanced v2.0 features

v2.0 Architecture Benefits:
- Modular components: BackupManager, TemplateManager
- Enhanced backup metadata with project_uuid information
- Templates stored in documents table with document_type='template'
- Future-proof backup and template management aligned with unified documents architecture
"""

import logging
from typing import Optional, List, Dict, Any

# Import v2.0 modular components (DXT compatible)
from .backup_tools_modules import BackupManager, TemplateManager

logger = logging.getLogger(__name__)

class BackupTools:
    """
    Database backup management and template specification tools with v2.0 modular architecture
    
    Features:
    - Enhanced database backup creation, listing, and management
    - Template specification storage in documents table with document_type='template'
    - Cross-project template discovery with project_uuid support
    - Future-proof design aligned with v2.0 unified documents architecture
    """
    
    def __init__(self, context_manager):
        """Initialize BackupTools with v2.0 modular components"""
        self.context_manager = context_manager
        
        # Initialize v2.0 modular components
        self.backup_manager = BackupManager(context_manager)
        self.template_manager = TemplateManager(context_manager)
    
    # Backup Management Methods (delegated to BackupManager)
    
    async def backup_context_db(self, backup_type: str = "manual", force: bool = False, 
                               verify: bool = True) -> str:
        """Create a backup of the current context.db file with v2.0 enhancements"""
        return await self.backup_manager.backup_context_db(backup_type, force, verify)
    
    async def list_backups(self, backup_type: Optional[str] = None, include_metadata: bool = True, 
                          verify_integrity: bool = False) -> str:
        """List all available backups with v2.0 enhanced metadata"""
        return await self.backup_manager.list_backups(backup_type, include_metadata, verify_integrity)
    
    # Template Management Methods (delegated to TemplateManager)
    
    async def store_template_spec(self, template_name: str, template_content: str, 
                                 template_version: str = "1.0", description: str = "",
                                 project_types: str = "general", spec_phase: Optional[str] = None,
                                 workflow_system: str = "spec-workflow", update_existing: bool = True) -> str:
        """Store complete template specification in v2.0 documents table"""
        return await self.template_manager.store_template_spec(
            template_name, template_content, template_version, description,
            project_types, spec_phase, workflow_system, update_existing
        )
    
    async def discover_templates(self, search_query: Optional[str] = None, project_type: Optional[str] = None,
                                spec_phase: Optional[str] = None, workflow_system: Optional[str] = None,
                                sort_by: str = "updated_at", limit: int = 20) -> str:
        """Discover templates based on criteria with v2.0 FTS search"""
        return await self.template_manager.discover_templates(
            search_query, project_type, spec_phase, workflow_system, sort_by, limit
        )
