# Docker Deployment

This section provides comprehensive Docker deployment instructions for the Property Data Dashboard, from quick setup to production deployment.

## Prerequisites and System Requirements

### Required Software
- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)

### System Resources
**Minimum Requirements:**
- RAM: 4GB allocated to Docker
- CPU: 2 cores
- Disk Space: 10GB free

**Recommended for Production:**
- RAM: 8GB allocated to Docker
- CPU: 4 cores
- Disk Space: 20GB free

**For Large Files (>200MB):**
- RAM: 16GB allocated to Docker
- CPU: 8 cores
- Disk Space: 50GB free

### Docker Installation
- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: [Docker Engine](https://docs.docker.com/engine/install/)
- **Docker Compose**: [Installation Guide](https://docs.docker.com/compose/install/)

### Basic Docker Knowledge
This guide assumes basic familiarity with Docker concepts. If you're new to Docker:
- [Docker Getting Started Guide](https://docs.docker.com/get-started/)
- [Docker Compose Overview](https://docs.docker.com/compose/)

## Quick Start Guide

Get the Property Data Dashboard running in 4 simple steps:

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd Property-Data-Dashboard
```

### 2. Configure Docker Memory
```bash
# Ensure Docker has at least 4GB RAM allocated
# Docker Desktop: Settings > Resources > Advanced > Memory: 4GB+
```

### 3. Start the Application
```bash
docker-compose up --build
```
**Expected Output:**
```
✓ Container property_analyzer_redis  Created
✓ Container property_analyzer_web    Created
✓ Container property_analyzer_web    Started
✓ Container property_analyzer_redis  Started
```

### 4. Access the Dashboard
Open your browser and navigate to: **http://localhost:8080**

**Success Indicators:**
- Dashboard loads without errors
- File upload area is visible
- No error messages in browser console

**Next Steps:**
- Upload a CSV file to test functionality
- For customization, see [Environment Configuration](#environment-configuration)
- For production deployment, see [Production Deployment](#production-deployment)

## Development Deployment

This section provides detailed instructions for setting up the Property Data Dashboard in a development environment with hot reload, debugging capabilities, and development-optimized configurations.

### Development Environment Setup

#### Step 1: Clone and Prepare Repository
```bash
# Clone the repository
git clone <repository-url>
cd Property-Data-Dashboard

# Verify project structure
ls -la
# Expected files: app.py, docker-compose.yml, Dockerfile, requirements.txt
```
**What this does:** Sets up your local development workspace with all necessary project files.

#### Step 2: Create Development Environment Configuration
```bash
# Create development environment file
cat > .env.dev << EOF
# Development-specific settings
DEBUG=true
LOG_LEVEL=DEBUG
SECRET_KEY=dev-secret-key-not-for-production
MAX_FILE_SIZE=1000
SESSION_TIMEOUT=7200
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_ENABLED=false
UPLOAD_TIMEOUT=600

# Development performance settings
CACHE_TIMEOUT=60
MAX_WORKERS=2
WORKER_TIMEOUT=300
CHUNK_SIZE=5000
EOF
```
**What this does:** Creates development-specific configuration that enables debugging, extends timeouts, and disables rate limiting for easier development.

#### Step 3: Create Development Docker Compose Override
```bash
# Create docker-compose.override.yml for development
cat > docker-compose.override.yml << EOF
version: '3.8'
services:
  web:
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - SESSION_TIMEOUT=7200
      - RATE_LIMIT_ENABLED=false
      - MAX_FILE_SIZE=1000
    volumes:
      # Enable hot reload by mounting source code
      - .:/app:rw
      - /app/__pycache__  # Exclude Python cache
    ports:
      - "8080:5000"
      - "5678:5678"  # Debug port for remote debugging
    command: >
      sh -c "pip install debugpy &&
             python -m debugpy --listen 0.0.0.0:5678 --wait-for-client app.py"
    stdin_open: true
    tty: true
    
  redis:
    ports:
      - "6379:6379"  # Expose Redis port for external tools
    command: redis-server --appendonly yes --appendfsync everysec
EOF
```
**What this does:** Overrides the production configuration with development-friendly settings including volume mounting for hot reload and debug port exposure.

#### Step 4: Start Development Environment
```bash
# Start all services in development mode
docker-compose up --build

# Or run in detached mode (background)
docker-compose up --build -d

# View logs in real-time (if running detached)
docker-compose logs -f web
```
**Expected Output:**
```
✓ Container property_analyzer_redis  Created
✓ Container property_analyzer_web    Created
✓ Container property_analyzer_web    Started
✓ Container property_analyzer_redis  Started

web_1    | DEBUG: Starting Property Data Dashboard in DEBUG mode
web_1    | DEBUG: Hot reload enabled - watching for file changes
web_1    | INFO: Redis connection established
web_1    | DEBUG: Application ready on port 5000
```

**What this does:** Launches the application with development configuration, enabling hot reload and debug logging.

### Development-Specific Environment Variables

#### Core Development Variables
| Variable | Development Value | Purpose |
|----------|------------------|---------|
| `DEBUG` | `true` | Enables Flask debug mode with detailed error pages |
| `LOG_LEVEL` | `DEBUG` | Shows all log messages including debug information |
| `SESSION_TIMEOUT` | `7200` (2 hours) | Longer sessions to avoid frequent re-uploads |
| `RATE_LIMIT_ENABLED` | `false` | Disables API rate limiting for testing |
| `MAX_FILE_SIZE` | `1000` (1GB) | Higher limit for testing large files |

#### Development Performance Variables
| Variable | Development Value | Purpose |
|----------|------------------|---------|
| `CACHE_TIMEOUT` | `60` | Shorter cache for seeing changes quickly |
| `UPLOAD_TIMEOUT` | `600` | Extended timeout for large file testing |
| `MAX_WORKERS` | `2` | Fewer workers to reduce resource usage |
| `CHUNK_SIZE` | `5000` | Smaller chunks for better debugging |

#### Setting Environment Variables
```bash
# Method 1: Using .env.dev file (recommended)
docker-compose --env-file .env.dev up --build

# Method 2: Export in shell session
export DEBUG=true
export LOG_LEVEL=DEBUG
docker-compose up --build

# Method 3: Inline with docker-compose
DEBUG=true LOG_LEVEL=DEBUG docker-compose up --build
```

### Volume Mounting for Hot Reload

#### Understanding Volume Mounting
The development setup uses Docker volume mounting to enable hot reload - changes to your code are immediately reflected in the running container without rebuilding.

#### Volume Configuration Explained
```yaml
volumes:
  - .:/app:rw              # Mount current directory to /app with read-write
  - /app/__pycache__       # Exclude Python cache directory
  - /app/node_modules      # Exclude node_modules if present
```

#### Hot Reload Behavior
- **Python Files**: Flask automatically restarts when `.py` files change
- **Templates**: HTML templates update immediately without restart
- **Static Files**: CSS/JS files are served directly from mounted volume
- **Configuration**: Changes to `config.py` trigger application restart

#### Testing Hot Reload
```bash
# 1. Start development environment
docker-compose up --build

# 2. In another terminal, make a change to app.py
echo "# Development change" >> app.py

# 3. Watch the logs - you should see:
# web_1    | DEBUG: Detected file change in app.py
# web_1    | INFO: Restarting application...
# web_1    | DEBUG: Application restarted successfully
```

#### Volume Mounting Troubleshooting
```bash
# Check if volumes are mounted correctly
docker-compose exec web ls -la /app

# Verify file changes are reflected
docker-compose exec web cat /app/app.py | tail -5

# Fix permission issues (Linux/Mac)
sudo chown -R $USER:$USER .
chmod -R 755 .

# Windows: Ensure drive sharing is enabled in Docker Desktop
# Settings > Resources > File Sharing > Add your project drive
```

### Debug Mode Configuration

#### Enabling Debug Mode
Debug mode provides detailed error information and interactive debugging capabilities.

```bash
# Ensure DEBUG=true in your environment
export DEBUG=true

# Start with debug configuration
docker-compose up --build
```

#### Debug Features Available
- **Detailed Error Pages**: Full stack traces with code context
- **Interactive Debugger**: Click on stack trace lines to inspect variables
- **Auto-Reload**: Automatic restart on code changes
- **Template Debugging**: Detailed template error information
- **SQL Query Logging**: Database query logging (if applicable)

#### Remote Debugging Setup
For advanced debugging with IDE integration:

```bash
# 1. Install debugpy in container (already included in override)
# 2. Start with debug port exposed
docker-compose up --build

# 3. Connect your IDE to localhost:5678
# VS Code: Use "Python: Remote Attach" configuration
# PyCharm: Create "Python Debug Server" configuration
```

#### Debug Configuration Example (VS Code)
```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: Remote Attach",
            "type": "python",
            "request": "attach",
            "connect": {
                "host": "localhost",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}",
                    "remoteRoot": "/app"
                }
            ]
        }
    ]
}
```

#### Debugging Best Practices
- **Use Breakpoints**: Set breakpoints in your IDE for step-through debugging
- **Log Strategically**: Use `logger.debug()` for development insights
- **Test Error Handling**: Intentionally trigger errors to test error pages
- **Monitor Performance**: Use debug logs to identify slow operations

### Development Workflow Tips and Best Practices

#### Daily Development Workflow
```bash
# 1. Start your development session
docker-compose up --build -d

# 2. Check service health
curl http://localhost:8080/health

# 3. Monitor logs during development
docker-compose logs -f web

# 4. Make code changes (hot reload handles restart)

# 5. Test your changes
curl -X POST http://localhost:8080/api/upload \
  -F "file=@test-data.csv"

# 6. Stop services when done
docker-compose down
```

#### Code Development Best Practices

##### 1. Use Development Logging
```python
# Add debug logging to your code
import logging
logger = logging.getLogger(__name__)

def process_data(data):
    logger.debug(f"Processing {len(data)} rows")
    # Your code here
    logger.debug("Processing completed successfully")
```

##### 2. Test with Various File Sizes
```bash
# Create test files of different sizes
head -n 100 large-dataset.csv > small-test.csv      # Small file
head -n 10000 large-dataset.csv > medium-test.csv   # Medium file
# Use full file for large file testing
```

##### 3. Database Development (Redis)
```bash
# Connect to Redis for debugging
docker-compose exec redis redis-cli

# Common Redis commands for development
KEYS *                    # List all keys
GET session:abc123        # Get session data
FLUSHALL                  # Clear all data (development only!)
```

##### 4. Performance Monitoring
```bash
# Monitor resource usage during development
docker stats

# Check memory usage of specific container
docker stats property_analyzer_web --no-stream

# Monitor file processing performance
time curl -X POST http://localhost:8080/api/upload \
  -F "file=@test-data.csv"
```

#### Testing and Validation Workflow

##### 1. Automated Testing Setup
```bash
# Run tests in development environment
docker-compose exec web python -m pytest tests/ -v

# Run with coverage
docker-compose exec web python -m pytest tests/ --cov=. --cov-report=html

# Run specific test file
docker-compose exec web python -m pytest tests/test_file_processor.py -v
```

##### 2. Manual Testing Checklist
- [ ] File upload with various CSV formats
- [ ] Large file processing (>100MB)
- [ ] Filter functionality testing
- [ ] Export functionality (CSV/PDF)
- [ ] Session management testing
- [ ] Error handling validation

##### 3. API Testing with curl
```bash
# Test health endpoint
curl http://localhost:8080/health

# Test file upload
curl -X POST http://localhost:8080/api/upload \
  -F "file=@sample.csv" \
  -H "Content-Type: multipart/form-data"

# Test data filtering
curl -X POST http://localhost:8080/api/data \
  -H "Content-Type: application/json" \
  -d '{"session_id": "your-session-id", "filters": {}}'
```

#### Development Environment Maintenance

##### 1. Regular Cleanup
```bash
# Clean up Docker resources weekly
docker system prune -a

# Remove unused volumes
docker volume prune

# Clean up development containers
docker-compose down --volumes --remove-orphans
```

##### 2. Dependency Management
```bash
# Update Python dependencies
docker-compose exec web pip install --upgrade -r requirements.txt

# Add new dependency
echo "new-package==1.0.0" >> requirements.txt
docker-compose up --build

# Check for security vulnerabilities
docker-compose exec web pip-audit
```

##### 3. Configuration Validation
```bash
# Validate environment configuration
docker-compose config

# Check environment variables
docker-compose exec web env | grep -E "(DEBUG|LOG_LEVEL|SESSION_TIMEOUT)"

# Test configuration changes
docker-compose up --build --force-recreate
```

#### Common Development Commands

##### Container Management
```bash
# Restart specific service
docker-compose restart web

# Rebuild single service
docker-compose up --build web

# Access container shell
docker-compose exec web bash

# View container resource usage
docker stats property_analyzer_web
```

##### Log Management
```bash
# View recent logs
docker-compose logs web --tail=50

# Follow logs in real-time
docker-compose logs -f web

# Filter logs by level
docker-compose logs web | grep DEBUG

# Export logs for analysis
docker-compose logs web > development.log
```

##### Development Database Operations
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Backup Redis data
docker-compose exec redis redis-cli BGSAVE

# Monitor Redis operations
docker-compose exec redis redis-cli MONITOR

# Clear development data
docker-compose exec redis redis-cli FLUSHALL
```

#### IDE Integration Tips

##### VS Code Setup
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "files.watcherExclude": {
        "**/__pycache__/**": true,
        "**/node_modules/**": true
    }
}
```

##### PyCharm Setup
- Configure Docker Compose as Python interpreter
- Set up remote debugging configuration
- Enable auto-reload for template files
- Configure code formatting with Black

#### Troubleshooting Development Issues

##### Hot Reload Not Working
```bash
# Check volume mounting
docker-compose exec web ls -la /app

# Verify file permissions
ls -la app.py

# Force container recreation
docker-compose up --build --force-recreate
```

##### Debug Mode Issues
```bash
# Verify DEBUG environment variable
docker-compose exec web env | grep DEBUG

# Check Flask debug mode
docker-compose exec web python -c "from config import config; print(config.DEBUG)"

# Restart with fresh configuration
docker-compose down && docker-compose up --build
```

##### Performance Issues in Development
```bash
# Reduce file size limits
export MAX_FILE_SIZE=100

# Use fewer workers
export MAX_WORKERS=1

# Increase memory allocation
# Docker Desktop: Settings > Resources > Memory: 8GB+
```

## Production Deployment

This section provides comprehensive guidance for deploying the Property Data Dashboard in production environments with security, performance, and reliability optimizations.

### Production Docker Compose Configuration

#### Create Production Docker Compose File
```bash
# Create docker-compose.prod.yml
cat > docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  web:
    build: 
      context: .
      dockerfile: Dockerfile
    container_name: property_analyzer_web_prod
    ports:
      - "80:5000"
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
      - SECRET_KEY=${SECRET_KEY}
      - MAX_FILE_SIZE=${MAX_FILE_SIZE:-500}
      - SESSION_TIMEOUT=${SESSION_TIMEOUT:-3600}
      - REDIS_URL=redis://redis:6379/0
      - RATE_LIMIT_ENABLED=true
      - UPLOAD_TIMEOUT=300
      - MAX_WORKERS=4
      - WORKER_TIMEOUT=120
    depends_on:
      redis:
        condition: service_healthy
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
      restart_policy:
        condition: unless-stopped
        delay: 5s
        max_attempts: 3
        window: 120s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"
    security_opt:
      - no-new-privileges:true
    read_only: false
    tmpfs:
      - /tmp:noexec,nosuid,size=100m

  redis:
    image: redis:7-alpine
    container_name: property_analyzer_redis_prod
    command: >
      redis-server 
      --appendonly yes 
      --appendfsync everysec
      --maxmemory 1gb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
    ports:
      - "127.0.0.1:6379:6379"  # Bind to localhost only
    volumes:
      - redis_data:/data
      - ./redis.conf:/usr/local/etc/redis/redis.conf:ro
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "50m"
        max-file: "3"
    security_opt:
      - no-new-privileges:true

  nginx:
    image: nginx:alpine
    container_name: property_analyzer_nginx_prod
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx.prod.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    depends_on:
      - web
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
        reservations:
          memory: 128M
          cpus: '0.25'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "100m"
        max-file: "5"

volumes:
  redis_data:
    driver: local
  nginx_logs:
    driver: local

networks:
  default:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
EOF
```

#### Create Production Nginx Configuration
```bash
# Create nginx.prod.conf
cat > nginx.prod.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream app {
        server web:5000;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=1r/s;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # SSL Configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    server {
        listen 80;
        server_name _;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        client_max_body_size 1G;
        client_body_timeout 300s;
        client_header_timeout 60s;

        location / {
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 300s;
        }

        location /api/upload {
            limit_req zone=upload burst=5 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_connect_timeout 60s;
            proxy_send_timeout 300s;
            proxy_read_timeout 600s;
        }

        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            proxy_pass http://app;
            access_log off;
        }
    }
}
EOF
```

### Security Considerations and Required Environment Variables

#### Production Environment Configuration
```bash
# Create secure production environment file
cat > .env.prod << 'EOF'
# Security Settings
DEBUG=false
SECRET_KEY=your-64-character-secure-secret-key-generated-with-secrets-module
LOG_LEVEL=INFO

# Application Settings
MAX_FILE_SIZE=500
SESSION_TIMEOUT=3600
UPLOAD_TIMEOUT=300
MAX_WORKERS=4
WORKER_TIMEOUT=120

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security Features
RATE_LIMIT_ENABLED=true
CSRF_ENABLED=true
SECURE_COOKIES=true

# SSL/TLS Settings (if using HTTPS)
SSL_DISABLE=false
FORCE_HTTPS=true

# Monitoring and Logging
SENTRY_DSN=your-sentry-dsn-for-error-tracking
LOG_FORMAT=json
METRICS_ENABLED=true
EOF
```

#### Generate Secure Secrets
```bash
# Generate secure SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))" >> .env.prod

# Generate SSL certificates (self-signed for testing)
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Set secure file permissions
chmod 600 .env.prod
chmod 600 ssl/key.pem
chmod 644 ssl/cert.pem
```

#### Security Hardening Checklist
```bash
# 1. Verify security settings
grep -E "(DEBUG|SECRET_KEY|RATE_LIMIT)" .env.prod

# 2. Check file permissions
ls -la .env.prod ssl/

# 3. Validate SSL configuration
openssl x509 -in ssl/cert.pem -text -noout | grep -A2 "Validity"

# 4. Test security headers
curl -I https://localhost/health

# 5. Verify rate limiting
for i in {1..15}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost/api/health; done
```

#### Required Production Environment Variables

| Variable | Required | Example | Security Impact |
|----------|----------|---------|-----------------|
| `SECRET_KEY` | **Yes** | `64-char-hex-string` | Session security, CSRF protection |
| `DEBUG` | **Yes** | `false` | Prevents information disclosure |
| `LOG_LEVEL` | **Yes** | `INFO` | Reduces log verbosity |
| `RATE_LIMIT_ENABLED` | **Yes** | `true` | Prevents abuse and DoS |
| `REDIS_URL` | **Yes** | `redis://redis:6379/0` | Session persistence |
| `SSL_DISABLE` | No | `false` | Forces HTTPS usage |
| `SECURE_COOKIES` | No | `true` | Cookie security |
| `CSRF_ENABLED` | No | `true` | CSRF attack prevention |

### Resource Limits and Optimization Settings

#### Container Resource Configuration
```yaml
# Optimized resource limits for production
deploy:
  resources:
    # Web Application Container
    web:
      limits:
        memory: 4G        # Maximum memory usage
        cpus: '2.0'       # Maximum CPU cores
      reservations:
        memory: 2G        # Guaranteed memory
        cpus: '1.0'       # Guaranteed CPU cores
    
    # Redis Container
    redis:
      limits:
        memory: 1G        # Redis memory limit
        cpus: '0.5'       # Redis CPU limit
      reservations:
        memory: 512M      # Redis guaranteed memory
        cpus: '0.25'      # Redis guaranteed CPU
    
    # Nginx Container
    nginx:
      limits:
        memory: 256M      # Nginx memory limit
        cpus: '0.5'       # Nginx CPU limit
      reservations:
        memory: 128M      # Nginx guaranteed memory
        cpus: '0.25'      # Nginx guaranteed CPU
```

#### Performance Optimization Settings
```bash
# Create performance optimization configuration
cat > performance.env << 'EOF'
# Application Performance
MAX_WORKERS=4                    # Number of Gunicorn workers
WORKER_TIMEOUT=120              # Worker timeout in seconds
WORKER_CLASS=sync               # Worker class for CPU-bound tasks
WORKER_CONNECTIONS=1000         # Max connections per worker
PRELOAD_APP=true               # Preload application for faster startup

# File Processing Optimization
CHUNK_SIZE=10000               # CSV processing chunk size
MAX_FILE_SIZE=500              # Maximum file size in MB
UPLOAD_TIMEOUT=300             # Upload timeout in seconds
PROCESSING_TIMEOUT=600         # File processing timeout

# Caching Configuration
CACHE_TIMEOUT=300              # Cache timeout in seconds
CACHE_MAX_SIZE=1000            # Maximum cache entries
REDIS_MAX_CONNECTIONS=20       # Redis connection pool size

# Memory Management
MEMORY_LIMIT_SOFT=3G           # Soft memory limit
MEMORY_LIMIT_HARD=4G           # Hard memory limit
GC_THRESHOLD=0.8               # Garbage collection threshold

# Database Optimization
REDIS_MAXMEMORY=1gb            # Redis maximum memory
REDIS_MAXMEMORY_POLICY=allkeys-lru  # Redis eviction policy
REDIS_SAVE_INTERVAL=300        # Redis persistence interval
EOF
```

#### System Resource Requirements

**Minimum Production Requirements:**
- **CPU**: 2 cores (4 recommended)
- **RAM**: 6GB total (8GB recommended)
  - Web container: 2GB
  - Redis container: 512MB
  - Nginx container: 128MB
  - System overhead: 1GB
- **Storage**: 20GB SSD (50GB recommended)
- **Network**: 100Mbps (1Gbps recommended)

**High-Load Production Requirements:**
- **CPU**: 8 cores
- **RAM**: 16GB total
  - Web container: 8GB
  - Redis container: 2GB
  - Nginx container: 256MB
  - System overhead: 2GB
- **Storage**: 100GB SSD
- **Network**: 1Gbps

### Health Checks and Monitoring Setup

#### Application Health Checks
```bash
# Create comprehensive health check script
cat > health-check.sh << 'EOF'
#!/bin/bash

# Health check configuration
HEALTH_URL="http://localhost:5000/health"
TIMEOUT=10
MAX_RETRIES=3

# Function to check service health
check_health() {
    local service=$1
    local url=$2
    local retries=0
    
    while [ $retries -lt $MAX_RETRIES ]; do
        if curl -f -s --max-time $TIMEOUT "$url" > /dev/null; then
            echo "✓ $service is healthy"
            return 0
        else
            echo "✗ $service health check failed (attempt $((retries + 1)))"
            retries=$((retries + 1))
            sleep 2
        fi
    done
    
    echo "✗ $service is unhealthy after $MAX_RETRIES attempts"
    return 1
}

# Check all services
echo "Performing health checks..."
check_health "Web Application" "$HEALTH_URL"
check_health "Redis" "http://localhost:6379"
check_health "Nginx" "http://localhost/health"

# Check resource usage
echo "Resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
EOF

chmod +x health-check.sh
```

#### Monitoring Configuration
```bash
# Create monitoring docker-compose extension
cat > docker-compose.monitoring.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: property_analyzer_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'
    restart: unless-stopped

  grafana:
    image: grafana/grafana:latest
    container_name: property_analyzer_grafana
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=secure_password_here
      - GF_USERS_ALLOW_SIGN_UP=false
    restart: unless-stopped

  node-exporter:
    image: prom/node-exporter:latest
    container_name: property_analyzer_node_exporter
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    restart: unless-stopped

volumes:
  prometheus_data:
  grafana_data:
EOF
```

#### Create Prometheus Configuration
```bash
# Create prometheus.yml
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "alert_rules.yml"

scrape_configs:
  - job_name: 'property-dashboard'
    static_configs:
      - targets: ['web:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093
EOF
```

#### Health Check Integration in Docker Compose
```yaml
# Enhanced health checks in production
healthcheck:
  test: |
    curl -f http://localhost:5000/health &&
    curl -f http://localhost:5000/api/status &&
    python -c "
    import redis, sys
    try:
        r = redis.Redis(host='redis', port=6379, db=0)
        r.ping()
        print('Redis OK')
    except:
        sys.exit(1)
    "
  interval: 30s
  timeout: 15s
  retries: 3
  start_period: 60s
```

### Backup and Persistence Considerations

#### Redis Data Persistence Configuration
```bash
# Create Redis persistence configuration
cat > redis.conf << 'EOF'
# Persistence Configuration
save 900 1      # Save if at least 1 key changed in 900 seconds
save 300 10     # Save if at least 10 keys changed in 300 seconds  
save 60 10000   # Save if at least 10000 keys changed in 60 seconds

# AOF (Append Only File) Configuration
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Memory Management
maxmemory 1gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Security
requirepass your_redis_password_here
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG "CONFIG_b835729c9f154c72"

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log
EOF
```

#### Automated Backup Scripts
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash

# Backup configuration
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Function to backup Redis data
backup_redis() {
    echo "Starting Redis backup..."
    
    # Create Redis backup
    docker-compose exec redis redis-cli BGSAVE
    
    # Wait for backup to complete
    while [ "$(docker-compose exec redis redis-cli LASTSAVE)" = "$(docker-compose exec redis redis-cli LASTSAVE)" ]; do
        sleep 1
    done
    
    # Copy backup file
    docker cp property_analyzer_redis_prod:/data/dump.rdb "$BACKUP_DIR/redis_backup_$DATE.rdb"
    docker cp property_analyzer_redis_prod:/data/appendonly.aof "$BACKUP_DIR/redis_aof_backup_$DATE.aof"
    
    echo "Redis backup completed: redis_backup_$DATE.rdb"
}

# Function to backup application configuration
backup_config() {
    echo "Starting configuration backup..."
    
    # Create configuration backup
    tar -czf "$BACKUP_DIR/config_backup_$DATE.tar.gz" \
        .env.prod \
        docker-compose.prod.yml \
        nginx.prod.conf \
        redis.conf \
        ssl/
    
    echo "Configuration backup completed: config_backup_$DATE.tar.gz"
}

# Function to backup logs
backup_logs() {
    echo "Starting log backup..."
    
    # Create log backup
    docker-compose logs --no-color > "$BACKUP_DIR/application_logs_$DATE.log"
    
    echo "Log backup completed: application_logs_$DATE.log"
}

# Function to cleanup old backups
cleanup_old_backups() {
    echo "Cleaning up backups older than $RETENTION_DAYS days..."
    find "$BACKUP_DIR" -name "*backup*" -type f -mtime +$RETENTION_DAYS -delete
    echo "Cleanup completed"
}

# Main backup process
main() {
    echo "Starting backup process at $(date)"
    
    backup_redis
    backup_config
    backup_logs
    cleanup_old_backups
    
    echo "Backup process completed at $(date)"
    echo "Backup location: $BACKUP_DIR"
    ls -la "$BACKUP_DIR" | tail -10
}

# Run main function
main
EOF

chmod +x backup.sh
```

#### Restore Procedures
```bash
# Create restore script
cat > restore.sh << 'EOF'
#!/bin/bash

# Restore configuration
BACKUP_DIR="/backups"

# Function to restore Redis data
restore_redis() {
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        echo "Error: Backup file $backup_file not found"
        return 1
    fi
    
    echo "Stopping Redis container..."
    docker-compose stop redis
    
    echo "Restoring Redis data from $backup_file..."
    docker cp "$backup_file" property_analyzer_redis_prod:/data/dump.rdb
    
    echo "Starting Redis container..."
    docker-compose start redis
    
    echo "Redis restore completed"
}

# Function to restore configuration
restore_config() {
    local backup_file=$1
    
    if [ ! -f "$backup_file" ]; then
        echo "Error: Configuration backup $backup_file not found"
        return 1
    fi
    
    echo "Restoring configuration from $backup_file..."
    tar -xzf "$backup_file"
    
    echo "Configuration restore completed"
}

# Function to list available backups
list_backups() {
    echo "Available backups:"
    ls -la "$BACKUP_DIR" | grep backup
}

# Usage information
usage() {
    echo "Usage: $0 [redis|config|list] [backup_file]"
    echo "  redis backup_file  - Restore Redis data"
    echo "  config backup_file - Restore configuration"
    echo "  list              - List available backups"
}

# Main restore process
case "$1" in
    redis)
        restore_redis "$2"
        ;;
    config)
        restore_config "$2"
        ;;
    list)
        list_backups
        ;;
    *)
        usage
        ;;
esac
EOF

chmod +x restore.sh
```

#### Persistent Volume Configuration
```yaml
# Enhanced volume configuration for production
volumes:
  redis_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/property-dashboard/redis-data
  
  nginx_logs:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/property-dashboard/nginx-logs
  
  app_uploads:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/property-dashboard/uploads
  
  backups:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /opt/property-dashboard/backups
```

#### Automated Backup Scheduling
```bash
# Create systemd service for automated backups
sudo cat > /etc/systemd/system/property-dashboard-backup.service << 'EOF'
[Unit]
Description=Property Dashboard Backup Service
After=docker.service

[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/property-dashboard
ExecStart=/opt/property-dashboard/backup.sh
StandardOutput=journal
StandardError=journal
EOF

# Create systemd timer for daily backups
sudo cat > /etc/systemd/system/property-dashboard-backup.timer << 'EOF'
[Unit]
Description=Property Dashboard Daily Backup Timer
Requires=property-dashboard-backup.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Enable and start the backup timer
sudo systemctl daemon-reload
sudo systemctl enable property-dashboard-backup.timer
sudo systemctl start property-dashboard-backup.timer

# Check timer status
sudo systemctl status property-dashboard-backup.timer
```

### Production Deployment Commands

#### Complete Production Deployment
```bash
# 1. Prepare production environment
./prepare-production.sh

# 2. Deploy with production configuration
docker-compose -f docker-compose.prod.yml up --build -d

# 3. Verify deployment
./health-check.sh

# 4. Setup monitoring (optional)
docker-compose -f docker-compose.prod.yml -f docker-compose.monitoring.yml up -d

# 5. Configure automated backups
sudo systemctl enable property-dashboard-backup.timer
sudo systemctl start property-dashboard-backup.timer
```

#### Production Maintenance Commands
```bash
# Update application
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up --build -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f --tail=100

# Backup data
./backup.sh

# Monitor resource usage
docker stats

# Scale services (if needed)
docker-compose -f docker-compose.prod.yml up --scale web=2 -d
```

## Environment Configuration

### Complete Environment Variable Reference

| Variable | Default | Development | Production | Description |
|----------|---------|-------------|------------|-------------|
| `DEBUG` | `false` | `true` | `false` | Enable debug mode with detailed errors |
| `LOG_LEVEL` | `INFO` | `DEBUG` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) |
| `SECRET_KEY` | auto-generated | any-value | secure-random | Flask secret key for sessions |
| `MAX_FILE_SIZE` | `500` | `500` | `500` | Maximum file upload size in MB |
| `SESSION_TIMEOUT` | `3600` | `7200` | `3600` | Session timeout in seconds |
| `REDIS_URL` | `None` | `None` | `redis://redis:6379/0` | Redis connection for session storage |
| `RATE_LIMIT_ENABLED` | `true` | `false` | `true` | Enable API rate limiting |

### Configuration Examples

#### Development Configuration
```bash
# .env.dev
DEBUG=true
LOG_LEVEL=DEBUG
SESSION_TIMEOUT=7200
RATE_LIMIT_ENABLED=false
MAX_FILE_SIZE=1000
```

#### Production Configuration
```bash
# .env.prod
DEBUG=false
LOG_LEVEL=INFO
SECRET_KEY=your-32-character-secret-key-here
SESSION_TIMEOUT=3600
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_ENABLED=true
MAX_FILE_SIZE=500
```

#### High-Performance Configuration
```bash
# .env.performance
DEBUG=false
LOG_LEVEL=WARNING
SESSION_TIMEOUT=1800
REDIS_URL=redis://redis:6379/0
RATE_LIMIT_ENABLED=true
MAX_FILE_SIZE=200
```

### Security Best Practices
- **Never commit `.env` files** to version control
- **Use strong, unique SECRET_KEY** in production
- **Rotate secrets regularly** in production environments
- **Limit file sizes** based on your infrastructure capacity
- **Enable rate limiting** to prevent abuse

### Performance Tuning Options
- **Reduce SESSION_TIMEOUT** for better memory management
- **Lower MAX_FILE_SIZE** for faster processing
- **Use Redis** for session storage in production
- **Adjust LOG_LEVEL** to reduce I/O overhead

## Verification and Testing

### Health Check Verification

#### 1. Service Health Check
```bash
# Check application health
curl http://localhost:8080/health

# Expected response
{
  "status": "healthy",
  "timestamp": "2025-01-25T10:00:00Z",
  "version": "2.0.0"
}
```

#### 2. Container Status Check
```bash
# Check all containers are running
docker-compose ps

# Expected output
NAME                     COMMAND                  SERVICE   STATUS    PORTS
property_analyzer_redis  "docker-entrypoint.s…"   redis     Up        0.0.0.0:6379->6379/tcp
property_analyzer_web    "python app.py"          web       Up        0.0.0.0:8080->5000/tcp
```

### Log Verification

#### 1. Application Logs
```bash
# View recent application logs
docker-compose logs web --tail=50

# Expected healthy startup logs
INFO: Starting Property Data Dashboard
INFO: Redis connection established
INFO: Application ready on port 5000
```

#### 2. Error Log Monitoring
```bash
# Monitor for errors in real-time
docker-compose logs -f web | grep ERROR

# No output expected for healthy system
```

### Functionality Testing Checklist

#### Basic Functionality Test
- [ ] Dashboard loads at http://localhost:8080
- [ ] File upload area is visible and responsive
- [ ] No JavaScript errors in browser console
- [ ] Health endpoint returns 200 status

#### File Processing Test
- [ ] Upload a small CSV file (< 10MB)
- [ ] Processing completes without errors
- [ ] Data displays in the dashboard
- [ ] Filters work correctly
- [ ] Export functions work

#### Performance Verification
- [ ] Page loads within 3 seconds
- [ ] File upload processes within reasonable time
- [ ] Memory usage stays within limits
- [ ] No memory leaks during extended use

### Performance Verification Guidelines

#### Memory Usage Check
```bash
# Monitor memory usage
docker stats --no-stream

# Expected ranges
# web container: < 2GB under normal load
# redis container: < 512MB
```

#### Response Time Testing
```bash
# Test response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8080/

# Create curl-format.txt:
#     time_namelookup:  %{time_namelookup}\n
#     time_connect:     %{time_connect}\n
#     time_total:       %{time_total}\n
```

## Troubleshooting

### Common Container Issues

#### Container Won't Start
**Symptoms:**
- `docker-compose up` fails
- Container exits immediately
- Port binding errors

**Solutions:**
```bash
# Check port availability
netstat -tulpn | grep :8080

# Kill process using port
sudo kill -9 $(lsof -t -i:8080)

# Check Docker daemon
sudo systemctl status docker

# Restart Docker service
sudo systemctl restart docker
```

#### Out of Memory Errors
**Symptoms:**
- Container killed unexpectedly
- "Killed" messages in logs
- Slow performance

**Solutions:**
```bash
# Check Docker memory allocation
docker system info | grep Memory

# Increase Docker memory (Docker Desktop)
# Settings > Resources > Advanced > Memory: 8GB+

# Check container memory usage
docker stats

# Reduce file size limits
export MAX_FILE_SIZE=200
```

### Port Binding Problems

#### Port Already in Use
**Symptoms:**
- "Port 8080 already in use" error
- Cannot access dashboard

**Solutions:**
```bash
# Find process using port
sudo lsof -i :8080

# Kill the process
sudo kill -9 <PID>

# Use different port
docker-compose up --build -p 8081:5000
```

#### Network Connectivity Issues
**Symptoms:**
- Cannot access dashboard from browser
- Connection refused errors

**Solutions:**
```bash
# Check container networking
docker network ls
docker network inspect property-data-dashboard_default

# Test internal connectivity
docker-compose exec web curl http://localhost:5000/health

# Check firewall settings
sudo ufw status
```

### Volume Mounting Issues

#### Permission Denied Errors
**Symptoms:**
- Cannot write to mounted volumes
- File permission errors

**Solutions:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Check volume mounts
docker-compose exec web ls -la /app

# Use bind mounts with proper permissions
volumes:
  - .:/app:rw
```

#### File Changes Not Reflected
**Symptoms:**
- Code changes don't trigger restart
- Static files not updating

**Solutions:**
```bash
# Verify volume mounting
docker-compose config

# Force rebuild
docker-compose up --build --force-recreate

# Check file watching
docker-compose exec web ls -la /app
```

### Memory and Resource Problems

#### High Memory Usage
**Symptoms:**
- System becomes slow
- Docker containers killed
- Out of memory errors

**Solutions:**
```bash
# Monitor resource usage
docker stats

# Reduce memory limits
# Edit docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 1G

# Clear Docker cache
docker system prune -a
```

#### CPU Performance Issues
**Symptoms:**
- Slow file processing
- High CPU usage
- Timeouts

**Solutions:**
```bash
# Check CPU usage
top -p $(docker inspect -f '{{.State.Pid}}' property_analyzer_web)

# Limit CPU usage
# Edit docker-compose.yml:
deploy:
  resources:
    limits:
      cpus: '2.0'

# Optimize file processing
export MAX_FILE_SIZE=100
```

### Service Dependency Issues

#### Redis Connection Problems
**Symptoms:**
- Session errors
- "Redis connection failed" in logs

**Solutions:**
```bash
# Check Redis container
docker-compose ps redis

# Test Redis connectivity
docker-compose exec redis redis-cli ping

# Restart Redis service
docker-compose restart redis

# Check Redis logs
docker-compose logs redis
```

#### Service Startup Order
**Symptoms:**
- Web service starts before Redis
- Connection errors during startup

**Solutions:**
```bash
# Use depends_on in docker-compose.yml
services:
  web:
    depends_on:
      - redis

# Add health checks
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Diagnostic Commands

#### Container Inspection
```bash
# Inspect container configuration
docker inspect property_analyzer_web

# Check container logs
docker logs property_analyzer_web

# Access container shell
docker exec -it property_analyzer_web bash
```

#### Network Diagnostics
```bash
# Test internal connectivity
docker-compose exec web curl http://redis:6379

# Check DNS resolution
docker-compose exec web nslookup redis

# Inspect network configuration
docker network inspect $(docker-compose ps -q | head -1 | xargs docker inspect -f '{{range .NetworkSettings.Networks}}{{.NetworkID}}{{end}}')
```

#### Log Analysis Commands
```bash
# Filter error logs
docker-compose logs web | grep -i error

# Monitor logs in real-time
docker-compose logs -f --tail=100

# Export logs for analysis
docker-compose logs web > application.log
```

---

**Need More Help?**
- Check the [DEPLOYMENT.md](DEPLOYMENT.md) for advanced deployment scenarios
- Review the [Configuration](#configuration) section for environment variables
- See the main [README.md](README.md) for application-specific troubleshooting