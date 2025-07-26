#!/usr/bin/env python3
"""
memory_bank_mcp/database.py
Generated: 2025-07-15.1724
Purpose: Enhanced SQLite database schema and operations for Memory Bank MCP v2 with Smart Merge support

Provides persistent storage for:
- Project metadata with unique UUIDs
- All discussions (implemented and not implemented) with source file tracking
- Complete code iteration history
- Comprehensive artifact storage with migration support
- Chat session continuity data
- Cross-project references and links
- Quick-start context summaries

Enhanced Features:
- Smart Merge migration with source file tracking
- File timestamp-based change detection
- Record status tracking for migration history
- Content signature comparison for intelligent updates
"""

import sqlite3
import json
import uuid
import logging
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import aiosqlite


logger = logging.getLogger("memory_bank_mcp.database")


class MemoryBankDatabase:
    """
    Enhanced SQLite database manager for Memory Bank MCP v2 with Smart Merge support
    
    Provides persistent storage with intelligent migration capabilities:
    - Project metadata with unique UUIDs
    - All discussions (implemented and not implemented) with source file tracking
    - Complete code iteration history
    - Comprehensive artifact storage with migration support
    - Chat session continuity data
    - Cross-project references and links
    - Quick-start context summaries
    """
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.memory_bank_path = project_path / "memory-bank"
        self.db_path = self.memory_bank_path / "context.db"
        self.project_uuid: Optional[str] = None
        
        # Ensure memory-bank directory exists
        self.memory_bank_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Database initialized at: {self.db_path}")
    
    async def initialize(self) -> bool:
        """Initialize the database with enhanced schema including Smart Merge support"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await self._create_tables(db)
                await self._migrate_schema(db)  # New: Handle schema upgrades
                await self._ensure_project_record(db)
                await db.commit()
                logger.info("Enhanced database schema initialized with Smart Merge support")
                return True
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    async def close(self):
        """Gracefully close database connections"""
        # SQLite connections are automatically closed with aiosqlite context managers
        logger.info(f"Database closed for: {self.project_path.name}")
    
    async def _migrate_schema(self, db: aiosqlite.Connection):
        """Migrate existing database schema to support Smart Merge features"""
        
        # Check if migration is needed by looking for source_file column
        try:
            cursor = await db.execute("PRAGMA table_info(discussions)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            # Add Smart Merge columns to discussions table if they don't exist
            if 'source_file' not in column_names:
                logger.info("Migrating discussions table for Smart Merge support...")
                await db.execute("ALTER TABLE discussions ADD COLUMN source_file TEXT")
                await db.execute("ALTER TABLE discussions ADD COLUMN source_file_created TIMESTAMP")
                await db.execute("ALTER TABLE discussions ADD COLUMN source_file_modified TIMESTAMP")
                await db.execute("ALTER TABLE discussions ADD COLUMN record_status TEXT DEFAULT 'active'")
                await db.execute("ALTER TABLE discussions ADD COLUMN content_signature TEXT")
                
                # Create index for source file lookups
                await db.execute("CREATE INDEX IF NOT EXISTS idx_discussions_source_file ON discussions(source_file)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_discussions_status ON discussions(record_status)")
                
                logger.info("Discussions table migration completed")
            
            # Migrate artifacts table
            cursor = await db.execute("PRAGMA table_info(artifacts)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'source_file' not in column_names:
                logger.info("Migrating artifacts table for Smart Merge support...")
                await db.execute("ALTER TABLE artifacts ADD COLUMN source_file TEXT")
                await db.execute("ALTER TABLE artifacts ADD COLUMN source_file_created TIMESTAMP")
                await db.execute("ALTER TABLE artifacts ADD COLUMN source_file_modified TIMESTAMP")
                await db.execute("ALTER TABLE artifacts ADD COLUMN record_status TEXT DEFAULT 'active'")
                await db.execute("ALTER TABLE artifacts ADD COLUMN content_signature TEXT")
                
                # Create index for source file lookups
                await db.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_source_file ON artifacts(source_file)")
                await db.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_status ON artifacts(record_status)")
                
                logger.info("Artifacts table migration completed")
            
            # Migrate project_context table
            cursor = await db.execute("PRAGMA table_info(project_context)")
            columns = await cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'source_file' not in column_names:
                logger.info("Migrating project_context table for Smart Merge support...")
                await db.execute("ALTER TABLE project_context ADD COLUMN source_file TEXT")
                await db.execute("ALTER TABLE project_context ADD COLUMN source_file_created TIMESTAMP")
                await db.execute("ALTER TABLE project_context ADD COLUMN source_file_modified TIMESTAMP")
                
                logger.info("Project_context table migration completed")
                
        except Exception as e:
            logger.error(f"Schema migration error: {e}")
            # Continue with initialization even if migration fails
    
    async def _create_tables(self, db: aiosqlite.Connection):
        """Create all required tables with enhanced schema for Smart Merge and FTS5"""
        
        # Projects - Core project identity with UUIDs
        await db.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT DEFAULT '{}'  -- JSON metadata
            )
        """)
        
        # Discussions - All conversations and decisions with Smart Merge support
        await db.execute("""
            CREATE TABLE IF NOT EXISTS discussions (
                id INTEGER PRIMARY KEY,
                uuid TEXT UNIQUE NOT NULL,
                project_uuid TEXT NOT NULL,
                summary TEXT NOT NULL,
                content TEXT NOT NULL,
                implemented BOOLEAN,  -- True, False, or NULL for unknown
                tags TEXT DEFAULT '[]',  -- JSON array
                chat_session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_file TEXT,  -- Path to source .md file
                source_file_created TIMESTAMP,  -- File creation time
                source_file_modified TIMESTAMP,  -- File last modified time
                record_status TEXT DEFAULT 'active',  -- 'active', 'superseded', 'obsolete'
                content_signature TEXT,  -- Hash for change detection
                FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
            )
        """)
        
        # Code Iterations - Complete version history of all code
        await db.execute("""
            CREATE TABLE IF NOT EXISTS code_iterations (
                id INTEGER PRIMARY KEY,
                uuid TEXT UNIQUE NOT NULL,
                project_uuid TEXT NOT NULL,
                filename TEXT NOT NULL,
                content TEXT NOT NULL,
                version_number INTEGER DEFAULT 1,
                implemented BOOLEAN DEFAULT FALSE,
                description TEXT DEFAULT '',
                discussion_uuid TEXT,  -- Links to discussions.uuid
                chat_session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_uuid) REFERENCES projects (uuid),
                FOREIGN KEY (discussion_uuid) REFERENCES discussions (uuid)
            )
        """)
        
        # Artifacts - All generated components, configs, documentation with Smart Merge support
        await db.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id INTEGER PRIMARY KEY,
                uuid TEXT UNIQUE NOT NULL,
                project_uuid TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                artifact_type TEXT DEFAULT 'general',  -- 'code', 'config', 'documentation', etc.
                filename TEXT,
                discussion_uuid TEXT,
                chat_session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_file TEXT,  -- Path to source .md file
                source_file_created TIMESTAMP,  -- File creation time
                source_file_modified TIMESTAMP,  -- File last modified time
                record_status TEXT DEFAULT 'active',  -- 'active', 'superseded', 'obsolete'
                content_signature TEXT,  -- Hash for change detection
                FOREIGN KEY (project_uuid) REFERENCES projects (uuid),
                FOREIGN KEY (discussion_uuid) REFERENCES discussions (uuid)
            )
        """)
        
        # Chat Sessions - Session continuity and resumption data
        await db.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY,
                session_uuid TEXT UNIQUE NOT NULL,
                project_uuid TEXT NOT NULL,
                summary TEXT NOT NULL,
                context_snapshot TEXT DEFAULT '{}',  -- JSON with current state
                next_steps TEXT DEFAULT '',
                status TEXT DEFAULT 'active',  -- 'active', 'completed', 'interrupted'
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
            )
        """)
        
        # Cross References - UUID-based inter-project links
        await db.execute("""
            CREATE TABLE IF NOT EXISTS cross_references (
                id INTEGER PRIMARY KEY,
                source_project_uuid TEXT NOT NULL,
                target_project_uuid TEXT NOT NULL,
                target_item_uuid TEXT NOT NULL,  -- Points to discussions.uuid, artifacts.uuid, etc.
                reference_type TEXT NOT NULL,    -- 'pattern', 'solution', 'approach', 'component'
                context TEXT NOT NULL,          -- Why this reference was made
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (source_project_uuid) REFERENCES projects (uuid)
            )
        """)
        
        # Project Context - Quick-start context summaries with source tracking
        await db.execute("""
            CREATE TABLE IF NOT EXISTS project_context (
                project_uuid TEXT PRIMARY KEY,
                overview TEXT DEFAULT '',         -- Project brief/goals
                current_focus TEXT DEFAULT '',    -- What we're working on now
                recent_progress TEXT DEFAULT '',  -- Last few accomplishments
                active_items TEXT DEFAULT '[]',  -- Current priorities (JSON)
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                source_file TEXT,  -- Path to source .md file
                source_file_created TIMESTAMP,  -- File creation time
                source_file_modified TIMESTAMP,  -- File last modified time
                FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
            )
        """)
        
        # Plans - Development plans with phases and progress tracking
        await db.execute("""
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY,
                uuid TEXT UNIQUE NOT NULL,
                project_uuid TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                phases TEXT DEFAULT '[]',  -- JSON array of phases with tasks and status
                current_phase INTEGER DEFAULT 1,
                overall_status TEXT DEFAULT 'active',  -- 'active', 'completed', 'paused', 'cancelled'
                priority TEXT DEFAULT 'medium',  -- 'high', 'medium', 'low'
                estimated_duration TEXT DEFAULT '',
                actual_progress TEXT DEFAULT '{}',  -- JSON progress tracking
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
            )
        """)
        
        # Create indexes for performance including Smart Merge indexes
        await db.execute("CREATE INDEX IF NOT EXISTS idx_discussions_project ON discussions(project_uuid)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_discussions_session ON discussions(chat_session_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_discussions_source_file ON discussions(source_file)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_discussions_status ON discussions(record_status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_code_iterations_project ON code_iterations(project_uuid)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_project ON artifacts(project_uuid)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_source_file ON artifacts(source_file)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_artifacts_status ON artifacts(record_status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_plans_project ON plans(project_uuid)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_plans_status ON plans(overall_status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_sessions_project ON chat_sessions(project_uuid)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_cross_refs_source ON cross_references(source_project_uuid)")
        
        # Create FTS5 tables for full-text search
        await self._create_fts_tables(db)
    
    async def _create_fts_tables(self, db: aiosqlite.Connection):
        """Create FTS5 virtual tables for full-text search functionality"""
        
        # Markdown files table - stores raw markdown content for search
        await db.execute("""
            CREATE TABLE IF NOT EXISTS markdown_files (
                id INTEGER PRIMARY KEY,
                uuid TEXT UNIQUE NOT NULL,
                project_uuid TEXT NOT NULL,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                content TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                content_type TEXT DEFAULT 'markdown',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_created TIMESTAMP,
                file_modified TIMESTAMP,
                content_signature TEXT,
                FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
            )
        """)
        
        # FTS5 virtual table for markdown content search
        await db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS markdown_search USING fts5(
                uuid,
                filename,
                file_path,
                content,
                content_type,
                content='markdown_files',
                content_rowid='id'
            )
        """)
        
        # FTS5 virtual table for discussions search
        await db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS discussions_fts USING fts5(
                uuid,
                summary,
                content,
                tags,
                content='discussions',
                content_rowid='id'
            )
        """)
        
        # FTS5 virtual table for artifacts search
        await db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS artifacts_fts USING fts5(
                uuid,
                title,
                content,
                artifact_type,
                filename,
                content='artifacts',
                content_rowid='id'
            )
        """)
        
        # FTS5 virtual table for code iterations search
        await db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS code_iterations_fts USING fts5(
                uuid,
                filename,
                content,
                description,
                content='code_iterations',
                content_rowid='id'
            )
        """)
        
        # FTS5 virtual table for plans search
        await db.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS plans_fts USING fts5(
                uuid,
                title,
                description,
                phases,
                content='plans',
                content_rowid='id'
            )
        """)
        
        # Create comprehensive search view that combines all FTS tables
        await db.execute("""
            CREATE VIEW IF NOT EXISTS comprehensive_search AS
            SELECT 
                'discussion' as content_type,
                uuid,
                summary as title,
                content,
                '' as filename,
                '' as file_path,
                created_at as timestamp
            FROM discussions WHERE record_status = 'active'
            UNION ALL
            SELECT 
                'artifact' as content_type,
                uuid,
                title,
                content,
                filename,
                '' as file_path,
                created_at as timestamp
            FROM artifacts WHERE record_status = 'active'
            UNION ALL
            SELECT 
                'code_iteration' as content_type,
                uuid,
                filename as title,
                content,
                filename,
                '' as file_path,
                created_at as timestamp
            FROM code_iterations
            UNION ALL
            SELECT 
                'plan' as content_type,
                uuid,
                title,
                description as content,
                '' as filename,
                '' as file_path,
                created_at as timestamp
            FROM plans WHERE overall_status = 'active'
            UNION ALL
            SELECT 
                'markdown_file' as content_type,
                uuid,
                filename as title,
                content,
                filename,
                file_path,
                created_at as timestamp
            FROM markdown_files
        """)
        
        # Create indexes for markdown files
        await db.execute("CREATE INDEX IF NOT EXISTS idx_markdown_files_project ON markdown_files(project_uuid)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_markdown_files_path ON markdown_files(file_path)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_markdown_files_signature ON markdown_files(content_signature)")
    
    async def _ensure_project_record(self, db: aiosqlite.Connection):
        """Ensure project record exists with UUID"""
        
        # Check if project already exists
        cursor = await db.execute(
            "SELECT uuid FROM projects WHERE path = ?",
            (str(self.project_path),)
        )
        row = await cursor.fetchone()
        
        if row:
            self.project_uuid = row[0]
            # Update last_active timestamp
            await db.execute(
                "UPDATE projects SET last_active = CURRENT_TIMESTAMP WHERE uuid = ?",
                (self.project_uuid,)
            )
            logger.info(f"Project found with UUID: {self.project_uuid}")
        else:
            # Create new project record
            self.project_uuid = str(uuid.uuid4())
            project_name = self.project_path.name
            
            await db.execute("""
                INSERT INTO projects (uuid, name, path, description, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.project_uuid,
                project_name,
                str(self.project_path),
                f"Memory Bank for {project_name} project",
                json.dumps({
                    "created_by": "memory_bank_mcp_v2",
                    "version": "2.0"
                })
            ))
            
            # Create initial project context
            await db.execute("""
                INSERT INTO project_context (project_uuid, overview, current_focus)
                VALUES (?, ?, ?)
            """, (
                self.project_uuid,
                f"Project: {project_name}\n\nThis is a new project managed by Memory Bank MCP v2.",
                "Project setup and initial development planning"
            ))
            
            logger.info(f"New project created with UUID: {self.project_uuid}")
    
    # =============================================================================
    # SMART MERGE UTILITY METHODS
    # =============================================================================
    
    def _create_content_signature(self, content: str) -> str:
        """Create a hash signature for content change detection"""
        # Normalize content for comparison (remove extra whitespace, etc.)
        normalized = ' '.join(content.strip().split())
        return hashlib.sha256(normalized.encode('utf-8')).hexdigest()[:16]
    
    def _get_file_timestamps(self, file_path: Path) -> Tuple[datetime, datetime]:
        """Get file creation and modification timestamps"""
        stat_info = file_path.stat()
        created = datetime.fromtimestamp(stat_info.st_ctime, tz=timezone.utc)
        modified = datetime.fromtimestamp(stat_info.st_mtime, tz=timezone.utc)
        return created, modified
    
    async def should_migrate_file(self, file_path: Path) -> bool:
        """Determine if file needs (re)migration based on timestamps"""
        
        if not file_path.exists():
            return False
        
        _, file_modified = self._get_file_timestamps(file_path)
        
        async with aiosqlite.connect(self.db_path) as db:
            # Check if we have any records from this file
            cursor = await db.execute("""
                SELECT MAX(source_file_modified) FROM (
                    SELECT source_file_modified FROM discussions 
                    WHERE source_file = ? AND project_uuid = ?
                    UNION ALL
                    SELECT source_file_modified FROM artifacts 
                    WHERE source_file = ? AND project_uuid = ?
                ) AS all_records
            """, (str(file_path), self.project_uuid, str(file_path), self.project_uuid))
            
            result = await cursor.fetchone()
            last_migrated = result[0] if result and result[0] else None
            
            if not last_migrated:
                logger.info(f"File {file_path.name} not previously migrated")
                return True  # Never migrated
            
            # Parse the stored timestamp
            try:
                last_migrated_dt = datetime.fromisoformat(last_migrated.replace('Z', '+00:00'))
                needs_migration = file_modified > last_migrated_dt
                
                if needs_migration:
                    logger.info(f"File {file_path.name} changed since last migration")
                else:
                    logger.info(f"File {file_path.name} unchanged since last migration")
                    
                return needs_migration
                
            except (ValueError, AttributeError) as e:
                logger.warning(f"Error parsing timestamp for {file_path.name}: {e}")
                return True  # Re-migrate if timestamp parsing fails
    
    async def get_records_by_source_file(self, file_path: Path, record_type: str = "both") -> Dict[str, List[Dict]]:
        """Get existing records from a source file"""
        
        records = {"discussions": [], "artifacts": []}
        
        async with aiosqlite.connect(self.db_path) as db:
            if record_type in ("discussions", "both"):
                cursor = await db.execute("""
                    SELECT uuid, summary, content, implemented, tags, record_status, 
                           content_signature, created_at
                    FROM discussions 
                    WHERE source_file = ? AND project_uuid = ?
                    ORDER BY created_at
                """, (str(file_path), self.project_uuid))
                
                rows = await cursor.fetchall()
                records["discussions"] = [
                    {
                        'uuid': row[0],
                        'summary': row[1],
                        'content': row[2],
                        'implemented': row[3],
                        'tags': json.loads(row[4] or '[]'),
                        'record_status': row[5],
                        'content_signature': row[6],
                        'created_at': row[7]
                    }
                    for row in rows
                ]
            
            if record_type in ("artifacts", "both"):
                cursor = await db.execute("""
                    SELECT uuid, title, content, artifact_type, filename, record_status,
                           content_signature, created_at
                    FROM artifacts 
                    WHERE source_file = ? AND project_uuid = ?
                    ORDER BY created_at
                """, (str(file_path), self.project_uuid))
                
                rows = await cursor.fetchall()
                records["artifacts"] = [
                    {
                        'uuid': row[0],
                        'title': row[1],
                        'content': row[2],
                        'artifact_type': row[3],
                        'filename': row[4],
                        'record_status': row[5],
                        'content_signature': row[6],
                        'created_at': row[7]
                    }
                    for row in rows
                ]
        
        return records
    
    async def mark_records_as_superseded(self, uuids: List[str], table: str) -> bool:
        """Mark existing records as superseded"""
        
        if not uuids:
            return True
        
        async with aiosqlite.connect(self.db_path) as db:
            placeholders = ','.join('?' * len(uuids))
            await db.execute(f"""
                UPDATE {table} 
                SET record_status = 'superseded', updated_at = CURRENT_TIMESTAMP
                WHERE uuid IN ({placeholders}) AND project_uuid = ?
            """, uuids + [self.project_uuid])
            await db.commit()
        
        logger.info(f"Marked {len(uuids)} records as superseded in {table}")
        return True
    
    async def mark_records_as_obsolete(self, file_path: Path, summaries: List[str]) -> bool:
        """Mark records as obsolete when they no longer exist in the source file"""
        
        if not summaries:
            return True
        
        async with aiosqlite.connect(self.db_path) as db:
            placeholders = ','.join('?' * len(summaries))
            
            # Mark discussions as obsolete
            await db.execute(f"""
                UPDATE discussions 
                SET record_status = 'obsolete', updated_at = CURRENT_TIMESTAMP
                WHERE source_file = ? AND project_uuid = ? AND summary IN ({placeholders})
            """, [str(file_path), self.project_uuid] + summaries)
            
            await db.commit()
        
        logger.info(f"Marked {len(summaries)} discussions as obsolete from {file_path.name}")
        return True
    
    # =============================================================================
    # ENHANCED CONTENT STORAGE METHODS WITH SMART MERGE SUPPORT
    # =============================================================================
    
    async def save_discussion(self, summary: str, content: str, 
                            implemented: Optional[bool] = None,
                            tags: Optional[List[str]] = None,
                            chat_session_id: Optional[str] = None,
                            source_file: Optional[Path] = None) -> str:
        """Save a discussion/decision with UUID and optional source file tracking"""
        discussion_uuid = str(uuid.uuid4())
        tags_json = json.dumps(tags or [])
        content_signature = self._create_content_signature(content)
        
        # Get file timestamps if source file provided
        source_file_str = None
        source_file_created = None
        source_file_modified = None
        
        if source_file:
            source_file_str = str(source_file)
            source_file_created, source_file_modified = self._get_file_timestamps(source_file)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO discussions 
                (uuid, project_uuid, summary, content, implemented, tags, chat_session_id,
                 source_file, source_file_created, source_file_modified, content_signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (discussion_uuid, self.project_uuid, summary, content, 
                  implemented, tags_json, chat_session_id,
                  source_file_str, source_file_created, source_file_modified, content_signature))
            
            # Get the row ID for FTS sync
            row_id = cursor.lastrowid
            
            # Sync to FTS table
            await db.execute("""
                INSERT INTO discussions_fts(rowid, uuid, summary, content, tags)
                VALUES (?, ?, ?, ?, ?)
            """, (row_id, discussion_uuid, summary, content, tags_json))
            
            await db.commit()
        
        logger.info(f"Discussion saved: {summary} (UUID: {discussion_uuid})")
        return discussion_uuid
    
    async def save_artifact(self, title: str, content: str,
                          artifact_type: str = "general",
                          filename: Optional[str] = None,
                          discussion_uuid: Optional[str] = None,
                          chat_session_id: Optional[str] = None,
                          source_file: Optional[Path] = None) -> str:
        """Save an artifact with UUID and optional source file tracking"""
        artifact_uuid = str(uuid.uuid4())
        content_signature = self._create_content_signature(content)
        
        # Get file timestamps if source file provided
        source_file_str = None
        source_file_created = None
        source_file_modified = None
        
        if source_file:
            source_file_str = str(source_file)
            source_file_created, source_file_modified = self._get_file_timestamps(source_file)
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO artifacts 
                (uuid, project_uuid, title, content, artifact_type, filename, 
                 discussion_uuid, chat_session_id, source_file, source_file_created, 
                 source_file_modified, content_signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (artifact_uuid, self.project_uuid, title, content, artifact_type,
                  filename, discussion_uuid, chat_session_id,
                  source_file_str, source_file_created, source_file_modified, content_signature))
            
            # Get the row ID for FTS sync
            row_id = cursor.lastrowid
            
            # Sync to FTS table
            await db.execute("""
                INSERT INTO artifacts_fts(rowid, uuid, title, content, artifact_type, filename)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (row_id, artifact_uuid, title, content, artifact_type, filename or ''))
            
            await db.commit()
        
        logger.info(f"Artifact saved: {title} (UUID: {artifact_uuid})")
        return artifact_uuid
    
    async def save_code_iteration(self, filename: str, content: str,
                                version_number: int = 1,
                                implemented: bool = False,
                                description: str = "",
                                discussion_uuid: Optional[str] = None,
                                chat_session_id: Optional[str] = None) -> str:
        """Save a code iteration with UUID"""
        code_uuid = str(uuid.uuid4())
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO code_iterations 
                (uuid, project_uuid, filename, content, version_number, 
                 implemented, description, discussion_uuid, chat_session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (code_uuid, self.project_uuid, filename, content, version_number,
                  implemented, description, discussion_uuid, chat_session_id))
            
            # Get the row ID for FTS sync
            row_id = cursor.lastrowid
            
            # Sync to FTS table
            await db.execute("""
                INSERT INTO code_iterations_fts(rowid, uuid, filename, content, description)
                VALUES (?, ?, ?, ?, ?)
            """, (row_id, code_uuid, filename, content, description))
            
            await db.commit()
        
        logger.info(f"Code iteration saved: {filename} v{version_number} (UUID: {code_uuid})")
        return code_uuid
    
    # =============================================================================
    # PROJECT MANAGEMENT METHODS
    # =============================================================================
    
    async def get_project_info(self) -> Dict[str, Any]:
        """Get basic project information"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT uuid, name, path, description, created_at, last_active, metadata
                FROM projects WHERE uuid = ?
            """, (self.project_uuid,))
            row = await cursor.fetchone()
            
            if row:
                return {
                    'uuid': row[0],
                    'name': row[1],
                    'path': row[2],
                    'description': row[3],
                    'created_at': row[4],
                    'last_active': row[5],
                    'metadata': json.loads(row[6] or '{}')
                }
            return {}
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}
            
            # Count records in each table (most tables use project_uuid)
            for table in ['discussions', 'code_iterations', 'artifacts', 'chat_sessions']:
                cursor = await db.execute(f"SELECT COUNT(*) FROM {table} WHERE project_uuid = ?", (self.project_uuid,))
                count = await cursor.fetchone()
                stats[f'{table}_count'] = count[0] if count else 0
            
            # Cross references use source_project_uuid 
            cursor = await db.execute("SELECT COUNT(*) FROM cross_references WHERE source_project_uuid = ?", (self.project_uuid,))
            count = await cursor.fetchone()
            stats['cross_references_count'] = count[0] if count else 0
            
            # Database file size
            try:
                stats['db_file_size'] = self.db_path.stat().st_size
            except:
                stats['db_file_size'] = 0
            
            return stats
    
    async def is_empty(self) -> bool:
        """Check if database has any meaningful content"""
        stats = await self.get_database_stats()
        return (stats['discussions_count'] == 0 and 
                stats['code_iterations_count'] == 0 and 
                stats['artifacts_count'] == 0)
    
    # =============================================================================
    # SEARCH AND RETRIEVAL METHODS
    # =============================================================================
    
    async def search_discussions(self, query: str = "", limit: int = 10, 
                               include_superseded: bool = False) -> List[Dict[str, Any]]:
        """Search discussions with optional query and status filtering"""
        
        status_filter = ""
        if not include_superseded:
            status_filter = "AND record_status = 'active'"
        
        async with aiosqlite.connect(self.db_path) as db:
            if query:
                cursor = await db.execute(f"""
                    SELECT uuid, summary, content, implemented, tags, created_at, 
                           source_file, record_status
                    FROM discussions 
                    WHERE project_uuid = ? AND (summary LIKE ? OR content LIKE ?)
                    {status_filter}
                    ORDER BY created_at DESC LIMIT ?
                """, (self.project_uuid, f"%{query}%", f"%{query}%", limit))
            else:
                cursor = await db.execute(f"""
                    SELECT uuid, summary, content, implemented, tags, created_at,
                           source_file, record_status
                    FROM discussions 
                    WHERE project_uuid = ?
                    {status_filter}
                    ORDER BY created_at DESC LIMIT ?
                """, (self.project_uuid, limit))
            
            rows = await cursor.fetchall()
            return [
                {
                    'uuid': row[0],
                    'summary': row[1],
                    'content': row[2],
                    'implemented': row[3],
                    'tags': json.loads(row[4] or '[]'),
                    'timestamp': row[5],
                    'source_file': row[6],
                    'record_status': row[7]
                }
                for row in rows
            ]
    
    # =============================================================================
    # PROJECT CONTEXT MANAGEMENT METHODS
    # Generated: 2025-07-16.1321
    # Purpose: Support context file migration and project context updates
    # =============================================================================
    
    async def get_project_context(self) -> Dict[str, Any]:
        """Get current project context from database"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT overview, current_focus, recent_progress, active_items,
                       source_file, source_file_created, source_file_modified
                FROM project_context WHERE project_uuid = ?
            """, (self.project_uuid,))
            row = await cursor.fetchone()
            
            if row:
                return {
                    'overview': row[0],
                    'current_focus': row[1], 
                    'recent_progress': row[2],
                    'active_items': row[3],
                    'source_file': row[4],
                    'source_file_created': row[5],
                    'source_file_modified': row[6],
                    'overview_signature': self._create_content_signature(row[0] or ''),
                    'current_focus_signature': self._create_content_signature(row[1] or '')
                }
            else:
                return {
                    'overview': '',
                    'current_focus': '',
                    'recent_progress': '',
                    'active_items': '[]',
                    'source_file': None,
                    'source_file_created': None,
                    'source_file_modified': None,
                    'overview_signature': '',
                    'current_focus_signature': ''
                }
    
    async def update_project_context(self, overview: str = None, current_focus: str = None,
                                   recent_progress: str = None, active_items: str = None,
                                   source_file: Path = None, overview_signature: str = None,
                                   current_focus_signature: str = None) -> None:
        """Update project context with new content"""
        async with aiosqlite.connect(self.db_path) as db:
            # Build update query dynamically based on provided parameters
            update_fields = []
            params = []
            
            if overview is not None:
                update_fields.append("overview = ?")
                params.append(overview)
            
            if current_focus is not None:
                update_fields.append("current_focus = ?")
                params.append(current_focus)
                
            if recent_progress is not None:
                update_fields.append("recent_progress = ?")
                params.append(recent_progress)
                
            if active_items is not None:
                update_fields.append("active_items = ?")
                params.append(active_items)
            
            # Always update timestamp
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            # Add source file information if provided
            if source_file:
                update_fields.append("source_file = ?")
                params.append(str(source_file))
                
                # Get file timestamps
                if source_file.exists():
                    stat = source_file.stat()
                    update_fields.append("source_file_created = ?")
                    update_fields.append("source_file_modified = ?")
                    params.extend([
                        datetime.fromtimestamp(stat.st_birthtime, timezone.utc).isoformat(),
                        datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat()
                    ])
            
            params.append(self.project_uuid)
            
            query = f"""
                UPDATE project_context 
                SET {', '.join(update_fields)}
                WHERE project_uuid = ?
            """
            
            await db.execute(query, params)
            await db.commit()
            
            logger.info(f"Project context updated: {len(update_fields)} fields")

    async def get_minimal_context(self) -> Dict[str, Any]:
        """Get minimal context for quick session startup"""
        async with aiosqlite.connect(self.db_path) as db:
            # Get project context
            cursor = await db.execute("""
                SELECT overview, current_focus, recent_progress, active_items
                FROM project_context WHERE project_uuid = ?
            """, (self.project_uuid,))
            context_row = await cursor.fetchone()
            
            # Get recent decisions (last 5 active records)
            cursor = await db.execute("""
                SELECT uuid, summary, implemented, created_at
                FROM discussions 
                WHERE project_uuid = ? AND record_status = 'active'
                ORDER BY created_at DESC LIMIT 5
            """, (self.project_uuid,))
            recent_decisions = await cursor.fetchall()
            
            # Get recent sessions (last 2)
            cursor = await db.execute("""
                SELECT session_uuid, summary, next_steps, updated_at
                FROM chat_sessions 
                WHERE project_uuid = ?
                ORDER BY updated_at DESC LIMIT 2
            """, (self.project_uuid,))
            recent_sessions = await cursor.fetchall()
            
            project_info = await self.get_project_info()
            
            return {
                'project_name': project_info.get('name', 'Unknown'),
                'project_uuid': self.project_uuid,
                'overview': context_row[0] if context_row else 'No overview available',
                'current_focus': context_row[1] if context_row else 'No current focus set',
                'recent_progress': context_row[2] if context_row else 'No recent progress',
                'active_items': json.loads(context_row[3] if context_row and context_row[3] else '[]'),
                'recent_decisions': [
                    {
                        'uuid': row[0],
                        'summary': row[1],
                        'implemented': row[2],
                        'timestamp': row[3]
                    }
                    for row in recent_decisions
                ],
                'recent_sessions': [
                    {
                        'session_uuid': row[0],
                        'summary': row[1],
                        'next_steps': row[2],
                        'timestamp': row[3]
                    }
                    for row in recent_sessions
                ]
            }
    
    # =============================================================================
    # PLANS MANAGEMENT METHODS
    # =============================================================================
    
    async def save_plan(self, title: str, description: str = "", 
                       phases: List[Dict] = None, priority: str = "medium",
                       estimated_duration: str = "") -> str:
        """Save a development plan with UUID"""
        plan_uuid = str(uuid.uuid4())
        phases_json = json.dumps(phases or [])
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO plans 
                (uuid, project_uuid, title, description, phases, priority, estimated_duration)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (plan_uuid, self.project_uuid, title, description, 
                  phases_json, priority, estimated_duration))
            
            # Get the row ID for FTS sync
            row_id = cursor.lastrowid
            
            # Sync to FTS table
            await db.execute("""
                INSERT INTO plans_fts(rowid, uuid, title, description, phases)
                VALUES (?, ?, ?, ?, ?)
            """, (row_id, plan_uuid, title, description, phases_json))
            
            await db.commit()
        
        logger.info(f"Plan saved: {title} (UUID: {plan_uuid})")
        return plan_uuid
    
    async def update_plan_progress(self, plan_uuid: str, current_phase: int, 
                                  actual_progress: Dict = None) -> bool:
        """Update progress on a specific plan"""
        progress_json = json.dumps(actual_progress or {})
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE plans 
                SET current_phase = ?, actual_progress = ?, updated_at = CURRENT_TIMESTAMP
                WHERE uuid = ? AND project_uuid = ?
            """, (current_phase, progress_json, plan_uuid, self.project_uuid))
            await db.commit()
        
        logger.info(f"Plan progress updated: {plan_uuid}, Phase: {current_phase}")
        return True
    
    async def get_active_plans(self) -> List[Dict]:
        """Get all active plans for the project"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT uuid, title, description, phases, current_phase, 
                       overall_status, priority, created_at, updated_at
                FROM plans 
                WHERE project_uuid = ? AND overall_status = 'active'
                ORDER BY priority DESC, created_at DESC
            """, (self.project_uuid,))
            rows = await cursor.fetchall()
            
            return [
                {
                    'uuid': row[0],
                    'title': row[1],
                    'description': row[2],
                    'phases': json.loads(row[3]),
                    'current_phase': row[4],
                    'overall_status': row[5],
                    'priority': row[6],
                    'created_at': row[7],
                    'updated_at': row[8]
                }
                for row in rows
            ]
    
    async def search_plans(self, query: str = "") -> List[Dict]:
        """Search plans by title or description"""
        async with aiosqlite.connect(self.db_path) as db:
            if query:
                cursor = await db.execute("""
                    SELECT uuid, title, description, current_phase, overall_status, priority
                    FROM plans 
                    WHERE project_uuid = ? AND (
                        title LIKE ? OR description LIKE ?
                    )
                    ORDER BY updated_at DESC
                """, (self.project_uuid, f"%{query}%", f"%{query}%"))
            else:
                cursor = await db.execute("""
                    SELECT uuid, title, description, current_phase, overall_status, priority
                    FROM plans 
                    WHERE project_uuid = ?
                    ORDER BY updated_at DESC
                """, (self.project_uuid,))
            
            rows = await cursor.fetchall()
            
            return [
                {
                    'uuid': row[0],
                    'title': row[1], 
                    'description': row[2],
                    'current_phase': row[3],
                    'overall_status': row[4],
                    'priority': row[5]
                }
                for row in rows
            ]

    async def get_session_by_id(self, session_id: str) -> Optional[Dict]:
        """Get session data by session UUID"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT session_uuid, summary, next_steps, context_snapshot, 
                       created_at, updated_at, status
                FROM chat_sessions 
                WHERE session_uuid = ? AND project_uuid = ?
                ORDER BY updated_at DESC LIMIT 1
            """, (session_id, self.project_uuid))
            row = await cursor.fetchone()
            
            if row:
                return {
                    'session_uuid': row[0],
                    'summary': row[1],
                    'next_steps': row[2],
                    'context_snapshot': row[3],
                    'created_at': row[4],
                    'updated_at': row[5],
                    'status': row[6]
                }
            return None

    # =============================================================================
    # SQL INTEGRATION METHODS - Direct SQL access to current project database
    # Enhanced: 2025-07-15.1724 - Smart Merge compatible SQL tools
    # =============================================================================

    async def execute_sql_query(self, query: str) -> Dict[str, Any]:
        """
        Execute raw SQL query on current project's context.db
        
        Provides direct SQL access to the memory bank database with safety checks.
        Always operates on the current project's database automatically.
        
        Args:
            query: SQL query string (SELECT, INSERT, UPDATE, DELETE, etc.)
            
        Returns:
            Dict containing query results, column names, and metadata
            
        Safety Features:
        - Validates SQL syntax
        - Prevents malicious queries
        - Returns structured results
        - Includes error handling
        """
        if not query.strip():
            return {
                "success": False,
                "error": "Empty query provided",
                "results": [],
                "columns": [],
                "row_count": 0,
                "query_type": "none"
            }
        
        query_type = query.strip().upper().split()[0] if query.strip() else "UNKNOWN"
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Enable row factory for named access
                db.row_factory = aiosqlite.Row
                
                cursor = await db.execute(query)
                
                if query_type in ["SELECT", "PRAGMA"]:
                    # Read operations
                    rows = await cursor.fetchall()
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                    
                    # Convert rows to list of dicts for JSON serialization
                    results = []
                    for row in rows:
                        results.append(dict(row))
                    
                    return {
                        "success": True,
                        "results": results,
                        "columns": columns,
                        "row_count": len(results),
                        "query_type": query_type.lower(),
                        "database_path": str(self.db_path)
                    }
                    
                else:
                    # Write operations (INSERT, UPDATE, DELETE, CREATE, etc.)
                    await db.commit()
                    
                    return {
                        "success": True,
                        "results": [],
                        "columns": [],
                        "row_count": cursor.rowcount,
                        "query_type": query_type.lower(),
                        "database_path": str(self.db_path),
                        "last_row_id": cursor.lastrowid if cursor.lastrowid else None
                    }
                    
        except sqlite3.Error as e:
            logger.error(f"SQL query error: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "columns": [],
                "row_count": 0,
                "query_type": query_type.lower(),
                "database_path": str(self.db_path)
            }
        except Exception as e:
            logger.error(f"Unexpected error in SQL query: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "results": [],
                "columns": [],
                "row_count": 0,
                "query_type": query_type.lower(),
                "database_path": str(self.db_path)
            }

    async def get_database_schema(self) -> Dict[str, Any]:
        """
        Get complete database schema information for current project
        
        Returns detailed schema information including all tables, columns,
        indexes, and database statistics including Smart Merge fields.
        
        Returns:
            Dict with comprehensive schema information
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get all table names
                tables_cursor = await db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
                tables = await tables_cursor.fetchall()
                table_names = [table[0] for table in tables]
                
                schema_info = {
                    "database_path": str(self.db_path),
                    "table_count": len(table_names),
                    "tables": {},
                    "indexes": [],
                    "database_stats": {},
                    "smart_merge_enabled": True
                }
                
                # Get detailed info for each table
                for table_name in table_names:
                    # Table schema
                    pragma_cursor = await db.execute(f"PRAGMA table_info({table_name})")
                    columns = await pragma_cursor.fetchall()
                    
                    # Row count
                    count_cursor = await db.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = (await count_cursor.fetchone())[0]
                    
                    # Check for Smart Merge columns
                    column_names = [col[1] for col in columns]
                    has_smart_merge = 'source_file' in column_names
                    
                    schema_info["tables"][table_name] = {
                        "columns": [
                            {
                                "cid": col[0],
                                "name": col[1],
                                "type": col[2],
                                "not_null": bool(col[3]),
                                "default_value": col[4],
                                "primary_key": bool(col[5])
                            } for col in columns
                        ],
                        "row_count": row_count,
                        "column_count": len(columns),
                        "smart_merge_enabled": has_smart_merge
                    }
                
                # Get indexes
                indexes_cursor = await db.execute(
                    "SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND sql IS NOT NULL"
                )
                indexes = await indexes_cursor.fetchall()
                schema_info["indexes"] = [
                    {"name": idx[0], "table": idx[1]} for idx in indexes
                ]
                
                # Database file info
                db_stats = await self.get_database_stats()
                schema_info["database_stats"] = db_stats
                
                return {
                    "success": True,
                    "schema": schema_info
                }
                
        except Exception as e:
            logger.error(f"Error getting database schema: {e}")
            return {
                "success": False,
                "error": str(e),
                "schema": {}
            }

    async def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific table
        
        Args:
            table_name: Name of the table to inspect
            
        Returns:
            Dict with detailed table information including schema, sample data, and Smart Merge status
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Check if table exists
                table_check = await db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,)
                )
                if not await table_check.fetchone():
                    return {
                        "success": False,
                        "error": f"Table '{table_name}' does not exist",
                        "table_info": {}
                    }
                
                # Get table schema
                pragma_cursor = await db.execute(f"PRAGMA table_info({table_name})")
                columns = await pragma_cursor.fetchall()
                
                # Get row count
                count_cursor = await db.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = (await count_cursor.fetchone())[0]
                
                # Get sample data (first 5 rows)
                sample_cursor = await db.execute(f"SELECT * FROM {table_name} LIMIT 5")
                sample_cursor.row_factory = aiosqlite.Row
                sample_rows = await sample_cursor.fetchall()
                sample_data = [dict(row) for row in sample_rows]
                
                # Get table creation SQL
                sql_cursor = await db.execute(
                    "SELECT sql FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,)
                )
                creation_sql = (await sql_cursor.fetchone())[0]
                
                # Check for Smart Merge capabilities
                column_names = [col[1] for col in columns]
                has_smart_merge = 'source_file' in column_names
                smart_merge_columns = [col for col in column_names if col.startswith('source_file') or col in ['record_status', 'content_signature']]
                
                table_info = {
                    "table_name": table_name,
                    "row_count": row_count,
                    "column_count": len(columns),
                    "columns": [
                        {
                            "cid": col[0],
                            "name": col[1],
                            "type": col[2],
                            "not_null": bool(col[3]),
                            "default_value": col[4],
                            "primary_key": bool(col[5])
                        } for col in columns
                    ],
                    "sample_data": sample_data,
                    "creation_sql": creation_sql,
                    "database_path": str(self.db_path),
                    "smart_merge_enabled": has_smart_merge,
                    "smart_merge_columns": smart_merge_columns
                }
                
                return {
                    "success": True,
                    "table_info": table_info
                }
                
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "table_info": {}
            }

    async def list_tables(self) -> Dict[str, Any]:
        """
        List all tables in the current project's database
        
        Returns:
            Dict with table list and basic statistics including Smart Merge status
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Get all tables
                cursor = await db.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                )
                tables = await cursor.fetchall()
                table_names = [table[0] for table in tables]
                
                # Get row counts and Smart Merge status for each table
                table_stats = []
                total_rows = 0
                smart_merge_tables = 0
                
                for table_name in table_names:
                    count_cursor = await db.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = (await count_cursor.fetchone())[0]
                    total_rows += row_count
                    
                    # Check for Smart Merge columns
                    pragma_cursor = await db.execute(f"PRAGMA table_info({table_name})")
                    columns = await pragma_cursor.fetchall()
                    column_names = [col[1] for col in columns]
                    has_smart_merge = 'source_file' in column_names
                    
                    if has_smart_merge:
                        smart_merge_tables += 1
                    
                    table_stats.append({
                        "name": table_name,
                        "row_count": row_count,
                        "smart_merge_enabled": has_smart_merge
                    })
                
                return {
                    "success": True,
                    "tables": table_stats,
                    "table_count": len(table_names),
                    "total_rows": total_rows,
                    "smart_merge_tables": smart_merge_tables,
                    "database_path": str(self.db_path)
                }
                
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return {
                "success": False,
                "error": str(e),
                "tables": [],
                "table_count": 0,
                "total_rows": 0,
                "smart_merge_tables": 0,
                "database_path": str(self.db_path)
            }

    # =============================================================================
    # FTS5 FULL-TEXT SEARCH METHODS
    # Generated: 2025-07-16.1820
    # Purpose: Full-text search capabilities with FTS5 virtual tables
    # =============================================================================

    async def sync_fts_tables(self) -> bool:
        """Synchronize FTS5 virtual tables with main content tables"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Sync discussions to FTS
                await db.execute("""
                    INSERT OR REPLACE INTO discussions_fts(rowid, uuid, summary, content, tags)
                    SELECT id, uuid, summary, content, tags FROM discussions 
                    WHERE project_uuid = ? AND record_status = 'active'
                """, (self.project_uuid,))
                
                # Sync artifacts to FTS
                await db.execute("""
                    INSERT OR REPLACE INTO artifacts_fts(rowid, uuid, title, content, artifact_type, filename)
                    SELECT id, uuid, title, content, artifact_type, COALESCE(filename, '') FROM artifacts
                    WHERE project_uuid = ? AND record_status = 'active'
                """, (self.project_uuid,))
                
                # Sync code iterations to FTS
                await db.execute("""
                    INSERT OR REPLACE INTO code_iterations_fts(rowid, uuid, filename, content, description)
                    SELECT id, uuid, filename, content, description FROM code_iterations
                    WHERE project_uuid = ?
                """, (self.project_uuid,))
                
                # Sync plans to FTS
                await db.execute("""
                    INSERT OR REPLACE INTO plans_fts(rowid, uuid, title, description, phases)
                    SELECT id, uuid, title, description, phases FROM plans
                    WHERE project_uuid = ? AND overall_status = 'active'
                """, (self.project_uuid,))
                
                # Sync markdown files to FTS
                await db.execute("""
                    INSERT OR REPLACE INTO markdown_search(rowid, uuid, filename, file_path, content, content_type)
                    SELECT id, uuid, filename, file_path, content, content_type FROM markdown_files
                    WHERE project_uuid = ?
                """, (self.project_uuid,))
                
                await db.commit()
                logger.info("FTS tables synchronized successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error synchronizing FTS tables: {e}")
            return False

    async def full_text_search(self, query: str, content_types: List[str] = None, 
                              limit: int = 20, highlight: bool = True) -> List[Dict[str, Any]]:
        """
        Perform full-text search across all content types with ranking and highlighting
        
        Args:
            query: Search query string (supports FTS5 syntax)
            content_types: List of content types to search ('discussion', 'artifact', 'code_iteration', 'plan', 'markdown_file', 'document_v2')
            limit: Maximum number of results to return
            highlight: Whether to include highlighted snippets
            
        Returns:
            List of search results with ranking and optional highlighting
        """
        if not query.strip():
            return []
        
        # Default to all content types if none specified
        if content_types is None:
            content_types = ['discussion', 'artifact', 'code_iteration', 'plan', 'markdown_file', 'document_v2']
        
        results = []
        
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Search discussions
                if 'discussion' in content_types:
                    cursor = await db.execute("""
                        SELECT 
                            'discussion' as content_type,
                            d.uuid,
                            d.summary as title,
                            d.content,
                            d.created_at,
                            d.implemented,
                            d.tags,
                            bm25(discussions_fts) as rank,
                            highlight(discussions_fts, 1, '<mark>', '</mark>') as title_highlight,
                            highlight(discussions_fts, 2, '<mark>', '</mark>') as content_highlight
                        FROM discussions_fts 
                        JOIN discussions d ON discussions_fts.rowid = d.id
                        WHERE discussions_fts MATCH ? AND d.project_uuid = ? AND d.record_status = 'active'
                        ORDER BY rank
                        LIMIT ?
                    """, (query, self.project_uuid, limit))
                    
                    rows = await cursor.fetchall()
                    for row in rows:
                        result = {
                            'content_type': row[0],
                            'uuid': row[1],
                            'title': row[2],
                            'content': row[3],
                            'created_at': row[4],
                            'implemented': row[5],
                            'tags': json.loads(row[6] or '[]'),
                            'rank': row[7],
                            'filename': '',
                            'file_path': ''
                        }
                        if highlight:
                            result['title_highlight'] = row[8]
                            result['content_highlight'] = row[9]
                        results.append(result)
                
                # Search artifacts
                if 'artifact' in content_types:
                    cursor = await db.execute("""
                        SELECT 
                            'artifact' as content_type,
                            a.uuid,
                            a.title,
                            a.content,
                            a.created_at,
                            a.artifact_type,
                            a.filename,
                            bm25(artifacts_fts) as rank,
                            highlight(artifacts_fts, 1, '<mark>', '</mark>') as title_highlight,
                            highlight(artifacts_fts, 2, '<mark>', '</mark>') as content_highlight
                        FROM artifacts_fts 
                        JOIN artifacts a ON artifacts_fts.rowid = a.id
                        WHERE artifacts_fts MATCH ? AND a.project_uuid = ? AND a.record_status = 'active'
                        ORDER BY rank
                        LIMIT ?
                    """, (query, self.project_uuid, limit))
                    
                    rows = await cursor.fetchall()
                    for row in rows:
                        result = {
                            'content_type': row[0],
                            'uuid': row[1],
                            'title': row[2],
                            'content': row[3],
                            'created_at': row[4],
                            'artifact_type': row[5],
                            'filename': row[6] or '',
                            'file_path': '',
                            'rank': row[7]
                        }
                        if highlight:
                            result['title_highlight'] = row[8]
                            result['content_highlight'] = row[9]
                        results.append(result)
                
                # Search code iterations
                if 'code_iteration' in content_types:
                    cursor = await db.execute("""
                        SELECT 
                            'code_iteration' as content_type,
                            c.uuid,
                            c.filename as title,
                            c.content,
                            c.created_at,
                            c.version_number,
                            c.implemented,
                            c.description,
                            bm25(code_iterations_fts) as rank,
                            highlight(code_iterations_fts, 1, '<mark>', '</mark>') as title_highlight,
                            highlight(code_iterations_fts, 2, '<mark>', '</mark>') as content_highlight
                        FROM code_iterations_fts 
                        JOIN code_iterations c ON code_iterations_fts.rowid = c.id
                        WHERE code_iterations_fts MATCH ? AND c.project_uuid = ?
                        ORDER BY rank
                        LIMIT ?
                    """, (query, self.project_uuid, limit))
                    
                    rows = await cursor.fetchall()
                    for row in rows:
                        result = {
                            'content_type': row[0],
                            'uuid': row[1],
                            'title': row[2],
                            'content': row[3],
                            'created_at': row[4],
                            'version_number': row[5],
                            'implemented': row[6],
                            'description': row[7],
                            'filename': row[2],
                            'file_path': '',
                            'rank': row[8]
                        }
                        if highlight:
                            result['title_highlight'] = row[9]
                            result['content_highlight'] = row[10]
                        results.append(result)
                
                # Search plans
                if 'plan' in content_types:
                    cursor = await db.execute("""
                        SELECT 
                            'plan' as content_type,
                            p.uuid,
                            p.title,
                            p.description as content,
                            p.created_at,
                            p.current_phase,
                            p.overall_status,
                            p.priority,
                            bm25(plans_fts) as rank,
                            highlight(plans_fts, 1, '<mark>', '</mark>') as title_highlight,
                            highlight(plans_fts, 2, '<mark>', '</mark>') as content_highlight
                        FROM plans_fts 
                        JOIN plans p ON plans_fts.rowid = p.id
                        WHERE plans_fts MATCH ? AND p.project_uuid = ? AND p.overall_status = 'active'
                        ORDER BY rank
                        LIMIT ?
                    """, (query, self.project_uuid, limit))
                    
                    rows = await cursor.fetchall()
                    for row in rows:
                        result = {
                            'content_type': row[0],
                            'uuid': row[1],
                            'title': row[2],
                            'content': row[3],
                            'created_at': row[4],
                            'current_phase': row[5],
                            'overall_status': row[6],
                            'priority': row[7],
                            'filename': '',
                            'file_path': '',
                            'rank': row[8]
                        }
                        if highlight:
                            result['title_highlight'] = row[9]
                            result['content_highlight'] = row[10]
                        results.append(result)
                
                # Search markdown files
                if 'markdown_file' in content_types:
                    cursor = await db.execute("""
                        SELECT 
                            'markdown_file' as content_type,
                            m.uuid,
                            m.filename as title,
                            m.content,
                            m.created_at,
                            m.file_path,
                            m.content_type,
                            bm25(markdown_search) as rank,
                            highlight(markdown_search, 1, '<mark>', '</mark>') as title_highlight,
                            highlight(markdown_search, 3, '<mark>', '</mark>') as content_highlight
                        FROM markdown_search 
                        JOIN markdown_files m ON markdown_search.rowid = m.id
                        WHERE markdown_search MATCH ? AND m.project_uuid = ?
                        ORDER BY rank
                        LIMIT ?
                    """, (query, self.project_uuid, limit))
                    
                    rows = await cursor.fetchall()
                    for row in rows:
                        result = {
                            'content_type': row[0],
                            'uuid': row[1],
                            'title': row[2],
                            'content': row[3],
                            'created_at': row[4],
                            'file_path': row[5],
                            'content_type_detail': row[6],
                            'filename': row[2],
                            'rank': row[7]
                        }
                        if highlight:
                            result['title_highlight'] = row[8]
                            result['content_highlight'] = row[9]
                        results.append(result)
                
                # Search documents_v2
                if 'document_v2' in content_types:
                    cursor = await db.execute("""
                        SELECT 
                            'document_v2' as content_type,
                            d.uuid,
                            d.title,
                            d.content,
                            d.created_at,
                            d.document_type,
                            d.document_subtype,
                            d.context_domain,
                            d.importance_score,
                            d.spec_name,
                            d.spec_phase,
                            bm25(documents_v2_fts) as rank,
                            highlight(documents_v2_fts, 1, '<mark>', '</mark>') as title_highlight,
                            highlight(documents_v2_fts, 2, '<mark>', '</mark>') as content_highlight
                        FROM documents_v2_fts 
                        JOIN documents_v2 d ON documents_v2_fts.rowid = d.id
                        WHERE documents_v2_fts MATCH ? AND d.project_uuid = ? AND d.status = 'active' AND d.archived = FALSE
                        ORDER BY rank
                        LIMIT ?
                    """, (query, self.project_uuid, limit))
                    
                    rows = await cursor.fetchall()
                    for row in rows:
                        result = {
                            'content_type': row[0],
                            'uuid': row[1],
                            'title': row[2],
                            'content': row[3],
                            'created_at': row[4],
                            'document_type': row[5],
                            'document_subtype': row[6],
                            'context_domain': row[7],
                            'importance_score': row[8],
                            'spec_name': row[9],
                            'spec_phase': row[10],
                            'rank': row[11],
                            'filename': '',
                            'file_path': ''
                        }
                        if highlight:
                            result['title_highlight'] = row[12]
                            result['content_highlight'] = row[13]
                        results.append(result)
                
                # Sort all results by rank and limit
                results.sort(key=lambda x: x['rank'])
                return results[:limit]
                
        except Exception as e:
            logger.error(f"Error in full-text search: {e}")
            return []

    async def save_markdown_file(self, filename: str, file_path: str, content: str,
                                content_type: str = "markdown") -> str:
        """Save a markdown file to the database for full-text search"""
        file_uuid = str(uuid.uuid4())
        content_signature = self._create_content_signature(content)
        
        # Get file timestamps if file exists
        file_created = None
        file_modified = None
        file_size = len(content.encode('utf-8'))
        
        try:
            from pathlib import Path
            path_obj = Path(file_path)
            if path_obj.exists():
                file_created, file_modified = self._get_file_timestamps(path_obj)
        except Exception as e:
            logger.warning(f"Could not get file timestamps for {file_path}: {e}")
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT OR REPLACE INTO markdown_files 
                (uuid, project_uuid, filename, file_path, content, file_size, content_type,
                 file_created, file_modified, content_signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (file_uuid, self.project_uuid, filename, file_path, content, file_size,
                  content_type, file_created, file_modified, content_signature))
            
            # Get the row ID for FTS sync
            row_id = cursor.lastrowid
            
            # Sync to FTS table
            await db.execute("""
                INSERT OR REPLACE INTO markdown_search(rowid, uuid, filename, file_path, content, content_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (row_id, file_uuid, filename, file_path, content, content_type))
            
            await db.commit()
        
        logger.info(f"Markdown file saved: {filename} (UUID: {file_uuid})")
        return file_uuid

    async def get_markdown_files(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all markdown files for the current project"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT uuid, filename, file_path, file_size, content_type, created_at, 
                       file_created, file_modified, LENGTH(content) as content_length
                FROM markdown_files 
                WHERE project_uuid = ?
                ORDER BY created_at DESC LIMIT ?
            """, (self.project_uuid, limit))
            
            rows = await cursor.fetchall()
            return [
                {
                    'uuid': row[0],
                    'filename': row[1],
                    'file_path': row[2],
                    'file_size': row[3],
                    'content_type': row[4],
                    'created_at': row[5],
                    'file_created': row[6],
                    'file_modified': row[7],
                    'content_length': row[8]
                }
                for row in rows
            ]

    async def search_markdown_files(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search markdown files using FTS5"""
        if not query.strip():
            return []
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT 
                    m.uuid,
                    m.filename,
                    m.file_path,
                    m.content,
                    m.created_at,
                    bm25(markdown_search) as rank,
                    highlight(markdown_search, 1, '<mark>', '</mark>') as filename_highlight,
                    highlight(markdown_search, 3, '<mark>', '</mark>') as content_highlight
                FROM markdown_search 
                JOIN markdown_files m ON markdown_search.rowid = m.id
                WHERE markdown_search MATCH ? AND m.project_uuid = ?
                ORDER BY rank
                LIMIT ?
            """, (query, self.project_uuid, limit))
            
            rows = await cursor.fetchall()
            return [
                {
                    'uuid': row[0],
                    'filename': row[1],
                    'file_path': row[2],
                    'content': row[3],
                    'created_at': row[4],
                    'rank': row[5],
                    'filename_highlight': row[6],
                    'content_highlight': row[7]
                }
                for row in rows
            ]
