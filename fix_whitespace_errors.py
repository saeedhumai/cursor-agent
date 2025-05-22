#!/usr/bin/env python3
import os
import re
import argparse
from pathlib import Path
from typing import List, Tuple, Set

def find_python_files(root_dir: str, exclude_dirs: Set[str] = None) -> List[Path]:
    """Find all Python files in the given directory and subdirectories."""
    if exclude_dirs is None:
        exclude_dirs = {'venv', '.venv', '__pycache__', '.git', '.pytest_cache', '.mypy_cache'}
    
    python_files = []
    for path in Path(root_dir).rglob('*.py'):
        # Skip files in excluded directories
        if any(excluded in path.parts for excluded in exclude_dirs):
            continue
        python_files.append(path)
    return python_files

def fix_whitespace_issues(file_path: Path) -> Tuple[int, int, int]:
    """Fix whitespace issues in a Python file and return count of fixes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print(f"Error: Could not decode {file_path}. Skipping.")
        return 0, 0, 0
    
    # Count of fixes made
    trailing_whitespace_fixes = 0
    blank_line_whitespace_fixes = 0
    no_newline_end_of_file_fixes = 0
    
    # Fix whitespace issues
    fixed_lines = []
    for line in lines:
        # Check for blank line with whitespace (W293)
        if re.match(r'^\s+$', line):
            fixed_lines.append('\n')
            blank_line_whitespace_fixes += 1
        else:
            # Check for trailing whitespace (W291)
            stripped_line = re.sub(r'[ \t]+$', '', line)
            if stripped_line != line:
                trailing_whitespace_fixes += 1
            fixed_lines.append(stripped_line)
    
    # Check for missing newline at end of file (W292)
    if fixed_lines and not fixed_lines[-1].endswith('\n'):
        fixed_lines[-1] = fixed_lines[-1] + '\n'
        no_newline_end_of_file_fixes = 1
    
    # Only write if changes were made
    if trailing_whitespace_fixes > 0 or blank_line_whitespace_fixes > 0 or no_newline_end_of_file_fixes > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(fixed_lines)
    
    return trailing_whitespace_fixes, blank_line_whitespace_fixes, no_newline_end_of_file_fixes

def main():
    parser = argparse.ArgumentParser(description='Fix whitespace issues in Python files')
    parser.add_argument('--dir', type=str, nargs='+',
                        default=[
                            '/Users/femi/Documents/civai/cursor-agent/cursor_agent_tools',
                            '/Users/femi/Documents/civai/cursor-agent/tests'
                        ],
                        help='Root directories to search for Python files')
    parser.add_argument('--exclude', type=str, nargs='*', 
                        help='Additional directories to exclude')
    parser.add_argument('--check', action='store_true',
                        help='Check for whitespace issues without fixing them')
    args = parser.parse_args()
    
    root_dirs = args.dir
    exclude_dirs = {'venv', '.venv', '__pycache__', '.git', '.pytest_cache', '.mypy_cache'}
    
    if args.exclude:
        exclude_dirs.update(args.exclude)
    
    total_trailing_whitespace_fixes = 0
    total_blank_line_whitespace_fixes = 0
    total_newline_end_of_file_fixes = 0
    files_with_issues = 0
    total_files_scanned = 0
    
    for root_dir in root_dirs:
        print(f"Searching for Python files in {root_dir}...")
        python_files = find_python_files(root_dir, exclude_dirs)
        total_files_scanned += len(python_files)
        print(f"Found {len(python_files)} Python files")
        
        for file_path in python_files:
            trailing_fixes, blank_line_fixes, newline_fixes = fix_whitespace_issues(file_path)
            
            if trailing_fixes > 0 or blank_line_fixes > 0 or newline_fixes > 0:
                files_with_issues += 1
                if args.check:
                    print(f"Issues found in {file_path}: {trailing_fixes} trailing whitespace, {blank_line_fixes} blank line whitespace, {newline_fixes} missing final newline")
                else:
                    print(f"Fixed in {file_path}: {trailing_fixes} trailing whitespace, {blank_line_fixes} blank line whitespace, {newline_fixes} missing final newline")
            
            total_trailing_whitespace_fixes += trailing_fixes
            total_blank_line_whitespace_fixes += blank_line_fixes
            total_newline_end_of_file_fixes += newline_fixes
    
    print("\nSummary:")
    print(f"Files scanned: {total_files_scanned}")
    print(f"Files with whitespace issues: {files_with_issues}")
    print(f"Total trailing whitespace issues (W291): {total_trailing_whitespace_fixes}")
    print(f"Total blank line whitespace issues (W293): {total_blank_line_whitespace_fixes}")
    print(f"Total missing newline at EOF issues (W292): {total_newline_end_of_file_fixes}")
    
    if args.check:
        # Return non-zero exit code if issues were found
        return 1 if files_with_issues > 0 else 0
    
    return 0

if __name__ == "__main__":
    exit(main()) 