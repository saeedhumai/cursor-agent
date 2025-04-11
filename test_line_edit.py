#!/usr/bin/env python3

import json
import logging
from pathlib import Path
from agent.tools import file_tools

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Set agent.tools.file_tools logger to DEBUG
file_tools_logger = logging.getLogger("agent.tools.file_tools")
file_tools_logger.setLevel(logging.DEBUG)

# Create a temporary directory and test file
temp_dir = Path("./test_temp")
temp_dir.mkdir(exist_ok=True)

test_file = temp_dir / "test.py"
original_content = """#!/usr/bin/env python3

def hello():
    print("Hello")

def add(a, b):
    return a + b

def main():
    hello()
    print(add(1, 2))

if __name__ == "__main__":
    main()
"""

with open(test_file, "w") as f:
    f.write(original_content)
logger.info(f"Created test file at {test_file}")

# Create a test edit
line_edits = {
    "3-4": "def hello():\n    print(\"Hello, World!\")"
}

# Convert to JSON string
json_str = json.dumps(line_edits)
logger.info(f"JSON string: {json_str}")

# First, test if apply_line_based_edit works directly
with open(test_file, "r") as f:
    content = f.read()

try:
    # Direct test of apply_line_based_edit
    logger.info("Testing apply_line_based_edit directly...")
    edited = file_tools.apply_line_based_edit(content, line_edits)
    logger.info(f"Result from direct call:\n{edited}")
    
    # Now test through apply_edit with the JSON string
    logger.info("Testing apply_edit with JSON string...")
    edited = file_tools.apply_edit(content, json_str)
    logger.info(f"Result from apply_edit:\n{edited}")
    
    # Finally test through edit_file
    logger.info("Testing edit_file...")
    result = file_tools.edit_file(
        target_file=str(test_file),
        instructions="Update hello function",
        code_edit=json_str
    )
    logger.info(f"Edit result: {result}")
    
    # Check the file content
    with open(test_file, "r") as f:
        final_content = f.read()
        logger.info(f"Final file content:\n{final_content}")
        
except Exception as e:
    logger.error(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

# Cleanup
import shutil
shutil.rmtree(temp_dir)
logger.info("Cleaned up") 