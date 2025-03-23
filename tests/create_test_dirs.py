#!/usr/bin/env python3
"""
Create necessary test directories for the test suite.
Run this before running the tests to ensure all required directories exist.
"""

import os
import sys
import shutil
import tempfile


def create_test_directories() -> bool:
    """
    Create necessary test directories.
    
    Returns:
        bool: True if all directories were created successfully, False otherwise
    """
    print("Creating test directories...")
    
    # Save original working directory
    original_dir = os.getcwd()
    print(f"Original working directory: {original_dir}")
    
    # List of directories to create
    directories = [
        "test_files_tmp",
        os.path.join("tests", "test_files_tmp"),
    ]
    
    success = True
    
    # Create each directory
    for directory in directories:
        try:
            # Use absolute path to avoid issues with changing directories
            path = os.path.abspath(os.path.join(original_dir, directory))
            print(f"Checking directory: {path}")
            
            # Remove existing directory if it exists to ensure a clean state
            if os.path.exists(path):
                try:
                    shutil.rmtree(path)
                    print(f"Removed existing directory: {path}")
                except Exception as e:
                    print(f"Warning: Could not remove existing directory {path}: {e}")
            
            # Create directory with explicit permissions
            os.makedirs(path, mode=0o755, exist_ok=True)
            print(f"Created directory: {path}")
            
            # Verify the directory exists and is writable
            if not os.path.exists(path):
                print(f"Error: Directory creation failed for {path}")
                success = False
            elif not os.access(path, os.W_OK):
                print(f"Error: Directory {path} is not writable")
                success = False
            else:
                # Create a small test file to verify file creation works
                test_file = os.path.join(path, "test_permissions.txt")
                try:
                    with open(test_file, 'w') as f:
                        f.write("Test file to verify permissions\n")
                    os.remove(test_file)  # Clean up
                    print(f"Directory {path} is writable")
                except Exception as e:
                    print(f"Error: Could not write to directory {path}: {e}")
                    success = False
                    
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            success = False
    
    # Create and test a temporary chdir wrapper
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Try to change to the temp directory and back
            os.chdir(temp_dir)
            print(f"Successfully changed to temporary directory: {temp_dir}")
            os.chdir(original_dir)
            print(f"Successfully changed back to original directory: {original_dir}")
        except Exception as e:
            print(f"Error with directory operations: {e}")
            success = False
            try:
                # Ensure we're back in the original directory
                os.chdir(original_dir)
            except Exception as ex:
                print(f"Could not return to original directory! {ex}")
                success = False
    
    print("Test directories setup complete.")
    return success


if __name__ == "__main__":
    print(f"Current working directory: {os.getcwd()}")
    success = create_test_directories()
    sys.exit(0 if success else 1) 
