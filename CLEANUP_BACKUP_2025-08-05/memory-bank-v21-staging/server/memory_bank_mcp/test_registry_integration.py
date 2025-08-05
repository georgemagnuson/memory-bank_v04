"""
Filename: test_registry_integration.py
Generated: 2025-08-02.1721
Purpose: Test script to verify centralized context registry integration
        Tests the complete flow from work_on_project through all tool operations
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from registry_integration import (
    work_on_project,
    get_current_context,
    save_info,
    search_info,
    save_document,
    search_documents,
    get_registry_status,
    debug_context_propagation,
    validate_registry_integration
)


def test_registry_integration():
    """
    Complete test of the registry integration system
    """
    print("🧪 **Testing Memory Bank v2.0 Registry Integration**\n")
    
    # Test 1: Check initial state
    print("1️⃣ **Initial State Check**")
    print(debug_context_propagation())
    print("\n" + "="*60 + "\n")
    
    # Test 2: Work on project
    print("2️⃣ **Testing work_on_project()**")
    project_path = "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp"
    result = work_on_project(project_path)
    print(result)
    print("\n" + "="*60 + "\n")
    
    # Test 3: Check context after work_on_project
    print("3️⃣ **Testing get_current_context() after work_on_project()**")
    context_result = get_current_context()
    print(context_result)
    print("\n" + "="*60 + "\n")
    
    # Test 4: Check registry status
    print("4️⃣ **Testing get_registry_status()**")
    registry_status = get_registry_status()
    print(registry_status)
    print("\n" + "="*60 + "\n")
    
    # Test 5: Validation check
    print("5️⃣ **Testing validate_registry_integration()**")
    validation = validate_registry_integration()
    print("Validation Results:")
    for key, value in validation.items():
        status = "✅" if value else "❌"
        print(f"  • {key}: {status} {value}")
    print("\n" + "="*60 + "\n")
    
    # Test 6: Debug propagation
    print("6️⃣ **Testing debug_context_propagation()**")
    debug_result = debug_context_propagation()
    print(debug_result)
    print("\n" + "="*60 + "\n")
    
    # Test 7: Content operations
    print("7️⃣ **Testing Content Operations**")
    
    # Test save_info
    print("Testing save_info()...")
    save_result = save_info("This is test content for registry integration", "test", "registry,integration,test")
    print(save_result)
    print()
    
    # Test search_info
    print("Testing search_info()...")
    search_result = search_info("test content")
    print(search_result)
    print()
    
    # Test save_document
    print("Testing save_document()...")
    doc_result = save_document("Test Document", "This is a test document for registry integration", "test", "registry,test")
    print(doc_result)
    print()
    
    # Test search_documents
    print("Testing search_documents()...")
    doc_search_result = search_documents("test document")
    print(doc_search_result)
    print("\n" + "="*60 + "\n")
    
    print("🎯 **Registry Integration Test Complete**")
    print("Check the results above to verify that context propagation is working correctly.")


if __name__ == "__main__":
    test_registry_integration()
