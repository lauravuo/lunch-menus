#!/usr/bin/env python3
"""
Setup script for the Lunch Menu Scraper project.
"""

import os
import sys
import subprocess


def run_command(command, description):
    """Run a shell command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install Python dependencies."""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")


def create_env_file():
    """Create .env file from template if it doesn't exist."""
    if os.path.exists('.env'):
        print("✅ .env file already exists")
        return True
    
    if os.path.exists('config.example.env'):
        print("📝 Creating .env file from template...")
        try:
            with open('config.example.env', 'r') as template:
                content = template.read()
            
            with open('.env', 'w') as env_file:
                env_file.write(content)
            
            print("✅ .env file created from template")
            print("⚠️  Please edit .env file with your actual Telegram bot credentials")
            return True
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
            return False
    else:
        print("⚠️  config.example.env not found, skipping .env creation")
        return True


def main():
    """Main setup function."""
    print("🚀 Setting up Lunch Menu Scraper")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed during dependency installation")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    print("\n" + "=" * 40)
    print("🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Create a Telegram bot via @BotFather")
    print("2. Add the bot to your target channel")
    print("3. Edit .env file with your bot token and channel ID")
    print("4. Test the scrapers: python test_scrapers.py")
    print("5. Push to GitHub and set up GitHub Secrets")
    print("\nFor more information, see README.md")


if __name__ == "__main__":
    main()
