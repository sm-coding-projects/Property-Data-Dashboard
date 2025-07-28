# Verification and Testing

This section provides comprehensive guidance for verifying successful deployment and testing the Property Data Dashboard functionality after Docker deployment.

## Health Check Endpoints and Usage

### Application Health Check Endpoint

The Property Data Dashboard includes a built-in health check endpoint that provides detailed status information about all application components.

#### Primary Health Check
```bash
# Basic health check
curl http://localhost:8080/health

# Expected healthy response:
{
  "status": "healthy",
  "timestamp": "2025-01-25T10:30:45.123456",
  "version": "1.0.0",
  "components": {
    "session_manager": "ok",
    "file_processor": "ok"
  }
}
```

#### Health Check with Detailed Output
```bash
# Health check with formatted output
curl -s http://localhost:8080/health | python3 -m json.tool

# Health check with response time
curl -w "Response time: %{time_total}s\n" -s http://localhost:8080/health
```

#### Health Check Status Codes
- **200 OK**: All components are healthy and functioning
- **500 Internal Server Error**: One or more components are unhealthy

#### Component Status Meanings
| Component | Status | Description |
|-----------|--------|-------------|
| `session_manager` | `ok` | Redis connection and session handling working |
| `file_processor` | `ok` | CSV processing capabilities available |

### Service-Specific Health Checks

#### Web Application Health
```bash
# Test web application responsiveness
curl -I http://localhost:8080/
# Expected: HTTP/1.1 200 OK

# Test with timeout
curl --max-time 10 -f http://localhost:8080/health
# Should complete within 10 seconds
```

#### Redis Health Check
```bash
# Check Redis connectivity (if Redis port is exposed)
docker-compose exec redis redis-cli ping
# Expected: PONG

# Check Redis from web container
docker-compose exec web python3 -c "
import redis
r = redis.Redis(host='redis', port=6379, db=0)
print('Redis ping:', r.ping())
"
# Expected: Redis ping: True
```

#### Container Health Status
```bash
# Check Docker health status for all containers
docker-compose ps

# Expected output showing healthy containers:
# NAME                     STATUS
# property_analyzer_web    Up (healthy)
# property_analyzer_redis  Up (healthy)

# Detailed health check status
docker inspect property_analyzer_web --format='{{.State.Health.Status}}'
# Expected: healthy
```

## Log Verification Steps and Commands

### Application Log Access

#### Real-time Log Monitoring
```bash
# Follow all service logs
docker-compose logs -f

# Follow specific service logs
docker-compose logs -f web
docker-compose logs -f redis

# Follow logs with timestamps
docker-compose logs -f -t web
```

#### Log Analysis Commands
```bash
# View recent logs (last 50 lines)
docker-compose logs --tail=50 web

# Search for specific log patterns
docker-compose logs web | grep "ERROR"
docker-compose logs web | grep "Health check"
docker-compose logs web | grep "Session"

# Export logs for analysis
docker-compose logs web > application.log
docker-compose logs redis > redis.log
```

### Log Verification Checklist

#### Startup Verification Logs
Look for these key log messages during startup:

```bash
# 1. Application startup
docker-compose logs web | grep -E "(Starting|Ready|Listening)"
# Expected patterns:
# "Starting Property Data Dashboard"
# "Application ready on port 5000"

# 2. Redis connection
docker-compose logs web | grep -i redis
# Expected: "Redis connection established"

# 3. Configuration loading
docker-compose logs web | grep -i config
# Expected: "Configuration loaded successfully"
```

#### Runtime Verification Logs
```bash
# 4. Health check logs
docker-compose logs web | grep -i health
# Expected: Regular health check responses

# 5. Session management logs
docker-compose logs web | grep -i session
# Expected: Session creation and cleanup logs

# 6. File processing logs
docker-compose logs web | grep -i "file\|upload\|process"
# Expected: File upload and processing activity
```

#### Error Log Monitoring
```bash
# Check for error patterns
docker-compose logs web | grep -E "(ERROR|CRITICAL|Exception|Traceback)"

# Check for warning patterns
docker-compose logs web | grep -E "(WARNING|WARN)"

# Monitor Redis errors
docker-compose logs redis | grep -E "(error|Error|ERROR)"
```

### Log Level Configuration

#### Development Log Verification
```bash
# Verify debug logging is enabled (development)
docker-compose logs web | grep DEBUG | head -5

# Check log level configuration
docker-compose exec web python3 -c "
from config import config
print('Current log level:', config.LOG_LEVEL)
"
```

#### Production Log Verification
```bash
# Verify appropriate log level (production)
docker-compose logs web | grep -E "(INFO|WARNING|ERROR)" | head -10

# Ensure debug logs are not present in production
docker-compose logs web | grep DEBUG
# Should return no results in production
```

## Basic Functionality Testing Checklist

### Pre-Testing Setup
```bash
# Ensure services are running
docker-compose ps

# Verify health status
curl -f http://localhost:8080/health

# Prepare test data
# Download or create a sample CSV file with columns:
# Property locality, Purchase price, Contract date, Primary purpose, etc.
```

### Core Functionality Tests

#### 1. Web Interface Access Test
```bash
# Test main page access
curl -I http://localhost:8080/
# Expected: HTTP/1.1 200 OK

# Test page content
curl -s http://localhost:8080/ | grep -i "property data dashboard"
# Should find the application title
```

**Manual Verification:**
- [ ] Open http://localhost:8080 in browser
- [ ] Page loads without errors
- [ ] File upload area is visible
- [ ] No JavaScript console errors

#### 2. File Upload Functionality Test
```bash
# Create test CSV file
cat > test-data.csv << 'EOF'
Property locality,Purchase price,Contract date,Primary purpose,Property house number,Property street name,Property ID
Sydney,500000,2024-01-15,Residential,123,Main Street,PROP001
Melbourne,450000,2024-01-20,Residential,456,Oak Avenue,PROP002
Brisbane,350000,2024-01-25,Commercial,789,Business Road,PROP003
EOF

# Test file upload via API
curl -X POST http://localhost:8080/api/upload \
  -F "file=@test-data.csv" \
  -H "Content-Type: multipart/form-data"

# Expected response should include:
# - "message": "File processed successfully"
# - "session_id": "some-uuid"
# - "filters": {...}
```

**Manual Verification:**
- [ ] Upload test CSV file through web interface
- [ ] Upload progress indicator appears
- [ ] Success message displays
- [ ] Filter options populate correctly
- [ ] Data table shows uploaded records

#### 3. Data Filtering Test
```bash
# Test data filtering (replace SESSION_ID with actual session ID from upload)
SESSION_ID="your-session-id-here"

curl -X POST http://localhost:8080/api/data \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"suburbs\": [\"Sydney\"],
    \"priceRange\": [400000, 600000]
  }"

# Expected response should include:
# - "metrics": {...}
# - "table": {"data": [...], "totalRows": ...}
```

**Manual Verification:**
- [ ] Select suburbs from dropdown filter
- [ ] Adjust price range filters
- [ ] Set date range filters
- [ ] Verify data table updates correctly
- [ ] Check metrics update appropriately

#### 4. Export Functionality Test
```bash
# Test CSV export
curl -X POST http://localhost:8080/api/export \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"export_format\": \"csv\",
    \"suburbs\": [\"Sydney\"]
  }" \
  -o exported-data.csv

# Verify export file
head -5 exported-data.csv

# Test PDF export (if reportlab is installed)
curl -X POST http://localhost:8080/api/export \
  -H "Content-Type: application/json" \
  -d "{
    \"session_id\": \"$SESSION_ID\",
    \"export_format\": \"pdf\"
  }" \
  -o exported-data.pdf
```

**Manual Verification:**
- [ ] Click CSV export button
- [ ] File downloads successfully
- [ ] CSV contains filtered data
- [ ] Click PDF export button (if available)
- [ ] PDF generates and downloads

#### 5. Session Management Test
```bash
# Test session validation
curl http://localhost:8080/api/session/$SESSION_ID

# Expected response:
# {"valid": true, "session_info": {...}}

# Test invalid session
curl http://localhost:8080/api/session/invalid-session-id
# Expected: {"valid": false, "message": "Session not found or expired"}
```

#### 6. Error Handling Test
```bash
# Test invalid file upload
echo "invalid,csv,content" > invalid.txt
curl -X POST http://localhost:8080/api/upload \
  -F "file=@invalid.txt"
# Should return appropriate error message

# Test missing session ID
curl -X POST http://localhost:8080/api/data \
  -H "Content-Type: application/json" \
  -d "{}"
# Should return session ID required error
```

### Advanced Functionality Tests

#### 7. Large File Handling Test
```bash
# Create larger test file (adjust size as needed)
python3 -c "
import csv
import random
from datetime import datetime, timedelta

suburbs = ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide']
purposes = ['Residential', 'Commercial', 'Industrial']

with open('large-test.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Property locality', 'Purchase price', 'Contract date', 'Primary purpose', 'Property house number', 'Property street name', 'Property ID'])
    
    for i in range(10000):  # 10,000 records
        writer.writerow([
            random.choice(suburbs),
            random.randint(200000, 1000000),
            (datetime.now() - timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
            random.choice(purposes),
            random.randint(1, 999),
            f'Street {i}',
            f'PROP{i:06d}'
        ])
"

# Test large file upload
time curl -X POST http://localhost:8080/api/upload \
  -F "file=@large-test.csv"
# Monitor response time and memory usage
```

#### 8. Concurrent User Test
```bash
# Test multiple simultaneous uploads (basic load test)
for i in {1..5}; do
  (curl -X POST http://localhost:8080/api/upload \
    -F "file=@test-data.csv" &)
done
wait

# Monitor system resources during test
docker stats --no-stream
```

### Functionality Test Results Validation

#### Success Criteria Checklist
- [ ] All health checks return status 200
- [ ] File upload completes without errors
- [ ] Data filtering produces expected results
- [ ] Export functions generate valid files
- [ ] Session management works correctly
- [ ] Error handling provides appropriate messages
- [ ] Large files process within reasonable time
- [ ] System remains stable under concurrent load

#### Common Issues and Solutions
| Issue | Symptoms | Solution |
|-------|----------|----------|
| Upload fails | 413 error, timeout | Check MAX_FILE_SIZE, increase timeout |
| Filtering slow | Long response times | Reduce data size, check memory |
| Export fails | 500 error | Check disk space, verify dependencies |
| Session expired | 404 session errors | Check SESSION_TIMEOUT setting |

## Performance Verification Guidelines

### Response Time Benchmarks

#### Acceptable Response Times
| Operation | Target Time | Maximum Time |
|-----------|-------------|--------------|
| Health check | < 100ms | < 500ms |
| Page load | < 2s | < 5s |
| File upload (10MB) | < 30s | < 60s |
| Data filtering | < 1s | < 3s |
| Export generation | < 10s | < 30s |

#### Performance Testing Commands
```bash
# Test response times
curl -w "Time: %{time_total}s\n" -s http://localhost:8080/health

# Test page load time
curl -w "Connect: %{time_connect}s, Total: %{time_total}s\n" \
  -s http://localhost:8080/ > /dev/null

# Test file upload performance
time curl -X POST http://localhost:8080/api/upload \
  -F "file=@test-data.csv"

# Test data filtering performance
time curl -X POST http://localhost:8080/api/data \
  -H "Content-Type: application/json" \
  -d "{\"session_id\": \"$SESSION_ID\"}"
```

### Resource Usage Monitoring

#### Memory Usage Verification
```bash
# Monitor container memory usage
docker stats --no-stream --format "table {{.Container}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Check for memory leaks (run over time)
watch -n 5 'docker stats --no-stream property_analyzer_web --format "{{.MemUsage}}"'

# Memory usage thresholds:
# - Normal operation: < 1GB
# - File processing: < 2GB
# - Alert threshold: > 3GB
```

#### CPU Usage Verification
```bash
# Monitor CPU usage
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}"

# CPU usage thresholds:
# - Idle: < 5%
# - Normal operation: < 30%
# - File processing: < 80%
# - Alert threshold: > 90% sustained
```

#### Disk Usage Verification
```bash
# Check disk usage
df -h

# Check Docker volume usage
docker system df

# Monitor log file sizes
du -sh $(docker inspect property_analyzer_web --format='{{.LogPath}}')

# Disk usage thresholds:
# - Available space: > 10GB
# - Log files: < 1GB total
# - Alert threshold: < 5GB available
```

### Performance Optimization Verification

#### Database Performance (Redis)
```bash
# Check Redis performance
docker-compose exec redis redis-cli info stats

# Monitor Redis memory usage
docker-compose exec redis redis-cli info memory

# Test Redis response time
docker-compose exec redis redis-cli --latency -h redis -p 6379
```

#### Application Performance Metrics
```bash
# Check application metrics (if available)
curl -s http://localhost:8080/health | grep -E "(response_time|memory_usage|cpu_usage)"

# Monitor request processing time
docker-compose logs web | grep -E "Processing time|Response time" | tail -10
```

### Load Testing Guidelines

#### Basic Load Test
```bash
# Install Apache Bench (if not available)
# Ubuntu/Debian: apt-get install apache2-utils
# macOS: brew install httpie

# Simple load test
ab -n 100 -c 10 http://localhost:8080/health
# 100 requests, 10 concurrent

# Expected results:
# - Success rate: 100%
# - Average response time: < 100ms
# - No failed requests
```

#### File Upload Load Test
```bash
# Create test script for upload load testing
cat > upload-load-test.sh << 'EOF'
#!/bin/bash
CONCURRENT_UPLOADS=5
TEST_FILE="test-data.csv"

echo "Starting $CONCURRENT_UPLOADS concurrent uploads..."
for i in $(seq 1 $CONCURRENT_UPLOADS); do
  (
    echo "Upload $i starting..."
    curl -X POST http://localhost:8080/api/upload \
      -F "file=@$TEST_FILE" \
      -w "Upload $i completed in %{time_total}s\n" \
      -s -o /dev/null
  ) &
done
wait
echo "All uploads completed"
EOF

chmod +x upload-load-test.sh
./upload-load-test.sh
```

#### Performance Monitoring During Load
```bash
# Monitor system during load test
watch -n 1 'docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"'

# Monitor application logs during load
docker-compose logs -f web | grep -E "(ERROR|WARNING|Processing)"
```

## Service Status Checking Procedures

### Container Status Verification

#### Docker Compose Service Status
```bash
# Check all service status
docker-compose ps

# Expected output format:
# NAME                     COMMAND                  SERVICE   STATUS    PORTS
# property_analyzer_web    "python app.py"          web       Up        0.0.0.0:8080->5000/tcp
# property_analyzer_redis  "redis-server"           redis     Up        6379/tcp

# Check specific service status
docker-compose ps web
docker-compose ps redis
```

#### Individual Container Health
```bash
# Check container health status
docker inspect property_analyzer_web --format='{{.State.Health.Status}}'
docker inspect property_analyzer_redis --format='{{.State.Health.Status}}'

# Possible health statuses:
# - "healthy": Container is functioning properly
# - "unhealthy": Container health check is failing
# - "starting": Container is still starting up
# - "none": No health check configured
```

#### Container Resource Status
```bash
# Check container resource usage
docker stats --no-stream property_analyzer_web property_analyzer_redis

# Check container uptime
docker inspect property_analyzer_web --format='{{.State.StartedAt}}'

# Check container restart count
docker inspect property_analyzer_web --format='{{.RestartCount}}'
```

### Service Dependency Verification

#### Service Startup Order
```bash
# Verify services started in correct order
docker-compose logs | grep -E "(Starting|Started|Ready)" | sort

# Expected order:
# 1. Redis starts first
# 2. Web application connects to Redis
# 3. Web application becomes ready
```

#### Inter-Service Communication
```bash
# Test web -> redis communication
docker-compose exec web python3 -c "
import redis
try:
    r = redis.Redis(host='redis', port=6379, db=0)
    print('Redis connection:', r.ping())
    print('Redis info:', r.info('server')['redis_version'])
except Exception as e:
    print('Redis connection failed:', e)
"

# Test network connectivity
docker-compose exec web ping -c 3 redis
```

### Service Recovery Procedures

#### Restart Individual Services
```bash
# Restart web service only
docker-compose restart web

# Restart redis service only
docker-compose restart redis

# Restart all services
docker-compose restart
```

#### Service Recovery Verification
```bash
# Check service recovery after restart
docker-compose restart web
sleep 10
curl -f http://localhost:8080/health

# Monitor recovery in logs
docker-compose logs -f web | grep -E "(Starting|Ready|Health)"
```

#### Troubleshooting Service Issues
```bash
# Check service logs for errors
docker-compose logs web | grep -E "(ERROR|CRITICAL|Exception)"

# Check container exit codes
docker-compose ps -a

# Inspect container configuration
docker inspect property_analyzer_web | grep -A 10 -B 10 -E "(Health|Restart)"
```

### Automated Status Monitoring

#### Create Status Check Script
```bash
cat > status-check.sh << 'EOF'
#!/bin/bash

echo "=== Property Data Dashboard Status Check ==="
echo "Timestamp: $(date)"
echo

# Check Docker Compose services
echo "1. Service Status:"
docker-compose ps

echo -e "\n2. Health Checks:"
# Web application health
if curl -f -s http://localhost:8080/health > /dev/null; then
    echo "✓ Web application: Healthy"
else
    echo "✗ Web application: Unhealthy"
fi

# Redis health
if docker-compose exec -T redis redis-cli ping | grep -q PONG; then
    echo "✓ Redis: Healthy"
else
    echo "✗ Redis: Unhealthy"
fi

echo -e "\n3. Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

echo -e "\n4. Recent Errors:"
docker-compose logs --since=10m | grep -E "(ERROR|CRITICAL)" | tail -5

echo -e "\n5. Uptime:"
docker inspect property_analyzer_web --format='Started: {{.State.StartedAt}}'
docker inspect property_analyzer_redis --format='Started: {{.State.StartedAt}}'

echo -e "\nStatus check completed."
EOF

chmod +x status-check.sh
```

#### Schedule Regular Status Checks
```bash
# Add to crontab for regular monitoring (every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /path/to/status-check.sh >> /var/log/property-dashboard-status.log") | crontab -

# Manual status check
./status-check.sh
```

### Status Check Integration

#### Integration with Monitoring Systems
```bash
# Create JSON status output for monitoring systems
cat > status-json.sh << 'EOF'
#!/bin/bash

# Get service status
WEB_STATUS=$(curl -f -s http://localhost:8080/health >/dev/null && echo "healthy" || echo "unhealthy")
REDIS_STATUS=$(docker-compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG && echo "healthy" || echo "unhealthy")

# Get resource usage
CPU_USAGE=$(docker stats --no-stream --format "{{.CPUPerc}}" property_analyzer_web | sed 's/%//')
MEM_USAGE=$(docker stats --no-stream --format "{{.MemPerc}}" property_analyzer_web | sed 's/%//')

# Output JSON
cat << JSON
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "services": {
    "web": "$WEB_STATUS",
    "redis": "$REDIS_STATUS"
  },
  "resources": {
    "cpu_percent": $CPU_USAGE,
    "memory_percent": $MEM_USAGE
  },
  "overall_status": "$([ "$WEB_STATUS" = "healthy" ] && [ "$REDIS_STATUS" = "healthy" ] && echo "healthy" || echo "unhealthy")"
}
JSON
EOF

chmod +x status-json.sh
./status-json.sh
```

This comprehensive verification and testing section provides all the tools and procedures needed to ensure the Property Data Dashboard is deployed correctly and functioning optimally. The section covers health checks, log verification, functionality testing, performance monitoring, and service status procedures as required by the task specifications.