#!/usr/bin/env python3
"""
Example usage of the lang_select package
"""

import os
import sys
import argparse
from lang_select import extract_items, select_item, select_with_external


def read_file(file_path):
    """Read file contents"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def main():
    """Example main function"""
    parser = argparse.ArgumentParser(description="Lang-Select Example Usage")
    parser.add_argument("file", help="Path to LM response file")
    parser.add_argument("--tool", choices=["internal", "fzf", "gum", "peco", "auto"], 
                       default="auto", help="Selection tool to use")
    args = parser.parse_args()
    
    # Read the input file
    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        return 1
    
    text = read_file(args.file)
    
    # Extract items from the text
    items = extract_items(text)
    
    if not items:
        print("No items found in the input text")
        return 1
    
    print(f"Found {len(items)} items:")
    for item in items:
        print(f"  {item.id}. {item.content}")
    
    # Select an item
    print("\nNow let's select an item:")
    if args.tool == "internal":
        selected = select_item(items, "Choose an item from the list")
    else:
        selected = select_with_external(items, tool=args.tool, prompt="Choose an item")
    
    # Do something with the selected item
    if selected:
        print(f"\nYou selected: {selected.content}")
        
        # Example of using the selected item as input to another process
        print(f"\nThis is where you might use this selection for further processing.")
        print(f"For example, you could use it as input to another tool:")
        print(f"  $ some-other-tool --input \"{selected.content}\"")
    else:
        print("\nNo selection made")
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 