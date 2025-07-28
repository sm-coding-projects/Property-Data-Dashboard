# Environment Configuration Guide

This comprehensive guide covers all environment variables, configuration examples for different deployment scenarios, security best practices, performance tuning options, and validation steps for the Property Data Dashboard.

## Complete Environment Variable Reference

### Core Application Settings

| Variable | Type | Default | Development | Production | Description |
|----------|------|---------|-------------|------------|-------------|
| `DEBUG` | Boolean | `false` | `true` | `false` | Enable Flask debug mode with detailed error pages |
| `SECRET_KEY` | String | Auto-generated | `dev-key-only` | **Required** | Flask secret key for session security and CSRF protection |
| `LOG_LEVEL` | String | `INFO` | `DEBUG` | `INFO` | Logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FILE` | String | `None` | `None` | `/var/log/app.log` | Log file path (None for console output) |
| `LOG_FORMAT` | String | Standard | Standard | JSON | Log message format |

### File Processing Configuration

| Variable | Type | Default | Development | Production | Description |
|----------|------|---------|-------------|------------|-------------|
| `MAX_FILE_SIZE` | Integer | `500` | `1000` | `500` | Maximum file upload size in MB |
| `UPLOAD_TIMEOUT` | Integer | `300` | `600` | `300` | File upload timeout in seconds |
| `CHUNK_SIZE` | Integer | `10000` | `5000` | `10000` | CSV processing chunk size in rows |
| `MAX_MEMORY_USAGE` | Integer | `1024` | `2048` | `1024` | Maximum memory usage in MB |
| `ALLOWED_EXTENSIONS` | List | `csv` | `csv` | `csv` | Allowed file extensions (configured in code) |

### Session and Storage Settings

| Variable | Type | Default | Development | Production | Description |
|----------|------|---------|-------------|------------|-------------|
| `SESSION_TIMEOUT` | Integer | `3600` | `7200` | `3600` | Session timeout in seconds |
| `REDIS_URL` | String | `None` | `redis://redis:6379/0` | `redis://redis:6379/0` | Redis connection URL for session storage |
| `CACHE_TIMEOUT` | Integer | `300` | `60` | `300` | Cache timeout in seconds |
| `USE_REDIS` | Boolean | Auto-detected | `true` | `true` | Enable Redis for session storage |

### Performance and Scaling Settings

| Variable | Type | Default | Development | Production | Description |
|----------|------|---------|-------------|------------|-------------|
| `MAX_WORKERS` | Integer | `4` | `2` | `4` | Number of Gunicorn worker processes |
| `WORKER_TIMEOUT` | Integer | `600` | `300` | `120` | Worker timeout in seconds |
| `WORKER_CLASS` | String | `sync` | `sync` | `sync` | Gunicorn worker class |
| `WORKER_CONNECTIONS` | Integer | `1000` | `100` | `1000` | Maximum connections per worker |
| `PRELOAD_APP` | Boolean | `false` | `false` | `true` | Preload application for faster startup |

### Security Configuration

| Variable | Type | Default | Development | Production | Description |
|----------|------|---------|-------------|------------|-------------|
| `RATE_LIMIT_ENABLED` | Boolean | `true` | `false` | `true` | Enable API rate limiting |
| `RATE_LIMIT_REQUESTS` | Integer | `100` | `1000` | `100` | Rate limit requests per window |
| `RATE_LIMIT_WINDOW` | Integer | `3600` | `3600` | `3600` | Rate limit window in seconds |
| `CSRF_ENABLED` | Boolean | `true` | `false` | `true` | Enable CSRF protection |
| `SECURE_COOKIES` | Boolean | `false` | `false` | `true` | Force secure cookies (HTTPS only) |
| `FORCE_HTTPS` | Boolean | `false` | `false` | `true` | Redirect HTTP to HTTPS |

### Monitoring and Observability

| Variable | Type | Default | Development | Production | Description |
|----------|------|---------|-------------|------------|-------------|
| `METRICS_ENABLED` | Boolean | `false` | `false` | `true` | Enable application metrics collection |
| `HEALTH_CHECK_ENABLED` | Boolean | `true` | `true` | `true` | Enable health check endpoint |
| `SENTRY_DSN` | String | `None` | `None` | **Recommended** | Sentry DSN for error tracking |
| `PROMETHEUS_METRICS` | Boolean | `false` | `false` | `true` | Enable Prometheus metrics endpoint |

## Configuration Examples for Different Deployment Scenarios

### Development Environment Configuration

#### Option 1: Environment File (.env.dev)
```bash
# Development Environment Configuration
# File: .env.dev

# Core Settings
DEBUG=true
SECRET_KEY=dev-secret-key-change-for-production
LOG_LEVEL=DEBUG
LOG_FILE=

# File Processing - Relaxed limits for testing
MAX_FILE_SIZE=1000
UPLOAD_TIMEOUT=600
CHUNK_SIZE=5000
MAX_MEMORY_USAGE=2048

# Session Management - Extended for development
SESSION_TIMEOUT=7200
REDIS_URL=redis://redis:6379/0
CACHE_TIMEOUT=60

# Performance - Reduced for development
MAX_WORKERS=2
WORKER_TIMEOUT=300
WORKER_CLASS=sync
PRELOAD_APP=false

# Security - Relaxed for development
RATE_LIMIT_ENABLED=false
CSRF_ENABLED=false
SECURE_COOKIES=false
FORCE_HTTPS=false

# Monitoring - Basic for development
METRICS_ENABLED=false
HEALTH_CHECK_ENABLED=true
SENTRY_DSN=
```

#### Option 2: Docker Compose Environment
```yaml
# docker-compose.override.yml
version: '3.8'
services:
  web:
    environment:
      # Development overrides
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - SESSION_TIMEOUT=7200
      - RATE_LIMIT_ENABLED=false
      - MAX_FILE_SIZE=1000
      - UPLOAD_TIMEOUT=600
      - MAX_WORKERS=2
      - WORKER_TIMEOUT=300
      - CACHE_TIMEOUT=60
    volumes:
      - .:/app:rw  # Enable hot reload
    ports:
      - "8080:5000"
      - "5678:5678"  # Debug port
```

#### Option 3: Shell Export
```bash
#!/bin/bash
# Development environment setup script
# File: setup-dev.sh

export DEBUG=true
export LOG_LEVEL=DEBUG
export SECRET_KEY=dev-secret-key-only
export MAX_FILE_SIZE=1000
export SESSION_TIMEOUT=7200
export REDIS_URL=redis://localhost:6379/0
export RATE_LIMIT_ENABLED=false
export UPLOAD_TIMEOUT=600
export MAX_WORKERS=2
export WORKER_TIMEOUT=300

echo "Development environment configured"
echo "Run: docker-compose up --build"
```

### Production Environment Configuration

#### Secure Production Configuration
```bash
# Production Environment Configuration
# File: .env.prod

# Core Settings - Production Hardened
DEBUG=false
SECRET_KEY=your-64-character-secure-secret-key-here
LOG_LEVEL=INFO
LOG_FILE=/var/log/property-dashboard/app.log
LOG_FORMAT=json

# File Processing - Production Limits
MAX_FILE_SIZE=500
UPLOAD_TIMEOUT=300
CHUNK_SIZE=10000
MAX_MEMORY_USAGE=1024

# Session Management - Production Optimized
SESSION_TIMEOUT=3600
REDIS_URL=redis://redis:6379/0
CACHE_TIMEOUT=300

# Performance - Production Scaling
MAX_WORKERS=4
WORKER_TIMEOUT=120
WORKER_CLASS=sync
WORKER_CONNECTIONS=1000
PRELOAD_APP=true

# Security - Full Protection
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600
CSRF_ENABLED=true
SECURE_COOKIES=true
FORCE_HTTPS=true

# Monitoring - Full Observability
METRICS_ENABLED=true
HEALTH_CHECK_ENABLED=true
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
PROMETHEUS_METRICS=true
```

#### High-Performance Production Configuration
```bash
# High-Performance Production Configuration
# File: .env.prod.high-performance

# Core Settings
DEBUG=false
SECRET_KEY=your-secure-secret-key
LOG_LEVEL=WARNING
LOG_FILE=/var/log/property-dashboard/app.log

# File Processing - High Performance
MAX_FILE_SIZE=1000
UPLOAD_TIMEOUT=600
CHUNK_SIZE=20000
MAX_MEMORY_USAGE=4096

# Session Management - Optimized
SESSION_TIMEOUT=1800
REDIS_URL=redis://redis:6379/0
CACHE_TIMEOUT=600

# Performance - High Throughput
MAX_WORKERS=8
WORKER_TIMEOUT=180
WORKER_CLASS=gevent
WORKER_CONNECTIONS=2000
PRELOAD_APP=true

# Security - Balanced
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS=200
RATE_LIMIT_WINDOW=3600

# Monitoring - Performance Focused
METRICS_ENABLED=true
PROMETHEUS_METRICS=true
```

### Cloud Deployment Configurations

#### AWS ECS Configuration
```bash
# AWS ECS Environment Configuration
# File: .env.aws

# Core Settings
DEBUG=false
SECRET_KEY=${AWS_SECRET_KEY}
LOG_LEVEL=INFO
LOG_FORMAT=json

# File Processing - Cloud Optimized
MAX_FILE_SIZE=500
UPLOAD_TIMEOUT=300
CHUNK_SIZE=15000
MAX_MEMORY_USAGE=2048

# Session Management - ElastiCache
SESSION_TIMEOUT=3600
REDIS_URL=${ELASTICACHE_REDIS_URL}
CACHE_TIMEOUT=300

# Performance - ECS Optimized
MAX_WORKERS=4
WORKER_TIMEOUT=120
PRELOAD_APP=true

# Security - AWS Security Groups + App Level
RATE_LIMIT_ENABLED=true
SECURE_COOKIES=true
FORCE_HTTPS=true

# Monitoring - CloudWatch Integration
METRICS_ENABLED=true
SENTRY_DSN=${SENTRY_DSN}
```

#### Kubernetes Configuration
```yaml
# Kubernetes ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: property-dashboard-config
data:
  DEBUG: "false"
  LOG_LEVEL: "INFO"
  LOG_FORMAT: "json"
  MAX_FILE_SIZE: "500"
  UPLOAD_TIMEOUT: "300"
  SESSION_TIMEOUT: "3600"
  MAX_WORKERS: "4"
  WORKER_TIMEOUT: "120"
  RATE_LIMIT_ENABLED: "true"
  SECURE_COOKIES: "true"
  FORCE_HTTPS: "true"
  METRICS_ENABLED: "true"
  HEALTH_CHECK_ENABLED: "true"
```

### Testing Environment Configuration

#### Automated Testing Configuration
```bash
# Testing Environment Configuration
# File: .env.test

# Core Settings - Testing Optimized
DEBUG=false
SECRET_KEY=test-secret-key-not-secure
LOG_LEVEL=WARNING
LOG_FILE=

# File Processing - Fast Testing
MAX_FILE_SIZE=100
UPLOAD_TIMEOUT=60
CHUNK_SIZE=1000
MAX_MEMORY_USAGE=512

# Session Management - In-Memory
SESSION_TIMEOUT=300
REDIS_URL=
CACHE_TIMEOUT=10

# Performance - Minimal Resources
MAX_WORKERS=1
WORKER_TIMEOUT=30
PRELOAD_APP=false

# Security - Disabled for Testing
RATE_LIMIT_ENABLED=false
CSRF_ENABLED=false
SECURE_COOKIES=false

# Monitoring - Minimal
METRICS_ENABLED=false
HEALTH_CHECK_ENABLED=true
```

## Security Best Practices for Production Variables

### Secret Key Management

#### Generating Secure Secret Keys
```bash
# Method 1: Using Python secrets module (Recommended)
python3 -c "import secrets; print(secrets.token_hex(32))"

# Method 2: Using OpenSSL
openssl rand -hex 32

# Method 3: Using /dev/urandom (Linux/Mac)
head -c 32 /dev/urandom | base64

# Method 4: Using UUID (Less secure, not recommended)
python3 -c "import uuid; print(str(uuid.uuid4()).replace('-', ''))"
```

#### Secret Key Storage Best Practices
```bash
# 1. Environment Variables (Recommended)
export SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 2. Secure File with Restricted Permissions
echo "SECRET_KEY=$(openssl rand -hex 32)" > /etc/property-dashboard/secrets
chmod 600 /etc/property-dashboard/secrets
chown app:app /etc/property-dashboard/secrets

# 3. Docker Secrets (Docker Swarm)
echo "your-secret-key" | docker secret create property_dashboard_secret -

# 4. Kubernetes Secrets
kubectl create secret generic property-dashboard-secret \
  --from-literal=SECRET_KEY=$(openssl rand -hex 32)
```

### Environment Variable Security

#### Secure Environment File Management
```bash
# Create secure environment file
cat > .env.prod << 'EOF'
# Production secrets - Keep secure!
SECRET_KEY=your-64-character-secure-secret-key
REDIS_URL=redis://username:password@redis:6379/0
SENTRY_DSN=https://key@sentry.io/project
EOF

# Set secure permissions
chmod 600 .env.prod
chown app:app .env.prod

# Verify permissions
ls -la .env.prod
# Should show: -rw------- 1 app app
```

#### Environment Variable Validation
```bash
# Create environment validation script
cat > validate-env.sh << 'EOF'
#!/bin/bash

# Required production variables
REQUIRED_VARS=(
    "SECRET_KEY"
    "REDIS_URL"
    "LOG_LEVEL"
)

# Security validation
validate_secret_key() {
    if [ ${#SECRET_KEY} -lt 32 ]; then
        echo "ERROR: SECRET_KEY must be at least 32 characters"
        exit 1
    fi
    
    if [[ "$SECRET_KEY" == *"dev"* ]] || [[ "$SECRET_KEY" == *"test"* ]]; then
        echo "ERROR: SECRET_KEY appears to be a development key"
        exit 1
    fi
}

validate_debug_mode() {
    if [ "$DEBUG" = "true" ] && [ "$ENVIRONMENT" = "production" ]; then
        echo "ERROR: DEBUG mode cannot be enabled in production"
        exit 1
    fi
}

# Run validations
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "ERROR: Required variable $var is not set"
        exit 1
    fi
done

validate_secret_key
validate_debug_mode

echo "✓ Environment validation passed"
EOF

chmod +x validate-env.sh
```

### Redis Security Configuration

#### Secure Redis Connection
```bash
# Redis with authentication
REDIS_URL=redis://username:strong-password@redis:6379/0

# Redis with SSL/TLS
REDIS_URL=rediss://username:password@redis:6380/0

# Redis Sentinel configuration
REDIS_URL=redis+sentinel://sentinel1:26379,sentinel2:26379/mymaster

# Redis Cluster configuration
REDIS_URL=redis://node1:7000,node2:7000,node3:7000/0
```

#### Redis Security Best Practices
```bash
# Create Redis configuration with security
cat > redis-security.conf << 'EOF'
# Authentication
requirepass your-strong-redis-password
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""

# Network security
bind 127.0.0.1
port 0
unixsocket /var/run/redis/redis.sock
unixsocketperm 700

# SSL/TLS
tls-port 6380
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt

# Memory and performance
maxmemory 1gb
maxmemory-policy allkeys-lru
EOF
```

### HTTPS and SSL Configuration

#### SSL Certificate Management
```bash
# Generate self-signed certificate (development only)
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# Let's Encrypt certificate (production)
certbot certonly --webroot -w /var/www/html -d yourdomain.com

# Certificate validation
openssl x509 -in cert.pem -text -noout | grep -A2 "Validity"
```

#### HTTPS Environment Configuration
```bash
# HTTPS-enabled environment
SSL_DISABLE=false
FORCE_HTTPS=true
SECURE_COOKIES=true
SSL_CERT_PATH=/etc/ssl/certs/cert.pem
SSL_KEY_PATH=/etc/ssl/private/key.pem
```

## Performance Tuning Options and Recommendations

### Memory Optimization

#### Memory Configuration Guidelines
```bash
# Small deployment (< 100MB files)
MAX_MEMORY_USAGE=512
CHUNK_SIZE=5000
MAX_WORKERS=2

# Medium deployment (100-500MB files)
MAX_MEMORY_USAGE=1024
CHUNK_SIZE=10000
MAX_WORKERS=4

# Large deployment (> 500MB files)
MAX_MEMORY_USAGE=4096
CHUNK_SIZE=20000
MAX_WORKERS=8
```

#### Memory Monitoring Configuration
```bash
# Enable memory monitoring
MEMORY_MONITORING=true
MEMORY_ALERT_THRESHOLD=0.8
MEMORY_CLEANUP_THRESHOLD=0.9

# Garbage collection tuning
GC_THRESHOLD_0=700
GC_THRESHOLD_1=10
GC_THRESHOLD_2=10
```

### CPU and Worker Optimization

#### Worker Configuration by CPU Cores
```bash
# Calculate optimal workers
CPU_CORES=$(nproc)
OPTIMAL_WORKERS=$((CPU_CORES * 2 + 1))

# Conservative approach (recommended)
MAX_WORKERS=$((CPU_CORES))

# High-throughput approach
MAX_WORKERS=$((CPU_CORES * 2))

# Memory-constrained approach
MAX_WORKERS=$((CPU_CORES / 2))
```

#### Worker Class Selection
```bash
# CPU-bound tasks (file processing)
WORKER_CLASS=sync
MAX_WORKERS=4

# I/O-bound tasks (many concurrent users)
WORKER_CLASS=gevent
WORKER_CONNECTIONS=1000

# Mixed workload
WORKER_CLASS=gthread
THREADS=2
MAX_WORKERS=4
```

### Caching Optimization

#### Cache Configuration Strategies
```bash
# Aggressive caching (high-read workload)
CACHE_TIMEOUT=3600
CACHE_MAX_SIZE=10000
REDIS_MAXMEMORY=2gb
REDIS_MAXMEMORY_POLICY=allkeys-lru

# Conservative caching (frequently changing data)
CACHE_TIMEOUT=300
CACHE_MAX_SIZE=1000
REDIS_MAXMEMORY=512mb
REDIS_MAXMEMORY_POLICY=volatile-lru

# No caching (development/testing)
CACHE_TIMEOUT=0
REDIS_URL=
```

#### Redis Performance Tuning
```bash
# Redis performance configuration
cat > redis-performance.conf << 'EOF'
# Memory optimization
maxmemory 2gb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Persistence optimization
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec

# Network optimization
tcp-keepalive 300
timeout 0

# Performance tuning
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-size -2
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
EOF
```

### Database and Storage Optimization

#### File Processing Optimization
```bash
# Large file optimization
CHUNK_SIZE=50000
PARALLEL_PROCESSING=true
MEMORY_MAPPED_FILES=true
COMPRESSION_ENABLED=true

# Small file optimization
CHUNK_SIZE=1000
BATCH_PROCESSING=false
IN_MEMORY_PROCESSING=true

# Balanced optimization
CHUNK_SIZE=10000
ADAPTIVE_CHUNKING=true
MEMORY_THRESHOLD=0.8
```

#### Storage Performance Configuration
```bash
# SSD optimization
STORAGE_TYPE=ssd
READ_AHEAD=256
WRITE_CACHE=true

# Network storage optimization
STORAGE_TYPE=network
BUFFER_SIZE=65536
CONNECTION_POOL_SIZE=10

# Local storage optimization
STORAGE_TYPE=local
DIRECT_IO=true
SYNC_WRITES=false
```

## Validation Steps for Configuration Verification

### Environment Validation Scripts

#### Comprehensive Environment Validator
```bash
#!/bin/bash
# File: validate-environment.sh

set -e

echo "🔍 Property Data Dashboard - Environment Validation"
echo "=================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Validation functions
validate_required_vars() {
    echo "📋 Checking required environment variables..."
    
    local required_vars=(
        "SECRET_KEY"
        "LOG_LEVEL"
        "MAX_FILE_SIZE"
        "SESSION_TIMEOUT"
    )
    
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        else
            echo -e "  ✓ $var: ${GREEN}Set${NC}"
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo -e "${RED}❌ Missing required variables:${NC}"
        printf '  - %s\n' "${missing_vars[@]}"
        return 1
    fi
    
    echo -e "${GREEN}✅ All required variables are set${NC}"
}

validate_secret_key() {
    echo "🔐 Validating SECRET_KEY..."
    
    if [ ${#SECRET_KEY} -lt 32 ]; then
        echo -e "${RED}❌ SECRET_KEY must be at least 32 characters${NC}"
        return 1
    fi
    
    if [[ "$SECRET_KEY" == *"dev"* ]] || [[ "$SECRET_KEY" == *"test"* ]]; then
        echo -e "${YELLOW}⚠️  SECRET_KEY appears to be a development key${NC}"
    fi
    
    echo -e "${GREEN}✅ SECRET_KEY validation passed${NC}"
}

validate_debug_mode() {
    echo "🐛 Checking DEBUG mode configuration..."
    
    if [ "$DEBUG" = "true" ]; then
        if [ "$ENVIRONMENT" = "production" ] || [ "$FLASK_ENV" = "production" ]; then
            echo -e "${RED}❌ DEBUG mode cannot be enabled in production${NC}"
            return 1
        else
            echo -e "${YELLOW}⚠️  DEBUG mode is enabled (development only)${NC}"
        fi
    else
        echo -e "${GREEN}✅ DEBUG mode is properly disabled${NC}"
    fi
}

validate_redis_connection() {
    echo "🔗 Testing Redis connection..."
    
    if [ -n "$REDIS_URL" ]; then
        # Extract host and port from Redis URL
        local redis_host=$(echo "$REDIS_URL" | sed -n 's/.*:\/\/.*@\?\([^:]*\):.*/\1/p')
        local redis_port=$(echo "$REDIS_URL" | sed -n 's/.*:\([0-9]*\).*/\1/p')
        
        if command -v redis-cli &> /dev/null; then
            if redis-cli -h "$redis_host" -p "$redis_port" ping &> /dev/null; then
                echo -e "${GREEN}✅ Redis connection successful${NC}"
            else
                echo -e "${RED}❌ Redis connection failed${NC}"
                return 1
            fi
        else
            echo -e "${YELLOW}⚠️  redis-cli not available, skipping connection test${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Redis URL not configured (using in-memory sessions)${NC}"
    fi
}

validate_file_limits() {
    echo "📁 Validating file processing limits..."
    
    if [ "$MAX_FILE_SIZE" -gt 1000 ]; then
        echo -e "${YELLOW}⚠️  MAX_FILE_SIZE is very large (${MAX_FILE_SIZE}MB)${NC}"
    fi
    
    if [ "$UPLOAD_TIMEOUT" -lt 60 ]; then
        echo -e "${YELLOW}⚠️  UPLOAD_TIMEOUT might be too short (${UPLOAD_TIMEOUT}s)${NC}"
    fi
    
    echo -e "${GREEN}✅ File limits validation passed${NC}"
}

validate_performance_settings() {
    echo "⚡ Checking performance configuration..."
    
    local cpu_cores=$(nproc 2>/dev/null || echo "unknown")
    
    if [ "$cpu_cores" != "unknown" ] && [ "$MAX_WORKERS" -gt $((cpu_cores * 2)) ]; then
        echo -e "${YELLOW}⚠️  MAX_WORKERS (${MAX_WORKERS}) might be too high for ${cpu_cores} CPU cores${NC}"
    fi
    
    if [ "$WORKER_TIMEOUT" -lt 30 ]; then
        echo -e "${YELLOW}⚠️  WORKER_TIMEOUT might be too short (${WORKER_TIMEOUT}s)${NC}"
    fi
    
    echo -e "${GREEN}✅ Performance settings validation passed${NC}"
}

validate_security_settings() {
    echo "🔒 Checking security configuration..."
    
    if [ "$DEBUG" = "true" ] && [ "$RATE_LIMIT_ENABLED" = "false" ]; then
        echo -e "${YELLOW}⚠️  Rate limiting is disabled in debug mode${NC}"
    fi
    
    if [ "$SECURE_COOKIES" = "true" ] && [ "$FORCE_HTTPS" != "true" ]; then
        echo -e "${YELLOW}⚠️  SECURE_COOKIES enabled but FORCE_HTTPS is not${NC}"
    fi
    
    echo -e "${GREEN}✅ Security settings validation passed${NC}"
}

# Run all validations
main() {
    local exit_code=0
    
    validate_required_vars || exit_code=1
    echo
    
    validate_secret_key || exit_code=1
    echo
    
    validate_debug_mode || exit_code=1
    echo
    
    validate_redis_connection || exit_code=1
    echo
    
    validate_file_limits || exit_code=1
    echo
    
    validate_performance_settings || exit_code=1
    echo
    
    validate_security_settings || exit_code=1
    echo
    
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}🎉 All validations passed! Environment is ready.${NC}"
    else
        echo -e "${RED}❌ Some validations failed. Please review the configuration.${NC}"
    fi
    
    return $exit_code
}

# Run main function
main "$@"
```

#### Quick Configuration Check
```bash
#!/bin/bash
# File: quick-config-check.sh

echo "Quick Configuration Check"
echo "========================"

# Check essential variables
echo "Essential Variables:"
echo "  DEBUG: ${DEBUG:-not set}"
echo "  SECRET_KEY: ${SECRET_KEY:+set (${#SECRET_KEY} chars)}${SECRET_KEY:-not set}"
echo "  LOG_LEVEL: ${LOG_LEVEL:-not set}"
echo "  REDIS_URL: ${REDIS_URL:+set}${REDIS_URL:-not set}"

# Check file processing
echo "File Processing:"
echo "  MAX_FILE_SIZE: ${MAX_FILE_SIZE:-not set}MB"
echo "  UPLOAD_TIMEOUT: ${UPLOAD_TIMEOUT:-not set}s"
echo "  CHUNK_SIZE: ${CHUNK_SIZE:-not set} rows"

# Check performance
echo "Performance:"
echo "  MAX_WORKERS: ${MAX_WORKERS:-not set}"
echo "  WORKER_TIMEOUT: ${WORKER_TIMEOUT:-not set}s"
echo "  SESSION_TIMEOUT: ${SESSION_TIMEOUT:-not set}s"

# Check security
echo "Security:"
echo "  RATE_LIMIT_ENABLED: ${RATE_LIMIT_ENABLED:-not set}"
echo "  SECURE_COOKIES: ${SECURE_COOKIES:-not set}"
echo "  FORCE_HTTPS: ${FORCE_HTTPS:-not set}"
```

### Docker Configuration Validation

#### Docker Compose Configuration Validator
```bash
#!/bin/bash
# File: validate-docker-config.sh

echo "🐳 Docker Configuration Validation"
echo "=================================="

# Validate docker-compose.yml
validate_compose_file() {
    echo "📋 Validating docker-compose.yml..."
    
    if [ ! -f "docker-compose.yml" ]; then
        echo "❌ docker-compose.yml not found"
        return 1
    fi
    
    if docker-compose config &> /dev/null; then
        echo "✅ docker-compose.yml is valid"
    else
        echo "❌ docker-compose.yml has syntax errors:"
        docker-compose config
        return 1
    fi
}

# Check environment file
validate_env_file() {
    local env_file=${1:-.env}
    echo "📄 Validating environment file: $env_file"
    
    if [ ! -f "$env_file" ]; then
        echo "⚠️  Environment file $env_file not found"
        return 0
    fi
    
    # Check for common issues
    if grep -q "^[[:space:]]*#" "$env_file"; then
        echo "✅ Environment file contains comments"
    fi
    
    if grep -q "=" "$env_file"; then
        echo "✅ Environment file contains variable assignments"
    else
        echo "❌ Environment file appears to be empty or invalid"
        return 1
    fi
    
    # Check for sensitive data exposure
    if grep -qi "password\|secret\|key" "$env_file"; then
        echo "⚠️  Environment file contains sensitive variables"
        echo "   Ensure file permissions are secure (600)"
        ls -la "$env_file"
    fi
}

# Test Docker services
test_services() {
    echo "🧪 Testing Docker services..."
    
    # Start services
    if docker-compose up -d; then
        echo "✅ Services started successfully"
        
        # Wait for services to be ready
        sleep 10
        
        # Test web service
        if curl -f -s http://localhost:8080/health > /dev/null; then
            echo "✅ Web service is responding"
        else
            echo "❌ Web service is not responding"
            docker-compose logs web
        fi
        
        # Test Redis (if configured)
        if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
            echo "✅ Redis service is responding"
        else
            echo "⚠️  Redis service test failed or not configured"
        fi
        
        # Cleanup
        docker-compose down
    else
        echo "❌ Failed to start services"
        return 1
    fi
}

# Run validations
validate_compose_file
echo
validate_env_file
echo
test_services
```

### Application Health Validation

#### Health Check Script
```bash
#!/bin/bash
# File: health-check.sh

HEALTH_URL="${HEALTH_URL:-http://localhost:8080/health}"
TIMEOUT="${TIMEOUT:-10}"
MAX_RETRIES="${MAX_RETRIES:-3}"

echo "🏥 Application Health Check"
echo "=========================="
echo "URL: $HEALTH_URL"
echo "Timeout: ${TIMEOUT}s"
echo "Max Retries: $MAX_RETRIES"
echo

check_health() {
    local retries=0
    
    while [ $retries -lt $MAX_RETRIES ]; do
        echo "Attempt $((retries + 1))/$MAX_RETRIES..."
        
        if curl -f -s --max-time $TIMEOUT "$HEALTH_URL" > /dev/null; then
            echo "✅ Health check passed"
            
            # Get detailed health info
            echo "Health Details:"
            curl -s --max-time $TIMEOUT "$HEALTH_URL" | python3 -m json.tool 2>/dev/null || echo "Raw response received"
            
            return 0
        else
            echo "❌ Health check failed"
            retries=$((retries + 1))
            
            if [ $retries -lt $MAX_RETRIES ]; then
                echo "Retrying in 2 seconds..."
                sleep 2
            fi
        fi
    done
    
    echo "❌ Health check failed after $MAX_RETRIES attempts"
    return 1
}

# Additional checks
check_endpoints() {
    echo "🔍 Testing additional endpoints..."
    
    # Test main page
    if curl -f -s --max-time $TIMEOUT "http://localhost:8080/" > /dev/null; then
        echo "✅ Main page accessible"
    else
        echo "❌ Main page not accessible"
    fi
    
    # Test API endpoints (basic)
    if curl -f -s --max-time $TIMEOUT "http://localhost:8080/api/" > /dev/null; then
        echo "✅ API endpoints accessible"
    else
        echo "⚠️  API endpoints may not be accessible"
    fi
}

# Run checks
check_health
echo
check_endpoints
```

### Performance Validation

#### Performance Test Script
```bash
#!/bin/bash
# File: performance-test.sh

echo "⚡ Performance Validation"
echo "======================="

# Test file upload performance
test_upload_performance() {
    echo "📤 Testing file upload performance..."
    
    # Create test file if it doesn't exist
    if [ ! -f "test-data.csv" ]; then
        echo "Creating test CSV file..."
        echo "Property locality,Purchase price,Purchase date,Property type" > test-data.csv
        for i in {1..1000}; do
            echo "Suburb $((i % 100)),$(($RANDOM * 1000)),2023-01-$((i % 28 + 1)),House" >> test-data.csv
        done
    fi
    
    # Time the upload
    echo "Uploading test file..."
    start_time=$(date +%s)
    
    if curl -X POST -F "file=@test-data.csv" http://localhost:8080/api/upload > /dev/null 2>&1; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo "✅ Upload completed in ${duration}s"
        
        if [ $duration -lt 10 ]; then
            echo "✅ Upload performance is good"
        elif [ $duration -lt 30 ]; then
            echo "⚠️  Upload performance is acceptable"
        else
            echo "❌ Upload performance is slow"
        fi
    else
        echo "❌ Upload test failed"
    fi
}

# Test memory usage
test_memory_usage() {
    echo "💾 Testing memory usage..."
    
    if command -v docker &> /dev/null; then
        local memory_usage=$(docker stats --no-stream --format "{{.MemUsage}}" property_analyzer_web 2>/dev/null)
        if [ -n "$memory_usage" ]; then
            echo "Current memory usage: $memory_usage"
        else
            echo "⚠️  Could not retrieve memory usage"
        fi
    else
        echo "⚠️  Docker not available for memory testing"
    fi
}

# Test response times
test_response_times() {
    echo "⏱️  Testing response times..."
    
    local endpoints=(
        "http://localhost:8080/"
        "http://localhost:8080/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        local response_time=$(curl -o /dev/null -s -w "%{time_total}" "$endpoint" 2>/dev/null)
        if [ -n "$response_time" ]; then
            echo "  $endpoint: ${response_time}s"
            
            if (( $(echo "$response_time < 1.0" | bc -l) )); then
                echo "    ✅ Good response time"
            elif (( $(echo "$response_time < 3.0" | bc -l) )); then
                echo "    ⚠️  Acceptable response time"
            else
                echo "    ❌ Slow response time"
            fi
        else
            echo "  $endpoint: Failed to measure"
        fi
    done
}

# Run performance tests
test_upload_performance
echo
test_memory_usage
echo
test_response_times
```

### Usage Instructions

#### Running Validation Scripts
```bash
# Make scripts executable
chmod +x validate-environment.sh
chmod +x validate-docker-config.sh
chmod +x health-check.sh
chmod +x performance-test.sh

# Run environment validation
./validate-environment.sh

# Run Docker configuration validation
./validate-docker-config.sh

# Run health check
./validate-environment.sh && ./health-check.sh

# Run performance tests
./performance-test.sh

# Run all validations
./validate-environment.sh && \
./validate-docker-config.sh && \
./health-check.sh && \
./performance-test.sh
```

#### Integration with CI/CD
```yaml
# GitHub Actions example
name: Configuration Validation
on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Validate Environment
        run: |
          export SECRET_KEY=${{ secrets.SECRET_KEY }}
          export REDIS_URL=${{ secrets.REDIS_URL }}
          ./validate-environment.sh
      
      - name: Validate Docker Configuration
        run: ./validate-docker-config.sh
      
      - name: Health Check
        run: |
          docker-compose up -d
          sleep 30
          ./health-check.sh
          docker-compose down
```

This comprehensive Environment Configuration Guide provides complete coverage of all environment variables, configuration examples for different scenarios, security best practices, performance tuning options, and thorough validation procedures for the Property Data Dashboard.