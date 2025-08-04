@echo off
REM Air Overhead Docker Build Script for Windows
REM This script builds and optionally pushes the Docker image

setlocal enabledelayedexpansion

REM Configuration
set IMAGE_NAME=air-overhead
set TAG=%1
if "%TAG%"=="" set TAG=latest
set REGISTRY=%2
if "%REGISTRY%"=="" set REGISTRY=

echo 🚀 Building Air Overhead Docker Image
echo Image: %REGISTRY%%IMAGE_NAME%:%TAG%
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

REM Check if required files exist
echo 📋 Checking required files...
set missing_files=0

if not exist "credentials.json" (
    echo   - credentials.json
    set missing_files=1
)

if not exist "aerodatabox_credentials.json" (
    echo   - aerodatabox_credentials.json
    set missing_files=1
)

if not exist "vestaboard_config.json" (
    echo   - vestaboard_config.json
    set missing_files=1
)

if %missing_files%==1 (
    echo ❌ Missing required configuration files
    echo.
    echo Please ensure all configuration files are present before building.
    exit /b 1
)

echo ✅ All required files found

REM Build the image
echo 🔨 Building Docker image...
docker build -t "%REGISTRY%%IMAGE_NAME%:%TAG%" .

if errorlevel 1 (
    echo ❌ Docker build failed
    exit /b 1
)

echo ✅ Docker image built successfully!

REM Show image info
echo.
echo 📊 Image Information:
docker images "%REGISTRY%%IMAGE_NAME%:%TAG%"

REM Optional: Push to registry
if not "%REGISTRY%"=="" (
    echo.
    set /p push_choice="Do you want to push this image to the registry? (y/N): "
    if /i "!push_choice!"=="y" (
        echo 📤 Pushing image to registry...
        docker push "%REGISTRY%%IMAGE_NAME%:%TAG%"
        if errorlevel 1 (
            echo ❌ Failed to push image
            exit /b 1
        )
        echo ✅ Image pushed successfully!
    )
)

echo.
echo 🎉 Build completed successfully!
echo.
echo Next steps:
echo 1. Start the services: docker-compose up -d
echo 2. Check status: docker-compose ps
echo 3. View logs: docker-compose logs -f
echo.
echo To run with custom settings:
echo 1. Copy docker-compose.override.yml.example to docker-compose.override.yml
echo 2. Modify the override file as needed
echo 3. Start services: docker-compose up -d 