#!/bin/bash

echo "===================================="
echo "Braai Bites & Beverages - Setup"
echo "===================================="
echo ""

echo "[1/5] Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi
python3 --version
echo ""

echo "[2/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "Virtual environment created successfully"
else
    echo "Virtual environment already exists"
fi
echo ""

echo "[3/5] Activating virtual environment..."
source venv/bin/activate
echo ""

echo "[4/5] Installing dependencies..."
pip install -r requirements.txt
echo ""

echo "[5/5] Setting up environment file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ".env file created from template"
    echo ""
    echo "IMPORTANT: Please edit .env and add your AliExpress API credentials"
    echo ""
else
    echo ".env file already exists"
fi

echo ""
echo "===================================="
echo "Setup Complete!"
echo "===================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API credentials"
echo "2. Run: python app.py"
echo "3. Visit: http://localhost:5000"
echo ""
echo "For syncing products:"
echo "  python -m app.utils.aliexpress_sync sync"
echo ""
