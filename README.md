# 🛩️ Local Flight Tracker

A real-time flight tracking application that displays aircraft in a user-defined area with detailed information including routes, aircraft types, and operators. Built with a local HTML/JavaScript frontend and a Python Flask backend proxy.

## 📋 Features

### Frontend (HTML/JavaScript)
- **Real-time flight tracking** with auto-refresh capability
- **Interactive map** (Leaflet.js) showing aircraft positions and search radius
- **Detailed flight information** including:
  - Flight route (departure → destination)
  - Aircraft operator/airline
  - Aircraft type and model
  - Altitude, speed, heading, and vertical rate
  - All OpenSky state vector fields
  - Registration and country information
- **Geofencing** with user-defined center point and radius
- **"Use My Location"** button for automatic positioning
- **Raw data viewer** for technical users
- **Direct links** to OpenSky aircraft profiles
- **Responsive design** that works on desktop and mobile

### Backend (Python Flask)
- **Proxy server** for OpenSky API with authentication
- **Aircraft metadata** fetching (type, operator, registration)
- **Flight route information** from recent flight history
- **Caching system** to avoid rate limits
- **CORS enabled** for local browser access
- **Error handling** with detailed status messages
- **Vestaboard integration** for flight notifications

## 🚀 Quick Start

### Prerequisites

1. **Python 3.7+** installed on your system
2. **OpenSky Network account** (free registration at [opensky-network.org](https://opensky-network.org))
3. **Web browser** with JavaScript enabled

### Installation

#### Quick Install (Recommended)

**Windows:**
```bash
install.bat
```

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

#### Manual Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up configuration files**:
   ```bash
   # Copy credential templates
   cp credentials.json.example credentials.json
   cp vestaboard_config.json.example vestaboard_config.json
   ```
   
3. **Edit configuration files**:
   
   **OpenSky credentials** (`credentials.json`):
   ```json
   {
       "username": "your_opensky_username",
       "password": "your_opensky_password"
   }
   ```
   
   **Vestaboard configuration** (`vestaboard_config.json`):
   ```json
   {
     "vestaboard": {
       "localUrl": "http://192.168.1.70:7000",
       "apiKey": "your_vestaboard_api_key_here",
       "enablementToken": "your_enablement_token_here"
     }
   }
   ```

### Running the Application

#### Quick Start
```bash
python run.py
```

This will:
- Start the Flask backend server
- Automatically open your web browser to the application
- Display the flight tracking interface

#### Manual Start
1. **Start the Flask backend**:
   ```bash
   python app.py
   ```

2. **Open the frontend**:
   Open `index.html` in your web browser or go to `http://localhost:5000`

3. **Start tracking flights**:
   - Set your location (or click "📍 My Location")
   - Set your desired search radius
   - Click "🔍 Search" to find flights
   - Optionally enable auto-refresh for live updates

## 🎯 Usage Guide

### Setting Search Parameters

- **Latitude/Longitude**: Enter coordinates manually or use "My Location"
- **Radius**: Set search radius in kilometers (1-500 km)
- **Auto-refresh**: Enable 30-second automatic updates

## 📺 Vestaboard Integration

The Flight Tracker can send notifications to a Vestaboard display when new aircraft enter your geofence. This provides real-time flight alerts on your physical display.

### Setup

1. **Enable Vestaboard Local API**:
   - Request Local API access from Vestaboard
   - Use your enablement token to enable the Local API
   - Save your API key

2. **Configure Vestaboard**:
   - Ensure your `vestaboard_config.json` file is in the parent directory
   - The config should contain your API key and board's local URL

3. **Test Connection**:
   ```bash
   python test_vestaboard_integration.py
   ```

### How It Works

- **Automatic Detection**: When aircraft enter your geofence, the system automatically detects them
- **One-time Notifications**: Each aircraft is only notified once per session to avoid spam
- **Rich Information**: Displays flight callsign, aircraft type, altitude, speed, and registration
- **6x22 Display**: Optimized for Vestaboard's character grid

### API Endpoints

- `GET /api/vestaboard/test` - Test Vestaboard connection and send test message
- `GET /api/vestaboard/status` - Get Vestaboard status and tracked aircraft count

### Example Notification

```
RYR717W   EI-IGO
Ryanair  Ireland
Boeing 737MAX 8 200
36000 ft
429 knots 
277°
```

**Note**: All numeric values (altitude, speed, heading) are displayed with 0 decimal places for cleaner formatting.

**Format**: The display shows callsign and registration on line 1, operator and country on line 2, aircraft type on line 3, altitude on line 4, speed on line 5, and heading on line 6.

### Understanding Flight Data

#### Basic Information (from OpenSky state vectors):
- **Callsign**: Flight number or aircraft identifier
- **Country**: Country of registration
- **ICAO24**: Unique aircraft identifier
- **Altitude**: Current altitude in feet
- **Speed**: Ground speed in knots
- **Heading**: Direction of travel in degrees
- **Vertical Rate**: Climb/descent rate in ft/min
- **On Ground**: Whether aircraft is on the ground
- **Squawk**: Transponder code

#### Enhanced Information (from backend proxy):
- **Route**: Departure and destination airports
- **Operator**: Airline or aircraft operator
- **Aircraft Type**: Manufacturer and model
- **Registration**: Aircraft registration number

## 🎉 Enjoy tracking flights!

The application provides a comprehensive view of air traffic in your area with rich detail about each flight. Perfect for aviation enthusiasts, researchers, or anyone curious about the aircraft overhead.