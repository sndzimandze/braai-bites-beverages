@echo off
echo ====================================
echo Braai Bites & Beverages - Setup
echo ====================================
echo.

echo [1/5] Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)
echo.

echo [2/5] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created successfully
) else (
    echo Virtual environment already exists
)
echo.

echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo [4/5] Installing dependencies...
pip install -r requirements.txt
echo.

echo [5/5] Setting up environment file...
if not exist ".env" (
    copy .env.example .env
    echo .env file created from template
    echo.
    echo IMPORTANT: Please edit .env and add your AliExpress API credentials
    echo.
) else (
    echo .env file already exists
)

echo.
echo ====================================
echo Setup Complete!
echo ====================================
echo.
echo Next steps:
echo 1. Edit .env file and add your API credentials
echo 2. Run: python app.py
echo 3. Visit: http://localhost:5000
echo.
echo For syncing products:
echo   python -m app.utils.aliexpress_sync sync
echo.
pause
