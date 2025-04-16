#!/usr/bin/env python3
"""
Enhanced Extractor Example

This script demonstrates how to use the enhanced extractor compared to the original lang-select parser.
It shows how the enhanced extractor handles complex structures better than the original parser.
"""

import sys
import os
from typing import List

# Try to import from lang_select
try:
    from lang_select.parser import extract_items as original_extract_items
    from lang_select.parser import SelectableItem
    has_lang_select = True
except ImportError:
    has_lang_select = False
    print("Warning: lang_select package not found. Only enhanced extractor will be used.")
    
# Import the enhanced extractor
from enhanced_extractor import EnhancedExtractor, SelectableItem as EnhancedItem


def print_items(title: str, items: List) -> None:
    """Print extracted items with a title"""
    print(f"\n{title} ({len(items)} items):")
    print("-" * (len(title) + 10))
    
    for item in items:
        # Handle both original and enhanced items
        if hasattr(item, 'section') and item.section:
            section_info = f" [Section: {item.section}]"
        else:
            section_info = ""
            
        if hasattr(item, 'level') and item.level > 0:
            level_info = f" [Level: {item.level}]"
        else:
            level_info = ""
            
        if hasattr(item, 'parent_id') and item.parent_id:
            parent_info = f" [Parent: {item.parent_id}]"
        else:
            parent_info = ""
            
        print(f"{item.id}. {item.content}{section_info}{level_info}{parent_info}")


def compare_extractors(text: str, title: str = "Sample Text") -> None:
    """Compare original and enhanced extractors on the same text"""
    print(f"\n{'=' * 50}")
    print(f"COMPARING EXTRACTORS ON: {title}")
    print(f"{'=' * 50}")
    
    # Print the text for reference
    print("\nINPUT TEXT:")
    print("-" * 20)
    print(text)
    
    # Extract with enhanced extractor
    enhanced_extractor = EnhancedExtractor()
    enhanced_items = enhanced_extractor.extract_items(text)
    print_items("ENHANCED EXTRACTOR RESULTS", enhanced_items)
    
    # Extract with original extractor if available
    if has_lang_select:
        original_items = original_extract_items(text)
        print_items("ORIGINAL EXTRACTOR RESULTS", original_items)
    

def example_1_simple_list():
    """Simple list example"""
    text = """
Here are some recommended books:
1. The Pragmatic Programmer
2. Clean Code
3. Design Patterns
4. Refactoring
5. The Clean Coder
    """
    compare_extractors(text, "Simple Numbered List")


def example_2_mixed_list():
    """Mixed list example"""
    text = """
Shopping List:
* Milk
* Eggs
- Bread
+ Cheese
• Apples
    """
    compare_extractors(text, "Mixed Bullet List")


def example_3_hierarchical_list():
    """Hierarchical list example"""
    text = """
Project Tasks:
1. Design phase
   a. Create wireframes
   b. Design database schema
   c. Choose color palette
2. Development phase
   a. Set up project structure
   b. Implement core features
      - User authentication
      - Data storage
      - API endpoints
   c. Create user interface
3. Testing phase
   a. Unit tests
   b. Integration tests
   c. User acceptance testing
    """
    compare_extractors(text, "Hierarchical List")


def example_4_sections():
    """Sections example"""
    text = """
# Project Overview

This document describes the project scope and timeline.

## Features

- User authentication
- Content management
- Analytics dashboard
- Reporting system

## Timeline

1. Week 1-2: Planning
2. Week 3-6: Development
3. Week 7-8: Testing
4. Week 9: Deployment

## Resources

Team members:
* Project Manager: Alice
* Lead Developer: Bob
* Designer: Charlie
* QA Engineer: Diana
    """
    compare_extractors(text, "Sections with Mixed Lists")


def example_5_complex_formatting():
    """Complex formatting example"""
    text = """
PROJET: Système de Gestion de Contenu

OBJECTIFS:
1) Créer une plateforme facile à utiliser
2) Permettre la collaboration en temps réel
3) Offrir des analyses avancées

FONCTIONNALITÉS:
• Authentification des utilisateurs
  - Connexion sociale
  - Authentification à deux facteurs
• Gestion de contenu
  - Éditeur WYSIWYG
  - Système de versions
• Tableaux de bord analytiques
• API RESTful

TECHNOLOGIES:
Frontend: React avec TypeScript
Backend: Node.js, Express
Base de données: MongoDB
Déploiement: Docker, Kubernetes

CALENDRIER:
Phase 1 (Q1): Conception et planification
Phase 2 (Q2): Développement du MVP
Phase 3 (Q3): Tests et améliorations
Phase 4 (Q4): Lancement et marketing
    """
    compare_extractors(text, "Complex Formatting (French)")


def example_6_no_obvious_list():
    """No obvious list example"""
    text = """
Project Description

The application aims to simplify document management. Users should be able to upload, categorize, and share documents. The system must include robust search capabilities.

Security is a primary concern. All data must be encrypted, and access controls should be granular. Performance is also important for large document repositories.

We need to support multiple file formats including PDF, DOCX, and images. Mobile access is required for on-the-go users.
    """
    compare_extractors(text, "No Obvious List Structure")


if __name__ == "__main__":
    # Run all examples
    example_1_simple_list()
    example_2_mixed_list()
    example_3_hierarchical_list()
    example_4_sections()
    example_5_complex_formatting()
    example_6_no_obvious_list()
    
    # If a file path is provided, extract from that file
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                text = f.read()
            compare_extractors(text, f"File: {file_path}")
        else:
            print(f"Error: File {file_path} not found") 