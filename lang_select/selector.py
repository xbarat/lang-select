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
    
    # Display items
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
    
    # Display items
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
                         multi_select: bool = False) -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """
    Use an external selection tool (fzf, gum, peco) to select from items.
    If tool is "auto", will try to find an available tool.
    
    Args:
        items: List of SelectableItem objects
        tool: Selection tool to use ("fzf", "gum", "peco", "auto", "overlay")
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections (only supported by some tools)
        
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
        # Check for overlay first if available
        if TEXTUAL_AVAILABLE and not os.environ.get("LANG_SELECT_NO_OVERLAY"):
            result = select_with_overlay(items, prompt, multi_select)
            return result
            
        # Then check external tools
        for t in ["fzf", "gum", "peco"]:
            if _is_tool_available(t):
                tool = t
                break
        else:
            # If no external tools found, fall back to built-in selector
            return select_item(items, prompt, multi_select)
    elif tool == "internal":
        # Direct use of the internal selector
        return select_item(items, prompt, multi_select)
    
    # Create temporary file for selection
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        # Write items with content as the main text
        for item in items:
            temp.write(f"{item.content}\n")
        temp_path = temp.name
    
    try:
        # Run the appropriate selection tool
        selected_texts = []
        if tool == "fzf":
            cmd = ["fzf", "--height=40%", f"--prompt={prompt}: "]
            if multi_select:
                cmd.append("-m")  # Enable multi-select
            result = subprocess.run(
                cmd,
                input="\n".join(item.content for item in items),
                text=True,
                capture_output=True
            )
            if result.returncode == 0:
                selected_texts = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        elif tool == "gum":
            cmd = ["gum", "choose", f"--header={prompt}"]
            if multi_select:
                cmd.extend(["--no-limit"])  # Remove selection limit
            else:
                cmd.extend(["--limit=1"])
            result = subprocess.run(
                cmd,
                input="\n".join(item.content for item in items),
                text=True,
                capture_output=True
            )
            if result.returncode == 0:
                selected_texts = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        elif tool == "peco":
            # Note: peco supports multi-select with TAB by default
            result = subprocess.run(
                ["peco", f"--prompt={prompt}:"],
                input="\n".join(item.content for item in items),
                text=True,
                capture_output=True
            )
            if result.returncode == 0:
                selected_texts = [line.strip() for line in result.stdout.strip().split('\n') if line.strip()]
        
        # Find the matching items
        selected_items = []
        for text in selected_texts:
            for item in items:
                if item.content == text:
                    selected_items.append(item)
                    break
        
        if multi_select:
            return selected_items
        else:
            return selected_items[0] if selected_items else None
    
    except (subprocess.SubprocessError, FileNotFoundError):
        # Fall back to built-in selector if external tool fails
        return select_item(items, prompt, multi_select)
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    return [] if multi_select else None


def select_with_overlay(items: List[SelectableItem], 
                       prompt: str = "Select an item",
                       multi_select: bool = False) -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """
    Use a terminal overlay to select from items.
    Falls back to the built-in selector if textual is not available.
    
    Args:
        items: List of SelectableItem objects
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections
        
    Returns:
        If multi_select is False: Selected item or None if selection was cancelled
        If multi_select is True: List of selected items or empty list if no selection was made
    """
    # Lazy import to avoid requiring textual for basic functionality
    if TEXTUAL_AVAILABLE:
        # Only import when actually used
        from .textual_overlay import select_with_textual_overlay
        return select_with_textual_overlay(
            items, 
            prompt,
            multi_select=multi_select,
            on_not_available=lambda: select_item(items, prompt, multi_select)
        )
    else:
        # Fall back to built-in selector
        return select_item(items, prompt, multi_select)


def select_from_terminal(prompt: str = "Select an item",
                        multi_select: bool = False) -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """
    Capture current terminal content, extract items, and show overlay selector.
    Falls back to the built-in selector if textual is not available.
    
    Args:
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections
        
    Returns:
        If multi_select is False: Selected item or None if selection was cancelled
        If multi_select is True: List of selected items or empty list if no selection was made
    """
    # Lazy import to avoid requiring textual for basic functionality
    if TEXTUAL_AVAILABLE:
        from .textual_overlay import overlay_select_from_recent
        return overlay_select_from_recent(prompt=prompt, multi_select=multi_select)
    else:
        print("Terminal overlay selection requires textual. Install with:")
        print("pip install lang-select[textual]")
        return [] if multi_select else None


def _is_tool_available(name: str) -> bool:
    """Check if a command-line tool is available"""
    try:
        devnull = open(os.devnull, 'w')
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except (OSError, subprocess.SubprocessError):
        return False
    return True 