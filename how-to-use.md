# Interactive Selection with lang-select

Aider integrates with [lang-select](https://github.com/xbarat/lang-select), a powerful tool that helps you select options from LLM responses.

## Installation

To use the enhanced interactive selection feature, you need to install the lang-select library:

```bash
pip install git+https://github.com/xbarat/lang-select.git
```

For the best experience, also install fzf:
```bash
# macOS
brew install fzf

# Linux
apt install fzf  # Debian/Ubuntu
```

## Usage

When an LLM response contains structured options like numbered lists, bullet points, or other selectable items, you can use the `/select` command to interactively choose which options you want.

### Example

1. Get a response from the LLM that contains structured options:

```
Here are some JavaScript frameworks:

1. React - A library for building user interfaces
2. Angular - A platform for building mobile and desktop web applications
3. Vue.js - A progressive framework for building user interfaces
4. Express.js - A minimal and flexible Node.js web application framework
5. Next.js - A React framework for production
```

2. Type `/select` and press Enter

3. An interactive selection UI will appear, allowing you to navigate and select options

4. Your selections will be sent back to the LLM as a new user message

## Selection Tools

The integration supports multiple selection tools:

- `internal`: A simple built-in selector (default fallback)
- `fzf`: A powerful fuzzy finder with search capabilities (recommended)
- `overlay`: A terminal overlay selector (when textual is installed)

If one selection tool fails, the system will automatically try an alternative.

## How It Works

The lang-select library uses advanced parsing techniques to identify selectable content in LLM responses. It automatically handles various formats including:

- Numbered lists
- Bullet points
- Short paragraphs
- And more

The key methods used in the integration are:

- `ResponseManager()` - Creates a manager for handling selections
- `store(content)` - Stores the text content to be analyzed 
- `has_selectable_content()` - Checks if there are items that can be selected
- `select(tool="fzf", feedback=True)` - Presents an interactive selection UI
- `get_selection_summary()` - Returns a formatted summary of what was selected
- `get_items()` - Returns the list of extractable items

This provides a much more robust selection experience compared to relying on regex patterns alone.

## Troubleshooting

If you encounter issues with the selection tool:

1. Make sure lang-select is properly installed with `pip install git+https://github.com/xbarat/lang-select.git`
2. For the `fzf` selector, ensure you have fzf installed on your system
3. Check if your terminal supports the required interactive features
4. Try using `/select` on a different LLM response with clearly structured content
