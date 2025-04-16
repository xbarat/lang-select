# Lang Select

A utility for extracting and selecting items from language model responses.

## Overview

Lang Select is a tool that helps you:

1. Parse language model responses to extract numbered or bulleted lists
2. Present those items in an interactive selector
3. Use various selection interfaces (internal, fzf, overlay, etc.)
4. Select single items or multiple items at once
5. Extract hierarchical structure and section organization from complex text (v0.6.0+)
6. Visualize extracted content with different display styles and colorized output (v0.7.0+)

It's especially useful for interactive chat applications where you want to let users select from options provided by an LLM.

## Features

- Extract numbered lists (e.g., "1. First item", "2. Second item")
- Extract bulleted lists (e.g., "• First item", "* Second item")
- Interactive selection using:
  - Built-in terminal UI
  - External tools like fzf, gum, peco
  - Terminal overlay selection (v0.4.0+)
- Multi-selection support for all selection methods (v0.5.0+)
- Enhanced extraction capabilities (v0.6.0+):
  - Hierarchical list support (parent-child relationships)
  - Section recognition (markdown-style headers)
  - Additional format recognition (lettered lists, roman numerals, key-value pairs)
- Multiple display styles for visualizing extracted content (v0.7.0+):
  - Flat view: Simple bullet list with section labels
  - Hierarchical view: Indented structure with different bullet styles per level
  - Mixed view: Numbered top-level items with bulleted children
- Colorized output for better readability with proper ANSI handling (v0.7.1+)
- Programmatic API for use in applications
- Command-line interface for direct use
- Terminal content capture and selection (v0.4.0+)

## Installation

### Basic Installation

```bash
# From PyPI (if published)
pip install lang-select

# From GitHub
pip install git+https://github.com/xbarat/lang-select.git
```

### With Optional Dependencies

```bash
# With Rich for prettier output
pip install lang-select[rich]

# With Textual for overlay functionality
pip install lang-select[textual]

# With all optional dependencies
pip install lang-select[all]
```

## Command-Line Usage

### Basic Usage

```bash
# Select from a file
lang-select path/to/response.txt

# Select from stdin
cat response.txt | lang-select -

# Use a specific selection tool
lang-select --tool fzf response.txt

# Just print extracted items without selection
lang-select --print-only response.txt

# Output as JSON
lang-select --json response.txt
```

### Enhanced Extraction (v0.6.0+)

```bash
# Use enhanced extraction capabilities
lang-select --enhanced response.txt

# Print hierarchical items with section information
lang-select --enhanced --print-only response.txt

# Enhanced extraction with JSON output
lang-select --enhanced --json response.txt

# Use enhanced extraction with overlay and multi-selection
lang-select --enhanced --overlay --multi response.txt
```

### Multi-Selection (v0.5.0+)

```bash
# Enable multi-selection mode (works with all tools)
lang-select --multi response.txt

# Using multi-select with a specific tool
lang-select --tool fzf --multi response.txt

# Multi-selection with JSON output
lang-select --multi --json response.txt
```

### Overlay Selection (v0.4.0+)

```bash
# Use terminal overlay for selection
lang-select --overlay response.txt

# Use overlay with multi-selection
lang-select --overlay --multi response.txt

# Capture terminal content and select from it
lang-select --capture-terminal
```

### Display Styles

Lang Select supports multiple ways to display extracted content:

```bash
# Flat style (simple list with section labels)
lang-select --enhanced --view flat response.txt

# Hierarchical style (indented structure with different bullet styles)
lang-select --enhanced --view hierarchy response.txt

# Mixed style (numbered top-level items with bulleted children)
lang-select --enhanced --view mixed response.txt

# Disable colored output
lang-select --enhanced --view hierarchy --no-color response.txt
```

## Programmatic Usage

### Basic Usage

```python
from lang_select import extract_items, select_with_external

# Parse text to extract items
text = """
Here are some options:
1. First option
2. Second option
3. Third option
"""

items = extract_items(text)
selected = select_with_external(items, tool="fzf")

if selected:
    print(f"Selected: {selected.content}")
```

### Enhanced Extraction (v0.6.0+)

```python
from lang_select import extract_enhanced_items, EnhancedResponseManager

# Sample text with hierarchical structure and sections
text = """
# Project Tasks

1. Phase One
   a. Research requirements
   b. Create prototype
      i. Design UI mockups
      ii. Implement basic functionality

# Timeline
- Week 1: Planning
- Week 2: Development
- Week 3: Testing
"""

# Extract with hierarchy and section awareness
items = extract_enhanced_items(text)

# Print items with their structure
for item in items:
    indent = "  " * item.level
    section = f" [Section: {item.section}]" if item.section else ""
    parent = f" [Parent: {item.parent_id}]" if item.parent_id else ""
    print(f"{indent}{item.id}. {item.content}{section}{parent}")

# Use the enhanced response manager
manager = EnhancedResponseManager()
manager.store(text)

# Get items organized by section
sections = manager.get_sections()
for section_name, section_items in sections.items():
    print(f"\n=== {section_name} ===")
    for item in section_items:
        print(f"- {item.content}")
```

### Quick Selection

```python
from lang_select import quick_select

text = "1. Option one\n2. Option two\n3. Option three"
selected = quick_select(text)

# Use enhanced extraction
selected = quick_select(text, use_enhanced=True)

if selected:
    print(f"You selected: {selected}")
```

### Multi-Selection (v0.5.0+)

```python
from lang_select import quick_select

text = "1. Option one\n2. Option two\n3. Option three"
selected_items = quick_select(text, multi_select=True)

# With enhanced extraction
selected_items = quick_select(text, multi_select=True, use_enhanced=True)

if selected_items:
    print(f"You selected {len(selected_items)} items:")
    for item in selected_items:
        print(f"- {item}")
```

### Response Manager

```python
from lang_select import ResponseManager

# Create a manager (optionally with enhanced extraction)
manager = ResponseManager(use_enhanced=False)

# With enhanced extraction capabilities
enhanced_manager = ResponseManager(use_enhanced=True)

# Store a response
manager.store("1. First option\n2. Second option")

# Select from it
selected = manager.select(tool="fzf", feedback=True)

if selected:
    print(f"Selected: {selected}")
    
    # Get information about the selection
    info = manager.get_selection_info()
    print(f"Selection info: {info}")
```

### Multi-Selection with ResponseManager (v0.5.0+)

```python
from lang_select import ResponseManager

manager = ResponseManager()
manager.store("1. Option one\n2. Option two\n3. Option three")

# Select multiple items
selected_items = manager.select(multi_select=True, feedback=True)

if selected_items:
    print(f"Selected {len(selected_items)} items:")
    for item in selected_items:
        print(f"- {item}")
```

### Overlay Selection (v0.4.0+)

Terminal overlay selection provides a floating selection interface that appears on top of the terminal content.

```python
from lang_select import quick_overlay_select, is_overlay_available

# Check if overlay is available (requires textual)
if is_overlay_available():
    # Select from provided text
    selected = quick_overlay_select("1. Option one\n2. Option two")
    
    # Or capture terminal content and select from it
    selected = quick_overlay_select()
    
    # Multi-select with overlay (v0.5.0+)
    selected_items = quick_overlay_select("1. Option one\n2. Option two", multi_select=True)
    
    if selected:
        print(f"Selected: {selected}")
```

Using with ResponseManager:

```python
from lang_select import ResponseManager

manager = ResponseManager()
manager.store("1. Option one\n2. Option two")

# Use overlay selection
selected = manager.select_with_overlay()

# Multi-select with overlay (v0.5.0+)
selected_items = manager.select_with_overlay(multi_select=True)

if selected:
    print(f"Selected: {selected}")
```

### Using Formatters

```python
from lang_select import extract_enhanced_items, create_formatter

# Extract items from text
text = "Your LLM response with lists here..."
items = extract_enhanced_items(text)

# Use different formatters
from lang_select import FlatFormatter, HierarchicalFormatter, MixedFormatter

# Flat style
flat_formatter = FlatFormatter()
print(flat_formatter.format_items(items))

# Hierarchical style
hierarchical_formatter = HierarchicalFormatter()
print(hierarchical_formatter.format_items(items))

# Mixed style (numbered + bullets)
mixed_formatter = MixedFormatter()
print(mixed_formatter.format_items(items))

# Or use the factory function
formatter = create_formatter('hierarchy', use_color=True)
print(formatter.format_items(items))
```

## Integration Examples

### Chat Application Integration

```python
from lang_select import quick_select, ResponseManager

# Store the latest LLM response
manager = ResponseManager()

def handle_llm_response(response_text):
    """Handle a new response from the LLM"""
    manager.store(response_text)
    # Display the response to the user...

def handle_select_command(multi=False):
    """Handle when the user types /select or /multi-select"""
    selected = manager.select(tool="fzf", multi_select=multi)
    if selected:
        print(f"Selected: {selected}")
        return selected
    else:
        print("No selection made")
        return None
```

### Overlay Selection in Chat Applications

```python
from lang_select import ResponseManager, is_overlay_available

# Create a manager for LLM responses
manager = ResponseManager()

def handle_llm_response(response_text):
    """Store the LLM response when received"""
    manager.store(response_text)
    # Display the response...

def handle_select_command(multi=False):
    """Handle when the user types /select or /multi-select"""
    if is_overlay_available():
        # Use the overlay selector
        selected = manager.select_with_overlay(multi_select=multi)
    else:
        # Fall back to regular selection
        selected = manager.select(tool="fzf", multi_select=multi)
        
    if selected:
        return selected
    return None
```

### Terminal Content Capture

```python
from lang_select import quick_overlay_select

def capture_and_select(multi=False):
    """Capture terminal content and select from it"""
    selected = quick_overlay_select(multi_select=multi)
    
    if selected:
        print(f"Selected: {selected}")
    else:
        print("No selection made")
```

## Dependencies

- Core: No dependencies required
- Rich UI: [rich](https://github.com/textualize/rich) (optional)
- Terminal Overlay: [textual](https://github.com/textualize/textual) (optional)
- External selectors:
  - [fzf](https://github.com/junegunn/fzf) (optional)
  - [gum](https://github.com/charmbracelet/gum) (optional)
  - [peco](https://github.com/peco/peco) (optional)

## Version History

- **0.7.1** - Fixed ANSI color code handling for improved terminal compatibility
- **0.7.0** - Added multiple display styles (flat, hierarchy, mixed) with colorized output
- **0.6.0** - Added enhanced extraction with hierarchical structure and section support
- **0.5.0** - Added multi-selection support for all selection methods
- **0.4.1** - Added missing `has_selectable_content` method to fix integration issues
- **0.4.0** - Added terminal overlay selection and terminal content capture
- **0.3.0** - Added ResponseManager, improved feedback options
- **0.2.0** - Added quick_select and improved API
- **0.1.0** - Initial release with basic functionality

## License

MIT License

