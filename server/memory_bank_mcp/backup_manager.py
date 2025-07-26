"""
Memory Bank Backup System - Phase 1 Completion Feature

Filename: backup_manager.py
Generated: 2025-07-22.1721
Purpose: Comprehensive backup system for Memory Bank context.db files with local and centralized storage

Features:
- Local daily backups (7 retained) in project directory
- Centralized weekly/monthly backups (4 weekly, 6 monthly)
- SQLite file copies with timestamp and project metadata
- Automatic time-based and manual on-demand triggers
- Backup verification and integrity checks
- Easy restore functionality with backup listing
"""

import asyncio
import json
import os
import shutil
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    """
    Comprehensive backup manager for Memory Bank context.db files
    
    Implements Option C strategy:
    - Local backups: Daily in project directory (7 retained)
    - Centralized backups: Weekly + Monthly in global location (4+6 retained)
    """
    
    def __init__(self, project_path: str, centralized_backup_path: str = None):
        self.project_path = Path(project_path)
        self.context_db_path = self.project_path / "memory-bank" / "context.db"
        self.local_backup_dir = self.project_path / "memory-bank" / "backups"
        
        # Centralized backup location (defaults to user's Documents/MemoryBankBackups)
        if centralized_backup_path:
            self.centralized_backup_dir = Path(centralized_backup_path)
        else:
            self.centralized_backup_dir = Path.home() / "Documents" / "MemoryBankBackups"
        
        # Backup retention policies
        self.retention_policies = {
            'daily': {'count': 7, 'location': 'local'},
            'weekly': {'count': 4, 'location': 'centralized'}, 
            'monthly': {'count': 6, 'location': 'centralized'}
        }
        
        # Ensure backup directories exist
        self._ensure_backup_directories()
    
    def _ensure_backup_directories(self):
        """Create backup directories if they don't exist"""
        # Local backup directories
        (self.local_backup_dir / "daily").mkdir(parents=True, exist_ok=True)
        
        # Centralized backup directories
        project_name = self.project_path.name
        self.centralized_project_dir = self.centralized_backup_dir / project_name
        (self.centralized_project_dir / "weekly").mkdir(parents=True, exist_ok=True)
        (self.centralized_project_dir / "monthly").mkdir(parents=True, exist_ok=True)
    
    def _get_backup_filename(self, backup_type: str) -> str:
        """Generate backup filename with timestamp and project info"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = self.project_path.name
        return f"{project_name}_{backup_type}_{timestamp}.db"
    
    def _get_backup_metadata(self) -> Dict:
        """Generate metadata for backup"""
        try:
            # Get database statistics
            with sqlite3.connect(self.context_db_path) as conn:
                cursor = conn.cursor()
                
                # Count records in main tables
                stats = {}
                tables = ['discussions', 'artifacts', 'documents_v2', 'chat_sessions']
                for table in tables:
                    try:
                        cursor.execute(f"SELECT COUNT(*) FROM {table}")
                        stats[f"{table}_count"] = cursor.fetchone()[0]
                    except sqlite3.Error:
                        stats[f"{table}_count"] = 0
                
                # Get database file size
                stats['file_size_bytes'] = self.context_db_path.stat().st_size
                
                return {
                    'project_name': self.project_path.name,
                    'project_path': str(self.project_path),
                    'backup_timestamp': datetime.now().isoformat(),
                    'database_stats': stats,
                    'memory_bank_version': '1.0.0'
                }
        except Exception as e:
            logger.warning(f"Could not generate backup metadata: {e}")
            return {
                'project_name': self.project_path.name,
                'project_path': str(self.project_path),
                'backup_timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _verify_backup_integrity(self, backup_path: Path) -> bool:
        """Verify backup file integrity by testing SQLite connection"""
        try:
            with sqlite3.connect(backup_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                return table_count > 0
        except sqlite3.Error as e:
            logger.error(f"Backup integrity check failed for {backup_path}: {e}")
            return False
    
    async def create_backup(self, backup_type: str, force: bool = False) -> Dict:
        """
        Create a backup of the context.db file
        
        Args:
            backup_type: 'daily', 'weekly', 'monthly', or 'manual'
            force: Create backup even if one already exists for the period
            
        Returns:
            Dict with backup details and status
        """
        if not self.context_db_path.exists():
            raise FileNotFoundError(f"Context database not found: {self.context_db_path}")
        
        # Determine backup location
        if backup_type == 'daily' or backup_type == 'manual':
            backup_dir = self.local_backup_dir / "daily"
        elif backup_type == 'weekly':
            backup_dir = self.centralized_project_dir / "weekly"
        elif backup_type == 'monthly':
            backup_dir = self.centralized_project_dir / "monthly"
        else:
            raise ValueError(f"Invalid backup type: {backup_type}")
        
        # Generate backup filename and path
        backup_filename = self._get_backup_filename(backup_type)
        backup_path = backup_dir / backup_filename
        
        # Check if backup already exists for this period (unless forced)
        if not force and backup_type != 'manual':
            existing_backup = self._find_existing_backup_for_period(backup_dir, backup_type)
            if existing_backup:
                return {
                    'status': 'skipped',
                    'reason': f'Backup already exists for this {backup_type} period',
                    'existing_backup': str(existing_backup),
                    'backup_type': backup_type
                }
        
        try:
            # Create backup metadata
            metadata = self._get_backup_metadata()
            
            # Copy database file
            shutil.copy2(self.context_db_path, backup_path)
            
            # Verify backup integrity
            if not self._verify_backup_integrity(backup_path):
                backup_path.unlink()  # Remove corrupted backup
                raise Exception("Backup integrity verification failed")
            
            # Create metadata file
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Clean up old backups according to retention policy
            await self._cleanup_old_backups(backup_dir, backup_type)
            
            return {
                'status': 'success',
                'backup_path': str(backup_path),
                'backup_size_bytes': backup_path.stat().st_size,
                'backup_type': backup_type,
                'metadata': metadata
            }
            
        except Exception as e:
            # Clean up partial backup on error
            if backup_path.exists():
                backup_path.unlink()
            metadata_path = backup_path.with_suffix('.json')
            if metadata_path.exists():
                metadata_path.unlink()
            
            logger.error(f"Backup creation failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'backup_type': backup_type
            }
    
    def _find_existing_backup_for_period(self, backup_dir: Path, backup_type: str) -> Optional[Path]:
        """Check if backup already exists for current period"""
        now = datetime.now()
        
        if backup_type == 'daily':
            # Check if backup exists for today
            date_pattern = now.strftime("%Y%m%d")
        elif backup_type == 'weekly':
            # Check if backup exists for this week (Monday-Sunday)
            start_of_week = now - timedelta(days=now.weekday())
            date_pattern = start_of_week.strftime("%Y%m%d")
        elif backup_type == 'monthly':
            # Check if backup exists for this month
            date_pattern = now.strftime("%Y%m")
        else:
            return None
        
        # Look for existing backups matching the pattern
        for backup_file in backup_dir.glob("*.db"):
            if date_pattern in backup_file.name:
                return backup_file
        
        return None
    
    async def _cleanup_old_backups(self, backup_dir: Path, backup_type: str):
        """Remove old backups according to retention policy"""
        policy = self.retention_policies.get(backup_type)
        if not policy:
            return
        
        # Get all backup files sorted by creation time (newest first)
        backup_files = []
        for backup_file in backup_dir.glob("*.db"):
            try:
                stat = backup_file.stat()
                backup_files.append((backup_file, stat.st_mtime))
            except OSError:
                continue
        
        backup_files.sort(key=lambda x: x[1], reverse=True)
        
        # Remove excess backups
        for backup_file, _ in backup_files[policy['count']:]:
            try:
                backup_file.unlink()
                # Also remove metadata file if it exists
                metadata_file = backup_file.with_suffix('.json')
                if metadata_file.exists():
                    metadata_file.unlink()
                logger.info(f"Removed old backup: {backup_file}")
            except OSError as e:
                logger.warning(f"Could not remove old backup {backup_file}: {e}")
    
    async def list_backups(self) -> Dict[str, List[Dict]]:
        """List all available backups with metadata"""
        backups = {
            'daily': [],
            'weekly': [],
            'monthly': []
        }
        
        # Local daily backups
        daily_dir = self.local_backup_dir / "daily"
        if daily_dir.exists():
            backups['daily'] = await self._list_backups_in_directory(daily_dir, 'daily')
        
        # Centralized weekly/monthly backups
        if self.centralized_project_dir.exists():
            weekly_dir = self.centralized_project_dir / "weekly"
            if weekly_dir.exists():
                backups['weekly'] = await self._list_backups_in_directory(weekly_dir, 'weekly')
            
            monthly_dir = self.centralized_project_dir / "monthly"
            if monthly_dir.exists():
                backups['monthly'] = await self._list_backups_in_directory(monthly_dir, 'monthly')
        
        return backups
    
    async def _list_backups_in_directory(self, backup_dir: Path, backup_type: str) -> List[Dict]:
        """List backups in a specific directory"""
        backups = []
        
        for backup_file in backup_dir.glob("*.db"):
            try:
                stat = backup_file.stat()
                metadata_file = backup_file.with_suffix('.json')
                
                backup_info = {
                    'filename': backup_file.name,
                    'path': str(backup_file),
                    'size_bytes': stat.st_size,
                    'created_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'backup_type': backup_type,
                    'verified': self._verify_backup_integrity(backup_file)
                }
                
                # Add metadata if available
                if metadata_file.exists():
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                            backup_info['metadata'] = metadata
                    except (json.JSONDecodeError, OSError):
                        pass
                
                backups.append(backup_info)
                
            except OSError:
                continue
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created_time'], reverse=True)
        return backups
    
    async def restore_backup(self, backup_path: str, confirm: bool = False) -> Dict:
        """
        Restore from a backup file
        
        Args:
            backup_path: Path to the backup file to restore from
            confirm: Confirmation that user wants to overwrite current database
            
        Returns:
            Dict with restore status and details
        """
        if not confirm:
            return {
                'status': 'confirmation_required',
                'message': 'Restore operation requires confirmation as it will overwrite current database',
                'current_db_path': str(self.context_db_path),
                'backup_path': backup_path
            }
        
        backup_file = Path(backup_path)
        if not backup_file.exists():
            return {
                'status': 'error',
                'error': f'Backup file not found: {backup_path}'
            }
        
        # Verify backup integrity
        if not self._verify_backup_integrity(backup_file):
            return {
                'status': 'error',
                'error': 'Backup file integrity check failed'
            }
        
        try:
            # Create backup of current database before restore
            if self.context_db_path.exists():
                pre_restore_backup = await self.create_backup('manual', force=True)
                if pre_restore_backup['status'] != 'success':
                    return {
                        'status': 'error',
                        'error': 'Failed to create pre-restore backup',
                        'details': pre_restore_backup
                    }
            
            # Restore the backup
            shutil.copy2(backup_file, self.context_db_path)
            
            # Verify restored database
            if not self._verify_backup_integrity(self.context_db_path):
                return {
                    'status': 'error',
                    'error': 'Restored database failed integrity check'
                }
            
            return {
                'status': 'success',
                'message': 'Database successfully restored from backup',
                'restored_from': backup_path,
                'pre_restore_backup': pre_restore_backup.get('backup_path') if 'pre_restore_backup' in locals() else None
            }
            
        except Exception as e:
            logger.error(f"Restore operation failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def verify_all_backups(self) -> Dict:
        """Verify integrity of all existing backups"""
        backups = await self.list_backups()
        verification_results = {
            'daily': [],
            'weekly': [],
            'monthly': [],
            'summary': {'total': 0, 'verified': 0, 'failed': 0}
        }
        
        for backup_type, backup_list in backups.items():
            for backup in backup_list:
                verification_results['summary']['total'] += 1
                
                result = {
                    'filename': backup['filename'],
                    'path': backup['path'],
                    'verified': backup['verified']
                }
                
                if backup['verified']:
                    verification_results['summary']['verified'] += 1
                else:
                    verification_results['summary']['failed'] += 1
                
                verification_results[backup_type].append(result)
        
        return verification_results
    
    async def get_backup_status(self) -> Dict:
        """Get comprehensive backup system status"""
        backups = await self.list_backups()
        
        status = {
            'project_name': self.project_path.name,
            'project_path': str(self.project_path),
            'context_db_exists': self.context_db_path.exists(),
            'context_db_size_bytes': self.context_db_path.stat().st_size if self.context_db_path.exists() else 0,
            'backup_directories': {
                'local': str(self.local_backup_dir),
                'centralized': str(self.centralized_backup_dir)
            },
            'retention_policies': self.retention_policies,
            'backup_counts': {
                'daily': len(backups['daily']),
                'weekly': len(backups['weekly']),
                'monthly': len(backups['monthly'])
            },
            'last_backups': {}
        }
        
        # Get last backup for each type
        for backup_type, backup_list in backups.items():
            if backup_list:
                status['last_backups'][backup_type] = {
                    'filename': backup_list[0]['filename'],
                    'created_time': backup_list[0]['created_time'],
                    'size_bytes': backup_list[0]['size_bytes']
                }
        
        return status


# Automatic backup scheduler (to be integrated with MCP server)
class BackupScheduler:
    """
    Automatic backup scheduler for time-based triggers
    """
    
    def __init__(self, backup_manager: BackupManager):
        self.backup_manager = backup_manager
        self.last_daily_backup = None
        self.last_weekly_backup = None
        self.last_monthly_backup = None
    
    async def check_and_run_scheduled_backups(self) -> Dict[str, Dict]:
        """Check if any scheduled backups need to run and execute them"""
        results = {}
        now = datetime.now()
        
        # Check daily backup (run once per day)
        if self._should_run_daily_backup(now):
            results['daily'] = await self.backup_manager.create_backup('daily')
            if results['daily']['status'] == 'success':
                self.last_daily_backup = now.date()
        
        # Check weekly backup (run once per week, on Sundays)
        if self._should_run_weekly_backup(now):
            results['weekly'] = await self.backup_manager.create_backup('weekly')
            if results['weekly']['status'] == 'success':
                self.last_weekly_backup = now.date()
        
        # Check monthly backup (run once per month, on the 1st)
        if self._should_run_monthly_backup(now):
            results['monthly'] = await self.backup_manager.create_backup('monthly')
            if results['monthly']['status'] == 'success':
                self.last_monthly_backup = now.date()
        
        return results
    
    def _should_run_daily_backup(self, now: datetime) -> bool:
        """Check if daily backup should run"""
        if self.last_daily_backup is None:
            return True
        return now.date() > self.last_daily_backup
    
    def _should_run_weekly_backup(self, now: datetime) -> bool:
        """Check if weekly backup should run (Sundays)"""
        if now.weekday() != 6:  # Not Sunday
            return False
        if self.last_weekly_backup is None:
            return True
        return now.date() > self.last_weekly_backup
    
    def _should_run_monthly_backup(self, now: datetime) -> bool:
        """Check if monthly backup should run (1st of month)"""
        if now.day != 1:  # Not first day of month
            return False
        if self.last_monthly_backup is None:
            return True
        return now.date() > self.last_monthly_backup
