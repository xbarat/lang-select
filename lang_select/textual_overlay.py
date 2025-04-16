"""
Textual-based overlay selector for terminal interfaces.
"""

import os
import sys
import time
from typing import List, Optional, Dict, Any, Callable, Union

try:
    from textual.app import App, ComposeResult
    from textual.containers import Container, Vertical
    from textual.widgets import Label, ListItem, ListView, Button, Footer, Checkbox
    from textual.screen import Screen
    from textual import events
    from textual.binding import Binding
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False

from .parser import SelectableItem


class OverlayApp(App):
    """Textual app for overlay selection"""
    
    BINDINGS = [
        Binding(key="q", action="quit", description="Quit"),
        Binding(key="escape", action="quit", description="Quit"),
        Binding(key="enter", action="select", description="Select"),
        Binding(key="space", action="toggle", description="Toggle selection"),
    ]
    
    def __init__(self, items: List[SelectableItem], prompt: str = "Select an item", multi_select: bool = False):
        """Initialize the overlay app with items to select from"""
        super().__init__()
        self.items = items
        self.prompt = prompt
        self.multi_select = multi_select
        self.selected_item = None
        self.selected_items = []
        self.selected_indices = set()
        
    def compose(self) -> ComposeResult:
        """Create the UI components"""
        with Container(id="overlay-container"):
            if self.multi_select:
                yield Label(f"{self.prompt} (Space to toggle, Enter to confirm)", id="prompt-label")
            else:
                yield Label(self.prompt, id="prompt-label")
            
            list_view = ListView(id="item-list")
            for item in self.items:
                if self.multi_select:
                    list_view.append(ListItem(
                        Checkbox(value=False, id=f"checkbox-{item.id}"),
                        Label(f"{item.id}. {item.content}")
                    ))
                else:
                    list_view.append(ListItem(Label(f"{item.id}. {item.content}")))
            
            yield list_view
            
            with Container(id="buttons-container"):
                yield Button("Select", id="select-button", variant="primary")
                if self.multi_select:
                    yield Button("Select All", id="select-all-button", variant="default")
                yield Button("Cancel", id="cancel-button", variant="error")
                
        yield Footer()
    
    def on_list_view_selected(self, event: events.Selected) -> None:
        """Handle list item selection"""
        if not self.multi_select:
            self.selected_item = self.items[event.index]
    
    def action_toggle(self) -> None:
        """Toggle selection for the highlighted item in multi-select mode"""
        if not self.multi_select:
            return
            
        list_view = self.query_one(ListView)
        if list_view.highlighted_child is not None:
            index = list_view.index_of(list_view.highlighted_child)
            if 0 <= index < len(self.items):
                list_item = list_view.children[index]
                checkbox = list_item.query_one(Checkbox)
                checkbox.value = not checkbox.value
                
                if checkbox.value:
                    self.selected_indices.add(index)
                else:
                    self.selected_indices.discard(index)
    
    def on_button_pressed(self, event: events.Button.Pressed) -> None:
        """Handle button presses"""
        if event.button.id == "select-button":
            self.action_select()
        elif event.button.id == "select-all-button":
            self.select_all_items()
        elif event.button.id == "cancel-button":
            self.action_quit()
    
    def select_all_items(self) -> None:
        """Select all available items"""
        if not self.multi_select:
            return
            
        list_view = self.query_one(ListView)
        for i, list_item in enumerate(list_view.children):
            checkbox = list_item.query_one(Checkbox)
            checkbox.value = True
            self.selected_indices.add(i)
            
    def action_select(self) -> None:
        """Select the current item or selected items and exit"""
        if self.multi_select:
            self.selected_items = []
            for index in self.selected_indices:
                if 0 <= index < len(self.items):
                    self.selected_items.append(self.items[index])
        else:
            list_view = self.query_one(ListView)
            if list_view.highlighted_child is not None:
                index = list_view.index_of(list_view.highlighted_child)
                if 0 <= index < len(self.items):
                    self.selected_item = self.items[index]
        self.exit()
        
    def on_mount(self) -> None:
        """Set initial focus and styling when the app is mounted"""
        self.query_one(ListView).focus()


class TerminalOverlay:
    """Manages terminal overlay capabilities"""
    
    def __init__(self):
        """Initialize the terminal overlay"""
        self.can_use_textual = TEXTUAL_AVAILABLE
        
    def is_available(self) -> bool:
        """Check if the terminal overlay can be used"""
        return self.can_use_textual
    
    def select_with_overlay(self, 
                           items: List[SelectableItem], 
                           prompt: str = "Select an item",
                           multi_select: bool = False) -> Union[Optional[SelectableItem], List[SelectableItem]]:
        """
        Present an overlay selection interface for the user to select item(s).
        
        Args:
            items: List of SelectableItem objects
            prompt: Prompt text to display
            multi_select: Whether to allow multiple selections
            
        Returns:
            If multi_select is False: Selected item or None if selection was cancelled
            If multi_select is True: List of selected items or empty list if no selection was made
        """
        if not self.can_use_textual:
            raise ImportError(
                "Textual is required for overlay functionality. "
                "Install it with 'pip install textual' or 'pip install lang-select[textual]'"
            )
            
        if not items:
            return [] if multi_select else None
            
        app = OverlayApp(items, prompt, multi_select)
        app.run()
        
        if multi_select:
            return app.selected_items
        else:
            return app.selected_item


class TerminalCapture:
    """Utility to capture and replay terminal content"""
    
    def __init__(self):
        """Initialize the terminal capture"""
        self.content = ""
        self.capture_time = None
        
    def capture_screen(self) -> str:
        """
        Try to capture current terminal content.
        This is a basic implementation and may not work in all terminals.
        
        Returns:
            Captured text content
        """
        # Method 1: Try to use terminal's buffer
        if sys.platform == "darwin" or sys.platform.startswith("linux"):
            try:
                import subprocess
                result = subprocess.run(["tput", "sc"], check=True)  # Save cursor position
                result = subprocess.run(
                    ["clear; cat /dev/tty"], 
                    shell=True,
                    text=True,
                    capture_output=True, 
                    check=False
                )
                subprocess.run(["tput", "rc"], check=True)  # Restore cursor position
                self.content = result.stdout
                self.capture_time = time.time()
                return self.content
            except Exception:
                pass
        
        # If all else fails, rely on user providing content
        self.content = ""
        return self.content
    
    def get_recent_capture(self) -> str:
        """Get the most recently captured content"""
        return self.content
        
    def set_content(self, content: str) -> None:
        """Set content manually"""
        self.content = content
        self.capture_time = time.time()


# Singleton instance for the terminal overlay
overlay_manager = TerminalOverlay()

# Singleton instance for terminal capture
terminal_capture = TerminalCapture()


def select_with_textual_overlay(items: List[SelectableItem], 
                               prompt: str = "Select an item",
                               multi_select: bool = False,
                               on_not_available: Callable[[], Union[Optional[SelectableItem], List[SelectableItem]]] = None) -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """
    Public API for selecting with the textual overlay.
    Falls back to the provided function if textual is not available.
    
    Args:
        items: List of SelectableItem objects
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections
        on_not_available: Function to call if textual is not available
        
    Returns:
        If multi_select is False: Selected item or None if selection was cancelled
        If multi_select is True: List of selected items or empty list if no selection was made
    """
    if not overlay_manager.is_available():
        if on_not_available is not None:
            return on_not_available()
        else:
            raise ImportError(
                "Textual is required for overlay functionality. "
                "Install it with 'pip install textual' or 'pip install lang-select[textual]'"
            )
    
    return overlay_manager.select_with_overlay(items, prompt, multi_select)


def check_overlay_availability() -> bool:
    """
    Check if the overlay functionality is available.
    
    Returns:
        True if overlay is available, False otherwise
    """
    return overlay_manager.is_available()


def capture_terminal_content() -> str:
    """
    Attempt to capture current terminal content.
    
    Returns:
        Captured terminal content as string
    """
    return terminal_capture.capture_screen()


def overlay_select_from_recent(text: str = None,
                              prompt: str = "Select an item",
                              multi_select: bool = False) -> Union[Optional[SelectableItem], List[SelectableItem]]:
    """
    Select items from recently captured terminal content or provided text.
    
    Args:
        text: Optional text to use instead of captured content
        prompt: Prompt text to display
        multi_select: Whether to allow multiple selections
        
    Returns:
        If multi_select is False: Selected item or None if selection was cancelled
        If multi_select is True: List of selected items or empty list if no selection was made
    """
    from .parser import extract_items
    
    # Use provided text or captured content
    content = text if text is not None else terminal_capture.get_recent_capture()
    
    if not content:
        # Try to capture now if no content available
        content = capture_terminal_content()
        
    if not content:
        return [] if multi_select else None
    
    items = extract_items(content)
    if not items:
        return [] if multi_select else None
        
    return select_with_textual_overlay(items, prompt, multi_select) 