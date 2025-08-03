# Vestaboard Local API Client

A clean, reusable Python client for sending data to Vestaboard displays using the Local API.

## Features

- ✅ **Simple API**: Easy-to-use interface for sending messages
- ✅ **Multi-line Support**: Send messages with line breaks
- ✅ **Color Support**: Include color chips in your messages
- ✅ **Read Board**: Get current board content
- ✅ **Raw Codes**: Send custom character codes for advanced usage
- ✅ **Error Handling**: Robust error handling and connection testing
- ✅ **Type Hints**: Full type annotations for better IDE support

## Quick Start

### Installation

1. Copy `vestaboard_api.py` to your project
2. Install the required dependency:
   ```bash
   pip install requests
   ```

### Basic Usage

```python
from vestaboard_api import VestaboardAPI

# Initialize with your API key
vesta = VestaboardAPI("your_api_key_here")

# Send a simple message
vesta.send_message("Hello World!")

# Send a multi-line message
vesta.send_message("Line 1\nLine 2\nLine 3")

# Send with colors
vesta.send_message("Hello 🔴 World 🟢!")

# Read current board content
content = vesta.read_board()
if content:
    print(f"Current board: {content}")
```

## API Reference

### VestaboardAPI Class

#### Constructor

```python
VestaboardAPI(api_key: str, base_url: str = "http://192.168.1.70:7000")
```

- `api_key`: Your Vestaboard Local API key
- `base_url`: Base URL of your Vestaboard (default: your board's IP)

#### Methods

##### send_message(text: str) -> bool

Send a text message to the Vestaboard.

```python
# Simple message
vesta.send_message("Hello World!")

# Multi-line message
vesta.send_message("Line 1\nLine 2\nLine 3")

# Message with colors
vesta.send_message("Hello 🔴 World 🟢!")
```

##### read_board() -> Optional[str]

Read the current content of the Vestaboard.

```python
content = vesta.read_board()
if content:
    print(f"Current board: {content}")
```

##### clear_board() -> bool

Clear the board (send all blanks).

```python
vesta.clear_board()
```

##### send_raw_codes(character_codes: List[List[int]]) -> bool

Send raw character codes to the Vestaboard.

```python
# Send "HELLO" on line 1
codes = [[8, 5, 12, 12, 15] + [0] * 17] + [[0] * 22] * 5
vesta.send_raw_codes(codes)
```

##### test_connection() -> bool

Test the connection to the Vestaboard.

```python
if vesta.test_connection():
    print("Connection successful!")
else:
    print("Connection failed!")
```

##### get_board_raw() -> Optional[Dict]

Get the raw board data (character codes).

```python
raw_data = vesta.get_board_raw()
if raw_data:
    print(f"Raw board data: {raw_data}")
```

## Character Codes

The Vestaboard uses its own character code system. The client automatically converts text to the correct codes.

### Supported Characters

- **Letters**: A-Z (codes 1-26)
- **Numbers**: 0-9 (codes 27-36)
- **Punctuation**: !@#$()&+-=;:'"%.,/?° (codes 37-62)
- **Colors**: 🔴🟠🟡🟢🔵🟣⚪⚫ (codes 63-70)
- **Blank**: Space (code 0)

### Color Chips

- 🔴 Red (code 63)
- 🟠 Orange (code 64)
- 🟡 Yellow (code 65)
- 🟢 Green (code 66)
- 🔵 Blue (code 67)
- 🟣 Violet (code 68)
- ⚪ White (code 69)
- ⚫ Black (code 70)

## Examples

### Weather Display

```python
from vestaboard_api import VestaboardAPI

vesta = VestaboardAPI("your_api_key")

weather_data = {
    "temperature": "72°F",
    "condition": "SUNNY",
    "humidity": "45%",
    "location": "NEW YORK"
}

message = f"WEATHER UPDATE:\n{weather_data['location']}\n{weather_data['temperature']} {weather_data['condition']}\nHUMIDITY: {weather_data['humidity']}"

vesta.send_message(message)
```

### Stock Ticker

```python
from vestaboard_api import VestaboardAPI

vesta = VestaboardAPI("your_api_key")

stocks = [
    ("AAPL", "$150.25", "🔴"),
    ("GOOGL", "$2750.80", "🟢"),
    ("MSFT", "$310.45", "🟢"),
    ("TSLA", "$850.20", "🔴")
]

ticker_lines = ["STOCK TICKER:", ""]
for symbol, price, color in stocks:
    ticker_lines.append(f"{symbol}: {price} {color}")

ticker_message = "\n".join(ticker_lines)
vesta.send_message(ticker_message)
```

### System Notifications

```python
from vestaboard_api import VestaboardAPI
import datetime

vesta = VestaboardAPI("your_api_key")

notifications = [
    "NEW EMAIL RECEIVED! 🔴",
    "SYSTEM BACKUP COMPLETE 🟢",
    "SERVER RESTARTED SUCCESSFULLY 🟢",
    "WARNING: DISK SPACE LOW 🔴"
]

for notification in notifications:
    message = f"NOTIFICATION:\n{notification}\n{datetime.datetime.now().strftime('%H:%M:%S')}"
    vesta.send_message(message)
```

### Clock Display

```python
from vestaboard_api import VestaboardAPI
import datetime
import time

vesta = VestaboardAPI("your_api_key")

while True:
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    message = f"Current Time:\n{current_time}\n{current_date}"
    vesta.send_message(message)
    
    time.sleep(60)  # Update every minute
```

## Setup Instructions

### 1. Enable Local API

1. Request Local API access from Vestaboard
2. Use your enablement token to enable the Local API
3. Save your API key

### 2. Find Your Board's IP

Your board should be accessible at `http://your_board_ip:7000`. Common IPs:
- `http://vestaboard.local:7000`
- `http://192.168.1.100:7000`
- `http://192.168.0.100:7000`

### 3. Test Connection

```python
from vestaboard_api import VestaboardAPI

vesta = VestaboardAPI("your_api_key", "http://your_board_ip:7000")

if vesta.test_connection():
    print("✅ Connection successful!")
    vesta.send_message("Hello from API!")
else:
    print("❌ Connection failed!")
```

## Error Handling

The client includes robust error handling:

```python
from vestaboard_api import VestaboardAPI

vesta = VestaboardAPI("your_api_key")

# Test connection first
if not vesta.test_connection():
    print("Cannot connect to Vestaboard")
    exit(1)

# Send message with error handling
if vesta.send_message("Hello World!"):
    print("Message sent successfully!")
else:
    print("Failed to send message")

# Read board with error handling
content = vesta.read_board()
if content:
    print(f"Board content: {content}")
else:
    print("Failed to read board")
```

## Board Specifications

- **Display**: 6 lines × 22 characters
- **Character Set**: Uppercase letters, numbers, punctuation, and color chips
- **API Endpoint**: `/local-api/message`
- **Protocol**: HTTP REST API
- **Authentication**: API key in header `X-Vestaboard-Local-Api-Key`

## Troubleshooting

### Connection Issues

1. **Check IP Address**: Ensure you're using the correct IP address
2. **Network**: Verify both devices are on the same network
3. **API Key**: Confirm your API key is correct
4. **Local API**: Ensure Local API is enabled

### Message Not Displaying

1. **Character Codes**: The client automatically converts text to proper character codes
2. **Case**: All text is converted to uppercase
3. **Unknown Characters**: Unsupported characters are replaced with blanks

### Performance

- **Rate Limiting**: Avoid sending messages too frequently
- **Timeout**: Default timeout is 10 seconds
- **Connection Pooling**: Uses requests library for efficient connections

## License

This project is open source and available under the MIT License.

## Support

For issues with the Vestaboard Local API itself, refer to the [official documentation](https://docs.vestaboard.com/docs/local-api/authentication). 