#!/usr/bin/env python3
"""
Examples of how to use the lang-select package programmatically
"""

import sys
import json

from lang_select import (
    extract_items, 
    select_item, 
    select_with_external,
    quick_select,
    select_to_json,
    ResponseManager
)

def basic_usage():
    """Basic usage example - extract and select items programmatically"""
    # Example LLM response text
    llm_response = """
Here are the key steps for implementing a REST API:
1. Define your API endpoints
2. Design your data models
3. Implement authentication
4. Write controller logic
5. Add input validation
6. Implement error handling
7. Write tests
8. Deploy your API
"""
    
    # Extract items from the response
    items = extract_items(llm_response)
    
    # Show the extracted items
    print(f"Found {len(items)} items:")
    for item in items:
        print(f"  {item}")
    
    # Let the user select an item using the built-in selector
    print("\nSelect an item using the built-in selector:")
    selected = select_item(items, "Choose a step")
    
    if selected:
        print(f"\nYou selected: {selected.content}")


def external_selector_example():
    """Example using external selection tools like fzf"""
    llm_response = """
Tasks for today:
- Send invoices to clients
- Review pull requests
- Update documentation
- Schedule team meeting
- Prepare demo for tomorrow
"""
    
    # Extract items from the response
    items = extract_items(llm_response)
    
    # Let the user select an item using fzf (if available)
    print("\nSelect a task using fzf (if available):")
    selected = select_with_external(items, tool="fzf", prompt="Choose a task")
    
    if selected:
        print(f"\nYou selected: {selected.content}")


def convenience_functions_example():
    """Example using the new convenience functions"""
    llm_response = """
Options for vacation destinations:
1. Beach resort in Hawaii 
2. Historical tour of Rome
3. Safari adventure in Kenya
4. Mountain retreat in Switzerland
5. Cultural exploration in Japan
"""
    
    # Using quick_select (one-liner)
    print("\nUsing quick_select:")
    selected = quick_select(llm_response, tool="auto")
    if selected:
        print(f"Selected: {selected}")

    # Using select_to_json
    print("\nUsing select_to_json:")
    json_result = select_to_json(llm_response)
    result = json.loads(json_result)
    if result["success"]:
        print(f"Selected: {result['selected']['content']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")


def response_manager_example():
    """Example using the ResponseManager"""
    # Create a response manager with a file to store recent responses
    manager = ResponseManager(recent_file="recent_response.txt")
    
    # Store a response
    llm_response = """
Recommended books:
- The Pragmatic Programmer
- Clean Code
- Design Patterns
- Refactoring
- Domain-Driven Design
"""
    manager.store(llm_response)
    
    # Select from the stored response with feedback enabled
    print("\nSelect from the stored response (with feedback):")
    selected = manager.select(tool="auto", feedback=True)
    
    # Get information about the selection
    selection_info = manager.get_selection_info()
    print("\nSelection information:")
    print(f"  Selected: {selection_info['selected']}")
    print(f"  Number of items: {selection_info['num_items']}")
    print(f"  Has selection: {selection_info['has_selection']}")
    
    # Get a summary of the selection
    summary = manager.get_selection_summary()
    print(f"\nSelection summary: {summary}")


def callback_example():
    """Example using callback functions with quick_select"""
    llm_response = """
Debugging strategies:
1. Add print statements
2. Use a debugger
3. Check logs
4. Reproduce the issue in isolation
5. Binary search through the code
"""
    
    # Define callback functions
    def on_success(selection):
        print(f"Success callback: You selected '{selection}'")
        
    def on_empty():
        print("Empty callback: No items found to select from")
        
    def on_cancel():
        print("Cancel callback: Selection was cancelled")
    
    # Use quick_select with callbacks
    print("\nUsing quick_select with callbacks:")
    result = quick_select(
        llm_response, 
        tool="auto",
        prompt="Choose a debugging strategy",
        on_success=on_success,
        on_empty=on_empty,
        on_cancel=on_cancel
    )


def cli_tool_integration_example():
    """Example showing how to integrate with a CLI tool that uses the /select command"""
    # This simulates a chat history with multiple messages
    chat_history = [
        {"role": "user", "content": "How do I optimize database queries?"},
        {"role": "assistant", "content": """
Here are several ways to optimize database queries:

1. Use proper indexing
2. Avoid SELECT *
3. Use query caching
4. Optimize JOINs
5. Use EXPLAIN to analyze query performance
6. Limit the number of rows returned
7. Use stored procedures for complex queries
8. Consider denormalization for read-heavy workloads
"""},
        {"role": "user", "content": "/select"}
    ]
    
    # Implement the /select command
    def cmd_select():
        # Find the most recent assistant message
        assistant_message = None
        for message in reversed(chat_history):
            if message["role"] == "assistant":
                assistant_message = message["content"]
                break
        
        if not assistant_message:
            print("No assistant messages found in chat history")
            return
        
        # Create a response manager
        manager = ResponseManager()
        manager.store(assistant_message)
        
        # Use select with feedback
        print("\nSelecting from most recent assistant message:")
        selected = manager.select(tool="auto", feedback=True)
        
        if selected:
            print(f"\nCommand result: Selected \"{selected}\"")
            # Here you would typically do something with the selection
            print("Now you can use this selection for your next operation!")
        else:
            print("\nCommand result: No selection was made")
            
        # Get a summary for logging
        print(f"\nLog entry: {manager.get_selection_summary()}")
    
    # Run the command
    cmd_select()


def example_has_selectable_content():
    """Example demonstrating the has_selectable_content method"""
    print("\n--- Example: Checking for Selectable Content ---")
    
    # Create a response manager
    manager = ResponseManager()
    
    # Response with selectable content
    response_with_items = """
    Here are some options:
    1. First option
    2. Second option
    3. Third option
    """
    
    # Response without selectable content
    response_without_items = """
    Thanks for your message. I'll get back to you soon.
    Have a great day!
    """
    
    # Check response with items
    manager.store(response_with_items)
    if manager.has_selectable_content():
        print("✅ Response contains selectable items.")
        print(f"   Number of items: {len(manager.get_items())}")
    else:
        print("❌ Response does not contain selectable items.")
    
    # Check response without items
    manager.store(response_without_items)
    if manager.has_selectable_content():
        print("✅ Response contains selectable items.")
        print(f"   Number of items: {len(manager.get_items())}")
    else:
        print("❌ Response does not contain selectable items.")


def main():
    """Run all examples"""
    try:
        # Run examples
        basic_usage()
        external_selector_example()
        convenience_functions_example()
        response_manager_example()
        callback_example()
        cli_tool_integration_example()
        example_has_selectable_content()
        
        return 0
    except KeyboardInterrupt:
        print("\nExamples interrupted.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 