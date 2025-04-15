"""
Parser module for extracting selectable items from language model responses.
"""

import re
from typing import List, Dict, Any, Optional


class SelectableItem:
    """Represents an item that can be selected by the user"""
    def __init__(self, id: int, content: str, original_marker: str = None):
        self.id = id
        self.content = content
        self.original_marker = original_marker
    
    def __str__(self):
        return f"{self.id}. {self.content}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the item to a dictionary representation"""
        return {
            "id": self.id,
            "content": self.content,
            "original_marker": self.original_marker
        }


def extract_numbered_items(text: str) -> List[SelectableItem]:
    """Extract items that are already numbered (like '1. First, let's define...')"""
    # Match numbered items with various formats: '1.', '1)', '1 -', or just '1' followed by text
    pattern = r'^\s*(\d+)(?:[.)\s-]+)\s*(.+)$'
    items = []
    
    for line in text.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            number, content = match.groups()
            items.append(SelectableItem(int(number), content.strip(), original_marker=number))
    
    return items


def extract_bullet_items(text: str) -> List[SelectableItem]:
    """Extract items that are bulleted (•, *, -, etc.)"""
    # Match various bullet formats: •, *, -, +
    pattern = r'^\s*([•*\-+])\s+(.+)$'
    items = []
    
    for line in text.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            bullet, content = match.groups()
            # Assign sequential IDs to bullet points
            items.append(SelectableItem(len(items) + 1, content.strip(), original_marker=bullet))
    
    return items


def extract_potential_items_from_paragraphs(text: str) -> List[SelectableItem]:
    """Extract short paragraphs that might be list items but aren't explicitly formatted as such"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    items = []
    
    # Consider short paragraphs (less than 150 chars) that might be list items
    for line in lines:
        if 10 < len(line) < 150 and not line.startswith('>') and not re.match(r'^\s*\d+[.)\s-]', line) and not re.match(r'^\s*[•*\-+]', line):
            items.append(SelectableItem(len(items) + 1, line))
    
    return items


def extract_items(text: str) -> List[SelectableItem]:
    """
    Parse an LM response and extract items that can be presented as interactive selections.
    Returns a list of SelectableItems with consistent numbering.
    """
    # First try to find explicitly numbered items
    numbered_items = extract_numbered_items(text)
    
    # Then try to find bulleted items
    bulleted_items = extract_bullet_items(text)
    
    # Combine lists, ensuring consistent numbering
    all_items = []
    for i, item in enumerate(numbered_items + bulleted_items):
        all_items.append(SelectableItem(i+1, item.content, item.original_marker))
    
    # If no obvious items found, try to extract potential items from paragraphs
    if not all_items:
        all_items = extract_potential_items_from_paragraphs(text)
    
    return all_items 