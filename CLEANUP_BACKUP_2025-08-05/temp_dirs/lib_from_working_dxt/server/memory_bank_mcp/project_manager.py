#!/usr/bin/env python3
"""
memory_bank_mcp/project_manager.py
Generated: 2025-07-13.2004
Purpose: Project detection, initialization, and management for Memory Bank MCP v2

Provides:
- Project detection and status analysis
- New project initialization
- Migration from existing memory-bank/ folders
- Project listing and management utilities
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from .database import MemoryBankDatabase

logger = logging.getLogger("memory_bank_mcp.project_manager")


class ProjectManager:
    """
    Project Management for Memory Bank MCP v2
    
    Handles project detection, initialization, and migration workflows.
    Provides smart project status analysis and setup recommendations.
    """
    
    @staticmethod
    def detect_project_status(project_path: Path) -> Dict[str, Any]:
        """
        Detect project status and provide setup recommendations
        
        Returns:
        - project_status: 'new_project', 'needs_migration', 'needs_setup', 'ready'
        - memory_bank_exists: bool
        - context_db_exists: bool
        - migration_files: List of .md files found
        - recommendations: List of suggested actions
        """
        
        project_path = project_path.resolve()
        memory_bank_path = project_path / "memory-bank"
        context_db_path = memory_bank_path / "context.db"
        
        status = {
            'project_path': str(project_path),
            'project_name': project_path.name,
            'memory_bank_path': str(memory_bank_path),
            'memory_bank_exists': memory_bank_path.exists(),
            'context_db_exists': context_db_path.exists(),
            'migration_files': [],
            'project_status': 'unknown',
            'recommendations': [],
            'can_initialize': True,
            'setup_required': True
        }
        
        # Check for existing memory-bank files
        if memory_bank_path.exists():
            md_files = list(memory_bank_path.glob("*.md"))
            status['migration_files'] = [str(f.relative_to(memory_bank_path)) for f in md_files]
            
            if context_db_path.exists():
                # Full setup - check if database is populated
                status['project_status'] = 'ready'
                status['setup_required'] = False
                status['recommendations'] = [
                    "Project is ready to use",
                    "Use get_memory_bank_status() to see database contents",
                    "Use generate_enhanced_session_starter() to begin working"
                ]
            elif md_files:
                # Has .md files but no database - migration available
                status['project_status'] = 'needs_migration'
                status['recommendations'] = [
                    f"Found {len(md_files)} memory-bank files ready for migration",
                    "Use get_migration_recommendations() to analyze files",
                    "Use migrate_existing_files() to convert to database",
                    "Or use start_new_project() to start fresh"
                ]
            else:
                # Empty memory-bank directory
                status['project_status'] = 'needs_setup'
                status['recommendations'] = [
                    "Empty memory-bank directory found",
                    "Use start_new_project() to initialize database",
                    "Or manually create initial documentation"
                ]
        else:
            # No memory-bank directory
            status['project_status'] = 'new_project'
            status['recommendations'] = [
                "New project detected - no memory-bank directory",
                "Use start_new_project() to create memory-bank structure",
                "Database will be initialized automatically"
            ]
        
        return status
    
    @staticmethod
    async def start_new_project(project_path: Path, 
                               project_name: str = "",
                               template: str = "standard") -> Dict[str, Any]:
        """
        Initialize a new project with memory-bank structure and database
        
        Args:
            project_path: Path to the project directory
            project_name: Optional custom project name
            template: Project template to use ('standard', 'django', 'react', etc.)
        
        Returns:
            Success status and project information
        """
        
        project_path = project_path.resolve()
        memory_bank_path = project_path / "memory-bank"
        
        try:
            # Create memory-bank directory
            memory_bank_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize database
            database = MemoryBankDatabase(project_path)
            success = await database.initialize()
            
            if not success:
                return {
                    'success': False,
                    'error': 'Failed to initialize database',
                    'project_path': str(project_path)
                }
            
            # Get project info
            project_info = await database.get_project_info()
            
            # Create initial project context based on template
            await ProjectManager._create_initial_context(database, project_name or project_path.name, template)
            
            # Create template files if requested
            if template != "minimal":
                await ProjectManager._create_template_files(memory_bank_path, project_name or project_path.name, template)
            
            await database.close()
            
            result = {
                'success': True,
                'project_path': str(project_path),
                'project_name': project_info['name'],
                'project_uuid': project_info['uuid'],
                'memory_bank_path': str(memory_bank_path),
                'template_used': template,
                'created_at': project_info['created_at'],
                'message': f"Successfully initialized memory-bank for {project_info['name']}"
            }
            
            logger.info(f"New project initialized: {project_info['name']} (UUID: {project_info['uuid']})")
            return result
            
        except Exception as e:
            logger.error(f"Failed to initialize project: {e}")
            return {
                'success': False,
                'error': str(e),
                'project_path': str(project_path)
            }
    
    @staticmethod
    async def _create_initial_context(database: MemoryBankDatabase, project_name: str, template: str):
        """Create initial project context entries"""
        
        # Create welcome discussion
        welcome_content = f"""# Welcome to {project_name}

This project is now managed by Memory Bank MCP v2. All discussions, code iterations, and artifacts will be automatically saved to the context.db database.

## Key Features:
- **Automatic context saving** after every exchange
- **Session persistence** across chat restarts
- **Cross-project intelligence** with UUID-based referencing
- **Minimal context loading** for quick session starts

## Getting Started:
1. Use `get_memory_bank_status()` to see project status
2. Use `generate_enhanced_session_starter()` to begin development
3. All your work will be automatically saved and retrievable
"""
        
        await database.save_discussion(
            summary="Memory Bank MCP v2 Project Initialization",
            content=welcome_content,
            implemented=True,
            tags=["initialization", "welcome", "setup"]
        )
        
        # Update project context
        import aiosqlite
        async with aiosqlite.connect(database.db_path) as db:
            await db.execute("""
                UPDATE project_context 
                SET overview = ?, current_focus = ?, updated_at = CURRENT_TIMESTAMP
                WHERE project_uuid = ?
            """, (
                f"# {project_name}\n\nA {template} project managed by Memory Bank MCP v2.\n\nThis project provides persistent AI collaboration memory with automatic context saving and session continuity.",
                "Project setup complete - ready for development",
                database.project_uuid
            ))
            await db.commit()
    
    @staticmethod
    async def _create_template_files(memory_bank_path: Path, project_name: str, template: str):
        """Create template documentation files"""
        
        # Create basic README for reference
        readme_content = f"""# {project_name} Memory Bank

This directory contains the Memory Bank MCP v2 database and optional reference files.

## Database
- `context.db` - Primary storage for all project memory (discussions, code, artifacts)

## Usage
All interactions through Claude Desktop will automatically save to the database.
Use the Memory Bank MCP tools to query and manage your project context.

## Template: {template}
Project initialized with {template} template on {datetime.now().strftime('%Y-%m-%d %H:%M')}.
"""
        
        readme_path = memory_bank_path / "README.md"
        readme_path.write_text(readme_content)
        
        # Create template-specific files
        if template == "django":
            django_notes = """# Django Development Notes

## Database Considerations
- Models and migrations tracking
- Performance optimization patterns
- Security best practices

## Common Patterns
- ViewSets and serializers
- Custom managers and querysets
- Signal handlers

This file can be used for manual notes, but all AI interactions are saved automatically to context.db.
"""
            (memory_bank_path / "django_notes.md").write_text(django_notes)
        
        elif template == "react":
            react_notes = """# React Development Notes

## Component Patterns
- Component composition strategies
- State management approaches
- Performance optimization

## Development Workflow
- Testing strategies
- Build and deployment patterns
- Code organization

This file can be used for manual notes, but all AI interactions are saved automatically to context.db.
"""
            (memory_bank_path / "react_notes.md").write_text(react_notes)
    
    @staticmethod
    def list_available_projects(base_paths: Optional[List[Path]] = None) -> List[Dict[str, Any]]:
        """
        List all available projects with memory-bank directories
        
        Args:
            base_paths: Optional list of base paths to search. Defaults to ~/Documents/GitHub/
        
        Returns:
            List of project information dictionaries
        """
        
        if base_paths is None:
            # Default search paths
            base_paths = [
                Path.home() / "Documents" / "GitHub",
                Path.home() / "Projects",
                Path.cwd().parent  # Parent of current directory
            ]
        
        projects = []
        
        for base_path in base_paths:
            if not base_path.exists():
                continue
                
            try:
                # Look for directories with memory-bank subdirectories
                for project_dir in base_path.iterdir():
                    if project_dir.is_dir() and not project_dir.name.startswith('.'):
                        memory_bank_path = project_dir / "memory-bank"
                        if memory_bank_path.exists():
                            status = ProjectManager.detect_project_status(project_dir)
                            projects.append({
                                'project_name': project_dir.name,
                                'project_path': str(project_dir),
                                'memory_bank_path': str(memory_bank_path),
                                'status': status['project_status'],
                                'context_db_exists': status['context_db_exists'],
                                'migration_files_count': len(status['migration_files']),
                                'base_path': str(base_path)
                            })
            except PermissionError:
                logger.warning(f"Permission denied accessing: {base_path}")
                continue
        
        # Sort by project name
        projects.sort(key=lambda x: x['project_name'].lower())
        
        logger.info(f"Found {len(projects)} projects with memory-bank directories")
        return projects
    
    @staticmethod
    def get_migration_recommendations(project_path: Path) -> Dict[str, Any]:
        """
        Analyze existing memory-bank files and provide migration recommendations
        
        Returns detailed analysis of what would be migrated and how
        """
        
        project_path = project_path.resolve()
        memory_bank_path = project_path / "memory-bank"
        
        if not memory_bank_path.exists():
            return {
                'can_migrate': False,
                'error': 'No memory-bank directory found',
                'project_path': str(project_path)
            }
        
        md_files = list(memory_bank_path.glob("*.md"))
        
        if not md_files:
            return {
                'can_migrate': False,
                'error': 'No .md files found in memory-bank directory',
                'project_path': str(project_path),
                'memory_bank_path': str(memory_bank_path)
            }
        
        # Analyze each file
        file_analysis = []
        total_content_length = 0
        
        for md_file in md_files:
            try:
                content = md_file.read_text(encoding='utf-8')
                total_content_length += len(content)
                
                # Estimate what would be extracted
                lines = content.split('\n')
                estimated_discussions = content.count('## ') + content.count('# ')
                estimated_code_blocks = content.count('```')
                
                file_analysis.append({
                    'filename': md_file.name,
                    'size_bytes': md_file.stat().st_size,
                    'content_length': len(content),
                    'line_count': len(lines),
                    'estimated_discussions': estimated_discussions,
                    'estimated_code_blocks': estimated_code_blocks,
                    'last_modified': md_file.stat().st_mtime
                })
                
            except Exception as e:
                file_analysis.append({
                    'filename': md_file.name,
                    'error': str(e),
                    'size_bytes': 0,
                    'can_read': False
                })
        
        recommendations = {
            'can_migrate': True,
            'project_path': str(project_path),
            'memory_bank_path': str(memory_bank_path),
            'files_found': len(md_files),
            'total_content_length': total_content_length,
            'file_analysis': file_analysis,
            'estimated_discussions': sum(f.get('estimated_discussions', 0) for f in file_analysis),
            'estimated_code_blocks': sum(f.get('estimated_code_blocks', 0) for f in file_analysis),
            'recommendations': [
                f"Found {len(md_files)} markdown files ready for migration",
                f"Estimated {sum(f.get('estimated_discussions', 0) for f in file_analysis)} discussions/sections",
                f"Estimated {sum(f.get('estimated_code_blocks', 0) for f in file_analysis)} code blocks",
                "Original files will be preserved during migration",
                "Use migrate_existing_files() to perform the migration"
            ]
        }
        
        return recommendations
