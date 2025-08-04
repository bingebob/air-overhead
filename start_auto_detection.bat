@echo off
echo 🛩️  Air Overhead Auto-Detection Startup
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Start the auto-detection system
echo Starting auto-detection system...
python start_auto_detection.py

echo.
echo Auto-detection completed
pause 