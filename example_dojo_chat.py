#!/usr/bin/env python3
"""
Example integration with a Dojo chat interface
"""

from lang_select import ResponseManager, quick_select
import sys

class Coder:
    """Simulates the Dojo coder class mentioned in the query"""
    
    def __init__(self):
        # This simulates the chat history
        self.cur_messages = []
    
    def send_text(self, text):
        """Simulates sending text back to the user"""
        print(f"[CODER OUTPUT]: {text}")
    
    def add_message(self, role, content):
        """Add a message to the history"""
        self.cur_messages.append({"role": role, "content": content})


class Commands:
    """Commands class that implements the /select command as described in the query"""
    
    def __init__(self, coder):
        self.coder = coder
    
    def cmd_select(self, args=None):
        """
        Implementation of the /select command as described in the user query:
        
        - Searches through the current conversation history (self.coder.cur_messages)
        - Finds the most recent message from the assistant
        - Extracts the content of that message
        - Uses lang-select to present selectable items
        """
        # Find the most recent message from the assistant
        assistant_message = None
        for message in reversed(self.coder.cur_messages):
            if message.get("role") == "assistant":
                assistant_message = message.get("content", "")
                break
        
        if not assistant_message:
            self.coder.send_text("No assistant messages found in the conversation.")
            return False
        
        # Option 1: Using ResponseManager with feedback
        manager = ResponseManager()
        manager.store(assistant_message)
        
        selected = manager.select(tool="fzf", feedback=True)
        
        if selected:
            self.coder.send_text(f"Selected: {selected}")
            
            # Log the selection for debugging
            print(f"DEBUG: {manager.get_selection_summary()}", file=sys.stderr)
            return True
        else:
            self.coder.send_text("No selection was made or no items were found.")
            return False
        
        # Option 2: Using quick_select (simpler, less features)
        # Uncomment this and comment out the ResponseManager code above to use this instead
        """
        selected = quick_select(
            assistant_message,
            tool="fzf",
            on_success=lambda s: print(f"DEBUG: Selected '{s}'", file=sys.stderr),
            on_empty=lambda: print("DEBUG: No items found", file=sys.stderr),
            on_cancel=lambda: print("DEBUG: Selection cancelled", file=sys.stderr)
        )
        
        if selected:
            self.coder.send_text(f"Selected: {selected}")
            return True
        else:
            self.coder.send_text("No selection was made or no items were found.")
            return False
        """


def main():
    """Example usage"""
    # Create a coder instance
    coder = Coder()
    
    # Add some example chat messages
    coder.add_message("user", "What are some key steps for deploying a web application?")
    coder.add_message("assistant", """
Here are the key steps for deploying a web application:

1. Set up version control
2. Choose a hosting provider
3. Configure your environment
4. Set up a CI/CD pipeline
5. Configure a domain name
6. Set up SSL certificates
7. Deploy your application
8. Monitor performance and logs
9. Set up backups
10. Implement security measures
""")
    coder.add_message("user", "/select")
    
    # Create the commands handler
    commands = Commands(coder)
    
    # Execute the /select command
    print("\nRunning /select command...")
    commands.cmd_select()
    
    # Example of what you might do after selection
    print("\nThe selected item could now be used for various purposes:")
    print("  - Generating more details about this specific step")
    print("  - Creating a task in your project management system")
    print("  - Adding the item to your notes or documentation")


if __name__ == "__main__":
    main() 