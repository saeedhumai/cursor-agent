#!/usr/bin/env python3
"""
Test script that verifies the module structure of the cursor-agent package.
This tests the package structure in detail without making actual API calls.
"""
import inspect
import os
from cursor_agent.agent import create_agent, BaseAgent, ClaudeAgent, OpenAIAgent

def test_module_structure():
    """Test the module structure and imports in detail."""
    results = []
    
    # Check that create_agent is a function
    is_function = inspect.isfunction(create_agent)
    results.append(("create_agent is a function", is_function))
    
    # Check that BaseAgent is a class
    is_class = inspect.isclass(BaseAgent)
    results.append(("BaseAgent is a class", is_class))
    
    # Check that ClaudeAgent is a subclass of BaseAgent
    is_subclass = issubclass(ClaudeAgent, BaseAgent)
    results.append(("ClaudeAgent is a subclass of BaseAgent", is_subclass))
    
    # Check that OpenAIAgent is a subclass of BaseAgent
    is_subclass = issubclass(OpenAIAgent, BaseAgent)
    results.append(("OpenAIAgent is a subclass of BaseAgent", is_subclass))
    
    # Check that the create_agent function has the expected parameters
    signature = inspect.signature(create_agent)
    has_model_param = 'model' in signature.parameters
    results.append(("create_agent has 'model' parameter", has_model_param))
    
    # Print results
    print("\nModule Structure Test Results:")
    print("-" * 40)
    
    all_passed = True
    for test, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        all_passed = all_passed and result
        print(f"{status} | {test}")
    
    print("-" * 40)
    if all_passed:
        print("✅ All module structure tests passed!")
    else:
        print("❌ Some module structure tests failed")
    
    return all_passed

def test_readme_example_structure():
    """Test that the structure in the README.md examples is valid."""
    print("\nVerifying README.md examples structure:")
    print("-" * 40)
    
    # Test Quick Start example structure
    try:
        # This code is from the README.md Quick Start example
        # We're just checking that the structure/imports work
        def example():
            agent = create_agent(model='claude-3-5-sonnet-latest')
            return agent
            
        # Create the agent instance without making API calls
        agent_type = type(example()).__name__
        print(f"✅ PASS | Successfully created agent instance of type: {agent_type}")
        print("✅ PASS | README.md Quick Start example structure is valid")
    except Exception as e:
        print(f"❌ FAIL | README.md Quick Start example structure failed: {str(e)}")
        return False
    
    print("-" * 40)
    return True

if __name__ == "__main__":
    print("Running module structure tests for cursor-agent package")
    
    # Test the module structure
    structure_passed = test_module_structure()
    
    # Test README example structure
    example_passed = test_readme_example_structure()
    
    # Overall result
    if structure_passed and example_passed:
        print("\n✅ All tests passed! The package structure is correct.")
    else:
        print("\n❌ Some tests failed. Please review the issues above.") 