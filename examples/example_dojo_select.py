#!/usr/bin/env python3
"""
Example implementation of the /select command for a chat application
"""

from lang_select import ResponseManager
import sys
import io

class ChatHistory:
    """Simple class to simulate a chat history"""
    def __init__(self):
        self.messages = []
    
    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})
    
    def get_messages(self):
        return self.messages


class ChatCommands:
    """Example of a chat command handler with /select implementation"""
    
    def __init__(self, chat_history):
        self.chat_history = chat_history
        
    def output(self, text):
        """Simulates sending output back to the user"""
        print(text)
    
    def cmd_select(self, args=None):
        """
        Implementation of the /select command.
        
        This command:
        1. Searches through the conversation history
        2. Finds the most recent message from the assistant
        3. Extracts the content of that message
        4. Uses lang-select to present selectable items to the user
        """
        # Find the most recent assistant message
        assistant_message = None
        for message in reversed(self.chat_history.get_messages()):
            if message["role"] == "assistant":
                assistant_message = message["content"]
                break
        
        if not assistant_message:
            self.output("No assistant messages found in the chat history.")
            return False
        
        # Create a response manager
        manager = ResponseManager()
        manager.store(assistant_message)
        
        # Capture feedback in a string buffer if you don't want it going to stdout directly
        # This is useful if you have a custom UI and don't want terminal output
        # (remove these lines if terminal output is fine)
        feedback_buffer = io.StringIO()
        selected = manager.select(tool="fzf", feedback=True, feedback_stream=feedback_buffer)
        feedback_text = feedback_buffer.getvalue()
        
        # Process the result
        if selected:
            # Send the selection back to the user
            self.output(f"Selected: {selected}")
            
            # Here you would do something with the selection
            # For example:
            # - Use it as input for another command
            # - Send it to a database
            # - Use it for a follow-up prompt
            
            # Log the action for debugging
            print(f"DEBUG: {manager.get_selection_summary()}", file=sys.stderr)
            
            return True
        else:
            self.output("No selection was made.")
            return False


def main():
    """Example main function"""
    # Create a simulated chat history
    history = ChatHistory()
    history.add_message("user", "Can you list some popular JavaScript frameworks?")
    history.add_message("assistant", """
Sure! Here are some popular JavaScript frameworks:

1. React - A library for building user interfaces
2. Angular - A platform for building mobile and desktop web applications
3. Vue.js - A progressive framework for building user interfaces
4. Express.js - A minimal and flexible Node.js web application framework
5. Next.js - A React framework for production
6. Svelte - A radical new approach to building user interfaces
7. Ember.js - A framework for ambitious web developers
8. Meteor - A full-stack JavaScript platform for developing modern apps
""")
    history.add_message("user", "/select")
    
    # Create the commands handler
    commands = ChatCommands(history)
    
    # Run the select command
    print("Running /select command:")
    commands.cmd_select()
    
    # Example of what you might do after selection
    print("\nAfter selection, you could use the selected item for further actions.")
    print("For example:")
    print("  - Use as input for another command")
    print("  - Save to a database")
    print("  - Use as context for a follow-up prompt")


if __name__ == "__main__":
    main() 