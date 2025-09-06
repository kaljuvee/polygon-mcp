#!/usr/bin/env python3
"""
Main entry point for deployment - runs the simple demo
"""

import streamlit as st
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the simple demo
if __name__ == '__main__':
    # Import the simple demo module
    import simple_demo
    
    # Run the main function
    simple_demo.main()

