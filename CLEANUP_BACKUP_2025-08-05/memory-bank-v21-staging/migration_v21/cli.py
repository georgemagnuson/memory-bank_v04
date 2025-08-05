#!/usr/bin/env python3
"""
Memory Bank v2.1 Migration CLI
==============================

Command-line interface for Memory Bank v2.1 migration operations.
"""

import sys
import argparse
from pathlib import Path

# Add the parent directory to sys.path so we can import migration_v21
sys.path.insert(0, str(Path(__file__).parent.parent))

from migration_v21 import MigrationManager, integrate_with_memory_bank

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Memory Bank v2.1 Migration Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze database
  python -m migration_v21.cli analyze /path/to/context.db
  
  # Dry run migration
  python -m migration_v21.cli migrate /path/to/context.db --dry-run
  
  # Perform migration
  python -m migration_v21.cli migrate /path/to/context.db
  
  # Work on project with auto-migration
  python -m migration_v21.cli work-on-project /path/to/project
  
  # Create new v2.1 database
  python -m migration_v21.cli create /path/to/project
  
  # Integrate with existing Memory Bank
  python -m migration_v21.cli integrate
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze database for migration')
    analyze_parser.add_argument('database_path', help='Path to context.db file')
    
    # Migrate command  
    migrate_parser = subparsers.add_parser('migrate', help='Migrate database to v2.1')
    migrate_parser.add_argument('database_path', help='Path to context.db file')
    migrate_parser.add_argument('--dry-run', action='store_true', help='Analyze only, do not migrate')
    migrate_parser.add_argument('--project-uuid', default='legacy-project', help='Project UUID for migrated content')
    
    # Work on project command
    work_parser = subparsers.add_parser('work-on-project', help='Enhanced work_on_project with auto-migration')
    work_parser.add_argument('project_path', help='Path to project directory')
    
    # Create command
    create_parser = subparsers.add_parser('create', help='Create new v2.1 database')
    create_parser.add_argument('project_path', help='Path to project directory')
    
    # Integrate command
    integrate_parser = subparsers.add_parser('integrate', help='Integrate with existing Memory Bank')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate v2.1 database')
    validate_parser.add_argument('database_path', help='Path to context.db file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    manager = MigrationManager()
    
    try:
        if args.command == 'analyze':
            print(manager.analyze_database(args.database_path))
            return 0
            
        elif args.command == 'migrate':
            result = manager.migrate_to_v21(args.database_path, dry_run=args.dry_run, project_uuid=args.project_uuid)
            if result['success']:
                print(f"✅ {result['message']}")
                return 0
            else:
                print(f"❌ {result.get('error', 'Migration failed')}")
                return 1
                
        elif args.command == 'work-on-project':
            result = manager.work_on_project(args.project_path)
            if result['success']:
                print(f"✅ {result['message']}")
                print(f"Database: {result.get('database_path', 'Unknown')}")
                print(f"Version: v{result.get('version', 'Unknown')}")
                return 0
            else:
                print(f"❌ {result.get('error', 'Operation failed')}")
                return 1
                
        elif args.command == 'create':
            project_path = Path(args.project_path).absolute()
            project_name = project_path.name
            database_path = project_path / "memory-bank" / "context.db"
            
            result = manager.create_v21_database(str(database_path), project_name, str(project_path))
            if result['success']:
                print(f"✅ Created new v2.1 database for {project_name}")
                print(f"Database: {database_path}")
                print(f"Project UUID: {result.get('project_uuid', 'Unknown')}")
                return 0
            else:
                print(f"❌ {result.get('error', 'Database creation failed')}")
                return 1
                
        elif args.command == 'validate':
            result = manager.validate_v21_database(args.database_path)
            if result['valid']:
                print(f"✅ Database validation passed")
                print(f"Version: {result['version']} (expected: {result['expected_version']})")
                print(f"Tables: {result['total_tables']} (expected: ~{result['expected_tables']})")
                return 0
            else:
                print(f"❌ Database validation failed: {result['message']}")
                if result.get('missing_tables'):
                    print(f"Missing tables: {result['missing_tables']}")
                return 1
                
        elif args.command == 'integrate':
            results = integrate_with_memory_bank()
            if all(results.values()):
                print("✅ Integration complete!")
                return 0
            else:
                print("⚠️ Partial integration - some components may need manual setup")
                return 1
                
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
