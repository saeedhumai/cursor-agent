"""
Tools for image analysis and processing using LLMs.
"""

import os
from typing import Any, Dict, List

from ..logger import get_logger
from ..permissions import PermissionStatus

# Initialize logger
logger = get_logger(__name__)


async def query_images(query: str, image_paths: List[str], agent: Any) -> Dict[str, Any]:
    """
    Query an AI model about one or more images.

    This function supports analyzing images using the vision capabilities of large language models.
    The agent must implement a query_image method to support this functionality.

    Args:
        query: The question or query about the image(s)
        image_paths: List of local paths to image files to analyze
        agent: The agent instance with vision capabilities

    Returns:
        A dictionary containing the result or error message
    """
    logger.info(f"Processing query for {len(image_paths)} images")

    # Request permission to access the images
    details = {
        "query": query,
        "image_paths": image_paths
    }

    permission_status = agent.permission_manager.request_permission("read_image", details)
    if permission_status != PermissionStatus.GRANTED:
        error_msg = "Permission to access images was denied"
        logger.warning(error_msg)
        return {"error": error_msg}

    # Validate image paths and existence
    for path in image_paths:
        if not os.path.exists(path):
            error_msg = f"Image file not found: {path}"
            logger.error(error_msg)
            return {"error": error_msg}

        # Validate file is an image based on extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
        file_extension = os.path.splitext(path)[1].lower()
        if file_extension not in valid_extensions:
            error_msg = f"File {path} does not appear to be a valid image (must have extension: {', '.join(valid_extensions)})"
            logger.error(error_msg)
            return {"error": error_msg}

    try:
        # Use the agent's query_image method to analyze the images
        result = await agent.query_image(image_paths, query)
        logger.info("Successfully processed image query")
        return {"result": result}
    except Exception as e:
        error_msg = f"Error processing image query: {str(e)}"
        logger.error(error_msg)
        return {"error": error_msg}
