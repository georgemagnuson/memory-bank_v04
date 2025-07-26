#!/usr/bin/env python3
"""
test_documents_v2_search.py
Generated: 2025-07-21.1803
Purpose: Test the documents_v2 search functionality
"""

import asyncio
import sys
from pathlib import Path

# Add the memory_bank_mcp to the path
sys.path.insert(0, str(Path(__file__).parent))

from memory_bank_mcp.database import MemoryBankDatabase

async def test_search():
    """Test the documents_v2 search functionality"""
    
    # Initialize database
    project_path = Path("/Users/georgemagnuson/Documents/GitHub/memory-bank_v04")
    db = MemoryBankDatabase(project_path)
    
    success = await db.initialize()
    if not success:
        print("❌ Failed to initialize database")
        return
    
    print(f"✅ Database initialized")
    print(f"Project UUID: {db.project_uuid}")
    
    # Test the full_text_search method directly
    try:
        results = await db.full_text_search(
            query="Phase",
            content_types=['document_v2'],
            limit=5,
            highlight=True
        )
        
        print(f"📊 Found {len(results)} document_v2 results:")
        for result in results:
            print(f"- {result.get('title', 'No title')} ({result.get('document_type', 'unknown')})")
            print(f"  UUID: {result.get('uuid', 'unknown')[:8]}...")
            print(f"  Content type: {result.get('content_type', 'unknown')}")
            print()
            
    except Exception as e:
        print(f"❌ Search error: {e}")
        import traceback
        traceback.print_exc()
    
    await db.close()

if __name__ == "__main__":
    asyncio.run(test_search())
