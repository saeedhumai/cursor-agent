import os
from typing import Any, Dict, Optional


def read_file(
    target_file: str,
    offset: Optional[int] = None,
    limit: Optional[int] = None,
    should_read_entire_file: bool = False,
) -> Dict[str, Any]:
    """
    Read the contents of a file.

    Args:
        target_file: The path of the file to read
        offset: The line number to start reading from (1-indexed)
        limit: The number of lines to read
        should_read_entire_file: Whether to read the entire file

    Returns:
        Dict containing the file contents
    """
    try:
        # Handle the case where target_file is a dictionary with a path key
        if isinstance(target_file, dict) and "path" in target_file:
            file_path = target_file["path"]
        else:
            file_path = target_file

        if not os.path.exists(file_path):
            return {"error": f"File {file_path} does not exist"}

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        if should_read_entire_file:
            content = "".join(lines)
            return {"content": content, "total_lines": len(lines)}

        # Ensure offset and limit are valid
        if offset is None:
            offset = 1  # 1-indexed
        else:
            offset = max(1, min(offset, len(lines)))

        if limit is None:
            limit = min(250, len(lines) - offset + 1)  # Default to at most 250 lines

        # Ensure we read at minimum 150 lines if available
        limit = max(min(limit, len(lines) - offset + 1), min(150, len(lines) - offset + 1))

        # Extract the requested lines (convert from 1-indexed to 0-indexed)
        selected_lines = lines[offset - 1 : offset - 1 + limit]
        content = "".join(selected_lines)

        # Create a summary of lines outside the range
        if offset > 1:
            before_summary = f"[Lines 1-{offset-1} omitted]"
        else:
            before_summary = ""

        if offset + limit - 1 < len(lines):
            after_summary = f"[Lines {offset+limit}-{len(lines)} omitted]"
        else:
            after_summary = ""

        return {
            "content": content,
            "before_summary": before_summary,
            "after_summary": after_summary,
            "start_line": offset,
            "end_line": offset + limit - 1,
            "total_lines": len(lines),
        }

    except Exception as e:
        return {"error": str(e)}


def edit_file(target_file: str, instructions: str, code_edit: str) -> Dict[str, Any]:
    """
    Edit a file in the codebase.

    Args:
        target_file: The target file to modify
        instructions: A single sentence instruction describing the edit
        code_edit: The precise lines of code to edit

    Returns:
        Dict containing the status of the edit
    """
    try:
        # Create the directory if it doesn't exist
        directory = os.path.dirname(target_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # If the file doesn't exist, create it with the code_edit
        if not os.path.exists(target_file):
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(code_edit)
            return {"status": "success", "message": f"Created file {target_file}"}

        # If the file exists, read its content and apply the edit
        # We open and close the file to ensure it exists and is readable
        with open(target_file, "r", encoding="utf-8"):
            pass

        # If code_edit contains "// ... existing code ..." markers, apply the edit
        # This is a simplistic implementation and may not work for all cases
        if "// ... existing code ..." in code_edit or "# ... existing code ..." in code_edit:
            # Replace the content by parsing the code_edit
            edit_lines = code_edit.splitlines()
            
            # Parse and apply the edits
            result_lines = []
            for line in edit_lines:
                if "// ... existing code ..." in line or "# ... existing code ..." in line:
                    # Skip this placeholder line, we'll handle it in a more sophisticated way
                    continue
                else:
                    result_lines.append(line)

            new_content = "\n".join(result_lines)

            # Write the new content
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(new_content)

            return {
                "status": "success",
                "message": f"Edited file {target_file} based on instructions: {instructions}",
            }
        else:
            # If no markers, simply replace the file content
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(code_edit)

            return {
                "status": "success",
                "message": f"Replaced content of {target_file} based on instructions: {instructions}",
            }

    except Exception as e:
        return {"error": str(e)}


def delete_file(target_file: str) -> Dict[str, Any]:
    """
    Delete a file at the specified path.

    Args:
        target_file: The path of the file to delete

    Returns:
        Dict containing the status of the deletion
    """
    try:
        if not os.path.exists(target_file):
            return {"status": "error", "message": f"File {target_file} does not exist"}

        os.remove(target_file)
        return {"status": "success", "message": f"Deleted file {target_file}"}

    except Exception as e:
        return {"error": str(e)}


def create_file(file_path: str, content: str) -> Dict[str, Any]:
    """
    Create a new file with the given content.

    Args:
        file_path: Path where the file should be created
        content: Content to write to the file

    Returns:
        Dict containing the status of the creation
    """
    try:
        # Create the directory if it doesn't exist
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

        # Check if the file already exists
        if os.path.exists(file_path):
            return {"status": "error", "message": f"File {file_path} already exists"}

        # Create the file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {"status": "success", "message": f"Created file at {file_path}"}

    except Exception as e:
        return {"error": str(e)}


def list_directory(relative_workspace_path: str) -> Dict[str, Any]:
    """
    List the contents of a directory.

    Args:
        relative_workspace_path: Path to list contents of

    Returns:
        Dict containing the directory contents
    """
    try:
        if not os.path.exists(relative_workspace_path):
            return {"error": f"Directory {relative_workspace_path} does not exist"}

        if not os.path.isdir(relative_workspace_path):
            return {"error": f"{relative_workspace_path} is not a directory"}

        # Get the directory contents
        contents = []
        for item in os.listdir(relative_workspace_path):
            item_path = os.path.join(relative_workspace_path, item)
            item_type = "dir" if os.path.isdir(item_path) else "file"
            item_size = os.path.getsize(item_path) if item_type == "file" else None

            contents.append({"name": item, "type": item_type, "size": item_size, "path": item_path})

        return {"contents": contents}

    except Exception as e:
        return {"error": str(e)}
