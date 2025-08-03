#!/usr/bin/env python3
"""
Vestaboard Local API Client
A clean, reusable client for sending data to Vestaboard displays

Usage:
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
"""

import requests
import json
from typing import List, Dict, Optional, Union

class VestaboardAPI:
    """
    Vestaboard Local API Client
    
    Provides a simple interface for reading from and writing to Vestaboard displays
    using the Local API.
    """
    
    def __init__(self, api_key: str, base_url: str = "http://192.168.1.70:7000"):
        """
        Initialize the Vestaboard API client.
        
        Args:
            api_key (str): Your Vestaboard Local API key
            base_url (str): Base URL of your Vestaboard (default: your board's IP)
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "X-Vestaboard-Local-Api-Key": api_key
        }
        
        # Vestaboard character codes mapping
        self.char_codes = {
            ' ': 0,   # Blank
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9, 'J': 10,
            'K': 11, 'L': 12, 'M': 13, 'N': 14, 'O': 15, 'P': 16, 'Q': 17, 'R': 18, 'S': 19, 'T': 20,
            'U': 21, 'V': 22, 'W': 23, 'X': 24, 'Y': 25, 'Z': 26,
            '1': 27, '2': 28, '3': 29, '4': 30, '5': 31, '6': 32, '7': 33, '8': 34, '9': 35, '0': 36,
            '!': 37, '@': 38, '#': 39, '$': 40, '(': 41, ')': 42, '-': 44, '+': 46, '&': 47, '=': 48,
            ';': 49, ':': 50, "'": 52, '"': 53, '%': 54, ',': 55, '.': 56, '/': 59, '?': 60, '°': 62,
            # Color chips
            '🔴': 63,  # Red
            '🟠': 64,  # Orange  
            '🟡': 65,  # Yellow
            '🟢': 66,  # Green
            '🔵': 67,  # Blue
            '🟣': 68,  # Violet
            '⚪': 69,  # White
            '⚫': 70,  # Black
        }
        
        # Reverse mapping for decoding
        self.code_to_char = {v: k for k, v in self.char_codes.items()}
    
    def _text_to_character_codes(self, text: str, max_lines: int = 6, max_chars: int = 22) -> List[List[int]]:
        """
        Convert text to Vestaboard character codes.
        
        Args:
            text (str): Text to convert
            max_lines (int): Maximum number of lines (default: 6)
            max_chars (int): Maximum characters per line (default: 22)
            
        Returns:
            List[List[int]]: 2D array of character codes
        """
        # Split text into lines
        lines = text.split('\n')
        
        # Limit to max_lines
        lines = lines[:max_lines]
        
        # Convert each line to character codes
        character_lines = []
        for line in lines:
            # Convert string to Vestaboard codes
            codes = []
            for char in line[:max_chars]:
                upper_char = char.upper()
                if upper_char in self.char_codes:
                    codes.append(self.char_codes[upper_char])
                else:
                    codes.append(0)  # Blank for unknown characters
            
            # Pad with zeros to reach max_chars
            while len(codes) < max_chars:
                codes.append(0)
            
            character_lines.append(codes)
        
        # Pad with empty lines to reach max_lines
        while len(character_lines) < max_lines:
            character_lines.append([0] * max_chars)
        
        return character_lines
    
    def _character_codes_to_text(self, character_codes: List[List[int]]) -> str:
        """
        Convert character codes back to text.
        
        Args:
            character_codes (List[List[int]]): 2D array of character codes
            
        Returns:
            str: Converted text
        """
        lines = []
        for line in character_codes:
            text_line = ""
            for code in line:
                if code in self.code_to_char:
                    text_line += self.code_to_char[code]
                else:
                    text_line += " "  # Space for unknown codes
            lines.append(text_line.rstrip())
        
        return '\n'.join(lines)
    
    def send_message(self, text: str) -> bool:
        """
        Send a text message to the Vestaboard.
        
        Args:
            text (str): Text message to display (supports \n for line breaks)
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            vesta.send_message("Hello World!")
            vesta.send_message("Line 1\nLine 2\nLine 3")
            vesta.send_message("Hello 🔴 World 🟢!")
        """
        url = f"{self.base_url}/local-api/message"
        
        # Convert text to character codes
        character_codes = self._text_to_character_codes(text)
        data = {"characters": character_codes}
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                return True
            else:
                print(f"Error sending message: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"Error sending message: {str(e)}")
            return False
    
    def read_board(self) -> Optional[str]:
        """
        Read the current content of the Vestaboard.
        
        Returns:
            Optional[str]: Current board content as text, or None if failed
            
        Example:
            content = vesta.read_board()
            if content:
                print(f"Current board: {content}")
        """
        url = f"{self.base_url}/local-api/message"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if 'message' in result:
                    return self._character_codes_to_text(result['message'])
                else:
                    return None
            else:
                print(f"Error reading board: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error reading board: {str(e)}")
            return None
    
    def get_board_raw(self) -> Optional[Dict]:
        """
        Get the raw board data (character codes).
        
        Returns:
            Optional[Dict]: Raw board data, or None if failed
        """
        url = f"{self.base_url}/local-api/message"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error reading board: HTTP {response.status_code}")
                return None
        except Exception as e:
            print(f"Error reading board: {str(e)}")
            return None
    
    def send_raw_codes(self, character_codes: List[List[int]]) -> bool:
        """
        Send raw character codes to the Vestaboard.
        
        Args:
            character_codes (List[List[int]]): 2D array of character codes
            
        Returns:
            bool: True if successful, False otherwise
            
        Example:
            # Send "HELLO" on line 1
            codes = [[8, 5, 12, 12, 15] + [0] * 17] + [[0] * 22] * 5
            vesta.send_raw_codes(codes)
        """
        url = f"{self.base_url}/local-api/message"
        data = {"characters": character_codes}
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 201:
                return True
            else:
                print(f"Error sending raw codes: HTTP {response.status_code}")
                return False
        except Exception as e:
            print(f"Error sending raw codes: {str(e)}")
            return False
    
    def clear_board(self) -> bool:
        """
        Clear the board (send all blanks).
        
        Returns:
            bool: True if successful, False otherwise
        """
        blank_codes = [[0] * 22 for _ in range(6)]
        return self.send_raw_codes(blank_codes)
    
    def test_connection(self) -> bool:
        """
        Test the connection to the Vestaboard.
        
        Returns:
            bool: True if connection is working, False otherwise
        """
        try:
            content = self.read_board()
            return content is not None
        except:
            return False

# Example usage and testing
if __name__ == "__main__":
    # Your API key
    API_KEY = "MDNlYjJhOTYtMTRkNi00OTdjLTkzMGItZDZhMzEwY2NkMjQ3"
    
    # Initialize the API client
    vesta = VestaboardAPI(API_KEY)
    
    print("🧪 Testing Vestaboard API Client")
    print("=" * 50)
    
    # Test connection
    if vesta.test_connection():
        print("✅ Connection successful!")
        
        # Read current board
        current = vesta.read_board()
        print(f"📖 Current board content:\n{current}")
        
        # Send a test message
        test_message = "Hello from API Client!\nThis is a test message\nWith multiple lines"
        if vesta.send_message(test_message):
            print("✅ Test message sent successfully!")
            
            # Read board again to confirm
            import time
            time.sleep(2)
            updated = vesta.read_board()
            print(f"📖 Updated board content:\n{updated}")
        else:
            print("❌ Failed to send test message")
    else:
        print("❌ Connection failed!") 