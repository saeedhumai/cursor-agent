import json
import os
import re
import subprocess
from typing import Any, Dict, List, Optional

from ..logger import get_logger

# Initialize logger
logger = get_logger(__name__)


def codebase_search(
    query: str, target_directories: Optional[List[str]] = None, explanation: Optional[str] = None
) -> Dict[str, Any]:
    """
    Find snippets of code from the codebase most relevant to the search query.
    This is a semantic search tool that finds code semantically matching the query.

    Args:
        query: The search query to find relevant code
        target_directories: Optional list of directories to search in
        explanation: Optional explanation of why this search is being performed

    Returns:
        Dict containing the search results
    """
    try:
        logger.info(f"Performing codebase search for: {query}")
        
        if target_directories is None:
            # Default to current directory if none specified
            target_directories = [os.getcwd()]
            logger.debug(f"No target directories specified, using current directory: {os.getcwd()}")
        else:
            logger.debug(f"Searching in directories: {', '.join(target_directories)}")

        # For now, we'll use a simple grep-based approach since we don't have a semantic search engine
        # In a real implementation, this should use a vector search or dedicated code search tool
        results = []

        for directory in target_directories:
            if not os.path.exists(directory):
                logger.warning(f"Directory does not exist: {directory}")
                continue

            for root, _, files in os.walk(directory):
                for file in files:
                    # Skip binary files and hidden files
                    if file.startswith(".") or any(
                        file.endswith(ext) for ext in [".jpg", ".png", ".gif", ".zip", ".pyc"]
                    ):
                        continue

                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()

                        # Very simple search - in a real implementation, use semantic search
                        if query.lower() in content.lower():
                            # Find the line numbers where the query appears
                            lines = content.splitlines()
                            matches = []

                            for i, line in enumerate(lines):
                                if query.lower() in line.lower():
                                    context_start = max(0, i - 2)
                                    context_end = min(len(lines) - 1, i + 2)
                                    context = "\n".join(lines[context_start : context_end + 1])
                                    matches.append(
                                        {
                                            "line_number": i + 1,  # 1-indexed
                                            "content": line,
                                            "context": context,
                                        }
                                    )

                            if matches:
                                results.append(
                                    {
                                        "file": file_path,
                                        "matches": matches[:5],  # Limit to 5 matches per file
                                    }
                                )
                                logger.debug(f"Found {len(matches)} matches in file: {file_path}")
                    except Exception as e:
                        # Skip files that can't be read
                        logger.debug(f"Error reading file {file_path}: {str(e)}")
                        continue

        logger.info(f"Codebase search completed. Found relevant code in {len(results)} files")
        return {
            "query": query,
            "results": results[:20],  # Limit to 20 files
            "total_files_searched": sum(
                1 for _ in os.walk(directory) for directory in target_directories
            ),
        }

    except Exception as error:
        logger.error(f"Error in codebase search: {str(error)}")
        return {"error": str(error)}


def grep_search(
    query: str,
    explanation: Optional[str] = None,
    case_sensitive: bool = False,
    include_pattern: Optional[str] = None,
    exclude_pattern: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Fast text-based regex search that finds exact pattern matches within files or directories.

    Args:
        query: The regex pattern to search for
        explanation: Optional explanation of why this search is being performed
        case_sensitive: Whether the search should be case sensitive
        include_pattern: Optional glob pattern for files to include
        exclude_pattern: Optional glob pattern for files to exclude

    Returns:
        Dict containing the search results
    """
    try:
        logger.info(f"Performing grep search for pattern: {query}")
        logger.debug(f"Search parameters - case_sensitive: {case_sensitive}, include: {include_pattern}, exclude: {exclude_pattern}")
        
        # Check if ripgrep is installed
        have_ripgrep = False
        try:
            subprocess.run(["rg", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            have_ripgrep = True
            logger.debug("Using ripgrep for search")
        except (subprocess.SubprocessError, FileNotFoundError):
            have_ripgrep = False
            logger.debug("Ripgrep not available, using fallback search")

        results = []

        if have_ripgrep:
            # Use ripgrep for faster searching
            cmd = ["rg", "--json"]

            if not case_sensitive:
                cmd.append("-i")

            if include_pattern:
                cmd.extend(["-g", include_pattern])

            if exclude_pattern:
                cmd.extend(["-g", f"!{exclude_pattern}"])

            cmd.extend(["--max-count", "50", query, "."])

            logger.debug(f"Executing ripgrep command: {' '.join(cmd)}")
            process = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = process.stdout

            # Parse the JSON output
            for line in output.splitlines():
                try:
                    data = json.loads(line)
                    if data["type"] == "match":
                        file_path = data["data"]["path"]["text"]
                        line_number = data["data"]["line_number"]
                        line_text = data["data"]["lines"]["text"]

                        results.append(
                            {
                                "file": file_path,
                                "line_number": line_number,
                                "content": line_text.strip(),
                            }
                        )
                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    logger.debug(f"Error parsing ripgrep output: {str(e)}")
                    continue
        else:
            # Fallback to a simple recursive grep
            for root, _, files in os.walk(os.getcwd()):
                for file in files:
                    # Apply include/exclude filters
                    if include_pattern and not re.match(include_pattern, file):
                        continue

                    if exclude_pattern and re.match(exclude_pattern, file):
                        continue

                    file_path = os.path.join(root, file)

                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            lines = f.readlines()

                        for i, line in enumerate(lines):
                            flags = 0 if case_sensitive else re.IGNORECASE
                            if re.search(query, line, flags=flags):
                                results.append(
                                    {
                                        "file": file_path,
                                        "line_number": i + 1,  # 1-indexed
                                        "content": line.strip(),
                                    }
                                )
                    except Exception as e:
                        # Skip files that can't be read
                        logger.debug(f"Error reading file {file_path}: {str(e)}")
                        continue

                    # Limit to 50 matches
                    if len(results) >= 50:
                        break

                if len(results) >= 50:
                    break

        logger.info(f"Grep search completed. Found {len(results)} matches")
        return {"query": query, "results": results, "total_matches": len(results)}

    except Exception as error:
        logger.error(f"Error in grep search: {str(error)}")
        return {"error": str(error)}


def file_search(query: str, explanation: Optional[str] = None) -> Dict[str, Any]:
    """
    Fast file search based on fuzzy matching against file path.

    Args:
        query: Fuzzy filename to search for
        explanation: Optional explanation of why this search is being performed

    Returns:
        Dict containing the search results
    """
    try:
        logger.info(f"Performing file search for: {query}")
        
        results = []

        for root, _, files in os.walk(os.getcwd()):
            for file in files:
                if query.lower() in file.lower():
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    file_type = "unknown"

                    # Determine file type based on extension
                    if "." in file:
                        extension = file.split(".")[-1].lower()
                        file_type = extension

                    results.append(
                        {"path": file_path, "name": file, "size": file_size, "type": file_type}
                    )
                    logger.debug(f"Found matching file: {file_path}")

                    # Limit to 10 results
                    if len(results) >= 10:
                        break

            if len(results) >= 10:
                break

        logger.info(f"File search completed. Found {len(results)} matching files")
        return {"query": query, "results": results, "total_matches": len(results)}

    except Exception as error:
        logger.error(f"Error in file search: {str(error)}")
        return {"error": str(error)}


def web_search(search_term: str, explanation: Optional[str] = None) -> Dict[str, Any]:
    """
    Search the web for information about any topic.

    Args:
        search_term: The search term to look up on the web
        explanation: Optional explanation of why this search is being performed

    Returns:
        Dict containing the search results
    """
    try:
        logger.info(f"Performing web search for: {search_term}")
        
        # This is a placeholder for a real web search implementation
        # In a real implementation, you'd use a search API like Google Custom Search or DuckDuckGo

        logger.debug("Using placeholder implementation for web search")
        # For now, we'll return a message indicating this is a placeholder
        return {
            "results": [
                {
                    "title": "Web search placeholder",
                    "snippet": f"This is a placeholder for web search results for: {search_term}",
                    "url": "https://example.com",
                }
            ],
            "message": "Note: This is a placeholder. In a real implementation, you would use a search API or web scraping to get actual search results.",
        }

    except Exception as error:
        logger.error(f"Error in web search: {str(error)}")
        return {"error": str(error)}
