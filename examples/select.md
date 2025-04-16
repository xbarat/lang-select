## Add as cmd_select in lang_select/commands.py
def cmd_select(self, args):
        "Select options from the last assistant message using an interactive UI"
        if not self.coder.cur_messages:
            self.io.tool_error("No conversation history to select from.")
            return

        # Find the last assistant message
        for msg in reversed(self.coder.cur_messages):
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                break
        else:
            self.io.tool_error("No assistant messages found in the conversation.")
            return

        # Check if lang-select is available
        if not self.lang_select_available:
            self.io.tool_error("The lang-select package is not installed. Please install it with:")
            self.io.tool_error("pip install git+https://github.com/xbarat/lang-select.git")
            return
            
        # Use lang-select for option detection and selection
        try:
            from lang_select import ResponseManager
            
            # Create a response manager and store the assistant's message
            manager = ResponseManager()
            manager.store(content)
            
            # Check if any options were detected - use a safe approach instead of has_selectable_content
            try:
                # Try to generate a selection summary - if empty, no selectable content
                test_summary = manager.get_selection_summary()
                has_content = bool(test_summary) or len(manager.get_selectable_content()) > 0
                if not has_content:
                    self.io.tool_error("No structured options detected in the last assistant message.")
                    return
            except Exception:
                # If we can't check for content, we'll just try to select and see if it works
                pass
                
            self.io.tool_output("Interactive options detected. Press Enter to continue to the selection menu...")
            input()  # Give the user a moment to read the full response
            
            # Determine the best selection tool to use (choose is simpler, fzf is more powerful)
            selection_tool = "choose"  # Simpler option that works in more environments
            
            try:
                # Present the options for selection
                selected = manager.select(tool=selection_tool, feedback=True)
                
                if not selected:
                    self.io.tool_output("No options were selected.")
                    return
                
                # Get a summary of what was selected
                selection_summary = manager.get_selection_summary()
                if selection_summary:
                    # Format the selections for a nice message to the LLM
                    formatted_selections = f"I've selected the following option(s):\n\n{selection_summary}"
                    
                    # Add the selections as a new user message
                    self.coder.cur_messages.append(dict(role="user", content=formatted_selections))
                    self.io.tool_output("Your selections have been added to the conversation.")
                else:
                    self.io.tool_output("No valid selections were made.")
                
            except Exception as e:
                self.io.tool_error(f"Error during selection: {str(e)}")
                
                # Try an alternative selector if available
                try:
                    self.io.tool_output("Trying alternative selection method...")
                    alternative_tool = "fzf" if selection_tool == "choose" else "choose"
                    selected = manager.select(tool=alternative_tool, feedback=True)
                    
                    if not selected:
                        self.io.tool_output("No options were selected.")
                        return
                    
                    selection_summary = manager.get_selection_summary()
                    if selection_summary:
                        formatted_selections = f"I've selected the following option(s):\n\n{selection_summary}"
                        self.coder.cur_messages.append(dict(role="user", content=formatted_selections))
                        self.io.tool_output("Your selections have been added to the conversation.")
                    else:
                        self.io.tool_output("No valid selections were made.")
                except Exception as e2:
                    self.io.tool_error(f"Alternative selection also failed: {str(e2)}")
                    self.io.tool_error("Please check that fzf or another selection tool is installed.")
                
        except Exception as e:
            self.io.tool_error(f"Error with lang-select: {str(e)}")
            self.io.tool_error("Please check your lang-select installation or reinstall with:")
            self.io.tool_error("pip install git+https://github.com/xbarat/lang-select.git")
