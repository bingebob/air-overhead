@echo off
echo 🛩️  Air Overhead Flight Tracker - Installation
echo ================================================

echo.
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

echo.
echo 📝 Setting up configuration files...
if not exist "credentials.json" (
    echo Copying credentials template...
    copy "credentials.json.example" "credentials.json"
    echo ⚠️  Please edit credentials.json with your OpenSky credentials
)

if not exist "vestaboard_config.json" (
    echo Copying Vestaboard config template...
    copy "vestaboard_config.json.example" "vestaboard_config.json"
    echo ⚠️  Please edit vestaboard_config.json with your Vestaboard settings
)

echo.
echo ✅ Installation complete!
echo.
echo 🚀 To start the application, run:
echo    python run.py
echo.
echo 📖 For more information, see README.md
pause 