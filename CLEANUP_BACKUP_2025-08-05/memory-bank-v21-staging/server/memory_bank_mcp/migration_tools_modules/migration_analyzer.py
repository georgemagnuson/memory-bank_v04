#!/usr/bin/env python3
"""
server/memory_bank_mcp/migration_tools_modules/migration_analyzer.py
Generated: 2025-07-30.1927
Purpose: Project analysis and migration readiness assessment for v2.0 architecture

Key v2.0 Features:
- Uses documents table document_type categories instead of deprecated table names
- Enhanced project_uuid support for cross-project migration analysis
- v2.0 content categorization aligned with unified documents structure
- Clean v2.0-only implementation (no backward compatibility)
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple

logger = logging.getLogger(__name__)

class MigrationAnalyzer:
    """Project analysis and migration readiness assessment with v2.0 architecture"""
    
    def __init__(self, context_manager):
        """Initialize with context manager for v2.0 database access"""
        self.context_manager = context_manager
        
        # v2.0 project indicators - updated for documents table architecture
        self.project_indicators = [
            "memory-bank", "memory_bank", "context.db", "discussions.md", 
            "artifacts.md", "plans.md", "project_overview.md", "documents.md"
        ]
        
        # Markdown file patterns for migration
        self.markdown_patterns = ['*.md', '*.markdown', '*.txt']
        
        # Directories to exclude from migration
        self.exclude_patterns = {
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'venv', 'env', '.env', 'dist', 'build', '.next',
            'coverage', '.coverage', '.nyc_output', 'logs', '.DS_Store'
        }
        
        # v2.0 Content categories - using document_type values for documents table
        self.content_categories = {
            'discussion': ['discussion', 'chat', 'conversation', 'exchange', 'meeting'],
            'artifact': ['artifact', 'code', 'implementation', 'solution', 'output'],
            'plan': ['plan', 'roadmap', 'strategy', 'timeline', 'milestone'],
            'document': ['readme', 'doc', 'guide', 'manual', 'help', 'documentation'],
            'note': ['note', 'observation', 'thought', 'idea', 'memo'],
            'code': ['code', 'script', 'program', 'function', 'class'],
            'analysis': ['analysis', 'research', 'study', 'review', 'evaluation'],
            'decision': ['decision', 'choice', 'resolution', 'conclusion']
        }
    
    async def analyze_migration_candidates(self) -> str:
        """
        Analyze potential projects for migration to Memory Bank v2.0 architecture
        
        Searches common locations for projects containing markdown files that could
        be migrated to the unified documents table with appropriate document_type values.
        
        Returns:
            Formatted analysis report with v2.0 migration recommendations
        """
        try:
            # Common project locations to search
            search_locations = [
                os.path.expanduser("~/Documents"),
                os.path.expanduser("~/Projects"), 
                os.path.expanduser("~/Development"),
                os.path.expanduser("~/GitHub"),
                os.path.expanduser("~/Desktop"),
                "/Users/georgemagnuson/Documents/GitHub"  # Current user's GitHub
            ]
            
            # Filter to existing locations
            existing_locations = [loc for loc in search_locations if os.path.exists(loc)]
            
            stats = {
                'locations_searched': len(existing_locations),
                'projects_found': 0,
                'candidates': [],
                'total_md_files': 0,
                'total_size_mb': 0
            }
            
            # Analyze each location
            for location in existing_locations:
                location_candidates = await self._analyze_location(location)
                stats['candidates'].extend(location_candidates)
                stats['projects_found'] += len(location_candidates)
            
            # Calculate totals
            for candidate in stats['candidates']:
                stats['total_md_files'] += candidate.get('md_file_count', 0)
                stats['total_size_mb'] += candidate.get('total_size_mb', 0)
            
            # Format and return analysis
            return self._format_migration_analysis(stats)
            
        except Exception as e:
            logger.error(f"Error analyzing migration candidates: {e}")
            return f"❌ Error during migration analysis: {str(e)}"
    
    async def _analyze_location(self, location: str) -> List[Dict[str, Any]]:
        """Analyze a single location for migration candidates"""
        candidates = []
        
        try:
            location_path = Path(location)
            
            # Search for project directories (limit depth to avoid excessive scanning)
            for root, dirs, files in os.walk(location_path):
                # Limit search depth
                if root.count(os.sep) - str(location_path).count(os.sep) > 3:
                    continue
                
                # Skip excluded directories
                dirs[:] = [d for d in dirs if d not in self.exclude_patterns]
                
                # Analyze if this directory looks like a project
                project_analysis = await self._analyze_project_directory(root, files)
                if project_analysis['is_candidate']:
                    candidates.append(project_analysis)
                
                # Limit results to prevent overwhelming output
                if len(candidates) >= 20:
                    break
                    
        except Exception as e:
            logger.warning(f"Error analyzing location {location}: {e}")
        
        return candidates
    
    async def _analyze_project_directory(self, directory: str, files: List[str]) -> Dict[str, Any]:
        """Analyze a single directory for migration potential with v2.0 categorization"""
        try:
            dir_path = Path(directory)
            
            # Check for project indicators
            has_indicators = any(
                indicator in file.lower() or indicator in dir_path.name.lower()
                for indicator in self.project_indicators
                for file in files
            )
            
            # Find markdown files
            md_files = []
            total_size = 0
            
            for file in files:
                if any(Path(file).match(pattern) for pattern in self.markdown_patterns):
                    file_path = dir_path / file
                    try:
                        if file_path.exists():
                            size = file_path.stat().st_size
                            md_files.append({
                                'name': file,
                                'size': size,
                                'path': str(file_path)
                            })
                            total_size += size
                    except:
                        continue
            
            # Categorize files using v2.0 document types
            categories = self._categorize_markdown_files(md_files)
            
            # Calculate readiness score
            readiness_score = self._calculate_readiness_score(
                len(md_files), total_size, has_indicators, categories
            )
            
            # Determine if this is a migration candidate
            is_candidate = (
                len(md_files) >= 2 and  # At least 2 markdown files
                (readiness_score >= 30 or has_indicators)  # Good score or clear indicators
            )
            
            return {
                'is_candidate': is_candidate,
                'directory': directory,
                'project_name': dir_path.name,
                'md_file_count': len(md_files),
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'has_indicators': has_indicators,
                'categories': categories,
                'readiness_score': readiness_score,
                'md_files': md_files[:10]  # Limit to first 10 for display
            }
            
        except Exception as e:
            logger.error(f"Error analyzing directory {directory}: {e}")
            return {
                'is_candidate': False,
                'directory': directory,
                'project_name': Path(directory).name,
                'error': str(e)
            }
    
    def _categorize_markdown_files(self, md_files: List[Dict]) -> Dict[str, int]:
        """Categorize markdown files by v2.0 document_type values"""
        categories = {}
        
        for file_info in md_files:
            filename = file_info['name'].lower()
            
            # Check against v2.0 document types
            for doc_type, keywords in self.content_categories.items():
                if any(keyword in filename for keyword in keywords):
                    categories[doc_type] = categories.get(doc_type, 0) + 1
                    break
            else:
                # Default to 'document' type for uncategorized files
                categories['document'] = categories.get('document', 0) + 1
        
        return categories
    
    def _calculate_readiness_score(self, file_count: int, total_size: int, 
                                 has_indicators: bool, categories: Dict[str, int]) -> int:
        """Calculate migration readiness score for v2.0 architecture"""
        score = 0
        
        # Base score from file count (v2.0 considers all as documents)
        score += min(file_count * 5, 30)  # Max 30 points for file count
        
        # Size considerations
        size_mb = total_size / (1024 * 1024)
        if 0.1 <= size_mb <= 50:  # Sweet spot for migration
            score += 15
        elif size_mb > 50:
            score += 5  # Large projects need more consideration
        
        # Project indicators boost
        if has_indicators:
            score += 25
        
        # v2.0 document type diversity (unified documents table benefits)
        unique_types = len(categories)
        if unique_types >= 3:
            score += 15
        elif unique_types >= 2:
            score += 10
        
        # Bonus for specific v2.0 document types
        if 'discussion' in categories:
            score += 10  # High value content type
        if 'plan' in categories:
            score += 8   # Strategic content
        if 'decision' in categories:
            score += 12  # Critical architectural content
        
        return min(score, 100)
    
    def _format_migration_analysis(self, stats: Dict) -> str:
        """Format migration candidate analysis results for v2.0"""
        if stats['projects_found'] == 0:
            return f"""🔍 **MIGRATION CANDIDATE ANALYSIS** (v2.0)

**Locations Searched:** {stats['locations_searched']}
**Projects Found:** 0

❌ No migration candidates found.

**💡 Migration Tips for v2.0:**
• Look for projects with markdown files that could become document types
• v2.0 uses unified documents table with document_type filtering
• All content types (discussion, plan, artifact, etc.) stored in documents table
• Enhanced project_uuid support for cross-project functionality"""
        
        # Sort candidates by readiness score
        sorted_candidates = sorted(
            stats['candidates'], 
            key=lambda x: x.get('readiness_score', 0), 
            reverse=True
        )
        
        analysis = f"""🔍 **MIGRATION CANDIDATE ANALYSIS** (v2.0 Architecture)

**📊 Summary:**
• Locations Searched: {stats['locations_searched']}
• Projects Found: {stats['projects_found']}
• Total Markdown Files: {stats['total_md_files']}
• Total Size: {stats['total_size_mb']:.1f} MB

**🎯 Top Migration Candidates:**"""
        
        # Show top 10 candidates
        for i, candidate in enumerate(sorted_candidates[:10], 1):
            score = candidate.get('readiness_score', 0)
            file_count = candidate.get('md_file_count', 0)
            size_mb = candidate.get('total_size_mb', 0)
            categories = candidate.get('categories', {})
            
            # Create category summary using v2.0 document types
            cat_summary = ', '.join([f"{k}({v})" for k, v in list(categories.items())[:3]])
            if len(categories) > 3:
                cat_summary += f" +{len(categories)-3} more"
            
            analysis += f"""

**{i}. {candidate.get('project_name', 'Unknown')}**
   📂 Path: {candidate.get('directory', '')}
   📊 Score: {score}/100 {'🔥' if score >= 70 else '⭐' if score >= 50 else '💡'}
   📄 Files: {file_count} ({size_mb:.1f} MB)
   🏷️ Document Types: {cat_summary or 'mixed content'}"""
        
        analysis += f"""

**🚀 v2.0 Migration Benefits:**
• Unified documents table with flexible document_type filtering
• Enhanced project_uuid support for cross-project organization
• Advanced full-text search across all content types
• Modular architecture for better maintainability
• Future-proof design as deprecated tables will be removed

**💡 Next Steps:**
• Use `migrate_specific_project("project_name")` for targeted migration
• All content will be stored in documents table with appropriate document_type
• Enhanced metadata and project_uuid support for v2.0 architecture"""
        
        return analysis
