"""
Tests for the image analysis tools.
"""

import os
import tempfile
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Any, Generator, Optional, Union

from agent.tools.image_tools import query_images
from agent.permissions import PermissionManager, PermissionOptions, PermissionStatus


@pytest.fixture
def mock_agent() -> MagicMock:
    """
    Create a mock agent with permission handling and query_image method.
    """
    agent = MagicMock()
    agent.query_image = AsyncMock(return_value="This is a test image of a landscape.")
    
    # Set up permission manager with mocked request_permission method
    permission_manager = MagicMock()
    permission_manager.request_permission.return_value = PermissionStatus.GRANTED
    agent.permission_manager = permission_manager
    
    return agent


@pytest.fixture
def test_image() -> str:
    """
    Create a temporary test image file.
    """
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        # Create a minimal valid JPEG file
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xd9')
        return f.name


@pytest.mark.asyncio
async def test_query_images_successful(mock_agent: MagicMock, test_image: str) -> None:
    """
    Test that query_images successfully calls the agent's query_image method.
    """
    query = "What's in this image?"
    image_paths = [test_image]
    
    result = await query_images(query, image_paths, mock_agent)
    
    assert "result" in result
    assert result["result"] == "This is a test image of a landscape."
    mock_agent.query_image.assert_called_once_with(image_paths, query)


@pytest.mark.asyncio
async def test_query_images_nonexistent_file(mock_agent: MagicMock) -> None:
    """
    Test handling of nonexistent image files.
    """
    query = "What's in this image?"
    nonexistent_path = "/path/to/nonexistent/image.jpg"
    
    result = await query_images(query, [nonexistent_path], mock_agent)
    
    assert "error" in result
    assert "not found" in result["error"]
    mock_agent.query_image.assert_not_called()


@pytest.mark.asyncio
async def test_query_images_invalid_extension(mock_agent: MagicMock, test_image: str) -> None:
    """
    Test handling of files with invalid extensions.
    """
    query = "What's in this image?"
    invalid_path = test_image + ".invalid"
    
    # Create a copy with invalid extension
    with open(test_image, 'rb') as src, open(invalid_path, 'wb') as dst:
        dst.write(src.read())
    
    try:
        result = await query_images(query, [invalid_path], mock_agent)
        
        assert "error" in result
        assert "valid image" in result["error"]
        mock_agent.query_image.assert_not_called()
    finally:
        # Clean up
        if os.path.exists(invalid_path):
            os.remove(invalid_path)


@pytest.mark.asyncio
async def test_query_images_permission_denied(mock_agent: MagicMock, test_image: str) -> None:
    """
    Test handling of permission denial.
    """
    query = "What's in this image?"
    
    # Override permission manager to deny permissions
    mock_agent.permission_manager.request_permission = MagicMock(return_value=PermissionStatus.DENIED)
    
    result = await query_images(query, [test_image], mock_agent)
    
    assert "error" in result
    assert "denied" in result["error"]
    mock_agent.query_image.assert_not_called()


@pytest.mark.asyncio
async def test_query_images_agent_error(mock_agent: MagicMock, test_image: str) -> None:
    """
    Test handling of agent errors.
    """
    query = "What's in this image?"
    
    # Set up agent to raise an exception
    mock_agent.query_image = AsyncMock(side_effect=Exception("Test error"))
    
    result = await query_images(query, [test_image], mock_agent)
    
    assert "error" in result
    assert "Test error" in result["error"]
    mock_agent.query_image.assert_called_once()


# Clean up test image after all tests
def teardown_module(module: Any) -> None:
    """Clean up any temporary files."""
    # Get all global variables to check for any test images
    for name, value in module.__dict__.items():
        # If the variable is a string, check if it's a path that exists
        if isinstance(value, str) and name.endswith('_file') and os.path.exists(value):
            os.remove(value)
