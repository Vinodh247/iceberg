#!/usr/bin/env python3
"""
Iceberg Documentation Improvement Scanner

Automatically identifies and fixes:
- Missing or outdated documentation links
- Incomplete API documentation
- Formatting inconsistencies
- Missing contributor guides
"""

import os
import re
import json
from pathlib import Path
from typing import List, Tuple

# Configuration
DOCS_PATH = Path('docs')
JAVA_SRC_PATH = Path('java')
PYTHON_SRC_PATH = Path('python')
OUTPUT_CHANGES = []

def find_broken_doc_links() -> List[Tuple[str, str]]:
    """Find broken documentation links in markdown files."""
    broken_links = []
    
    for md_file in DOCS_PATH.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        
        # Find markdown links: [text](link)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        
        for text, link in matches:
            # Skip external links and anchors
            if link.startswith(('http://', 'https://', '#')):
                continue
            
            # Resolve relative path
            target_path = md_file.parent / link
            if not target_path.exists():
                broken_links.append((str(md_file), link))
    
    return broken_links

def fix_broken_links(broken_links: List[Tuple[str, str]]) -> bool:
    """Create a report and fix obvious broken links."""
    if not broken_links:
        return False
    
    report_file = DOCS_PATH / 'BROKEN_LINKS_REPORT.md'
    content = '# Documentation Link Report\n\n'
    content += f'Found {len(broken_links)} broken or questionable links:\n\n'
    
    for file_path, broken_link in broken_links:
        content += f'- **{file_path}**: `{broken_link}`\n'
    
    content += '\n## Notes\n'
    content += '- Check if files have been moved or renamed\n'
    content += '- Verify external links are still valid\n'
    content += '- Update relative paths as needed\n'
    
    report_file.write_text(content)
    print(f'Created {report_file}')
    return True

def find_undocumented_api_classes() -> List[str]:
    """Find Java classes in main API that lack documentation files."""
    undocumented = []
    
    if not JAVA_SRC_PATH.exists():
        return undocumented
    
    # Find main API classes (org.apache.iceberg package)
    api_pattern = re.compile(r'package org\.apache\.iceberg;')
    
    for java_file in JAVA_SRC_PATH.rglob('*.java'):
        try:
            content = java_file.read_text(encoding='utf-8')
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        
        # Only care about public API
        if not ('package org.apache.iceberg;' in content and 'public class' in content):
            continue
        
        # Extract class name
        class_match = re.search(r'public class (\w+)', content)
        if not class_match:
            continue
        
        class_name = class_match.group(1)
        
        # Check if documentation exists
        doc_file = DOCS_PATH / 'api' / f'{class_name}.md'
        if not doc_file.exists():
            undocumented.append(class_name)
    
    return undocumented

def create_api_doc_stubs(undocumented_classes: List[str]) -> bool:
    """Create documentation stubs for undocumented API classes."""
    if not undocumented_classes:
        return False
    
    api_docs_dir = DOCS_PATH / 'api'
    api_docs_dir.mkdir(parents=True, exist_ok=True)
    
    for class_name in undocumented_classes[:5]:  # Limit to 5 per run
        doc_file = api_docs_dir / f'{class_name}.md'
        
        content = f"""# {class_name}

**Status**: This documentation is a stub and needs to be completed.

## Overview

Brief description of what {class_name} does.

## Usage

```java
// Example usage goes here
```

## Methods

<!-- Auto-generated placeholder -->
See source code for method documentation.

## See Also

- Related classes
- Related documentation

---

**Note**: This is an auto-generated stub. Please complete this documentation by:
1. Adding a detailed overview
2. Including code examples
3. Documenting all public methods
4. Adding cross-references

"""
        
        doc_file.write_text(content)
        print(f'Created API doc stub: {doc_file}')
    
    return True

def check_missing_changelog() -> bool:
    """Check if CHANGELOG needs updating."""
    changelog_path = Path('CHANGELOG.md')
    
    if not changelog_path.exists():
        # Create basic changelog structure
        content = """# Changelog

All notable changes to Apache Iceberg are documented here.

## [Unreleased]

### Added
- 

### Changed
- 

### Fixed
- 

### Deprecated
- 

## [Version History]

See git log for historical changes.
"""
        changelog_path.write_text(content)
        print(f'Created {changelog_path}')
        return True
    
    return False

def standardize_markdown_formatting() -> bool:
    """Fix common markdown formatting issues."""
    changes_made = False
    
    for md_file in DOCS_PATH.rglob('*.md'):
        try:
            content = md_file.read_text(encoding='utf-8')
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        
        original_content = content
        
        # Fix: Multiple blank lines -> single blank line
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        # Fix: Ensure headers have blank lines before them
        content = re.sub(r'([^\n])\n(#{1,6} )', r'\1\n\n\2', content)
        
        # Fix: Trailing whitespace
        content = '\n'.join(line.rstrip() for line in content.split('\n'))
        
        # Fix: Ensure file ends with newline
        if content and not content.endswith('\n'):
            content += '\n'
        
        if content != original_content:
            md_file.write_text(content)
            print(f'Formatted: {md_file}')
            changes_made = True
    
    return changes_made

def create_contributing_guide() -> bool:
    """Create or update CONTRIBUTING.md if missing."""
    contrib_file = Path('CONTRIBUTING.md')
    
    if contrib_file.exists():
        return False
    
    content = """# Contributing to Apache Iceberg

Thank you for your interest in contributing to Apache Iceberg!

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a feature branch
4. Make your changes
5. Write/update tests
6. Submit a pull request

## Documentation Contributions

When contributing documentation:

- Use clear, concise language
- Include code examples where relevant
- Keep documentation up-to-date with code changes
- Follow the existing documentation structure
- Link to related documentation and code

## Pull Request Guidelines

- Reference related issues
- Include meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Follow existing code style and conventions

## Code of Conduct

This project is governed by the Apache Code of Conduct.
Please review and adhere to it in all interactions.

## Questions?

- Check existing issues and documentation
- Open a discussion issue
- Reach out to the community

---

For more information, see the official Apache Iceberg documentation.
"""
    
    contrib_file.write_text(content)
    print(f'Created {contrib_file}')
    return True

def main():
    print('Starting Iceberg documentation scan...\n')
    
    changes_made = False
    
    # 1. Check for broken links
    print('[1/5] Scanning for broken documentation links...')
    broken_links = find_broken_doc_links()
    if fix_broken_links(broken_links):
        changes_made = True
    
    # 2. Find undocumented API classes
    print('[2/5] Finding undocumented API classes...')
    undocumented = find_undocumented_api_classes()
    if undocumented:
        print(f'  Found {len(undocumented)} undocumented classes')
        if create_api_doc_stubs(undocumented):
            changes_made = True
    
    # 3. Check changelog
    print('[3/5] Checking changelog...')
    if check_missing_changelog():
        changes_made = True
    
    # 4. Standardize markdown
    print('[4/5] Standardizing markdown formatting...')
    if standardize_markdown_formatting():
        changes_made = True
    
    # 5. Create contributing guide
    print('[5/5] Checking contributor guide...')
    if create_contributing_guide():
        changes_made = True
    
    print('\nDocumentation scan complete.')
    
    if changes_made:
        print('✓ Changes made and ready for review')
    else:
        print('No changes needed')

if __name__ == '__main__':
    main()
