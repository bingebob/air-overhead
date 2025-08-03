#!/usr/bin/env python3
"""
Test script for Vestaboard integration with Flight Tracker
This script tests the Vestaboard notification functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"

def test_health_endpoint():
    """Test the health endpoint to check Vestaboard status"""
    print("🔍 Testing health endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed")
            print(f"   Vestaboard enabled: {data.get('vestaboard_enabled', False)}")
            print(f"   Vestaboard connected: {data.get('vestaboard_connected', False)}")
            print(f"   Tracked aircraft: {data.get('tracked_aircraft_count', 0)}")
            return data
        else:
            print(f"❌ Health check failed: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return None

def test_vestaboard_status():
    """Test the Vestaboard status endpoint"""
    print("\n🔍 Testing Vestaboard status endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/vestaboard/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Vestaboard status retrieved")
            print(f"   Enabled: {data.get('vestaboard_enabled', False)}")
            print(f"   Connected: {data.get('vestaboard_connected', False)}")
            print(f"   Tracked aircraft count: {data.get('tracked_aircraft_count', 0)}")
            if data.get('tracked_aircraft'):
                print(f"   Sample tracked aircraft: {data.get('tracked_aircraft', [])[:3]}")
            return data
        else:
            print(f"❌ Vestaboard status failed: HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Vestaboard status error: {str(e)}")
        return None

def test_vestaboard_connection():
    """Test Vestaboard connection and send test message"""
    print("\n🔍 Testing Vestaboard connection...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/vestaboard/test")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Vestaboard test successful")
            print(f"   Message: {data.get('message', 'Unknown')}")
            return True
        else:
            data = response.json()
            print(f"❌ Vestaboard test failed: {data.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ Vestaboard test error: {str(e)}")
        return False

def test_flight_detection():
    """Test flight detection with a sample location"""
    print("\n🔍 Testing flight detection...")
    
    # Test coordinates (New York area)
    test_lat = 40.7128
    test_lon = -74.0060
    test_radius = 10
    
    try:
        url = f"{BASE_URL}/api/aircraft?lat={test_lat}&lon={test_lon}&radius={test_radius}"
        response = requests.get(url)
        
        if response.status_code == 200:
            aircraft_list = response.json()
            print(f"✅ Flight detection successful")
            print(f"   Found {len(aircraft_list)} aircraft")
            
            if aircraft_list:
                print("   Sample aircraft:")
                for i, aircraft in enumerate(aircraft_list[:3]):
                    callsign = aircraft.get('callsign', 'UNKNOWN')
                    icao24 = aircraft.get('icao24', 'UNKNOWN')
                    altitude = aircraft.get('altitude', 0)
                    print(f"     {i+1}. {callsign} ({icao24}) at {altitude}ft")
            
            return aircraft_list
        else:
            data = response.json()
            print(f"❌ Flight detection failed: {data.get('error', 'Unknown error')}")
            return None
    except Exception as e:
        print(f"❌ Flight detection error: {str(e)}")
        return None

def main():
    """Run all tests"""
    print("🛩️  Vestaboard Integration Test")
    print("=" * 50)
    print(f"Testing against: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Test 1: Health endpoint
    health_data = test_health_endpoint()
    
    # Test 2: Vestaboard status
    status_data = test_vestaboard_status()
    
    # Test 3: Vestaboard connection test
    connection_ok = test_vestaboard_connection()
    
    # Test 4: Flight detection (this should trigger Vestaboard notifications)
    aircraft_list = test_flight_detection()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if health_data:
        print(f"✅ Health endpoint: Working")
        print(f"   Vestaboard enabled: {health_data.get('vestaboard_enabled', False)}")
        print(f"   Vestaboard connected: {health_data.get('vestaboard_connected', False)}")
    else:
        print(f"❌ Health endpoint: Failed")
    
    if status_data:
        print(f"✅ Vestaboard status: Working")
        print(f"   Tracked aircraft: {status_data.get('tracked_aircraft_count', 0)}")
    else:
        print(f"❌ Vestaboard status: Failed")
    
    if connection_ok:
        print(f"✅ Vestaboard connection: Working")
    else:
        print(f"❌ Vestaboard connection: Failed")
    
    if aircraft_list is not None:
        print(f"✅ Flight detection: Working ({len(aircraft_list)} aircraft found)")
        if aircraft_list and health_data and health_data.get('vestaboard_enabled') and health_data.get('vestaboard_connected'):
            print(f"   Vestaboard notifications should be sent for new aircraft")
    else:
        print(f"❌ Flight detection: Failed")
    
    print("\n💡 Next steps:")
    print("   1. Check your Vestaboard for test messages")
    print("   2. If aircraft were found, check for flight notifications")
    print("   3. Monitor the server logs for notification attempts")
    print("   4. Use the web interface to search for flights in your area")

if __name__ == "__main__":
    main() 