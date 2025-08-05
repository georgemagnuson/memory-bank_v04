#!/usr/bin/env python3
"""
Schema Creator Module
=====================

Creates clean v2.1 database schemas from scratch.
Handles initial database setup and schema templates.
"""

import sqlite3
import logging
import uuid
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class SchemaCreator:
    """Creates clean v2.1 database schemas"""
    
    def __init__(self):
        self.version = 2.1
        self.version_code = 21  # For PRAGMA user_version
    
    def create_v21_database(self, database_path: str, project_name: str, 
                           project_path: str) -> Dict[str, Any]:
        """
        Create a new v2.1 database with clean schema
        
        Args:
            database_path: Path where to create the database
            project_name: Name of the project
            project_path: Full path to project directory
            
        Returns:
            Dict with creation results
        """
        try:
            # Ensure database doesn't already exist
            if Path(database_path).exists():
                return {
                    'success': False,
                    'error': f'Database already exists: {database_path}'
                }
            
            print(f"📄 Creating new v2.1 database: {Path(database_path).name}")
            
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            try:
                # Create v2.1 schema
                self._create_core_tables(cursor)
                self._create_fts_tables(cursor)  
                self._create_indexes(cursor)
                self._insert_default_data(cursor, project_name, project_path)
                
                # Set schema version
                cursor.execute(f'PRAGMA user_version = {self.version_code}')
                
                conn.commit()
                
                # Verify creation
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                table_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT uuid FROM projects LIMIT 1")
                project_uuid = cursor.fetchone()[0]
                
                print(f"   ✅ Created clean v2.1 database with {table_count} tables")
                
                return {
                    'success': True,
                    'database_path': database_path,
                    'project_uuid': project_uuid,
                    'project_name': project_name,
                    'table_count': table_count,
                    'version': self.version,
                    'message': f'Successfully created v2.1 database for {project_name}'
                }
                
            except Exception as e:
                conn.rollback()
                raise Exception(f"Failed to create v2.1 database: {e}")
                
            finally:
                conn.close()
                
        except Exception as e:
            logger.error(f"Database creation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_core_tables(self, cursor):
        """Create core v2.1 tables"""
        
        # Projects table
        cursor.execute("""
            CREATE TABLE projects (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active',
                metadata TEXT DEFAULT '{}'
            )
        """)
        
        # Documents table (main content table)
        cursor.execute("""
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT,
                status TEXT DEFAULT 'active',
                importance INTEGER DEFAULT 5,
                source_file TEXT,
                PRIMARY KEY (project_uuid, uuid, version),
                FOREIGN KEY (project_uuid) REFERENCES projects(uuid)
            )
        """)
        
        # Semantic equivalents for search expansion
        cursor.execute("""
            CREATE TABLE semantic_equivalents (
                domain TEXT NOT NULL,
                primary_term TEXT NOT NULL,
                equivalent_terms TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (domain, primary_term)
            )
        """)
    
    def _create_fts_tables(self, cursor):
        """Create FTS5 search tables"""
        
        # FTS5 search table for documents
        cursor.execute("""
            CREATE VIRTUAL TABLE documents_fts USING fts5(
                title, 
                content, 
                summary, 
                tags,
                importance,
                content='documents',
                content_rowid='rowid'
            )
        """)
    
    def _create_indexes(self, cursor):
        """Create performance indexes"""
        
        indexes = [
            "CREATE INDEX idx_documents_project ON documents(project_uuid)",
            "CREATE INDEX idx_documents_type ON documents(document_type)",
            "CREATE INDEX idx_documents_importance ON documents(importance)",
            "CREATE INDEX idx_documents_status ON documents(status)",
            "CREATE INDEX idx_documents_created ON documents(created_at)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def _insert_default_data(self, cursor, project_name: str, project_path: str):
        """Insert default data and project record"""
        
        # Generate project UUID
        project_uuid = self._generate_project_uuid(project_name)
        
        # Insert project record
        cursor.execute("""
            INSERT INTO projects (uuid, name, path, description, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            project_uuid, 
            project_name, 
            project_path,
            f"Memory Bank v2.1 project for {project_name}",
            '{"created_by": "migration_v21", "schema_version": "2.1"}'
        ))
        
        # Insert default semantic equivalents
        default_semantics = [
            ('spec_workflow', 'requirements', 'user_stories,acceptance_criteria,specifications'),
            ('development', 'implementation', 'coding,development,building,creating,programming'),
            ('dxt', 'DXT', 'desktop_extension,claude_extension,mcp_server')
        ]
        
        for domain, term, equivalents in default_semantics:
            cursor.execute("""
                INSERT INTO semantic_equivalents (domain, primary_term, equivalent_terms)
                VALUES (?, ?, ?)
            """, (domain, term, equivalents))
    
    def _generate_project_uuid(self, project_name: str) -> str:
        """Generate deterministic project UUID based on project name"""
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')
        project_uuid = str(uuid.uuid5(namespace, f"memorybank-v21-{project_name}"))
        return project_uuid
    
    def validate_v21_schema(self, database_path: str) -> Dict[str, Any]:
        """Validate that database has proper v2.1 schema"""
        try:
            conn = sqlite3.connect(database_path)
            cursor = conn.cursor()
            
            # Check version
            cursor.execute('PRAGMA user_version')
            version = cursor.fetchone()[0]
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            required_tables = {'projects', 'documents', 'documents_fts', 'semantic_equivalents'}
            missing_tables = required_tables - existing_tables
            
            # Check sample data
            cursor.execute("SELECT COUNT(*) FROM projects")
            project_count = cursor.fetchone()[0]
            
            conn.close()
            
            is_valid = (
                version == self.version_code and
                len(missing_tables) == 0 and
                project_count > 0
            )
            
            return {
                'valid': is_valid,
                'version': version,
                'expected_version': self.version_code,
                'total_tables': len(existing_tables),
                'missing_tables': list(missing_tables),
                'project_count': project_count,
                'message': 'Schema validation passed' if is_valid else 'Schema validation failed'
            }
            
        except Exception as e:
            logger.error(f"Schema validation failed: {e}")
            return {
                'valid': False,
                'error': str(e),
                'message': f'Schema validation error: {e}'
            }
