#!/usr/bin/env python3
"""
Dog Voting Platform - Quick Start Script
Run this file to start the application with proper setup.
"""

import os
import sys
import subprocess

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_requirements():
    """Install required packages."""
    print("📦 Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements. Please run: pip install -r requirements.txt")
        sys.exit(1)

def create_directories():
    """Create necessary directories."""
    directories = ['static/uploads', 'static/css', 'static/js', 'templates']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    print("✅ Directories created!")

def main():
    """Main setup and run function."""
    print("🐕 Dog Voting Platform - Quick Start")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Check if requirements need to be installed
    try:
        import flask
        print("✅ Flask is already installed")
    except ImportError:
        install_requirements()
    
    print("\n🚀 Starting the Dog Voting Platform...")
    print("📍 Server will be available at: http://localhost:5000")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 40)
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Thanks for using Dog Voting Platform!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 