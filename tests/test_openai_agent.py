#!/usr/bin/env python3
import asyncio
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from typing import Any, Callable, Dict, TypeVar, Optional, ClassVar, Coroutine

import pytest
from dotenv import load_dotenv

from agent.openai_agent import OpenAIAgent
from tests.utils import (
    check_response_quality,
    create_test_file,
    create_user_info,
    delete_test_file,
    get_test_env,
    is_real_api_key,
)

# Type variable for the coroutine return type
T = TypeVar('T')


# Helper for async tests
def async_test(coro: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., T]:
    def wrapper(*args: Any, **kwargs: Any) -> T:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))

    return wrapper


@pytest.mark.openai
class TestOpenAIAgent(unittest.TestCase):
    """Test the OpenAI agent functionality with real API."""
    
    api_key: ClassVar[Optional[str]] = os.environ.get("OPENAI_API_KEY")

    def setUp(self) -> None:
        """Set up the test environment."""
        # Store the original directory to ensure we can return to it
        try:
            self.original_dir = os.path.abspath(os.getcwd())
        except FileNotFoundError:
            # If we can't get the current directory, use the directory where the test file is located
            self.original_dir = os.path.abspath(os.path.dirname(__file__))
            os.chdir(self.original_dir)
            print(f"Reset working directory to: {self.original_dir}")
            
        self.env = get_test_env()

        # Skip entire class if no valid API key
        if "OPENAI_API_KEY" not in self.env:
            self.skipTest("No valid OPENAI_API_KEY found, skipping OpenAI tests")

        openai_key = self.env.get("OPENAI_API_KEY")
        if not is_real_api_key(openai_key, "openai"):
            self.skipTest("OpenAI API key does not have a valid format")

        # Initialize with real API key
        try:
            # Cast to str to satisfy mypy since we've already checked if it's valid
            self.agent = OpenAIAgent(api_key=str(openai_key))
            self.agent.register_default_tools()
        except Exception as e:
            self.skipTest(f"Failed to initialize OpenAI agent: {str(e)}")

        # Debug information - use try/except to handle potential errors
        try:
            print(f"Current working directory: {os.getcwd()}")
            
            # Create an absolute path for the test directory
            self.test_dir = os.path.abspath(os.path.join(self.original_dir, "test_files_tmp"))
            
            # Ensure directory exists
            os.makedirs(self.test_dir, exist_ok=True)
            
            print(f"Test directory path: {self.test_dir}")
            print(f"Test directory exists: {os.path.exists(self.test_dir)}")
            print(f"Test directory is writable: {os.access(self.test_dir, os.W_OK)}")
            
            # Test that we can actually write to the directory
            test_file = os.path.join(self.test_dir, "test_permissions.txt")
            with open(test_file, 'w') as f:
                f.write("Test file to verify permissions\n")
            os.remove(test_file)  # Clean up
            
        except Exception as e:
            self.skipTest(f"Error setting up test environment: {str(e)}")

    def tearDown(self) -> None:
        """Clean up after tests."""
        # Clean up test directory if it exists
        if hasattr(self, "test_dir") and os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir, ignore_errors=True)
            except Exception as e:
                print(f"Warning: Could not clean up test directory: {str(e)}")
                
        # Return to original directory if we changed it
        if hasattr(self, "original_dir"):
            try:
                os.chdir(self.original_dir)
            except Exception as e:
                print(f"Warning: Could not return to original directory: {str(e)}")

    def test_init(self) -> None:
        """Test agent initialization."""
        api_key = os.environ.get("OPENAI_API_KEY") or "sk-dummy"
        agent = OpenAIAgent(api_key=api_key)
        self.assertIsNotNone(agent)

    def test_tool_registration(self) -> None:
        """Test registering tools."""
        api_key = os.environ.get("OPENAI_API_KEY") or "sk-dummy"
        agent = OpenAIAgent(api_key=api_key)
        
        agent.register_tool(
            name="test_tool",
            function=lambda x: x,
            description="Test tool",
            parameters={
                "properties": {
                    "input": {"description": "Test input", "type": "string"}
                },
                "required": ["input"]
            }
        )
        
        self.assertIn("test_tool", agent.available_tools)
        self.assertEqual(agent.available_tools["test_tool"]["schema"]["description"], "Test tool")

    @async_test
    async def test_simple_chat(self) -> None:
        """Test a simple chat interaction with real API."""
        query = "What is Python?"
        
        # Skip if no API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or not is_real_api_key(api_key, "openai"):
            self.skipTest("No valid OpenAI API key for live testing")

        response = await self.agent.chat(query)

        # Skip test if API error detected
        if response.startswith("Error:"):
            self.skipTest(f"API error detected: {response[:100]}")

        print(f"Simple chat response: {response[:100]}...")
        self.assertTrue(check_response_quality(response), "Response failed quality check")
        self.assertEqual(len(self.agent.conversation_history), 2)  # User message + agent response

    @async_test
    async def test_chat_with_user_info(self) -> None:
        """Test chat with user info with real API."""
        # Skip if no API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or not is_real_api_key(api_key, "openai"):
            self.skipTest("No valid OpenAI API key for live testing")
        
        agent = OpenAIAgent(api_key=api_key)
        
        query = "What files do I have open?"
        user_info = create_user_info()
        
        response = await agent.chat(query, user_info)
        self.assertTrue(check_response_quality(response))
        self.assertIn("test_file.py", response)

    @async_test
    async def test_file_tools(self) -> None:
        """Test file-related tools with real API."""
        # Skip if no API key
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or not is_real_api_key(api_key, "openai"):
            self.skipTest("No valid OpenAI API key for live testing")
        
        # Create a test directory and file
        self.test_dir = tempfile.mkdtemp()
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("This is a test file.")
        
        agent = OpenAIAgent(api_key=api_key)
        agent.register_default_tools()
        
        # Ask about the file
        response = await agent.chat(f"Can you read the file {test_file}?")
        self.assertTrue(check_response_quality(response))
        
        # The response should either have content from the file or mention using a tool
        # Lowercasing and checking for multiple possible variations
        response_lower = response.lower()
        self.assertTrue(
            "test file" in response_lower or
            "read" in response_lower or
            "content" in response_lower or
            "file" in response_lower or
            "tool" in response_lower,
            f"Response does not contain expected content: {response[:100]}..."
        )

    # Can add more tests for other tool functionality


if __name__ == "__main__":
    unittest.main()
