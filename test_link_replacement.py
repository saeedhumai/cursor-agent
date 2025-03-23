import re

# Sample README content with various link types
sample_readme = """
# Test README

- [Regular file link](file.md)
- [Directory link](directory/)
- [Directory without trailing slash](examples)
- [Subdirectory file](examples/file.md)
- [Link with anchor](file.md#section)
- [Absolute URL](https://github.com/user/repo)
- [Link with parameters](file.md?param=value)
- Image: ![image](image.png)
"""

# Replace relative links with absolute GitHub URLs
repo_url = "https://github.com/civai-technologies/cursor-agent"
branch = "main"

print("=== ORIGINAL README ===")
print(sample_readme)

# Process in this order:
# 1. First handle image links separately (which use ![ syntax)
img_pattern = r'!\[([^\]]+)\]\((?!https?://)([^)]+)\)'
img_replacement = lambda m: f'![{m.group(1)}]({repo_url}/raw/{branch}/{m.group(2)})'
result1 = re.sub(img_pattern, img_replacement, sample_readme)

print("\n=== AFTER IMAGE REPLACEMENT ===")
print(result1)

# 2. Replace directory links (paths ending with /)
dir_with_slash_pattern = r'\[([^\]]+)\]\((?!https?://|#)([^)]+/)\)'
dir_with_slash_replacement = lambda m: f'[{m.group(1)}]({repo_url}/tree/{branch}/{m.group(2)})'
result2 = re.sub(dir_with_slash_pattern, dir_with_slash_replacement, result1)

print("\n=== AFTER DIRECTORY WITH SLASH REPLACEMENT ===")
print(result2)

# 3. Replace directory links without trailing slash - looking for directories referenced in the TOC
dir_pattern = r'\[([^\]]+)\]\((?!https?://|#)([^.)]+)\)'
dir_replacement = lambda m: f'[{m.group(1)}]({repo_url}/tree/{branch}/{m.group(2)})'
result3 = re.sub(dir_pattern, dir_replacement, result2)

print("\n=== AFTER DIRECTORY WITHOUT SLASH REPLACEMENT ===")
print(result3)

# 4. Finally replace remaining file links
file_pattern = r'\[([^\]]+)\]\((?!https?://|#)([^)]+\.[a-zA-Z0-9]+[^)]*)\)'
file_replacement = lambda m: f'[{m.group(1)}]({repo_url}/blob/{branch}/{m.group(2)})'
final_result = re.sub(file_pattern, file_replacement, result3)

print("\n=== FINAL RESULT ===")
print(final_result) 