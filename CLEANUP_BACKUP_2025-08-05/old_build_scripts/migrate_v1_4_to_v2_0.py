#!/usr/bin/env python3
"""
migrate_v1_4_to_v2_0.py
Generated: 2025-07-30.1331
Purpose: Standalone migration script for Memory Bank v1.4.0 to v2.0
Migrates unified_documents table to documents table with cross-project support
- Removes 'original_' prefixes (original_uuid -> uuid)
- Includes project_uuid for three-project ecosystem cross-references
- Full backup and verification with proper error handling
"""

import sys
import logging
from pathlib import Path
from datetime import datetime, timezone

# Add server directory to path
sys.path.insert(0, str(Path(__file__).parent / "server" / "memory_bank_mcp"))

from migration_modules.database_migrator import DatabaseMigrator

def setup_logging():
    """Configure logging for migration process"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(f'migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )

def main():
    """Main migration function"""
    print("🔄 **MEMORY BANK v1.4.0 → v2.0 MIGRATION**")
    print("=" * 50)
    
    # Target database path
    db_path = Path("/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp/memory-bank/context.db")
    
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        return 1
    
    print(f"📁 **Target Database:** {db_path}")
    print(f"⏰ **Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize migrator
    migrator = DatabaseMigrator(db_path)
    
    # Step 1: Dry run analysis
    print(f"\n🔍 **STEP 1: DRY RUN ANALYSIS**")
    print("-" * 30)
    
    dry_run_report = migrator.migrate_to_v2_0(dry_run=True)
    migrator.print_migration_report(dry_run_report)
    
    if dry_run_report['status'] == 'failed':
        print(f"\n❌ Dry run failed. Aborting migration.")
        return 1
    
    if not dry_run_report.get('migration_needed', False):
        print(f"\n⏭️  No migration needed. Database may already be v2.0 or incompatible.")
        return 0
    
    # Step 2: Confirmation
    print(f"\n❓ **PROCEED WITH MIGRATION?**")
    print(f"• This will create a backup and migrate {dry_run_report.get('unified_documents_count', 0)} documents")
    print(f"• Migration strategy: {dry_run_report.get('migration_strategy', 'unknown')}")
    
    confirm = input("\nProceed with migration? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Migration cancelled by user.")
        return 1
    
    # Step 3: Full migration
    print(f"\n🚀 **STEP 2: FULL MIGRATION**")
    print("-" * 30)
    
    migration_report = migrator.migrate_to_v2_0(dry_run=False)
    migrator.print_migration_report(migration_report)
    
    if migration_report['status'] == 'completed':
        print(f"\n✅ **MIGRATION COMPLETED SUCCESSFULLY!**")
        print(f"📊 Records migrated: {migration_report.get('records_migrated', 0)}")
        if migration_report.get('backup_created'):
            print(f"💾 Backup created: {migration_report.get('backup_path', 'Unknown')}")
        return 0
    else:
        print(f"\n❌ **MIGRATION FAILED**")
        if migration_report.get('errors'):
            for error in migration_report['errors']:
                print(f"  • {error}")
        return 1

if __name__ == "__main__":
    setup_logging()
    sys.exit(main())
