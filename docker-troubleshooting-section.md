# Docker Troubleshooting

This section provides comprehensive troubleshooting guidance for Docker-specific issues when deploying the Property Data Dashboard. Issues are organized by symptoms to help you quickly identify and resolve problems.

## Container Startup Issues

### Container Won't Start

**Symptoms:**
- `docker-compose up` command fails
- Container exits immediately after starting
- Error messages during container initialization
- Services show as "Exited" status

**Common Causes & Solutions:**

#### Port Binding Conflicts
```bash
# Check if port 8080 is already in use
netstat -tulpn | grep :8080
# or on macOS
lsof -i :8080

# Kill process using the port
sudo kill -9 $(lsof -t -i:8080)

# Alternative: Use a different port
docker-compose up --build -p 8081:5000
```

#### Docker Daemon Issues
```bash
# Check Docker daemon status
sudo systemctl status docker

# Restart Docker service (Linux)
sudo systemctl restart docker

# Restart Docker Desktop (macOS/Windows)
# Use Docker Desktop interface to restart
```

#### Image Build Failures
```bash
# Clean build with no cache
docker-compose build --no-cache

# Remove existing images and rebuild
docker-compose down --rmi all
docker-compose up --build

# Check for build errors
docker-compose build web 2>&1 | tee build.log
```

#### Configuration File Errors
```bash
# Validate docker-compose.yml syntax
docker-compose config

# Check for indentation issues
python -c "import yaml; yaml.safe_load(open('docker-compose.yml'))"

# Verify environment variables
docker-compose config --services
```

### Container Exits Immediately

**Symptoms:**
- Container starts but exits within seconds
- Exit code 125, 126, or 127 in logs
- "Container command not found" errors

**Diagnostic Commands:**
```bash
# Check container exit code
docker-compose ps

# View detailed container logs
docker-compose logs web --tail=50

# Inspect container configuration
docker inspect property_analyzer_web

# Run container interactively for debugging
docker-compose run --rm web bash
```

**Solutions:**
```bash
# Fix common Python path issues
docker-compose exec web which python
docker-compose exec web python --version

# Verify application files are present
docker-compose exec web ls -la /app

# Check file permissions
docker-compose exec web ls -la /app/app.py

# Test application startup manually
docker-compose exec web python app.py
```

## Port Binding and Network Connectivity Problems

### Port Already in Use

**Symptoms:**
- "bind: address already in use" error
- "Port 8080 is already allocated" message
- Cannot access dashboard at expected URL

**Solutions:**
```bash
# Find process using port 8080
sudo lsof -i :8080

# Kill the conflicting process
sudo kill -9 <PID>

# Use netstat to check port usage
netstat -tulpn | grep :8080

# Change port in docker-compose.yml
ports:
  - "8081:5000"  # Use port 8081 instead

# Or use environment variable
PORT=8081 docker-compose up
```

### Network Connectivity Issues

**Symptoms:**
- Cannot access dashboard from browser
- "Connection refused" errors
- Timeouts when accessing the application

**Diagnostic Steps:**
```bash
# Check if containers are running
docker-compose ps

# Test internal container connectivity
docker-compose exec web curl http://localhost:5000/health

# Check container networking
docker network ls
docker network inspect property-data-dashboard_default

# Test external connectivity
curl http://localhost:8080/health

# Check firewall settings (Linux)
sudo ufw status
sudo iptables -L
```

**Solutions:**
```bash
# Restart networking
docker-compose down
docker-compose up

# Reset Docker networks
docker network prune

# Check Docker Desktop network settings (macOS/Windows)
# Ensure "Use kernel networking for UDP" is disabled

# Verify host file entries (if using custom domains)
cat /etc/hosts
```

### Service Communication Problems

**Symptoms:**
- Web service cannot connect to Redis
- "Connection refused" between services
- DNS resolution failures between containers

**Solutions:**
```bash
# Test inter-service connectivity
docker-compose exec web ping redis
docker-compose exec web nslookup redis

# Check service dependencies
docker-compose config | grep depends_on

# Verify service names in docker-compose.yml
docker-compose exec web curl http://redis:6379

# Restart services in correct order
docker-compose down
docker-compose up redis
docker-compose up web
```

## Volume Mounting and Permission Issues

### Permission Denied Errors

**Symptoms:**
- "Permission denied" when accessing mounted files
- Cannot write to application directories
- File ownership conflicts

**Solutions:**
```bash
# Fix file ownership (Linux/macOS)
sudo chown -R $USER:$USER .

# Check current file permissions
ls -la

# Fix permissions for Docker user
sudo chmod -R 755 .

# Use proper user in Dockerfile
USER 1000:1000

# Alternative: Run container as current user
docker-compose run --user $(id -u):$(id -g) web bash
```

### Volume Mount Failures

**Symptoms:**
- Files not appearing in container
- Changes not reflected between host and container
- "No such file or directory" errors

**Diagnostic Commands:**
```bash
# Verify volume mounts
docker-compose config

# Check mounted volumes in container
docker-compose exec web ls -la /app

# Inspect volume configuration
docker volume ls
docker volume inspect property-data-dashboard_redis_data

# Test file creation
docker-compose exec web touch /app/test.txt
ls -la test.txt
```

**Solutions:**
```bash
# Use absolute paths in docker-compose.yml
volumes:
  - /absolute/path/to/project:/app

# Fix relative path issues
volumes:
  - .:/app:rw

# Recreate containers with new volumes
docker-compose down -v
docker-compose up --build

# Use named volumes for persistent data
volumes:
  app_data:
services:
  web:
    volumes:
      - app_data:/app/data
```

### File Synchronization Issues

**Symptoms:**
- Code changes not reflected in running container
- Static files not updating
- Hot reload not working in development

**Solutions:**
```bash
# Force container recreation
docker-compose up --build --force-recreate

# Check file watching capabilities
docker-compose exec web ls -la /app

# Verify volume mount type
docker inspect property_analyzer_web | grep -A 10 Mounts

# Use polling for file watching (if needed)
# Add to docker-compose.yml:
environment:
  - CHOKIDAR_USEPOLLING=true

# Restart with clean volumes
docker-compose down -v
docker-compose up --build
```

## Memory and Resource Constraint Problems

### Out of Memory Errors

**Symptoms:**
- Container killed unexpectedly
- "Killed" messages in logs
- Process exits with code 137
- System becomes unresponsive

**Diagnostic Commands:**
```bash
# Check Docker memory allocation
docker system info | grep Memory

# Monitor container memory usage
docker stats

# Check system memory
free -h
top

# View container resource limits
docker inspect property_analyzer_web | grep -A 10 Memory
```

**Solutions:**
```bash
# Increase Docker Desktop memory allocation
# Docker Desktop > Settings > Resources > Memory: 8GB+

# Reduce memory usage in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G
    reservations:
      memory: 1G

# Optimize application memory usage
export MAX_FILE_SIZE=200  # Reduce max file size

# Clear Docker cache
docker system prune -a

# Use memory-efficient processing
# Set environment variables:
export PANDAS_MEMORY_EFFICIENT=true
```

### CPU Performance Issues

**Symptoms:**
- Slow file processing
- High CPU usage
- Request timeouts
- Unresponsive application

**Diagnostic Commands:**
```bash
# Monitor CPU usage
docker stats

# Check container CPU limits
docker inspect property_analyzer_web | grep -A 5 Cpu

# Monitor system CPU
htop
top -p $(docker inspect -f '{{.State.Pid}}' property_analyzer_web)
```

**Solutions:**
```bash
# Limit CPU usage in docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '2.0'
    reservations:
      cpus: '1.0'

# Optimize file processing
export MAX_FILE_SIZE=100
export CHUNK_SIZE=10000

# Use multiple workers (if supported)
command: ["gunicorn", "--workers", "2", "--bind", "0.0.0.0:5000", "app:app"]

# Monitor and adjust worker timeout
command: ["gunicorn", "--timeout", "300", "--bind", "0.0.0.0:5000", "app:app"]
```

### Disk Space Issues

**Symptoms:**
- "No space left on device" errors
- Container fails to write files
- Docker build failures

**Solutions:**
```bash
# Check disk usage
df -h
docker system df

# Clean up Docker resources
docker system prune -a --volumes

# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Clean up build cache
docker builder prune -a

# Monitor disk usage during operation
watch -n 5 'df -h && docker system df'
```

## Service Dependency and Timing Issues

### Redis Connection Problems

**Symptoms:**
- "Redis connection failed" in logs
- Session storage errors
- Application starts but sessions don't work

**Diagnostic Commands:**
```bash
# Check Redis container status
docker-compose ps redis

# Test Redis connectivity
docker-compose exec redis redis-cli ping

# Check Redis logs
docker-compose logs redis

# Test connection from web service
docker-compose exec web telnet redis 6379
```

**Solutions:**
```bash
# Restart Redis service
docker-compose restart redis

# Check Redis configuration
docker-compose exec redis redis-cli info

# Verify Redis URL in environment
docker-compose exec web env | grep REDIS

# Use health checks for proper startup order
services:
  redis:
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
  web:
    depends_on:
      redis:
        condition: service_healthy
```

### Service Startup Order Issues

**Symptoms:**
- Web service starts before dependencies
- Connection errors during startup
- Intermittent startup failures

**Solutions:**
```bash
# Use depends_on in docker-compose.yml
services:
  web:
    depends_on:
      - redis

# Implement health checks
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s

# Add startup delays if needed
command: sh -c "sleep 10 && gunicorn --bind 0.0.0.0:5000 app:app"

# Use wait scripts for complex dependencies
# Add to Dockerfile:
COPY wait-for-it.sh /wait-for-it.sh
CMD ["/wait-for-it.sh", "redis:6379", "--", "gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

### Database Connection Issues

**Symptoms:**
- Cannot connect to database
- Connection timeouts
- Authentication failures

**Solutions:**
```bash
# Check database container
docker-compose ps db

# Test database connectivity
docker-compose exec web nc -zv db 5432

# Check database logs
docker-compose logs db

# Verify connection string
docker-compose exec web env | grep DATABASE_URL

# Reset database connection
docker-compose restart db
docker-compose restart web
```

## Diagnostic Commands and Log Analysis

### Container Inspection Commands

```bash
# View container configuration
docker inspect property_analyzer_web

# Check container processes
docker-compose exec web ps aux

# View container resource usage
docker stats property_analyzer_web

# Check container networking
docker port property_analyzer_web

# View container environment variables
docker-compose exec web env
```

### Log Analysis Commands

```bash
# View all service logs
docker-compose logs

# View specific service logs
docker-compose logs web
docker-compose logs redis

# Follow logs in real-time
docker-compose logs -f --tail=100

# Filter error logs
docker-compose logs web | grep -i error
docker-compose logs web | grep -i warning

# Export logs for analysis
docker-compose logs web > application.log
docker-compose logs redis > redis.log

# View logs with timestamps
docker-compose logs -t web

# Search logs for specific patterns
docker-compose logs web | grep "HTTP/1.1"
docker-compose logs web | grep -E "(ERROR|CRITICAL)"
```

### Network Diagnostic Commands

```bash
# List Docker networks
docker network ls

# Inspect network configuration
docker network inspect property-data-dashboard_default

# Test internal connectivity
docker-compose exec web curl http://redis:6379
docker-compose exec web ping redis

# Check DNS resolution
docker-compose exec web nslookup redis
docker-compose exec web dig redis

# Test external connectivity
docker-compose exec web curl http://google.com
docker-compose exec web wget -qO- http://httpbin.org/ip
```

### Performance Monitoring Commands

```bash
# Monitor resource usage
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# Check system resources
free -h
df -h
iostat 1 5

# Monitor container processes
docker-compose exec web top
docker-compose exec web htop

# Check application performance
docker-compose exec web curl -w "@curl-format.txt" http://localhost:5000/health

# Monitor file system usage
docker-compose exec web du -sh /app/*
```

### Health Check Commands

```bash
# Check application health
curl http://localhost:8080/health

# Verify service endpoints
curl -I http://localhost:8080/
curl http://localhost:8080/api/health

# Test file upload functionality
curl -X POST -F "file=@test.csv" http://localhost:8080/api/upload

# Check Redis health
docker-compose exec redis redis-cli ping
docker-compose exec redis redis-cli info stats
```

## Advanced Troubleshooting Techniques

### Container Debugging

```bash
# Run container in debug mode
docker-compose run --rm web bash

# Attach to running container
docker attach property_analyzer_web

# Copy files from container for analysis
docker cp property_analyzer_web:/app/logs ./local-logs

# Run commands in container context
docker-compose exec web python -c "import sys; print(sys.path)"
docker-compose exec web pip list
```

### Performance Profiling

```bash
# Profile application startup
time docker-compose up

# Monitor memory usage over time
while true; do docker stats --no-stream; sleep 5; done

# Check application metrics
docker-compose exec web curl http://localhost:5000/metrics

# Analyze container layers
docker history property-data-dashboard_web
```

### Security Diagnostics

```bash
# Check container security
docker-compose exec web whoami
docker-compose exec web id

# Verify file permissions
docker-compose exec web ls -la /app
docker-compose exec web find /app -type f -perm /o+w

# Check network security
docker-compose exec web netstat -tulpn
docker-compose exec web ss -tulpn
```

## Getting Additional Help

If you continue to experience issues after trying these troubleshooting steps:

1. **Check Application Logs**: Review detailed application logs for specific error messages
2. **Verify System Requirements**: Ensure your system meets minimum requirements (4GB RAM, Docker 20.10+)
3. **Update Docker**: Make sure you're using the latest version of Docker and Docker Compose
4. **Clean Installation**: Try a fresh installation with `docker-compose down -v && docker-compose up --build`
5. **Community Support**: Check Docker documentation and community forums for similar issues

### Useful Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Property Data Dashboard DEPLOYMENT.md](DEPLOYMENT.md) for advanced scenarios
- [Application-specific troubleshooting](README.md#troubleshooting) in main README

### Emergency Recovery

If the system is completely unresponsive:

```bash
# Stop all containers
docker-compose down

# Remove all containers and volumes
docker-compose down -v --remove-orphans

# Clean Docker system
docker system prune -a --volumes

# Restart Docker service
sudo systemctl restart docker  # Linux
# Or restart Docker Desktop

# Fresh installation
docker-compose up --build --force-recreate
```