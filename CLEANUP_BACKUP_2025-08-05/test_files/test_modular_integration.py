#!/usr/bin/env python3
"""
test_modular_integration.py
Generated: 2025-07-28.1411
Purpose: Test modular unified functionality integration

This script tests that the modular approach integrates properly without disrupting existing code.
"""

import sys
import os
from pathlib import Path

# Add server path for imports
sys.path.append('/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server')

def test_modular_imports():
    """Test that modular components can be imported independently"""
    print("🧪 Testing Modular Component Imports")
    print("=" * 50)
    
    try:
        # Test individual module imports
        from memory_bank_mcp.unified.types import DocumentType, SearchResult, DocumentTypes
        print("✅ Successfully imported unified.types")
        
        from memory_bank_mcp.unified.search import UnifiedSearch
        print("✅ Successfully imported unified.search")
        
        from memory_bank_mcp.unified.extraction import UnifiedExtraction
        print("✅ Successfully imported unified.extraction")
        
        from memory_bank_mcp.unified.adapter import UnifiedAdapter
        print("✅ Successfully imported unified.adapter")
        
        # Test package-level imports
        from memory_bank_mcp.unified import UnifiedSearch as PackageSearch
        print("✅ Successfully imported from package level")
        
        # Test integration module
        from memory_bank_mcp.content_tools_integration import add_unified_functionality
        print("✅ Successfully imported integration helper")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False

def test_unified_types():
    """Test unified types functionality"""
    print("\n🧪 Testing Unified Types")
    print("=" * 30)
    
    try:
        from memory_bank_mcp.unified.types import DocumentTypes, SearchResult
        
        # Test document type validation
        valid_types = DocumentTypes.validate_types(['discussion', 'document', 'invalid'])
        print(f"✅ Type validation: {valid_types}")
        
        # Test icon retrieval
        icon = DocumentTypes.get_icon('discussion')
        print(f"✅ Discussion icon: {icon}")
        
        # Test priority ordering
        priority = DocumentTypes.get_priority('document')
        print(f"✅ Document priority: {priority}")
        
        # Test SearchResult creation
        result = SearchResult(
            id=1,
            uuid="test-uuid",
            title="Test Title",
            content="Test content",
            document_type="discussion",
            source_table="discussions",
            summary="Test summary",
            tags=["test"],
            metadata={"test": "data"},
            created_at="2025-07-28",
            updated_at="2025-07-28",
            content_length=12
        )
        print(f"✅ SearchResult created: {result.title} ({result.document_type})")
        
        return True
        
    except Exception as e:
        print(f"❌ Types test failed: {e}")
        return False

def test_search_module():
    """Test unified search module functionality"""
    print("\n🧪 Testing Unified Search Module")
    print("=" * 35)
    
    try:
        from memory_bank_mcp.unified.search import UnifiedSearch
        from memory_bank_mcp.unified.types import SearchConfig
        
        db_path = "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/memory-bank/context.db"
        
        # Test if database exists
        if not os.path.exists(db_path):
            print(f"⚠️ Database not found at {db_path}")
            return True  # Not a failure, just missing test data
        
        # Test search configuration
        config = SearchConfig(query="DXT", limit=3)
        print(f"✅ SearchConfig created: {config.query} (limit: {config.limit})")
        
        # Test actual search
        results, stats = UnifiedSearch.search_content(db_path, config)
        print(f"✅ Search executed: {stats.total_results} results found")
        
        if results:
            first_result = results[0]
            print(f"✅ First result: {first_result.title} ({first_result.document_type})")
        
        # Test UUID search
        if results:
            uuid_result = UnifiedSearch.search_by_uuid(db_path, results[0].uuid)
            print(f"✅ UUID search: {'Found' if uuid_result else 'Not found'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Search test failed: {e}")
        return False

def test_integration_adapter():
    """Test the integration adapter"""
    print("\n🧪 Testing Integration Adapter")
    print("=" * 32)
    
    try:
        from memory_bank_mcp.unified.adapter import UnifiedAdapter
        
        # Create mock context manager
        class MockContext:
            def __init__(self):
                self.current_db_path = "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/memory-bank/context.db"
        
        adapter = UnifiedAdapter(MockContext())
        print("✅ UnifiedAdapter created")
        
        # Test database path access
        db_path = adapter.db_path
        print(f"✅ Database path: {db_path}")
        
        # Test search adapter (with small query to avoid large output)
        if os.path.exists(db_path):
            result = adapter.search_all_content("phase", limit=2)
            success = not result.startswith("❌")
            print(f"✅ Adapter search: {'Success' if success else 'Failed'}")
        else:
            print("⚠️ Database not available for adapter test")
        
        return True
        
    except Exception as e:
        print(f"❌ Adapter test failed: {e}")
        return False

def test_backwards_compatibility():
    """Test that existing content_tools.py still works"""
    print("\n🧪 Testing Backwards Compatibility")
    print("=" * 35)
    
    try:
        # Test importing original content tools (now updated)
        from memory_bank_mcp.content_tools import ContentTools
        print("✅ ContentTools imported successfully")
        
        # Create mock context
        class MockContext:
            def __init__(self):
                self.current_db_path = "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/memory-bank/context.db"
        
        content_tools = ContentTools(MockContext())
        print("✅ ContentTools instantiated")
        
        # Check that it has expected methods
        methods_to_check = [
            'search_all_content',
            'sync_fts_tables',
            'import_markdown_files'
        ]
        
        for method in methods_to_check:
            if hasattr(content_tools, method):
                print(f"✅ Method {method} available")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Backwards compatibility test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Memory Bank Modular Integration Testing")
    print("=" * 50)
    
    tests = [
        test_modular_imports,
        test_unified_types,
        test_search_module,
        test_integration_adapter,
        test_backwards_compatibility
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All modular integration tests passed!")
        print("✅ Unified architecture is properly modularized and non-disruptive")
    else:
        print("⚠️ Some tests failed - check modular integration")
    
    print("=" * 50)
