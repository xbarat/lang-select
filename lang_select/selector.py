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


def select_item(items: List[SelectableItem], prompt_text: str = "Select an item") -> Optional[SelectableItem]:
    """
    Display a list of items and let the user select one.
    If rich is available, uses rich UI, otherwise falls back to basic terminal UI.
    """
    if not items:
        return None
    
    if RICH_AVAILABLE:
        return _select_with_rich(items, prompt_text)
    else:
        return _select_basic(items, prompt_text)


def _select_with_rich(items: List[SelectableItem], prompt_text: str) -> Optional[SelectableItem]:
    """Use rich for a nicer selection experience"""
    console = Console()
    
    console.print(Panel(f"[bold]{prompt_text}[/] (Enter number or use arrow keys + Enter)", 
                       box=box.ROUNDED, style="blue"))
    
    # Display items
    for item in items:
        console.print(f"  [cyan]{item.id}.[/] {item.content}")
    
    # Get user selection
    valid_ids = [str(item.id) for item in items]
    try:
        choice = Prompt.ask("\nEnter selection", choices=valid_ids, show_choices=False)
        
        # Return the selected item
        selected_id = int(choice)
        for item in items:
            if item.id == selected_id:
                return item
    except KeyboardInterrupt:
        console.print("\n[yellow]Selection cancelled[/]")
        return None
    
    return None


def _select_basic(items: List[SelectableItem], prompt_text: str) -> Optional[SelectableItem]:
    """Basic terminal selection fallback when rich is not available"""
    print(f"\n{prompt_text}:")
    print("-" * len(prompt_text))
    
    # Display items
    for item in items:
        print(f"{item.id}. {item.content}")
    
    # Get user selection
    try:
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
        return None


def select_with_external(items: List[SelectableItem], 
                         tool: str = "auto", 
                         prompt: str = "Select an item") -> Optional[SelectableItem]:
    """
    Use an external selection tool (fzf, gum, peco) to select from items.
    If tool is "auto", will try to find an available tool.
    
    Args:
        items: List of SelectableItem objects
        tool: Selection tool to use ("fzf", "gum", "peco", "auto", "overlay")
        prompt: Prompt text to display
        
    Returns:
        Selected item or None if selection was cancelled
    """
    if not items:
        return None
    
    # Handle overlay as a special case
    if tool == "overlay":
        return select_with_overlay(items, prompt)
    
    # Find available tool if set to auto
    if tool == "auto":
        # Check for overlay first if available
        if TEXTUAL_AVAILABLE and not os.environ.get("LANG_SELECT_NO_OVERLAY"):
            return select_with_overlay(items, prompt)
            
        # Then check external tools
        for t in ["fzf", "gum", "peco"]:
            if _is_tool_available(t):
                tool = t
                break
        else:
            # If no external tools found, fall back to built-in selector
            return select_item(items, prompt)
    
    # Create temporary file for selection
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp:
        # Write items with content as the main text
        for item in items:
            temp.write(f"{item.content}\n")
        temp_path = temp.name
    
    try:
        # Run the appropriate selection tool
        selected_text = None
        if tool == "fzf":
            result = subprocess.run(
                ["fzf", "--height=40%", f"--prompt={prompt}: "],
                input="\n".join(item.content for item in items),
                text=True,
                capture_output=True
            )
            if result.returncode == 0:
                selected_text = result.stdout.strip()
        
        elif tool == "gum":
            result = subprocess.run(
                ["gum", "choose", "--limit=1", f"--header={prompt}"],
                input="\n".join(item.content for item in items),
                text=True,
                capture_output=True
            )
            if result.returncode == 0:
                selected_text = result.stdout.strip()
        
        elif tool == "peco":
            result = subprocess.run(
                ["peco", f"--prompt={prompt}:"],
                input="\n".join(item.content for item in items),
                text=True,
                capture_output=True
            )
            if result.returncode == 0:
                selected_text = result.stdout.strip()
        
        # Find the matching item
        if selected_text:
            for item in items:
                if item.content == selected_text:
                    return item
    
    except (subprocess.SubprocessError, FileNotFoundError):
        # Fall back to built-in selector if external tool fails
        return select_item(items, prompt)
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)
    
    return None


def select_with_overlay(items: List[SelectableItem], 
                       prompt: str = "Select an item") -> Optional[SelectableItem]:
    """
    Use a terminal overlay to select from items.
    Falls back to the built-in selector if textual is not available.
    
    Args:
        items: List of SelectableItem objects
        prompt: Prompt text to display
        
    Returns:
        Selected item or None if selection was cancelled
    """
    # Lazy import to avoid requiring textual for basic functionality
    if TEXTUAL_AVAILABLE:
        # Only import when actually used
        from .textual_overlay import select_with_textual_overlay
        return select_with_textual_overlay(
            items, 
            prompt,
            on_not_available=lambda: select_item(items, prompt)
        )
    else:
        # Fall back to built-in selector
        return select_item(items, prompt)


def select_from_terminal(prompt: str = "Select an item") -> Optional[SelectableItem]:
    """
    Capture current terminal content, extract items, and show overlay selector.
    Falls back to the built-in selector if textual is not available.
    
    Args:
        prompt: Prompt text to display
        
    Returns:
        Selected item or None if selection was cancelled
    """
    # Lazy import to avoid requiring textual for basic functionality
    if TEXTUAL_AVAILABLE:
        from .textual_overlay import overlay_select_from_recent
        return overlay_select_from_recent(prompt=prompt)
    else:
        print("Terminal overlay selection requires textual. Install with:")
        print("pip install lang-select[textual]")
        return None


def _is_tool_available(name: str) -> bool:
    """Check if a command-line tool is available"""
    try:
        devnull = open(os.devnull, 'w')
        subprocess.Popen([name], stdout=devnull, stderr=devnull).communicate()
    except (OSError, subprocess.SubprocessError):
        return False
    return True 