"""
Integration tests for image query functionality.

These tests use real API calls to test the image query capabilities
of both OpenAI and Claude agents.
"""

import os
import pytest
import base64
from pathlib import Path
from unittest.mock import patch, MagicMock
from typing import Optional, Union

from agent.claude_agent import ClaudeAgent
from agent.openai_agent import OpenAIAgent
from agent.permissions import PermissionOptions


# Create a simple test image
@pytest.fixture
def test_image_path() -> Optional[str]:
    """Use the specified test image."""
    image_path = "/Users/femi/Documents/civai/chrome-cap/test.png"
    
    if not os.path.exists(image_path):
        pytest.skip(f"Test image not found at {image_path}")
    
    return image_path


class TestOpenAIImageIntegration:
    """Integration tests for OpenAI image query functionality."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.environ.get("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY environment variable not set"
    )
    async def test_openai_query_image(self, test_image_path: str) -> None:
        """Test that OpenAI agent can analyze an image."""
        api_key = os.environ.get("OPENAI_API_KEY", "")
        
        # Create agent with auto-approval for permissions
        agent = OpenAIAgent(
            api_key=api_key,
            model="gpt-4o",
            permission_options=PermissionOptions(yolo_mode=True)
        )
        
        # Query about the test image
        result = await agent.query_image([test_image_path], "Describe this image briefly.")
        
        # Verify we got a reasonable response
        assert isinstance(result, str)
        assert len(result) > 20  # Should have some content
        assert "proxy error" in result.lower() or "server" in result.lower()


class TestClaudeImageIntegration:
    """Integration tests for Claude image query functionality."""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.environ.get("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY environment variable not set"
    )
    async def test_claude_query_image(self, test_image_path: str) -> None:
        """Test that Claude agent can analyze an image."""
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        
        # Create agent with auto-approval for permissions
        agent = ClaudeAgent(
            api_key=api_key,
            model="claude-3-5-sonnet-latest",
            permission_options=PermissionOptions(yolo_mode=True)
        )
        
        # Query about the test image
        result = await agent.query_image([test_image_path], "Describe this image briefly.")
        
        # Verify we got a reasonable response
        assert isinstance(result, str)
        assert len(result) > 20  # Should have some content
        assert "proxy error" in result.lower() or "server" in result.lower()
