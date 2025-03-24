import asyncio
import os
import shutil
import tempfile
import unittest
import pytest
from typing import Any, Callable, Dict, Optional, ClassVar, Coroutine, TypeVar

from agent.claude_agent import ClaudeAgent
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


@pytest.mark.anthropic
class TestClaudeAgent(unittest.TestCase):
    """Test the Claude agent functionality with real API."""

    api_key: ClassVar[Optional[str]] = os.environ.get("ANTHROPIC_API_KEY")

    @classmethod
    def setup_class(cls) -> None:
        """Set up for the test class."""
        cls.api_key = os.environ.get("ANTHROPIC_API_KEY")

    @classmethod
    def teardown_class(cls) -> None:
        """Tear down for the test class."""
        # Nothing to do here for now
        pass

    def setUp(self) -> None:
        """Set up the test environment."""
        # Set up a temporary directory
        self.test_dir = tempfile.mkdtemp()
        os.chdir(self.test_dir)
        
        # Initialize agent
        self.agent_api_key = os.environ.get("ANTHROPIC_API_KEY") or "sk-ant-dummy"
        self.agent = ClaudeAgent(api_key=self.agent_api_key)
        
        # Set up test files
        self.test_file_path = os.path.join(self.test_dir, "test_file.txt")
        create_test_file(self.test_file_path, "This is a test file.")

    def tearDown(self) -> None:
        """Clean up after tests."""
        # Clean up test directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @unittest.skipIf(not api_key, "Anthropic API key not available")
    def test_init(self) -> None:
        """Test agent initialization."""
        self.assertIsNotNone(self.agent)
        self.assertEqual(self.agent.api_key, self.agent_api_key)
        # Just verify it's a Claude model without checking exact version
        self.assertIsNotNone(self.agent.model)
        self.assertTrue('claude' in str(self.agent.model).lower())

    def test_tool_registration(self) -> None:
        """Test registering tools."""
        self.agent.register_tool(
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
        
        self.assertIn("test_tool", self.agent.available_tools)
        self.assertEqual(self.agent.available_tools["test_tool"]["schema"]["description"], "Test tool")

    @pytest.mark.asyncio
    async def test_chat(self) -> None:
        """Test the chat method returns a proper response"""
        response = await self.agent.chat("What is the capital of France?")
        
        # Check if it's the new structured response
        if isinstance(response, dict):
            assert "message" in response
            assert isinstance(response["message"], str)
            assert "tool_calls" in response
            assert "thinking" in response
            
            # Check response content
            assert "Paris" in response["message"]
        else:
            # For backward compatibility with string responses
            assert isinstance(response, str)
            assert "Paris" in response

    @async_test
    @unittest.skipIf(not api_key, "Anthropic API key not available")
    async def test_chat_with_user_info(self) -> None:
        """Test chat with user info with real API."""
        if not self.agent_api_key or not is_real_api_key(self.agent_api_key, "anthropic"):
            self.skipTest("No valid Anthropic API key for live testing")
            
        test_message = "What files do I have open?"
        user_info = {
            "open_files": ["test.py", "main.py"],
            "cursor_position": {"file": "test.py", "line": 10},
            "workspace_path": "/tmp/test"
        }
        
        response = await self.agent.chat(test_message, user_info)
        
        # Check if it's the new structured response
        if isinstance(response, dict):
            self.assertIn("message", response)
            self.assertIn("tool_calls", response)
            self.assertTrue(
                "test.py" in response["message"] or 
                "main.py" in response["message"]
            )
        else:
            # For backward compatibility
            self.assertIsInstance(response, str)
            self.assertTrue("test.py" in response or "main.py" in response)

    @async_test
    @unittest.skipIf(not api_key, "Anthropic API key not available")
    async def test_file_tools(self) -> None:
        """Test file tools with the agent."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
            tmp.write(b"This is a test file content.")
            self.test_file_path = tmp.name
        
        # Register tools
        from agent.tools.file_tools import read_file, list_directory
        self.agent.register_tool(
            name="read_file", 
            function=read_file, 
            description="Read a file", 
            parameters={
                "properties": {
                    "path": {"type": "string", "description": "Path to the file"}
                },
                "required": ["path"]
            }
        )
        self.agent.register_tool(
            name="list_dir", 
            function=list_directory, 
            description="List directory contents", 
            parameters={
                "properties": {
                    "path": {"type": "string", "description": "Path to the directory"}
                },
                "required": ["path"]
            }
        )
        
        # Test file-related query
        response = await self.agent.chat(f"Read the file at {self.test_file_path}")
        
        # Handle structured response
        if isinstance(response, dict):
            # Test if it's a valid AgentResponse
            self.assertIn("message", response)
            self.assertIn("tool_calls", response)
            
            # Check message content
            message = response["message"]
            self.assertTrue(
                "test file" in message.lower() or 
                "read" in message.lower() or 
                "tool" in message.lower()
            )
        else:
            # For backward compatibility with string responses
            self.assertIsInstance(response, str)
            # The response should either include the content or explain that tool usage is needed
            self.assertTrue(
                "test file" in response.lower() or 
                "read" in response.lower() or 
                "tool" in response.lower()
            )

    # Can add more tests for other tool functionality


if __name__ == "__main__":
    unittest.main()
