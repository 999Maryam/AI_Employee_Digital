#!/bin/bash

# Social Media Automation System - Setup Script
# Run this script to install dependencies and configure the system

echo "🚀 Social Media Automation System - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r social_media/requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

# Install Playwright browsers
echo ""
echo "🌐 Installing Playwright browsers..."
playwright install chromium

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Playwright browsers"
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp social_media/.env.example .env
    echo "✅ .env file created. Please edit it with your credentials."
else
    echo ""
    echo "✅ .env file already exists"
fi

# Create necessary directories
echo ""
echo "📁 Creating directory structure..."
mkdir -p Pending_Approval Approved Done Logs session/linkedin session/facebook

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Odoo credentials"
echo "2. Run session setup for LinkedIn:"
echo "   python social_media/session_manager.py --platform linkedin --setup"
echo "3. Run session setup for Facebook:"
echo "   python social_media/session_manager.py --platform facebook --setup"
echo "4. Start the orchestrator:"
echo "   python social_media/orchestrator.py"
echo "5. Create your first post:"
echo "   python social_media/cli.py post linkedin 'Hello World!'"
echo ""
echo "For help: python social_media/cli.py --help"
