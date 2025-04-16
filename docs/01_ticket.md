# Large gap between the user instruction and user selection panel
The code that displays the selection interface is controlled by the lang-select library rather than directly by aider's implementation. Let me examine how the selection tools are implemented in lang-select:
Let's look at the sample implementation of a selection interface using fzf to better understand where the gap might come from:
Let's look at the implementation of fzf in the actual lang-select library that might be responsible for the gap:
Since we can't access the full lang-select library code, I'll implement a fix based on what we can understand from the available code and the issue description.
The gap between the selection display and the instructions is likely happening because:
The fzf interface is being launched with some empty lines before or after the selection items
This is a UI issue in how the lang-select library integrates with fzf
Here's my solution:
Tool edit_file not found. Try switching to Agent mode.
I'll use the file_search tool to find the implementation of the selection tools in lang-select: