# example snippet of a command line tool that uses lang-select (imports not included, ignore them)

def cmd_select(self, args):
    """
    Present an interactive selection menu using lang-select.
    
    Features:
    - Uses fzf as the default selection interface
    - Enables multi-selection by default
    - Enhanced extraction for hierarchical lists and sections
    - Multiple display styles (flat, hierarchy, mixed)
    - Colorized output for better readability
    
    Usage:
      /select                   - Multi-select with enhanced extraction and hierarchical view
      /select --single          - Single-select with enhanced extraction
      /select --basic           - Use basic extraction (no hierarchy or sections)
      /select --flat            - Use flat display style
      /select --mixed           - Use mixed display style (numbers + bullets)
      /select --no-color        - Disable colorized output
    """
    # Parse arguments
    multi_select = True
    use_enhanced = True  # Default to using enhanced extraction
    display_style = "hierarchy"  # Default to hierarchical view
    use_color = True  # Default to colorized output
    
    # Process flags
    args_text = args.strip()
    
    if args_text.startswith("--single"):
        multi_select = False
        args_text = args_text.replace("--single", "", 1).strip()
    
    if args_text.startswith("--basic") or "--basic" in args_text.split():
        use_enhanced = False
        args_text = args_text.replace("--basic", "", 1).strip()
    
    if args_text.startswith("--flat") or "--flat" in args_text.split():
        display_style = "flat"
        args_text = args_text.replace("--flat", "", 1).strip()
    
    if args_text.startswith("--mixed") or "--mixed" in args_text.split():
        display_style = "mixed"
        args_text = args_text.replace("--mixed", "", 1).strip()
    
    if args_text.startswith("--no-color") or "--no-color" in args_text.split():
        use_color = False
        args_text = args_text.replace("--no-color", "", 1).strip()
    
    # Find the latest assistant message
    all_messages = self.coder.done_messages + self.coder.cur_messages
    assistant_messages = [msg for msg in reversed(all_messages) if msg["role"] == "assistant"]
    
    if not assistant_messages:
        self.io.tool_error("No assistant messages found to extract options from.")
        return
    
    last_message = assistant_messages[0]["content"]
    
    # Enforce the use of lang-select
    try:
        # Import core functionality
        from lang_select import ResponseManager, extract_items, extract_enhanced_items, select_with_external
        
        # Try to import formatters (will be available in v0.7.0+)
        try:
            from lang_select import create_formatter, FlatFormatter, HierarchicalFormatter, MixedFormatter
            formatters_available = True
        except ImportError:
            formatters_available = False
            
    except ImportError:
        self.io.tool_error("This command requires lang-select. Installing it now...")
        
        # Attempt to install lang-select automatically
        try:
            import subprocess
            import sys
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "git+https://github.com/xbarat/lang-select.git"
            ])
            self.io.tool_output("Successfully installed lang-select.")
            
            # Import after installation
            from lang_select import ResponseManager, extract_items, extract_enhanced_items, select_with_external
            try:
                from lang_select import create_formatter, FlatFormatter, HierarchicalFormatter, MixedFormatter
                formatters_available = True
            except ImportError:
                formatters_available = False
        except Exception as e:
            self.io.tool_error(f"Failed to install lang-select: {str(e)}")
            self.io.tool_error("Please install manually: pip install git+https://github.com/xbarat/lang-select.git")
            return
    
    # Create a response manager with enhanced extraction if requested
    manager = ResponseManager(use_enhanced=use_enhanced)
    manager.store(last_message)
    
    # Get items and check if we have any selectable content
    selectable_items = manager.get_items()
    
    # Progressive fallback strategy
    # Step 1: If using basic extraction with no results, try enhanced extraction
    if not selectable_items and not use_enhanced:
        self.io.tool_warning("Standard extraction found no items, trying enhanced extraction...")
        manager = ResponseManager(use_enhanced=True)
        manager.store(last_message)
        selectable_items = manager.get_items()
    
    # Step 2: If enhanced extraction failed, try with custom preprocessing for special cases
    if not selectable_items:
        self.io.tool_warning("Enhanced extraction found no items, trying additional strategies...")
        
        # Custom extraction for special cases like all-caps sections
        lines = last_message.split('\n')
        custom_text = []
        
        # Process each line looking for all-caps headers to convert to markdown format
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
    
    # Display information about the view mode
    self.io.tool_output(f"Using lang-select with {selection_tool} interface...")
    self.io.tool_output(f"Mode: {'multi-selection' if multi_select else 'single selection'}")
    
    # Show info about the display style if formatters are available
    if formatters_available:
        style_descriptions = {
            "flat": "flat list with section labels",
            "hierarchy": "hierarchical indented structure",
            "mixed": "numbered top-level items with bulleted children"
        }
        style_desc = style_descriptions.get(display_style, display_style)
        self.io.tool_output(f"Display style: {style_desc}" + (" (colorized)" if use_color else ""))
    
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
    
    # Show key instructions based on the selection tool
    if multi_select:
        if selection_tool == "fzf":
            self.io.tool_output("v0.7.0: Press TAB to select multiple items, ENTER to confirm")
        else:
            self.io.tool_output("Use SPACE to select multiple items, ENTER to confirm")
    
    # Modified custom selection function to properly handle ANSI color codes
    def enhanced_select():
        """Custom selection function that supports the formatter parameters"""
        if not formatters_available:
            # Use standard selection if formatters not available
            return manager.select(
                tool=selection_tool,
                multi_select=multi_select,
                feedback=False
            )
        
        # If formatters are available, we'll implement a custom selection that
        # uses select_with_external directly with our view and color preferences
        items = manager.get_items()
        if not items:
            return None
        
        # For fzf, we need special handling for ANSI color codes
        if selection_tool == "fzf" and use_color:
            # We need to call select_with_external directly as ResponseManager.select
            # doesn't yet support view and use_color parameters
            custom_items = items.copy()  # Use a copy to avoid modifying the original items
            
            # Create a temporary file to store content with color codes
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
                # Format the content with the appropriate formatter with colors
                formatter = create_formatter(display_style, use_color=use_color)
                
                # Create a copy of each item that includes its ID in the content
                display_items = []
                for item in items:
                    # Create a shallow copy of the item
                    display_item = type(item)(
                        id=item.id,
                        content=f"{item.id}: {item.content}",
                        original_marker=getattr(item, 'original_marker', None)
                    )
                    
                    # Copy all additional attributes
                    for attr in ['section', 'level', 'parent_id']:
                        if hasattr(item, attr):
                            setattr(display_item, attr, getattr(item, attr))
                            
                    display_items.append(display_item)
                
                # Write formatted content to the file
                formatted_content = formatter.format_items(display_items)
                temp_file.write(formatted_content)
                temp_file.flush()
                temp_filename = temp_file.name
            
            try:
                import subprocess
                import os
                
                # Build fzf command with ANSI support and other options
                cmd = [
                    "fzf", 
                    "--ansi",  # Enable ANSI color code processing
                    "--layout=reverse", 
                    "--height=40%", 
                    "--prompt=Select an item: "
                ]
                
                if multi_select:
                    cmd.append("--multi")
                    cmd.extend(["--header", "Press TAB to select multiple items, ENTER to confirm"])
                
                # Execute fzf with the formatted content
                result = subprocess.run(
                    cmd,
                    input=open(temp_filename, 'r').read(),
                    text=True,
                    capture_output=True
                )
                
                # Process the results
                if result.returncode == 0 and result.stdout.strip():
                    selected_lines = result.stdout.strip().split('\n')
                    
                    # Extract item IDs from the selected lines
                    selected_items = []
                    for line in selected_lines:
                        # Look for the item ID at the beginning of the line
                        for item in items:
                            if f"{item.id}:" in line:
                                selected_items.append(item)
                                break
                    
                    # Update manager's selection state and return results
                    if selected_items:
                        if multi_select:
                            manager.last_selections = [item.content for item in selected_items]
                            manager.last_selection = manager.last_selections[0] if manager.last_selections else None
                            return manager.last_selections
                        else:
                            manager.last_selection = selected_items[0].content
                            manager.last_selections = [manager.last_selection]
                            return manager.last_selection
            
            except Exception as e:
                self.io.tool_error(f"Error using fzf with ANSI colors: {str(e)}")
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_filename)
                except:
                    pass
        
        # Fallback to standard select_with_external
        selected = select_with_external(
            items,
            tool=selection_tool,
            prompt="Select an item",
            multi_select=multi_select,
            view=display_style  # This parameter is supported in select_with_external
        )
        
        # Process the results to match what ResponseManager.select would return
        if selected:
            if multi_select:
                manager.last_selections = [item.content for item in selected]
                manager.last_selection = manager.last_selections[0] if manager.last_selections else None
                return manager.last_selections
            else:
                manager.last_selection = selected.content
                manager.last_selections = [manager.last_selection] if manager.last_selection else []
                return manager.last_selection
        else:
            return None
    
    # Perform the selection using our custom function
    selected = enhanced_select()
    
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
