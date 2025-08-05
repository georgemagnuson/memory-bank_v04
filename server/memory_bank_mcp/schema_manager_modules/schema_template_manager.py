#!/usr/bin/env python3
"""
server/memory_bank_mcp/schema_template_manager.py
Generated: 2025-07-29.0125
Purpose: Schema template storage and retrieval for Memory Bank v2.0

Handles:
- Template storage in documents/unified_documents table
- Version-aware template management
- v2.0 schema template generation and storage
"""

import logging
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

class SchemaTemplateManager:
    """Manages schema templates stored in the documents table"""
    
    @staticmethod
    async def store_template(context_manager, template_name: str, template_content: str, 
                           description: str = "") -> bool:
        """Store schema template in documents table"""
        try:
            if not context_manager.is_initialized():
                logger.error("Context manager not initialized")
                return False
                
            cursor = context_manager.database.get_cursor()
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Check if we have documents table (v2.0) or unified_documents (v1.4.0)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('documents', 'unified_documents')")
            tables = [row[0] for row in cursor.fetchall()]
            
            if 'documents' in tables:
                # v2.0 schema - use documents table
                cursor.execute("""
                    INSERT OR REPLACE INTO documents 
                    (document_id, title, content, document_type, importance_rating, 
                     project_uuid, file_path, tags, created_date, modified_date)
                    VALUES (?, ?, ?, 'template', 10, NULL, NULL, 'schema,template,v2.0', ?, ?)
                """, (f"template_{template_name}", template_name, template_content, 
                      timestamp, timestamp))
            elif 'unified_documents' in tables:
                # v1.4.0 schema - use unified_documents table
                cursor.execute("""
                    INSERT OR REPLACE INTO unified_documents 
                    (original_uuid, source_table, document_type, title, content, summary,
                     tags, metadata, created_at, updated_at, status)
                    VALUES (?, 'templates', 'template', ?, ?, ?, ?, ?, ?, ?, 'active')
                """, (f"template_{template_name}", template_name, template_content, description,
                      '["schema","template","v2.0"]', 
                      '{"importance": 10, "template_type": "schema"}',
                      timestamp, timestamp))
            else:
                logger.error("No suitable table found for template storage")
                return False
            
            context_manager.database.connection.commit()
            logger.info(f"Schema template stored: {template_name}")
            return True
            
        except Exception as e:
            logger.error(f"Template storage failed: {e}")
            return False
    
    @staticmethod
    async def get_template(context_manager, template_name: str) -> Optional[str]:
        """Retrieve schema template from documents table"""
        try:
            if not context_manager.is_initialized():
                logger.error("Context manager not initialized")
                return None
                
            cursor = context_manager.database.get_cursor()
            
            # Try documents table first (v2.0)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT content FROM documents 
                    WHERE document_type = 'template' AND title = ?
                """, (template_name,))
                result = cursor.fetchone()
                if result:
                    logger.info(f"Schema template retrieved from documents: {template_name}")
                    return result[0]
            
            # Try unified_documents table (v1.4.0)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='unified_documents'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT content FROM unified_documents 
                    WHERE document_type = 'template' AND title = ?
                """, (template_name,))
                result = cursor.fetchone()
                if result:
                    logger.info(f"Schema template retrieved from unified_documents: {template_name}")
                    return result[0]
            
            logger.warning(f"Schema template not found: {template_name}")
            return None
                
        except Exception as e:
            logger.error(f"Template retrieval failed: {e}")
            return None
    
    @staticmethod
    async def list_templates(context_manager) -> list:
        """List all available schema templates"""
        try:
            if not context_manager.is_initialized():
                logger.error("Context manager not initialized")
                return []
                
            cursor = context_manager.database.get_cursor()
            templates = []
            
            # Check documents table first (v2.0)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='documents'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT title, created_date FROM documents 
                    WHERE document_type = 'template' 
                    ORDER BY created_date DESC
                """)
                templates.extend(cursor.fetchall())
            
            # Check unified_documents table (v1.4.0)
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='unified_documents'")
            if cursor.fetchone():
                cursor.execute("""
                    SELECT title, created_at FROM unified_documents 
                    WHERE document_type = 'template' 
                    ORDER BY created_at DESC
                """)
                templates.extend(cursor.fetchall())
            
            return templates
                
        except Exception as e:
            logger.error(f"Template listing failed: {e}")
            return []
    
    @staticmethod
    def get_v2_schema_template() -> str:
        """Get the v2.0 schema template definition"""
        return """# Memory Bank v2.0 Schema Template
**Version:** 2.0
**Generated:** 2025-07-29T01:25:58+12:00
**Purpose:** Clean unified architecture with documents table

## Core Schema Changes

### Main Content Table (v2.0)
```sql
-- Renamed from unified_documents
CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uuid TEXT NOT NULL,
    project_uuid TEXT NOT NULL,
    source_table TEXT NOT NULL,
    source_id INTEGER,
    document_type TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    summary TEXT,
    tags TEXT DEFAULT '[]',
    metadata TEXT DEFAULT '{}',
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    imported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'active',
    FOREIGN KEY (project_uuid) REFERENCES projects (uuid)
);
```

### Full-Text Search (v2.0)
```sql
-- Renamed from unified_documents_fts
CREATE VIRTUAL TABLE documents_fts USING fts5(
    title, content, summary, tags,
    content='documents',
    content_rowid='id'
);
```

### Version Management
```sql
-- Set database version for v2.0
PRAGMA user_version = 4;
```

## Migration Process

### From v1.4.0 to v2.0
1. **Backup Creation:** Automatic backup before migration
2. **Table Rename:** unified_documents → documents (1:1 mapping)
3. **FTS Update:** All FTS tables renamed to match
4. **Version Update:** PRAGMA user_version = 4
5. **Template Storage:** This template stored for reference

### Supporting Tables (Preserved)
- chat_sessions (preserved from v1.4.0)
- projects (preserved from v1.4.0)  
- project_context (preserved from v1.4.0)
- semantic_equivalents (enhanced search)

## Benefits
- **Clean Naming:** No more "unified" prefix confusion
- **Backward Compatibility:** All functionality preserved
- **Performance:** Improved query performance
- **Future Ready:** Foundation for v2.0 features

## Migration Notes
- **Data Safety:** All records preserved during migration
- **Rollback Available:** Automatic backup enables rollback
- **Zero Data Loss:** 1:1 table rename preserves all content
- **FTS Synchronization:** Full-text search updated automatically
"""

# Export main class
__all__ = ['SchemaTemplateManager']
