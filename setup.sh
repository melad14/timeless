#!/bin/bash
# Setup script for Timeless Backend on macOS/Linux

echo "================================="
echo " Timeless Backend Setup"
echo "================================="

# Check if Python is installed
if ! python3 --version > /dev/null 2>&1; then
    echo "Please install Python 3.10 or higher first"
    exit 1
fi

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment"
    exit 1
fi

# Install requirements
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install requirements"
    exit 1
fi

# Copy .env file
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Remember to update .env with your configuration!"
fi

echo ""
echo "================================="
echo " Setup Complete!"
echo "================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run: source venv/bin/activate"
echo "3. Run: uvicorn app.main:app --reload"
echo ""
