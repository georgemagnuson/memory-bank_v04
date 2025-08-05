"""
Filename: test_registry_basic.py
Generated: 2025-08-02.1721
Purpose: Basic test of centralized context registry core functionality
        Tests the fundamental registry mechanics before full integration
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from registry_integration import (
    work_on_project,
    get_current_context,
    save_info,
    get_registry_status,
    debug_context_propagation,
    validate_registry_integration
)


def test_basic_registry():
    """
    Basic test of the registry system core functionality
    """
    print("🧪 **Testing Memory Bank v2.0 Registry Core**\n")
    
    # Test 1: Check initial state
    print("1️⃣ **Initial State Check**")
    print(debug_context_propagation())
    print("\n" + "="*60 + "\n")
    
    # Test 2: Work on project
    print("2️⃣ **Testing work_on_project()**")
    project_path = "/Users/georgemagnuson/Documents/GitHub/memory-bank_v04/server/memory_bank_mcp"
    try:
        result = work_on_project(project_path)
        print("work_on_project() result:")
        print(result)
    except Exception as e:
        print(f"❌ Error in work_on_project(): {e}")
        import traceback
        traceback.print_exc()
    print("\n" + "="*60 + "\n")
    
    # Test 3: Check context after work_on_project
    print("3️⃣ **Testing get_current_context() after work_on_project()**")
    try:
        context_result = get_current_context()
        print("get_current_context() result:")
        print(context_result)
    except Exception as e:
        print(f"❌ Error in get_current_context(): {e}")
        import traceback
        traceback.print_exc()
    print("\n" + "="*60 + "\n")
    
    # Test 4: Check registry status
    print("4️⃣ **Testing get_registry_status()**")
    try:
        registry_status = get_registry_status()
        print("get_registry_status() result:")
        print(registry_status)
    except Exception as e:
        print(f"❌ Error in get_registry_status(): {e}")
        import traceback
        traceback.print_exc()
    print("\n" + "="*60 + "\n")
    
    # Test 5: Validation check
    print("5️⃣ **Testing validate_registry_integration()**")
    try:
        validation = validate_registry_integration()
        print("Validation Results:")
        for key, value in validation.items():
            status = "✅" if value else "❌"
            print(f"  • {key}: {status} {value}")
    except Exception as e:
        print(f"❌ Error in validate_registry_integration(): {e}")
        import traceback
        traceback.print_exc()
    print("\n" + "="*60 + "\n")
    
    # Test 6: Debug propagation
    print("6️⃣ **Testing debug_context_propagation()**")
    try:
        debug_result = debug_context_propagation()
        print("debug_context_propagation() result:")
        print(debug_result)
    except Exception as e:
        print(f"❌ Error in debug_context_propagation(): {e}")
        import traceback
        traceback.print_exc()
    print("\n" + "="*60 + "\n")
    
    print("🎯 **Basic Registry Test Complete**")
    print("Check the results above to identify any issues with the registry system.")


if __name__ == "__main__":
    test_basic_registry()
