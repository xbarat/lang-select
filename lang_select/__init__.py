"""
Lang Select - Extract selectable items from language model responses
"""

__version__ = "0.3.0"

import json
import os
import sys
from typing import Optional, Dict, Any, List, Tuple, Callable

from .parser import extract_items, extract_numbered_items, extract_bullet_items, SelectableItem
from .selector import select_item, select_with_external

# New convenience functions
def quick_select(text: str, tool: str = "auto", prompt: str = "Select an item",
                on_success: Callable[[str], None] = None,
                on_empty: Callable[[], None] = None,
                on_cancel: Callable[[], None] = None) -> Optional[str]:
    """One-line function to extract and select from text in a single call
    
    Args:
        text: Text content to extract items from
        tool: Selection tool to use ("auto", "fzf", "gum", "peco", "internal")
        prompt: Prompt text to display
        on_success: Optional callback function when an item is selected
        on_empty: Optional callback function when no items are found
        on_cancel: Optional callback function when selection is cancelled
        
    Returns:
        Selected item content as string or None if no selection was made
    """
    items = extract_items(text)
    if not items:
        if on_empty:
            on_empty()
        return None
    
    selected = select_with_external(items, tool=tool, prompt=prompt)
    if selected:
        result = selected.content
        if on_success:
            on_success(result)
        return result
    else:
        if on_cancel:
            on_cancel()
        return None


def select_to_json(text: str, tool: str = "auto", prompt: str = "Select an item") -> str:
    """Extract, select, and return result as JSON string
    
    Args:
        text: Text content to extract items from
        tool: Selection tool to use
        prompt: Prompt text to display
        
    Returns:
        JSON string with selection result or error information
    """
    items = extract_items(text)
    if not items:
        return json.dumps({"success": False, "error": "No items found"})
    
    selected = select_with_external(items, tool=tool, prompt=prompt)
    if selected:
        return json.dumps({
            "success": True,
            "selected": selected.to_dict()
        })
    return json.dumps({"success": False, "error": "No selection made"})


class ResponseManager:
    """Manager for handling recent language model responses"""
    
    def __init__(self, recent_file: str = None):
        """Initialize the response manager
        
        Args:
            recent_file: Optional path to store the most recent response
        """
        self.recent_response = None
        self.recent_file = recent_file
        self.last_selection = None
        self.last_selected_items = []
        
    def store(self, text: str) -> 'ResponseManager':
        """Store a recent response
        
        Args:
            text: Text content to store
            
        Returns:
            Self for method chaining
        """
        self.recent_response = text
        self.last_selection = None
        self.last_selected_items = []
        
        # Optionally save to file if recent_file is specified
        if self.recent_file:
            try:
                with open(self.recent_file, 'w', encoding='utf-8') as f:
                    f.write(text)
            except Exception:
                pass  # Silently fail if we can't write to the file
                
        return self
        
    def select(self, tool: str = "auto", prompt: str = "Select an item", 
               feedback: bool = False, feedback_stream = sys.stdout) -> Optional[str]:
        """Quick select from the stored response
        
        Args:
            tool: Selection tool to use
            prompt: Prompt text to display
            feedback: Whether to print feedback about the selection
            feedback_stream: Stream to write feedback to (default: sys.stdout)
            
        Returns:
            Selected item content as string or None if no selection was made
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
            
        selected = select_with_external(self.last_selected_items, tool=tool, prompt=prompt)
        if selected:
            self.last_selection = selected.content
            if feedback:
                print(f"\nSelected: {selected.content}", file=feedback_stream)
            return selected.content
        else:
            if feedback:
                print("No selection made", file=feedback_stream)
            return None
    
    def get_items(self) -> List[SelectableItem]:
        """Extract items from the stored response without selection
        
        Returns:
            List of SelectableItem objects or empty list if no items found
        """
        if not self.recent_response:
            # Try to load from file if available
            if self.recent_file and os.path.exists(self.recent_file):
                try:
                    with open(self.recent_file, 'r', encoding='utf-8') as f:
                        self.recent_response = f.read()
                except Exception:
                    return []
            else:
                return []
        
        self.last_selected_items = extract_items(self.recent_response)        
        return self.last_selected_items
    
    def get_selection_info(self) -> Dict[str, Any]:
        """Get information about the last selection
        
        Returns:
            Dictionary with information about the last selection
        """
        return {
            "selected": self.last_selection,
            "num_items": len(self.last_selected_items) if self.last_selected_items else 0,
            "has_selection": self.last_selection is not None,
            "items": [item.to_dict() for item in self.last_selected_items] if self.last_selected_items else []
        }
    
    def get_selection_summary(self) -> str:
        """Get a human-readable summary of the last selection
        
        Returns:
            A string summarizing the last selection
        """
        if not self.last_selected_items:
            return "No items were found in the response"
        
        if self.last_selection is None:
            return f"No selection was made from {len(self.last_selected_items)} available items"
        
        return f"Selected: \"{self.last_selection}\" from {len(self.last_selected_items)} available items"


__all__ = [
    "extract_items",
    "extract_numbered_items", 
    "extract_bullet_items",
    "select_item",
    "select_with_external",
    "SelectableItem",
    "quick_select",
    "select_to_json",
    "ResponseManager"
] 