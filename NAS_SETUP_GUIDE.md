# Air Overhead - NAS Setup Guide

This guide will help you deploy Air Overhead on your NAS system.

## 🎯 Quick Start

1. **Copy files** to your NAS
2. **Run the deployment script**: `./deploy-to-nas.sh`
3. **Follow the prompts** to customize settings
4. **Done!** Air Overhead will be running

## 📋 Prerequisites

### Required Software
- **Docker** - Container runtime
- **Docker Compose** - Container orchestration

### Required Files
- `credentials.json` - OpenSky API credentials
- `aerodatabox_credentials.json` - AeroDataBox API credentials  
- `vestaboard_config.json` - Vestaboard device configuration

## 🖥️ NAS-Specific Instructions

### Synology NAS
1. **Install Docker**:
   - Open Package Center
   - Search for "Docker"
   - Install Docker package
   - Docker Compose is included

2. **Access via SSH**:
   - Enable SSH in Control Panel → Terminal & SNMP
   - Connect via SSH: `ssh admin@your-nas-ip`
   - Navigate to your air-overhead directory

3. **Run deployment**:
   ```bash
   chmod +x deploy-to-nas.sh
   ./deploy-to-nas.sh
   ```

### QNAP NAS
1. **Install Container Station**:
   - Open App Center
   - Search for "Container Station"
   - Install Container Station
   - Docker and Docker Compose are included

2. **Access via SSH**:
   - Enable SSH in myQNAPcloud → Remote Access
   - Connect via SSH: `ssh admin@your-nas-ip`
   - Navigate to your air-overhead directory

3. **Run deployment**:
   ```bash
   chmod +x deploy-to-nas.sh
   ./deploy-to-nas.sh
   ```

### TrueNAS Core/Scale
1. **Install Docker**:
   - **TrueNAS Scale**: Docker is available via Apps
   - **TrueNAS Core**: Install via CLI or use jails

2. **Access via SSH**:
   - Enable SSH in System Settings → General
   - Connect via SSH: `ssh root@your-nas-ip`
   - Navigate to your air-overhead directory

3. **Run deployment**:
   ```bash
   chmod +x deploy-to-nas.sh
   ./deploy-to-nas.sh
   ```

### Generic Linux NAS
1. **Install Docker**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   sudo usermod -aG docker $USER
   ```

2. **Install Docker Compose**:
   ```bash
   sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
   sudo chmod +x /usr/local/bin/docker-compose
   ```

3. **Run deployment**:
   ```bash
   chmod +x deploy-to-nas.sh
   ./deploy-to-nas.sh
   ```

## 📁 File Structure

Your NAS directory should look like this:
```
/volume1/docker/air-overhead/  # or your preferred location
├── credentials.json
├── aerodatabox_credentials.json
├── vestaboard_config.json
├── docker-compose.yml
├── Dockerfile
├── deploy-to-nas.sh
├── logs/                      # Created automatically
└── ... (other files)
```

## ⚙️ Configuration

### Customizing Settings
The deployment script will ask if you want to customize:
- **Latitude/Longitude** - Your location
- **Detection Radius** - How far to look for aircraft (km)
- **Refresh Interval** - How often to check (seconds)

### Manual Configuration
Edit `docker-compose.yml`:
```yaml
environment:
  - AIR_OVERHEAD_LAT=51.5995      # Your latitude
  - AIR_OVERHEAD_LON=-0.5545      # Your longitude
  - AIR_OVERHEAD_RADIUS=5         # Detection radius in km
  - AIR_OVERHEAD_REFRESH=1        # Refresh interval in seconds
```

## 🚀 Deployment Steps

### Step 1: Prepare Files
1. **Copy the entire air-overhead directory** to your NAS
2. **Add your configuration files**:
   - Copy your existing `credentials.json`
   - Copy your existing `aerodatabox_credentials.json`
   - Copy your existing `vestaboard_config.json`

### Step 2: Run Deployment
```bash
# Make script executable
chmod +x deploy-to-nas.sh

# Run deployment
./deploy-to-nas.sh
```

### Step 3: Follow Prompts
The script will:
- ✅ Check prerequisites
- ✅ Verify configuration files
- ✅ Ask if you want to customize settings
- ✅ Build Docker image
- ✅ Start services
- ✅ Show status

## 🔍 Verification

### Check Services
```bash
# View running containers
docker-compose ps

# Check logs
docker-compose logs -f
```

### Test API
```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Should return: {"status": "healthy", "timestamp": "..."}
```

### Monitor Aircraft Detection
```bash
# Watch for aircraft detection
docker-compose logs -f air-overhead-detector

# Look for lines like: "Found X aircraft"
```

## 🛠️ Management

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Restart Services
```bash
docker-compose restart
```

### Update Settings
```bash
# Stop detector
docker-compose stop air-overhead-detector

# Edit docker-compose.yml with new settings
nano docker-compose.yml

# Restart detector
docker-compose up -d air-overhead-detector
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f air-overhead
docker-compose logs -f air-overhead-detector

# Recent logs only
docker-compose logs --tail=100
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Docker Not Found
```bash
# Check if Docker is installed
docker --version

# If not installed, follow NAS-specific instructions above
```

#### 2. Permission Denied
```bash
# Make script executable
chmod +x deploy-to-nas.sh

# Add user to docker group (if needed)
sudo usermod -aG docker $USER
# Then log out and back in
```

#### 3. Configuration Files Missing
```bash
# Check if files exist
ls -la credentials.json aerodatabox_credentials.json vestaboard_config.json

# If missing, copy from your existing installation
```

#### 4. Port Already in Use
```bash
# Check what's using port 5000
netstat -tulpn | grep :5000

# Change port in docker-compose.yml
ports:
  - "8080:5000"  # Use port 8080 instead
```

#### 5. Services Won't Start
```bash
# Check detailed logs
docker-compose logs

# Check container status
docker-compose ps

# Restart everything
docker-compose down
docker-compose up -d
```

### Getting Help

1. **Check logs**: `docker-compose logs -f`
2. **Verify configuration**: Ensure all JSON files are valid
3. **Test connectivity**: `curl http://localhost:5000/api/health`
4. **Check resources**: Ensure NAS has enough memory/CPU

## 📊 Monitoring

### Resource Usage
```bash
# Check container resource usage
docker stats

# Check disk usage
df -h
```

### Log Monitoring
```bash
# Watch for errors
docker-compose logs | grep ERROR

# Watch for aircraft detection
docker-compose logs air-overhead-detector | grep "Found"
```

### Health Checks
```bash
# Check service health
docker-compose ps

# Test API health
curl http://localhost:5000/api/health
```

## 🔄 Updates

### Update Application
```bash
# Stop services
docker-compose down

# Pull latest code (if using git)
git pull

# Rebuild and start
docker-compose build --no-cache
docker-compose up -d
```

### Backup Configuration
```bash
# Create backup
tar -czf air-overhead-backup-$(date +%Y%m%d).tar.gz \
    credentials.json \
    aerodatabox_credentials.json \
    vestaboard_config.json \
    logs/
```

## 🎉 Success!

Once deployed, Air Overhead will:
- ✅ **Monitor aircraft** in your specified radius
- ✅ **Send Vestaboard notifications** for detected aircraft
- ✅ **Provide API endpoints** for web interface
- ✅ **Auto-restart** if services crash
- ✅ **Log all activity** for monitoring

Your NAS is now running a production-ready aircraft detection system! 