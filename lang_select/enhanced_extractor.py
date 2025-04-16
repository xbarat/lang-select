#!/usr/bin/env python3
"""
Enhanced Extractor for Lang Select

This module provides an advanced extraction mechanism that can recognize various
list formats, hierarchical structures, and sections in text. It builds on the base
extraction capabilities of Lang Select by supporting additional patterns and maintaining
the hierarchical relationships between items.
"""

import re
from typing import List, Dict, Any, Optional, Tuple

from .parser import SelectableItem


class ExtendedSelectableItem(SelectableItem):
    """
    Extended version of SelectableItem that adds section, level, and parent_id fields
    to support hierarchical structures and section grouping.
    """
    def __init__(self, 
                id: int, 
                content: str, 
                original_marker: str = None, 
                section: Optional[str] = None,
                level: int = 0, 
                parent_id: Optional[int] = None):
        super().__init__(id, content, original_marker)
        self.section = section
        self.level = level
        self.parent_id = parent_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the item to a dictionary representation"""
        result = super().to_dict()
        result.update({
            "section": self.section,
            "level": self.level,
            "parent_id": self.parent_id
        })
        return result


class EnhancedExtractor:
    """
    Enhanced extractor for identifying and extracting selectable items from text.
    
    This extractor recognizes various list formats including:
    - Numbered lists (1., 2., 3., etc.)
    - Lettered lists (a., b., c., etc. and A., B., C., etc.)
    - Roman numerals (i., ii., iii., etc. and I., II., III., etc.)
    - Bullet points (*, -, +, •)
    - Parenthesized numbers ((1), (2), (3), etc.)
    - Key-value pairs (Key: Value)
    
    It also maintains hierarchical structure based on indentation and recognizes
    section headers for improved organization of extracted items.
    """
    
    def __init__(self):
        # Regular expressions for different list formats
        self.numbered_pattern = re.compile(r'^\s*(\d+)[\.)\s]\s*(.+)$')
        self.lettered_pattern = re.compile(r'^\s*([a-zA-Z])[\.)\s]\s*(.+)$')  # Match a., a), a 
        self.roman_pattern = re.compile(r'^\s*((?:i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)+)[\.)\s]\s*(.+)$')
        self.bullet_pattern = re.compile(r'^\s*([\*\-\+•])\s*(.+)$')  # More flexible spacing after bullet
        self.paren_number_pattern = re.compile(r'^\s*\((\d+)\)\s+(.+)$')
        self.key_value_pattern = re.compile(r'^\s*([^:]+):\s+(.+)$')
        
        # Pattern for section headers
        self.section_pattern = re.compile(r'^\s*(#{1,6})\s+(.+)$')
    
    def extract_items(self, text: str) -> List[SelectableItem]:
        """
        Extract selectable items from the given text.
        
        Args:
            text: The text to extract items from
            
        Returns:
            A list of SelectableItem objects representing the extracted items
        """
        lines = text.strip().split('\n')
        items = []
        current_section = None
        item_id = 0
        section_stack = []  # Keep track of section hierarchy
        
        # Process each line
        line_idx = 0
        while line_idx < len(lines):
            line = lines[line_idx].rstrip()
            line_idx += 1
            
            if not line.strip():
                continue
            
            # Check if line is a section header
            section_match = self.section_pattern.match(line)
            if section_match:
                level_markers, section_title = section_match.groups()
                level = len(level_markers)  # Get section level from number of # characters
                
                # Update section stack
                while section_stack and section_stack[-1][0] >= level:
                    section_stack.pop()
                
                section_stack.append((level, section_title.strip()))
                current_section = section_title.strip()
                continue
            
            # Try to match against known list patterns
            item_content, raw_prefix = self._match_list_item(line)
            
            if item_content is not None:
                item_id += 1
                
                # Get the indentation level based on visible whitespace
                line_indent = len(line) - len(line.lstrip())
                
                # Determine the logical level based on the marker type and indent
                level = 0
                if line_indent >= 2:
                    level = 1
                
                # Adjust level based on marker type
                marker_type = self._determine_marker_type(raw_prefix)
                if marker_type == "letter":
                    level = 1  # Letters are always level 1
                elif marker_type == "roman":
                    level = 2  # Roman numerals are always level 2
                
                # Find the parent based on the calculated level
                parent_id = self._find_parent_for_level(items, level)
                
                item = ExtendedSelectableItem(
                    id=item_id,
                    content=item_content,
                    original_marker=raw_prefix,
                    section=current_section,
                    level=level,
                    parent_id=parent_id
                )
                items.append(item)
        
        return items
    
    def _match_list_item(self, line: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Match a line against various list item patterns.
        
        Args:
            line: The line to match
            
        Returns:
            A tuple containing (item_content, raw_prefix) if a match is found, or (None, None) otherwise
        """
        # Try numbered pattern (1., 2., etc.)
        match = self.numbered_pattern.match(line)
        if match:
            return match.group(2), match.group(1) + "."
        
        # Try lettered pattern (a., b., etc.)
        match = self.lettered_pattern.match(line)
        if match:
            # Determine what follows the letter (. or ) or space)
            letter = match.group(1)
            rest_of_line = line.lstrip()[1:].lstrip()
            if rest_of_line.startswith('.'):
                return match.group(2), letter + "."
            elif rest_of_line.startswith(')'):
                return match.group(2), letter + ")"
            else:
                return match.group(2), letter
        
        # Try roman numeral pattern (i., ii., etc.)
        match = self.roman_pattern.match(line)
        if match:
            # Determine what follows the roman numeral (. or ) or space)
            numeral = match.group(1)
            rest_of_line = line.lstrip()[len(numeral):].lstrip()
            if rest_of_line.startswith('.'):
                return match.group(2), numeral + "."
            elif rest_of_line.startswith(')'):
                return match.group(2), numeral + ")"
            else:
                return match.group(2), numeral
        
        # Try bullet pattern (*, -, +, etc.)
        match = self.bullet_pattern.match(line)
        if match:
            return match.group(2), match.group(1)
        
        # Try parenthesized number pattern ((1), (2), etc.)
        match = self.paren_number_pattern.match(line)
        if match:
            return match.group(2), match.group(1)
        
        # Try key-value pattern (Key: Value)
        match = self.key_value_pattern.match(line)
        if match and not self._is_likely_section_header(line):
            return f"{match.group(1)}: {match.group(2)}", ""
        
        # Check if it resembles a list item even if it doesn't match explicit patterns
        if self._resembles_list_item(line):
            return line.strip(), ""
        
        return None, None
    
    def _is_likely_section_header(self, line: str) -> bool:
        """
        Check if a line is likely to be a section header rather than a key-value pair.
        
        Args:
            line: The line to check
            
        Returns:
            True if the line is likely a section header, False otherwise
        """
        stripped = line.strip()
        if not stripped.endswith(':'):
            return False
        
        # If there's no space after the colon, it's likely a section header
        if ':' in stripped and not stripped.split(':', 1)[1].strip():
            return True
        
        return False
    
    def _resembles_list_item(self, line: str) -> bool:
        """
        Check if a line resembles a list item even if it doesn't match explicit patterns.
        
        Args:
            line: The line to check
            
        Returns:
            True if the line resembles a list item, False otherwise
        """
        stripped = line.strip()
        
        # Check for emoji/unicode bullet point patterns not covered by bullet_pattern
        if re.match(r'^\s*[^\w\s]\s+.+$', stripped):
            return True
        
        # Check for simple dash or asterisk that might not be properly spaced
        if stripped.startswith('-') or stripped.startswith('*'):
            return True
        
        return False
    
    def _determine_marker_type(self, marker: str) -> str:
        """
        Determine the type of marker being used.
        
        Args:
            marker: The marker string
            
        Returns:
            A string representing the marker type: "number", "letter", "roman", "bullet", or "other"
        """
        if not marker:
            return "other"
        
        # Clean the marker (remove punctuation)
        clean_marker = marker.rstrip('.)]')
        
        # Check for letter markers
        if len(clean_marker) == 1 and clean_marker.isalpha():
            return "letter"
        
        # Check for number markers
        if clean_marker.isdigit():
            return "number"
        
        # Check for roman numeral markers
        roman_pattern = r'^(?:i|ii|iii|iv|v|vi|vii|viii|ix|x|xi|xii|I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)$'
        if re.match(roman_pattern, clean_marker):
            return "roman"
        
        # Check for bullet markers
        if clean_marker in '*-+•':
            return "bullet"
        
        return "other"
    
    def _find_parent_for_level(self, items: List[SelectableItem], current_level: int) -> Optional[int]:
        """
        Find the parent ID for an item with the given level.
        
        Args:
            items: The list of items processed so far
            current_level: The level of the current item
            
        Returns:
            The ID of the parent item, or None if there is no parent
        """
        if current_level == 0 or not items:
            return None
        
        # For indentation-based hierarchy
        for i in range(len(items) - 1, -1, -1):
            if hasattr(items[i], 'level'):
                # The parent is the closest item with a level one less than current
                if items[i].level == current_level - 1:
                    return items[i].id
        
        # If no direct parent found, look for any valid ancestor
        for i in range(len(items) - 1, -1, -1):
            if hasattr(items[i], 'level') and items[i].level < current_level:
                return items[i].id
        
        return None


class EnhancedResponseManager:
    """Enhanced version of ResponseManager with better extraction capabilities"""
    
    def __init__(self):
        """Initialize the enhanced response manager"""
        self.extractor = EnhancedExtractor()
        self.recent_response = None
        self.last_items = []
    
    def store(self, text: str) -> None:
        """
        Store text and extract items from it
        
        Args:
            text: Text to store and extract items from
        """
        self.recent_response = text
        self.last_items = self.extractor.extract_items(text)
    
    def get_items(self) -> List[SelectableItem]:
        """
        Get the extracted items
        
        Returns:
            List of SelectableItem objects
        """
        return self.last_items
    
    def get_sections(self) -> Dict[str, List[SelectableItem]]:
        """
        Get items grouped by section
        
        Returns:
            Dictionary of section name to list of items
        """
        sections = {}
        
        for item in self.last_items:
            section = item.section if hasattr(item, 'section') and item.section else "Unsectioned"
            if section not in sections:
                sections[section] = []
            sections[section].append(item)
        
        return sections


# Convenience function to extract items with the enhanced extractor
def extract_enhanced_items(text: str) -> List[SelectableItem]:
    """
    Extract items from text using the enhanced extractor.
    
    This function provides all the capabilities of the enhanced extractor,
    including recognition of hierarchical lists, sections, and various list formats.
    
    Args:
        text: The text to extract items from
        
    Returns:
        A list of SelectableItem objects representing the extracted items
    """
    extractor = EnhancedExtractor()
    return extractor.extract_items(text) 