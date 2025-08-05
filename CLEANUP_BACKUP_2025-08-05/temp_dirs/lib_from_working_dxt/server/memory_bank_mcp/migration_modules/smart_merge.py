"""
migration_modules/smart_merge.py
Generated: 2025-07-29.2316
Purpose: Smart Merge engine for Memory Bank v2.0 unified document architecture
Handles intelligent change detection and content merging
"""

import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timezone

logger = logging.getLogger("memory_bank_mcp.migration.smart_merge")


class SmartMergeEngine:
    """
    Smart Merge engine for unified document architecture
    
    v2.0 Changes:
    - Works with unified documents table instead of separate tables
    - Uses document_type field for categorization
    - Maintains content signatures for duplicate detection
    - Handles record status management (active, superseded, obsolete)
    """
    
    def __init__(self, context_manager):
        self.context_manager = context_manager
    
    async def analyze_content_changes(self, current_items: List[Dict[str, Any]], 
                                    existing_items: List[Dict[str, Any]], 
                                    match_field: str = "title") -> Dict[str, Any]:
        """
        Analyze changes between current and existing items for unified documents
        
        Args:
            current_items: Items from current file content
            existing_items: Items from database
            match_field: Field to use for matching (title, summary, etc.)
            
        Returns:
            Analysis with new, updated, and obsolete items categorized
        """
        analysis = {
            'new_items': [],
            'updated_items': [],
            'unchanged_items': [],
            'obsolete_items': [],
            'statistics': {
                'total_current': len(current_items),
                'total_existing': len(existing_items),
                'new_count': 0,
                'updated_count': 0,
                'unchanged_count': 0,
                'obsolete_count': 0
            }
        }
        
        # Create lookup maps
        existing_by_field = {item.get(match_field, ''): item for item in existing_items}
        current_by_field = {item.get(match_field, ''): item for item in current_items}
        
        # Process current items
        for current_item in current_items:
            match_value = current_item.get(match_field, '')
            
            if match_value in existing_by_field:
                existing_item = existing_by_field[match_value]
                
                # Check if content has changed
                if self._has_content_changed(current_item, existing_item):
                    analysis['updated_items'].append({
                        'current': current_item,
                        'existing_uuid': existing_item.get('uuid'),
                        'change_type': 'content_updated',
                        'changes_detected': self._detect_specific_changes(current_item, existing_item)
                    })
                    analysis['statistics']['updated_count'] += 1
                else:
                    analysis['unchanged_items'].append({
                        'current': current_item,
                        'existing_uuid': existing_item.get('uuid'),
                        'status': 'no_changes'
                    })
                    analysis['statistics']['unchanged_count'] += 1
            else:
                # New item
                analysis['new_items'].append(current_item)
                analysis['statistics']['new_count'] += 1
        
        # Find obsolete items (in database but not in current file)
        for existing_item in existing_items:
            match_value = existing_item.get(match_field, '')
            if match_value not in current_by_field:
                analysis['obsolete_items'].append(existing_item)
                analysis['statistics']['obsolete_count'] += 1
        
        logger.info(f"Smart merge analysis: {analysis['statistics']['new_count']} new, "
                   f"{analysis['statistics']['updated_count']} updated, "
                   f"{analysis['statistics']['obsolete_count']} obsolete")
        
        return analysis
    
    def _has_content_changed(self, current_item: Dict[str, Any], existing_item: Dict[str, Any]) -> bool:
        """Check if content has meaningfully changed"""
        current_content = current_item.get('content', '')
        existing_content = existing_item.get('content', '')
        
        # Generate content signatures for comparison
        current_signature = self._generate_content_signature(current_content)
        existing_signature = self._generate_content_signature(existing_content)
        
        return current_signature != existing_signature
    
    def _detect_specific_changes(self, current_item: Dict[str, Any], existing_item: Dict[str, Any]) -> List[str]:
        """Detect specific types of changes between items"""
        changes = []
        
        # Check title changes
        if current_item.get('title') != existing_item.get('title'):
            changes.append('title_modified')
        
        # Check content length changes
        current_len = len(current_item.get('content', ''))
        existing_len = len(existing_item.get('content', ''))
        
        if abs(current_len - existing_len) > 100:  # Significant length change
            if current_len > existing_len:
                changes.append('content_expanded')
            else:
                changes.append('content_reduced')
        
        # Check for structural changes
        current_sections = len(self._extract_sections(current_item.get('content', '')))
        existing_sections = len(self._extract_sections(existing_item.get('content', '')))
        
        if current_sections != existing_sections:
            changes.append('structure_modified')
        
        return changes
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from content"""
        import re
        return re.findall(r'^## (.+)$', content, re.MULTILINE)
    
    def _generate_content_signature(self, content: str) -> str:
        """Generate normalized content signature for comparison"""
        import re
        
        # Normalize content for signature
        normalized = content.strip().lower()
        normalized = re.sub(r'\s+', ' ', normalized)  # Normalize whitespace
        normalized = re.sub(r'[^\w\s]', '', normalized)  # Remove punctuation
        
        return hashlib.md5(normalized.encode()).hexdigest()
    
    async def merge_documents_to_unified_table(self, items: List[Dict[str, Any]], 
                                             document_type: str, source_file: str,
                                             merge_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge documents into unified documents table based on analysis
        
        Args:
            items: Items to merge
            document_type: Type for unified documents table
            source_file: Source file path
            merge_analysis: Analysis from analyze_content_changes
            
        Returns:
            Merge results with statistics
        """
        results = {
            'items_new': 0,
            'items_updated': 0,
            'items_superseded': 0,
            'items_unchanged': 0,
            'errors': []
        }
        
        try:
            # Process new items
            for item in merge_analysis['new_items']:
                await self._create_unified_document(item, document_type, source_file)
                results['items_new'] += 1
            
            # Process updated items
            for item_data in merge_analysis['updated_items']:
                current_item = item_data['current']
                existing_uuid = item_data['existing_uuid']
                
                # Mark old version as superseded
                await self._mark_document_superseded(existing_uuid)
                
                # Create new version
                await self._create_unified_document(current_item, document_type, source_file)
                
                results['items_updated'] += 1
                results['items_superseded'] += 1
            
            # Handle obsolete items
            for obsolete_item in merge_analysis['obsolete_items']:
                await self._mark_document_obsolete(obsolete_item['uuid'])
                results['items_superseded'] += 1
            
            # Count unchanged items
            results['items_unchanged'] = len(merge_analysis['unchanged_items'])
            
            logger.info(f"Merged to unified documents: {results['items_new']} new, "
                       f"{results['items_updated']} updated, {results['items_superseded']} superseded")
            
        except Exception as e:
            error_msg = f"Error merging documents: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
    
    async def _create_unified_document(self, item: Dict[str, Any], document_type: str, source_file: str) -> str:
        """Create new document in unified documents table"""
        import uuid as uuid_module
        
        document_uuid = str(uuid_module.uuid4())
        project_uuid = self.context_manager.database.project_uuid
        
        # Extract fields with fallbacks
        title = item.get('title', item.get('summary', 'Untitled'))
        content = item.get('content', item.get('full_content', ''))
        
        # Create content signature
        content_signature = self._generate_content_signature(content)
        
        query = """
        INSERT INTO unified_documents 
        (uuid, project_uuid, title, content, document_type, source_file, 
         content_signature, record_status, created_at, updated_at, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?)
        """
        
        # Build metadata
        metadata = {
            'migrated_from': document_type,
            'original_source': source_file,
            'migration_timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        # Add any additional metadata from the item
        for key in ['artifact_type', 'discussion_type', 'pattern_type', 'rule_category', 'language']:
            if key in item:
                metadata[key] = item[key]
        
        import json
        await self.context_manager.database._execute_query(
            query, (document_uuid, project_uuid, title, content, document_type, 
                   source_file, content_signature, json.dumps(metadata))
        )
        
        logger.debug(f"Created unified document: {title} (type: {document_type})")
        return document_uuid
    
    async def _mark_document_superseded(self, document_uuid: str) -> None:
        """Mark document as superseded"""
        query = """
        UPDATE unified_documents 
        SET record_status = 'superseded', updated_at = CURRENT_TIMESTAMP
        WHERE uuid = ?
        """
        
        await self.context_manager.database._execute_query(query, (document_uuid,))
        logger.debug(f"Marked document {document_uuid} as superseded")
    
    async def _mark_document_obsolete(self, document_uuid: str) -> None:
        """Mark document as obsolete"""
        query = """
        UPDATE unified_documents 
        SET record_status = 'obsolete', updated_at = CURRENT_TIMESTAMP
        WHERE uuid = ?
        """
        
        await self.context_manager.database._execute_query(query, (document_uuid,))
        logger.debug(f"Marked document {document_uuid} as obsolete")
    
    async def get_existing_documents_by_source(self, source_file: str, document_type: str) -> List[Dict[str, Any]]:
        """Get existing documents from unified table by source file and type"""
        query = """
        SELECT uuid, title, content, document_type, source_file, content_signature, metadata
        FROM unified_documents 
        WHERE source_file = ? AND document_type = ? AND record_status = 'active'
        ORDER BY created_at DESC
        """
        
        result = await self.context_manager.database._execute_query(query, (source_file, document_type))
        
        documents = []
        if result:
            for row in result:
                import json
                metadata = {}
                try:
                    metadata = json.loads(row[6]) if row[6] else {}
                except:
                    pass
                
                documents.append({
                    'uuid': row[0],
                    'title': row[1],
                    'content': row[2],
                    'document_type': row[3],
                    'source_file': row[4],
                    'content_signature': row[5],
                    'metadata': metadata
                })
        
        return documents
    
    async def deduplicate_by_content_signature(self, document_type: str = None) -> Dict[str, Any]:
        """Remove duplicate documents based on content signatures"""
        results = {
            'duplicates_found': 0,
            'duplicates_removed': 0,
            'errors': []
        }
        
        try:
            # Build query with optional document type filter
            query = """
            SELECT uuid, title, content_signature, created_at
            FROM unified_documents 
            WHERE record_status = 'active'
            """
            params = []
            
            if document_type:
                query += " AND document_type = ?"
                params.append(document_type)
            
            query += " ORDER BY content_signature, created_at"
            
            result = await self.context_manager.database._execute_query(query, params)
            
            if result:
                # Group by content signature
                signature_groups = {}
                for row in result:
                    uuid, title, signature, created_at = row
                    if signature not in signature_groups:
                        signature_groups[signature] = []
                    signature_groups[signature].append({
                        'uuid': uuid,
                        'title': title,
                        'created_at': created_at
                    })
                
                # Process duplicates (keep the oldest, mark others as obsolete)
                for signature, documents in signature_groups.items():
                    if len(documents) > 1:
                        results['duplicates_found'] += len(documents) - 1
                        
                        # Sort by creation date, keep the first one
                        documents.sort(key=lambda x: x['created_at'])
                        
                        # Mark duplicates as obsolete
                        for duplicate in documents[1:]:
                            await self._mark_document_obsolete(duplicate['uuid'])
                            results['duplicates_removed'] += 1
                            
                            logger.info(f"Removed duplicate document: {duplicate['title']}")
            
        except Exception as e:
            error_msg = f"Error during deduplication: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
        
        return results
