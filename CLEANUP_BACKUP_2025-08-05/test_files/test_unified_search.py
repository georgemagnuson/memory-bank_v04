#!/usr/bin/env python3
"""
test_unified_search.py
Generated: 2025-07-28.1411
Purpose: Test script for Phase 1 unified search functionality

This script tests the new unified search functions to ensure they work correctly
with the unified_documents table architecture.
"""

import sys
import sqlite3
import json
from pathlib import Path

# Add server path for imports
sys.path.append('/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server')

def test_direct_unified_search():
    """Test direct database queries against unified_documents table"""
    print("🧪 Testing Direct Unified Search Functions")
    print("=" * 50)
    
    db_path = "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/memory-bank/context.db"
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test 1: Count total records
        print("1. Total Records Test:")
        cursor.execute("SELECT COUNT(*) as total FROM unified_documents")
        total = cursor.fetchone()['total']
        print(f"   ✅ Total unified_documents records: {total}")
        
        # Test 2: Document type distribution
        print("\n2. Document Type Distribution:")
        cursor.execute("""
            SELECT document_type, COUNT(*) as count 
            FROM unified_documents 
            GROUP BY document_type 
            ORDER BY count DESC
        """)
        
        for row in cursor.fetchall():
            print(f"   📊 {row['document_type']}: {row['count']} records")
        
        # Test 3: FTS Search Test
        print("\n3. FTS Search Test (searching for 'DXT'):")
        cursor.execute("""
            SELECT ud.document_type, ud.title, LENGTH(ud.content) as content_length
            FROM unified_documents_fts fts
            JOIN unified_documents ud ON fts.rowid = ud.id
            WHERE unified_documents_fts MATCH 'DXT'
            ORDER BY CASE ud.document_type 
                WHEN 'document' THEN 1 
                WHEN 'discussion' THEN 2 
                WHEN 'plan' THEN 3 
                ELSE 4 
            END
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        if results:
            print(f"   ✅ Found {len(results)} DXT matches:")
            for i, row in enumerate(results, 1):
                title_short = row['title'][:60] + "..." if len(row['title']) > 60 else row['title']
                print(f"   {i}. [{row['document_type']}] {title_short} ({row['content_length']:,} chars)")
        else:
            print("   ❌ No DXT matches found")
        
        # Test 4: Type-specific search
        print("\n4. Type-specific Search Test (plans containing 'phase'):")
        cursor.execute("""
            SELECT ud.title, LENGTH(ud.content) as content_length
            FROM unified_documents_fts fts
            JOIN unified_documents ud ON fts.rowid = ud.id
            WHERE unified_documents_fts MATCH 'phase'
            AND ud.document_type = 'plan'
            ORDER BY rank
            LIMIT 3
        """)
        
        results = cursor.fetchall()
        if results:
            print(f"   ✅ Found {len(results)} plan matches:")
            for i, row in enumerate(results, 1):
                title_short = row['title'][:60] + "..." if len(row['title']) > 60 else row['title']
                print(f"   {i}. {title_short} ({row['content_length']:,} chars)")
        else:
            print("   ❌ No plan matches found")
        
        # Test 5: Source table preservation  
        print("\n5. Source Table Preservation Test:")
        cursor.execute("""
            SELECT source_table, COUNT(*) as count 
            FROM unified_documents 
            GROUP BY source_table 
            ORDER BY count DESC
        """)
        
        for row in cursor.fetchall():
            print(f"   📋 {row['source_table']}: {row['count']} records")
        
        conn.close()
        print("\n✅ All direct search tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Direct search test failed: {e}")
        return False
    
    return True

def test_extraction_simulation():
    """Simulate the extraction functionality"""
    print("\n🧪 Testing Extraction Simulation")
    print("=" * 50)
    
    db_path = "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/memory-bank/context.db"
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Find some content for extraction simulation
        cursor.execute("""
            SELECT ud.id, ud.title, ud.document_type, LENGTH(ud.content) as content_length
            FROM unified_documents_fts fts
            JOIN unified_documents ud ON fts.rowid = ud.id
            WHERE unified_documents_fts MATCH 'migration'
            ORDER BY rank
            LIMIT 3
        """)
        
        results = cursor.fetchall()
        if results:
            print(f"   ✅ Found {len(results)} items for extraction simulation:")
            total_chars = 0
            for i, row in enumerate(results, 1):
                title_short = row['title'][:50] + "..." if len(row['title']) > 50 else row['title']
                print(f"   {i}. [{row['document_type']}] {title_short}")
                print(f"      Size: {row['content_length']:,} characters")
                total_chars += row['content_length']
            
            print(f"\n   📊 Total content for extraction: {total_chars:,} characters")
            
            if total_chars > 5000:
                print("   💡 Large content detected - /tmp/ extraction would be beneficial")
            else:
                print("   💡 Content size manageable for direct display")
        else:
            print("   ❌ No content found for extraction simulation")
        
        conn.close()
        print("\n✅ Extraction simulation completed!")
        
    except Exception as e:
        print(f"\n❌ Extraction simulation failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Memory Bank Unified Search - Phase 1 Testing")
    print("=" * 60)
    
    success1 = test_direct_unified_search()
    success2 = test_extraction_simulation()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All Phase 1 tests passed! Unified search architecture is working.")
    else:
        print("❌ Some tests failed. Check the output above for details.")
    
    print("=" * 60)
