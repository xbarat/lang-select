"""
Selector module for interactive selection from extracted items.
"""

import os
import sys
import subprocess
import tempfile
from typing import List, Optional, Dict, Any, Union, Callable

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# Lazy import of textual_overlay to avoid import errors when not installed
TEXTUAL_AVAILABLE = False
try:
    # Just check if the import would work, but don't actually import yet
    import textual
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

from .parser import SelectableItem

# Try to import formatters if available
try:
    from .formatter import create_formatter, HierarchicalFormatter
    FORMATTERS_AVAILABLE = True
except ImportError:
    FORMATTERS_AVAILABLE = False


def select_item(items: List[SelectableItem], prompt_text: str = "Select an item", 
                multi_select: bool = False) -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """
    Display a list of items and let the user select one or more.
    If rich is available, uses rich UI, otherwise falls back to basic terminal UI.
    
    Args:
        items: List of SelectableItem objects
        prompt_text: Prompt text to display
        multi_select: Whether to allow multiple selections
        
    Returns:
        If multi_select is False: Selected item or None if selection was cancelled
        If multi_select is True: List of selected items or empty list if no selection was made
    """
    if not items:
        return [] if multi_select else None
    
    if RICH_AVAILABLE:
        return _select_with_rich(items, prompt_text, multi_select)
    else:
        return _select_basic(items, prompt_text, multi_select)


def _select_with_rich(items: List[SelectableItem], prompt_text: str, 
                     multi_select: bool = False) -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """Use rich for a nicer selection experience"""
    console = Console()
    
    if multi_select:
        console.print(Panel(f"[bold]{prompt_text}[/] (Enter numbers separated by spaces, or 'all' for all items)", 
                           box=box.ROUNDED, style="blue"))
    else:
        console.print(Panel(f"[bold]{prompt_text}[/] (Enter number or use arrow keys + Enter)", 
                           box=box.ROUNDED, style="blue"))
    
    # Display items - use formatters when available and items have hierarchy info
    if FORMATTERS_AVAILABLE and any(hasattr(item, 'level') for item in items):
        # Create a copy of each item that includes its ID in the content
        display_items = []
        for item in items:
            # Create a shallow copy of the item
            display_item = type(item)(
                id=item.id,
                content=f"[cyan]{item.id}.[/] {item.content}",
                original_marker=getattr(item, 'original_marker', None)
            )
            
            # Copy all additional attributes
            for attr in ['section', 'level', 'parent_id']:
                if hasattr(item, attr):
                    setattr(display_item, attr, getattr(item, attr))
                    
            display_items.append(display_item)
            
        # Format using hierarchical formatter
        formatter = HierarchicalFormatter(use_color=True)
        formatted_text = formatter.format_items(display_items)
        console.print(formatted_text)
    else:
        # Fallback to simple display
        for item in items:
            console.print(f"  [cyan]{item.id}.[/] {item.content}")
    
    # Get user selection
    valid_ids = [str(item.id) for item in items]
    try:
        if multi_select:
            choice = Prompt.ask("\nEnter selection(s)", default="")
            
            # Handle special case for selecting all items
            if choice.lower() == "all":
                return items
            
            # Process multiple selections
            selected_ids = []
            for part in choice.replace(',', ' ').split():
                try:
                    selected_ids.append(int(part))
                except ValueError:
                    console.print(f"[yellow]Invalid selection: {part}. Skipping.[/]")
            
            # Return the selected items
            selected_items = []
            for item in items:
                if item.id in selected_ids:
                    selected_items.append(item)
            
            if selected_items:
                return selected_items
            else:
                console.print("[yellow]No valid selections made.[/]")
                return []
        else:
            choice = Prompt.ask("\nEnter selection", choices=valid_ids, show_choices=False)
            
            # Return the selected item
            selected_id = int(choice)
            for item in items:
                if item.id == selected_id:
                    return item
    except KeyboardInterrupt:
        console.print("\n[yellow]Selection cancelled[/]")
        return [] if multi_select else None
    
    return [] if multi_select else None


def _select_basic(items: List[SelectableItem], prompt_text: str, 
                 multi_select: bool = False) -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """Basic terminal selection fallback when rich is not available"""
    print(f"\n{prompt_text}:")
    print("-" * len(prompt_text))
    
    # Display items - use formatters when available and items have hierarchy info
    if FORMATTERS_AVAILABLE and any(hasattr(item, 'level') for item in items):
        # Create a copy of each item that includes its ID in the content
        display_items = []
        for item in items:
            # Create a shallow copy of the item
            display_item = type(item)(
                id=item.id,
                content=f"{item.id}. {item.content}",
                original_marker=getattr(item, 'original_marker', None)
            )
            
            # Copy all additional attributes
            for attr in ['section', 'level', 'parent_id']:
                if hasattr(item, attr):
                    setattr(display_item, attr, getattr(item, attr))
                    
            display_items.append(display_item)
            
        # Format using hierarchical formatter
        formatter = create_formatter('hierarchy', use_color=True)
        print(formatter.format_items(display_items))
    else:
        # Fallback to simple display
        for item in items:
            print(f"{item.id}. {item.content}")
    
    # Get user selection
    try:
        if multi_select:
            print("\nEnter selection numbers separated by spaces, or 'all' for all items")
            choice = input("Selection: ")
            
            # Handle special case for selecting all items
            if choice.lower() == "all":
                return items
            
            # Process multiple selections
            selected_ids = []
            for part in choice.replace(',', ' ').split():
                try:
                    selected_ids.append(int(part))
                except ValueError:
                    print(f"Invalid selection: {part}. Skipping.")
            
            # Return the selected items
            selected_items = []
            for item in items:
                if item.id in selected_ids:
                    selected_items.append(item)
            
            if selected_items:
                return selected_items
            else:
                print("No valid selections made.")
                return []
        else:
            while True:
                choice = input("\nEnter selection number: ")
                try:
                    selected_id = int(choice)
                    for item in items:
                        if item.id == selected_id:
                            return item
                    print(f"Invalid selection: {choice}. Please enter a number from the list.")
                except ValueError:
                    print(f"Invalid input: {choice}. Please enter a number.")
    except KeyboardInterrupt:
        print("\nSelection cancelled")
        return [] if multi_select else None
    
    return [] if multi_select else None


def select_with_external(items: List[SelectableItem], 
                         tool: str = "auto", 
                         prompt: str = "Select an item",
                         multi_select: bool = False,
                         view: str = "hierarchy") -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """
    Use an external selection tool (fzf, gum, peco) to select from items.
    If tool is "auto", will try to find an available tool.
    
    Args:
        items: List of SelectableItem objects
        tool: Selection tool to use ("fzf", "gum", "peco", "auto", "overlay")
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections (only supported by some tools)
        view: Display style for items ('flat', 'hierarchy', 'mixed')
        
    Returns:
        If multi_select is False: Selected item or None if selection was cancelled
        If multi_select is True: List of selected items or empty list if no selection was made
    """
    if not items:
        return [] if multi_select else None
    
    # Handle overlay as a special case
    if tool == "overlay":
        result = select_with_overlay(items, prompt, multi_select)
        return result
    
    # Find available tool if set to auto
    if tool == "auto":
        for candidate in ["fzf", "gum", "peco"]:
            if _is_tool_available(candidate):
                tool = candidate
                break
        else:
            # No external tool found, fall back to internal
            tool = "internal"
    
    # Fall back to internal selector if external tool not available
    if tool == "internal" or not _is_tool_available(tool):
        return select_item(items, prompt, multi_select)
    
    # Create temp file for selection
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
        temp_filename = f.name
        
        # Generate content for the file
        if FORMATTERS_AVAILABLE and any(hasattr(item, 'level') for item in items):
            # Create a copy of each item that includes its ID in the content
            display_items = []
            for item in items:
                # Create a shallow copy of the item
                display_item = type(item)(
                    id=item.id,
                    content=f"{item.id}: {item.content}",
                    original_marker=getattr(item, 'original_marker', None)
                )
                
                # Copy all additional attributes
                for attr in ['section', 'level', 'parent_id']:
                    if hasattr(item, attr):
                        setattr(display_item, attr, getattr(item, attr))
                        
                display_items.append(display_item)
                
            # Format using appropriate formatter (but without color for file output)
            formatter = create_formatter(view, use_color=False)
            f.write(formatter.format_items(display_items))
        else:
            # Fallback to simple display
            for item in items:
                f.write(f"{item.id}: {item.content}\n")
        
        f.flush()
    
    try:
        # Build command based on the tool
        if tool == "fzf":
            cmd = ["fzf", "--layout=reverse", "--height=40%", f"--prompt={prompt}: "]
            if multi_select:
                cmd.append("--multi")
                
            # Show clear instructions for multi-select mode
            if multi_select:
                cmd.extend(["--header", "Press TAB to select multiple items, ENTER to confirm"])

            # Add -e/--exact to make the search exact instead of fuzzy
            cmd.append("-e")
        elif tool == "gum":
            cmd = ["gum", "filter", f"--placeholder={prompt}"]
        elif tool == "peco":
            cmd = ["peco", f"--prompt={prompt}"]
        else:
            # Unknown tool
            os.unlink(temp_filename)
            return select_item(items, prompt, multi_select)
        
        # Execute the command
        result = subprocess.run(
            cmd, 
            input=open(temp_filename, 'r').read(), 
            text=True, 
            capture_output=True
        )
        
        # Parse the output
        if result.returncode == 0 and result.stdout.strip():
            selected_lines = result.stdout.strip().split('\n')
            
            if multi_select:
                selected_items = []
                for line in selected_lines:
                    # Extract item ID from the start of the line
                    try:
                        item_id = int(line.split(':', 1)[0])
                        for item in items:
                            if item.id == item_id:
                                selected_items.append(item)
                                break
                    except (ValueError, IndexError):
                        continue
                
                return selected_items
            else:
                # Single selection mode
                try:
                    item_id = int(selected_lines[0].split(':', 1)[0])
                    for item in items:
                        if item.id == item_id:
                            return item
                except (ValueError, IndexError):
                    pass
    except Exception as e:
        print(f"Error using external selector: {e}", file=sys.stderr)
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_filename)
        except:
            pass
    
    # Fall back to internal selector if external fails
    return select_item(items, prompt, multi_select)


def select_with_overlay(items: List[SelectableItem], 
                       prompt: str = "Select an item",
                       multi_select: bool = False) -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """
    Use a terminal overlay for selection. Provides a more modern UX than the
    traditional command-line selectors.
    
    Args:
        items: List of SelectableItem objects
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections
        
    Returns:
        If multi_select is False: Selected item or None if selection was cancelled
        If multi_select is True: List of selected items or empty list if no selection was made
    """
    if not TEXTUAL_AVAILABLE:
        print("Terminal overlay requires textual. Falling back to basic selection.", file=sys.stderr)
        return select_item(items, prompt, multi_select)
    
    # Import TextualOverlay here to avoid import errors when not installed
    from .textual_overlay import run_overlay_selector
    return run_overlay_selector(items, prompt, multi_select)


def select_from_terminal(prompt: str = "Select an item",
                        multi_select: bool = False) -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """
    Capture terminal content and select from it.
    
    Args:
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections
        
    Returns:
        If multi_select is False: Selected item or None if selection was cancelled
        If multi_select is True: List of selected items or empty list if no selection was made
    """
    if not TEXTUAL_AVAILABLE:
        print("Terminal capture requires textual. Install with pip install lang-select[textual]", 
              file=sys.stderr)
        return [] if multi_select else None
    
    # Import relevant parts of textual_overlay
    from .textual_overlay import capture_terminal, run_overlay_selector
    
    # Capture terminal
    screen_text = capture_terminal()
    if not screen_text:
        print("No text captured from terminal.", file=sys.stderr)
        return [] if multi_select else None
    
    # Extract items from captured text
    try:
        from .enhanced_extractor import extract_enhanced_items
        items = extract_enhanced_items(screen_text)
    except ImportError:
        from .parser import extract_items
        items = extract_items(screen_text)
    
    if not items:
        print("No selectable items found in captured terminal text.", file=sys.stderr)
        return [] if multi_select else None
    
    # Select from items
    return run_overlay_selector(items, prompt, multi_select)


def _is_tool_available(name: str) -> bool:
    """Check if a command-line tool is available"""
    try:
        devnull = open(os.devnull, 'w')
        subprocess.call([name, "--version"], stdout=devnull, stderr=devnull)
        return True
    except (OSError, subprocess.SubprocessError):
        return False 