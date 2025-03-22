import os
import shutil
import tempfile
import unittest
from typing import Any, Dict

from agent.tools.file_tools import create_file, delete_file, edit_file, list_directory, read_file
from agent.tools.search_tools import file_search, grep_search
from agent.tools.system_tools import run_terminal_command


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
        # With the test file of only 5 lines, it will read to the end
        self.assertEqual(result["end_line"], 5)
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


class TestSearchTools(unittest.TestCase):
    """Test the search tools."""

    def setUp(self) -> None:
        """Set up the test environment."""
        # Create a temp directory for test files
        self.test_dir = tempfile.mkdtemp()

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

    def tearDown(self) -> None:
        """Clean up after tests."""
        # Remove temp directory
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_grep_search(self) -> None:
        """Test grep search."""
        # Change to the test directory to make relative paths work
        original_dir = os.getcwd()
        os.chdir(self.test_dir)

        try:
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
            os.chdir(original_dir)

    def test_file_search(self) -> None:
        """Test file search."""
        # Change to the test directory to make relative paths work
        original_dir = os.getcwd()
        os.chdir(self.test_dir)

        try:
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
            os.chdir(original_dir)


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
