# Air Overhead - Docker Version

This is the Docker version of Air Overhead, designed to run on your NAS or any Docker-compatible system.

## Features

- 🐳 **Dockerized**: Easy deployment on NAS systems
- 🔄 **Auto-restart**: Services restart automatically if they crash
- 📊 **Health checks**: Built-in health monitoring
- 📝 **Persistent logs**: Logs are stored outside containers
- 🔧 **Configurable**: Easy to modify settings via mounted config files
- 🚀 **Production ready**: Optimized for 24/7 operation
- ⚙️ **Environment variables**: Easy customization of radius, refresh rate, and location

## Quick Start

### Prerequisites

1. **Docker and Docker Compose** installed on your NAS
2. **Configuration files** ready:
   - `credentials.json` (OpenSky API credentials)
   - `aerodatabox_credentials.json` (AeroDataBox API credentials)
   - `vestaboard_config.json` (Vestaboard configuration)

### Deployment

1. **Clone or copy** this directory to your NAS
2. **Place your config files** in the same directory:
   ```bash
   your-nas/
   ├── air-overhead/
   │   ├── credentials.json
   │   ├── aerodatabox_credentials.json
   │   ├── vestaboard_config.json
   │   ├── docker-compose.yml
   │   └── ... (other files)
   ```

3. **Start the services**:
   ```bash
   cd air-overhead
   docker-compose up -d
   ```

4. **Check status**:
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

## Services

### Main Application (`air-overhead`)
- **Port**: 5000
- **Purpose**: Flask web server with API endpoints
- **Health check**: Automatic monitoring
- **Restart**: Automatic on failure

### Auto-Detection (`air-overhead-detector`)
- **Purpose**: Automated aircraft detection and Vestaboard notifications
- **Dependencies**: Waits for main app to be healthy
- **Restart**: Automatic on failure
- **Configurable**: Radius, refresh rate, and location via environment variables

## Configuration

### Environment Variables

You can customize the behavior by adding environment variables to `docker-compose.yml`:

#### Main Application Variables
```yaml
environment:
  - FLASK_ENV=production
  - PYTHONUNBUFFERED=1
  - FLASK_APP=app.py
```

#### Auto-Detection Variables
```yaml
environment:
  - AIR_OVERHEAD_BASE_URL=http://air-overhead:5000  # Internal service URL
  - AIR_OVERHEAD_LAT=51.5995                        # Your latitude
  - AIR_OVERHEAD_LON=-0.5545                        # Your longitude
  - AIR_OVERHEAD_RADIUS=5                           # Detection radius in km
  - AIR_OVERHEAD_REFRESH=1                          # Refresh interval in seconds
```

#### Variable Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `AIR_OVERHEAD_BASE_URL` | `http://air-overhead:5000` | Internal URL for auto-detection to communicate with main app |
| `AIR_OVERHEAD_LAT` | `51.5995` | Your latitude coordinate |
| `AIR_OVERHEAD_LON` | `-0.5545` | Your longitude coordinate |
| `AIR_OVERHEAD_RADIUS` | `5` | Detection radius in kilometers |
| `AIR_OVERHEAD_REFRESH` | `1` | Refresh interval in seconds |

### Quick Customization

To change settings without editing files, you can use environment variables:

```bash
# Change radius to 10km and refresh to 5 seconds
AIR_OVERHEAD_RADIUS=10 AIR_OVERHEAD_REFRESH=5 docker-compose up -d

# Or modify docker-compose.yml directly
```

### Configuration Files

The following files are mounted from your host system:

| File | Purpose | Required |
|------|---------|----------|
| `credentials.json` | OpenSky API credentials | ✅ Yes |
| `aerodatabox_credentials.json` | AeroDataBox API credentials | ✅ Yes |
| `vestaboard_config.json` | Vestaboard device configuration | ✅ Yes |

### Logs

Logs are stored in the `./logs` directory on your host system:
- Application logs
- Auto-detection logs
- Error logs

## Management Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f air-overhead
docker-compose logs -f air-overhead-detector
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart air-overhead
docker-compose restart air-overhead-detector
```

### Update Application
```bash
# Pull latest changes and rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Check Health
```bash
# Service status
docker-compose ps

# Health check results
docker inspect air-overhead | grep -A 10 "Health"
```

### Update Settings Without Rebuild
```bash
# Stop detector service
docker-compose stop air-overhead-detector

# Update environment variables in docker-compose.yml
# Then restart
docker-compose up -d air-overhead-detector
```

## Monitoring

### Health Checks
- **Main app**: HTTP health check on `/api/health`
- **Auto-detector**: Monitored via container restart policy

### Log Monitoring
```bash
# Real-time logs
docker-compose logs -f --tail=100

# Error logs only
docker-compose logs | grep ERROR

# Auto-detection specific logs
docker-compose logs air-overhead-detector | grep "Found"
```

## Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker-compose logs air-overhead
   
   # Verify config files exist
   ls -la credentials.json aerodatabox_credentials.json vestaboard_config.json
   ```

2. **API not responding**
   ```bash
   # Check if container is running
   docker-compose ps
   
   # Test health endpoint
   curl http://localhost:5000/api/health
   ```

3. **Auto-detection not working**
   ```bash
   # Check detector logs
   docker-compose logs air-overhead-detector
   
   # Verify main app is healthy
   docker-compose ps
   
   # Check environment variables
   docker-compose exec air-overhead-detector env | grep AIR_OVERHEAD
   ```

4. **Wrong detection radius or refresh rate**
   ```bash
   # Check current settings
   docker-compose exec air-overhead-detector env | grep AIR_OVERHEAD
   
   # Update settings and restart
   docker-compose stop air-overhead-detector
   # Edit docker-compose.yml
   docker-compose up -d air-overhead-detector
   ```

### Reset Everything
```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Start fresh
docker-compose up -d
```

## Performance

### Resource Usage
- **Memory**: ~100-200MB per container
- **CPU**: Low usage (mostly idle)
- **Disk**: Minimal (logs only)

### Optimization
- Logs are rotated automatically
- Images are optimized for size
- Health checks prevent resource waste

## Security

- **Non-root user**: Containers run as `appuser`
- **Read-only configs**: Configuration files mounted as read-only
- **Network isolation**: Services communicate via internal network
- **No exposed secrets**: Credentials stored in mounted files

## Backup

### Important Files to Backup
- `credentials.json`
- `aerodatabox_credentials.json`
- `vestaboard_config.json`
- `logs/` directory

### Backup Script Example
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups/air-overhead"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/air-overhead_$DATE.tar.gz" \
    credentials.json \
    aerodatabox_credentials.json \
    vestaboard_config.json \
    logs/
```

## Support

For issues specific to the Docker version:
1. Check the logs: `docker-compose logs`
2. Verify configuration files
3. Test health endpoints
4. Check Docker and Docker Compose versions

## Migration from Local Installation

If you're migrating from a local Python installation:

1. **Copy config files** to the Docker directory
2. **Stop local services** if running
3. **Start Docker services**: `docker-compose up -d`
4. **Verify functionality**: Check logs and health endpoints
5. **Update any external references** to use the new Docker port (5000) 