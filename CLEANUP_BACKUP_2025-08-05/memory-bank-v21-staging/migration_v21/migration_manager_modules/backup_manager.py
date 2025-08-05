#!/usr/bin/env python3
"""
Backup Manager Module
=====================

Handles database backup operations for migration safety.
"""

import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

class BackupManager:
    """Manages database backups for migration safety"""
    
    def create_backup(self, database_path: str, backup_type: str = "migration") -> Optional[str]:
        """
        Create backup before migration
        
        Args:
            database_path: Path to database to backup
            backup_type: Type of backup (migration, manual, etc.)
            
        Returns:
            Path to backup file, or None if failed
        """
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{database_path}.{backup_type}_backup_{timestamp}"
            
            shutil.copy2(database_path, backup_path)
            print(f"💾 Backup created: {Path(backup_path).name}")
            return backup_path
            
        except Exception as e:
            logger.error(f"Backup creation failed: {e}")
            print(f"❌ Failed to create backup: {e}")
            return None
    
    def restore_backup(self, original_path: str, backup_path: str) -> bool:
        """
        Restore database from backup
        
        Args:
            original_path: Path to restore to
            backup_path: Path of backup file
            
        Returns:
            True if successful
        """
        try:
            if not Path(backup_path).exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            shutil.copy2(backup_path, original_path)
            print(f"✅ Database restored from backup")
            return True
            
        except Exception as e:
            logger.error(f"Backup restore failed: {e}")
            print(f"❌ Failed to restore backup: {e}")
            return False
