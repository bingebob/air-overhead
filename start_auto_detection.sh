#!/bin/bash

echo "🛩️  Air Overhead Auto-Detection Startup"
echo "================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.7+ and try again"
    exit 1
fi

echo "✅ Python 3 found"
echo

# Make the script executable
chmod +x start_auto_detection.py

# Start the auto-detection system
echo "Starting auto-detection system..."
python3 start_auto_detection.py

echo
echo "Auto-detection completed" 