#!/usr/bin/env python3
"""
memory_bank_mcp/context_manager.py
Generated: 2025-07-13.2004
Purpose: Session persistence and graceful project switching for Memory Bank MCP v2

Provides:
- Session state management and persistence
- Automatic context saving after every exchange
- Graceful project switching with context preservation
- Minimal context loading for quick session starts
- Safe database connection management
"""

import json
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict

from .database import MemoryBankDatabase

logger = logging.getLogger("memory_bank_mcp.context_manager")


@dataclass
class ExchangeContext:
    """Represents a single user-assistant exchange"""
    user_message: str
    assistant_response: str
    artifacts_created: List[str]
    discussions_logged: List[str]
    code_iterations: List[str]
    timestamp: str


@dataclass 
class SessionState:
    """Current session state information"""
    session_uuid: str
    project_uuid: str
    project_path: str
    current_focus: str
    exchanges: List[ExchangeContext]
    last_save: str
    total_exchanges: int


class ContextManager:
    """
    Enhanced Context Manager for Memory Bank MCP v2
    
    Manages session persistence, graceful project switching, and automatic context saving.
    Provides seamless continuity across chat sessions and safe database operations.
    """
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.database: Optional[MemoryBankDatabase] = None
        self.current_session: Optional[SessionState] = None
        self.exchange_count = 0
        self.auto_save_enabled = True
        self._initialized = False
        
    async def initialize(self) -> bool:
        """Initialize the context manager and database"""
        try:
            self.database = MemoryBankDatabase(self.project_path)
            success = await self.database.initialize()
            if success:
                self._initialized = True
                # Automatically start a new session
                session_uuid = await self.start_new_session()
                logger.info(f"Context manager initialized for: {self.project_path} with session: {session_uuid}")
                return True
            else:
                logger.error(f"Failed to initialize database for: {self.project_path}")
                return False
        except Exception as e:
            logger.error(f"Context manager initialization failed: {e}")
            return False
    
    async def close(self):
        """Gracefully close the context manager and database"""
        if self.current_session and self.auto_save_enabled:
            # Save current session before closing
            await self.force_save_context("Context manager closing")
        
        if self.database:
            await self.database.close()
            
        self._initialized = False
        logger.info(f"Context manager closed for: {self.project_path.name}")
    
    def is_initialized(self) -> bool:
        """Check if context manager is properly initialized"""
        return self._initialized and self.database is not None
    
    @property
    def database_path(self) -> str:
        """Get the path to the current project's context database"""
        if self.database and hasattr(self.database, 'db_path'):
            return str(self.database.db_path)
        # Fallback: construct path if database not initialized yet
        return str(self.project_path / "memory-bank" / "context.db")
    
    # Session Management
    
    async def start_new_session(self, resume_session_uuid: Optional[str] = None) -> str:
        """Start a new session or resume an existing one"""
        
        if not self.is_initialized():
            raise RuntimeError("Context manager not initialized")
        
        # Try to resume session if UUID provided
        if resume_session_uuid:
            session_data = await self._get_session_data(resume_session_uuid)
            if session_data:
                logger.info(f"Resuming session: {resume_session_uuid}")
                session_uuid = resume_session_uuid
                
                # Restore session state from database
                context_snapshot = json.loads(session_data.get('context_snapshot', '{}'))
                self.current_session = SessionState(
                    session_uuid=session_uuid,
                    project_uuid=self.database.project_uuid,
                    project_path=str(self.project_path),
                    current_focus=context_snapshot.get('current_focus', 'Resuming previous session'),
                    exchanges=[],  # Don't restore full exchange history for performance
                    last_save=session_data.get('updated_at', datetime.now(timezone.utc).isoformat()),
                    total_exchanges=context_snapshot.get('total_exchanges', 0)
                )
                self.exchange_count = self.current_session.total_exchanges
                return session_uuid
        
        # Create new session
        session_uuid = str(uuid.uuid4())
        project_info = await self.database.get_project_info()
        
        self.current_session = SessionState(
            session_uuid=session_uuid,
            project_uuid=self.database.project_uuid,
            project_path=str(self.project_path),
            current_focus=f"New session started for {project_info.get('name', 'Unknown')} project",
            exchanges=[],
            last_save=datetime.now(timezone.utc).isoformat(),
            total_exchanges=0
        )
        
        # Save initial session state
        await self._save_session_state("Session initialized")
        
        logger.info(f"Started new session: {session_uuid}")
        return session_uuid
    
    async def get_minimal_context(self) -> Dict[str, Any]:
        """Get minimal context for quick session startup"""
        if not self.is_initialized():
            return {'error': 'Context manager not initialized'}
        
        return await self.database.get_minimal_context()
    
    async def get_current_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        if not self.current_session:
            return {'error': 'No active session'}
        
        return {
            'session_uuid': self.current_session.session_uuid,
            'project_uuid': self.current_session.project_uuid,
            'project_path': self.current_session.project_path,
            'current_focus': self.current_session.current_focus,
            'total_exchanges': self.current_session.total_exchanges,
            'last_save': self.current_session.last_save,
            'auto_save_enabled': self.auto_save_enabled
        }
    
    async def force_save_context(self, reason: str = "Manual save") -> Dict[str, Any]:
        """Force save current context and return summary"""
        if not self.current_session:
            return {'error': 'No active session to save'}
        
        await self._save_session_state(reason)
        self.current_session.last_save = datetime.now(timezone.utc).isoformat()
        
        summary = {
            'session_uuid': self.current_session.session_uuid,
            'project_name': self.project_path.name,
            'total_exchanges': self.current_session.total_exchanges,
            'last_save': self.current_session.last_save,
            'current_focus': self.current_session.current_focus
        }
        
        logger.info(f"Force saved context: {reason}")
        return summary
    
    async def auto_save_context(self, activity_description: str = "") -> None:
        """
        Auto-save context after each exchange - transparent background operation
        
        This method is called automatically after every exchange to ensure no context is lost.
        Unlike force_save_context(), this is silent and doesn't return status information.
        """
        if not self.auto_save_enabled or not self.is_initialized():
            return
        
        if not self.current_session:
            logger.warning("Auto-save attempted but no active session")
            return
        
        # Increment exchange count
        self.exchange_count += 1
        self.current_session.total_exchanges = self.exchange_count
        
        # Update last save timestamp
        self.current_session.last_save = datetime.now(timezone.utc).isoformat()
        
        # Save session state silently
        try:
            await self._save_session_state(f"Auto-save: {activity_description}" if activity_description else "Auto-save after exchange")
            
            # Log for debugging but don't notify user
            logger.debug(f"Auto-saved context after exchange {self.exchange_count}: {activity_description}")
            
        except Exception as e:
            logger.error(f"Auto-save failed: {e}")
            # Don't raise exception - auto-save failures shouldn't interrupt user workflow
    
    async def switch_to_project(self, new_project_path: Path) -> Dict[str, Any]:
        """Gracefully switch to a different project"""
        
        old_project_name = self.project_path.name if self.project_path else "None"
        
        # 1. Save current context if we have one
        old_session_uuid = None
        if self.current_session:
            summary = await self.force_save_context("Switching projects")
            old_session_uuid = summary.get('session_uuid')
        
        # 2. Close current database connection
        if self.database:
            await self.close()
        
        # 3. Switch to new project
        self.project_path = new_project_path
        self.current_session = None
        self.exchange_count = 0
        
        # 4. Initialize new project context
        success = await self.initialize()
        if not success:
            raise RuntimeError(f"Failed to initialize new project: {new_project_path}")
        
        # 5. Start new session
        new_session_uuid = await self.start_new_session()
        
        switch_info = {
            'old_project': old_project_name,
            'new_project': self.project_path.name,
            'old_session_uuid': old_session_uuid,
            'new_session_uuid': new_session_uuid,
            'switch_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(f"Project switched: {old_project_name} → {self.project_path.name}")
        return switch_info
    
    # Private Helper Methods
    
    async def _save_session_state(self, summary: str) -> None:
        """Save current session state to database"""
        if not self.current_session or not self.database:
            return
        
        # Create context snapshot
        context_snapshot = {
            'current_focus': self.current_session.current_focus,
            'total_exchanges': self.current_session.total_exchanges,
            'project_path': self.current_session.project_path
        }
        
        # Save to database
        await self._save_session_to_db(
            session_uuid=self.current_session.session_uuid,
            summary=summary,
            context_snapshot=context_snapshot,
            next_steps="Continue development session"
        )
    
    async def _save_session_to_db(self, session_uuid: str, summary: str, 
                                context_snapshot: Dict[str, Any], next_steps: str) -> None:
        """Save session data to database"""
        import aiosqlite
        
        async with aiosqlite.connect(self.database.db_path) as db:
            # Check if session exists
            cursor = await db.execute(
                "SELECT id FROM chat_sessions WHERE session_uuid = ?",
                (session_uuid,)
            )
            exists = await cursor.fetchone()
            
            if exists:
                # Update existing session
                await db.execute("""
                    UPDATE chat_sessions 
                    SET summary = ?, context_snapshot = ?, next_steps = ?, 
                        updated_at = CURRENT_TIMESTAMP
                    WHERE session_uuid = ?
                """, (summary, json.dumps(context_snapshot), next_steps, session_uuid))
            else:
                # Insert new session
                await db.execute("""
                    INSERT INTO chat_sessions 
                    (session_uuid, project_uuid, summary, context_snapshot, next_steps, status)
                    VALUES (?, ?, ?, ?, ?, 'active')
                """, (session_uuid, self.database.project_uuid, summary, 
                      json.dumps(context_snapshot), next_steps))
            
            await db.commit()
    
    async def _get_session_data(self, session_uuid: str) -> Optional[Dict[str, Any]]:
        """Retrieve session data from database"""
        import aiosqlite
        
        async with aiosqlite.connect(self.database.db_path) as db:
            cursor = await db.execute("""
                SELECT summary, context_snapshot, next_steps, status, updated_at
                FROM chat_sessions WHERE session_uuid = ?
            """, (session_uuid,))
            row = await cursor.fetchone()
            
            if row:
                return {
                    'summary': row[0],
                    'context_snapshot': row[1],
                    'next_steps': row[2],
                    'status': row[3],
                    'updated_at': row[4]
                }
            return None
