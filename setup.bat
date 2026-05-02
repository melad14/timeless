@echo off
REM Setup script for Timeless Backend on Windows

echo =================================
echo  Timeless Backend Setup
echo =================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Please install Python 3.10 or higher first
    exit /b 1
)

REM Create virtual environment
echo.
echo Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    exit /b 1
)

REM Install requirements
echo.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install requirements
    exit /b 1
)

REM Copy .env file
if not exist .env (
    echo.
    echo Creating .env file from template...
    copy .env.example .env
    echo Remember to update .env with your configuration!
)

echo.
echo =================================
echo  Setup Complete!
echo =================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Run: venv\Scripts\activate.bat
echo 3. Run: uvicorn app.main:app --reload
echo.
pause
