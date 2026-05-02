#!/bin/bash
# Run script for development

if [ ! -d venv ]; then
    echo "Virtual environment not found. Please run setup.sh first."
    exit 1
fi

source venv/bin/activate

echo "Starting Timeless Backend..."
echo ""
echo "API Documentation: http://localhost:8000/docs"
echo "Health Check: http://localhost:8000/health"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
