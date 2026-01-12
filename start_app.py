#!/usr/bin/env python3
"""
Startup script for the MiniDB Todo App
"""

import subprocess
import sys
import webbrowser
import time
import threading

def start_server():
    """Start the FastAPI server"""
    try:
        print("Starting MiniDB Todo App...")
        print("Server will be available at: http://127.0.0.1:8000/")
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Start the server
        subprocess.run([sys.executable, "app.py"], cwd=".")
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")

def open_browser_delayed():
    """Open browser after a delay"""
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000/")

if __name__ == "__main__":
    print("MiniDB Todo Application")
    print("=" * 30)
    print()
    
    # Start browser opening in background
    browser_thread = threading.Thread(target=open_browser_delayed)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Start the server
    start_server()