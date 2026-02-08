#!/bin/bash
# Setup script for Career Recommendation Engine (Linux/Mac)
# Run this script to set up the Python environment

echo "============================================"
echo "Career Recommendation Engine - Setup"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "[1/4] Python found:"
python3 --version
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3"
    exit 1
fi

echo "[2/4] pip found:"
pip3 --version
echo ""

# Install dependencies
echo "[3/4] Installing dependencies..."
echo "This may take a few minutes..."
echo ""
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[4/4] Verifying installation..."
python3 -c "import flask; import sentence_transformers; import faiss; import numpy; import pandas; print('✓ All packages installed successfully!')"

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Some packages failed to import"
    exit 1
fi

echo ""
echo "============================================"
echo "Setup completed successfully!"
echo "============================================"
echo ""
echo "Next steps:"
echo "  1. Ensure careers.csv is in ../data/ directory"
echo "  2. Run 'python3 test_engine.py' to test the engine"
echo "  3. Run 'python3 app.py' to start the API server"
echo ""
