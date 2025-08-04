#!/bin/bash

# Air Overhead NAS Deployment Script
# This script helps you deploy Air Overhead to your NAS

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Air Overhead NAS Deployment Helper${NC}"
echo "=========================================="
echo ""

# Check if Docker is available
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    echo "Please install Docker on your NAS first."
    echo "Common NAS Docker installations:"
    echo "  - Synology: Install Docker package from Package Center"
    echo "  - QNAP: Install Container Station from App Center"
    echo "  - TrueNAS: Install Docker via Apps or CLI"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed or not in PATH${NC}"
    echo "Please install Docker Compose on your NAS."
    exit 1
fi

echo -e "${GREEN}✅ Docker and Docker Compose found${NC}"

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ docker-compose.yml not found${NC}"
    echo "Please run this script from the air-overhead directory."
    exit 1
fi

# Check configuration files
echo -e "${YELLOW}📋 Checking configuration files...${NC}"
missing_files=()

if [ ! -f "credentials.json" ]; then
    missing_files+=("credentials.json")
fi

if [ ! -f "aerodatabox_credentials.json" ]; then
    missing_files+=("aerodatabox_credentials.json")
fi

if [ ! -f "vestaboard_config.json" ]; then
    missing_files+=("vestaboard_config.json")
fi

if [ ${#missing_files[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing configuration files:${NC}"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo -e "${YELLOW}📝 Please create these files before continuing:${NC}"
    echo ""
    echo "1. Copy your existing configuration files to this directory, or"
    echo "2. Create new ones based on the examples:"
    echo "   - credentials.json.example"
    echo "   - vestaboard_config.json.example"
    echo ""
    echo "Once you have the configuration files, run this script again."
    exit 1
fi

echo -e "${GREEN}✅ All configuration files found${NC}"

# Create logs directory
echo -e "${YELLOW}📁 Creating logs directory...${NC}"
mkdir -p logs
echo -e "${GREEN}✅ Logs directory ready${NC}"

# Show current settings
echo -e "${YELLOW}⚙️  Current Configuration:${NC}"
echo "Location: $(grep AIR_OVERHEAD_LAT docker-compose.yml | cut -d'=' -f2), $(grep AIR_OVERHEAD_LON docker-compose.yml | cut -d'=' -f2)"
echo "Radius: $(grep AIR_OVERHEAD_RADIUS docker-compose.yml | cut -d'=' -f2) km"
echo "Refresh: $(grep AIR_OVERHEAD_REFRESH docker-compose.yml | cut -d'=' -f2) seconds"
echo ""

# Ask if user wants to customize settings
read -p "Do you want to customize the detection settings? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🔧 Customization Options:${NC}"
    echo ""
    
    # Get current values
    current_lat=$(grep AIR_OVERHEAD_LAT docker-compose.yml | cut -d'=' -f2)
    current_lon=$(grep AIR_OVERHEAD_LON docker-compose.yml | cut -d'=' -f2)
    current_radius=$(grep AIR_OVERHEAD_RADIUS docker-compose.yml | cut -d'=' -f2)
    current_refresh=$(grep AIR_OVERHEAD_REFRESH docker-compose.yml | cut -d'=' -f2)
    
    read -p "Latitude [$current_lat]: " new_lat
    read -p "Longitude [$current_lon]: " new_lon
    read -p "Detection radius in km [$current_radius]: " new_radius
    read -p "Refresh interval in seconds [$current_refresh]: " new_refresh
    
    # Use defaults if empty
    new_lat=${new_lat:-$current_lat}
    new_lon=${new_lon:-$current_lon}
    new_radius=${new_radius:-$current_radius}
    new_refresh=${new_refresh:-$current_refresh}
    
    # Update docker-compose.yml
    sed -i "s/AIR_OVERHEAD_LAT=$current_lat/AIR_OVERHEAD_LAT=$new_lat/g" docker-compose.yml
    sed -i "s/AIR_OVERHEAD_LON=$current_lon/AIR_OVERHEAD_LON=$new_lon/g" docker-compose.yml
    sed -i "s/AIR_OVERHEAD_RADIUS=$current_radius/AIR_OVERHEAD_RADIUS=$new_radius/g" docker-compose.yml
    sed -i "s/AIR_OVERHEAD_REFRESH=$current_refresh/AIR_OVERHEAD_REFRESH=$new_refresh/g" docker-compose.yml
    
    echo -e "${GREEN}✅ Settings updated${NC}"
    echo "New settings:"
    echo "Location: $new_lat, $new_lon"
    echo "Radius: $new_radius km"
    echo "Refresh: $new_refresh seconds"
    echo ""
fi

# Build and start
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker-compose build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

echo -e "${YELLOW}🚀 Starting services...${NC}"
docker-compose up -d

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Services started successfully${NC}"
else
    echo -e "${RED}❌ Failed to start services${NC}"
    exit 1
fi

# Wait a moment for services to start
echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
sleep 10

# Check status
echo -e "${YELLOW}📊 Checking service status...${NC}"
docker-compose ps

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. Check logs: docker-compose logs -f"
echo "2. Test API: curl http://localhost:5000/api/health"
echo "3. Monitor aircraft: docker-compose logs air-overhead-detector"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo "Stop services: docker-compose down"
echo "Restart services: docker-compose restart"
echo "Update settings: Edit docker-compose.yml, then docker-compose up -d air-overhead-detector"
echo ""
echo -e "${BLUE}📝 Logs Location:${NC}"
echo "Application logs: ./logs/"
echo "Docker logs: docker-compose logs -f"
echo ""
echo -e "${GREEN}✅ Air Overhead is now running on your NAS!${NC}" 