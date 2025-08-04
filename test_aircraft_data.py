#!/usr/bin/env python3
"""
Test script to check aircraft manufacturer and model data using enhanced auto-detection methods
"""

import requests
import json
import sys
import os

# Add the current directory to the path so we can import from auto_detection
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the enhanced functions from auto_detection
from auto_detection import get_aircraft_details

def test_aircraft_data():
    """Test getting aircraft data with manufacturer and model information using enhanced methods"""
    
    # Test basic aircraft detection
    print("Testing aircraft detection with enhanced methods...")
    url = "http://localhost:5000/api/aircraft?lat=51.5995&lon=-0.5545&radius=50"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            aircraft_list = response.json()
            print(f"Found {len(aircraft_list)} aircraft")
            
            if aircraft_list:
                # Test detailed data for multiple aircraft using enhanced method
                print(f"Testing enhanced detailed data for up to 5 aircraft...")
                
                for i, aircraft in enumerate(aircraft_list[:5]):
                    icao24 = aircraft.get('icao24')
                    callsign = aircraft.get('callsign', 'N/A')
                    print(f"\n--- Aircraft {i+1}: {icao24} ({callsign}) ---")
                    
                    # Use the enhanced get_aircraft_details function
                    detailed_aircraft = get_aircraft_details(icao24)
                    
                    if detailed_aircraft:
                        manufacturer = detailed_aircraft.get('manufacturer', 'N/A')
                        model = detailed_aircraft.get('model', 'N/A')
                        registration = detailed_aircraft.get('registration', 'N/A')
                        operator = detailed_aircraft.get('operator', 'N/A')
                        
                        print(f"  Registration: {registration}")
                        print(f"  Manufacturer: {manufacturer}")
                        print(f"  Model: {model}")
                        print(f"  Operator: {operator}")
                        
                        if manufacturer != 'N/A' or model != 'N/A':
                            print(f"  ✅ FOUND DATA: {manufacturer} {model}")
                            break
                        else:
                            print(f"  ⚠️  No manufacturer/model data")
                    else:
                        print(f"  ❌ Failed to get details")
                
                print(f"\n=== SUMMARY ===")
                print(f"Tested {min(5, len(aircraft_list))} aircraft")
                print(f"Total aircraft in area: {len(aircraft_list)}")
            else:
                print("No aircraft detected in the area")
        else:
            print(f"❌ Failed to get aircraft list: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_aircraft_data() 