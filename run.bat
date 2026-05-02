@echo off
REM Run script for development

if not exist venv (
    echo Virtual environment not found. Please run setup.bat first.
    exit /b 1
)

call venv\Scripts\activate.bat

echo Starting Timeless Backend...
echo.
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo.

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
