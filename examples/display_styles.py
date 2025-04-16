#!/usr/bin/env python3
"""
This example demonstrates the different display styles available for formatting extracted items.

It shows how to use the flat, hierarchical, and mixed formatters to display items
extracted from an LLM response in different ways.
"""

import sys
import os

# Add the parent directory to the path so we can import from lang_select
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lang_select.enhanced_extractor import extract_enhanced_items
from lang_select.formatter import (
    create_formatter, 
    FlatFormatter, 
    HierarchicalFormatter, 
    MixedFormatter
)

# Sample LLM response with hierarchical content
SAMPLE_RESPONSE = """
Here's a plan for implementing a task management system:

# Architecture

## Backend Components
1. RESTful API
   - User authentication endpoints
   - Task CRUD operations
   - Notification system
2. Database schema
   - User table
   - Tasks table
   - Categories table
   - Tags table
3. Background job processor
   - Email notifications
   - Data aggregation
   - Scheduled tasks

## Frontend Components
* User interface
  * Dashboard view
  * Task list view
  * Calendar view
* State management
* API integration layer

# Implementation Plan

## Phase 1: MVP
- User authentication
- Basic task creation and management
- Simple list view

## Phase 2: Enhanced Features
- Categories and tags
- Search and filtering
- Calendar integration

## Phase 3: Advanced Features
- Recurring tasks
- Team collaboration
- Analytics dashboard

Would you like me to elaborate on any specific component?
"""

def main():
    """
    Main function to demonstrate the different display styles
    """
    print("Extracting items from LLM response...\n")
    
    # Extract items from the sample response
    items = extract_enhanced_items(SAMPLE_RESPONSE)
    
    if not items:
        print("No items extracted from the response!")
        return
    
    print(f"Extracted {len(items)} items\n")
    
    # Demonstrate each formatting style
    print("=" * 60)
    print("FLAT STYLE (with section labels)")
    print("=" * 60)
    
    flat_formatter = FlatFormatter()
    print(flat_formatter.format_items(items))
    
    print("\n" + "=" * 60)
    print("HIERARCHICAL STYLE (with indentation and different bullets)")
    print("=" * 60)
    
    hierarchical_formatter = HierarchicalFormatter()
    print(hierarchical_formatter.format_items(items))
    
    print("\n" + "=" * 60)
    print("MIXED STYLE (numbered top-level items with bulleted children)")
    print("=" * 60)
    
    mixed_formatter = MixedFormatter()
    print(mixed_formatter.format_items(items))
    
    # Example of using the formatter factory
    print("\n" + "=" * 60)
    print("CREATING FORMATTERS WITH THE FACTORY FUNCTION")
    print("=" * 60)
    
    for style in ['flat', 'hierarchy', 'mixed']:
        formatter = create_formatter(style)
        print(f"\nUsing create_formatter('{style}'):")
        # Just print the first few lines to show it works
        formatted = formatter.format_items(items).split('\n')
        print('\n'.join(formatted[:5]) + "\n...")
    
    # Example of using with color vs. without color
    print("\n" + "=" * 60)
    print("COLOR VS NO COLOR (first few lines of each)")
    print("=" * 60)
    
    color_formatter = create_formatter('hierarchy', use_color=True)
    no_color_formatter = create_formatter('hierarchy', use_color=False)
    
    print("\nWith color:")
    formatted = color_formatter.format_items(items).split('\n')
    print('\n'.join(formatted[:5]) + "\n...")
    
    print("\nWithout color:")
    formatted = no_color_formatter.format_items(items).split('\n')
    print('\n'.join(formatted[:5]) + "\n...")

if __name__ == "__main__":
    main() 