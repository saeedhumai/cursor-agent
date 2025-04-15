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

# Add the parent directory to the path so we can import the agent package
parent_dir = str(Path(__file__).parent.parent.absolute())
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from agent.tools.search_tools import trend_search
from agent.factory import create_agent

# Load environment variables from .env file if it exists
dotenv.load_dotenv()


def main():
    """Run the trend_search examples."""
    # Check if required API keys are available
    if not os.environ.get("GOOGLE_API_KEY") or not os.environ.get("GOOGLE_SEARCH_ENGINE_ID"):
        print("ERROR: GOOGLE_API_KEY and GOOGLE_SEARCH_ENGINE_ID environment variables must be set.")
        print("Please set these variables and try again.")
        sys.exit(1)
        
    # Initialize an agent for category determination
    # Using gpt-4o for better function calling and structured output support
    agent = create_agent("gpt-4o", use_tools=True)
    print("Agent initialized for category determination")

    # print("\n=== Example 1: Default Search (All Categories) ===")
    # trends = trend_search(
    #     query="current trends", 
    #     max_results=1,
    #     agent=agent
    # )
    # print(f"Category: {trends['category']}")
    # print(f"Found {len(trends['trends'])} trends:")
    # for i, trend in enumerate(trends['trends'], 1):
    #     print(f"\n{i}. {trend['name']}")
    #     print(f"   Snippet: {trend['snippet']}")
    #     print(f"   Sources: {trend['sources'][:2]}")  # Show first 2 sources for brevity
    
    # print("\n=== Example 2: Entertainment Category ===")
    # entertainment_trends = trend_search(
    #     query="entertainment and arts trending topics",
    #     max_results=1,
    #     agent=agent
    # )
    # print(f"Category: {entertainment_trends['category']}")
    # print(f"Found {len(entertainment_trends['trends'])} trends:")
    # for i, trend in enumerate(entertainment_trends['trends'], 1):
    #     print(f"\n{i}. {trend['name']}")
    #     print(f"   Snippet: {trend['snippet']}")
    #     print(f"   Sources: {trend['sources'][:2]}")
    
    print("\n=== Example 3: Technology Trends in UK ===")
    uk_tech_trends = trend_search(
        query="technology and science trending topics",
        country_code="GB",  # United Kingdom
        max_results=3,
        agent=agent
    )
    print(f"Category: {uk_tech_trends['category']} (UK)")
    print(f"Found {len(uk_tech_trends['trends'])} trends:")
    for i, trend in enumerate(uk_tech_trends['trends'], 1):
        print(f"\n{i}. {trend['name']}")
        print(f"   Snippet: {trend['snippet']}")
        print(f"   Sources: {trend['sources'][:2]}")
    
    # print("\n=== Example 4: Sports Trends ===")
    # sports_trends = trend_search(
    #     query="sports and fitness trending topics",
    #     max_results=1,
    #     agent=agent
    # )
    # print(f"Category: {sports_trends['category']}")
    # print(f"Found {len(sports_trends['trends'])} trends:")
    # for i, trend in enumerate(sports_trends['trends'], 1):
    #     print(f"\n{i}. {trend['name']}")
    #     print(f"   Snippet: {trend['snippet']}")
    #     print(f"   Sources: {trend['sources'][:2]}")


if __name__ == "__main__":
    main() 