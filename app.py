#!/usr/bin/env python3
"""
Flight Tracker Backend - Flask Proxy Server
This server provides a hybrid approach using OpenSky for initial aircraft detection
and AeroDataBox for enriched aircraft metadata and flight details.
"""

import json
import os
import math
import requests
import time
import csv
import gzip
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
CREDENTIALS_FILE = 'credentials.json'
AERODATABOX_CREDENTIALS_FILE = 'aerodatabox_credentials.json'
VESTABOARD_CONFIG_FILE = 'vestaboard_config.json'
OPENSKY_BASE_URL = 'https://opensky-network.org/api'
AERODATABOX_BASE_URL = 'https://aerodatabox.p.rapidapi.com'

# Cache for API responses to avoid rate limiting
cache = {}
CACHE_DURATION = 300  # 5 minutes in seconds

# Aircraft metadata cache
aircraft_metadata_cache = {}
METADATA_CACHE_FILE = 'aircraft_metadata_cache.json'

# Vestaboard tracking for aircraft entering geofence
tracked_aircraft = set()  # Set of ICAO24 codes that have been notified
VESTABOARD_ENABLED = False

# Public aircraft databases
PUBLIC_APIS = [
    {
        'name': 'hexdb',
        'url': 'https://hexdb.io/api/v1/aircraft/{icao24}',
        'timeout': 5
    },
    {
        'name': 'adsbexchange',
        'url': 'https://public-api.adsbexchange.com/VirtualRadar/AircraftList.json?icao={icao24}',
        'timeout': 5
    }
]

OPENSKY_CSV_FILE = 'aircraftDatabase.csv'
opensky_csv_db = None

def load_opensky_credentials():
    """Load OpenSky API credentials from credentials file."""
    try:
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(f"Credentials file '{CREDENTIALS_FILE}' not found")
        
        with open(CREDENTIALS_FILE, 'r') as f:
            credentials = json.load(f)
        
        # Check for OAuth2 client credentials format (preferred)
        if 'clientId' in credentials and 'clientSecret' in credentials:
            return credentials['clientId'], credentials['clientSecret']
        # Check for legacy username/password format
        elif 'username' in credentials and 'password' in credentials:
            return credentials['username'], credentials['password']
        else:
            raise ValueError("Credentials file must contain either 'clientId'/'clientSecret' (OAuth2) or 'username'/'password' (legacy) fields")
    
    except Exception as e:
        print(f"Error loading OpenSky credentials: {e}")
        return None, None

def load_aerodatabox_credentials():
    """Load AeroDataBox API credentials from credentials file."""
    try:
        if not os.path.exists(AERODATABOX_CREDENTIALS_FILE):
            # If dedicated file doesn't exist, try to get from main credentials file
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(f"Credentials files not found")
            
            with open(CREDENTIALS_FILE, 'r') as f:
                credentials = json.load(f)
            
            if 'x-rapidapi-key' in credentials and 'x-rapidapi-host' in credentials:
                return credentials['x-rapidapi-key'], credentials['x-rapidapi-host']
            else:
                raise ValueError("Could not find AeroDataBox credentials")
        else:
            with open(AERODATABOX_CREDENTIALS_FILE, 'r') as f:
                credentials = json.load(f)
            
            if 'x-rapidapi-key' in credentials and 'x-rapidapi-host' in credentials:
                return credentials['x-rapidapi-key'], credentials['x-rapidapi-host']
            else:
                raise ValueError("AeroDataBox credentials file must contain 'x-rapidapi-key' and 'x-rapidapi-host' fields")
    
    except Exception as e:
        print(f"Error loading AeroDataBox credentials: {e}")
        return None, None

def load_aircraft_metadata_cache():
    """Load cached aircraft metadata from file."""
    try:
        if os.path.exists(METADATA_CACHE_FILE):
            with open(METADATA_CACHE_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading metadata cache: {e}")
    return {}

def save_aircraft_metadata_cache():
    """Save aircraft metadata cache to file."""
    try:
        with open(METADATA_CACHE_FILE, 'w') as f:
            json.dump(aircraft_metadata_cache, f, indent=2)
    except Exception as e:
        print(f"Error saving metadata cache: {e}")

def load_opensky_csv_db():
    """Load OpenSky aircraft database CSV into a dictionary."""
    global opensky_csv_db
    if opensky_csv_db is not None:
        return opensky_csv_db
    db = {}
    if os.path.exists(OPENSKY_CSV_FILE):
        try:
            with open(OPENSKY_CSV_FILE, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    icao = row.get('icao24', '').lower()
                    if icao:
                        db[icao] = row
            print(f"Loaded OpenSky CSV database with {len(db)} records.")
        except Exception as e:
            print(f"Error loading OpenSky CSV: {e}")
    else:
        print(f"OpenSky CSV file '{OPENSKY_CSV_FILE}' not found.")
    opensky_csv_db = db
    return db

def fetch_aircraft_metadata_from_public_apis(icao24):
    """Fetch aircraft metadata from public APIs."""
    for api in PUBLIC_APIS:
        try:
            url = api['url'].format(icao24=icao24)
            response = requests.get(url, timeout=api['timeout'])
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse hexdb response
                if api['name'] == 'hexdb' and 'aircraft' in data:
                    aircraft = data['aircraft']
                    return {
                        'manufacturer': aircraft.get('manufacturer'),
                        'model': aircraft.get('type'),
                        'registration': aircraft.get('registration'),
                        'operator': aircraft.get('operator'),
                        'serialNumber': aircraft.get('serial_number')
                    }
                
                # Parse adsbexchange response
                elif api['name'] == 'adsbexchange' and 'acList' in data:
                    for ac in data['acList']:
                        if ac.get('Icao') == icao24:
                            return {
                                'manufacturer': ac.get('Man'),
                                'model': ac.get('Mdl'),
                                'registration': ac.get('Reg'),
                                'operator': ac.get('Op'),
                                'serialNumber': ac.get('Sqk')
                            }
                            
        except Exception as e:
            print(f"Error fetching from {api['name']}: {e}")
            continue
    
    return None

def fetch_aircraft_metadata_from_opensky_csv(icao24):
    db = load_opensky_csv_db()
    icao = icao24.lower()
    if icao in db:
        row = db[icao]
        return {
            'manufacturer': row.get('manufacturername'),
            'model': row.get('model'),
            'registration': row.get('registration'),
            'operator': row.get('operator'),
            'serialNumber': row.get('serialnumber')
        }
    return None

def get_aircraft_metadata(icao24):
    """Get aircraft metadata from cache or public APIs."""
    # Check cache first
    if icao24 in aircraft_metadata_cache:
        return aircraft_metadata_cache[icao24]
    
    # Try public APIs
    metadata = fetch_aircraft_metadata_from_public_apis(icao24)
    
    if metadata:
        # Cache the result
        aircraft_metadata_cache[icao24] = metadata
        save_aircraft_metadata_cache()
        return metadata
    
    # Try OpenSky CSV
    metadata = fetch_aircraft_metadata_from_opensky_csv(icao24)
    if metadata:
        aircraft_metadata_cache[icao24] = metadata
        save_aircraft_metadata_cache()
        return metadata
    
    return None

def get_opensky_token():
    """Get OpenSky OAuth2 access token."""
    try:
        # Load credentials
        client_id, client_secret = load_opensky_credentials()
        
        if not client_id or not client_secret:
            raise Exception("OpenSky OAuth2 credentials not found")
        
        # Get access token
        token_url = "https://auth.opensky-network.org/auth/realms/opensky-network/protocol/openid-connect/token"
        token_data = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }
        
        response = requests.post(token_url, data=token_data, timeout=30)
        
        if response.status_code == 200:
            token_info = response.json()
            return token_info.get('access_token')
        else:
            raise Exception(f"Failed to get access token: {response.status_code} - {response.text}")
    
    except Exception as e:
        print(f"Error getting OpenSky token: {e}")
        return None

def make_opensky_request(endpoint, params=None):
    """Make a request to the OpenSky API using OAuth2."""
    try:
        # Get access token
        access_token = get_opensky_token()
        
        if not access_token:
            raise Exception("Could not obtain OpenSky access token")
        
        url = f"{OPENSKY_BASE_URL}/{endpoint}"
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 401:
            raise Exception("Invalid OpenSky credentials or expired token")
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded. Please try again later.")
        elif response.status_code == 404:
            return None  # Not found, return None instead of raising exception
        elif response.status_code != 200:
            raise Exception(f"OpenSky API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    except requests.exceptions.Timeout:
        raise Exception("Request to OpenSky API timed out")
    except requests.exceptions.ConnectionError:
        raise Exception("Failed to connect to OpenSky API")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request error: {str(e)}")

def make_aerodatabox_request(endpoint, params=None):
    """Make a request to the AeroDataBox API."""
    try:
        # Load credentials
        api_key, api_host = load_aerodatabox_credentials()
        if not api_key or not api_host:
            raise Exception("AeroDataBox API credentials not loaded")
        
        url = f"{AERODATABOX_BASE_URL}/{endpoint}"
        
        headers = {
            'x-rapidapi-key': api_key,
            'x-rapidapi-host': api_host,
            'User-Agent': 'Flight-Tracker-Proxy/1.0'
        }
        
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 401 or response.status_code == 403:
            raise Exception("Invalid AeroDataBox API credentials")
        elif response.status_code == 429:
            raise Exception("Rate limit exceeded. Please try again later.")
        elif response.status_code == 404:
            return None  # Not found, return None instead of raising exception
        elif response.status_code != 200:
            raise Exception(f"AeroDataBox API error: {response.status_code} - {response.text}")
        
        return response.json()
    
    except requests.exceptions.Timeout:
        raise Exception("Request to AeroDataBox API timed out")
    except requests.exceptions.ConnectionError:
        raise Exception("Failed to connect to AeroDataBox API")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request error: {str(e)}")

def get_cached_or_fetch(cache_key, fetch_function, *args, **kwargs):
    """Get data from cache or fetch new data if not cached or expired."""
    now = time.time()
    
    if cache_key in cache:
        cached_data, timestamp = cache[cache_key]
        if now - timestamp < CACHE_DURATION:
            return cached_data
    
    # Fetch new data
    data = fetch_function(*args, **kwargs)
    cache[cache_key] = (data, now)
    return data

# OpenSky API functions
def fetch_opensky_states(lat, lon, radius_km):
    """Fetch state vectors for aircraft within a radius."""
    # Convert radius to a bounding box
    # 1 degree of latitude is approximately 111 km
    # 1 degree of longitude is approximately 111*cos(lat) km
    lat_km = 111.32
    lon_km = 111.32 * math.cos(math.radians(lat))
    
    lat_delta = radius_km / lat_km
    lon_delta = radius_km / lon_km
    
    # Calculate bounding box
    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    min_lon = lon - lon_delta
    max_lon = lon + lon_delta
    
    # Query OpenSky with the bounding box
    params = {
        'lamin': min_lat,
        'lomin': min_lon,
        'lamax': max_lat,
        'lomax': max_lon
    }
    
    return make_opensky_request('states/all', params)

def process_opensky_states(states_data, center_lat, center_lon, radius_km):
    """Process and filter OpenSky state vectors."""
    if not states_data or 'states' not in states_data or not states_data['states']:
        return []
    
    result = []
    for state in states_data['states']:
        # OpenSky states format: [icao24, callsign, country, ..., longitude, latitude, ...]
        icao24 = state[0]
        callsign = state[1].strip() if state[1] else None
        country = state[2]
        longitude = state[5]
        latitude = state[6]
        
        # Skip if no position data
        if longitude is None or latitude is None:
            continue
        
        # Calculate actual distance to verify it's in the radius
        distance = calculate_distance(center_lat, center_lon, latitude, longitude)
        if distance > radius_km:
            continue
        
        # Basic aircraft data from OpenSky
        aircraft_data = {
            'icao24': icao24,
            'callsign': callsign,
            'country': country,
            'latitude': latitude,
            'longitude': longitude,
            'altitude': state[7] * 3.28084 if state[7] else None,  # Convert m to feet
            'speed': state[9] * 1.94384 if state[9] else None,  # Convert m/s to knots
            'heading': state[10],
            'verticalRate': state[11] * 196.85 if state[11] else None,  # Convert m/s to ft/min
            'onGround': state[8],
            'distance': round(distance, 1)
        }
        
        result.append(aircraft_data)
    
    # Sort by distance from center point
    result.sort(key=lambda x: x['distance'])
    return result

# AeroDataBox API functions
def fetch_aircraft_details(icao):
    """Fetch aircraft details from AeroDataBox API."""
    endpoint = f"v2/aircraft/{icao}"
    return make_aerodatabox_request(endpoint)

def fetch_aircraft_flights(icao):
    """Fetch current flight info for an aircraft."""
    endpoint = f"v2/flights/aircraft/{icao}/position"
    return make_aerodatabox_request(endpoint)

def fetch_airport_details(icao_code):
    """Fetch airport details by ICAO code."""
    endpoint = f"v1/airports/icao/{icao_code}"
    return make_aerodatabox_request(endpoint)

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in kilometers."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return R * c

# Import the existing VestaboardAPI class
from vestaboard_api import VestaboardAPI

class VestaboardClient:
    """Wrapper for the existing VestaboardAPI class"""
    
    def __init__(self, api_key, base_url="http://192.168.1.70:7000"):
        self.api = VestaboardAPI(api_key, base_url)
    
    def send_message(self, text):
        """Send a text message to the Vestaboard"""
        try:
            success = self.api.send_message(text)
            if success:
                print(f"✅ Vestaboard message sent successfully!")
            else:
                print(f"❌ Failed to send Vestaboard message")
            return success
        except Exception as e:
            print(f"❌ Error sending Vestaboard message: {str(e)}")
            return False
    
    def test_connection(self):
        """Test connection to Vestaboard"""
        try:
            return self.api.test_connection()
        except Exception as e:
            print(f"❌ Vestaboard connection test failed: {str(e)}")
            return False

def load_vestaboard_config():
    """Load Vestaboard configuration from config file"""
    global VESTABOARD_ENABLED
    
    try:
        if not os.path.exists(VESTABOARD_CONFIG_FILE):
            print(f"⚠️ Vestaboard config file not found: {VESTABOARD_CONFIG_FILE}")
            return None
        
        with open(VESTABOARD_CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        if 'vestaboard' in config:
            vesta_config = config['vestaboard']
            api_key = vesta_config.get('apiKey')
            local_url = vesta_config.get('localUrl')
            
            if api_key and local_url:
                VESTABOARD_ENABLED = True
                return VestaboardClient(api_key, local_url)
            else:
                print("⚠️ Vestaboard config missing apiKey or localUrl")
                return None
        else:
            print("⚠️ Vestaboard config file missing 'vestaboard' section")
            return None
    
    except Exception as e:
        print(f"❌ Error loading Vestaboard config: {str(e)}")
        return None

def format_flight_notification(aircraft_data):
    """
    Format aircraft data for Vestaboard display
    Returns a formatted string suitable for the 6x22 character display
    """
    # Debug logging to see what data we're receiving
    print(f"🔍 Formatting notification for aircraft {aircraft_data.get('icao24', 'unknown')}")
    print(f"   All available fields: {list(aircraft_data.keys())}")
    print(f"   Callsign: {aircraft_data.get('callsign', 'N/A')}")
    print(f"   Manufacturer: {aircraft_data.get('manufacturer', 'N/A')}")
    print(f"   Model: {aircraft_data.get('model', 'N/A')}")
    print(f"   Registration: {aircraft_data.get('registration', 'N/A')}")
    print(f"   Operator: {aircraft_data.get('operator', 'N/A')}")
    print(f"   Owner: {aircraft_data.get('owner', 'N/A')}")
    print(f"   AircraftType: {aircraft_data.get('aircraftType', 'N/A')}")
    print(f"   RegisteredOwner: {aircraft_data.get('registeredOwner', 'N/A')}")
    print(f"   Country: {aircraft_data.get('country', 'N/A')}")
    
    # Extract key information - use both possible field names
    callsign = aircraft_data.get('callsign', 'UNKNOWN').strip()
    
    # Try to get altitude and heading from different possible sources
    altitude = aircraft_data.get('altitude', 0)
    heading = aircraft_data.get('heading', 0)
    
    # If not found as numbers, try parsing from position string
    if not altitude or not heading:
        position_str = aircraft_data.get('position', '')
        if position_str:
            try:
                # Extract altitude (e.g., "22750 ft")
                alt_part = position_str.split('|')[0].strip()
                altitude = int(alt_part.split()[0])
                # Extract heading (e.g., "207°")
                heading_part = position_str.split('|')[1].strip()
                heading = int(heading_part.replace('°', ''))
            except:
                pass
    
    # Try to get speed from different possible sources
    speed = aircraft_data.get('speed', 0)
    if isinstance(speed, str):
        try:
            speed = int(speed.split()[0])
        except:
            speed = 0
    
    # Try to get manufacturer and model from different possible sources
    manufacturer = aircraft_data.get('manufacturer', '')
    model = aircraft_data.get('model', '')
    
    # If not found, try parsing from aircraftType (this is the main source based on console output)
    if not manufacturer or not model:
        aircraft_type_str = aircraft_data.get('aircraftType', '')
        if aircraft_type_str:
            if ':' in aircraft_type_str:
                parts = aircraft_type_str.split(':', 1)
                manufacturer = parts[0].strip()
                model = parts[1].strip()
            else:
                model = aircraft_type_str
    
    registration = aircraft_data.get('registration', '')
    # Based on console output, the field is 'registeredOwner'
    operator = aircraft_data.get('registeredOwner', '')
    owner = aircraft_data.get('registeredOwner', '')
    country = aircraft_data.get('country', '')
    
    # Format altitude, speed, and heading (0 decimal places)
    alt_str = f"{int(altitude):,} ft" if altitude else "N/A"
    speed_str = f"{int(speed)} knots" if speed else "N/A"
    heading_str = f"{int(heading)}°" if heading else "N/A"
    
    # Create aircraft type string
    if manufacturer and model:
        aircraft_type = f"{manufacturer} {model}".replace("  ", " ").strip()
    elif manufacturer:
        aircraft_type = manufacturer
    elif model:
        aircraft_type = model
    else:
        aircraft_type = "Unknown"
    
    # Create owner/operator string (prioritize operator, then owner)
    owner_operator = ""
    if operator:
        owner_operator = operator
    elif owner:
        owner_operator = owner
    
    # Truncate long strings to fit display (22 characters max)
    callsign = callsign[:22] if len(callsign) > 22 else callsign
    registration = registration[:22] if len(registration) > 22 else registration
    owner_operator = owner_operator[:22] if len(owner_operator) > 22 else owner_operator
    aircraft_type = aircraft_type[:22] if len(aircraft_type) > 22 else aircraft_type
    country = country[:22] if len(country) > 22 else country
    
    # Format the message for 6x22 display
    lines = [
        f"{callsign}   {registration}",
        f"{owner_operator}  {country}",
        f"{aircraft_type}",
        f"{alt_str}",
        f"{speed_str}",
        f"{heading_str}"
    ]
    
    return "\n".join(lines)

def notify_new_aircraft(aircraft_data):
    """
    Send notification to Vestaboard for new aircraft entering geofence
    Only sends notification once per aircraft per session
    """
    global tracked_aircraft, VESTABOARD_ENABLED
    
    if not VESTABOARD_ENABLED:
        return False
    
    icao24 = aircraft_data.get('icao24')
    if not icao24:
        return False
    
    # Check if we've already notified about this aircraft
    if icao24 in tracked_aircraft:
        return False
    
    # Load Vestaboard client
    vesta_client = load_vestaboard_config()
    if not vesta_client:
        return False
    
    # Test connection
    if not vesta_client.test_connection():
        print("❌ Cannot connect to Vestaboard")
        return False
    
    # Format and send notification
    notification_text = format_flight_notification(aircraft_data)
    
    if vesta_client.send_message(notification_text):
        # Mark this aircraft as notified
        tracked_aircraft.add(icao24)
        print(f"✅ Vestaboard notification sent for aircraft {icao24}")
        return True
    else:
        print(f"❌ Failed to send Vestaboard notification for aircraft {icao24}")
        return False

@app.route('/')
def index():
    """Root endpoint - provides API information."""
    return jsonify({
        'name': 'Flight Tracker Backend',
        'version': '1.0',
        'endpoints': {
            '/api/aircraft/details': 'Get aircraft details by ICAO',
            '/api/aircraft': 'Get aircraft near a location',
            '/api/health': 'Health check endpoint'
        }
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    opensky_client_id, opensky_client_secret = load_opensky_credentials()
    aerodatabox_key, aerodatabox_host = load_aerodatabox_credentials()
    
    # Check Vestaboard status
    vesta_client = load_vestaboard_config()
    vestaboard_connected = False
    if vesta_client:
        vestaboard_connected = vesta_client.test_connection()
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'opensky_credentials_loaded': opensky_client_id is not None and opensky_client_secret is not None,
        'aerodatabox_credentials_loaded': aerodatabox_key is not None and aerodatabox_host is not None,
        'vestaboard_enabled': VESTABOARD_ENABLED,
        'vestaboard_connected': vestaboard_connected,
        'tracked_aircraft_count': len(tracked_aircraft),
        'apis': ['OpenSky', 'AeroDataBox', 'Vestaboard']
    })

@app.route('/api/aircraft/details')
def get_aircraft_details():
    """
    Get detailed aircraft information.
    
    Query Parameters:
    - icao24: ICAO24 identifier for the aircraft (required)
    
    Returns:
    JSON object with aircraft details
    """
    icao24 = request.args.get('icao24')
    
    if not icao24:
        return jsonify({'error': 'Missing icao24 parameter'}), 400
    
    try:
        print(f"Fetching details for aircraft {icao24}")
        details_cache_key = f"aircraft_details_{icao24}"
        aircraft_details = get_cached_or_fetch(
            details_cache_key,
            fetch_aircraft_details,
            icao24
        )
        # Fallback: If AeroDataBox returns nothing useful, try hexdb
        if not aircraft_details or not any([
            aircraft_details.get('model'),
            aircraft_details.get('manufacturer'),
            aircraft_details.get('registration')
        ]):
            print(f"AeroDataBox returned no data for {icao24}, trying hexdb...")
            aircraft_details = get_aircraft_metadata(icao24)
        flight_cache_key = f"aircraft_flight_{icao24}"
        flight_info = get_cached_or_fetch(
            flight_cache_key,
            fetch_aircraft_flights,
            icao24
        )
        route_info = None
        if flight_info and 'departure' in flight_info and 'arrival' in flight_info:
            departure_airport = flight_info.get('departure', {}).get('airport', {}).get('icao')
            arrival_airport = flight_info.get('arrival', {}).get('airport', {}).get('icao')
            if departure_airport and arrival_airport:
                dep_cache_key = f"airport_{departure_airport}"
                departure_details = get_cached_or_fetch(
                    dep_cache_key,
                    fetch_airport_details,
                    departure_airport
                )
                arr_cache_key = f"airport_{arrival_airport}"
                arrival_details = get_cached_or_fetch(
                    arr_cache_key,
                    fetch_airport_details,
                    arrival_airport
                )
                route_info = {
                    'from': departure_airport,
                    'to': arrival_airport,
                    'fromName': departure_details.get('fullName') if departure_details else None,
                    'toName': arrival_details.get('fullName') if arrival_details else None,
                    'departureTime': flight_info.get('departure', {}).get('scheduledTime', {}).get('utc'),
                    'arrivalTime': flight_info.get('arrival', {}).get('scheduledTime', {}).get('utc')
                }
        current_position = None
        if flight_info and 'position' in flight_info:
            position = flight_info.get('position', {})
            current_position = {
                'latitude': position.get('latitude'),
                'longitude': position.get('longitude'),
                'altitude': position.get('altitude', {}).get('feet'),
                'speed': position.get('groundSpeed', {}).get('knots'),
                'heading': position.get('heading'),
                'verticalRate': position.get('verticalRate'),
                'timestamp': position.get('reportedAt')
            }
        meta = None
        if aircraft_details:
            meta = {
                'model': aircraft_details.get('model'),
                'manufacturer': aircraft_details.get('manufacturer'),
                'registration': aircraft_details.get('registration'),
                'serialNumber': aircraft_details.get('serialNumber'),
                'operator': aircraft_details.get('operator'),
                'age': aircraft_details.get('age'),
                'callsign': flight_info.get('callsign') if flight_info else None,
                'flightNumber': flight_info.get('number') if flight_info else None
            }
            if current_position:
                meta.update({
                    'altitude': current_position.get('altitude'),
                    'speed': current_position.get('speed'),
                    'heading': current_position.get('heading'),
                    'verticalRate': current_position.get('verticalRate'),
                    'onGround': current_position.get('altitude', 0) <= 100
                })
        response_data = {
            'icao24': icao24,
            'meta': meta,
            'route': route_info,
            'position': current_position,
            'rawData': {
                'aircraft': aircraft_details,
                'flight': flight_info
            },
            'timestamp': datetime.now().isoformat()
        }
        print(f"Successfully fetched details for {icao24}")
        return jsonify(response_data)
    except Exception as e:
        error_message = str(e)
        print(f"Error fetching details for {icao24}: {error_message}")
        return jsonify({
            'error': error_message,
            'icao24': icao24,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/aircraft')
def get_nearby_aircraft():
    """
    Get aircraft near a specific location.
    
    Query Parameters:
    - lat: Latitude (required)
    - lon: Longitude (required)
    - radius: Radius in kilometers (optional, default 10)
    
    Returns:
    JSON array with aircraft information
    """
    try:
        # Get request parameters
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        radius = request.args.get('radius', default=3)
        
        if not lat or not lon:
            return jsonify({'error': 'Missing lat/lon parameters'}), 400
        
        # Convert to float
        try:
            lat = float(lat)
            lon = float(lon)
            radius = float(radius)
        except ValueError:
            return jsonify({'error': 'Invalid parameter format'}), 400
        
        # Validate parameter ranges
        if not (-90 <= lat <= 90):
            return jsonify({'error': 'Latitude must be between -90 and 90'}), 400
        if not (-180 <= lon <= 180):
            return jsonify({'error': 'Longitude must be between -180 and 180'}), 400
        if not (1 <= radius <= 100):
            return jsonify({'error': 'Radius must be between 1 and 100 km'}), 400
        
        # Fetch flights from OpenSky API
        print(f"Fetching aircraft near position ({lat}, {lon}) with radius {radius}km")
        cache_key = f"nearby_aircraft_{lat}_{lon}_{radius}"
        
        opensky_data = get_cached_or_fetch(
            cache_key,
            fetch_opensky_states,
            lat, lon, radius
        )
        
        # Process and filter OpenSky data
        aircraft_list = process_opensky_states(opensky_data, lat, lon, radius)
        
        if not aircraft_list:
            return jsonify([])
        
        print(f"Found {len(aircraft_list)} aircraft near position")
        
        # Enrich the first few aircraft with AeroDataBox data if possible
        # We limit to avoid hitting rate limits
        enrichment_limit = min(5, len(aircraft_list))
        for i in range(enrichment_limit):
            try:
                icao24 = aircraft_list[i]['icao24']
                # Check if we already have this data cached
                details_cache_key = f"aircraft_details_{icao24}"
                flight_cache_key = f"aircraft_flight_{icao24}"
                
                if details_cache_key in cache:
                    aircraft_details, _ = cache[details_cache_key]
                    if aircraft_details:
                        aircraft_list[i]['manufacturer'] = aircraft_details.get('manufacturer')
                        aircraft_list[i]['model'] = aircraft_details.get('model')
                        aircraft_list[i]['registration'] = aircraft_details.get('registration')
                        aircraft_list[i]['operator'] = aircraft_details.get('operator')
                        aircraft_list[i]['owner'] = aircraft_details.get('owner')
                
                if flight_cache_key in cache:
                    flight_info, _ = cache[flight_cache_key]
                    if flight_info:
                        aircraft_list[i]['flightNumber'] = flight_info.get('number')
                        
                        # Extract route if available
                        if 'departure' in flight_info and 'arrival' in flight_info:
                            departure = flight_info.get('departure', {}).get('airport', {}).get('icao')
                            arrival = flight_info.get('arrival', {}).get('airport', {}).get('icao')
                            
                            if departure and arrival:
                                aircraft_list[i]['route'] = {
                                    'from': departure,
                                    'to': arrival
                                }
            except Exception as e:
                print(f"Error enriching aircraft data for {aircraft_list[i]['icao24']}: {str(e)}")
                # Continue with the next aircraft if one fails
                continue
        
        # Vestaboard notifications are now handled in the frontend
        # where the enriched data is available
                
        return jsonify(aircraft_list)
    
    except Exception as e:
        error_message = str(e)
        print(f"Error fetching nearby aircraft: {error_message}")
        
        return jsonify({
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/vestaboard/test')
def test_vestaboard():
    """Test Vestaboard connection and send a test message."""
    try:
        vesta_client = load_vestaboard_config()
        if not vesta_client:
            return jsonify({
                'error': 'Vestaboard not configured',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Test connection
        if not vesta_client.test_connection():
            return jsonify({
                'error': 'Cannot connect to Vestaboard',
                'timestamp': datetime.now().isoformat()
            }), 500
        
        # Send test message
        test_message = "FLIGHT TRACKER TEST\nVestaboard Connected!\nReady for notifications\n" + datetime.now().strftime("%H:%M:%S")
        
        if vesta_client.send_message(test_message):
            return jsonify({
                'status': 'success',
                'message': 'Test message sent successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'error': 'Failed to send test message',
                'timestamp': datetime.now().isoformat()
            }), 500
    
    except Exception as e:
        error_message = str(e)
        print(f"Error testing Vestaboard: {error_message}")
        
        return jsonify({
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/vestaboard/notify', methods=['POST'])
def vestaboard_notify():
    """Send notification to Vestaboard from frontend."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract aircraft data from frontend
        aircraft_data = data.get('aircraft', {})
        if not aircraft_data:
            return jsonify({'error': 'No aircraft data provided'}), 400
        
        # Send notification
        success = notify_new_aircraft(aircraft_data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Notification sent successfully',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'error': 'Failed to send notification',
                'timestamp': datetime.now().isoformat()
            }), 500
    
    except Exception as e:
        error_message = str(e)
        print(f"Error sending Vestaboard notification: {error_message}")
        
        return jsonify({
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/vestaboard/status')
def vestaboard_status():
    """Get Vestaboard status and tracked aircraft count."""
    try:
        vesta_client = load_vestaboard_config()
        vestaboard_connected = False
        
        if vesta_client:
            vestaboard_connected = vesta_client.test_connection()
        
        return jsonify({
            'vestaboard_enabled': VESTABOARD_ENABLED,
            'vestaboard_connected': vestaboard_connected,
            'tracked_aircraft_count': len(tracked_aircraft),
            'tracked_aircraft': list(tracked_aircraft)[:10],  # Show first 10
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        error_message = str(e)
        print(f"Error getting Vestaboard status: {error_message}")
        
        return jsonify({
            'error': error_message,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🛩️  Flight Tracker Backend Starting...")
    print("="*50)
    
    # Check OpenSky credentials on startup
    opensky_client_id, opensky_client_secret = load_opensky_credentials()
    if opensky_client_id and opensky_client_secret:
        print(f"✅ OpenSky OAuth2 credentials loaded for {opensky_client_id}")
    else:
        print("⚠️ WARNING: OpenSky OAuth2 credentials not found or invalid")
        print("   Anonymous access will be used (rate limited)")
    
    # Check AeroDataBox credentials on startup
    aerodatabox_key, aerodatabox_host = load_aerodatabox_credentials()
    if aerodatabox_key and aerodatabox_host:
        print(f"✅ AeroDataBox API credentials loaded!")
    else:
        print("❌ WARNING: Could not load AeroDataBox API credentials!")
        print(f"   Aircraft enrichment features will be limited.")
    
    # Check Vestaboard configuration on startup
    vesta_client = load_vestaboard_config()
    if vesta_client and vesta_client.test_connection():
        print(f"✅ Vestaboard connected and ready for flight notifications!")
    elif VESTABOARD_ENABLED:
        print("⚠️ WARNING: Vestaboard enabled but connection failed!")
        print("   Flight notifications will not be sent.")
    else:
        print("ℹ️  Vestaboard not configured - flight notifications disabled")
    
    print("\n📡 API Endpoints:")
    print("   GET  /                     - API information")
    print("   GET  /api/health           - Health check")
    print("   GET  /api/aircraft/details - Aircraft details by ICAO")
    print("   GET  /api/aircraft         - Aircraft near a location")
    print("   GET  /api/vestaboard/test  - Test Vestaboard connection")
    print("   GET  /api/vestaboard/status - Vestaboard status")
    print("   POST /api/vestaboard/notify - Send notification from frontend")
    
    print("\n🔀 Hybrid API Strategy:")
    print("   - Using OpenSky for geofence aircraft detection")
    print("   - Using AeroDataBox for aircraft metadata enrichment")
    print("   - Using Vestaboard for flight notifications")
    
    print(f"\n🌐 Server will be available at: http://localhost:5000")
    print("   Make sure to enable CORS in your browser if needed.")
    
    print("\n🔧 Cache Settings:")
    print(f"   Cache duration: {CACHE_DURATION} seconds")
    print("   This helps avoid API rate limits.")
    
    print("\n" + "="*50)
    print("Starting Flask development server...")
    
    # Run the Flask app
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        threaded=True
    )