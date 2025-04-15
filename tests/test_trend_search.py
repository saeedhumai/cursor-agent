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
from typing import ClassVar, Optional

# Add the parent directory to the path so we can import the agent package
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

# Import agent package components
from agent.tools.search_tools import trend_search, get_trending_topics  # noqa: E402


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

    def test_get_trending_topics(self) -> None:
        """Test the get_trending_topics function."""
        self.check_skip()
        
        # Test with default parameters
        search_term = "top trending topics in Arts & Entertainment"
        category = "Arts & Entertainment"
        topics = get_trending_topics(search_term, category)
        
        # Verify we got a result
        self.assertIsNotNone(topics)
        self.assertIsInstance(topics, list)
        self.assertGreater(len(topics), 0)
        
        # Verify each topic is a string
        for topic in topics:
            self.assertIsInstance(topic, str)
            self.assertTrue(topic)  # Not empty

    def test_trend_search_basic(self) -> None:
        """Test the basic functionality of trend_search."""
        self.check_skip()
        
        # Test with basic parameters
        result = trend_search(query="entertainment trends")
        
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

    def test_trend_search_with_custom_parameters(self) -> None:
        """Test trend_search with custom parameters."""
        self.check_skip()
        
        # Test with custom parameters
        result = trend_search(
            query="technology trends",
            country_code="GB",  # United Kingdom
            max_results=5
        )
        
        # Verify the result has the expected category
        self.assertIn(result['category'], ["Science & Technology", "Arts & Entertainment"])
        self.assertIsInstance(result['category_id'], int)
        
        # Verify the number of trends
        self.assertLessEqual(len(result['trends']), 5)

    def test_trend_search_with_invalid_category(self) -> None:
        """Test trend_search with an invalid category."""
        self.check_skip()
        
        # Test with an invalid search term - should still work
        result = trend_search(
            query="invalid category trends"
        )
        
        # Verify we still get a valid category
        self.assertIsInstance(result['category'], str)
        self.assertIsInstance(result['category_id'], int)
        self.assertTrue(result['category'])  # Not empty

    def test_trend_search_with_max_results(self) -> None:
        """Test trend_search with a specified max_results."""
        self.check_skip()
        
        # Test with max_results=3
        max_results = 3
        result = trend_search(
            query="sports trends",
            max_results=max_results
        )
        
        # Verify the number of trends doesn't exceed max_results
        self.assertLessEqual(len(result['trends']), max_results)


if __name__ == "__main__":
    unittest.main() 
