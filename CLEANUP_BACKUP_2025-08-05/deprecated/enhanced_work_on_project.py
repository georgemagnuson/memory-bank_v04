🚀 Starting automatic migration...")
        migration_success = complete_v21_migration(database_path, dry_run=False)
        
        if migration_success:
            # Verify final state
            final_schema = EnhancedVersionDetector.detect_version_enhanced(database_path)
            final_records = sum(final_schema.record_counts.values())
            
            return {
                "success": True,
                "project_name": project_name,
                "project_path": project_path,
                "database_path": database_path,
                "action": "migrated_to_v21",
                "version": str(final_schema.version),
                "migration_type": schema_info.migration_type,
                "records_before": total_records,
                "records_after": final_records,
                "tables_before": schema_info.table_count,
                "tables_after": final_schema.table_count,
                "message": f"✅ Successfully migrated to v{final_schema.version}! Ready to use."
            }
        else:
            return {
                "success": False,
                "error": "Migration failed - check logs for details",
                "project_path": project_path,
                "database_path": database_path,
                "action": "migration_failed"
            }
    
    def _create_new_v21_database(self, database_path: str, project_name: str, 
                                project_path: str) -> Dict[str, Any]:
        """Create a new v2.1 database with clean schema"""
        
        print(f"📄 Creating new v2.1 database: {Path(database_path).name}")
        
        conn = sqlite3.connect(database_path)
        cursor = conn.cursor()
        
        try:
            # Create v2.1 schema
            self._create_v21_schema(cursor)
            
            # Set version
            cursor.execute('PRAGMA user_version = 21')  # v2.1 = version 21
            
            # Create initial project record
            project_uuid = self._generate_project_uuid(project_name)
            cursor.execute("""
                INSERT INTO projects (uuid, name, path, created_at, updated_at, status)
                VALUES (?, ?, ?, datetime('now'), datetime('now'), 'active')
            """, (project_uuid, project_name, project_path))
            
            conn.commit()
            print("   ✅ Created clean v2.1 database with schema")
            
            return {
                "success": True,
                "message": f"✅ Created new v2.1 database for {project_name}",
                "project_uuid": project_uuid
            }
            
        except Exception as e:
            conn.rollback()
            raise Exception(f"Failed to create v2.1 database: {e}")
            
        finally:
            conn.close()
    
    def _create_v21_schema(self, cursor):
        """Create clean v2.1 database schema"""
        
        # Projects table
        cursor.execute("""
            CREATE TABLE projects (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'
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
        
        # Markdown files table
        cursor.execute("""
            CREATE TABLE markdown_files (
                project_uuid TEXT NOT NULL,
                uuid TEXT NOT NULL,
                file_path TEXT NOT NULL,
                title TEXT,
                content TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (project_uuid, uuid),
                FOREIGN KEY (project_uuid) REFERENCES projects(uuid)
            )
        """)
        
        # FTS5 search for markdown files
        cursor.execute("""
            CREATE VIRTUAL TABLE markdown_search USING fts5(
                title,
                content,
                content='markdown_files',
                content_rowid='rowid'
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
        
        # Cross references
        cursor.execute("""
            CREATE TABLE cross_references (
                project_uuid TEXT NOT NULL,
                source_uuid TEXT NOT NULL,
                target_uuid TEXT NOT NULL,
                reference_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (project_uuid, source_uuid, target_uuid),
                FOREIGN KEY (project_uuid) REFERENCES projects(uuid)
            )
        """)
        
        # Project context
        cursor.execute("""
            CREATE TABLE project_context (
                project_uuid TEXT PRIMARY KEY,
                context_data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_uuid) REFERENCES projects(uuid)
            )
        """)
        
        # Create indexes for performance
        indexes = [
            "CREATE INDEX idx_documents_project ON documents(project_uuid)",
            "CREATE INDEX idx_documents_type ON documents(document_type)",
            "CREATE INDEX idx_documents_importance ON documents(importance)",
            "CREATE INDEX idx_documents_status ON documents(status)",
            "CREATE INDEX idx_documents_created ON documents(created_at)",
            "CREATE INDEX idx_markdown_project ON markdown_files(project_uuid)",
            "CREATE INDEX idx_cross_ref_source ON cross_references(source_uuid)",
            "CREATE INDEX idx_cross_ref_target ON cross_references(target_uuid)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        # Insert default semantic equivalents
        default_semantics = [
            ('spec_workflow', 'requirements', 'user_stories,acceptance_criteria,specifications,needs,business_requirements'),
            ('development', 'implementation', 'coding,development,building,creating,programming'),
            ('dxt', 'DXT', 'desktop_extension,claude_extension,mcp_server,installation,package')
        ]
        
        for domain, term, equivalents in default_semantics:
            cursor.execute("""
                INSERT INTO semantic_equivalents (domain, primary_term, equivalent_terms)
                VALUES (?, ?, ?)
            """, (domain, term, equivalents))
    
    def _generate_project_uuid(self, project_name: str) -> str:
        """Generate a project UUID based on project name"""
        import uuid
        import hashlib
        
        # Create deterministic UUID based on project name
        namespace = uuid.UUID('6ba7b810-9dad-11d1-80b4-00c04fd430c8')  # DNS namespace
        project_uuid = str(uuid.uuid5(namespace, project_name))
        return project_uuid

# Example usage and integration
def enhanced_work_on_project_tool(project_path: str) -> str:
    """
    Tool function that can be integrated into Memory Bank MCP server
    
    Args:
        project_path: Path to project directory
        
    Returns:
        Formatted status message
    """
    manager = EnhancedWorkOnProject()
    result = manager.work_on_project(project_path)
    
    if result["success"]:
        action_messages = {
            "created_new_database": f"🆕 Created new v2.1 database",
            "opened_current_database": f"✅ Opened current database",
            "migrated_to_v21": f"🔄 Migrated to v2.1"
        }
        
        action = result.get("action", "unknown")
        action_msg = action_messages.get(action, f"✅ {action}")
        
        # Build status message
        status_lines = [
            f"✅ **Working on Project: {result['project_name']}**",
            "",
            f"📁 **Project Path:** {result['project_path']}",
            f"💾 **Database:** {result['database_path']}",
            "",
            f"{action_msg}",
            f"🏷️ **Version:** v{result.get('version', 'unknown')}",
            f"📋 **Tables:** {result.get('table_count', 'N/A')}",
            f"📄 **Records:** {result.get('record_count', 'N/A')}"
        ]
        
        # Add migration details if applicable
        if action == "migrated_to_v21":
            status_lines.extend([
                "",
                "🔄 **Migration Summary:**",
                f"• Migration type: {result.get('migration_type', 'unknown')}",
                f"• Records: {result.get('records_before', 0)} → {result.get('records_after', 0)}",  
                f"• Tables: {result.get('tables_before', 0)} → {result.get('tables_after', 0)}"
            ])
        
        status_lines.extend([
            "",
            "🛠️ **Tools Ready:**",
            "• Core Tools: ✅ Content operations",
            "• SQL Tools: ✅ Database queries", 
            "• Project Tools: ✅ Project management",
            "• Content Tools: ✅ Document management",
            "• Migration Tools: ✅ Schema operations",
            "• Backup Tools: ✅ Data protection",
            "",
            "🚀 **Memory Bank v2.1 Ready!**",
            "",
            "💡 **Quick Start:**",
            "• `get_current_context()` - Check project status",
            "• `save_info(\"content\", \"category\")` - Save information",  
            "• `search_info(\"query\")` - Find content",
            "• `execute_sql(\"SELECT * FROM documents LIMIT 5\")` - Query database"
        ])
        
        return "\n".join(status_lines)
    
    else:
        return f"""❌ **Failed to work on project**

📁 **Project Path:** {project_path}
❌ **Error:** {result.get('error', 'Unknown error')}

Please check the project path and try again."""

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        project_path = sys.argv[1]
        result = enhanced_work_on_project_tool(project_path)
        print(result)
    else:
        print("Usage: python enhanced_work_on_project.py /path/to/project")
