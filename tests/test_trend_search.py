#!/usr/bin/env python3
"""
Tests for the trend_search functionality.

These tests verify the functionality of the trend_search tool by making
real API calls to the Google Trends API.

Requirements:
- GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables must be set
"""

import os
import sys
from pathlib import Path
import dotenv
import pytest
import unittest
from typing import ClassVar, Optional, Any
import asyncio
import json

# Add the parent directory to the path so we can import the agent package
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

# Import agent package components
from cursor_agent_tools.tools.search_tools import trend_search, get_trending_topics  # noqa: E402


class TestTrendSearch(unittest.TestCase):
    """Test cases for the trend_search feature."""

    # Add type hints for class variables
    api_key: ClassVar[Optional[str]]
    search_engine_id: ClassVar[Optional[str]]
    skip_tests: ClassVar[bool]

    @classmethod
    def setUpClass(cls) -> None:
        """Set up test class and check for required API keys."""
        cls.api_key = os.environ.get("GOOGLE_API_KEY")
        cls.search_engine_id = os.environ.get("GOOGLE_SEARCH_ENGINE_ID")

        # Skip tests if API keys are not available
        if not cls.api_key or not cls.search_engine_id:
            cls.skip_tests = True
            print("WARNING: GOOGLE_API_KEY or GOOGLE_SEARCH_ENGINE_ID not set. Skipping tests.")
        else:
            cls.skip_tests = False

    def check_skip(self) -> None:
        """Check if tests should be skipped."""
        if self.skip_tests:
            self.skipTest("API keys not available")

    async def test_get_trending_topics(self) -> None:
        """Test the get_trending_topics function."""
        self.check_skip()

        # Test with default parameters
        search_term = "top trending topics in Arts & Entertainment"
        category = "Arts & Entertainment"
        topics = await get_trending_topics(search_term, category)

        # Verify we got a result
        self.assertIsNotNone(topics)
        self.assertIsInstance(topics, list)
        self.assertGreater(len(topics), 0)

        # Verify each topic is a string
        for topic in topics:
            self.assertIsInstance(topic, str)
            self.assertTrue(topic)  # Not empty

    async def test_trend_search_basic(self) -> None:
        """Test the basic functionality of trend_search."""
        self.check_skip()

        # Test with basic parameters
        result = await trend_search(query="entertainment trends", max_results=1)

        # Verify the structure of the result
        self.assertIsInstance(result, dict)
        self.assertIn('category', result)
        self.assertIn('category_id', result)
        self.assertIn('trends', result)

        # Verify trends are present
        self.assertIsInstance(result['trends'], list)
        self.assertGreater(len(result['trends']), 0)

        # Verify structure of each trend
        for trend in result['trends']:
            self.assertIn('name', trend)
            self.assertIn('snippet', trend)
            self.assertIn('sources', trend)
            self.assertIsInstance(trend['sources'], list)

    async def test_trend_search_with_custom_parameters(self) -> None:
        """Test trend_search with custom parameters."""
        self.check_skip()

        # Test with custom parameters
        result = await trend_search(
            query="technology trends",
            country_code="GB",  # United Kingdom
            max_results=1
        )

        # Verify the result has the expected category
        self.assertIn(result['category'], ["Science & Technology", "Arts & Entertainment"])
        self.assertIsInstance(result['category_id'], int)

        # Verify the number of trends
        self.assertLessEqual(len(result['trends']), 5)


@pytest.mark.asyncio
async def test_trend_search_basic() -> None:
    """Test basic trend search functionality."""
    result = await trend_search(query="entertainment trends", max_results=1)

    assert isinstance(result, dict)
    assert "query" in result
    assert "category" in result
    assert "trends" in result
    assert isinstance(result["trends"], list)


@pytest.mark.asyncio
async def test_trend_search_with_agent() -> None:
    """Test trend search with mock agent."""
    # Create a mock agent
    class MockAgent:
        async def get_structured_output(self, prompt: str, schema: Any) -> dict:
            return {"category": "Entertainment"}

    mock_agent = MockAgent()

    result = await trend_search(
        query="What's trending in movies?",
        max_results=1,
        agent=mock_agent
    )

    assert isinstance(result, dict)
    assert result["category"] == "Entertainment"
    assert isinstance(result["trends"], list)


if __name__ == "__main__":
    unittest.main()
