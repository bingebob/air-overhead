#!/bin/bash

# Air Overhead Docker Build Script
# This script builds and optionally pushes the Docker image

set -e

# Configuration
IMAGE_NAME="air-overhead"
TAG=${1:-latest}
REGISTRY=${2:-""}  # Optional registry (e.g., "your-registry.com/")

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Building Air Overhead Docker Image${NC}"
echo "Image: ${REGISTRY}${IMAGE_NAME}:${TAG}"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if required files exist
echo -e "${YELLOW}📋 Checking required files...${NC}"
required_files=("credentials.json" "aerodatabox_credentials.json" "vestaboard_config.json")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo -e "${RED}❌ Missing required configuration files:${NC}"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    echo ""
    echo "Please ensure all configuration files are present before building."
    exit 1
fi

echo -e "${GREEN}✅ All required files found${NC}"

# Build the image
echo -e "${YELLOW}🔨 Building Docker image...${NC}"
docker build -t "${REGISTRY}${IMAGE_NAME}:${TAG}" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Docker image built successfully!${NC}"
else
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
fi

# Show image info
echo ""
echo -e "${YELLOW}📊 Image Information:${NC}"
docker images "${REGISTRY}${IMAGE_NAME}:${TAG}"

# Optional: Push to registry
if [ ! -z "$REGISTRY" ]; then
    echo ""
    read -p "Do you want to push this image to the registry? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}📤 Pushing image to registry...${NC}"
        docker push "${REGISTRY}${IMAGE_NAME}:${TAG}"
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Image pushed successfully!${NC}"
        else
            echo -e "${RED}❌ Failed to push image${NC}"
            exit 1
        fi
    fi
fi

echo ""
echo -e "${GREEN}🎉 Build completed successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Start the services: docker-compose up -d"
echo "2. Check status: docker-compose ps"
echo "3. View logs: docker-compose logs -f"
echo ""
echo -e "${YELLOW}To run with custom settings:${NC}"
echo "1. Copy docker-compose.override.yml.example to docker-compose.override.yml"
echo "2. Modify the override file as needed"
echo "3. Start services: docker-compose up -d" 