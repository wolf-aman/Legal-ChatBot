#!/usr/bin/env python3
"""
Simple script to run the Streamlit Legal RAG Chatbot
"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app with proper configuration."""
    
    # Check if we're in the right directory
    if not os.path.exists("streamlit_app.py"):
        print("Error: streamlit_app.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("Warning: .env file not found. Make sure you have configured your environment variables.")
        print("Required variables: GROQ_API_KEY, WEAVIATE_URL")
    
    print("Starting Legal RAG Chatbot...")
    print("The app will open in your default web browser.")
    print("Press Ctrl+C to stop the server.")
    print("="*50)
    
    try:
        # Run streamlit with custom configuration
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\nShutting down the server...")
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
