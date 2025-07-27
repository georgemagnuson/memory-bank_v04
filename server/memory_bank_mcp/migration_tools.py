#!/usr/bin/env python3
"""
Memory Bank v04 Enhanced - Migration Tools Module
Filename: migration_tools.py
Generated: 2025-07-27.1934
Purpose: Legacy project migration and conversion tools for Memory Bank v04

Migration Tools Implementation:
- Migrate existing .md files from projects to Memory Bank database format
- Analyze potential migration candidates with readiness assessment
- Migrate specific projects by name with comprehensive FTS import analysis
- Dry run support for safe migration planning and analysis
- Integration with existing FTS and content management systems

v1.4.0 Features Preserved:
- Content signature-based duplicate detection
- Enhanced metadata extraction and preservation
- Smart file filtering and error recovery
- Comprehensive progress reporting and statistics
"""

import logging
import sqlite3
import hashlib
import json
import os
import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Set
from datetime import datetime
import shutil
import re

logger = logging.getLogger(__name__)

class MigrationTools:
    """Legacy project migration and conversion tools for Memory Bank v04"""
    
    def __init__(self, context_manager):
        """Initialize MigrationTools with context manager dependency
        
        Args:
            context_manager: Active ContextManager instance with database connection
        """
        self.context_manager = context_manager
        self.logger = logger
        
        # Common project locations to search
        self.search_locations = [
            Path.home() / "Documents" / "GitHub",
            Path.home() / "Documents" / "Projects", 
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path("/Users") / os.getenv("USER", "user") / "Documents" / "GitHub",
            Path("/Users") / os.getenv("USER", "user") / "Projects",
            Path.cwd().parent,  # Parent of current directory
            Path.cwd()  # Current directory
        ]
        
        # File patterns that indicate a Memory Bank or similar project
        self.project_indicators = [
            "memory-bank", "memory_bank", "context.db", "discussions.md",
            "artifacts.md", "plans.md", "project_overview.md"
        ]
        
        # Markdown file patterns for migration
        self.markdown_patterns = ['*.md', '*.markdown', '*.txt']
        
        # Directories to exclude from migration
        self.exclude_patterns = {
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'venv', 'env', '.env', 'dist', 'build', '.next',
            'coverage', '.coverage', '.nyc_output', 'logs', '.DS_Store'
        }
        
        # Content categories for imported files
        self.content_categories = {
            'discussions': ['discussion', 'chat', 'conversation', 'exchange'],
            'artifacts': ['artifact', 'code', 'implementation', 'solution'],
            'plans': ['plan', 'roadmap', 'strategy', 'timeline'],
            'documentation': ['readme', 'doc', 'guide', 'manual', 'help'],
            'analysis': ['analysis', 'research', 'study', 'review'],
            'specifications': ['spec', 'requirement', 'design', 'architecture']
        }
    
    async def analyze_migration_candidates(self) -> str:
        """Analyze potential projects for migration from .md to Memory Bank MCP v2
        
        Searches common locations for projects containing markdown files that could
        be migrated to Memory Bank database format.
        
        Returns:
            Comprehensive analysis report of migration candidates
        """
        try:
            if not self.context_manager:
                return "❌ **ANALYSIS FAILED**\n\nNo context manager available."
            
            analysis_stats = {
                'locations_searched': 0,
                'projects_found': 0,
                'total_md_files': 0,
                'total_size': 0,
                'candidates': [],
                'search_errors': []
            }
            
            self.logger.info("Starting migration candidate analysis...")
            
            # Search each location
            for location in self.search_locations:
                if not location.exists():
                    continue
                    
                analysis_stats['locations_searched'] += 1
                
                try:
                    # Find potential project directories
                    for item in location.iterdir():
                        if not item.is_dir():
                            continue
                        
                        # Skip hidden directories and common excludes
                        if item.name.startswith('.') or item.name in self.exclude_patterns:
                            continue
                        
                        # Analyze directory for migration potential
                        candidate_info = await self._analyze_project_directory(item)
                        
                        if candidate_info and candidate_info['md_files'] > 0:
                            analysis_stats['candidates'].append(candidate_info)
                            analysis_stats['projects_found'] += 1
                            analysis_stats['total_md_files'] += candidate_info['md_files']
                            analysis_stats['total_size'] += candidate_info['total_size']
                
                except (PermissionError, OSError) as e:
                    analysis_stats['search_errors'].append(f"Error searching {location}: {str(e)}")
                    self.logger.warning(f"Could not search {location}: {e}")
            
            # Sort candidates by potential (size and file count)
            analysis_stats['candidates'].sort(
                key=lambda x: (x['md_files'], x['total_size']), 
                reverse=True
            )
            
            return self._format_migration_analysis(analysis_stats)
            
        except Exception as e:
            self.logger.error(f"Migration analysis failed: {e}")
            return f"❌ **ANALYSIS FAILED**\n\nError: {str(e)}"
    
    async def _analyze_project_directory(self, directory: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single directory for migration potential"""
        try:
            # Count markdown files and analyze structure
            md_files = []
            total_size = 0
            has_indicators = False
            
            # Check for project indicators
            for indicator in self.project_indicators:
                if any(file.name.lower().find(indicator.lower()) >= 0 for file in directory.rglob("*")):
                    has_indicators = True
                    break
            
            # Find all markdown files
            for pattern in self.markdown_patterns:
                for file_path in directory.rglob(pattern):
                    # Skip files in excluded directories
                    if any(exclude in str(file_path).lower() for exclude in self.exclude_patterns):
                        continue
                    
                    try:
                        file_size = file_path.stat().st_size
                        md_files.append({
                            'path': str(file_path),
                            'name': file_path.name,
                            'size': file_size,
                            'modified': datetime.fromtimestamp(file_path.stat().st_mtime)
                        })
                        total_size += file_size
                    except (OSError, PermissionError):
                        continue
            
            if len(md_files) == 0:
                return None
            
            # Categorize files
            categories = self._categorize_markdown_files(md_files)
            
            # Calculate migration readiness score
            readiness_score = self._calculate_readiness_score(
                len(md_files), total_size, has_indicators, categories
            )
            
            return {
                'name': directory.name,
                'path': str(directory),
                'md_files': len(md_files),
                'total_size': total_size,
                'has_indicators': has_indicators,
                'categories': categories,
                'readiness_score': readiness_score,
                'recent_activity': max((f['modified'] for f in md_files), default=datetime.min),
                'files_sample': md_files[:5]  # First 5 files as sample
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing directory {directory}: {e}")
            return None
    
    def _categorize_markdown_files(self, md_files: List[Dict]) -> Dict[str, int]:
        """Categorize markdown files by content type"""
        categories = {category: 0 for category in self.content_categories.keys()}
        categories['uncategorized'] = 0
        
        for file_info in md_files:
            file_name_lower = file_info['name'].lower()
            categorized = False
            
            for category, keywords in self.content_categories.items():
                if any(keyword in file_name_lower for keyword in keywords):
                    categories[category] += 1
                    categorized = True
                    break
            
            if not categorized:
                categories['uncategorized'] += 1
        
        # Remove empty categories
        return {k: v for k, v in categories.items() if v > 0}
    
    def _calculate_readiness_score(self, file_count: int, total_size: int, 
                                 has_indicators: bool, categories: Dict[str, int]) -> int:
        """Calculate migration readiness score (0-100)"""
        score = 0
        
        # File count score (0-30 points)
        if file_count >= 20:
            score += 30
        elif file_count >= 10:
            score += 20
        elif file_count >= 5:
            score += 10
        
        # Size score (0-20 points)
        size_mb = total_size / (1024 * 1024)
        if size_mb >= 5:
            score += 20
        elif size_mb >= 1:
            score += 15
        elif size_mb >= 0.5:
            score += 10
        
        # Project indicators (0-20 points)
        if has_indicators:
            score += 20
        
        # Category diversity (0-20 points)
        category_count = len(categories)
        if category_count >= 4:
            score += 20
        elif category_count >= 3:
            score += 15
        elif category_count >= 2:
            score += 10
        
        # Structure bonus (0-10 points)
        if 'discussions' in categories and 'artifacts' in categories:
            score += 10
        elif 'discussions' in categories or 'documentation' in categories:
            score += 5
        
        return min(score, 100)
    
    def _format_migration_analysis(self, stats: Dict) -> str:
        """Format migration candidate analysis results"""
        if stats['projects_found'] == 0:
            return f"""🔍 **MIGRATION CANDIDATE ANALYSIS**

**Locations Searched:** {stats['locations_searched']}
**Projects Found:** 0

❌ No migration candidates found.

**Search Locations:**
{chr(10).join(f'- {loc}' for loc in self.search_locations if loc.exists())}

**Recommendations:**
- Check if projects use different markdown patterns
- Look for projects in other locations
- Consider manual project specification with `migrate_specific_project()`
"""
        
        total_size_mb = stats['total_size'] / (1024 * 1024)
        
        output = [f"""🔍 **MIGRATION CANDIDATE ANALYSIS**

**Locations Searched:** {stats['locations_searched']}
**Projects Found:** {stats['projects_found']}
**Total Markdown Files:** {stats['total_md_files']}
**Total Size:** {total_size_mb:.2f} MB

## 📋 Migration Candidates (Top 10)

"""]
        
        # Show top candidates
        for i, candidate in enumerate(stats['candidates'][:10], 1):
            size_mb = candidate['total_size'] / (1024 * 1024)
            readiness_emoji = "🟢" if candidate['readiness_score'] >= 70 else "🟡" if candidate['readiness_score'] >= 40 else "🔴"
            
            output.append(f"**{i}. {candidate['name']}** {readiness_emoji}")
            output.append(f"   📁 Path: `{candidate['path']}`")
            output.append(f"   📄 Files: {candidate['md_files']} markdown files")
            output.append(f"   📦 Size: {size_mb:.2f} MB")
            output.append(f"   📊 Readiness: {candidate['readiness_score']}/100")
            output.append(f"   🏷️ Categories: {', '.join(candidate['categories'].keys())}")
            output.append(f"   📅 Recent: {candidate['recent_activity'].strftime('%Y-%m-%d')}")
            
            if candidate['has_indicators']:
                output.append("   ✨ Contains Memory Bank indicators")
            
            output.append("")
        
        # Show readiness legend
        output.append("## 📊 Readiness Score Legend")
        output.append("- 🟢 **70-100**: Excellent candidate - Rich content, good structure")
        output.append("- 🟡 **40-69**: Good candidate - Moderate content, some structure") 
        output.append("- 🔴 **0-39**: Basic candidate - Limited content or structure")
        output.append("")
        
        # Migration recommendations
        output.append("## 🚀 Next Steps")
        if stats['candidates']:
            best_candidate = stats['candidates'][0]
            output.append(f"**Recommended:** Start with `{best_candidate['name']}` (Score: {best_candidate['readiness_score']})")
            output.append(f"```")
            output.append(f"migrate_specific_project(\"{best_candidate['name']}\")")
            output.append(f"# or")
            output.append(f"migrate_project_md_files(\"{best_candidate['path']}\")")
            output.append(f"```")
        
        # Show search errors if any
        if stats['search_errors']:
            output.append("## ⚠️ Search Issues")
            for error in stats['search_errors']:
                output.append(f"- {error}")
            output.append("")
        
        output.append("💡 **Tip:** Use `migrate_specific_project(project_name, dry_run=True)` for detailed analysis before migration.")
        
        return "\n".join(output)
        # Category breakdown
        if stats['categories']:
            output.append("## 📋 Content Categories\n")
            for category, count in sorted(stats['categories'].items()):
                percentage = (count / stats['files_found'] * 100) if stats['files_found'] > 0 else 0
                output.append(f"- **{category.title()}**: {count} files ({percentage:.1f}%)")
            output.append("")
        
        # Migration details
        if stats['migration_details'] and not stats['dry_run']:
            output.append("## 📝 Migration Details\n")
            for detail in stats['migration_details'][:10]:  # Show first 10
                output.append(f"- {detail}")
            if len(stats['migration_details']) > 10:
                output.append(f"- ... and {len(stats['migration_details']) - 10} more items")
            output.append("")
        
        # Errors
        if stats['errors']:
            output.append(f"## ❌ Issues ({len(stats['errors'])})\n")
            for error in stats['errors'][:5]:  # Show first 5 errors
                output.append(f"- {error}")
            if len(stats['errors']) > 5:
                output.append(f"- ... and {len(stats['errors']) - 5} more issues")
            output.append("")
        
        # Results summary
        if stats['dry_run']:
            output.append("ℹ️ **Dry run complete.** Use `migrate_project_md_files(project_path, dry_run=False)` to perform migration.")
        elif completed:
            if stats['files_migrated'] + stats['files_updated'] > 0:
                output.append("✅ **Migration successful!** All migrated content is now searchable via `search_all_content()`.")
            else:
                output.append("ℹ️ **No new content migrated.** All files were already up-to-date or skipped.")
        
        return "\n".join(output)
    
    async def migrate_specific_project(self, project_name: str, dry_run: bool = False, auto_import_md: bool = False) -> str:
        """Migrate a specific project by name with comprehensive FTS import analysis and optional auto-import
        
        Args:
            project_name: Name or partial name of project to find and migrate
            dry_run: If True, analyze without making changes (default: False)
            auto_import_md: If True, automatically imports all markdown files after migration (default: False)
        
        Returns:
            Comprehensive migration report with FTS analysis and recommendations
        """
        try:
            if not self.context_manager:
                return "❌ **MIGRATION FAILED**\n\nNo context manager available."
            
            # Find project by name
            project_candidates = []
            
            for location in self.search_locations:
                if not location.exists():
                    continue
                
                try:
                    for item in location.iterdir():
                        if not item.is_dir():
                            continue
                        
                        # Check if project name matches (case-insensitive partial match)
                        if project_name.lower() in item.name.lower():
                            # Verify it contains markdown files
                            has_md = any(item.rglob(pattern) for pattern in self.markdown_patterns)
                            if has_md:
                                project_candidates.append(item)
                
                except (PermissionError, OSError):
                    continue
            
            if not project_candidates:
                return f"""❌ **PROJECT NOT FOUND**

**Search Term:** "{project_name}"
**Locations Searched:** {len(self.search_locations)}

No projects found matching "{project_name}" with markdown files.

**Suggestions:**
- Check project name spelling
- Use `analyze_migration_candidates()` to see available projects
- Use `migrate_project_md_files("/full/path/to/project")` with full path
"""
            
            # If multiple candidates, choose the best match
            if len(project_candidates) > 1:
                # Sort by name similarity and modification time
                project_candidates.sort(key=lambda p: (
                    -len([c for c in project_name.lower() if c in p.name.lower()]),  # Name similarity
                    -p.stat().st_mtime  # Modification time
                ))
            
            selected_project = project_candidates[0]
            
            migration_stats = {
                'search_term': project_name,
                'candidates_found': len(project_candidates),
                'selected_project': str(selected_project),
                'project_name': selected_project.name,
                'auto_import_md': auto_import_md
            }
            
            # Perform detailed analysis first
            project_analysis = await self._analyze_project_directory(selected_project)
            
            if not project_analysis:
                return f"❌ **ANALYSIS FAILED**\n\nCould not analyze project: {selected_project}"
            
            # Show project selection and analysis
            output = [f"""🎯 **SPECIFIC PROJECT MIGRATION**

**Search Term:** "{project_name}"
**Candidates Found:** {len(project_candidates)}
**Selected Project:** {selected_project.name}
**Project Path:** {str(selected_project)}

## 📊 Project Analysis
- **Markdown Files:** {project_analysis['md_files']}
- **Total Size:** {project_analysis['total_size'] / (1024 * 1024):.2f} MB
- **Readiness Score:** {project_analysis['readiness_score']}/100
- **Categories:** {', '.join(project_analysis['categories'].keys())}
- **Memory Bank Indicators:** {'Yes' if project_analysis['has_indicators'] else 'No'}

"""]
            
            if len(project_candidates) > 1:
                output.append("## 🔍 Other Candidates Found\n")
                for i, candidate in enumerate(project_candidates[1:6], 2):  # Show next 5
                    output.append(f"{i}. {candidate.name} (`{candidate}`)")
                if len(project_candidates) > 6:
                    output.append(f"... and {len(project_candidates) - 6} more")
                output.append("")
            
            # Perform migration
            migration_result = await self.migrate_project_md_files(str(selected_project), dry_run)
            
            # If not dry run and auto_import_md is True, also import all markdown files
            if not dry_run and auto_import_md and self.context_manager.current_db_path:
                try:
                    from .content_tools import ContentTools
                    content_tools = ContentTools(self.context_manager)
                    
                    output.append("## 📥 Automatic Markdown Import\n")
                    import_result = await content_tools.import_project_documentation(include_external=True)
                    output.append(import_result)
                    output.append("")
                    
                except ImportError:
                    output.append("## ⚠️ Auto-Import Unavailable\n")
                    output.append("ContentTools not available for automatic markdown import.")
                    output.append("Use `import_project_documentation()` manually after migration.")
                    output.append("")
            
            # Add migration results
            output.append("## 📁 Migration Results\n")
            output.append(migration_result)
            
            # FTS recommendations
            if not dry_run:
                output.append("\n## 🔍 Full-Text Search Recommendations\n")
                if auto_import_md:
                    output.append("✅ **Auto-import completed** - All content is now searchable")
                else:
                    output.append("💡 **Next Steps for Full Search Integration:**")
                    output.append("```")
                    output.append("import_project_documentation()  # Import all project docs")
                    output.append("sync_fts_tables()              # Update search indexes")
                    output.append("search_all_content(\"your_query\")  # Search all content")
                    output.append("```")
                
                output.append("\n**Search Examples:**")
                output.append(f"- `search_all_content(\"{selected_project.name}\")`")
                output.append("- `search_all_content(\"implementation\", content_types=\"artifacts\")`")
                output.append("- `generate_markdown_import_report()` - View import statistics")
            
            return "\n".join(output)
            
        except Exception as e:
            self.logger.error(f"Specific project migration failed: {e}")
            return f"❌ **MIGRATION FAILED**\n\nError: {str(e)}"
