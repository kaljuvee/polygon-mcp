#!/usr/bin/env python3
"""
Flask wrapper for the Streamlit app to enable deployment
"""

import os
import subprocess
import threading
import time
from flask import Flask, redirect

app = Flask(__name__)

def run_streamlit():
    """Run Streamlit in a separate thread"""
    try:
        # Change to the app directory
        os.chdir('/app')
        
        # Run Streamlit
        subprocess.run([
            'streamlit', 'run', 'simple_demo.py',
            '--server.port', '8501',
            '--server.address', '0.0.0.0',
            '--server.headless', 'true',
            '--server.enableCORS', 'false'
        ])
    except Exception as e:
        print(f"Error running Streamlit: {e}")

@app.route('/')
def index():
    """Redirect to Streamlit app"""
    return redirect('http://localhost:8501')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {'status': 'healthy', 'service': 'polygon-mcp-demo'}

if __name__ == '__main__':
    # Start Streamlit in background thread
    streamlit_thread = threading.Thread(target=run_streamlit, daemon=True)
    streamlit_thread.start()
    
    # Give Streamlit time to start
    time.sleep(5)
    
    # Start Flask app
    app.run(host='0.0.0.0', port=5000, debug=False)

