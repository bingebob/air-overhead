#!/usr/bin/env python3
"""
Automated Flight Detection Script
This script periodically checks for aircraft in your area and triggers Vestaboard notifications
without requiring a browser to be open.
"""

import requests
import time
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
CHECK_INTERVAL = 30  # seconds between checks

# Update these to match your location
YOUR_LAT = 51.5995  # Match frontend default
YOUR_LON = -0.5545
YOUR_RADIUS = 2  # Match geofence radius

def check_for_aircraft():
    """Check for aircraft in the specified area"""
    try:
        url = f"{BASE_URL}/api/aircraft?lat={YOUR_LAT}&lon={YOUR_LON}&radius={YOUR_RADIUS}"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            aircraft_list = response.json()
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            if aircraft_list:
                print(f"[{timestamp}] Found {len(aircraft_list)} aircraft")
                # The server will automatically send Vestaboard notifications for new aircraft
                return len(aircraft_list)
            else:
                print(f"[{timestamp}] No aircraft detected")
                return 0
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Error: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] Error checking for aircraft: {str(e)}")
        return None

def check_vestaboard_status():
    """Check Vestaboard connection status"""
    try:
        response = requests.get(f"{BASE_URL}/api/vestaboard/status")
        if response.status_code == 200:
            data = response.json()
            return data.get('vestaboard_enabled', False), data.get('vestaboard_connected', False)
        return False, False
    except:
        return False, False

def main():
    """Main loop for automated detection"""
    print("🛩️  Automated Flight Detection")
    print("=" * 50)
    print(f"Location: ({YOUR_LAT}, {YOUR_LON})")
    print(f"Radius: {YOUR_RADIUS} km")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("=" * 50)
    
    # Check Vestaboard status
    vesta_enabled, vesta_connected = check_vestaboard_status()
    if vesta_enabled and vesta_connected:
        print("✅ Vestaboard connected - notifications will be sent")
    elif vesta_enabled:
        print("⚠️  Vestaboard enabled but not connected")
    else:
        print("ℹ️  Vestaboard not configured")
    
    print(f"\n🔄 Starting automated detection...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            aircraft_count = check_for_aircraft()
            
            # Wait for next check
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\n\n🛑 Detection stopped by user")
        print("Thanks for using Automated Flight Detection!")

if __name__ == "__main__":
    main() 