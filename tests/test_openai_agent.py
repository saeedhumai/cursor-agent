import os
import asyncio
import unittest
import tempfile
import shutil
from typing import Dict, Any

from agent.openai_agent import OpenAIAgent
from tests.utils import get_test_env, create_test_file, delete_test_file, create_user_info, check_response_quality, is_real_api_key

# Helper for async tests
def async_test(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(coro(*args, **kwargs))
    return wrapper

class TestOpenAIAgent(unittest.TestCase):
    """Test the OpenAI agent functionality with real API."""
    
    def setUp(self):
        """Set up the test environment."""
        self.env = get_test_env()
        
        # Skip entire class if no valid API key
        if "OPENAI_API_KEY" not in self.env:
            self.skipTest("No valid OPENAI_API_KEY found, skipping OpenAI tests")
        
        openai_key = self.env.get("OPENAI_API_KEY")
        if not is_real_api_key(openai_key, "openai"):
            self.skipTest("OpenAI API key does not have a valid format")
        
        # Initialize with real API key
        try:
            self.agent = OpenAIAgent(api_key=openai_key)
            self.agent.register_default_tools()
        except Exception as e:
            self.skipTest(f"Failed to initialize OpenAI agent: {str(e)}")
        
        # Create a temp directory for test files
        # Use a temp directory in the workspace instead of the system temp directory
        self.test_dir = os.path.join(os.getcwd(), "test_files_tmp")
        os.makedirs(self.test_dir, exist_ok=True)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temp directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_init(self):
        """Test agent initialization."""
        self.assertIsNotNone(self.agent)
        self.assertIsNotNone(self.agent.client)
        self.assertIsNotNone(self.agent.system_prompt)
        self.assertEqual(len(self.agent.conversation_history), 0)
    
    def test_tool_registration(self):
        """Test tool registration."""
        # Check that default tools are registered
        self.assertGreater(len(self.agent.available_tools), 0)
        
        # Check for specific tools
        self.assertIn("read_file", self.agent.available_tools)
        self.assertIn("edit_file", self.agent.available_tools)
        self.assertIn("codebase_search", self.agent.available_tools)
    
    @async_test
    async def test_simple_chat(self):
        """Test a simple chat interaction with real API."""
        query = "What is Python?"
        response = await self.agent.chat(query)
        
        # Skip test if API error detected
        if response.startswith("Error:"):
            self.skipTest(f"API error detected: {response[:100]}")
            
        print(f"Simple chat response: {response[:100]}...")
        self.assertTrue(check_response_quality(response), "Response failed quality check")
        self.assertEqual(len(self.agent.conversation_history), 2)  # User message + agent response
    
    @async_test
    async def test_chat_with_user_info(self):
        """Test chat with user info with real API."""
        query = "What files do I have open?"
        user_info = create_user_info()
        
        response = await self.agent.chat(query, user_info)
        
        # Skip test if API error detected
        if response.startswith("Error:"):
            self.skipTest(f"API error detected: {response[:100]}")
            
        print(f"User info chat response: {response[:100]}...")
        self.assertTrue(check_response_quality(response), "Response failed quality check")
        self.assertIn("test_file.py", response)
    
    @async_test
    async def test_file_tools(self):
        """Test file-related tools with real API."""
        # Create a test file
        test_file_path = os.path.join(self.test_dir, "test_file.py")
        create_test_file(test_file_path, "def test_function():\n    return 'Hello, World!'")
        
        # Test reading the file
        query = f"What's in the file {test_file_path}?"
        response = await self.agent.chat(query)
        
        # Skip test if API error detected
        if response.startswith("Error:"):
            self.skipTest(f"API error detected: {response[:100]}")
            
        print(f"File tools response: {response[:100]}...")
        self.assertTrue(check_response_quality(response), "Response failed quality check")
        self.assertIn("test_function", response)
    
    # Can add more tests for other tool functionality

if __name__ == "__main__":
    unittest.main() 