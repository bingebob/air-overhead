#!/usr/bin/env python3
"""
Auto-Detection Startup Script
This script starts both the Flask server and the auto-detection script together.
"""

import subprocess
import time
import sys
import os
from datetime import datetime

def check_dependencies():
    """Check if required files exist"""
    required_files = [
        'app.py',
        'auto_detection.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_flask_server():
    """Start the Flask server in the background"""
    print("🚀 Starting Flask server...")
    try:
        # Start Flask server in background
        flask_process = subprocess.Popen([sys.executable, 'app.py'], 
                                       stdout=subprocess.PIPE, 
                                       stderr=subprocess.PIPE,
                                       text=True)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        if flask_process.poll() is None:
            print("✅ Flask server started successfully")
            return flask_process
        else:
            stdout, stderr = flask_process.communicate()
            print(f"❌ Flask server failed to start:")
            print(f"   STDOUT: {stdout}")
            print(f"   STDERR: {stderr}")
            return None
    except Exception as e:
        print(f"❌ Error starting Flask server: {e}")
        return None

def start_auto_detection():
    """Start the auto-detection script"""
    print("🛩️  Starting auto-detection script...")
    try:
        # Start auto-detection script
        auto_process = subprocess.run([sys.executable, 'auto_detection.py'], 
                                    check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Auto-detection script failed: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Auto-detection stopped by user")
        return True

def main():
    """Main startup function"""
    print("🛩️  Air Overhead Auto-Detection Startup")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please ensure all required files are present")
        return 1
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return 1
    
    # Start Flask server
    flask_process = start_flask_server()
    if not flask_process:
        print("\n❌ Failed to start Flask server")
        return 1
    
    try:
        # Start auto-detection
        success = start_auto_detection()
        
        if success:
            print("\n✅ Auto-detection completed successfully")
            return 0
        else:
            print("\n❌ Auto-detection failed")
            return 1
            
    finally:
        # Clean up Flask server
        if flask_process and flask_process.poll() is None:
            print("\n🛑 Stopping Flask server...")
            flask_process.terminate()
            try:
                flask_process.wait(timeout=5)
                print("✅ Flask server stopped")
            except subprocess.TimeoutExpired:
                print("⚠️  Force killing Flask server...")
                flask_process.kill()

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Startup interrupted by user")
        sys.exit(1) 