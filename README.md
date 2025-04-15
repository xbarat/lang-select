# Lang Select

A Python package to extract selectable items from language model responses and present them for interactive selection.

## Installation

```bash
pip install lang-select
```

For enhanced UI, install with Rich:

```bash
pip install lang-select[rich]
```

## Usage

### Command Line

```bash
# Basic usage
lang-select response.txt

# Use specific tool
lang-select response.txt --tool fzf

# Just print extracted items
lang-select response.txt --print-only

# Output JSON for scripting
lang-select response.txt --json

# Read from stdin
cat response.txt | lang-select -

# Use a recent response file
lang-select --recent recent_response.txt

# Save the current input for future use
lang-select response.txt --save-recent recent_response.txt
```

### Python API

#### Basic Usage

```python
from lang_select import extract_items, select_item

# Read text from somewhere
with open("response.txt", "r") as f:
    text = f.read()

# Extract selectable items
items = extract_items(text)

# Display for selection
selected = select_item(items, "Choose an option")
if selected:
    print(f"Selected: {selected.content}")

# Or use external tools (fzf, gum, peco)
from lang_select import select_with_external
selected = select_with_external(items, tool="fzf")
```

#### New Simplified API (v0.2+)

```python
from lang_select import quick_select

# One-liner to extract and select in a single call
text = "1. Option one\n2. Option two\n3. Option three"
selected = quick_select(text, tool="fzf")
if selected:
    print(f"Selected: {selected}")  # Returns the content string directly
```

#### With Callback Functions

```python
from lang_select import quick_select

# Define callback functions for different outcomes
def on_success(selection):
    print(f"Success! You selected: {selection}")
    
def on_empty():
    print("No selectable items found")
    
def on_cancel():
    print("Selection was cancelled")

# Use with callbacks
selected = quick_select(
    text,
    tool="fzf",
    on_success=on_success,
    on_empty=on_empty,
    on_cancel=on_cancel
)
```

#### JSON Output

```python
from lang_select import select_to_json
import json

# Get result as JSON
json_result = select_to_json(text)
result = json.loads(json_result)

if result["success"]:
    print(f"Selected: {result['selected']['content']}")
else:
    print(f"Error: {result.get('error')}")
```

#### Response Manager for Recent Responses

```python
from lang_select import ResponseManager

# Create a manager (optionally with file storage)
manager = ResponseManager(recent_file="recent_response.txt")

# Store a response
manager.store(llm_response)

# Later, select from the stored response with feedback
selected = manager.select(tool="fzf", feedback=True)
if selected:
    # Process the selection
    print(f"Selected: {selected}")

# Get comprehensive information about the selection
info = manager.get_selection_info()
print(f"Selected: {info['selected']}")
print(f"Number of items: {info['num_items']}")
print(f"Has selection: {info['has_selection']}")

# Get a human-readable summary for logging
summary = manager.get_selection_summary()
print(f"Summary: {summary}")
```

## Features

- Extracts selectable items from various language model response formats:
  - Numbered lists (1., 1), 1 -, etc.)
  - Bulleted lists (•, *, -, +)
  - Short paragraph items
- Multiple selection interfaces:
  - Built-in terminal UI
  - Rich-enhanced UI (if installed)
  - External tools (fzf, gum, peco)
- Easy integration with other Python code or scripts
- NEW! Simplified API for common use cases:
  - One-liner `quick_select()` function
  - JSON output with `select_to_json()`
  - `ResponseManager` for handling recent LLM responses
- NEW! Comprehensive feedback mechanisms:
  - Callback functions for different outcomes
  - Detailed selection information
  - Human-readable summaries for logging

## Integration Examples

### Using with LM responses directly

```python
import requests
from lang_select import quick_select

# Get a language model response
response = requests.post("https://api.example.com/llm", json={"prompt": "List 5 programming languages"})
text = response.json()["text"]

# Extract and select in one line
selected = quick_select(text)
if selected:
    print(f"You selected: {selected}")
```

### CLI Tools with /select Command

```python
from lang_select import ResponseManager

# Sample chat history
chat_history = [
    {"role": "user", "content": "How do I optimize a database?"},
    {"role": "assistant", "content": "1. Add indexes\n2. Optimize queries\n3. Use caching"},
    {"role": "user", "content": "/select"}
]

# Implement /select command
def cmd_select():
    # Find most recent assistant message
    for msg in reversed(chat_history):
        if msg["role"] == "assistant":
            # Create manager and store the message
            manager = ResponseManager()
            manager.store(msg["content"])
            
            # Select with feedback
            selected = manager.select(tool="fzf", feedback=True)
            
            # Log the result
            print(f"Log: {manager.get_selection_summary()}")
            
            # Return the selection for further processing
            return selected
            
    print("No assistant messages found")
    return None
```

### Integrating with other CLI tools

```python
import subprocess
from lang_select import ResponseManager

# Create a manager for working with responses
manager = ResponseManager()

# Run an LM tool that outputs to stdout
result = subprocess.run(["llm-tool", "generate", "list of tasks"], capture_output=True, text=True)
text = result.stdout

# Store the response
manager.store(text)

# Select with FZF
selected = manager.select(tool="fzf")
if selected:
    # Use selected item as input to another tool
    subprocess.run(["task-manager", "add", selected])
```

## One-liner Examples

Extract numbered items from a file and pipe to fzf:

```bash
grep -E '^\s*[0-9]+[.)\s-]' response.txt | sed -E 's/^\s*[0-9]+[.)\s-]+\s*//' | fzf
```

Extract bullet points from a file and choose with gum:

```bash
grep -E '^\s*[•*\-+]' response.txt | sed -E 's/^\s*[•*\-+]\s+//' | gum choose
```

## License

MIT 