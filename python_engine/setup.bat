@echo off
REM Setup script for Career Recommendation Engine
REM Run this script to set up the Python environment

echo ============================================
echo Career Recommendation Engine - Setup
echo ============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python found:
python --version
echo.

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not installed
    echo Please ensure pip is installed with Python
    pause
    exit /b 1
)

echo [2/4] pip found:
pip --version
echo.

REM Install dependencies
echo [3/4] Installing dependencies...
echo This may take a few minutes...
echo.
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [4/4] Verifying installation...
python -c "import flask; import sentence_transformers; import faiss; import numpy; import pandas; print('✓ All packages installed successfully!')"

if errorlevel 1 (
    echo.
    echo ERROR: Some packages failed to import
    pause
    exit /b 1
)

echo.
echo ============================================
echo Setup completed successfully!
echo ============================================
echo.
echo Next steps:
echo   1. Ensure careers.csv is in ../data/ directory
echo   2. Run 'python test_engine.py' to test the engine
echo   3. Run 'python app.py' to start the API server
echo.
pause
