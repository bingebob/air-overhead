#!/bin/bash
set -e

echo "🚀 Starting Air Overhead in Docker..."

# Check if required configuration files exist
if [ ! -f "/app/credentials.json" ]; then
    echo "❌ Error: credentials.json not found!"
    echo "Please mount your credentials.json file to /app/credentials.json"
    exit 1
fi

if [ ! -f "/app/aerodatabox_credentials.json" ]; then
    echo "❌ Error: aerodatabox_credentials.json not found!"
    echo "Please mount your aerodatabox_credentials.json file to /app/aerodatabox_credentials.json"
    exit 1
fi

if [ ! -f "/app/vestaboard_config.json" ]; then
    echo "❌ Error: vestaboard_config.json not found!"
    echo "Please mount your vestaboard_config.json file to /app/vestaboard_config.json"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p /app/logs

# Set proper permissions
chown -R appuser:appuser /app/logs

echo "✅ Configuration files found"
echo "✅ Logs directory ready"

# Execute the main command
exec "$@" 