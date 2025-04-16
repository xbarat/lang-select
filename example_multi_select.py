#!/usr/bin/env python3
"""
Example demonstrating the multi-selection functionality of lang-select.

This example shows how to use multi-selection with various selection tools.
"""

import sys
import time
from lang_select import (
    quick_select,
    quick_overlay_select,
    is_overlay_available,
    ResponseManager,
    extract_items,
    select_with_external
)

# Sample LLM response with selectable items
SAMPLE_RESPONSE = """
Here are the tasks you need to complete for the project:

1. Set up the project repository
2. Create the database schema
3. Implement user authentication
4. Design the UI/UX
5. Build the API endpoints
6. Write unit tests
7. Create documentation
8. Deploy to production

Please let me know which tasks you'd like to focus on first.
"""


def example_1_basic_multi_select():
    """Basic example of using multi-selection with quick_select"""
    print("\n--- Example 1: Basic Multi-Selection ---")
    
    print("Selecting multiple tasks from a sample LLM response...\n")
    
    # Extract and select multiple items using quick_select
    selected = quick_select(
        SAMPLE_RESPONSE, 
        tool="internal", 
        prompt="Select tasks to focus on first",
        multi_select=True
    )
    
    if selected:
        print(f"\nYou selected {len(selected)} tasks:")
        for i, task in enumerate(selected, 1):
            print(f"  {i}. {task}")
    else:
        print("\nNo tasks were selected")


def example_2_fzf_multi_select():
    """Example of using multi-selection with fzf"""
    print("\n--- Example 2: Multi-Selection with fzf ---")
    
    print("Selecting multiple tasks using fzf (use TAB to select, ENTER to confirm)...\n")
    
    # Extract items and use fzf directly
    items = extract_items(SAMPLE_RESPONSE)
    
    if not items:
        print("No items found!")
        return
        
    selected = select_with_external(
        items, 
        tool="fzf", 
        prompt="Select tasks with TAB key",
        multi_select=True
    )
    
    if selected:
        print(f"\nYou selected {len(selected)} tasks:")
        for item in selected:
            print(f"  - {item.content}")
    else:
        print("\nNo tasks were selected")


def example_3_response_manager():
    """Example of using multi-selection with ResponseManager"""
    print("\n--- Example 3: Multi-Selection with ResponseManager ---")
    
    manager = ResponseManager()
    manager.store(SAMPLE_RESPONSE)
    
    print("Using ResponseManager to select multiple tasks...\n")
    
    selected = manager.select(
        tool="internal", 
        prompt="Select tasks to assign",
        multi_select=True,
        feedback=True
    )
    
    # The manager.select() method already provides feedback, so we don't need to 
    # print the selection again here
    if not selected:
        print("\nNo tasks were assigned")


def example_4_overlay_multi_select():
    """Example of using multi-selection with textual overlay"""
    print("\n--- Example 4: Multi-Selection with Overlay ---")
    
    if not is_overlay_available():
        print("This example requires textual to be installed.")
        print("Install with: pip install textual")
        return
        
    print("Selecting tasks using the overlay selector...")
    print("The overlay will appear shortly...")
    time.sleep(1)  # Give time to read the instructions
    
    selected = quick_overlay_select(
        SAMPLE_RESPONSE,
        prompt="Select tasks for the sprint",
        multi_select=True
    )
    
    if selected:
        print(f"\nYou selected {len(selected)} tasks for the sprint:")
        for i, task in enumerate(selected, 1):
            print(f"  {i}. {task}")
    else:
        print("\nNo tasks were selected for the sprint")


def main():
    """Run all examples"""
    print("Lang Select Multi-Selection Examples")
    print("==================================")
    
    try:
        # Run the examples
        example_1_basic_multi_select()
        
        # Only run these if we're not in a testing environment
        if not any(arg in sys.argv for arg in ['-t', '--test']):
            example_2_fzf_multi_select()
            example_3_response_manager()
            example_4_overlay_multi_select()
        
        print("\nAll examples completed!")
    except KeyboardInterrupt:
        print("\nExamples interrupted.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main()) 