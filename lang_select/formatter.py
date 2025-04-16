#!/usr/bin/env python3
"""
Output formatting for Lang Select.

This module provides formatters for displaying extracted items in various styles,
including hierarchical views, colorized output, and special handling for markdown
characters and section headers.
"""

import re
from typing import List, Dict, Optional, Any, Union, Tuple

# Import rich with proper fallback handling
try:
    import rich
    from rich.console import Console
    from rich.text import Text
    from rich.style import Style
    RICH_AVAILABLE = True
    RichText = Text  # Type alias for use in type annotations
except ImportError:
    RICH_AVAILABLE = False
    # Define a dummy Text class for type annotations when rich is not available
    class RichText:
        pass

# Define ANSI color codes for systems without rich
ANSI_COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "italic": "\033[3m",
    "blue": "\033[34m",
    "green": "\033[32m",
    "cyan": "\033[36m",
    "magenta": "\033[35m",
    "yellow": "\033[33m",
    "red": "\033[31m",
    "gray": "\033[90m",
}

# Create fallback styling function when rich is not available
def ansi_style(text: str, **styles) -> str:
    """Apply ANSI styling to text"""
    if not any(styles.values()):
        return text
        
    codes = []
    if styles.get("bold"):
        codes.append(ANSI_COLORS["bold"])
    if styles.get("italic"):
        codes.append(ANSI_COLORS["italic"])
        
    # Handle foreground color
    for color in ["blue", "green", "cyan", "magenta", "yellow", "red", "gray"]:
        if styles.get(color):
            codes.append(ANSI_COLORS[color])
            break
            
    if not codes:
        return text
        
    return f"{''.join(codes)}{text}{ANSI_COLORS['reset']}"


class FormatterBase:
    """Base class for formatters"""
    
    def __init__(self, use_color: bool = True):
        self.use_color = use_color and RICH_AVAILABLE
        if self.use_color:
            self.console = Console(highlight=False)
            
    def format_items(self, items: List[Any]) -> str:
        """Format a list of items into a string representation"""
        raise NotImplementedError("Subclasses must implement format_items")
        
    def _style_text(self, text: str, **styles) -> Union[str, RichText]:
        """Apply styling to text, with fallbacks for systems without rich"""
        if not self.use_color:
            return ansi_style(text, **styles)
            
        styled_text = Text(text)
        for style_name, value in styles.items():
            if value:
                if style_name in ["bold", "italic"]:
                    styled_text.stylize(style_name)
                else:
                    styled_text.stylize(f"color({style_name})")
        return styled_text
        
    def _output_text(self, text: Union[str, RichText]) -> str:
        """Output text, handling rich Text objects appropriately"""
        if self.use_color and RICH_AVAILABLE and isinstance(text, Text):
            with self.console.capture() as capture:
                self.console.print(text, end="")
            return capture.get()
        return str(text)
        
    def _escape_markdown(self, text: str) -> str:
        """Escape markdown characters in text"""
        # Replace ** with styled bold text
        text = re.sub(r'\*\*(.*?)\*\*', lambda m: self._output_text(
            self._style_text(m.group(1), bold=True)
        ), text)
        
        # Replace * with styled italic text
        text = re.sub(r'\*(.*?)\*', lambda m: self._output_text(
            self._style_text(m.group(1), italic=True)
        ), text)
        
        # Escape remaining markdown characters
        for char in ['`', '#', '|', '_']:
            text = text.replace(char, '\\' + char)
            
        return text


class FlatFormatter(FormatterBase):
    """Formats items as a flat list with bullets"""
    
    def __init__(self, bullet_char: str = "•", use_color: bool = True):
        super().__init__(use_color)
        self.bullet_char = bullet_char
        
    def format_items(self, items: List[Any]) -> str:
        """Format items as a simple flat list"""
        result = []
        
        for item in items:
            bullet = self._style_text(self.bullet_char, cyan=True)
            text = self._escape_markdown(item.content)
            
            # Add section as prefix if available
            if hasattr(item, 'section') and item.section:
                section = self._style_text(f"[{item.section}] ", blue=True, bold=True)
                line = f"{self._output_text(section)}{self._output_text(bullet)} {text}"
            else:
                line = f"{self._output_text(bullet)} {text}"
                
            result.append(line)
            
        return "\n".join(result)


class HierarchicalFormatter(FormatterBase):
    """Formats items as a hierarchical tree structure"""
    
    def __init__(self, use_color: bool = True):
        super().__init__(use_color)
        # Define bullet styles for different levels
        self.bullet_styles = [
            ("•", "cyan"),    # Level 0
            ("◦", "blue"),    # Level 1
            ("‣", "green"),   # Level 2
            ("▪", "magenta"), # Level 3
            ("▫", "yellow")   # Level 4+
        ]
        self.indent_char = "  "  # Two spaces for each level
        
    def format_items(self, items: List[Any]) -> str:
        """Format items as a hierarchical tree"""
        result = []
        
        # Create a map of items by ID for faster lookup
        item_map = {item.id: item for item in items}
        
        # Group items by section
        sections = {}
        section_order = []
        
        for item in items:
            section = getattr(item, 'section', None)
            if section and section not in section_order:
                section_order.append(section)
                
            if section not in sections:
                sections[section] = []
            sections[section].append(item)
            
        # Handle items with no section
        if None in sections:
            result.extend(self._format_section_items(None, sections[None], item_map))
            
        # Handle items with sections
        for section in section_order:
            # Add section header
            section_header = self._style_text(f"━━━ {section} ━━━", bold=True, blue=True)
            result.append(self._output_text(section_header))
            
            # Add all items in this section
            result.extend(self._format_section_items(section, sections[section], item_map))
            
        return "\n".join(result)
        
    def _format_section_items(self, section: Optional[str], items: List[Any], 
                              item_map: Dict[int, Any]) -> List[str]:
        """Format items within a section"""
        result = []
        
        # Find top-level items (those with no parent or parent outside this section)
        top_level = [item for item in items 
                     if not hasattr(item, 'parent_id') or 
                     not item.parent_id or 
                     item.parent_id not in item_map or
                     getattr(item_map[item.parent_id], 'section', None) != section]
        
        # Format each top-level item and its children
        for item in top_level:
            result.extend(self._format_item_tree(item, 0, items, item_map))
            
        return result
        
    def _format_item_tree(self, item: Any, depth: int, 
                         all_items: List[Any], 
                         item_map: Dict[int, Any]) -> List[str]:
        """Recursively format an item and its children"""
        result = []
        
        # Get the appropriate bullet style for this level
        bullet_idx = min(depth, len(self.bullet_styles) - 1)
        bullet_char, bullet_color = self.bullet_styles[bullet_idx]
        
        # Create the indentation
        indent = self.indent_char * depth
        
        # Style the bullet
        bullet = self._style_text(bullet_char, **{bullet_color: True})
        
        # Format the item text
        text = self._escape_markdown(item.content)
        line = f"{indent}{self._output_text(bullet)} {text}"
        result.append(line)
        
        # Find and format children
        children = [i for i in all_items 
                   if hasattr(i, 'parent_id') and 
                   i.parent_id == item.id]
        
        for child in children:
            result.extend(self._format_item_tree(child, depth + 1, all_items, item_map))
            
        return result


class MixedFormatter(FormatterBase):
    """Formats items using a mix of numbering and bullets"""
    
    def __init__(self, use_color: bool = True):
        super().__init__(use_color)
        self.indent_char = "  "  # Two spaces for each level
        
    def format_items(self, items: List[Any]) -> str:
        """Format items using numbers for top level and bullets for children"""
        result = []
        
        # Create a map of items by ID for faster lookup
        item_map = {item.id: item for item in items}
        
        # Group items by section
        sections = {}
        section_order = []
        
        for item in items:
            section = getattr(item, 'section', None)
            if section and section not in section_order:
                section_order.append(section)
                
            if section not in sections:
                sections[section] = []
            sections[section].append(item)
            
        # Handle items with no section
        if None in sections:
            result.extend(self._format_section_items(None, sections[None], item_map))
            
        # Handle items with sections
        for section in section_order:
            # Add section header
            section_header = self._style_text(f"━━━ {section} ━━━", bold=True, blue=True)
            result.append(self._output_text(section_header))
            
            # Add all items in this section
            result.extend(self._format_section_items(section, sections[section], item_map))
            
        return "\n".join(result)
        
    def _format_section_items(self, section: Optional[str], items: List[Any], 
                              item_map: Dict[int, Any]) -> List[str]:
        """Format items within a section"""
        result = []
        
        # Find top-level items (those with no parent or parent outside this section)
        top_level = [item for item in items 
                     if not hasattr(item, 'parent_id') or 
                     not item.parent_id or 
                     item.parent_id not in item_map or
                     getattr(item_map[item.parent_id], 'section', None) != section]
        
        # Number the top-level items
        for idx, item in enumerate(top_level, 1):
            # Style the number
            number = self._style_text(f"{idx}.", bold=True, green=True)
            
            # Format the item text
            text = self._escape_markdown(item.content)
            line = f"{self._output_text(number)} {text}"
            result.append(line)
            
            # Find and format children
            self._add_children(item, items, item_map, result, 1)
            
        return result
        
    def _add_children(self, parent: Any, all_items: List[Any], 
                     item_map: Dict[int, Any], result: List[str], depth: int) -> None:
        """Add all children of an item to the result list"""
        # Find children
        children = [i for i in all_items 
                   if hasattr(i, 'parent_id') and 
                   i.parent_id == parent.id]
        
        for child in children:
            # Create the indentation
            indent = self.indent_char * depth
            
            # Style the bullet (cyan for odd depths, blue for even)
            color = "cyan" if depth % 2 == 1 else "blue"
            bullet = self._style_text("•", **{color: True})
            
            # Format the item text
            text = self._escape_markdown(child.content)
            line = f"{indent}{self._output_text(bullet)} {text}"
            result.append(line)
            
            # Recursively add children
            self._add_children(child, all_items, item_map, result, depth + 1)


def create_formatter(style: str = "hierarchy", use_color: bool = True) -> FormatterBase:
    """Factory function to create the appropriate formatter based on style"""
    if style == "flat":
        return FlatFormatter(use_color=use_color)
    elif style == "mixed":
        return MixedFormatter(use_color=use_color)
    else:  # Default to hierarchy
        return HierarchicalFormatter(use_color=use_color) 