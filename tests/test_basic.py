#!/usr/bin/env python3
"""Basic tests that don't require any API keys."""

import unittest


class TestBasic(unittest.TestCase):
    """Simple tests that don't require API keys."""

    def setUp(self) -> None:
        """Set up the test environment."""
        pass

    def tearDown(self) -> None:
        """Clean up after the tests."""
        pass

    def test_true_is_true(self) -> None:
        """Test that True is True - this should always pass."""
        self.assertTrue(True)

    def test_string_equals(self) -> None:
        """Test string equality - this should always pass."""
        self.assertEqual("test", "test")

    def test_math(self) -> None:
        """Test basic math - this should always pass."""
        self.assertEqual(2 + 2, 4)


if __name__ == "__main__":
    unittest.main()
