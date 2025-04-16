"""
Lang Select - Extract selectable items from language model responses
"""

__version__ = "0.7.0"

import json
import os
import sys
from typing import Optional, Dict, Any, List, Tuple, Callable, Union

from .parser import extract_items, extract_numbered_items, extract_bullet_items, SelectableItem
from .selector import select_item, select_with_external, select_with_overlay, select_from_terminal
from .enhanced_extractor import EnhancedExtractor, ExtendedSelectableItem, EnhancedResponseManager, extract_enhanced_items

# Check if textual is available
try:
    import textual
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

# Export formatter classes
try:
    from .formatter import (
        create_formatter,
        FormatterBase,
        FlatFormatter,
        HierarchicalFormatter, 
        MixedFormatter
    )
except ImportError:
    pass  # Formatters may not be available

# New convenience functions
def quick_select(text: str, tool: str = "auto", prompt: str = "Select an item",
                multi_select: bool = False,
                on_success: Callable[[Union[str, List[str]]], None] = None,
                on_empty: Callable[[], None] = None,
                on_cancel: Callable[[], None] = None,
                use_enhanced: bool = False) -> Optional[Union[str, List[str]]]:
    """One-line function to extract and select from text in a single call
    
    Args:
        text: Text content to extract items from
        tool: Selection tool to use ("auto", "fzf", "gum", "peco", "internal", "overlay")
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections
        on_success: Optional callback function when item(s) are selected
        on_empty: Optional callback function when no items are found
        on_cancel: Optional callback function when selection is cancelled
        use_enhanced: Whether to use the enhanced extractor (for better hierarchy and section support)
        
    Returns:
        If multi_select is False: Selected item content as string or None if no selection was made
        If multi_select is True: List of selected item contents or None if no selection was made
    """
    if use_enhanced:
        items = extract_enhanced_items(text)
    else:
        items = extract_items(text)
        
    if not items:
        if on_empty:
            on_empty()
        return None
    
    selected = select_with_external(items, tool=tool, prompt=prompt, multi_select=multi_select)
    if selected:
        if multi_select:
            result = [item.content for item in selected]
        else:
            result = selected.content
        if on_success:
            on_success(result)
        return result
    else:
        if on_cancel:
            on_cancel()
        return None


def quick_overlay_select(text: str = None, prompt: str = "Select an item", 
                         multi_select: bool = False) -> Optional[Union[str, List[str]]]:
    """Capture terminal content (or use provided text) and show an overlay selector
    
    This function captures the current terminal content if no text is provided,
    extracts selectable items, and shows them in an overlay selector.
    
    Args:
        text: Optional text to parse instead of capturing terminal content
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections
        
    Returns:
        If multi_select is False: Selected item content as string or None if no selection was made
        If multi_select is True: List of selected item contents or empty list if no selection was made
    """
    if not TEXTUAL_AVAILABLE:
        print("Terminal overlay selection requires textual. Install with:")
        print("pip install lang-select[textual]")
        return None
        
    # Import here to avoid issues if textual is not installed
    from .textual_overlay import overlay_select_from_recent
    
    selected = overlay_select_from_recent(text, prompt, multi_select=multi_select)
    if selected:
        if multi_select:
            return [item.content for item in selected]
        else:
            return selected.content
    return None


def select_to_json(text: str, tool: str = "auto", prompt: str = "Select an item", 
                   multi_select: bool = False) -> str:
    """Extract, select, and return result as JSON string
    
    Args:
        text: Text content to extract items from
        tool: Selection tool to use
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections
        
    Returns:
        JSON string with selection result or error information
    """
    items = extract_items(text)
    if not items:
        return json.dumps({"success": False, "error": "No items found"})
    
    selected = select_with_external(items, tool=tool, prompt=prompt, multi_select=multi_select)
    if selected:
        if multi_select:
            return json.dumps({
                "success": True,
                "selected": [item.to_dict() for item in selected]
            })
        else:
            return json.dumps({
                "success": True,
                "selected": selected.to_dict()
            })
    return json.dumps({"success": False, "error": "No selection made"})


class ResponseManager:
    """Manager for handling recent language model responses"""
    
    def __init__(self, recent_file: str = None, use_enhanced: bool = False):
        """Initialize the response manager
        
        Args:
            recent_file: Optional path to a file that stores the most recent response
            use_enhanced: Whether to use the enhanced extractor for better hierarchy and section support
        """
        self.recent_response = None
        self.recent_file = recent_file
        self.last_selected_items = []
        self.last_selection = None
        self.last_selections = []  # For multi-select support
        self.use_enhanced = use_enhanced
        
    def store(self, response: str):
        """Store a response for later selection
        
        Args:
            response: Text content to store
        """
        self.recent_response = response
        self.last_selected_items = []
        self.last_selection = None
        self.last_selections = []
        
        # Save to file if configured
        if self.recent_file:
            try:
                with open(self.recent_file, 'w', encoding='utf-8') as f:
                    f.write(response)
            except Exception:
                pass
        
    def select(self, tool: str = "auto", prompt: str = "Select an item", 
               multi_select: bool = False,
               feedback: bool = False, feedback_stream = sys.stdout) -> Optional[Union[str, List[str]]]:
        """Quick select from the stored response
        
        Args:
            tool: Selection tool to use
            prompt: Prompt text to display
            multi_select: Whether to allow multiple selections
            feedback: Whether to print feedback about the selection
            feedback_stream: Stream to write feedback to (default: sys.stdout)
            
        Returns:
            If multi_select is False: Selected item content as string or None if no selection was made
            If multi_select is True: List of selected item contents or None if no selection was made
        """
        if not self.recent_response:
            # Try to load from file if available
            if self.recent_file and os.path.exists(self.recent_file):
                try:
                    with open(self.recent_file, 'r', encoding='utf-8') as f:
                        self.recent_response = f.read()
                except Exception:
                    if feedback:
                        print("Error: Could not read from recent file", file=feedback_stream)
                    return None
            else:
                if feedback:
                    print("No recent response available", file=feedback_stream)
                return None
        
        self.last_selected_items = extract_items(self.recent_response)
        if not self.last_selected_items:
            if feedback:
                print("No selectable items found in the response", file=feedback_stream)
            return None
        
        if feedback:
            print(f"Found {len(self.last_selected_items)} selectable items:", file=feedback_stream)
            for item in self.last_selected_items:
                print(f"  {item}", file=feedback_stream)
            
        selected = select_with_external(self.last_selected_items, tool=tool, prompt=prompt, multi_select=multi_select)
        if selected:
            if multi_select:
                self.last_selections = [item.content for item in selected]
                self.last_selection = self.last_selections[0] if self.last_selections else None
                if feedback:
                    print("\nSelected items:", file=feedback_stream)
                    for item in selected:
                        print(f"  {item.content}", file=feedback_stream)
                return self.last_selections
            else:
                self.last_selection = selected.content
                self.last_selections = [self.last_selection] if self.last_selection else []
                if feedback:
                    print(f"\nSelected: {selected.content}", file=feedback_stream)
                return self.last_selection
        else:
            if feedback:
                print("No selection made", file=feedback_stream)
            return None
    
    def select_with_overlay(self, prompt: str = "Select an item",
                           multi_select: bool = False,
                           feedback: bool = False, feedback_stream = sys.stdout) -> Optional[Union[str, List[str]]]:
        """Select from the stored response using an overlay
        
        Args:
            prompt: Prompt text to display
            multi_select: Whether to allow multiple selections
            feedback: Whether to print feedback about the selection
            feedback_stream: Stream to write feedback to (default: sys.stdout)
            
        Returns:
            If multi_select is False: Selected item content as string or None if no selection was made
            If multi_select is True: List of selected item contents or empty list if no selection was made
        """
        if not TEXTUAL_AVAILABLE:
            if feedback:
                print("Terminal overlay selection requires textual. Install with:", file=feedback_stream)
                print("pip install lang-select[textual]", file=feedback_stream)
            return None
            
        return self.select(tool="overlay", prompt=prompt, multi_select=multi_select, 
                           feedback=feedback, feedback_stream=feedback_stream)
    
    def get_items(self) -> List[SelectableItem]:
        """Get the selectable items from the last stored response
        
        Returns:
            List of SelectableItem objects
        """
        if not self.recent_response:
            return []
        
        # If we've already parsed this response, return the cached items
        if self.last_selected_items:
            return self.last_selected_items
        
        # Otherwise, parse the response and cache the results
        if self.use_enhanced:
            self.last_selected_items = extract_enhanced_items(self.recent_response)
        else:
            self.last_selected_items = extract_items(self.recent_response)
        
        return self.last_selected_items
    
    def has_selectable_content(self) -> bool:
        """Check if the stored response contains selectable items
        
        Returns:
            True if the response contains selectable items, False otherwise
        """
        items = self.get_items()
        return len(items) > 0
    
    def get_selection_info(self) -> Dict[str, Any]:
        """Get information about the last selection
        
        Returns:
            Dictionary with information about the last selection
        """
        return {
            "selected": self.last_selection,
            "selected_items": self.last_selections,
            "num_items": len(self.last_selected_items) if self.last_selected_items else 0,
            "has_selection": bool(self.last_selections),
            "items": [item.to_dict() for item in self.last_selected_items] if self.last_selected_items else []
        }
    
    def get_selection_summary(self) -> str:
        """Get a human-readable summary of the last selection
        
        Returns:
            A string summarizing the last selection
        """
        if not self.last_selected_items:
            return "No items were found in the response"
        
        if not self.last_selections:
            return f"No selection was made from {len(self.last_selected_items)} available items"
        
        if len(self.last_selections) == 1:
            return f"Selected: \"{self.last_selections[0]}\" from {len(self.last_selected_items)} available items"
        else:
            selections = "\n".join(f"  - {item}" for item in self.last_selections)
            return f"Selected {len(self.last_selections)} items from {len(self.last_selected_items)} available items:\n{selections}"


def is_overlay_available() -> bool:
    """Check if the overlay functionality is available
    
    Returns:
        True if overlay is available, False otherwise
    """
    return TEXTUAL_AVAILABLE
    

__all__ = [
    "extract_items",
    "extract_numbered_items", 
    "extract_bullet_items",
    "select_item",
    "select_with_external",
    "select_with_overlay",
    "select_from_terminal",
    "SelectableItem",
    "quick_select",
    "quick_overlay_select",
    "select_to_json",
    "ResponseManager",
    "is_overlay_available"
] 