#!/bin/bash

echo "🛩️  Air Overhead Flight Tracker - Installation"
echo "================================================"

echo
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo
echo "📝 Setting up configuration files..."
if [ ! -f "credentials.json" ]; then
    echo "Copying credentials template..."
    cp "credentials.json.example" "credentials.json"
    echo "⚠️  Please edit credentials.json with your OpenSky credentials"
fi

if [ ! -f "vestaboard_config.json" ]; then
    echo "Copying Vestaboard config template..."
    cp "vestaboard_config.json.example" "vestaboard_config.json"
    echo "⚠️  Please edit vestaboard_config.json with your Vestaboard settings"
fi

echo
echo "✅ Installation complete!"
echo
echo "🚀 To start the application, run:"
echo "   python3 run.py"
echo
echo "📖 For more information, see README.md" 