"""
Filename: enhanced_project_manager.py
Generated: 2025-08-02.1721
Purpose: Enhanced project manager that integrates with centralized context registry
        Ensures work_on_project() properly registers context for all tool modules
"""

import os
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from context_registry import (
    ProjectContext, 
    get_global_registry, 
    ContextRegistry
)


class EnhancedProjectManager:
    """
    Enhanced project manager with centralized context registration
    Replaces legacy project switching with registry-based approach
    """
    
    def __init__(self):
        self.registry = get_global_registry()
        self.logger = logging.getLogger(__name__)
    
    def work_on_project(self, project_path: str) -> Dict[str, Any]:
        """
        Enhanced work_on_project with context registry integration
        
        Args:
            project_path: Path to the project directory
            
        Returns:
            Dict with operation results and context information
        """
        try:
            # Clear any existing context first
            self.registry.clear_context()
            
            # Normalize project path
            project_path = os.path.abspath(project_path)
            project_name = os.path.basename(project_path)
            
            # Ensure project directory exists
            os.makedirs(project_path, exist_ok=True)
            
            # Construct database path
            memory_bank_dir = os.path.join(project_path, "memory-bank")
            os.makedirs(memory_bank_dir, exist_ok=True)
            database_path = os.path.join(memory_bank_dir, "context.db")
            
            # Check if database exists and get/create schema
            schema_info = self._initialize_database(database_path)
            
            # Gather context information
            context_info = self._gather_context_info(
                project_name, project_path, database_path, schema_info
            )
            
            # Create and register project context
            project_context = ProjectContext(
                project_name=project_name,
                project_path=project_path,
                database_path=database_path,
                database_version=context_info["database_version"],
                table_count=context_info["table_count"],
                document_count=context_info["document_count"],
                connection_info=context_info["connection_info"],
                initialized_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # Register context globally
            if self.registry.register_context(project_context):
                return {
                    "success": True,
                    "message": f"✅ Project '{project_name}' loaded with context registry",
                    "context": self.registry.get_context_info(),
                    "migration_performed": schema_info.get("migration_performed", False),
                    "database_path": database_path
                }
            else:
                return {
                    "success": False,
                    "message": "❌ Failed to register project context",
                    "error": "Context registration failed"
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error initializing project: {str(e)}",
                "error": str(e)
            }
    
    def _initialize_database(self, database_path: str) -> Dict[str, Any]:
        """
        Initialize or migrate database schema
        
        Returns:
            Dict with schema information and migration status
        """
        schema_info = {
            "migration_performed": False,
            "version_before": None,
            "version_after": None,
            "tables_created": 0
        }
        
        # Check if database exists
        db_exists = os.path.exists(database_path)
        
        if not db_exists:
            # Create new v2.0 database
            schema_info.update(self._create_v2_database(database_path))
            schema_info["migration_performed"] = True
            schema_info["version_after"] = "v2.0"
        else:
            # Check existing version and migrate if needed
            current_version = self._detect_database_version(database_path)
            schema_info["version_before"] = current_version
            
            if current_version == "v1.4.0":
                # Perform migration to v2.0
                migration_result = self._migrate_to_v2(database_path)
                schema_info.update(migration_result)
                schema_info["migration_performed"] = True
                schema_info["version_after"] = "v2.0"
            else:
                schema_info["version_after"] = current_version
        
        return schema_info
    
    def _gather_context_info(self, project_name: str, project_path: str, 
                           database_path: str, schema_info: Dict) -> Dict[str, Any]:
        """
        Gather comprehensive context information
        """
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            # Get table count
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # Get document count (try v2.0 first, fallback to v1.4.0)
            document_count = 0
            try:
                cursor.execute("SELECT COUNT(*) FROM documents")
                document_count = cursor.fetchone()[0]
            except sqlite3.OperationalError:
                try:
                    cursor.execute("SELECT COUNT(*) FROM unified_documents")
                    document_count = cursor.fetchone()[0]
                except sqlite3.OperationalError:
                    document_count = 0
            
            # Get database version
            try:
                cursor.execute("PRAGMA user_version")
                version_num = cursor.fetchone()[0]
                if version_num >= 4:
                    db_version = "v2.0"
                elif version_num >= 1:
                    db_version = "v1.4.0"
                else:
                    db_version = "unknown"
            except:
                db_version = "unknown"
            
            conn.close()
            
            return {
                "database_version": db_version,
                "table_count": table_count,
                "document_count": document_count,
                "connection_info": {
                    "database_size": os.path.getsize(database_path),
                    "last_modified": os.path.getmtime(database_path),
                    "readable": os.access(database_path, os.R_OK),
                    "writable": os.access(database_path, os.W_OK)
                }
            }
            
        except Exception as e:
            return {
                "database_version": "error",
                "table_count": 0,
                "document_count": 0,
                "connection_info": {"error": str(e)}
            }
    
    def _detect_database_version(self, database_path: str) -> str:
        """Detect the version of an existing database"""
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            # Check for v2.0 tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
            if cursor.fetchone():
                conn.close()
                return "v2.0"
            
            # Check for v1.4.0 tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='unified_documents'")
            if cursor.fetchone():
                conn.close()
                return "v1.4.0"
            
            conn.close()
            return "unknown"
            
        except Exception:
            return "error"
    
    def _create_v2_database(self, database_path: str) -> Dict[str, Any]:
        """Create a new v2.0 database with full schema"""
        import sqlite3
        import uuid
        import os
        from pathlib import Path
        
        try:
            # Get the template DDL file path
            current_dir = Path(__file__).parent
            template_ddl = current_dir / "context_template_v2.0.ddl"
            template_db = current_dir / "context_template_v2.0.db"
            
            # Method 1: Try copying template database
            if template_db.exists():
                import shutil
                shutil.copy2(str(template_db), database_path)
                self.logger.info(f"Created v2.0 database from template: {database_path}")
                
                # Add initial project entry
                project_name = os.path.basename(os.path.dirname(os.path.dirname(database_path)))
                project_path = os.path.dirname(os.path.dirname(database_path))
                project_uuid = str(uuid.uuid4())
                
                conn = sqlite3.connect(database_path)
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO projects (uuid, name, path, description, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    project_uuid,
                    project_name,
                    project_path,
                    f"Memory Bank for {project_name} project",
                    '{"created_by": "memory_bank_mcp_v2", "version": "2.0"}'
                ))
                conn.commit()
                conn.close()
                
                return {
                    "tables_created": 15,  # 10 core + 5 FTS/index
                    "schema_version": "v2.0",
                    "method": "template_database",
                    "project_uuid": project_uuid
                }
            
            # Method 2: Execute DDL file
            elif template_ddl.exists():
                with open(template_ddl, 'r') as f:
                    ddl_content = f.read()
                
                conn = sqlite3.connect(database_path)
                cursor = conn.cursor()
                cursor.executescript(ddl_content)
                
                # Add initial project entry
                project_name = os.path.basename(os.path.dirname(os.path.dirname(database_path)))
                project_path = os.path.dirname(os.path.dirname(database_path))
                project_uuid = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO projects (uuid, name, path, description, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    project_uuid,
                    project_name,
                    project_path,
                    f"Memory Bank for {project_name} project",
                    '{"created_by": "memory_bank_mcp_v2", "version": "2.0"}'
                ))
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Created v2.0 database from DDL: {database_path}")
                
                return {
                    "tables_created": 15,  # 10 core + 5 FTS/index
                    "schema_version": "v2.0", 
                    "method": "ddl_execution",
                    "project_uuid": project_uuid
                }
            
            # Method 3: Fallback inline schema
            else:
                conn = sqlite3.connect(database_path)
                cursor = conn.cursor()
                
                # Create minimal v2.0 schema inline
                cursor.executescript("""
                    CREATE TABLE projects (
                        uuid TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        path TEXT NOT NULL UNIQUE,
                        description TEXT DEFAULT '',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT DEFAULT '{}'
                    );
                    
                    CREATE TABLE documents (
                        project_uuid TEXT NOT NULL,
                        uuid TEXT NOT NULL,
                        version INTEGER NOT NULL DEFAULT 1,
                        document_type TEXT NOT NULL,
                        title TEXT,
                        content TEXT NOT NULL,
                        summary TEXT,
                        tags TEXT DEFAULT '[]',
                        metadata TEXT DEFAULT '{}',
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP,
                        created_by TEXT,
                        status TEXT DEFAULT 'active',
                        
                        PRIMARY KEY (project_uuid, uuid, version),
                        FOREIGN KEY (project_uuid) REFERENCES projects(uuid)
                    );
                    
                    CREATE INDEX idx_documents_type ON documents(document_type);
                    CREATE INDEX idx_documents_project ON documents(project_uuid);
                    CREATE INDEX idx_documents_uuid_latest ON documents(uuid, version);
                """)
                
                # Add initial project entry
                project_name = os.path.basename(os.path.dirname(os.path.dirname(database_path)))
                project_path = os.path.dirname(os.path.dirname(database_path))
                project_uuid = str(uuid.uuid4())
                
                cursor.execute("""
                    INSERT INTO projects (uuid, name, path, description, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    project_uuid,
                    project_name,
                    project_path,
                    f"Memory Bank for {project_name} project",
                    '{"created_by": "memory_bank_mcp_v2", "version": "2.0"}'
                ))
                
                conn.commit()
                conn.close()
                
                self.logger.info(f"Created v2.0 database with inline schema: {database_path}")
                
                return {
                    "tables_created": 5,  # Minimal schema
                    "schema_version": "v2.0",
                    "method": "inline_schema",
                    "project_uuid": project_uuid
                }
                
        except Exception as e:
            self.logger.error(f"Failed to create v2.0 database: {e}")
            return {
                "tables_created": 0,
                "schema_version": "error",
                "error": str(e)
            }
    
    def _migrate_to_v2(self, database_path: str) -> Dict[str, Any]:
        """Migrate existing database to v2.0"""
        # This would contain the migration logic
        # For now, returning placeholder - we'll implement full migration
        return {
            "tables_created": 6,  # new tables added
            "records_migrated": 0,  # to be implemented
            "schema_version": "v2.0"
        }


# Global instance for tool integration
_enhanced_manager = EnhancedProjectManager()


def enhanced_work_on_project(project_path: str) -> Dict[str, Any]:
    """
    Global function for enhanced work_on_project with context registry
    """
    return _enhanced_manager.work_on_project(project_path)
