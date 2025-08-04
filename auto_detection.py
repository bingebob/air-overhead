#!/usr/bin/env python3
"""
Automated Flight Detection Script
This script periodically checks for aircraft in your area and triggers Vestaboard notifications
without requiring a browser to be open.

Production-ready version with enhanced error handling and logging.
"""

import requests
import time
import json
import os
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('auto_detection.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration - can be overridden by environment variables
BASE_URL = os.getenv('AIR_OVERHEAD_BASE_URL', "http://localhost:5000")
YOUR_LAT = float(os.getenv('AIR_OVERHEAD_LAT', 51.5995))  # Match frontend default
YOUR_LON = float(os.getenv('AIR_OVERHEAD_LON', -0.5545))
YOUR_RADIUS = float(os.getenv('AIR_OVERHEAD_RADIUS', 5))  # Match geofence radius
CHECK_INTERVAL = int(os.getenv('AIR_OVERHEAD_REFRESH', 1))  # seconds between checks
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# Statistics tracking
stats = {
    'start_time': None,
    'checks_performed': 0,
    'aircraft_detected': 0,
    'errors': 0,
    'last_aircraft_count': 0
}

# Track aircraft that have been notified to avoid duplicates
notified_aircraft = set()

def check_server_health():
    """Check if the Flask server is running and healthy"""
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=10)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except Exception as e:
        logger.error(f"Server health check failed: {str(e)}")
        return False, None

def check_for_aircraft():
    """Check for aircraft in the specified area with retry logic"""
    for attempt in range(MAX_RETRIES):
        try:
            url = f"{BASE_URL}/api/aircraft?lat={YOUR_LAT}&lon={YOUR_LON}&radius={YOUR_RADIUS}"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                aircraft_list = response.json()
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                if aircraft_list:
                    logger.info(f"[{timestamp}] Found {len(aircraft_list)} aircraft")
                    stats['aircraft_detected'] += len(aircraft_list)
                    stats['last_aircraft_count'] = len(aircraft_list)
                    
                    # Trigger Vestaboard notifications for new aircraft
                    trigger_vestaboard_notifications(aircraft_list)
                    
                    return len(aircraft_list)
                else:
                    logger.debug(f"[{timestamp}] No aircraft detected")
                    stats['last_aircraft_count'] = 0
                    return 0
            else:
                logger.error(f"HTTP {response.status_code} error from server")
                stats['errors'] += 1
                return None
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                stats['errors'] += 1
                return None
        except Exception as e:
            logger.error(f"Unexpected error (attempt {attempt + 1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                stats['errors'] += 1
                return None
    
    return None

def get_aircraft_details(icao24):
    """Fetch detailed aircraft information including registration, manufacturer, model, operator"""
    try:
        url = f"{BASE_URL}/api/aircraft/details?icao24={icao24}"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle the actual API response structure
            meta = data.get('meta', {})
            if meta is None:
                meta = {}
            
            # Extract the rich aircraft data
            enriched_data = {
                'icao24': icao24,
                'registration': meta.get('registration', 'N/A'),
                'manufacturer': meta.get('manufacturer', 'N/A'),
                'model': meta.get('model', 'N/A'),
                'operator': meta.get('operator', 'N/A'),
                'serialNumber': meta.get('serialNumber', 'N/A'),
                'age': meta.get('age', 'N/A'),
                'callsign': meta.get('callsign', 'N/A'),
                'flightNumber': meta.get('flightNumber', 'N/A'),
                'altitude': meta.get('altitude', 'N/A'),
                'speed': meta.get('speed', 'N/A'),
                'heading': meta.get('heading', 'N/A')
            }
            
            # Check if we need to try public sources (same logic as web interface)
            needs_public_lookup = (
                enriched_data['manufacturer'] == 'N/A' and 
                enriched_data['model'] == 'N/A' and 
                enriched_data['registration'] == 'N/A'
            )
            
            if needs_public_lookup:
                logger.info(f"   Backend data incomplete, trying public sources...")
                public_data = fetch_public_aircraft_data(icao24)
                if public_data:
                    # Merge public data with backend data
                    enriched_data.update(public_data)
                    logger.info(f"   ✅ Got public data: {public_data.get('manufacturer', 'N/A')} {public_data.get('model', 'N/A')}")
                else:
                    logger.info(f"   ⚠️  No public data available")
            
            logger.info(f"   DETAILS: {enriched_data['registration']} | {enriched_data['manufacturer']} {enriched_data['model']}")
            logger.info(f"   OPERATOR: {enriched_data['operator']} | FLIGHT: {enriched_data['flightNumber']}")
            
            return enriched_data
        else:
            logger.warning(f"Failed to get details for {icao24}: HTTP {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error fetching details for {icao24}: {str(e)}")
        return None

def fetch_public_aircraft_data(icao24):
    """Fetch aircraft metadata from public sources (same as web interface)"""
    try:
        # Use hexdb API (same as web interface)
        url = f"https://hexdb.io/api/v1/aircraft/{icao24}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Parse hexdb response (same logic as web interface)
            aircraft = None
            
            if data.get('aircraft'):
                aircraft = data['aircraft']
            elif data.get('data', {}).get('aircraft'):
                aircraft = data['data']['aircraft']
            elif data.get('icao24') or data.get('ModeS'):
                # Data is at root level
                aircraft = data
            
            if aircraft:
                result = {
                    'manufacturer': aircraft.get('manufacturer') or aircraft.get('Manufacturer'),
                    'model': aircraft.get('type') or aircraft.get('model') or aircraft.get('aircraft_type') or aircraft.get('Type') or aircraft.get('ICAOTypeCode'),
                    'registration': aircraft.get('registration') or aircraft.get('reg') or aircraft.get('Registration'),
                    'operator': aircraft.get('operator') or aircraft.get('owner') or aircraft.get('RegisteredOwners'),
                    'serialNumber': aircraft.get('serial_number') or aircraft.get('serialnumber')
                }
                
                # Filter out None values
                result = {k: v for k, v in result.items() if v is not None}
                
                if result:
                    return result
        
        return None
        
    except Exception as e:
        logger.debug(f"Error fetching public data for {icao24}: {str(e)}")
        return None

def trigger_vestaboard_notifications(aircraft_list):
    """Trigger Vestaboard notifications for detected aircraft with detailed information"""
    global notified_aircraft
    
    try:
        # Send notification for each aircraft
        for aircraft in aircraft_list:
            icao24 = aircraft.get('icao24')
            if icao24:
                # Check if we've already notified about this aircraft
                if icao24 in notified_aircraft:
                    logger.debug(f"REPEAT Aircraft {icao24} already notified, skipping")
                    continue
                
                logger.info(f"NEW AIRCRAFT DETECTED: {icao24}")
                logger.info(f"   Basic Info: {aircraft.get('callsign', 'N/A')} | Alt: {aircraft.get('altitude', 'N/A')} ft | Speed: {aircraft.get('speed', 'N/A')} knots")
                logger.info(f"   Distance: {aircraft.get('distance', 'N/A')} km")
                
                # Get detailed aircraft information
                detailed_aircraft = get_aircraft_details(icao24)
                
                # Merge basic and detailed data for best results
                if detailed_aircraft:
                    # Use detailed data as base, but fall back to basic data for missing fields
                    notification_data = detailed_aircraft.copy()
                    # Ensure we have basic flight data
                    if notification_data.get('callsign') == 'N/A':
                        notification_data['callsign'] = aircraft.get('callsign', 'N/A')
                    if notification_data.get('altitude') == 'N/A':
                        notification_data['altitude'] = aircraft.get('altitude', 'N/A')
                    if notification_data.get('speed') == 'N/A':
                        notification_data['speed'] = aircraft.get('speed', 'N/A')
                    if notification_data.get('heading') == 'N/A':
                        notification_data['heading'] = aircraft.get('heading', 'N/A')
                    notification_data['distance'] = aircraft.get('distance', 'N/A')
                else:
                    # Use basic data if detailed data is not available
                    notification_data = aircraft.copy()
                
                # Call the Vestaboard notification endpoint
                notification_url = f"{BASE_URL}/api/vestaboard/notify"
                notification_payload = {
                    'aircraft': notification_data
                }
                
                response = requests.post(notification_url, json=notification_payload, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success') or result.get('status') == 'success':
                        logger.info(f"OK Vestaboard notification sent for {icao24}")
                        notified_aircraft.add(icao24)  # Mark as notified
                    else:
                        logger.warning(f"WARNING Vestaboard notification failed for {icao24}: {result.get('error', 'Unknown error')}")
                elif response.status_code == 500:
                    # Check if this is because aircraft is already tracked (which is normal)
                    try:
                        result = response.json()
                        if "Failed to send notification" in result.get('error', ''):
                            logger.info(f"INFO Aircraft {icao24} already tracked by server (normal)")
                            notified_aircraft.add(icao24)  # Mark as notified to avoid retries
                        else:
                            logger.error(f"ERROR Server error for {icao24}: {result.get('error', 'Unknown error')}")
                    except:
                        logger.error(f"ERROR Server error for {icao24}: HTTP 500")
                else:
                    logger.error(f"ERROR Failed to send Vestaboard notification for {icao24}: HTTP {response.status_code}")
                    
    except Exception as e:
        logger.error(f"Error triggering Vestaboard notifications: {str(e)}")

def check_vestaboard_status():
    """Check Vestaboard connection status with detailed logging"""
    try:
        response = requests.get(f"{BASE_URL}/api/vestaboard/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            enabled = data.get('vestaboard_enabled', False)
            connected = data.get('vestaboard_connected', False)
            tracked_count = data.get('tracked_aircraft_count', 0)
            
            logger.info(f"Vestaboard Status - Enabled: {enabled}, Connected: {connected}, Tracked: {tracked_count}")
            return enabled, connected, tracked_count
        else:
            logger.error(f"Failed to get Vestaboard status: HTTP {response.status_code}")
            return False, False, 0
    except Exception as e:
        logger.error(f"Error checking Vestaboard status: {str(e)}")
        return False, False, 0

def clear_notified_aircraft():
    """Clear the notified aircraft list periodically to allow re-notifications"""
    global notified_aircraft
    if len(notified_aircraft) > 100:  # Clear when we have too many tracked
        logger.info(f"CLEAR Clearing notified aircraft list (had {len(notified_aircraft)} entries)")
        notified_aircraft.clear()

def print_statistics():
    """Print current statistics"""
    if stats['start_time']:
        runtime = datetime.now() - stats['start_time']
        runtime_str = str(runtime).split('.')[0]  # Remove microseconds
        
        logger.info("=" * 60)
        logger.info("STATISTICS AUTO-DETECTION STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Runtime: {runtime_str}")
        logger.info(f"Checks performed: {stats['checks_performed']}")
        logger.info(f"Total aircraft detected: {stats['aircraft_detected']}")
        logger.info(f"Errors encountered: {stats['errors']}")
        logger.info(f"Current aircraft count: {stats['last_aircraft_count']}")
        logger.info(f"Aircraft notified: {len(notified_aircraft)}")
        
        if stats['checks_performed'] > 0:
            avg_interval = runtime.total_seconds() / stats['checks_performed']
            logger.info(f"Average check interval: {avg_interval:.1f} seconds")
        
        logger.info("=" * 60)

def main():
    """Main loop for automated detection with enhanced error handling"""
    logger.info("AIRPLANE Automated Flight Detection - Production Ready")
    logger.info("=" * 60)
    logger.info(f"Location: ({YOUR_LAT}, {YOUR_LON})")
    logger.info(f"Radius: {YOUR_RADIUS} km")
    logger.info(f"Check interval: {CHECK_INTERVAL} seconds")
    logger.info(f"Max retries: {MAX_RETRIES}")
    logger.info(f"Retry delay: {RETRY_DELAY} seconds")
    logger.info("=" * 60)
    
    # Initialize statistics
    stats['start_time'] = datetime.now()
    
    # Initial server health check
    server_healthy, health_data = check_server_health()
    if not server_healthy:
        logger.error("ERROR Flask server is not running or not responding")
        logger.error("Please start the Flask server first: python app.py")
        return
    
    logger.info("OK Flask server is running and healthy")
    
    # Check Vestaboard status
    vesta_enabled, vesta_connected, tracked_count = check_vestaboard_status()
    if vesta_enabled and vesta_connected:
        logger.info("OK Vestaboard connected - notifications will be sent")
        logger.info(f"   Currently tracking {tracked_count} aircraft")
    elif vesta_enabled:
        logger.warning("WARNING Vestaboard enabled but not connected")
        logger.info("   Check your Vestaboard configuration and network connection")
    else:
        logger.info("INFO Vestaboard not configured - flight notifications disabled")
        logger.info("   Create vestaboard_config.json to enable notifications")
    
    logger.info("")
    logger.info("STARTING Starting automated detection...")
    logger.info("Press Ctrl+C to stop gracefully")
    logger.info("")
    
    try:
        while True:
            stats['checks_performed'] += 1
            
            # Check for aircraft
            aircraft_count = check_for_aircraft()
            
            # Clear notified aircraft periodically
            clear_notified_aircraft()

            # Log statistics every 100 checks
            if stats['checks_performed'] % 100 == 0:
                print_statistics()
            
            # Wait for next check
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        logger.info("")
        logger.info("STOP Detection stopped by user")
        print_statistics()
        logger.info("Thanks for using Automated Flight Detection!")
        logger.info("Log file saved to: auto_detection.log")
    except Exception as e:
        logger.error(f"Unexpected error in main loop: {str(e)}")
        print_statistics()
        raise

if __name__ == "__main__":
    main() 