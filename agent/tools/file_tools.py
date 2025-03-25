import os
from typing import Any, Dict, List, Optional, Tuple

from ..base import BaseAgent
from ..logger import get_logger

# Initialize logger
logger = get_logger(__name__)


def read_file(
    target_file: str,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    should_read_entire_file: bool = False,
    agent: Optional[BaseAgent] = None,  # Optional agent reference for permissions
) -> Dict[str, Any]:
    """
    Read the contents of a file.

    Args:
        target_file: The path of the file to read
        offset: The line number to start reading from (1-indexed)
        limit: The number of lines to read
        should_read_entire_file: Whether to read the entire file
        agent: Reference to the agent instance for permission checks

    Returns:
        Dict containing the file contents
    """
    # No permission required for reading files
    try:
        # Handle the case where target_file is a dictionary with a path key
        if isinstance(target_file, dict) and "path" in target_file:
            file_path = target_file["path"]
        else:
            file_path = target_file

        logger.debug(f"Reading file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.warning(f"File does not exist: {file_path}")
            return {"error": f"File {file_path} does not exist"}

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if should_read_entire_file:
            content = "".join(lines)
            logger.debug(f"Read entire file ({len(lines)} lines): {file_path}")
            return {"content": content, "total_lines": len(lines)}

        # Ensure offset and limit are valid
        if offset is None:
            offset = 1
        if limit is None:
            limit = 150  # Default to 150 lines

        # Convert to 0-indexed
        offset_idx = max(0, offset - 1)
        end_idx = min(len(lines), offset_idx + limit)

        # Extract the requested lines
        content_lines = lines[offset_idx:end_idx]
        content = "".join(content_lines)

        # Calculate summary
        summary = []
        if offset_idx > 0:
            summary.append(f"... {offset_idx} lines before ...")
        if end_idx < len(lines):
            summary.append(f"... {len(lines) - end_idx} lines after ...")

        # For tests that expect the end_line to be the actual line number,
        # ensure this correctly represents the last line we read
        end_line = offset + len(content_lines) - 1
        if end_line < offset:
            end_line = offset
            
        # If we read to the end of the file due to a small file size,
        # set end_line to the total number of lines
        if len(content_lines) > 0 and end_idx == len(lines):
            end_line = len(lines)

        logger.debug(f"Read file {file_path} from line {offset} to {end_line}")
        return {
            "content": content,
            "start_line": offset,
            "end_line": end_line,
            "summary": summary,
            "total_lines": len(lines),
        }

    except Exception as e:
        logger.error(f"Error reading file {target_file}: {str(e)}")
        return {"error": str(e)}


def edit_file(
    target_file: str,
    instructions: str,
    code_edit: str,
    agent: Optional[BaseAgent] = None,  # Optional agent reference for permissions
) -> Dict[str, Any]:
    """
    Edit a file according to the provided instructions and code edit.

    Args:
        target_file: Path to the file to edit
        instructions: Instructions describing the edit
        code_edit: The actual edit to apply
        agent: Reference to the agent instance for permission checks

    Returns:
        Dict containing the status of the edit operation
    """
    try:
        logger.info(f"Editing file: {target_file}")
        logger.debug(f"Edit instructions: {instructions}")
        
        # Request permission if agent is provided
        if agent:
            operation_details = {
                "target_file": target_file,
                "instructions": instructions,
                "code_edit_preview": code_edit[:100] + ("..." if len(code_edit) > 100 else ""),
            }

            if not agent.request_permission("edit_file", operation_details):
                logger.warning(f"Permission denied to edit file: {target_file}")
                return {"status": "error", "message": "Permission denied to edit file"}

        # Check if file exists
        if not os.path.exists(target_file):
            logger.warning(f"File does not exist: {target_file}")
            return {"status": "error", "message": f"File {target_file} does not exist"}

        # Read the original content
        with open(target_file, "r") as f:
            original_content = f.read()

        # Parse and apply the edit
        edited_content = apply_edit(original_content, code_edit)

        # Write the edited content back to the file
        with open(target_file, "w") as f:
            f.write(edited_content)

        logger.info(f"Successfully edited file: {target_file}")
        return {"status": "success", "message": f"Successfully edited {target_file}"}

    except Exception as e:
        logger.error(f"Error editing file {target_file}: {str(e)}")
        return {"status": "error", "message": str(e)}


def delete_file(
    target_file: str,
    agent: Optional[BaseAgent] = None,  # Optional agent reference for permissions
) -> Dict[str, Any]:
    """
    Delete a file at the specified path.

    Args:
        target_file: The path of the file to delete
        agent: Reference to the agent instance for permission checks

    Returns:
        Dict containing the status of the deletion
    """
    try:
        logger.info(f"Deleting file: {target_file}")
        
        # Request permission if agent is provided
        if agent:
            operation_details = {
                "target_file": target_file,
                "operation": "delete",
            }

            if not agent.request_permission("delete_file", operation_details):
                logger.warning(f"Permission denied to delete file: {target_file}")
                return {"status": "error", "message": "Permission denied to delete file"}

        if not os.path.exists(target_file):
            logger.warning(f"File does not exist: {target_file}")
            return {"status": "error", "message": f"File {target_file} does not exist"}

        os.remove(target_file)
        logger.info(f"Successfully deleted file: {target_file}")
        return {"status": "success", "message": f"Deleted file {target_file}"}

    except Exception as e:
        logger.error(f"Error deleting file {target_file}: {str(e)}")
        return {"error": str(e)}


def create_file(
    file_path: str,
    content: str,
    agent: Optional[BaseAgent] = None,  # Optional agent reference for permissions
) -> Dict[str, Any]:
    """
    Create a new file with the given content.

    Args:
        file_path: Path where the file should be created
        content: Content to write to the file
        agent: Reference to the agent instance for permission checks

    Returns:
        Dict containing the status of the creation
    """
    try:
        logger.info(f"Creating file: {file_path}")
        
        # Request permission if agent is provided
        if agent:
            operation_details = {
                "file_path": file_path,
                "content_preview": content[:100] + ("..." if len(content) > 100 else ""),
            }

            if not agent.request_permission("create_file", operation_details):
                logger.warning(f"Permission denied to create file: {file_path}")
                return {"status": "error", "message": "Permission denied to create file"}

        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

        # Check if file already exists
        file_exists = os.path.exists(file_path)

        with open(file_path, "w") as f:
            f.write(content)

        if file_exists:
            logger.info(f"Updated existing file: {file_path}")
            return {"status": "success", "message": f"Updated file at {file_path}"}
        else:
            logger.info(f"Created new file: {file_path}")
            return {"status": "success", "message": f"Created file at {file_path}"}

    except Exception as e:
        logger.error(f"Error creating file {file_path}: {str(e)}")
        return {"error": str(e)}


def list_directory(
    relative_workspace_path: str,
    agent: Optional[BaseAgent] = None,  # Optional agent reference for permissions
) -> Dict[str, Any]:
    """
    List the contents of a directory.

    Args:
        relative_workspace_path: Path to list contents of
        agent: Reference to the agent instance for permission checks

    Returns:
        Dict containing the directory contents
    """
    # No permission required for listing directories
    try:
        logger.debug(f"Listing directory: {relative_workspace_path}")
        
        if not os.path.exists(relative_workspace_path):
            logger.warning(f"Directory does not exist: {relative_workspace_path}")
            return {"error": f"Directory {relative_workspace_path} does not exist"}

        if not os.path.isdir(relative_workspace_path):
            logger.warning(f"Not a directory: {relative_workspace_path}")
            return {"error": f"{relative_workspace_path} is not a directory"}

        # Get the directory contents
        contents = []
        for item in os.listdir(relative_workspace_path):
            item_path = os.path.join(relative_workspace_path, item)
            item_type = "dir" if os.path.isdir(item_path) else "file"
            item_size = os.path.getsize(item_path) if item_type == "file" else None

            contents.append({"name": item, "type": item_type, "size": item_size, "path": item_path})

        logger.debug(f"Listed {len(contents)} items in directory: {relative_workspace_path}")
        return {"contents": contents}

    except Exception as e:
        logger.error(f"Error listing directory {relative_workspace_path}: {str(e)}")
        return {"error": str(e)}


def apply_edit(original_content: str, code_edit: str) -> str:
    """
    Parse and apply an edit to the original content.

    Args:
        original_content: The original file content
        code_edit: The edit to apply, which may contain "... existing code ..." markers

    Returns:
        The content after applying the edit
    """
    # If no markers, simply return the code_edit
    if "// ... existing code ..." not in code_edit and "# ... existing code ..." not in code_edit:
        logger.debug("No existing code markers found, replacing entire content")
        return code_edit

    original_lines = original_content.splitlines()
    edit_lines = code_edit.splitlines()

    # Parse the edit to identify segments
    segments: List[Tuple[str, Optional[List[str]]]] = []
    current_segment: List[str] = []
    for line in edit_lines:
        if "// ... existing code ..." in line or "# ... existing code ..." in line:
            if current_segment:
                segments.append(("edit", current_segment))
                current_segment = []
            segments.append(("keep", None))
        else:
            current_segment.append(line)

    if current_segment:
        segments.append(("edit", current_segment))

    # Apply the segments to the original content
    result_lines = []
    original_index = 0

    for segment_type, segment_lines in segments:
        if segment_type == "keep":
            # For "keep" segments, include the original lines
            # This is a simplistic approach; in a real implementation,
            # you might want to match the context to determine which lines to keep
            if original_index < len(original_lines):
                result_lines.append(original_lines[original_index])
                original_index += 1
        else:  # "edit"
            # For "edit" segments, include the new lines
            if segment_lines:  # Check if segment_lines is not None
                result_lines.extend(segment_lines)

    # Add any remaining original lines
    if original_index < len(original_lines):
        result_lines.extend(original_lines[original_index:])

    logger.debug(f"Applied edit with {len(segments)} segments")
    return "\n".join(result_lines)
