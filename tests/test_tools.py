import os
import shutil
import tempfile
import unittest
from typing import Any, Dict

import pytest

from agent.tools.file_tools import create_file, delete_file, edit_file, list_directory, read_file
from agent.tools.search_tools import file_search, grep_search
from agent.tools.system_tools import run_terminal_command


@pytest.mark.fs_tools
class TestFileTools(unittest.TestCase):
    """Test the file operation tools."""

    def setUp(self) -> None:
        """Set up the test environment."""
        # Create a temp directory for test files
        self.test_dir = tempfile.mkdtemp()

        # Create some test files
        self.test_file = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file, "w") as f:
            f.write("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")

        self.test_code_file = os.path.join(self.test_dir, "test.py")
        with open(self.test_code_file, "w") as f:
            f.write("def test_function():\n    return 'Hello, World!'\n")

    def tearDown(self) -> None:
        """Clean up after tests."""
        # Remove temp directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_read_file(self) -> None:
        """Test reading a file."""
        # Read the entire file
        result = read_file(self.test_file, should_read_entire_file=True)
        self.assertIn("content", result)
        self.assertEqual(result["total_lines"], 5)
        self.assertIn("Line 1", result["content"])

        # Read with offset and limit
        # The function has a minimum read of 150 lines with a 5-line file, so it reads all lines
        result = read_file(self.test_file, offset=2, limit=2)
        self.assertIn("content", result)
        self.assertEqual(result["start_line"], 2)
        # Check that we're reading at least the requested range
        self.assertGreaterEqual(result["end_line"], 3)
        # Check content contains the expected lines
        self.assertIn("Line 2", result["content"])
        self.assertIn("Line 3", result["content"])

        # Try reading a non-existent file
        result = read_file(os.path.join(self.test_dir, "nonexistent.txt"))
        self.assertIn("error", result)

    def test_create_edit_delete_file(self) -> None:
        """Test the file creation, editing, and deletion cycle."""
        # Create a new file
        new_file = os.path.join(self.test_dir, "new.txt")
        create_result = create_file(new_file, "This is a new file")
        self.assertIn("status", create_result)
        self.assertEqual(create_result["status"], "success")
        self.assertTrue(os.path.exists(new_file))

        # Edit the file
        edit_result = edit_file(
            new_file, "Add a second line", "This is a new file\nSecond line added"
        )
        self.assertIn("status", edit_result)
        self.assertEqual(edit_result["status"], "success")

        # Read to verify the edit
        read_result = read_file(new_file, should_read_entire_file=True)
        self.assertIn("Second line added", read_result["content"])

        # Delete the file
        delete_result = delete_file(new_file)
        self.assertIn("status", delete_result)
        self.assertEqual(delete_result["status"], "success")
        self.assertFalse(os.path.exists(new_file))

    def test_list_directory(self) -> None:
        """Test listing a directory."""
        result = list_directory(self.test_dir)
        self.assertIn("contents", result)
        self.assertEqual(len(result["contents"]), 2)  # We created 2 files in setUp

        # Check file details
        for item in result["contents"]:
            self.assertIn("name", item)
            self.assertIn("type", item)
            self.assertIn("path", item)

        # Try listing a non-existent directory
        result = list_directory(os.path.join(self.test_dir, "nonexistent"))
        self.assertIn("error", result)


@pytest.mark.fs_tools
class TestSearchTools(unittest.TestCase):
    """Test the search tools."""

    def setUp(self) -> None:
        """Set up the test environment."""
        # Store the original directory to ensure we can return to it
        try:
            self.original_dir = os.path.abspath(os.getcwd())
        except FileNotFoundError:
            # If we can't get the current directory, use the directory where the test file is located
            self.original_dir = os.path.abspath(os.path.dirname(__file__))
            os.chdir(self.original_dir)
            print(f"Reset working directory to: {self.original_dir}")
            
        # Create a temp directory for test files using absolute paths
        try:
            # Create a test directory in the test_files_tmp directory
            self.test_dir = os.path.abspath(os.path.join(self.original_dir, "test_files_tmp", "search_tools_test"))
            os.makedirs(self.test_dir, exist_ok=True)
            print(f"Test directory path: {self.test_dir}")
            print(f"Test directory exists: {os.path.exists(self.test_dir)}")
            print(f"Test directory is writable: {os.access(self.test_dir, os.W_OK)}")
            
            # Create multiple test files with content to search
            self.files = []
            for i in range(3):
                file_path = os.path.join(self.test_dir, f"test{i}.txt")
                with open(file_path, "w") as f:
                    f.write(f"This is test file {i}\nIt contains searchable content\nFIND_ME_{i}")
                self.files.append(file_path)

            # Add a Python file
            self.py_file = os.path.join(self.test_dir, "test.py")
            with open(self.py_file, "w") as f:
                f.write("def search_function():\n    return 'FIND_ME_PY'\n")
            self.files.append(self.py_file)
            
        except Exception as e:
            self.skipTest(f"Error setting up test environment: {str(e)}")

    def tearDown(self) -> None:
        """Clean up after tests."""
        # Clean up test directory if it exists
        if hasattr(self, "test_dir") and os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir, ignore_errors=True)
                print(f"Removed test directory: {self.test_dir}")
            except Exception as e:
                print(f"Warning: Could not clean up test directory: {str(e)}")
                
        # Return to original directory if we changed it
        if hasattr(self, "original_dir"):
            try:
                os.chdir(self.original_dir)
                print(f"Returned to original directory: {self.original_dir}")
            except Exception as e:
                print(f"Warning: Could not return to original directory: {str(e)}")

    def test_grep_search(self) -> None:
        """Test grep search."""
        # Change to the test directory to make relative paths work
        try:
            original_dir = os.path.abspath(os.getcwd())
            os.chdir(self.test_dir)
            print(f"Changed to test directory: {self.test_dir}")

            # Search for a term that exists in all files
            result = grep_search("searchable")
            self.assertIn("results", result)
            self.assertEqual(result["total_matches"], 3)

            # Search for a specific term
            result = grep_search("FIND_ME_PY")
            self.assertIn("results", result)
            self.assertEqual(result["total_matches"], 1)
            self.assertIn("test.py", result["results"][0]["file"])

            # Case-insensitive search
            result = grep_search("find_me", case_sensitive=False)
            self.assertIn("results", result)
            self.assertGreaterEqual(result["total_matches"], 4)  # All 4 files have "FIND_ME"
        finally:
            # Restore the original directory
            try:
                os.chdir(original_dir)
                print(f"Returned to original directory: {original_dir}")
            except Exception as e:
                print(f"Warning: Could not return to original directory: {str(e)}")
                # Try to go back to the initial directory as a fallback
                if hasattr(self, "original_dir"):
                    try:
                        os.chdir(self.original_dir)
                        print(f"Returned to setup directory: {self.original_dir}")
                    except Exception as ex:
                        print(f"Failed to return to any known directory: {str(ex)}")

    def test_file_search(self) -> None:
        """Test file search."""
        # Change to the test directory to make relative paths work
        try:
            original_dir = os.path.abspath(os.getcwd())
            os.chdir(self.test_dir)
            print(f"Changed to test directory: {self.test_dir}")

            # Search for Python files
            result = file_search(".py")
            self.assertIn("results", result)
            self.assertEqual(len(result["results"]), 1)
            self.assertIn("test.py", result["results"][0]["path"])

            # Search for all test files
            result = file_search("test")
            self.assertIn("results", result)
            self.assertEqual(len(result["results"]), 4)  # All 4 files have "test" in name
        finally:
            # Restore the original directory
            try:
                os.chdir(original_dir)
                print(f"Returned to original directory: {original_dir}")
            except Exception as e:
                print(f"Warning: Could not return to original directory: {str(e)}")
                # Try to go back to the initial directory as a fallback
                if hasattr(self, "original_dir"):
                    try:
                        os.chdir(self.original_dir)
                        print(f"Returned to setup directory: {self.original_dir}")
                    except Exception as ex:
                        print(f"Failed to return to any known directory: {str(ex)}")


class TestSystemTools(unittest.TestCase):
    """Test the system tools."""

    def setUp(self) -> None:
        """Set up the test environment."""
        pass

    def test_run_terminal_command(self) -> None:
        """Test running terminal commands."""
        # Run a simple echo command
        result = run_terminal_command("echo 'test'")
        self.assertIn("stdout", result)
        self.assertIn("test", result["stdout"])
        self.assertEqual(result["exit_code"], 0)

        # Run a command that pipes to cat (testing pager handling)
        result = run_terminal_command("echo 'test' | less")
        self.assertIn("stdout", result)
        self.assertIn("test", result["stdout"])
        self.assertEqual(result["exit_code"], 0)

        # Test command that doesn't exist
        result = run_terminal_command("command_that_does_not_exist")
        self.assertIn("stderr", result)
        self.assertNotEqual(result["exit_code"], 0)

        # Test dangerous command rejection
        result = run_terminal_command("rm -rf /")
        self.assertIn("error", result)


if __name__ == "__main__":
    unittest.main()
