#!/usr/bin/env python3
"""
Command line interface for the lang-select tool.
"""

import os
import sys
import argparse
import json
from typing import Optional, List, Dict, Any

try:
    import rich_click as click
    from rich.console import Console
    RICH_AVAILABLE = True
except ImportError:
    try:
        import click
    except ImportError:
        click = None
    RICH_AVAILABLE = False

# Check if textual is available (only used for feature detection, not imported)
try:
    import textual
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

from .parser import extract_items, SelectableItem
from .selector import select_with_external
from .enhanced_extractor import extract_enhanced_items

# Import our new formatters
try:
    from .formatter import create_formatter
    FORMATTERS_AVAILABLE = True
except ImportError:
    FORMATTERS_AVAILABLE = False


def read_file(path: str) -> str:
    """Read text from a file"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {path}: {e}", file=sys.stderr)
        sys.exit(1)


def read_stdin() -> str:
    """Read text from stdin"""
    try:
        return sys.stdin.read()
    except Exception as e:
        print(f"Error reading from stdin: {e}", file=sys.stderr)
        sys.exit(1)


if click:
    @click.command(help="Extract and select numbered or bulleted items from language model responses.")
    @click.argument('file', required=False, default="-", 
                   help="File containing the LM response, or - for stdin (default: -)")
    @click.option('--tool', type=str, default="auto", 
                  help="Selection tool to use (auto, internal, fzf, gum, peco, overlay)")
    @click.option('--debug/--no-debug', default=False, 
                  help="Enable debug output")
    @click.option('--print-only/--no-print-only', default=False, 
                  help="Only print the extracted items without selection")
    @click.option('--json/--no-json', 'json_output', default=False, 
                  help="Output as JSON")
    @click.option('--recent', type=str, 
                  help="Path to a file that stores the most recent response")
    @click.option('--save-recent', type=str, 
                  help="Save the current input to the specified file for future use")
    @click.option('--overlay/--no-overlay', default=False,
                  help="Use terminal overlay selection (requires textual package)")
    @click.option('--capture-terminal/--no-capture-terminal', default=False,
                  help="Capture terminal content and select from it (requires textual package)")
    @click.option('--multi/--no-multi', default=False,
                  help="Enable multi-selection mode")
    @click.option('--enhanced/--no-enhanced', default=False,
                  help="Use enhanced extraction with support for hierarchies and sections")
    @click.option('--view', type=click.Choice(['flat', 'hierarchy', 'mixed']), default='flat',
                  help="Choose display style for extracted items (requires enhanced extraction)")
    @click.option('--no-color/--color', 'use_color', default=True,
                  help="Disable colored output")
    def main(file: str, tool: str, debug: bool, print_only: bool, json_output: bool, 
             recent: Optional[str] = None, save_recent: Optional[str] = None,
             overlay: bool = False, capture_terminal: bool = False,
             multi: bool = False, enhanced: bool = False,
             view: str = 'flat', use_color: bool = True) -> None:
        """Main entry point for the script"""
        # Handle overlay option
        if overlay:
            if not TEXTUAL_AVAILABLE:
                print("Terminal overlay selection requires textual. Install with:")
                print("pip install lang-select[textual]")
                sys.exit(1)
            tool = "overlay"
            
        # Handle terminal capture option
        if capture_terminal:
            if not TEXTUAL_AVAILABLE:
                print("Terminal capture requires textual. Install with:")
                print("pip install lang-select[textual]")
                sys.exit(1)
                
            from .selector import select_from_terminal
            selected = select_from_terminal()
            if selected:
                print(selected.content)
            sys.exit(0)
        
        # Use the recent file if specified
        if recent and os.path.exists(recent):
            text = read_file(recent)
        elif file == "-":
            text = read_stdin()
        else:
            text = read_file(file)
            
        # Save to recent file if specified
        if save_recent:
            try:
                with open(save_recent, 'w', encoding='utf-8') as f:
                    f.write(text)
            except Exception as e:
                print(f"Error saving to recent file {save_recent}: {e}", file=sys.stderr)
        
        # Set enhanced mode if view is hierarchy or mixed
        if view in ['hierarchy', 'mixed'] and not enhanced:
            enhanced = True
            if debug:
                print(f"Setting enhanced mode to True because view mode is {view}")
        
        # Extract items from the text
        if enhanced:
            items = extract_enhanced_items(text)
        else:
            items = extract_items(text)
        
        if not items:
            if json_output:
                print(json.dumps({"success": False, "error": "No selectable items found in the text"}))
            else:
                print("No selectable items found in the text", file=sys.stderr)
            sys.exit(1)
            
        if debug:
            print(f"Found {len(items)} selectable items:")
            for item in items:
                original = f"(original: {item.original_marker})" if item.original_marker else ""
                section = f"[section: {item.section}]" if hasattr(item, 'section') and item.section else ""
                level = f"[level: {item.level}]" if hasattr(item, 'level') and item.level > 0 else ""
                parent = f"[parent: {item.parent_id}]" if hasattr(item, 'parent_id') and item.parent_id else ""
                print(f"  {item.id}. {item.content} {original} {section} {level} {parent}".strip())
                
        if print_only:
            # Use formatters if available and enhanced mode is on
            if FORMATTERS_AVAILABLE and enhanced:
                formatter = create_formatter(view, use_color)
                print(formatter.format_items(items))
            else:
                # Fallback to simple printing
                for item in items:
                    prefix = f"[{item.section}] " if hasattr(item, 'section') and item.section else ""
                    indent = "  " * getattr(item, 'level', 0) if hasattr(item, 'level') else ""
                    print(f"{indent}• {prefix}{item.content}")
            sys.exit(0)
            
        # Select item(s)
        selected = select_with_external(items, tool=tool, multi_select=multi)
        
        if selected:
            if json_output:
                if multi:
                    result = {
                        "success": True,
                        "selected": [
                            {
                                "id": item.id,
                                "content": item.content,
                                "original_marker": item.original_marker
                            }
                            for item in selected
                        ]
                    }
                else:
                    result = {
                        "success": True, 
                        "selected": {
                            "id": selected.id,
                            "content": selected.content,
                            "original_marker": selected.original_marker
                        }
                    }
                print(json.dumps(result))
            else:
                if multi:
                    for item in selected:
                        print(item.content)
                else:
                    print(selected.content)
        else:
            if json_output:
                print(json.dumps({"success": False, "error": "No selection made"}))
            else:
                print("No selection made", file=sys.stderr)
            sys.exit(1)
else:
    def main() -> None:
        """Fallback when click is not available"""
        parser = argparse.ArgumentParser(
            description="Extract and select numbered or bulleted items from language model responses."
        )
        parser.add_argument('file', nargs='?', default="-", 
                          help="File containing the LM response, or - for stdin (default: -)")
        parser.add_argument('--tool', type=str, default="auto", 
                          help="Selection tool to use (auto, internal, fzf, gum, peco, overlay)")
        parser.add_argument('--debug', action='store_true', 
                          help="Enable debug output")
        parser.add_argument('--print-only', action='store_true', 
                          help="Only print the extracted items without selection")
        parser.add_argument('--json', action='store_true', 
                          help="Output as JSON")
        parser.add_argument('--recent', type=str, 
                          help="Path to a file that stores the most recent response")
        parser.add_argument('--save-recent', type=str, 
                          help="Save the current input to the specified file for future use")
        parser.add_argument('--overlay', action='store_true',
                          help="Use terminal overlay selection (requires textual package)")
        parser.add_argument('--capture-terminal', action='store_true',
                          help="Capture terminal content and select from it (requires textual package)")
        parser.add_argument('--multi', action='store_true',
                          help="Enable multi-selection mode")
        parser.add_argument('--enhanced', action='store_true',
                          help="Use enhanced extraction with support for hierarchies and sections")
        parser.add_argument('--view', choices=['flat', 'hierarchy', 'mixed'], default='flat',
                          help="Choose display style for extracted items (requires enhanced extraction)")
        parser.add_argument('--no-color', dest='use_color', action='store_false',
                          help="Disable colored output")
                          
        args = parser.parse_args()
        
        # Handle overlay option
        if args.overlay:
            if not TEXTUAL_AVAILABLE:
                print("Terminal overlay selection requires textual. Install with:")
                print("pip install lang-select[textual]")
                sys.exit(1)
            args.tool = "overlay"
            
        # Handle terminal capture option
        if args.capture_terminal:
            if not TEXTUAL_AVAILABLE:
                print("Terminal capture requires textual. Install with:")
                print("pip install lang-select[textual]")
                sys.exit(1)
                
            from .selector import select_from_terminal
            selected = select_from_terminal()
            if selected:
                print(selected.content)
            sys.exit(0)
        
        # Set enhanced mode if view is hierarchy or mixed
        if args.view in ['hierarchy', 'mixed'] and not args.enhanced:
            args.enhanced = True
            if args.debug:
                print(f"Setting enhanced mode to True because view mode is {args.view}")
        
        # Use the recent file if specified
        if args.recent and os.path.exists(args.recent):
            text = read_file(args.recent)
        elif args.file == "-":
            text = read_stdin()
        else:
            text = read_file(args.file)
            
        # Save to recent file if specified
        if args.save_recent:
            try:
                with open(args.save_recent, 'w', encoding='utf-8') as f:
                    f.write(text)
            except Exception as e:
                print(f"Error saving to recent file {args.save_recent}: {e}", file=sys.stderr)
        
        # Extract items from the text
        if args.enhanced:
            items = extract_enhanced_items(text)
        else:
            items = extract_items(text)
        
        if not items:
            if args.json:
                print(json.dumps({"success": False, "error": "No selectable items found in the text"}))
            else:
                print("No selectable items found in the text", file=sys.stderr)
            sys.exit(1)
            
        if args.debug:
            print(f"Found {len(items)} selectable items:")
            for item in items:
                original = f"(original: {item.original_marker})" if item.original_marker else ""
                section = f"[section: {item.section}]" if hasattr(item, 'section') and item.section else ""
                level = f"[level: {item.level}]" if hasattr(item, 'level') and item.level > 0 else ""
                parent = f"[parent: {item.parent_id}]" if hasattr(item, 'parent_id') and item.parent_id else ""
                print(f"  {item.id}. {item.content} {original} {section} {level} {parent}".strip())
                
        if args.print_only:
            # Use formatters if available and enhanced mode is on
            if FORMATTERS_AVAILABLE and args.enhanced:
                formatter = create_formatter(args.view, args.use_color)
                print(formatter.format_items(items))
            else:
                # Fallback to simple printing
                for item in items:
                    prefix = f"[{item.section}] " if hasattr(item, 'section') and item.section else ""
                    indent = "  " * getattr(item, 'level', 0) if hasattr(item, 'level') else ""
                    print(f"{indent}• {prefix}{item.content}")
            sys.exit(0)
            
        # Select item(s)
        selected = select_with_external(items, tool=args.tool, multi_select=args.multi)
        
        if selected:
            if args.json:
                if args.multi:
                    result = {
                        "success": True,
                        "selected": [
                            {
                                "id": item.id,
                                "content": item.content,
                                "original_marker": item.original_marker
                            }
                            for item in selected
                        ]
                    }
                else:
                    result = {
                        "success": True, 
                        "selected": {
                            "id": selected.id,
                            "content": selected.content,
                            "original_marker": selected.original_marker
                        }
                    }
                print(json.dumps(result))
            else:
                if args.multi:
                    for item in selected:
                        print(item.content)
                else:
                    print(selected.content)
        else:
            if args.json:
                print(json.dumps({"success": False, "error": "No selection made"}))
            else:
                print("No selection made", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main() 