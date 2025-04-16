#!/usr/bin/env python3
"""
Test script for the enhanced cmd_select implementation.

This script simulates the behavior of the cmd_select plugin with different display styles.
"""

import os
import sys
import argparse

# Add the parent directory to the path so we can import from lang_select
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock implementation of the coder and io classes for testing
class MockIO:
    def tool_output(self, message):
        print(f"[OUTPUT] {message}")
        
    def tool_error(self, message):
        print(f"[ERROR] {message}")
        
    def tool_warning(self, message):
        print(f"[WARNING] {message}")

class MockCoder:
    def __init__(self, assistant_message):
        self.assistant_message = assistant_message
        self.done_messages = [{"role": "assistant", "content": assistant_message}]
        self.cur_messages = []
        
    def send_message(self, message):
        print(f"[FEEDBACK] {message}")
        return []

# Import the cmd_select implementation
from cmd_select_02 import cmd_select

# Sample assistant message with hierarchical content
SAMPLE_MESSAGE = """
Here's a plan for implementing a task management system:

# Architecture

## Backend Components
1. RESTful API
   - User authentication endpoints
   - Task CRUD operations
   - Notification system
2. Database schema
   - User table
   - Tasks table
   - Categories table
   - Tags table
3. Background job processor
   - Email notifications
   - Data aggregation
   - Scheduled tasks

## Frontend Components
* User interface
  * Dashboard view
  * Task list view
  * Calendar view
* State management
* API integration layer

# Implementation Plan

## Phase 1: MVP
- User authentication
- Basic task creation and management
- Simple list view

## Phase 2: Enhanced Features
- Categories and tags
- Search and filtering
- Calendar integration

## Phase 3: Advanced Features
- Recurring tasks
- Team collaboration
- Analytics dashboard

Would you like me to elaborate on any specific component?
"""

def main():
    """Test the cmd_select functionality with different display styles"""
    parser = argparse.ArgumentParser(description="Test the enhanced cmd_select implementation")
    parser.add_argument("--style", choices=["flat", "hierarchy", "mixed"], default="hierarchy",
                       help="Display style to use")
    parser.add_argument("--basic", action="store_true", help="Use basic extraction (no hierarchy)")
    parser.add_argument("--single", action="store_true", help="Use single selection mode")
    parser.add_argument("--no-color", action="store_true", help="Disable colorized output")
    args = parser.parse_args()
    
    # Build the command string
    cmd = ""
    if args.single:
        cmd += "--single "
    if args.basic:
        cmd += "--basic "
    if args.style == "flat":
        cmd += "--flat "
    elif args.style == "mixed":
        cmd += "--mixed "
    if args.no_color:
        cmd += "--no-color"
        
    # Create mock objects
    mock_coder = MockCoder(SAMPLE_MESSAGE)
    mock_io = MockIO()
    
    # Create a mock instance with the required attributes
    class MockInstance:
        def __init__(self):
            self.coder = mock_coder
            self.io = mock_io
    
    instance = MockInstance()
    
    # Call the cmd_select function
    print(f"\nTesting cmd_select with args: '{cmd}'")
    print("-" * 60)
    cmd_select(instance, cmd)

if __name__ == "__main__":
    main() 