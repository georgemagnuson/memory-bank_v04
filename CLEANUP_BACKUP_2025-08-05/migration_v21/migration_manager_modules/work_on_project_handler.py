#!/usr/bin/env python3
"""
Work On Project Handler Module
===============================

Handles enhanced work_on_project functionality with automatic migration.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from ..version_detector import VersionDetector
from ..schema_creator import SchemaCreator

logger = logging.getLogger(__name__)

class WorkOnProjectHandler:
    """Handles enhanced work_on_project operations"""
    
    def __init__(self):
        self.version_detector = VersionDetector()
        self.schema_creator = SchemaCreator()
    
    def work_on_project(self, project_path: str) -> Dict[str, Any]:
        """
        Enhanced work_on_project with automatic v2.1 migration
        
        Args:
            project_path: Path to project directory
            
        Returns:
            Work operation result
        """
        try:
            # Normalize paths
            project_path = str(Path(project_path).absolute())
            project_name = Path(project_path).name
            memory_bank_dir = Path(project_path) / "memory-bank"
            database_path = memory_bank_dir / "context.db"
            
            # Ensure directories exist
            memory_bank_dir.mkdir(parents=True, exist_ok=True)
            
            # Handle database scenarios
            if not database_path.exists():
                return self._create_new_database(database_path, project_name, project_path)
            else:
                return self._handle_existing_database(database_path, project_name, project_path)
                
        except Exception as e:
            logger.error(f"work_on_project failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'project_path': project_path
            }
    
    def _create_new_database(self, database_path: Path, project_name: str, project_path: str) -> Dict[str, Any]:
        """Create new v2.1 database"""
        print(f"📄 Creating new v2.1 database for {project_name}")
        result = self.schema_creator.create_v21_database(str(database_path), project_name, project_path)
        
        if result['success']:
            return {
                'success': True,
                'action': 'created_new_database',
                'project_name': project_name,
                'project_path': project_path,
                'database_path': str(database_path),
                'version': '2.1',
                'message': f"✅ Created new v2.1 database for {project_name}"
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Database creation failed'),
                'project_path': project_path
            }
    
    def _handle_existing_database(self, database_path: Path, project_name: str, project_path: str) -> Dict[str, Any]:
        """Handle existing database with version detection"""
        # Analyze existing database
        db_info = self.version_detector.analyze_database(str(database_path))
        
        if db_info.version >= 2.1:
            # Already v2.1 - ready to use
            return {
                'success': True,
                'action': 'opened_current_database',
                'project_name': project_name,
                'project_path': project_path,
                'database_path': str(database_path),
                'version': str(db_info.version),
                'table_count': db_info.table_count,
                'record_count': sum(db_info.content_tables.values()),
                'message': f"✅ Database is current v{db_info.version}"
            }
        
        elif db_info.needs_migration:
            # Offer migration
            print(f"🔄 Database needs migration to v2.1")
            print(f"   Current: v{db_info.version}, {db_info.table_count} tables")
            print(f"   Records: {sum(db_info.content_tables.values())}")
            
            return {
                'success': True,
                'action': 'migration_needed',
                'project_name': project_name,
                'project_path': project_path,
                'database_path': str(database_path),
                'current_version': str(db_info.version),
                'migration_type': db_info.migration_type,
                'message': f"⚠️ Database needs migration from v{db_info.version} to v2.1"
            }
        
        else:
            return {
                'success': False,
                'error': f"Unknown database state: v{db_info.version}",
                'project_path': project_path,
                'database_path': str(database_path)
            }
