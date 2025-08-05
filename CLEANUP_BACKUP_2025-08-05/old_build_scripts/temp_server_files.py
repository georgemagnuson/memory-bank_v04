def get_server_files():
    """Define all server files to include in DXT package - Updated for actual file structure"""
    base_path = "server/memory_bank_mcp"
    
    server_files = [
        # Core MCP Server Files
        f"{base_path}/__init__.py",
        f"{base_path}/__main__.py",
        f"{base_path}/main.py",
        
        # Enhanced Core System (v2.1)
        f"{base_path}/database.py",
        f"{base_path}/context_manager.py",
        f"{base_path}/core_tools.py",
        f"{base_path}/content_tools.py",
        f"{base_path}/migration_tools.py",
        f"{base_path}/backup_tools.py",
        
        # Registry Integration System (Context Propagation Fix)
        f"{base_path}/context_registry.py",
        f"{base_path}/enhanced_project_manager.py", 
        f"{base_path}/enhanced_context_tools.py",
        f"{base_path}/registry_integration.py",
        
        # Additional Tools
        f"{base_path}/project_manager.py",
        f"{base_path}/project_tools.py",
        f"{base_path}/schema_manager.py",
        f"{base_path}/sql_tools.py",
        f"{base_path}/migration.py",
        
        # Core Tools Modules (actual files)
        f"{base_path}/core_tools_modules/__init__.py",
        f"{base_path}/core_tools_modules/content_search_engine.py",
        f"{base_path}/core_tools_modules/content_extractor.py",
        f"{base_path}/core_tools_modules/database_interface.py",
        
        # Content Tools Modules (actual files)
        f"{base_path}/content_tools_modules/__init__.py",
        f"{base_path}/content_tools_modules/search_engine.py",
        f"{base_path}/content_tools_modules/fts_manager.py",
        f"{base_path}/content_tools_modules/import_manager.py",
        
        # Migration Tools Modules (actual files)
        f"{base_path}/migration_tools_modules/__init__.py",
        f"{base_path}/migration_tools_modules/migration_analyzer.py",
        f"{base_path}/migration_tools_modules/content_importer.py",
        f"{base_path}/migration_tools_modules/project_migrator.py",
        
        # Backup Tools Modules
        f"{base_path}/backup_tools_modules/__init__.py",
        f"{base_path}/backup_tools_modules/backup_manager.py",
        f"{base_path}/backup_tools_modules/template_manager.py",
        
        # Schema Manager Modules
        f"{base_path}/schema_manager_modules/__init__.py",
        f"{base_path}/schema_manager_modules/schema_template_manager.py",
        
        # Migration Modules
        f"{base_path}/migration_modules/__init__.py",
        f"{base_path}/migration_modules/content_extractors.py",
        f"{base_path}/migration_modules/smart_merge.py",
        f"{base_path}/migration_modules/markdown_importer.py",
        
        # SQL Tools Modules
        f"{base_path}/sql_tools_modules/__init__.py",
        
        # Project Tools Modules
        f"{base_path}/project_tools_modules/__init__.py",
        
        # Schema Templates (v2.1 with importance)
        f"{base_path}/context_template_v2.0.ddl",
        f"{base_path}/context_template_v2.0.db",
        f"{base_path}/schema_v2_0_template.sql",
        
        # Version Detection and Utilities
        f"{base_path}/schema_version_detector.py"
    ]
    
    return server_files