# Air Overhead Auto-Detection System

## Overview

The Auto-Detection system provides continuous monitoring of aircraft in your area without requiring a browser to be open. It automatically detects aircraft entering your specified geofence and can send notifications to your Vestaboard.

## Features

- ✅ **Continuous Monitoring**: Checks for aircraft every second (configurable)
- ✅ **Automatic Notifications**: Sends Vestaboard notifications when new aircraft are detected
- ✅ **Production Ready**: Enhanced error handling, logging, and retry logic
- ✅ **Statistics Tracking**: Monitors performance and provides detailed statistics
- ✅ **Easy Startup**: Simple scripts to start everything with one command
- ✅ **Cross-Platform**: Works on Windows, Linux, and macOS

## Quick Start

### Windows Users
```bash
# Double-click or run:
start_auto_detection.bat
```

### Linux/Mac Users
```bash
# Make executable and run:
chmod +x start_auto_detection.sh
./start_auto_detection.sh
```

### Manual Start
```bash
# 1. Start the Flask server (in background)
python app.py &

# 2. Start auto-detection
python auto_detection.py
```

## Configuration

### Location Settings
Edit `auto_detection.py` to set your location:

```python
# Update these to match your location
YOUR_LAT = 51.5995  # Your latitude
YOUR_LON = -0.5545  # Your longitude  
YOUR_RADIUS = 2     # Detection radius in km
```

### Check Interval
Change how frequently the system checks for aircraft:

```python
CHECK_INTERVAL = 1  # seconds between checks
```

### Vestaboard Configuration
Ensure your `vestaboard_config.json` is properly configured:

```json
{
  "vestaboard": {
    "localUrl": "http://192.168.1.70:7000",
    "apiKey": "your_vestaboard_api_key_here",
    "enablementToken": "your_enablement_token_here",
    "readEndpoint": "/local-api/message",
    "writeEndpoint": "/local-api/message"
  }
}
```

## How It Works

1. **Server Health Check**: Verifies the Flask server is running
2. **Vestaboard Status**: Checks if Vestaboard is configured and connected
3. **Continuous Monitoring**: Polls the aircraft API every second
4. **Automatic Notifications**: The Flask server handles Vestaboard notifications
5. **Statistics Tracking**: Logs performance metrics and aircraft counts
6. **Error Handling**: Retries failed requests with exponential backoff

## Logging

The system creates detailed logs in `auto_detection.log`:

```
2024-01-15 10:30:15,123 - INFO - 🛩️  Automated Flight Detection - Production Ready
2024-01-15 10:30:15,124 - INFO - ✅ Flask server is running and healthy
2024-01-15 10:30:15,125 - INFO - ✅ Vestaboard connected - notifications will be sent
2024-01-15 10:30:16,126 - INFO - [10:30:16] No aircraft detected
2024-01-15 10:30:17,127 - INFO - [10:30:17] Found 3 aircraft
```

## Statistics

The system tracks:
- Runtime duration
- Number of checks performed
- Total aircraft detected
- Error count
- Current aircraft count
- Average check interval

Statistics are displayed every 100 checks and when the script stops.

## Error Handling

- **Connection Errors**: Retries up to 3 times with 5-second delays
- **Server Errors**: Logs HTTP errors and continues monitoring
- **Vestaboard Errors**: Continues monitoring even if notifications fail
- **Graceful Shutdown**: Properly stops both Flask server and auto-detection

## Troubleshooting

### Flask Server Not Starting
```bash
# Check if port 5000 is in use
netstat -an | grep :5000

# Kill any existing processes
taskkill /F /IM python.exe  # Windows
pkill -f "python.*app.py"   # Linux/Mac
```

### Vestaboard Not Connected
1. Verify your `vestaboard_config.json` has correct credentials
2. Check your Vestaboard device is powered on and connected to network
3. Test the connection manually:
   ```bash
   python test_vestaboard_integration.py
   ```

### No Aircraft Detected
1. Verify your coordinates are correct
2. Try increasing the radius (e.g., 5-10 km)
3. Check if there's air traffic in your area
4. Verify OpenSky API credentials in `credentials.json`

### High Error Rate
1. Check your internet connection
2. Verify OpenSky API rate limits
3. Consider increasing `CHECK_INTERVAL` to reduce API calls

## Performance Tuning

### For High-Traffic Areas
```python
CHECK_INTERVAL = 5  # Check every 5 seconds instead of 1
YOUR_RADIUS = 1     # Reduce radius to focus on closer aircraft
```

### For Low-Traffic Areas
```python
CHECK_INTERVAL = 10  # Check every 10 seconds
YOUR_RADIUS = 5      # Increase radius to catch more aircraft
```

### For Production Use
```python
MAX_RETRIES = 5      # More retries for reliability
RETRY_DELAY = 10     # Longer delays between retries
```

## Integration with Web Interface

The auto-detection system works alongside the web interface:
- Both use the same Flask server
- Both share the same Vestaboard configuration
- Both access the same aircraft data
- Web interface can be used for manual checks while auto-detection runs

## System Requirements

- Python 3.7+
- Internet connection
- Vestaboard device (optional, for notifications)
- OpenSky API credentials (optional, for better rate limits)

## Files

- `auto_detection.py` - Main auto-detection script
- `start_auto_detection.py` - Startup script for both server and detection
- `start_auto_detection.bat` - Windows batch file
- `start_auto_detection.sh` - Linux/Mac shell script
- `auto_detection.log` - Log file (created automatically)

## Support

For issues or questions:
1. Check the log file for error details
2. Verify all configuration files are present
3. Test individual components manually
4. Check the main project README for additional information 