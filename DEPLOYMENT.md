# Deployment Guide

This guide covers deploying the Property Data Dashboard in various environments.

## 🚀 Quick Start (Development)

```bash
# Clone the repository
git clone <repository-url>
cd Property-Data-Dashboard

# Start with Docker Compose
docker-compose up --build
```

Access at: http://localhost:8080

## 🏭 Production Deployment

### Prerequisites
- Docker and Docker Compose
- At least 4GB RAM (8GB recommended)
- Redis server (optional, for session storage)

### Environment Configuration

Create a `.env` file in the project root:

```bash
# Production settings
DEBUG=false
LOG_LEVEL=INFO

# File processing
MAX_FILE_SIZE=500
SESSION_TIMEOUT=3600

# Security
SECRET_KEY=your-secret-key-here
RATE_LIMIT_ENABLED=true

# Redis (optional)
REDIS_URL=redis://redis:6379/0
```

### Docker Compose Production

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
      - MAX_FILE_SIZE=500
      - SESSION_TIMEOUT=3600
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 256M
```

Deploy with:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Docker-Specific Configuration Examples

#### Development Configuration with Hot Reload
```yaml
# docker-compose.dev.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8080:5000"
      - "5678:5678"  # Debug port
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - SESSION_TIMEOUT=7200
      - RATE_LIMIT_ENABLED=false
      - MAX_FILE_SIZE=1000
      - UPLOAD_TIMEOUT=600
    volumes:
      - .:/app:rw  # Enable hot reload
      - /app/node_modules  # Exclude node_modules
    depends_on:
      - redis
    restart: "no"  # Don't restart in development

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"  # Expose for debugging
    command: redis-server --appendonly yes
```

#### High-Availability Production Configuration
```yaml
# docker-compose.ha.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "8080:5000"
    environment:
      - DEBUG=false
      - LOG_LEVEL=INFO
      - SECRET_KEY=${SECRET_KEY}
      - REDIS_URL=redis://redis:6379/0
      - SECURE_COOKIES=true
      - FORCE_HTTPS=true
      - MAX_WORKERS=8
      - WORKER_TIMEOUT=120
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
        reservations:
          memory: 1G
          cpus: '0.5'
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    depends_on:
      redis:
        condition: service_healthy

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 1gb --maxmemory-policy allkeys-lru
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

#### Container Resource Optimization
```yaml
# Resource-optimized configuration
services:
  web:
    build: .
    environment:
      # Memory optimization
      - MAX_FILE_SIZE=200
      - CHUNK_SIZE=5000
      - MAX_MEMORY_USAGE=1024
      
      # CPU optimization
      - MAX_WORKERS=4
      - WORKER_CLASS=sync
      - WORKER_TIMEOUT=60
      
      # I/O optimization
      - UPLOAD_TIMEOUT=180
      - CACHE_TIMEOUT=600
    deploy:
      resources:
        limits:
          memory: 1.5G
          cpus: '1.5'
        reservations:
          memory: 512M
          cpus: '0.5'
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

## ☁️ Cloud Deployment

### AWS ECS

1. **Build and push image to ECR**:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t property-dashboard .
docker tag property-dashboard:latest <account>.dkr.ecr.us-east-1.amazonaws.com/property-dashboard:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/property-dashboard:latest
```

2. **Create ECS task definition** with:
   - Memory: 2048 MB
   - CPU: 1024 units
   - Environment variables as needed
   - Health check: `/health`

3. **Set up Application Load Balancer** with health check path `/health`

### Google Cloud Run

```bash
# Build and deploy
gcloud builds submit --tag gcr.io/PROJECT-ID/property-dashboard
gcloud run deploy --image gcr.io/PROJECT-ID/property-dashboard --platform managed --port 8080
```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name property-dashboard \
  --image myregistry.azurecr.io/property-dashboard:latest \
  --cpu 2 \
  --memory 4 \
  --ports 8080 \
  --environment-variables DEBUG=false LOG_LEVEL=INFO
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Type | Default | Development | Production | Docker Context | Description |
|----------|------|---------|-------------|------------|----------------|-------------|
| `DEBUG` | Boolean | `false` | `true` | `false` | Container env | Enable Flask debug mode |
| `LOG_LEVEL` | String | `INFO` | `DEBUG` | `INFO` | Container env | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_FILE_SIZE` | Integer | `500` | `1000` | `500` | Container env | Max file size (MB) |
| `SESSION_TIMEOUT` | Integer | `3600` | `7200` | `3600` | Container env | Session timeout (seconds) |
| `SECRET_KEY` | String | auto-generated | `dev-key` | **Required** | Container env | Flask secret key |
| `REDIS_URL` | String | `None` | `redis://redis:6379/0` | `redis://redis:6379/0` | Service link | Redis connection URL |
| `RATE_LIMIT_ENABLED` | Boolean | `true` | `false` | `true` | Container env | Enable rate limiting |
| `UPLOAD_TIMEOUT` | Integer | `300` | `600` | `300` | Container env | File upload timeout (seconds) |
| `MAX_WORKERS` | Integer | `4` | `2` | `4` | Container config | Gunicorn worker processes |
| `WORKER_TIMEOUT` | Integer | `120` | `300` | `120` | Container config | Worker timeout (seconds) |
| `SECURE_COOKIES` | Boolean | `false` | `false` | `true` | Container env | Force secure cookies (HTTPS) |
| `FORCE_HTTPS` | Boolean | `false` | `false` | `true` | Container env | Redirect HTTP to HTTPS |

### Resource Requirements

**Minimum**:
- CPU: 1 core
- Memory: 2GB
- Storage: 10GB

**Recommended**:
- CPU: 2 cores
- Memory: 4GB
- Storage: 20GB

**For large files (>100MB)**:
- CPU: 4 cores
- Memory: 8GB
- Storage: 50GB

## 📊 Monitoring

### Health Checks
- Endpoint: `GET /health`
- Expected response: `200 OK` with JSON status

### Logging
- Application logs to stdout/stderr
- Structured JSON logging in production
- Log levels: DEBUG, INFO, WARNING, ERROR

### Metrics to Monitor
- Response time
- Memory usage
- File upload success rate
- Session count
- Error rate

## 🔒 Security Considerations

### Production Checklist
- [ ] Set `DEBUG=false`
- [ ] Use strong `SECRET_KEY`
- [ ] Enable rate limiting
- [ ] Configure appropriate `MAX_FILE_SIZE`
- [ ] Use HTTPS in production
- [ ] Set up proper firewall rules
- [ ] Regular security updates
- [ ] Monitor for suspicious activity

### Network Security
- Use HTTPS/TLS in production
- Restrict access to necessary ports only
- Consider VPN for internal access
- Implement proper CORS policies

## 🔄 Backup and Recovery

### Session Data
- If using Redis, backup Redis data
- In-memory sessions are lost on restart
- Consider persistent session storage for critical deployments

### Application Data
- No persistent application data stored
- Users upload files per session
- Consider implementing file retention policies

## 🚨 Troubleshooting

### Docker-Specific Issues

**Container Startup Problems**:
```bash
# Check container status
docker-compose ps

# View startup logs
docker-compose logs web --tail=50

# Rebuild without cache
docker-compose build --no-cache

# Reset everything
docker-compose down -v
docker-compose up --build
```

**Port Binding Issues**:
```bash
# Find process using port
lsof -i :8080

# Kill conflicting process
sudo kill -9 <PID>

# Use different port
docker-compose up -p 8081:5000
```

**Service Communication Problems**:
```bash
# Test inter-service connectivity
docker-compose exec web ping redis
docker-compose exec web curl http://redis:6379

# Check service dependencies
docker-compose config | grep depends_on

# Restart services in order
docker-compose down
docker-compose up redis
docker-compose up web
```

### Common Application Issues

**Out of Memory**:
```bash
# Check memory usage
docker stats

# Monitor container memory
docker stats property_analyzer_web

# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G

# Check Docker memory allocation
docker system info | grep Memory
```

**File Upload Fails**:
```bash
# Check file size limits
echo $MAX_FILE_SIZE

# Check disk space
df -h
docker system df

# Check container logs
docker-compose logs web | grep -i upload

# Test upload endpoint
curl -X POST -F "file=@test.csv" http://localhost:8080/api/upload
```

**Redis/Session Issues**:
```bash
# Check Redis connection
docker-compose exec redis redis-cli ping

# Test Redis from web container
docker-compose exec web telnet redis 6379

# Check session timeout
echo $SESSION_TIMEOUT

# View Redis logs
docker-compose logs redis

# Restart Redis
docker-compose restart redis
```

**Performance Issues**:
```bash
# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Check application response times
curl -w "Time: %{time_total}s\n" http://localhost:8080/health

# Optimize worker configuration
# Increase MAX_WORKERS for CPU-bound tasks
# Adjust WORKER_TIMEOUT for long-running requests
```

### Log Analysis and Monitoring
```bash
# View application logs
docker-compose logs web

# Follow logs in real-time
docker-compose logs -f web --tail=100

# Filter error logs
docker-compose logs web | grep -E "(ERROR|CRITICAL)"

# Export logs for analysis
docker-compose logs web > application.log

# Monitor multiple services
docker-compose logs -f web redis

# Search logs for specific patterns
docker-compose logs web | grep "HTTP/1.1"
docker-compose logs web | grep -i "memory"
```

### Health Check and Diagnostics
```bash
# Test application health
curl http://localhost:8080/health

# Check service endpoints
curl -I http://localhost:8080/

# Test file upload functionality
curl -X POST -F "file=@test.csv" http://localhost:8080/api/upload

# Container diagnostics
docker inspect property_analyzer_web
docker-compose exec web ps aux
docker-compose exec web df -h
```

### Emergency Recovery
```bash
# Complete system reset
docker-compose down -v --remove-orphans
docker system prune -a --volumes
docker-compose up --build --force-recreate

# Backup important data before reset
docker cp property_analyzer_web:/app/logs ./backup-logs
```

### Configuration Validation

**Validate Docker Compose Configuration**:
```bash
# Check docker-compose.yml syntax
docker-compose config

# Validate environment variables
docker-compose config --services

# Test configuration with dry run
docker-compose up --dry-run
```

**Environment Variable Validation**:
```bash
# Check required variables are set
docker-compose exec web env | grep -E "(SECRET_KEY|REDIS_URL|DEBUG)"

# Validate secret key length
docker-compose exec web python -c "import os; print('SECRET_KEY length:', len(os.getenv('SECRET_KEY', '')))"

# Test Redis connectivity
docker-compose exec web python -c "
import os, redis
try:
    r = redis.from_url(os.getenv('REDIS_URL', 'redis://redis:6379/0'))
    print('Redis connection:', r.ping())
except Exception as e:
    print('Redis error:', e)
"
```

**Security Configuration Check**:
```bash
# Verify production security settings
if [ "$DEBUG" = "true" ] && [ "$ENVIRONMENT" = "production" ]; then
    echo "ERROR: DEBUG mode enabled in production"
fi

# Check file permissions
ls -la .env* | grep -v "^-rw-------"

# Validate HTTPS configuration
curl -I http://localhost:8080/ | grep -i "strict-transport-security"
```

For comprehensive Docker troubleshooting including detailed diagnostic commands, see the main [README.md Docker Troubleshooting](README.md#docker-troubleshooting) section.

## 📈 Scaling

### Horizontal Scaling
- Deploy multiple instances behind load balancer
- Use Redis for shared session storage
- Consider sticky sessions if needed

### Vertical Scaling
- Increase memory for larger files
- Add CPU cores for concurrent users
- Monitor resource usage and adjust

### Performance Optimization
- Enable Redis caching
- Optimize file upload size limits
- Use CDN for static assets
- Implement connection pooling

---

For additional support or questions, refer to the main README.md or create an issue in the project repository.