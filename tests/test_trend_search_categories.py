#!/usr/bin/env python3
"""
Tests for the trend_search functionality with specific category handling.

These tests verify the functionality of the trend_search tool with
different categories by making real API calls to the Google Trends API.

Requirements:
- GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables must be set
"""

import os
import sys
from pathlib import Path
import dotenv
import pytest
import unittest
import logging
from typing import ClassVar, Optional

# Configure logging to see debugging output
logging.basicConfig(level=logging.INFO)

# Add the parent directory to the path so we can import the agent package
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

# Import agent package components
from agent.tools.search_tools import trend_search, get_trending_topics  # noqa: E402


class TestTrendSearchCategoriesAndCountries(unittest.TestCase):
    """Test cases for the trend_search category determination and country handling."""

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
            
    def test_country_codes(self) -> None:
        """Test if different country codes produce different results."""
        self.check_skip()
        
        # Test default country (US)
        us_results = trend_search(
            query="current trending topics",
            max_results=2
        )
        
        # Test UK trends
        uk_results = trend_search(
            query="current trending topics",
            country_code="GB",
            max_results=2
        )
        
        # Test Japan trends
        jp_results = trend_search(
            query="current trending topics",
            country_code="JP",
            max_results=2
        )
        
        # Verify each result has the expected country code
        self.assertEqual(us_results['country_code'], "US")
        self.assertEqual(uk_results['country_code'], "GB")
        self.assertEqual(jp_results['country_code'], "JP")
        
        # Print trend titles for manual inspection
        print("\nUS Trends:")
        for trend in us_results['trends']:
            print(f"- {trend['name']}")
            
        print("\nUK Trends:")
        for trend in uk_results['trends']:
            print(f"- {trend['name']}")
            
        print("\nJapan Trends:")
        for trend in jp_results['trends']:
            print(f"- {trend['name']}")
    
    def test_various_queries(self) -> None:
        """Test if different queries are properly processed."""
        self.check_skip()
        
        # Test different query types to see what categories are assigned
        query_results = {}
        
        queries = [
            "current trending topics",
            "trending technology topics",
            "trending sports news",
            "trending entertainment news",
            "trending business topics"
        ]
        
        for query in queries:
            result = trend_search(
                query=query,
                max_results=1
            )
            query_results[query] = {
                'category': result['category'],
                'category_id': result['category_id']
            }
            
        # Print out results for analysis
        print("\nCategory Results per Query:")
        for query, data in query_results.items():
            print(f"Query: '{query}'")
            print(f"  Category: {data['category']}")
            print(f"  Category ID: {data['category_id']}")
            
        # Since we don't have an agent, all should default to Arts & Entertainment
        # This test just verifies the default behavior
        for data in query_results.values():
            self.assertEqual(data['category'], "Arts & Entertainment")
            self.assertEqual(data['category_id'], 4)
            
        # Note: With a proper agent implementation, different queries should yield
        # different categories. This test verifies the current default behavior.


if __name__ == "__main__":
    unittest.main() 
