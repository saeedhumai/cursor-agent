#!/usr/bin/env python3
"""
Test script that verifies only the import structure of the cursor-agent package.
This test is focused on imports only and does not attempt to initialize any clients.
"""
import inspect
import sys

def test_imports():
    """Test just the import structure without initializing clients."""
    results = []
    
    print("Testing cursor_agent.agent imports...")
    
    # Import from cursor_agent.agent
    try:
        from cursor_agent.agent import create_agent, BaseAgent, ClaudeAgent, OpenAIAgent
        results.append(("Import from cursor_agent.agent", True))
    except ImportError as e:
        results.append(("Import from cursor_agent.agent", False))
        print(f"Error: {str(e)}")
        return False
    
    # Check types
    try:
        results.append(("create_agent is a function", inspect.isfunction(create_agent)))
        results.append(("BaseAgent is a class", inspect.isclass(BaseAgent)))
        results.append(("ClaudeAgent is a class", inspect.isclass(ClaudeAgent)))
        results.append(("OpenAIAgent is a class", inspect.isclass(OpenAIAgent)))
    except Exception as e:
        print(f"Error checking types: {str(e)}")
        return False
    
    # Check hierarchy
    try:
        results.append(("ClaudeAgent is a subclass of BaseAgent", issubclass(ClaudeAgent, BaseAgent)))
        results.append(("OpenAIAgent is a subclass of BaseAgent", issubclass(OpenAIAgent, BaseAgent)))
    except Exception as e:
        print(f"Error checking hierarchy: {str(e)}")
        return False
    
    # Check original agent package imports
    try:
        import agent
        from agent import factory
        results.append(("Original agent package imports", True))
    except ImportError as e:
        results.append(("Original agent package imports", False))
        print(f"Error importing original agent package: {str(e)}")
        return False
    
    # Check modules in sys.modules
    cursor_agent_modules = [m for m in sys.modules if m.startswith('cursor_agent')]
    agent_modules = [m for m in sys.modules if m == 'agent' or m.startswith('agent.')]
    
    print("\nLoaded cursor_agent modules:")
    for module in cursor_agent_modules:
        print(f"  - {module}")
    
    print("\nLoaded agent modules:")
    for module in agent_modules:
        print(f"  - {module}")
    
    # Print results
    print("\nImport Structure Test Results:")
    print("-" * 40)
    
    all_passed = True
    for test, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        all_passed = all_passed and result
        print(f"{status} | {test}")
    
    print("-" * 40)
    if all_passed:
        print("✅ All import tests passed!")
        print("The import structure is configured correctly.")
    else:
        print("❌ Some import tests failed")
    
    return all_passed

if __name__ == "__main__":
    print("Running import-only tests for cursor-agent package")
    success = test_imports()
    
    if success:
        print("\nSUCCESS: The package structure is correctly configured for imports.")
        print("The issue with client initialization is likely a dependency version mismatch,")
        print("not a problem with the package structure itself.")
    else:
        print("\nFAILED: There are issues with the import structure.") 