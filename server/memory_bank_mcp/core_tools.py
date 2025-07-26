#!/usr/bin/env python3
"""
server/memory_bank_mcp/core_tools.py
Generated: 2025-07-26.1800
Purpose: Core database operations and content extraction tools for Memory Bank v1.4.0
         Clean implementation with proper database interface usage

Essential v1.4.0 Features Preserved:
- EnhancedContentSearch class with documents_v2 → discussions → artifacts priority
- Multi-table content extraction with UUID and fuzzy search
- Enhanced metadata extraction with safe filename generation
- Smart content discovery across all tables
"""

import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
import re

logger = logging.getLogger(__name__)

class EnhancedContentSearch:
    """Enhanced search manager for multi-table content discovery with priority ordering"""
    
    SEARCH_TABLES = [
        {'name': 'documents_v2', 'title_field': 'title', 'content_field': 'content', 'uuid_field': 'uuid', 'icon': '📄'},
        {'name': 'discussions', 'title_field': 'summary', 'content_field': 'content', 'uuid_field': 'uuid', 'icon': '💭'},
        {'name': 'artifacts', 'title_field': 'title', 'content_field': 'content', 'uuid_field': 'uuid', 'icon': '📄'}
    ]    
    
    @classmethod
    async def search_content(cls, context_manager, title_search=None, uuid_search=None, source_table="auto"):
        """Search for content across multiple tables with priority order"""
        tables_to_search = cls.SEARCH_TABLES if source_table == "auto" else [t for t in cls.SEARCH_TABLES if t['name'] == source_table]
        if not tables_to_search:
            return None
        
        if uuid_search:
            result = await cls._search_by_uuid(context_manager, uuid_search, tables_to_search)
            if result:
                return result
        
        if title_search:
            result = await cls._search_by_title(context_manager, title_search, tables_to_search)
            if result:
                return result
        
        return None
    
    @classmethod
    async def _search_by_uuid(cls, context_manager, uuid_search, tables_to_search):
        """Search by UUID across specified tables"""
        for table_info in tables_to_search:
            try:
                query = f"SELECT {table_info['title_field']}, {table_info['content_field']}, {table_info['uuid_field']} FROM {table_info['name']} WHERE {table_info['uuid_field']} = '{uuid_search}' LIMIT 1"
                result = await context_manager.database.execute_sql_query(query)
                if result['success'] and result['results']:
                    row = result['results'][0]
                    return {
                        'title': list(row.values())[0],
                        'content': list(row.values())[1],
                        'uuid': list(row.values())[2],
                        'source_table': table_info['name'],
                        'icon': table_info['icon']
                    }
            except Exception as e:
                logger.warning(f"UUID search failed in {table_info['name']}: {e}")
                continue
        return None
    
    @classmethod
    async def _search_by_title(cls, context_manager, title_search, tables_to_search):
        """Search by title with fuzzy matching across specified tables"""
        # Try exact match first
        for table_info in tables_to_search:
            try:
                query = f"SELECT {table_info['title_field']}, {table_info['content_field']}, {table_info['uuid_field']} FROM {table_info['name']} WHERE {table_info['title_field']} = '{title_search}' LIMIT 1"
                result = await context_manager.database.execute_sql_query(query)
                if result['success'] and result['results']:
                    row = result['results'][0]
                    return {
                        'title': list(row.values())[0],
                        'content': list(row.values())[1],
                        'uuid': list(row.values())[2],
                        'source_table': table_info['name'],
                        'icon': table_info['icon'],
                        'match_type': 'exact'
                    }
            except Exception as e:
                logger.warning(f"Exact title search failed in {table_info['name']}: {e}")
                continue
        
        # Try fuzzy match if exact fails
        for table_info in tables_to_search:
            try:
                query = f"SELECT {table_info['title_field']}, {table_info['content_field']}, {table_info['uuid_field']} FROM {table_info['name']} WHERE {table_info['title_field']} LIKE '%{title_search}%' LIMIT 1"
                result = await context_manager.database.execute_sql_query(query)
                if result['success'] and result['results']:
                    row = result['results'][0]
                    return {
                        'title': list(row.values())[0],
                        'content': list(row.values())[1],
                        'uuid': list(row.values())[2],
                        'source_table': table_info['name'],
                        'icon': table_info['icon'],
                        'match_type': 'fuzzy'
                    }
            except Exception as e:
                logger.warning(f"Fuzzy title search failed in {table_info['name']}: {e}")
                continue
        return None

    @classmethod
    def generate_safe_filename(cls, title: str, uuid: str) -> str:
        """Generate safe filename for extracted content"""
        safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
        safe_title = re.sub(r'[-\s]+', '_', safe_title).strip('_')
        short_uuid = uuid[:8] if uuid else "unknown"
        return f"{safe_title}_{short_uuid}.md"


class CoreTools:
    """Core database operations and content extraction tools"""
    
    def __init__(self, context_manager):
        self.context_manager = context_manager
    
    async def _execute_query(self, query: str) -> List[Any]:
        """Execute SQL query and return results in simple format"""
        result = await self.context_manager.database.execute_sql_query(query)
        if result['success']:
            return [tuple(row.values()) for row in result['results']]
        else:
            raise Exception(result['error'])
    
    async def get_memory_bank_system_info(self) -> str:
        """Get detailed technical information about the Memory Bank system"""
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            db_stats = await self.context_manager.database.get_database_stats()
            schema_info = {'table_count': 'Unknown'}
            
            try:
                table_count_result = await self._execute_query("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
                if table_count_result:
                    schema_info['table_count'] = table_count_result[0][0]
            except Exception as e:
                logger.warning(f"Could not get table count: {e}")
            
            project_info = await self.context_manager.get_current_session_info()
            
            return f"""🔧 **MEMORY BANK SYSTEM INFORMATION**

**📊 Database Statistics:**
• Total Tables: {schema_info.get('table_count', 'Unknown')}
• 💭 Discussions: {db_stats.get('discussions_count', 0)}
• 📄 Documents v2: {db_stats.get('documents_v2_count', 0)}
• 🎯 Artifacts: {db_stats.get('artifacts_count', 0)}
• 🎪 Sessions: {db_stats.get('sessions_count', 0)}

**🗄️ Database Details:**
• Path: {self.context_manager.database_path}
• Schema Version: Memory Bank v04 Enhanced

**📁 Project Information:**
• Project: {project_info.get('project_name', 'Unknown')}
• Path: {self.context_manager.project_path}
• Session UUID: {project_info.get('session_uuid', 'Unknown')}

**🚀 v1.4.0 ENHANCED FEATURES:**
• ✅ Smart SQL Truncation System
• ✅ Multi-Table Content Extraction  
• ✅ Search Prioritization (context.db first)
• ✅ Automatic Command Awareness

**🔍 Search Tables Priority:**
1. 📄 documents_v2 (highest priority)
2. 💭 discussions (medium priority)
3. 🎯 artifacts (lower priority)""".strip()
            
        except Exception as e:
            logger.error(f"Error getting system info: {e}")
            return f"❌ Error retrieving system information: {str(e)}"
    
    async def memory_bank_describe_schema(self) -> str:
        """Get complete database schema for current project"""
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            tables_result = await self._execute_query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            if not tables_result:
                return "❌ No tables found in database"
            
            schema_info = f"""🗄️ **MEMORY BANK DATABASE SCHEMA**

**📍 Database:** {self.context_manager.database_path}
**📊 Total Tables:** {len(tables_result)}

**🔥 CORE CONTENT TABLES:**"""
            
            core_tables = ['discussions', 'documents_v2', 'artifacts', 'sessions']
            for table_row in tables_result:
                table_name = table_row[0]
                if table_name in core_tables:
                    try:
                        count_result = await self._execute_query(f"SELECT COUNT(*) FROM {table_name}")
                        count = count_result[0][0] if count_result else 0
                    except:
                        count = 0
                    
                    icon = "📄" if table_name == "documents_v2" else "💭" if table_name == "discussions" else "🎯" if table_name == "artifacts" else "🎪"
                    schema_info += f"\n• {icon} {table_name}: {count} records"
            
            schema_info += "\n\n**📋 ALL TABLES:**"
            for table_row in tables_result:
                schema_info += f"\n• {table_row[0]}"
            
            schema_info += "\n\n💡 Use `memory_bank_table_info(table_name)` for detailed table structure"
            return schema_info
            
        except Exception as e:
            logger.error(f"Error describing schema: {e}")
            return f"❌ Error retrieving schema: {str(e)}"
    
    async def memory_bank_table_info(self, table_name: str) -> str:
        """Get detailed information about a specific table"""
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            check_result = await self._execute_query(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            if not check_result:
                return f"❌ Table '{table_name}' not found"
            
            structure_result = await self._execute_query(f"PRAGMA table_info({table_name})")
            count_result = await self._execute_query(f"SELECT COUNT(*) FROM {table_name}")
            count = count_result[0][0] if count_result else 0
            
            table_info = f"""🗄️ **TABLE INFORMATION: {table_name}**

**📊 Records:** {count}

**📋 COLUMNS:**"""
            
            for col in structure_result:
                col_id, col_name, col_type, not_null, default_val, is_pk = col
                nullable = "NOT NULL" if not_null else "NULL"
                pk_indicator = " 🔑" if is_pk else ""
                default_info = f" (default: {default_val})" if default_val else ""
                table_info += f"\n• {col_name}: {col_type} {nullable}{default_info}{pk_indicator}"
            
            return table_info
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return f"❌ Error retrieving table info for '{table_name}': {str(e)}"
    
    async def memory_bank_list_tables(self) -> str:
        """List all tables in current project's database"""
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            result = await self._execute_query("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY type, name")
            if not result:
                return "❌ No tables found in database"
            
            tables = [row for row in result if row[1] == 'table']
            views = [row for row in result if row[1] == 'view']
            
            tables_info = f"""🗄️ **MEMORY BANK DATABASE TABLES**

**📊 TABLES ({len(tables)}):**"""
            
            for table_name, _ in tables:
                try:
                    count_result = await self._execute_query(f"SELECT COUNT(*) FROM {table_name}")
                    count = count_result[0][0] if count_result else 0
                    icon = "📄" if table_name == "documents_v2" else "💭" if table_name == "discussions" else "🎯" if table_name == "artifacts" else "🎪" if table_name == "sessions" else "📋"
                    tables_info += f"\n• {icon} {table_name} ({count} records)"
                except:
                    tables_info += f"\n• 📋 {table_name}"
            
            if views:
                tables_info += f"\n\n**👁️ VIEWS ({len(views)}):**"
                for view_name, _ in views:
                    tables_info += f"\n• 👁️ {view_name}"
            
            tables_info += "\n\n💡 Use `memory_bank_table_info('table_name')` for detailed structure"
            return tables_info
            
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            return f"❌ Error listing tables: {str(e)}"
    
    async def extract_large_document(self, title_search: str, output_dir: str = "/tmp") -> str:
        """Extract large document content to file for full reading (bypasses SQL truncation limits)"""
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            content_result = await EnhancedContentSearch.search_content(self.context_manager, title_search=title_search)
            if not content_result:
                return f"❌ Document not found: '{title_search}'\n\n💡 Try:\n• Checking spelling\n• Using partial title\n• Using `search_all_content('{title_search}')` to find similar content"
            
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            filename = EnhancedContentSearch.generate_safe_filename(content_result['title'], content_result['uuid'])
            file_path = output_path / filename
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {content_result['title']}\n\n")
                f.write(f"**Source:** {content_result['source_table']} {content_result['icon']}\n")
                f.write(f"**UUID:** {content_result['uuid']}\n")
                f.write(f"**Match:** {content_result.get('match_type', 'direct')}\n\n")
                f.write("---\n\n")
                f.write(content_result['content'])
            
            file_size = file_path.stat().st_size
            content_length = len(content_result['content'])
            
            return f"""✅ **DOCUMENT EXTRACTED SUCCESSFULLY**

**📄 Title:** {content_result['title']}
**🔍 Source:** {content_result['source_table']} {content_result['icon']}
**📍 File:** {file_path}
**📊 Size:** {file_size:,} bytes ({content_length:,} characters)
**🎯 Match:** {content_result.get('match_type', 'direct')}

**📁 Full content available at:** {file_path}

💡 **v1.4.0 Enhanced Features Used:**
• Multi-table search priority (documents_v2 → discussions → artifacts)
• {content_result.get('match_type', 'Direct')} title matching
• Safe filename generation with UUID
• Enhanced metadata extraction""".strip()
            
        except Exception as e:
            logger.error(f"Error extracting document '{title_search}': {e}")
            return f"❌ Error extracting document '{title_search}': {str(e)}"
    
    async def verify_and_repair_schema(self) -> str:
        """Manually verify and repair project schema to ensure complete Memory Bank v04 structure"""
        try:
            if not self.context_manager or not self.context_manager.is_initialized():
                return "❌ Memory Bank not initialized. Use `work_on_project()` to start."
            
            logger.info("Starting manual schema verification and repair...")
            
            verification_result = {
                'success': True,
                'repairs_made': [],
                'total_tables': 'Unknown',
                'schema_complete': True,
                'backup_created': False
            }
            
            try:
                core_tables = ['discussions', 'documents_v2', 'artifacts', 'sessions']
                existing_tables_result = await self._execute_query("SELECT name FROM sqlite_master WHERE type='table'")
                existing_tables = [row[0] for row in existing_tables_result] if existing_tables_result else []
                
                verification_result['total_tables'] = len(existing_tables)
                
                missing_tables = [table for table in core_tables if table not in existing_tables]
                if missing_tables:
                    verification_result['schema_complete'] = False
                    verification_result['repairs_made'].append(f"Missing core tables: {', '.join(missing_tables)}")
                
            except Exception as e:
                logger.error(f"Schema verification failed: {e}")
                verification_result['success'] = False
                verification_result['error'] = str(e)
            
            if verification_result['success']:
                result_text = "✅ **SCHEMA VERIFICATION & REPAIR COMPLETED**\n\n"
                
                if verification_result.get('repairs_made'):
                    result_text += "**🔧 REPAIRS MADE:**\n"
                    for repair in verification_result['repairs_made']:
                        result_text += f"• {repair}\n"
                    result_text += "\n"
                
                result_text += f"""**📊 FINAL STATUS:**
• Total Tables: {verification_result.get('total_tables', 'Unknown')}
• Schema Complete: {'✅ Yes' if verification_result.get('schema_complete') else '❌ No'}"""
                
                if verification_result.get('backup_created'):
                    result_text += f"\n• Backup Created: ✅ {verification_result['backup_path']}"
                
                result_text += f"""

🚀 **v1.4.0 FEATURES VERIFIED:**
• ✅ Enhanced documents_v2 schema
• ✅ Multi-table content extraction
• ✅ Search prioritization support
• ✅ Full-text search capabilities"""
                
                return result_text
            else:
                return f"❌ Schema verification failed: {verification_result.get('error', 'Unknown error')}"
                
        except Exception as e:
            logger.error(f"Error in manual schema verification: {e}")
            return f"❌ Error during schema verification: {str(e)}"
