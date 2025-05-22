#!/usr/bin/env python3
"""
Example demonstrating how to use the trend_search feature.

This example shows how to use the trend_search function to obtain trending
topics from different categories and countries.

Requirements:
- GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables must be set
"""

import os
import sys
from pathlib import Path
import dotenv
from pprint import pprint
import asyncio
from cursor_agent_tools.tools.search_tools import trend_search
from utils.print_utils import print_info, print_error, print_separator, print_system_message

# Add the parent directory to the path so we can import the agent package
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agent.factory import create_agent

# Load environment variables from .env file if it exists
dotenv.load_dotenv()

async def main():
    """Run trend search examples."""
    try:
        print_system_message("TREND SEARCH DEMO")
        print_separator()
        
        # Example 1: Basic trend search
        print_info("\n1. Basic trend search for entertainment trends")
        uk_tech_trends = await trend_search(
            query="What's trending in technology?",
            country_code="GB",
            max_results=3
        )
        
        if "error" in uk_tech_trends:
            print_error(f"Error: {uk_tech_trends['error']}")
        else:
            print_info(f"\nFound {len(uk_tech_trends['trends'])} trends in {uk_tech_trends['category']}")
            for i, trend in enumerate(uk_tech_trends['trends'], 1):
                print_info(f"\n{i}. {trend['name']}")
                print_info(f"   Snippet: {trend['snippet'][:200]}...")
                print_info(f"   Sources: {len(trend['sources'])}")
        
        print_separator()
        print_system_message("TREND SEARCH DEMO COMPLETED")
        
    except Exception as e:
        print_error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 