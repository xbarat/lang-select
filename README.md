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
```

### Python API

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

## Integration Examples

### Using with LM responses directly

```python
import requests
from lang_select import extract_items, select_item

# Get a language model response
response = requests.post("https://api.example.com/llm", json={"prompt": "List 5 programming languages"})
text = response.json()["text"]

# Extract and select
items = extract_items(text)
selected = select_item(items)
if selected:
    print(f"You selected: {selected.content}")
```

### Integrating with other CLI tools

```python
import subprocess
from lang_select import extract_items, select_with_external

# Run an LM tool that outputs to stdout
result = subprocess.run(["llm-tool", "generate", "list of tasks"], capture_output=True, text=True)
text = result.stdout

# Extract and select with FZF
items = extract_items(text)
selected = select_with_external(items, tool="fzf")
if selected:
    # Use selected item as input to another tool
    subprocess.run(["task-manager", "add", selected.content])
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