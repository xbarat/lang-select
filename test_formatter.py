#!/usr/bin/env python3
"""
Test script for the formatter classes.

This script tests the hierarchical formatting and colorized output
of the formatter classes using a sample text with various list formats.
"""

import sys
import os
from typing import List, Dict, Any, Optional

# Add parent directory to the path so we can import from lang_select
sys.path.insert(0, os.path.abspath('.'))

from lang_select.enhanced_extractor import EnhancedExtractor, ExtendedSelectableItem
from lang_select.formatter import (
    FormatterBase, FlatFormatter, HierarchicalFormatter, 
    MixedFormatter, create_formatter
)

# Sample text with mixed formats and hierarchical structure
SAMPLE_TEXT = """
# Project Plan

## Design Phase
1. Create wireframes
   - Mobile version
   - Desktop version
2. Design database schema
   - User table
   - Product table
   - Order table
3. Choose color palette

## Development Phase
* Setup project repository
* Implement core features
  * User authentication
    * Login
    * Registration
    * Password reset
  * Data storage
  * API endpoints
* Create user interface

## Testing Phase
- Unit tests
- Integration tests
- User acceptance testing

**Additional Notes**:
This is a preliminary plan and might change as the project progresses.
"""

def print_separator():
    """Print a separator line"""
    print("\n" + "=" * 50 + "\n")

def test_formatters():
    """Test all formatter classes with sample text"""
    print("Testing lang_select formatters with sample hierarchical text\n")
    
    # Extract items from the sample text
    extractor = EnhancedExtractor()
    items = extractor.extract_items(SAMPLE_TEXT)
    
    if not items:
        print("No items extracted from the sample text")
        return
    
    print(f"Extracted {len(items)} items from the sample text")
    
    # Test flat formatter
    print_separator()
    print("FLAT FORMATTER (with sections shown in brackets):")
    flat_formatter = FlatFormatter()
    flat_output = flat_formatter.format_items(items)
    print(flat_output)
    
    # Test hierarchical formatter
    print_separator()
    print("HIERARCHICAL FORMATTER (with indented structure):")
    hierarchical_formatter = HierarchicalFormatter()
    hierarchical_output = hierarchical_formatter.format_items(items)
    print(hierarchical_output)
    
    # Test mixed formatter
    print_separator()
    print("MIXED FORMATTER (numbered top-level items with bulleted children):")
    mixed_formatter = MixedFormatter()
    mixed_output = mixed_formatter.format_items(items)
    print(mixed_output)
    
    # Test factory function
    print_separator()
    print("FORMATTER FACTORY (create_formatter):")
    for style in ["flat", "hierarchy", "mixed"]:
        print(f"\n{style.upper()} style via factory:")
        formatter = create_formatter(style)
        # Only print first few lines to save space
        output = formatter.format_items(items).split('\n')
        print('\n'.join(output[:min(5, len(output))]) + "\n...")
    
    # Test markdown escaping
    print_separator()
    print("MARKDOWN ESCAPING TEST:")
    
    # Create a sample item with markdown
    markdown_item = ExtendedSelectableItem(
        id=1,
        content="This has **bold** and *italic* text with `code` and # headers",
        section="Markdown Test"
    )
    
    flat_formatter = FlatFormatter()
    print(flat_formatter.format_items([markdown_item]))

if __name__ == "__main__":
    test_formatters() 