#!/usr/bin/env python3
"""
Simple run script for Streamlit deployment
"""

import os
import sys

if __name__ == '__main__':
    # Set environment variables
    os.environ['STREAMLIT_SERVER_PORT'] = '8080'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
    
    # Run the simple demo
    os.system('streamlit run simple_demo.py --server.port 8080 --server.address 0.0.0.0 --server.headless true')

