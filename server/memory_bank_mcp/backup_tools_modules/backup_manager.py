#!/usr/bin/env python3
"""
server/memory_bank_mcp/backup_tools_modules/backup_manager.py
Generated: 2025-07-30.1927
Purpose: Database backup creation, listing, and management with v2.0 support

Key v2.0 Features:
- Enhanced backup metadata with project_uuid information
- v2.0 database schema awareness for backup validation
- Smart backup organization with modular architecture
- Future-proof backup format compatible with unified documents table
"""

import logging
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

class BackupManager:
    """Database backup creation, listing, and management with v2.0 support"""
    
    def __init__(self, context_manager):
        """Initialize with context manager for v2.0 database access"""
        self.context_manager = context_manager
        self.logger = logging.getLogger(__name__)
        
        # Enhanced backup directory structure for v2.0
        self.backup_base_dir = Path.home() / "memory-bank-backups" / "v2.0"
        self.local_backup_dir = self.backup_base_dir / "local"
        self.weekly_backup_dir = self.backup_base_dir / "weekly"
        self.monthly_backup_dir = self.backup_base_dir / "monthly"
        
        # Create backup directories with v2.0 structure
        for backup_dir in [self.local_backup_dir, self.weekly_backup_dir, self.monthly_backup_dir]:
            backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Enhanced retention policies for v2.0
        self.retention_policies = {
            'daily': 7, 
            'weekly': 4, 
            'monthly': 12,
            'manual': 20  # Keep more manual backups for v2.0 development
        }
    
    async def backup_context_db(self, backup_type: str = "manual", force: bool = False, 
                               verify: bool = True) -> str:
        """Create a backup of the current context.db file with v2.0 enhancements"""
        try:
            if not self.context_manager or not self.context_manager.database_path:
                return "❌ BACKUP FAILED (v2.0) - No active project. Use work_on_project() first."
            
            source_db = Path(self.context_manager.database_path)
            
            # Get enhanced project info for v2.0
            project_info = await self._get_v2_project_info()
            
            # Determine backup location and filename
            backup_dir, backup_filename = self._get_backup_location(backup_type, project_info)
            backup_path = backup_dir / backup_filename
            
            # Check if backup already exists (unless forced)
            if backup_path.exists() and not force:
                return f"⚠️ BACKUP ALREADY EXISTS (v2.0) - Use force=True to overwrite."
            
            # Create the backup
            shutil.copy2(source_db, backup_path)
            
            # Verify backup if requested
            verification_result = ""
            if verify:
                verification_result = await self._verify_backup_v2(backup_path, source_db)
            
            # Get backup file info
            backup_size = backup_path.stat().st_size
            size_mb = backup_size / (1024 * 1024)
            
            return f"""✅ BACKUP CREATED SUCCESSFULLY (v2.0)

Project: {project_info.get('project_name', 'Unknown')}
Project UUID: {project_info.get('project_uuid', 'Not set')[:8]}...
Backup Type: {backup_type.title()}
Source: {source_db}
Backup: {backup_path}
Size: {size_mb:.2f} MB

{verification_result}

v2.0 Benefits:
• Enhanced backup metadata with project_uuid
• Future-proof format compatible with unified documents table
• Smart organization for modular architecture"""
            
        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            return f"❌ BACKUP FAILED (v2.0) - Error: {str(e)}"
    
    async def list_backups(self, backup_type: Optional[str] = None, include_metadata: bool = True, 
                          verify_integrity: bool = False) -> str:
        """List all available backups with v2.0 enhanced metadata"""
        try:
            backup_files = []
            
            # Search v2.0 backup directories
            search_dirs = [self.local_backup_dir, self.weekly_backup_dir, self.monthly_backup_dir]
            for backup_dir in search_dirs:
                if backup_dir.exists():
                    for backup_file in backup_dir.glob("*.db*"):
                        backup_info = await self._analyze_backup_file(backup_file, verify_integrity)
                        if backup_type is None or backup_info.get('type') == backup_type:
                            backup_files.append(backup_info)
            
            if not backup_files:
                return """📦 BACKUP INVENTORY (v2.0)

❌ No backups found.

💡 Create your first v2.0 backup: backup_context_db()
🏗️ v2.0 Structure: Enhanced metadata and project_uuid support"""
            
            # Sort by creation date (newest first)
            backup_files.sort(key=lambda x: x.get('created', ''), reverse=True)
            
            # Format backup listing
            inventory = f"""📦 BACKUP INVENTORY (v2.0 Architecture)

Summary:
• Total Backups: {len(backup_files)}
• v2.0 Enhanced: ✅ Project UUID tracking, future-proof format

Available Backups:"""
            
            for i, backup_info in enumerate(backup_files[:10], 1):  # Show top 10
                name = backup_info.get('name', 'Unknown')
                created = backup_info.get('created', 'Unknown')
                size_mb = backup_info.get('size_mb', 0)
                backup_type = backup_info.get('type', 'unknown')
                integrity = backup_info.get('integrity', 'Not checked')
                
                inventory += f"""

{i}. {name}
   Created: {created}
   Type: {backup_type.title()}
   Size: {size_mb:.2f} MB
   Integrity: {integrity}"""
                
                if include_metadata and backup_info.get('metadata'):
                    metadata = backup_info['metadata']
                    if 'project_uuid' in metadata:
                        inventory += f"\n   Project UUID: {metadata['project_uuid'][:8]}..."
            
            if len(backup_files) > 10:
                inventory += f"\n\n... and {len(backup_files) - 10} more backups"
            
            inventory += """

v2.0 Features:
• Enhanced backup metadata with project_uuid tracking
• Future-proof format compatible with unified documents table
• Smart organization and retention policies"""
            
            return inventory
            
        except Exception as e:
            self.logger.error(f"Error listing backups: {e}")
            return f"❌ ERROR LISTING BACKUPS (v2.0) - Error: {str(e)}"
    
    async def _get_v2_project_info(self) -> Dict[str, Any]:
        """Get enhanced project information for v2.0 backups"""
        try:
            if hasattr(self.context_manager, 'get_current_session_info'):
                project_info = await self.context_manager.get_current_session_info()
                return {
                    'project_name': project_info.get('project_name', 'memory-bank_v04'),
                    'project_uuid': project_info.get('project_uuid', 'unknown'),
                    'architecture_version': '2.0'
                }
            else:
                return {
                    'project_name': 'memory-bank_v04',
                    'project_uuid': 'unknown',
                    'architecture_version': '2.0'
                }
        except Exception as e:
            self.logger.warning(f"Could not get v2.0 project info: {e}")
            return {
                'project_name': 'memory-bank_v04',
                'project_uuid': 'unknown',
                'architecture_version': '2.0'
            }
    
    def _get_backup_location(self, backup_type: str, project_info: Dict) -> tuple:
        """Determine backup directory and filename with v2.0 structure"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = project_info.get('project_name', 'memory-bank')
        project_uuid = project_info.get('project_uuid', 'unknown')[:8]
        
        # Enhanced filename with v2.0 metadata
        filename = f"{project_name}_v2.0_{project_uuid}_{backup_type}_{timestamp}.db"
        
        # Select appropriate directory
        if backup_type in ['daily', 'manual']:
            backup_dir = self.local_backup_dir
        elif backup_type == 'weekly':
            backup_dir = self.weekly_backup_dir
        elif backup_type == 'monthly':
            backup_dir = self.monthly_backup_dir
        else:
            backup_dir = self.local_backup_dir
        
        return backup_dir, filename
    
    async def _verify_backup_v2(self, backup_path: Path, source_path: Path) -> str:
        """Verify backup integrity with v2.0 enhancements"""
        try:
            # Basic file size comparison
            backup_size = backup_path.stat().st_size
            source_size = source_path.stat().st_size
            
            if backup_size != source_size:
                return "⚠️ Verification: Size mismatch detected"
            
            # Basic file hash comparison (for smaller files)
            if backup_size < 100 * 1024 * 1024:  # Less than 100MB
                with open(backup_path, 'rb') as f:
                    backup_hash = hashlib.md5(f.read()).hexdigest()
                with open(source_path, 'rb') as f:
                    source_hash = hashlib.md5(f.read()).hexdigest()
                
                if backup_hash == source_hash:
                    return "✅ Verification: Backup integrity confirmed"
                else:
                    return "⚠️ Verification: Hash mismatch detected"
            else:
                return "✅ Verification: Size match confirmed (large file)"
                
        except Exception as e:
            self.logger.warning(f"Backup verification failed: {e}")
            return f"⚠️ Verification: Could not verify - {str(e)}"
    
    async def _analyze_backup_file(self, backup_path: Path, verify_integrity: bool = False) -> Dict[str, Any]:
        """Analyze backup file with v2.0 metadata extraction"""
        try:
            stat = backup_path.stat()
            
            # Extract backup type from filename
            filename = backup_path.name
            backup_type = 'unknown'
            for btype in ['manual', 'daily', 'weekly', 'monthly']:
                if btype in filename:
                    backup_type = btype
                    break
            
            # Extract project UUID from v2.0 filename format
            parts = filename.split('_')
            project_uuid = 'unknown'
            if len(parts) >= 4 and len(parts[2]) == 8:
                project_uuid = parts[2]
            
            backup_info = {
                'name': filename,
                'path': str(backup_path),
                'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                'size_mb': stat.st_size / (1024 * 1024),
                'type': backup_type,
                'metadata': {
                    'project_uuid': project_uuid,
                    'architecture_version': '2.0'
                }
            }
            
            # Add integrity check if requested
            if verify_integrity:
                # Basic integrity check - file can be opened
                try:
                    import sqlite3
                    conn = sqlite3.connect(str(backup_path))
                    conn.execute("SELECT name FROM sqlite_master LIMIT 1")
                    conn.close()
                    backup_info['integrity'] = '✅ Valid SQLite DB'
                except:
                    backup_info['integrity'] = '❌ Corrupted'
            else:
                backup_info['integrity'] = 'Not checked'
            
            return backup_info
            
        except Exception as e:
            self.logger.error(f"Error analyzing backup file {backup_path}: {e}")
            return {
                'name': backup_path.name,
                'path': str(backup_path),
                'created': 'Unknown',
                'size_mb': 0,
                'type': 'unknown',
                'error': str(e),
                'integrity': 'Error'
            }
