#!/usr/bin/env python3
"""
Command-line interface for Lang Select.
"""

import os
import sys
import argparse
import json
from typing import List, Optional, Dict, Any

from .parser import extract_items, SelectableItem
from .selector import select_item, select_with_external


def read_file(file_path: str) -> str:
    """Read the contents of a file and return as a string"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        sys.exit(1)


def read_stdin() -> str:
    """Read content from stdin"""
    if sys.stdin.isatty():
        print("Error: No input provided on stdin", file=sys.stderr)
        sys.exit(1)
    return sys.stdin.read()


def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="Extract and select items from language model responses")
    parser.add_argument("file", nargs="?", default="-", 
                        help="Path to the file containing LM response (use '-' for stdin)")
    parser.add_argument("--tool", choices=["auto", "fzf", "gum", "peco", "internal"],
                        default="auto", help="Selection tool to use")
    parser.add_argument("--debug", action="store_true", help="Enable debug output")
    parser.add_argument("--print-only", action="store_true", 
                       help="Only print the parsed items without interactive selection")
    parser.add_argument("--json", action="store_true",
                       help="Output result as JSON (useful for scripting)")
    parser.add_argument("--recent", type=str, 
                       help="Path to a file that stores the most recent response")
    parser.add_argument("--save-recent", type=str,
                       help="Save the current input to the specified file for future use")
    args = parser.parse_args()
    
    # Read the input
    if args.recent and os.path.exists(args.recent):
        # Prioritize the recent file if specified
        text = read_file(args.recent)
    elif args.file == "-":
        text = read_stdin()
    else:
        # Check if file exists
        if not os.path.isfile(args.file):
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            sys.exit(1)
        text = read_file(args.file)
    
    # Save to recent file if requested
    if args.save_recent:
        try:
            with open(args.save_recent, 'w', encoding='utf-8') as f:
                f.write(text)
            if args.debug:
                print(f"Saved input to recent file: {args.save_recent}", file=sys.stderr)
        except Exception as e:
            print(f"Error saving to recent file: {e}", file=sys.stderr)
    
    # Extract items
    items = extract_items(text)
    
    # If no items found
    if not items:
        print("No selectable items found in the response.", file=sys.stderr)
        sys.exit(0)
    
    # Print-only mode
    if args.print_only:
        print(f"Found {len(items)} selectable items:")
        for item in items:
            print(f"{item}")
        return 0
    
    # Debug output
    if args.debug:
        print(f"Found {len(items)} selectable items:", file=sys.stderr)
        for item in items:
            marker = f" (original: {item.original_marker})" if item.original_marker else ""
            print(f"  {item.id}. {item.content}{marker}", file=sys.stderr)
    
    # Select an item
    if args.tool == "internal":
        selected = select_item(items, "Choose an option from the list")
    else:
        selected = select_with_external(items, args.tool, "Choose an option from the list")
    
    # Return the result
    if selected:
        if args.json:
            print(json.dumps(selected.to_dict()))
        else:
            print(f"{selected.content}")
        return 0
    else:
        print("No selection made", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main()) 