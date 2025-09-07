#!/usr/bin/env python3
"""
Setup script for Cover Letter Generator
"""

import os
import shutil

def setup_environment():
    """Set up the environment file"""
    if not os.path.exists('.env'):
        shutil.copy('env_example.txt', '.env')
        print("✅ Created .env file from template")
        print("📝 Please edit .env and add your Google API key")
    else:
        print("✅ .env file already exists")

def create_directories():
    """Create necessary directories"""
    directories = [
        'static_content/examples',
        'static_content/templates'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def main():
    print("🚀 Setting up Cover Letter Generator...")
    create_directories()
    setup_environment()
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file and add your Google API key")
    print("2. Add your own content files to static_content/ folder")
    print("3. Run: streamlit run app.py")

if __name__ == "__main__":
    main()
