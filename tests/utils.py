import os
import time
from typing import Any, Dict, Optional


def get_test_env() -> Dict[str, str]:
    """
    Get environment variables needed for testing.
    For E2E testing, we require real API keys.
    """
    env = {}

    # Check for Anthropic API key - needed for real testing
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    if anthropic_key and is_real_api_key(anthropic_key, "anthropic"):
        env["ANTHROPIC_API_KEY"] = anthropic_key
        print("✓ Using valid Anthropic API key")
    else:
        print("⚠ No valid Anthropic API key found - Claude tests will be skipped")

    # Check for OpenAI API key - needed for real testing
    openai_key = os.environ.get("OPENAI_API_KEY")
    if openai_key and is_real_api_key(openai_key, "openai"):
        env["OPENAI_API_KEY"] = openai_key
        print("✓ Using valid OpenAI API key")
    else:
        print("⚠ No valid OpenAI API key found - OpenAI tests will be skipped")

    return env


def is_real_api_key(api_key: Optional[str], provider: str) -> bool:
    """
    Check if an API key looks like a real one.

    Args:
        api_key: The API key to check
        provider: The API provider ('anthropic' or 'openai') - used to determine expected key format

    Returns:
        True if the key looks real, False otherwise
    """
    if not api_key:
        return False

    # Placeholder patterns that indicate a fake key
    placeholder_patterns = [
        "your_api_key",
        "your-api-key",
        "api_key",
        "api-key",
        "placeholder",
        "demo",
        "test_",
        "dummy",
    ]

    api_key_lower = api_key.lower()
    if any(pattern in api_key_lower for pattern in placeholder_patterns):
        return False

    # Check key format per provider
    if provider == "anthropic":  # For Claude models
        return api_key.startswith(("sk-ant-", "sk-")) and len(api_key) > 20
    elif provider == "openai":  # For GPT models
        return api_key.startswith(("sk-", "org-")) and len(api_key) > 20

    return False


def create_test_file(filepath: str, content: str) -> str:
    """Create a temporary test file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)
    return filepath


def delete_test_file(filepath: str) -> None:
    """Delete a temporary test file."""
    if os.path.exists(filepath):
        os.remove(filepath)


def create_user_info(open_files: Optional[list] = None) -> Dict[str, Any]:
    """Create a sample user info dictionary for testing."""
    return {
        "open_files": open_files or ["test_file.py"],
        "cursor_position": {"file": "test_file.py", "line": 10},
        "recent_files": ["other_file.py"],
        "os": "darwin",
        "workspace_path": "/tmp/test_workspace",
    }


def check_response_quality(response: str) -> bool:
    """
    More rigorous quality check for real API responses.
    This ensures we're getting proper responses from the real APIs.
    """
    if not response:
        return False

    # Check for error messages
    if response.startswith("Error:"):
        print(f"Failed quality check - response contains error: {response[:100]}")
        return False

    # Check for authentication errors
    auth_error_patterns = [
        "api key",
        "API key",
        "authentication",
        "auth",
        "credential",
        "invalid key",
        "expired key",
        "unauthorized",
        "not authorized",
        "not authenticated",
    ]

    for pattern in auth_error_patterns:
        if pattern in response.lower() and (
            "error" in response.lower() or "invalid" in response.lower()
        ):
            print(f"Failed quality check - likely auth error: {response[:100]}")
            return False

    # Extract first 10 words of response to detect query type
    first_words = " ".join(response.split()[:10]).lower()

    # Special case for file-related responses which can be shorter but still valid
    if ("file" in first_words or "open" in first_words) and "test_file.py" in response:
        # This is a file query and the response contains the expected filename
        # Even if it's short, it's likely valid
        return True

    # Check minimum length for real API responses
    if len(response) < 50:
        print(f"Failed quality check - response too short: {response}")
        return False

    # Check for meaningful content - real APIs should mention these for our test prompts
    expected_keywords = {
        "Python": ["programming", "language", "interpreted", "code", "dynamically"],
        "files": ["open", "directory", "path", "content", "file"],
        "test_function": ["function", "Hello", "World", "return", "test_file.py"],
    }

    if "python" in first_words and not any(
        word in response.lower() for word in expected_keywords["Python"]
    ):
        print(f"Failed quality check - Python query lacks key concepts: {response[:100]}")
        return False

    if (
        "file" in first_words
        and "open" in first_words
        and not any(word in response.lower() for word in expected_keywords["files"])
    ):
        print(f"Failed quality check - file query lacks key concepts: {response[:100]}")
        return False

    if "test_function" in first_words and not any(
        word in response.lower() for word in expected_keywords["test_function"]
    ):
        print(f"Failed quality check - function query lacks key concepts: {response[:100]}")
        return False

    return True
