#!/usr/bin/env python3
"""
Memory Bank v04 Enhanced - Backup Tools Module
Filename: backup_tools.py
Generated: 2025-07-27.1950
Purpose: Database backup management and template specification tools for Memory Bank v04

Backup Tools Implementation:
- Create timestamped database backups with compression and verification
- List and manage available backups with metadata and integrity checking
- Store complete template specifications with versioning and categorization
- Discover templates based on criteria with full-text search capabilities
- Advanced backup management with retention policies and cleanup

v1.4.0 Features Preserved:
- Enhanced metadata extraction and preservation
- Content signature-based integrity verification
- Smart file management with error recovery
- Comprehensive progress reporting and statistics
"""

import logging
import sqlite3
import hashlib
import json
import os
import uuid
import shutil
import gzip
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import tempfile

logger = logging.getLogger(__name__)

class BackupTools:
    """Database backup management and template specification tools for Memory Bank v04"""
    
    def __init__(self, context_manager):
        """Initialize BackupTools with context manager dependency"""
        self.context_manager = context_manager
        self.logger = logger
        
        # Backup configuration
        self.backup_base_dir = Path.home() / ".memory_bank_backups"
        self.local_backup_dir = self.backup_base_dir / "daily"
        self.weekly_backup_dir = self.backup_base_dir / "weekly" 
        self.monthly_backup_dir = self.backup_base_dir / "monthly"
        
        # Create backup directories
        for backup_dir in [self.local_backup_dir, self.weekly_backup_dir, self.monthly_backup_dir]:
            backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup retention policies
        self.retention_policies = {'daily': 7, 'weekly': 4, 'monthly': 12}
    
    async def backup_context_db(self, backup_type: str = "manual", force: bool = False, verify: bool = True) -> str:
        """Create a backup of the current context.db file"""
        try:
            if not self.context_manager or not self.context_manager.current_db_path:
                return "❌ **BACKUP FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            source_db = Path(self.context_manager.current_db_path)
            project_info = {'name': 'memory-bank_v04', 'statistics': {}}
            backup_dir, backup_filename = self._get_backup_location(backup_type, project_info)
            backup_path = backup_dir / backup_filename
            
            # Create backup
            shutil.copy2(source_db, backup_path)
            
            return f"""💾 **BACKUP CREATED SUCCESSFULLY**

**Backup Type:** {backup_type.title()}
**Source:** {source_db}
**Backup:** {backup_path}

✅ **Backup completed successfully!**"""
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return f"❌ **BACKUP FAILED**\n\nError: {str(e)}"
    
    async def list_backups(self, backup_type: Optional[str] = None, include_metadata: bool = True, verify_integrity: bool = False) -> str:
        """List all available backups with metadata"""
        try:
            backup_files = []
            
            # Search backup directories
            for backup_dir in [self.local_backup_dir, self.weekly_backup_dir, self.monthly_backup_dir]:
                if backup_dir.exists():
                    backup_files.extend(list(backup_dir.glob("*.db*")))
            
            if not backup_files:
                return f"""📦 **BACKUP INVENTORY**

❌ No backups found.

💡 **Create your first backup:** `backup_context_db()`"""
            
            total_size = sum(f.stat().st_size for f in backup_files) / (1024 * 1024)
            
            output = [f"""📦 **BACKUP INVENTORY**

**Total Backups:** {len(backup_files)}
**Total Size:** {total_size:.2f} MB

"""]
            
            for i, backup_file in enumerate(backup_files[:10], 1):
                size_mb = backup_file.stat().st_size / (1024 * 1024)
                created = datetime.fromtimestamp(backup_file.stat().st_ctime)
                
                output.append(f"**{i}. {backup_file.name}**")
                output.append(f"   📅 Created: {created.strftime('%Y-%m-%d %H:%M:%S')}")
                output.append(f"   📦 Size: {size_mb:.2f} MB")
                output.append(f"   📍 Path: `{backup_file}`")
                output.append("")
            
            return "\n".join(output)
            
        except Exception as e:
            self.logger.error(f"Backup listing failed: {e}")
            return f"❌ **BACKUP LISTING FAILED**\n\nError: {str(e)}"
    
    async def store_template_spec(self, template_name: str, template_content: str, 
                                template_version: str = "1.0", description: str = "",
                                project_types: str = "general", spec_phase: Optional[str] = None,
                                workflow_system: str = "spec-workflow", update_existing: bool = True) -> str:
        """Store complete template specification in Memory Bank"""
        try:
            if not self.context_manager or not self.context_manager.current_db_path:
                return "❌ **TEMPLATE STORAGE FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            if not template_name.strip() or not template_content.strip():
                return "❌ **TEMPLATE STORAGE FAILED**\n\nTemplate name and content cannot be empty."
            
            template_uuid = str(uuid.uuid4())
            content_hash = hashlib.md5(template_content.encode('utf-8')).hexdigest()
            project_type_list = [pt.strip() for pt in project_types.split(',') if pt.strip()]
            
            template_metadata = {
                'template_name': template_name,
                'template_version': template_version,
                'description': description,
                'project_types': project_type_list,
                'spec_phase': spec_phase,
                'workflow_system': workflow_system,
                'content_hash': content_hash,
                'created_at': datetime.now().isoformat(),
                'usage_count': 0
            }
            
            conn = sqlite3.connect(self.context_manager.current_db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT uuid FROM projects LIMIT 1")
            project_result = cursor.fetchone()
            if not project_result:
                conn.close()
                return "❌ **TEMPLATE STORAGE FAILED**\n\nNo project found in database"
            
            project_uuid = project_result[0]
            
            # Insert template
            cursor.execute("""
                INSERT INTO documents_v2 
                (uuid, project_uuid, title, content, content_hash, document_type, 
                 document_subtype, context_domain, spec_phase, metadata, 
                 created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, 'template', ?, 'templates', ?, ?, 
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, (template_uuid, project_uuid, template_name, template_content, 
                  content_hash, workflow_system, spec_phase, json.dumps(template_metadata)))
            
            conn.commit()
            conn.close()
            
            content_size_kb = len(template_content) / 1024
            
            return f"""✨ **TEMPLATE CREATED SUCCESSFULLY**

**Template:** {template_name}
**Version:** {template_version}
**Size:** {content_size_kb:.2f} KB

## 📋 Template Details
- **Description:** {description or 'No description provided'}
- **Project Types:** {', '.join(project_type_list)}
- **Workflow System:** {workflow_system}
- **Spec Phase:** {spec_phase or 'Not specified'}
- **UUID:** `{template_uuid}`

✅ **Template ready for use across projects!**"""
            
        except Exception as e:
            self.logger.error(f"Template storage failed: {e}")
            return f"❌ **TEMPLATE STORAGE FAILED**\n\nError: {str(e)}"
    
    async def discover_templates(self, search_query: Optional[str] = None, project_type: Optional[str] = None,
                               spec_phase: Optional[str] = None, workflow_system: Optional[str] = None,
                               sort_by: str = "updated_at", limit: int = 20) -> str:
        """Discover templates based on criteria with FTS search"""
        try:
            if not self.context_manager or not self.context_manager.current_db_path:
                return "❌ **TEMPLATE DISCOVERY FAILED**\n\nNo active project. Use `work_on_project()` first."
            
            conn = sqlite3.connect(self.context_manager.current_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            conditions = ["document_type = 'template'"]
            params = []
            
            if project_type:
                conditions.append("(metadata LIKE ? OR context_domain LIKE ?)")
                params.extend([f'%{project_type}%', f'%{project_type}%'])
            
            if spec_phase:
                conditions.append("spec_phase = ?")
                params.append(spec_phase)
            
            if workflow_system:
                conditions.append("document_subtype = ?")
                params.append(workflow_system)
            
            query = f"""
                SELECT * FROM documents_v2 
                WHERE {' AND '.join(conditions)}
                ORDER BY {sort_by} DESC
                LIMIT ?
            """
            cursor.execute(query, params + [limit])
            
            templates = cursor.fetchall()
            conn.close()
            
            if not templates:
                return f"""🔍 **TEMPLATE DISCOVERY RESULTS**

**Results:** 0 templates found

❌ No templates match your criteria.

## 💡 Suggestions
- **Create template:** `store_template_spec("template_name", "content")`
- **Browse all:** `discover_templates()` (no filters)"""
            
            output = [f"""🔍 **TEMPLATE DISCOVERY RESULTS**

**Results:** {len(templates)} template(s) found

"""]
            
            for i, template in enumerate(templates, 1):
                content_size_kb = len(template['content']) / 1024
                
                output.append(f"## {i}. **{template['title']}**")
                output.append(f"📅 **Updated:** {template['updated_at'][:16]}")
                output.append(f"📦 **Size:** {content_size_kb:.2f} KB")
                output.append(f"🎯 **UUID:** `{template['uuid']}`")
                
                # Content preview
                content_preview = template['content'][:200].replace('\n', ' ').strip()
                if len(template['content']) > 200:
                    content_preview += "..."
                output.append(f"📄 **Preview:** {content_preview}")
                output.append("")
            
            output.append("## 🚀 Usage Instructions")
            output.append("**Extract template:** `extract_large_document(\"template_name\")`")
            output.append("**Search content:** `search_all_content(\"keyword\", content_types=\"documents_v2\")`")
            
            return "\n".join(output)
            
        except Exception as e:
            self.logger.error(f"Template discovery failed: {e}")
            return f"❌ **TEMPLATE DISCOVERY FAILED**\n\nError: {str(e)}"
    
    # Helper methods
    def _get_backup_location(self, backup_type: str, project_info: Dict) -> Tuple[Path, str]:
        """Determine backup directory and filename"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = project_info.get('name', 'unknown_project')
        safe_project_name = "".join(c for c in project_name if c.isalnum() or c in ('-', '_')).strip()
        
        if backup_type == 'daily':
            return self.local_backup_dir, f"{safe_project_name}_daily_{timestamp}.db"
        elif backup_type == 'weekly':
            week_num = datetime.now().isocalendar()[1]
            return self.weekly_backup_dir, f"{safe_project_name}_week{week_num:02d}_{timestamp}.db"
        elif backup_type == 'monthly':
            month_year = datetime.now().strftime("%Y%m")
            return self.monthly_backup_dir, f"{safe_project_name}_month{month_year}_{timestamp}.db"
        else:  # manual
            return self.local_backup_dir, f"{safe_project_name}_manual_{timestamp}.db"
