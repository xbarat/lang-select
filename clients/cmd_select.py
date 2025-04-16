# example snippet of a command line tool that uses lang-select (imports not included, ignore them)
   def cmd_select(self, args):
        """
        Present an interactive selection menu using lang-select.
        Uses fzf as the default selection interface and enables multi-selection by default.
        Now with enhanced extraction support for hierarchical lists and sections.
        """
        # Default to multi-select mode unless explicitly disabled
        multi_select = True
        use_enhanced = True  # Default to using enhanced extraction
        if args.strip().startswith("--single"):
            multi_select = False
            # Remove the flag from args
            args = args.strip().replace("--single", "", 1).strip()
        
        if args.strip().startswith("--basic"):
            use_enhanced = False
            # Remove the flag from args
            args = args.strip().replace("--basic", "", 1).strip()
        
        # Find the latest assistant message
        all_messages = self.coder.done_messages + self.coder.cur_messages
        assistant_messages = [msg for msg in reversed(all_messages) if msg["role"] == "assistant"]
        
        if not assistant_messages:
            self.io.tool_error("No assistant messages found to extract options from.")
            return
        
        last_message = assistant_messages[0]["content"]
        
        # Enforce the use of lang-select
        try:
            from lang_select import ResponseManager, extract_items, extract_enhanced_items
        except ImportError:
            self.io.tool_error("This command requires lang-select. Installing it now...")
            
            # Attempt to install lang-select automatically
            try:
                import subprocess
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", 
                    "git+https://github.com/xbarat/lang-select.git"
                ])
                self.io.tool_output("Successfully installed lang-select.")
                
                # Import after installation
                from lang_select import ResponseManager, extract_items, extract_enhanced_items
            except Exception as e:
                self.io.tool_error(f"Failed to install lang-select: {str(e)}")
                self.io.tool_error("Please install manually: pip install git+https://github.com/xbarat/lang-select.git")
                return
        
        # Create a response manager with enhanced extraction if requested
        manager = ResponseManager(use_enhanced=use_enhanced)
        manager.store(last_message)
        
        # Get items and check if we have any selectable content
        selectable_items = manager.get_items()
        
        # If no items were found and we're not already using enhanced extraction, try it
        if not selectable_items and not use_enhanced:
            self.io.tool_warning("Standard extraction found no items, trying enhanced extraction...")
            manager = ResponseManager(use_enhanced=True)
            manager.store(last_message)
            selectable_items = manager.get_items()
        
        # If still no items are found, try a more aggressive approach with all-caps section detection
        if not selectable_items:
            self.io.tool_warning("Enhanced extraction found no items, trying additional strategies...")
            
            # Custom extraction for special cases like all-caps sections
            lines = last_message.split('\n')
            custom_text = []
            
            # Process each line looking for all-caps headers to convert to markdown format
            current_section = None
            for line in lines:
                stripped = line.strip()
                # Skip empty lines
                if not stripped:
                    continue
                    
                # Check for section headings in ALL CAPS (without markdown #)
                if stripped.isupper() and len(stripped) > 3 and len(stripped) < 50:
                    # Convert to markdown format for the enhanced extractor
                    custom_text.append(f"# {stripped}")
                    continue
                
                # Add all other lines as-is
                custom_text.append(line)
            
            # Try extracting from the modified text
            manager = ResponseManager(use_enhanced=True)
            manager.store("\n".join(custom_text))
            selectable_items = manager.get_items()
        
        # If still no items, give up
        if not selectable_items:
            self.io.tool_error("No selectable options found in the last assistant message.")
            return
        
        # Check if fzf is available
        import shutil
        if not shutil.which("fzf"):
            self.io.tool_warning("fzf is not installed. For best experience, please install fzf:")
            self.io.tool_warning("- macOS: brew install fzf")
            self.io.tool_warning("- Linux: apt-get install fzf")
            self.io.tool_warning("- Windows: scoop install fzf")
            self.io.tool_warning("Falling back to internal selector...")
            selection_tool = "internal"
        else:
            selection_tool = "fzf"
        
        # Announce the selection mode and stats
        self.io.tool_output(f"Using lang-select with {selection_tool} interface...")
        self.io.tool_output(f"Mode: {'multi-selection' if multi_select else 'single selection'}")
        
        # Count items by section if using enhanced extractor
        if hasattr(manager, 'get_sections'):
            sections = manager.get_sections()
            if len(sections) > 1:  # Only show section breakdown if there are multiple sections
                self.io.tool_output(f"Found {len(selectable_items)} selectable items across {len(sections)} sections:")
                for section_name, items in sections.items():
                    self.io.tool_output(f"  - {section_name}: {len(items)} items")
            else:
                self.io.tool_output(f"Found {len(selectable_items)} selectable items")
        else:
            self.io.tool_output(f"Found {len(selectable_items)} selectable items")
        
        if multi_select and selection_tool == "fzf":
            self.io.tool_output("Press TAB to select multiple items, ENTER to confirm")
        elif multi_select:
            self.io.tool_output("Use SPACE to select multiple items, ENTER to confirm")
        
        # Perform the selection
        selected = manager.select(
            tool=selection_tool,
            multi_select=multi_select,
            feedback=False  # We'll handle our own feedback
        )
        
        if selected:
            # Format the selection feedback
            if multi_select:
                num_selected = len(selected)
                selections_list = ", ".join(selected)
                feedback = f"I've selected {num_selected} items: {selections_list}"
                self.io.tool_output(f"You selected {num_selected} options")
            else:
                feedback = f"I've selected: {selected}"
                self.io.tool_output(f"You selected: {selected}")
            
            # Send the selection back to the LLM
            list(self.coder.send_message(feedback))
            return
        else:
            self.io.tool_error("No selection made.")
