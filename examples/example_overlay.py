#!/usr/bin/env python3
"""
Example demonstrating the overlay functionality of lang-select.

This example shows how to use the terminal overlay for selection.
To run this example, you need to install the textual package:

    pip install textual

Or install lang-select with the textual extra:

    pip install lang-select[textual]
"""

import sys
import time
from lang_select import (
    quick_overlay_select,
    is_overlay_available,
    ResponseManager,
    quick_select
)

# Sample LLM response with selectable items
SAMPLE_RESPONSE = """
Here are the steps to complete the project:

1. Set up the development environment
2. Create the project structure
3. Implement the core functionality
4. Write unit tests
5. Add documentation
6. Set up CI/CD pipeline
7. Deploy to production
8. Monitor and maintain

Let me know if you have any questions!
"""


def example_1_basic_overlay():
    """Basic example of using the overlay selector"""
    print("\n--- Example 1: Basic Overlay Selection ---")
    
    if not is_overlay_available():
        print("This example requires textual to be installed.")
        print("Install with: pip install textual")
        return
        
    print("Selecting from a sample LLM response...")
    print("The overlay will appear shortly...")
    time.sleep(1)  # Give time to read the instructions
    
    # Use the overlay to select from the sample response
    selected = quick_overlay_select(SAMPLE_RESPONSE)
    
    if selected:
        print(f"\nYou selected: {selected}")
    else:
        print("\nNo selection was made")


def example_2_response_manager():
    """Example using ResponseManager with overlay"""
    print("\n--- Example 2: Using ResponseManager with Overlay ---")
    
    if not is_overlay_available():
        print("This example requires textual to be installed.")
        print("Install with: pip install textual")
        return
        
    # Create a response manager
    manager = ResponseManager()
    
    # Store a response
    manager.store(SAMPLE_RESPONSE)
    
    print("Using ResponseManager with overlay...")
    print("The overlay will appear shortly...")
    time.sleep(1)  # Give time to read the instructions
    
    # Select with overlay
    selected = manager.select_with_overlay(feedback=True)
    
    if selected:
        # Get information about the selection
        info = manager.get_selection_info()
        print(f"\nSelection info: {info}")
        
        # Get a human-readable summary
        summary = manager.get_selection_summary()
        print(f"Summary: {summary}")
    else:
        print("\nNo selection was made")


def example_3_terminal_capture():
    """Example of capturing terminal content and selecting from it"""
    print("\n--- Example 3: Terminal Content Capture ---")
    
    if not is_overlay_available():
        print("This example requires textual to be installed.")
        print("Install with: pip install textual")
        return
    
    # Print some selectable content to the terminal
    print("Here are some options to select from:")
    print("1. Option One - This is the first option")
    print("2. Option Two - This is the second option")
    print("3. Option Three - This is the third option")
    print("4. Option Four - This is the fourth option")
    
    print("\nCapturing terminal content...")
    print("The overlay will appear shortly...")
    time.sleep(1)  # Give time to read the instructions
    
    # Capture terminal content and select from it
    selected = quick_overlay_select()
    
    if selected:
        print(f"\nYou selected: {selected}")
    else:
        print("\nNo selection was made")


def example_4_fallback():
    """Example demonstrating fallback to other selection tools"""
    print("\n--- Example 4: Fallback Selection ---")
    
    print("This example demonstrates selection with different tools")
    print("with automatic fallback if a tool is not available.")
    
    # Try to use overlay first, but fall back to other tools if not available
    selected = quick_select(
        SAMPLE_RESPONSE,
        tool="overlay",  # Will try overlay first
        on_success=lambda s: print(f"\nSelection successful: {s}"),
        on_cancel=lambda: print("\nSelection cancelled"),
        on_empty=lambda: print("\nNo items found to select from")
    )
    
    if selected:
        print(f"Selected: {selected}")


def main():
    """Run all examples"""
    print("Lang Select Overlay Examples")
    print("===========================")
    
    if not is_overlay_available():
        print("\nWARNING: Textual is not installed. Some examples may not work.")
        print("To install textual: pip install textual")
        print("Or: pip install lang-select[textual]")
    
    try:
        # Run all examples
        example_1_basic_overlay()
        example_2_response_manager()
        example_3_terminal_capture()
        example_4_fallback()
        
        print("\nAll examples completed!")
    except KeyboardInterrupt:
        print("\nExamples interrupted.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main()) 