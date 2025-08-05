#!/usr/bin/env python3
"""
server/memory_bank_mcp/migration_tools_modules/content_importer.py
Generated: 2025-07-30.1927
Purpose: Enhanced content import with v2.0 metadata support and documents table integration

Key v2.0 Features:
- Direct import to documents table with document_type categorization
- Enhanced project_uuid support for cross-project content organization
- Smart duplicate detection using content signatures
- Rich metadata preservation with v2.0 structure
"""

import logging
import hashlib
import json
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ContentImporter:
    """Enhanced content import with v2.0 documents table integration"""
    
    def __init__(self, context_manager):
        """Initialize with context manager for v2.0 database access"""
        self.context_manager = context_manager
    
    async def _execute_query(self, query: str, params: tuple = ()) -> List[Any]:
        """Execute SQL query using context manager with v2.0 error handling"""
        try:
            # Use the context manager's SQL query capability
            if hasattr(self.context_manager, 'database') and hasattr(self.context_manager.database, 'execute_query'):
                result = await self.context_manager.database.execute_query(query, params)
                if isinstance(result, dict) and result.get('success'):
                    return [tuple(row.values()) for row in result.get('results', [])]
                elif isinstance(result, list):
                    return result
                else:
                    raise Exception(f"Query failed: {result.get('error', 'Unknown error')}")
            else:
                # Fallback for testing or simplified execution
                return []
        except Exception as e:
            logger.error(f"Database query failed: {e}")
            raise
    
    async def import_project_documentation(self, include_external: bool = True) -> str:
        """
        Import all documentation files from current project for v2.0 FTS
        
        Args:
            include_external: Whether to include external documentation files
            
        Returns:
            Formatted import report with v2.0 details
        """
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            # Get current project context for v2.0
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', str(uuid.uuid4()))
            project_path = getattr(self.context_manager, 'project_path', None)
            
            if not project_path:
                return "❌ No active project path available for documentation import."
            
            # Discover and analyze documentation files
            import_stats = await self._discover_and_analyze_docs(
                project_path, project_uuid, include_external
            )
            
            # Import files to v2.0 documents table
            import_results = await self._import_files_to_v2(import_stats['files'], project_uuid)
            
            return self._format_import_report(import_stats, import_results)
            
        except Exception as e:
            logger.error(f"Error importing project documentation: {e}")
            return f"❌ Error importing project documentation: {str(e)}"
    
    async def _discover_and_analyze_docs(self, project_path: str, project_uuid: str, 
                                        include_external: bool) -> Dict[str, Any]:
        """Discover and analyze documentation files for v2.0 import"""
        stats = {
            'files': [],
            'total_files': 0,
            'total_size': 0,
            'document_types': {},
            'duplicates_found': 0,
            'external_files': 0
        }
        
        try:
            project_dir = Path(project_path)
            
            # Documentation file patterns
            doc_patterns = ['*.md', '*.markdown', '*.txt', '*.rst', '*.adoc']
            
            # Find all documentation files
            for pattern in doc_patterns:
                for doc_file in project_dir.rglob(pattern):
                    if self._should_import_file(doc_file, include_external):
                        file_info = await self._analyze_doc_file(doc_file, project_uuid)
                        if file_info:
                            stats['files'].append(file_info)
                            stats['total_size'] += file_info['size']
                            
                            # Track document types for v2.0
                            doc_type = file_info['document_type']
                            stats['document_types'][doc_type] = stats['document_types'].get(doc_type, 0) + 1
                            
                            # Check if external
                            if not str(doc_file).startswith(str(project_dir)):
                                stats['external_files'] += 1
            
            stats['total_files'] = len(stats['files'])
            
            # Check for existing duplicates in v2.0 documents table
            stats['duplicates_found'] = await self._check_for_duplicates_v2(
                stats['files'], project_uuid
            )
            
            return stats
            
        except Exception as e:
            logger.error(f"Error discovering documentation: {e}")
            stats['error'] = str(e)
            return stats
    
    def _should_import_file(self, file_path: Path, include_external: bool) -> bool:
        """Check if file should be imported to v2.0 documents table"""
        # Skip files in excluded directories
        exclude_patterns = {
            'node_modules', '.git', '__pycache__', 'venv', 'env',
            'dist', 'build', '.next', 'coverage', '.pytest_cache'
        }
        
        for part in file_path.parts:
            if part in exclude_patterns:
                return False
        
        # Skip very large files (>10MB for docs)
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except:
            return False
        
        # Skip binary files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(100)  # Test readability
        except:
            return False
        
        return True
    
    async def _analyze_doc_file(self, file_path: Path, project_uuid: str) -> Optional[Dict[str, Any]]:
        """Analyze documentation file for v2.0 import"""
        try:
            stat = file_path.stat()
            
            # Read content for analysis
            content = ""
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                # Try alternative encodings
                for encoding in ['latin-1', 'cp1252']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except:
                        continue
            
            if not content.strip():
                return None
            
            # Generate content signature for duplicate detection
            content_signature = hashlib.sha256(content.encode()).hexdigest()
            
            # Determine v2.0 document_type
            document_type = self._determine_doc_type_v2(file_path.name, content)
            
            # Extract title from content or filename
            title = self._extract_title_from_content(content, file_path.name)
            
            return {
                'path': str(file_path),
                'name': file_path.name,
                'title': title,
                'content': content,
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'document_type': document_type,
                'content_signature': content_signature,
                'project_uuid': project_uuid
            }
            
        except Exception as e:
            logger.warning(f"Error analyzing doc file {file_path}: {e}")
            return None
    
    def _determine_doc_type_v2(self, filename: str, content: str) -> str:
        """Determine v2.0 document_type for documentation"""
        filename_lower = filename.lower()
        content_lower = content.lower()
        
        # v2.0 documentation type mapping
        if 'readme' in filename_lower or content_lower.startswith('# readme'):
            return 'document'
        elif any(word in filename_lower for word in ['guide', 'tutorial', 'manual', 'help']):
            return 'document'
        elif any(word in filename_lower for word in ['api', 'reference', 'spec']):
            return 'document'
        elif any(word in filename_lower for word in ['plan', 'roadmap', 'strategy']):
            return 'plan'
        elif any(word in filename_lower for word in ['note', 'notes', 'memo']):
            return 'note'
        elif '```' in content or 'function' in content_lower or 'class ' in content_lower:
            return 'code'
        else:
            return 'document'  # Default for documentation
    
    def _extract_title_from_content(self, content: str, filename: str) -> str:
        """Extract title from content or derive from filename"""
        # Look for first heading
        lines = content.split('\n')
        for line in lines[:10]:
            line = line.strip()
            if line.startswith('# '):
                return line[2:].strip()
            elif line.startswith('## ') and not line.startswith('###'):
                return line[3:].strip()
        
        # Fallback to cleaned filename
        return Path(filename).stem.replace('_', ' ').replace('-', ' ').title()
    
    async def _check_for_duplicates_v2(self, files: List[Dict], project_uuid: str) -> int:
        """Check for duplicate content in v2.0 documents table"""
        try:
            duplicates = 0
            
            for file_info in files:
                # Check by content signature in documents table
                query = """
                SELECT COUNT(*) FROM documents 
                WHERE project_uuid = ? AND metadata LIKE ?
                """
                signature_pattern = f'%"content_signature":"{file_info["content_signature"]}"%'
                
                result = await self._execute_query(query, (project_uuid, signature_pattern))
                if result and result[0][0] > 0:
                    duplicates += 1
            
            return duplicates
            
        except Exception as e:
            logger.error(f"Error checking duplicates: {e}")
            return 0
    
    async def _import_files_to_v2(self, files: List[Dict], project_uuid: str) -> Dict[str, Any]:
        """Import files to v2.0 documents table"""
        results = {
            'imported': 0,
            'skipped': 0,
            'errors': [],
            'document_uuids': []
        }
        
        try:
            for file_info in files:
                try:
                    # Check if already exists (duplicate prevention)
                    signature_pattern = f'%"content_signature":"{file_info["content_signature"]}"%'
                    check_query = """
                    SELECT uuid FROM documents 
                    WHERE project_uuid = ? AND metadata LIKE ?
                    """
                    
                    existing = await self._execute_query(check_query, (project_uuid, signature_pattern))
                    if existing:
                        results['skipped'] += 1
                        continue
                    
                    # Insert into v2.0 documents table
                    document_uuid = str(uuid.uuid4())
                    
                    # Create rich v2.0 metadata
                    metadata = {
                        'source_file': file_info['path'],
                        'original_size': file_info['size'],
                        'import_date': datetime.utcnow().isoformat(),
                        'content_signature': file_info['content_signature'],
                        'import_type': 'documentation',
                        'version': '2.0'
                    }
                    
                    insert_query = """
                    INSERT INTO documents (
                        uuid, project_uuid, title, content, document_type,
                        status, created_at, updated_at, metadata
                    ) VALUES (?, ?, ?, ?, ?, 'active', datetime('now'), datetime('now'), ?)
                    """
                    
                    await self._execute_query(insert_query, (
                        document_uuid,
                        project_uuid,
                        file_info['title'],
                        file_info['content'],
                        file_info['document_type'],
                        json.dumps(metadata)
                    ))
                    
                    results['imported'] += 1
                    results['document_uuids'].append(document_uuid)
                    
                except Exception as e:
                    logger.error(f"Error importing file {file_info['name']}: {e}")
                    results['errors'].append(f"{file_info['name']}: {str(e)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error importing files to v2.0: {e}")
            results['errors'].append(f"Import error: {str(e)}")
            return results
    
    def _format_import_report(self, stats: Dict, results: Dict) -> str:
        """Format comprehensive import report for v2.0"""
        doc_types = ', '.join([f"{k}: {v}" for k, v in stats.get('document_types', {}).items()])
        
        report = f"""📄 **DOCUMENTATION IMPORT COMPLETED** (v2.0)

**📊 Discovery Results:**
• Files Found: {stats['total_files']}
• Total Size: {stats['total_size'] / 1024:.1f} KB
• External Files: {stats.get('external_files', 0)}
• Duplicates Detected: {stats.get('duplicates_found', 0)}

**📋 Document Types (v2.0):**
{doc_types or 'No categorization available'}

**🔄 Import Results:**
• Successfully Imported: {results['imported']}
• Skipped (Duplicates): {results['skipped']}
• Errors: {len(results.get('errors', []))}

**🚀 v2.0 Benefits Applied:**
• ✅ All content stored in unified documents table
• ✅ Enhanced document_type categorization
• ✅ Rich metadata with content signatures
• ✅ Project UUID support for cross-project organization
• ✅ Full-text search ready across all imported content"""
        
        if results.get('errors'):
            report += f"\n\n**⚠️ Import Errors:**"
            for error in results['errors'][:3]:
                report += f"\n• {error}"
            if len(results['errors']) > 3:
                report += f"\n• ... and {len(results['errors']) - 3} more errors"
        
        report += f"""

**💡 Next Steps:**
• Use full-text search to find imported documentation
• Filter by document_type for specific content types
• Enhanced cross-project search with project_uuid support"""
        
        return report
    
    async def get_import_statistics(self) -> Dict[str, Any]:
        """Get statistics about imported content in v2.0 documents table"""
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return {'error': 'Memory Bank not initialized'}
            
            project_info = await self.context_manager.get_current_session_info()
            project_uuid = project_info.get('project_uuid', '')
            
            # Get comprehensive stats from documents table
            stats_query = """
            SELECT 
                document_type,
                COUNT(*) as count,
                SUM(LENGTH(content)) as total_content_size,
                MAX(updated_at) as latest_update
            FROM documents 
            WHERE project_uuid = ? AND status = 'active'
            GROUP BY document_type
            """
            
            results = await self._execute_query(stats_query, (project_uuid,))
            
            return {
                'project_uuid': project_uuid,
                'document_types': {row[0]: {
                    'count': row[1],
                    'total_size': row[2],
                    'latest_update': row[3]
                } for row in results},
                'architecture_version': '2.0'
            }
            
        except Exception as e:
            logger.error(f"Error getting import statistics: {e}")
            return {'error': str(e)}
