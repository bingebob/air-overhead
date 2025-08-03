#!/usr/bin/env python3
"""
Air Overhead Flight Tracker - Launcher Script
Simple script to start the flight tracking application
"""

import sys
import os
import webbrowser
import time
from threading import Timer

def open_browser():
    """Open the web interface in the default browser"""
    webbrowser.open('http://localhost:5000')

def main():
    """Main launcher function"""
    print("🛩️  Air Overhead Flight Tracker")
    print("=" * 50)
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Import and run the Flask app
        from app import app
        
        print("✅ Starting Flask server...")
        print("🌐 Web interface will open automatically in 3 seconds...")
        print("📱 Access the app at: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Open browser after 3 seconds
        Timer(3.0, open_browser).start()
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 