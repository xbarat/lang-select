#!/usr/bin/env python3
"""
Unit tests for the EnhancedExtractor class.

These tests verify that the enhanced extractor correctly identifies and extracts
items from various text formats, including different list styles, hierarchical structures,
and sections.
"""

import unittest
from enhanced_extractor import EnhancedExtractor

class TestEnhancedExtractor(unittest.TestCase):
    """Test cases for the EnhancedExtractor class"""
    
    def setUp(self):
        """Initialize the extractor before each test"""
        self.extractor = EnhancedExtractor()
    
    def test_simple_numbered_list(self):
        """Test extraction from a simple numbered list"""
        text = """
        1. First item
        2. Second item
        3. Third item
        """
        
        items = self.extractor.extract_items(text)
        
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].content, "First item")
        self.assertEqual(items[1].content, "Second item")
        self.assertEqual(items[2].content, "Third item")
        self.assertEqual(items[0].original_marker, "1.")
        self.assertEqual(items[1].original_marker, "2.")
        self.assertEqual(items[2].original_marker, "3.")
    
    def test_bullet_points(self):
        """Test extraction from bullet points"""
        text = """
        * First bullet
        - Second bullet
        + Third bullet
        • Fourth bullet
        """
        
        items = self.extractor.extract_items(text)
        
        self.assertEqual(len(items), 4)
        self.assertEqual(items[0].content, "First bullet")
        self.assertEqual(items[1].content, "Second bullet")
        self.assertEqual(items[2].content, "Third bullet")
        self.assertEqual(items[3].content, "Fourth bullet")
        self.assertEqual(items[0].original_marker, "*")
        self.assertEqual(items[1].original_marker, "-")
        self.assertEqual(items[2].original_marker, "+")
        self.assertEqual(items[3].original_marker, "•")
    
    def test_hierarchical_list(self):
        """Test extraction from a hierarchical list"""
        text = """
        1. Top level item
          a. Second level item
          b. Another second level item
            i. Third level item
        2. Another top level item
        """
        
        items = self.extractor.extract_items(text)
        
        self.assertEqual(len(items), 5)
        self.assertEqual(items[0].content, "Top level item")
        self.assertEqual(items[1].content, "Second level item")
        self.assertEqual(items[2].content, "Another second level item")
        self.assertEqual(items[3].content, "Third level item")
        self.assertEqual(items[4].content, "Another top level item")
        
        # Check levels
        self.assertEqual(items[0].level, 0)
        self.assertEqual(items[1].level, 1)
        self.assertEqual(items[2].level, 1)
        self.assertEqual(items[3].level, 2)
        self.assertEqual(items[4].level, 0)
        
        # Check parent-child relationships
        self.assertIsNone(items[0].parent_id)
        self.assertEqual(items[1].parent_id, 1)  # First item is parent of second
        self.assertEqual(items[2].parent_id, 1)  # First item is parent of third
        self.assertEqual(items[3].parent_id, 3)  # Third item is parent of fourth
        self.assertIsNone(items[4].parent_id)
    
    def test_deeply_nested_hierarchy(self):
        """Test extraction from a deeply nested list structure"""
        text = """
        1. Level 1
          a. Level 2
            i. Level 3
              * Level 4
                - Level 5
        """
        
        items = self.extractor.extract_items(text)
        
        self.assertEqual(len(items), 5)
        self.assertEqual(items[0].content, "Level 1")
        self.assertEqual(items[1].content, "Level 2")
        self.assertEqual(items[2].content, "Level 3")
        self.assertEqual(items[3].content, "Level 4")
        self.assertEqual(items[4].content, "Level 5")
        
        # Check levels
        self.assertEqual(items[0].level, 0)
        self.assertEqual(items[1].level, 1)
        self.assertEqual(items[2].level, 2)
        self.assertEqual(items[3].level, 2)  # Indentation-based level
        self.assertEqual(items[4].level, 2)  # Indentation-based level
    
    def test_section_recognition(self):
        """Test section recognition"""
        text = """
        # First Section
        1. Item in first section
        2. Another item in first section
        
        ## Subsection
        * Item in subsection
        * Another item in subsection
        
        # Second Section
        - Item in second section
        """
        
        items = self.extractor.extract_items(text)
        
        self.assertEqual(len(items), 6)
        self.assertEqual(items[0].section, "First Section")
        self.assertEqual(items[1].section, "First Section")
        self.assertEqual(items[2].section, "Subsection")
        self.assertEqual(items[3].section, "Subsection")
        self.assertEqual(items[4].section, "Second Section")
    
    def test_parenthesis_numbering(self):
        """Test extraction with parenthesis numbering"""
        text = """
        (1) First item
        (2) Second item
        (3) Third item
        """
        
        items = self.extractor.extract_items(text)
        
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].content, "First item")
        self.assertEqual(items[1].content, "Second item")
        self.assertEqual(items[2].content, "Third item")
        self.assertEqual(items[0].original_marker, "1")
        self.assertEqual(items[1].original_marker, "2")
        self.assertEqual(items[2].original_marker, "3")
    
    def test_roman_numerals(self):
        """Test extraction with Roman numeral formatting"""
        text = """
        i. First item
        ii. Second item
        iii. Third item
        iv. Fourth item
        """
        
        items = self.extractor.extract_items(text)
        
        self.assertEqual(len(items), 4)
        self.assertEqual(items[0].content, "First item")
        self.assertEqual(items[1].content, "Second item")
        self.assertEqual(items[2].content, "Third item")
        self.assertEqual(items[3].content, "Fourth item")
        self.assertEqual(items[0].original_marker, "i.")
        self.assertEqual(items[1].original_marker, "ii.")
        self.assertEqual(items[2].original_marker, "iii.")
        self.assertEqual(items[3].original_marker, "iv.")
    
    def test_key_value_pairs(self):
        """Test extraction of key-value pairs"""
        text = """
        Name: John Doe
        Age: 30
        Occupation: Developer
        """
        
        items = self.extractor.extract_items(text)
        
        self.assertEqual(len(items), 3)
        self.assertEqual(items[0].content, "Name: John Doe")
        self.assertEqual(items[1].content, "Age: 30")
        self.assertEqual(items[2].content, "Occupation: Developer")
    
    def test_mixed_formats(self):
        """Test extraction from a text with mixed formats"""
        text = """
        # Shopping List
        
        1. Groceries
          * Apples
          * Bananas
          * Bread
        
        2. Hardware
          a. Screws
          b. Nails
        
        # Tasks
        - Clean the house
        - Do laundry
        """
        
        items = self.extractor.extract_items(text)
        
        self.assertEqual(len(items), 9)
        
        # Check sections
        self.assertEqual(items[0].section, "Shopping List")
        self.assertEqual(items[7].section, "Tasks")
        
        # Check content
        self.assertEqual(items[0].content, "Groceries")
        self.assertEqual(items[1].content, "Apples")
        self.assertEqual(items[4].content, "Hardware")
        self.assertEqual(items[5].content, "Screws")
        self.assertEqual(items[7].content, "Clean the house")
    
    def test_no_list_items(self):
        """Test behavior when no list items are present"""
        text = """
        This is just a regular paragraph with no list items.
        It should not extract anything from this text.
        """
        
        items = self.extractor.extract_items(text)
        
        self.assertEqual(len(items), 0)


if __name__ == "__main__":
    unittest.main() 